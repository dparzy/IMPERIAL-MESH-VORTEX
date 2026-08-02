---
kategoria: CONSILIUM
typ: zywy
wlasciciel: —
stan_na: 2026-08-02
powod_istnienia: "Mapa dróg rozwoju systemu w 5 fazach (0-4), od pierwszego cyklu paper trading do pełnej autonomii."
---
# 🏛️ ROADMAP IMPERIUM — MAPA DRÓG SYSTEMU

**Dokument:** Plan rozwoju systemu IMPERIUM — AI crypto trading z motywem Cesarstwa Rzymskiego
**Aktualna faza:** FAZA 1 — Namiestnik (Regime + Timeframe-Aware Gating)
**Data:** 2026-06-12
**Wersja:** v0.9.1

---

## 🗓️ PLAN WACHT — operacyjna kolejka zadań (stan 2026-08-02)

> **Czym to jest, a czym nie:** FAZY 0–4 niżej to mapa STRATEGICZNA (dokąd zmierzamy).
> Ta sekcja to kolejka OPERACYJNA — co robimy w najbliższych wachtach, w kolejności.
> Każda pozycja ma **stan zmierzony**, nie deklarowany, i przechodzi **CURSUS PLENUS**
> (zadanie → testy → checklista → działa na żywych danych → kalibracja → ocena →
> zwiad → pomiary → symbioza). Pozycja bez kalibracji przyrządu **nie jest skończona**.

**Legenda stanu:** ✅ zrobione · 🟡 kod jest, brak dowodu · 🔴 nie istnieje · ⏸️ świadomie odłożone

### 👑 CZTERY KORONY — kolejność ZATWIERDZONA PRZEZ CEZARA 2026-08-03

> Powstały jako opcje spłaty NOTY (LEX TALIONIS) za zwiad puszczony równolegle z bramką.
> **Nowy ROZKAZ STAŁY z tej samej wachty:** przed spłatą noty Architekt podaje **TRZY
> opcje CORONY** (uzasadnienie · opis · wpływ · co wnosi), a **wybiera Cezar** — dotąd
> 54 korony powstały bez tej bramki, czyli wybierał ten, kto zawinił. Cezar wybrał
> **wszystkie cztery** i dodał czwartą własnym pytaniem o organ ewolucji.

| # | CORONA | Co wnosi | Piętro | Koszt |
|---|---|---|---|---|
| **A** ⭐ | **SILENTIUM** — bramka zakłada blokadę, hook PreToolUse **odmawia zapisu do repo** w trakcie biegu | VINDEX *wykrywa* zabrudzenie po fakcie; **nic nie ZAPOBIEGA**. Zmierzone: 4 unieważnione biegi w 4 dni, **dwa z nich w jednej wachcie 08-03 przez tego samego, kto zasadę zapisał** — dowód, że sama wiedza nie wystarcza | HARNESS | ~1 wachta |
| **C** | **CUSTOS BIBLIOTHECAE** (= A15) — warstwa W25: dysk ↔ katalog ↔ cache ↔ RAG | Żadna z 24 warstw nie pyta o KSIĘGI. Dowód: 40 ksiąg przybyło 01.08, **nikt nie zauważył przez dobę**, audyt drukował „pełna harmonia" | LOOP | ~1 wachta |
| **B** | **VINDEX → GRAF W8** (= H6) — krawędzie `(plik) —[naruszenie]→ (commit)` | Jedyny producent krawędzi z **realnych zdarzeń**, nie z tekstu. Jedyna droga na GRAPH **nieblokowana przez A10** — ale nie daje czytelnika przy decyzji, więc GRAPH zostanie 3/4 | GRAPH | ~½ wachty |
| **D** | **CURSUS ARTIS** — organ mierzący **WSZYSTKIE piętra**, z **rejestrem układów** (wzorce połączeń, status `ZATWIERDZONY/KANDYDAT/OBALONY`) | MATURITAS mierzy **3 z 9**. Dwa spoza trójki **JUŻ STOJĄ i nie są liczone**: HARNESS (6 hooków, 24 warstwy, SIGILLARIUM) i NEURO-SYMBOLIC (Prawo XXI, INDEX FALSORUM, VINDEX = weryfikacja w architekturze, nie audyt post-hoc). **Prawdopodobnie ZANIŻAMY własny stan.** INGENIUM = zero plików (grep) | wszystkie | ~2 wachty |

