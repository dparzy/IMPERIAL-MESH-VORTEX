"""
Testy backfillu sentymentu historycznego (PSY-01/02/04 — pomiar w backteście).

Weryfikuje:
  • AdapterFutures.pobierz_historie() parsuje funding/OI/L-S (mock, offline),
  • forward_fill_na_bary() jest kauzalny (bar dostaje ostatni punkt ≤ ts),
  • OPEN_INTEREST_PREV liczone poprawnie (pierwszy odczyt + dywergencja),
  • granice: bar przed pierwszym fundingiem → None, dokładny timestamp,
  • CSV roundtrip (zapisz → wczytaj == oryginał),
  • backtest_portfel(sentyment_per=...) budzi PSY w backteście (Prawo XVI).
"""

import json
import logging
import tempfile
from pathlib import Path

from imperium.akwedukty.adaptery.futures import AdapterFutures
from imperium.akwedukty.sentyment_historyczny import (
    forward_fill_na_bary, zapisz_csv, wczytaj_csv,
)

logging.disable(logging.CRITICAL)


def _mock_hist(url: str) -> str:
    """Mock Binance historical endpoints — deterministyczny, offline."""
    if "fundingRate" in url:
        return json.dumps([
            {"symbol": "BTCUSDT", "fundingTime": 1000, "fundingRate": "0.0001"},
            {"symbol": "BTCUSDT", "fundingTime": 9000, "fundingRate": "0.0015"},
        ])
    if "openInterestHist" in url:
        return json.dumps([
            {"symbol": "BTCUSDT", "sumOpenInterest": "100000", "timestamp": 1000},
            {"symbol": "BTCUSDT", "sumOpenInterest": "120000", "timestamp": 5000},
        ])
    if "globalLongShortAccountRatio" in url:
        return json.dumps([
            {"longAccount": "0.60", "timestamp": 1000},
            {"longAccount": "0.75", "timestamp": 5000},
        ])
    return "[]"


def test_pobierz_historie_parsuje():
    a = AdapterFutures(fetcher=_mock_hist)
    hist = a.pobierz_historie("BTCUSDT")
    # Rosnąco po timestamp
    ts = [r["timestamp"] for r in hist]
    assert ts == sorted(ts)
    # Funding z dwóch punktów
    fundings = [r["FUNDING_RATE"] for r in hist if r["FUNDING_RATE"] is not None]
    assert 0.0001 in fundings and 0.0015 in fundings


def test_pobierz_historie_pusta_odpowiedz():
    a = AdapterFutures(fetcher=lambda url: "[]")
    assert a.pobierz_historie("BTCUSDT") == []


def test_forward_fill_kauzalny():
    """Każdy bar dostaje ostatni punkt o ts ≤ ts_baru (bez look-ahead)."""
    historia = [
        {"timestamp": 1000, "FUNDING_RATE": 0.0001, "OPEN_INTEREST": None, "LONG_SHORT_RATIO": None},
        {"timestamp": 9000, "FUNDING_RATE": 0.0015, "OPEN_INTEREST": None, "LONG_SHORT_RATIO": None},
    ]
    bary = [
        {"timestamp": 500},   # przed pierwszym fundingiem → None
        {"timestamp": 1000},  # dokładnie na pierwszym → 0.0001
        {"timestamp": 5000},  # między → wciąż 0.0001 (forward-fill)
        {"timestamp": 9000},  # na drugim → 0.0015
        {"timestamp": 12000}, # po drugim → 0.0015
    ]
    m = forward_fill_na_bary(bary, historia)
    assert 500 not in m                     # granica: przed pierwszym = brak
    assert m[1000]["FUNDING_RATE"] == 0.0001  # granica: dokładny ts
    assert m[5000]["FUNDING_RATE"] == 0.0001  # forward-fill
    assert m[9000]["FUNDING_RATE"] == 0.0015
    assert m[12000]["FUNDING_RATE"] == 0.0015


