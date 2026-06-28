"""
🗿 STATISTICAL JUMP MODEL — detektor reżimu z karą za skok (W-281).

ŹRÓDŁA (ZPO — pełne linki):
  • Cortese, Kolm, Lindström (2023), "What drives cryptocurrency returns?
    A sparse statistical jump model approach", Digital Finance 5:483-518,
    https://link.springer.com/article/10.1007/s42521-023-00085-x
    → na KRYPTO: 3 stany (bull/neutral/bear) najlepiej opisują zwroty.
  • Nystrup et al., "Downside Risk Reduction Using Regime-Switching Signals:
    A Statistical Jump Model Approach", https://arxiv.org/html/2402.05272v3
    → jump model bije HMM trwałością stanów (mniej fałszywych alarmów).

DLA NOWICJUSZA: to k-means ze ŚWIADOMOŚCIĄ CZASU. Zwykły k-means przypisuje
każdy bar do najbliższego centroidu — stan może migotać co bar (jak HMM na
szumie). Jump model dodaje KARĘ λ za każdą zmianę stanu między sąsiednimi
barami: zmiana opłaca się tylko, gdy dane naprawdę się przestawiły. Wynik:
trwałe reżimy (bull/neutral/bear) zamiast nerwowego przełącznika.

ALGORYTM (naprzemienny, jak w paperach):
  1. Przypisanie stanów: programowanie dynamiczne (Viterbi po koszcie):
         koszt(t, k) = ||x_t − c_k||² + λ·1[s_t ≠ s_{t−1}]
  2. Aktualizacja centroidów: c_k = średnia barów przypisanych do k.
  Iteruj do zbieżności; multi-start (kilka losowych inicjalizacji) → najlepszy.

PRAWO I: model NIE liczy wskaźników — dostaje gotową macierz cech (z Bramy).
PRAWO XVIII (plan etapowy master-switcha): to jest KLOCEK Fazy 3 — wpięcie
do klasyfikuj_rezim() dopiero po pomiarze przewagi (pomiar_namiestnik.py).
"""

import logging
from typing import Optional

import numpy as np

from imperium.legiony._jit import njit

logger = logging.getLogger("JumpModel")


@njit(cache=True)
def _viterbi_core(xs: np.ndarray, c: np.ndarray, kara: float) -> np.ndarray:
    """
    Rdzeń Viterbi (DP po koszcie) — jawne pętle, JIT-owalne przez Numba (W-380).
    Wynik IDENTYCZNY z wersją numpy (ta sama logika, ta sama konwencja argmin=pierwszy).
    Gorąca ścieżka: wołany n_startow × max_iter razy na każde dopasuj() w backteście.
    """
    t = xs.shape[0]
    k = c.shape[0]
    f = xs.shape[1]
    # koszt emisji ||x_t − c_k||² (jawne pętle — numba je kompiluje do C)
    emisja = np.empty((t, k))
    for i in range(t):
        for m in range(k):
            s = 0.0
            for d in range(f):
                diff = xs[i, d] - c[m, d]
                s += diff * diff
            emisja[i, m] = s
    koszt = np.empty((t, k))
    wstecz = np.zeros((t, k), dtype=np.int64)
    for m in range(k):
        koszt[0, m] = emisja[0, m]
    for i in range(1, t):
        # najtańszy stan w t-1 (pierwszy minimalny — jak np.argmin)
        mn = koszt[i - 1, 0]
        arg = 0
        for j in range(1, k):
            if koszt[i - 1, j] < mn:
                mn = koszt[i - 1, j]
                arg = j
        najtanszy_skok = mn + kara
        for m in range(k):
            zostan = koszt[i - 1, m]               # j == m (brak skoku)
            if zostan <= najtanszy_skok:
                koszt[i, m] = zostan + emisja[i, m]
                wstecz[i, m] = m
            else:
                koszt[i, m] = najtanszy_skok + emisja[i, m]
                wstecz[i, m] = arg
    stany = np.empty(t, dtype=np.int64)
    mn = koszt[t - 1, 0]
    arg = 0
    for j in range(1, k):
        if koszt[t - 1, j] < mn:
            mn = koszt[t - 1, j]
            arg = j
    stany[t - 1] = arg
    for i in range(t - 2, -1, -1):
        stany[i] = wstecz[i + 1, stany[i + 1]]
    return stany


