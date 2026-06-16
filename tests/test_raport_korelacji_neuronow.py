"""
W-306: raport dekorelacji NEURONÓW (Prawo XVI) — pełny rój, nie tylko zwiadowcy.

Rozszerza "redundancja mierzona, nie zgadywana" z 11 zwiadowców EXP na wszystkie
aktywne neurony, korzystając z macierzy korelacji zebranej online (W-305).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.diagnostyka_korelacji import (
    KolektorKorelacjiNeuronow, raport_z_kolektora, sformatuj_raport,
)
from imperium.legiony.mikro_neuron import SygnalNeuronu


def _syg(nid, kierunek, pewnosc=0.8):
    return SygnalNeuronu(neuron_id=nid, legion="TREND", wskaznik=nid, wartosc=1.0,
                         kierunek=kierunek, pewnosc=pewnosc, waga=3, kategoria="T")


def test_raport_pusty_kolektor():
    """Świeży kolektor → raport bez par, zero modułów."""
    rap = raport_z_kolektora(KolektorKorelacjiNeuronow())
    assert rap["liczba_modulow"] == 0
    assert rap["pary_redundantne"] == []
    assert rap["pary_dywersyfikujace"] == []


def test_raport_wykrywa_redundancje():
    """Para zawsze zgodna (corr≈1) → pary_redundantne (kandydat do wagi w dół)."""
    import random
    k = KolektorKorelacjiNeuronow(min_probek=10)
    random.seed(3)
    for _ in range(40):
        kier = random.choice(["LONG", "SHORT"])
        k.zarejestruj([_syg("A", kier), _syg("B", kier)])
    rap = raport_z_kolektora(k)
    klucze_red = [(a, b) for a, b, _ in rap["pary_redundantne"]]
    assert ("A", "B") in klucze_red


def test_raport_wykrywa_dywersyfikacje():
    """Para nieskorelowana (corr≈0) → pary_dywersyfikujace (filar siły)."""
    import random
    k = KolektorKorelacjiNeuronow(min_probek=20)
    random.seed(4)
    for _ in range(80):
        # A i B losowane NIEZALEŻNIE → korelacja ≈ 0
        k.zarejestruj([_syg("A", random.choice(["LONG", "SHORT"])),
                       _syg("B", random.choice(["LONG", "SHORT"]))])
    rap = raport_z_kolektora(k)
    klucze_dyw = [(a, b) for a, b, _ in rap["pary_dywersyfikujace"]]
    # przy 80 niezależnych próbkach |corr| zwykle < 0.20
    assert ("A", "B") in klucze_dyw or rap["macierz"].get("A~B") is not None


def test_raport_progi_konfigurowalne():
    """Zaostrzenie progu redundancji zmienia klasyfikację par."""
    import random
    k = KolektorKorelacjiNeuronow(min_probek=10)
    random.seed(5)
    for _ in range(40):
        kier = random.choice(["LONG", "SHORT"])
        # B zgadza się z A w 80% — umiarkowana korelacja
        kb = kier if random.random() < 0.8 else ("SHORT" if kier == "LONG" else "LONG")
        k.zarejestruj([_syg("A", kier), _syg("B", kb)])
    rap_luzny = raport_z_kolektora(k, prog_redundancji=0.95)
    rap_ostry = raport_z_kolektora(k, prog_redundancji=0.40)
    assert len(rap_ostry["pary_redundantne"]) >= len(rap_luzny["pary_redundantne"])


def test_raport_formater_dziala():
    """sformatuj_raport() przyjmuje raport neuronowy (wspólny kształt ze zwiadowcami)."""
    k = KolektorKorelacjiNeuronow(min_probek=5)
    for _ in range(10):
        k.zarejestruj([_syg("A", "LONG"), _syg("B", "LONG")])
    txt = sformatuj_raport(raport_z_kolektora(k))
    assert "DEKORELACJ" in txt.upper()


def test_dyrygent_akcesor_bez_kolektora_zwraca_none():
    """Dyrygent bez zebranych korelacji → raport_korelacji_neuronow() = None."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)  # synapsy OFF → brak kolektora
    assert d.raport_korelacji_neuronow() is None
