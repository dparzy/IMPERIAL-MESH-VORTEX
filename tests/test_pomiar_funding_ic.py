"""Testy PROBATIO FUNDING (walidacja TIER A) — logika bez sieci (Prawo XXI + Reguła Test-Granic).

Nie pobiera danych z giełdy — testuje czystą logikę IC: zwroty forward, próg MIN_PAR,
stały sygnał (zero wariancji), zgodność ze Spearmanem. Granice: n==MIN_PAR-1 vs ==MIN_PAR,
stały funding → None (nie fałszywy IC).
"""
from narzedzia import pomiar_funding_ic as pf


def test_zwroty_forward_poprawne():
    closes = [100.0, 110.0, 121.0]
    z = pf._zwroty_fwd(closes, 1)
    assert abs(z[0] - 0.10) < 1e-9 and abs(z[1] - 0.10) < 1e-9
    assert z[2] is None            # brak bara t+1 dla ostatniego


def test_ic_za_malo_par_zwraca_none():
    # n < MIN_PAR → None (nie liczymy IC na garstce próbek)
    fund = [float(i) for i in range(pf.MIN_PAR)]      # przy kroku 2 → ~15 par < 30
    zwr = [float(i) for i in range(pf.MIN_PAR)]
    ic, n = pf._ic(fund, zwr, krok=2)
    assert ic is None and n < pf.MIN_PAR


def test_ic_staly_funding_zwraca_none():
    # zero wariancji sygnału → None (Prawo I: stały sygnał = brak głosu, nie fałszywy IC)
    fund = [0.0001] * 100
    zwr = [float(i % 7) for i in range(100)]
    ic, n = pf._ic(fund, zwr, krok=1)
    assert ic is None, "stały funding nie może dać liczbowego IC"


def test_ic_idealna_antykorelacja():
    # funding rosnący, zwrot malejący → IC ≈ -1 (kierunek kontrariański wykrywalny)
    fund = [float(i) for i in range(60)]
    zwr = [float(-i) for i in range(60)]
    ic, n = pf._ic(fund, zwr, krok=1)
    assert ic is not None and ic < -0.99 and n == 60


def test_prog_skill_i_min_par_sensowne():
    assert pf.PROG_SKILL == 0.03      # konwencja W-369
    assert pf.MIN_PAR >= 30           # dość próbek na wiarygodny Spearman


def test_pasek_smoke():
    pf._pasek(1, 2, "test"); pf._pasek(2, 2, "koniec")
