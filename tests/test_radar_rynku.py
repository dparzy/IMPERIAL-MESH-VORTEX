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
