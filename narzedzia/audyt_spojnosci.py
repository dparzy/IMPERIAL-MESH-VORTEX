#!/usr/bin/env python3
"""
🔬 AUDYT SPÓJNOŚCI IMPERIUM — silnik Prawa XXI (KROK 0)

Uruchamiany automatycznie przez hooki Claude Code (SessionStart + Stop) oraz ręcznie:
    python narzedzia/audyt_spojnosci.py            # raport + exit code
    python narzedzia/audyt_spojnosci.py --cichy     # tylko gdy są błędy

Sprawdza 13 warstw spójności (zgodnie z ZASADY_FUNDAMENTALNE.md § PRAWO XXI):
  Warstwa 1  — żywy rój:        liczby, kategorie, elity, klucze
  Warstwa 2  — infrastruktura:  WAGI_REZIMU vs KAT w kodzie
  Warstwa 3  — dokumentacja:    MANIFEST klucze vs kod, liczby README/MANIFEST/CLAUDE
  Warstwa 4  — strategie:       Klucznik — klucze w strategiach vs kod
  Warstwa 5  — INDEKS:          liczby w INDEKS_IMPERIUM vs żywy kod
  Warstwa 6  — daty:            "Stan na:" w MANIFEST i README = bieżący dzień lub niedawno
  Warstwa 7  — sieroty:         pliki docs/ w INDEKS, linki cross-docs istnieją na dysku
  Warstwa 8  — LOG_ZMIAN:       jeśli kod zmieniony, LOG_ZMIAN ma wpis z bieżącą datą
  Warstwa 9  — KATALOG_STRATEGII: cytowane klucze neuronów = klucze zaimplementowane
  Warstwa 10 — słowa kluczowe:  kluczowe dokumenty modułowe zawierają wymagane terminy
  Warstwa 11 — biblioteki/:     moduły w imperium/biblioteki/ wymienione w INDEKS_IMPERIUM
  Warstwa 12 — żywotność głosu: każdy aktywny neuron głosuje (≠martwy) w ≥1 scenariuszu (Prawo XV)
  Warstwa 13 — ruff (linter):   bugi i martwy kod (F811 duplikaty, F821 undefined, F841/F401 martwe)

Exit code:
  0 = pełna spójność (Imperium gotowe)
  1 = wykryto rozbieżność (złamanie Prawa XXI — STOP, napraw)

Zasada: ten skrypt NIE liczy z pamięci. Wszystkie liczby pochodzą z żywego kodu.
"""