def test_forward_fill_oi_prev():
    """OPEN_INTEREST_PREV: pierwszy odczyt = OI, potem poprzednia RÓŻNA wartość."""
    historia = [
        {"timestamp": 1000, "FUNDING_RATE": None, "OPEN_INTEREST": 100.0, "LONG_SHORT_RATIO": None},
        {"timestamp": 2000, "FUNDING_RATE": None, "OPEN_INTEREST": 120.0, "LONG_SHORT_RATIO": None},
    ]
    bary = [{"timestamp": 1000}, {"timestamp": 1500}, {"timestamp": 2000}]
    m = forward_fill_na_bary(bary, historia)
    # Pierwszy bar z OI → PREV = OI (brak dywergencji)
    assert m[1000]["OPEN_INTEREST"] == 100.0
    assert m[1000]["OPEN_INTEREST_PREV"] == 100.0
    # Bar 1500 wciąż OI=100 (forward-fill), PREV=100
    assert m[1500]["OPEN_INTEREST"] == 100.0
    # Bar 2000 OI=120 → PREV=100 (poprzednia różna)
    assert m[2000]["OPEN_INTEREST"] == 120.0
    assert m[2000]["OPEN_INTEREST_PREV"] == 100.0


def test_forward_fill_pusta_historia():
    assert forward_fill_na_bary([{"timestamp": 100}], []) == {}


def test_csv_roundtrip():
    """zapisz_csv → wczytaj_csv zachowuje wartości i None."""
    historia = [
        {"timestamp": 1000, "FUNDING_RATE": 0.0001, "OPEN_INTEREST": 100.0, "LONG_SHORT_RATIO": None},
        {"timestamp": 2000, "FUNDING_RATE": None, "OPEN_INTEREST": 120.0, "LONG_SHORT_RATIO": 0.75},
    ]
    with tempfile.TemporaryDirectory() as d:
        sciezka = Path(d) / "BTCUSDT.csv"
        n = zapisz_csv(historia, sciezka)
        assert n == 2
        wczytane = wczytaj_csv(sciezka)
    assert wczytane[0]["timestamp"] == 1000
    assert wczytane[0]["FUNDING_RATE"] == 0.0001
    assert wczytane[0]["LONG_SHORT_RATIO"] is None
    assert wczytane[1]["FUNDING_RATE"] is None
    assert wczytane[1]["LONG_SHORT_RATIO"] == 0.75


def test_wczytaj_csv_nieistniejacy():
    assert wczytaj_csv("/nieistnieje/xyz.csv") == []


