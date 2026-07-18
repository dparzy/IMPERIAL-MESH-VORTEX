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
import re
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


def test_mapa_ma_13_warstw():
    """Konsolidacja: mapa() wymienia wszystkie 13 warstw pamięci."""
    m = ku.mapa()
    for klucz in ("W1", "W6", "W7", "W8", "W11", "W12", "W13"):
        assert klucz in m
    assert len(ku.WARSTWY) == 14   # W1..W13 + W3b


def test_mapa_warstwy_maja_komplet_pol():
    for w in ku.WARSTWY:
        assert len(w) == 4 and all(w)   # (klucz, nazwa, rola, typ) — nic pustego


def test_kompresuj_granica_dni_dokladnie(tmp_path):
    """Granica dni: st_mtime > prog (ściśle). Deterministyczny `teraz` (bez wyścigu z zegarem):
    wiek dokładnie 30 dni (mtime==prog) NIE kompresowany; 31 dni (mtime<prog) tak (Reguła Test-Granic)."""
    import os
    TERAZ = 2_000_000_000.0
    # Kod: `if mtime > prog: pomiń`. prog = teraz - 30d. Więc mtime==prog (dokładnie 30 dni)
    # → NIE > prog → KOMPRESOWANA; mtime>prog (29 dni, świeższa) → pominięta.
    p30 = _sesja(tmp_path, "sesja_30.md", "## Cezar\ntreść graniczna\n" * 40)
    p29 = _sesja(tmp_path, "sesja_29.md", "## Cezar\ntreść świeższa\n" * 40)
    os.utime(p30, (TERAZ - 30 * 86400, TERAZ - 30 * 86400))   # mtime == prog → kompres
    os.utime(p29, (TERAZ - 29 * 86400, TERAZ - 29 * 86400))   # mtime >  prog → pominięta
    ku.kompresuj_zimne(dni=30, kronika_dir=tmp_path, teraz=TERAZ)
    assert (tmp_path / "sesja_30.md.gz").exists()             # dokładnie 30 dni → skompresowana
    assert (tmp_path / "sesja_29.md").exists()                # 29 dni → NIE (świeższa niż próg)


def test_kompresuj_dni_ujemne_bezpieczne(tmp_path):
    """dni<0 nie kompresuje aktywnych sesji (walidacja)."""
    _sesja(tmp_path, "sesja_teraz.md", "## Cezar\nświeża\n", wiek_dni=0)
    r = ku.kompresuj_zimne(dni=-5, kronika_dir=tmp_path)
    assert r["skompresowane"] == 0
    assert (tmp_path / "sesja_teraz.md").exists()


def test_mapa_nie_zaszywa_liczby_ksiazek():
    """Liczba książek w W2 idzie z bazy RAG, nigdy ze stałej.

    Zmierzone 2026-07-17: „42 książek" było ZASZYTE w `WARSTWY` (i w trzech innych miejscach
    kodu) przy 79 realnych. Biblioteka rośnie — każda wpisana liczba musi się zestarzeć.
    """
    from imperium.biblioteki.srodowisko_pamieci import ksiazki_w_bazie
    rola_w2 = next(rola for klucz, _n, rola, _t in ku.WARSTWY if klucz == "W2")
    assert not re.search(r"\d", rola_w2), \
        f"W2 ma zaszytą liczbę w stałej WARSTWY: {rola_w2!r} — ma ją dokładać mapa() z bazy"
    n = ksiazki_w_bazie()
    if n:  # bez bazy RAG (świeży klon) mapa po prostu nie dokłada liczby
        assert f"{n} książek zaindeksowanych" in ku.mapa()


def test_mapa_liczy_warstwy_bez_organu():
    """W7 (Kustosz) to ORGAN, nie warstwa-dana — `len(WARSTWY)` przekłamałoby o jeden.

    Pierwsza wersja tej poprawki drukowała „14 warstw", bo liczyła W7 razem z warstwami.
    """
    naglowek = ku.mapa().splitlines()[0]
    oczekiwane = len([w for w in ku.WARSTWY if w[0] != "W7"])
    assert f"{oczekiwane} warstw" in naglowek, naglowek
    assert "organ W7" in naglowek, "nagłówek musi odróżniać organ od warstw"
