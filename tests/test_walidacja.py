"""
Testy bramki anty-overfittingu Koloseum (W-282): DSR + PBO/CSCV.
Reguła Test-Granic: zero/None/±/dokładny-próg sprawdzone jawnie.
"""

import os
import sys


import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.koloseum.walidacja import (   # noqa: E402
    deflated_sharpe, pbo_cscv, bramka_walidacji, sharpe_zerowy,
    _phi, _phi_inv, PROG_PBO,
)

RNG = np.random.default_rng(42)


# ── Φ / Φ⁻¹ ──────────────────────────────────────────────────────────────────

def test_phi_granice_i_srodek():
    assert abs(_phi(0.0) - 0.5) < 1e-12
    assert _phi(3.0) > 0.99
    assert _phi(-3.0) < 0.01


def test_phi_inv_odwraca_phi():
    for p in (0.01, 0.1, 0.5, 0.9, 0.99):
        assert abs(_phi(_phi_inv(p)) - p) < 1e-7


def test_phi_inv_granice_rzucaja():
    for p in (0.0, 1.0, -0.1, 1.1):
        try:
            _phi_inv(p)
            raise AssertionError(f"p={p} powinno rzucić ValueError")
        except ValueError:
            pass


# ── SR₀ (selection-bias poprzeczka) ──────────────────────────────────────────

def test_sr0_jedna_proba_zero():
    """n_prob=1 → brak selection bias → SR₀=0 (granica dolna)."""
    assert sharpe_zerowy(1, 0.01) == 0.0


def test_sr0_rosnie_z_liczba_prob():
    """Więcej testowanych wariantów → wyższa poprzeczka."""
    assert sharpe_zerowy(100, 0.01) > sharpe_zerowy(10, 0.01) > 0


def test_sr0_zero_wariancji():
    """Zerowa wariancja między próbami → SR₀=0 (granica)."""
    assert sharpe_zerowy(50, 0.0) == 0.0


# ── Deflated Sharpe ──────────────────────────────────────────────────────────

def test_dsr_prawdziwa_przewaga_przechodzi():
    """Wyraźny edge (μ=0.2%, σ=1%) na 500 barach, 1 próba → DSR wysoki."""
    z = RNG.normal(0.002, 0.01, 500)
    w = deflated_sharpe(z, n_prob=1)
    assert w["dsr"] > 0.95 and w["ok"]


def test_dsr_szum_nie_przechodzi():
    """Czysty szum (μ=0) → DSR ~0.5, nie przechodzi."""
    z = RNG.normal(0.0, 0.01, 500)
    w = deflated_sharpe(z, n_prob=1)
    assert not w["ok"]


def test_dsr_selection_bias_obniza():
    """Ten sam zwycięzca, ale przy 100 próbach → DSR niższy niż przy 1."""
    z = RNG.normal(0.001, 0.01, 300)
    d1 = deflated_sharpe(z, n_prob=1)["dsr"]
    d100 = deflated_sharpe(z, n_prob=100)["dsr"]
    assert d100 < d1, "korekta o liczbę prób musi obniżać pewność"


def test_dsr_za_malo_obserwacji():
    """Granica długości: <10 obserwacji → odrzucone z powodem."""
    w = deflated_sharpe([0.01] * 5)
    assert not w["ok"] and "za mało" in w["powod"]


def test_dsr_zerowa_wariancja():
    """Stały zwrot (σ=0) → martwa strategia, odrzucona (granica)."""
    w = deflated_sharpe([0.01] * 50)
    assert not w["ok"] and "wariancja" in w["powod"]


# ── PBO / CSCV ───────────────────────────────────────────────────────────────

def test_pbo_szum_wysoki():
    """N strategii czystego szumu → wybór najlepszego IS nic nie mówi → PBO duże."""
    m = RNG.normal(0.0, 0.01, (240, 20))
    w = pbo_cscv(m, s_blokow=8)
    assert w["pbo"] is not None and w["pbo"] > PROG_PBO and not w["ok"]


def test_pbo_prawdziwy_edge_niski():
    """Jedna strategia z realnym edge wśród szumu → PBO niskie (zwycięzca trwały)."""
    m = RNG.normal(0.0, 0.01, (240, 10))
    m[:, 3] += 0.004  # wyraźna przewaga kolumny 3
    w = pbo_cscv(m, s_blokow=8)
    assert w["pbo"] is not None and w["pbo"] < PROG_PBO and w["ok"]


def test_pbo_liczba_podzialow():
    """C(8,4)=70 podziałów dla S=8."""
    m = RNG.normal(0.0, 0.01, (160, 5))
    w = pbo_cscv(m, s_blokow=8)
    assert w["n_podzialow"] == 70


def test_pbo_granice_wejscia():
    """Granice: 1 strategia → odrzucone; S nieparzyste → ValueError; za krótko → powód."""
    m1 = RNG.normal(0.0, 0.01, (100, 1))
    assert not pbo_cscv(m1, s_blokow=8)["ok"]
    try:
        pbo_cscv(RNG.normal(0, 1, (100, 3)), s_blokow=7)
        raise AssertionError("S nieparzyste powinno rzucić")
    except ValueError:
        pass
    w = pbo_cscv(RNG.normal(0, 1, (10, 3)), s_blokow=8)
    assert not w["ok"] and "za mało" in w["powod"]


def test_pbo_martwa_kolumna_nie_wybucha():
    """Strategia o zerowej wariancji (martwa) nie psuje procedury (granica σ=0)."""
    m = RNG.normal(0.0, 0.01, (160, 4))
    m[:, 0] = 0.0
    w = pbo_cscv(m, s_blokow=8)
    assert w["pbo"] is not None and 0.0 <= w["pbo"] <= 1.0


# ── Bramka łączna ────────────────────────────────────────────────────────────

def test_bramka_edge_przechodzi_szum_nie():
    m = RNG.normal(0.0, 0.01, (240, 10))
    m[:, 0] += 0.004
    ok = bramka_walidacji(m[:, 0], macierz_wszystkich=m, s_blokow=8)
    assert ok["ok"], f"realny edge powinien przejść: {ok}"
    szum = bramka_walidacji(m[:, 1], macierz_wszystkich=m, s_blokow=8)
    assert not szum["ok"], "szum nie może przejść bramki"
    assert szum["powod"], "odrzucenie zawsze z czytelnym powodem (Prawo I)"


def test_bramka_bez_macierzy_tylko_dsr():
    z = RNG.normal(0.002, 0.01, 500)
    w = bramka_walidacji(z, n_prob=1)
    assert w["pbo"] is None and w["ok"]


def test_bramka_n_prob_z_macierzy():
    """n_prob domyślnie = liczba kolumn macierzy (uczciwa korekta)."""
    m = RNG.normal(0.0, 0.01, (240, 50))
    w = bramka_walidacji(m[:, 0], macierz_wszystkich=m, s_blokow=8)
    # przy 50 próbach szumu DSR musi być niski
    assert not w["ok"]


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items())
          if k.startswith("test_") and callable(v)]
    bledy = 0
    for nazwa, f in fn:
        try:
            f()
            print(f"  ✅ {nazwa}")
        except Exception as e:
            bledy += 1
            print(f"  ❌ {nazwa}: {e}")
    print(f"\n{len(fn)-bledy}/{len(fn)} zaliczone")
    sys.exit(1 if bledy else 0)
