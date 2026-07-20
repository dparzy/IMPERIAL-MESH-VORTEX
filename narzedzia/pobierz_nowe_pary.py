"""
Pobierz nowe pary — skrypt do uruchomienia LOKALNIE przez Cezara.

Pobiera dane historyczne (1h) dla nowych par z MEXC i agreguje do 4h.
Uruchom: python narzedzia/pobierz_nowe_pary.py

Wymaga: pip install ccxt (juz zainstalowane w Imperium)
Siec: polaczenie z api.mexc.com (dziala tylko lokalnie, nie w cloud)
"""

import os, sys, csv, time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import ccxt
except ImportError:
    print("BLAD: brak ccxt. Uruchom: pip install ccxt")
    sys.exit(1)

# Kandydaci na nowe pary — uzasadnienie (Prawo I — dane, nie opinia):
NOWE_PARY = {
    "ADA/USDT":  "Cardano — nizsza korelacja z BTC (~0.65), fundamentals-driven",
    "AVAX/USDT": "Avalanche — silny momentum layer-1, dobra zmiennosc 4h",
    "XRP/USDT":  "Ripple — skoki regulacyjne, unikalny risk profile, top volume",
    "PEPE/USDT": "Memecoin — ekstremalne fundingi (PSY-01), niska korelacja",
}

INTERWAL = "1h"
LIMIT_NA_REQUEST = 1000
DOCELOWE_BARY = 30000

exchange = ccxt.mexc({"enableRateLimit": True})


def pobierz_pare(symbol: str) -> list:
    """Pobiera do DOCELOWE_BARY barow 1h z MEXC."""
    print(f"\n  {symbol}: laduje historie...")
    wszystkie: list = []
    since = None

    # Pobierz pierwszy batch, by sprawdzic dostepny zakres
    try:
        pierwsze = exchange.fetch_ohlcv(symbol, INTERWAL, limit=1)
        if not pierwsze:
            print(f"  Brak danych dla {symbol}")
            return []
    except Exception as e:
        print(f"  Blad: {e}")
        return []

    # Wyznacz start: DOCELOWE_BARY * 1h wstecz od teraz
    teraz_ms = int(time.time() * 1000)
    ms_per_bar = 3600 * 1000
    since = teraz_ms - DOCELOWE_BARY * ms_per_bar

    while len(wszystkie) < DOCELOWE_BARY:
        try:
            bars = exchange.fetch_ohlcv(symbol, INTERWAL, since=since, limit=LIMIT_NA_REQUEST)
        except Exception as e:
            print(f"  Blad: {e}")
            break

        if not bars:
            break

        nowe = [b for b in bars if not wszystkie or b[0] > wszystkie[-1][0]]
        if not nowe:
            break
        wszystkie.extend(nowe)
        since = wszystkie[-1][0] + 1
        print(f"    {len(wszystkie)} barow...", end="\r")
        time.sleep(0.2)

    print(f"  OK {symbol}: {len(wszystkie)} barow 1h")
    return wszystkie


def zapisz_csv_1h(symbol: str, bars: list) -> str:
    """Zapisuje w formacie zgodnym z CryptoDataDownload dla czytnika Imperium."""
    sym_clean = symbol.replace("/", "")
    sciezka = os.path.join("dane", "godzinowe", f"MEXC_{sym_clean}_1h.csv")

    with open(sciezka, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Unix", "Date", "Symbol", "Open", "High", "Low", "Close",
                    f"Volume {sym_clean[:3]}", "Volume USDT", "tradecount"])
        for b in reversed(bars):
            ts, o, h, l, c, vol = b
            dt = datetime.utcfromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
            w.writerow([ts, dt, sym_clean, o, h, l, c, vol, round(vol * c, 2), 0])

    print(f"  Zapisano: {sciezka}")
    return sciezka


def main():
    print("=" * 60)
    print("POBIERANIE NOWYCH PAR DLA IMPERIUM")
    print("=" * 60)

    os.makedirs(os.path.join("dane", "godzinowe"), exist_ok=True)
    os.makedirs(os.path.join("dane", "4h"), exist_ok=True)

    pobrane = []
    for pair, opis in NOWE_PARY.items():
        print(f"\n{'─'*50}")
        print(f"Para: {pair}")
        print(f"Powod: {opis}")

        bars = pobierz_pare(pair)
        if len(bars) < 1000:
            print(f"  Zbyt malo barow ({len(bars)}) — pomijam")
            continue

        zapisz_csv_1h(pair, bars)
        pobrane.append(pair)

    print("\n" + "=" * 60)
    print("Agregowanie 1h -> 4h...")
    try:
        from narzedzia.agreguj_bary import main as _agr
        _agr()
    except Exception as e:
        print(f"Blad agregacji: {e}")
        print("Uruchom recznie: python narzedzia/agreguj_bary.py --z 1h --do 4h")

    print(f"\nGOTOWE! Pobrano {len(pobrane)} par: {', '.join(pobrane)}")
    print("\nAby testowac nowe pary:")
    print("  python narzedzia/backtest_nowe_pary.py")


if __name__ == "__main__":
    main()
