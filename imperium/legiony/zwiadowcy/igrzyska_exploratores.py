"""
🏛️ IMV-ORI | Igrzyska Exploratores — osobna skala oceniania dla Zwiadowców

DLACZEGO OSOBNA SKALA:
  Exploratores sygnalizują rzadziej niż zwykłe neurony — np. Higuchi FD
  potrzebuje 200 barów i daje sygnał raz na kilka godzin. Gdyby oceniać go
  tą samą skalą co RSI (który daje sygnał co świecę), FD zawsze przegrałby
  statystycznie (mała próba = wysoka wariancja accuracy).

  Analogia: oceniamy snajpera i karabiniera inaczej. Snajper oddaje 5 strzałów
  dziennie — każdy musi być celny. Karabinier oddaje 500. Metryki muszą być
  dostosowane do charakteru zadania.

RÓŻNICE SKALI EXPLORATORES vs STANDARD:
  ┌─────────────────┬─────────────────┬─────────────────┐
  │ Ranga           │ Standard (prog) │ Exploratores    │
  ├─────────────────┼─────────────────┼─────────────────┤
  │ Aquilifer       │ 0.93            │ 0.88 (łatwiej)  │
  │ PrimusPilus     │ 0.85            │ 0.80            │
  │ Centurion       │ 0.73            │ 0.68            │
  │ Optio           │ 0.60            │ 0.55            │
  │ Miles           │ 0.45            │ 0.40            │
  │ Tiro            │ 0.00            │ 0.00            │
  └─────────────────┴─────────────────┴─────────────────┘

  Ale waga×mnożnik jest WYŻSZA:
  ┌─────────────────┬──────────┬───────────────┐
  │ Ranga           │ Standard │ Exploratores  │
  ├─────────────────┼──────────┼───────────────┤
  │ Aquilifer       │ ×2.0     │ ×2.5          │
  │ PrimusPilus     │ ×1.6     │ ×2.0          │
  │ Centurion       │ ×1.3     │ ×1.6          │
  │ Optio           │ ×1.0     │ ×1.2          │
  │ Miles           │ ×0.8     │ ×0.9          │
  │ Tiro            │ ×0.5     │ ×0.5          │
  └─────────────────┴──────────┴───────────────┘

FORMUŁA WYNIK_NEURONU dla Exploratores:
  Tak samo jak standard, ale z dodatkową premią za rzadkość:
  WYNIK = 0.35×Accuracy + 0.30×Precision + 0.20×Contribution + 0.15×Stability
  (Timeliness usunięty — Exploratores z definicji wolniejsi, to nie wada)
  + PREMIA_RZADKOSCI = max(0, (1 - n_sygnaly/n_sygnaly_avg) × 0.05)
    Jeśli zwiadowca sygnalizuje 2× rzadziej od średniej → +0.05 do wyniku.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


# ─── Rangi Exploratores ───────────────────────────────────────────────────────

@dataclass
class RangaExploratores:
    nazwa: str
    prog_wynik: float    # Próg WYNIK_NEURONU do awansu
    mnoznik: float       # Mnożnik wagi w Legatusie


RANGI_EXPLORATORES = [
    RangaExploratores("Aquilifer",   0.88, 2.5),
    RangaExploratores("PrimusPilus", 0.80, 2.0),
    RangaExploratores("Centurion",   0.68, 1.6),
    RangaExploratores("Optio",       0.55, 1.2),
    RangaExploratores("Miles",       0.40, 0.9),
    RangaExploratores("Tiro",        0.00, 0.5),
]


def okresl_range_exploratores(wynik: float) -> RangaExploratores:
    for ranga in RANGI_EXPLORATORES:
        if wynik >= ranga.prog_wynik:
            return ranga
    return RANGI_EXPLORATORES[-1]  # Tiro


# ─── Statystyki Zwiadowcy ────────────────────────────────────────────────────

@dataclass
class StatystykaZwiadowcy:
    """Śledzi historię wyników jednego ZwiadowcyElitarnego."""
    klucz: str
    tp: int = 0       # True Positive (prawidłowy kierunek + zysk)
    fp: int = 0       # False Positive (zły kierunek lub strata)
    flipy: int = 0    # Zmiany kierunku z baru na bar
    sygnaly: int = 0  # Łączna liczba sygnałów (tylko LONG/SHORT, nie NEUTRAL)
    neutralne: int = 0  # Liczba NEUTRAL (dla kalkulacji rzadkości)
    contribution_sum: float = 0.0  # Suma contribution_score z Legatusa

    # Exploratores: dodatkowe metryki jakości obliczeń
    srednia_pewnosc_metody: float = 1.0  # Avg pewnosc_metody z RaportZwiadowcy
    sredni_czas_obliczen_ms: float = 0.0

    @property
    def accuracy(self) -> float:
        total = self.tp + self.fp
        return self.tp / total if total > 0 else 0.0

    @property
    def precision_dominujaca(self) -> float:
        """Jak często sygnał ma dominującą pewność (>0.70)."""
        return self.accuracy  # uproszczenie bez danych per-sygnał

    @property
    def contribution(self) -> float:
        return self.contribution_sum / self.sygnaly if self.sygnaly > 0 else 0.0

    @property
    def stability(self) -> float:
        """Odwrotność flip-flop. Exploratores z definicji stabilniejsze."""
        if self.sygnaly <= 1:
            return 1.0
        return max(0.0, 1.0 - self.flipy / (self.sygnaly - 1))

    @property
    def wspolczynnik_rzadkosci(self) -> float:
        """Ile % barów daje sygnał (1.0 = każdy, 0.0 = nigdy)."""
        total = self.sygnaly + self.neutralne
        return self.sygnaly / total if total > 0 else 0.0

    def wynik(self, sredni_wspolczynnik_rzadkosci: float = 0.5) -> float:
        """
        WYNIK_NEURONU dla Exploratores.
        Bez Timeliness + z premią za rzadkość.
        """
        bazowy = round(
            0.35 * self.accuracy
            + 0.30 * self.precision_dominujaca
            + 0.20 * self.contribution
            + 0.15 * self.stability,
            4
        )
        # Premia za rzadkość: sygnalizuje rzadziej od średniej → +0.05
        premia = 0.0
        if (sredni_wspolczynnik_rzadkosci > 0
                and self.wspolczynnik_rzadkosci < sredni_wspolczynnik_rzadkosci):
            premia = min(0.05, (1.0 - self.wspolczynnik_rzadkosci / sredni_wspolczynnik_rzadkosci) * 0.05)
        return round(min(1.0, bazowy + premia), 4)


# ─── Silnik Igrzysk Exploratores ──────────────────────────────────────────────

@dataclass
class WpisInfamiiExp:
    klucz: str
    wynik: float
    ranga: str
    powod: str


class IgrzyskaExploratores:
    """
    Osobna instancja Igrzysk dla Dywizji Exploratores.
    Działa niezależnie od standardowych Igrzysk (biblioteki/igrzyska.py).
    Legatus może scalić obie listy wag przy agregacji.

    Użycie:
        ig = IgrzyskaExploratores()
        ig.zarejestruj_wynik("EXP-01", kierunek="LONG", tp=True, contribution=0.8)
        wagi = ig.nowe_wagi()
        ig.drukuj_kapitol()
    """

    def __init__(self) -> None:
        self.statystyki: Dict[str, StatystykaZwiadowcy] = {}
        self._prev_kierunki: Dict[str, str] = {}

    def zarejestruj_wynik(
        self,
        klucz: str,
        kierunek: str,
        tp: bool,
        contribution: float = 0.0,
        pewnosc_metody: float = 1.0,
        czas_ms: float = 0.0,
    ) -> None:
        """Rejestruje wynik jednego sygnału zwiadowcy po zamknięciu trade'u."""
        if klucz not in self.statystyki:
            self.statystyki[klucz] = StatystykaZwiadowcy(klucz=klucz)
        s = self.statystyki[klucz]

        if kierunek in ("LONG", "SHORT"):
            s.sygnaly += 1
            if tp:
                s.tp += 1
            else:
                s.fp += 1
            if klucz in self._prev_kierunki and self._prev_kierunki[klucz] != kierunek:
                s.flipy += 1
            self._prev_kierunki[klucz] = kierunek
            s.contribution_sum += contribution
        else:
            s.neutralne += 1

        # Aktualizuj średnią pewność metody (running mean)
        n = s.sygnaly + s.neutralne
        if n > 0:
            s.srednia_pewnosc_metody = (s.srednia_pewnosc_metody * (n - 1) + pewnosc_metody) / n
            s.sredni_czas_obliczen_ms = (s.sredni_czas_obliczen_ms * (n - 1) + czas_ms) / n

    def _sredni_wspolczynnik_rzadkosci(self) -> float:
        if not self.statystyki:
            return 0.5
        wartosci = [s.wspolczynnik_rzadkosci for s in self.statystyki.values()]
        return sum(wartosci) / len(wartosci)

    def wyniki_wszystkich(self) -> Dict[str, float]:
        avg_rzadkosc = self._sredni_wspolczynnik_rzadkosci()
        return {k: s.wynik(avg_rzadkosc) for k, s in self.statystyki.items()}

    def nowe_wagi(self) -> Dict[str, float]:
        """Zwraca {klucz: mnoznik} do użycia przez Legatusa."""
        wyniki = self.wyniki_wszystkich()
        return {k: okresl_range_exploratores(w).mnoznik for k, w in wyniki.items()}

    def zloty_helm(self) -> Optional[Dict]:
        """Najlepszy Zwiadowca sesji."""
        wyniki = self.wyniki_wszystkich()
        if not wyniki:
            return None
        najlepszy = max(wyniki, key=wyniki.get)
        ranga = okresl_range_exploratores(wyniki[najlepszy])
        return {
            "klucz": najlepszy,
            "wynik": wyniki[najlepszy],
            "ranga": ranga.nazwa,
            "mnoznik": ranga.mnoznik,
        }

    def lista_infamii(self) -> List[WpisInfamiiExp]:
        wyniki = self.wyniki_wszystkich()
        infamia = []
        for klucz, wynik in wyniki.items():
            ranga = okresl_range_exploratores(wynik)
            if ranga.nazwa == "Tiro":
                infamia.append(WpisInfamiiExp(
                    klucz=klucz, wynik=wynik, ranga="Tiro",
                    powod=f"accuracy={self.statystyki[klucz].accuracy:.0%}, "
                          f"sygnaly={self.statystyki[klucz].sygnaly}"
                ))
        return infamia

    def drukuj_kapitol(self, top_n: int = 5) -> None:
        wyniki = self.wyniki_wszystkich()
        ranking = sorted(wyniki.items(), key=lambda x: x[1], reverse=True)
        avg = self._sredni_wspolczynnik_rzadkosci()
        linia = "═" * 64
        print(f"\n{linia}")
        print(f"  🔭 KAPITOL EXPLORATORES — Top {top_n} Zwiadowców")
        print(f"  Avg rzadkość sygnałów: {avg:.1%}")
        print(linia)
        for i, (klucz, wynik) in enumerate(ranking[:top_n], 1):
            s = self.statystyki[klucz]
            ranga = okresl_range_exploratores(wynik)
            premia_str = "(+premia rzadkości)" if s.wspolczynnik_rzadkosci < avg else ""
            print(f"  {i}. {klucz:<10} {ranga.nazwa:<12} "
                  f"W={wynik:.3f} ×{ranga.mnoznik} | "
                  f"acc={s.accuracy:.0%} sig={s.sygnaly} {premia_str}")
        print(linia)
