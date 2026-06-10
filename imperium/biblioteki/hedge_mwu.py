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

    def __init__(self, eta: float = 0.5, min_waga: float = 1e-6,
                 alpha_share: float = 0.02):
        """
        eta: tempo uczenia (>0). Większe = szybsza, bardziej nerwowa adaptacja.
             0.5 to rozsądny default dla strumieni o umiarkowanym szumie.
        min_waga: podłoga wagi surowej — ekspert nigdy nie umiera całkowicie
                  (może wrócić do łask, gdy znów zacznie trafiać). Prawo XV.
        alpha_share: Fixed-Share (W-280, Herbster & Warmuth 1998). Po każdej
             rundzie ułamek α masy wraca równo do puli:
                 w_i ← (1−α)·w_i + α·średnia(wag)
             Czysty Hedge (α=0) ma strukturalną wadę na rynkach NIESTACJONARNYCH:
             zakopana waga wraca tylko mnożnikowo (≈nigdy), nawet gdy reżim się
             zmienił i ekspert znów trafia. Fixed-Share: żal O(1/√T) przy zmianach
             reżimu vs STAŁY żal Hedge. Źródła: https://arxiv.org/pdf/2106.13021,
             https://arxiv.org/pdf/1008.4532. α=0 → dokładnie stary HedgeMWU.
        """
        if eta <= 0:
            raise ValueError("eta musi być > 0")
        if not (0.0 <= alpha_share < 1.0):
            raise ValueError("alpha_share musi być w [0, 1)")
        self.eta = eta
        self.min_waga = min_waga
        self.alpha_share = alpha_share
        self.wagi_raw: Dict[str, float] = {}   # nieznormalizowane wagi ekspertów
        self.rundy: Dict[str, int] = {}        # ile wyników widział dany ekspert

    def _waga(self, klucz: str) -> float:
        return self.wagi_raw.get(klucz, 1.0)

    def aktualizuj(self, klucz: str, strata: float):
        """
        Jedna runda dla eksperta: strata ∈ [0,1] (0=trafił, 1=pomylił się).
        Krok 1 (Hedge):       w ← max(min_waga, w · exp(-η·strata))
        Krok 2 (Fixed-Share): w_i ← (1−α)·w_i + α·średnia(wag) dla WSZYSTKICH
        znanych ekspertów — droga powrotu dla zakopanych wag (W-280).
        """
        strata = max(0.0, min(1.0, strata))
        w = self._waga(klucz) * math.exp(-self.eta * strata)
        self.wagi_raw[klucz] = max(self.min_waga, w)
        self.rundy[klucz] = self.rundy.get(klucz, 0) + 1
        if self.alpha_share > 0.0 and len(self.wagi_raw) > 1:
            srednia = sum(self.wagi_raw.values()) / len(self.wagi_raw)
            for k in self.wagi_raw:
                self.wagi_raw[k] = ((1.0 - self.alpha_share) * self.wagi_raw[k]
                                    + self.alpha_share * srednia)

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


class HedgeMWUzPamieciaRezimu(HedgeMWU):
    """
    💎 W-285.1 | "Pretorianin Pamięci Reżimów" — ORYGINALNY wariant Imperium.

    DLA NOWICJUSZA: Fixed-Share (W-280) ratuje zakopane wagi, dosypując im masę
    RÓWNO (uniform). Ale my wiemy więcej: Namiestnik mówi nam, JAKI jest reżim
    (TREND/RANGING/VOLATILE...). Ten wariant pamięta, jakie wagi miał każdy
    neuron W KAŻDYM REŻIMIE z przeszłości — i gdy reżim wraca, dosypywana masa
    idzie wg TAMTYCH wag, nie uniform. Neurony mean-reversion odzyskują siłę
    NATYCHMIAST, gdy wraca RANGING — bez rozgrzewki od zera.

    Inspiracja literaturowa: "sharing to past posteriors" (Bousquet & Warmuth,
    JMLR 2002, https://jmlr.org/papers/v3/bousquet02b.html) miesza do PRZESZŁYCH
    rozkładów indeksowanych CZASEM. Nasz oryginalny twist: indeksowanie REŻIMEM
    z Namiestnika — przeszłość ma sens przez podobieństwo rynku, nie kalendarz.

    Mechanika:
      • ustaw_rezim(r) — Dyrygent/Namiestnik woła przy każdej zmianie reżimu.
      • po kroku Hedge: w_i ← (1−α)·w_i + α·pamięć[r][i]
        (pamięć[r] = EMA znormalizowanych wag obserwowanych w reżimie r;
         brak pamięci dla r → fallback uniform = czysty Fixed-Share).
      • pamięć aktualizowana po każdej rundzie (EMA, beta_pamieci).
    """

    def __init__(self, eta: float = 0.5, min_waga: float = 1e-6,
                 alpha_share: float = 0.02, beta_pamieci: float = 0.05):
        super().__init__(eta=eta, min_waga=min_waga, alpha_share=alpha_share)
        if not (0.0 < beta_pamieci <= 1.0):
            raise ValueError("beta_pamieci musi być w (0, 1]")
        self.beta_pamieci = beta_pamieci
        self.rezim: str = "NORMAL"
        # pamięć: rezim → {klucz: znormalizowana waga (EMA)}
        self.pamiec: Dict[str, Dict[str, float]] = {}

    def ustaw_rezim(self, rezim: str):
        """Wołane przez Dyrygenta/Namiestnika przy każdej klasyfikacji reżimu."""
        if rezim:
            self.rezim = rezim

    def aktualizuj(self, klucz: str, strata: float):
        # Krok 1+2: Hedge + mixing (nadpisany kierunek mieszania niżej)
        strata = max(0.0, min(1.0, strata))
        w = self._waga(klucz) * math.exp(-self.eta * strata)
        self.wagi_raw[klucz] = max(self.min_waga, w)
        self.rundy[klucz] = self.rundy.get(klucz, 0) + 1
        if self.alpha_share > 0.0 and len(self.wagi_raw) > 1:
            cel = self._cel_mieszania()
            suma = sum(self.wagi_raw.values())
            for k in self.wagi_raw:
                self.wagi_raw[k] = ((1.0 - self.alpha_share) * self.wagi_raw[k]
                                    + self.alpha_share * suma * cel.get(
                                        k, 1.0 / len(self.wagi_raw)))
        # Krok 3: zapisz obecny rozkład do pamięci bieżącego reżimu (EMA)
        self._zapamietaj()

    def _cel_mieszania(self) -> Dict[str, float]:
        """Rozkład docelowy mixing: pamięć reżimu albo uniform (fallback W-280)."""
        pam = self.pamiec.get(self.rezim)
        if not pam:
            n = len(self.wagi_raw)
            return {k: 1.0 / n for k in self.wagi_raw}
        # normalizuj pamięć do sumy 1 na znanych ekspertach
        suma = sum(pam.get(k, 0.0) for k in self.wagi_raw)
        if suma <= 0:
            n = len(self.wagi_raw)
            return {k: 1.0 / n for k in self.wagi_raw}
        return {k: pam.get(k, 0.0) / suma for k in self.wagi_raw}

    def _zapamietaj(self):
        wagi = self.wagi()
        pam = self.pamiec.setdefault(self.rezim, {})
        for k, w in wagi.items():
            stara = pam.get(k, w)
            pam[k] = (1.0 - self.beta_pamieci) * stara + self.beta_pamieci * w


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
