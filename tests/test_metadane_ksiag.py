"""
Testy katalogu metadanych książek (Bibliotheca Ulpia, calibre jako backend).

Dwa poziomy: parsowanie nazwy (fallback zawsze) + parser wyjścia `ebook-meta` (wzbogacenie).
Reguła Test-Granic: nazwa niestandardowa, „ : " w wartości, „Unknown", brak dopasowania.
"""

from narzedzia.rag import metadane_ksiag as mk


# ── Fallback: parsowanie nazwy pliku ─────────────────────────────────────────

def test_parsuj_nazwe_standardowa():
    w = mk.parsuj_nazwe("BIB-007_Lopez-de-Prado_Advances-in-Financial-Machine-Learning.epub")
    assert w["bib"] == "BIB-007"
    assert w["autor"] == "Lopez de Prado"
    assert w["tytul"] == "Advances in Financial Machine Learning"
    assert w["format"] == "epub"


def test_parsuj_nazwe_myslniki_w_autorze_i_tytule():
    """Myślniki → spacje w autorze i tytule; numer BIB zachowany."""
    w = mk.parsuj_nazwe("BIB-053_Antonopoulos-Harding_Mastering-Bitcoin-3rd-ed.mobi")
    assert w["autor"] == "Antonopoulos Harding"
    assert w["tytul"] == "Mastering Bitcoin 3rd ed"
    assert w["format"] == "mobi"


def test_parsuj_nazwe_niestandardowa_nie_wybucha():
    """Plik bez wzorca BIB-NNN_Autor_Tytul → komplet kluczy, tytuł z nazwy (stabilny kontrakt)."""
    w = mk.parsuj_nazwe("jakas-losowa-ksiazka.pdf")
    assert w["bib"] == "" and w["autor"] == ""
    assert w["tytul"] == "jakas losowa ksiazka" and w["format"] == "pdf"
    assert set(w) == {"bib", "autor", "tytul", "format", "plik"}


# ── Parser wyjścia ebook-meta (calibre) ──────────────────────────────────────

_PROBKA = """Title               : Advances in Financial Machine Learning
Author(s)           : Marcos Lopez de Prado
Publisher           : Wiley
Tags                : Finance, Machine Learning
Languages           : eng
Published           : 2018-02-21T00:00:00+00:00
Identifiers         : isbn:9781119482086
Series              : Unknown
Comments            : Some blurb : with a colon inside
Rating              : Unknown"""


def test_parser_ebook_meta_mapuje_klucze():
    m = mk.parsuj_wyjscie_ebook_meta(_PROBKA)
    assert m["tytul"] == "Advances in Financial Machine Learning"
    assert m["autor"] == "Marcos Lopez de Prado"
    assert m["wydawca"] == "Wiley"
    assert m["tagi"] == "Finance, Machine Learning"
    assert m["jezyk"] == "eng"


def test_parser_pomija_unknown():
    """'Series : Unknown' i 'Rating : Unknown' NIE mogą trafić do wyniku."""
    m = mk.parsuj_wyjscie_ebook_meta(_PROBKA)
    assert "seria" not in m


def test_parser_pomija_nieznany_djvu():
    """djvu bez metadanych: calibre zwraca Author='Nieznany' (locale PL) — NIE może
    nadpisać dobrego autora z nazwy pliku (Prawo XV: filtr autora łapie Shreve/Aronson)."""
    wy = ("Title               : BIB-022 Kissell Optimal-trading-strategies\n"
          "Author(s)           : Nieznany")
    m = mk.parsuj_wyjscie_ebook_meta(wy)
    assert "autor" not in m                    # 'Nieznany' odsiane
    assert m.get("tytul", "").startswith("BIB-")  # tytul-echo przechodzi parser...
    assert mk._tytul_echo_nazwy(m["tytul"])       # ...ale merge go odrzuci


def test_tytul_echo_nazwy_wykrywany():
    assert mk._tytul_echo_nazwy("BIB-022 Kissell Optimal-trading-strategies")
    assert mk._tytul_echo_nazwy("bib-7 cos")               # case-insensitive
    assert not mk._tytul_echo_nazwy("Advances in Financial Machine Learning")
    assert not mk._tytul_echo_nazwy("")


def test_parser_zachowuje_dwukropek_w_wartosci():
    """Wartość z ' : ' w środku — partition po PIERWSZYM separatorze, reszta zachowana.
    (Comments nie jest mapowany, więc sprawdzamy na Title z dopisanym dwukropkiem.)"""
    m = mk.parsuj_wyjscie_ebook_meta("Title               : Market Microstructure : Theory")
    assert m["tytul"] == "Market Microstructure : Theory"


def test_parser_ignoruje_nieznane_etykiety():
    assert mk.parsuj_wyjscie_ebook_meta("Coś tam bez separatora\nFoo : bar") == {}


def test_parser_pusty():
    assert mk.parsuj_wyjscie_ebook_meta("") == {}
