"""Testy Kalkulatora Lewara — likwidacja, stop-loss, bezpiecznik AOA (W-028)."""

import sys, os
from datetime import date as _date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date

from imperium.pretorianie.kalkulator_lewara import (
    KalkulatorLewara, BezpiecznikKapitalu, MAX_DRAWDOWN_STOP,
    VOL_TARGET_DEFAULT, SKALA_VOL_MIN, SKALA_VOL_MAX,
    BezpiecznikKrzywejKapitalu, SkalowanieFrakcjaDD,
    RegulaSzesciuProcentEldera,
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


# ── Volatility Drag (W-130, Sinclair rozdz. 13) ──────────────────────────────

def test_drag_brak_danych_none():
    """Brak vol_realized → drag None (kompatybilność wsteczna, Prawo XV)."""
    assert KalkulatorLewara.volatility_drag(10, None) is None
    assert KalkulatorLewara.volatility_drag(10, 0.0) is None


def test_drag_lewar_1_zero():
    """λ=1 → brak erozji (½·1·0·σ² = 0)."""
    assert KalkulatorLewara.volatility_drag(1, 0.80) == 0.0


def test_drag_wzor_polowa_lambda():
    """½·λ·(λ−1)·σ²: λ=3, σ=1.0 → 3.0 (300%/rok, przykład z analizy)."""
    assert KalkulatorLewara.volatility_drag(3, 1.0) == 3.0
    # λ=2, σ=0.6 → ½·2·1·0.36 = 0.36
    assert abs(KalkulatorLewara.volatility_drag(2, 0.6) - 0.36) < 1e-9


def test_drag_rosnie_z_lewarem():
    """Drag rośnie super-liniowo z dźwignią przy tej samej vol."""
    d2 = KalkulatorLewara.volatility_drag(2, 0.8)
    d5 = KalkulatorLewara.volatility_drag(5, 0.8)
    assert d5 > d2 * 3  # ½·5·4=10 vs ½·2·1=1 → 10×


def test_drag_raportowany_w_planie():
    """policz() z vol_realized wypełnia drag_roczny w planie."""
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78,
                       vol_realized=0.60)
    # ½·10·9·0.36 = 16.2
    assert plan.drag_roczny is not None
    assert abs(plan.drag_roczny - 16.2) < 0.01


def test_drag_domyslnie_none_w_planie():
    """Bez vol_realized plan ma drag_roczny None (nic się nie zmienia)."""
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78)
    assert plan.drag_roczny is None


def test_drag_weto_tylko_z_limitem():
    """Weto na drag działa TYLKO gdy max_drag_roczny jawnie ustawiony."""
    kalk = KalkulatorLewara()
    # Bez limitu: wysoki drag NIE blokuje (kompatybilność wsteczna)
    bez = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78,
                      rezim="TREND_STRONG", vol_realized=0.60)
    assert bez.checklist_ok, "bez limitu drag nie może blokować"
    # Z limitem 0.30: drag 16.2 >> 0.30 → weto
    z_lim = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 5_000, pewnosc=0.78,
                        rezim="TREND_STRONG", vol_realized=0.60, max_drag_roczny=0.30)
    assert not z_lim.checklist_ok
    assert "DRAG" in z_lim.powod_veto


def test_drag_weto_przepuszcza_niski():
    """Niski drag (mały lewar + spokój) przechodzi mimo ustawionego limitu."""
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 2, 5_000, pewnosc=0.78,
                       rezim="TREND_STRONG", vol_realized=0.30, max_drag_roczny=0.30)
    # ½·2·1·0.09 = 0.09 < 0.30 → przechodzi
    assert plan.drag_roczny is not None and plan.drag_roczny < 0.30
    assert plan.checklist_ok


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


# ── Drawdown-Fractional Sizing (W-063, Maier-Paape) ──────────────────────────

def test_frakcja_dd_brak_drawdownu_frakcja_1():
    """DD=0 → frakcja = 1.0 (pełny rozmiar)."""
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)
    assert sd.frakcja() == 1.0


def test_frakcja_dd_polowa_prog_max():
    """DD=10% przy prog_max=20% → frakcja = 0.5."""
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)   # szczyt
    sd.aktualizuj(9_000)    # DD = 10%
    assert abs(sd.frakcja() - 0.5) < 0.01


def test_frakcja_dd_osiaga_min():
    """DD >= prog_max → frakcja = min_frakcja (podłoga)."""
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)
    sd.aktualizuj(7_500)    # DD = 25% > prog_max(20%)
    assert sd.frakcja() == sd.min_frakcja


def test_frakcja_dd_nie_przekracza_1():
    """Kapitał rośnie → frakcja nigdy > 1.0."""
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)
    sd.aktualizuj(12_000)   # nowy szczyt — DD=0
    assert sd.frakcja() == 1.0


def test_frakcja_dd_plynna_redukcja():
    """Frakcja maleje monotonicznie z rosnącym DD."""
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)
    frakcje = []
    for kapital in [10_000, 9_500, 9_000, 8_500, 8_000, 7_500]:
        sd.aktualizuj(kapital)
        frakcje.append(sd.frakcja())
    for i in range(len(frakcje) - 1):
        assert frakcje[i] >= frakcje[i + 1], (
            f"Frakcja powinna maleć: {frakcje[i]} >= {frakcje[i+1]}")


