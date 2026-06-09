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


def test_strategie_vi_lv_futures_obecne():
    """Faza B: strategie Legio VI Ferrata (Futures/Leverage) w rejestrze, używają kat. R."""
    strategie = {s.id: s for s in wszystkie_strategie()}
    assert "VI-LV-001" in strategie, "Brak VI-LV-001 (Funding Contrarian)"
    assert "VI-LV-002" in strategie, "Brak VI-LV-002 (Liquidation Cascade)"
    # VI-LV-001 opiera się na obudzonej kategorii R (PSY)
    assert "PSY-01" in strategie["VI-LV-001"].wszystkie_klucze()
    assert "PSY-04" in strategie["VI-LV-002"].wszystkie_klucze()


def test_strategie_vi_lv_dobierane_w_volatile():
    """VI-LV-001 dopasowuje się gdy funding/LS ekstremalne (VOLATILE, 1H)."""
    sygnaly = {s.neuron_id: s for s in [
        _syg("PSY-01", "SHORT", 0.85), _syg("PSY-02", "SHORT", 0.80),
        _syg("VI-13", "SHORT", 0.6), _syg("V-13", "SHORT", 0.6),
    ]}
    top = dobierz_najlepsze(wszystkie_strategie(), sygnaly,
                            rezim="VOLATILE", top=5, interwal="1H")
    assert any(d.strategia.id == "VI-LV-001" for d in top), \
        "VI-LV-001 powinna pasować przy ekstremalnym fundingu w VOLATILE/1H"


def test_strategia_trojekran_eldera_obecna():
    """BIB-015: Triple Screen Eldera w rejestrze, używa Force Index V-05."""
    strategie = {s.id: s for s in wszystkie_strategie()}
    assert "IMV-TR-008" in strategie, "Brak IMV-TR-008 (Trójekran Eldera)"
    klucze = strategie["IMV-TR-008"].wszystkie_klucze()
    assert "V-05" in klucze, "Trójekran musi używać Force Index (V-05)"
    assert "X-03" in klucze, "Trójekran musi używać MACD (1. ekran trendu)"


def test_strategia_trojekran_dobierana_w_trendzie():
    """Trójekran dopasowuje się w silnym trendzie wzrostowym (4H/1D)."""
    sygnaly = {s.neuron_id: s for s in [
        _syg("X-03", "LONG", 0.85), _syg("V-05", "LONG", 0.80),
        _syg("XII-03", "LONG", 0.8), _syg("X-02", "LONG", 0.65),
    ]}
    top = dobierz_najlepsze(wszystkie_strategie(), sygnaly,
                            rezim="TREND_STRONG", top=5, interwal="4H")
    assert any(d.strategia.id == "IMV-TR-008" for d in top), \
        "IMV-TR-008 powinna pasować w silnym trendzie na 4H"


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


def test_dopasowanie_wyciszone_filtry_nie_karza():
    """Strategia z filtrami, ale WSZYSTKIE filtry wyciszone → brak kary (Prawo XV).
    Wynik musi być równy strategii bez filtrów przy tych samych wejściach."""
    we = ["XII-03", "XII-04"]
    sygnaly = {"XII-03": _syg("XII-03", "LONG", 0.9), "XII-04": _syg("XII-04", "LONG", 0.9)}

    # A: filtry zdefiniowane, ale nieobecne w sygnałach (wyciszone)
    strat_filtr = Strategia(id="T-F", nazwa="Z filtrem", legion="X", styl="TR",
                            warunki="t", neurony_wejscie=we, neurony_filtr=["V-01", "V-02"])
    # B: brak filtrów w ogóle
    strat_bez = Strategia(id="T-B", nazwa="Bez filtra", legion="X", styl="TR",
                          warunki="t", neurony_wejscie=we, neurony_filtr=[])

    d_filtr = dopasuj_strategie(strat_filtr, sygnaly)
    d_bez = dopasuj_strategie(strat_bez, sygnaly)
    assert d_filtr.wynik == d_bez.wynik, \
        f"Wyciszone filtry karzą: {d_filtr.wynik} ≠ {d_bez.wynik}"


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


# ── INTEGRACJA Z LEGATUSEM (silnik podpięty do Generała) ─────────────────────

def test_legatus_zwraca_dobrane_strategie():
    """Pełny Legatus na trendzie wzrostowym dobiera strategie LONG z bazy."""
    import math
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow

    bary = []
    p = 100.0
    for i in range(120):
        p += 0.6 + math.sin(i / 8) * 0.4
        bary.append({"open": p - 0.2, "high": p + 0.4, "low": p - 0.4,
                     "close": p, "volume": 1000 + i * 5, "timestamp": i})

    leg = zbuduj_legatusa(min_neuronow=3, min_przewaga=0.4, aktywuj_smc=False)
    w = BudowniczyWskaznikow().zbuduj(bary)
    raport = leg.fokus("BTCUSDT", w, rezim="TREND_STRONG", bary=bary)

    # raport ma pole strategie_dopasowane i coś w nim jest
    assert hasattr(raport, "strategie_dopasowane")
    assert len(raport.strategie_dopasowane) >= 1
    # na trendzie wzrostowym dobrane strategie idą LONG
    assert all(d.kierunek == "LONG" for d in raport.strategie_dopasowane)


def test_legatus_short_symetryczny():
    """Trend SPADKOWY → agregat SHORT i strategie dobrane SHORT (symetria LONG/SHORT)."""
    import math
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow

    bary = []
    p = 200.0
    for i in range(120):
        p -= 0.6 + math.sin(i / 8) * 0.4
        bary.append({"open": p + 0.2, "high": p + 0.4, "low": p - 0.4,
                     "close": p, "volume": 1000 + i * 5, "timestamp": i})

    leg = zbuduj_legatusa(min_neuronow=3, min_przewaga=0.4, aktywuj_smc=False)
    w = BudowniczyWskaznikow().zbuduj(bary)
    raport = leg.fokus("BTCUSDT", w, rezim="TREND_STRONG", bary=bary)

    assert raport.kierunek == "SHORT"
    assert len(raport.strategie_dopasowane) >= 1
    assert all(d.kierunek == "SHORT" for d in raport.strategie_dopasowane)


def test_dopasowanie_short_na_poziomie_silnika():
    """Silnik dobiera SHORT gdy wejścia strategii głosują SHORT."""
    strat = Strategia(
        id="TEST-S", nazwa="Test Short", legion="X", styl="TR", warunki="test",
        neurony_wejscie=["XII-03", "XII-04"], neurony_filtr=["V-01"],
    )
    sygnaly = {
        "XII-03": _syg("XII-03", "SHORT", 0.9),
        "XII-04": _syg("XII-04", "SHORT", 0.8),
        "V-01": _syg("V-01", "SHORT", 0.7),
    }
    d = dopasuj_strategie(strat, sygnaly)
    assert d.kierunek == "SHORT"
    assert d.zgodnych_wejsc == 2
    assert d.wynik > 0.5


def test_legatus_bez_strategii_pusta_lista():
    """Legatus bez bazy strategii zwraca pustą listę (brak kosztu, brak błędu)."""
    from imperium.legiony.legatus import Legatus
    from imperium.legiony.neurony.momentum import NeuronRSI
    leg = Legatus([NeuronRSI()], min_neuronow=1, min_przewaga=0.1)
    raport = leg.fokus("BTCUSDT", {"RSI_14": 25.0, "RSI_PREV": 24.0})
    assert raport.strategie_dopasowane == []
