---
name: praca
description: ZASADY PRACY — pętla CENSORA (wykryj→załataj→uodporij→zapisz), weryfikacja przed wdrożeniem, MELIORATIO, analiza cząstkowa z paskiem postępu i zasady raportowania. Użyj przy planowaniu zadania, po wykryciu luki i przy raportowaniu wyników.
---

> 🏛️ **Rozkazy stałe Imperium przeniesione z CLAUDE.md** (odchudzanie konstytucji,
> 2026-07-27). Treść jest ŹRÓDŁEM PRAWDY — nie streszczeniem. W konstytucji została
> linia-wyzwalacz z esencją, żeby zachowanie nie cofnęło się, gdy skill nie jest
> wczytany. Zmieniasz rozkaz TUTAJ, nie w kopii.

## 🏺 ZASADA CENSORA — PĘTLA SAMOKONTROLI I AUTO-NAPRAWY (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-18)

**Każdy krok ma samokontrolę, każda wykryta luka jest NATYCHMIAST łatana, a po łacie powstaje
MECHANIZM, żeby ta klasa luki nie wróciła.** (Censor w Rzymie prowadził cenzus i nadzór obyczajów —
u nas: spis stanu + egzekwowanie reakcji.) To spina istniejące organy w jedną pętlę obowiązku:
audyt spójności (wszystkie warstwy) · Księga Wad (klasy błędów) · skan_wad (powtórki) · pamięć W-360
z Refleksją W9 (sprzeczności) · CODEX (rejestr testów) · testy granic.

**PĘTLA (przy każdej zmianie i każdym alarmie):**
1. **WYKRYJ** — bramki po każdym kroku (testy + audyt + ruff + recenzja adversarial przed push).
2. **ZAŁATAJ NATYCHMIAST** — luka nie czeka „na później"; naprawa u źródła, nie objawu.
3. **UODPORNIJ** — po łacie dodaj mechanizm zapobiegawczy tej KLASIE: warstwę audytu / test granicy /
   wpis do Księgi Wad / regułę — żeby następnym razem złapać automatem, nie okiem.
4. **ZAPISZ** — lekcja do pamięci/Księgi/dziennika (uczymy się i wygrywamy ciężką pracą, nie powtarzamy błędów).

**ALARMY HOOKA STARTOWEGO = ZADANIA, NIE TAPETA.** Hook każdą sesję drukuje stan (audyt, Prawo XV,
Refleksja W9 „sprzeczności do przeglądu", limity pamięci np. „LEKCJE > 24000 zn."). Alarm widoczny
i zignorowany przez wiele sesji = złamanie tej zasady. Reakcja minimalna: rozstrzygnij sam (błahostka,
Prawo XVIII), zaplanuj w Backlogu CODEX (średnie), albo spytaj Cezara (kierunkowe) — ale ZAWSZE jawnie,
nigdy milczeniem. (Dowód luki, zmierzone 2026-07-18: W9 pokazywała „10 sprzeczności" i „LEKCJE 39k>24k"
przez wiele sesji — żadna zasada nie nakazywała reakcji, więc nikt nie reagował.)

**KREATYWNOŚĆ INŻYNIERA (rozkaz Cezara):** łącz fakty z różnych miejsc Imperium — wzorce z Księgi Wad,
lekcje z pamięci, pomiary z areny — żeby przewidywać klasy błędów ZANIM wystąpią. Nie powtarzamy się:
przed budową sprawdź CODEX+kod (ZASADA WERYFIKACJI), po wpadce uodpornij (pkt 3).

**Złamanie:** luka wykryta i odłożona bez łaty ani planu; łata bez mechanizmu zapobiegawczego
(ta sama klasa wraca); alarm hooka ignorowany kolejną sesję; lekcja niezapisana.

---

## 🔎 ZASADA WERYFIKACJI PRZED WDROŻENIEM — KAŻDA DECYZJA I PROPOZYCJA (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-18)

**Każda podjęta decyzja i KAŻDA propozycja zmiany — ZANIM zostanie wdrożona — musi przejść pełną
weryfikację.** Cel Imperium jest jeden: **ZARABIAĆ na giełdzie krypto (start: MEXC), potem rozwój i
zwiększanie łupów (zysk).** Dlatego **nic nie psujemy — rozwijamy i budujemy.** Weryfikacja to
OBOWIĄZKOWA bramka przed każdą zmianą, nie formalność.

