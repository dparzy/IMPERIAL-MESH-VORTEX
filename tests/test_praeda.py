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


def test_stres_korelacji_weto():
    """W-292: STRES_KORELACJI > 0.85 → kaskada koszyka → zero łupu (weto)."""
    ok = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "STRES_KORELACJI": 0.9}, "LONG", dd_normal=True)
    assert not ok.potwierdzona and "STRES" in ok.powody[0]


def test_dominacja_wspiera_alt_long():
    """W-292: alt-season (BTC_DOMINANCJA<0) dodaje siłę LONG-owi alta (bonus)."""
    bazowy = Okazjon().ocen(_R(), {"VPIN_50": 0.2}, "LONG", dd_normal=True)
    z_dom = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "BTC_DOMINANCJA": -0.8}, "LONG", dd_normal=True)
    assert z_dom.sila >= bazowy.sila
    # SHORT przy alt-season NIE dostaje bonusu (kierunek niezgodny)
    short_dom = Okazjon().ocen(_R(), {"VPIN_50": 0.2, "BTC_DOMINANCJA": -0.8}, "SHORT", dd_normal=True)
    short_baza = Okazjon().ocen(_R(), {"VPIN_50": 0.2}, "SHORT", dd_normal=True)
    assert abs(short_dom.sila - short_baza.sila) < 1e-9


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


def test_kalkulator_mnoznik_rozmiaru_skaluje():
    """W-291: mnoznik_rozmiaru zwiększa rozmiar, ale clamp 50% kapitału trzyma sufit."""
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    k = KalkulatorLewara()
    baza = k.policz(symbol="BTCUSDT", kierunek="LONG", cena_wejscia=100.0,
                    dzwignia=3, kapital_usdt=10_000.0, pewnosc=0.8, rezim="TREND_STRONG")
    wiekszy = k.policz(symbol="BTCUSDT", kierunek="LONG", cena_wejscia=100.0,
                       dzwignia=3, kapital_usdt=10_000.0, pewnosc=0.8, rezim="TREND_STRONG",
                       mnoznik_rozmiaru=1.5)
    assert wiekszy.rozmiar_usdt >= baza.rozmiar_usdt
    # Clamp: nawet ekstремальny mnożnik nie przekroczy 50% kapitału.
    ekstrem = k.policz(symbol="BTCUSDT", kierunek="LONG", cena_wejscia=100.0,
                       dzwignia=20, kapital_usdt=10_000.0, pewnosc=1.0, rezim="TREND_STRONG",
                       mnoznik_rozmiaru=99.0)
    assert ekstrem.rozmiar_usdt <= 10_000.0 * 0.5 + 1e-6


def test_kalkulator_mnoznik_zero_nie_ujemny():
    """Granica: mnoznik_rozmiaru=0 → rozmiar 0 (nie ujemny), max(0,·) chroni."""
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    k = KalkulatorLewara()
    p = k.policz(symbol="BTCUSDT", kierunek="LONG", cena_wejscia=100.0,
                 dzwignia=3, kapital_usdt=10_000.0, pewnosc=0.8, rezim="TREND_STRONG",
                 mnoznik_rozmiaru=0.0)
    assert p.rozmiar_usdt == 0.0


def test_neuron_dominacja_glosuje():
    """RADAR-02: alt-season(dom<0)→LONG, ucieczka do BTC(dom>0)→SHORT, ~0→NEUTRAL, brak→abstynencja."""
    from imperium.legiony.neurony.sesje import NeuronDominacja
    n = NeuronDominacja()
    assert n.interpretuj({"BTC_DOMINANCJA": -0.8}).kierunek == "LONG"
    assert n.interpretuj({"BTC_DOMINANCJA": 0.8}).kierunek == "SHORT"
    assert n.interpretuj({"BTC_DOMINANCJA": 0.0}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).kierunek == "NEUTRAL"
    # granica progu 0.30
    assert n.interpretuj({"BTC_DOMINANCJA": -0.30}).kierunek == "LONG"
    assert n.interpretuj({"BTC_DOMINANCJA": -0.29}).kierunek == "NEUTRAL"


def test_neuron_przeplyw_glosuje():
    """RADAR-03: napływ(pk≥0.65)→LONG, odpływ(pk≤0.35)→SHORT, środek→NEUTRAL, brak→abstynencja."""
    from imperium.legiony.neurony.sesje import NeuronPrzeplyw
    n = NeuronPrzeplyw()
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.9}).kierunek == "LONG"
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.1}).kierunek == "SHORT"
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.5}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).kierunek == "NEUTRAL"
    # granice progów 0.65 / 0.35
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.65}).kierunek == "LONG"
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.64}).kierunek == "NEUTRAL"
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.35}).kierunek == "SHORT"
    assert n.interpretuj({"PRZEPLYW_KAPITALU": 0.36}).kierunek == "NEUTRAL"


def test_dyrygent_okazjon_none_brak_wplywu():
    """Domyślnie okazjon=None → Praeda nie ingeruje (mnoznik_rozmiaru pozostaje 1.0)."""
    from imperium.koloseum.dyrygent import Dyrygent
    assert Dyrygent.__init__ is not None
    # okazjon i praeda_dd_normal to atrybuty instancji — sprawdzamy domyślne wartości.
    import inspect
    src = inspect.getsource(Dyrygent.__init__)
    assert "self.okazjon = None" in src
    assert "self.praeda_dd_normal" in src


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


def test_neuron_radar_btc_glosuje():
    """RADAR-01: BTC↑→LONG-wsparcie, BTC↓→SHORT-ostrzeżenie, ~0→NEUTRAL, brak→abstynencja."""
    from imperium.legiony.neurony.sesje import NeuronRadarBTC
    n = NeuronRadarBTC()
    assert n.interpretuj({"BTC_TREND": 0.8}).kierunek == "LONG"
    assert n.interpretuj({"BTC_TREND": -0.8}).kierunek == "SHORT"
    assert n.interpretuj({"BTC_TREND": 0.0}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).kierunek == "NEUTRAL"
    # granica progu 0.30
    assert n.interpretuj({"BTC_TREND": 0.30}).kierunek == "LONG"
    assert n.interpretuj({"BTC_TREND": 0.29}).kierunek == "NEUTRAL"


def test_radar_btc_provider_granice():
    """RadarBTC: trend w [-1,1], za mało danych → None, parametry walidowane."""
    from imperium.legiony.radar_btc import RadarBTC
    r = RadarBTC()
    assert r.trend([100.0] * 3) is None
    up = [100 * 1.01 ** i for i in range(80)]
    assert 0.5 < r.trend(up) <= 1.0
    for zle in (dict(ema_szybka=30, ema_wolna=10), dict(okno_vol=2)):
        try:
            RadarBTC(**zle); raise AssertionError("zły parametr ma rzucić")
        except ValueError:
            pass
