#!/usr/bin/env python3
"""
Bibliotheca-RAG MCP Server — wystawia narzedzie `biblioteka_szukaj` dla Claude Code.

Uruchomienie:
    python narzedzia/rag/mcp_server.py

Konfiguracja w .claude/settings.json (mcpServers):
    {
      "biblioteka": {
        "command": "python",
        "args": ["/path/to/narzedzia/rag/mcp_server.py"]
      }
    }

Dostepne narzedzia MCP:
    biblioteka_szukaj(zapytanie, topk=5, tryb="hybrid")
    biblioteka_info()
"""
from __future__ import annotations
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))
DEFAULT_BAZA = ROOT / "narzedzia" / "rag" / "baza_wiedzy.db"

# Leniwe ładowanie modelu (tylko gdy pytanie trafia do serwera)
_model_cache = None


def _get_model():
    global _model_cache
    if _model_cache is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model_cache = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        except ImportError:
            pass
    return _model_cache


def _szukaj(zapytanie: str, topk: int = 5, tryb: str = "hybrid", korpus: str | None = None,
            autor: str | None = None, tag: str | None = None) -> str:
    from szukaj import szukaj, formatuj  # type: ignore[import]
    wyniki = szukaj(zapytanie, topk, tryb, DEFAULT_BAZA, cichy=True,
                    korpus=korpus, autor=autor, tag=tag)
    return formatuj(wyniki, zapytanie)


def _info() -> str:
    if not DEFAULT_BAZA.exists():
        return "Baza nie istnieje. Uruchom: python narzedzia/rag/indeksuj.py"
    conn = sqlite3.connect(str(DEFAULT_BAZA))
    n_chunks = conn.execute("SELECT COUNT(*) FROM fragmenty").fetchone()[0]
    n_sources = conn.execute("SELECT COUNT(DISTINCT zrodlo) FROM fragmenty").fetchone()[0]
    n_vecs = conn.execute("SELECT COUNT(*) FROM wektory").fetchone()[0]
    # rozbicie per korpus (jesli kolumna istnieje)
    kolumny = {r[1] for r in conn.execute("PRAGMA table_info(fragmenty)").fetchall()}
    rozbicie = ""
    if "korpus" in kolumny:
        rows = conn.execute(
            "SELECT korpus, COUNT(*) FROM fragmenty GROUP BY korpus ORDER BY 2 DESC"
        ).fetchall()
        rozbicie = " | korpusy: " + ", ".join(f"{k}={n}" for k, n in rows)
    conn.close()
    return (
        f"Bibliotheca-RAG: {n_chunks} fragmentów z {n_sources} źródeł | "
        f"wektory: {'✅' if n_vecs > 0 else '❌ (tylko FTS)'}{rozbicie}"
    )


# ── MCP server (stdio transport, JSON-RPC 2.0) ──────────────────────────────

TOOLS = [
    {
        "name": "biblioteka_szukaj",
        "description": (
            "Przeszukuje Bibliothecę Ulpię — 69 książek o tradingu + encyklopedię Imperium. "
            "Zwraca najbliższe semantycznie fragmenty z podaniem źródła (BIB-xxx, tytuł, chunk) "
            "i metadanych z katalogu (autor, rok, tagi). Można filtrować po autorze/tagu. "
            "Użyj zamiast czytania całych plików epub/pdf."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "zapytanie": {"type": "string", "description": "Pytanie lub słowa kluczowe po polsku lub angielsku"},
                "topk": {"type": "integer", "default": 5, "description": "Liczba wyników (1-20)"},
                "tryb": {
                    "type": "string",
                    "enum": ["hybrid", "fts", "wektor"],
                    "default": "hybrid",
                    "description": "hybrid=FTS+semantic, fts=keyword only, wektor=semantic only",
                },
                "korpus": {
                    "type": "string",
                    "enum": ["biblioteka", "dane", "docs"],
                    "description": "Ogranicz do korpusu: biblioteka=książki+encyklopedia, dane=dane tematyczne, docs=dokumentacja Imperium. Domyślnie wszystkie.",
                },
                "autor": {"type": "string", "description": "Filtr: tylko książki tego autora (podciąg, np. 'Lopez de Prado'). Wg katalogu metadanych."},
                "tag": {"type": "string", "description": "Filtr: tylko książki z tym tagiem (podciąg, np. 'Machine Learning'). Wymaga metadanych calibre."},
            },
            "required": ["zapytanie"],
        },
    },
    {
        "name": "biblioteka_info",
        "description": "Zwraca statystyki bazy RAG (liczba fragmentów, źródeł, status wektorów).",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def _handle(req: dict) -> dict:
    method = req.get("method", "")
    rid = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "bibliotheca-rag", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        try:
            # Parsowanie WEWNĄTRZ try (Księga Wad): malformed request bez "params"/"name"
            # → JSON-RPC error, nie crash procesu serwera.
            name = req["params"]["name"]
            args = req["params"].get("arguments", {})
            if name == "biblioteka_szukaj":
                result = _szukaj(
                    args["zapytanie"],
                    int(args.get("topk", 5)),
                    args.get("tryb", "hybrid"),
                    args.get("korpus"),
                    args.get("autor"),
                    args.get("tag"),
                )
            elif name == "biblioteka_info":
                result = _info()
            else:
                raise ValueError(f"Nieznane narzędzie: {name}")
            return {
                "jsonrpc": "2.0",
                "id": rid,
                "result": {"content": [{"type": "text", "text": result}]},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": rid,
                "error": {"code": -32603, "message": str(e)},
            }

    if method == "notifications/initialized":
        return None  # type: ignore[return-value]

    return {
        "jsonrpc": "2.0",
        "id": rid,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


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
