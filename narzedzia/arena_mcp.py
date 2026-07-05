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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Baza wyników areny — wspólna warstwa (Prawo XVI reuse); rdzeń SQL w imperium/biblioteki.
from imperium.biblioteki.arena_baza import (  # noqa: E402
    pytaj_pomiary,
    zapisz_pomiar,
)


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


# (baza wyników areny: zapisz_pomiar / pytaj_pomiary importowane z arena_baza wyżej)


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
        try:
            # Parsowanie pól WEWNĄTRZ try — malformed request wraca jako JSON-RPC error,
            # nie wywala procesu serwera (cubic P1).
            params = req.get("params") or {}
            name = params["name"]
            args = params.get("arguments") or {}
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
                limit = min(100, max(1, int(args.get("limit", 20))))   # clamp do kontraktu 1-100
                result = _fmt_pomiary(pytaj_pomiary(args.get("rodzaj"), args.get("neuron"), limit))
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
