"""
Runner testów Imperium — bez zależności zewnętrznych.

Uruchom:  python tests/run_tests.py

Odkrywa wszystkie funkcje test_* w plikach test_*.py, uruchamia je,
raportuje wynik. Działa też z pytest jeśli zainstalowany (pytest tests/).

Testuje TYLKO moduły niewymagające TA-Lib/numpy/API (czysty Python):
  - kalkulator_lewara (+ bezpiecznik AOA)
  - igrzyska (scoring neuronów)
  - pamiec_absolutna (logi JSONL)
"""

import sys, os, importlib, traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# AUTO-DISCOVERY (Prawo XV): każdy tests/test_*.py jest zbierany automatycznie.
# Sztywna lista cicho gubiła nowe pliki testów (test_walidacja, 2026-06-10) —
# nowy moduł testowy "istniał", ale nie był uruchamiany = martwy strażnik.
import glob as _glob

MODULY_TESTOWE = sorted(
    os.path.splitext(os.path.basename(p))[0]
    for p in _glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "test_*.py"))
)


def uruchom():
    zaliczone = 0
    oblane = 0
    bledy = []

    for nazwa_modulu in MODULY_TESTOWE:
        try:
            modul = importlib.import_module(f"tests.{nazwa_modulu}")
        except Exception as e:
            print(f"❌ Nie można zaimportować {nazwa_modulu}: {e}")
            oblane += 1
            continue

        funkcje = [f for f in dir(modul) if f.startswith("test_")]
        print(f"\n📋 {nazwa_modulu} ({len(funkcje)} testów)")

        for nazwa_f in funkcje:
            funkcja = getattr(modul, nazwa_f)
            try:
                funkcja()
                print(f"  ✅ {nazwa_f}")
                zaliczone += 1
            except AssertionError as e:
                print(f"  ❌ {nazwa_f}: {e}")
                oblane += 1
                bledy.append((nazwa_modulu, nazwa_f, str(e)))
            except Exception as e:
                print(f"  💥 {nazwa_f}: {type(e).__name__}: {e}")
                oblane += 1
                bledy.append((nazwa_modulu, nazwa_f, traceback.format_exc()))

    print("\n" + "═" * 60)
    print(f"  WYNIK: {zaliczone} zaliczone, {oblane} oblane "
          f"({zaliczone}/{zaliczone + oblane})")
    print("═" * 60)

    if bledy:
        print("\nSzczegóły błędów:")
        for modul, test, blad in bledy:
            print(f"\n  {modul}::{test}")
            print(f"    {blad}")
        return 1
    print("\n✅ Wszystkie testy zaliczone — Imperium gotowe.")
    return 0


if __name__ == "__main__":
    sys.exit(uruchom())
