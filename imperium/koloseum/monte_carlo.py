"""
🎲 MONTE CARLO ROBUSTNESS — walidacja odporności przewagi (W-293).

Inspiracja: Jesse framework (jesse.trade/roadmap — Monte Carlo stress test 2025).

Dwa niezależne testy potwierdzające, że edge jest PRAWDZIWY, a nie przypadkowy:

1. SHUFFLE TRANSAKCJI: tasuje kolejność historycznych trade'ów N razy → rozkład
   krzywych equity → przedziały ufności Sharpe/MaxDD.
   DLA NOWICJUSZA: jeśli zysk zależy od KOLEJNOŚCI transakcji (a nie od ich
   indywidualnej wartości), to edge jest przypadkowy. Prawdziwy edge tasowanie
   przeżyje: rozkład wyników pozostaje solidny niezależnie od kolejności.

2. BOOTSTRAP (próbkowanie ze zwrotem): losuje N transakcji z historii N razy
   (z powtórzeniami) → symuluje alternatywne "scenariusze przyszłości".
   DLA NOWICJUSZA: mierzymy czy zysk zależy od kilku wyjątkowych transakcji
   (które mogą się nie powtórzyć), czy od stabilnego powtarzalnego edge.

Razem z DSR/PBO tworzy TRÓJKĘ walidacji anty-overfittingowej Imperium:
  DSR (selection bias) + PBO/CSCV (in-sample→OOS) + Monte Carlo (stabilność).
"""

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np


@dataclass
class WynikMonteCarlo:
    """Raport z jednej symulacji Monte Carlo (shuffle lub bootstrap)."""
    n_symulacji: int
    metoda: str           # "shuffle" | "bootstrap"
    sharpe_mediana: float
    sharpe_p5: float      # 5. percentyl — pesymistyczny scenariusz
    sharpe_p95: float     # 95. percentyl — optymistyczny
    maxdd_mediana: float
    maxdd_p95: float      # 95. percentyl worst-case drawdown
    p_sharpe_dodatni: float   # P(Sharpe > 0)
    p_sharpe_pow_1: float     # P(Sharpe > 1)
    ok: bool
    powod: str


@dataclass
class PelenRaportMC:
    """Zbiorczy raport Monte Carlo (shuffle + bootstrap)."""
    shuffle: WynikMonteCarlo
    bootstrap: WynikMonteCarlo
    ok: bool
    powod: str
    n_transakcji: int


# ─── Progi werdyktu Imperium ───────────────────────────────────────────────────
PROG_P_DODATNI = 0.90   # P(Sharpe>0) ≥ 90% → edge stabilny
PROG_MAXDD_P95 = 0.25   # MaxDD_p95 < 25% → akceptowalny worst-case


def _sharpe_z_zwrotow(zwroty: np.ndarray) -> float:
    sd = float(zwroty.std(ddof=1))
    if sd == 0.0:
        return 0.0
    return float(zwroty.mean() / sd)


def _max_dd(krzywa: np.ndarray) -> float:
    """Maksymalny drawdown z krzywej equity [0, 1]."""
    szczyt = np.maximum.accumulate(krzywa)
    mask = szczyt > 0
    dd = np.where(mask, (szczyt - krzywa) / szczyt, 0.0)
    return float(dd.max())


def _krzywa_z_pnl(pnl_seria: np.ndarray, kapital_start: float) -> np.ndarray:
    krzywa = np.empty(len(pnl_seria) + 1)
    krzywa[0] = kapital_start
    np.cumsum(pnl_seria, out=krzywa[1:])
    krzywa[1:] += kapital_start
    return krzywa


def _buduj_raport(
    sharpe_lista: np.ndarray,
    maxdd_lista: np.ndarray,
    n_sym: int,
    metoda: str,
) -> WynikMonteCarlo:
    p_pos = float((sharpe_lista > 0).mean())
    p_pow1 = float((sharpe_lista > 1.0).mean())
    maxdd_p95 = float(np.percentile(maxdd_lista, 95))

    ok = p_pos >= PROG_P_DODATNI and maxdd_p95 < PROG_MAXDD_P95
    powod = ""
    if not ok:
        if p_pos < PROG_P_DODATNI:
            powod = f"P(Sharpe>0)={p_pos:.1%} < {PROG_P_DODATNI:.0%} — edge niestabilny"
        elif maxdd_p95 >= PROG_MAXDD_P95:
            powod = f"MaxDD_p95={maxdd_p95:.1%} ≥ {PROG_MAXDD_P95:.0%} — zbyt głęboki worst-case"

    return WynikMonteCarlo(
        n_symulacji=n_sym,
        metoda=metoda,
        sharpe_mediana=round(float(np.median(sharpe_lista)), 4),
        sharpe_p5=round(float(np.percentile(sharpe_lista, 5)), 4),
        sharpe_p95=round(float(np.percentile(sharpe_lista, 95)), 4),
        maxdd_mediana=round(float(np.median(maxdd_lista)), 4),
        maxdd_p95=round(maxdd_p95, 4),
        p_sharpe_dodatni=round(p_pos, 4),
        p_sharpe_pow_1=round(p_pow1, 4),
        ok=ok,
        powod=powod,
    )


