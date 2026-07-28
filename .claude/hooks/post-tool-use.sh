#!/bin/bash
# 🔦 VIGIL — skan świeżo zapisanego pliku .py (PostToolUse).
#
# Cienki wrapper: decyzja i skan w organie `imperium/pretorianie/vigil.py` (z testami).
# Zmierzony koszt: ruff ~0.17 s + skan_wad_kodu ~0.18 s na plik. Cisza gdy zielone.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 1
exec python -m imperium.pretorianie.vigil
