"""
Testy W-384: Konfluencja Multi-Timeframe na poziomie roju.
REGUŁA TEST-GRANIC: brak stosu TF, brak kierunku, za mało barów, zgodność vs konflikt, weto.
"""

import numpy as np

from imperium.legiony.mtf_konfluencja import (
    ocena_konfluencji_tf, _agreguj, _kierunek_trendu, _ema, _STOS_TF,
)


def _bary_trend(n, nachylenie, start=100.0, szum=0.0, seed=0):
    """Bary z liniowym trendem (nachylenie>0 = wzrost)."""
    rng = np.random.default_rng(seed)
    bary = []
    cena = start
    for i in range(n):
        cena = start + nachylenie * i + (rng.normal(0, szum) if szum else 0)
        bary.append({"open": cena, "high": cena * 1.005, "low": cena * 0.995,
                     "close": cena, "volume": 1000.0, "timestamp": i})
    return bary


# ── _ema / _agreguj ──────────────────────────────────────────────────────────

def test_ema_stala_seria():
    assert _ema(np.array([5.0] * 20), 10) == 5.0


def test_agreguj_grupuje_poprawnie():
    bary = _bary_trend(24, nachylenie=1.0)
    agg = _agreguj(bary, 6)  # 24/6 = 4 bary wyższego TF
    assert len(agg) == 4
    # pierwszy agregat: open z baru 0, close z baru 5
    assert agg[0]["open"] == bary[0]["open"]
    assert agg[0]["close"] == bary[5]["close"]
    # high = max z grupy
    assert agg[0]["high"] == max(b["high"] for b in bary[:6])


def test_agreguj_pomija_niepelna_grupe():
    bary = _bary_trend(25, nachylenie=1.0)  # 25 = 4×6 + 1 (ostatni niepełny)
    agg = _agreguj(bary, 6)
    assert len(agg) == 4  # niepełna grupa pominięta (bez lookahead)


# ── _kierunek_trendu ─────────────────────────────────────────────────────────

def test_kierunek_trendu_wzrost():
    bary = _bary_trend(250, nachylenie=0.5)
    assert _kierunek_trendu(bary) == "LONG"


def test_kierunek_trendu_spadek():
    bary = _bary_trend(250, nachylenie=-0.5, start=300.0)
    assert _kierunek_trendu(bary) == "SHORT"


def test_kierunek_trendu_za_malo_barow():
    bary = _bary_trend(30, nachylenie=0.5)
    assert _kierunek_trendu(bary) == "NEUTRAL"  # < _MIN_BAROW_TF


# ── ocena_konfluencji_tf ─────────────────────────────────────────────────────

def test_konfluencja_brak_kierunku():
    bary = _bary_trend(500, 0.5)
    o = ocena_konfluencji_tf(bary, "1h", "NEUTRAL")
    assert o["mnoznik"] == 1.0
    assert o["weto"] is False


def test_konfluencja_brak_stosu_tf():
    bary = _bary_trend(500, 0.5)
    o = ocena_konfluencji_tf(bary, "7h", "LONG")  # brak "7h" w _STOS_TF
    assert o["mnoznik"] == 1.0
    assert "brak stosu" in o["werdykt"]


def test_konfluencja_zgodna_wzmacnia():
    # Silny trend wzrostowy, decyzja LONG → wyższe TF potwierdzają → mnoznik > 1
    bary = _bary_trend(2000, nachylenie=0.5)
    o = ocena_konfluencji_tf(bary, "1h", "LONG")
    assert o["wyrownanie"] > 0
    assert o["mnoznik"] > 1.0
    assert o["weto"] is False


def test_konfluencja_konflikt_tlumi():
    # Silny trend wzrostowy, ale decyzja SHORT → konflikt → mnoznik < 1
    bary = _bary_trend(2000, nachylenie=0.5)
    o = ocena_konfluencji_tf(bary, "1h", "SHORT")
    assert o["wyrownanie"] < 0
    assert o["mnoznik"] < 1.0


def test_konfluencja_weto_przeciwtrend():
    # Pełny konflikt + prog_weta=-0.5 → weto
    bary = _bary_trend(2000, nachylenie=0.5)
    o = ocena_konfluencji_tf(bary, "1h", "SHORT", prog_weta=-0.5)
    assert o["weto"] is True


def test_konfluencja_mnoznik_w_zakresie():
    bary = _bary_trend(2000, nachylenie=0.5)
    for kier in ("LONG", "SHORT"):
        o = ocena_konfluencji_tf(bary, "4h", kier)
        assert 0.5 <= o["mnoznik"] <= 1.2


def test_konfluencja_tf_kierunki_zwracane():
    bary = _bary_trend(2000, nachylenie=0.5)
    o = ocena_konfluencji_tf(bary, "1h", "LONG")
    assert set(o["tf_kierunki"].keys()) == set(_STOS_TF["1h"].keys())


# ── integracja z Dyrygentem (opt-in, domyślnie OFF) ──────────────────────────

def test_dyrygent_mtf_domyslnie_off():
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    leg = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1)
    d = Dyrygent(legatus=leg, kalkulator=KalkulatorLewara(),
                 engine=PaperTradingEngine(kapital_startowy=10000))
    assert d.mtf_konfluencja is False  # opt-in: zero zmiany zachowania domyślnie
    assert d.mtf_weto_przeciwtrend is False