def test_backtest_portfel_sentyment_budzi_psy():
    """sentyment_per wstrzyknięty → PSY dostają FUNDING_RATE (Prawo XVI)."""
    from imperium.koloseum.backtest import backtest_portfel

    def bary(n, sym):
        b = []
        c = 100.0
        for i in range(n):
            c *= 1.002 if (i // 7) % 2 == 0 else 0.999
            o = c
            cl = c * (1.001 if i % 2 == 0 else 0.9995)
            b.append({"timestamp": 1_600_000_000_000 + i * 3_600_000,
                      "open": o, "high": max(o, cl) * 1.002, "low": min(o, cl) * 0.998,
                      "close": cl, "volume": 1000.0 + i, "volume_quote": 0,
                      "symbol": sym, "interwal": "1H", "tradecount": 100})
        return b

    bp = {"BTC": bary(300, "BTC")}
    # Zbuduj sentyment: ekstremalny funding na każdym barze
    hist = [{"timestamp": b["timestamp"], "FUNDING_RATE": 0.002,
             "OPEN_INTEREST": 100.0 + i, "LONG_SHORT_RATIO": 0.8}
            for i, b in enumerate(bp["BTC"])]
    sent_map = forward_fill_na_bary(bp["BTC"], hist)
    sentyment_per = {"BTC": sent_map}

    # Kontrakt: przebieg z sentymentem nie crashuje i daje dodatnie equity
    eng = backtest_portfel({}, "1H", bary_per=bp, sentyment_per=sentyment_per)
    assert eng.podsumowanie().kapital_koncowy > 0


def test_backtest_portfel_sentyment_none_bez_zmian():
    """sentyment_per=None (domyślne) → identyczne zachowanie jak dotąd (zero regresji)."""
    from imperium.koloseum.backtest import backtest_portfel

    def bary(n, sym):
        b = []
        c = 100.0
        for i in range(n):
            c *= 1.002 if (i // 7) % 2 == 0 else 0.999
            o = c
            cl = c * (1.001 if i % 2 == 0 else 0.9995)
            b.append({"timestamp": 1_600_000_000_000 + i * 3_600_000,
                      "open": o, "high": max(o, cl) * 1.002, "low": min(o, cl) * 0.998,
                      "close": cl, "volume": 1000.0 + i, "volume_quote": 0,
                      "symbol": sym, "interwal": "1H", "tradecount": 100})
        return b

    bp = {"BTC": bary(300, "BTC")}
    e1 = backtest_portfel({}, "1H", bary_per={"BTC": list(bp["BTC"])})
    e2 = backtest_portfel({}, "1H", bary_per={"BTC": list(bp["BTC"])}, sentyment_per=None)
    assert e1.podsumowanie().total_trades == e2.podsumowanie().total_trades


def test_brak_stale_sentymentu_bez_btc():
    """
    Bug recenzji: koszyk bez BTC (radar nie wstaje) — bar bez punktu sentymentu
    NIE może dziedziczyć starego funding z poprzedniego baru (stale-data, Prawo XV).
    Sentyment tylko dla 1. baru po oknie → kolejne bary muszą mieć kontekst czysty.
    """
    from imperium.koloseum.backtest import backtest_portfel

    def bary(n, sym):
        b = []
        c = 100.0
        for i in range(n):
            c *= 1.002 if (i // 7) % 2 == 0 else 0.999
            o = c
            cl = c * (1.001 if i % 2 == 0 else 0.9995)
            b.append({"timestamp": 1_600_000_000_000 + i * 3_600_000,
                      "open": o, "high": max(o, cl) * 1.002, "low": min(o, cl) * 0.998,
                      "close": cl, "volume": 1000.0 + i, "volume_quote": 0,
                      "symbol": sym, "interwal": "1H", "tradecount": 100})
        return b

    import imperium.koloseum.backtest as bt_mod
    from imperium.koloseum.dyrygent import Dyrygent

    # Koszyk bez BTC (same alty → radar nie wstaje, kontekst nie jest resetowany)
    bp = {"ETH": bary(300, "ETH")}
    ts_okno = int(bp["ETH"][250]["timestamp"])
    # Sentyment TYLKO dla baru[250]; kolejne bary go nie mają
    sentyment_per = {"ETH": {ts_okno: {"FUNDING_RATE": 0.002}}}

    # Szpieg: rejestruje FUNDING_RATE widziany w kontekście per bar
    funding_per_bar = []

    class SzpiegDyrygent(Dyrygent):
        def cykl(self, symbol, okno_barow, *args, **kwargs):
            funding_per_bar.append(self.kontekst_dodatkowy.get("FUNDING_RATE"))
            return super().cykl(symbol, okno_barow, *args, **kwargs)

    pierwotny = bt_mod.Dyrygent
    bt_mod.Dyrygent = SzpiegDyrygent
    try:
        backtest_portfel({}, "1H", bary_per=bp, sentyment_per=sentyment_per)
    finally:
        bt_mod.Dyrygent = pierwotny

    # Pierwszy bar (ts_okno) widzi funding; kolejne NIE (brak stale-data)
    assert funding_per_bar[0] == 0.002
    assert all(f is None for f in funding_per_bar[1:]), \
        f"stale-data: stary funding wyciekł na kolejne bary: {funding_per_bar[:5]}"
