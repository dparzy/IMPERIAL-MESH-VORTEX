#!/usr/bin/env python3
"""
🔬 AUDYT SPÓJNOŚCI IMPERIUM — silnik Prawa XXI (KROK 0)

Uruchamiany automatycznie przez hooki Claude Code (SessionStart + Stop) oraz ręcznie:
    python narzedzia/audyt_spojnosci.py            # raport + exit code
    python narzedzia/audyt_spojnosci.py --cichy     # tylko gdy są błędy

Sprawdza 7 warstw spójności (zgodnie z ZASADY_FUNDAMENTALNE.md § PRAWO XXI):
  Warstwa 1 — żywy rój:        liczby, kategorie, elity, klucze
  Warstwa 2 — infrastruktura:  WAGI_REZIMU vs KAT w kodzie
  Warstwa 3 — dokumentacja:    MANIFEST klucze vs kod, liczby README/MANIFEST/CLAUDE
  Warstwa 4 — strategie:       Klucznik — klucze w strategiach vs kod
  Warstwa 5 — INDEKS:          liczby w INDEKS_IMPERIUM vs żywy kod
  Warstwa 6 — daty:            "Stan na:" w MANIFEST i README = bieżący dzień lub niedawno
  Warstwa 7 — sieroty:         pliki docs/ w INDEKS, linki cross-docs istnieją na dysku
  Warstwa 8 — LOG_ZMIAN:       jeśli kod zmieniony, LOG_ZMIAN ma wpis z bieżącą datą

Exit code:
  0 = pełna spójność (Imperium gotowe)
  1 = wykryto rozbieżność (złamanie Prawa XXI — STOP, napraw)

Zasada: ten skrypt NIE liczy z pamięci. Wszystkie liczby pochodzą z żywego kodu.
"""

import os
import re
import sys
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Litery KATEGORII dozwolone w kodzie (legenda — jedyne źródło prawdy)
LEGENDA_KAT = set("MTVFOLRSAKEGm")

# Pliki docs/ które celowo NIE są w INDEKS (archiwum, pliki techniczne)
INDEKS_WHITELIST = {
    "README.md",  # w docs/ ale to root README
}


def _czytaj(sciezka: str) -> str:
    with open(os.path.join(ROOT, sciezka), encoding="utf-8") as f:
        return f.read()


def _istnieje(sciezka: str) -> bool:
    return os.path.exists(os.path.join(ROOT, sciezka))


