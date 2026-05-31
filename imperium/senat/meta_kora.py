"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     MetaCortex — Samodoskonalący się Agent z Meta-Learningiem v3.0          ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                        ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-BRAIN-026                                                   |
| Nazwa oryginalna    | MetaCortex — Samodoskonalący się Agent z Meta-Learningiem    |
| Nazwa w Imperium    | MetaCortex (Meta-Kora)                                        |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/BRAIN-026_MetaCortex.py              |
| Kategoria           | BRAIN / Meta-learning, decyzja wieloagentowa                 |
| Wpływ na Imperium   | Centralny mózg debaty agentów (Aktor-Sędzia-MetaSędzia).     |
|                     | Trend liczony teraz z TA-Lib (Prawo I).                    |
| Powiązane moduły    | N-TOOLS-208 (ToolForge), N-ORCH-209 (TitanMind),             |
|                     | N-MEM-206 (Mnemosyne)                                        |

CHANGELOG:
  v3.0 (2026-05-28) — (1) ZGODNOŚĆ Z ZASADĄ 75: TrendAgent liczy EMA20/EMA50 przez
        TA-Lib (poprzednio liczył ZWYKŁĄ ŚREDNIĄ i błędnie nazywał ją "EMA").
        (2) BUGFIX: MetaJudge.evaluate() — błąd precedencji `and/or` powodował, że
        warunek SHORT nie był chroniony przez `pnl_pct is not None`; celność była
        liczona błędnie. Poprawiono jawnym grupowaniem nawiasami.
  v2.0 — wersja wyjściowa.

Mechanizm:
1. AKTOR-SĘDZIA-META-SĘDZIA — zamknięta pętla uczenia bez nadzoru.
2. DEBATA MoA — TrendAgent, SentimentAgent, MicroAgent → SuperJudge.
3. EWOLUCJA STRATEGII — co N cykli mutacja najlepszej, zastępowanie najsłabszej.
═════════════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import random
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

# ── Prawo I: matematyka trendu z deterministycznego rdzenia TA-Lib. ──
try:
    import talib
except ImportError as e:
    raise RuntimeError(
        "N-BRAIN-026 wymaga TA-Lib (Prawo I). Instalacja: `pip install TA-Lib`. "
        "Brak ręcznego fallbacku — gwarancja kanonicznych wartości EMA."
    ) from e

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("MetaCortex")


class Signal(str, Enum):
    LONG = "LONG"; SHORT = "SHORT"; NEUTRAL = "NEUTRAL"


@dataclass
class DebateArgument:
    agent: str; signal: Signal; confidence: float; reasoning: str


@dataclass
class DecisionRecord:
    timestamp: float; symbol: str; agents_votes: Dict[str, Signal]
    final_decision: Signal; pnl_pct: Optional[float] = None
    regret: float = 0.0; hash: str = ""


@dataclass
class StrategyVariant:
    name: str; weight: float; sharpe: float = 0.0; trades: int = 0; wins: int = 0; generation: int = 0


class TrendAgent:
    def analyze(self, prices: list) -> DebateArgument:
        if len(prices) < 50:
            return DebateArgument("TrendAgent", Signal.NEUTRAL, 0.0, "Za mało danych.")
        # ZASADA 75: prawdziwe EMA z TA-Lib (nie ręczna średnia).
        arr = np.asarray(prices, dtype=np.float64)
        ema20 = talib.EMA(arr, timeperiod=20)[-1]
        ema50 = talib.EMA(arr, timeperiod=50)[-1]
        last = prices[-1]
        if np.isnan(ema20) or np.isnan(ema50):
            return DebateArgument("TrendAgent", Signal.NEUTRAL, 0.0, "Za mało danych (EMA warmup).")
        if last > ema20 > ema50:
            return DebateArgument("TrendAgent", Signal.LONG, 0.75, "Uptrend EMA20>EMA50 (TA-Lib).")
        elif last < ema20 < ema50:
            return DebateArgument("TrendAgent", Signal.SHORT, 0.75, "Downtrend (TA-Lib).")
        return DebateArgument("TrendAgent", Signal.NEUTRAL, 0.3, "Brak trendu.")


class SentimentAgent:
    def analyze(self, headlines: List[str]) -> DebateArgument:
        if not headlines:
            return DebateArgument("SentimentAgent", Signal.NEUTRAL, 0.0, "Brak danych.")
        pos = sum(1 for h in headlines if any(w in h.lower() for w in ["bull", "surge", "rally", "breakout"]))
        neg = sum(1 for h in headlines if any(w in h.lower() for w in ["crash", "dump", "fear", "ban"]))
        if pos > neg:
            return DebateArgument("SentimentAgent", Signal.LONG, 0.6, f"Pozytywny ({pos} vs {neg})")
        elif neg > pos:
            return DebateArgument("SentimentAgent", Signal.SHORT, 0.6, f"Negatywny ({neg} vs {pos})")
        return DebateArgument("SentimentAgent", Signal.NEUTRAL, 0.2, "Neutralny.")


