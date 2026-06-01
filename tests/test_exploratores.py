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