def monte_carlo_shuffle(
    pnl_transakcji: Sequence[float],
    n_symulacji: int = 1000,
    kapital_start: float = 10_000.0,
    seed: Optional[int] = 42,
) -> WynikMonteCarlo:
    """
    Shuffle Monte Carlo: tasuje kolejność transakcji N razy.

    pnl_transakcji: lista P&L każdej zamkniętej transakcji (USD).
    n_symulacji:    liczba tasowań (≥ 500 zalecane).
    kapital_start:  do liczenia MaxDD.
    seed:           dla reprodukowalności (None → losowe).
    """
    pnl = np.asarray(list(pnl_transakcji), dtype=float)
    n_tr = len(pnl)
    if n_tr < 10:
        return WynikMonteCarlo(
            n_symulacji=0, metoda="shuffle",
            sharpe_mediana=0, sharpe_p5=0, sharpe_p95=0,
            maxdd_mediana=0, maxdd_p95=0,
            p_sharpe_dodatni=0, p_sharpe_pow_1=0,
            ok=False, powod=f"za mało transakcji ({n_tr} < 10)",
        )
    rng = np.random.default_rng(seed)
    sharpe_a = np.empty(n_symulacji)
    maxdd_a = np.empty(n_symulacji)
    for i in range(n_symulacji):
        tasowane = rng.permutation(pnl)
        krzywa = _krzywa_z_pnl(tasowane, kapital_start)
        zwroty = np.diff(krzywa) / np.where(krzywa[:-1] != 0, krzywa[:-1], 1.0)
        sharpe_a[i] = _sharpe_z_zwrotow(zwroty)
        maxdd_a[i] = _max_dd(krzywa)
    return _buduj_raport(sharpe_a, maxdd_a, n_symulacji, "shuffle")


def monte_carlo_bootstrap(
    pnl_transakcji: Sequence[float],
    n_symulacji: int = 1000,
    kapital_start: float = 10_000.0,
    seed: Optional[int] = 42,
) -> WynikMonteCarlo:
    """
    Bootstrap Monte Carlo: próbkuje transakcje ze zwrotem.

    Symuluje alternatywne "scenariusze" z tych samych cegiełek.
    Wykrywa zależność zysku od kilku wyjątkowych transakcji.
    """
    pnl = np.asarray(list(pnl_transakcji), dtype=float)
    n_tr = len(pnl)
    if n_tr < 10:
        return WynikMonteCarlo(
            n_symulacji=0, metoda="bootstrap",
            sharpe_mediana=0, sharpe_p5=0, sharpe_p95=0,
            maxdd_mediana=0, maxdd_p95=0,
            p_sharpe_dodatni=0, p_sharpe_pow_1=0,
            ok=False, powod=f"za mało transakcji ({n_tr} < 10)",
        )
    rng = np.random.default_rng(seed)
    sharpe_a = np.empty(n_symulacji)
    maxdd_a = np.empty(n_symulacji)
    for i in range(n_symulacji):
        probka = rng.choice(pnl, size=n_tr, replace=True)
        krzywa = _krzywa_z_pnl(probka, kapital_start)
        zwroty = np.diff(krzywa) / np.where(krzywa[:-1] != 0, krzywa[:-1], 1.0)
        sharpe_a[i] = _sharpe_z_zwrotow(zwroty)
        maxdd_a[i] = _max_dd(krzywa)
    return _buduj_raport(sharpe_a, maxdd_a, n_symulacji, "bootstrap")


def pelen_raport_mc(
    pnl_transakcji: Sequence[float],
    n_symulacji: int = 1000,
    kapital_start: float = 10_000.0,
    seed: Optional[int] = 42,
) -> PelenRaportMC:
    """
    Pełny raport Monte Carlo (shuffle + bootstrap) z werdyktem zbiorczym.

    ok=True tylko gdy OBA testy przeszły (P(SR>0)≥90%, MaxDD_p95<25%).
    Wywoływany po etap_pierwszy_koloseum jako dodatkowa bramka pewności.
    """
    pnl = list(pnl_transakcji)
    sh = monte_carlo_shuffle(pnl, n_symulacji, kapital_start, seed)
    bo = monte_carlo_bootstrap(pnl, n_symulacji, kapital_start, seed)
    ok = sh.ok and bo.ok
    powod = ""
    if not sh.ok:
        powod = f"shuffle: {sh.powod}"
    elif not bo.ok:
        powod = f"bootstrap: {bo.powod}"
    return PelenRaportMC(
        shuffle=sh,
        bootstrap=bo,
        ok=ok,
        powod=powod,
        n_transakcji=len(pnl),
    )
