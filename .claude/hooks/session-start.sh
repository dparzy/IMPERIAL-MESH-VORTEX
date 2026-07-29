#!/bin/bash
# 🏛️ IMPERIAL MESH VORTEX — SessionStart hook
# Instaluje zależności żywego systemu w świeżym kontenerze (Claude Code na webie),
# potem uruchamia audyt spójności (Prawo XXI) jako KROK 0.
#
# Testy działają bez zależności (Prawo I), ale pełna moc Imperium (Brama TA-Lib,
# numpy, dashboard, AI) wymaga pakietów z requirements.txt.
#
# ── ZASADA WYDRUKU (rozkaz Cezara 2026-07-26: „hook musi zawierać wszystko, żeby nie było
#    luk — zgodnie z zasadami oszczędzania tokenów i pod nadzorem") ────────────────────────
# KOMPLETNOŚĆ JEST TANIA, ROZWLEKŁOŚĆ NIE. Zmierzone na biegu 2026-07-26 (35,5 KB wydruku):
# DZIENNIK 84% · audyt 5% · Centrum Pamięci 4% · BREVIARIUM 2% · WSZYSTKIE POZOSTAŁE ORGANY
# RAZEM ~4% (1,3 KB, każdy po jednej linii). Dokładanie organu kosztuje ~100 zn. — dokładanie
# rozwiniętych narracji kosztuje ~2 000 zn. każda. Stąd reguły:
#   1. Każdy nowy organ w hooku drukuje JEDNĄ linię, a pełny raport ma pod osobną komendą.
#   2. Cisza gdy zielone, krzyk gdy czerwone — banery nie opisują stanu normalnego.
#   3. Liczby GENEROWANE z żywego kodu, nigdy wpisane w ten plik (klasa wady W15).
#   4. AERARIUM (krok 0.75) mierzy koszt POPRZEDNIEGO wydruku i wskazuje blok dominujący,
#      więc każde dołożenie meldunku jest widoczne w rachunku, a nie na wiarę.
#
# ŚWIADOMIE POMINIĘTE (to nie luki — to decyzje z podanym powodem):
#   • cenzus adapterów (narzedzia/cenzus_adapterow.py) — wymaga SIECI i realnych feedów;
#     na starcie byłby wolny i kruchy. Uruchamiany na żądanie przy pracy z adapterami.
#   • pełny raport CODEX PROBATIONUM (Excel, 12 arkuszy) — na starcie idzie tylko
#     jednolinijkowe podsumowanie ledgera; generowanie arkusza to zadanie, nie meldunek.
#   • pełny skan wad całego repo — na starcie tylko ostatni commit; pełny skan przed push.
#   • `/usage` — komenda interaktywna bez API; zużycia planu NIE da się odczytać skryptem,
#     dlatego AERARIUM świadomie tego nie udaje (Prawo I), a liczbę podaje Cezar.
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

# 0) SYNC Z GITHUB (koniec „kręcenia się w kółko" — Cezar 2026-07-04)
#    Root cause: laptop i chmura to DWA osobne checkouty. Gdy laptop nie pociągnął
#    ostatnich commitów, Claude czyta STARE dokumenty i „nic nie wie" o świeżej pracy.
#    Bezpieczny auto-pull: TYLKO gdy drzewo czyste i pull jest fast-forward (--ff-only).
#    Brudne drzewo / rozjazd → NIE ruszamy nic, tylko podpowiedź (żadnych konfliktów, żadnej utraty).
if git rev-parse --git-dir >/dev/null 2>&1; then
  GALAZ="$(git symbolic-ref --short HEAD 2>/dev/null || echo '')"
  if [ -n "$GALAZ" ]; then
    if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
      echo "[hook] SYNC — git pull --ff-only origin $GALAZ (aktualny status z GitHub)..."
      if git pull --ff-only origin "$GALAZ" 2>&1 | grep -qE "Already up to date|Updating|Fast-forward"; then
        echo "[hook] SYNC ✅ — repo na najnowszym commicie."
      else
        echo "[hook] SYNC ⚠️ — nie fast-forward (lokalne commity lub rozjazd). Zrób ręcznie:"
        echo "         git pull --rebase origin $GALAZ"
      fi
    else
      echo "[hook] SYNC ⏭️ — drzewo brudne (niezacommitowane zmiany), pomijam auto-pull."
      echo "         Zacommituj albo 'git stash', potem: git pull --rebase origin $GALAZ"
    fi
  fi
fi

# 0.5) NASTĘPNY KROK na GÓRZE (A2 — uszczelnienie OTWARCIA 2026-07-19).
#      Powód (luka L7): pełny wydruk hooka (~25 KB) ucinał podgląd w harnessie i plan
#      „→ następny" z Dziennika wypadał poza pierwsze okno. Ta jedna linia u samej góry
#      jest zawsze widoczna, zanim audyt/pamięć zaleją ekran.
if [ -f imperium/biblioteki/dziennik_niesmiertelny.py ]; then
  python -m imperium.biblioteki.dziennik_niesmiertelny nastepny || true
