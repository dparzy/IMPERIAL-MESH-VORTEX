"""Testy Filtra Asymetrii Reżimu (W-314) — granice ADX, kontr-trend, abstynencja."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.pretorianie.filtr_asymetrii import FiltrAsymetriiRezimu


def _w(close, ema, adx):
    return {"CLOSE": close, "EMA_200": ema, "ADX_14": adx}


# ─── Abstynencja (Prawo XV) ────────────────────────────────────────────────────

def test_brak_danych_przepuszcza():
    f = FiltrAsymetriiRezimu()
    assert f.ocen("LONG", 0.30, {}).dozwolone
    assert f.ocen("LONG", 0.30, {"CLOSE": 100}).dozwolone           # brak EMA/ADX
    assert f.ocen("LONG", 0.30, {"CLOSE": 100, "EMA_200": 90}).dozwolone  # brak ADX


def test_brak_danych_trend_oznaczony_brak():
    f = FiltrAsymetriiRezimu()
    w = f.ocen("LONG", 0.30, {})
    assert w.trend == "BRAK"
    assert w.adx == 0.0


# ─── Zgodne z trendem przechodzi ───────────────────────────────────────────────

def test_long_zgodny_z_trendem_silnym_przechodzi():
    f = FiltrAsymetriiRezimu()
    # CLOSE>EMA → UP, LONG zgodny, ADX silny → przepuść nawet przy niskiej pewności
    w = f.ocen("LONG", 0.40, _w(110, 100, 30))
    assert w.dozwolone
    assert w.trend == "UP"
    assert not w.kontr_trend


def test_short_zgodny_z_trendem_spadkowym_przechodzi():
    f = FiltrAsymetriiRezimu()
    w = f.ocen("SHORT", 0.40, _w(90, 100, 30))   # DOWN, SHORT zgodny
    assert w.dozwolone
    assert w.trend == "DOWN"


# ─── Kontr-trend przy silnym ADX ───────────────────────────────────────────────

def test_kontr_trend_slaba_pewnosc_weto():
    f = FiltrAsymetriiRezimu()
    # UP trend silny (ADX 30), SHORT = kontr-trend, pewność < prog_kontr (0.65)
    w = f.ocen("SHORT", 0.60, _w(110, 100, 30))
    assert not w.dozwolone
    assert w.kontr_trend
    assert w.prog_wymagany == 0.65


def test_kontr_trend_silna_pewnosc_przechodzi():
    f = FiltrAsymetriiRezimu()
    w = f.ocen("SHORT", 0.70, _w(110, 100, 30))   # kontr ale pewność ≥ 0.65
    assert w.dozwolone
    assert w.kontr_trend


def test_kontr_trend_dokladnie_prog_przechodzi():
    """Granica: pewność == prog_kontr → przechodzi (≥, nie >)."""
    f = FiltrAsymetriiRezimu()
    w = f.ocen("SHORT", 0.65, _w(110, 100, 30))
    assert w.dozwolone


# ─── Rynek boczny (ADX niski) ──────────────────────────────────────────────────

def test_rynek_boczny_slaba_pewnosc_weto():
    f = FiltrAsymetriiRezimu()
    # ADX 15 < prog_adx_range (20) → boczny; pewność < prog_range (0.70)
    w = f.ocen("LONG", 0.60, _w(110, 100, 15))
    assert not w.dozwolone
    assert w.prog_wymagany == 0.70


def test_rynek_boczny_wysoka_pewnosc_przechodzi():
    f = FiltrAsymetriiRezimu()
    w = f.ocen("LONG", 0.75, _w(110, 100, 15))
    assert w.dozwolone


def test_rynek_boczny_dokladnie_prog_przechodzi():
    """Granica: pewność == prog_range → przechodzi."""
    f = FiltrAsymetriiRezimu()
    w = f.ocen("LONG", 0.70, _w(110, 100, 15))
    assert w.dozwolone


def test_boczny_ma_priorytet_nad_kontr_trendem():
    """ADX niski → ścieżka 'boczny' (prog_range), nawet gdy sygnał kontr-trendowy."""
    f = FiltrAsymetriiRezimu()
    # ADX 15 boczny; SHORT przy CLOSE>EMA byłby kontr, ale liczy się prog_range
    w = f.ocen("SHORT", 0.66, _w(110, 100, 15))
    assert not w.dozwolone           # 0.66 < prog_range 0.70
    assert w.prog_wymagany == 0.70   # nie 0.65 (kontr)


# ─── Strefa neutralna (range..trend) ───────────────────────────────────────────

def test_strefa_neutralna_przepuszcza():
    """ADX między prog_adx_range (20) a prog_adx_trend (25) → bez kary."""
    f = FiltrAsymetriiRezimu()
    # ADX 22, kontr-trend, niska pewność — ale strefa neutralna → przepuść
    w = f.ocen("SHORT", 0.30, _w(110, 100, 22))
    assert w.dozwolone
    assert w.prog_wymagany == 0.0


def test_granica_adx_range_dokladnie():
    """ADX == prog_adx_range (20) → NIE boczny (warunek <), wchodzi w neutralną/kontr."""
    f = FiltrAsymetriiRezimu()
    # ADX dokładnie 20, zgodny z trendem → neutralna strefa, przepuść
    w = f.ocen("LONG", 0.30, _w(110, 100, 20))
    assert w.dozwolone   # nie wpadł w prog_range bo 20 nie jest < 20


def test_granica_adx_trend_dokladnie_kontr():
    """ADX == prog_adx_trend (25) + kontr-trend → próg kontr aktywny (≥)."""
    f = FiltrAsymetriiRezimu()
    w = f.ocen("SHORT", 0.50, _w(110, 100, 25))
    assert not w.dozwolone
    assert w.prog_wymagany == 0.65


# ─── Konfigurowalność progów ───────────────────────────────────────────────────

def test_progi_konfigurowalne():
    f = FiltrAsymetriiRezimu(prog_kontr=0.80, prog_range=0.85)
    assert not f.ocen("SHORT", 0.79, _w(110, 100, 30)).dozwolone
    assert f.ocen("SHORT", 0.80, _w(110, 100, 30)).dozwolone
