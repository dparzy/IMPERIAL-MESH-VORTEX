"""Testy Trybu Praeda (W-291) — Okazjon: auto-skalowana, kontrolowana chciwość."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imperium.pretorianie.praeda import Okazjon, SilaOkazji, PROG_OKAZJI, PROG_PYRAMIDA


class _R:
    def __init__(self, pew=0.92, rez="TREND_STRONG", akt=40, zgod=32):
        self.pewnosc_agregatu = pew; self.rezim = rez
        self.aktywnych_neuronow = akt; self.zgodnych_neuronow = zgod


def test_silna_okazja_skaluje_agresje():
    ok = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "EVENT_PROB_WZROSTU": 85, "EVENT_N": 3},
                        "LONG", dd_normal=True)
    assert ok.potwierdzona and ok.sila >= PROG_OKAZJI
    assert ok.mnoznik_lewara > 1.0 and ok.mnoznik_rozmiaru > 1.0
    assert ok.pyramiding == (ok.sila >= PROG_PYRAMIDA)


def test_drawdown_wylacza_praede():
    """DD-control ≠ NORMAL → Praeda śpi (sila=0, mnożniki 1.0) — łup tylko gdy wygrywasz."""
    ok = Okazjon().ocen(_R(), {"VPIN_50": 0.1}, "LONG", dd_normal=False)
    assert ok.sila == 0.0 and not ok.potwierdzona
    assert ok.mnoznik_lewara == 1.0 and ok.mnoznik_rozmiaru == 1.0


def test_toksyczny_vpin_weto():
    """VPIN > 0.7 → toksyczny flow → zero łupu (bramka bezpieczeństwa)."""
    ok = Okazjon().ocen(_R(), {"VPIN_50": 0.85}, "LONG", dd_normal=True)
    assert not ok.potwierdzona and "VPIN" in ok.powody[0]


def test_blackout_fomc_weto():
    ok = Okazjon().ocen(_R(), {"EVENT_BLACKOUT": True, "VPIN_50": 0.2}, "LONG", dd_normal=True)
    assert not ok.potwierdzona and "BLACKOUT" in ok.powody[0]


def test_kaskada_weto():
    ok = Okazjon().ocen(_R(), {"CASCADE_FLAG": True, "VPIN_50": 0.2}, "LONG", dd_normal=True)
    assert not ok.potwierdzona and "askad" in ok.powody[0]


def test_slaba_okazja_brak_wzmocnienia():
    """Słaba zgoda + RANGING → sila < próg → mnożniki 1.0 (zwykła pozycja)."""
    ok = Okazjon().ocen(_R(pew=0.6, rez="RANGING", zgod=12), {"VPIN_50": 0.3},
                        "LONG", dd_normal=True)
    assert not ok.potwierdzona
    assert ok.mnoznik_lewara == 1.0 and ok.mnoznik_rozmiaru == 1.0


def test_sentyment_kontrarian_zgodny():
    """Fear&Greed ekstremalny strach + LONG → składnik sentymentu dodaje siły."""
    bez = Okazjon().ocen(_R(pew=0.8, zgod=24), {"VPIN_50": 0.2}, "LONG", dd_normal=True)
    z = Okazjon().ocen(_R(pew=0.8, zgod=24),
                       {"VPIN_50": 0.2, "FEAR_GREED_INDEX": 8}, "LONG", dd_normal=True)
    assert z.sila >= bez.sila


def test_sentyment_niezgodny_nie_pomaga():
    """Ekstremalna chciwość (F&G=90) przy LONG → sentyment=0 (nie kontrarian)."""
    z = Okazjon().ocen(_R(pew=0.8, zgod=24),
                       {"VPIN_50": 0.2, "FEAR_GREED_INDEX": 90}, "LONG", dd_normal=True)
    assert isinstance(z, SilaOkazji)
    assert 0.0 <= z.sila <= 1.0


def test_event_za_malo_n_ignorowany():
    """Augur z n<2 nie wchodzi do konfluencji (Prawo I)."""
    a = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "EVENT_PROB_WZROSTU": 90, "EVENT_N": 1},
                       "LONG", dd_normal=True)
    assert isinstance(a, SilaOkazji)


def test_sila_zawsze_w_zakresie():
    for pew in (0.55, 0.7, 0.85, 1.0):
        for rez in ("TREND_STRONG", "RANGING", "VOLATILE"):
            ok = Okazjon().ocen(_R(pew=pew, rez=rez), {"VPIN_50": 0.3}, "LONG", dd_normal=True)
            assert 0.0 <= ok.sila <= 1.0
            assert 1.0 <= ok.mnoznik_lewara <= 2.0
            assert 1.0 <= ok.mnoznik_rozmiaru <= 2.0


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    bl = 0
    for nm, f in fn:
        try:
            f(); print(f"  ✅ {nm}")
        except Exception as e:
            bl += 1; print(f"  ❌ {nm}: {e}")
    sys.exit(1 if bl else 0)


def test_radar_btc_wiatr_w_plecy():
    """BTC rośnie + LONG alta → bonus RadarBTC podnosi siłę okazji."""
    bez = Okazjon().ocen(_R(pew=0.8, zgod=24), {"VPIN_50": 0.2}, "LONG", dd_normal=True)
    z = Okazjon().ocen(_R(pew=0.8, zgod=24),
                       {"VPIN_50": 0.2, "BTC_TREND": 0.9}, "LONG", dd_normal=True)
    assert z.sila >= bez.sila, "BTC w trendzie↑ to wiatr w plecy dla LONG alta"


def test_radar_btc_weto_spadajacy_btc():
    """BTC mocno spada + LONG alta → WETO (alty lecą za BTC, lead-lag)."""
    ok = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "BTC_TREND": -0.8}, "LONG", dd_normal=True)
    assert not ok.potwierdzona and "BTC spada" in ok.powody[0]


def test_radar_btc_weto_short_pod_prad():
    ok = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "BTC_TREND": 0.9}, "SHORT", dd_normal=True)
    assert not ok.potwierdzona and "BTC mocno rośnie" in ok.powody[0]
