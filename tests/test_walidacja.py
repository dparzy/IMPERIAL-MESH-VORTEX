"""
Testy bramki anty-overfittingu Koloseum (W-282): DSR + PBO/CSCV.
Reguła Test-Granic: zero/None/±/dokładny-próg sprawdzone jawnie.
"""

import os
import sys


import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.koloseum.walidacja import (   # noqa: E402
    deflated_sharpe, pbo_cscv, bramka_walidacji, sharpe_zerowy,
    _phi, _phi_inv, PROG_PBO,
)

RNG = np.random.default_rng(42)


# ── Φ / Φ⁻¹ ──────────────────────────────────────────────────────────────────

def test_phi_granice_i_srodek():
    assert abs(_phi(0.0) - 0.5) < 1e-12
    assert _phi(3.0) > 0.99
    assert _phi(-3.0) < 0.01


def test_phi_inv_odwraca_phi():
    for p in (0.01, 0.1, 0.5, 0.9, 0.99):
        assert abs(_phi(_phi_inv(p)) - p) < 1e-7


def test_phi_inv_granice_rzucaja():
    for p in (0.0, 1.0, -0.1, 1.1):
        try:
            _phi_inv(p)
            raise AssertionError(f"p={p} powinno rzucić ValueError")
        except ValueError:
            pass


# ── SR₀ (selection-bias poprzeczka) ──────────────────────────────────────────

def test_sr0_jedna_proba_zero():
    """n_prob=1 → brak selection bias → SR₀=0 (granica dolna)."""
    assert sharpe_zerowy(1, 0.01) == 0.0


def test_sr0_rosnie_z_liczba_prob():
    """Więcej testowanych wariantów → wyższa poprzeczka."""
    assert sharpe_zerowy(100, 0.01) > sharpe_zerowy(10, 0.01) > 0


def test_sr0_zero_wariancji():
    """Zerowa wariancja między próbami → SR₀=0 (granica)."""
    assert sharpe_zerowy(50, 0.0) == 0.0


# ── Deflated Sharpe ──────────────────────────────────────────────────────────

def test_dsr_prawdziwa_przewaga_przechodzi():
    """Wyraźny edge (μ=0.2%, σ=1%) na 500 barach, 1 próba → DSR wysoki."""
    z = RNG.normal(0.002, 0.01, 500)
    w = deflated_sharpe(z, n_prob=1)
    assert w["dsr"] > 0.95 and w["ok"]


def test_dsr_szum_nie_przechodzi():
    """Czysty szum (μ=0) → DSR ~0.5, nie przechodzi."""
    z = RNG.normal(0.0, 0.01, 500)
    w = deflated_sharpe(z, n_prob=1)
    assert not w["ok"]


def test_dsr_selection_bias_obniza():
    """Ten sam zwycięzca, ale przy 100 próbach → DSR niższy niż przy 1."""
    z = RNG.normal(0.001, 0.01, 300)
    d1 = deflated_sharpe(z, n_prob=1)["dsr"]
    d100 = deflated_sharpe(z, n_prob=100)["dsr"]
    assert d100 < d1, "korekta o liczbę prób musi obniżać pewność"


def test_dsr_za_malo_obserwacji():
    """Granica długości: <10 obserwacji → odrzucone z powodem."""
    w = deflated_sharpe([0.01] * 5)
    assert not w["ok"] and "za mało" in w["powod"]


def test_dsr_zerowa_wariancja():
    """Stały zwrot (σ=0) → martwa strategia, odrzucona (granica)."""
    w = deflated_sharpe([0.01] * 50)
    assert not w["ok"] and "wariancja" in w["powod"]


# ── PBO / CSCV ───────────────────────────────────────────────────────────────

def test_pbo_szum_wysoki():
    """N strategii czystego szumu → wybór najlepszego IS nic nie mówi → PBO duże."""
    m = RNG.normal(0.0, 0.01, (240, 20))
    w = pbo_cscv(m, s_blokow=8)
    assert w["pbo"] is not None and w["pbo"] > PROG_PBO and not w["ok"]


