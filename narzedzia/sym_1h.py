"""
Runner symulacji TRYB NAJLEPSZY (pełny stack W-317..W-321) na danych 1h.
Porównanie z biegiem 4h (W-319: 90.2x). Prawo I — liczby z realnego backtestu.

Uruchom:  python narzedzia/sym_1h.py
Limit:    MAX_BAROW=30000 python narzedzia/sym_1h.py   (cap barów/parę — kontrola RAM)

UWAGA RAM (Prawo I): pełny bieg 5 par × ~67k barów 1h akumuluje pamięć liniowo
(historia trade'ów per tik) i przekracza ~13GB → ryzyko OOM w kontenerze 15GB.
Domyślny cap 30k barów/parę (~3.4 lat 1h) daje ukończalny, uczciwy pomiar.
Cap zdejmiesz przez MAX_BAROW=0 (pełna historia — tylko gdy RAM wystarcza).
"""
import logging
import os
import time

logging.disable(logging.CRITICAL)  # cisza Bramy — czysty raport

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from imperium.koloseum.backtest import backtest_portfel  # noqa: E402

PLIKI_1H = {
    "BTCUSDT":  "dane/godzinowe/Binance_BTCUSDT_1h.csv",
    "ETHUSDT":  "dane/godzinowe/Binance_ETHUSDT_1h.csv",
    "SOLUSDT":  "dane/godzinowe/Binance_SOLUSDT_1h.csv",
    "BNBUSDT":  "dane/godzinowe/Binance_BNBUSDT_1h.csv",
    "DOGEUSDT": "dane/godzinowe/Binance_DOGEUSDT_1h.csv",
}

MAX_BAROW = int(os.getenv("MAX_BAROW", "30000"))  # 0 = pełna historia


def _raport(nazwa, eng):
    s = eng.podsumowanie()
    pnl_pct = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"\n=== {nazwa} ===")
    print(f"  Trade:           {s.total_trades}")
    print(f"  Win Rate:        {s.win_rate:.1%}")
    print(f"  PnL:             {s.total_pnl_usdt:+,.2f} USDT ({pnl_pct:+.1f}%)")
    print(f"  Kapitał końcowy: {s.kapital_koncowy:,.2f} USDT")
    print(f"  Mnożnik:         {s.kapital_koncowy / s.kapital_startowy:.2f}x")
    return s


def main():
    t0 = time.time()
    limit = MAX_BAROW if MAX_BAROW > 0 else None
    print(f"⚙️  Ładuję dane 1h (cap/parę: {limit or 'PEŁNA HISTORIA'}) — "
          f"PEŁNY STACK (TOP-3 + Conviction + Compounding + filtr asymetrii)...")

    bary_per = {}
    for sym, sciezka in PLIKI_1H.items():
        bary = wczytaj_csv(sciezka, interwal="1h", limit=limit)
        bary_per[sym] = bary
        print(f"  {sym}: {len(bary)} barów 1h")

    eng_full = backtest_portfel(
        PLIKI_1H, interwal="1h", bary_per=bary_per,
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True,
    )
    _raport(f"PEŁNY STACK + COMPOUNDING (1h, cap {limit or 'pełna'})", eng_full)

    print(f"\n⏱️  Czas: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