fi

# 0.6) PORTITOR — celnik u wrót: pre-flight środowiska (B1 — uszczelnienie OTWARCIA 2026-07-19).
#      Lekki, BEZ SIECI, stdlib-only: Python + krytyczne deps (numpy/TA-Lib) + OBECNOŚĆ kluczy
#      API (nigdy wartość) + świeżość danych + dryf vs baseline. Uzupełnia CENSOR SPRZĘTU
#      (żelazo) i CENZUS ADAPTERÓW (sieć) — Prawo XVI. Non-blocking, zwięzły banner.
if [ -f imperium/pretorianie/portitor.py ]; then
  python -m imperium.pretorianie.portitor banner || true
fi

# 0.7) CENSOR SPRZĘTU — cenzus ŻELAZA na starcie (rozkaz Cezara 2026-07-20).
#      Powód: Architekt twierdził w rozmowie „8 GB Fujitsu" Z PAMIĘCI, mając ten organ
#      w kodzie — CENSOR mierzy 15.88 GB. Liczby o sprzęcie mają stać przed oczami ZANIM
#      padnie jakakolwiek teza o wydajności (Prawo XVII: policzone, nie wspominane).
if [ -f imperium/oczy/censor_sprzetu.py ]; then
  python -c "from imperium.oczy.censor_sprzetu import banner; print(banner())" 2>/dev/null || true
fi

# 0.75) AERARIUM — skarbiec: ile kontekstu kosztuje SAM START sesji + stopnie wysiłku.
#       Stoi obok CENSORA świadomie: tam waga ŻELAZA, tu waga KONTEKSTU. Powód (zmierzone
#       2026-07-26): CLAUDE.md urósł do 760 linii przy zalecanych 200, a koszt startu nie
#       był nigdzie widoczny, więc rósł niezauważony (klasa wady „rzecz niemierzona rośnie").
if [ -f imperium/cesarz/aerarium.py ]; then
  python -c "from imperium.cesarz.aerarium import banner; print(banner())" 2>/dev/null || true
fi

# 0.8) INDEX FALSORUM — czy obalone twierdzenie nie żyje dalej w korpusie jako fakt.
if [ -f imperium/biblioteki/index_falsorum.py ]; then
  python -m imperium.biblioteki.index_falsorum || true
fi

# 0.9) BREVIARIUM — zwięzły spis SŁUG Imperium (zarzut Cezara 2026-07-21).
#      Powód: hook wołał 10 organów i ani jeden nie mówił, co robią HYGINUS i TIRO ani
#      z jakich modeli korzystamy. Dwaj słudzy z osobnymi rozkazami i osobnymi kosztami
#      byli na otwarciu niewidzialni — stan kolejki, plon czekający na sędziego, pary
#      nauczyciela, modele na dysku trzeba było wygrzebywać ręcznie co sesję.
if [ -f imperium/oczy/breviarium.py ]; then
  # --migawka: drukuje meldunek I utrwala punkt odniesienia, żeby domknięcie wachty
  # mogło pokazać RÓŻNICĘ (co ta sesja zmieniła), a nie tylko stan.
  python -m imperium.oczy.breviarium --migawka || true
fi

# 0.9b) SCHOLA CAESARIS — jedna linia nauki (rozkaz Cezara 2026-07-29: „dokument żywy
#       stale podlegający rozwojowi i pamiętany co sesja"). JEDNA linia, nie raport —
#       AERARIUM pilnuje wagi wydruku, a szkoła ma przypominać o sobie, nie zajmować
#       ekranu. Postęp i lista hipotez są LICZONE z dokumentu przy każdym wywołaniu,
#       więc spis nie może zgnić (klasa wady: runbook W11 z własną, ręczną treścią).
if [ -f imperium/biblioteki/schola.py ]; then
  python -m imperium.biblioteki.schola linia || true
fi

# 0.10) LEX TALIONIS — dług honorowy NA OTWARCIU (zarzut Cezara 2026-07-21, potwierdzony).
#       Powód: bilans not stał WYŁĄCZNIE w kroku 5b zamknięcia. Sesja urwana przed
#       domknięciem zostawiała niespłacony dług, którego następne otwarcie NIE POKAZYWAŁO —
#       czyli jedyny mechanizm pilnujący długu milkł dokładnie wtedy, gdy był potrzebny.
#       Klasa znana: bramka widoczna tylko na jednym końcu procesu.
if [ -f imperium/biblioteki/codex_notarum.py ]; then
  python -m imperium.biblioteki.codex_notarum bilans || true
fi

