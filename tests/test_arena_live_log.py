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
