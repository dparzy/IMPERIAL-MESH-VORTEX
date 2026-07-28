"""Smoke-test orkiestratora przygotuj_biblioteke (cienki wrapper — komponenty testowane osobno)."""

import sys

from imperium.fundament import faber
from narzedzia import przygotuj_biblioteke as pb


def test_wykrywanie_narzedzia_istniejacego_i_brakujacego():
    # Detektor obecności przeniesiony 2026-07-28 z lokalnego `_narzedzie` (samo shutil.which)
    # do organu FABER — powód: which() zwracał None dla ZAINSTALOWANEGO calibre spoza PATH,
    # a potok zamieniał to w cichą stratę. Gwarancja testu zostaje ta sama co wcześniej:
    # pozytyw MOCNY (nie tautologia `in (True, False)` — cubic PR119 P3) + jawny negatyw.
    faber.wyczysc_cache()
    assert faber.sciezka(sys.executable) is not None      # interpreter tego testu ISTNIEJE zawsze
    assert faber.sciezka("na-pewno-nie-ma-tego-narzedzia-xyz") is None


def test_orkiestrator_uzywa_fabera():
    """Potok MUSI wołać FABERA — inaczej wraca stara, cicha ścieżka wykrywania narzędzi."""
    zrodlo = (pb.ROOT / "narzedzia" / "przygotuj_biblioteke.py").read_text(encoding="utf-8")
    assert "faber.zapewnij_path()" in zrodlo
    assert "faber.alarmy(" in zrodlo


def test_modul_ma_main():
    assert callable(pb.main)
