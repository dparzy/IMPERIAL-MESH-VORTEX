"""
A/B W-323 — profil stylu vs pełny rój na TRYB NAJLEPSZY (4h, okno 2022→2026).
„Pełnia" = 70 neuronów (dziś). „Profil" = dedykowany zestaw SWING (neurony_dla_trybu).
Hipoteza: dedykacja neuronów do stylu poprawia sygnał (nie rozcieńcza). Prawo I.

4h mapuje na styl SWING (namiestnik.styl_interwalu) → testujemy SWING-profil.
Uruchom: python narzedzia/ab_w323.py
"""
import logging
import os
import time

logging.disable(logging.CRITICAL)

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from imperium.koloseum.backtest import backtest_portfel  # noqa: E402
from imperium.legiony.rejestr import neurony_dla_trybu, wszystkie_neurony  # noqa: E402

PLIKI_4H = {
    "BTCUSDT":  "dane/4h/Binance_BTCUSDT_4h.csv",
    "ETHUSDT":  "dane/4h/Binance_ETHUSDT_4h.csv",
    "SOLUSDT":  "dane/4h/Binance_SOLUSDT_4h.csv",
    "BNBUSDT":  "dane/4h/Binance_BNBUSDT_4h.csv",
    "DOGEUSDT": "dane/4h/Binance_DOGEUSDT_4h.csv",
}
LIMIT = int(os.getenv("LIMIT_4H", "7500"))
STYL = os.getenv("STYL_AB", "SWING")


def _bary():
    return {s: wczytaj_csv(sc, interwal="4h", limit=LIMIT) for s, sc in PLIKI_4H.items()}


def _raport(nazwa, eng):
    s = eng.podsumowanie()
    pct = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"=== {nazwa} ===")
    print(f"  Trade: {s.total_trades} | WR {s.win_rate:.1%} | "
          f"PnL {s.total_pnl_usdt:+,.0f} USDT ({pct:+.2f}%) | {s.kapital_koncowy:,.0f}$")
    return pct, s.total_trades


def _bieg(bary_per, styl):
    return backtest_portfel(
        PLIKI_4H, interwal="4h", bary_per=bary_per, styl=styl,
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True,
    )


def main():
    t0 = time.time()
    bary_per = _bary()
    pelnia = len(wszystkie_neurony())
    prof = len(neurony_dla_trybu(STYL))
    print(f"⚙️  A/B W-323 — 4h, {LIMIT} barów/parę. Pełnia ({pelnia}) vs profil {STYL} ({prof}).\n")

    pct0, tr0 = _raport(f"PEŁNIA ({pelnia} neuronów)",
                        _bieg({k: list(v) for k, v in bary_per.items()}, None))
    pct1, tr1 = _raport(f"PROFIL {STYL} ({prof} neuronów)",
                        _bieg({k: list(v) for k, v in bary_per.items()}, STYL))

    print(f"\n>>> IMPAKT PROFIL {STYL}: {pct1 - pct0:+.2f} pkt proc. PnL "
          f"({pct0:+.2f}% → {pct1:+.2f}%), trade {tr0}→{tr1}")
    print(f"⏱️  {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
