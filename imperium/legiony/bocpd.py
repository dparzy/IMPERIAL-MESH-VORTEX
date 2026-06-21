"""
W-338 | BOCPD — Bayesian Online Change-Point Detection.

DLA NOWICJUSZA: CUSUM (CP-01) mówi „WŁAŚNIE nastąpił przełom" — binarnie.
BOCPD (Adams & MacKay 2007) mówi coś innego: w każdym barze t daje PRAWDOPODOBIEŃSTWO
„jak długo trwa obecny reżim?" (run-length). Gdy to prawdopodobieństwo spada gwałtownie
→ zmiana reżimu. To miarę ciągłą, nie binarną — różna informacja.

Algorytm (Adams & MacKay 2007, Bayesian Online Changepoint Detection):
  1. Utrzymuje rozkład nad długościami biegu (run-length = ile barów w bieżącym reżimie).
  2. Dla każdego nowego bara aktualizuje rozkład Bayesowsko przez:
     (a) P(hazard): prawdopodobieństwo a priori, że reżim się zmienia w tym barze.
         Używamy hazardu geometrycznego: P(zmiana) = 1/λ, gdzie λ = oczekiwana długość reżimu.
     (b) Predictive likelihood: jak prawdopodobne są nowe dane przy zaktualizowanym rozkładzie
         parametrów reżimu (normalność Gaussian — mean + variance update).
  3. P(zmiana) = max_over_t P(run-length == 0 | dane do t) — margines przełomu.

Brak lookahead (Prawo I): w barze t używa wyłącznie zwrotów do bara t.
Ortogonalny do CP-01 (CUSUM): CUSUM = progowy detektor przełomów; BOCPD = Bayesowskie
prawdopodobieństwo przełomu per-bar. Różna matematyka, różna kalibracja (Prawo XVI).

Uproszczenia dla online/real-time:
  - Hazard stały (geometric prior, 1/lambda).
  - Obcinamy run-length posterior do MAX_RL elementów (kompresja pamięci).
  - Dane modelujemy Normal(μ, σ²) z conjugate prior Normal-InverseGamma.

Źródło: Adams & MacKay (2007), „Bayesian Online Changepoint Detection",
  https://arxiv.org/abs/0710.3742 (⚠️ arXiv ID potwierdzony, pełny tekst niezweryfikowany)
"""

import math
from typing import List, Optional, Tuple

import numpy as np


# ─── Normal-InverseGamma sufficient statistics (conjugate prior) ──────────────

class _NIGStats:
    """
    Sufficient statistics dla Normal-InverseGamma (conjugate do Normal).
    Parametry: μ₀ (mean prior), κ₀ (strength), α₀, β₀ (IG shape/scale).
    Aktualizacja: O(1) per bar (wystarczające statystyki).
    """
    __slots__ = ("mu0", "kappa0", "alpha0", "beta0", "n", "mean", "m2")

    def __init__(self, mu0: float = 0.0, kappa0: float = 1.0,
                 alpha0: float = 1.0, beta0: float = 0.01):
        self.mu0 = mu0
        self.kappa0 = kappa0
        self.alpha0 = alpha0
        self.beta0 = beta0
        self.n = 0
        self.mean = mu0
        self.m2 = 0.0  # suma kwadratów odchyleń (Welford)

    def copy(self) -> "_NIGStats":
        s = _NIGStats(self.mu0, self.kappa0, self.alpha0, self.beta0)
        s.n = self.n
        s.mean = self.mean
        s.m2 = self.m2
        return s

    def update(self, x: float) -> None:
        """Welford online update."""
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.m2 += delta * delta2

    @property
    def kappa_n(self) -> float:
        return self.kappa0 + self.n

    @property
    def alpha_n(self) -> float:
        return self.alpha0 + self.n / 2.0

    @property
    def beta_n(self) -> float:
        """Posterior β: β₀ + ½ m2 + (κ₀ n (x̄ - μ₀)²) / (2(κ₀ + n))"""
        kn = self.kappa0 + self.n
        prior_term = (self.kappa0 * self.n * (self.mean - self.mu0) ** 2) / (2.0 * kn) if kn > 0 else 0.0
        return self.beta0 + 0.5 * self.m2 + prior_term

    def predictive_log_prob(self, x: float) -> float:
        """
        Log P(x | dane) pod Student-t z parametrami posterior.
        Marginalizing out (μ, σ²) daje Student-t.
        """
        kn = self.kappa_n
        an = self.alpha_n
        bn = self.beta_n
        # Posterior predictive: Student-t(2α_n, μ_n, β_n(κ_n+1)/(α_n κ_n))
        mu_n = (self.kappa0 * self.mu0 + self.n * self.mean) / kn if kn > 0 else self.mu0
        dof = 2.0 * an
        scale2 = bn * (kn + 1.0) / (an * kn) if (an > 0 and kn > 0) else 1.0
        scale = math.sqrt(scale2) if scale2 > 1e-30 else 1e-15

        # Log Student-t density
        t = (x - mu_n) / scale
        log_p = (
            math.lgamma((dof + 1.0) / 2.0)
            - math.lgamma(dof / 2.0)
            - 0.5 * math.log(dof * math.pi)
            - math.log(scale)
            - ((dof + 1.0) / 2.0) * math.log(1.0 + t * t / dof)
        )
        return log_p


