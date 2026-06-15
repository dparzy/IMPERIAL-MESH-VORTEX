"""
Kalibracja progów wejścia pod 1h (W-321c). Cel: znaleźć konfigurację, która
na danych 1h daje dodatni edge (1h z domyślną konfig 4h traci −9.8%, W-321b).

Hipoteza: 1h jest szumniejsze → wyższe progi (min_adx, min_pewnosc) odsiewają
słabe wejścia. Mierzymy, nie zgadujemy (Prawo I).

Bary ładowane RAZ, siatka liczona sekwencyjnie (gc między biegami — kontrola RAM).
Cap przez MAX_BAROW (domyślnie 12000 ≈ 1.4 lat — szybka iteracja; zwycięzcę
waliduj osobno na 30000, tym samym oknie co W-321b).

Uruchom: python narzedzia/kalibracja_1h.py
"""
import gc
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
MAX_BAROW = int(os.getenv("MAX_BAROW", "12000"))

# Siatka: (min_adx, min_pewnosc, top_n). Pierwszy = baseline 4h-config (ref).
SIATKA = [
    (36.0, 0.70, 2),   # zwycięzca v1 (kotwica) — ref −6.4% na 12k
    (45.0, 0.70, 2),   # najlepszy ze wszystkich: −5.9%
    (45.0, 0.70, 1),   # top1 gorszy: −6.5%
    (36.0, 0.75, 1),
    (50.0, 0.75, 1),   # najostrzejszy: tylko najsilniejszy trend, jedna okazja
]


def main():
    t0 = time.time()
    print(f"⚙️  Kalibracja 1h — cap {MAX_BAROW} barów/parę (~{MAX_BAROW/24/365:.1f} lat). "
          f"{len(SIATKA)} konfiguracji.")

    bary_per = {sym: wczytaj_csv(sc, interwal="1h", limit=MAX_BAROW)
                for sym, sc in PLIKI_1H.items()}
    pierwszy = next(iter(bary_per.values()))
    import datetime as dt
    od = dt.datetime.utcfromtimestamp(pierwszy[0]["timestamp"] / 1000).date()
    do = dt.datetime.utcfromtimestamp(pierwszy[-1]["timestamp"] / 1000).date()
    print(f"   okno: {od} → {do} | barów/parę: {len(pierwszy)}\n")

    wyniki = []
    for i, (adx, pew, topn) in enumerate(SIATKA, 1):
        t1 = time.time()
        eng = backtest_portfel(
            PLIKI_1H, interwal="1h", bary_per=bary_per,
            tryb_skaner=True, skaner_top_n=topn, skaner_min_adx=adx,
            min_pewnosc=pew, sizing_przekonania=True,
            compounding=True, filtr_asymetrii=True,
        )
        s = eng.podsumowanie()
        pct = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
        wyniki.append((pct, adx, pew, topn, s.total_trades, s.win_rate))
        tag = " (baseline)" if (adx, pew, topn) == (20.0, 0.55, 3) else ""
        print(f"[{i}/{len(SIATKA)}] adx≥{adx} pew≥{pew} top{topn}{tag}: "
              f"{s.total_trades} tr, WR {s.win_rate:.1%}, {pct:+.1f}%  "
              f"({time.time()-t1:.0f}s)")
        del eng
        gc.collect()

    print("\n=== RANKING (po PnL%) ===")
    for pct, adx, pew, topn, tr, wr in sorted(wyniki, reverse=True):
        print(f"  {pct:+6.1f}%  | adx≥{adx} pew≥{pew} top{topn} | {tr} tr, WR {wr:.1%}")

    print(f"\n⏱️  Czas: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