import os
import re
import sys
import subprocess
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Litery KATEGORII dozwolone w kodzie (legenda — jedyne źródło prawdy)
LEGENDA_KAT = set("MTVFOLRSAKEGHmNZD")

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
    except ModuleNotFoundError as e:
        # Tylko BRAK modułu strategii jest dopuszczalny (warstwa 4 opcjonalna).
        # Inny brakujący moduł (np. zależność strategii padła) = realna awaria.
        if e.name and e.name.startswith("imperium.legiony.strategie"):
            pass
        else:
            bledy.append(f"[W4] Błąd importu w warstwie strategii: {e}")
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
                # Pomiń zewnętrzne URL-e (http/https/mailto) — W7 sprawdza tylko
                # lokalne linki cross-doc. Uwaga: domeny jak "www.mdpi.com"
                # zawierają ".md" i wpadały w regex jako fałszywy martwy link.
                if re.match(r"^(https?:|mailto:|ftp:)", href_clean, re.I):
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

    # ── WARSTWA 8: LOG_ZMIAN — świeżość (git, NIE mtime) ────────────────────
    # mtime systemu plików jest bezużyteczny po świeżym klonie/resetcie kontenera
    # (wszystkie pliki dostają „teraz"). Używamy git: czy są zmienione pliki .py
    # (staged + working tree) bez wpisu w LOG_ZMIAN z dzisiejszą datą.
    try:
        log = _czytaj("docs/LOG_ZMIAN.md")
        log_dates = re.findall(r"^## (\d{4}-\d{2}-\d{2})", log, re.M)
        if not log_dates:
            bledy.append("[W8] docs/LOG_ZMIAN.md nie zawiera żadnej daty (format: ## YYYY-MM-DD)")
        else:
            last_log_date = date.fromisoformat(sorted(log_dates)[-1])
            zmienione = set()
            for args in (["diff", "--name-only", "HEAD"], ["diff", "--cached", "--name-only"]):
                try:
                    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                         text=True, timeout=20).stdout
                    zmienione |= {l for l in out.splitlines()
                                  if l.startswith(("imperium/", "narzedzia/")) and l.endswith(".py")}
                except Exception:
                    pass
            if zmienione and date.today() > last_log_date:
                bledy.append(
                    f"[W8] Kod .py zmieniony ({sorted(zmienione)[:3]}) bez wpisu w "
                    f"LOG_ZMIAN z dzisiejszą datą (ostatni: {last_log_date}). Dodaj wpis."
                )
    except Exception as e:
        bledy.append(f"[W8] Błąd sprawdzania świeżości LOG_ZMIAN: {e}")

    # ── WARSTWA 9: KATALOG_STRATEGII — klucze zaimplementowanych = kod ───────
    # Prawo XIX/XXI: opis strategii w katalogu NIE może cytować kluczy neuronów,
    # których dana strategia nie używa w kodzie (martwe/stare klucze mylą czytelnika).
    try:
        from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
        kat = _czytaj("docs/KATALOG_STRATEGII.md")
        code_keys = {s.id: (set(s.neurony_wejscie) | set(s.neurony_filtr)
                            | set(s.neurony_wyjscie)) for s in wszystkie_strategie()}
        impl_ids = set(code_keys)
        # Podziel katalog na bloki "### ID ..." i sprawdź klucze w bloku.
        bloki = re.split(r"\n### ", kat)
        key_pat = re.compile(r"\b((?:X|XII|VI|V|A|PSY|III|OC|SMC)-\d{2,3})\b")
        rozjazdy = []
        for blk in bloki:
            m = re.match(r"([A-Z0-9-]+)", blk)
            if not m or m.group(1) not in impl_ids:
                continue
            sid = m.group(1)
            cytowane = set(key_pat.findall(blk)) - {sid}
            obce = cytowane - code_keys[sid]
            if obce:
                rozjazdy.append(f"{sid}: obce klucze {sorted(obce)}")
        if rozjazdy:
            bledy.append("[W9] KATALOG_STRATEGII cytuje klucze spoza kodu "
                         f"(zaimplementowane strategie): {rozjazdy}")
    except ModuleNotFoundError as e:
        if not (e.name and e.name.startswith("imperium.legiony.strategie")):
            bledy.append(f"[W9] Błąd importu strategii: {e}")
    except Exception as e:
        bledy.append(f"[W9] Błąd sprawdzania kluczy KATALOG_STRATEGII: {e}")

    # ── WARSTWA 10: SŁOWA KLUCZOWE W DOKUMENTACH MODUŁOWYCH ─────────────────
    bledy += _warstwa_10_doc_keywords()

    # ── WARSTWA 11: BIBLIOTEKI/ MODUŁY W INDEKS ───────────────────────────────
    bledy += _warstwa_11_biblioteki_indeks()

    # ── WARSTWA 12: ŻYWOTNOŚĆ GŁOSU (Prawo XV) ────────────────────────────────
    w12_bledy, w12_info = _warstwa_12_zywotnosc_glosu(neurony)
    bledy += w12_bledy
    info += w12_info

    # ── WARSTWA 13: RUFF — bugi/martwy kod (linter, Prawo XXI) ─────────────────
    w13_bledy, w13_info = _warstwa_13_ruff()
    bledy += w13_bledy
    info += w13_info

    return bledy, info


def _warstwa_13_ruff():
    """
    W13 — statyczny linter (ruff) łapie BUGI i martwy kod, których warstwy
    spójności nie widzą: duplikaty klas (F811), niezdefiniowane nazwy (F821),
    martwe zmienne (F841), nieużyte importy (F401). Konfiguracja: ruff.toml.

    Filozofia jak testy: jeśli ruff NIE jest zainstalowany → tylko nota (audyt
    działa w minimalnym środowisku). Jeśli JEST i znajdzie błąd → twarda blokada.
    """
    bledy, info = [], []
    try:
        wynik = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "imperium", "tests", "narzedzia",
             "--quiet", "--output-format", "concise"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError:
        info.append("⚠️ W13: ruff niezainstalowany — linter pominięty (pip install ruff)")
        return bledy, info
    except Exception as e:
        info.append(f"⚠️ W13: ruff nie uruchomił się ({e}) — linter pominięty")
        return bledy, info

    if wynik.returncode == 0:
        info.append("Ruff (W13): czysto ✅ (F/E9/E711-714/B006-008/B904/PLE — bez bugów/martwego kodu)")
        return bledy, info
    linie = [l for l in wynik.stdout.strip().splitlines() if l.strip()]
    if not linie:
        # rc≠0 bez znalezisk = ruff nie wykonał się (np. "No module named ruff" po
        # resecie kontenera, błąd configu) — to NIE są znaleziska. Nota, nie blokada.
        szczegol = wynik.stderr.strip().splitlines()[:1] or ["nieznany błąd"]
        info.append(f"⚠️ W13: ruff nie wykonał się ({szczegol[0]}) — linter pominięty (pip install ruff)")
        return bledy, info
    bledy.append(f"[W13] Ruff wykrył {len(linie)} problemów (bugi/martwy kod): "
                 f"{linie[:8]}{' …' if len(linie) > 8 else ''}")
    return bledy, info


