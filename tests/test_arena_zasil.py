"""Testy zasilacza bazy areny (narzedzia/arena_zasil.py) — rdzeń bez backtestu."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.arena_zasil import zasil_z_ic
from narzedzia.arena_mcp import pytaj_pomiary


def test_zasil_zapisuje_wszystkie(tmp_path):
    db = tmp_path / "a.db"
    n = zasil_z_ic({"V-03": 0.041, "Z-01": -0.02}, "4h", db_path=db)
    assert n == 2
    rows = pytaj_pomiary(rodzaj="IC", db_path=db)
    assert {r["neuron"] for r in rows} == {"V-03", "Z-01"}


def test_zasil_pomija_nan(tmp_path):
    db = tmp_path / "a.db"
    nan = float("nan")
    n = zasil_z_ic({"A": 0.03, "B": nan}, "4h", db_path=db)
    assert n == 1   # NaN pominięty (Prawo I: tylko realny pomiar)
    assert [r["neuron"] for r in pytaj_pomiary(db_path=db)] == ["A"]


def test_zasil_pomija_niepoprawne_typy(tmp_path):
    db = tmp_path / "a.db"
    n = zasil_z_ic({"A": 0.03, "B": None, "C": "brak"}, "4h", db_path=db)
    assert n == 1


def test_zasil_pusty_slownik(tmp_path):
    db = tmp_path / "a.db"
    assert zasil_z_ic({}, "4h", db_path=db) == 0
    assert pytaj_pomiary(db_path=db) == []


def test_zasil_nota_zawiera_interwal(tmp_path):
    db = tmp_path / "a.db"
    zasil_z_ic({"A": 0.03}, "1d", nota_extra="wachta", db_path=db)
    r = pytaj_pomiary(db_path=db)[0]
    assert "1d" in r["nota"] and "wachta" in r["nota"]


def test_zasil_rodzaj_konfigurowalny(tmp_path):
    db = tmp_path / "a.db"
    zasil_z_ic({"A": 0.03}, "4h", db_path=db, rodzaj="WALK_FORWARD")
    assert pytaj_pomiary(rodzaj="WALK_FORWARD", db_path=db)
    assert pytaj_pomiary(rodzaj="IC", db_path=db) == []
