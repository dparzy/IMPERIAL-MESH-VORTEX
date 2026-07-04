"""Test raportu IC roju (narzedzia/raport_ic.py) — na syntetycznych barach."""

import logging
logging.disable(logging.CRITICAL)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.raport_ic import zbierz_ic, raport, _klasa_ic


def test_klasa_ic_progi():
    assert _klasa_ic(0.01) == "szum"
    assert _klasa_ic(0.03) == "słaba przewaga"
    assert _klasa_ic(0.06) == "MOCNY"
    assert _klasa_ic(-0.06) == "MOCNY"   # znak nieistotny dla klasy siły


def test_klasa_ic_granice_dokladne():
    """Reguła Test-Granic: wartości DOKŁADNIE na progu (<0.02, <0.05 → który bok?)."""
    assert _klasa_ic(0.0) == "szum"       # zero = brak sygnału
    assert _klasa_ic(0.02) == "słaba przewaga"   # 0.02 nie jest <0.02 → już nie szum
    assert _klasa_ic(-0.02) == "słaba przewaga"  # znak nieistotny
    assert _klasa_ic(0.05) == "MOCNY"     # 0.05 nie jest <0.05 → już MOCNY
    assert _klasa_ic(-0.05) == "MOCNY"
    assert _klasa_ic(0.0199) == "szum"    # tuż pod progiem
    assert _klasa_ic(0.0499) == "słaba przewaga"


def test_zbierz_ic_pusta_lista():
    w = zbierz_ic([], "4h")
    assert w["ic"] == {} and w["pary"] == 0


def test_raport_bez_danych():
    assert "brak danych" in raport([], "4h")
