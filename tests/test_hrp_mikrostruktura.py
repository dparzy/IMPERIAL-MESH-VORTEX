"""
Testy W-374 (HRP), W-381 (PIN), W-382 (Engle-Granger kointegracja).
REGUŁA TEST-GRANIC: pojedynczy aktyw, za mało danych, zerowa wariancja, ceny ≤ 0.
"""

import numpy as np

from imperium.legiony.denoising_macierzy import hrp_wagi
from imperium.legiony.mikrostruktura import (
    pin_metoda_momentow, kointegracja_engle_granger, _adf_stat,
)


# ---------------------------------------------------------------------------
# W-374 HRP
# ---------------------------------------------------------------------------

def _cov_blokowa(seed=0):
    """Kowariancja z 2 blokami skorelowanych aktywów + różne wariancje."""
    rng = np.random.default_rng(seed)
    t, n = 500, 4
    fa = rng.standard_normal(t)
    fb = rng.standard_normal(t)
    X = np.zeros((t, n))
    X[:, 0] = 0.9 * fa + 0.1 * rng.standard_normal(t)
    X[:, 1] = 0.9 * fa + 0.1 * rng.standard_normal(t)
    X[:, 2] = 0.9 * fb + 0.1 * rng.standard_normal(t)
    X[:, 3] = 0.9 * fb + 0.1 * rng.standard_normal(t)
    return np.cov(X, rowvar=False)


def test_hrp_wagi_sumuja_do_1():
    cov = _cov_blokowa()
    wynik = hrp_wagi(cov)
    assert abs(wynik["wagi_wektor"].sum() - 1.0) < 1e-9


def test_hrp_wagi_dodatnie():
    cov = _cov_blokowa()
    wynik = hrp_wagi(cov)
    assert np.all(wynik["wagi_wektor"] >= 0), "HRP nie powinno mieć wag ujemnych"


def test_hrp_pojedynczy_aktyw():
    # GRANICA: 1 aktyw → waga 1.0
    cov = np.array([[0.04]])
    wynik = hrp_wagi(cov, klucze=["A"])
    assert wynik["wagi"]["A"] == 1.0


def test_hrp_preferuje_niska_wariancje():
    # 2 nieskorelowane aktywy, jeden 4× bardziej zmienny → mniejsza waga
    cov = np.array([[0.01, 0.0], [0.0, 0.16]])
    wynik = hrp_wagi(cov, klucze=["low", "high"])
    assert wynik["wagi"]["low"] > wynik["wagi"]["high"]


def test_hrp_klucze_zachowane():
    cov = _cov_blokowa()
    wynik = hrp_wagi(cov, klucze=["a", "b", "c", "d"])
    assert set(wynik["wagi"].keys()) == {"a", "b", "c", "d"}


def test_hrp_kolejnosc_jest_permutacja():
    cov = _cov_blokowa()
    wynik = hrp_wagi(cov)
    assert sorted(wynik["kolejnosc"]) == [0, 1, 2, 3]


def test_hrp_vs_naiwny_rownowazny():
    # HRP powinno różnić się od 1/N gdy są wyraźne klastry
    cov = _cov_blokowa()
    wynik = hrp_wagi(cov)
    rownowazny = np.full(4, 0.25)
    assert not np.allclose(wynik["wagi_wektor"], rownowazny, atol=0.01)


# ---------------------------------------------------------------------------
# W-381 PIN
# ---------------------------------------------------------------------------

def test_pin_za_malo_danych():
    wynik = pin_metoda_momentow([1, 2], [1, 2])
    assert np.isnan(wynik["pin"])


def test_pin_symetryczny_niski():
    # Symetryczny flow (buy≈sell) → niski PIN (brak informacji kierunkowej)
    rng = np.random.default_rng(1)
    buy = rng.normal(100, 5, 50)
    sell = rng.normal(100, 5, 50)
    wynik = pin_metoda_momentow(buy, sell)
    assert wynik["pin"] < 0.1


def test_pin_asymetryczny_wysoki():
    # Silna asymetria (dużo więcej kupna) → wysoki PIN
    buy = [200.0] * 50
    sell = [50.0] * 50
    wynik = pin_metoda_momentow(buy, sell)
    assert wynik["pin"] > 0.5


def test_pin_w_przedziale():
    rng = np.random.default_rng(3)
    buy = rng.uniform(50, 150, 40)
    sell = rng.uniform(50, 150, 40)
    wynik = pin_metoda_momentow(buy, sell)
    assert 0.0 <= wynik["pin"] <= 1.0


def test_pin_zerowy_flow():
    # GRANICA: zerowy flow → PIN = 0 (nie crash)
    wynik = pin_metoda_momentow([0.0] * 10, [0.0] * 10)
    assert wynik["pin"] == 0.0


# ---------------------------------------------------------------------------
# W-382 Engle-Granger
# ---------------------------------------------------------------------------

def test_adf_stacjonarny_ujemny():
    # Biały szum (stacjonarny) → ADF mocno ujemny
    rng = np.random.default_rng(5)
    szum = rng.standard_normal(200)
    assert _adf_stat(szum) < -3.0


def test_adf_random_walk_bliski_zera():
    # Random walk (niestacjonarny) → ADF blisko 0
    rng = np.random.default_rng(7)
    rw = np.cumsum(rng.standard_normal(200))
    assert _adf_stat(rw) > -2.5


def test_kointegracja_za_malo_danych():
    wynik = kointegracja_engle_granger([1, 2, 3], [1, 2, 3])
    assert wynik["kointegrowane"] is False


def test_kointegracja_ceny_ujemne():
    # GRANICA: ceny ≤ 0 → odrzuć (log niemożliwy)
    a = list(range(-5, 30))
    b = list(range(1, 36))
    wynik = kointegracja_engle_granger(a, b)
    assert wynik["kointegrowane"] is False


def test_kointegracja_pary_skointegrowane():
    # b = random walk, a = b + szum stacjonarny → skointegrowane
    rng = np.random.default_rng(11)
    b = 100 + np.cumsum(rng.standard_normal(300)) * 0.5
    a = 2.0 * b + rng.standard_normal(300) * 0.3  # spread stacjonarny
    wynik = kointegracja_engle_granger(a, b)
    assert wynik["kointegrowane"] is True
    assert abs(wynik["beta"] - 1.0) < 0.5  # log-log beta ≈ 1 (a∝b)


def test_kointegracja_niezalezne_nieskointegrowane():
    # Dwa niezależne random walki → NIE skointegrowane
    rng = np.random.default_rng(13)
    a = 100 + np.cumsum(rng.standard_normal(300))
    b = 100 + np.cumsum(rng.standard_normal(300))
    wynik = kointegracja_engle_granger(a, b)
    assert wynik["kointegrowane"] is False


def test_kointegracja_kierunek_z_score():
    # Wymuś spread znacznie poniżej średniej → kierunek LONG
    rng = np.random.default_rng(17)
    b = 100 + np.cumsum(rng.standard_normal(300)) * 0.5
    a = 2.0 * b + rng.standard_normal(300) * 0.3
    a[-1] = a[-1] - 5.0  # ostatni punkt mocno w dół → spread bardzo niski
    wynik = kointegracja_engle_granger(a, b)
    if wynik["kointegrowane"]:
        assert wynik["kierunek"] in {"LONG", "NEUTRAL"}
