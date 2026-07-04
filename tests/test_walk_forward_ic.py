"""Testy walk-forward IC (narzedzia/walk_forward_ic.py) — logika werdyktu."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pytest
from narzedzia.walk_forward_ic import analizuj, _ic_per_okno


def test_robust_stabilny_dodatni():
    r = analizuj({"A": [0.1, 0.12, 0.09, 0.11]})
    assert r[0]["werdykt"] == "ROBUST" and r[0]["spojnosc"] == 1.0


def test_robust_odwroc_stabilny_ujemny():
    r = analizuj({"A": [-0.1, -0.12, -0.09, -0.11]})
    assert "odwróć" in r[0]["werdykt"]


def test_niepewny_miesza_znak():
    r = analizuj({"A": [0.5, -0.1, -0.1, 0.1]})   # śr 0.1>prog, spójność 50%<75%
    assert r[0]["werdykt"] == "niepewny"


def test_szum_niski_ic():
    r = analizuj({"A": [0.01, 0.02, -0.01, 0.005]})
    assert r[0]["werdykt"] == "szum"


def test_za_malo_okien_pomija():
    r = analizuj({"A": [0.1]})   # 1 okno < 2
    assert r == []


def test_min_okien_niepewny():
    """2 okna spójne ale <min_okien(3) → nie ROBUST."""
    r = analizuj({"A": [0.1, 0.1]}, min_okien=3)
    assert r[0]["werdykt"] != "ROBUST"


def test_granica_prog_ic_dokladnie():
    """Reguła Test-Granic: średni IC DOKŁADNIE == prog (0.03) → już ROBUST (>=)."""
    # 3 okna, każdy 0.03 → średnia 0.03, spójność 1.0 → abs>=prog spełnione
    r = analizuj({"A": [0.03, 0.03, 0.03]}, prog=0.03)
    assert r[0]["werdykt"] == "ROBUST"
    # tuż pod progiem → szum
    r2 = analizuj({"A": [0.0299, 0.0299, 0.0299]}, prog=0.03)
    assert r2[0]["werdykt"] == "szum"


def test_granica_spojnosc_dokladnie():
    """Spójność DOKŁADNIE == prog_spojnosci (0.75) → ROBUST (>=)."""
    # 4 okna: 3 dodatnie + 1 ujemne, ale średnia >prog → spójność 0.75
    r = analizuj({"A": [0.1, 0.1, 0.1, -0.02]}, prog=0.03, prog_spojnosci=0.75)
    assert r[0]["spojnosc"] == 0.75
    assert r[0]["werdykt"] == "ROBUST"


def test_ic_per_okno_zero_okien_rzuca():
    """okna<1 → ValueError zamiast dzielenia przez zero."""
    with pytest.raises(ValueError):
        _ic_per_okno([{}] * 100, "4h", 0, 250)
