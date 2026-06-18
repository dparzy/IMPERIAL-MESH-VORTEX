"""
A/B W-324 — Brama Momentum Bezwzględnego (TS Gate) vs brak bramy.

Hipoteza (Han/Kang/Ryu 2024, SSRN): w krypto time-series momentum > cross-sectional.
Skaner był 100% cross-sectional — zawsze wybierał TOP-N, nawet gdy cały koszyk stał.
W-324 dodaje min_bezwzgledny_ts: moneta musi ruszyć ≥ próg |ROC| w oknie lookback.
W martwym rynku (wszystkie <próg) → 0 wejść = suchy proch.

Test: 3 warianty progu na 4h, 5 par, TRYB NAJLEPSZY.
Uruchom: python narzedzia/ab_w324.py
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
    print(f"  {nazwa:<35}: Trade {s.total_trades:4d} | WR {s.win_rate:.1%} | "
          f"{s.kapital_koncowy:>12,.0f}$ ({pct:+.2f}%)")
    return pct, s.total_trades


def _bieg(bary_per, min_ts):
    return backtest_portfel(
        PLIKI_4H, interwal="4h", bary_per=bary_per,
        tryb_skaner=True, skaner_top_n=3, skaner_min_ts=min_ts,
        sizing_przekonania=True, compounding=True, filtr_asymetrii=True,
    )


def main():
    t0 = time.time()
    bary_per = _bary()
    print(f"⚙️  A/B W-324 — 4h, {LIMIT} barów/parę, 5 par. TS Gate: 0% vs 0.5% vs 1% vs 2%.\n")

    warianty = [
        ("BASELINE (min_ts=0.0%)", 0.0),
        ("TS-Gate 0.5% (0.005)",   0.005),
        ("TS-Gate 1.0% (0.010)",   0.010),
        ("TS-Gate 2.0% (0.020)",   0.020),
    ]
    wyniki = []
    for nazwa, min_ts in warianty:
        pct, tr = _raport(nazwa, _bieg({k: list(v) for k, v in bary_per.items()}, min_ts))
        wyniki.append((nazwa, pct, tr))

    best = max(wyniki, key=lambda x: x[1])
    baseline_pct = wyniki[0][1]
    print(f"\n{'─'*65}")
    print(f"  Najlepsza konfiguracja: {best[0]} ({best[1]:+.2f}%)")
    delta = best[1] - baseline_pct
    znak = "✅ POPRAWA" if delta > 0.5 else ("🔴 FALSYFIKAT" if delta < -0.5 else "➖ NEUTRALNA")
    print(f"  vs baseline: {delta:+.2f}pp — {znak} (Prawo I)")
    print(f"  Czas: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
