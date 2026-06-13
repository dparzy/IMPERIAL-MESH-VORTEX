"""Testy Monte Carlo robustness (W-293)."""
import numpy as np

from imperium.koloseum.monte_carlo import (
    waliduj_mc,
    monte_carlo_shuffle,
    monte_carlo_bootstrap,
    pelen_raport_mc,
    WynikMonteCarlo,
    PelenRaportMC,
)


# ── dane pomocnicze ──────────────────────────────────────────────────────────

def _pnl_zyskowny(n=50, srednia=10.0, seed=0):
    rng = np.random.default_rng(seed)
    return list(rng.normal(srednia, 20.0, n))


def _pnl_stratny(n=50, seed=1):
    rng = np.random.default_rng(seed)
    return list(rng.normal(-8.0, 20.0, n))


# ── test granicy: za mało danych ─────────────────────────────────────────────

def test_shuffle_za_malo_transakcji():
    wynik = monte_carlo_shuffle([10.0, 20.0, -5.0], n_symulacji=100)
    assert wynik.ok is False
    assert "za mało" in wynik.powod


def test_bootstrap_za_malo_transakcji():
    wynik = monte_carlo_bootstrap([1.0] * 9, n_symulacji=100)
    assert wynik.ok is False
    assert "za mało" in wynik.powod


# ── struktura wyniku ──────────────────────────────────────────────────────────

def test_shuffle_zwraca_wynik_mc():
    wynik = monte_carlo_shuffle(_pnl_zyskowny(), n_symulacji=200, seed=42)
    assert isinstance(wynik, WynikMonteCarlo)
    assert wynik.metoda == "shuffle"
    assert wynik.n_symulacji == 200


def test_bootstrap_zwraca_wynik_mc():
    wynik = monte_carlo_bootstrap(_pnl_zyskowny(), n_symulacji=200, seed=42)
    assert isinstance(wynik, WynikMonteCarlo)
    assert wynik.metoda == "bootstrap"


# ── przedziały ufności są sensowne ───────────────────────────────────────────

def test_shuffle_percentyle_zysk(order=("p5", "mediana", "p95")):
    wynik = monte_carlo_shuffle(_pnl_zyskowny(n=100, srednia=15.0), n_symulacji=500, seed=0)
    assert wynik.sharpe_p5 <= wynik.sharpe_mediana <= wynik.sharpe_p95


def test_bootstrap_percentyle_sa_posortowane():
    wynik = monte_carlo_bootstrap(_pnl_zyskowny(), n_symulacji=300, seed=0)
    assert wynik.sharpe_p5 <= wynik.sharpe_mediana <= wynik.sharpe_p95


def test_maxdd_nie_ujemny():
    wynik = monte_carlo_shuffle(_pnl_zyskowny(), n_symulacji=200, seed=0)
    assert wynik.maxdd_mediana >= 0
    assert wynik.maxdd_p95 >= wynik.maxdd_mediana


# ── prawdopodobieństwa ─────────────────────────────────────────────────────

def test_p_dodatni_wysoki_dla_zysk():
    wynik = monte_carlo_shuffle(_pnl_zyskowny(n=100, srednia=20.0), n_symulacji=500, seed=0)
    assert wynik.p_sharpe_dodatni > 0.80


def test_p_dodatni_niski_dla_strata():
    wynik = monte_carlo_shuffle(_pnl_stratny(), n_symulacji=300, seed=0)
    assert wynik.p_sharpe_dodatni < 0.50


# ── werdykt ok ────────────────────────────────────────────────────────────────

def test_dobry_edge_przechodzi():
    pnl = [12.0] * 40 + [-5.0] * 10  # 80% win rate, stabilny
    wynik = monte_carlo_shuffle(pnl, n_symulacji=500, seed=42)
    assert wynik.ok is True
    assert wynik.powod == ""


def test_stratny_edge_nie_przechodzi():
    wynik = monte_carlo_shuffle(_pnl_stratny(n=50), n_symulacji=300, seed=0)
    assert wynik.ok is False


# ── reprodukowalność ──────────────────────────────────────────────────────────

