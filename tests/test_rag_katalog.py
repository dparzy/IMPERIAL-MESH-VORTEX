"""
Testy wpięcia katalogu książek w RAG (wzbogacenie + filtr autor/tag).

Dwa poziomy: (1) czyste funkcje katalog.py, (2) integracja end-to-end — filtr `szukaj`
na syntetycznej bazie z fragmentami książek (realna baza ma dziś tylko docs).
"""

import json
import sqlite3
import tempfile
from pathlib import Path

from narzedzia.rag import katalog
from narzedzia.rag import szukaj as szuk


# ── Katalog: dane testowe ────────────────────────────────────────────────────

_KATALOG = {
    "n": 2,
    "calibre": True,
    "ksiegi": [
        {"bib": "BIB-007", "plik": "BIB-007_LdP_AFML.epub", "autor": "Marcos Lopez de Prado",
         "tytul": "Advances in Financial Machine Learning", "format": "epub",
         "tagi": "Finance, Machine Learning", "wydano": "2018-02-21T00:00:00+00:00"},
        {"bib": "BIB-015", "plik": "BIB-015_Elder_Trading.epub", "autor": "Alexander Elder",
         "tytul": "The New Trading for a Living", "format": "epub", "tagi": "Trading, Psychology"},
    ],
}


def _katalog_plik() -> Path:
    p = Path(tempfile.mkdtemp()) / "katalog_ksiag.json"
    p.write_text(json.dumps(_KATALOG, ensure_ascii=False), encoding="utf-8")
    return p


# ── Czyste funkcje katalog.py ────────────────────────────────────────────────

def test_wczytaj_katalog_mapuje_po_pliku():
    kat = katalog.wczytaj_katalog(_katalog_plik())
    assert set(kat) == {"BIB-007_LdP_AFML.epub", "BIB-015_Elder_Trading.epub"}
    assert kat["BIB-007_LdP_AFML.epub"]["autor"] == "Marcos Lopez de Prado"


def test_wczytaj_katalog_brak_pliku_graceful():
    assert katalog.wczytaj_katalog(Path("/nie/ma/takiego.json")) == {}


def test_wczytaj_katalog_uszkodzony_graceful():
    p = Path(tempfile.mkdtemp()) / "zly.json"
    p.write_text("{ to nie jest json", encoding="utf-8")
    assert katalog.wczytaj_katalog(p) == {}


def test_opis_metadanych_autor_rok_tagi():
    kat = katalog.wczytaj_katalog(_katalog_plik())
    opis = katalog.opis_metadanych("BIB-007_LdP_AFML.epub", kat)
    assert "Marcos Lopez de Prado" in opis and "2018" in opis and "Machine Learning" in opis


def test_opis_metadanych_zrodlo_spoza_katalogu_puste():
    kat = katalog.wczytaj_katalog(_katalog_plik())
    assert katalog.opis_metadanych("JAKIS_DOKUMENT.md", kat) == ""


def test_pasuje_filtr_brak_filtra_przepuszcza():
    kat = katalog.wczytaj_katalog(_katalog_plik())
    assert katalog.pasuje_filtr("BIB-007_LdP_AFML.epub", kat) is True
    assert katalog.pasuje_filtr("COKOLWIEK.md", kat) is True   # brak filtra → wszystko


def test_pasuje_filtr_autor_podciag_insensitive():
    kat = katalog.wczytaj_katalog(_katalog_plik())
    assert katalog.pasuje_filtr("BIB-007_LdP_AFML.epub", kat, autor="lopez")
    assert not katalog.pasuje_filtr("BIB-015_Elder_Trading.epub", kat, autor="lopez")


def test_pasuje_filtr_tag_podciag():
    kat = katalog.wczytaj_katalog(_katalog_plik())
    assert katalog.pasuje_filtr("BIB-015_Elder_Trading.epub", kat, tag="psychology")
    assert not katalog.pasuje_filtr("BIB-007_LdP_AFML.epub", kat, tag="psychology")


def test_pasuje_filtr_zrodlo_spoza_katalogu_odpada_przy_filtrze():
    """Dokument .md (spoza katalogu) przy AKTYWNYM filtrze książkowym → False."""
    kat = katalog.wczytaj_katalog(_katalog_plik())
    assert not katalog.pasuje_filtr("DOKUMENT.md", kat, autor="lopez")


# ── Integracja end-to-end: filtr w szukaj() na syntetycznej bazie ────────────

def _baza_z_ksiazkami() -> Path:
    """Minimalna baza RAG: 3 fragmenty (2 książki), fts5 external content, pusta wektory."""
    p = Path(tempfile.mkdtemp()) / "baza.db"
    conn = sqlite3.connect(str(p))
    conn.executescript(
        """
        CREATE TABLE fragmenty (
            id INTEGER PRIMARY KEY, zrodlo TEXT, tytul TEXT,
            korpus TEXT DEFAULT 'biblioteka', nr_chunk INT, tekst TEXT);
        CREATE VIRTUAL TABLE fts USING fts5(
            tekst, zrodlo UNINDEXED, tytul UNINDEXED,
            content='fragmenty', content_rowid='id');
        CREATE TABLE wektory (fragment_id INTEGER PRIMARY KEY, wektor BLOB);
        """
    )
    wiersze = [
        ("BIB-007_LdP_AFML.epub", "AFML", "biblioteka", 0, "meta labeling triple barrier purged cv"),
        ("BIB-007_LdP_AFML.epub", "AFML", "biblioteka", 1, "fractional differentiation stationarity memory"),
        ("BIB-015_Elder_Trading.epub", "Trading", "biblioteka", 0, "force index triple screen memory trading"),
    ]
    conn.executemany(
        "INSERT INTO fragmenty (zrodlo,tytul,korpus,nr_chunk,tekst) VALUES (?,?,?,?,?)", wiersze)
    conn.execute("INSERT INTO fts(fts) VALUES('rebuild')")   # populacja fts z external content
    conn.commit()
    conn.close()
    return p


def test_szukaj_bez_filtra_zwraca_obie_ksiazki():
    baza = _baza_z_ksiazkami()
    wyniki = szuk.szukaj("memory", topk=5, tryb="fts", baza=baza, cichy=True)
    zrodla = {w.zrodlo for w in wyniki}
    assert "BIB-007_LdP_AFML.epub" in zrodla and "BIB-015_Elder_Trading.epub" in zrodla


def test_szukaj_filtr_autor_ogranicza_do_ksiazki(monkeypatch=None):
    baza = _baza_z_ksiazkami()
    stara = katalog.KATALOG_PLIK
    katalog.KATALOG_PLIK = _katalog_plik()   # podmiana ścieżki (wczytaj_katalog rozwiązuje w locie)
    try:
        wyniki = szuk.szukaj("memory", topk=5, tryb="fts", baza=baza, cichy=True, autor="Elder")
    finally:
        katalog.KATALOG_PLIK = stara
    assert wyniki and all(w.zrodlo == "BIB-015_Elder_Trading.epub" for w in wyniki)


def test_szukaj_filtr_tag_ogranicza():
    baza = _baza_z_ksiazkami()
    stara = katalog.KATALOG_PLIK
    katalog.KATALOG_PLIK = _katalog_plik()
    try:
        wyniki = szuk.szukaj("memory", topk=5, tryb="fts", baza=baza, cichy=True, tag="Machine Learning")
    finally:
        katalog.KATALOG_PLIK = stara
    assert wyniki and all(w.zrodlo == "BIB-007_LdP_AFML.epub" for w in wyniki)
