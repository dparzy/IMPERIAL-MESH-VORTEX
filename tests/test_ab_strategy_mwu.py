"""Testy harnessu A/B strategy-MWU (narzedzia/ab_strategy_mwu.py) — guardy areny + metryki."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.ab_strategy_mwu import _metryki, _nota, _rodzaj, _wczytaj_z_areny  # noqa: F401


class _FakeStats:
    def __init__(self, kk, tt, wr):
        self.kapital_koncowy, self.kapital_startowy = kk, 10_000.0
        self.total_trades, self.win_rate = tt, wr


class _FakeEngine:
    def __init__(self, s): self._s = s
    def podsumowanie(self): return self._s


def test_metryki_zwrot():
    m = _metryki(_FakeEngine(_FakeStats(11_500.0, 20, 0.55)))
    assert abs(m["ret"] - 0.15) < 1e-9 and m["trades"] == 20


def test_rodzaj_rozdziela_tryby():
    # tryb strategia i filtr mają OSOBNE partycje areny (resume nie miesza)
    assert _rodzaj("strategia") == "ab_strat_mwu_strategia"
    assert _rodzaj("filtr") == "ab_strat_mwu_filtr"
    assert _rodzaj("strategia") != _rodzaj("filtr")


def test_nota_roundtrip():
    w = {"bary": 3000, "ret_off": -0.02, "ret_on": 0.05,
         "tr_off": 30, "tr_on": 28, "wr_off": 0.4, "wr_on": 0.5}
    nota = _nota("Binance_ETHUSDT_4h.csv", w)
    p = dict(kv.split("=", 1) for kv in nota.split(";") if "=" in kv)
    assert float(p["retON"]) == 0.05 and int(p["trOFF"]) == 30 and int(p["bary"]) == 3000