def test_seed_daje_reprodukowalny_wynik():
    pnl = _pnl_zyskowny(n=50, seed=99)
    w1 = monte_carlo_shuffle(pnl, n_symulacji=200, seed=7)
    w2 = monte_carlo_shuffle(pnl, n_symulacji=200, seed=7)
    assert w1.sharpe_mediana == w2.sharpe_mediana


# ── pelen_raport_mc ──────────────────────────────────────────────────────────

def test_pelen_raport_struktura():
    pnl = _pnl_zyskowny()
    r = pelen_raport_mc(pnl, n_symulacji=200, seed=42)
    assert isinstance(r, PelenRaportMC)
    assert r.n_transakcji == len(pnl)
    assert isinstance(r.shuffle, WynikMonteCarlo)
    assert isinstance(r.bootstrap, WynikMonteCarlo)


def test_pelen_raport_ok_gdy_oba_ok():
    pnl = [15.0] * 40 + [-4.0] * 10
    r = pelen_raport_mc(pnl, n_symulacji=500, seed=42)
    if r.shuffle.ok and r.bootstrap.ok:
        assert r.ok is True
        assert r.powod == ""


def test_pelen_raport_nie_ok_gdy_jeden_nie_ok():
    pnl = _pnl_stratny(n=60)
    r = pelen_raport_mc(pnl, n_symulacji=200, seed=0)
    assert r.ok is False


# ─── W-308: waliduj_mc() — most do PaperTradingEngine ────────────────────────

class _MockWynik:
    def __init__(self, pnl_usdt): self.pnl_usdt = pnl_usdt


class _MockEngine:
    def __init__(self, pnl_lista, kapital=10_000.0):
        self.historia_zamkniec = [_MockWynik(p) for p in pnl_lista]
        self.kapital_startowy = kapital


def test_waliduj_mc_za_malo_transakcji():
    """< 10 trade'ów → ok=False, n_transakcji < 10."""
    eng = _MockEngine([10.0] * 5)
    r = waliduj_mc(eng, n_symulacji=100)
    assert r.ok is False
    assert r.n_transakcji == 5


def test_waliduj_mc_dobry_edge():
    """Zyski > straty → P(Sharpe>0) wysoki → ok=True."""
    pnl = [200.0] * 20 + [-50.0] * 10
    eng = _MockEngine(pnl)
    r = waliduj_mc(eng, n_symulacji=200, seed=1)
    assert r.n_transakcji == 30
    assert r.shuffle.p_sharpe_dodatni > 0.7


def test_waliduj_mc_kapital_z_silnika():
    """kapital_startowy z silnika trafia do MC (krzywa equity)."""
    eng = _MockEngine([50.0] * 30, kapital=5_000.0)
    r = waliduj_mc(eng, n_symulacji=100, seed=2)
    assert r.n_transakcji == 30


def test_waliduj_mc_granica_10_transakcji():
    """Dokładnie 10 trade'ów → nie blokuje (<10 blokuje, ≥10 liczy)."""
    eng_9 = _MockEngine([10.0] * 9)
    eng_10 = _MockEngine([10.0] * 10)
    r9 = waliduj_mc(eng_9, n_symulacji=50)
    r10 = waliduj_mc(eng_10, n_symulacji=50)
    assert r9.n_transakcji < 10
    assert r10.n_transakcji == 10


# ─── W-308: Dyrygent.raport_monte_carlo() ─────────────────────────────────────

def test_dyrygent_raport_mc_za_malo_zamkniec():
    """Dyrygent bez wystarczającej historii → raport_monte_carlo() = None."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    assert d.raport_monte_carlo() is None  # 0 zamknięć < 10


def test_dyrygent_raport_mc_struktura():
    """raport_monte_carlo() z wystarczającą historią → prawidłowe klucze."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    # Wstrzyknij fałszywe zamknięcia do silnika
    for p in [200.0] * 20 + [-50.0] * 10:
        d.engine.historia_zamkniec.append(_MockWynik(p))
    raport = d.raport_monte_carlo(n_symulacji=100, seed=5)
    assert raport is not None
    assert "ok" in raport
    assert "shuffle" in raport
    assert "bootstrap" in raport
    assert raport["n_transakcji"] == 30
