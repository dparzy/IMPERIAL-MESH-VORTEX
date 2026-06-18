"""
🧪 Testy AdapterMEXCFutures — funding/OI rodzime z MEXC (contract public API).

Wszystkie testy OFFLINE (wstrzyknięty fetcher → próbki JSON MEXC). Każdy test
budzący neurony przywraca stan w `finally` (by nie zafałszować statycznego audytu).
Prawo XXI (Reguła Test-Granic): symbol-konwersja, None przy braku/błędzie, OI_PREV.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.akwedukty.adaptery import AdapterMEXCFutures
from imperium.legiony.neurony.psychologia import NeuronFundingExtreme, NeuronOIDiv


def _fetcher_mexc(funding="0.0001", oi="1500000"):
    """Wstrzykiwany fetcher(url)->JSON w formacie MEXC contract (data-wrapped)."""
    def fetch(url: str) -> str:
        if "funding_rate" in url:
            return '{"success":true,"code":0,"data":{"symbol":"BTC_USDT","fundingRate":%s}}' % funding
        if "ticker" in url:
            return '{"success":true,"code":0,"data":{"symbol":"BTC_USDT","lastPrice":40000,"holdVol":%s}}' % oi
        return "{}"
    return fetch


# ── Konwersja symbolu (granice) ──────────────────────────────────────────────

def test_symbol_konwersja():
    f = AdapterMEXCFutures._na_symbol_mexc
    assert f("BTCUSDT") == "BTC_USDT"
    assert f("BTC/USDT") == "BTC_USDT"
    assert f("BTC_USDT") == "BTC_USDT"
    assert f("ethusdt") == "ETH_USDT"


# ── Wzbogacanie dict ─────────────────────────────────────────────────────────

def test_dolewa_funding_i_oi():
    ad = AdapterMEXCFutures(fetcher=_fetcher_mexc(funding="0.0025", oi="1600000"))
    wsk = ad.wzbogac({}, "BTCUSDT")
    assert abs(wsk["FUNDING_RATE"] - 0.0025) < 1e-9
    assert abs(wsk["OPEN_INTEREST"] - 1600000) < 1e-6
    assert "OPEN_INTEREST_PREV" in wsk


def test_klucze_deklarowane_zgodne():
    ad = AdapterMEXCFutures(fetcher=_fetcher_mexc())
    dane = ad.pobierz("BTCUSDT")
    assert set(ad.KLUCZE) <= set(dane.keys())


# ── OI_PREV — pamięć między cyklami (Prawo I) ────────────────────────────────

def test_oi_prev_pamiec():
    ad = AdapterMEXCFutures(fetcher=_fetcher_mexc(oi="1500000"))
    d1 = ad.pobierz("BTCUSDT")
    assert d1["OPEN_INTEREST"] == d1["OPEN_INTEREST_PREV"]   # pierwszy: brak dywergencji
    ad._fetcher = _fetcher_mexc(oi="1600000")
    d2 = ad.pobierz("BTCUSDT")
    assert d2["OPEN_INTEREST_PREV"] == 1500000.0             # pamięta poprzedni
    assert d2["OPEN_INTEREST"] == 1600000.0


# ── Odporność na błędy (Prawo XV — None, nie halucynacja) ────────────────────

def test_padniety_fetcher_bezpieczny():
    def zly(url):
        raise ConnectionError("brak sieci")
    ad = AdapterMEXCFutures(fetcher=zly)
    dane = ad.pobierz("BTCUSDT")
    assert dane["FUNDING_RATE"] is None
    assert dane["OPEN_INTEREST"] is None


def test_uszkodzony_json_nie_psuje():
    def smieci(url):
        return "to-nie-json"
    ad = AdapterMEXCFutures(fetcher=smieci)
    wsk = ad.wzbogac({"ISTNIEJACY": 1}, "BTCUSDT")
    assert wsk["ISTNIEJACY"] == 1   # nie nadpisuje istniejących pustką
    assert "FUNDING_RATE" not in wsk  # None pominięte


def test_brak_pola_funding_zwraca_none():
    def bez_funding(url):
        if "funding_rate" in url:
            return '{"success":true,"data":{"symbol":"BTC_USDT"}}'
        return '{"success":true,"data":{"holdVol":1500000}}'
    ad = AdapterMEXCFutures(fetcher=bez_funding)
    dane = ad.pobierz("BTCUSDT")
    assert dane["FUNDING_RATE"] is None
    assert dane["OPEN_INTEREST"] == 1500000.0   # OI nadal działa


# ── Budzenie / usypianie neuronów (Prawo XV) ─────────────────────────────────

def test_budzi_psy01_psy04():
    ad = AdapterMEXCFutures(fetcher=_fetcher_mexc())
    try:
        obudzone = ad.aktywuj()
        assert NeuronFundingExtreme.KLUCZ in obudzone
        assert NeuronOIDiv.KLUCZ in obudzone
        assert NeuronFundingExtreme.DOSTEPNY is True
        assert NeuronOIDiv.DOSTEPNY is True
    finally:
        ad.usypiaj()
        # przywróć dokładnie pierwotny stan (PSY-01/04 są aktywne globalnie przez AdapterFutures)
        NeuronFundingExtreme.DOSTEPNY, NeuronOIDiv.DOSTEPNY = (True, True)
    assert NeuronFundingExtreme.KLUCZ == "PSY-01"
    assert NeuronOIDiv.KLUCZ == "PSY-04"


def test_neurony_obslugiwane():
    ad = AdapterMEXCFutures()
    obsl = set(ad.neurony_obslugiwane())
    assert obsl == {"PSY-01", "PSY-04"}
