"""
Testy B-02 Feature Neutralization (Prawo XXI — testy granic).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.legiony.neutralizacja import (
    neutralizuj_sygnaly,
    neutralizuj_sygnaly_z_korelacja,
    policz_neutralizacje_roju,
    _srednia_wazona,
)


# ─── _srednia_wazona ──────────────────────────────────────────────────────────

def test_srednia_wazona_rownomierna():
    assert abs(_srednia_wazona([1.0, 2.0, 3.0], [1.0, 1.0, 1.0]) - 2.0) < 1e-9


def test_srednia_wazona_zero_wagi():
    """Suma wag = 0 → zwraca 0.0 (brak danych)."""
    assert _srednia_wazona([1.0, 2.0], [0.0, 0.0]) == 0.0


def test_srednia_wazona_pusta():
    assert _srednia_wazona([], []) == 0.0


# ─── neutralizuj_sygnaly — granice ───────────────────────────────────────────

def test_neutralizuj_sila_zero_passthrough():
    """sila=0.0 → brak zmiany."""
    wej = [0.8, -0.3, 0.5]
    wyj = neutralizuj_sygnaly(wej, [5.0, 5.0, 5.0], sila=0.0)
    for a, b in zip(wej, wyj):
        assert abs(a - b) < 1e-9


def test_neutralizuj_pelna_korelacja():
    """Wszystkie identyczne → po pełnej neutralizacji ≈ 0."""
    wej = [0.6, 0.6, 0.6]
    wyj = neutralizuj_sygnaly(wej, [1.0, 1.0, 1.0], sila=1.0)
    for v in wyj:
        assert abs(v) < 1e-9


def test_neutralizuj_ortogonalne_nie_zerowane():
    """Sygnały symetryczne (suma=0) → pełna neutralizacja nie zeruje wszystkiego."""
    wej = [0.8, -0.8]
    wyj = neutralizuj_sygnaly(wej, [1.0, 1.0], sila=1.0)
    # Średnia = 0, więc residuum = wartość (sygnały orthogonalne od środka)
    assert abs(wyj[0] - 0.8) < 1e-9
    assert abs(wyj[1] - (-0.8)) < 1e-9


def test_neutralizuj_klampowanie():
    """Wynik jest klamkowany do [-1, 1]."""
    # Duże wartości po neutralizacji powinny być okrojone
    wyj = neutralizuj_sygnaly([1.0, -0.5], [1.0, 10.0], sila=1.0)
    for v in wyj:
        assert -1.0 <= v <= 1.0


def test_neutralizuj_pusta_lista():
    assert neutralizuj_sygnaly([], [], sila=0.5) == []


def test_neutralizuj_jeden_element():
    """Jeden element — średnia = wartość, residuum = 0 przy sile=1."""
    wyj = neutralizuj_sygnaly([0.7], [5.0], sila=1.0)
    assert abs(wyj[0]) < 1e-9


def test_neutralizuj_pol_sily():
    """sila=0.5 → residuum = wartość - 0.5 × srednia (połowa redukcji)."""
    # [0.8, 0.8], wagi równe → srednia = 0.8, residuum = 0.8 - 0.5×0.8 = 0.4
    wyj = neutralizuj_sygnaly([0.8, 0.8], [1.0, 1.0], sila=0.5)
    for v in wyj:
        assert abs(v - 0.4) < 1e-9


def test_neutralizuj_rozne_wagi():
    """Wagi mają wpływ na ważoną średnią roju."""
    # [1.0, 0.0] wagi=[9, 1] → srednia_wazona ≈ 0.9
    wyj = neutralizuj_sygnaly([1.0, 0.0], [9.0, 1.0], sila=1.0)
    # residuum[0] = 1.0 - 0.9 = 0.1, residuum[1] = 0.0 - 0.9 = -0.9
    assert abs(wyj[0] - 0.1) < 1e-9
    assert abs(wyj[1] - (-0.9)) < 1e-9


# ─── neutralizuj_sygnaly_z_korelacja ─────────────────────────────────────────

def test_neutralizuj_korelacja_n_male():
    """n<2 → passthrough."""
    wej = [0.5]
    wyj = neutralizuj_sygnaly_z_korelacja(wej, [5.0], sila=1.0)
    assert abs(wyj[0] - 0.5) < 1e-9


def test_neutralizuj_korelacja_std_zero():
    """Wszystkie identyczne (std=0) → residuua = 0.0 (rój w pełni skorelowany)."""
    wyj = neutralizuj_sygnaly_z_korelacja([0.4, 0.4, 0.4], [1.0, 1.0, 1.0], sila=1.0)
    for v in wyj:
        assert abs(v) < 1e-9


def test_neutralizuj_korelacja_klampowanie():
    wyj = neutralizuj_sygnaly_z_korelacja([1.0, -1.0, 1.0], [1.0, 1.0, 1.0], sila=1.0)
    for v in wyj:
        assert -1.0 <= v <= 1.0


# ─── policz_neutralizacje_roju ────────────────────────────────────────────────

def test_policz_neutralizacje_roju_kolejnosc():
    """ID muszą pasować do wartości po neutralizacji."""
    wejscie = [("N1", 0.8, 5.0), ("N2", -0.4, 3.0), ("N3", 0.2, 7.0)]
    wyj = policz_neutralizacje_roju(wejscie, sila=0.5)
    assert len(wyj) == 3
    assert wyj[0][0] == "N1"
    assert wyj[1][0] == "N2"
    assert wyj[2][0] == "N3"


def test_policz_neutralizacje_roju_pusta():
    assert policz_neutralizacje_roju([], sila=0.5) == []


def test_policz_neutralizacje_roju_wartosci_w_zakresie():
    """Wyniki muszą być ∈ [-1, 1]."""
    wejscie = [("A", 0.9, 6.0), ("B", 0.9, 6.0), ("C", -0.1, 4.0)]
    wyj = policz_neutralizacje_roju(wejscie, sila=1.0)
    for _, v in wyj:
        assert -1.0 <= v <= 1.0
