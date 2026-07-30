#!/usr/bin/env python3
"""
Testy AESTIMATORA — przyrządu mierzącego wierność biblioteki cyfrowej.

DLACZEGO TE TESTY ISTNIEJĄ (pytanie Cezara 2026-07-29: „skąd wiesz, czy jest dobrze
skalibrowany i czy będzie wiarygodny?"): miernik, którego nikt nie zmierzył, jest
kolejną wiarą — tylko z ładniejszą tabelką. Nasza własna lekcja brzmi „kłamie
przyrząd, nie system", a AESTIMATOR ORZEKA O STRACIE, więc jego błąd nie jest
niedokładnością — jest fałszywym alarmem albo fałszywym spokojem.

Kalibracja odbyła się na PRAWDZIE PODSTAWOWEJ z ręki (8 losowych próbek podpisów
listingów odczytanych i ocenionych osobiście) i wykryła DWA realne błędy:

  1. Wzorzec listingu bezwzględny na wielkość liter liczył ZDANIA PROZY
     („Snippet 9.1 lists function clfHyperFit") jako obietnicę kodu.
     Skutek: zawyżona strata 259 zamiast 96 — czyli 2,7×.
  2. Detektor kodu zawierał gołe `return`, które w książkach finansowych znaczy
     „stopa zwrotu". Zmierzone 6,2% fałszywek na 600 oknach czystej prozy;
     po naprawie 1,5%, a i te okazały się realnym kodem w tekście.

Testy niżej PRZYPINAJĄ obie poprawki. Każdy używa tekstu o ZNANEJ z góry
zawartości, bo tylko wtedy „poprawny wynik" jest faktem, a nie opinią.
"""

from __future__ import annotations

