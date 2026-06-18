"""
Testy B-01 Meta-labeling scorer (Prawo XXI — testy granic).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.legiony.meta_labeling import (
    CechyMeta,
    MetaLabelingScorer,
    WynikMeta,
    _sigmoid,
    _LogisticSGD,
)


# ─── Mock RaportLegatusa ──────────────────────────────────────────────────────

class _MockRaport:
    def __init__(self, kierunek="LONG", pewnosc=0.7, sl=0.6, ss=0.4, aktyw=20, zgodnych=15, weto=False):
        self.kierunek = kierunek
        self.pewnosc_agregatu = pewnosc
        self.sila_long = sl
        self.sila_short = ss
        self.aktywnych_neuronow = aktyw
        self.zgodnych_neuronow = zgodnych
        self.weto = weto


# ─── _sigmoid ────────────────────────────────────────────────────────────────

def test_sigmoid_zero():
    assert abs(_sigmoid(0.0) - 0.5) < 1e-9


def test_sigmoid_duzy_dodatni():
    assert _sigmoid(100.0) > 0.999


def test_sigmoid_duzy_ujemny():
    assert _sigmoid(-100.0) < 0.001


def test_sigmoid_zakres():
    for x in [-50, -1, 0, 1, 50]:
        s = _sigmoid(float(x))
        assert 0.0 < s < 1.0


# ─── CechyMeta ───────────────────────────────────────────────────────────────

def test_cechy_z_raportu_podstawowe():
    r = _MockRaport()
    c = CechyMeta.z_raportu(r)
    assert c.pewnosc_agregatu == 0.7
    assert c.sila_long == 0.6
    assert c.sila_short == 0.4
    assert c.log_aktywnych > 0
    assert 0.0 <= c.roznica_sil <= 1.0


def test_cechy_wektor_dlugosc():
    c = CechyMeta.z_raportu(_MockRaport())
    assert len(c.jako_wektor()) == 6


def test_cechy_roznica_sil_symetria():
    """Równe siły → roznica = 0."""
    r = _MockRaport(sl=0.5, ss=0.5)
    c = CechyMeta.z_raportu(r)
    assert abs(c.roznica_sil) < 1e-9


def test_cechy_roznica_sil_max():
    """Jedna strona = 0 → roznica = 1."""
    r = _MockRaport(sl=0.8, ss=0.0)
    c = CechyMeta.z_raportu(r)
    assert abs(c.roznica_sil - 1.0) < 1e-6


# ─── _LogisticSGD ────────────────────────────────────────────────────────────

def test_logistic_init_przewiduje_poltora():
    """Przed treningiem (wagi=0) → przewiduje 0.5."""
    m = _LogisticSGD()
    p = m.przewiduj([0.5] * 6)
    assert abs(p - 0.5) < 1e-9


def test_logistic_ucz_zmienia_wagi():
    m = _LogisticSGD(lr=0.1)
    w_przed = list(m._w)
    m.ucz([1.0] * 6, 1)
    assert m._w != w_przed


def test_logistic_wyuczony_prog():
    m = _LogisticSGD()
    assert not m.wyuczony
    for _ in range(10):
        m.ucz([0.5] * 6, 1)
    assert m.wyuczony


def test_logistic_zbieznosc_zawsze_pozytywne():
    """Wiele iteracji z y=1 → P powinna rosnąć."""
    m = _LogisticSGD(lr=0.1)
    x = [0.7, 0.6, 0.4, 2.9, 2.7, 0.2]
    p_pocz = m.przewiduj(x)
    for _ in range(50):
        m.ucz(x, 1)
    p_po = m.przewiduj(x)
    assert p_po > p_pocz


# ─── MetaLabelingScorer — granice ────────────────────────────────────────────

def test_scorer_weto_daje_zero():
    scorer = MetaLabelingScorer()
    r = _MockRaport(weto=True)
    wynik = scorer.ocen(r)
    assert wynik.bet_size == 0.0
    assert wynik.pewnosc_meta == 0.0


def test_scorer_neutral_daje_zero():
    scorer = MetaLabelingScorer()
    r = _MockRaport(kierunek="NEUTRAL")
    wynik = scorer.ocen(r)
    assert wynik.bet_size == 0.0


def test_scorer_przed_treningiem_passthrough():
    """Przed 10 próbkami → bet_size = pewnosc_agregatu."""
    scorer = MetaLabelingScorer()
    r = _MockRaport(kierunek="LONG", pewnosc=0.72)
    wynik = scorer.ocen(r)
    assert not wynik.wyuczony
    assert abs(wynik.bet_size - 0.72) < 1e-6


def test_scorer_zakres_bet_size():
    """bet_size zawsze ∈ [0, 1]."""
    scorer = MetaLabelingScorer()
    # Trenuj trochę
    r = _MockRaport(kierunek="LONG")
    for _ in range(15):
        scorer.zaktualizuj(r, zysk=True)
    wynik = scorer.ocen(r)
    assert 0.0 <= wynik.bet_size <= 1.0


def test_scorer_zakaz_trenowania_neutral():
    """zaktualizuj() ignoruje NEUTRAL."""
    scorer = MetaLabelingScorer()
    r = _MockRaport(kierunek="NEUTRAL")
    scorer.zaktualizuj(r, zysk=True)
    assert scorer.liczba_prob == 0


def test_scorer_zakaz_trenowania_weto():
    scorer = MetaLabelingScorer()
    r = _MockRaport(weto=True)
    scorer.zaktualizuj(r, zysk=False)
    assert scorer.liczba_prob == 0


def test_scorer_trening_zwieksza_prob():
    scorer = MetaLabelingScorer()
    r = _MockRaport(kierunek="LONG")
    scorer.zaktualizuj(r, zysk=True)
    scorer.zaktualizuj(r, zysk=False)
    assert scorer.liczba_prob == 2


def test_scorer_diagnostyka_klucze():
    scorer = MetaLabelingScorer()
    d = scorer.diagnostyka()
    assert "wyuczony" in d
    assert "liczba_prob" in d
    assert "wagi" in d
    assert "bias" in d
    assert len(d["wagi"]) == 6


def test_scorer_min_max_bet_clamping():
    """min_bet/max_bet ograniczają zakres."""
    scorer = MetaLabelingScorer(min_bet=0.2, max_bet=0.8)
    r = _MockRaport(kierunek="LONG", pewnosc=0.05)  # bardzo niska pewność
    wynik = scorer.ocen(r)
    assert wynik.bet_size >= 0.2


def test_scorer_long_short_symetria():
    """Scorer działa równie dobrze dla SHORT."""
    scorer = MetaLabelingScorer()
    r = _MockRaport(kierunek="SHORT", pewnosc=0.65, sl=0.2, ss=0.8)
    wynik = scorer.ocen(r)
    assert isinstance(wynik, WynikMeta)
    assert 0.0 <= wynik.bet_size <= 1.0
