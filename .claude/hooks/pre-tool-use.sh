#!/bin/bash
# 🚧 CUSTOS LIMINIS — bariera PRZED zadziałaniem narzędzia (PreToolUse).
#
# Wrapper jest CIENKI Z ROZMYSŁEM: cała decyzja siedzi w organie `imperium/pretorianie/
# custos_liminis.py`, który ma testy. Skrypt powłoki bez testów jest miejscem, w którym
# reguły cicho gniją — ta sama lekcja co przy siglach (pieczęć woła kroki, nie kopiuje ich).
#
# `jq` NIE JEST DOSTĘPNY na tej maszynie (zmierzone 2026-07-27), więc JSON zdarzenia parsuje
# Python, który jest warunkiem działania całego Imperium.
#
# AWARIA STRAŻNIKA NIE BLOKUJE PRACY: kod 2 blokowałby wywołanie, więc świadomie go NIE
# używamy przy błędzie własnym — twardą barierą jest `permissions.deny` w settings.json,
# a ten hook to szelki do tamtego pasa. Ale awaria też nie milczy (stderr → transkrypt).
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 1
exec python -m imperium.pretorianie.custos_liminis