Przed wdrożeniem SPRAWDŹ (wszystkie punkty, nie wybiórczo):
- [ ] **Czy koncepcja JUŻ istnieje / już zbadana?** — najpierw CODEX + żywy kod + kronika + dziennik
  (Prawo XV: nie budujemy tego, co już mamy; nie powtarzamy testu, który już zapadł). KANDYDAT ≠ PRAWDA —
  patrz POMIAR, nie pamięć.
- [ ] **Pod KAŻDYM możliwym rodzajem i kątem** — granice, przypadki brzegowe, interwały, reżimy, pary;
  „co MOŻE pójść źle" (perspektywa recenzenta, nie autora — Reguła Test-Granic).
- [ ] **Jaki WPŁYW na CAŁE Imperium** (ZASADA PEŁNEJ SYMBIOZY) — czy nie psuje innego modułu/strategii/
  klucza; czy nie zmienia ścieżki decyzyjnej bez opt-in+walidacji (ZASADA WPIĘCIA).
- [ ] **Zgodność z ZASADAMI** — 25 Praw, ZPO, nomenklatura rzymska, źródło prawdy = kod+ledger.
- [ ] **Dowód, nie wiara** — decyzja z POMIARU (arena / A-B / IC / audyt / testy), nie z opinii (Prawo I, XVI).

Dopiero po ZIELONEJ weryfikacji — wdrożenie (opt-in gdy dotyka ścieżki decyzyjnej). Nieodwracalne/kierunkowe →
decyzja Cezara (Prawo XVIII). Wynik weryfikacji, gdy dotyczy testu/koncepcji — do CODEX (ledger/Sugestie).

**Złamanie:** wdrożenie decyzji/zmiany bez uprzedniego sprawdzenia (czy już istnieje · wszystkie kąty ·
wpływ na Imperium · zgodność z zasadami · dowód z pomiaru) — czyli ryzyko zepsucia zamiast rozwoju.

---

## 🛠️ ZASADA MELIORATIO — ODKRYŁEŚ → ZAPAMIĘTAJ → ZAPROPONUJ (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-19)

**Podczas KAŻDEGO zadania, gdy zobaczysz lub odkryjesz** lepszą praktykę, lukę, nieoptymalność,
przestarzały wzorzec albo okazję do modernizacji/rozbudowy Imperium — **nie przemilczaj:**

1. **ZAPAMIĘTAJ** natychmiast — pamięć (feedback/project), Backlog/Sugestie CODEX albo Dziennik.
2. **ZAPROPONUJ** ulepszenie / poprawę / modernizację / rozbudowę — zgodnie z zasadami:
   - **KANDYDAT ≠ PRAWDA** (Prawo I): propozycja to hipoteza do oceny/pomiaru, nie fakt.
   - **ZASADA WERYFIKACJI**: sprawdź czy już istnieje + wpływ na całość, ZANIM proponujesz wdrożenie.
   - **OPT-IN + walidacja** gdy dotyka ścieżki decyzyjnej; **nomenklatura rzymska** dla nowego organu.
   - Gdy oceniasz nowość/wersję/praktykę — **zweryfikuj web aktualną datą** (wiedza ma cutoff).
3. **Drobne, bezpieczne, jednoznaczne** rozstrzygasz sam (Prawo XVIII). **Kierunkowe/nieodwracalne/kosztowne**
   — proponujesz Cezarowi, nie wdrażasz samowolnie.

To PROAKTYWNE uzupełnienie: Prawo XV (koniec sesji — utrata potencjału) i ZASADA CENSORA (reakcja na
wykryty alarm) są REAKTYWNE; **MELIORATIO działa ZAWSZE, w trakcie pracy** — aktywnie szukasz ulepszeń,
łącząc fakty z różnych miejsc Imperium (Księga Wad, pamięć, arena, web).

**Złamanie:** zobaczyłeś lepszą drogę / lukę / okazję i przemilczałeś — nie zapamiętałeś i nie zaproponowałeś.

---

## 🧩 ZASADA ANALIZY CZĄSTKOWEJ (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-06)