def _warstwa_10_doc_keywords():
    """W10 — słowa kluczowe w dokumentach modułowych (spójność z kodem)."""
    bledy = []

    # Each entry: (file_path, required_keyword, error_message)
    checks = [
        ("docs/KALKULATOR_LEWARA.md", "vol_targeting",
         "KALKULATOR_LEWARA.md brak 'vol_targeting' — dodaj sekcję Volatility Targeting (W-059)"),
        ("docs/KALKULATOR_LEWARA.md", "skala_vol",
         "KALKULATOR_LEWARA.md brak 'skala_vol' — PlanPozycji.skala_vol nie opisane"),
        ("docs/IGRZYSKA_IMPERIUM.md", "HedgeMWU",
         "IGRZYSKA_IMPERIUM.md brak 'HedgeMWU' — dodaj sekcję online learning (W-049)"),
        ("docs/IGRZYSKA_IMPERIUM.md", "obserwatorzy",
         "IGRZYSKA_IMPERIUM.md brak 'obserwatorzy' — observer pattern Igrzyska nie opisany"),
        ("docs/GENERAL_LEGATUS.md", "mnozniki_neuronow",
         "GENERAL_LEGATUS.md brak 'mnozniki_neuronow' — HedgeMWU→Legatus integracja nie opisana"),
        ("docs/GENERAL_LEGATUS.md", "HedgeMWU",
         "GENERAL_LEGATUS.md brak 'HedgeMWU' — online learning nie opisane"),
        ("docs/LEGIONY_ARCHITEKTURA.md", "Hurst",
         "LEGIONY_ARCHITEKTURA.md brak 'Hurst' — kategoria H nie opisana w legendzie"),
        ("docs/ARCHITEKTURA_IMPERIUM.md", "21",
         "ARCHITEKTURA_IMPERIUM.md brak '21' praw — aktualizuj z 19→21"),
    ]

    for fpath, keyword, msg in checks:
        try:
            with open(os.path.join(ROOT, fpath), encoding="utf-8") as f:
                content = f.read()
            if keyword.lower() not in content.lower():
                bledy.append(f"[W10] {msg}")
        except FileNotFoundError:
            bledy.append(f"[W10] Brak pliku: {fpath}")

    return bledy


def _warstwa_11_biblioteki_indeks():
    """W11 — moduły w imperium/biblioteki/ muszą być wymienione w INDEKS_IMPERIUM."""
    bledy = []
    try:
        bib_dir = os.path.join(ROOT, "imperium/biblioteki")
        modules = [f[:-3] for f in os.listdir(bib_dir)
                   if f.endswith(".py") and not f.startswith("_")]
        with open(os.path.join(ROOT, "docs/INDEKS_IMPERIUM.md"), encoding="utf-8") as f:
            indeks = f.read()
        for mod in sorted(modules):
            if mod not in indeks:
                bledy.append(f"[W11] Moduł biblioteki '{mod}' nie wymieniony w INDEKS_IMPERIUM.md")
    except Exception as e:
        bledy.append(f"[W11] Błąd sprawdzania biblioteki: {e}")
    return bledy


