"""
🔮 POMIAR HARUSPEXA — trafność predykcji reżimu na REALNYCH świecach (Prawo I + XXIV).

Odtwarza sekwencję reżimów z prawdziwych danych giełdy (klasyfikuj_rezim po rosnących
oknach, zero look-ahead) i mierzy trafność Haruspexa vs baseline „najczęstszy reżim".
Wynik = dowód, czy prognoza przejść reżimu ma wartość PRZED jakimkolwiek wpięciem
(ZASADA WPIĘCIA W ŚCIEŻKĘ DECYZYJNĄ — pomiar najpierw).

Pasek postępu na stderr (Prawo XXIV — widoczność operacyjna): budowa wskaźników po
oknach jest wolna, więc raportujemy [i/N] na żywo.

Użycie:
    python narzedzia/pomiar_haruspex.py --symbol BTCUSDT --interwal 4H --limit 500 --warmup 200
"""

import os
import sys
import argparse
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _sekwencja_rezimow(symbol: str, interwal: str, limit: int, warmup: int):
    """Buduje sekwencję reżimów z realnych świec (rosnące okna, bez look-ahead)."""
    from imperium.akwedukty.kwatermistrz_danych import DataLoader
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.legatus import klasyfikuj_rezim
    from imperium.koloseum.petla_live import _df_do_barow

    df = DataLoader().fetch(symbol.replace("USDT", "/USDT"), timeframe=interwal, limit=limit)
    bary = _df_do_barow(df, symbol, interwal)
    budowniczy = BudowniczyWskaznikow()

    sekwencja = []
    n = len(bary)
    for i in range(warmup, n):
        wsk = budowniczy.zbuduj(bary[:i])
        sekwencja.append(klasyfikuj_rezim(wsk))
        if (i - warmup) % 20 == 0 or i == n - 1:
            print(f"\r[{i - warmup + 1}/{n - warmup}] klasyfikuję reżimy — {symbol} {interwal}",
                  end="", file=sys.stderr, flush=True)
    print("", file=sys.stderr)
    return sekwencja


def main(argv=None):
    p = argparse.ArgumentParser(description="Pomiar trafności Haruspexa na realnych świecach.")
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--interwal", default="4H")
    p.add_argument("--limit", type=int, default=500)
    p.add_argument("--warmup", type=int, default=200, help="ile pierwszych barów na rozgrzewkę wskaźników")
    p.add_argument("--min-obserwacji", type=int, default=5)
    p.add_argument("--prog-zmiany", type=float, default=0.5,
                   help="P(następny≠obecny) > tego → ostrzeżenie zmiany (domyślnie 0.5)")
    a = p.parse_args(argv)

    from imperium.koloseum.haruspex import Haruspex

    seq = _sekwencja_rezimow(a.symbol, a.interwal, a.limit, a.warmup)
    if not seq:
        print("Brak sekwencji (za mało danych).", file=sys.stderr)
        return 1

    h = Haruspex(min_obserwacji=a.min_obserwacji, prog_zmiany=a.prog_zmiany)
    raport = h.oszacuj_trafnosc(seq)

    # Zbuduj pełną macierz (na całej sekwencji, do podglądu)
    hpelny = Haruspex(min_obserwacji=a.min_obserwacji)
    for r in seq:
        hpelny.dodaj_rezim(r)

    print(f"\n🔮 HARUSPEX — pomiar {a.symbol} {a.interwal} ({len(seq)} reżimów, warmup={a.warmup})")
    print(f"   Rozkład reżimów: {dict(Counter(seq))}")
    print(f"   Prognoz (nie-milczących): {raport.n_prognoz} | milczeń: {raport.n_milczen}")
    print(f"   TRAFNOŚĆ Haruspexa: {raport.trafnosc:.1%}")
    print(f"   Baseline słaby (najczęstszy reżim): {raport.baza_czestosci:.1%}")
    print(f"   Baseline MOCNY (persystencja: następny=obecny): {raport.baza_persystencji:.1%}")
    przewaga = raport.trafnosc - raport.baza_persystencji
    print(f"   Przewaga nad persystencją: {przewaga:+.1%}  "
          f"{'✅ realna wartość (przewiduje ZMIANY)' if przewaga > 0.005 else '⚠️ ≈ persystencja (nie bije lepkości reżimu)'}")
    print(f"   Brier (0=idealny): {raport.brier:.4f}")
    # Sygnał ZMIANY — właściwa wartość organu (rzadkie, ważne zdarzenia):
    nz = raport.n_zmian_faktycznych
    recall = raport.zmiany_zlapane / nz if nz else 0.0
    ostrzezen = raport.zmiany_zlapane + raport.zmiany_falszywe
    precyzja = raport.zmiany_zlapane / ostrzezen if ostrzezen else 0.0
    print("   ── Sygnał ZMIANY reżimu (czy_zmiana_prawdopodobna) ──")
    print(f"   Realnych zmian: {nz} | ostrzeżeń: {ostrzezen} "
          f"(trafnych {raport.zmiany_zlapane}, fałszywych {raport.zmiany_falszywe})")
    print(f"   Recall zmian: {recall:.1%} | Precyzja: {precyzja:.1%}  "
          f"{'✅ sygnał ma wartość' if (recall > 0.1 and precyzja > 0.3) else '⚠️ sygnał słaby'}")
    print("   Macierz przejść P(następny | obecny):")
    for z_rezimu, rozklad in sorted(hpelny.macierz().items()):
        top = sorted(rozklad.items(), key=lambda kv: -kv[1])[:3]
        print(f"     {z_rezimu:14s} → " + ", ".join(f"{do}:{p:.0%}" for do, p in top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