def _pred_log_prob_batch(stats: "List[_NIGStats]", x: float) -> np.ndarray:
    """
    Wektoryzowany odpowiednik [s.predictive_log_prob(x) for s in stats].
    Zastępuje ~30 wywołań Python math.lgamma na 3 wywołania scipy.special.gammaln.
    """
    from scipy.special import gammaln
    k0, a0, b0, mu0 = 1.0, 1.0, 0.01, 0.0
    ns = np.array([s.n for s in stats], dtype=np.float64)
    means = np.array([s.mean for s in stats], dtype=np.float64)
    m2s = np.array([s.m2 for s in stats], dtype=np.float64)

    kn = k0 + ns
    an = a0 + ns / 2.0
    prior_term = np.where(kn > 0,
                          k0 * ns * (means - mu0) ** 2 / (2.0 * kn),
                          0.0)
    bn = b0 + 0.5 * m2s + prior_term
    mu_n = np.where(kn > 0, (k0 * mu0 + ns * means) / kn, mu0)
    dof = 2.0 * an
    scale2 = np.where((an > 0) & (kn > 0),
                      bn * (kn + 1.0) / (an * kn),
                      1.0)
    scale = np.sqrt(np.maximum(scale2, 1e-30))
    t = (x - mu_n) / np.maximum(scale, 1e-15)
    log_p = (
        gammaln((dof + 1.0) / 2.0)
        - gammaln(dof / 2.0)
        - 0.5 * np.log(np.maximum(dof * np.pi, 1e-30))
        - np.log(np.maximum(scale, 1e-15))
        - ((dof + 1.0) / 2.0) * np.log1p(np.maximum(t ** 2 / np.maximum(dof, 1e-15), 0.0))
    )
    return log_p


def _zwroty(close: List[float]) -> List[float]:
    """Zwroty procentowe bar-do-bara."""
    out = []
    for i in range(1, len(close)):
        p = close[i - 1]
        out.append((close[i] - p) / p if p > 0 else 0.0)
    return out


# ─── BOCPD run-length filter ──────────────────────────────────────────────────

