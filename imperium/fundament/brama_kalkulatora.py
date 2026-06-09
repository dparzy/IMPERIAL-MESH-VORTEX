"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            BRAMA KALKULATORA — Fundament Prawa I (Zero Halucynacji)          ║
║                          Projekt: IMPERIUM (Cesarstwo)                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── POCHODZENIE (Prawo I) ──────────────────────────────
Idea: "Calculator Pattern" z systemu DNSS (patrz docs/WZORZEC_DNSS.md).
      LLM halucynują matematykę → kod liczy, AI tylko interpretuje.
Kod bazowy: zaadaptowany z działającej implementacji "Calculator Gateway"
      (oryginał: projekt Kingdom Pixel, Zasada 75). Logika obliczeń bez zmian.
      W Imperium pełni rolę fundamentu Prawa I i Prawa XIII.

──────────────────────────────── ROLA W IMPERIUM ──────────────────────────────────
JEDYNE wejście do matematyki. Żaden bot nie liczy sam — pyta Bramę i dostaje
wynik + pieczątkę audytu (hash + czas + źródło). AI nigdy nie wymyśla liczb.

Realizuje:
  • PRAWO I   — Zero halucynacji (matematykę liczy deterministyczny TA-Lib)
  • PRAWO XIII — Każda decyzja audytowalna (pieczątka SHA + log)
  • PRAWO IX  — Weryfikacja w głębi (guardrail: odrzuca nieznane obliczenia)

CHANGELOG:
  v1.0 — adaptacja do Imperium: rejestr dozwolonych obliczeń, kontrakt JSON,
         log audytu, twarde odrzucanie nieznanych żądań (guardrail).
═════════════════════════════════════════════════════════════════════════════════════
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Callable, Optional

import numpy as np

# ── Prawo I: deterministyczny rdzeń. Bez TA-Lib Brama NIE działa (celowo). ──
try:
    import talib
except ImportError as e:
    raise RuntimeError(
        "Brama Kalkulatora wymaga TA-Lib (Prawo I — Zero halucynacji). "
        "Instalacja: `pip install TA-Lib`. Brak fallbacku do ręcznej matematyki."
    ) from e

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("BramaKalkulatora")

SOURCE_TAG = "TA-Lib (C-core, deterministic)"
SOURCE_TAG_PY = "pure-Python (deterministic)"

# Wskaźniki liczone czystą matematyką Pythona (TA-Lib ich nie ma).
# compute() stempluje je SOURCE_TAG_PY — audyt nie może kłamać o źródle (Prawo XIII).
_PURE_PYTHON_INDICATORS = {
    "AO", "AO_PREV", "AC", "AC_PREV", "HMA", "HMA_PREV",
    "DONCHIAN", "RVOL", "HIST_VOL", "YANG_ZHANG", "HURST_DFA", "PERMUTATION_ENTROPY", "VPIN", "WASH_TRADING", "CHOPPINESS", "ULCER",
    "BUBBLE_Z", "VOV", "RET_AR1", "VALUE_Z", "MOMA_Z", "OU_HALFLIFE", "VARIANCE_RATIO",
    "VWAP", "VWAP_STD",
    "SUPERTREND", "SUPERTREND_DIR", "SUPERTREND_DIR_PREV", "ICHIMOKU",
}


def _arr(x) -> np.ndarray:
    return np.asarray(x, dtype=np.float64)


def _last_valid(a: np.ndarray):
    """Ostatnia nie-NaN wartość (TA-Lib zwraca NaN w okresie rozgrzewania)."""
    a = np.asarray(a, dtype=np.float64)
    valid = a[~np.isnan(a)]
    return float(valid[-1]) if valid.size else None


def _second_last_valid(a: np.ndarray):
    """Przedostatnia nie-NaN wartość — wartość z poprzedniego baru (dla crossoverów)."""
    a = np.asarray(a, dtype=np.float64)
    valid = a[~np.isnan(a)]
    return float(valid[-2]) if valid.size >= 2 else None


# ── Pure-Python: wskaźniki których TA-Lib nie posiada ────────────────────────

def _py_vwap(high, low, close, volume) -> float:
    """VWAP = Σ(TypicalPrice × Volume) / Σ(Volume). Okres = cała podana seria."""
    tp = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
    vol = list(volume)
    total = sum(vol)
    return sum(t * v for t, v in zip(tp, vol)) / total if total else 0.0


def _py_vwap_std(high, low, close, volume) -> float:
    """Odchylenie standardowe VWAP (wolumenowo ważone)."""
    tp = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
    vol = list(volume)
    total = sum(vol)
    if not total:
        return 0.0
    vwap = sum(t * v for t, v in zip(tp, vol)) / total
    var = sum(v * (t - vwap) ** 2 for t, v in zip(tp, vol)) / total
    return var ** 0.5


def _py_awesome(high, low, fast: int = 5, slow: int = 34):
    """Awesome Oscillator = SMA(median,5) − SMA(median,34). median=(H+L)/2.
    Zwraca (AO_last, AO_prev). Bez TA-Lib — czysta matematyka."""
    med = [(h + l) / 2 for h, l in zip(high, low)]
    if len(med) < slow + 1:
        return None, None
    def sma(seq, p, idx):
        return sum(seq[idx - p + 1: idx + 1]) / p
    n = len(med)
    ao_last = sma(med, fast, n - 1) - sma(med, slow, n - 1)
    ao_prev = sma(med, fast, n - 2) - sma(med, slow, n - 2)
    return ao_last, ao_prev


