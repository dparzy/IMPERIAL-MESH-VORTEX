"""
W-339 | Fractional Differentiation — stacjonaryzacja z zachowaną pamięcią długiego zasięgu.

DLA NOWICJUSZA: standardowe zwroty (first difference) niszczą całą pamięć historyczną.
Logarytm ceny jest niestacjonarny (random walk) — modele ML na nim halucinują.
Fractional differentiation (López de Prado, AFML Ch5) to kompromis:
  d=1 → pełna stacjonarność, zero pamięci (zwykłe zwroty)
  d=0 → brak stacjonarności, pełna pamięć (raw log-price)
  d∈(0,1) → częściowa stacjonarność + zachowana pamięć długiego zasięgu

Cel: znaleźć minimalne d takie, że seria jest stacjonarna (ADF p < 0.05).
Wynik: FRAC_DIFF_D (optymalne d) + ostatnia wartość znormalizowanej serii.

Matematyka:
  Operator frac-diff stopnia d: (1-L)^d = Σ_{k=0}^∞ w_k L^k
  gdzie L = operator opóźnienia, wagi: w_0=1, w_k = w_{k-1} × (k-d)/k
  Obcinamy gdy |w_k| < eps (threshold cutoff, domyślnie 1e-4).

Brak lookahead (Prawo I): w barze t używa wyłącznie historii do t.
Brak scipy/statsmodels: ADF (Augmented Dickey-Fuller) zaimplementowany ręcznie — OLS.

Źródło: López de Prado, Advances in Financial ML, Chapter 5 (Fractional Differentiation).
  https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086
  (⚠️ pełny tekst niezweryfikowany — opis rozdziału potwierdzony)
"""

import math
from typing import List, Optional, Tuple


# ─── Fractional differentiation weights ──────────────────────────────────────

def _frac_diff_weights(d: float, eps: float = 1e-4, max_w: int = 200) -> List[float]:
    """
    Wagi operatora frac-diff stopnia d (z obcinaniem przy |w_k| < eps).
    Zwraca listę [w_0, w_1, ..., w_K] gdzie w_0=1.
    """
    w = [1.0]
    k = 1
    while k < max_w:
        wk = -w[-1] * (d - k + 1) / k
        if abs(wk) < eps:
            break
        w.append(wk)
        k += 1
    return w


def frac_diff_series(
    log_prices: List[float],
    d: float,
    eps: float = 1e-4,
) -> List[float]:
    """
    Zastosuj frac-diff stopnia d na serii log-cen.
    Zwraca serię (krótsza o len(weights)-1 z przodu — warmup).
    Brak lookahead: bar t używa wyłącznie hist do t.
    """
    w = _frac_diff_weights(d, eps)
    W = len(w)
    n = len(log_prices)
    if n < W:
        return []
    out = []
    for t in range(W - 1, n):
        val = sum(w[k] * log_prices[t - k] for k in range(W))
        out.append(val)
    return out


# ─── Minimalne d (ADF uproszczony) ───────────────────────────────────────────

def _adf_stat(x: List[float]) -> Optional[float]:
    """
    Uproszczony ADF (Augmented Dickey-Fuller) — tylko t-stat na Δx vs x_{t-1}.
    Model: Δx_t = α + β x_{t-1} + ε_t (bez dodatkowych lagów — ADF(0)).
    H0: β=0 (unit root). Małe β < 0 → stacjonarność.
    Zwraca t-stat β lub None jeśli brak danych.

    Uproszczenie vs pełny ADF: brak p-value, brak tabel krytycznych — używamy
    tylko znaku i wielkości t-stat jako heurystyki (t < -2.9 ≈ p<0.05).
    """
    n = len(x)
    if n < 6:
        return None

    # Δx_t, x_{t-1}
    dx = [x[t] - x[t - 1] for t in range(1, n)]
    xlag = x[:n - 1]
    m = len(dx)

    # OLS: [intercept, xlag] → dx
    mean_dl = sum(dx) / m
    mean_xl = sum(xlag) / m
    cov_xy = sum((dx[i] - mean_dl) * (xlag[i] - mean_xl) for i in range(m))
    var_x = sum((xlag[i] - mean_xl) ** 2 for i in range(m))
    if var_x < 1e-18:
        return None

    beta = cov_xy / var_x
    alpha = mean_dl - beta * mean_xl

    # Residuals + SE(beta)
    resid = [dx[i] - alpha - beta * xlag[i] for i in range(m)]
    sse = sum(r * r for r in resid)
    sigma2 = sse / max(1, m - 2)
    se_beta = math.sqrt(sigma2 / var_x) if sigma2 > 0 else 1e-9

    return beta / se_beta


def _find_min_d(
    log_prices: List[float],
    d_step: float = 0.1,
    adf_threshold: float = -2.9,
    eps: float = 1e-4,
) -> float:
    """
    Znajdź minimalne d ∈ [0, 1] takie, że frac_diff_series jest (quasi-)stacjonarna.
    Krok d_step = 0.1 (szybkie przybliżenie; dokładniejsze wymaga grid search 0.01 — wolne).
    Zwraca minimalne d lub 1.0 jeśli brak stacjonarności.
    """
    for d_int in range(1, 11):
        d = round(d_int * d_step, 2)
        serie = frac_diff_series(log_prices, d, eps)
        if not serie:
            continue
        t_stat = _adf_stat(serie)
        if t_stat is not None and t_stat < adf_threshold:
            return d
    return 1.0  # fallback: pełna różnica


# ─── Główna funkcja ───────────────────────────────────────────────────────────

def frac_diff_signal(
    close: List[float],
    eps: float = 1e-4,
    min_barow: int = 30,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Oblicza (d_opt, ostatnia_wartość_znormalizowanej_serii).

    close:      seria zamknięć (najnowsze na końcu).
    eps:        próg obcinania wag.
    min_barow:  minimum danych.

    Zwraca:
      (d_opt, z_last):
        d_opt ∈ [0.1, 1.0] — minimalne d zapewniające quasi-stacjonarność.
        z_last — znormalizowana ostatnia wartość frac-diff serii (z-score na oknie).
      (None, None) jeśli za mało danych.
    """
    n = len(close)
    if n < min_barow:
        return None, None

    log_p = [math.log(max(c, 1e-10)) for c in close]
    d_opt = _find_min_d(log_p)
    serie = frac_diff_series(log_p, d_opt, eps)
    if not serie:
        return d_opt, None

    # Z-score ostatniej wartości na całej serii (normalizacja)
    mu = sum(serie) / len(serie)
    std = math.sqrt(sum((v - mu) ** 2 for v in serie) / len(serie))
    z_last = (serie[-1] - mu) / std if std > 1e-12 else 0.0

    return d_opt, z_last
