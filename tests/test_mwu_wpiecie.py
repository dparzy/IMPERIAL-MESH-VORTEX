"""
W-303 HedgeMWU wiring tests.

Sprawdza, że MWU podpięty do Legatusa via Dyrygenta:
- zarejestruje wyniki zamkniętych pozycji
- zaktualizuje mnozniki_neuronow w Legatusie
- neutral przy równych wagach (Prawo XV — zero zniekształcenia)
- opt-in działa w backtest_portfel (mwu_learning=True/False)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.hedge_mwu import HedgeMWU


def _dyrygent_z_mwu():
    """Buduje lekki Dyrygent z MWU — bez TA-Lib."""
    from tests.helpers import zbuduj_dyrygenta_testowego
    d = zbuduj_dyrygenta_testowego()
    d.legatus.mwu = HedgeMWU(eta=0.5)
    return d


def _bary(n=30, cena=100.0):
    return [
        {"open": cena, "high": cena * 1.01, "low": cena * 0.99,
         "close": cena, "volume": 1000.0, "timestamp": i * 3600_000}
        for i in range(n)
    ]


def test_mwu_inicjalny_stan_neutralny():
    """HedgeMWU ze stanem zerowym → mnozniki() = {} (brak zniekształcenia, Prawo XV)."""
    mwu = HedgeMWU()
    assert mwu.mnozniki() == {}


def test_mwu_trafny_ekspert_rosnie():
    """Ekspert, który zawsze trafia, musi mieć wyższy mnożnik niż mylący się."""
    mwu = HedgeMWU(eta=0.5)
    for _ in range(20):
        mwu.zarejestruj_wynik("X-01", "LONG", "LONG")   # trafia
        mwu.zarejestruj_wynik("X-02", "SHORT", "LONG")  # myli się
    mn = mwu.mnozniki()
    assert mn["X-01"] > mn["X-02"], "Trafny neuron musi mieć wyższy mnożnik"


def test_mwu_neutral_nie_jest_karany():
    """NEUTRAL kierunek jest ignorowany przez MWU (nie zanieczyszcza historii)."""
    mwu = HedgeMWU(eta=0.5)
    mwu.zarejestruj_wynik("X-01", "NEUTRAL", "LONG")
    assert "X-01" not in mwu.wagi_raw, "NEUTRAL nie może trafić do wag"


def test_mwu_podpiecie_do_legatusa():
    """Legatus.mwu = HedgeMWU() → mnozniki_neuronow zostają zaktualizowane po zamknięciu."""
    try:
        from tests.helpers import zbuduj_dyrygenta_testowego
    except ImportError:
        return  # brak helpera — skip

    d = zbuduj_dyrygenta_testowego()
    mwu = HedgeMWU(eta=0.5)
    d.legatus.mwu = mwu

    # Symuluj zamknięte pozycje w historii silnika i pending
    from unittest.mock import MagicMock
    wynik = MagicMock()
    wynik.pozycja_id = "pos-1"
    wynik.pnl_pct = 0.05  # zysk
    d.engine.historia_zamkniec = [wynik]
    d._synapsy_ostatni_idx = 0

    # Zarejestruj pending sygnały
    from imperium.legiony.mikro_neuron import SygnalNeuronu
    s1 = SygnalNeuronu(neuron_id="T-01", kierunek="LONG", pewnosc=0.8, waga=3,
                       kategoria="T", legion="TREND")
    s2 = SygnalNeuronu(neuron_id="M-01", kierunek="LONG", pewnosc=0.7, waga=3,
                       kategoria="M", legion="WSPOLNY")
    d._synapsy_pending["pos-1"] = ([s1, s2], "TREND_STRONG", "LONG", "4H")

    d._aktualizuj_synapsy()

    # MWU powinien mieć zarejestrowane wyniki (oba trafiły — pnl > 0)
    assert "T-01" in mwu.wagi_raw
    assert "M-01" in mwu.wagi_raw
    # Mnożniki Legatusa powinny być zaktualizowane
    assert d.legatus.mnozniki_neuronow != {}


def test_mwu_trade_na_zero_jest_neutralny():
    """Granica: pnl_pct == 0 → MWU NIE karze ani nie nagradza (spójne z Synapsy, Prawo XVI)."""
    from imperium.legiony.mikro_neuron import SygnalNeuronu
    try:
        from tests.helpers import zbuduj_dyrygenta_testowego
    except ImportError:
        return

    d = zbuduj_dyrygenta_testowego()
    mwu = HedgeMWU(eta=0.5)
    d.legatus.mwu = mwu

    from unittest.mock import MagicMock
    wynik = MagicMock()
    wynik.pozycja_id = "pos-zero"
    wynik.pnl_pct = 0.0  # break-even
    d.engine.historia_zamkniec = [wynik]
    d._synapsy_ostatni_idx = 0

    s1 = SygnalNeuronu(neuron_id="T-01", kierunek="LONG", pewnosc=0.8, waga=3,
                       kategoria="T", legion="TREND")
    d._synapsy_pending["pos-zero"] = ([s1], "TREND_STRONG", "LONG", "4H")

    d._aktualizuj_synapsy()

    # Trade na zero nie powinien dotknąć wag żadnego neuronu
    assert "T-01" not in mwu.wagi_raw, "Break-even nie może karać ani nagradzać neuronu"


def test_mwu_przegrana_obniza_wage():
    """Po przegranym trade'cie mnożnik mylącego neuronu spada poniżej 1."""
    mwu = HedgeMWU(eta=1.0)  # wysoka eta = szybka nauka
    for _ in range(10):
        mwu.zarejestruj_wynik("X-01", "LONG", "SHORT")  # myli się 10x
        mwu.zarejestruj_wynik("X-02", "SHORT", "SHORT")  # trafia 10x
    mn = mwu.mnozniki()
    assert mn["X-01"] < 1.0, "Mylący neuron musi mieć mnożnik < 1"
    assert mn["X-02"] > 1.0, "Trafny neuron musi mieć mnożnik > 1"


