"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Valhalla — Backtesting & Simulation Arena v2.0                         ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                        ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-BACK-210                                                    |
| Nazwa oryginalna    | Valhalla — Backtesting & Simulation Arena                    |
| Nazwa w Imperium    | Valhalla (Arena Próby)                                        |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/BACK-210_Valhalla.py                 |
| Kategoria           | BACK / Backtest, Monte Carlo, walk-forward                   |
| Wpływ na Imperium   | Arena testowa strategii. Sygnały RSI z TA-Lib (Prawo I);   |
|                     | metryki portfela = deterministyczny NumPy (brak ich w TA-Lib)|
| Powiązane moduły    | N-TOOLS-208, N-BRAIN-026, N-ORCH-209                         |

CHANGELOG:
  v2.0 (2026-05-28) — (1) ZASADA 75: generator sygnałów liczył RSI ręcznie →
        zastąpiony TA-Lib. (2) BUGFIX: stary generator liczył JEDEN RSI i wpisywał
        IDENTYCZNY sygnał do wszystkich barów (sygnał zdegenerowany). Teraz RSI jest
        liczone per-bar, a sygnał generowany dla każdego baru osobno.
        (3) Guard liczbowy: Sharpe/Sortino = 0 dla <2 zwrotów (std≈0 powodował
        eksplozję wartości w oknach walk-forward).
        UWAGA metodologiczna: annualizacja Sharpe sqrt(252) traktuje zwroty z
        transakcji jak dzienne — świadome uproszczenie demonstracyjne.
  v1.0 — wersja wyjściowa (ręczny RSI + sygnał zdegenerowany).

Mechanizm:
1. WALK-FORWARD BACKTESTING — okna trening/test.
2. MONTE CARLO — bootstrap zwrotów dla oceny stabilności.
3. SHARPE / SORTINO / CALMAR / MAX DD — pełny zestaw metryk (NumPy, deterministyczny).
═════════════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import logging
from typing import List, Dict
from dataclasses import dataclass

# ── Prawo I: wskaźniki z deterministycznego rdzenia TA-Lib. ──
try:
    import talib
except ImportError as e:
    raise RuntimeError(
        "N-BACK-210 wymaga TA-Lib (Prawo I) do generacji sygnałów. "
        "Instalacja: `pip install TA-Lib`."
    ) from e

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("Valhalla")


@dataclass
class BacktestResult:
    total_return: float; sharpe: float; sortino: float; calmar: float
    max_drawdown: float; win_rate: float; profit_factor: float; trades: int


