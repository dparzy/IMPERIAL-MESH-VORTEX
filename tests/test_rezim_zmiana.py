"""
W-336 CP-01 — testy CUSUM change-point (helper + neuron).

Reguła Test-Granic: płaska seria→brak, świeży skok↑→LONG, ↓→SHORT, stary przełom
(poza oknem świeżości)→brak, za mało danych→brak, brak serii→NEUTRAL.
"""

from imperium.legiony.zmiana_rezimu import cusum_break, _zwroty
from imperium.legiony.neurony.rezim_zmiana import NeuronChangePoint
from imperium.legiony.rejestr import wszystkie_neurony


def test_zwroty_pomija_niedodatnia_baze():
    z = _zwroty([0.0, 100.0, 110.0])
    assert z[0] == 0.0          # baza 0 → 0.0
    assert abs(z[1] - 0.1) < 1e-9


def test_za_malo_danych_brak():
    assert cusum_break([100.0] * 5) == (None, 0.0)


def test_plaska_seria_brak():
    """Stała cena → zero zmienności → brak przełomu (nie udawaj)."""
    assert cusum_break([100.0] * 60) == (None, 0.0)


def test_swiezy_skok_w_gore_long():
    """Spokój, potem gwałtowny ciąg wzrostów na końcu → świeży przełom LONG."""
    seria = [100.0 + 0.01 * i for i in range(50)]      # leniwy dryf
    seria += [seria[-1] * (1.03 ** k) for k in range(1, 6)]  # nagły impuls w górę
    kier, sila = cusum_break(seria, prog_h=3.0)
    assert kier == "LONG"
    assert 0.0 < sila <= 1.0


def test_swiezy_skok_w_dol_short():
    seria = [100.0 - 0.01 * i for i in range(50)]
    seria += [seria[-1] * (0.97 ** k) for k in range(1, 6)]  # nagły impuls w dół
    kier, sila = cusum_break(seria, prog_h=3.0)
    assert kier == "SHORT"


def test_swiezosc_ostrzejsze_okno_wycisza_przelom():
    """
    Świeżość działa: ta sama seria z przełomem fires przy oknie 3, a przy oknie 1
    (tylko przełom dokładnie w ostatnim kroku) już nie — przełom nie jest na samym końcu.
    """
    seria = [100.0 + 0.01 * i for i in range(50)] + [100.5 * (1.03 ** k) for k in range(1, 5)]
    seria += [seria[-1] * 1.0005]  # ostatni bar: leniwy, NIE przebija sam z siebie
    kier_szerokie, _ = cusum_break(seria, prog_h=3.0, okno_swiezosci=3)
    kier_waskie, _ = cusum_break(seria, prog_h=3.0, okno_swiezosci=1)
    assert kier_szerokie == "LONG"      # przełom w ostatnich 3 krokach
    assert kier_waskie is None          # ale nie w samym ostatnim → poza wąskim oknem


# ── Neuron ───────────────────────────────────────────────────────────────────

def test_neuron_brak_serii_neutral():
    n = NeuronChangePoint()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_neuron_za_krotka_seria_neutral():
    n = NeuronChangePoint()
    s = n.interpretuj({"CLOSE_SERIES_60": [100.0] * 10})
    assert s.kierunek == "NEUTRAL"


def test_neuron_swiezy_przelom_long():
    n = NeuronChangePoint()
    seria = [100.0 + 0.01 * i for i in range(50)] + [100.5 * (1.03 ** k) for k in range(1, 6)]
    s = n.interpretuj({"CLOSE_SERIES_60": seria})
    assert s.kierunek == "LONG"


def test_neuron_plaska_seria_neutral_niska_pewnosc():
    n = NeuronChangePoint()
    s = n.interpretuj({"CLOSE_SERIES_60": [100.0] * 60})
    assert s.kierunek == "NEUTRAL"


def test_cp01_zarejestrowany_kategoria_R():
    klucze = {x.KLUCZ: x for x in wszystkie_neurony()}
    assert "CP-01" in klucze
    assert klucze["CP-01"].KATEGORIA == "R"
