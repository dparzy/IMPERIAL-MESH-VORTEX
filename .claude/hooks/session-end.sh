#!/bin/bash
# 🏛️ IMPERIAL MESH VORTEX — SessionEnd hook (auto-commit PAMIĘCI, BEZ pushu)
# Decyzja Cezara 2026-07-04: auto-generowane pliki pamięci przepisują się co sesję
# i rozjeżdżały laptop↔chmurę (blokada `git pull`). Rozwiązanie: na KOŃCU sesji hook
# sam commituje TYLKO pliki pamięci (whitelist) — nigdy kodu (żeby nie wypchnąć
# niedokończonej pracy). Best-effort: nigdy nie blokuje zamknięcia sesji.
#
# ZMIANA 2026-07-10 (decyzja Cezara): hook NIE PUSHUJE.
# Powód: push po każdej sesji produkował dziesiątki commitów „auto: sync pamięci sesji"
# w historii chmury i wymuszał rebase przy każdym starcie na drugiej maszynie.
# Lokalny git JEST repozytorium — commit kosztuje zero. Push to osobna, świadoma decyzja:
#   bash narzedzia/synchronizuj.sh          # podgląd: co czeka na wypchnięcie
#   bash narzedzia/synchronizuj.sh --push   # skleja commity pamięci w jeden i pushuje
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
echo "[hook] Pamięć sesji zacommitowana LOKALNIE (bez pushu — decyzja Cezara 2026-07-10)."

# Ile commitów czeka na wypchnięcie? Informacja, nie akcja.
# Bez upstreamu (nowa gałąź) po prostu milczymy — nie ma z czym porównać.
if git rev-parse --abbrev-ref "@{upstream}" >/dev/null 2>&1; then
  CZEKA="$(git rev-list --count "@{upstream}"..HEAD 2>/dev/null || echo 0)"
  if [ "${CZEKA:-0}" -gt 0 ]; then
    echo "[hook] 📦 Lokalnie czeka na push: $CZEKA commit(ów)."
    echo "       Wypchnięcie: bash narzedzia/synchronizuj.sh --push"
  fi
fi
