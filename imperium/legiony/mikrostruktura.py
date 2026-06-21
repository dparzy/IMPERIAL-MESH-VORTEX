"""
🔬 IMV-OHARA | Mikrostruktura informacyjna (O'Hara, BIB-032, INF-44).

W-381: PIN — Probability of Informed Trading (Easley-O'Hara).
       Estymacja metodą momentów (bez scipy — numpy.linalg.solve).
W-382: Engle-Granger kointegracja par — sygnał powrotu do równowagi (stat-arb).

PO CO TO (dla nowicjusza):
  PIN = jaki procent transakcji pochodzi od inwestorów Z INFORMACJĄ (vs szum/płynność).
        Wysoki PIN = rynek "wie coś czego my nie wiemy" → ryzyko adverse selection.
        Komplementarny do VPIN (Z-01): VPIN mierzy IMBALANCE, PIN mierzy PROPORCJĘ informowanych.
  Kointegracja = dwie pary (BTC/ETH) poruszają się razem w długim okresie; gdy spread
        odchyla się od równowagi → sygnał powrotu (mean-reversion na parze, nie na cenie).

ZALEŻNOŚCI: tylko numpy (scipy niedostępne → metoda momentów zamiast MLE).
"""

from __future__ import annotations

import logging
from typing import Dict, Sequence

import numpy as np

logger = logging.getLogger("Mikrostruktura")


# ─── W-381 PIN (Probability of Informed Trading) ─────────────────────────────

def pin_metoda_momentow(buy_volumes: Sequence[float],
                        sell_volumes: Sequence[float]) -> Dict[str, float]:
    """
    🔬 W-381 | PIN metodą momentów (Easley-O'Hara, O'Hara BIB-032 rozdz. 3).

    Model: w każdym okresie (barze) napływ kupna i sprzedaży =
      uninformed (ε, obie strony) + informed (μ, tylko przy zdarzeniu α, kierunek δ).

    PIN = α·μ / (α·μ + 2·ε)   gdzie:
      α = prawdopodobieństwo zdarzenia informacyjnego
      μ = intensywność informed trading (przy zdarzeniu)
      ε = intensywność uninformed trading (zawsze, obie strony)

    Metoda momentów (bez MLE/scipy):
      E[buy]  = α·δ·μ + ε
      E[sell] = α·(1−δ)·μ + ε
      Var efekt: |E[buy] − E[sell]| niesie α·μ·|2δ−1|; nadwyżka nad bazą ε niesie α·μ.

    Uproszczony, odporny estymator:
      ε ≈ min(mean_buy, mean_sell)            (baza dwustronna = szum)
      informed_flow ≈ |mean_buy − mean_sell|  (asymetria = informacja kierunkowa)
      PIN ≈ informed_flow / (informed_flow + 2·ε)

    Zwraca: {pin, epsilon, informed_flow, mean_buy, mean_sell, n}.
    """
    b = np.asarray(buy_volumes, dtype=float)
    s = np.asarray(sell_volumes, dtype=float)
    n = min(len(b), len(s))
    if n < 5:
        return {"pin": float("nan"), "epsilon": float("nan"),
                "informed_flow": float("nan"), "mean_buy": float("nan"),
                "mean_sell": float("nan"), "n": n}

    b, s = b[:n], s[:n]
    mean_buy = float(np.mean(b))
    mean_sell = float(np.mean(s))

    epsilon = min(mean_buy, mean_sell)          # baza dwustronna = uninformed
    informed_flow = abs(mean_buy - mean_sell)   # asymetria = informed (kierunkowy)

    denom = informed_flow + 2.0 * epsilon
    pin = informed_flow / denom if denom > 1e-12 else 0.0

    return {
        "pin": round(float(pin), 4),
        "epsilon": round(epsilon, 4),
        "informed_flow": round(informed_flow, 4),
        "mean_buy": round(mean_buy, 4),
        "mean_sell": round(mean_sell, 4),
        "n": n,
    }


# ─── W-382 Engle-Granger kointegracja ────────────────────────────────────────

