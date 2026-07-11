"""Smoke-test orkiestratora przygotuj_biblioteke (cienki wrapper — komponenty testowane osobno)."""

from narzedzia import przygotuj_biblioteke as pb


def test_narzedzie_zwraca_bool():
    # Coś, co na pewno istnieje (python) vs coś nieistniejącego.
    assert pb._narzedzie("python") in (True, False)   # nie wybucha
    assert pb._narzedzie("na-pewno-nie-ma-tego-narzedzia-xyz") is False


def test_modul_ma_main():
    assert callable(pb.main)
