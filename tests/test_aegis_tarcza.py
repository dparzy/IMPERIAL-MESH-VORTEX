"""Testy AegisShield (imperium/pretorianie/aegis_tarcza.py).

Moduł miał ZERO testów (zwiad ryzyka kodu 2026-07-21) — a ma mianowniki
(peak_capital, initial_capital) podatne na ZeroDivisionError. P5 fali 1:
guard kapitału + pokrycie ścieżek drawdown/limit dziennego.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from imperium.pretorianie.aegis_tarcza import AegisShield


def test_kapital_niedodatni_odrzucony_u_wrot():
    """initial_capital <= 0 = mianownik zero w update() → ValueError w __init__,
    nie ZeroDivisionError później. Fail-loud."""
    for zly in (0.0, -50.0):
        with pytest.raises(ValueError, match="initial_capital"):
            AegisShield(initial_capital=zly)


def test_kapital_dodatni_dziala():
    a = AegisShield(initial_capital=50.0)
    assert a.update(-1.0) == "OK"          # mały strata, żaden próg
    assert a.update(+2.0) == "OK"


def test_flatten_przy_50pct_drawdown():
    """Granica: drawdown ≥ 50% → FLATTEN_ALL (peak_capital w mianowniku, kapitał>0)."""
    a = AegisShield(initial_capital=100.0)
    assert a.update(-60.0) == "FLATTEN_ALL"   # 100→40, drawdown 60% ≥ 50%


def test_circuit_breaker_po_serii_strat():
    """3 straty z rzędu → CIRCUIT_BREAKER (domyślne max_consecutive_losses=3)."""
    a = AegisShield(initial_capital=1000.0, max_consecutive_losses=3)
    assert a.update(-1.0) == "OK"
    assert a.update(-1.0) == "OK"
    assert a.update(-1.0) == "CIRCUIT_BREAKER"
