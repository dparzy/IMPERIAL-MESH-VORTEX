"""Testy Legionów Cieni (imperium/koloseum/legiony_cieni.py) — Prawo XV/XVI + XXI.

Testy granic offline: przycinanie progów na skraju [0,1], watermark bez podwójnego
zapisu, graceful przy awarii cienia, zapis CIEN_PNL wstrzykniętym kolektorem (bez SQLite).
"""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum import legiony_cieni as lc


# ─── Fałszywe klocki (bez sieci/SQLite) ──────────────────────────────────────

class _FakeZamkniecie:
    def __init__(self, pnl_pct, symbol="BTCUSDT", rezim="TREND"):
        self.pnl_pct = pnl_pct
        self.symbol = symbol
        self.rezim = rezim


class _FakeEngine:
    def __init__(self):
        self.historia_zamkniec = []
        self.kapital_calkowity = 10000.0


class _FakeDyrygent:
    """cykl() opcjonalnie dokłada zamknięcie do silnika; może symulować awarię."""
    def __init__(self, engine, pnl_na_cykl=None, pada=False):
        self.engine = engine
        self._pnl = list(pnl_na_cykl or [])
        self._pada = pada

    def cykl(self, symbol, bary, rezim="NORMAL", timestamp=None):
        if self._pada:
            raise RuntimeError("cień padł")
        if self._pnl:
            self.engine.historia_zamkniec.append(_FakeZamkniecie(self._pnl.pop(0), symbol, rezim))
            return type("D", (), {"wszedl": True})()
        return type("D", (), {"wszedl": False})()


def _cien(nazwa, pnl_na_cykl=None, pada=False):
    eng = _FakeEngine()
    return lc.Cien(nazwa=nazwa, dyrygent=_FakeDyrygent(eng, pnl_na_cykl, pada), engine=eng, opis=nazwa)


# ─── warianty_domyslne (granica progu) ───────────────────────────────────────

def test_warianty_trzy_domyslne():
    w = lc.warianty_domyslne(0.55)
    assert [v["nazwa"] for v in w] == ["bez_wet", "prog_lagodny", "prog_surowy"]
    assert w[1]["min_pewnosc"] == 0.45 and w[2]["min_pewnosc"] == 0.65
    assert w[0]["bez_wet"] is True and w[1]["bez_wet"] is False


def test_prog_lagodny_przyciety_do_zera():
    w = lc.warianty_domyslne(0.05)
    lagodny = next(v for v in w if v["nazwa"] == "prog_lagodny")
    assert lagodny["min_pewnosc"] == 0.0          # 0.05-0.10 przycięte do 0, nie -0.05


def test_prog_surowy_przyciety_do_jeden():
    w = lc.warianty_domyslne(0.95)
    surowy = next(v for v in w if v["nazwa"] == "prog_surowy")
    assert surowy["min_pewnosc"] == 1.0           # 0.95+0.10 przycięte do 1, nie 1.05


# ─── krok: zapis CIEN_PNL + watermark ────────────────────────────────────────

def test_krok_zapisuje_nowe_zamkniecia():
    zebrane = []
    legiony = lc.LegionyCieni([_cien("a", pnl_na_cykl=[2.5])], arena_zapis=lambda w: zebrane.extend(w) or len(w))
    wynik = legiony.krok("BTCUSDT", [{"close": 1}], rezim="TREND")
    assert wynik["a"]["nowe_zamkniecia"] == 1 and wynik["a"]["weszedl"] is True
    assert len(zebrane) == 1
    rodzaj, neuron, wartosc, nota = zebrane[0]
    assert rodzaj == lc.RODZAJ_ARENA and neuron == "a" and wartosc == 2.5
    assert "TREND" in nota


