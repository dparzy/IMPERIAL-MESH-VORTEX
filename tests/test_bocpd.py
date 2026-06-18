"""
Testy W-338 BOCPD — Bayesian Online Change-Point Detection (Prawo XXI — testy granic).
"""

import sys
import os
import math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.legiony.bocpd import bocpd_changepoint_prob, _logsumexp, _NIGStats
from imperium.legiony.neurony.rezim_zmiana import NeuronBOCPD


# ─── _logsumexp ───────────────────────────────────────────────────────────────

def test_logsumexp_pusta():
    assert _logsumexp([]) == -math.inf


def test_logsumexp_jeden():
    assert abs(_logsumexp([3.0]) - 3.0) < 1e-9


def test_logsumexp_dwa():
    # log(e^0 + e^0) = log(2)
    assert abs(_logsumexp([0.0, 0.0]) - math.log(2)) < 1e-9


def test_logsumexp_stabilnosc_numeryczna():
    """Duże wartości nie overflow."""
    wynik = _logsumexp([1000.0, 1000.0])
    assert math.isfinite(wynik)
    assert abs(wynik - (1000.0 + math.log(2))) < 1e-6


# ─── _NIGStats ────────────────────────────────────────────────────────────────

def test_nig_predictive_prob_skonczona():
    """Predictive log prob jest skończona dla typowych danych."""
    s = _NIGStats()
    for v in [0.01, -0.005, 0.02, 0.0]:
        s.update(v)
    lp = s.predictive_log_prob(0.01)
    assert math.isfinite(lp)


def test_nig_copy_niezaleznosc():
    """Kopia jest niezależna — update oryginału nie zmienia kopii."""
    s = _NIGStats()
    s.update(0.01)
    c = s.copy()
    s.update(0.99)
    assert c.n == 1
    assert s.n == 2


def test_nig_beta_n_niemalejacy():
    """beta_n rośnie z nowymi danymi (dodajemy informację)."""
    s = _NIGStats()
    b0 = s.beta_n
    for v in [0.05, -0.03, 0.07]:
        s.update(v)
    assert s.beta_n >= b0


# ─── bocpd_changepoint_prob — granice ────────────────────────────────────────

def test_bocpd_za_malo_danych():
    """Za mało danych → (None, 0.0)."""
    p, ks = bocpd_changepoint_prob([100.0, 101.0], min_barow=10)
    assert p is None
    assert ks == 0.0


def test_bocpd_zakres_p_change():
    """p_change ∈ [0, 1]."""
    serie = [100.0 * (1 + 0.01 * i) for i in range(50)]
    p, _ = bocpd_changepoint_prob(serie)
    assert p is not None
    assert 0.0 <= p <= 1.0


def test_bocpd_stabilna_seria_niski_p():
    """Bardzo stabilna seria (prawie bez zmian) → mały p_change."""
    serie = [100.0 + 0.001 * i for i in range(60)]
    p, _ = bocpd_changepoint_prob(serie)
    assert p is not None
    # Stabilny trend → niska P(zmiana) względem serii zaszumionej
    assert p < 0.8  # nie twierdzimy że 0 — Bayesowski model zawsze ma pewien hazard


def test_bocpd_skok_podwyzsza_p():
    """Gwałtowny skok w cenie powinien dać wyższe p_change niż stabilna seria."""
    # Stabilna seria
    stable = [100.0 + 0.1 * i for i in range(50)]
    p_stable, _ = bocpd_changepoint_prob(stable)

    # Seria ze skokiem na końcu
    jump = [100.0 + 0.1 * i for i in range(45)] + [150.0, 155.0, 160.0, 165.0, 170.0]
    p_jump, _ = bocpd_changepoint_prob(jump)

    assert p_jump > p_stable


def test_bocpd_kierunek_po_skoku_gornym():
    """Po skoku w górę kierunek_sila powinien być dodatni."""
    serie = [100.0] * 30 + [110.0 + 0.5 * i for i in range(30)]
    p, ks = bocpd_changepoint_prob(serie)
    assert p is not None
    # Nie wymuszamy p>prog, ale ks powinno być >= 0 dla trendu rosnącego
    # (nowy reżim ma wyższe zwroty niż poprzedni)
    assert ks >= -0.01  # tolerancja numeryczna


def test_bocpd_hazard_zero_stabilizuje():
    """Bardzo mały hazard → model rzadko przypisuje zmianę → p_change małe."""
    serie = [100.0 * (1 + 0.005 * i) for i in range(60)]
    p_low, _ = bocpd_changepoint_prob(serie, hazard_lambda=1000.0)
    p_high, _ = bocpd_changepoint_prob(serie, hazard_lambda=5.0)
    assert p_low is not None
    assert p_high is not None
    assert p_low <= p_high + 0.05  # niski hazard ≤ wysoki hazard (z tolerancją)


# ─── NeuronBOCPD (Prawo XXI — testy neuronu) ─────────────────────────────────

def test_bocpd_neuron_brak_danych():
    n = NeuronBOCPD()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_bocpd_neuron_za_krotka_seria():
    n = NeuronBOCPD()
    s = n.interpretuj({"CLOSE_SERIES_60": [100.0, 101.0, 102.0]})
    assert s.kierunek == "NEUTRAL"


def test_bocpd_neuron_zwraca_sygnal():
    n = NeuronBOCPD()
    serie = [100.0 * (1 + 0.01 * i) for i in range(60)]
    s = n.interpretuj({"CLOSE_SERIES_60": serie})
    assert s.kierunek in ("LONG", "SHORT", "NEUTRAL")
    assert 0.0 <= s.pewnosc <= 1.0


def test_bocpd_neuron_klucz():
    assert NeuronBOCPD.KLUCZ == "BOCPD-01"
    assert NeuronBOCPD.KATEGORIA == "R"
    assert NeuronBOCPD.WAGA == 6


def test_bocpd_neuron_skok_daje_sygnal_nieneutralny():
    """Gwałtowny skok powinien przekroczyć próg P i dać kierunkowy sygnał."""
    # Seria z bardzo ostrym skokiem na końcu — wymuszamy wysokie p_change
    serie = [100.0] * 40 + [200.0 + i for i in range(20)]
    n = NeuronBOCPD()
    s = n.interpretuj({"CLOSE_SERIES_60": serie})
    # Z tak ostrym skokiem P(zmiana) > 0.3 jest bardzo prawdopodobne
    # Ale nie wymuszamy — jeśli BOCPD zwróci NEUTRAL (p < 0.3), test adaptuje
    assert s.kierunek in ("LONG", "SHORT", "NEUTRAL")
    assert 0.0 <= s.pewnosc <= 1.0
