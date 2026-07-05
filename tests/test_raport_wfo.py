"""Testy raportu WFO (narzedzia/raport_wfo.py) — ewaluator + formatowanie."""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.raport_wfo import ewaluator_backtest, raport_pliku


def _bary(n=200, symbol="BTCUSDT"):
    c = 100.0
    out = []
    for i in range(n):
        c *= 1.004 if (i // 6) % 2 == 0 else 0.997
        out.append({
            "timestamp": 1_600_000_000_000 + i * 3_600_000,
            "open": c, "high": c * 1.002, "low": c * 0.998, "close": c,
            "volume": 1000.0 + i, "volume_quote": 0.0,
            "symbol": symbol, "interwal": "1H", "tradecount": 100,
        })
    return out


def test_ewaluator_zwraca_kapital_i_zwroty():
    ev = ewaluator_backtest("1H", okno=60)
    kapital, zwroty = ev(_bary(), {"min_pewnosc": 0.55})
    assert isinstance(kapital, float) and kapital > 0
    assert isinstance(zwroty, list)
    assert all(isinstance(z, float) for z in zwroty)


def test_raport_pliku_formatuje_werdykt(monkeypatch):
    """Formatowanie bez ciężkiej optymalizacji — monkeypatch walk_forward."""
    import imperium.koloseum.walk_forward as wf

    class _Fake:
        werdykt = "ROBUST"
        powod = "WFE>0.5"
        n_okien = 4
        wfe_srednia = 0.72
        oos_sharpe_zagregowany = 0.31
        stabilnosc_parametrow = {"min_pewnosc": 0.12}

    monkeypatch.setattr(wf, "walk_forward", lambda *a, **k: _Fake())
    out = raport_pliku(_bary(), "1H", 100, 40, 60, 5, 0.45, 0.75)
    assert "ROBUST" in out and "WFE śr: +0.720" in out and "CV(min_pewnosc): 0.12" in out


def test_raport_pliku_brak_danych(monkeypatch):
    import imperium.koloseum.walk_forward as wf

    class _Fake:
        werdykt = "BRAK_DANYCH"; powod = "za mało barów"; n_okien = 0
        wfe_srednia = 0.0; oos_sharpe_zagregowany = 0.0; stabilnosc_parametrow = {}

    monkeypatch.setattr(wf, "walk_forward", lambda *a, **k: _Fake())
    out = raport_pliku([], "1H", 500, 150, 60, 5, 0.45, 0.75)
    assert "BRAK_DANYCH" in out
