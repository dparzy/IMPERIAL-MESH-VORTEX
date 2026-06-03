"""
HedgeMWU — Multiplicative Weights Update / algorytm Hedge (wizja W-049).

Online, adaptacyjne ważenie ekspertów (neuronów) z gwarancją regretu
O(√(T·ln N)) — Freund & Schapire (1997), "A Decision-Theoretic Generalization
of On-Line Learning". Źródło: https://doi.org/10.1006/jcss.1997.1504

Dla nowicjusza:
  Mamy N "ekspertów" (każdy neuron to ekspert). Po każdym rozstrzygniętym
  trade'cie sprawdzamy, kto miał rację (kierunek zgodny z kierunkiem zyskownym),
  a kto się pomylił. Ekspertom, którzy się mylą, OBNIŻAMY wagę wykładniczo
  (×exp(-η)), trafnym zostawiamy. Po wielu rundach wagi same "znajdują" najlepsze
  neurony — bez ręcznego strojenia. To jest "brakujący mózg" Legata: zamiast wag
  ustawianych na sztywno, uczą się one z wyników w czasie.

Różnica od Igrzysk (oba żywią Legata mnożnikami {klucz: mnoznik}):
  • Igrzyska  — BATCH: okresowy (np. co 30 dni) ranking z dyskretnymi rangami
                (Tiro→Aquilifer), liczony od zera na oknie logów.
  • HedgeMWU  — ONLINE: strumieniowy, inkrementalny, z teoretyczną granicą
                regretu; aktualizuje wagę po KAŻDYM wyniku. Komplementarne
                (Prawo XVI — różna informacja: stan ciągły vs ranking okresowy).

Neutralność (Prawo XV — brak zniekształcenia, brak martwego głosu):
  Gdy wszyscy eksperci mają równe wagi (stan początkowy / brak danych),
  mnozniki() zwraca 1.0 dla każdego → Legatus działa jak bez MWU. Mnożnik
  oddala się od 1.0 dopiero, gdy historia faktycznie różnicuje neurony.
"""

import math
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("HedgeMWU")


