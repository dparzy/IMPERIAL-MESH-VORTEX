"""
Testy diagnostyki dekorelacji — Prawo XV (mierzyć redundancję, nie zgadywać).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.diagnostyka_korelacji import (
    sygnal_na_liczbe, korelacja_pearson, zbierz_sygnaly_zwiadowcow,
    macierz_korelacji, raport_dekorelacji, sformatuj_raport,
)


def _bar(c, o=None, h=None, l=None, vol=1000.0, ts=0):
    o = o if o is not None else c - 0.5
    h = h if h is not None else c + 1.0
    l = l if l is not None else c - 1.0
    return {"open": o, "high": h, "low": l, "close": c, "volume": vol, "timestamp": ts}


def _bary_trend(n=120, start=100.0, krok=0.4):
    return [_bar(start + i * krok, ts=i * 60) for i in range(n)]


# ─── Mapowanie sygnału ────────────────────────────────────────────────────────

def test_sygnal_na_liczbe():
    assert sygnal_na_liczbe("LONG", 0.8) == 0.8
    assert sygnal_na_liczbe("SHORT", 0.8) == -0.8
    assert sygnal_na_liczbe("NEUTRAL", 0.8) == 0.0


# ─── Korelacja Pearsona ───────────────────────────────────────────────────────

def test_korelacja_idealna_dodatnia():
    x = [1.0, 2.0, 3.0, 4.0]
    y = [2.0, 4.0, 6.0, 8.0]  # y = 2x
    assert abs(korelacja_pearson(x, y) - 1.0) < 1e-9


def test_korelacja_idealna_ujemna():
    x = [1.0, 2.0, 3.0, 4.0]
    y = [4.0, 3.0, 2.0, 1.0]
    assert abs(korelacja_pearson(x, y) - (-1.0)) < 1e-9


def test_korelacja_staly_wektor_none():
    """Stały wektor (zerowa wariancja) → korelacja nieokreślona (None, nie 0)."""
    x = [1.0, 1.0, 1.0, 1.0]
    y = [1.0, 2.0, 3.0, 4.0]
    assert korelacja_pearson(x, y) is None


def test_korelacja_za_malo_danych():
    assert korelacja_pearson([1.0], [2.0]) is None


# ─── Macierz korelacji ────────────────────────────────────────────────────────

def test_macierz_pary_bez_duplikatow():
    serie = {"A": [1.0, 2.0, 3.0], "B": [3.0, 2.0, 1.0], "C": [1.0, 2.0, 3.0]}
    m = macierz_korelacji(serie)
    # 3 moduły → 3 pary (A~B, A~C, B~C), bez przekątnej i duplikatów
    assert set(m.keys()) == {("A", "B"), ("A", "C"), ("B", "C")}
    assert abs(m[("A", "C")] - 1.0) < 1e-9   # identyczne
    assert abs(m[("A", "B")] - (-1.0)) < 1e-9  # przeciwne


# ─── Zbieranie sygnałów zwiadowców ────────────────────────────────────────────

def test_zbierz_pomija_wyciszonych():
    """Wyciszony zwiadowca (EXP-12) nie jest zbierany."""
    from imperium.legiony.zwiadowcy import ZwiadowcaAtmabhan, ZwiadowcaHurst
    bary = _bary_trend(n=120)
    serie = zbierz_sygnaly_zwiadowcow(bary, [ZwiadowcaAtmabhan(), ZwiadowcaHurst()], okno=60)
    assert "EXP-12" not in serie   # wyciszony
    assert "EXP-03" in serie       # aktywny
    assert len(serie["EXP-03"]) > 0


def test_zbierz_za_krotka_seria():
    from imperium.legiony.zwiadowcy import ZwiadowcaHurst
    bary = _bary_trend(n=30)
    serie = zbierz_sygnaly_zwiadowcow(bary, [ZwiadowcaHurst()], okno=60)
    assert serie["EXP-03"] == []  # okno większe niż seria


# ─── Pełny raport dekorelacji ─────────────────────────────────────────────────

def test_raport_dekorelacji_struktura():
    from imperium.legiony.rejestr import wszyscy_zwiadowcy
    bary = _bary_trend(n=130, krok=0.4)
    rap = raport_dekorelacji(bary, wszyscy_zwiadowcy(), okno=60, krok=5)
    assert "pary_redundantne" in rap
    assert "pary_dywersyfikujace" in rap
    assert "moduly_stale" in rap
    assert rap["liczba_modulow"] >= 1
    # Format tekstowy nie crashuje
    txt = sformatuj_raport(rap)
    assert "RAPORT DEKORELACJI" in txt


def test_raport_wykrywa_martwy_glos():
    """Moduł zawsze NEUTRAL w oknie = martwy głos (utrata potencjału)."""
    from imperium.legiony.zwiadowcy.baza import ZwiadowcaElitarny, RaportZwiadowcy

    class ZawszeNeutral(ZwiadowcaElitarny):
        KLUCZ = "EXP-TEST-N"
        WSKAZNIK = "test"
        KATEGORIA = "M"
        WYMAGA_BAROW = 1
        def analizuj(self, bary):
            return self._buduj_raport("NEUTRAL", 0.0, ["zawsze neutral"],
                                      {"main_value": 0}, len(bary))

    class ZawszeLong(ZwiadowcaElitarny):
        KLUCZ = "EXP-TEST-L"
        WSKAZNIK = "test"
        KATEGORIA = "M"
        WYMAGA_BAROW = 1
        def analizuj(self, bary):
            return self._buduj_raport("LONG", 0.7, ["zawsze long"],
                                      {"main_value": 1}, len(bary))

    bary = _bary_trend(n=80)
    rap = raport_dekorelacji(bary, [ZawszeNeutral(), ZawszeLong()], okno=60, krok=5)
    # Oba mają stały sygnał → oba w moduly_stale
    assert "EXP-TEST-N" in rap["moduly_stale"]
    assert "EXP-TEST-L" in rap["moduly_stale"]