# Neurony świadomie zależne od danych adapterów zewnętrznych (futures/CVD/F&G).
# W backteście czysto-OHLCV milczą (NEUTRAL pewnosc=0) — to ZNANA luka Prawa XV,
# nie regresja: ożyją po podpięciu adapterów do pipeline. W12 raportuje je jako
# ⚠️ ostrzeżenie (nie blokuje commita). Każdy INNY milczący neuron = błąd blokujący.
NEURONY_ZALEZNE_OD_ADAPTEROW = {
    "PSY-01": "FUNDING_RATE (AdapterFutures)",
    "PSY-02": "LONG_SHORT_RATIO (AdapterFutures)",
    "PSY-03": "FEAR_GREED_INDEX (AdapterFearGreed)",
    "PSY-04": "OPEN_INTEREST (AdapterFutures)",
    "V-03":   "CVD (AdapterCVD/trade-feed)",
    "AUG-01": "EVENT_* (AdapterKronikarz — okno zdarzenia fundamentalnego)",
    "RADAR-01": "BTC_TREND (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300; "
                "ożywa gdy pętla portfelowa poda serie BTC)",
    "RADAR-02": "BTC_DOMINANCJA (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300)",
    "RADAR-03": "PRZEPLYW_KAPITALU (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300)",
    "NEWS-01": "NEWS_SENTYMENT (AdapterNewsLLM — wpięty w zbuduj_bojowy W-301; "
               "ożywa z RSS fetcher lub DEEPSEEK_API_KEY; bez feedu: abstynuje)",
    "X-28":   "MTF_4H_RSI_14/MTF_1D_RSI_14 (Budowniczy MTF — ożywa gdy bary mają "
              "pole 'interwal' i odpowiedni TF; bez niego abstynuje per Prawo XV)",
}

# Dowód allowlisty (Prawo I — bez zaufania na słowo): każdy neuron adapterowy
# MUSI ożyć, gdy nakarmimy go ekstremalną wartością jego klucza. Jeśli milczy
# MIMO danych adaptera → realny bug (błąd blokujący, nie wybaczany allowlistą).
WERYFIKACJA_ADAPTEROW = {
    "PSY-01": {"FUNDING_RATE": 0.0025},                                   # crowded long → SHORT
    "PSY-02": {"LONG_SHORT_RATIO": 0.82},                                 # tłum long → SHORT
    "PSY-03": {"FEAR_GREED_INDEX": 8},                                    # ekstremalny strach → LONG
    "PSY-04": {"OPEN_INTEREST": 150000.0, "OPEN_INTEREST_PREV": 100000.0,
               "CLOSE": 101.0, "CLOSE_PREV": 100.0},                      # OI↑ + cena → sygnał
    "V-03":   {"CVD": 5000.0, "CVD_PREV": 1000.0,
               "CLOSE": 101.0, "CLOSE_PREV": 100.0},                      # napływ kupna → LONG
    "AUG-01": {"EVENT_TYP": "HALVING", "EVENT_DNI_PO": 5.0,
               "EVENT_N": 3, "EVENT_PROB_WZROSTU": 100.0},                # analogia → LONG
    "RADAR-01": {"BTC_TREND": 0.9},                                       # BTC↑ → LONG-wsparcie
    "RADAR-02": {"BTC_DOMINANCJA": -0.9},                                 # alt-season → LONG-wsparcie
    "RADAR-03": {"PRZEPLYW_KAPITALU": 0.95},                              # napływ → LONG-wsparcie
    "NEWS-01": {"NEWS_SENTYMENT": 0.8, "NEWS_PEWNOSC": 0.9, "NEWS_N": 5},  # mocno bycze → LONG
    "X-28":   {"CLOSE": 50000.0, "RSI_14": 60.0, "EMA_21": 49000.0,
               "MTF_4H_RSI_14": 65.0, "MTF_4H_EMA_50": 47000.0,
               "MTF_1D_RSI_14": 58.0, "MTF_1D_EMA_50": 46000.0},  # 3/3 TF LONG → LONG
}


