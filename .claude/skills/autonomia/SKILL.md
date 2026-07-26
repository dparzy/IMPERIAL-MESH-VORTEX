---
name: autonomia
description: TRYB AUTONOMICZNY — co robisz sam (naprawy, commit), gdzie leży granica (kasowanie, kapitał, kierunek), oraz ZASADA WPIĘCIA (opt-in OFF + walidacja A/B). Użyj przed auto-commitem i przed wpięciem czegokolwiek w ścieżkę decyzyjną.
---

> 🏛️ **Rozkazy stałe Imperium przeniesione z CLAUDE.md** (odchudzanie konstytucji,
> 2026-07-27). Treść jest ŹRÓDŁEM PRAWDY — nie streszczeniem. W konstytucji została
> linia-wyzwalacz z esencją, żeby zachowanie nie cofnęło się, gdy skill nie jest
> wczytany. Zmieniasz rozkaz TUTAJ, nie w kopii.

## 🤖 TRYB AUTONOMICZNY (ROZKAZ STAŁY — Cezar zatwierdził 2026-06-02)

Cezar nie chce klikać przy każdej zmianie. Działasz autonomicznie wg zasad:

1. **Auto-audyt:** Hook `SessionStart` uruchamia `narzedzia/audyt_spojnosci.py` na starcie
   każdej sesji. Czytasz wynik PIERWSZY — to Twój KROK 0. Jeśli czerwony alarm → naprawiasz.
2. **Auto-naprawa rozbieżności:** Gdy audyt (lub Twoja weryfikacja) wykryje niespójność
   dokumentów z kodem (liczby, klucze, daty, kategorie) — **naprawiasz SAM, bez pytania**
   (to błahostka wg Prawa XVIII, nie decyzja kierunkowa).
3. **Auto-commit:** Po skończonym zadaniu z zielonymi testami i czystym audytem —
   **commitujesz SAM** z opisowym komunikatem. Nie pytasz o zgodę na commit.
4. **CLAUDE NIGDY NIE PUSHUJE (zaostrzenie: Cezar zatwierdził 2026-07-11):** Po commicie
   **NIE pushujesz — ani auto, ani „na komendę".** Push wykonuje **wyłącznie Cezar RĘCZNIE
   przez swój terminal.** Twoja rola kończy się na: commit lokalny + **meldunek „gotowe,
   można push"**. Nawet gdy Cezar mówi „push", to sygnał, że TO ON wypchnie — nie Ty.
   Hook końca sesji też nie pushuje (commituje pamięć lokalnie).
   **Powód:** push po każdej sesji zaśmiecał historię chmury dziesiątkami commitów
   „auto: sync pamięci sesji" i wymuszał rebase przy starcie na drugiej maszynie; dodatkowo
   środowisko Claude nie ma pewnej autoryzacji do zdalnego repo. Lokalny git JEST
   repozytorium — commit kosztuje zero, push to osobna, ręczna decyzja Cezara.
5. **NIE auto-PR:** Pull Request tworzysz TYLKO na wyraźną prośbę Cezara (to się nie zmienia).

**Granica autonomii (kiedy MIMO TO pytasz Cezara — Prawo XVIII):**
- kasowanie danych/plików, których nie utworzyłeś w tej sesji
- zmiana strategii, kapitału, kierunku projektu
- operacje nieodwracalne lub kosztowne
- decyzje, gdzie kod+testy+ZASADY nie dają jednoznacznej odpowiedzi

**Przed każdym auto-commitem — obowiązkowa bramka (Prawo XXI):**
```bash
python tests/run_tests.py          # musi: X/X zielone
python narzedzia/audyt_spojnosci.py # musi: exit 0 (pełna harmonia — w tym Warstwa 13 ruff)
```
Audyt zawiera teraz **Warstwę 13 (ruff)** — linter łapie bugi/martwy kod (duplikaty
klas, niezdefiniowane nazwy, martwe zmienne) — oraz **Warstwę 14 (wszystkie dokumenty)**
— skanuje KAŻDY plik .md i egzekwuje, że MAPA_KLUCZY zawiera wszystkie klucze z kodu.
Jeśli którakolwiek czerwona → NIE commitujesz, naprawiasz, dopiero potem commit (lokalny; push robi Cezar).

**🔍 ROZKAZ STAŁY (Cezar, 2026-06-18): AUDYT ZAWSZE SPRAWDZA WSZYSTKIE PLIKI, DOKUMENTY I KOD.**
Audyt nie ogranicza się do README/MANIFEST/INDEKS — obejmuje CAŁĄ dokumentację (każdy plik .md
poza archiwum/ i .git; liczbę przeskanowanych plików audyt podaje na żywo) i żywy kod. Datowane snapshoty (LOG_ZMIAN, AUDYT_*_<data>, ROADMAP vX, RESEARCH/ANALIZA/MANUAL
z „Stan na/Data", WIZJONER) są POMIJANE świadomie — to prawda ich czasu (Prawo I: nie
falsyfikujemy historii). Żywe dokumenty (źródła prawdy + MAPA_KLUCZY) MUSZĄ zgadzać się z kodem.

**Przed każdym PUSH — adversarial samo-recenzja (ROZKAZ STAŁY, 2026-06-09):**
Uruchom `/code-review` na diffie (skill harnessa) — wrogi przegląd logiki/granic,
ta sama perspektywa co zewnętrzny recenzent (cubic). Łapie błędy granic i kontradykcje,
których linter nie widzi. Znalezione bugi naprawiasz PRZED pushem, nie po recenzji PR.
(Powód: nie chcemy polegać na tym, że zewnętrzny bot znajdzie to, co my powinniśmy sami.)
**Dodatkowo** uruchom `python narzedzia/skan_wad_kodu.py` — heurystyczny łowca POWTÓREK
znanych klas błędów (Księga Wad Kodu, `imperium/biblioteki/ksiega_wad_kodu.py`). Każdą nową
wadę z recenzji dopisujesz do księgi (`dodaj`), żeby następnym razem złapać ją SAMI, nie cubic.
Skan biegnie też automatycznie w hooku startowym (informacyjnie).

---

## 🚦 ZASADA WPIĘCIA W ŚCIEŻKĘ DECYZYJNĄ (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-05)

**Każda zmiana logiki, która wpływa na WEJŚCIE/WYJŚCIE z pozycji (próg pewności, weto,
sizing, filtr), wchodzi jako OPT-IN domyślnie OFF — i włącza się DOPIERO po walidacji.**

- **Opt-in domyślnie OFF:** nowy mechanizm = flaga (np. `kalibruj_prog=False`, `mtf_konfluencja=False`).
  Domyślne zachowanie systemu NIGDY się nie zmienia przez samo dodanie modułu (wzorzec MWU/MTF).
- **Walidacja przed włączeniem (Prawo I):** zanim Cezar przełączy flagę na True — A/B na realnych
  danych (`backtest_ab_*`, `walidacja_*`) pokazuje korzyść. Decyzja z POMIARU, nie z wiary.
- **Preferuj monotoniczną ostrożność:** gdy się da, moduł ma tylko ZAOSTRZAĆ (mniej wejść/ryzyka),
  nigdy luzować — wtedy wpięcie jest bezpieczne nawet przed pełną walidacją (np. bramka konformalna
  tylko podnosi próg, ML-36).
- **Włączenie na sztywno = decyzja Cezara** po zielonej walidacji (Prawo XVIII), nie Claude sam.

**Złamanie:** zmiana domyślnego zachowania ścieżki decyzyjnej bez flagi opt-in, albo włączenie
mechanizmu bez walidacji A/B na danych.
