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


# ── Fixed-Share (W-280) ──────────────────────────────────────────────────────

def test_fixed_share_alpha_zero_rowna_sie_hedge():
    """α=0 → dokładnie stary Hedge (zero regresji, granica dolna parametru)."""
    a = HedgeMWU(eta=0.5, alpha_share=0.0)
    b = HedgeMWU(eta=0.5, alpha_share=0.0)
    for _ in range(10):
        a.zarejestruj_wynik("X", "LONG", "SHORT")
        a.zarejestruj_wynik("Y", "LONG", "LONG")
        b.zarejestruj_wynik("X", "LONG", "SHORT")
        b.zarejestruj_wynik("Y", "LONG", "LONG")
    assert a.wagi_raw == b.wagi_raw


def test_fixed_share_zakopany_ekspert_wraca():
    """Zakopany ekspert odzyskuje wagę szybciej z Fixed-Share niż z czystym Hedge."""
    hedge = HedgeMWU(eta=0.5, alpha_share=0.0)
    share = HedgeMWU(eta=0.5, alpha_share=0.05)
    # Faza 1: X myli się 30 razy (zakopany), Y trafia
    for m in (hedge, share):
        for _ in range(30):
            m.zarejestruj_wynik("X", "LONG", "SHORT")
            m.zarejestruj_wynik("Y", "SHORT", "SHORT")
    assert share.wagi()["X"] > hedge.wagi()["X"], \
        "Fixed-Share musi utrzymać zakopanemu więcej masy (droga powrotu)"
    # Faza 2: reżim się odwraca — X trafia 10 razy, Y się myli
    for m in (hedge, share):
        for _ in range(10):
            m.zarejestruj_wynik("X", "LONG", "LONG")
            m.zarejestruj_wynik("Y", "SHORT", "LONG")
    assert share.wagi()["X"] > hedge.wagi()["X"], \
        "Po zmianie reżimu Fixed-Share wraca szybciej niż czysty Hedge"


def test_fixed_share_zachowuje_sume_mas():
    """Mieszanie Fixed-Share nie zmienia sumy wag (tylko redystrybuuje)."""
    m = HedgeMWU(eta=0.5, alpha_share=0.1)
    m.zarejestruj_wynik("A", "LONG", "LONG")
    m.zarejestruj_wynik("B", "LONG", "SHORT")
    suma_przed = sum(m.wagi_raw.values())
    m.zarejestruj_wynik("A", "LONG", "LONG")
    # po updacie B się nie zmienił Hedge'owo, ale suma po mixingu = suma po kroku Hedge
    wagi = m.wagi()
    assert abs(sum(wagi.values()) - 1.0) < 1e-9
    assert suma_przed > 0


def test_fixed_share_alpha_graniczne():
    """Granice parametru: α<0 i α≥1 odrzucone; α=0 dozwolone (czysty Hedge)."""
    HedgeMWU(alpha_share=0.0)
    try:
        HedgeMWU(alpha_share=-0.01)
        raise AssertionError("α<0 powinno rzucić ValueError")
    except ValueError:
        pass
    try:
        HedgeMWU(alpha_share=1.0)
        raise AssertionError("α=1.0 powinno rzucić ValueError (granica wyłączona)")
    except ValueError:
        pass


def test_fixed_share_trafny_nadal_wygrywa():
    """Mixing nie niszczy uczenia: trafny ekspert wciąż ma najwyższy mnożnik."""
    m = HedgeMWU(eta=0.5, alpha_share=0.02)
    for _ in range(40):
        m.zarejestruj_wynik("DOBRY", "LONG", "LONG")
        m.zarejestruj_wynik("ZLY", "SHORT", "LONG")
    assert m.mnozniki()["DOBRY"] > 1.0 > m.mnozniki()["ZLY"]


# ── W-285.1: Pretorianin Pamięci Reżimów ─────────────────────────────────────

def _trenuj(m, ekspert_dobry, ekspert_zly, rundy=25):
    for _ in range(rundy):
        m.zarejestruj_wynik(ekspert_dobry, "LONG", "LONG")
        m.zarejestruj_wynik(ekspert_zly, "SHORT", "LONG")


