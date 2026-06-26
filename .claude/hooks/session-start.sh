#!/bin/bash
# 🏛️ IMPERIAL MESH VORTEX — SessionStart hook
# Instaluje zależności żywego systemu w świeżym kontenerze (Claude Code na webie),
# potem uruchamia audyt spójności (Prawo XXI) jako KROK 0.
#
# Testy działają bez zależności (Prawo I), ale pełna moc Imperium (Brama TA-Lib,
# numpy, dashboard, AI) wymaga pakietów z requirements.txt.
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

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

# 3) CENTRUM PAMIĘCI (W-360 v3) — scored TOP-k lekcji (Generative Agents: recency×importance×relevance)
#    + profil Cezara + alarm przepełnienia + cross-layer search. Zastępuje proste "ostatnie 3".
if [ -f imperium/biblioteki/centrum_pamieci.py ]; then
  echo "[hook] CENTRUM PAMIĘCI (W-360 v3):"
  python -m imperium.biblioteki.centrum_pamieci start || \
    python -m imperium.biblioteki.pamiec_sesji start || true
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
  python -m imperium.biblioteki.kronika_czatu eksportuj || true
  python -m imperium.biblioteki.kronika_czatu statystyki || true
fi

# 5) AUTO-LEKCJA (W-360 v4 — Opcja C) — DeepSeek ekstrahuje lekcje/wizje/decyzje
#    z nowych sesji kroniki (przyrostowo, max 3 sesje per start = kontrola kosztów).
#    Silent gdy brak DEEPSEEK_API_KEY (Prawo Bezpieczeństwa: bez klucza nic nie robi).
if [ -f narzedzia/auto_lekcja.py ]; then
  echo "[hook] AUTO-LEKCJA (W-360 v4):"
  python narzedzia/auto_lekcja.py --maks 3 || true
fi
