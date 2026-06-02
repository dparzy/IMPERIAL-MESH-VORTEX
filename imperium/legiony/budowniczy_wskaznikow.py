"""
🔧 Budowniczy Wskaźników — spina Bramę v2 z serią barów w komplet dict dla neuronów.

ROLA (Prawo XV — pełne wykorzystanie potencjału):
  Neurony czytają z dict `wskazniki`. Brama liczy wartości, ale ktoś musi:
    1. zebrać serie OHLCV z barów
    2. wywołać Bramę po KAŻDY klucz, którego potrzebują neurony
    3. zbudować jeden komplet dict
  Bez tego Brama v2 (24 obliczenia) leży odłogiem — neurony dostają puste klucze.

  Ten moduł jest mostem: bary → Brama → kompletny dict → neurony głosują.

UWAGA TA-Lib:
  Brama wymaga TA-Lib (Prawo I — zero halucynacji). Bez niej budowniczy
  nie zadziała (celowo — żadnej ręcznej matematyki w zastępstwie).
  Import Bramy jest leniwy, by moduł dał się zaimportować w testach bez TA-Lib.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("Budowniczy")


def _serie(bary: List[Dict[str, Any]]) -> Dict[str, List[float]]:
    """Rozbija bary OHLCV na osobne serie dla Bramy."""
    return {
        "open":   [float(b.get("open", 0)) for b in bary],
        "high":   [float(b.get("high", 0)) for b in bary],
        "low":    [float(b.get("low", 0)) for b in bary],
        "close":  [float(b.get("close", 0)) for b in bary],
        "volume": [float(b.get("volume", 0)) for b in bary],
    }


# Klucz w dict → (nazwa obliczenia w Bramie, jakich serii potrzebuje)
# Dla obliczeń zwracających dict (MACD, ICHIMOKU, BBANDS) rozpakowujemy osobno.
_PLAN_SKALARNE = {
    "RSI_14":        ("RSI", ("close",), {"period": 14}),
    "RSI_PREV":      ("RSI_PREV", ("close",), {"period": 14}),
    "EMA_9":         ("EMA_9", ("close",), {}),
    "EMA_21":        ("EMA_21", ("close",), {}),
    "EMA_50":        ("EMA_50", ("close",), {}),
    "EMA_200":       ("EMA_200", ("close",), {}),
    "EMA_9_PREV":    ("EMA_9_PREV", ("close",), {}),
    "EMA_21_PREV":   ("EMA_21_PREV", ("close",), {}),
    "EMA_50_PREV":   ("EMA_50_PREV", ("close",), {}),
    "EMA_200_PREV":  ("EMA_200_PREV", ("close",), {}),
    "MACD_HIST_PREV":("MACD_HIST_PREV", ("close",), {}),
    "ADX_14":        ("ADX_14", ("high", "low", "close"), {"period": 14}),
    "DI_PLUS":       ("DI_PLUS", ("high", "low", "close"), {"period": 14}),
    "DI_MINUS":      ("DI_MINUS", ("high", "low", "close"), {"period": 14}),
    "WILLIAMS_R":    ("WILLIAMS_R", ("high", "low", "close"), {"period": 14}),
    "STOCHRSI":      ("STOCHRSI", ("close",), {"period": 14}),
    "TRIX":          ("TRIX", ("close",), {"period": 15}),
    "TRIX_PREV":     ("TRIX_PREV", ("close",), {"period": 15}),
    "AO":            ("AO", ("high", "low"), {}),
    "AO_PREV":       ("AO_PREV", ("high", "low"), {}),
    "HMA":           ("HMA", ("close",), {"period": 16}),
    "HMA_PREV":      ("HMA_PREV", ("close",), {"period": 16}),
    "AC":            ("AC", ("high", "low"), {}),
    "AC_PREV":       ("AC_PREV", ("high", "low"), {}),
    "RVOL":          ("RVOL", ("volume",), {"period": 20}),
    "OBV":           ("OBV", ("close", "volume"), {}),
    "OBV_EMA_20":    ("OBV_EMA_20", ("close", "volume"), {}),
    "VOLUME_MA20":   ("VOLUME_MA20", ("volume",), {}),
    "ATR_DEVIATION": ("ATR_DEVIATION", ("high", "low", "close"), {}),
    "VWAP":          ("VWAP", ("high", "low", "close", "volume"), {}),
    "VWAP_STD":      ("VWAP_STD", ("high", "low", "close", "volume"), {}),
    "SUPERTREND":          ("SUPERTREND", ("high", "low", "close"), {}),
    "SUPERTREND_DIR":      ("SUPERTREND_DIR", ("high", "low", "close"), {}),
    "SUPERTREND_DIR_PREV": ("SUPERTREND_DIR_PREV", ("high", "low", "close"), {}),
}


class BudowniczyWskaznikow:
    """
    Buduje kompletny dict `wskazniki` z serii barów przez Bramę Kalkulatora.

    Użycie:
        from imperium.fundament.brama_kalkulatora import CalculatorGateway
        bud = BudowniczyWskaznikow(CalculatorGateway())
        wskazniki = bud.zbuduj(bary)        # dict gotowy dla neuronów
    """

    def __init__(self, brama=None):
        if brama is None:
            # Leniwy import — Brama wymaga TA-Lib
            from imperium.fundament.brama_kalkulatora import CalculatorGateway
            brama = CalculatorGateway()
        self.brama = brama

    def zbuduj(self, bary: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Zwraca pełny dict wskaźników dla bieżącego (ostatniego) baru."""
        if not bary:
            return {}
        serie = _serie(bary)
        w: Dict[str, Any] = {}

        # Surowe wartości bieżącego i poprzedniego baru (dla neuronów struktury/OI)
        ostatni = bary[-1]
        w["OPEN"] = float(ostatni.get("open", 0))
        w["CLOSE"] = float(ostatni.get("close", 0))
        w["HIGH"] = float(ostatni.get("high", 0))
        w["LOW"] = float(ostatni.get("low", 0))
        w["VOLUME"] = float(ostatni.get("volume", 0))
        if len(bary) >= 2:
            w["OPEN_PREV"] = float(bary[-2].get("open", 0))
            w["CLOSE_PREV"] = float(bary[-2].get("close", 0))
            w["HIGH_PREV"] = float(bary[-2].get("high", 0))
            w["LOW_PREV"] = float(bary[-2].get("low", 0))
            w["VOLUME_PREV"] = float(bary[-2].get("volume", 0))

        # Skalarne obliczenia Bramy
        for klucz, (calc, args, kwargs) in _PLAN_SKALARNE.items():
            try:
                params = {a: serie[a] for a in args}
                params.update(kwargs)
                w[klucz] = self.brama.compute(calc, **params).value
            except Exception as e:
                logger.debug(f"[Budowniczy] {klucz} pominięty: {e}")
                w[klucz] = None

        # Obliczenia zwracające dict — rozpakuj do płaskich kluczy
        self._dodaj_macd(serie, w)
        self._dodaj_bbands(serie, w)
        self._dodaj_ichimoku(serie, w)
        self._dodaj_donchian(serie, w)
        self._dodaj_ha(bary, w)

        return w

    def _dodaj_macd(self, serie, w):
        try:
            d = self.brama.compute("MACD", close=serie["close"]).value
            w["MACD"] = d.get("MACD")
            w["MACD_SIGNAL"] = d.get("SIGNAL")
            w["MACD_HIST"] = d.get("HISTOGRAM")
        except Exception as e:
            logger.debug(f"[Budowniczy] MACD pominięty: {e}")

    def _dodaj_bbands(self, serie, w):
        try:
            d = self.brama.compute("BBANDS", close=serie["close"]).value
            w["BB_UPPER"] = d.get("UPPER")
            w["BB_MIDDLE"] = d.get("MIDDLE")
            w["BB_LOWER"] = d.get("LOWER")
        except Exception as e:
            logger.debug(f"[Budowniczy] BBANDS pominięty: {e}")

    def _dodaj_ichimoku(self, serie, w):
        try:
            d = self.brama.compute("ICHIMOKU", high=serie["high"], low=serie["low"]).value
            w.update(d)  # ICHIMOKU_TENKAN/KIJUN/SENKOU_A/SENKOU_B
        except Exception as e:
            logger.debug(f"[Budowniczy] ICHIMOKU pominięty: {e}")

    def _dodaj_donchian(self, serie, w):
        try:
            d = self.brama.compute("DONCHIAN", high=serie["high"], low=serie["low"]).value
            w.update(d)  # DONCHIAN_UPPER/LOWER/MID
        except Exception as e:
            logger.debug(f"[Budowniczy] DONCHIAN pominięty: {e}")

    def _dodaj_ha(self, bary, w):
        """
        Heiken Ashi dla X-26 NeuronHAScalper (Prawo XV — był martwym głosem bo
        Budowniczy nie produkował HA_*). HA liczone rekurencyjnie z surowych OHLC
        (bez repainting — identycznie jak EXP-02). Wystawia ostatni bar:
          HA_BULL, HA_BEAR, HA_MOMENTUM (znorm. ATR), HA_VOLATILITY_INDEX (ATR/MidMA20).
        """
        try:
            if len(bary) < 2:
                return
            # HA rekurencyjne
            ha = []
            for i, b in enumerate(bary):
                o, h, l, c = (float(b.get("open", 0)), float(b.get("high", 0)),
                              float(b.get("low", 0)), float(b.get("close", 0)))
                ha_close = (o + h + l + c) / 4
                ha_open = (o + c) / 2 if i == 0 else (ha[i - 1]["o"] + ha[i - 1]["c"]) / 2
                ha_high = max(h, ha_open, ha_close)
                ha_low = min(l, ha_open, ha_close)
                ha.append({"o": ha_open, "c": ha_close, "mid": (ha_high + ha_low) / 2})

            # ATR (True Range z surowych barów, okres 14)
            trs = []
            for i in range(1, len(bary)):
                h = float(bary[i].get("high", 0)); l = float(bary[i].get("low", 0))
                pc = float(bary[i - 1].get("close", 0))
                trs.append(max(h - l, abs(h - pc), abs(l - pc)))
            atr = sum(trs[-14:]) / len(trs[-14:]) if trs else 0.0

            ostatni = ha[-1]
            w["HA_BULL"] = ostatni["c"] >= ostatni["o"]
            w["HA_BEAR"] = ostatni["c"] < ostatni["o"]
            if atr > 0:
                w["HA_MOMENTUM"] = (ostatni["mid"] - ha[-2]["mid"]) / atr
                mids = [x["mid"] for x in ha[-20:]]
                mid_ma = sum(mids) / len(mids)
                w["HA_VOLATILITY_INDEX"] = atr / mid_ma if mid_ma > 0 else 0.0
        except Exception as e:
            logger.debug(f"[Budowniczy] HA pominięty: {e}")
