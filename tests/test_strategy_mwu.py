"""Testy W-362 strategy-MWU — ważenie 20 strategii zrealizowanym P&L (opt-in OFF).

Reguła Test-Granic (Prawo XXI): waga strategii wchodzi w PRÓG doboru (min_wynik) →
testujemy że down-weight wypycha poniżej progu, up-weight podnosi ranking, brak wag =
zero zmiany (ZASADA WPIĘCIA), a pętla uczenia w backteście domyślnie OFF."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.strategie.baza import dobierz_najlepsze
from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
from imperium.legiony.legatus import Legatus


def _sygnaly_dla(strategia, kier="LONG"):
    """Buduje mapę sygnałów, w której WSZYSTKIE neurony wejścia/filtra strategii głosują `kier`."""
    from imperium.legiony.mikro_neuron import SygnalNeuronu
    mapa = {}
    for k in list(strategia.neurony_wejscie) + list(strategia.neurony_filtr):
        s = SygnalNeuronu(neuron_id=k, legion="X", wskaznik="x", wartosc=1.0,
                          kierunek=kier, kategoria="M")
        s.pewnosc_finalna = 0.6
        mapa[k] = s
    return mapa


# ── dobierz_najlepsze z wagami strategii ───────────────────────────────────────

def test_brak_wag_zero_zmiany():
    strat = wszystkie_strategie()
    s0 = strat[0]
    mapa = _sygnaly_dla(s0)
    bez = dobierz_najlepsze(strat, mapa, interwal="")
    z_pustymi = dobierz_najlepsze(strat, mapa, interwal="", wagi_strategii=None)
    assert [d.strategia.id for d in bez] == [d.strategia.id for d in z_pustymi]


def test_waga_mnozy_wynik():
    strat = wszystkie_strategie()
    s0 = strat[0]
    mapa = _sygnaly_dla(s0)
    # top=20 (wszystkie) — izolujemy efekt mnożenia od rankingu top-3
    baseline = dobierz_najlepsze(strat, mapa, interwal="", top=20)
    assert baseline, "sanity: bez wag strategia powinna się dopasować"
    w_base = next(d.wynik for d in baseline if d.strategia.id == s0.id)
    # mnożnik 0.5 → wynik o połowę mniejszy (0.5·w_base > min_wynik, więc nie wypada przez próg)
    z_waga = dobierz_najlepsze(strat, mapa, interwal="", top=20, wagi_strategii={s0.id: 0.5})
    w_pol = next(d.wynik for d in z_waga if d.strategia.id == s0.id)
    assert abs(w_pol - round(w_base * 0.5, 4)) < 1e-6


def test_down_weight_wypycha_ponizej_progu():
    strat = wszystkie_strategie()
    s0 = strat[0]
    mapa = _sygnaly_dla(s0)
    # bardzo mały mnożnik → wynik spada poniżej min_wynik (0.3) → strategia wypada z listy
    wynik = dobierz_najlepsze(strat, mapa, interwal="", wagi_strategii={s0.id: 0.01})
    assert s0.id not in [d.strategia.id for d in wynik]


# ── Legatus setter ─────────────────────────────────────────────────────────────

def test_legatus_domyslnie_bez_wag_strategii():
    leg = Legatus(neurony=[], min_neuronow=1)
    assert leg.wagi_strategii == {}


def test_legatus_ustaw_wagi_strategii():
    leg = Legatus(neurony=[], min_neuronow=1)
    leg.ustaw_wagi_strategii({"X-SC-001": 1.4})
    assert leg.wagi_strategii == {"X-SC-001": 1.4}
    leg.ustaw_wagi_strategii(None)      # None → puste (neutralne)
    assert leg.wagi_strategii == {}


# ── Opt-in w backteście: domyślnie OFF ─────────────────────────────────────────

def test_backtest_ucz_mwu_strategii_domyslnie_off():
    from imperium.koloseum.backtest import backtest
    bary = _bary(n=340)
    eng = backtest("x", "4h", bary=bary, okno=250)   # bez ucz_mwu_strategii
    assert eng is not None and hasattr(eng, "podsumowanie")


def test_backtest_ucz_mwu_strategii_on_nie_wybucha():
    from imperium.koloseum.backtest import backtest
    bary = _bary(n=360)
    eng = backtest("x", "4h", bary=bary, okno=250, tryb="strategia", ucz_mwu_strategii=True)
    assert eng is not None and hasattr(eng, "podsumowanie")


def _bary(n=340):
    import math
    bary = []
    cena = 100.0
    for i in range(n):
        cena *= 1 + 0.003 * math.sin(i / 4.0) + 0.0006
        bary.append({
            "symbol": "TESTUSDT", "interwal": "4h",
            "open": cena, "high": cena * 1.012, "low": cena * 0.988,
            "close": cena * (1 + 0.0012 * math.cos(i / 6.0)),
            "volume": 1000.0 + 8 * i, "timestamp": 1_600_000_000 + i * 14400,
        })
    return bary
