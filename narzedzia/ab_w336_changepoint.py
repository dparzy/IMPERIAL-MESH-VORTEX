"""
A/B W-336 — czy neuron CP-01 (CUSUM change-point) POMAGA (Prawo I/XVI).

Portfel z CP-01 WLACZONYM (stan obecny) vs WYCISZONYM (DOSTEPNY=False) na tym samym
oknie. C-01 ozywa tylko w pętli portfelowej (wstrzykuje CROSS_RS), więc to uczciwy
test wartosci nowej osi przekrojowej. delta>0 → zostawiamy; inaczej → wyciszenie.

Uruchom: python narzedzia/ab_w336_changepoint.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.backtest import backtest_portfel
from imperium.akwedukty.czytnik_csv import wczytaj_csv
from imperium.legiony.neurony.rezim_zmiana import NeuronChangePoint

PLIKI = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}
N_BAROW = 1500
BAZA = dict(tryb_skaner=True, synapsy_rezimowe=True, cache_wskaznikow=True)


def _bary():
    out = {}
    for sym, sc in PLIKI.items():
        b = wczytaj_csv(sc, interwal="4h")
        out[sym] = b[-N_BAROW:] if len(b) > N_BAROW else b
    return out


def zmierz(bary):
    eng = backtest_portfel(PLIKI, "4h", bary_per={k: list(v) for k, v in bary.items()}, **BAZA)
    s = eng.podsumowanie()
    return (s.kapital_koncowy / s.kapital_startowy - 1) * 100, s.max_drawdown_pct, s.total_trades


def main():
    bary = _bary()
    print(f"\nA/B W-336 — neuron CP-01 CUSUM change-point (5-par, 4h, {N_BAROW} barow)")
    print(f"{'Wariant':<28} | {'Zysk%':>8} | {'MaxDD%':>7} | {'Trades':>7}")
    print("-" * 60)

    z1, dd1, t1 = zmierz(bary)
    print(f"{'CP-01 WLACZONY':<28} | {z1:+7.2f}% | {dd1:6.1%} | {t1:7d}", flush=True)

    NeuronChangePoint.DOSTEPNY = False
    try:
        z2, dd2, t2 = zmierz(bary)
    finally:
        NeuronChangePoint.DOSTEPNY = True
    print(f"{'CP-01 WYCISZONY':<28} | {z2:+7.2f}% | {dd2:6.1%} | {t2:7d}", flush=True)

    print("-" * 60)
    delta = z1 - z2
    print(f"Delta (wlaczony - wyciszony): {delta:+.2f}pp")
    print("Werdykt:", "CP-01 POMAGA — zostawic" if delta > 0
          else "CP-01 NEUTRALNY/SZKODZI — rozwazyc wyciszenie (Prawo I)")


if __name__ == "__main__":
    main()
