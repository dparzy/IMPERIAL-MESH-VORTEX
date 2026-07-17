---
kategoria: DISCIPLINA
typ: zywy
wlasciciel: skrypty/start.py
stan_na: 2026-06-20
powod_istnienia: "Spis skryptów startowych i ich komend — punkt wejścia dla Cezara"
---
# 🚀 Skrypty Startowe Imperium

Gotowe skrypty do uruchomienia. Wszystkie w trybie **paper** (symulacja, zero
prawdziwych pieniędzy). Uruchamiaj z **głównego folderu** projektu.

| Skrypt | Co robi | Komenda |
|---|---|---|
| `start.py` | Najprostsze — paper + panel webowy | `python skrypty/start.py` |
| `start_tv.py` | Paper + odbiornik TradingView | `python skrypty/start_tv.py` |
| `start_uczenie.py` | Paper + pełne uczenie roju | `python skrypty/start_uczenie.py` |

Po uruchomieniu otwórz **http://localhost:8777**. Zatrzymanie: **Ctrl+C**.

Pełna instrukcja krok po kroku: [`docs/MANUAL_UZYTKOWNIKA.md`](../docs/MANUAL_UZYTKOWNIKA.md)

> Zmieniasz pary/interwał/opcje bezpośrednio w pliku skryptu (sekcja USTAWIENIA).
> Pełna lista opcji `KonfigPetliLive` — sekcja 7 manuala.
