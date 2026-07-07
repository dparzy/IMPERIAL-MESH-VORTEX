"""Testy hipotezy B (narzedzia/hipoteza_b.py) — logika ważenia głosów IC + granice.

Reguła Test-Granic (Prawo XXI): moduł decyduje na ZNAKU agregatu → testujemy
zero/None/±/dokładnie-remis. Autor testuje happy-path; tu testujemy co MOŻE PÓJŚĆ ŹLE."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from narzedzia.hipoteza_b import (
    _glos, _ic_kierunkowy_train, _trafnosc_agregatu,
)


def test_glos_mapowanie():
    assert _glos("LONG") == 1
    assert _glos("SHORT") == -1
    assert _glos("NEUTRAL") == 0        # abstynencja → brak głosu
    assert _glos("") == 0 and _glos("cokolwiek") == 0


def test_ic_train_dodatni_gdy_trafia():
    # neuron A głosuje LONG i za każdym razem etykieta = +1 → IC = +1
    syg = [{"A": "LONG"}, {"A": "LONG"}, {"A": "LONG"}]
    wyn = [1, 1, 1]
    wagi, licz = _ic_kierunkowy_train(syg, wyn)
    assert wagi["A"] == 1.0 and licz["A"] == 3


def test_ic_train_ujemny_gdy_myli():
    # neuron myli się systematycznie: LONG a rynek spada → IC ujemny (kandydat do inwersji)
    syg = [{"A": "LONG"}, {"A": "LONG"}]
    wyn = [-1, -1]
    wagi, _ = _ic_kierunkowy_train(syg, wyn)
    assert wagi["A"] == -1.0


def test_ic_train_pomija_abstynencje():
    # NEUTRAL nie liczy się do IC (brak głosu, nie zerowa trafność)
    syg = [{"A": "NEUTRAL"}, {"A": "LONG"}]
    wyn = [1, 1]
    wagi, licz = _ic_kierunkowy_train(syg, wyn)
    assert licz["A"] == 1 and wagi["A"] == 1.0


def test_trafnosc_rowna_waga():
    # 2 barów: agregat LONG a etykieta +1 (trafny), potem SHORT a etykieta +1 (pudło) → 50%
    syg = [{"A": "LONG", "B": "LONG"}, {"A": "SHORT", "B": "SHORT"}]
    wyn = [1, 1]
    acc, akt = _trafnosc_agregatu(syg, wyn)
    assert akt == 2 and acc == 0.5


def test_trafnosc_agregat_neutralny_pomijany():
    # A:LONG B:SHORT → suma 0 → bar bez decyzji, nie liczony
    syg = [{"A": "LONG", "B": "SHORT"}]
    wyn = [1]
    acc, akt = _trafnosc_agregatu(syg, wyn)
    assert akt == 0 and acc != acc   # NaN gdy brak aktywnych barów


def test_wazenie_ic_odwraca_mylacy_neuron():
    # A myli się (IC<0) → w agregacie B jego głos LONG działa jak SHORT.
    # Bar testowy: tylko A głosuje LONG, rynek spada (etykieta -1).
    # Równa waga: agregat LONG → pudło. Ważony ujemnym IC: agregat SHORT → trafny.
    wagi = {"A": -1.0}
    syg = [{"A": "LONG"}]
    wyn = [-1]
    acc_a, _ = _trafnosc_agregatu(syg, wyn, wagi=None)
    acc_b, _ = _trafnosc_agregatu(syg, wyn, wagi=wagi)
    assert acc_a == 0.0 and acc_b == 1.0


def test_trafnosc_dokladny_remis_znaku():
    # suma dokładnie 0 z wagami → pomijany (granica > vs >=)
    wagi = {"A": 0.5, "B": 0.5}
    syg = [{"A": "LONG", "B": "SHORT"}]
    acc, akt = _trafnosc_agregatu(syg, [1], wagi=wagi)
    assert akt == 0


def test_pusty_zbior_nie_wybucha():
    acc, akt = _trafnosc_agregatu([], [])
    assert akt == 0 and acc != acc
    wagi, licz = _ic_kierunkowy_train([], [])
    assert wagi == {} and licz == {}
