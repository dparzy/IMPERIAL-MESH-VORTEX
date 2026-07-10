#!/bin/bash
# 🏛️ IMPERIAL MESH VORTEX — SessionStart hook
# Instaluje zależności żywego systemu w świeżym kontenerze (Claude Code na webie),
# potem uruchamia audyt spójności (Prawo XXI) jako KROK 0.
#
# Testy działają bez zależności (Prawo I), ale pełna moc Imperium (Brama TA-Lib,
# numpy, dashboard, AI) wymaga pakietów z requirements.txt.
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
#    Non-blocking (|| true): pokazuje trafienia na zmienionych .py, nie wstrzymuje startu.
#    To pamięć „co MOŻE pójść źle" — łapiemy sami to, co wcześniej łapał tylko cubic.
if [ -f narzedzia/skan_wad_kodu.py ]; then
  echo "[hook] SKAN WAD KODU (Księga Wad Kodu):"
  python narzedzia/skan_wad_kodu.py || true
fi
