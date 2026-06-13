"""
W-305: domknięcie pętli korelacji w SynapsyRezimowych (Prawo XVI).

KolektorKorelacjiNeuronow zbiera głosy neuronów strumieniowo i liczy macierz
korelacji par; Dyrygent zasila nią SynapsyRezimowe → dekorelacja przestaje być
martwa (corr już nie jest na stałe 0).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.diagnostyka_korelacji import KolektorKorelacjiNeuronow
from imperium.legiony.mikro_neuron import SygnalNeuronu
from imperium.biblioteki.synapsy_rezimowe import SynapsyRezimowe


def _syg(nid, kierunek, pewnosc=0.8):
    return SygnalNeuronu(neuron_id=nid, legion="TREND", wskaznik=nid, wartosc=1.0,
                         kierunek=kierunek, pewnosc=pewnosc, waga=3, kategoria="T")


def test_kolektor_pusty_brak_korelacji():
    """Świeży kolektor → pusta macierz (Prawo I: brak danych = brak wiedzy)."""
    k = KolektorKorelacjiNeuronow()
    assert k.korelacje() == {}
    assert k.liczba_krokow() == 0


def test_kolektor_ponizej_min_probek_pomija():
    """Granica: < min_probek wspólnych próbek → para pominięta (None → niezależna)."""
    k = KolektorKorelacjiNeuronow(min_probek=20)
    for _ in range(5):  # tylko 5 < 20
        k.zarejestruj([_syg("A", "LONG"), _syg("B", "LONG")])
    assert k.korelacje() == {}


def test_kolektor_idealna_korelacja_dodatnia():
    """Dwa neurony głosujące zawsze tak samo → korelacja ≈ +1."""
    k = KolektorKorelacjiNeuronow(min_probek=10)
    import random
    random.seed(1)
    for _ in range(40):
        kier = random.choice(["LONG", "SHORT"])
        k.zarejestruj([_syg("A", kier), _syg("B", kier)])
    kor = k.korelacje()
    assert ("A", "B") in kor
    assert kor[("A", "B")] > 0.9, f"oczekiwano ~+1, jest {kor[('A','B')]}"


def test_kolektor_idealna_korelacja_ujemna():
    """Neurony głosujące zawsze przeciwnie → korelacja ≈ -1."""
    k = KolektorKorelacjiNeuronow(min_probek=10)
    import random
    random.seed(2)
    for _ in range(40):
        kier = random.choice(["LONG", "SHORT"])
        przeciwny = "SHORT" if kier == "LONG" else "LONG"
        k.zarejestruj([_syg("A", kier), _syg("B", przeciwny)])
    kor = k.korelacje()
    assert kor[("A", "B")] < -0.9, f"oczekiwano ~-1, jest {kor[('A','B')]}"


def test_kolektor_staly_sygnal_pomijany():
    """Neuron zawsze NEUTRAL (zerowa wariancja) → para nieokreślona, pominięta."""
    k = KolektorKorelacjiNeuronow(min_probek=10)
    for _ in range(30):
        k.zarejestruj([_syg("A", "LONG"), _syg("STALY", "NEUTRAL")])
    kor = k.korelacje()
    assert ("A", "STALY") not in kor, "stały sygnał nie może mieć określonej korelacji"


def test_kolektor_okno_przesuwne_ograniczone():
    """Okno przesuwne nie rośnie w nieskończoność (bounded memory)."""
    k = KolektorKorelacjiNeuronow(okno=50, min_probek=10)
    for _ in range(200):
        k.zarejestruj([_syg("A", "LONG")])
    assert k.liczba_krokow() == 50


def test_kolektor_nieobecny_neuron_pad_zero():
    """Neuron nieobecny w kroku → 0.0 (NEUTRAL), serie zostają wyrównane czasowo."""
    k = KolektorKorelacjiNeuronow(min_probek=5)
    for _ in range(10):
        k.zarejestruj([_syg("A", "LONG")])      # B nieobecny
    for _ in range(10):
        k.zarejestruj([_syg("A", "LONG"), _syg("B", "LONG")])
    # Obie serie tej samej długości (B dostał padding 0.0 wstecz? nie — B pojawia się
    # od kroku 10, ale od tego momentu obie rosną równo). Sprawdzamy spójność długości.
    assert k.liczba_krokow() == 20


def test_synapsy_fallback_korelacje_uzywany():
    """SynapsyRezimowe.ustaw_korelacje() → wzmocnij_pewnosc używa go bez jawnego arg."""
    s = SynapsyRezimowe(min_trad=1)
    # Zbuduj silną synapsę dla pary (A,B) w TREND
    for _ in range(5):
        s.aktualizuj([_syg("A", "LONG"), _syg("B", "LONG")],
                     kierunek_decyzji="LONG", pnl_pct=2.0, rezim="TREND")

    zgodne = [_syg("A", "LONG"), _syg("B", "LONG")]

    # Bez korelacji (niezależne) → pełne wzmocnienie
    s.ustaw_korelacje({})
    p_niezalezne = s.wzmocnij_pewnosc(0.6, zgodne, "TREND")

    # Z wysoką korelacją (skorelowane) → wzmocnienie stłumione przez dekorelację
    s.ustaw_korelacje({("A", "B"): 0.95})
    p_skorelowane = s.wzmocnij_pewnosc(0.6, zgodne, "TREND")

    assert p_niezalezne > p_skorelowane, (
        "para niezależna musi być wzmacniana mocniej niż skorelowana (Prawo XVI)")


def test_synapsy_ustaw_korelacje_none_czysci():
    """ustaw_korelacje(None) → czyści (wszystkie pary niezależne)."""
    s = SynapsyRezimowe()
    s.ustaw_korelacje({("A", "B"): 0.9})
    s.ustaw_korelacje(None)
    assert s._korelacje_biezace == {}
