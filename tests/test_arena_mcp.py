"""Testy Arena MCP (narzedzia/arena_mcp.py) — migawka roju + baza wyników + JSON-RPC."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.arena_mcp import (
    _handle,
    neuron_szczegoly,
    pytaj_pomiary,
    snapshot_roj,
    zapisz_pomiar,
)


# ── migawka roju (z rejestru) ────────────────────────────────────────────────

def test_snapshot_roj_liczby_zgodne():
    s = snapshot_roj()
    assert s["neurony_lacznie"] == s["neurony_aktywne"] + s["neurony_wyciszone"]
    assert s["neurony_lacznie"] > 0 and s["zwiadowcy"] > 0
    assert isinstance(s["kategorie"], dict) and s["kategorie"]


def test_neuron_szczegoly_istnieje():
    s = snapshot_roj()  # rój żyje
    assert s  # sanity
    from imperium.legiony.rejestr import wszystkie_neurony
    klucz = wszystkie_neurony()[0].KLUCZ
    d = neuron_szczegoly(klucz)
    assert d and d["klucz"] == klucz and "kategoria" in d


def test_neuron_szczegoly_brak_zwraca_none():
    assert neuron_szczegoly("NIE-MA-TAKIEGO-999") is None


# ── baza wyników (SQLite) — granice ──────────────────────────────────────────

def test_zapisz_i_pytaj(tmp_path):
    db = tmp_path / "arena.db"
    zapisz_pomiar("IC", "V-03", 0.041, "BTC 4h", db_path=db)
    rows = pytaj_pomiary(db_path=db)
    assert len(rows) == 1 and rows[0]["neuron"] == "V-03" and abs(rows[0]["wartosc"] - 0.041) < 1e-9


def test_pytaj_pusta_baza_zwraca_liste(tmp_path):
    assert pytaj_pomiary(db_path=tmp_path / "nie_ma.db") == []


def test_pytaj_filtr_neuron_i_rodzaj(tmp_path):
    db = tmp_path / "a.db"
    zapisz_pomiar("IC", "V-03", 0.04, db_path=db)
    zapisz_pomiar("IC", "Z-01", -0.02, db_path=db)
    zapisz_pomiar("WALK_FORWARD", "V-03", 0.03, db_path=db)
    assert len(pytaj_pomiary(neuron="V-03", db_path=db)) == 2
    assert len(pytaj_pomiary(rodzaj="IC", db_path=db)) == 2
    assert len(pytaj_pomiary(rodzaj="IC", neuron="V-03", db_path=db)) == 1


def test_pytaj_limit_zero_zwraca_pusto(tmp_path):
    db = tmp_path / "a.db"
    zapisz_pomiar("IC", "V-03", 0.04, db_path=db)
    assert pytaj_pomiary(limit=0, db_path=db) == []
    assert pytaj_pomiary(limit=-5, db_path=db) == []


def test_pytaj_najnowsze_pierwsze(tmp_path):
    db = tmp_path / "a.db"
    zapisz_pomiar("IC", "A", 0.01, ts=100.0, db_path=db)
    zapisz_pomiar("IC", "B", 0.02, ts=200.0, db_path=db)
    rows = pytaj_pomiary(db_path=db)
    assert rows[0]["neuron"] == "B"   # najnowszy (wyższe id) pierwszy


def test_zapisz_pusty_rodzaj_lub_neuron_rzuca(tmp_path):
    db = tmp_path / "a.db"
    import pytest
    with pytest.raises(ValueError):
        zapisz_pomiar("", "V-03", 0.04, db_path=db)
    with pytest.raises(ValueError):
        zapisz_pomiar("IC", "", 0.04, db_path=db)


# ── JSON-RPC handler ─────────────────────────────────────────────────────────

def test_handle_tools_list():
    resp = _handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    nazwy = {t["name"] for t in resp["result"]["tools"]}
    assert nazwy == {"arena_roj", "arena_neuron", "arena_zapisz", "arena_pytaj"}


def test_handle_initialize():
    resp = _handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["result"]["serverInfo"]["name"] == "arena"


def test_handle_nieznana_metoda_zwraca_error():
    resp = _handle({"jsonrpc": "2.0", "id": 1, "method": "foo/bar"})
    assert resp["error"]["code"] == -32601


def test_handle_notifications_initialized_zwraca_none():
    assert _handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_handle_call_arena_roj():
    resp = _handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                    "params": {"name": "arena_roj", "arguments": {}}})
    assert "rój TERAZ" in resp["result"]["content"][0]["text"]


def test_handle_call_nieznane_narzedzie_error():
    resp = _handle({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                    "params": {"name": "nie_ma", "arguments": {}}})
    assert resp["error"]["code"] == -32603
