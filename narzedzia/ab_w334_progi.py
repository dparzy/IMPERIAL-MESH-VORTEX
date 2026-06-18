"""
A/B W-334 — czy progi adaptacyjne RSI/ADX POMAGAJA (Prawo I).

Porownuje portfel z progami ADAPTACYJNYMI (stan obecny) vs SZTYWNYMI (30/70, 25).
Sztywne wymuszamy monkeypatchem progi_rsi/prog_adx na stale bazowe. Ten sam
window, te same bary. Jesli adaptacyjne <= sztywne → nie pomaga → rozwazyc cofniecie.

Uruchom: python narzedzia/ab_w334_progi.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.backtest import backtest_portfel
from imperium.akwedukty.czytnik_csv import wczytaj_csv
import imperium.legiony.progi_adaptacyjne as PA

PLIKI = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}
N_BAROW = 1500
BAZA = dict(tryb_skaner=True, synapsy_rezimowe=True)


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
    print(f"\nA/B W-334 — progi adaptacyjne RSI/ADX (5-par, 4h, {N_BAROW} barow)")
    print(f"{'Wariant':<28} | {'Zysk%':>8} | {'MaxDD%':>7} | {'Trades':>7}")
    print("-" * 60)

    # ADAPTACYJNE (stan obecny)
    z1, dd1, t1 = zmierz(bary)
    print(f"{'PROGI ADAPTACYJNE':<28} | {z1:+7.2f}% | {dd1:6.1%} | {t1:7d}", flush=True)

    # SZTYWNE — monkeypatch na bazowe
    _orig_rsi, _orig_adx = PA.progi_rsi, PA.prog_adx
    PA.progi_rsi = lambda rezim=None, atr_p=None: (PA.RSI_DOLNY_BAZA, PA.RSI_GORNY_BAZA)
    PA.prog_adx = lambda rezim=None, atr_p=None: PA.ADX_BAZA
    # Neurony zaimportowaly nazwy bezposrednio — podmieniamy tam tez
    import imperium.legiony.neurony.momentum as MOM
    import imperium.legiony.neurony.trend as TRE
    MOM.progi_rsi = PA.progi_rsi
    TRE.prog_adx = PA.prog_adx
    try:
        z2, dd2, t2 = zmierz(bary)
    finally:
        PA.progi_rsi, PA.prog_adx = _orig_rsi, _orig_adx
        MOM.progi_rsi = _orig_rsi
        TRE.prog_adx = _orig_adx
    print(f"{'PROGI SZTYWNE (30/70, 25)':<28} | {z2:+7.2f}% | {dd2:6.1%} | {t2:7d}", flush=True)

    print("-" * 60)
    delta = z1 - z2
    print(f"Delta (adaptacyjne - sztywne): {delta:+.2f}pp")
    print("Werdykt:", "ADAPTACYJNE POMAGAJA — zostawic" if delta > 0
          else "ADAPTACYJNE NEUTRALNE/SZKODZA — rozwazyc cofniecie (Prawo I)")


if __name__ == "__main__":
    main()
