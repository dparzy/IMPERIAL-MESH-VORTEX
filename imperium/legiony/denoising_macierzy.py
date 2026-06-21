"""
🧬 IMV-LDP | Denoising + Clustering macierzy korelacji (López de Prado, MLAM 2020).

ŹRÓDŁO: Marcos López de Prado "Machine Learning for Asset Managers" (BIB-023, INF-35).
Wizje W-365 (denoising), W-366 (ONC clustering), W-367 (NCO), W-368 (detoning).

PO CO TO (dla nowicjusza):
  Macierz korelacji między GŁOSAMI neuronów jest w >90% szumem (López de Prado).
  Surowa korelacja (diagnostyka_korelacji.py) magnifikuje ten szum → fałszywe pary
  „redundantne" i niestabilne wagi (synapsy_rezimowe). Te narzędzia czyszczą macierz
  ZANIM podejmiemy decyzję o dekorelacji (Prawo XVI) lub alokacji wag.

  W-365 DENOISING (Marchenko-Pastur): wartości własne poniżej progu losowego (λ⁺)
        to szum → uśredniamy je (constant residual eigenvalue). Bije shrinkage
        Ledoit-Wolf, bo nie rozcieńcza sygnału razem z szumem.
  W-368 DETONING: dodatkowo usuwa 1-2 dominujące wartości własne („ton rynkowy" —
        wspólny czynnik poruszający wszystkimi naraz) → wzmacnia subtelne, zdekorelowane
        głosy = filary siły Prawa XVI.
  W-366 ONC (Optimal Number of Clusters): auto-grupuje skorelowane neurony (K-Means
        na metryce odległości + silhouette), bez zadawania liczby klastrów z góry.
        Zamiast ręcznie patrzeć na pary |ρ|>0.80 → system sam znajduje klastry redundancji.
  W-367 NCO (Nested Clustered Optimization): stabilne wagi min-wariancji — klastruj,
        optymalizuj WEWNĄTRZ klastra, potem MIĘDZY klastrami. RMSE −47..55% vs Markowitz
        (klątwa Markowitza: wysoka korelacja → V⁻¹ eksploduje).

ZALEŻNOŚCI: tylko numpy (scipy/sklearn niedostępne → KDE i K-Means w czystym numpy).
BRAK LOOKAHEAD: operuje na podanej macierzy, nie czyta przyszłości.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger("DenoisingMacierzy")


# ─── Podstawy PCA / konwersje ────────────────────────────────────────────────

def pca(macierz: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Rozkład spektralny macierzy symetrycznej (korelacji/kowariancji).
    Zwraca (wartosci_wlasne, wektory_wlasne) posortowane MALEJĄCO.
    """
    eval_, evec = np.linalg.eigh(macierz)
    idx = eval_.argsort()[::-1]
    return eval_[idx], evec[:, idx]


def cov_na_corr(cov: np.ndarray) -> np.ndarray:
    """Macierz kowariancji → korelacji (przekątna = 1)."""
    std = np.sqrt(np.clip(np.diag(cov), 1e-12, None))
    corr = cov / np.outer(std, std)
    return np.clip(corr, -1.0, 1.0)


def corr_na_cov(corr: np.ndarray, std: np.ndarray) -> np.ndarray:
    """Macierz korelacji + wektor odchyleń → kowariancji."""
    return corr * np.outer(std, std)


# ─── W-365: Denoising Marchenko-Pastur ───────────────────────────────────────

