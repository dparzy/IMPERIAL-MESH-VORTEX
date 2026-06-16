"""
A/B impakt 5 nowych neuronów W-322 na TRYB NAJLEPSZY (4h, to samo okno 2022→2026).
„Przed" = rój bez V-06/V-07/VP-01/Z-06/Z-07 (65). „Po" = pełne 70.
Monkey-patch wszystkie_neurony (czyste A/B, ten sam kod/dane). Prawo I/XVI.

Uruchom: python narzedzia/ab_w322.py
"""
import logging
import os
import time

logging.disable(logging.CRITICAL)

import imperium.legiony.rejestr as R  # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from imperium.koloseum.backtest import backtest_portfel  # noqa: E402

PLIKI_4H = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}
NOWE = {"V-06", "V-07", "VP-01", "Z-06", "Z-07"}
LIMIT = int(os.getenv("LIMIT_4H", "7500"))   # ~3.4 lat 4h (okno W-321b)

_orig = R.wszystkie_neurony


def _bary():
    return {s: wczytaj_csv(sc, interwal="4h", limit=LIMIT) for s, sc in PLIKI_4H.items()}


def _raport(nazwa, eng):
    s = eng.podsumowanie()
    pct = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"=== {nazwa} ===")
    print(f"  Trade: {s.total_trades} | WR {s.win_rate:.1%} | "
          f"PnL {s.total_pnl_usdt:+,.0f} USDT ({pct:+.2f}%) | {s.kapital_koncowy:,.0f}$")
    return pct, s.total_trades


def _bieg(bary_per):
    return backtest_portfel(
        PLIKI_4H, interwal="4h", bary_per=bary_per,
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True,
    )


def main():
    t0 = time.time()
    bary_per = _bary()
    print(f"⚙️  A/B W-322 — 4h, {LIMIT} barów/parę. 65 (bez nowych) vs 70 (pełne).\n")

    # PRZED: rój bez 5 nowych neuronów
    R.wszystkie_neurony = lambda: [n for n in _orig() if n.KLUCZ not in NOWE]
    print(f"[PRZED] neuronów: {len(R.wszystkie_neurony())}")
    pct0, tr0 = _raport("PRZED (65, bez W-322)", _bieg({k: list(v) for k, v in bary_per.items()}))

    # PO: pełny rój
    R.wszystkie_neurony = _orig
    print(f"\n[PO] neuronów: {len(R.wszystkie_neurony())}")
    pct1, tr1 = _raport("PO (70, z W-322)", _bieg({k: list(v) for k, v in bary_per.items()}))

    print(f"\n>>> IMPAKT W-322: {pct1 - pct0:+.2f} pkt proc. PnL "
          f"({pct0:+.2f}% → {pct1:+.2f}%), trade {tr0}→{tr1}")
    print(f"⏱️  {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
