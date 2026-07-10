"""
Testy Filtra Ekonomicznego (ECON — market price of risk, ARTEMIS arXiv 2603.18107).

Reguła Test-Granic (Prawo XXI): próg λ_max i granica edge=0 mają testy wartości granicznych.
ZASADA WPIĘCIA: dowód, że opt-in domyślnie OFF nie zmienia zachowania sizingu.
"""

import math

from imperium.pretorianie.filtr_ekonomiczny import FiltrEkonomiczny
from imperium.pretorianie.sizing_przekonania import SizingPrzekonania


# ── Rdzeń: matematyka Sharpe'a zakładu ───────────────────────────────────────

def _sharpe_reczny(p, rr):
    q = 1.0 - p
    edge = p * rr - q
    var = p * rr * rr + q - edge * edge
    return edge / math.sqrt(var)


def test_zaklad_wiarygodny_przechodzi():
    """p=0.7, RR=3 → Sharpe ≈ 0.98 < 2.0 → dozwolone."""
    w = FiltrEkonomiczny().ocen(0.7, 3.0)
    assert w.dozwolone
    assert abs(w.sharpe_zakladu - _sharpe_reczny(0.7, 3.0)) < 1e-9


def test_zaklad_zbyt_dobry_wetowany():
    """p=0.9, RR=5 → Sharpe ≈ 2.44 > 2.0 → weto (market price of risk)."""
    w = FiltrEkonomiczny().ocen(0.9, 5.0)
    assert not w.dozwolone
    assert "market price of risk" in w.powod
    assert w.sharpe_zakladu > 2.0


def test_brak_przewagi_wetowany():
    """edge ≤ 0 (p=0.4, RR=1 → edge=-0.2) → weto, nie betujemy ujemnego EV."""
    w = FiltrEkonomiczny().ocen(0.4, 1.0)
    assert not w.dozwolone and w.edge < 0
    assert "przewag" in w.powod


def test_granica_edge_dokladnie_zero():
    """edge == 0 (p·RR = 1−p) musi być WETOWANE (≤ 0, nie < 0). Dla RR=1: p=0.5 → edge=0."""
    w = FiltrEkonomiczny().ocen(0.5, 1.0)
    assert w.edge == 0.0 and not w.dozwolone


def test_granica_sharpe_dokladnie_na_progu():
    """Sharpe == λ_max przechodzi (weto jest przy > λ_max, nie ≥). Dobieramy λ_max = S."""
    p, rr = 0.9, 5.0
    s = _sharpe_reczny(p, rr)
    tuz_pod = FiltrEkonomiczny(lambda_max=s)         # λ_max == Sharpe → dozwolone (nie >)
    assert tuz_pod.ocen(p, rr).dozwolone
    tuz_nad = FiltrEkonomiczny(lambda_max=s - 1e-6)  # λ_max < Sharpe → weto
    assert not tuz_nad.ocen(p, rr).dozwolone


def test_abstynencja_rr_niedodatnie():
    """RR ≤ 0 → abstynencja (przepuść), nie weto (Prawo XV)."""
    assert FiltrEkonomiczny().ocen(0.9, 0.0).dozwolone
    assert FiltrEkonomiczny().ocen(0.9, -2.0).dozwolone


def test_pewna_wygrana_wetowana():
    """p=1.0 (zdegenerowana wariancja, pewny zysk) = skrajne 'too good to be true' → weto."""
    w = FiltrEkonomiczny().ocen(1.0, 3.0)
    assert not w.dozwolone and math.isinf(w.sharpe_zakladu)


def test_p_zero_brak_przewagi():
    """p=0 → edge = -1 < 0 → weto (przez gałąź braku przewagi lub degeneracji)."""
    assert not FiltrEkonomiczny().ocen(0.0, 3.0).dozwolone


# ── Wpięcie opt-in do sizingu (ZASADA WPIĘCIA — domyślnie OFF) ────────────────

def test_sizing_bez_filtra_zachowanie_niezmienione():
    """Kluczowy dowód opt-in OFF: kelly_frakcja bez filtra == wartość sprzed zmiany."""
    # p=0.9, RR=5, half-Kelly: f=(5·0.9−0.1)/5=0.88; ×0.5 = 0.44
    assert SizingPrzekonania.kelly_frakcja(0.9, 5.0) == 0.44
    assert SizingPrzekonania.kelly_frakcja(0.9, 5.0, filtr_ekonomiczny=None) == 0.44


def test_sizing_z_filtrem_wetuje_niewiarygodny_zaklad():
    """Z filtrem: ten sam zbyt-dobry zakład (p=0.9, RR=5) → stawka 0.0."""
    f = FiltrEkonomiczny()
    assert SizingPrzekonania.kelly_frakcja(0.9, 5.0, filtr_ekonomiczny=f) == 0.0


def test_sizing_z_filtrem_przepuszcza_wiarygodny():
    """Z filtrem: wiarygodny zakład (p=0.7, RR=3) liczy się normalnie, filtr nie przeszkadza."""
    f = FiltrEkonomiczny()
    bez = SizingPrzekonania.kelly_frakcja(0.7, 3.0)
    z = SizingPrzekonania.kelly_frakcja(0.7, 3.0, filtr_ekonomiczny=f)
    assert z == bez and z > 0