def bocpd_changepoint_prob(
    close: List[float],
    hazard_lambda: float = 30.0,
    max_rl: int = 100,
    min_barow: int = 10,
    okno_swiezosci: int = 5,
) -> Tuple[Optional[float], float]:
    """
    Bayesian Online Change-Point Detection na serii zamknięć.

    close:            seria zamknięć (najnowsze na końcu).
    hazard_lambda:    oczekiwana długość reżimu w barach (geometric prior).
                      30 = spodziewamy się zmiany co ~30 barów.
    max_rl:           maks. utrzymywana długość run-length (kompresja).
    min_barow:        minimum danych przed pierwszym wynikiem.
    okno_swiezosci:   ile ostatnich barów uznajemy za „świeżą" zmianę.
                      Zwracamy MAX p_change z okna — jak w CP-01 (świeżość przełomu).

    Zwraca (p_change_max, kierunek_sila):
      p_change_max ∈ [0,1]: MAX P(zmiana) w ostatnich `okno_swiezosci` barach.
      kierunek_sila: siła kierunkowa przy barze o max P(zmiana) (> 0 → bycza, < 0 → niedźwiedzia).
      (None, 0.0): za mało danych.
    """
    if len(close) < min_barow + 1:
        return None, 0.0

    r = _zwroty(close)
    n = len(r)
    if n < min_barow:
        return None, 0.0

    hazard = 1.0 / max(1.0, hazard_lambda)
    prior = _NIGStats()

    log_w_arr = np.zeros(1)  # log(1.0)
    stats: List[_NIGStats] = [prior.copy()]

    # Śledzimy P(zmiana) w ostatnich okno_swiezosci barach
    window_start = n - okno_swiezosci
    best_p = 0.0
    best_kier_sila = 0.0
    log1p_survival = math.log1p(-hazard)
    log_hazard = math.log(hazard)

    for t, x in enumerate(r):
        # Wektoryzowana predykcja (zastępuje 531K Python math.lgamma calls)
        log_preds = _pred_log_prob_batch(stats, x)   # np.ndarray

        # Growth: wszystkie runy się przedłużają (wektoryzowane log_w)
        new_log_w_arr = log_w_arr + log_preds + log1p_survival
        new_stats: List[_NIGStats] = []
        for s in stats:
            ns = s.copy()
            ns.update(x)
            new_stats.append(ns)

        # Changepoint: nowy run od 0 (logsumexp przez numpy)
        lse_cp = float(np.max(log_w_arr + log_preds))
        lse_cp = lse_cp + math.log(float(np.sum(np.exp(log_w_arr + log_preds - lse_cp))))
        cp_log_w = log_hazard + lse_cp
        new_cp = prior.copy()
        new_cp.update(x)
        cp_obj_id = id(new_cp)
        new_log_w_arr = np.append(new_log_w_arr, cp_log_w)
        new_stats.append(new_cp)

        # Normalizacja (numpy)
        lse = float(np.max(new_log_w_arr))
        new_log_w_arr = new_log_w_arr - lse - math.log(float(np.sum(np.exp(new_log_w_arr - lse))))

        # Kompresja pamięci
        if len(new_log_w_arr) > max_rl + 1:
            indices = np.argpartition(new_log_w_arr, -(max_rl + 1))[-(max_rl + 1):]
            new_log_w_arr = new_log_w_arr[indices]
            new_stats = [new_stats[i] for i in indices]
            lse2 = float(np.max(new_log_w_arr))
            new_log_w_arr = new_log_w_arr - lse2 - math.log(float(np.sum(np.exp(new_log_w_arr - lse2))))

        # Rejestruj P(zmiana) dla barów w oknie świeżości
        if t >= window_start:
            cp_idx = next((i for i, s in enumerate(new_stats) if id(s) == cp_obj_id), None)
            if cp_idx is not None:
                p_t = float(np.exp(new_log_w_arr[cp_idx]))
                p_t = min(1.0, max(0.0, p_t))
                if p_t > best_p:
                    best_p = p_t
                    longest_idx = max(range(len(new_stats)), key=lambda i: new_stats[i].n)
                    mean_after = new_stats[cp_idx].mean
                    mean_before = new_stats[longest_idx].mean
                    best_kier_sila = mean_after - mean_before

        log_w_arr = new_log_w_arr
        stats = new_stats

    return best_p, best_kier_sila


def _logsumexp(log_vals: List[float]) -> float:
    """Numerycznie stabilny log-sum-exp."""
    if not log_vals:
        return -math.inf
    mx = max(log_vals)
    if mx == -math.inf:
        return -math.inf
    return mx + math.log(sum(math.exp(v - mx) for v in log_vals))