class Valhalla:
    def __init__(self, prices: List[float]):
        self.prices = prices

    def run_simple_backtest(self, signals: List[int]) -> BacktestResult:
        """signals: 1 (LONG), -1 (SHORT), 0 (NEUTRAL). Backtest bez kosztów transakcyjnych."""
        returns = []
        wins = 0; trades = 0
        position = 0
        entry_price = 0.0

        for i, sig in enumerate(signals[:-1]):
            if sig != 0 and position == 0:
                position = sig; entry_price = self.prices[i]; trades += 1
            elif sig == 0 and position != 0:
                pnl = (self.prices[i] - entry_price) * position / entry_price
                returns.append(pnl)
                if pnl > 0: wins += 1
                position = 0

        if position != 0:
            pnl = (self.prices[-1] - entry_price) * position / entry_price
            returns.append(pnl)
            if pnl > 0: wins += 1

        return self._calculate_metrics(returns, wins, trades)

    def _calculate_metrics(self, returns: List[float], wins: int, trades: int) -> BacktestResult:
        if not returns:
            return BacktestResult(0, 0, 0, 0, 0, 0, 0, 0)

        arr = np.array(returns)
        total_return = np.prod(1 + arr) - 1

        # BUGFIX v2.0: dla <2 zwrotów odchylenie jest nieokreślone (std≈0) → Sharpe
        # eksplodował do absurdów. Guard: wymagamy min. 2 zwrotów i std > 0.
        std_all = np.std(arr)
        sharpe = (np.mean(arr) / std_all * np.sqrt(252)) if (len(arr) >= 2 and std_all > 1e-8) else 0.0

        neg_returns = arr[arr < 0]
        std_neg = np.std(neg_returns) if len(neg_returns) > 0 else 0.0
        sortino = (np.mean(arr) / std_neg * np.sqrt(252)) if (len(neg_returns) >= 2 and std_neg > 1e-8) else 0.0

        cumulative = np.cumprod(1 + arr)
        peak = np.maximum.accumulate(cumulative)
        drawdowns = (peak - cumulative) / peak
        max_dd = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
        calmar = total_return / (max_dd + 1e-9)

        wr = wins / trades if trades > 0 else 0.0
        gross_profit = arr[arr > 0].sum() if len(arr[arr > 0]) > 0 else 0.0
        gross_loss = abs(arr[arr < 0].sum()) if len(arr[arr < 0]) > 0 else 1.0
        pf = gross_profit / (gross_loss + 1e-9)

        return BacktestResult(total_return, sharpe, sortino, calmar, max_dd, wr, pf, trades)

    def monte_carlo(self, returns: List[float], n_sims: int = 1000) -> Dict[str, float]:
        arr = np.array(returns)
        sharpes = []
        for _ in range(n_sims):
            shuffled = np.random.choice(arr, size=len(arr), replace=True)
            s = np.mean(shuffled) / (np.std(shuffled) + 1e-9) * np.sqrt(252)
            sharpes.append(s)
        return {"sharpe_mean": np.mean(sharpes), "sharpe_5pct": np.percentile(sharpes, 5), "sharpe_95pct": np.percentile(sharpes, 95)}

    def walk_forward(self, signals_func, n_windows: int = 4, train_pct: float = 0.6) -> List[BacktestResult]:
        n = len(self.prices)
        window_size = n // n_windows
        results = []
        for i in range(n_windows):
            start = i * window_size
            end = min((i + 1) * window_size, n)
            split = start + int(window_size * train_pct)
            test_prices = self.prices[split:end]
            test_signals = signals_func(test_prices)
            results.append(Valhalla(test_prices).run_simple_backtest(test_signals))
        return results


def generate_rsi_signals(prices: List[float], period: int = 14, low: float = 35, high: float = 65) -> List[int]:
    """
    ZASADA 75: RSI z TA-Lib (deterministyczny rdzeń C).
    BUGFIX v2.0: sygnał liczony PER BAR (stary kod wpisywał jeden sygnał do wszystkich barów).
    """
    arr = np.asarray(prices, dtype=np.float64)
    if len(arr) <= period:
        return [0] * len(prices)
    rsi = talib.RSI(arr, timeperiod=period)
    signals = []
    for v in rsi:
        if np.isnan(v):
            signals.append(0)
        elif v < low:
            signals.append(1)      # oversold → LONG
        elif v > high:
            signals.append(-1)     # overbought → SHORT
        else:
            signals.append(0)
    return signals


def main():
    logger.info("=== Valhalla v2.0 Demo (Prawo I — sygnały TA-Lib) ===")
    np.random.seed(42)
    prices = [50000.0]
    for _ in range(500):
        prices.append(prices[-1] * (1 + np.random.normal(0.0005, 0.02)))

    valhalla = Valhalla(prices)
    signals = generate_rsi_signals(prices)
    result = valhalla.run_simple_backtest(signals)

    logger.info(f"Sharpe: {result.sharpe:.2f} | Sortino: {result.sortino:.2f} | Calmar: {result.calmar:.2f}")
    logger.info(f"Max DD: {result.max_drawdown:.2%} | Win Rate: {result.win_rate:.1%} | PF: {result.profit_factor:.2f} | Trades: {result.trades}")

    mc = valhalla.monte_carlo([r for r in np.diff(prices) / prices[:-1]][:100])
    logger.info(f"Monte Carlo Sharpe: mean={mc['sharpe_mean']:.2f} [5%-95%: {mc['sharpe_5pct']:.2f} - {mc['sharpe_95pct']:.2f}]")

    wf = valhalla.walk_forward(generate_rsi_signals, n_windows=4)
    logger.info(f"Walk-Forward: {len(wf)} okien | Średni Sharpe: {np.mean([r.sharpe for r in wf]):.2f}")

    print("\n✅ Valhalla v2.0 — demo zakończone (sygnały z TA-Lib, bug per-bar naprawiony).")


if __name__ == "__main__":
    main()