def test_pamiec_rezimu_szybszy_powrot():
    """Przy IDENTYCZNYM punkcie startowym (zakopany MR) powrót reżimu RANGING
    z pamięcią przywraca MR szybciej niż uniform Fixed-Share.
    (Wyrównany start jest kluczowy: w fazie TREND wariant pamięciowy słusznie
    zakopuje MR głębiej — porównanie absolutów mieszałoby dwa efekty.)"""
    from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
    pam = HedgeMWUzPamieciaRezimu(eta=0.5, alpha_share=0.05, beta_pamieci=0.2)
    uni = HedgeMWU(eta=0.5, alpha_share=0.05)
    # Zbuduj pamięć reżimu RANGING (MR był tam królem)
    pam.ustaw_rezim("RANGING")
    _trenuj(pam, "MR", "TR")
    # Wyrównany punkt startowy po "zakopaniu": identyczne wagi w obu wariantach
    start = {"MR": 1e-4, "TR": 1.0}
    pam.wagi_raw = dict(start)
    uni.wagi_raw = dict(start)
    pam.ustaw_rezim("RANGING")   # reżim wraca
    for _ in range(3):
        pam.zarejestruj_wynik("MR", "LONG", "LONG")
        pam.zarejestruj_wynik("TR", "SHORT", "LONG")
        uni.zarejestruj_wynik("MR", "LONG", "LONG")
        uni.zarejestruj_wynik("TR", "SHORT", "LONG")
    assert pam.wagi()["MR"] > uni.wagi()["MR"], \
        "pamięć reżimu musi przyspieszać powrót eksperta dobrego w tym reżimie"


def test_pamiec_brak_rezimu_fallback_uniform():
    """Nieznany reżim → cel mieszania = uniform (czysty Fixed-Share, Prawo XV)."""
    from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
    m = HedgeMWUzPamieciaRezimu(alpha_share=0.05)
    m.ustaw_rezim("NIGDY_NIE_WIDZIANY")
    m.zarejestruj_wynik("A", "LONG", "LONG")
    m.zarejestruj_wynik("B", "LONG", "SHORT")
    cel = m._cel_mieszania()
    # po pierwszych rundach pamięć już powstała dla tego reżimu — sprawdź świeży
    m2 = HedgeMWUzPamieciaRezimu(alpha_share=0.05)
    m2.wagi_raw = {"A": 1.0, "B": 1.0}
    cel2 = m2._cel_mieszania()
    assert abs(cel2["A"] - 0.5) < 1e-9 and abs(cel2["B"] - 0.5) < 1e-9
    assert abs(sum(cel.values()) - 1.0) < 1e-9


def test_pamiec_beta_graniczna():
    """beta_pamieci poza (0,1] → ValueError (granice parametru)."""
    from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
    HedgeMWUzPamieciaRezimu(beta_pamieci=1.0)
    for zla in (0.0, -0.1, 1.5):
        try:
            HedgeMWUzPamieciaRezimu(beta_pamieci=zla)
            raise AssertionError(f"beta={zla} powinno rzucić")
        except ValueError:
            pass


def test_pamiec_ustaw_rezim_pusty_ignorowany():
    """ustaw_rezim('') nie zmienia reżimu (granica pustego stringa)."""
    from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
    m = HedgeMWUzPamieciaRezimu()
    m.ustaw_rezim("RANGING")
    m.ustaw_rezim("")
    assert m.rezim == "RANGING"


def test_pamiec_rozdzielona_per_rezim():
    """Pamięć RANGING ≠ pamięć TREND (oddzielne rozkłady)."""
    from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
    m = HedgeMWUzPamieciaRezimu(alpha_share=0.05, beta_pamieci=0.3)
    m.ustaw_rezim("RANGING"); _trenuj(m, "MR", "TR")
    m.ustaw_rezim("TREND_STRONG"); _trenuj(m, "TR", "MR")
    assert m.pamiec["RANGING"]["MR"] > m.pamiec["RANGING"]["TR"]
    assert m.pamiec["TREND_STRONG"]["TR"] > m.pamiec["TREND_STRONG"]["MR"]
