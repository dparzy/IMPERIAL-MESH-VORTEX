"""
W-376: GARCH(1,1) + GJR-GARCH — zmienność warunkowa (Tsay, BIB-031, rozdz. 3).

GARCH(1,1) — Bollerslev (1986):
  σ²_t = α₀ + α₁·a²_{t-1} + β₁·σ²_{t-1}

GJR-GARCH — Glosten-Jagannathan-Runkle (1993):
  σ²_t = α₀ + (α₁ + γ·𝟙[a_{t-1}<0])·a²_{t-1} + β₁·σ²_{t-1}

Estymacja: grid search 3D/4D z log-likelihood Gaussa (pure numpy, bez scipy).
"""

from __future__ import annotations

import time
import logging
from typing import List, Dict, Any

import numpy as np

from imperium.legiony.zwiadowcy.baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych

logger = logging.getLogger("Exploratores")


# ---------------------------------------------------------------------------
# GARCH engine
# ---------------------------------------------------------------------------

def _rekurencja_gjr(a: np.ndarray, a0: float, a1: float, b1: float, gamma: float) -> np.ndarray:
    """
    GJR-GARCH variance recursion. Scipy lfilter dla sekwencji IIR:
      sigma2[t] = innovation[t-1] + b1 * sigma2[t-1]
    Innowacje wektoryzowane numpy; recursja przez scipy (C), nie Python loop.
    """
    from scipy.signal import lfilter
    T = len(a)
    sigma2_0 = max(float(np.var(a)), 1e-10)
    if T <= 1:
        return np.full(T, sigma2_0)
    # Innowacje (wektoryzowane — bez Python loop)
    ind = (a[:-1] < 0).view(np.uint8).astype(np.float64)
    innovation = a0 + (a1 + gamma * ind) * (a[:-1] ** 2)
    # IIR: sigma2[t] = innovation[t-1] + b1*sigma2[t-1] = lfilter([1],[1,-b1], innovation, zi)
    # zi = [b1 * sigma2_0] — warunek początkowy
    sigma2_rest, _ = lfilter([1.0], [1.0, -b1], innovation, zi=np.array([b1 * sigma2_0]))
    sigma2 = np.empty(T)
    sigma2[0] = sigma2_0
    sigma2[1:] = np.maximum(sigma2_rest, 1e-10)
    return sigma2


def _log_likelihood(sigma2: np.ndarray, a: np.ndarray) -> float:
    return float(-0.5 * np.sum(np.log(sigma2) + a ** 2 / sigma2))


def _fit_gjr_garch(returns: np.ndarray) -> Dict[str, Any]:
    a = returns - float(np.mean(returns))
    var_a = float(np.var(a)) or 1e-6

    best_ll = -1e12
    best = (var_a * 0.02, 0.10, 0.85, 0.10)

    for a0_f in (0.01, 0.05, 0.10):
        for a1 in (0.05, 0.10, 0.15):
            for b1 in (0.80, 0.85, 0.90):
                if a1 + b1 >= 1.0:
                    continue
                for gamma in (0.0, 0.05, 0.10, 0.20):
                    a0 = a0_f * var_a
                    s2 = _rekurencja_gjr(a, a0, a1, b1, gamma)
                    ll = _log_likelihood(s2, a)
                    if ll > best_ll:
                        best_ll = ll
                        best = (a0, a1, b1, gamma)

    a0, a1, b1, gamma = best
    sigma2 = _rekurencja_gjr(a, a0, a1, b1, gamma)

    ind_last = 1.0 if a[-1] < 0 else 0.0
    sigma2_next = max(a0 + (a1 + gamma * ind_last) * a[-1] ** 2 + b1 * sigma2[-1], 1e-10)

    return {
        "sigma_next": float(sigma2_next ** 0.5),
        "sigma_current": float(sigma2[-1] ** 0.5),
        "persistence": a1 + b1,
        "leverage_ratio": gamma / a1 if a1 > 1e-8 else 0.0,
        "params": {"a0": a0, "a1": a1, "b1": b1, "gamma": gamma},
        "log_likelihood": best_ll,
    }


