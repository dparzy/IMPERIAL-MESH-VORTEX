"""
📐 IMV-EXP | EXP-03 Hurst Exponent — detektor persystencji szeregu czasowego

DLACZEGO W EXPLORATORES:
  Wykładnik Hursta wymaga obliczenia R/S (Rescaled Range) na serii min. 50 barów.
  H = nachylenie log(R/S) vs log(n) — niemożliwe do sprowadzenia do jednej wartości
  bez historii. Brama może dać ATR, ale nie H.

INTERPRETACJA:
  H > 0.55 → persystencja → trend kontynuuje → działaj z trendem
  H < 0.45 → antypersystencja → mean-reversion → działaj przeciwko trendowi
  H ≈ 0.50 → random walk → brak przewagi → NEUTRAL

RÓŻNICA OD HIGUCHI FD (EXP-01):
  Higuchi FD (1.0–2.0) mierzy "szorstkość" szeregu (wymiar fraktalny).
  Hurst (0.0–1.0) mierzy "pamięć długiego zasięgu" (korelację przyrostów).
  Są powiązane: H ≈ 2 - FD, ale nie identyczne. Używamy obu jako krzyżowego potwierdzenia.

  Razem: EXP-01 mówi CZY jest trend (reżim), EXP-03 mówi JAK SILNA jest pamięć.
"""

import math
import time
from typing import List, Dict, Any

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _hurst_rs(x: List[float], min_n: int = 8, max_lags: int = 6) -> float:
    """
    Oblicza wykładnik Hursta metodą R/S (Rescaled Range Analysis).

    Algorytm (Hurst, 1951):
      1. Podziel szereg na podokna o długości n
      2. Dla każdego okna: oblicz R = max(cumdev) - min(cumdev), S = std(x_w)
      3. E[R/S] ~ c * n^H → log(R/S) = H * log(n) + const
      4. H = nachylenie regresji log(R/S) vs log(n)

    Zwraca H ∈ (0, 1). Fallback = 0.5 przy zbyt małej próbie.
    """
    n_total = len(x)
    if n_total < min_n * 2:
        return 0.5

    log_n_list = []
    log_rs_list = []

    # Lagi: geometryczna sekwencja od min_n do n_total//2
    lag_sizes = []
    lag = min_n
    for _ in range(max_lags):
        if lag > n_total // 2:
            break
        lag_sizes.append(lag)
        lag = max(lag + 1, int(lag * 1.5))

    if len(lag_sizes) < 2:
        return 0.5

    for n in lag_sizes:
        rs_vals = []
        # Przesuń okno po całym szeregu
        for start in range(0, n_total - n + 1, n):
            window = x[start: start + n]
            if len(window) < n:
                continue
            mean_w = sum(window) / n
            cumdev = []
            acc = 0.0
            for v in window:
                acc += v - mean_w
                cumdev.append(acc)
            r = max(cumdev) - min(cumdev)
            # Odchylenie standardowe (population)
            var = sum((v - mean_w) ** 2 for v in window) / n
            s = var ** 0.5
            if s > 0:
                rs_vals.append(r / s)

        if rs_vals:
            rs_avg = sum(rs_vals) / len(rs_vals)
            if rs_avg > 0:
                log_n_list.append(math.log(n))
                log_rs_list.append(math.log(rs_avg))

    if len(log_n_list) < 2:
        return 0.5

    # Regresja liniowa (MNK) — nachylenie = H
    n_pts = len(log_n_list)
    sx = sum(log_n_list)
    sy = sum(log_rs_list)
    sxy = sum(log_n_list[i] * log_rs_list[i] for i in range(n_pts))
    sxx = sum(v ** 2 for v in log_n_list)
    denom = n_pts * sxx - sx ** 2
    if denom == 0:
        return 0.5

    slope = (n_pts * sxy - sx * sy) / denom
    return round(max(0.01, min(0.99, slope)), 4)


class ZwiadowcaHurst(ZwiadowcaElitarny):
    """
    📐 IMV-EXP | EXP-03 Hurst Exponent
    Persystencja szeregu cen — krzyżowe potwierdzenie z EXP-01 (Higuchi FD).
    """
    KLUCZ = "EXP-03"
    WSKAZNIK = "HURST_EXPONENT"
    KATEGORIA = "T"
    WAGA = 8
    WYMAGA_BAROW = 50
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = (
        "Hurst Exponent (R/S Analysis) na serii close. "
        "H>0.55 = persystencja (trend), H<0.45 = antypersystencja (mean-rev). "
        "Wymaga min. 50 barów. Komplementarny z EXP-01 (Higuchi FD)."
    )

    H_TREND = 0.55       # H > H_TREND → persystencja → z trendem
    H_MEANREV = 0.45     # H < H_MEANREV → antypersystencja → przeciw trendowi

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()

        ok, komunikat = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(komunikat)

        close = self._pobierz_close(bary)
        seria = close[-self.WYMAGA_BAROW:]
        h = _hurst_rs(seria)
        czas_ms = (time.time() - t0) * 1000

        nonzero = sum(1 for c in seria if c > 0)
        pewnosc_metody = nonzero / len(seria)

        # Kierunek EMA (analogicznie do EXP-01)
        k = 2.0 / (10)  # EMA period 9
        ema = seria[0]
        for p in seria[1:]:
            ema = p * k + ema * (1 - k)
        kierunek_ema = "LONG" if seria[-1] > ema else "SHORT"

        diagnostics = {
            "main_value": h,
            "hurst": h,
            "n_barow": len(seria),
            "ema_trend": round(ema, 4),
            "rezim": "TREND" if h > self.H_TREND else ("MEAN_REV" if h < self.H_MEANREV else "RANDOM_WALK"),
        }

        if h > self.H_TREND:
            pewnosc = 0.75 + (h - self.H_TREND) * 0.5  # max ~0.975 przy H=1.0
            return self._buduj_raport(
                kierunek=kierunek_ema,
                pewnosc=round(min(0.95, pewnosc), 4),
                powody=[
                    f"H={h:.3f} > {self.H_TREND} → PERSYSTENCJA — trend ma pamięć długiego zasięgu",
                    f"Działaj z trendem: {kierunek_ema}",
                ],
                diagnostics=diagnostics, n_barow=len(seria),
                pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
            )

        if h < self.H_MEANREV:
            # Antypersystencja — działaj przeciwko trendowi (contrarian)
            kierunek_contra = "SHORT" if kierunek_ema == "LONG" else "LONG"
            pewnosc = 0.70 + (self.H_MEANREV - h) * 0.5
            return self._buduj_raport(
                kierunek=kierunek_contra,
                pewnosc=round(min(0.90, pewnosc), 4),
                powody=[
                    f"H={h:.3f} < {self.H_MEANREV} → ANTYPERSYSTENCJA — mean-reversion",
                    f"Działaj PRZECIW trendowi (contrarian): {kierunek_contra}",
                ],
                diagnostics=diagnostics, n_barow=len(seria),
                pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
            )

        return self._buduj_raport(
            kierunek="NEUTRAL",
            pewnosc=0.0,
            powody=[f"H={h:.3f} — random walk ({self.H_MEANREV}–{self.H_TREND}), brak przewagi"],
            diagnostics=diagnostics, n_barow=len(seria),
            pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
        )
