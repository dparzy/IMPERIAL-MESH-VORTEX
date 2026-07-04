"""Testy wykresu backtestu (narzedzia/wykres_backtestu.py) — mapowanie trades, EMA."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from types import SimpleNamespace
from narzedzia.wykres_backtestu import trades_z_historii, _ema


def _w(ts_we, bary_trwania, we, wy, pnl):
    return SimpleNamespace(timestamp_wejscia=ts_we, czas_trwania_bar=bary_trwania,
                           cena_wejscia=we, cena_zamkniecia=wy, pnl_usdt=pnl)


def _bary(n=10):
    return [{"timestamp": 1000 + i, "close": 100.0 + i} for i in range(n)]


def test_mapuje_wejscie_i_wyjscie():
    t = trades_z_historii([_w(1002, 3, 102.0, 105.0, 50.0)], _bary())
    assert t == [{"entry_idx": 2, "entry_price": 102.0, "exit_idx": 5,
                  "exit_price": 105.0, "win": True}]


def test_strata_win_false():
    t = trades_z_historii([_w(1001, 2, 101.0, 99.0, -20.0)], _bary())
    assert t[0]["win"] is False


def test_ts_zero_pomijany():
    """timestamp_wejscia=0 (brak danych) → trade pominięty na rysunku, nie crash."""
    assert trades_z_historii([_w(0, 2, 1.0, 2.0, 1.0)], _bary()) == []


def test_exit_poza_zakresem_przyciety():
    t = trades_z_historii([_w(1008, 99, 108.0, 109.0, 1.0)], _bary())
    assert t[0]["exit_idx"] == 9   # przycięte do ostatniego baru


def test_ema_rozgrzewka_none():
    e = _ema([1.0] * 60, okres=50)
    assert e[:49] == [None] * 49 and e[49] is not None


def test_ema_za_krotka_seria():
    assert _ema([1.0, 2.0], okres=50) == [None, None]
