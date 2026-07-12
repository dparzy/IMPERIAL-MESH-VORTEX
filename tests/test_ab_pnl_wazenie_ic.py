"""Testy W-361 A/B na P&L (narzedzia/ab_pnl_wazenie_ic.py) — werdykt + wpięcie flagi.

Reguła Test-Granic (Prawo XXI): werdykt decyduje na PROGACH (liczba par konkluzywnych,
znak Δ equity, większość). Testujemy każdą granicę osobno + że opt-in w backtescie
domyślnie NIE zmienia zachowania (ZASADA WPIĘCIA)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.ab_pnl_wazenie_ic import _status_werdyktu, _metryki, _nota


class _FakeStats:
    def __init__(self, kapital_koncowy, total_trades, win_rate, profit_factor):
        self.kapital_koncowy = kapital_koncowy
        self.kapital_startowy = 10_000.0
        self.total_trades = total_trades
        self.win_rate = win_rate
        self.profit_factor = profit_factor


class _FakeEngine:
    def __init__(self, stats):
        self._stats = stats

    def podsumowanie(self):
        return self._stats


# ── Ekstrakcja metryk ──────────────────────────────────────────────────────────

def test_metryki_liczy_zwrot():
    eng = _FakeEngine(_FakeStats(11_000.0, 8, 0.5, 1.4))
    m = _metryki(eng)
    assert abs(m["ret"] - 0.10) < 1e-9      # 11000/10000 - 1
    assert m["trades"] == 8 and m["wr"] == 0.5 and m["pf"] == 1.4


def test_metryki_strata_ujemny_zwrot():
    m = _metryki(_FakeEngine(_FakeStats(9_000.0, 3, 0.33, 0.7)))
    assert abs(m["ret"] + 0.10) < 1e-9      # -10%


# ── Werdykt: granice (konkluzywność / znak Δ / większość) ──────────────────────

def test_werdykt_niekonkluzywny_gdy_malo_par():
    # <2 pary konkluzywne → NIEKONKLUZYWNE niezależnie od equity
    s = _status_werdyktu(n_konkluzywne=1, baza_n=1, total_off=0.0, total_on=0.5, lepsze=1)
    assert "NIEKONKLUZYWNE" in s


def test_werdykt_zielony_gdy_equity_wyzsze_i_wiekszosc():
    s = _status_werdyktu(n_konkluzywne=5, baza_n=5, total_off=0.10, total_on=0.20, lepsze=3)
    assert s.startswith("✅")


def test_werdykt_granica_dokladnie_polowa_par_liczy_sie_jako_wiekszosc():
    # lepsze*2 >= baza_n → 2*2>=4 True (remis liczy się na korzyść ON, bo equity wyższe)
    s = _status_werdyktu(n_konkluzywne=4, baza_n=4, total_off=0.05, total_on=0.06, lepsze=2)
    assert s.startswith("✅")


def test_werdykt_niestabilny_gdy_equity_wyzsze_ale_mniejszosc():
    # equity ON>OFF ale ON lepsze tylko na 1/4 → ostrzeżenie, nie zielony
    s = _status_werdyktu(n_konkluzywne=4, baza_n=4, total_off=0.10, total_on=0.11, lepsze=1)
    assert s.startswith("⚠️") and "niestabilny" in s


def test_werdykt_czerwony_gdy_equity_nizsze():
    s = _status_werdyktu(n_konkluzywne=5, baza_n=5, total_off=0.20, total_on=0.10, lepsze=2)
    assert s.startswith("❌")


def test_werdykt_czerwony_gdy_equity_rowne():
    # równe equity → ON NIE bije OFF (granica > vs >=) → czerwony
    s = _status_werdyktu(n_konkluzywne=3, baza_n=3, total_off=0.15, total_on=0.15, lepsze=3)
    assert s.startswith("❌")


# ── Nota: format stabilny i parsowalny ─────────────────────────────────────────

def test_nota_zawiera_klucze_metryk():
    w = {"bary_test": 300, "ret_off": 0.05, "ret_on": 0.08,
         "trades_off": 12, "trades_on": 14, "wr_off": 0.5, "wr_on": 0.57,
         "pf_off": 1.2, "pf_on": 1.5}
    nota = _nota("Binance_BTCUSDT_4h.csv", 0.6, w)
    pola = dict(kv.split("=", 1) for kv in nota.split(";") if "=" in kv)
    assert pola["retON"] == "0.0800" and pola["trON"] == "14"
    assert float(pola["retOFF"]) == 0.05 and int(pola["test"]) == 300


# ── Opt-in w backtescie: domyślnie OFF nie zmienia zachowania ──────────────────

def test_backtest_domyslnie_bez_wazenia_ic():
    """Bez wagi_ic backtest nie dotyka Legatusa (ZASADA WPIĘCIA: zero zmiany domyślnej)."""
    from imperium.koloseum.backtest import backtest

    bary = _bary_syntetyczne(n=340)
    eng = backtest("x", "4h", bary=bary, okno=250)
    # Domyślnie ważenie IC nieaktywne — backtest przebiega jak dotąd (zwraca silnik).
    assert eng is not None and hasattr(eng, "podsumowanie")


def test_backtest_z_wagami_ic_nie_wybucha():
    """wazenie_ic=True + wagi_ic przechodzi pełny bieg bez błędu (wpięcie w Legatusa)."""
    from imperium.koloseum.backtest import backtest

    bary = _bary_syntetyczne(n=340)
    wagi = {"X-01": 0.4, "XII-01": -0.3}     # dowolne klucze — brakujące pomija domyslny_ic=0
    eng = backtest("x", "4h", bary=bary, okno=250, wazenie_ic=True, wagi_ic=wagi)
    assert eng is not None and hasattr(eng, "podsumowanie")


def _bary_syntetyczne(n=340):
    """Prosta seria OHLCV rosnąco-falująca (wystarcza do przejścia pipeline)."""
    import math
    bary = []
    cena = 100.0
    for i in range(n):
        cena *= 1 + 0.002 * math.sin(i / 5.0) + 0.0005
        o = cena
        h = cena * 1.01
        low = cena * 0.99
        c = cena * (1 + 0.001 * math.cos(i / 7.0))
        bary.append({
            "symbol": "TESTUSDT", "interwal": "4h",
            "open": o, "high": h, "low": low, "close": c,
            "volume": 1000.0 + 10 * i, "timestamp": 1_600_000_000 + i * 14400,
        })
    return bary
