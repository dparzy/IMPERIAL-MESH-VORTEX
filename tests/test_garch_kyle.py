"""
Testy W-376 (GJR-GARCH) + W-380 (Kyle's Lambda) + OC-06..08 (BTC on-chain deterministyczne).
REGUŁA TEST-GRANIC: za mało barów, stałe zwroty, zero wolumenu, block_height=0.
"""

import numpy as np
import pytest

from imperium.legiony.zwiadowcy.exp_garch import ZwiadowcaGARCH, _fit_gjr_garch, _rekurencja_gjr
from imperium.legiony.zwiadowcy.exp_kyle_lambda import ZwiadowcaKyleLambda, _ols_slope
from imperium.legiony.neurony.onchain import (
    NeuronS2F, NeuronDaysToHalving, NeuronBTCSupplyInflation, _info_bloku,
)


# ---------------------------------------------------------------------------
# Pomocnicze: generatory barów
# ---------------------------------------------------------------------------

def _bary(n: int, vol_scale: float = 0.01, seed: int = 42) -> list:
    rng = np.random.default_rng(seed)
    price = 50000.0
    bary = []
    for _ in range(n):
        ret = rng.normal(0, vol_scale)
        open_ = price
        close = price * (1 + ret)
        high = max(open_, close) * (1 + abs(rng.normal(0, 0.002)))
        low = min(open_, close) * (1 - abs(rng.normal(0, 0.002)))
        vol = abs(rng.normal(100, 20))
        bary.append({"open": open_, "high": high, "low": low,
                     "close": close, "volume": vol, "timestamp": len(bary)})
        price = close
    return bary


def _bary_stale(n: int) -> list:
    return [{"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0,
             "volume": 0.0, "timestamp": i} for i in range(n)]


# ---------------------------------------------------------------------------
# GARCH engine
# ---------------------------------------------------------------------------

def test_rekurencja_gjr_dlugosc():
    a = np.array([0.01, -0.02, 0.03, -0.01, 0.02])
    s2 = _rekurencja_gjr(a, 1e-5, 0.10, 0.85, 0.05)
    assert len(s2) == len(a)
    assert all(v > 0 for v in s2)


def test_rekurencja_gjr_persistence():
    a = np.random.default_rng(7).normal(0, 0.01, 100)
    s2 = _rekurencja_gjr(a, 1e-5, 0.10, 0.85, 0.05)
    # persistence = a1 + b1 = 0.95 < 1 → wariancja skońcona
    assert np.all(np.isfinite(s2))


def test_fit_gjr_garch_zwraca_sigma():
    rng = np.random.default_rng(99)
    returns = rng.normal(0, 0.015, 100)
    wynik = _fit_gjr_garch(returns)
    assert 0 < wynik["sigma_next"] < 1.0
    assert 0 < wynik["sigma_current"] < 1.0
    assert 0 < wynik["persistence"] < 1.0


def test_fit_gjr_garch_persistence_ponizej_1():
    # GRANICA: α₁+β₁ musi być < 1 (stacjonarność)
    rng = np.random.default_rng(11)
    returns = rng.normal(0, 0.01, 80)
    wynik = _fit_gjr_garch(returns)
    assert wynik["persistence"] < 1.0, "GARCH niestacjonarny!"


# ---------------------------------------------------------------------------
# ZwiadowcaGARCH
# ---------------------------------------------------------------------------

def test_garch_za_malo_barow():
    z = ZwiadowcaGARCH()
    r = z.analizuj(_bary(20))
    assert r.sygnal.kierunek == "NEUTRAL"
    assert r.sygnal.pewnosc == 0.0


def test_garch_dosc_barow_zwraca_sygnal():
    z = ZwiadowcaGARCH()
    r = z.analizuj(_bary(80))
    assert r.sygnal.kierunek in {"LONG", "SHORT", "NEUTRAL"}
    assert 0.0 <= r.sygnal.pewnosc <= 1.0
    assert "sigma_next" in r.diagnostics


def test_garch_wysoka_vol_short():
    # Ekstremalna zmienność → SHORT
    z = ZwiadowcaGARCH()
    bary = _bary(80, vol_scale=0.10)  # 10% per bar — skrajne
    r = z.analizuj(bary)
    assert r.sygnal.kierunek == "SHORT"


def test_garch_stale_ceny_neutral():
    # GRANICA: stałe ceny → stałe zwroty 0 → sigma→0 → LONG (niska vol)
    z = ZwiadowcaGARCH()
    r = z.analizuj(_bary_stale(80))
    assert r.sygnal.kierunek in {"LONG", "NEUTRAL"}


def test_garch_klucz_kategoria():
    z = ZwiadowcaGARCH()
    assert z.KLUCZ == "EXP-13"
    assert z.KATEGORIA == "V"
    assert z.ELITARNY is True


