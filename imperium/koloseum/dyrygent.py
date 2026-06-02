"""
🏛️ DYRYGENT — orkiestrator pełnego cyklu decyzyjnego Imperium (Faza 0).

Spina rozproszone klocki w jeden łańcuch end-to-end:

    bary OHLCV
        │
        ▼
    [Budowniczy + Brama Kalkulatora]  → wskazniki (Prawo I: tylko Brama liczy)
        │
        ▼
    [Legatus.fokus]                   → RaportLegatusa (kierunek, pewność, reżim, weto)
        │
        ▼
    [KalkulatorLewara.policz]         → PlanPozycji (SL/TP/dźwignia/rozmiar, checklist)
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
    ) -> None:
        self.legatus = legatus
        self.kalkulator = kalkulator
        self.engine = engine
        self.budowniczy = budowniczy
        self.wskazniki_provider = wskazniki_provider
        self.min_pewnosc = min_pewnosc
        # Tryb roli warstwy strategii (Klucznik) w decyzji:
        #   "agregat"   — kierunek z gołego głosowania neuronów (strategie ignorowane)
        #   "filtr"     — wejście tylko gdy top-strategia zgadza się z neuronami (Opcja 1)
        #   "strategia" — kierunek z top-1 dopasowanej strategii; neurony dają pewność (Opcja 2)
        assert tryb in ("agregat", "filtr", "strategia"), f"nieznany tryb: {tryb}"
        self.tryb = tryb

    # ── Fabryka pełnego składu (produkcyjna — wymaga TA-Lib) ─────────────────
    @classmethod
    def zbuduj(cls, kapital_startowy: float = 10_000.0, sesja_id: str = "",
               min_neuronow: int = 5, min_przewaga: float = 0.55,
               min_pewnosc: float = 0.55, log_dir=None, tryb: str = "agregat") -> "Dyrygent":
        """Składa Dyrygenta z pełnym rojem, Budowniczym (TA-Lib) i silnikiem paper."""
        from imperium.legiony.rejestr import zbuduj_legatusa
        from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow

        legatus = zbuduj_legatusa(min_neuronow=min_neuronow,
                                  min_przewaga=min_przewaga, aktywuj_smc=True)
        budowniczy = BudowniczyWskaznikow()
        engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                    sesja_id=sesja_id, log_dir=log_dir)
        return cls(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                   budowniczy=budowniczy, min_pewnosc=min_pewnosc, tryb=tryb)

    # ── Jeden cykl decyzyjny ─────────────────────────────────────────────────
    def cykl(self, symbol: str, bary: List[Dict[str, Any]],
             rezim: str = "NORMAL", timestamp: Optional[int] = None) -> DecyzjaCyklu:
        """
        Przeprowadza pełny łańcuch dla jednego symbolu i okna barów.
        Zwraca DecyzjaCyklu z przejrzystym śladem każdego etapu.
        """
        # 1. Wskaźniki (Prawo I — Brama/Budowniczy liczą, nie Dyrygent)
        wskazniki = self._wskazniki(bary)
        if not wskazniki:
            return DecyzjaCyklu(symbol, "BUDOWNICZY", False,
                                powod="brak wskaźników (puste bary lub błąd Bramy)")

        # 2. Legatus — agregacja roju
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

        if raport.pewnosc_agregatu < self.min_pewnosc:
            return DecyzjaCyklu(symbol, "LEGATUS_SLABY", False,
                                kierunek=raport.kierunek, pewnosc=raport.pewnosc_agregatu,
                                rezim=raport.rezim,
                                powod=f"pewność {raport.pewnosc_agregatu:.2f} < próg {self.min_pewnosc}",
                                raport=raport)

        # 2b. Warstwa strategii (Klucznik) — rola zależna od trybu (Opcja 3)
        kierunek = raport.kierunek
        pewnosc = raport.pewnosc_agregatu
        top_strat = raport.strategie_dopasowane[0] if raport.strategie_dopasowane else None

        if self.tryb == "filtr":
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
        elif self.tryb == "strategia":
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

        plan = self.kalkulator.policz(
            symbol=symbol,
            kierunek=kierunek,
            cena_wejscia=cena_wejscia,
            dzwignia=0,  # 0 = auto z pewności i reżimu
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
    def _wskazniki(self, bary: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Liczy wskaźniki przez wstrzyknięty provider lub Budowniczego (Prawo I)."""
        if self.wskazniki_provider is not None:
            return self.wskazniki_provider(bary)
        if self.budowniczy is not None:
            return self.budowniczy.zbuduj(bary)
        raise RuntimeError("Dyrygent bez Budowniczego i bez wskazniki_provider — nie ma skąd wziąć wskaźników (Prawo I)")
