"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         WarRoom — Dashboard & Command Center v2.0                            ║
║  Autor: Jack (Wizjoner, Architekt, Wynalazca, Magik)                        ║
║  Licencja: Kingdom Pixel — wszelkie prawa autorskie                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA (Zasada 11) ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-DASH-207                                                    |
| Nazwa oryginalna    | WarRoom — Dashboard & Command Center                         |
| Nazwa w Królestwie  | WarRoom (Sala Wojenna)                                        |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/DASH-207_WarRoom.py                  |
| Kategoria           | DASH / Monitoring, alerty                                     |
| Wpływ na Królestwo  | Centrum dowodzenia botów. Po naprawie win_rate jest          |
|                     | policzony poprawnie (wins/trades).                           |
| Powiązane moduły    | N-ORCH-209, N-MEM-206, N-SHIELDS-205                         |

CHANGELOG:
  v2.0 (2026-05-28) — BUGFIX (Zasada 2 — Prawda). `win_rate` był aktualizowany
        TYLKO przy wygranej (`if won:`), więc przy przegranych licznik trades rósł,
        a wskaźnik nie był przeliczany → win_rate ZAWYŻONY. Dodano osobny licznik
        `wins` i win_rate = wins / trades (zawsze spójny).
  v1.0 — wersja wyjściowa (błędny win_rate).

Mechanizm:
1. REAL-TIME MONITORING — śledzenie botów i PnL.
2. ALERTY — krytyczne zdarzenia (wyczerpanie kapitału, +30% profit).
3. PERFORMANCE DASHBOARD — przegląd stanu floty.
═════════════════════════════════════════════════════════════════════════════════════
"""

import time
import random
import logging
from dataclasses import dataclass
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("WarRoom")


@dataclass
class BotStatus:
    name: str
    capital: float
    pnl: float
    win_rate: float
    trades: int
    active: bool
    wins: int = 0          # BUGFIX v2.0: osobny licznik wygranych
    initial_capital: float = 0.0
    profit_alert_fired: bool = False


class WarRoom:
    def __init__(self):
        self.bots: Dict[str, BotStatus] = {}
        self.alerts: List[str] = []

    def register_bot(self, name: str, capital: float):
        self.bots[name] = BotStatus(name, capital, 0.0, 0.0, 0, True, wins=0, initial_capital=capital)
        logger.info(f"[WarRoom] Zarejestrowano bota: {name} (${capital:.2f})")

    def update_bot(self, name: str, trade_pnl: float, won: bool):
        bot = self.bots[name]
        bot.capital += trade_pnl
        bot.pnl += trade_pnl
        bot.trades += 1
        if won:
            bot.wins += 1
        # BUGFIX v2.0: zawsze przeliczamy z licznika wins (spójne przy stratach).
        bot.win_rate = bot.wins / bot.trades if bot.trades > 0 else 0.0

        if bot.capital <= 0:
            bot.active = False
            self.alerts.append(f"🚨 {name}: KAPITAŁ WYCZERPANY!")
            logger.error(f"[WarRoom] {self.alerts[-1]}")

        # +30% zwrotu względem kapitału początkowego (alert jednorazowy)
        if (not bot.profit_alert_fired and bot.initial_capital > 0
                and (bot.pnl / bot.initial_capital) >= 0.30):
            bot.profit_alert_fired = True
            self.alerts.append(f"⚡ {name}: +30% PROFIT — zamknij lub skaluj!")
            logger.info(f"[WarRoom] {self.alerts[-1]}")

    def display_dashboard(self):
        logger.info("=" * 50)
        logger.info("         🏰 WAR ROOM DASHBOARD")
        logger.info("=" * 50)
        for name, bot in self.bots.items():
            status = "🟢" if bot.active else "🔴"
            logger.info(f"{status} {name:20s} | Kapitał: ${bot.capital:7.2f} | PnL: {bot.pnl:+6.2f} | WR: {bot.win_rate:.1%} ({bot.wins}/{bot.trades})")
        logger.info("=" * 50)

    def get_alerts(self) -> List[str]:
        alerts = self.alerts.copy()
        self.alerts.clear()
        return alerts


def main():
    logger.info("=== WarRoom v2.0 Demo ===")
    random.seed(11)
    wr = WarRoom()
    for bot_name in ["THOR-MACRO", "THOR-SNIPER", "THOR-GRID", "THOR-MEME"]:
        wr.register_bot(bot_name, random.uniform(5, 20))

    for _ in range(5):
        for name in wr.bots:
            pnl = random.uniform(-3, 5)
            won = pnl > 0
            wr.update_bot(name, pnl, won)
        time.sleep(0.05)

    wr.display_dashboard()
    for alert in wr.get_alerts():
        logger.warning(f"📢 ALERT: {alert}")

    print("\n✅ WarRoom v2.0 — demo zakończone (win_rate naprawiony).")


if __name__ == "__main__":
    main()
