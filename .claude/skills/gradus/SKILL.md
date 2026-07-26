---
name: gradus
description: GRADUS OPERIS — dobór modelu i stopnia wysiłku do zadania oraz próg opłacalności subagenta. Użyj, zanim zdecydujesz, czy zadanie robisz sam, na jakim stopniu, i czy warto wysłać zwiadowcę. Zawiera pełną tabelę zadanie→model, stopnie VELES–DICTATOR i zasadę eskalacji przy zaskoczeniu.
---

> 🏛️ **Rozkazy stałe Imperium przeniesione z CLAUDE.md** (odchudzanie konstytucji,
> 2026-07-27). Treść jest ŹRÓDŁEM PRAWDY — nie streszczeniem. W konstytucji została
> linia-wyzwalacz z esencją, żeby zachowanie nie cofnęło się, gdy skill nie jest
> wczytany. Zmieniasz rozkaz TUTAJ, nie w kopii.

## 💰 ZASADA OSZCZĘDNOŚCI TOKENÓW — MODEL WG TRUDNOŚCI (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-14)

**Nie każde zadanie wymaga Opusa.** Dobieraj model/effort do trudności i ryzyka — ciężkie/kierunkowe
zostaje na Opusie, mechaniczne/rutynowe schodzi taniej. Dwie dźwignie: (a) Cezar przełącza model
sesji (`/model`), (b) Agent tool z `model: sonnet|haiku` dla delegowalnych bloków.

**ZASADA ESKALACJI (twardy warunek, nie tylko sugestia):** tańszy model/niski effort działa TYLKO
dopóki wynik jest oczekiwany. Gdy wynik jest ZASKAKUJĄCY — zero transakcji tam gdzie spodziewano się
ruchu, błąd, wyjątek, rozbieżność z założeniem — **eskaluj do Opus/wyższy effort NATYCHMIAST**, nie
brnij dalej na tanim modelu zgadując. Dowód z sesji 2026-07-14: dwa krytyczne bugi (`'1H'`→ccxt
NotSupported blokujący całą pętlę live; brak `__main__` w `petla_live.py`) ujawniły się właśnie
podczas „rutynowych" testów paper — złapanie ich wymagało czytania kodu źródłowego i budowania
hipotezy, czego niski-effort/tańszy model by nie zrobił rzetelnie.

### Tabela: zadanie → model/effort (obowiązkowa, rozszerzaj o nowe wzorce)

| Zadanie | Model/effort | Uzasadnienie |
|---|---|---|
| **Testy paper/live — RUTYNOWY bieg** (uruchom, odczytaj wynik, zrelacjonuj) | Sonnet 5, effort **low** | mechaniczne: fetch danych, wywołanie funkcji, formatowanie |
| **Testy paper/live — DIAGNOZA anomalii** (0 transakcji, błąd, nieoczekiwany wynik) | **Opus** (eskalacja) | wymaga czytania kodu, hipotezy, naprawy — 2× złapane bugi krytyczne |
| Uruchamianie testów/audytu/ruff (exec + odczyt exit code) | Haiku lub Sonnet low | mechaniczne, brak osądu |
| Pisanie commitów/LOG_ZMIAN wg wzorca | Sonnet low | szablonowe, niska stawka błędu |
| Web-research / weryfikacja faktów w internecie | Sonnet 5 (subagent) | dobre z narzędziami web, tańsze niż Opus |
| Recenzja niezależna „drugie oko" (np. web-recenzja plonu Hyginusa) | Sonnet 5 (subagent, osobny kontekst) | wartość w niezależności, nie w głębi Opusa |
| Pisanie kodu wg gotowej, precyzyjnej specyfikacji | Sonnet (medium/high effort) | wykonanie, nie projektowanie |
| Projektowanie architektury / nowego modułu / API | **Opus** | decyzje kompozycyjne, konsekwencje długoterminowe |
| Debugowanie realnego bugu (nieznana przyczyna) | **Opus** | wymaga hipotezy + dowodu z runtime (zasada debugowania) |
| Osąd/sędzia kandydatów (np. plon Hyginusa, PLON_*.md) | **Opus** | ważenie dowodów, Prawo XVI/I, konsekwencje wpięcia |
| Nazewnictwo/doktryna/ZASADY w CLAUDE.md | **Opus** | rozkazy stałe, tożsamość Imperium, trwałe skutki |
| Decyzje kierunkowe/nieodwracalne (Prawo XVIII) | **Opus** + pytanie Cezara | z definicji poza automatyzacją |
| Mechaniczne mapowania/liczenie/formatowanie dużych list | Haiku | zero osądu, czysta transformacja |