def test_frakcja_dd_wplywa_na_rozmiar():
    """skalowanie_dd redukuje rozmiar pozycji proportjonalnie do DD."""
    kalk = KalkulatorLewara()
    # Plan bez DD
    plan_normalny = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 10_000,
                                pewnosc=0.9, rezim="TREND_STRONG")
    # Plan z DD=10% (frakcja ≈ 0.5 dla prog_max=0.20)
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)
    sd.aktualizuj(9_000)    # DD=10% → frakcja≈0.5
    plan_dd = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 10_000,
                           pewnosc=0.9, rezim="TREND_STRONG", skalowanie_dd=sd)
    assert plan_dd.frakcja_dd < 1.0
    assert plan_dd.rozmiar_usdt < plan_normalny.rozmiar_usdt


def test_frakcja_dd_domyslnie_1_w_planie():
    """Brak skalowania_dd → frakcja_dd=1.0 w planie (kompatybilność wsteczna)."""
    kalk = KalkulatorLewara()
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 10_000,
                       pewnosc=0.9, rezim="TREND_STRONG")
    assert plan.frakcja_dd == 1.0


def test_frakcja_dd_reset():
    """Reset FrakcjaDD: nowy szczyt = bieżący kapitał, frakcja = 1.0."""
    sd = SkalowanieFrakcjaDD(prog_max=0.20, min_frakcja=0.10)
    sd.aktualizuj(10_000)
    sd.aktualizuj(8_000)    # DD=20% → min
    assert sd.frakcja() == sd.min_frakcja
    sd.reset()
    assert sd.frakcja() == 1.0


# ── Reguła 6% Eldera (BIB-015) ───────────────────────────────────────────────

def test_regula_6pct_normal_ponizej_progu():
    """Strata 3% tego miesiąca → stan NORMAL (poniżej progu 6%)."""
    reg = RegulaSzesciuProcentEldera()
    reg.reset_miesiac(10_000)
    reg.aktualizuj(9_700, dzisiaj=date(2026, 6, 9))
    assert reg.stan == "NORMAL"
    assert not reg.halt


def test_regula_6pct_halt_po_przekroczeniu():
    """Strata 7% tego miesiąca → stan HALT (powyżej progu 6%)."""
    reg = RegulaSzesciuProcentEldera()
    reg.reset_miesiac(10_000)
    reg.aktualizuj(9_300, dzisiaj=date(2026, 6, 9))
    assert reg.stan == "HALT"
    assert reg.halt


def test_regula_6pct_reset_nowy_miesiac():
    """Po zmianie miesiąca stan wraca do NORMAL i liczy od nowego kapitału."""
    reg = RegulaSzesciuProcentEldera()
    reg.reset_miesiac(10_000)
    reg.aktualizuj(9_300, dzisiaj=date(2026, 6, 30))
    assert reg.halt
    reg.aktualizuj(9_300, dzisiaj=date(2026, 7, 1))
    assert reg.stan == "NORMAL", "Nowy miesiąc musi resetować HALT"


def test_regula_6pct_weto_w_planie():
    """Gdy Reguła 6% HALT, policz() zwraca checklist_ok=False z odpowiednim powodem."""
    kalk = KalkulatorLewara()
    reg = RegulaSzesciuProcentEldera()
    reg.reset_miesiac(10_000)
    reg.aktualizuj(9_300, dzisiaj=date(2026, 6, 9))
    assert reg.halt
    plan = kalk.policz("BTCUSDT", "LONG", 100_000, 10, 9_300,
                       pewnosc=0.9, rezim="TREND_STRONG", regula_6pct=reg)
    assert not plan.checklist_ok
    assert "Elder" in plan.powod_veto or "6%" in plan.powod_veto


# ── Skew-Kelly (W-211, Sinclair BIB-018) ─────────────────────────────────────

def test_skew_kelly_symetria_rowna_klasycznemu():
    """Skos = 0 → f* = μ/σ² (klasyczne Kelly, zero zmian)."""
    f = KalkulatorLewara.skew_kelly(0.10, 0.20, 0.0)
    assert abs(f - 0.10 / 0.04) < 1e-6


def test_skew_kelly_ujemny_skos_tnie_pozycje():
    """Ujemny skos (gruby lewy ogon) → f* < klasyczne Kelly."""
    klasyczne = 0.10 / 0.04
    f = KalkulatorLewara.skew_kelly(0.10, 0.20, -1.0)
    assert f < klasyczne, "ujemny skos musi zmniejszyć frakcję Kelly"
    assert f > 0


def test_skew_kelly_dodatni_skos_nie_zawysza():
    """Dodatni skos → wracamy do klasycznego Kelly (nie zawyżamy zakładu)."""
    f = KalkulatorLewara.skew_kelly(0.10, 0.20, 1.0)
    assert abs(f - 0.10 / 0.04) < 1e-6


def test_skew_kelly_brak_danych_none():
    """Brak μ/σ lub niedodatnie → None (Prawo XV, bez halucynacji)."""
    assert KalkulatorLewara.skew_kelly(None, 0.2, -1.0) is None
    assert KalkulatorLewara.skew_kelly(0.10, None, -1.0) is None
    assert KalkulatorLewara.skew_kelly(0.0, 0.2, -1.0) is None
    assert KalkulatorLewara.skew_kelly(0.10, 0.0, -1.0) is None


def test_skew_kelly_silniejszy_skos_mocniej_tnie():
    """Im bardziej ujemny skos, tym mniejsza frakcja (monotonicznie)."""
    f_slaby = KalkulatorLewara.skew_kelly(0.10, 0.20, -0.5)
    f_silny = KalkulatorLewara.skew_kelly(0.10, 0.20, -2.0)
    assert f_silny < f_slaby, "silniejszy ujemny skos = ostrożniejszy sizing"
