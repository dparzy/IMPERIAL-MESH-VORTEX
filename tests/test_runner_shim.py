"""Testy namiastki `monkeypatch` w runnerze Imperium (tests/run_tests.py).

DLACZEGO TEN PLIK ISTNIEJE (zmierzone dwukrotnie): runner JEST bramką Prawa XXI, a pytest
nie. Gdy shim nie ma metody, której używa test, autor widzi ZIELONO pod pytest i CZERWONO
pod bramką — fałszywy spokój w narzędziu, któremu ufa. Brak `setitem` złapano 2026-07-20
(pieczęcie) i ponownie 2026-07-21 (leksykon LIBRA MESSIS). Lekarstwem nie jest omijanie
shimu w testach, tylko trzymanie go w zgodzie z tym, czego testy naprawdę używają.

Testy biegną pod OBOMA silnikami (pytest i runner) i muszą przechodzić w obu.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_shim_ma_metody_uzywane_w_testach():
    """Shim musi pokrywać KAŻDĄ metodę monkeypatch faktycznie wołaną w tests/*.py.

    Test szuka wywołań `monkeypatch.<metoda>` w korpusie testów i żąda, żeby shim je miał —
    więc dodanie testu z nową metodą zapala się TU, a nie dopiero na bramce przed commitem."""
    import re
    from tests.run_tests import _MonkeyPatch

    katalog = os.path.dirname(os.path.abspath(__file__))
    uzywane = set()
    for nazwa in os.listdir(katalog):
        if not (nazwa.startswith("test_") and nazwa.endswith(".py")):
            continue
        tresc = open(os.path.join(katalog, nazwa), encoding="utf-8", errors="replace").read()
        uzywane |= set(re.findall(r"monkeypatch\.(\w+)\s*\(", tresc))
    brak = {m for m in uzywane if not hasattr(_MonkeyPatch, m)}
    assert not brak, f"testy wołają metody, których shim runnera NIE MA: {sorted(brak)}"


def test_setitem_i_cofanie(monkeypatch):
    """setitem podmienia i cofa — także gdy klucza NIE BYŁO (nie zostawia śmiecia)."""
    from tests.run_tests import _MonkeyPatch

    mapa = {"jest": 1}
    mp = _MonkeyPatch()
    mp.setitem(mapa, "jest", 99)
    mp.setitem(mapa, "nowy", 5)
    assert mapa == {"jest": 99, "nowy": 5}
    mp.undo()
    assert mapa == {"jest": 1}, "cofanie zostawiło klucz, którego pierwotnie nie było"


def test_delitem_i_cofanie():
    """delitem usuwa i przywraca; brak klucza przy raising=True to KeyError."""
    from tests.run_tests import _MonkeyPatch

    mapa = {"a": 1, "b": 2}
    mp = _MonkeyPatch()
    mp.delitem(mapa, "a")
    assert mapa == {"b": 2}
    mp.undo()
    assert mapa == {"a": 1, "b": 2}

    try:
        _MonkeyPatch().delitem({}, "nie_ma")
    except KeyError:
        pass
    else:
        raise AssertionError("delitem(raising=True) na brakującym kluczu nie rzucił KeyError")


def test_setattr_cofa_gdy_atrybutu_nie_bylo():
    """Granica: None jest LEGALNĄ wartością atrybutu, więc znacznik braku nie może być None.

    Stara wersja shimu zapisywała `getattr(obj, name, None)` — atrybut o wartości None
    i atrybut NIEISTNIEJĄCY były nierozróżnialne, więc cofanie kasowało pole, które
    istniało i legalnie trzymało None."""
    from tests.run_tests import _MonkeyPatch

    class Pusty:
        pole_none = None

    mp = _MonkeyPatch()
    mp.setattr(Pusty, "pole_none", 7)
    mp.setattr(Pusty, "pole_nowe", 8)
    mp.undo()
    assert Pusty.pole_none is None, "cofanie skasowało atrybut, który legalnie trzymał None"
    assert not hasattr(Pusty, "pole_nowe")


def test_setenv_delenv_cofaja_srodowisko():
    """Zmienne środowiskowe wracają do stanu sprzed testu (także brak zmiennej)."""
    from tests.run_tests import _MonkeyPatch

    klucz = "IMPERIUM_TEST_SHIM_XYZ"
    os.environ.pop(klucz, None)
    mp = _MonkeyPatch()
    mp.setenv(klucz, "wartosc")
    assert os.environ[klucz] == "wartosc"
    mp.undo()
    assert klucz not in os.environ


def test_runner_honoruje_pominiecie_w_dialekcie_pytesta():
    """Runner musi traktować `pytest.skip()` jak pominięcie — NIE jak śmierć całego biegu.

    ZMIERZONA WADA (2026-08-06, symulacja CI na czystym klonie bez bazy RAG):
    `_pytest.outcomes.Skipped` dziedziczy po BaseException, nie po Exception, więc
    przelatywał przez wszystkie `except` pętli runnera i przerywał bieg tracebackiem —
    wszystkie pliki testowe PO winowajcy nie uruchamiały się w ogóle. Lokalnie niewidoczne
    (u Cezara baza RAG istnieje, więc skip nie zachodził): strażnik działający na jednej
    maszynie. To jest TEST GRANICY: celowo rzucam to, co producent wcześniej zabijało.
    """
    from tests.run_tests import _POMINIECIA

    assert unittest.SkipTest in _POMINIECIA, "stdlibowy SkipTest wypadł z obsługi pominięć"

    try:
        from _pytest.outcomes import Skipped
    except Exception:  # noqa: BLE001 — bez pytesta nie ma czego sprawdzać
        raise unittest.SkipTest(
            "pytest niezainstalowany — dialekt pytesta nie dotyczy tej maszyny") from None

    # Sedno wady: gdyby Skipped był zwykłym Exception, obsługa nie byłaby potrzebna.
    # Gdy pytest kiedyś zmieni hierarchię, ten assert zgaśnie i powie DLACZEGO.
    assert not issubclass(Skipped, Exception), \
        "Skipped stał się zwykłym Exception — obsługa specjalna może być zbędna, sprawdź runner"
    assert Skipped in _POMINIECIA, \
        "pytest.skip() ubije cały bieg runnera — Skipped musi być w _POMINIECIA"

    # Dowód wykonawczy, nie tylko strukturalny: krotka MUSI faktycznie łapać.
    zlapane = False
    try:
        raise Skipped("celowe pominięcie w dialekcie pytesta")
    except _POMINIECIA:
        zlapane = True
    assert zlapane, "krotka _POMINIECIA nie łapie Skipped — bieg nadal umiera na pytest.skip()"