**How to apply:** przy większym zadaniu — jedno zdanie: jaki tier i dlaczego, zanim ruszysz. Nie
spawnuj subagenta do drobiazgu (koszt zimnego startu przewyższa oszczędność). Tabelę rozszerzaj, gdy
pojawi się nowy powtarzalny wzorzec zadania — wpis w tym samym commicie co pierwsze użycie.
**„Opus" w tabeli = skrót na NAJWYŻSZY dostępny tier** — REGUŁA, nie nazwa. Nazwa modelu
zaszyta na sztywno starzeje się jak każda ręczna liczba (klasa wady: MANUAL podawał
nieistniejący „sonnet-4-6", złapane 2026-07-17), więc tier czytamy z tego, co Cezar
faktycznie ustawił (`/model`), nie z tego, co pamiętamy.

### 🏦 GRADUS OPERIS — stopnie wysiłku (organ: `imperium/cesarz/aerarium.py`)

**Model to jedna dźwignia, stopień wysiłku (`effort`) to druga — i tańsza.** Źródło prawdy
tabeli jest w kodzie (`aerarium.GRADUS`), test parytetu pilnuje zgodności z tym dokumentem.

| Stopień | Imię (funkcja) | Kiedy | Trwałość |
|---|---|---|---|
| `low` | **VELES** — lekka piechota bez zbroi | mechaniczne, zero osądu: uruchom testy, regeneruj CODEX, licz pliki | trwały |
| `medium` | **MILES** — szeregowy legionista | rutyna wg wzorca: commity, LOG_ZMIAN, naprawa liczb, wpisy do ledgerów | trwały |
| `high` | **CENTURIO** — dowódca centurii | **domyślny Opusa 5**: implementacja wg spec, recenzja, raporty | trwały |
| `xhigh` | **TRIBUNUS** — decyzje operacyjne legionu | trudne: debug realnego buga, projekt organu, osąd kandydatów, A/B | trwały |
| `max` | **DICTATOR** — władza nadzwyczajna, wygasała z czasem | nieodwracalne: konstytucja, kierunek, kapitał | **tylko ta sesja** |
| `ultrathink` (słowo w prompcie) | **AUSPICIUM** — wróżba przed czynem | jedna tura głębiej bez podnoszenia wachty | jedna tura |
| `ultracode` (ustawienie CC) | **PRAEFECTUS FABRUM** — oficer od robót | xhigh + orkiestracja workflow, wiele frontów | **tylko ta sesja** |

**ZASADA DOBORU:** stopień podnosisz za **KONSEKWENCJE, nie za rozmiar**. Duże ale mechaniczne
= VELES. Małe ale nieodwracalne = DICTATOR. Zaskoczenie na niskim stopniu = eskalacja
natychmiast (ta sama reguła co dla modeli, wyżej).

**OBALONE (INDEX FALSORUM, 2026-07-26):** „think", „think hard", „think more" **NIE są
słowami kluczowymi** — idą do modelu jako zwykły tekst promptu. W dół schodzi się `/effort`,
nie zaklęciem. Jedyne działające słowo to `ultrathink`.

**Skille i subagenci mogą mieć własny `effort` we frontmatterze** — mechaniczna bramka biegnie
taniej, osąd drożej, bez ręcznego przełączania przez Cezara.

**Stan modeli na 2026-07-26 (decyzja Cezara):** model główny Imperium to **OPUS 5**
(`claude-opus-5`) — wg rankingów zdecydowanie mocniejszy od poprzednika. **Opus 4.8
przechodzi na emeryturę.** Wcześniej rolę najwyższego tieru pełniły kolejno Opus 4.8
i Fable 5 — ta lista JEST datowana i z założenia się zestarzeje; wiążąca jest reguła
powyżej, a nie ten akapit.

**ARCHITEKT NIE MIERZY WŁASNEGO MODELU** (zmierzone 2026-07-21, potwierdzone 07-26):
środowisko hooka nie niesie identyfikatora modelu, więc BREVIARIUM świadomie go nie
zgaduje, a Vitruviusz DEKLARUJE go na otwarciu z konfiguracji sesji. Gdy deklaracja
Architekta rozjedzie się z tym, co ustawił Cezar — **źródłem prawdy jest ustawienie
Cezara**, nie deklaracja (Prawo I: kto nie mierzy, ten nie rozstrzyga).

**Złamanie:** użycie Opusa na czysto mechanicznym zadaniu BEZ powodu, LUB — poważniejsze — pozostanie
na tanim modelu/niskim effort mimo zaskakującego/nieoczekiwanego wyniku zamiast eskalacji.
