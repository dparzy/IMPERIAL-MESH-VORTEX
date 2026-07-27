"""Testy INDEX FALSORUM — Spis Twierdzeń Obalonych (organ z 2026-07-20, NOTA N-7d2c4847).

Reguła Test-Granic: detektor, który nic nie wykrywa, jest gorszy niż jego brak — daje
FAŁSZYWY SPOKÓJ. Dlatego testujemy OBIE strony: że łapie głoszone kłamstwo I że nie
krzyczy na sprostowanie (klasa FP z Księgi Wad #35).
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.index_falsorum import (  # noqa: E402
    dodaj, przeszukaj, wczytaj, aktywne, wycofaj, _linia_prostuje, _okno_prostuje,
    _negacja_przy,
)

WPIS = [{"fraza": r"O\(n[²^]?2?\)", "poprawna_teza": "Backtest jest LINIOWY",
         "obalone_przez": "pomiar 2026-07-19", "data": "2026-07-20", "zrodlo": "test"}]


def _korpus(tresc: str, nazwa: str = "zywy.md") -> Path:
    """Tworzy tymczasowy korzeń korpusu z jednym plikiem."""
    kat = Path(tempfile.mkdtemp())
    (kat / nazwa).write_text(tresc, encoding="utf-8")
    return kat


def test_wykrywa_glosone_twierdzenie():
    """DOWÓD ŻE NIE JEST ŚLEPY: obalone twierdzenie głoszone jako fakt → trafienie."""
    kat = _korpus("Uwaga: backtest jest O(n²), wiec ograniczaj okno.\n")
    traf = przeszukaj(korzen=kat, wpisy=WPIS)
    assert len(traf) == 1, f"musi zlapac glosone klamstwo, zlapal: {traf}"
    assert traf[0]["linia_nr"] == 1
    assert traf[0]["poprawna_teza"] == "Backtest jest LINIOWY"


def test_negacja_w_tej_samej_linii_nie_jest_trafieniem():
    """Zdanie prostujące zawiera frazę, ale ją obala — nie wolno go zgłaszać."""
    kat = _korpus("Backtest jest LINIOWY, nie O(n²) — zmierzone.\n")
    assert przeszukaj(korzen=kat, wpisy=WPIS) == []


def test_korekta_przez_granice_linii_nie_jest_trafieniem():
    """REGRESJA 2026-07-20: scriba_codex.py:135 'sugestia O(n^2) zostala' / :136 'obalona
    pomiarem' — detektor jednoliniowy zglaszal SPROSTOWANIE jako klamstwo (FP #35)."""
    kat = _korpus('Sugestia "Naprawa backtestu O(n^2)" zostala\n'
                  "obalona pomiarem (backtest jest LINIOWY).\n")
    assert przeszukaj(korzen=kat, wpisy=WPIS) == [], "korekta zawijana przez linie to NIE klamstwo"


def test_okno_kontekstu_dziala_w_obie_strony():
    """Granica: marker korekty PRZED frazą i PO frazie — obie strony okna."""
    przed = ["korekta ponizej:", "backtest O(n²)"]
    po = ["backtest O(n²)", "to twierdzenie obalono"]
    assert _okno_prostuje(przed, 1), "marker PRZED fraza musi wyciszac"
    assert _okno_prostuje(po, 0), "marker PO frazie musi wyciszac"
    assert not _okno_prostuje(["backtest O(n²)"], 0), "sama fraza bez markera = trafienie"


def test_marker_poza_oknem_nie_wycisza():
    """Granica dokładna: marker dalej niż ±2 linie NIE wycisza (inaczej detektor oślepnie)."""
    linie = ["backtest O(n²)", "a", "b", "c", "to obalono"]
    assert not _okno_prostuje(linie, 0), "marker 4 linie dalej nie dotyczy tej frazy"


