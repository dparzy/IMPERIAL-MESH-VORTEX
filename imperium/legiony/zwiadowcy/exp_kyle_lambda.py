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

    # Próg ADAPTACYJNY (Prawo XV — pomiar 2026-06-21): absolutny próg λ był 50× za
    # wysoki i zależny od skali wolumenu (BTC vs DOGE) → neuron nigdy nie strzelał.
    # Zamiast wartości bezwzględnej: stosunek BIEŻĄCEGO impactu do mediany okna.
    # Skalowalny na KAŻDĄ parę (ratio jest bezwymiarowy).
    # Progi skalibrowane na realny rozkład (pomiar 2026-06-21, 5 par × 3 TF):
    # mediana ratio=2.05, p85=6.2, p95=18 → HIGH≈p85 (~15%), EXTREME≈p93 (~8%).
    # Detektor ryzyka ogonowego (cienki rynek), nie sygnał co-drugi-bar.
    _RATIO_HIGH = 6.0      # bieżący impact > 6× mediana okna → podwyższony (~15%)
    _RATIO_EXTREME = 12.0  # > 12× → ekstremalny, cienki rynek/stop-gun ryzyko (~8%)
    _OGON_BARY = 5         # ile ostatnich barów uśredniamy jako "bieżący impact"

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

        lam = _ols_slope(nf[mask], dp[mask])  # globalna λ okna (diagnostyka)

        # Per-bar impact |Δp|/|netflow| — szereg do progu adaptacyjnego (skalowalny)
        lambda_bars = np.abs(dp[mask]) / (np.abs(nf[mask]) + 1e-10)
        if len(lambda_bars) < self._OGON_BARY + 5:
            return self._brak_danych("Za mało barów do progu adaptacyjnego")

        mediana = float(np.median(lambda_bars))
        biezacy = float(np.mean(lambda_bars[-self._OGON_BARY:]))
        ratio = biezacy / mediana if mediana > 1e-15 else 1.0

        # Korelacja pearson (diagnostyka Prawa XVI vs Amihud)
        amihud_proxy = np.where(volumes[:-1][mask] > 0,
                                np.abs(dp[mask]) / volumes[:-1][mask], 0.0)
        corr_amihud = float(np.corrcoef(amihud_proxy, lambda_bars)[0, 1]) if len(lambda_bars) > 2 else 0.0

        if ratio >= self._RATIO_EXTREME:
            kierunek, pewnosc = "SHORT", 0.75
            powody = [
                f"impact {ratio:.1f}× mediany okna — EKSTREMALNY, cienki rynek/stop-gun ryzyko",
                "Net-flow przesuwa cenę dużo mocniej niż zwykle",
            ]
        elif ratio >= self._RATIO_HIGH:
            kierunek, pewnosc = "SHORT", 0.55
            powody = [
                f"impact {ratio:.1f}× mediany okna — podwyższony, ograniczona głębokość",
            ]
        else:
            kierunek, pewnosc = "NEUTRAL", 0.0
            powody = [f"impact {ratio:.1f}× mediany — normalna głębokość rynku"]

        if abs(corr_amihud) > 0.80:
            powody.append(f"⚠️ Prawo XVI: |ρ(λ,Amihud)|={corr_amihud:.2f}>0.8 → kandydat scalenia z Z-06")

        czas_ms = (time.time() - t0) * 1000
        return self._buduj_raport(
            kierunek=kierunek,
            pewnosc=pewnosc,
            powody=powody,
            diagnostics={
                "main_value": round(ratio, 3),
                "kyle_lambda": round(float(lam), 10),
                "impact_ratio": round(ratio, 3),
                "corr_z06_amihud": round(corr_amihud, 3),
                "n_bars_used": int(mask.sum()),
            },
            n_barow=len(bary),
            pewnosc_metody=float(mask.sum()) / len(bary),
            czas_ms=czas_ms,
        )
