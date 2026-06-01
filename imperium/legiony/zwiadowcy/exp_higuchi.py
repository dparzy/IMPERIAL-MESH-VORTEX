"""
🔬 IMV-EXP | EXP-01 Higuchi Fractal Dimension — detektor reżimu rynkowego

Dlaczego w Exploratores (nie w MikroNeuron):
  Higuchi FD wymaga obliczenia na SERII barów (min. 50), nie jednym barze.
  Algorytm iteruje po k_max×m kombinacjach subserii — niemożliwy do
  sprowadzenia do jednej wartości w Bramie bez utraty sensu.

Oryginał: HFT QUARTET (research, 2024). Nasz wkład:
  - Implementacja pure-Python (bez scipy) z iteracyjnym obliczaniem FD
  - Adaptacyjny próg graniczny: D_TREND/D_MEAN_REV kalibrowany do krypto
  - Integracja z systemem Exploratores (RaportZwiadowcy)

Interpretacja:
  D ≈ 1.0 → rynek trendujący (niski wymiar fraktalny = "gładka" seria)
  D ≈ 2.0 → rynek mean-reverting / chaotyczny (wysoki wymiar = "szorstka" seria)
  D ≈ 1.5 → random walk (H = 0.5 w Hurstcie)

Sygnał dla Legatusa:
  D < 1.35 → TREND_STRONG → LONG/SHORT wg kierunku EMA
  D > 1.65 → RANGING → mean-reversion bias
  1.35–1.65 → NEUTRAL (random walk, brak przewagi)
"""

import math
import time
from typing import List, Dict, Any

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _higuchi_fd(x: List[float], k_max: int = 8) -> float:
    """
    Oblicza wymiar fraktalny Higuchi dla szeregu czasowego x.
    Złożoność: O(k_max × N). Dla N=50, k_max=8 → ~1ms w pure-Python.

    Algorytm:
      1. Dla każdego k (lag) i m (offset) oblicz Lm(k) = długość subserii
      2. L(k) = średnia Lm(k) ważona N/(m×k)
      3. FD = nachylenie regresji log(L(k)) vs log(1/k)
    """
    n = len(x)
    if n < k_max * 2:
        return 1.5  # za mało danych → zwróć random walk

    log_k_list = []
    log_L_list = []

    for k in range(1, k_max + 1):
        Lk = []
        for m in range(1, k + 1):
            # Subseria startująca od m z krokiem k
            indices = list(range(m - 1, n, k))
            if len(indices) < 2:
                continue
            sub = [x[i] for i in indices]
            # Długość ścieżki
            path_len = sum(abs(sub[i] - sub[i - 1]) for i in range(1, len(sub)))
            # Normalizacja Higuchi
            normalizacja = (n - 1) / (((len(indices) - 1) * k) * k)
            Lk.append(path_len * normalizacja)

        if Lk:
            L_avg = sum(Lk) / len(Lk)
            if L_avg > 0:
                log_k_list.append(math.log(1.0 / k))
                log_L_list.append(math.log(L_avg))

    if len(log_k_list) < 2:
        return 1.5

    # Regresja liniowa (MNK) — nachylenie = FD
    n_pts = len(log_k_list)
    sum_x = sum(log_k_list)
    sum_y = sum(log_L_list)
    sum_xy = sum(log_k_list[i] * log_L_list[i] for i in range(n_pts))
    sum_xx = sum(lk ** 2 for lk in log_k_list)
    denom = n_pts * sum_xx - sum_x ** 2
    if denom == 0:
        return 1.5
    slope = (n_pts * sum_xy - sum_x * sum_y) / denom
    return round(abs(slope), 4)


class ZwiadowcaHiguchiFD(ZwiadowcaElitarny):
    """
    🔬 IMV-EXP | EXP-01 Higuchi Fractal Dimension
    Detektor reżimu rynkowego przez wymiar fraktalny szeregu cen zamknięcia.
    """
    KLUCZ = "EXP-01"
    WSKAZNIK = "HIGUCHI_FD"
    KATEGORIA = "T"
    WAGA = 9
    WYMAGA_BAROW = 50
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = ("Higuchi Fractal Dimension na serii close[N]. "
                   "Wymaga min. 50 barów ciągłych — nie redukowalny do jednej wartości w Bramie.")

    # Progi detekcji reżimu (skalibrowane do krypto BTC 1H)
    D_TREND = 1.35       # D < D_TREND → trend
    D_RANGING = 1.65     # D > D_RANGING → ranging/chaotyczny
    K_MAX = 8

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()

        ok, komunikat = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(komunikat)

        close = self._pobierz_close(bary)

        # Oblicz FD na ostatnich WYMAGA_BAROW barach
        seria = close[-self.WYMAGA_BAROW:]
        fd = _higuchi_fd(seria, k_max=self.K_MAX)
        czas_ms = (time.time() - t0) * 1000

        # Jakość danych: % barów z niezerowym close
        nonzero = sum(1 for c in seria if c > 0)
        pewnosc_metody = nonzero / len(seria)

        # Trend EMA (prosty — do kierunku)
        ema_fast = _ema(close[-21:], period=9)
        ema_slow = _ema(close[-21:], period=21)
        kierunek_trendu = "LONG" if ema_fast > ema_slow else "SHORT"

        diagnostics = {
            "main_value": fd,
            "hfd": fd,
            "k_max": self.K_MAX,
            "n_barow": len(seria),
            "ema_fast": round(ema_fast, 4),
            "ema_slow": round(ema_slow, 4),
        }

        if fd < self.D_TREND:
            return self._buduj_raport(
                kierunek=kierunek_trendu,
                pewnosc=0.80 + max(0, (self.D_TREND - fd) / self.D_TREND) * 0.15,
                powody=[f"HFD={fd:.3f} < {self.D_TREND} → TREND {'SILNY' if fd < 1.25 else ''}",
                        f"Kierunek EMA9/21: {kierunek_trendu}"],
                diagnostics=diagnostics,
                n_barow=len(seria),
                pewnosc_metody=pewnosc_metody,
                czas_ms=czas_ms,
            )

        if fd > self.D_RANGING:
            return self._buduj_raport(
                kierunek="NEUTRAL",
                pewnosc=0.0,
                powody=[f"HFD={fd:.3f} > {self.D_RANGING} → RANGING/CHAOS — brak sygnału"],
                diagnostics=diagnostics,
                n_barow=len(seria),
                pewnosc_metody=pewnosc_metody,
                czas_ms=czas_ms,
                ostrzezenia=["Rynek chaotyczny — Exploratores nie sygnalizuje"],
            )

        # Strefa przejściowa (random walk)
        return self._buduj_raport(
            kierunek="NEUTRAL",
            pewnosc=0.0,
            powody=[f"HFD={fd:.3f} — random walk ({self.D_TREND}–{self.D_RANGING}), brak przewagi"],
            diagnostics=diagnostics,
            n_barow=len(seria),
            pewnosc_metody=pewnosc_metody,
            czas_ms=czas_ms,
        )


def _ema(prices: List[float], period: int) -> float:
    """EMA pure-Python — tylko do wewnętrznego użytku Exploratores."""
    if not prices or period <= 0:
        return 0.0
    k = 2.0 / (period + 1)
    ema = prices[0]
    for p in prices[1:]:
        ema = p * k + ema * (1 - k)
    return ema