def test_pbo_prawdziwy_edge_niski():
    """Jedna strategia z realnym edge wśród szumu → PBO niskie (zwycięzca trwały)."""
    m = RNG.normal(0.0, 0.01, (240, 10))
    m[:, 3] += 0.004  # wyraźna przewaga kolumny 3
    w = pbo_cscv(m, s_blokow=8)
    assert w["pbo"] is not None and w["pbo"] < PROG_PBO and w["ok"]


def test_pbo_liczba_podzialow():
    """C(8,4)=70 podziałów dla S=8."""
    m = RNG.normal(0.0, 0.01, (160, 5))
    w = pbo_cscv(m, s_blokow=8)
    assert w["n_podzialow"] == 70


def test_pbo_granice_wejscia():
    """Granice: 1 strategia → odrzucone; S nieparzyste → ValueError; za krótko → powód."""
    m1 = RNG.normal(0.0, 0.01, (100, 1))
    assert not pbo_cscv(m1, s_blokow=8)["ok"]
    try:
        pbo_cscv(RNG.normal(0, 1, (100, 3)), s_blokow=7)
        raise AssertionError("S nieparzyste powinno rzucić")
    except ValueError:
        pass
    w = pbo_cscv(RNG.normal(0, 1, (10, 3)), s_blokow=8)
    assert not w["ok"] and "za mało" in w["powod"]


def test_pbo_martwa_kolumna_nie_wybucha():
    """Strategia o zerowej wariancji (martwa) nie psuje procedury (granica σ=0)."""
    m = RNG.normal(0.0, 0.01, (160, 4))
    m[:, 0] = 0.0
    w = pbo_cscv(m, s_blokow=8)
    assert w["pbo"] is not None and 0.0 <= w["pbo"] <= 1.0


# ── Bramka łączna ────────────────────────────────────────────────────────────

def test_bramka_edge_przechodzi_szum_nie():
    m = RNG.normal(0.0, 0.01, (240, 10))
    m[:, 0] += 0.004
    ok = bramka_walidacji(m[:, 0], macierz_wszystkich=m, s_blokow=8)
    assert ok["ok"], f"realny edge powinien przejść: {ok}"
    szum = bramka_walidacji(m[:, 1], macierz_wszystkich=m, s_blokow=8)
    assert not szum["ok"], "szum nie może przejść bramki"
    assert szum["powod"], "odrzucenie zawsze z czytelnym powodem (Prawo I)"


def test_bramka_bez_macierzy_tylko_dsr():
    z = RNG.normal(0.002, 0.01, 500)
    w = bramka_walidacji(z, n_prob=1)
    assert w["pbo"] is None and w["ok"]


def test_bramka_n_prob_z_macierzy():
    """n_prob domyślnie = liczba kolumn macierzy (uczciwa korekta)."""
    m = RNG.normal(0.0, 0.01, (240, 50))
    w = bramka_walidacji(m[:, 0], macierz_wszystkich=m, s_blokow=8)
    # przy 50 próbach szumu DSR musi być niski
    assert not w["ok"]


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items())
          if k.startswith("test_") and callable(v)]
    bledy = 0
    for nazwa, f in fn:
        try:
            f()
            print(f"  ✅ {nazwa}")
        except Exception as e:
            bledy += 1
            print(f"  ❌ {nazwa}: {e}")
    print(f"\n{len(fn)-bledy}/{len(fn)} zaliczone")
    sys.exit(1 if bledy else 0)


# ── W-285.2: Dwu-zegarowy DSR (bary wolumenowe, trading-time) ────────────────

from imperium.koloseum.walidacja import (  # noqa: E402
    bary_wolumenowe, zwroty_z_barow, bramka_dwuzegarowa,
)


def _bary_syntetyczne(n=400, seed=5):
    rng = np.random.default_rng(seed)
    cena = 100.0
    bary = []
    for i in range(n):
        ret = rng.normal(0.001, 0.01)
        o = cena
        cena = cena * (1 + ret)
        bary.append({"open": o, "high": max(o, cena) * 1.001,
                     "low": min(o, cena) * 0.999, "close": cena,
                     "volume": float(rng.uniform(50, 150))})
    return bary


