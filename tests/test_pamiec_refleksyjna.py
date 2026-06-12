"""Testy pamięci refleksyjnej Brain (W-295)."""
import os
import tempfile

from imperium.cesarz.pamiec_refleksyjna import (
    PamiecRefleksyjna,
    Lekcja,
    _generuj_auto,
)


def _tmp_pamiec():
    """Tworzy PamiecRefleksyjna w tymczasowym pliku."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    os.unlink(path)  # usuń pusty plik — PamiecRefleksyjna sama go stworzy
    return PamiecRefleksyjna(plik=path), path


def _cleanup(path):
    if os.path.exists(path):
        os.unlink(path)


# ── zapis i odczyt ─────────────────────────────────────────────────────────

def test_zapisz_wynik_tworzy_plik():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([10.0, 20.0, -5.0], rezim="TRENDING", interwal="1D")
        assert os.path.exists(p.plik)
    finally:
        _cleanup(path)


def test_wczytaj_zwraca_lekcje():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([10.0, 20.0, -5.0])
        lekcje = p.wczytaj_wszystkie()
        assert len(lekcje) == 1
        assert isinstance(lekcje[0], Lekcja)
    finally:
        _cleanup(path)


def test_wiele_wpisow():
    p, path = _tmp_pamiec()
    try:
        for i in range(5):
            p.zapisz_wynik([float(i)] * 10)
        assert len(p.wczytaj_wszystkie()) == 5
    finally:
        _cleanup(path)


def test_wczytaj_pusty_plik_zwraca_liste():
    p, path = _tmp_pamiec()
    try:
        assert p.wczytaj_wszystkie() == []
    finally:
        _cleanup(path)


# ── pola lekcji ──────────────────────────────────────────────────────────────

def test_pola_lekcji_poprawne():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([10.0, -2.0], rezim="RANGING", interwal="4H")
        l = p.wczytaj_wszystkie()[0]
        assert l.rezim == "RANGING"
        assert l.interwal == "4H"
        assert l.n_transakcji == 2
        assert l.wynik == "ZYSK"
        assert 0.0 <= l.win_rate <= 1.0
    finally:
        _cleanup(path)


def test_strata_wykryta():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([-10.0, -5.0])
        l = p.wczytaj_wszystkie()[0]
        assert l.wynik == "STRATA"
        assert l.pnl_usdt < 0
    finally:
        _cleanup(path)


def test_kontekst_zachowany():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([5.0], kontekst={"radar": "BULLISH", "lewar": 2})
        l = p.wczytaj_wszystkie()[0]
        assert l.kontekst["radar"] == "BULLISH"
    finally:
        _cleanup(path)


def test_lekcja_tekst_custom():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([1.0], lekcja_tekst="Moja lekcja")
        l = p.wczytaj_wszystkie()[0]
        assert l.lekcja_tekst == "Moja lekcja"
    finally:
        _cleanup(path)


# ── filtrowanie ───────────────────────────────────────────────────────────────

def test_pobierz_n_ostatnich():
    p, path = _tmp_pamiec()
    try:
        for _ in range(10):
            p.zapisz_wynik([1.0])
        assert len(p.pobierz_lekcje(n=3)) == 3
    finally:
        _cleanup(path)


def test_filtr_po_rezimie():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([1.0], rezim="TRENDING")
        p.zapisz_wynik([1.0], rezim="RANGING")
        p.zapisz_wynik([1.0], rezim="TRENDING")
        trendy = p.pobierz_lekcje(rezim="TRENDING")
        assert all(l.rezim == "TRENDING" for l in trendy)
        assert len(trendy) == 2
    finally:
        _cleanup(path)


def test_filtr_tylko_straty():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([10.0])
        p.zapisz_wynik([-5.0])
        straty = p.pobierz_lekcje(tylko_straty=True)
        assert all(l.wynik == "STRATA" for l in straty)
    finally:
        _cleanup(path)


# ── formatuj_dla_llm ──────────────────────────────────────────────────────────

def test_formatuj_niepusty():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([10.0, 5.0], rezim="NORMAL", interwal="1D")
        tekst = p.formatuj_dla_llm(n=3)
        assert "LEKCJE" in tekst
        assert "NORMAL" in tekst
    finally:
        _cleanup(path)


def test_formatuj_pusta_pamiec():
    p, path = _tmp_pamiec()
    try:
        tekst = p.formatuj_dla_llm()
        assert "Brak" in tekst
    finally:
        _cleanup(path)


# ── statystyki ────────────────────────────────────────────────────────────────

def test_statystyki_n_lekcji():
    p, path = _tmp_pamiec()
    try:
        p.zapisz_wynik([10.0])
        p.zapisz_wynik([-5.0])
        st = p.statystyki()
        assert st["n_lekcji"] == 2
    finally:
        _cleanup(path)


def test_statystyki_pusta_pamiec():
    p, path = _tmp_pamiec()
    try:
        st = p.statystyki()
        assert st["n_lekcji"] == 0
    finally:
        _cleanup(path)


# ── _generuj_auto ─────────────────────────────────────────────────────────────

def test_generuj_auto_zysk():
    tekst = _generuj_auto([10.0, 5.0], "TRENDING", "1D")
    assert len(tekst) > 0
    assert "TRENDING" in tekst or "działa" in tekst or "zysk" in tekst.lower()


def test_generuj_auto_strata():
    tekst = _generuj_auto([-10.0, -5.0], "RANGING", "4H")
    assert "STRATA" in tekst or "strat" in tekst.lower()


def test_generuj_auto_pusta_lista():
    tekst = _generuj_auto([], "NORMAL", "1D")
    assert len(tekst) > 0
