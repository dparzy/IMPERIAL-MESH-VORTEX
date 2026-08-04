#!/bin/bash
# 🤫 SILENTIUM — cisza nad repozytorium na czas biegu bramki (PreToolUse).
#
# OSOBNY HOOK, NIE DOKLEJKA DO CUSTOS LIMINIS — świadomie. Strażnik Progu broni rozkazów
# STAŁYCH (git push, archiwum); SILENTIUM broni stanu CHWILOWEGO (trwa bieg / nie trwa).
# Zlanie ich w jeden organ dałoby moduł o dwóch niezależnych powodach zmiany, a przy okazji
# jedna awaria uciszałaby obie bariery naraz. Protokół hooka pozwala na wiele wpisów przy
# tym samym matcherze — korzystamy z tego zamiast z dziedziczenia.
#
# Wrapper jest CIENKI Z ROZMYSŁEM: decyzja siedzi w `imperium/pretorianie/silentium.py`,
# który ma testy i kalibrację. Skrypt powłoki bez testów to miejsce, gdzie reguły gniją.
#
# AWARIA STRAŻNIKA NIE BLOKUJE PRACY (kod 1, nie 2), ale nie milczy — stderr idzie do
# transkryptu. Blokada, która przy własnym błędzie zamurowałaby repo, byłaby gorsza od
# ryzyka, przed którym broni.
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 1
exec python -m imperium.pretorianie.silentium hook
