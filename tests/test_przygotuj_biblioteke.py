"""Smoke-test orkiestratora przygotuj_biblioteke (cienki wrapper — komponenty testowane osobno)."""

from narzedzia import przygotuj_biblioteke as pb


def test_narzedzie_wykrywa_istniejace_i_brak():
    # Pozytyw MOCNY (cubic PR119 P3: `in (True, False)` było tautologią). shutil.which na
    # PEŁNEJ ścieżce zwraca ją, gdy jest wykonywalna — sys.executable (interpreter tego testu)
    # istnieje ZAWSZE, więc _narzedzie MUSI dać True. Regresja „zawsze False" zostałaby złapana.
    import sys
    assert pb._narzedzie(sys.executable) is True
    assert pb._narzedzie("na-pewno-nie-ma-tego-narzedzia-xyz") is False


def test_modul_ma_main():
    assert callable(pb.main)
