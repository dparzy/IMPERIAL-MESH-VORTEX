"""Testy walk-forward (W-345) — kroczące okna IS/OOS, WFE, werdykt przeuczenia.

Granice (Prawo XXI): brak look-ahead (OOS po IS), za mało barów, zero-wariancji
Sharpe, IS≤0 → WFE=0, werdykty ROBUST/PRZEUCZONY/SLABY.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.walk_forward import (
    walk_forward, generuj_okna, _sharpe, _wsp_zmiennosci, _werdykt,
    WynikOkna, OknoWF,
)
from imperium.koloseum.optymalizator import PrzestrzeńParam


# ── generuj_okna ─────────────────────────────────────────────────────────────

def test_okna_brak_lookahead():
    """OOS zawsze zaczyna się tam gdzie kończy IS — zero nakładania (Prawo I)."""
    okna = generuj_okna(1000, rozmiar_is=400, rozmiar_oos=100)
    for o in okna:
        assert o.oos_start == o.is_end, "OOS musi następować PO IS"
        assert o.is_start < o.is_end <= o.oos_start < o.oos_end


def test_okna_rolling_liczba():
    """1000 barów, IS=400 OOS=100 krok=100 → okna co 100, dopóki OOS mieści się."""
    okna = generuj_okna(1000, 400, 100, krok=100)
    # is_start: 0,100,... is_end=is_start+400, oos_end=is_end+100<=1000
    # ostatnie: is_start=500 → is_end=900 → oos_end=1000 OK; is_start=600→oos_end=1100>1000 stop
    assert len(okna) == 6
    assert okna[0].is_start == 0 and okna[-1].oos_end == 1000


def test_okna_zakotwiczony_rosnie():
    """Zakotwiczony: IS zawsze startuje od 0 i rośnie."""
    okna = generuj_okna(1000, 400, 100, krok=100, zakotwiczony=True)
    assert all(o.is_start == 0 for o in okna)
    assert okna[1].is_end > okna[0].is_end  # IS rośnie


def test_okna_za_malo_barow_puste():
    assert generuj_okna(300, 400, 100) == []


def test_okna_walidacja_rozmiarow():
    try:
        generuj_okna(1000, 1, 100)
        assert False
    except ValueError:
        pass


# ── _sharpe ──────────────────────────────────────────────────────────────────

def test_sharpe_zero_wariancji():
    """GRANICA: stałe zwroty → wariancja 0 → Sharpe 0 (nie dziel/0)."""
    assert _sharpe([0.01, 0.01, 0.01]) == 0.0


def test_sharpe_pusty_i_jeden():
    assert _sharpe([]) == 0.0
    assert _sharpe([0.5]) == 0.0


def test_sharpe_dodatni_ujemny():
    assert _sharpe([0.03, 0.01, 0.02, 0.04]) > 0
    assert _sharpe([-0.03, -0.01, -0.02, -0.04]) < 0


# ── _wsp_zmiennosci ──────────────────────────────────────────────────────────

def test_cv_stale_zero():
    assert _wsp_zmiennosci([0.5, 0.5, 0.5]) == 0.0


def test_cv_zmienne_dodatnie():
    assert _wsp_zmiennosci([0.4, 0.6, 0.5]) > 0


def test_cv_jeden_element():
    assert _wsp_zmiennosci([0.5]) == 0.0


# ── _werdykt (bezpośrednio — najczystsze dla PRZEUCZONY) ─────────────────────

def _okno_stub(sh_is, sh_oos):
    return WynikOkna(okno=OknoWF(0, 0, 1, 1, 2), parametry={}, sharpe_is=sh_is,
                     sharpe_oos=sh_oos, wynik_is=0, wynik_oos=0, efektywnosc=0)


def test_werdykt_slaby_oos_ujemny():
    w, _ = _werdykt(wfe_sr=0.9, oos_sharpe=-0.1, prog_wfe=0.5,
                    wyniki=[_okno_stub(0.5, -0.1)])
    assert w == "SLABY"


def test_werdykt_przeuczony():
    """IS dodatni, OOS dodatni-ale-zdegradowany, WFE < próg → PRZEUCZONY."""
    w, powod = _werdykt(wfe_sr=0.2, oos_sharpe=0.05, prog_wfe=0.5,
                        wyniki=[_okno_stub(1.0, 0.2)])  # IS>0
    assert w == "PRZEUCZONY"
    assert "WFE" in powod


def test_werdykt_robust():
    w, _ = _werdykt(wfe_sr=0.8, oos_sharpe=0.3, prog_wfe=0.5,
                    wyniki=[_okno_stub(0.4, 0.32)])
    assert w == "ROBUST"


def test_werdykt_wfe_nisko_is_zero_slaby():
    """WFE < próg ale żadne IS nie było dodatnie → SLABY, nie PRZEUCZONY."""
    w, _ = _werdykt(wfe_sr=0.1, oos_sharpe=0.05, prog_wfe=0.5,
                    wyniki=[_okno_stub(0.0, 0.05)])
    assert w == "SLABY"


# ── walk_forward end-to-end (ewaluator syntetyczny) ──────────────────────────

def _bary_ze_zwrotami(zwroty_per_idx):
    """Bary z polem 'r' = zwrot na barze (ewaluator je czyta)."""
    return [{"r": r, "close": 100 + i} for i, r in enumerate(zwroty_per_idx)]


def _ewaluator(bary, params):
    """Ignoruje params; zwraca zwroty z pól 'r' i kapitał = suma."""
    zwroty = [b["r"] for b in bary]
    return 1000 * (1 + sum(zwroty)), zwroty


def test_wf_brak_danych():
    bary = _bary_ze_zwrotami([0.01] * 100)
    r = walk_forward(bary, _ewaluator, [PrzestrzeńParam("x", 0.0, 1.0)],
                     rozmiar_is=500, rozmiar_oos=100, n_iteracji=3)
    assert r.werdykt == "BRAK_DANYCH"
    assert r.n_okien == 0


def test_wf_robust_zwroty_dodatnie():
    """Spójnie dodatnie zwroty (z wariancją) wszędzie → ROBUST."""
    import random
    random.seed(1)
    zwroty = [0.02 + random.uniform(-0.005, 0.005) for _ in range(800)]
    bary = _bary_ze_zwrotami(zwroty)
    r = walk_forward(bary, _ewaluator, [PrzestrzeńParam("x", 0.0, 1.0)],
                     rozmiar_is=300, rozmiar_oos=100, n_iteracji=3)
    assert r.n_okien >= 1
    assert r.oos_sharpe_zagregowany > 0
    assert r.werdykt == "ROBUST"


def test_wf_slaby_zwroty_ujemne():
    """Spójnie ujemne zwroty → OOS Sharpe ≤ 0 → SLABY."""
    import random
    random.seed(2)
    zwroty = [-0.02 + random.uniform(-0.005, 0.005) for _ in range(800)]
    bary = _bary_ze_zwrotami(zwroty)
    r = walk_forward(bary, _ewaluator, [PrzestrzeńParam("x", 0.0, 1.0)],
                     rozmiar_is=300, rozmiar_oos=100, n_iteracji=3)
    assert r.oos_sharpe_zagregowany <= 0
    assert r.werdykt == "SLABY"


def test_wf_raport_ma_stabilnosc_parametrow():
    bary = _bary_ze_zwrotami([0.01 + (i % 3) * 0.002 for i in range(800)])
    r = walk_forward(bary, _ewaluator, [PrzestrzeńParam("x", 0.0, 1.0)],
                     rozmiar_is=300, rozmiar_oos=100, n_iteracji=3)
    assert "x" in r.stabilnosc_parametrow
    assert len(r.okna) == r.n_okien
