"""Testy Debaty Senatu (W-343) — Byk/Niedźwiedź/Cenzor + weto."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.senat.debata_senatu import (
    GlosNeuronu, SenatorByk, SenatorNiedzwiedz, Cenzor, KonsulSenatu,
    glosy_z_raportu,
)


def _glosy_bycze():
    return [
        GlosNeuronu("X-03", "LONG", 0.80, 8, "trend", "M"),
        GlosNeuronu("XII-03", "LONG", 0.70, 7, "trend", "T"),
        GlosNeuronu("V-01", "LONG", 0.60, 6, "trend", "F"),
    ]


def test_senator_byk_zbiera_long():
    arg = SenatorByk().przemow(_glosy_bycze())
    assert arg.stanowisko == "LONG"
    assert arg.sila > 0
    assert len(arg.dowody) == 3


def test_senator_byk_ignoruje_short():
    glosy = [GlosNeuronu("X-01", "SHORT", 0.9, 8, "trend", "M")]
    arg = SenatorByk().przemow(glosy)
    assert arg.sila == 0.0  # brak LONG


def test_senator_byk_ignoruje_risk_filter_mechanizm():
    """Byk liczy tylko mechanizmy kierunkowe — risk_filter pomijany."""
    glosy = [GlosNeuronu("Z-01", "LONG", 0.9, 8, "risk_filter", "Z")]
    arg = SenatorByk().przemow(glosy)
    assert arg.sila == 0.0


def test_senator_niedzwiedz_zbiera_short():
    glosy = [GlosNeuronu("X-01", "SHORT", 0.7, 6, "mean_rev", "M")]
    arg = SenatorNiedzwiedz().przemow(glosy)
    assert arg.stanowisko == "SHORT"
    assert arg.sila > 0


def test_cenzor_brak_alarmow_ok():
    arg = Cenzor().przemow(_glosy_bycze(), rezim="NORMAL")
    assert arg.stanowisko == "OK"
    assert arg.sila == 0.0


def test_cenzor_panic_zawsze_weto():
    """Reżim PANIC gwarantuje weto Cenzora niezależnie od alarmów."""
    arg = Cenzor().przemow(_glosy_bycze(), rezim="PANIC")
    assert arg.stanowisko == "WSTRZYMAJ"
    assert "PANIC" in " ".join(arg.dowody)


def test_cenzor_wysokie_ryzyko_weto():
    """Suma alarmów >= prog_weta → WSTRZYMAJ."""
    glosy = [
        GlosNeuronu("Z-01", "SHORT", 0.9, 8, "risk_filter", "Z"),
        GlosNeuronu("Z-04", "SHORT", 0.9, 8, "risk_filter", "Z"),
    ]  # siła = 0.9*8 + 0.9*8 = 14.4 >= 12.0
    arg = Cenzor(prog_weta=12.0).przemow(glosy)
    assert arg.stanowisko == "WSTRZYMAJ"


def test_cenzor_granica_progu_dokladnie():
    """Siła alarmów dokładnie == prog → weto (>=, nie >)."""
    glosy = [GlosNeuronu("Z-01", "SHORT", 1.0, 12, "risk_filter", "Z")]  # 12.0
    arg = Cenzor(prog_weta=12.0).przemow(glosy)
    assert arg.stanowisko == "WSTRZYMAJ"


def test_konsul_byk_wygrywa():
    konsul = KonsulSenatu()
    w = konsul.obraduj(_glosy_bycze(), rezim="TREND_STRONG")
    assert w.kierunek == "LONG"
    assert w.pewnosc > 0.5
    assert not w.weto_cenzora


def test_konsul_weto_panic_neutralizuje():
    konsul = KonsulSenatu()
    w = konsul.obraduj(_glosy_bycze(), rezim="PANIC")
    assert w.kierunek == "NEUTRAL"
    assert w.pewnosc == 0.0
    assert w.weto_cenzora
    assert w.mnoznik_ryzyka == 0.0


def test_konsul_remis_neutral():
    """Równa siła Byka i Niedźwiedzia → NEUTRAL."""
    glosy = [
        GlosNeuronu("X-03", "LONG", 0.5, 6, "trend", "M"),
        GlosNeuronu("X-01", "SHORT", 0.5, 6, "trend", "M"),
    ]
    konsul = KonsulSenatu()
    w = konsul.obraduj(glosy, rezim="NORMAL")
    assert w.kierunek == "NEUTRAL"


def test_konsul_redukcja_ryzyka_bez_weta():
    """Alarmy poniżej progu weta → mnożnik ryzyka < 1.0 ale > 0."""
    glosy = _glosy_bycze() + [
        GlosNeuronu("Z-01", "SHORT", 0.5, 6, "risk_filter", "Z"),  # 3.0 < 12
    ]
    konsul = KonsulSenatu()
    w = konsul.obraduj(glosy, rezim="NORMAL")
    assert not w.weto_cenzora
    assert 0.0 < w.mnoznik_ryzyka < 1.0


def test_konsul_prog_przewagi():
    """Za słaba dominacja (< prog_przewagi) → NEUTRAL."""
    glosy = [
        GlosNeuronu("X-03", "LONG", 0.52, 6, "trend", "M"),
        GlosNeuronu("X-01", "SHORT", 0.48, 6, "trend", "M"),
    ]
    konsul = KonsulSenatu(prog_przewagi=0.70)  # wymaga 70% dominacji
    w = konsul.obraduj(glosy, rezim="NORMAL")
    assert w.kierunek == "NEUTRAL"


def test_protokol_ma_trzech_senatorow():
    konsul = KonsulSenatu()
    w = konsul.obraduj(_glosy_bycze())
    assert len(w.protokol) == 3
    senatorzy = {a.senator for a in w.protokol}
    assert senatorzy == {"Byk", "Niedźwiedź", "Cenzor"}


def test_glosy_z_raportu_adapter():
    """Adapter buduje głosy z obiektu z .sygnaly."""
    class FakeSygnal:
        def __init__(self, klucz, kierunek, pewnosc):
            self.klucz_neuronu = klucz
            self.kierunek = kierunek
            self.pewnosc_finalna = pewnosc
            self.waga = 5.0

    class FakeRaport:
        sygnaly = [FakeSygnal("X-03", "LONG", 0.8), FakeSygnal("Z-01", "SHORT", 0.4)]

    mapa = {"X-03": "trend", "Z-01": "risk_filter"}
    glosy = glosy_z_raportu(FakeRaport(), mapa_mechanizmow=mapa)
    assert len(glosy) == 2
    assert glosy[0].mechanizm == "trend"
    assert glosy[1].mechanizm == "risk_filter"


def test_glosy_z_raportu_pusty():
    class Pusty:
        sygnaly = []
    assert glosy_z_raportu(Pusty()) == []
