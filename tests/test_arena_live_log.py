"""Testy wspólnej warstwy areny + kontrakt opt-in auto-logu w pętli live."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.arena_baza import pytaj_pomiary, zapisz_pomiar


def test_baza_zapis_i_odczyt(tmp_path):
    db = tmp_path / "a.db"
    zapisz_pomiar("LIVE_PNL", "BTCUSDT", 1.5, "4h NORMAL bar3", db_path=db)
    r = pytaj_pomiary(rodzaj="LIVE_PNL", db_path=db)
    assert len(r) == 1 and r[0]["neuron"] == "BTCUSDT" and abs(r[0]["wartosc"] - 1.5) < 1e-9


def test_baza_puste_rodzaj_neuron_rzuca(tmp_path):
    db = tmp_path / "a.db"
    import pytest
    with pytest.raises(ValueError):
        zapisz_pomiar("", "BTC", 1.0, db_path=db)


def test_mcp_reeksportuje_te_same_funkcje():
    """arena_mcp musi wystawiać te same funkcje bazy (wspólna warstwa, Prawo XVI)."""
    from imperium.biblioteki.arena_baza import zapisz_pomiar as bazowy
    from narzedzia.arena_mcp import zapisz_pomiar as mcp
    assert mcp is bazowy   # ten sam obiekt — nie duplikat


def test_konfig_arena_log_domyslnie_off():
    """Opt-in: arena_log domyślnie False = zero zmiany zachowania pętli live."""
    from imperium.koloseum.petla_live import KonfigPetliLive
    cfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert cfg.arena_log is False


def test_batch_zapisuje_wiele_jednym_polaczeniem(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiary
    db = tmp_path / "a.db"
    n = zapisz_pomiary([("LIVE_PNL", "BTCUSDT", 1.0, "x"),
                        ("LIVE_PNL", "ETHUSDT", -0.5, "y")], db_path=db)
    assert n == 2 and len(pytaj_pomiary(db_path=db)) == 2


def test_batch_pomija_puste_klucze(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiary
    db = tmp_path / "a.db"
    n = zapisz_pomiary([("LIVE_PNL", "", 1.0, ""), ("", "BTC", 1.0, ""),
                        ("LIVE_PNL", "BTC", 2.0, "")], db_path=db)
    assert n == 1   # dwa wiersze z pustym rodzaj/neuron pominięte


def test_batch_pusta_lista_zero(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiary
    assert zapisz_pomiary([], db_path=tmp_path / "a.db") == 0


def test_sortowanie_po_ts_nie_id(tmp_path):
    """Backfill (starszy ts wstawiony później) NIE udaje najnowszego — ORDER BY ts."""
    db = tmp_path / "a.db"
    zapisz_pomiar("IC", "NOWY", 0.1, ts=1000.0, db_path=db)      # id=1, ts nowszy
    zapisz_pomiar("IC", "BACKFILL", 0.2, ts=100.0, db_path=db)   # id=2, ts starszy
    rows = pytaj_pomiary(db_path=db)
    assert rows[0]["neuron"] == "NOWY"   # najnowszy wg CZASU, mimo niższego id


def test_wynik_zamkniecia_ma_rezim():
    """WynikZamkniecia niesie reżim (cubic P2 — arena-log przestaje kłamać 'NORMAL')."""
    from imperium.koloseum.paper_trading import WynikZamkniecia
    import dataclasses
    pola = {f.name for f in dataclasses.fields(WynikZamkniecia)}
    assert "rezim" in pola
