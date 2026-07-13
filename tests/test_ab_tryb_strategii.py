"""Testy harnessu walidacji warstwy strategii (narzedzia/ab_tryb_strategii.py).

Reguła Test-Granic (Prawo XXI): guard poprawności zapisu/odczytu areny (nota round-trip —
błąd tu = resume zwraca złe liczby) + ekstrakcja metryk."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.ab_tryb_strategii import _metryki, _nota, _TRYBY


class _FakeStats:
    def __init__(self, kapital_koncowy, total_trades, win_rate):
        self.kapital_koncowy = kapital_koncowy
        self.kapital_startowy = 10_000.0
        self.total_trades = total_trades
        self.win_rate = win_rate


class _FakeEngine:
    def __init__(self, stats):
        self._stats = stats

    def podsumowanie(self):
        return self._stats


def test_metryki_liczy_zwrot():
    m = _metryki(_FakeEngine(_FakeStats(10_800.0, 12, 0.5)))
    assert abs(m["ret"] - 0.08) < 1e-9 and m["trades"] == 12 and m["wr"] == 0.5


def test_tryby_kompletne():
    # kolejność/zawartość trybów stała — od niej zależą klucze noty i kolumny raportu
    assert _TRYBY == ("agregat", "filtr", "strategia")


def test_nota_roundtrip_wszystkie_tryby():
    w = {"bary": 1500}
    for tr in _TRYBY:
        w[f"ret_{tr}"] = 0.1234
        w[f"tr_{tr}"] = 42
        w[f"wr_{tr}"] = 0.55
    nota = _nota("Binance_BTCUSDT_4h.csv", w)
    pola = dict(kv.split("=", 1) for kv in nota.split(";") if "=" in kv)
    # każdy tryb zapisany i parsowalny — brak kolizji kluczy (agregat/filtr/strategia)
    for tr in _TRYBY:
        assert pola[f"ret_{tr}"] == "0.1234"
        assert int(pola[f"tr_{tr}"]) == 42
    assert int(pola["bary"]) == 1500
