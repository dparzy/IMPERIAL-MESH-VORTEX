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
from typing import Callable, List, Optional, Dict, Any

from imperium.koloseum.paper_trading import (
    PaperTradingEngine, SygnalWejscia, BarData,
)
from imperium.koloseum.namiestnik import Namiestnik, get_namiestnik
from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara, PlanPozycji

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
    ) -> None:
        self.legatus = legatus
        self.kalkulator = kalkulator
        self.engine = engine
        self.budowniczy = budowniczy
        self.wskazniki_provider = wskazniki_provider
        self.min_pewnosc = min_pewnosc
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
        # 1. Wskaźniki (Prawo I — Brama/Budowniczy liczą, nie Dyrygent)
        wskazniki = self._wskazniki(bary, symbol)
        if not wskazniki:
            return DecyzjaCyklu(symbol, "BUDOWNICZY", False,
                                powod="brak wskaźników (puste bary lub błąd Bramy)")

        # 1b. Auto-klasyfikacja reżimu (Prawo XV — ożywia system reżimowy).
        # rezim="AUTO" → klasyfikator z gotowych wskaźników (nie zgadywanie, dane Bramy).
        if rezim == "AUTO":
            from imperium.legiony.legatus import klasyfikuj_rezim
            rezim = klasyfikuj_rezim(wskazniki)

        # Interwał z danych — sterownik warstwy stylu (SCALP/SWING/INVEST).
        interwal = bary[-1].get("interwal", "") if bary else ""

        # 2. Namiestnik — Regime-Aware + Timeframe-Aware Gating (Faza 1)
        # Wyznacza: tryb, prog_pewnosci, lewar_factor, lewar_cap, rynek, czy_grac
        # dla pary (reżim × styl interwałowy).
        tryb_aktywny = self.tryb
        prog_aktywny = self.min_pewnosc
        lewar_factor = 1.0
        decyzja_nam = None
        if self.namiestnik is not None:
            decyzja_nam = self.namiestnik.decyduj(rezim, interwal)
            if not decyzja_nam.czy_grac:
                return DecyzjaCyklu(symbol, "NAMIESTNIK_CISZA", False,
                                    rezim=rezim, powod=f"Namiestnik: {decyzja_nam.opis}")
            tryb_aktywny = decyzja_nam.tryb
            prog_aktywny = decyzja_nam.prog_pewnosci
            lewar_factor = decyzja_nam.lewar_factor

        # 3. Legatus — agregacja roju
        raport = self.legatus.fokus(symbol, wskazniki, rezim=rezim, bary=bary)

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

        plan = self.kalkulator.policz(
            symbol=symbol,
            kierunek=kierunek,
            cena_wejscia=cena_wejscia,
            dzwignia=dzwignia_final,
            kapital_usdt=self.engine.kapital,
            pewnosc=pewnosc,
            rezim=raport.rezim,
        )

        if not plan.checklist_ok:
            return DecyzjaCyklu(symbol, "PRETORIANIE_WETO", False, kierunek=kierunek,
                                pewnosc=pewnosc, rezim=raport.rezim,
                                powod=f"weto Pretorianów: {plan.powod_veto}",
                                raport=raport, plan=plan)

        # 4. Sygnał wejścia → silnik paper trading
        powody = f"{raport.zgodnych_neuronow}/{raport.aktywnych_neuronow} neuronów zgodnych"
        if top_strat is not None:
            powody += f" | strategia {top_strat.strategia.id} {top_strat.kierunek} ({top_strat.wynik:.0%})"
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

        return DecyzjaCyklu(symbol, "WEJSCIE", True, kierunek=kierunek,
                            pewnosc=pewnosc, rezim=raport.rezim,
                            powod=f"pozycja otwarta: {pozycja.pozycja_id}",
                            raport=raport, plan=plan, sygnal=sygnal)

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
