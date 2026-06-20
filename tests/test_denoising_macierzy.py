"""
Testy denoising/clustering macierzy korelacji (W-365..368, López de Prado MLAM).
REGUŁA TEST-GRANIC (Prawo XXI): identyczność, blok znany, pojedynczy element, szum.
"""

import numpy as np

from imperium.legiony.denoising_macierzy import (
    pca, cov_na_corr, corr_na_cov,
    mp_pdf, denoise_macierz,
    detone_macierz, klastruj_onc, nco_wagi,
    _wagi_min_wariancji,
)


def _macierz_blokowa(seed=0):
    """Macierz korelacji z 2 wyraźnymi blokami (klastry) + szum."""
    rng = np.random.default_rng(seed)
    t, n = 1000, 6
    # 2 ukryte czynniki: pierwsze 3 zmienne z czynnika A, kolejne 3 z B
    fa = rng.standard_normal(t)
    fb = rng.standard_normal(t)
    X = np.zeros((t, n))
    for i in range(3):
        X[:, i] = 0.9 * fa + 0.1 * rng.standard_normal(t)
    for i in range(3, 6):
        X[:, i] = 0.9 * fb + 0.1 * rng.standard_normal(t)
    return np.corrcoef(X, rowvar=False), t, n


# ─── PCA / konwersje ──────────────────────────────────────────────────────────

def test_pca_sortuje_malejaco():
    corr, _, _ = _macierz_blokowa()
    eval_, evec = pca(corr)
    assert np.all(np.diff(eval_) <= 1e-9)  # malejąco
    assert eval_[0] > eval_[-1]


def test_cov_corr_roundtrip():
    corr, _, _ = _macierz_blokowa()
    std = np.array([2.0, 1.0, 0.5, 3.0, 1.5, 0.8])
    cov = corr_na_cov(corr, std)
    corr2 = cov_na_corr(cov)
    assert np.allclose(corr, corr2, atol=1e-9)
    assert np.allclose(np.diag(corr2), 1.0)


# ─── W-365 Denoising ──────────────────────────────────────────────────────────

def test_mp_pdf_wymaga_q_powyzej_1():
    import pytest
    with pytest.raises(ValueError):
        mp_pdf(1.0, q=0.5)  # GRANICA: q≤1 niedozwolone


def test_mp_pdf_calkuje_sie_do_okolo_1():
    x, pdf = mp_pdf(1.0, q=10.0, pts=5000)
    całka = np.trapezoid(pdf, x)
    assert 0.85 < całka < 1.05  # MP-pdf to gęstość (część masy w atomie przy małym q)


def test_denoise_zachowuje_wymiar_i_przekatna():
    corr, t, n = _macierz_blokowa()
    wynik = denoise_macierz(corr, q=t / n)
    cd = wynik["corr_denoised"]
    assert cd.shape == (n, n)
    assert np.allclose(np.diag(cd), 1.0, atol=1e-9)  # przekątna pozostaje 1


def test_denoise_wykrywa_czynniki_sygnalu():
    # 2 bloki → spodziewamy się ≥1 czynnika sygnału (wartość własna > e_max)
    corr, t, n = _macierz_blokowa()
    wynik = denoise_macierz(corr, q=t / n)
    assert wynik["n_czynnikow"] >= 1
    assert wynik["e_max"] > 0


def test_denoise_macierz_identycznosci_szum():
    # GRANICA: czysta identyczność (zero korelacji) = czysty szum, 0 czynników sygnału
    n, t = 5, 2000
    corr = np.eye(n)
    wynik = denoise_macierz(corr, q=t / n)
    assert wynik["n_czynnikow"] == 0  # brak sygnału w identyczności
    assert np.allclose(np.diag(wynik["corr_denoised"]), 1.0)


# ─── W-368 Detoning ───────────────────────────────────────────────────────────

def _macierz_z_rynkiem(seed=0):
    """Macierz gdzie WSZYSTKIE zmienne ładują wspólny czynnik rynkowy + idiosynkrazja."""
    rng = np.random.default_rng(seed)
    t, n = 2000, 6
    rynek = rng.standard_normal(t)
    X = np.column_stack([0.8 * rynek + 0.2 * rng.standard_normal(t) for _ in range(n)])
    return np.corrcoef(X, rowvar=False), n