def _py_hma(close, period: int = 16):
    """Hull Moving Average — szybka MA o minimalnym opóźnieniu.
    HMA = WMA(2·WMA(N/2) − WMA(N), sqrt(N)). Zwraca (HMA_last, HMA_prev).
    Bez TA-Lib — czysta matematyka. None gdy za mało danych."""
    c = list(close)
    half = max(1, period // 2)
    root = max(1, int(period ** 0.5))
    potrzeba = period + root  # by policzyć 2 ostatnie punkty HMA
    if len(c) < potrzeba:
        return None, None

    def wma(seq, p, idx):
        # ważona średnia: wagi 1..p, najnowszy bar waży najwięcej
        okno = seq[idx - p + 1: idx + 1]
        wagi = range(1, p + 1)
        return sum(s * w for s, w in zip(okno, wagi)) / (p * (p + 1) / 2)

    # surowa seria raw = 2·WMA(N/2) − WMA(N) dla każdego baru, potem WMA(sqrt) z raw
    n = len(c)
    raw = []
    for idx in range(period - 1, n):
        raw.append(2 * wma(c, half, idx) - wma(c, period, idx))
    if len(raw) < root + 1:
        return None, None
    m = len(raw)
    hma_last = wma(raw, root, m - 1)
    hma_prev = wma(raw, root, m - 2)
    return hma_last, hma_prev


def _py_accelerator(high, low, fast: int = 5, slow: int = 34, sma_ac: int = 5):
    """Accelerator Oscillator (Bill Williams) = AO − SMA(AO, 5).
    Mierzy PRZYSPIESZENIE momentum (2. pochodna ceny) — wyprzedza AO.
    Zwraca (AC_last, AC_prev). Bez TA-Lib — czysta matematyka."""
    med = [(h + l) / 2 for h, l in zip(high, low)]
    # Najgłębszy SMA(slow) przy najwcześniejszym indeksie AO (n−sma_ac−1) wymaga
    # n ≥ slow + sma_ac. Bez nadmiarowego +1 (off-by-one opóźniał wynik o 1 bar).
    potrzeba = slow + sma_ac
    if len(med) < potrzeba:
        return None, None

    def sma(seq, p, idx):
        return sum(seq[idx - p + 1: idx + 1]) / p

    n = len(med)
    # seria AO dla ostatnich (sma_ac+1) barów, by policzyć SMA(AO) i jego poprzednik
    ao_seria = [sma(med, fast, i) - sma(med, slow, i) for i in range(n - sma_ac - 1, n)]
    # AC[-1] = AO[-1] − SMA(AO, sma_ac) liczone do ostatniego baru
    ac_last = ao_seria[-1] - sum(ao_seria[-sma_ac:]) / sma_ac
    ac_prev = ao_seria[-2] - sum(ao_seria[-sma_ac - 1:-1]) / sma_ac
    return ac_last, ac_prev


def _py_donchian(high, low, period: int = 20):
    """Donchian Channel: górny=max(high,period), dolny=min(low,period), środek.
    Zwraca dict UPPER/LOWER/MID (z barów do −2, bez bieżącego — brak lookahead na wybicie)."""
    if len(high) < period + 1:
        return {"DONCHIAN_UPPER": None, "DONCHIAN_LOWER": None, "DONCHIAN_MID": None}
    # kanał liczony z okna POPRZEDNIEGO baru → bieżący close może go przebić (wybicie)
    okno_h = list(high)[-period - 1:-1]
    okno_l = list(low)[-period - 1:-1]
    up = max(okno_h); lo = min(okno_l)
    return {"DONCHIAN_UPPER": up, "DONCHIAN_LOWER": lo, "DONCHIAN_MID": (up + lo) / 2}


def _py_rvol(volume, period: int = 20):
    """Relative Volume = bieżący wolumen / średnia z 'period' poprzednich barów."""
    vol = list(volume)
    if len(vol) < period + 1:
        return None
    srednia = sum(vol[-period - 1:-1]) / period
    return vol[-1] / srednia if srednia > 0 else None


def _py_hist_vol(close, period: int = 20) -> Optional[float]:
    """
    Historical (Realized) Volatility = annualized std of log returns.
    Wzór: std(log(c[i]/c[i-1])) * sqrt(252) (annualizacja dziennych danych).
    Dla interwałów krótszych niż 1D wartość i tak porównywalna (relative ranking).
    """
    import math
    c = list(close)
    if len(c) < period + 1:
        return None
    window = c[-(period + 1):]
    log_ret = [math.log(window[i] / window[i - 1]) for i in range(1, len(window)) if window[i - 1] > 0]
    if len(log_ret) < 2:
        return None
    n = len(log_ret)
    mean = sum(log_ret) / n
    variance = sum((r - mean) ** 2 for r in log_ret) / (n - 1)
    return math.sqrt(variance) * math.sqrt(252)


def _py_yang_zhang(open_, high, low, close, period: int = 20) -> Optional[float]:
    """
    Yang-Zhang Realized Volatility — annualizowana zmienność z pełnego OHLC.

    Dla nowicjusza: zwykła zmienność (HIST_VOL) liczy tylko ceny zamknięcia
    (close), więc IGNORUJE skoki overnight (luka między zamknięciem a otwarciem)
    oraz cały zakres świecy (high/low). Yang-Zhang (2000) używa WSZYSTKICH czterech
    cen i jest do ~14× bardziej efektywny statystycznie — ta sama "prawdziwa" vol,
    ale policzona z dużo mniejszym szumem, odporny na drift i luki.

    Wzór (Yang & Zhang, 2000, "Drift-Independent Volatility Estimation"):
      σ²_YZ = σ²_overnight + k·σ²_open-close + σ²_RS
        overnight:   o_i = ln(O_i / C_{i-1})  → wariancja próbkowa
        open-close:  u_i = ln(C_i / O_i)       → wariancja próbkowa
        Rogers-Satchell: σ²_RS = mean[ ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O) ]
        k = 0.34 / (1.34 + (n+1)/(n-1))
      σ_YZ = sqrt(σ²_YZ) × sqrt(252)   (annualizacja, ta sama skala co HIST_VOL)

    Skala wyniku jest IDENTYCZNA z HIST_VOL (annualizowana), więc progi reżimu
    neuronu V-13 pozostają ważne — to czystsza wersja tej samej liczby (Prawo XV:
    pełne wykorzystanie informacji OHLC zamiast samego close).
    """
    import math
    o, h, l, c = list(open_), list(high), list(low), list(close)
    n_bars = min(len(o), len(h), len(l), len(c))
    if n_bars < period + 1:
        return None
    # Okno: ostatnie `period` świec; overnight potrzebuje C_{i-1}, więc bierzemy period+1 close.
    o = o[-period:]
    h = h[-period:]
    l = l[-period:]
    c_prev = c[-(period + 1):-1]   # C_{i-1} dla każdej z `period` świec
    c = c[-period:]
    n = period

    overnight = []   # ln(O_i / C_{i-1})
    openclose = []   # ln(C_i / O_i)
    rs = []          # Rogers-Satchell term
    for i in range(n):
        if min(o[i], h[i], l[i], c[i], c_prev[i]) <= 0:
            return None
        overnight.append(math.log(o[i] / c_prev[i]))
        openclose.append(math.log(c[i] / o[i]))
        rs.append(math.log(h[i] / c[i]) * math.log(h[i] / o[i])
                  + math.log(l[i] / c[i]) * math.log(l[i] / o[i]))

    if n < 2:
        return None
    mean_on = sum(overnight) / n
    var_on = sum((x - mean_on) ** 2 for x in overnight) / (n - 1)
    mean_oc = sum(openclose) / n
    var_oc = sum((x - mean_oc) ** 2 for x in openclose) / (n - 1)
    var_rs = sum(rs) / n

    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    var_yz = var_on + k * var_oc + (1 - k) * var_rs
    if var_yz < 0:
        var_yz = 0.0
    return math.sqrt(var_yz) * math.sqrt(252)


def _py_hurst_dfa(close, period: int = 100) -> Optional[float]:
    """
    Wykładnik Hursta metodą DFA (Detrended Fluctuation Analysis, Peng i in. 1994).
    Źródło: https://doi.org/10.1103/PhysRevE.49.1685

    Dla nowicjusza: wykładnik Hursta (H) mówi, czy rynek ma "pamięć":
      H > 0.5 → persystencja (trend ma kontynuację — podążaj za trendem)
      H < 0.5 → antypersystencja (mean-reversion — graj przeciw ruchowi)
      H ≈ 0.5 → błądzenie losowe (brak przewagi — NIE handluj, meta-brama STOP)

    Różnica od R/S (EXP-03 ZwiadowcaHurst): DFA DETRENDUJE każde okno wielomianem
    przed pomiarem fluktuacji, więc jest odporny na niestacjonarność (trendy).
    R/S na silnie trendującym krypto daje obciążone H; DFA — nie. Dlatego oba
    estymatory dekorelują na trendzie (Prawo XVI — różna informacja, krzyżowe
    potwierdzenie, analogicznie do duetu Higuchi FD + Hurst R/S).

    Algorytm:
      1. x = log-zwroty close
      2. profil Y(i) = skumulowana suma (x - średnia)
      3. dla okien n: podziel profil na pudełka, w każdym dopasuj prostą (trend
         lokalny) i policz RMS reszt; F(n) = średnia RMS po pudełkach
      4. F(n) ~ n^H → H = nachylenie regresji log F(n) vs log n
    Zwraca H ∈ (0,1). Fallback None gdy za mało danych (Prawo I — bez halucynacji).
    """
    import math
    c = list(close)
    if len(c) < period:
        return None
    seria = c[-period:]
    # log-zwroty — obie świece muszą być dodatnie (log domain), inaczej brak danych
    x = []
    for i in range(1, len(seria)):
        if seria[i - 1] <= 0 or seria[i] <= 0:
            return None
        x.append(math.log(seria[i] / seria[i - 1]))
    n_x = len(x)
    if n_x < 16:
        return None
    srednia = sum(x) / n_x
    # profil (skumulowana suma odchyleń)
    Y = []
    acc = 0.0
    for v in x:
        acc += v - srednia
        Y.append(acc)

    # rozmiary okien: geometrycznie od 4 do n_x//4
    okna = []
    n = 4
    while n <= n_x // 4:
        okna.append(n)
        n = max(n + 1, int(n * 1.4))
    if len(okna) < 2:
        return None

    log_n, log_F = [], []
    for n in okna:
        liczba_pudelek = n_x // n
        if liczba_pudelek < 1:
            continue
        rms_sum = 0.0
        for b in range(liczba_pudelek):
            seg = Y[b * n:(b + 1) * n]
            # dopasowanie prostej (MNK) — lokalny trend
            idx = list(range(n))
            sx = sum(idx); sy = sum(seg)
            sxx = sum(i * i for i in idx); sxy = sum(idx[i] * seg[i] for i in range(n))
            denom = n * sxx - sx * sx
            if denom == 0:
                continue
            a = (n * sxy - sx * sy) / denom        # nachylenie
            b0 = (sy - a * sx) / n                  # wyraz wolny
            reszty2 = sum((seg[i] - (a * i + b0)) ** 2 for i in range(n))
            rms_sum += math.sqrt(reszty2 / n)
        if liczba_pudelek > 0:
            F = rms_sum / liczba_pudelek
            if F > 0:
                log_n.append(math.log(n))
                log_F.append(math.log(F))

    if len(log_n) < 2:
        return None
    m = len(log_n)
    sx = sum(log_n); sy = sum(log_F)
    sxx = sum(v * v for v in log_n); sxy = sum(log_n[i] * log_F[i] for i in range(m))
    denom = m * sxx - sx * sx
    if denom == 0:
        return None
    slope = (m * sxy - sx * sy) / denom
    return round(max(0.01, min(0.99, slope)), 4)


def _py_permutation_entropy(close, period: int = 100, dim: int = 3, delay: int = 1) -> Optional[float]:
    """
    Permutation Entropy (Entropia Permutacyjna) — Bandt & Pompe (2002).
    Źródło: Phys. Rev. Lett. 88:174102, https://doi.org/10.1103/PhysRevLett.88.174102
            (synteza: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7597144/)

    Dla nowicjusza: mierzy ZŁOŻONOŚĆ szeregu czasowego patrząc na WZORCE PORZĄDKU
    (ordinal patterns), a nie na kierunek czy magnitudę ruchu. Dla każdego okna
    `dim` kolejnych wartości (z odstępem `delay`) liczymy permutację argsort —
    czyli który punkt jest najmniejszy, który średni, który największy. Z dim!
    możliwych wzorców liczymy ich częstość i entropię Shannona, znormalizowaną do
    [0,1] przez log(dim!).

      PE ≈ 1   → CHAOS: wszystkie wzorce równie częste → rynek efektywny, brak
                 przewagi (meta-brama mówi „nie handluj").
      PE niskie → przewidywalność: część wzorców „zakazana" (forbidden patterns) →
                 rynek nieefektywny, jest struktura → przewaga obecna.

    Dlaczego ORTOGONALNE do RSI/MACD (Prawo XVI): PE patrzy na STRUKTURĘ porządku,
    nie na poziom ceny ani kierunek. To inna OŚ informacji niż Trend (T), Zmienność
    (V) czy Momentum (M) — ~34% czulszy niż GARCH na klasteryzację zmienności.

    Zwraca PE ∈ [0,1]. None gdy mniej niż `period` świec (Prawo I — bez halucynacji).
    """
    import math
    from collections import Counter
    c = list(close)
    if len(c) < period:
        return None
    seria = c[-period:]
    span = delay * (dim - 1)
    if len(seria) <= span:
        return None
    wzorce = Counter()
    for i in range(len(seria) - span):
        okno = [seria[i + j * delay] for j in range(dim)]
        # permutacja argsort jako krotka — wzorzec porządkowy
        wzorzec = tuple(sorted(range(dim), key=lambda k: (okno[k], k)))
        wzorce[wzorzec] += 1
    total = sum(wzorce.values())
    if total == 0:
        return None
    entropia = -sum((n / total) * math.log(n / total) for n in wzorce.values())
    norm = math.log(math.factorial(dim))
    if norm == 0:
        return None
    return round(max(0.0, min(1.0, entropia / norm)), 4)


def _py_vpin(close, volume, n_buckets: int = 50, period: Optional[int] = None) -> Optional[float]:
    """
    VPIN — Volume-Synchronized Probability of Informed Trading (radar toksyczności przepływu).
    Źródło: Easley, López de Prado, O'Hara (2012), "Flow Toxicity and Liquidity in a
            High-Frequency World", Review of Financial Studies 25(5):1457,
            https://doi.org/10.1093/rfs/hhs053

    Dla nowicjusza: VPIN mierzy „toksyczność" przepływu zleceń — czy gracze
    poinformowani (wieloryby, market makerzy) handlują przeciwko tłumowi. Wysoki
    VPIN poprzedza kaskady likwidacji (flash crash 2010 miał ekstremalny VPIN).
    NIE mówi „w górę / w dół" — mówi „jak niebezpiecznie jest teraz handlować".

    Metoda (BVC — Bulk Volume Classification, klasyfikacja masowa wolumenu):
      1. Zmiany ceny dP[i] = close[i] − close[i−1].
      2. sigma = odchylenie std próbkowe dP (guard: zero → None).
      3. Frakcja kupna = Φ(dP/sigma), gdzie Φ to dystrybuanta standardowego rozkładu
         normalnego (przez math.erf). Frakcja sprzedaży = 1 − frakcja kupna.
      4. V_buy[i] = volume[i]·frakcja_kupna; V_sell[i] = volume[i]·frakcja_sprzedaży.
      5. Kubełkowanie: w tej wersji v1 używamy OSTATNICH `n_buckets` BARÓW jako
         kubełków (proxy „per-bar"). Standardowy VPIN dzieli na kubełki o RÓWNYM
         WOLUMENIE; proxy barowy jest prostszy i wystarcza na danych OHLCV bez
         danych tickowych. Świadomy kompromis (Prawo I — jawnie udokumentowany).
      6. VPIN = Σ|V_buy − V_sell| / Σ(V_buy + V_sell) ∈ [0,1].

    Zwraca VPIN ∈ [0,1]. None gdy mniej niż n_buckets+1 barów lub zerowy wolumen.
    """
    import math
    c = list(close)
    v = list(volume)
    if len(c) < n_buckets + 1 or len(v) < n_buckets + 1:
        return None
    # Zmiany ceny względem poprzedniego bara
    dP = [c[i] - c[i - 1] for i in range(1, len(c))]
    vol = v[1:]  # zrównaj długość z dP (volume bara, którego dotyczy zmiana)
    # Odchylenie std próbkowe dP na całym dostępnym oknie
    n = len(dP)
    srednia = sum(dP) / n
    war = sum((x - srednia) ** 2 for x in dP) / (n - 1) if n > 1 else 0.0
    sigma = math.sqrt(war)
    if sigma < 1e-12:
        return None
    # Ostatnie n_buckets barów jako kubełki (proxy barowy)
    dP_okno = dP[-n_buckets:]
    vol_okno = vol[-n_buckets:]
    sqrt2 = math.sqrt(2.0)
    sum_imbalance = 0.0
    sum_total = 0.0
    for dp, vbar in zip(dP_okno, vol_okno):
        frac_buy = 0.5 * (1.0 + math.erf((dp / sigma) / sqrt2))
        v_buy = vbar * frac_buy
        v_sell = vbar * (1.0 - frac_buy)
        sum_imbalance += abs(v_buy - v_sell)
        sum_total += v_buy + v_sell
    if sum_total < 1e-12:
        return None
    return round(max(0.0, min(1.0, sum_imbalance / sum_total)), 4)


def _py_wash_trading(volume, period: int = 100) -> Optional[float]:
    """
    Wash Trading Score — detekcja fałszywego wolumenu (Benford + zaokrąglenia).
    Źródło: Cong, Li, Tang, Yang (2023), "Crypto Wash Trading", NBER w30783,
            https://www.nber.org/papers/w30783

    Dla nowicjusza: Giełdy (szczególnie nieregulowane jak MEXC) sztucznie pompują
    wolumen handlując ze sobą własnymi botami. Zdradza je łamanie dwóch praw statystyki:
      1. Prawo Benforda — w naturalnych danych pierwsza cyfra wolumenu: 1 pojawia
         się 30%, 2=18%, 3=12% itd. (malejąco). Wash boty używają okrągłych liczb
         → 1, 2, 5 są przesadzone, 3, 4, 6–9 za rzadkie.
      2. Efekt zaokrągleń — legalne wolumeny są losowe; boty używają okrągłych
         liczb (100, 1000, 500) → ostatnie cyfry 0 i 5 są zbyt częste.

    Wynik ∈ [0,1]:
      0.0 = wolumen wydaje się naturalny (Benford OK, brak klasterowania)
      1.0 = silny sygnał wash trading (dwa testy czerwone jednocześnie)

    Algorytm:
      Benford: chi² odstępstwo od rozkładu Benforda na pierwszych cyfrach.
               chi²_znorm = min(chi²_obs / chi²_prog, 1.0), gdzie prog = χ²(0.01, df=8).
      Okrągłe: frakcja wolumenów kończących się na 0 lub 5 (po ×1 skalowaniu do int).
               Oczekiwane losowo: ~20%. Próg anomalii: 40%+.
      score = sqrt(benford_score × rounding_score) (geometryczna — oba muszą być wysokie).
    """
    import math
    vols = [v for v in list(volume)[-period:] if v and v > 0]
    if len(vols) < 30:
        return None

    # ── Test 1: Prawo Benforda (pierwsza cyfra wolumenu) ──────────────────────
    benford_expected = [0.30103, 0.17609, 0.12494, 0.09691, 0.07918,
                        0.06695, 0.05799, 0.05115, 0.04576]  # log10(1+1/d)
    counts = [0] * 9
    for v in vols:
        s = f"{int(v)}"
        if s and s[0].isdigit() and '1' <= s[0] <= '9':
            counts[int(s[0]) - 1] += 1
    n_benf = sum(counts)
    chi2 = 0.0
    if n_benf > 0:
        for i, cnt in enumerate(counts):
            expected = benford_expected[i] * n_benf
            if expected > 0:
                chi2 += (cnt - expected) ** 2 / expected
    # chi² krytyczne (α=0.01, df=8) ≈ 20.09; powyżej → anomalia
    chi2_prog = 20.09
    benford_score = min(1.0, chi2 / chi2_prog)

    # ── Test 2: Klasterowanie zaokrągleń (ostatnia cyfra skali) ───────────────
    # Skalujemy do najbardziej informacyjnego rzędu: interesują nas "okrągłe" wolumeny
    round_count = 0
    for v in vols:
        # Pierwsza cyfra po wiodących zerach: sprawdzamy czy relatywnie okrągły
        # (divisible by 10^(digits-2) — tj. trailing zeros relative to magnitude)
        iv = int(v)
        if iv <= 0:
            continue
        # Uproszczone: czy wolumen po podzieleniu przez najbliższą potęgę 10 ma resztę 0 lub 0.5
        digits = len(str(iv))
        scale = 10 ** max(0, digits - 2)
        last2 = iv % (scale * 10)
        if last2 == 0 or last2 == scale * 5:
            round_count += 1
    round_frac = round_count / len(vols)
    # Oczekiwane losowo: ~20%; progowa anomalia wash = 40%. Normalizujemy [0→0, 0.4+→1.0].
    rounding_score = min(1.0, max(0.0, (round_frac - 0.20) / 0.20))

    # ── Wynik łączny (geometryczny — oba testy muszą pokazywać anomalię) ──────
    score = math.sqrt(benford_score * rounding_score)
    return round(max(0.0, min(1.0, score)), 4)


def _py_choppiness(high, low, close, period: int = 14) -> Optional[float]:
    """
    Choppiness Index (CHOP) — mierzy, czy rynek TRENDUJE czy się KONSOLIDUJE.
    Wzór: 100 * log10(Σ TR(n) / (maxHigh(n) − minLow(n))) / log10(n).
    Zakres 0–100: >61.8 = konsolidacja (chop), <38.2 = silny trend.
    Dekoreluje z realized volatility (magnituda) — CHOP mierzy EFEKTYWNOŚĆ ruchu.
    """
    import math
    h, l, c = list(high), list(low), list(close)
    if len(c) < period + 1:
        return None
    # True Range dla ostatnich `period` barów
    tr = []
    for i in range(len(c) - period, len(c)):
        if i == 0:
            tr.append(h[i] - l[i])
        else:
            tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    suma_tr = sum(tr)
    max_h = max(h[-period:])
    min_l = min(l[-period:])
    rozpietosc = max_h - min_l
    if rozpietosc <= 0 or suma_tr <= 0:
        return None
    return round(100 * math.log10(suma_tr / rozpietosc) / math.log10(period), 2)


def _py_ulcer(close, period: int = 14) -> Optional[float]:
    """
    Ulcer Index (UI) — miara ryzyka SPADKOWEGO (głębokość i czas obsunięć).
    Wzór: sqrt(mean(drawdown_pct²)), gdzie drawdown liczony od kroczącego maksimum.
    Dekoreluje z ATR (symetryczny zakres) — UI karze tylko ruch W DÓŁ.
    Wyższy UI = większy ból posiadania → mniejsza bezpieczna dźwignia (kat. L).
    """
    import math
    c = list(close)
    if len(c) < period:          # UI potrzebuje dokładnie `period` świec (okno = c[-period:])
        return None
    okno = c[-period:]
    szczyt = okno[0]
    kwadraty = []
    for cena in okno:
        if cena > szczyt:
            szczyt = cena
        dd = (cena - szczyt) / szczyt * 100 if szczyt > 0 else 0.0
        kwadraty.append(dd * dd)
    return round(math.sqrt(sum(kwadraty) / len(kwadraty)), 4)


def _py_bubble_z(close, period: int = 200) -> Optional[float]:
    """
    Bubble-Z — odchylenie ceny od długoterminowego trendu w jednostkach σ (BIB-020, Harris rozdz. 28).

    Dla nowicjusza: bańka to cena oderwana od swojej długoterminowej "grawitacji".
    Mierzymy logarytmiczne odchylenie ceny od EMA-200 i normalizujemy je przez jego
    własną zmienność historyczną. Wynik to z-score:
      bubble_z > +3.5 → 🚨 skrajne przegrzanie (możliwa bańka, ryzyko pęknięcia)
      bubble_z < −3.5 → skrajne wyprzedanie (overshoot krachu, strefa odbicia)
      |bubble_z| < 2  → cena "informacyjna" (granice Fischera Blacka: 0.5×–2× wartości).

    Wzór: log_dev[i] = ln(close[i]) − ln(EMA200[i]); bubble_z = log_dev[-1] / std(log_dev).
    Annualizacja zbędna — to czysty z-score (bezwymiarowy).
    Źródło: Harris, "Trading and Exchanges" (2003), rozdz. 28; granice Fischera Blacka (1986).
    """
    import math
    c = _arr(close)
    if len(c) < period + 2:
        return None
    ema = talib.EMA(c, timeperiod=period)
    log_dev = []
    for i in range(len(c)):
        e = ema[i]
        if e is None or np.isnan(e) or e <= 0 or c[i] <= 0:
            continue
        log_dev.append(math.log(c[i]) - math.log(e))
    # z-score wymaga sensownej próbki odchyleń (EMA-200 ma warmup 199 barów,
    # więc dla wiarygodnego σ potrzeba ~period+15 barów). Mniej → None (Prawo I).
    if len(log_dev) < 15:
        return None
    n = len(log_dev)
    mean = sum(log_dev) / n
    var = sum((x - mean) ** 2 for x in log_dev) / (n - 1)
    std = math.sqrt(var)
    if std < 1e-12:
        return 0.0
    return round(log_dev[-1] / std, 4)


def _py_vov(high, low, close, period: int = 14, window: int = 20) -> Optional[float]:
    """
    VoV — Volatility-of-Volatility (BIB-020, Harris rozdz. 28): prekursor krachu.

    Dla nowicjusza: przed krachem sama zmienność staje się NIESTABILNA — ATR nie tylko
    rośnie, ale skacze z baru na bar (rozpad konsensusu cenowego). Stabilna wysoka vol
    to co innego niż chaotyczna vol. Mierzymy współczynnik zmienności ATR:
      VoV = std(ATR, window) / mean(ATR, window)
      VoV > 1.2 → 🚨 skrajna niestabilność (kill-switch), VoV < 0.5 → spokój.

    Zwraca współczynnik zmienności ATR-14 z ostatnich `window` barów (bezwymiarowy).
    Źródło: Harris, "Trading and Exchanges" (2003), rozdz. 28 (portfolio insurance / "who would buy?").
    """
    import math
    atr = talib.ATR(_arr(high), _arr(low), _arr(close), timeperiod=period)
    vals = [x for x in atr[-window:] if x is not None and not np.isnan(x)]
    if len(vals) < max(5, window // 2):
        return None
    n = len(vals)
    mean = sum(vals) / n
    if mean < 1e-12:
        return None
    var = sum((x - mean) ** 2 for x in vals) / (n - 1)
    return round(math.sqrt(var) / mean, 4)


def _py_ret_ar1(close, window: int = 20) -> Optional[float]:
    """
    AR1 — autokorelacja zwrotów lag-1 (BIB-020, Harris rozdz. 28): wskaźnik refleksywności.

    Dla nowicjusza: w rynku efektywnym kolejne zwroty są nieskorelowane (AR1≈0).
    Gdy AR1 robi się DODATNI, ceny napędzają same siebie (kaskada momentum / margin calls):
      AR1 > +0.40 → 🚨 kaskada (dynamika krachu lub paraboli) — kill-switch
      AR1 > +0.25 → refleksywność (reżim momentum, tłum dogania)
      AR1 < −0.20 → silna rewersja (stabilny, efektywny rynek).

    Wzór: r[i] = close[i]/close[i-1] − 1; AR1 = corr(r[t], r[t-1]) z ostatnich `window` par.
    Źródło: Harris, "Trading and Exchanges" (2003), rozdz. 28; Soros (refleksywność).
    """
    import math
    c = list(close)
    if len(c) < window + 2:
        return None
    rets = [c[i] / c[i - 1] - 1.0 for i in range(1, len(c)) if c[i - 1] > 0]
    rets = rets[-(window + 1):]
    if len(rets) < window:
        return None
    x = rets[1:]      # r[t]
    y = rets[:-1]     # r[t-1]
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    vx = sum((v - mx) ** 2 for v in x)
    vy = sum((v - my) ** 2 for v in y)
    if vx < 1e-18 or vy < 1e-18:
        return 0.0
    return round(cov / math.sqrt(vx * vy), 4)


def _py_value_z(close, period: int = 200) -> Optional[float]:
    """
    Value-Z — odchylenie ceny od długoterminowej wartości godziwej w jednostkach σ
    (BIB-020, Harris rozdz. 16 "Value Traders").

    Dla nowicjusza: value traderzy wchodzą dopiero, gdy cena ODERWAŁA się materialnie
    od swojej wartości godziwej (ich "outside spread"). Kotwicą wartości jest SMA-200,
    a miarą oderwania — z-score: ile odchyleń standardowych cena jest poniżej/powyżej.
      Value-Z < −2.0 → wyprzedanie (kandydat LONG, rewersja do wartości)
      Value-Z > +2.0 → wykupienie (kandydat SHORT)
      |Value-Z| < 1.5 → cena blisko wartości (NEUTRAL).

    Wzór: z = (close[-1] − SMA_period) / std(close[-period:]).
    Źródło: Harris, "Trading and Exchanges" (2003), rozdz. 16; wizja W-273.
    """
    import math
    c = list(close)
    if len(c) < period:
        return None
    okno = c[-period:]
    n = len(okno)
    mean = sum(okno) / n
    var = sum((x - mean) ** 2 for x in okno) / (n - 1)
    std = math.sqrt(var)
    if std < 1e-12:
        return 0.0
    return round((c[-1] - mean) / std, 4)


def _py_moma_z(close, period: int = 200) -> Optional[float]:
    """
    MoMA-Z — odchylenie ceny od ŚREDNIEJ ŚREDNICH (Moving average of Moving Averages),
    wieloskalowa kotwica wartości (BIB-020, Harris rozdz. 16; wizja W-273).

    Dla nowicjusza: pojedyncza SMA-200 jest mocno opóźniona. Value traderzy patrzą na
    wartość w wielu horyzontach naraz. MoMA = średnia z SMA-20/50/100/200 — łączy
    krótki, średni i długi obraz. z = (close − MoMA) / std(close, 200).
    Komplementarny do Value-Z (inna kotwica) — krzyżowe potwierdzenie rewersji.

    Wzór: MoMA = mean(SMA20, SMA50, SMA100, SMA200); z = (close[-1] − MoMA)/std(close[-200:]).
    Źródło: Harris, "Trading and Exchanges" (2003), rozdz. 16; wizja W-273.
    """
    import math
    c = list(close)
    if len(c) < period:
        return None

    def _sma(seria, okr):
        return sum(seria[-okr:]) / okr

    moma = (_sma(c, 20) + _sma(c, 50) + _sma(c, 100) + _sma(c, period)) / 4.0
    okno = c[-period:]
    n = len(okno)
    mean = sum(okno) / n
    var = sum((x - mean) ** 2 for x in okno) / (n - 1)
    std = math.sqrt(var)
    if std < 1e-12:
        return 0.0
    return round((c[-1] - moma) / std, 4)


def _py_ou_halflife(close, period: int = 50) -> Optional[float]:
    """
    OU Half-Life — czas połowicznego powrotu do średniej (BIB-020, Harris rozdz. 16; wizja W-274).

    Dla nowicjusza: gdy value traderzy są aktywni, rynek jest "sprężysty" (resilient) —
    cena szybko wraca do średniej po szoku. Mierzymy to modelem Ornsteina-Uhlenbecka:
    regresja Δx na x dla spreadu x=(price − SMA_period). Współczynnik β<0 = rewersja;
    half-life = −ln(2)/β to liczba barów do przebycia połowy drogi powrotu.
      half-life KRÓTKI (<~20 barów) → silna rewersja (value traderzy obecni) → RANGING
      half-life DŁUGI (>~40 barów)  → słaba rewersja / trend dominuje → TREND_STRONG

    Zwraca half-life w barach (float). Gdy β≥0 (brak rewersji, dynamika trendu) → 9999.0
    (sygnał "bardzo długi" = trend). None gdy za mało danych.
    Źródło: Harris (2003) rozdz. 16; Chan "Algorithmic Trading" (OU half-life); wizja W-274.
    """
    import math
    c = list(close)
    if len(c) < period + 5:
        return None
    okno = c[-period:]
    n = len(okno)
    sma = sum(okno) / n
    x = [v - sma for v in okno]          # spread wokół średniej
    lag = x[:-1]
    delta = [x[i] - x[i - 1] for i in range(1, len(x))]
    m = len(lag)
    mean_lag = sum(lag) / m
    var_lag = sum((v - mean_lag) ** 2 for v in lag)
    if var_lag < 1e-12:
        return None
    mean_delta = sum(delta) / m
    cov = sum((lag[i] - mean_lag) * (delta[i] - mean_delta) for i in range(m))
    beta = cov / var_lag
    if beta >= 0:
        return 9999.0                    # brak rewersji → "nieskończenie długi" = trend
    return round(-math.log(2) / beta, 4)


def _py_variance_ratio(close, k: int = 4, period: int = 100) -> Optional[float]:
    """
    Variance Ratio (Lo-MacKinlay) — dekompozycja zmienności: trwała (trend) vs przejściowa
    (szum/rewersja) (BIB-020, Harris rozdz. 20/16; wizja W-263).

    Dla nowicjusza: jeśli zwroty są niezależne (błądzenie losowe), wariancja zwrotu
    k-okresowego = k × wariancja zwrotu 1-okresowego, więc VR=1. Gdy ceny TRENDUJĄ
    (dodatnia autokorelacja), wariancja rośnie SZYBCIEJ niż liniowo → VR>1. Gdy REWERTUJĄ
    (ujemna autokorelacja), wolniej → VR<1. To kanoniczny "master-switch" reżimu:
      VR > 1.05 → trend (zmienność trwała) → TREND_STRONG
      VR < 0.95 → rewersja (zmienność przejściowa) → RANGING

    Wzór: VR(k) = Var(r_k) / (k · Var(r_1)), r = logarytmiczne zwroty na oknie `period`.
    Źródło: Lo & MacKinlay (1988); Harris (2003) rozdz. 20; wizja W-263.
    """
    import math
    c = list(close)
    if len(c) < period or len(c) < k + 2:
        return None
    okno = c[-period:]
    logp = [math.log(v) for v in okno if v > 0]
    if len(logp) < k + 2:
        return None
    r1 = [logp[i] - logp[i - 1] for i in range(1, len(logp))]
    rk = [logp[i] - logp[i - k] for i in range(k, len(logp))]
    n1 = len(r1)
    nk = len(rk)
    if n1 < 2 or nk < 2:
        return None
    m1 = sum(r1) / n1
    var1 = sum((v - m1) ** 2 for v in r1) / (n1 - 1)
    if var1 < 1e-18:
        return None
    mk = sum(rk) / nk
    vark = sum((v - mk) ** 2 for v in rk) / (nk - 1)
    return round(vark / (k * var1), 4)


def _py_supertrend(high, low, close, period: int = 10, multiplier: float = 3.0):
    """
    Supertrend — pure Python, bez TA-Lib.
    Zwraca (st_value, direction, st_value_prev, direction_prev).
    direction: 1=bullish, -1=bearish.
    """
    n = len(close)
    if n < period + 2:
        return None, None, None, None

    # ATR Wilder (EMA-style)
    trs = [max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
           for i in range(1, n)]
    atr = [sum(trs[:period]) / period]
    for tr in trs[period:]:
        atr.append((atr[-1] * (period - 1) + tr) / period)

    offset = period  # atr[0] odpowiada bar-indeksowi = period
    basic_upper = [(high[offset + i] + low[offset + i]) / 2 + multiplier * atr[i]
                   for i in range(len(atr))]
    basic_lower = [(high[offset + i] + low[offset + i]) / 2 - multiplier * atr[i]
                   for i in range(len(atr))]

    final_upper = [basic_upper[0]]
    final_lower = [basic_lower[0]]
    for i in range(1, len(atr)):
        prev_c = close[offset + i - 1]
        fu = basic_upper[i] if basic_upper[i] < final_upper[-1] or prev_c > final_upper[-1] else final_upper[-1]
        fl = basic_lower[i] if basic_lower[i] > final_lower[-1] or prev_c < final_lower[-1] else final_lower[-1]
        final_upper.append(fu)
        final_lower.append(fl)

    direction = []
    for i in range(len(atr)):
        c = close[offset + i]
        if not direction:
            direction.append(1 if c > final_lower[i] else -1)
        else:
            prev_dir = direction[-1]
            if prev_dir == 1:
                direction.append(1 if c > final_upper[i] else -1)
            else:
                direction.append(-1 if c < final_lower[i] else 1)

    st_vals = [final_lower[i] if direction[i] == 1 else final_upper[i] for i in range(len(direction))]
    return (
        st_vals[-1], direction[-1],
        st_vals[-2] if len(st_vals) >= 2 else None,
        direction[-2] if len(direction) >= 2 else None,
    )


def _py_ichimoku(high, low):
    """
    Ichimoku Cloud — ostatnie wartości z podanej serii.
    Wymaga min. 52 barów (Senkou B potrzebuje 52 obserwacji).
    """
    def _hl2(h, l, period):
        if len(h) < period:
            return None
        return (max(h[-period:]) + min(l[-period:])) / 2

    tenkan = _hl2(high, low, 9)
    kijun = _hl2(high, low, 26)
    senkou_b = _hl2(high, low, 52)
    senkou_a = (tenkan + kijun) / 2 if tenkan is not None and kijun is not None else None
    return {
        "ICHIMOKU_TENKAN": tenkan,
        "ICHIMOKU_KIJUN": kijun,
        "ICHIMOKU_SENKOU_A": senkou_a,
        "ICHIMOKU_SENKOU_B": senkou_b,
    }


@dataclass
class CalcResult:
    """Wynik obliczenia z pieczątką audytu (Prawo XIII — audytowalność)."""
    indicator: str
    params: Dict[str, Any]
    value: Any                      # ostatnia wartość lub słownik wartości
    source: str = SOURCE_TAG
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sha256: str = ""

    def __post_init__(self):
        if not self.sha256:
            payload = json.dumps(
                {"indicator": self.indicator, "params": self.params,
                 "value": self.value, "source": self.source, "timestamp": self.timestamp},
                sort_keys=True, ensure_ascii=False, default=str,
            )
            self.sha256 = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    def as_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class CalculatorGateway:
    """
    Jedyne wejście do matematyki w Imperium.
      - compute(name, **params) → CalcResult (deterministyczny TA-Lib + pieczątka)
      - nieznany wskaźnik = twarde odrzucenie (guardrail — Prawo IX)
      - każde obliczenie trafia do logu audytu (Prawo XIII)
    """

    def __init__(self):
        self._registry: Dict[str, Callable[..., Any]] = {
            # ── TA-Lib: podstawowe ─────────────────────────────────────────────
            "RSI":      lambda close, period=14: _last_valid(talib.RSI(_arr(close), timeperiod=period)),
            "EMA":      lambda close, period=20: _last_valid(talib.EMA(_arr(close), timeperiod=period)),
            "SMA":      lambda close, period=20: _last_valid(talib.SMA(_arr(close), timeperiod=period)),
            "ATR":      lambda high, low, close, period=14: _last_valid(talib.ATR(_arr(high), _arr(low), _arr(close), timeperiod=period)),
            "MACD":     self._macd,
            "BBANDS":   self._bbands,

            # ── TA-Lib: EMA na konkretnych okresach (dla neuronów crossover) ──
            "EMA_9":    lambda close: _last_valid(talib.EMA(_arr(close), timeperiod=9)),
            "EMA_21":   lambda close: _last_valid(talib.EMA(_arr(close), timeperiod=21)),
            "EMA_50":   lambda close: _last_valid(talib.EMA(_arr(close), timeperiod=50)),
            "EMA_200":  lambda close: _last_valid(talib.EMA(_arr(close), timeperiod=200)),

            # ── TA-Lib: PREV — wartość z poprzedniego baru (dla crossoverów) ──
            "RSI_PREV":     lambda close, period=14: _second_last_valid(talib.RSI(_arr(close), timeperiod=period)),
            "EMA_9_PREV":   lambda close: _second_last_valid(talib.EMA(_arr(close), timeperiod=9)),
            "EMA_21_PREV":  lambda close: _second_last_valid(talib.EMA(_arr(close), timeperiod=21)),
            "EMA_50_PREV":  lambda close: _second_last_valid(talib.EMA(_arr(close), timeperiod=50)),
            "EMA_200_PREV": lambda close: _second_last_valid(talib.EMA(_arr(close), timeperiod=200)),
            "MACD_HIST_PREV": self._macd_hist_prev,

            # ── TA-Lib: ADX + kierunkowe ───────────────────────────────────────
            "ADX_14":   lambda high, low, close, period=14: _last_valid(talib.ADX(_arr(high), _arr(low), _arr(close), timeperiod=period)),
            "DI_PLUS":  lambda high, low, close, period=14: _last_valid(talib.PLUS_DI(_arr(high), _arr(low), _arr(close), timeperiod=period)),
            "DI_MINUS": lambda high, low, close, period=14: _last_valid(talib.MINUS_DI(_arr(high), _arr(low), _arr(close), timeperiod=period)),

            # ── TA-Lib: oscylatory momentum ────────────────────────────────────
            "WILLIAMS_R": lambda high, low, close, period=14: _last_valid(talib.WILLR(_arr(high), _arr(low), _arr(close), timeperiod=period)),
            # StochRSI: bierzemy linię %K (fastk) 0–100. talib.STOCHRSI → (fastk, fastd).
            "STOCHRSI":   lambda close, period=14: _last_valid(talib.STOCHRSI(_arr(close), timeperiod=period, fastk_period=5, fastd_period=3, fastd_matype=0)[0]),
            # TRIX: potrójnie wygładzone ROC (momentum z filtracją szumu)
            "TRIX":       lambda close, period=15: _last_valid(talib.TRIX(_arr(close), timeperiod=period)),
            "TRIX_PREV":  lambda close, period=15: _second_last_valid(talib.TRIX(_arr(close), timeperiod=period)),

            # ── Pure-Python: Awesome Oscillator (TA-Lib nie ma) ───────────────
            "AO":      lambda high, low: _py_awesome(high, low)[0],
            "AO_PREV": lambda high, low: _py_awesome(high, low)[1],

            # ── Pure-Python: Hull Moving Average (TA-Lib nie ma) ──────────────
            "HMA":      lambda close, period=16: _py_hma(close, period)[0],
            "HMA_PREV": lambda close, period=16: _py_hma(close, period)[1],

            # ── Pure-Python: Accelerator Oscillator (TA-Lib nie ma) ───────────
            "AC":      lambda high, low: _py_accelerator(high, low)[0],
            "AC_PREV": lambda high, low: _py_accelerator(high, low)[1],

            # ── Pure-Python: Donchian Channel (TA-Lib nie ma) ─────────────────
            "DONCHIAN": lambda high, low, period=20: _py_donchian(high, low, period),

            # ── Pure-Python: Relative Volume (TA-Lib nie ma) ──────────────────
            "RVOL":      lambda volume, period=20: _py_rvol(volume, period),

            # ── Pure-Python: Historical/Realized Volatility (TA-Lib nie ma) ──
            "HIST_VOL":  lambda close, period=20: _py_hist_vol(close, period),

            # ── Pure-Python: Yang-Zhang OHLC Volatility (TA-Lib nie ma) ───────
            # ~14× efektywniejszy estymator annualizowanej vol niż HIST_VOL (close-only).
            "YANG_ZHANG": lambda open, high, low, close, period=20: _py_yang_zhang(open, high, low, close, period),

            # ── Pure-Python: Hurst-DFA — pamięć długiego zasięgu / meta-brama (kat. H, W-053) ──
            "HURST_DFA": lambda close, period=100: _py_hurst_dfa(close, period),

            # ── Pure-Python: Permutation Entropy — meta-brama chaosu (kat. N, W-054) ──
            "PERMUTATION_ENTROPY": lambda close, period=100, dim=3, delay=1: _py_permutation_entropy(close, period, dim, delay),

            # ── Pure-Python: VPIN — radar toksycznego przepływu (kat. Z, W-036) ──
            "VPIN": lambda close, volume, n_buckets=50: _py_vpin(close, volume, n_buckets),

            # ── Pure-Python: Wash Trading Score — Benford + zaokrąglenia (kat. O, W-061) ──
            "WASH_TRADING": lambda volume, period=100: _py_wash_trading(volume, period),

            # ── Pure-Python: Choppiness Index — trend vs konsolidacja (kat. V) ──
            "CHOPPINESS": lambda high, low, close, period=14: _py_choppiness(high, low, close, period),

            # ── Pure-Python: Ulcer Index — ryzyko spadkowe (kat. L) ───────────
            "ULCER":     lambda close, period=14: _py_ulcer(close, period),

            # ── Pure-Python: W-278 bubble/crash kill-switch (kat. Z, BIB-020 Harris rozdz. 28) ──
            "BUBBLE_Z":   lambda close, period=200: _py_bubble_z(close, period),
            "VOV":        lambda high, low, close, period=14, window=20: _py_vov(high, low, close, period, window),
            "RET_AR1":    lambda close, window=20: _py_ret_ar1(close, window),

            # ── Pure-Python: W-273 value convergence (kat. M, BIB-020 Harris rozdz. 16) ──
            "VALUE_Z":    lambda close, period=200: _py_value_z(close, period),
            "MOMA_Z":     lambda close, period=200: _py_moma_z(close, period),

            # ── Pure-Python: W-274/W-263 master-switch reżimu (BIB-020 Harris rozdz. 16/20) ──
            "OU_HALFLIFE":    lambda close, period=50: _py_ou_halflife(close, period),
            "VARIANCE_RATIO": lambda close, k=4, period=100: _py_variance_ratio(close, k, period),

            # ── TA-Lib: wolumen ────────────────────────────────────────────────
            "OBV":          lambda close, volume: _last_valid(talib.OBV(_arr(close), _arr(volume))),
            "OBV_EMA_20":   lambda close, volume: _last_valid(talib.EMA(talib.OBV(_arr(close), _arr(volume)), timeperiod=20)),
            "VOLUME_MA20":  lambda volume: _last_valid(talib.SMA(_arr(volume), timeperiod=20)),
            "VOLUME_PREV":  lambda volume: _second_last_valid(talib.SMA(_arr(volume), timeperiod=1)),

            # ── TA-Lib: ATR Deviation = (close[-1] - EMA_20) / ATR ────────────
            "ATR_DEVIATION": self._atr_deviation,

            # ── Pure-Python: VWAP (TA-Lib nie ma) ─────────────────────────────
            "VWAP":     lambda high, low, close, volume: _py_vwap(high, low, close, volume),
            "VWAP_STD": lambda high, low, close, volume: _py_vwap_std(high, low, close, volume),

            # ── Pure-Python: Supertrend (TA-Lib nie ma) ───────────────────────
            "SUPERTREND":          self._supertrend_value,
            "SUPERTREND_DIR":      self._supertrend_dir,
            "SUPERTREND_DIR_PREV": self._supertrend_dir_prev,

            # ── Pure-Python: Ichimoku (TA-Lib nie ma) ─────────────────────────
            "ICHIMOKU": self._ichimoku,
        }
        self.audit_log: List[CalcResult] = []

    # ── Metody pomocnicze dla złożonych wskaźników ────────────────────────────

    @staticmethod
    def _macd(close, fast=12, slow=26, signal=9) -> Dict[str, float]:
        macd, sig, hist = talib.MACD(_arr(close), fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return {"MACD": _last_valid(macd), "SIGNAL": _last_valid(sig), "HISTOGRAM": _last_valid(hist),
                "MACD_PREV": _second_last_valid(macd), "SIGNAL_PREV": _second_last_valid(sig),
                "HISTOGRAM_PREV": _second_last_valid(hist)}

    @staticmethod
    def _macd_hist_prev(close, fast=12, slow=26, signal=9):
        _, _, hist = talib.MACD(_arr(close), fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return _second_last_valid(hist)

    @staticmethod
    def _bbands(close, period=20, std=2.0) -> Dict[str, float]:
        up, mid, low = talib.BBANDS(_arr(close), timeperiod=period, nbdevup=std, nbdevdn=std, matype=0)
        return {"UPPER": _last_valid(up), "MIDDLE": _last_valid(mid), "LOWER": _last_valid(low)}

    @staticmethod
    def _atr_deviation(high, low, close, ema_period=20, atr_period=14):
        """(close[-1] - EMA_20) / ATR — znormalizowane odchylenie od średniej."""
        ema_arr = talib.EMA(_arr(close), timeperiod=ema_period)
        atr_arr = talib.ATR(_arr(high), _arr(low), _arr(close), timeperiod=atr_period)
        ema = _last_valid(ema_arr)
        atr = _last_valid(atr_arr)
        c = float(close[-1]) if hasattr(close, '__len__') else float(close)
        if ema is None or atr is None or atr == 0:
            return None
        return round((c - ema) / atr, 4)

    @staticmethod
    def _supertrend_value(high, low, close, period=10, multiplier=3.0):
        st, _, _, _ = _py_supertrend(list(high), list(low), list(close), period, multiplier)
        return st

    @staticmethod
    def _supertrend_dir(high, low, close, period=10, multiplier=3.0):
        _, d, _, _ = _py_supertrend(list(high), list(low), list(close), period, multiplier)
        return d

    @staticmethod
    def _supertrend_dir_prev(high, low, close, period=10, multiplier=3.0):
        _, _, _, dp = _py_supertrend(list(high), list(low), list(close), period, multiplier)
        return dp

    @staticmethod
    def _ichimoku(high, low) -> Dict[str, Any]:
        return _py_ichimoku(list(high), list(low))

    def available(self) -> List[str]:
        return sorted(self._registry.keys())

    def compute_series(self, indicator: str, **kwargs):
        """Zwraca PEŁNĄ serię wskaźnika (do backtestów na dużych danych).
        Nadal jedyne wejście do matematyki — Prawo I zachowane. Brak lookahead:
        wartość TA-Lib przy indeksie i zależy tylko od danych do i włącznie."""
        name = indicator.upper()
        series_fns = {
            "RSI": lambda close, period=14: talib.RSI(_arr(close), timeperiod=period),
            "EMA": lambda close, period=20: talib.EMA(_arr(close), timeperiod=period),
            "SMA": lambda close, period=20: talib.SMA(_arr(close), timeperiod=period),
        }
        if name not in series_fns:
            raise ValueError(f"Brama (seria) odrzuca '{indicator}': dostępne {sorted(series_fns)}")
        arr = series_fns[name](**kwargs)
        n = int(len(kwargs.get("close", [])))
        logger.info(f"[Brama] {name}(seria) period={kwargs.get('period')} input_len={n}")
        return arr

    def compute(self, indicator: str, **kwargs) -> CalcResult:
        name = indicator.upper()
        if name not in self._registry:
            # GUARDRAIL (Prawo IX): nic spoza rejestru. AI nie wymyśla obliczeń.
            raise ValueError(
                f"Brama odrzuca '{indicator}': nieznane obliczenie. Dostępne: {self.available()}"
            )
        value = self._registry[name](**kwargs)
        # Do audytu zapisujemy tylko skalarne parametry (bez wielkich tablic danych).
        params = {k: v for k, v in kwargs.items() if isinstance(v, (int, float, str, bool))}
        series = kwargs.get("close")
        if series is not None:
            params["input_len"] = int(len(series))
        zrodlo = SOURCE_TAG_PY if name in _PURE_PYTHON_INDICATORS else SOURCE_TAG
        result = CalcResult(indicator=name, params=params, value=value, source=zrodlo)
        self.audit_log.append(result)
        logger.info(f"[Brama] {name} {params} = {value} | hash={result.sha256}")
        return result

    def export_audit(self) -> str:
        """Pełny log audytu w JSON (Prawo XIII — audytowalność)."""
        return json.dumps([asdict(r) for r in self.audit_log], ensure_ascii=False, indent=2)


def main():
    logger.info("=== Brama Kalkulatora v1.0 — Imperium (fundament Prawa I) ===")
    rng = np.random.default_rng(42)
    close = 50000 + np.cumsum(rng.normal(0, 150, 300))
    high = close + rng.uniform(0, 100, 300)
    low = close - rng.uniform(0, 100, 300)

    gw = CalculatorGateway()
    logger.info(f"Dostępne obliczenia: {gw.available()}")

    gw.compute("RSI", close=close, period=14)
    gw.compute("EMA", close=close, period=50)
    gw.compute("MACD", close=close)
    gw.compute("ATR", high=high, low=low, close=close)

    # Kontrakt JSON (to dostaje AI — i tylko interpretuje):
    last = gw.audit_log[0]
    logger.info(f"Kontrakt dla AI: {last.as_json()}")

    # Guardrail: próba nielegalnego obliczenia
    try:
        gw.compute("ZMYSLONY_WSKAZNIK", close=close)
    except ValueError as e:
        logger.info(f"[TEST guardrail] poprawnie odrzucono: {e}")

    logger.info(f"Audyt: {len(gw.audit_log)} obliczeń zalogowanych.")
    print("\n✅ Brama Kalkulatora v1.0 — demo zakończone (Prawo I w kodzie).")


if __name__ == "__main__":
    main()
