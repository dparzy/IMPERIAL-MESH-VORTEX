"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       ToolForge — IndicatorFactory v5 + API Toolkit v2.0                     ║
║  Autor: Jack (Wizjoner, Architekt, Wynalazca, Magik)                        ║
║  Licencja: Kingdom Pixel — wszelkie prawa autorskie                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA (Zasada 11) ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-TOOLS-208                                                   |
| Nazwa oryginalna    | ToolForge — IndicatorFactory + API Toolkit                   |
| Nazwa w Królestwie  | ToolForge (Kuźnia Narzędzi)                                   |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/TOOLS-208_ToolForge.py               |
| Kategoria           | TOOLS / Wskaźniki i sygnały                                   |
| Wpływ na Królestwo  | Jedyne źródło kanonicznych, deterministycznych wskaźników     |
|                     | (TA-Lib) dla całego Królestwa. Fundament wykonawczy Zasady 75.|
| Powiązane moduły    | N-BRAIN-026, N-CORE-XX (Calculator Gateway), N-BACK-210,      |
|                     | N-EYES-028                                                    |

CHANGELOG:
  v2.0 (2026-05-28) — ZGODNOŚĆ Z ZASADĄ 75. Cała matematyka (RSI/MACD/BBANDS/ATR/
        SMA/EMA) przeniesiona z ręcznego NumPy na TA-Lib (deterministyczny rdzeń C).
        Stary RSI używał zwykłej średniej kroczącej zamiast wygładzania Wildera →
        dawał wartości NIEKANONICZNE. Teraz wynik = referencyjny TA-Lib.
  v1.0 — wersja wyjściowa (ręczne NumPy, niezgodna z Zasadą 75).

Mechanizm:
1. INDICATOR FACTORY — RSI, MACD, BBANDS, ATR, Supertrend (wszystko z TA-Lib).
2. SIGNAL GENERATOR — sygnały z ochroną przed look-ahead bias i wartościami NaN.
3. ZASADA 75 — moduł NIE liczy matematyki samodzielnie; deleguje do TA-Lib.
═════════════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import logging
from typing import List, Dict

# ── Zasada 75: deterministyczny rdzeń obliczeń. Bez TA-Lib moduł NIE działa celowo. ──
try:
    import talib
except ImportError as e:
    raise RuntimeError(
        "N-TOOLS-208 wymaga TA-Lib (Zasada 75 — deterministyczny rdzeń C). "
        "Instalacja: `pip install TA-Lib`. "
        "Świadomie BRAK fallbacku do ręcznej matematyki — to gwarantuje wartości kanoniczne."
    ) from e

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("ToolForge")


def _arr(x) -> np.ndarray:
    """Konwersja na float64 wymagany przez TA-Lib."""
    return np.asarray(x, dtype=np.float64)


def _valid(x) -> bool:
    """True, jeśli wartość jest liczbą (nie NaN z okresu rozgrzewania TA-Lib)."""
    return x is not None and not (isinstance(x, float) and np.isnan(x))


