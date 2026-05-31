"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Brama Kalkulatora (Calculator Gateway) — Keystone Zasady 75 v1.0       ║
║  Autor: Jack (Główny Projektant Królestwa Pixel)                            ║
║  Oryginał Kingdom Pixel — wszelkie prawa autorskie                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA (Zasada 11) ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-CORE-006  (numer do potwierdzenia wg ZBADANE — 005 zajęty) |
| Nazwa oryginalna    | Calculator Gateway (oryginał Kingdom Pixel)                  |
| Nazwa w Królestwie  | Brama Kalkulatora                                            |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/CORE-006_CalculatorGateway.py       |
| Kategoria           | CORE / Deterministyczna warstwa obliczeń (Zasada 75)        |
| Wpływ na Królestwo  | JEDYNE wejście do matematyki. AI nigdy nie liczy — pyta      |
|                     | Bramę i dostaje wynik + pieczątkę audytu. Serce Zasady 75.  |
| Powiązane moduły    | N-TOOLS-208 (ToolForge), N-BRAIN-026, każdy moduł liczący   |

────────────────────────────── IDEA (dla nowicjusza) ──────────────────────────────
Problem: modele AI mylą się w arytmetyce (Zasada 75). Rozwiązanie: cała matematyka
idzie przez tę Bramę, która używa TA-Lib (rdzeń C, deterministyczny) i zwraca
DOKŁADNĄ liczbę z pieczątką (hash + czas + źródło). AI tylko interpretuje wynik.

CHANGELOG:
  v1.0 (2026-05-28) — pierwszy oryginalny keystone Królestwa: rejestr dozwolonych
        obliczeń, kontrakt JSON, log audytu (Data Lineage — Zasada 23), twarde
        odrzucanie nieznanych żądań (guardrail).
═════════════════════════════════════════════════════════════════════════════════════
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Callable

import numpy as np

# ── Zasada 75: deterministyczny rdzeń. Bez TA-Lib Brama NIE działa (celowo). ──
try:
    import talib
except ImportError as e:
    raise RuntimeError(
        "N-CORE-006 (Brama Kalkulatora) wymaga TA-Lib (Zasada 75). "
        "Instalacja: `pip install TA-Lib`. Brak fallbacku do ręcznej matematyki."
    ) from e

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("BramaKalkulatora")

SOURCE_TAG = "TA-Lib (C-core, deterministic)"


def _arr(x) -> np.ndarray:
    return np.asarray(x, dtype=np.float64)


def _last_valid(a: np.ndarray):
    """Ostatnia nie-NaN wartość (TA-Lib zwraca NaN w okresie rozgrzewania)."""
    a = np.asarray(a, dtype=np.float64)
    valid = a[~np.isnan(a)]
    return float(valid[-1]) if valid.size else None


@dataclass
class CalcResult:
    """Wynik obliczenia z pieczątką audytu (Zasada 23 — Data Lineage)."""
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
    Jedyne wejście do matematyki w Królestwie.
      - compute(name, **params) → CalcResult (deterministyczny TA-Lib + pieczątka)
      - nieznany wskaźnik = twarde odrzucenie (guardrail)
      - każde obliczenie trafia do logu audytu (Data Lineage)
    """

    def __init__(self):
        self._registry: Dict[str, Callable[..., Any]] = {
            "RSI":    lambda close, period=14: _last_valid(talib.RSI(_arr(close), timeperiod=period)),
            "EMA":    lambda close, period=20: _last_valid(talib.EMA(_arr(close), timeperiod=period)),
            "SMA":    lambda close, period=20: _last_valid(talib.SMA(_arr(close), timeperiod=period)),
            "ATR":    lambda high, low, close, period=14: _last_valid(talib.ATR(_arr(high), _arr(low), _arr(close), timeperiod=period)),
            "MACD":   self._macd,
            "BBANDS": self._bbands,
        }
        self.audit_log: List[CalcResult] = []

    @staticmethod
    def _macd(close, fast=12, slow=26, signal=9) -> Dict[str, float]:
        macd, sig, hist = talib.MACD(_arr(close), fastperiod=fast, slowperiod=slow, signalperiod=signal)
        return {"MACD": _last_valid(macd), "SIGNAL": _last_valid(sig), "HISTOGRAM": _last_valid(hist)}

    @staticmethod
    def _bbands(close, period=20, std=2.0) -> Dict[str, float]:
        up, mid, low = talib.BBANDS(_arr(close), timeperiod=period, nbdevup=std, nbdevdn=std, matype=0)
        return {"UPPER": _last_valid(up), "MIDDLE": _last_valid(mid), "LOWER": _last_valid(low)}

    def available(self) -> List[str]:
        return sorted(self._registry.keys())

    def compute_series(self, indicator: str, **kwargs):
        """Zwraca PEŁNĄ serię wskaźnika (do backtestów na dużych danych).
        Nadal jedyne wejście do matematyki — Zasada 75 zachowana. Brak lookahead:
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
            # GUARDRAIL: nic spoza rejestru. AI nie wymyśla obliczeń.
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
        """Pełny log audytu w JSON (Data Lineage — Zasada 23)."""
        return json.dumps([asdict(r) for r in self.audit_log], ensure_ascii=False, indent=2)


def main():
    logger.info("=== Brama Kalkulatora v1.0 Demo (keystone Zasady 75) ===")
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

    logger.info(f"Audyt: {len(gw.audit_log)} obliczeń zalogowanych (Data Lineage).")
    print("\n✅ Brama Kalkulatora v1.0 — demo zakończone (Zasada 75 w kodzie).")


if __name__ == "__main__":
    main()
