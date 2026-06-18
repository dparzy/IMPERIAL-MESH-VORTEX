"""
Testy W-325 — GUBERNATOR (homeostatyczny sterownik portfela).

Prawo XXI (Reguła Test-Granic): neutralność (≈1.0 w stanie bazowym), granice mnożnika
(floor/ceiling), histereza (brak trzepotania), nadrzędność obsunięcia, monotoniczność.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.gubernator import (  # noqa: E402
    Gubernator, StanGubernatora, rozrzut_ocen,
    EKSPANSJA, NORMALNY, OSTROZNY, OBRONA, KWARANTANNA,
)


# ── Neutralność (Prawo XV) ──────────────────────────────────────────────────

def test_stan_bazowy_neutralny():
    """Wejście neutralne (konwikcja 0.5, rozrzut 0, kapitał zdrowy) → mnożnik ≈ 1.0."""
    g = Gubernator()
    s = g.ocen(konwikcja_koszyka=0.5, rozrzut_okazji=0.0, dd_frakcja=1.0, breadth=1.0)
    assert abs(s.mnoznik - 1.0) < 0.12, f"oczekiwano ≈1.0, jest {s.mnoznik}"
    assert s.postawa in (NORMALNY, OSTROZNY)


def test_zwraca_stan_gubernatora():
    g = Gubernator()
    s = g.ocen(konwikcja_koszyka=0.5, rozrzut_okazji=0.5)
    assert isinstance(s, StanGubernatora)
    assert s.powod and isinstance(s.powod, str)


# ── Granice mnożnika (floor/ceiling) ────────────────────────────────────────

def test_mnoznik_nie_przekracza_ceiling():
    """Maksymalna pewność przez wiele tyków → mnożnik dąży do ceiling, nie wyżej."""
    g = Gubernator(ceiling=1.3)
    s = None
    for _ in range(50):
        s = g.ocen(konwikcja_koszyka=1.0, rozrzut_okazji=1.0, dd_frakcja=1.0, breadth=1.0)
    assert s.mnoznik <= 1.3 + 1e-9
    assert s.mnoznik > 1.0, "przy pełnej pewności mnożnik powinien przekroczyć 1.0"
    assert s.postawa == EKSPANSJA


def test_mnoznik_nie_spada_ponizej_floor():
    """Głębokie obsunięcie przez wiele tyków → mnożnik dąży do floor, nie niżej."""
    g = Gubernator(floor=0.5)
    s = None
    for _ in range(50):
        s = g.ocen(konwikcja_koszyka=0.0, rozrzut_okazji=0.0, dd_frakcja=0.2, breadth=0.0)
    assert s.mnoznik >= 0.5 - 1e-9
    assert s.postawa == KWARANTANNA


# ── Nadrzędność obsunięcia ──────────────────────────────────────────────────

def test_obsuniecie_blokuje_ekspansje():
    """Nawet przy maksymalnej pewności — obsunięcie DD nie pozwala na ekspansję."""
    g = Gubernator()
    s = g.ocen(konwikcja_koszyka=1.0, rozrzut_okazji=1.0, dd_frakcja=0.7, breadth=1.0)
    assert s.postawa in (OBRONA, KWARANTANNA)
    assert s.mnoznik < 1.0


def test_kwarantanna_przy_glebokim_dd():
    g = Gubernator(prog_kwarantanna_dd=0.5)
    s = g.ocen(konwikcja_koszyka=0.8, rozrzut_okazji=0.8, dd_frakcja=0.4)
    assert s.postawa == KWARANTANNA
    assert s.mnoznik < 1.0   # ruszył ku floor (wygładzanie opóźnia pełny zjazd)
    # po ustabilizowaniu dochodzi do floor
    for _ in range(40):
        s = g.ocen(konwikcja_koszyka=0.8, rozrzut_okazji=0.8, dd_frakcja=0.4)
    assert abs(s.mnoznik - g.floor) < 1e-6


def test_granica_dd_dokladnie_prog_obrony():
    """dd_frakcja == prog_obrona_dd → kapitał uznany za zdrowy (warunek <, nie <=)."""
    g = Gubernator(prog_obrona_dd=0.95)
    # dokładnie na progu → NIE w obronie (zdrowy), więc postawa zależy od zdrowia
    s = g.ocen(konwikcja_koszyka=0.5, rozrzut_okazji=0.5, dd_frakcja=0.95)
    assert s.postawa not in (OBRONA, KWARANTANNA)


# ── Histereza (brak trzepotania) ────────────────────────────────────────────

def test_histereza_brak_trzepotania_na_granicy():
    """Sygnał oscylujący tuż przy progu nie powoduje skoków postawy co tyk."""
    g = Gubernator(prog_ekspansja=0.62, histereza=0.06)
    # ustaw EKSPANSJĘ
    for _ in range(10):
        g.ocen(konwikcja_koszyka=1.0, rozrzut_okazji=1.0)
    assert g.postawa == EKSPANSJA
    # zejdź TUŻ poniżej progu wejścia, ale w paśmie histerezy (próg - h < zdrowie < próg + h)
    # zdrowie ≈ 0.60 (między 0.56 a 0.68) → powinno UTRZYMAĆ ekspansję (histereza)
    s = g.ocen(konwikcja_koszyka=0.62, rozrzut_okazji=0.62, dd_frakcja=1.0, breadth=0.62)
    assert s.postawa == EKSPANSJA, f"histereza zawiodła: {s.postawa}"


def test_wygladzanie_mnoznika_plynne():
    """Skok wejścia z neutralnego do pełnej pewności nie daje natychmiastowego ceiling."""
    g = Gubernator(ceiling=1.3, alpha_wygladzania=0.3)
    g.ocen(konwikcja_koszyka=0.5, rozrzut_okazji=0.0)   # neutralny start
    s = g.ocen(konwikcja_koszyka=1.0, rozrzut_okazji=1.0)  # nagły skok
    assert s.mnoznik < 1.3, "wygładzanie powinno opóźnić dojście do ceiling"


# ── Monotoniczność ──────────────────────────────────────────────────────────

def test_wyzsza_konwikcja_wyzszy_mnoznik():
    """Przy zdrowym kapitale wyższa pewność ⇒ nie niższy mnożnik (po ustabilizowaniu)."""
    def ustabilizuj(konw, rozrzut):
        g = Gubernator()
        s = None
        for _ in range(40):
            s = g.ocen(konwikcja_koszyka=konw, rozrzut_okazji=rozrzut, dd_frakcja=1.0, breadth=1.0)
        return s.mnoznik
    niski = ustabilizuj(0.3, 0.2)
    wysoki = ustabilizuj(1.0, 1.0)
    assert wysoki > niski


# ── rozrzut_ocen (meta-cecha dyspersji) ─────────────────────────────────────

def test_rozrzut_pusta_i_jeden():
    assert rozrzut_ocen([]) == 0.0
    assert rozrzut_ocen([5.0]) == 0.0


def test_rozrzut_zerowy_rozstep():
    """Wszystkie oceny równe → brak wyrazistości lidera → 0.0."""
    assert rozrzut_ocen([3.0, 3.0, 3.0]) == 0.0


def test_rozrzut_wyrazny_lider():
    """Jeden odstający lider (reszta nisko) → wysoki rozrzut."""
    r = rozrzut_ocen([0.0, 0.1, 0.2, 5.0])
    assert r > 0.7, f"wyraźny lider powinien dać wysoki rozrzut, jest {r}"


def test_rozrzut_papka():
    """Oceny równomiernie rozłożone (mediana w środku) → rozrzut umiarkowany/niski."""
    r = rozrzut_ocen([1.0, 2.0, 3.0])
    assert r == 0.5   # (3-2)/(3-1)


def test_rozrzut_w_zakresie():
    for oceny in ([1, 2, 3, 4, 100], [-5, 0, 5], [0.1, 0.2], [10, 10, 10, 11]):
        r = rozrzut_ocen([float(x) for x in oceny])
        assert 0.0 <= r <= 1.0


# ── Walidacja konstruktora ──────────────────────────────────────────────────

def test_zle_parametry_rzucaja():
    for kw in (dict(floor=1.5), dict(ceiling=0.8),
               dict(prog_ostrozny=0.7, prog_ekspansja=0.6), dict(histereza=-0.1)):
        try:
            Gubernator(**kw)
            assert False, f"powinno rzucić ValueError dla {kw}"
        except ValueError:
            pass
