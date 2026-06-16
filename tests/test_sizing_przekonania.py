"""Testy Sizing Przekonania (W-318) — mnożnik stawki + fractional Kelly, granice."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.pretorianie.sizing_przekonania import SizingPrzekonania


def _s():
    return SizingPrzekonania()


# ─── Mnożnik przekonania ───────────────────────────────────────────────────────

def test_neutralny_daje_jeden():
    """Przekonanie == prog_neutralny → mnożnik dokładnie 1.0 (stawka bazowa)."""
    assert _s().mnoznik(0.5) == 1.0


def test_pelne_przekonanie_max():
    assert _s().mnoznik(1.0) == 3.0


def test_zero_przekonania_min():
    assert _s().mnoznik(0.0) == 0.5


def test_rosnie_monotonicznie():
    s = _s()
    vals = [s.mnoznik(p) for p in (0.0, 0.25, 0.5, 0.75, 1.0)]
    assert vals == sorted(vals)


def test_polowa_drogi_w_gore():
    """Przekonanie 0.75 (połowa między 0.5 a 1.0) → mnożnik połowa między 1.0 a 3.0 = 2.0."""
    assert _s().mnoznik(0.75) == 2.0


def test_clamp_powyzej_jeden():
    assert _s().mnoznik(1.5) == 3.0


def test_clamp_ponizej_zero():
    assert _s().mnoznik(-0.3) == 0.5


def test_progi_konfigurowalne():
    s = SizingPrzekonania(min_mnoznik=0.2, max_mnoznik=5.0, prog_neutralny=0.6)
    assert s.mnoznik(0.6) == 1.0
    assert s.mnoznik(1.0) == 5.0
    assert s.mnoznik(0.0) == 0.2


# ─── Fractional Kelly ──────────────────────────────────────────────────────────

def test_kelly_dodatnia_przewaga():
    """p=0.6, rr=2 → f=(2*0.6-0.4)/2=0.4; half-Kelly=0.2."""
    assert SizingPrzekonania.kelly_frakcja(0.6, 2.0, frakcja=0.5) == 0.2


def test_kelly_ujemna_przewaga_zero():
    """p=0.3, rr=1 → f=(0.3-0.7)/1=-0.4 → przycięte do 0 (nie betuj)."""
    assert SizingPrzekonania.kelly_frakcja(0.3, 1.0) == 0.0


def test_kelly_rr_zero_zwraca_zero():
    assert SizingPrzekonania.kelly_frakcja(0.9, 0.0) == 0.0


def test_kelly_pelny_vs_frakcyjny():
    full = SizingPrzekonania.kelly_frakcja(0.6, 2.0, frakcja=1.0)
    half = SizingPrzekonania.kelly_frakcja(0.6, 2.0, frakcja=0.5)
    assert abs(full - 2 * half) < 1e-9


def test_kelly_granica_break_even():
    """p=1/3, rr=2 → f=(2/3 - 2/3)/2 = 0 (dokładnie próg break-even)."""
    assert SizingPrzekonania.kelly_frakcja(1/3, 2.0, frakcja=1.0) == 0.0
