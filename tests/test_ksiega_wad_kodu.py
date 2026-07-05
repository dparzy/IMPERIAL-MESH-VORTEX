"""Testy KsiegaWadKodu (pamięć wzorców błędów + skaner) — z granicami."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from imperium.biblioteki.ksiega_wad_kodu import (
    WZORCE_STARTOWE,
    KsiegaWadKodu,
    zasiej_startowe,
)


def test_dodaj_i_skanuj(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert k.dodaj("odpornosc", r"eval\(", "użycie eval", "nie używaj eval")
    trafienia = k.skanuj("x = eval('2+2')\n")
    assert len(trafienia) == 1 and trafienia[0]["linia"] == 1


def test_dodaj_duplikat_regex_odrzucony(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert k.dodaj("a", r"foo", "o1", "l1") is True
    assert k.dodaj("a", r"foo", "o2", "l2") is False   # ten sam regex → nie dubluj
    assert len(k.wszystkie()) == 1


def test_dodaj_pusty_lub_zly_regex_rzuca(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    with pytest.raises(ValueError):
        k.dodaj("a", "", "opis", "lekcja")       # pusty regex
    with pytest.raises(ValueError):
        k.dodaj("a", r"(niezamkniety", "o", "l")  # błędny regex


def test_skanuj_brak_trafien(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    k.dodaj("a", r"eval\(", "o", "l")
    assert k.skanuj("czysty = kod()\n") == []


def test_skanuj_numer_linii(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    k.dodaj("a", r"BUG", "o", "l")
    assert k.skanuj("linia1\nlinia2\nBUG tutaj\n")[0]["linia"] == 3


def test_persystencja_zapis_odczyt(tmp_path):
    sciezka = tmp_path / "k.jsonl"
    k = KsiegaWadKodu(sciezka)
    k.dodaj("a", r"foo", "o", "l", "src")
    k.zapisz()
    k2 = KsiegaWadKodu(sciezka)           # świeże wczytanie
    assert len(k2.wszystkie()) == 1 and k2.wszystkie()[0]["zrodlo"] == "src"


def test_zasiej_startowe_idempotentne(tmp_path):
    sciezka = tmp_path / "k.jsonl"
    n1 = zasiej_startowe(sciezka)
    assert n1 == len(WZORCE_STARTOWE)
    n2 = zasiej_startowe(sciezka)          # drugi raz nic nie dodaje (dedup regex)
    assert n2 == 0


def test_wzorce_startowe_maja_poprawne_regexy():
    import re
    for w in WZORCE_STARTOWE:
        re.compile(w["regex"])             # nie rzuca = poprawny


def test_wzorzec_startowy_lapie_order_by_id(tmp_path):
    zasiej_startowe(tmp_path / "k.jsonl")
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert any(t["kat"] == "kontrakt" for t in k.skanuj('conn.execute("... ORDER BY id DESC LIMIT ?")'))
