"""Testy PAVOR (pomiar IC DVOL) — logika bez sieci (Prawo XXI + Reguła Test-Granic)."""
from narzedzia import pomiar_dvol_ic as pd


def test_dzien_ms_i_s():
    assert pd._dzien(1704067200) == pd._dzien(1704067200000) == "2024-01-01"


def test_wyrownaj_kauzalny():
    seria = {"2024-01-01": 40.0, "2024-01-03": 45.0}
    w = pd._wyrownaj(["2024-01-02", "2024-01-03"], seria)
    assert w("2024-01-02") == 40.0        # bierze ostatni ≤ dzień (01, nie 03)
    assert w("2024-01-03") == 45.0
    assert w("2023-12-31") is None        # przed historią → None


def test_ic_granice():
    assert pd._ic([0.1] * 20, [0.1] * 20, 1)[0] is None            # n<MIN_PAR
    assert pd._ic([5.0] * 100, [float(i) for i in range(100)], 1)[0] is None  # stały → None
    ic, n = pd._ic([float(i) for i in range(60)], [float(i) for i in range(60)], 1)
    assert ic is not None and ic > 0.99 and n == 60


def test_stale():
    assert pd.PROG_SKILL == 0.03 and pd.MIN_PAR >= 30
    assert pd.URL_DVOL.startswith("https://") and pd.DELTA_DNI == 7
