"""
Testy Dywizji Strategii — Klucznik (spójność) + silnik dopasowania.
Wizja: sygnały neuronów → automatycznie dobrana najbliższa strategia.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from imperium.legiony.mikro_neuron import SygnalNeuronu
from imperium.legiony.strategie.baza import (
    Strategia, dopasuj_strategie, dobierz_najlepsze,
)
from imperium.legiony.strategie.rejestr_strategii import (
    wszystkie_strategie, klucze_uzyte_w_strategiach,
)
from imperium.legiony.rejestr import wszystkie_neurony


def _syg(kid, kier, pew=0.8):
    s = SygnalNeuronu(neuron_id=kid, legion="X", wskaznik="", wartosc=None,
                      kierunek=kier, pewnosc=pew, waga=7)
    s.policz_finalna()
    return s


# ── KLUCZNIK — spójność strategie ↔ kod (Prawo XIX/XXI) ──────────────────────

def test_klucznik_strategie_uzywaja_istniejacych_neuronow():
    """Każdy klucz w strategii MUSI istnieć w kodzie (żadnych neuronów-widm)."""
    klucze_strat = klucze_uzyte_w_strategiach()
    klucze_kod = {n.KLUCZ for n in wszystkie_neurony()}
    widma = klucze_strat - klucze_kod
    assert not widma, f"Strategie wskazują nieistniejące neurony: {sorted(widma)}"


def test_klucznik_strategie_uzywaja_aktywnych_neuronow():
    """Strategie nie powinny polegać na wyciszonych neuronach (martwy głos)."""
    klucze_strat = klucze_uzyte_w_strategiach()
    aktywne = {n.KLUCZ for n in wszystkie_neurony() if n.DOSTEPNY}
    wyciszone = klucze_strat - aktywne
    assert not wyciszone, f"Strategie wskazują wyciszone neurony: {sorted(wyciszone)}"


def test_rejestr_strategii_niepusty():
    strategie = wszystkie_strategie()
    assert len(strategie) >= 5
    # każda ma niepuste wejście i unikalne ID
    idki = [s.id for s in strategie]
    assert len(idki) == len(set(idki)), "Zduplikowane ID strategii"
    for s in strategie:
        assert s.neurony_wejscie, f"{s.id} bez neuronów wejścia"


# ── SILNIK DOPASOWANIA ───────────────────────────────────────────────────────

def test_dopasowanie_trend_wzrostowy():
    """Silny trend wzrostowy → strategie trendowe LONG z wysokim dopasowaniem."""
    sygnaly = {s.neuron_id: s for s in [
        _syg("XII-03", "LONG", 0.9), _syg("XII-04", "LONG", 0.85),
        _syg("XII-01", "LONG", 0.8), _syg("V-01", "LONG", 0.7),
        _syg("X-05", "LONG", 0.75), _syg("X-02", "LONG", 0.6),
    ]}
    top = dobierz_najlepsze(wszystkie_strategie(), sygnaly, rezim="TREND_STRONG", top=3)
    assert top, "Powinna być co najmniej jedna pasująca strategia"
    assert all(d.kierunek == "LONG" for d in top)
    # Złoty Orzeł (Golden Cross) powinien być wśród najlepszych
    assert any(d.strategia.id == "XII-TR-001" for d in top)
    assert top[0].wynik >= 0.5


def test_dopasowanie_neutralne_gdy_brak_sygnalow():
    """Brak sygnałów wejścia → strategia nie pasuje (NEUTRAL, wynik 0)."""
    strat = wszystkie_strategie()[0]
    d = dopasuj_strategie(strat, {}, rezim="NORMAL")
    assert d.kierunek == "NEUTRAL"
    assert d.wynik == 0.0


def test_dopasowanie_pomija_wyciszone_nie_karze():
    """Nieobecny (wyciszony) neuron nie obniża dopasowania — jest pomijany."""
    strat = Strategia(
        id="TEST-01", nazwa="Test", legion="X", styl="TR", warunki="test",
        neurony_wejscie=["XII-03", "XII-04"], neurony_filtr=["V-01"],
    )
    # tylko jeden z dwóch wejść ma sygnał — ale jest zgodny → pełna zgodność aktywnych
    sygnaly = {"XII-03": _syg("XII-03", "LONG", 0.9), "V-01": _syg("V-01", "LONG", 0.7)}
    d = dopasuj_strategie(strat, sygnaly)
    assert d.kierunek == "LONG"
    assert d.zgodnych_wejsc == 1
    assert d.wynik > 0.0


def test_dopasowanie_konflikt_kierunku():
    """Gdy wejścia idą w przeciwne strony — wygrywa silniejszy kierunek."""
    strat = Strategia(
        id="TEST-02", nazwa="Test", legion="X", styl="TR", warunki="test",
        neurony_wejscie=["X-01", "X-02"],
    )
    sygnaly = {
        "X-01": _syg("X-01", "LONG", 0.9),   # silny LONG
        "X-02": _syg("X-02", "SHORT", 0.3),  # słaby SHORT
    }
    d = dopasuj_strategie(strat, sygnaly)
    assert d.kierunek == "LONG"
