#!/bin/bash
# 🔄 SYNCHRONIZUJ — świadomy push gałęzi roboczej (decyzja Cezara 2026-07-10).
#
# Hook końca sesji commituje pamięć LOKALNIE i nie pushuje. To narzędzie wypycha,
# sklejając wcześniej commity pamięci w jeden — żeby historia w chmurze nie tonęła
# w dziesiątkach „auto: sync pamięci sesji".
#
#   bash narzedzia/synchronizuj.sh          # PODGLĄD — co czeka, nic nie zmienia
#   bash narzedzia/synchronizuj.sh --push   # skleja commity pamięci i pushuje
#
# ZASADA BEZPIECZEŃSTWA: sklejamy WYŁĄCZNIE gdy każdy commit czekający na push jest
# commitem pamięci. Gdy w kolejce jest choć jeden commit merytoryczny (kod, dokumenty) —
# NIE przepisujemy historii, pushujemy jak jest. Praca Cezara nigdy nie jest przepisywana.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 1
git rev-parse --git-dir >/dev/null 2>&1 || { echo "❌ To nie jest repozytorium git."; exit 1; }

PUSH=0
[ "${1:-}" = "--push" ] && PUSH=1

GALAZ="$(git symbolic-ref --short HEAD 2>/dev/null || echo '')"
[ -n "$GALAZ" ] || { echo "❌ Odłączona HEAD — najpierw wejdź na gałąź."; exit 1; }

# Wzorzec commita pamięci. Musi zgadzać się z komunikatem z .claude/hooks/session-end.sh.
WZOR_PAMIECI='^auto: sync pamięci sesji'

if ! git rev-parse --abbrev-ref '@{upstream}' >/dev/null 2>&1; then
  echo "⚠️  Gałąź '$GALAZ' nie ma upstreamu."
  [ "$PUSH" -eq 1 ] && { echo "→ Ustawiam i pushuję."; git push -u origin "$GALAZ"; exit $?; }
  echo "→ Wypchnięcie: bash narzedzia/synchronizuj.sh --push"
  exit 0
fi

git fetch -q origin "$GALAZ" 2>/dev/null || true

PRZED="$(git rev-list --count 'HEAD..@{upstream}' 2>/dev/null || echo 0)"
CZEKA="$(git rev-list --count '@{upstream}..HEAD' 2>/dev/null || echo 0)"

echo "🔄 Gałąź: $GALAZ"
echo "   Czeka na push: $CZEKA   |   Zdalna wyprzedza o: $PRZED"

if [ "$CZEKA" -eq 0 ]; then
  echo "✅ Nic do wypchnięcia."
  [ "$PRZED" -gt 0 ] && echo "→ Ale zdalna ma $PRZED nowych: git pull --rebase origin $GALAZ"
  exit 0
fi

echo
echo "Commity czekające na push:"
git log --oneline '@{upstream}..HEAD'

# Czy WSZYSTKIE czekające commity to pamięć? (wtedy i tylko wtedy sklejamy)
INNE="$(git log --format='%s' '@{upstream}..HEAD' | grep -cv "$WZOR_PAMIECI" || true)"
if [ "${INNE:-0}" -eq 0 ]; then
  echo
  echo "📦 Wszystkie $CZEKA commit(ów) to pamięć sesji → zostaną sklejone w jeden."
  SKLEJ=1
else
  echo
  echo "🛡️  W kolejce jest $INNE commit(ów) merytorycznych → historii NIE przepisuję."
  SKLEJ=0
fi

if [ "$PUSH" -eq 0 ]; then
  echo
  echo "PODGLĄD — nic nie zmieniono. Wypchnięcie: bash narzedzia/synchronizuj.sh --push"
  exit 0
fi

if [ "$PRZED" -gt 0 ]; then
  echo "❌ Zdalna gałąź wyprzedza o $PRZED commit(ów). Najpierw:"
  echo "     git pull --rebase origin $GALAZ"
  exit 1
fi

if [ "$SKLEJ" -eq 1 ] && [ "$CZEKA" -gt 1 ]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "❌ Drzewo robocze nie jest czyste — sklejanie wymaga czystego stanu."
    echo "   Zacommituj albo 'git stash', potem powtórz."
    exit 1
  fi
  # `git log` idzie od najnowszego — najstarszy commit zakresu to OSTATNIA linia (tail -1).
  OD="$(git log --format=%ad --date=short '@{upstream}..HEAD' | tail -1)"
  DO="$(git log -1 --format=%ad --date=short HEAD)"
  ZAKRES="$OD"; [ "$OD" != "$DO" ] && ZAKRES="$OD..$DO"
  echo "→ Sklejam $CZEKA commitów pamięci w jeden ($ZAKRES)."
  git reset --soft '@{upstream}' || { echo "❌ reset nieudany"; exit 1; }
  git commit -q -m "auto: sync pamięci sesji ($ZAKRES, $CZEKA sesji)" || {
    echo "❌ commit nieudany — historia NIE została wypchnięta"; exit 1; }
fi

echo "→ Push na origin/$GALAZ"
git push origin "$GALAZ" || { echo "❌ Push nieudany."; exit 1; }
echo "✅ Wypchnięte."
