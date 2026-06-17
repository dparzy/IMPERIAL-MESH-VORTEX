"""
W-334 — testy progów adaptacyjnych (P3) + neurony RSI/ADX z kontekstem reżimu.

Reguła Test-Granic: zero/None/próg dokładny/klamry bezpieczeństwa.
"""

from imperium.legiony.progi_adaptacyjne import (
    progi_rsi, prog_adx, atr_pct,
    RSI_DOLNY_BAZA, RSI_GORNY_BAZA, ADX_BAZA,
    RSI_DOLNY_MIN, RSI_GORNY_MAX, ADX_MIN, ADX_MAX,
)
from imperium.legiony.neurony.momentum import NeuronRSI
from imperium.legiony.neurony.trend import NeuronADX


# ── atr_pct ──────────────────────────────────────────────────────────────────

def test_atr_pct_brak_danych_zwraca_none():
    assert atr_pct({}) is None
    assert atr_pct({"ATR_14": 100.0}) is None          # brak CLOSE
    assert atr_pct({"CLOSE": 50000.0}) is None          # brak ATR
    assert atr_pct({"ATR_14": 100.0, "CLOSE": 0.0}) is None  # dzielenie przez 0


def test_atr_pct_oblicza_poprawnie():
    assert abs(atr_pct({"ATR_14": 1000.0, "CLOSE": 50000.0}) - 0.02) < 1e-9


# ── progi_rsi ────────────────────────────────────────────────────────────────

def test_rsi_bez_kontekstu_zwraca_baze():
    dolny, gorny = progi_rsi(None, None)
    assert dolny == RSI_DOLNY_BAZA
    assert gorny == RSI_GORNY_BAZA


def test_rsi_trend_strong_rozsuwa():
    dolny, gorny = progi_rsi("TREND_STRONG", None)
    assert dolny == 20.0
    assert gorny == 80.0


def test_rsi_ranging_zsuwa():
    dolny, gorny = progi_rsi("RANGING", None)
    assert dolny == 35.0
    assert gorny == 65.0


def test_rsi_wysoka_zmiennosc_rozsuwa_dalej():
    dolny, gorny = progi_rsi(None, 0.06)   # >5%
    assert dolny == 25.0   # 30 - 5
    assert gorny == 75.0   # 70 + 5


def test_rsi_niska_zmiennosc_zsuwa():
    dolny, gorny = progi_rsi(None, 0.005)  # <1%
    assert dolny == 33.0   # 30 + 3
    assert gorny == 67.0   # 70 - 3


def test_rsi_prog_dokladnie_na_granicy_zmiennosci():
    """Granica: atr_pct == ATR_PCT_WYSOKA (0.05) → rozsunięcie (>=)."""
    dolny, gorny = progi_rsi(None, 0.05)
    assert dolny == 25.0
    assert gorny == 75.0


def test_rsi_klamry_bezpieczenstwa():
    """Skrajny przypadek: trend + bardzo wysoka zmienność nie wyjdzie poza granice."""
    dolny, gorny = progi_rsi("TREND_STRONG", 0.50)
    assert dolny >= RSI_DOLNY_MIN
    assert gorny <= RSI_GORNY_MAX


# ── prog_adx ─────────────────────────────────────────────────────────────────

def test_adx_bez_kontekstu_baza():
    assert prog_adx(None, None) == ADX_BAZA


def test_adx_chaos_podnosi_prog():
    assert prog_adx("VOLATILE", None) == 30.0
    assert prog_adx("PANIC", None) == 30.0


def test_adx_trend_strong_obniza():
    assert prog_adx("TREND_STRONG", None) == 22.0


def test_adx_klamry():
    assert ADX_MIN <= prog_adx("VOLATILE", 0.99) <= ADX_MAX


# ── NeuronRSI z kontekstem ───────────────────────────────────────────────────

def test_neuron_rsi_bez_rezimu_zachowuje_stare_progi():
    """Prawo XV: brak _REZIM → próg 30/70 (zero regresji)."""
    n = NeuronRSI()
    # RSI=29 bez kontekstu → LONG (wyprzedany, próg 30)
    s = n.interpretuj({"RSI_14": 29.0})
    assert s.kierunek == "LONG"


def test_neuron_rsi_trend_strong_nie_gra_kontra_przy_72():
    """W TREND_STRONG próg górny=80 → RSI=72 NIE jest jeszcze SHORT (lekki byk)."""
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": 72.0, "_REZIM": "TREND_STRONG"})
    assert s.kierunek == "LONG"  # 72 < 80, > 50 → lekki byk


def test_neuron_rsi_bazowo_72_jest_short():
    """Bez trendu RSI=72 > 70 → SHORT (kontrast z testem wyżej)."""
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": 72.0})
    assert s.kierunek == "SHORT"


def test_neuron_rsi_ranging_lapie_66_jako_short():
    """W RANGING próg górny=65 → RSI=66 JEST SHORT (mean-reversion)."""
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": 66.0, "_REZIM": "RANGING"})
    assert s.kierunek == "SHORT"


def test_neuron_rsi_none_neutral():
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": None})
    assert s.kierunek == "NEUTRAL"


# ── NeuronADX z kontekstem ───────────────────────────────────────────────────

def test_neuron_adx_chaos_wymaga_mocniejszego_trendu():
    """W VOLATILE próg=30, prog_brak=25 → ADX=24 to 'brak trendu'."""
    n = NeuronADX()
    s = n.interpretuj({"ADX_14": 24.0, "DI_PLUS": 30.0, "DI_MINUS": 10.0,
                       "_REZIM": "VOLATILE"})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_neuron_adx_bazowo_24_to_slaby_trend_nie_zero():
    """Bez reżimu prog_brak=20 → ADX=24 przechodzi (trend, choć słaby)."""
    n = NeuronADX()
    s = n.interpretuj({"ADX_14": 24.0, "DI_PLUS": 30.0, "DI_MINUS": 10.0})
    assert s.kierunek == "LONG"


def test_neuron_adx_none_neutral():
    n = NeuronADX()
    s = n.interpretuj({"ADX_14": None})
    assert s.kierunek == "NEUTRAL"


def test_neuron_adx_trend_strong_nizszy_prog_lapie_21():
    """TREND_STRONG prog=22, prog_brak=17 → ADX=21 przechodzi jako trend."""
    n = NeuronADX()
    s = n.interpretuj({"ADX_14": 21.0, "DI_PLUS": 30.0, "DI_MINUS": 10.0,
                       "_REZIM": "TREND_STRONG"})
    assert s.kierunek == "LONG"
