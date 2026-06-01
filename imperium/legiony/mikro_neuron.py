"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       MikroNeuron — Bazowa klasa roju Imperium v1.0                          ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Bazowa klasa dla WSZYSTKICH mikro-neuronów (81+ wg docs/KATALOG_NEURONOW.md).

Każdy neuron:
  - ma swój klucz (np. "X-02"), legion, kategorię, wagę
  - NIE liczy matematyki sam (Prawo I) — pyta Bramę Kalkulatora
  - produkuje ustandaryzowany SygnalNeuronu
  - filtr anty-manipulacja może go zdyskwalifikować zanim trafi do Senatu

Nowy neuron = dziedziczysz po MikroNeuron i nadpisujesz interpretuj().
"""

import time
import hashlib
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger("MikroNeuron")


# ─── Schemat sygnału (zgodny z docs/LEGIONY_ARCHITEKTURA.md) ──────────────────

@dataclass
class SygnalNeuronu:
    neuron_id: str                       # np. "X-02"
    legion: str                          # SCALP / SWING / INVEST / LEVERAGE / WSPOLNY
    wskaznik: str                        # np. "StochRSI"
    wartosc: Optional[float]             # surowa wartość z Bramy
    kierunek: str                        # LONG / SHORT / NEUTRAL
    pewnosc: float = 0.0                 # 0.0–1.0 (siła argumentu ZA)
    pewnosc_przeciwnika: float = 0.0     # siła argumentu PRZECIW
    pewnosc_finalna: float = 0.0         # po uwzględnieniu przeciwnika
    powody: List[str] = field(default_factory=list)
    waga: int = 5                        # waga ważności 1-10 (dynamiczna)
    timestamp: float = field(default_factory=time.time)
    hash_danych: str = ""                # SHA-256 z Bramy (dowód nienaruszalności)

    def policz_finalna(self):
        """Pewność finalna = pewność ZA minus przeciwnik, przeskalowana wagą."""
        netto = max(0.0, self.pewnosc - self.pewnosc_przeciwnika)
        self.pewnosc_finalna = round(netto * (self.waga / 10.0), 4)
        return self.pewnosc_finalna


# ─── Bazowa klasa neuronu ─────────────────────────────────────────────────────

class MikroNeuron(ABC):
    """Bazowa klasa. Każdy konkretny neuron dziedziczy i nadpisuje interpretuj()."""

    # Te pola nadpisuje każdy konkretny neuron
    KLUCZ: str = "???-00"
    LEGION: str = "WSPOLNY"
    WSKAZNIK: str = "abstract"
    KATEGORIA: str = "?"   # M/T/V/F/O/L/S/A
    WAGA: int = 5

    def __init__(self):
        if self.KLUCZ == "???-00":
            raise NotImplementedError(f"{type(self).__name__} musi ustawić KLUCZ.")

    @abstractmethod
    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        """
        Czyta gotowe liczby z Bramy (dict) → zwraca SygnalNeuronu.
        NIE liczy wskaźnika sam (Prawo I). Tylko interpretuje wynik.
        """
        ...

    def _bazowy_sygnal(self, wartosc, kierunek, pewnosc, powody, hash_danych="") -> SygnalNeuronu:
        """Pomocnik — buduje sygnał z metadanymi neuronu."""
        s = SygnalNeuronu(
            neuron_id=self.KLUCZ,
            legion=self.LEGION,
            wskaznik=self.WSKAZNIK,
            wartosc=wartosc,
            kierunek=kierunek,
            pewnosc=pewnosc,
            powody=powody,
            waga=self.WAGA,
            hash_danych=hash_danych,
        )
        s.policz_finalna()
        return s


# ─── Przykładowa implementacja: Neuron X-02 (StochRSI) ───────────────────────

class NeuronStochRSI(MikroNeuron):
    """X-02 | Legio X | Stochastic RSI — ekstrema wykupienia/wyprzedania."""
    KLUCZ = "X-02"
    LEGION = "SCALP"
    WSKAZNIK = "StochRSI"
    KATEGORIA = "M"
    WAGA = 6

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        v = wskazniki.get("StochRSI")
        if v is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych StochRSI."])
        if v < 20:
            return self._bazowy_sygnal(v, "LONG", 0.75,
                [f"StochRSI={v:.1f} < 20 → strefa wyprzedania, możliwe odbicie"])
        if v > 80:
            return self._bazowy_sygnal(v, "SHORT", 0.75,
                [f"StochRSI={v:.1f} > 80 → strefa wykupienia, możliwa korekta"])
        return self._bazowy_sygnal(v, "NEUTRAL", 0.3, [f"StochRSI={v:.1f} w strefie neutralnej"])


# ─── Przykładowa implementacja: Neuron VI-01 (Funding Rate) ──────────────────

class NeuronFundingRate(MikroNeuron):
    """VI-01 | Legio VI | Funding Rate — przeważenie long/short na futures."""
    KLUCZ = "VI-01"
    LEGION = "LEVERAGE"
    WSKAZNIK = "FundingRate"
    KATEGORIA = "L"
    WAGA = 9

    def interpretuj(self, wskazniki: dict) -> SygnalNeuronu:
        v = wskazniki.get("FundingRate")
        if v is None:
            return self._bazowy_sygnal(None, "NEUTRAL", 0.0, ["Brak danych Funding Rate."])
        # >0.03% = za dużo longów (ryzyko long squeeze → kontra SHORT)
        if v > 0.0003:
            return self._bazowy_sygnal(v, "SHORT", 0.7,
                [f"Funding={v*100:.4f}% > 0.03% → za dużo longów, ryzyko long squeeze"])
        if v < -0.0003:
            return self._bazowy_sygnal(v, "LONG", 0.7,
                [f"Funding={v*100:.4f}% < -0.03% → za dużo shortów, ryzyko short squeeze"])
        return self._bazowy_sygnal(v, "NEUTRAL", 0.3, [f"Funding={v*100:.4f}% zrównoważony"])


# ─── Rój — agregator neuronów jednego legionu ────────────────────────────────

class Roj:
    """Zbiera neurony, odpala je na danych z Bramy, zwraca listę sygnałów."""

    def __init__(self, neurony: List[MikroNeuron]):
        self.neurony = neurony

    def zbierz_sygnaly(self, wskazniki: dict) -> List[SygnalNeuronu]:
        sygnaly = []
        for n in self.neurony:
            try:
                sygnaly.append(n.interpretuj(wskazniki))
            except Exception as e:
                logger.error(f"[Rój] Neuron {n.KLUCZ} padł: {e}")
        return sygnaly


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')

    przyklad = {"StochRSI": 18.5, "FundingRate": 0.0005}
    roj = Roj([NeuronStochRSI(), NeuronFundingRate()])

    print("=== Rój Imperium — demo 2 neuronów ===\n")
    for s in roj.zbierz_sygnaly(przyklad):
        print(f"[{s.neuron_id}] {s.wskaznik}: {s.kierunek} "
              f"(pewność {s.pewnosc:.0%}, finalna {s.pewnosc_finalna:.2f}, waga {s.waga})")
        for p in s.powody:
            print(f"     - {p}")
        print()
