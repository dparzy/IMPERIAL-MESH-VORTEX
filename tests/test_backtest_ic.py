"""Test pomiaru IC roju w backteście (W-385, Prawo XVI) — bez look-ahead."""

import logging
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest


def _bary_syntetyczne(n=300):
    bary = []
    p = 100.0
    for i in range(n):
        p *= 1 + (0.002 if (i // 20) % 2 == 0 else -0.001)
        bary.append({"open": p * 0.999, "high": p * 1.004, "low": p * 0.996,
                     "close": p, "volume": 1000 + i, "timestamp": 1700000000 + i * 3600,
                     "symbol": "BTCUSDT", "interwal": "4h"})
    return bary


def test_mierz_ic_dolacza_raport():
    eng = backtest("X", "4h", okno=60, bary=_bary_syntetyczne(), mierz_ic=True)
    assert hasattr(eng, "ic_srednie")
    assert hasattr(eng, "ic_pelne")
    assert isinstance(eng.ic_srednie, dict)


def test_mierz_ic_obejmuje_news_neurony():
    """NEWS-01..04 są śledzone przez kolektor (dostaną IC gdy będzie feed)."""
    eng = backtest("X", "4h", okno=60, bary=_bary_syntetyczne(), mierz_ic=True)
    news = [k for k in eng.ic_srednie if k.startswith("NEWS")]
    assert "NEWS-01" in news and "NEWS-04" in news


def test_bez_mierz_ic_brak_raportu():
    """Domyślnie (mierz_ic=False) — zero narzutu, brak atrybutu IC."""
    eng = backtest("X", "4h", okno=60, bary=_bary_syntetyczne(), mierz_ic=False)
    assert not hasattr(eng, "ic_srednie")


def test_ic_wartosci_w_zakresie():
    """IC ∈ [-1, 1] (Spearman) dla zmierzonych neuronów."""
    eng = backtest("X", "4h", okno=60, bary=_bary_syntetyczne(), mierz_ic=True)
    for nid, v in eng.ic_srednie.items():
        if v == v:   # nie-NaN
            assert -1.0 <= v <= 1.0, f"{nid}: IC poza zakresem: {v}"