def test_watermark_bez_podwojnego_zapisu():
    zebrane = []
    c = _cien("a", pnl_na_cykl=[1.0])       # zamknięcie tylko w 1. cyklu
    legiony = lc.LegionyCieni([c], arena_zapis=lambda w: zebrane.extend(w) or len(w))
    legiony.krok("BTCUSDT", [{"close": 1}])   # zapisze 1
    legiony.krok("BTCUSDT", [{"close": 2}])   # brak nowych → nic
    assert len(zebrane) == 1                   # to samo zamknięcie NIE zapisane dwa razy


def test_pusty_krok_nie_zapisuje():
    zapisano = {"n": 0}
    def _zap(w):
        zapisano["n"] += len(w); return len(w)
    legiony = lc.LegionyCieni([_cien("a")], arena_zapis=_zap)   # cykl nic nie zamyka
    legiony.krok("BTCUSDT", [{"close": 1}])
    assert zapisano["n"] == 0                   # brak zamknięć → zero wywołań zapisu


def test_awaria_cienia_nie_zabija_reszty():
    """Cień, którego cykl rzuca, nie blokuje pomiaru pozostałych (graceful, Prawo XV)."""
    zebrane = []
    legiony = lc.LegionyCieni(
        [_cien("pada", pada=True), _cien("zdrowy", pnl_na_cykl=[3.0])],
        arena_zapis=lambda w: zebrane.extend(w) or len(w),
    )
    wynik = legiony.krok("BTCUSDT", [{"close": 1}])
    assert wynik["pada"]["weszedl"] is False    # padł — nie wszedł, ale nie wywalił kroku
    assert wynik["zdrowy"]["nowe_zamkniecia"] == 1
    assert len(zebrane) == 1 and zebrane[0][1] == "zdrowy"


def test_awaria_zapisu_areny_nie_wywala():
    def _pada(w):
        raise RuntimeError("baza padła")
    legiony = lc.LegionyCieni([_cien("a", pnl_na_cykl=[1.0])], arena_zapis=_pada)
    # nie może rzucić — pętla live musi przeżyć awarię bazy areny
    legiony.krok("BTCUSDT", [{"close": 1}])


# ─── raport ──────────────────────────────────────────────────────────────────

def test_raport_agreguje_pnl():
    c = _cien("a", pnl_na_cykl=[2.0, -1.0])
    legiony = lc.LegionyCieni([c], arena_zapis=lambda w: len(w))
    legiony.krok("BTCUSDT", [{"close": 1}])
    legiony.krok("BTCUSDT", [{"close": 2}])
    r = legiony.raport()[0]
    assert r["trades"] == 2
    assert r["pnl_pct_suma"] == 1.0 and r["pnl_pct_srednia"] == 0.5


def test_raport_pusty_cien():
    legiony = lc.LegionyCieni([_cien("a")], arena_zapis=lambda w: len(w))
    r = legiony.raport()[0]
    assert r["trades"] == 0 and r["pnl_pct_srednia"] == 0.0


# ─── Fabryka produkcyjna ─────────────────────────────────────────────────────

def test_fabryka_buduje_trzy_cienie():
    legiony = lc.zbuduj_cienie_paper(["BTCUSDT"], bazowy_prog=0.55)
    assert len(legiony.cienie) == 3
    nazwy = {c.nazwa for c in legiony.cienie}
    assert nazwy == {"bez_wet", "prog_lagodny", "prog_surowy"}


def test_fabryka_progi_i_bezpieczniki():
    legiony = lc.zbuduj_cienie_paper(["BTCUSDT"], bazowy_prog=0.55, bazowy_breaker=True)
    cienie = {c.nazwa: c for c in legiony.cienie}
    # progi
    assert cienie["prog_lagodny"].dyrygent.min_pewnosc == 0.45
    assert cienie["prog_surowy"].dyrygent.min_pewnosc == 0.65
    # bez_wet: breaker OFF (Dyrygent konwertuje bool→obiekt, None gdy wyłączony);
    # wariant progowy dziedziczy realny breaker ON (obiekt bezpiecznika)
    assert cienie["bez_wet"].dyrygent.breaker_krzywej is None
    assert cienie["prog_surowy"].dyrygent.breaker_krzywej is not None
