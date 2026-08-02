#!/bin/bash
# ⚖️ VINDEX — czy komenda powłoki złamała kontrakt któregoś ledgera (PostToolUse: Bash).
#
# Dlaczego OSOBNY hook, a nie rozszerzenie VIGILA: VIGIL skanuje plik wskazany przez
# `tool_input.file_path`, a komenda powłoki takiego pola nie ma. Tworzy za to pliki
# i zmienia dane — czyli dokładnie to, czego dotąd NIKT nie oglądał (zmierzone 2026-08-02:
# matcher VIGILA to Write|Edit|NotebookEdit, więc `python skrypt.py > plik` był niewidzialny).
#
# ZASIĘG WĄSKI Z ROZMYSŁU (--tylko-kontrakty): hook bada WYŁĄCZNIE kontrakty ledgerów,
# których odzywalność zmierzono na 2,0% (5 z 254 commitów). Obce pliki NIE wchodzą do
# automatu — plik roboczy jest nieśledzony od chwili powstania aż do `git add`, więc
# strażnik krzyczałby na każdy plik, który Architekt właśnie tworzy. To ta sama decyzja,
# co u EXACTORA: w automacie tylko powinność ze zmierzonym zerem fałszywek.
#
# Zmierzony koszt: ~0,36 s na wywołanie. Cisza gdy zielone.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 1
exec python -m imperium.pretorianie.vindex --hook
