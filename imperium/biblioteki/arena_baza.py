"""
🏟️ ARENA BAZA — wspólna warstwa bazy wyników areny (SQLite, stdlib).

Jedno źródło prawdy dla zapisu/odczytu pomiarów areny (IC, scoreboard, live PnL).
Używają jej: `narzedzia/arena_mcp.py` (soczewka MCP dla Claude) oraz
`imperium/koloseum/petla_live.py` (opt-in auto-log wyników live). Dzięki wspólnej
warstwie (Prawo XVI reuse) narzędzie i rdzeń nie duplikują SQL-a ani ścieżki DB.

Baza `arena_wyniki.db` — runtime per-maszyna (gitignore, jak baza_wiedzy.db).
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = ROOT / "bibliotheca_ulpia" / "dane" / "arena_wyniki.db"


def _polacz(db_path: Path | str = DEFAULT_DB) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS pomiary ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " ts REAL NOT NULL,"
        " rodzaj TEXT NOT NULL,"
        " neuron TEXT NOT NULL,"
        " wartosc REAL NOT NULL,"
        " nota TEXT DEFAULT '')"
    )
    return conn


def zapisz_pomiar(rodzaj: str, neuron: str, wartosc: float, nota: str = "",
                  db_path: Path | str = DEFAULT_DB, ts: float | None = None) -> int:
    """Zapisuje jeden pomiar areny. Zwraca id wiersza. Puste rodzaj/neuron → ValueError."""
    if not rodzaj or not neuron:
        raise ValueError("rodzaj i neuron nie mogą być puste")
    conn = _polacz(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO pomiary (ts, rodzaj, neuron, wartosc, nota) VALUES (?,?,?,?,?)",
            (float(ts if ts is not None else time.time()), rodzaj, neuron, float(wartosc), nota),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def zapisz_pomiary(wiersze, db_path: Path | str = DEFAULT_DB, ts: float | None = None) -> int:
    """Batch: lista krotek (rodzaj, neuron, wartosc, nota). JEDNO połączenie SQLite
    (mniej I/O w pętli live — cubic P2). Pomija wiersze z pustym rodzaj/neuron. Zwraca ile zapisano."""
    wiersze = list(wiersze)
    if not wiersze:
        return 0
    conn = _polacz(db_path)
    try:
        t = float(ts if ts is not None else time.time())
        n = 0
        for rodzaj, neuron, wartosc, nota in wiersze:
            if not rodzaj or not neuron:
                continue
            conn.execute(
                "INSERT INTO pomiary (ts, rodzaj, neuron, wartosc, nota) VALUES (?,?,?,?,?)",
                (t, str(rodzaj), str(neuron), float(wartosc), nota or ""))
            n += 1
        conn.commit()
        return n
    finally:
        conn.close()


def pytaj_pomiary(rodzaj: str | None = None, neuron: str | None = None,
                  limit: int = 20, db_path: Path | str = DEFAULT_DB) -> list[dict]:
    """Zwraca pomiary (najnowsze wg CZASU pierwsze), z opcjonalnym filtrem rodzaj/neuron."""
    if limit < 1:
        return []
    if not Path(db_path).exists():
        return []
    conn = _polacz(db_path)
    try:
        warunki, param = [], []
        if rodzaj:
            warunki.append("rodzaj = ?"); param.append(rodzaj)
        if neuron:
            warunki.append("neuron = ?"); param.append(neuron)
        gdzie = (" WHERE " + " AND ".join(warunki)) if warunki else ""
        param.append(int(limit))
        # ORDER BY ts (czas zdarzenia), id jako tie-breaker — backfill nie udaje „najnowszego".
        rows = conn.execute(
            f"SELECT id, ts, rodzaj, neuron, wartosc, nota FROM pomiary{gdzie} "
            "ORDER BY ts DESC, id DESC LIMIT ?", param,
        ).fetchall()
        return [{"id": r[0], "ts": r[1], "rodzaj": r[2], "neuron": r[3],
                 "wartosc": r[4], "nota": r[5]} for r in rows]
    finally:
        conn.close()
