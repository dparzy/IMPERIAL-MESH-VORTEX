"""Testy KalibratorKonformalny (ACI) — kwantyl, przedział, adaptacja, granice."""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from imperium.legiony.kalibrator_konformalny import KalibratorKonformalny


# ── konstrukcja / walidacja ──────────────────────────────────────────────────

def test_cel_pokrycia_poza_zakresem_rzuca():
    for zly in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError):
            KalibratorKonformalny(cel_pokrycia=zly)


def test_okno_i_gamma_walidacja():
    with pytest.raises(ValueError):
        KalibratorKonformalny(okno=0)
    with pytest.raises(ValueError):
        KalibratorKonformalny(gamma=0)


# ── kwantyl: granice ─────────────────────────────────────────────────────────

def test_kwantyl_bez_danych_inf():
    k = KalibratorKonformalny()
    assert k.kwantyl() == math.inf


def test_kwantyl_alpha_zero_inf_przy_skonczonej_probie():
    k = KalibratorKonformalny()
    for s in (0.1, 0.2, 0.3):
        k.dodaj_score(s)
    assert k.kwantyl(alpha=0.0) == math.inf   # 100% pokrycia niegwarantowalne


def test_kwantyl_alpha_jeden_zero():
    k = KalibratorKonformalny()
    for s in (0.1, 0.2, 0.3):
        k.dodaj_score(s)
    assert k.kwantyl(alpha=1.0) == 0.0


def test_kwantyl_znany_order_statistic():
    # 9 scoresów 0.1..0.9, alpha=0.1 → ranga=ceil(10*0.9)=9 → 9. order stat = 0.9
    k = KalibratorKonformalny(okno=100)
    for i in range(1, 10):
        k.dodaj_score(i / 10.0)
    assert abs(k.kwantyl(alpha=0.1) - 0.9) < 1e-9
    # alpha=0.5 → ranga=ceil(10*0.5)=5 → 5. order stat = 0.5
    assert abs(k.kwantyl(alpha=0.5) - 0.5) < 1e-9


def test_kwantyl_uzywa_wartosci_bezwzglednej():
    k = KalibratorKonformalny(okno=10)
    k.dodaj_score(-0.4)   # |−0.4| = 0.4
    k.dodaj_score(0.2)
    assert k.kwantyl(alpha=0.5) in (0.2, 0.4)   # jeden z order-stats, nieujemny
    assert all(s >= 0 for s in k._scores)


# ── przedział / pokrycie ─────────────────────────────────────────────────────

def test_przedzial_symetryczny_wokol_punktu():
    k = KalibratorKonformalny(okno=10)
    for s in (0.1, 0.2, 0.3):
        k.dodaj_score(s)
    d, g = k.przedzial(5.0, alpha=0.5)   # n=3 → skończony kwantyl (0.2)
    assert d < 5.0 < g and abs((g - 5.0) - (5.0 - d)) < 1e-9


def test_pokryty_true_false():
    k = KalibratorKonformalny(okno=10)
    for s in (0.1, 0.2, 0.3):
        k.dodaj_score(s)
    # q(alpha=0.1)=inf-ish? n=3 → ranga=ceil(4*0.9)=4>3 → inf → wszystko pokryte
    assert k.pokryty(0.0, 100.0, alpha=0.1)
    # alpha=0.5 → ranga=ceil(4*0.5)=2 → order stat 0.2 → wąsko
    assert k.pokryty(0.0, 0.15, alpha=0.5)
    assert not k.pokryty(0.0, 0.9, alpha=0.5)


# ── adaptacja ACI ────────────────────────────────────────────────────────────

def test_krok_miss_obniza_alpha_hit_podnosi():
    k = KalibratorKonformalny(cel_pokrycia=0.9, gamma=0.05)
    a0 = k.alpha_t
    k.krok(pokryty=False)          # miss → alpha maleje (szerszy przedział)
    assert k.alpha_t < a0
    a1 = k.alpha_t
    k.krok(pokryty=True)           # hit → alpha rośnie
    assert k.alpha_t > a1


def test_alpha_t_zawsze_w_zakresie():
    k = KalibratorKonformalny(cel_pokrycia=0.9, gamma=0.9)
    for _ in range(50):
        k.krok(pokryty=False)
    assert 0.0 <= k.alpha_t <= 1.0
    for _ in range(50):
        k.krok(pokryty=True)
    assert 0.0 <= k.alpha_t <= 1.0


def test_dlugofalowe_pokrycie_zbiega_do_celu():
    """Deterministyczny strumień → empiryczne pokrycie ≈ cel (split conformal)."""
    k = KalibratorKonformalny(cel_pokrycia=0.9, okno=200, gamma=0.02)
    # deterministyczny „szum": powtarzalna sekwencja błędów o rozpiętości 0..0.99
    seq = [((i * 37) % 100) / 100.0 for i in range(1, 401)]
    for s in seq[:150]:               # rozgrzewka koszyka scores
        k.dodaj_score(s)
    pokryte = 0
    prob = 0
    for s in seq[150:]:
        # punkt predykcji 0, „prawda" = błąd o znaku zależnym od indeksu
        prawda = s if (prob % 2 == 0) else -s
        if k.pokryty(0.0, prawda):
            pokryte += 1
        k.krok(k.pokryty(0.0, prawda))
        k.dodaj_score(prawda)
        prob += 1
    pokrycie = pokryte / prob
    assert 0.80 <= pokrycie <= 1.0    # w okolicy celu 0.9 (tolerancja na skończoną próbę)


def test_obserwuj_cykl_dziala():
    k = KalibratorKonformalny(okno=50)
    for s in (0.1, 0.2, 0.3, 0.15):
        k.dodaj_score(s)
    przed = k.n
    czy = k.obserwuj(0.0, 0.1)
    assert isinstance(czy, bool) and k.n == przed + 1
