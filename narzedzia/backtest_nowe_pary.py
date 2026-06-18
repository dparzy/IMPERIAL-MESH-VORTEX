"""
Backtest nowych par — porownuje rozszerzony koszyk z baseline.

Uruchom PO pobierz_nowe_pary.py:
  python narzedzia/backtest_nowe_pary.py

Wynik: tabela porownawcza (zysk%, MaxDD, WR, trades) dla:
  A) Baseline 5-pair (BTC/ETH/SOL/BNB/DOGE) — 4h
  B) Rozszerzony koszyk +ADA/AVAX/XRP/PEPE — 4h
  C) Najlepsze 3 nowe pary solo — 4h
  D) Nowe pary na 1h (jezeli pobrano dane)
"""

import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.backtest import backtest_portfel


BASELINE = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}

NOWE_KANDYDATY_4H = {
    "ADAUSDT":  "dane/4h/MEXC_ADAUSDT_4h.csv",
    "AVAXUSDT": "dane/4h/MEXC_AVAXUSDT_4h.csv",
    "XRPUSDT":  "dane/4h/MEXC_XRPUSDT_4h.csv",
    "PEPEUSDT": "dane/4h/MEXC_PEPEUSDT_4h.csv",
}


def filtruj_dostepne(pliki: dict) -> dict:
    return {k: v for k, v in pliki.items() if os.path.exists(v)}


def raportuj(label: str, eng):
    s = eng.podsumowanie()
    pnl = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"  {label:<35} | {pnl:+7.2f}% | WR={s.win_rate:.1%}"
          f" | MaxDD={s.max_drawdown_pct:.1%} | trades={s.total_trades}")


def main():
    print("\n" + "=" * 70)
    print("BACKTEST NOWYCH PAR — IMPERIUM W-328")
    print("=" * 70)

    print("\n" + "-" * 70)
    print(f"{'Wariant':<35} | {'Zysk':>8} | {'WR':>6} | {'MaxDD':>7} | {'Trades':>7}")
    print("-" * 70)

    # A. Baseline
    eng_a = backtest_portfel(BASELINE, "4h", tryb_skaner=True)
    raportuj("A: Baseline 5-pair (BTC/ETH/SOL/BNB/DOGE)", eng_a)

    # B. Rozszerzony koszyk (wszystkie dostepne)
    nowe_dostepne = filtruj_dostepne(NOWE_KANDYDATY_4H)
    if nowe_dostepne:
        rozszerzony = {**BASELINE, **nowe_dostepne}
        eng_b = backtest_portfel(rozszerzony, "4h", tryb_skaner=True)
        raportuj(f"B: Rozszerzony ({len(rozszerzony)}-pair)", eng_b)

        # C. Kazda nowa para solo
        print()
        for sym, sciezka in nowe_dostepne.items():
            try:
                eng_c = backtest_portfel({sym: sciezka}, "4h", tryb_skaner=True)
                raportuj(f"C: {sym} solo", eng_c)
            except Exception as e:
                print(f"  C: {sym} BLAD: {e}")
    else:
        print("\n  UWAGA: Brak nowych plikow CSV w dane/4h/")
        print("  Uruchom najpierw: python narzedzia/pobierz_nowe_pary.py")

    # D. 1h backtest istniejacych par (dla porownania TF)
    pliki_1h_bazowe = {
        "BTCUSDT": "dane/godzinowe/Binance_BTCUSDT_1h.csv",
        "ETHUSDT": "dane/godzinowe/Binance_ETHUSDT_1h.csv",
        "SOLUSDT": "dane/godzinowe/Binance_SOLUSDT_1h.csv",
    }
    dostepne_1h = filtruj_dostepne(pliki_1h_bazowe)
    if dostepne_1h:
        print()
        try:
            eng_d = backtest_portfel(dostepne_1h, "1h", tryb_skaner=True)
            raportuj("D: 1h BTC/ETH/SOL (TF porownanie)", eng_d)
        except Exception as e:
            print(f"  D: 1h BLAD: {e}")

    print("=" * 70)
    print("\nWniosek: porownaj zysk% i MaxDD — dodaj te pary ktore:")
    print("  1. Maja zysk% > Baseline (nowa alfa)")
    print("  2. MaxDD nie gorszy niz baseline + 3pp (Prawo I)")
    print("  3. WR > 50% (szanse po stronie systemu)")


if __name__ == "__main__":
    main()
