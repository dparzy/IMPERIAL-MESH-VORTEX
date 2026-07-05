"""
🏟️ ARENA ZASIL — domyka pętlę „graj → mierz → ucz się" (Prawo XVI/XXV).

Uruchamia pomiar IC roju (raport_ic.zbierz_ic) na lokalnych świecach i ZAPISUJE
wynik per neuron do bazy areny (arena_wyniki.db) przez arena_mcp.zapisz_pomiar.
Potem Claude czyta skuteczność roju narzędziem MCP `arena_pytaj` — bez ponownego
liczenia. Wiedza AKUMULUJE się między biegami/wachtami zamiast parować.

Rdzeń (zasil_z_ic) jest czysty i testowalny bez backtestu. CLI dokłada backtest.

Użycie (lokal — wymaga danych CSV):
    python narzedzia/arena_zasil.py                       # 4h, domyślny glob
    python narzedzia/arena_zasil.py --glob "dane/dzienne/*_d.csv" --interwal 1d
    python narzedzia/arena_zasil.py --nota "wachta 0000-1200"
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

from imperium.biblioteki.arena_baza import DEFAULT_DB, zapisz_pomiar  # noqa: E402


def zasil_z_ic(ic: dict, interwal: str, nota_extra: str = "",
               db_path=DEFAULT_DB, rodzaj: str = "IC") -> int:
    """Zapisuje słownik {neuron: IC} do bazy areny. Zwraca liczbę zapisanych wierszy.

    Pomija wartości nie-liczbowe/NaN (Prawo I: do bazy tylko realny pomiar).
    """
    zapisane = 0
    nota = f"{interwal}".strip()
    if nota_extra:
        nota = f"{nota} {nota_extra}".strip()
    for neuron, wartosc in ic.items():
        try:
            w = float(wartosc)
        except (TypeError, ValueError):
            continue
        if w != w:   # NaN
            continue
        zapisz_pomiar(rodzaj, str(neuron), w, nota, db_path=db_path)
        zapisane += 1
    return zapisane


def _cli() -> None:
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Zasil bazę areny wynikami IC (Prawo XVI)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--max-barow", type=int, default=None)
    p.add_argument("--nota", default="")
    args = p.parse_args()

    from narzedzia.raport_ic import zbierz_ic
    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print(f"Brak plików dla wzorca: {args.glob}")
        sys.exit(1)
    print(f"Liczę IC na {len(pliki)} parach ({args.interwal})...", file=sys.stderr, flush=True)
    w = zbierz_ic(pliki, args.interwal, okno=args.okno, max_barow=args.max_barow)
    n = zasil_z_ic(w["ic"], args.interwal, nota_extra=args.nota)
    print(f"✅ Zasilono bazę areny: {n} pomiarów IC ({w['pary']} par). "
          f"Claude czyta je narzędziem MCP arena_pytaj (rodzaj='IC').")


if __name__ == "__main__":
    _cli()
