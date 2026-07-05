"""Testy raportu etykiet (narzedzia/raport_etykiet.py) — na serii syntetycznej."""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.raport_etykiet import raport_z_close


def _close_trend(n=200):
    # trend z oscylacją — CUSUM wykryje zdarzenia, bariery się rozstrzygną
    c = 100.0
    out = []
    for i in range(n):
        c *= 1.01 if (i // 5) % 2 == 0 else 0.995
        out.append(c)
    return out


def test_raport_zwraca_statystyki():
    out = raport_z_close(_close_trend(), h_cusum=0.005)
    assert "RAPORT ETYKIET" in out
    assert "TP (+1" in out and "uniqueness" in out


def test_za_malo_barow():
    assert "za mało" in raport_z_close([100.0, 101.0, 102.0]).lower()


def test_cusum_bez_zdarzen_komunikat():
    # płaska seria + wysoki próg → brak zdarzeń CUSUM
    plaska = [100.0] * 100
    out = raport_z_close(plaska, h_cusum=0.5)
    assert "nie wykrył zdarzeń" in out.lower() or "za mało" in out.lower()


def test_procenty_tp_sl_timeout_sumuja_do_100():
    """TP% + SL% + timeout% = 100 (każde zdarzenie ma dokładnie jedną etykietę)."""
    import re
    out = raport_z_close(_close_trend(300), h_cusum=0.005)
    # trzy pierwsze wartości z '%' to TP/SL/timeout (avg_zysk ma znak, nie kończy się '%')
    procs = [float(m.group(1)) for m in re.finditer(r"([\d.]+)%", out)]
    assert abs(procs[0] + procs[1] + procs[2] - 100.0) < 0.5
