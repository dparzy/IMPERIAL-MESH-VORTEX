"""
Testy W-300 — wpięcie RadarRynku w sloty kontekstu Dyrygenta.

Dowodzą, że odswiez_kontekst_rynku():
  1. wypełnia kontekst_dodatkowy kluczami radaru (BTC_TREND/DOMINACJA/PRZEPLYW),
  2. ustawia stan_rynku (dla Namiestnika),
  3. realnie BUDZI neuron RADAR-01 (Prawo XV — koniec martwego głosu),
  4. abstynuje (zwraca stan z None) gdy za mało danych BTC (granica).
"""

from imperium.koloseum.dyrygent import Dyrygent
from imperium.koloseum.paper_trading import PaperTradingEngine
from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
from imperium.legiony.rejestr import zbuduj_legatusa
from imperium.legiony.neurony.sesje import NeuronRadarBTC


def _dyrygent():
    legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
    engine = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="TEST-RADAR")
    return Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine)


def _seria_rosnaca(n, start=100.0, krok=1.0):
    return [start + i * krok for i in range(n)]


def _seria_plaska(n, wartosc=100.0):
    return [wartosc for _ in range(n)]


# ── wypełnianie slotów ────────────────────────────────────────────────────────

def test_odswiez_wypelnia_kontekst_btc_trend():
    d = _dyrygent()
    close_btc = _seria_rosnaca(80)            # silny trend ↑ → BTC_TREND > 0
    close_alty = {"ETHUSDT": _seria_rosnaca(80, 50.0, 0.5)}
    d.odswiez_kontekst_rynku(close_btc, close_alty)
    assert "BTC_TREND" in d.kontekst_dodatkowy
    assert d.kontekst_dodatkowy["BTC_TREND"] > 0


def test_odswiez_ustawia_stan_rynku():
    d = _dyrygent()
    assert d.stan_rynku is None
    d.odswiez_kontekst_rynku(_seria_rosnaca(80), {"ETHUSDT": _seria_rosnaca(80, 50.0)})
    assert d.stan_rynku is not None
    assert hasattr(d.stan_rynku, "btc_trend")


def test_odswiez_nie_kasuje_innego_kontekstu():
    """update() — radar dolewa, nie nadpisuje kontekstu z innych źródeł (W-291)."""
    d = _dyrygent()
    d.kontekst_dodatkowy["JAKIS_INNY_KLUCZ"] = 42.0
    d.odswiez_kontekst_rynku(_seria_rosnaca(80), {"ETHUSDT": _seria_rosnaca(80, 50.0)})
    assert d.kontekst_dodatkowy["JAKIS_INNY_KLUCZ"] == 42.0
    assert "BTC_TREND" in d.kontekst_dodatkowy


# ── DOWÓD: neuron RADAR-01 faktycznie się budzi (Prawo XV) ────────────────────

def test_radar01_abstynuje_bez_kontekstu():
    """Bez odswiez_kontekst_rynku() — RADAR-01 milczy (stan sprzed wpięcia)."""
    neuron = NeuronRadarBTC()
    sygnal = neuron.interpretuj({})           # brak BTC_TREND
    assert sygnal.kierunek == "NEUTRAL"
    assert sygnal.pewnosc == 0.0


def test_radar01_budzi_sie_po_wpieciu():
    """Po odswiez_kontekst_rynku() z trendem ↑ — RADAR-01 głosuje LONG."""
    d = _dyrygent()
    d.odswiez_kontekst_rynku(_seria_rosnaca(80), {"ETHUSDT": _seria_rosnaca(80, 50.0)})
    neuron = NeuronRadarBTC()
    sygnal = neuron.interpretuj(d.kontekst_dodatkowy)
    assert sygnal.kierunek == "LONG"          # lider rośnie → wsparcie LONG
    assert sygnal.pewnosc > 0.0


# ── granica: za mało danych → radar milczy, nie zgaduje ───────────────────────

def test_odswiez_za_malo_danych_btc_trend_none():
    d = _dyrygent()
    # RadarBTC wymaga ema_wolna(30)+okno_vol(20)=50 zamknięć — dajemy 20.
    stan = d.odswiez_kontekst_rynku(_seria_rosnaca(20), {"ETHUSDT": _seria_rosnaca(20)})
    assert stan.btc_trend is None
    assert "BTC_TREND" not in d.kontekst_dodatkowy   # jako_wskazniki pomija None


def test_radar01_abstynuje_przy_plaskim_btc():
    """Płaski BTC (sd=0 / rozjazd≈0) → BTC_TREND ≈ 0 → neuron NEUTRAL."""
    d = _dyrygent()
    d.odswiez_kontekst_rynku(_seria_plaska(80), {"ETHUSDT": _seria_plaska(80)})
    bt = d.kontekst_dodatkowy.get("BTC_TREND")
    if bt is not None:                         # radar może zwrócić 0.0 lub None
        neuron = NeuronRadarBTC()
        assert neuron.interpretuj(d.kontekst_dodatkowy).kierunek == "NEUTRAL"


def test_odswiez_zwraca_stan_rynku():
    d = _dyrygent()
    stan = d.odswiez_kontekst_rynku(_seria_rosnaca(80), {"ETHUSDT": _seria_rosnaca(80, 50.0)})
    assert stan is d.stan_rynku
