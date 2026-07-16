"""Testy K-04 USD strength — neuron (granice) + AdapterUSD (offline z-score).
Prawo XXI + Reguła Test-Granic: progi ±1.5/±0.7, None, kierunek (silny USD→SHORT)."""
import json

from imperium.legiony.neurony.makro import NeuronUSDStrength
from imperium.akwedukty.adaptery.usd_sila import AdapterUSD


# ── Neuron: granice (silny USD → SHORT, słaby → LONG) ─────────────────────────
def test_usd_brak_danych_neutral():
    s = NeuronUSDStrength().interpretuj({})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0


def test_usd_silny_short():
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": 2.0}).kierunek == "SHORT"
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": 1.5}).pewnosc == 0.70
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": 1.4}).pewnosc == 0.50   # 0.7-1.5


def test_usd_slaby_long():
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": -2.0}).kierunek == "LONG"
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": -1.5}).pewnosc == 0.70


def test_usd_prog_07_granica():
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": 0.7}).kierunek == "SHORT"
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": 0.6}).kierunek == "NEUTRAL"
    assert NeuronUSDStrength().interpretuj({"USD_ZSCORE": -0.7}).kierunek == "LONG"


def test_k04_klucz_kategoria():
    n = NeuronUSDStrength()
    assert n.KLUCZ == "K-04" and n.KATEGORIA == "K" and n.WSKAZNIK == "USD_ZSCORE"


# ── Adapter: offline (z-score z historii FX) ──────────────────────────────────
def _probka(rates_per_dzien):
    return json.dumps({"rates": rates_per_dzien})


def test_adapter_liczy_zscore():
    # 70 dni płaskich + ostatni skok USD → dodatni z-score
    rates = {}
    for i in range(70):
        rates[f"2024-01-{i+1:02d}" if i < 31 else f"2024-02-{i-30:02d}"] = {
            "EUR": 0.9, "JPY": 150.0, "GBP": 0.8}
    # ostatni dzień: silniejszy USD (wyższe kursy)
    rates["2024-03-15"] = {"EUR": 0.95, "JPY": 158.0, "GBP": 0.84}
    a = AdapterUSD(fetcher=lambda: _probka(rates))
    r = a.pobierz()
    assert r["USD_ZSCORE"] is not None and r["USD_ZSCORE"] > 2.0   # skok → wysoki z-score


def test_adapter_za_malo_dni_none():
    rates = {f"2024-01-{i+1:02d}": {"EUR": 0.9, "JPY": 150.0, "GBP": 0.8} for i in range(10)}
    a = AdapterUSD(fetcher=lambda: _probka(rates))
    assert a.pobierz()["USD_ZSCORE"] is None


def test_adapter_uszkodzone_none():
    a = AdapterUSD(fetcher=lambda: "nie-json")
    assert a.pobierz()["USD_ZSCORE"] is None
