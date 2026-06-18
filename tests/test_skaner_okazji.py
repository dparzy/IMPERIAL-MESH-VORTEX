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


# ─── W-324: Brama Momentum Bezwzględnego (TS gate) ────────────────────────────

def test_w324_domyslnie_wylaczona():
    """min_bezwzgledny_ts=0.0 → brama TS wyłączona, zachowanie identyczne jak dotąd."""
    s = SkanerOkazji(min_bezwzgledny_ts=0.0)
    # Słaby ruch 0.001 (0.1%) → powinien przejść przy ADX > min_adx
    rank = s.skanuj({
        "A": _wsk(roc=0.001, adx=25, vol_spike=2.0),
        "B": _wsk(roc=0.002, adx=30, vol_spike=2.0),
    })
    assert len(rank) == 2


def test_w324_dead_market_zero_wejsc():
    """W-324: martwy rynek — wszystkie |ROC| < próg → 0 okazji (suchy proch)."""
    s = SkanerOkazji(min_bezwzgledny_ts=0.01)
    rank = s.skanuj({
        "A": _wsk(roc=0.003, adx=25, vol_spike=2.0),
        "B": _wsk(roc=-0.004, adx=30, vol_spike=2.0),
        "C": _wsk(roc=0.005, adx=28, vol_spike=1.5),
    })
    assert rank == [], f"Oczekiwano 0 okazji, dostano {len(rank)}"


def test_w324_prog_dokładnie_przepuszcza():
    """W-324: |ROC| == próg → przepuszcza (warunek < próg, nie <=)."""
    s = SkanerOkazji(min_bezwzgledny_ts=0.01)
    rank = s.skanuj({
        "NA_GRANICY": _wsk(roc=0.01, adx=25, vol_spike=2.0),
        "PONIZEJ":    _wsk(roc=0.009, adx=25, vol_spike=2.0),
    })
    symbole = {o.symbol for o in rank}
    assert "NA_GRANICY" in symbole, "ROC==próg powinien przejść"
    assert "PONIZEJ" not in symbole, "ROC<próg powinien być odsiany"


def test_w324_selektywny_rynek():
    """W-324: jeden mocny ruch przepuszczony, słabe odsiane."""
    s = SkanerOkazji(min_bezwzgledny_ts=0.02)
    rank = s.skanuj({
        "MOCNY": _wsk(roc=0.05, adx=35, vol_spike=3.0),
        "SLABY1": _wsk(roc=0.01, adx=25, vol_spike=2.0),
        "SLABY2": _wsk(roc=-0.01, adx=28, vol_spike=2.0),
    })
    assert len(rank) == 1
    assert rank[0].symbol == "MOCNY"


def test_w324_krótka_pozycja_ts_gate():
    """W-324: SHORT (ujemne ROC) też podlega bramie — |ROC| < próg → odsiany."""
    s = SkanerOkazji(min_bezwzgledny_ts=0.03)
    rank = s.skanuj({
        "MOCNY_SHORT": _wsk(roc=-0.10, adx=40, vol_spike=3.0),
        "SLABY_SHORT": _wsk(roc=-0.01, adx=30, vol_spike=2.0),
    })
    assert len(rank) == 1
    assert rank[0].symbol == "MOCNY_SHORT"
    assert rank[0].kierunek == "SHORT"
