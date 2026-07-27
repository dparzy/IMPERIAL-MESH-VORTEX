---
name: ledgery
description: LEDGERY IMPERIUM — CODEX PROBATIONUM (rejestr testów) i LEX TALIONIS / CODEX NOTARUM (noty za błędy i korony za unikaty). Użyj przed zadaniem (czytasz CODEX), po każdym wyniku A/B/IC i przy domykaniu sesji z długiem honorowym.
---

> 🏛️ **Rozkazy stałe Imperium przeniesione z CLAUDE.md** (odchudzanie konstytucji,
> 2026-07-27). Treść jest ŹRÓDŁEM PRAWDY — nie streszczeniem. W konstytucji została
> linia-wyzwalacz z esencją, żeby zachowanie nie cofnęło się, gdy skill nie jest
> wczytany. Zmieniasz rozkaz TUTAJ, nie w kopii.

## 🗂️ ZASADA CODEX PROBATIONUM — REJESTR TESTÓW CZYTANY PRZED KAŻDYM ZADANIEM (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-18)

**CODEX_PROBATIONUM (`narzedzia/codex_probationum.py` → `raporty/CODEX_PROBATIONUM.xlsx`) traktujemy
BARDZO POWAŻNIE.** To dokładny, żywy rejestr testów Imperium — źródło prawdy „co zbadaliśmy, na czym,
z jakim wynikiem, co żywe, co planowane". Źródła: żywy kod (rejestry) + ledger
`bibliotheca_ulpia/dane/rejestr_testow.jsonl` (patrz [[codex-probationum-rejestr-testow]]).

- **CZYTAJ PRZED KAŻDĄ zmianą i zadaniem:** zanim cokolwiek zaczniesz — regeneruj i przeczytaj CODEX
  (`python narzedzia/codex_probationum.py`, potem sprawdź arkusze). Wiedza „co już zrobione / planowane /
  żywe" pochodzi z CODEX, nie z pamięci.
- **AKTUALIZUJ BEZZWŁOCZNIE, ZANIM coś wpiszesz:** jeśli zadanie wymaga aktualizacji, dodania
  elementu/arkusza (sheet) lub rozbudowy o nowy dział — najpierw zaktualizuj CODEX (dopisz wynik do
  `rejestr_testow.jsonl` / rozbuduj generator), DOPIERO POTEM reszta. Każdy nowy wynik testu = natychmiast
  do ledgera.
- **NIEZGODNOŚĆ/BRAK → POPRAW po weryfikacji:** jeśli przy czytaniu CODEX stwierdzisz niespójność z kodem
  albo brak elementu — sprawdź DOKŁADNIE wobec żywego kodu (KANDYDAT ≠ PRAWDA), zweryfikuj i popraw/dodaj.
  Każda liczba/fakt policzone z kodu (Prawo XXI), nie z pamięci.
- **WSZYSTKO ZGODNE Z IMPERIUM:** każdy nowy arkusz/dział/kolumna oraz KAŻDA sugestia rozbudowy musi być
  zgodna z zasadami Imperium (nomenklatura rzymska, ZPO, symbioza, źródło prawdy = kod+ledger). Sugestie
  rozbudowy trzymamy w arkuszu „Sugestie" jako KANDYDATÓW do oceny (nie wpinamy bez weryfikacji).
- **BŁĘDY KODU → NATYCHMIAST Księga Wad:** każdy błąd wykryty w kodzie (przy CODEX lub gdziekolwiek)
  zgłaszasz od razu i zapisujesz do Księgi Wad (`ksiega_wad_kodu`) — klasa semantyczna ZAWSZE, regex po
  pomiarze szumu (patrz [[rozkaz-porzadek-i-ksiega-wad]]).

**Złamanie:** zmiana/zadanie bez uprzedniego przeczytania CODEX; wpisanie czegoś zanim CODEX zaktualizowany;
pozostawienie w CODEX niezgodności z kodem; arkusz/dział niezgodny z Imperium; błąd kodu niezapisany do Księgi Wad.

---

## 📜 ZASADA LEX TALIONIS — OKO ZA OKO: BŁĄD RODZI UNIKAT (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-19)

**Każdy ZATWIERDZONY błąd Architekta rodzi OBOWIĄZEK dostarczenia ZATWIERDZONEGO unikatu** —
dług honorowy spłacany dopiero kompensującym pomysłem/mechanizmem zgodnym z zasadami.

**ZAKRES = CAŁE IMPERIUM (rozkaz Cezara 2026-07-19):** organ aktywują **wszelkiego rodzaju błędy —
DOKUMENTY i KOD — w całym Imperium**, nie tylko README. Prostujesz KAŻDY błąd (nie jeden plik), a każdy
zatwierdzony błąd rodzi unikat (fix + UODPORNIENIE klasy — spina się z ZASADĄ CENSORA). Przy wyborze,
co prostować najpierw, **wesprzyj się subagentem** (ZASADA OSZCZĘDNOŚCI: zwiad/sweep taniej, osąd Opus),
by wybrać najlepsze aktualne priorytety i opcje. To nie
kara osobista przez sesje — to **mechanizm** (jak ustalono: „winny=Claude, kara nie przez sesje,
mechanizm tak"). Cel: **silnik antykruchości** — Imperium nie tylko liczy pomyłki, ale **rośnie
z nich**, bo każda pomyłka jest zobowiązana urodzić przewagę. Parcie na wygraną; łup (zysk
z orderów) → kapitał → lepszy budulec Imperium (sprzęt).

**Organ:** `imperium/biblioteki/codex_notarum.py` — **CODEX NOTARUM** (Księga Not Cenzorskich),
append-only ledger `bibliotheca_ulpia/dane/codex_notarum.jsonl` (źródło prawdy, nie pamięć):
- **NOTA CENSORIA (−)** — zatwierdzony błąd (jak nota infamii rzymskiego cenzora); spina się z Księgą Wad.
- **CORONA (+)** — zatwierdzony oryginalny unikat zgodny z zasadami; `splaca=<id_noty>` zamyka dług honorowy.

**Reguły:**
- **Nic bez ZATWIERDZENIA** (KANDYDAT≠PRAWDA, Prawo I): puste `zatwierdzenie` = błąd. Dowód = pomiar / recenzja / decyzja Cezara.
- **Oko za oko musi mieć oko:** CORONA spłacająca musi wskazywać realną, istniejącą notę.
- **Sesja nie domyka się z niespłaconym długiem honorowym** — `codex_notarum.raport()` (zero-tokenowo) pokazuje stan; dług = zadanie (ZASADA CENSORA), nie tapeta. Dopisane do CHECKLISTY KONIEC SESJI.

**Złamanie:** zatwierdzony błąd bez kompensującego unikatu; nota/laur bez zatwierdzenia; domknięcie sesji z niespłaconym długiem honorowym.
