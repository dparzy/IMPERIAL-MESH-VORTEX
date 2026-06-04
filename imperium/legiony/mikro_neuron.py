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
    kategoria: str = "?"                 # M/T/V/F/O/L/S/A — dla wag reżimowych (Prawo XV)
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
    # Legenda KATEGORIA (jedno źródło prawdy, zgodne z docs/KATALOG_NEURONOW.md):
    #   M=Momentum  T=Trend  V=Zmienność  F=Flow/Wolumen  O=On-chain
    #   L=Leverage  R=Reżim/Sentyment  S=Struktura(SMC)  A=Anty-manipulacja
    #   K=Makro/Intermarket  E=Entropia/AI  G=Geo/Regionalne
    #   H=Hurst/Pamięć długiego zasięgu (meta-brama reżimu)
    #   N=Entropia/Informacja (Permutation Entropy — meta-brama chaosu)
    KATEGORIA: str = "?"
    WAGA: int = 5

    # Dostępność — ustaw False gdy neuron wymaga zewnętrznego API niedostępnego przez Bramę.
    # Rój automatycznie pomija niedostępne neurony zamiast produkować wieczne NEUTRAL.
    DOSTEPNY: bool = True
    POWOD_NIEDOSTEPNOSCI: str = ""

    # Status elitarny (Prawo XX) — ustaw True gdy neuron spełnia kryteria elity.
    # Status OTWARTY i AKTUALIZOWALNY: nadawany/odbierany pomiarem, nie opinią.
    ELITARNY: bool = False
    POWOD_ELITARNOSCI: str = ""   # które kryteria E1–E7 spełnia (do audytu)

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
            kategoria=self.KATEGORIA,
            hash_danych=hash_danych,
        )
        s.policz_finalna()
        return s


# UWAGA (Prawo XIX): klasy neuronów NIE mieszkają już w tym pliku bazowym.
# Każdy neuron żyje w swoim module (neurony/*.py) i jest rejestrowany w rejestr.py.
#   • X-02 StochRSI  → przeniesiony do neurony/momentum.py (aktywny, dane STOCHRSI z Bramy)
#   • VI-01 Funding  → wycofany jako redundantny z NeuronFundingExtreme (Prawo XVI);
#                      kanoniczny neuron funding to NeuronFundingExtreme w neurony/psychologia.py
# Dzięki temu nie ma "neuronów-sierot" z kodem, ale poza rojem (Prawo XV/XIX).


# ─── Rój — agregator neuronów jednego legionu ────────────────────────────────

class Roj:
    """Zbiera neurony, odpala je na danych z Bramy, zwraca listę sygnałów."""

    def __init__(self, neurony: List[MikroNeuron]):
        self.neurony = neurony
        # Loguj niedostępne neurony przy starcie (raz, nie co sygnał)
        for n in neurony:
            if not n.DOSTEPNY:
                logger.warning(
                    f"[Rój] Neuron {n.KLUCZ} ({n.WSKAZNIK}) NIEDOSTĘPNY — pomijany. "
                    f"Powód: {n.POWOD_NIEDOSTEPNOSCI or 'brak danych z Bramy'}"
                )

    def zbierz_sygnaly(self, wskazniki: dict) -> List[SygnalNeuronu]:
        sygnaly = []
        for n in self.neurony:
            if not n.DOSTEPNY:
                continue  # pomiń zombie — nie produkuj fałszywych NEUTRAL
            try:
                sygnaly.append(n.interpretuj(wskazniki))
            except Exception as e:
                logger.error(f"[Rój] Neuron {n.KLUCZ} padł: {e}")
        return sygnaly

    def lista_niedostepnych(self) -> List[str]:
        """Które neurony są wyciszone i dlaczego."""
        return [
            f"{n.KLUCZ} ({n.WSKAZNIK}): {n.POWOD_NIEDOSTEPNOSCI}"
            for n in self.neurony if not n.DOSTEPNY
        ]


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
