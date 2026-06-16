"""
Porównanie TF na TYM SAMYM oknie czasowym (izolacja: interwał vs okno).
Cap 1h = MAX_BAROW barów/parę; 4h = MAX_BAROW/4 barów (ten sam zakres kalendarzowy).
Prawo I: rozdziela efekt interwału od efektu okna (DOGE 2021 poza oknem 3.4 lat).

Uruchom: python narzedzia/sym_porownanie_tf.py
"""
import logging
import os
import time

logging.disable(logging.CRITICAL)

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from imperium.koloseum.backtest import backtest_portfel  # noqa: E402

PLIKI_1H = {
    "BTCUSDT":  "dane/godzinowe/Binance_BTCUSDT_1h.csv",
    "ETHUSDT":  "dane/godzinowe/Binance_ETHUSDT_1h.csv",
    "SOLUSDT":  "dane/godzinowe/Binance_SOLUSDT_1h.csv",
    "BNBUSDT":  "dane/godzinowe/Binance_BNBUSDT_1h.csv",
    "DOGEUSDT": "dane/godzinowe/Binance_DOGEUSDT_1h.csv",
}
PLIKI_4H = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}
MAX_BAROW = int(os.getenv("MAX_BAROW", "30000"))  # 1h barów/parę


def _raport(nazwa, eng):
    s = eng.podsumowanie()
    pct = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"\n=== {nazwa} ===")
    print(f"  Trade: {s.total_trades} | WR {s.win_rate:.1%} | "
          f"PnL {s.total_pnl_usdt:+,.0f} USDT ({pct:+.1f}%) | "
          f"{s.kapital_koncowy:,.0f}$ = {s.kapital_koncowy / s.kapital_startowy:.2f}x")


def _bieg(pliki, interwal, limit):
    bary_per = {}
    zakresy = []
    for sym, sc in pliki.items():
        b = wczytaj_csv(sc, interwal=interwal, limit=limit)
        bary_per[sym] = b
        if b:
            zakresy.append((b[0]["timestamp"], b[-1]["timestamp"]))
    if zakresy:
        import datetime as dt
        od = dt.datetime.utcfromtimestamp(min(z[0] for z in zakresy) / 1000).date()
        do = dt.datetime.utcfromtimestamp(max(z[1] for z in zakresy) / 1000).date()
        print(f"  okno: {od} → {do} | barów/parę: {len(next(iter(bary_per.values())))}")
    return backtest_portfel(
        pliki, interwal=interwal, bary_per=bary_per,
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True,
    )


def main():
    t0 = time.time()
    print(f"⚙️  Porównanie TF, to samo okno (~{MAX_BAROW/24/365:.1f} lat). Pełny stack.")

    print("\n▶ 4h (cap MAX_BAROW/4)...")
    _raport("4h — to samo okno", _bieg(PLIKI_4H, "4h", MAX_BAROW // 4))

    print("\n▶ 1h (cap MAX_BAROW)...")
    _raport("1h — to samo okno", _bieg(PLIKI_1H, "1h", MAX_BAROW))

    print(f"\n⏱️  Czas: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
