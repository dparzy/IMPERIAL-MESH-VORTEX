"""
Pobiera dane 4h bezpośrednio z publicznego API Binance (bez klucza).
Zapis do dane/4h/ w formacie kompatybilnym z czytnik_csv.py.

Użycie:
    python narzedzia/pobierz_4h_binance.py
    python narzedzia/pobierz_4h_binance.py --pary XRP,ADA,LINK
"""
import csv, time, sys, argparse
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Brak requests — zainstaluj: pip install requests")
    sys.exit(1)

PARY = ["XRP","ADA","AVAX","LINK","LTC","DOT","MATIC","TRX","ATOM","NEAR"]
FOLDER = Path("dane/4h")
INTERVAL = "4h"
LIMIT = 1000   # max Binance per request
_INTERWAL_MS = {"1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000}


def pobierz_klines(symbol: str, interval: str = "4h", limit: int = 1000) -> list:
    """Pobiera klines z Binance Spot API (publiczne, bez klucza) — ostatnie `limit` świec."""
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def pobierz_klines_zakres(symbol: str, interval: str, start_ms: int,
                          limit: int = 1000) -> list:
    """
    PAGINACJA: skleja strony od start_ms do teraz (Binach zwraca max `limit`/żądanie).
    Zwraca klines ROSNĄCO, zdeduplikowane po open-time. Wieloletnia historia 4h.
    """
    url = "https://api.binance.com/api/v3/klines"
    krok_ms = _INTERWAL_MS.get(interval)
    if krok_ms is None:
        raise ValueError(f"Nieznany interwał '{interval}' — dodaj do _INTERWAL_MS")
    widziane: dict = {}
    cur = start_ms
    while True:
        params = {"symbol": symbol, "interval": interval,
                  "startTime": cur, "limit": limit}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        for k in batch:
            widziane[int(k[0])] = k          # dedup po open-time
        ostatni_open = int(batch[-1][0])
        nastepny = ostatni_open + krok_ms
        if len(batch) < limit or nastepny <= cur:   # ostatnia strona / brak postępu
            break
        cur = nastepny
        time.sleep(0.3)                       # grzeczność wobec API
    return [widziane[t] for t in sorted(widziane)]


def zapisz_csv(symbol: str, klines: list, sciezka: Path):
    """Zapisuje w formacie CryptoDataDownload (kompatybilny z czytnik_csv.py)."""
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with open(sciezka, "w", newline="", encoding="utf-8") as f:
        f.write("https://www.binance.com\n")
        w = csv.writer(f)
        w.writerow(["Unix","Date","Symbol","Open","High","Low","Close",
                     f"Volume {symbol[:-4]}","Volume USDT","tradecount"])
        # Binance zwraca rosnąco — CDD zapisuje malejąco; odwracamy
        for k in reversed(klines):
            ts_ms = int(k[0])
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            w.writerow([
                ts_ms,
                dt.strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                k[1], k[2], k[3], k[4],   # OHLC
                k[5],                        # vol bazowy
                k[7],                        # vol USDT (quoteAssetVolume)
                int(k[8]),                   # tradecount
            ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pary", default=",".join(PARY))
    parser.add_argument("--od", default=None, metavar="YYYY-MM-DD",
                        help="Data początkowa → PAGINACJA do wieloletniej historii 4h "
                             "(np. --od 2021-01-01). Bez tego: ostatnie 1000 świec.")
    args = parser.parse_args()
    pary = [p.strip().upper() for p in args.pary.split(",")]

    start_ms = None
    if args.od:
        dt = datetime.strptime(args.od, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        start_ms = int(dt.timestamp() * 1000)

    ok, blad = 0, 0
    for p in pary:
        symbol = f"{p}USDT"
        cel = FOLDER / f"Binance_{symbol}_4h.csv"
        print(f"  {symbol} [4h] ... ", end="", flush=True)
        try:
            if start_ms is not None:
                klines = pobierz_klines_zakres(symbol, INTERVAL, start_ms)
            else:
                klines = pobierz_klines(symbol)
            zapisz_csv(symbol, klines, cel)
            print(f"OK ({len(klines)} swiec)")
            ok += 1
        except Exception as e:
            print(f"BLAD: {e}")
            blad += 1
        time.sleep(0.3)   # grzeczność wobec API

    print(f"\nGotowe. Pobrano: {ok} | Blad: {blad}")
    print("Sprawdz: python -c \"from imperium.akwedukty.czytnik_csv import wczytaj_csv; "
          "print(len(wczytaj_csv('dane/4h/Binance_XRPUSDT_4h.csv', interwal='4H')), 'barow')\"")


if __name__ == "__main__":
    main()
