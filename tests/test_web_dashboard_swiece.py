"""
Testy W-361 — feed MEXC + markery bota na wykresie web (web_dashboard.py).
Reguła Test-Granic (Prawo XXI): puste/None/złe dane, ms→s, sortowanie, fallback.
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.swiatynie.web_dashboard import (
    MagazynSwiec,
    znaczniki_do_lwc,
    obsluz_sciezke,
    stan_do_json,
)


# ── znaczniki_do_lwc ───────────────────────────────────────────────────────────

def test_znacznik_long_wejscie():
    m = znaczniki_do_lwc([{"timestamp": 1700000000, "cena": 100.0,
                           "kierunek": "LONG", "typ": "wejscie", "symbol": "BTCUSDT"}])
    assert len(m) == 1
    assert m[0]["position"] == "belowBar"
    assert m[0]["shape"] == "arrowUp"
    assert m[0]["symbol"] == "BTCUSDT"


def test_znacznik_short_wejscie_nad_swieca():
    m = znaczniki_do_lwc([{"timestamp": 1700000000, "cena": 100.0,
                           "kierunek": "SHORT", "typ": "wejscie", "symbol": "ETHUSDT"}])
    assert m[0]["position"] == "aboveBar"
    assert m[0]["shape"] == "arrowDown"


def test_znacznik_wyjscie():
    m = znaczniki_do_lwc([{"timestamp": 1700000000, "cena": 100.0,
                           "kierunek": "LONG", "typ": "wyjscie", "symbol": "BTCUSDT"}])
    assert m[0]["text"] == "wyjście"
    assert m[0]["shape"] == "arrowDown"


def test_znacznik_ms_na_sekundy():
    """timestamp w ms (>1e12) → sekundy (LWC)."""
    m = znaczniki_do_lwc([{"timestamp": 1700000000000, "cena": 1.0,
                           "kierunek": "LONG", "typ": "wejscie", "symbol": "X"}])
    assert m[0]["time"] == 1700000000


def test_znaczniki_sortowane_rosnaco():
    m = znaczniki_do_lwc([
        {"timestamp": 300, "cena": 1, "kierunek": "LONG", "typ": "wejscie", "symbol": "X"},
        {"timestamp": 100, "cena": 1, "kierunek": "LONG", "typ": "wejscie", "symbol": "X"},
        {"timestamp": 200, "cena": 1, "kierunek": "LONG", "typ": "wejscie", "symbol": "X"},
    ])
    assert [x["time"] for x in m] == [100, 200, 300]


def test_znacznik_zly_pomijany():
    m = znaczniki_do_lwc([{"brak": "kluczy"},
                          {"timestamp": "zła", "cena": 1}])
    assert m == []


def test_znaczniki_pusta_i_none():
    assert znaczniki_do_lwc([]) == []
    assert znaczniki_do_lwc(None) == []


# ── MagazynSwiec ───────────────────────────────────────────────────────────────

def _bary(n, base_ms=1700000000000):
    return [{"timestamp": base_ms + i * 3600_000, "open": 100 + i, "high": 103 + i,
             "low": 98 + i, "close": 101 + i, "volume": 5} for i in range(n)]


def test_magazyn_roundtrip_ms_na_s():
    mag = MagazynSwiec()
    mag.podaj("btcusdt", _bary(3))
    sw = mag.get("BTCUSDT")
    assert len(sw) == 3
    assert sw[0]["time"] == 1700000000        # ms→s
    assert set(sw[0]) == {"time", "open", "high", "low", "close"}


def test_magazyn_symbole_sortowane():
    mag = MagazynSwiec()
    mag.podaj("ETHUSDT", _bary(2))
    mag.podaj("BTCUSDT", _bary(2))
    assert mag.symbole() == ["BTCUSDT", "ETHUSDT"]


def test_magazyn_cap_max():
    mag = MagazynSwiec(max_swiec=5)
    mag.podaj("X", _bary(20))
    assert len(mag.get("X")) == 5


def test_magazyn_zly_bar_pomijany():
    mag = MagazynSwiec()
    mag.podaj("X", [{"timestamp": 1, "open": 1, "high": 2, "low": 0, "close": 1},
                    {"brak": "close"}])
    assert len(mag.get("X")) == 1


def test_magazyn_pusty_symbol():
    mag = MagazynSwiec()
    assert mag.get("NIEMA") == []
    assert mag.symbole() == []


def test_magazyn_posortowane_po_czasie():
    mag = MagazynSwiec()
    mag.podaj("X", [
        {"timestamp": 3000, "open": 1, "high": 1, "low": 1, "close": 1},
        {"timestamp": 1000, "open": 1, "high": 1, "low": 1, "close": 1},
    ])
    assert [c["time"] for c in mag.get("X")] == [1000, 3000]


# ── Router z magazynem (feed MEXC) ─────────────────────────────────────────────

class _PustyStan:
    symbol = "BTCUSDT"; rezim = "NORMAL"; kierunek_legatus = "NEUTRAL"
    pewnosc = 0.0; kapital = 1000.0; kapital_start = 1000.0
    postawa_gubernatora = "NORMALNY"; bary_przetworzone = 0
    decyzje_wejscia = 0; weta = 0; bledy = 0; pozycje = []; neurony_top = []


def test_wykresy_serwuje_magazyn_gdy_brak_webhooka():
    mag = MagazynSwiec()
    mag.podaj("BTCUSDT", _bary(4))
    status, ctype, body = obsluz_sciezke("/wykresy/BTCUSDT.json", _PustyStan(),
                                         odbiornik=None, magazyn=mag)
    assert status == 200
    dane = json.loads(body)
    assert len(dane) == 4
    assert dane[0]["time"] == 1700000000


def test_wykresy_pusty_gdy_brak_zrodel():
    status, ctype, body = obsluz_sciezke("/wykresy/BTCUSDT.json", _PustyStan())
    assert json.loads(body) == []


def test_stan_json_zawiera_symbole_swiec():
    mag = MagazynSwiec()
    mag.podaj("BTCUSDT", _bary(2))
    mag.podaj("ETHUSDT", _bary(2))
    status, ctype, body = obsluz_sciezke("/stan.json", _PustyStan(), magazyn=mag)
    dane = json.loads(body)
    assert dane["symbole_swiec"] == ["BTCUSDT", "ETHUSDT"]


def test_stan_do_json_ma_znaczniki():
    class Stan(_PustyStan):
        znaczniki_swiec = [{"timestamp": 1700000000, "cena": 1.0,
                            "kierunek": "LONG", "typ": "wejscie", "symbol": "BTCUSDT"}]
    dane = stan_do_json(Stan())
    assert "znaczniki" in dane
    assert dane["znaczniki"][0]["symbol"] == "BTCUSDT"


def test_stan_do_json_bez_znacznikow_pusta_lista():
    dane = stan_do_json(_PustyStan())
    assert dane["znaczniki"] == []


# ── Integracja: serwer podaj_swiece → router ───────────────────────────────────

def test_serwer_podaj_swiece_dostepne_przez_router():
    from imperium.swiatynie.web_dashboard import SerwerDashboard
    srv = SerwerDashboard(port=8798)
    srv.podaj_swiece("BTCUSDT", _bary(3))
    # magazyn wewnętrzny serwera serwowany przez router
    status, ctype, body = obsluz_sciezke("/wykresy/BTCUSDT.json", _PustyStan(),
                                         magazyn=srv._magazyn)
    assert len(json.loads(body)) == 3
