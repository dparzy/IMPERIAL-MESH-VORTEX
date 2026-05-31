"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Ładowarka Danych (Data Loader) — realne OHLCV + biblioteka v1.1        ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                            ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-DATA-001                                                   |
| Nazwa oryginalna    | Data Loader (oryginał Kingdom Pixel)                        |
| Nazwa w Imperium    | Ładowarka (Kwatermistrz Danych)                             |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/DATA-001_DataLoader.py              |
| Kategoria           | DATA / Pozyskiwanie danych rynkowych (OHLCV)                |
| Wpływ na Imperium   | Realne darmowe dane (CCXT) + import własnych CSV +           |
|                     | biblioteka wielu monet + kontrola jakości.                  |
| Powiązane moduły    | N-STRAT-001, N-BACK-210, N-CORE-006, N-VIZ-001              |

CHANGELOG:
  v1.2 (2026-05-29) — HIGIENA: import_csv usuwa złe znaczniki czasu, duplikaty
        (keep last) i sortuje rosnąco. Wykryte podczas testu 1H (brudne dane
        CryptoDataDownload — 1145 duplikatów). quality_check to złapał.
  v1.1 (2026-05-29) — (C) import_csv() z normalizatorem formatów (Binance/
        CryptoDataDownload/dowolny). (D) biblioteka monet (folder dane/, lista,
        wczytywanie, dodawanie). (G) quality_check() — dziury, duplikaty, błędne
        świece, ekstremalne skoki.
  v1.0 (2026-05-28) — CCXT fetch + bezpiecznik syntetyczny + CSV.