def test_detone_usuwa_ton_rynkowy():
    corr, n = _macierz_z_rynkiem()
    deton = detone_macierz(corr, n_czynnikow=1)
    # po usunięciu wspólnego tonu rynkowego suma |korelacji pozadiagonalnych| maleje
    off = ~np.eye(n, dtype=bool)
    assert np.abs(deton[off]).sum() < np.abs(corr[off]).sum()
    assert np.allclose(np.diag(deton), 1.0, atol=1e-9)


def test_detone_zero_czynnikow_bez_zmian():
    # GRANICA: n_czynnikow=0 → macierz niezmieniona
    corr, _, _ = _macierz_blokowa()
    assert np.allclose(detone_macierz(corr, n_czynnikow=0), corr)


# ─── W-366 ONC clustering ─────────────────────────────────────────────────────

def test_onc_znajduje_dwa_bloki():
    corr, _, _ = _macierz_blokowa()
    klucze = ["A1", "A2", "A3", "B1", "B2", "B3"]
    wynik = klastruj_onc(corr, klucze=klucze, seed=1)
    assert wynik["k"] == 2  # dwa wyraźne bloki
    # A* razem, B* razem (sprawdź że każdy klaster jest jednorodny)
    for czlonkowie in wynik["klastry"].values():
        prefiksy = {c[0] for c in czlonkowie}
        assert len(prefiksy) == 1  # tylko A albo tylko B


def test_onc_pojedyncza_zmienna():
    # GRANICA: 1 zmienna → 1 klaster, bez wywrotki
    wynik = klastruj_onc(np.array([[1.0]]), klucze=["X"])
    assert wynik["k"] == 1
    assert wynik["klastry"] == {0: ["X"]}


def test_onc_dwie_zmienne_bez_crashu():
    # GRANICA: n=2 → max_k=1, pętla pusta → 1 klaster, NIE crash (bug z recenzji)
    corr = np.array([[1.0, 0.5], [0.5, 1.0]])
    wynik = klastruj_onc(corr, klucze=["A", "B"])
    assert wynik["k"] == 1
    assert sorted(wynik["klastry"][0]) == ["A", "B"]


def test_nco_dwa_aktywa_bez_crashu():
    # GRANICA: NCO na n=2 (woła ONC wewnętrznie) — nie może wywrócić
    cov = np.array([[1.0, 0.3], [0.3, 2.0]])
    wynik = nco_wagi(cov, klucze=["X", "Y"])
    assert abs(wynik["wagi_wektor"].sum() - 1.0) < 1e-9


def test_onc_deterministyczny_seed():
    corr, _, _ = _macierz_blokowa()
    a = klastruj_onc(corr, seed=42)
    b = klastruj_onc(corr, seed=42)
    assert a["etykiety"] == b["etykiety"]  # ten sam seed = ten sam wynik


# ─── W-367 NCO ────────────────────────────────────────────────────────────────

def test_nco_wagi_sumuja_do_jeden():
    corr, _, n = _macierz_blokowa()
    std = np.ones(n)
    cov = corr_na_cov(corr, std)
    wynik = nco_wagi(cov, klucze=[f"N{i}" for i in range(n)])
    assert abs(wynik["wagi_wektor"].sum() - 1.0) < 1e-9


def test_nco_pojedynczy_aktyw():
    # GRANICA: 1 aktyw → waga 1.0
    wynik = nco_wagi(np.array([[4.0]]), klucze=["solo"])
    assert wynik["wagi"]["solo"] == 1.0


def test_min_wariancji_preferuje_niska_wariancje():
    # aktyw o niższej wariancji dostaje wyższą wagę (min-var)
    cov = np.diag([1.0, 4.0])  # drugi 4× bardziej zmienny
    w = _wagi_min_wariancji(cov)
    assert w[0] > w[1]
    assert abs(w.sum() - 1.0) < 1e-9


def test_nco_redukuje_skrajne_wagi_vs_markowitz():
    # NCO ma być stabilniejsze: brak ekstremalnych wag przy wysokiej korelacji
    corr, _, n = _macierz_blokowa()
    cov = corr_na_cov(corr, np.ones(n))
    nco = nco_wagi(cov)["wagi_wektor"]
    markowitz = _wagi_min_wariancji(cov)
    # NCO ma mniejszy rozrzut wag (bardziej zdywersyfikowane) niż surowy Markowitz
    assert nco.std() <= markowitz.std() + 1e-6
