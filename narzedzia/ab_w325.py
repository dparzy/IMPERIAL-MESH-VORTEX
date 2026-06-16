"""
A/B W-325 — GUBERNATOR (homeostatyczny sterownik portfela) vs baseline.

Hipoteza: globalny ster ekspozycji (ekspansja przy wyraźnym liderze + zdrowym
kapitale, obrona przy mdłym koszyku/obsunięciu) poprawia wynik portfela — naciska
przewagę gdy pewność wysoka, chroni proch gdy niska. Prawo I: MIERZYMY, nie wierzymy.

Pełny stack TRYB NAJLEPSZY (TOP-3 + conviction + compounding) na 4h, 5 par.
Uruchom: python narzedzia/ab_w325.py
"""
import logging
import os
import time

logging.disable(logging.CRITICAL)

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from imperium.koloseum.backtest import backtest_portfel  # noqa: E402

PLIKI_4H = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}
LIMIT = int(os.getenv("LIMIT_4H", "7500"))


def _bary():
    return {s: wczytaj_csv(sc, interwal="4h", limit=LIMIT) for s, sc in PLIKI_4H.items()}


def _raport(nazwa, eng):
    s = eng.podsumowanie()
    pct = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"  {nazwa:<28}: Trade {s.total_trades:4d} | WR {s.win_rate:.1%} | "
          f"MaxDD {s.max_drawdown_pct:.1%} | {s.kapital_koncowy:>12,.0f}$ ({pct:+.2f}%)")
    return pct


def _bieg(bary_per, gub):
    return backtest_portfel(
        PLIKI_4H, interwal="4h", bary_per=bary_per,
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True, gubernator=gub,
    )


def main():
    t0 = time.time()
    bary_per = _bary()
    print(f"⚙️  A/B W-325 — GUBERNATOR, 4h, {LIMIT} barów/parę, 5 par.\n")

    pct0 = _raport("BASELINE (bez gubernatora)",
                   _bieg({k: list(v) for k, v in bary_per.items()}, False))
    pct1 = _raport("GUBERNATOR (ON)",
                   _bieg({k: list(v) for k, v in bary_per.items()}, True))

    delta = pct1 - pct0
    znak = "✅ POPRAWA" if delta > 0.5 else ("🔴 FALSYFIKAT" if delta < -0.5 else "➖ NEUTRALNA")
    print(f"\n{'─'*70}")
    print(f"  Δ = {delta:+.2f}pp — {znak} (Prawo I)")
    print(f"  Czas: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
