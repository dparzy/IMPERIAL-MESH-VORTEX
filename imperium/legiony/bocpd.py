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

    log_w: List[float] = [0.0]  # log(1.0)
    stats: List[_NIGStats] = [prior.copy()]

    # Śledzimy P(zmiana) w ostatnich okno_swiezosci barach
    window_start = n - okno_swiezosci
    best_p = 0.0
    best_kier_sila = 0.0

    for t, x in enumerate(r):
        new_log_w: List[float] = []
        new_stats: List[_NIGStats] = []

        log_preds = [s.predictive_log_prob(x) for s in stats]

        # Growth: każdy run przedłuża się
        for lw, lp, s in zip(log_w, log_preds, stats):
            ns = s.copy()
            ns.update(x)
            new_log_w.append(lw + lp + math.log1p(-hazard))
            new_stats.append(ns)

        # Changepoint: nowy run od 0
        cp_log_w = math.log(hazard) + _logsumexp(
            [lw + lp for lw, lp in zip(log_w, log_preds)]
        )
        new_cp = prior.copy()
        new_cp.update(x)
        # Zapamiętaj referencję do obiektu changepoint — po kompresji identyfikujemy go przez id()
        cp_obj_id = id(new_cp)
        new_log_w.append(cp_log_w)
        new_stats.append(new_cp)

        # Normalizacja
        lse = _logsumexp(new_log_w)
        new_log_w = [lw - lse for lw in new_log_w]

        # Kompresja pamięci
        if len(new_log_w) > max_rl + 1:
            indices = sorted(range(len(new_log_w)), key=lambda i: new_log_w[i], reverse=True)[:max_rl + 1]
            kept_lw = [new_log_w[i] for i in indices]
            lse2 = _logsumexp(kept_lw)
            new_log_w = [lw - lse2 for lw in kept_lw]
            new_stats = [new_stats[i] for i in indices]

        # Rejestruj P(zmiana) dla barów w oknie świeżości
        if t >= window_start:
            # Szukamy changepoint run po id() — nie po n<=1 (n może być małe też u starych runów)
            cp_idx = next((i for i, s in enumerate(new_stats) if id(s) == cp_obj_id), None)
            if cp_idx is not None:
                p_t = math.exp(new_log_w[cp_idx])
                p_t = min(1.0, max(0.0, p_t))
                if p_t > best_p:
                    best_p = p_t
                    # Kierunek: nowy run vs najdłuższy istniejący run (poprzedni reżim)
                    longest_idx = max(range(len(new_stats)), key=lambda i: new_stats[i].n)
                    mean_after = new_stats[cp_idx].mean
                    mean_before = new_stats[longest_idx].mean
                    best_kier_sila = mean_after - mean_before

        log_w = new_log_w
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