# ---------------------------------------------------------------------------
# Kyle's Lambda
# ---------------------------------------------------------------------------

def test_ols_slope_idealna():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = 2.5 * x
    assert _ols_slope(x, y) == pytest.approx(2.5, rel=1e-5)


def test_ols_slope_za_malo():
    assert np.isnan(_ols_slope(np.array([1.0]), np.array([2.0])))


def test_kyle_za_malo_barow():
    z = ZwiadowcaKyleLambda()
    r = z.analizuj(_bary(10))
    assert r.sygnal.kierunek == "NEUTRAL"
    assert r.sygnal.pewnosc == 0.0


def test_kyle_dosc_barow():
    z = ZwiadowcaKyleLambda()
    r = z.analizuj(_bary(50))
    assert r.sygnal.kierunek in {"LONG", "SHORT", "NEUTRAL"}
    assert "kyle_lambda" in r.diagnostics


def test_kyle_zero_wolumen_fallback():
    # GRANICA: zero wolumenu → brak danych → neutral
    z = ZwiadowcaKyleLambda()
    bary = [{"open": 1.0, "high": 1.0, "low": 1.0, "close": float(1 + i * 0.001),
              "volume": 0.0, "timestamp": i} for i in range(40)]
    r = z.analizuj(bary)
    assert r.sygnal.kierunek == "NEUTRAL"


def test_kyle_klucz_kategoria():
    z = ZwiadowcaKyleLambda()
    assert z.KLUCZ == "EXP-14"
    assert z.KATEGORIA == "L"


# ---------------------------------------------------------------------------
# _info_bloku (BTC deterministyczne)
# ---------------------------------------------------------------------------

def test_info_bloku_genesis():
    info = _info_bloku(0)
    assert info["nagroda_blokowa"] == 50.0
    assert info["s2f"] == 0.0  # brak podaży przed pierwszym blokiem


def test_info_bloku_po_4_halvingu():
    # blok 900_000 → po 4. halvingu (840_000) → nagroda = 3.125
    info = _info_bloku(900_000)
    assert info["nagroda_blokowa"] == 3.125
    assert info["s2f"] > 100  # bardzo wysoki S2F


def test_info_bloku_przed_halvingiem():
    # blok 839_000 → przed 4. halvingiem → nagroda = 6.25
    info = _info_bloku(839_000)
    assert info["nagroda_blokowa"] == 6.25
    assert info["dni_do_halvingu"] > 0
    assert info["bloki_do_halvingu"] == 1000


def test_info_bloku_s2f_rosnie_po_halvingu():
    s2f_przed = _info_bloku(839_000)["s2f"]
    s2f_po = _info_bloku(841_000)["s2f"]
    assert s2f_po > s2f_przed


# ---------------------------------------------------------------------------
# NeuronS2F
# ---------------------------------------------------------------------------

def test_neuron_s2f_brak_block_height():
    n = NeuronS2F()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_neuron_s2f_po_halvingu_long():
    n = NeuronS2F()
    s = n.interpretuj({"BTC_BLOCK_HEIGHT": 900_000})
    assert s.kierunek == "LONG"
    assert s.wartosc > 100


# ---------------------------------------------------------------------------
# NeuronDaysToHalving
# ---------------------------------------------------------------------------

def test_neuron_halving_brak():
    n = NeuronDaysToHalving()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"


def test_neuron_halving_blisko():
    # Blok 839_950 → ~50 dni do halvingu 840_000
    n = NeuronDaysToHalving()
    s = n.interpretuj({"BTC_BLOCK_HEIGHT": 839_650})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.60


def test_neuron_halving_daleko():
    # Blok 640_000 → ~1400 dni do kolejnego halvingu
    n = NeuronDaysToHalving()
    s = n.interpretuj({"BTC_BLOCK_HEIGHT": 640_000})
    assert s.kierunek == "NEUTRAL"


# ---------------------------------------------------------------------------
# NeuronBTCSupplyInflation
# ---------------------------------------------------------------------------

def test_supply_inflation_brak():
    n = NeuronBTCSupplyInflation()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"


def test_supply_inflation_po_halvingu_long():
    n = NeuronBTCSupplyInflation()
    s = n.interpretuj({"BTC_BLOCK_HEIGHT": 900_000})
    assert s.kierunek == "LONG"  # inflacja < 1% → LONG


def test_supply_inflation_wczesna_faza_neutral():
    # Blok 100_000: reward=50 BTC, inflacja ~5% → NEUTRAL
    n = NeuronBTCSupplyInflation()
    s = n.interpretuj({"BTC_BLOCK_HEIGHT": 100_000})
    assert s.kierunek == "NEUTRAL"