def test_bary_wolumenowe_rowny_wolumen():
    """Każdy bar wolumenowy (poza odrzuconą końcówką) ma volume ≥ próg."""
    bary = _bary_syntetyczne()
    vb = bary_wolumenowe(bary, wolumen_na_bar=500.0)
    assert len(vb) > 10
    assert all(b["volume"] >= 500.0 for b in vb)


def test_bary_wolumenowe_high_low_spojne():
    """High ≥ open/close ≥ low w każdym barze zagregowanym."""
    vb = bary_wolumenowe(_bary_syntetyczne(), wolumen_na_bar=400.0)
    for b in vb:
        assert b["high"] >= max(b["open"], b["close"]) - 1e-9
        assert b["low"] <= min(b["open"], b["close"]) + 1e-9


def test_bary_wolumenowe_granice():
    """Granice: pusta lista → []; zerowy wolumen → []; próg ≤ 0 → ValueError."""
    assert bary_wolumenowe([]) == []
    zero = [{"open": 1, "high": 1, "low": 1, "close": 1, "volume": 0.0}] * 5
    assert bary_wolumenowe(zero) == []
    try:
        bary_wolumenowe(_bary_syntetyczne(10), wolumen_na_bar=0.0)
        raise AssertionError("próg 0 powinien rzucić")
    except ValueError:
        pass


def test_bary_wolumenowe_auto_prog():
    """Auto-próg (None) daje ≈ tyle barów co wejście (±50%)."""
    bary = _bary_syntetyczne(200)
    vb = bary_wolumenowe(bary)
    assert 100 <= len(vb) <= 220


def test_zwroty_z_barow():
    bary = [{"close": 100.0}, {"close": 110.0}, {"close": 99.0}]
    zw = zwroty_z_barow(bary)
    assert abs(zw[0] - 0.10) < 1e-9 and abs(zw[1] + 0.10) < 1e-9


def test_dwuzegarowa_buy_and_hold_z_dryfem_przechodzi():
    """Strategia long-zawsze na rynku z realnym dryfem → oba zegary zielone."""
    bary = _bary_syntetyczne(600, seed=9)
    zw_kal = [p * z for p, z in zip([1.0] * (len(bary) - 1),
                                    zwroty_z_barow(bary))]
    w = bramka_dwuzegarowa(zw_kal, bary, sygnal_fn=lambda vb: [1] * len(vb))
    assert w["zegar_wolumenowy"] is not None
    assert w["ok"], f"realny dryf powinien przejść oba zegary: {w}"


def test_dwuzegarowa_szum_nie_przechodzi():
    """Strategia losowa na rynku bez dryfu → odrzucona z czytelnym powodem."""
    rng = np.random.default_rng(3)
    bary = []
    cena = 100.0
    for _ in range(600):
        ret = rng.normal(0.0, 0.01)
        o = cena
        cena *= (1 + ret)
        bary.append({"open": o, "high": max(o, cena), "low": min(o, cena),
                     "close": cena, "volume": float(rng.uniform(50, 150))})
    zw_kal = [float(rng.choice([-1, 1])) * z for z in zwroty_z_barow(bary)]
    w = bramka_dwuzegarowa(zw_kal, bary,
                           sygnal_fn=lambda vb: list(rng.choice([-1, 1], len(vb))))
    assert not w["ok"] and w["powod"]


def test_dwuzegarowa_za_malo_barow_wolumenowych():
    """Granica: < 12 barów wolumenowych → odrzucone z powodem."""
    bary = _bary_syntetyczne(8)
    zw = zwroty_z_barow(bary)
    w = bramka_dwuzegarowa(zw, bary, sygnal_fn=lambda vb: [1] * len(vb))
    assert not w["ok"] and "za mało barów wolumenowych" in w["powod"]


