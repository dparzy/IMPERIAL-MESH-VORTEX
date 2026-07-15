"""Testy MONETA (pomiar IC siły USD) — logika bez sieci (Prawo XXI + Reguła Test-Granic)."""
from narzedzia import pomiar_usd_ic as pu


def test_dzien_ms_i_s():
    assert pu._dzien(1704067200) == pu._dzien(1704067200000) == "2024-01-01"


def test_wyrownaj_kauzalny():
    seria = {"2024-01-01": 1.0, "2024-01-05": 1.1}
    w = pu._wyrownaj(["2024-01-03", "2024-01-05"], seria)
    assert w("2024-01-03") == 1.0        # ostatni ≤ dzień (01, nie 05)
    assert w("2024-01-05") == 1.1
    assert w("2023-12-31") is None


def test_ic_granice():
    assert pu._ic([1.0] * 20, [1.0] * 20, 1)[0] is None                       # n<MIN_PAR
    assert pu._ic([2.0] * 100, [float(i) for i in range(100)], 1)[0] is None  # stały→None
    ic, n = pu._ic([float(-i) for i in range(60)], [float(i) for i in range(60)], 1)
    assert ic is not None and ic < -0.99 and n == 60                          # antykorelacja


def test_stale():
    assert pu.PROG_SKILL == 0.03 and pu.MIN_PAR >= 30
    assert pu.URL_FX.startswith("https://") and "User-Agent" in pu.UA
