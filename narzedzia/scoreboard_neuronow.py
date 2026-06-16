"""
W-323c — SCOREBOARD KONTRYBUCJI NEURONÓW (mierzona baza do strojenia profili).

Uruchamia jeden backtest portfelowy z igrzyska_learning=True i drukuje ranking
neuronów (accuracy / stability / wynik / liczba sygnałów) na danym interwale.
To DOWÓD (Prawo I), które neurony realnie pomagają per styl — zamiast intuicji
przy NEURONY_STYLU. „Złoty Hełm" = lider; ogon listy = kandydaci do wykluczenia
ze stylu (jeśli niska trafność I niska kontrybucja — nie sam fakt „bo wolny").

Uruchom:  python narzedzia/scoreboard_neuronow.py
Zmienne:  LIMIT_4H (domyślnie 7500), STYL_SB (None=pełnia / SCALP / SWING / INVEST)
"""
import logging
import os

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
STYL = os.getenv("STYL_SB") or None


def main():
    bary = {s: wczytaj_csv(sc, interwal="4h", limit=LIMIT) for s, sc in PLIKI_4H.items()}
    print(f"⚙️  SCOREBOARD — 4h, {LIMIT} barów/parę, styl={STYL or 'PEŁNIA'}. Liczę...\n")
    eng = backtest_portfel(
        PLIKI_4H, interwal="4h", bary_per=bary, styl=STYL,
        tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
        compounding=True, filtr_asymetrii=True, igrzyska_learning=True,
    )
    ranking = getattr(eng, "ranking_neuronow", None)
    if not ranking:
        print("⚠️  Brak rankingu (żaden neuron nie został rozliczony).")
        return

    print(f"{'#':>3} {'KLUCZ':<10} {'WYNIK':>6} {'ACC':>6} {'STAB':>6} {'SYGN':>6}  RANGA")
    print("─" * 56)
    for i, r in enumerate(ranking, 1):
        print(f"{i:>3} {r['klucz']:<10} {r['wynik']:>6.3f} {r['accuracy']:>6.1%} "
              f"{r['stability']:>6.2f} {r['sygnaly']:>6}  {r['ranga']}")

    ogon = [r for r in ranking if r["accuracy"] < 0.45 and r["sygnaly"] >= 20]
    if ogon:
        print(f"\n🔎 Kandydaci do rewizji (acc<45% przy ≥20 sygn.): "
              f"{', '.join(r['klucz'] for r in ogon)}")
    print(f"\n🏆 Złoty Hełm: {ranking[0]['klucz']} (wynik {ranking[0]['wynik']:.3f})")


if __name__ == "__main__":
    main()
