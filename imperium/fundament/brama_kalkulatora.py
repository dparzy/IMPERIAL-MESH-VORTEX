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
    potrzeba = slow + sma_ac + 1
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
    if len(c) < period + 1:
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

            # ── Pure-Python: Choppiness Index — trend vs konsolidacja (kat. V) ──
            "CHOPPINESS": lambda high, low, close, period=14: _py_choppiness(high, low, close, period),

            # ── Pure-Python: Ulcer Index — ryzyko spadkowe (kat. L) ───────────
            "ULCER":     lambda close, period=14: _py_ulcer(close, period),

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
        result = CalcResult(indicator=name, params=params, value=value)
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