class HedgeMWU:
    """
    Użycie:
        mwu = HedgeMWU(eta=0.5)
        mwu.zarejestruj_wynik("X-01", "LONG", zyskowny_kierunek="LONG")  # trafił
        mwu.zarejestruj_wynik("X-07", "SHORT", zyskowny_kierunek="LONG") # pomylił
        mnozniki = mwu.mnozniki()        # {klucz: mnoznik≈1.0} do Legatusa

    Można też podpiąć jako obserwatora Igrzysk (ten sam strumień wyników):
        ig = Igrzyska(); ig.obserwatorzy.append(mwu); ig.przetworz_logi(logi)
    """

    def __init__(self, eta: float = 0.5, min_waga: float = 1e-6):
        """
        eta: tempo uczenia (>0). Większe = szybsza, bardziej nerwowa adaptacja.
             0.5 to rozsądny default dla strumieni o umiarkowanym szumie.
        min_waga: podłoga wagi surowej — ekspert nigdy nie umiera całkowicie
                  (może wrócić do łask, gdy znów zacznie trafiać). Prawo XV.
        """
        if eta <= 0:
            raise ValueError("eta musi być > 0")
        self.eta = eta
        self.min_waga = min_waga
        self.wagi_raw: Dict[str, float] = {}   # nieznormalizowane wagi ekspertów
        self.rundy: Dict[str, int] = {}        # ile wyników widział dany ekspert

    def _waga(self, klucz: str) -> float:
        return self.wagi_raw.get(klucz, 1.0)

    def aktualizuj(self, klucz: str, strata: float):
        """
        Jedna runda dla eksperta: strata ∈ [0,1] (0=trafił, 1=pomylił się).
        w ← max(min_waga, w · exp(-η·strata)).
        """
        strata = max(0.0, min(1.0, strata))
        w = self._waga(klucz) * math.exp(-self.eta * strata)
        self.wagi_raw[klucz] = max(self.min_waga, w)
        self.rundy[klucz] = self.rundy.get(klucz, 0) + 1

    def zarejestruj_wynik(self, klucz: str, kierunek: str,
                          zyskowny_kierunek: str,
                          contribution: Optional[float] = None,
                          timeliness: Optional[float] = None):
        """
        Sygnatura zgodna z Igrzyska.zarejestruj_wynik (by działać jako obserwator).
        contribution/timeliness są ignorowane — MWU patrzy tylko na trafność
        kierunku (binarna strata). NEUTRAL nie jest karany ani nagradzany.
        """
        if kierunek not in ("LONG", "SHORT"):
            return
        strata = 0.0 if kierunek == zyskowny_kierunek else 1.0
        self.aktualizuj(klucz, strata)

    def wagi(self) -> Dict[str, float]:
        """Wagi znormalizowane do sumy 1 (rozkład prawdopodobieństwa nad ekspertami)."""
        if not self.wagi_raw:
            return {}
        suma = sum(self.wagi_raw.values())
        if suma <= 0:
            return {k: 1.0 / len(self.wagi_raw) for k in self.wagi_raw}
        return {k: w / suma for k, w in self.wagi_raw.items()}

    def mnozniki(self) -> Dict[str, float]:
        """
        Mnożniki wokół 1.0 do wstrzyknięcia Legatusowi: mnoznik = waga_norm · N.
        Stan neutralny (równe wagi) → wszystkie 1.0 (brak zniekształcenia).
        Trafni eksperci > 1.0, myleni < 1.0.
        """
        wagi = self.wagi()
        n = len(wagi)
        if n == 0:
            return {}
        return {k: round(w * n, 6) for k, w in wagi.items()}

    @classmethod
    def z_logow(cls, logi: list, eta: float = 0.5) -> "HedgeMWU":
        """
        Buduje MWU ze strumienia logów Pamięci Absolutnej, używając TEJ SAMEJ
        logiki parowania SYGNAŁ↔TRADE_CLOSE co Igrzyska (DRY — bez duplikacji
        reguł). Zwraca gotowy MWU z online-wyuczonymi wagami.
        """
        try:
            from imperium.biblioteki.igrzyska import Igrzyska
        except ImportError:
            from igrzyska import Igrzyska
        mwu = cls(eta=eta)
        ig = Igrzyska()
        ig.obserwatorzy.append(mwu)   # MWU dostaje ten sam strumień wyników
        ig.przetworz_logi(logi)
        return mwu

    def raport(self) -> List[dict]:
        """Tabela ekspertów posortowana wg mnożnika (do diagnostyki/logów)."""
        mn = self.mnozniki()
        wiersze = [
            {"klucz": k, "mnoznik": mn[k], "waga": round(self.wagi()[k], 4),
             "rundy": self.rundy.get(k, 0)}
            for k in mn
        ]
        wiersze.sort(key=lambda x: x["mnoznik"], reverse=True)
        return wiersze


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import random
    logging.basicConfig(level=logging.INFO)
    random.seed(42)

    mwu = HedgeMWU(eta=0.5)
    for _ in range(40):
        zysk = random.choice(["LONG", "SHORT"])
        # X-01 trafia 85%, X-02 50%, X-07 25%
        mwu.zarejestruj_wynik("X-01", zysk if random.random() < 0.85 else
                              ("SHORT" if zysk == "LONG" else "LONG"), zysk)
        mwu.zarejestruj_wynik("X-02", zysk if random.random() < 0.50 else
                              ("SHORT" if zysk == "LONG" else "LONG"), zysk)
        mwu.zarejestruj_wynik("X-07", zysk if random.random() < 0.25 else
                              ("SHORT" if zysk == "LONG" else "LONG"), zysk)

    print("MWU online mnożniki (po 40 rundach):")
    for w in mwu.raport():
        print(f"  {w['klucz']}: ×{w['mnoznik']:.3f}  (waga {w['waga']}, rund {w['rundy']})")
    assert mwu.mnozniki()["X-01"] > mwu.mnozniki()["X-07"], \
        "Trafny ekspert musi mieć wyższy mnożnik niż mylący się"
    print("\n✅ HedgeMWU działa — trafny neuron zyskał wagę, mylący stracił.")
