"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          AegisShield — Multi-Layer Risk Engine v1.0                          ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                        ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Mechanizm:
1. 3-TIER DRAWDOWN — 20% alert / 30% stop nowych / 50% flatten all.
2. MAX DAILY LOSS — UTC-based daily loss limit z auto-resetem.
3. CIRCUIT BREAKER — 3 kolejne straty = 60min blokady.
"""

import time, logging
from dataclasses import dataclass
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("AegisShield")

class AegisShield:
    def __init__(self, initial_capital: float = 50.0, daily_loss_limit_pct: float = 0.10,
                 tier_warning: float = 0.20, tier_no_new: float = 0.30, tier_flatten: float = 0.50,
                 max_consecutive_losses: int = 3, cooldown_minutes: int = 60):
        self.initial_capital = initial_capital
        self.peak_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = 0.0
        self.daily_reset_time = time.time()
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.tiers = {"WARNING": tier_warning, "NO_NEW": tier_no_new, "FLATTEN": tier_flatten}
        self.consecutive_losses = 0
        self.max_consecutive = max_consecutive_losses
        self.cooldown_minutes = cooldown_minutes
        self.cooldown_until: float = 0.0
        self.blocked: bool = False

    def _reset_daily(self):
        if time.time() - self.daily_reset_time > 86400:
            self.daily_pnl = 0.0
            self.daily_reset_time = time.time()
            logger.info("[Aegis] Nowy dzień — daily PnL zresetowany.")

    def update(self, trade_pnl: float) -> str:
        self._reset_daily()
        self.current_capital += trade_pnl
        self.daily_pnl += trade_pnl
        self.peak_capital = max(self.peak_capital, self.current_capital)

        drawdown_from_peak = (self.peak_capital - self.current_capital) / self.peak_capital

        if time.time() < self.cooldown_until:
            logger.warning("[Aegis] ⏳ COOLDOWN — handel zablokowany.")
            self.blocked = True
            return "COOLDOWN"

        if trade_pnl < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.max_consecutive:
                self.cooldown_until = time.time() + self.cooldown_minutes * 60
                logger.warning(f"[Aegis] 🔴 CIRCUIT BREAKER — {self.cooldown_minutes}min blokady!")
                self.blocked = True
                return "CIRCUIT_BREAKER"
        else:
            self.consecutive_losses = 0
            self.blocked = False

        if drawdown_from_peak >= self.tiers["FLATTEN"]:
            logger.error("[Aegis] 🛑 FLATTEN ALL — 50% drawdown!")
            return "FLATTEN_ALL"
        elif drawdown_from_peak >= self.tiers["NO_NEW"]:
            logger.warning("[Aegis] ⚠️ NO NEW POSITIONS — 30% drawdown.")
            return "NO_NEW_POSITIONS"
        elif drawdown_from_peak >= self.tiers["WARNING"]:
            logger.info("[Aegis] ⚡ WARNING — 20% drawdown.")
            return "WARNING"

        if abs(self.daily_pnl) / self.initial_capital >= self.daily_loss_limit_pct and self.daily_pnl < 0:
            logger.warning("[Aegis] 🚫 DAILY LOSS LIMIT osiągnięty!")
            return "DAILY_LIMIT"

        return "OK"

def main():
    logger.info("=== AegisShield v1.0 Demo ===")
    shield = AegisShield(initial_capital=50.0)

    trades = [-2.0, -3.0, -5.0, 1.0, -8.0, -4.0, -15.0]
    for i, pnl in enumerate(trades):
        status = shield.update(pnl)
        logger.info(f"Trade {i+1}: PnL={pnl:+.1f} | Kapitał={shield.current_capital:.1f} | Status={status}")
        if status in ["CIRCUIT_BREAKER", "FLATTEN_ALL"]:
            break

    print("\n✅ AegisShield v1.0 — demo zakończone.")

if __name__ == "__main__":
    main()