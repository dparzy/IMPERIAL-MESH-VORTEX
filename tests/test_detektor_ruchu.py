"""Testy Z-05 NeuronDetektorRuchu (W-315) — klimaks dwukierunkowy, granice."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.neurony.zagrozenie import NeuronDetektorRuchu


def _w(roc, rsi, vol_spike, lookback=6):
    """Buduje wskazniki: seria close z zadanym ROC, RSI, vol_spike."""
    baza = 100.0
    cena = round(baza * (1 + roc), 6)     # zaokrąglenie tnie szum float na granicy progu
    closes = [baza] * lookback + [cena]   # closes[-1-lookback]=baza, closes[-1]=cena
    return {
        "CLOSE_SERIES_20": closes,
        "RSI_14": rsi,
        "VOLUME": vol_spike * 1000.0,
        "VOLUME_MA20": 1000.0,
    }


def _n():
    return NeuronDetektorRuchu()


# ─── Abstynencja (Prawo XV) ────────────────────────────────────────────────────

def test_brak_danych_neutral():
    assert _n().interpretuj({}).kierunek == "NEUTRAL"
    assert _n().interpretuj({"CLOSE_SERIES_20": [1, 2]}).kierunek == "NEUTRAL"


def test_za_krotka_seria_neutral():
    s = _n().interpretuj({"CLOSE_SERIES_20": [100, 101], "RSI_14": 80,
                          "VOLUME": 3000, "VOLUME_MA20": 1000})
    assert s.kierunek == "NEUTRAL"


# ─── Szczyt klimaksowy → SHORT ─────────────────────────────────────────────────

def test_szczyt_klimaksowy_short():
    s = _n().interpretuj(_w(roc=0.20, rsi=75, vol_spike=3.0))
    assert s.kierunek == "SHORT"
    assert s.pewnosc >= 0.55


def test_szczyt_silniejszy_wyzsza_pewnosc():
    slaby = _n().interpretuj(_w(roc=0.15, rsi=70, vol_spike=2.0))
    mocny = _n().interpretuj(_w(roc=0.40, rsi=95, vol_spike=5.0))
    assert mocny.pewnosc > slaby.pewnosc


# ─── Dołek kapitulacyjny → LONG ────────────────────────────────────────────────

def test_dolek_kapitulacyjny_long():
    s = _n().interpretuj(_w(roc=-0.20, rsi=25, vol_spike=3.0))
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.55


# ─── Granice (Prawo XXI) ───────────────────────────────────────────────────────

def test_granica_roc_dokladnie_prog_pump():
    """ROC == +15%, RSI == 70, vol == 2.0 → dokładnie próg, SHORT (≥)."""
    s = _n().interpretuj(_w(roc=0.15, rsi=70.0, vol_spike=2.0))
    assert s.kierunek == "SHORT"


def test_granica_roc_dokladnie_prog_dump():
    s = _n().interpretuj(_w(roc=-0.15, rsi=30.0, vol_spike=2.0))
    assert s.kierunek == "LONG"


def test_roc_duzy_ale_brak_wolumenu_neutral():
    """Pump bez klimaksu wolumenu → NIE szczyt (brak potwierdzenia)."""
    s = _n().interpretuj(_w(roc=0.30, rsi=80, vol_spike=1.5))
    assert s.kierunek == "NEUTRAL"


def test_roc_duzy_ale_rsi_nieekstremalny_neutral():
    """Pump +20% ale RSI 60 (nie wykupienie) → NEUTRAL."""
    s = _n().interpretuj(_w(roc=0.20, rsi=60, vol_spike=3.0))
    assert s.kierunek == "NEUTRAL"


def test_pump_z_oversold_nie_short():
    """Sprzeczność: ROC dodatni ale RSI niski → nie SHORT, nie LONG (NEUTRAL)."""
    s = _n().interpretuj(_w(roc=0.20, rsi=25, vol_spike=3.0))
    assert s.kierunek == "NEUTRAL"


def test_spokoj_neutral():
    """Mały ruch, RSI neutralny, wolumen normalny → NEUTRAL."""
    s = _n().interpretuj(_w(roc=0.02, rsi=50, vol_spike=1.0))
    assert s.kierunek == "NEUTRAL"


def test_vol_ma_zero_neutral():
    s = _n().interpretuj({"CLOSE_SERIES_20": [100]*7 + [120], "RSI_14": 80,
                          "VOLUME": 3000, "VOLUME_MA20": 0.0})
    assert s.kierunek == "NEUTRAL"


# ─── Rejestracja w roju ────────────────────────────────────────────────────────

def test_z05_zarejestrowany():
    from imperium.legiony.rejestr import wszystkie_neurony
    klucze = {n.KLUCZ for n in wszystkie_neurony()}
    assert "Z-05" in klucze


def test_z05_kategoria_i_dostepny():
    n = NeuronDetektorRuchu()
    assert n.KATEGORIA == "Z"
    assert getattr(n, "DOSTEPNY", True) is True