class IndicatorFactory:
    """
    ZASADA 75: każda zwracana liczba pochodzi z TA-Lib (rdzeń C, deterministyczny).
    Żadnych ręcznych, niekanonicznych implementacji wskaźników.
    Każda metoda zwraca listę długości == len(wejścia); okres rozgrzewania = NaN.
    """

    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> List[float]:
        return talib.RSI(_arr(prices), timeperiod=period).tolist()

    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        macd_line, signal_line, hist = talib.MACD(
            _arr(prices), fastperiod=fast, slowperiod=slow, signalperiod=signal
        )
        return {"MACD": macd_line.tolist(), "SIGNAL": signal_line.tolist(), "HISTOGRAM": hist.tolist()}

    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[float]]:
        upper, middle, lower = talib.BBANDS(
            _arr(prices), timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev, matype=0
        )
        return {"MIDDLE": middle.tolist(), "UPPER": upper.tolist(), "LOWER": lower.tolist()}

    @staticmethod
    def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
        return talib.ATR(_arr(highs), _arr(lows), _arr(closes), timeperiod=period).tolist()

    @staticmethod
    def supertrend(highs: List[float], lows: List[float], closes: List[float],
                   period: int = 7, multiplier: float = 3.0) -> Dict[str, List[float]]:
        # ATR pochodzi z TA-Lib (deterministyczny); pasma to trywialna kombinacja arytmetyczna.
        atr = _arr(IndicatorFactory.atr(highs, lows, closes, period))
        hl2 = (_arr(highs) + _arr(lows)) / 2.0
        upper = (hl2 + multiplier * atr).tolist()
        lower = (hl2 - multiplier * atr).tolist()
        return {"UPPER_BAND": upper, "LOWER_BAND": lower}

    @staticmethod
    def sma(prices: List[float], period: int) -> List[float]:
        return talib.SMA(_arr(prices), timeperiod=period).tolist()

    @staticmethod
    def ema(prices: List[float], period: int) -> List[float]:
        return talib.EMA(_arr(prices), timeperiod=period).tolist()


class SignalGenerator:
    """Sygnały zbudowane wyłącznie na kanonicznych wartościach TA-Lib (Zasada 75)."""

    def __init__(self, prices: List[float], highs: List[float], lows: List[float]):
        self.prices = prices
        self.highs = highs
        self.lows = lows

    def golden_cross(self, fast: int = 50, slow: int = 200) -> bool:
        if len(self.prices) < slow + 2:
            return False
        sma_fast = IndicatorFactory.sma(self.prices, fast)
        sma_slow = IndicatorFactory.sma(self.prices, slow)
        if not all(_valid(v) for v in (sma_fast[-2], sma_fast[-1], sma_slow[-2], sma_slow[-1])):
            return False
        return sma_fast[-2] < sma_slow[-2] and sma_fast[-1] > sma_slow[-1]

    def rsi_oversold(self, period: int = 14, threshold: float = 35) -> bool:
        rsi = IndicatorFactory.rsi(self.prices, period)
        return _valid(rsi[-1]) and rsi[-1] < threshold

    def macd_bullish_cross(self) -> bool:
        macd = IndicatorFactory.macd(self.prices)
        m2, m1 = macd["MACD"][-2], macd["MACD"][-1]
        s2, s1 = macd["SIGNAL"][-2], macd["SIGNAL"][-1]
        if not all(_valid(v) for v in (m2, m1, s2, s1)):
            return False
        return m2 < s2 and m1 > s1


def main():
    logger.info("=== ToolForge v2.0 Demo (Zasada 75 — TA-Lib) ===")
    np.random.seed(42)
    prices = [50000 + i * 50 + np.random.uniform(-200, 200) for i in range(300)]
    highs = [p + np.random.uniform(0, 100) for p in prices]
    lows = [p - np.random.uniform(0, 100) for p in prices]

    rsi = IndicatorFactory.rsi(prices)
    macd = IndicatorFactory.macd(prices)
    bb = IndicatorFactory.bollinger_bands(prices)
    sig = SignalGenerator(prices, highs, lows)

    logger.info(f"RSI[last]: {rsi[-1]:.1f}  (kanoniczny TA-Lib, Wilder)")
    logger.info(f"MACD[last]: {macd['MACD'][-1]:.2f}")
    logger.info(f"BB Upper/Middle/Lower: {bb['UPPER'][-1]:.1f} / {bb['MIDDLE'][-1]:.1f} / {bb['LOWER'][-1]:.1f}")
    logger.info(f"Golden Cross: {sig.golden_cross()} | RSI Oversold: {sig.rsi_oversold()} | MACD Bullish: {sig.macd_bullish_cross()}")

    print("\n✅ ToolForge v2.0 — demo zakończone (Zasada 75 spełniona).")


if __name__ == "__main__":
    main()
