#!/usr/bin/env python3
"""
📊 STATUS IMPERIUM — pulpit jednego spojrzenia (Prawo XVII)

Uruchom:
    python narzedzia/status.py

Pokazuje:
  • Faza i wersja projektu
  • Żywy rój: neurony / zwiadowcy / elitarne / strategie / testy
  • Ostatni wpis LOG_ZMIAN
  • Kolejne kroki z ROADMAP
  • Stan git (gałąź, uncommitted, last commit)
  • Wynik audytu spójności (Prawo XXI)
"""

import os
import re
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

W = 60  # szerokość ramki


def _sep(char="─"):
    return char * W


def _box(title: str):
    print(f"\n┌{'─' * (W - 2)}┐")
    print(f"│ {title:<{W - 3}}│")
    print(f"└{'─' * (W - 2)}┘")


def _czytaj(sciezka: str) -> str:
    try:
        with open(os.path.join(ROOT, sciezka), encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _run(cmd: str) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=ROOT)
        return r.stdout.strip()
    except Exception:
        return "(błąd)"


def sekcja_meta():
    _box("🏛️  IMPERIUM — STATUS (Prawo XVII)")
    indeks = _czytaj("docs/INDEKS_IMPERIUM.md")
    wersja = re.search(r"\*\*Wersja\*\*\s*\|\s*([^\n|]+)", indeks)
    faza = re.search(r"\*\*Faza\*\*\s*\|\s*([^\n|]+)", indeks)
    data_ind = re.search(r"\*\*Data\*\*\s*\|\s*([^\n|]+)", indeks)
    print(f"  Wersja : {wersja.group(1).strip() if wersja else '?'}")
    print(f"  Faza   : {faza.group(1).strip() if faza else '?'}")
    print(f"  Dziś   : {date.today()}")
    print(f"  Indeks : {data_ind.group(1).strip() if data_ind else '?'}")


def sekcja_roj():
    _box("⚔️  ŻYWY ROJ")
    try:
        from imperium.legiony.rejestr import (
            wszystkie_neurony, wszyscy_zwiadowcy, raport_potencjalu, raport_elity,
        )
        n = wszystkie_neurony()
        z = wszyscy_zwiadowcy()
        p = raport_potencjalu()
        e = raport_elity()

        print(f"  Neurony    : {len(n):3d}  (aktywne: {p['neurony_aktywne']}, "
              f"wyciszone: {p['neurony_wyciszone']})")
        print(f"  Zwiadowcy  : {len(z):3d}  (aktywni: {p['zwiadowcy_aktywni']}, "
              f"wyciszeni: {p['zwiadowcy_wyciszeni']})")
        print(f"  Elitarne   : {e['lacznie_elite']:3d}  (Prawo XX)")

        try:
            from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
            print(f"  Strategie  : {len(wszystkie_strategie()):3d}")
        except Exception:
            print("  Strategie  :  ? (moduł niedostępny)")

        kat = sorted({x.KATEGORIA for x in n})
        print(f"  Kategorie  : {kat}")

    except Exception as ex:
        print(f"  ❌ Błąd ładowania roju: {ex}")


def sekcja_testy():
    _box("🧪 TESTY")
    wynik = _run("python tests/run_tests.py 2>&1 | tail -5")
    for line in wynik.splitlines():
        print(f"  {line}")


def sekcja_log():
    _box("📜 OSTATNI WPIS LOG_ZMIAN")
    log = _czytaj("docs/LOG_ZMIAN.md")
    # Znajdź pierwsze sekcję ## YYYY-MM-DD
    m = re.search(r"(## \d{4}-\d{2}-\d{2}[^\n]*\n(?:.*\n){0,8})", log)
    if m:
        for line in m.group(1).strip().splitlines():
            print(f"  {line}")
    else:
        print("  (brak wpisu)")


def sekcja_roadmap():
    _box("🗺️  NASTĘPNE KROKI (ROADMAP)")
    road = _czytaj("docs/ROADMAP_IMPERIUM.md")
    if not road:
        print("  (brak ROADMAP_IMPERIUM.md)")
        return
    # Szukaj sekcji TODO / NASTĘPNE / KROK
    lines = road.splitlines()
    printing = False
    count = 0
    for line in lines:
        if re.search(r"(TODO|NASTĘPNE|KROK|Faza\s*1|Faza\s*2)", line, re.I):
            printing = True
        if printing:
            print(f"  {line}")
            count += 1
            if count >= 12:
                print("  ...")
                break


def sekcja_git():
    _box("🌿 GIT")
    branch = _run("git rev-parse --abbrev-ref HEAD")
    last_commit = _run("git log -1 --format='%h %s (%ar)'")
    status = _run("git status --short")
    ahead = _run("git rev-list --count @{u}..HEAD 2>/dev/null || echo 0")

    print(f"  Gałąź       : {branch}")
    print(f"  Last commit  : {last_commit}")
    print(f"  Ahead origin : {ahead} commit(ów)")
    if status:
        print(f"  Niezatwierdzone:")
        for line in status.splitlines()[:10]:
            print(f"    {line}")
    else:
        print("  Niezatwierdzone: ✅ czyste drzewo")


def sekcja_audyt():
    _box("🔬 AUDYT SPÓJNOŚCI (Prawo XXI)")
    try:
        sys.path.insert(0, os.path.join(ROOT, "narzedzia"))
        # Importuj ze ścieżki, nie jako pakiet
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "audyt_spojnosci",
            os.path.join(ROOT, "narzedzia", "audyt_spojnosci.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        bledy, info = mod.audyt()
        if bledy:
            print("  🚨 ROZBIEŻNOŚCI:")
            for b in bledy:
                print(f"    ❌ {b}")
        else:
            print("  ✅ pełna harmonia")
            for i in info:
                print(f"     • {i}")
    except Exception as ex:
        print(f"  ❌ Błąd audytu: {ex}")


def main():
    sekcja_meta()
    sekcja_roj()
    sekcja_testy()
    sekcja_log()
    sekcja_roadmap()
    sekcja_git()
    sekcja_audyt()
    print(f"\n{'═' * W}")
    print("  Vitruviusz: 'Status to dowód. Milczenie to kłamstwo.'")
    print(f"{'═' * W}\n")


if __name__ == "__main__":
    main()
