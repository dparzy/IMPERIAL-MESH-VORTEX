"""
A/B W-329 — ktore mechanizmy uczenia online warto wlaczyc w LIVE (Prawo I).

W petla_live domyslnie tylko synapsy=True. MWU/Igrzyska/KsiegaWad/Gubernator = OFF.
Mierzy KAZDY z osobna na portfelu 5-par (4h, tryb skaner). Bary ograniczone do
ostatnich N (szybkosc) — wspolne dla wszystkich wariantow (uczciwe porownanie).

Uruchom:
  python narzedzia/ab_w329.py            # wszystkie warianty
  python narzedzia/ab_w329.py +MWU       # tylko jeden wariant (do tla)
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.backtest import backtest_portfel
from imperium.akwedukty.czytnik_csv import wczytaj_csv

PLIKI = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}

N_BAROW = 1500  # ostatnie ~1500 barow 4h (~8 mies) — szybko, wspolne dla wariantow

BAZA = dict(tryb_skaner=True, synapsy_rezimowe=True)

WARIANTY = {
    "BASELINE (synapsy)":      {},
    "+MWU":                    dict(mwu_learning=True),
    "+Igrzyska":               dict(igrzyska_learning=True),
    "+KsiegaWad":              dict(ksiega_wad=True),
    "+Gubernator":             dict(gubernator=True),
    "WSZYSTKO":                dict(mwu_learning=True, igrzyska_learning=True,
                                    ksiega_wad=True, gubernator=True),
}


def _bary_z_limitem():
    """Wstepnie laduje bary, tnie do ostatnich N (wspolne dla wszystkich wariantow)."""
    out = {}
    for sym, sc in PLIKI.items():
        b = wczytaj_csv(sc, interwal="4h")
        out[sym] = b[-N_BAROW:] if len(b) > N_BAROW else b
    return out


def zmierz(extra: dict, bary_per: dict):
    eng = backtest_portfel(PLIKI, "4h", bary_per={k: list(v) for k, v in bary_per.items()},
                           **BAZA, **extra)
    s = eng.podsumowanie()
    zysk = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    return zysk, s.max_drawdown_pct, s.win_rate, s.total_trades


def main():
    bary = _bary_z_limitem()
    wybrany = sys.argv[1] if len(sys.argv) > 1 else None

    print(f"\nA/B W-329 — uczenie online w LIVE (5-par, 4h, ostatnie {N_BAROW} barow)")
    print(f"{'Wariant':<22} | {'Zysk%':>8} | {'MaxDD%':>7} | {'WR':>6} | {'Trades':>7}")
    print("-" * 66)

    for label, extra in WARIANTY.items():
        if wybrany and label != wybrany:
            continue
        zysk, dd, wr, tr = zmierz(extra, bary)
        print(f"{label:<22} | {zysk:+7.2f}% | {dd:6.1%} | {wr:5.1%} | {tr:7d}", flush=True)


if __name__ == "__main__":
    main()
