---
kategoria: CONSILIUM
typ: zywy
wlasciciel: —
bez_wlasciciela: "plan calego Imperium — zamiar, nie opis istniejacego organu"
stan_na: 2026-08-06
powod_istnienia: "Mapa dróg rozwoju systemu w 5 fazach (0-4), od pierwszego cyklu paper trading do pełnej autonomii."
---
# 🏛️ ROADMAP IMPERIUM — MAPA DRÓG SYSTEMU

**Dokument:** Plan rozwoju systemu IMPERIUM — AI crypto trading z motywem Cesarstwa Rzymskiego
**Aktualna faza:** FAZA 1 — Namiestnik (Regime + Timeframe-Aware Gating)
**Data:** 2026-06-12
**Wersja:** v0.9.1

---

## 🗓️ PLAN WACHT — operacyjna kolejka zadań (przegląd 2026-08-06)

> **Czym to jest, a czym nie:** FAZY 0–4 niżej to mapa STRATEGICZNA (dokąd zmierzamy).
> Ta sekcja to kolejka OPERACYJNA — co robimy w najbliższych wachtach, w kolejności.
> Każda pozycja ma **stan zmierzony**, nie deklarowany, i przechodzi **CURSUS PLENUS**
> (zadanie → testy → checklista → działa na żywych danych → kalibracja → ocena →
> zwiad → pomiary → symbioza). Pozycja bez kalibracji przyrządu **nie jest skończona**.

**Legenda stanu:** ✅ zrobione · 🟡 kod jest, brak dowodu · 🔴 nie istnieje · ⏸️ świadomie odłożone

> ⚠️ **Ta sekcja przez trzy dni była NAGŁÓWKIEM BEZ KOLEJKI** — obiecywała „co robimy
> w najbliższych wachtach", a kolejka leżała rozsypana po ośmiu sekcjach niżej (H, G, A,
> F, B, C, Ł, E). Uporządkowane 2026-08-05 na rozkaz Cezara.

### 👑 SUCCESSIO — DOKTRYNA NADRZĘDNA (ROZKAZ KIERUNKOWY Cezara 2026-08-07)

> *„działaj tak, aby przygotowywać się na powolne stopniowe przekazywanie pałeczki lokalnemu
> LLM, dbając o dobrą kondycję i działający kod i cały system (…) dawaj z siebie wszystko
> i ostrożnie buduj nasze imperium"*

**To nie jest odległa wizja, tylko KRYTERIUM OCENY KAŻDEJ POZYCJI NIŻEJ.** Cel: orkiestrator
oparty na TIRO. Zmierzone ograniczenia, w których musi się zmieścić: sprzęt PEDES unosi
1–3 mld parametrów szybko (Q4) albo 7–8 mld wsadowo; TIRO ma **254 użyteczne pary z progu
1000**. Model tej klasy **nie zastąpi rozumowania** — więc jedyna droga to **zmniejszać liczbę
rzeczy wymagających sądu**, nie czekać na większy model.

| # | Reguła | Konsekwencja inżynierska |
|---|---|---|
| 1 | **Determinizm bije sąd** | reguła z kodem wyjścia = jedna rzecz mniej dla orkiestratora (dowód: HARNESS 4/4, NEURO-SYM 4/4) |
| 2 | **Każdy organ ma WOŁACZA i kontrakt** | mały model nie odgadnie, kiedy coś wywołać; wołacz-widmo = przyszła ślepa plama |
| 3 | **Liczby zamiast intuicji** | każdy próg z kalibracją i testem granicy (LEX TALARUS) |
| 4 | **Zapisuj DLACZEGO, nie tylko CO** | docstringi z dowodem to materiał, z którego TIRO uczy się domeny |
| 5 | **Kondycja przed rozbudową** | zielona bramka i zero długu mają pierwszeństwo przed nowym organem |

**GRANICA PRAWNA, NIENARUSZALNA:** TIRO uczy się od **Hyginusa (DeepSeek) i z danych Imperium**,
NIGDY z wyjść Architekta — destylacja modelu Anthropic jest zabroniona przez ToS, niezależnie
od tego, kto uruchamia trening. **Zweryfikowane pomiarem 2026-08-07:** 482 pary nauczyciela
pochodzą w 100 % z DeepSeeka (v4-flash 464, v4-pro 18), **zero z Architekta** — droga jest
czysta i ma taka zostać.

**PYTANIE OTWARTE, do zaplanowania RAZEM z orkiestratorem, nie po nim:** dziś umiemy zmierzyć
„czy organ ma wołacza". Przy orkiestratorze pytanie zabrzmi „czy zawołał we **właściwym
momencie**" — a to wymaga prawdy podstawowej, której nie mamy. Bez tego powtórzymy klasę
„organ orzekający bez kalibracji" (47 organów, 11 bez kalibracji).

---

### 🔄 RAMA POJĘCIOWA — CZTERY PYTANIA O ORGAN I SZEŚĆ PĘTLI

**Powstała 2026-08-07, bo Cezar powiedział wprost: *„już się zagubiłem"*.** To nie ma być
w niczyjej głowie — ma być w kodzie i w tym dokumencie.

**O KAŻDYM organie zadajemy CZTERY pytania, nie jedno:**

| # | Pytanie | Nazwa | Kto dziś na nie odpowiada |
|---|---|---|---|
| 1 | Kto go **uruchamia**? | **wołacz** | od 2026-08-06: `komendy_konstytucji_poza_pieczecia` — ale **tylko dla LIMES** |
| 2 | Co robi i **co zwraca**? | **kontrakt** | nikt systematycznie |
| 3 | Kto sprawdza, że **działa**? | **weryfikator** | testy + LUSTRUM — **ale LUSTRUM liczy regexem, więc myli się** |
| 4 | Gdzie idzie jego **werdykt**? | **odbiorca** | nikt systematycznie |

**TRZY POZIOMY ODPOWIEDZIALNOŚCI:** wykonawcy (265 organów — robią jedno dobrze, nie decydują
kiedy) · strażnicy (audyt, SILENTIUM, VALLUM, VINDEX — **mają prawo zatrzymać**) · **kora
decyzyjna (dziś: wyłącznie Architekt)**. Nikt nie weryfikuje samych strażników — dlatego
LUSTRUM przez miesiąc dawał martwemu organowi ocenę 1.00.

**SZEŚĆ PĘTLI (zmierzone 2026-08-07) — kryterium: czy wyjście wraca na wejście:**

| # | pętla | co wraca | stan |
|---|---|---|---|
| 1 | **sesji** | Dziennik z `/clausura` wstrzykiwany na starcie następnej | ✅ |
| 2 | **bramki** | VALLUM czerwieni → naprawa → push → nowy bieg | ✅ |
| 3 | **długu honorowego** | błąd → nota → korona → bilans blokuje commit | ✅ |
| 4 | **handlowa** (`petla_live`) | pozycja → wynik → stan → następna decyzja | ✅ |
| 5 | **uczenia** (`ucz_mwu`) | werdykt areny → **wagi neuronów** | 🔴 **zbudowana, WYŁĄCZONA — zmierzone, że SZKODZI** (−0,6 pp, PBO ~0,6) |
| 6 | **CENSORA** | wada → łatka → **uodpornienie** → Księga Wad | 🟡 **PRZECIEKA: 79 % klas wad WRACA** |

**Dwie chore pętle to te najważniejsze:** (5) rój **nie uczy się z własnych wyników** — arena
osądza, werdykty nie zmieniają wag; (6) lekcja **nie staje się mechanizmem** — dowód z jednej
doby 2026-08-06/07: **cztery trafienia w tę samą klasę**, mimo że była zapisana jako lekcja.
Pozycja **M2** niżej domyka pętlę 6. Pozycja **5** domyka pętlę 5.

**BRAKUJE SIÓDMEJ — OBIEGU WIEDZY.** Zmierzone 2026-08-07 na ścieżce
`petla_live → dyrygent → rejestr`: `diagnostyka_korelacji` **jest** wołana (2 trafienia), ale
`bibliotekarz`, `quaesitor`, `graf_pamieci`, `schola` mają **ZERO**. Biblioteka rośnie, RAG
indeksuje, Hyginus zbiera — i **nic z tego nie wraca do decyzji**. Zgodne z pomiarem DESCRIPTIO
z 08-05: filar RÓJ nie sięga do filara WIEDZA ani razu.
**Wzorzec, który to zamyka, nazywa się ARCHITEKTURA TABLICOWA (blackboard, HEARSAY-II)** —
specjaliści obserwują wspólny stan i **odzywają się sami**, gdy rozpoznają swoją dziedzinę.
Pokrewne, rozróżnione świadomie: *event-driven* (mamy — w hookach, czyli w procesie, nie
w decyzji), *stigmergia* (ledgery są śladami, ale nikt ich nie czyta przy decyzji),
*ensemble/voting* (**to mamy** — 87 neuronów, MWU, konfluencja).
⚠️ **Warunek wstępny:** kryterium „istotności" nie może powstać z tych samych danych, na
których testujemy — inaczej blackboard staje się maszyną do look-ahead i przeuczenia.

**⚠️ NAZWA MYLĄCA — do rozstrzygnięcia:** nasze piętro **LOOP** w MATURITAS mierzy *domykanie
zobowiązań* (ROADMAP 14,3 %, sugestie, wizje bez werdyktu), a branżowe *loop engineering*
znaczy *pętlę wykonawczą agenta* (obserwuj → działaj → sprawdź → popraw). Dwie różne rzeczy
pod jedną nazwą. Przy budowie orkiestratora to może kosztować — TIRO odczyta nazwę
po branżowemu. Albo doprecyzować nazwę, albo zapisać różnicę w organie.

---

### 🎯 KOLEJKA NA TERAZ (rekomendacja Architekta, kolejność = priorytet)