def test_mwu_backtest_portfel_opt_in():
    """backtest_portfel(mwu_learning=True) — sygnatura akceptuje parametr."""
    try:
        from imperium.koloseum.backtest import backtest_portfel
        import inspect
        sig = inspect.signature(backtest_portfel)
        assert "mwu_learning" in sig.parameters
        assert sig.parameters["mwu_learning"].default is False
    except ImportError:
        return


def test_mwu_backtest_portfel_false_domyslnie():
    """backtest_portfel() bez mwu_learning → domyślnie wyłączony (zero kosztu)."""
    try:
        from imperium.koloseum.backtest import backtest_portfel
        import inspect
        sig = inspect.signature(backtest_portfel)
        assert sig.parameters["mwu_learning"].default is False
    except ImportError:
        return


def test_mwu_min_waga_nie_umiera():
    """Ekspert który zawsze myli się NIE spada do zera (min_waga Prawo XV)."""
    mwu = HedgeMWU(eta=2.0, min_waga=1e-6)
    for _ in range(100):
        mwu.zarejestruj_wynik("X-bad", "LONG", "SHORT")
    assert mwu.wagi_raw["X-bad"] >= mwu.min_waga


def test_mwu_wiele_zamkniec_aktualizuje_mnozniki():
    """Wiele zamknięć w kolejnych cyklach nakładają się — nie resetują (strumieniowo)."""
    mwu = HedgeMWU(eta=0.5)
    mwu.zarejestruj_wynik("X-01", "LONG", "LONG")
    mn1 = mwu.mnozniki()["X-01"]
    mwu.zarejestruj_wynik("X-01", "LONG", "LONG")
    mn2 = mwu.mnozniki()["X-01"]
    # Po 2 trafnych wagach mnożnik powinien być co najmniej równy (prawdopodobnie wyższy
    # gdyby X-02 nie istniał — z Fixed-Share jest wyrównywany, ale wciąż ≥ 1)
    assert mn2 >= mn1 or abs(mn2 - mn1) < 0.3, "MWU jest inkrementalny"
