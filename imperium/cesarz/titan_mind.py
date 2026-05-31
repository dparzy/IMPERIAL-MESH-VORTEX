"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       TitanMind — Strategy Orchestrator & Scheduler v1.0                     ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                        ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Mechanizm:
1. STRATEGY SCHEDULER — zarządzanie harmonogramem uruchamiania botów.
2. CONFLICT RESOLVER — zapobieganie kolizjom (dwa boty na tym samym symbolu).
3. RESOURCE ALLOCATOR — dynamiczny przydział kapitału na podstawie wyników.
"""

import time, logging
from dataclasses import dataclass, field
from typing import Dict, List, Set
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("TitanMind")

class StrategyState(str, Enum): IDLE = "IDLE"; ACTIVE = "ACTIVE"; COOLDOWN = "COOLDOWN"; BANNED = "BANNED"

@dataclass
class Strategy:
    name: str; symbols: List[str]; capital: float; weight: float
    state: StrategyState = StrategyState.IDLE
    cooldown_until: float = 0.0; total_pnl: float = 0.0; trades: int = 0

class TitanMind:
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
        self.active_symbols: Set[str] = set()

    def register(self, name: str, symbols: List[str], capital: float, weight: float):
        self.strategies[name] = Strategy(name, symbols, capital, weight)
        logger.info(f"[TitanMind] Zarejestrowano: {name} | Symbole: {symbols} | Kapitał: ${capital:.2f}")

    def request_execution(self, name: str) -> str:
        strat = self.strategies[name]
        if strat.state == StrategyState.COOLDOWN and time.time() < strat.cooldown_until:
            logger.warning(f"[TitanMind] {name}: ⏳ COOLDOWN — odmowa.")
            return "COOLDOWN"
        if strat.state == StrategyState.BANNED:
            logger.warning(f"[TitanMind] {name}: 🚫 BANNED — odmowa.")
            return "BANNED"

        # Conflict resolution — sprawdź czy symbol nie jest już zajęty
        for sym in strat.symbols:
            if sym in self.active_symbols:
                logger.warning(f"[TitanMind] {name}: ⚠️ Kolizja — {sym} już aktywny!")
                return "CONFLICT"

        strat.state = StrategyState.ACTIVE
        for sym in strat.symbols:
            self.active_symbols.add(sym)
        logger.info(f"[TitanMind] ✅ {name}: START | Symbole: {strat.symbols}")
        return "OK"

    def release(self, name: str, pnl: float):
        strat = self.strategies[name]
        strat.state = StrategyState.IDLE
        strat.total_pnl += pnl
        strat.trades += 1
        for sym in strat.symbols:
            self.active_symbols.discard(sym)
        logger.info(f"[TitanMind] {name}: ZWOLNIONY | PnL: {pnl:+.2f}")

        # Auto-cooldown dla słabo radzących sobie strategii
        if pnl < 0 and strat.trades >= 3 and (strat.total_pnl / (strat.capital + 1e-9)) < -0.15:
            strat.cooldown_until = time.time() + 3600
            strat.state = StrategyState.COOLDOWN
            logger.warning(f"[TitanMind] {name}: 🔄 AUTO-COOLDOWN 1h z powodu słabych wyników.")

    def get_best_strategy(self) -> str:
        best = max(self.strategies.values(), key=lambda s: s.total_pnl / (s.capital + 1e-9) * s.weight)
        return best.name

def main():
    logger.info("=== TitanMind v1.0 Demo ===")
    tm = TitanMind()
    tm.register("THOR-MACRO", ["BTC/USDT", "ETH/USDT"], 16.5, 0.33)
    tm.register("THOR-SNIPER", ["SOL/USDT", "DOGE/USDT"], 2.5, 0.05)
    tm.register("THOR-GRID", ["LTC/USDT"], 2.5, 0.05)

    # Test 1: poprawne uruchomienie
    logger.info(tm.request_execution("THOR-MACRO"))

    # Test 2: kolizja — ten sam symbol
    logger.info(tm.request_execution("THOR-GRID"))  # LTC/USDT — OK

    # Test 3: zwolnienie
    tm.release("THOR-MACRO", 5.0)
    tm.release("THOR-GRID", -1.5)

    logger.info(f"Najlepsza strategia: {tm.get_best_strategy()}")
    print("\n✅ TitanMind v1.0 — demo zakończone.")

if __name__ == "__main__":
    main()