"""
Testy HARUSPEX — predykcyjny Namiestnik (kandydat #20).

Reguła Test-Granic (Prawo XXI):
  - pusta historia / brak przejść / < min_obserwacji → MILCZENIE (nie zgadujemy — Prawo I)
  - dokładnie min_obserwacji → prognoza (granica ≥ vs >)
  - próg P(zmiany) dokładnie == PROG_ZMIANY → NIE zmiana (strict >)
  - deterministyczne przejścia → p=1.0; pozostanie w reżimie → czy_zmiana=False
  - oszacuj_trafnosc bez look-ahead: deterministyczna sekwencja → wysoka trafność, Brier→0
  - walidacja konstruktora (min_obserwacji, prog_zmiany)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.koloseum.haruspex import Haruspex, Prognoza, PROG_ZMIANY


# ── MILCZENIE (za mało danych — Prawo I) ──────────────────────────────────────

def test_pusta_historia_milczy():
    h = Haruspex()
    p = h.przewiduj()
    assert p.czy_milczy is True
    assert p.docelowy_rezim is None
    assert p.n_obserwacji == 0


def test_jeden_rezim_bez_przejsc_milczy():
    h = Haruspex()
    h.dodaj_rezim("NORMAL")   # brak poprzednika → zero przejść
    p = h.przewiduj()
    assert p.czy_milczy is True


def test_ponizej_min_obserwacji_milczy():
    """4 przejścia z NORMAL przy min_obserwacji=5 → MILCZENIE."""
    h = Haruspex(min_obserwacji=5)
    for _ in range(4):
        h.dodaj_rezim("NORMAL")
        h.dodaj_rezim("VOLATILE")   # NORMAL→VOLATILE ×4, VOLATILE→NORMAL ×3
    p = h.przewiduj("NORMAL")
    assert p.czy_milczy is True
    assert p.n_obserwacji == 4


def test_dokladnie_min_obserwacji_prognozuje():
    """Granica: dokładnie 5 przejść z NORMAL → JUŻ prognozuje (≥, nie >)."""
    h = Haruspex(min_obserwacji=5)
    for _ in range(5):
        h.dodaj_rezim("NORMAL")
        h.dodaj_rezim("VOLATILE")
    p = h.przewiduj("NORMAL")
    assert p.czy_milczy is False
    assert p.n_obserwacji == 5
    assert p.docelowy_rezim == "VOLATILE"
    assert abs(p.prawdopodobienstwo - 1.0) < 1e-9


def test_nieznany_rezim_milczy():
    h = Haruspex(min_obserwacji=2)
    for _ in range(5):
        h.dodaj_rezim("NORMAL")
        h.dodaj_rezim("VOLATILE")
    p = h.przewiduj("PANIC")   # nigdy nie widziany jako źródło
    assert p.czy_milczy is True


# ── Predykcja i próg zmiany ───────────────────────────────────────────────────

def test_deterministyczne_przejscie_p1():
    """TREND_STRONG → RANGING zawsze → prognoza RANGING p=1.0, zmiana prawdopodobna."""
    h = Haruspex(min_obserwacji=3)
    for _ in range(6):
        h.dodaj_rezim("TREND_STRONG")
        h.dodaj_rezim("RANGING")
    p = h.przewiduj("TREND_STRONG")
    assert p.docelowy_rezim == "RANGING"
    assert abs(p.prawdopodobienstwo - 1.0) < 1e-9
    assert p.czy_zmiana_prawdopodobna is True


def test_pozostanie_w_rezimie_bez_zmiany():
    """NORMAL → NORMAL zawsze → docelowy NORMAL, czy_zmiana_prawdopodobna=False."""
    h = Haruspex(min_obserwacji=3)
    for _ in range(6):
        h.dodaj_rezim("NORMAL")
    p = h.przewiduj("NORMAL")
    assert p.docelowy_rezim == "NORMAL"
    assert p.czy_zmiana_prawdopodobna is False


def test_prog_zmiany_dokladnie_na_progu_nie_zmienia():
    """P(zmiany) == PROG_ZMIANY (0.5) → NIE zmiana (strict >, nie ≥)."""
    h = Haruspex(min_obserwacji=4, prog_zmiany=PROG_ZMIANY)
    # 5× A→A, 5× A→B: p_pozostania=0.5 → p_zmiany=0.5 == próg
    for _ in range(5):
        h.dodaj_rezim("A"); h.dodaj_rezim("A")
    for _ in range(5):
        h.dodaj_rezim("A"); h.dodaj_rezim("B")
    p = h.przewiduj("A")
    assert p.czy_zmiana_prawdopodobna is False   # 0.5 nie jest > 0.5


def test_prog_zmiany_powyzej_progu_zmienia():
    h = Haruspex(min_obserwacji=4, prog_zmiany=0.5)
    for _ in range(3):
        h.dodaj_rezim("A"); h.dodaj_rezim("A")   # 3× A→A
    for _ in range(7):
        h.dodaj_rezim("A"); h.dodaj_rezim("B")   # 7× A→B → p_zmiany=0.7 > 0.5
    p = h.przewiduj("A")
    assert p.czy_zmiana_prawdopodobna is True
    assert p.docelowy_rezim == "B"


def test_pusty_rezim_ignorowany():
    """dodaj_rezim('') to no-op — brak danych nie tworzy fałszywego przejścia."""
    h = Haruspex(min_obserwacji=1)
    h.dodaj_rezim("NORMAL")
    h.dodaj_rezim("")          # ignorowane
    h.dodaj_rezim("VOLATILE")
    # przejście powinno być NORMAL→VOLATILE (nie NORMAL→'' ani ''→VOLATILE)
    m = h.macierz()
    assert m.get("NORMAL", {}).get("VOLATILE") == 1.0
    assert "" not in m


# ── Pomiar trafności (bez look-ahead) ─────────────────────────────────────────

def test_oszacuj_trafnosc_deterministyczna():
    """Sekwencja ściśle naprzemienna A,B,A,B... → po nauce trafność wysoka, Brier→0."""
    seq = ["A", "B"] * 30
    r = Haruspex(min_obserwacji=2).oszacuj_trafnosc(seq)
    assert r.n_prognoz > 0
    assert r.trafnosc == 1.0        # deterministyczne → wszystkie trafione po min_obserwacji
    assert r.brier < 1e-9           # rozkład skupiony na faktycznym → Brier 0


def test_oszacuj_trafnosc_pusta_sekwencja():
    r = Haruspex().oszacuj_trafnosc([])
    assert r.n_prognoz == 0
    assert r.trafnosc == 0.0
    assert r.brier == 0.0


def test_oszacuj_trafnosc_bez_lookahead_nie_widzi_przyszlosci():
    """Pierwsze kroki muszą milczeć (macierz pusta) — dowód braku look-ahead."""
    seq = ["A", "B"] * 10
    r = Haruspex(min_obserwacji=3).oszacuj_trafnosc(seq)
    assert r.n_milczen >= 1          # zanim uzbiera 3 przejścia z A — milczy


# ── Walidacja konstruktora ────────────────────────────────────────────────────

def test_konstruktor_walidacja():
    import pytest
    with pytest.raises(ValueError):
        Haruspex(min_obserwacji=0)
    with pytest.raises(ValueError):
        Haruspex(prog_zmiany=1.5)
    with pytest.raises(ValueError):
        Haruspex(prog_zmiany=-0.1)


def test_macierz_prawdopodobienstwa_sumuja_do_1():
    h = Haruspex()
    for _ in range(10):
        h.dodaj_rezim("X"); h.dodaj_rezim("Y")
    m = h.macierz()
    for z_rezimu, rozklad in m.items():
        assert abs(sum(rozklad.values()) - 1.0) < 1e-6


def test_prognoza_typ():
    assert isinstance(Haruspex().przewiduj(), Prognoza)


def test_oszacuj_trafnosc_baseline_persystencji():
    """Baseline persystencji policzony i ≤ 1. Dla naprzemiennej A,B (zero lepkości)
    persystencja=0% a Haruspex=100% → jasny dowód wartości nad persystencją."""
    seq = ["A", "B"] * 30
    r = Haruspex(min_obserwacji=2).oszacuj_trafnosc(seq)
    assert r.baza_persystencji == 0.0    # nigdy next==current
    assert r.trafnosc == 1.0
    # sekwencja lepka (same A) — brak przejść, wszystko milczy albo A→A
    r2 = Haruspex(min_obserwacji=2).oszacuj_trafnosc(["A"] * 20)
    assert r2.baza_persystencji == 1.0 if r2.n_prognoz else True
