"""
Testy W-339 Fractional Differentiation (Prawo XXI — testy granic).
"""

import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.legiony.frac_diff import (
    _frac_diff_weights,
    frac_diff_series,
    _adf_stat,
    _find_min_d,
    frac_diff_signal,
)
from imperium.legiony.neurony.entropia import NeuronFracDiff


# ─── _frac_diff_weights ───────────────────────────────────────────────────────

def test_weights_d1_dwa_elementy():
    """d=1: w_0=1, w_1=-1 (zwykła różnica)."""
    w = _frac_diff_weights(1.0, eps=1e-9, max_w=5)
    assert abs(w[0] - 1.0) < 1e-9
    assert abs(w[1] - (-1.0)) < 1e-9


def test_weights_d0_jeden_element():
    """d=0: dokładnie zero → tylko w_0=1 (brak różnicowania)."""
    w = _frac_diff_weights(0.0, eps=1e-4)
    # w_1 = -w_0*(0-1)/1 = 0 → obcięcie przy eps
    assert len(w) == 1


def test_weights_suma_pf_d05():
    """d=0.5: wagi maleją i obcinają się."""
    w = _frac_diff_weights(0.5)
    assert len(w) >= 2
    assert abs(w[0] - 1.0) < 1e-9
    assert w[1] < 0  # w_1 zawsze ujemny dla d>0


def test_weights_malejace_absolutnie():
    """|w_k| nie rośnie."""
    w = _frac_diff_weights(0.5)
    for i in range(1, len(w)):
        assert abs(w[i]) <= abs(w[i - 1]) + 1e-9


# ─── frac_diff_series ─────────────────────────────────────────────────────────

def test_frac_diff_d1_rowne_zwrotom():
    """d=1, seria log-cen → powinno dawać log-zwroty (first difference)."""
    import math as _m
    ceny = [100.0, 102.0, 101.0, 103.0, 104.0]
    log_p = [_m.log(c) for c in ceny]
    serie = frac_diff_series(log_p, 1.0, eps=1e-9)
    # Serie powinna mieć len-1 elementów (warmup = 1 dla d=1, 2 wag)
    diffs = [log_p[i] - log_p[i - 1] for i in range(1, len(log_p))]
    assert len(serie) == len(diffs)
    for a, b in zip(serie, diffs):
        assert abs(a - b) < 1e-9


def test_frac_diff_za_krotka():
    """Za krótka seria → []."""
    assert frac_diff_series([100.0, 101.0], 0.5) == []


def test_frac_diff_wartosc_skonczona():
    """Wyniki skończone dla typowej serii."""
    import math as _m
    log_p = [_m.log(100.0 + i * 0.5) for i in range(50)]
    serie = frac_diff_series(log_p, 0.4)
    for v in serie:
        assert math.isfinite(v)


# ─── _adf_stat ────────────────────────────────────────────────────────────────

def test_adf_za_malo():
    assert _adf_stat([1.0, 2.0, 3.0]) is None


def test_adf_random_walk_duzy_t():
    """Random walk (unit root) → duży t-stat (bliski 0, nie ujemny)."""
    serie = [float(i) for i in range(50)]  # perfect random walk
    t = _adf_stat(serie)
    assert t is not None
    # Dla czystego trendu liniowego β ≈ 0, t ≈ 0 (brak odrzucenia H0)
    assert t > -2.9  # nie odrzucamy unit root (słuszne)


def test_adf_stacjonarna_ujemny_t():
    """Stacjonarna seria (oscylacyjna) → ujemny t-stat."""
    import math as _m
    serie = [_m.sin(i * 0.3) for i in range(50)]
    t = _adf_stat(serie)
    assert t is not None
    assert t < 0  # odrzucamy unit root (H0: unit root)


# ─── _find_min_d ─────────────────────────────────────────────────────────────

def test_find_min_d_zwraca_w_zakresie():
    """d ∈ [0.1, 1.0]."""
    import math as _m
    log_p = [_m.log(100.0 + i * 0.1) for i in range(80)]
    d = _find_min_d(log_p)
    assert 0.09 < d <= 1.0


# ─── frac_diff_signal ─────────────────────────────────────────────────────────

def test_signal_za_malo():
    p, z = frac_diff_signal([100.0] * 10)
    assert p is None
    assert z is None


def test_signal_zwraca_d_i_z():
    ceny = [100.0 * (1 + 0.01 * i) for i in range(60)]
    d, z = frac_diff_signal(ceny)
    assert d is not None
    assert 0.09 < d <= 1.0
    assert z is not None
    assert math.isfinite(z)


def test_signal_z_w_zakresie():
    """z-score nie jest absurdalnie duże."""
    import random; random.seed(7)
    ceny = [100.0]
    for _ in range(80):
        ceny.append(ceny[-1] * (1 + random.gauss(0.001, 0.02)))
    d, z = frac_diff_signal(ceny)
    assert d is not None
    assert z is not None
    assert -10.0 < z < 10.0  # typowy z-score


# ─── NeuronFracDiff ───────────────────────────────────────────────────────────

def test_neuron_brak_danych():
    n = NeuronFracDiff()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_neuron_za_krotka():
    n = NeuronFracDiff()
    s = n.interpretuj({"CLOSE_SERIES_100": [100.0] * 10})
    assert s.kierunek == "NEUTRAL"


def test_neuron_zwraca_sygnal():
    n = NeuronFracDiff()
    serie = [100.0 * (1.0 + 0.005 * i) for i in range(60)]
    s = n.interpretuj({"CLOSE_SERIES_100": serie})
    assert s.kierunek in ("LONG", "SHORT", "NEUTRAL")
    assert 0.0 <= s.pewnosc <= 1.0


def test_neuron_klucz():
    assert NeuronFracDiff.KLUCZ == "N-02"
    assert NeuronFracDiff.KATEGORIA == "N"
    assert NeuronFracDiff.WAGA == 6
