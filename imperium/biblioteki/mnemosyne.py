"""
╔══════════════════════════════════════════════════════════════════════════════╗
║      Mnemosyne — Memory & Trade Learning Record System v2.0                 ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                        ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-MEM-206                                                     |
| Nazwa oryginalna    | Mnemosyne — Memory & Trade Learning Record System           |
| Nazwa w Imperium    | Mnemosyne (Pamięć Imperium)                                  |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/MEM-206_Mnemosyne.py                 |
| Kategoria           | MEM / Pamięć trwała, uczenie z transakcji                    |
| Wpływ na Imperium   | Trwała pamięć transakcji + Księga Wad. Po naprawie każdy     |
|                     | rekord ma prawdziwy, własny znacznik czasu.                  |
| Powiązane moduły    | N-BRAIN-026, N-BACK-210, N-DASH-207                         |

CHANGELOG:
  v2.0 (2026-05-28) — BUGFIX (Prawo I — Prawda). `timestamp: float = time.time()`
        było ewaluowane RAZ przy definicji klasy → wszystkie rekordy dostawały ten
        sam (startowy) znacznik czasu. Zmieniono na `field(default_factory=time.time)`,
        więc czas jest pobierany w momencie tworzenia każdego rekordu.
  v1.0 — wersja wyjściowa (wspólny timestamp).

Mechanizm:
1. TRADE LEARNING RECORD — każdy trade → wpis z atrybucją i lekcją.
2. BOOK OF FLAWS — rejestr błędów blokujący powtarzanie pomyłek.
3. PERSISTENT MEMORY — SQLite do ciągłego uczenia.
═════════════════════════════════════════════════════════════════════════════════════
"""

import sqlite3
import time
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("Mnemosyne")


@dataclass
class TradeLearningRecord:
    record_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    pnl_pct: float
    reasoning: str
    lesson: str
    # BUGFIX v2.0: default_factory — czas pobierany przy tworzeniu KAŻDEGO rekordu.
    timestamp: float = field(default_factory=time.time)


class Mnemosyne:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS trades "
            "(id TEXT, symbol TEXT, side TEXT, entry REAL, exit REAL, pnl REAL, reasoning TEXT, lesson TEXT, ts REAL)"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS book_of_flaws "
            "(id INTEGER PRIMARY KEY, flaw TEXT, severity TEXT, timestamp REAL)"
        )
        self.conn.commit()

    def record_trade(self, trade: TradeLearningRecord) -> str:
        self.conn.execute(
            "INSERT INTO trades VALUES (?,?,?,?,?,?,?,?,?)",
            (trade.record_id, trade.symbol, trade.side, trade.entry_price, trade.exit_price,
             trade.pnl_pct, trade.reasoning, trade.lesson, trade.timestamp)
        )
        self.conn.commit()
        logger.info(f"[Mnemosyne] Zapisano trade: {trade.record_id} | PnL: {trade.pnl_pct:+.2%} | ts: {trade.timestamp:.3f}")
        return trade.record_id

    def add_flaw(self, flaw: str, severity: str = "MEDIUM"):
        self.conn.execute(
            "INSERT INTO book_of_flaws (flaw, severity, timestamp) VALUES (?,?,?)",
            (flaw, severity, time.time())
        )
        self.conn.commit()
        logger.warning(f"[Mnemosyne] BookOfFlaws: {flaw} ({severity})")

    def check_flaw(self, reasoning: str) -> bool:
        flaws = self.conn.execute("SELECT flaw FROM book_of_flaws").fetchall()
        for f in flaws:
            if f[0].lower() in reasoning.lower():
                logger.info(f"[Mnemosyne] ⚠️ Wykryto znany błąd: {f[0]}")
                return True
        return False

    def get_lessons(self) -> list:
        return self.conn.execute("SELECT DISTINCT lesson FROM trades WHERE lesson != ''").fetchall()


def main():
    logger.info("=== Mnemosyne v2.0 Demo ===")
    mem = Mnemosyne()

    trade1 = TradeLearningRecord(
        record_id=hashlib.md5(b"BTCUSDT_BUY_1").hexdigest()[:12],
        symbol="BTC/USDT", side="BUY", entry_price=50000, exit_price=51000,
        pnl_pct=0.02, reasoning="Golden Cross + CVD divergence",
        lesson="Wchodzić tylko gdy CVD potwierdza trend."
    )
    mem.record_trade(trade1)
    time.sleep(0.05)
    trade2 = TradeLearningRecord(
        record_id=hashlib.md5(b"ETHUSDT_SELL_1").hexdigest()[:12],
        symbol="ETH/USDT", side="SELL", entry_price=3000, exit_price=2950,
        pnl_pct=0.017, reasoning="Bear div RSI", lesson="Szanować opór."
    )
    mem.record_trade(trade2)

    # Dowód poprawki: różne znaczniki czasu
    assert trade1.timestamp != trade2.timestamp, "BUG: identyczne timestampy!"
    logger.info(f"[TEST] Różne timestampy: {trade2.timestamp - trade1.timestamp:.3f}s — OK")

    mem.add_flaw("Kupowanie bez potwierdzenia CVD", "HIGH")
    print("\n✅ Mnemosyne v2.0 — demo zakończone (timestamp naprawiony).")


if __name__ == "__main__":
    main()
