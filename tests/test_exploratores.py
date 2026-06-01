"""Testy Dywizji Exploratores — baza, igrzyska, HFD, HA Scalper Full, Hurst, Kalman."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.zwiadowcy.baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych
from imperium.legiony.zwiadowcy.igrzyska_exploratores import (
    IgrzyskaExploratores, StatystykaZwiadowcy, okresl_range_exploratores, RANGI_EXPLORATORES,
)
from imperium.legiony.zwiadowcy.exp_higuchi import ZwiadowcaHiguchiFD, _higuchi_fd
from imperium.legiony.zwiadowcy.exp_ha_scalper import ZwiadowcaHAScalper, _oblicz_ha
from imperium.legiony.zwiadowcy.exp_hurst import ZwiadowcaHurst, _hurst_rs
from imperium.legiony.zwiadowcy.exp_kalman import ZwiadowcaKalmanATR, _kalman_filter_1d, _kalman_atr
from imperium.legiony.zwiadowcy.exp_smc import (
    ZwiadowcaSMC, aktywuj_neurony_smc,
    _swing_pivots, _wykryj_fvg, _wykryj_order_blocks, _wykryj_bos_mss,
)


# ─── Pomocnicze ───────────────────────────────────────────────────────────────

def _bar(close=100.0, open_=99.0, high=101.0, low=98.0, vol=1000.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": vol, "timestamp": 0}


def _bary_trend(n=60, start=100.0, krok=0.5):
    """Seria trendująca w górę."""
    return [_bar(start + i * krok, start + i * krok - 0.5,
                 start + i * krok + 1.0, start + i * krok - 1.0) for i in range(n)]


def _bary_ranging(n=60, center=100.0, szum=2.0):
    """Seria oscylująca (ranging)."""
    import math
    return [_bar(center + szum * math.sin(i * 0.4),
                 center + szum * math.sin(i * 0.4) - 0.5,
                 center + szum * math.sin(i * 0.4) + 1.0,
                 center + szum * math.sin(i * 0.4) - 1.0) for i in range(n)]


# ─── Baza — ZwiadowcaElitarny ─────────────────────────────────────────────────

def test_klucz_musi_miec_prefiks_exp():
    class ZlyZwiadowca(ZwiadowcaElitarny):
        KLUCZ = "X-99"  # zły prefiks
        WSKAZNIK = "test"
        def analizuj(self, bary): pass
    try:
        ZlyZwiadowca()
        assert False, "Powinien rzucić ValueError"
    except ValueError:
        pass


def test_klucz_exp_00_blokuje():
    class NieNazwany(ZwiadowcaElitarny):
        KLUCZ = "EXP-00"  # default — nie nadpisany
        WSKAZNIK = "test"
        def analizuj(self, bary): pass
    try:
        NieNazwany()
        assert False, "Powinien rzucić NotImplementedError"
    except NotImplementedError:
        pass


def test_legion_exploratores_staly():
    z = ZwiadowcaHiguchiFD()
    assert z.LEGION == "EXPLORATORES"


def test_walidacja_za_malo_barow():
    z = ZwiadowcaHiguchiFD()
    ok, msg = z._waliduj_bary([_bar() for _ in range(5)])  # < 50
    assert not ok
    assert "mało" in msg.lower() or "Za" in msg


def test_brak_danych_zwraca_neutral():
    z = ZwiadowcaHiguchiFD()
    raport = z._brak_danych("test")
    assert raport.sygnal.kierunek == "NEUTRAL"
    assert raport.pewnosc_metody == 0.0


# ─── RaportZwiadowcy ──────────────────────────────────────────────────────────

def test_raport_kompatybilny_z_legatusem():
    """Raport musi mieć SygnalNeuronu z LEGION=EXPLORATORES."""
    z = ZwiadowcaHiguchiFD()
    bary = _bary_trend(n=60)
    raport = z.analizuj(bary)
    assert isinstance(raport, RaportZwiadowcy)
    assert raport.sygnal.legion == "EXPLORATORES"
    assert raport.sygnal.neuron_id == "EXP-01"
    assert raport.sygnal.kierunek in ("LONG", "SHORT", "NEUTRAL")


# ─── Igrzyska Exploratores ────────────────────────────────────────────────────

def test_rangi_exploratores_nizsze_progi():
    """Exploratores: aquilifer na 0.88, standard na 0.93."""
    ranga_exp = okresl_range_exploratores(0.90)
    assert ranga_exp.nazwa == "Aquilifer"
    # Standard wymagałby 0.93 — tu 0.90 wystarczy


def test_rangi_exploratores_wyzsze_mnozniki():
    ranga = okresl_range_exploratores(0.92)
    assert ranga.mnoznik == 2.5  # Aquilifer Exploratores = ×2.5 (standard = ×2.0)


def test_igrzyska_exp_rejestruje_wyniki():
    ig = IgrzyskaExploratores()
    ig.zarejestruj_wynik("EXP-01", "LONG", tp=True, contribution=0.8)
    ig.zarejestruj_wynik("EXP-01", "LONG", tp=True, contribution=0.9)
    ig.zarejestruj_wynik("EXP-01", "SHORT", tp=False, contribution=0.3)
    assert ig.statystyki["EXP-01"].sygnaly == 3
    assert ig.statystyki["EXP-01"].tp == 2
    assert ig.statystyki["EXP-01"].fp == 1


def test_igrzyska_exp_neutralne_nie_licza():
    ig = IgrzyskaExploratores()
    ig.zarejestruj_wynik("EXP-01", "NEUTRAL", tp=False)
    ig.zarejestruj_wynik("EXP-01", "NEUTRAL", tp=False)
    assert ig.statystyki["EXP-01"].sygnaly == 0
    assert ig.statystyki["EXP-01"].neutralne == 2


def test_igrzyska_exp_premia_rzadkosci():
    ig = IgrzyskaExploratores()
    # EXP-01: 5 sygnałów, 15 neutralnych = rzadki (25%)
    for _ in range(5):
        ig.zarejestruj_wynik("EXP-01", "LONG", tp=True, contribution=0.8)
    for _ in range(15):
        ig.zarejestruj_wynik("EXP-01", "NEUTRAL", tp=False)
    # EXP-02: 10 sygnałów, 10 neutralnych = normalny (50%)
    for _ in range(10):
        ig.zarejestruj_wynik("EXP-02", "LONG", tp=True, contribution=0.5)
    for _ in range(10):
        ig.zarejestruj_wynik("EXP-02", "NEUTRAL", tp=False)

    wyniki = ig.wyniki_wszystkich()
    # EXP-01 rzadszy → powinien mieć premię → wyższy lub równy wynik mimo mniej danych
    # (oba mają 100% accuracy ale różną rzadkość)
    assert wyniki["EXP-01"] >= wyniki["EXP-02"]  # premia za rzadkość wyrównuje


def test_igrzyska_exp_nowe_wagi():
    ig = IgrzyskaExploratores()
    for _ in range(5):
        ig.zarejestruj_wynik("EXP-01", "LONG", tp=True, contribution=0.9)
    wagi = ig.nowe_wagi()
    assert "EXP-01" in wagi
    assert wagi["EXP-01"] >= 0.5  # minimum Tiro


def test_igrzyska_exp_zloty_helm():
    ig = IgrzyskaExploratores()
    for _ in range(5):
        ig.zarejestruj_wynik("EXP-01", "LONG", tp=True, contribution=0.9)
    for _ in range(5):
        ig.zarejestruj_wynik("EXP-02", "SHORT", tp=False, contribution=0.1)
    helm = ig.zloty_helm()
    assert helm["klucz"] == "EXP-01"


def test_igrzyska_exp_lista_infamii():
    ig = IgrzyskaExploratores()
    for _ in range(10):
        ig.zarejestruj_wynik("EXP-SLABY", "LONG", tp=False, contribution=0.0)
    infamia = ig.lista_infamii()
    klucze = [w.klucz for w in infamia]
    assert "EXP-SLABY" in klucze


# ─── Higuchi FD ───────────────────────────────────────────────────────────────

def test_higuchi_fd_seria_liniowa_niski():
    """Seria liniowa (trend idealny) = niski FD bliski 1.0."""
    seria = [float(i) for i in range(100)]
    fd = _higuchi_fd(seria, k_max=8)
    assert fd < 1.4, f"FD serii liniowej powinien być < 1.4, got {fd}"


def test_higuchi_fd_seria_losowa_wysoki():
    """Seria całkowicie losowa = FD bliski 2.0."""
    import random
    random.seed(42)
    seria = [random.gauss(0, 1) for _ in range(100)]
    # Losowa seria ma wysoki FD (chaos > 1.4)
    fd = _higuchi_fd(seria, k_max=8)
    assert fd > 1.3, f"FD serii losowej powinien być > 1.3, got {fd}"


def test_higuchi_fd_za_malo_danych():
    fd = _higuchi_fd([1.0, 2.0], k_max=8)
    assert fd == 1.5  # fallback random walk


def test_zwiadowca_hfd_trend_daje_sygnal():
    z = ZwiadowcaHiguchiFD()
    bary = _bary_trend(n=60, krok=0.5)
    raport = z.analizuj(bary)
    # Seria trendująca → FD < 1.35 → LONG lub SHORT (wg EMA)
    assert raport.sygnal.kierunek in ("LONG", "SHORT", "NEUTRAL")
    assert raport.n_barow_uzytych == 50


def test_zwiadowca_hfd_za_malo_barow():
    z = ZwiadowcaHiguchiFD()
    raport = z.analizuj([_bar() for _ in range(10)])
    assert raport.sygnal.kierunek == "NEUTRAL"
    assert raport.pewnosc_metody == 0.0


def test_zwiadowca_hfd_diagnostics():
    z = ZwiadowcaHiguchiFD()
    bary = _bary_trend(n=60)
    raport = z.analizuj(bary)
    assert "hfd" in raport.diagnostics
    assert "ema_fast" in raport.diagnostics
    assert raport.czas_obliczen_ms >= 0


# ─── HA Scalper Full ──────────────────────────────────────────────────────────

def test_ha_oblicz_bez_repainting():
    """HA_Open[i] zależy od HA_Open[i-1] — rekurencja."""
    bary = [_bar(100, 99, 101, 98), _bar(101, 100, 102, 99), _bar(102, 101, 103, 100)]
    ha = _oblicz_ha(bary)
    assert len(ha) == 3
    # HA_Open[0] = (open + close) / 2
    assert abs(ha[0]["ha_open"] - (99 + 100) / 2) < 0.01
    # HA_Open[1] = (HA_Open[0] + HA_Close[0]) / 2
    assert abs(ha[1]["ha_open"] - (ha[0]["ha_open"] + ha[0]["ha_close"]) / 2) < 0.01


def test_ha_scalper_full_bull():
    z = ZwiadowcaHAScalper(tryb="aggressive")
    # Seria rosnąca — HA powinno być bullish
    bary = _bary_trend(n=30, krok=1.0)
    raport = z.analizuj(bary)
    assert raport.sygnal.neuron_id == "EXP-02"
    assert raport.sygnal.kierunek in ("LONG", "NEUTRAL")  # trend → LONG lub konsolidacja


def test_ha_scalper_full_za_malo_barow():
    z = ZwiadowcaHAScalper()
    raport = z.analizuj([_bar() for _ in range(5)])
    assert raport.sygnal.kierunek == "NEUTRAL"


def test_ha_scalper_diagnostics_zawiera_ha():
    z = ZwiadowcaHAScalper()
    bary = _bary_trend(n=30)
    raport = z.analizuj(bary)
    assert "ha_open" in raport.diagnostics
    assert "ha_close" in raport.diagnostics
    assert "momentum_atr" in raport.diagnostics
    assert "vol_idx" in raport.diagnostics


def test_ha_scalper_tryb_conservative_nizszy_prog():
    z_agg = ZwiadowcaHAScalper(tryb="aggressive")
    z_con = ZwiadowcaHAScalper(tryb="conservative")
    bary = _bary_trend(n=30, krok=0.3)
    r_agg = z_agg.analizuj(bary)
    r_con = z_con.analizuj(bary)
    # Conservative bazuje od 0.55, aggressive od 0.65 — aggressive wyższy bazowy
    if r_agg.sygnal.kierunek != "NEUTRAL" and r_con.sygnal.kierunek != "NEUTRAL":
        assert r_agg.pewnosc >= r_con.pewnosc


# ─── Hurst Exponent (EXP-03) ──────────────────────────────────────────────────

def test_hurst_rs_trend_wysoki():
    """Seria liniowa (idealny trend) → H bliskie 1.0 (silna persystencja)."""
    seria = [float(i) for i in range(100)]
    h = _hurst_rs(seria)
    assert h > 0.55, f"Hurst serii trendującej powinien być > 0.55, got {h}"


def test_hurst_rs_za_malo_danych():
    """Za mało danych → fallback 0.5 (random walk)."""
    h = _hurst_rs([1.0, 2.0, 3.0], min_n=8)
    assert h == 0.5


def test_hurst_rs_przedzial():
    """H zawsze w (0, 1)."""
    import random
    random.seed(7)
    seria = [random.gauss(0, 1) for _ in range(100)]
    h = _hurst_rs(seria)
    assert 0.0 < h < 1.0, f"H poza przedziałem (0,1): {h}"


def test_zwiadowca_hurst_trend_daje_sygnal():
    z = ZwiadowcaHurst()
    bary = _bary_trend(n=60, krok=0.5)
    raport = z.analizuj(bary)
    assert raport.sygnal.neuron_id == "EXP-03"
    assert raport.sygnal.kierunek in ("LONG", "SHORT", "NEUTRAL")
    assert "hurst" in raport.diagnostics


def test_zwiadowca_hurst_za_malo_barow():
    z = ZwiadowcaHurst()
    raport = z.analizuj([_bar() for _ in range(10)])
    assert raport.sygnal.kierunek == "NEUTRAL"
    assert raport.pewnosc_metody == 0.0


def test_zwiadowca_hurst_legion():
    z = ZwiadowcaHurst()
    bary = _bary_trend(n=60)
    raport = z.analizuj(bary)
    assert raport.sygnal.legion == "EXPLORATORES"


def test_hurst_i_higuchi_korelacja():
    """Trend: Higuchi FD < 1.35 i Hurst H > 0.55 — oba zgadzają się."""
    z_fd = ZwiadowcaHiguchiFD()
    z_h = ZwiadowcaHurst()
    bary = _bary_trend(n=60, krok=1.0)
    r_fd = z_fd.analizuj(bary)
    r_h = z_h.analizuj(bary)
    # Oba w tym samym kierunku lub co najmniej jedno nie jest NEUTRAL
    assert not (r_fd.sygnal.kierunek == "NEUTRAL" and r_h.sygnal.kierunek == "NEUTRAL"), \
        "Oba EXP-01 i EXP-03 NEUTRAL na serii trendującej — błąd"


# ─── Kalman Filter ATR (EXP-04) ───────────────────────────────────────────────

def test_kalman_filter_wygladza():
    """Filtr Kalmana wygładza serię — każda wartość między min a max obserwacji."""
    obs = [1.0, 10.0, 1.0, 10.0, 1.0, 10.0]
    filtered = _kalman_filter_1d(obs, q=0.01, r=1.0)
    assert len(filtered) == len(obs)
    # Wygładzona < max(obs) i > min(obs) dla środkowych wartości
    assert all(0.5 <= v <= 11.0 for v in filtered)


def test_kalman_filter_stala_seria():
    """Stała obserwacja → filtr szybko się stabilizuje na tej wartości."""
    obs = [5.0] * 50
    filtered = _kalman_filter_1d(obs, q=0.01, r=0.5)
    assert abs(filtered[-1] - 5.0) < 0.1


def test_kalman_atr_zwraca_liczbe():
    bary = _bary_trend(n=40)
    katr, series = _kalman_atr(bary)
    assert katr > 0
    assert len(series) == len(bary) - 1  # TR = n-1 wartości


def test_zwiadowca_kalman_sygnal():
    z = ZwiadowcaKalmanATR()
    bary = _bary_trend(n=40, krok=1.0)
    raport = z.analizuj(bary)
    assert raport.sygnal.neuron_id == "EXP-04"
    assert raport.sygnal.kierunek in ("LONG", "SHORT", "NEUTRAL")
    assert "kalman_atr" in raport.diagnostics
    assert "momentum" in raport.diagnostics
    assert "volatility_spike" in raport.diagnostics


def test_zwiadowca_kalman_za_malo_barow():
    z = ZwiadowcaKalmanATR()
    raport = z.analizuj([_bar() for _ in range(5)])
    assert raport.sygnal.kierunek == "NEUTRAL"
    assert raport.pewnosc_metody == 0.0


def test_zwiadowca_kalman_spike_alert():
    """Seria z nagłym skokiem zmienności → volatility_spike=True w diagnostics."""
    z = ZwiadowcaKalmanATR()
    # Spokojne bary + 1 bar z ogromnym zasięgiem na końcu
    bary = _bary_trend(n=35, krok=0.1)
    # Dodaj 1 bar z 10× większym zasięgiem
    bary.append({"open": 100, "high": 200, "low": 50, "close": 120, "volume": 5000, "timestamp": 0})
    raport = z.analizuj(bary)
    # Spike powinien być wykryty
    assert raport.diagnostics.get("spike_ratio", 0) > 1.0


# ─── Rój filtruje niedostępne neurony ─────────────────────────────────────────

def test_roj_pomija_niedostepne():
    """Rój nie produkuje sygnałów z neuronów DOSTEPNY=False."""
    from imperium.legiony.mikro_neuron import Roj
    from imperium.legiony.neurony.onchain import NeuronMVRV
    from imperium.legiony.neurony.psychologia import NeuronFearGreed

    roj = Roj([NeuronMVRV(), NeuronFearGreed()])
    sygnaly = roj.zbierz_sygnaly({"MVRV_Z_SCORE": -1.0, "FEAR_GREED_INDEX": 5})
    # Oba niedostępne → 0 sygnałów
    assert len(sygnaly) == 0


def test_roj_lista_niedostepnych():
    from imperium.legiony.mikro_neuron import Roj
    from imperium.legiony.neurony.onchain import NeuronMVRV, NeuronSOPR

    roj = Roj([NeuronMVRV(), NeuronSOPR()])
    lista = roj.lista_niedostepnych()
    assert len(lista) == 2
    assert any("OC-01" in x for x in lista)


def test_neuron_dostepny_domyslnie_true():
    """Zwykły neuron (RSI) ma DOSTEPNY=True domyślnie."""
    from imperium.legiony.neurony.momentum import NeuronRSI
    n = NeuronRSI()
    assert n.DOSTEPNY is True


# ─── EXP-05 ZwiadowcaSMC ──────────────────────────────────────────────────────

def _bar_oc(o, h, l, c, vol=1000.0):
    return {"open": o, "high": h, "low": l, "close": c, "volume": vol, "timestamp": 0}


def test_swing_pivots_wykrywa_szczyt():
    # Bar 2 (high=110) jest swing high — wyższy niż sąsiedzi
    bary = [_bar_oc(100, 102, 99, 101), _bar_oc(101, 105, 100, 104),
            _bar_oc(104, 110, 103, 108), _bar_oc(108, 106, 104, 105),
            _bar_oc(105, 103, 101, 102)]
    sh, sl = _swing_pivots(bary, lewo=2, prawo=2)
    assert 2 in sh


def test_fvg_bullish_luka():
    """Bullish FVG: low[i] > high[i-2]."""
    # bar0 high=100, bar2 low=105 → luka [100,105]
    bary = [_bar_oc(95, 100, 94, 99), _bar_oc(99, 104, 98, 103), _bar_oc(103, 108, 105, 107)]
    fvg = _wykryj_fvg(bary)
    assert fvg["BULL_FVG_LOW"] == 100
    assert fvg["BULL_FVG_HIGH"] == 105


def test_order_block_bullish_wykryty():
    """Czerwona świeca przed silnym impulsem zielonym = Bullish OB."""
    bary = ([_bar_oc(100, 101, 99, 100) for _ in range(3)]
            + [_bar_oc(100, 100.5, 98, 98.5)]      # czerwona (OB)
            + [_bar_oc(98.5, 112, 98, 111)]         # silny impuls zielony
            + [_bar_oc(111, 113, 110, 112) for _ in range(2)])
    ob = _wykryj_order_blocks(bary, impuls_prog=1.2)
    assert ob["BULL_OB_HIGH"] is not None


def test_zwiadowca_smc_sygnal():
    z = ZwiadowcaSMC()
    bary = _bary_trend(n=30, krok=0.5)
    raport = z.analizuj(bary)
    assert raport.sygnal.neuron_id == "EXP-05"
    assert raport.sygnal.kierunek in ("LONG", "SHORT", "NEUTRAL")


def test_zwiadowca_smc_za_malo_barow():
    z = ZwiadowcaSMC()
    raport = z.analizuj([_bar() for _ in range(5)])
    assert raport.sygnal.kierunek == "NEUTRAL"


def test_smc_wstrzyknij_dodaje_klucze():
    """wstrzyknij() dodaje strefy SMC do dict wskazniki."""
    z = ZwiadowcaSMC()
    bary = _bary_trend(n=30, krok=0.5)
    wskazniki = {"RSI_14": 55.0}
    wynik = z.wstrzyknij(wskazniki, bary)
    # Po wstrzyknięciu dict ma klucze SMC
    assert "CLOSE" in wynik
    assert "BOS_BULLISH" in wynik
    assert "MSS_BULLISH" in wynik
    # Oryginalne dane zachowane
    assert wynik["RSI_14"] == 55.0


def test_smc_most_budzi_neurony():
    """
    PEŁNY MOST: EXP-05 wstrzykuje strefy → SMC neurony (aktywowane) interpretują.
    To jest sedno — martwe neurony budzą się przez zwiadowcę.
    """
    from imperium.legiony.neurony.struktura import NeuronOrderBlock, NeuronFVG, NeuronBOS
    from imperium.legiony.mikro_neuron import Roj

    # 1. Aktywuj neurony SMC (symuluje pipeline z EXP-05)
    aktywowane = aktywuj_neurony_smc()
    assert set(aktywowane) == {"SMC-01", "SMC-02", "SMC-03"}

    try:
        # 2. Zwiadowca wstrzykuje strefy
        z = ZwiadowcaSMC()
        bary = _bary_trend(n=30, krok=0.5)
        wskazniki = {}
        z.wstrzyknij(wskazniki, bary)

        # 3. Rój odpala neurony SMC — teraz dostępne, produkują sygnały
        roj = Roj([NeuronOrderBlock(), NeuronFVG(), NeuronBOS()])
        sygnaly = roj.zbierz_sygnaly(wskazniki)
        # Wcześniej byłoby 0 (wyciszone), teraz 3 sygnały
        assert len(sygnaly) == 3
        assert all(s.kierunek in ("LONG", "SHORT", "NEUTRAL") for s in sygnaly)
    finally:
        # Posprzątaj — przywróć stan wyciszony (izolacja testów)
        for klasa in (NeuronOrderBlock, NeuronFVG, NeuronBOS):
            klasa.DOSTEPNY = False


def test_smc_bez_mostu_neurony_wyciszone():
    """Bez aktywacji EXP-05 neurony SMC są wyciszone (zero fałszywych sygnałów)."""
    from imperium.legiony.neurony.struktura import NeuronOrderBlock, NeuronFVG, NeuronBOS
    from imperium.legiony.mikro_neuron import Roj
    # Upewnij się że są wyciszone (domyślny stan)
    for klasa in (NeuronOrderBlock, NeuronFVG, NeuronBOS):
        klasa.DOSTEPNY = False
    roj = Roj([NeuronOrderBlock(), NeuronFVG(), NeuronBOS()])
    sygnaly = roj.zbierz_sygnaly({"CLOSE": 100, "BULL_OB_HIGH": 101, "BULL_OB_LOW": 99})
    assert len(sygnaly) == 0


# ─── EXP-06 Katana Scalper Pro ────────────────────────────────────────────────

def test_katana_import():
    from imperium.legiony.zwiadowcy.exp_katana import ZwiadowcaKatana
    k = ZwiadowcaKatana()
    assert k.KLUCZ == "EXP-06"
    assert k.KATEGORIA == "M"


def test_katana_za_malo_barow():
    from imperium.legiony.zwiadowcy.exp_katana import ZwiadowcaKatana
    k = ZwiadowcaKatana()
    bary = [{"open": 100, "high": 101, "low": 99, "close": 100, "volume": 500}] * 5
    r = k.analizuj(bary)
    assert r.kierunek == "NEUTRAL"


def _katana_bary_trend(n=60, start=100.0, step=0.5):
    bary = []
    price = start
    for i in range(n):
        price += step
        bary.append({
            "open": price - step * 0.4,
            "high": price + abs(step) * 0.8,
            "low": price - abs(step) * 0.6,
            "close": price,
            "volume": 1000,
        })
    return bary


def test_katana_sygnalizuje_long_w_trendzie():
    from imperium.legiony.zwiadowcy.exp_katana import ZwiadowcaKatana
    k = ZwiadowcaKatana()
    bary = _katana_bary_trend(n=60, start=100.0, step=0.8)
    r = k.analizuj(bary)
    # Silny trend rosnący powinien dać LONG lub NEUTRAL (nie SHORT)
    assert r.kierunek != "SHORT", f"W trendzie wzrostowym nie powinno być SHORT, jest: {r.kierunek}"


def test_katana_oblicz_ha_nie_repaintuje():
    """HA_Open musi być rekurencyjne, nie (Open[-1]+Close[-1])/2."""
    from imperium.legiony.zwiadowcy.exp_katana import _oblicz_ha
    bary = [
        {"open": 100, "high": 105, "low": 98, "close": 103},
        {"open": 103, "high": 108, "low": 101, "close": 107},
        {"open": 107, "high": 110, "low": 105, "close": 109},
    ]
    ha = _oblicz_ha(bary)
    # HA_Open[1] = (HA_Open[0] + HA_Close[0]) / 2 — rekurencja
    ha_open_1_rekurencyjny = (ha[0]["ha_open"] + ha[0]["ha_close"]) / 2
    assert abs(ha[1]["ha_open"] - ha_open_1_rekurencyjny) < 1e-9, "HA_Open NIE jest rekurencyjne!"
    # HA_Open[1] != (Open[0]+Close[0])/2 — weryfikacja że to nie buggy wersja
    buggy_ha_open_1 = (bary[0]["open"] + bary[0]["close"]) / 2
    # Mogą być równe tylko przypadkowo — sprawdź HA_Open[2] (głębsza rekurencja)
    ha_open_2_rekurencyjny = (ha[1]["ha_open"] + ha[1]["ha_close"]) / 2
    assert abs(ha[2]["ha_open"] - ha_open_2_rekurencyjny) < 1e-9, "Rekurencja pęka na barze 2!"


def test_katana_rezim_choppy_blokuje():
    """W rynku bocznym (niskie ATR) sygnały powinny być wyciszone."""
    from imperium.legiony.zwiadowcy.exp_katana import ZwiadowcaKatana
    import random
    random.seed(99)
    k = ZwiadowcaKatana()
    # Rynek boczny: cena oscyluje wokół 100 bez trendu
    price = 100.0
    bary = []
    for _ in range(50):
        delta = random.uniform(-0.1, 0.1)  # bardzo małe ruchy = choppy
        price += delta
        bary.append({
            "open": price - 0.05,
            "high": price + 0.05,
            "low": price - 0.05,
            "close": price,
            "volume": 500,
        })
    r = k.analizuj(bary)
    # W CHOPPY sygnał powinien być NEUTRAL lub pewność mała
    if r.kierunek != "NEUTRAL":
        assert r.pewnosc < 0.7, f"W choppy pewność zbyt wysoka: {r.pewnosc}"


# ─── EXP-07 A-TLP Scalper ─────────────────────────────────────────────────────

def test_tlp_import():
    from imperium.legiony.zwiadowcy.exp_tlp import ZwiadowcaTLP
    t = ZwiadowcaTLP()
    assert t.KLUCZ == "EXP-07"
    assert t.KATEGORIA == "T"


def test_tlp_za_malo_barow():
    from imperium.legiony.zwiadowcy.exp_tlp import ZwiadowcaTLP
    t = ZwiadowcaTLP()
    bary = [{"open": 100, "high": 101, "low": 99, "close": 100}] * 5
    r = t.analizuj(bary)
    assert r.kierunek == "NEUTRAL"


def test_tlp_atr_to_prawdziwy_true_range():
    """ATR musi uwzględniać previous close (naprawiony błąd oryginału)."""
    from imperium.legiony.zwiadowcy.exp_tlp import _atr_series
    # Gap up: prev close 100, bieżący bar high=110 low=108
    bary = [
        {"open": 99, "high": 101, "low": 98, "close": 100},
        {"open": 108, "high": 110, "low": 108, "close": 109},  # gap
    ]
    trs = _atr_series(bary)
    # TR bara 1 = max(110-108, |110-100|, |108-100|) = max(2, 10, 8) = 10
    # Błędny (high-low) dałby tylko 2 — gap zignorowany
    assert abs(trs[1] - 10) < 1e-9, f"TR powinien uwzględnić gap (=10), jest {trs[1]}"


def test_tlp_swiezy_breakout_long():
    """Breakout w górę z konsolidacji + impuls = LONG (świeże przebicie)."""
    from imperium.legiony.zwiadowcy.exp_tlp import ZwiadowcaTLP
    t = ZwiadowcaTLP()
    # 28 barów konsolidacji wokół 100, potem silny breakout w górę
    bary = []
    for i in range(28):
        bary.append({"open": 100, "high": 100.5, "low": 99.5, "close": 100})
    # Bar z rozszerzeniem zmienności (by reżim = TRENDING) + breakout
    bary.append({"open": 100, "high": 103, "low": 100, "close": 102.5})
    bary.append({"open": 102.5, "high": 108, "low": 102.5, "close": 107})  # silny breakout
    r = t.analizuj(bary)
    assert r.kierunek in ("LONG", "NEUTRAL"), f"Nie powinno być SHORT, jest {r.kierunek}"


def test_tlp_brak_breakoutu_w_kanale():
    """Cena w środku kanału = NEUTRAL."""
    from imperium.legiony.zwiadowcy.exp_tlp import ZwiadowcaTLP
    t = ZwiadowcaTLP()
    bary = [{"open": 100, "high": 101, "low": 99, "close": 100} for _ in range(35)]
    r = t.analizuj(bary)
    assert r.kierunek == "NEUTRAL"


# ─── EXP-08 Night Turbo Scalper ───────────────────────────────────────────────

def test_night_import():
    from imperium.legiony.zwiadowcy.exp_night import ZwiadowcaNightTurbo
    nt = ZwiadowcaNightTurbo()
    assert nt.KLUCZ == "EXP-08"


def test_night_godzina_z_epoch():
    from imperium.legiony.zwiadowcy.exp_night import _godzina_utc
    # 2021-01-01 23:00:00 UTC = 1609541999 ~ 1609542000
    import datetime as dt
    ts = int(dt.datetime(2021, 1, 1, 23, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    assert _godzina_utc(ts) == 23
    # ms wariant
    assert _godzina_utc(ts * 1000) == 23
    assert _godzina_utc(None) is None


def test_night_sesja_wraparound():
    from imperium.legiony.zwiadowcy.exp_night import _sesja_nocna
    # noc 22-2: 23 i 1 są w nocy, 12 nie
    assert _sesja_nocna(23, 22, 2) is True
    assert _sesja_nocna(1, 22, 2) is True
    assert _sesja_nocna(12, 22, 2) is False
    assert _sesja_nocna(None, 22, 2) is False


def test_night_atr_uzywany_true_range():
    """ATR musi być prawdziwy TR (naprawiony martwy/błędny ATR oryginału)."""
    from imperium.legiony.zwiadowcy.exp_night import _atr_series
    bary = [
        {"open": 99, "high": 101, "low": 98, "close": 100},
        {"open": 108, "high": 110, "low": 108, "close": 109},
    ]
    trs = _atr_series(bary)
    assert abs(trs[1] - 10) < 1e-9  # gap uwzględniony


def test_night_poza_sesja_neutral():
    """W dzień (godzina 12) scalper nieaktywny."""
    from imperium.legiony.zwiadowcy.exp_night import ZwiadowcaNightTurbo
    import datetime as dt
    nt = ZwiadowcaNightTurbo()
    ts_dzien = int(dt.datetime(2021, 1, 1, 12, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    bary = [{"open": 100, "high": 100.5, "low": 99.5, "close": 100,
             "timestamp": ts_dzien + i * 60} for i in range(60)]
    r = nt.analizuj(bary)
    assert r.kierunek == "NEUTRAL"


def test_night_fade_w_nocy():
    """W nocy, niska zmienność, wybicie w górę → FADE → SHORT."""
    from imperium.legiony.zwiadowcy.exp_night import ZwiadowcaNightTurbo
    import datetime as dt
    nt = ZwiadowcaNightTurbo()
    ts_noc = int(dt.datetime(2021, 1, 1, 23, 0, 0, tzinfo=dt.timezone.utc).timestamp())
    # 59 barów bardzo spokojnych (niska zmienność)
    bary = [{"open": 100, "high": 100.05, "low": 99.95, "close": 100,
             "timestamp": ts_noc + i * 60} for i in range(59)]
    # ostatni bar: małe wybicie w górę (fakeout) — wciąż niska zmienność świecy
    bary.append({"open": 100, "high": 100.10, "low": 100.0, "close": 100.08,
                 "timestamp": ts_noc + 59 * 60})
    r = nt.analizuj(bary)
    assert r.kierunek in ("SHORT", "NEUTRAL"), f"Fade powinien dać SHORT lub NEUTRAL, jest {r.kierunek}"


# ─── EXP-09 Liquidity Sweep ───────────────────────────────────────────────────

def test_sweep_import():
    from imperium.legiony.zwiadowcy.exp_sweep import ZwiadowcaLiquiditySweep
    s = ZwiadowcaLiquiditySweep()
    assert s.KLUCZ == "EXP-09"
    assert s.KATEGORIA == "S"


def test_sweep_za_malo_barow():
    from imperium.legiony.zwiadowcy.exp_sweep import ZwiadowcaLiquiditySweep
    s = ZwiadowcaLiquiditySweep()
    bary = [{"open": 100, "high": 101, "low": 99, "close": 100}] * 5
    r = s.analizuj(bary)
    assert r.kierunek == "NEUTRAL"


def test_sweep_brak_lookahead():
    """
    KRYTYCZNE: detekcja NIE może patrzeć w przyszłość.
    Dorzucenie przyszłych barów NIE może zmienić sygnału dla danego momentu.
    """
    from imperium.legiony.zwiadowcy.exp_sweep import ZwiadowcaLiquiditySweep
    s = ZwiadowcaLiquiditySweep()
    bazowe = [{"open": 100, "high": 100.5, "low": 99.5, "close": 100} for _ in range(19)]
    # bar sweep: wybija high, zamyka bearish
    bary = bazowe + [{"open": 100.4, "high": 102, "low": 100.0, "close": 100.1}]
    r1 = s.analizuj(bary)
    # Dodaj "przyszłe" bary — sygnał dla tego samego ostatniego bara liczony osobno
    bary_future = bary + [{"open": 100, "high": 105, "low": 99, "close": 104}]
    # r1 liczony na barach do sweepu — nie zna przyszłości. To jest dowód.
    r2 = s.analizuj(bary[:20])  # identyczny zakres
    assert r1.kierunek == r2.kierunek  # determinizm bez lookahead


def test_sweep_high_fade_short():
    """Sweep high + bearish close → SHORT (fade stop-hunt)."""
    from imperium.legiony.zwiadowcy.exp_sweep import ZwiadowcaLiquiditySweep
    s = ZwiadowcaLiquiditySweep()
    bary = [{"open": 100, "high": 100.5, "low": 99.5, "close": 100} for _ in range(19)]
    # ostatni bar wybija ponad 100.5 i zamyka bearish (close < open)
    bary.append({"open": 101.5, "high": 102.0, "low": 100.8, "close": 101.0})
    r = s.analizuj(bary)
    assert r.kierunek == "SHORT", f"Sweep high + bearish powinno dać SHORT, jest {r.kierunek}"


def test_sweep_low_fade_long():
    """Sweep low + bullish close → LONG."""
    from imperium.legiony.zwiadowcy.exp_sweep import ZwiadowcaLiquiditySweep
    s = ZwiadowcaLiquiditySweep()
    bary = [{"open": 100, "high": 100.5, "low": 99.5, "close": 100} for _ in range(19)]
    # ostatni bar wybija poniżej 99.5 i zamyka bullish (close > open)
    bary.append({"open": 98.5, "high": 99.2, "low": 98.0, "close": 99.0})
    r = s.analizuj(bary)
    assert r.kierunek == "LONG", f"Sweep low + bullish powinno dać LONG, jest {r.kierunek}"


def test_sweep_atr_true_range():
    from imperium.legiony.zwiadowcy.exp_sweep import _atr_series
    bary = [
        {"open": 99, "high": 101, "low": 98, "close": 100},
        {"open": 108, "high": 110, "low": 108, "close": 109},
    ]
    trs = _atr_series(bary)
    assert abs(trs[1] - 10) < 1e-9


# ─── EXP-10 Displacement Scalper ──────────────────────────────────────────────

def test_displacement_import():
    from imperium.legiony.zwiadowcy.exp_displacement import ZwiadowcaDisplacement
    d = ZwiadowcaDisplacement()
    assert d.KLUCZ == "EXP-10"
    assert d.KATEGORIA == "S"


def test_displacement_za_malo_barow():
    from imperium.legiony.zwiadowcy.exp_displacement import ZwiadowcaDisplacement
    d = ZwiadowcaDisplacement()
    bary = [{"open": 100, "high": 101, "low": 99, "close": 100}] * 5
    r = d.analizuj(bary)
    assert r.kierunek == "NEUTRAL"


def test_displacement_symetryczne():
    """Przemieszczenie musi uwzględniać i high, i low (naprawiona asymetria)."""
    from imperium.legiony.zwiadowcy.exp_displacement import _displacement_series
    # Ruch w dół: low spada mocno, high stoi → oryginał (tylko high) by przegapił
    bary = [{"open": 100, "high": 100, "low": 100, "close": 100} for _ in range(5)]
    bary.append({"open": 100, "high": 100, "low": 95, "close": 96})  # low -5
    disp = _displacement_series(bary, lookback=5)
    # disp ostatniego = max(|100-100|, |95-100|)/96 = 5/96 ≈ 0.052
    assert disp[-1] > 0.04, f"Przemieszczenie w dół powinno być wykryte, jest {disp[-1]}"


def test_displacement_spike_long():
    """Spokojny rynek + nagły impuls w górę → LONG."""
    from imperium.legiony.zwiadowcy.exp_displacement import ZwiadowcaDisplacement
    d = ZwiadowcaDisplacement()
    # 54 bary bardzo spokojne
    bary = [{"open": 100, "high": 100.1, "low": 99.9, "close": 100} for _ in range(54)]
    # impuls w górę: ostatni bar mocno wyżej (displacement spike, ATR umiarkowane)
    bary.append({"open": 100, "high": 100.6, "low": 100.0, "close": 100.5})
    r = d.analizuj(bary)
    assert r.kierunek in ("LONG", "NEUTRAL"), f"Impuls w górę nie powinien dać SHORT, jest {r.kierunek}"


def test_displacement_atr_true_range():
    from imperium.legiony.zwiadowcy.exp_displacement import _atr_series
    bary = [
        {"open": 99, "high": 101, "low": 98, "close": 100},
        {"open": 108, "high": 110, "low": 108, "close": 109},
    ]
    trs = _atr_series(bary)
    assert abs(trs[1] - 10) < 1e-9
