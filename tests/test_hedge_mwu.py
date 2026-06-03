"""
Testy HedgeMWU (wizja W-049) — online Multiplicative Weights Update.
Oraz integracja: wstrzykiwanie mnożników uczenia do Legatusa.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from imperium.biblioteki.hedge_mwu import HedgeMWU


def test_mwu_stan_neutralny_mnozniki_1():
    """Pusty/równy stan → mnożniki = 1.0 (brak zniekształcenia, Prawo XV)."""
    mwu = HedgeMWU()
    assert mwu.mnozniki() == {}            # brak danych → brak mnożników
    # po jednej trafnej rundzie każdego z dwóch ekspertów (równe straty) → równo
    mwu.zarejestruj_wynik("X-01", "LONG", "LONG")
    mwu.zarejestruj_wynik("X-02", "SHORT", "SHORT")
    mn = mwu.mnozniki()
    assert abs(mn["X-01"] - 1.0) < 1e-9 and abs(mn["X-02"] - 1.0) < 1e-9


def test_mwu_trafny_rosnie_mylacy_spada():
    """Ekspert trafny zyskuje wagę, mylący traci (rdzeń algorytmu)."""
    mwu = HedgeMWU(eta=0.5)
    for _ in range(20):
        mwu.zarejestruj_wynik("DOBRY", "LONG", "LONG")     # zawsze trafia
        mwu.zarejestruj_wynik("ZLY", "SHORT", "LONG")      # zawsze myli
    mn = mwu.mnozniki()
    assert mn["DOBRY"] > 1.0 > mn["ZLY"], f"DOBRY={mn['DOBRY']}, ZLY={mn['ZLY']}"


def test_mwu_wagi_sumuja_do_jeden():
    """Wagi znormalizowane tworzą rozkład prawdopodobieństwa (suma=1)."""
    mwu = HedgeMWU()
    mwu.zarejestruj_wynik("A", "LONG", "LONG")
    mwu.zarejestruj_wynik("B", "SHORT", "LONG")
    mwu.zarejestruj_wynik("C", "LONG", "LONG")
    assert abs(sum(mwu.wagi().values()) - 1.0) < 1e-9


def test_mwu_mnozniki_srednia_jeden():
    """mnoznik = waga_norm·N → średnia mnożników = 1.0 (kalibracja wokół 1)."""
    mwu = HedgeMWU(eta=0.7)
    for i in range(15):
        mwu.zarejestruj_wynik("A", "LONG", "LONG")
        mwu.zarejestruj_wynik("B", "SHORT" if i % 2 else "LONG", "LONG")
        mwu.zarejestruj_wynik("C", "SHORT", "LONG")
    mn = mwu.mnozniki()
    srednia = sum(mn.values()) / len(mn)
    assert abs(srednia - 1.0) < 1e-6


def test_mwu_neutral_nie_karany():
    """NEUTRAL/nieznany kierunek nie zmienia wagi (tylko LONG/SHORT liczą)."""
    mwu = HedgeMWU()
    mwu.zarejestruj_wynik("X", "NEUTRAL", "LONG")
    assert mwu.rundy.get("X", 0) == 0       # NEUTRAL pominięty


def test_mwu_eta_dodatnia():
    """eta <= 0 jest błędem (regret-bound wymaga η>0)."""
    try:
        HedgeMWU(eta=0)
        assert False, "eta=0 powinno rzucić ValueError"
    except ValueError:
        pass


def test_mwu_min_waga_chroni_przed_smiercia():
    """Ekspert ciągle mylący nie spada do zera (może wrócić — Prawo XV)."""
    mwu = HedgeMWU(eta=2.0, min_waga=1e-6)
    for _ in range(100):
        mwu.zarejestruj_wynik("ZLY", "SHORT", "LONG")
    assert mwu.wagi_raw["ZLY"] >= 1e-6


def test_mwu_obserwator_igrzysk_ten_sam_strumien():
    """MWU jako obserwator Igrzysk dostaje ten sam strumień wyników (DRY)."""
    from imperium.biblioteki.igrzyska import Igrzyska
    ig = Igrzyska()
    mwu = HedgeMWU()
    ig.obserwatorzy.append(mwu)
    for _ in range(10):
        ig.zarejestruj_wynik("X-01", "LONG", "LONG")
        ig.zarejestruj_wynik("X-07", "SHORT", "LONG")
    # MWU widział te same rundy co Igrzyska
    assert mwu.rundy["X-01"] == 10 and mwu.rundy["X-07"] == 10
    assert mwu.mnozniki()["X-01"] > mwu.mnozniki()["X-07"]


def test_mwu_raport_posortowany():
    """raport() zwraca ekspertów malejąco wg mnożnika."""
    mwu = HedgeMWU()
    for _ in range(10):
        mwu.zarejestruj_wynik("DOBRY", "LONG", "LONG")
        mwu.zarejestruj_wynik("ZLY", "SHORT", "LONG")
    r = mwu.raport()
    assert r[0]["klucz"] == "DOBRY" and r[-1]["klucz"] == "ZLY"


# ─── Integracja z Legatusem (wstrzykiwanie mnożników uczenia) ─────────────────

def _legatus_z_dwoma_neuronami():
    from imperium.legiony.neurony.momentum import NeuronRSI, NeuronStochRSI
    from imperium.legiony.legatus import Legatus
    return Legatus([NeuronRSI(), NeuronStochRSI()], min_neuronow=1, min_przewaga=0.0)


def test_legatus_domyslnie_bez_mnoznikow_uczenia():
    """Bez mnożników uczenia Legatus działa jak dawniej (kompatybilność wsteczna)."""
    leg = _legatus_z_dwoma_neuronami()
    assert leg.mnozniki_neuronow == {}
    r = leg.fokus("BTCUSDT", {"RSI_14": 20.0, "STOCHRSI": 10.0}, rezim="NORMAL")
    assert r.aktywnych_neuronow == 2


def test_legatus_mnoznik_uczenia_wplywa_na_wage():
    """Mnożnik uczenia per-neuron faktycznie zmienia wagę sygnału (Prawo XV — pętla zamknięta)."""
    from imperium.legiony.mikro_neuron import SygnalNeuronu
    leg = _legatus_z_dwoma_neuronami()
    syg = [SygnalNeuronu(neuron_id="X-02", legion="SCALP", wskaznik="RSI",
                         wartosc=20.0, kierunek="LONG", pewnosc=0.8, waga=5,
                         kategoria="M")]
    syg[0].policz_finalna()
    # mnożnik 2.0 dla X-02 → waga 5 → 10
    leg.ustaw_mnozniki_neuronow({"X-02": 2.0})
    wynik = leg._dostosuj_wagi(syg, rezim="BRAK_REZIMU")
    assert wynik[0].waga == 10, f"waga powinna wzrosnąć do 10, jest {wynik[0].waga}"


def test_legatus_setter_aktualizuje():
    """ustaw_mnozniki_neuronow nadpisuje słownik mnożników."""
    leg = _legatus_z_dwoma_neuronami()
    leg.ustaw_mnozniki_neuronow({"X-01": 1.5})
    assert leg.mnozniki_neuronow == {"X-01": 1.5}
    leg.ustaw_mnozniki_neuronow(None)
    assert leg.mnozniki_neuronow == {}
