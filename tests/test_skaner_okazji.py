"""Testy Skanera Okazji (W-316) — ranking cross-symbol, TOP-N, kierunek, granice."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.skaner_okazji import SkanerOkazji, OkazjaRank, _zscore


def _wsk(roc, adx, vol_spike, atr_pct=0.02, lookback=6):
    baza = 100.0
    cena = round(baza * (1 + roc), 6)
    closes = [baza] * lookback + [cena]
    return {
        "CLOSE_SERIES_20": closes,
        "CLOSE": cena,
        "ADX_14": adx,
        "VOLUME": vol_spike * 1000.0,
        "VOLUME_MA20": 1000.0,
        "ATR_14": atr_pct * cena,
    }


# ─── z-score pomocnik ──────────────────────────────────────────────────────────

def test_zscore_pusta():
    assert _zscore([]) == []


def test_zscore_zerowa_wariancja():
    assert _zscore([5.0, 5.0, 5.0]) == [0.0, 0.0, 0.0]


def test_zscore_normalny():
    z = _zscore([1.0, 2.0, 3.0])
    assert abs(z[1]) < 1e-9          # środek = 0
    assert z[0] < 0 < z[2]


# ─── Pusty / brak danych ───────────────────────────────────────────────────────

def test_pusty_koszyk():
    assert SkanerOkazji().skanuj({}) == []


def test_brak_danych_pomijany():
    s = SkanerOkazji()
    rank = s.skanuj({"BTC": {"CLOSE_SERIES_20": [1, 2]}})  # niekompletne
    assert rank == []


def test_chop_odsiany():
    """Moneta z ADX < min_adx (chop) wypada z rankingu (lekcja W-314)."""
    s = SkanerOkazji(min_adx=20.0)
    rank = s.skanuj({"BTC": _wsk(roc=0.10, adx=15, vol_spike=2.0)})
    assert rank == []


# ─── Ranking i kierunek ────────────────────────────────────────────────────────

def test_kierunek_z_momentum():
    s = SkanerOkazji()
    rank = s.skanuj({
        "UP": _wsk(roc=0.10, adx=30, vol_spike=2.0),
        "DN": _wsk(roc=-0.10, adx=30, vol_spike=2.0),
    })
    kier = {o.symbol: o.kierunek for o in rank}
    assert kier["UP"] == "LONG"
    assert kier["DN"] == "SHORT"


def test_top_n_obcina():
    s = SkanerOkazji()
    koszyk = {f"C{i}": _wsk(roc=0.01 * i, adx=25 + i, vol_spike=1.0 + 0.1 * i)
              for i in range(1, 6)}
    rank = s.skanuj(koszyk, top_n=2)
    assert len(rank) == 2


def test_ranking_posortowany_malejaco():
    s = SkanerOkazji()
    koszyk = {f"C{i}": _wsk(roc=0.02 * i, adx=25 + 2 * i, vol_spike=1.0 + 0.2 * i)
              for i in range(1, 5)}
    rank = s.skanuj(koszyk)
    scores = [o.score for o in rank]
    assert scores == sorted(scores, reverse=True)


def test_najmocniejsza_okazja_na_szczycie():
    """Moneta z najwyższym momentum+trend+wolumen powinna być #1."""
    s = SkanerOkazji()
    koszyk = {
        "SLABA": _wsk(roc=0.02, adx=22, vol_spike=1.0),
        "MOCNA": _wsk(roc=0.30, adx=45, vol_spike=4.0),
        "SREDNIA": _wsk(roc=0.10, adx=30, vol_spike=2.0),
    }
    rank = s.skanuj(koszyk)
    assert rank[0].symbol == "MOCNA"


def test_short_okazja_tez_rankowana():
    """Silny spadek (SHORT) z mocnym trendem to też wysoka okazja (|momentum|)."""
    s = SkanerOkazji()
    koszyk = {
        "PLASKA": _wsk(roc=0.01, adx=21, vol_spike=1.0),
        "KRACH": _wsk(roc=-0.35, adx=50, vol_spike=5.0),
    }
    rank = s.skanuj(koszyk)
    assert rank[0].symbol == "KRACH"
    assert rank[0].kierunek == "SHORT"


# ─── Struktura wyniku ──────────────────────────────────────────────────────────

def test_okazja_ma_skladniki():
    s = SkanerOkazji()
    rank = s.skanuj({"A": _wsk(roc=0.1, adx=30, vol_spike=2.0),
                     "B": _wsk(roc=0.2, adx=35, vol_spike=3.0)})
    assert isinstance(rank[0], OkazjaRank)
    for klucz in ("momentum_z", "trend_z", "wolumen_z", "zmiennosc_z"):
        assert klucz in rank[0].skladniki


def test_granica_adx_dokladnie_min_przechodzi():
    """ADX == min_adx → NIE odsiany (warunek < min_adx)."""
    s = SkanerOkazji(min_adx=20.0)
    rank = s.skanuj({"A": _wsk(roc=0.1, adx=20.0, vol_spike=2.0),
                     "B": _wsk(roc=0.2, adx=25.0, vol_spike=2.0)})
    symbole = {o.symbol for o in rank}
    assert "A" in symbole