# 1) Instalacja zależności — tylko w środowisku zdalnym (lokalnie masz swoje venv)
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  if [ -f requirements.txt ]; then
    echo "[hook] Instaluję zależności Imperium (requirements.txt)..."
    python -m pip install --quiet --disable-pip-version-check -r requirements.txt || \
      echo "[hook] UWAGA: część zależności nie wstała — testy i tak przejdą (Prawo I, fallback)."
  fi
  # PYTHONPATH=. by importy 'imperium.*' działały z każdego miejsca
  if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
    echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"
  fi
fi

# 2) KROK 0 — audyt spójności (Prawo XXI). Nie blokuje startu (|| true).
if [ -f narzedzia/audyt_spojnosci.py ]; then
  echo "[hook] KROK 0 — audyt spójności (Prawo XXI):"
  python narzedzia/audyt_spojnosci.py || true
fi

# 2b) CODEX PROBATIONUM — podsumowanie rejestru testów na starcie (C1 — 2026-07-19).
#     Domyka asymetrię: CODEX był tylko w ZAMKNIĘCIU (krok 2 checklisty). Tanie — czyta
#     ledger JSONL, NIE generuje Excela (ZASADA CODEX PROBATIONUM: czytany PRZED zadaniem).
if [ -f narzedzia/codex_probationum.py ]; then
  echo "[hook] CODEX PROBATIONUM (podsumowanie ledgera):"
  python narzedzia/codex_probationum.py --podsumowanie || true
fi

# 3) CENTRUM PAMIĘCI (W-360 v5) — scored TOP-k lekcji (Generative Agents: recency×importance×relevance)
#    + profil Cezara + alarm przepełnienia + cross-layer search. Zastępuje proste "ostatnie 3".
# CENTRUM_OK=1 tylko gdy centrum_pamieci start faktycznie wydrukował podsumowanie
# (w tym statystyki kroniki „X sesji, Y MB"). Na ścieżce awaryjnej (centrum pada → pamiec_sesji
# start) statystyk kroniki NIE ma — dlatego niżej dodrukowuje je kronika_czatu (recenzja cubic).
CENTRUM_OK=0
if [ -f imperium/biblioteki/centrum_pamieci.py ]; then
  echo "[hook] CENTRUM PAMIĘCI (W-360 v5):"
  if python -m imperium.biblioteki.centrum_pamieci start; then
    CENTRUM_OK=1
  else
    python -m imperium.biblioteki.pamiec_sesji start || true
  fi
else
  # Fallback: stara warstwa W3 (gdy centrum jeszcze niedostępne)
  if [ -f imperium/biblioteki/pamiec_sesji.py ]; then
    echo "[hook] PAMIĘĆ SESJI (W-360):"
    python -m imperium.biblioteki.pamiec_sesji start || true
  fi
fi

# 4) KRONIKA CZATU (W-360) — destyluj transkrypty do repo (przyrostowo), by CAŁY
#    czat przetrwał kompakcję i wygaśnięcie kontenera chmury (commit niesie historię).
if [ -f imperium/biblioteki/kronika_czatu.py ]; then
  echo "[hook] KRONIKA CZATU (W-360):"
  # Eksport tej sesji (raportuje, co dopisał). Statystyki „X sesji, Y MB" drukuje już
  # `centrum_pamieci start` na ścieżce głównej — osobne `statystyki` dawało trzeci, zdublowany
  # wydruk. Ale gdy centrum PADŁO (CENTRUM_OK=0), statystyk nikt nie wydrukował → dodrukowujemy
  # je TUTAJ, żeby nie zginęły na ścieżce awaryjnej (recenzja cubic PR #118).
  python -m imperium.biblioteki.kronika_czatu eksportuj || true
  [ "$CENTRUM_OK" = "1" ] || python -m imperium.biblioteki.kronika_czatu statystyki || true
fi

# 5) AUTO-LEKCJA (W-360 v5 — Opcja C) — DeepSeek ekstrahuje lekcje/wizje/decyzje
#    z nowych sesji kroniki (przyrostowo, max 3 sesje per start = kontrola kosztów).
#    Silent gdy brak DEEPSEEK_API_KEY (Prawo Bezpieczeństwa: bez klucza nic nie robi).
if [ -f narzedzia/auto_lekcja.py ]; then
  echo "[hook] AUTO-LEKCJA (W-360 v5):"
  python narzedzia/auto_lekcja.py --maks 3 || true
fi

# 6) SKAN WAD KODU — heurystyczny łowca powtórek błędów z recenzji (Księga Wad Kodu).
#    Non-blocking (|| true). Na starcie skanuje OSTATNI COMMIT (A4 — 2026-07-19): skan
#    zmienionych plików był no-op na czystym drzewie („brak plików"). Po SYNC pull łapie
#    regresje w świeżo pociągniętym/zacommitowanym kodzie. Pełny skan zmian → pre-push.
if [ -f narzedzia/skan_wad_kodu.py ]; then
  echo "[hook] SKAN WAD KODU (ostatni commit — Księga Wad Kodu):"
  python narzedzia/skan_wad_kodu.py --ostatni-commit || true
fi