import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
for p in (KORZEN, KORZEN / "narzedzia" / "rag"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import aestimator as A  # noqa: E402

# ── Prawda podstawowa: teksty, o których wiemy WSZYSTKO ────────────────────────

LISTING_Z_KODEM = (
    "SNIPPET 2.1 THE MARCENKO-PASTUR PDF\n"
    "import numpy as np,pandas as pd\n"
    "def mpPDF(var,q,pts):\n"
    "    eVal=np.linspace(0,1,pts)\n"
)
LISTING_BEZ_KODU = (
    "SNIPPET 18.1 PLUG-IN ENTROPY ESTIMATOR \n\n \n\n \n\n \n\n \n\n\n"
    "18.4 Lempel-Ziv Estimators \n\n"
    "Entropy can be interpreted as a measure of complexity.\n"
)
PROZA_O_LISTINGU = (
    "Snippet 9.1 lists function clfHyperFit, which implements a purged "
    "GridSearchCV. The argument fit_params can be used to pass sample_weight.\n"
)
PROZA_FINANSOWA = (
    "The expected return of the portfolio depends on the risk premium. "
    "Investors demand a higher return for bearing additional risk, and the "
    "realized return may differ from the expected return.\n"
)


def _wypelniacz(n_slow: int = 900) -> str:
    """Tekst wypełniający — przesuwa treść poza próg front matter (8%)."""
    return ("alpha beta gamma delta epsilon " * (n_slow // 5)) + "\n"


# ── 1. Wzorzec listingu: nagłówek TAK, wzmianka w prozie NIE ──────────────────

def test_naglowek_listingu_rozpoznany():
    assert A.RE_SNIPPET.search(LISTING_Z_KODEM), "nagłówek wersalikami musi być listingiem"


def test_proza_o_listingu_NIE_jest_listingiem():
    """Sedno błędu #1: zdanie odsyłające do listingu to nie obietnica kodu."""
    assert not A.RE_SNIPPET.search(PROZA_O_LISTINGU), (
        "wzmianka 'Snippet 9.1 lists function...' liczona jako listing ZAWYŻA stratę"
    )


def test_naglowek_bez_kodu_tez_jest_listingiem():
    """Listing pozbawiony treści MUSI być policzony — to właśnie jest strata."""
    assert A.RE_SNIPPET.search(LISTING_BEZ_KODU)


# ── 2. Detektor kodu: nie może brać prozy finansowej za Pythona ───────────────

def test_kod_wykryty_w_prawdziwym_listingu():
    assert A.RE_KOD.search(LISTING_Z_KODEM)


def test_slowo_return_w_prozie_finansowej_to_NIE_kod():
    """Sedno błędu #2: 'expected return' to stopa zwrotu, nie słowo kluczowe."""
    assert not A.RE_KOD.search(PROZA_FINANSOWA), (
        "'return' w prozie finansowej dawało 6,2% fałszywek — nie wolno go przywracać"
    )


def test_listing_bez_kodu_nie_ma_kodu():
    assert not A.RE_KOD.search(LISTING_BEZ_KODU)


# ── 3. Front matter nie może być liczony jako strata ──────────────────────────

def test_spis_tresci_odsiany():
    """Podpisy z początku pliku to spis treści — liczone jako strata zawyżałyby wynik."""
    tekst = LISTING_BEZ_KODU + _wypelniacz(4000)
    poz = A._po_front_matter(tekst, A.RE_SNIPPET)
    assert poz == [], "podpis w pierwszych 8% pliku to front matter, nie utracony listing"


def test_listing_poza_front_matter_policzony():
    tekst = _wypelniacz(4000) + LISTING_BEZ_KODU
    poz = A._po_front_matter(tekst, A.RE_SNIPPET)
    assert len(poz) == 1


# ── 4. Pomiar całej książki na znanej zawartości ──────────────────────────────

def test_zmierz_ksiazke_liczy_strate_kodu(tmp_path: Path):
    """Książka o ZNANEJ zawartości: 2 listingi, z tego 1 z kodem → strata 1."""
    tresc = _wypelniacz(4000) + LISTING_Z_KODEM + _wypelniacz(200) + LISTING_BEZ_KODU
    p = tmp_path / "BIB-999_Test_Kalibracja__deadbeef.txt"
    p.write_text(tresc, encoding="utf-8")

    w = A.zmierz_ksiazke(p)
    assert w["listingi_zapowiedziane"] == 2, w
    assert w["listingi_z_kodem"] == 1, w


def test_fragmentacja_jest_bezstratna_slownie(tmp_path: Path):
    """Cięcie nie może zgubić ANI JEDNEGO słowa — to osobna klasa straty niż struktura."""
    p = tmp_path / "BIB-998_Test_Bezstratnosc__cafe.txt"
    p.write_text(_wypelniacz(3000) + "unikalneslowokontrolne\n", encoding="utf-8")
    w = A.zmierz_ksiazke(p)
    assert w["slow_zgubionych_przy_cieciu"] == 0, "fragmentacja zgubiła słowa"


def test_strata_struktury_jest_RAPORTOWANA(tmp_path: Path):
    """Fragmentacja kasuje 100% linii — przyrząd MUSI to pokazać, nie przemilczeć."""
    p = tmp_path / "BIB-997_Test_Struktura__f00d.txt"
    p.write_text("wiersz jeden dwa trzy\n" * 400, encoding="utf-8")
    w = A.zmierz_ksiazke(p)
    assert w["linie_w_cache"] > 200
    assert w["linie_po_fragmentacji"] == 0, "gdyby to kiedyś było > 0, chunker naprawiono"


# ── 5. Werdykt: NIEZNANE/PUSTY to wynik, nie zero ─────────────────────────────

def test_pusta_ksiazka_to_werdykt_PUSTY(tmp_path: Path):
    p = tmp_path / "BIB-996_Test_Pusta__beef.txt"
    p.write_text("ledwie kilka slow tutaj\n", encoding="utf-8")
    w = A.zmierz_ksiazke(p)
    werd, powody = A.werdykt(w)
    assert werd == "PUSTY" and powody


def test_werdykt_nazywa_powod_a_nie_tylko_etykiete(tmp_path: Path):
    tresc = _wypelniacz(4000) + (LISTING_BEZ_KODU * 5)
    p = tmp_path / "BIB-995_Test_Uszkodzona__abcd.txt"
    p.write_text(tresc, encoding="utf-8")
    w = A.zmierz_ksiazke(p)
    werd, powody = A.werdykt(w)
    assert werd == "USZKODZONA"
    assert any("listingi" in x for x in powody), powody


def test_raport_pustego_korpusu_nie_wybucha():
    assert "brak książek" in A.raport({"zbadanych": 0, "ksiazki": []})
