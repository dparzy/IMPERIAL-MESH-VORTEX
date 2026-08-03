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


# Moduł wzorców trzyma regexy JAKO DANE, więc trafia sam w siebie — musi być pominięty.
_MODUL_WZORCOW = "imperium/biblioteki/ksiega_wad_kodu.py"


def _pomijany(p: Path) -> bool:
    """Czy ten plik jest wyłączony ze skanu — pytane W JEDNYM miejscu, przy skanowaniu.

    Zmierzone 2026-08-03: wyłączenie stało wyłącznie w `_filtruj_py`, czyli na drodze
    „pliki z gita". Plik podany JAWNIE (tak woła VIGIL w hooku PostToolUse) omijał je
    bokiem i dawał 5 fałszywych trafień — z własnych opisów wzorców. To ta sama klasa,
    co kontrakt append-only deklarowany w sześciu organach i egzekwowany przez zero:
    reguła zapisana przy jednym wejściu nie obowiązuje przy drugim. Fałszywki
    w narzędziu bramkowym są droższe niż jego brak, bo uczą przewijać jego wydruk.
    """
    try:
        wzgledna = p.resolve().relative_to(ROOT).as_posix()
    except (ValueError, OSError):
        return False
    return wzgledna == _MODUL_WZORCOW


def _filtruj_py(linie) -> set[str]:
    """Filtr wspólny: z listy nazw plików zostaw .py w imperium/ i narzedzia/.
    Za wyłączenia odpowiada `_pomijany` przy samym skanie — tu ich świadomie NIE ma,
    żeby nie istniały dwa miejsca decydujące o tym samym."""
    return {l for l in linie
            if l.endswith(".py") and l.startswith(("imperium/", "narzedzia/"))}


def _zmienione_py() -> list[Path]:
    pliki: set[str] = set()
    # diff (zmienione/staged) + untracked (nowe pliki — inaczej świeży moduł umyka skanowi).
    for args in (["diff", "--name-only", "HEAD"], ["diff", "--cached", "--name-only"],
                 ["ls-files", "--others", "--exclude-standard"]):
        try:
            out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                 text=True, timeout=20,
                                 encoding="utf-8", errors="replace").stdout
            pliki |= _filtruj_py(out.splitlines())
        except Exception:
            pass
    return [ROOT / p for p in sorted(pliki) if (ROOT / p).exists()]


def _py_ostatni_commit() -> list[Path]:
    """Pliki .py zmienione w OSTATNIM commicie (HEAD~1..HEAD) — do skanu na starcie sesji
    po SYNC pull (A4, uszczelnienie OTWARCIA 2026-07-19).

    Powód: skan zmienionych plików na starcie był no-op (czyste drzewo → „brak plików").
    Skan ostatniego commitu łapie regresje w świeżo pociągniętym/zacommitowanym kodzie.
    Pierwszy commit repo (brak HEAD~1) lub brak gita → [] (start się nie wywala, Prawo I)."""
    try:
        out = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                             cwd=ROOT, capture_output=True, text=True, timeout=20,
                             encoding="utf-8", errors="replace")
    except Exception:
        return []
    if out.returncode != 0:
        return []
    return [ROOT / p for p in sorted(_filtruj_py(out.stdout.splitlines()))
            if (ROOT / p).exists()]


def skanuj_pliki(pliki: list[Path], ksiega: KsiegaWadKodu) -> list[tuple[Path, dict]]:
    trafienia = []
    for p in pliki:
        if _pomijany(p):
            continue
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
    p.add_argument("--ostatni-commit", action="store_true",
                   help="skanuj .py zmienione w OSTATNIM commicie (start sesji po SYNC, A4)")
    p.add_argument("--falsa", action="store_true",
                   help="sweep INDEX FALSORUM: gdzie obalone twierdzenie wciąż jest "
                        "głoszone jako fakt (cały korpus .py+.md, bez historii)")
    args = p.parse_args()

    if args.falsa:
        from imperium.biblioteki.index_falsorum import przeszukaj, raport
        print(raport())
        return 2 if przeszukaj() else 0

    zasiej_startowe()                      # utwórz księgę z wzorcami jeśli pusta
    ksiega = KsiegaWadKodu()

    if args.lista:
        wzorce, checklista = ksiega.wzorce(), ksiega.checklista()
        print(f"🐞 KSIĘGA WAD KODU — {len(wzorce)} wzorców regex (auto-skan):")
        for w in wzorce:
            print(f"   [{w['kat']}] {w['opis']}\n       → {w['lekcja']}  ({w.get('zrodlo','')})")
        if checklista:
            print(f"\n📋 CHECKLISTA REVIEW — {len(checklista)} klas semantycznych "
                  "(przejrzyj ręcznie przed pushem, obok /code-review):")
            for w in checklista:
                print(f"   [{w['kat']}] {w['opis']}\n       → {w['lekcja']}  ({w.get('zrodlo','')})")
        return 0

    if args.plik:
        pliki = [ROOT / args.plik]
    elif args.ostatni_commit:
        pliki = _py_ostatni_commit()
    else:
        pliki = _zmienione_py()
    if not pliki:
        zrodlo = "w ostatnim commicie" if args.ostatni_commit else "zmienionych"
        print(f"🐞 Brak plików .py {zrodlo} do skanu.")
        return 0
    n_check = len(ksiega.checklista())
    przypomnienie = (f"   📋 Pamiętaj o checkliście review ({n_check} klas semantycznych): "
                     "python narzedzia/skan_wad_kodu.py --lista" if n_check else "")
    trafienia = skanuj_pliki(pliki, ksiega)
    if not trafienia:
        print(f"🐞 SKAN WAD KODU — czysto ✅ ({len(pliki)} plików, {len(ksiega.wzorce())} wzorców regex).")
        if przypomnienie:
            print(przypomnienie)
        return 0
    print(f"🐞 SKAN WAD KODU — {len(trafienia)} trafień (NUDGE — sprawdź, nie pewnik):")
    for p, t in trafienia:
        rel = p.relative_to(ROOT)
        print(f"   {rel}:{t['linia']}  [{t['kat']}] {t['opis']}\n       → {t['lekcja']}")
    if przypomnienie:
        print(przypomnienie)
    return 2


if __name__ == "__main__":
    sys.exit(main())
