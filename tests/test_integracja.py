"""
Testy integracji — Legatus + zwiadowcy EXP + most SMC + wagi reżimowe.
Sprawdza Prawo XV: czy potencjał jest faktycznie wykorzystany w pipeline.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.legatus import Legatus
from imperium.legiony.mikro_neuron import SygnalNeuronu
from imperium.legiony.rejestr import (
    wszystkie_neurony, wszyscy_zwiadowcy, zbuduj_legatusa, raport_potencjalu,
)
from imperium.legiony.zwiadowcy import aktywuj_neurony_smc


def _bar(close=100.0, open_=99.0, high=101.0, low=98.0, vol=1000.0):
    return {"open": open_, "high": high, "low": low, "close": close, "volume": vol, "timestamp": 0}


def _bary_trend(n=60, start=100.0, krok=0.5):
    return [_bar(start + i * krok, start + i * krok - 0.5,
                 start + i * krok + 1.0, start + i * krok - 1.0) for i in range(n)]


# ─── Kategoria w sygnale — wagi reżimowe ożywione ─────────────────────────────

def test_sygnal_niesie_kategorie():
    """SygnalNeuronu musi nieść kategorię (inaczej wagi reżimowe martwe)."""
    from imperium.legiony.neurony.momentum import NeuronRSI
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": 15.0})
    assert s.kategoria == "M", f"Kategoria RSI powinna być M, jest {s.kategoria}"


def test_wagi_rezimowe_dzialaja():
    """W reżimie TREND_STRONG neurony T dostają ×1.5 — waga musi się zmienić."""
    leg = Legatus(neurony=[], min_neuronow=1, min_przewaga=0.1)
    syg = [
        SygnalNeuronu("XII-01", "SWING", "ADX", 30, "LONG", 0.8, waga=6, kategoria="T"),
    ]
    syg[0].policz_finalna()
    waga_przed = syg[0].waga
    dostosowane = leg._dostosuj_wagi(syg, "TREND_STRONG")
    # T w TREND_STRONG = ×1.5 → 6 * 1.5 = 9
    assert dostosowane[0].waga == 9, f"Waga T w TREND powinna być 9, jest {dostosowane[0].waga}"
    assert waga_przed == 6  # oryginał nietknięty (copy)


# ─── Rejestr — pełny skład ────────────────────────────────────────────────────

def test_rejestr_wszystkie_neurony():
    neurony = wszystkie_neurony()
    assert len(neurony) == 34, f"Powinno być 34 neurony, jest {len(neurony)}"


def test_rejestr_wszyscy_zwiadowcy():
    zw = wszyscy_zwiadowcy()
    assert len(zw) == 12
    klucze = {z.KLUCZ for z in zw}
    assert klucze == {"EXP-01", "EXP-02", "EXP-03", "EXP-04", "EXP-05",
                      "EXP-06", "EXP-07", "EXP-08", "EXP-09", "EXP-10",
                      "EXP-11", "EXP-12"}


def test_raport_potencjalu():
    rap = raport_potencjalu()
    assert rap["neurony_lacznie"] == 34
    assert rap["zwiadowcy_exp"] == 12
    # EXP-12 (L2) wyciszony do czasu feedu orderbook
    assert rap["zwiadowcy_wyciszeni"] >= 1
    # Część neuronów wyciszona (on-chain/futures/SMC bez mostu/CVD)
    assert rap["neurony_wyciszone"] > 0
    assert 0 < rap["wykorzystanie_pct"] <= 100


# ─── Legatus z zwiadowcami — pełny pipeline ───────────────────────────────────

def test_legatus_odpala_zwiadowcow():
    """Legatus z barami odpala zwiadowców EXP — ich sygnały wchodzą do agregacji."""
    from imperium.legiony.neurony.momentum import NeuronRSI
    zwiadowcy = wszyscy_zwiadowcy()
    leg = Legatus(neurony=[NeuronRSI()], min_neuronow=1, min_przewaga=0.1,
                  zwiadowcy=zwiadowcy)

    bary = _bary_trend(n=60, krok=0.5)
    # wskazniki minimalny (RSI) — neuron RSI zagłosuje
    wskazniki = {"RSI_14": 25.0}
    raport = leg.fokus("BTCUSDT", wskazniki, rezim="NORMAL", bary=bary)

    # Powinny być sygnały z RSI + 5 zwiadowców EXP
    klucze = {s.neuron_id for s in raport.sygnaly}
    assert "X-01" in klucze            # RSI
    assert "EXP-01" in klucze          # Higuchi
    assert "EXP-03" in klucze          # Hurst
    assert "EXP-05" in klucze          # SMC


def test_legatus_bez_barow_tylko_neurony():
    """Bez barów zwiadowcy nie ruszają — tylko neurony głosują."""
    from imperium.legiony.neurony.momentum import NeuronRSI
    leg = Legatus(neurony=[NeuronRSI()], min_neuronow=1, min_przewaga=0.1,
                  zwiadowcy=wszyscy_zwiadowcy())
    raport = leg.fokus("BTCUSDT", {"RSI_14": 25.0}, rezim="NORMAL")  # brak bary
    klucze = {s.neuron_id for s in raport.sygnaly}
    assert "X-01" in klucze
    assert "EXP-01" not in klucze  # zwiadowcy nie ruszyli


def test_most_smc_w_pipeline():
    """
    PEŁNY MOST W LEGATUSIE: ZwiadowcaSMC wstrzykuje strefy → neurony SMC budzą się
    i głosują w tym samym fokus(). To jest dowód odzyskanego potencjału.
    """
    from imperium.legiony.neurony.struktura import NeuronOrderBlock, NeuronFVG, NeuronBOS
    aktywuj_neurony_smc()
    try:
        neurony = [NeuronOrderBlock(), NeuronFVG(), NeuronBOS()]
        leg = Legatus(neurony=neurony, min_neuronow=1, min_przewaga=0.1,
                      zwiadowcy=wszyscy_zwiadowcy())
        bary = _bary_trend(n=60, krok=0.5)
        raport = leg.fokus("BTCUSDT", {}, rezim="NORMAL", bary=bary)
        klucze = {s.neuron_id for s in raport.sygnaly}
        # SMC neurony obudzone przez wstrzyknięcie stref
        assert "SMC-01" in klucze
        assert "SMC-03" in klucze
    finally:
        for klasa in (NeuronOrderBlock, NeuronFVG, NeuronBOS):
            klasa.DOSTEPNY = False


def test_zbuduj_legatusa_pelny():
    """Fabryka składa Legatusa z pełnym składem i działającym mostem SMC."""
    from imperium.legiony.neurony.struktura import NeuronOrderBlock
    try:
        leg = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=True)
        bary = _bary_trend(n=60, krok=0.5)
        raport = leg.fokus("BTCUSDT", {"RSI_14": 25.0}, rezim="TREND_STRONG", bary=bary)
        # Pełny skład głosuje — neurony + zwiadowcy
        assert raport.aktywnych_neuronow > 5
        klucze = {s.neuron_id for s in raport.sygnaly}
        assert "EXP-05" in klucze
    finally:
        NeuronOrderBlock.DOSTEPNY = False
        from imperium.legiony.neurony.struktura import NeuronFVG, NeuronBOS
        NeuronFVG.DOSTEPNY = False
        NeuronBOS.DOSTEPNY = False


def test_prawo_xx_status_elitarny():
    """Prawo XX: status elitarny mierzony, nie opinią."""
    from imperium.legiony.rejestr import raport_elity, wszystkie_neurony, wszyscy_zwiadowcy

    raport = raport_elity()

    assert "neurony_elite" in raport
    assert "zwiadowcy_elite" in raport
    assert "lacznie_elite" in raport

    # X-25 i X-26 są elitarne
    klucze_elite = [e["klucz"] for e in raport["neurony_elite"]]
    assert "X-25" in klucze_elite
    assert "X-26" in klucze_elite

    # Każdy elitarny moduł musi mieć niepusty powód
    for e in raport["neurony_elite"] + raport["zwiadowcy_elite"]:
        assert e["powod"], f"{e['klucz']} jest elitarny, ale brak POWOD_ELITARNOSCI"

    # Wszyscy zwiadowcy Exploratores są elitarni (E1 — definicja klasy)
    zwiadowcy = wszyscy_zwiadowcy()
    for z in zwiadowcy:
        assert getattr(z, "ELITARNY", False), f"Zwiadowca {z.KLUCZ} powinien być ELITARNY"

    # Zwykłe neurony NIE są domyślnie elitarne — elita musi być zarobiona
    neurony = wszystkie_neurony()
    nie_elitarne = [n for n in neurony if not getattr(n, "ELITARNY", False)]
    assert len(nie_elitarne) > 0, "Część neuronów powinna NIE być elitarna"

    # Łączna liczba elitarnych > 0
    assert raport["lacznie_elite"] > 0

