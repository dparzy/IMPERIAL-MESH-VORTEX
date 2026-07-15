"""Testy K-03 Stablecoin flow — neuron (granice) + AdapterStablecoin (offline).
Prawo XXI + Reguła Test-Granic: progi 0.015/0.004/-0.008, None, kierunek trend-following."""
import json

from imperium.legiony.neurony.makro import NeuronStablecoinFlow
from imperium.akwedukty.adaptery.stablecoin import AdapterStablecoin


# ── Neuron: granice (trend-following — druk stablecoinów → LONG) ───────────────
def test_flow_brak_danych_neutral():
    s = NeuronStablecoinFlow().interpretuj({})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0


def test_flow_silny_druk_long():
    s = NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": 0.02})
    assert s.kierunek == "LONG" and s.pewnosc == 0.70


def test_flow_prog_0015_granica():
    assert NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": 0.015}).pewnosc == 0.70
    assert NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": 0.014}).pewnosc == 0.50   # 0.004-0.015


def test_flow_prog_0004_granica():
    assert NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": 0.004}).kierunek == "LONG"
    assert NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": 0.003}).kierunek == "NEUTRAL"


def test_flow_umorzenia_short():
    assert NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": -0.008}).kierunek == "SHORT"
    assert NeuronStablecoinFlow().interpretuj({"STABLE_FLOW": -0.007}).kierunek == "NEUTRAL"


def test_k03_klucz_kategoria():
    n = NeuronStablecoinFlow()
    assert n.KLUCZ == "K-03" and n.KATEGORIA == "K" and n.WSKAZNIK == "STABLE_FLOW"


# ── Adapter: offline (7d % zmiana z historii) ─────────────────────────────────
def _probka(supply_dni):
    """Buduje JSON DefiLlama z listy (data, supply)."""
    return json.dumps([{"date": str(ts), "totalCirculatingUSD": {"peggedUSD": v}}
                       for ts, v in supply_dni])


def test_adapter_liczy_delte_7d():
    # 9 dni: od 100e9 do 103e9; delta 7d = supply[-1]/supply[-8] - 1
    base = 1_700_000_000
    dni = [(base + i * 86400, (100 + i * 0.5) * 1e9) for i in range(9)]
    a = AdapterStablecoin(fetcher=lambda: _probka(dni))
    r = a.pobierz()
    # supply[-1]=104e9 (i=8), supply[-8]=100.5e9 (i=1) → ~3.48%
    assert r["STABLE_FLOW"] is not None and 0.03 < r["STABLE_FLOW"] < 0.04


def test_adapter_za_malo_dni_none():
    dni = [(1_700_000_000 + i * 86400, 100e9) for i in range(5)]   # <8 dni
    a = AdapterStablecoin(fetcher=lambda: _probka(dni))
    assert a.pobierz()["STABLE_FLOW"] is None


def test_adapter_uszkodzone_none():
    a = AdapterStablecoin(fetcher=lambda: "nie-json")
    assert a.pobierz()["STABLE_FLOW"] is None