def test_dwuzegarowa_sygnal_fn_zla_dlugosc_rzuca():
    """sygnal_fn zwracający złą długość → ValueError (kontrakt jawny)."""
    bary = _bary_syntetyczne(300)
    zw = zwroty_z_barow(bary)
    try:
        bramka_dwuzegarowa(zw, bary, sygnal_fn=lambda vb: [1] * (len(vb) - 1))
        raise AssertionError("powinno rzucić ValueError")
    except ValueError:
        pass


# ── Etap I Koloseum (ROADMAP + W-282 w jednej bramce) ────────────────────────

from imperium.koloseum.walidacja import etap_pierwszy_koloseum  # noqa: E402


class _Stat:
    """Minimalny duck-type StatystykiSesji do testów."""
    def __init__(self, trades=30, dd=0.08, wr=0.60, pf=2.0):
        # UWAGA: silnik trzyma wr/dd jako UŁAMKI (0.5=50%) mimo nazwy _pct
        self.total_trades = trades
        self.max_drawdown_pct = dd
        self.win_rate = wr
        self.profit_factor = pf


def _krzywa_dobra(n=400, seed=21):
    rng = np.random.default_rng(seed)
    zw = rng.normal(0.003, 0.008, n)
    return 10_000 * np.cumprod(1 + zw)


def test_etap1_dobra_strategia_przechodzi():
    w = etap_pierwszy_koloseum(_krzywa_dobra(), _Stat(), interwal="1D")
    assert w["ok"], f"powinna przejść: {w}"
    assert w["sharpe_roczny"] > 1.0 and w["dsr"] >= 0.95


def test_etap1_szum_odpada_na_dsr_lub_sharpe():
    rng = np.random.default_rng(4)
    krzywa = 10_000 * np.cumprod(1 + rng.normal(0.0, 0.01, 400))
    w = etap_pierwszy_koloseum(krzywa, _Stat(), interwal="1D")
    assert not w["ok"] and w["powod"]


def test_etap1_za_malo_tradow():
    w = etap_pierwszy_koloseum(_krzywa_dobra(), _Stat(trades=5))
    assert not w["ok"] and "za mało trade" in w["powod"]


def test_etap1_drawdown_za_duzy():
    w = etap_pierwszy_koloseum(_krzywa_dobra(), _Stat(dd=0.20))
    assert not w["ok"] and "MaxDD" in w["powod"]


def test_etap1_wr_lub_pf_wystarczy_jedno():
    """WR niski ALE PF wysoki → przechodzi (alternatywa z ROADMAP)."""
    w = etap_pierwszy_koloseum(_krzywa_dobra(), _Stat(wr=0.40, pf=2.5))
    assert w["ok"], f"PF>1.5 powinno wystarczyć: {w}"
    w2 = etap_pierwszy_koloseum(_krzywa_dobra(), _Stat(wr=0.40, pf=1.2))
    assert not w2["ok"], "oba poniżej progu → odpada"


def test_etap1_granice_krzywej():
    """Za krótka krzywa i bankructwo (equity ≤ 0) odrzucone z powodem."""
    w = etap_pierwszy_koloseum([10_000.0] * 10)
    assert not w["ok"] and "za krótka" in w["powod"]
    krzywa = list(_krzywa_dobra(50))
    krzywa[25] = 0.0
    w2 = etap_pierwszy_koloseum(krzywa)
    assert not w2["ok"] and "bankructwo" in w2["powod"]


def test_etap1_bez_statystyk_tylko_sharpe_dsr():
    """statystyki=None → tylko progi z krzywej (Sharpe + DSR)."""
    w = etap_pierwszy_koloseum(_krzywa_dobra(), statystyki=None)
    assert w["ok"]


def test_etap1_selection_bias_zaostrza():
    """Słaba-pozytywna strategia: przy n_prob=200 odpada na DSR (uczciwość)."""
    rng = np.random.default_rng(8)
    krzywa = 10_000 * np.cumprod(1 + rng.normal(0.0006, 0.01, 300))
    w1 = etap_pierwszy_koloseum(krzywa, _Stat(), n_prob=1)
    w200 = etap_pierwszy_koloseum(krzywa, _Stat(), n_prob=200)
    assert (w1["dsr"] or 0) > (w200["dsr"] or 0)
    assert not w200["ok"]
