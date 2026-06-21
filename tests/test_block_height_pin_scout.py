"""
Testy W-377..379 obudzenie (szacuj_block_height + Budowniczy) + W-383 EXP-15 PIN scout.
REGUŁA TEST-GRANIC: timestamp przed genesis, kotwice halvingów, ekstrapolacja, brak wolumenu.
"""

import numpy as np

from imperium.legiony.neurony.onchain import (
    szacuj_block_height, NeuronS2F, NeuronDaysToHalving, NeuronBTCSupplyInflation,
)
from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
from imperium.legiony.zwiadowcy.exp_pin import ZwiadowcaPIN


# ---------------------------------------------------------------------------
# szacuj_block_height
# ---------------------------------------------------------------------------

def test_block_height_przed_genesis():
    # GRANICA: timestamp przed genesis → block 0
    assert szacuj_block_height(1_000_000_000) == 0


def test_block_height_genesis():
    assert szacuj_block_height(1_231_006_505) == 0


def test_block_height_kotwice_halvingow():
    # Kotwice muszą trafiać dokładnie w znane bloki halvingów
    assert szacuj_block_height(1_354_116_278) == 210_000
    assert szacuj_block_height(1_468_082_773) == 420_000
    assert szacuj_block_height(1_589_225_023) == 630_000
    assert szacuj_block_height(1_713_571_200) == 840_000


def test_block_height_interpolacja_monotoniczna():
    # Wartości muszą rosnąć z czasem
    bh1 = szacuj_block_height(1_400_000_000)
    bh2 = szacuj_block_height(1_500_000_000)
    bh3 = szacuj_block_height(1_700_000_000)
    assert bh1 < bh2 < bh3


def test_block_height_ekstrapolacja_po_2024():
    # Po ostatniej kotwicy: 10 min/blok
    bh = szacuj_block_height(1_713_571_200 + 600 * 1000)  # +1000 bloków
    assert abs(bh - 841_000) < 5


# ---------------------------------------------------------------------------
# Budowniczy wpina BTC_BLOCK_HEIGHT
# ---------------------------------------------------------------------------

def _bary_z_ts(n=60, ts_start=1_748_736_000):
    bary = []
    for i in range(n):
        bary.append({
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5,
            "volume": 1000.0, "timestamp": ts_start + i * 3600,
        })
    return bary


def test_budowniczy_dodaje_block_height():
    b = BudowniczyWskaznikow()
    w = b.zbuduj(_bary_z_ts())
    assert "BTC_BLOCK_HEIGHT" in w
    assert w["BTC_BLOCK_HEIGHT"] > 800_000  # 2025 → po 4. halvingu


def test_budowniczy_block_height_none_bez_ts():
    b = BudowniczyWskaznikow()
    bary = [{"open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]  # bez timestamp
    w = b.zbuduj(bary)
    assert w.get("BTC_BLOCK_HEIGHT") is None


def test_oc06_zywy_przez_budowniczego():
    # Integracja: Budowniczy → OC-06 produkuje sygnał (nie martwy głos)
    b = BudowniczyWskaznikow()
    w = b.zbuduj(_bary_z_ts())
    s = NeuronS2F().interpretuj(w)
    assert s.kierunek in {"LONG", "NEUTRAL"}
    assert s.wartosc is not None  # ma wartość S2F


def test_oc07_oc08_zywe():
    b = BudowniczyWskaznikow()
    w = b.zbuduj(_bary_z_ts())
    s7 = NeuronDaysToHalving().interpretuj(w)
    s8 = NeuronBTCSupplyInflation().interpretuj(w)
    assert s7.wartosc is not None
    assert s8.wartosc is not None


# ---------------------------------------------------------------------------
# EXP-15 PIN scout
# ---------------------------------------------------------------------------

def _bary_pin(n=50, asymetria=0.0, seed=1):
    """asymetria>0 przesuwa close ku high (więcej buy volume)."""
    rng = np.random.default_rng(seed)
    bary = []
    for _ in range(n):
        low = 100.0
        high = 102.0
        # close bliżej high gdy asymetria dodatnia
        pos = np.clip(0.5 + asymetria + rng.normal(0, 0.05), 0.0, 1.0)
        close = low + pos * (high - low)
        bary.append({"open": 101.0, "high": high, "low": low,
                     "close": close, "volume": 1000.0, "timestamp": 0})
    return bary


def test_pin_scout_za_malo_barow():
    z = ZwiadowcaPIN()
    r = z.analizuj(_bary_pin(10))
    assert r.sygnal.kierunek == "NEUTRAL"
    assert r.sygnal.pewnosc == 0.0


def test_pin_scout_symetryczny_niski():
    z = ZwiadowcaPIN()
    r = z.analizuj(_bary_pin(50, asymetria=0.0))
    assert r.sygnal.kierunek == "NEUTRAL"
    assert "pin" in r.diagnostics
    assert r.diagnostics["pin"] < 0.35


def test_pin_scout_asymetryczny_wysoki():
    # Silna asymetria → wysoki PIN → tłumi rój (pewnosc_przeciwnika > 0)
    z = ZwiadowcaPIN()
    r = z.analizuj(_bary_pin(50, asymetria=0.45))
    assert r.diagnostics["pin"] > 0.35
    assert r.sygnal.pewnosc_przeciwnika > 0.0


def test_pin_scout_klucz_kategoria():
    z = ZwiadowcaPIN()
    assert z.KLUCZ == "EXP-15"
    assert z.KATEGORIA == "L"
    assert z.ELITARNY is True


def test_pin_scout_zero_wolumen():
    # GRANICA: zero wolumenu → PIN obliczalny (zerowy flow → PIN=0)
    z = ZwiadowcaPIN()
    bary = [{"open": 1, "high": 1.5, "low": 0.5, "close": 1.0,
             "volume": 0.0, "timestamp": 0} for _ in range(40)]
    r = z.analizuj(bary)
    assert r.sygnal.kierunek == "NEUTRAL"