class JumpModel:
    """
    Użycie:
        jm = JumpModel(n_stanow=3, kara_skoku=20.0)
        stany = jm.dopasuj(cechy)           # cechy: T×F (np. zwroty, vol, Hurst)
        nazwy = jm.nazwij_stany(zwroty)     # stan→BULL/NEUTRAL/BEAR po średnim zwrocie
        rezim_teraz = nazwy[stany[-1]]
    """

    def __init__(self, n_stanow: int = 3, kara_skoku: float = 20.0,
                 max_iter: int = 30, n_startow: int = 8, seed: int = 7):
        """
        n_stanow: liczba reżimów (3 = bull/neutral/bear wg Cortese et al. 2023).
        kara_skoku: λ ≥ 0 — koszt zmiany stanu między sąsiednimi barami.
            λ=0 → zwykły k-means po czasie (migocze); λ→∞ → jeden stan na zawsze.
            Skala zależy od wariancji cech — cechy są standaryzowane wewnętrznie,
            więc λ≈10–50 daje reżimy o trwałości tygodni na danych dziennych.
        n_startow: liczba losowych inicjalizacji (bierzemy najlepszą po koszcie).
        """
        if n_stanow < 2:
            raise ValueError("n_stanow musi być ≥ 2")
        if kara_skoku < 0:
            raise ValueError("kara_skoku musi być ≥ 0")
        self.n_stanow = n_stanow
        self.kara_skoku = kara_skoku
        self.max_iter = max_iter
        self.n_startow = n_startow
        self.seed = seed
        self.centroidy: Optional[np.ndarray] = None
        self._std_mu: Optional[np.ndarray] = None
        self._std_sd: Optional[np.ndarray] = None

    # ── API ──────────────────────────────────────────────────────────────────

    def dopasuj(self, cechy) -> np.ndarray:
        """
        Dopasowuje model do macierzy cech T×F i zwraca sekwencję stanów (T,).
        Cechy standaryzowane wewnętrznie (z-score po kolumnach).
        """
        x = np.asarray(cechy, dtype=float)
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        t, f = x.shape
        if t < self.n_stanow * 5:
            raise ValueError(f"za mało barów ({t}) na {self.n_stanow} stanów")
        # standaryzacja (kolumny o zerowej wariancji → zostają zerami, nie NaN)
        self._std_mu = x.mean(axis=0)
        sd = x.std(axis=0)
        sd[sd == 0] = 1.0
        self._std_sd = sd
        xs = (x - self._std_mu) / self._std_sd

        rng = np.random.default_rng(self.seed)
        najlepszy_koszt = np.inf
        najlepsze_stany = None
        najlepsze_c = None
        for _ in range(self.n_startow):
            idx = rng.choice(t, size=self.n_stanow, replace=False)
            c = xs[idx].copy()
            stany = None
            for _ in range(self.max_iter):
                nowe = self._viterbi(xs, c)
                if stany is not None and np.array_equal(nowe, stany):
                    break
                stany = nowe
                for k in range(self.n_stanow):
                    maska = stany == k
                    if maska.any():
                        c[k] = xs[maska].mean(axis=0)
            koszt = self._koszt(xs, stany, c)
            if koszt < najlepszy_koszt:
                najlepszy_koszt, najlepsze_stany, najlepsze_c = koszt, stany, c
        self.centroidy = najlepsze_c
        return najlepsze_stany

    def przypisz_ostatni(self, cechy_bar) -> int:
        """Stan pojedynczego nowego baru (bez kary — najbliższy centroid)."""
        if self.centroidy is None:
            raise RuntimeError("najpierw dopasuj()")
        xb = (np.asarray(cechy_bar, dtype=float).reshape(1, -1)
              - self._std_mu) / self._std_sd
        d = ((self.centroidy - xb) ** 2).sum(axis=1)
        return int(np.argmin(d))

    @staticmethod
    def nazwij_stany(zwroty, stany) -> dict:
        """
        Mapuje numery stanów na nazwy reżimów po ŚREDNIM ZWROCIE w stanie:
        najwyższy → BULL, najniższy → BEAR, reszta → NEUTRAL.
        (Konwencja Cortese/Kolm/Lindström 2023 — 3 stany na krypto.)
        """
        z = np.asarray(zwroty, dtype=float)
        s = np.asarray(stany)
        if z.shape[0] != s.shape[0]:
            raise ValueError("zwroty i stany muszą mieć tę samą długość")
        unikalne = sorted(set(int(k) for k in np.unique(s)))
        srednie = {k: float(z[s == k].mean()) for k in unikalne}
        kolejnosc = sorted(unikalne, key=lambda k: srednie[k])
        nazwy = {k: "NEUTRAL" for k in unikalne}
        nazwy[kolejnosc[0]] = "BEAR"
        nazwy[kolejnosc[-1]] = "BULL"
        return nazwy

    def liczba_skokow(self, stany) -> int:
        """Ile razy sekwencja zmienia stan (diagnostyka trwałości reżimów)."""
        s = np.asarray(stany)
        return int((s[1:] != s[:-1]).sum())

    # ── rdzeń ────────────────────────────────────────────────────────────────

    def _viterbi(self, xs: np.ndarray, c: np.ndarray) -> np.ndarray:
        """
        Optymalna sekwencja stanów przy danych centroidach (DP po koszcie).
        Deleguje do _viterbi_core (JIT/Numba gdy dostępna, inaczej czysty Python).
        Tablice w C-contiguous float64 — numba lubi przewidywalny layout.
        """
        xs = np.ascontiguousarray(xs, dtype=np.float64)
        c = np.ascontiguousarray(c, dtype=np.float64)
        return _viterbi_core(xs, c, float(self.kara_skoku))

    def _koszt(self, xs, stany, c) -> float:
        emis = float(((xs - c[stany]) ** 2).sum())
        skoki = self.liczba_skokow(stany)
        return emis + self.kara_skoku * skoki
