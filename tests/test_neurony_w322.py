"""
Testy neuronów W-322 (scalp/swing/invest) — Reguła Test-Granic (Prawo XXI):
zero/None, znak graniczny, próg dokładny.
"""
from imperium.legiony.neurony.zagrozenie import NeuronAmihudIlliquidity, NeuronPiCycleTop
from imperium.legiony.neurony.wolumen import NeuronDeltaDivergence, NeuronAnchoredVWAP
from imperium.legiony.neurony.struktura import NeuronVolumeProfile


# ── Z-06 Amihud Illiquidity (meta-brama, pewnosc_przeciwnika) ──
def test_amihud_none_neutral():
    s = NeuronAmihudIlliquidity().interpretuj({})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0
    assert getattr(s, "pewnosc_przeciwnika", 0) == 0

def test_amihud_plynne_brak_tlumienia():
    s = NeuronAmihudIlliquidity().interpretuj({"AMIHUD_20": 0.1})
    assert s.kierunek == "NEUTRAL"
    assert getattr(s, "pewnosc_przeciwnika", 0) == 0

def test_amihud_krucha_plynnosc_tlumi():
    s = NeuronAmihudIlliquidity().interpretuj({"AMIHUD_20": 5.0})
    assert s.kierunek == "NEUTRAL"           # nigdy kierunkowy
    assert s.pewnosc_przeciwnika > 0.5       # silne tłumienie

def test_amihud_prog_dokladny_spokoj():
    # dokładnie próg spokoju (0.5): warunek < prog → False, więc tłumi minimalnie
    s = NeuronAmihudIlliquidity().interpretuj({"AMIHUD_20": 0.5})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc_przeciwnika == 0.0      # przy progu tłumienie = 0 (rozp od prog)


# ── Z-07 Pi Cycle Top ──
def test_picycle_none_neutral():
    s = NeuronPiCycleTop().interpretuj({})
    assert s.kierunek == "NEUTRAL"

def test_picycle_cross_od_dolu_short():
    s = NeuronPiCycleTop().interpretuj({"PI_111": 105.0, "PI_350X2": 100.0,
                                        "PI_111_PREV": 98.0, "PI_350X2_PREV": 100.0})
    assert s.kierunek == "SHORT" and s.pewnosc >= 0.8

def test_picycle_daleko_neutral():
    s = NeuronPiCycleTop().interpretuj({"PI_111": 50.0, "PI_350X2": 100.0,
                                        "PI_111_PREV": 49.0, "PI_350X2_PREV": 100.0})
    assert s.kierunek == "NEUTRAL"

def test_picycle_blisko_slaby_short():
    # ratio 0.95 ≥ prog 0.92, brak świeżego crossu → słaby SHORT
    s = NeuronPiCycleTop().interpretuj({"PI_111": 95.0, "PI_350X2": 100.0,
                                        "PI_111_PREV": 94.0, "PI_350X2_PREV": 100.0})
    assert s.kierunek == "SHORT" and 0 < s.pewnosc < 0.6


# ── V-06 Delta Divergence ──
def test_deltadiv_none_neutral():
    assert NeuronDeltaDivergence().interpretuj({}).kierunek == "NEUTRAL"

def test_deltadiv_zero_neutral():
    s = NeuronDeltaDivergence().interpretuj({"DELTA_DIV": 0.0})
    assert s.kierunek == "NEUTRAL" and s.pewnosc == 0.0

def test_deltadiv_dodatni_long():
    s = NeuronDeltaDivergence().interpretuj({"DELTA_DIV": 0.5})
    assert s.kierunek == "LONG"

def test_deltadiv_ujemny_short():
    s = NeuronDeltaDivergence().interpretuj({"DELTA_DIV": -0.5})
    assert s.kierunek == "SHORT"

def test_deltadiv_prog_dokladny_neutral():
    # |0.15| ≤ prog 0.15 → NEUTRAL (krawędź wyłączona)
    assert NeuronDeltaDivergence().interpretuj({"DELTA_DIV": 0.15}).kierunek == "NEUTRAL"


# ── V-07 Anchored VWAP ──
def test_avwap_none_neutral():
    assert NeuronAnchoredVWAP().interpretuj({"AVWAP": None, "CLOSE": 100}).kierunek == "NEUTRAL"

def test_avwap_nad_long():
    s = NeuronAnchoredVWAP().interpretuj({"AVWAP": 100.0, "CLOSE": 105.0})
    assert s.kierunek == "LONG"

def test_avwap_pod_short():
    s = NeuronAnchoredVWAP().interpretuj({"AVWAP": 100.0, "CLOSE": 95.0})
    assert s.kierunek == "SHORT"

def test_avwap_w_pasmie_neutral():
    # 0.3% < prog 0.5% → NEUTRAL
    s = NeuronAnchoredVWAP().interpretuj({"AVWAP": 100.0, "CLOSE": 100.3})
    assert s.kierunek == "NEUTRAL"


# ── VP-01 Volume Profile ──
def test_vpoc_none_neutral():
    assert NeuronVolumeProfile().interpretuj({}).kierunek == "NEUTRAL"

def test_vpoc_ponizej_va_long():
    s = NeuronVolumeProfile().interpretuj({"VPOC": 100.0, "VA_HIGH": 105.0,
                                           "VA_LOW": 95.0, "CLOSE": 90.0})
    assert s.kierunek == "LONG"

def test_vpoc_powyzej_va_short():
    s = NeuronVolumeProfile().interpretuj({"VPOC": 100.0, "VA_HIGH": 105.0,
                                           "VA_LOW": 95.0, "CLOSE": 110.0})
    assert s.kierunek == "SHORT"

def test_vpoc_w_value_area_neutral():
    s = NeuronVolumeProfile().interpretuj({"VPOC": 100.0, "VA_HIGH": 105.0,
                                           "VA_LOW": 95.0, "CLOSE": 100.0})
    assert s.kierunek == "NEUTRAL"

def test_vpoc_krawedz_va_low_neutral():
    # CLOSE == VA_LOW: warunek < VA_LOW False → NEUTRAL (krawędź = w strefie)
    s = NeuronVolumeProfile().interpretuj({"VPOC": 100.0, "VA_HIGH": 105.0,
                                           "VA_LOW": 95.0, "CLOSE": 95.0})
    assert s.kierunek == "NEUTRAL"
