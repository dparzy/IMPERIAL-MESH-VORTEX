"""
Testy W-340 Detektor reżimu zmienności (vol-gate) — Prawo XXI testy granic.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.legiony.rezim_zmiennosci import (
    vol_regime_turbo,
    _ewma,
    _standaryzuj,
    _viterbi_2stan,
)
from imperium.legiony.legatus import klasyfikuj_rezim


# ─── _ewma ────────────────────────────────────────────────────────────────────

def test_ewma_pusta():
    assert _ewma([], 10) == []


def test_ewma_stala_seria():
    """Stała seria → EWMA = ta sama stała."""
    out = _ewma([5.0] * 10, 5)
    for v in out:
        assert abs(v - 5.0) < 1e-9


def test_ewma_dlugosc():
    assert len(_ewma([1.0, 2.0, 3.0], 2)) == 3


# ─── _standaryzuj ─────────────────────────────────────────────────────────────

def test_standaryzuj_zero_wariancji():
    """Stała seria → same zera (nie NaN)."""
    out = _standaryzuj([3.0, 3.0, 3.0])
    assert all(abs(v) < 1e-9 for v in out)


def test_standaryzuj_srednia_zero():
    out = _standaryzuj([1.0, 2.0, 3.0, 4.0, 5.0])
    assert abs(sum(out) / len(out)) < 1e-9


# ─── _viterbi_2stan ───────────────────────────────────────────────────────────

def test_viterbi_pusta():
    assert _viterbi_2stan([], 0.0, 1.0, 30.0) == []


def test_viterbi_dlugosc():
    seq = _viterbi_2stan([0.0, 0.1, 0.9, 1.0], 0.0, 1.0, 5.0)
    assert len(seq) == 4
    assert all(s in (0, 1) for s in seq)


def test_viterbi_duza_kara_jeden_stan():
    """Bardzo duża kara → brak przełączeń (jeden stan na całość)."""
    seq = _viterbi_2stan([0.0, 1.0, 0.0, 1.0], 0.0, 1.0, 1e6)
    assert len(set(seq)) == 1


def test_viterbi_zero_kary_najblizszy():
    """Kara=0 → każdy bar do najbliższego centroidu."""
    seq = _viterbi_2stan([0.1, 0.9, 0.1, 0.9], 0.0, 1.0, 0.0)
    assert seq == [0, 1, 0, 1]


# ─── vol_regime_turbo — granice ───────────────────────────────────────────────

def test_turbo_za_malo_danych():
    turbo, trw, sila = vol_regime_turbo([100.0] * 10)
    assert turbo is False
    assert trw == 0
    assert sila == 0.0


def test_turbo_stala_cena_brak_rezimu():
    """Stała cena (zero zmienności) → brak separacji reżimów → False."""
    turbo, trw, sila = vol_regime_turbo([100.0] * 60)
    assert turbo is False
    assert sila == 0.0


def test_turbo_zwraca_typy():
    import random
    random.seed(11)
    ceny = [100.0]
    for _ in range(80):
        ceny.append(ceny[-1] * (1 + random.gauss(0.0, 0.02)))
    turbo, trw, sila = vol_regime_turbo(ceny)
    assert isinstance(turbo, bool)
    assert isinstance(trw, int)
    assert 0.0 <= sila <= 1.0


def test_turbo_wykrywa_wzrost_zmiennosci():
    """Seria: spokój → nagła turbulencja na końcu → ostatni bar turbo."""
    import random
    random.seed(3)
    ceny = [100.0]
    # 50 barów spokoju (mała zmienność)
    for _ in range(50):
        ceny.append(ceny[-1] * (1 + random.gauss(0.0, 0.003)))
    # 20 barów turbulencji (duża zmienność)
    for _ in range(20):
        ceny.append(ceny[-1] * (1 + random.gauss(0.0, 0.05)))
    turbo, trw, sila = vol_regime_turbo(ceny)
    assert turbo is True
    assert trw >= 1


def test_turbo_spokoj_na_koncu():
    """Seria: turbulencja → spokój na końcu → ostatni bar NIE turbo."""
    import random
    random.seed(5)
    ceny = [100.0]
    for _ in range(25):
        ceny.append(ceny[-1] * (1 + random.gauss(0.0, 0.05)))
    for _ in range(45):
        ceny.append(ceny[-1] * (1 + random.gauss(0.0, 0.003)))
    turbo, trw, sila = vol_regime_turbo(ceny)
    assert turbo is False


# ─── Integracja z klasyfikatorem reżimu (opt-in) ──────────────────────────────

def test_klasyfikator_vol_regime_off_domyslnie():
    """Domyślnie (OFF) — VOL_REGIME_TURBO ignorowany."""
    wsk = {"VOL_REGIME_TURBO": 1.0, "VOL_REGIME_TRWALOSC": 10.0}
    assert klasyfikuj_rezim(wsk) == "NORMAL"


def test_klasyfikator_vol_regime_on_turbo():
    """opt-in ON + turbo trwały → VOLATILE."""
    wsk = {"VOL_REGIME_TURBO": 1.0, "VOL_REGIME_TRWALOSC": 5.0}
    assert klasyfikuj_rezim(wsk, uzyj_vol_regime=True) == "VOLATILE"


def test_klasyfikator_vol_regime_on_krotka_trwalosc():
    """opt-in ON ale trwałość < 4 → NIE VOLATILE (filtr whipsaw)."""
    wsk = {"VOL_REGIME_TURBO": 1.0, "VOL_REGIME_TRWALOSC": 2.0}
    assert klasyfikuj_rezim(wsk, uzyj_vol_regime=True) == "NORMAL"


def test_klasyfikator_vol_regime_on_spokoj():
    """opt-in ON ale spokój → NIE VOLATILE."""
    wsk = {"VOL_REGIME_TURBO": 0.0, "VOL_REGIME_TRWALOSC": 10.0}
    assert klasyfikuj_rezim(wsk, uzyj_vol_regime=True) == "NORMAL"


def test_klasyfikator_atr_priorytet_nad_vol_regime():
    """ATR_DEVIATION > 2.5 → VOLATILE niezależnie od vol-regime."""
    wsk = {"ATR_DEVIATION": 3.0, "VOL_REGIME_TURBO": 0.0}
    assert klasyfikuj_rezim(wsk, uzyj_vol_regime=True) == "VOLATILE"
