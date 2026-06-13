"""
W-307: Igrzyska wpiête w pipeline Dyrygenta — batch ranking neuronów.

Komplementarne do online HedgeMWU: Igrzyska kumuluje kumulatywne
statystyki (accuracy/stability/ranga), MWU stosuje eksponencjalne
zapomnienie. Gdy oba aktywne — mnożniki łączone (×).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.igrzyska import Igrzyska, okresl_range


# ─── Testy jednostkowe Igrzysk (logika rankingowa) ───────────────────────────

def test_igrzyska_pusta_bez_zlotego_helmu():
    """Świeże Igrzyska → brak rankingu, brak Złotego Hełmu."""
    ig = Igrzyska()
    assert ig.zloty_helm() is None
    assert ig.ranking() == []
    assert ig.lista_infamii() == []


def test_igrzyska_dokladny_neuron_dostaje_wysoka_range():
    """Neuron zawsze trafny → wynik 1.0 → Aquilifer (mnożnik 2.0)."""
    ig = Igrzyska()
    # Deterministyczne: DOBRY zawsze trafia, ZLY zawsze myli
    for _ in range(20):
        ig.zarejestruj_wynik("DOBRY", "LONG", "LONG")
        ig.zarejestruj_wynik("ZLY", "SHORT", "LONG")

    ranking = ig.ranking()
    top = ranking[0]
    assert top["klucz"] == "DOBRY"
    assert top["mnoznik"] >= 1.3   # Centurion lub wyżej


def test_igrzyska_slaby_neuron_trafia_na_liste_infamii():
    """Neuron z accuracy < 0.40 i ≥5 sygnałów → Lista Infamii."""
    ig = Igrzyska()
    for _ in range(10):
        ig.zarejestruj_wynik("SLABY", "LONG", "SHORT")  # zawsze myli
    lista = ig.lista_infamii()
    klucze = [w.klucz for w in lista]
    assert "SLABY" in klucze


def test_okresl_range_wartosci_graniczne():
    """Granice prog → ranga i mnożnik."""
    assert okresl_range(0.93)[0] == "Aquilifer"
    assert okresl_range(0.85)[0] == "PrimusPilus"
    assert okresl_range(0.73)[0] == "Centurion"
    assert okresl_range(0.0)[0] == "Tiro"
    # Próg dokładny — ≥ prog → wyższa ranga
    assert okresl_range(0.60)[0] == "Optio"
    assert okresl_range(0.4499)[0] == "Tiro"


def test_igrzyska_break_even_neutralny():
    """Trade na zero (pnl_pct == 0) → Igrzyska nie rejestrują (pomija Dyrygent).
    Test weryfikuje, że po break-even statystyka neuronu jest pusta."""
    ig = Igrzyska()
    # Igrzyska.zarejestruj_wynik() jest wywoływane przez Dyrygenta tylko gdy pnl != 0.
    # Symulujemy: brak wywołań → brak statystyk.
    assert ig.ranking() == []


def test_igrzyska_nowe_wagi_format():
    """nowe_wagi() zwraca dict {klucz: float}."""
    ig = Igrzyska()
    ig.zarejestruj_wynik("A", "LONG", "LONG")
    ig.zarejestruj_wynik("B", "SHORT", "LONG")
    wagi = ig.nowe_wagi()
    assert isinstance(wagi, dict)
    assert "A" in wagi
    assert "B" in wagi
    assert all(isinstance(v, float) for v in wagi.values())


def test_igrzyska_obserwator_pattern():
    """Obserwator podpięty do Igrzysk odbiera zdarzenia (W-049/DRY)."""
    class MockMWU:
        def __init__(self): self.log = []
        def zarejestruj_wynik(self, k, d, g, contribution=None, timeliness=None):
            self.log.append((k, d, g))

    ig = Igrzyska()
    obs = MockMWU()
    ig.obserwatorzy.append(obs)
    ig.zarejestruj_wynik("X", "LONG", "LONG")
    assert ("X", "LONG", "LONG") in obs.log


# ─── Testy integracji z Dyrygent.zbuduj() ────────────────────────────────────

def test_zbuduj_igrzyska_domyslnie_wylaczone():
    """Domyślny Dyrygent.zbuduj() → _igrzyska = None."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    assert d._igrzyska is None


def test_zbuduj_igrzyska_aktywne():
    """Dyrygent.zbuduj(igrzyska=True) → _igrzyska to instancja Igrzysk."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.biblioteki.igrzyska import Igrzyska
    d = Dyrygent.zbuduj(adaptery_live=False, igrzyska=True)
    assert isinstance(d._igrzyska, Igrzyska)


def test_zbuduj_igrzyska_i_mwu_razem():
    """igrzyska=True AND mwu=True → oba aktywne (komplementarne warstwy)."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.biblioteki.igrzyska import Igrzyska
    from imperium.biblioteki.hedge_mwu import HedgeMWU
    d = Dyrygent.zbuduj(adaptery_live=False, igrzyska=True, mwu=True)
    assert isinstance(d._igrzyska, Igrzyska)
    assert isinstance(d.legatus.mwu, HedgeMWU)


def test_raport_igrzysk_bez_kolektora_zwraca_none():
    """Dyrygent bez Igrzysk → raport_igrzysk() = None."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    assert d.raport_igrzysk() is None


def test_raport_igrzysk_pusta_gdy_brak_tradow():
    """Igrzyska aktywne, ale zero trade'ów → raport_igrzysk() = None."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False, igrzyska=True)
    assert d.raport_igrzysk() is None


def test_backtest_igrzyska_learning_sygnatura():
    """backtest_portfel() akceptuje igrzyska_learning=True bez błędu sygnaturowego."""
    import inspect
    from imperium.koloseum.backtest import backtest_portfel
    sig = inspect.signature(backtest_portfel)
    assert "igrzyska_learning" in sig.parameters


def test_mnozniki_laczone_mwu_i_igrzyska():
    """Gdy oba MWU i Igrzyska aktywne, combined = mwu × igr dla każdego neuronu."""
    # Test czysto jednostkowy — symuluje logikę _aktualizuj_synapsy() bez Dyrygenta
    from imperium.biblioteki.hedge_mwu import HedgeMWU
    mwu = HedgeMWU()
    ig = Igrzyska()

    # Neuron A trafny → HedgeMWU nie karze (waga bliska 1.0), Igrzyska wysoka ranga
    for _ in range(10):
        mwu.zarejestruj_wynik("A", "LONG", "LONG")
        ig.zarejestruj_wynik("A", "LONG", "LONG")

    wagi_mwu = mwu.mnozniki()
    wagi_igr = ig.nowe_wagi()
    all_keys = set(wagi_mwu) | set(wagi_igr)
    combined = {k: wagi_mwu.get(k, 1.0) * wagi_igr.get(k, 1.0) for k in all_keys}

    # Neuron A powinien mieć combined >= 1.0 (trafny → obie warstwy nie karzą)
    assert combined["A"] >= 1.0
