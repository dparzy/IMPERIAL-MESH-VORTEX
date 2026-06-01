"""
Generał Legatus — koordynator między Legionami a Senatem.

Zbiera sygnały ze wszystkich aktywnych neuronów, filtruje szum,
klasyfikuje reżim rynku i przekazuje zagregowany raport do Senatu.

Dwa tryby:
  SKANER — skanuje listę aktywów, szuka najlepszej okazji
  FOKUS  — wszystkie neurony na jeden cel
"""

import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional
try:
    from .mikro_neuron import SygnalNeuronu, MikroNeuron, Roj
except ImportError:
    from mikro_neuron import SygnalNeuronu, MikroNeuron, Roj

logger = logging.getLogger("Legatus")


@dataclass
class RaportLegatusa:
    symbol: str
    tryb: str                      # SKANER / FOKUS
    rezim: str                     # TREND_STRONG / RANGING / VOLATILE / PANIC / NORMAL
    kierunek: str                  # LONG / SHORT / NEUTRAL
    sila_long: float               # 0.0–1.0
    sila_short: float              # 0.0–1.0
    pewnosc_agregatu: float        # finalna siła dominującego kierunku
    aktywnych_neuronow: int
    zgodnych_neuronow: int
    sygnaly: List[SygnalNeuronu] = field(default_factory=list)
    weto: bool = False
    powod_weta: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class KandydatAktywa:
    symbol: str
    wynik: float
    kierunek: str
    raport: Optional[RaportLegatusa] = None


# ─── Wagi reżimowe dla kategorii neuronów ─────────────────────────────────────

WAGI_REZIMU = {
    "TREND_STRONG": {"T": 1.5, "M": 1.2, "O": 0.7, "L": 0.8},
    "RANGING":      {"M": 1.5, "V": 1.3, "T": 0.5},
    "VOLATILE":     {"A": 2.0, "L": 0.3, "_default": 0.7},
    "PANIC":        {"A": 3.0, "_default": 0.1},
    "NORMAL":       {},
    "ON-CHAIN_BULLISH": {"O": 2.0, "L": 0.8},
}