def audyt() -> tuple:
    """Zwraca (bledy: list, info: list)."""
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
        return bledy + ["(audyt przerwany — napraw import)"], info

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

    # ── WARSTWA 4: KLUCZNIK — strategie ↔ kod (Prawo XIX/XXI) ───────────────
    try:
        from imperium.legiony.strategie.rejestr_strategii import (
            klucze_uzyte_w_strategiach, wszystkie_strategie,
        )
        klucze_strat = klucze_uzyte_w_strategiach()
        klucze_kod = {n.KLUCZ for n in neurony}
        aktywne_kod = {n.KLUCZ for n in neurony if n.DOSTEPNY}

        widma = klucze_strat - klucze_kod
        if widma:
            bledy.append(f"[W4] Strategie wskazują klucze-widma (brak w kodzie): {sorted(widma)}")
        wyciszone = klucze_strat - aktywne_kod - widma
        if wyciszone:
            bledy.append(f"[W4] Strategie wskazują WYCISZONE neurony (martwy głos): {sorted(wyciszone)}")

        info.append(f"Strategie: {len(wszystkie_strategie())} (klucze: {len(klucze_strat)}, Klucznik spójny)")
    except ImportError:
        pass  # moduł strategii opcjonalny — brak = brak warstwy 4
    except Exception as e:
        bledy.append(f"[W4] Błąd sprawdzania Klucznika strategii: {e}")

    # ── WARSTWA 5: INDEKS_IMPERIUM — liczby ─────────────────────────────────
    # Sprawdzamy sekcję MAPA KODU w INDEKS (tam są liczby z kodu, nie z katalogu)
    try:
        indeks = _czytaj("docs/INDEKS_IMPERIUM.md")

        # Szukamy w sekcji MAPA KODU: "mikro-neurony (42)"
        mapa_kodu = ""
        if "## 🏛️ MAPA KODU" in indeks:
            mapa_kodu = indeks.split("## 🏛️ MAPA KODU")[1].split("##")[0]

        in_match = re.search(r"mikro-neurony\s*\((\d+)\)", mapa_kodu)
        if in_match:
            in_n = int(in_match.group(1))
            if in_n != n_neuronow:
                bledy.append(f"[W5] INDEKS (MAPA KODU) mikro-neurony={in_n} ≠ kod={n_neuronow}")

        # Liczba zwiadowców w INDEKS (MAPA KODU)
        iz_match = re.search(r"zwiadowców?\s*\((\d+)\)", mapa_kodu)
        if not iz_match:
            iz_match = re.search(r"zwiadowcy\s*\((\d+)\)", mapa_kodu)
        if iz_match:
            iz_n = int(iz_match.group(1))
            if iz_n != n_zwiadowcow:
                bledy.append(f"[W5] INDEKS (MAPA KODU) zwiadowcy={iz_n} ≠ kod={n_zwiadowcow}")

    except Exception as e:
        bledy.append(f"[W5] Błąd sprawdzania INDEKS_IMPERIUM: {e}")

    # ── WARSTWA 6: DATY "Stan na:" ──────────────────────────────────────────
    try:
        today = date.today()
        # Tolerancja: "Stan na:" może być z poprzedniego dnia (np. commit był wieczorem)
        TOLERANCJA_DNI = 2

        for doc_path, label in [("docs/MANIFEST_KODU.md", "MANIFEST"), ("README.md", "README")]:
            doc = _czytaj(doc_path)
            # Tolerancja markdown: '**Stan na:** 2026-06-03' (gwiazdki/spacje przed datą)
            m = re.search(r"Stan na:\s*\**\s*(\d{4}-\d{2}-\d{2})", doc)
            if m:
                doc_date = date.fromisoformat(m.group(1))
                delta = (today - doc_date).days
                if delta > TOLERANCJA_DNI:
                    bledy.append(
                        f"[W6] {label} 'Stan na:' = {m.group(1)} — "
                        f"przestarzałe o {delta} dni (dziś {today}). Zaktualizuj po każdej sesji."
                    )
            else:
                bledy.append(
                    f"[W6] {label} nie zawiera pola 'Stan na:' (format: YYYY-MM-DD). "
                    f"Wymagane przez Prawo XXI (data = data commitu)."
                )
    except Exception as e:
        bledy.append(f"[W6] Błąd sprawdzania dat 'Stan na:': {e}")

    # ── WARSTWA 7: SIEROTY — pliki docs/ bez wpisu w INDEKS ─────────────────
    try:
        indeks_txt = _czytaj("docs/INDEKS_IMPERIUM.md")
        docs_dir = os.path.join(ROOT, "docs")
        docs_files = {f for f in os.listdir(docs_dir)
                      if f.endswith(".md") and f not in INDEKS_WHITELIST}

        sieroty = []
        for fname in sorted(docs_files):
            # Plik w docs/archiwum/ — pomijamy (archiwum ma swoje zasady)
            if fname.startswith("archiwum"):
                continue
            # Sprawdź czy nazwa pliku pojawia się w INDEKS
            if fname not in indeks_txt:
                sieroty.append(fname)

        if sieroty:
            bledy.append(f"[W7] Pliki docs/ bez wpisu w INDEKS_IMPERIUM: {sieroty}")

        # Linki cross-docs: [text](ścieżka.md) — sprawdź czy plik istnieje
        dead_links = []
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)#]+\.md[^)]*)\)")
        for fname in sorted(docs_files):
            fpath = os.path.join(docs_dir, fname)
            if not os.path.isfile(fpath):
                continue
            try:
                content = open(fpath, encoding="utf-8").read()
            except Exception:
                continue
            for text, href in link_pattern.findall(content):
                # Usuń kotwice (#...)
                href_clean = href.split("#")[0].strip()
                if not href_clean:
                    continue
                # Ścieżki względne od docs/
                if href_clean.startswith("../"):
                    target = os.path.join(ROOT, href_clean[3:])
                elif href_clean.startswith("/"):
                    target = os.path.join(ROOT, href_clean.lstrip("/"))
                elif "/" not in href_clean:
                    target = os.path.join(docs_dir, href_clean)
                else:
                    target = os.path.join(docs_dir, href_clean)
                if not os.path.exists(target):
                    dead_links.append(f"{fname} → {href_clean}")

        if dead_links:
            bledy.append(f"[W7] Martwe linki w docs/ ({len(dead_links)}): {dead_links[:10]}"
                         + (" ..." if len(dead_links) > 10 else ""))

    except Exception as e:
        bledy.append(f"[W7] Błąd sprawdzania sierot/linków: {e}")

    # ── WARSTWA 8: LOG_ZMIAN — świeżość ─────────────────────────────────────
    try:
        import glob
        import time

        log = _czytaj("docs/LOG_ZMIAN.md")

        # Ostatnia data w logu (format: ## YYYY-MM-DD)
        log_dates = re.findall(r"^## (\d{4}-\d{2}-\d{2})", log, re.M)
        if log_dates:
            last_log_date = date.fromisoformat(sorted(log_dates)[-1])

            # Znajdź najnowszy plik .py w imperium/ (mtime)
            py_files = glob.glob(os.path.join(ROOT, "imperium", "**", "*.py"), recursive=True)
            if py_files:
                newest_py = max(py_files, key=os.path.getmtime)
                newest_mtime = date.fromtimestamp(os.path.getmtime(newest_py))

                if newest_mtime > last_log_date:
                    rel = os.path.relpath(newest_py, ROOT)
                    bledy.append(
                        f"[W8] Kod zmieniony ({rel}, {newest_mtime}) "
                        f"po ostatnim wpisie w LOG_ZMIAN ({last_log_date}). "
                        f"Dodaj wpis do docs/LOG_ZMIAN.md."
                    )
        else:
            bledy.append("[W8] docs/LOG_ZMIAN.md nie zawiera żadnej daty (format: ## YYYY-MM-DD)")

    except Exception as e:
        bledy.append(f"[W8] Błąd sprawdzania świeżości LOG_ZMIAN: {e}")

    return bledy, info


def main():
    cichy = "--cichy" in sys.argv
    bledy, info = audyt()

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
