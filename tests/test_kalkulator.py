"""Testy Kalkulatora Lewara — likwidacja, stop-loss, bezpiecznik AOA (W-028)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.pretorianie.kalkulator_lewara import (
    KalkulatorLewara, BezpiecznikKapitalu, MAX_DRAWDOWN_STOP,
    VOL_TARGET_DEFAULT, SKALA_VOL_MIN, SKALA_VOL_MAX,
    BezpiecznikKrzywejKapitalu,
)


# ── Volatility Targeting (W-059) ─────────────────────────────────────────────

def test_vol_targeting_brak_danych_skala_1():
    """Brak vol_realized → skala 1.0 (kompatybilność wsteczna, Prawo XV)."""
    assert KalkulatorLewara.skala_vol_targeting(None) == 1.0
    assert KalkulatorLewara.skala_vol_targeting(0.0) == 1.0


def test_vol_targeting_wysoka_vol_tnie_pozycje():
    """Realized vol > target → skala < 1.0 (mniejsza pozycja w burzy)."""
    skala = KalkulatorLewara.skala_vol_targeting(1.20, vol_target=0.60)
    assert skala == 0.5, f"0.60/1.20 = 0.5, jest {skala}"


def test_vol_targeting_niska_vol_powieksza():
    """Realized vol < target → skala > 1.0 (większa pozycja w spokoju, w granicach)."""
    skala = KalkulatorLewara.skala_vol_targeting(0.40, vol_target=0.60)
    assert 1.0 < skala <= SKALA_VOL_MAX


def test_vol_targeting_przyciecie_min_max():
    """Skala przycięta do [MIN, MAX] — ekstremalna vol nie zeruje, cisza nie rozdmuchuje."""
    assert KalkulatorLewara.skala_vol_targeting(10.0, vol_target=0.60) == SKALA_VOL_MIN
    assert KalkulatorLewara.skala_vol_targeting(0.01, vol_target=0.60) == SKALA_VOL_MAX


def test_vol_targeting_wplywa_na_rozmiar_planu():
    """policz() z vol_realized faktycznie zmniejsza rozmiar vs bez (ten sam setup)."""
    kalk = KalkulatorLewara()
    bazowy = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78)
    burza = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78,
                        vol_realized=1.20, vol_target=0.60)
    assert burza.skala_vol == 0.5
    assert burza.rozmiar_usdt < bazowy.rozmiar_usdt
    assert abs(burza.rozmiar_usdt - bazowy.rozmiar_usdt * 0.5) < 0.5


def test_vol_targeting_domyslnie_neutralne_w_planie():
    """Bez vol_realized plan ma skala_vol == 1.0 (nic się nie zmienia)."""
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78)
    assert plan.skala_vol == 1.0


def test_likwidacja_long_ponizej_wejscia():
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78,
                       rezim="TREND_STRONG")
    assert plan.cena_likwidacji < plan.cena_wejscia, "Likwidacja LONG musi być poniżej wejścia"
    assert plan.stop_loss > plan.cena_likwidacji, "SL musi być powyżej likwidacji (LONG)"


def test_likwidacja_short_powyzej_wejscia():
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "SHORT", 100_000, 10, 5_000, pewnosc=0.78)
    assert plan.cena_likwidacji > plan.cena_wejscia, "Likwidacja SHORT musi być powyżej wejścia"
    assert plan.stop_loss < plan.cena_likwidacji, "SL musi być poniżej likwidacji (SHORT)"


def test_rr_minimum_2():
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78)
    assert plan.rr_ratio >= 2.0, "R:R musi być minimum 1:2"


def test_panic_blokuje():
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.9,
                       rezim="PANIC")
    assert not plan.checklist_ok, "Reżim PANIC musi blokować"


def test_slaby_sygnal_blokuje():
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.50)
    assert not plan.checklist_ok, "Pewność < 55% musi blokować"


def test_auto_dzwignia_rosnie_z_pewnoscia():
    kalk = KalkulatorLewara()
    niska = kalk.auto_dzwignia(0.60, "NORMAL")
    wysoka = kalk.auto_dzwignia(0.90, "NORMAL")
    assert wysoka > niska, "Wyższa pewność = wyższa dźwignia"


def test_auto_dzwignia_panic_minimalna():
    kalk = KalkulatorLewara()
    dz = kalk.auto_dzwignia(0.90, "PANIC")
    assert dz <= 2, "PANIC musi drastycznie ciąć dźwignię"


# ── Bezpiecznik AOA (W-028) ──

def test_bezpiecznik_nie_przepalony_przy_10pct():
    bezp = BezpiecznikKapitalu(kapital_startowy=5_000)
    bezp.aktualizuj(4_500)  # -10%
    assert not bezp.przepalony
    assert abs(bezp.drawdown - 0.10) < 0.001


def test_bezpiecznik_przepala_sie_przy_30pct():
    bezp = BezpiecznikKapitalu(kapital_startowy=5_000)
    bezp.aktualizuj(3_500)  # -30%
    assert bezp.przepalony, "30% obsunięcia MUSI przepalić bezpiecznik"


def test_bezpiecznik_blokuje_wejscie():
    kalk = KalkulatorLewara()
    bezp = BezpiecznikKapitalu(kapital_startowy=5_000)
    bezp.aktualizuj(3_400)  # -32%
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 3_400, pewnosc=0.9,
                       rezim="TREND_STRONG", bezpiecznik=bezp)
    assert not plan.checklist_ok, "Przepalony bezpiecznik musi blokować wejście"
    assert "BEZPIECZNIK" in plan.powod_veto


def test_bezpiecznik_reset():
    bezp = BezpiecznikKapitalu(kapital_startowy=5_000)
    bezp.aktualizuj(3_400)
    assert bezp.przepalony
    bezp.reset()
    assert not bezp.przepalony, "Reset musi rozbroić bezpiecznik"


def test_bezpiecznik_aktualizuje_szczyt():
    bezp = BezpiecznikKapitalu(kapital_startowy=5_000)
    bezp.aktualizuj(7_000)  # zysk — nowy szczyt
    assert bezp.kapital_szczyt == 7_000
    bezp.aktualizuj(5_500)  # spadek od szczytu 7000 = -21%
    assert not bezp.przepalony, "21% od szczytu jeszcze nie przepala"
    assert abs(bezp.drawdown - 0.214) < 0.01


# ── Equity-Curve Circuit Breaker (W-062) ──

def test_breaker_krzywej_normal_pelna_frakcja():
    br = BezpiecznikKrzywejKapitalu()
    br.aktualizuj(10_000)  # świeży szczyt, zero DD
    assert br.stan == "NORMAL"
    assert br.frakcja_pozycji() == 1.0
    assert not br.halt


def test_breaker_krzywej_reduced_polowa():
    # Krzywa rosnąca → szczyt, potem łagodny spadek poniżej MA ale DD < 20%.
    br = BezpiecznikKrzywejKapitalu(okno_ma=5)
    for k in (10_000, 10_200, 10_400, 10_600, 10_800):
        br.aktualizuj(k)        # napełnij okno MA, szczyt 10_800
    br.aktualizuj(10_100)       # poniżej MA (~10_420), DD ~6.5% < 10% i < 20%
    assert br.ma_kapitalu is not None
    assert br.stan == "REDUCED", "kapitał < MA powinien dać REDUCED"
    assert br.frakcja_pozycji() == 0.5
    assert not br.halt


def test_breaker_krzywej_halt_blokuje():
    br = BezpiecznikKrzywejKapitalu()
    br.aktualizuj(10_000)
    br.aktualizuj(7_900)        # -21% od szczytu ≥ 20%
    assert br.stan == "HALT"
    assert br.halt
    assert br.frakcja_pozycji() == 0.0


def test_breaker_krzywej_powrot_do_normal():
    br = BezpiecznikKrzywejKapitalu(okno_ma=3)
    br.aktualizuj(10_000)
    br.aktualizuj(9_300)        # -7% < 10%, ale brak pełnego okna MA → NORMAL
    br.aktualizuj(9_000)        # okno=3 pełne, MA≈9433, kapitał<MA → REDUCED
    assert br.stan == "REDUCED"
    br.aktualizuj(11_000)       # nowy szczyt, kapitał > MA, DD=0 → NORMAL
    assert br.stan == "NORMAL"
    assert br.frakcja_pozycji() == 1.0


def test_breaker_krzywej_histereza_halt():
    br = BezpiecznikKrzywejKapitalu()
    br.aktualizuj(10_000)
    br.aktualizuj(7_900)        # -21% → HALT
    assert br.stan == "HALT"
    br.aktualizuj(8_700)        # -13% (≥10% reduced, <20% halt) → histereza trzyma HALT
    assert br.stan == "HALT", "histereza: nie wychodź z HALT póki DD ≥ prog_dd_reduced"
    br.aktualizuj(9_100)        # -9% < 10% → dopiero teraz wyjście z HALT
    assert br.stan != "HALT"


def test_breaker_krzywej_w_checklist_blokuje():
    kalk = KalkulatorLewara()
    br = BezpiecznikKrzywejKapitalu()
    br.aktualizuj(10_000)
    br.aktualizuj(7_900)        # HALT
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 7_900, pewnosc=0.9,
                       rezim="TREND_STRONG", breaker_krzywej=br)
    assert not plan.checklist_ok, "HALT breakera musi blokować wejście"
    assert "BREAKER KRZYWEJ" in plan.powod_veto


def test_breaker_krzywej_reduced_zmniejsza_rozmiar():
    kalk = KalkulatorLewara()
    plan_normal = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 10_000,
                              pewnosc=0.9, rezim="TREND_STRONG")
    br = BezpiecznikKrzywejKapitalu(okno_ma=5)
    for k in (10_000, 10_200, 10_400, 10_600, 10_800):
        br.aktualizuj(k)
    br.aktualizuj(10_100)       # REDUCED
    assert br.stan == "REDUCED"
    plan_reduced = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 10_000,
                               pewnosc=0.9, rezim="TREND_STRONG", breaker_krzywej=br)
    assert plan_reduced.frakcja_breaker == 0.5
    assert abs(plan_reduced.rozmiar_usdt - plan_normal.rozmiar_usdt * 0.5) < 1.0