class Legatus:
    """
    Generał Legatus — agreguje sygnały 261 neuronów i przekazuje raport Senatowi.

    Użycie:
        legatus = Legatus(neurony=[...], min_neuronow=5, min_przewaga=0.55)
        raport = legatus.fokus("BTCUSDT", wskazniki, rezim="TREND_STRONG")
    """

    def __init__(self, neurony: List[MikroNeuron],
                 min_neuronow: int = 5,
                 min_przewaga: float = 0.55):
        self.roj = Roj(neurony)
        self.min_neuronow = min_neuronow
        self.min_przewaga = min_przewaga

    # ── Tryb FOKUS ─────────────────────────────────────────────────────────────

    def fokus(self, symbol: str, wskazniki: dict,
              rezim: str = "NORMAL") -> RaportLegatusa:
        """Koncentruje wszystkie neurony na jednym symbolu."""
        sygnaly = self.roj.zbierz_sygnaly(wskazniki)
        sygnaly = self._dostosuj_wagi(sygnaly, rezim)
        return self._agreguj(symbol, "FOKUS", rezim, sygnaly)

    # ── Tryb SKANER ────────────────────────────────────────────────────────────

    def skaner(self, watchlista: List[str],
               pobierz_wskazniki,  # callable(symbol) -> dict
               rezim: str = "NORMAL") -> List[KandydatAktywa]:
        """
        Skanuje listę aktywów. Zwraca top-3 kandydatów.

        pobierz_wskazniki: funkcja (symbol: str) -> dict z wartościami wskaźników
        """
        kandydaci = []
        for symbol in watchlista:
            try:
                wskazniki = pobierz_wskazniki(symbol)
                raport = self.fokus(symbol, wskazniki, rezim)
                kandydaci.append(KandydatAktywa(
                    symbol=symbol,
                    wynik=raport.pewnosc_agregatu,
                    kierunek=raport.kierunek,
                    raport=raport,
                ))
            except Exception as e:
                logger.error(f"[Skaner] Błąd dla {symbol}: {e}")

        kandydaci.sort(key=lambda x: x.wynik, reverse=True)
        return kandydaci[:3]

    # ── Agregacja ──────────────────────────────────────────────────────────────

    def _agreguj(self, symbol: str, tryb: str, rezim: str,
                 sygnaly: List[SygnalNeuronu]) -> RaportLegatusa:
        long_s  = [s for s in sygnaly if s.kierunek == "LONG"]
        short_s = [s for s in sygnaly if s.kierunek == "SHORT"]

        sila_l = sum(s.pewnosc_finalna * s.waga for s in long_s)
        sila_s = sum(s.pewnosc_finalna * s.waga for s in short_s)
        razem  = sila_l + sila_s + 1e-9

        prev_l = sila_l / razem
        prev_s = sila_s / razem

        if prev_l >= prev_s:
            kierunek = "LONG"
            pewnosc  = prev_l
            zgodnych = len(long_s)
        else:
            kierunek = "SHORT"
            pewnosc  = prev_s
            zgodnych = len(short_s)

        if pewnosc < 0.5:
            kierunek = "NEUTRAL"

        # Filtr minimum
        weto = False
        powod = ""
        if len(sygnaly) < self.min_neuronow:
            weto = True
            powod = f"Za mało aktywnych neuronów: {len(sygnaly)} < {self.min_neuronow}"
        elif pewnosc < self.min_przewaga and kierunek != "NEUTRAL":
            weto = True
            powod = f"Za słaba przewaga: {pewnosc:.2%} < {self.min_przewaga:.0%}"
        elif rezim == "PANIC":
            weto = True
            powod = "Reżim PANIC — system w trybie obronnym"

        return RaportLegatusa(
            symbol=symbol,
            tryb=tryb,
            rezim=rezim,
            kierunek=kierunek if not weto else "NEUTRAL",
            sila_long=round(prev_l, 4),
            sila_short=round(prev_s, 4),
            pewnosc_agregatu=round(pewnosc, 4),
            aktywnych_neuronow=len(sygnaly),
            zgodnych_neuronow=zgodnych,
            sygnaly=sygnaly,
            weto=weto,
            powod_weta=powod,
        )

    def _dostosuj_wagi(self, sygnaly: List[SygnalNeuronu],
                       rezim: str) -> List[SygnalNeuronu]:
        """Modyfikuje wagi neuronów zgodnie z bieżącym reżimem."""
        mapa = WAGI_REZIMU.get(rezim, {})
        if not mapa:
            return sygnaly

        default = mapa.get("_default", 1.0)
        wynik = []
        for s in sygnaly:
            k = getattr(s, "_kategoria", None)  # neurony mogą mieć kategorię w przyszłości
            mnoznik = mapa.get(k, default) if k else default
            if mnoznik != 1.0:
                import copy
                s2 = copy.copy(s)
                s2.waga = max(1, min(10, round(s.waga * mnoznik)))
                s2.policz_finalna()
                wynik.append(s2)
            else:
                wynik.append(s)
        return wynik


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

    from imperium.legiony.mikro_neuron import NeuronStochRSI, NeuronFundingRate

    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')

    neurony = [NeuronStochRSI(), NeuronFundingRate()]
    legatus = Legatus(neurony, min_neuronow=1, min_przewaga=0.4)

    wskazniki = {"StochRSI": 15.0, "FundingRate": 0.0002}
    raport = legatus.fokus("BTCUSDT", wskazniki, rezim="TREND_STRONG")

    print(f"\n=== Raport Legatusa: {raport.symbol} ===")
    print(f"Tryb: {raport.tryb} | Reżim: {raport.rezim}")
    print(f"Kierunek: {raport.kierunek} | Pewność: {raport.pewnosc_agregatu:.2%}")
    print(f"Siła LONG: {raport.sila_long:.2%} | Siła SHORT: {raport.sila_short:.2%}")
    print(f"Neurony: {raport.aktywnych_neuronow} aktywnych, {raport.zgodnych_neuronow} zgodnych")
    if raport.weto:
        print(f"⛔ WETO: {raport.powod_weta}")
    else:
        print("✅ Gotowy dla Senatu")