# ---------------------------------------------------------------------------
# Zwiadowca EXP-13
# ---------------------------------------------------------------------------

class ZwiadowcaGARCH(ZwiadowcaElitarny):
    """
    EXP-13 | GJR-GARCH(1,1) — warunkowa zmienność (W-376, Tsay BIB-031).

    HIGH_VOL / rosnąca → SHORT bias (ryzyko odwrócenia).
    LOW_VOL / spokojna → bias bullish (kontynuacja).
    γ > α₁ → efekt dźwigni (leverage): rynek boi się spadków bardziej niż wzrostów.
    """

    KLUCZ = "EXP-13"
    LEGION = "EXPLORATORES"
    WSKAZNIK = "GARCH_SIGMA"
    KATEGORIA = "V"
    WAGA = 7
    WYMAGA_BAROW = 60
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = (
        "GJR-GARCH(1,1): σ²_t = α₀ + (α₁+γ·I[a<0])·a²_{t-1} + β₁·σ²_{t-1}. "
        "Grid search log-likelihood (pure numpy). BIB-031 Tsay rozdz. 3."
    )
    ELITARNY = True
    POWOD_ELITARNOSCI = "E1: Exploratores — GJR-GARCH w pure numpy bez scipy (BIB-031 Tsay)"

    PROG_HIGH = 0.025    # σ per-bar > 2.5% → wysoka zmienność
    PROG_EXTREME = 0.05  # σ per-bar > 5.0% → ekstremalna

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()
        ok, msg = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(msg)

        closes = np.array(self._pobierz_close(bary), dtype=float)
        returns = np.diff(np.log(np.maximum(closes, 1e-10)))

        # GRANICA: brak wariancji w danych → za mało informacji do wnioskowania
        if float(np.var(returns)) < 1e-12:
            return self._brak_danych("Zerowa wariancja zwrotów — brak informacji o zmienności")

        try:
            wynik = _fit_gjr_garch(returns)
        except Exception as e:
            logger.warning(f"[EXP-13] GJR-GARCH error: {e}")
            return self._brak_danych(f"GARCH error: {e}")

        sigma = wynik["sigma_next"]
        sigma_curr = wynik["sigma_current"]
        persistence = wynik["persistence"]
        lev = wynik["leverage_ratio"]
        vol_rising = sigma > sigma_curr * 1.05

        if sigma >= self.PROG_EXTREME:
            kierunek, pewnosc = "SHORT", 0.85
            powody = [
                f"σ_GARCH={sigma:.4f} EKSTREMALNA (>{self.PROG_EXTREME:.1%}/bar) — bias SHORT",
                f"persistence={persistence:.3f}",
            ]
        elif sigma >= self.PROG_HIGH and vol_rising:
            kierunek, pewnosc = "SHORT", 0.60
            powody = [
                f"σ_GARCH={sigma:.4f} wysoka i rosnąca — ostrożność",
                f"leverage_ratio={lev:.2f}" + (" (dźwignia: spadki straszą)" if lev > 1 else ""),
            ]
        elif sigma < self.PROG_HIGH * 0.5:
            kierunek, pewnosc = "LONG", 0.50
            powody = [f"σ_GARCH={sigma:.4f} NISKA — spokojne warunki, trend może trwać"]
        else:
            kierunek, pewnosc = "NEUTRAL", 0.0
            powody = [f"σ_GARCH={sigma:.4f} — normalna zmienność"]

        czas_ms = (time.time() - t0) * 1000
        return self._buduj_raport(
            kierunek=kierunek,
            pewnosc=pewnosc,
            powody=powody,
            diagnostics={
                "main_value": round(sigma, 6),
                "sigma_next": round(sigma, 6),
                "sigma_current": round(sigma_curr, 6),
                "persistence": round(persistence, 4),
                "leverage_ratio": round(lev, 3),
                "a0": round(wynik["params"]["a0"], 8),
                "a1": round(wynik["params"]["a1"], 4),
                "b1": round(wynik["params"]["b1"], 4),
                "gamma": round(wynik["params"]["gamma"], 4),
            },
            n_barow=len(bary),
            pewnosc_metody=1.0,
            czas_ms=czas_ms,
        )