UCZCIWIE: dane z giełdy darmowe i publiczne (bez klucza). Offline → bezpiecznik
syntetyczny z WYRAŹNYM ostrzeżeniem. Różne strony mają różne kolumny — dlatego
normalizator sprowadza każdy plik do schematu: timestamp, open, high, low, close, volume.
═════════════════════════════════════════════════════════════════════════════════════
"""

import os
import time
import glob
import logging
from typing import List, Optional, Dict

import numpy as np
import pandas as pd

try:
    import ccxt
    _CCXT = True
except ImportError:
    _CCXT = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("Ladowarka")

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]
LIBRARY_DIR = "dane"

# kandydaci nazw kolumn (małymi literami) → nasze pole
_ALIASES = {
    "timestamp": ["timestamp", "time", "date", "datetime", "unix", "open_time"],
    "open": ["open", "o"],
    "high": ["high", "h"],
    "low": ["low", "l"],
    "close": ["close", "c", "price"],
    "volume": ["volume", "vol", "volume btc", "volume usdt", "v"],
}


class DataLoader:
    def __init__(self, exchange_id: str = "mexc", timeout_ms: int = 8000):
        self.exchange_id = exchange_id
        self._ex = None
        if _CCXT and hasattr(ccxt, exchange_id):
            self._ex = getattr(ccxt, exchange_id)({"enableRateLimit": True, "timeout": timeout_ms})
        elif not _CCXT:
            logger.warning("[Ładowarka] Brak CCXT (`pip install ccxt`) — tylko dane lokalne/syntetyczne.")

    # ─────────────────────────── CCXT (v1.0) ───────────────────────────
    def fetch(self, symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        if self._ex is None:
            raise RuntimeError("Brak działającej giełdy CCXT.")
        return self._to_df(self._ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit))

    @staticmethod
    def _to_df(raw: list) -> pd.DataFrame:
        df = pd.DataFrame(raw, columns=COLUMNS)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    @staticmethod
    def synthetic(n: int = 500, seed: int = 2026, start: float = 50000.0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        close = [start]
        for _ in range(n - 1):
            close.append(close[-1] * (1 + rng.normal(0.0003, 0.018)))
        close = np.array(close)
        open_ = np.concatenate([[start], close[:-1]])
        hi_base = np.maximum(open_, close)
        lo_base = np.minimum(open_, close)
        high = hi_base * (1 + rng.uniform(0, 0.01, n))
        low = lo_base * (1 - rng.uniform(0, 0.01, n))
        vol = rng.uniform(10, 100, n)
        ts = pd.date_range(end=pd.Timestamp.now("UTC"), periods=n, freq="h")
        return pd.DataFrame({"timestamp": ts, "open": open_, "high": high, "low": low, "close": close, "volume": vol})

    # ─────────────────────── C: import + normalizator ───────────────────────
    @classmethod
    def import_csv(cls, path: str, mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """Wczytuje CSV z DOWOLNEJ darmowej strony i normalizuje do naszego schematu."""
        # niektóre strony mają wiersz tytułowy — spróbuj pominąć, jeśli pierwszy wiersz to nie nagłówek danych
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
        # niektóre strony (np. CryptoDataDownload) mają wiersz tytułowy bez przecinków
        skip = 1 if first_line.count(",") < 2 else 0
        raw = pd.read_csv(path, skiprows=skip)
        cols_lower = {c.lower().strip(): c for c in raw.columns}
        m = mapping or {}
        norm = {}
        for field, aliases in _ALIASES.items():
            src = m.get(field)
            if not src:
                for a in aliases:
                    if a in cols_lower:
                        src = cols_lower[a]
                        break
            if src is None:
                raise ValueError(f"Nie znaleziono kolumny dla '{field}'. Podaj mapping={{'{field}':'nazwa_kolumny'}}. "
                                 f"Dostępne kolumny: {list(raw.columns)}")
            norm[field] = raw[src]
        df = pd.DataFrame(norm)
        df["timestamp"] = cls._parse_timestamp(df["timestamp"])
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        # higiena: wyrzuć złe znaczniki czasu i ceny, usuń duplikaty czasu, posortuj rosnąco
        df = df.dropna(subset=["timestamp", "close"])
        df = df.drop_duplicates(subset="timestamp", keep="last")
        df = df.sort_values("timestamp").reset_index(drop=True)
        logger.info(f"[Ładowarka] Zaimportowano {len(df)} świec z {os.path.basename(path)} (znormalizowane).")
        return df[COLUMNS]

    @staticmethod
    def _parse_timestamp(s: pd.Series) -> pd.Series:
        if pd.api.types.is_numeric_dtype(s):
            mx = float(s.max())
            unit = "ms" if mx > 1e12 else ("s" if mx > 1e9 else "ms")
            return pd.to_datetime(s, unit=unit)
        return pd.to_datetime(s, errors="coerce")

    # ─────────────────────────── D: biblioteka ───────────────────────────
    @staticmethod
    def library_list(directory: str = LIBRARY_DIR) -> List[str]:
        if not os.path.isdir(directory):
            return []
        return sorted(os.path.basename(p) for p in glob.glob(os.path.join(directory, "*.csv")))

    @classmethod
    def library_add(cls, df: pd.DataFrame, coin: str, timeframe: str, directory: str = LIBRARY_DIR):
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{coin}_{timeframe}.csv")
        df.to_csv(path, index=False)
        logger.info(f"[Ładowarka] Dodano do biblioteki: {os.path.basename(path)} ({len(df)} świec).")
        return path

    @classmethod
    def library_load(cls, name: str, directory: str = LIBRARY_DIR) -> pd.DataFrame:
        path = os.path.join(directory, name if name.endswith(".csv") else name + ".csv")
        df = pd.read_csv(path, parse_dates=["timestamp"])
        logger.info(f"[Ładowarka] Wczytano z biblioteki: {os.path.basename(path)} ({len(df)} świec).")
        return df

    # ─────────────────────────── G: kontrola jakości ───────────────────────────
    @staticmethod
    def quality_check(df: pd.DataFrame) -> Dict:
        issues = []
        if df["timestamp"].duplicated().any():
            issues.append(f"duplikaty czasu: {int(df['timestamp'].duplicated().sum())}")
        if not df["timestamp"].is_monotonic_increasing:
            issues.append("czas NIE rośnie monotonicznie")
        nan = int(df[COLUMNS].isna().sum().sum())
        if nan:
            issues.append(f"brakujące wartości (NaN): {nan}")
        bad = df[(df["high"] < df["low"]) | (df["close"] <= 0) | (df["high"] < df[["open", "close"]].max(axis=1))]
        if len(bad):
            issues.append(f"błędne świece (high<low / cena<=0 / high<max(o,c)): {len(bad)}")
        # luki czasowe vs dominujący interwał
        if len(df) > 3:
            diffs = df["timestamp"].diff().dropna()
            modal = diffs.mode()
            if len(modal):
                gaps = int((diffs > modal.iloc[0] * 1.5).sum())
                if gaps:
                    issues.append(f"luki czasowe: {gaps}")
        # ekstremalne skoki (>50%)
        jumps = int((df["close"].pct_change().abs() > 0.5).sum())
        if jumps:
            issues.append(f"ekstremalne skoki >50%: {jumps}")
        ok = not issues
        (logger.info if ok else logger.warning)(
            f"[Jakość] {'OK — dane czyste' if ok else 'UWAGI: ' + '; '.join(issues)} ({len(df)} świec)")
        return {"ok": ok, "rows": len(df), "issues": issues}

    @staticmethod
    def closes(df: pd.DataFrame) -> List[float]:
        return df["close"].astype(float).tolist()


def main():
    logger.info("=== Ładowarka v1.1 Demo ===")
    base = os.path.dirname(os.path.abspath(__file__))
    libdir = os.path.join(base, LIBRARY_DIR)

    # 1) Dane (offline → synthetic) → dodaj do biblioteki (D)
    df_btc = DataLoader.synthetic(n=400, seed=2026)
    DataLoader.library_add(df_btc, "BTC", "1h", libdir)
    DataLoader.library_add(DataLoader.synthetic(n=300, seed=7, start=3000), "ETH", "1d", libdir)
    logger.info(f"[D] Biblioteka monet: {DataLoader.library_list(libdir)}")

    # 2) Symulacja pliku z 'darmowej strony' w innym formacie → import + normalizacja (C)
    foreign = pd.DataFrame({
        "unix": (df_btc["timestamp"].astype("int64") // 10**6).iloc[:50],   # ms epoch
        "Open": df_btc["open"].iloc[:50], "High": df_btc["high"].iloc[:50],
        "Low": df_btc["low"].iloc[:50], "Close": df_btc["close"].iloc[:50],
        "Volume BTC": df_btc["volume"].iloc[:50],
    })
    fpath = os.path.join(base, "obcy_format.csv"); foreign.to_csv(fpath, index=False)
    df_imp = DataLoader.import_csv(fpath)
    logger.info(f"[C] Zaimportowano obcy format → kolumny: {list(df_imp.columns)}")

    # 3) Kontrola jakości (G)
    DataLoader.quality_check(df_imp)

    print("\n✅ Ładowarka v1.1 — demo zakończone (C import, D biblioteka, G jakość).")


if __name__ == "__main__":
    main()
