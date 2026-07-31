---
name: clausura
description: SIGILLUM CLAUSURA — domknięcie wachty Imperium. Użyj na koniec każdej sesji oraz gdy Cezar pisze „zamknięcie", „koniec sesji", „domykamy", „kończymy". Rozwija pełną checklistę zamknięcia (bramka Prawa XXI, CODEX PROBATIONUM, recenzja adversarialna, symbioza dokumentów, Prawo XV, dług honorowy LEX TALIONIS, Dziennik Nieśmiertelny, commit lokalny, blok push dla Cezara, alarmy hooka).
---

# 🔏 SIGILLUM CLAUSURA — domknięcie wachty

Ta pieczęć **nie zawiera kroków** — pobiera je z KONSTYTUCJI (`CLAUDE.md § KONIEC
SESJI`) w chwili wywołania, więc nigdy nie rozjedzie się z rozkazem.

## Wykonanie

1. Uruchom pieczęć i **przeczytaj wydrukowane kroki**:

```bash
python -m imperium.biblioteki.sigillarium clausura
```

2. **Wykonaj każdy krok po kolei.** Krok 1 i 3 (bramka + skan wad) możesz odpalić
   jednym haslem: `/limes`.
3. `🚨 PIECZĘĆ PUSTA` w wydruku = alarm o zniknięciu sekcji w CLAUDE.md, nie „brak zadań".
4. **Blok push kroku 8 GENERUJESZ, nie przepisujesz z pamięci** — pamięć zawiodła raz
   i kosztowała TALARA (nota `N-b74ce133`):

```bash
python -m imperium.pretorianie.exactor --blok-push
```

5. **Zanim wyślesz meldunek domykający — przepuść go przez EXACTORA.** Zapisz szkic
   meldunku do pliku i sprawdź go wobec ŻYWEJ checklisty; kod wyjścia ≠ 0 znaczy, że
   meldunek nie spłaca rozkazu, a nie że rozkazu nie było:

```bash
python -m imperium.pretorianie.exactor --plik <szkic_meldunku.md> --domkniecie --bramka
```

## Twarde granice tej procedury

- **Claude NIGDY nie pushuje** (rozkaz 2026-07-11). Kończysz na commicie lokalnym i
  meldunku „gotowe, można push" + pełnym bloku PowerShell dla Cezara.
- **Sesja nie domyka się z niespłaconym długiem honorowym** (LEX TALIONIS):
  `python -m imperium.biblioteki.codex_notarum bilans` musi pokazać 0.
- Wpis do Dziennika Nieśmiertelnego idzie **przed** ostatnim commitem, nie po.