def _scenariusze_barow():
    """5 syntetycznych reżimów rynku — każdy aktywny neuron powinien ożyć w ≥1.

    byk/niedźwiedź — silny trend; kaskada — 4 przyspieszające spadki z rosnącym
    wolumenem (budzi Z-04); bańka — paraboliczny blow-off (budzi Z-03);
    spokój — wąski range (budzi neurony rewersji). Determinizm: stałe ziarno.
    """
    import random
    scen = ["byk", "niedzwiedz", "kaskada", "banka", "spokoj"]
    out = {}
    for typ in scen:
        random.seed(42)
        b = []
        p = 100.0
        n = 260
        for i in range(n):
            v = 1000 + random.random() * 300
            if typ == "byk":
                p *= (1 + abs(random.gauss(0.004, 0.006)))
            elif typ == "niedzwiedz":
                p *= (1 - abs(random.gauss(0.004, 0.006)))
            elif typ == "kaskada":
                if i >= n - 4:
                    p *= (1 - 0.03 * (i - (n - 5)))
                    v = 1000 * (i - (n - 5)) * 1.5
                else:
                    p *= (1 + random.gauss(0.001, 0.004))
            elif typ == "banka":
                p *= (1 + (0.035 if i > n - 8 else random.gauss(0.001, 0.004)))
            else:  # spokoj
                p *= (1 + random.gauss(0, 0.003))
            b.append({
                "open": p, "high": p * 1.012, "low": p * 0.988,
                "close": p * (1 + random.gauss(0, 0.004)), "volume": v,
                # Zegary rynku (SES-*): bary godzinowe od piątku 00:00 UTC
                # (1970-01-02) — seria trafia w okno fundingu, piątek 21–23 UTC
                # i domyka zakres Azji (budzi SES-01/SES-02 w scenariuszach).
                "timestamp": 86_400_000 + i * 3_600_000,
            })
        out[typ] = b
    return out


def _warstwa_12_zywotnosc_glosu(neurony):
    """W12 — Prawo XV: aktywny neuron, który MILCZY (NEUTRAL pewnosc=0 i zero
    pewnosc_przeciwnika) we WSZYSTKICH scenariuszach = martwy głos.

    Zwraca (bledy_blokujace, info_ostrzezenia):
      • milczący neuron spoza allowlisty adapterowej → ❌ błąd (regresja Prawa XV)
      • milczący neuron z allowlisty adapterowej      → ⚠️ info (znana luka)
    """
    bledy, info = [], []
    try:
        import logging
        from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow

        # Wycisz logi Bramy na czas budowania scenariuszy (czysty raport audytu)
        prev = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        try:
            bud = BudowniczyWskaznikow()
            wsk = {s: bud.zbuduj(b) for s, b in _scenariusze_barow().items()}
        finally:
            logging.disable(prev)

        martwe = []
        for n in neurony:
            if not getattr(n, "DOSTEPNY", True):
                continue
            zywy = False
            for s in wsk.values():
                try:
                    sig = n.interpretuj(s)
                    if (sig.kierunek != "NEUTRAL" or sig.pewnosc > 0
                            or getattr(sig, "pewnosc_przeciwnika", 0) > 0):
                        zywy = True
                        break
                except Exception:
                    continue
            if not zywy:
                martwe.append(n.KLUCZ)

        regresje = [k for k in martwe if k not in NEURONY_ZALEZNE_OD_ADAPTEROW]
        znane = [k for k in martwe if k in NEURONY_ZALEZNE_OD_ADAPTEROW]

        if regresje:
            bledy.append(
                f"[W12] Martwy głos (Prawo XV) — aktywne neurony milczą we wszystkich "
                f"scenariuszach: {sorted(regresje)}. Podłącz dane lub wycisz (DOSTEPNY=False)."
            )
        if znane:
            powody = ", ".join(f"{k}:{NEURONY_ZALEZNE_OD_ADAPTEROW[k]}" for k in sorted(znane))
            info.append(f"⚠️ Prawo XV — czekają na adaptery ({len(znane)}): {powody}")

        # DOWÓD ALLOWLISTY (Prawo I): neuron adapterowy MUSI ożyć z danymi adaptera.
        by_klucz = {n.KLUCZ: n for n in neurony}
        martwe_mimo_danych = []
        for klucz, trigger in WERYFIKACJA_ADAPTEROW.items():
            n = by_klucz.get(klucz)
            if n is None or not getattr(n, "DOSTEPNY", True):
                continue
            try:
                sig = n.interpretuj(dict(trigger))
                if (sig.kierunek == "NEUTRAL" and sig.pewnosc == 0
                        and getattr(sig, "pewnosc_przeciwnika", 0) == 0):
                    martwe_mimo_danych.append(klucz)
            except Exception as e:
                martwe_mimo_danych.append(f"{klucz}({e})")
        if martwe_mimo_danych:
            bledy.append(
                f"[W12] Neuron adapterowy milczy MIMO danych adaptera (realny bug, nie "
                f"luka): {sorted(martwe_mimo_danych)}. Sprawdź logikę interpretuj()."
            )
    except Exception as e:
        bledy.append(f"[W12] Błąd testu żywotności głosu: {e}")
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
