#!/usr/bin/env python3
"""
🔬 AUDYT SPÓJNOŚCI IMPERIUM — silnik Prawa XXI (KROK 0)

Uruchamiany automatycznie przez hooki Claude Code (SessionStart + Stop) oraz ręcznie:
    python narzedzia/audyt_spojnosci.py            # raport + exit code
    python narzedzia/audyt_spojnosci.py --cichy     # tylko gdy są błędy

Sprawdza 4 warstwy spójności (zgodnie z ZASADY_FUNDAMENTALNE.md § PRAWO XXI):
  Warstwa 1 — żywy rój:        liczby, kategorie, elity, klucze
  Warstwa 2 — infrastruktura:  WAGI_REZIMU vs KAT w kodzie
  Warstwa 3 — dokumentacja:    MANIFEST klucze vs kod, liczby README/MANIFEST/CLAUDE

Exit code:
  0 = pełna spójność (Imperium gotowe)
  1 = wykryto rozbieżność (złamanie Prawa XXI — STOP, napraw)

Zasada: ten skrypt NIE liczy z pamięci. Wszystkie liczby pochodzą z żywego kodu.
"""

import os
import re
import sys
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Litery KATEGORII dozwolone w kodzie (legenda — jedyne źródło prawdy)
LEGENDA_KAT = set("MTVFOLRSAKEGm")


def _czytaj(sciezka: str) -> str:
    with open(os.path.join(ROOT, sciezka), encoding="utf-8") as f:
        return f.read()


