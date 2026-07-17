#!/usr/bin/env python3
"""
🔬 AUDYT SPÓJNOŚCI IMPERIUM — silnik Prawa XXI (KROK 0)

Uruchamiany automatycznie przez hooki Claude Code (SessionStart + Stop) oraz ręcznie:
    python narzedzia/audyt_spojnosci.py            # raport + exit code
    python narzedzia/audyt_spojnosci.py --cichy     # tylko gdy są błędy

Sprawdza 14 warstw spójności (zgodnie z ZASADY_FUNDAMENTALNE.md § PRAWO XXI):
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
  Warstwa 14 — wszystkie docs:  MAPA_KLUCZY zawiera każdy klucz z kodu (skan wszystkich .md)

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

# Windows: konsola cp1250 wywala się na emoji audytu → wymuś UTF-8 (no-op na Linux/macOS).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")   # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Litery KATEGORII dozwolone w kodzie (legenda — jedyne źródło prawdy)
LEGENDA_KAT = set("MTVFOLRSAKEGHmNZDC")

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

        # W-323: NEURONY_STYLU pokrywa KAŻDY neuron (zero sierot/braków, Prawo XXI)
        from imperium.legiony.rejestr import raport_profili
        rp = raport_profili()
        if rp["sieroty_w_mapie"]:
            bledy.append(f"[W1] NEURONY_STYLU sieroty (w mapie, brak w kodzie): {rp['sieroty_w_mapie']}")
        if rp["braki_w_mapie"]:
            bledy.append(f"[W1] NEURONY_STYLU braki (neuron bez profilu stylu): {rp['braki_w_mapie']}")
        info.append(f"Profile stylu (W-323): SCALP {rp['scalp']} | SWING {rp['swing']} | INVEST {rp['invest']}")

        # W-325: GUBERNATOR — neutralność (stan bazowy ≈1.0) i granice mnożnika.
        from imperium.koloseum.gubernator import Gubernator
        _g = Gubernator()
        _baz = _g.ocen(konwikcja_koszyka=0.5, rozrzut_okazji=0.0, dd_frakcja=1.0, breadth=1.0)
        if not (_g.floor <= _baz.mnoznik <= _g.ceiling):
            bledy.append(f"[W1] Gubernator mnożnik poza [floor,ceiling]: {_baz.mnoznik}")
        if abs(_baz.mnoznik - 1.0) > 0.15:
            bledy.append(f"[W1] Gubernator nie-neutralny w stanie bazowym: {_baz.mnoznik} (Prawo XV)")
        info.append(f"Gubernator (W-325): floor {_g.floor}× | ceiling {_g.ceiling}× | "
                    f"baza {_baz.mnoznik}× ({_baz.postawa})")

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
        # NAPRAWA (2026-07-04): odniesienie = data OSTATNIEGO COMMITU, nie date.today().
        # Powód: porównanie z „dziś" powodowało FAŁSZYWY alarm co kilka dni gdy repo leżało
        # bez commitu (data dokumentu = data ostatniej zmiany = poprawna, ale „starsza niż
        # dziś"). Teraz: doc-date musi nadążać za ostatnią ZMIANĄ (commitem), nie za zegarem.
        # To wciąż łapie prawdziwą niespójność: kod zmieniony (nowy commit) + stara data → alarm.
        import subprocess
        ref = date.today()
        try:
            _out = subprocess.run(["git", "log", "-1", "--format=%cd", "--date=short"],
                                  capture_output=True, text=True, timeout=5)
            if _out.returncode == 0 and _out.stdout.strip():
                ref = date.fromisoformat(_out.stdout.strip())
        except Exception:  # noqa: BLE001 — brak gita → fallback na dziś
            pass
        TOLERANCJA_DNI = 2

        for doc_path, label in [("docs/MANIFEST_KODU.md", "MANIFEST"), ("README.md", "README")]:
            doc = _czytaj(doc_path)
            # Tolerancja markdown: '**Stan na:** 2026-06-03' (gwiazdki/spacje przed datą)
            m = re.search(r"Stan na:\s*\**\s*(\d{4}-\d{2}-\d{2})", doc)
            if m:
                doc_date = date.fromisoformat(m.group(1))
                delta = (ref - doc_date).days
                if delta > TOLERANCJA_DNI:
                    bledy.append(
                        f"[W6] {label} 'Stan na:' = {m.group(1)} — "
                        f"starsze o {delta} dni niż ostatni commit ({ref}). Zaktualizuj po zmianie."
                    )
            else:
                bledy.append(
                    f"[W6] {label} nie zawiera pola 'Stan na:' (format: YYYY-MM-DD). "
                    f"Wymagane przez Prawo XXI (data = data commitu)."
                )
    except Exception as e:
        bledy.append(f"[W6] Błąd sprawdzania dat 'Stan na:': {e}")

    # ── WARSTWA 6b: DATY WSZYSTKICH ŻYWYCH DOKUMENTÓW ────────────────────────
    # ROZKAZ CEZARA 2026-07-16: „zapominasz o spójności dokumentów, pełna synchronizacja 1:1…
    # straszny bałagan w tych dokumentach których przybywa. Zarządzam pełen porządek."
    #
    # DZIURA, KTÓRĄ TO ZATYKA (zmierzona): W6 pilnowała dat tylko w MANIFEST i README —
    # 2 dokumenty z 64. Reszta gniła bezkarnie przy exit 0. Znalezione realne rozjazdy:
    # ARCHITEKTURA_IMPERIUM (20 dni), MANUAL_UZYTKOWNIKA (25), REJESTR_INSPIRACJI (32).
    #
    # DLACZEGO PER-PLIK, NIE PER-REPO: odniesieniem jest ostatni commit TEGO dokumentu,
    # nie całego repo. Inaczej GUBERNATOR.md („Stan na: 2026-06-16", od czerwca niezmieniony
    # = POPRAWNY) dostawałby fałszywy alarm co dzień. Dokument ma nadążać za WŁASNĄ zmianą.
    #
    # POMIJAMY (Prawo I — nie falsyfikujemy historii): datowane snapshoty (data w NAZWIE pliku)
    # oraz dokumenty akumulujące historię/generowane. Ich data to prawda ich czasu.
    try:
        import subprocess

        POMIJANE_ZAWSZE = {"LOG_ZMIAN.md", "WIZJONER.md", "PAMIEC_SESJI.md",
                           "MANIFEST_KODU.md", "README.md"}   # MANIFEST/README ma już W6

        # Jedno przejście gita zamiast N wywołań: data ostatniego commitu per plik.
        daty_plikow: dict = {}
        # encoding="utf-8" OBOWIĄZKOWE (klasa wady zmierzona 2026-07-17): `text=True` bez
        # encoding dekoduje wyjście gita kodowaniem konsoli Windows (cp1250). Nazwy plików
        # są dziś ASCII, więc W6b działa — ale PIERWSZY plik z polską literą w nazwie
        # wywala wątek czytający, stdout=None i bramka dat cichnie NA GŁUCHO.
        _log = subprocess.run(
            ["git", "log", "--format=@%cd", "--date=short", "--name-only", "--", "docs"],
            capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace")
        biezaca = None
        for linia in _log.stdout.splitlines():
            if linia.startswith("@"):
                biezaca = linia[1:].strip()
            elif linia.strip() and biezaca:
                daty_plikow.setdefault(linia.strip(), biezaca)   # pierwszy = najnowszy

        przeterminowane, przekazane_tabularium = [], 0
        for sciezka_rel, data_commitu in sorted(daty_plikow.items()):
            nazwa = os.path.basename(sciezka_rel)
            if nazwa in POMIJANE_ZAWSZE:
                continue
            if re.search(r"\d{4}-\d{2}-\d{2}", nazwa):        # snapshot datowany nazwą
                continue
            pelna = os.path.join(ROOT, sciezka_rel)
            if not os.path.isfile(pelna):                      # usunięty/przeniesiony
                continue
            with open(pelna, encoding="utf-8", errors="replace") as f:
                tresc = f.read()

            # ── PRZEKAZANIE PAŁECZKI DO TABULARIUM (2026-07-17) ──────────────────────
            # Dokument z nagłówkiem Tabularium podlega bramce T2, która pyta OSTRZEJ:
            # „czy nadążasz za KODEM, który opisujesz" — zamiast W6b: „czy nadążasz za
            # SAMYM SOBĄ". W6b stała na założeniu „plik ruszony ⇒ treść się zmieniła";
            # nagłówki metadanych to założenie obaliły (commit dodający nagłówek nie zmienia
            # ANI JEDNEGO twierdzenia dokumentu). Bez tego wyjątku W6b żądała stemplowania
            # dzisiejszą datą 16 dokumentów, których nikt dziś nie zweryfikował — czyli
            # żądała KŁAMSTWA (Prawo I), a fałszywy alarm uczy ignorować bramkę.
            # Dwie bramki mierzące tę samą datę sprzecznymi definicjami = redundancja,
            # która szkodzi (Prawo XVI). Sprawdź dokumenty z nagłówkiem:
            #     python narzedzia/tabularium.py sprawdz
            # Parser Tabularium, NIE własny (Prawo XVI: jeden format = jeden parser).
            # Pierwsza wersja szukała `stan_na` w oknie 600 znaków — MAPA_PAMIECI (11
            # właścicieli) ma je na pozycji 609, SCIAGA_LOKAL na 778. Magiczne okno zamiast
            # granic bloku = bramka omijana przez dokumenty, które akurat są dłuższe.
            from narzedzia.tabularium import czytaj_naglowek
            if czytaj_naglowek(pelna).get("stan_na"):
                przekazane_tabularium += 1
                continue

            m = re.search(r"Stan na:\s*\**\s*(\d{4}-\d{2}-\d{2})", tresc)
            if not m:
                continue      # brak pola „Stan na:" NIE jest błędem — nie każdy dokument je ma
            delta = (date.fromisoformat(data_commitu) - date.fromisoformat(m.group(1))).days
            if delta > TOLERANCJA_DNI:
                przeterminowane.append(f"{nazwa} ('Stan na:' {m.group(1)} vs commit "
                                       f"{data_commitu} = {delta} dni)")
        if przeterminowane:
            bledy.append("[W6b] Dokumenty ze 'Stan na:' STARSZYM niż własna ostatnia zmiana "
                         "(Prawo XXI reguła 9 — zaktualizuj datę w tym samym commicie co treść): "
                         + "; ".join(przeterminowane))
        else:
            info.append(f"Daty żywych dokumentów (W6b): {len(daty_plikow)} sprawdzonych, "
                        "wszystkie 'Stan na:' nadążają za własną zmianą ✅"
                        + (f" | {przekazane_tabularium} dokumentów przekazanych bramce T2 "
                           f"Tabularium (ostrzejsze pytanie: nadąża za KODEM, nie za sobą)"
                           if przekazane_tabularium else ""))
    except Exception as e:  # noqa: BLE001 — brak gita nie może zabić audytu
        info.append(f"Daty żywych dokumentów (W6b): pominięte ({type(e).__name__}: {e})")

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
                                         text=True, timeout=20,
                                         encoding="utf-8", errors="replace").stdout
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

    # ── WARSTWA 14: WSZYSTKIE DOKUMENTY — MAPA_KLUCZY ↔ kod + sieroty ──────────
    w14_bledy, w14_info = _warstwa_14_wszystkie_dokumenty(neurony)
    bledy += w14_bledy
    info += w14_info

    return bledy, info


def _warstwa_14_wszystkie_dokumenty(neurony):
    """
    W14 — audyt CAŁEJ dokumentacji (rozkaz Cezara 2026-06-18: „audyt ZAWSZE
    sprawdza wszystkie pliki, dokumenty i kod").

    Deterministyczne sprawdzenie (bez fałszywych alarmów): MAPA_KLUCZY.md musi
    zawierać KAŻDY klucz z żywego kodu — żywy rejestr „klucz↔kod" jest jedynym
    miejscem, gdzie kompletność da się egzekwować bez szumu. Sieroty (klucz w docu
    bez kodu) NIE są błędem: dokumenty legalnie cytują klucze KATALOGOWE/planowane
    (MANIFEST „DO WDROŻENIA", MAPA_KLUCZY kolumna „W katalogu").

    Datowane snapshoty (LOG_ZMIAN, AUDYT_*_<data>, ROADMAP vX, RESEARCH/ANALIZA/MANUAL
    z „Stan na/Data") są POMIJANE świadomie — to prawda ich czasu (Prawo I: nie
    falsyfikujemy historii). Raportuje też ile plików .md istnieje (transparentność).
    """
    bledy, info = [], []
    klucze_kodu = {n.KLUCZ for n in neurony}

    # ── MAPA_KLUCZY kompletność: każdy klucz kodu MUSI być w mapie ──
    if _istnieje("docs/MAPA_KLUCZY.md"):
        txt = _czytaj("docs/MAPA_KLUCZY.md")
        w_mapie = set(re.findall(r"\*\*([A-Z][\w-]+)\*\*", txt)) | \
            set(re.findall(r"\|\s*([A-Z]{1,6}-[\w]+)\s*\|", txt))
        w_mapie = {k for k in w_mapie if re.match(r"^[A-Z]+-", k)}
        brak = sorted(klucze_kodu - w_mapie)
        if brak:
            bledy.append(f"[W14] MAPA_KLUCZY brak kluczy z kodu (dopisz mapę): {brak}")
        else:
            info.append(f"MAPA_KLUCZY (W14): wszystkie {len(klucze_kodu)} kluczy kodu pokryte ✅")
    else:
        bledy.append("[W14] Brak docs/MAPA_KLUCZY.md — żywy rejestr klucz↔kod zniknął")

    # ── Transparentność: ile plików .md istnieje (poza archiwum) ──
    md_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if any(seg in dirpath for seg in ("/.git", "/archiwum", "/.pytest_cache", "/__pycache__")):
            continue
        md_files += [f for f in filenames if f.endswith(".md")]
    info.append(f"Dokumenty (W14): przeskanowano {len(md_files)} plików .md "
                f"(datowane snapshoty pominięte świadomie — Prawo I)")

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
            [sys.executable, "-m", "ruff", "check", "imperium", "tests", "narzedzia", "skrypty",
             "--quiet", "--output-format", "concise"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
            # ruff cytuje linię źródła w komunikacie — nasze komentarze są po polsku,
            # więc bez encoding="utf-8" W13 wywala się dokładnie wtedy, gdy ZNAJDZIE bug.
            encoding="utf-8", errors="replace",
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

    # 🚨 LICZBA PRAW — POLICZONA z ZASADY_FUNDAMENTALNE, nie zaszyta (naprawa 2026-07-16).
    # POWÓD: tu stało na sztywno `"21"` z komunikatem „aktualizuj z 19→21" — ktoś podbił ręcznie
    # 19→21, a gdy praw przybyło do XXV, audyt dalej ŻĄDAŁ „21" i ODRZUCAŁ prawdziwe „25".
    # Bramka egzekwowała KŁAMSTWO. Ironia: W10 pilnuje Prawa XXI, którego reguła 8 brzmi
    # „liczby policzone, nie zaokrąglone" — a sama miała liczbę z pamięci. Zaszyta liczba
    # MUSI się zestarzeć; to kwestia czasu, nie dyscypliny autora.
    try:
        with open(os.path.join(ROOT, "ZASADY_FUNDAMENTALNE.md"), encoding="utf-8") as f:
            _zasady = f.read()
        _liczba_praw = str(len(set(re.findall(r"PRAWO\s+([IVXL]+)\b", _zasady))))
    except Exception:  # noqa: BLE001 — brak pliku praw nie może zabić audytu
        _liczba_praw = None

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
    ]
    if _liczba_praw:
        checks.append((
            "docs/ARCHITEKTURA_IMPERIUM.md", _liczba_praw,
            f"ARCHITEKTURA_IMPERIUM.md nie podaje aktualnej liczby praw ({_liczba_praw}) — "
            f"policzone z ZASADY_FUNDAMENTALNE.md. Zaktualizuj nagłówek."))

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
    "PSY-05": "DVOL_INDEX (AdapterDVOL — indeks strachu opcji Deribit; opt-in --dvol; "
              "bez adaptera abstynuje, IC +0.16@7d zwalidowany)",
    "K-03":   "STABLE_FLOW (AdapterStablecoin — podaż stablecoinów DefiLlama; opt-in "
              "--stablecoin; bez adaptera abstynuje, IC +0.05..0.10@7-30d zwalidowany)",
    "K-04":   "USD_ZSCORE (AdapterUSD — siła dolara Frankfurter z-score 120d; opt-in "
              "--usd; bez adaptera abstynuje, IC -0.17@14d/-0.27@30d zwalidowany)",
    "V-03":   "CVD (AdapterCVD/trade-feed)",
    "AUG-01": "EVENT_* (AdapterKronikarz — okno zdarzenia fundamentalnego)",
    "RADAR-01": "BTC_TREND (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300; "
                "ożywa gdy pętla portfelowa poda serie BTC)",
    "RADAR-02": "BTC_DOMINANCJA (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300)",
    "RADAR-03": "PRZEPLYW_KAPITALU (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300)",
    "RADAR-04": "STRES_KORELACJI (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300; "
                "ożywa gdy pętla portfelowa poda serie koszyka; detektor kaskady W-329)",
    "RADAR-05": "LEAD_BTC (RadarRynku → Dyrygent.odswiez_kontekst_rynku — hook W-300; "
                "ożywa gdy pętla portfelowa poda serie koszyka; lead-lag BTC→alty W-330)",
    "C-01":   "CROSS_RS (cross-sectional RS — pętla portfelowa wstrzykuje z-score zwrotu "
              "vs koszyk; backtest_portfel/petla_live; bez koszyka 1 para: abstynuje, W-335)",
    "NEWS-01": "NEWS_SENTYMENT (AdapterNewsLLM — wpięty w zbuduj_bojowy W-301; "
               "ożywa z RSS fetcher lub DEEPSEEK_API_KEY; bez feedu: abstynuje)",
    "NEWS-02": "NEWS_EVENT_KIERUNEK (AdapterNewsLLM + klasyfikator zdarzeń W-381 — "
               "kierunek per typ; ożywa z FetcherNewsRSS/feed; bez nagłówków: abstynuje)",
    "NEWS-03": "NEWS_ATTENTION_SPIKE (AdapterNewsLLM stan kroczący W-382 — przełom uwagi; "
               "ożywa po kilku barach z feedem; bez historii nagłówków: abstynuje)",
    "NEWS-04": "NEWS_SENTYMENT_DELTA (AdapterNewsLLM stan kroczący W-382 — momentum sentymentu; "
               "ożywa po ≥2 barach z feedem; bez historii: abstynuje)",
    "X-28":   "MTF_4H_RSI_14/MTF_1D_RSI_14 (Budowniczy MTF — ożywa gdy bary mają "
              "pole 'interwal' i odpowiedni TF; bez niego abstynuje per Prawo XV)",
    "Z-06":   "AMIHUD_20 wysoki (krucha płynność) — scenariusze audytu są płynne "
              "(duży obrót); ożywa przy cienkiej księdze (W-322)",
    "Z-07":   "PI_CYCLE wymaga ≥350 barów — scenariusze audytu mają 260; "
              "ożywa na pełnej historii 1D (W-322, kill-switch szczytu)",
    "OC-06":   "BTC_S2F wymaga realnego timestampu (block z daty) — scenariusze audytu "
               "mają sztuczny ts z ery 1970 → block 0 → S2F=0; ożywa na realnych barach (W-377)",
    "OC-07":   "BTC_DAYS_TO_HALVING wymaga realnego timestampu — jak OC-06; "
               "ożywa gdy bar ma datę w oknie ~180 dni przed halvingiem (W-378)",
    "OC-08":   "BTC_SUPPLY_INFLATION wymaga realnego timestampu — jak OC-06; "
               "ożywa gdy block daje inflację <2% (po 3. halvingu, W-379)",
}

# Dowód allowlisty (Prawo I — bez zaufania na słowo): każdy neuron adapterowy
# MUSI ożyć, gdy nakarmimy go ekstremalną wartością jego klucza. Jeśli milczy
# MIMO danych adaptera → realny bug (błąd blokujący, nie wybaczany allowlistą).
WERYFIKACJA_ADAPTEROW = {
    "PSY-01": {"FUNDING_RATE": 0.0025},                                   # crowded long → SHORT
    "PSY-02": {"LONG_SHORT_RATIO": 0.82},                                 # tłum long → SHORT
    "PSY-03": {"FEAR_GREED_INDEX": 8},                                    # ekstremalny strach → LONG
    "PSY-05": {"DVOL_INDEX": 85.0},                                       # ekstremalny strach opcji → LONG
    "K-03": {"STABLE_FLOW": 0.02},                                        # silny druk stablecoinów → LONG
    "K-04": {"USD_ZSCORE": 2.0},                                          # silny USD rozciągnięty → SHORT
    "PSY-04": {"OPEN_INTEREST": 150000.0, "OPEN_INTEREST_PREV": 100000.0,
               "CLOSE": 101.0, "CLOSE_PREV": 100.0},                      # OI↑ + cena → sygnał
    "V-03":   {"CVD": 5000.0, "CVD_PREV": 1000.0,
               "CLOSE": 101.0, "CLOSE_PREV": 100.0},                      # napływ kupna → LONG
    "AUG-01": {"EVENT_TYP": "HALVING", "EVENT_DNI_PO": 5.0,
               "EVENT_N": 3, "EVENT_PROB_WZROSTU": 100.0},                # analogia → LONG
    "RADAR-01": {"BTC_TREND": 0.9},                                       # BTC↑ → LONG-wsparcie
    "RADAR-02": {"BTC_DOMINANCJA": -0.9},                                 # alt-season → LONG-wsparcie
    "RADAR-03": {"PRZEPLYW_KAPITALU": 0.95},                              # napływ → LONG-wsparcie
    "RADAR-04": {"STRES_KORELACJI": 0.95, "BTC_TREND": -0.5},             # kaskada + BTC↓ → SHORT
    "RADAR-05": {"LEAD_BTC": 0.8},                                       # BTC pchnął↑ → LONG-wsparcie
    "C-01":    {"CROSS_RS": 1.5},                                        # lider koszyka → LONG
    "NEWS-01": {"NEWS_SENTYMENT": 0.8, "NEWS_PEWNOSC": 0.9, "NEWS_N": 5},  # mocno bycze → LONG
    "NEWS-02": {"NEWS_EVENT_KIERUNEK": -0.9, "NEWS_EVENT_TYP": "HACK",
                "NEWS_EVENT_PEWNOSC": 0.9},                                # hack → SHORT
    "NEWS-03": {"NEWS_ATTENTION_SPIKE": 3.0, "NEWS_SENTYMENT": 0.6},        # spike+byczo → LONG
    "NEWS-04": {"NEWS_SENTYMENT_DELTA": 0.5},                               # sentyment↑ → LONG
    "X-28":   {"CLOSE": 50000.0, "RSI_14": 60.0, "EMA_21": 49000.0,
               "MTF_4H_RSI_14": 65.0, "MTF_4H_EMA_50": 47000.0,
               "MTF_1D_RSI_14": 58.0, "MTF_1D_EMA_50": 46000.0},  # 3/3 TF LONG → LONG
    "Z-06":   {"AMIHUD_20": 5.0},                                 # krucha płynność → pewnosc_przeciwnika
    "Z-07":   {"PI_111": 105.0, "PI_350X2": 100.0,
               "PI_111_PREV": 98.0, "PI_350X2_PREV": 100.0},      # cross od dołu → SHORT
    "OC-06":   {"BTC_BLOCK_HEIGHT": 900_000},                      # po 4. halvingu, S2F>100 → LONG
    "OC-07":   {"BTC_BLOCK_HEIGHT": 839_700},                      # ~60 dni do halvingu → LONG
    "OC-08":   {"BTC_BLOCK_HEIGHT": 900_000},                      # inflacja <1% → LONG
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
            # Na starcie: liczba + KLUCZE (zwięźle). Pełne powody (dla każdego neuronu, po co
            # mu jaki adapter) drukuje `--luki` — powtarzanie ich co sesję ważyło 2.5 KB, a nie
            # zmieniają się między sesjami. Alarm pozostaje głośny i pełny co do liczby i kluczy.
            klucze = ", ".join(sorted(znane))
            info.append(
                f"ℹ️ Prawo XV — {len(znane)} modułów zależnych od adapterów: ŻYWE na realnych danych, "
                f"ciche tylko w syntetycznych scenariuszach audytu (adaptery istnieją i wpięte w "
                f"petla_live, zweryfikowane na żywo: Futures/FearGreed/CVD). ZMIERZ na żywo: "
                f"python narzedzia/cenzus_adapterow.py (20/22 ŻYWE 2026-07-15; AUG-01+RADAR-05 "
                f"warunkowo — bramka zdarzenia/siły). Klucze: {klucze}  (powody: --luki)"
            )

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
    if "--luki" in sys.argv:
        # Pełne powody Prawa XV: dla każdego neuronu adapterowego — jaki adapter/dane go ożywią.
        print("ℹ️ Prawo XV — moduły adapterowe: żywe na realnych danych (adaptery wpięte w petla_live),"
              " ciche tylko w syntetycznym audycie. Jaki feed/dane je ćwiczą:")
        for k in sorted(NEURONY_ZALEZNE_OD_ADAPTEROW):
            print(f"   • {k}: {NEURONY_ZALEZNE_OD_ADAPTEROW[k]}")
        sys.exit(0)

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
