"""
🎯 RAPORT WAŻNOŚCI NEURONÓW — Feature Importance MDA+SFI (López de Prado, W-355).

Odkopuje moduł `imperium/legiony/feature_importance.py` (był gotowy + testy, ale bez
wejścia — Prawo XV). Uruchamia backtest(zbieraj_sygnaly=True) na prawdziwych świecach,
zbiera per bar {neuron: kierunek} + etykietę forward (znak zwrotu następnego baru) i liczy:

  • MDA (Mean Decrease Accuracy) — permutacyjna ważność: o ile spada trafność roju gdy
    zepsujemy sygnał tego neuronu. MDA ≤ 0 → neuron nie pomaga (martwy głos/redundant).
  • SFI (Single Feature Importance) — % poprawnych sygnałów LONG/SHORT osobno.

LdP: „Backtesting is not a research tool. Feature importance is."

Opcjonalnie zapisuje MDA per neuron do bazy areny (rodzaj='WAZNOSC') — Claude czyta
MCP-em arena_pytaj. Dane rynkowe są LOKALNE (poza gitem) — uruchamiaj na laptopie:

    python narzedzia/raport_waznosci.py
    python narzedzia/raport_waznosci.py --glob "dane/dzienne/*_d.csv" --interwal 1d --do-areny
"""
from __future__ import annotations

import argparse
import glob as _glob
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def zbierz_sygnaly(pliki, interwal: str, okno: int = 250, max_barow=None):
    """Uruchamia backtest(zbieraj_sygnaly) per plik; scala historię sygnałów+wyników."""
    from imperium.koloseum.backtest import backtest
    hist_syg: list = []
    hist_wyn: list = []
    pary = 0
    n = len(pliki)
    for i, plik in enumerate(pliki, 1):
        print(f"  [{i}/{n}] {Path(plik).name} — zbieram sygnały...", file=sys.stderr, flush=True)
        try:
            eng = backtest(plik, interwal, okno=okno, max_barow=max_barow,
                           auto_rezim=True, zbieraj_sygnaly=True)
        except Exception as e:  # noqa: BLE001 — pojedyncza para nie wywala raportu
            print(f"  ⚠️ {Path(plik).name}: {e}", file=sys.stderr, flush=True)
            continue
        hist_syg.extend(getattr(eng, "historia_sygnalow", []))
        hist_wyn.extend(getattr(eng, "historia_wynikow", []))
        pary += 1
    return hist_syg, hist_wyn, pary


def raport(pliki, interwal: str, okno: int = 250, max_barow=None,
           do_areny: bool = False, n_permutacji: int = 20) -> str:
    from imperium.legiony.feature_importance import raport_waznosci
    hist_syg, hist_wyn, pary = zbierz_sygnaly(pliki, interwal, okno=okno, max_barow=max_barow)
    if len(hist_syg) < 10:
        return ("🎯 RAPORT WAŻNOŚCI — za mało obserwacji "
                f"({len(hist_syg)}). Potrzeba pełniejszej historii/więcej par.")
    rap = raport_waznosci(hist_syg, hist_wyn, n_permutacji=n_permutacji)

    if do_areny:
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        wiersze = [("WAZNOSC", w.klucz, float(w.mda), f"{interwal} MDA {pary}par")
                   for w in rap.rankowanie if not w.pominiety]
        zapisano = zapisz_pomiary(wiersze)
        koda = f"\n💾 Zapisano {zapisano} pomiarów MDA do bazy areny (rodzaj='WAZNOSC')."
    else:
        koda = "\n(dodaj --do-areny by zapisać MDA do bazy — Claude czyta MCP arena_pytaj)"

    naglowek = f"🎯 RAPORT WAŻNOŚCI ROJU — {pary} par, interwał {interwal}\n"
    return naglowek + str(rap) + koda


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Raport ważności neuronów (MDA/SFI, W-355)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--max-barow", type=int, default=None)
    p.add_argument("--permutacje", type=int, default=20)
    p.add_argument("--do-areny", action="store_true", help="zapisz MDA do bazy areny")
    args = p.parse_args()
    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print(f"Brak plików dla wzorca: {args.glob} (dane są lokalne — pobierz je najpierw)")
        sys.exit(1)
    print(raport(pliki, args.interwal, okno=args.okno, max_barow=args.max_barow,
                 do_areny=args.do_areny, n_permutacji=args.permutacje))
