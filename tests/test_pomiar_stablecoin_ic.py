"""Testy AERARIUM (pomiar IC stablecoinów) — logika bez sieci (Prawo XXI + Reguła Test-Granic).

Nie pobiera z DefiLlama — testuje czystą logikę: konwersję dni (ms vs s), kauzalny
forward-fill delty (None gdy brak historii), próg MIN_PAR, stały sygnał → None.
"""
from narzedzia import pomiar_stablecoin_ic as ps


def test_dzien_ms_i_sekundy():
    # ten sam moment jako sekundy i milisekundy → ten sam dzień
    assert ps._dzien(1704067200) == ps._dzien(1704067200000) == "2024-01-01"


def test_sygnal_delta_kauzalny_i_none_gdy_brak():
    # supply rośnie 100→110 (dzień do dnia); delta1d w drugim dniu = +10%
    supply = {"2024-01-01": 100.0, "2024-01-02": 110.0, "2024-01-03": 110.0}
    dni = ["2024-01-01", "2024-01-02", "2024-01-03"]
    sig = ps._sygnal_delta(dni, supply, delta_dni=1)
    assert sig[0] is None                       # brak dnia -1 (przed historią) → None
    assert abs(sig[1] - 0.10) < 1e-9            # 110/100-1
    assert abs(sig[2] - 0.0) < 1e-9             # 110/110-1


def test_ic_za_malo_par_none():
    sig = [0.01 * i for i in range(20)]
    zwr = [0.01 * i for i in range(20)]
    ic, n = ps._ic(sig, zwr, krok=1)
    assert ic is None and n < ps.MIN_PAR


def test_ic_staly_sygnal_none():
    # zero wariancji → None (nie fałszywy IC)
    sig = [0.05] * 100
    zwr = [float(i % 5) for i in range(100)]
    ic, n = ps._ic(sig, zwr, krok=1)
    assert ic is None


def test_ic_dodatnia_korelacja_wykrywana():
    sig = [float(i) for i in range(60)]
    zwr = [float(i) for i in range(60)]
    ic, n = ps._ic(sig, zwr, krok=1)
    assert ic is not None and ic > 0.99 and n == 60


def test_stale_sensowne():
    assert ps.PROG_SKILL == 0.03 and ps.MIN_PAR >= 30
    assert ps.URL_STABLECOINS.startswith("https://")