def mp_pdf(var: float, q: float, pts: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
    """
    Teoretyczna gęstość Marchenko-Pastur dla macierzy losowej.

    var: wariancja (1.0 dla czystego szumu w macierzy korelacji)
    q:   T/N (liczba obserwacji / liczba zmiennych), musi być > 1
    Zwraca (x = wartości własne, pdf).
    """
    if q <= 1:
        raise ValueError(f"q=T/N musi być >1 (masz {q:.3f}) — za mało obserwacji na zmienną")
    e_min = var * (1 - (1.0 / q) ** 0.5) ** 2
    e_max = var * (1 + (1.0 / q) ** 0.5) ** 2
    eval_ = np.linspace(e_min, e_max, pts)
    pdf = q / (2 * np.pi * var * eval_) * np.sqrt(np.clip((e_max - eval_) * (eval_ - e_min), 0, None))
    return eval_, pdf


def _kde_gauss(obserwacje: np.ndarray, x: np.ndarray, bwidth: float) -> np.ndarray:
    """
    Estymator gęstości jądrowej (Gaussian KDE) — czysty numpy (brak sklearn).
    Liczy gęstość empiryczną wartości własnych w punktach x.
    """
    obs = obserwacje.reshape(-1, 1)
    xx = x.reshape(1, -1)
    # jądro Gaussa: (1/√2π) exp(-z²/2), z=(x-obs)/h, uśrednione po obserwacjach
    z = (xx - obs) / bwidth
    ker = np.exp(-0.5 * z ** 2) / np.sqrt(2 * np.pi)
    return ker.mean(axis=0) / bwidth


def _blad_dopasowania(var: float, eval_emp: np.ndarray, q: float, bwidth: float, pts: int) -> float:
    """SSE między teoretycznym MP-pdf a empirycznym KDE wartości własnych."""
    x, pdf_teo = mp_pdf(var, q, pts)
    pdf_emp = _kde_gauss(eval_emp, x, bwidth)
    return float(np.sum((pdf_emp - pdf_teo) ** 2))


def znajdz_max_eval(eval_emp: np.ndarray, q: float, bwidth: float = 0.25,
                    pts: int = 1000) -> Tuple[float, float]:
    """
    Dopasowuje wariancję szumu var (grid search, bo brak scipy.minimize) tak, by
    teoretyczny MP-pdf najlepiej pasował do empirycznego rozkładu wartości własnych.

    Zwraca (e_max, var): e_max = górna granica szumu (wartości własne > e_max = sygnał).
    """
    najlepsze_var, najlepszy_blad = 1.0, np.inf
    for var in np.linspace(0.05, 1.0, 100):
        b = _blad_dopasowania(var, eval_emp, q, bwidth, pts)
        if b < najlepszy_blad:
            najlepszy_blad, najlepsze_var = b, var
    e_max = najlepsze_var * (1 + (1.0 / q) ** 0.5) ** 2
    return e_max, najlepsze_var


def denoise_macierz(corr: np.ndarray, q: float, bwidth: float = 0.25) -> Dict[str, object]:
    """
    🧬 W-365 | Denoising macierzy korelacji metodą constant residual eigenvalue.

    Wartości własne ≤ e_max (próg Marchenko-Pastur) to szum → zastępujemy je ich
    średnią (zachowujemy ślad macierzy). Wartości > e_max to sygnał → bez zmian.

    corr:   macierz korelacji (N×N), przekątna = 1
    q:      T/N (liczba próbek / liczba zmiennych); musi być > 1
    Zwraca dict: {corr_denoised, e_max, var_szumu, n_czynnikow (ile sygnału)}.
    """
    corr = np.asarray(corr, dtype=float)
    n = corr.shape[0]
    eval_, evec = pca(corr)
    e_max, var = znajdz_max_eval(eval_, q, bwidth)
    n_czynnikow = int((eval_ > e_max).sum())  # ile wartości własnych to sygnał

    eval_clean = eval_.copy()
    if n_czynnikow < n:
        reszta = eval_clean[n_czynnikow:]
        eval_clean[n_czynnikow:] = reszta.sum() / float(n - n_czynnikow)  # uśrednij szum

    corr1 = evec @ np.diag(eval_clean) @ evec.T
    corr1 = cov_na_corr(corr1)  # przywróć przekątną = 1
    return {
        "corr_denoised": corr1,
        "e_max": float(e_max),
        "var_szumu": float(var),
        "n_czynnikow": n_czynnikow,
    }


# ─── W-368: Detoning ─────────────────────────────────────────────────────────

def detone_macierz(corr: np.ndarray, n_czynnikow: int = 1) -> np.ndarray:
    """
    🧬 W-368 | Detoning — usuwa „ton rynkowy" (n dominujących wartości własnych).

    Wspólny czynnik (np. cały rynek rośnie/spada) sprawia, że wszystkie głosy są
    pozornie skorelowane. Usunięcie go wzmacnia subtelne, zdekorelowane sygnały
    (filary Prawa XVI). UWAGA: macierz detonowana jest osobliwa (singular) — używać
    do KLASTROWANIA, nie do odwracania (V⁻¹).

    corr:         macierz korelacji
    n_czynnikow:  ile czołowych wartości własnych usunąć (1-2 typowo)
    Zwraca macierz korelacji bez tonu (przekątna przywrócona = 1).
    """
    corr = np.asarray(corr, dtype=float)
    if n_czynnikow < 1:
        return corr.copy()
    eval_, evec = pca(corr)
    n_czynnikow = min(n_czynnikow, len(eval_))
    # składowa rynkowa = czołowe wartości/wektory własne
    eval_m = eval_[:n_czynnikow]
    evec_m = evec[:, :n_czynnikow]
    corr_rynek = evec_m @ np.diag(eval_m) @ evec_m.T
    corr_deton = corr - corr_rynek
    return cov_na_corr(corr_deton)


# ─── W-366: ONC — Optimal Number of Clusters ─────────────────────────────────

def _kmeans(x: np.ndarray, k: int, n_init: int = 10, max_iter: int = 100,
            seed: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    K-Means w czystym numpy (brak sklearn). Zwraca (etykiety, centroidy) najlepszej
    inicjalizacji (najmniejsza inercja). Deterministyczny przez seed.
    """
    rng = np.random.default_rng(seed)
    m = x.shape[0]
    najlepsze_etyk, najlepsze_cen, najlepsza_inercja = None, None, np.inf
    for init in range(n_init):
        idx = rng.choice(m, size=k, replace=False)
        centroidy = x[idx].copy()
        etyk = np.zeros(m, dtype=int)
        for _ in range(max_iter):
            # przypisz do najbliższego centroidu
            dyst = np.linalg.norm(x[:, None, :] - centroidy[None, :, :], axis=2)
            nowe = dyst.argmin(axis=1)
            if np.array_equal(nowe, etyk):
                etyk = nowe
                break
            etyk = nowe
            # przelicz centroidy (puste klastry zostają)
            for c in range(k):
                masc = etyk == c
                if masc.any():
                    centroidy[c] = x[masc].mean(axis=0)
        dyst = np.linalg.norm(x[:, None, :] - centroidy[None, :, :], axis=2)
        inercja = float((dyst.min(axis=1) ** 2).sum())
        if inercja < najlepsza_inercja:
            najlepsza_inercja, najlepsze_etyk, najlepsze_cen = inercja, etyk.copy(), centroidy.copy()
    return najlepsze_etyk, najlepsze_cen


def _silhouette(dist: np.ndarray, etyk: np.ndarray) -> np.ndarray:
    """
    Silhouette score per-punkt na macierzy odległości (brak sklearn).
    s = (b - a) / max(a, b): a=śr. odległość wewnątrz klastra, b=najbliższy obcy klaster.
    """
    m = len(etyk)
    s = np.zeros(m)
    klastry = np.unique(etyk)
    for i in range(m):
        wlasny = etyk[i]
        masc_w = etyk == wlasny
        masc_w[i] = False
        a = dist[i, masc_w].mean() if masc_w.any() else 0.0
        b = np.inf
        for c in klastry:
            if c == wlasny:
                continue
            masc_c = etyk == c
            if masc_c.any():
                b = min(b, dist[i, masc_c].mean())
        s[i] = 0.0 if max(a, b) == 0 else (b - a) / max(a, b)
    return s


def klastruj_onc(corr: np.ndarray, klucze: Optional[List[str]] = None,
                 max_k: Optional[int] = None, n_init: int = 10,
                 seed: int = 0) -> Dict[str, object]:
    """
    🧬 W-366 | ONC — auto-klastrowanie skorelowanych zmiennych (López de Prado).

    Metryka odległości oparta na korelacji: d = √(½(1−ρ)) (prawdziwa metryka).
    Testuje k = 2..max_k, wybiera k o najlepszym wskaźniku jakości (średnia/odch.
    silhouette = t-stat) — bez zadawania liczby klastrów z góry.

    corr:   macierz korelacji (N×N)
    klucze: nazwy zmiennych (np. klucze neuronów); domyślnie indeksy
    max_k:  maks. liczba klastrów (domyślnie N//2)
    Zwraca dict: {klastry: {id: [klucze]}, etykiety, q_jakosc, silhouette_sr, k}.
    """
    corr = np.asarray(corr, dtype=float)
    n = corr.shape[0]
    if klucze is None:
        klucze = [str(i) for i in range(n)]
    if n < 2:
        return {"klastry": {0: list(klucze)}, "etykiety": [0] * n,
                "q_jakosc": 0.0, "silhouette_sr": 0.0, "k": 1}

    dist = np.sqrt(np.clip((1.0 - corr) / 2.0, 0, None))
    np.fill_diagonal(dist, 0.0)
    if max_k is None:
        max_k = max(2, n // 2)
    max_k = min(max_k, n - 1)

    najlepsze = None
    for k in range(2, max_k + 1):
        etyk, _ = _kmeans(dist, k, n_init=n_init, seed=seed)
        sil = _silhouette(dist, etyk)
        std = sil.std()
        q = sil.mean() / std if std > 1e-12 else sil.mean()  # t-stat jakości klastrowania
        if najlepsze is None or q > najlepsze[0]:
            najlepsze = (q, k, etyk, sil)

    # GRANICA: n=2 → max_k=1, pętla pusta → wszystkie w jednym klastrze (brak crashu)
    if najlepsze is None:
        return {"klastry": {0: list(klucze)}, "etykiety": [0] * n,
                "q_jakosc": 0.0, "silhouette_sr": 0.0, "k": 1}

    q, k, etyk, sil = najlepsze
    klastry: Dict[int, List[str]] = {}
    for i, c in enumerate(etyk):
        klastry.setdefault(int(c), []).append(klucze[i])
    return {
        "klastry": klastry,
        "etykiety": [int(c) for c in etyk],
        "q_jakosc": float(q),
        "silhouette_sr": float(sil.mean()),
        "k": int(k),
    }


# ─── W-367: NCO — Nested Clustered Optimization ───────────────────────────────

def _wagi_min_wariancji(cov: np.ndarray) -> np.ndarray:
    """
    Wagi portfela minimalnej wariancji: w = Σ⁻¹·1 / (1ᵀ·Σ⁻¹·1).
    Pseudo-odwrotność (pinv) dla stabilności przy macierzy bliskiej osobliwej.
    """
    inv = np.linalg.pinv(cov)
    jeden = np.ones((cov.shape[0], 1))
    w = inv @ jeden
    w = w / (jeden.T @ inv @ jeden)
    return w.flatten()


def nco_wagi(cov: np.ndarray, klucze: Optional[List[str]] = None,
             max_k: Optional[int] = None, seed: int = 0) -> Dict[str, object]:
    """
    🧬 W-367 | NCO — Nested Clustered Optimization (López de Prado).

    Stabilne wagi min-wariancji odporne na klątwę Markowitza (wysoka korelacja →
    Σ⁻¹ eksploduje). Algorytm: (1) klastruj korelację (ONC); (2) optymalizuj wagi
    WEWNĄTRZ każdego klastra; (3) zredukuj kowariancję do poziomu klastrów; (4)
    optymalizuj MIĘDZY klastrami; (5) złóż wagi (intra × inter).

    cov:    macierz kowariancji (N×N)
    klucze: nazwy zmiennych
    Zwraca dict: {wagi: {klucz: waga}, wagi_wektor, klastry, k}.
    """
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if klucze is None:
        klucze = [str(i) for i in range(n)]
    if n == 1:
        return {"wagi": {klucze[0]: 1.0}, "wagi_wektor": np.array([1.0]),
                "klastry": {0: list(klucze)}, "k": 1}

    corr = cov_na_corr(cov)
    onc = klastruj_onc(corr, klucze=klucze, max_k=max_k, seed=seed)
    etyk = np.array(onc["etykiety"])

    # mapowanie klucz→indeks (kolejność cov)
    klastry_idx: Dict[int, List[int]] = {}
    for i, c in enumerate(etyk):
        klastry_idx.setdefault(int(c), []).append(i)

    klastry_posort = sorted(klastry_idx)
    w_intra = np.zeros(n)
    # macierz redukcji: kolumna na klaster, wagi wewnątrzklastrowe
    redukcja = np.zeros((n, len(klastry_posort)))
    for kol, c in enumerate(klastry_posort):
        idx = klastry_idx[c]
        sub = cov[np.ix_(idx, idx)]
        w = _wagi_min_wariancji(sub)
        for lokalny, glob in enumerate(idx):
            w_intra[glob] = w[lokalny]
            redukcja[glob, kol] = w[lokalny]

    # kowariancja na poziomie klastrów + wagi międzyklastrowe
    cov_klastry = redukcja.T @ cov @ redukcja
    w_inter = _wagi_min_wariancji(cov_klastry)

    # złożenie: waga globalna = waga_intra × waga_inter(klastra)
    wagi = np.zeros(n)
    for kol, c in enumerate(klastry_posort):
        for glob in klastry_idx[c]:
            wagi[glob] = w_intra[glob] * w_inter[kol]

    suma = wagi.sum()
    if abs(suma) > 1e-12:
        wagi = wagi / suma  # normalizacja do Σw=1

    return {
        "wagi": {klucze[i]: float(wagi[i]) for i in range(n)},
        "wagi_wektor": wagi,
        "klastry": onc["klastry"],
        "k": onc["k"],
    }


# ─── W-374 HRP (Hierarchical Risk Parity) ────────────────────────────────────

def _odleglosc_korelacji(corr: np.ndarray) -> np.ndarray:
    """Metryka odległości López de Prado: d = √(½(1−ρ)) ∈ [0,1]."""
    return np.sqrt(np.clip(0.5 * (1.0 - corr), 0.0, 1.0))


def _linkage_single(dist: np.ndarray) -> List[Tuple[int, int, float, int]]:
    """
    Aglomeracyjne klastrowanie single-linkage w czystym numpy.
    Zwraca listę połączeń [(klaster_a, klaster_b, odległość, rozmiar)] (jak scipy.linkage).
    """
    n = dist.shape[0]
    # aktywne klastry: id → lista indeksów oryginalnych
    klastry: Dict[int, List[int]] = {i: [i] for i in range(n)}
    nastepny_id = n
    linkage: List[Tuple[int, int, float, int]] = []
    aktywne = list(range(n))

    while len(aktywne) > 1:
        # znajdź najbliższą parę (single-linkage = min odległość między elementami)
        najmniej = np.inf
        para = (aktywne[0], aktywne[1])
        for ia in range(len(aktywne)):
            for ib in range(ia + 1, len(aktywne)):
                a, b = aktywne[ia], aktywne[ib]
                # single linkage: minimalna odległość między członkami
                sub = dist[np.ix_(klastry[a], klastry[b])]
                d = float(np.min(sub))
                if d < najmniej:
                    najmniej = d
                    para = (a, b)

        a, b = para
        nowy = klastry[a] + klastry[b]
        linkage.append((a, b, najmniej, len(nowy)))
        klastry[nastepny_id] = nowy
        aktywne.remove(a)
        aktywne.remove(b)
        aktywne.append(nastepny_id)
        nastepny_id += 1

    return linkage


def _kolejnosc_quasi_diag(linkage: List[Tuple[int, int, float, int]], n: int) -> List[int]:
    """Seriation: kolejność liści z dendrogramu (quasi-diagonalizacja macierzy)."""
    if not linkage:
        return list(range(n))
    # ostatnie połączenie zawiera korzeń
    kolejnosc = [linkage[-1][0], linkage[-1][1]]
    # rozwijaj klastry > n-1 do liści
    zmiana = True
    while zmiana:
        zmiana = False
        nowa = []
        for item in kolejnosc:
            if item >= n:  # to klaster, rozwiń
                idx = item - n
                nowa.append(linkage[idx][0])
                nowa.append(linkage[idx][1])
                zmiana = True
            else:
                nowa.append(item)
        kolejnosc = nowa
    return kolejnosc


def _wariancja_klastra(cov: np.ndarray, idx: List[int]) -> float:
    """Wariancja portfela inverse-variance wewnątrz klastra."""
    sub = cov[np.ix_(idx, idx)]
    diag = np.diag(sub).copy()
    diag[diag <= 1e-12] = 1e-12  # guard: aktyw o zerowej wariancji nie psuje 1/var
    iv = 1.0 / diag
    iv = iv / iv.sum()
    return float(iv @ sub @ iv)


def hrp_wagi(cov: np.ndarray, klucze: Optional[List[str]] = None) -> Dict[str, object]:
    """
    🌲 W-374 | HRP — Hierarchical Risk Parity (López de Prado 2016, Jansen BIB-026).

    Alokacja oparta na dendrogramie — NIE wymaga odwracania macierzy (w przeciwieństwie
    do Markowitza/min-wariancji), więc odporna na klątwę Markowitza i numerycznie stabilna.

    Algorytm:
      (1) odległość korelacji d=√(½(1−ρ)), (2) single-linkage clustering,
      (3) quasi-diagonalizacja (seriation), (4) recursive bisection — dziel kapitał
          między dwie połowy proporcjonalnie do odwrotności ich wariancji.

    cov:    macierz kowariancji (N×N)
    klucze: nazwy zmiennych
    Zwraca: {wagi: {klucz: waga}, wagi_wektor, kolejnosc}.
    """
    cov = np.asarray(cov, dtype=float)
    n = cov.shape[0]
    if klucze is None:
        klucze = [str(i) for i in range(n)]
    if n == 1:
        return {"wagi": {klucze[0]: 1.0}, "wagi_wektor": np.array([1.0]), "kolejnosc": [0]}

    corr = cov_na_corr(cov)
    dist = _odleglosc_korelacji(corr)
    linkage = _linkage_single(dist)
    kolejnosc = _kolejnosc_quasi_diag(linkage, n)

    # recursive bisection
    wagi = np.ones(n)
    klastry_do_podzialu = [kolejnosc]
    while klastry_do_podzialu:
        nowe = []
        for grupa in klastry_do_podzialu:
            if len(grupa) <= 1:
                continue
            polowa = len(grupa) // 2
            lewa, prawa = grupa[:polowa], grupa[polowa:]
            var_l = _wariancja_klastra(cov, lewa)
            var_p = _wariancja_klastra(cov, prawa)
            # alfa = udział lewej połowy (mniejsza wariancja → większy udział)
            alfa = 1.0 - var_l / (var_l + var_p) if (var_l + var_p) > 1e-12 else 0.5
            for i in lewa:
                wagi[i] *= alfa
            for i in prawa:
                wagi[i] *= (1.0 - alfa)
            nowe.append(lewa)
            nowe.append(prawa)
        klastry_do_podzialu = nowe

    suma = wagi.sum()
    if abs(suma) > 1e-12:
        wagi = wagi / suma

    return {
        "wagi": {klucze[i]: float(wagi[i]) for i in range(n)},
        "wagi_wektor": wagi,
        "kolejnosc": kolejnosc,
    }