class MicrostructureAgent:
    def analyze(self, bid_vol: float, ask_vol: float) -> DebateArgument:
        if ask_vol > bid_vol * 1.5:
            return DebateArgument("MicroAgent", Signal.SHORT, 0.7, "Przewaga ask.")
        elif bid_vol > ask_vol * 1.5:
            return DebateArgument("MicroAgent", Signal.LONG, 0.7, "Przewaga bid.")
        return DebateArgument("MicroAgent", Signal.NEUTRAL, 0.3, "Zbalansowany.")


class SuperJudge:
    def __init__(self):
        self.agent_accuracy: Dict[str, float] = {"TrendAgent": 0.55, "SentimentAgent": 0.50, "MicroAgent": 0.52}
        self.accuracy_window: List[Dict[str, float]] = []

    def debate(self, arguments: List[DebateArgument]) -> Tuple[Signal, float]:
        votes: Dict[str, float] = {"LONG": 0.0, "SHORT": 0.0, "NEUTRAL": 0.0}
        for arg in arguments:
            w = self.agent_accuracy.get(arg.agent, 0.5) * arg.confidence
            votes[arg.signal.value] += w
        best = max(votes, key=votes.get)
        confidence = votes[best] / (sum(votes.values()) + 1e-9)
        logger.info(f"[SuperJudge] Głosy: {votes} → {best} (pewność: {confidence:.2f})")
        return Signal(best), confidence

    def update_accuracy(self, agent: str, was_correct: bool):
        old = self.agent_accuracy[agent]
        lr = 0.1
        self.agent_accuracy[agent] = old + lr * ((1.0 if was_correct else 0.0) - old)
        self.agent_accuracy[agent] = max(0.1, min(0.95, self.agent_accuracy[agent]))
        logger.info(f"[SuperJudge] {agent}: {old:.2f} → {self.agent_accuracy[agent]:.2f}")


class MetaJudge:
    """Poprawia kryteria oceny SuperJudge'a na podstawie wyników."""
    def __init__(self):
        self.criteria_weights: Dict[str, float] = {"accuracy": 0.5, "consistency": 0.3, "adaptability": 0.2}

    def evaluate(self, records: List[DecisionRecord]) -> Dict[str, float]:
        # BUGFIX v3.0: jawne grupowanie nawiasami — warunek poprawnej decyzji ZAWSZE
        # chroniony przez `pnl_pct is not None`. Wcześniej `or` rozrywał ten warunek.
        correct = sum(
            1 for r in records
            if r.pnl_pct is not None and (
                (r.final_decision == Signal.LONG and r.pnl_pct > 0) or
                (r.final_decision == Signal.SHORT and r.pnl_pct < 0)
            )
        )
        total = len([r for r in records if r.pnl_pct is not None])
        acc = correct / total if total > 0 else 0.5
        logger.info(f"[MetaJudge] Celność ostatnich {total} decyzji: {acc:.2%}")
        return {"accuracy": acc, "recommendation": "Zwiększ wagę pewności" if acc < 0.5 else "Utrzymaj kryteria"}


class StrategyEvolution:
    def __init__(self, population_size: int = 5):
        self.population: List[StrategyVariant] = [
            StrategyVariant(f"Strategy_{i}", weight=1.0 / population_size, generation=0)
            for i in range(population_size)
        ]

    def evolve(self):
        best = max(self.population, key=lambda s: s.sharpe)
        worst = min(self.population, key=lambda s: s.sharpe)
        mutant = StrategyVariant(f"{best.name}_mut", weight=best.weight * 0.8,
                                 sharpe=best.sharpe * 0.9, generation=best.generation + 1)
        self.population.remove(worst)
        self.population.append(mutant)
        logger.info(f"[Evolution] Usunięto {worst.name} (Sharpe:{worst.sharpe:.2f}), dodano mutację {mutant.name}")


def main():
    logger.info("=== MetaCortex v3.0 Demo (Prawo I — TA-Lib) ===")
    random.seed(7)
    prices = [50000 + i * 100 + random.uniform(-500, 500) for i in range(60)]
    headlines = ["Bitcoin surges past resistance!", "Analysts predict new rally", "Fear of regulation looms"]
    trend = TrendAgent(); sentiment = SentimentAgent(); micro = MicrostructureAgent()
    judge = SuperJudge(); meta = MetaJudge(); evo = StrategyEvolution()

    args = [trend.analyze(prices), sentiment.analyze(headlines), micro.analyze(100.0, 50.0)]
    decision, conf = judge.debate(args)
    logger.info(f"Decyzja: {decision.value} (pewność: {conf:.2f})")

    was_correct = random.random() > 0.4
    judge.update_accuracy("TrendAgent", was_correct)

    records = [DecisionRecord(time.time(), "BTC/USDT", {a.agent: a.signal for a in args},
                              decision, pnl_pct=0.02 if was_correct else -0.01)]
    meta.evaluate(records)
    evo.evolve()

    print("\n✅ MetaCortex v3.0 — demo zakończone (Prawo I spełniona, bug MetaJudge naprawiony).")


if __name__ == "__main__":
    main()