| # | zadanie | stan | dlaczego TERAZ |
|---|---|---|---|
| **W1** ✅ | **ZROBIONE 2026-08-07.** Wszystkie pięć naprawione, każda z testem regresji (+9 testów). **POMIAR SPRZED NAPRAWY UJAWNIŁ, ŻE P1 JEST SZERSZE, NIŻ ZGŁOSIŁA RECENZJA:** ten sam ślepy punkt siedział także w `ocen_pokrycie`, czyli w **ŚCIEŻCE BRAMKOWEJ** — szkic recenzji (PENDING) na HEADzie dawał `status=pokryte, exit 0`, więc ROZPOCZĘCIE pisania recenzji zwalniało `/limes` mocniej niż jej ZŁOŻENIE. Naprawione w obu miejscach + „nieporównywalny znacznik czasu" (ta sama klasa na sąsiednim wejściu). Miara główna (`miara_glowna`) jest teraz DANĄ, którą czyta nagłówek raportu. **PRZY OKAZJI ZŁAPANE I ZAMKNIĘTE MECHANIZMEM:** `KsiegaWadKodu.dodaj*()` mutowało tylko pamięć — mój zapis 5 klas NIE trafił na dysk, wykryty wyłącznie przez policzenie rekordów Z DYSKU. Ta pułapka jest opisana od 2026-07-20 i ugryzła **trzeci raz**, więc dostała autozapis (`utrwal=True`) + 2 testy, nie czwartą lekcję. Księga: 170 → 175 wpisów (5 nowych klas semantycznych). **Oryginalny opis wad:** &nbsp; **P1:** `recognitor.py:298` — `_sekundy(...) or 0` zamienia BRAK daty złożenia recenzji w 0 s, więc recenzja PENDING przy PR zmergowanym w 10 s liczy się jako **złożona NA CZAS** (zmierzone wywołaniem: `odsetek_na_czas = 100%` dla PR, którego nikt nie przejrzał). **P2:** `recognitor.py:279` docstring podaje 13/141 (9,2 %), kod zwraca 10/141 (7,1 %) · `sigillarium.py:78` `sekcja_komend` bez `kroki_komend` = **cichy nadzór**. **P3:** `historia --bramka` kończy exit 0 przed obsługą flagi · dwie miary procentowe obok siebie, łagodniejsza brzmi jak główna | ✅ | **ROZKAZ CEZARA 2026-08-06: „zapamiętaj te błędy po code review, będziemy od nich zaczynać nową sesję".** P1 to **dokładnie ta klasa, którą organ ma zwalczać** — brak danych udający sukces — popełniona w organie od jej wykrywania. Przy P2 rozważyć **rozszerzenie Warstwy 23 na docstringi `.py`**, inaczej naprawimy instancję, nie klasę |
| **W2** ⭐ | **ZDJĄĆ BIAŁĄ LISTĘ Z NADZORU KOMEND** — `sigillarium.komendy_konstytucji_poza_pieczecia()` działa **tylko dla LIMES**; APERTIO i CLAUSURA mają puste `sekcja_komend`, więc funkcja zwraca `[]` natychmiast. Zmierzone: **8 z 13 komend konstytucji nie ma egzekutora** — w tym `maturitas` (krok 5b otwarcia, ROZKAZ STAŁY), `descriptio --bramka`, `breviarium --delta`, `dziennik_niesmiertelny wpis` | 🔴 | **To naprawa MOJEJ WŁASNEJ wachty z 08-06, która powtórzyła klasę zapisaną w pamięci jako lekcja:** *„bramka o wąskim zasięgu = fałszywy spokój"* (W11 pilnowała 1 katalogu z 11). **Potwierdzone pomiarem: `maturitas` występuje 0 razy w hooku startowym**, a descriptio/breviarium/codex mają tam 7 trafień — uruchomiłem go ręcznie i gdybym zapomniał, nikt by nie zauważył. **Koszt: godziny** — to zdjęcie białej listy z działającej funkcji, nie nowy organ |
| **W3** | **DESCRIPTIO — przestać gubić moduł w sumie filara.** `sieroty_filara()` (moduły filara z zerem wołaczy) + twardy warunek w `bledy()`: **strażnik filara musi mieć WOŁACZA**, nie tylko istnieć (dziś `.exists()`) + przepiąć `wspolpraca()` z regexu na **AST** (dziś liczy też `import json`) | 🔴 | Zmierzone zwiadem AST 2026-08-07: **3 z 13 strażników filarów ma ZERO wołaczy** — `quaesitor` (WIEDZA), `meta_kora` (DECYZJA), `nexus_hub` (EGZEKUCJA, filar „zero realnych orderów"). Filar RÓJ pokazuje „wołany 82" i wygląda zdrowo, mając w środku 5 organów z zerem: **dane są zbierane per moduł i tracone przy sumowaniu**. Bramkowo tylko dla filarów `imperium/` — `narzedzia/` to warsztat CLI, gdzie brak wołacza jest normą (51 przypadków) |
| **W4** | **NAPRAWIĆ `lustrum.sygnaly()` — liczy wołaczy REGEXEM, nie AST-em** (`re.compile(rf"\b{nazwa}\b")`), więc proza w cudzym docstringu liczy się jako wywołanie produkcyjne warte 0.40 | 🔴 | **RECOGNITOR — kanoniczny wołacz-widmo — dostał od LUSTRUM pożytek 1.00 i werdykt ZOSTAW.** Do tego sam próg (CLI 0.20 + docs 0.15 + ledger 0.15 = 0.45 > 0.40) sprawia, że organ opisany i otestowany **nigdy nie zejdzie poniżej progu**, choćby nikt go nie wołał. Póki tak jest, **każdy raport pożytku jest zawyżony** (zmierzone: 2, 3, 1, 2 fałszywych wołaczy na czterech organach). To nie nowy organ — jedna funkcja |
| **0** | **DOMKNĄĆ BRAMKĘ DO 7/7** — `conditor_lustri` ma świecić zielono **spełnieniem kryteriów**, nie decyzją. Brakuje: TABULARIUM (33 alarmy T2/T3), ETAPY (7 otwartych L0–L3x), **KLASY** (rejestr leków na K1–K4 — nie istnieje), **KALIBRACJA** (rejestr kalibracji organów orzekających — nie istnieje) | 🔴 | **ROZKAZ CEZARA 2026-08-05: „naprawimy to na nowej sesji, aby wszystkie były spełnione".** Zamrożenie zdjęto DECYZJĄ przy czerwonej bramce — dług nie zniknął razem z zakazem |
| **0a** ✅ | **ZROBIONE 2026-08-05 (wachta 0a).** Pięć wad naprawionych, każda z testem granicy „celowo psuję producenta"; **dowód mutacyjny: 8/8 testów czerwienieje z ASERCJI** przy przywróconej wadzie (czerwień z importu nie liczy się jako dowód). Zmierzony skutek naprawy W4 na żywym repo: DANE woła 23→14, RÓJ wołany 93→82 — **11 krawędzi było raportowanych pod złym filarem**. Dołożony lek na KLASĘ: `tests/test_kontrakty_publiczne.py` (skan całego repo + jawna lista 13 plików długu, która ma maleć). **🚨 PRZY OKAZJI ZŁAPANE: zapis 5 klas do Księgi Wad, deklarowany w Dzienniku i w tym wierszu, NIGDY NIE NASTĄPIŁ** (0 wpisów z datą 2026-08-05; ostatni był z 08-03) — dopisane teraz, 159→164, potwierdzone odczytem z dysku. Naprawione (plik:linia sprzed naprawy): `dyrygent.py:344` odcisk przed `wskazniki.update(kontekst_dodatkowy)` · `descriptio.py:158` tautologiczna kontrola kompletności · `pamiec_absolutna.py:216` bump `sekwencja` przy stałym haszu · `descriptio.py:137` mapa `stem→filar` gubiąca kolizje · `conditor_lustri.py:173` import prywatnej `_stan_domkniety` | ✅ | Dwie pierwsze to ta sama ironia: naprawiłem bezpiecznik, który nie mógł się zapalić, i w tej samej wachcie zbudowałem **drugi taki sam** oraz jego **lustrzane odbicie** (zapala się zawsze). Klasa przeżyła naprawę, bo naprawiłem INSTANCJĘ, nie WZORZEC |
| **0b** | **PIĘĆ BRAKUJĄCYCH FILARÓW + dwie wady mapy** — `INSTITUTIO` (uczenie), `FISCUS` (kapitał/ryzyko), `HARNESS` (7 hooków + 9 skilli), `ŚWIADECTWO` (187 plików testów), `FAMILIA` (Hyginus, TIRO). Do tego: DESCRIPTIO musi **deklarować swój zakres** i liczyć to, co poza nim; `scheduler.py` ma **0 wołaczy** | 🔴 | Znalezione w TRZECH przejściach pod różnym kątem — **każde coś dało**, więc nie mam podstaw twierdzić, że czwarte nic by nie dało. Wariant zatwierdzony przez Cezara: przypisania per-moduł + test istnienia pliku |
| **M1** ⭐ | **25. WARSTWA AUDYTU — MARTWY KAPITAŁ** *(fitness function)*. Asercja o właściwości architektury, nie o funkcji: „moduł bez wołacza produkcyjnego I bez pomiaru, starszy niż N dni = CZERWIEŃ". Do tego `vulture` na zmierzone sieroty. **Wchodzi RAZEM z antywskaźnikiem** — inaczej podniesie się dopisaniem pustego pomiaru do ledgera. **🆕 DOSTAŁ SWÓJ POMIAR 2026-08-07** (zwiad AST na rozkaz Cezara — grep dawał fałszywe „ma wołacza" na prozie w docstringach, np. `self.discriminator_weights`, łacina „condere lustrum"; odsiane też dokumenty GENEROWANE, bo wymieniają każdy moduł automatycznie): **82 z 265 (31 %) bez wołacza wykonawczego**, z czego **51 to przyrządy CLI wołane ręcznie = NIE WADA** (odsiew świadomy — LUSTRUM zmierzył 08-04, że jednosygnałowe „brak wołacza" dałoby 100 % fałszywek). **Realnie do oceny: 31**, w tym **5 NIEOSIĄGALNYCH** (bez `__main__` i bez wołacza = 1231 linii: `bary_zdarzeniowe`, `meta_labeling`, `kronikarz_zdarzen`, `neutralizacja`, `filtr_ekonomiczny`) i **3 strażników filarów**. **ŁAŃCUCH WIDMA:** `maturitas` ma jednego wołacza w kodzie — `conditor_lustri`, **który sam jest widmem** | 🔴 | **Najtańszy mechanizm z całego zwiadu (~3 h)**: ta sama forma co 24 istniejące warstwy, zero nowych zależności. Celuje wprost w Prawo XV. **Do rozstrzygnięcia PRZEZ CEZARA, nie przez pomiar:** 7 modułów z **2026-05-31** (dzień pierwszy repo, ozdobne ramki „NexGenHub", „MetaCortex", „OmniSight", „AegisShield") — świadoma decyzja czy zapomniany kod? **68 dni bez wołacza.** Druga warstwa dat to 4 organy z 07-29…08-05, czyli **wzorzec powtarza się co kilka dni, nie jest reliktem** |
| **M2** ⭐ | **KLASA WADY BEZ STRAŻNIKA BLOKUJE COMMIT** — każdy wpis Księgi Wad z ≥2 wystąpieniami musi mieć test odpowiadający na pytanie „czy ta klasa zostałaby DZIŚ złapana automatycznie"; brak → `/limes` blokuje, tak jak dziś blokuje dług honorowy. **To jest brakujący producent kryterium KLASY** w `conditor_lustri` | 🔴 | Celuje w **79% klas wad, które wróciły** (kontrakt 13×, testy 12×, pomiar 12×). Wzór: Google SRE error-budget policy — przekroczenie progu przez JEDNĄ klasę wymusza pozycję P0, nie jest opcją. ~4 h + ciągła dyscyplina |
| **M3** ⭐ | **MUTATOR — organ dowodzący, że test UMIE ZAWIEŚĆ** (mutation testing próbkowany: 1 moduł na wachtę, rotacja, wynik do CODEX). **To jest brakujący producent kryterium KALIBRACJA** — kalibracja strażnika to pytanie „czy wykrywa, gdy psuję producenta" | 🔴 | **Zalążek ISTNIEJE**: dowód mutacyjny wachty 0a (8/8 wad wykrytych z asercji) — ale leży w katalogu tymczasowym, więc **jutro nie istnieje**. Celuje w to, że wady łapie recenzja (64), a nie testy (35). ~3 h + bieg w tle |
| **1** | **BIBLIOTHECA ULPIA — domknięcie biblioteki** (a) 133 księgi poza RAG → zaindeksować, (b) **świeży bieg `aestimator.py`** — ile realnie ginie z tabel, wzorów i wykresów i w których pozycjach, (c) watchdog przyrostu ksiąg (dziś **żadna z 24 warstw audytu nie pilnuje ksiąg**) | 🔴 | **ROZKAZ CEZARA 2026-08-05: „najpierw musimy mieć najlepszą Bibliotekę Ulpia — nazwa zobowiązuje".** *Bibliotheca Ulpia* Trajana była największą biblioteką cesarstwa. Dopóki 133 z 248 ksiąg jest niewidzialnych, każdy zwiad czerpie z połowy zasobu |
| **1b** | **Organy mają czytać LINKI, WYKRESY, TABELE i ZŁOŻONE WZORY** — dziś każda ścieżka ekstrakcji (`_pdf` PyMuPDF, OCR, epub/mobi/djvu/calibre) daje **płaski tekst**; struktura tabel, wzory i wykresy **nie są odzyskiwane przez ŻADNĄ z nich** | 🔴 | Rozkaz Cezara 08-05: *„aby nic nie ginęło, aby cała wiedza była w 100% zbadana, oceniona, porównana i wybrana"*. **Kolejność: najpierw pomiar AESTIMATOREM, potem wybór technologii** — struktura tabel ≠ wzory ≠ wykresy to trzy różne problemy o trzech różnych kosztach |
| **2** | **LUDUS MAGNUS P1 — IC dla WSZYSTKICH 87 neuronów** (15 par 4h, walk-forward OOS, PBO/DSR od pierwszego biegu, wynik do CODEX) | 🔴 narzędzia istnieją | **Rozkaz Cezara 2026-08-05.** Ledger ma **4 wyniki IC na 87 neuronów** — skill ~95% roju nigdy nie zmierzony. Bez tego P2–P5 nie mają czego ważyć, a MEXC byłby hazardem |
| **3** | **LUDUS MAGNUS P5 — wiarygodność źródeł MIERZONA** | 🔴 | `WIARYGODNOSC_ZRODEL` to 6 liczb wpisanych ręcznie; zgadywanie udające wiarygodność. Domyka też DOKTRYNĘ WIEDZY Cezara |
| **4** | **LUDUS MAGNUS P3 — walidacja 20 strategii** (SZKIC → zmierzone, DSR+PBO) | 🔴 | MANIFEST sam mówi „status SZKIC — nie zwalidowane"; to najbliżej ostatecznej decyzji (U2) |
| **5** | **Domknięcie pętli areny** — `ucz_mwu` stoi na `False`, bo zmierzono, że SZKODZI (−0,6/−0,5 pp, PBO ~0,6) | 🔴 | Arena osądza walki, a **werdykty nie zmieniają wag**. Warunek WSTĘPNY dla EDITOR MUNERIS, nie jego skutek |
| **6** | **EDITOR MUNERIS** — organ układający program igrzysk (wizja Cezara 08-05) | 🔴 | Zasada nienaruszalna: liczba prób jest składnikiem werdyktu (DSR), budżet zamiast przeszukiwania wyczerpującego |
| **7** | **Dwa organy blokujące ODMROŻENIE**: rejestr klas K1–K4 + rejestr kalibracji organów orzekających. **FORMĘ DOSTAŁY 2026-08-05 — to są M2 i M3** (sekcja „ZWIAD ZEWNĘTRZNY" niżej): rejestr klas = „klasa wady z ≥2 wystąpieniami musi mieć test-strażnika", rejestr kalibracji = MUTATOR | 🔴 | Jedyne dwa kryteria `CONDITOR LUSTRI` bez producenta — świecą NIE WIEM i **blokują pozycję 0**. Do 08-05 pozycja była NAZWANA BEZ FORMY: wiedzieliśmy, czego brakuje, nie wiedzieliśmy, jak to zbudować |
| **8** | **A/B dla flagi `weryfikuj_integralnosc`** (D1.1) | 🔴 | Kod stoi opt-in OFF; LEX TALARUS zabrania ogłaszać działanie przed pomiarem |
| **9** | **LUSTRATIO L3c** — strażnik pracy bez śladu w Dzienniku | 🔴 | Deklaracja w CLAUDE.md, implementacja ZERO; złapane na żywym przypadku |
| **M4** | **WYNIK DOJRZAŁOŚCI PER MODUŁ + PRÓG CZASOWY** (0–4 zamiast globalnego %) wzorem OpenSSF Scorecard — liczony z sygnałów repo, bez recenzenta. Moduł poniżej 4/4 dłużej niż N dni → alarm audytu | 🔴 | Po M1–M3, bo bez nich podnosiłby się sam. **Wymaga antywskaźnika** — to jest miernik najłatwiejszy do oszukania z całej piątki. Punkt wyjścia: 24% modułów ma 4/4 |
| **M5** | **EVALS `pass^k` dla organów orzekających** wzorem Anthropica (5–10 przypadków z Księgi Wad jako zadania; `pass@k` = udało się raz, `pass^k` = udaje się KONSEKWENTNIE). Bez modelu-sędziego — tylko code-based, koszt tokenów zero | 🔴 | Naturalne piętro nad M3 i wejście do LUDUS MAGNUS. **Nie teraz** — 6–10 h na pierwsze 10 modułów, a przedtem trzeba mieć M1, żeby eval sam nie stał się 41. sierotą |
| **KM1** ✅ **DOMKNIĘTE 2026-08-06 — `VALLUM` DZIAŁA** (trzeci bieg `31083330629` ZIELONY na 3.10 **i** 3.11 — dopiero to dało prawo do ✅; przez trzy biegi stało 🟡) (decyzja Cezara: „zaczniemy od km1 wg rekomendacji") | **`.github/workflows/ci.yml` + `pyproject.toml`** ISTNIEJĄ. Wał: ruff → audyt (24 warstwy) → `tests/run_tests.py`, macierz Python 3.10 + 3.11, `timeout-minutes: 30`. **Antywskaźnik wykonany — trzy OSOBNE mutacje**, bo jedna wywalająca wszystko dowodzi tylko, że *coś* czerwienieje: `F821` → ruff rc=1; rozjazd wstrzykniętej liczby → audyt rc=1 na W15; `MAX_DRAWDOWN_STOP` 0.30→0.99 → testy rc=1. Każda cofnięta, każda w klonie (żywe repo nietknięte). **PIERWSZY REALNY BIEG 2026-08-06 (`31060020148`): CZERWONY — i to dowód, że wał żyje.** Przeszły: instalacja pełnych zależności, TA-Lib z wheeli, RUFF, **AUDYT (24 warstwy)** — na 3.10 i 3.11. Padła noga TESTÓW: **8 z 3540**, identycznie na obu wersjach (czyli przyczyną NIE jest wersja Pythona, tylko system). **Wszystkie 8 naprawione w tej samej wachcie** — patrz KM1b | 🟡 | **Zwróciło się PRZED pierwszym biegiem CI.** Symulacja na czystym klonie złapała **P0: bramka testów działała wyłącznie na maszynie Cezara** — `pytest.skip()` rzuca `Skipped` z `BaseException`, przelatywał przez każdy `except` runnera i urywał bieg po 2345 liniach; pliki po winowajcy nie biegły wcale. Naprawione KLASOWO (`_POMINIECIA`) + test granicy dowiedziony mutacyjnie. Drugie znalezisko: **`requirements.txt` mówił nieprawdę** — bez TA-Lib pada **138 z 3539** testów i audyt na W12 (Brama Kalkulatora rzuca `RuntimeError`, Prawo I), więc wał instaluje pełne zależności; TA-Lib 0.6.6 ma wheels `manylinux_2_28` cp310/cp311 (sprawdzone na PyPI). ⏳ **CO ZOSTAŁO:** udowodnione, że **komendy** wału czerwienieją — że czerwienieje **workflow na GitHubie**, pokaże dopiero pierwszy bieg po pushu Cezara (Architekt nie pushuje). Do tego czasu: **zmierzony lokalnie, niezweryfikowany zdalnie** (LEX TALARUS) |
| **KM1b** ✅ **ŻNIWO PIERWSZEGO BIEGU VALLUM — 8 testów żyjących tylko na maszynie Cezara** (2026-08-06, **domknięte zielonym biegiem `31083330629`**) | Naprawione wszystkie 8, w trzech różnych klasach. **(A) WADA ORGANU, nie testów — 4× SILENTIUM + kalibracja:** `_w_repo()` obsługiwał ścieżkę POSIX-ową pod Windowsem, ale **nie miał lustra** — ścieżka `C:\…` widziana spod Linuksa nie jest absolutna, więc `Path` doklejał ją do korzenia repo i strażnik **pilnował cudzego katalogu tymczasowego jak własnego**. Dodana `_obca_sciezka_windows()` + test granicy badający OBA systemy przez udawanie `os.name`, z twardą asercją, że pod Windowsem reguła MUSI milczeć (inaczej uznałaby `C:\Projekty\…` za obce i rozbroiła strażnika u Cezara). **(B) 2× `test_calibre_*`:** padały na `faber.wymagaj("ebook-convert")`, choć same udają `subprocess.run` i prawdziwy calibre nie jest im potrzebny — podmieniony FABER zamiast pominięcia, bo pominięcie oddawałoby pokrycie na każdej maszynie bez calibre. **(C) `test_raport_alarmuje_o_skazonej_krytyce`:** przyczyną **NIE był Linux** — test padał też w klonie na Windowsie. `raport()` ma bramkę „brak indeksu RAG = awaria infry" i wraca komunikatem, zanim dojdzie do badanej sekcji; baza `baza_wiedzy.db` jest w `.gitignore`, więc **istnieje wyłącznie na maszynie, która ją zaindeksowała**. Bramka w kodzie SŁUSZNA i zostaje — to test nie deklarował zależności | 🟡 | **MOC DOWODU RÓŻNA — nie zrównuję jej (LEX TALARUS):** (C) odtworzone i zgaszone na realnej porażce w klonie = dowód pełny; (B) dowiedzione symulacją braku narzędzia = mocne; (A) diagnoza + test granicy pod udawanym `os.name` = **niepełne**, bo czy kalibracja wróci z 89,6% na 93,5% pod PRAWDZIWYM Linuksem, pokaże dopiero następny bieg wału. Klasa nadrzędna, trzecia w jednej wachcie: *rzecz uznana za sprawdzoną, bo sprawdzano ją w jedynym miejscu, gdzie ją kiedykolwiek uruchomiono*. **DRUGI BIEG (`31062067510`): 8 → 2** — kalibracja SILENTIUM wróciła ponad próg (hipoteza (A) POTWIERDZONA zdalnie). Dwa ostatnie testy wskazały **lustrzane odbicie tej samej wady**: reguła „ścieżka od `/` to nie nasze drzewo" jest poprawna tylko pod Windowsem, a pod Linuksem uznawała **własne repo za obce** — strażnik nie chronił żadnego pliku podanego ścieżką absolutną. Warunek obwarowany `os.name == "nt"` + test granicy. **Ta sama reguła przenośności była zepsuta w OBIE strony, każda połowa widoczna wyłącznie z drugiego systemu** |
| **KM2** | **WARSTWA PEWNOŚCI per fragment RAG** — `pewność: float` · `status: ALIGNED/UNALIGNED/GENERAL` · `typ: tekst/tabela/wzór/wykres` · `weryfikowalność: cytat/parafraza/wniosek_autora`. Reguła: `pewność < próg` → fragment **nie wchodzi do kontekstu decyzyjnego** | 🔴 | Zmierzone: grep `pewnosc\|confidence` w `imperium/biblioteki/szukaj.py` → **zero trafień**. To jest **Prawo I w kodzie, nie w dokumencie**. ⚠️ **WARUNEK: po A10** — próg odcięcia bez zbioru ewaluacyjnego byłby liczbą wpisaną z palca (LEX TALARUS: przyrząd bez kalibracji nie istnieje). Progi VeNRY (0,55/0,30) są skalibrowane na **angielskich 10-K**, nasz korpus to polskie zapytania o książki metodyczne — **do przeliczenia, nie do skopiowania** |
| **KM3** | **ARENA PRZED MEXC — Bitget/Bybit demo** przez CCXT `set_sandbox_mode(True)` + `productType: "SUSDT-FUTURES"`; kalibracja poślizgu, fill ratio i `PORTITOR` na realnym order booku | 🔴 | **Zweryfikowane w sieci 2026-08-06:** MEXC **ma** Demo Trading na Futures (interfejs, do 50 000 USDT), ale **API nie ma środowiska sandbox** — teza audytu „brak testnet/demo" jest **przesadzona, wniosek operacyjny słuszny**. Wzmacnia rozkaz `LUDUS MAGNUS` (arena przed MEXC) konkretem: droga do pierwszego zamkniętego obiegu **bez ryzyka kapitału**. Warunek: **po LUDUS MAGNUS P1** (bez IC roju byłby to hazard na cudzym sandboxie) |
| **KM4** | **KANDYDACI EKSTRAKCJI STRUKTURALNEJ — wejście do pozycji 1b:** `MinerU` (MIT, tabele jako tabele, wzory jako LaTeX), `Marker`, `Docling` (IBM), `Nougat` (wzory LaTeX z PDF akademickich) | 🔴 | Zadanie **1b jest nasze**, ale **listy kandydatów nie mieliśmy** — audyt wnosi odpowiedź na pytanie *czym*. **Kolejność NIENARUSZONA: najpierw pomiar AESTIMATOREM, ile realnie ginie i w których pozycjach, potem wybór narzędzia.** Nie odwrotnie |
| **KM5** | **POMIAR PAMIĘCI OBSERWACYJNEJ** — czy forma `[data] obserwacja` (Letta / observational memory) bije nasz esej-kronikę. Mierzymy: ile znaków oszczędza przy **zachowaniu odpowiedzi na te same pytania** (zbiór pytań z QUAESITORA) | 🔴 | Celuje w **zmierzony** dług kontekstu: AERARIUM mówi, że DZIENNIK to **76% wydruku hooka**, a `CLAUDE.md` przekracza limit doktrynalny. ⚠️ „10× taniej" to **liczba producenta, nie nasza** — kandydat ≠ prawda. **Bez pomiaru to wiara**, dlatego pozycja brzmi „pomiar", nie „wdrożenie" |
| **KM6** | **HMO Tier-2 — pamięć sesyjna skompresowana** (mamy Tier 1 = kontekst i Tier 3 = dysk/graf; brak warstwy środkowej) | ⏸️ | Odłożone **świadomie, z powodem**: ryzyko, że budujemy organ nad czymś, co harness (`/compact`) już robi. Wraca dopiero, gdy KM5 pokaże, że forma obserwacyjna daje mierzalny zysk |
| **KM7** | **KIMI K3 jako silnik pod Claude Code** — `ANTHROPIC_BASE_URL=https://api.moonshot.ai/anthropic`, model `kimi-k3[1m]` | ⏸️ **DECYZJA CEZARA** | **Fakty zweryfikowane w sieci 2026-08-06:** 2,8 bln parametrów (MoE, 104 mld aktywnych), **1M kontekstu**, $3/$15 za M tokenów, wagi otwarte 27.07.2026, reasoning always-on. **ZA:** 1M kontekstu = całe repo w jednej sesji, nasz dług kontekstu przestaje boleć. **PRZECIW:** wyższy wskaźnik halucynacji (**Prawo I**) · always-on reasoning = płacisz za myślenie przy `grep` (**Prawo XV**). **Rekomendacja Architekta: PO A10** — bez zbioru ewaluacyjnego A/B „K3 vs Claude" da liczbę z zastrzeżeniem większym niż sama liczba (ta sama pułapka co K10 na 30 pytaniach) |
| **SĄD-140** | **Sąd nad recenzją cubic z PR #140** (`wrzutnia/PR 140 cubic.md`, 2267 znaków — dotyczy SILENTIUM, LUSTRUM, VIATORA). Werdykt **per uwaga** wobec żywego kodu; słuszne naprawiać z testem granicy; po osądzie zaktualizować RECOGNITOR, **żeby alarm zgasł zgodnie z prawdą, a nie przez wyciszenie** | 🔴 | ⚠️ **Zadeklarowany 2026-08-05 jako „PIERWSZA POZYCJA następnej wachty", NIE WYKONANY** — Cezar 2026-08-06 skierował wachtę na audyt Kimi K3, a potem wybrał KM1 jako start kolejnej. **Zapisany tutaj, bo do tej pory żył WYŁĄCZNIE w polu „następny krok" Dziennika** — a to pole właśnie zostało nadpisane przez KM1, więc pozycja zniknęłaby bez śladu. Klasa: *„praca bez śladu"* — dokładnie ta, na którą L3c nie ma jeszcze strażnika |
| **KM8** | **BIB: „Adaptive Markets" — Andrew Lo** → dopisać do `PLAN_ROZBUDOWY_BIBLIOTEKI.md` | 🔴 **dostawa Cezara** | Z ośmiu tytułów proponowanych przez audyt **siedem już mamy** (Douglas ×2, Lefevre, Lewis, Ilmanen ×2, McNeil, Narang, Chan ×8 — zmierzone `ls`). Brakuje wyłącznie Lo. `BIB-229 Miller-Page Complex-Adaptive-Systems` to **inna książka**, nie zamiennik |

### 🐎 ZWIAD ZEWNĘTRZNY 2026-08-05 — jak INNI domykają cykl dojrzałości (pytanie Cezara)

> **Pytanie Cezara (2026-08-05):** *„zastanawiam się, skąd te wszystkie błędy i powroty do
> organów — musimy znaleźć przyczyny. Może dlatego, że nie mamy wzorców określających
> postępowanie i brak dopełnienia etapów ewolucji danej kategorii inżynierii AI"* —
> o **całość Imperium**, nie o sam kod.

**POMIAR PRZED ZWIADEM** (bo diagnoza z opinii nie jest diagnozą). Zmierzone na 262 modułach
— nazwa `baza` wyłączona jako niejednoznaczna, ta sama pułapka co wada nr 4 tej wachty:

| co zmierzone | wynik |
|---|---|
| moduły z **pełnym cyklem 4/4** (test · wpięcie · pomiar w CODEX · opis w żywym dokumencie) | **24%** |
| 3/4 · 2/4 · ≤1/4 | 48% · 18% · 9% |
| moduły **bez ani jednego pomiaru** w `rejestr_testow.jsonl` | **72%** ← wąskie gardło |
| moduły bez testów · bez opisu | 17% · 3% |
| **organy bez wołacza produkcyjnego I bez pomiaru** (martwy kapitał, Prawo XV) | **40** |
| klasy wad należące do kategorii, która wystąpiła **>1×** | **79%** (kontrakt 13×, testy 12×, pomiar 12×) |
| kto łapie wady: **recenzja / testy** | **64 / 35** |

> ⚠️ **Te liczby NIE MAJĄ PRODUCENTA W REPO** — policzył je skrypt wachty 0a, leżący
> w katalogu tymczasowym. Dopóki **M1** nie powstanie, są prawdą **swojego dnia**, nie
> liczbą żywą; za tydzień nikt ich nie odtworzy. To jest ta sama klasa co „liczba rosnąca
> sama", tylko od drugiej strony — i dlatego M1 stoi wyżej niż M4, który by je ładnie pokazał.

**WERDYKT ZWIADU (FRUMENTARIUS, Sonnet, 19 wywołań narzędzi):** hipoteza Cezara broni się
**w połowie, i ta druga połowa jest ważniejsza**. Wzorzec ISTNIEJE — CURSUS PLENUS stoi
w konstytucji. Czego nie ma, to **miernika dopełnienia i KONSEKWENCJI ograniczonej czasowo**.
U innych działa nie lepszy opis, tylko konsekwencja wpięta w miernik: Google SRE — przekroczenie
budżetu błędów przez jedną klasę → *production freeze* i obowiązkowe P0; OpenSSF Scorecard —
wynik liczony z sygnałów repo bez recenzenta; Backstage/Cortex — niski wynik rodzi
przypomnienie **z terminem**, nie liczbę w raporcie.

**SPROSTOWANIE ARCHITEKTA DO MELDUNKU ZWIADOWCY (Prawo I — kandydat ≠ prawda):** zwiadowca
napisał, że *„świadomie odcięliśmy miernik od egzekucji"*, powołując się na regułę „MATURITAS
jest LUSTREM, NIE KIEROWNICĄ". **Zatarł różnicę.** Zakaz brzmi: *„nie wolno go wpiąć w ścieżkę
decyzyjną ani w dobór wag"* — a ścieżka decyzyjna jest u nas zdefiniowana jako **wejście/wyjście
z pozycji**. Bramka commita nią NIE JEST. Wpięcie miernika dojrzałości w `/limes` nie łamie
zakazu Goodharta; wpięcie go w wagi neuronów — łamałoby. Realne ryzyko leży gdzie indziej:
próg blokujący commit kusi, żeby podnosić wskaźnik zamiast naprawiać to, co mierzy — dlatego
**każdy z tych mechanizmów wchodzi razem ze swoim antywskaźnikiem**.

**ODKRYCIE, KTÓRE ZMIENIA PRIORYTET:** M2 i M3 to nie jest nowa praca obok planu — to jest
**brakujący producent pozycji 7** (rejestr klas K1–K4 + rejestr kalibracji), która blokuje
**pozycję 0** (bramka 7/7). Pozycja 7 była dotąd NAZWANA BEZ FORMY. Dlatego M1–M3 stoją
w kolejce zaraz po 0b, a nie na końcu.

**CO ZWIAD ODRZUCIŁ (z powodem, nie z gustu):**

| odrzucone | powód |
|---|---|
| Spotify Backstage / Soundcheck, Cortex.io | platformy webowe z backendem — idea scorecardów TAK, produkt NIE (mamy „jeden lokalny skrypt-bramka") |
| DORA Four Keys | mierzy częstość deployów; nie mamy CI/CD ani wielu wdrożeń tygodniowo — zła SKALA, nie zła idea |
| chaos engineering (Chaos Toolkit, AWS FIS) | mierzyłby odporność systemu, który **nie ma jeszcze ani jednego realnego ordera** — odłożyć do zamkniętego obiegu P&L |
| recenzja przez drugiego inżyniera (rdzeń PRR) | wykluczone naszym układem: jeden nietechniczny właściciel + jeden agent. Zastępują ją M1 i M3 |
| Jira/Scrum Definition-of-Done | otoczka nieadekwatna; samą zasadę „checklista weryfikowana automatycznie" już mamy w 24 warstwach |

**CZEGO ZWIAD NIE ZNALAZŁ (uczciwie zapisane — to jest część wyniku):**

- **Zero prior artu dla układu „jeden nietechniczny właściciel + jeden agent AI pisze cały kod".**
  Każde źródło (Google SRE, Cortex, Backstage, postmortem) zakłada ZESPÓŁ z rolami. Nikt nie
  opisuje sytuacji, w której recenzent i autor to ten sam model w innej sesji.
- **Brak benchmarku, z którym porównać nasze 24%** — branża używa poziomów (bronze/silver/gold),
  nie odsetka „ile modułów przeszło WSZYSTKIE etapy". Pytanie „czy 24% to źle" **zostaje bez
  zewnętrznego punktu odniesienia**.
- **Liczby wydajności mutation testingu odrzucone przez samego zwiadowcę** („1200 mutantów/min",
  „benchmark PyCon 2025") — bez wiarygodnego źródła, prawdopodobny artefakt sumaryzatora.
  **Zmierzyć samemu przy M3, nie wierzyć.**
- Brak literatury łączącej **wiek komponentu w chwili wykrycia wady** z jakimkolwiek standardowym
  miernikiem. Nasza obserwacja (10 z 16 policzalnych wad w organie młodszym niż doba, mediana
  0 dni — MAŁA PRÓBA) może być miarą własną. Warta rozwinięcia przy M4.

**ŹRÓDŁA:** [Google SRE — Error Budget Policy](https://sre.google/workbook/error-budget-policy/) ·
[OpenSSF Scorecard](https://scorecard.dev/) ·
[Thoughtworks — fitness functions](https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development) ·
[Anthropic — Demystifying evals for AI agents](https://anthropic.com/engineering/demystifying-evals-for-ai-agents) ·
[mutmut](https://github.com/boxed/mutmut) · [cosmic-ray](https://github.com/sixty-north/cosmic-ray) ·
[vulture](https://github.com/jendrikseipp/vulture) · [Hypothesis](https://hypothesis.readthedocs.io/)

> 🐢 **DELIBERATIO OBOWIĄZUJE KAŻDĄ Z TYCH POZYCJI** (rozkaz Cezara 2026-08-05: *„zawsze musimy
> sprawdzić dokładnie, powoli wszystko przed podjęciem decyzji"*). Przed startem M1–M5 — jak
> przed każdym innym zadaniem — powstaje jawna analiza pięciu punktów: co robimy i czego to
> dotyka · czego NIE WIEMY · czym zmierzymy i co uznamy za sukces · co może pójść źle i jak to
> wykryjemy · czy to już istnieje. **Zapis w ROADMAP nie jest zgodą na budowę** — jest zapisem
> kandydata. Kolejność wyżej to REKOMENDACJA Architekta, nie decyzja.

### 🔎 SĄD NAD AUDYTEM KIMI K3 (`wrzutnia/05.08.2026/`, osądzone 2026-08-06)

> **Materiał:** 7 plików — metaprompt + 4 raporty (156 KB markdown) + 3 obrazy. Autor: „AI Auditor
> (Kimi K3)". **Przeczytane w całości**, każda falsyfikowalna teza zderzona z ŻYWYM KODEM albo
> z SIECIĄ. Rozkaz Cezara: *„nie odrzucamy, tylko analizujemy i dokładnie sprawdzamy"*.

**⚠️ OSTRZEŻENIE METODOLOGICZNE — czytaj przed użyciem czegokolwiek stąd.**
Raport ogólny **sam deklaruje w nagłówku**: *„Treść plików źródłowych Python (.py) niedostępna do
bezpośredniej inspekcji (blokada GitHub raw)"* — i konsekwentnie mapuje repo jako **3 pliki `.py`**
oraz konstytucję **10 zasad**. Metaprompt **tego samego autora, tej samej sesji** mówi o **467
plikach**. Zmierzone: **466**. Ocena **3,75/10** została wystawiona repozytorium, które nie istnieje.

| Wielkość | Audyt ogólny | Metaprompt | **Zmierzone 2026-08-06** |
|---|---|---|---|
| pliki `.py` | 3 | 467 | **466** |
| prawa konstytucji | 10 | 21 | **25** |
| commity | — | 141 | **1054** |

#### ⚠️ WERDYKT „ZASADY NIE BLOKUJĄ" — PROCEDURALNIE NIEWAŻNY, NIE FAŁSZYWY

Trzy dokumenty (metaprompt §2.2, STRATEGICZNY §7, KOMPLEKSOWY §12) wydają ten sam werdykt na
podstawie tabeli **21 praw**. Mamy **25**. Zgodne treścią: **I** (zero halucynacji), **VII**
(stopniowo), **XIX** (kod+testy), **XX** (status elitarny) — **4 z 25, trafność ~16%**.
Rozjechane m.in.: ich **XV** „nie płacisz za organ" ≠ nasze **CZERWONY ALARM UTRATY POTENCJAŁU**;
ich **XXI** „neuro-symboliczna weryfikacja" ≠ nasz **PROTOKÓŁ SPÓJNOŚCI**. **Nieobecne
całkowicie: XXII, XXIII, XXIV, XXV.** Egzaminowano inną konstytucję → **werdykt nie został
wydany**, nie „został wydany błędnie". Dług otwarty: przejść pytanie na naszych 25 prawach.

#### ✅ POTWIERDZONE POMIAREM — przyjęte (→ KM1–KM8)

> ⚠️ **Kolumna „skąd" celowo BEZ znaczników stanu** (`✅ 🔴 🟡 ⏸️`). Pierwsza wersja tej tabeli
> ich użyła i **zafałszowała piętro LOOP MATURITASA o 4 pozycje otwarte i 2 domknięte** —
> `maturitas.stan_domkniety()` liczy pozycje ROADMAP po tych emoji w KAŻDEJ tabeli, także
> dowodowej. Złapane pomiarem w tej samej wachcie (86→98 zamiast 86→94). Klasa: **zapis
> o pracy poruszył miernik pracy**. Producent pozycji to wyłącznie tabela KOLEJKI.

| Teza audytu | Dowód | Skąd |
|---|---|---|
| Brak CI/CD (`.github/workflows`) | katalogu **nie ma** | **NOWE — jedyne w pełni** → KM1 |
| Brak `pyproject.toml` | potwierdzone | NOWE → KM1 |
| `scheduler.py` — zero wołaczy produkcyjnych | grep importów → **pusto** | nasze (0b) |
| Graf nieczytany przy decyzji | nasz MATURITAS: `kto_przy_decyzji: NIKT` | nasze |
| 133 księgi poza RAG · K10 nieznane | nasz pomiar | nasze (poz. 1) |
| Brak warstwy pewności per fragment RAG | grep w `szukaj.py` → **zero** | częściowo nowe → KM2 |
| MEXC: API bez sandboxu | sieć 2026-08-06 | zewnętrzne → KM3 |
| Kimi K3: 2,8 bln / 1M / $3/$15 / wagi 27.07 | sieć 2026-08-06 | zewnętrzne → KM7 |
| Kimi K3 działa w Claude Code (`ANTHROPIC_BASE_URL`) | sieć — **potwierdzone**, choć w dokumencie stoi na **pustym cytacie** (`article🛠web_search:16#9`, l. 328 STRATEGICZNEGO) | zewnętrzne → KM7 |

#### ❌ OBALONE POMIAREM — do INDEX FALSORUM

| Twierdzenie audytu | Stan faktyczny |
|---|---|
| „**SENAT** nie istnieje" | `imperium/senat/` — `debata_senatu.py`, `meta_kora.py` |
| „**TRYBUNAŁ** (audyt) nie istnieje" | 24 warstwy audytu + 19 pretorianów |
| „**SKARBIEC** (persystencja) nie istnieje" | `pamiec_absolutna.py`, `arena_baza.py`, ledgery JSONL, `baza_wiedzy.db` — **funkcja jest, brakuje tylko nazwy** |
| „Brak `requirements.txt`" | **plik istnieje** |
| „Imperium ma 21 praw" | **25** |
| „P0: zbudować MCP Server dla Imperium (~3 h)" | **mamy DWA** — `.mcp.json`: `biblioteka` + `arena` |
| „Brak headless / automatyzacji bez GUI" | **5 typów hooków działa**: PreToolUse, PostToolUse, SessionStart, SessionEnd, Stop |
| Patenty `US 11,847,xxx` · `CN 115xxxxxx` · `EP 3xxx xxx` | **numery-zaślepki** — nieweryfikowalne, nie wolno cytować jako faktu |

#### 🚫 ODRZUCONE — z powodem

| Odrzucone | Powód |
|---|---|
| **Ocena 3,75/10 + plan 30 dni + plan 12 tygodni** | Wystawione repo liczącemu **3 pliki `.py`** zamiast 466. Wszystko, co z tej oceny wynika, dziedziczy wadę |
| **VIA APPIA** (message bus) — jedyna trafiona teza o brakującym organie | Nasza architektura to **synchroniczny pipeline w jednym procesie**, nie system rozproszony. Rozwiązywałby problem, którego nie mamy |
| **„Tolerancja immunologiczna"** (podnoś próg po serii strat) | **JUŻ MAMY:** `backtest.py:132` — *„ML-36 Bramka konformalna — podnosi próg pewności po serii strat"* |
| **„Quorum threshold per reżim"** | **JUŻ MAMY:** `progi_adaptacyjne.py`, `progi_rsi(rezim, atr_pct)`, `prog_adx(rezim, atr_pct)`, `UstawieniaRezimu` |
| **Reranking / RRF jako nowość** | **JUŻ W ROADMAP** jako A8, z adnotacją „potwierdzone niezależnie z zewnątrz" |
| **A15, A10, A1b, A13, A14, F1, F2 jako rekomendacje audytu** | To **NASZE pozycje** — cytowane z naszymi datami, naszymi liczbami i naszym zdaniem *„leksyka jest sędzią, wektor wnioskodawcą"*. Ocena „5,5/10" biblioteki to ocena **naszej własnej samooceny** |
| **„Ekologiczna redundancja"** (≥2 implementacje każdej krytycznej funkcji) | ⚠️ **KOLIDUJE z Prawem XVI**: odrzucamy za *skorelowany sygnał bez nowej informacji*, **mierzymy** — nie dublujemy na zapas |
| **Mapowanie VSM (Stafford Beer, 5 systemów)** | Mamy **DESCRIPTIO z 11 filarami**, wpięte w apertio/clausura. Druga taksonomia bez pomiaru = Prawo XVI |
| **7 z 8 proponowanych książek** | Zmierzone `ls`: Douglas ×2, Lefevre, Lewis, Ilmanen ×2, McNeil, Narang, Chan ×8 — **już w zbiorze**. Zostaje tylko Lo → KM8 |

#### 🎭 TRZY OBRAZY — ilustracje, ZERO wartości dowodowej

| Obraz | Werdykt |
|---|---|
| `1000101472.jpg` — dashboard „87 neuronów na XAUUSD" | Seria **syntetyczna**: 1180→2400 w 10 świecach, RSI to idealna sinusoida, symetryczne piki MACD na obu krawędziach. Instrument = **złoto**; handlujemy krypto. Nie mówi nic o naszych neuronach |
| `1000101474.jpg` — schemat decyzyjny | Zawiera **filtr godzin 09:00–17:00 UTC** = sesja akcji; krypto handluje się **24/7**. Klasy (Momentum 15 / Trend 12 / … / ML 4) **sumują się do 87**, ale nasza taksonomia jest **literowa: 15 kategorii A–Z** — fabrykacja trafiająca w sumę |
| `1000101475.jpg` — gap analysis | **Falsyfikowalny z naszego środowiska:** „Parallel Agents 1/10", „Multi-Agent 1/10", „CLI Scripting 1/10", „Background Run 2/10" — istnieje narzędzie `Agent` (9 typów subagentów), `run_in_background`, Bash+PowerShell, `CronCreate`, 5 typów hooków, 2 serwery MCP. Oceny „0–10" **bez rubryki**. Trafione: **CI/CD** |

**Bilans:** ze 156 KB materiału **jedna pozycja w pełni nowa i wysokiej wartości** (CI/CD → KM1),
dwie wnoszą konkret do rzeczy już zaplanowanych (KM3, KM4), jedna to zweryfikowany fakt do
decyzji Cezara (KM7). Reszta to **nasze własne odbicie albo tezy obalone pomiarem**.
**To jest drugi z rzędu „audyt zewnętrzny", który okazał się echem** (pierwszy: DeepSeek 07-30) —
klasa do zapamiętania: *materiał opisujący nas naszymi liczbami nie jest niezależnym pomiarem*.

---

### 📌 Co zostało po wachcie 2026-08-05 (stan zmierzony, nie deklarowany)

**Zrobione tej wachty:** U1 `CONDITOR LUSTRI` ✅ · D1.1 `hash_ok` ✅ (opt-in OFF) · K1
w MATURITASIE ✅ · dwie wady bramek (W6, W20) ✅ · LUDUS MAGNUS i EDITOR MUNERIS zapisane ·
kolizja numeracji `D` → `Ł` naprawiona · cztery przeterminowane liczby w tym dokumencie
zastąpione **wskazaniem producenta** (klasa „liczba rosnąca sama").

**Otwarte pozycje wg sekcji (policzone z tabel niżej, nie z pamięci):**

| sekcja | otwarte | uwaga |
|---|---|---|
| WACHTA F — adopcje i alarmy | **17** | największa kolejka; wymaga przesiania wg wagi |
| WACHTA A — biblioteka | **12** | tu leży 133 księgi poza RAG (doktryna wiedzy) |
| WACHTA H — domykanie pętli | **7** | |
| LUSTRATIO L0–L3x | **7** | L4 zależy od kryteriów bramki wyjścia |
| WACHTA G — dług recenzji | **6** | |
| WACHTA C — kolejka Cezara | **5** | |
| WACHTA Ł — łup | **5** | czeka na wynik LUDUS MAGNUS |
| WACHTA E — dług techniczny | **4** | |
| KORONY B/C/D | **3** | ⏸️ zamrożone do L4 |
| WACHTA B — dług kalibracyjny | **3** | zasila kryterium KALIBRACJA bramki wyjścia — **realizuje to M3** |
| MECHANIZMY M1–M5 (zwiad 08-05) | **5** | dopisane 2026-08-05; M2+M3 to producent pozycji 7 |
| ADOPCJE KM1–KM8 (sąd nad Kimi K3) | **8** | dopisane 2026-08-06; z tego **1 w pełni nowa** (KM1 CI/CD), 2 odłożone świadomie (KM6, KM7) |

> **Uczciwa uwaga o tej liczbie (rosnącej po dopisaniu M1–M5):** rośnie, bo mierzymy więcej, niż zamykamy —
> i **spadek wskaźnika domknięcia po dopisaniu uczciwie nazwanego zadania jest ZDROWY**
> (MATURITAS, antywskaźnik piętra LOOP). Wskaźnika **nie wpisujemy tutaj ręcznie**: liczy go
> `python -m imperium.oczy.maturitas`.

---

## 📕 REJESTR DŁUGÓW — czego NIE USTALONO i NIE NAPRAWIONO (rozkaz Cezara 2026-08-04)

> **Po co ta sekcja:** długi Imperium leżały rozsypane po ROADMAP, Księdze Wad, CODEX
> i Dzienniku — widoczne pojedynczo, niewidoczne razem. Cezar zażądał **jednej listy
> uporządkowanej wg ważności**. Kolejność jest REKOMENDACJĄ Architekta, nie alfabetem.
> Każda pozycja ma **datę powstania długu** — bo dług, który nie starzeje się na widoku,
> nie jest długiem, tylko notatką.
>
> **Rozróżnienie, które trzyma tę listę w ryzach:** *nie ustalono* = brak POMIARU (nie
> wiemy, jak jest); *nie naprawiono* = wiemy dokładnie, co jest złe, i kod stoi nietknięty.
> Mieszanie tych dwóch rzeczy jest tym, co pozwalało im obu wisieć.

### 🔴 D1 — kod łamie spisane prawo (NAJWYŻSZY priorytet)

| poz. | dług | zmierzone | od |
|---|---|---|---|
| **D1.1** ✅ | **SPŁACONE 2026-08-05** (19 dni długu). `policz_hash`/`zweryfikuj` + wypełnianie pola w `zapisz()`; w Dyrygencie literał zastąpiony `_integralnosc_wskaznikow()` — **opt-in OFF**, więc przy wyłączonej fladze ani jedna decyzja się nie zmienia. Dwie granice „braku dowodu" pilnowane testami: rekord bez hasza → `False`, weryfikacja bez odcisku → BRUDNE. **Czeka na A/B przed włączeniem.** Opis wady poniżej zostaje jako historia: ~~**Bramka integralności, która zawsze przepuszcza.** `dyrygent.py:961` podaje Hermesowi `hash_ok=True` **na sztywno**, a pole `hash_sha256` ma **ZERO przypisań** w całej bazie kodu. Prawo IX wymienia je jako OBOWIĄZKOWE → **kod łamie własne prawo**. Naprawa zmienia ścieżkę decyzyjną (Hermes zacznie oznaczać dane jako BRUDNE), więc wchodzi **opt-in OFF** — i wymaga **decyzji Cezara** ~~ | naprawione i otestowane 2026-08-05 | **2026-07-17** → spłacone po 19 dniach |

### 🔴 D2 — mechanizm zadeklarowany, implementacja zerowa

| poz. | dług | zmierzone | od |
|---|---|---|---|
| **D2.1** | **Strażnik pracy bez śladu** (= L3c). CLAUDE.md deklaruje „brak wpisu z dziś = czerwony alarm", grep po hookach/audycie/Dzienniku daje **ZERO** implementacji. Złapane na żywym przypadku: wachta wykonała pełną pracę, wpis nie powstał wcale, **żaden organ nie zauważył** | 2026-08-04 | 2026-06-28 (deklaracja) |
| **D2.2** | **Klasa „cytat dosłowny KODU"** (= L3d). Dokument bywa wierny nie nazwie, lecz kodowi — żadne świadectwo oparte na symbolach tego nie widzi | 2026-08-04 | 2026-08-04 |

### 🟡 D3 — niewiadome blokujące inne prace

| poz. | niewiadoma | co blokuje | od |
|---|---|---|---|
| **D3.1** | **K10 — trafność RAG NIEZNANA.** QUAESITOR pobiegł raz, dał naprawę u źródła (recall@5 16,7 % → 80,0 % na ścieżce MCP), ale zbiór 30 pytań to **0,22 %** zawołań z indeksów | A6 (przepięcie na REDDITORA), prawo do słowa „najlepsza" w NORMIE, A14 (wektory) | 2026-07-30 |
| **D3.2** | **Czy graf W8 pomaga przy DECYZJI.** `czytelnicy_przy_decyzji: 0`, `kto_przy_decyzji: NIKT` — 234 węzły i 1680 krawędzi karmią pamięć, nie wybór | całe piętro GRAPH stoi na 3/4; bez zbioru A10 nie ma na czym zrobić A/B | 2026-08-02 |
| **D3.3** | **Precyzja bramki T3 DUBLET** (= L3e). T3 grupuje po `(kategoria, wlasciciel)` — pyta „czy dwa dokumenty wskazują ten sam plik", nie o podobieństwo treści | 10 werdyktów `dublet_rozstrzygniety`, świadomie niewpisanych (klasa K3) | 2026-08-04 |
| **D3.4** | **LUSTRUM: 24 pozycje klasy ZBADAĆ** nigdy nie zweryfikowane pojedynczo; prawdę podstawową klasy WPIĄĆ ustalił **sam autor klasyfikatora** | wiarygodność wycofywania narzędzi | 2026-08-04 |
| **D3.5** | **Narzut MCP niezmierzony** (MCP odroczone) | decyzja o soczewkach | 2026-07-15 |

### 🔴 D4 — zapłacone i niewykorzystane (Prawo XV)

| poz. | dług | liczba | od |
|---|---|---|---|
| **D4.1** | **Zwiad bez sędziego:** cząstki Hyginusa czekające na werdykt · wizje bez rozstrzygnięcia · sugestie otwarte w CODEX | 37 · 398 · 34 | narasta od 2026-07-21 |
| **D4.2** | **Księgi poza RAG** (248 na dysku, 115 zaindeksowanych). Przyrost 40 pozycji z 01.08 przeszedł niezauważony — **żadna z 24 warstw audytu nie pilnuje ksiąg** | 133 | 2026-08-02 |
| **D4.3** | **Otwieramy szybciej, niż zamykamy** — wąskie gardło piętra LOOP. Wskaźnika **nie wpisujemy tu ręcznie**: liczy go `python -m imperium.oczy.maturitas` (ta pozycja rozjechała się z prawdą w ciągu jednej wachty, zanim ktokolwiek zdążył ją przeczytać — dokładnie klasa „liczba rosnąca sama") | czytaj z MATURITASA | trwałe |
| **D4.4** | **CLAUDE.md 308 linii** przy limicie doktrynalnym 200 — dług kontekstu płacony w KAŻDEJ sesji | +108 | trwałe |

### 🔴 D5 — największa luka strategiczna

| poz. | dług | zmierzone | od |
|---|---|---|---|
| **D5.1** | **Zero realnych orderów na MEXC.** PORTITOR melduje `MEXC✗`. Rój jest backtestowany, **nie wdrożony**; pętla P&L → wagi pozostaje NIEZAMKNIĘTA. Efekt latarni: mierzymy to, co tanie, bo drogie jest trudne | 2026-08-04 (hook) | od zawsze |
| **D5.2** | **Dane rynkowe stare:** 1H sprzed 6,4 dnia, 4H sprzed 6,5 dnia. Nie blokuje pracy nad kodem i dokumentami — **blokuje każdy pomiar na żywych danych** | 2026-08-04 (PORTITOR) | bieżące |

### ⏸️ D6 — odłożone ŚWIADOMIE, z powodem (nie milczeniem)

| poz. | pozycja | powód odłożenia |
|---|---|---|
| **D6.1** | CUSTOS LIMINIS — treść heredoca czytana jak polecenie (= G7) | strażnik **ma rację**: zawartość heredoca JEST częścią komendy; naprawa wymagałaby osłabienia strażnika |
| **D6.2** | Korony B / C / D | ZAMROŻENIE LUSTRATIO — to rozwój, a rozwój czeka na bramkę wyjścia L4 |

> **Uczciwa uwaga o wadze tej listy:** pozycje **D1 i D3.1–D3.2** psują WNIOSKI — na ich
> podstawie moglibyśmy orzec coś nieprawdziwego. Reszta to niedomknięte pętle: kolejka
> rośnie, bo mierzymy więcej, niż zamykamy, i to jest stan **zdrowszy** niż cisza, choć
> wygląda gorzej w tabeli. D1.1 było jedyną pozycją czekającą wyłącznie na słowo Cezara —
> **słowo padło 2026-08-05 i dług został spłacony**; teraz czeka już tylko na A/B przed
> włączeniem flagi, bo dotyka ścieżki decyzyjnej.

---

## 🧱 PIĘĆ BRAKUJĄCYCH FILARÓW IMPERIUM (zmierzone 2026-08-05, decyzja Cezara: DODAJEMY)

> **Pytanie Cezara:** *„czy mamy wszystkie filary, czy jakiegoś brakuje?"* — a po pierwszej
> odpowiedzi: *„sprawdź jeszcze raz, pod innym kątem, może czegoś nie mamy"*. **Trzy przejścia,
> każde pod innym kątem, każde coś znalazło.** To jest najważniejszy wniosek metodyczny tej
> wachty: **jedno spojrzenie na mapę nie wystarcza** — a skoro trzecie wciąż produkowało
> znaleziska, nie wolno ogłaszać mapy za kompletną.

### PRZEJŚCIE I — „funkcja rozrzucona po cudzych filarach, bez strażnika"

| filar | moduły | dziś leżą w | strażnik |
|---|---|---|---|
| **INSTITUTIO — UCZENIE** (wynik → zmiana zachowania) | `hedge_mwu`, `igrzyska`, `notarius`, `schola`, `drift_adapter`, `optymalizator` | **2 filary** (WIEDZA + PRÓBA) | **żaden** |
| **FISCUS — KAPITAŁ I RYZYKO** (ile stawiamy) | `kalkulator_lewara`, `praeda`, `sizing_przekonania`, `straznik_przewagi`, `aegis_tarcza`, `gubernator`, `aerarium` | **3 filary** (OBRONA + PRÓBA + DECYZJA) | **żaden** |

**Dlaczego to nie kosmetyka:** filar bez granicy nie ma strażnika, więc nikt nie pyta o jego
zdrowie JAKO CAŁOŚĆ. Dowód z tej samej wachty: filar WIEDZY **woła 3 / jest wołany 56**, a RÓJ
**ani razu** nie sięga do WIEDZY — droga powrotna nie istnieje, **bo uczenie jest niczyje**.
`ucz_mwu` stoi wyłączony od 2026-07-29 (zmierzono, że szkodzi) i od tamtej pory nienaprawiony.

### PRZEJŚCIE II — „co leży POZA granicą pomiaru"

W repo jest **467 plików `.py`**, a DESCRIPTIO liczy **270**. Poza mapą stoją: `tests/`
(**187 plików / 3517 testów**), 7 hooków, 9 skilli, `skrypty/`, `wrzutnia/`.
`archiwum/` (4) jest wykluczone **słusznie** — otwierane wyłącznie na rozkaz Cezara.

| filar | co obejmuje | dlaczego jest filarem |
|---|---|---|
| **HARNESS — RYTM I ROZKAZY** | 7 hooków, 9 skilli, `settings.json`, SIGILLARIUM | **uruchamia CAŁE Imperium** — każda sesja zaczyna się od hooka. L2b orzekło o nim „✅ POTWIERDZONE, ❌ niemierzone"; teraz wiadomo DLACZEGO: leży poza granicą wszystkich liczników |
| **ŚWIADECTWO — TESTY** | 187 plików, 3517 testów | Prawo XIX mówi, że nic nie istnieje bez kodu **i testów** — nośnik najważniejszego prawa był niewidoczny w mapie Imperium |

> 🚨 **WADA W ORGANIE Z DNIA JEGO BUDOWY (klasa K2, moja własna):** DESCRIPTIO drukował
> „✅ zero pominięć", licząc wyłącznie własny zakres. `census_organorum` ma
> `KORZENIE = ("imperium", "narzedzia")` **bez jednego słowa uzasadnienia** — granica jest
> CICHA, nie zadeklarowana. Zbudowałem organ przeciw tej klasie i sam w nią wpadłem.
> **Naprawa:** organ ma jawnie deklarować zakres i **liczyć to, co poza nim**.

### PRZEJŚCIE III — „co dzieje się bez Cezara" i „czyje ręce pracują"

| znalezisko | pomiar | znaczenie |
|---|---|---|
| 🚨 **`imperium/drogi/scheduler.py` — ZERO wołaczy produkcyjnych** | 1 plik testów, zero użycia w kodzie | **Imperium nie ma autonomii w czasie** — nic nie dzieje się, dopóki Cezar nie otworzy sesji. Prawo XV: organ zapłacony i niewpięty. Pętle ciągłe UMIEMY (`live_monitor`, `webhook_tradingview` są wpięte w `petla_live`) — brakuje **wyzwalacza**, nie pętli |
| **FAMILIA — SŁUDZY** | `bibliotekarz.py` (XI), `deepseek_glos.py` (V), `notarius.py` (I), silnik TIRO w `C:\TIRO` **poza repo** | siła robocza Imperium rozrzucona po **3 filarach**, a jej silnik leży poza repozytorium. BREVIARIUM ich raportuje, ale **raport to nie opieka**. Nazwa z *familia Caesaris* — personel administracyjny, który realnie prowadził rzymskie Imperium |

### Nazwy i sposób wdrożenia

*institutio* = kształcenie (Kwintylian, *Institutio Oratoria*) · *fiscus* = prywatny skarbiec
cesarza (odróżniany od państwowego *aerarium*) · *familia Caesaris* = personel cesarski.
Sprawdzone: żadna nie koliduje z organem ani kategorią dokumentu (`DISCIPLINA` odpadła — jest
już kategorią w TABULARIUM).

**Wariant WYBRANY PRZEZ CEZARA:** przypisania **per-moduł** w `DESCRIPTIO` jako jawne wyjątki od
reguły katalogowej, **z testem pilnującym, że każdy wymieniony plik istnieje** (ten sam mechanizm,
którym organ broni się przed strażnikami-widmami). Tanie i odwracalne, nie dotyka ani jednego
importu. **Odrzucone świadomie:** przenoszenie plików do nowych katalogów — taksonomicznie
czystsze, ale dotyka importów przy 265 modułach i 3517 testach.

---

## 🏟️ LUDUS MAGNUS — SZKOŁA GLADIATORÓW (ROZKAZ CEZARA 2026-08-05)

> **Rzymski *Ludus Magnus* stał tuż przy Koloseum: gladiator nie wchodził na arenę,
> dopóki nie przeszedł szkoły.** Cezar odrzucił podpięcie MEXC pytaniem, na które nie
> mieliśmy odpowiedzi: *„skąd wiemy, czy neurony są dobrze zbudowane i czy głosują dobrze?
> Kto im dał wzorce? Skąd wiemy, że legiony są zdrowe i że ostateczna decyzja jest właściwa,
> skoro strategie mamy tylko w szkicach?"* — **mamy 15 par z kilku lat i 63 pliki CSV**
> (4h · 15m · 5m · godzinowe · dzienne · minutowe), więc rój szkolimy i mierzymy na historii.

**Zmierzone 2026-08-05, gdy padły te pytania:**

| pytanie Cezara | co odpowiada KOD |
|---|---|
| „czy głosują dobrze" | ledger ma **4 wyniki IC na 87 neuronów** — skill ~95% roju nigdy nie zmierzony |
| „kto nimi steruje" | wagi reżimowe **wpisane ręcznie**; jedyny mechanizm uczenia (`ucz_mwu`) zmierzony jako **SZKODLIWY** i wyłączony |
| „czy strategia właściwa" | MANIFEST sam mówi: 20 strategii, **„status SZKIC — przepisy, nie zwalidowane"** |
| „czy skalibrowane" | kryterium KALIBRACJA w CONDITOR LUSTRI świeci **NIE WIEM** — rejestr nie istnieje |
| „ocena źródeł news" | `WIARYGODNOSC_ZRODEL` to **6 liczb wpisanych ręcznie** — zgadywanie udające wiarygodność |

### Kolejność ZATWIERDZONA PRZEZ CEZARA: **P1 → P5 → P3**

> ⚠️ **LISTA OTWARTA (Cezar 2026-08-05: „ludus magnus później będziemy rozbudowywać jeszcze").**
> Poniższa tabela to **szkielet startowy, nie komplet** — kolejne etapy DOPISUJEMY, nie
> zastępujemy istniejących. Kolejność P1→P5→P3 obowiązuje, dopóki Cezar jej nie zmieni.

| # | etap | odpowiada na pytanie | narzędzie |
|---|---|---|---|
| **P1** | **IC dla WSZYSTKICH 87 neuronów** — 15 par 4h, walk-forward OOS, wynik do CODEX | „czy głosują dobrze" | `narzedzia/raport_ic.py`, `narzedzia/walk_forward_ic.py` — **istnieją, użyte 4×** | 
| **P5** | **Wiarygodność źródeł MIERZONA** — 6 ręcznych liczb → skuteczność na historii (czy ostrzegało i z jakim wyprzedzeniem) | lista zaufanych źródeł | NEWS-05 + archiwum kanałów |
| **P3** | **Walidacja 20 strategii** — SZKIC → zmierzone | „czy strategia właściwa" | backtest + DSR + PBO |
| P2 | Dekorelacja całego roju (martwe głosy, dublety) | „czy legiony zdrowe" | `diagnostyka_korelacji` (Prawo XVI) |
| P4 | Rejestr kalibracji (organ bez wpisu = nieskalibrowany) | domyka bramkę wyjścia | — |
| P6 | **MEXC dopiero na końcu**: paper → grosze → skala | | |

### 🎪 EDITOR MUNERIS — organ układający PROGRAM igrzysk (wizja Cezara 2026-08-05)

**Słowa Cezara:** *„musimy mieć organ, który będzie nam wymyślał najlepsze testy, wymyślne
igrzyska — będzie poddawał próbom wszystkie bary, różne interwały na różnych parach, wszystkie
możliwe neurony w różnych ustawieniach: pojedynczo, w parach, i również strategie; wymyślał
najlepsze miksy. I za każdym razem system, dzięki najlepszym systemom anty-przeuczenia, będzie
się sam uczył. A gdy zbudujemy największą bibliotekę wiedzy — będzie z niej czerpał do nauki."*

**Nazwa (ZASADA NOMENKLATURY):** rzymski *editor muneris* układał PROGRAM igrzysk i decydował
o parach gladiatorów — nie walczył i nie sędziował. Trening i rankingi mamy w `igrzyska.py`
(LANISTA), sędziowanie w `walidacja.py`; brakuje **tego, kto decyduje, kto z kim staje**.

> 🔒 **ZASADA NIENARUSZALNA — LICZBA PRÓB JEST SKŁADNIKIEM WERDYKTU, NIE JEGO TŁEM.**
> „Wszystkie możliwe ustawienia" jest niewykonalne kombinatorycznie (same pary z 87 neuronów
> to **3 741 kombinacji × ~90 zbiorów** par/interwałów ≈ **337 tys. biegów**), ale groźniejsze
> jest co innego: **im więcej prób, tym pewniejsze, że najlepszy wynik jest dziełem przypadku.**
> Deflated Sharpe Ratio istnieje dokładnie po to — deflacja NALEŻY do liczby prób. Organ
> przeszukujący bez budżetu i bez zapisu liczby prób **unieważnia własne wyniki**.

**Konstrukcja wynikająca z tej zasady:** sekwencyjny **plan doświadczeń z budżetem prób**
zamiast przeszukiwania wyczerpującego · każda próba w ledgerze append-only · licznik prób
**zasila DSR/PBO** · purged-CV od pierwszego biegu · wiedza z biblioteki wchodzi jako
**priorytet kolejnych prób** (co sprawdzić najpierw), nigdy jako uzasadnienie wyniku.

**Warunek wstępny, nie skutek:** pętla areny jest dziś ROZWARTA (`ucz_mwu = False`, bo
zmierzono, że SZKODZI: −0,6/−0,5 pp, PBO ~0,6). EDITOR MUNERIS bez domkniętej pętli do wag
będzie produkował rankingi, których nikt nie skonsumuje — czyli powtórzy stan obecny, tylko drożej.

> ⚠️ **ZASTRZEŻENIE OBOWIĄZUJĄCE OD PIERWSZEGO BIEGU P1:** arena strojona wielokrotnie na
> tych samych 15 parach zaczyna mierzyć **własne dopasowanie, nie rynek**. PBO, DSR
> i purged-CV chodzą **od początku**, nie na końcu — inaczej zbudujemy arenę, która
> wygrywa wyłącznie z przeszłością.

> 📕 **KLASA WADY ZNALEZIONA PRZY OKAZJI:** **U2** niżej nakazuje „kolejność wg RYZYKA, nie
> alfabetu — najpierw ścieżka decyzyjna, potem przyrządy orzekające, **na końcu dokumentacja**".
> Trzy wachty z rzędu robiły dokumenty i bramki, czyli **ostatnią pozycję tej listy**. Rozkaz
> Cezara nie zmienia kursu — **przywraca kolejność, którą sami zapisaliśmy i której nie
> wykonywaliśmy**.

---

## 🧹 LUSTRATIO IMPERII — WIELKI PRZEGLĄD (ROZKAZ STAŁY — Cezar 2026-08-04)

> ### ✅ ZAMROŻENIE ZDJĘTE 2026-08-05 — zastąpione rozkazem DELIBERATIO
> **Cezar:** *„odmrażam oficjalnie, to nic nie daje — tylko teraz, zanim coś zrobimy,
> musimy dokładnie to przeanalizować: każde zadanie wolniej, ale dokładniej."*
> **Zdjęte DECYZJĄ, nie spełnieniem kryteriów** — `conditor_lustri` świecił wtedy
> 2 spełnione / 2 niespełnione / 3 NIE WIEM. Organ zostaje **miernikiem zdrowia**,
> przestaje być blokadą; kryteria bez producenta **nadal są długiem**.
> Ograniczeniem nie jest już TEMAT zadania, lecz **głębokość jego analizy** (`CLAUDE.md § DELIBERATIO`).
> Powód: zamrożenie nie zapobiegło ANI JEDNEJ z wad złapanych 2026-08-05 — wszystkie
> wzięły się z pośpiechu WEWNĄTRZ dozwolonego zadania, nie z niedozwolonego tematu.
>
> *Poniższa treść zostaje jako zapis powodu i przebiegu przeglądu — LUSTRATIO trwa jako
> program porządkowy, przestaje być zakazem.*

**Słowa Cezara (2026-08-04):** *„jabłko psuje się od środka, a ryba od głowy — dlatego
nie możemy pozwolić, aby nasze Imperium było robaczywe i zepsute w żadnej z warstw."*

**Powód zmierzony tego samego dnia — trzy dziury w trzech różnych organach:**
- LUSTRUM: **27 z 260 modułów** bez żadnego wołacza; naiwny sygnał dałby **100% fałszywek**
  (25/25 sierot to przyrządy ręczne z CLI), a pod nimi **3 realne moduły otestowane
  i nigdzie niewpięte** — majątek leżący odłogiem.
- TABULARIUM: **23 błędy + 33 ostrzeżenia** leżące w trybie miękkim; **23 dokumenty bez
  pola `wlasciciel` są NIEWIDZIALNE dla bramki GNICIA** (pętla po właścicielach nie
  wykonuje się ani razu) — nie „przechodzą kontrolę", tylko nie są kontrolowane.
- MATURITAS: **52 wiersze ROADMAP** wypadają z pomiaru bez śladu, bo mają w kolumnie 3
  opis zamiast statusu; dług honorowy liczony osobną arytmetyką, nieświadomą ODROCZENIA.

Wspólna KLASA wszystkich trzech: **organ, który nie umie powiedzieć „nie wiem", milczy —
a milczenie czytamy jako zieleń.** To jest robactwo, o którym mówi rozkaz.

### Kolejność przeglądu (ZATWIERDZONA)

| # | Etap | Stan |
|---|---|---|
| L0 | **LUSTRUM** — testy ✅ (24 w `tests/test_lustrum.py`) i kalibracja ✅ (pięć świadectw zamiast jednego sygnału). **Zostaje granica kalibracji (= D3.4):** prawdę podstawową klasy WPIĄĆ ustalił sam autor klasyfikatora (klasa K3), a 24 pozycje klasy ZBADAĆ nie były weryfikowane pojedynczo. ⚠️ Ten wiersz mówił „brak testów i kalibracji" jeszcze 2026-08-05, gdy jedno i drugie istniało od doby — **dokument o przeglądzie gnicia sam zgnił**, złapane przez CONDITOR LUSTRI | 🟡 granica kalibracji |
| L1 | **TABULARIUM — MECHANIZM** ✅ (2026-08-04): błędy **23 → 0**. Naprawiona sprzeczność „`—` znaczy brak, a bramka żąda wartości"; nowe bramki **T1b** (właściciel albo jawny `bez_wlasciciela`, z zakazem wyciszania dla TABULA/FORMA/MENSURA), **T2b** (zegar 90 dni dla dokumentów bez właściciela — brak kodu ≠ brak kontroli) i **filtr gita** (plik spoza kontroli wersji nie jest dokumentem Imperium, Prawo XIX). 22 dokumenty uporządkowane, właściciel-widmo `schola` naprawiony, +10 testów | ✅ |
| L2 | **Przegląd WSZYSTKICH organów** wg kategorii, wykonalności, zadań, piętra ewolucji i **wzajemnej współpracy** — checklisty kontrolne per kategoria. Wchodzi tu **L2a** (mapa współpracy) i **L2b** (taksonomia pięter — WYKONANE) | 🟡 w toku |
| **L3** | **PRZEGLĄDY TREŚCI — ZACZĘTE OD KALIBRACJI PRZYRZĄDU** (2026-08-04, decyzja Cezara „wg rekomendacji"). Zamiast odhaczać 26 pozycji po kolei, **zmierzono najpierw sam sygnał** na zamrożonej próbce 6 (ziarno 20260804, etykiety z pełnej treści + diffów): **precyzja werdyktu 33%** (2/6), **precyzja przyczyny 0/6**. Oba prawdziwe gnicia brały się z **liczb rosnących SAME** (fragmenty RAG, sesje kroniki) — niewidzialnych dla bramki opartej na commitach. **Zrobione:** naprawa u źródła (klucz `sesje_kroniki` + `sesje_w_kronice()`, zaszyte liczby → znaczniki W15) w MAPA_PAMIECI i PLAN_TIRO; **drugie świadectwo** `python narzedzia/tabularium.py swiadectwa` dzieli 26 alarmów na **9 MOCNYCH / 17 SŁABYCH** (zgodność z próbką 6/6, próg pospolitości <5 plików). **Kalibracja II (L3a, ten sam dzień)** przeetykietowała wszystkie MOCNE prawdą podstawową i wymieniła mechanizm — dziś **4 MOCNE / 20 SŁABYCH** z 24. **Zostaje:** 4 przeglądy MOCNYCH + 11× T3 DUBLET + 20 SŁABYCH okazjonalnie | 🟡 **przyrząd skalibrowany dwukrotnie, kolejka posortowana** |
| L3a | **Limit drugiego świadectwa — nagłówek hunka podawał KLASĘ** ✅ (zmierzone i domknięte 2026-08-04, kalibracja II). Prawda podstawowa dla **wszystkich 7 MOCNYCH** (dokument w całości + realny diff): realnie kłamały **2** — PLAN_DEEPSEEK (sygnatura `zapytaj` bez 4 parametrów DISPENSATORA) i PAMIEC_ABSOLUTNA (cytat `f"{data}_{symbol}_…"` przy sanityzowanym symbolu); oba naprawione. **Kandydat B („hunk bez `class`") ODRZUCONY POMIAREM** — kupował +5 pp precyzji za **połowę recallu**; wariant C dał wynik identyczny z B, bo w populacji nie ma ani jednego `diff-class`, więc dane tego wyboru **nie rozstrzygają**. Wdrożony **wariant D**: z hunka bierzemy NUMER LINII i szukamy definicji, która ją obejmuje. Efekt: 7 → **4 MOCNE**, przyczyna wreszcie wskazuje sprawcę (`policz` zamiast `KalkulatorLewara`, `zapytaj` zamiast `GlosImperium`), **żaden SŁABY nie awansował** (D ⊂ A, zero nowego szumu). Koszt biegu 40 s → **97 s** (świadomie poza audytem). +5 testów granic | ✅ |
| L3a2 | **Druga runda tej samej kalibracji: BLOKI KODU też są cytowaniem** ✅ (2026-08-04). `_symbole_cytowane` czytało wyłącznie backticki inline, a dokumenty pokazują REALNE API w blokach ```` ```python ````. Złapane na żywym przypadku: `MANUAL_UZYTKOWNIKA` uczy wywołania `raport_waznosci(sygnaly, wyniki)`, które od `8561bc6` **rzuca `ValueError`** przy nierównych seriach — nazwa stała tylko w bloku, więc manual uczący wywołania, które wybucha, przechodził jako SŁABY. Zmierzone na populacji 23: precyzja **3/7** wobec 2/4 bez bloków (różnica w granicach szumu przy tej próbie), ale **recall 3/3** wobec 2/3 — dla narzędzia PRZEGLĄDU właściwy kierunek, bo fałszywka kosztuje minutę czytania, a przeoczenie kosztuje kłamiący manual. +2 testy granic | ✅ |
| L3e | **T3 DUBLET — bramka BEZ prawdy podstawowej** (obserwacja zmierzona 2026-08-04, do rozstrzygnięcia). T3 grupuje po `(kategoria, wlasciciel)`, czyli pyta „czy dwa dokumenty wskazują ten sam plik" — **nie o podobieństwo treści**. Na 10 zgłoszeniach: `rejestr.py` łączy README (1 wzmianka), INDEKS (10), MANIFEST (2), MAPA_KLUCZY (2) — cztery różne przekroje; **9 z 12 dokumentów w zgłoszonych grupach otwiera `powod_istnienia` słowem „Jedyny/Jedyne"**. Precyzja T3 jest **NIEZNANA** — nie odhaczamy 10 werdyktów `dublet_rozstrzygniety`, bo to wyciszenie pisane przez autora dokumentu (klasa K3: piszący decyduje o własnej prawdzie), i po nim alarm znika na zawsze. **Do zrobienia najpierw:** kalibracja jak przy T2 — prawda podstawowa z porównania TREŚCI o wspólnym pliku | 🔴 |
| L3d | **Klasa nieobjęta ŻADNYM świadectwem: CYTAT DOSŁOWNY KODU** (wykryta pomiarem 2026-08-04). Dokument bywa wierny nie NAZWIE, lecz kodowi — `PAMIEC_ABSOLUTNA.md` podawała `f"{data}_{symbol}_{typ.lower()}.jsonl"`, gdy kod od 2026-07-29 sanityzuje symbol, a rozjazd siedzi w prywatnej `_sciezka`, której dokument nie wymienia z nazwy. **Żaden wariant oparty na symbolach tego nie złapie**; wariant sprzed kalibracji II „trafiał" ten przypadek wyłącznie przez nazwę klasy, czyli z tautologii — utrata tego trafienia jest uczciwsza niż fałszywa zasługa. **Do zbudowania:** świadectwo pytające, czy fragment kodu cytowany w backticku/bloku nadal występuje dosłownie w pliku-właścicielu | 🔴 |
| **L3c** | 🚨 **STRAŻNIK PRACY BEZ ŚLADU — dziura międzyorganowa** (rozkaz Cezara 2026-08-04: *„musimy mieć zabezpieczenie i weryfikowanie takiej sytuacji, któryś organ musi to wykrywać"*). **Zmierzone tego samego dnia na żywym przypadku:** wachta wykonała pełną pracę w kodzie, a wpis do Dziennika **nie powstał wcale** (komenda padła przed zapisem) — i **żaden organ tego nie zauważył**. CLAUDE.md **deklaruje** „Brak wpisu z dziś = czerwony alarm w podsumowaniu startowym", ale grep po hookach, audycie i Dzienniku daje **ZERO** implementacji: hook startowy woła tylko `dziennik_niesmiertelny nastepny` (drukuje następny krok, nie sprawdza czy poprzedni wpis istnieje). EXACTOR świadomie tego nie bada, bo jego komentarz mówi, że „bramkę, Dziennik i commit sprawdza bramka i audyt" — a **audyt tego nie sprawdza**. Klasyczne K2 (milczenie czytane jako zieleń) + przekazanie odpowiedzialności organowi, który jej nie przyjął. **Do zbudowania:** warstwa audytu / krok hooka porównujący commity wachty z ostatnim wpisem Dziennika — commit merytoryczny bez wpisu = alarm | 🔴 **P0 następnej wachty** |
| L3b | **Uzupełnienie pozostałych wykrytych braków i luk** — dopiero po komplecie pomiarów | 🔴 |
| L4 | **Bramka wyjścia** ✅ *(zamrożenie zdjęte decyzją Cezara 2026-08-05, przy CZERWONEJ bramce — patrz ramka wyżej)*. **U1 WYKONANE 2026-08-05**: organ `CONDITOR LUSTRI` (`python -m imperium.pretorianie.conditor_lustri --bramka`, 7 kryteriów, +18 testów) zamienia „w pełni skalibrowane" w exit code. Pierwszy pomiar: **1 spełnione / 3 niespełnione / 3 NIE WIEM**. Sam etap L4 domknie się dopiero przy exit 0 — i **zdejmuje zamrożenie CEZAR, nie organ** | 🔴 bramka istnieje, świeci czerwono |

### Co sprawdzamy przy KAŻDYM organie (checklista bazowa)

1. **Zgodność z prawem** — które z 25 Praw go dotyczą i czy je spełnia
2. **Wykonalność** — czy w ogóle da się go uruchomić (droga wejścia: import, CLI, hook)
3. **Kalibracja** — czy przyrząd orzekający był mierzony na PRAWDZIE PODSTAWOWEJ (LEX TALARUS)
4. **Testy** — czy istnieją i czy mają **test granicy** dla każdego progu
5. **Piętro ewolucji** — PROMPT / LOOP / GRAPH / HARNESS / NEURO-SYMBOLIC …
6. **Współpraca** — kto go woła, kogo on woła, czy zgadza się ze schematem swojego etapu
7. **Luka** — czego mu brakuje, żeby był zgodny ze wzorcem

### ⚖️ METODA PRZEGLĄDU: KLASA, NIE ILOŚĆ (ZATWIERDZONE — Cezar 2026-08-04)

> *„nie ilość — o tym mówiłem wcześniej, ilość to niepotrzebne przeciążenie,
> ale KLASA i JAKOŚĆ jest ważna"* — Cezar

**Nie odhaczamy 262 organów po kolei.** Szukamy **WZORCA WADY** i naprawiamy go u źródła;
jedna naprawa klasy zamyka wiele pozycji naraz. Dowód, że to działa: sześć dzisiejszych
wad w pięciu różnych organach okazało się **czterema klasami**, nie sześcioma sprawami.

Konsekwencja dla bramek: **nie dobudowujemy warstwy 25.** Audyt ma dziś 24 warstwy
i wszystkie dzisiejsze wady przez nie przeszły — dokładanie kolejnej to leczenie objawu
metodą, która właśnie zawiodła. Najpierw **mierzymy siłę tego, co mamy** (U8).

**Cztery klasy zmierzone 2026-08-04 — to jest lista robocza L2:**

| Klasa | Objaw u nas | Lek |
|---|---|---|
| **K1 — dwa organy liczą ten sam fakt osobno** | MATURITAS liczy dług jako `NOTA−CORONA` zamiast pytać `codex_notarum`, więc nie wie o ODROCZENIU; CENSUS i INDEKS trzymają tę samą datę dwa razy (wywaliło bramkę 08-04) | fakt ma **jednego producenta**, reszta go woła; warstwa tropiąca powtórne wyprowadzanie |
| **K2 — milczenie czytane jako zieleń** | MATURITAS gubi 52 wiersze ROADMAP; TABULARIUM zwalnia 22 dokumenty z bramki GNICIA | każdy klasyfikator ma trzeci wynik **NIE WIEM** i musi go **LICZYĆ**; audyt czerwony przy nieznanych > 0 bez jawnej deklaracji |
| **K3 — piszący decyduje o własnej prawdzie** | `dopisz_lekcje` brało datę od wołającego i **cofało** świeżość dokumentu | niezmiennik należy do **POLA**, nie do wołającego (monotoniczność, append-only) — egzekwowany w miejscu zapisu |
| **K4 — wyciszenie bez powodu** | działa tam, gdzie jest (`powod_acta`, `dublet_rozstrzygniety`), nie działa nigdzie indziej | **uogólnić na wszystkie bramki**: wyciszenie zawsze wymaga powodu, który zostaje na widoku |

### 🔎 L2b — QUAESTIO NAD TAKSONOMIĄ PIĘTER (WYKONANE 2026-08-04, rozkaz Cezara „tak zrób")

**Po co:** Cezar rozkazał, by każdy moduł nosił oznaczenie **grupy ewolucji**. Stemplowanie
261 organów taksonomią, której sami nie osądziliśmy, rozniosłoby jeden błąd po całym
Imperium — naprawa byłaby 261-krotna zamiast jednokrotnej. Dlatego najpierw sąd.

**Źródło:** `wrzutnia/Imperium-Botów-Tradingowych 2.md` (§5.2–5.3) — materiał zewnętrzny,
ten sam, który wyprodukował `US20230000000A1` i `abc123.ngrok.io`. Kandydat ≠ prawda.

> 🚨 **KOREKTA WŁASNEJ LICZBY:** mówiliśmy „MATURITAS mierzy **3 z 9**". Źródło wymienia
> **OSIEM** pięter (warstwy 0–7), nie dziewięć. Liczba „9" pochodziła z pamięci, nie
> z materiału — czyli dokładnie ten błąd, który nasze własne prawo zakazuje. Jest **3 z 8**.

| # | Piętro | Co u NAS je realizuje (grep) | Werdykt | Mierzone? |
|---|---|---|---|---|
| 0 | PROMPT | TIRO (`notarius.py`), Hyginus (`bibliotekarz.py`), DISPENSATOR | ✅ POTWIERDZONE | ✅ — ale patrz kolizja niżej |
| 1 | CONTEXT | 6 modułów pamięci + 11 modułów RAG | ✅ POTWIERDZONE | ❌ **niemierzone** |
| 2 | HARNESS | 7 hooków, senat, audyt 24 warstw, SIGILLARIUM, 25 Praw | ✅ POTWIERDZONE | ❌ **niemierzone** |
| 3 | LOOP | `hedge_mwu.py` + pętla decyzyjna | ✅ POTWIERDZONE | ✅ |
| 4 | GRAPH | `graf_pamieci.py` — ale to graf PAMIĘCI, nie routing decyzyjny; `LangGraph` = **0 trafień** | 🟡 CZĘŚCIOWE | ✅ (3/4, „nie czytany przy decyzji") |
| 5 | HIPERGRAF | **zero trafień w całym repo** | 🔴 BRAK | — |
| 6 | NEURO-SYMBOLIC | INDEX FALSORUM, VINDEX, Prawo XXI | ⚠️ **SPORNE** | ❌ |
| 7 | SAMO-EWOLUCJA | `ucz_mwu` | ⚠️ **ISTNIEJE, ale OBALONE** | ❌ |

**Dwie tezy, które NIE PRZETRWAŁY pomiaru — obie były nasze własne:**

1. **„HARNESS i NEURO-SYMBOLIC już stoją i nie są liczone".** HARNESS — tak, potwierdzone.
   **NEURO-SYMBOLIC — wątpliwe.** Źródło rozumie przez to *weryfikację ŁAŃCUCHA DECYZYJNEGO*
   (VeriCoT, SITL: czy decyzja jest logicznie spójna). Nasze INDEX FALSORUM i VINDEX weryfikują
   **KOD i DOKUMENTY**, nie decyzje handlowe. To inna rzecz pod tą samą nazwą — a podpięcie jej
   pod piętro 6 zawyżyłoby nasz stan. Do rozstrzygnięcia, nie do policzenia.
2. **„Prawdopodobnie zaniżamy własny stan" — częściowo prawda, ale mniej, niż sądziliśmy.**
   Realnie niemierzone i potwierdzone są **DWA** piętra (CONTEXT, HARNESS), nie sześć.

**Trzecia rzecz do rozstrzygnięcia — KOLIZJA NAZWY na piętrze 0.** MATURITAS mierzy pod
nazwą „PROMPT" *zdrowie specyfikacji* (czy `CLAUDE.md` nie puchnie), a źródło rozumie
*warstwę instrukcji dla modeli* (TIRO/Hyginus). Dwie różne rzeczy w jednym słowie — jeśli
tego nie rozdzielimy, `CURSUS ARTIS` zsumuje jabłka z gruszkami.

**Wniosek operacyjny:** do stemplowania modułów wchodzą **cztery piętra potwierdzone**
(PROMPT · CONTEXT · HARNESS · LOOP) + GRAPH jako częściowe. HIPERGRAF, NEURO-SYMBOLIC
i SAMO-EWOLUCJA **nie stemplują niczego**, dopóki nie zostaną rozstrzygnięte.

### 🕸️ L2a — MAPA WSPÓŁPRACY ORGANÓW (pytanie Cezara: „czy organy właściwie się komunikują")

Zmierzone 2026-08-04 (import z drzewa składniowego, nie regex): **261 organów, 489 krawędzi**,
164 wołających, 140 wołanych, **30 zupełnie samotnych**. Huby: `czytnik_csv` (44), `backtest` (36),
`baza` (28), `mikro_neuron` (23). Trzy luki o różnej trudności:

- **G1 — graf połączeń.** Da się zbudować dziś (liczby wyżej). ⚠️ **30 samotnych ≠ 27 sierot LUSTRUM**
  — dwie różne miary (import AST vs wzmianka nazwy); rozjazd sam jest informacją, do zbadania.
- **G3 — wzorzec oczekiwany.** Bez zadeklarowanego schematu graf jest obrazkiem, nie kontrolą.
  To **rejestr układów z CORONY D** i jedyne znane domknięcie wąskiego gardła GRAPH
  („graf nie jest czytany przy żadnej decyzji") — graf organów czytany przy przeglądzie
  byłby PIERWSZYM czytelnikiem przy decyzji.
- **G2 — aktywność RUNTIME.** Zero. Wszystko dziś mierzymy statycznie; organ może być
  zaimportowany i **nigdy się nie wykonać** (np. za flagą opt-in OFF). Ostatni w kolejce —
  wymaga instrumentacji kodu produkcyjnego, a rozwój jest zamrożony.

### 🆕 CO ARCHITEKT PROPONUJE DOŁOŻYĆ DO POSTANOWIENIA (do decyzji Cezara)

Rozkaz kazał sprawdzić, czym go uzupełnić. Siedem pozycji, każda z powodem:

- ✅ **U1 — MIERZALNY WARUNEK WYJŚCIA (WYKONANE 2026-08-05).** „W pełni skalibrowane" bez
  liczby jest stanem niefalsyfikowalnym: zamrożenie albo nigdy się nie skończy, albo skończy
  się arbitralnie. Zbudowany organ **CONDITOR LUSTRI** — jedna bramka, exit 0 dopiero przy
  komplecie siedmiu kryteriów, `NIE WIEM` blokuje tak samo jak `NIE`.
  **Dwa kryteria nie mają jeszcze producenta i to one są realnym warunkiem odmrożenia:**
  rejestr klas K1–K4 (czy lek WDROŻONY, nie tylko nazwany) i rejestr kalibracji organów
  orzekających. Ocena ryzyka przekazana Cezarowi: groźniejsze od przedwczesnego odmrożenia
  jest zamrożenie bez licznika — po jego drugiej stronie leży D5.1 (zero realnych orderów).
- **U2 — KOLEJNOŚĆ WG RYZYKA, NIE ALFABETU.** „Ryba psuje się od głowy" — głową jest to,
  co decyduje o kapitale. Najpierw ścieżka decyzyjna (wejście/wyjście z pozycji), potem
  przyrządy orzekające, na końcu dokumentacja.
- **U3 — CHECKLISTA PER KATEGORIA, nie jedna dla wszystkich.** Neuron sprawdza się inaczej
  niż strażnik: neuron musi mieć pole WYMAGA i nie zwracać wiecznie NEUTRAL, strażnik musi
  być przetestowany na OBU drogach wejścia (zmierzona klasa: 3 wady w jednej wachcie 08-03).
- **U4 — REJESTR POSTĘPU PRZEGLĄDU (append-only).** 262 organy nie zmieszczą się w jednej
  wachcie. Bez ledgera przegląd zgubi się między sesjami albo zrobimy go dwa razy.
- **U5 — ZAKAZ POWIĘKSZANIA MIANOWNIKA.** W czasie przeglądu nie powstają nowe organy poza
  tymi, które zamykają wykrytą lukę — inaczej liczba do sprawdzenia rośnie szybciej,
  niż ją zbijamy.
- **U6 — ANTYWSKAŹNIKI.** Przegląd musi być NIEOSZUKIWALNY: pozycji nie zamyka się przez
  skasowanie jej ani przez zmianę nazwy. Wzorzec gotowy — `maturitas --antywskazniki`.
- **U7 — SPRZĄTANIE PO SOBIE JEST CZĘŚCIĄ PRZEGLĄDU.** Każda znaleziona luka od razu dostaje
  albo naprawę, albo wpis w rejestrze z terminem. Znalezisko bez adresu to kolejna sugestia
  w stosie 34 nierozstrzygniętych.
- **U8 — MUTACJA JAKO STAŁY POMIAR** ⭐ *rekomendacja nr 1 Architekta*. Okresowo wstrzykujemy
  znane wady i mierzymy, ile bramka łapie. **Bramka o niezmierzonej sile to bramka, w którą
  WIERZYMY.** Robiliśmy to RAZ (7/8 złapanych) i nigdy więcej. To jedyny punkt, który mówi,
  czy pozostałe naprawy w ogóle działają — reszta to naprawy, ten jeden to sprawdzian.
- **U9 — KALIBRACJA JAKO BRAMKA, NIE ZASADA.** LEX TALARUS wymaga kalibracji przyrządu, ale
  **nic tego nie egzekwuje**. Organ orzekający bez wpisu kalibracyjnego w ledgerze → błąd
  audytu. Dowód opłacalności z 08-04: naiwna miara LUSTRUM miała **7,4% precyzji**.
- **U10 — JEDNA KOMENDA SYMBIOZY.** Wszystkie generatory przepisywane w kolejności zależności
  jednym poleceniem. Dziś trzeba **pamiętać**, że CENSUS karmi INDEKS — i właśnie dlatego
  bramka poszła na czerwono 08-04. Zależność trzymana w ludzkiej pamięci to awaria zaplanowana.

### 👑 CZTERY KORONY — kolejność ZATWIERDZONA PRZEZ CEZARA 2026-08-03

> ⚠️ **ODŁOŻONE na czas LUSTRATIO** (rozkaz 2026-08-04): korony C, B i D to ROZWÓJ, a rozwój
> jest zamrożony do zdjęcia bramki. Korona **A jest już wdrożona**, więc nic nie blokuje.

> Powstały jako opcje spłaty NOTY (LEX TALIONIS) za zwiad puszczony równolegle z bramką.
> **Nowy ROZKAZ STAŁY z tej samej wachty:** przed spłatą noty Architekt podaje **TRZY
> opcje CORONY** (uzasadnienie · opis · wpływ · co wnosi), a **wybiera Cezar** — dotąd
> 54 korony powstały bez tej bramki, czyli wybierał ten, kto zawinił. Cezar wybrał
> **wszystkie cztery** i dodał czwartą własnym pytaniem o organ ewolucji.

| # | CORONA | Co wnosi | Piętro | Koszt |
|---|---|---|---|---|
| **A** ✅ | **SILENTIUM** (WDROŻONA 2026-08-03) — bramka zakłada blokadę, hook PreToolUse **odmawia zapisu do repo** w trakcie biegu | VINDEX *wykrywa* zabrudzenie po fakcie; **nic nie ZAPOBIEGA**. Zmierzone: 4 unieważnione biegi w 4 dni, **dwa z nich w jednej wachcie 08-03 przez tego samego, kto zasadę zapisał** — dowód, że sama wiedza nie wystarcza | HARNESS | ~1 wachta |
| **C** | **CUSTOS BIBLIOTHECAE** (= A15) — warstwa W25: dysk ↔ katalog ↔ cache ↔ RAG | Żadna z 24 warstw nie pyta o KSIĘGI. Dowód: 40 ksiąg przybyło 01.08, **nikt nie zauważył przez dobę**, audyt drukował „pełna harmonia" | LOOP | ~1 wachta |
| **B** | **VINDEX → GRAF W8** (= H6) — krawędzie `(plik) —[naruszenie]→ (commit)` | Jedyny producent krawędzi z **realnych zdarzeń**, nie z tekstu. Jedyna droga na GRAPH **nieblokowana przez A10** — ale nie daje czytelnika przy decyzji, więc GRAPH zostanie 3/4 | GRAPH | ~½ wachty |
| **D** 🟡 | **CURSUS ARTIS** — organ mierzący **WSZYSTKIE piętra**, z **rejestrem układów** (wzorce połączeń, status `ZATWIERDZONY/KANDYDAT/OBALONY`) | **CZĘŚCIOWO WYKONANE 2026-08-06** (rozkaz Cezara „zróbmy teraz, żeby przy następnej sesji już działało"): MATURITAS mierzy **5 pięter, nie 3** — dopisane HARNESS (4/4) i NEURO-SYM (4/4), które **stały zbudowane i nieliczone**, więc zaniżanie POTWIERDZONE i usunięte. Wydruk pokazuje organy per piętro, luki i wskazówkę o pozycji w planie. **Rejestr układów NADAL nierobiony.** | wszystkie | ~1 wachta (reszta) |

> **ROZSTRZYGNIĘCIE CEZARA o układach (D):** wzorce wchodzą do rejestru **wyłącznie po
> zatwierdzeniu nowej wizji albo po zmierzonym odkryciu** — nigdy z lektury materiału.
> Domyka to pętlę *odkrycie → zatwierdzenie → wzorzec → egzekwowanie* i usuwa zarzut,
> że budowalibyśmy miernik na cudzej, nieosądzonej taksonomii.
>
> **⚠️ WARUNEK UCZCIWOŚCI DLA D — SPRAWDZONY I ROZSTRZYGNIĘTY 2026-08-06.** Brzmiał: osiem
> z dziewięciu pięter znamy z materiału, którego jeszcze nie osądziliśmy — tego samego, który
> wyprodukował `US20230000000A1`. **Cezar kazał to zweryfikować zwiadem; FRUMENTARIUS obalił
> OBIE rzeczy:**
> - **patent `US20230000000A1` NIE ISTNIEJE** — Google Patents 404, a numeracja publikacji USA
>   startuje od `0000001`, więc numer z samych zer jest strukturalnie niemożliwy. Kontrola
>   pozytywna na sąsiednim `US20230010000A1` zwróciła pełny rekord, więc 404 jest realny.
> - **liczba „9 pięter" NIE MA POKRYCIA W ŹRÓDŁACH.** Realne taksonomie mają 5
>   (Prompt/Context/Harness/Loop/Graph — Rastogi, arXiv 2606.28270), 6 (autonomia L0–L5),
>   7 (Arsanjani) albo 8 (Eledath). Jedyna znaleziona „dziewiątka" to oś FILOZOFICZNA
>   Twemlowa (ANI→AGI→ASI→„AI as God") — inna oś niż warstwy inżynierii. Nasza dziewiątka
>   była prawdopodobnie **sklejką dwóch taksonomii**.
>
> Oba twierdzenia trafiły do **INDEX FALSORUM** (18→20), więc nie wrócą jako fakt. Zasięg
> miernika liczy się odtąd od taksonomii POTWIERDZONEJ: **5 z 6** (5 warstw + NEURO-SYM),
> nie 3 z 9. Jedyne piętro brakujące z potwierdzonej piątki to **CONTEXT** (arXiv 2507.13334) —
> dziś mierzone częściowo wewnątrz PROMPT przez AERARIUM, bez własnego poziomu.
> Sześciu kandydatów spoza tej osi (OBSERVABILITY, GUARDRAILS, INTENT, MEMORY, COORDINATION,
> AUTONOMIA L0–L5) czeka w kodzie jako `KANDYDACI_NA_PIETRA` — **nie awansują sami**,
> wchodzą wyłącznie po zatwierdzeniu przez Cezara (rozstrzygnięcie o układach, wyżej).
> i `abc123.ngrok.io`. Pierwsza wersja rejestru zawiera **tylko to, co potwierdzone
> w NASZYM kodzie**; reszta czeka na QUAESTIO.

### 👑 DRUGA TRÓJKA KORON — spłata NOTY `N-fa723062` (wybór Cezara 2026-08-03)

> **Nota:** SILENTIUM przeszedł bramkę z wadą cyklu życia blokady — cisza WYŁĄCZNA
> chroniła *plik blokady* zamiast *repozytorium*, drugi bieg dostawał komunikat
> „bieg idzie BEZ ochrony" (nieprawdę), a pierwszy wychodzący zdejmował ciszę spod
> trwającego biegu. **19 testów tego nie złapało, bo cały pakiet testuje JEDNOWĄTKOWO.**
> Zgodnie z ROZKAZEM STAŁYM Architekt podał trzy opcje; **Cezar wybrał A i rozkazał
> zacząć od niej w nowej sesji, resztę wg rekomendacji.**

| # | CORONA | Unikat — czego dziś NIE MA | Wpływ | Stan |
|---|---|---|---|---|
| **A** 🎯 | **LUSTRUM** — organ mierzący **POŻYTEK** narzędzia (kto woła, wiek ostatniego użycia, testy, ślad w ledgerze) i wycofujący etapami `PODEJRZANY → KARENCJA → HONESTA MISSIO` | CENSUS ORGANORUM (W17) pyta wyłącznie „czy **zameldowany**", **nigdy „czy jeszcze potrzebny"**. Prawo XV robiliśmy RĘCZNIE 05.07 (12 niepodpiętych) — audyt na rozkaz, nie organ w pętli | pierwszy organ, który **ZAMYKA, a nie otwiera**: ROADMAP 15,5%, 375 wizji i 34 sugestie bez werdyktu | 🔴 **START NOWEJ SESJI** (rozkaz Cezara 08-03) |
| **B** | **PROBATIO ITINERUM** — warstwa sprawdzająca, że narzędzie bramkowe daje **ten sam werdykt każdą drogą wejścia** (jawny plik / git / hook / `pytest` vs `run_tests.py`) | nikt nie testuje **równoważności dróg wejścia**. Zmierzone 08-03: **trzy wady tej klasy w jednej wachcie** (skaner wad — 5 fałszywek przy wywołaniu z hooka; test przechodzący pod pytest i padający pod bramką; wcześniej append-only w 6 organach / 0 egzekucji) | broni wiarygodności **wszystkich** bramek naraz — bez tego „czysto" znaczy tylko „czysto tą drogą" | 🔴 wg rekomendacji |
| **C** | **SPECULATOR CONCURRENS** — kalibrowany próbnik współbieżności: N równoległych biegów i pomiar, czy niezmienniki (cisza, append-only, sigillum) trzymają | **całe Imperium testuje jednowątkowo** — to ślepa plama pakietu, nie luka jednego organu | jedyny sposób, by wada tej klasy została złapana **testem, a nie sesją Cezara** | 🔴 wg rekomendacji |

> **🚨 DWA ROZJAZDY MATURITASA zmierzone przy domykaniu 2026-08-03** (dopisane, nie
> przemilczane — miernik chwalący zamiast mierzyć jest gorszy od braku miernika):
> **(1)** dopisanie do ROADMAP **7 realnych pozycji** (3 korony + 4 pytania) nie ruszyło
> licznika — dalej `11/71`, więc te tabele są dla niego niewidzialne; to druga strona
> zarzutu z recenzji PR #139, że liczy wiersze legionów jako pozycje.
> **(2)** migawka zapisała `dlug_honorowy: 0` w chwili, gdy `codex_notarum bilans`
> pokazuje **1** (nota `N-fa723062`). Miernik długu, który nie widzi długu, to dokładnie
> klasa „przyrząd kłamie, nie system". **Zadanie na wachtę CORONY A** — LUSTRUM i tak
> będzie czytał te same źródła.

### ❓ PYTANIA OTWARTE — czekają na rozstrzygnięcie Cezara (zapisane 2026-08-03 na rozkaz)

> Powód zapisu: pytanie zadane w rozmowie i nieutrwalone **ginie** — to ta sama klasa,
> co 375 wizji bez werdyktu. Każde ma mieć albo odpowiedź, albo widoczny status.

| # | Pytanie | Kontekst zmierzony | Stan |
|---|---|---|---|
| **P-01** | **Stos dashboardu PRAETORIUM: Dart/Flutter/Wasm czy to, co już mamy (HTML+JS)?** | materiał `wrzutnia/Dart-WebAssembly-components.md` (3495 linii, 168 KB, 83 adresy) opisuje budowę dashboardu w Dart/Wasm — to **nowy język i cały nowy stos** w Imperium Pythonowym. Rekomendacja Architekta: HTML+JS, zero nowych zależności | ⏳ **OTWARTE** |
| **P-02** | **Repozytorium publiczne czy prywatne?** | DeepSeek **czytał nasz kod z GitHuba i cytuje go** znacznikami `[reference:N]`; zweryfikowane pomiarem: 4 z 5 liczb plików w organach dokładne, piąta nieaktualna o jeden dzień. Wcześniejszy zamiar Cezara („push po repo → private") nigdy nie został wykonany | ⏳ **OTWARTE** |
| **P-03** | **Sąd VERITAS nad materiałem Dart/Wasm** — kiedy i w jakim zakresie | VIATOR gotowy (55 testów) na 83 adresy; destylat techniczny osobno. Materiał zawiera też **mockup dashboardu w stylu rzymskim** — wprost dotyka zamówienia Cezara z 02.08 (żywy schemat Imperium) | ⏳ **OTWARTE** |
| **P-04** | **Czy LUSTRUM wchłania „strażnika obcych plików"** (pomysł Cezara 28.07) | 82 pliki we wrzutni; strażnik miał **kierować do kwarantanny, nie kasować** — to ta sama doktryna „nigdy nie kasuj sam", więc kandydat na jeden organ zamiast dwóch (Prawo XVI) | ⏳ **OTWARTE** |

### WACHTA H — DOMYKANIE PĘTLI *(kolejność = rekomendacja po skanie Imperium 2026-08-02)*

> **Diagnoza ze skanu całego Imperium (rozkaz Cezara 2026-08-02, liczby z żywych źródeł):**
> Imperium ma **znakomite wykrywanie i budowanie, a słabe ZAMYKANIE**. ROADMAP: 51 z 61
> pozycji otwartych (84%). Rejestr wizji: **367 bez rozstrzygnięcia** (256 POMYSŁ + 111
> PLANOWANE), najstarsze z **30.06** — 34 dni. Wrzutnia: 82 pliki. Hyginus: 35 cząstek
> bez sędziego. Jedyna kategoria BEZ długu: TODO/FIXME w kodzie ≈ **0** (13 trafień to
> `HACK` jako typ zdarzenia rynkowego).
>
> **⚠️ SPROSTOWANIE W TRAKCIE SKANU (Prawo I — kłamał mój przyrząd, nie system):** pierwszy
> przebieg zgłosił „55 sugestii, ZERO zamkniętych, `zamknij_sugestia()` nigdy nie wołana".
> **Było to FAŁSZYWE** — skaner filtrował status `ZAMKNIETA` (końcówka żeńska), a ledger
> zapisuje `ZAMKNIETE`. Prawda z ledgera: 55 rekordów = **45 unikalnych sugestii**, statusy
> `ZAMKNIETE` 8 · `ZREALIZOWANE` 2 · `ZABLOKOWANE` 1 · `CZESCIOWO` 1 · `STALE` 1 ·
> `OCZEKUJE decyzji Cezara` 2 · `KANDYDAT` 40; dziesięć elementów ma po dwa rekordy, czyli
> **mechanizm zamykania działa i był używany**. Otwartych realnie **35**. Wniosek o słabym
> zamykaniu zostaje w mocy (35 otwartych, najstarsze z 18.07), ale jego uzasadnienie jest
> słabsze, niż brzmiał pierwszy alarm — i tak ma być zapisane.

| # | Zadanie | Stan | Dlaczego w tej kolejności |
|---|---|---|---|
| H0 | **VERITAS — sąd nad `Imperium-Botów-Tradingowych 1.md`** (wrzutnia): ocena wszystkich wersji, **sprawdzenie KAŻDEGO linku, repo i propozycji** | 🔴 **ROZKAZ CEZARA — pierwsze zadanie następnej wachty** | Skala ZMIERZONA przed przyjęciem: wersja rozszerzona ma **13 820 linii / 842 KB / 230 unikalnych linków** (poprzednia: 7 267 linii / 452 KB / 141). Nie mieści się w jednej turze → **partiami, z paskiem postępu i wznawialnie** (Prawo XXIV: nigdy jeden wielki blokujący bieg). Kolejność: (1) narzędzie sprawdzające linki wsadowo (HTTP), bo 230 ręcznie to szaleństwo i błąd metody; (2) klasyfikacja propozycji na „mamy / nie mamy / obalone"; (3) sąd VERITAS wg zasady **kandydat ≠ prawda** (zmierzone: 39,3% kandydatów Hyginusa twierdziło „nie dubluje" o rzeczy stojącej w kodzie) |
| H1 | **35 otwartych sugestii CODEX — przejść i zamknąć** istniejącą `zamknij_sugestia()` | 🔴 **REKOMENDACJA #1 po H0** | domyka pętlę **bez pisania ani linijki nowego kodu**. Domykanie jest dziś naszą słabą stroną (ROADMAP domknięty w **16,2%** — pomiar MATURITASA), a A10 to duże zadanie, które lepiej zaczynać z czystą kolejką |
| H2 | **Warstwa audytu: „sugestia bez werdyktu starsza niż N dni"** | 🔴 | uodpornienie przeciw KLASIE, nie łatanie objawu — inaczej kolejka odrośnie (zasada CENSORA) |
| H3 | **A10 — zbiór ewaluacyjny z 13 729 haseł** | 🔴 **klucz do całego piętra grafowego** | odblokowuje G4 (graf przy decyzji), A14 (wektory) i domyka K10 w NORMIE. **Bez niego nie ma czym zmierzyć, czy graf pomaga** |
| H4 | **367 wizji — sąd nad kolejką** (256 POMYSŁ + 111 PLANOWANE) | 🔴 | największy zbiornik niedomkniętych pętli. Uwaga metodyczna: to NIE 367 zadań — rejestr miesza pomysły surowe z planami, więc pierwszym krokiem jest rozdzielenie, nie ocenianie |
| H5 | **35 cząstek Hyginusa bez sędziego** | 🔴 | zapłacony zwiad bez werdyktu (Prawo XV) |
| H6 | **VINDEX → graf W8** — krawędzie `(plik) —[naruszenie]→ (commit)` zbierane do grafu | 🔴 | organ od 02.08 **produkuje** krawędzie, których nikt nie zbiera. Tania droga na graf, niezależna od A10 |

### WACHTA G — dług recenzji i piętro pętli *(zaczęta 2026-08-02, kolejność = rekomendacja)*

> Powstała z sądu nad recenzją cubic PR #138 (20 uwag: 18 słusznych, 1 odrzucona, 1 odłożona)
> oraz z pytania Cezara o **etap inżynierii**. Zmierzony stan: jesteśmy głęboko w **LOOP
> ENGINEERING** (5 hooków, bramka 24 warstw, SIGILLARIUM, EXACTOR czytający własny meldunek,
> Księga Wad), a **GRAPH ENGINEERING mamy w zalążku** — graf W8 (234 węzły, 1680 połączeń)
> karmi raport startowy i `zapominanie.py`, ale **nie wnioskowanie**; RAG jest leksykalny (FTS).
> Zastrzeżenie: nasza ścieżka decyzyjna handlowa **nie zawiera LLM-a**, więc graf poprawia
> pamięć Imperium i pracę Architekta — **nie wynik tradingowy**. Mylenie tych dwóch rzeczy
> byłoby tym samym rozkalibrowaniem, które złapaliśmy przy frazach P1 zwiadu.

| # | Zadanie | Stan | Dlaczego w tej kolejności |
|---|---|---|---|
| G1 | **P1 recenzji** — E3 (`\S+` łyka separator w nazwie gałęzi), E5 (spacje w ścieżce łamią `cd`), D2 (pomiar gubi ostatni zamknięty bar), D4 (ujemne `od` przyjmowane) | ✅ **2026-08-02**, +9 testów granic, mutacja **5/5** złapanych | Domknięte wraz z **piątą wadą znalezioną dopiero realnym użyciem**: pasek postępu szedł na `stdout`, więc `--json` był niesparsowalny — organ psuł własny wydruk, a testy tego nie widziały, bo czytały funkcje, nie CLI.<br>**POWTÓRKA WYKONANA:** 441 kroków zamiast 440, `X-05 ↔ XII-02` **r = 0,8218** vs baza **0,8217** — werdykt NIEZMIENIONY (17 skupisk / 125 par / 1 kandydat / 27 milczących / 0 awaryjnych). D2 usuwa KLASĘ, nie zmienia wniosku o składzie roju.<br>**Kalibracja EXACTORA nienaruszona:** A/B starych i nowych wzorców na 76 meldunkach kroniki z `git push` — **zero** zmienionych werdyktów. ⚠️ E3 **nie miał historycznej ofiary** (5 wystąpień `<gałąź>;` siedzi po `{` w pętli retry, poza pozycją polecenia — niewidoczne dla OBU wzorców), więc naprawa jest prewencyjna, potwierdzona mutacją, nie retrospektywna |
| G1b | **VINDEX — obrońca zapisu** (poza pierwotną kolejką: rozkaz Cezara „watchdog", zakres B) | ✅ **2026-08-02**, 18 testów, commit `b0b986c` | Powstał z pytania Cezara o watchdog, które odsłoniło lukę większą niż samo pytanie: **kontrakt append-only deklarowany w 6+ organach, egzekwowany przez ZERO mechanizmów**. Kontrakty ustalone KALIBRACJĄ na 883 commitach (ŚCISŁY / KORYGOWALNY / MUTOWALNY), odzywalność **2,0%**, recall 3/3 na znanych korektach. Załatana druga luka: matcher VIGILA nie obejmował powłoki, więc plik tworzony komendą był niewidzialny → hook `PostToolUse: Bash\|PowerShell`. Granica JAWNA: ACTA `.md` poza miarą liniową (dałaby 330 fałszywek na 379 commitach `LOG_ZMIAN`) |
| G2 | **F17 — pole `WYMAGA`/`ZRODLO` w neuronach** | 🔴 | **decyzja Cezara z 2026-07-31**, wyprzedzona przez recenzję. Usuwa CAŁĄ KLASĘ niewiedzy zamiast 27 pojedynczych przypadków: dziś żaden organ nie odróżni „milczy z braku wejścia" od „milczy, bo zepsuty". Nazwa musi być rozłączna z istniejącym `WYMAGA_BAROW` u zwiadowców.<br>➕ **ROZSZERZENIE zmierzone 2026-08-02:** `MECHANIZMY_ZWIADOWCY` (12 wpisów) ma **ZERO czytelników** w całym repo, `_wstrzyknij_mechanizm` obsługuje wyłącznie neurony, a EXP-13/14/15 nie mają wpisu wcale — więc **DISCRIMINATOR i dekorelacja mechanizmowa nie obejmują ani jednego z 15 zwiadowców** (alarm Prawa XV) |
| G3 | **Reguła behawioralna z recenzji — automat** (praca `2607.13091`, Microsoft, wrzutnia 01.08) | 🔴 | domyka pętlę, którą dziś zamykam RĘCZNIE: zaakceptowana uwaga → trwała reguła. Mamy Księgę Wad, ale wpis robi Architekt. To jest właściwy następny krok **loop engineeringu**, nie graf |
| G4 | **Graf pamięci czytany PRZY DECYZJI, nie tylko drukowany** | 🔴 | pierwszy realny krok w **graph engineering**: pytanie → sąsiedztwo w W8 → dopiero potem FTS. Wpięcie **opt-in OFF**, walidacja **A/B na zbiorze A10** (RAG sam vs RAG + sąsiedztwo). Bez A10 nie ma czym mierzyć → G4 **czeka na A10** |
| G5 | **Sąd nad grupą B — 10 prac o grafach wiedzy** (wrzutnia 01.08: Disco-RAG, KAG, ROGRAG, GroundedKG-RAG, agentic KG-RAG/MIT, LLMs+Graphs, Context Graphs, ARIA, swj3854, HuixiangDou) | 🔴 | **kandydaci, nie plan** (zmierzone: 39,3% kandydatów Hyginusa twierdziło „nie dubluje" o rzeczy stojącej w kodzie). Pytanie brzmi „co dokłada się do W8, które STOI", nie „czy grafy są dobre" |
| G6 | **E4 — kalibracja kroku 4b EXACTORA** (meldunek sług przechodzi przy JEDNEJ nazwie) | ⏸️ | zarzut recenzji **trafny**, ale powinność jest NIESKALIBROWANA. Zaostrzenie progu bez prawdy podstawowej to dokładnie to, za co powstał talar N-b74ce133. Wymaga pomiaru na korpusie 190 meldunków, nie zgadywania |
| G7 | **CUSTOS LIMINIS — treść heredoca czytana jak polecenie** | ⏸️ ŚWIADOMIE ODŁOŻONE | strażnik **miał rację**: zawartość heredoca JEST częścią komendy Bash. Wyłączenie jej otwiera realny wektor obejścia (`bash <<EOF` zawartość wykonuje). Koszt fałszywki zmierzony: 1 tura; obejście istnieje. **Reguła operacyjna zamiast kodu:** pliki o treści shell-podobnej pisz narzędziem `Write`, nigdy heredocem |

### WACHTA A — domknięcie biblioteki *(zaczęta 2026-07-29)*

> **📚 PRZYROST KSIĘGOZBIORU ZMIERZONY 2026-08-02 (rozkaz Cezara) — i DOWÓD na potrzebę watchdoga.**
> Cezar dograł **40 nowych ksiąg 2026-08-01** (`BIB-206..245`, ciągły blok, wszystkie zgodne
> ze schematem nazw i z naszą listą: DeFi 206–211 · prognozowanie/osąd 212–221 ·
> ekonofizyka i złożoność 222–231 · inżynieria systemów 232–245).
>
> | Warstwa | Stan 2026-07-28 (dokument) | **Stan ZMIERZONY 2026-08-02** | Δ |
> |---|---|---|---|
> | Pliki BIB na dysku | 209 | **248** (1 852 MB) | **+39** |
> | W katalogu metadanych | 115 | **115** | 0 |
> | W cache tekstu | 117 | **118** | +1 |
> | Wyszukiwalne w RAG | 115 | **115** (37 331 fragm.) | **0** |
> | **POZA RAG** | 92 | **133 (53,6% zbioru)** | **+41** |
>
> **NIKT tego nie zauważył przez dobę** — audyt drukował „pełna harmonia", bo **żadna z 24 warstw
> nie pilnuje księgozbioru** (W11 dotyczy `imperium/biblioteki/`, czyli modułów kodu, nie ksiąg).
> To ta sama klasa co kontrakt append-only: **rzecz deklarowana w dokumencie, egzekwowana przez
> zero mechanizmów**. Dokument sam się przedawnił w 4 dni. Stąd A15 (watchdog) przed A7 (nadrobienie):
> **najpierw mechanizm, potem nadrabianie** — inaczej za tydzień znów będziemy liczyć ręcznie.
>
> **Wpływ na doktrynę LOOP/GRAPH:** 133 księgi poza RAG to **otwarta pętla o największej masie**
> w Imperium (53,6% zapłaconego zasobu bezużyteczne dla Hyginusa i QUAESITORA). Zarazem indeksy
> tych 133 ksiąg **karmią A10** (zbiór ewaluacyjny), a A10 odblokowuje **całe piętro GRAPH** (G4,
> A14, K10). Domykanie tej pętli jest jednocześnie otwieraniem drogi na graf — dokładnie kryterium
> z rozkazu 2026-08-02.

| # | Zadanie | Stan | Dlaczego teraz |
|---|---|---|---|
| A1 | **AESTIMATOR** — pomiar wierności korpusu + kalibracja | ✅ 14 testów | dał liczby, na których stoi cała reszta wachty |
| A2 | **REDDITOR** — fragmentacja z dowodem SHA-256 | ✅ 18 testów, 118/118 bajt-w-bajt | struktura 1 479 710 linii → **zachowana** (było 0) |
| A3 | **NORMA** — węgielnica 10 kryteriów | ✅ 12 testów, 9/10 zielonych | K10 celowo NIEZNANE — blokuje słowo „najlepsza" |
| A4 | **QUAESITOR — pierwszy bieg, domknięcie K10** | 🟡 **uruchomiony 2026-07-30, 19 testów** — K10 nadal NIEZNANE | pierwszy bieg dał naprawę u źródła (sanityzacja FTS w `szukaj.sanityzuj_fts`, ścieżka MCP recall@5 **16,7% → 80,0%**), ale K10 wymaga zbioru z A10 — 30 pytań to 0,22% zawołań |
| A5 | **OCR na BIB-007 (AFML)** — 93 listingi kodu jako obrazy | ⏸️ WARUNKOWE (po A11) | najbardziej wykonalna treść w najważniejszej książce ilościowej; ~30–40 min przy 5,2 s/stronę |
| A6 | **Przepięcie indeksu na REDDITORA** + reindeksacja | 🔴 | **dopiero po zielonym K10** (ZASADA WPIĘCIA: opt-in, po dowodzie) |
| A7 | **133 książki poza indeksem** → ekstrakcja → cache → indeks → **fragmentacja** | 🔴 **liczba PRZEMIERZONA 2026-08-02: było 91/92, jest 133** | rozkaz Cezara. Zakres urósł o **41 pozycji w 4 dni** (40 dogranych 08-01 + BIB-136/155 z OCR). Wykonanie **partiami z paskiem postępu** (Prawo XXIV) — 133 pozycje × ekstrakcja to nie jeden bieg. Po ekstrakcji **REDDITOR** (A2) daje fragmenty z dowodem SHA-256, więc podział na fragmenty jest już ROZWIĄZANY, nie do wymyślania |
| A15 | **CUSTOS BIBLIOTHECAE — watchdog księgozbioru** (warstwa audytu W25) | 🔴 **ROZKAZ CEZARA 2026-08-02, PRZED A7** | **Dowód konieczności zmierzony:** 40 ksiąg przybyło 08-01, dokument mówił „209 plików / 92 poza RAG", prawda to „248 / 133" — a audyt 24 warstw drukował **pełna harmonia**. Żadna warstwa nie pyta o KSIĘGI (W11 pilnuje modułów kodu). Kontrakt: dysk ↔ `katalog_ksiag.json` ↔ `tekst_cache/` ↔ `baza_wiedzy.db` **muszą się zgadzać**, rozjazd = alarm z listą ID. Ta sama klasa co VINDEX: rzecz deklarowana w dokumencie, egzekwowana przez zero. **Uodpornia przeciw KLASIE** (zasada CENSORA), zamiast nadrabiać ręcznie po każdej dostawie Cezara |
| A16 | **Analiza 40 nowych pozycji BIB-206..245** — sąd nad treścią + edycja dokumentacji | 🔴 **po A15/A7** | wg wzorca z BIBLIO28: AESTIMATOR mierzy wierność (w tym **A13 — kryterium języka**, bo BIB-011 przeszedł jako „OKROJONA" przy 100% straty użyteczności), potem wpis do `PLAN_ROZBUDOWY_BIBLIOTEKI.md` + `katalog_ksiag.json`. **Nie „wygląda dobrze" — POMIAR** (`unikalne słowa`, nie długość: lekcja z 07-28). Blok 232–245 (inżynieria: Kleppmann, Fowler, Nygard, SRE) jest osobno cenny — to korpus dla **naszych własnych** decyzji architektonicznych, nie dla tradingu |
| A8 | **R2 — fuzja RRF** zamiast sortowania po mieszanych skalach | 🔴 | mina latentna w Księdze Wad; wybuchnie w dniu włączenia wektorów. **Potwierdzone niezależnie z zewnątrz** (sąd 07-30, poz. F2) — RRF+cross-encoder jest standardem produkcyjnym, nie naszym wynalazkiem |
| A9 | **R3 — 3 gotowe książki + korpus `docs` (305 plików)** | 🔴 | dwa polecenia, zero ryzyka. Kandydat bez dowodu (MARK 2506.23026, praca **bez własnych pomiarów**): korekty wchodzą do korpusu retrievalu i **przebijają źródło** — u nas INDEX FALSORUM i lekcje miałyby wygrywać z książką, gdy się z nią kłócą |
| A10 | **Zbiór ewaluacyjny z INDEKSÓW książek** — 13 729 haseł wyliczonych przez samych autorów | 🔴 | zmierzone: zbiór QUAESITORA to 30 pytań = **0,22%** zawołań zadeklarowanych w indeksach (42/118 książek ma użyteczny indeks, ~326 haseł na książkę). K10 na takiej próbce jest liczbą bez mocy. Prawda podstawowa **napisana przez autora**: zero tokenów, zero halucynacji.<br>🔧 **PROJEKT SKORYGOWANY 07-30 (VeNRA §5, decyzja Cezara):** podział **po RODZINACH, nie losowy**. Rodzina = hasło + wszystkie pytania z niego pochodne + warianty z tej samej książki. Losowy podział 80/10/10 na zbiorze z rekordami pochodnymi **gwarantuje wyciek** (rodzic w treningu, dziecko w teście → metryka zawyżona, **niewykrywalnie**). Dodatkowo: zachować **pary kontrastowe** w zbiorze testowym, by liczyć **Flip Rate** (czy przyrząd ODWRACA werdykt pod minimalną perturbacją) — sama trafność tego nie pokaże |
| A11 | **Podmiana BIB-007 (AFML)** na wydanie z TEKSTOWYM kodem | 🔴 Cezar podmienia | 93/94 listingi to obrazy + wstrzyknięte stopki watermarku w indeksie. Próg przyjęcia: `listingi_z_kodem` > 1/94 (mierzy AESTIMATOR). **Udana podmiana usuwa A5 z planu** — OCR kodu jest podstępny (`l`/`1`, `O`/`0` cicho zmieniają znaczenie) |
| A12 | **Podmiana BIB-011 (Chan)** na wydanie angielskie | 🔴 Cezar podmienia | **85,6% znaków to CJK** — chińskie tłumaczenie. Nie uszkodzone, lecz NIEOSIĄGALNE naszymi zapytaniami: 152 tys. znaków martwego balastu w indeksie. Jedyna taka pozycja na 118 (przeskanowano cały korpus) |
| A13 | **AESTIMATOR: kryterium JĘZYKA** (siódmy wymiar) | 🔴 | luka odsłonięta pytaniem Cezara: BIB-011 przeszedł jako „OKROJONA", choć strata użyteczności wynosi 100%. Przyrząd mierzy sześć wymiarów i nie mierzy tego, w jakim języku jest tekst. ~20 linii + test granicy |
| A14 | **Wektory — jako WNIOSKODAWCA za bramką leksykalną, nie zamiennik FTS** | 🔴 **kształt skorygowany, zanim cokolwiek napisano** | Dotąd „wektory" wisiały w planie jako *następny krok po K10* bez określonej roli. **VeNRA §3.4 podaje przyczynę i lekarstwo:** gęste embeddingi **zlepiają terminy matematycznie przeciwne** („Net Income" vs „Net Sales" / „Net Loss"), bo stoją w identycznym kontekście językowym — *distributional semantic conflation*, wskazana jako źródło kaskadowych błędów; wymieniają `bge-m3` wprost. Ich lekarstwem **nie jest** rezygnacja z wektorów, ale **deterministyczna bramka leksykalna**, którą każdy kandydat wektorowy musi przejść przed wejściem do kontekstu.<br>**Zbiega się z naszym pomiarem 07-30 z drugiej strony:** FTS/BM25 (OR + odsiew słów pustych) dał recall@5 **80,0%**, a luka słownikowa to **+40,0 pp**. Wniosek: w domenie technicznej **leksyka jest sędzią, wektor wnioskodawcą**. Warunek wejścia: po A10 i A8, opt-in OFF, A/B na zbiorze rodzinowym |

### 🐎 ZWIAD ZEWNĘTRZNY (GitHub, 2026-07-29) — znaleziska wg WAGI

> **Status: KANDYDACI, nie prawda.** Każdy wymaga pomiaru u nas przed wdrożeniem.
> Oznaczenia zwiadowcy: `[KOD]` = czytał implementację, `[OPIS]` = tylko README/tytuł.
> **`↗` = ścieżka w CUDZYM repozytorium** — istnieje, ale nie u nas (marker rozumiany przez Warstwę 16).

| Waga | Znalezisko | Gdzie | Co nam daje |
|---|---|---|---|
| 🥇 **1** | **Testy NIEZMIENNIKÓW księgowych** zamiast wartości z pamięci: brak transakcji ⇒ equity stałe; `\|(kapitał+ΣP&L) − wartość_końcowa\| < 1e-9` | ↗ `ml4t/backtest` → `tests/contracts/test_ledger_invariants.py` `[KOD]` | **Rozwiązuje WACHTĘ B**: przyrząd sprawdzany prawem zachowania, nie liczbą z pamięci. Zero zależności, tanie na CPU |
| 🥈 **2** | **Look-ahead przy agregacji interwałów** — wskaźnik wyższego TF liczony z niższych barów potrafi przeciekać przyszłość okresu | `vectorbt` issue #101 `[KOD/treść]` | 🚨 **DOTYCZY NAS WPROST** — mamy `mtf_konfluencja` 1m→1H→4H. Podejrzenie o realną wadę w produkcji, do SPRAWDZENIA POMIAREM |
| 🥉 **3** | **HRP / HERC** — odległość kątowa `sqrt(0.5*(1−corr))` → klaster hierarchiczny → rekurencyjna bisekcja wag | ↗ `skfolio` → `optimization/cluster/hierarchical/_hrp.py`, `_herc.py`, `utils/tools.py#L623` `[KOD]` | Skorelowana rodzina sygnałów dzieli **jedną pulę wagi klastra** — kolejny skorelowany głos jej nie zwiększa, tylko rozcieńcza. Wprost pod nasze 87 neuronów i Prawo XVI. numpy/scipy, unosi 4 wątki |
| 4 | **Golden values w regresji** — słownik `ExpectedStatistics` przy algorytmie, porównanie string-po-string | ↗ `QuantConnect/Lean` → `Algorithm.CSharp/BasicTemplateAlgorithm.cs#L93` `[KOD]` | Zmiana silnika psująca Sharpe o 0.001 czerwieni test. Uzupełnia (nie zastępuje) niezmienniki z poz. 1 |
| 5 | **Warstwowe modele wypełnienia** (`TwoTier`/`ThreeTier`/`VolumeSensitive`) — głębokość księgi symulowana **z samego wolumenu świecy**, bez L2 | ↗ `nautilus_trader` → `backtest/models/fill.pyx` `[KOD]` | Pasuje do OHLCV z MEXC; zasila **D1/D3** (koszt egzekucji). ⚠️ auto-kalibracji poślizgu do realnych fillów **nie ma NIGDZIE** — definiujemy sami, jak przy rejestrze książka→moduł |
| 6 | **Parytet międzysilnikowy** — te same scenariusze w 4 silnikach, porównanie transakcja-po-transakcji | ↗ `ml4t/backtest` → `validation/` `[OPIS]` | Kosztowne (obce zależności) — do rozważenia dopiero po poz. 1 |

**🚫 OSTRZEŻENIE — nie tracić czasu:** publiczny `hudson-and-thames/mlfinlab` to **atrapa** —
metody mają ciała `pass` po komercjalizacji (zwiadowca sprawdził kod). Brać stamtąd **nazwy
koncepcji, nigdy implementacje**. Zwiadowca **nie znalazł** udokumentowanego przypadku „zły
annualizator" ani „survivorship bias" z numerem issue — i napisał to wprost zamiast zmyślać.

**Nowa pozycja z tego zwiadu:** → **B4. Sprawdzić `mtf_konfluencja` na przeciek przyszłości**
(klasa z `vectorbt` #101) — pomiarem, nie przeglądem kodu. Waga: wysoka, bo dotyczy ŻYWEJ
ścieżki decyzyjnej, a nie narzędzia pomocniczego.

> 🚨 **B4 PODNIESIONE 2026-07-30 — najwyższy priorytet WACHTY B.** Powód: **trzy niezależne
> prace, w trzech różnych domenach, wskazały tę samą klasę jako główny tryb awarii** —
> VeNRA (ugruntowanie w źródle), **Atkinson 2606.29280** (reguła *prefix-only*: stan zawiera
> tylko wiersze z `set_at ≤ t`, pole wyniku **nigdy** nie wchodzi do stanu), FinAbstain
> (*point-in-time*: „every evidence path is filtered by public availability at the decision
> timestamp"). **Atkinson podaje też ZMIERZONĄ MAGNITUDĘ**: w konfiguracji **z wyciekiem**
> XGBoost dawał **99,4–99,9%** wierności i DT 98,9%; **po usunięciu wycieku zadanie staje się
> realistyczne**. Czyli wyciek nie przesuwa wyniku o punkty — **fabrykuje niemal doskonałość**.
> Wzorzec do naśladowania: protokół **LEAP** (obcięcie po cutoffie PRZED joinami i agregacją)
> + audyt proweniencji cech. To samo prawo stoi za korektą A10 (podział rodzinowy).

---

### 🔎 SĄD NAD MATERIAŁEM ZEWNĘTRZNYM (DeepSeek web-czat, 2026-07-30)

> **Materiał:** `wrzutnia/Imperium-Botów-Tradingowych.md` — 7 267 linii / 452 KB, rozmowa
> Cezara z web-czatem DeepSeeka 02:24–11:09. Przeczytany w całości blokami, każde nośne
> twierdzenie zderzone z KODEM albo z SIECIĄ.

**⚠️ OSTRZEŻENIE METODOLOGICZNE — czytaj przed użyciem czegokolwiek z tego materiału.**
Ten dokument **nie jest audytem zewnętrznym, lecz echem**. Dowody:
1. Model oświadczył „czytam wprost z repozytorium — bez wymyślania" (l. 1797), a **5 minut
   później** napisał „nie mam bezpośredniego dostępu do Internetu" (l. 1932).
2. Jego „stan faktyczny Z KODU" to **przepisanie naszego `README.md`** — podane liczby plików
   per organ zgadzają się co do jednego z wstrzykiwanymi `<!-- LICZBA:organ_* -->`, w tym
   `biblioteki`=28 z chwili odczytu (dziś 29).
3. Reszta „stanu Imperium" to **nasza własna kronika**, wklejona do czatu (l. 2057–2957).

**Zgodność liczb NIE jest tu dowodem weryfikacji.** Wszystko, co pasuje, pochodzi od nas.

#### ✅ ZWERYFIKOWANE ZEWNĘTRZNIE — istnieje (sprawdzone 2026-07-30)

| Byt | Co realnie mówi źródło | Wartość dla nas |
|---|---|---|
| **VeNRA** — [arXiv 2603.04663v2](https://arxiv.org/abs/2603.04663), PDF w `wrzutnia/` | „Neuro-Symbolic Financial Reasoning via Deterministic Fact Ledgers…", Pedram Agand, FactAI Lab. **Przeczytana w całości** (13 686 słów, ekstrakcja naszym ekstraktorem). Ablacja **2×2** z **własnym wynikiem negatywnym** (Run 2: lepszy retriever **pogarsza** EM 39,2 → 37,4, gdy generator zostaje tekstowy), rozkład porażek per typ, wynik per benchmark | 🥇🥇 **NAJWAŻNIEJSZA POZYCJA CAŁEGO MATERIAŁU.** Nie dodaje funkcji — **koryguje kierunek dwóch zatwierdzonych zadań** (A10, A14) i wręcza metodę na dług, który sami nazwaliśmy najcięższym (F7 → WACHTA B). ⚠️ **Architekt ją PRZEOCZYŁ w pierwszym przebiegu sądu — wyłapał ją Cezar.** Zapisane jako lekcja: materiał był przeszukany pod „co proponuje", a nie pod „co obala nasz plan" |
| **OCC-RAG-1.7B** — [HF](https://huggingface.co/occ-ai/OCC-RAG-1.7B), [GGUF](https://huggingface.co/occ-ai/OCC-RAG-1.7B-GGUF), [arXiv 2606.00683](https://arxiv.org/abs/2606.00683) | mid-trenowany z **Qwen3-1.7B-Base**; cytuje dosłownymi cytatami; **wstrzymuje się, gdy kontekst nie wspiera odpowiedzi**. Licencja **MIT**, Q4_K_M **1,11 GB**, CPU-only na llama.cpp | 🥇 **najmocniejsze trafienie materiału** — ta sama rodzina i rozmiar co TIRO, mieści się na PEDES **bez Acera**. Wnosi zdolność, której nie mamy: abstynencję wypaloną w wagach, nie w prompcie |
| **HDRR** — [arXiv 2603.26815v3](https://arxiv.org/abs/2603.26815) | „Sustainable Hybrid Document-Routed Retrieval for Financial RAG"; routing **dokument → fragment**; benchmark FinDER; ~5–15K tokenów/zapytanie | 🥈 celuje w naszą zmierzoną **lukę słownikową +40,0 pp** (dosłowne 100% vs opisowe 60% @5) — **bez modelu i bez GB RAM-u**; `szukaj` ma już filtr katalogowy (nadpobiera ×20) |
| **MRC** — [arXiv 2605.24490](https://arxiv.org/abs/2605.24490) | kredyty **Shapleya** per reżim dla agentów; Sharpe **1,51**, 440,1% skumulowane, **1 037 dni, 13 kryptoaktywów** | 🥉 jedyna pozycja dotykająca ROJU. Nasze MWU przypisuje zasługę globalnie; `ucz_mwu` **zmierzone jako szkodliwe** (Δ −0,6 pp, PBO ~0,6, flaga OFF) → kandydat na następcę |
| **RAG-Anything** — [arXiv 2510.12323](https://arxiv.org/abs/2510.12323) | dual-graph, obrazy/tabele/wzory jako powiązane byty, X 2025 | celuje w **11 314 ślepych podpisów wykresów**, ale wymaga MinerU/Docling + modelu wizyjnego → **nie unosimy na PEDES** |
| **Fin-Analyst** — [arXiv 2607.12233](https://arxiv.org/abs/2607.12233) | 88% WR **na jednej spółce (TSLA)**, Sharpe 4,10, konkurs FinMMEval | ⚠️ **wyłącznie jako dowód, że liczba 88% nie dotyczy nas** — patrz INDEX FALSORUM niżej |
| **zembed-1 / zerank-2** — [ZeroEntropy](https://huggingface.co/zeroentropy/zembed-1-embedding) | `zembed-1-embedding`: **4B**, Apache-2.0, Matryoshka 2560→40, ~8 GB VRAM | ❌ **nie na PEDES** (brak CUDA); na Acerze 6 GB nie zmieści się razem z LLM-em — materiał sam to przyznaje i nie wycofuje rekomendacji |

#### ❌ ZWERYFIKOWANE — NIE ISTNIEJE / niesprawdzone

| Byt | Werdykt |
|---|---|
| **`fin-mini-v1`** („33,4M, +35% na parach finansowych") | **NIE ZNALEZIONY.** A była to jego rekomendacja **numer jeden** dla naszej warstwy embeddingów. Realne odpowiedniki, których **nie wymienił**: [FinE5](https://huggingface.co/FinanceMTEB/FinE5), benchmark [FinMTEB](https://huggingface.co/spaces/FinanceMTEB/FinMTEB) |
| `mist-reranker-22.7M`, `Merino-Nano/Small`, `Tarka-Embedding-250M`, `Harrier-Embedding-270M`, `MoonFinance v3.1`, `Amsi-fin-o1.5`, `Qwen3.5-4B`, InKH, FinanceComplexQA, RIDGE, NextRAG, TwinMarket, AlphaQuanter, QFinZero | **NIESPRAWDZONE** — ani „są", ani „nie ma". Żadnego z nich nie wolno użyć jako argumentu przed weryfikacją |

**Zmierzona trafność na próbce sprawdzonej: 6 z 7 nośnych bytów prawdziwych — a tym jednym
fałszywym była rekomendacja numer jeden.** To ta sama klasa co zmierzone 39,3% cząstek
Hyginusa pisanych jako „nie dubluje" o rzeczy stojącej w kodzie.

#### ⚠️ JAK MATERIAŁ PRZEKRĘCIŁ VeNRĘ — trzy przekłamania na jednej pracy

Ta praca jest w materiale **zakopana** jako „Filar 2, Sentinel może być TIRO" — czyli jako
jedyna rzecz, która się z niej **nie** przenosi. Przy okazji przekręcona trzykrotnie:

| Co materiał napisał | Co praca faktycznie mówi |
|---|---|
| „Redukuje halucynacje do **1,2%**" — postawione obok naszych „7,2%" | 1,2% to prawdziwa liczba, ale to **4,1% → 1,2%** ich pipeline vs **ich** baseline. Zestawienie z naszą sfabrykowaną bazą to porównanie z niczym |
| „**28× przyspieszenie** w porównaniu do modeli 70B+" | **Zlepione dwa osobne wyniki abstraktu.** 28× to *latency speedup z algorytmu treningowego Micro-Chunking*. Osobno: 3B Sentinel *bije 70B+ w detekcji błędów*. Dwa zdania → jedno |
| „**Zero-hallucination** financial reasoning" — podane jak sprawność | Zakopana liczba główna: **EM 49,1%** (baseline 39,2%); **37,4% pytań nie rozwiązuje ŻADNA konfiguracja**. „Zero halucynacji" znaczy tu **ugruntowanie, nie poprawność** — system ma być UCZCIWY, nie wszechwiedzący. To dokładnie nasze **bezstratność ≠ poprawność** |

**Czego w VeNRZE nie wiemy:** jeden autor, preprint v2, brak informacji o recenzji; EM pod 50%
na ich własnym benchmarku; wszystkie liczby na **angielskich sprawozdaniach 10-K**, gdy nasz
korpus to książki o metodzie, a zapytania są polskie. Progi **0,55 / 0,30 / τ=3000 / k=300** są
skalibrowane **na ich danych** — do przeliczenia u nas, **nie do skopiowania**. Zbioru
`pagand/venra` na HuggingFace **nie weryfikowano**.

#### 🚫 ODRZUCONE — z powodem

| Odrzucone | Powód |
|---|---|
| **Cała wieża „MEMOR-AGENT" 1.0→ULTIMA** ze szkicami patentu i tabelami Sharpe/WR | Stoi na (a) błędnym rozumieniu naszych 17 warstw (uznał je za hierarchię rynkową L1=tick…L17=meta; to pamięć SESJI W1–W13), (b) **sfabrykowanej bazie odniesienia**, (c) cudzych wynikach z jednej spółki przypisanych naszemu BTC 4H. Ani jednej liczby nie wolno zacytować |
| **„PRAWO XXVI — Porządek Kategorii"** + `docs/REJESTR_KATEGORII.md` + nowy audyt kategorii | **Mamy to poczwórnie:** CENSUS ORGANORUM (W17, 255 modułów zameldowanych) · TABULARIUM (katalog nadrzędny) · MANIFEST_KODU (Prawo XIX) · W20/W22 (jeden katalog) · NOMENCLATOR (strażnik imion). Piąty spis = złamanie Prawa XVI |
| **Nagłówki `WERSJA: 1.2.3 / HISTORIA:` w każdym pliku** | Duplikuje git i **gnije z definicji**. Dokładnie klasa wady, za którą zapłaciliśmy: runbook W11 kazał Architektowi `git push` 9 dni po zakazie, bo miał własną ręczną treść. Lek brzmi „odebrać dokumentowi prawo do własnej treści" — ta propozycja robi odwrotnie |
| Wzorce agentowe: TradingAgents, moon-dev, Fractal Debate, LangGraph, ChromaDB, Ollama | Mamy Senat, Legatusa, Bramę, arenę i llama.cpp. **Ollama odrzucona pomiarem 2026-07-16** |
| Kod z bloków I i V (szkielety bramy, senatu, „Lagustrata", organu pamięci) | Ciała `pass` rzeczy będących u nas w produkcji. „Lagustrat" to przekręcony **Legatus** |
| „7-dniowy plan zakończenia projektu, dzień 7 = wejście kapitałem" | Doradza kapitał systemowi, którego trafności retrievalu nie znał i którego P&L nigdy nie widział. **D1 nie znika przez terminarz** |

---

### 🚨 WACHTA F — adopcje i alarmy z sądu nad materiałem *(otwarta 2026-07-30)*

| # | Zadanie | Stan | Waga / warunek |
|---|---|---|---|
| **F0** | ✅ **ZROBIONE 2026-07-31 — organ DISCRIMINATOR** (`imperium/legiony/discriminator.py`, 17 testów, commit `5be5440`) | ✅ | **Zadanie okazało się inne, niż brzmiało.** Nie chodziło o „wydrukowanie listy": własny docstring `raport_mechanizmow` mówi, że skupisko to **kandydat do POMIARU korelacji**, przyrząd istniał, ścieżka bary→Brama→`interpretuj` też — a kandydaci **nigdy nie trafiali pod przyrząd**.<br>**Wynik (BTCUSDT 4h): 125 par, JEDEN kandydat do scalenia** `X-05 ↔ XII-02` r=0,82. **Teza o masowej redundancji NIEPOTWIERDZONA** — `T/trend` (8 neuronów, 28 par) ma 17 par poniżej progu dywersyfikacji. Stabilne na 6× większej próbce (r=0,81).<br>**Uboczne:** 27 z 66 neuronów milczy — nie z braku historii, tylko z braku wejścia (`RADAR-01` czyta `BTC_TREND`, nieznany Bramie przy jednej parze). → rodzi **F17** |
| **F17** | 🆕 **Pole `WYMAGA` / `ZRODLO` w neuronach — deklaracja wymaganych danych** (DECYZJA CEZARA 2026-07-31) | 🔴 **następne zadanie po powrocie** | **Luka strukturalna zmierzona przez F0:** neurony NIE deklarują w kodzie, jakich danych potrzebują (sprawdzone na K-03, K-04, X-05 — brak jakiegokolwiek pola). Skutek: **żaden organ nie odróżni „milczy z braku wejścia" od „milczy, bo zepsuty"**, więc każdy audyt martwych głosów (Prawo XV, pkt 1 checklisty) musi zgadywać. DISCRIMINATOR nazwał 27 neuronów `CISZA_W_POMIARZE` zamiast oskarżyć — poprawnie, ale to obejście, nie naprawa.<br>**Dlaczego to bije bieg z adapterami:** jedno działanie usuwa całą KLASĘ niewiedzy i uzbraja wszystkie przyszłe pomiary, zamiast rozstrzygać 27 przypadków raz.<br>**Zakres:** pole deklaratywne na `MikroNeuron` + wypełnienie dla rodzin (alt-dane, kontekst międzyrynkowy, czyste OHLCV) + warstwa audytu „neuron deklaruje dane, których Brama nie dostarcza" + wpięcie w DISCRIMINATOR, żeby cisza legalna była odróżniona od podejrzanej. Kandydaci pod lupę: `SMC-*`, `OC-*`, `PSY-01..04`, `Z-05`, `Z-06` (przyczyna ciszy NIEZMIERZONA) |
| ~~F0 (opis pierwotny)~~ | 🚨 `skupiska_redundancji` — wskaźnik LICZONY, ale przez NIKOGO nie czytany (Prawo XV, pkt 2 checklisty) | ✅ zamknięte | `raport_mechanizmow()` w `imperium/legiony/rejestr.py` grupuje neurony po `(KATEGORIA, MECHANIZM)` i zwraca `skupiska_redundancji`. **Zmierzone teraz: 17 skupisk** — m.in. `Z/risk_filter` **7 neuronów**, `T/trend` **8**, `R/regime` **6**, `R/mean_rev` **5 (całe PSY)**, `M/trend` **6**. `grep` po repozytorium: jedyne wystąpienia to własna definicja i test na obecność klucza. **Żaden audyt ani hook tego nie czyta.** Ironia: materiał proponował zbudować od zera organ, który u nas **stoi gotowy i milczy**. To właściwa odpowiedź na „PRAWO XXVI" — nie nowy rejestr, a wypuszczenie na wierzch tego, co już liczymy |
| **F1** | **OCC-RAG-1.7B jako baza TIRO** — A/B vs obecny Qwen3-1.7B | 🔴 czeka na decyzję Cezara o pobraniu pliku | **po A10** (bez zbioru nie ma na czym mierzyć). Opt-in **OFF**, wchodzi po zielonym A/B (ZASADA WPIĘCIA). Zysk celowany: abstynencja przy braku podstawy = Prawo I w wagach. ⚠️ **nie wiemy**, czy jest lepszy na polskich pytaniach o krypto — jego benchmarki są angielskie i ogólne.<br>**Dlaczego OCC-RAG BIJE budowanie Sentinela z VeNRY** (rozstrzygnięte 07-30): Sentinel wymaga ich zbioru VeNRA-Data, trenera Micro-Chunking i pełnego treningu — a nasza blokada uczenia TIRO **nigdy nie była sprzętowa, jest ToS**: nauczycielem może być wyłącznie DeepSeek, nie Architekt. OCC-RAG daje ~tę samą zdolność (cytowanie + abstynencja) jako **gotowy GGUF na MIT**. 3–4 tygodnie treningu vs pobranie 1,11 GB |
| **F2** | **HDRR — routing dokument → fragment** (dwustopniowy retrieval) | 🔴 | **po A10**, mierzone QUAESITOREM. Tanie: bez modelu, bez RAM-u, filtr katalogowy już istnieje. ⚠️ **nie wiemy**, czy działa na 118 heterogenicznych książkach — publikacja mierzyła jednorodne zgłoszenia regulacyjne |
| **F3** | **MRC — kredyty Shapleya per reżim** jako następca `ucz_mwu` | 🔴 | dotyczy ŻYWEJ ścieżki decyzyjnej → opt-in OFF, walidacja A/B jak każda zmiana wag. ⚠️ Shapley na 87 głosach jest kombinatoryczny — **na 4 wątkach wymaga aproksymacji**, do zmierzenia przed obietnicą |
| **F4** | **3 obalone twierdzenia → INDEX FALSORUM** | 🔴 | (1) „Sharpe 0,52 / WR 48% / MaxDD −18,4% / halucynacje 7,2% to baza Imperium" — **nigdy nie zmierzone**; 0,52 to dosłownie baseline z cudzej pracy. (2) „2 484 tabele nierozerwane" — zmierzone **294/294**, zawyżone **8,4×**. (3) „17 warstw pamięci = hierarchia rynkowa L1 tick → L17 meta" — to pamięć sesji, nie rynku |
| **F5** | **RAG-Anything — multimodalność na 11 314 ślepych podpisów** | ⏸️ **odłożone, nie odrzucone** | wymaga MinerU/Docling + modelu wizyjnego; wraca przy GPU albo przy decyzji o przetwarzaniu przez API |
| **F6** | **Rozliczyć obietnicę „RAG 53/100 → 85/100 po zmianie laptopa"** | 🔴 do policzenia | Materiał twierdzi, że sprzęt podnosi trafność RAG. **To nieprawda** — trafność zmienia RRF (A8), zbiór ewaluacyjny (A10) i routing (F2), nie VRAM. Acer realnie odblokowuje **QLoRA na TIRO** — ale blokada uczenia TIRO **nigdy nie była sprzętowa**: nauczycielem może być wyłącznie DeepSeek, nie Architekt (ToS). Do policzenia: co dokładnie daje 6 GB VRAM przy tej blokadzie w mocy |
| **F10** | 🥇 **ORACLE AKCJI + pomiar nadmiernego wchodzenia** — reguła hindsight na naszych barach | 🔴 **niezależne od A10** | **Atkinson 2606.29280** zmierzył *intervention bias*: oracle wskazuje **70,1%** przypadków bez interwencji, a GPT-4o działa w **73%** → **43 pp** fałszywych wejść; wszystkie ramiona LLM przepisują nadmiernie o **28–43 pp** i **wypadają poniżej klasy większościowej**. Ich oracle to **sześć linii `if`** liczonych niezależnie od jakiegokolwiek ramienia. U nas: definiujemy post factum optymalne wejście/wyjście na historycznych barach i mierzymy, **jak często rój wchodzi, gdy oracle mówi STÓJ**. Rozstrzyga zmierzoną, a nierozumianą zagadkę: **1h ma WR 50,6% i traci, bo straty > zyski**. Metryki z **FinAbstain 2607.24875** (eq. 6–7): `Cov(θ)`, **ryzyko selektywne** `Risk(θ)` (błąd tylko na przyjętych), **ECE**, risk–coverage area; próg θ dobierany **wyłącznie na walidacji**. Deterministyczne, nasze dane, **zero tokenów** |
| **F11** | 🚨 **Audyt PROBATORA i profilu `krytyka` na EVALUATION GAP** | 🔴 | Atkinson §1: ocena LLM-jako-sędzia (G-Eval, DeepEval, **RAGAS**) jest **strukturalnie ślepa** na nadmierne przepisywanie — nagradza płynność i rozbudowanie, a zwięzłe **poprawne** `NO_ACTION` wypada **gorzej** niż pewne siebie błędne zalecenie. Nazywają to **inwersją rankingu**. U nas sędzią jest profil `krytyka → v4-pro/high`, a PROBATOR zbadał 10 cząstek i znalazł 2 podejrzane. Pytanie do pomiaru: czy nasz sędzia preferuje kandydata, który proponuje **więcej**. Wzmacnia F7 (kalibracja deterministyczna zamiast sędziego-LLM) |
| **F12** | **Nazwać stronniczość Hyginusa** — wpis do INDEX FALSORUM | 🔴 | Mamy ją **zmierzoną, a nienazwaną: 39,3% kandydatów** twierdziło „nie dubluje" o rzeczy stojącej w kodzie. To **intervention bias** proponenta: „dodaj neuron" zamiast „nic nie trzeba". Nota z **Arm G** Atkinsona, kluczowa: prompt zaprojektowany, by przeciwdziałać nadmiernej interwencji, **ODWRÓCIŁ stronniczość, a nie usunął** — system zaczął interweniować za rzadko. *„Prompt jest perturbacją rozkładu generowania tokenów, nie regułą deterministyczną."* **Wniosek: instrukcją w prompcie tego nie naprawimy** — tylko bramką liczoną poza modelem |
| **F13** | **Router bramkowany niepewnością** nad istniejącymi organami | 🔴 **opt-in OFF, tylko po zielonym A/B** | FinAbstain daje **cztery stopniowane odpowiedzi** zamiast dwóch: przewiduj / wstrzymaj się / **poproś o dowód** / **zredukuj ekspozycję** / oddaj człowiekowi. **Mamy wszystkie organy** — NEUTRAL, Gubernator (0,5×–1,3× to jest redukcja ekspozycji), Hyginus (dowód), Cezar (człowiek) — ale **nie mamy routera**, który wybiera między nimi na podstawie niepewności. Ich `U` (eq. 4) składa się z 6 członów z wagami dopasowanymi na walidacji; **mamy składniki** (`pewnosc_agregatu`, `zgodnych_neuronow`, `NEWS_ROZRZUT` = ich „contradiction"), nie mamy **skalibrowanego skalara**. Bonus: człon „niezgodność powtórzonych próbek" jest u nas **tożsamościowo zerowy**, bo rój jest deterministyczny — jeden z sześciu dostajemy darmo. **RUSZA ŚCIEŻKĘ DECYZYJNĄ** → ZASADA WPIĘCIA bez wyjątku |
| **F14** | **A/B kalibratorów pewności** — nasza konformalna ML-36 vs temperature scaling vs isotonic; policzyć **ECE** | 🔴 tanie | FinAbstain wymienia cztery metody jako kandydatów, w tym conformal prediction — **a my mamy `BramkaPewnosciKonformalna` (ML-36) wpiętą od 2026-07-05** z ACI podnoszącym próg po serii strat. **Tu jesteśmy przed stanem sztuki.** Czego nie mamy: temperature scaling i isotonic jako **zmierzonych alternatyw**, oraz ECE i risk–coverage w ogóle |
| **F15** | 🚨 **WRAPPER INFERENCJI TIRO** — Prawo XIX: organ nie istnieje | 🔴 **ukryta zależność F1** | Zmierzone 2026-07-30: `grep` po całym repozytorium za `llama-cli` / `llama-server` / `llama_cpp` → **zero trafień w kodzie**. Jedyne wystąpienia to `docs/PLAN_TIRO_LOKALNY_LLM.md`, `docs/ZADANIE_TIRO_E3_ZNIWO.md` i pliki kroniki. BREVIARIUM robi wyłącznie `katalog.glob("*.gguf")` — **melduje, że pliki leżą na dysku**. Czyli TIRO to dziś: 2 modele + 433 pary + meldunek o plikach; pomiar „1,7B = 9,6 t/s, 4B = 4,9 wsadowo" istnieje **poza repozytorium**, z ręki. **Wg Prawa XIX TIRO jako organ NIE ISTNIEJE** — i F1 (OCC-RAG jako baza TIRO) nie ma czym zrobić A/B, dopóki wrappera nie ma |
| **F16** | **N_eff / HHI — efektywna liczba głosów roju** | 🔴 ~15 linii, zero nowych danych | Z **SaR 2603.09164** (Sepper, ex-Gauntlet) — przełożone na NASZ problem, nie ich. Ich haircut koncentracyjny to czysta arytmetyka na wektorze udziałów: `HHI = Σ(share)²`, `N_eff = 1/HHI`, `CR1 = max(share)`, `h = 0.5·max(0, 15/N_eff − 1) + 0.3·max(0, CR1 − 0.5)`. Zmierzone: **nie liczymy niczego takiego w całym Imperium** (jedyne trafienie na „koncentracja" to komentarz w docstringu SMC-01). Pytanie, które to odpowiada: **87 neuronów głosuje — ale ilu głosuje EFEKTYWNIE?** Jeśli agregat jest zdominowany przez trzy, `N_eff` powie to liczbą. Prawo XVI i XXII z miernikiem zamiast opinii; **spina się z F0** (17 skupisk redundancji) |
| **F7** | 🥇 **ADVERSARIAL SIMULATION jako kalibrator WACHTY B** — sabotaż programowy zamiast etykiet z ręki | 🔴 **najwyższa waga w całym planie** | VeNRA §5 odrzucił szum generowany przez LLM na rzecz **programowego sabotażu złotych rekordów**: 8 320 rekordów z FinQA/TAT-QA/FinanceBench/TruthfulQA/PHANTOM, wyważone **51,3% SUPPORTED / 47,2% UNFOUNDED**. To **nasza własna lekcja „bramka sprawdzona mutacją" (7/8 wad złapanych), uogólniona i opublikowana**. Mamy **11 organów bez kalibracji, w tym 8 narzędzi A/B, których werdykty ustawiły skład roju** — a AESTIMATOR skalibrowano na **8 próbkach z ręki**. Sabotaż deterministyczny nie wymaga **ani jednej ręcznej etykiety, ani jednego tokena, ani GPU**. Najtańsza i największa spłata długu kalibracyjnego w naszym zasięgu. Metryka: **Flip Rate** — czy przyrząd odwraca werdykt pod minimalną perturbacją |
| **F8** | **REDDITOR: propagacja skali tabeli + drabina dopasowania + pewność/UNALIGNED** | 🔴 | (a) VeNRA §3.1 propaguje **ostatnie k=300 znaków poprzedniego bloku** jako prefiks następnego — powód podany wprost: **nagłówki tabel niosą kontekst skalarny („in millions")**, bez propagacji nie da się rozwiązać odniesienia. Mamy zakładkę 50 słów, ale **skali tabeli nie propagujemy**; zmierzone „294/294 tabele mają treść" **nie znaczy** „fragment wie, w jakiej jednostce" — ta sama klasa co bezstratność≠poprawność. (b) Trójstopniowa drabina dopasowania (dokładne → najdłuższy token liczbowy → okno przesuwne, **R > 0,55**) to maszyneria, której zabrakło oknom REDDITORA — 63,4% startów w pół słowa naprawiono ręcznie. (c) Fakt bez dopasowania dostaje **UNALIGNED, pewność 0,0, zakaz dalszego obiegu**; nasze fragmenty **nie mają pola pewności w ogóle** (znana luka: „brak warstwy pewności") |
| **F9** | **Nota projektowa: ortogonalne etykiety werdyktu** — ZANIM TIRO dostanie głowę klasyfikacyjną | 🔴 zapis, nie kod | VeNRA §5.1 zmierzył: etykiety `True`/`False` mają **cos ≈ 0,68** (wektory blisko siebie → warstwy uwagi muszą je rozdzielać), a zestaw `Found`/`Fake`/`General` **< 0,25**. Sprawdzone u nas: **433 pary TIRO są regresyjne** (`{"sentyment": 0.6, "pewnosc": 0.7}`), więc **dziś to nie gryzie** — ale zagryzie w chwili, gdy TIRO dostanie głowę werdyktu, czyli w **F1**. Zapisane teraz, żeby nie odkryć tego po treningu. Powiązane ostrzeżenie: **Loss Dilution / „Sycophant"** — przy 1 tokenie etykiety na ~150 tokenów uzasadnienia gradient werdyktu to **<0,7%**, model uczy się większościowej klasy i brzmi płynnie, mając losowy Flip Rate |

**Kolejność wobec planu:** **A10 → K10 bez zmian** — ale A10 wchodzi już w **skorygowanym
projekcie** (podział rodzinowy + Flip Rate), a „wektory" przestały być mgłą i mają kształt (A14).

F1/F2/F3/A14 to kandydaci DO ZMIERZENIA, a mierzyć ich nie ma czym, dopóki zbiór ewaluacyjny liczy
30 pytań (**0,22%** z 13 729 haseł) — każdy A/B dałby liczbę z zastrzeżeniem większym niż sama
liczba (LEX TALARUS).

**Dwa wyjątki, które NIE czekają na A10:**
- **F0** — zamyka alarm Prawa XV (organ gotowy, wypięty; ~30 min + test granicy).
- **F7** — kalibruje przyrządy **sabotażem naszego własnego korpusu**, więc nie potrzebuje zbioru
  z indeksów ani ani jednego tokena. Spłaca WACHTĘ B, którą sami nazwaliśmy najcięższym długiem.

**Zasada wyniesiona z tego sądu (do SCHOLA CAESARIS):** materiał zewnętrzny przeszukuje się
**dwoma pytaniami, nie jednym** — „co proponuje" ORAZ **„co obala nasz plan"**. Pierwszy przebieg
sądu 07-30 zadał tylko pierwsze pytanie i dlatego prawie wyrzucił VeNRĘ jako jedną z siedmiu
pozycji, gdy była jedyną, która **koryguje kierunek** (A10, A14) zamiast dokładać zadanie.

**Uwaga o wycieku kontekstu:** w bloku II materiału (l. 2057–2957) leży pełny transkrypt naszych
wacht wklejony do web-czatu — z architekturą, nazwami organów i **naszymi jeszcze niezałatanymi
minami** (mieszane skale w sortowaniu, lista 11 organów bez kalibracji). Kluczy API tam nie ma
(sprawdzone). To nie zarzut, lecz warunek oceny: jego „audyt" mógł wyglądać trafnie **wyłącznie
dlatego, że czytał nasze notatki**.

### WACHTA B — dług kalibracyjny przyrządów *(najcięższy dług Imperium)*

Zmierzone 2026-07-29: **47 organów orzekających, 11 bez testu kalibracyjnego.**

| # | Zadanie | Stan | Waga |
|---|---|---|---|
| B1 | **8 narzędzi A/B bez kalibracji** — `ab_dvol`, `ab_stablecoin`, `ab_usd`, `ab_w329`, `ab_w330_radar`, `ab_w334_progi`, `ab_w335_cross_rs`, `ab_w336_changepoint` | 🔴 | **najwyższa** — ich werdykty zadecydowały o składzie roju (PSY-05, K-03, K-04) |
| B2 | `audyt_danych` — przyrząd oceniający jakość danych wejściowych | 🔴 | ocenia to, czym karmimy rój |
| B3 | **Warstwa audytu: „organ orzekający bez kalibracji"** | ⏸️ odłożone rozkazem Cezara | zamienia jednorazowy przegląd w mechanizm |

### WACHTA C — kolejka zatwierdzona wcześniej przez Cezara

| # | Zadanie | Stan |
|---|---|---|
| C1 | **Sąd nad cząstkami Hyginusa** — stan kolejki czytaj z `python -m imperium.oczy.breviarium`; liczb NIE wpisujemy tu ręcznie, bo „kolejka 44 / osądzonych 8” rozjechało się w kilka dni (klasa „liczba rosnąca sama”) | 🟡 narzędzie jest, plon czeka |
| C2 | **ESSENTIA** — esencja = falsyfikowalna hipoteza, nie streszczenie | 🔴 kod nie istnieje |
| C3 | **Rejestr książka→moduł→werdykt** wg McLean-Pontiff (IC przed/po wdrożeniu) | 🔴 **brak prior artu — definiujemy sami** |
| C4 | **TIRO E3** — postęp par użytecznych wobec progu 1000 czytaj z `python -m imperium.oczy.breviarium` (wpisane tu „229/1000” było już nieaktualne) | 🟡 w toku |
| C5 | **INGENIUM** — IQ Imperium w 7 kategoriach | 🔴 projekt w docs, kod nie istnieje |

### WACHTA Ł — fronty, które decydują o ŁUPIE (nie o wiedzy)

> 🔤 **Przemianowana z „WACHTA D” 2026-08-05:** prefiks `D` znaczył w tym samym
> dokumencie DWIE różne rzeczy — pozycje tej wachty i pozycje REJESTRU DŁUGÓW
> (D1.1 = `hash_ok`, D1 = MEXC). Dwa znaczenia jednego klucza w jednym dokumencie
> to ta sama klasa co dwa organy liczące ten sam fakt (K1): rozjazd jest niewidoczny,
> dopóki ktoś nie zacytuje „D1” i nie trafi w drugie znaczenie.

| # | Zadanie | Stan | Uwaga |
|---|---|---|---|
| Ł1 | **JEDEN zamknięty obieg na realnych groszach (MEXC)** | 🔴 `MEXC_API_KEY` brak | **zero prawdziwych wypełnień w historii Imperium** — poślizg i prowizja są ZAŁOŻONE, nie zmierzone. Decyzja kapitałowa = wyłącznie Cezar |
| Ł2 | **Świeżość danych** — dryf per interwał melduje PORTITOR na starcie sesji; liczb nie wpisujemy ręcznie, bo wartości z 07-29 zdążyły się przeterminować | 🔴 zmierzone, niezałatane | rój głosuje na nieświeżych danych |
| Ł3 | **Kalibracja kosztu egzekucji na realnych fillach** | 🔴 | zależy od Ł1. **Zwiad 07-30 (SaR 2603.09164, Sepper/ex-Gauntlet) NIE domyka D3** — mierzy poślizg **likwidacji po stronie giełdy** (wielkość funduszu ubezpieczeniowego, wymogi kapitałowe), a nie to, ile zje NASZE małe zlecenie; **2 z 4 jego wejść są dla nas nieosiągalne** (pełne migawki L2 ≥1/min — mamy zero; atrybucja na poziomie kont — dostępna „on fully on-chain DEXs", a MEXC jest scentralizowana). Co się przenosi: forma `S ∝ 1/L` i legitymizacja **poślizgu ZALEŻNEGO OD STANU** zamiast stałej założonej. Odłożone do dnia wpięcia L2 |
| Ł4 | **Poślizg zależny od stanu zamiast stałej** — funkcja mierzalnych zmiennych (zakres, wolumen, zmienność) | 🔴 | Dziś poślizg i prowizja są **ZAŁOŻONE**, więc mogą odwracać znak wyniku strategii. Nie wymaga L2: nawet zgrubna funkcja tego, co mierzymy, jest **ściśle lepsza od stałej**. Prior art do wzięcia: warstwowe modele wypełnienia z `nautilus_trader` (poz. 5 zwiadu 07-29 — głębokość symulowana **z samego wolumenu świecy**) |
| Ł5 | **DR-OPE — oszacowanie zwrotu polityki BEZ realnych zleceń** | 🔴 | Z Atkinsona: *Doubly Robust Off-Policy Evaluation*, nieobciążony estymator oczekiwanego zwrotu, wagi IPS obcinane. **Odblokowuje pomiar tam, gdzie D1 stoi na braku kluczy MEXC i decyzji kapitałowej Cezara** — polityki nie trzeba wdrożyć, żeby oszacować jej zwrot. Do tego z tego samego źródła: **Temporal Degradation** (nachylenie wierności względem czasu) — mamy Prawo XXIII o trafności per reżim, ale **nachylenia nie liczymy** |

### WACHTA E — dług techniczny z zamrożonej listy

| # | Zadanie | Stan |
|---|---|---|
| E1 | `zip(strict=)` w Bramie · RUF012 · strażnik budżetu | 🔴 |
| E2 | WFO chunkowany (backtest liniowy ~66 ms/tik — premisa „kwadratowy" była błędna) | 🟡 |
| E3 | Strażnik obcych plików → wrzutnia/kwarantanna zamiast kasowania | 🔴 pomysł Cezara 07-28 |
| E4 | Dług kontekstu: CLAUDE.md ponad limit 200 linii — **liczbę podaje `python -m imperium.oczy.maturitas`** (piętro PROMPT). Wpisana tu „259” była nieaktualna o kilkadziesiąt linii: dokument opisujący dług kontekstu sam gnił | 🔴 rośnie z każdym rozkazem |

---

## ⚔️ ZASADA DRÓG

> *"Roma non fuit una die condita."*
> Rzym nie został zbudowany w jeden dzień.

**NIE budujemy wszystkiego naraz.**

Każdy moduł wchodzi najpierw do **Koloseum** (arena backtestingu) zanim trafi na żywy rynek. Zasada jest prosta i nienaruszalna:

```
BUDUJ → TESTUJ W KOLOSEUM → KALIBRUJ → WDRAŻAJ → ROZSZERZAJ
```

Żaden Legion nie idzie na pole bitwy bez przeszkolenia. Żadna strategia nie dotyka prawdziwego kapitału bez przejścia przez arenę.

---

## 🔄 FAZA 0 — Fundament *(UKOŃCZONA 2026-06-03)*

**Status:** ✅ Ukończona
**Cel:** Pierwszy działający cykl na prawdziwych danych z minimalnymi modułami

### Wymagania techniczne

| Wymaganie | Status |
|-----------|--------|
| TA-Lib zainstalowane na Windows 10 | Wymagane |
| `DEEPSEEK_API_KEY` w środowisku | Wymagane |
| Klucz API MEXC skonfigurowany | Wymagane (zweryfikowane) |
| Python 3.10+ | Wymagane |

**Uruchomienie:**
```bash
python imperium/legiony/pierwszy_zwiadowca.py
```

### Moduły aktywne w Fazie 0

| Moduł | Status | Opis |
|-------|--------|------|
| Kwatermistrz Danych | ✅ Aktywny | Pobieranie danych CCXT/MEXC |
| Brama Kalkulatora | ✅ Aktywna | Obliczenia wskaźników TA-Lib |
| Pierwszy Zwiadowca | ✅ Aktywny | EMA cross + RSI + ATR |
| Aegis Tarcza | ✅ Aktywna | Weto ryzyka — blokada złych sygnałów |
| Głos Imperium | 🟡 Częściowy | DeepSeek — wymaga testu klucza API |
| Titan Mind | 🟡 Częściowy | Podstawowa orkiestracja |

### Parametry operacyjne

- **Instrumenty:** BTC/USDT *(tylko)*
- **Tryb:** Paper trading ONLY — żadnego prawdziwego kapitału
- **Giełda:** MEXC (primary, verified)
- **Obliczenia ciężkie:** przez API, nie lokalnie (Fujitsu 15.88 GB RAM / 4 wątki / brak CUDA —
  klasa PEDES, zmierzone `censor_sprzetu.py`; ogranicza CPU i brak GPU, nie pamięć)

---

## ⚡ FAZA 1 — Namiestnik *(TERAZ — aktualna)*

**Status:** 🔄 W trakcie
**Cel:** Regime + Timeframe-Aware Gating Network — 62 neurony, 743 testy, master-switch Reżimu Faza 2

### Stan Fazy 1 (2026-06-12)

| Kamień milowy | Status |
|---------------|--------|
| 62 neurony w kodzie (58 aktywnych — SMC-01/02/03 odblokowane) | ✅ DONE |
| 743 testy automatyczne (0 zależności) | ✅ DONE |
| Namiestnik (Regime×Timeframe Gating) | ✅ DONE |
| Master-switch reżimu Faza 1 | ✅ DONE |
| Master-switch reżimu Faza 2 (online Hedge/MWU głosów reżimu) | ✅ DONE |
| BIB-015 Reguła 6% Elder (miesięczny circuit-breaker) | ✅ DONE |
| BIB-018 skew-Kelly (sizing skorygowany o fat tails) | ✅ DONE |
| BIB-020 (pomiar_dekorelacji tool) | ✅ DONE |
| Neurony Z-03/Z-04/X-27 | ✅ DONE |
| AdapterFutures + AdapterCVD + AdapterFearGreed | ✅ DONE |
| Paper Trading Engine (TP/SL/LIQ/MAE/MFE) | ✅ DONE |

### Dawne cele Fazy 1 (Legiony)

### Legiony — docelowy skład

| Legion | Specjalizacja | Aktualne neurony | Cel |
|--------|--------------|-----------------|-----|
| Legio X Equestris | Scalp (krótki termin) | ✅ aktywne | 15+ |
| Legio XII Fulminata | Swing (średni termin) | ✅ aktywne | 20+ |
| Legio III Augusta | Invest/Spot (długi termin) | ✅ aktywne | 15+ |
| Legio VI Ferrata | Dźwignia *(najniebezpieczniejszy)* | ✅ aktywne | 10+ |

### Pozostałe cele Fazy 1

- Debata Senatu w pełni operacyjna (**Populares** vs **Optimates**)
- Koloseum uruchamia równoległe backtesty na każdej nowej strategii
- **Cel łączny:** 79+ neuronów (jak system DNSS) — 62 z 79 zaimplementowane

### Parametry operacyjne

- **Instrumenty:** BTC + ETH
- **Tryb:** Paper trading → pierwsze żywe mikro-pozycje

---

## 👁️ FAZA 2 — Senat i Oczy *(3-6 miesięcy)*

**Status:** 📋 Zaplanowana
**Cel:** Pełny wywiad — oczy widzą wszystko

### Nowe moduły

| Moduł | Funkcja |
|-------|---------|
| Oczy / Wszechoko | Dane on-chain (Glassnode / CryptoQuant free tier) |
| Analiza sentymentu newsów | NewsAPI lub podobne |
| Social signal tracking | Whale alerts, Twitter/X, linki on-chain |
| Pełna debata Senatu | Z oceną pewności (confidence scoring) |
| MetaJudge | Śledzi, który agent był najdokładniejszy w czasie |
| LangFuse monitoring | Śledzenie kosztów wywołań DeepSeek |

### Parametry operacyjne

- **Instrumenty:** BTC + ETH + top 5 altcoinów wg wolumenu MEXC
- **Tryb:** Live trading *(małe pozycje, ≤2% kapitału na transakcję)*

---

## 🚀 FAZA 3 — Ekspansja *(6-12 miesięcy)*

**Status:** 📋 Zaplanowana
**Cel:** Multi-giełda, arbitraż, strategie samoewoluujące

### Nowe moduły

| Moduł | Funkcja |
|-------|---------|
| Integracja drugiej giełdy | Nowe możliwości arbitrażowe |
| Abordaż (moduł piracki) | Cross-exchange arbitraż — szybkie uderzenie i odwrót |
| Ewolucja strategii | System proponuje nowe kombinacje na podstawie wyników Koloseum |
| Macierz zdarzeń historycznych | Każda minuta BTC/ETH skorelowana ze zdarzeniami rynkowymi |
| Katalog Kostki Rubika | Wskaźniki × strategie × timeframy × Legiony = macierz probabilistyczna |

### Nowe instrumenty

- Nowe tokeny MEXC *(moduł wczesnego wejścia)*
- Rotacja altseason

---

## 🧬 FAZA 4 — Autonomia *(12+ miesięcy)*

**Status:** 📋 Przyszłość
**Cel:** Strategie samogenerujące się

> *"To jest faza Avatar/Eywa — system staje się świadomy własnych ślepych punktów."*

### Zdolności autonomiczne

- System **identyfikuje własne luki** (raportuje: *"Legio X jest ślepy na sygnał funding rate"*)
- **Auto-generuje** kandydatów na nowe mikroneurony
- **Testuje je w Koloseum** automatycznie
- **Promuje zwycięzców** do aktywnych Legionów
- Pętle ewolucji zamknięte — system ulepsza się bez ingerencji człowieka

---

## 📊 SYSTEM WERSJONOWANIA

| Wersja | Faza | Opis |
|--------|------|------|
| v0.x | Faza 0 | Paper trading, jeden instrument |
| v1.x | Faza 1 | 4 Legiony, 79+ neuronów |
| v2.x | Faza 2 | Oczy, pełny Senat |
| v3.x | Faza 3 | Multi-giełda |
| v4.x | Faza 4 | Autonomia |

**Aktualna wersja: v0.9.1** (62 neurony / 58 aktywnych, 743 testy, Namiestnik+Radar Opcja A+B, Paper Trading Etap II)

---

## 🏟️ ZASADA ARENY — Koloseum

> *Żadna strategia nie wychodzi z Koloseum bez krwi na rękach.*

Przed wejściem na żywy rynek każdy moduł musi przejść przez kolejne etapy w tej dokładnej kolejności:

### Etap I — Backtest historyczny  ✅ ZALICZONY 2026-06-11 (portfel 5 par: Sharpe 1.74, DSR 1.0, MaxDD 13.5%, PF 2.01)

| Kryterium | Minimum wymagane |
|-----------|-----------------|
| Długość backtestu | ≥ 30 dni na danych historycznych |
| Sharpe ratio | > 1.0 |
| Maksymalny drawdown | < 15% |
| Win rate | > 55% **LUB** Profit factor > 1.5 |

### Etap II — Paper trading

- Minimum **14 dni** na papierowym koncie po przejściu Etapu I

### Etap III — Live (mikro)

- Dopiero po Etapie II: wejście live z **≤ 0.5% kapitału**
- Monitorowanie przez minimum 7 dni przed zwiększeniem ekspozycji

**Nie ma skrótów. Koloseum jest sprawiedliwe.**

---

## ⚖️ ZASADA ZGODNOŚCI Z REGULAMINEM

> *"Lex dura, sed lex."*
> Prawo surowe, ale prawo.

### Zasady operacyjne

- Przed wdrożeniem jakiejkolwiek strategii bota na giełdzie: **przeczytaj regulamin giełdy**
- Zakaz: wash trading, spoofing, manipulacja rynkiem
- Znaj limity: rate limits, limity pozycji, ograniczenia API
- Działaj w granicach prawa lokalnego i regulacji MEXC

### Manipulacje używane PRZECIWKO nam — filtruj je

| Manipulacja | Opis | Działanie systemu |
|-------------|------|-------------------|
| Pump & dump | Sztuczne pompowanie ceny przed dump | Wykrywaj anomalie wolumenu |
| Stop hunt | Celowe wybijanie stop-lossów przez wieloryby | Ustawiaj SL poza oczywistymi poziomami |
| Fake walls | Fałszywe zlecenia w księdze zleceń | Monitoruj order book depth i cancellations |

**MEXC jest giełdą zweryfikowaną. Współpracuj z nią, nie przeciwko niej.**

---

## 📚 ŹRÓDŁA — Biblioteka napędza roadmapę (BIB)

> **Stan na:** 2026-06-26 | Każdy duży kierunek rozwoju ma fundament w bibliotece (42 książki).
> Pełna esencja: `bibliotheca_ulpia/encyklopedia/INDEX_MAIOR.md` (16 działów).

| Kierunek roadmapy | Fundament (koncept) | Źródło BIB |
|-------------------|---------------------|-----------|
| Reguła 6% + bezpieczniki ryzyka | budżet ryzyka portfela + circuit-breaker | BIB-015 Elder; uzasadnienie BIB-040 Bernstein |
| Walidacja w Koloseum (DSR/PBO) | anty-overfitting, magnituda > częstotliwość | BIB-007 López de Prado + BIB-041 Taleb |
| HRP / alokacja portfela | Hierarchical Risk Parity (klastry korelacji) | BIB-007 López de Prado + BIB-026 Jansen |
| Warstwa ryzyka EWMA/VaR/ES | EWMA λ=0.94, Expected Shortfall (grube ogony) | BIB-042 Jorion |
| Bibliotheca-RAG (pamięć semantyczna) | RAG nad książkami, CONDENSE_QUESTION, FTI | BIB-033 Huyen + BIB-036 Alto + BIB-035 Iusztin&Labonne |
| Kontekst makro (RADAR/Gubernator) | faza 18-letniego cyklu jako TŁO reżimu | BIB-001 Patel (+ planowane BIB-056..058 Dalio) |
| Neurony zmienności / GARCH | GARCH, vol cone, realized vol | BIB-031 Tsay + BIB-008 Sinclair |

> Mapa książka→neuron: `docs/KATALOG_NEURONOW.md` § Źródła. Książka→strategia: `docs/KATALOG_STRATEGII.md` § Źródła.
> Książka→warstwa architektury: `docs/ARCHITEKTURA_IMPERIUM.md` § Źródła.

---

*Dokument żywy — aktualizowany wraz z postępem systemu IMPERIUM.*
*"Alea iacta est." — kości zostały rzucone.*
