"""Testy NEWS-03 (spike uwagi) + NEWS-04 (Δ sentymentu) + stan kroczący adaptera."""

from imperium.legiony.neurony.news_dynamika import NeuronDeltaeSentymentu, NeuronSpikeUwagi
from imperium.akwedukty.adaptery.news_llm import AdapterNewsLLM


# ── NEWS-04 Δ sentymentu ──────────────────────────────────────────────────────

def test_delta_long_na_poprawie():
    s = NeuronDeltaeSentymentu().interpretuj({"NEWS_SENTYMENT_DELTA": 0.5})
    assert s.kierunek == "LONG"


def test_delta_short_na_pogorszeniu():
    s = NeuronDeltaeSentymentu().interpretuj({"NEWS_SENTYMENT_DELTA": -0.5})
    assert s.kierunek == "SHORT"


def test_delta_neutral_w_szumie():
    s = NeuronDeltaeSentymentu().interpretuj({"NEWS_SENTYMENT_DELTA": 0.1})
    assert s.kierunek == "NEUTRAL"


def test_delta_abstynuje_bez_danych():
    s = NeuronDeltaeSentymentu().interpretuj({})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0


# ── NEWS-03 spike uwagi ───────────────────────────────────────────────────────

def test_spike_long_z_pozytywnym_sentymentem():
    s = NeuronSpikeUwagi().interpretuj({"NEWS_ATTENTION_SPIKE": 3.0, "NEWS_SENTYMENT": 0.6})
    assert s.kierunek == "LONG"


def test_spike_short_z_negatywnym():
    s = NeuronSpikeUwagi().interpretuj({"NEWS_ATTENTION_SPIKE": 3.0, "NEWS_SENTYMENT": -0.6})
    assert s.kierunek == "SHORT"


def test_spike_neutral_bez_kierunku_sentymentu():
    """Spike bez wyraźnego sentymentu → NEUTRAL (czujność, nie pozycja)."""
    s = NeuronSpikeUwagi().interpretuj({"NEWS_ATTENTION_SPIKE": 3.0, "NEWS_SENTYMENT": 0.05})
    assert s.kierunek == "NEUTRAL"


def test_spike_neutral_gdy_uwaga_normalna():
    s = NeuronSpikeUwagi().interpretuj({"NEWS_ATTENTION_SPIKE": 1.0, "NEWS_SENTYMENT": 0.6})
    assert s.kierunek == "NEUTRAL"


def test_spike_abstynuje_bez_danych():
    assert NeuronSpikeUwagi().interpretuj({}).kierunek == "NEUTRAL"


# ── Stan kroczący adaptera ────────────────────────────────────────────────────

def test_adapter_delta_liczona_wzgledem_historii():
    """Δ = bieżący sentyment − średnia historyczna; pierwszy bar = None."""
    feeds = [["market quiet"], ["bitcoin surge rally record breakout adoption"]]
    box = {"i": 0}
    ad = AdapterNewsLLM(fetcher=lambda s: feeds[box["i"]], uzyj_llm=False)
    box["i"] = 0
    d0 = ad.pobierz("BTCUSDT")
    assert d0["NEWS_SENTYMENT_DELTA"] is None      # brak historii
    box["i"] = 1
    d1 = ad.pobierz("BTCUSDT")
    assert d1["NEWS_SENTYMENT_DELTA"] is not None
    assert d1["NEWS_SENTYMENT_DELTA"] > 0          # sentyment wzrósł


def test_adapter_spike_liczony_z_liczby_naglowkow():
    """Spike = liczba bieżąca / średnia historyczna; wysyp nagłówków → spike>1."""
    feeds = [["a news"], ["a news"], ["n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8"]]
    box = {"i": 0}
    ad = AdapterNewsLLM(fetcher=lambda s: feeds[box["i"]], uzyj_llm=False)
    for k in range(3):
        box["i"] = k
        d = ad.pobierz("BTCUSDT")
    assert d["NEWS_ATTENTION_SPIKE"] > 2.0          # 8 nagłówków vs średnia ~1
