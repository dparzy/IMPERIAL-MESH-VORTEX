"""
🌐 Pobieranie danych makro z Yahoo Finance (DXY, XAUUSD, SPX)
Uruchom z LAPTOPA (nie z serwera chmurowego — brak dostępu do sieci).

Pobiera: DXY (dolar), XAUUSD (złoto), ^GSPC (S&P 500)
Zapisuje do: dane/makro/

Po pobraniu backtest_portfel() automatycznie wykryje pliki i wstrzyknie dane
do neuronów K-01 (DXY_MOM) i K-02 (GOLD_BTC_MOM).

UZYCIE:
    pip install yfinance
    python narzedzia/pobierz_makro.py
"""
import sys
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("Zainstaluj: pip install yfinance")
    sys.exit(1)

SYMBOLE = {
    "DXY":  "DX-Y.NYB",   # US Dollar Index
    "GOLD": "GC=F",        # Złoto (futures)
    "SPX":  "^GSPC",       # S&P 500
}
START = "2015-01-01"
FOLDER = Path("dane/makro")


def pobierz(ticker_key: str, ticker_yf: str):
    print(f"  Pobieranie {ticker_key} ({ticker_yf})...", end=" ")
    df = yf.download(ticker_yf, start=START, interval="1d",
                     auto_adjust=True, progress=False)
    if df.empty:
        print("BRAK DANYCH")
        return
    out = FOLDER / f"{ticker_key}_1D.csv"
    # Ujednolicony format: timestamp (ms), open, high, low, close, volume
    df_out = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df_out.columns = ["open", "high", "low", "close", "volume"]
    df_out.index.name = "date"
    df_out["timestamp"] = (df_out.index.astype("int64") // 10**6).values
    df_out.to_csv(out, index=True)
    print(f"✅ {len(df_out)} świec → {out}")


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    print(f"\n🌐 Pobieranie danych makro (od {START} do dziś)\n")
    for key, ticker in SYMBOLE.items():
        pobierz(key, ticker)
    print(f"\n✅ Gotowe. Pliki w {FOLDER.resolve()}")
    print("   Prześlij folder dane/makro/ na serwer i uruchom backtest.")
    print("   Neurony K-01 (DXY) i K-02 (Gold/BTC) ożyją automatycznie.")


if __name__ == "__main__":
    main()
