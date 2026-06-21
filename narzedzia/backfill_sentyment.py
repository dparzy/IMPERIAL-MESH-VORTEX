#!/usr/bin/env python3
"""
📡 Backfill sentymentu — pobiera historię funding/OI/L-S z Binance public → CSV.

CEL (Prawo XVI): dostarczyć historyczne dane PSY-01/02/04 do backtestu, żeby
ZMIERZYĆ czy te neurony dodają przewagę (dotąd żyły tylko live → niemierzalne).

UŻYCIE (lokalnie — wymaga sieci, w chmurze Binance bywa zablokowany):
    python narzedzia/backfill_sentyment.py BTCUSDT ETHUSDT
    python narzedzia/backfill_sentyment.py BTCUSDT --period 4h --limit 1000

Zapisuje do: dane/sentyment/<SYMBOL>.csv (timestamp, FUNDING_RATE, OPEN_INTEREST,
LONG_SHORT_RATIO). Funding ma pełną historię; OI/L-S tylko ~30 dni (limit Binance).

BEZPIECZEŃSTWO: endpointy publiczne, BEZ klucza API (Prawo V — zero kluczy w kodzie).

Po backfillu — wpięcie do backtestu:
    from imperium.akwedukty.sentyment_historyczny import wczytaj_csv, forward_fill_na_bary
    hist = wczytaj_csv("dane/sentyment/BTCUSDT.csv")
    sent_map = forward_fill_na_bary(bary, hist)   # {ts_baru: {FUNDING_RATE,...}}
    backtest_portfel(..., sentyment_per={"BTCUSDT": sent_map})
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from imperium.akwedukty.adaptery.futures import AdapterFutures  # noqa: E402
from imperium.akwedukty.sentyment_historyczny import zapisz_csv  # noqa: E402

DEFAULT_KATALOG = ROOT / "dane" / "sentyment"


def backfill(symbol: str, period: str, limit: int, katalog: Path) -> int:
    adapter = AdapterFutures()
    historia = adapter.pobierz_historie(symbol, limit=limit, period=period)
    if not historia:
        print(f"  [{symbol}] BRAK danych (sieć zablokowana? endpoint padł?)")
        return 0
    sciezka = katalog / f"{symbol.upper()}.csv"
    n = zapisz_csv(historia, sciezka)
    z_funding = sum(1 for r in historia if r.get("FUNDING_RATE") is not None)
    z_oi = sum(1 for r in historia if r.get("OPEN_INTEREST") is not None)
    print(f"  [{symbol}] {n} rekordów → {sciezka}  (funding={z_funding}, OI={z_oi})")
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill historii sentymentu z Binance public")
    ap.add_argument("symbole", nargs="+", help="np. BTCUSDT ETHUSDT")
    ap.add_argument("--period", default="1h", help="period dla OI/L-S (5m/15m/1h/4h/1d)")
    ap.add_argument("--limit", type=int, default=1000, help="liczba rekordów/zapytanie")
    ap.add_argument("--katalog", default=str(DEFAULT_KATALOG))
    args = ap.parse_args()

    katalog = Path(args.katalog)
    print(f"📡 Backfill sentymentu → {katalog}")
    lacznie = 0
    for sym in args.symbole:
        lacznie += backfill(sym, args.period, args.limit, katalog)
    print(f"✅ Zapisano {lacznie} rekordów dla {len(args.symbole)} par.")


if __name__ == "__main__":
    main()
