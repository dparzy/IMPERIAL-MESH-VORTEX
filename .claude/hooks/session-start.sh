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

# 3) PAMIĘĆ SESJI (W-360) — mapa podpięć + ostatnie lekcje na starcie KAŻDEJ sesji,
#    by ciągłość nie ginęła w kompakcji kontekstu (problem zgłoszony przez Cezara).
if [ -f imperium/biblioteki/pamiec_sesji.py ]; then
  echo "[hook] PAMIĘĆ SESJI (W-360):"
  python -m imperium.biblioteki.pamiec_sesji start || true
fi
