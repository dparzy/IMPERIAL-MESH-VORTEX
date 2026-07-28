#!/usr/bin/env python3
"""
🔬 AUDYT SPÓJNOŚCI IMPERIUM — silnik Prawa XXI (KROK 0)

Uruchamiany automatycznie przez hooki Claude Code (SessionStart + Stop) oraz ręcznie:
    python narzedzia/audyt_spojnosci.py            # raport + exit code
    python narzedzia/audyt_spojnosci.py --cichy     # tylko gdy są błędy

Sprawdza warstwy 1–21 spójności (zgodnie z ZASADY_FUNDAMENTALNE.md § PRAWO XXI).
Lista poniżej JEST spisem — nie podajemy tu osobnej liczby, bo ręczna liczba zawsze się
rozjedzie z listą (zmierzone 2026-07-26: nagłówek mówił „16 warstw", gdy kod miał 18 —
Warstwy 17 i 18 dopisano do kodu, ale nie do tego spisu. Dokładnie klasa wady W15):
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
  Warstwa 15 — liczby:          bloki <!-- LICZBA:x --> zgodne z żywym kodem (Tabularium, Filar 4)
  Warstwa 16 — API-widma:       plik kodu cytowany w żywym docu MUSI istnieć (łowca widm)
  Warstwa 17 — census organów:  każdy moduł imperium/ i narzedzia/ zameldowany w CENSUS
  Warstwa 18 — LEX TALIONIS:    dług honorowy = 0 (zatwierdzony błąd ma kompensujący unikat)
  Warstwa 19 — parytet dat:     frontmatter `stan_na` = nagłówek "Stan na:" w tym samym pliku
  Warstwa 20 — katalog INDEKS:  sekcja generowana = to, co wypluwa Tabularium (zero ręcznych edycji)
  Warstwa 21 — wyzwalacze:      każdy `/skill` cytowany w konstytucji istnieje na dysku

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

        # Toleruj oba formaty: gołe „87 zaimplementowane" oraz blok W15
        # „87<!-- /LICZBA --> zaimplementowane" (README przeszło na LICZBA 2026-07-18).
        rn = re.search(r"(\d+)(?:<!-- /LICZBA -->)? zaimplementowane", readme)
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
                                  capture_output=True, text=True, timeout=5,
                                  encoding="utf-8", errors="replace")
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

        # REKURENCYJNIE (naprawa 2026-07-17): `os.listdir` widział TYLKO płaski docs/.
        # Przeniesienie dokumentu do podkatalogu (docs/migawki/) po cichu wypychało go
        # z bramki sierot — dokument znikał z kontroli dokładnie w chwili porządkowania.
        # Ta sama pułapka siedziała w rag/indeksuj.py (glob → rglob).
        docs_files = set()
        for katalog, podkatalogi, pliki in os.walk(docs_dir):
            podkatalogi[:] = [d for d in podkatalogi if d != "archiwum"]  # archiwum ma swoje zasady
            for f in pliki:
                if f.endswith(".md") and f not in INDEKS_WHITELIST:
                    rel = os.path.relpath(os.path.join(katalog, f), docs_dir)
                    docs_files.add(rel.replace("\\", "/"))

        sieroty = []
        for fname in sorted(docs_files):
            # W INDEKS katalog generowany wypisuje pełną ścieżkę (docs/migawki/X.md),
            # więc szukamy samej nazwy pliku — działa dla obu form zapisu.
            if os.path.basename(fname) not in indeks_txt:
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

    # ── WARSTWA 15: LICZBY WSTRZYKIWANE (Tabularium, Filar 4) ─────────────────
    w15_bledy, w15_info = _warstwa_15_liczby_wstrzykiwane()
    bledy += w15_bledy
    info += w15_info

    # ── WARSTWA 16: API-WIDMA — plik kodu opisany w docs MUSI istnieć ─────────
    w16_bledy, w16_info = _warstwa_16_api_widma()
    bledy += w16_bledy
    info += w16_info

    # ── WARSTWA 17: CENSUS ORGANORUM — każdy moduł kodu musi być zameldowany ──
    w17_bledy, w17_info = _warstwa_17_census_organorum()
    bledy += w17_bledy
    info += w17_info

    # ── WARSTWA 18: LEX TALIONIS — zatwierdzony błąd musi mieć kompensujący unikat ──
    w18_bledy, w18_info = _warstwa_18_dlug_honorowy()
    bledy += w18_bledy
    info += w18_info

    # ── WARSTWA 19: PARYTET DAT — jedna data, dwa miejsca, jedna prawda ───────
    w19_bledy, w19_info = _warstwa_19_parytet_dat()
    bledy += w19_bledy
    info += w19_info

    # ── WARSTWA 20: KATALOG INDEKS — sekcja generowana nietknięta ręką ────────
    w20_bledy, w20_info = _warstwa_20_katalog_nietkniety()
    bledy += w20_bledy
    info += w20_info

    # ── WARSTWA 21: WYZWALACZE — rozkaz odesłany do skilla MUSI być osiągalny ─
    w21_bledy, w21_info = _warstwa_21_wyzwalacze_rozkazow()
    bledy += w21_bledy
    info += w21_info

    # ── WARSTWA 22: JEDEN KATALOG DOKUMENTÓW — żadnych ręcznych spisów obok ───
    w22_bledy, w22_info = _warstwa_22_jeden_katalog()
    bledy += w22_bledy
    info += w22_info

    return bledy, info


def _warstwa_21_wyzwalacze_rozkazow():
    """W21 — każdy `/skill` cytowany w konstytucji musi istnieć na dysku.

    Powód (odchudzanie konstytucji 2026-07-27): CLAUDE.md schudł z 787 do 253 linii, bo
    treść 20 rozkazów stałych przeniesiono do sześciu skilli ładowanych NA ŻĄDANIE, a w
    konstytucji została linia-wyzwalacz z esencją. To oszczędza ~10 tys. tokenów na każdej
    sesji, ale tworzy NOWĄ klasę wady: rozkaz odesłany do skilla, którego nie ma, jest
    gorszy niż gruby CLAUDE.md — staje się NIEOSIĄGALNY, a Architekt nawet nie wie, że go
    zgubił. Jedno zmienione imię katalogu wystarczy.

    Bramka TWARDA, dokładnie jak W16 (API-widma) i W17 (census): dokument nie ma prawa
    obiecywać treści, której nie da się wczytać.

    Osobno — DŁUG DŁUGOŚCI konstytucji zostaje ALARMEM AERARIUM, nie bramką: 253 linie to
    wciąż więcej niż doktrynalne 200, a droga do 200 wiedzie przez przeniesienie checklist
    otwarcia/zamknięcia, co wymaga przebudowy SIGILLARIUM (dziś pieczęć czyta je wprost z
    CLAUDE.md). Twarde blokowanie commitów za dług, którego naprawa jest ryzykowna,
    wymusiłoby pośpiech na najwrażliwszym organie — dlatego widoczność tak, przymus nie.
    """
    import glob as _glob
    try:
        with open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8") as f:
            konst = f.read()
    except OSError as e:
        return [f"[W21] Nie mogę odczytać CLAUDE.md: {e}"], []

    katalog = os.path.join(ROOT, ".claude", "skills")
    istniejace = {os.path.basename(os.path.dirname(p))
                  for p in _glob.glob(os.path.join(katalog, "*", "SKILL.md"))}
    # Bierzemy WYŁĄCZNIE zapis `**`/nazwa`**` — tak wygląda wyzwalacz rozkazu. Goły `/slowo`
    # w prozie (np. ścieżka, „wejście/wyjście") nie jest obietnicą skilla i nie ma prawa
    # generować alarmu — warstwa pilnująca prawdy nie może produkować nieprawdy (lekcja W19).
    cytowane = set(re.findall(r"\*\*`/([a-z][a-z0-9_-]*)`\*\*", konst))
    widma = sorted(cytowane - istniejace)
    if widma:
        return [(f"[W21] Konstytucja odsyła do NIEISTNIEJĄCYCH skilli: {widma}. "
                 f"Rozkaz nieosiągalny — dodaj skill albo usuń wyzwalacz")], []
    return [], [f"Wyzwalacze rozkazów (W21): {len(cytowane)} skilli cytowanych w konstytucji, "
                f"wszystkie osiągalne ✅"]


def _warstwa_22_jeden_katalog(katalog_docs=None):
    """W22 — spis dokumentów wolno trzymać JEDNEMU dokumentowi: INDEKS_IMPERIUM.

    Powód (decyzja C Cezara 2026-07-27, zgłoszenie z recenzji cubic PR #133): `docs/README.md`
    trzymał ręczny spis tych samych dokumentów, które Tabularium generuje z nagłówków do
    INDEKSU. ZMIERZONE przed usunięciem: ręczny spis wymieniał 22 z 56 plików `docs/*.md`,
    czyli 33 dokumenty (59% korpusu) były dla niego niewidzialne — a nikt tego nie zauważył
    przez wiele wacht, bo gnicie drugiego spisu nie boli od razu. Klasyczne drugie źródło
    prawdy (Prawo XVI): gnije zawsze ten pisany ręką.

    Usunięcie samego spisu byłoby ŁATKĄ — spis odrodzi się przy pierwszym „dopiszę tu tylko
    jeden link". Ta warstwa broni KLASY: żaden żywy dokument poza INDEKSEM nie ma prawa
    urosnąć do rozmiaru katalogu.

    PRÓG zamiast zera — świadomie i po pomiarze. Zero byłoby fałszywym alarmem: dokument ma
    pełne prawo linkować do kilku innych (README wskazuje na INDEKS, konstytucję i ZASADY;
    MANUAL_DODAWANIE_AGENTOW cytuje dwa wzorce). Pomiar całego korpusu w chwili budowy
    warstwy: INDEKS 73 wiersze (generowane, wyłączone), docs/README 26 (usunięte tą decyzją),
    MANUAL_DODAWANIE_AGENTOW 2, WIZJONER 1, README repo 2 — nic pomiędzy. Próg 5 leży w pustce
    między „kilka odnośników" a „katalog", z zapasem nad zmierzonym maksimum przypadkowym (2).
    Warstwa pilnująca cudzej prawdy nie ma prawa produkować własnej nieprawdy (lekcja W19).

    ZASIĘG = WSZYSTKIE żywe dokumenty zadeklarowane w Tabularium (74, w tym 8 spoza `docs/`),
    nie sam katalog `docs/`. Pytanie o zasięg zadane OSOBNO od pytania o logikę — to nawracająca
    klasa wady Imperium (W11 pilnowała 1 katalogu z 11; dedup lekcji widział 91 z 298; PROBATOR
    badał dwa plony, czytaliśmy jeden). Katalog może odrodzić się w `imperium/README.md` równie
    dobrze jak w `docs/`, a bramka o wąskim zasięgu daje fałszywy spokój.
    """
    PROG_WIERSZY = 5
    ZWOLNIONE = {"INDEKS_IMPERIUM.md"}   # jedyny katalog — generowany, pilnowany przez W20

    # Wiersz katalogu = wiersz tabeli, którego PIERWSZA komórka wskazuje na dokument .md
    # (link `[X](Y.md)` albo `` `Y.md` ``). Wzmianka o .md w dalszych kolumnach to opis,
    # nie pozycja spisu — dlatego patrzymy wyłącznie na kolumnę pierwszą.
    komorka_md = re.compile(r"\]\([^)]+\.md[^)]*\)|`[^`]+\.md`")

    def policz(tresc):
        ile = 0
        for w in tresc.splitlines():
            if not w.startswith("|"):
                continue
            kolumny = w.split("|")
            if len(kolumny) > 1 and komorka_md.search(kolumny[1]):
                ile += 1
        return ile

    if katalog_docs:          # tryb testowy: płaski katalog na dysku
        korzen = katalog_docs
        pliki = [n for n in sorted(os.listdir(katalog_docs)) if n.endswith(".md")]
    else:                     # produkcja: żywe dokumenty zadeklarowane w Tabularium
        try:
            from narzedzia.tabularium import ROOT as T_ROOT
            from narzedzia.tabularium import zbierz_dokumenty
        except Exception as e:  # noqa: BLE001 — awaria warstwy nie może wywrócić audytu
            return [f"[W22] Błąd kontroli katalogów: {e}"], []
        korzen = T_ROOT
        pliki = [wzgledna for wzgledna, _ in zbierz_dokumenty()]

    bledy, zbadane = [], 0
    for wzgledna in pliki:
        if os.path.basename(wzgledna) in ZWOLNIONE:
            continue
        try:
            with open(os.path.join(korzen, wzgledna), encoding="utf-8") as f:
                tresc = f.read()
        except OSError:
            continue
        zbadane += 1
        ile = policz(tresc)
        if ile >= PROG_WIERSZY:
            bledy.append(
                f"[W22] {wzgledna}: {ile} wierszy wskazujących na dokumenty — to drugi "
                f"katalog obok INDEKS_IMPERIUM.md (próg {PROG_WIERSZY}). Spis dokumentów "
                f"generuje Tabularium; zostaw tu wskaźnik, nie kopię (Prawo XVI)")
    info = ([f"Jeden katalog (W22): {zbadane} dokumentów bez konkurencyjnego spisu ✅"]
            if not bledy else [])
    return bledy, info


def _warstwa_19_parytet_dat():
    """W19 — dwa pola deklarujące „stan na" muszą mówić to samo.

    Powód (recenzja zewnętrzna 2026-07-26): README miał `stan_na: 2026-07-19` we
    frontmatterze i „Stan na: 2026-07-26" w nagłówku. Audyt meldował „86 dokumentów,
    wszystkie nadążają ✅", bo Warstwa 6 czyta WYŁĄCZNIE nagłówek, a Tabularium czyta
    WYŁĄCZNIE frontmatter. Dwa organy pilnowały dwóch pól i żaden nie porównał ich ze
    sobą — klasa „dwa liczniki rozjadą się co do sztuki".

    Sprawdzamy tylko dokumenty mające OBA pola: brak któregokolwiek nie jest błędem
    (nie każdy dokument deklaruje datę), rozjazd między nimi — jest.

    ZASIĘG = NAGŁÓWEK DOKUMENTU (pierwsze `LINIE_NAGLOWKA` wierszy). Pierwsza wersja tej
    warstwy skanowała CAŁY plik i sama dała trzy fałszywe alarmy, złapane przed commitem:
      • LOG_ZMIAN — dopasowała frazę „Stan na:" CYTOWANĄ w treści wpisu changelogu,
      • KATALOG_NEURONOW i ROADMAP — datę SEKCJI w środku dokumentu, która opisuje tę
        sekcję, a nie cały plik, więc porównywanie jej z frontmatterem jest bez sensu.
    Warstwa pilnująca prawdy nie ma prawa produkować nieprawdy o cudzych dokumentach.
    """
    LINIE_NAGLOWKA = 30
    try:
        from narzedzia.tabularium import ROOT as T_ROOT
        from narzedzia.tabularium import zbierz_dokumenty
    except Exception as e:  # noqa: BLE001 — awaria warstwy nie może wywrócić audytu
        return [f"[W19] Błąd parytetu dat: {e}"], []

    bledy, sprawdzone = [], 0
    for wzgledna, meta in zbierz_dokumenty():
        fm = (meta or {}).get("stan_na")
        if not fm:
            continue
        try:
            with open(os.path.join(T_ROOT, wzgledna), encoding="utf-8") as f:
                tresc = f.read()
        except OSError:
            continue
        naglowek = "\n".join(tresc.splitlines()[:LINIE_NAGLOWKA])
        m = re.search(r"Stan na:\s*\**\s*(\d{4}-\d{2}-\d{2})", naglowek)
        if not m:
            continue
        sprawdzone += 1
        if str(fm).strip() != m.group(1):
            bledy.append(
                f"[W19] {wzgledna}: frontmatter `stan_na: {fm}` ≠ nagłówek "
                f"'Stan na: {m.group(1)}' — jedna data, dwa miejsca, jedna prawda")
    info = ([f"Parytet dat (W19): {sprawdzone} dokumentów z obiema datami — zgodne ✅"]
            if not bledy else [])
    return bledy, info


def _warstwa_20_katalog_nietkniety():
    """W20 — sekcja katalogu w INDEKS musi być tym, co generuje Tabularium.

    Powód (recenzja zewnętrzna 2026-07-26): do sekcji opisanej „NIE edytuj ręcznie"
    dopisano wiersz `docs/ZADANIE_TIRO_E3_ZNIWO.md` — w sekcji CONSILIUM, choć dokument
    deklaruje `kategoria: DISCIPLINA`. Audyt przepuścił, bo pilnował wyłącznie OBECNOŚCI
    dokumentu w INDEKS (Warstwa 7), nigdy jego MIEJSCA. Regeneracja katalogu ujawniła
    przy okazji trzy dodatkowe nieaktualne daty — ręczna edycja artefaktu generowanego
    kłamie do pierwszego `--zapisz`.

    Lekarstwo jak w CENSUS ORGANORUM (W17): odebrać dokumentowi prawo do własnej treści.

    Porównujemy STRUKTURĘ (nagłówki sekcji + wiersze tabel), świadomie POMIJAJĄC linię
    „Ostatni spis: <data>" — ta zmienia się każdego dnia, więc dosłowne porównanie
    żądałoby przepisywania katalogu codziennie. To ten sam fałszywy alarm, który
    naprawiliśmy w Warstwie 6 (data porównywana z commitem, nie z `date.today()`).
    """
    try:
        from narzedzia.tabularium import ROOT as T_ROOT
        from narzedzia.tabularium import (ZNACZNIK_KONIEC, ZNACZNIK_START, katalog_md)
    except Exception as e:  # noqa: BLE001 — awaria warstwy nie może wywrócić audytu
        return [f"[W20] Błąd kontroli katalogu: {e}"], []

    indeks = os.path.join(T_ROOT, "docs", "INDEKS_IMPERIUM.md")
    try:
        with open(indeks, encoding="utf-8") as f:
            tresc = f.read()
    except OSError as e:
        return [f"[W20] Nie mogę odczytać INDEKS_IMPERIUM.md: {e}"], []

    if ZNACZNIK_START not in tresc or ZNACZNIK_KONIEC not in tresc:
        return [("[W20] INDEKS_IMPERIUM.md nie ma znaczników sekcji generowanej — "
                 "katalog przestał być pod kontrolą Tabularium")], []

    # ZNACZNIK MUSI BYĆ DOKŁADNIE JEDEN (recenzja cubic PR #134, P2 — przyjęta 2026-07-27).
    # Bramka sprawdzała OBECNOŚĆ, a porównanie bierze `split(...)[1]`, czyli treść między
    # PIERWSZĄ parą znaczników. Przy zdublowanym `start` drugi blok zostaje poza kontrolą:
    # generator ma dwie kandydujące sekcje, audyt ogląda jedną i melduje „zgodne ✅".
    # To ta sama klasa co bramka pilnująca jednego katalogu z jedenastu — wąski zasięg
    # produkujący fałszywy spokój, więc liczba znaczników jest częścią kontraktu, nie detalem.
    ile_s, ile_k = tresc.count(ZNACZNIK_START), tresc.count(ZNACZNIK_KONIEC)
    if ile_s != 1 or ile_k != 1:
        return [(f"[W20] INDEKS_IMPERIUM.md ma {ile_s}× znacznik START i {ile_k}× KONIEC "
                 "(ma być po jednym) — sekcja poza pierwszą parą jest niezarządzana przez "
                 "Tabularium, a porównanie treści widziałoby tylko pierwszą")], []

    def istotne(tekst):
        """Wiersze niosące treść katalogu: nagłówki sekcji i wiersze tabeli."""
        return [w.strip() for w in tekst.splitlines()
                if w.startswith("### ") or (w.startswith("|") and "Ostatni spis" not in w)]

    w_pliku = istotne(tresc.split(ZNACZNIK_START, 1)[1].split(ZNACZNIK_KONIEC, 1)[0])
    z_kodu = istotne(katalog_md())
    if w_pliku == z_kodu:
        return [], [f"Katalog INDEKS (W20): {len(z_kodu)} wierszy zgodnych z generatorem ✅"]

    nadmiar = [w for w in w_pliku if w not in z_kodu]
    brak = [w for w in z_kodu if w not in w_pliku]
    szczegol = []
    if nadmiar:
        szczegol.append(f"dopisane ręcznie ({len(nadmiar)}): {nadmiar[0][:90]}")
    if brak:
        szczegol.append(f"brakujące ({len(brak)}): {brak[0][:90]}")
    if not szczegol:          # te same wiersze, inna KOLEJNOŚĆ (zła sekcja / złe sortowanie)
        szczegol.append("te same wiersze w innej kolejności lub sekcji")
    return [("[W20] Katalog w INDEKS_IMPERIUM.md rozjechał się z generatorem — "
             + "; ".join(szczegol)
             + ". Napraw: python narzedzia/tabularium.py katalog --zapisz")], []


def _warstwa_18_dlug_honorowy(sciezka=None):
    """W18 — niespłacony dług honorowy (LEX TALIONIS) zatrzymuje commit.

    Powód (zwiad adwersarialny 2026-07-21, decyzja Cezara): bilans not był najpierw
    sprawdzany WYŁĄCZNIE w kroku 5b zamknięcia sesji, potem — po pierwszej naprawie —
    również drukowany na otwarciu. Ale drukowanie to WIDOCZNOŚĆ, nie EGZEKWOWALNOŚĆ:
    `codex_notarum bilans` nie zwracał niezerowego kodu, a hook wołał go z `|| true`.
    Dług otwarty w sesji N mógł więc przeżyć N+1 i N+2, mimo że zasada mówi wprost:
    „sesja nie domyka się z niespłaconym długiem honorowym".

    Bramka TWARDA (decyzja Cezara), tak jak W17. Miękki alarm odrzucony świadomie —
    to ten sam mechanizm, który u nas zawiódł już dwa razy (wąska Warstwa 11 przy
    „pełnej harmonii", alarm W9 wiszący przez sesje). Alarm, którego wolno nie
    posłuchać, prędzej czy później nie zostaje posłuchany.

    Zakleszczenia nie ma: dług spłaca się dopisaniem CORONY do ledgera, co nie wymaga
    commitu — więc bramka nigdy nie blokuje własnej naprawy.

    `sciezka` istnieje, żeby bramkę dało się SPRAWDZIĆ na sztucznym ledgerze. Bez tego
    dowód „czy gryzie" był niewykonalny: `bilans(sciezka=LEDGER)` wiąże domyślny argument
    w chwili definicji, więc podmiana stałej modułu NIE ma wpływu — pierwsza wersja mojego
    dowodu po cichu czytała prawdziwy ledger i meldowała zieleń dla sztucznego długu.
    Klasa: skrypt weryfikujący, który mierzy co innego, niż deklaruje.
    """
    try:
        from imperium.biblioteki.codex_notarum import bilans
        b = bilans(sciezka) if sciezka is not None else bilans()
        dlug = b.get("dlug_honorowy") or []
        if not dlug:
            return [], [f"LEX TALIONIS (W18): dług honorowy 0 — {b['noty']} not, "
                        f"{b['korony']} koron ✅"]
        opisy = "; ".join(str(n.get("opis", "?"))[:80] for n in dlug[:3])
        return [f"[W18] DŁUG HONOROWY: {len(dlug)} zatwierdzonych błędów bez kompensującego "
                f"unikatu (LEX TALIONIS). Dostarcz CORONĘ zanim commitujesz: {opisy}"], []
    except Exception as e:  # noqa: BLE001 — awaria ledgera nie może wywrócić audytu
        return [f"[W18] Błąd odczytu CODEX NOTARUM: {e}"], []


def _warstwa_17_census_organorum():
    """W17 — każdy moduł `imperium/` i `narzedzia/` musi być w CENSUS_ORGANORUM.

    Powód (zmierzone 2026-07-20, zarzut Cezara): Warstwa 11 pilnowała meldunku
    WYŁĄCZNIE dla `imperium/biblioteki/` — 1 katalog z 11. Dlatego
    `imperium/cesarz/dispensator.py` (152 linie + testy) przeżył całą sesję nie
    występując w ŻADNYM dokumencie, a audyt meldował „✅ pełna harmonia". Łącznie
    19 modułów `imperium/` i 31 narzędzi milczało bezkarnie.

    Bramka TWARDA (decyzja Cezara 2026-07-20): rozjazd = czerwień = commit stoi.
    Miękkie ostrzeżenie odrzucone świadomie — to dokładnie mechanizm, który już raz
    zawiódł (alarm widoczny i ignorowany przez sesje, ZASADA CENSORA).
    """
    try:
        # Import przez pakiet `narzedzia`, NIE przez wstrzyknięcie katalogu w sys.path:
        # `census_organorum` i `narzedzia.census_organorum` byłyby DWOMA modułami o
        # osobnym stanie (własne DOKUMENT, własne cache). Testy patchują jedną kopię,
        # audyt czytałby drugą — bramka mogłaby świecić na zielono na innym module niż
        # ten, który sprawdzamy. Klasa: podwójna tożsamość modułu.
        from narzedzia.census_organorum import spisz_moduly, sprawdz
        bledy = sprawdz()
        lacznie = sum(len(v) for v in spisz_moduly().values())
        info = [f"Census organów (W17): {lacznie} modułów zameldowanych ✅"] if not bledy else []
        return bledy, info
    except Exception as e:  # noqa: BLE001 — awaria cenzusu nie może wywrócić audytu
        return [f"[W17] Błąd cenzusu organów: {e}"], []


def _warstwa_15_liczby_wstrzykiwane():
    """Każdy blok <!-- LICZBA:x --> musi zgadzać się z żywym kodem.

    Ręcznie wpisana liczba w dokumencie ZAWSZE się rozjedzie — bo rośnie kod, nie
    dokument. Zmierzone 2026-07-17: trzy dokumenty podawały „neuronów w kodzie" jako
    47, 27 i 55 przy 87 w rejestrze; każda była prawdziwa w dniu pisania. Ta warstwa
    pilnuje, że raz wstrzyknięta liczba nie zamarznie ani nie zostanie nadpisana ręcznie.
    Naprawa jedną komendą: `python narzedzia/tabularium.py liczby --zapisz`.
    """
    bledy, info = [], []
    try:
        from narzedzia.tabularium import wstrzyknij_liczby
        zmiany, blad_kluczy = wstrzyknij_liczby(sucho=True)   # sucho: audyt NIGDY nie pisze
    except Exception as e:  # noqa: BLE001 — brak modułu/rejestru nie może wywrócić audytu
        info.append(f"⚠️ W15: liczby wstrzykiwane pominięte ({type(e).__name__}: {e})")
        return bledy, info

    bledy += blad_kluczy
    if zmiany:
        bledy.append("[W15] Wstrzyknięte liczby ROZJECHAŁY SIĘ z kodem (napraw: "
                     "python narzedzia/tabularium.py liczby --zapisz): " + "; ".join(zmiany))
    else:
        info.append("Liczby wstrzykiwane (W15): wszystkie zgodne z żywym kodem ✅")
    return bledy, info


# Dokumenty POMIJANE (Prawo I — nie falsyfikujemy historii): akumulują przeszłość
# lub rejestrują zamiary, więc ścieżka do pliku, którego dziś nie ma, to prawda ich
# czasu, nie kłamstwo. LOG_ZMIAN/WERSJONOWANIE = changelog; WIZJONER/ODLOZONE = rejestr
# pomysłów; PAMIEC_SESJI = kronika. Datowane-w-nazwie snapshoty lecą osobnym filtrem.
_W16_POMIJANE = {"LOG_ZMIAN.md", "WERSJONOWANIE.md", "WIZJONER.md",
                 "ODLOZONE_DECYZJE.md", "PAMIEC_SESJI.md"}

# Markery w LINII, które zmieniają twierdzenie „ten plik istnieje" w „ma powstać /
# nie istnieje / to przykład". Zmierzone na realnych trafieniach (2026-07-18): bez nich
# ODLOZONE „(do zbudowania)" i PAPER_TRADING „pliku, który NIGDY nie istniał" byłyby
# fałszywym alarmem.
#
# GRANICA SŁOWA OBOWIĄZKOWA dla stemów (recenzja 2026-07-18): goły podłańcuch „todo"
# trafia WEWNĄTRZ „metodologia", a „wizja" wewnątrz „telewizja/dywizja" (a Legiony mają
# dywizje!) → prawdziwe widmo na takiej linii byłoby po cichu zciszone (false-negative).
# `\b` przed stemem to blokuje: „telewizja" ma literę przed „wizja", więc brak granicy.
_W16_MARKERY_TEKST = re.compile(
    r"\b(?:do zbudowania|do zrobienia|do powstania|planowan|nie istnia|"
    r"todo|wizja|widmo|usunięt|usuniet|zarchiwizowan)", re.IGNORECASE)
# Symbole/frazy z własną granicą (emoji nie jest znakiem-słowem, więc \b nie działa).
_W16_MARKERY_SYMBOL = ("🔴", "🟠", "💭", "(plan")

# Ścieżki-korzenie kodu, które muszą fizycznie istnieć, gdy dokument je cytuje jako fakt.
_W16_KORZENIE = ("imperium", "narzedzia", "tests", "skrypty")

_W16_PAT = re.compile(r"(?:" + "|".join(_W16_KORZENIE) + r")/[A-Za-z0-9_/]+\.py")


def _w16_widma_w_tresci(tresc: str, real: set) -> list:
    """Czysty skaner JEDNEGO dokumentu — zwraca [(sciezka, nr_linii)] dla widm.

    Wydzielony z warstwy, żeby testy granic (Reguła Test-Granic) mogły podać treść
    wprost, bez zaśmiecania docs/. Suppresje: bloki ```python/```py oraz markery
    planu/negacji w linii. NIE decyduje o wyborze dokumentu (POMIJANE/snapshoty) —
    to robi warstwa przy iteracji po plikach.
    """
    znalezione = []
    fence_py = False
    for nr, linia in enumerate(tresc.splitlines(), 1):
        stripped = linia.lstrip()
        if stripped.startswith("```"):
            jezyk = stripped[3:].strip().lower()
            fence_py = jezyk in ("python", "py", "python3") if not fence_py else False
            continue
        if fence_py:
            continue                        # kod przykładowy — nie twierdzenie o istnieniu
        if _W16_MARKERY_TEKST.search(linia) or any(s in linia for s in _W16_MARKERY_SYMBOL):
            continue                        # plan / negacja / widmo oznaczone wprost
        for m in _W16_PAT.finditer(linia):
            if m.group(0) not in real:
                znalezione.append((m.group(0), nr))
    return znalezione


def _w16_realne_pliki() -> set:
    """Zbiór ścieżek .py fizycznie istniejących (bez .git/archiwum/cache).

    archiwum/ NIE liczy się jako „istnieje" — plik przeniesiony do archiwum, a wciąż
    cytowany w żywym docu jako `imperium/…`, to widmo (przypadek war_lancer/valhalla).
    """
    real = set()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if any(seg in dirpath for seg in (os.sep + ".git", os.sep + "archiwum",
                                          os.sep + "__pycache__", os.sep + ".pytest_cache")):
            continue
        for f in filenames:
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(dirpath, f), ROOT).replace(os.sep, "/")
                real.add(rel)
    return real


def _warstwa_16_api_widma():
    """W16 — API opisane w żywym dokumencie MUSI istnieć w kodzie (łowca widm).

    DZIURA, KTÓRĄ TO ZATYKA (zmierzona 2026-07-18, sesja sztabowa): spłata długu gnicia
    szła DOKUMENT-PO-DOKUMENCIE (czy nadąża za sobą / za kodem który opisuje), więc
    NIE łapała odwołań do plików, których NIGDY nie było. Skan całego korpusu naraz
    znalazł 3 martwe komendy w żywym INDEKS-ie (`mexc_feed.py`, `calculator_gate.py` →
    dziś `brama_kalkulatora.py`, `veto_check.py`) — każda przechodziła audyt „pełna
    harmonia". To ta sama klasa co war_lancer/sala_wojenna/valhalla (ARCHITEKTURA
    twierdziła `imperium/…`, a pliki leżą w archiwum/kingdom_pixel_p1/) i Kronikarz v2
    Interrogator (0 trafień w kodzie): API-widmo.

    DLACZEGO ŚCIEŻKA-PLIK, NIE KLASA/FUNKCJA: pełna ścieżka `korzeń/…/x.py` to
    jednoznaczne twierdzenie „ten plik istnieje TU". Nazwy klas/funkcji są zbyt
    wieloznaczne (przykłady w prozie, cytaty, homonimy) — łapanie ich = szum, którego
    Prawo XVI zakazuje. Ścieżka łapie 4/5 znanych wpadek przy zerowym szumie.

    SUPRESJE (inaczej alarm bez pomiaru = też halucynacja — lekcja 2026-07-17):
      • dokumenty-changelogi/rejestry-zamiarów (_W16_POMIJANE) i datowane snapshoty,
      • bloki ```python/```py — kod przykładowy (MANUAL uczy „stwórz vulcan.py"),
      • markery planu/negacji w linii (_W16_MARKERY_PLANU).
    Zwalidowane: na obecnym korpusie 9 kandydatów → 6 poprawnie zciszonych, 3 realne
    widma. Twarda bramka dopiero PO naprawie tych 3 (żeby start był czysty).
    """
    bledy, info = [], []
    docs_dir = os.path.join(ROOT, "docs")
    if not os.path.isdir(docs_dir):
        return bledy, info

    real = _w16_realne_pliki()
    widma = {}   # sciezka -> [(plik, linia_nr)]
    for nazwa in sorted(os.listdir(docs_dir)):
        if not nazwa.endswith(".md"):
            continue
        if nazwa in _W16_POMIJANE:
            continue
        if re.search(r"\d{4}-\d{2}-\d{2}", nazwa):     # snapshot datowany nazwą
            continue
        with open(os.path.join(docs_dir, nazwa), encoding="utf-8", errors="replace") as f:
            tresc = f.read()
        for sciezka, nr in _w16_widma_w_tresci(tresc, real):
            widma.setdefault(sciezka, []).append((nazwa, nr))

    if widma:
        opis = "; ".join(
            f"{s} ({', '.join(f'{fn}:{ln}' for fn, ln in occ[:2])})"
            for s, occ in sorted(widma.items()))
        bledy.append("[W16] API-WIDMO — żywy dokument cytuje plik kodu, którego NIE MA "
                     "(napraw ścieżkę, usuń martwą komendę albo oznacz jako plan/wizja): "
                     + opis)
    else:
        info.append("API-widma (W16): każda ścieżka .py cytowana w żywych docs istnieje w kodzie ✅")
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
        info.append("Ruff (W13): czysto ✅ (F/E9/E711-714/B006-008/B904/PLE/RUF034 "
                    "— bez bugów/martwego kodu)")
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
    # JEDEN parser praw dla całego Imperium (Prawo XVI) — `tabularium.policz_prawa()`.
    # Wcześniej ten sam regex żył w dwóch miejscach; dwa parsery tego samego formatu
    # rozjeżdżają się co do znaku, a bramka pilnująca prawdy nie może sama zgadywać.
    try:
        from narzedzia.tabularium import policz_prawa
        _liczba_praw = str(policz_prawa())
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
        # Legenda kategorii przeniesiona 2026-07-17: LEGIONY_ARCHITEKTURA miała jej DRUGĄ,
        # ręczną kopię — identycznie fałszywą (zmyślone E/G, brak C/D/N/Z). Scalona w jedno
        # źródło u GENERAŁA, bo to on używa KATEGORIA jako klucza w WAGI_REZIMU.
        # Bramka MUSI wędrować za treścią — inaczej pilnuje pustego miejsca (złapane przez
        # nią samą przy tym scaleniu; to koszt sprawdzeń zaszytych na sztywno per dokument).
        ("docs/GENERAL_LEGATUS.md", "Hurst",
         "GENERAL_LEGATUS.md brak 'Hurst' — kategoria H nie opisana w legendzie kategorii"),
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
        # ALARM IDZIE NA STDOUT, NIE NA STDERR (zmierzone 2026-07-26 — realna luka).
        # Powód: hook startowy woła ten audyt, a środowisko utrwala z hooka WYŁĄCZNIE
        # stdout. Przy czerwonym audycie stdout miał 0 bajtów, więc otwarcie sesji
        # pokazywało pod nagłówkiem „KROK 0" PUSTĄ LINIĘ. Gałąź „pełna harmonia" pisała
        # na stdout, więc sesja ZDROWA wyglądała GŁOŚNIEJ niż sesja z alarmem — milczenie
        # udające spokój, najgroźniejsza odmiana klasy „milczenie udające wynik".
        # Kod wyjścia 1 nadal bramkuje commit; zmienia się tylko widoczność.
        print("🚨 AUDYT SPÓJNOŚCI — WYKRYTO ROZBIEŻNOŚCI (złamanie Prawa XXI):")
        for b in bledy:
            print(f"  ❌ {b}")
        print("\n→ STOP. Napraw spójność zanim zaczniesz/zakończysz zadanie.")
        sys.exit(1)

    if not cichy:
        print("🔬 AUDYT SPÓJNOŚCI (Prawo XXI) — ✅ pełna harmonia")
        for i in info:
            print(f"   • {i}")
    sys.exit(0)


if __name__ == "__main__":
    main()
