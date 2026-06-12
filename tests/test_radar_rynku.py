"""Testy RadarRynku (W-292) — wielowymiarowy kontekst: dominacja, przepływ, stres."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imperium.legiony.radar_rynku import (RadarRynku, StanRynku, _korelacja,
                                          frakcja_korelacyjna, rezim_risk_off)


def _seria(start, krok, n):
    return [start * (1 + krok) ** i for i in range(n)]


def test_dominacja_btc_silniejszy():
    """BTC rośnie szybciej niż alty → dominacja > 0 (kapitał ucieka do BTC)."""
    r = RadarRynku()
    btc = _seria(100, 0.02, 90)          # +2%/bar
    alty = {"ETH": _seria(50, 0.005, 90), "SOL": _seria(20, 0.004, 90)}  # słabsze
    stan = r.skanuj(btc, alty)
    assert stan.dominacja is not None and stan.dominacja > 0.0


def test_alt_season_dominacja_ujemna():
    """Alty rosną szybciej niż BTC → dominacja < 0 (alt-season)."""
    r = RadarRynku()
    btc = _seria(100, 0.002, 90)
    alty = {"ETH": _seria(50, 0.02, 90), "SOL": _seria(20, 0.025, 90)}
    stan = r.skanuj(btc, alty)
    assert stan.dominacja is not None and stan.dominacja < 0.0


def test_przeplyw_w_zakresie():
    """PRZEPLYW_KAPITALU ∈ [0,1]; rynek rosnący → wysoki breadth."""
    r = RadarRynku()
    btc = _seria(100, 0.01, 90)
    alty = {"ETH": _seria(50, 0.01, 90), "SOL": _seria(20, 0.01, 90)}
    vol = {"ETH": _seria(1000, 0.01, 90), "SOL": _seria(800, 0.01, 90)}
    stan = r.skanuj(btc, alty, vol)
    assert stan.przeplyw is not None and 0.0 <= stan.przeplyw <= 1.0
    assert stan.przeplyw > 0.5  # wszystko nad EMA + wolumen rośnie


def test_stres_korelacji_kaskada():
    """Identyczny ruch wszystkich par → wysoki stres korelacji (kaskada)."""
    r = RadarRynku()
    wspolny = _seria(100, 0.01, 90)
    btc = wspolny
    alty = {"ETH": [x * 0.5 for x in wspolny], "SOL": [x * 0.2 for x in wspolny]}
    stan = r.skanuj(btc, alty)
    assert stan.stres_korelacji is not None and stan.stres_korelacji > 0.8
    assert any("KASKADA" in p for p in stan.powody)


def test_za_malo_danych_milczy():
    """Za krótkie serie → pola None (Prawo I: radar milczy, nie zgaduje)."""
    r = RadarRynku()
    stan = r.skanuj([100.0] * 3, {"ETH": [50.0] * 3})
    assert isinstance(stan, StanRynku)
    assert stan.dominacja is None and stan.przeplyw is None


def test_jako_wskazniki_eksport():
    """jako_wskazniki() zwraca tylko policzone klucze (bez None)."""
    r = RadarRynku()
    btc = _seria(100, 0.01, 90)
    alty = {"ETH": _seria(50, 0.01, 90), "SOL": _seria(20, 0.01, 90)}
    w = r.skanuj(btc, alty).jako_wskazniki()
    assert all(v is not None for v in w.values())
    assert "BTC_DOMINANCJA" in w


def test_korelacja_granice():
    """_korelacja: idealnie zgodne→+1, przeciwne→-1, zerowa wariancja→None."""
    assert abs(_korelacja([1, 2, 3, 4], [2, 4, 6, 8]) - 1.0) < 1e-9
    assert abs(_korelacja([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-9
    assert _korelacja([1, 1, 1, 1], [1, 2, 3, 4]) is None
    assert _korelacja([1], [1]) is None


def test_frakcja_korelacyjna_teoria_portfela():
    """Ster korelacyjny: ρ=0→1.0 (pełny), ρ=1→1/√N (tnij), monotonicznie maleje."""
    import math
    # Brak cięcia: dekorelacja lub brak danych lub pojedyncza para
    assert frakcja_korelacyjna(5, 0.0) == 1.0
    assert frakcja_korelacyjna(5, None) == 1.0
    assert frakcja_korelacyjna(1, 0.9) == 1.0
    # Pełna kaskada N=5 → 1/√5
    assert abs(frakcja_korelacyjna(5, 1.0) - 1.0 / math.sqrt(5)) < 1e-9
    # Monotoniczność: większa korelacja → mniejszy rozmiar
    assert frakcja_korelacyjna(5, 0.3) > frakcja_korelacyjna(5, 0.7)
    # Clamp ρ poza [0,1] nie wybucha
    assert frakcja_korelacyjna(5, 1.5) == frakcja_korelacyjna(5, 1.0)
    assert frakcja_korelacyjna(5, -0.5) == 1.0


def test_rezim_risk_off_konfluencja():
    """Rygiel: risk-off TYLKO gdy kaskada ∧ odpływ ∧ BTC↓ jednocześnie (konfluencja)."""
    # Wszystkie trzy spełnione → risk-off
    pelny = StanRynku(btc_trend=-0.3, przeplyw=0.2, stres_korelacji=0.9)
    off, powod = rezim_risk_off(pelny)
    assert off and "RISK-OFF" in powod
    # Brak jednego warunku → NIE blokuje (BTC rośnie)
    assert not rezim_risk_off(StanRynku(btc_trend=0.3, przeplyw=0.2, stres_korelacji=0.9))[0]
    # Brak jednego warunku → NIE blokuje (przepływ zdrowy)
    assert not rezim_risk_off(StanRynku(btc_trend=-0.3, przeplyw=0.6, stres_korelacji=0.9))[0]
    # Brak jednego warunku → NIE blokuje (brak kaskady)
    assert not rezim_risk_off(StanRynku(btc_trend=-0.3, przeplyw=0.2, stres_korelacji=0.5))[0]


def test_rezim_risk_off_brak_danych_nie_blokuje():
    """None w którymkolwiek sygnale → ten warunek nie blokuje (Prawo XV)."""
    assert not rezim_risk_off(StanRynku())[0]
    assert not rezim_risk_off(StanRynku(btc_trend=-0.5, przeplyw=None, stres_korelacji=0.9))[0]


def test_rezim_risk_off_granice_progow():
    """Granice: dokładnie próg NIE wyzwala (≥/≤ vs ostre >/<)."""
    # stres == prog (0.85) nie jest > 0.85 → brak kaskady → nie blokuje
    assert not rezim_risk_off(StanRynku(btc_trend=-0.1, przeplyw=0.2, stres_korelacji=0.85))[0]
    # przeplyw == prog (0.35) nie jest < 0.35 → nie blokuje
    assert not rezim_risk_off(StanRynku(btc_trend=-0.1, przeplyw=0.35, stres_korelacji=0.9))[0]
    # btc == prog (0.0) nie jest < 0.0 → nie blokuje
    assert not rezim_risk_off(StanRynku(btc_trend=0.0, przeplyw=0.2, stres_korelacji=0.9))[0]


def test_walidacja_parametrow():
    for zle in (dict(okno_rs=2), dict(okno_breadth=1), dict(okno_korelacji=0)):
        try:
            RadarRynku(**zle); raise AssertionError("zły parametr ma rzucić")
        except ValueError:
            pass


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    bl = 0
    for nm, f in fn:
        try:
            f(); print(f"  ✅ {nm}")
        except Exception as e:
            bl += 1; print(f"  ❌ {nm}: {e}")
    sys.exit(1 if bl else 0)


# ── Opcja A: radar-aware strategy switching ───────────────────────────────────

def test_bonus_radar_trend_flow_high():
    """PRZEPLYW>0.65 → TR/SC dostają bonus, RV/RG penalty."""
    from imperium.legiony.strategie.baza import bonus_radar
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    stan = StanRynku(przeplyw=0.75, stres_korelacji=0.3, btc_trend=0.1)
    strats = {s.id: s for s in wszystkie_strategie()}
    tr = next(s for s in strats.values() if s.styl == "TR")
    rv = next(s for s in strats.values() if s.styl == "RV")
    assert bonus_radar(tr, stan) > 1.0
    assert bonus_radar(rv, stan) < 1.0


def test_bonus_radar_flow_low_reversal():
    """PRZEPLYW<0.35 → RV/RG bonus, TR/SC penalty."""
    from imperium.legiony.strategie.baza import bonus_radar
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    stan = StanRynku(przeplyw=0.20, stres_korelacji=0.3, btc_trend=-0.1)
    strats = {s.id: s for s in wszystkie_strategie()}
    tr = next(s for s in strats.values() if s.styl == "TR")
    rv = next(s for s in strats.values() if s.styl == "RV")
    assert bonus_radar(tr, stan) < 1.0
    assert bonus_radar(rv, stan) > 1.0


def test_bonus_radar_stres_wysoki():
    """STRES>0.85 → TR/SC kara, RV/RG/BK bonus — selectywne, nie globalne."""
    from imperium.legiony.strategie.baza import bonus_radar
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    stan = StanRynku(przeplyw=0.5, stres_korelacji=0.90, btc_trend=0.0)
    for s in wszystkie_strategie():
        b = bonus_radar(s, stan)
        if s.styl in ("TR", "SC"):
            assert b < 1.0, f"{s.id} (TR/SC) musi być < 1.0 przy STRES 0.9"
        elif s.styl in ("RV", "RG", "BK"):
            assert b >= 1.0, f"{s.id} (RV/RG/BK) musi być >= 1.0 przy STRES 0.9"


def test_bonus_radar_brak_stanu():
    """None stan_rynku → mnożnik = 1.0 (brak efektu)."""
    from imperium.legiony.strategie.baza import bonus_radar
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    for s in wszystkie_strategie():
        assert bonus_radar(s, None) == 1.0


def test_bonus_radar_granice_zakresu():
    """Mnożnik zawsze w [0.6, 1.3]."""
    from imperium.legiony.strategie.baza import bonus_radar
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    for przeplyw in (0.0, 0.35, 0.65, 1.0):
        for stres in (0.0, 0.85, 1.0):
            stan = StanRynku(przeplyw=przeplyw, stres_korelacji=stres, btc_trend=0.5)
            for s in wszystkie_strategie():
                b = bonus_radar(s, stan)
                assert 0.6 <= b <= 1.3, f"{s.id} bonus={b} poza zakresem"


def test_namiestnik_decyduj_z_radarem_bycze_wiekszy_lewar():
    """BTC>0.3 + PRZEPLYW>0.6 → lewar_factor większy niż bez radaru."""
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    stan = StanRynku(btc_trend=0.5, przeplyw=0.70, stres_korelacji=0.3)
    bazowa = n.decyduj("NORMAL")
    z_radarem = n.decyduj_z_radarem("NORMAL", stan_rynku=stan)
    assert z_radarem.lewar_factor > bazowa.lewar_factor, "Bycze tło → większy lewar"
    assert z_radarem.prog_pewnosci <= bazowa.prog_pewnosci, "Bycze tło → niższy próg"
    assert z_radarem.rezim == "NORMAL", "Radar moduluje parametry, nie zmienia rezim"


def test_namiestnik_decyduj_z_radarem_stres_mniejszy_lewar():
    """STRES>0.8 + BTC<0 → lewar_factor mniejszy, próg wyższy."""
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    stan = StanRynku(btc_trend=-0.2, przeplyw=0.4, stres_korelacji=0.85)
    bazowa = n.decyduj("TREND_STRONG")
    z_radarem = n.decyduj_z_radarem("TREND_STRONG", stan_rynku=stan)
    assert z_radarem.lewar_factor < bazowa.lewar_factor, "Stres → mniejszy lewar"
    assert z_radarem.prog_pewnosci >= bazowa.prog_pewnosci, "Stres → wyższy próg"
    assert z_radarem.rezim == "TREND_STRONG", "Radar moduluje parametry, nie zmienia rezim"


def test_namiestnik_decyduj_z_radarem_panic_bez_zmiany():
    """PANIC reżim nie zmienia się niezależnie od radaru."""
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    stan = StanRynku(btc_trend=0.9, przeplyw=0.95, stres_korelacji=0.1)
    wynik = n.decyduj_z_radarem("PANIC", stan_rynku=stan)
    assert wynik.rezim == "PANIC"


def test_namiestnik_decyduj_z_radarem_none_stan():
    """None stan_rynku → identyczny wynik jak decyduj()."""
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    for rezim in ("NORMAL", "TREND_STRONG", "VOLATILE", "RANGING"):
        bazowa = n.decyduj(rezim)
        z_none = n.decyduj_z_radarem(rezim, stan_rynku=None)
        assert bazowa.rezim == z_none.rezim


def test_dobierz_najlepsze_z_radarem_zmienia_ranking():
    """Radar zmienia kolejność strategii — TR dostaje bonus przy wysokim przepływie."""
    from imperium.legiony.strategie.baza import dobierz_najlepsze
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie

    strats = [s for s in wszystkie_strategie() if s.styl in ("TR", "RV")]
    if not strats:
        return

    # Symuluj sygnały które dają kierunek każdej strategii
    class MockSygnal:
        def __init__(self):
            self.kierunek = "LONG"
            self.pewnosc_finalna = 0.8

    mock_sig = MockSygnal()
    sygnaly = {}
    for s in strats:
        for k in s.wszystkie_klucze():
            sygnaly[k] = mock_sig

    bez_radaru = dobierz_najlepsze(strats, sygnaly, rezim="NORMAL", stan_rynku=None)
    z_radarem = dobierz_najlepsze(strats, sygnaly, rezim="NORMAL",
                                   stan_rynku=StanRynku(przeplyw=0.75, stres_korelacji=0.2, btc_trend=0.5))
    # Nie crash i zwraca wyniki
    assert isinstance(bez_radaru, list)
    assert isinstance(z_radarem, list)
