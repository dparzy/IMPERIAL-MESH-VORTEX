"""
W-335 C-01 — testy Cross-sectional Relative Strength (neuron + helper koszyka).

Reguła Test-Granic: brak CROSS_RS→NEUTRAL, próg słaby/silny, znak, koszyk<2,
zerowa wariancja koszyka, brak lookahead (zwrot do bara t).
"""

from imperium.legiony.neurony.przekroj import NeuronRelativeStrength
from imperium.legiony.przekroj_koszyka import cross_sectional_rs, zwrot_lookback
from imperium.legiony.rejestr import wszystkie_neurony


# ── Neuron C-01 ──────────────────────────────────────────────────────────────

def test_brak_cross_rs_neutral_abstynuje():
    """Prawo XV: bez koszyka (brak CROSS_RS) neuron abstynuje (NEUTRAL pewność 0)."""
    n = NeuronRelativeStrength()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_lider_koszyka_long():
    n = NeuronRelativeStrength()
    s = n.interpretuj({"CROSS_RS": 1.5})
    assert s.kierunek == "LONG"
    assert s.pewnosc > 0.0


def test_maruder_koszyka_short():
    n = NeuronRelativeStrength()
    s = n.interpretuj({"CROSS_RS": -1.5})
    assert s.kierunek == "SHORT"


def test_blisko_zera_neutral():
    """|RS| < prog_słaby (0.3) → zachowuje się jak koszyk → NEUTRAL."""
    n = NeuronRelativeStrength()
    s = n.interpretuj({"CROSS_RS": 0.1})
    assert s.kierunek == "NEUTRAL"


def test_granica_prog_slaby_dokladnie():
    """RS dokładnie na progu słabym (0.3) → już głosuje (nie NEUTRAL)."""
    n = NeuronRelativeStrength()
    s = n.interpretuj({"CROSS_RS": 0.3})
    assert s.kierunek == "LONG"  # >= prog_słaby, dodatni


def test_strefa_posrednia_slabszy_glos():
    """RS w (0.3, 1.0) → LONG ale słabszy niż lider."""
    n = NeuronRelativeStrength()
    posr = n.interpretuj({"CROSS_RS": 0.6})
    lider = n.interpretuj({"CROSS_RS": 1.5})
    assert posr.kierunek == "LONG"
    assert posr.pewnosc < lider.pewnosc


def test_pewnosc_klamrowana():
    """Skrajne RS nie przekracza 0.70 pewności."""
    n = NeuronRelativeStrength()
    s = n.interpretuj({"CROSS_RS": 10.0})
    assert s.pewnosc <= 0.70


def test_c01_zarejestrowany_kategoria_C():
    klucze = {x.KLUCZ: x for x in wszystkie_neurony()}
    assert "C-01" in klucze
    assert klucze["C-01"].KATEGORIA == "C"


# ── Helper koszyka ───────────────────────────────────────────────────────────

def test_zwrot_lookback_za_malo_danych():
    assert zwrot_lookback([100.0], 5) is None


def test_zwrot_lookback_oblicza():
    close = [100.0, 101.0, 102.0, 103.0, 104.0, 110.0]  # 6 barów
    z = zwrot_lookback(close, 5)  # (110-100)/100
    assert abs(z - 0.10) < 1e-9


def test_cross_sectional_rs_lider_dodatni_maruder_ujemny():
    # ETH rośnie najmocniej, DOGE spada → ETH z-score>0, DOGE<0
    close = {
        "BTC": [100.0] * 25 + [105.0],   # +5%
        "ETH": [100.0] * 25 + [120.0],   # +20% lider
        "DOGE": [100.0] * 25 + [95.0],   # -5% maruder
    }
    rs = cross_sectional_rs(close, lookback=24)
    assert rs["ETH"] > 0
    assert rs["DOGE"] < 0
    assert rs["ETH"] > rs["BTC"] > rs["DOGE"]


def test_cross_sectional_rs_jeden_symbol_pusty():
    """Koszyk <2 symbole → brak przewagi przekrojowej → pusty dict."""
    rs = cross_sectional_rs({"BTC": [100.0] * 30}, lookback=24)
    assert rs == {}


def test_cross_sectional_rs_identyczny_ruch_pusty():
    """Koszyk porusza się identycznie (zerowa wariancja) → pusty dict (brak rozróżnienia)."""
    close = {s: [100.0] * 25 + [110.0] for s in ("BTC", "ETH", "SOL")}
    rs = cross_sectional_rs(close, lookback=24)
    assert rs == {}


def test_cross_sectional_rs_z_scores_sumuja_do_zera():
    """Z-score: średnia ~0 (własność standaryzacji)."""
    close = {
        "BTC": [100.0] * 25 + [105.0],
        "ETH": [100.0] * 25 + [115.0],
        "SOL": [100.0] * 25 + [95.0],
    }
    rs = cross_sectional_rs(close, lookback=24)
    assert abs(sum(rs.values())) < 1e-9
