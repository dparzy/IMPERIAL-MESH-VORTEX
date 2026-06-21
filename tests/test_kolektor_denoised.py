"""
Testy integracji denoisingu (W-365) z KolektorKorelacjiNeuronow.
REGUŁA TEST-GRANIC: fallback gdy za mało danych, q≤1, seria stała; format zgodny.
"""

import numpy as np

from imperium.legiony.diagnostyka_korelacji import KolektorKorelacjiNeuronow


class _Syg:
    def __init__(self, neuron_id, kierunek, pewnosc):
        self.neuron_id = neuron_id
        self.kierunek = kierunek
        self.pewnosc = pewnosc


def _zasil(kol, n_krokow, seed=0):
    """Zasila kolektor losowymi (ale skorelowanymi) głosami 4 neuronów."""
    rng = np.random.default_rng(seed)
    for _ in range(n_krokow):
        wspolny = rng.choice(["LONG", "SHORT"])  # czynnik wspólny (ton)
        syg = [
            _Syg("A", wspolny if rng.random() > 0.1 else "NEUTRAL", 0.8),
            _Syg("B", wspolny if rng.random() > 0.1 else "NEUTRAL", 0.7),
            _Syg("C", rng.choice(["LONG", "SHORT", "NEUTRAL"]), 0.6),
            _Syg("D", rng.choice(["LONG", "SHORT", "NEUTRAL"]), 0.5),
        ]
        kol.zarejestruj(syg)


def test_denoised_fallback_za_malo_danych():
    # GRANICA: <min_probek kroków → fallback do surowej (ten sam wynik co korelacje())
    kol = KolektorKorelacjiNeuronow(okno=120, min_probek=20)
    _zasil(kol, 5)
    assert kol.korelacje_denoised() == kol.korelacje()


def test_denoised_fallback_q_ponizej_1():
    # GRANICA: t < n nie zajdzie tu, ale q≤1 gdy t≈n. min_probek wymusza t≥20>n=4,
    # więc sprawdzamy że przy dużej liczbie neuronów a małym t spada do surowej.
    kol = KolektorKorelacjiNeuronow(okno=120, min_probek=3)
    # 4 neurony, 3 kroki → t=3, n=4, q=0.75 ≤1 → fallback
    _zasil(kol, 3)
    assert kol.korelacje_denoised() == kol.korelacje()


def test_denoised_zwraca_pary_przy_dosc_danych():
    # Dość danych (t=200, n=4, q=50>1) → denoising aktywny, zwraca pary w formacie
    kol = KolektorKorelacjiNeuronow(okno=300, min_probek=20)
    _zasil(kol, 200)
    den = kol.korelacje_denoised()
    assert len(den) == 6  # C(4,2) par
    for (a, b), v in den.items():
        assert a < b  # klucze posortowane
        assert -1.0 <= v <= 1.0


def test_denoised_stala_seria_fallback():
    # GRANICA: wszystkie głosy stałe (zerowa wariancja) → NaN w corrcoef → fallback
    kol = KolektorKorelacjiNeuronow(okno=120, min_probek=20)
    for _ in range(50):
        kol.zarejestruj([_Syg("A", "LONG", 0.8), _Syg("B", "LONG", 0.8)])
    # nie może rzucić — fallback do surowej (która też pomija stałe pary)
    den = kol.korelacje_denoised()
    assert isinstance(den, dict)


def test_denoised_pusty_kolektor():
    # GRANICA: brak danych → {} (jak korelacje())
    kol = KolektorKorelacjiNeuronow()
    assert kol.korelacje_denoised() == {}
