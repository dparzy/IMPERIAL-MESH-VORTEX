"""Testy optymalizatora hiperparametrów DSR-guided (W-294)."""
import numpy as np

from imperium.koloseum.optymalizator import (
    optymalizuj,
    PrzestrzeńParam,
    WynikIteracji,
    RaportOptymalizacji,
)


# ── mock funkcja celu ────────────────────────────────────────────────────────

def _cel_staly_zysk(params):
    """Zawsze zwraca dobrą serię zwrotów niezależnie od params."""
    rng = np.random.default_rng(42)
    zwroty = list(rng.normal(0.003, 0.02, 200))
    return 10500.0, zwroty


def _cel_stala_strata(params):
    rng = np.random.default_rng(0)
    zwroty = list(rng.normal(-0.002, 0.025, 200))
    return 9500.0, zwroty


def _cel_zalezny(params):
    """Lepszy Sharpe dla wyższego min_pewnosc."""
    v = params.get("min_pewnosc", 0.5)
    rng = np.random.default_rng(int(v * 1000) % 1000)
    srednia = 0.001 + (v - 0.45) * 0.008
    zwroty = list(rng.normal(srednia, 0.02, 200))
    return 0.0, zwroty


def _cel_rzuca_wyjatek(params):
    raise RuntimeError("symulowany błąd backtesta")


# ── podstawowa struktura ──────────────────────────────────────────────────────

def test_zwraca_raport_optymalizacji():
    r = optymalizuj(
        _cel_staly_zysk,
        [PrzestrzeńParam("x", 0.0, 1.0)],
        n_iteracji=5,
        seed=0,
    )
    assert isinstance(r, RaportOptymalizacji)
    assert r.n_iteracji == 5
    assert len(r.historia) == 5


def test_historia_ma_wyniki_iteracji():
    r = optymalizuj(
        _cel_staly_zysk,
        [PrzestrzeńParam("x", 0.0, 1.0)],
        n_iteracji=3,
        seed=0,
    )
    for w in r.historia:
        assert isinstance(w, WynikIteracji)
        assert 0.0 <= w.parametry["x"] <= 1.0


# ── zakres parametrów ─────────────────────────────────────────────────────────

def test_parametry_w_zakresie_ciaglym():
    r = optymalizuj(
        _cel_staly_zysk,
        [PrzestrzeńParam("p", 0.45, 0.75)],
        n_iteracji=20,
        seed=0,
    )
    for w in r.historia:
        assert 0.45 <= w.parametry["p"] <= 0.75


def test_parametry_dyskretne_krok():
    r = optymalizuj(
        _cel_staly_zysk,
        [PrzestrzeńParam("okno", 150.0, 350.0, krok=25.0)],
        n_iteracji=20,
        seed=0,
    )
    for w in r.historia:
        val = w.parametry["okno"]
        assert abs(round(val) % 25) <= 1 or val == 150.0


def test_wielowymiarowa_przestrzen():
    r = optymalizuj(
        _cel_staly_zysk,
        [
            PrzestrzeńParam("min_pewnosc", 0.45, 0.75),
            PrzestrzeńParam("okno", 150.0, 350.0, krok=50.0),
            PrzestrzeńParam("sl_mult", 1.0, 4.0),
        ],
        n_iteracji=10,
        seed=0,
    )
    assert len(r.historia[0].parametry) == 3


# ── obsługa błędów ────────────────────────────────────────────────────────────

def test_wyjatki_w_celu_nie_przerywaja():
    r = optymalizuj(
        _cel_rzuca_wyjatek,
        [PrzestrzeńParam("x", 0.0, 1.0)],
        n_iteracji=5,
        seed=0,
    )
    assert r.n_iteracji == 5
    for w in r.historia:
        assert w.dsr == 0.0
        assert w.ok is False


# ── DSR jako cel (nie surowy Sharpe) ─────────────────────────────────────────

def test_najlepszy_wg_dsr_nie_sharpe():
    # DSR maleje z liczbą prób — przy małej liczbie prób wybieramy lepiej
    r = optymalizuj(
        _cel_zalezny,
        [PrzestrzeńParam("min_pewnosc", 0.45, 0.75)],
        n_iteracji=30,
        seed=42,
    )
    # najlepszy DSR ≥ każdego innego DSR
    assert all(r.najlepszy_dsr >= w.dsr for w in r.historia)


def test_n_udanych_nie_wieksze_niz_n_iteracji():
    r = optymalizuj(
        _cel_staly_zysk,
        [PrzestrzeńParam("x", 0.0, 1.0)],
        n_iteracji=20,
        seed=0,
    )
    assert 0 <= r.n_udanych <= r.n_iteracji


# ── deterministyczność ────────────────────────────────────────────────────────

def test_seed_daje_reprodukowalny_wynik():
    p = [PrzestrzeńParam("x", 0.0, 1.0)]
    r1 = optymalizuj(_cel_staly_zysk, p, n_iteracji=10, seed=7)
    r2 = optymalizuj(_cel_staly_zysk, p, n_iteracji=10, seed=7)
    assert r1.najlepszy_dsr == r2.najlepszy_dsr
    assert r1.najlepsze_parametry == r2.najlepsze_parametry


# ── brak przestrzeni ─────────────────────────────────────────────────────────

def test_pusta_przestrzen_rzuca():
    try:
        optymalizuj(_cel_staly_zysk, [], n_iteracji=5)
        assert False, "Powinien rzucić ValueError"
    except ValueError:
        pass