def test_historia_i_archiwum_pominiete():
    """Prawo I: LOG_ZMIAN to datowana prawda swojego czasu — nie falsyfikujemy historii."""
    kat = _korpus("backtest jest O(n²)\n", nazwa="LOG_ZMIAN.md")
    assert przeszukaj(korzen=kat, wpisy=WPIS) == []
    kat2 = Path(tempfile.mkdtemp())
    (kat2 / "archiwum").mkdir()
    (kat2 / "archiwum" / "stare.md").write_text("backtest jest O(n²)\n", encoding="utf-8")
    assert przeszukaj(korzen=kat2, wpisy=WPIS) == []


def test_dodaj_wymaga_dowodu():
    """KANDYDAT ≠ PRAWDA: bez `obalone_przez` organ stałby się cenzurą poglądów."""
    plik = Path(tempfile.mkdtemp()) / "l.jsonl"
    try:
        dodaj(fraza="cokolwiek", poprawna_teza="x", obalone_przez="", sciezka=plik)
        assert False, "brak dowodu MUSI byc odrzucony"
    except ValueError as e:
        assert "obalone_przez" in str(e)


def test_dodaj_odrzuca_bledny_regex():
    """Granica: niepoprawne wyrażenie regularne → głośny błąd, nie cichy brak skanu."""
    plik = Path(tempfile.mkdtemp()) / "l.jsonl"
    try:
        dodaj(fraza="O(n[", poprawna_teza="x", obalone_przez="pomiar", sciezka=plik)
        assert False, "bledny regex MUSI byc odrzucony"
    except ValueError as e:
        assert "regularn" in str(e)


def test_idempotencja_po_frazie():
    """Ta sama fraza drugi raz nie dubluje wpisu (spis to zbiór, nie szereg czasowy)."""
    plik = Path(tempfile.mkdtemp()) / "l.jsonl"
    assert dodaj(fraza=r"X\(n\)", poprawna_teza="a", obalone_przez="pomiar", sciezka=plik) is True
    assert dodaj(fraza=r"X\(n\)", poprawna_teza="a", obalone_przez="pomiar", sciezka=plik) is False
    assert len(wczytaj(plik)) == 1


def test_pusty_spis_nie_skanuje():
    """Brak zarejestrowanych twierdzeń → sweep zwraca [] bez czytania korpusu."""
    assert przeszukaj(korzen=Path(tempfile.mkdtemp()), wpisy=[]) == []


def test_marker_korekty_rozpoznawany():
    """Granica słownika markerów JAWNEJ korekty (mówią wprost: było błędne)."""
    assert _linia_prostuje("premisa byla bledna")
    assert _linia_prostuje("twierdzenie obalone pomiarem")
    assert not _linia_prostuje("backtest jest O(n²) i koniec")
    # Sama negacja NIE jest jawną korektą — o niej decyduje bliskość frazy.
    assert not _linia_prostuje("to jest LINIOWE, nie kwadratowe")


# ── Pułapki zmierzone 2026-07-20 przy pierwszym sweepie (regresje) ─────────────────

def test_negacja_musi_dotyczyc_frazy_nie_calej_linii():
    """REGRESJA: 'przez API, nie lokalnie (Fujitsu, 8GB RAM)' — negacja dotyczy LOKALNOŚCI,
    nie liczby RAM. Szeroki marker wyciszał to zdanie i obalona liczba przeżyła w ROADMAP:69."""
    linia = "Obliczenia ciezkie: przez API, nie lokalnie (Fujitsu, 8GB RAM)"
    start = linia.index("Fujitsu")
    assert not _negacja_przy(linia, start, "Fujitsu, 8GB"), \
        "negacja odlegla i dotyczaca czego innego NIE moze wyciszac frazy"


def test_negacja_wewnatrz_dopasowania_wycisza():
    """Wzorzec kodujący twierdzenie bywa rozciągnięty, a negacja siedzi w środku:
    'backtest LINIOWY, nie O(n²)' to sprostowanie, nie kłamstwo."""
    linia = "# naprawa HMA (backtest LINIOWY, nie O(n²))"
    start = linia.index("backtest")
    assert _negacja_przy(linia, start, "backtest LINIOWY, nie O(n²)")


