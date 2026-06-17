"""
A/B W-329 — ktore mechanizmy uczenia online warto wlaczyc w LIVE (Prawo I).

W petla_live domyslnie tylko synapsy=True. MWU/Igrzyska/KsiegaWad/Gubernator = OFF.
Ten skrypt mierzy KAZDY z osobna i razem na portfelu 5-par (4h, tryb skaner),
by decydowac DANYMI, nie opinia. Zostawiamy w live tylko te, ktore poprawiaja wynik.

Uruchom: python narzedzia/ab_w329.py
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.backtest import backtest_portfel

PLIKI = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}

# Wspolna baza: tryb skaner (TRYB NAJLEPSZY) + synapsy (live default)
BAZA = dict(tryb_skaner=True, synapsy_rezimowe=True)

WARIANTY = {
    "BASELINE (synapsy)":      {},
    "+MWU":                    dict(mwu_learning=True),
    "+Igrzyska":               dict(igrzyska_learning=True),
    "+KsiegaWad":              dict(ksiega_wad=True),
    "+Gubernator":             dict(gubernator=True),
    "+MWU+Igrzyska":           dict(mwu_learning=True, igrzyska_learning=True),
    "WSZYSTKO":                dict(mwu_learning=True, igrzyska_learning=True,
                                    ksiega_wad=True, gubernator=True),
}


def zmierz(label: str, extra: dict):
    eng = backtest_portfel(PLIKI, "4h", **BAZA, **extra)
    s = eng.podsumowanie()
    zysk = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    return zysk, s.max_drawdown_pct, s.win_rate, s.total_trades


def main():
    print("\n" + "=" * 78)
    print("A/B W-329 — mechanizmy uczenia online w LIVE (portfel 5-par, 4h, skaner)")
    print("=" * 78)
    print(f"{'Wariant':<22} | {'Zysk%':>8} | {'MaxDD%':>7} | {'WR':>6} | {'Trades':>7} | {'Δ vs baza':>9}")
    print("-" * 78)

    baseline_zysk = None
    for label, extra in WARIANTY.items():
        zysk, dd, wr, tr = zmierz(label, extra)
        if baseline_zysk is None:
            baseline_zysk = zysk
            delta = "—"
        else:
            delta = f"{zysk - baseline_zysk:+.2f}pp"
        print(f"{label:<22} | {zysk:+7.2f}% | {dd:6.1%} | {wr:5.1%} | {tr:7d} | {delta:>9}")

    print("=" * 78)
    print("Werdykt: wlaczyc w live tylko warianty z Δ > 0 (Prawo I).")


if __name__ == "__main__":
    main()
