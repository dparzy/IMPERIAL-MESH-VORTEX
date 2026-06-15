"""
Runner symulacji TRYB NAJLEPSZY (pełny stack W-317..W-321) na danych 1h.
Porównanie z biegiem 4h (W-319: 90.2x). Prawo I — liczby z realnego backtestu.

Uruchom: python narzedzia/sym_1h.py
"""
import logging
import time

logging.disable(logging.CRITICAL)  # cisza Bramy — czysty raport

from imperium.koloseum.backtest import backtest_portfel  # noqa: E402

PLIKI_1H = {
    "BTCUSDT":  "dane/godzinowe/Binance_BTCUSDT_1h.csv",
    "ETHUSDT":  "dane/godzinowe/Binance_ETHUSDT_1h.csv",
    "SOLUSDT":  "dane/godzinowe/Binance_SOLUSDT_1h.csv",
    "BNBUSDT":  "dane/godzinowe/Binance_BNBUSDT_1h.csv",
    "DOGEUSDT": "dane/godzinowe/Binance_DOGEUSDT_1h.csv",
}


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
    print("⚙️  Ładuję dane 1h i uruchamiam PEŁNY STACK (TOP-3 + Conviction + Compounding)...")

    eng_full = backtest_portfel(
        PLIKI_1H, interwal="1h",
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True,
    )
    _raport("PEŁNY STACK + COMPOUNDING (1h)", eng_full)

    print(f"\n⏱️  Czas: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
