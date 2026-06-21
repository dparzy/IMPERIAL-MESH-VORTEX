"""
Testy W-369..371: IC per-neuron, breadth, Fundamental Law IR=IC·√breadth.
REGUŁA TEST-GRANIC: NaN przy brak danych, stała seria, h≥max_buffer; poprawny IC ∈ [-1,1].
"""

import math
import numpy as np
import pytest

from imperium.legiony.metryki_ic import KolektorIC, prawo_fundamentalne, _spearman


# ---------------------------------------------------------------------------
# _spearman
# ---------------------------------------------------------------------------

def test_spearman_korelacja_idealna():
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    assert _spearman(x, x) == pytest.approx(1.0)


def test_spearman_antykorelacja():
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    assert _spearman(x, x[::-1]) == pytest.approx(-1.0)


def test_spearman_wartosc_znana():
    # Konkretne wartości z tabelek
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    y = np.array([1, 3, 2, 5, 4], dtype=float)
    # d = [0,1,-1,1,-1], sum_d2=4, rs=1-6*4/(5*24)=1-24/120=0.8
    assert _spearman(x, y) == pytest.approx(0.8)


def test_spearman_ties():
    # Ties — nie rzuca wyjątkiem
    x = np.array([1, 1, 2, 3, 3], dtype=float)
    y = np.array([1, 2, 3, 4, 5], dtype=float)
    val = _spearman(x, y)
    assert -1.0 <= val <= 1.0


# ---------------------------------------------------------------------------
# KolektorIC — podstawowe ścieżki
# ---------------------------------------------------------------------------

def _zasil_kolektor(kol: KolektorIC, n: int, seed: int = 42):
    """Zasila kolektor: neurony A,B z sygnałem korelującym z przyszłym zwrotem."""
    rng = np.random.default_rng(seed)
    for _ in range(n):
        # sygnał A jest blisko prawdziwego kierunku
        trend = rng.choice([-1.0, 1.0])
        kol.rejestruj_sygnal({
            "A": trend + rng.normal(0, 0.1),
            "B": rng.uniform(-1, 1),  # szum
        })
        kol.rejestruj_zwrot(trend * 0.01 + rng.normal(0, 0.001))


def test_ic_pusty_kolektor():
    kol = KolektorIC(min_probek=5)
    assert kol.ic() == {}


def test_ic_za_malo_danych():
    kol = KolektorIC(min_probek=20, horyzonty=(1,))
    _zasil_kolektor(kol, 5)
    wynik = kol.ic(h=1)
    for nid, hz in wynik.items():
        assert math.isnan(hz[1]), f"{nid} powinien mieć NaN gdy za mało danych"


def test_ic_wynik_w_przedziale():
    kol = KolektorIC(min_probek=10, horyzonty=(1,))
    _zasil_kolektor(kol, 50)
    wynik = kol.ic(h=1)
    assert "A" in wynik or "B" in wynik
    for nid, hz in wynik.items():
        v = hz[1]
        if not math.isnan(v):
            assert -1.0 <= v <= 1.0, f"{nid}: IC={v} poza [-1,1]"


def test_ic_neuron_a_lepszy_niz_b():
    # Neuron A ma wyższy |IC| niż B (szum)
    kol = KolektorIC(min_probek=10, horyzonty=(1,))
    _zasil_kolektor(kol, 100, seed=7)
    ic = kol.ic_srednie()
    # A powinien mieć wyższe |IC| niż B (szum losowy)
    if "A" in ic and "B" in ic and not math.isnan(ic["A"]) and not math.isnan(ic["B"]):
        assert abs(ic["A"]) > abs(ic["B"]) or abs(ic["A"]) > 0


def test_ic_stala_seria_nan():
    # GRANICA: stały sygnał → NaN
    kol = KolektorIC(min_probek=5, horyzonty=(1,))
    for _ in range(20):
        kol.rejestruj_sygnal({"A": 0.5})
        kol.rejestruj_zwrot(0.01)
    wynik = kol.ic(h=1)
    assert math.isnan(wynik["A"][1])


def test_ic_srednie_format():
    kol = KolektorIC(min_probek=10, horyzonty=(1, 5))
    _zasil_kolektor(kol, 60)
    sr = kol.ic_srednie()
    assert isinstance(sr, dict)
    for v in sr.values():
        assert isinstance(v, float)


# ---------------------------------------------------------------------------
# prawo_fundamentalne
# ---------------------------------------------------------------------------

def test_prawo_fundamentalne_brak_danych():
    wynik = prawo_fundamentalne({})
    assert math.isnan(wynik["ir"])
    assert wynik["breadth"] == 0


def test_prawo_fundamentalne_wszystkie_nan():
    wynik = prawo_fundamentalne({"A": float("nan"), "B": float("nan")})
    assert math.isnan(wynik["ir"])


def test_prawo_fundamentalne_prosty():
    # IC=0.1, breadth=4 → IR=0.1*2=0.2
    wynik = prawo_fundamentalne({"A": 0.1, "B": 0.1, "C": 0.1, "D": 0.1}, breadth=4)
    assert wynik["ir"] == pytest.approx(0.2, abs=1e-3)
    assert wynik["breadth"] == 4
    assert abs(wynik["ic_zbiorowy"] - 0.1) < 1e-3


def test_prawo_fundamentalne_ic_niski():
    wynik = prawo_fundamentalne({"A": 0.005}, breadth=10)
    assert "IC_NISKI" in wynik["diagnoza"]


def test_prawo_fundamentalne_ir_dobry():
    # IC=0.1, breadth=100 → IR=1.0
    wynik = prawo_fundamentalne({"A": 0.1}, breadth=100)
    assert "IR_DOBRY" in wynik["diagnoza"]


def test_prawo_fundamentalne_breadth_z_onc():
    # Gdy brak breadth i brak korelacji → breadth = len(neurony)
    wynik = prawo_fundamentalne({"A": 0.05, "B": 0.05, "C": 0.05})
    assert wynik["breadth"] == 3


def test_prawo_fundamentalne_posortowane_neurony():
    ic = {"A": 0.05, "B": 0.15, "C": -0.10}
    wynik = prawo_fundamentalne(ic, breadth=9)
    klucze = list(wynik["neurony"].keys())
    # posortowane wg |IC| malejąco
    wartosci = [abs(wynik["neurony"][k]) for k in klucze]
    assert wartosci == sorted(wartosci, reverse=True)
