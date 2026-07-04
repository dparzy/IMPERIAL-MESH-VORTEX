#!/usr/bin/env python3
"""
Arena MCP Server — wystawia stan i wyniki ROJU dla Claude Code (nauka areny na żywo).

Filozofia (Prawo XVI reuse, XXV przewaga): rój UCZY SIĘ w kodzie (MWU/synapsy/igrzyska).
Ten serwer to SOCZEWKA — pozwala Claude pytać o arenę bez czytania całych plików:
  • migawka roju TERAZ (rejestr — instant, bez backtestu),
  • szczegóły pojedynczego neuronu,
  • baza SQLite wyników areny: Claude ZAPISUJE pomiary (np. IC z lokalnego biegu)
    i PYTA o nie później — akumulacja wiedzy o skuteczności przez całą wachtę.

Zero zewnętrznych zależności (stdlib: json, sqlite3). Zgodny z JSON-RPC 2.0 (stdio),
ten sam wzorzec co narzedzia/rag/mcp_server.py.

Uruchomienie:
    python narzedzia/arena_mcp.py

Konfiguracja w .claude/settings.json (mcpServers):
    {
      "arena": { "command": "python", "args": ["/abs/path/narzedzia/arena_mcp.py"] }
    }

Dostepne narzedzia MCP:
    arena_roj()                          — migawka roju: liczby, kategorie, elita, wyciszone
    arena_neuron(klucz)                  — szczegóły neuronu (kategoria/waga/elita/dostępność)
    arena_zapisz(rodzaj, neuron, wartosc, nota="")  — zapisz pomiar do bazy areny
    arena_pytaj(rodzaj=None, neuron=None, limit=20)  — przeszukaj zapisane pomiary
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Baza wyników areny — lokalna, runtime (per-maszyna), gitignore jak baza_wiedzy.db.
DEFAULT_DB = ROOT / "bibliotheca_ulpia" / "dane" / "arena_wyniki.db"


# ── Rdzeń: migawka roju (czyste funkcje, testowalne bez MCP) ─────────────────

def snapshot_roj() -> dict:
    """Instant stan roju z rejestru (bez backtestu). Źródło prawdy = kod (Prawo I)."""
    from imperium.legiony.rejestr import (
        raport_elity,
        raport_potencjalu,
        wszystkie_neurony,
    )
    neurony = wszystkie_neurony()
    pot = raport_potencjalu()
    elita = raport_elity()
    kategorie: dict = {}
    for n in neurony:
        kategorie[n.KATEGORIA] = kategorie.get(n.KATEGORIA, 0) + 1
    return {
        "neurony_lacznie": pot["neurony_lacznie"],
        "neurony_aktywne": pot["neurony_aktywne"],
        "neurony_wyciszone": pot["neurony_wyciszone"],
        "zwiadowcy": pot["zwiadowcy_exp"],
        "zwiadowcy_aktywni": pot["zwiadowcy_aktywni"],
        "elita": elita["lacznie_elite"],
        "wykorzystanie_pct": pot["wykorzystanie_pct"],
        "kategorie": dict(sorted(kategorie.items())),
    }


def neuron_szczegoly(klucz: str) -> dict | None:
    """Szczegóły jednego neuronu po KLUCZU (None gdy nie ma takiego)."""
    from imperium.legiony.rejestr import wszystkie_neurony
    for n in wszystkie_neurony():
        if n.KLUCZ == klucz:
            return {
                "klucz": n.KLUCZ,
                "wskaznik": n.WSKAZNIK,
                "kategoria": n.KATEGORIA,
                "waga": n.WAGA,
                "dostepny": bool(n.DOSTEPNY),
                "elitarny": bool(n.ELITARNY),
                "powod_elitarnosci": getattr(n, "POWOD_ELITARNOSCI", "") or "",
            }
    return None


# ── Rdzeń: baza wyników areny (SQLite) ───────────────────────────────────────

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
    """Zapisuje jeden pomiar areny (np. IC neuronu). Zwraca id wiersza."""
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


def pytaj_pomiary(rodzaj: str | None = None, neuron: str | None = None,
                  limit: int = 20, db_path: Path | str = DEFAULT_DB) -> list[dict]:
    """Zwraca zapisane pomiary (najnowsze pierwsze), z opcjonalnym filtrem."""
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
        rows = conn.execute(
            f"SELECT id, ts, rodzaj, neuron, wartosc, nota FROM pomiary{gdzie} "
            "ORDER BY id DESC LIMIT ?", param,
        ).fetchall()
        return [{"id": r[0], "ts": r[1], "rodzaj": r[2], "neuron": r[3],
                 "wartosc": r[4], "nota": r[5]} for r in rows]
    finally:
        conn.close()


# ── Formatowanie tekstu dla Claude ───────────────────────────────────────────

def _fmt_roj(s: dict) -> str:
    kat = " ".join(f"{k}:{v}" for k, v in s["kategorie"].items())
    return (f"🏟️ ARENA — rój TERAZ:\n"
            f"   Neurony: {s['neurony_lacznie']} (aktywne {s['neurony_aktywne']}, "
            f"wyciszone {s['neurony_wyciszone']}) | wykorzystanie {s['wykorzystanie_pct']}%\n"
            f"   Zwiadowcy: {s['zwiadowcy']} (aktywni {s['zwiadowcy_aktywni']}) | "
            f"Elita: {s['elita']}\n   Kategorie: {kat}")


def _fmt_pomiary(rows: list[dict]) -> str:
    if not rows:
        return "🏟️ ARENA — brak zapisanych pomiarów dla tego filtra."
    linie = [f"🏟️ ARENA — {len(rows)} pomiarów (najnowsze pierwsze):"]
    for r in rows:
        nota = f"  ({r['nota']})" if r["nota"] else ""
        linie.append(f"   {r['rodzaj']:<12} {r['neuron']:<12} {r['wartosc']:>+8.4f}{nota}")
    return "\n".join(linie)


# ── MCP server (stdio, JSON-RPC 2.0) ─────────────────────────────────────────

TOOLS = [
    {
        "name": "arena_roj",
        "description": ("Migawka roju TERAZ (z rejestru, instant): liczba neuronów aktywnych/"
                        "wyciszonych, zwiadowcy, elita, wykorzystanie %, rozkład kategorii."),
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "arena_neuron",
        "description": "Szczegóły jednego neuronu po KLUCZU (kategoria, waga, dostępność, status elitarny).",
        "inputSchema": {
            "type": "object",
            "properties": {"klucz": {"type": "string", "description": "KLUCZ neuronu, np. 'NEWS-01'"}},
            "required": ["klucz"],
        },
    },
    {
        "name": "arena_zapisz",
        "description": ("Zapisz pomiar skuteczności do bazy areny (akumulacja wiedzy przez wachtę). "
                        "Np. rodzaj='IC', neuron='V-03', wartosc=0.041."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "rodzaj": {"type": "string", "description": "Typ pomiaru: IC / WALK_FORWARD / SCOREBOARD..."},
                "neuron": {"type": "string", "description": "KLUCZ neuronu lub 'ROJ'"},
                "wartosc": {"type": "number", "description": "Zmierzona wartość"},
                "nota": {"type": "string", "default": "", "description": "Kontekst (para, interwał, okno)"},
            },
            "required": ["rodzaj", "neuron", "wartosc"],
        },
    },
    {
        "name": "arena_pytaj",
        "description": "Przeszukaj zapisane pomiary areny (najnowsze pierwsze), filtr po rodzaju/neuronie.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "rodzaj": {"type": "string", "description": "Filtr typu pomiaru (opcjonalny)"},
                "neuron": {"type": "string", "description": "Filtr neuronu (opcjonalny)"},
                "limit": {"type": "integer", "default": 20, "description": "Ile wyników (1-100)"},
            },
        },
    },
]


def _handle(req: dict) -> dict | None:
    method = req.get("method", "")
    rid = req.get("id")

    if method == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "arena", "version": "1.0.0"}}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = req["params"]["name"]
        args = req["params"].get("arguments", {})
        try:
            if name == "arena_roj":
                result = _fmt_roj(snapshot_roj())
            elif name == "arena_neuron":
                d = neuron_szczegoly(args["klucz"])
                result = json.dumps(d, ensure_ascii=False) if d else f"Brak neuronu o kluczu '{args['klucz']}'."
            elif name == "arena_zapisz":
                new_id = zapisz_pomiar(args["rodzaj"], args["neuron"], float(args["wartosc"]),
                                       args.get("nota", ""))
                result = f"✅ Zapisano pomiar #{new_id}: {args['rodzaj']} {args['neuron']} = {args['wartosc']:+.4f}"
            elif name == "arena_pytaj":
                result = _fmt_pomiary(pytaj_pomiary(args.get("rodzaj"), args.get("neuron"),
                                                    int(args.get("limit", 20))))
            else:
                raise ValueError(f"Nieznane narzędzie: {name}")
            return {"jsonrpc": "2.0", "id": rid,
                    "result": {"content": [{"type": "text", "text": result}]}}
        except Exception as e:  # noqa: BLE001 — błąd narzędzia wraca jako JSON-RPC error
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32603, "message": str(e)}}

    if method == "notifications/initialized":
        return None

    return {"jsonrpc": "2.0", "id": rid,
            "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle(req)
        if resp is not None:
            print(json.dumps(resp, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
