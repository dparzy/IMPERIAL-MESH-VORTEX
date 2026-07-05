"""
🐞 SKAN WAD KODU — heurystyczny łowca powtórek błędów (Księga Wad Kodu).

Skanuje zmienione pliki .py (git diff) przeciw znanym wzorcom błędów z recenzji.
Odpalaj PRZED push (obok `/code-review`) — łapie klasy, które już raz nas ugryzły.

  python narzedzia/skan_wad_kodu.py            # skan zmienionych .py (git)
  python narzedzia/skan_wad_kodu.py --lista    # pokaż całą księgę (checklist)
  python narzedzia/skan_wad_kodu.py plik.py    # skan konkretnego pliku

Kod wyjścia: 0 = czysto / lista; 2 = trafienia (do użycia w bramce/hooku).
To NUDGE, nie dowód (Prawo I) — trafienie = „sprawdź to", nie „to na pewno bug".
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from imperium.biblioteki.ksiega_wad_kodu import KsiegaWadKodu, zasiej_startowe  # noqa: E402


def _zmienione_py() -> list[Path]:
    pliki: set[str] = set()
    # diff (zmienione/staged) + untracked (nowe pliki — inaczej świeży moduł umyka skanowi).
    for args in (["diff", "--name-only", "HEAD"], ["diff", "--cached", "--name-only"],
                 ["ls-files", "--others", "--exclude-standard"]):
        try:
            out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                 text=True, timeout=20).stdout
            pliki |= {l for l in out.splitlines()
                      if l.endswith(".py") and l.startswith(("imperium/", "narzedzia/"))}
        except Exception:
            pass
    # Wyklucz sam moduł z definicjami wzorców (trzyma regexy jako dane — trafiałby w siebie).
    pliki.discard("imperium/biblioteki/ksiega_wad_kodu.py")
    return [ROOT / p for p in sorted(pliki) if (ROOT / p).exists()]


def skanuj_pliki(pliki: list[Path], ksiega: KsiegaWadKodu) -> list[tuple[Path, dict]]:
    trafienia = []
    for p in pliki:
        try:
            tekst = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for t in ksiega.skanuj(tekst):
            trafienia.append((p, t))
    return trafienia


def main() -> int:
    p = argparse.ArgumentParser(description="Skan wad kodu (Księga Wad Kodu)")
    p.add_argument("plik", nargs="?", help="konkretny plik (domyślnie: zmienione w git)")
    p.add_argument("--lista", action="store_true", help="pokaż całą księgę")
    args = p.parse_args()

    zasiej_startowe()                      # utwórz księgę z wzorcami jeśli pusta
    ksiega = KsiegaWadKodu()

    if args.lista:
        print(f"🐞 KSIĘGA WAD KODU — {len(ksiega.wszystkie())} wzorców:")
        for w in ksiega.wszystkie():
            print(f"   [{w['kat']}] {w['opis']}\n       → {w['lekcja']}  ({w.get('zrodlo','')})")
        return 0

    pliki = [ROOT / args.plik] if args.plik else _zmienione_py()
    if not pliki:
        print("🐞 Brak zmienionych plików .py do skanu.")
        return 0
    trafienia = skanuj_pliki(pliki, ksiega)
    if not trafienia:
        print(f"🐞 SKAN WAD KODU — czysto ✅ ({len(pliki)} plików, {len(ksiega.wszystkie())} wzorców).")
        return 0
    print(f"🐞 SKAN WAD KODU — {len(trafienia)} trafień (NUDGE — sprawdź, nie pewnik):")
    for p, t in trafienia:
        rel = p.relative_to(ROOT)
        print(f"   {rel}:{t['linia']}  [{t['kat']}] {t['opis']}\n       → {t['lekcja']}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