def audyt() -> list:
    """Zwraca listę błędów (pusta = spójność)."""
    bledy = []
    info = []

    # ── WARSTWA 1: ŻYWY ROJ ────────────────────────────────────────────────
    try:
        from imperium.legiony.rejestr import (
            wszystkie_neurony, wszyscy_zwiadowcy, raport_potencjalu, raport_elity,
        )
        neurony = wszystkie_neurony()
        zwiadowcy = wszyscy_zwiadowcy()
        pot = raport_potencjalu()
        eli = raport_elity()

        n_neuronow = len(neurony)
        n_zwiadowcow = len(zwiadowcy)
        kat_kodu = {n.KATEGORIA for n in neurony}
        kat_zwiad = {getattr(z, "KATEGORIA", "?") for z in zwiadowcy}

        info.append(f"Neurony: {n_neuronow} (aktywne {pot['neurony_aktywne']}, "
                    f"wyciszone {pot['neurony_wyciszone']})")
        info.append(f"Zwiadowcy: {n_zwiadowcow} (aktywni {pot['zwiadowcy_aktywni']}, "
                    f"wyciszeni {pot['zwiadowcy_wyciszeni']})")
        info.append(f"Elitarne (Prawo XX): {eli['lacznie_elite']}")
        info.append(f"Kategorie w kodzie: {sorted(kat_kodu)}")

        # Reguła 2: KATEGORIA ∈ legenda
        zle_kat = [(n.KLUCZ, n.KATEGORIA) for n in neurony if n.KATEGORIA not in LEGENDA_KAT]
        if zle_kat:
            bledy.append(f"[W1] Neurony z nieprawidłową KATEGORIA: {zle_kat}")

        # Reguła 6: ELITARNY=True ⇒ niepusty POWOD_ELITARNOSCI
        zle_elity = [n.KLUCZ for n in neurony
                     if getattr(n, "ELITARNY", False) and not getattr(n, "POWOD_ELITARNOSCI", "")]
        zle_elity += [z.KLUCZ for z in zwiadowcy
                      if getattr(z, "ELITARNY", False) and not getattr(z, "POWOD_ELITARNOSCI", "")]
        if zle_elity:
            bledy.append(f"[W1] ELITARNY bez POWOD_ELITARNOSCI: {zle_elity}")

        # Reguła: brak duplikatów kluczy
        klucze = [n.KLUCZ for n in neurony]
        dup = {k for k in klucze if klucze.count(k) > 1}
        if dup:
            bledy.append(f"[W1] Zduplikowane klucze neuronów: {sorted(dup)}")

    except Exception as e:
        bledy.append(f"[W1] Nie udało się załadować żywego roju: {e}")
        return bledy + ["(audyt przerwany — napraw import)"]

    # ── WARSTWA 2A: WAGI_REZIMU vs KAT ─────────────────────────────────────
    try:
        from imperium.legiony.legatus import WAGI_REZIMU
        try:
            from imperium.legiony.legatus import WAGI_REZIMU_PLANOWANE
        except ImportError:
            WAGI_REZIMU_PLANOWANE = set()

        kat_wszystkie = kat_kodu | kat_zwiad
        martwe = [(r, k) for r, m in WAGI_REZIMU.items() for k in m
                  if k != "_default" and k not in kat_wszystkie and k not in WAGI_REZIMU_PLANOWANE]
        if martwe:
            bledy.append(f"[W2A] Martwe litery KAT w WAGI_REZIMU (brak neuronu, brak w PLANOWANE): {martwe}")
    except Exception as e:
        bledy.append(f"[W2A] Błąd sprawdzania WAGI_REZIMU: {e}")

    # ── WARSTWA 3: MANIFEST klucze vs kod ──────────────────────────────────
    try:
        txt = _czytaj("docs/MANIFEST_KODU.md")
        if "## ⚡" in txt and "## 📋" in txt:
            sekcja = txt.split("## ⚡")[1].split("## 📋")[0]
            mkeys = set(re.findall(r"^\|\s*([A-Z][\w-]+)", sekcja, re.M)) - {"KLUCZ"}
            ckeys = {n.KLUCZ for n in neurony}
            tylko_m = mkeys - ckeys
            tylko_c = ckeys - mkeys
            if tylko_m:
                bledy.append(f"[W3] Klucze w MANIFEST, brak w kodzie: {sorted(tylko_m)}")
            if tylko_c:
                bledy.append(f"[W3] Klucze w kodzie, brak w MANIFEST: {sorted(tylko_c)}")
        else:
            bledy.append("[W3] MANIFEST_KODU.md — brak sekcji '## ⚡ NEURONY ZAIMPLEMENTOWANE'")
    except Exception as e:
        bledy.append(f"[W3] Błąd sprawdzania MANIFEST: {e}")

    # ── WARSTWA 3: LICZBY w dokumentach ────────────────────────────────────
    try:
        readme = _czytaj("README.md")
        manifest = _czytaj("docs/MANIFEST_KODU.md")
        claude = _czytaj("CLAUDE.md")

        rn = re.search(r"(\d+) zaimplementowane", readme)
        if rn and int(rn.group(1)) != n_neuronow:
            bledy.append(f"[W3] README neurony={rn.group(1)} ≠ kod={n_neuronow}")

        mn = re.search(r"(\d+) neurony \(zarejestrowane", manifest)
        if mn and int(mn.group(1)) != n_neuronow:
            bledy.append(f"[W3] MANIFEST neurony={mn.group(1)} ≠ kod={n_neuronow}")

        # liczba praw: CLAUDE vs ZASADY (policz nagłówki PRAWO w zasadach)
        zasady = _czytaj("ZASADY_FUNDAMENTALNE.md")
        praw_w_zasadach = len(set(re.findall(r"PRAWO ([IVXL]+) —", zasady)))
        cp = re.search(r"(\d+) Prawami", claude)
        if cp and praw_w_zasadach and int(cp.group(1)) != praw_w_zasadach:
            bledy.append(f"[W3] CLAUDE praw={cp.group(1)} ≠ ZASADY praw={praw_w_zasadach}")
    except Exception as e:
        bledy.append(f"[W3] Błąd sprawdzania liczb w dokumentach: {e}")

    return bledy, info


def main():
    cichy = "--cichy" in sys.argv
    wynik = audyt()
    bledy, info = wynik if isinstance(wynik, tuple) else (wynik, [])

    if bledy:
        print("🚨 AUDYT SPÓJNOŚCI — WYKRYTO ROZBIEŻNOŚCI (złamanie Prawa XXI):", file=sys.stderr)
        for b in bledy:
            print(f"  ❌ {b}", file=sys.stderr)
        print("\n→ STOP. Napraw spójność zanim zaczniesz/zakończysz zadanie.", file=sys.stderr)
        sys.exit(1)

    if not cichy:
        print("🔬 AUDYT SPÓJNOŚCI (Prawo XXI) — ✅ pełna harmonia")
        for i in info:
            print(f"   • {i}")
    sys.exit(0)


if __name__ == "__main__":
    main()
