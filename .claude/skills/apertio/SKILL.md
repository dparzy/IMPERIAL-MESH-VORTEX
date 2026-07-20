---
name: apertio
description: SIGILLUM APERTIO — otwarcie wachty Imperium. Użyj na starcie każdej sesji oraz gdy Cezar pisze „otwarcie", „start sesji", „zaczynamy", „nowa sesja". Rozwija pełną checklistę otwarcia (wydruk hooka, alarmy jako zadania, SYNC, weryfikacja „czy już istnieje", rozpoznanie terenu, przedstawienie rzymskie, plan).
---

# 🔏 SIGILLUM APERTIO — otwarcie wachty

Ta pieczęć **nie zawiera kroków** — pobiera je z KONSTYTUCJI (`CLAUDE.md § OTWARCIE
SESJI`) w chwili wywołania. Powód: ręcznie skopiowana checklista zgniłaby (dowód:
runbook W11 kazał Claude `git push` pół roku po zakazie). Źródło prawdy jest jedno.

## Wykonanie

1. Uruchom pieczęć i **przeczytaj wydrukowane kroki**:

```bash
python -m imperium.biblioteki.sigillarium apertio
```

2. **Wykonaj każdy krok po kolei** — pominięcie kroku jest złamaniem rozkazu stałego.
3. Jeśli wydruk zawiera `🚨 PIECZĘĆ PUSTA` — to alarm, nie brak zadań: sekcja w
   CLAUDE.md zniknęła lub zmieniła format. Napraw źródło, zanim ruszysz dalej.

## Uwagi

- Wydruk hooka `SessionStart` bywa ucięty w podglądzie (>25 KB) — pełna treść leży
  w `tool-results/hook-*.txt`. Przeczytaj plik, jeśli banner „NASTĘPNY KROK" zniknął.
- Alarm audytu / Prawa XV / Refleksji W9 to **zadanie**, nie tapeta (ZASADA CENSORA):
  rozstrzygnij sam, zaplanuj w Backlogu CODEX albo zapytaj Cezara — nigdy milczeniem.
- Pieczęć siostrzana domykająca wachtę: `/clausura`. Bramka przed commitem: `/limes`.
