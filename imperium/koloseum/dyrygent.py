"""
🏛️ DYRYGENT — orkiestrator pełnego cyklu decyzyjnego Imperium (Faza 1).

Spina rozproszone klocki w jeden łańcuch end-to-end:

    bary OHLCV
        │
        ▼
    [Budowniczy + Brama Kalkulatora]  → wskazniki (Prawo I: tylko Brama liczy)
        │
        ▼
    klasyfikuj_rezim()                → rezim (auto lub podany z zewnątrz)
        │
        ▼
    [NAMIESTNIK]                      → UstawieniaRezimu: {tryb, lewar_factor, prog, czy_grac}
        │                               (Regime-Aware Gating — arXiv:2508.02686, 2603.19136)
        ▼
    [Legatus.fokus]                   → RaportLegatusa (kierunek, pewność, reżim, weto)
        │
        ▼
    [KalkulatorLewara.policz]         → PlanPozycji (SL/TP/dźwignia×lewar_factor, checklist)
        │
        ▼
    [SygnalWejscia → PaperTradingEngine] → wirtualna pozycja + log do Pamięci Absolutnej

Zasady:
  • Prawo I — Dyrygent NIE liczy wskaźników sam; deleguje do Budowniczego/Bramy.
  • Prawo XV — gdy Legatus daje NEUTRAL lub weto, lub Kalkulator daje WETO,
    cykl kończy się bez pozycji (świadoma cisza, nie błąd).
  • Testowalność — Budowniczy (wymaga TA-Lib) jest WSTRZYKIWANY. Można podać
    `wskazniki_provider` (callable bary→dict) i pominąć TA-Lib w testach.

Użycie (pełne, produkcyjne):
    dyrygent = Dyrygent.zbuduj(kapital_startowy=10_000.0)
    for bar_dict, okno_barow in strumien:
        decyzja = dyrygent.cykl(symbol, okno_barow)
        dyrygent.engine.przetworz_bar(BarData(...))   # aktualizacja otwartych

Użycie (test, bez TA-Lib):
    dyrygent = Dyrygent(legatus=..., kalkulator=..., engine=...,
                        wskazniki_provider=lambda bary: {"RSI_14": 25.0, "CLOSE": 100.0})
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional, Dict, Any

from imperium.koloseum.paper_trading import (
    PaperTradingEngine, SygnalWejscia,
)
from imperium.koloseum.namiestnik import Namiestnik, get_namiestnik
from imperium.pretorianie.kalkulator_lewara import (
    KalkulatorLewara, PlanPozycji, BezpiecznikKrzywejKapitalu,
    RegulaSzesciuProcentEldera,
)

logger = logging.getLogger("Dyrygent")


@dataclass
class DecyzjaCyklu:
    """Wynik jednego cyklu decyzyjnego — przejrzysty ślad (Prawo I: jawność)."""
    symbol: str
    etap: str                     # gdzie cykl się zakończył
    wszedl: bool                  # czy otwarto pozycję
    kierunek: str = "NEUTRAL"
    pewnosc: float = 0.0
    rezim: str = "NORMAL"
    powod: str = ""               # czytelne wyjaśnienie zakończenia
    raport: Optional[object] = None   # RaportLegatusa
    plan: Optional[PlanPozycji] = None
    sygnal: Optional[SygnalWejscia] = None
    pozycja_id: str = ""          # ID otwartej pozycji (pętla uczenia MWU — atrybucja głosów)


class Dyrygent:
    """Orkiestrator cyklu decyzyjnego. Jeden symbol, jedno okno barów = jedna decyzja."""

    def __init__(
        self,
        legatus,
        kalkulator: KalkulatorLewara,
        engine: PaperTradingEngine,
        budowniczy=None,
        wskazniki_provider: Optional[Callable[[List[Dict[str, Any]]], Dict[str, Any]]] = None,
        min_pewnosc: float = 0.55,
        tryb: str = "agregat",
        namiestnik: Optional[Namiestnik] = None,
        adaptery: Optional[List[Any]] = None,
        breaker_krzywej: bool = True,
        regula_6pct: bool = False,
        min_pewnosc_interwalu: Optional[Dict[str, float]] = None,
        sl_atr_mult: Optional[float] = None,
        drift_adapter: Optional[Any] = None,
        rada_doradcow: Optional[Any] = None,
    ) -> None:
        self.legatus = legatus
        self.kalkulator = kalkulator
        self.engine = engine
        self.budowniczy = budowniczy
        self.wskazniki_provider = wskazniki_provider
        self.min_pewnosc = min_pewnosc
        # FAZA B (W-286): progi pewności per interwał (np. {"4H": 0.65}) —
        # nadpisują min_pewnosc dla danego interwału; brak wpisu → próg globalny.
        self.min_pewnosc_interwalu: Dict[str, float] = min_pewnosc_interwalu or {}
        # W-288: SL = sl_atr_mult × ATR_14 (opt-in; None = stary SL z dźwigni).
        self.sl_atr_mult = sl_atr_mult
        # W-291: kontekst zewnętrzny dolewany do wskaźników (RADAR BTC: BTC_TREND).
        self.kontekst_dodatkowy: Dict[str, Any] = {}
        # W-291 Praeda (tryb łowcy): Okazjon steruje agresją w potwierdzonych
        # momentach. None = wyłączony. praeda_dd_normal ustawia portfel/breaker.
        self.okazjon = None
        self.praeda_dd_normal: bool = True
        # W-296 DriftAdapter: antycypacyjna korekta WAGI_REZIMU przed zmianą reżimu.
        # None = wyłączony. Podpięty = dodaje reżim co bar i koryguje wagi Legatusa.
        self.drift_adapter = drift_adapter
        # W-299 Synapsy Reżimowe: graf par neuronów per-reżim × dekorelacja.
        # Przekazywany do legatus.synapsy. Dyrygent wykrywa nowe zamknięcia i wywołuje
        # aktualizuj() — zamknięta pętla uczenia koalicji bez ingerencji z zewnątrz.
        self._synapsy_pending: Dict[str, tuple] = {}  # pozycja_id → (sygnaly, rezim, kier)
        self._synapsy_ostatni_idx: int = 0     # ile zamknięć już przetworzyliśmy
        # Rada Doradców: 5-osobowe kolegium (Oracle/Fulmen/Iustitia/Hermes/Pythia).
        # None = wyłączona. Gdy aktywna: sprawdza plan po Kalkulatorze, może zawetować
        # lub zredukować rozmiar pozycji (OpinaRady.modyfikator_pozycji).
        self.rada_doradcow = rada_doradcow
        # W-290 portfel: budżet sizingu pary (None = pełny wolny kapitał silnika).
        # W koszyku N par każdy Dyrygent sizinguje wg kapital/N (równe wagi).
        self.kapital_sizing: Optional[float] = None
        # Opcja A: StanRynku z RadarRynku — przekazywany do Namiestnika i Klucznika
        # (radar-aware gating + strategy selection). None = tryb bez radaru.
        self.stan_rynku: Optional[Any] = None
        # W-300: RadarRynku wpięty w sloty kontekstu. odswiez_kontekst_rynku() woła
        # skanuj() i wypełnia kontekst_dodatkowy (BTC_TREND/DOMINACJA/PRZEPLYW →
        # wskazniki → RADAR-01/02/03) oraz stan_rynku (→ Namiestnik). Bez tego
        # wywołania trzy neurony RADAR abstynowały na zawsze (Prawo XV — martwy głos).
        self._radar_rynku: Optional[Any] = None
        # Adaptery danych (Faza B) — dolewają do wskaźników dane spoza OHLCV
        # (funding, OI, long/short, sentyment) po Budowniczym. Pusta lista = tryb
        # czysty OHLCV (np. backtest z CSV — neurony R abstynują, Prawo XV).
        self.adaptery: List[Any] = adaptery or []
        # Tryb domyślny (gdy Namiestnik wyłączony lub niezainicjowany):
        #   "agregat"   — kierunek z gołego głosowania neuronów
        #   "filtr"     — wejście tylko gdy top-strategia zgadza się z neuronami
        #   "strategia" — kierunek z top-1 dopasowanej strategii
        assert tryb in ("agregat", "filtr", "strategia"), f"nieznany tryb: {tryb}"
        self.tryb = tryb
        # Namiestnik: Regime-Aware Gating (Faza 1). None = tryb statyczny jak wcześniej.
        self.namiestnik: Optional[Namiestnik] = namiestnik
        # Equity-Curve Circuit Breaker (W-062): meta-poziom anti-tail nad AOA (30%).
        # Śledzi własną krzywą kapitału; REDUCED → ×0.5 rozmiaru, HALT → blokada wejść.
        # breaker_krzywej=False → wyłączony (opt-out, kompatybilność wsteczna).
        self.breaker_krzywej: Optional[BezpiecznikKrzywejKapitalu] = (
            BezpiecznikKrzywejKapitalu() if breaker_krzywej else None
        )
        # Reguła 6% Elder (BIB-015): miesięczny limit straty — meta-poziom ponad W-062.
        # regula_6pct=True → aktywna (domyślnie wyłączona — opt-in, wymaga kapitału bazowego).
        self.regula_6pct: Optional[RegulaSzesciuProcentEldera] = (
            RegulaSzesciuProcentEldera() if regula_6pct else None
        )

    # ── Fabryka pełnego składu (produkcyjna — wymaga TA-Lib) ─────────────────
    @classmethod
    def zbuduj(cls, kapital_startowy: float = 10_000.0, sesja_id: str = "",
               min_neuronow: int = 5, min_przewaga: float = 0.55,
               min_pewnosc: float = 0.55, log_dir=None, tryb: str = "agregat",
               adaptery_live: bool = True) -> "Dyrygent":
        """Składa Dyrygenta z pełnym rojem, Budowniczym (TA-Lib) i silnikiem paper.

        adaptery_live: gdy True (domyślnie), wpina publiczne adaptery futures+sentyment
            (Binance fapi + alternative.me, bez klucza) → kategoria R głosuje realnymi
            danymi. Ustaw False dla czystego backtestu OHLCV z CSV (neurony R abstynują).
        """
        from imperium.legiony.rejestr import zbuduj_legatusa
        from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow

        legatus = zbuduj_legatusa(min_neuronow=min_neuronow,
                                  min_przewaga=min_przewaga, aktywuj_smc=True)
        budowniczy = BudowniczyWskaznikow()
        engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                    sesja_id=sesja_id, log_dir=log_dir)
        adaptery = []
        if adaptery_live:
            from imperium.akwedukty.adaptery import AdapterFutures, AdapterFearGreed, AdapterCVD
            adaptery = [AdapterFutures(), AdapterFearGreed(), AdapterCVD()]
        return cls(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                   budowniczy=budowniczy, min_pewnosc=min_pewnosc, tryb=tryb,
                   namiestnik=get_namiestnik(), adaptery=adaptery)

    # ── Jeden cykl decyzyjny ─────────────────────────────────────────────────
    def cykl(self, symbol: str, bary: List[Dict[str, Any]],
             rezim: str = "NORMAL", timestamp: Optional[int] = None) -> DecyzjaCyklu:
        """
        Przeprowadza pełny łańcuch dla jednego symbolu i okna barów.
        Zwraca DecyzjaCyklu z przejrzystym śladem każdego etapu.
        """
        # 0. W-299 Synapsy Reżimowe — uczenie z nowo zamkniętych pozycji.
        # Sprawdzamy historia_zamkniec od ostatniego przetworzonego indeksu.
        if self.legatus.synapsy is not None:
            self._aktualizuj_synapsy()

        # 1. Wskaźniki (Prawo I — Brama/Budowniczy liczą, nie Dyrygent)
        wskazniki = self._wskazniki(bary, symbol)
        if not wskazniki:
            return DecyzjaCyklu(symbol, "BUDOWNICZY", False,
                                powod="brak wskaźników (puste bary lub błąd Bramy)")
        # Kontekst zewnętrzny (W-291): RADAR BTC i in. wstrzykiwane z poziomu
        # silnika portfelowego (BTC_TREND lidera) — dolewane do wskaźników.
        if self.kontekst_dodatkowy:
            wskazniki.update(self.kontekst_dodatkowy)

        # 1b. Auto-klasyfikacja reżimu (Prawo XV — ożywia system reżimowy).
        # rezim="AUTO" → klasyfikator z gotowych wskaźników (nie zgadywanie, dane Bramy).
        if rezim == "AUTO":
            from imperium.legiony.legatus import klasyfikuj_rezim
            rezim = klasyfikuj_rezim(wskazniki)

        # 1c. W-296 DriftAdapter — antycypacyjna korekta WAGI_REZIMU.
        # Rejestruje reżim w historii, oblicza sygnał dryfu; gdy dryfuje, pre-przesuwa
        # wagi kategorii ZANIM reżim oficjalnie się zmieni (mniej strat na przejściach).
        if self.drift_adapter is not None:
            self.drift_adapter.dodaj_rezim(rezim)
            _sygnal_dryfu = self.drift_adapter.skanuj()
            if _sygnal_dryfu.czy_drift:
                from imperium.legiony.legatus import WAGI_REZIMU
                self.legatus.ustaw_wagi_rezimu(
                    self.drift_adapter.koryguj_wagi(WAGI_REZIMU, rezim, _sygnal_dryfu)
                )

        # Interwał z danych — sterownik warstwy stylu (SCALP/SWING/INVEST).
        interwal = bary[-1].get("interwal", "") if bary else ""

        # 2. Namiestnik — Regime-Aware + Timeframe-Aware Gating (Faza 1)
        # Wyznacza: tryb, prog_pewnosci, lewar_factor, lewar_cap, rynek, czy_grac
        # dla pary (reżim × styl interwałowy).
        tryb_aktywny = self.tryb
        prog_aktywny = self.min_pewnosc_interwalu.get(interwal, self.min_pewnosc)
        lewar_factor = 1.0
        decyzja_nam = None
        if self.namiestnik is not None:
            decyzja_nam = self.namiestnik.decyduj_z_radarem(rezim, interwal, self.stan_rynku)
            if not decyzja_nam.czy_grac:
                return DecyzjaCyklu(symbol, "NAMIESTNIK_CISZA", False,
                                    rezim=rezim, powod=f"Namiestnik: {decyzja_nam.opis}")
            tryb_aktywny = decyzja_nam.tryb
            # FAZA B (W-286): próg per interwał ma pierwszeństwo nad progiem
            # reżimowym Namiestnika, gdy jest OSTRZEJSZY (max — bezpieczniej).
            prog_aktywny = max(decyzja_nam.prog_pewnosci, prog_aktywny)
            lewar_factor = decyzja_nam.lewar_factor

        # 3. Legatus — agregacja roju (Opcja A: przekaż StanRynku → radar scoring strategii)
        self.legatus.stan_rynku = self.stan_rynku
        raport = self.legatus.fokus(symbol, wskazniki, rezim=rezim, bary=bary)
        # Reset override WAGI_REZIMU — każdy cykl startuje z czystym stanem.
        if self.drift_adapter is not None:
            self.legatus.resetuj_wagi_rezimu()

        if raport.weto:
            return DecyzjaCyklu(symbol, "LEGATUS_WETO", False,
                                kierunek=raport.kierunek, pewnosc=raport.pewnosc_agregatu,
                                rezim=raport.rezim, powod=f"weto Legatusa: {raport.powod_weta}",
                                raport=raport)

        if raport.kierunek == "NEUTRAL":
            return DecyzjaCyklu(symbol, "LEGATUS_NEUTRAL", False,
                                kierunek="NEUTRAL", pewnosc=raport.pewnosc_agregatu,
                                rezim=raport.rezim, powod="rój neutralny — brak przewagi",
                                raport=raport)

        if raport.pewnosc_agregatu < prog_aktywny:
            return DecyzjaCyklu(symbol, "LEGATUS_SLABY", False,
                                kierunek=raport.kierunek, pewnosc=raport.pewnosc_agregatu,
                                rezim=raport.rezim,
                                powod=f"pewność {raport.pewnosc_agregatu:.2f} < próg {prog_aktywny:.2f} (Namiestnik)",
                                raport=raport)

        # 3b. Warstwa strategii (Klucznik) — tryb określony przez Namiestnika
        kierunek = raport.kierunek
        pewnosc = raport.pewnosc_agregatu
        top_strat = raport.strategie_dopasowane[0] if raport.strategie_dopasowane else None

        if tryb_aktywny == "filtr":
            # Wejście tylko gdy top-strategia zgadza się z głosowaniem neuronów (Opcja 1)
            if top_strat is None:
                return DecyzjaCyklu(symbol, "STRATEGIA_BRAK", False, kierunek=kierunek,
                                    pewnosc=pewnosc, rezim=raport.rezim,
                                    powod="tryb filtr: brak dopasowanej strategii", raport=raport)
            if top_strat.kierunek != kierunek:
                return DecyzjaCyklu(symbol, "STRATEGIA_KONFLIKT", False, kierunek=kierunek,
                                    pewnosc=pewnosc, rezim=raport.rezim,
                                    powod=f"tryb filtr: neurony {kierunek} ≠ strategia "
                                          f"{top_strat.strategia.id} {top_strat.kierunek}",
                                    raport=raport)
        elif tryb_aktywny == "strategia":
            # Kierunek z top-1 strategii; neurony tylko potwierdzają pewność (Opcja 2)
            if top_strat is None:
                return DecyzjaCyklu(symbol, "STRATEGIA_BRAK", False, kierunek=kierunek,
                                    pewnosc=pewnosc, rezim=raport.rezim,
                                    powod="tryb strategia: brak dopasowanej strategii", raport=raport)
            kierunek = top_strat.kierunek
            # pewność = średnia dopasowania strategii i pewności neuronów (gdy zgodne — wzmocnienie)
            zgoda = 1.0 if top_strat.kierunek == raport.kierunek else 0.6
            pewnosc = round(min(1.0, (top_strat.wynik + raport.pewnosc_agregatu) / 2 * zgoda), 4)

        # 3. Pretorianie — matematyka przeżycia (SL/TP/dźwignia/rozmiar)
        cena_wejscia = wskazniki.get("CLOSE") or (bary[-1].get("close") if bary else 0.0)
        if not cena_wejscia:
            return DecyzjaCyklu(symbol, "BRAK_CENY", False, kierunek=kierunek,
                                pewnosc=pewnosc, rezim=raport.rezim,
                                powod="brak ceny CLOSE w danych", raport=raport)

        # 4a. Dźwignia: auto z pewności/reżimu, Namiestnik skaluje lewar_factor
        #     i przycina sufitem stylu interwałowego (lewar_cap: scalp≤10, swing≤5, invest≤2).
        dzwignia_base = self.kalkulator.auto_dzwignia(pewnosc, raport.rezim)
        if self.namiestnik is not None:
            dzwignia_final = self.namiestnik.skaluj_dzwignie(dzwignia_base, raport.rezim, interwal)
        else:
            dzwignia_final = int(round(dzwignia_base * lewar_factor))
            dzwignia_final = max(1, min(dzwignia_final, 20))

        # Equity-Curve Circuit Breaker (W-062): dolicz aktualny stan kapitału roju
        # do krzywej i przelicz stan (NORMAL/REDUCED/HALT) przed sizingiem.
        if self.breaker_krzywej is not None:
            # Prawdziwe equity (wolny + zablokowany margin), NIE sam wolny kapitał —
            # inaczej breaker myli utylizację depozytu z drawdownem (Prawo XV).
            self.breaker_krzywej.aktualizuj(self.engine.kapital_calkowity)
        if self.regula_6pct is not None:
            # Data z czasu ŚWIECY (nie systemowego!) — w backteście timestamp to
            # czas bara, więc reset/HALT liczą się względem kalendarza danych, nie
            # date.today() maszyny (Prawo I — zero zniekształcenia czasem systemu).
            dzien_swiecy = None
            if timestamp is not None:
                dzien_swiecy = datetime.fromtimestamp(
                    timestamp / 1000, tz=timezone.utc).date()
            self.regula_6pct.aktualizuj(self.engine.kapital_calkowity,
                                        dzisiaj=dzien_swiecy)

        # 4b. 🗡️ PRAEDA (W-291): auto-skalowana agresja w POTWIERDZONYCH okazjach.
        #     Tylko AMPLIFIKUJE w klatce: lewar cap 20, rozmiar clamp 50% kapitału;
        #     śpi w drawdownie (praeda_dd_normal=False). Wszystkie weta nadal działają.
        mnoznik_rozmiaru = 1.0
        if self.okazjon is not None:
            ok = self.okazjon.ocen(raport, wskazniki, kierunek, self.praeda_dd_normal)
            if ok.potwierdzona:
                dzwignia_final = max(1, min(20, int(round(dzwignia_final * ok.mnoznik_lewara))))
                mnoznik_rozmiaru = ok.mnoznik_rozmiaru

        plan = self.kalkulator.policz(
            symbol=symbol,
            kierunek=kierunek,
            cena_wejscia=cena_wejscia,
            dzwignia=dzwignia_final,
            mnoznik_rozmiaru=mnoznik_rozmiaru,
            kapital_usdt=(self.kapital_sizing if self.kapital_sizing is not None
                          else self.engine.kapital),
            pewnosc=pewnosc,
            rezim=raport.rezim,
            breaker_krzywej=self.breaker_krzywej,
            regula_6pct=self.regula_6pct,
            atr=wskazniki.get("ATR_14") if self.sl_atr_mult else None,
            sl_atr_mult=self.sl_atr_mult,
        )

        if not plan.checklist_ok:
            return DecyzjaCyklu(symbol, "PRETORIANIE_WETO", False, kierunek=kierunek,
                                pewnosc=pewnosc, rezim=raport.rezim,
                                powod=f"weto Pretorianów: {plan.powod_veto}",
                                raport=raport, plan=plan)

        # 4b. Rada Doradców — kolegium pięciorga (Oracle/Fulmen/Iustitia/Hermes/Pythia).
        # Weto Rady (< 3/5 lub IUSTITIA BLOKADA) = brak wejścia. 3-4/5 = redukcja pozycji.
        if self.rada_doradcow is not None:
            opinia = self._opinia_rady(wskazniki, raport, plan, kierunek, interwal, rezim)
            if opinia.blokada:
                return DecyzjaCyklu(symbol, "RADA_WETO", False, kierunek=kierunek,
                                    pewnosc=pewnosc, rezim=raport.rezim,
                                    powod=f"Rada Doradców weto: {opinia.powod_blokady}",
                                    raport=raport, plan=plan)
            if opinia.modyfikator_pozycji < 1.0:
                plan = self.kalkulator.policz(
                    symbol=symbol, kierunek=kierunek, cena_wejscia=cena_wejscia,
                    dzwignia=plan.dzwignia,
                    mnoznik_rozmiaru=mnoznik_rozmiaru * opinia.modyfikator_pozycji,
                    kapital_usdt=(self.kapital_sizing if self.kapital_sizing is not None
                                  else self.engine.kapital),
                    pewnosc=pewnosc, rezim=raport.rezim,
                    breaker_krzywej=self.breaker_krzywej, regula_6pct=self.regula_6pct,
                    atr=wskazniki.get("ATR_14") if self.sl_atr_mult else None,
                    sl_atr_mult=self.sl_atr_mult,
                )
                if not plan.checklist_ok:
                    return DecyzjaCyklu(symbol, "PRETORIANIE_WETO", False, kierunek=kierunek,
                                        pewnosc=pewnosc, rezim=raport.rezim,
                                        powod=f"weto Pretorianów po redukcji Rady: {plan.powod_veto}",
                                        raport=raport, plan=plan)

        # 4. Sygnał wejścia → silnik paper trading
        powody = f"{raport.zgodnych_neuronow}/{raport.aktywnych_neuronow} neuronów zgodnych"
        if top_strat is not None:
            powody += f" | strategia {top_strat.strategia.id} {top_strat.kierunek} ({top_strat.wynik:.0%})"
        if plan.frakcja_breaker < 1.0:
            powody += f" | breaker krzywej REDUCED ×{plan.frakcja_breaker:.2f}"
        sygnal = SygnalWejscia(
            symbol=symbol,
            interwal=bary[-1].get("interwal", "") if bary else "",
            kierunek=kierunek,
            pewnosc=pewnosc,
            cena_wejscia=plan.cena_wejscia,
            stop_loss=plan.stop_loss,
            take_profit=plan.take_profit,
            dzwignia=plan.dzwignia,
            rozmiar_usdt=plan.rozmiar_usdt,
            rezim=raport.rezim,
            sesja_id=self.engine.sesja_id,
            powody=powody,
        )

        pozycja = self.engine.wejdz(sygnal, timestamp=timestamp)
        if pozycja is None:
            return DecyzjaCyklu(symbol, "ENGINE_ODRZUCIL", False, kierunek=kierunek,
                                pewnosc=pewnosc, rezim=raport.rezim,
                                powod="silnik odrzucił (limit pozycji / brak kapitału / duplikat)",
                                raport=raport, plan=plan, sygnal=sygnal)

        # W-299 Synapsy: zapamiętaj sygnały tej pozycji — po zamknięciu będziemy wiedzieć
        # które pary neuronów głosowały i jak (uczenie post-hoc).
        if self.legatus.synapsy is not None and raport.sygnaly:
            self._synapsy_pending[pozycja.pozycja_id] = (
                list(raport.sygnaly), raport.rezim, kierunek
            )

        return DecyzjaCyklu(symbol, "WEJSCIE", True, kierunek=kierunek,
                            pewnosc=pewnosc, rezim=raport.rezim,
                            powod=f"pozycja otwarta: {pozycja.pozycja_id}",
                            raport=raport, plan=plan, sygnal=sygnal,
                            pozycja_id=pozycja.pozycja_id)

    def _aktualizuj_synapsy(self) -> None:
        """
        W-299: wykrywa nowo zamknięte pozycje i aktualizuje SynapsyRezimowe.
        Wywołaj na początku każdego cyklu zanim Legatus.fokus().
        """
        synapsy = self.legatus.synapsy
        if synapsy is None:
            return
        hist = self.engine.historia_zamkniec
        nowe = hist[self._synapsy_ostatni_idx:]
        self._synapsy_ostatni_idx = len(hist)

        for wynik in nowe:
            pid = wynik.pozycja_id
            pending = self._synapsy_pending.pop(pid, None)
            if pending is None:
                continue
            sygnaly, rezim, kierunek = pending
            synapsy.aktualizuj(
                sygnaly=sygnaly,
                kierunek_decyzji=kierunek,
                pnl_pct=wynik.pnl_pct,
                rezim=rezim,
            )

    def odswiez_kontekst_rynku(
        self,
        close_btc: List[float],
        close_alty: Dict[str, List[float]],
        vol_alty: Optional[Dict[str, List[float]]] = None,
    ) -> Optional[Any]:
        """
        W-300: skanuje rynek RadarRynkiem i wypełnia oba sloty kontekstu Dyrygenta.

        Wołane RAZ na bar przez pętlę portfelową/backtest PRZED cyklami per-symbol —
        BTC i breadth to kontekst wspólny dla całego koszyka, nie per-symbol.
        Serie muszą być przyczynowe (DO bieżącej świecy włącznie — zero lookahead).

        Efekt:
          • kontekst_dodatkowy ← BTC_TREND / BTC_DOMINANCJA / PRZEPLYW_KAPITALU
            (dolewane do wskaźników w cyklu → budzą RADAR-01/02/03).
          • stan_rynku ← StanRynku (radar-aware gating w Namiestniku/Kluczniku).

        Zwraca StanRynku (lub None gdy radar nie ma dość danych — wtedy neurony
        RADAR abstynują zgodnie z Prawem XV, zamiast zgadywać).
        """
        if self._radar_rynku is None:
            from imperium.legiony.radar_rynku import RadarRynku
            self._radar_rynku = RadarRynku()

        stan = self._radar_rynku.skanuj(close_btc, close_alty, vol_alty)
        self.stan_rynku = stan
        # Aktualizuj tylko klucze radaru — nie kasuj innego kontekstu (np. W-291).
        self.kontekst_dodatkowy.update(stan.jako_wskazniki())
        return stan

    # ── Wewnętrzne ───────────────────────────────────────────────────────────
    def _wskazniki(self, bary: List[Dict[str, Any]], symbol: str = "") -> Dict[str, Any]:
        """Liczy wskaźniki przez wstrzyknięty provider lub Budowniczego (Prawo I).

        Po policzeniu wskaźników OHLCV dolewa dane z adapterów (Faza B): funding,
        OI, long/short, sentyment — most do neuronów kategorii R (PSY-01/02/03/04).
        Adapter, który padnie/nie ma danych, jest pomijany (wzbogac() bezpieczny).
        """
        if self.wskazniki_provider is not None:
            wskazniki = self.wskazniki_provider(bary)
        elif self.budowniczy is not None:
            wskazniki = self.budowniczy.zbuduj(bary)
        else:
            raise RuntimeError("Dyrygent bez Budowniczego i bez wskazniki_provider — nie ma skąd wziąć wskaźników (Prawo I)")

        # Faza B — adaptery dolewają dane spoza OHLCV (most do kategorii R/O)
        for adapter in self.adaptery:
            try:
                adapter.wzbogac(wskazniki, symbol)
            except Exception as e:
                logger.warning(f"[Dyrygent] adapter {getattr(adapter, 'NAZWA', '?')} pominięty: {e}")
        return wskazniki

    def _opinia_rady(self, wskazniki: Dict[str, Any], raport, plan,
                     kierunek: str, interwal: str, rezim: str):
        """
        Assembler Rady Doradców — zbiera dane z silnika/wskaźników i pyta każdego
        z pięciorga doradców. Brak danych historycznych → doradcy graceful-fall do
        BRAK_DANYCH/MILCZENIE (nie blokują — Prawo XV: cisza ≠ martwy głos).
        """
        from imperium.cesarz.doradcy.oracle import Oracle
        from imperium.cesarz.doradcy.fulmen import Fulmen, DaneFulmen
        from imperium.cesarz.doradcy.iustitia import (
            Iustitia, DaneIustitia,
            OtwartaPozycja as OtwartaPozycjaIustitia,
        )
        from imperium.cesarz.doradcy.hermes import Hermes, DaneHermes
        from imperium.cesarz.doradcy.pythia import (
            Pythia, buduj_odcisk, WpisHistorii,
        )

        # ORACLE: historia PnL z zamkniętych pozycji bieżącej sesji
        wyniki_hist = list(self.engine.historia_zamkniec)
        pnl_hist = [w.pnl_pct for w in wyniki_hist if hasattr(w, "pnl_pct")]
        ocena_oracle = Oracle().ocen(pnl_hist)

        # FULMEN: ortogonalna weryfikacja reżimu z wskaźników (DI+/DI- jako proxy VI)
        ocena_fulmen = Fulmen().ocen(DaneFulmen(
            adx_14=wskazniki.get("ADX_14") or 20.0,
            vi_plus_14=wskazniki.get("DI_PLUS") or 0.5,
            vi_minus_14=wskazniki.get("DI_MINUS") or 0.5,
            choppiness_14=wskazniki.get("CHOPPINESS_14") or 50.0,
            kaufman_er=0.5,   # nie liczony przez Budowniczego → neutral default
            legatus_rezim=rezim,
        ))

        # IUSTITIA: portfolio heat + Kelly fraction
        otwarte_poz = [
            OtwartaPozycjaIustitia(
                symbol=p.symbol,
                ryzyko_usdt=abs(p.cena_wejscia - p.stop_loss) / p.cena_wejscia * p.rozmiar_usdt,
                pnl_pct=0.0,   # brak bieżącej ceny w tym momencie
            )
            for p in self.engine.otwarte.values()
        ]
        ryzyko_new = abs(plan.cena_wejscia - plan.stop_loss) / plan.cena_wejscia * plan.rozmiar_usdt
        ostatnie_pnl = [w.pnl_pct for w in wyniki_hist[-5:]] if wyniki_hist else []
        wins = [p for p in ostatnie_pnl if p > 0]
        loss = [p for p in ostatnie_pnl if p <= 0]
        ocena_iustitia = Iustitia().ocen(DaneIustitia(
            kapital_total=self.engine.kapital_calkowity,
            nowe_ryzyko_usdt=ryzyko_new,
            otwarte_pozycje=otwarte_poz,
            ostatnie_5_pnl=ostatnie_pnl,
            korelacja_z_otwartymi=0.0,
            win_rate=len(wins) / max(len(ostatnie_pnl), 1),
            avg_win_pct=sum(wins) / max(len(wins), 1),
            avg_loss_pct=abs(sum(loss) / max(len(loss), 1)),
        ))

        # HERMES: kompletność danych + VPIN
        kompletne = sum(1 for v in wskazniki.values() if v is not None) / max(len(wskazniki), 1)
        _vpin_raw = wskazniki.get("VPIN_50")
        vpin_val = float(_vpin_raw) if _vpin_raw is not None else 0.5
        interwal_min = {"1m": 1, "5m": 5, "15m": 15, "30m": 30,
                        "1H": 60, "4H": 240, "1D": 1440}.get(interwal, 60)
        ocena_hermes = Hermes().ocen(DaneHermes(
            kompletnosc_danych=round(kompletne, 3),
            interwal_minut=interwal_min,
            wiek_danych_minut=1,   # bieżący bar = tylko co obliczony
            hash_ok=True,
            vpin=vpin_val,
        ))

        # PYTHIA: fingerprint matching z historii sesji
        odcisk = buduj_odcisk(
            rezim=rezim, interwal=interwal, kierunek=kierunek,
            pewnosc=raport.pewnosc_agregatu,
            funding_rate=wskazniki.get("FUNDING_RATE") or 0.0,
            atr_current=wskazniki.get("ATR_14") or 1.0,
            atr_30d_avg=wskazniki.get("ATR_14") or 1.0,  # brak 30d avg → proxy bieżącym
        )
        historia_pythia = [
            WpisHistorii(
                odcisk=buduj_odcisk(
                    rezim=w.rezim if hasattr(w, "rezim") else rezim,
                    interwal=w.interwal if hasattr(w, "interwal") else interwal,
                    kierunek=w.kierunek if hasattr(w, "kierunek") else "LONG",
                    pewnosc=0.6, funding_rate=0.0, atr_current=1.0, atr_30d_avg=1.0,
                ),
                pnl_pct=w.pnl_pct,
            )
            for w in wyniki_hist if hasattr(w, "pnl_pct")
        ]
        ocena_pythia = Pythia().ocen(odcisk, historia_pythia)

        return self.rada_doradcow.ocen(ocena_oracle, ocena_fulmen, ocena_iustitia,
                                       ocena_hermes, ocena_pythia)
