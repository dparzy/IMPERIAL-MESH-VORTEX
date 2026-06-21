"""
W-380: Kyle's Lambda — price impact per unit net order flow (O'Hara BIB-032, rozdz. 4).

λ = OLS nachylenie regresji: Δp_t = c + λ · netflow_t + ε_t
netflow_t = V_buy_t - V_sell_t (per bar, z aggTrades lub side-signed volume)

Interpretacja:
- Wysokie λ → duży price impact małych zleceń → cienki rynek (krucha płynność)
- Niskie λ → głęboki rynek, zlecenia nie ruszają ceny

Różnica vs Z-06 Amihud: Amihud = |Δp|/V (absolutna, bez znaku),
Kyle's λ = OLS Δp/netflow (kierunkowa, OLS — mierzy asymetrię, nie tylko skalę).
Test Prawa XVI: jeśli |ρ(λ, Amihud)| > 0.80 → redundancja → waga do dołu.
"""

from __future__ import annotations

import time
import logging
from typing import List, Dict, Any

import numpy as np

from imperium.legiony.zwiadowcy.baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych

logger = logging.getLogger("Exploratores")


def _ols_slope(x: np.ndarray, y: np.ndarray) -> float:
    """OLS nachylenie y ~ x (bez intercept korekty, Welford-stable)."""
    n = len(x)
    if n < 2:
        return float("nan")
    xm, ym = np.mean(x), np.mean(y)
    cov = float(np.mean((x - xm) * (y - ym)))
    var_x = float(np.mean((x - xm) ** 2))
    return cov / var_x if var_x > 1e-12 else float("nan")


class ZwiadowcaKyleLambda(ZwiadowcaElitarny):
    """
    EXP-14 | Kyle's Lambda — price impact per unit net order flow (W-380).

    Potrzebuje barów z polem 'buy_volume' lub 'net_flow' (side-signed aggTrades).
    Jeśli brak → fallback: szacuje buy_vol ≈ (close-low)/(high-low) * volume (tick rule proxy).

    HIGH_LAMBDA → cienki rynek (krucha płynność) → SHORT bias (stop-gun ryzyko).
    LOW_LAMBDA → głęboki rynek → mniejsze ryzyko manipulacji.
    """

    KLUCZ = "EXP-14"
    LEGION = "EXPLORATORES"
    WSKAZNIK = "KYLE_LAMBDA"
    KATEGORIA = "L"
    WAGA = 6
    WYMAGA_BAROW = 30
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = (
        "Kyle's Lambda: OLS regresja Δp ~ netflow. "
        "λ = nachylenie = price impact per unit. BIB-032 O'Hara rozdz. 4."
    )
    ELITARNY = True
    POWOD_ELITARNOSCI = "E1: Exploratores — Kyle's Lambda OLS w pure numpy (BIB-032 O'Hara)"

    _PROG_HIGH = 1.5e-5    # λ > 1.5e-5 → wysoki impact (cienki rynek)
    _PROG_EXTREME = 5e-5   # λ > 5e-5  → ekstremalny impact

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()
        ok, msg = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(msg)

        closes = np.array(self._pobierz_close(bary), dtype=float)
        highs = np.array(self._pobierz_high(bary), dtype=float)
        lows = np.array(self._pobierz_low(bary), dtype=float)
        volumes = np.array(self._pobierz_volume(bary), dtype=float)

        # Szacuj buy_volume przez tick rule proxy (BTP = (close-low)/(high-low))
        ranges = highs - lows
        with np.errstate(divide="ignore", invalid="ignore"):
            btp = np.where(ranges > 1e-10, (closes - lows) / ranges, 0.5)
        buy_vol = btp * volumes
        sell_vol = volumes - buy_vol
        netflow = buy_vol - sell_vol  # >0 = net buying pressure

        # Δp per bar (log return)
        dp = np.diff(np.log(np.maximum(closes, 1e-10)))
        nf = netflow[:-1]  # wyrównanie długości

        # Filtruj zera (bary bez ruchu)
        mask = volumes[:-1] > 0
        if mask.sum() < 10:
            return self._brak_danych("Za mało barów z wolumenem > 0")

        lam = _ols_slope(nf[mask], dp[mask])

        if np.isnan(lam):
            return self._brak_danych("OLS nie powiodło się (zerowa wariancja netflow)")

        lam_abs = abs(lam)
        # Korelacja pearson (diagnostyka Prawa XVI vs Amihud)
        amihud_proxy = np.where(volumes[:-1][mask] > 0,
                                np.abs(dp[mask]) / volumes[:-1][mask], 0.0)
        lambda_bars = np.abs(dp[mask]) / (np.abs(nf[mask]) + 1e-10)
        corr_amihud = float(np.corrcoef(amihud_proxy, lambda_bars)[0, 1]) if len(lambda_bars) > 2 else 0.0

        if lam_abs >= self._PROG_EXTREME:
            kierunek, pewnosc = "SHORT", 0.75
            powody = [
                f"λ={lam:.2e} EKSTREMALNY — cienki rynek, stop-gun ryzyko",
                "Nawet mały net-flow przesuwa cenę znacząco",
            ]
        elif lam_abs >= self._PROG_HIGH:
            kierunek, pewnosc = "SHORT", 0.55
            powody = [
                f"λ={lam:.2e} wysoki — ograniczona głębokość rynku, ostrożność",
            ]
        else:
            kierunek, pewnosc = "NEUTRAL", 0.0
            powody = [f"λ={lam:.2e} normalny — wystarczająca głębokość rynku"]

        if abs(corr_amihud) > 0.80:
            powody.append(f"⚠️ Prawo XVI: |ρ(λ,Amihud)|={corr_amihud:.2f}>0.8 → kandydat scalenia z Z-06")

        czas_ms = (time.time() - t0) * 1000
        return self._buduj_raport(
            kierunek=kierunek,
            pewnosc=pewnosc,
            powody=powody,
            diagnostics={
                "main_value": round(float(lam), 8),
                "kyle_lambda": round(float(lam), 8),
                "corr_z06_amihud": round(corr_amihud, 3),
                "n_bars_used": int(mask.sum()),
            },
            n_barow=len(bary),
            pewnosc_metody=float(mask.sum()) / len(bary),
            czas_ms=czas_ms,
        )
