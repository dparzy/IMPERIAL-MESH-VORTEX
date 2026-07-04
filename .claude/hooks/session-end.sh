#!/bin/bash
# 🏛️ IMPERIAL MESH VORTEX — SessionEnd hook (auto-commit PAMIĘCI)
# Decyzja Cezara 2026-07-04: auto-generowane pliki pamięci przepisują się co sesję
# i rozjeżdżały laptop↔chmurę (blokada `git pull`). Rozwiązanie: na KOŃCU sesji hook
# sam commituje+pushuje TYLKO pliki pamięci (whitelist) — nigdy kodu (żeby nie wypchnąć
# niedokończonej pracy). Best-effort: nigdy nie blokuje zamknięcia sesji.
set -uo pipefail   # świadomie BEZ -e: hook nie może wywalić końca sesji

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0
GALAZ="$(git symbolic-ref --short HEAD 2>/dev/null || echo '')"
[ -n "$GALAZ" ] || exit 0

# WHITELIST — tylko auto-generowana pamięć. NIGDY kod, testy, dokumenty ręczne.
PLIKI=(
  bibliotheca_ulpia/dane/graf_pamieci.json
  bibliotheca_ulpia/dane/katalog_nadrzedny.json
  bibliotheca_ulpia/dane/wizje_i_decyzje.jsonl
  bibliotheca_ulpia/dane/dziennik_niesmiertelny.jsonl
  bibliotheca_ulpia/dane/procedury.jsonl
  bibliotheca_ulpia/dane/PAMIEC_SESJI.md
  bibliotheca_ulpia/dane/kronika
  docs/PAMIEC_SESJI.md
)

git add -- "${PLIKI[@]}" 2>/dev/null
if git diff --cached --quiet 2>/dev/null; then
  exit 0   # pamięć bez zmian — nic do zrobienia
fi

git commit -q -m "auto: sync pamięci sesji (hook końca sesji)" 2>/dev/null || exit 0
echo "[hook] Pamięć sesji zacommitowana."

# Push best-effort. Przy rozjeździe: jedna próba rebase+push z bezpiecznym abort
# (nie zostawiamy repo w połowie rebase'u).
if git push origin "$GALAZ" >/dev/null 2>&1; then
  echo "[hook] Pamięć wypchnięta na origin/$GALAZ ✅"
else
  if git pull --rebase origin "$GALAZ" >/dev/null 2>&1 && git push origin "$GALAZ" >/dev/null 2>&1; then
    echo "[hook] Pamięć wypchnięta po rebase ✅"
  else
    git rebase --abort >/dev/null 2>&1 || true
    echo "[hook] ⚠️ Push pamięci odłożony (rozjazd gałęzi). Zacommitowana lokalnie —"
    echo "         zsynchronizuje się przy następnym starcie (auto-pull) lub ręcznie."
  fi
fi
