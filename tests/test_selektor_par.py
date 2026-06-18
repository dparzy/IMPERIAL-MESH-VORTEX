"""
🧪 Testy SelektorPar (W-330) — auto-dobór par LIVE. Wszystkie OFFLINE (mock loader).
Prawo XXI (Test-Granic): brak sieci, brak płynnych, dekorelacja, BTC kotwica, ranking.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from imperium.koloseum.selektor_par import SelektorPar, _korelacja, _zwroty


class MockLoader:
    """Loader bez sieci: predefiniowane pary, obroty i serie close."""
    def __init__(self, pary=None, obroty=None, serie=None):
        self._pary = pary or []
        self._obroty = obroty or {}      # symbol -> obrot_usd
        self._serie = serie or {}        # symbol -> list[close]

    def lista_par_rynku(self, quote="USDT", typ="swap"):
        return list(self._pary)

    def filtruj_plynne(self, pary, min_obrot_usd=5_000_000.0, limit=None):
        out = [{"symbol": s, "obrot_usd": self._obroty.get(s, 0.0), "cena": 100.0}
               for s in pary if self._obroty.get(s, 0.0) >= min_obrot_usd]
        out.sort(key=lambda x: x["obrot_usd"], reverse=True)
        return out[:limit] if limit else out

    def fetch(self, symbol, timeframe="4h", limit=200):
        return pd.DataFrame({"close": self._serie.get(symbol, [100.0] * 10)})


def test_brak_sieci_pusty_ranking():
    """Prawo XV: brak par z rynku → pusty ranking (nie crash)."""
    sel = SelektorPar(MockLoader(pary=[]))
    assert sel.ranking() == []
    assert sel.wybierz() == []


def test_brak_plynnych_pusty():
    """Wszystkie pary poniżej progu obrotu → pusty wynik."""
    loader = MockLoader(pary=["X/USDT:USDT"], obroty={"X/USDT:USDT": 1000.0})
    sel = SelektorPar(loader)
    assert sel.ranking(min_obrot_usd=5_000_000) == []


def test_plynnosc_filtruje_cienkie():
    """Para z dużym obrotem przechodzi, cienka odpada."""
    loader = MockLoader(
        pary=["BIG/USDT:USDT", "THIN/USDT:USDT"],
        obroty={"BIG/USDT:USDT": 50e6, "THIN/USDT:USDT": 100.0},
        serie={"BIG/USDT:USDT": [100, 101, 102, 103, 104, 105],
               "BTC/USDT:USDT": [100, 101, 102, 103, 104, 105]},
    )
    sel = SelektorPar(loader)
    syms = sel.wybierz(top_n=5, min_obrot_usd=5_000_000)
    assert "BIG/USDT:USDT" in syms
    assert "THIN/USDT:USDT" not in syms


def test_dekorelacja_premiowana():
    """Przy równym obrocie wygrywa para mniej skorelowana z BTC (alfa)."""
    btc = [100 + i for i in range(20)]                      # rosnący trend
    skorelowana = [200 + 2 * i for i in range(20)]          # idealnie skorelowana (+1)
    zdekorelowana = [100 + (5 if i % 2 else -5) for i in range(20)]  # piła — niska korelacja
    loader = MockLoader(
        pary=["BTC/USDT:USDT", "COPY/USDT:USDT", "INDEP/USDT:USDT"],
        obroty={"BTC/USDT:USDT": 100e6, "COPY/USDT:USDT": 50e6, "INDEP/USDT:USDT": 50e6},
        serie={"BTC/USDT:USDT": btc, "COPY/USDT:USDT": skorelowana,
               "INDEP/USDT:USDT": zdekorelowana},
    )
    sel = SelektorPar(loader)
    rank = sel.ranking(top_n=3, min_obrot_usd=1e6)
    # INDEP (zdekorelowana) musi mieć wyższy score niż COPY (przy równym obrocie)
    score = {k.symbol: k.score for k in rank}
    assert score["INDEP/USDT:USDT"] > score["COPY/USDT:USDT"]


def test_btc_kotwica_bez_kary():
    """BTC vs sam siebie: korelacja None, dekor=1.0 (nie karzemy kotwicy koszyka)."""
    loader = MockLoader(
        pary=["BTC/USDT:USDT"],
        obroty={"BTC/USDT:USDT": 100e6},
        serie={"BTC/USDT:USDT": [100, 101, 102, 103, 104, 105]},
    )
    sel = SelektorPar(loader)
    rank = sel.ranking(top_n=1, min_obrot_usd=1e6)
    assert rank[0].symbol == "BTC/USDT:USDT"
    assert rank[0].korelacja_btc is None


def test_top_n_ucina():
    """top_n ogranicza liczbę zwróconych par."""
    pary = [f"P{i}/USDT:USDT" for i in range(10)]
    obroty = {s: (10 + i) * 1e6 for i, s in enumerate(pary)}
    serie = {s: [100 + j for j in range(10)] for s in pary}
    serie["BTC/USDT:USDT"] = [100 + j for j in range(10)]
    sel = SelektorPar(MockLoader(pary=pary, obroty=obroty, serie=serie))
    assert len(sel.wybierz(top_n=3, min_obrot_usd=1e6)) == 3


def test_korelacja_pomocnicza_granice():
    """_korelacja: za krótkie → None, idealna → ~1, antykorelacja → ~-1."""
    assert _korelacja([1, 2], [1, 2]) is None              # < 5 pkt
    k = _korelacja([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
    assert k is not None and k > 0.99
    k2 = _korelacja([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert k2 is not None and k2 < -0.99


def test_zwroty_pomija_zera():
    """_zwroty: poprawnie liczy proste zwroty, pomija zerowe mianowniki."""
    z = _zwroty([100, 110, 99])
    assert len(z) == 2
    assert abs(z[0] - 0.10) < 1e-9