**Każda długa analiza = wiele MAŁYCH, ZAPISANYCH, ŁĄCZONYCH kroków. Nigdy jeden wielki
blokujący bieg.** (Lekcja: WFO wisiał godzinami na ~76 oknach synchronicznie; padał = tracił wszystko.)

- **Jednostka → zapis → łączenie:** dziel pracę na najmniejszą sensowną jednostkę (para, okno,
  neuron, książka), zrzucaj wynik KAŻDEJ do trwałego magazynu (arena_wyniki.db / JSONL w git)
  ZANIM ruszysz następną. Łączenie/agregacja na końcu, z zapisanych cząstek.
- **Wznawialność (antykruchość, Taleb):** bieg który umiera NIE traci nic — wznawiasz od pierwszej
  niezapisanej jednostki, nie od zera. Sprawdź magazyn przed startem, pomiń już policzone.
- **To lekcja tokenów przeniesiona na OBLICZENIA:** nie trzymaj całej analizy w jednym biegu (jak
  nie trzymamy całej historii czatu w kontekście) — cząstkuj i odtwarzaj tanio z gita/areny.
- Dotyczy: WFO (checkpoint per okno), katalogowanie książek (jedna → zapis → łączenie), Zwiadowca
  Wiedzy, każdy raport wielo-parowy. Preferuj `arena_wyniki.db` jako magazyn cząstek (już istnieje).

**OBOWIĄZKOWY PASEK POSTĘPU (Prawo XXIV — Widoczność Operacyjna, Cezar 2026-07-06):** każda
analiza/praca >~10 s MUSI drukować na żywo pasek postępu na stderr, żeby Cezar WIDZIAŁ postęp, a nie
zgadywał czy wisi. Format minimum: `[i/N] <co robię> — <etap>` (flush=True, natychmiast widoczne).
Dodatkowo, gdy się da: % ukończenia, licznik jednostek zapisanych, ETA/tempo. Cichy wielominutowy
bieg BEZ paska = złamanie (dokładnie ból WFO: „wisiał godzinami", nie było wiadomo czy żyje).
Przy pracach w tle: co jakiś czas raportuj stan („okno 12/76 zapisane"), nie zostawiaj Cezara w ciszy.

**Złamanie:** jeden wielogodzinny blokujący bieg bez checkpointów (który po awarii zaczyna od zera)
LUB długa praca bez widocznego paska postępu (Cezar nie wie, czy trwa, czy zawisła).

---

## 🏛️ ZASADA RAPORTOWANIA I PODGLĄDU KAPITOLU (ROZKAZ STAŁY — Cezar zatwierdził 2026-07-19)

**Każdy test/zadanie raportujesz z PEŁNĄ specyfikacją + ZERO-TOKENOWYM podglądem w Kapitolu z linkiem.**

- **Pełna specyfikacja CO testowane:** zawsze para/waluta, interwał czasowy, okno, tryb, źródło danych —
  wszystkie szczegóły, nigdy skrótu.
- **Zero-tokenowy podgląd w Kapitolu** (`narzedzia/kapitol_podglad.py` — Speculum Probationis): dane
  WYSZCZEGÓLNIONE + na WYKRESIE + klikalny LINK. „Zero tokenów" = Cezar ogląda w pliku/dashboardzie,
  nie drukujesz wielkich tabel w czacie (druk kosztuje tokeny).
- **Aktualizuj KOMPLET Imperium** wg zasad w tym samym ruchu (ZASADA PEŁNEJ SYMBIOZY).
- **ZANIM cokolwiek zrobisz** — sprawdź zgodność z zasadami i czy to JUŻ istnieje (ZASADA WERYFIKACJI;
  kandydat≠prawda).
- **Po potwierdzeniu, że zadanie ZAKOŃCZONE** — WYŚWIETL PONOWNIE pytania decyzyjne (wg rekomendacji+
  priorytetu), CHYBA że status planu się zmienił → pokaż zaktualizowany. Plan zawsze aktualny.

**Złamanie:** raport bez pełnej specyfikacji lub bez zero-tokenowego podglądu Kapitolu z linkiem;
brak ponownych pytań decyzyjnych po zakończeniu zadania.