> **ROZSTRZYGNIĘCIE CEZARA o układach (D):** wzorce wchodzą do rejestru **wyłącznie po
> zatwierdzeniu nowej wizji albo po zmierzonym odkryciu** — nigdy z lektury materiału.
> Domyka to pętlę *odkrycie → zatwierdzenie → wzorzec → egzekwowanie* i usuwa zarzut,
> że budowalibyśmy miernik na cudzej, nieosądzonej taksonomii.
>
> **Warunek uczciwości dla D:** osiem z dziewięciu pięter znamy z materiału, którego
> jeszcze nie osądziliśmy — tego samego, który wyprodukował `US20230000000A1`
> i `abc123.ngrok.io`. Pierwsza wersja rejestru zawiera **tylko to, co potwierdzone
> w NASZYM kodzie**; reszta czeka na QUAESTIO.

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
| C1 | **Sąd nad 35 cząstkami Hyginusa** (kolejka 44, osądzonych 8) | 🟡 narzędzie jest, plon czeka |
| C2 | **ESSENTIA** — esencja = falsyfikowalna hipoteza, nie streszczenie | 🔴 kod nie istnieje |
| C3 | **Rejestr książka→moduł→werdykt** wg McLean-Pontiff (IC przed/po wdrożeniu) | 🔴 **brak prior artu — definiujemy sami** |
| C4 | **TIRO E3** — 229/1000 par użytecznych (23% progu) | 🟡 w toku |
| C5 | **INGENIUM** — IQ Imperium w 7 kategoriach | 🔴 projekt w docs, kod nie istnieje |

### WACHTA D — fronty, które decydują o ŁUPIE (nie o wiedzy)

| # | Zadanie | Stan | Uwaga |
|---|---|---|---|
| D1 | **JEDEN zamknięty obieg na realnych groszach (MEXC)** | 🔴 `MEXC_API_KEY` brak | **zero prawdziwych wypełnień w historii Imperium** — poślizg i prowizja są ZAŁOŻONE, nie zmierzone. Decyzja kapitałowa = wyłącznie Cezar |
| D2 | **Świeżość danych** — dryf 1D **41,5 dnia**, 1m 9,3 dnia | 🔴 zmierzone, niezałatane | rój głosuje na nieświeżych danych |
| D3 | **Kalibracja kosztu egzekucji na realnych fillach** | 🔴 | zależy od D1. **Zwiad 07-30 (SaR 2603.09164, Sepper/ex-Gauntlet) NIE domyka D3** — mierzy poślizg **likwidacji po stronie giełdy** (wielkość funduszu ubezpieczeniowego, wymogi kapitałowe), a nie to, ile zje NASZE małe zlecenie; **2 z 4 jego wejść są dla nas nieosiągalne** (pełne migawki L2 ≥1/min — mamy zero; atrybucja na poziomie kont — dostępna „on fully on-chain DEXs", a MEXC jest scentralizowana). Co się przenosi: forma `S ∝ 1/L` i legitymizacja **poślizgu ZALEŻNEGO OD STANU** zamiast stałej założonej. Odłożone do dnia wpięcia L2 |
| D4 | **Poślizg zależny od stanu zamiast stałej** — funkcja mierzalnych zmiennych (zakres, wolumen, zmienność) | 🔴 | Dziś poślizg i prowizja są **ZAŁOŻONE**, więc mogą odwracać znak wyniku strategii. Nie wymaga L2: nawet zgrubna funkcja tego, co mierzymy, jest **ściśle lepsza od stałej**. Prior art do wzięcia: warstwowe modele wypełnienia z `nautilus_trader` (poz. 5 zwiadu 07-29 — głębokość symulowana **z samego wolumenu świecy**) |
| D5 | **DR-OPE — oszacowanie zwrotu polityki BEZ realnych zleceń** | 🔴 | Z Atkinsona: *Doubly Robust Off-Policy Evaluation*, nieobciążony estymator oczekiwanego zwrotu, wagi IPS obcinane. **Odblokowuje pomiar tam, gdzie D1 stoi na braku kluczy MEXC i decyzji kapitałowej Cezara** — polityki nie trzeba wdrożyć, żeby oszacować jej zwrot. Do tego z tego samego źródła: **Temporal Degradation** (nachylenie wierności względem czasu) — mamy Prawo XXIII o trafności per reżim, ale **nachylenia nie liczymy** |

### WACHTA E — dług techniczny z zamrożonej listy

| # | Zadanie | Stan |
|---|---|---|
| E1 | `zip(strict=)` w Bramie · RUF012 · strażnik budżetu | 🔴 |
| E2 | WFO chunkowany (backtest liniowy ~66 ms/tik — premisa „kwadratowy" była błędna) | 🟡 |
| E3 | Strażnik obcych plików → wrzutnia/kwarantanna zamiast kasowania | 🔴 pomysł Cezara 07-28 |
| E4 | Dług kontekstu: CLAUDE.md **259 linii > 200** | 🔴 rośnie z każdym rozkazem (253 po odchudzeniu 07-27 → 259 dziś) |

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