def test_nie_wewnatrz_slowa_nie_jest_negacja():
    """PUŁAPKA: podciąg 'nie ' trafia w środek słowa 'lokalNIE (' — stąd wymóg granic słów."""
    assert not _negacja_przy("dziala lokalnie (Fujitsu, 8GB RAM)", 20, "Fujitsu, 8GB")


def test_wycofanie_zdejmuje_fraze_ze_strazy():
    """Źle dobrana fraza musi dać się wycofać — inaczej zostaje wiecznym FP (Księga Wad #35)."""
    plik = Path(tempfile.mkdtemp()) / "l.jsonl"
    dodaj(fraza=r"ZLA\(fraza\)", poprawna_teza="x", obalone_przez="pomiar", sciezka=plik)
    assert len(aktywne(plik)) == 1
    assert wycofaj(fraza=r"ZLA\(fraza\)", powod="za szeroka — trafiala w cudzy kod", sciezka=plik)
    assert aktywne(plik) == [], "wycofana fraza nie moze dalej pilnowac korpusu"
    assert len(wczytaj(plik)) == 2, "historia zostaje (Prawo I) — nagrobek, nie kasowanie"


def test_wycofanie_wymaga_powodu_i_istniejacej_frazy():
    """Granica: nie wycofujemy bez powodu ani czegoś, czego w spisie nie ma."""
    plik = Path(tempfile.mkdtemp()) / "l.jsonl"
    dodaj(fraza="jest", poprawna_teza="x", obalone_przez="pomiar", sciezka=plik)
    for kwargs, oczekiwane in (({"fraza": "jest", "powod": ""}, "powod"),
                               ({"fraza": "nie ma", "powod": "bo tak"}, "brak frazy")):
        try:
            wycofaj(sciezka=plik, **kwargs)
            assert False, f"musi odrzucic: {kwargs}"
        except ValueError as e:
            assert oczekiwane in str(e)


# ── PONOWNA REJESTRACJA PO WYCOFANIU (naprawa 2026-07-27) ────────────────────

def test_fraza_wraca_pod_straz_po_wycofaniu(tmp_path):
    """Wycofaną frazę MUSI dać się zarejestrować ponownie — inaczej poprawianie wpisu
    (wycofaj → dodaj lepszą treść) cicho GUBI twierdzenie.

    Zmierzone na żywym organie 2026-07-27: dedup szedł wobec CAŁEGO ledgera (append-only,
    więc wycofany rekord zostaje w pliku na zawsze), przez co `dodaj` zwracało False —
    co czyta się jak nieszkodliwe „już jest" — a INDEX spadł z 7 pozycji na 6 i zameldował
    „korpus czysty", choć właśnie przestał pilnować obalonej tezy.
    """
    from imperium.biblioteki.index_falsorum import aktywne, dodaj, wycofaj
    p = tmp_path / "falsa.jsonl"
    assert dodaj(fraza="teza X", poprawna_teza="stara", obalone_przez="pomiar", sciezka=p)
    assert dodaj(fraza="teza X", poprawna_teza="druga", obalone_przez="pomiar",
                 sciezka=p) is False, "duplikat AKTYWNEJ frazy nadal musi być odrzucany"
    assert wycofaj(fraza="teza X", powod="zastąpione lepszą treścią", sciezka=p)
    assert [r["fraza"] for r in aktywne(p)] == []
    assert dodaj(fraza="teza X", poprawna_teza="nowa, mocniejsza", obalone_przez="replikacja",
                 sciezka=p) is True, "po wycofaniu fraza musi móc wrócić pod straż"
    wroc = aktywne(p)
    assert len(wroc) == 1 and wroc[0]["poprawna_teza"] == "nowa, mocniejsza"
