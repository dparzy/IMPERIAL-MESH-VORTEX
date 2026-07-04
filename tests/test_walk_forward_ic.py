"""Testy walk-forward IC (narzedzia/walk_forward_ic.py) — logika werdyktu."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from narzedzia.walk_forward_ic import analizuj


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
