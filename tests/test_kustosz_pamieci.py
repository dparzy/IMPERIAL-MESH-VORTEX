"""
Testy Kustosza Pamięci (W7 — nadrzędny organ, W-360 v7).

Weryfikuje:
  • census() widzi wszystkie warstwy,
  • zbuduj_katalog() — anti-blindness index z tematami,
  • kompresuj_zimne() — .md→.md.gz z poprawnym ratio, próg dni,
  • zimna warstwa WCIĄŻ przeszukiwalna (zero memory blindness),
  • szukaj() — routing nadrzędny,
  • granice: brak katalogu, świeże sesje pominięte.
"""

import os
import time
from pathlib import Path

from imperium.biblioteki import kustosz_pamieci as ku
from imperium.biblioteki import kronika_czatu as kc


def _sesja(d: Path, nazwa: str, tresc: str, wiek_dni: float = 0):
    p = d / nazwa
    p.write_text(tresc, encoding="utf-8")
    if wiek_dni:
        t = time.time() - wiek_dni * 86400
        os.utime(p, (t, t))
    return p


def test_census_ma_warstwy():
    c = ku.census()
    for k in ("srodowisko", "dziennik_wpisy", "kronika", "wizje", "katalog_istnieje"):
        assert k in c


def test_zbuduj_katalog_tematy(tmp_path):
    _sesja(tmp_path, "sesja_a.md", "## Cezar\nnumba wydajność wskaźniki backtest\n" * 10)
    kat = ku.zbuduj_katalog(kronika_dir=tmp_path, plik_katalogu=tmp_path / "kat.json")
    assert kat["n"] == 1
    assert any("numba" in t or "wydajność" in t or "backtest" in t for t in kat["tematy_globalne"])
    assert (tmp_path / "kat.json").exists()


def test_zbuduj_katalog_pusty(tmp_path):
    kat = ku.zbuduj_katalog(kronika_dir=tmp_path / "brak", plik_katalogu=tmp_path / "k.json")
    assert kat["n"] == 0


def test_kompresuj_zimne_ratio_i_usuwa_md(tmp_path):
    _sesja(tmp_path, "sesja_old.md", "## Cezar\npowtarzalna treść GARCH\n" * 80, wiek_dni=60)
    r = ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path)
    assert r["skompresowane"] == 1
    assert r["ratio"] > 1.0
    assert (tmp_path / "sesja_old.md.gz").exists()
    assert not (tmp_path / "sesja_old.md").exists()


def test_kompresuj_pomija_swieze(tmp_path):
    _sesja(tmp_path, "sesja_new.md", "## Cezar\nświeża\n", wiek_dni=1)
    r = ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path)
    assert r["skompresowane"] == 0 and r["pominiete"] == 1
    assert (tmp_path / "sesja_new.md").exists()       # świeża nietknięta


def test_zimna_warstwa_wciaz_przeszukiwalna(tmp_path):
    """ZERO memory blindness: skompresowana sesja nadal znajdowana przez szukaj()."""
    _sesja(tmp_path, "sesja_x.md", "## Cezar\ntajemnicze słowo kluczowe zonkulator\n", wiek_dni=90)
    ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path)
    assert (tmp_path / "sesja_x.md.gz").exists()
    wyniki = kc.szukaj("zonkulator", cel=tmp_path)
    assert wyniki, "Skompresowana sesja niewyszukiwalna = memory blindness (regresja)"
    assert wyniki[0]["sesja"] == "x"


def test_kompresuj_nie_dubluje(tmp_path):
    _sesja(tmp_path, "sesja_o.md", "## Cezar\ntreść\n" * 50, wiek_dni=60)
    ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path)
    r2 = ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path)   # drugi raz: nic nowego
    assert r2["skompresowane"] == 0


def test_id_sesji_obsluguje_gz(tmp_path):
    _sesja(tmp_path, "sesja_abc.md", "x", wiek_dni=60)
    ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path)
    from imperium.biblioteki.kronika_czatu import _id_sesji, _pliki_sesji
    pliki = _pliki_sesji(tmp_path)
    assert _id_sesji(pliki[0]) == "abc"


def test_raport_startowy_nie_wybucha():
    r = ku.raport_startowy()
    assert "Kustosz" in r