def _adf_stat(seria: np.ndarray, max_lag: int = 1) -> float:
    """
    Uproszczony test ADF (Augmented Dickey-Fuller) — statystyka t na współczynniku γ
    w regresji Δy_t = γ·y_{t-1} + Σφ·Δy_{t-i} + ε.
    Bardziej ujemna statystyka → silniejsza stacjonarność (powrót do średniej).
    Pure numpy (bez scipy — sama statystyka t, bez p-value z tablic).
    """
    y = np.asarray(seria, dtype=float)
    dy = np.diff(y)
    n = len(dy)
    if n <= max_lag + 2:
        return 0.0

    # regresory: y_{t-1} + opóźnione różnice
    y_lag = y[:-1][max_lag:]
    dy_dep = dy[max_lag:]
    X_cols = [y_lag]
    for i in range(1, max_lag + 1):
        X_cols.append(dy[max_lag - i:-i] if i < len(dy) else np.zeros_like(y_lag))
    X = np.column_stack([np.ones_like(y_lag)] + X_cols)

    try:
        beta, _, _, _ = np.linalg.lstsq(X, dy_dep, rcond=None)
        resid = dy_dep - X @ beta
        dof = len(dy_dep) - X.shape[1]
        if dof <= 0:
            return 0.0
        sigma2 = float(resid @ resid) / dof
        XtX_inv = np.linalg.pinv(X.T @ X)
        se_gamma = (sigma2 * XtX_inv[1, 1]) ** 0.5  # indeks 1 = y_lag (po stałej)
        gamma = beta[1]
        return float(gamma / se_gamma) if se_gamma > 1e-12 else 0.0
    except np.linalg.LinAlgError:
        return 0.0


def kointegracja_engle_granger(ceny_a: Sequence[float],
                               ceny_b: Sequence[float],
                               prog_adf: float = -3.4) -> Dict[str, object]:
    """
    🔗 W-382 | Engle-Granger kointegracja par (Tsay BIB-031 rozdz. 8).

    Dwustopniowo:
      1) OLS: log(a_t) = α + β·log(b_t) + u_t  → hedge ratio β, spread u_t
      2) ADF na residuach u_t — jeśli stacjonarne → para kointegrowana

    Gdy kointegrowane: z-score bieżącego spreadu = sygnał.
      z < −2 → spread za niski → LONG a / SHORT b (oczekuj powrotu w górę)
      z > +2 → spread za wysoki → SHORT a / LONG b

    Zwraca: {kointegrowane, beta, alfa, spread_z, adf_stat, kierunek, spread_aktualny}.
    """
    a = np.asarray(ceny_a, dtype=float)
    b = np.asarray(ceny_b, dtype=float)
    n = min(len(a), len(b))
    if n < 30:
        return {"kointegrowane": False, "powod": f"za mało danych ({n}<30)",
                "beta": float("nan"), "spread_z": float("nan"),
                "adf_stat": float("nan"), "kierunek": "NEUTRAL"}

    a, b = a[:n], b[:n]
    if np.any(a <= 0) or np.any(b <= 0):
        return {"kointegrowane": False, "powod": "ceny ≤ 0",
                "beta": float("nan"), "spread_z": float("nan"),
                "adf_stat": float("nan"), "kierunek": "NEUTRAL"}

    la, lb = np.log(a), np.log(b)

    # krok 1: OLS la ~ lb
    X = np.column_stack([np.ones_like(lb), lb])
    beta_vec, _, _, _ = np.linalg.lstsq(X, la, rcond=None)
    alfa, beta = float(beta_vec[0]), float(beta_vec[1])
    spread = la - (alfa + beta * lb)

    # krok 2: ADF na spreadzie
    adf = _adf_stat(spread)
    kointegrowane = adf < prog_adf

    mu, sigma = float(np.mean(spread)), float(np.std(spread))
    z = (spread[-1] - mu) / sigma if sigma > 1e-12 else 0.0

    kierunek = "NEUTRAL"
    if kointegrowane:
        if z <= -2.0:
            kierunek = "LONG"   # spread niski → a niedowartościowane vs b
        elif z >= 2.0:
            kierunek = "SHORT"

    return {
        "kointegrowane": kointegrowane,
        "beta": round(beta, 4),
        "alfa": round(alfa, 4),
        "spread_z": round(float(z), 4),
        "spread_aktualny": round(float(spread[-1]), 6),
        "adf_stat": round(adf, 4),
        "kierunek": kierunek,
    }
