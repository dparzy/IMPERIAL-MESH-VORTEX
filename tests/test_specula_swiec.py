"""
Testy SPECULA — świece OHLC w terminalu (W-361, Prawo XXIV + Reguła Test-Granic).

Testy przechodzą ZARÓWNO z zainstalowanym plotext, jak i bez (rdzeń bez zależności):
ścieżki graniczne (brak plotext / 0 / 1 bar / złe dane) nie wymagają plotext;
render właściwy testowany warunkowo tylko gdy PLOTEXT_DOSTEPNY.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.swiatynie import specula_swiec as sp
from imperium.swiatynie.specula_swiec import (
    render_swiece,
    komunikat_braku_plotext,
    MIN_BARY,
)


def _bary(n, base=None):
    """n barów w naszym formacie OHLC."""
    import datetime
    if base is None:
        base = int(datetime.datetime(2024, 1, 1).timestamp() * 1000)
    out = []
    for i in range(n):
        out.append({
            "timestamp": base + i * 3600_000,
            "open": 100.0 + i,
            "high": 103.0 + i,
            "low": 98.0 + i,
            "close": 101.0 + (i % 3) - 1,
            "volume": 10.0,
            "symbol": "BTCUSDT",
            "interwal": "1H",
        })
    return out


# ── Granica: brak plotext (degradacja, nie crash) ──────────────────────────────

def test_brak_plotext_komunikat():
    """Gdy plotext niedostępny → komunikat-podpowiedź, nie wyjątek."""
    stary = sp.PLOTEXT_DOSTEPNY
    try:
        sp.PLOTEXT_DOSTEPNY = False
        wynik = render_swiece(_bary(10))
        assert "plotext" in wynik.lower()
        assert wynik.startswith("🗼")
    finally:
        sp.PLOTEXT_DOSTEPNY = stary


def test_komunikat_braku_zawiera_instrukcje():
    msg = komunikat_braku_plotext()
    assert "pip install plotext" in msg


# ── Granica: za mało danych (0 i 1 bar) ────────────────────────────────────────

def _z_plotextem(f, *a, **kw):
    """Wymusza gałąź „plotext obecny", żeby granica LICZBY BARÓW była mierzona wszędzie.

    Zmierzone 2026-07-26: te dwa testy padały w chmurze (`plotext` to zależność
    OPCJONALNA, w chmurze nieobecna). `render_swiece` sprawdza bibliotekę PRZED liczbą
    barów, więc bez niej zwracał komunikat o bibliotece i asercja „za mało" nie miała
    prawa przejść — a docstring tego pliku twierdził, że granice działają BEZ plotext.
    Brak opcjonalnego zasobu nie może udawać ani porażki, ani zieleni: wymuszamy gałąź,
    zamiast pomijać test (pominięty test milczałby o granicy dokładnie tam, gdzie CI żyje).
    """
    stary = sp.PLOTEXT_DOSTEPNY
    try:
        sp.PLOTEXT_DOSTEPNY = True
        return f(*a, **kw)
    finally:
        sp.PLOTEXT_DOSTEPNY = stary


def test_zero_barow_nie_crashuje():
    wynik = _z_plotextem(render_swiece, [])
    assert wynik.startswith("🗼")
    assert "za mało" in wynik


def test_jeden_bar_ponizej_minimum():
    """1 bar < MIN_BARY (2) → komunikat, nie crash."""
    assert MIN_BARY == 2
    wynik = _z_plotextem(render_swiece, _bary(1))
    assert "za mało" in wynik


def test_none_zamiast_listy_nie_crashuje():
    wynik = render_swiece(None)
    assert wynik.startswith("🗼")


# ── Render właściwy (tylko gdy plotext dostępny) ───────────────────────────────

def test_render_dwa_bary_granica_minimum():
    """Dokładnie MIN_BARY barów — powinno się renderować (nie 'za mało')."""
    if not sp.PLOTEXT_DOSTEPNY:
        return  # bez plotext ścieżka renderu nietestowalna
    wynik = render_swiece(_bary(MIN_BARY))
    assert "za mało" not in wynik
    assert len(wynik) > 0


def test_render_zwykly_niepusty():
    if not sp.PLOTEXT_DOSTEPNY:
        return
    wynik = render_swiece(_bary(12), tytul="BTCUSDT 1H")
    assert len(wynik) > 50


def test_render_ze_znacznikami_nie_crashuje():
    if not sp.PLOTEXT_DOSTEPNY:
        return
    bary = _bary(12)
    znaczniki = [
        {"timestamp": bary[3]["timestamp"], "cena": bary[3]["low"],
         "kierunek": "LONG", "typ": "wejscie"},
        {"timestamp": bary[9]["timestamp"], "cena": bary[9]["high"],
         "kierunek": "LONG", "typ": "wyjscie"},
    ]
    wynik = render_swiece(bary, znaczniki=znaczniki)
    assert len(wynik) > 50


def test_zly_znacznik_pomijany_nie_crashuje():
    """Znacznik bez wymaganych kluczy nie wywraca całego wykresu."""
    if not sp.PLOTEXT_DOSTEPNY:
        return
    bary = _bary(8)
    znaczniki = [{"brak": "kluczy"}, {"timestamp": "zła", "cena": "x"}]
    wynik = render_swiece(bary, znaczniki=znaczniki)
    # nie rzuca — zwraca string (wykres albo komunikat błędu, oba to string)
    assert isinstance(wynik, str)


def test_zle_dane_baru_zwraca_string_nie_wyjatek():
    """Bar z brakującym kluczem 'close' → komunikat błędu, nie wyjątek."""
    if not sp.PLOTEXT_DOSTEPNY:
        return
    zle = [{"timestamp": 1, "open": 1, "high": 2, "low": 0},
           {"timestamp": 2, "open": 1, "high": 2, "low": 0}]
    wynik = render_swiece(zle)
    assert isinstance(wynik, str)  # nie crashuje


# ── Integracja z LiveMonitor (świece jako opcjonalny panel) ────────────────────

def test_live_monitor_render_ze_swiecami_nie_crashuje():
    from imperium.swiatynie.live_monitor import LiveMonitor, StanDashboardu
    stan = StanDashboardu(symbol="BTCUSDT", swiece=_bary(10))
    m = LiveMonitor()
    m.aktualizuj(stan)
    m.render(clear=False)  # nie rzuca


def test_live_monitor_bez_swiec_render_dziala():
    from imperium.swiatynie.live_monitor import LiveMonitor, StanDashboardu
    stan = StanDashboardu(symbol="BTCUSDT")  # swiece=[] domyślnie
    m = LiveMonitor()
    m.aktualizuj(stan)
    m.render(clear=False)
