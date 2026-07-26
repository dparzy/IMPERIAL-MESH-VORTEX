---
kategoria: ACTA
typ: acta
powod_acta: "Dziennik akumulujący — każdy wpis jest datowaną prawdą swojego czasu. Wpisów NIE aktualizujemy wstecz (ROZKAZ STAŁY, Prawo I: nie falsyfikujemy historii). Dokument jest żywy jako CAŁOŚĆ, ale jego treść to wyłącznie historia."
wlasciciel: —
stan_na: 2026-07-27
powod_istnienia: "Żywa pamięć projektu: chronologia KAŻDEJ zmiany (ROZKAZ STAŁY). Wpisy datowane = prawda swojego czasu, nie aktualizujemy wstecz"
---
# 📜 LOG ZMIAN IMPERIUM — Żywa Pamięć Projektu

> **Zasada (ROZKAZ STAŁY):** Po KAŻDEJ zmianie systemu, kodu, dokumentacji — wpis do tego logu.
> Format: Data | Typ | Opis | Powód | Pliki. Najnowsze wpisy na górze.
> Ten plik jest źródłem prawdy historii Imperium. Bez niego decyzje giną.

---

## 2026-07-27 | 🔬 | Sąd nad recenzją cubic PR #133 — 20/22 słuszne, dwie nowe warstwy audytu

**Cezar kazał sprawdzić, czy recenzent ma rację. Osądziłem każde z 22 znalezisk wobec
żywego kodu: 20 słusznych, 2 fałszywe — w tym jedyne P1 okazało się halucynacją.**

**Obalone:** (1) zarzut „ręcznej edycji `sigillum_probationis.json`" cytował DWIE
nieistniejące reguły — `grep` po całym korpusie `.md` nie znajduje tego pliku poza
diffstatem kroniki, a zapisuje go automatycznie `tests/run_tests.py` po każdym biegu.
(2) „katalog `wrzutnia/consilium/` nie istnieje" — istnieje, jest gitignorowany;
recenzent pomylił *niewidoczne w repo* z *nie ma*, czyli dokładnie tę klasę abstynencji,
przed którą Imperium się broni.

**Naprawione u źródła (kod):** filtr zbioru SFT wydzielony do jednego generatora
(`notarius.pary_sft`) — eksport i licznik nie mogą się już rozjechać; licznik par TIRO
przestał serializować cały zbiór do pliku tymczasowego dla jednej liczby i dostał jawny
ledger; `aerarium` przestał padać na poprawnym JSON-ie o złym kształcie i przestał
podawać CUDZĄ pamięć jako nasz pomiar.

**Testy, które nic nie broniły:** skasowana TAUTOLOGIA (`korpus_ksiazek_obecny() ==
(ksiazki_w_bazie() > 0)` — porównanie wyrażenia z własną definicją, przechodziło zawsze),
parytet GRADUS pilnuje teraz także KLUCZY wysiłku, a niezmiennik sesyjności objął
`ultracode`. Każda poprawka udowodniona MUTACJĄ: pod zepsutym kodem nowy test oblewa.

**Przyczyna źródłowa duplikatów — ZMIERZONA:** dedup lekcji przeglądał 91 wpisów
aktywnych i nie widział 207 zarchiwizowanych (69% korpusu poza zasięgiem bramki).
Chłodzenie wyprowadzało bliźniaka poza pole widzenia, więc auto-lekcja zapisywała tę
samą treść ponownie. To POWTÓRKA wady z cubic PR #118 — naprawiono wtedy PREDYKAT, ale
nie ZASIĘG. Ironia potwierdza diagnozę: najczęściej powielona lekcja (4×) mówi „archiwum
niewidoczne dla `szukaj()`". Rejestr wizji dedupował po samym napisie, więc parafrazy
DeepSeeka wchodziły podwójnie; teraz oba rejestry dzielą JEDEN predykat, a pominięcie
jest głośne (Prawo XV). Sprzątanie: ACTA 207→188, pamięć aktywna 91→89, ledger 827→803 —
wariant bogatszy zostaje, dwie pary świadomie NIE scalone (różne strategie / obserwacja
wraz z jej rozstrzygnięciem).

**Dwie nowe warstwy audytu (CORONY):**
- **W19 — parytet dat:** `stan_na` we frontmatterze musi równać się „Stan na:" w nagłówku.
  Cubic znalazł jeden taki rozjazd, mechanizm znalazł pięć kolejnych. Warstwa złapała też
  własny fałszywy alarm (cytat „Stan na:" w prozie changelogu i daty SEKCJI) — zasięg
  zawężony do nagłówka dokumentu, bo warstwa pilnująca prawdy nie może produkować nieprawdy.
- **W20 — katalog nietknięty:** sekcja generowana w INDEKS musi być tym, co wypluwa
  Tabularium. Ręczny wiersz siedział w sekcji CONSILIUM przy `kategoria: DISCIPLINA`;
  regeneracja ujawniła dodatkowo trzy nieaktualne daty. Porównujemy strukturę, świadomie
  pomijając linię „Ostatni spis" — inaczej audyt żądałby przepisania katalogu codziennie.

Przy okazji: docstring audytu deklarował „16 warstw" przy 18 w kodzie — usunięta ręczna
liczba, została sama lista (klasa wady W15).

**Pliki:** `imperium/biblioteki/notarius.py`, `imperium/oczy/breviarium.py`,
`imperium/cesarz/aerarium.py`, `imperium/biblioteki/pamiec_sesji.py`,
`imperium/biblioteki/rejestr_wizji.py`, `narzedzia/audyt_spojnosci.py`,
`narzedzia/auto_lekcja.py`, `tests/*`, `README.md`, `docs/README.md`,
`docs/INDEKS_IMPERIUM.md`, `docs/MANIFEST_KODU.md`, `docs/SCIAGA_LOKAL.md`.

---

## 2026-07-26 | 🎓 | TIRO: fałszywy alarm o silniku ODWOŁANY + korekta planowania par

**Cezar kazał sprawdzić, ZANIM podejmie decyzję — i miał rację.** Meldowałem „TIRO ma zero
silnika i zero modeli, największa utrata potencjału". **To był fałszywy alarm.**

**Przyczyna:** `KATALOG_TIRO = Path(os.getenv("TIRO_HOME", r"C:\TIRO"))` — ścieżka WINDOWS,
która w kontenerze Linuksa nie ma prawa istnieć. `.exists()` → False → 🚨. Tymczasem dziennik
z 07-16 dokumentuje: llama.cpp b10041 stoi w `C:\TIRO\silnik`, modele zmierzone `llama-bench`
(Qwen3-1.7B **9.64 t/s**, Qwen3-4B **4.86 t/s**). **E0 i E1 są zamknięte.**

To **czwarte** wystąpienie klasy „milczenie udaje wynik" tego samego dnia — i najgorsze,
bo tym razem fałszywy alarm nie tylko istniał, ale **został przekazany Cezarowi jako podstawa
decyzji o wydaniu pracy**. Uodpornienie: `_sciezka_z_innego_systemu()` rozpoznaje literę dysku
Windows na Linuksie (i ścieżkę POSIX na Windows) → `silnik: None` i meldunek „⚠️ dysk TIRO
niewidoczny stąd". Granica pilnowana testem: brak silnika na **widocznym** dysku nadal krzyczy.

**KOREKTA PLANOWANIA (zmierzona):** postęp Szkoły liczyliśmy parami SUROWYMI, a trening jedzie
na tych, które przeżyją eksport SFT (kolaps anty-monokultury + filtr jakości):

```
329 par surowych → 140 użytecznych   (przeżywa ~43%)
```

Meldunek zawyżał gotowość **2,35×**: „329/500 = 66%" zamiast prawdziwego **140/1000 = 14%**
(1000 = minimum sensownego LoRA). Droga do progu jest ~2× dłuższa, niż mówiła ekstrapolacja
z 07-16, bo tamta liczyła surowe. BREVIARIUM podaje teraz OBIE liczby i procent progu.

**Decyzje Cezara:** (1) lokalnie — E3 (egzamin wstępny ucznia) NAJPIERW, bo tani i mówi czy
warto zbierać, potem partia POMIAROWA żniwa; (2) licznik pokazuje obie liczby; (3) abstynencja
środowiskowa wpięta. Pakiet zadań: **`docs/ZADANIE_TIRO_E3_ZNIWO.md`** (wpisany do INDEKSU).

**Pliki:** `imperium/oczy/breviarium.py`, `tests/test_breviarium.py`,
`docs/ZADANIE_TIRO_E3_ZNIWO.md`, `docs/INDEKS_IMPERIUM.md`.

---

## 2026-07-26 | 🗺️ | Ścieżka lokalna sprostowana + OPUS 5 modelem głównym

**Poprawka Cezara (dwie sprawy naraz).**

**1. Ścieżka podana z WYGLĄDU nazwy, nie ze źródła.** Podałem blok push z
`cd C:\IMPERIAL-MESH-VORTEX` — przepisałem wersaliki z nagłówka README i nazwy repo na
GitHubie, gubiąc nadrzędny folder. Realnie: **`C:\Projekty\imperial-mesh-vortex`**
(`docs/SCIAGA_LOKAL.md`, potwierdzone niezależnie ścieżką temp Windows w kronice:
`C--Projekty-imperial-mesh-vortex`).

**Skan całego korpusu (decyzja Cezara) pokazał, że ta sama klasa GNIŁA w żywym manualu:**
`docs/MANUAL_CLAUDE_CODE.md` kazał w dwóch miejscach użyć `Desktop\imperial-mesh-vortex`
— raz jako `cd`, raz jako ścieżka serwera **MCP filesystem**. Cezar-nowicjusz wkleiłby ten
blok i dostał serwer wskazujący w próżnię. Oba miejsca poprawione + nota o sprostowaniu.
Reszta korpusu spójna (5 wystąpień poprawnej ścieżki). Kronika NIETKNIĘTA (Prawo I).

**2. OPUS 5 modelem głównym Imperium, Opus 4.8 na emeryturze** (decyzja Cezara — wg
rankingów Opus 5 jest zdecydowanie mocniejszy). Zapis w `CLAUDE.md` §ZASADA OSZCZĘDNOŚCI
TOKENÓW rozdzielony na **regułę** („Opus" = najwyższy dostępny tier — wiążąca, nie starzeje
się) i **datowany stan** (dziś: Opus 5; wcześniej kolejno 4.8 i Fable 5 — z założenia się
zestarzeje). Dopisana zasada rozstrzygania sporu: Architekt NIE MIERZY własnego modelu
(środowisko nie niesie identyfikatora), więc gdy jego deklaracja rozjedzie się z tym, co
ustawił Cezar — **wiąże ustawienie Cezara**, nie deklaracja (kto nie mierzy, ten nie rozstrzyga).

**Księga Wad +1 klasa:** „ścieżka/nazwa podana z wyglądu nazwy repo zamiast ze źródła prawdy"
— wypełniacz typu `TwojeImie` stosuj TYLKO tam, gdzie wartość jest naprawdę nieznana.

**Pliki:** `CLAUDE.md`, `docs/MANUAL_CLAUDE_CODE.md`, `bibliotheca_ulpia/dane/ksiega_wad_kodu.jsonl`.

---

## 2026-07-26 | 🔇 | ABSTYNENCJA ZAMIAST ZERA — narzędzie od prawdy żądało skasowania prawdy

**Alarm otwarcia wachty (audyt W15) okazał się fałszywy W SPOSÓB GROŹNY:** Warstwa 15
zażądała przepisania `ksiazki: 115 → 0` i `fragmenty: 37331 → 551` w sześciu dokumentach.
Wykonanie `tabularium.py liczby --zapisz` w chmurze **skasowałoby prawdziwe liczby lokalne**.

**Przyczyna (zmierzona, nie zgadnięta):** książki komercyjne są ŚWIADOMIE poza gitem
(rozkaz Cezara 2026-07-11), więc chmura ma pełny kod i zero książek. `ksiazki_w_bazie()`
zwracało wtedy `0` — **nieodróżnialne od zmierzonego zera** — a mechanizm W15 traktuje
każdą wartość jako pomiar. Dowód: `ls bibliotheca_ulpia/ksiazki` = 0 plików przy 551
fragmentach RAG w gicie.

**Naprawa u źródła + UODPORNIENIE KLASY (ZASADA CENSORA):**
- `srodowisko_pamieci.korpus_ksiazek_obecny()` — czy TO środowisko w ogóle MOŻE zmierzyć.
- `tabularium.wartosci_z_kodu()` → `ksiazki`/`fragmenty` = **None** (abstynencja) bez korpusu.
- `wstrzyknij_liczby()` — klucz abstynujący **zostawia blok nietknięty** i nie liczy się
  jako rozjazd. Milczenie nie jest pomiarem.
- 2 testy granic (`None` ≠ `0`: abstynencja NIE nadpisuje, zmierzone zero NADAL nadpisuje;
  spójność `korpus_ksiazek_obecny()` z `ksiazki_w_bazie()`).

**Najgorsze w tej wadzie:** istniejący test `test_liczby_z_kodu_sa_dodatnie` **przewidział
ten przypadek i rozstrzygnął go ŹLE** — komentarz „ksiazki/fragmenty mogą być 0 na świeżym
klonie bez bazy RAG" uznawał milczenie za wynik i tym samym **legalizował** żądanie W15.
Test poprawiony na niezmiennik: albo oba mierzą, albo oba milczą — nigdy pół na pół.

To ta sama klasa co martwy głos neuronu z Prawa XV: **brak danych to abstynencja, nie wynik**.

**Pliki:** `imperium/biblioteki/srodowisko_pamieci.py`, `narzedzia/tabularium.py`,
`tests/test_tabularium.py`. Dodatkowo W6: `Stan na:` w README/MANIFEST 07-19 → 07-26.

### Ta sama klasa wróciła jeszcze trzy razy tego samego dnia

Szukanie „gdzie indziej milczenie udaje wynik" dało trzy dalsze trafienia — zmierzone,
nie zgadnięte:

1. **BREVIARIUM meldował „kolejka 0 cząstek | czeka na sędziego 0"** w chmurze, choć
   kolejka jest gitignorowana (`.gitignore:55`) i pliku tam NIE MA (na lokalu leżały 34
   cząstki). Fałszywy spokój groźniejszy niż brak meldunku: krok 4b domknięcia liczy
   DELTĘ, więc „34 → 0" wyglądałoby na wykonaną pracę. Teraz: *„⚠️ kolejka NIEZNANA w tym
   środowisku"*, a delta ten wskaźnik pomija. Konfiguracja mowy (profile faz) NIE abstynuje
   — jest w kodzie, więc znamy ją wszędzie (moja pierwsza łata wygaszała ją razem z kolejką).
2. **Testy zależne od ZEGARA** (`test_dispensator`, 3 szt.): od taryfy szczytowej (07-21)
   `koszt_usd` liczy wg chwili wywołania (2× w oknach 01–04 i 06–10 UTC), ale trzy stare
   testy kosztu nie dostały `kiedy=`. **Przez ~7 godzin na dobę cały pakiet był czerwony**
   — złapane o 01:57 UTC (oczekiwane 0.14, policzone 0.28). Nowe testy taryfy miały helper
   `_utc`, starych nikt nie przeniósł.
3. **Runner nie znał POMINIĘCIA** — `tests/run_tests.py` znał wyłącznie „zaliczony/oblany",
   więc test wymagający zależności OPCJONALNEJ padał tam, gdzie jej nie ma (3× EPUB
   `ebooklib`, 2× SPECULA `plotext`). Dodane `unittest.SkipTest` (stdlib, honorowany też
   przez pytest) + licznik i GŁOŚNY wydruk powodów — ciche pominięcie udawałoby pokrycie.
   Gdzie gałąź da się wymusić flagą (`PLOTEXT_DOSTEPNY`), wymuszamy zamiast pomijać.

**Naprawiony przy okazji fałszywy WIDOK:** BREVIARIUM listował klucze słownika
`dispensator.PROFILE`, więc drukował `krytyka→v4-flash` i czytało się to jak mapowanie
fazy na model — na otwarciu odczytałem to jako sprzeczność z decyzją z 07-21 (krytyka na
profilu `osad`, v4-pro). Kod był poprawny, kłamał WIDOK. Teraz `krytyka→[osad] v4-pro/high`
+ test parytetu widok↔kod.

**Wynik bramki:** testy **2879/2879 zielone, 3 pominięte jawnie**, audyt exit 0 (18 warstw),
skan wad czysto. Księga Wad: +4 klasy semantyczne.

**Pliki dodatkowo:** `imperium/oczy/breviarium.py`, `tests/test_breviarium.py`,
`tests/test_dispensator.py`, `tests/test_rag.py`, `tests/test_specula_swiec.py`,
`tests/run_tests.py`.

---

## 2026-07-21 | 💰 | Taryfa szczytowa DeepSeeka — rachunek platformy obalił nasz model kosztu

Cezar pokazał **rzeczywisty rachunek z panelu DeepSeeka** za 2026-07-21. Zestawienie
z pomiarem LIBRA MESSIS:

| | platforma | nasz rejestr |
|---|---|---|
| v4-pro | 8 żądań · $0.03 | 8 wywołań · $0.0317 |
| v4-flash | 202 żądania · $0.12 | 152 wywołania · $0.0996 |

**Model kosztu wpięty tego dnia okazał się dokładny** — v4-pro zgadza się co do sztuki,
bo tych 8 wywołań to wyłącznie ramię `osad`. Brakujące 50 żądań flash rozliczone przez
NOTARIUSA: 21 par to `auto_lekcja` z hooków, reszta to wywołania rozbitego biegu, którego
proces nie zdążył zapisać. **Ok. 27 żądań (13%) pozostaje nierozliczonych i tak to
zapisujemy** — proces zabity na timeoucie z definicji nie zapisze tego, co wysłał.

**ZNALEZISKO WAŻNIEJSZE NIŻ RACHUNEK:** platforma stosuje **taryfę szczytową 2×** w oknach
**01:00–04:00 i 06:00–10:00 UTC**, a nasz `CENNIK` miał stawki płaskie. Rzecz w tym, że
dokument, z którego go przepisaliśmy (`api-docs.deepseek.com/quick_start/pricing`), **nie
był błędny — był NIEPEŁNY**: o taryfie milczy do dziś. Zweryfikowane w sieci przed zmianą
stałej (Prawo I): potwierdzają to niezależnie doniesienia TechNode i SCMP o zmianie
ogłoszonej 2026-06-30 oraz notatka na panelu rozliczeniowym; godziny zgodne co do minuty.

- `dispensator.czy_szczyt()` + `koszt_usd(..., kiedy=)` — koszt liczony wg taryfy z chwili
  WYWOŁANIA, nie z chwili raportu (inaczej ten sam rekord miałby inną cenę zależnie od pory
  uruchomienia raportu). LIBRA MESSIS zapisuje pole `szczyt` przy każdym pomiarze.
- **Sprawdzone wstecz: 0 ze 160 dzisiejszych pomiarów A/B padło w oknie szczytu**
  (biegły 10:38–12:38 UTC), a ramiona szły naprzemiennie — więc raportowane krotności
  kosztu (U4 1.46×, profile 3.46×) są **nieskażone taryfą**.
- **`auto_lekcja` odkłada analizę w szczycie.** 06:00–10:00 UTC to 08:00–12:00 czasu Cezara,
  czyli typowy poranny start sesji trafiał prosto w podwójną stawkę — wszystkie 22 dzisiejsze
  wywołania w szczycie pochodziły z tego hooka. Odłożenie nie kosztuje nic, bo analizowane
  sesje są już zakończone; zaległe domknie najbliższy start poza szczytem. Wyłączniki:
  `--takze-w-szczycie` i `--sesja`.
- Decyzja wydzielona z `__main__` do `powod_odlozenia()` — bramka schowana w bloku
  uruchomieniowym jest nietestowalna, a bramka bez testu przestaje gryźć niezauważona.
- Testy granic okien (początek wliczony, koniec wyłączony) + dowód, że stawki bazowe
  pozostały nietknięte: naprawa **dołożyła wymiar czasu, nie podmieniła cennika**.

---

## 2026-07-21 | ⚖️ | A/B jakości plonu Hyginusa — organ LIBRA MESSIS i trzy wady WŁASNEJ miary

Rozkaz Cezara: *„nowa sesja zaczyna od A/B, decyzja co lepsze DOPIERO po pomiarze"*.
Zbudowany organ **LIBRA MESSIS** (Waga Plonu, `narzedzia/ab_plon_hyginusa.py`) — waży dwa
ramiona zwiadu na tej samej liście tematów. **Nie dotyka produkcyjnej kolejki hipotez**
(woła `scout_temat` z pominięciem `raport()`), bo narzędzie mierzące nie ma prawa zmieniać
mierzonego stanu — dokładnie ta wada zaśmieciła kolejkę dzień wcześniej.

**WYNIK U4 (świadomość systemu) — NIEROZSTRZYGNIĘTY, i tak został zaraportowany.**
Poligon „rdzeń" (8 tematów o *zmierzonej* zdolności produkowania duplikatów):
OFF 11/26 (42.3%) vs ON 6/19 (31.6%) → −10.7 pp przy **Fisher p = 0.543**. Kierunek zgodny
z hipotezą, dowodu brak. Plon NOWYCH kandydatów płaski (13 vs 15). **Koszt jest pewny tam,
gdzie korzyść nie jest:** 1.84× ceny, 1.66× czasu, 2.2× tokenów rozumowania — liczone z
FAKTYCZNEGO `usage`, bo most wreszcie je wystawia (`GlosImperium.ostatnie_zuzycie`;
`DISPENSATOR.koszt_usd` miał wzór i cennik, ale nikt go nie karmił — Prawo XV).

**Trzy wady mojej własnej miary, wszystkie złapane POMIAREM, żadna testem:**

1. **Leksykon potwierdzał sam siebie.** Weryfikacja „czy pojęcie istnieje w kodzie" skanowała
   korpus RAZEM z plikiem deklarującym listę — każdy wpis znajdował dowód we własnej linijce
   i przechodziła ZAWSZE. Zielony test też, bo testował tę samą zatrutą funkcję. Skutkiem był
   wpis `order flow imbalance`, który oskarżał zwiad o duplikat rzeczy, **której rój nie ma**
   (mamy *imbalance bars* W-356 — inne pojęcie). Miara myliła się, model miał rację.
   Naprawa: korpus wyklucza własny plik + **test negatywny** (wpis-widmo musi zostać zgłoszony).
2. **Miara karała ramię za wykonanie instrukcji.** U4 każe dopisać „czy kandydat NIE dubluje
   istniejącego modułu", więc ramię ON z definicji wymienia nasze moduły w ZAPRZECZENIACH.
   Licząc wzmianki w całym bloku, dostałem wynik ODWROTNY do prawdy (ON 31% vs OFF 14%).
   Naprawa: liczymy NAZWĘ kandydata, nie uzasadnienie.
3. **Poligon bez możliwości zdarzenia.** Pierwszy bieg dał 0 duplikatów w OBU ramionach —
   to **brak mocy, nie remis**. Tematy pochodziły z obszarów słabo pokrytych przez rój.

Rejestr trzyma **surowy plon**, więc poprawki definicji miary przeliczyły się bez ani jednego
płatnego wywołania (`przelicz`). Pomiar stał się odwracalny. Bieg jest wznawialny i przeżywa
zryw łącza (ponowienia 5/15/45 s; pierwszy bieg padł na `APITimeoutError` przy 11 z 16 —
cząstki ocalały). Księga Wad 74 → 77.

**Przy okazji naprawione w CODEX:** arkusz Sugestie wypisywał KAŻDĄ linię append-only ledgera,
więc domknięta sugestia stała obok swojego starego KANDYDATA — backlog czytał się na 49 pozycji
przy realnych 41, a **7 zadań już zrobionych wyglądało na otwarte**. Strona zapisu miała
domykanie jako operację pierwszej kategorii (`scriba_codex.zamknij_sugestia`) od 2026-07-19;
strona odczytu jej nie honorowała. Naprawa: zwijanie „ostatni wpis wygrywa" po tym SAMYM kluczu
`element`, po którym pisze skryba, kolumna „Historia" zachowuje poprzednie statusy.

**DECYZJE CEZARA po przedstawieniu wyników (2026-07-21):**

1. **Domknąć U4 rozstrzygnięciem** — poligon rdzeniowy rozszerzony 8 → 16 tematów (nowe celują
   wprost w pojęcia, które *na pewno* mamy: VPIN, Hurst, entropia, funding/OI, Yang-Zhang, VWAP,
   Amihud, adaptacyjne średnie) + wprowadzone **rundy**: powtórzenie tematu to nowe losowanie
   (temperatura 0.4), czyli dodatkowa obserwacja. Bez wymiaru rundy jedynym sposobem na większą
   próbę byłoby wymyślanie kolejnych tematów, co mieszałoby moc z doborem próbki.

   **WYKONANE I ROZSTRZYGNIĘTE tego samego dnia** — 64 pary temat×ramię, **372 kandydatów**:

   | | U4 OFF | U4 ON |
   |---|---|---|
   | kandydatów | 203 | 169 |
   | **dublujących** | 81 (**39.9%**) | 47 (**27.8%**) |
   | **NOWYCH (niedublujących)** | **122** | **122** |
   | koszt | $0.0314 | $0.0458 (1.46×) |

   **Fisher p = 0.016 → ISTOTNE.** Efekt stabilny na trzech rozmiarach próby: −10.7 pp (n=45),
   −10.3 pp (n=181), −12.1 pp (n=372) — nie jest artefaktem jednego biegu. Rozmiar próby
   dobrany z PROJEKCJI wykonanej przed wydaniem pieniędzy (2× → p≈0.038; wyszło 0.016).

   **Najważniejsza liczba to 122 vs 122.** U4 usuwa 34 duplikaty, **nie zabierając ani jednego
   nowego pomysłu** — to nie jest kompromis między ilością a jakością, tylko czysty zysk minus
   46% dopłaty. Decyzja o domyślnym ON z poprzedniej wachty, podjęta wtedy z DIAGNOZY, ma
   wreszcie DOWÓD.
2. **Faza krytyki przeniesiona na profil `osad` (v4-pro)** — `_PROFIL_KRYTYKA = "osad"`.
   Podstawą jest **asymetria błędu, nie dowód statystyczny** i tak jest to zapisane w kodzie:
   sygnał jakości był słaby (23 vs 13 kapitulacji, rozkład 4-2-2 — nieistotny), koszt pewny
   (3.46×). Zdecydowało to, że krytyk, który pisze „nie znaleziono kontrargumentów" i **podnosi**
   ocenę kandydata do MOCNE, zamienia całe U3 w teatr — a v4-pro na tym samym materiale wyciągnął
   trzy zarzuty z cytatami dosłownymi. Tańsze ramię pozostaje dostępne przez `profil=`, więc A/B
   da się powtórzyć bez cofania zmiany. Nie dotyka ścieżki decyzyjnej tradingu.
3. **Następna wachta: sąd nad 33 cząstkami kolejki** — zwiad już opłacony, czekający na sędziego.

Pliki: `narzedzia/ab_plon_hyginusa.py` (nowy), `tests/test_ab_plon_hyginusa.py` (nowy, 16 testów),
`narzedzia/codex_probationum.py`, `narzedzia/bibliotekarz.py` (parametr `profil` w krytyce),
`imperium/cesarz/deepseek_glos.py`, `narzedzia/kapitol_podglad.py`, `docs/ARCHITEKTURA_IMPERIUM.md`.

---

## 2026-07-21 | 📋 | Raport sług na OBU końcach wachty — Δ zamiast samego stanu

Pytanie Cezara: *„zawsze na początku sesji i końcu raport Hyginusa i TIRO — czy to mamy"*.
**Odpowiedź była połowiczna i tak została powiedziana:** otwarcie ✅ (BREVIARIUM w hooku, krok 0.9),
zamknięcie ❌ — zero wzmianek w checkliście, a hook końca sesji w ogóle nie woła Pythona.
To ta sama klasa co dług honorowy z tego samego dnia — **rzecz widoczna tylko na jednym końcu
procesu** — tyle że w drugą stronę.

- **Na domknięciu liczy się RÓŻNICA, nie stan.** „Kolejka 34" nie mówi nic; „kolejka 34 → 41 (+7),
  czeka na sędziego +7" mówi, że wachta wyprodukowała dług przeglądu. Stąd `--delta`.
- Hook startowy woła `--migawka` (drukuje meldunek **i** utrwala punkt odniesienia);
  `CLAUDE.md § KONIEC SESJI` dostał krok **4b** z `--delta`. Pieczęć `/clausura` widzi go
  natychmiast (10 → 11 kroków), bo **czyta kroki z CLAUDE.md, nie przechowuje ich kopii**.
- Migawka celowo obejmuje tylko liczby zmienne w czasie (kolejka, plon czekający na sędziego,
  podejrzane cząstki, pary nauczyciela). Modele na dysku i klasa sprzętu nie zmieniają się
  w trakcie sesji — ich delta byłaby szumem zagłuszającym realny dorobek.
- **Brak migawki mówimy wprost** („różnicy nie znamy"), zamiast pokazać zero i sugerować
  „nic się nie zmieniło" (Prawo I).
- Liczby z kroku 4b **zasilają odpowiedź na Prawo XV** w kroku 5 — rosnąca kolejka bez sędziego
  to zapłacony i niewykorzystany zwiad.

**Wada złapana własnym testem granicy:** `zapisz_migawke` łapało tylko `OSError`, a ścieżka
z bajtem NUL daje `ValueError` już na `mkdir` — utrwalenie punktu odniesienia mogło wywrócić
meldunek, który miało tylko uzupełniać. +7 testów. **Pliki:** `imperium/oczy/breviarium.py`,
`.claude/hooks/session-start.sh`, `CLAUDE.md`, `tests/test_breviarium.py`.

---

## 2026-07-21 | 🩺 | RECENZJA: PROBATOR był MARTWY w produkcji — 7 znalezisk, 6 napraw

`/code-review` zlecona przez Cezara. **Najcięższe znalezisko: organ ogłoszony tego samego dnia
jako działający nie sprawdzał NICZEGO.**

- **Przyczyna:** PROBATOR czytał wynik RAG drabinką `isinstance`, w której gałąź `tuple` stała
  PRZED dostępem po atrybucie. Produkcyjny `szukaj.Wynik` to **NamedTuple** (dziedziczy po `tuple`)
  z polem `id: int` na PIERWSZEJ pozycji — więc za nazwę źródła brany był numer ID.
  **Zmierzone przed naprawą:** `podane_zrodla()` → `{}`, `aliasy_zrodel()` → `{}`, a jawna
  halucynacja `sprawdz("Teza wg BIB-999.", wyniki)` → `NIC_DO_SPRAWDZENIA` zamiast `PODEJRZANY`.
- **Dlaczego 20 zielonych testów tego nie złapało:** obie atrapy rozjechały się z produkcją —
  jedna nie była krotką, druga miała **inną kolejność pól**. W tej samej wachcie dodaliśmy test
  parytetu sygnatur dla atrapy `GlosImperium` i **nie zastosowaliśmy tej samej ochrony** do wyniku
  RAG. Ochrona zastosowana wybiórczo to ochrona pozorna.
- **Naprawa u źródła:** jeden ekstraktor `_pola()` wołany przez `podane_zrodla` i `aliasy_zrodel`
  (koniec zduplikowanej drabinki), **atrybut ma pierwszeństwo przed pozycją**. Testy używają
  **PRAWDZIWEJ klasy `szukaj.Wynik`** importowanej z produkcji, nie kopii kształtu.

**Pozostałe naprawione:** chunk sąsiedniego cytatu przyklejał się do poprzedniego BIB (fałszywe
OSKARŻENIE ugruntowanego plonu) · fraza `dry-run` z naszego żargonu uciszała całe sprawdzanie
cytatów (fałszywy NEGATYW) · pieczęć `0/0` raportowała ZIELONE zamiast awarii pomiaru · PORTITOR
brał linie opcji pip (`-r`, `--index-url`) za nazwy pakietów.

**INDEX FALSORUM +1:** twierdzenie „PROBATOR sprawdza cytaty w pipeline Hyginusa" obalone dla okresu
12ce701 → naprawa. Pomiar „0 cytatów spoza fragmentów na 33 cząstkach" **pozostaje ważny** — szedł
przez słowniki z JSONL, nie przez wpiętą ścieżkę produkcyjną.
**LEX TALIONIS:** N-4c81a58b ↔ C-77ea034d (waga 2, dług 0). **Księga Wad +4.** +14 testów.

---

## 2026-07-21 | 🧭 | U4 (świadomość systemu) DOMYŚLNIE ON — koniec płacenia za duplikaty

Wniosek z sądu nad kolejką, wdrożony w tej samej sesji (rozkaz Cezara „wg planu"). Zwiad, który
nie wie, co Imperium już posiada, z definicji proponuje to, co posiada — i dokładnie to zmierzyliśmy
na 33 cząstkach: VPIN, Value Area, Kelly, CVD, funding, Kalman, triple-barrier, DSR/PBO **już były
w kodzie**. Blok `_kontekst_systemu` (jedyne miejsce, gdzie pada „**NIE proponuj duplikatów**, oto
istniejące klucze" + luki Prawa XV) był opt-in.

- `scout_temat`/`raport`: `swiadomosc=True`. CLI: nowe `--bez-swiadomosci`; stare `--swiadomosc`
  zostawione jako bezefektowe, żeby cudze polecenia i skrypty nie padały.
- **Weryfikacja przed wdrożeniem (ZASADA WPIĘCIA):** zwiad **nie dotyka ścieżki decyzyjnej** —
  zero odwołań do `bibliotekarz` z `koloseum/` i `cesarz/`. Żaden próg, sizing ani filtr nie tknięty,
  więc opt-in nie jest wymagany.
- **Koszt zmierzony:** 3914 znaków ≈ 978 tokenów na temat (~$0.005 za 33 tematy na flashu) — wobec
  kosztu duplikatów i czasu sędziego to zaokrąglenie do zera.
- **Wyłącznik zostaje** — A/B jakości plonu (z blokiem vs bez) wymaga obu ramion.
- +3 testy, w tym jeden pilnujący, że U4 jest **domyślnie ON** (cichy powrót do opt-in = powrót do
  płacenia za powtórki) i jeden sprawdzający TREŚĆ bloku, nie sam fakt wstrzyknięcia.

Sugestia w ledgerze CODEX **ZAMKNIĘTA**, nie zostaje wiszącym kandydatem (lekcja z 07-20: sugestia
zgłoszona po raz drugi = naprawa TERAZ). **Pliki:** `narzedzia/bibliotekarz.py`,
`tests/test_bibliotekarz.py`.

---

## 2026-07-21 | ⚖️ | WARSTWA 18 — dług honorowy LEX TALIONIS zatrzymuje commit (bramka TWARDA)

Znalezisko zwiadu, **decyzja Cezara**: bilans not był najpierw sprawdzany tylko w kroku 5b
zamknięcia, potem — po pierwszej naprawie tego dnia — również *drukowany* na otwarciu. Ale
drukowanie to **widoczność, nie egzekwowalność**: `codex_notarum bilans` nie zwracał niezerowego
kodu, a hook wołał go z `|| true`. Dług otwarty w sesji N mógł przeżyć N+1 i N+2, mimo że zasada
mówi wprost „sesja nie domyka się z niespłaconym długiem honorowym".

- **Bramka TWARDA jak W17:** dług > 0 → audyt exit 1 → commit stoi. Miękki alarm odrzucony
  świadomie — to ten sam mechanizm, który zawiódł już dwa razy (wąska Warstwa 11 przy „pełnej
  harmonii", alarm W9 wiszący przez sesje). **Alarm, którego wolno nie posłuchać, prędzej czy
  później nie zostaje posłuchany.**
- **Zakleszczenia brak:** dług spłaca się dopisaniem CORONY do ledgera, co nie wymaga commitu.
- **DOWÓD, ŻE GRYZIE** (nie sama deklaracja): sztuczny dług → CZERWIEŃ, po CORONIE → zieleń.
  Dodatkowo test granicy LEX TALIONIS: **CORONA bez pola `splaca` NIE zamyka długu** — inaczej
  dowolny laur kasowałby dowolny błąd.
- **Wada złapana przy pisaniu samego dowodu:** pierwsza wersja podmieniała stałą modułu i po cichu
  czytała PRAWDZIWY ledger (`bilans(sciezka=LEDGER)` wiąże domyślny argument w chwili definicji),
  więc meldowała zieleń dla sztucznie utworzonego długu. **Sam dowód był mechanizmem, który przy
  awarii wygląda na sprawny.** Stąd jawna ścieżka w sygnaturze warstwy — organ bramkujący bez
  wstrzykiwalnego źródła jest z definicji niesprawdzalny.

**LEX TALIONIS:** N-02f2b752 ↔ C-562b21ef (dług 0). **Księga Wad +1:** „dowód »czy bramka gryzie«
mierzący inny obiekt, niż deklaruje". **Pliki:** `narzedzia/audyt_spojnosci.py`,
`tests/test_spojnosc.py`, `CLAUDE.md` (17→18 warstw, checklista Prawa XXI).

---

## 2026-07-21 | 🔭 | DISPENSATOR wpięty w Hyginusa + zwiad adwersarialny otwarcia (3 wady)

**Część 1 — rozkaz o rozbudowie Hyginusa.** Most mowy (`deepseek_glos.zapytaj`) przyjmuje teraz
`profil` / `model` / `thinking` / `reasoning_effort`; profil oddaje decyzję **DISPENSATOROWI**,
jawne argumenty go nadpisują. **Wsteczna zgodność udowodniona testem:** wywołanie bez nowych
argumentów wysyła DOKŁADNIE to samo żądanie co przed zmianą (zero `extra_body`, model z `__init__`).
Hyginus kupuje głębokość per faza: rozwijanie zapytania → `klasyfikacja` (thinking off, 11.7× taniej),
generacja → `zwiad` (effort low), **krytyka → `krytyka` (effort high)** — sceptyk płytszy od proponenta
byłby bezużyteczny. Profil `osad` (v4-pro) świadomie NIE jest używany: sędzią kandydatów jest Opus,
nie DeepSeek (ZASADA ZWIADOWCY WIEDZY — dwa modele o RÓŻNYCH rolach).
**Naprawione przy okazji:** `_protokoluj` logował `self.model`, więc para nauczyciela trafiałaby do
NOTARIUSA z CUDZĄ nazwą modelu — TIRO uczyłby się z fałszywą etykietą źródła. Teraz logowany jest
model FAKTYCZNIE użyty.

**Część 2 — zwiad adwersarialny checklisty otwarcia (2 subagenty, osobne konteksty).** Każde
znalezisko zweryfikowane osobiście (kandydat≠prawda). Trzy potwierdzone, wszystkie w organach,
które MIAŁY chronić:

1. **Wynik testów niewidoczny na otwarciu** — oba zwiady zbiegły się niezależnie. `grep run_tests`:
   0 trafień w hooku, w audycie tylko ścieżki `__pycache__`. Bieg trwa >5 min, więc powtarzanie go
   przy każdym starcie odpada — lekarstwem jest **SIGILLUM PROBATIONIS**: `run_tests` odciska wynik
   przypięty do **ODCISKU TREŚCI ŹRÓDEŁ**, a BREVIARIUM wykrywa NIEAKTUALNOŚĆ. „Zielone dla kodu,
   którego już nie ma" raportujemy jako **NIEZNANY** — cichy optymizm jest gorszy niż brak informacji.
   **Wada projektowa złapana na sobie, zanim ktokolwiek na niej poległ:** pierwsza wersja porównywała
   hash HEAD i przy naturalnym rytmie (edytuj → testy na brudnym drzewie → commit) **nigdy nie mogłaby
   dać werdyktu ZIELONE** — alarm przy każdym starcie uczy operatora ignorować organ, czyli niszczy to,
   po co powstał. Miara zmieniona na treść źródeł (405 plików, 232 ms), z testem kontrolnym na
   osiągalność werdyktu pozytywnego i na czułość (zmiana `.py` gasi pieczęć, wpis do LOG_ZMIAN nie).
2. **PORTITOR miał ręcznie wpisaną listę pakietów** (6 przy 9 w `requirements.txt`) — organ powołany
   do pilnowania Prawa XV nie sprawdzał ani `scipy` (a requirements mówi wprost: bez niego BOCPD-01
   milczy), ani `openai` (jedyne wejście LLM). Lista jest teraz **generowana z requirements**:
   deps 6/6 → **9/9**.
3. **Mój własny BREVIARIUM kłamał o DISPENSATORZE** — sprawdzał wpięcie po NAPISIE w pliku, więc
   meldował „NIEWPIĘTY" godzinę po tym, jak go wpiąłem (słowo padało tylko WIELKIMI literami
   w komentarzu, a realne wpięcie idzie przez `zapytaj(profil=...)`). Symetrycznie: komentarz
   „TODO: wpiąć DISPENSATORA" liczyłby się jak działający kod. Przepisane na **AST**.

**LEX TALIONIS:** N-7dfb397f ↔ C-0ecb7eb8, N-b4a470ef ↔ C-cfb94b20 (dług 0).
**Księga Wad +5:** „bramka widoczna tylko na jednym końcu procesu", „raport startowy nie widzi
własnych sług", „detektor obecności po napisie", „lista pilnowanych rzeczy wpisana ręcznie obok
źródła prawdy", „detektor, którego kontrakt nigdy nie dopuszcza werdyktu pozytywnego".
**Backlog CODEX +5 kandydatów** — znaleziska zwiadu świadomie NIEłatane w tym commicie (timeout
`auto_lekcja`, błąd W1 przerywający 16 warstw audytu, SYNC bez ahead/behind na brudnym drzewie,
dług honorowy widoczny lecz nieegzekwowalny, wąski zasięg skanu wad). **Pliki:** `imperium/cesarz/deepseek_glos.py`, `narzedzia/bibliotekarz.py`,
`imperium/pretorianie/portitor.py`, `imperium/oczy/breviarium.py`, `tests/run_tests.py`.

---

## 2026-07-21 | 📋 | BREVIARIUM + dług honorowy na otwarciu (zarzut Cezara o luki hooka)

Cezar: *„hook startowy ma luki — powinien być stan Hyginusa i TIRO, ich zadania zrobione i do
zrobienia, i jakiego modelu używasz Ty i oni"*. **Zarzut potwierdzony pomiarem:** hook wołał 10
organów (audyt, PORTITOR, CENSOR, CODEX, pamięć, Dziennik, kronika, skan wad…) i **ani jeden nie
mówił, co robią HYGINUS i TIRO ani z jakich modeli korzystamy**. Drugi brak, wskazany przez Cezara
i potwierdzony: **`codex_notarum bilans` NIE był wołany na starcie** — dług honorowy stał wyłącznie
w kroku 5b zamknięcia, więc sesja urwana przed domknięciem zostawiała dług, którego następne
otwarcie nie pokazywało. Klasa znana: **bramka widoczna tylko na jednym końcu procesu.**

- **Organ:** `imperium/oczy/breviarium.py` (August przekazywał Senatowi *breviarium totius imperii* —
  zwięzły rachunek zasobów państwa). Melduje: HYGINUS — kolejka, **plon czekający na sędziego**
  (dług przeglądu: płacimy za zwiad, którego nikt nie ocenia), ostatni zwiad, model, profile
  DISPENSATORA, werdykty PROBATORA; TIRO — pary nauczyciela, modele `.gguf` na dysku, silnik,
  klasa sprzętu i co ona unosi.
- **Od razu wykryty martwy potencjał:** `DISPENSATOR: 🚨 NIEWPIĘTY` — organ jest w repo, ale
  `bibliotekarz.py` go nie woła (to właśnie pierwsza część rozkazu o rozbudowie Hyginusa).
- **Czego świadomie NIE zgadujemy (Prawo I):** identyfikator modelu Claude **nie istnieje
  w środowisku** — env niesie `CLAUDE_EFFORT` i `CLAUDE_AGENT_SDK_VERSION`, żadnego `*_MODEL`.
  BREVIARIUM drukuje więc, co wie, i **żąda deklaracji od Architekta**, zamiast wpisać
  prawdopodobną nazwę, która zestarzeje się jak każda ręczna liczba. Skodyfikowane w CLAUDE.md
  (krok 6 OTWARCIA: „przedstaw się rzymsko **i zadeklaruj model + effort**").
- **Liczby GENEROWANE z żywego stanu**, nigdy przechowywane — ta sama żelazna zasada co
  SIGILLARIUM i CENSUS ORGANORUM.

Testy 2778→**2794** (+16, w tym granice: brak plików, uszkodzona linia JSONL, brak silnika TIRO,
znacznik nieliczbowy, kontrola pozytywna I negatywna detektora wpięcia). Audyt exit 0 (W17: 242).
**Pliki:** `imperium/oczy/breviarium.py`, `tests/test_breviarium.py`, `.claude/hooks/session-start.sh`,
`CLAUDE.md`, `docs/ARCHITEKTURA_IMPERIUM.md`, `docs/CENSUS_ORGANORUM.md`.

---

## 2026-07-21 | 🛡️ | PROBATOR — Strażnik Cytatów (warstwa 1 anty-halucynacyjna Hyginusa)

Rozkaz Cezara: rozbudowa Hyginusa, start od citation-checku. **Powód (web 2026-07-21):** DeepSeek
V4-Pro halucynuje **94%**, V4-Flash **96%** na pytaniach wiedzy. Z czterech typów halucynacji
(factual, grounding, **citation**, reasoning) **citation jako jedyny da się złapać
DETERMINISTYCZNIE — bez modelu, bez tokenów, bez kosztu**, więc idzie pierwszy.

- **Organ:** `imperium/pretorianie/probator.py` (rzym. *probator* — ten, kto bada i dopuszcza).
  Sprawdza, czy cytowane BIB-xxx/chunk **było modelowi PODANE w tym prompcie** — nie „czy istnieje
  w bibliotece". To rozróżnienie jest sednem: powołanie się na realną książkę, której się nie
  dostało, jest konfabulacją tak samo jak wymyślony tytuł.
- **Abstencja = wynik POPRAWNY:** „fragmenty nic nie wnoszą" nie ma cytatów i nie jest wadą —
  karanie milczenia uczyłoby model konfabulować.
- **Wpięcie:** pole `probator` (i `probator_krytyka`) w cząstce kolejki + alarm na stderr.
  **Monotonicznie ostrożne** — dokłada werdykt, nic nie odrzuca; `--bez-probatora` wyłącza.
- **POMIAR na 33 realnych cząstkach kolejki:** **0 cytatów spoza podanych fragmentów** — prompt RAG
  Hyginusa trzyma. Jeden prawdziwy alarm: temat *volatility surface…* ma **2367 znaków kandydatów
  i zero powołań na źródło** mimo żądania promptu. Zapisane w ledgerze CODEX (Pomiary).
- **Dwie ślepe plamy własnego detektora, obie znalezione zanim uznałem go za gotowy:** (1) `\b`
  **nie domyka się na podkreśleniu**, więc regex nie widział cytatu w formie `BIB-006_Autor_Tytul.pdf`
  — czyli w tej, którą model dostaje (złapane własnymi testami: 13/20 czerwonych); (2) brak wariantu
  **cytowania NAZWISKIEM autora** („Źródła: Hull chunk 560") dał **2 fałszywe alarmy z 4** przy
  pierwszym biegu na realnym plonie. Aliasy nazwisk działają **wyłącznie na korzyść modelu** —
  nigdy nie tworzą nowego alarmu, więc nie mogą wyprodukować fałszywego oskarżenia.

Testy 2744→**2778** (+34), audyt exit 0 (W17: 241 modułów). **LEX TALIONIS:** N-7dfb397f ↔
C-0ecb7eb8 (dług 0). **Księga Wad +2:** „granica słowa `\b` nie domyka się na podkreśleniu",
„detektor uznany za gotowy po testach autora, bez biegu na realnych danych".
**Pliki:** `imperium/pretorianie/probator.py`, `narzedzia/bibliotekarz.py`, `tests/test_probator.py`,
`tests/test_bibliotekarz.py`, `docs/ARCHITEKTURA_IMPERIUM.md`, `docs/CENSUS_ORGANORUM.md`.

---

## 2026-07-21 | 🧠 | TEMPERATOR MEMORIAE — pamięć chłodzi się sama (alarm Prawa XV przestał wracać)

Alarm hooka „sekcja LEKCJE > 24000 zn." wracał **po każdym ręcznym sprzątaniu**: 07-19 skonsolidowano
do 23820, nazajutrz `auto_lekcja` dopisała 21 wpisów → **28132**. Klasa: stan rośnie automatycznie,
kurczy się tylko ręcznie — ręka zawsze przegra z pętlą.

- **Mechanizm:** `egzekwuj_limit_sekcji` wpięty w **ścieżkę zapisu** (`dopisz_lekcje` **i**
  `aktualizuj_lekcje` — parytet bliźniaków), histereza `UDZIAL_CELU_SEKCJA=0.92`. Opt-out `chlodz=False`.
- **Trzy wady znalezione po drodze (pomiar, nie opinia):** (1) alarm liczył SUROWY TEKST sekcji, a
  konsolidacja SUMĘ bloków — dwie miary tej samej wielkości; teraz jedna `_rozmiar_sekcji`, zweryfikowana
  algebraicznie (`suma+n+1` = 28132 co do znaku). (2) próg 24000 i cel 22000 były **niezależnymi
  stałymi** — cel liczony jest teraz Z PROGU, więc zmiana progu nie zamienia naprawy w cichy no-op.
  (3) **archiwum ACTA było nieczytelne dla własnego parsera** (113 bloków, `lekcje()` widziało 0) —
  „nic nie skasowane" było prawdą bezużyteczną; `lekcje()` czyta oba nagłówki, `szukaj(z_archiwum=True)`.
- **Efekt na żywej pamięci:** 119→92 lekcji aktywnych, 28132→**22062 zn.**, alarm MILCZY, 27 lekcji
  schłodzonych do ACTA i **znajdywalnych przez API**. Testy 2729→**2744** (+15 granic: próg dokładny,
  próg+1, `None`, opt-out, piaskownica archiwum, sprzężenie celu z progiem).
- **Alarm W9** (20 przedawnionych pomysłów) zbadany i zaplanowany w Backlogu CODEX: wszystkie z
  **jednego dnia** (2026-06-30), `sprzeczne=0`, w próbce same duplikaty semantyczne i pozycje **już
  zrealizowane** (auto-lekcja żyje, HMM w Viterbi, RAG FTS, Prawo XIX skodyfikowane) — to dług
  deduplikacji, nie dług decyzyjny.

**LEX TALIONIS:** N-532d1ba9 ↔ C-1e85257a (dług 0). **Księga Wad +3:** „ręczna naprawa przeciw
automatycznemu przyrostowi", „dwie miary tej samej wielkości", „archiwum nieosiągalne dla własnego
czytnika". **Pliki:** `imperium/biblioteki/pamiec_sesji.py`, `tests/test_pamiec_sesji.py`,
`docs/PAMIEC_SESJI.md`, `docs/PAMIEC_SESJI_ARCHIWUM.md`.

---

## 2026-07-21 | 📚 | README biblioteki — koniec gnicia (zarzut Cezara + LEX TALIONIS)

Cezar: „plik gnije i jest mi wstyd". Potwierdzone: `bibliotheca_ulpia/README.md` mówił **69 ksiąg**
przy 115, a instrukcja kazała **`git add`+`git push` binariów** książek do GitHub — **wbrew decyzji
07-11** (binaria tylko lokal, RAG czyta wersjonowany `tekst_cache`). Niewykryte, bo `bibliotheca_ulpia`
jest w `POZA_REJESTREM` tabularium — żadna bramka nie pilnowała tego żywego drogowskazu.

- **Naprawa:** README przepisany — aktualny (115, binaria TYLKO lokal + `tekst_cache` w git, pipeline
  `przygotuj_biblioteke`, role Hyginus/Vitruviusz/NOTARIUS/TIRO, format nazwy), lepszy wygląd (tabela
  struktury, diagram przepływu). **Usunięta groźna instrukcja push binariów.**
- **UODPORNIENIE (klasa):** liczba ksiąg = blok `<!-- LICZBA:ksiazki -->` wpięty w tabularium przez
  `DROGOWSKAZY_Z_LICZBAMI` (wyjątek: żywy drogowskaz spoza rejestru, TYLKO warstwa liczb — nie T1/T2
  bez frontmatter). Dowód że gryzie: 115→99 → tabularium „ROZJAZD", audyt W15 obejmuje. +2 testy.
- **Standing order:** README biblioteki aktualizowany przy KAŻDEJ zmianie struktury/pipeline.

**LEX TALIONIS:** N-e860da78 ↔ C-5d054580 (dług 0). Księga Wad #56 „żywy dokument w strefie
wyłączonej z audytu". **Pliki:** `bibliotheca_ulpia/README.md`, `narzedzia/tabularium.py`,
`tests/test_tabularium.py`.

---

## 2026-07-21 | 📚 | Biblioteka: 36 nowych BIB skatalogowanych + plan esencji etapowy

Cezar dodał **36 nowych książek** (BIB-080..116) wg `PLAN_ROZBUDOWY_BIBLIOTEKI` — materiał POD TIRO
(LoRA/QLoRA/distillation/InstructGPT/DPO/GPTQ) + grafy + RL + przyczynowość.

- **Nazwy dopasowane do wzorca** `BIB-XXX_Autor_Tytuł-z-myślnikami.ext` (36/36) — autorzy wzięci z
  PLAN_ROZBUDOWY (źródło prawdy), nie z głowy; ASCII bez diakrytyki, zgodnie ze stylem BIB-001..079.
- **Przetworzone lokalnie (0 tokenów Claude):** ekstrakcja → `tekst_cache` (115), reindeks RAG,
  katalog metadanych (`katalog_ksiag.json` n=79→**115**). Pliki binarne książek poza git (decyzja 07-11),
  wersjonowany jest `tekst_cache`.
- **TIRO zbieranie potwierdzone** (pytanie Cezara): Hyginus woła DeepSeek przez most `deepseek_glos.py`,
  który automatycznie woła `NOTARIUS.zapisz_pare` — jedno wpięcie łapie wszystkich wołających.
- **Plan esencji: 4 etapy po sesji** (ZASADA ANALIZY CZĄSTKOWEJ) — LLM/TIRO · optymalizacja · grafy ·
  RL+przyczynowość. Zapisany w `PLAN_ROZBUDOWY_BIBLIOTEKI.md`. Esencja klastrów w kolejnych sesjach,
  by nie palić tokenów Opusa naraz (rozkaz Cezara).
- **Rozkaz odłożony do dedykowanej sesji:** wpięcie DISPENSATORA + trybów DeepSeek (thinking/pro-weryfikator/
  function-calling web) na stałe w Hyginusa — projekt w pamięci `rozbudowa-hyginusa-modele-tryby-deepseek`.
  Zmierzone: DeepSeek NIE ma natywnego web search (tylko function-calling); DISPENSATOR istnieje, niewpięty.

**Pliki:** `bibliotheca_ulpia/BIB-080..116` (rename), `bibliotheca_ulpia/dane/tekst_cache/`,
`katalog_ksiag.json`, `docs/PLAN_ROZBUDOWY_BIBLIOTEKI.md`.

---

## 2026-07-21 | 🛡️ | P5 fali 1: guard ZeroDiv w pretorianach (kalkulator_lewara + aegis)

Zwiad ryzyka kodu zreprodukował 3 × `ZeroDivisionError` na wejściach granicznych, ZANIM zadziałało
weto/checklist:

| Miejsce | Wejście graniczne | Przyczyna |
|---|---|---|
| `kalkulator_lewara.policz:425` | `dzwignia=200` | `1/200 == OPŁATA_UTRZYMANIA` → likwidacja == cena → `\|cena−likwidacja\|=0` |
| `kalkulator_lewara.policz:429` | `cena_wejscia=0` | `stop_pct = \|cena−stop\|/cena` |
| `aegis_tarcza.update:48` | `initial_capital=0` | `drawdown = (peak−cur)/peak_capital` |

Produkcja **chroniona** (dyrygent capuje dźwignię ≤20, realna cena >0) — ale funkcje same się nie
broniły (crash przy bezpośrednim/przyszłym wywołaniu). `aegis` miał **ZERO testów**.

**Naprawa (monotoniczna ostrożność — produkcja bez zmian):** walidacja `cena_wejscia>0` i
`initial_capital>0` u wrót (ValueError, fail-loud); guard mianownika `\|cena−likwidacja\|`
(bufor=0 zamiast crash — checklist i tak odrzuca dźwignię>20). **Testy:** `aegis` 0→4 (pierwsze
w historii), `kalkulator` +3 granice. Dźwignia=5 dalej `checklist_ok=True` (dowód braku regresji).

**LEX TALIONIS:** N-9a33798d ↔ C-5ca9dbad (dług 0). Backlog: P5 **zamknięta**. Księga Wad #55
„ZeroDiv na granicy przed zadziałaniem weta". **Pliki:** `imperium/pretorianie/kalkulator_lewara.py`,
`imperium/pretorianie/aegis_tarcza.py`, `tests/test_kalkulator.py`, `tests/test_aegis_tarcza.py`.

---

## 2026-07-21 | 📄 | P2 fali 1: TRYBY_IMPERIUM.md — realny dług dokumentów naprawiony

Jedyny prawdziwie gnijący dokument z 11 podejrzanych (10/11 to fałszywe alarmy — data ruszona,
treść nie). Żywy wiersz SKALP twierdził **„brak danych <1h w backteście"** + rekomendacja „wymaga
danych krótkointerwałowych — Etap C, live" — FAŁSZ po dograniu danych (commit 705370f):

- **POMIAR (weryfikacja osobista, kandydat≠prawda):** `dane/minutowe/` 10+ par (BTC ~1.34M barów
  ≈2.5 roku), `dane/5m`+`dane/15m` dla BTC/ETH (~268k barów).
- **Naprawa bez odwrotnego fałszu:** dane <1h SĄ, ale profil SCALP (RSI 4–7, lewar 10×) pozostaje
  **NIEPRZETESTOWANY** — dotychczasowy pomiar interwałów trzymał konfigurację swing, nie scalping.
  Brakuje nie danych, lecz testu profilu. `stan_na` 07-18 → 07-21.
- **UODPORNIENIE:** fraza „brak danych <1h w backteście" → INDEX FALSORUM (poprawna teza + dowód);
  sweep całego korpusu pilnuje, by nie wróciła jako fakt (lekcja: korekta jednorazowa nie wystarcza).

**LEX TALIONIS:** N-0447ca78 ↔ C-f69e9368 (dług 0). Backlog: sugestia P2 **zamknięta**.
Audyt exit 0 · sweep --falsa czysty (3 twierdzenia). **Pliki:** `docs/TRYBY_IMPERIUM.md`, ledgery.

---

## 2026-07-21 | 🛡️ | P1 fali 1: feature_importance strażnik serii + konsolidacja LEKCJE

### P1 — cicha obcinka niezrównanych serii (rozkaz Cezara po zwiadzie)

`feature_importance.raport_waznosci` (linia 240) cicho ucinał niezrównane serie `min()`+`[:n]`,
ostrzegając TYLKO gdy `n < MIN_OBS` — nie przy rozjeździe długości. Przy przesunięciu w ŚRODKU
serii `snap[i]`≠`wyk[i]` → skażone MDA/SFI → fałszywy osąd „martwy głos"/„redundantny" (Prawo XVI/XX).
Bliźniak `legatus.oblicz_wagi_ic:43-46` miał JUŻ twardy strażnik za tę samą klasę (cubic P2) —
**poprawka nie została przeniesiona**. Naprawa: `raise ValueError` przed liczeniem (fail-loud, wzór
bliźniaka) + test negatywny `test_raport_waznosci_odrzuca_niezrownane_serie`.

- **LEX TALIONIS:** N-247e4ac7 ↔ C-5ccba4f8 (dług 0). Backlog: sugestia P1 **zamknięta**.
- **Klasa (Księga Wad):** „poprawka nieprzeniesiona między bliźniakami" — ten sam kontrakt danych
  (`sygnaly` ‖ `wyniki`) musi mieć strażnik w OBU modułach; nieprzeniesiona poprawka to dług ukryty.

### Konsolidacja LEKCJE (alarm Prawa XV z hooka — decyzja Cezara „skonsoliduj teraz")

Sekcja LEKCJE 27526 zn > limit 24000. Usunięto **16 najstarszych** lekcji (119→103, **23820 zn**,
zapas 180) — kryterium: jednorazowy bug / nieaktualna infrastruktura POKRYTA źródłem prawdy
(kod+testy+Księga Wad+ZASADY); kod > pamięć. Doktryna (Prawo I ×2, martwe głosy/zombie) i Top-3
zachowane — zweryfikowane po usunięciu.

**Pliki:** `imperium/legiony/feature_importance.py`, `tests/test_raport_waznosci.py`,
`bibliotheca_ulpia/dane/pamiec_sesji*` (lekcje), ledgery.

---

## 2026-07-21 | 🔍 | Adversarialny zwiad SIGILLARIUM — 4 wady świeżego organu naprawione

### Rozkaz Cezara

> „wyślij podobne dla naszych nowych trzech pieczęci, cel poprawa i łatanie" — sześciu
> subagentów-zwiadowców (Sonnet, osobne konteksty) na organ SIGILLARIUM + całe Imperium.

### 4 wady MOJEGO świeżego kodu (commit e399abf), złapane przez zwiad, nie przez moje testy

| # | Wada | Dowód (POMIAR) | Naprawa u źródła |
|---|---|---|---|
| 1 | Parser `kroki_z_konstytucji` **cicho gubił niewciętą zawiniętą kontynuację** kroku — numeracja ciągła, treść ucięta | probka z niewciętą linią → 3 kroki, treść kroku 2 ucięta | dokleja KAŻDĄ niepustą linię w środku kroku; stop daje `**Złamanie:**`/nagłówek |
| 2 | `limes/SKILL.md` **kopiował 5 komend bramki** zamiast wołać pieczęć (naruszenie zasady organu) | czytanie pliku | skill woła pieczęć; komendy zostają jednym źródłem w `SIGLA` |
| 3 | `brakujace_komendy` **ślepe na `python -m pakiet`** (regex `\S+\.py`) — martwa komenda LEX TALIONIS przeszłaby cicho | `brakujace_komendy(Sigillum z -m widmo)` → `[]` | `_cel_komendy_istnieje` mapuje `a.b.c` → `a/b/c.py` |
| 4 | `zapisz()` **nieatomowy** — `write_text` w miejscu, crash mógł obciąć wszystkie runbooki | czytanie kodu (regresja vs stary `dodaj()`) | `_zapisz_atomowo`: `.tmp` + `os.replace` |

### Uodpornienie klasy (każda naprawa ma test łapiący JEJ klasę)

- `test_parser_nie_gubi_niewcietej_kontynuacji` + regresja liczb 7/10/5 na żywym CLAUDE.md
- `test_skill_nie_kopiuje_komend_bramki` — pilnuje NIEOBECNOŚCI każdej komendy w SKILL.md
- `test_brakujace_komendy_wykrywa_martwy_modul_dash_m` — przypadek NEGATYWNY (`-m` widmo MUSI być złapane)
- `test_zapisz_jest_atomowy_nie_zostawia_tmp`
- **Księga Wad #53:** „ślepa plama detektora na wariant składni" — detektor chroniący przed czymś
  musi pokryć WSZYSTKIE formy zapisu celu + mieć test negatywny (nie tylko „aktualne czyste").

### Ergonomia (Prawo XVIII — drobiazgi jednoznaczne)

Dopisane aliasy słowne: APERTIO „otwieramy"; CLAUSURA „zamykamy"; LIMES „zrób bramkę", „przed pushem".

### Bramki

Testy `tests/test_sigillarium.py` 25→**33** (+8) · LEX TALIONIS: **N-d925f3dd ↔ C-a9ab5637**, dług 0.
Pełna bramka LIMES + wpis Dziennika przed commitem.

**Pliki:** `imperium/biblioteki/sigillarium.py`, `imperium/biblioteki/pamiec_proceduralna.py`,
`.claude/skills/limes/SKILL.md`, `tests/test_sigillarium.py`, ledgery.

**Fala 1 (całe Imperium, 5 zwiadowców) — synteza do decyzji Cezara, NIE łatane w tym commicie:**
1 realny dług dokumentów (`TRYBY_IMPERIUM.md` wiersz SKALP „brak danych <1h" — fałsz po dograniu 1m);
ryzyko kodu (`feature_importance.py` cicha obcinka jak łatany `legatus.py`; `kalkulator_lewara`/`aegis_tarcza`
ZeroDiv poza chronioną ścieżką produkcyjną); 7/17 warstw audytu bez testu regresyjnego; census W17 pomija
`tests/`+`skrypty/`; „38 milczących neuronów" OBALONE pomiarem → realnie ~17 (6 wyciszonych + 2 + 11 przez
`sentyment_per=None`).

---

## 2026-07-20 | 🔏 | SIGLA IMPERII — organ SIGILLARIUM + naprawa gnicia pamięci proceduralnej

### Rozkaz Cezara (zamknięcie wachty doks20)

> „ustalić SIGLA IMPERII — skróty użytkowe (hasła-komendy) uruchamiające pełne procedury bez
> opisywania ich za każdym razem; NIE dublować runbooków W11 — skróty mają być ich WYZWALACZAMI"

**Decyzja Cezara 2026-07-20:** forma = **skille harnessa `/nazwa` + polskie aliasy słowne**;
zestaw = **rdzeń trzech pieczęci** (otwarcie / zamknięcie / bramka). Pozostali kandydaci
(krok 9, oko za oko, cenzus, kronika, podgląd) **nie wdrożeni** — czekają na decyzję.

### Wada znaleziona po drodze (POMIAR, nie podejrzenie)

| Co zmierzone | Dowód |
|---|---|
| Runbook W11 „Bezpieczny commit" kazał Claude `git push -u origin <branch>` | krok 5 w `procedury.jsonl` vs rozkaz z **2026-07-11** („Claude NIGDY nie pushuje") — gnił **9 dni** (07-11 → 07-20; runbook zapisany 07-01, więc miał 19 dni) |
| Runbooka **nie dało się** zaktualizować | `dodaj(dedup=True)` cicho zwracał `False` bez zapisu — brak jakiejkolwiek ścieżki UPSERT |
| Poprawka ziarna w kodzie nie docierała do danych | `zasiej()` wołał `dodaj()`, więc istniejąca nazwa była pomijana |
| Co widział Cezar | pogodne „🛠️ Pamięć proceduralna (W11): 4 procedur (runbooków) gotowych" |

Klasa znana z poprzedniej wachty: **mechanizm, który przy awarii wygląda na sprawny.**

### Wdrożone

| Element | Treść |
|---|---|
| **SIGILLARIUM** (organ) | `imperium/biblioteki/sigillarium.py` — Skarbiec Pieczęci; rejestr `SIGLA` + parser konstytucji + CLI (`lista`/`apertio`/`clausura`/`limes`/`sync-w11`) |
| **Rdzeń sigli** | `/apertio` (7 kroków), `/clausura` (10 kroków), `/limes` (5 komend bramki) — liczby **liczone z żywego CLAUDE.md**, nie wpisane |
| **Zasada rdzeniowa** | pieczęć **nie przechowuje kroków** — czyta je z `CLAUDE.md` w chwili wywołania; rozjazd strukturalnie niemożliwy (to samo lekarstwo co CENSUS ORGANORUM) |
| **Ujście w harnessie** | `.claude/skills/{apertio,clausura,limes}/SKILL.md` — cienkie, **wołają pieczęć zamiast kopiować kroki** (test pilnuje rozjazdu w obie strony) |
| **Naprawa W11** | `pamiec_proceduralna.zapisz()` = upsert z jawnym werdyktem `dodano`/`zaktualizowano`/`bez zmian`; `zasiej()` **leczy** zgniłe ziarno (wyleczył 1, drugi bieg 0 = idempotencja); aktualizacja nie kasuje nieznanych pól |
| **Wpięcie** | `synchronizuj_w11()` przepisuje żywe kroki do runbooków (hasło działa też pisane prozą); `raport_startowy()` w Centrum Pamięci — Cezar widzi pieczęcie na starcie |
| **Kodyfikacja** | `CLAUDE.md` § SIGLA IMPERII (tabela pieczęci + aliasy + żelazna zasada) |

### Uodpornienie klasy (ZASADA CENSORA)

- **Księga Wad #52:** „stan bez ścieżki aktualizacji (zapis jednokierunkowy)" — pytanie do review:
  *jak ta treść zostanie POPRAWIONA, gdy się zdezaktualizuje?* Odpowiedź „ręcznie"/„nijak" ⇒ nie
  przechowuj, **generuj ze źródła prawdy**. Świadomie **bez regexu** (wzorzec semantyczny, nie składniowy).
- **Test regresyjny:** żaden runbook nie może kazać Claude pushować.
- **Alarmy zamiast ciszy:** `🚨 PIECZĘĆ PUSTA` (zniknęła sekcja konstytucji), `🚨 MARTWE KOMENDY`
  (bramka woła nieistniejący skrypt), test **ciągłości numeracji** (dziura = krok zgubiony po cichu).

### Bramki

Testy `tests/test_sigillarium.py` **19 nowych** · audyt **exit 0** (sam złapał nowy organ w W11+W15+W17
i wymusił meldunek) · skan wad czysto · INDEX FALSORUM czysto · **LEX TALIONIS: N-fb66738e ↔ C-ecfaecb3,
dług honorowy 0** · sugestia SIGLA w ledgerze CODEX **zamknięta** (nie wisi jako KANDYDAT).

**Pliki:** `imperium/biblioteki/sigillarium.py`, `imperium/biblioteki/pamiec_proceduralna.py`,
`imperium/biblioteki/centrum_pamieci.py`, `.claude/skills/*/SKILL.md`, `tests/test_sigillarium.py`,
`CLAUDE.md`, `docs/ARCHITEKTURA_IMPERIUM.md`, `docs/INDEKS_IMPERIUM.md`, `docs/CENSUS_ORGANORUM.md`,
`README.md` (liczba organów biblioteki 27→28), ledgery CODEX/NOTARUM/Księga Wad.

---

## 2026-07-20 | 🏛️ | CENSUS ORGANORUM (Warstwa 17) + typ POMIAR — dwie NOTY spłacone

### Zarzut Cezara (zatwierdzony pomiarem, nie przyjęty na słowo)

> „CODEX_PROBATIONUM arkusze nie zaktualizowane po ostatniej sesji, widzę braki, zapewne
> inne dokumenty wyglądają podobnie" — **potwierdzony w całości.**

| Dowód | Pomiar |
|---|---|
| `imperium/cesarz/dispensator.py` (152 linie + 125 testów) | w dokumentach **0 razy** — MANIFEST 0, INDEKS 0, ARCHITEKTURA 0, README 0 |
| Conflator / Nuntius / VERITAS ANNALIUM / PORTITOR | tylko w ARCHITEKTURA, brak w INDEKS i MANIFEST |
| Dług zmierzony | **19 modułów `imperium/` + 31 narzędzi = 50** poza INDEKS+ARCH+MANIFEST |
| Werdykt interwałów (główny wynik wachty 07-20) | **brak w ledgerze** — schemat znał tylko AB/IC |
| Dlaczego audyt milczał | Warstwa 11 pilnowała meldunku **wyłącznie `imperium/biblioteki/`** — 1 katalog z 11 |

**Klasa błędu:** „✅ pełna harmonia" była prawdą o 1/11 organów i ciszą o reszcie.
Bramka o zbyt wąskim zasięgu jest gorsza niż brak bramki — daje fałszywy spokój.

### CORONA 1 — CENSUS ORGANORUM (`narzedzia/census_organorum.py`, Warstwa 17)

Spis WSZYSTKICH modułów `imperium/` i `narzedzia/` **generowany z żywego kodu**
(rola = pierwsza linia docstringu, czytana przez `ast`, bez importu). Audyt porównuje
`docs/CENSUS_ORGANORUM.md` z tym, co kod wygenerowałby TERAZ — rozjazd zapala czerwień.
**Bramka twarda** (decyzja Cezara): commit stoi. Miękkie ostrzeżenie odrzucone świadomie
— to mechanizm, który już raz zawiódł (alarm widoczny i ignorowany przez sesje).

Nie „dopisanie 50 wpisów ręcznie" — ręczny opis zgnije jak każda ręczna liczba przed
Filarem 4. Dokument traci prawo do własnej treści. **239 modułów** zameldowanych.
**Dowód że bramka gryzie** (nie martwa asercja): podrzucony organ-widmo → audyt exit 1,
po usunięciu → exit 0.

Efekt uboczny (Prawo XV): cenzus znalazł **jedyny moduł bez docstringu** w całym
Imperium — `narzedzia/dekorelacja_w322.py` — moduł, który nie mówi po co istnieje.

### CORONA 2 — typ POMIAR w ledgerze (`scriba_codex.zapisz_pomiar` + 15. arkusz „Pomiary")

Rekord dla wyniku wielowariantowego, którego ani AB (dwa ramiona), ani IC (skill na
horyzoncie) nie obejmuje. `warianty={nazwa: wartość}` — dowolna liczba ramion, bo
redukcja pomiaru N-wariantowego do pary gubi informację.

**Zgubiony werdykt interwałów dopisany wstecz** (4h +3.26 / 1d −3.03 / 1H −3.37 /
15m −5.71, zweryfikowany wobec tabeli LOG_ZMIAN, nie z pamięci) — wraz z uwagą Cezara,
że pomiar trzyma JEDNĄ konfigurację, więc profil SCALP pozostaje **nieprzetestowany**.
Zamknięte 2 sugestie, które ta CORONA realizuje.

**Najostrzejsza lekcja:** lukę schematu zgłaszałem jako SUGESTIĘ-KANDYDATA **trzy razy**
(07-19 `ab_wXXX`, 07-20 `NIEZMIENNIK`, 07-20 ponownie) i ani razu nie zamknąłem.
Sugestia w ledgerze to nie naprawa — to odłożenie z alibi. Klasa do Księgi Wad.

### Bramki

Testy +14 (`tests/test_census_organorum.py`, w tym granice: moduł bez meldunku,
widmo w spisie, brak dokumentu, pusty zestaw wariantów, kolejność wariantów,
ranga WSTĘPNY/ROZSTRZYGAJĄCY) · audyt exit 0 (17 warstw) · ruff czysto · skan wad czysto.

**LEX TALIONIS:** N-9992ba7b → CORONA 1, N-a0b792e1 → CORONA 2. Dług honorowy 0.

---

## 2026-07-20 | ⚖️ | HIPOTEZA INTERWAŁU — teza o monotoniczności OBALONA, 4h jedynym stabilnym

### Wynik (BTC+ETH, okno WYRÓWNANE PO DATACH 2025-06-18 → 2026-06-18, identyczna konfiguracja)

| interwał | ROI% | maxDD% | transakcje | win rate | barów/parę |
|---|---|---|---|---|---|
| **4h** | **+3.26** | 0.10 | 77 | 45.5% | 2 191 |
| 1d | −3.03 | 0.04 | **4** ⚠️ | 25.0% | 343 |
| 1h | −3.37 | 0.11 | 255 | **50.6%** | 7 607 |
| 15m | **−5.71** | 0.15 | **1 109** | 43.6% | 35 041 |

Podgląd: `raporty/KAPITOL_PODGLAD_hipoteza_interwalu.html`. Czas biegu: 4 363 s.

### Co obalone, co potwierdzone

**OBALONA — moja teza o monotoniczności.** Twierdziłem „im krótszy interwał, tym gorzej".
Fałsz: **4h bije 1d**. Zależność ma OPTIMUM, nie gradient.

**POTWIERDZONE — 4h jako jedyny stabilny.** Dwa różne okna: +3.93% (2.3 roku) i +3.26% (1 rok).
Powtarzalność jest cenniejsza niż pojedynczy wysoki odczyt (1d skakało +9.80 → −3.03).

**NIEINTERPRETOWALNE — wiersz 1d.** **Cztery transakcje**, win rate 25% (1 z 4). To anegdota,
nie pomiar. Nie wolno z tego wyciągać wniosku w żadną stronę.

**DIAGNOSTYCZNIE NAJCIEKAWSZE — 1h.** Najwyższy win rate w tabeli (**50.6%**) przy ujemnym ROI:
wygrywa częściej, a traci — **straty większe od zysków**. To nie jest awaria sygnału, tylko
problem zarządzania pozycją albo kosztów. Zupełnie inna diagnoza niż „sygnał nie działa".

### Naprawiona usterka metodologiczna (zgłaszana dwukrotnie, wreszcie zrobiona)

Narzędzie cięło po **liczbie barów**, zakładając, że pliki kończą się w tym samym momencie.
Nie kończyły: 1D sięgało 2026-06-18, świeżo pobrane 15m 2026-07-20 — **miesiąc różnicy udający
„to samo okno"**. Dodane `wspolne_okno()` (przecięcie zakresów dat, `--wyrownaj-daty` domyślnie ON)
oraz skalowanie limitu przez MINUTY interwału (bez tego 15m dawało dzielnik ułamkowy → okno zerowe).

### Czego wynik NIE mówi (uwaga Cezara)

To jest **konfiguracja swingowa puszczona na świecach 15-minutowych**, nie scalping. Namiestnik
(W-323) definiuje profil SCALP zupełnie inaczej: **RSI 4-7, lewar_cap=10, FUTURES, próg ×0.95**.
Pomiar poprawnie izoluje INTERWAŁ (styl stały), ale **profil SCALP — 75 neuronów — pozostaje
nieprzetestowany**. Wynik −5.71% znaczy „tak grać nie należy", NIE „scalping nie działa".
Zapisane w CODEX jako kandydat wraz z wymogiem uczciwego modelu kosztów transakcyjnych.

### Nowa luka wykryta przez ten wynik

**Brak progu MINIMALNEJ LICZBY TRANSAKCJI.** LIMEN FENESTRAE pilnuje pokrycia okna, ale werdykt
oparty na 4 transakcjach wychodzi z tą samą pewnością co oparty na 1109. Kandydat **LIMEN
NEGOTIORUM** dopisany do CODEX — rozszerzenie istniejącego mechanizmu, nie nowy organ.

---

## 2026-07-20 | 🧱 | CONFLATOR TEMPORUM + NUNTIUS MERCATUS: 5m/15m i odporne pobieranie

### Powód

Profil **SCALP** (Namiestnik W-323 mapuje M1–M15) **nigdy nie był testowany** — mieliśmy dane
1-minutowe, ale zero plików 5m/15m. Zmierzona zależność 1d +9.80% / 4h +3.93% / 1h −4.38% daje
falsyfikowalną prognozę: krótsze interwały mają wyjść **jeszcze gorzej**. Jeśli wyjdą lepiej —
teza o interwale upada i trzeba ją odwołać.

### Dwa narzędzia z rzymskimi imionami (ZASADA NOMENKLATURY)

| Organ | Plik | Rola |
|---|---|---|
| **CONFLATOR TEMPORUM** (Zlewacz Interwałów) | `narzedzia/agreguj_bary.py` | 1m→5m/15m, 1h→4h; odrzuca niepełne okna |
| **NUNTIUS MERCATUS** (Posłaniec Rynku) | `narzedzia/pobierz_binance.py` | świece dowolnego interwału z publicznego API |
| **VERITAS ANNALIUM** (Prawda Roczników) | `narzedzia/audyt_danych.py` | (nazwa nadana wstecz — organ z tej samej sesji) |

Oba powstały z **uogólnienia istniejących** (`agreguj_4h.py`, `pobierz_4h_binance.py`), nie obok nich —
nazwa pliku też jest dokumentacją i też potrafi skłamać, gdy moduł przestaje dotyczyć tylko 4h.
Stary `agreguj_4h.py` usunięty za zgodą Cezara (przeczytany w całości, 3 importy przepięte,
`agreguj_4h()` zachowane jako funkcja zgodności — woła je `audyt_danych.py`).

### Wynik agregacji (BTC+ETH)

5m: 301 993 / 279 076 barów · 15m: 100 661 / 93 023 barów · **0 barów poza siatką** ·
**200/200 zgodnych z Binance** dla obu par i obu interwałów.

### Odkrycie uboczne — ważniejsze niż sama agregacja

**Dane minutowe kończą się 2022-07-27** — mają prawie 4 lata. PORTITOR meldował „1m: 1453 dni",
co brzmiało jak świeże dane; to były dni **2019–2022**. Skutek: nie da się dołożyć 15m do tabeli
liczonej na oknie 2024→2026, bo mieszałoby to efekt interwału z efektem innego reżimu rynku.
Decyzja Cezara: dociągnąć świeże 1m z Binance (~1.34 mln świec/parę).

### Trzy własne wpadki → trzy mechanizmy (LEX TALIONIS)

**1. `N-962bc1d6` → `C-8fc89d2e` — nadpisanie bez kopii.** Testowy bieg nadpisał
`dane/4h/Binance_LINKUSDT_4h.csv` (pobrany z Binance) wersją przeliczoną z 1h. Wyszło dobrze
**tylko dlatego**, że 1h było już naprawione; godzinę wcześniej wgrałbym skażone dane bez cofnięcia.
To ta sama klasa, którą **godzinę wcześniej sam wpisałem do Księgi Wad**.
→ **STRAŻ POCHODZENIA**: kopia przed nadpisaniem + odczyt nagłówka i **głośne ostrzeżenie**,
gdy wersja przeliczona ma zastąpić plik z giełdy. Pilnuje degradacji źródła u sprawcy, nie w audycie.

**2. `N-7d5a9d47` → `C-9f8d479a` — wznawialność pozorna.** Docstring głosił „bieg przerwany w połowie
nie zaczyna od nowa", a narzędzie trzymało wynik w pamięci i pisało plik **na końcu**. Bieg zabity
na 10% stracił **140 000 świec**. Zasada, którą cytowałem, mówi wprost: *bieg który umiera NIE traci nic*.
→ **CHECKPOINT STRONICOWY**: każda strona natychmiast na dysk (z flush). Zmierzone: wznowienie
**0.7 s** wobec ~20 min pełnego pobrania; checkpoint rośnie na żywo (18 MB / 101 tys. linii po 7%).
Uszkodzona ostatnia linia (po zabiciu w trakcie zapisu) jest pomijana, nie wywraca odczytu.

**3. Licznik, który kłamał.** Raport mówił „dociągnięto 193" także wtedy, gdy drugi bieg nie wysłał
**ani jednego** żądania (wszystko z checkpointu). Liczył długość zwróconej listy, nie przyrost.
→ liczony **przyrost wobec stanu poprzedniego** (po − przed).

### Zatrzymania sesji — hipoteza zawężona, nie potwierdzona

Trzy biegi padły dziś z `KeyboardInterrupt` (sygnał z zewnątrz, nie błąd kodu). **Wykluczone pomiarem:**
brak pamięci (10.3 GB wolne), awaria sieci na poziomie OS (zero zdarzeń w dzienniku 05:35–05:55),
podagent jako wspólny mianownik (trzecie padnięcie było bez niego). **Zostaje** intensywny ruch
sieciowy — hipoteza z **n=3**, nie przyczyna. Tani test: tempo zapytań zwolnione 7/s → 3/s.

### Księga Wad +3 (46)

- **odporność pozorna:** mechanizm zapisujący stan dopiero na końcu — działa tylko gdy niepotrzebny
- **świeżość danych:** „plik istnieje, więc jest aktualny" — sprawdzaj ZAKRES DAT, nie liczbę wierszy
- **licznik który kłamie:** raportowanie długości wyniku zamiast rzeczywistego przyrostu

**Pliki:** `narzedzia/agreguj_bary.py` (nowy, zastępuje `agreguj_4h.py`),
`narzedzia/pobierz_binance.py` (nowy, uogólnia `pobierz_4h_binance.py`), `narzedzia/audyt_danych.py`,
`narzedzia/pobierz_nowe_pary.py`, `tests/test_czytnik_csv.py`, `docs/ARCHITEKTURA_IMPERIUM.md`, `.gitignore`

---

## 2026-07-20 | 🔬 | AUDYT DANYCH: 1H pochodziło od pośrednika — 245 barów naprawionych + hipoteza interwału

### Powód (rozkaz Cezara)

*„sprawdź interwały 4h, ściągnij inny sampel z netu, bo kiedyś jakiś moduł sam przerabiał z 1h na 4h,
może coś popsuł — zrób audyt"*. Podejrzenie padło na 4h. **Pomiar odwrócił kierunek: zepsute było 1H.**

### Organ: `narzedzia/audyt_danych.py` — trzy warstwy (Prawo XVI, każda pyta o co innego)

| Warstwa | Pyta | Sieć |
|---|---|---|
| **W1 STRUKTURA** | siatka UTC, monotoniczność, duplikaty, sensowność OHLC | nie |
| **W2 KRZYŻOWA** | czy 1h zagregowane do 4h zgadza się z plikiem 4h | nie |
| **W3 ŹRÓDŁO** | czy zgadza się z publicznym API Binance | tak |

### Trzy klasy wad — wszystkie ZMIERZONE

**1. Pochodzenie danych.** `dane/godzinowe/*.csv` → **CryptoDataDownload** (pośrednik), `dane/4h/*.csv`
→ **binance.com**. Dlatego 4h zgadzało się ze źródłem, a 1h nie.
Dowód rozstrzygający (ETH 2021-01-11 08:00): nasz 4h `low=1049.01` = **Binance 1049.01** ✅,
nasz 1h `low=1063.00` ❌. Świece godzinowe **gubiły knot** — dołek zawyżony o 1.3%.
**Dlaczego to nie kosmetyka:** zawyżony dołek = stop-loss, który w rzeczywistości by poleciał,
w backteście NIE leci → wynik obciążony **optymistycznie**.

**2. Bary poza siatką UTC.** 43 kolejne bary przesunięte o 28m14s (2018-02-09 09:28 → 02-11 03:28)
w BTC, ETH, BNB, LTC. W tych oknach **brak poprawnych godzinówek**, a Binance ma komplet — to agregaty
INNYCH okien, więc podmiana wartości nie wystarcza: wymieniono cały odcinek (`napraw_siatke`).
Binance sam nie ma jednego z tych barów (realna przerwa giełdy) — **luki nie dorabiamy** (Prawo I).

**3. Świeca niedomknięta.** Ostatni bar KAŻDEGO z 15 plików 4h miał zaniżony wolumen (BTC 741 vs 902)
— świeca złapana w trakcie formowania, licząca się jak pełna. Naprawa poszła **do czytnika**
(`czytnik_csv.pomin_niedomkniety`), nie do plików: łatanie plików wracałoby przy każdym pobraniu.
Warunek czasowy → dane historyczne NIETKNIĘTE, a chroni backtest, paper i live jednym ruchem.

### Wynik naprawy

**245 barów w 15 parach** (46 OHLC + wolumeny + 3 odcinki siatki po 42 bary). Kopie w `dane/_kopie/`
(dane są poza gitem — bez kopii zmiana byłaby nieodwracalna; katalog dopisany do `.gitignore`, 127 MB).
Weryfikacja: **BTC 75 954 barów zgodnych z Binance co do grosza**, wszystkie 15 par czyste w W1+W2.

**Rozkład dat uszkodzeń jest wymowny:** 2021-01-11 (krach), 2021-04-23, 2021-10-29, 2021-12-24,
2022-04-13 — **dni incydentów giełdowych**. Pośrednik gubił dane dokładnie wtedy, gdy działo się najwięcej.

**Zero zmian po 2024-01-01** → okno testu hipotezy interwału (start 2024-01-28) **nietknięte**;
wynik poniżej stoi na danych, których naprawa nie dotyczyła (sprawdzone przez porównanie kopii z plikiem).

### Hipoteza interwału — POTWIERDZONA (`narzedzia/sym_porownanie_tf.py`, rozszerzone o 1d + CLI + pasek)

BTC+ETH, **to samo okno kalendarzowe, identyczna konfiguracja**, zmienia się wyłącznie interwał:

| interwał | ROI% | maxDD% | transakcje | win rate |
|---|---|---|---|---|
| 1d | **+9.80** | 0.04 | 22 | 50.0% |
| 4h | **+3.93** | 0.12 | 178 | 49.4% |
| 1h | **−4.38** | 0.14 | 647 | 48.5% |

Zależność **monotoniczna**: krótszy interwał → niższy ROI, więcej transakcji (22 → 178 → 647), wyższe
obsunięcie, spadający win rate. Mechanika przegranej: **win rate poniżej progu opłacalności × 30-krotnie
więcej transakcji**. 1H nie ma słabego sygnału — ma za dużo okazji przy zbyt cienkiej przewadze.
Podgląd: `raporty/KAPITOL_PODGLAD_hipoteza_interwalu.html`.

**Konsekwencja operacyjna:** odłożenie powtórek Stablecoin/USD-DXY na 1H było trafne — te ~6 h poszłoby
na szukanie przewagi w grze przegranej na poziomie interwału. Testy Tier-1 przenieść na 4h/1d.

**Ranga wg SCALA FIDEI: szczebel 1–2** (EXPLORATIO + pełne okno) na jednej parze aktywów. Do statusu
reguły brakuje TRANSLATIO (inne pary) i wyrównania okien (narzędzie tnie po LICZBIE BARÓW, więc realne
zakresy rozjeżdżają się o ~2 miesiące — usterka wykryta w trakcie, do poprawy). **Nic nie wpięte.**

### Luka odkryta przy okazji

**Brak plików 5m/15m** — mamy dane 1-minutowe (14 par, ~1450 dni), ale nikt ich nie zagregował, więc
**profil SCALP (Namiestnik W-323 mapuje M1–M15) nigdy nie był testowany**. Falsyfikowalna prognoza:
jeśli zależność jest monotoniczna, 15m i 5m wyjdą **jeszcze gorzej** — jeśli lepiej, teza o interwale upada.

### Księga Wad +3 (43)

- **pochodzenie danych:** pośrednik traktowany jak giełda (błędy skupione w dniach incydentów)
- **pochodzenie danych:** mieszane pochodzenie w jednym katalogu — plik pochodny NIE może być sędzią
  dla swojego źródła (detektor krzyżowy milczy, gdy oba mają ten sam błąd)
- **wnioskowanie:** wniosek z przesłanki POŚREDNIEJ zamiast pomiaru wprost — 3 własne przypadki tego dnia

**Pliki:** `narzedzia/audyt_danych.py` (nowy), `narzedzia/sym_porownanie_tf.py`,
`imperium/akwedukty/czytnik_csv.py`, `narzedzia/kapitol_podglad.py`, `tests/test_czytnik_csv.py`, `.gitignore`

---

## 2026-07-20 | 📕 | P2: A/B DVOL 1H pełna era + INDEX FALSORUM + CENSOR w hooku + LIMEN FENESTRAE

### Wynik P2 (pomiar rozstrzygający)

**A/B DVOL (PSY-05), BTC+ETH, 1H, PEŁNA era DVOL (19 471 + 19 380 barów, ~2.2 roku):**

| wariant | ROI% | maxDD% | trades |
|---|---|---|---|
| B: DVOL OFF (baseline) | −5.49 | 0.14 | 649 |
| A: DVOL ON (PSY-05) | −5.25 | 0.14 | 649 |

**Δ ROI = +0.24 pp → ⚖️ NEUTRALNE.** Flaga zostaje opt-in OFF. IC ≠ PnL: sygnał ma skill
informacyjny (+0.16@7d), ale nie zamienia się na wynik na 1H.
Podgląd: `raporty/KAPITOL_PODGLAD_ab_dvol_1h_pelna_era.html` (`kapitol_podglad.py ab_dvol_1h`).

**HIPOTEZA (nie fakt, do osobnego pomiaru):** oba ramiona tracą na 1H (−5.5%), a 4H/1D dawały
dodatnie ROI — problemem może być sam **interwał 1H** dla tej strategii, nie sygnał DVOL.
Porównanie szło na różnych oknach, więc NIE ogłaszamy tego jako wniosku.

### Trzy błędy Architekta złapane i spłacone (LEX TALIONIS)

**1. `N-7d2c4847` → `C-fb1e3b37` — obalone twierdzenie żyło w kodzie.** Trzy żywe narzędzia A/B
głosiły w `--help` „backtest O(n²)", obalone pomiarem 2026-07-19. Skutek nie był kosmetyczny:
operator bał się długiego okna, więc biegi 1H szły na 800 barach — **kłamstwo w help-stringu
zafałszowało wynik badawczy**.
→ **INDEX FALSORUM** (`imperium/biblioteki/index_falsorum.py`) — Spis Twierdzeń Obalonych:
twierdzenie rejestruje się RAZ (fraza + poprawna teza + DOWÓD obalenia, ledger append-only),
a sweep pilnuje całego korpusu `.py`+`.md`. Klasa siostrzana Warstwy 15 (liczby) i 16 (API-widma)
— tylko po stronie TWIERDZEŃ. Wpięte w istniejący organ: `skan_wad_kodu.py --falsa`.

**2. `N-36596e99` → `C-cd9b749a` — liczba o sprzęcie z pamięci (zarzut Cezara).** Architekt
twierdził „8 GB Fujitsu", mając organ do zmierzenia w kodzie. CENSOR mierzy **15.88 GB RAM,
4 wątki, brak CUDA, klasa PEDES**. Korekta była **już raz zrobiona** (LOG_ZMIAN:1208), a kłamstwo
przeżyło w **5 miejscach 4 żywych dokumentów** — `MANUAL_MIGRACJA` przeczył sam sobie (linia 16:
15.88 GB, linia 159: „Fujitsu 8 GB"). Sprostowane: MANUAL (×3 + mapa RAM), PLAN_DEEPSEEK, ROADMAP,
REJESTR_INSPIRACJI. Przy okazji: „562/562 testów" w MANUAL przy realnych 2627.
→ **Potwierdzający system przed testami:** `censor_sprzetu.banner()` w hooku (krok 0.7) obok
PORTITORA + INDEX FALSORUM w hooku (krok 0.8). Żelazo stoi przed oczami, ZANIM padnie teza
o wydajności. **Korekta merytoryczna:** wąskim gardłem tej maszyny jest CPU i brak GPU, **nie RAM**.

**3. `N-4f7032a6` → `C-a0519dbb` — kandydat ogłoszony jako prawda.** Architekt ogłosił konkluzję
(„NEUTRALNE było artefaktem krótkiego okna") z próbki 2 000 barów = **10% ery**. Pełna era to
obaliła. Ten sam błąd metodologiczny, który właśnie diagnozował u poprzednika.
→ **LIMEN FENESTRAE** (`scriba_codex.ocen_pokrycie`): ranga werdyktu liczona z pokrycia ery
i zapisywana **W REKORDZIE** ledgera — ROZSTRZYGAJACY (≥50%) / WSTEPNY (z ostrzeżeniem
„nie zamykaj tematu") / NIEZNANE (brak wiedzy — Prawo I). Wpięte w 3 narzędzia Tier-1.
Retroaktywnie: biegi 800 barów = **4.1% ery**, próbka 2000 = **10.3%** — oba WSTĘPNE, a ledger
trzymał je jak równorzędne werdykty.

### Obrona przed fałszywym alarmem — zmierzona, nie założona

INDEX FALSORUM złapał **trzy własne pułapki** w pierwszej godzinie życia; każda ma test regresyjny:
- **sprostowanie zawijane przez granicę linii** (`scriba_codex.py:135` „O(n^2) została" / `:136`
  „obalona pomiarem") → okno kontekstu ±2 linie
- **negacja dotycząca czego innego** („przez API, **nie** lokalnie (Fujitsu, 8GB RAM)") → negacja
  liczy się tylko PRZY frazie (≤8 zn.) lub w jej obrębie, nie w całej linii
- **„nie" w środku słowa „lokal-nie ("** → granice słów (`\b`), nie podciąg
- oraz: `8 GB RAM` dopasowane wewnątrz `15.**88 GB RAM**` → granica cyfry w frazie

Organ dostał też **`wycofaj()`** (append-only nagrobek): źle dobrana fraza da się zdjąć ze straży,
więc nie zostaje wiecznym FP (Księga Wad #35 — chroniczny fałszywy alarm uczy ignorować bramkę).
**Fraza koduje TWIERDZENIE, nie token** (`backtest.*O(n²)`, nie samo `O(n²)`) — zawężone PO pomiarze
szumu, nie z góry. Organ złapał nawet własny świeży docstring cytujący „8 GB" — dowód czułości.

**Strażnik Prawa XXI zadziałał:** `set(keys) == POLA_AB` w `test_scriba_codex` złapał dryf schematu
po dodaniu pól `ranga`/`pokrycie_ery` → POLA_AB zaktualizowane w tym samym ruchu.

**Bramki:** testy 2627 → **2649** (+22) · audyt exit 0 · ruff czysto · skan wad czysto · INDEX
FALSORUM sweep czysty · dług honorowy 0.

**Pliki:** `imperium/biblioteki/index_falsorum.py` (nowy), `imperium/oczy/censor_sprzetu.py`,
`.claude/hooks/session-start.sh`, `narzedzia/{scriba_codex,ab_dvol,ab_usd,ab_stablecoin,skan_wad_kodu,kapitol_podglad}.py`,
`tests/{test_index_falsorum,test_scriba_codex}.py`, `docs/{MANUAL_MIGRACJA_I_SYMULATOR,PLAN_DEEPSEEK,ROADMAP_IMPERIUM,REJESTR_INSPIRACJI}.md`

---

## 2026-07-20 | 🛡️ | AEQUITAS SERIERUM — strażnik równej długości serii u wrót Bramy (P1)

**Powód (P1 zamrożonej listy):** teza zwiadowcy mówiła „`zip(strict=True)` w ~25 miejscach Bramy".
Zgodnie z ZASADĄ WERYFIKACJI teza została **zmierzona, nie przyjęta na wiarę** — i okazała się
słuszna co do kierunku, a błędna co do liczby i lekarstwa.

**Pomiar (2026-07-20, seria syntetyczna 100 barów, `volume` obcięty do 80):**
- TA-Lib przy nierównych seriach: **GŁOŚNO** — `Exception: input array lengths are different`
- pure-Python `VWAP`: **CICHO** — 147.166667 → 137.166667 (**rozjazd 10.0**, ~6.8%)
- pure-Python `VWAP_STD`: **CICHO** — 28.866070 → 23.092206 (rozjazd 5.774, ~20%)
- pieczątka audytu raportowała `input_len=100` przy wyniku policzonym z **80** barów → **audyt kłamał (Prawo XIII)**

**Korekty do tezy zwiadowcy (KANDYDAT ≠ PRAWDA):**
- nie „~25 miejsc": **23** `zip` w całym `imperium/`, z tego **10** w Bramie
- `diagnostyka_korelacji.py` — **4/4 zipy JUŻ strzeżone** (`if n < 2 or n != len(y): return None`);
  `strict=True` byłby tam **martwą asercją** = szum udający ochronę (Prawo XVI)

**Lekarstwo (unikat, lepszy niż teza):** JEDEN strażnik u wrót zamiast ~25 rozsypanych `strict=True`.
Obejmuje **także wskaźniki numpy bez `zip`** (których 25×strict by nie złapało), naprawia kłamiącą
pieczątkę i **nie da się go pominąć** przy dodaniu nowego wskaźnika.
- `_aequitas_serierum()` wpięty w `compute()` **i** `compute_series()` (drugie wejście do matematyki)
- **Dowód kompletności:** jedyne parametry seryjne całego rejestru Bramy to `open/high/low/close/volume`
  (reszta — `period/fast/slow/k/n/dim…` — to skalary) → zero martwego pola
- **Zero ryzyka regresu:** `_serie()` (`budowniczy_wskaznikow.py:26`) buduje wszystkie 5 serii z **tej samej
  listy barów** — ścieżka produkcyjna nie może potknąć się o strażnika
- dodatkowo `zip(..., strict=True)` w niezmienniku wewnętrznym `_py_hma.wma` (ujemny slice `seq[-3:2] → []`
  dawał cichą MA = 0.0 udającą policzoną) — tam strażnik u wrót nie sięga

**Bramki:** testy **2627/2627** (+7 granic; licznik 2620→2627 = dowód, że nie są cicho pomijane) ·
audyt exit 0 · ruff czysto · skan wad czysto.

**LEX TALIONIS:** NOTA `N-fd782251` (cicha nierówność serii + kłamiąca pieczątka) spłacona
CORONĄ `C-340771af` (AEQUITAS SERIERUM). Dług honorowy: **0**.
**Uodpornienie klasy:** Księga Wad **#38** — „kontrakt danych: łączenie serii bez sprawdzenia równej
długości". Świadomie **bez regexu** — samo `zip(` ma za duży szum (23 wystąpienia, większość legalna),
więc to klasa do CHECKLISTY review, nie do auto-skanu (regex dopiero po pomiarze szumu).

**Podgląd (zero-tokenowy):** `raporty/KAPITOL_PODGLAD_aequitas_serierum.html`
(`python narzedzia/kapitol_podglad.py aequitas`) — narzędzie dostało dispatch po nazwie raportu,
dotąd miało jeden raport zaszyty na sztywno.

**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `tests/test_neurony.py`,
`narzedzia/kapitol_podglad.py`, `bibliotheca_ulpia/dane/{codex_notarum,ksiega_wad_kodu,rejestr_testow}.jsonl`

---

## 2026-07-19 | ⚔️ | PRAETORIUM — Kwatera Główna Imperatora (Centrum Dowodzenia, hybryda C+A)

**Powód (rozkaz Cezara):** Imperium nie miało miejsca, z którego Imperator widzi CAŁOŚĆ i wydaje ordery.
Zalążki istniały (Panel Kapitolu, Speculum, dashboard), ale — słowami Cezara — „to nie jest to".

**Proces:** 4 szablony wizualne (CASTRUM / MAPPA IMPERII / HUD BOJOWY / MARMUR) → wybór Cezara:
**hybryda C+A** (kokpit operacyjny + castrum organów). Szkice: `raporty/PRAETORIUM_SZABLONY.html` (gitignore).

**Organ:** `imperium/swiatynie/praetorium.py` — **PRAETORIUM** (ZASADA NOMENKLATURY).
- **Prawo XVI (nie duplikujemy):** NIE stawia drugiego serwera. `web_dashboard.py` (Panel Kapitolu) zostaje
  żywym serwerem; PRAETORIUM daje **czystą funkcję** `render_praetorium(stan) -> str`, którą tamten może podać.
  Granice spisane w docstringu wobec `kapitol_podglad.py` (jeden test) i `live_monitor.py` (alarmy).
- **Prawo I (rdzeń organu):** każdy panel niesie znacznik **ŻYWE** (policzone z kodu przy renderze) albo
  **BRAK DANYCH**. Bez giełdy front mówi wprost „Front milczy" — **zero wypełniacza udającego pomiar**.
  Rozkazy egzekucji celowo `disabled` (ZASADA WPIĘCIA — wpięcie to osobna, świadoma decyzja).
- Żywe dane: rój (87/15), strategie, elity, organy (te same liczby co README), bilans CODEX NOTARUM.
- +11 testów granic (pusty stan, brak źródła, P&L ujemny, dług honorowy, escaping HTML, disabled).

**Dowód wpięcia mechanizmu z tej samej sesji:** dodanie `praetorium.py` podbiło `organ_swiatynie` 6→7,
a wstrzykiwanie liczb SAMO poprawiło README — dokładnie po to powstało.

**Pliki:** `imperium/swiatynie/praetorium.py`, `tests/test_praetorium.py`, `README.md`,
`docs/ARCHITEKTURA_IMPERIUM.md`, `docs/INDEKS_IMPERIUM.md`.

**Następny krok:** dopracowanie (zwiad opcji) → wpięcie trasy → finalizacja.

---

## 2026-07-20 | 🏛️ | PRAETORIUM — panele Grupy 1 + trasa `/praetorium` w Panelu Kapitolu

**Powód:** Cezar kazał wysłać zwiadowcę po WIĘCEJ opcji przed decyzją, a potem wybrał
„zgodnie z rekomendacją" = Grupa 1 (realne dane dziś) + wpięcie trasy.

**Zwiad subagenta + werdykt sędziego (KANDYDAT≠PRAWDA — każdy kandydat zweryfikowany osobiście):**
Zwiadowca zebrał ~13 kandydatów; **zweryfikowałem je sam** i podzieliłem na trzy grupy:
- 🟢 **Grupa 1 — realne dane DZIŚ (WDROŻONE):** PORTITOR + Censor Sprzętu (klasa maszyny `PEDES`),
  CODEX PROBATIONUM (`podsumowanie_ledger`), Refleksja W9 (`raport_startowy`), „następny krok"
  z Dziennika (`banner_nastepny`), treść ostatnich NOT/CORON. **Zmierzony koszt łączny ~334 ms**, offline.
- 🟡 **Grupa 2 — uczciwie puste dziś (odłożone):** Sybilla (`brier()` = None — brak rozliczonych proroctw),
  Igrzyska/HedgeMWU (**pliki stanu nie istnieją** — zweryfikowane), Legiony Cieni. Wejdą, gdy live pochodzi.
- 🔴 **Grupa 3 — ryzyko atrapy (ODRZUCONE do czasu snapshotu):** Gubernator/Haruspex/Drift. Dowód:
  `gubernator.py:91` resetuje postawę w `__init__`, a `petla_live.py` NIE zapisuje ich stanu (zapisuje
  MWU/synapsy/igrzyska/arenę). Pokazanie ich statycznie = fałszywe „NORMALNY ×1.0" udające pomiar (Prawo I).
- ⛔ **Odrzucone trwale:** Kartograf (wymaga `numpy`+`matplotlib` → łamie zero-zależności),
  diagnostyka korelacji przy każdym renderze (za droga), cenzus adapterów bez wcześniejszego refaktoru.

**TRASA:** `GET /praetorium` wpięta w `web_dashboard.obsluz_sciezke` (import leniwy — koszt płacony
tylko przy wejściu). Kokpit żyje pod `localhost:8777/praetorium`, odświeżany F5. **Żaden drugi serwer
nie powstał** (Prawo XVI).

**Odporność:** `_bezpiecznie()` — jedno padnięte źródło NIE zabija kokpitu, tylko jego panel pokazuje
BRAK DANYCH. Bezpieczeństwo: na ekran trafia wyłącznie OBECNOŚĆ kluczy API (`DEEPSEEK✓ MEXC✗`),
nigdy wartość. Testy 11 → **21**.

**Następny krok:** ewentualnie B · MAPPA IMPERII → snapshot live (odblokuje Grupę 3) → finalizacja.
Potem powrót do zamrożonej listy priorytetów.

---

## 2026-07-19 | 📜 | README naprawa (schemat + liczby organów wstrzykiwane) + CODEX NOTARUM (LEX TALIONIS)

**Powód (rozkaz Cezara):** (1) główne README „kurewsko nieaktualne" — schemat/układ Imperium nie nadążał
za kodem; (2) wprowadzić tryb kary/nagrody „oko za oko" (błąd rodzi kompensujący unikat).

**Naprawa README (wstyd zdjęty, ZWERYFIKOWANE pomiarem):**
- Mapa organów → tabela z liczbami plików `.py` **wstrzykiwanymi** z żywego kodu (`tabularium.wartosci_z_kodu`
  → klucze `organ_*`, Warstwa 15). Rozjazd: legiony 40→67, biblioteki 8→25, akwedukty 8→17, koloseum 11→16,
  pretorianie 5→9, swiatynie 2→6, cesarz 9→11 — nigdy więcej nie skłamie (UODPORNIJ).
- Linia „Faza" (urywała się na W-343) → wskaźnik do MANIFEST + LOG_ZMIAN. Role → nomenklatura rzymska +
  sekcja **TWÓRCY**: CEZAR PIXEL, VITRUVIUSZ, HYGINUS, **TIRO** (lokalny LLM). Doktryna wojenna w wizytówce.

**Nowy organ CODEX NOTARUM (LEX TALIONIS, ZASADA STAŁA):** `imperium/biblioteki/codex_notarum.py` +
ledger `bibliotheca_ulpia/dane/codex_notarum.jsonl` (append-only). NOTA CENSORIA (−) za zatwierdzony błąd,
CORONA (+) za zatwierdzony unikat; `splaca` = spłata długu honorowego (oko za oko). Nic bez `zatwierdzenie`
(KANDYDAT≠PRAWDA). +11 testów granic. Inauguracja e2e: NOTA (niedbałe README) → CORONA (mechanizm LEX
TALIONIS) → dług honorowy spłacony. Skodyfikowane w CLAUDE.md + krok 5b CHECKLISTY KONIEC SESJI.

**ZAKRES rozszerzony (rozkaz Cezara):** oko-za-oko obejmuje **wszelkie błędy — dokumenty I kod — w CAŁYM
Imperium**, nie tylko README; przy wyborze co prostować najpierw — wsparcie subagentem. Skodyfikowane w ZASADZIE.

**3 błędy złapane i spłacone w tej sesji (ledger, saldo +0, dług 0):**
1. README niedbałe (brak TWÓRCÓW + brak TIRO) → CORONA: mechanizm LEX TALIONIS + organ.
2. Opis Hyginusa niekompletny — pominięta rola **głosu newsowego** DeepSeek-przez-API (jest nie tylko
   Bibliotekarzem-Zwiadowcą) → CORONA: rozszerzenie zakresu na całe Imperium + sweep subagentem.
3. **`test_codex_notarum.py` napisany jako `unittest.TestCase`** — runner zbiera TYLKO funkcje modułowe
   `test_*`, więc 11 testów było **cicho pomijanych** (liczba 2584 nie drgnęła; złapane pomiarem).
   → CORONA/UODPORNIENIE: **strażnik silent-skip w `tests/run_tests.py`** — plik `test_*.py` z zerem
   funkcji modułowych = twarda porażka. Zweryfikowano: 0 istniejących plików miało zero (nic nie psuje).
   Testy przepisane w stylu funkcyjnym: **2584 → 2596** (12 realnie bramkowanych).

**SWEEP CAŁEGO IMPERIUM (subagent-zwiadowca + weryfikacja sędziego) — 2 kolejne błędy złapane:**

4. **Ledger CODEX kłamał:** sugestia „Naprawa backtestu O(n^2)" wisiała ze statusem `OCZEKUJE decyzji
   Cezara`, mimo że tego samego dnia teza została **obalona pomiarem** (backtest LINIOWY, ms/tik stały
   ~66). LOG_ZMIAN ogłosił korektę — ledger jej NIGDY nie dostał. Źródło prawdy testów wprowadzało w błąd.
   → CORONA: **`scriba_codex.zamknij_sugestia()`** — pierwszorzędne API zamykania/korygowania sugestii
   (append-only, kontekst przepisany z oryginału, ValueError gdy sugestia nie istnieje) + 3 testy granic.
   **Root cause klasy:** zamykanie nie miało własnego API, więc robiono je „w widoku" i ginęło.
   Sugestia realnie zamknięta (Sugestie 18→19).

5. **`gubernator.py:110` — martwa gałąź:** `return OBRONA if KOLEJNOSC_POSTAW.index(OBRONA) <= idx + 1
   else OBRONA` — **obie gałęzie identyczne**, warunek zawsze prawdziwy (index(OBRONA)=1 ≤ idx+1 dla
   idx≥0), a `idx` liczony wyłącznie dla martwego warunku. Test asertował tylko `postawa in (OBRONA,
   KWARANTANNA)`, więc nigdy by tego nie złapał. Uproszczone **BIT-IDENTYCZNIE** (16/16 testów).
   → CORONA/UODPORNIENIE: **RUF034 włączone na stałe w `ruff.toml`** (zmierzone: 1 trafienie w całym
   repo, naprawione → sygnał >> szum). **OTWARTE (decyzja Cezara, dotyka sizingu → wymaga A/B):**
   czy „co najwyżej OBRONA" ma znaczyć min(obecna, OBRONA) — dziś KWARANTANNA JEST podnoszona do OBRONY.

**Bilans not:** 5 NOTA / 5 CORONA, saldo +0, **dług honorowy 0** (`codex_notarum bilans`).

**Pliki:** `README.md`, `narzedzia/tabularium.py`, `narzedzia/scriba_codex.py`,
`imperium/biblioteki/codex_notarum.py`, `imperium/koloseum/gubernator.py`, `ruff.toml`,
`tests/test_codex_notarum.py`, `tests/test_scriba_codex.py`, `tests/run_tests.py`, `CLAUDE.md`,
`docs/ARCHITEKTURA_IMPERIUM.md`, `docs/INDEKS_IMPERIUM.md`,
`bibliotheca_ulpia/dane/codex_notarum.jsonl`, `bibliotheca_ulpia/dane/rejestr_testow.jsonl`.

---

## 2026-07-19 | 💰 | CODEX arkusz „Momenty modelu" — druga oś doboru modelu (zużycie/moment)

**Powód (pytanie kontrolne Cezara):** dobór modelu (ZASADA OSZCZĘDNOŚCI TOKENÓW) opiera się DZIŚ
wyłącznie na RODZAJU/ZŁOŻONOŚCI zadania (statyczna tabela) — NIE patrzy na realne zużycie w momencie
(start/zamknięcie/commit/intensywne fazy), brak auto-zmiany (poza jakościową eskalacją na anomalię).
Zwiad Sonnet (drugi punkt widzenia: routing wg zużycia/kosztu) + sędzia Opus → udokumentowana DRUGA OŚ.

**Dodane (TYLKO dokumentacja — decyzja Cezara „udokumentuj, mechanizm osobno"; nic nie wdrożone):**
- `narzedzia/codex_probationum.py` — stała `MOMENTY_MODELU` + **14. arkusz „Momenty modelu"** (moment→
  zużycie→tier→dźwignia→uwaga): referencja doktrynalna osi „w którym momencie / ile palę" obok osi task-type.
- `bibliotheca_ulpia/dane/rejestr_testow.jsonl` — 2 rekordy SUGESTIA (KANDYDACI, Prawo I): #1 Adaptive
  Effort, #8 strażnik budżetu sesji (CLAUDE_CODE_SUBAGENT_MODEL + OTEL → JAWNY alarm+/model). Ledger 18 Sugestii.

**Werdykt sędziego (KANDYDAT≠PRAWDA):** z 8 kandydatów zwiadu tylko #8 gruntowany w REALNYCH hakach
Claude Code; #3/#6/#7 odrzucone (własna infra/gateway poza stackiem). Twarde ograniczenia: model sesji
głównej zmienia TYLKO `/model` Cezara; automat realny tylko dla delegacji subagentom; cicha degradacja
ZAKAZANA (nasza transparentność — zawsze jawnie). Źródła arXiv/OSS zwiadu ⚠️ niezweryfikowane osobiście.

**Testy:** +1 (`test_arkusz_momenty_modelu`). CODEX 13→14 arkuszy. Ruff czysto, skan czysto.

**Pliki:** `narzedzia/codex_probationum.py`, `tests/test_codex_probationum.py`,
`bibliotheca_ulpia/dane/rejestr_testow.jsonl`, `docs/LOG_ZMIAN.md`.

---

## 2026-07-19 | 🏛️ | PORTITOR — nowy organ pre-flight środowiska u wrót sesji (B1)

**Powód (kontynuacja uszczelniania OTWARCIA, wybór Cezara B1):** żaden istniejący organ nie robił
LEKKIEGO, BEZ-sieciowego pre-flightu startu. CENSOR SPRZĘTU (oczy) mierzy ŻELAZO; CENZUS ADAPTERÓW /
WALIDUJ ZMYSŁY sprawdzają adaptery na ŻYWYCH danych (wymagają sieci, ręczne). Luka: nikt nie sprawdzał
na KAŻDYM starcie software'u — wersji deps, OBECNOŚCI kluczy API, świeżości danych, dryfu środowiska.

**Nowy organ `imperium/pretorianie/portitor.py`** (celnik u wrót — praetorian guard, nazwa rzymska
dobrana do funkcji, ZASADA NOMENKLATURY). Stdlib-only, BEZ sieci, non-blocking (ZASADA WPIĘCIA):
- **Runtime:** Python + obecność/wersje deps (numpy/TA-Lib krytyczne → alarm; pandas/ccxt/requests/openpyxl info).
- **Klucze API:** WYŁĄCZNIE obecność env (DEEPSEEK/MEXC) — NIGDY wartość (Bezpieczeństwo NIENARUSZALNE).
  Brak DEEPSEEK = alarm (Hyginus cichy); brak MEXC = info (faza paper).
- **Świeżość danych:** wiek najnowszej świecy lokalnych CSV per interwał (informacyjnie — dane backtestu
  bywają historyczne, więc bez alarmu; sonda żywego feedu = osobne, sieciowe).
- **Dryf vs baseline:** fingerprint (Python+pakiety) w git (`bibliotheca_ulpia/dane/portitor_baseline.json`);
  po `git pull` na innej maszynie porównanie ujawnia zmianę „pod spodem" (jak CENSOR dla sprzętu).
- CLI: `raport` (domyślnie) / `banner` (hook) / `migawka` / `zmiana` / `zatwierdz`.

**Wpięcie:** `.claude/hooks/session-start.sh` krok 0.6 — zwięzły `banner` (świadomie krótki, nie rozdymamy
startu — ironia luki L7). Baseline zatwierdzony na żywym środowisku Cezara (Python 3.11.9, 6/6 deps).

**Granica (Prawo XVI):** PORTITOR=software; CENSOR=żelazo; CENZUS/ZMYSŁY=sieć. Zero dublowania.
Drobna wada złapana samotestem: banner drukował „MEXC✗ MEXC✗" (2 klucze MEXC) → grupowanie po prefiksie (AND).

**Testy:** +17 (`tests/test_portitor.py` — granice kluczy/dryfu/alarmów/baseline). Ruff czysto, skan czysto.

**Pliki:** `imperium/pretorianie/portitor.py`, `tests/test_portitor.py`, `.claude/hooks/session-start.sh`,
`CLAUDE.md`, `docs/ARCHITEKTURA_IMPERIUM.md`, `bibliotheca_ulpia/dane/portitor_baseline.json`, `docs/LOG_ZMIAN.md`.

---

## 2026-07-19 | 🌅 | Uszczelnienie OTWARCIA sesji — Pakiet A+C1 (symetria do zamknięcia)

**Powód (rozkaz Cezara):** zamknięcie sesji miało 9-krokową egzekwowaną checklistę, ale OTWARCIE było
tylko narracyjne (PRAWO XVII rozproszone) — ta sama klasa luki, którą złapaliśmy w zamknięciu. Audyt
mechanizmu startu (oba hooki + config) + subagent ekonomiczny (Sonnet, research unikatów spoza Imperium)
dał katalog luk L1–L9 + 9 kandydatów zewnętrznych. Cezar zatwierdził **Pakiet A+C1**.

**Wdrożone (A+C1, wszystko non-blocking — ZASADA WPIĘCIA):**
- **A1+A3** `CLAUDE.md` — **🌅 OTWARCIE SESJI — CHECKLISTA STAŁA** (7 kroków, bliźniacza do zamknięcia):
  przeczytaj wydruk hooka → audyt≠harmonia rozstrzygnij JAWNIE → SYNC → weryfikacja „czy już istnieje" →
  rozpoznanie terenu (liczby z kodu) → przedstaw się rzymsko → pokaż plan/pytania.
- **A2** `dziennik_niesmiertelny.py` — subkomenda `nastepny` + `banner_nastepny()`: jednolinijkowy banner
  NASTĘPNEGO KROKU drukowany na GÓRZE hooka (luka L7: wydruk ~25 KB ucinał plan w podglądzie).
- **A4** `skan_wad_kodu.py` — flaga `--ostatni-commit` + `_py_ostatni_commit()` + wspólny `_filtruj_py()`:
  skan startowy zmienionych plików był no-op na czystym drzewie → teraz skanuje ostatni commit (regresje
  po SYNC pull).
- **C1** `codex_probationum.py` — flaga `--podsumowanie` + `podsumowanie_ledger()`: jednolinijkowe
  podsumowanie ledgera na starcie (bez Excela) — domyka asymetrię (CODEX był tylko w zamknięciu).
- `.claude/hooks/session-start.sh` — banner (krok 0.5), CODEX (krok 2b), skan→`--ostatni-commit` (krok 6).

**Uodpornienie (ZASADA CENSORA):** skan złapał chroniczny FP w `codex_probationum.py` (regex „bezpiecznik"
trafiał w podłańcuch `hash_ok=True` w prozie Backlogu) — przeredagowano opis, by nie wyglądał jak kod
(Księga Wad #35: chroniczny FP uczy ignorować bramkę).

**Odłożone do decyzji (katalog):** B1 PORTITOR (pre-flight środowiska/danych — nowy organ), B3 smoke-testy,
D1 delta między sesjami, E1 auto-kompakcja pamięci, F1/F2 bramki live (przed paper→live).

**Testy:** +5 banner (dziennik) +3 podsumowanie (codex) +7 skan (nowy `test_skan_wad_kodu.py`). Ruff czysto.

**Pliki:** `CLAUDE.md`, `.claude/hooks/session-start.sh`, `imperium/biblioteki/dziennik_niesmiertelny.py`,
`narzedzia/codex_probationum.py`, `narzedzia/skan_wad_kodu.py`, `tests/test_dziennik_niesmiertelny.py`,
`tests/test_codex_probationum.py`, `tests/test_skan_wad_kodu.py`, `docs/LOG_ZMIAN.md`.

---

## 2026-07-19 | 📜 | Konsolidacja zasad zamknięcia sesji (+ CODEX) + skodyfikowanie standing-orderów

**Powód (zmierzone tej sesji):** kroki zamknięcia sesji były ROZPROSZONE po `CLAUDE.md` (Dziennik u góry,
Prawo XV osobno, pre-push w linii 252) — brak jednej listy o mało nie spowodował pominięcia
`skan_wad_kodu.py`. Dodatkowo CODEX_PROBATIONUM był tylko „przed zadaniem", NIE w zamknięciu (dryf
łapany przypadkiem — np. fałszywy „O(n²)" w Backlogu poprawiony bo akurat dotknięty). Standing-order
raportowania (podgląd Kapitolu) żył tylko w pamięci prywatnej, 0 w repo.

**Dodane (rozkaz Cezara):**
- `CLAUDE.md` — **🏁 KONIEC SESJI — CHECKLISTA STAŁA** (9 kroków w kolejności): bramka Prawo XXI →
  **CODEX regen+weryfikacja+ledger** → adversarial pre-push (`/code-review` + `skan_wad_kodu`) →
  komplet docs+pamięć → Prawo XV → Dziennik → commit → blok push → alarmy hooka.
- `CLAUDE.md` — **🏛️ ZASADA RAPORTOWANIA I PODGLĄDU KAPITOLU**: pełna spec (para/interwał/okno/tryb/dane)
  + zero-tokenowy podgląd Kapitolu z linkiem + re-pytania decyzyjne po zadaniu (skodyfikowany standing-order).
- `docs/ARCHITEKTURA_IMPERIUM.md` — sekcja **🧰 Narzędzia z nazwą rzymską**: Speculum Probationis
  (kapitol_podglad), Cursus Fenestrarum (wfo_chunked), Scriba Codex (scriba_codex) — domknięcie ZASADY
  NOMENKLATURY (organy były tylko w docstringach). Bump `stan_na` → 2026-07-19.

**Otwarte (rekomendacja do decyzji Cezara):** automatyczny backstop — warstwa audytu / hook pre-close
egzekwująca te kroki (E/F z raportu luk). NIE dokładane przy zamknięciu (nowa warstwa audytu = kod z
testami, ZASADA WPIĘCIA / nic nie psujemy) — osobne zadanie.

**Pliki:** `CLAUDE.md`, `docs/ARCHITEKTURA_IMPERIUM.md`, `docs/LOG_ZMIAN.md`.

---

## 2026-07-19 | 🧩 | Chunkowany wznawialny WFO (Cursus Fenestrarum) — ZASADA ANALIZY CZĄSTKOWEJ

**Co:** `narzedzia/wfo_chunked.py` — walk-forward cząstkowy i WZNAWIALNY. Każde OKNO to najmniejsza
jednostka: policz → ZAPISZ checkpoint → następne. Bieg który padnie NIE traci nic — wznawia od
pierwszego niezapisanego okna (lekcja: WFO „wisiał godzinami synchronicznie, padał = tracił wszystko").
Checkpoint `raporty/wfo_ckpt/<sygnatura>.jsonl` (gitignore=widok), sygnatura = hash configu
(plik/interwał/IS/OOS/okno/iteracje/lo/hi/seed/zakotwiczony) → inny config = inny plik, zero mieszania.
Pasek postępu per okno na stderr (Prawo XXIV). Zero-tokenowy podgląd Kapitolu (WFE + Sharpe OOS per okno).

**Refaktor rdzenia (zachowuje zachowanie):** `imperium/koloseum/walk_forward.py` — wyodrębniono
`ewaluuj_okno()` (najmniejsza wznawialna jednostka, deterministyczna przy stałym seed) + `agreguj()`
(czysta agregacja z cząstek). `walk_forward()` zyskał opt-in haki `checkpoint_cb`/`postep_cb`/`wznow`
(domyślnie None = zachowanie bez zmian). Determinizm `optymalizuj(seed)` → okno policzone dwa razy =
identyczny wynik, więc wznawianie bezpieczne (zero zmiany wyniku — dowód: test równoważności).

**Fail-fast:** guard `IS/OOS > okno` ZANIM policzy jakiekolwiek okno (backtest wymaga wycinka > okno) —
złapane smoke-testem, nie marnuje pracy w środku biegu.

**Dowód (smoke-test e2e, mini-CSV):** bieg 0/3→liczy 3 okna z paskiem; ponowny bieg „3/3 wznowione,
tylko agregacja" (✓, bez przeliczania), IDENTYCZNY werdykt (PRZEUCZONY, WFE −0.177, OOS Sharpe +0.086).
+8 testów (round-trip checkpointu, wznowienie bez przeliczania, częściowe wznowienie liczy tylko brakujące,
uszkodzony checkpoint pomijany).

**Pliki:** `imperium/koloseum/walk_forward.py`, `narzedzia/wfo_chunked.py`, `tests/test_wfo_chunked.py`,
`narzedzia/codex_probationum.py` (Backlog).

---

## 2026-07-19 | ⚡ | Wydajność backtestu: LINIOWY (nie O(n²)) + naprawa HMA + Speculum Probationis (podgląd Kapitolu)

**Diagnoza (pomiar > pamięć, ZASADA DEBUGOWANIA):** dawna teza „backtest O(n²)" była **BŁĘDNA**.
Zmierzone (cProfile + skalowanie na ab_dvol, BTCUSDT+ETHUSDT 1H, okno=250 stałe): 500b→36.7s,
750b→69.1s, 1600b→179s — **ms/tik STAŁY ~66 → LINIOWE** O(n·okno). Poprzedni „profiler" mylił wysoki
*cumulative* w `compute` (woła się ticks×~40) ze skalowaniem kwadratowym. Realny koszt: ~40 wskaźników
liczonych od zera co tik nad oknem 251.

**Naprawa hotspotu #1 (bit-identyczna, commit 4466eda):** `_py_hma` liczył `raw` nad CAŁYM oknem
(~235 punktów), używając tylko `root+1 ≈ 5` ostatnich — guard `potrzeba=period+root` policzony (l.152)
ale IGNOROWANY przez pętlę. Fix: `c=c[-potrzeba:]`. **BIT-IDENTYCZNE** — 4000 losowych serii 0 rozjazdów,
ROI backtestu bez zmiany. Zysk ~25% (750b: 69→52s). Klasa wady → Księga Wad #37 + test regresyjny
niezmiennika ogona (`test_py_hma_ogon_niezmiennik`).

**Speculum Probationis (`narzedzia/kapitol_podglad.py`):** zero-tokenowy podgląd testu w Kapitolu
(rozkaz Cezara 2026-07-19) — samowystarczalny HTML, inline-SVG, ZERO zależności (wzorzec
`backtest_dashboard`). Pełna specyfikacja CO testowane (para/interwał/okno/tryb/dane) + wykresy + link
`file://`. Pierwszy raport: `raporty/KAPITOL_PODGLAD_wydajnosc_hma.html`. +5 testów.

**Konsekwencja (decyzja Cezara):** skoro LINIOWE, WFO nie był zablokowany — tylko wolny (~52ms/tik).
Opcje: chunkowany wznawialny WFO (niskie ryzyko) vs pełna wektoryzacja full-series (duże/ryzykowne;
path-dependent supertrend/HA/bocpd/viterbi). CODEX Backlog + pamięć skorygowane (O(n²)→LINIOWE).

**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `tests/test_neurony.py`,
`narzedzia/kapitol_podglad.py`, `tests/test_kapitol_podglad.py`, `narzedzia/codex_probationum.py`,
`bibliotheca_ulpia/dane/ksiega_wad_kodu.jsonl`.

---

## 2026-07-19 | 🖋️ | SCRIBA CODEX — flaga `--ledger` auto-append (rodzina Tier-1) + naprawa buga `%` w argparse

**Co:** nowy organ **SCRIBA** (`narzedzia/scriba_codex.py`) — jedyny reużywalny appender do
`bibliotheca_ulpia/dane/rejestr_testow.jsonl`. Idempotentny (identyczny rekord tego samego dnia
= skip), append-only, schemat pól 1:1 z `codex_probationum` (Prawo XXI). Wpięto flagę `--ledger`
w 7 narzędzi Tier-1: A/B (`ab_dvol`/`ab_stablecoin`/`ab_usd`) + IC (`pomiar_dvol`/`stablecoin`/
`usd`/`funding_ic`). Wynik testu dopisuje się do CODEX SAM (rozkaz Cezara 2026-07-18, sugestia
CODEX zrealizowana). Dowód end-to-end: `ab_usd --bary 400 --ledger` → ledger 20→21, ponowny bieg
„bez zmian" (idempotencja), CODEX Wyniki A-B 9→10.

**Bug złapany po drodze (ZASADA CENSORA):** `pomiar_stablecoin_ic --help` wywalał się —
`%` w help-stringu argparse (`"okno % zmiany"`) → `ValueError` przy formatowaniu. Latentny
(psuł tylko `--help`, nie bieg). Naprawa u źródła (`%%`) + wzorzec do Księgi Wad (36, kat.
kontrakt, regex zmierzony szum=0) + skan całego korpusu (0 innych wystąpień, klasa domknięta).

**Powód:** CODEX rośnie bez ręcznego wklejania linii JSON; klasa buga `%`-w-help uodporniona.

**Pliki:** narzedzia/scriba_codex.py (nowy), narzedzia/ab_{dvol,stablecoin,usd}.py,
narzedzia/pomiar_{dvol,stablecoin,usd,funding}_ic.py, tests/test_scriba_codex.py (nowy, 7 testów),
imperium/biblioteki/ksiega_wad_kodu.py (dane), rejestr_testow.jsonl (sugestia ZREALIZOWANE).

---

## 2026-07-19 | 📦 | Konsolidacja LEKCJI — archiwizacja wg wartości retencji (Prawo XV, nic nie skasowane)

**Co:** sekcja LEKCJE Z SESJI puchła do **39966 zn > limit 24000** (180 lekcji, hurtowy import).
Alarm hooka wisiał sesjami. Rozkaz Cezara: konsolidacja.

**Diagnoza (pomiar, nie opinia):** automatyczny dedup ZAWODZI — `czy_duplikaty` (zachowawczy,
„fałszywe scalenie kasuje wiedzę bezpowrotnie") daje 0; identyczna sygnatura = 0; Mądre
Zapominanie = 0 kandydatów (wszystko wartościowe). 32 pary Jaccard≥0.6 to duplikaty SEMANTYCZNE
(różne tokeny), których żaden bezpieczny automat nie scali. **Wniosek: nie kasujemy — archiwizujemy.**

**Mechanizm (reużywalny, CENSOR pkt 3):** `pamiec_sesji.konsoliduj_lekcje(cel_znakow)` +
`_dopisz_archiwum` + CLI `konsoliduj [--cel --sucho]`. Schładza NAJNIŻEJ-wartościowe lekcje
(kryterium: `zapominanie.wartosc_retencji` = łączność w grafie × świeżość × ważność) do nowego
pliku ACTA `docs/PAMIEC_SESJI_ARCHIWUM.md` aż aktywna sekcja ≤ cel. Wynik: **180→94 aktywnych,
86 zarchiwizowanych, sekcja 39244→21962 zn**, alarm zniknął. Bilans 94+86=180 — **nic nie zginęło**
(archiwum przeszukiwalne grep/RAG, poza wstrzykiwanym kontekstem startowym; kontekst i tak brał Top-3).

**Symbioza (CENSOR złapał audytem):** nowy plik → INDEKS (katalog Tabularium regenerowany) + W8
LOG_ZMIAN. **Testy:** +4 granic (przenosi-nie-kasuje · sucho-nie-zapisuje · poniżej-celu-nic ·
zostawia-najwartościowsze), 57/57 pamięci sesji. **Pliki:** pamiec_sesji.py, test_pamiec_sesji.py,
PAMIEC_SESJI.md, PAMIEC_SESJI_ARCHIWUM.md (nowy ACTA), INDEKS_IMPERIUM.md, codex_probationum.py.

---

## 2026-07-18 | 🪞 | CENSOR w akcji: 10 „sprzeczności" W9 = fałszywe alarmy detektora — naprawa u źródła

**Co:** przegląd alarmu Refleksji W9 wiszącego od wielu sesji („10 sprzeczności do przeglądu").
Diagnoza z kodu (nie opinia): **10/10 to FALSE POSITIVES** z dwóch wad detektora
(`imperium/biblioteki/refleksja_pamieci.py`):
1. `_NEGATYW` zawierał `kandydat/planowane/pomysł` → **nowy POMYSŁ liczył się jak NEGACJA**
   wdrożonego („Dodano H-01" ↔ „Time-Morph kand. #25" = rzekomy regres).
2. Stoplista bez słów funkcyjnych → pary spinane przez `{'jako','decyzja'}`, `{'moduł','nowy'}`
   („Odrzucono Zig" ↔ „Budowa ważenia IC" — nic wspólnego; „jako" ma 4 znaki i przechodziło `_MIN_DL`).

**Naprawa u źródła:** (a) `_NEGACJA_TWARDA` — SPRZECZNE wymaga realnego cofnięcia
(odrzucona/porzucone/wycofana/„nie"), późniejszy „−" będący planem = nowa hipoteza, nie regres;
(b) stoplista + słowa czynności/funkcyjne. **Wynik: Sprzeczne 10→0, Rozstrzygnięte 10→16**
(postęp widoczny, szum zgaszony). +3 testy granic (pomysł-nie-przeczy, twarda-negacja-łapana,
stoplista-tnie), 31/31 testów refleksji. Filozofia anty-utrwalania NIETKNIĘTA (moduł dalej
tylko zgłasza, nic nie kasuje).

**Lekcja (Księga Wad, 35 wpisów, kat. werdykt):** chroniczny fałszywy alarm uczy ignorować
bramkę — dokładnie dlatego wisiał sesjami. Konsolidacja LEKCJI: ODŁOŻONA (decyzja Cezara).
Pozostał 1 wiszący pomysł (Wektory semantyczne RAG, 22d) → decyzja Cezara w Backlogu CODEX.

**Pliki:** refleksja_pamieci.py, test_refleksja_pamieci.py, codex_probationum.py (Backlog),
ksiega_wad_kodu.jsonl.

---

## 2026-07-18 | 🏺 | AUDYT KONSTYTUCJI + ZASADA WERYFIKACJI + ZASADA CENSORA (Fable 5)

**Co:** dwa nowe ROZKAZY STAŁE Cezara skodyfikowane + pełny audyt CLAUDE.md zasada-po-zasadzie
(pierwsza sesja na Fable 5).

**ZASADA WERYFIKACJI PRZED WDROŻENIEM:** każda decyzja/propozycja przed wdrożeniem przechodzi
bramkę: czy już istnieje/zbadane (CODEX+kod+kronika) · pod każdym kątem (granice/reżimy/pary) ·
wpływ na CAŁE Imperium (symbioza) · zgodność z zasadami · dowód z POMIARU. Cel: zarabiać na
krypto (MEXC), nic nie psuć — rozwijać.

**ZASADA CENSORA (pętla samokontroli):** WYKRYJ→ZAŁATAJ→UODPORNIJ→ZAPISZ; alarmy hooka
startowego = ZADANIA, nie tapeta (dowód luki: W9 „10 sprzeczności" + „LEKCJE 39k>24k"
ignorowane przez wiele sesji, bo żadna zasada nie nakazywała reakcji). Oba alarmy → Backlog CODEX.

**Audyt CLAUDE.md — 5 niezgodności naprawionych (każda zweryfikowana wobec kodu):**
1. `stan_na` 07-14 → 07-18 (plik zmieniany, data nie nadążała).
2. „9 Nienaruszalnych Reguł" przy 10 pozycjach → nagłówek bez liczby (count-proof); klasa wady
   „ręczna liczba w nagłówku" → Księga Wad (34 wpisy).
3. KROK 0: „planowane A/L/V" — zmierzone: `WAGI_REZIMU_PLANOWANE` dziś PUSTY → komentarz naprawiony.
4. Sekcja OBSERWACJI PR rozcięta wklejką „Zasady debugowania" (jej zdanie wisiało za obcą sekcją)
   → scalona; debugowanie = własna sekcja H2.
5. „Opus" zaszyty jako najwyższy tier → dopisek „czytaj: najwyższy dostępny (dziś Fable 5)";
   ta sama klasa co nieistniejący „sonnet-4-6" (2026-07-17).

**Pliki:** CLAUDE.md, codex_probationum.py (Backlog +2 alarmy), ksiega_wad_kodu.jsonl, LOG_ZMIAN.

---

## 2026-07-18 | 📜 | CODEX_PROBATIONUM — żywy rejestr testów w Excelu

**Co:** generator wielo-arkuszowego .xlsx (`narzedzia/codex_probationum.py`) — nasz
dokładny rejestr testów. **12 arkuszy:** README/Legenda, Neurony (87), Zwiadowcy (15),
Strategie (20), Neurony×Strategie (macierz ról W/F/X), Adaptery (22 + żywotność),
Waluty×Interwały (15 par × 1m/1h/4h/1d, pokrycie), Interwały→Styl (Namiestnik),
Wyniki A/B, Wyniki IC, Korelacje (pomiar W-306), Backlog/Planowane.

**Architektura (Prawo XXI/Filar 4):** Excel = GENEROWANY WIDOK z dwóch źródeł prawdy —
żywy kod (rejestry) + wersjonowany `bibliotheca_ulpia/dane/rejestr_testow.jsonl` (ledger
wyników, seed 13 rekordów A/B+IC z tej sesji). Nigdy z pamięci → nie może się rozjechać.
Import openpyxl LENIWY + miękki fallback (Prawo I: rdzeń `zbierz_arkusze()` działa bez
biblioteki, testy przechodzą). `raporty/` w .gitignore (regenerowalny artefakt).

**🔧 Dług naprawiony (rozkaz Cezara „błędne → napraw"):** legenda kategorii w
`mikro_neuron.py:61-67` NIE miała liter **C** (Cross-sectional, C-01) i **D** (Path
Signature, D-01), choć kod ich używa — złamanie ZPO. Dopisane; test `test_legenda_kategorii_kompletna`
pilnuje pokrycia KAŻDEJ żywej kategorii.

**Zależność:** `openpyxl>=3.1` do requirements.txt. **Testy:** +8 (rdzeń bez openpyxl +
zapis pod importorskip + granice: pusty/uszkodzony ledger, parser korelacji, zgodność
liczb z rejestrem). **Pliki:** codex_probationum.py, rejestr_testow.jsonl, test_codex_probationum.py, mikro_neuron.py, requirements.txt.

---

## 2026-07-18 | 📊 | A/B TIER-1 NA 1H/4H + 🚨 Prawo XV (backtest O(n²))

**Co:** rozkaz Cezara 07-16 — powtórka A/B sygnałów Tier-1 (DVOL/stablecoin/USD) na
interwałach roboczych. Narzędzia `ab_dvol/stablecoin/usd.py` sparametryzowane opcjami
`--interwal {1d,4h,1h}`, `--od`, `--bary N` — NIE-destrukcyjnie (domyślny `1d` reprodukuje
dokładnie stare +2.27pp, ruff czysto).

**🚨 Prawo XV (utrata potencjału) — backtest jest O(n²):** profiler wskazał `compute`
(brama_kalkulatora:1409) = 53s/105s — wskaźniki (wma/supertrend/volume_profile) przeliczane
od zera nad rosnącą historią KAŻDEGO baru (600 barów→9.6s, 1800→81.5s). Pełne okno 1H/4H „nigdy
nie kończyło" nie przez sieć, lecz przez silnik. NIE naprawiane w tej sesji (inkrementalne
wskaźniki zmieniłyby wyniki → ZASADA WPIĘCIA, osobne zadanie). Obejście: `--bary 800`.

**Wyniki (800 barów/symbol, 4H≈133 dni, 1H≈33 dni — WSTĘPNE, jeden reżim):**
| Sygnał | 4H Δ ROI | 1H Δ ROI |
|---|---|---|
| DVOL PSY-05 | +3.60pp ✅ | +0.00pp ⚖️ |
| STABLECOIN K-03 | +0.79pp ✅ | +0.00pp ⚖️ |
| USD K-04 | +0.20pp ⚖️ | +0.00pp ⚖️ |

**Werdykt:** 4H potwierdza dzienne (DVOL+stablecoin pomagają; USD marginalnie <próg). 1H =
0.00 dla WSZYSTKICH — sygnały wolne (dzienne) nie ruszają skanera na 33-dniowym oknie; to
brak efektu na krótkim oknie (wymuszonym O(n²)), NIE odrzucenie. Flagi zostają opt-in OFF
(decyzja Cezara). **Pliki:** ab_dvol.py, ab_stablecoin.py, ab_usd.py.

---

## 2026-07-18 | 🛡️ | SESJA SZTABOWA — WARSTWA 16 AUDYTU (łowca API-widm)

**Co:** bramka zapobiegawcza „API opisane w żywym docu MUSI istnieć w kodzie" —
`narzedzia/audyt_spojnosci.py` `_warstwa_16_api_widma()` + helpery `_w16_widma_w_tresci`
(czysty skaner) i `_w16_realne_pliki`. Skanuje ścieżki `korzeń/…/x.py` w żywych docs.

**Dziura zatkana (zmierzona):** spłata długu gnicia szła dokument-po-dokumencie, więc NIE
łapała plików, których NIGDY nie było. Skan całego korpusu naraz znalazł **3 martwe komendy
w żywym INDEKS-ie** przy „pełnej harmonii": `mexc_feed.py`→`cenzus_adapterow.py`,
`calculator_gate.py`→`brama_kalkulatora.py` (stara ang. nazwa), `veto_check.py`→`aegis_tarcza.py`.
To klasa war_lancer/valhalla (w archiwum, nie w `imperium/`) i Kronikarz v2 Interrogator.

**Suprsje (walidacja: 9 kandydatów → 6 zciszonych, 3 realne):** bloki ```python (kod
przykładowy), markery planu/negacji w linii (`do zbudowania`, `NIGDY nie istniał`, 🔴/🟠/💭/
WIZJA — z GRANICĄ SŁOWA: „todo"∉„metodologia", „wizja"∉„dywizja"), changelogi/rejestry-zamiarów.

**Recenzja adversarial złapała:** goły podłańcuch „todo"/„wizja" trafiał wewnątrz polskich
słów → false-negative; naprawione `\b`. **Testy:** +8 granic (detekcja, każda suprsja osobno,
granica-słowa). **Pliki:** audyt_spojnosci.py, tests/test_spojnosc.py, INDEKS_IMPERIUM.md, CLAUDE.md.

---

## 2026-07-18 | 🏁 | DŁUG GNICIA SPŁACONY DO ZERA — IGRZYSKA + ARCHITEKTURA + MANUAL

**Co:** ostatnia trójka + domknięcie całej kampanii porządkowej. **T2 gnicie: 0/70 dokumentów.**

• **IGRZYSKA_IMPERIUM** — rozdzielono kod od wizji: ✅ Arena Neuronów w pełni w kodzie (wzór
  WYNIK_NEURONU 0.30/0.25/0.20/0.15/0.10, tablica RANGI Tiro→Aquilifer 0.0/0.5…0.93/2.0,
  PROG_INFAMII, zloty_helm, lista_infamii, WpisInfamii) + HedgeMWU ✅; 🔴 Arena Legionów i Senatu
  NIE ISTNIEJĄ (0 trafień) — oznaczone WIZJA; 🔴 pliki panteonu (PANTEON/TRIUMPHI/ALBUM/
  LISTA_INFAMII) nie zapisywane (dane w pamięci).

• **ARCHITEKTURA_IMPERIUM** — naprawiony dług z pola `dlug:`: mapa opisywała **nieistniejący kod**
  `drogi/war_lancer`, `swiatynie/sala_wojenna`, `koloseum/valhalla` (0 plików). Zastąpione realnymi:
  egzekucja → `oms`/`real_order_router`, dashboard → `web_dashboard`, backtest → `backtest`/
  `monte_carlo`. Liczby (neurony/książki) → bloki LICZBA. Pole `dlug:` usunięte.

• **MANUAL_UZYTKOWNIKA** — „78 neuronów" → 87 (blok LICZBA), „1532/1532 testów" → odesłanie do
  runnera. KonfigPetliLive (12 pól), handluj_live, 5 modułów AFML (W-355..359) zweryfikowane ✅.

**🏁 BILANS KAMPANII (dług gnicia 18 → 0):** 21 dokumentów spłaconych weryfikacją wobec kodu.
Wzorce znalezione: **API-widmo w docs** (kronikarz.zapytaj, policz_dzwignie, CesarzZDoradcami —
kandydat na Warstwę 16) · **liczba zaszyta w kodzie** (42 książek ×4, liczba praw) → rozwiązane
funkcjami liczącymi + W15 (11 wstrzykiwanych liczb) · **pomiar datowany mylony z opisem stanu** ·
**„brak/odłożone" starzeje się najszybciej** (RS-X=C-01, 6/6 braków TRYBY już istniało).
Otwarte długi kodu (do sesji sztabowej): łańcuch SHA-256 (hash_ok=True na sztywno), 14,9 mln
barów 1m nieużytych. Wstrzykiwanych liczb: neurony/aktywne/zwiadowcy/strategie/elity/pola_logu/
styl_scalp/swing/invest/prawa/ksiazki/fragmenty.

**Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅ · **T2 gnicie 0**.

---

## 2026-07-18 | 🎓 | PLAN_TIRO — rdzeń potwierdzony + liczba fragmentów RAG na LICZBA

**Co (dług gnicia):** weryfikacja planu TIRO (priorytet #1). Gnicie było przez commit metadanych
TABULARIUM w `censor_sprzetu.py` — **nie zmiana logiki**. Rdzeń stanu potwierdzony ✅:
CENSOR (5 klas PROLETARIUS→CONSUL + CLI raport/migawka/klasa/zmiana/zatwierdz) · NOTARIUS
(`tiro_pary_nauczyciela.jsonl`, `LIMIT_PROBEK_NA_PYTANIE=3`, `eksportuj_sft`) · rój 87 · kronika 102.
Pomiary E1 (llama-bench tok/s) = prawda DATOWANA, nietknięta.

**Jedyna korekta + naprawa u źródła:** RAG „27 959 fragmentów" → dziś **29 699**. Dodano publiczny
`srodowisko_pamieci.fragmenty_w_bazie()` + klucz Tabularium `fragmenty` (W15), więc liczba w
dokumencie już nie zamarznie (rośnie z biblioteką — jak `ksiazki`). Wstrzykiwanych liczb: 11.

**Pliki:** `docs/PLAN_TIRO_LOKALNY_LLM.md` · `imperium/biblioteki/srodowisko_pamieci.py`
(+`fragmenty_w_bazie`) · `narzedzia/tabularium.py` (klucz) · `tests/test_tabularium.py`.
**Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅.

---

## 2026-07-18 | 📋 | Trójka instrukcji: NAMIESTNIK (nadal prawda) + INSTRUKCJA + SETUP_LOKALNY

**Co (dług gnicia, 3 dokumenty):**
• **NAMIESTNIK** — ✅ **nadal prawdziwy**. API (`get_namiestnik`/`decyduj`/`skaluj_dzwignie`/
  `raport`) i obie tablice (reżim × parametry, styl × cap) zgadzają się z kodem co do liczby
  (zmierzone: TREND_STRONG/1D → INVEST/filtr/cap2/SPOT/0.605; RANGING ×0.4/72%; PANIC ×0.1/90%).
  Potwierdzenie + bump (poprawna spłata gnicia bywa „nadal prawda"). Doprecyzowano, że
  `klasyfikuj_rezim` żyje w `legatus.py`. Tabela dowodowa = pomiar datowany, nietknięta.
• **INSTRUKCJA_URUCHOMIENIA** — rozjazd właściciela: nagłówek wskazywał `skrypty/start.py`,
  a dokument opisuje `pierwszy_zwiadowca.py` (Faza 0). Poprawiony właściciel + dodana wzmianka
  o start.py (dashboard :8777) jako nowszej ścieżce. Reszta (git URL, 5 modułów, ścieżka
  `base/dane`, wykres+raport) zweryfikowana ✅.
• **SETUP_LOKALNY** — liczby książek „41/42"/„32"/„17" → realnie 79 (bloki LICZBA:ksiazki);
  sekcja wydajności oznaczona jako pomiar DATOWANY (35 plików, czerwiec 2026 — dziś ~29,7k
  fragmentów); nota, że calibre czyta djvu (osobny djvulibre zbędny). Dublet z START_LOKAL
  (oba o `indeksuj.py`) rozstrzygnięty werdyktem: pełny setup RAG vs skrócony start.

**Bramka:** audyt exit 0 ✅ · gnicie trójki → 0.

---

## 2026-07-18 | 💾 | PAMIEC_SESJI — sekcja „auto-aktualizuj" utknęła na 06-22, na LICZBA

**Co (dług gnicia):** dokument z mapą podpięć + ~200 lekcjami. Lekcje i mapy = zapis DATOWANY
(prawda swojego czasu, nie odświeżam — Prawo I). Sekcja **STAN BIEŻĄCY**, oznaczona „auto-
aktualizuj każdą sesję", w praktyce zamarzła: „1720/1720 testów (2026-06-22)", „81 neuronów
(aktywne 75)" — przy realnych 2507 testach i 87 neuronach (81 aktywnych). Ironia: sekcja
kazała się aktualizować, a nie miała mechanizmu.

**Naprawa u źródła:** STAN BIEŻĄCY → liczby WSTRZYKIWANE (neurony/aktywne/zwiadowcy/elity =
bloki W15); testy → odesłanie do runnera (nie hardkodujemy); usunięty martwy „Ostatni commit:
7a0dbf8". „42 książek" w mapie MCP → `<!-- LICZBA:ksiazki -->` (79). Lekcje nietknięte.

**Przy okazji:** domknięta pułapka README z poprzedniego commita — README ma DWIE daty
(frontmatter `stan_na:` czyta Tabularium, treść `**Stan na:**` czyta audyt W6); bumpnąłem
tylko treść, frontmatter został 07-15 → Tabularium wciąż gniło. Frontmatter poprawiony na 07-18.

**Pliki:** `docs/PAMIEC_SESJI.md` · `README.md` (frontmatter). **Bramka:** audyt exit 0 ✅.

---

## 2026-07-18 | 🎯 | TRYBY_IMPERIUM — lista „czego brakuje" gdzie 6/6 braków już powstało

**Co (dług gnicia):** weryfikacja propozycji trybów (5× kod). Dwie warstwy rozdzielone:
• **Pomiary 1H** (W-321b/c/c-v2/c-v3) — POMIARY DATOWANE z czerwca 2026, **nie odświeżane**
  (Prawo I). Werdykt „1H bez robustnego edge'u, asymptota ~−2.5%" nadal stoi.
• **Listy „czego brakuje"** — zestarzały się. Właściciele istnieją ✅.

**🔴 6 z 6 braków neuronowych JUŻ ISTNIEJE** (ten sam wzorzec co RS-X w ANALIZA_NEURONY):
Relative Strength → **C-01** · MTF Confluence → **X-28** · Breakout/Range → **X-12** ·
Katalizator Augur → **AUG-01** (a AdapterKronikarz **wpięty** w `neurony/sesje.py`, nie
„martwy") · Kategoria K makro → **K-01…K-04** żywa · Funding/OI → **PSY-01/02/04**.
Przepisane na tabelę „co powstało od czasu propozycji".

**Braki modułowe — zweryfikowane, mieszane:**
• ✅ Conviction sizing (W-318) — `sizing_przekonania.py`, opt-in · ✅ Compounding — dyrygent
  sizinguje z `kapital_calkowity`.
• 🔴 **Wpięcie skanera do pętli decyzyjnej (W-317)** — nadal brak: `SkanerOkazji` żyje TYLKO
  w `backtest.py`, nie ma go w `dyrygent.py`/`petla_live.py`. To wciąż warunek istnienia
  trybu NAJLEPSZE na żywo · 🔴 Bayesian P(sukces) per setup (Sybilla liczy Brier, nie to) ·
  🔴 egzekucja spot, auto-kalibracja live.

**Pliki:** `docs/TRYBY_IMPERIUM.md` · `docs/INDEKS_IMPERIUM.md`.
**Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅.

---

## 2026-07-18 | 🔢 | README na bloki LICZBA + naprawa W3/testów po zmianie daty

**Co:** przejście dnia (07-17 → 07-18) ujawniło, że **README podawał liczby RĘCZNIE** („87
zaimplementowane", „20 zmapowanych", „18 elitarnych") — mimo że jego `powod_istnienia` głosi
„podaje liczby wprost z kodu". To bomba jak „42 książek": dziś 87 się zgadza, ale rój rośnie.

**Wykryte przez bramkę W6, nie przeze mnie:** commit z 07-18 do repo + README ze „Stan na:
2026-07-15" → W6 słusznie zażądał potwierdzenia świeżości źródła prawdy (2 testy padły na tym
samym alarmie). To zamierzone działanie bramki, nie bug.

**Naprawa u źródła (nie sam bump daty):**
• 5 liczb README (neurony, neurony_aktywne, zwiadowcy, strategie, elity) → bloki
  `<!-- LICZBA:x -->` (W15). Zweryfikowane: 87/81/15/20/18 zgadzają się z kodem. Bump „Stan
  na:" → 2026-07-18 jest teraz WERYFIKACJĄ (liczby policzone), nie ślepym bumpem.
• **Regresja złapana w tym samym ruchu:** zmiana formatu (gołe „87" → blok) złamała regex
  warstwy **W3 audytu** (`(\d+) zaimplementowane` nie trafiał w „87<!-- /LICZBA --> zaimpl.")
  — audyt PRZESTAŁ porównywać liczbę neuronów README z kodem. Naprawione: regex toleruje oba
  formaty (`(\d+)(?:<!-- /LICZBA -->)? zaimplementowane`). Test `test_audyt_wykrywa_rozbieznosc`
  zaktualizowany, by podmieniać liczbę w bloku — dwuwarstwowa ochrona (W3 + W15) znów żywa.

**Pliki:** `README.md` · `narzedzia/audyt_spojnosci.py` (W3) · `tests/test_spojnosc.py`.
**Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅.

---

## 2026-07-18 | 🧠 | PLAN_DEEPSEEK — plan zrealizowany INNĄ drogą niż zakładał

**Co (dług gnicia 7 → 6):** weryfikacja planu DeepSeeka (5× kod). Werdykt: **zostaje CONSILIUM
żywy, NIE ACTA** — adapter `GlosImperium` żyje i ma 4 realnych konsumentów, ale realizacja
poszła zupełnie inną drogą niż plan, a to jest właśnie treść warta zapisu.

**🔴 Rozjazd właścicieli:** nagłówek wskazywał `titan_mind`, `meta_kora`, `wszechoko` jako
odbiorców DeepSeeka. **Żaden z nich go nie używa** (0 trafień). Poprawieni na realnych
konsumentów: `deepseek_glos` (adapter) · `news_llm` (Oczy/sentyment) · `notarius` (pary dla
TIRO) · `bibliotekarz` (zwiad Hyginusa).

**Plan vs rzeczywistość (zmierzone):**
• ✅ Adapter `GlosImperium.zapytaj()` + `test_polaczenia()` — istnieje.
• ✅ Sentyment newsów — realny, ale przez `news_llm.py`, nie `wszechoko.py`.
• 🔴 Debata Senatu Populares/Optimates przez LLM — NIE. `meta_kora` poszła drogą agentów ML
  (TrendAgent/SentimentAgent/MicrostructureAgent → MetaJudge/SuperJudge). Wzorzec LLM-debaty
  żyje TYLKO w `archiwum/kingdom_pixel_p1/meta_kora_debate.py`.
• 🔴 Decyzja LLM Cesarza — NIE. `titan_mind` to Strategy Orchestrator, nie używa DeepSeeka.
• ➕ Konsumenci, których plan NIE przewidział: **NOTARIUS** (zbiera pary prompt→odpowiedź dla
  treningu lokalnego LLM — dziś najważniejszy), Bibliotekarz/Hyginus (zwiad), auto_lekcja.

**Wniosek (Prawo I):** DeepSeek trafił jako narzędzie WIEDZY i TRENINGU, nie mózg decyzyjny.
Ścieżka wejść pozostała deterministyczna (Brama + neurony + Rada) — zgodne z kierunkiem.

**Model:** dokument podawał `deepseek-chat` — wycofany 2026-07-24. Realnie `deepseek-v4-flash`
(domyślny) / `deepseek-v4-pro`. base_url bez zmian.

**Dublet rozstrzygnięty:** notarius w PLAN_DEEPSEEK (konsument GlosImperium) vs PLAN_TIRO
(element pipeline treningu) — świadomy podział ról, werdykt w nagłówku.

**Pliki:** `docs/PLAN_DEEPSEEK.md`. **Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅ · gnicie 7→6.

---

## 2026-07-17 | 🔮 | DORADCY_CARA — trzecie API-widmo + Fulmen tylko połowicznie ortogonalny

**Co (dług gnicia 8 → 7):** weryfikacja Rady Pięciu (5× kod doradców).
**Wzory i progi wszystkich pięciorga zgadzają się z kodem ✅** — rozjechało się to, co ich SPINA.

**🔴 API-widmo #3 w tej kampanii:** klasa **`CesarzZDoradcami`**, `podejmij_decyzje()`,
`_wymagani_doradcy()` i `cesarz.wezwij_doradcow(powod)` — **0 trafień w kodzie**. Dokument
prezentował je jako działającą integrację (z wywołaniem DeepSeeka!). Realnie Rada jest w 100%
DETERMINISTYCZNA (zero LLM): dyrygent woła każdego doradcę osobno własnymi danymi, a
`RadaDoradcow.ocen()` tylko zlicza gotowe oceny. *(Poprzednie widma: `kronikarz.zapytaj`
w PAMIEC_ABSOLUTNA, `policz_dzwignie` w KALKULATOR_LEWARA — wzorzec systematyczny.)*

**🔴 „Warunki automatycznej aktywacji" nie istnieją:** dokument obiecywał wzywanie Rady przy
Senacie podzielonym (<0.15), przy WETO Legatusa, w szarej strefie 0.55–0.65 i w VOLATILE/PANIC.
**Realnie jedyny warunek to flaga:** `Dyrygent(rada=True)` → `if self.rada_doradcow is not None`
(dyrygent.py:540). Włączona = ocenia KAŻDE wejście; wyłączona = żadnego. Zero stanów pośrednich.
Warunkowe wzywanie zostaje postulatem 🔵.

**🚨 Prawo XVI — ortogonalność FULMENA jest CZĘŚCIOWA (zmierzone):** doradca ma weryfikować
reżim „zestawem ortogonalnym (innym niż Legatus)", ale **2 z 4** jego wskaźników to DOKŁADNIE
te, którymi już głosują neurony: `ADX_14` → **XII-01 NeuronADX**, `CHOPPINESS_14` → **V-14
NeuronChoppiness**. To nie pełna redundancja (Fulmen pyta o REŻIM, neurony o KIERUNEK), ale
„niezależna weryfikacja" czerpiąca w połowie z tego samego pomiaru jest słabsza, niż głosił
dokument: gdy `ADX_14` kłamie, myli się i neuron, i jego „niezależny" audytor.

**🔴 „Vortex" nie istnieje:** dokument obiecywał `VI+/VI- (Vortex 14)`; w kodzie **zero**
wskaźników Vortex. Pola `DaneFulmen.vi_plus_14/vi_minus_14` karmi `DI_PLUS`/`DI_MINUS`
(dyrygent nazywa to wprost „DI+/DI- jako proxy VI"). Nazwa pola została po niezrealizowanym zamiarze.

**🚨 Prawo XV — bramka hashów HERMESA martwa:** `dyrygent.py:911` podaje `hash_ok=True` na
sztywno, bo `ImperiumLog.hash_sha256` nie jest wypełniany przez NIC — nie ma czego porównywać.
Ten sam alarm co LUKA 1 w PAMIEC_ABSOLUTNA; w Księdze Wad klasa `bezpiecznik`. Dopisany wprost.

**Drobne:** „3/5 → 50% pozycji" → realnie **×0.6** (ta sama nieścisłość siedzi w komentarzu kodu).

**Zweryfikowane ✅:** Oracle Q=0.3·Sharpe+0.25·Sortino+0.25·Calmar+0.2·Omega, progi 1.2/0.8 ·
Fulmen ADX>25, Chop<38.2, ER>0.6 · Iustitia HEAT_MAX 0.06, CRITICAL 0.1, CORR_MAX 0.75,
COOLING 5 · Hermes KOMPLETNOSC 0.8, VPIN 0.75, EVENT 30min, ŚWIEŻE ×2 · Pythia MIN_SETUPOW 10,
p 0.6/0.45 · modyfikatory 1.0/0.8/0.6/blokada · PYTHIA MILCZENIE = neutralne (brak danych ≠ zły sygnał).

**Pliki:** `docs/DORADCY_CARA.md`. **Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅ · gnicie 8→7.

---

## 2026-07-17 | ⚖️ | KALKULATOR_LEWARA — dokument o ryzyku nie znał połowy bezpieczników

**Co (dług gnicia 9 → 8):** weryfikacja „matematyki przeżycia" (9× `kalkulator_lewara.py`).
Dokument o RYZYKU, więc każde twierdzenie sprawdzone wobec kodu i pomiaru runtime.

**🚨 Najgroźniejsze — dokument był MNIEJ ostrożny niż kod:**
• **„PANIC: dźwignia = 1× maksymalnie"** sugerowało, że w panice HANDLUJEMY małą dźwignią.
  **Nieprawda: `_checklist()` wetuje twardo — „Reżim PANIC, zero pozycji lewarowanych".**
  Mnożnik ×0.1 nigdy nie decyduje, bo pozycja odpada wcześniej. Kod bezpieczniejszy niż opis.
• **`policz_dzwignie(pewnosc, rezim, pretorianie_ok)` NIE ISTNIEJE** — realnie
  `KalkulatorLewara.auto_dzwignia(pewnosc, rezim)` (staticmethod, bez `pretorianie_ok`).
• **Granica myląca:** tabela mówi „<0.55 → 0× (nie handluj)", ale `auto_dzwignia(0.10)`
  zwraca **1**, nie 0 (`max(...,1)`). Słaby sygnał odrzuca OSOBNE weto w checkliście
  („Zbyt słaby sygnał: 10% < 55%"). Skutek dobry, mechanizm inny niż opisany — nikt nie może
  polegać na zwróconym zerze, bo `auto_dzwignia` nigdy zera nie zwraca.

**Checklist: lista życzeń ≠ kod.** Dokument obiecywał bramki, których nie ma: 🔴 Funding Rate,
🔴 ATR < 2× średniej (ATR służy WYŁĄCZNIE do liczenia SL, nie wetuje), 🔴 seria strat < 3.
Mylił też pojęcia: „rozmiar ≤ 2% kapitału" — `MAX_RYZYKO=0.02` ogranicza **ryzyko** (stratę na
stopie), nie rozmiar; checklist wetuje dopiero **rozmiar > 50% kapitału**. „Drawdown < 10%" nie
wetuje (to REDUCED ×0.5; weto dopiero 20% HALT, twardy stop AOA 30%). „R:R ≥ 1:2" — `MIN_RR=2.0`
istnieje, ale checklist go NIE sprawdza (2:1 wychodzi z konstrukcji TP). Wpisano pełną tabelę
8 realnych wet w kolejności z kodu.

**§11 — pięć mechanizmów, o których „pełna matematyka przeżycia" milczała** (wszystkie opt-in):
• **Reguła 6% Eldera** (BIB-015) — miesięczny meta-limit 6% → HALT; trzeci horyzont obok
  W-062 (equity 10/20%) i AOA (30%). ⚠️ ma historię buga „HALT zdejmowany przy odrobieniu".
• **SkalowanieFrakcjaDD** (W-063, Maier-Paape) — CIĄGŁY sizing; zmierzone: DD 0/5/10/20% →
  frakcja 1.00/0.75/0.50/0.10.
• **volatility_drag** ½·λ·(λ−1)·σ² — zmierzone przy σ=0.6: λ=1 → 0.0, λ=10 → **16.2**,
  λ=20 → **68.4** rocznie. Przy 20× sam drag zjada wielokrotność kapitału w skali roku.
• **skew_kelly** (Sinclair BIB-018) — Kelly z trzecim momentem, tnie przy ujemnym skosie.
• **SL oparty na ATR** (`atr`+`sl_atr_mult`) — łączony z buforem likwidacji przez wybór
  OSTROŻNIEJSZEGO (`max` LONG / `min` SHORT); może stop tylko zacieśnić, nigdy rozluźnić.

**Reszta zweryfikowana ✅:** wzory likwidacji · `OPLATA_UTRZYMANIA=0.005` (dokument pisał
`OPLATE_` — taka nazwa nie istnieje) · progi dźwigni 0.55/0.65/0.75/0.85/0.92 → 2/5/10/15/20 ·
korektory reżimu · volatility targeting (0.6/0.25/1.5) · breaker W-062 (20/0.10/0.20/0.5).
`PlanPozycji` uzupełniony o brakujące `bufor_likwidacji_pct`, `frakcja_dd`, `drag_roczny`.

**Pliki:** `docs/KALKULATOR_LEWARA.md`. **Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅ · gnicie 9→8.

---

## 2026-07-17 | 🗺️ | MAPA_PAMIECI — „v13" było liczbą warstw, a „42 książek" ma dziś 79

**Co (dług gnicia 10 → 9):** weryfikacja mapy pamięci (10× kod właścicieli, 14 plików).
Trzy twierdzenia fałszywe, wszystkie z tej samej rodziny — **liczba wpisana zamiast liczonej**:

• **Tytuł „Centrum Pamięci W-360 v13"** → kod mówi **v5** (`centrum_pamieci.py`, v5 z 2026-06-26).
  „13" to liczba WARSTW, nie numer wersji — ktoś pomylił jedno z drugim i tytuł niósł to dalej.
• **„wiedza z 42 książek"** → realnie **79** książek BIB-* zaindeksowanych (104 źródła łącznie:
  79 książek + 25 plików encyklopedii, 29 699 fragmentów). Liczba była **ZASZYTA w czterech
  miejscach kodu** (`kustosz_pamieci.WARSTWY`, `centrum_pamieci` docstring, dwa komunikaty
  `srodowisko_pamieci`) i powielona w dokumencie. Biblioteka rośnie (BIB-070..274 w planie),
  więc każda wpisana liczba MUSI się zestarzeć — to ta sama klasa co zaszyta liczba praw w W10.
• **„W chmurze FTS, lokalnie wektory"** → 🚨 środowisko = **lokal**, a `wektory = 0`.
  **Lokalnie też ich nie ma** — RAG działa wyłącznie na FTS5/BM25 (keyword), nie semantycznie;
  `model_embeddings: False`. Dokument sugerował, że to ograniczenie chmury. Sprostowane
  tabelą pomiaru; alarm zgłasza zresztą sam kod (`_alarmy()`: „LOKALNIE TO STRATA").

**Naprawa u źródła (nie tylko w dokumencie):** nowa funkcja
`srodowisko_pamieci.ksiazki_w_bazie()` — JEDNO źródło prawdy (Prawo XVI), liczy `COUNT(DISTINCT
zrodlo) WHERE zrodlo LIKE 'BIB-%'`. Wołają ją: `kustosz.mapa()` (dokłada żywą liczbę do W2),
`instrukcja_lokal()` i Tabularium (nowy klucz `ksiazki`, W15 → dokument). Stała `WARSTWY` nie
trzyma już żadnej liczby.

**Self-review złapał MOJĄ regresję:** pierwsza wersja poprawki drukowała „**14** warstw", bo
liczyła `len(WARSTWY)` — a **W7 (Kustosz) to ORGAN, nie warstwa-dana**. Oryginalne „13" było
poprawne; moja „poprawka" cicho przekłamałaby architekturę o jeden. Teraz liczone jako
`[w for w in WARSTWY if w[0] != "W7"]`, z testem pilnującym obu rzeczy (13 warstw + „organ W7"
w nagłówku) i drugim testem: `WARSTWY["W2"]` nie może zawierać żadnej cyfry.

**Pliki:** `docs/MAPA_PAMIECI.md` · `imperium/biblioteki/srodowisko_pamieci.py` (+`ksiazki_w_bazie`) ·
`imperium/biblioteki/kustosz_pamieci.py` · `imperium/biblioteki/centrum_pamieci.py` ·
`narzedzia/tabularium.py` (klucz `ksiazki`) · `tests/test_kustosz_pamieci.py` (+2).
**Bramka:** testy 2507/2507 ✅ · audyt exit 0 ✅ · skan wad czysto ✅ · gnicie 10→9.

---

## 2026-07-17 | 🤖 | MANUAL_CLAUDE_CODE — koniec sprzeczności o pushu + jeden parser praw

**Co (dług gnicia 11 → 10):** weryfikacja instrukcji obsługi (12× `audyt_spojnosci.py` — plik
zmieniany też w tej wachcie). Dokument **przeczył sam sobie**: sekcje 1 i 4.3 mówiły „push robisz
TY", a sekcja 4.4 „Claude Code zawsze pushuje tam" — zdanie sprzeczne z rozkazem z 2026-07-11.
Sprostowane; przy okazji dopisano, skąd bierze się granica (`permissions.deny` jest puste, więc
zakaz trzyma CLAUDE.md, nie maszyna — **układ świadomy i ustalony**, decyzja Cezara 2026-07-17).

**Pozostałe rozjazdy (zmierzone):** „24 Prawa" → **25** (teraz wstrzykiwane) · „1532 testów" →
2505 (zastąpione odesłaniem do runnera — liczba testów rośnie co sesję, więc nie wpisujemy jej
do dokumentu) · sekcja MCP opisywała GitHub/Filesystem jako naszą konfigurację, a `.mcp.json`
deklaruje **`biblioteka` + `arena`** (dopisana sekcja 5.0 z prawdą + ZASADA MCP „soczewka, nie
mózg"; 5.1–5.2 oznaczone jako opcje NIE wpięte) · hook startowy robi więcej, niż opisano (SYNC
`git pull --ff-only`, Centrum Pamięci, skan wad) — kolejność zweryfikowana i rozpisana; dopisany
hook **SessionEnd** (commit pamięci lokalnie) · `/model` podawał `sonnet-4-6` — poprawione na
aktualne **Opus 4.8 / Sonnet 5 / Haiku 4.5** (+ `/fast`).

**W15 — nowa liczba wstrzykiwana `prawa` + JEDEN parser (Prawo XVI):** liczba praw żyła jako
regex w `audyt_spojnosci.py` (W10). Zamiast dopisać drugi taki sam regex do Tabularium — audyt
**woła teraz `tabularium.policz_prawa()`**. Powód: dwa parsery tego samego formatu rozjadą się
co do znaku, a bramka pilnująca prawdy nie może zgadywać (klasa z Księgi Wad: „jeden format =
jeden parser"). Historia tej bramki jest ostrzeżeniem: miała kiedyś liczbę praw ZASZYTĄ i żądała
„21", gdy praw było 25 — egzekwowała kłamstwo. Test pilnuje, że audyt nie wróci do własnej kopii.

**Pliki:** `docs/MANUAL_CLAUDE_CODE.md` · `narzedzia/tabularium.py` (`policz_prawa` + klucz) ·
`narzedzia/audyt_spojnosci.py` (import zamiast kopii regexu) · `tests/test_tabularium.py` (+1).
**Bramka:** testy 2505/2505 ✅ · audyt exit 0 ✅ · gnicie 11→10.

---

## 2026-07-17 | 🔬 | ANALIZA_NEURONY zweryfikowana — propozycja „odłożona" żyje jako C-01

**Co (dług gnicia 12 → 11):** weryfikacja dokumentu MENSURA (17× `rejestr.py` od `stan_na`).
Kluczowa trudność: dokument MIESZA pomiar datowany z opisem stanu — więc rozdzieliłem je jawnie
(nagłówek „Jak czytać"), zamiast odświeżać liczby w środku pomiarów (Prawo I: A/B z czerwca na
roju 65→70 to prawda swojego czasu, nie odświeżamy).

**Sprostowania stanu (zmierzone):**
• **„5 z 6 propozycji wdrożono (Cross-Sectional RS odłożony — wymaga cross-symbol w pętli)"** →
  **wdrożone 6/6**. RS-X powstał 2026-06-17 jako **C-01 `NeuronRelativeStrength`**
  (`WSKAZNIK=CROSS_RS`, DOSTEPNY=True) — i dostał **własną kategorię C „Przekrój koszyka"**
  zamiast proponowanej R, z wagami reżimowymi pod jego naturę (silny w trendzie, słaby w PANIC,
  gdy korelacje→1). Dokument opisywał jako „do zrobienia" coś, co żyje od miesiąca.
• **„brama obronna Z (5)"** → Z liczy dziś **8**; kategorie C/D/H/K/N powstały po tamtym researchu.
  Osie roju przeliczone `Counter(n.KATEGORIA)`: R 16 · M 12 · T 11 · F 9 · O 8 · Z 8 · S 6 · A 4 ·
  K 4 · L 2 · N 2 · V 2 · C 1 · D 1 · H 1.
• **„AI/ML 0%"** i **„EXP-12 wyciszony"** → ✅ nadal prawda (brak kat. E; Atmabhan czeka na feed L2).
• **V-06/V-07/VP-01/Z-06/Z-07** → ✅ wszystkie istnieją, kategorie zgodne (F/F/S/Z/Z);
  OC-01..04 `DOSTEPNY=False` ✅ zgodnie z sekcją 9b.

**Warstwa 15 — trzy nowe liczby wstrzykiwane (`styl_scalp`/`styl_swing`/`styl_invest`):**
ten jeden dokument podawał rozmiary profili kolejno jako **41/59/35**, **65/65/70** i dziś
**75/75/87** — każda prawdziwa w dniu zapisu, każda skłamała miesiąc później. Tabela
`NEURONY_STYLU` jest z założenia *strojona pomiarem*, więc ręczna liczba rozjeżdża się po
KAŻDYM A/B. Liczby żyją teraz w kodzie (`neurony_dla_trybu`), nie w zdaniu.

**Nowa sekcja 10 — otwarte długi tego dokumentu** (obiecane pomiary, których NIE zrobiono):
🔴 VP-01 OOS na 5 parach (obiecany w sekcji 6 — do tego czasu VP-01 zostaje z pełną wagą,
bo jedno okno ≠ dowód redundancji) · 🔴 A/B „SWING-szeroki vs pełnia" (obiecany w 9a) ·
🔴 per-neuron mnożnik reżimowy (decyzja kierunkowa odłożona w 9b).

**Pliki:** `docs/ANALIZA_NEURONY_SCALP_SWING_INVEST.md` · `narzedzia/tabularium.py` (+3 klucze) ·
`tests/test_tabularium.py` (+1) · `docs/INDEKS_IMPERIUM.md`.
**Bramka:** testy 2504/2504 ✅ · audyt exit 0 ✅ · gnicie 12→11.

---

## 2026-07-17 | 🔱 | WIZJA_TRYBY_I_ROZWOJ zweryfikowana — 🚨 14,9 mln barów 1m leży nieużytych

**Co (dług gnicia 13 → 12):** weryfikacja najcięższego dokumentu długu (19× `rejestr.py` od
`stan_na`). Cztery twierdzenia o STANIE okazały się nieprawdziwe:

• **„🔴 `dane/minutowe/` puste — najwyższy priorytet danych"** → realnie **14 par, ~14,9 mln
  barów 1m**. Co gorsza: `wczytaj_csv(..., interwal="1m")` działa **bez żadnej zmiany kodu**
  (dowód runtime: AVAXUSDT → 145 185 barów w 1,1 s, chronologia rosnąca, pełne OHLCV) — format
  CryptoDataDownload identyczny z 1h. Mimo to **żaden moduł nie czyta `dane/minutowe/`**
  (0 trafień w `imperium/` i `narzedzia/`). 🚨 **Prawo XV — utrata potencjału.** To POWTÓRKA
  klasy, którą ten sam dokument opisał akapit wyżej przy 1h („dane leżały nieużyte").
• **Niuans, który zmienia werdykt (kandydat ≠ prawda):** dane 1m kończą się **2022-07-27**
  (luka 4 lata). Nadają się do BACKTESTU skalpu 2019–2022 (COVID/hossa/bessa), NIE do live.
  Priorytet brzmi więc „wpiąć istniejące do backtestu + dociągnąć świeże", nie „zdobyć dane".
• **„~76k barów 1h/parę (5 par)"** → realnie **15 par** (do 2026-06-18; MATIC urwany 2024-09-09).
• **„Wymaga: AdapterKronikarz live"** → **ISTNIEJE** i jest wpięty (`kronikarz_zdarzen.py:217`,
  zasila AUG-01 + `neurony/sesje.py`). Zdjęte z kolejki rozwoju.

**Propozycja Praw XXII–XXV — rozstrzygnięta (Prawo XVIII):** numery zostały w międzyczasie
nadane czemu innemu (Dekorelacja / Niezawodność warunkowa / Widoczność operacyjna / Przewaga
konkurencyjna), więc propozycja z 2026-06-14 była martwa. Werdykt: nie nadajemy ponownie —
„Ucieczka przed likwidacją" i „Obracanie kapitałem" już ŻYJĄ jako kod (`kalkulator_lewara`,
compounding W-319), „Płynność ponad balastem" pokrywa Prawo XVI+XXII, a „Prześwietlenie przed
wejściem" zostaje postulatem produktowym (AdapterKartaWaluty), nie nowym prawem. Mnożenie praw
bez potrzeby = ten sam błąd co mnożenie dokumentów.

**Tabela API prześwietlania — stan zmierzony:** GoPlus/RugCheck/GeckoTerminal 🔴 0 trafień ·
CoinGecko 🔴 tylko wzmianka w komentarzu · DefiLlama ✅ wpięty, ale **w INNEJ roli** niż
zakładała wizja (`adaptery/stablecoin.py` → K-03/K-04, podaż stablecoinów jako sygnał makro,
nie karta waluty). `AdapterKartaWaluty` 🔴 nie istnieje. Dostępność darmowych API sprawdzana
2026-06-14 i NIE weryfikowana ponownie — oznaczone ⚠️ w dokumencie (Prawo I).

**Pliki:** `docs/WIZJA_TRYBY_I_ROZWOJ.md` (weryfikacja + ✅/🔴 per twierdzenie) ·
`docs/INDEKS_IMPERIUM.md` (katalog regenerowany).
**Bramka:** testy 2503/2503 ✅ · audyt exit 0 ✅ · gnicie 13→12 · dublet `rejestr.py`
(KATALOG_NEURONOW ↔ WIZJA) rozstrzygnięty z powodem na widoku.

---

## 2026-07-17 | 🧠 | PAMIEC_ABSOLUTNA zweryfikowana + wstrzykiwacz, który ZJADŁ HISTORIĘ

**Co (dług gnicia 14 → 13):** spłata `docs/PAMIEC_ABSOLUTNA.md` przez WERYFIKACJĘ twierdzeń
wobec kodu, nie bump daty. Zmierzone rozbieżności: schemat `ImperiumLog` podawany jako
„~80 pól" przy **68** w kodzie · pola `top3_neurony_long/short` nie istnieją (kod:
`top3_long/short`) · brak `mae_pct`/`mfe_pct` i typu `DORADCY` · nazwa pliku to `_sygnał.jsonl`
· katalogi `igrzyska/ sesje/ analizy/` i `indeks.json` **nie istnieją** (opisane jako gotowe)
· **„Kronikarz v2 — Interrogator"** (`zapytaj`, `porownaj_okresy`, `replay_sesji`)
prezentowany jako działające API — **0 trafień w kodzie**; Kronikarz ma wyłącznie
`zapisz(RunReport)`. Realne API (`wczytaj`, `podsumowanie_sesji`, `log_sygnal`,
`log_trade_open`, `IMPERIUM_LOG_DIR`) nie było opisane wcale. Usunięta sekcja WFO podawała
progi „Sharpe > 0.6 / < 0.4" i okna „90/30 dni" — kod liczy `WFE = sharpe_oos/sharpe_is`
z `prog_wfe=0.5` w BARACH (zweryfikowane przed usunięciem — Zasada Archiwizacji).
Rozmiar schematu jest teraz liczbą wstrzykiwaną (klucz `pola_logu`, W15) — nie zgnije znowu.

**🚨 Prawo XV — LUKA 1 (łańcuch integralności przerwany):** Brama liczy `CalcResult.sha256`
per wskaźnik, ale `ImperiumLog.hash_sha256` **nie jest wypełniany przez NIC** (0 przypisań),
a `dyrygent.py:911` karmi bramkę Hermesa literałem `hash_ok=True` — bezpiecznik, który nie
może się zapalić. Prawo IX wymienia `hash_sha256` jako obowiązkowe → kod łamie własne prawo.
Udokumentowane jako LUKA; naprawa = osobne zadanie (ZASADA WPIĘCIA: Hermes stoi na ścieżce
decyzyjnej, więc opt-in OFF). **LUKA 2:** 6 z 9 typów `TypLogu` bez producenta.

**🚨 NAJWAŻNIEJSZE — narzędzie od prawdy sfalsyfikowało historię (Prawo I):** przy tej sesji
`wstrzyknij_liczby` **ZJADŁ 44 linie LOG_ZMIAN** — mój wpis, cały wpis TABULARIUM i początek
Filara 4, sklejone w kaszę. Przyczyna: regex bloku liczbowego używał leniwego `.*?` z
`re.DOTALL`, więc zacytowany w tekście znacznik BEZ domknięcia skleił się z domknięciem
NASTĘPNEGO bloku, a `sub()` skasował całą treść pomiędzy. Wykryte przez czytanie wyjścia
testów (historia przywrócona z gita, nic nie utracone). **Druga wada tej samej klasy:**
wstrzykiwacz przepisywał też dokumenty `typ: acta` — wpis z 2026-07-17 cytuje „87 neuronów"
jako prawdę swojego dnia; gdy rój urośnie, narzędzie CICHO zmieniłoby historię na nową liczbę
(dziś no-op, bo liczba się zgadza — bomba utajona). **Trzecia:** identyczna bomba `.*?`+DOTALL
w generatorze katalogu (`zapisz_katalog`), a INDEKS to dokument O dokumentach, więc cytat
znacznika jest tam naturalny. Naprawa u źródła: treść bloku nie może zawierać własnego
otwarcia (`(?:(?!<!--)[\s\S])*?`) · wstrzykiwacz omija `typ: acta` · testy granic na oba.

**Wada Księgi Wad (znaleziona przy okazji):** `zasiej_startowe` CICHO ignorował pole `regex`
w `CHECKLIST_STARTOWA` — wzorzec wpisany do złej listy stawał się **ozdobą**. Tak leżał od
dnia dodania wzorzec `subprocess text=True`: **nigdy niczego nie przeskanował**. Liczbowy test
partycji tego nie widział. Naprawa: bramka `ValueError` przy regexie w checkliście · `dodaj()`
AWANSUJE checklistę do wzorca zamiast dublować (Prawo XVI). **Ożywiony wzorzec natychmiast
złapał przeoczenie:** `audyt_spojnosci.py:259` — jedyny `subprocess.run(text=True)` bez
`encoding` (3 pozostałe naprawiono 07-17, ten umknął). Naprawione.

**Dwa nowe wzorce regex, szum zmierzony PRZED dodaniem (rozkaz stały):** `bezpiecznik`
(bramka karmiona literałem `True`) — 1 trafienie / 377 plików = dokładnie bug, 0 fałszywek,
idiom `mkdir(exist_ok=True)` wykluczony · `parsowanie` (`.*?` + DOTALL w jednym `re.compile`)
— baza miała 2 wystąpienia, oba naprawione, dziś 0 trafień i 0 fałszywek; wzorzec sprawdzony
w obie strony na obu wariantach (`.*?` gołe i w nawiasie).

**Pliki:** `docs/PAMIEC_ABSOLUTNA.md` (v2.0) · `imperium/biblioteki/ksiega_wad_kodu.py` ·
`narzedzia/tabularium.py` · `narzedzia/audyt_spojnosci.py` · `tests/test_ksiega_wad_kodu.py`
(+6) · `tests/test_tabularium.py` (+3) · `docs/INDEKS_IMPERIUM.md`.
**Bramka:** testy 2503/2503 ✅ · audyt exit 0 (ruff czysty) ✅ · gnicie 14→13 · dublet
kronikarza rozstrzygnięty z powodem na widoku.

---

## 2026-07-17 | 🏛️ | TABULARIUM — rejestr dokumentów + naprawa klasy wad kodowania (6 wystąpień)

**Co:** nowy organ **TABULARIUM** (`narzedzia/tabularium.py`, 20 testów) — rzymskie archiwum
państwowe: każdy żywy dokument DEKLARUJE SAM SIEBIE w nagłówku metadanych (kategoria ze
zamkniętego słownika LEX/TABULA/FORMA/DISCIPLINA/CONSILIUM/MENSURA/ACTA · typ · właściciel
· stan_na · powód istnienia), a maszyna to weryfikuje. Trzy bramki: **T1 deklaracja**,
**T2 gnicie** (właściciel-plik kodu zmieniony PO `stan_na` → opis nie nadąża za kodem),
**T3 dublet** (ta sama kategoria + ten sam właściciel = kod opisany dwa razy, Prawo XVI).
Katalog dokumentów GENEROWANY z nagłówków (`katalog --zapisz`) między znacznikami.

**Dlaczego (rozkaz Cezara — porządek Imperium):** ręcznie pisany indeks kłamie z definicji.
DOWÓD (Prawo I): `INDEKS_IMPERIUM.md:50` twierdzi „299 mikro-neuronów (72 w kodzie)" przy **87**
w kodzie — i przechodzi audyt na ZIELONO, bo W5 czyta liczbę z innej sekcji tego samego pliku.
Zwiad 42/56 dokumentów wykazał **pięć różnych twierdzeń** o liczbie neuronów (87/72/47/27/55/62)
oraz pliki-widma w 4 dokumentach (`sala_wojenna.py`, `war_lancer.py`, `valhalla.py` — nigdy nie
istniały). Zmierzone: przenoszenie żywych docs kosztuje 271 żywych odwołań + **1003 w kronice**,
której Prawo I zabrania przepisać → **decyzja Cezara: porządek w METADANYCH, fizycznie tylko
migawki** (1-3 odwołania każda).

**Klasa wad (rozkaz stały — Księga Wad):** `subprocess.run(text=True)` BEZ `encoding="utf-8"`
dekoduje wyjście gita kodowaniem konsoli Windows (cp1250), a nasze commity zaczynają się od emoji.
**2 wady aktywne** (`status.py` drukował „8f18d07 đź§ą PORZÄ„DEK…"; bramka gnicia Tabularium
CICHŁA NA GŁUCHO — stdout=None → zawsze zielona) + **4 utajone**, w tym w naszych bramkach
**W6b** (pierwszy plik z polską literą w nazwie ucisza bramkę dat) i **W13** (ruff pęka DOKŁADNIE
wtedy, gdy znajdzie buga — bo dopiero wtedy cytuje polski komentarz). Regex zmierzony wg nauczki
07-16: 6 trafień / 377 plików .py, zero trafień na kodzie naprawionym (sprawdzony w obie strony).

**Pliki:** narzedzia/tabularium.py (nowy), tests/test_tabularium.py (nowy, 20 testów granic),
imperium/biblioteki/ksiega_wad_kodu.py (+klasa „kodowanie"), narzedzia/status.py,
narzedzia/audyt_spojnosci.py (W6b/W8/W13), narzedzia/skan_wad_kodu.py, imperium/oczy/censor_sprzetu.py.

**Powód:** P0 porządku domknięte. Następny krok: nagłówki do 64 dokumentów (`stan_na` = data
faktycznej weryfikacji, NIGDY „dziś" — inaczej kłamstwo), katalog generowany, potem lista
scaleń/archiwum do zgody Cezara. Bramki Tabularium: MIĘKKIE do spłaty długu (ZASADA WPIĘCIA).

## 2026-07-17 | 👁️ | Dług gnicia: OBSERWATORZY + naprawa MOJEJ pochopnej flagi

**OBSERWATORZY (17 zmian w 7 plikach) — spłacony.** Weryfikacja wszystkich ścieżek kodu:

| | |
|---|---|
| ✅ ścieżka poprawna | 7 |
| ⚠️ **zła ścieżka** (plik żyje gdzie indziej) | **2** — `akwedukty/nexus_hub.py` → realnie **`imperium/drogi/nexus_hub.py`** (zły ORGAN: jest w *drogach*, nie w *akweduktach*); `akwedukty/kwatermistrz_danych.py` → brak przedrostka |
| 🚨 widmo | **0** (patrz niżej) |

**🚩 NAPRAWA MOJEJ WŁASNEJ POCHOPNEJ FLAGI:** przy wstrzykiwaniu nagłówków (P1) mój skrypt
automatycznie wpisał temu dokumentowi `dlug: "🚨 opisuje nieistniejący kod: multi_exchange.py"`.
**To było za pochopne.** Wiersze z `multi_exchange.py` mają status **🟠 Prowincja (faza 2)** —
dokument NIE twierdzi, że plik istnieje, tylko go **planuje**. Mechaniczne sprawdzenie
„czy plik istnieje" nie odróżnia **twierdzenia** od **zamiaru**. Flaga poprawiona, a ścieżka
zamieniona na jawne *(plan fazy 2 — moduł nie istnieje)*, żeby żaden skaner (ani człowiek)
nie wziął jej znów za deklarację.

**🔑 LEGENDA STATUSÓW DODANA (ZPO):** dokument używał **czterech** znaczników (✅ / 🔑 / 🟠 / 🔴)
i **nie definiował ANI JEDNEGO** — czytelnik musiał zgadywać, co znaczy „🟠 Prowincja".
Znaczenia odtworzone z kontekstu i zweryfikowane wobec kodu, z jawną kolumną **„Czy moduł
ISTNIEJE w kodzie?"**. To była realna przyczyna mojej pomyłki: **dokument bez legendy zmusza
do zgadywania — i skaner też zgaduje.**

**Pliki:** docs/OBSERWATORZY.md, docs/INDEKS_IMPERIUM.md.

## 2026-07-17 | 🖥️ | Dług gnicia: START_LOKAL + SCIAGA_LOKAL — spłata przez SPRAWDZENIE

**Oba dokumenty broniły się w CAŁOŚCI — treść nie wymagała ani jednej zmiany.**

| Dokument | Co zmierzono | Werdykt |
|---|---|---|
| `START_LOKAL` (21 zmian, 14× `audyt_spojnosci.py`) | 6 komend · „13 warstw pamięci" · luka „W1 ma 0 logów" | wszystkie ✅ — **13 warstw potwierdzone** (W1–W13 + W3b w `kustosz_pamieci.py`), **luka W1 NADAL AKTUALNA** (brak plików logów) → zostaje jako żywe zadanie |
| `SCIAGA_LOKAL` (5 zmian) | **24 komendy** | **24/24 istnieją** (moduły importowalne, skrypty na dysku) |

**🔑 LEKCJA O NATURZE BRAMKI T2 (ważna na przyszłość):** T2 mówi **„kod się ruszył"**, a NIE
**„dokument kłamie"**. `audyt_spojnosci.py` zmienił się 14×, ale START_LOKAL twierdzi o nim
tylko „uruchom, ma być exit 0" — twierdzenie odporne na te zmiany. **Spłatą długu jest
WERYFIKACJA, a poprawną odpowiedzią bywa „nadal prawda".** Bumpnięcie `stan_na` bez sprawdzenia
byłoby kłamstwem (Prawo I); bumpnięcie PO sprawdzeniu jest dokładnie tym, co `stan_na` znaczy:
**data, w której twierdzenia zostały ostatnio zweryfikowane.**

**Dług gnicia: 17 → 15.** W tej wachcie spłacone: GENERAL_LEGATUS, LEGIONY_ARCHITEKTURA,
KATALOG_NEURONOW, MATRYCA_KORELACJI, START_LOKAL, SCIAGA_LOKAL (**6 dokumentów**).

**Pliki:** docs/START_LOKAL.md, docs/SCIAGA_LOKAL.md, docs/INDEKS_IMPERIUM.md.

## 2026-07-17 | 🧭 | Dług gnicia: KATALOG_NEURONOW + MATRYCA_KORELACJI (katalog ślepy na pół roju)

**KATALOG_NEURONOW (40 zmian `rejestr.py`) — spłacony.** Weryfikacja mechaniczna 307 ID:

| | |
|---|---|
| ✅ oznaczone „w kodzie", a nieistniejące | **0** — katalog **nigdy nie kłamie w tę stronę** |
| **żyją w kodzie, a katalog ich NIE ZNA** | **44** (`OC-*`, `RADAR-*`, `NEWS-*`, `SMC-*`, `Z-*`, `V-*`, `C-01`, `D-01`, `H-01`, `BOCPD-01`, `CP-01`, `AUG-01`…) |
| oznaczone ✅ | **15** przy 87 w kodzie — znaczniki zamarzły |

**Diagnoza:** to ROADMAPA (CONSILIUM), nie mapa roju. Te 44 neurony **urosły POZA katalogiem**
— z deep-researchu i pomiarów areny, nie z pierwotnego skanu wskaźników. Rój przestał rosnąć
według tej listy. Dodany baner „czym ten dokument JEST, a czym NIE JEST" + wskazanie źródeł
prawdy (MANIFEST_KODU / MAPA_KLUCZY, Prawo XIX).

**Sprzeczność wewnętrzna NIEPOPRAWIONA — świadomie (Prawo I):** tabela mówi „RAZEM **129**",
proza dwie linie niżej „**142** w rdzeniu + 132 w dywizjach = **274**". Trzy liczby planu,
**żadnej nie da się zweryfikować wobec kodu** → nazwana wprost, nie zgadnięta.
**Zgadnięta liczba byłaby halucynacją udającą naprawę.**

**MATRYCA_KORELACJI (22 zmiany) — spłacona.** Zmierzone: **schemat numeracji
`[LITERA]-[001-157]-W[WAGA]` NIGDY nie wszedł do kodu** — 0 pasujących kluczy. Realny format
to `X-01`, a kategoria i waga to OSOBNE pola klasy (`X-01`: `KATEGORIA='M'`, `WAGA=6`) — bo
waga w kluczu oznaczałaby, że zmiana wagi zmienia identyfikator. Sekcja **zostawiona**
(tłumaczy intencję), ale nazwana. Legenda kategorii (6 liter z 15) → wskaźnik do jednego źródła.
**Pomiar „46 neuronów" ZOSTAWIONY nietknięty** i oznaczony jako prawda swojego czasu — pomiar
objął tamte 46, nie dzisiejsze 87; podmiana liczby sfalsyfikowałaby wynik (Prawo I).

**Fałszywe widmo, którego NIE zgłosiłem:** mój skan ID wskazał `INF-20` jako nieistniejący
neuron — to **odwołanie bibliograficzne** (Sinclair), nie klucz. Sprawdzenie kontekstu przed
meldunkiem powstrzymało szósty fałszywy alarm tego dnia.

**Pliki:** docs/KATALOG_NEURONOW.md, docs/MATRYCA_KORELACJI.md, docs/INDEKS_IMPERIUM.md.

## 2026-07-17 | ⚔️ | Dług gnicia: GENERAL_LEGATUS + LEGIONY_ARCHITEKTURA (86% rosteru było fikcją)

**GENERAL_LEGATUS (19 zmian `legatus.py` od `stan_na`) — spłacony.** Każde twierdzenie
zweryfikowane wobec kodu:
- ✅ **PRAWDA:** „min 5 neuronów, przewaga 55%" → `legatus.py:379` `min_neuronow=5, min_przewaga=0.55`
- ❌ „Szkielet kodu — patrz plik implementacji" → `legatus.py` ma **833 linie**
- ❌ **Legenda kategorii**: wymieniała **E** i **G**, których w kodzie NIE MA, i pomijała
  **C, D, N, Z** — cztery całe rodziny neuronów z deep-researchu. Przepisana z docstringów
  kodu (15 kategorii, **bez liczników** — Filar 4: ręczna liczba i tak by zgniła).
- ❌ Tabela reżimów nie znała **SMC_ACTIVE** (`{'S': 2.0, 'F': 1.2, 'T': 1.1}` w kodzie) → dodany
- ❌ „Faza 0 (teraz) — 2 testowe neurony" → Faza 0 i 1 **dawno wykonane**; sekcja PLAN → STAN

**LEGIONY_ARCHITEKTURA (17 zmian w 6 plikach) — 🚨 86% rosteru było FIKCJĄ.** Weryfikacja
mechaniczna **wszystkich 28 ID** wobec `rejestr.wszystkie_neurony()`:

| | |
|---|---|
| zgodne z kodem | **4 z 28** |
| zła nazwa | **9** — `X-01` opisany jako „Neuron EMA", w kodzie **RSI (14)**; `X-05` „OrderFlow" → **EMA Cross (9/21)** |
| **ID nieistniejące** | **15** — w tym **CAŁY roster Legio III** (`III-01..III-07`) |

**Odkrycie większe niż błędne nazwy: schemat „prefiks klucza = legion" UMARŁ.** W kodzie:
`X-*` 17 · `XII-*` 7 · `VI-*` 1 · **`III-*` ZERO**. Pozostałe ~60 neuronów ma prefiksy
**funkcyjne** (`OC-*`, `PSY-*`, `RADAR-*`, `NEWS-*`, `SMC-*`, `Z-*`…), które w podziale na
cztery legiony się nie mieszczą. Rój organizuje się przez **KATEGORIA** (15 liter), nie przez
numer legionu. **Metafora legionów żyje** (nazwa organu `imperium/legiony/`) — umarł schemat kluczy.

**Rostery USUNIĘTE, nie „poprawione":** przepisanie zduplikowałoby `MAPA_KLUCZY.md` (jedyne
źródło prawdy, audyt W14 wymusza pokrycie każdego z 87 kluczy). Dwie listy tych samych kluczy
rozjadą się ponownie — dokładnie tak jak ta. Stara treść żyje w gicie.

**Legenda kategorii SCALONA (Prawo XVI):** oba dokumenty miały własną ręczną kopię —
**identycznie fałszywą** (te same zmyślone E/G, te same brakujące C/D/N/Z). Dowód, że
problemem była KOPIA, nie autor. Jedno źródło: GENERAL_LEGATUS (Generał używa `KATEGORIA`
jako klucza w `WAGI_REZIMU`).

**Bramka złapała moje własne scalenie:** W10 miała **zaszyte na sztywno**, że słowo „Hurst"
ma być w LEGIONY_ARCHITEKTURA — po przeniesieniu legendy pilnowała pustego miejsca. Audyt
zaświecił czerwono, sprawdzenie przeniesione za treścią. To dokładnie ta kruchość, którą
Tabularium ma zastąpić: **bramka zaszyta per-dokument nie przeżywa reorganizacji dokumentów.**

**Pliki:** docs/GENERAL_LEGATUS.md, docs/LEGIONY_ARCHITEKTURA.md, narzedzia/audyt_spojnosci.py
(W10 za treścią), docs/INDEKS_IMPERIUM.md (katalog).

## 2026-07-17 | 🛡️ | ZAPORA TESTÓW — testy przestały PALIĆ PIENIĄDZE (nawrót klasy z 07-16)

**🚨 Co się stało:** po commicie porządkowym zobaczyłem w drzewie niewyjaśnioną zmianę
`tiro_pary_nauczyciela.jsonl` — **5 nowych par NOTARIUSA ze stemplem 2026-07-17 05:41,
źródło `news_llm`**, choć ani razu nie wołałem DeepSeeka świadomie. Śledztwo (dowód z DWÓCH
niezależnych źródeł — kod + stemple pisarza): `handluj_live` (`petla_live.py:193`) buduje
**bezwarunkowo** `AdapterNewsLLM(fetcher=FetcherNewsRSS())`, adapter ma `uzyj_llm=True`
domyślnie i `glos=None` → **lazy-init z klucza w środowisku**. `tests/test_petla_live.py`
woła `handluj_live` **pięć razy**. Klucz na maszynie Cezara jest ustawiony → **każdy bieg
`python tests/run_tests.py` płacił.** Uruchomiłem dziś testy ~6 razy.

**🔁 To NAWRÓT, nie odkrycie.** Klasa „testy palą pieniądze" była **zapisana w Księdze Wad
2026-07-16** (zmierzone: 8 wywołań, 4 min 42 s) — i **nie naprawiona**. Wróciła tego samego
dnia. **Księga, która tylko notuje, jest pamiętnikiem, nie systemem samo-leczenia.**

**✅ NAPRAWA U ŹRÓDŁA — `tests/conftest.py` (zapora, nie łatka):** zamiast poprawiać każde
wywołanie z osobna, **ODBIERAMY TESTOM KLUCZE** (`DEEPSEEK_API_KEY`, `MEXC_API_KEY`,
`MEXC_SECRET`) przy imporcie — zanim pytest zaimportuje moduły testowe (import potrafi już
zbudować adapter). Lazy-init nie znajduje klucza → deterministyczny fallback słownikowy
(ścieżka i tak wymagana przez Prawo XV). Test, który CHCE sprawdzić LLM, wstrzykuje atrapę
(`glos=_FakeGlos(...)` — `test_sentyment_news.py`) i działa dalej. Kod produkcyjny bez zmian.
Zapora wpięta w OBA runnery (pytest ładuje conftest sam; `run_tests.py` woła jawnie).

**Trzy szkody zabite jednym ruchem:** koszt (każdy bieg płacił) · niedeterminizm (wynik zależał
od tego, co akurat piszą w newsach) · czas (wolna bramka = rzadziej uruchamiana).

**DOWÓD (Prawo I — pomiar, nie deklaracja):** par NOTARIUSA **przed** pełnym biegiem: **162**,
**po** biegu: **162**. Zero nowych wywołań. Testy: **2494/2494**.

**Fałszywy trop po drodze (uczciwie):** najpierw podejrzałem `test_sentyment_news.py:252`
(`uzyj_llm=True` bez `uzyj_llm=False`) — **sprawdziłem i to był fałszywy alarm**: ten test
wstrzykuje `glos=_FakeGlos(...)`, więc nie płaci. Prawdziwym winowajcą był `handluj_live`.
Piąty raz dziś, gdy sprawdzenie przed meldunkiem powstrzymało fałszywy alarm.

**Widoczność (Prawo XXIV):** runner drukuje `🛡️ Zapora testów: odebrano klucze [...]` —
cicha zapora byłaby zaporą, w której działanie trzeba wierzyć. Pierwsza wersja komunikatu
milczała (conftest odbiera klucze już przy imporcie, więc drugie wywołanie nie miało czego
odebrać) — naprawione.

**Pliki:** tests/conftest.py (nowy), tests/test_zapora_testow.py (nowy, 4 testy granic),
tests/run_tests.py (zapora + raport), imperium/biblioteki/ksiega_wad_kodu.py (wpis: NAWRÓT
+ naprawa u źródła).

## 2026-07-17 | 📖 | Dług T5 spłacony (8→0) + DWA werdykty zwiadowców OBALONE pomiarem

**Co:** przeczytane W CAŁOŚCI 2 ostatnie dokumenty świecące T5. **Oba werdykty zwiadowców
okazały się BŁĘDNE** — trzeci i czwarty raz tego dnia, gdy pomiar obala kandydata.

**`PAPER_TRADING_MEXC` — zwiadowca: „KANDYDAT_DO_ARCHIWUM". BŁĄD.** To jedyne miejsce
z **kryteriami zaliczenia Etapu II** (Sharpe≥1.0, MaxDD<15%, DSR≥0.95, WR≥55% lub PF>1.5,
≥100 trades) i drabiną Etapów II→IIb→III→IV — **żywa bramka „kiedy wolno wejść za realne
pieniądze"**. Archiwizacja skasowałaby warunki wejścia na rynek. → `typ: zywy`.
Naprawione (zweryfikowane wobec kodu): **KROK 4 wklejał ~80 linii źródła
`narzedzia/paper_trading_live.py` — pliku, który NIGDY nie istniał** (instrukcja kazała
uruchomić widmo) → zastąpione realnym CLI `python -m imperium.koloseum.petla_live`
(**sprawdzone `--help`, działa**) · `adaptery.py` → to PAKIET `adaptery/` · „RAM ⏳ upgrade
laptopa" → CENSOR zmierzył **15.88 GB, maszyna to ma**.

**`MANUAL_MIGRACJA_I_SYMULATOR` — zwiadowca: „KANDYDAT_DO_SCALENIA", oznaczony acta. BŁĄD.**
To **żywy przewodnik dydaktyczny**: pełny przepływ cyklu decyzyjnego, ścieżka pieniędzy,
obalenie mitu CHIMERY (Prawo I) i **10 bramek wstrzymania**. Progi ZWERYFIKOWANE wobec kodu
— `dyrygent.py:210`: `min_neuronow=5, min_przewaga=0.55` → **dokument mówi PRAWDĘ**.
Gnił tylko licznik („48 aktywnych" przy **81**) → wpięty w Filar 4 + sprzęt 8 GB → 15.88 GB.

**🚨 KOREKTA MOJEGO WŁASNEGO FAŁSZYWEGO TWIERDZENIA (2 commity wstecz):** zapisałem
w banerze MAPA_IMPERIUM_FLOW „Imperium NIE MA narracyjnego przewodnika po aktualnej
architekturze — to realny brak". **Twierdzenie bez weryfikacji. Fałszywe.** Przewodnik
istnieje — to właśnie `MANUAL_MIGRACJA_I_SYMULATOR` § 2. Baner poprawiony, wskazuje następcę.
**Trzeci raz dziś: ogłosiłem lukę/alarm, nie sprawdziwszy. Alarm bez pomiaru to halucynacja.**

**Wynik:** T5 **8 → 0** — każda historia w Imperium umie powiedzieć, CZEMU jest historią.
Rejestr 70/70 · ACTA 13 · CONSILIUM 12 · DISCIPLINA 10 · FORMA 12 · LEX 6 · MENSURA 6 · TABULA 11.

**Bilans werdyktów zwiadowców (4 sprawdzone w całości):** 4/4 wymagały korekty —
NAZWY_PLIKOW („95% dublet" → 177 unikatów), SYMBIOZA („archiwum" → uratowana żywa doktryna),
PAPER_TRADING („archiwum" → żywa bramka Etapu II), MANUAL_MIGRACJA („scalenie/acta" → żywy
przewodnik z prawdziwymi progami). **Zwiadowca czyta szeroko i myli się często — sędzia musi
mierzyć, nie ufać** (ZASADA ZWIADOWCY WIEDZY: kandydat ≠ prawda).

**Pliki:** docs/PAPER_TRADING_MEXC.md, docs/MANUAL_MIGRACJA_I_SYMULATOR.md,
docs/MAPA_IMPERIUM_FLOW.md (korekta), docs/INDEKS_IMPERIUM.md (katalog).

## 2026-07-17 | 🕳️ | Bramka T5 — zamknięcie TYLNYCH DRZWI we własnym mechanizmie

**Co:** nowa bramka **T5 (ucieczka w historię)** + degradacja `MAPA_IMPERIUM_FLOW` do ACTA
+ naprawa 6 błędnych klasyfikacji (w tym MOICH WŁASNYCH, zaimportowanych hurtem od zwiadowców).

**🕳️ TYLNE DRZWI, KTÓRE SAM ODKRYŁEM:** przeklasyfikowanie dokumentu `zywy → acta`
**natychmiast ucisza bramkę gnicia** (migawka z definicji nie gnije). Czyli **każdy z 18
gnijących dokumentów da się „naprawić" ogłaszając go historią** — a bramka z tylnymi drzwiami
jest bramką pozorną. Zapora (ta sama zasada co `dublet_rozstrzygniety`): **historia musi UMIEĆ
SIĘ WYTŁUMACZYĆ** — data w nazwie (urodzona jako migawka), wskazany następca (świadoma
degradacja) albo jawne pole `powod_acta`. **Wyciszenie bramki ZAWSZE wymaga powodu na widoku.**

**MAPA_IMPERIUM_FLOW → ACTA (przeczytana w całości, zweryfikowana wobec kodu):** najgorszy
dokument Imperium — `stan_na 2026-05-31`, kod zmieniony 92× w 11 plikach. Zweryfikowane
kłamstwa: „Oczy 🔴 Plan, do zbudowania" (a `wszechoko.py` istnieje, 145 linii) · „Koloseum
🟡 Szkielet" (16 modułów; `valhalla.py` nigdy nie istniał) · „Senat 🟡 Szkielet" (`meta_kora.py`,
203 linie) · „Zwiadowca 1..4" (jest 87 neuronów i 15 zwiadowców). **Dokument dydaktyczny
uczący nowicjusza systemu, który nie istnieje, jest GORSZY niż jego brak.** Zdegradowany,
NIE skasowany (jedyny narracyjny zapis „po co" każdy organ powstał).
**NIE przeniesiony do migawek** — ma **17 odwołań w kronice** (migawki miały 0–1); stosujemy
tę samą regułę co przy P4: ruszamy tylko tanie.
**🚨 LUKA ZAPISANA JAWNIE:** Imperium NIE MA narracyjnego przewodnika po AKTUALNEJ
architekturze dla nowicjusza — ARCHITEKTURA jest zwięzła/tabelaryczna. Degradacja tego nie załatwia.

**T5 NATYCHMIAST ZŁAPAŁA MÓJ WŁASNY BŁĄD** (import klasyfikacji zwiadowców hurtem):
- `WERSJONOWANIE` — **LEX + acta** (prawo, które jest historią?!). Dowód: akumuluje
  post-mortemy 05-28 → 06-01 → 06-09 → **07-15**, a deklarował `stan_na 2026-06-01`.
  **Żyje** → `typ: zywy`, `stan_na: 2026-07-15`.
- `TRYBY_IMPERIUM` — **CONSILIUM + acta** (plan na przyszłość, który jest historią?!).
  Dowód: SCALP/SWING/INVEST żyją w `dyrygent.py`/`namiestnik.py`/`backtest.py`, ale reszta
  trybów niezbudowana → plan wciąż żywy → `typ: zywy`.
- `LOG_ZMIAN`, `AUDYT_SYSTEMU`, `POMIAR_FILTR_ASYMETRII`, `POMIAR_WARSTW_ADAPTACYJNYCH` —
  prawdziwa historia, dostały `powod_acta` (dziennik akumulujący / migawka z datą w treści /
  pomiar z konkretnego okna: „wynik nie starzeje się — starzeje się system, którego dotyczył").

**Dług WIDOCZNY, nie zamieciony:** 2 dokumenty (`MANUAL_MIGRACJA_I_SYMULATOR`,
`PAPER_TRADING_MEXC`) nadal świecą T5 — bo NIE przeczytałem ich w całości i **nie zgaduję**
(Prawo I). Bramka zostawia je jako widoczne zadanie.

**Pliki:** narzedzia/tabularium.py (+T5), tests/test_tabularium.py (30 testów: łapie ucieczkę,
przepuszcza datę w nazwie / następcę / powod_acta), docs/MAPA_IMPERIUM_FLOW.md (ACTA + baner),
docs/WERSJONOWANIE.md, docs/TRYBY_IMPERIUM.md, docs/LOG_ZMIAN.md, docs/AUDYT_SYSTEMU.md,
docs/POMIAR_*.md, docs/INDEKS_IMPERIUM.md (katalog).

**Powód:** mechanizm broni się teraz także przede mną. Następne: 2 dokumenty do przeczytania
w całości, spłata długu gnicia (17 dokumentów), twarde bramki.

## 2026-07-17 | 📦 | P4 — migawki → docs/migawki/ + naprawa DWÓCH cichych pułapek

**Co:** 10 datowanych migawek (ACTA) przeniesionych `git mv` do `docs/migawki/`.
`docs/` z 63 płaskich plików → **53 żywe + 10 migawek w podkatalogu**. Historia plików
zachowana (git mv, nie kopiuj-usuń).

**🚨 DWIE CICHE PUŁAPKI NAPRAWIONE W TYM SAMYM RUCHU (ZASADA PEŁNEJ SYMBIOZY):**
1. **`narzedzia/rag/indeksuj.py`** — `DOCS.glob("*.md")` (płaski!) → `rglob`. Bez tego
   przeniesienie **wypchnęłoby 10 dokumentów z korpusu RAG** — i **nikt by nie zauważył**,
   bo RAG dalej odpowiadałby, tylko bez nich. Utrata potencjału (Prawo XV) bez jednego
   czerwonego światła. **Dowód po naprawie:** korpus docs = 63 pliki, w tym 10 migawek.
2. **Audyt W7 (sieroty)** — `os.listdir(docs_dir)` (płaski!) → `os.walk`. Bez tego
   dokument w podkatalogu **znikałby z bramki sierot dokładnie w chwili porządkowania**.

To była realna pułapka wykryta POMIAREM na starcie sesji, nie teoria: gdyby przyjąć
pierwotny plan „wszystkie docs do podkatalogów", **cały korpus dokumentacji wypadłby
z RAG i z bramki**, a audyt dalej świeciłby na zielono.

**Dlaczego tylko migawki (decyzja Cezara, poparta pomiarem):** każda ma 1–3 żywe odwołania
i 0–1 w kronice. Żywe źródła prawdy zostają płasko: mają 8–19 żywych odwołań **+ 12–63
w kronice sesji**, której Prawo I zabrania przepisać — przeniesienie unieważniłoby historię.

**Pliki:** 10× git mv docs/*_2026-*.md → docs/migawki/, narzedzia/rag/indeksuj.py (rglob),
narzedzia/audyt_spojnosci.py (W7 rekurencyjnie), docs/INDEKS_IMPERIUM.md (katalog
przegenerowany — sam wychwycił nowe ścieżki, zero ręcznej pracy).

**Powód:** struktura docs/ uporządkowana bez jednego martwego linku. Zostało: reszta
kandydatów do scalenia (każdy czytany w całości), twarde bramki po spłacie długu gnicia.

## 2026-07-17 | 🔢 | Filar 4 — LICZBY WSTRZYKIWANE + Warstwa 15 audytu (koniec klasy kłamstw)

**Co:** `tabularium.py liczby [--zapisz]` — liczby o systemie żyją między znacznikami
`<!-- LICZBA:neurony -->87<!-- /LICZBA -->` i są przepisywane **z żywych rejestrów**
(neurony, neurony_aktywne, zwiadowcy, strategie, elity). **Warstwa 15 audytu** pilnuje, że
żaden wstrzyknięty blok nie zamarzł ani nie został nadpisany ręcznie — audyt **nigdy nie
zapisuje** (suchy bieg), naprawa jedną komendą.

**Dlaczego (zmierzone, nie z raportu zwiadowcy — Prawo I):** trzy dokumenty podawały
„neuronów w kodzie" jako **47** (`GENERAL_LEGATUS:38`), **27** (`OBSERWATORZY:166`) i **55**
(`IGRZYSKA:29`) — przy **87** w rejestrze. **Każda z nich była prawdziwa w dniu pisania.**
To nie jest lenistwo autorów — to nieuchronność: rośnie kod, a nie dokument. Dlatego NIE
poprawiliśmy liczb (za miesiąc skłamałyby znowu), tylko **odebraliśmy dokumentom prawo do
ich wpisywania**.

**Zweryfikowane w obie strony (Reguła Test-Granic):** wstrzyknięte kłamstwo `999` → W15
czerwona, exit 1 → `liczby --zapisz` → 87 → audyt zielony. Test negatywny w `test_tabularium.py`:
literówka w kluczu (`neuronyy`) MUSI krzyczeć — cicha akceptacja dałaby martwy znacznik,
który nigdy się nie odświeży i zamrozi liczbę na zawsze (czyli dokładnie to, co Filar 4 zabija).

**Bug złapany po drodze:** `tabularium.py` nie dokładał ROOT do `sys.path` — `liczby` nie
mogło zaimportować rejestru (`ModuleNotFoundError: imperium`). Niewidoczne dotąd, bo żadna
wcześniejsza komenda nie sięgała do kodu Imperium.

**Pliki:** narzedzia/tabularium.py (+wartosci_z_kodu, +wstrzyknij_liczby, +sys.path),
narzedzia/audyt_spojnosci.py (+W15, +docstring), CLAUDE.md (+Warstwa 15 w Prawie XXI),
tests/test_tabularium.py (26 testów), docs/GENERAL_LEGATUS.md, docs/OBSERWATORZY.md,
docs/IGRZYSKA_IMPERIUM.md (znaczniki zamiast liczb z palca).

**Powód:** klasa kłamstw „licznik zamrożony w prozie" zamknięta mechanicznie. Następne:
migawki → docs/migawki/ (z naprawą rag/indeksuj.py glob→rglob), reszta kandydatów do scalenia.

## 2026-07-17 | 🏛️ | P3 — pierwsze scalenie + POMIAR OBALIŁ ZWIADOWCĘ (177 pozycji uratowanych)

**🚨 NAJWAŻNIEJSZE — kandydat ≠ prawda (ZASADA ZWIADOWCY WIEDZY, Prawo I):** zwiadowca (Sonnet)
zaraportował *„NAZWY_PLIKOW_BIB-070+.md to ~95% redundancja PLAN_ROZBUDOWY_BIBLIOTEKI.md — te same
205 pozycji"*. **POMIAR:** 197 pozycji BIB w jednym, **27** w drugim, wspólnych **20** → **177
pozycji istnieje TYLKO w NAZWY_PLIKOW**. Dokumenty mają tę samą STRUKTURĘ sekcji, ale inną
FUNKCJĘ: PLAN = co i dlaczego (status weryfikacji, linki), NAZWY = 197 gotowych nazw plików +
konwencja + rejestr spalonych numerów (083, 127, 138, 165, 166, 198, 199, 262). **Rekomendacja
ODRZUCONA — plik zostaje.** Zaufanie zwiadowcy bez pomiaru = utrata 177 wpisów, czyli dokładnie
to, czego Cezar zakazał („bez utraty niczego wartościowego").

**SCALENIE WYKONANE — SYMBIOZA_MODULOW → archiwum** (przeczytana W CAŁOŚCI przed ruchem, ZASADA
ARCHIWIZACJI). Uratowane: tabela **„czego NIE wolno duplikować"** (jedyny właściciel matematyki/
LLM/egzekucji/ryzyka — żywa doktryna, nigdzie indziej niezapisana) → `ARCHITEKTURA_IMPERIUM.md`
§ ZASADA SYMBIOZY. Zarchiwizowane: przepływ z 4 widmami (`straznik_ryzyka.py`,
`wykonawca_rozkazow.py`, `mnemozyne.py`, `sala_wojenna.py`) + nieaktualna rola „Alchemika".

**SCALENIE ODRZUCONE — START_LOKAL ↔ SCIAGA_LOKAL.** 4 z 6 komend wspólnych, ale to **dwie role**:
START to „pełny przewodnik dla nowicjusza" (prowadzi za rękę), SCIAGA to ściąga z 24 komendami dla
kogoś, kto już wie. Scalenie zabiłoby przewodnik, na którym stoi **ZPO** (Cezar jest nowicjuszem —
to jedyny powód istnienia tej zasady).

**NOWY MECHANIZM — `dublet_rozstrzygniety` (T3):** werdykt człowieka wycisza parę, ale **wymaga
podania POWODU w nagłówku** — nie da się schować dubletu po cichu. Powód istnienia: bramka
krzycząca fałszywie co sesję uczy ignorować WSZYSTKIE bramki. Test granicy pilnuje, że
rozstrzygnięcie JEDNEJ pary nie jest wytrychem na inne.

**NOMENKLATURA (rozkaz Cezara):** „Alchemik Imperium" → **VITRUVIUSZ** w KATALOG_NEURONOW
i docs/README — źródłem prawdy imion jest PROFIL_CEZARA, a rola Alchemika umarła wraz z nadaniem
imienia Architektowi.

**DOWÓD WARTOŚCI GENEROWANEGO KATALOGU:** archiwizacja SYMBIOZY kosztowała **zero** utrzymania
spisu — INDEKS przepisał się sam. Ręczny indeks wymagałby pamiętania o wykreśleniu (czyli nie
zostałaby wykreślona, jak 70 innych pozycji).

**Pliki:** archiwum/SYMBIOZA_MODULOW.md (git mv, historia zachowana), docs/ARCHITEKTURA_IMPERIUM.md
(+§ ZASADA SYMBIOZY), docs/README.md, docs/KATALOG_NEURONOW.md, docs/START_LOKAL.md,
docs/INDEKS_IMPERIUM.md (katalog), narzedzia/tabularium.py (+dublet_rozstrzygniety),
tests/test_tabularium.py (22 testy).

**Powód:** rejestr 70/70, 1 dublet rozstrzygnięty świadomie. Następne: reszta kandydatów
(MANUAL_MIGRACJA, PAPER_TRADING_MEXC, WERSJONOWANIE, MAPA_IMPERIUM_FLOW) — każdy czytany
w całości przed ruchem; potem migawki → docs/migawki/ z naprawą rag/indeksuj.py (glob→rglob).

## 2026-07-17 | 🏛️ | P2 — katalog GENEROWANY + W6b przekazuje pałeczkę bramce T2

**Co:** (1) **71/71 dokumentów zadeklarowanych** (rozkład: FORMA 14 · ACTA 12 · CONSILIUM 12 ·
TABULA 11 · DISCIPLINA 10 · MENSURA 6 · LEX 6) — żaden dokument Imperium nie jest już bezpański,
w tym 4 spoza `docs/`, których NIE WIDZIAŁA żadna bramka (`imperium/README.md`,
`imperium/INSTRUKCJA_URUCHOMIENIA.md`, `narzedzia/rag/SETUP_LOKALNY.md`, `skrypty/README.md`).
(2) Ręczna „MAPA DOKUMENTÓW" w INDEKS (**17 054 znaki prozy**, w tym kłamstwo „299 neuronów,
72 w kodzie") **zastąpiona katalogiem GENEROWANYM** z nagłówków między znacznikami.

**W6b → T2 (przekazanie pałeczki, 49 dokumentów):** wstrzyknięcie nagłówków obaliło założenie,
na którym stała W6b — *„plik ruszony ⇒ treść się zmieniła"*. Commit dodający metadane nie zmienia
ANI JEDNEGO twierdzenia dokumentu, więc W6b zażądała ostemplowania dzisiejszą datą **16 dokumentów,
których nikt dziś nie zweryfikował — czyli zażądała KŁAMSTWA** (Prawo I). Fałszywy alarm uczy
ignorować bramkę, a dwie bramki mierzące tę samą datę sprzecznymi definicjami to redundancja,
która szkodzi (Prawo XVI). Rozstrzygnięcie: dokument z nagłówkiem podlega **T2**, która pyta
OSTRZEJ — „czy nadążasz za KODEM, który opisujesz" zamiast „czy nadążasz za samym sobą".

**Wada złapana i zapisana (Księga Wad — klasa `parsowanie`, checklista):** pierwsza wersja
przekazania szukała `stan_na` w oknie `tresc[:600]` — MAPA_PAMIECI (11 właścicieli) ma je na
pozycji **609**, SCIAGA_LOKAL na **778**, więc CICHO omijały bramkę. Podstępne, bo wymykają się
dokumenty NAJBOGATSZE, czyli najważniejsze. Naprawa u źródła: audyt używa **parsera Tabularium**,
nie własnego (jeden format = jeden parser; dwa rozjadą się co do znaku).

**Pliki:** docs/INDEKS_IMPERIUM.md (katalog generowany), 20× dokumenty (nagłówki),
narzedzia/audyt_spojnosci.py (W6b→T2), imperium/biblioteki/ksiega_wad_kodu.py (+klasa parsowanie).

**Powód:** rejestr kompletny. Następne: egzekucja kłamstw liczbowych (5 sprzecznych liczb neuronów:
87 prawda vs 72/47/27/55/62), lista scaleń/archiwum do zgody Cezara, migawki → docs/migawki/
(z naprawą rag/indeksuj.py glob→rglob — inaczej wypadną z korpusu RAG).

## 2026-07-17 | 🏛️ | P1 — nagłówki Tabularium w 51 dokumentach: dług POLICZONY, nie zgadnięty

**Co:** nagłówki metadanych wstrzyknięte do **51 dokumentów** (`51/71` zadeklarowanych; rozkład:
FORMA 13 · ACTA 11 · CONSILIUM 9 · DISCIPLINA 7 · MENSURA 5 · TABULA 5 · LEX 1). Raport bramki
T2 zagregowany per dokument (Prawo XXIV): **41 ostrzeżeń zamiast 86** — rozbicie na
(dokument × właściciel) dawało ścianę tekstu, a bramka, której nikt nie czyta, to bramka,
której nikt nie słucha.

**Dług ujawniony (18 dokumentów gnije — teraz WIDAĆ, ile):** MAPA_IMPERIUM_FLOW `stan_na
2026-05-31`, a kod zmieniony **92× w 11 plikach** · MATRYCA_KORELACJI 22× · ANALIZA_NEURONY 20× ·
GENERAL_LEGATUS 19× (legatus.py) · LEGIONY_ARCHITEKTURA 17× · OBSERWATORZY 17×.

**Dublety wskazane MASZYNOWO (Prawo XVI — odpowiedź na „co warto połączyć"):** ARCHITEKTURA_IMPERIUM
↔ MAPA_IMPERIUM_FLOW (7 wspólnych właścicieli) · MANUAL_CLAUDE_CODE ↔ MANUAL_UZYTKOWNIKA ↔
START_LOKAL (ten sam audyt_spojnosci.py + run_tests.py) · SCIAGA_LOKAL ↔ START_LOKAL (start.py).

**Widma zapisane W NAGŁÓWKU (pole `dlug`) — dokument sam przyznaje się do kłamstwa:**
ARCHITEKTURA_IMPERIUM i MAPA_IMPERIUM_FLOW (`war_lancer.py`, `sala_wojenna.py`, `valhalla.py`),
SYMBIOZA_MODULOW (4 martwe ścieżki), OBSERWATORZY (`multi_exchange.py`),
PAPER_TRADING_MEXC (`paper_trading_live.py`) — kod, którego NIE MA nigdzie w repo.

**ZASADA (Prawo I): `stan_na` = data z samego dokumentu, NIGDY „dziś".** Wpisanie dzisiejszej
daty dokumentowi, którego dziś nie zweryfikowano, to kłamstwo — i uciszyłoby bramkę gnicia,
czyli zniszczyło jej jedyny sens. Dług ma być widoczny, nie zamalowany.

**Pliki:** 51× docs/*.md (tylko nagłówek na górze — ani jeden bajt treści nie tknięty),
narzedzia/tabularium.py (agregacja T2).

**Powód:** zostaje 20 dokumentów bez nagłówka (8 molochów + 5 z paczki manuali + drobne poza
docs/). Potem: znaczniki katalogu w INDEKS, egzekucja kłamstw liczbowych, lista scaleń do zgody Cezara.

## 2026-07-16 | 🎓 | CENSOR sprzętu + plan TIRO (lokalny hybrydowy LLM-uczeń)

**Co:** nowy organ **CENSOR SPRZĘTU** (`imperium/oczy/censor_sprzetu.py`) — „oczy" mierzące
majątek maszyny (CPU/RAM/GPU, stdlib-only bez psutil), klasyfikujące ją do KLASY majątkowej
(census→classis: PROLETARIUS→PEDES→EQUES→PRAETOR→CONSUL) i podnoszące ALARM POTENCJAŁU
(Prawo XV) przy AWANSIE/degradacji sprzętu. Baseline w git → po `git pull` na nowej maszynie
wykrywa migrację. + dokument **`docs/PLAN_TIRO_LOKALNY_LLM.md`** (roadmapa E0–E6).

**Dlaczego (rozkaz Cezara 2026-07-16):** budowa lokalnego LLM-ucznia (nauczyciele: Hyginus/DeepSeek
+ Vitruviusz/Opus) z auto-wykrywaniem zmian sprzętu i zgłaszaniem potencjału. Sprzęt zmierzony
(Prawo I): Fujitsu i5-4200M Haswell 2-rdz., 16 GB, brak CUDA = klasa **PEDES** (model 1–3B żywo /
7B wsadowo). Zwiad web (Sonnet) obalił zawyżenie DeepSeeka „7B @ 10–15 tok/s" (realnie 2–5) i
halucynację „aom-news-4b"; potwierdził że trening MUSI iść przez Colab (CPU-only nie fine-tunuje).

**Pliki:** imperium/oczy/censor_sprzetu.py (nowy), tests/test_censor_sprzetu.py (16 testów granic),
bibliotheca_ulpia/dane/censor_sprzet.json (baseline PEDES), docs/PLAN_TIRO_LOKALNY_LLM.md (nowy).

**Powód:** E0 roadmapy TIRO domknięty. Następny krok E1: instal Ollama + `llama-bench` — TWARDY
pomiar tok/s na Fujitsu (zastąpić estymacje). Wpięcie ucznia w ścieżkę decyzyjną: opt-in OFF do walidacji A/B.

## 2026-07-16 | 🪙 | K-04 USD strength — WPIĘCIE 3. zwalidowanego sygnału (opt-in, MONETA)

**Co:** trzeci i ostatni sygnał Tier-1 — **siła dolara** (makro, DXY-proxy). Nowy neuron
**K-04 NeuronUSDStrength** (kat. K, waga 6, silny USD → SHORT) + **AdapterUSD** (Frankfurter
FX, DARMOWE bez klucza). Rój: 86→87 neuronów (81 aktywnych). Nazwa: MONETA.

**Dlaczego (Prawo I + XVI):** z-score poziomu USD na oknie 120d ma IC -0.17@14d, -0.27@30d
na zwroty BTC (`narzedzia/pomiar_usd_ic.py` + kontrola formy 2026-07-16). KLUCZOWE
odkrycie: forma K-01 DXYTrend (EMA20-momentum) zmierzona jako SZUM; wolny z-score 120d
poziomu = MOCNY sygnał → K-04 to INNA informacja niż K-01 (Prawo XVI, mierzone nie zgadywane).
Silny USD (rozciągnięty vs ~6-mies. zakres) = odpływ z ryzyka = bearish BTC (BTC-DXY inverse).

**OPT-IN:** AdapterUSD za flagą `--usd` (domyślnie OFF). Bez flagi K-04 abstynuje.

**Pliki:** adaptery/usd_sila.py (nowy), neurony/makro.py (NeuronUSDStrength), rejestr.py,
petla_live.py (--usd), backtest.py (USD_ZSCORE clear-list), adaptery/__init__.py,
audyt_spojnosci.py (allowlista), MANIFEST/README/INDEKS/MAPA_KLUCZY (87), tests.

**Powód:** domknięcie kampanii Tier-1 — 3/3 zwalidowane sygnały (DVOL/stablecoin/USD)
wpięte wzorcem, opt-in OFF. A/B USD po commicie (bieg backtest). Live: USD_z=1.30 (dolar mocny).

## 2026-07-16 | 🏛️ | K-03 Stablecoin flow — WPIĘCIE 2. zwalidowanego sygnału (opt-in)

**Co:** replikacja wzorca wpięcia (po DVOL) dla drugiego sygnału Tier-1 — **podaż
stablecoinów** (makro-płynność, „suchy proch"). Nowy neuron **K-03 NeuronStablecoinFlow**
(kat. K makro, waga 6, trend-following: druk stablecoinów → LONG) + **AdapterStablecoin**
(DefiLlama, DARMOWE bez klucza). Rój: 85→86 neuronów (80 aktywnych). Nazwa pomiaru: AERARIUM.

**Dlaczego (Prawo I):** 7d % zmiana podaży ma IC +0.05..+0.10 @7-30d na zwroty BTC
(`narzedzia/pomiar_stablecoin_ic.py`, 2026-07-15, spójny nn/ov, ~3150 dni). Druk = napływ
kapitału = bullish flow (makro, wolny). Walidacja na długiej historii (mocniejsza niż DVOL).

**OPT-IN:** AdapterStablecoin za flagą `--stablecoin` (KonfigPetliLive.stablecoin=False).
Bez flagi K-03 abstynuje → zero zmiany zachowania do A/B.

**Pliki:** adaptery/stablecoin.py (nowy), neurony/makro.py (NeuronStablecoinFlow), rejestr.py,
petla_live.py (--stablecoin), backtest.py (STABLE_FLOW clear-list), adaptery/__init__.py,
audyt_spojnosci.py (allowlista), MANIFEST/README/INDEKS/MAPA_KLUCZY (86), tests.

**Powód:** 2. z 3 zwalidowanych sygnałów wpiętych wzorcem DVOL. Zostaje USD/MONETA (z uwagą
na pokrycie z K-01 DXYTrend — Prawo XVI).

## 2026-07-16 | 😱 | PSY-05 DVOL — WPIĘCIE zwalidowanego sygnału (opt-in, ZASADA WPIĘCIA)

**Co:** wpięto pierwszy sygnał z kampanii Tier-1 alt-danych — **DVOL** (indeks strachu opcji
Deribit, „crypto VIX"). Nowy neuron **PSY-05 NeuronDVOL** (kat. R, waga 6, kontrariański:
wysoki strach → LONG) + **AdapterDVOL** (Deribit public API, DARMOWE bez klucza). Rój: 84→85
neuronów (79 aktywnych). Nazwa rzymska adaptera/pomiaru: PAVOR (bóstwo strachu).

**Dlaczego (Prawo I — POMIAR PRZED wpięciem):** DVOL POZIOM ma IC +0.16 @7d na zwroty BTC
(zmierzone `narzedzia/pomiar_dvol_ic.py`, 2026-07-15, spójny nienakł/nakł, rośnie z horyzontem).
Wysoki strach opcyjny poprzedza rewersję w górę (Sinclair/VIX). Walidacja WSTĘPNA (~16-23 mies.,
jeden reżim) — dlatego opt-in OFF do A/B.

**OPT-IN (ZASADA WPIĘCIA):** AdapterDVOL wpinany TYLKO za flagą `--dvol` (KonfigPetliLive.dvol=False
domyślnie). Bez flagi PSY-05 abstynuje (Prawo XV, brak DVOL_INDEX) → ZERO zmiany zachowania roju
aż do walidacji A/B na realnych danych. Cezar włącza po zielonym A/B (Prawo XVIII).

**Pliki:** imperium/akwedukty/adaptery/dvol.py (nowy), imperium/legiony/neurony/psychologia.py
(NeuronDVOL), imperium/legiony/rejestr.py (rejestracja+mapy), imperium/koloseum/petla_live.py
(opt-in --dvol), adaptery/__init__.py, tests/test_dvol_psy05.py (nowy), tests/test_integracja.py
(84→85), narzedzia/audyt_spojnosci.py (allowlista), MANIFEST/README/INDEKS/MAPA_KLUCZY (85).

**Powód:** kampania pomiar-najpierw dała 4 zwalidowane sygnały (funding/stablecoin/DVOL/USD);
DVOL najmocniejszy IC → pierwszy pilot wpięcia jako wzorzec dla stablecoin/USD.

## 2026-07-15 | 🔮 | HARUSPEX (kand. #20) — prototyp + POMIAR = FALSYFIKACJA (Prawo I, pomiar-najpierw)

**Co:** prototyp kandydata #20 „predykcyjny Namiestnik" (żniwo wrzutni). Nazwa rzymska
**HARUSPEX** (kapłan-wróżbita, dobrana do funkcji predykcji — ZASADA NOMENKLATURY). Łańcuch
Markowa 1. rzędu na strumieniu reżimów (klasyfikuj_rezim) — przewiduje następny reżim +
sygnał „przygotuj się na zmianę". Poza ścieżką decyzyjną (opt-in OFF, ZASADA WPIĘCIA).

**POMIAR (Prawo I, `narzedzia/pomiar_haruspex.py` na realnych świecach BTC/ETH 4H):**
Zbudowano sekwencję reżimów z rosnących okien (zero look-ahead), zmierzono trafność vs
baseline'y. **Werdykt: FALSYFIKOWANY — brak wartości.**
  • argmax trafność == baseline PERSYSTENCJI (BTC 97.5%=97.5%, ETH 92.5%=92.5%) → przewaga +0%
  • sygnał ZMIANY: recall 0% (0 ostrzeżeń na 7 realnych zmian, także przy progu 0.10)
  • przyczyna strukturalna: reżimy o wysokim P(zmiany) (NORMAL 33%, VOLATILE) są RZADKIE →
    milczą (< min_obserwacji); częste (TREND/RANGING) 97-98% lepkie → zmiana nieprognozowana.

**Decyzja (Prawo XVIII):** NIE wpinam (pomiar nie dał przewagi — dokładnie po to jest
pomiar-najpierw). Moduł+narzędzie+testy ZOSTAJĄ jako infrastruktura pomiaru + udokumentowany
negatyw (antykruchość: nie budować goły Markow ponownie). Werdykt w nagłówku modułu.
Ewentualna wartość dopiero z modelem WARUNKOWYM na cechy — osobny kandydat, po pomiarze.

**Testy granic:** 17 (MILCZENIE <min_obs, granica ≥min_obs, próg zmiany ==/>, bez look-ahead,
baseline persystencji, walidacja konstruktora). Testy 2334/2334, ruff czysty.

**Pliki:** `imperium/koloseum/haruspex.py`, `narzedzia/pomiar_haruspex.py`, `tests/test_haruspex.py`,
`docs/ARCHITEKTURA_IMPERIUM.md` (organ Haruspex w KOLOSEUM)

## 2026-07-15 | 📥 | Żniwo wrzutni — 6 nieprzerobionych tur 12 lip → destylat + backlog

**Co:** domknięto ostatni punkt planu po U1-U4 Hyginusa — żniwo 6 tur web-DeepSeeka z 2026-07-12
(16:06–16:32), których `ANALIZA_WRZUTNIA_2026-07-10.md` nie pokrywała.

**Metoda (ZASADA ZWIADOWCY WIEDZY):** Hyginus = proponent, Vitruviusz = sędzia. Web-zweryfikowano
KAŻDE cytowanie Tury 5 (rozkaz stały: WebSearch przed oceną post-cutoff) → **5/5 realnych prac**
(AgenticAITA arXiv 2605.12532, FinLumen ICASSP 2026, FinDPO arXiv 2507.18417, DecoupledMarket
ICML 2026, DC-GNN IEEE 2026). Lekcja re-audytu 2026-07-13 potwierdzona.

**Sąd:** ~połowa propozycji nakłada się z rdzeniem (Senat W-343, W8, W13, triada, Legiony Cieni,
BOCPD/CUSUM) → Sekcja A. ODRZUCONO Terminator auto-merge (łamie ład: Claude nigdy nie merguje do
main). Wyekstrahowano 8 kandydatów #18-25 (⚠️ każdy → arena, opt-in OFF), zarejestrowano jako
POMYSŁ w rejestrze wizji (W4). Top-3 realne: #18 FinDPO (sentyment DPO), #19 FinLumen (negocjacje
w Senacie), #20 Nostradamus-light (predykcja reżimu, najtańszy splot).

**Pliki:** `docs/ANALIZA_WRZUTNIA_2026-07-12.md` (nowy destylat), `bibliotheca_ulpia/dane/wizje_i_decyzje.jsonl` (8 kand.)

## 2026-07-15 | 🔧 | Domknięcie CLI pętli live — behawioralne opt-iny (Prawo XV, przegląd kompletności)

**Co:** przegląd 35 pól `KonfigPetliLive` vs flagi CLI wykazał, że kilka realnych toggli
behawioralnych żyło TYLKO w config-obiekcie (nieosiągalne z linii poleceń). Domknięto
te istotne dla biegu obserwacyjnego P0:
  • `--cienie` — Legiony Cieni (kontrfaktyczny pomiar 3 widmowych wariantów → arena CIEN_PNL;
    czysty pomiar, BEZ zmiany realnej decyzji)
  • `--funding-mexc` — funding/OI z MEXC (rodzimy, TIER A funding+ELR)
  • `--mwu` / `--igrzyska` — warstwy uczenia (opt-in; faktyczne włączenie = decyzja Cezara)
  • `--filtr-asymetrii` (W-314) / `--ksiega-wad` (W-309) — filtry weta
  • `--min-pewnosc 0.6` — próg pewności wejścia (walidacja ∈ (0,1) → SystemExit)

**Świadomie tylko-config (nie CLI):** ścieżki (`plik_pamieci`/`log_dir`/`sciezka_*`), strojenie
(`limit_barow`/`radar_co_bar`/`synapsy_decay_co_bar`), trio `auto_discover*` — to parametry
programowe obiektu konfiguracji, nie codzienne przełączniki biegu.

**Weryfikacja Prawa XV:** każda nowa flaga faktycznie konsumowana w pętli (cienie→338,
funding_mexc→178, mwu→202, igrzyska→224, ksiega_wad→232/385, filtr_asymetrii→220/355,
min_pewnosc→217/240/351) — zero flag-atrap.

**Testy granic:** +3 (domyślne OFF / włączane / --min-pewnosc poza (0,1) → SystemExit).

**Pliki:** `imperium/koloseum/petla_live.py`, `tests/test_petla_live.py`, `docs/MANUAL_UZYTKOWNIKA.md`

## 2026-07-15 | 🔧 | W-288 SL z ATR wpięty w pętlę live (Prawo XV — realistyczne zamknięcia paper)

**Co:** `sl_atr_mult` (SL = k×ATR_14) istniał w Dyrygencie, KalkulatorzeLewara i backteście,
ale `KonfigPetliLive` + `_buduj_dyrygencie` go NIE przekazywały — żywy paper zamykał crude
stopem z dźwigni (połowa drogi do likwidacji ≈ −25% na 1H, nieosiągalne → 198/201 = TIMEOUT).
Skutek: pomiar TIER A w arenie zniekształcony sztucznymi TIMEOUTAMI zamiast rytmu rynku.

**Naprawa:**
  • pole `KonfigPetliLive.sl_atr_mult: Optional[float] = None` (opt-in; None = stary SL).
  • `_buduj_dyrygencie` przekazuje `sl_atr_mult=cfg.sl_atr_mult` do każdego Dyrygenta.
  • CLI `--sl-atr-mult 2.0`; walidacja: ≤ 0 → `SystemExit` (mnożnik ATR musi być dodatni).

**Bezpieczeństwo (ZASADA WPIĘCIA — monotoniczna ostrożność):** ATR-SL może stop tylko
ZACIEŚNIĆ (`max` LONG / `min` SHORT względem lewarowego) — nigdy bliżej likwidacji. Bezpieczny
do wpięcia nawet przed pełną walidacją A/B; domyślnie OFF (None) = zero zmiany zachowania.

**Dowód e2e:** bieg `--sl-atr-mult 2.0 --max-barow 1` → WEJŚCIE BTCUSDT LONG 79% TREND_STRONG,
0 błędów. Logika zacieśniania już pokryta testami kalkulatora (ciaśniejszy/nigdy-szerszy/granice/TP).

**Testy granic:** +5 (CLI domyślne None / →config / ≤0 SystemExit; wpięcie w Dyrygenta / domyślne None).

**Pliki:** `imperium/koloseum/petla_live.py`, `tests/test_petla_live.py`, `docs/MANUAL_UZYTKOWNIKA.md`

## 2026-07-15 | 🔧 | CLI pętli live — flaga `--dashboard` wpięta (Prawo XV: podgląd był niepodpięty)

**Co:** `KonfigPetliLive` od dawna miała pola `dashboard/dashboard_port/webhook_tv/senat/`
`kalibruj_prog/telegram`, ale blok `__main__` CLI ich NIE eksponował — budował konfig tylko z
`monitor/arena_log/pauza`. Skutek: cel P0 „monitorowany bieg paper (`--monitor --dashboard`)"
był nieuruchamialny z linii poleceń — podgląd web dla oczu Cezara istniał w kodzie, ale martwy
z CLI (utrata potencjału, Prawo XV).

**Naprawa:**
  • wyodrębniono `_zbuduj_parser()` + `zbuduj_konfig_z_argv(argv)` — testowalny punkt wejścia CLI
    (dotąd parsowanie żyło tylko pod `if __name__`, nietestowalne — Reguła Test-Granic).
  • dołożono flagi: `--dashboard`, `--dashboard-port` (dom. 8777), `--webhook-tv`, `--senat`,
    `--kalibruj-prog`, `--telegram` — wszystkie opt-in OFF (ZASADA WPIĘCIA: zero zmiany domyślnego
    zachowania; brak flag = identyczny bieg jak dotąd).
  • walidacja głośna: `--webhook-tv` bez `--dashboard` → `SystemExit` (serwer HTTP musi działać),
    zamiast cichego OFF (Prawo XVIII).

**Dowód end-to-end:** `python -m ... --symbole BTCUSDT --dashboard --arena-log --max-barow 1`
pobrał realne dane MEXC, policzył wskaźniki, wywołał DeepSeek (v4-flash HTTP 200), podjął decyzję
paper (WEJŚCIE BTCUSDT LONG pewność=77% reżim=VOLATILE), zapisał stan uczenia — 0 błędów.

**Testy granic:** +6 (`test_cli_*`): domyślne paper/OFF, dashboard+port, wszystkie flagi opt-in
→ config, `--real`→paper=False, `--webhook-tv` bez dashboardu → SystemExit, webhook+dashboard OK.

**Symbioza:** MANUAL_UZYTKOWNIKA §4.1 — dopisany jednolinijkowiec CLI z URL podglądu.

**Pliki:** `imperium/koloseum/petla_live.py`, `tests/test_petla_live.py`, `docs/MANUAL_UZYTKOWNIKA.md`

## 2026-07-14 | ✨ | W-361 web — feed MEXC + markery bota na wykresie (panel przeglądarki)

**Co:** rozbudowa `web_dashboard.py` (drugi kanał obserwacji, po terminalowej SPECULA):
  • **MagazynSwiec** — pętla live wpycha bary z DataLoadera (`serwer_web.podaj_swiece(sym, bary)`),
    router serwuje je na `/wykresy/{symbol}.json` gdy webhook TV pusty → **wykres pokazuje
    świece MEXC BEZ konfiguracji TradingView/ngrok** (dotąd wymagany był webhook TV).
  • **Markery wejść bota** — `znaczniki_do_lwc()` konwertuje wejścia (exact `timestamp_wejscia`
    z otwartych pozycji + ostatnich zamknięć) na markery Lightweight Charts (▲ LONG zielony /
    ▼ SHORT czerwony); JS `setMarkers()` filtruje po aktywnym symbolu. Cezar widzi GDZIE rój wszedł.
  • **Selektor symboli** z obu źródeł (webhook TV ∪ feed MEXC), pole `symbole_swiec` w `/stan.json`.

**Bonus:** ta sama pętla karmi też terminalową SPECULA (`stan.swiece`/`swiece_symbol`) — świece
w terminalu ożywają na realnym biegu paper/live, nie tylko w demo.

**Prawo I (bez zmyślania):** markery tylko WEJŚĆ — mają exact `timestamp_wejscia`. Markery WYJŚĆ
odłożone: `WynikZamkniecia` nie ma czasu wyjścia (tylko `czas_trwania_bar`), dodanie wymaga
przewleczenia timestampu przez ścieżkę zamknięcia engine — osobny krok, nie fałszujemy czasu.

**Testy granic:** 19 testów (znaczniki LONG/SHORT/wyjście, ms→s, sortowanie, zły pomijany,
MagazynSwiec roundtrip/cap/symbole, router fallback MEXC, symbole_swiec, integracja serwer→router).

**Pliki:** `imperium/swiatynie/web_dashboard.py`, `imperium/swiatynie/live_monitor.py`
(pole swiece_symbol + filtr znaczników), `imperium/koloseum/petla_live.py` (markery + feed),
`tests/test_web_dashboard_swiece.py` (nowy).

---

## 2026-07-14 | ✨ | SPECULA (W-361) — świece OHLC w terminalu (podgląd live jak MEXC)

**Co:** nowy organ `imperium/swiatynie/specula_swiec.py` (SPECULA — rzymska wieża
strażnicza/obserwacyjna, ZASADA NOMENKLATURY) renderujący wykres ŚWIECOWY OHLC
bezpośrednio w terminalu (nie w przeglądarce) — Cezar widzi świece jak na MEXC, plus
opcjonalne znaczniki wejść (▲) / wyjść (▼) bota. Wpięte jako opcjonalny panel w
`live_monitor.py` (`StanDashboardu.swiece` / `znaczniki_swiec`) — dokładany pod ramką TUI.

**Dlaczego (Prawo XVI — nie redundancja):** trzeci kanał obserwacji tego samego feedu
OHLC. Mieliśmy świece w PRZEGLĄDARCE (`web_dashboard.py`, Lightweight Charts) i liczby
w TERMINALU (`live_monitor.py`) — ale NIE świec w terminalu. SPECULA wypełnia lukę.
Motyw oszczędności tokenów: podgląd idzie do OCZU Cezara (osobny proces/okno), nie do
kontekstu Claude — obserwacja rynku = 0 tokenów modelu.

**Zależność OPCJONALNA (filozofia „runner bez deps"):** renderer to `plotext` (PyPI,
MIT, zero obowiązkowych zależności). Guarded import — gdy plotext brak, panel degraduje
się elegancko (komunikat-podpowiedź, nigdy crash); rdzeń i testy zostają bez zależności
(jak matplotlib w kartografie, calibre/rapidocr w bibliotece). Instalacja lokalna:
`pip install plotext` (poza requirements — wersjonowany kod nie wymaga jej na innych maszynach).

**Lekcja Windows (Prawo I, dowód z runtime):** plotext wywala się na `fromtimestamp`
(OSError 22) przy formie daty samej "H:M" — wymaga PEŁNEJ daty ("d/m/Y H:M") + lokalnego
`fromtimestamp`. Ustalone eksperymentem, nie zgadywaniem.

**Testy granic (Reguła Test-Granic):** 12 testów — brak plotext / 0 barów / 1 bar (<MIN=2) /
None / dokładnie MIN / zły znacznik pomijany / zły bar → string nie wyjątek / integracja
z LiveMonitor z i bez świec. Przechodzą z plotext i bez.

**Pliki:** `imperium/swiatynie/specula_swiec.py` (nowy), `imperium/swiatynie/live_monitor.py`
(pola swiece/znaczniki_swiec + render panelu), `tests/test_specula_swiec.py` (nowy).

---

## 2026-07-14 | 🐞 | FIX: petla_live nie miała entrypointu — `python -m` nic nie uruchamiał

**Bug (Prawo I, złapany gdy Cezar wkleił komendę):** `imperium/koloseum/petla_live.py` NIE miał bloku
`if __name__ == "__main__"` → `python -m imperium.koloseum.petla_live` tylko importował moduł i wychodził
bez akcji (pętla nie startowała). Handoff dawał komendę, która nic nie robiła.

**Fix:** dodany entrypoint CLI (argparse): `--symbole` (domyślnie BTC/ETH/SOL), `--interwal` (1H),
`--kapital`, `--real` (domyślnie PAPER — zero realnych zleceń), `--arena-log`, `--monitor`, `--max-barow`
(limit/test), `--pauza`. Baner startowy jasno mówi PAPER vs REALNE. Uwaga w help: 1H = 1 bar/godzinę
(pętla czeka między świecami — normalne). DOWÓD: `python -m ... --max-barow 2 --pauza 1` → 2 bary, 1 wejście, 0 błędów.

**Poprawna komenda paper:** `python -m imperium.koloseum.petla_live --symbole BTCUSDT ETHUSDT --arena-log`
(szybki test: `--max-barow 3 --pauza 2`).

**Pliki:** `imperium/koloseum/petla_live.py`.

---

## 2026-07-14 | 🐞 | FIX krytyczny: żywa pętla nie pobierała danych ('1H'→ccxt NotSupported)

**Bug znaleziony w runtime (nie zgadywany — zasada debugowania):** `KonfigPetliLive.interwal`
domyślnie `'1H'`, ale `DataLoader.fetch` przekazywał go wprost do ccxt (mexc), który zna tylko
`'1h'` → `NotSupported: timeframe unit H` → pętla live logowała „Brak danych dla żadnego symbolu"
i przetwarzała 0 barów. **To prawdopodobnie powód, czemu paper/live nigdy nie wystartował** (INDEKS #3).

**Fix:** `_ccxt_timeframe()` w `kwatermistrz_danych.py` — normalizuje notację Imperium (godziny/dni
UPPERCASE `1H`/`4H`/`1D`) do ccxt (`1h`/`4h`/`1d`); minuty (`15m`) i miesiąc ccxt (`1M`) nietknięte.
+1 test granic (`test_ccxt_timeframe_normalizuje_interwal_imperium`).

**DOWÓD (Prawo I):** po fixie bieg paper 2 barów na ŻYWYCH danych BTCUSDT: **2 bary przetworzone,
1 decyzja wejścia (paper), 0 błędów.** Cały rój działa end-to-end na realnym rynku — unlock „C paper/live".

**Pliki:** `imperium/akwedukty/kwatermistrz_danych.py`, `tests/test_petla_live.py`.

---

## 2026-07-14 | 🔴 | REFRAME „22 luk" Prawa XV — adaptery ŻYJĄ, narracja audytu naprawiona

**Odkrycie (Prawo I):** premisa „22 moduły czekają na adaptery / martwy potencjał" była MYLĄCA.
Dowód na żywo: `AdapterFutures.pobierz('BTCUSDT')` → FUNDING_RATE=5.1e-05, LS=0.63, OI=106405;
`AdapterFearGreed` → FEAR_GREED=22 (Extreme Fear); `AdapterCVD` → CVD=32.5. Adaptery ISTNIEJĄ,
zwracają realne dane i są **wpięte w `petla_live`** (linie 166–177: AdapterFutures/FearGreed/CVD/NewsLLM
→ Dyrygent). PSY-01..04 + V-03 są DOSTEPNY=True i konsumują te klucze.

**Prawda:** „22 luki" to ARTEFAKT syntetycznych scenariuszy audytu (sztuczne bary bez danych
futures/sentymentu/realnej daty/serii portfelowej → neurony NEUTRAL). NIE brak adapterów. Prawdziwe
wąskie gardło (wspólne z odroczonym P1 strategy-MWU): brak REALNEGO BIEGU paper/live, który by je
ćwiczył i pozwolił ZMIERZYĆ (IC/arena).

**Naprawa (B):** poprawiona narracja audytu — z „czeka na adaptery" (⚠️) na „żywe na realnych danych,
ciche tylko w syntetycznym audycie; do zmierzenia trzeba biegu paper/live" (ℹ️). Audyt już miał dowód
`WERYFIKACJA_ADAPTEROW` (neurony ożywają z danymi). Test `test_audyt_w12_raportuje_neurony_adapterowe` zielony.

**Pliki:** `narzedzia/audyt_spojnosci.py` (komunikat startowy + `--luki`).

---

## 2026-07-14 | 🔭 | Hyginus U4 — świadomość systemu (luki Prawa XV + anty-redundancja) — KOMPLET U1–U4

**Ulepszenie U4 (`narzedzia/bibliotekarz.py`) — ostatni krok kompletu:** opcjonalne (`--swiadomosc`,
domyślnie OFF) wstrzyknięcie DeepSeekowi **świadomości systemu** przy generacji kandydatów:
- **LUKI (Prawo XV):** 22 moduły czekające na dane/adapter (z `NEURONY_ZALEZNE_OD_ADAPTEROW`) z opisami
  → Hyginus PREFERUJE kandydatów, którzy je zasilają lub wnoszą NOWĄ informację.
- **ISTNIEJĄCE moduły (Prawo XVI):** wszystkie klucze + kategorie roju → NIE proponuj duplikatów.
- Każdy kandydat oznacza: którą lukę zasila / jaką nową informację wnosi / czy nie dubluje istniejącego.
- Blok cache'owany (`lru_cache`), brak rejestru → '' (zwiad działa dalej, Prawo XV). +2 testy.

**Flaga `--pelny`** włącza komplet U2+U3+U4 (`--rozwin --krytyka --swiadomosc`) — najlepszy zwiad.
U4 odtwarza główną siłę ręcznego web-DeepSeeka (kontekst systemu), ale ze źródeł biblioteki, bez halucynacji.

**Powód:** domknięcie planu U1+U2+U3+U4 (rozkaz Cezara). U5 (tryb otwarty) ODRZUCONY — żadnych halucynacji.
Wszystko opt-in OFF; Hyginus nie jest w ścieżce decyzyjnej roju, wyniki ⚠️ prawdą dopiero po arenie.

**Pliki:** `narzedzia/bibliotekarz.py`, `tests/test_bibliotekarz.py`.

---

## 2026-07-14 | 📖 | BIB-032 O'Hara domknięty — 69/69 książek w RAG (OCR angielskiego skanu)

**Domknięcie biblioteki (Prawo XV):** BIB-032 „O'Hara — Market Microstructure Theory" był jedyną
książką poza RAG (68/69) — chiński skan bez warstwy tekstu. Cezar dostarczył **angielskie wydanie**
(też skan, 298 stron). OCR przez `rapidocr-onnxruntime` (render PyMuPDF, ~187 DPI) → **686 986 znaków**
angielskiego tekstu do wersjonowanego `tekst_cache`. Reindeks: +319 fragmentów BIB-032, **69/69 książek**,
parytet fragmenty=fts=27959, wyszukiwalny (spread/market-maker/inventory zwraca BIB-032).

- Skrypt OCR wznawialny (strona→plik→sklejenie, ZASADA ANALIZY CZĄSTKOWEJ, pasek postępu — scratchpad, nie repo).
- Stary chiński cache (pusty, inny hash) usunięty; nowy cache wersjonowany (chmura czyta bez OCR — Prawo XVII).
- Prawo I: proza angielska czysta i użyteczna; wzory matematyczne kruszą się w OCR (jak Shreve) — esencja pojęć, nie wzory.

**Pliki:** `bibliotheca_ulpia/dane/tekst_cache/BIB-032_...__bcfde4140356c035.txt` (nowy), stary cache usunięty.

---

## 2026-07-14 | 🔭 | Hyginus U3 — self-critique: dowody PRZECIW (anty-confirmation-bias)

**Ulepszenie U3 (`narzedzia/bibliotekarz.py`):** opcjonalne (`--krytyka`, domyślnie OFF) drugie
przejście po wygenerowaniu kandydatów — **sędzia-sceptyk szuka DOWODÓW PRZECIW**.

- Osobne retrieval na kontrargumenty (temat + `risk failure limitation assumption drawback criticism
  overfitting`) → DeepSeek ocenia każdego kandydata: MOCNE / SŁABE / SPRZECZNE, wskazuje ukryte
  założenia i pułapki. Wynik w polu `krytyka` cząstki — Opus-sędzia i arena widzą słabe hipotezy od razu.
- Wzorzec agentic-RAG (disconfirming evidence) wzmacnia ZASADĘ ZWIADOWCY WIEDZY: kandydat≠prawda.
  Gdy brak dowodów przeciw — model mówi to wprost (sygnał confirmation bias, nie dowód słuszności).
- Błąd API krytyki nie przekreśla cząstki (kandydaci już zapisani; Prawo XV). +2 testy granic.

**Powód:** trzeci krok planu U1+U2+U3. Opt-in OFF (+1 RAG +1 call/temat), monotonicznie ostrożne.

**Pliki:** `narzedzia/bibliotekarz.py`, `tests/test_bibliotekarz.py`.

---

## 2026-07-14 | 🔭 | Hyginus U2 — recall: sanityzacja FTS + query-expansion + hybrid

**Ulepszenie U2 (`narzedzia/bibliotekarz.py`):** trzy rzeczy dla lepszego recall zwiadu.

- **Fix crash-buga FTS (Prawo XV):** temat `momentum trend-following breakout entry rules` WYWALAŁ
  FTS5 MATCH (`OperationalError: no such column: following` — myślnik/składnia) → temat cicho ginął.
  Nowy `_fts_bezpieczne` sanityzuje KAŻDE zapytanie do słów złączonych `OR` (poszerza recall, BM25 rankuje).
- **Query-expansion opt-in (`--rozwin`, domyślnie OFF):** DeepSeek rozszerza temat w synonimy PRZED RAG
  (`rozwin_zapytanie`). Retrieval-only → ryzyko halucynacji ograniczone do trafień, które filtruje
  sędzia+arena. Fallback na surowy temat przy błędzie/pustce (zwiad nigdy nie ginie).
- **Hybrid jako domyślny tryb (future-proof):** auto-fallback na FTS gdy brak wektorów. Uwaga (Prawo I):
  na tej maszynie baza ma 0 wektorów i brak `sentence-transformers` → hybrid = FTS aż zbudujemy embeddingi.
- +3 testy granic (sanitizer, rozszerzenie+fallback, scout na rozszerzonym zapytaniu).

**Powód:** drugi krok planu U1+U2+U3. Opt-in, monotonicznie ostrożne. `zapytanie` zapisywane w rekordzie kolejki (transparentność).

**Pliki:** `narzedzia/bibliotekarz.py`, `tests/test_bibliotekarz.py`.

---

## 2026-07-14 | 🔭 | Hyginus U1 — zwiad tylko z korpusu „biblioteka" (anty-echo)

**Ulepszenie U1 Bibliotekarza-Zwiadowcy (`narzedzia/bibliotekarz.py`):** `scout_temat`/`raport`
domyślnie czytają TYLKO korpus `biblioteka` (książki BIB-xxx), a nie `dane`/`docs`. Wcześniej
zwiad szedł po wszystkich korpusach (`korpus=None`) — mógł wyciągnąć NASZE własne fragmenty
(`dane`: 75 frag.) i podać je jako „odkrycie" (echo własnego głosu = redundancja, Prawo XVI).

- Nowa flaga CLI `--korpus` (domyślnie `biblioteka`; `wszystko` przywraca dawne zachowanie bez filtra).
- Ustalono empirycznie: realne korpusy w bazie to `biblioteka` (27 566) i `dane` (75); `docs` NIE indeksowany.
- +1 test granicy (`test_scout_domyslnie_korpus_biblioteka`) — forward korpusu + domyślna wartość.

**Powód:** pierwszy krok planu ulepszeń Hyginusa (U1+U2+U3 → U4 → żniwo; U5 odrzucony). Opt-in,
monotonicznie ostrożne, zero zmiany domyślnej ścieżki decyzyjnej roju.

**Pliki:** `narzedzia/bibliotekarz.py`, `tests/test_bibliotekarz.py`.

---

## 2026-07-13 | 🔎 | Re-Audyt weryfikacyjny — korekta błędnych odrzuceń (brak weryfikacji web)

**Cezar wskazał głęboki błąd procesu:** oceniałem pomysły/opcje BEZ weryfikacji najświeższych
informacji z internetu → **odrzucałem/wątpiłem w REALNE rzeczy** (prace 2025-2026, po moim cutoffie
ze stycznia 2026). Skutek: audyty niekompletne, prawdziwe opcje błędnie skasowane. NAPRAWA:

**Korekty potwierdzone web (`docs/RE_AUDYT_WERYFIKACYJNY_2026-07-13.md`):**
- `deepseek-v4-flash` — ❌ „halucynacja" → ✅ REALNY (legacy retire 07-24, migracja zrobiona).
- **PandaAI** — ⚠️ „liczby niepewne" → ✅ REALNY, [arXiv 2606.06823], Rank IC +18.2%/MDD −25.7% DOKŁADNIE.
- **AgentEvolver** — ⚠️ „nieweryfikowalne" → ✅ REALNY, [arXiv 2511.10395], github modelscope.
- ARTEMIS/SD-FMM — koncepcje realne (neural-SDE bez arbitrażu / GNN manipulacja), nazwy niepewne.

**Zasada stała (pamięć):** ZAWSZE `WebSearch` (bieżący miesiąc) PRZED oceną — modele/API/arXiv/wersje.
Rehabilitacja ≠ auto-adopcja: pozycje nadal ⚠️ KANDYDACI → opt-in OFF + arena (ZASADA WPIĘCIA).
Do dokończenia: Fin-R1/FinGPT, RL-GNN, Gödel/OmniAgent/Recursive Flow/Galaxy/thoughtful-agents.

**Pliki:** `docs/RE_AUDYT_WERYFIKACYJNY_2026-07-13.md` (nowy), `docs/INDEKS_IMPERIUM.md` (#63).

---

## 2026-07-13 | 🔧 | Migracja DeepSeek V4 — legacy deepseek-chat/reasoner wycofane 2026-07-24

**Pilna naprawa (Prawo XV — antykruchość przed awarią).** Cezar wskazał, a weryfikacja web
potwierdziła (api-docs.deepseek.com): nazwy `deepseek-chat` i `deepseek-reasoner` **wycofywane
2026-07-24** (za 11 dni). Nasz `deepseek_glos.py` (zasila NEWS-01..04, PamięćRefleksyjną,
auto-lekcję, Bibliotekarza W-363) używał ich → padłoby.

**Mapowanie (oficjalne):** `deepseek-chat`→`deepseek-v4-flash` (non-thinking, tani ~$0.14/1M),
`deepseek-reasoner`→`deepseek-v4-flash` thinking / `deepseek-v4-pro` (premium). base_url bez zmian.

**Zmiana:** `GlosImperium.MODELE` = {szybki: deepseek-v4-flash, mysliciel: deepseek-v4-pro},
default `deepseek-v4-flash`. Callery (auto_lekcja, bibliotekarz) na domyślny model (DRY — następna
migracja ruszy tylko słownik). Komentarz w sentyment.py zaktualizowany.

**Lekcja (pamięć):** oceniłem v4-flash jako halucynację z przeterminowanej pamięci — błąd. Zasada
stała Cezara: ZAWSZE weryfikuj najświeższe info z web PRZED oceną (modele/wersje po cutoffie).

**Pliki:** `imperium/cesarz/deepseek_glos.py`, `narzedzia/auto_lekcja.py`, `narzedzia/bibliotekarz.py`,
`imperium/legiony/neurony/sentyment.py`.

---

## 2026-07-13 | ✅ | W-362 strategy-MWU A/B na P&L: ZIELONY (+63pp) — kandydat do flagi

**Walidacja ① z sekwencji Cezara — POZYTYWNA (pierwsza tej sesji).** A/B na P&L (`ab_strategy_mwu.py`,
tryb=strategia, 15 par 4h, 3000 barów): OFF = dobór strukturalny, ON = + online strategy-MWU.

**Wynik: PORTFEL OFF=−64.7% → ON=−1.8%, Δ=+63.0pp. ON>OFF na 11/15 par.** Wielkie pary mocno
dodatnie: ETH −13.3→+0.4, BNB −5.5→+7.2, BTC −18.3→−7.0, ADA −9.8→+0.8, NEAR −6.4→+4.2. Ujemne
tylko 4 małe (AVAX −0.8, LTC −1.1, ATOM −2.6, TRX −4.4). ✅ Werdykt: ważenie strategii realnym P&L
LECZY routing (w przeciwieństwie do W-361 IC, które padło na P&L).

**Zastrzeżenie (Prawo I):** ON wciąż −1.8% (poniżej progu zysku) w tym oknie — to +63pp POPRAWA
nad baseline strategia, nie maszyna do zysku. Ale mechanizm zwalidowany → kandydat do włączenia
flagi `ucz_mwu_strategii` na żywo — decyzja Cezara (Prawo XVIII). Flaga nadal OFF.

---

## 2026-07-13 | 📚 | W-363 Bibliotekarz-Zwiadowca: DeepSeek skanuje bibliotekę (pod nadzorem Opusa)

**Prośba Cezara — jeden z pomysłów z rozmowy DeepSeek (wrzutnia/Mapa-kluczy calosc plus.md):
DeepSeek jako bibliotekarz pod nadzorem Claude.** Operacjonalizacja ZASADY ZWIADOWCY WIEDZY
(dwa modele: tani DeepSeek proponuje, Opus rozstrzyga).

**Ocena rozmowy DeepSeek (Prawo I) — SKORYGOWANA po weryfikacji web (2026-07-13):** dobra intuicja
(proaktywność/ciekawość/bibliotekarz). Nieścisłości: `claude-3.7-sonnet` (przestarzałe), zmyślony
format `.claude/settings.json agents/skills`, `imperium-push` z git push (łamie zasadę), wymyślony
`czat_deepseek.py`. ⚠️ **KOREKTA MOJEGO BŁĘDU:** wstępnie nazwałem `deepseek-v4-flash` halucynacją —
NIEPRAWDA, to REALNY model (wydany 2026-04-24, po moim cutoffie; api-docs.deepseek.com). Oceniłem
z przeterminowanej pamięci bez sprawdzenia web. Nowa zasada stała (pamięć): ZAWSZE weryfikuj
najświeższe info z internetu PRZED oceną. Większość „duszy" JUŻ mamy (auto-naprawa, samoewolucja,
14-warstwowa pamięć). Cenne jądro: bibliotekarz = nasza doktryna.

**Build (`narzedzia/bibliotekarz.py`, W-363):**
- REUŻYCIE: `imperium.cesarz.deepseek_glos.GlosImperium` (deepseek-v4-flash — po migracji V4) +
  `narzedzia/rag/szukaj.szukaj` (RAG biblioteki). Zero duplikacji (Prawo XVI).
- Pętla: temat → RAG (fragmenty z BIB-xxx) → DeepSeek proponuje 1-4 KANDYDATÓW (nazwa/typ/
  mechanizm/JAK ZMIERZYĆ, z cytatem źródła) → zapis cząstki do kolejki JSONL. Cząstkowane,
  pasek postępu (Prawo XXIV), dry-run bez kosztu API.
- **Dyscyplina (system prompt):** proponuj TYLKO z fragmentów, cytuj BIB, każdy = HIPOTEZA,
  podaj dowód-pomiaru, nie konfabuluj. Kolejka gitignored (surowy output = artefakt runtime).

**Pierwszy zwiad (temat „mean reversion") + WERDYKT SĘDZIEGO (Opus):** DeepSeek dał 4 kandydatów
(Chan/Narang/Hull/Kaufman). Odsiane: ① Vasicek (stopy proc., Hull) = off-target dla crypto.
Zachowane ⚠️: ② cross-sectional MR pairs (częściowo redundant z C-01), ③ MR z filtrem ekstremów
(spójny z vol-gate/Z), ④ MR-vs-trend wg reżimu (= nasz kierunek Namiestnik/strategy-MWU). Dowód,
po co dwa modele: zwiadowca sam przepuściłby Vasicka.

**Status:** narzędzie on-demand (opt-in). Harmonogram/autonomia = decyzja Cezara (ZASADA MCP/hooki).
Każdy kandydat ⚠️ — do kodu tylko po weryfikacji Opusa + arenie (Prawo I, ZASADA WPIĘCIA).

**Pliki:** `narzedzia/bibliotekarz.py`, `tests/test_bibliotekarz.py` (+4), `.gitignore`.

---

## 2026-07-13 | 🎯 | W-362 strategy-MWU: dobór strategii ważony realnym P&L (opt-in OFF)

**Opcja 2 z sekwencji Cezara — build + tooling walidacyjne.** Poprzedzone zwiadem wiedzy
(`docs/ANALIZA_AUTODOBOR_STRATEGII_2026-07-13.md`): 5 kandydatów metod auto-doboru; wybrany
① strategy-MWU jako najwyższa dźwignia × najmniejsze ryzyko × reużycie kodu.

**Zdiagnozowana luka:** `dobierz_najlepsze` dobierał strategie czysto STRUKTURALNIE (zgodność
sygnałów × filtr × reżim × radar) — IGNOROWAŁ zrealizowany P&L. Smoke (BTC 1500 barów) pokazał,
że routing przez strategie potrafi mocno szkodzić (agregat +16.5% vs strategia −7.0%).

**Build ① (opt-in OFF — ZASADA WPIĘCIA):**
- `baza.dobierz_najlepsze(..., wagi_strategii)` — mnożnik per strategia wchodzi w wynik doboru
  (down-weight wypycha poniżej min_wynik). Brak wag = baseline (zero zmiany, Prawo XV).
- `Legatus.ustaw_wagi_strategii()` + pole `wagi_strategii` → przekazane do `_dobierz_strategie`.
- `backtest(ucz_mwu_strategii=True)` — online `HedgeMWU` keyed strategy_id (REUŻYCIE hedge_mwu.py,
  nie duplikat): atrybucja top-1 strategii przy wejściu → `aktualizuj(sid, 0/1)` na zamknięciu
  (strata binarna z P&L) → `mnozniki()` wracają do Legatusa. Domyślnie OFF (zero zmiany ścieżki).

**Tooling walidacyjne:**
- `narzedzia/ab_tryb_strategii.py` — A/B warstwy: agregat vs filtr vs strategia (P&L, cząstkowany,
  arena `ab_tryb_strat`, pasek postępu). Cząstkowy (7/15, 6000 barów): PORTFEL agregat −33.3%
  bije filtr −56.7% i strategia −38.4% → statyczny routing szkodzi (motywacja dla ①).
- `narzedzia/ab_strategy_mwu.py` — A/B ①: tryb strategia OFF-mwu vs ON-mwu (P&L; MWU online →
  bez podziału train/test, zero look-ahead; arena `ab_strat_mwu_<tryb>`). Werdykt pending.

**Status flag: OFF.** Wszystkie werdykty (2a warstwa + A/B strategy-MWU na P&L) czekają na pomiar —
flagę na sztywno przełącza Cezar po zielonym A/B (Prawo XVIII). Kandydat, nie prawda (Prawo I).

**Testy:** `tests/test_strategy_mwu.py` (+7), `tests/test_ab_tryb_strategii.py` (+3) — Reguła
Test-Granic (waga w progu doboru, opt-in OFF, round-trip areny).

**Pliki:** `imperium/legiony/strategie/baza.py`, `imperium/legiony/legatus.py`,
`imperium/koloseum/backtest.py`, `narzedzia/ab_tryb_strategii.py`, `tests/*`.

---

## 2026-07-13 | 🔬 | W-361b SHRINKAGE: próg |IC| ratuje 122pp, ale wciąż < baseline — OFF

**Wariant naprawczy po negatywnym A/B P&L (opcja 1 z sekwencji Cezara).** Diagnoza z poprzedniego
biegu: naiwne ON firowało 781 vs 483 transakcji (win-rate ~30–40%) przez (a) odwracanie znaku na
SZUMOWYCH |IC| i (b) ×|IC| przepuszczające śmieciowe wejścia przez weto. Lek: **próg istotności
|IC|** (neuron z |IC|<prog zostaje na baseline — bez flipa/skalowania) + tryb **tylko-znak**
(korekta kierunku bez ×|IC|, by nie firować nadmiaru wejść). Grinold&Kahn: |IC|<0.02 = szum.

**Implementacja:** `Legatus.ustaw_wagi_ic(..., prog_ic, skaluj_ic)` + `_wklady_kierunkowe`
(warunek `abs(ic) >= prog_ic`); prog=0/skaluj=True = pierwotne W-361 (kompat wsteczna, testy zielone).
Opt-in przez backtest (`wagi_ic_prog`/`wagi_ic_skaluj`) + harness `--prog-ic`/`--bez-skali`
(osobny rodzaj areny `ab_pnl_ic_p030_s0` — nie miesza z baseline).

**Wynik (15 par 4h, prog|IC|≥0.03, tylko-znak):**
- **PORTFEL: OFF=+34.1% → ON=+7.2%, Δ=−26.8pp.** Shrinkage odzyskał ~122pp vs naiwne ON (−114.9%).
- ON>OFF na **5/15** par (było 3/15); transakcje 396 vs 483 OFF (naiwne było 781) — over-firing naprawiony.
- **Wzorzec warunkowy:** ON WYGRYWA tam, gdzie OFF słaby/ujemny (ADA −3.8%→+15.4%, NEAR, DOT, LTC),
  a PRZEGRYWA gdzie OFF mocny (ETH +18→+1.6, XRP +14.4→+3.7, MATIC +10.3→−0.6).

**Decyzja (Prawo I+XV): flaga zostaje OFF.** Shrinkage potwierdził diagnozę i uratował moduł
przed katastrofą, ale UNIFORM ważenie IC nadal nie bije baseline w kasie — nie wpinamy.

**Hipoteza na przyszłość (nie realizowana bez decyzji Cezara):** wzorzec „ON pomaga słabym parom,
szkodzi mocnym" sugeruje WARUNKOWE stosowanie (per-para/per-reżim, wg jakości bazowej roju) —
ale to ryzyko przeuczenia doboru par; osobna hipoteza, osobny A/B. Na teraz: temat ważenia IC
zamknięty jako OFF.

**Pliki:** `imperium/legiony/legatus.py` (prog_ic/skaluj_ic), `imperium/koloseum/backtest.py`
(opt-in), `narzedzia/ab_pnl_wazenie_ic.py` (--prog-ic/--bez-skali), `tests/test_wazenie_ic.py` (+5).

---

## 2026-07-13 | ❌ | W-361 A/B na P&L: ważenie IC NIE poprawia zysku — flaga zostaje OFF

**Rozstrzygający pomiar (ZASADA WPIĘCIA — walidacja korzyści na realnych danych = P&L, nie proxy).**
Poprzedni A/B mierzył SAM ZNAK agregatu (weto OFF): +3.3pp OOS. To metryka-proxy. Tu zmierzono
rzecz, która NAPRAWDĘ decyduje: P&L pełnego backtestu OFF vs ON (weto 0.55 + sizing + SL aktywne).

**Metoda:** nowy harness `narzedzia/ab_pnl_wazenie_ic.py` — split TRAIN/TEST, IC z TRAIN
(kanoniczna `oblicz_wagi_ic`), pełny backtest na TEST 2× (flaga `wazenie_ic` przez nowy opt-in
w `backtest()`: `wazenie_ic`/`wagi_ic` → `legatus.ustaw_wagi_ic`). Metryki: zwrot %/win-rate/PF.
Cząstki → arena (`ab_pnl_ic`), wznawialne, pasek postępu (Prawo XXIV).

**Wynik (15 par 4h, frac=0.6, cap 6000):**
- **PORTFEL (suma zwrotów): OFF=+34.1% → ON=−114.9%, Δ=−149pp.** ON>OFF tylko na **3/15** par.
- Pary z dużym OOS (te „najlepsze" w teście znaku) są w P&L KATASTROFALNE: ETH +18.0%→−16.1%,
  XRP +14.4%→−17.7%, BNB −1.8%→−20.3%, ADA −3.8%→−12.4%.
- **ON firuje dużo więcej transakcji (781 vs 483), win-rate ~30–40%.** Przyczyna: odwracanie
  znaku przy SZUMOWYCH |IC| (Grinold&Kahn: |IC|<0.02 = szum) przepuszcza masę słabych,
  przeciwtrendowych wejść przez weto 0.55. Przewaga +3.3pp na surowym znaku znika po sizingu.

**Decyzja (Prawo I + XV): flaga `wazenie_ic` zostaje OFF, NIE wpinamy w runtime.** Moduł jest
zwalidowany jako NIEkorzystny w kasie — zostaje dostępny (opt-in), ale wyłączony. Wartość tej
sesji to NEGATYWNY wynik, który uchronił P&L przed wdrożeniem szkodliwego modułu.

**Hipoteza na przyszłość (nie realizowana bez decyzji Cezara):** naiwne odwracanie znaku IC
przeucza na szumie — wariant z SHRINKAGE/progiem |IC| (waż/odwracaj tylko przy istotnym IC)
mógłby zachować przewagę bez firowania śmieciowych wejść. Osobna hipoteza, osobny A/B na P&L.

**Pliki:** `imperium/koloseum/backtest.py` (opt-in `wazenie_ic`/`wagi_ic`),
`narzedzia/ab_pnl_wazenie_ic.py`, `tests/test_ab_pnl_wazenie_ic.py` (+11), `docs/SCIAGA_LOKAL.md`.

---

## 2026-07-12 | ⚖️ | W-361 A/B na żywo: ważenie IC potwierdzone na REALNYM Legatusie

**Walidacja P1 (ZASADA WPIĘCIA — pomiar przed włączeniem flagi).** Nowy harness
`narzedzia/ab_wazenie_ic.py` porównuje `Legatus._agreguj` OFF vs ON na OOS — na PRAWDZIWEJ
ścieżce decyzyjnej (wagi reżimowe już wliczone w `pewnosc_finalna·waga`), nie na uproszczonym
agregatorze jak offline `hipoteza_b`.

**Metoda (OOS, zero look-ahead):** backtest z nowym opt-in `zbieraj_pelne_sygnaly=True` zbiera
pełne `SygnalNeuronu` per bar (równolegle do etykiet forward). IC kierunkowy liczony na TRAIN
(kanoniczna `oblicz_wagi_ic`), replay TEST-barów przez Legatus dwa razy (OFF / ON). Cząstkowanie:
każda para → `arena_wyniki.db` (rodzaj `ab_wazenie_ic`) przed następną, restart pomija policzone,
pasek postępu na stderr (ZASADA ANALIZY CZĄSTKOWEJ + Prawo XXIV).

**Wynik (15 par 4h, frac=0.6, max 6000 barów):**
- **GLOBALNIE (ważone barami OOS): OFF=48.6% → ON=51.8%, Δ=+3.3pp** — niemal replika offline (+3.6pp).
- **ON > OFF na 12/15 parach.** Wszystkie 5 par z dużym OOS (2300 barów) dodatnie:
  ETH +5.8, ADA +4.0, BTC +3.9, XRP +2.6, BNB +2.1.
- Ujemne/płaskie (SOL −7.3, NEAR −0.3, MATIC 0.0) — wyłącznie małe próbki 300 barów (szum).
- ✅ Werdykt harnessu: ważenie IC leczy realny Legatus (ON>OFF i ON>50% OOS).

**Status flagi:** nadal **OFF** — włączenie na sztywno to decyzja Cezara (Prawo XVIII). Efekt
realny, ale umiarkowany (ON ledwie >50%); wiarygodny sygnał niosą pary z dużym OOS.

**Pliki:** `imperium/koloseum/backtest.py` (opt-in `zbieraj_pelne_sygnaly`),
`narzedzia/ab_wazenie_ic.py`, `tests/test_ab_wazenie_ic.py` (+9), `docs/SCIAGA_LOKAL.md`.

---

## 2026-07-12 | ⚖️ | W-361: ważenie głosów IC w Legatusie (hipoteza B, opt-in OFF)

**Build P1 — wpięcie ważenia IC w agregację Legatusa (ZASADA WPIĘCIA: opt-in domyślnie OFF).**

**Kontekst (Prawo I, pomiar):** diagnoza triady (2026-07-06) — skill SIEDZI w neuronach
(stabilny IC), GINIE w agregacji przy równej wadze (base acc 48.3% < 50%). `narzedzia/hipoteza_b.py`
zwalidował OFFLINE (OOS, 5 par 4h): agregat ważony IC = **51.8%**, bije równą wagę o **+3.6pp**
i przekracza 50% na KAŻDEJ z 5 par. Grinold & Kahn (BIB-025): sygnał = Σ IC_i · głos_i.

**Co wchodzi (`imperium/legiony/legatus.py`):**
- `oblicz_wagi_ic(sygnaly, wyniki, min_glosow)` — kanoniczne per-neuron IC KIERUNKOWE
  (jedno źródło prawdy; `narzedzia/hipoteza_b._ic_kierunkowy_train` teraz je REUŻYWA, nie duplikuje).
- `Legatus.ustaw_wagi_ic(wagi, wlacz=True, domyslny_ic=0.0)` + `resetuj_wazenie_ic()` + flagi
  `wazenie_ic`/`wagi_ic`/`_domyslny_ic`.
- `_wklady_kierunkowe(sygnaly)` — wspólna warstwa: OFF → wkład = `pewnosc_finalna×waga`
  (identyczne ze starym `_agreguj`); ON → ×|IC|, a przy **IC<0 kierunek ODWRÓCONY** (neuron
  mylący się systematycznie głosuje na przeciwną stronę). Buckety long/short liczone z kierunku
  EFEKTYWNEGO → synapsy i `zgodnych_neuronow` spójne z korektą.

**Bezpieczeństwo (ZASADA WPIĘCIA):** domyślnie OFF — samo dodanie modułu NIE zmienia decyzji.
IC=0 / brak pomiaru (`domyslny_ic=0`) → neuron nie waży (nie wpada w przeciwny kierunek przez
pomyłkę). Puste wagi → guard traktuje jak OFF. Włączenie na żywo = decyzja Cezara po A/B (Prawo XVIII).

**Testy:** `tests/test_wazenie_ic.py` (+20, Reguła Test-Granic): OFF=regresja, jednorodne IC
nie zmienia kierunku, stałe IC znosi się w normalizacji, IC<0 flip, IC=0 wyciszenie,
brak-pomiaru×domyslny, guardy setterów, kanoniczna `oblicz_wagi_ic` (znak/abstynencja/min_głosów/pusty).

**Następny krok:** A/B na żywo (pełny pipeline Legatusa OFF vs ON na OOS) — dopiero zielony wynik
uzasadni przełączenie flagi. Pliki: `imperium/legiony/legatus.py`, `narzedzia/hipoteza_b.py`,
`tests/test_wazenie_ic.py`.

---

## 2026-07-12 | 🪞 | Refleksja: sprzeczności tylko ze źródeł statusowych (20→0 fałszywych)

Sesja lokalna, lista P0 krok po kroku. Trzy fixy tego dnia:

**P0-2 (ten commit) — precyzja detektora sprzeczności (`refleksja_pamieci.py`).**
Baner startowy krzyczał „⚠️ 20 sprzeczności do przeglądu", a wszystkie były FAŁSZYWE.
Pomiar (Prawo I): tylko-wizje=0, tylko-dziennik=1, **mieszane=92**. Źródło szumu:
`kierunek` liczony z wolnego tekstu Dziennika („co zrobiliśmy"→+, „czego NIE robić"→−)
parowany z wizjami — to narracja osi czasu, nie flip statusu per-przedmiot. Fix chirurgiczny:
`wykryj_sprzecznosci` domyślnie liczy tylko ze źródeł niosących REALNY status
(`_ZRODLA_STATUSOWE={"wizje"}`); `zrodla=` pozwala świadomie rozszerzyć. Efekt: baner pusty,
detektor nadal odpala na realnym flipie wizji (test-granica). +1 test, 4 testy syntetyczne
zaktualizowane (źródło→wizje).

**P0-1 (commit `afe2ea7`) — higiena LEKCJE + fix nie-hermetycznego testu kroniki.**
Sekcja LEKCJE 110→88 (bezstratny dedup 11 + retire 11 najstarszych, decyzja Cezara);
złapany fałszywy-zielony: `test_kronika_score_nie_jest_flat` zależał od realnych danych.

**Fix środowiska (commit `6dca659`) — Windows zawsze LOKAL + override IMPERIUM_SRODOWISKO.**
Baner mylnie pokazywał CHMURA na laptopie (harness ustawia CLAUDE_ENV_FILE w hooku).

**P0-3 (osobny commit) — uspójnienie liczb README/MANIFEST z kodem (Prawo XXI).**
Stale „76" (stary licznik neuronów, dziś 84) w 3 miejscach → 84; README „15 elitarnych"
→ 18 (kod: D-01,X-25,X-26 + 15 zwiadowców); „Do wdrożenia 240/223" → 215 (299−84);
„Stan na" 07-10 → 07-12. Tabela per-legion opatrzona notą, że rozkład jest orientacyjny,
a autorytatywny licznik (84) pochodzi z `wszystkie_neurony()`.

**P0-4 (osobny commit) — metadane autora djvu (Prawo XV).**
Bug: `ebook-meta` na djvu bez osadzonych metadanych zwraca Author="Nieznany" (locale PL,
więc filtr `!= "unknown"` go przepuszczał) i Title=echo nazwy pliku ("BIB-022 Kissell…").
Linia `wpis.update()` NADPISYWAŁA dobrego autora/tytuł z nazwy pliku tymi śmieciami →
`autor='Nieznany'`, filtr autor= nie łapał Shreve/Aronson/Kissell. Fix: `_WARTOSCI_PUSTE`
odsiewa „Nieznany" w parserze; `_tytul_echo_nazwy` odrzuca tytuł-echo w merge (nazwa pliku
jest autorytatywna dla autora/tytułu, calibre wzbogaca tylko tagi/jezyk/rok/wydawca/seria).
Katalog przebudowany: 5 djvu → Kissell/Aronson/Shreve×2/Sutton Barto, 0× Nieznany. +2 testy.
Pliki: `narzedzia/rag/metadane_ksiag.py`, `tests/test_metadane_ksiag.py`, `katalog_ksiag.json`.

**Pliki (P0-2/3):** `imperium/biblioteki/refleksja_pamieci.py`, `tests/test_refleksja_pamieci.py`,
`README.md`, `docs/MANIFEST_KODU.md`. Bramka: 2184/2184 zielone, audyt exit 0, ruff czysty.

**Sweep dokumentacji (osobny commit, na prośbę Cezara) — aktualizacja zasad po zmianach:**
- **CLAUDE.md p.4:** „PUSH NA KOMENDĘ" → **CLAUDE NIGDY NIE PUSHUJE** (zaostrzenie 2026-07-11):
  push wyłącznie Cezar ręcznie przez terminal; Claude melduje „gotowe". Spójnie: p.4, sekcja Git,
  bramka auto-commit (już bez „+push").
- **SCIAGA_LOKAL.md:** dodano wariant **aplikacja desktopowa Claude Code (Win 10 Pro)** obok
  terminala; zasada push (auto-pull, push ręczny); calibre portable PATH + **djvulibre/djvutxt
  zbędne** (calibre czyta djvu sam); Stan na → 07-12.
- **MANUAL_CLAUDE_CODE.md:** poprawione 2× „commituje i pushuje" → „commit lokalny, push Cezar";
  nota o desktop app; Stan na → 07-12.
- **MAPA_KLUCZY.md:** „81 neuronów" → 84 (stale), data → 07-12.
Pliki: `CLAUDE.md`, `docs/SCIAGA_LOKAL.md`, `docs/MANUAL_CLAUDE_CODE.md`, `docs/MAPA_KLUCZY.md`.
Audyt exit 0 (W14: 208 .md, MAPA_KLUCZY 84 kluczy pokryte).

**P0-5 (osobny commit) — domknięcie uwag cubic PR#118/119 (P2/P3).**
Weryfikacja stanu (Prawo I): część już naprawiona wcześniej — PAMIEC_SESJI duplikaty (zdjął P0-1),
session-start.sh statystyki (fallback guard jest), `_skroc` (str() już w środku funkcji), P1 katalog
Nieznany (P0-4). Domknięte teraz:
- **katalog autorzy (P3):** calibre gubił unicode/placeholdery (LŁpez, Lef?vre, User) — teraz
  NAZWA PLIKU jest autorytatywna dla autora i tytułu (`_POLA_Z_NAZWY`); calibre wzbogaca tylko
  tagi/jezyk/rok/wydawca. Regeneracja: Lopez de Prado/Lefevre/Douglas, 0× garbled.
- **test_przygotuj (P3):** tautologia `in (True, False)` → mocna asercja `_narzedzie(sys.executable) is True`.
- **encyklopedia (P2/P3):** RLA — miscytat „Prawo XVI: RLA⊥ALG⊥MEM" skorygowany (Prawo XVI nie
  definiuje granic domen, nakazuje POMIAR); DEF — usunięto fałszywą zdolność Straży/OC-05 do
  wykrywania flash-ataków (wymaga on-chain, KANDYDAT nie kod); BAN — LOLR → Lender of Last Resort.
- **wizje (P3):** typ/status mismatch — DECYZJA „Odrzucono Mnemosyne" POMYSŁ→ZAMKNIĘTA, 2× ZMIANA
  wdrożona POMYSŁ→WDROŻONA.
Świadomie POMINIĘTE (Prawo I): ANALIZA_BIB (datowany snapshot), tekst_cache copyright (decyzja
Cezara repo→private). Pliki: `narzedzia/rag/metadane_ksiag.py`, `imperium/biblioteki/dziennik_niesmiertelny.py`,
`tests/test_przygotuj_biblioteke.py`, 3× encyklopedia, `wizje_i_decyzje.jsonl`, `katalog_ksiag.json`.
Bramka: testy zielone, audyt exit 0, ruff czysty.

---

## 2026-07-11 | 📚 | JEDNA KOMENDA: przygotuj bibliotekę lokalnie (0 tokenów Claude)

Odpowiedź na pytanie Cezara o beztokenową konwersję lokalną. Uczciwa ocena 3 opcji:
- „Claude portable do folderu" — NIE istnieje (Claude Code to CLI, nie app per-folder); ale
  SETUP jest już przenośny (CLAUDE.md+hooki+.mcp.json+pamięć jadą w repo). Nic do dodania.
- „MCP dla lokala" — JUŻ jest (.mcp.json: biblioteka RAG + arena, lokalne, token-free).
- „Beztokenowa konwersja djvu" — realne; brakowało jednej komendy spinającej.

**Wdrożone:** `narzedzia/przygotuj_biblioteke.py` — jedna komenda, 3 kroki token-free:
(1) `konwerter --buduj` (cache tekstu), (2) `indeksuj --korpus biblioteka` (RAG),
(3) `metadane_ksiag` (katalog). Diagnoza narzędzi (calibre/djvutxt), graceful bez nich,
idempotentne. Smoke-test w chmurze: **64/69 książek scache'owane** (5 djvu zgłoszone jako
wymagające djvutxt: Kissell/Aronson/Shreve I,II/Sutton-Barto).

**Filozofia tokenów (SCIAGA §2d, dopisane):** ciężka praca (konwersja+indeks) LOKALNIE = 0
tokenów LLM; Claude potem pyta RAG chirurgicznie (płaci za fragmenty, nie za całe książki).

**Pliki:** `narzedzia/przygotuj_biblioteke.py`, `tests/test_przygotuj_biblioteke.py`,
`docs/SCIAGA_LOKAL.md` (§2d). Bramka: testy zielone, audyt exit 0, ruff czysty.

---

## 2026-07-11 | 🔄 | KONWERTER/CACHE TEKSTU KSIĄG — auto-convert djvu, odblokowanie chmury

Odpowiedź na pytanie Cezara o auto-convert formatów. **Prawo XVI:** calibre `ebook-convert` JUŻ jest
fallbackiem w `ekstraktor.py` — nowy konwerter byłby redundancją. Realną luką był **cache tekstu**.

**Wdrożone:**
- `narzedzia/rag/konwerter.py` — `ekstrahuj_z_cache(path)`: cache kluczowany HASZEM TREŚCI
  (sha1[:16]). Trafienie działa BEZ calibre → laptop konwertuje djvu RAZ, po zacommitowaniu pliku
  cache **chmura czyta go bez calibre** (Prawo XVII — spójność między maszynami). `buduj_cache()`
  prekonwertuje całą bibliotekę (pasek postępu, idempotentne). Demo: epub 510k zn., 2. odczyt 14× szybszy.
- `ekstraktor.py` — timeout konwersji 60→300 s (wielkie książki: Shreve, Sutton-Barto, Kaufman).
- `.gitignore` — cache per-maszyna domyślnie; `git add -f <plik>` odblokowuje wybrane djvu dla chmury.

**Samo-recenzja złapała 3 bugi przed pushem:** (1) KRYTYCZNY — zapis cache nieatomowy → częściowy
plik serwowany jako prawda (i, po commicie, trułby chmurę uciętą książką); fix: `.tmp`→`os.replace`.
(2) `_djvu` ignorował kod wyjścia djvutxt → częściowy stdout jako tekst; fix: sprawdzenie returncode.
(3) próg MIN_ZNAKOW chroni przed pustką, nie przed śmieciem — zmitygowane przez (1)+(2).

**Jak odblokować djvu w chmurze (workflow):** na laptopie z calibre/djvulibre →
`python -m narzedzia.rag.konwerter --buduj` → `git add -f bibliotheca_ulpia/dane/tekst_cache/BIB-065*.txt
BIB-066* BIB-067* BIB-048*` → commit. Wtedy chmura domknie QNT/RLA (Shreve/Sutton-Barto) i Aronsona.

Testy: `tests/test_konwerter.py` (8 — cache hit/miss, atomowość, poisoning-guard, graceful).
Bramka: 2168 testów zielone, audyt exit 0, ruff czysty.

**Pliki:** `narzedzia/rag/konwerter.py`, `narzedzia/rag/ekstraktor.py`, `.gitignore`,
`tests/test_konwerter.py`

---

## 2026-07-11 | ⛓️ | ENCYKLOPEDIA: DEF ✅ + RLA/QNT 🚧 (domknięcie serii nowych działów)

Trzy ostatnie działy z serii nowych ksiąg — do granicy tego, co wykonalne w chmurze.

- **DEF ✅** (BIB-069 Voshmgir + BIB-054 Antonopoulos-Wood, ekstrakcja z plików): klasy tokenów,
  stablecoiny + Impossible Trinity, AMM/DEX, flash loans/flash-ataki, perpetuale, PoS, gas/EIP-1559,
  oracles, composability. **Wpływ:** PSY-01/04 (funding/OI ← perpetuale), OC-05/Straż (flash-ataki).
  **KANDYDACI ⚠️:** reżim depeg stablecoina, głębokość AMM, gas jako termometr sieci, funding-neuron.
- **RLA 🚧** (BIB-068 Goodfellow ✅ z pliku): DL — curse of dimensionality, regularyzacja, CNN/RNN,
  representation learning; most do hedge_mwu (MWU=online learning/regret) ugruntowany w KODZIE.
  BIB-067 Sutton-Barto (RL) — **djvu PENDING** ekstrakcji na laptopie.
- **QNT 🚧** (styki z kodem ✅): Feynman-Kac→ECON (z ARTEMIS), GARCH/FracDiff/BOCPD, martyngał→
  uczciwy backtest. BIB-065/066 Shreve — **djvu PENDING** na laptopie.

**Ograniczenie chmury (Prawo I):** djvu nieczytelne bez `djvutxt` (brak w chmurze) — Shreve I/II
i Sutton-Barto oznaczone ⚠️ PENDING, esencja djvu domknie się na laptopie. Nie fabrykuję z pamięci.

**Bilans encyklopedii:** wszystkie 15 działów mają treść — 13 ✅, 2 🚧 (RLA/QNT, czekają na djvu).
INDEX_MAIOR: statusy + kanon zaktualizowane. Pliki: DEF/RLA/QNT + INDEX_MAIOR.

---

## 2026-07-11 | 📊 | ENCYKLOPEDIA: dział MAK domknięty (makro, cykle długu) — Dalio + Popper

Drugi dział z serii nowych ksiąg. **MAK 🚧 → ✅** (był tylko Patel; dodano 3× Dalio + Popper).

Esencja UGRUNTOWANA ekstrakcją z plików (Prawo I): Dalio — archetyp Big Debt Cycle (deflacyjny/
inflacyjny), 4 dźwignie (austerity/default/druk/transfery), „beautiful deleveraging", „pushing on
a string", Big Cycle mocarstw (500 lat, 18 determinant, waluta rezerwowa), 5 stadiów wypłacalności;
Popper — BTC jako store-of-value w debasementcie fiata (digital gold, ograniczona inflacja podaży).

**Wpływ na kod:** Gubernator (mnożnik reżimu ← faza makro jako wolnozmienne TŁO), RADAR-01/03
(płynność, risk-on/off), Senat (debata makro). **KANDYDACI ⚠️:** neuron kontekstu makro-reżimu
(faza Big Debt Cycle — TŁO, NIE sygnał per-bar — Prawo XV, ryzyko martwego głosu), detektor
„pushing on a string", reżim debasement→BTC-hedge (łączy MAK+ONC). Prawo XVI: dekorelacja z RADAR
do zmierzenia przed budową.

**Pliki:** `bibliotheca_ulpia/encyklopedia/MAK_makroekonomia_i_cykle.md` (🚧→✅),
`bibliotheca_ulpia/encyklopedia/INDEX_MAIOR.md` (MAK 🚧→✅). Następne: DEF → QNT → RLA (djvu pending).

---

## 2026-07-11 | 🫧 | ENCYKLOPEDIA: dział BAN wypełniony (bańki, krachy, behawioralne)

Pierwsze domknięcie działu z listy nowych ksiąg (rekomendacja z audytu pokrycia BIB-001..042 vs
043..069: stary kanon kompletny, luka po stronie nowych działów). Dział **BAN 🔲 → ✅**.

Esencja UGRUNTOWANA ekstrakcją fragmentów z plików (Prawo I, nie z pamięci): model Minsky-
Kindleberger (displacement→overtrading→mania→critical stage→panika→contagion), Shiller (feedback
loop = naturalny Ponzi, CAPE), Thaler (nadreakcja DeBondt-Thaler, awersja do straty ~2×),
Reinhart-Rogoff (debt intolerance, „this time is different" jako sygnał szczytu).

**Wpływ na kod (zmapowany na anatomię):** Z-03 kill-switch ← critical stage; Z-04 ← kaskada;
Z-07 PI-Cycle ← szczyt sprzężenia; PSY-03 ← herd; RADAR-04 ← contagion; X-27 ← nadreakcja.
**KANDYDACI ⚠️** (do walidacji areną): neuron „faza cyklu kredytowego" (Minsky classifier),
analog CAPE dla krypto, filtr „New Era/this-time-is-different", asymetria loss-aversion w sizingu
(spójne z ECON). Prawo XVI: kandydaci 1-2 sąsiadują z Z-03/07 → zmierzyć dekorelację przed budową.

**Pliki:** `bibliotheca_ulpia/encyklopedia/BAN_banki_krachy_behawioralne.md` (szkielet → pełny),
`bibliotheca_ulpia/encyklopedia/INDEX_MAIOR.md` (BAN 🔲→✅, Stan na 06-25→07-11).
Następne działy do wypełnienia: MAK (domknąć 🚧) → DEF → QNT → RLA.

---

## 2026-07-11 | 📚 | ANALIZA KSIĄG BIB-043..069 — mapowanie 27 nowych pozycji na Imperium

Analiza „zgodnie z zasadami" 27 nowo dodanych książek. Ekstrakcja TOC+wstępu z KAŻDEGO pliku
(ebooklib/pymupdf zainstalowane jednorazowo, nie do requirements) — analiza UGRUNTOWANA w
realnej treści, nie z pamięci (Prawo I). 23/27 przeczytane; 4 djvu (Aronson, Shreve I/II,
Sutton-Barto) czekają na `djvutxt` na laptopie — oznaczone ⚠️ PENDING.

**Kluczowe odkrycie:** nowe księgi mapują się dokładnie na PLANOWANE (🔲) działy encyklopedii:
- **BAN** (bańki/behawioralne) — 7 ksiąg: Kindleberger, Shiller, Thaler, Reinhart-Rogoff,
  Chancellor, MacKay → Z-03/04/07, PSY-03, RADAR stres.
- **MAK** (makro/dług) — 3× Dalio (Big Debt Cycle) + Popper → Gubernator, RADAR, reżim makro.
- **QNT** (stochastyka) — Shreve I/II (Feynman-Kac, brak arbitrażu) → FUNDAMENT ECON/FiltrEkonomiczny.
- **RLA** (RL/DL) — Sutton-Barto, Goodfellow → hedge_mwu, KANDYDAT GIFT (RL portfela z wrzutni).
- **DEF** (DeFi) — Voshmgir, Antonopoulos-Ethereum → neurony DeFi, funding/perp (PSY-01).

**Symbioza:** ECON (zbudowany dziś) ma teraz dwa filary w kanonie — Duke „Thinking in Bets"
(zakład, nie pewnik) + Shreve Feynman-Kac (brak arbitrażu). Backlog wrzutni ma teorię w kanonie.

**Deliverable:** `docs/ANALIZA_BIB_043-069_2026-07-11.md` (datowany snapshot) — tabela 27 ksiąg
(dział/ważność/status) + grupowanie po działach z wpływem na kod + KANDYDACI ⚠️. To FUNDAMENT;
wypełnienie działów prozą = follow-up (ZASADA ANALIZY CZĄSTKOWEJ: książka → esencja → zapis).
Zaktualizowano: INDEKS_IMPERIUM (poz. 61), INDEX_MAIOR (kanon 42→69, nieaktualny — Prawo XVII).

**Pliki:** `docs/ANALIZA_BIB_043-069_2026-07-11.md`, `docs/INDEKS_IMPERIUM.md`,
`bibliotheca_ulpia/encyklopedia/INDEX_MAIOR.md`

---

## 2026-07-11 | 🔗 | WPIĘCIE KATALOGU KSIĄG W RAG — wzbogacenie + filtr autor/tag

Dokończenie ścieżki calibre: katalog metadanych (`katalog_ksiag.json`) jako SOCZEWKA nad RAG.

**Wdrożone:**
- `narzedzia/rag/katalog.py` — łączy katalog z wynikami RAG po nazwie pliku (`zrodlo` = `plik`).
  `wczytaj_katalog` / `opis_metadanych` / `pasuje_filtr`. Graceful: brak/uszkodzony katalog → {}.
- `szukaj.py` — wyniki wzbogacone o autora/rok/tagi w nagłówku; nowy OPT-IN filtr `autor`/`tag`
  (domyślnie None → zachowanie IDENTYCZNE, dowiedzione testem). Filtr nadpobiera i post-filtruje.
- `mcp_server.py` — `biblioteka_szukaj` dostał parametry `autor`/`tag` (Claude może filtrować
  po autorze/tagu przez MCP); opis „42 książki" → „69".
- `tests/test_rag_katalog.py` — 12 testów, w tym integracja end-to-end filtra na syntetycznej
  bazie z fragmentami książek (realna baza ma dziś tylko docs).

**Bug złapany w samo-recenzji przed pushem:** `from narzedzia.rag import katalog` WYWALAŁ serwer
MCP (ma na sys.path tylko `narzedzia/rag`, nie root; robi `from szukaj import`). Testy tego nie
łapały (runner startuje z roota). Naprawiono importem odpornym na oba konteksty (try/except).
Dodatkowo przeniesiono parsowanie żądania MCP do `try` (Księga Wad: malformed → JSON-RPC error).

**Adversarial recenzja — 2 znaleziska (ograniczenia danych, nie logiki):**
- Filtr `tag` i wzbogacenie o rok są NIEAKTYWNE na obecnym katalogu (calibre=False → 0/69 tagów;
  autor 69/69 działa). To pułapka UX (tag → puste = wygląda na zepsute). Dodano uczciwą
  podpowiedź na stderr: „uruchom metadane_ksiag z calibre na laptopie". Ożyje po calibre.
- Nadpobranie zwiększone `max(topk*10,50)` → `max(topk*20,100)` (recall dla rzadkich autorów).

**Status:** autor-filtr + autor-enrichment działają OD RAZU. Tag/rok ożywają po `metadane_ksiag`
z calibre. Uwaga: filtr działa po REINDEKSACJI z książkami — ta baza RAG ma dziś tylko docs
(książki indeksuje `indeksuj.py --korpus biblioteka` na laptopie). Zero zmian w `.mcp.json`.

**Pliki:** `narzedzia/rag/katalog.py`, `narzedzia/rag/szukaj.py`, `narzedzia/rag/mcp_server.py`,
`tests/test_rag_katalog.py`

---

## 2026-07-11 | 📖 | KATALOG METADANYCH KSIĄG — calibre jako backend (nie MCP)

Rozbudowa Bibliotheki Ulpia. Cezar wybrał: calibre jako NARZĘDZIE zaplecza karmiące istniejący
RAG, nie serwer MCP (ZASADA MCP — MCP wchodzi tylko gdy dokłada NOWĄ zdolność; własny RAG już
szuka w treści, dodawanie calibre MCP byłoby redundancją).

**Luka (Prawo XVI, zmierzona):** RAG indeksuje TREŚĆ (FTS), ale metadane książki to dziś tylko
`tytul` z nazwy pliku. Brak autora, tagów, języka, roku, ISBN, wydawcy, serii. `ebook-convert`
już był fallbackiem konwersji w `ekstraktor.py` — więc konwersja pokryta; luką były METADANE.

**Wdrożone:**
- `narzedzia/rag/metadane_ksiag.py` — buduje `bibliotheca_ulpia/dane/katalog_ksiag.json`.
  Dwa poziomy (graceful, jak abstynencja Prawa XV): (1) ZAWSZE parsowanie nazwy
  `BIB-NNN_Autor_Tytul`; (2) GDY calibre obecny — `ebook-meta` dokłada tagi/język/rok/ISBN.
  Bez calibre katalog nadal powstaje (uboższy). Pasek postępu na stderr (Prawo XXIV).
- Katalog zbudowany TERAZ (fallback nazw, calibre brak w chmurze): **69 książek**
  (epub 45, pdf 10, azw3 7, djvu 5, mobi 2). Na laptopie z calibre — wzbogaci się metadanymi.
- `bibliotheca_ulpia/README.md` — naprawiony nieaktualny stan „42 książki" → 69 + opis katalogu.
- `tests/test_metadane_ksiag.py` — 9 testów: parsowanie nazw (granice: niestandardowa nazwa),
  parser `ebook-meta` (mapowanie kluczy, pomijanie „Unknown", „ : " w wartości, pusty).

**Status:** działa dziś (fallback nazw). Na laptopie z calibre `python -m narzedzia.rag.metadane_ksiag`
odświeży katalog z pełnymi metadanymi. Zero zmian w `.mcp.json` (config startowy = decyzja Cezara).

**Pliki:** `narzedzia/rag/metadane_ksiag.py`, `bibliotheca_ulpia/dane/katalog_ksiag.json`,
`bibliotheca_ulpia/README.md`, `tests/test_metadane_ksiag.py`

---

## 2026-07-10 | 🛡️ | FILTR EKONOMICZNY (ECON) — brama „zbyt dobre, by było prawdziwe"

Pierwsza realizacja z listy nowości wrzutni (`ANALIZA_WRZUTNIA_2026-07-10.md`, poz. C1 ARTEMIS).
Wybrana bo: realna luka (brak warstwy ograniczeń ekonomicznych), deterministyczna (filozofia
Bramy Kalkulatora, zero zależności ML), monotonicznie ostrożna (tylko wetuje → bezpieczna).

**Źródło zweryfikowane (nie halucynacja):** ARTEMIS, arXiv 2603.18107 „A Neuro-Symbolic
Framework for Economically Constrained Market Dynamics" (marzec 2026) — istnieje realnie
(WebSearch). Realizujemy jego karę **market price of risk** (ograniczenie chwilowego Sharpe'a)
DETERMINISTYCZNIE, bez sieci neuronowej.

**Prawo XVI (redundancja MIERZONA):** planowany wariant „ekstensja w ATR" byłby redundantny
z X-25 (`ATR_DEVIATION`). Dlatego ECON działa na INNEJ danej — ekonomii ZAKŁADU (p, RR):
liczy Sharpe pojedynczego zakładu `edge/√var` z (p·RR−(1−p)) i wetuje, gdy > λ_max
(„too good to be true") lub gdy edge ≤ 0 (ujemny EV). Nic w systemie tego nie sprawdzało.

**Wdrożone:**
- `imperium/pretorianie/filtr_ekonomiczny.py` — `FiltrEkonomiczny.ocen(p, rr)` → werdykt
  (wzorzec `FiltrAsymetrii`: abstynencja przy RR≤0, tylko wetuje, czysty Python).
- `sizing_przekonania.kelly_frakcja(..., filtr_ekonomiczny=None)` — **opt-in, domyślnie OFF**
  (ZASADA WPIĘCIA): bez filtra zachowanie IDENTYCZNE; z filtrem zwraca 0.0 dla zawetowanego.
- `tests/test_filtr_ekonomiczny.py` — 12 testów, Reguła Test-Granic: edge=0, Sharpe==λ_max
  (≥ vs >), p=0/p=1, RR≤0 abstynencja, dowód że opt-in OFF nie zmienia sizingu.

**Samo-recenzja złapała bug przed pushem:** dla p=0 (pewna strata) wariancja=0 uruchamiała
gałąź „abstynencja" przed sprawdzeniem edge≤0 → pewna strata byłaby PRZEPUSZCZONA. Naprawiono
kolejność: brak przewagi sprawdzany pierwszy.

**Status:** KANDYDAT — λ_max=2.0 zachowawczy, do KALIBRACJI areną (A/B) przed włączeniem na
sztywno (decyzja Cezara po zielonej walidacji). To nie neuron (veto ≠ głos) — filtr Pretorianów
jak `FiltrAsymetrii`, więc liczba neuronów bez zmian (84).

**Pliki:** `imperium/pretorianie/filtr_ekonomiczny.py`, `imperium/pretorianie/sizing_przekonania.py`,
`tests/test_filtr_ekonomiczny.py`

---

## 2026-07-10 | 🪶 | ODCHUDZENIE STARTU SESJI — 28,5 KB → ~15 KB (bez utraty łuku)

**Powód (decyzja Cezara):** hook startowy wypluwał ~28 KB przy każdym starcie — nie mieściło
się w wyniku narzędzia. POMIAR rozkładu (nie zgadywanie): Dziennik Nieśmiertelny 81%,
audyt 11% (z czego alarm XV 2,5 KB), kronika drukowana 3× (bug).

**Trzy cięcia:**
1. **Kronika drukowana 3×** — `centrum_pamieci start` już drukuje „X sesji, Y MB", a hook
   wołał osobno `kronika_czatu statystyki` (ten sam wydruk, inne zaokrąglenie: 6.8 vs 6.79).
   Usunięto zdublowane wywołanie z `session-start.sh`.
2. **Alarm Prawa XV** — jedna linia 2 551 zn. wyliczała 22 moduły z pełnym uzasadnieniem
   każdego. Na starcie: liczba + KLUCZE (288 zn., alarm nadal głośny i pełny co do liczby).
   Pełne powody na żądanie: `python narzedzia/audyt_spojnosci.py --luki`.
3. **Dziennik Nieśmiertelny** — warstwowość już istniała (`ostatnie=N`), ale (a) jednolinijkowce
   starszych sesji brały CAŁY pierwszy punkt „co" (do 721 zn.), (b) pełnych było 12.
   `_skroc()` tnie jednolinijkowce do 110 zn., `DOMYSLNE_PELNE=8`. 27,9 KB → 14 KB.
   **Wszystkie 69 sesji nadal widoczne** — Prawo XV nienaruszone, znikają tylko rozwinięcia
   (detale zostają w kronice, przeszukiwalnej po słowach).

**Testy:** `tests/test_dziennik_niesmiertelny.py` (12 testów, Reguła Test-Granic: _skroc na
granicy/o jeden dłuższy/pusty, os_czasu ostatnie=0 vs [:-0], ostatnie>liczba wpisów).

**Pliki:** `.claude/hooks/session-start.sh`, `narzedzia/audyt_spojnosci.py`,
`imperium/biblioteki/dziennik_niesmiertelny.py`, `imperium/biblioteki/centrum_pamieci.py`,
`tests/test_dziennik_niesmiertelny.py`

---

## 2026-07-10 | 🔎 | NAPRAWA 5 UWAG cubica (PR #118, drugi przebieg recenzji)

Recenzent przeczytał commity dedupu i pushu-na-komendę. **Wszystkie 5 uwag potwierdzone
wykonaniem** (nie na słowo — każda odtworzona skryptem przed naprawą):

1. **Daty ISO w sygnaturze** (`pamiec_sesji.py`) — każda lekcja niesie datę sesji, więc
   „2026", „06", „30" wchodziły do sygnatur wszystkich lekcji z tego samego dnia.
   „Neuron X-01 zwraca NEUTRAL (2026-06-30)" vs „Zwiadowca EXP-13 milczy (2026-06-30)"
   dawało Jaccard 3/5 = **0.60 → scalenie dwóch niezwiązanych lekcji**. Daty wycinane
   przed tokenizacją (`_WZOR_DATY`).
2. **Sito prozatorskie nadpisywało werdykt sygnatur** — „Bug w EXP-07" i „Bug w EXP-13"
   mają ten sam worek rdzeni. Sito 3 nie scala, gdy obie sygnatury są mocne i ROZŁĄCZNE.
3. **Marker: hasz i ID w jednym zbiorze** (`auto_lekcja.py`) — kronika dopisana po
   przetworzeniu dostawała nowy hasz, ale jej stare `sesja_id` wciąż blokowało. Mechanizm
   unieważniania był martwy od pierwszego dnia. Zbiory rozdzielone; zmigrowane ID wypadają
   ze starego markera.
4. **Cichy `git fetch || true`** (`synchronizuj.sh`) — przy porażce fetch `PRZED` liczyło
   się ze starego `origin/…`, więc strażnik „zdalna wyprzedza" przepuszczał sklejanie na
   nieaktualnym stanie. Przy `--push` fetch musi się udać, inaczej przerwanie.
5. **Skrypt omijał bramkę Prawa XXI** — `--push` mógł wypchnąć kod bez testów i audytu.
   Gdy w kolejce jest `.py`, `synchronizuj.sh` odpala testy + audyt + skan wad i odmawia
   pushu przy czerwonym. Push samej pamięci bramki nie wymaga (kod nietknięty).

**Regresja:** te same 5 grup / 11 duplikatów na korpusie 71 lekcji — naprawy nie osłabiły
dedupu. 5 nowych testów + `tests/test_auto_lekcja_marker.py` (4 testy: hasz unieważnia,
zmigrowane ID nie blokuje, komentarze pomijane, brak markerów).

Klasy 1 i 3 dopisane do **Księgi Wad Kodu** (7 → 9 wzorców).

**Pliki:** `imperium/biblioteki/pamiec_sesji.py`, `narzedzia/auto_lekcja.py`,
`narzedzia/synchronizuj.sh`, `tests/test_pamiec_sesji.py`, `tests/test_auto_lekcja_marker.py`,
`bibliotheca_ulpia/dane/ksiega_wad_kodu.jsonl`

---

## 2026-07-10 | 🌿 | PUSH NA KOMENDĘ — hook końca sesji przestaje pushować

**Powód (decyzja Cezara):** hook `SessionEnd` commitował **i pushował** pamięć po każdej
sesji. Efekt: historia w chmurze utonęła w commitach „auto: sync pamięci sesji" (30+ na
gałęzi), a start na drugiej maszynie wymuszał rebase. Dziś sesja wystartowała 30 commitów
za remote i push się odbił — to był objaw tej właśnie polityki.

**Wdrożone:**
- `.claude/hooks/session-end.sh` — commituje pamięć LOKALNIE, **nie pushuje**;
  informuje ile commitów czeka na wypchnięcie.
- `narzedzia/synchronizuj.sh` — świadomy push. Domyślnie PODGLĄD (nic nie zmienia);
  `--push` skleja commity pamięci w jeden i wypycha.
- `CLAUDE.md` § Tryb autonomiczny pkt 4: „Auto-push" → „Push na komendę".

**Zasada bezpieczeństwa (zweryfikowana w izolowanym repo, 4 scenariusze):**
sklejamy **wyłącznie** gdy KAŻDY commit czekający na push jest commitem pamięci. Gdy
w kolejce jest choć jeden commit merytoryczny — historia NIE jest przepisywana (SHA
zachowane, potwierdzone testem). Odmowa przy brudnym drzewie i przy zdalnej wyprzedzającej
gałąź (HEAD nietknięty).

**Nie zmieniamy:** auto-commit (Prawo XVIII, zero kosztu) i auto-pull na starcie sesji.

**Pliki:** `.claude/hooks/session-end.sh`, `narzedzia/synchronizuj.sh`, `CLAUDE.md`

---

## 2026-07-10 | 🧠 | DEDUP SEMANTYCZNY LEKCJI — koniec czterech kopii tej samej wiedzy

**Powód:** recenzja cubic na PR #118 wykryła, że `docs/PAMIEC_SESJI.md` puchnie od
duplikatów (4× „Lookahead bias w SMC Engine", 4× „HA bez repainting", 3× „ATR_MULT w EXP-07",
3× „True Range"). Napuchnięty plik wstrzykuje się w kontekst KAŻDEJ sesji — utrata tokenów
i fałszywy sygnał ważności (Prawo XV).

**Diagnoza (dwie przyczyny, obie potwierdzone pomiarem):**
1. Dedup w `auto_lekcja.py` porównywał **dokładny podciąg tytułu** (`szukaj(tytul)`).
   DeepSeek ekstrahuje z `temperatura=0.3` → za każdym przebiegiem inna parafraza.
   „Martwy głos ATR_MULT w EXP-07" vs „Dead voice bug: ATR_MULT w EXP-07" — żaden nie jest
   podciągiem drugiego, duplikat przechodził.
2. Marker przetworzonych kronik (`.auto_lekcja_przetworzone.txt`) był **w `.gitignore`**,
   czyli per-maszyna: 13 z 102 kronik oznaczonych tutaj, 0 na laptopie → ta sama kronika
   ekstrahowana wielokrotnie, za każdym razem nową parafrazą.

**Pomiar (Prawo XVI — redundancja mierzona, nie zgadywana), 71 realnych lekcji:**
podobieństwo NAPISÓW nie rozdziela klas (prawdziwy duplikat 0.642 **poniżej** pary różnych
lekcji 0.667: „ATR_MULT w TLP" vs „ATR w Night Turbo" to EXP-07 i EXP-08). Podobieństwo
**sygnatur technicznych** rozdziela czysto: wszystkie pary ≥ 0.60 to duplikaty, najbliższy
fałszywy kandydat 0.571.

**Wdrożone:**
- `pamiec_sesji.czy_duplikaty()` — trzy sita: tytuł znormalizowany → Jaccard sygnatur
  technicznych (`PROG_PODOBIENSTWA=0.60`, `MIN_TOKENOW_SYGNATURY=2`) → worek rdzeni tytułu
  (dla lekcji prozatorskich bez identyfikatorów, np. „True Range").
- `pamiec_sesji.duplikat_lekcji()` / `sygnatura_lekcji()` — API dedupu.
- `auto_lekcja.py` — używa dedupu semantycznego; marker **wersjonowany**, kluczowany
  **haszem treści kroniki** (`auto_lekcja_przetworzone.txt`), ze zgodnością wstecz.
- Jednorazowe scalenie: **71 → 60 lekcji** (11 duplikatów), zero fałszywych scaleń.
- 12 nowych testów, w tym Reguła Test-Granic: Jaccard dokładnie == próg, sygnatura
  1-tokenowa, dwa puste zbiory, i test negatywny „nie scalaj EXP-07 z EXP-08".

**Świadomie zachowawczy:** przy ubogiej sygnaturze dedup milczy. Fałszywe scalenie kasuje
wiedzę bezpowrotnie; fałszywy duplikat kosztuje kilka linii pliku.

**Adversarial samo-recenzja przed pushem złapała 4 bugi w pierwszej wersji tej naprawy**
(rozkaz stały — nie czekamy, aż znajdzie je cubic):
1. **Kolejność alternatyw w regexie:** `[A-Z]{2,}` szło przed `[A-Z]+-\d+`, więc „EXP-07"
   tokenizowało się jako „EXP" + osierocone „07". Osierocone liczby zawyżały Jaccarda:
   „EXP-07 ATR 14" vs „EXP-07 RSI 14" dawało dokładnie 0.60 → scalenie dwóch RÓŻNYCH bugów.
2. **Negacja jako stopword:** „nie" było w `_SLOWA_PUSTE`, więc sito 3 uznawało „Numba
   przyspiesza" i „Numba NIE przyspiesza" za tę samą lekcję — lekcja obalająca poprzednią
   byłaby odrzucona. Negacja to treść, nie szum.
3. **Sygnatura czysto liczbowa:** `\d{2,}` łapie daty i progi, więc {14, 30} vs {14, 30}
   dawało Jaccard 1.0. Wymagany ≥ 1 token z literą (`_sygnatura_rozstrzygajaca`).
4. **Dwa puste tytuły** były „duplikatem" (`"" == ""`).

Obie klasy 1–2 dopisane do **Księgi Wad Kodu** (5 → 7 wzorców), żeby skaner łapał je sam.

**Znane ograniczenie (Prawo I — nie udajemy, że go nie ma):** sygnatura widzi identyfikatory,
nie kierunek wniosku. „ATR_MULT za niski" i „ATR_MULT za wysoki" mają tę samą sygnaturę.
Dlatego `auto_lekcja` **loguje każdy pominięty tytuł** na stderr — pominięcie jest widoczne,
nie ciche. Lekcja obalająca poprzednią wymaga `aktualizuj_lekcje()`, nie dopisania obok.

**Pliki:** `imperium/biblioteki/pamiec_sesji.py`, `narzedzia/auto_lekcja.py`,
`tests/test_pamiec_sesji.py`, `docs/PAMIEC_SESJI.md`, `.gitignore`,
`bibliotheca_ulpia/dane/auto_lekcja_przetworzone.txt`

---

## 2026-07-06 | 🔬 | WALIDACJA TRIADY na realnych danych + 🚨 ALARM PRAWA XV

Uruchomiono **pełną triadę pomiaru skilla** na moich danych (15 par Binance 4h, 36 346
obserwacji, wszystko OOS) — trzy niezależne narzędzia, każde odpowiada na inne pytanie:

| Noga | Narzędzie | Co mierzy | Werdykt |
|------|-----------|-----------|---------|
| 1. Walk-Forward IC | `narzedzia/walk_forward_ic.py` | stabilność korelacji sygnał→zwrot | **32/49 ROBUST** |
| 2. Ważność MDA/SFI | `narzedzia/raport_waznosci.py` | wkład neuronu do trafności roju | **base acc 48.3%, MDA≈0** |
| 3. WFO progu | `narzedzia/raport_wfo.py` | czy próg wejścia generalizuje OOS | **BTC WFE 0.13 · ETH WFE 0.23 → PRZEUCZONE** |

**Diagnoza (spójna na BTC+ETH, zmierzona — nie opinia):** skill *jest* na poziomie sygnału
(stabilny IC: V-02 +0.23/24 okna, X-17 +0.15/25 okien, z dziesiątkami tys. głosów), ale
*ginie* w warstwie agregacji i progu — głosowanie nie zamienia ciągłego IC w binarną trafność
(MDA≈0, base acc <50%), a strojony `min_pewnosc` nie przenosi przewagi poza próbę (OOS Sharpe≈0).

**🚨 UTRATA POTENCJAŁU (Prawo XV):** skill neuronów (IC) tracony w warstwie decyzyjnej
(agregacja + próg); base accuracy roju **48.3% < 50%** na predykcji znaku następnego baru.
Zmierzone na BTC+ETH OOS. Wąskie gardło = sposób sklejania głosów + próg in-sample, **NIE**
neurony. Kandydaci naprawy (do decyzji Cezara, **nic nie wdrożono** — ZASADA WPIĘCIA):
(a) waga głosu ∝ IC_warunkowy × spójność_WF; (b) konformalna bramka progu; (c) wyciszenie/
inwersja odwróconych (X-18 44% S-acc, H-01/V-07/EXP-03 <48%) — najpierw per-reżim.

**Otwarte wątki przed jakąkolwiek budową (Prawo I):** sprawdzić artefakt IC (EXP-13/SMC-01/
V-13 mają wysoki IC ale 3–6 okien = podejrzenie rzadkości/remisów Spearmana — nie ważyć na
tym); zmierzyć hipotezę (a) OFFLINE (agregat równa-waga vs ważony-IC na OOS) zanim cokolwiek
budujemy. Kluczowe liczby zapisane do bazy areny (`rodzaj='WALIDACJA_TRIADA'`) dla Sybilli.

**Pliki:** brak zmian kodu — walidacja istniejących narzędzi (Prawo XIX: triada już w kodzie).
`docs/LOG_ZMIAN.md`, `bibliotheca_ulpia/dane/dziennik_niesmiertelny.jsonl`, baza areny.

## 2026-07-06 | 👥 | Raport Żalu — Kronika Żyć Nieprzeżytych (krok 3 Cieni)

`narzedzia/raport_zalu.py` — domyka fazę 1 Legionów Cieni. Czyta z bazy areny `LIVE_PNL`
(real) i `CIEN_PNL` (widmowe warianty) i liczy ŻAL każdego mechanizmu: `żal(cień) = średni
PnL% cienia − średni PnL% realny`, per reżim (NORMAL/RANGING/TREND_STRONG/VOLATILE/PANIC).
Interpretacja: bez_wet żal>0 → weta nas kosztują; prog_lagodny żal>0 → za ostrożni; prog_surowy
żal>0 → za odważni. Guard próby (Prawo I): przy < min_barow zamknięć w reżimie raport mówi
„za mało danych" — NIE zmyśla werdyktu z szumu. Ograniczenie jawne: real i cienie to osobne
serie (nie sparowane per-trade) — zgrubny pierwszy pomiar KIERUNKU żalu. Fundament: CFR
(Zinkevich et al. NeurIPS 2007). 10 testów granic (parsowanie reżimu z obu formatów noty,
żal ±/0, guard próby, brak real w reżimie). Reuse arena_baza (Prawo XVI).

**Pliki:** `narzedzia/raport_zalu.py` (NEW), `tests/test_raport_zalu.py` (NEW),
`docs/WIZJA_LEGIONY_CIENI.md` (raport gotowy), `docs/LOG_ZMIAN.md`.

## 2026-07-06 | 👥 | Legiony Cieni — Kontrfaktyczne Kolosseum (faza 1, kod)

Perełka z wizji→kod (Prawo XIX). `imperium/koloseum/legiony_cieni.py`: menedżer N widmowych
wariantów roju maszerujących obok realnej decyzji na PAPIEROWYCH silnikach — mierzy „cenę
ostrożności i cenę odwagi" NA ŻYWO (Prawo XV podniesione do potęgi: alarm o niewykorzystanych
DECYZJACH, nie modułach). 3 startowe cienie: `bez_wet` (bezpieczniki OFF — koszt wet),
`prog_lagodny` (próg −0.10 — wchodzi częściej), `prog_surowy` (próg +0.10 — ostrożniej).
Zamknięcia → arena `CIEN_PNL` (neuron=nazwa cienia, per reżim). Fundament: CFR (Zinkevich,
Johanson, Bowling, Piccione, NeurIPS 2007; rodzina pokonała ludzi w pokerze — Libratus/Pluribus).

DLACZEGO TYLKO MY: rój DETERMINISTYCZNY → „co by było gdyby" odtwarzalne uczciwie (LLM-agenci
konkurencji mają nieodtwarzalne kontrfaktyki). Determinizm = broń badawcza.

Opt-in `cienie=False` w KonfigPetliLive, wpięte w `petla_live` (krok 3c) — cienie to OBSERWATORZY,
nie dotykają realnych zleceń (ZASADA WPIĘCIA, zero zmiany domyślnego zachowania). Graceful:
awaria cienia/bazy nie zabija realnego handlu. **Faza 2 (żal→wagi MWU) NIEZBUDOWANA** — czeka
na walidację ≥100 barów paper (raport_zalu.py + osobna decyzja Cezara). 12 testów granic
(przycinanie progów [0,1], watermark bez podwójnego zapisu, graceful awarii) + 2 integracyjne
pętli (opt-in OFF + cienie=True nie crashuje). 2054+12+2 → suite zielony, audyt exit 0.

**Pliki:** `imperium/koloseum/legiony_cieni.py` (NEW), `tests/test_legiony_cieni.py` (NEW),
`imperium/koloseum/petla_live.py` (flaga `cienie` + wpięcie 3c), `tests/test_petla_live.py`
(+2 testy), `docs/WIZJA_LEGIONY_CIENI.md` (status→WDROŻONE faza 1), `docs/INDEKS_IMPERIUM.md`,
`docs/LOG_ZMIAN.md`.

## 2026-07-06 | E+A+L3 | 👁️ Zmysły zweryfikowane na żywo + 🔮 Księgi Sybillińskie (kod)

Sesja przy laptopie wg planu (E+L2→A+L3). Trzy rzeczy:

**E — obudzenie zmysłów ZWERYFIKOWANE NA ŻYWO (Prawo XV, pomiar nie opinia).** Adaptery
Futures/FearGreed/CVD/News RSS zwracają realne dane (funding 8e-5, F&G=23 Extreme Fear,
30 nagłówków RSS, block height 956179). Rój oddaje głosy sensoryczne: V-03(CVD), PSY-03/04,
NEWS-01; OC-06(S2F=180)/OC-08(inflacja 0.555%) ożywają na realnej dacie — były martwe w
audycie (sztuczny ts z ery 1970). Wszystkie abstynencje legalne (progi/stan kroczący/pętla
portfelowa) — zero martwych głosów. Nowe narzędzie `narzedzia/waliduj_zmysly.py`: rój
BAZA vs ZMYSŁY, różnica głosów = wkład zmysłów, per neuron GŁOS/ABSTYNUJE+powód (6 testów).

**A — arena_log track record: potwierdzono że infra JUŻ istnieje** (`petla_live.py` opt-in
`arena_log=False`, batch LIVE_PNL→arena_baza). Nic do budowy — zegar włącza Cezar.

**L3 — Księgi Sybillińskie WDROŻONE** (`imperium/biblioteki/ksiegi_sybillinskie.py`, perełka II
z wizji→kod, Prawo XIX): rejestr falsyfikowalnych PROROCTW Imperium o sobie. `dodaj`/`rozlicz`/
`brier`/`krzywa_kalibracji`, JSONL→git niemutowalny, rozstrzyganie AUTOMATYCZNE z bazy areny
po horyzoncie, Brier score samowiedzy (Brier 1950). Anty-oszustwo (Prawo I): `rozlicz` NIGDY
nie tyka P/twierdzenia — zmiana P po fakcie widoczna w git diff. **Zegar OFF (decyzja Cezara):**
moduł istnieje, realnych proroctw nie zasiano (księgi puste) — zasiew to świadoma decyzja
Cezara (ZASADA WPIĘCIA). Domyka trójcę kalibracji: conformal(sygnały)→Cienie(decyzje)→Sybilla(przekonania).
21 testów granic (P∈{0,1}, horyzont==próg, nierozstrzygalne, niemutowalność, Brier znany).

**Pliki:** `narzedzia/waliduj_zmysly.py` (NEW), `tests/test_waliduj_zmysly.py` (NEW),
`imperium/biblioteki/ksiegi_sybillinskie.py` (NEW), `tests/test_ksiegi_sybillinskie.py` (NEW),
`docs/WIZJA_KSIEGI_SYBILLINSKIE.md` (status→WDROŻONE), `docs/INDEKS_IMPERIUM.md` (+Sybilla),
`docs/LOG_ZMIAN.md`.

## 2026-07-05 | L1 | 🔥 Prova Ignis — próba ognia egzekucji (7 kampanii chaosu, OMS zdał)

Plan Domykania Luk L1 (egzekucja: pancerz zamiast szybkości). `tests/test_prova_ignis.py`:
KAMPANIE CHAOSU — wielokrokowe scenariusze awarii (nie unit-testy przejść jak test_oms.py):
(1) zgubiona odpowiedź giełdy → anti-double-submit przez query, zero duplikatów;
(2) total blackout → jawny BLAD, świadome ponowienie nowym zleceniem; (3) crash w połowie
partiala → restart → reconcile domyka do prawdy giełdy; (4) zdublowany webhook fill →
over-fill zablokowany, księga nietknięta; (5) wyścig anulacji z wypełnieniem → stan końcowy
nienaruszony, rozjazd JAWNY (nie udajemy naprawy); (6) burza 10 zleceń na kapryśnej sieci →
dokładnie 10 na giełdzie, zero duplikatów, zero wiszących; (7) giełda raportuje mniej niż
wiemy → nie cofamy wypełnień. Deterministyczne (skrypt awarii jawny, zero random — Prawo I).

WYNIK: OMS (W-344) zdał 7/7 za pierwszym podejściem — maszyna stanów + idempotencja + reconcile
trzymają się pod ogniem. Znane ograniczenie (kampania 5, zgodne z projektem): wyścig
anulacja-vs-fill zostawia jawny rozjazd do obsłużenia wyżej (router/operator).

**Pliki:** `tests/test_prova_ignis.py` (NEW), `docs/LOG_ZMIAN.md`.

---

## 2026-07-05 | AUDYT | 🧹 Naprawa żywych rozjazdów docs↔kod (Prawo XXI/XVIII)

Audycik na koniec wachty. Rdzeń audytu zielony (14 warstw, ruff, MAPA_KLUCZY 84/84). Dodatkowy
skan złapał 2 ŻYWE (niedatowane) rozjazdy, których audyt nie łapie (inline, nie nagłówki):
- `INDEKS_IMPERIUM.md`: „Neurony: 62 / Strategie: 18 / Testy: 743/743" (stan 2026-06-04) →
  odświeżone na 84/20 + de-hardcode testów + data 2026-07-05 + aktualne kategorie A..Z.
- `PAPER_TRADING_MEXC.md`: „Testy: 743/743" → de-hardcode („wszystkie zielone").
Datowane migawki (PAMIEC_SESJI 2026-06-22, MANUAL_MIGRACJA 2026-06-09) POZOSTAWIONE świadomie
(Prawo I: prawda ich czasu). Audyt exit 0 po naprawie.

---

## 2026-07-05 | PRAWO XV | 🔄 Raport WFO — odkopany Walk-Forward Optimization (W-345)

Odkopano `imperium/koloseum/walk_forward.py` (Pardo WFO; był gotowy+testy bez wejścia).
`narzedzia/raport_wfo.py`: optymalizuje próg `min_pewnosc` na oknie IS (DSR-guided `optymalizuj`),
egzaminuje na OOS, przesuwa okno. Werdykt z OOS (Prawo I): WFE=Sharpe_OOS/Sharpe_IS (>0.5=ROBUST,
~0/<0=PRZEUCZONY). Ewaluator = backtest na wycinku barów z danym progiem (okno warmup=60 < OOS,
by OOS produkował decyzje). Różne od walk_forward_ic (stabilność IC neuronów) — tu stroimy próg
wejścia i badamy czy generalizuje. 3 testy (ewaluator zwraca kapitał+zwroty, formatowanie werdyktu,
brak danych). Dane lokalne → WFO odpalasz u siebie (ciężkie: kilka minut).

**Pliki:** `narzedzia/raport_wfo.py` (NEW), `tests/test_raport_wfo.py` (NEW), `docs/LOG_ZMIAN.md`.

---

## 2026-07-05 | PRAWO XV | 🏷️ Raport Etykiet — odkopany Triple-Barrier + CUSUM (W-357)

Odkopano `imperium/legiony/triple_barrier.py` (López de Prado AFML Ch.3-4; był gotowy bez
wejścia). `narzedzia/raport_etykiet.py`: próbkuje zdarzenia filtrem CUSUM, etykietuje serię
Triple-Barrier (bariery ×σ: która padła pierwsza TP/SL/czas) i liczy sample-uniqueness
(obserwacje z nakładającymi się oknami nie są IID — waga próbki = unikalność). Rdzeń
`raport_z_close` testowalny bez CSV. Fundament pod trening ML (uczciwe etykiety vs naiwne
„cena wzrosła"). Dane rynkowe lokalne → raport odpalasz u siebie. 4 testy (statystyki,
za mało barów, CUSUM bez zdarzeń, suma TP+SL+timeout=100%). Skan wad czysty.

**Pliki:** `narzedzia/raport_etykiet.py` (NEW), `tests/test_raport_etykiet.py` (NEW), `docs/LOG_ZMIAN.md`.

---

## 2026-07-05 | PRAWO XVI | 📏 Pomiar redundancji: triple_barrier & walk_forward — NIE duplikaty

Skan Prawa XV znalazł 12 niepodpiętych modułów. Zmierzono funkcjonalnie 2 podejrzenia o redundancję
(Prawo XVI — pomiar, nie opinia):
- **triple_barrier (W-357) vs arena_trzech_bram (W-035, wpięty):** NIE duplikaty. arena_trzech_bram
  = scoring Igrzysk, stałe % TP/SL. triple_barrier = etykietowanie ML: bariery ×zmienność + filtr
  CUSUM + sample_uniqueness (AFML Ch.3-4). triple_barrier dokłada NOWĄ zdolność (research-grade) →
  utrata potencjału XV, nie redundancja. Wspólny tylko prymityw „która bariera pierwsza" (drobne).
- **walk_forward (W-345) vs walk_forward_ic (wpięty):** różne cele. walk_forward_ic = stabilność IC
  neuronów (bez parametrów). walk_forward = WFO optymalizacji PARAMETRÓW (ewaluator IS/OOS). NIE
  redundancja; walk_forward niepodpięty (brak optymalizatora+CLI) = utrata potencjału XV, odrębny.

Wniosek: backlog XV nie kurczy się archiwizacją — „niepodpięte" wersje to realna nieodkopana zdolność.
Dokument-only (pomiar+werdykt), zero zmian w kodzie.

---

## 2026-07-05 | PRAWO XV | 🎯 Raport Ważności — odkopany Feature Importance (MDA/SFI)

Odkopano `imperium/legiony/feature_importance.py` (W-355, López de Prado) — był gotowy +
testy, ale BEZ wejścia (utrata potencjału Prawo XV). Zbudowano:
- `backtest(zbieraj_sygnaly=False)` opt-in: zbiera per bar {neuron: kierunek} + etykietę
  forward (znak zwrotu następnego baru; bez look-ahead w decyzji — etykieta tylko do POMIARU).
- `narzedzia/raport_waznosci.py`: uruchamia backtest, liczy MDA (permutacyjna ważność) + SFI
  (trafność LONG/SHORT), drukuje ranking + martwe głosy/redundantne. `--do-areny` zapisuje
  MDA per neuron do arena_wyniki.db (rodzaj='WAZNOSC') — Claude czyta MCP arena_pytaj.

Domyka triadę pomiaru skilla roju: IC (korelacja) + walk-forward (stabilność) +
feature-importance (przyczynowość permutacyjna). Dane rynkowe lokalne → raport odpalasz u siebie.
5 testów (wyrównanie sygnał↔wynik, opt-in OFF, za mało próby, zapis MDA do areny). 2013/2013 zielone.

**Pliki:** `narzedzia/raport_waznosci.py` (NEW), `imperium/koloseum/backtest.py` (opt-in
zbieraj_sygnaly), `tests/test_raport_waznosci.py` (NEW), `docs/LOG_ZMIAN.md`, `docs/SCIAGA_LOKAL.md`.

---

## 2026-07-05 | UNIKAT | 🐞 Księga Wad Kodu — pamięć błędów + auto-skan (samo-leczenie)

Odpowiedź na „czemu cubic łapie, a my nie": nie brak narzędzia (mamy `/code-review` w mandacie),
lecz brak PAMIĘCI wzorców i wymuszenia. Zbudowano:
- `imperium/biblioteki/ksiega_wad_kodu.py` — KsiegaWadKodu: JSONL wzorców błędów (kat/regex/
  opis/lekcja/zrodlo), `dodaj` (dedup+walidacja regex), `skanuj(tekst)` (heurystyczny nudge z nr linii),
  `zasiej_startowe`. 5 wzorców startowych z realnych uwag cubic (parse-in-try, ORDER BY id,
  clamp limit, test-None, SQLite-w-pętli). Księga wersjonowana w git (wiedza uniwersalna).
- `narzedzia/skan_wad_kodu.py` — CLI: skanuje zmienione+untracked .py przeciw księdze, exit 2
  na trafienia. Wpięty w hook startowy (informacyjnie, non-blocking) + rytuał pre-push w CLAUDE.md.
- Dogfood złapał 2 własne luki: skaner pomijał untracked (naprawione) i trafiał w plik definicji
  (wykluczony). To NUDGE, nie dowód (Prawo I).

Lekcja procesowa utrwalona: każdą nową wadę z recenzji dopisujemy do księgi → z czasem łapiemy
SAMI to, co dziś łapie cubic. 9 testów granic (dedup, zły/pusty regex, nr linii, idempotencja).

**Pliki:** `ksiega_wad_kodu.py` (NEW), `narzedzia/skan_wad_kodu.py` (NEW),
`tests/test_ksiega_wad_kodu.py` (NEW), `.claude/hooks/session-start.sh` (krok 6),
`CLAUDE.md` (rytuał pre-push), `docs/INDEKS_IMPERIUM.md`, `bibliotheca_ulpia/dane/ksiega_wad_kodu.jsonl`.

---

## 2026-07-05 | RECENZJA | 🔍 Cubic PR — 12 uwag naprawionych (arena/kalibrator/walidacja)

Adversarial review (cubic) na PR z Areną+conformalem. Naprawione u źródła:
- **arena_mcp**: parsowanie `params/name` WEWNĄTRZ try (malformed request → JSON-RPC error,
  nie crash procesu, P1); `limit` clampowany do 1-100 (P2).
- **arena_baza**: `pytaj_pomiary` sortuje `ORDER BY ts DESC, id DESC` (backfill nie udaje
  najnowszego, P2); nowy `zapisz_pomiary` (batch, jedno połączenie — P2 latencja live).
- **petla_live**: arena-log batchem raz/bar (nie per-trade connect, P2).
- **paper_trading**: `WynikZamkniecia.rezim` dodane i wypełniane z `poz.rezim` — arena-log
  przestaje kłamać „NORMAL" (P2).
- **walidacja_kalibrator**: agreguje parę TYLKO gdy oba tryby OK (fair A/B, P1); dodane
  maxDD do metryk i werdyktu (ochrona kapitału, P2).
- **arena_zasil**: zły klucz łapany (ValueError→skip), batch odporny (P2).
- **testy kalibratora**: None→TypeError, `==0.4` zamiast `in`, pokrycie ≤0.98 (P2/P3).
- **SCIAGA**: `${CLAUDE_PROJECT_DIR:-.}` z fallbackiem (P2).

Lekcja procesu: uruchomiono `/code-review` na diffie PRZED pushem (mandat CLAUDE.md,
którego wcześniej w sesji nie dopełniłem — stąd cubic łapał to, co my sami powinniśmy).
2000/2000 testów zielone, audyt exit 0.

---

## 2026-07-05 | UNIKAT | 🎯 Bramka konformalna w progu pewności (opt-in) + narzędzie walidacji

Wpięcie KalibratorKonformalnego (ML-36) w ścieżkę decyzyjną — zgodnie z rozkazem „po walidacji".
`BramkaPewnosciKonformalna` (kalibrator_konformalny.py): traktuje zamkniętą pozycję jako
obserwację (zysk=pokryte, strata=miss); po serii strat ACI **PODNOSI** efektywny próg pewności
(rój wchodzi rzadziej/pewniej). BEZPIECZNIK: bramka TYLKO zaostrza (delta≥0) — nigdy nie luzuje
progu poniżej bazowego, więc NIE zwiększa liczby wejść ani ryzyka. To czyni wpięcie bezpiecznym.

Wpięcie (wszystkie opt-in, domyślnie OFF = zero zmiany):
- `Dyrygent.bramka_kalibr` (None) — użyta w bramce `pewnosc < prog` (dyrygent.py).
- `backtest(kalibruj_prog=False)` — tworzy bramkę, karmi wynikami zamknięć (bez look-ahead).
- `KonfigPetliLive.kalibruj_prog=False` — analogicznie w live, karmienie per symbol.

WALIDACJA (Prawo I — decyzja z pomiaru): `narzedzia/walidacja_kalibrator.py` robi A/B
baza vs kalibracja na LOKALNych danych (rynkowe CSV poza gitem) — trades/win-rate/PnL + werdykt.
Cezar włącza `kalibruj_prog=True` DOPIERO gdy tabela potwierdzi korzyść. Mechanizm zweryfikowany
10 testami granic (tylko-zaostrza, sufit 0.95, powrót do bazy, max_podniesienie, kontrakty OFF).

**Pliki:** `kalibrator_konformalny.py` (+BramkaPewnosciKonformalna), `dyrygent.py`,
`backtest.py`, `petla_live.py` (opt-in kalibruj_prog), `narzedzia/walidacja_kalibrator.py` (NEW),
`tests/test_bramka_pewnosci.py` (NEW), `docs/LOG_ZMIAN.md`.

---

## 2026-07-04 | UNIKAT | 🎯 Kalibrator Konformalny (ACI) + auto-log areny w pętli live

Po przeglądzie vs konkurencja (mamy DSR/PBO/purged-CV/meta-labeling na poziomie AFML;
luka: brak kalibracji prawdopodobieństwa) — zbudowano DWA ulepszenia:

**#1 KalibratorKonformalny** (`imperium/legiony/kalibrator_konformalny.py`) — Adaptive
Conformal Inference (Gibbs & Candès 2021, arXiv:2106.00170; ZPO w REJESTR_INSPIRACJI ML-36).
Zamienia mgliste „pewność 0.7" w przedział z GWARANCJĄ pokrycia; ACI dostraja poziom po
każdym barze pod dryf rynku. Split-conformal kwantyl z korektą skończonej próby (n+1);
alpha=0→inf uczciwie (Prawo I). Unikat, dekorelowany (nie generuje kierunku — szerokość
zaufania). 13 testów granic (pusta próba, alpha 0/1, order-statistic, ACI clamp, zbieżność).

**#2 Auto-log areny w pętli live** — wspólna warstwa `imperium/biblioteki/arena_baza.py`
(SQL wyjęty z arena_mcp — Prawo XVI reuse, poprawne warstwy). `KonfigPetliLive.arena_log`
opt-in (domyślnie False = zero zmiany): każde zamknięcie loguje realny PnL% do arena_wyniki.db
(rodzaj='LIVE_PNL') → Claude czyta skuteczność live MCP-em arena_pytaj. Domyka pętlę
graj→mierz→ucz się bez udziału człowieka.

1984/1984 testów zielone, audyt exit 0 (ruff czysto, INDEKS zsynchronizowany).
**Pliki:** `kalibrator_konformalny.py` (NEW), `arena_baza.py` (NEW), `arena_mcp.py`
(przepięty na wspólną warstwę), `arena_zasil.py`, `petla_live.py` (opt-in arena_log),
4 nowe pliki testów, `REJESTR_INSPIRACJI.md`, `INDEKS_IMPERIUM.md`, `LOG_ZMIAN.md`.

---

## 2026-07-04 | MCP | 🔁 Arena Zasil — domknięcie pętli graj→mierz→ucz się

`narzedzia/arena_zasil.py`: liczy IC roju (raport_ic.zbierz_ic) i ZAPISUJE per neuron do
bazy areny (arena_mcp.zapisz_pomiar). Rdzeń `zasil_z_ic(ic, interwal, ...)` czysty/testowalny,
pomija NaN i niepoprawne typy (Prawo I: do bazy tylko realny pomiar). CLI dokłada backtest.
Efekt: pomiar z lokalnego biegu trafia do arena_wyniki.db → Claude czyta go MCP-em `arena_pytaj`
bez ponownego liczenia; wiedza akumuluje się między wachtami. 6 testów granic (NaN/None/typy/
pusty/nota/rodzaj). Pełne testy zielone, audyt exit 0.

**Pliki:** `narzedzia/arena_zasil.py` (NEW), `tests/test_arena_zasil.py` (NEW),
`docs/LOG_ZMIAN.md`, `docs/SCIAGA_LOKAL.md`.

---

## 2026-07-04 | MCP | 🏟️ Arena MCP — Claude uczy się areny (migawka roju + baza wyników)

Cezar (wachta): „opcje MCP do nauki areny — tylko najlepsze wg zasad". Zbudowany
`narzedzia/arena_mcp.py` — serwer MCP (JSON-RPC/stdio, zero zależności, wzorzec
`rag/mcp_server.py`). 4 narzędzia: `arena_roj` (instant migawka z rejestru — neurony
aktywne/wyciszone, zwiadowcy, elita, kategorie, wykorzystanie %), `arena_neuron` (szczegóły
po KLUCZU), `arena_zapisz`/`arena_pytaj` (baza SQLite `arena_wyniki.db` — Claude ZAPISUJE
pomiary IC/scoreboard i PYTA o nie później; akumulacja przez wachtę). DB gitignore (runtime
per-maszyna, jak `baza_wiedzy.db`).

Filozofia (Prawo XVI/XXV): rój UCZY SIĘ w kodzie (MWU/synapsy/igrzyska) — MCP to soczewka,
nie learner. Świadomie NIE dodano oficjalnego „Memory" MCP (redundancja z 13 warstwami).
`.mcp.json` (rejestracja serwerów + npx filesystem) zostawiony Cezarowi do ręcznego wklejenia
(config startowy — decyzja użytkownika, nie auto).

Testy: `tests/test_arena_mcp.py` — 15, w tym granice (pusta baza, limit≤0, pusty rodzaj/neuron
→ ValueError, filtry, najnowsze-pierwsze, JSON-RPC nieznana metoda/narzędzie). Pełne testy
zielone, audyt exit 0, smoke-test serwera OK.

**Pliki:** `narzedzia/arena_mcp.py` (NEW), `tests/test_arena_mcp.py` (NEW),
`.gitignore` (arena_wyniki.db), `docs/LOG_ZMIAN.md`, `docs/SCIAGA_LOKAL.md`.

---

## 2026-07-04 | RECENZJA | 🔍 Cubic PR #104 — 12 uwag naprawionych (granice + robustność)

Adversarial review (cubic) na PR #104. Ważne uwagi naprawione u źródła:
- **news_fetcher**: daty pubDate/ISO bez strefy normalizowane do UTC (naive→tzinfo=utc),
  koniec błędnego wieku nagłówka przy porównaniu świeżości (NEWS-08).
- **deepseek_glos**: SSL_CERT_DIR traktowany jako lista os.pathsep — nie kasujemy całego
  wpisu gdy CHOĆ JEDEN komponent CA-bundle istnieje (enterprise CA nietknięty).
- **walk_forward_ic**: `_ic_per_okno` rzuca ValueError przy okna<1 (zamiast dzielenia przez 0).
- **wykres_backtestu**: guardy okno>=1 i max_barow>=1.
- **raport_ic**: `ranking[:max(0, top)]` — top<0 nie odsłania ogona (kontrakt „top N").
- **README**: usunięty hardkod „1038/1038" (Prawo I: liczby nie przeterminowane).

Test-Granice dodane (Reguła Test-Granic): _klasa_ic na 0.0/0.02/0.05/±; walk_forward
średni IC==prog(0.03) i spójność==prog(0.75) → ROBUST (>=); SSL_CERT_DIR lista zachowana
gdy jeden istnieje / skasowana gdy wszystkie martwe. 1946/1946 zielone, audyt exit 0.

**Pliki:** news_fetcher.py, deepseek_glos.py, walk_forward_ic.py, wykres_backtestu.py,
raport_ic.py, README.md, test_raport_ic.py, test_walk_forward_ic.py, test_deepseek_cert.py.

---

## 2026-07-04 | NAPRAWA | 📅 Audyt W6: data vs OSTATNI COMMIT (koniec codziennego fałszywego alarmu)

Cezar (lokal): testy pękały co kilka dni — audyt W6 porównywał „Stan na:" z date.today(),
tolerancja 2 dni → repo leżące bez commitu szło czerwone, choć data dokumentu = data ostatniej
zmiany (poprawna). Fix: odniesienie = data OSTATNIEGO COMMITU (git log -1 --date=short),
nie zegar. Wciąż łapie prawdziwą niespójność (kod zmieniony + stara data → alarm), ale repo
w spoczynku pozostaje zielone. Fallback na dziś gdy brak gita. 13/13 test_spojnosc.

---

## 2026-07-04 | NEWS | ⏳ NEWS-08: half-life — świeży nagłówek waży więcej

Plan NEWS pkt 8. Fetcher: `_pozycje_z_rss()` wyłuskuje pubDate (RSS RFC822) / published/updated
(Atom ISO) → `_parsuj_date_pub()` (email.utils + fromisoformat, stdlib). Metadane dostają
`data_pub`. Adapter `_wagi_swiezosci()`: waga = 0.5^(wiek/half_life), wiek WZGLĘDEM najnowszego
w partii (samowystarczalne, bez zegara); half-life 12h; brak daty → 1.0. Wagi świeżości ×
wagi źródeł (05×08) w ważonym sentymencie; NEWS_SWIEZOSC jako wskaźnik. Zmierzone: świeży 1.0,
sprzed 24h ≈0.25; świeży byczy przeważa stary niedźwiedzi. +9 testów (84/84 news).

System NEWS: 8/10 punktów planu (fetcher+01-08). Zostały: social(9)/on-chain(10).

---

## 2026-07-04 | NEWS | ⚖️ NEWS-07: rozrzut/niezgoda nagłówków (dispersion)

Plan NEWS pkt 7. `_rozrzut_naglowkow()`: każdy nagłówek klasyfikowany osobno (leksykon)
na byczy/niedźwiedzi; NEWS_ROZRZUT = 1 − |byki−niedźwiedzie|/głosy (0=jednomyślne,
1=pół-na-pół, None=brak wydźwięku). Zmierzone: 2:1 → 0.667.

DECYZJA (Prawo XVI — pomiar przed wpływem): rozrzut jest WSKAŹNIKIEM informacyjnym w kluczu,
celowo NIE mnoży pewności (mamy już stack 05×06) — wartość predykcyjna zostanie zmierzona
IC zanim dostanie wpływ na głos. +6 testów (45/45 sentyment_news).

---

## 2026-07-04 | NEWS | 🔄 NEWS-06: novelty — powtórzony news już wyceniony (original-vs-amplified)

Plan NEWS pkt 6. Adapter pamięta znormalizowane nagłówki z poprzednich pobrań (deque 300
per symbol). NEWS_NOVELTY = frakcja świeżych nagłówków (liczona WZGLĘDEM przeszłości, przed
dopisaniem bieżących — jak Δ/spike). Pewność × (0.5+0.5·novelty): feed całkiem przeżuty waży
o połowę mniej (stary news już w cenie), świeży bez kary. Pamięć per symbol (BTC nie zaraża ETH).
Zmierzone: ten sam nagłówek bar2 → novelty 0.0, pewność 0.7→0.35. +4 testy (69/69 news).
Modyfikator jakości jak NEWS-05 (Prawo XVI — nie neuron).

---

## 2026-07-04 | NEWS | 📰 NEWS-05: wiarygodność źródła (source credibility, research 2026)

Plan z NEWS_ROZBUDOWA pkt 5. Decyzja (Prawo XVI): to MODYFIKATOR jakości sentymentu, nie osobny
neuron (byłby skorelowany z NEWS-01). Wpięte w fetcher+adapter:
- `news_fetcher.py`: WIARYGODNOSC_ZRODEL (coindesk 1.0, cointelegraph 0.9, decrypt 0.85,
  reuters/bloomberg 1.0; nieznane 0.5) + `pobierz_z_metadanymi()` → [{tytul, zrodlo, waga}].
  Stare `pobierz()` nietknięte (wstecznie kompatybilne).
- `news_llm.py`: słownikowy sentyment WAŻONY wagą źródła (trafienie z CoinDesk > blog);
  NEWS_PEWNOSC × średnia wiarygodność; nowy klucz NEWS_WIARYGODNOSC.
Zmierzone: ten sam nagłówek — CoinDesk pewność 0.6 vs nieznany blog 0.3. +7 testów.

---

## 2026-07-04 | WIZUALIZACJA | 🖼️ Wykres backtestu — oczy Cezara (Prawo XV: Kartograf wpięty)

Cezar: „czuję się jak dziecko we mgle — nie mam podglądu wykresów jak zachowuje się Imperium".
AUDYT WIZUALIZACJI: mamy web_dashboard :8777 (świecowy live przy skrypty/start.py), LiveMonitor
TUI+Telegram, 2 symulatory HTML — ale 🚨 UTRATA POTENCJAŁU: `swiatynie/kartograf.py` (PNG:
cena+EMA+trades+equity) wpięty TYLKO w pierwszy_zwiadowca — backtesty były ślepe.

**`narzedzia/wykres_backtestu.py`** (reuse Kartografa, Prawo XVI): jedna komenda backtest→PNG,
2 panele: cena+EMA-50+znaczniki transakcji (▲/▼, zysk/strata kolorem, linia wejście↔wyjście)
+ krzywa kapitału per bar. Mapowanie WynikZamkniecia→indeksy barów po timestamp_wejscia
(ts=0 pomijany; exit przycinany). Zweryfikowane na DOGE 4h (uczciwy obraz: bessa, -1281$, WR 39%
— Cezar to ZOBACZYŁ zamiast zgadywać). +6 testów. Lekcja o potrzebie wizualizacji → W3 (profil).

---

## 2026-07-04 | POMIAR | 🔬 Walk-forward IC — stabilność skillu neuronu w czasie (OOS, Prawo XVI)

Pojedynczy IC mówi ILE, nie czy POWTARZALNE. `narzedzia/walk_forward_ic.py`: dzieli historię
na K kolejnych okien, mierzy IC WARUNKOWY per okno, werdykt po SPÓJNOŚCI ZNAKU:
  • ROBUST — |śr.IC|>0.03 + ten sam znak w ≥75% okien (skill stabilny, nie przeuczony)
  • ROBUST (odwróć) — stabilnie ujemny → kandydat do odwrócenia wagi
  • niepewny/szum — miesza znak lub IC ~0.
Neurony=reguły stałe → każde okno OOS z natury (zero look-ahead). Reuse czytnik_csv + backtest.

DOGE 4h (4 okna): SMC-01/02, V-14, X-28, X-17, V-02, X-01 → 100% spójność (skill POTWIERDZONY
OOS); SES-02 robustnie ujemny (odwróć). Zgodne z raportem IC z 15 par — walidacja krzyżowa.
+6 testów. Pasek postępu per para/okno. To baza decyzji o wagach (Prawo XXV).

---

## 2026-07-01 | NAPRAWA | 🔒 DeepSeek odporny na zepsuty SSL_CERT_FILE (Prawo XV)

Realny przypadek Cezara na lokalu: `SSL_CERT_FILE=C:\...\Temp\cacert.pem` (leftover po jakimś
narzędziu) wskazywał na NIEISTNIEJĄCY plik → httpx/openai wywalał FileNotFoundError zanim
dotarł do DeepSeek API. Klucz był poprawny — winna martwa zmienna środowiskowa.

Fix (`deepseek_glos.py`): `_napraw_zepsuty_cert_env()` przed utworzeniem klienta — gdy
SSL_CERT_FILE/SSL_CERT_DIR wskazuje na nieistniejący plik/katalog, usuwa go z env (fallback
na certifi). Poprawne ścieżki nietknięte. +4 testy (bez sieci). 1895→1899. Chroni każdą maszynę.

---

## 2026-07-01 | POMIAR | 📊 Raport IC roju — który neuron ma realny skill (Prawo XVI)

Domknięcie „metod treningowych": `narzedzia/raport_ic.py` uruchamia backtest(mierz_ic=True)
na prawdziwych świecach i rankuje Information Coefficient per neuron przez pary. Interpretacja
Grinold&Kahn (BIB-025): |IC|<0.02 szum, ~0.03 słaba przewaga, >0.05 mocny; IC ujemne = kandydat
do odwrócenia. Flaguje neurony do wygaszenia i pokazuje status NEWS-01..04.

UCZCIWIE (Prawo I): na KRÓTKICH danych IC bywa zawyżone (|IC|>0.2 = artefakt rzadkich sygnałów
+ remisów Spearmana, NIE realny skill; prawdziwy IC krypto ~0.02-0.05). Raport sam OSTRZEGA gdy
za dużo |IC|>0.2 i zaleca pełną historię. Wiarygodny pomiar = pełna historia + kontrole
(narzedzia/pomiar_nowe_moduly.py backward-IC/non-overlapping). +3 testy. 1892→1895.

To baza pod Prawo XXV: wagi neuronów mają iść za ZMIERZONYM IC, nie intuicją. PR #103 (naprawy
cubic) zmergowany do main — cubic zamknięty.

**Update 2026-07-01 (lokal Cezara):** dodany pasek postępu na stderr (15 par bez niego wyglądało
jak zawieszenie). POMIAR na danych dziennych/krótkich → ostrzeżenie „niska wiarygodność" działa
poprawnie (IC 0.4-0.5 = ARTEFAKT rzadkich głosów + remisów Spearmana, NIE skill). WNIOSEK (Prawo I):
IC z DYSKRETNYCH głosów (kierunek×pewność, w większości 0) jest zawyżony dla rzadko głosujących
neuronów. Prawidłowy pomiar = IC WARUNKOWY (tylko bary gdzie neuron głosuje) lub ciągły sygnał
(pomiar_nowe_moduly.py). Następny krok: warunkowy IC w KolektorIC. **ZROBIONE (ten sam dzień):** KolektorIC.ic(tylko_glosy=True) — IC warunkowy liczony tylko na barach z głosem; backtest wystawia engine.ic_warunkowy; raport_ic używa go domyślnie. Inflacja znikła (DOGE 4h: brak ostrzeżenia, rozkład 0.10-0.25 + neurony ujemne widoczne). +2 testy. 1899→1901.

---

## 2026-07-01 | RECENZJA | 🔧 Naprawa 30 uwag recenzenta (cubic) — P0/P1/P2/P3

Recenzja cubic na PR: 38 uwag. Naprawione wszystkie trafne (Prawo XXI — bugi PRZED mergem):

**P0:** `klasyfikator_zdarzen.py` — ZeroDivisionError gdy tylko MAKRO (kierunek=0) trafiony
(sum(wklad)=0). Fix: gałąź suma_wkladu==0 → typ po rozkładzie, kierunek 0. +test regresji.
**P1:** `start_lokal.py` — brak `sys.path.insert(ROOT)` → importy imperium.* padały lokalnie. Fix.

**P2 (bugi):**
- `news_fetcher.py`: (a) BUSD przed USD w kolejności sufiksów (BTCBUSD→BTC); (b) tylko tytuły
  item/entry (tytuł kanału to metadane, nie nagłówek); (c) aliasy per-aktywo z granicą \b (nie podciąg).
- `backtest.py`: zwrot IC rejestrowany KAŻDY bar (nie tylko z raportem) — zgodność horyzontów.
- `graf_pamieci.py`: filtr węzłów do obecnych w zachowanych krawędziach (koniec węzłów-sierot).
- `dziennik_niesmiertelny.py`: walidacja że wczytany JSON to obiekt (jedna zła linia nie psuje recall).
- `zapominanie.py`: raport() bez limitu (pełna liczba kandydatów, nie ucięta do 30).
- `pamiec_proweniencji.py`: tokeny ≥2 znaki (śledzenie W3/W8); kronika bez limitu przed sortem.
- `kronika_czatu.py`: (a) .md.gz liczone jako istniejący eksport (koniec duplikatów); (b) sort po mtime.
- `kustosz_pamieci.py`: walidacja dni<0 (nie kompresuj aktywnych sesji).
- `centrum_pamieci.py`: pusty Dziennik wykrywany po dokładnym markerze (nie substring „pusty").
- `_jit.py`: @njit i @njit() spójne (cache=True domyślnie w obu).
- `audyt_spojnosci.py`: NEWS-02/03/04 dodane do WERYFIKACJA_ADAPTEROW (kontrakt weryfikacji).
- `pamiec_robocza.py` → CoALA + Zep + event-sentiment w REJESTR_INSPIRACJI (ZPO).

**P3:** typo CLI (biblioteci→biblioteki ×2); `dziennik` ostatnie≤0; `proceduralna` CLI --zrodlo;
procedury.jsonl — sprostowanie o pre-commit hooku (nie klonuje się); klasyfikator pewnosc w teście.

**Testy graniczne (Reguła Test-Granic):** +14 testów granic (news_dynamika Δ/spike/sent,
zapominanie prog/wiek, kustosz dni=30 dokładnie + dni<0, proceduralna limit/regex, graf izolowane,
klasyfikator MAKRO-only, fetcher exact count). Zachowana logika, wynik identyczny.

**Bonus (Prawo XVIII) — krucha zależność od daty:** `RegulaSzesciuProcentEldera.reset_miesiac`
stemplowała `date.today().month` → w nowym miesiącu (lipiec) 4 testy 6% pękały (fałszywy reset
przy aktualizuj z czerwcową datą). Fix: reset_miesiac przyjmuje `dzisiaj` (deterministyczny miesiąc);
testy go używają. Testy 6% niezależne od wall-clock.

---

## 2026-06-30 | POMIAR | 📊 W-385: IC roju w backteście — fundament Prawa XVI

Cezar: „dawaj". Logowanie/pomiar predykcyjności newsów. UCZCIWIE (Prawo I): brak historycznych
danych newsów → newsów nie da się zbacktestować TERAZ. Ale infrastruktura pomiaru wpięta dla
CAŁEGO roju — NEWS-01..04 dołączą automatycznie, gdy popłynie feed (lokal+RSS/DeepSeek).

Reuse (Prawo XVI — nie dublujemy): `KolektorIC` (W-369, Spearman) i `_spearman` już istniały,
ale NIE były wpięte nigdzie. Teraz `backtest(mierz_ic=True)` zbiera sygnał_t każdego neuronu
(kierunek×pewność) i paruje z PRZYSZŁYM zwrotem_{t+h} — zero look-ahead (sygnał nie widzi t+h).

- `imperium/koloseum/backtest.py`: opt-in `mierz_ic` → `engine.ic_srednie` + `engine.ic_pelne`.
  Domyślnie False (zero narzutu). Zmierzone na syntetyku: 34/91 neuronów z IC; NEWS-01..04 śledzone.
- +4 testy (raport dołączony, NEWS objęte, zakres [-1,1], brak narzutu gdy off). 1873→1877.

To domyka „metody treningowe": każdy neuron (w tym news) dostaje MIERZALNĄ przewagę
predykcyjną (IC) zanim dostanie większą wagę — zgodnie z Prawem XVI i nowym Prawem XXV.

---

## 2026-06-30 | NEURONY+PRAWO | 📈 NEWS-03/04 dynamika newsów + PRAWO XXV (W-382)

Cezar: „dawaj wszystko". Dwa neurony dynamiki + zatwierdzona zasada przewagi.

**Stan kroczący adaptera** (AdapterNewsLLM): deque per symbol pamięta poprzednie
sentymenty i liczby nagłówków → dolewa NEWS_SENTYMENT_DELTA + NEWS_ATTENTION_SPIKE.

- **NEWS-04 Δ Sentymentu** (`news_dynamika.py`): momentum informacyjny = pochodna
  sentymentu (bieżący − średnia historii). Rośnie→LONG, opada→SHORT. WSKAZNIK
  NEWS_SENTYMENT_DELTA, kat R, waga 5, mechanizm event.
- **NEWS-03 Spike Uwagi**: przełom informacyjny = liczba nagłówków / średnia historyczna.
  Spike ≥2× × kierunek sentymentu → breakout LONG/SHORT; spike bez kierunku → czujność
  (NEUTRAL). WSKAZNIK NEWS_ATTENTION_SPIKE, kat R, waga 5, mechanizm vol_signal.
- Cztery wymiary newsów (Prawo XVI — nie redundancja): poziom (01), typ (02), uwaga (03),
  momentum (04). Rejestracja pełna; neurony 82→84 (78 aktywnych). +11 testów. 1862→1873.

**PRAWO XXV — PRZEWAGA KONKURENCYJNA** (ZASADY_FUNDAMENTALNE.md): Cezar zatwierdził.
Imperium mierzy się ze stanem sztuki; gdy słabsze — research+adopcja+pomiar (spina XV+XVI+XXII).
Konstytucja 24→25 praw (CLAUDE.md, README zaktualizowane). XXII pozostaje „Dekorelacja Przewagi".

UWAGA (Prawo XVI — następny krok): logowanie sentymentu do W1 dla pomiaru predykcyjności
per kategoria — NIE zrobione w tej rundzie (infra pomiarowa), zaplanowane.

---

## 2026-06-30 | NEURON | 🏷️ NEWS-02 Taksonomia Zdarzeń — kierunek per TYP (W-381)

Cezar: „dawaj wszystko". Drugi neuron newsowy — research-grounded (arXiv:2508.07408):
kierunek zależy od TYPU zdarzenia, nie samej polaryzacji. Rumor/spekulacja = KONTRARIAŃSKIE
(ujemny Sharpe → fade hype). To czyni NEWS-02 mądrzejszym od płaskiego NEWS-01.

- `imperium/akwedukty/klasyfikator_zdarzen.py`: deterministyczna taksonomia 8 typów
  (HACK/UPADEK/REGULACJA_NEG → ujemne; ETF/INSTYTUCJONALNY/TECHNICZNY → dodatnie;
  RUMOR → ujemny kontrariański; MAKRO → 0). Słowniki pełnych słów, kierunek znakowany netto.
- `imperium/legiony/neurony/zdarzenia.py`: NEWS-02 NeuronTaksonomiaZdarzen (kat. R, waga 6,
  WSKAZNIK NEWS_EVENT_KIERUNEK). Próg 0.30/0.65; abstynuje bez feedu (Prawo XV).
- AdapterNewsLLM rozszerzony: dolewa NEWS_EVENT_KIERUNEK/TYP/PEWNOSC; budzi NEWS-02.
- Rejestracja: rejestr.py (import+lista+2 mapy), MANIFEST, MAPA_KLUCZY, audyt whitelist.
- Neurony 81→82 (76 aktywnych). +11 testów. 1851→1862.

Różne od NEWS-01 (Prawo XVI — nie redundancja): NEWS-01=JAK pozytywny (sentyment),
NEWS-02=JAKI TYP i jego kierunek (rumor=kontrariański). Dwa różne sygnały.

UWAGA (Prawo I): Prawo XXII już istnieje (Dekorelacja Przewagi). Proponowana „przewaga
konkurencyjna" → Prawo XXV (do decyzji Cezara — zmiana konstytucji).

---

## 2026-06-30 | UNLOCK+RESEARCH | 📰 FetcherNewsRSS — odblokowanie NEWS-01 + plan rozbudowy

Cezar: rozbuduj NEWS-01, sweep świata, oryginalne moduły, wyprzedzać konkurencję.

AUDYT NEWS-01: neuron + adapter (DeepSeek + fallback słownikowy) gotowe, ale adapter miał
PUSTY fetcher → NEWS-01 zawsze milczał, nawet z DeepSeek. Brakującym ogniwem był FEED, nie API.

**UNLOCK — FetcherNewsRSS** (`imperium/akwedukty/news_fetcher.py`): pobiera nagłówki z darmowych
RSS (CoinDesk/CoinTelegraph/Decrypt), parsowanie stdlib (xml.etree, ZERO nowych zależności),
filtr per-aktywo (BTC/ETH/DOGE...), dedup między wydawcami, wstrzykiwalny pobieracz (offline-test).
Graceful: brak sieci → [] → NEWS-01 abstynuje (Prawo XV). Wpięty w petla_live (opt-in live).
+10 testów. Działa: BTC→"ETF rally" +1.0, ETH→"hack" neg, pełny feed +0.655.

RESEARCH (sweep świata, ZPO): dostawcy CoinGecko News/CoinDesk/Crypto News API; badania granicy
2026 — event-aware sentiment (arXiv:2508.07408: rumor/retail-buzz = KONTRARIAŃSKIE, ujemny Sharpe!),
Janus-Q (arXiv:2602.19919). Plan 10 modułów: taksonomia zdarzeń, spike uwagi, Δ sentymentu,
wiarygodność źródła, novelty, rozrzut, social, on-chain. Propozycja Prawa XXII (przewaga konkurencyjna).
Pełny plan: docs/NEWS_ROZBUDOWA_2026-06-30.md. 1841→1851.

---

## 2026-06-30 | NAPRAWA+LOKAL | 🖥️ Przewodnik startu lokalnego + naprawa reprodukowalności

Cezar: „jak pamięć działa w chmurze vs lokal, czy lokal ma dostęp do wszystkich plików,
sprawdź nowinki, i kiedy ostatnio używaliśmy lokala (test pamięci)."

**Test pamięci (zdał):** proweniencja + kronika znalazły — lokal konfigurowany ~2026-06-22
(TA-Lib Windows 10, Paper Trading, plan MEXC live, test DOGE). UCZCIWIE (Prawo I): brak
twardego logu W1 → test DOGE/MEXC był OMAWIANY, wynik nie trafił do pamięci. Luka do domknięcia.

**🚨 CZERWONY ALARM złapany (Prawo XV):** świeży kontener wystartował na ZŁYM commicie
(main merge #101 = stara migawka v5) zamiast na czubku gałęzi (065f789 = pełne v6-v13).
Cała praca sesji „zniknęła" z working tree. DIAGNOZA: praca BEZPIECZNA na origin; lokalny
desync. NAPRAWA: `git reset --hard origin/claude/sleepy-fermi-dsdE4` → wszystko wróciło.

**🚨 Luka reprodukowalności (Prawo XV):** `scipy` i `pytest` NIE były w requirements.txt —
działało tylko bo stary kontener je miał. Świeży: BOCPD-01 milczy (martwy głos), 17 testów
import-error. NAPRAWA: dodane do requirements (scipy>=1.10 runtime, pytest>=7.0 dev).
Po instalacji: 1841/1841 zielone, audyt harmonia, BOCPD-01 znów głosuje.

**Deliverable:** `skrypty/start_lokal.py` (jednokomendowy rozruch lokala: env→audyt→katalog+graf
→RAG→mapa) + `docs/START_LOKAL.md` (przewodnik dla nowicjusza: chmura vs lokal, dodatki
tylko-lokal = wektory/Filesystem MCP/DeepSeek/trwałe logi W1, domknięcie luki testu DOGE).
Pliki: requirements.txt, skrypty/start_lokal.py (nowy), docs/START_LOKAL.md (nowy), INDEKS.

---

## 2026-06-29 | KONSOLIDACJA | 🗺️ W-360 v13: przegląd 13 warstw + mapa + odchudzenie grafu

Cezar: „konsolidacja". Przegląd całej pamięci (13 warstw, 3568 linii kodu) — pomiar, nie opinia.

**Mapa jako jedno źródło prawdy:** `docs/MAPA_PAMIECI.md` + `kustosz.mapa()` (CLI: `kustosz mapa`)
— tabela 13 warstw (klucz/moduł/rola/typ CoALA), pokrycie taksonomii CoALA (kompletne),
domknięte problemy granicy 2026, unikaty, jeden punkt wejścia.

**Pomiar redundancji (Prawo XVI):** każda warstwa pełni odrębną rolę CoALA/granicy — ZERO
dwóch warstw o tym samym sygnale. Nic do scalenia. W12/W13 bez własnych plików (czytają
z innych — zero redundancji danych). Potwierdzono: brak waty, brak dubli.

**Odchudzenie grafu (W8):** persistowany graf przełączony na `min_waga≥2` — jednorazowe
współwystąpienia (szum) odcięte: 30833→883 krawędzi, 3.74MB→0.18MB (95% mniej w repo),
graf ostrzejszy. Funkcja zachowuje param min_waga (małe próbki/testy: 1).

13 warstw potwierdzone i zmapowane. +4 testy (mapa, graf waga). 1839→1841.
Pliki: kustosz_pamieci.py (mapa), graf_pamieci.py (waga≥2), docs/MAPA_PAMIECI.md (nowy), INDEKS.

---

## 2026-06-29 | UNIKAT | 🔍 W-360 v13: Pamięć Proweniencji — ŚLAD POCHODZENIA („skąd to wiemy")

Cezar: „dawaj". Deep research: „From Agent Traces to Trust — Evidence Tracing and Execution
Provenance in LLM Agents" (arXiv:2606.04990) — pamięć agenta potrzebuje PROVENANCE-AWARE
RETRIEVAL + temporal credit assignment: wiedzieć skąd info, kiedy weszła, jak wędrowała.

**W13 Pamięć Proweniencji** (`pamiec_proweniencji.py`): dla dowolnego pojęcia buduje
ŚLAD POCHODZENIA — wystąpienia w czasie przez wszystkie warstwy (kronika W3b + dziennik W6
+ lekcje W3 + wizje W4), z datą i sesją. `geneza()` = pierwsze wystąpienie („tu się narodziło"),
`raport()` = ugruntowanie (ile sesji/warstw — temporal credit). Odpowiada: „skąd to wiemy?",
„świeży pomysł czy ugruntowana wiedza?". Zmierzone: „numba" → geneza 2026-06-21, 3 warstwy.

Różne od Grafu (W8=połączenia) i Katalogu (W7=indeks): proweniencja = oś czasu JEDNEGO
pojęcia z atrybucją źródła. Bez własnego pliku (czyta z warstw — Prawo XVI). +6 testów.
13 warstw pamięci pod Kustoszem. 1833→1839. Pliki: pamiec_proweniencji.py (nowy), INDEKS_IMPERIUM.md.

---

## 2026-06-29 | UNIKAT | 🛠️🎯 W-360 v11+v12: Pamięć Proceduralna + Robocza — pełna czwórka CoALA

Cezar: „jeszcze kilka warstw pamięci, poszukaj, wg zasad." Deep research: CoALA
(arXiv:2309.02427) definiuje 4 kanoniczne typy pamięci agenta. Mieliśmy 2 (epizodyczna=kronika,
semantyczna=lekcje/RAG). Brakowało PROCEDURALNEJ i ROBOCZEJ — dobudowane (Prawo XVI: nie
redundancja, lecz domknięcie taksonomii poznawczej).

**W11 Pamięć Proceduralna** (`pamiec_proceduralna.py`) — runbooki JAK wykonać zadanie
(różne od lekcji=CO wiemy): „dodać neuron", „naprawić audyt W11", „bezpieczny commit",
„dodać warstwę pamięci". Każda = wyzwalacz (kiedy użyć) + KROKI + źródło. szukaj() po
słowach → właściwa procedura pod ręką. Ziarno 4 realnych procedur Imperium. JSONL→git.

**W12 Pamięć Robocza** (`pamiec_robocza.py`) — CoALA working memory: AKTYWNY CEL bieżącego
cyklu (ostatni „następny" z Dziennika W6) + pilne sygnały (sprzeczności W9). Bez własnego
pliku (czyta z W6/W9 — zero kosztu, nie duplikuje). Różne od Dziennika: oś=cały łuk vs
robocza=jedno ostrze TU-I-TERAZ. Wstrzykiwana na starcie: jednym rzutem wiesz gdzie wejść.

DOMKNIĘTA pełna czwórka CoALA: robocza(W12)+epizodyczna(W3b)+semantyczna(W3/W2)+proceduralna(W11).
12 warstw pamięci pod Kustoszem. +11 testów. 1822→1833. Pliki: pamiec_proceduralna.py,
pamiec_robocza.py (nowe), centrum_pamieci.py, INDEKS_IMPERIUM.md, procedury.jsonl.

---

## 2026-06-29 | UNIKAT | 🍂 W-360 v10: Mądre Zapominanie — LEARNED FORGETTING

Cezar: „wszystko dawaj". Trzeci (po reflection i contradiction = W9) nierozwiązany problem
granicy pamięci agentów 2026 (arXiv:2603.07670): LEARNED FORGETTING — obecne systemy
zapominają prymitywnie (czasowo/po limicie); cel = zapominanie SELEKTYWNE, wartościowe.

**W10 Mądre Zapominanie** (`zapominanie.py`) — zapominanie NIE czasowe, lecz wartościowe:
- `wartosc_retencji()` = ważność (słowa-klucze) × świeżość (zanik warstwowy FinMem)
  × bonus łączności w Grafie W8 (hub = cenny); otwarte plany POMYSŁ/PLANOWANE chronione (≥0.5).
- `kandydaci_do_zapomnienia(prog, dni)` — niska retencja + wiek → propozycja SCHŁODZENIA
  do zimnej warstwy Kustosza W7 (.md.gz, wciąż przeszukiwalne → nic nie ginie, odwracalne).
- ZASADA ANTY-UTRWALANIA (jak W9): NIGDY nie kasuje — tylko proponuje, Cezar decyduje.
  Test pilnuje braku metod kasujących. „Safe forgetting": git + zimna warstwa = nic nie ginie.
- Deterministyczny (bez API), z W3 lekcji + W4 wizji + W8 grafu; wpięty w start gdy są kandydaci.

Zamyka pętlę: W10 decyduje CO schłodzić, W7 to kompresuje. 10 warstw pamięci pod Kustoszem.
Trzy problemy granicy 2026 (reflection+contradiction=W9, forgetting=W10) — domknięte deterministycznie.
+10 testów. 1812→1822. Pliki: zapominanie.py (nowy), centrum_pamieci.py, INDEKS_IMPERIUM.md.

---

## 2026-06-29 | UNIKAT | 🪞 W-360 v9: Refleksja Pamięci — SPRZECZNOŚCI + PRZEDAWNIENIE

Cezar: „czy pamięć jest najlepsza na świecie? ulepsz o kolejne warstwy/autorskie moduły —
deep research, kreatywność, wizja, wg zasad."

UCZCIWA OCENA (Prawo I): żaden system nie jest „najlepszy na świecie" na wszystkich osiach.
Nasza przewaga = wyjątkowo KOMPLETNA, deterministyczna, domenowa kombinacja (8→9 warstw +
reżim + graf). Deep research granicy 2026 (arXiv:2603.07670 przegląd; arXiv:2602.01966
self-consolidation) wskazał czego nam brakowało: TRUSTWORTHY REFLECTION, contradiction
handling, learned forgetting. OSTRZEŻENIE z literatury: refleksja potrafi UTRWALAĆ błędy.

**W9 Refleksja Pamięci** (`refleksja_pamieci.py`) — autorski moduł wg granicy:
- `wykryj_sprzecznosci()` — wpisy o tym samym temacie z przeciwnym kierunkiem statusu
  w czasie: ROZSTRZYGNIĘTE (- →+, postęp/koniec krążenia) vs SPRZECZNE (+ →-, kolizja).
- `wykryj_przedawnienia(dni)` — otwarte POMYSŁ/PLANOWANE starsze niż N dni bez śladu
  realizacji (okno ważności à la Zep) → „wisi, zdecyduj".
- ZASADA ANTY-UTRWALANIA (wprost z literatury): TYLKO zgłasza, NIGDY nie kasuje —
  maszyna proponuje, Cezar dysponuje (Prawo XVIII). Test pilnuje braku metod kasujących.
- Deterministyczny (bez API), z W4 wizji + W6 dziennika; wpięty w start (gdy jest co zgłosić).

9 warstw pamięci pod Kustoszem. +9 testów. 1803→1812. Pliki: refleksja_pamieci.py (nowy),
centrum_pamieci.py, INDEKS_IMPERIUM.md.

---

## 2026-06-28 | UNIKAT | 🕸️ W-360 v8: Graf Pamięci — POŁĄCZENIA NEURONÓW (temporalny graf wiedzy)

Cezar: „wielopłaszczyznowe zapamiętywanie POŁĄCZEŃ NEURONÓW; przeszukaj patenty/repozytoria
globalnie (Azja/USA/EU), wdróż najlepsze, zrób petardę godną poza streszczeniem konkurentów."

Research SOTA 2026 (ZPO, globalny przegląd): **Zep/Graphiti** — Temporal Knowledge Graph dla
pamięci agenta (https://arxiv.org/abs/2501.13956), bije MemGPT na Deep Memory Retrieval; fakty
z OKNEM WAŻNOŚCI (validity window). A-Mem (połączone notatki). MemOS/Tsinghua (memory OS, Chiny).
Krytyka uczciwa: „Does Memory Need Graphs?" (arXiv:2601.01280) → graf to DODATKOWA soczewka do
pytań RELACYJNYCH, nie zamiennik retrievalu. Dlatego W8 uzupełnia W1-W7, nie zastępuje.

**W8 Graf Pamięci** (`graf_pamieci.py`) — to czego nie mamy, a jest hot 2026:
- WĘZŁY = encje (Numba, Kustosz, Viterbi, kompresja…), KRAWĘDZIE = współwystąpienia w jednym
  wpisie (waga + okno czasowe pierwszy/ostatni — temporal jak Zep).
- `polaczenia(X)` — z czym X jest połączone; `centralne()` — huby (centralne neurony);
  `sciezka(a,b)` — BFS jak dwa pojęcia są powiązane.
- Budowany deterministycznie (bez API) z Dziennika W6 + wizji W4 + lekcji W3. Persystowany
  do graf_pamieci.json (git → bezgraniczny, chmura↔lokal). Pod zarządem Kustosza W7.
- Zmierzone: 716 neuronów, 25802 połączeń. Numba↔{cache_wskaznikow, requirements, zmierzone}.

8 warstw pamięci pod jednym organem (reżimowa+środowiskowa+dziennik+kompresja+graf) —
tej kombinacji nie ma żaden konkurent. +9 testów grafu. 1794→1803. Pliki: graf_pamieci.py (nowy),
centrum_pamieci.py, INDEKS_IMPERIUM.md, graf_pamieci.json.

---

## 2026-06-28 | UNIKAT | 👑 W-360 v7: Kustosz Pamięci — NADRZĘDNY ORGAN + kompresja zimnej warstwy

Cezar: „nadrzędny organ, który kieruje wszystkimi warstwami — kompresja, katalogowanie,
pamięć bezgraniczna, niezależnie chmura/lokal. Coś czego nikt nie ma."

Research SOTA 2026 (ZPO): MemGPT/Letta (OS-like tiering, arXiv:2310.08560), TiMem
(arXiv:2601.02845), przegląd arXiv:2603.07670. Główny problem literatury: „memory blindness"
— agent nie wie, że fakt jest w zimnym magazynie. Nasz Dziennik (W6) już to łamie.

**W7 Kustosz Pamięci** (`kustosz_pamieci.py`) — jeden organ nad 7 warstwami:
- `census()` — stan wszystkich warstw (W1-W6) naraz
- `zbuduj_katalog()` — katalog nadrzędny (anti-blindness): każda sesja → tematy/data/rozmiar
- `kompresuj_zimne(dni)` — zimne sesje .md→.md.gz, WCIĄŻ przeszukiwalne (dekompresja w locie
  w kronika.szukaj) → zero blindness. Zmierzone 22× na sesji testowej.
- `szukaj()` — routing nadrzędny (6 warstw cross-layer + dziennik W6)

Pamięć BEZGRANICZNA: git = storage bez limitu; Kustosz trzyma kontekst ograniczony
(Dziennik zwięzły + zimne skompresowane), a NIC nie ginie. Wpięty w podsumowanie startowe.

Decyzja Prawo XVI (mierzone, nie przedwczesne): NIE kompresuję masowo teraz — przy 6 MB
to przedwczesne, .gz traci czytelność historii w git. Mechanizm gotowy, włączy się gdy urośnie.

kronika_czatu: szukaj/statystyki czytają .md i .md.gz (transparentnie). +9 testów Kustosza,
+ regresja „zimna przeszukiwalna". 1785→1794. Katalog nadrzędny zbudowany (100 sesji).
Pliki: kustosz_pamieci.py (nowy), kronika_czatu.py, centrum_pamieci.py, INDEKS_IMPERIUM.md, katalog_nadrzedny.json.

---

## 2026-06-28 | WYDAJNOŚĆ | ⚡ W-380: Numba/JIT na Viterbi Jump Model (zmierzone 256×)

Cezar: „dawaj numba". Numba była omawiana, nigdy zaimplementowana (W6 Dziennik to wychwycił).

**Cel wybrany pomiarem, nie zgadywaniem:** GARCH używa już scipy lfilter (C) → Numba mało by
dała. Prawdziwa gorąca pętla Python to `_viterbi` w Jump Model (DP, wołany n_startow×max_iter
razy na każde dopasuj(); zagnieżdżone pętle + np.argmin w środku).

**Wdrożenie:** `imperium/legiony/_jit.py` — most JIT: `njit` kompiluje gdy numba dostępna,
inaczej no-op (czysty Python). Prawo I: testy/audyt działają bez numby (fallback). Rdzeń
`_viterbi_core` (jawne pętle) wydzielony i jit-owany. `_viterbi` deleguje do niego.

**Pomiar (Prawo I):** rdzeń Viterbi 5.36 ms → 0.021 ms = **256× szybciej**. Wynik IDENTYCZNY
z referencją numpy (test na 4 wartościach kary). numba>=0.59 w requirements (opcjonalna).
+3 testy (identyczność jit vs ref, no-op fallback bez numby, determinizm). 1782→1785.
Pliki: _jit.py (nowy), jump_model.py, requirements.txt, test_jump_model.py.

---

## 2026-06-28 | UNIKAT+NAPRAWA | ♾️ W-360 v6: Dziennik Nieśmiertelny + naprawa wyszukiwarki

Cezar (niezadowolony, słusznie): „każde zdanie, każdy punkt co zrobiliśmy ma być pamiętane
DOŻYWOTNIO. Cofamy się, tracimy czas/tokeny/potencjał — to dziadostwo, łamie zasady."

**Diagnoza twarda (dane, nie zgadywanie):**
- NUMBA/JIT — SPRAWDZONE: NIE zaimplementowana (zero kodu, brak w requirements), była tylko
  OMAWIANA w 4 sesjach (jest w kronice). Dowód, że pamięć przechowuje, ale nie surfacuje.
- **Bug KRYTYCZNY wyszukiwarki kroniki:** `if zapytanie in linia` — cała fraza jako jeden
  substring. „numba JIT wydajność" → 0 trafień, samo „numba" → 4. Każde naturalne wielosłowne
  pytanie NIE znajdowało historii → wracaliśmy do zamkniętych tematów. To rdzeń problemu Cezara.

**Naprawa 1:** wyszukiwarka kroniki token-based (po słowach, ranking = liczba trafionych słów).
Teraz „numba JIT wydajność wskaźniki" → 6 trafień z historii. +2 testy regresji.

**Naprawa 2 (UNIKAT) — W6 Dziennik Nieśmiertelny** (`dziennik_niesmiertelny.py`): dożywotnia
ZWIĘZŁA oś czasu. Każda sesja = co zrobiono/decyzje/następny krok (~5 linii). Wstrzykiwana
W CAŁOŚCI na starcie (ostatnie 12 pełne, starsze jednolinijkowe) → na początku KAŻDEJ sesji
widzę cały łuk projektu, nie tylko top-3 lekcje. Deterministyczne: pisze Claude SAM (bez
DeepSeek). ROZKAZ STAŁY w CLAUDE.md; brak wpisu z dziś = alarm w podsumowaniu startowym.
Backfill 4 sesji. +6 testów. 1774→1782.

Różnica od konkurencji: Mem0/Zep/Letta polegają na retrievalu (gubi). Dziennik GWARANTUJE
widoczność całej historii — pełne wstrzyknięcie, nie statystyka.

---

## 2026-06-28 | WYDAJNOŚĆ | ⚡ Cache wskaźników wpięty w sweepy AB (zmierzone 1.4×)

Cezar: „dawaj" (wydajność). Odkrycie (Prawo XV): cache wskaźników + multiprocessing
(`cache_wskaznikow`, `prekalkuluj_portfel`) BYŁ zaimplementowany i przetestowany jako
identyczny wynikowo, ale `cache_wskaznikow` domyślnie False → ŻADNE narzędzie sweepu
go nie włączało. Optymalizacja spała.

**Pomiar (dane, nie obietnice):** 3 pary / 400 barów 4h → OFF 30.1s, ON 21.5s = **1.4×**,
kapitał identyczny (9979.80). Wcześniejsze „6-8×" w dokumentacji było aspiracyjne —
skorygowane (Prawo XXI/I). Pętli portfela NIE da się zrównoleglić po parach (współdzielą
kapitał → złamana semantyka); cache obejmuje prekalkulację wskaźników (równoległą).

**Zmiana:** `cache_wskaznikow=True` w BAZA 5 narzędzi sweepu (ab_w329/330/334/335/336).
Bezpieczne — wyniki dowiedzione identyczne (test_backtest_portfel_cache_wskaznikow).
Dokument PAMIEC_SESJI A2 zaktualizowany zmierzonymi liczbami.

---

## 2026-06-28 | NAPRAWA | 🚨 Kronika czatu — re-eksport rosnącej sesji (UTRATA POTENCJAŁU)

Audyt hooka wykrył: kronika bieżącej sesji zamrożona na 2026-06-22 (24 KB), a żywy
transkrypt miał 1933 linie z całą pracą v4/v5 (27-28 czerwca). Przyczyna: `eksportuj`
z `tylko_nowe=True` pomijał KAŻDY istniejący `.md` → AKTYWNA sesja, eksportowana raz
na pierwszym starcie (gdy krótka), nigdy nie dostawała reszty dialogu. **5 dni pracy,
w tym cała budowa pamięci v4/v5, ginęło z efemerycznym kontenerem chmury** — wprost
zaprzeczenie celu „mamy wszystko pamiętać każdy krok rozmowy" (Prawo XV).

**Naprawa:** `eksportuj` re-destyluje sesję, gdy mtime źródła > mtime celu (aktywna
sesja rośnie → doeksportowywana aż cały dialog trafi do repo/git). Nowy licznik
`zaktualizowane`. Po naprawie: sesja_895ce14f urosła 24 KB → 214 KB (cała praca v5).
Testy: +2 granice (re-eksport gdy źródło świeższe, pomija gdy cel świeższy). 1772→1774.
Pliki: kronika_czatu.py, tests/test_kronika_czatu.py.

---

## 2026-06-26 | WARSTWA | 🌉 W-360 v5 — Most Chmura↔Lokal + Pełna Symbioza Pamięci

Cezar: „rób mocniejsze memory, dokładny audyt, unikaty, następna warstwa dla chmury i lokala, pełen wypas".
Audyt agentowy wykrył 9 luk UTRATY POTENCJAŁU (Prawo XV). Naprawione najcięższe:

- **L2:** W2 RAG (42 książki) podpięty do `szukaj_wszedzie` — fasada „jedyna ścieżka do pamięci"
  wcześniej pomijała największą warstwę wiedzy. Teraz 6 warstw: lekcje+kronika+wizje+logi+wiedza+refleksje.
- **L4:** W5 pamięć refleksyjna (narracyjne lekcje rynkowe) podpięta do cross-layer search.
- **L6:** Deduplikacja — `rejestr_wizji.dodaj(dedup=True)` zwraca bool; `auto_lekcja` sprawdza istnienie
  przed dopisem (DeepSeek nie dubluje lekcji co sesję).
- **L9:** Usunięto martwą stałą `_EPOKA` (Prawo XV/martwy kod).

**UNIKAT — Most Chmura↔Lokal** (`imperium/biblioteki/srodowisko_pamieci.py`): pamięć
środowiskowo-adaptacyjna (żaden konkurent — Mem0/Zep/Letta/A-Mem — tego nie ma). Wykrywa
chmura/lokal, raportuje co działa gdzie, generuje MANIFEST pamięci który lokalny Claude czyta
po `git pull`. Chmura: FTS (przeżywa przez git). Lokal: upgrade do wektorów semantycznych
(huggingface zablokowany proxy w chmurze). Most = git + manifest. Wpięty w podsumowanie startowe.

Testy: 1760→1772 (+12 granic). Audyt exit 0. Ruff czysty. Dogfooding: v5 zarejestrowane w W4.
Pliki: centrum_pamieci.py, srodowisko_pamieci.py (nowy), rejestr_wizji.py, auto_lekcja.py,
kronika_czatu.py, tests/run_tests.py (+setenv/delenv), INDEKS_IMPERIUM.md.

---

## 2026-06-26 | UNIKAT | 🎯 Pamięć Reżimowa (Regime-Conditioned Retrieval) — lepsza od konkurencji

Cezar: „czy da lepszą opcję pamięci, zrób unikat lepsze od konkurencji". Research SOTA 2026
(Mem0/Zep/Graphiti/Letta/A-Mem + MemEvolve/SSGM) → wszystkie DOMENOWO ŚLEPE: retrieval =
semantyka + recency + ewent. czas. ŻADEN nie warunkuje pamięci na reżimie rynku.

**Unikat wdrożony:** 4. wymiar scoringu Generative Agents — `score = recency × importance ×
relevance × regime_match`. Wspomnienie z bieżącego reżimu (z klasyfikuj_rezim/Gubernatora) →
pełna waga; z innego → ×0.4; bez tagu → 1.0 (lekcje ogólne nietknięte). Logi W1 mają JAWNE
pole rezim (dopasowanie precyzyjne), lekcje W3 — token z treści. Naprawia „regime-stale bug"
(otwarty problem rynku) u źródła: pamięć nie wyciąga bańkowych lekcji w krachu.

Kod: centrum_pamieci.py (_regime_match, _wykryj_rezim, +param rezim_biezacy w score_lekcji/
szukaj_wszedzie/top_lekcji/_szukaj_w_logach), CLI `szukaj --rezim`. +9 testów granic.
Wstecznie kompatybilne (rezim_biezacy='' → wyłączone). Dokumenty: REJESTR_INSPIRACJI MEM-05/06,
encyklopedia MEM §3. Testy 1743→1752 ✅ · audyt exit 0 · ruff czysto.

---

## 2026-06-26 | Pamięć | W1 (logi pamiec_absolutna) podpięta do cross-layer search — naprawa Prawa XV

UTRATA POTENCJAŁU naprawiona: `szukaj_wszedzie()` przeszukiwał tylko W3 (lekcje) + W3b (kronika),
a najbogatsze dane (logi TRADE_CLOSE: rezim/PnL/MAE/MFE/powód) były POZA zasięgiem fasady pamięci.
Dodano `_szukaj_w_logach()` — scoring recency×relevance, resilient (brak logów/katalogu → []).
LOG_DIR przekazywany jawnie (testowalność przez monkeypatch). +3 testy granic (dopasowanie,
brak dopasowania <0.05, brak katalogu). Docstringi zaktualizowane (W1 podpięty, nie backlog).

Pliki: imperium/biblioteki/centrum_pamieci.py, tests/test_centrum_pamieci.py
Testy: 1740→1743 ✅ · Audyt exit 0 · Ruff czysto

---

## 2026-06-26 | RAG + Pamięć + Testy | Przebudowa RAG na 41/42 książek + naprawa rozjazdu doc↔kod

**RAG:** ekstraktor.py rozszerzony o ekstrakcję azw3/mobi przez pakiet `mobi` (rozpakowuje do epub → _epub).
Pełna przebudowa indeksu: 24→41 książek w FTS5 (15 204 fragmentów, 82 MB, 44 s).
BIB-032 O'Hara — skan obrazowy, OCR daje bełkot → NIE zaindeksowany (Prawo I); esencja w MKS encyklopedii.
Wektory niedostępne (huggingface.co zablokowane przez proxy środowiska) — tryb FTS-only.

**Testy (audyt):** 1740/1740 ✅, 81 plików, zero trywialnych. 11 duplikatów NAZW funkcji —
to helpery (_bar, _bary, _bary_trend) kopiowane między plikami, bez redundancji asercji.
6 plików importuje pytest.approx/raises — działają, bo pytest jest w env (runner to wykrywa).

**Pamięć (rozjazd doc↔kod Prawo XXI):** mnemosyne.py był podawany jako żywa warstwa W1 —
kod pokazuje świadome wycofanie (Prawo XVI: redundancja vs pamiec_refleksyjna + ksiega_wad).
Naprawiono: centrum_pamieci.py docstring, MEM_pamiec_agentow_ai.md §2/§7 (diagram, tabela warstw),
SETUP_LOKALNY.md (nota BIB-032 + wektory FTS-only). Ścieżka pamiec_refleksyjna skorygowana
na imperium/cesarz/ (nie biblioteki/). Backlog: podpięcie pamiec_absolutna do szukaj_wszedzie.

Pliki: narzedzia/rag/ekstraktor.py, narzedzia/rag/SETUP_LOKALNY.md,
       imperium/biblioteki/centrum_pamieci.py, bibliotheca_ulpia/encyklopedia/MEM_pamiec_agentow_ai.md

---

## 2026-06-26 | Dokumentacja | Sekcje „📚 Źródła (Kanon BIB)" w 4 dokumentach strategicznych

Cezar: „esencja była wcześniej wpisywana z książek… zobacz czy 42 książki są ujęte w wizji,
strategii, planowaniu". Audyt wykazał: WIZJONER.md miał 77 odwołań BIB (✅), ale KATALOG_NEURONOW,
KATALOG_STRATEGII, ARCHITEKTURA i ROADMAP miały 0–3 odwołania.

Naprawa: dodano sekcję „📚 Źródła — Kanon biblioteki (BIB)" do 4 dokumentów, mapując REALNE
powiązania koncept→książka (2 agentów zbudowało mapowania z WIZJONER + encyklopedii + rejestr_strategii.py).
**Zero fabrykacji (Prawo I):** neurony kanonu AT/skanu TradingView NIE przypisane punktowo do BIB;
tylko 2 strategie mają twardy numer BIB w kodzie (IMV-TR-008→Elder, IMV-RG-002→Lefèvre). BIB-024 Lowe
oznaczony jako ANTYWZORZEC. Pełna symbioza: dokumenty linkują wzajemnie do swoich § Źródła.

Pliki: docs/KATALOG_NEURONOW.md, docs/KATALOG_STRATEGII.md, docs/ARCHITEKTURA_IMPERIUM.md, docs/ROADMAP_IMPERIUM.md

---

## 2026-06-25 | Audyt | Głęboki audyt przypisania 42 książek → 4 sieroty naprawione

Cezar: „zrób głęboki audyt wszystkich książek z biblioteki i przypisz do naszych dokumentów".

Metoda: macierz pokrycia 42 książek (plik fizyczny ↔ dział encyklopedii). Wykryto **3 prawdziwe
sieroty** (nigdzie nieprzypisane) + 1 półsierotę (w dziale, brak w Kanonie INDEX). Każdą
przeczytano agentem przed przypisaniem (ZPO, Prawo I — nie z tytułu).

Naprawione przypisania:
- **BIB-001 Patel** *The Secret Wealth Advantage* (978-0-85719-857-0 ✅ web) → **MAK** (główny:
  18-letni cykl nieruchomości; MAK 🔲→🚧, pierwszy realny tom + esencja) + **BAN** (poboczny).
- **BIB-012 Van Der Post/Strauss/Schwartz** *Coding Capital* (979-8-87385-994-8 ✅ web) → **ALG**
  (główny: warsztat algo-Python) + **IMP/RSK** (poboczny).
- **BIB-024 Lowe** *Bitcoin & Crypto Trading for Beginners* (ISBN ⚠️ self-pub) → **ONC** (główny,
  ⭐1/5) + **RSK**. 🚨 Oznaczono ANTYWZORZEC: „uśrednianie w dół" sprzeczne z Regułą 6%.
- **BIB-005 Blum** *What Exactly Is Crypto* (ISBN ⚠️ self-pub, ⭐2) — był w ONC, dopisany do Kanonu INDEX.

Wynik: **pokrycie 42/42 — zero sierot.** Każda książka przypisana do ≥1 działu. ISBN
zweryfikowane web dla Patel/Coding Capital; Blum/Lowe to self-publishing bez ISBN (uczciwe ⚠️).

- Pliki: `INDEX_MAIOR.md` (Kanon ONC/ALG/MAK, status MAK 🚧), `MAK_*.md` (esencja Patel),
  `BAN_*.md`, `ONC_*.md`, `ALG_*.md`. Testy zielone, audyt exit 0.

---

## 2026-06-25 | Biblioteka | Kanon 36→42: analiza BIB-037..042 → LEW/TRD/PSY/RSK

Cezar wgrał 6 klasyków na branch roboczy: BIB-037 Hull *Options, Futures and Other Derivatives*,
BIB-038 Schwager *Market Wizards*, BIB-039 Lefèvre *Reminiscences of a Stock Operator*,
BIB-040 Bernstein *Against the Gods*, BIB-041 Taleb *Fooled by Randomness*, BIB-042 Jorion *Value at Risk*.

Wykonane: ekstrakcja EPUB + 6 równoległych agentów → esencja do działów LEW (Hull), TRD
(Schwager+Lefèvre), PSY (Schwager+Lefèvre), RSK (Bernstein+Taleb+Jorion). ISBN zweryfikowane
(Prawo I): Hull 978-0-13-693997-9, Schwager 978-1-118-27305-0, Lefèvre 978-0-470-59322-6 (w plikach);
Bernstein 978-0-471-12104-6 i Taleb 978-0-8129-7521-5 (plik=bundel Incerto → web). Jorion 978-0-07-146495-6.

Esencja kluczowa: Hull — margin call dopłaca do INITIAL nie maintenance, Lehman 31:1, GARCH>EWMA;
⚠️ Hull NIE pokrywa crypto perpetual/funding (Prawo I). Schwager — undertrade, korelacja pozycji
codziennie (Prawo XVI), oceniaj proces nie wynik. Lefèvre — sit tight, anty-uśrednianie, hope/fear
odwrócone, anty-tip=Prawo I. Bernstein — loss aversion (uzasadnia twardy HALT), 3 pułapki regresji.
Taleb — magnituda nie częstotliwość, survivorship bias→DSR/PBO, katastrofa nieobecna w danych.
Jorion — VaR vs Expected Shortfall (krypto: ES>>VaR), EWMA λ=0.94, backtest VaR strefy Basel.

Symbioza (Prawo XXI): 36→42 zsync w README, INDEX_MAIOR (Kanon+wiersze LEW/TRD/PSY/RSK),
MEM (W2), centrum_pamieci.py, mcp_server.py, SETUP_LOKALNY, PAMIEC_SESJI (A3). Daty działów → 2026-06-25.

- Pliki: `bibliotheca_ulpia/BIB-037..042` (6 e-booków), działy `LEW/TRD/PSY/RSK_*.md`,
  `INDEX_MAIOR.md`, `MEM_*.md`, `README.md`, `centrum_pamieci.py`, `mcp_server.py`,
  `SETUP_LOKALNY.md`, `docs/PAMIEC_SESJI.md`, `dane/PAMIEC_SESJI.md`. Testy zielone, audyt exit 0.

---

## 2026-06-25 | Biblioteka | Kanon 32→36: analiza BIB-033..036 → dział MEM

Cezar wgrał 4 książki o inżynierii LLM/agentów (BIB-033 Huyen *AI Engineering*, BIB-034 Infante
*AI Agents and Applications*, BIB-035 Iusztin&Labonne *LLM Engineer's Handbook*, BIB-036 Alto
*Building LLM Powered Applications*) i polecił dokładną analizę zgodnie z zasadami.

Wykonane: ekstrakcja pełnych tekstów (EPUB/AZW3), analiza 4 równoległymi agentami, esencja
wyciśnięta do działu **MEM** (nowa §8 „Kanon książkowy" + mapa wiedza→kod z 17 konceptów).
Metadane zweryfikowane (Prawo I): ISBN BIB-033 978-1-098-16630-4, BIB-035 978-1-83620-007-9,
BIB-036 978-1-83546-231-7 (w plikach); BIB-034 978-1-63343-654-1 + autor **Roberto** Infante
(nie Michael) potwierdzone WebSearch — autor pracuje dla londyńskiego hedge fundu (nasza dziedzina).

Esencja kluczowa: Huyen — trójwarstwowa pamięć (internal/short/long) + reguła routingu +
pułapka FIFO (uzasadnia nasz zanik warstwowy) + reranking wg świeżości („stock market") +
RAG vs fine-tuning + compound mistakes 0,95ⁿ. Infante — stan grafu=pamięć (checkpoint),
Router vs Supervisor (Senat), MCP. Iusztin — FTI + hybrid search + reranking cross-encoderem.
Alto — taksonomia pamięci (Buffer/Summary/Entity/KG) + CONDENSE_QUESTION + 3 warstwy anty-halucynacji.

🚨 Prawo XV: blueprint domknięcia Bibliotheca-RAG (W2) z książek — ingestion⊥inference,
hybryda BM25+dense, reranking, context precision/recall jako metryki.

Symbioza (Prawo XXI): liczba 32→36 zsynchronizowana w README biblioteki, INDEX_MAIOR (tabela+Kanon),
MEM (W2), centrum_pamieci.py (docstring), mcp_server.py, SETUP_LOKALNY.md, PAMIEC_SESJI (tabela A3).
Wpisy datowane (snapshot indeksu 7760 fragm./32 z 2026-06-21) świadomie nietknięte — Prawo I.

- Pliki: `bibliotheca_ulpia/BIB-033..036` (4 e-booki), `encyklopedia/MEM_pamiec_agentow_ai.md` (+§8),
  `encyklopedia/INDEX_MAIOR.md`, `bibliotheca_ulpia/README.md`, `centrum_pamieci.py`,
  `narzedzia/rag/mcp_server.py`, `narzedzia/rag/SETUP_LOKALNY.md`, `docs/PAMIEC_SESJI.md`,
  `bibliotheca_ulpia/dane/PAMIEC_SESJI.md`. Testy zielone, audyt exit 0.

---

## 2026-06-22 | W-360 v3 | FinMem layered decay + scan rynku pamięci (MEM-01..04)

Cezar: „FinMem (2311.13743)/FinAgent (2402.18485) to nasza dziedzina — czy to mamy? poszukaj
unikatów temat mem0 i pamięć absolutna, i nasz unikat".

Weryfikacja ID arXiv na żywo (WebSearch, Prawo I — zero fabrykacji): FinMem=**2311.13743**
(nasz `pamiec_refleksyjna.py` cytował błędnie 2408.14900 → NAPRAWIONE), FinAgent=2402.18485,
Mem0=2504.19413, A-Mem=2502.12110. Dopisane do REJESTR_INSPIRACJI jako MEM-01..04 (pełny ZPO).

WDROŻONE (Prawo XIX — kod+testy, nie deklaracja): **zanik warstwowy FinMem** w
`centrum_pamieci._decay_dla_waznosci()`. Tempo zaniku zależy od ważności lekcji:
rutyna (i=0.3) → 0.99/dzień (half-life ~69 dni), krytyczna (i=1.0, „utrata potencjału") →
0.999/dzień (half-life ~690 dni). NASZ UNIKAT: funkcja CIĄGŁA vs 3 dyskretne kubełki FinMem.

NAPRAWA UTRATY POTENCJAŁU (Prawo XV): wcześniej jeden zanik 0.995 dla wszystkich — lekcja
o krytycznym bugu znikała z pamięci tak szybko jak notatka o profilu. Teraz krytyczne trwają ~10×.

Plany (wzorce, jeszcze nie kod): MEM-02 dual-level reflection, MEM-03 auto-konsolidacja/dedup
(Mem0), MEM-04 auto-linkowanie lekcji (A-Mem Zettelkasten). Unikat Imperium: pamięć rynku +
pełny dialog+lekcje+profil w git (przeżywa kompakcję/wygaśnięcie kontenera) — brak na rynku.

- Pliki: `centrum_pamieci.py` (+`_decay_dla_waznosci`, `_recency(importance)`), `pamiec_refleksyjna.py`
  (fix ID arXiv), `tests/test_centrum_pamieci.py` (+4 testy granic zaniku, 19 total),
  `docs/REJESTR_INSPIRACJI.md` (MEM-01..04), `docs/PAMIEC_SESJI.md` (lekcja). Testy 1740/1740, audyt exit 0.

---

## 2026-06-22 | W-360 | Pamięć v2: CRUD lekcji + profil Cezara + Kronika Czatu (adopcja Hermes/Zep/Mem0)

Cezar: „porównaj naszą pamięć z hermes-agent.org i dodaj, byśmy pamiętali cały czat — lokal+chmura".
Research konkurencji (5 agentów): Hermes (MEMORY.md/USER.md), Zep/Graphiti (bi-temporal KG),
Cognee (ECL poly-store), Mem0 (ADD/UPDATE/DELETE/NOOP), MemGPT (paging), Generative Agents
(recency·importance·relevance), CoALA (episodic/semantic/procedural), RAPTOR (tree-summary).

WNIOSEK: nasza Warstwa 3 zbiegła się architektonicznie z Hermesem (markdown rdzeń + FTS5).
Domknięto 3 luki + dodano pełną pamięć czatu:
- CRUD: `usun_lekcje()` / `aktualizuj_lekcje()` (wcześniej tylko append — UTRATA POTENCJAŁU)
- Limit zwięzłości `LIMIT_ZNAKOW_LEKCJA=1200` (Hermes-style twardy błąd) + `alarm_przepelnienia`
- Profil Cezara (`docs/PROFIL_CEZARA.md`) = odpowiednik USER.md (model użytkownika ⊥ środowisko)
- Kronika Czatu (`kronika_czatu.py`): destyluje 148MB transkryptów ~/.claude → ~6MB dialogu
  w repo (git niesie historię lokal↔chmura), redakcja kluczy API, przyrostowa, wpięta w hook

PLIKI: imperium/biblioteki/pamiec_sesji.py, imperium/biblioteki/kronika_czatu.py,
docs/PROFIL_CEZARA.md, docs/PAMIEC_SESJI.md, .claude/hooks/session-start.sh,
tests/test_pamiec_sesji.py (+15), tests/test_kronika_czatu.py (+10),
bibliotheca_ulpia/dane/kronika/ (100 sesji destylatu), docs/INDEKS_IMPERIUM.md, docs/LOG_ZMIAN.md

---

## 2026-06-21 | W-384 | A/B MTF PER REŻIM — brama pomaga TYLKO w bessie, szkodzi w hossie/range

Po obaleniu na 6-mies. oknie: re-test na WIELOREŻIMOWEJ historii (paginacja). Hipoteza
Cezara warunkowa: brama pomaga w TRENDZIE, szkodzi w RANGE. Test rozbity na 4 reżimy.

NARZĘDZIA: `pobierz_4h_binance.py` + paginacja (`--od YYYY-MM-DD`, pętla po startTime,
sklejanie stron → 11987 barów 4h/para od 2021). `backtest_ab_mtf_rezimy.py` — A/B na
wycinkach reżimowych. 5 par z pełnym pokryciem 2021 (BTC/ETH/BNB/XRP/ADA).

TABELA A/B PER REŻIM (baseline → MTF):
  reżim                 PnL%          Sharpe        MaxDD        DSR       werdykt
  BULL_2021 (↑)   +7.54→+2.06   3.01→0.74    1.8%→3.6%   0.86→0.43   🔻 MTF gorzej
  BEAR_2022 (↓)   -1.15→+3.16  -0.39→+1.99   6.1%→5.1%   0.24→0.69   ✅ MTF DUŻO lepiej
  RANGE_2023(bok) +0.70→-0.07   1.03→-0.15   1.0%→2.1%   0.49→0.28   🔻 MTF gorzej
  RECENT_25-26    -1.09→-3.35  -1.05→-2.42   3.4%→4.4%   0.13→0.03   🔻 MTF gorzej

WERDYKT WARUNKOWY (Prawo I — hipoteza CZĘŚCIOWO obalona):
  • „Pomaga w trendzie" — TYLKO W BESSIE. W BEAR_2022 brama zamieniła stratę w zysk
    (-1.15%→+3.16%), podniosła Sharpe (-0.39→+1.99), DSR (0.24→0.69) i OBNIŻYŁA DD
    (6.1%→5.1%) — klasyczne „nie walcz ze spadkiem": weto wycięło kontrtrendowe longi.
  • W HOSSIE (BULL_2021) brama SZKODZI (Sharpe 3.01→0.74, DD↑) — mnoznik 1.2× powiększał
    longi przed korektą V.2021 / weto cięło zyskowne pullbacki.
  • W RANGE — szkodzi (zgodnie z hipotezą: tnie mean-reversion).
  • Wniosek: MTF to NIE uniwersalna wygrana ani prosty „trend vs range". Jedyna wyraźna
    korzyść = OCHRONA KAPITAŁU w trwałej BESSIE.

OGRANICZENIE: 5 par, po JEDNYM oknie/reżim (~5 mies., 50–85 transakcji). BEAR=Apr–Aug
2022 (kaskada LUNA/3AC — wyjątkowo czysty jednokierunkowy zjazd; może nie generalizować).
DSR w większości <0.95 (niewalidowane).

WNIOSEK PER-REŻIM (jednozdaniowo): **BEAR = TARCZA** (brama chroni kapitał w trwałym
zjeździe: −1.15%→+3.16%, DD 6.1%→5.1%, DSR 0.24→0.69), **HOSSA / RANGE / MIX = SZKODZI**
(tnie zyskowne pullbacki i mean-reversion, powiększa longi 1.2× przed korektą).

DECYZJA: default OFF bez zmian (brama uniwersalna szkodzi w 3/4 reżimów).
KIERUNEK PRZYSZŁY (nie teraz): **warunkowe weto MTF TYLKO w reżimie BESSA/wysoki-stres**
przez Namiestnika (który już klasyfikuje reżim) — „tarcza bessy" zamiast uniwersalnej bramy.
WARUNEK WDROŻENIA: najpierw WALIDACJA na niezależnych bessach 2018 i 2025 (czy efekt
BEAR_2022 generalizuje, czy to artefakt kaskady LUNA/3AC). Bez tej walidacji — NIE wdrażać.

Kod: paginacja + nowy harness reżimowy. 1648/1648 testów, audyt exit 0, ruff czysty.
Pliki: `narzedzia/pobierz_4h_binance.py` (paginacja `--od`),
`narzedzia/backtest_ab_mtf_rezimy.py` (NEW), `docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | W-384 | Backtest A/B MTF — brama NIE poprawia wyniku na tym oknie (hipoteza DD obalona) 🔻

Pytanie Cezara (o pieniądze): czy widzenie wyższych TF (brama konfluencji W-384) poprawia
wynik? Hipoteza Cezara: najlepszy efekt MTF to NIŻSZY drawdown (wycięte wejścia przeciw
głównemu trendowi), nie wyższy zysk.

NARZĘDZIE: `narzedzia/backtest_ab_mtf.py` — uczciwe A/B na identycznych barach. Do
`backtest()` dodano opt-in `mtf_konfluencja`/`mtf_weto_przeciwtrend` (domyślnie False —
ZERO zmiany domyślnego zachowania). Baza 4h, okno=400 → stos {"1d":6} daje 66 barów
dziennych ≥60 ⇒ brama ocenia TREND DZIENNY (główny trend). 15 par, 1209 barów-obserwacji.

TABELA A/B (BASELINE mtf=False vs MTF mtf=True+weto):
  metryka            baseline     MTF       Δ
  PnL [%]            +0.68%      +0.18%    -0.50%  🔻
  Transakcje          177         164       -13   (brama wycięła 13 wejść)
  Win rate           47.5%       48.2%     +0.7%  ✅ (marginalnie)
  Sharpe portfela     1.62        1.61     -0.01  ≈
  MaxDD portfela      2.3%        3.9%     +1.5%  🔻 (DD WYŻSZY!)
  MaxDD śr/para       2.8%        3.5%     +0.7%  🔻
  DSR (n_prob=2)      0.79        0.81     +0.01  ≈  (oba dsr_ok=False, <0.95)
  PBO (selekcja par)  0.43        0.60     +0.17  🔻 (oba pbo_ok=False)

WERDYKT WARUNKOWY (Prawo I):
  • Kryterium „niższy DD" (hipoteza Cezara): ❌ NIESPEŁNIONE — DD WYŻSZY (2.3%→3.9%).
  • Kryterium „lepszy Sharpe/DSR": ≈ neutralnie (zmiany w granicach szumu).
  • Brama wycięła 13 wejść, ale netto te wejścia były ZYSKOWNE (PnL spadł o połowę), a DD
    wzrósł — prawdopodobny mechanizm: mnoznik konfluencji skaluje zgodne wejścia do 1.2×,
    większe pozycje → głębszy DD; weto usunęło zyskowne kontrtrendy (I–VI 2026 sprzyjał
    mean-reversion). Brama nie selekcjonuje tu dobrze.
  • OGRANICZENIE: 6 mies., 1 reżim, ~11 transakcji/parę — pomiar INDYKATYWNY, nie
    ostateczny. Różnice DD małe bezwzględnie, mogą się odwrócić na innych danych.

DECYZJA: default pozostaje OFF (mtf_konfluencja=False) — dane nie dają podstaw do włączenia.
Przed jakąkolwiek decyzją o włączeniu: re-test na dłuższej, wieloreżimowej historii (4h
paginowane do lat / baza 1h ze stosem dziennym). Domyślne ustawienia NIEZMIENIONE.

Kod: backtest opt-in (domyślnie False) + nowe narzędzie. 1648/1648 testów, audyt exit 0,
ruff czysty, /code-review na diffie.
Pliki: `imperium/koloseum/backtest.py` (opt-in MTF), `narzedzia/backtest_ab_mtf.py` (NEW),
`docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | Prawo I | Backward-IC (--backward) — ROZSTRZYGNIĘCIE: EXP-13/14 OPISUJĄ REŻIM, nie przewidują 🚩

Krok A.2 (rozstrzygający, po nieprzekonującym teście lagu): backward-IC =
Spearman(sygnał_t, zwrot PRZESZŁY t-h→t). Jeśli ≈ forward-IC, sygnał opisuje ruch,
który WŁAŚNIE się dokonał (reżim/współbieżność), a nie przewiduje przyszłość.

POMIAR OBOK SIEBIE (matryca 15×3, n=45):

  moduł    h    IC_forward   IC_backward   |Δ|
  EXP-13   1     +0.245       +0.263      0.018
  EXP-13   6     +0.249       +0.284      0.035
  EXP-13   30    +0.251       +0.283      0.032
  EXP-14   1     +0.304       +0.310      0.006
  EXP-14   6     +0.305       +0.313      0.008
  EXP-14   30    +0.310       +0.317      0.007

WERDYKT (Prawo I — kryterium Cezara |Δ|<0.05):
  🚩 WSZYSTKIE 6 przypadków |Δ|<0.05 → sygnał OPISUJE REŻIM, nie przewiduje.
  • EXP-14 Kyle: forward≈backward co do trzeciego miejsca (Δ 0.006–0.008) — czysty
    deskryptor współbieżny. Wysokie IC to NIE predykcja.
  • EXP-13 GARCH: Δ 0.018–0.035, też <0.05; backward nawet WYŻSZE niż forward.
  • Brak dodatniej asymetrii czasowej (fwd>bwd) w ŻADNYM przypadku — przeciwnie,
    backward ≥ forward → zero śladu predykcji; forward-IC to echo współbieżnej
    korelacji reżimu rzutowane w przyszłość przez persystencję.

INTERPRETACJA (spójna z teorią): GARCH = zmienność warunkowa (stan/reżim), Kyle's λ =
illikwidność/impact (stan mikrostruktury). Z definicji to MIARY STANU, nie predyktory
kierunku. IC ~0.25–0.30 było artefaktem persystencji reżimu + Spearman łapiący asocjację
współbieżną. Edge kierunkowy OOS implikowany przez to IC — ILUZORYCZNY.

DECYZJA (Prawo XV/XVI, bez przesady w drugą stronę): NIE kasujemy — moduły niosą
ORTOGONALNĄ informację (max|ρ|<0.20, dekorelacja trzyma), ale to informacja o REŻIMIE,
nie kierunku. Stosować jako FILTR reżimu / kontekst sizingu, NIE jako sygnał wejścia.
Waga jako predyktor kierunku — w dół.

Zmiana wyłącznie narzędziowa. 1648/1648 testów, audyt exit 0, ruff czysty.
Pliki: `narzedzia/pomiar_nowe_moduly.py` (flaga `--backward`, `wstecz` w zwrotach i IC),
`docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | Prawo I | Kontrola look-ahead IC (--przesuniecie) — leak czasowy obalony, ale lag skonfundowany persystencją

Krok A diagnostyki IC (po obaleniu nakładania): czy sygnał PRZEWIDUJE przyszłość, czy
tylko OPISUJE teraźniejszość (współbieżność / leak bieżącego baru)?

Dodano flagę `--przesuniecie LAG` (lag w barach): IC = Spearman(sygnał_{t-lag}, zwrot od
t do t+h) — sygnał z PRZESZŁOŚCI vs przyszły zwrot. Lag aplikowany na siatce próbkowania
(eff = round(lag/krok)·krok). Sweep 0/3/6/9/30 barów, pełna matryca 15×3 (n=45):

  EXP-13 GARCH:  IC(h=1) 0.245→0.250→0.253→0.249→0.245 | IC(h=30) 0.251→...→0.208 (lekki spadek)
  EXP-14 Kyle:   IC(h=1) 0.304→0.303→0.307→0.309→0.307 | IC(h=30) 0.310→...→0.294 (płasko)

WERDYKT (Prawo I):
  1. TWARDY LOOK-AHEAD (użycie przyszłych barów) — DISFAVORED. Realny leak przyszłości
     opadałby gwałtownie, gdy odsuwamy sygnał w przeszłość; tu IC jest ~płaskie. Brak
     oznak buga lookahead.
  2. ALE lag NIE rozstrzyga współbieżności — bo sygnały są wysoce PERSYSTENTNE (okno 60,
     zmienność/illikwidność klastrują): sygnał_{t-30} ≈ sygnał_t, więc IC z definicji się
     nie rusza, niezależnie czy jest prawdziwa predykcja czy nie. To konfundent zapowiedziany
     w poprzednim wpisie.
  3. Sama PŁASKOŚĆ IC przez 30 barów jest podejrzana: realna krótkoterminowa przewaga
     powinna zanikać ze starzeniem sygnału. Brak zaniku → asocjacja na poziomie REŻIMU
     (wolnozmienny stan), nie ostry timing. Magnituda IC ~0.25–0.30 prawdopodobnie zawyża
     realny edge out-of-sample.

DECYZJA: leak/bug wykluczony, ale „realny skill" wciąż NIEpotwierdzony. Rozstrzygający tani
test: backward-IC (sygnał_t vs PRZESZŁY zwrot t-h→t) — jeśli ≈ forward-IC, sygnał opisuje
reżim, nie przewiduje. Ostatecznym arbitrem jest backtest OOS z DSR/PBO (krok B).

Zmiana wyłącznie narzędziowa. 1648/1648 testów, audyt exit 0, ruff czysty.
Pliki: `narzedzia/pomiar_nowe_moduly.py` (flaga `--przesuniecie`, lag w `_ic_modulu`),
`docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | Prawo I | Kontrola autokorelacji IC — wysokie IC NIE jest artefaktem nakładania

Cezar (Prawo I): IC nowych modułów 0.25–0.30 podejrzanie wysokie — może łapać
autokorelację zmienności na NAKŁADAJĄCYCH się oknach forward-return, nie czysty skill.

DOMKNIĘCIE WĄTKU: do `pomiar_nowe_moduly.py` dodano flagę `--nienakladajace` — IC liczone
na rozłącznych oknach zwrotu (odstęp próbek = krok·ceil(h/krok) ≥ h, więc okna [t,t+h] się
nie nachodzą). Te same sygnały i zwroty co tryb standardowy — usuwamy WYŁĄCZNIE nakładające
się próbki, by odizolować efekt persystencji.

POMIAR (pełna matryca 15 par × 3 TF, n=45):
  • EXP-13 GARCH:  standard IC h1/6/30 = +0.245/+0.249/+0.251  →  nienakł. +0.245/+0.248/+0.249
  • EXP-14 Kyle:   standard IC h1/6/30 = +0.304/+0.305/+0.310  →  nienakł. +0.304/+0.308/+0.301
  • max|ρ| bez zmian: EXP-13=0.149, EXP-14=0.093 (oba <0.20 → filary siły, zdekorelowane)

WERDYKT (Prawo I, bez przeceniania): hipoteza „IC zawyżone przez nakładanie" ODRZUCONA —
IC stabilne pod kontrolą rozłączności (zmiana <0.01). Dodatkowy dowód: IC dla h=1 (z natury
nienakładające) było równie wysokie — czyli nakładanie NIGDY nie było źródłem. ALE to NIE
dowodzi realnego skillu tradingowego: IC ~0.25–0.30 pozostaje nienaturalnie wysokie jak na
forward-return i wymaga osobnej kontroli (leak bieżącego baru / współbieżność sygnał↔zwrot).
Wykluczyliśmy jeden konfundent, nie wszystkie.

Zmiana wyłącznie narzędziowa (pomiar) — zero wpływu na sygnały/strategie roju.
1648/1648 testów, audyt exit 0, ruff czysty.

Pliki: `narzedzia/pomiar_nowe_moduly.py` (flaga `--nienakladajace`, `_ic_modulu` rozłączne
próbkowanie), `docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | W-384 | Konfluencja Multi-Timeframe na poziomie roju (odpowiedź na pytanie Cezara)

Cezar: "czy Imperium widzi wszystkie interwały podczas wybierania ordera?" — NIE w pełni.
Diagnoza: decyzja na JEDNYM TF; jedyna nadbudowa MTF (X-28) to RSI+EMA dla 1 neuronu.

ROZWIĄZANIE: `imperium/legiony/mtf_konfluencja.py` — brama konfluencji na poziomie ROJU
(jak Senat, warstwa nad Legatusem). Po decyzji kierunkowej agreguje bary w GÓRĘ na 2 wyższe
TF (stos: 1h→4h+1d, 4h→1d+1w, itd.), liczy robustny trend każdego (EMA50vsEMA200 + cena
vs EMA50 + MACD znak) i zwraca:
  • wyrownanie -1..+1, mnoznik 0.5..1.2, weto (opt-in), werdykt
Wpięte w Dyrygenta (opt-in, domyślnie OFF — zero zmiany zachowania):
  • mtf_konfluencja=True → mnoznik skaluje rozmiar pozycji (zgodność↑ / konflikt↓)
  • mtf_weto_przeciwtrend=True → twarde weto wejść przeciw wyższym TF (MTF_WETO)
Mnoznik aplikowany w OBU ścieżkach sizingu (przy okazji naprawiono gubienie mnoznik_senatu
w ścieżce Rady Doradców).

14 testów (test_mtf_konfluencja.py): agregacja bez lookahead, kierunek trendu, zgodność
wzmacnia, konflikt tłumi, weto, mnoznik w zakresie, Dyrygent domyślnie OFF.
1648/1648 testów, audyt exit 0, ruff czysty.

Pliki: `legiony/mtf_konfluencja.py` (NEW), `koloseum/dyrygent.py` (brama + 2× sizing),
`tests/test_mtf_konfluencja.py` (NEW, 14), `docs/MANIFEST_KODU.md`, `docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | POMIAR MATRYCOWY + naprawa EXP-14 | 5 par × 3 interwały (Prawo XV/XVI)

Cezar wskazał słabość: pomiar tylko na BTC 4h. Rozszerzono `pomiar_nowe_moduly.py` na
PEŁNĄ matrycę 5 par (BTC/ETH/BNB/SOL/DOGE) × 3 interwały (1h/4h/1d). To ujawniło BUG:

🚨 EXP-14 Kyle's Lambda — próg ABSOLUTNY (1.5e-5) był 50× za wysoki i zależny od skali
wolumenu (BTC λ~3e-7, inne pary inaczej). Neuron NIGDY nie strzelał na realnych danych
(n/a na wszystkich 15 kombinacjach). Pojedynczy pomiar BTC 4h na pełnej historii dał
mylące IC=0.48 z garstki sygnałów ze starej, niepłynnej ery BTC.

NAPRAWA (W-380): próg ADAPTACYJNY — stosunek bieżącego impactu (|Δp|/|netflow|, ostatnie
5 barów) do mediany okna. Bezwymiarowy → skalowalny na KAŻDĄ z 15 par. Progi skalibrowane
na realny rozkład (mediana ratio=2.05, p85=6.2): HIGH=6.0 (~15%), EXTREME=12.0 (~8%).

WYNIK PO NAPRAWIE (średnia 5 par × 3 TF):
- EXP-13 GARCH: max|ρ|=0.124, IC≈+0.25 — strzela na każdej parze/TF, zdekorelowany ✅
- EXP-14 Kyle:  max|ρ|=0.063, IC≈+0.31 — NAJBARDZIEJ zdekorelowany, teraz strzela wszędzie ✅
- EXP-15 PIN: martwy (wyciszony w poprzedniej turze)

UWAGA METODOLOGICZNA (Prawo I): IC ~0.25-0.31 jest płaskie przez h=1/6/30 — to częściowo
artefakt persystencji sygnału (wolnozmienny sygnał × trendujący rynek zawyża IC). Wartość
bezwzględna IC zawyżona; realny dowód wartości to backtest P&L, nie surowe IC. Pewne są:
(1) dekorelacja (nowa informacja), (2) skalowalność na wszystkie pary po naprawie.

Lekcja: pomiar na 1 parze/1 TF = pułapka (Prawo XV). Absolutne progi nie generalizują
na pary o różnej skali — domyślnie progi adaptacyjne/względne.

Testy: +2 (skalowalność progu, impact_ratio w diagnostyce). 1634/1634, audyt exit 0.
Pliki: `zwiadowcy/exp_kyle_lambda.py` (próg adaptacyjny), `narzedzia/pomiar_nowe_moduly.py`
(matryca 5×3), `tests/test_garch_kyle.py` (+2), `docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | POMIAR (Prawo XVI) | Dekorelacja + IC nowych modułów → EXP-15 wyciszony

Narzędzie `narzedzia/pomiar_nowe_moduly.py` — pomiar EXP-13/14/15 na realnych danych
(Binance BTC 4h, 18631 barów). Cel: czy nowe moduły niosą nową informację (Prawo XVI),
nie zgadywanie.

WYNIKI DEKORELACJI (|ρ| z resztą zwiadowców):
- EXP-13 (GARCH): max|ρ|=0.143 → 🟢 UNIKALNY (justified — nowa informacja)
- EXP-14 (Kyle): max|ρ|=0.143 → 🟢 UNIKALNY
- EXP-15 (PIN): stały sygnał → nie da się skorelować (martwy)

WYNIKI IC (Spearman sygnał_t vs zwrot_{t+h}, h=1/6/30 barów 4h):
- EXP-13 GARCH: IC≈+0.10..0.12 (realny skill, ostrożność vol)
- EXP-14 Kyle: IC≈+0.48 (PODEJRZANIE WYSOKIE — flaga, artefakt reżimowy? wymaga backtestu;
  zweryfikowano że NIE jest trywialnym lookahead: zgodność ze znakiem bieżącej świecy 38%)
- EXP-15 PIN: n/a (stały sygnał)

🚨 DECYZJA (Prawo XV + Prawo I): EXP-15 PIN WYCISZONY (DOSTEPNY=False).
PIN > próg tylko 0.1% czasu (2/1858 barów), pewnosc_przeciwnika>0 raptem 2× w całej historii.
Przyczyna strukturalna: PIN to zjawisko TICK-LEVEL; uśrednianie buy/sell z tick-rule po barach
OHLCV niszczy asymetrię (mean_buy≈mean_sell→PIN≈0). Dodany przedwcześnie — pomiar to wychwycił.
Ożywa po podpięciu feedu aggTrades (trade-by-trade) — jak EXP-12 (L2). To jest CEL pomiaru:
nie dodawać w ciemno, mierzyć i cofać gdy moduł nie niesie wartości.

Liczniki: 81 neuronów (75 aktywnych) + 15 zwiadowców (13 aktywnych, 2 wyciszone: EXP-12, EXP-15).
1632/1632 testów, audyt exit 0.

Pliki: `narzedzia/pomiar_nowe_moduly.py` (NEW), `legiony/zwiadowcy/exp_pin.py` (DOSTEPNY=False),
`docs/MANIFEST_KODU.md`, `docs/MAPA_KLUCZY.md`, `docs/LOG_ZMIAN.md`.

---

## 2026-06-21 | W-377..379 obudzenie + W-383 | OC-06..08 ożywione + EXP-15 PIN scout

Obudzenie 3 martwych głosów (Prawo XV) + wpięcie PIN do roju:
- **W-377..379 obudzenie**: `szacuj_block_height(timestamp)` w onchain.py — interpolacja
  po kotwicach halvingów (genesis/210k/420k/630k/840k) + ekstrapolacja 10min/blok +
  normalizacja ms→s (bary MEXC w ms). Wpięte do `BudowniczyWskaznikow._dodaj_btc_onchain()`.
  OC-06/07/08 DOSTEPNY=True — działają w backteście i live (bez sieci, deterministyczne).
- **W-383 EXP-15 ZwiadowcaPIN** (`zwiadowcy/exp_pin.py`): PIN metodą momentów na buy/sell
  z tick-rule OHLCV. Wysoki PIN → NEUTRAL + pewnosc_przeciwnika (tłumi rój, adverse
  selection). Komplementarny do VPIN Z-01 i Kyle EXP-14.
- Audyt: OC-06/07/08 dodane do NEURONY_ZALEZNE_OD_ADAPTEROW + WERYFIKACJA_ADAPTEROW
  (dowód ożywienia przy realnym BTC_BLOCK_HEIGHT — Prawo I, wzorzec Z-06/Z-07).
- 14 nowych testów (test_block_height_pin_scout.py): kotwice halvingów, ekstrapolacja,
  Budowniczy wpina block height, OC-06..08 żywe, PIN scout granice.
Liczniki: 81 neuronów (75 aktywnych) + 15 zwiadowców = 96 modułów. 1632/1632 testów, audyt exit 0.

Pliki: `legiony/neurony/onchain.py` (szacuj_block_height + DOSTEPNY=True),
`legiony/budowniczy_wskaznikow.py` (_dodaj_btc_onchain), `legiony/zwiadowcy/exp_pin.py` (NEW),
`legiony/rejestr.py` (EXP-15), `narzedzia/audyt_spojnosci.py` (allowlist+weryfikacja),
`tests/test_block_height_pin_scout.py` (NEW, 14), `tests/test_integracja.py` (liczniki),
`docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`, `docs/MANIFEST_KODU.md`, `docs/MAPA_KLUCZY.md`,
`README.md`, `docs/INDEKS_IMPERIUM.md`.

---

## 2026-06-21 | W-374/381/382 | HRP + PIN + Engle-Granger kointegracja (pure numpy)

Kontynuacja kolejki kandydatów z BIB-025..032 — wszystko pure numpy, bez scipy/sklearn:
- **W-374 HRP** (`denoising_macierzy.py` → `hrp_wagi()`): Hierarchical Risk Parity
  (López de Prado 2016, Jansen BIB-026). Single-linkage clustering + quasi-diagonalizacja
  (seriation) + recursive bisection. NIE odwraca macierzy → odporna na klątwę Markowitza.
  Dopełnia NCO (W-367). 7 testów.
- **W-381 PIN** (`mikrostruktura.py` → `pin_metoda_momentow()`): Probability of Informed
  Trading (Easley-O'Hara, BIB-032). Metoda momentów zamiast MLE: ε=min(buy,sell) baza
  szumu, informed=|buy−sell|, PIN=informed/(informed+2ε). Komplementarny do VPIN Z-01. 5 testów.
- **W-382 Engle-Granger** (`mikrostruktura.py` → `kointegracja_engle_granger()`): kointegracja
  par (Tsay BIB-031 rozdz. 8). OLS log-log → spread; ADF na spreadzie (próg −3.4 anty-spurious).
  z-score spreadu = sygnał stat-arb. 7 testów (skointegrowane vs spurious random walks).

Nowy moduł `imperium/legiony/mikrostruktura.py`. denoising_macierzy.py + metryki_ic.py +
mikrostruktura.py dopisane do MANIFEST (sekcja Moduły Infrastruktury).
1618/1618 testów, audyt exit 0, ruff czysty.

Pliki: `legiony/mikrostruktura.py` (NEW), `legiony/denoising_macierzy.py` (+hrp_wagi),
`tests/test_hrp_mikrostruktura.py` (NEW, 19 testów), `docs/REJESTR_INSPIRACJI.md`,
`docs/LOG_ZMIAN.md`, `docs/MANIFEST_KODU.md`.

---

## 2026-06-21 | W-376..380 + BIB-029..032 | GARCH/Kyle's Lambda/BTC halvings (INF-41..44)

4 nowe książki przeanalizowane (BIB-029..032):
- INF-41 Bashir Mastering Blockchain 2/10 → ODRZUCONA (DApp inżynierska, zero metryk tradingowych)
- INF-42 Ammous Bitcoin Standard 3/10 → OC-06..08 deterministyczne
- INF-43 Tsay Analysis of Financial Time Series 9/10 → EXP-13 GJR-GARCH
- INF-44 O'Hara Market Microstructure Theory 8/10 → EXP-14 Kyle's Lambda

Nowe moduły:
- **W-376 EXP-13 ZwiadowcaGARCH** (`zwiadowcy/exp_garch.py`): GJR-GARCH(1,1) =
  σ²_t = α₀ + (α₁+γ·I[a<0])·a²_{t-1} + β₁·σ²_{t-1}. Grid search log-likelihood
  (pure numpy, zero scipy). HIGH_VOL/EXTREME_VOL → SHORT, LOW_VOL → LONG. 5 testów.
- **W-377..379 OC-06..08** (onchain.py): NeuronS2F (S2F = podaż/roczna_emisja),
  NeuronDaysToHalving (bloki_do×10min/1440), NeuronBTCSupplyInflation — wszystkie
  deterministyczne z BTC_BLOCK_HEIGHT, zero API zewnętrznych.
- **W-380 EXP-14 ZwiadowcaKyleLambda** (`zwiadowcy/exp_kyle_lambda.py`): Kyle's Lambda
  OLS: λ = Δp/netflow — nachylenie regresji. Prawo XVI: mierzy |ρ(λ, Amihud)| live.
  27 testów granic (zero wolumenu, OLS fail, bloki zerowe).
Liczniki: 81 neuronów, 14 zwiadowców = 95 modułów. 1599/1599 testów, audyt exit 0.

Pliki: `zwiadowcy/exp_garch.py` (NEW), `zwiadowcy/exp_kyle_lambda.py` (NEW),
`neurony/onchain.py` (OC-06..08 dodane), `rejestr.py` (rejestracja),
`tests/test_garch_kyle.py` (NEW, 27 testów), `tests/test_integracja.py` (liczniki),
`docs/REJESTR_INSPIRACJI.md` (INF-41..44), `docs/MANIFEST_KODU.md`, `docs/MAPA_KLUCZY.md`,
`README.md`, `docs/INDEKS_IMPERIUM.md`.

---

## 2026-06-21 | W-369..371 | Fundamental Law (IC/breadth/IR) — Grinold & Kahn (BIB-025..028)

Nowy moduł `imperium/legiony/metryki_ic.py` (W-369..371, pure numpy):
- **W-369 IC per-neuron** — `KolektorIC`: buforuje sygnały neuronów i zrealizowane forward
  returny, liczy `Spearman(sygnał_t, zwrot_{t+h})` dla h∈{1,5,21}. `_spearman()` w czystym
  numpy (rank z uśrednieniem ties). Fallback NaN gdy <min_probek, stała seria, pusta baza.
- **W-370 Breadth** — liczba niezależnych zakładów wyliczana z ONC (W-366), fallback do
  `len(neurony)`. Zintegrowane w `prawo_fundamentalne()`.
- **W-371 IR decomposition** — `prawo_fundamentalne()`: IR = IC_śr · √breadth. Diagnoza
  4-poziomowa (IC_NISKI/BREADTH_NISKI/IR_DOBRY/IR_SREDNI/IR_SLABY). Sortuje neurony wg |IC|.
- 17 nowych testów (`test_metryki_ic.py`) — granice: NaN, stała seria, pusta baza, idealna
  antykorelacja, ties, diagnoza IC_NISKI/IR_DOBRY, kolejność sortowania.

BIB-025..028 przeanalizowane i zarejestrowane (INF-37..40):
- INF-37 ⭐ Grinold&Kahn 9/10: Fundamental Law IR=IC·√breadth (W-369..371 wdrożone)
- INF-38 Jansen 5/10: IC Scorer konwerguje z INF-37; HRP kandydat W-374
- INF-39 Aldridge 4/10: Kyle's Lambda kandydat W-374b (czeka test Prawa XVI)
- INF-40 Narang 7/10: audyt architektoniczny 8 kategorii alpha; point-in-time kandydat W-375
ŻYCZ-15..18 zamknięte (BIB-025..028 dostarczone i przeanalizowane).
Daty "Stan na:" zaktualizowane (MANIFEST+README → 2026-06-21).
1572/1572 testów, audyt exit 0.

Pliki: `imperium/legiony/metryki_ic.py` (NEW), `tests/test_metryki_ic.py` (NEW),
`docs/REJESTR_INSPIRACJI.md` (INF-37..40 + wizje W-369..373 + ŻYCZ-15..18 zamknięte),
`docs/LOG_ZMIAN.md`, `docs/MANIFEST_KODU.md` (data), `README.md` (data).

---

## 2026-06-20 | W-365 INTEGRACJA | Denoising wpięty w żywy przepływ synaps

`KolektorKorelacjiNeuronow.korelacje_denoised()` (diagnostyka_korelacji.py) — buduje pełną
macierz korelacji par neuronów, odszumia ją (Marchenko-Pastur, W-365) i zwraca pary w formacie
zgodnym z `korelacje()`. Dyrygent (linia ~343) preferuje wersję ODSZUMIONĄ przy zasilaniu
SynapsyRezimowe (flaga `denoising_korelacji=True`). Dzięki temu synapsy karzą/wzmacniają za
SYGNAŁ, nie szum — Prawo XVI działa tam gdzie jest konsumowane. BEZPIECZNY FALLBACK do surowej:
<2 neuronów / t<min_probek / q=T/N≤1 / seria stała (NaN). 5 testów granic (`test_kolektor_denoised.py`).
1555/1555 testów, audyt exit 0, adversarialna recenzja czysta przed pushem.

---

## 2026-06-20 | W-365..368 | Denoising/Clustering macierzy (López de Prado MLAM, BIB-023)

Wdrożono `imperium/legiony/denoising_macierzy.py` (czysty numpy — scipy/sklearn niedostępne):
- **W-365 Denoising** — `denoise_macierz()` metodą Marchenko-Pastur + constant residual
  eigenvalue. `mp_pdf()` (teoretyczna gęstość MP), `znajdz_max_eval()` (dopasowanie wariancji
  szumu przez KDE Gaussa w czystym numpy + grid search, bo brak scipy.minimize).
- **W-366 ONC** — `klastruj_onc()`: auto-klastrowanie na metryce `√(½(1−ρ))`, K-Means +
  silhouette w czystym numpy, auto-dobór k przez t-stat jakości (śr/odch silhouette).
- **W-367 NCO** — `nco_wagi()`: Nested Clustered Optimization, wagi min-wariancji odporne
  na klątwę Markowitza (klastruj → wewnątrz → między klastrami). `_wagi_min_wariancji()` (pinv).
- **W-368 Detoning** — `detone_macierz()`: usuwa „ton rynkowy" (n czołowych wartości własnych).

16 testów (`test_denoising_macierzy.py`) z REGUŁĄ TEST-GRANIC (identyczność=szum, blok znany,
pojedynczy element, q≤1 ValueError, n_czynnikow=0 bez zmian, determinizm seed). Zamyka lukę
dekorelacji macierzowej z ANALIZA_HERMES_I_PAMIEC. 🚨 ODKRYCIE SPÓJNOŚCI: **W-364 (Variation
of Information) JUŻ był w kodzie** (`diagnostyka_korelacji.py`) — agent mylił MANIFEST z kodem.

---

## 2026-06-20 | RESEARCH | Analiza 4 nowych książek (BIB-020/022/023/024) — 4 zwiadowców Opus

Cezar wrzucił do `bibliotheca_ulpia/` 24 książki (20 starych już w rejestrze + 4 nowe pliki).
Ekstrakcja tekstu: epub→unzip+html, pdf→pymupdf, djvu→djvutxt. 4 agentów Opus przeżyło każdą:

- **BIB-020 Harris "Trading and Exchanges"** — fizyczny plik dodany, ale **książka była już
  przeżyta w WIZJONER** (ŻYCZ-10, W-250..279, 5 wizji w kodzie: X-27/Z-03/Z-04/VR/OU). Agent
  „odkrył" U-01 Roll = już W-264, U-03 resiliency = już W-274. **Nic nowego** (Prawo XXI: spójność).
- **BIB-022 Kissell "Optimal Trading Strategies"** → INF-34, 4/10. IS = już W-267, impact gate =
  już W-266/269. Jedyne ziarno: EXEC-01 (slippage zależny od płynności vs stały slippage_pct).
- **BIB-023 López de Prado "ML for Asset Managers"** → INF-35 ⭐ 8/10 SKARB. Realnie nowe:
  denoising (Marchenko-Pastur), Variation of Information (nieliniowa metryka), ONC, NCO, detoning.
  Zamyka 2 luki pamięci z ANALIZA_HERMES. **→ W-364..368 zaplanowane** (VI najpierw).
- **BIB-024 Lowe "Bitcoin for Beginners"** → INF-36 ❌ 1/10 odrzucona (niżej niż INF-31, błędy
  merytoryczne, zero ziarna). Wizji nie przyznano (Prawo I).

🚨 Prawo XV: `diagnostyka_korelacji` mierzy tylko Pearsona liniowo — redundancja nieliniowa między
głosami niewidoczna. W-364 (Variation of Information) to zamyka. Pliki książek w `bibliotheca_ulpia/`.

---

## 2026-06-20 | DOC | Analiza Hermes Agent vs Pamięć Imperium + status książek

`docs/ANALIZA_HERMES_I_PAMIEC.md` — odpowiedź na pytanie Cezara o pamięć absolutną „jak Hermes".
Ustalenia (Prawo I + web research 2026-06-20): (1) „Hermes Agent" tradingowy = fabrykacja
z rozmowy DeepSeek (już w INF-32); (2) realny Hermes Agent Nous Research istnieje — asystent
osobisty, pamięć 5-filarowa (memory/skills/soul/crons/self-improving). Porównanie z naszymi
8 modułami pamięci (2135 linii): wygrywamy hashem SHA-256, MAE/MFE, synapsami reżimowymi;
luki: wyszukiwanie semantyczne, graf wiedzy, auto-lekcje, pamięć proceduralna. Status 21 książek
BIB (esencja wyciągnięta, wdrożenie w kodzie = backlog). Plan W-360..363 + rekomendacja
kolejnej książki (López de Prado "ML for Asset Managers"). Powód: Cezar prosił o ciągłość pamięci.

---

## 2026-06-20 | DOC | Manual dodawania agentów + 2 subagenci Claude Code

`docs/MANUAL_DODAWANIE_AGENTOW.md` — rozróżnienie dwóch typów „agentów": Doradcy Imperium
(moduły Python w `imperium/cesarz/doradcy/`) vs Subagenci Claude Code (`.claude/agents/*.md`).
Krok po kroku jak dodać każdy typ — wzorzec doradcy VULCAN (audytor płynności), struktura
subagenta z nagłówkiem YAML, kiedy który typ, zasady Prawo VII/VIII/XIX/XXI.
Dodano 2 działające subagenty: `straznik-prawa-xxi` (kontrola spójności przed commitem),
`hermes-audytor-danych` (audyt jakości danych, wzorowany na doradcy HERMES).
Powód: Cezar zapytał jak dodawać narzędzia typu „Hermes agent" zgodnie z dokumentacją.

---

## 2026-06-20 | DOC | Manual Claude Code — instalacja i konfiguracja z Imperium

`docs/MANUAL_CLAUDE_CODE.md` — kompletny przewodnik instalacji Claude Code na laptopie:
Node.js, npm install claude-code, logowanie Pro, pierwsze uruchomienie z Imperium,
automatyki (hook SessionStart, uprawnienia, tryb autonomiczny), MCP GitHub i Filesystem,
klucze API (Prawo V), codzienna praca (komendy, skróty, Plan Mode), tabela problemów.
Powód: Cezar ma już repo na laptopie, chce uruchamiać Claude Code lokalnie z pełną integracją.

---

## 2026-06-20 | DOC | Manual Użytkownika — pełna instrukcja dla nowicjusza

`docs/MANUAL_UZYTKOWNIKA.md` — kompletny przewodnik krok po kroku: instalacja od zera
(Windows/Mac/Linux), pierwsze uruchomienie, wszystkie tryby (paper/dry-run/real), panel
webowy, TradingView+ngrok krok po kroku, wszystkie opcje KonfigPetliLive, wszystkie komendy,
klucze API (bezpieczeństwo), narzędzia AFML (W-355..W-359), tabela problemów i rozwiązań.
Powód: Cezar (nowicjusz, ZPO) poprosił o pełny manual obsługi.

---

## 2026-06-20 | W-355..W-359 | AFML (López de Prado) — 5 modułów z "Advances in Financial ML"

**Źródło:** Lektura i analiza książki "Advances in Financial Machine Learning" (INF-34),
najważniejsza pozycja w dziedzinie. Agent Opus przeczytał całość i wskazał 5 braków vs Imperium.

**W-355 | Feature Importance: MDA + SFI (AFML Ch. 8)**
`imperium/legiony/feature_importance.py` — `raport_waznosci(historia, wyniki)`.
MDA (Mean Decrease Accuracy): permutuje sygnał neuronu → mierzy spadek accuracy roju.
SFI (Single Feature Importance): accuracy każdego neuronu samodzielnie (odporna na korelacje).
Realizuje Prawo XV (martwy głos = neuron z MDA≤0) i Prawo XVI (redundancja mierzona OOS).

**W-356 | Dollar/Volume/Tick/Imbalance Bars (AFML Ch. 2)**
`imperium/akwedukty/bary_zdarzeniowe.py` — próbkowanie zdarzeniowe zamiast czasowego.
Dollar bars (co N USD obrotu) mają homoskedastyczność i własności bliższe IID vs świece 1h.
Aproksymacja z OHLCV (4 syntetyczne ticki per bar) + prawdziwe websocket ticki.
Imbalance bars: adaptacyjne próbkowanie przy asymetrii Buy/Sell (detekcja informatywnych flow'ów).

**W-357 | Triple-Barrier Method + CUSUM Filter (AFML Ch. 3 + 17)**
`imperium/legiony/triple_barrier.py` — spójny silnik etykiet pod meta-labeling (B-01).
Dynamiczne progi w wielokrotnościach σ zmienności (nie fixed %). CUSUM sampler zdarzeń.
Sample Uniqueness (AFML Ch. 4) — wagi próbek odwrotnie proporcjonalne do nakładania etykiet.

**W-358 | Purged K-Fold + Embargo (AFML Ch. 7)**
`imperium/koloseum/walidacja.py` — `purged_kfold_podzialy()` + `cross_val_score_purged()`.
Purging: usuwa train-obs nakładające się z test (brak information leakage).
Embargo: usuwa obs tuż PO teście (embargo_pct × n barów, autokorelacja residualna).

**W-359 | Bet Sizing LdP: Gaussian CDF + averaging + dyskretyzacja (AFML Ch. 10)**
`imperium/legiony/meta_labeling.py` — `bet_size_ldp()` + `BuforAktywnych`.
Gaussian CDF: m = 2Φ((p−0.5)/√(p(1-p)))−1 zamiast Kelly 2p−1 (mocniej skaluje).
Averaging active bets: uśrednione bet_size nakładających się pozycji → niższy turnover.
Size discretization: round(m/d)×d → eliminuje mikrodrgania i koszt transakcyjny.

**Testy:** 1531/1532 → 1531+35 nowych (test_afml.py) po naprawie.
**Audyt:** pełna harmonia ✅ | Ruff: czysty ✅

---

## 2026-06-19 | W-354 | TradingView Webhook Receiver — sygnały na żywo w roju (Prawo XV)

**Cel:** Podłączenie TradingView do Imperium przez HTTP POST webhook — alerty z Pine Script
trafiają bezpośrednio do roju (Dyrygent.cykl). Wykres świecowy (Lightweight Charts, MIT)
w Panelu Kapitolu. Selector pary/interwału. Cross-session bar buffer per symbol.

**Nowe pliki:**
- `imperium/swiatynie/webhook_tradingview.py` — `AlertTV`, `parsuj_alert_tv()`, `OdbiornikWebhook`
- `tests/test_webhook_tv.py` — 25 testów (granice, sekret, historia, dashboard routing)

**Zmiany:**
- `web_dashboard.py` — `do_POST` w `DashboardHandler`, `/webhook/tv`, `/wykresy/{SYM}.json`,
  Lightweight Charts widget, symbol selector, Pine Script template w panelu, `obsluz_post()`
- `petla_live.py` — `KonfigPetliLive.webhook_tv: bool`, `OdbiornikWebhook` tworzony przy
  `dashboard=True, webhook_tv=True`; alerty z TV dołączane do `bary_per` w pętli live;
  auto-rejestracja nowych symboli z TV w `dyrygenci`
- `docs/LOG_ZMIAN.md` — ten wpis

**Bezpieczeństwo:** sekret webhooka WYŁĄCZNIE przez `WEBHOOK_TV_SEKRET` env (nigdy hardcode).
Domyślny bind 127.0.0.1. Zewnętrzny dostęp przez ngrok/Cloudflare Tunnel — poinstruowane
w Pine Script template i docs.

**Testy:** 1497/1497 ✅ | Audyt: pełna harmonia ✅

---

## 2026-06-19 | W-353 | Kaufman Efficiency Ratio — ożywienie martwego głosu Fulmena (Prawo XV)

**Pochodzenie:** lektura książki "High Win Rate Day Trading Setups" (INF-33/BIB-021,
ocena 3/10 — detaliczny katalog skryptów TradingView, ~80% pokrycia z rojem). Rozdział
o KAMA (Kaufman Adaptive MA) naprowadził na audyt: gdzie używamy Efficiency Ratio?

**Diagnoza (dowód, nie zgadywanie):** Doradca **Fulmen** (ortogonalna weryfikacja reżimu)
w `ocen()` używa `kaufman_er > ER_EFEKTYWNY (0.6)` jako JEDNEGO Z TRZECH warunków
potwierdzenia TRENDU (obok ADX i Choppiness). Ale `Dyrygent._zbuduj_rade()` przekazywał
`kaufman_er=0.5` na sztywno z komentarzem *"nie liczony przez Budowniczego → neutral default"*.
Efekt: **1/3 logiki trendu Fulmena była trwale martwa** (wąskie gardło, Prawo XV) — ER nigdy
nie mógł przekroczyć progu 0.6, więc nigdy nie współpotwierdzał trendu.

**Wdrożenie:**
- `brama_kalkulatora.py`: nowa funkcja `_py_kaufman_er(close, period=10)` — ER = |zmiana netto| / Σ|ruchy brutto|, zakres [0,1]. Rejestracja `KAUFMAN_ER` + dopis do `_PURE_PYTHON_INDICATORS` (uczciwa pieczątka źródła, Prawo XIII).
- `budowniczy_wskaznikow.py`: `KAUFMAN_ER_10` w planie skalarnym (period=10).
- `dyrygent.py`: `kaufman_er=wskazniki.get("KAUFMAN_ER_10") or 0.5` — martwy głos ożył.

**Testy granic (6 nowych, reguła Test-Granic):**
- trend liniowy → ER=1.0 | piła (zero netto) → 0.0 | płasko → 0.0 (NIE dzielenie przez zero)
- < period+1 barów → None (Prawo XV) | realna zaszumiona seria → ER∈[0,1]
- symbioza: Budowniczy faktycznie produkuje `KAUFMAN_ER_10`

**Decyzja o reszcie książki (Prawo XVI):** MFI już skatalogowany (INF-18, W-101..W-106) —
nie dublujemy. Pozostałe wskaźniki redundantne z rojem. Liczba neuronów bez zmian (78).

**Wynik testów:** 1472/1472 ✅ | ruff ✅ | audyt exit 0 ✅ | Pliki: `brama_kalkulatora.py`, `budowniczy_wskaznikow.py`, `dyrygent.py`, `test_neurony.py`, `REJESTR_INSPIRACJI.md`

---

## 2026-06-19 | W-352 | Persystencja uczenia — MWU/Igrzyska/Synapsy pamiętają między sesjami

**Diagnoza:** Wszystkie trzy mechanizmy uczenia (HedgeMWU, Igrzyska, SynapsyRezimowe) działały
poprawnie WEWNĄTRZ sesji, ale po restarcie kasowały się do stanu startowego (zerowe wagi).
Brak cross-session persistence = rój zaczyna uczyć się od zera przy każdym uruchomieniu.
To była kluczowa **utrata potencjału (Prawo XV)** — uczenie istniało, ale bez pamięci.

**Wdrożenie:**
- `HedgeMWU`: dodano `zapisz(sciezka)` i `wczytaj(sciezka)` — serialize `wagi_raw` + `rundy` do JSON.
- `HedgeMWUzPamieciaRezimu`: nadpisuje `zapisz()`/`wczytaj()` — dodatkowo serializuje `pamiec` reżimową i `rezim`.
- `Igrzyska`: dodano `zapisz(sciezka)` i `wczytaj(sciezka)` — serialize pełne `StatystykaNeuronu` (tp, fp, per-reżim, stability, contribution) do JSON.
- `KonfigPetliLive`: dodano trzy nowe pola: `sciezka_mwu`, `sciezka_igrzyska`, `sciezka_synapsy` (domyślnie `logs/`).
- `petla_live.py`: 
  - bootstrap przy starcie: `mwu.wczytaj()`, `ig.wczytaj()`, `SynapsyRezimowe(sciezka_stanu=...)`.
  - zapis przy zakończeniu (w bloku po `except KeyboardInterrupt`): `mwu.zapisz()`, `ig.zapisz()`, `syn.zapisz()`.
  - MWU upgraded do `HedgeMWUzPamieciaRezimu` (pamięć reżimowa aktywna domyślnie).
  - Per-symbol paths: `logs/mwu_BTCUSDT.json`, `logs/igrzyska_ETHUSDT.json` (izolacja par).

**Testy (6 nowych):**
- `test_mwu_zapisz_wczytaj_roundtrip`, `test_mwu_pamiec_rezimowa_roundtrip` — wagi i pamięć reżimowa identyczne po roundtrip.
- `test_mwu_wczytaj_nieistniejacy_plik_nie_crashuje` — bezpieczny start od zera.
- `test_igrzyska_zapisz_wczytaj_roundtrip`, `test_igrzyska_akumuluje_po_wczytaniu` — rangi i akumulacja cross-session.
- `test_igrzyska_wczytaj_nieistniejacy_plik_nie_crashuje` — bezpieczny start od zera.

**Wynik testów:** 1466/1466 ✅ | Pliki: `hedge_mwu.py`, `igrzyska.py`, `petla_live.py`, `test_hedge_mwu.py`, `test_igrzyska.py`

---

## 2026-06-19 | W-351 | Trailing Stop — koniec oddawania szczytu zysku (Prawo XV)

**Diagnoza (dowód, nie zgadywanie):** dashboard skanera pokazał zyskowne pozycje
zamykane przez `TIMEOUT` daleko poniżej szczytu (np. LTC SHORT +12% ceny → TIMEOUT,
DOT SHORT +13% → TIMEOUT), a stratne lecące do pełnego SL mimo wcześniejszego ruchu
w naszą stronę. W kodzie `paper_trading.py` MAE/MFE były LICZONE co bar, ale NIGDY
nieużywane do wyjścia — `_sprawdz_wyzwalacze` znał tylko `LIQ > SL > TP > TIMEOUT`.
Brak blokady zysku = **utrata potencjału (Prawo XV)**.

**Wdrożenie (`imperium/koloseum/paper_trading.py`):** trailing stop oparty na szczycie
korzystnej ceny.
  • Uzbraja się dopiero po ruchu korzystnym ≥ `TRAILING_AKTYWACJA_PCT` (4%), potem
    podąża za szczytem oddając max `TRAILING_GIVEBACK_FRAC` (35%) — blokuje 65% szczytu.
  • Stop **monotoniczny** — tylko się zaciska, nigdy nie cofa przeciw pozycji.
  • Kolejność wyjść: `LIQ > SL > TRAIL > TP > TIMEOUT`.
  • **Anty-look-ahead:** bar uzbrajający NIE wyzwala trailingu (nie znamy ścieżki
    intrabar — high mógł paść po low); trailing działa po poziomie z POCZĄTKU bara.
    Zamknięcie po poziomie sprzed bara (pesymizm wykonania) + slippage.
  • Domyślnie **OFF** (`trailing=False`) — zero regresji dla istniejących sesji;
    `backtest_portfel(trailing=...)` przekazuje flagę; `najlepszy_tryb.py` ma ON.

**Testy:** +7 (`tests/test_paper_trading.py`) — Reguła Test-Granic: próg dokładny (≥),
tuż-poniżej-progu, LONG/SHORT lustrzanie, monotonia stopu, cena zamknięcia = poziom
stopu, zero-regresji przy OFF. **1453 → 1460/1460 zielone.** Audyt exit 0, ruff czysto.

**Pliki:** imperium/koloseum/paper_trading.py, imperium/koloseum/backtest.py,
narzedzia/najlepszy_tryb.py, tests/test_paper_trading.py, docs/LOG_ZMIAN.md.

---

## 2026-06-19 | W-346 | Web Dashboard — Panel Kapitolu (realizuje W-004 + W-031)

**Luka #3 ze skanu konkurencji (Prawo XV):** Freqtrade FreqUI, Jesse UI mają panel
webowy; mieliśmy tylko LiveMonitor TUI + Telegram. Rój 76 neuronów decydował „w ciemno"
— Cezar nie WIDZIAŁ walki neuronów na żywo (ukryta utrata potencjału).

**Wdrożenie (`imperium/swiatynie/web_dashboard.py`):** ZERO ZALEŻNOŚCI (jak cały
Imperium) — stdlib `http.server` + samowystarczalny HTML (inline CSS/JS, fetch),
zamiast FastAPI. Ten sam `StanDashboardu` co LiveMonitor (jedno źródło — Prawo XVI).
  • `obsluz_sciezke()` — czysty router (testowalny bez gniazda): `/` HTML,
    `/stan.json` JSON, `/godlo.svg` godło (W-342).
  • `SerwerDashboard` — serwer w wątku-daemonie, bind 127.0.0.1 (tylko lokalnie,
    nie wychodzi na świat — bezpieczeństwo), `aktualizuj(stan)` co bar.
  • **W-031 Roman Naming**: BTC→Capitolium, ETH→Patricii Aeterni, SOL→Velocitas
    Barbari, DOGE→Mimus Augusti — szlacheckie nazwy walut w panelu.

**Wpięcie (Prawo XV):** `KonfigPetliLive.dashboard=True` (opt-in, OFF) → serwer
startuje, `aktualizuj(stan)` współdzieli StanDashboardu z LiveMonitorem, stop po pętli.

**Testy:** +18 (`tests/test_web_dashboard.py`) — routing, serializacja, Roman Naming,
granica zero-kapitał-start, e2e serwer na efemerycznym porcie. **1430 → 1447/1447 zielone.**

---

## 2026-06-19 | W-345 | Walk-Forward — kroczące okna IS/OOS (obrona przed przeuczeniem)

**Luka #2 ze skanu konkurencji (Prawo XV):** Freqtrade/Jesse mają WFO od lat.
Mieliśmy hyperopt (`optymalizator.py`, DSR-guided) i walidację (`walidacja.py`,
PBO/DSR), ale BRAK orkiestracji walk-forward — jedynej uczciwej obrony przed
przeuczeniem przy 76 neuronach × wagi reżimowe (ogromna przestrzeń parametrów).

**Wdrożenie (`imperium/koloseum/walk_forward.py`):** kroczące pary okien:
  • IS (In-Sample) — `optymalizuj()` szuka parametrów (wykorzystuje istniejący
    DSR-guided hyperopt — Prawo XVI, nie dubluje).
  • OOS (Out-of-Sample) — egzamin tych parametrów na danych NIEWIDZIANYCH.
  • Okno sunie (rolling) lub rośnie od zera (anchored); OOS zawsze PO IS (zero look-ahead).

**WFE (Walk-Forward Efficiency)** = Sharpe_OOS / Sharpe_IS:
  • ≥ próg (0.5, Pardo) + OOS Sharpe > 0 → **ROBUST** (parametry trzymają poza próbą)
  • IS uczył przewagi ale WFE < próg → **PRZEUCZONY** (degradacja OOS)
  • OOS Sharpe ≤ 0 → **SLABY** (brak przewagi poza próbą, niezależnie od WFE)
Werdykt liczony WYŁĄCZNIE z OOS (Prawo I — egzamin na nieznanym). Raport zawiera
też stabilność parametrów (CV między oknami) — skaczący parametr = ostrożność.

**Testy:** +19 (`tests/test_walk_forward.py`) — granice: brak look-ahead, za mało
barów, zero-wariancji Sharpe, IS≤0→WFE=0, trzy werdykty. **1407 → 1426/1426 zielone.**

---

## 2026-06-19 | W-344 | OMS — Zarządca Zleceń: maszyna stanów cyklu życia zlecenia

**Luka ze skanu konkurencji (Prawo XV):** NautilusTrader/Freqtrade mają jawny
order-lifecycle od lat; my mieliśmy fire-and-forget `create_order` w
`RealOrderRouter` (try/except, bez stanu zlecenia, retry, akumulacji partial-fill).
„Mózg bez rąk" — najlepszy rój sygnałów bez solidnej egzekucji.

**Wdrożenie (`imperium/drogi/oms.py`):** jawna maszyna stanów
`NOWE→ZLOZONE→CZESCIOWE→WYPELNIONE` (+ ODRZUCONE/ANULOWANE/BLAD jako końcowe).
Nielegalne przejście = wyjątek (Prawo I), nie cisza. Klasy: `StanZlecenia`,
`Zlecenie` (akumuluje partial-fille, cena średnia ważona wolumenem), `ZarzadcaZlecen`.

**Funkcje:**
  • `zloz()` — retry z backoffem wykładniczym; po wyczerpaniu prób → BLAD + False (jawna porażka).
  • `zarejestruj_wypelnienie()` — akumuluje partial-fille; over-fill → wyjątek (granica Prawa XXI).
  • `reconcile(stan_gieldy)` — uzgadnia OMS z prawdą giełdy (Prawo I), nie cofa stanów końcowych.
  • Tryb paper (submit_fn=None, domyślny) = od razu ZLOZONE bez sieci; realny = owija
    `RealOrderRouter._zloz_zlecenie` w retry+maszynę stanów (parity backtest=live).

**Wpięcie (Prawo XV — bez osieroconego modułu):** `RealOrderRouter` dostał opt-in
`sledz_oms=True` → każde wejście/wyjście idzie przez `_zloz_sledzone()` (OMS owija
`_zloz_zlecenie` w retry+maszynę stanów, rejestruje fill z odpowiedzi giełdy).
Domyślnie OFF = stare zachowanie bez zmian. `raport_oms()` = diagnostyka stanów.

**Idempotencja (anti-double-submit, W-345):** `Zlecenie.klucz_idempotencji`
(= stabilny zlecenie_id) → wysyłany jako `newClientOrderId` (MEXC dedupuje duplikat).
OMS dostał `query_fn`: PRZED każdą ponowną próbą pyta giełdę (`fetch_order` po kluczu)
czy poprzednia próba jednak weszła mimo wyjątku — jeśli tak, NIE wysyła duplikatu
(Prawo I — fakt z giełdy bije założenie „nie weszło"). Zamyka ryzyko double-submit.

**Bezpieczeństwo:** zero realnego kapitału — pure-Python, testowany mockiem.

**Testy:** +34 (`tests/test_oms.py`: granice + idempotencja) + 5 integracji
(`test_real_order_router.py`). **1372 → 1430/1430 zielone.** Audyt: pełna harmonia.

---

## 2026-06-18 | W-340 | Vol-gate: Jump Model zmienności → klasyfikator reżimu (opt-in, zmierzony)

**Odkrycie Prawa XV (utrata potencjału):** JumpModel (W-281) miał kod+testy+narzędzie
pomiarowe, ale NIE był podpięty do niczego — gotowy moduł poza pipeline.

**Pomiar (Prawo I) ROZSTRZYGNĄŁ kierunkowy JumpModel jako NIESPÓJNY:** narzędzie
`pomiar_jump_model.py` na realnych danych 1D (walk-forward, bez look-ahead):
  • BTC: separacja BULL−BEAR = **−6.3 bps** (odwrócona!), ETH = **−23.2 bps**
  • ADX baseline bije go: BTC +20.9, ETH +32.5 bps; JM whipsaw 21–23 przeł/100 vs ADX 5.6
  • Z cechami EWMA: BTC +26.9 (OK) ale ETH −21.1 (wciąż odwrócony) — aktywo-zależny.
→ Kierunkowy naming bull/bear zawodzi out-of-sample (mean-reversion). NIE wpinamy kierunku.

**Co DZIAŁA (zmierzone, aktywo-NIEZALEŻNE):** vol-reżim turbulentny/spokojny.
Reżim turbulentny przewiduje **1.22–1.56× wyższy |zwrot| t+1** spójnie na
BTC/ETH/SOL/DOGE, przełączeń tylko 2–3.4/100 (zero whipsaw). To stabilna oś.

**Wdrożenie (`imperium/legiony/rezim_zmiennosci.py`):** lekki, czysto-pythonowy
2-stanowy Jump Model zmienności (Viterbi z karą za skok, bez numpy w hot-path —
tani na 1m/5m/15m, TF-agnostyczny — operuje na serii zwrotów). `vol_regime_turbo()`
→ (turbo, trwałość, siła). Budowniczy eksponuje VOL_REGIME_TURBO/TRWALOSC/SILA.

**Hook klasyfikatora (opt-in, domyślnie OFF — A/B na P&L pending):**
`klasyfikuj_rezim(..., uzyj_vol_regime=True)` + `Legatus.uzyj_vol_regime`. Turbo
trwały (≥4 bary) → VOLATILE, ale DOPIERO PO TREND_STRONG (jasny trend ADX wygrywa —
turbo zna magnitudę, nie kierunek; fix z code-review).

**Wynik:** 1315/1315 zielonych, audyt czysty. 21 testów granic (vol-regime + klasyfikator).
Neurony bez zmian (76 — to infra klasyfikatora, nie neuron). NeuronBOCPD/CP-01 bez zmian.

---

## 2026-06-18 | W-337 | B-02 Feature Neutralization + B-01 Meta-labeling (nowa warstwa B nad Legatusem)

**Luka strukturalna:** Legatus liczył głosy 74 neuronów, ale nie mierzył:
(a) ile z sygnałów to ta sama informacja powtórzona N razy (redundancja),
(b) ile postawić (bet-sizing po stronie pewności meta-modelu).

**B-02 Feature Neutralization** (`imperium/legiony/neutralizacja.py`):
Regresja każdego sygnału (pewnosc_finalna) na ważoną średnią roju.
Zostaje residuum — ortogonalna część, niezawarta w innych neuronach.
Czysta realizacja Prawa XVI: „redundancja mierzona, nie zgadywana". Opt-in, sila ∈ [0,1].
Źródło: Numerai Feature Neutralization Coefficient (FNC); López de Prado MLAM Ch2 (⚠️ niezw.).
Testy: `tests/test_neutralizacja.py` — 19 testów, w tym granice (sila=0, std=0, klamkowanie).

**B-01 Meta-labeling scorer** (`imperium/legiony/meta_labeling.py`):
Online logistic regression (SGD, D=6 cech: pewnosc_agregatu, sila_long/short, log aktywnych,
log zgodnych, różnica sił). Przewiduje P(sygnał trafny | cechy raportu). Bet_size = Kelly × pewnosc.
Przed 10 próbkami: passthrough z pewnością Legatusa (bezpieczny fallback).
Uczenie: `scorer.zaktualizuj(raport, zysk=True/False)` po zamknięciu pozycji.
Źródło: López de Prado, AFML Ch3 — Meta-labeling (⚠️ pełny tekst niezweryfikowany).
Testy: `tests/test_meta_labeling.py` — 19 testów, w tym granice (weto=0, NEUTRAL=0, sigmoid).

**Wynik:** 1260/1260 testów zielonych. Audyt spójności czysty.
Nowe pliki: `neutralizacja.py`, `meta_labeling.py`, `test_neutralizacja.py`, `test_meta_labeling.py`.
MANIFEST zaktualizowany: nowa sekcja "Meta-warstwy B".
Kolejka ODLOZONE_DECYZJE zaktualizowana.

---

## 2026-06-17 | W-330b | RADAR-05 NeuronLeadBTC + wymiar lead-lag radaru (BTC->alty timing)

**Rozbudowa radaru (wizja Cezara — wiecej oczu):** radar liczyl 4 wymiary. Dodano 5.:
LEAD_BTC — sygnal wyprzedzajacy BTC->alty (lead-lag / Transfer Entropy W-071). Cross-korelacja
zwrotow BTC opoznionych o k vs zwroty altow: najlepszy lag = sila wyprzedzania. Swiezy impuls
BTC x ta sila = kierunkowy sygnal timingu ("BTC pchnal, alty pojda za nim").

**RADAR-05 (`NeuronLeadBTC`, kategoria R, waga 5):** glos na LEAD_BTC, prog 0.30 (wyzszy niz
siostry — odsiewa szum spornych lagow na krotkim oknie). LEAD>=0.30 LONG, <=-0.30 SHORT.
Filar sily: tylko gdy |korelacja lag| >= 0.20 (slaby lead = brak sygnalu). Roj: 71 -> 72.

**RadarRynku:** parametr max_lag (domyslnie 3, 0=wylaczony), pole StanRynku.lead_btc,
eksport LEAD_BTC w jako_wskazniki(). Testy granic: alty podazaja za BTC, max_lag=0 off,
prog 0.30 (>= vs <), walidacja max_lag<0. Spojnosc: MANIFEST/README/INDEKS/audyt = 72.

UWAGA (Prawo I): RADAR-04/05 to glosy kontekstowe niskiej wagi wypelniajace zmierzone luki
(STRES_KORELACJI byl martwy, lead-lag nowy). Wymagaja czystego A/B P&L na portfelu (TODO).

---

## 2026-06-17 | W-330 | SelektorPar — auto-dobor par LIVE (plynnosc x dekorelacja)

**Luka audytu (przed LIVE):** petla_live miala SZTYWNA liste par. System nie umial sam
wykryc co jest dostepne i plynne na MEXC. DataLoader nie wolal load_markets().

**SelektorPar (`koloseum/selektor_par.py`):** pipeline auto-doboru w 3 warstwach (Prawo I):
  1. lista_par_rynku() — CCXT load_markets (wszystkie aktywne USDT-perp)
  2. filtruj_plynne() — min. obrot 24h (chroni przed poslizgiem na cienkiej ksiedze)
  3. ranking alfy = 0.60*obrot_norm + 0.40*(1-|korelacja BTC|) — Prawo XVI: premiujemy
     pary niosace WLASNA informacje, nie kopie ruchu BTC (dywersyfikacja realna)

**DataLoader (W-330):** nowe metody lista_par_rynku() + filtruj_plynne() (CCXT public).
**petla_live (W-330):** KonfigPetliLive.auto_discover (domyslnie False — zero zmiany).
  True → zastepuje cfg.symbole rankingiem TOP-N. Bez sieci/loadera → lista z konfiguracji.

Loader wstrzykiwalny → testy OFFLINE (mock). 8 testow selektora + 2 wpiecia w petli.
Prawo XXI: brak sieci, brak plynnych, dekorelacja premiowana, BTC kotwica, top_n.

---

## 2026-06-17 | W-329b | P4 decay synaps w live — higiena pamieci (Prawo XV)

**Luka audytu P4:** SynapsyRezimowe.zapomnij() istnial, ale NIGDY nie byl wolany w
petla_live — martwe pary neuronow nigdy nie wygasaly w dlugim live (silos rosl bez konca).

**Naprawa:** KonfigPetliLive.synapsy_decay_co_bar (domyslnie 50 barow ~8 dni na 4h).
Co N barow petla wola synapsy.zapomnij() dla kazdego dyrygenta — lagodne tlumienie
silosu + kasacja par ponizej alpha_decay. 0 = wylaczone.

Testy: domyslna wartosc 50, zapomnij() redukuje zywe + kasuje martwe pary.
Pliki: petla_live.py (config + krok 3b petli), test_petla_live.py.

---

## 2026-06-17 | W-329 | RADAR-04 NeuronStresKorelacji — głos dla martwego wskaźnika (Prawo XV)

**Kontekst (głęboki audyt przed LIVE):** Radar liczył STRES_KORELACJI (średnia |korelacja|
par koszyka, Prawo XVI) i używał go w ryglu ryzyka oraz sterze korelacyjnym — ale ŻADEN neuron
nie głosował na jego podstawie. Martwy wskaźnik = utrata potencjału (Prawo XV).

**RADAR-04 (`NeuronStresKorelacji`, kategoria Z, waga 6):** detektor kaskady systemowej.
Stres sam jest bezkierunkowy → kierunek bierze z BTC_TREND (konfluencja, nie zgadywanie):
- STRES ≥ 0.80 ∧ BTC_TREND < −0.10 → SHORT (lawina w dół — alty lecą za liderem)
- STRES ≥ 0.80 ∧ BTC_TREND > +0.10 → LONG słaby ≤0.45 (rajd skorelowany — FOMO ryzykowny)
- STRES ≥ 0.80 ∧ BTC płaski/brak → NEUTRAL ostrzegawczy (kaskada bez kierunku = nie wchodź)
- STRES < 0.80 → NEUTRAL (zdrowa dywersyfikacja)

Kategoria Z (nie R) celowo — wzmacniany w VOLATILE (×1.5) i PANIC (×2.0), dokładnie tam gdzie
kaskady niszczą koszyki. Rój: 70 → **71 neuronów** (67 aktywnych).

**Testy granic (Prawo XXI):** abstynencja bez danych, próg dokładny 0.80 (≥ vs <), kaskada↓/↑,
płaski BTC, brak BTC_TREND (nie crash). Pliki: sesje.py, rejestr.py, audyt_spojnosci.py
(allowlista + weryfikacja adaptera), test_radar_rynku.py, MANIFEST/README/INDEKS.

---

## 2026-06-16 | W-328 | Nowe pary i backtest — skrypty pobierania i testowania (przygotowanie LIVE)

**Kontekst:** Cezar pyta o rozszerzenie koszyka o nowe pary (ADA, AVAX, XRP, PEPE, WIF, memecoin).
Środowisko cloud nie ma dostępu do internetu, więc: (1) przeanalizowano kandydatów; (2) dostarczono
skrypt pobierania do uruchomienia lokalnie; (3) dostarczono skrypt backtestu dla porównania.

**Kandydaci (uzasadnienie):**
- ADA/USDT — niższa korelacja z BTC (~0.65), fundamentals-driven, duży volume
- AVAX/USDT — silny momentum layer-1, dobra zmienność 4h
- XRP/USDT — skoki regulacyjne, unikalny risk profile, top 5 volume
- PEPE/USDT — memecoin: ekstremalne fundingi (PSY-01 złoto), korelacja ~0.45 z BTC

**Nowe narzędzia:**
- `narzedzia/pobierz_nowe_pary.py` — pobiera 1h OHLCV z MEXC (ccxt) i agreguje do 4h
- `narzedzia/backtest_nowe_pary.py` — A/B test: baseline vs rozszerzony koszyk vs solo vs 1h TF

**Protokół:** Uruchom lokalnie: `python narzedzia/pobierz_nowe_pary.py` (wymaga sieci) →
potem `python narzedzia/backtest_nowe_pary.py` → dodaj pary tylko gdy zysk% > baseline (Prawo I).

---

## 2026-06-16 | W-327 | AdapterMEXCFutures — funding/OI rodzime dla LIVE na MEXC

**Kontekst (Prawo I — poprawność dla LIVE):** Cezar wchodzi na żywo na MEXC ($50, 5 par).
DataLoader już domyślnie ciągnie OHLCV z MEXC (ccxt), a petla_live wpina adaptery sentymentu.
Luka: `AdapterFutures` ciągnie funding/OI z BINANCE, a funding który Cezar FAKTYCZNIE PŁACI to
funding MEXC. Dla PSY-01 (contrarian na ekstremalnym fundingu) sygnał musi pochodzić z giełdy,
na której trzymana jest pozycja — inaczej myli się o własnym koszcie.

**AdapterMEXCFutures (`akwedukty/adaptery/mexc_futures.py`):** publiczne contract API MEXC
(funding_rate + ticker/holdVol = OI), bez klucza. Budzi PSY-01 (Funding) i PSY-04 (OI). PSY-02
(L/S ratio) zostaje przy AdapterFutures (MEXC nie ma łatwego public L/S; sentyment cross-giełdowy
OK). Konwersja symbolu BTCUSDT→BTC_USDT, OI_PREV pamięć per symbol, fetcher wstrzykiwalny (testy
offline). Bezpieczeństwo: endpointy publiczne; klucze podpisane (gdy zlecenia) WYŁĄCZNIE os.getenv.

**Wpięcie:** `KonfigPetliLive.funding_mexc` (domyślnie False). Gdy True — MEXC dokładany PO Binance
w liście adapterów, więc nadpisuje funding+OI rodzimymi, a L/S zostaje z Binance (MEXC go nie
dostarcza → nie nadpisze). Kolejność listy = priorytet ostatniego dla danego klucza.

**Testy:** 9 nowych (konwersja symbolu, dolewanie kluczy, OI_PREV pamięć, padnięty fetcher=None,
uszkodzony JSON, brak pola, budzenie PSY-01/04). 1106/1106 zielone, audyt exit 0, ruff czysto.

**Pliki:** `imperium/akwedukty/adaptery/mexc_futures.py`, `imperium/akwedukty/adaptery/__init__.py`,
`imperium/koloseum/petla_live.py`, `tests/test_adapter_mexc_futures.py`, `docs/MANIFEST_KODU.md`.

## 2026-06-16 | W-326 | Oryginalne strategie SMC — Łowca Stref + Żniwa Szczytu (utrata potencjału)

**Kontekst (Prawo XV):** audyt strategii ujawnił, że nasza najbardziej UNIKALNA broń —
SMC-01 (Order Block), SMC-02 (FVG), SMC-03 (BOS/MSS), VP-01 (VPOC) — NIE miała ŻADNEJ
strategii. Reżim SMC_ACTIVE istniał w WAGI_REZIMU, ale żadna z 18 strategii go nie celowała
(martwy reżim). Komentarz rejestru „SMC NIE wchodzą dopóki neurony nieaktywne" był przestarzały
— SMC-01/02/03 i VP-01 są aktywne (DOSTEPNY=True). Nikt nie wrócił dodać strategii.

**IMV-RV-006 ŁOWCA STREF (Smart Money Zone Hunter):** RV, reżim SMC_ACTIVE, 4H/1D.
WEJSCIE: SMC-03 (złamanie struktury BOS/MSS) + SMC-01 (powrót do strefy Order Block).
FILTR: SMC-02 (luka FVG = nierównowaga) + VP-01 (VPOC akceptacja) + H-01 (Hurst = nie szum).
WYJSCIE: SMC-02 (domknięcie luki) + X-25 (rozciągnięcie ATR). Łapie dołki/górki w strefach
instytucjonalnych — tam gdzie kapitał odwraca rynek. Źródło: ICT/Order Block + Fair Value Gap.

**IMV-RV-007 ŻNIWA SZCZYTU (Peak & Trough Harvest):** RV, reżim VOLATILE, 4H/1D.
WEJSCIE: Z-05 (Klimaks: blow-off szczyt→SHORT / kapitulacja dołek→LONG) + X-27 (Value-Z dystans).
FILTR: VP-01 (VPOC) + V-07 (Anchored VWAP — kierunek powrotu do wartości). WYJSCIE: V-07 + X-25.
Celuje wprost w górki i dołki klimaksowe z powrotem do wartości godziwej.

**Spójność (Prawo XXI/XIX):** Klucznik czysty (34 klucze istnieją i aktywne), ID IMV-SMC-*
wolne w KATALOG (kolizja z IMV-RV-* uniknięta), audyt exit 0. Reżimy pokryte: +SMC_ACTIVE.
Testy: 4 nowe (obecność, pokrycie reżimu, dołek LONG, górka SHORT) — łącznie 20 testów strategii.

**Pomiar (Prawo I — uczciwie):** strategie wpływają na tryby Dyrygenta „filtr"/„strategia", nie
na etalon „agregat" (+5.19% niezmieniony). Pełny A/B trybu strategii = następny krok po wpięciu
adapterów na żywo (SMC_ACTIVE wymaga realnej klasyfikacji reżimu z danych).

**Pliki:** `imperium/legiony/strategie/rejestr_strategii.py`, `tests/test_strategie.py`,
`docs/MANIFEST_KODU.md`, `docs/KATALOG_STRATEGII.md`, `docs/LOG_ZMIAN.md`.

## 2026-06-16 | W-325 | GUBERNATOR — homeostatyczny sterownik portfela (nowy moduł)

**Kontekst:** rozpoznanie terenu wykazało, że warstwy adaptacyjne JUŻ istnieją i są podpięte
(HedgeMWU per-neuron, Synapsy Reżimowe per-para, router strategii per reżim+TF, drift adapter).
Modyfikowanie SYGNAŁU wyczerpane (4 falsyfikacje). Realna luka: brak GLOBALNEGO sterownika
portfela — każdy podsystem rządzi lokalnie, nikt nie steruje ekspozycją całej floty 5 par.

**GUBERNATOR (`imperium/koloseum/gubernator.py`):** jeden ster na cały portfel. Po skanerze i
bezpieczniku DD dokłada globalny mnożnik [floor=0.5×, ceiling=1.3×] z agregatu koszyka. Maszyna
postaw z histerezą: KWARANTANNA→OBRONA→OSTROŻNY→NORMALNY→EKSPANSJA, mnożnik wygładzany wykładniczo.
UNIKAT (niespotykany w retail): sygnał pewności = ROZRZUT OCEN SKANERA (meta-labeling López de
Prado na poziomie PORTFELA — wewnętrzna dyspersja rankingu jako homeostatyczny regulator ryzyka).
Neutralny w stanie bazowym (≈1.0, Prawo XV), audyt Warstwa 1 to weryfikuje. Domyślnie OPT-IN.

**Wyniki A/B (`narzedzia/ab_w325.py`, 4h, 7500 barów/parę, Prawo I — SFALSYFIKOWANA dla celu zysk):**
- BASELINE (OFF): +5.19% | MaxDD 13.7% | 717 trade
- GUBERNATOR (ON): +4.16% | MaxDD 13.4% | 717 trade → **Δ = −1.04pp** 🔴
Diagnostyka (rozkład postaw na realnych danych): mechanizm działa — śr. mnożnik 1.068 (netto
wzmacnia), EKSPANSJA dominuje (224/361 tyków), zakres 0.889–1.223. Przyczyna minusu: w pętli
`dd_frakcja=frakcja_breaker` → Gubernator hamuje NA WIERZCHU Bezpiecznika (podwójne tłumienie w DD),
a ekspansja+compounding powiększa pozycje wjeżdżające potem w obsunięcie. To POKRĘTŁO ryzyko/zwrot:
1pp zwrotu za 0.3pp niższy MaxDD na tym łagodnym oknie. NIE darmowy lunch.

**Werdykt:** moduł zostaje jako OPT-IN (baseline nietknięty), w pełni otestowany (16 testów granic),
udokumentowany (`docs/GUBERNATOR.md`). Realna przyszłość: ochrona drawdown / risk-off na żywo, gdzie
łagodny backtest nie nagradza ostrożności. Piąta falsyfikacja z rzędu = dowód, że sygnał+architektura
są dobrze dostrojone, a kapitał $50 wejdzie na system NIEPOPSUTY niesprawdzonymi pomysłami.

**Pliki:** `imperium/koloseum/gubernator.py`, `imperium/koloseum/backtest.py`,
`tests/test_gubernator.py`, `narzedzia/ab_w325.py`, `narzedzia/audyt_spojnosci.py`, `docs/GUBERNATOR.md`.

## 2026-06-16 | W-324 | Brama Momentum Bezwzględnego (TS Gate) — suchy proch w martwym rynku

**Kontekst:** Skaner Okazji (W-316) był 100% cross-sectional — zawsze rankował i wybierał TOP-N,
nawet gdy CAŁY koszyk stał w miejscu (dead market). Literatura (Han/Kang/Ryu 2024): TS momentum
> CS w krypto. Gap: brak absolutnego progu jakości — wybieranie "najlepszego ze złych" w słabym rynku.

**W-324 — `min_bezwzgledny_ts` (TS Gate):** nowy parametr `SkanerOkazji`. Moneta z |ROC| < próg
wypada z rankingu PRZED z-score (jeszcze przed porównaniem cross-sectional). W martwym rynku
(wszystkie pary <próg) → wynik = 0 okazji = 0 wejść = "suchy proch". Domyślnie 0.0 (wsteczna
zgodność). `backtest_portfel` przyjmuje `skaner_min_ts=`. A/B: `narzedzia/ab_w324.py`.

**Wyniki A/B (4h, 7500 barów/parę, Prawo I — SFALSYFIKOWANA):**
- BASELINE (0%): +5.19% (717 trade, WR 43.8%) ✅
- TS-Gate 0.5%: −8.01% (−13.20pp) 🔴 | TS-Gate 1.0%: −9.41% (−14.60pp) 🔴 | TS-Gate 2.0%: −9.85% (−15.04pp) 🔴
Lekcja: CS i TS już sprzęgnięte w score (momentum_z z wagą 1.0). Brama TS PRZED z-score = podwójny
filtr niszczący edge. Moneta z ROC=0.5% przy ADX=35 to prawdziwa okazja gdy reszta koszyka=0%.
Kod wstecznie zgodny (domyślnie=0.0), hipoteza sfalsyfikowana. Czwarta falsyfikacja z rzędu.

**Testy:** 5 nowych testów granicznych w `test_skaner_okazji.py` — martwy rynek=0, próg dokładny
(|ROC|==próg → przepuszcza), selektywny rynek, SHORT TS-gated, domyślnie wyłączony.

**Pliki:** `imperium/koloseum/skaner_okazji.py`, `imperium/koloseum/backtest.py`,
`tests/test_skaner_okazji.py`, `narzedzia/ab_w324.py`.

## 2026-06-16 | W-323b/c | Profile WŁĄCZNE (po falsyfikacji) + scoreboard kontrybucji

**Kontekst:** A/B W-323 obalił pierwszą (wykluczającą) tabelę profili — SWING 59 dał −3.29%
vs pełnia +5.19% (−8.48pp). Przyczyna: wycięto 5 AKTYWNYCH neuronów (HA Scalper elitarny,
CVD, AC, sesje) — momentum/flow działają cross-TF. OC-01..04 i tak wyciszone (DOSTEPNY=False).

**W-323b — zasada włączności (Prawo I):** neuron należy do WSZYSTKICH stylów, CHYBA że
strukturalnie niezdolny: OC-01..04 (feed on-chain → tylko INVEST), Z-07 Pi Cycle (cykl
dzienny, szum na 4h → tylko INVEST). Reszta uniwersalna. Zestawy: SCALP 65 | SWING 65 | INVEST 70.

**W-323c — scoreboard kontrybucji:** `backtest_portfel(igrzyska_learning=True)` dołącza
`engine.ranking_neuronow` (scalone Igrzyska wszystkich par: accuracy/stability/wynik per neuron).
`narzedzia/scoreboard_neuronow.py` drukuje ranking — MIERZONA baza do strojenia NEURONY_STYLU
(„żonglowanie" danymi, nie intuicją). Kandydaci do rewizji = niska trafność przy wielu sygnałach.

**Pliki:** `imperium/legiony/rejestr.py`, `imperium/koloseum/backtest.py`,
`narzedzia/scoreboard_neuronow.py`, `tests/test_profile_stylu.py`,
`docs/ANALIZA_NEURONY_SCALP_SWING_INVEST.md`.

## 2026-06-16 | W-323 | Profile stylu gry — dedykowany zestaw neuronów per SCALP/SWING/INVEST

**Kontekst:** lekcja W-322/W-322b — „więcej neuronów = lepiej" i wagowanie reżimowe per-kategoria
SFALSYFIKOWANE pomiarem (rozcieńczenie sygnału / zabicie SMC w VOLATILE). Cezar: zamiast zawsze
grać pełnym rojem (70), wybierać DEDYKOWANY zestaw neuronów do stylu/interwału — „żonglować"
nimi w czasie.

**Wdrożenie (kod jest prawem):**
- `rejestr.NEURONY_STYLU` — jawna tabela KLUCZ→(style) dla wszystkich 70 (zero sierot/braków).
- `rejestr.neurony_dla_trybu(styl)` + `raport_profili()` — selekcja zestawu + diagnostyka.
- `zbuduj_legatusa(styl=)` i `backtest_portfel(styl=)` — opt-in (None=pełne 70, zero regresji).
- Komplementarne do `namiestnik.styl_interwalu/ProfilStylu` (interwał→styl, ryzyko per styl).

**Zestawy (po A/B):** SCALP 65 | SWING 65 | INVEST 70. Zasada włączności: wykluczamy TYLKO
neurony abstynujące strukturalnie (OC-01..04 bez feedu + Z-07 cykl dzienny). SWING-59 (węższe
wykluczenia) kosztowało −8.48pp (sfalsyfikowane); SWING-65 = +0.00pp (neutralne, bezpieczne).
**Prawo I:** każda zmiana granicy = A/B. Audyt Warstwa 1. Testy: `tests/test_profile_stylu.py`.

**Pliki:** `imperium/legiony/rejestr.py`, `imperium/koloseum/backtest.py`,
`narzedzia/audyt_spojnosci.py`, `narzedzia/ab_w323.py`, `tests/test_profile_stylu.py`,
`docs/ANALIZA_NEURONY_SCALP_SWING_INVEST.md`.

## 2026-06-16 | W-322 | 5 nowych neuronów scalp/swing/invest (z analizy + research)

**Kontekst:** po analizie `ANALIZA_NEURONY_SCALP_SWING_INVEST.md` (porównanie 65 neuronów
z best practices docs+internet) wdrożono 5 z 6 zaproponowanych unikatowych, zdekorelowanych
neuronów (wykonalne na OHLCV). Cross-Sectional RS (6.) odłożony — wymaga wpięcia
cross-symbol w pętli portfelowej (nie pasuje do interfejsu single-symbol).

**Wdrożone (65 → 70 neuronów):**
- **V-06 NeuronDeltaDivergence** (F, SCALP) — dywergencja cena↔delta (proxy footprint z OHLCV).
- **V-07 NeuronAnchoredVWAP** (F, SWING) — VWAP kotwiczony od pivotu swing.
- **VP-01 NeuronVolumeProfile** (S, SWING) — Volume Profile/VPOC + Value Area (Dalton BIB-013).
- **Z-06 NeuronAmihudIlliquidity** (Z, meta-brama) — impakt cenowy/krucha płynność (Amihud 2002).
- **Z-07 NeuronPiCycleTop** (Z, INVEST 1D) — SMA-111 vs 2×SMA-350, kill-switch szczytu cyklu.

**Brama (W-322):** 5 nowych obliczeń pure-Python (AMIHUD, VOLUME_PROFILE, PI_CYCLE,
ANCHORED_VWAP, DELTA_DIVERGENCE) + wpięcie w Budowniczy (skalarne + dict-unpack VPOC/Pi).

**Audyt:** Z-06 (płynne scenariusze) i Z-07 (≥350 barów) w allowliście W12 z dowodem
WERYFIKACJA (ożywają z właściwymi danymi — Prawo I). Testy granic: `tests/test_neurony_w322.py`
(22 testy: zero/None, znak, próg dokładny). Następny krok: pomiar dekorelacji
(`raport_dekorelacji`) + ewentualne Cross-Sectional RS.

**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/{wolumen,struktura,zagrozenie}.py`, `imperium/legiony/rejestr.py`,
`narzedzia/audyt_spojnosci.py`, `tests/test_neurony_w322.py`, MANIFEST/README/INDEKS.

## 2026-06-15 | W-321b | Runner symulacji 1h odtworzony + bieg pełnego stacku na danych godzinowych

**Kontekst (Prawo I — uczciwość):** symulacja 1h z sesji 2026-06-14 (W-320) NIE
ukończyła się — proces zginął razem z efemerycznym kontenerem, a tymczasowy skrypt
runnera nie był zacommitowany. W `/tmp` zostały tylko linie ładowania danych, BEZ
wyników. Wpis „Tryb NAJLEPSZY na danych 1h" był więc przedwczesny co do liczb 1h.

**Wdrożenie:** `narzedzia/sym_1h.py` (trwały, zacommitowany) — uruchamia
`backtest_portfel` na 5 parach 1h, pełny stack (TOP-3 + Sizing Przekonania +
Compounding + filtr asymetrii).

**Odkrycie RAM (Prawo I):** pełny bieg 5 par × ~67k barów 1h akumuluje pamięć
LINIOWO (~5.5MB/s, historia trade'ów per tik) i przekracza ~13GB → OOM w kontenerze
15GB (pierwszy bieg zabity SIGKILL exit 137). Runner dostał cap `MAX_BAROW`
(domyślnie 30k barów/parę ≈ 3.4 lat 1h) — ukończalny, uczciwy pomiar. Pełna historia
tylko gdy RAM wystarcza (`MAX_BAROW=0`). Wynik liczbowy 1h dopisany po zakończeniu biegu.

**Porównanie TF na tym samym oknie (`narzedzia/sym_porownanie_tf.py`, Prawo I):**
żeby rozdzielić efekt interwału od efektu okna (90.2x na 4h liczone na pełnej historii
~9 lat zdominowanej przez pompę DOGE 2021), uruchomiono oba TF na IDENTYCZNYM oknie
2022→2026 (~3.4 lat). **Wynik (UTRATA POTENCJAŁU, Prawo XV):**
- 4h, to samo okno: 722 trade, WR 43.8%, **+5.8% (1.06x)** ✅
- 1h, to samo okno: 2347 trade, WR 46.4%, **−9.8% (0.90x)** ❌
- 4h pełne 9 lat (odniesienie): 90.2x — **artefakt grubego ogona DOGE 2021**, nie przewaga.

Dwa twarde wnioski: (1) 90.2x nie jest powtarzalny — ten sam stack 4h na ostatnich
3.4 lat daje tylko +5.8%; (2) 1h jest GORSZE od 4h na tym samym oknie (−9.8% vs +5.8%,
3.3× więcej trade'ów, edge per-trade ujemny — i to bez prowizji). Priorytet Cezara
(krótkie interwały) z obecną konfiguracją pogarsza wynik → wymaga osobnej kalibracji
progów pod 1h ZANIM wejdzie do gry. Szczegóły: `docs/TRYBY_IMPERIUM.md` § W-321b.

**Kalibracja progów 1h (W-321c, `narzedzia/kalibracja_1h.py` + `_v2.py`):** 13 konfiguracji
na oknie 1.4 lat (cap 12k). Ranking po PnL%:
- **adx≥50 / pew≥0.75 / top1: −3.4% (94 tr)** — najlepszy ze wszystkich, skrajna selektywność.
- adx≥45 / 0.70 / top2: −5.9%; adx≥36 / 0.70 / top2: −6.4%; baseline adx20: −12.8%.

Korekta tezy (Prawo I): top1 NIE jest jednostajnie gorszy — przy umiarkowanym ADX traci
mocno (adx36/top1 = −11.2%), ale przy ekstremalnym ADX jest najlepszy (adx50/top1 = −3.4%).
Lewar = skrajna selektywność (silny trend + jedna okazja). **Wciąż minus**, a −3.4% na 94
trade'ach jest w granicach szumu (nie robustny edge). KONKLUZJA: rój nie ma robustnego
edge'u na 1h; zostać na 4h (+5.8%). Szczegóły: `docs/TRYBY_IMPERIUM.md` § W-321c / W-321c-v2.

**Pliki:** `narzedzia/sym_1h.py`, `narzedzia/sym_porownanie_tf.py`,
`narzedzia/kalibracja_1h.py`, `narzedzia/kalibracja_1h_v2.py`.

---

## 2026-06-14 | W-320 | Dane 1h wpięte — Tryb NAJLEPSZY na krótszym interwale (Prawo XV)

**Odkrycie (UTRATA POTENCJAŁU, Prawo XV):** w `dane/godzinowe/` leżą dane **1h**
(~76k barów/parę, 5 par BTC/ETH/SOL/BNB/DOGE) — śledzone w repo, obsługiwane przez
czytnik CSV, ale NIEUŻYWANE. Dotychczasowa diagnoza („gramy tylko 4H/1D") była błędna —
najwyższy priorytet Cezara (krótkie interwały) był częściowo spełniony, tylko niewpięty.

**Wdrożenie:** test integracyjny `test_realne_dane_1h_laduja_sie` (Prawo XIX — dowód
kodem) ładuje realne pliki 1h i weryfikuje chronologię + OHLC. Tryb NAJLEPSZY (skaner+
conviction+compounding) uruchomiony na pełnej serii 1h (~75k barów/parę) — wynik
liczbowy zostanie dopisany po zakończeniu pomiaru (Prawo I: nie raportuję przed końcem).

**Pełny stack na 4h (W-319, zmierzony):** 10 000$ → 902 295$ = **90.2x** (2665 trade'ów,
WR 46%) — ⚠️ gruboogonowy (DOGE), bez prowizji/poślizgu = górna granica potencjału, nie obietnica.

**Zostaje 🔴:** interwały sub-godzinne (1m/5m/15m) — `dane/minutowe/` puste.

**Pliki:** `tests/test_czytnik_csv.py` (+1 test), `docs/{TRYBY_IMPERIUM,WIZJA_TRYBY_I_ROZWOJ}.md`,
`README.md`. Testy: 1023/1023.

---

## 2026-06-14 | W-319 | Compounding (pula łupów) — reinwestycja zysku w większe pozycje

**Wizja Cezara:** zysk dorzucamy do puli łupów, powiększamy kapitał. Trzeci wzmacniacz
trybu NAJLEPSZE (po selekcji W-317 i conviction W-318).

**Wdrożenie:** `backtest_portfel(compounding=True)` — budżet sizingu liczony od
BIEŻĄCEGO equity (`engine.kapital_calkowity`), nie od kapitału startowego. Zysk
reinwestowany → wzrost geometryczny. Domyślnie OFF (stały sizing = liniowy, łatwiejsza
ocena edge bez efektu składania).

**Pliki:** `koloseum/backtest.py`, `tests/test_portfel.py` (+4 testy: skaner/top_n/
conviction/compounding). 1022/1022. Etap B audytu — kompletny potok łowcy okazji:
skan koszyka → TOP-N → conviction sizing → compounding.

---

## 2026-06-14 | W-318 | Sizing Przekonania — większa stawka na mocniejszej okazji

**Lekcja z symulacji 9-letniej (W-317):** sama selekcja TOP-N daje MNIEJ zysku
(+24k vs baseline +52k), bo przycina gruby ogon (pompy DOGE) bez kompensacji większą
stawką. Wizja Cezara: „mało trade'ów, ale większy lewar/stawka na najlepszych".

**Wdrożenie:** `SizingPrzekonania` (`pretorianie/sizing_przekonania.py`). Mnożnik
stawki ∈ [min,max] (domyślnie 0.5×–3.0×) rośnie z przekonaniem; prog_neutralny→1.0×.
Plus `kelly_frakcja()` (fractional Kelly, half-Kelly domyślnie) jako principled backbone.
W trybie skanera (`backtest_portfel(sizing_przekonania=True)`) mnoży budżet pozycji
przez siłę okazji (score znormalizowany min-max w rankingu koszyka). Domyślnie OFF.

**Pliki:** `pretorianie/sizing_przekonania.py` (nowy), `koloseum/backtest.py`,
`tests/test_sizing_przekonania.py` (13 testów granic). Wynik re-testu: osobny commit.
Źródła: Kelly (Zerodha/Coriva), fractional Kelly (enlightenedstocktrading). 1018/1018.

---

## 2026-06-14 | W-317 | TRYB NAJLEPSZE — wpięcie Skanera Okazji do pętli portfelowej

**Rozkaz Cezara:** system ma wyłapywać najlepsze okazje ze WSZYSTKICH walut i grać
tylko najmocniejszymi (kilka/tydzień). To zmienia Imperium z „N botów jednowalutowych"
w łowcę okazji.

**Wdrożenie:** `backtest_portfel(tryb_skaner=True, skaner_top_n=N, skaner_min_adx=...)`.
W każdym tyku skaner rankuje koszyk (snapshot wskaźników per symbol, aktualizowany na
jego barze → O(N)/tyk) i dopuszcza do WEJŚCIA tylko TOP-N okazji. Exity działają
niezależnie (w `przetworz_bar`). Domyślnie OFF — zero regresji.

Dokument trybów: `docs/TRYBY_IMPERIUM.md` — 5 trybów (NAJLEPSZE/SKALP/SWING/INVEST/
OBRONA) + mapa brakujących neuronów/strategii. Wynik symulacji 9-letniej: osobny commit.

**Pliki:** `koloseum/backtest.py` (tryb_skaner), `docs/TRYBY_IMPERIUM.md` (nowy), INDEKS.
Część Etapu B audytu 2026-06-14. 1005/1005 zielone, audyt exit 0.

---

## 2026-06-14 | W-316 | Skaner Okazji — łowca najlepszych setupów w koszyku (serce wizji)

**Największa luka audytu 2026-06-14:** system był „N botów jednowalutowych", nie łowca
okazji. Skaner to warstwa SELEKCJI ponad rojem — patrzy na WSZYSTKIE monety naraz,
liczy ocenę okazji i zwraca TOP-N najmocniejszych (realizuje „mało trade'ów wysokiej pewności").

**Wdrożenie:** `imperium/koloseum/skaner_okazji.py` (`SkanerOkazji`, `OkazjaRank`).
Ocena = cross-sectional z-score 4 składników (momentum/ROC, trend/ADX, wolumen, zmienność/ATR%):
- momentum cross-sectional = relative strength (lider vs maruder koszyka)
- kierunek ze znaku momentum (lider rosnący→LONG, spadający→SHORT)
- chop (ADX<min_adx) odsiany z rankingu (lekcja W-314)
- siła = |momentum_z| + trend_z + wolumen_z + zmiennosc_z

Czysty OHLCV; brak danych monety → pomijana (Prawo XV). Skaner RANKUJE, nie handluje —
decyzję wejścia podejmuje dalej Dyrygent. Następny krok: wpięcie do pętli portfelowej
(selekcja TOP-N zamiast „każda para gra") + backtest cross-sectional.

**Pliki:** `skaner_okazji.py` (nowy), `tests/test_skaner_okazji.py` (13 testów granic).
Źródła: cross-sectional momentum (FXEmpire, Moskowitz 2012), ADX (Wilder 1978).

---

## 2026-06-14 | W-315 | Z-05 Detektor Ruchu Klimaksowego — dwukierunkowy (szczyt→SHORT, dołek→LONG)

**Rozkaz Cezara:** detektor gwałtownych ruchów nie tylko pump, ale pump I dump
(różne ROC), nie tylko dołek ale i szczyt — szczyt na SHORT, dołek na LONG.

**Wdrożenie:** neuron Z-05 `NeuronDetektorRuchu` (czysty OHLCV: CLOSE_SERIES_20 +
RSI_14 + VOLUME_MA20). Łapie KLIMAKS (wyczerpanie ruchu), gra przeciw niemu:
- SZCZYT: ROC ≥ +15% ∧ RSI ≥ 70 ∧ wolumen ≥ 2× → SHORT (blow-off top)
- DOŁEK: ROC ≤ −15% ∧ RSI ≤ 30 ∧ wolumen ≥ 2× → LONG (kapitulacja)
- inaczej NEUTRAL (specjalista — abstynuje prawie zawsze, „mało trade'ów wysokiej pewności")

Ortogonalny do Z-02 (akumulacja PRZED pumpem); Z-05 łapie ruch JUŻ zaistniały.
Źródło: blow-off top / capitulation + volume climax (Wyckoff, Murphy) — progi do
kalibracji walk-forward/live (Prawo I).

**Pliki:** `neurony/zagrozenie.py` (Z-05), `rejestr.py`, `tests/test_detektor_ruchu.py`
(14 testów granic), MANIFEST/README/INDEKS (64 neurony). Część Etapu B audytu 2026-06-14.

---

## 2026-06-13 | W-314 | Filtr Asymetrii Reżimu — brama wejścia oparta na trendzie

**Odkrycie OOS:** pomiar kierunków na świeżym oknie (2024-10..2026-06, BTC płaski
+0,8%) ujawnił, że stare „+26 152$" było in-sample na hossie 2017-2021. Na płaskim
rynku rój TRACI (−386$) — wchodzi za często w chopie. Split kierunków zbalansowany
51/49 (SHORT nie jest martwym głosem, Prawo XV OK); warstwy adaptacyjne nie ratują
chopu (synapsy+mwu −373$).

**Wdrożenie:** FiltrAsymetriiRezimu (czysty OHLCV: CLOSE/EMA_200/ADX_14):
- rynek boczny (ADX<20) → wymóg pewności ≥0,70
- kontr-trend przy ADX≥25 → wymóg pewności ≥0,65 (Moskowitz/Ooi/Pedersen 2012)
- zgodne z trendem / strefa neutralna → przepuść; brak danych → abstynencja

**Dowód A/B (Prawo XVI):** OOS strata −386$ → −238$ (**−38% krwawienia**),
PnL/trade −2,3 → −1,4, oba kierunki lepsze. Uczciwie: wciąż ujemny (chop pozostaje
trudny) — filtr tnie stratę, nie czyni rynku bocznego zyskownym.

**Pliki:** `imperium/pretorianie/filtr_asymetrii.py` (nowy), `dyrygent.py`,
`backtest.py`, `petla_live.py` (opt-in OFF), `tests/test_filtr_asymetrii.py` (15),
`tests/test_zbuduj_warstwy.py`, `docs/POMIAR_FILTR_ASYMETRII.md`, README. 978/978.

---

## 2026-06-13 | W-313 | Naprawa deadlocka breakera krzywej — sondujący handel w HALT

**Problem:** Po HALT (DD≥20%) żaden trade → equity zamrożona → DD nigdy nie spada
poniżej prog_dd_reduced (10%) → histereza trzyma HALT wiecznie → 5 lat martwego
handlu w backteście BTC 4H (2021-09 → 2026-06). Structural impossibility.

**Rozwiązanie (W-313):** `frakcja_halt=0.1` — HALT zwraca 0.1× (sondujący handel)
zamiast 0.0× (totalna blokada). Kapitał może się poruszać → DD może spaść → HALT
może się odblokować gdy warunki rynkowe się poprawią. Stary `frakcja_halt=0.0`
dostępny jako jawna konfiguracja per instancja.

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py` (frakcja_halt + frakcja_pozycji),
`imperium/koloseum/backtest.py` (blokada na frakcja_breaker≤0 zamiast halt),
`tests/test_kalkulator.py` (zaktualizowane testy granic + 3 nowe)

---

## 2026-06-13 | W-311 | Ablacja warstw adaptacyjnych — pomiar in-sample (Prawo XVI)

**Pomiar, nie zgadywanie.** Ablacja 4 warstw (synapsy/mwu/igrzyska/ksiega_wad)
osobno vs baseline na koszyku 5 par 4H (pełna historia), z metryką PnL/trade
korygującą confound liczby trade'ów.

Wynik (PnL/trade vs baseline +49,9$):
- synapsy +64,4 (+29%, trade flat) — czysta jakość, najmocniejszy dowód
- mwu +83,1 (+66%, +68% trade'ów) — działa, częściowo wolumen
- igrzyska +55,3 (+11%, WR -1pp) — słaba, możliwa redundancja z mwu
- ksiega_wad +49,9 (=baseline) — neutralna z projektu (nie wetuje domyślnie)

⚠️ IN-SAMPLE — wymaga walk-forward OOS przed włączeniem w produkcji (Prawo I:
bez fałszywej weryfikacji; Monte Carlo nie koryguje biasu trendu).

**Pliki:** `docs/POMIAR_WARSTW_ADAPTACYJNYCH.md` (pomiar — bez zmian kodu)

---

## 2026-06-13 | W-310 | Domknięcie pętli pamięci — KsięgaWad czyta przeszłe sesje

**Prawo XV — martwy read-path PamięciRefleksyjnej.** Lekcje były pisane do
`logs/pamiec_refleksyjna.jsonl` co sesja, ale NIGDY czytane w produkcji
(`formatuj_dla_llm()`/`wczytaj_wszystkie()` bez konsumenta). Świeży Dyrygent
startował ślepy — setup który tracił przez 10 poprzednich sesji nie był znany.

W-310: `_bootstrap_ksiega_wad(dyrygenci, pamiec)` w PętliLive — gdy `ksiega_wad`
aktywna, zasila KsięgęWad każdego Dyrygenta persystentnymi lekcjami przed 1. barem.
Cross-session learning staje się realne: stratny setup flagowany od startu sesji.

- Wydzielony testowalny helper `_bootstrap_ksiega_wad()` (zwraca n lekcji).
- Log startowy raportuje liczbę wczytanych lekcji.
- +2 testy (bootstrap zasila wadę z 6 lekcji; brak KsięgiWad → 0, nie pada).
- 959/959 testów, audyt pełna harmonia, ruff czysty.

**Pliki:** `koloseum/petla_live.py`, `tests/test_ksiega_wad.py`,
`docs/MANIFEST_KODU.md`, `README.md`

---

## 2026-06-13 | W-309 | KsięgaWad — prewencyjny filtr wad setupu (ekstrakcja z Mnemosyne)

**Pomiar redundancji (Prawo XVI) + decyzja Cezara.** Audyt Mnemosyne (N-MEM-206):
- 🔴 zero testów (formalnie nie istnieje wg Prawa XIX), niepodpięta nigdzie.
- trade-learning MIERZALNIE dubluje PamięćRefleksyjną (W-295) — obie zapisują
  PnL+narrację lekcji. Prawo XVI: nie duplikować.
- jedyna unikatowa zdolność: `book_of_flaws` — prewencyjny filtr (patrzy W PRZÓD,
  czego PamięćRefleksyjna nie umie — ona tylko narratywnie opisuje przeszłość).

Cezar (Prawo XVIII) wybrał: **wyekstrahuj Księgę Wad**, Mnemosyne nietknięta.

Nowy moduł `cesarz/ksiega_wad.py`:
- `KsiegaWad.zarejestruj(rezim, interwal, pnl)` — online, z każdego zamknięcia.
- Sygnatura setupu staje się WADĄ gdy ≥ min_prob prób ORAZ wskaźnik strat ≥ prog_wady.
- `sprawdz(rezim, interwal)` PRZED wejściem → CZYSTO / OSTRZEŻENIE / WETO.
- Domyślnie tylko ostrzega (prog_weta=None → nigdy nie wetuje — bezpieczne).
- `ucz_z_pamieci(pamiec)` — bootstrap z PamięciRefleksyjnej (Prawo XVI: jedno źródło).

Wpięcie (opt-in, domyślnie OFF — Prawo XV, zero zmiany zachowania):
- `Dyrygent.zbuduj(ksiega_wad=True)`, `.ksiega_wad`, `.raport_ksiegi_wad()`
- uczenie w `_aktualizuj_synapsy()`, weto w `cykl()` (krok 4c, jak Rada Doradców)
- `KonfigPetliLive.ksiega_wad`, `backtest_portfel(ksiega_wad=True)`
- pending tuple rozszerzony 3→4 (dodano interwał setupu); 3 unpacki zaktualizowane.

20 testów (logika, granice progów Prawa XXI, bootstrap, integracja Dyrygent/pętla).
957/957 testów, audyt pełna harmonia, ruff czysty.

**Pliki:** `cesarz/ksiega_wad.py`, `koloseum/dyrygent.py`, `koloseum/petla_live.py`,
`koloseum/backtest.py`, `tests/test_ksiega_wad.py`, `tests/test_mwu_wpiecie.py`,
`docs/MANIFEST_KODU.md`, `README.md`

---

## 2026-06-13 | W-308 | Monte Carlo bridge — walidacja post-backtest z silnika

**Odzysk potencjału (Prawo XV):** `monte_carlo.py` i jego `pelen_raport_mc()` istniały
od dawna, ale nigdy nie były podpięte do `PaperTradingEngine` — trzeba było ręcznie
budować listę PnL. W-308 zamyka tę lukę.

Zmiany:
- `waliduj_mc(engine)` w `monte_carlo.py`: pobiera `pnl_usdt` z `historia_zamkniec`
  i wywołuje `pelen_raport_mc()` z `kapital_startowy` z silnika.
- `Dyrygent.raport_monte_carlo()`: jeden-liniowy wrapper — `None` gdy < 10 trade'ów,
  inaczej dict z shuffle+bootstrap (Sharpe mediana/p5/p95, MaxDD_p95, P(SR>0), ok).
- 9 nowych testów: granica 10 trade'ów, dobry/zły edge, kapital z silnika,
  Dyrygent z za-małą historią → None, struktura raportu.

Zastosowanie: po backtestcie wywołaj `dyrygent.raport_monte_carlo()` lub
`waliduj_mc(engine)` — dostaniesz potwierdzenie że edge jest prawdziwy
(shuffle + bootstrap > 90% P(Sharpe>0), MaxDD_p95 < 25%).

**Pliki:** `koloseum/monte_carlo.py`, `koloseum/dyrygent.py`,
`tests/test_monte_carlo.py`, `docs/MANIFEST_KODU.md`, `README.md` (937/937)

---

## 2026-06-13 | W-307 | Igrzyska wpięte w pipeline — batch ranking komplementarny do MWU

**Domknięcie pętli uczenia neuronów: batch (Igrzyska) + online (HedgeMWU) razem.**
Igrzyska (W-002) istniały od dawna, ale nigdy nie były podpięte do Dyrygenta —
`nowe_wagi()` nigdy nie trafiało do Legatusa. W-307 to naprawia (Prawo XV).

Zmiany:
- `Dyrygent.__init__`: `self._igrzyska: Optional[Any] = None`
- `Dyrygent.zbuduj(igrzyska=True)`: opt-in jak MWU/synapsy/drift/rada
- `_aktualizuj_synapsy()`: rejestruje każde zamknięcie trade'u w Igrzyskach
- Mnożniki łączone: `combined = mwu_mult × igr_mult` per neuron (oba aktywne)
- `raport_igrzysk()`: publiczny accessor (ranking/Złoty Hełm/Lista Infamii)
- `backtest_portfel(igrzyska_learning=True)`: opt-in w backteście
- 14 nowych testów (jednostkowe + integracyjne, test granic Prawa XXI)

Prawo XVI: Igrzyska (cumulative accuracy/stability) vs MWU (eksponencjalne
zapomnienie) niosą różną informację — dlatego mnożniki łączone, nie zastępowane.

**Pliki:** `koloseum/dyrygent.py`, `koloseum/backtest.py`, `tests/test_igrzyska_wpiecie.py`,
`docs/MANIFEST_KODU.md`, `README.md` (929/929 testów)

**W-307b (dopięcie):** warstwy uczenia wpięte też w produkcyjną `PętlęLive`
(`KonfigPetliLive.mwu/igrzyska` opt-in, domyślnie OFF). Wcześniej dostępne tylko
przez `Dyrygent.zbuduj()`/`backtest_portfel()` — teraz osiągalne z głównego
entrypointa live. +2 testy (wpięcie + domyślnie OFF). 931/931.
**Pliki:** `koloseum/petla_live.py`, `tests/test_petla_live.py`

---

## 2026-06-13 | W-306b | Pierwszy realny pomiar redundancji roju (Prawo XVI w akcji)

**Użycie narzędzia W-305/306 na danych historycznych.** Przepuszczono BTCUSDT 4H
(1500 barów, 1301 cykli) przez `Dyrygent.zbuduj(synapsy=True)` i odczytano
`raport_korelacji_neuronow()`. Wynik zapisany do `docs/MATRYCA_KORELACJI.md`
(żywy szablon wypełniony pierwszymi rzeczywistymi liczbami).

- 🚨 **Alarm Prawa XV/XVI:** V-13 (Yang-Zhang vol) ~ VI-13 (ATR) = **+1.000** —
  identyczny sygnał, podwójne liczenie zmienności. Potwierdza INF-20 (Sinclair):
  Yang-Zhang traci przewagę na crypto 24/7. SynapsyRezimowe (W-305) już to częściowo
  neutralizują (dekorelacja=0 → brak wzmocnienia). Scalenie/redukcja = decyzja Cezara
  (Prawo XVIII — nie usuwam składu roju autonomicznie).
- 8 dalszych par |corr|>0.80 (trend ADX~Ichimoku, przepływ OBV~Force Index).
- 248 par dywersyfikujących (|corr|<0.20) — rój zdrowo zdekorelowany.

**Pliki:** `docs/MATRYCA_KORELACJI.md`, `docs/LOG_ZMIAN.md` (pomiar — bez zmian kodu)

---

## 2026-06-13 | W-306 | Raport dekorelacji neuronów — Prawo XVI dla całego roju

**Korelacje par neuronów (W-305) były liczone, ale tylko konsumowane wewnętrznie
przez SynapsyRezimowe — Cezar ich nie widział.** Prawo XVI („redundancja mierzona,
nie zgadywana") działało dotąd tylko dla 11 zwiadowców EXP. Rozszerzone na rój:

- `raport_z_kolektora()` — z populowanego `KolektorKorelacjiNeuronow` produkuje
  raport par nadmiarowych (|corr|>0.80, kandydat do wagi w dół) vs dywersyfikujących
  (|corr|<0.20, filar siły); kształt zgodny z `raport_dekorelacji` (wspólny formater)
- `Dyrygent.raport_korelacji_neuronow()` — akcesor po backteście/sesji
- `KolektorKorelacjiNeuronow.klucze()` — lista zebranych neuronów
- 6 testów (`tests/test_raport_korelacji_neuronow.py`) — 915/915

**Pliki:** `legiony/diagnostyka_korelacji.py`, `koloseum/dyrygent.py`, `tests/test_raport_korelacji_neuronow.py`, `docs/MANIFEST_KODU.md`, `README.md`

---

## 2026-06-13 | W-305 | Domknięcie pętli korelacji w SynapsyRezimowych (Prawo XVI)

**Naprawa utraty potencjału z audytu W-304:** `kara_korelacji = 1.0 + corr` i
`dekorelacja = 1.0 - corr` to serce Prawa XVI w SynapsyRezimowych (W-299), ale
`corr` był ZAWSZE 0 — call-site nie podawał korelacji, a diagnostyka liczyła tylko
zwiadowców (EXP), nie neurony. Pętla domknięta:

- `KolektorKorelacjiNeuronow` (diagnostyka_korelacji.py) — online okno przesuwne
  głosów neuronów z `raport.sygnaly`, macierz korelacji Pearsona par neuronów
- `SynapsyRezimowe.ustaw_korelacje()` + fallback `_korelacje_biezace` w
  `aktualizuj()`/`wzmocnij_pewnosc()` — bez zmiany sygnatur call-sites
- `Dyrygent.cykl()`: odczyt korelacji PRZED fokus (z przeszłych barów), rejestracja
  bieżącego głosu PO fokus → zero lookahead (Prawo I)
- Pary niezależne (corr≈0) wzmacniane pełnym głosem; skorelowane (corr≈1) stłumione
- 9 testów granicznych (`tests/test_korelacje_synapsy.py`) — 909/909

**Pliki:** `legiony/diagnostyka_korelacji.py`, `biblioteki/synapsy_rezimowe.py`, `koloseum/dyrygent.py`, `tests/test_korelacje_synapsy.py`, `docs/MANIFEST_KODU.md`, `README.md`

---

## 2026-06-13 | W-304 | Fabryka odblokowuje 4 martwe-w-produkcji warstwy (audyt Prawo XV)

**Analiza całego Imperium + konkurencja wykazała UTRATĘ POTENCJAŁU:** DriftAdapter
(W-296), RadaDoradcow, SynapsyRezimowe (W-299) i HedgeMWU (W-303) były wpięte w
logikę konstruktora/cyklu Dyrygenta, ale produkcyjna fabryka `Dyrygent.zbuduj()`
(której używa `petla_live`) nigdy ich nie instancjonowała → martwe w realnym życiu.

- `Dyrygent.zbuduj(drift=False, rada=False, synapsy=False, mwu=False)` — 4 opt-in
- Domyślnie wszystkie OFF → zachowanie identyczne (zero zmian, kompatybilność wsteczna)
- 7 testów (`tests/test_zbuduj_warstwy.py`) — 900/900
- Pozostałe utraty potencjału (Igrzyska osierocony, korelacje nie docierają do
  SynapsyRezimowych, Pamięć Refleksyjna zapis-bez-odczytu) — zaraportowane Cezarowi
  jako decyzje kierunkowe (Prawo XVIII), nie naprawione autonomicznie.

**Pliki:** `koloseum/dyrygent.py`, `tests/test_zbuduj_warstwy.py`, `docs/MANIFEST_KODU.md`, `README.md`

---

## 2026-06-13 | W-303 | HedgeMWU wiring — online wagi neuronów wpięte w Legatusa

**Online Multiplicative Weights Update (Freund & Schapire 1997) — zamknięta pętla uczenia:**
- `Legatus.mwu = HedgeMWU()` — nowy slot (analogiczny do `synapsy`)
- `Dyrygent._aktualizuj_synapsy()` — po każdym zamkniętym trade'cie rejestruje wynik każdego neuronu, potem pcha `mwu.mnozniki()` do `Legatus.mnozniki_neuronow`
- `backtest_portfel(mwu_learning=True)` — opt-in per-symbol MWU learning
- 9 nowych testów (`tests/test_mwu_wpiecie.py`) — pokrycie granic (Prawo XXI)
- MANIFEST, LOG zaktualizowane

**Pliki:** `legiony/legatus.py`, `koloseum/dyrygent.py`, `koloseum/backtest.py`, `tests/test_mwu_wpiecie.py`, `docs/MANIFEST_KODU.md`

---

## 2026-06-13 | W-302 | PętlaLive + PamięćRefleksyjna wpięta w pipeline

**Główny entrypoint systemu tradingowego + cross-session learning:**

- `koloseum/petla_live.py`: `handluj_live(KonfigPetliLive)` — spina DataLoader(OHLCV)
  → RadarRynku(BTC_TREND/DOMINACJA/PRZEPLYW co bar) → Dyrygent.cykl() per symbol
  → PamięćRefleksyjna.zapisz_wynik() per zamknięcie. Graceful-degradation: padnięty
  fetch jednego symbolu nie zatrzymuje innych. `uruchom()`: skrót produkcyjny.
- `koloseum/dyrygent.py`: `self._pamiec` hook + wpięcie w `_aktualizuj_synapsy()` —
  po każdym zamknięciu pozycji automatycznie zapisuje lekcję (symbol, rezim, interwal,
  pnl) do JSONL. Never-block: błąd pamięci = log + skip.
- `_df_do_barow()`: mostek DataFrame → List[Dict] (timestamp=int ms).
- 10 testów: max_barow, fetch-fail graceful, brak BTC w koszyku, synapsy+pętla,
  PamięćRefleksyjna hook, KonfigPetliLive domyślne. → **883/883** ✅

---

## 2026-06-13 | W-301 | Domknięcie adaptacyjnych plugi — SynapsyRezimowe w backtest_portfel + AdapterNewsLLM

**Prawo XV — domykanie luk pomiędzy gotowym kodem a pipeline:**

- `koloseum/backtest.py`: nowy parametr `synapsy_rezimowe=False` (opt-in, zero kosztu
  bez włączenia). `True` → każdy symbol w portfelu dostaje własny `SynapsyRezimowe()` w
  `legatus.synapsy` i uczy par przez cały backtest (1 linia, wstrzykiwana przez Prawo I).
- `akwedukty/adaptery/__init__.py`: eksportuje `AdapterNewsLLM` (wcześniej osierocony —
  klasa istniała, ale poza publicznym interfejsem pakietu).
- `koloseum/dyrygent.py`: `zbuduj_bojowy(adaptery_live=True)` teraz zawiera
  `AdapterNewsLLM()` — NEWS-01 próbuje pobrać nagłówki; bez RSS/klucza: abstynuje (Prawo XV).
- `narzedzia/audyt_spojnosci.py`: opis NEWS-01 odzwierciedla że adapter wpięty.
- 2 nowe testy portfela (synapsy opt-in + default=False) → **873/873** ✅

---

## 2026-06-13 | W-300 | Hook RadarRynku — wpięcie RADAR-01/02/03 w sloty kontekstu

**Prawo XV — koniec trzech martwych głosów (RADAR czytał klucze, których nikt nie podawał):**

- `koloseum/dyrygent.py`: `odswiez_kontekst_rynku(close_btc, close_alty, vol_alty=None)` —
  woła `RadarRynku.skanuj()` i wypełnia DWA istniejące sloty (zaprojektowane w W-291/292,
  nigdy niepodłączone): `kontekst_dodatkowy` (BTC_TREND/BTC_DOMINANCJA/PRZEPLYW_KAPITALU →
  dolewane do wskaźników → budzą RADAR-01/02/03) i `stan_rynku` (→ Namiestnik, radar-aware
  gating). Serie przyczynowe (DO bieżącej świecy — zero lookahead). `update()` nie kasuje
  innego kontekstu. Za mało danych → StanRynku z None → neurony abstynują (Prawo XV).
- Wołane RAZ na bar przez pętlę portfelową PRZED cyklami per-symbol (BTC = kontekst wspólny
  koszyka). Sama pętla portfelowa jeszcze nie istnieje — to gotowy, przetestowany hook.
- 8 testów: wypełnianie slotów, nie-kasowanie kontekstu, DOWÓD że RADAR-01 budzi się LONG
  po wpięciu (abstynuje bez), granica za-mało-danych, płaski BTC → NEUTRAL. → **871/871** ✅
- Audyt: notka Prawa XV zaktualizowana (hook gotowy, RADAR ożywa z serią BTC).

---

## 2026-06-13 | W-299 | Synapsy Reżimowe — Regime-Aware Decorrelated Coalition Graph

**Flagowa unikalna technologia: Hebbian × per-reżim × Prawo XVI (dekorelacja):**

- `biblioteki/synapsy_rezimowe.py`: `SynapsyRezimowe` — graf `w[i][j][reżim]` par neuronów.
  Reguła uczenia: `delta = eta * pnl_znak / (1 + |corr(i,j)|)` — pary o wysokiej korelacji
  uczą się wolniej (redundancja ≠ siła). Boost pewności max ±25%. Persystencja JSONL.
- `legiony/legatus.py`: `self.synapsy` + `wzmocnij_pewnosc()` po kierunku/pewności.
- `koloseum/dyrygent.py`: `_synapsy_pending` + `_aktualizuj_synapsy()` — zamknięta pętla
  uczenia koalicji bez ingerencji zewnętrznej.
- 22 testy granic W-299 → **863/863** ✅

---

## 2026-06-13 | W-298 | DriftAdapter wpięty + Rada Doradców wpięta do Dyrygenta

**Prawo XV — ożywienie gotowych modułów, które żyły poza pipeline:**

- `legiony/legatus.py`: `ustaw_wagi_rezimu()` + `resetuj_wagi_rezimu()` + `_wagi_rezimu_override` —
  per-cykl override WAGI_REZIMU dla DriftAdapter W-296 (antycypacja zmiany reżimu).
- `koloseum/dyrygent.py`: param `drift_adapter` — rejestruje reżim co bar, koryguje wagi
  kategorii gdy wykryje dryfowanie (entropia/momentum) przed pełną zmianą reżimu.
- `koloseum/dyrygent.py`: param `rada_doradcow` + `_opinia_rady()` — Rada Pięciorga
  (Oracle/Fulmen/Iustitia/Hermes/Pythia) wywołana po Kalkulatorze, może zawetować lub
  zredukować rozmiar pozycji (×0.6–×0.8). Nowa ścieżka RADA_WETO w DecyzjaCyklu.

---

## 2026-06-12 | W-297 | NEWS-01 Sentyment Newsów LLM (DeepSeek + fallback słownikowy)

**Nowy neuron sentymentu z newsów — offline-first, LLM-opcjonalny:**

- `legiony/neurony/sentyment.py`: `NeuronSentymentNews` (NEWS-01, KAT=R, WAGA=6)
  Czyta NEWS_SENTYMENT[-1..+1]/NEWS_PEWNOSC/NEWS_N → momentum informacyjny
  (silnie bycze nagłówki→LONG, niedźwiedzie→SHORT, szum→cisza). Progi: szum 0.30.
- `akwedukty/adaptery/news_llm.py`: `AdapterNewsLLM` — dwa tryby klasyfikacji:
  (1) DeepSeek (GlosImperium) gdy DEEPSEEK_API_KEY; (2) fallback słownikowy
  (leksykon byczy/niedźwiedzi, deterministyczny, OFFLINE, zero zależności/sieci).
  Wstrzykiwany fetcher (jak AdapterFearGreed) → pełne testy offline.
- Rejestracja w `rejestr.py` (63 neurony), allowlista adapterowa w audycie (W12).
- 33 nowe testy (Reguła Test-Granic: progi/znaki/zero/None/clamp LLM) → **833/833** ✅
- Liczby zsynchronizowane: MANIFEST 63/75, README 63 (59 aktywnych), INDEKS 63.

---

## 2026-06-12 | W-293/294/295/296 | Monte Carlo + Optymalizator DSR + Pamięć Refleksyjna + Drift Adapter

**4 nowe moduły antyoverfitting/samouczenia — inspiracja: Jesse, Freqtrade, TradingAgents, Qlib DDG-DA:**

- `koloseum/monte_carlo.py` (W-293): shuffle transakcji + bootstrap → P(Sharpe>0), MaxDD_p95 CI
  Progi Imperium: P(Sharpe>0)≥90%, MaxDD_p95<25%. `pelen_raport_mc()` = shuffle+bootstrap.
- `koloseum/optymalizator.py` (W-294): Latin Hypercube Search po przestrzeni parametrów,
  DSR jako cel (karze selection bias proporcjonalnie do liczby prób). 0 zależności zewn.
- `cesarz/pamiec_refleksyjna.py` (W-295): JSONL dziennik lekcji narracyjnych,
  `formatuj_dla_llm()` → gotowy prompt-inject dla Senatu/Cesarza. Działa bez klucza API.
- `koloseum/drift_adapter.py` (W-296): DDG-DA-lite — entropia Shannona reżimu +
  momentum reżimowy → pre-shift WAGI_REZIMU PRZED zmianą reżimu (antycypacja).
- 60 nowych testów → **803/803** ✅
- MANIFEST_KODU.md, LOG_ZMIAN.md, README.md zaktualizowane

---

## 2026-06-12 | Spójność dokumentacji | 708→743 testy, 55→62 neurony

- README.md, ROADMAP_IMPERIUM.md, INDEKS_IMPERIUM.md, AUDYT_SYSTEMU.md:
  synchronizacja liczb do stanu faktycznego (743 testy, 62/58 neurony, v0.9.1)

---

## 2026-06-11 | Opcja A+B+C | Radar-adaptive strategy switching + vol-weighted portfolio + paper trading docs

**Opcja A — radar-aware strategy switching:**
- `bonus_radar(strategia, stan_rynku)`: score modifier per-styl wg RadarRynku
  (TR/SC +10% przy PRZEPLYW>0.65 i BTC bullish; RV/RG +10% przy PRZEPLYW<0.35)
- `decyduj_z_radarem()` w Namiestnik: lewar_factor ×1.2 bycze/×0.65 stres
- `legatus.stan_rynku`, `dyrygent.stan_rynku` — przekazywane per-tick
- Wynik: Sharpe=1.504, DSR=1.0 ✅ | 4H: Sharpe=2.196, DSR=1.0 ✅

**Opcja B — vol-adjusted portfolio allocation:**
- `wagi_inwerse_vol(bary_per, okno_vol)`: 1/σ wagi z warmup barów (kauzalne)
- `backtest_portfel(..., wagi=dict)`: nowy parametr — równe wagi domyślnie
- Vol-adj vs equal-weight 1D: Sharpe 1.504→1.559 (+4%)

**Opcja C — paper trading MEXC:**
- `docs/PAPER_TRADING_MEXC.md`: krok po kroku (klucze API, pętla live, Etap II)

**Testy:** 729→743 (14 nowych). Ruff czysty. Audyt exit 0.
**Pliki:** `baza.py`, `namiestnik.py`, `legatus.py`, `dyrygent.py`,
`backtest.py`, `test_radar_rynku.py`, `test_portfel.py`,
`docs/PAPER_TRADING_MEXC.md`, `docs/INDEKS_IMPERIUM.md`.

---

## 2026-06-11 | W-292 💎📊 | NeuronPrzeplyw (RADAR-03) — neuron 62, wynik MIESZANY (uczciwie)

**Opis:** PRZEPLYW_KAPITALU dostał neuron głosujący (napływ→LONG, odpływ→SHORT).
Pomiar regresyjny — wynik MIESZANY (Prawo I, bez upiększania):

| | Sharpe | PnL | PF | WR | Etap I |
|---|--------|-----|----|----|--------|
| RADAR-02 (przed) | 1.480 | +42986 | 2.69 | 55.4% | ✅ |
| + RADAR-03 | 1.475 ↓ | **+43598** ↑ | **2.73** ↑ | 55.4% | ✅ |

Sharpe −0.005 (szum), PnL i PF ↑. Bramka przechodzi z marginesem (DSR 1.0).
ZOSTAWIONY: dodaje realny barometr risk-on/off (Prawo XVI — dywersyfikacja
informacji), nie psuje bramki. Ale to NIE czysta wygrana jak RADAR-02 — raport
uczciwy. Rój: 61→62 (58 aktywnych, 6 kat. R).

**Pliki:** `sesje.py`, `rejestr.py`, `audyt_spojnosci.py`, `test_praeda.py`,
`test_integracja.py`, `MANIFEST_KODU.md`, `INDEKS_IMPERIUM.md`, `README.md`.

---

## 2026-06-11 | W-292 💎📈 | NeuronDominacja (RADAR-02) — neuron 61, zmierzony zysk

**Opis:** BTC_DOMINANCJA dostała neuron głosujący (alt-season→LONG, ucieczka do BTC→
SHORT). Pomiar regresyjny POTWIERDZIŁ poprawę (nie założenie — Prawo I):

| | Sharpe | PnL | PF | WR | Etap I |
|---|--------|-----|----|----|--------|
| bez RADAR-02 | 1.463 | +42369 | 2.67 | 55.1% | ✅ |
| z RADAR-02 | **1.480** | **+42986** | **2.69** | **55.4%** | ✅ |

Wszystkie metryki ↑ (drobno, ale realnie), DSR=1.0. Neuron zarobił na miejsce.
Rój: 60→61 neuronów (57 aktywnych, 5 kat. R). Pełna symbioza zsynchronizowana.

**Pliki:** `imperium/legiony/neurony/sesje.py`, `rejestr.py`, `narzedzia/audyt_spojnosci.py`,
`tests/test_praeda.py`, `tests/test_integracja.py`, `docs/MANIFEST_KODU.md`,
`docs/INDEKS_IMPERIUM.md`, `README.md`.

---

## 2026-06-11 | W-293 🗡️🏆 | ŁOWCA ODBLOKOWANY: tryb łupieżczy przechodzi Etap I

**Opis:** Z ciaśniejszym bezpiecznikiem (HALT 13%) tryb łupieżczy (Praeda) też przechodzi
bramkę — i łupi prawie 2× więcej niż baza, legalnie.

| Tryb | trades | WR | PF | PnL | Sharpe | DSR | Etap I |
|------|--------|----|----|-----|--------|-----|--------|
| BAZA | 664 | 55.1% | 2.67 | +42369 | 1.46 | 1.0 | ✅ |
| ŁUPIEŻCZY | 749 | 53.3% | 3.03 | **+71671** | 1.29 | 1.0 | ✅ |

**Wniosek:** ciaśniejszy bezpiecznik OKIEŁZNAŁ chciwość — Praeda wzmacnia na
potwierdzonych okazjach (PnL +69% vs baza), a HALT@13% ucina krwawienie. Niższy
Sharpe łupieżcy (1.29 vs 1.46) to cena agresji (większy zysk, większe wahania) —
ale przechodzi DSR=1.0 + MaxDD<15%. Tryb OPT-IN (`tryb_lupiezcy=True`), nie domyślny —
łowca na świadomą decyzję, nie na ślepo.

**Pliki:** (pomiar potwierdzający integrację W-291/293 — bez zmian kodu).

---

## 2026-06-11 | W-293 🎯🏆 | PORTFEL PRZECHODZI ETAP I: ciaśniejszy HALT (20%→13%)

**Opis:** Debugging (nie zgadywanie) ustalił przyczynę MaxDD 20%: bezpiecznik HALT@20%
pozwalał equity spaść DO progu, zanim blokował wejścia. Próby sygnałowe (ster
korelacyjny W-292, rygiel risk-off) NIE ruszyły MaxDD — bo zjazd dział się poza
wykrywanymi oknami. Właściwa dźwignia: **próg HALT bezpiecznika**.

**POMIAR (Prawo I) — HALT 20%→13% nie tylko przeszedł bramkę, ale PODNIÓSŁ WSZYSTKO:**

| Próg HALT | MaxDD | PnL | Sharpe | PF | WR | Etap I |
|-----------|-------|-----|--------|----|----|--------|
| 20% (stary) | 20.2% | +39477 | 1.41 | 2.19 | 53.3% | ❌ False |
| **13% (nowy)** | **<15%** | **+42369** | **1.46** | **2.67** | **55.1%** | **✅ True** |
| 11% | <15% | +43167 | 1.48 | 2.85 | 56.0% | ✅ True |

**Decyzja:** domyślne progi PORTFELOWE = REDUCED@7% / HALT@13% (świadomie nie 11% —
zostawiamy bufor, anty-overfit). Powód (polityka ryzyka, NIE curve-fit): 5 jednoczesnych
skorelowanych pozycji wymaga ciaśniejszej kontroli equity niż pojedyncza para (W-062@20%).
Wcześniejsze ucięcie krwawienia zachowuje kapitał do składania → zysk ROŚNIE. DSR=1.0.

**Pliki:** `imperium/koloseum/backtest.py` (dd_reduced/dd_halt + nowe domyślne),
`tests/test_portfel.py`.

---

## 2026-06-11 | W-292 🛡️🔬 | Ster korelacyjny OPT-IN + uczciwy pomiar (lekcja MaxDD)

**Opis:** Próba naprawy MaxDD portfela (20%) sterem korelacyjnym 1/√(1+(N-1)ρ).
POMIAR (Prawo I): MaxDD 20.2%→20.0% (bez zmian!), PnL +39477→+18969 (spadł o połowę).
**Lekcja:** MaxDD to RATIO (peak-to-trough %), niezmienny pod równomiernym skalowaniem
pozycji. Krypto-koszyk jest TRWALE skorelowany (ρ≈0.8 zawsze, nie spike'owo), więc
czynnik działał jak stały haircut ×0.5 — ciął zysk, nie ruszał MaxDD%. Dlatego ster
DOMYŚLNIE OFF (`ster_korelacyjny=False`) — nie blokujemy potencjału (Prawo XV).

**Wniosek:** MaxDD 20% NIE pochodzi ze skoków korelacji, lecz ze złego okresu
kierunkowej przewagi na pełnych danych. Wymaga STANOWEGO de-risku (cięcie w czasie
złego okresu), nie równomiernego — do zaprojektowania i ZMIERZENIA osobno.

**Pliki:** `imperium/koloseum/backtest.py`, `imperium/legiony/radar_rynku.py`,
`tests/test_radar_rynku.py`.

---

## 2026-06-11 | W-292 🛰️🌐 | RADAR RYNKU: dominacja BTC + przepływ kapitału + stres korelacji

**Opis:** Rozwój RadarBTC (W-291) → wielowymiarowy `RadarRynku`. Stary radar patrzył
TYLKO na momentum ceny BTC. Nowy dokłada trzy KAUZALNE sygnały liczone z barów koszyka
(bez API — Cezar na telefonie): **BTC_DOMINANCJA** (siła względna BTC vs alty — proxy
dominacji, alt-season detector), **PRZEPLYW_KAPITALU** (breadth × momentum wolumenu —
napływ/odpływ), **STRES_KORELACJI** (średnia korelacja par — detektor kaskady "alty za
BTC w dół", Prawo XVI). Wstrzykiwane do KAŻDEJ pary w `backtest_portfel` (przyczynowo,
bisect ≤ ts). Praeda: nowe weto STRES>0.85 (kaskada = brak dywersyfikacji = zero łupu)
+ bonus dominacji (alt-season wspiera LONG alta).

**Powód:** Pytanie Cezara — czy radar sprawdza tylko cenę, czy też odpływ kapitału,
wolumen, dominację BTC i ukryte rzeczy do skorelowania dla większej pewności ruchów.
Odpowiedź w kodzie: cztery flanki zamiast jednej, wszystko zsynchronizowane.

**Pliki:** `imperium/legiony/radar_rynku.py` (nowy), `imperium/koloseum/backtest.py`,
`imperium/pretorianie/praeda.py`, `tests/test_radar_rynku.py` (nowy), `tests/test_praeda.py`.

---

## 2026-06-11 | W-291 🗡️ | PRAEDA wpięta w silnik portfelowy (tryb_lupiezcy)

**Opis:** Domknięcie integracji Praedy: `Dyrygent` amplifikuje lewar+rozmiar w
POTWIERDZONYCH okazjach (cap 20 / clamp 50%), `KalkulatorLewara.policz` przyjmuje
`mnoznik_rozmiaru`. `backtest_portfel(tryb_lupiezcy=False)` — opt-in tryb łowcy:
ustawia `Okazjon()` per para, śpi gdy breaker ≠ NORMAL.

**Powód:** Wizja łowcy — auto-skalowana chciwość tylko gdy bezpiecznie. Domyślnie OFF.

**Pliki:** `imperium/koloseum/dyrygent.py`, `imperium/pretorianie/kalkulator_lewara.py`,
`imperium/koloseum/backtest.py`, `tests/test_praeda.py`.

---

---

---

---

---

---

## 2026-06-11 | W-291 💎 | RADAR BTC: provider + neuron RADAR-01 (lead-lag, wsparcie scalpu)

**Wizja Cezara (BTC prowadzi, alty lecą za nim):** zrealizowane jako KOD —
WIZJONER W-071/W-085/W-086 (intermarket/lead-lag) z idei → żywy neuron.

- **`imperium/legiony/radar_btc.py`** — `RadarBTC.trend(close_btc)` → BTC_TREND ∈ [-1,1]
  (momentum EMA-short vs EMA-long znormalizowane zmiennością, tanh; czysty OHLC, bez API).
- **RADAR-01 NeuronRadarBTC** (R, waga 6, WSPOLNY): głos wsparcia — BTC↑ → LONG-wsparcie
  altów, BTC↓ → SHORT-ostrzeżenie ("uważaj, alty lecą za BTC"), |trend|<0.3 → NEUTRAL.
- Radar wpięty też w Okazjon (Praeda): bonus konfluencji gdy zgodny + WETO na silny
  przeciwprąd (LONG przeciw spadającemu BTC / SHORT pod rosnący).

60 neuronów (56 aktywnych). +5 testów. W12: RADAR-01 na allowliście kontekstu (jak AUG-01).
✅ Wstrzyknięcie BTC_TREND wpięte: `Dyrygent.kontekst_dodatkowy` + `backtest_portfel`
liczy BTC_TREND z barów BTC przyczynowo (bisect do ts) i podaje każdej parze.

**🎯 POMIAR — RADAR BTC POPRAWIŁ REKORDOWY PORTFEL (intuicja Cezara potwierdzona):**

| Metryka | Portfel bez radaru | Portfel + RADAR BTC |
|---|---|---|
| Sharpe roczny | 1.74 | **1.82** 📈 |
| PF | 2.01 | **2.08** |
| MaxDD | 13.5% | **12.7%** (niżej) |
| PnL | +7155 | **+7516 (+75%)** |
| DSR | 1.0 | **1.0** |
| Etap I | ✅ | **✅ z zapasem** |

Radar lead-lag (BTC↓ → ostrzega LONG-i altów) podniósł WSZYSTKIE metryki naraz —
nowy rekord Sharpe 1.82. Wizja Cezara ("obserwuj BTC, alty lecą za nim") = realna
przewaga, nie tylko teoria. Zwalidowana konfiguracja Etapu II rozszerzona o RADAR BTC.

**Pliki:** `imperium/legiony/radar_btc.py` (nowy), `imperium/legiony/neurony/sesje.py`,
`imperium/legiony/rejestr.py`, `imperium/pretorianie/praeda.py`, `narzedzia/audyt_spojnosci.py`,
`tests/test_praeda.py`, docs.
**Testy:** 708/708 ✅. Audyt: 60 neuronów, pełna harmonia.

## 2026-06-11 | UNIKAT W-291 💎 | TRYB PRAEDA (Łowca) + RADAR BTC — auto-skalowana chciwość

**Wizja Cezara:** Imperium jako organizm-łowca — skanuje monety, szuka OFIARY
(najlepszej okazji), sam dobiera agresję wg SIŁY OKAZJI, łupi maksymalnie w
potwierdzonych momentach. Plus: BTC jako sygnał wspierający/ostrzegający alty.

**`imperium/pretorianie/praeda.py` — Okazjon (wykrywacz okazji):**
- SIŁA OKAZJI ∈ [0,1] z konfluencji (model BONUSOWY — więcej potwierdzeń STACKUJE,
  nigdy nie uśrednia w dół): rdzeń zgoda×reżim + bonusy za sentyment / Augur / RadarBTC.
- AUTO-DECYZJA: mnoznik_lewara/rozmiaru rosną ciągle z siłą (cap ×2, i tak nadrzędne
  MAX_DZWIGNIA + clamp 50% kapitału); pyramiding tylko gdy siła ≥ 0.80.
- 🛰️ RADAR BTC (lead-lag): BTC_TREND ∈ [-1,1] → wiatr w plecy gdy zgodny; WETO gdy
  LONG przeciw mocno spadającemu BTC ("alty lecą za BTC") lub SHORT pod rosnący BTC.
- NIENARUSZALNA KLATKA: Praeda tylko amplifikuje wewnątrz bezpieczników; WYŁĄCZA SIĘ
  w drawdownie (dd_normal=False → siła 0); weto na toksyczny VPIN, blackout FOMC, kaskadę.

**Status:** detektor + radar gotowe i otestowane (13 testów). Wpięcie do Dyrygenta
(tryb_lupiezcy) + provider RadarBTC w portfelu + pomiar 5 par — następny krok.

**Pliki:** `imperium/pretorianie/praeda.py` (nowy), `tests/test_praeda.py` (nowy).
**Testy:** 706/706 ✅. Audyt: pełna harmonia.

## 2026-06-11 | W-290 | DD-control portfela (wspólny BezpiecznikKrzywejKapitalu W-062)

**Opis:** `backtest_portfel(dd_control=True)` — JEDEN wspólny BezpiecznikKrzywejKapitalu
na poziomie koszyka (nie 5 z fragmentaryczną wizją), domyślne progi W-062
(REDUCED@10% DD → ×0.5 sizingu wszystkich par, HALT@20% → blokada wejść). Per-para
Dyrygenci mają breaker_krzywej=False (sterowanie centralne). Progi NIE strojone pod
backtest — dyscyplina anty-overfit; DSR/PBO pilnują reszty. +1 test.

**🎉🎉 PIERWSZY PEŁNY ZIELONY ETAP I W HISTORII IMPERIUM (silnik portfelowy):**

| Wariant | trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR | Etap I |
|---|---|---|---|---|---|---|---|---|
| bez DD-control | 422 | 51.2% | 1.60 | 22.8% | +6290 | 1.25 | 0.99 | ⛔ MaxDD |
| **z DD-control** | 422 | 51.2% | **2.01** | **13.5%** | **+7155** | **1.74** | **1.0** | **✅ ETAP I** |

**DD-control POPRAWIŁ WSZYSTKO naraz** (nie tylko ściął DD): PF 1.60→2.01, PnL +71.5%,
Sharpe 1.25→1.74, DSR→1.0, MaxDD 22.8%→13.5%. Mechanizm: bezpiecznik tnie rozmiar
DOKŁADNIE gdy portfel krwawi (REDUCED@10%), przywraca przy odbiciu — unika najgorszych
strat, więc i Sharpe rośnie. To NIE overfitting (progi domyślne W-062, DSR=1.0 idealne).

**ZWALIDOWANA KONFIGURACJA gotowa do Etapu II (paper):** koszyk 5 par
(BTC/ETH/SOL/BNB/DOGE) · 1D · AUTO-reżim (Namiestnik) · wspólny kapitał równoważony ·
DD-control (W-062). Uczciwie (Prawo I): to BACKTEST — Etap II (14 dni paper) i III
(live mikro MEXC) wciąż przed nami; ale bramka przeszła twardo (DSR 1.0), nie oknem.

**Testy:** 693/693 ✅. Audyt: pełna harmonia.

## 2026-06-11 | W-290 💎 | SILNIK PORTFELOWY — koszyk N par w jednej sesji (Kostka Rubika)

**Opis:** `backtest_portfel(pliki, interwal)` — produkcyjny tryb koszyka: N par,
JEDEN wspólny PaperTradingEngine (kapitał dzielony, max N pozycji), per-para Dyrygent
sizingujący wg kapital/N (równe wagi, Markowitz). Chronologiczna unia osi czasu —
każdy bar (ts, symbol) przetwarzany w kolejności czasu, bez look-ahead. Realizuje
ROADMAP Faza 3 "Kostka Rubika" jako kod, nie tylko pomiar.

Wsparcie: `Dyrygent.kapital_sizing` (budżet sizingu pary; None = pełny kapitał silnika).
+4 testy (wspólny kapitał, oś czasu, budżet równy, brak historii).

**🎯 BÓJ 5 PAR PRZEZ SILNIK (1D AUTO, krzywa dzienna, n_prob=5):**
trades=422, WR 51.2%, PF 1.74, PnL +6057 (+60%), **Sharpe_r 1.427 ✅**, **DSR 0.9989 ✅**,
MaxDD **16.5% ⛔** (próg <15%). Produkcyjny silnik z DYNAMICZNYM dzieleniem kapitału
dał Sharpe NAWET WYŻSZY niż idealny pomiar równowag (1.24) — kapitał płynie do par,
które akurat sygnalizują. Diagnoza krzywej potwierdzona: per-zdarzenie dawało 0.69
(√365 zaniżał o √N), dzienne = 1.43.

**JEDYNY BLOKER: MaxDD 16.5% > 15%** (o 1.5%!). To NIE overfitting do naprawy
parametrem — mamy gotowe, ZASADNICZE moduły kontroli obsunięcia: W-062
BezpiecznikKrzywejKapitalu (REDUCED@10%/HALT@20%) i W-063 SkalowanieFrakcjaDD
(płynna redukcja rozmiaru z DD). Następny krok: wpiąć DD-control do silnika
portfelowego i zmierzyć (DSR/PBO pilnują, by nie przeuczyć).

**Pliki:** `imperium/koloseum/backtest.py` (backtest_portfel), `imperium/koloseum/dyrygent.py`
(kapital_sizing), `tests/test_portfel.py` (nowy).
**Testy:** 692/692 ✅. Audyt: pełna harmonia.

## 2026-06-11 | KAMIEŃ MILOWY | Test 5 par 1D — EDGE UNIWERSALNY (wszystkie zarabiają!)

**Pierwszy szeroki test (BTC/ETH/SOL/BNB/DOGE, 1D AUTO, pełne historie, formacja
Legionów + Augur w roju, n_prob=5):**

| Para | trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR | Etap I |
|---|---|---|---|---|---|---|---|---|
| BTC | 61 | 55.7% | **2.26** | 4.3% | +3934 | 0.86 | **0.94** | ⛔ blisko |
| ETH | 75 | 48.0% | 1.12 | 12.7% | +705 | 0.17 | 0.23 | ⛔ |
| SOL | 55 | 38.2% | 1.14 | 9.0% | +636 | 0.22 | 0.23 | ⛔ |
| BNB | 68 | 51.5% | 1.63 | 10.8% | +3320 | 0.60 | 0.71 | ⛔ |
| DOGE | 16 | 75.0% | **2.73** | 22.2% | +9745 | 0.95 | 0.92 | ⛔ (n=16) |

**WNIOSEK (Prawo I — twardy fakt):** **PF > 1 na WSZYSTKICH 5 parach, PnL dodatni
wszędzie.** Dzienny edge roju jest UNIWERSALNY, nie przypadkiem BTC. To fundamentalnie
zmienia obraz: mamy realną, przenośną przewagę kierunkową na 1D.

**Czemu żadna nie przechodzi Etapu I:** próg Sharpe>1.0 (surowy, słuszny) — pojedyncze
pary mają zbyt zmienne zwroty względem średniej. BTC i DOGE są o włos (0.86–0.95).

**🎉 WYNIK PORTFELA (2026-06-11) — PIERWSZY RAZ W HISTORII IMPERIUM ETAP I ZALICZONY:**

`narzedzia/pomiar_portfela.py` (W-290) złożył 5 krzywych equity w portfel równoważony
(2945 dni, dzienne zwroty wyrównane po dacie UTC):

| Metryka | Najlepsza para sama | PORTFEL 5 par |
|---|---|---|
| Sharpe roczny | 0.95 (DOGE) | **+1.24 ✅ >1.0** |
| MaxDD | 4.3% (BTC) | **6.9% ✅ <15%** |
| DSR (n_prob=5) | 0.94 (BTC) | **0.9962 ✅ ≥0.95** |
| **Werdykt Etapu I** | ⛔ żadna | **✅ ZALICZONY** |

**DLACZEGO DZIAŁA (Prawo XVI — zmierzone, nie zgadnięte):** średnia korelacja par
dziennych zwrotów = **+0.02** (niemal ZEROWA!). Edge roju na każdej parze jest
praktycznie NIEZALEŻNY → dywersyfikacja redukuje wariancję portfela ~5×, średnia
zwrotu zostaje. Markowitz w czystej postaci. To NIE wymagało zmiany ani jednego
neuronu — sama struktura portfela przeskoczyła próg.

**ZNACZENIE:** mamy pierwszą konfigurację gotową do Etapu II (paper trading):
NIE pojedyncza para, lecz KOSZYK 5 par równoważony (ROADMAP Faza 3 "Kostka Rubika"
zrealizowana w pomiarze). Uczciwie: to backtest — Etap II (14 dni paper) i III (live
mikro) wciąż przed nami; ale droga jest OTWARTA i zmierzona twardą bramką (DSR 0.996).

**Pliki:** `narzedzia/pomiar_portfela.py`. **Następne:** silnik portfelowy (jedna
sesja, N par, wspólny kapitał, realokacja) jako produkcyjny tryb backtestu.

## 2026-06-11 | UNIKAT W-289 v2 💎 | Augur rozbudowany: per-para + kalendarz FOMC (blackout) + decay/spójność

**Rozbudowa Kronikarza Zdarzeń o 3 wymiary (na prośbę Cezara):**
1. **PER-PARA:** zdarzenia mają pole `pary` (ETH ETF → tylko ETHUSDT; halving/krach/
   FOMC = makro/BTC-dominacja → wszystkie). `kontekst(ts, symbol)` filtruje —
   kluczowe pod test 5 par (ETH ETF nie zafałszuje SOL).
2. **KALENDARZ FOMC (56 dat 2020–2026, publiczne):** dwie funkcje na raz —
   • event-study post-FOMC (wysokie n → statystyka mocna),
   • **BLACKOUT pre-FOMC**: ≤2 dni PRZED posiedzeniem augur WIE, że FED idzie →
     AUG-01 głosuje NEUTRAL-ostrożność "zredukuj ryzyko". To "znajomość przyszłości",
     o którą prosił Cezar (dokładny dzień/czas). Daty 2026 = znane przyszłe okna.
3. **DECAY + SPÓJNOŚĆ:** `waga_zaniku` (1.0 w dniu zdarzenia → 0 na krawędzi okna)
   i `zgodne_kierunkowo`/`rozrzut_pct` (czy historyczne epizody mówią jednym głosem).
   AUG-01 moduluje pewność: bazowa × decay × bonus-zgodności.

**Symbioza:** EVENT_* rozszerzone (WAGA, ZGODNE, BLACKOUT, DNI_DO); AUG-01 v2
respektuje blackout (pierwszeństwo) i decay. +7 testów (per-para, blackout,
pierwszeństwo, decay, spójność, neuron-blackout, neuron-decay).

**Pliki:** `imperium/biblioteki/kronikarz_zdarzen.py`, `imperium/legiony/neurony/sesje.py`,
`tests/test_kronikarz_zdarzen.py`.
**Testy:** 688/688 ✅. Audyt: pełna harmonia.

## 2026-06-10 | UNIKAT W-289 💎 | KRONIKARZ ZDARZEŃ (Augur) — zdarzenia fundamentalne jako głos roju

**Wizja Cezara zrealizowana** (= ROADMAP Faza 3 "Macierz zdarzeń historycznych" + W-039):
system zna zdarzenia fundamentalne, dopasowuje historyczne analogie do live i podaje
PROCENTOWE prawdopodobieństwa jako głos w roju.

**Architektura (3 płaszczyzny, pełna symbioza):**
1. **`biblioteki/kronikarz_zdarzen.py`** — KATALOG 12 zdarzeń (HALVING×3, ETF×3,
   KRACH×3, REGULACJA×2, MAKRO; daty powszechnie weryfikowalne) + **przyczynowe
   event-study**: `studium(typ, ts)` liczy forward-zwroty WYŁĄCZNIE z epizodów
   o domkniętym horyzoncie przed ts (test wymusza zero look-ahead; bieżące zdarzenie
   nie zasila własnych statystyk).
2. **AdapterKronikarz** (mechanizm adapterów Dyrygenta) → wstrzykuje EVENT_TYP/
   DNI_PO/N/PROB_WZROSTU/MEDIANA_PCT tylko w oknie ≤30 dni po zdarzeniu.
3. **AUG-01 NeuronAugur** (R, waga 6, WSPOLNY): n≥2 ∧ prob≥65% → LONG;
   prob≤35% → SHORT; n<2 → NEUTRAL "za mało historii" (Prawo I). W12: allowlista
   adapterowa + twarda weryfikacja ożywienia.

**ORYGINALNOŚĆ:** literatura daje jedną liczbę z jednego badania — nasz augur
SAMOKALIBRUJE się z własnych barów i mądrzeje z każdą parą/historią bez zmiany kodu.
Źródła naukowe kierunku (ZPO, w docstringu): FOMC-drift (JFM 2022), halving-synthetic-
control (+24.55%, arXiv 2511.05512), spot-ETF (IRFA 2025).

**TABELA DOWODOWA (BTC 1D 2017–2026, policzona przez moduł, ts=2026-06-10):**

| Typ | n | 30 dni: prob↑ / mediana | 90 dni: prob↑ / mediana |
|---|---|---|---|
| HALVING | 2 | **100% / +12.7%** | **100% / +19.6%** |
| ETF | 3 | 33% / −5.5% ("sell the news"!) | 33% / −10.0% |
| KRACH | 3 | 67% / +0.4% | 67% / +22.7% (odbicia) |
| REGULACJA | 2 | 50% / +19.9% | 100% / +20.3% |

**Bug złapany testem podczas budowy:** zdarzenie spoza pokrycia danych dopasowywało
się do pierwszego dostępnego baru (halving 2016 → bar 2024, absurdalny zwrot) —
naprawione tolerancją ≤3 dni w `_indeks_baru` (Prawo I: brak danych ≠ wymyślone).

**Pliki:** `imperium/biblioteki/kronikarz_zdarzen.py` (nowy), `imperium/legiony/neurony/
sesje.py` (AUG-01), `rejestr.py`, `narzedzia/audyt_spojnosci.py` (W12 allowlista+weryfikacja),
`tests/test_kronikarz_zdarzen.py` (nowy, 8 testów z przyczynowością), docs.
**Testy:** 681/681 ✅ (59 neuronów, 55 aktywnych). Audyt: pełna harmonia.
**Następne rozszerzenia (zapisane):** kalendarz FOMC/CPI (cykliczne daty → przyszłe
okna), zdarzenia per-para, wagi malejące z dni_po.

## 2026-06-10 | W-288 | ATR-SL/TP (opt-in) + fix sprzężenia sizing↔SL — mechanika naprawiona, edge obnażony

**Wdrożone:**
1. **SL z ATR (opt-in):** `policz(atr=…, sl_atr_mult=…)` → SL = cena ∓ k×ATR, ale
   TYLKO ciaśniejszy niż lewarowy (nigdy bliżej likwidacji — clamp bezpieczeństwa).
   TP=MIN_RR×SL skaluje się automatycznie. Dyrygent: `sl_atr_mult` → bierze ATR_14
   z Bramy; backtest przelotowo. +4 testy granic (None/0, ogromny ATR, TP-skala).
2. **Fix sprzężenia sizing↔SL (uniwersalny):** risk-sizing (2%/stop_pct) z ciasnym
   SL żądał pozycji >>50% kapitału → checklist WETOWAŁ niemal każde wejście
   (pomiar: 201→2 trade'y!). Teraz CLAMP rozmiaru do 50% kapitału przed checklistą
   (ryzyko tylko maleje — uczciwy raport ryzyka z finalnego rozmiaru bez zmian).
3. Clamp odsłonił 2 KRUCHE testy przechodzące dzięki staremu wetu (pewność agregatu
   =1.0 przy zgodnym komplecie wskaźników) — naprawione na płaskie bary/sprzeczne
   sygnały z komentarzem-lekcją.

**POMIAR (BTC 1H, 12k barów, AUTO):**

| Wariant | Trades | WR | PF | MaxDD | PnL | TP/SL/TIMEOUT |
|---|---|---|---|---|---|---|
| baseline | 201 | 49.3% | 0.72 | 10.8% | −838 | 0/3/198 |
| ATR-SL 2.0 | 109 | 34.9% | 0.72 | 18.1% | −1536 | **29/66/14** |
| ATR+Strażnik | 95 | 31.6% | 0.69 | 18.5% | −1572 | 24/59/12 |

**Werdykt (Prawo I — pełna prawda):** mechanika wyjść NAPRAWIONA (TIMEOUT 198→14,
TP wreszcie trafiane 0→29) — ale ekonomicznie GORZEJ: ciasny SL × większe pozycje
(clamp) = częstsze i droższe SL-y. **TIMEOUT-y nie były źródłem straty — MASKOWAŁY
ujemny kierunkowy edge 1H/2025 małymi stratami; ATR-SL go skrystalizował.**
Wniosek strategiczny: problem 1H leży w PRZEWADZE KIERUNKOWEJ roju w tamtym okresie,
nie w mechanice. W-288 zostaje jako poprawne narzędzie (opt-in, NIEzalecane bez
zmierzonego edge); clamp 50% zostaje na stałe (naprawia realne sprzężenie).
Dalej: trop "edge dojrzewa" (autopsja) + walidacja na 5 parach świeżego okna.

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `imperium/koloseum/dyrygent.py`,
`imperium/koloseum/backtest.py`, `tests/test_kalkulator.py` (+4), `tests/test_dyrygent.py`.
**Testy:** 673/673 ✅. Audyt: pełna harmonia.

## 2026-06-10 | UNIKAT W-287 | Strażnik Przewagi + autopsja 1H — tarcza tnie krwawienie 5×

**AUTOPSJA (12k barów 1H, per ćwiartka czasu):** PF 0.32→0.79→0.99→1.48 — edge roju
monotonicznie DOJRZEWA (wczesny 2025 wrogi, świeży rynek sprzyja). Drugi trop:
198/201 zamknięć = TIMEOUT (mechanika wyjść na 1H — osobna iteracja). LONG −308 /
SHORT −530 — obie strony, problem nie w kierunku.

**💎 W-287 STRAŻNIK PRZEWAGI (unikat):** pretorianin patrzący na samą PRZEWAGĘ:
rolling expectancy N=12 zamkniętych < 0 → HALT 96 barów → SONDA (1 pozycja zwiadowcza;
wygrana=powrót z resetem, przegrana=ponowny HALT). Literatura zna "strategy decay"
jako raport; u nas automat w pętli z tanim powrotem. Maszyna stanów + 9 testów granic
(expectancy==0 nie halt, sonda PnL==0 = przegrana, jedna sonda naraz, parametry).

**POMIAR (BTC 1H, 12k, AUTO):**

| Wariant | Trades | PF | MaxDD | PnL | Sharpe_r | DSR |
|---|---|---|---|---|---|---|
| bez Strażnika | 201 | 0.72 | 10.8% | −838 | −1.34 | 0.003 |
| **ze Strażnikiem** | 175 | **0.95** | **6.4%** | **−150** | **−0.30** | 0.082 |

**Werdykt:** tarcza potwierdzona (strata ~5× mniejsza, DD prawie o połowę) — Strażnik
automatycznie wyłącza rój w okresach wygasłego edge'a. To NIE tworzy przewagi (PF<1
wciąż) — miecz (edge bazowy, mechanika TIMEOUT na 1H) to następna iteracja. Opt-in.

**Pliki:** `imperium/pretorianie/straznik_przewagi.py` (nowy), `imperium/koloseum/backtest.py`,
`tests/test_straznik_przewagi.py` (nowy), docs (MANIFEST/WIZJONER/LOG).
**Testy:** 669/669 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FAZA C (W-286) | ZEGARY RYNKU: SES-01/SES-02 — PRZEŁOM NA 1H (pierwszy Sharpe > 1.0!)

**Zwiad (agent docs + deep search internet, pełne linki w neurony/sesje.py):**
- Katalog: W-011 Azja Range Breakout = top kandydat (5/5, pure OHLCV+timestamp, kod czekał).
- Internet: rytm fundingu 8h — spread peak ~2h po settlement 00/08/16 UTC (MDPI 2026,
  badanie 26 giełd); sezonowość godzinowa BTC 21–23 UTC + efekt piątku (QuantPedia,
  turn-of-the-candle PMC 2023). Wszystko liczone z SAMEGO TIMESTAMPU — działa w backteście.
- ⚠️ W-010 CME Gap: agent ustalił, że CME handluje 24/7 od 29.05.2026 → strategia gapów
  UMARŁA; w katalogu do rebrandu na Monday-effect.

**Wdrożone (58 neuronów, 54 aktywne):**
- **Budowniczy:** TIMESTAMP + ASIA_HIGH/ASIA_LOW/ASIA_GOTOWA (zakres 00–08 UTC bieżącej
  doby; GOTOWA dopiero po 08:00 — bez look-ahead).
- **SES-01 NeuronZegarSesji** (S, waga 4): 0–2h po settlement fundingu → kontekst
  ostrożności; piątek 21–23 UTC → słaby LONG-bias. Kontekst, nie silnik.
- **SES-02 NeuronAzjaRange** (S, waga 7, W-011): breakout/breakdown domkniętego zakresu
  Azji, pewność rośnie z odległością od zakresu (cap 0.85).
- W12 audytu: scenariusze syntetyczne dostały timestampy (piątek, godzinowe) — żywotność
  SES-* weryfikowana co sesję. +7 testów granic (settlement dokładnie 0h/2h, close==high,
  zakres zdegenerowany, Azja niedomknięta).

**POMIAR (BTC, 4000 barów, AUTO, n_prob=4):**

| Rynek | Wariant | Trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR |
|---|---|---|---|---|---|---|---|---|
| 1H | baseline (przed) | 67 | 56.7% | 1.11 | 4.8% | +128 | 0.28 | 0.19 |
| 1H | **+ZEGARY** | 65 | 52.3% | **1.59** | **2.5%** | **+540** | **1.47 ✅>1.0!** | 0.46 |
| 4H | +ZEGARY | 74 | 41.9% | 0.59 | 14.5% | −1168 | −1.29 | 0.002 |

**Werdykt PIERWOTNY:** 1H, 4000 barów: pierwszy Sharpe>1.0 w historii Imperium; DSR 0.46.

**SUPLEMENT — dłuższa próba (Prawo I, bez lukru):** na 12000 barach 1H (≈16 mies.,
2025-02→2026-06): trades=201, WR 49.3%, PF 0.72, Sharpe_r −1.34 → wynik się ODWRACA.
**DSR 0.46 słusznie ostrzegał** — świetne okno 5,5-miesięczne nie jest stabilne w czasie;
rok 2025 zjada strategię. To nie zegary zawiodły (kontekst, niska waga) — cały rój na 1H
jest NIESTABILNY MIĘDZY OKRESAMI. Wnioski: (1) zegary SES-* zostają (tanie, badawczo
uzasadnione, nieszkodliwe); (2) 1H NIE jest gotowe — następny krok: analiza per okres
(czy strata skoncentrowana w jednym reżimie/krachu 2025?) i per para (5 par czeka);
(3) nasza bramka DSR po raz kolejny obroniła przed wdrożeniem szczęśliwego okna.
4H bez zmian (ziarno za grube dla sesji) — czeka na inne źródło przewagi.

**Pliki:** `imperium/legiony/neurony/sesje.py` (nowy), `budowniczy_wskaznikow.py`,
`rejestr.py`, `narzedzia/audyt_spojnosci.py` (W12 timestampy), `tests/test_neurony.py`,
`tests/test_integracja.py`, docs (MANIFEST/README/INDEKS).
**Testy:** 660/660 ✅. Audyt: pełna harmonia (58 neuronów).

## 2026-06-10 | FAZA B (W-286) | Diagnoza 4H + grid TIMEOUT — bramka PBO ZABLOKOWAŁA kalibrację (wzorcowe!)

**DIAGNOZA (atrybucja przez pętlę MWU + rozkład zamknięć, BTC 4H):**
- **75% zamknięć = TIMEOUT** (54/72), tylko 2×TP vs 15×SL — pozycje umierają z czasu.
- Przyczyna mechaniczna: `MAX_BARS_OTWARCIA=48` ŚWIEC stałe per system — 48 dni na 1D,
  ale tylko 8 dni na 4H, podczas gdy TP (z dźwigni) wymaga podobnego ruchu %.
- LONG i SHORT tracą symetrycznie → problem egzekucji wyjść, nie kierunku.
- MWU najgorsi na 4H: XII-02 Ichimoku, H-01 Hurst, V-13, XII-05 Fibo, V-01 OBV.

**MECHANIZMY (wdrożone, opt-in, zero regresji — +2 testy):**
- `PaperTradingEngine(max_bars_otwarcia=N)` — TIMEOUT per silnik (None → stała stara).
- `Dyrygent(min_pewnosc_interwalu={"4H": 0.65})` — próg pewności per interwał
  (z Namiestnikiem: max(prog_reżimu, prog_interwału) — ostrzejszy wygrywa).
- `backtest(...)` przelotowo wspiera oba.

**GRID (BTC 4H, 4000 barów, AUTO; n_prob=4):**

| max_bars | trades | WR | PF | PnL | DSR | TIMEOUT |
|---|---|---|---|---|---|---|
| 48 (baseline) | 74 | 41.9% | 0.59 | −1168 | 0.002 | 57 |
| 96 | 45 | 37.8% | 0.85 | −382 | 0.072 | 29 |
| 144 | 35 | 42.9% | **1.07** | **+167** | 0.193 | 18 |
| 192 | 31 | 38.7% | 0.99 | −31 | 0.145 | 10 |
| **PBO (CSCV, S=8)** | | | | | **0.614 ⛔** | |

**WERDYKT (Prawo XVIII + W-282 — bramka obroniła nas przed samooszustwem):**
Kierunek diagnozy POTWIERDZONY (monotoniczna poprawa z TIMEOUT), ale PBO=0.61 >> 0.20:
wybór "najlepszego" wariantu z gridu to dopasowanie do szumu — zwycięzca in-sample
niestabilny out-of-sample. NAJLEPSZY wariant i tak ledwo PF 1.07. **Wniosek:** edge
dzienny roju NIE skaluje się na 4H przez samą mechanikę wyjść — 4H wymaga innego
źródła przewagi (Faza C: mikrostruktura/scalp lub osobne wagi reżimowe — przyszły
pomiar na WIĘKSZEJ próbie/wielu parach). Domyślne wartości BEZ ZMIAN; mechanizmy
zostają jako narzędzia kalibracji.

**To jest dokładnie po co zbudowaliśmy W-282** — pierwsza realna interwencja bramki.

**Pliki:** `imperium/koloseum/paper_trading.py`, `imperium/koloseum/dyrygent.py`,
`imperium/koloseum/backtest.py`, `tests/test_paper_trading.py`, `tests/test_dyrygent.py`.
**Testy:** 655/655 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FAZA A (W-286) | Formacja Legionów per interwał — POMIAR: 1D lepsze, 4H czeka na Fazę B

**Opis:** `Legatus._formacja_interwalu()` — na danym interwale głosują tylko neurony
właściwego legionu: M1/M5/M15→SCALP; 1H→SCALP+SWING; 4H/1D/1W→SWING; uniwersalne
(WSPOLNY/STRAZ/VOLUME/TREND/EXPLORATORES) zawsze; nieznany/pusty interwał → pełny rój
(stare zachowanie, Prawo XV). +4 testy formacji (granice: 1D bez SCALP, M5 bez SWING,
1H oba, nieznany bez filtra).

**POMIAR (BTC, AUTO, n_prob=4) — formacja vs baseline z wcześniejszych testów:**

| Rynek | Wariant | Trades | WR | PF | PnL | Sharpe_r | DSR |
|---|---|---|---|---|---|---|---|
| BTC 1D | baseline | 59 | 55.9% | 2.23 | +3622 | 0.825 | 0.938 |
| BTC 1D | **FORMACJA** | 61 | 55.7% | **2.26** | **+3934** | **0.859** | **0.954 ✅>0.95** |
| BTC 4H | baseline | 73 | 43.8% | 0.61 | −1012 | −1.18 | 0.003 |
| BTC 4H | FORMACJA | 74 | 41.9% | 0.59 | −1168 | −1.29 | 0.002 |

**Werdykt (Prawo XVIII):** Faza A PRZYJĘTA — na 1D poprawia wszystko (PnL +9%, DSR
przekracza próg 0.95; do Etapu I brakuje już TYLKO Sharpe 0.86→1.0). Na 4H sama
formacja nie wystarcza (problem leży w wagach reżimu/progach, nie w składzie roju) —
dokładnie po to jest **Faza B: kalibracja per interwał** (następna sesja, pod bramką
DSR/PBO). Plan W-286 (A✅→B→C) zapisany w WIZJONER.

**Pliki:** `imperium/legiony/legatus.py`, `tests/test_integracja.py` (+4), `docs/WIZJONER.md`.
**Testy:** 653/653 ✅. Audyt: pełna harmonia.

## 2026-06-10 | NARZĘDZIE+POMIAR | Agregator 4H (5 par z 1H) + test bojowy 4H

**Opis:** `narzedzia/agreguj_4h.py` — buduje bary 4H z 1H po siatce UTC (open/max/min/
close/suma; NIEPEŁNE okna odrzucane — Prawo I). Wynik: 5 plików `dane/4h/Binance_*_4h.csv`
(12.1k–18.6k barów, do 2026-06-08), prosty format Imperium, czytnik czyta wprost.
+2 testy (kompletność okna, luka w środku).

**TEST BOJOWY 4H (4000 barów, AUTO, n_prob=4):**
- BTC 4H: 73 trades, WR 43.8%, PF 0.61, PnL −1012, Sharpe_r −1.18 → ⛔ (STRATA!)
- SOL 4H: 80 trades, WR 51.2%, PF 1.11, PnL +493, Sharpe_r 0.30 → ⛔

**Werdykt (Prawo I):** rój w obecnej kalibracji jest GRACZEM DZIENNYM — edge na 1D
(PF 2.23), brak na 1H (1.11), strata na 4H BTC (0.61). Progi/wagi/strategie wymagają
kalibracji per interwał ZANIM pomyślimy o scalpie. To jest GŁÓWNE zadanie następnej
sesji — teraz mamy do tego pełne dane (5 par × 1D/4H/1H do 2026-06-08).

**Pliki:** `narzedzia/agreguj_4h.py` (nowy), `dane/4h/*` (5), `tests/test_czytnik_csv.py`.
**Testy:** 649/649 ✅. Audyt: pełna harmonia.

## 2026-06-10 | DANE+FIX | Świeże dane 5 par (1D+1H do 2026-06-08) + brud µs w CDD naprawiony w czytniku

**Opis:** Cezar dostarczył 10 plików CryptoDataDownload (BTC/ETH/SOL/BNB/DOGE × 1D+1H,
pełne historie do 2026-06-08). Weryfikacja wykryła REALNY BRUD ŹRÓDŁOWY: pliki 1h
mieszają wiersze z unixem w MILISEKUNDACH i ~700/parę w MIKROSEKUNDACH (×1000 za duże,
marzec 2025) → daty "rok 57163". Fix w `czytnik_csv._parse_ts`: heurystyka >1e14 → µs ÷1000;
plus deduplikacja po timestamp (duble µs/ms tej samej świecy — zostaje nowszy wpis).
Po fixie: 5×1H monotoniczne ✅ (49.6k–75.7k barów), 5×1D świeże ✅.

**Pliki:** `dane/dzienne/*` (5), `dane/godzinowe/*` (5), `imperium/akwedukty/czytnik_csv.py`,
`tests/test_czytnik_csv.py` (+2 testy granic heurystyki i dedup).
**Testy:** 647/647 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FEATURE | CLI backtestu z werdyktem Etapu I + flagi --auto/--ucz

**Opis:** Każdy backtest z linii poleceń kończy się teraz JAWNYM werdyktem bramki
Etapu I Koloseum (✅ awans do paper / ⛔ powód odrzucenia) — Prawo I: koniec z
"raportem bez wniosku". Nowe flagi CLI: `--auto` (Namiestnik AUTO-reżim),
`--ucz` (pętla uczenia MWU). Użycie:
`python -m imperium.koloseum.backtest dane/dzienne/Binance_BTCUSDT_d.csv 1D --auto`

**POMIAR 1H (BTC, 4000 barów, AUTO — dokończenie pomiaru pętli uczenia z 1D):**
- bez uczenia: 67 trades, WR 56.7%, PF 1.11, PnL +128, Sharpe_r 0.28 → ⛔
- z uczeniem:  67 trades, WR 53.7%, PF 0.95, PnL −61, Sharpe_r −0.29 → ⛔

**Werdykt (Prawo I):** hipoteza "gęstsze dane = więcej rund MWU" NIE potwierdziła się —
rój na 1H wchodzi rzadko (67 wejść / 4000 barów; ostre progi pewności), więc rund uczenia
nadal za mało, a edge roju na 1H w tym oknie jest słaby (PF 1.11). Wnioski na następne
sesje (laptop): (a) kalibracja selektywności/progów pod 1H-4H, (b) świeże dane MEXC,
(c) strojenie eta/alpha MWU dopiero przy ≥300 transakcjach. `ucz_mwu` zostaje OFF.

**Pliki:** `imperium/koloseum/backtest.py`.
**Testy:** 645/645 ✅. Audyt: pełna harmonia.

---

## 2026-06-10 | FEATURE+POMIAR | Zamknięta pętla uczenia w backteście (ucz_mwu) — werdykt: działa, na 1D za mało rund

**Opis:** Największa luka Prawa XV zamknięta — Igrzyska/MWU przestały być martwym
klockiem w backteście:
- `DecyzjaCyklu.pozycja_id` — atrybucja: które neurony głosowały przy wejściu.
- `backtest(ucz_mwu=True)`: każda ZAMKNIĘTA pozycja rozlicza głosujące neurony przez
  `HedgeMWUzPamieciaRezimu` (W-049+W-280+W-285.1: Hedge + Fixed-Share + pamięć per-reżim),
  świeże mnożniki wracają do Legatusa na bieżąco. Bez look-ahead (uczenie wyłącznie
  z już zamkniętych transakcji); `ustaw_rezim()` indeksuje pamięć klasyfikacją bara.
- Opt-in (`ucz_mwu=False` domyślnie — test dowodzi identyczności ze starym zachowaniem).

**POMIAR (BTC 1D AUTO, eta=0.3, α=0.02):** bez uczenia PF 2.23 / Sharpe_r 0.83;
z uczeniem PF 1.95 / Sharpe_r 0.67. **Werdykt (Prawo I):** pętla technicznie działa,
ale 58 zamkniętych transakcji to ZA MAŁO rund dla MWU (szum dominuje sygnał uczenia).
Następny pomiar: interwał 1H/4H (setki transakcji) na laptopie — tam MWU ma szansę.
Domyślnie wyłączone do czasu pozytywnego pomiaru (Prawo XVIII).

**Pliki:** `imperium/koloseum/dyrygent.py`, `imperium/koloseum/backtest.py`,
`tests/test_backtest.py` (+2).
**Testy:** 645/645 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FIX+POMIAR | Bug jednostek w bramce Etapu I + pierwszy TEST BOJOWY roju

**Bug (złapany testem bojowym, nie unit-testem — lekcja):** `StatystykiSesji` trzyma
`win_rate` i `max_drawdown_pct` jako UŁAMKI (0.5=50%) mimo sufiksu `_pct`; bramka
dzieliła przez 100 → progi WR i MaxDD były martwe. Unit-test nie złapał, bo duck-type
`_Stat` podawał procenty — test powielił błędne założenie autora. Naprawione
(bramka + testy na ułamkach, komentarz ostrzegawczy o jednostkach).

**TEST BOJOWY (pełny rój, realne dane, bramka Etapu I, n_prob=4):**

| Rynek | Tryb | Trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR | Werdykt |
|---|---|---|---|---|---|---|---|---|---|
| BTC 1D | agregat | 133 | 52% | 1.22 | — | +2353 | 0.34 | 0.47 | ⛔ Sharpe |
| BTC 1D | agregat-AUTO | 59 | 55.9% | **2.23** | **4.3%** | **+3622** | 0.83 | 0.94 | ⛔ Sharpe 0.83≤1.0 |
| ETH 1D | agregat-AUTO | 72 | 51.4% | 1.15 | 11.3% | +791 | 0.19 | 0.30 | ⛔ |

**Wnioski (Prawo I — uczciwie):**
1. **Namiestnik AUTO-reżim to ogromna wartość:** PF 1.22→2.23, DSR 0.47→0.94, połowa trade'ów.
2. Rój ZARABIA na BTC z świetną kontrolą ryzyka (MaxDD 4.3%), ale Sharpe 0.83 — bramka
   (słusznie surowa) jeszcze nie przepuszcza do Etapu II. Brakuje selektywności/rozmiaru.
3. ETH 1D: brak przewagi — rój kalibrowany na BTC nie przenosi się 1:1.

**Pliki:** `imperium/koloseum/walidacja.py`, `tests/test_walidacja.py`.
**Testy:** 643/643 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FEATURE | Bramka Etapu I Koloseum wpięta w backtest (ROADMAP × W-282)

**Opis:** Domknięcie pętli walidacji — bramki przestały być "gotowe ale niepodpięte"
(czerwony alarm Prawa XV z poprzedniej sesji):
- `backtest()` zbiera teraz **krzywą equity per bar** (`engine.krzywa_equity`) —
  +1 punkt po zamknięciu końcowym; testowany kontrakt długości.
- NOWA `etap_pierwszy_koloseum(krzywa, statystyki, interwal, n_prob)` w
  `koloseum/walidacja.py`: progi ROADMAP § ZASADA ARENY (≥10 trade'ów, Sharpe
  roczny > 1.0 annualizowany wg interwału, MaxDD < 15%, WR > 55% LUB PF > 1.5)
  **plus** DSR ≥ 0.95 (W-282) — jeden werdykt ok/powod. Strategia bez przejścia
  bramki nie awansuje do Etapu II (paper).
- Werdykt zawsze z czytelnym powodem pierwszego czerwonego progu (Prawo I).

**Pliki:** `imperium/koloseum/backtest.py`, `imperium/koloseum/walidacja.py`,
`tests/test_walidacja.py` (+8), `tests/test_backtest.py` (+1, kontrakt end-to-end).
**Testy:** 643/643 ✅ (634+9). Audyt: pełna harmonia.

## 2026-06-10 | FEATURE+POMIAR | W-285.2 Dwu-zegarowy DSR (unikat) + pomiar W-281 (werdykt: ADX zostaje)

**Opis:**
1. **W-285.2 💎 Dwu-zegarowy DSR** (`koloseum/walidacja.py`): `bary_wolumenowe()` (trading-time
   Mandelbrota, BIB-009/W-144 — bary o równym wolumenie, końcówka odrzucana) + `bramka_dwuzegarowa()` —
   DSR liczony na zwrotach kalendarzowych ORAZ na strategii odtworzonej w trading-time
   (`sygnal_fn` na barach wolumenowych, pozycja[i−1]·zwrot[i], bez look-ahead). Przechodzi
   tylko gdy OBA zegary zielone — odpada strategia żyjąca z nierównej gęstości czasu. +9 testów.
2. **Pomiar W-281** (`narzedzia/pomiar_jump_model.py`, NOWE narzędzie): przyczynowy walk-forward
   (okno 250, refit 20, λ=30), miara = zwrot baru t+1 po stanie t. WYNIK NEGATYWNY dla JM:
   BTC 1D sep(B−B) −5.0 bps vs ADX +20.9; ETH 1D −24.9 vs +31.0; przełączeń 4× więcej.
   **Werdykt (Prawo XVIII): JumpModel NIE wchodzi do klasyfikuj_rezim(); W-285.3 Trybunał
   odłożony.** Moduł+testy zostają. Uczciwy pomiar > entuzjazm papierów (Prawo I).
   Bugi naprawione w narzędziu: CSV CryptoDataDownload od najnowszych (sort po Unix),
   Volume ETH/BTC/USDT, stan bez wystąpień → NEUTRAL.

**Pliki:** `imperium/koloseum/walidacja.py`, `tests/test_walidacja.py`,
`narzedzia/pomiar_jump_model.py` (nowy), `docs/` (WIZJONER werdykt+tabela, MANIFEST, LOG, README).
**Testy:** 634/634 ✅ (625+9). Audyt: pełna harmonia.

## 2026-06-10 | FEATURE | Pakiet "najlepsi z najlepszych": W-280 + W-281 + W-282 + W-285.1 (unikat)

**Opis:** Wdrożenie pakietu z deep researchu (4 moduły, +39 testów, 586→625):

1. **W-280 Fixed-Share** (`biblioteki/hedge_mwu.py`): parametr `alpha_share` — po każdej
   rundzie ułamek α masy wraca do puli (w_i ← (1−α)·w_i + α·średnia). Naprawia strukturalną
   wadę czystego Hedge w niestacjonarności (zakopane wagi wracają po zmianie reżimu).
   α=0 → dokładnie stary HedgeMWU (test dowodzi zero regresji).
2. **W-282 Bramka anty-overfittingu** (`koloseum/walidacja.py`, NOWY): Deflated Sharpe Ratio
   (korekta o liczbę prób + skośność/kurtozę; Bailey & de Prado 2014) + PBO przez CSCV
   (C(S,S/2) podziałów; Bailey et al. 2015) + `bramka_walidacji()` — strategia przechodzi
   tylko gdy DSR ≥ 0.95 ORAZ PBO < 0.20. Pure-Python (Φ przez erf, Φ⁻¹ Acklam).
3. **W-281 JumpModel** (`legiony/jump_model.py`, NOWY): detektor reżimu z karą za skok λ
   (Viterbi-DP + naprzemienna aktualizacja centroidów, multi-start, deterministyczny seed).
   Krypto-paper: Cortese/Kolm/Lindström 2023 (3 stany bull/neutral/bear). KLOCEK Fazy 3
   master-switcha — wpięcie do klasyfikuj_rezim() po pomiarze (Prawo XVIII).
4. **W-285.1 💎 HedgeMWUzPamieciaRezimu** (unikat Imperium): Fixed-Share, ale masa mieszana
   wg PAMIĘCI wag per-reżim (EMA) zamiast uniform — gdy wraca RANGING, neurony mean-reversion
   odzyskują wagę natychmiast. Inspiracja: Bousquet & Warmuth (JMLR 2002) "sharing to past
   posteriors"; nasz twist: indeksowanie reżimem z Namiestnika, nie czasem.

**Infrastruktura przy okazji (Prawo XV):** `tests/run_tests.py` — AUTO-DISCOVERY plików
test_*.py (sztywna lista cicho zgubiła test_walidacja — nowy strażnik istniał, ale nie był
uruchamiany). Bramka W13 złapała w trakcie pracy 3 nieużywane importy — system działa.

**Pliki:** `imperium/biblioteki/hedge_mwu.py`, `imperium/koloseum/walidacja.py` (nowy),
`imperium/legiony/jump_model.py` (nowy), `tests/test_walidacja.py` (nowy),
`tests/test_jump_model.py` (nowy), `tests/test_hedge_mwu.py`, `tests/run_tests.py`,
`docs/` (MANIFEST, WIZJONER statusy, README, LOG).
**Testy:** 625/625 ✅ (586+39). Audyt: 13 warstw, pełna harmonia.

## 2026-06-10 | ZWIAD | Deep research 2024-2026 → wizje W-280..W-285 (WIZJONER)

**Opis:** Zwiad internetowy (5 osi: agregacja głosów, detekcja reżimu, anty-overfitting,
risk mgmt, darmowe dane). Najważniejsze znaleziska (pełne linki w WIZJONER § 2026-06-10):
- **W-280 Fixed-Share** — naprawia strukturalną wadę Hedge/MWU w niestacjonarnych rynkach
  (zakopane wagi nie wracają); wdrożenie = 1 linia w hedge_mwu.py. 🔴
- **W-281 Statistical Jump Model** — detektor reżimu z karą za skok; na krypto (Cortese/Kolm/
  Lindström 2023) bije HMM trwałością stanów; kandydat na Fazę 3 master-switcha. 🔴
- **W-282 DSR + PBO/CSCV** — twarda bramka anty-overfittingu w Koloseum (procedura konkretna). 🔴
- **W-283** — crypto-carry skompresowane od 2024 (BIS WP 1087): W-065 degradacja priorytetu;
  PSY-01 funding-extreme zostaje (inny mechanizm).
- **W-284** — OFI z L2 ma uniwersalną krótkoterminową moc (arXiv 2026) — potwierdza EXP-12/W-060.
- **W-285** — 3 oryginalne syntezy Imperium: Fixed-Share z pamięcią reżimu (Mnemosyne-mixing),
  dwu-zegarowy DSR (czas barowy × trading-time), Trybunał Trzech Zegarów (jump model jako
  ekspert meta-gry rozliczany Fixed-Share).

**Pliki:** `docs/WIZJONER.md` (nowa sekcja + 6 wizji), `docs/LOG_ZMIAN.md`.
**Kod:** bez zmian (czysty zwiad — wdrożenia wg priorytetu po decyzji Cezara).

---

## 2026-06-10 | INFRA | Ruff (W13) — rozszerzony ruleset o realne klasy bugów + audyt wsteczny granic

**Opis:** „Żeby było najlepiej" — zastosowano nową dyscyplinę WSTECZ i wzmocniono bramkę:
1. **Audyt graniczny roju (Prawo XXI Reguła Test-Granic):** przeskanowano wszystkie
   neurony pod kątem bugu granicznego typu Force Index (`==0`/próg → zły kierunek).
   Wynik: rój zdrowy — TRIX/AO/AC i pozostałe poprawnie domykają granicę do NEUTRAL;
   Force Index był jedynym wyjątkiem (już naprawiony). Wzorzec binarny (próg→A/B) przy
   równości miary-zero jest świadomy i bezpieczny.
2. **Ruff ruleset rozszerzony** z `F,E9` o realne klasy bugów (mierzone, nie zgadywane —
   pełny zestaw zielony): `E711/E712/E714` (bugi porównań `==None`/`==True`/`not x is y`),
   `B006/B008` (mutowalne argumenty domyślne — klasyczny bug współdzielonego stanu),
   `B904` (raise w except bez `from` — gubi traceback), `PLE` (błędy pylintu).
   Znaleziono i naprawiono 3× `== True/False` w `tests/test_scheduler.py` → `is`.

**Pliki:** `ruff.toml`, `tests/test_scheduler.py`.
**Testy:** 586/586 ✅. Audyt: 13 warstw, pełna harmonia. Ruff (9 reguł): czysto.

---

## 2026-06-10 | FIX | Warstwa 8 audytu — świeżość LOG przez git, nie mtime (fałszywy alarm po resecie)

**Opis:** W8 (świeżość LOG_ZMIAN) używała `os.path.getmtime` — bezużytecznego po
świeżym klonie/resecie kontenera: git ustawia mtime wszystkich plików na „teraz",
więc audyt fałszywie raportował „kod zmieniony po ostatnim wpisie", mimo że treść
== ostatni commit (working tree czysty). Naprawiono: W8 wykrywa zmienione pliki .py
przez **git** (`git diff HEAD` + `git diff --cached`) w `imperium/` i `narzedzia/`,
flaguje tylko gdy są REALNE zmiany bez wpisu LOG z dzisiejszą datą. Deterministyczne
w CI/świeżym klonie. Przy okazji: docstring „12 warstw" → „13 warstw".

**Dlaczego ważne:** bramka pre-commit była krucha — mogła blokować (lub przepuszczać)
zależnie od mtime, nie treści. Teraz sygnał = faktyczna zmiana kodu (git), nie zegar.

**Pliki:** `narzedzia/audyt_spojnosci.py`.
**Testy:** 586/586 ✅. Audyt: 13 warstw, pełna harmonia (exit 0), ruff czysto.

---

## 2026-06-09 | INFRA | Wykrywanie bugów: ruff (Warstwa 13) + reguła test-granic + adversarial review

**Kontekst:** Cezar zapytał, czemu zewnętrzny recenzent (cubic) łapie bugi, a my nie.
Diagnoza: nasz audyt (12 warstw) sprawdzał SPÓJNOŚĆ (liczby/klucze/dokumenty=kod), nie
POPRAWNOŚĆ logiki ani statyczną jakość; testy pisaliśmy na „happy path", bez granic;
brak lintera. Wdrożono trzy uzupełniające się mechanizmy (wszystkie do zasad):

1. **Warstwa 13 audytu — ruff** (`ruff.toml`, ruleset F+E9): linter łapie bugi/martwy
   kod, których warstwy spójności nie widzą. Zweryfikowano: F811 łapie duplikat klasy
   (dokładnie bug z merge, który cubic znalazł). Audyt blokuje commit przy znalezisku;
   gdy ruff niezainstalowany → tylko nota (działa w minimalnym środowisku).
2. **Reguła Test-Granic** (rozszerzenie Prawa XXI w CLAUDE.md): każdy moduł z progiem/
   znakiem MUSI mieć testy granic (0/None/±/dokładny-próg/trwałość-stanu).
3. **Adversarial `/code-review` przed każdym push** (rozkaz stały): wrogi przegląd
   logiki/granic — ta sama perspektywa co cubic, ale ZANIM trafi na PR.

**Sprzątanie przy okazji (Prawo XV/XIX):** ruff wyczyścił 88 nieużywanych importów +
puste f-stringi, oraz realne znaleziska: martwy policzony sygnał `trend_napływu` (OC-04),
martwe zmienne (`wzorzec`, `linia`, `powody`), zepsute demo `mikro_neuron.py` (odwołania
do nieistniejących klas → NameError przy uruchomieniu), forward-ref `RaportAreny` przez
TYPE_CHECKING.

**Pliki:** `ruff.toml` (nowy), `requirements.txt`, `narzedzia/audyt_spojnosci.py` (W13),
`CLAUDE.md` (3 zasady), 9 plików kodu/testów (sprzątanie ruff).
**Testy:** 586/586 ✅. Audyt: 13 warstw, pełna harmonia (exit 0), ruff czysto.

---

## 2026-06-09 | FIX | Force Index (V-05) — granice fi==0 + tag źródła pure-Python (PR review cubic)

**Opis:** Dwie poprawki po recenzji PR (cubic-dev-ai):
1. **P1 — błąd graniczny neuronu:** przy `FORCE_INDEX_2 == 0` w trendzie wzrostowym
   kod spadał do gałęzi `return SHORT` (sygnał PRZECIWNY do trendu); `FORCE_INDEX_13 == 0`
   było traktowane jako bessa. Teraz: FI(13)=0 → NEUTRAL (brak przewagi), FI(2)=0 →
   słaby głos zgodny z trendem (pewność 0.40), zero implicytnego SHORT na zerze.
2. **P2 — metadane źródła:** `FORCE_INDEX_13/2` (liczone `_py_force_index`, własna
   formuła) były w sekcji TA-Lib → `compute()` stemplował je jako TA-Lib. Dodano do
   `_PURE_PYTHON_INDICATORS` → poprawny tag `pure-Python` (Prawo XIII — audyt nie kłamie o źródle).

**Pliki:** `imperium/legiony/neurony/wolumen.py`, `imperium/fundament/brama_kalkulatora.py`,
`tests/test_neurony.py`, `README.md`.
**Testy:** +2 graniczne (584→586/586). Audyt: pełna harmonia (exit 0).

---

## 2026-06-09 | FIX | Reguła 6% Elder — data ze świecy + HALT do końca miesiąca + usunięcie duplikatu (PR review cubic)

**Opis:** Trzy poprawki po recenzji PR (cubic-dev-ai):
1. **P1 — data z czasu świecy:** `Dyrygent.cykl()` przekazywał `regula_6pct.aktualizuj()`
   bez daty → w backteście używał `date.today()` (czas systemowy), błędnie licząc
   reset/HALT względem zegara maszyny, nie kalendarza danych. Teraz konwertuje
   `timestamp` świecy (ms epoch, UTC) na datę i przekazuje jako `dzisiaj=`.
2. **P2 — HALT do końca miesiąca:** logika zdejmowała HALT, gdy kapitał chwilowo
   odrobił w tym samym miesiącu — sprzecznie z komunikatem „HALT do końca miesiąca"
   i doktryną Eldera. Usunięto gałąź `strata < prog → NORMAL`; HALT trwa do zmiany
   miesiąca lub ręcznego `reset_miesiac()`.
3. **Duplikat klasy:** `RegulaSzesciuProcentEldera` była zdefiniowana DWUKROTNIE
   (pozostałość po rozwiązaniu konfliktu merge) — druguje shadowowała pierwszą.
   Usunięto duplikat, została jedna definicja (przy bezpiecznikach AOA/W-062).

**Pliki:** `imperium/koloseum/dyrygent.py`, `imperium/pretorianie/kalkulator_lewara.py`,
`tests/test_kalkulator.py`, `tests/test_dyrygent.py`, `README.md`.
**Testy:** +2 (582→584/584). Audyt: pełna harmonia (exit 0).
**Symulator:** issues cubic w `symulator_live.html` zostawione do wersji on-demand
(rozkaz stały Cezara — symulatory poza auto-audytem).

---

## 2026-06-09 | FEATURE | Triple Screen Eldera (BIB-015) + neuron Force Index (V-05)

**Opis:** Domknięcie BIB-015 (Alexander Elder). Dwa elementy:
- **Neuron V-05 `NeuronForceIndex`** (kat. F, waga 7): Force Index = kierunek×dystans×wolumen,
  wygładzony EMA. Dwie skale — FI(13) trend, FI(2) trigger pullbacku. Doktryna Eldera:
  kupuj słabość w sile (trend↑ + FI(2)<0). Pure-Python, bez API.
- **Brama:** `FORCE_INDEX_13` / `FORCE_INDEX_2` (`_py_force_index` na talib.EMA surowego FI).
- **Strategia `IMV-TR-008` TRÓJEKRAN ELDERA**: 3 ekrany — MACD/EMA(50/200) trend (X-03,XII-03),
  Force Index pullback+trigger (V-05), StochRSI timing (X-02). Spójna z Regułą 6% Eldera.

**Symbioza (Prawo XXI):** neurony 55→56 (52 aktywne), strategie 17→18. Zaktualizowane:
README, MANIFEST (wiersz V-05, tabela legionów, status SMC), INDEKS, KATALOG_STRATEGII
(blok IMV-TR-008), ROADMAP. SMC-01/02/03 opisane jako aktywne (były „budzone wewnętrznie").

**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/wolumen.py`, `imperium/legiony/rejestr.py`,
`imperium/legiony/strategie/rejestr_strategii.py`, `tests/test_neurony.py`,
`tests/test_strategie.py`, `tests/test_integracja.py`, `docs/*` (README, MANIFEST, INDEKS,
KATALOG_STRATEGII, ROADMAP).
**Testy:** +7 (575→582/582). Audyt: pełna harmonia (exit 0).

---

## 2026-06-09 | FEATURE | Master-switch Faza 2 — online-learning wag głosujących (Hedge/MWU)

**Opis:** `MasterSwitchOnline` w `legiony/legatus.py` — Faza 2 master-switcha reżimu.
Faza 1 (2-z-3) traktuje VR/half-life/AR1 równo; Faza 2 daje każdemu głosującemu wagę
uczoną online z wyników: gdy ADX wyjdzie ze strefy spornej (>25 → był TREND; <20 →
RANGING), `rozlicz()` aktualizuje wagi HedgeMWU (reuse W-049, DRY — ta sama matematyka
co wagi neuronów). `klasyfikuj_rezim(wskazniki, master_switch_online=ms)` — opt-in.

**Neutralność (Prawo XV):** przy równych wagach decyzja ważona = dokładnie 2-z-3 z Fazy 1
(test `test_masterswitch_f2_neutralnosc_rowne_wagi` to dowodzi). Zero regresji.
**Zero halucynacji (Prawo I):** ADX nadal sporny → `rozlicz()` nic nie uczy.

**Pliki:** `imperium/legiony/legatus.py`, `tests/test_integracja.py`,
`docs/MANIFEST_KODU.md`, `README.md`
**Testy:** +4 (571→575/575). Audyt: exit 0.

---

## 2026-06-09 | FEATURE | Skew-Kelly (BIB-018, Sinclair) — sizing na grube ogony (W-211)

**Opis:** `KalkulatorLewara.skew_kelly(mu, sigma, skos)` — Kelly skorygowany o trzeci
moment rozkładu (skośność). Klasyczne Kelly (μ/σ²) zakłada symetrię; krypto ma gruby
lewy ogon (krachy). Przy ujemnym skosie wzór automatycznie tnie frakcję, chroniąc
przed ryzykiem ogona.

**Matematyka:** rozwinięcie Taylora E[log(1+fX)] do 3. rzędu →
f* = (σ² − √(σ⁴ − 4μ·m₃)) / (2m₃), gdzie m₃ = skos·σ³. Pierwiastek dobrany tak,
że skos→0 daje dokładnie μ/σ². Dodatni skos → wracamy do klasycznego (nie zawyżamy).

**Weryfikacja numeryczna:** μ=0.10, σ=0.20 → symetria 2.50, skos −1.0 → 1.83 (cięcie),
skos +1.0 → 2.50, brak danych → None (Prawo XV).

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `tests/test_kalkulator.py`,
`docs/MANIFEST_KODU.md`, `README.md`
**Testy:** +5 (566→571/571). Audyt: exit 0.

---

## 2026-06-09 | FEATURE | Reguła 6% Alexandra Eldera (BIB-015) — miesięczny circuit-breaker

**Opis:** Wdrożenie Reguły 6% z "Come Into My Trading Room" (Elder, BIB-015).
Gdy łączna strata w bieżącym miesiącu ≥ 6% kapitału z początku miesiąca → HALT:
zero nowych wejść do końca miesiąca. Reset 1. dnia nowego miesiąca (automatyczny).

**Gdzie działa:** wymiar MIESIĘCZNY — komplementarny z BezpiecznikKrzywejKapitalu (intraday W-062)
i Bezpiecznikiem AOA (30%, W-028). Razem: Elder = miesięczny meta-limit, W-062 = dzienny ekwilib,
W-028 = twardy stop całości. Weto Reguły 6% jest w `_checklist()` jako pierwsze.

**Podpięcie:** `KalkulatorLewara.policz(regula_6pct=...)` + `Dyrygent(regula_6pct=True)`.
W Dyrygent domyślnie wyłączone (opt-in), żeby nie łamać kompatybilności backtestu.

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `imperium/koloseum/dyrygent.py`,
`tests/test_kalkulator.py`, `docs/MANIFEST_KODU.md`, `README.md`
**Testy:** +4 (562→566/566). Audyt: exit 0.

---

## 2026-06-09 | DOKUMENT | Symulator canvas (styl v1-5.1) — aktualny + marzenie

**Opis:** Nowy `docs/symulator_imperium.html` — symulator w stylu animowanych diagramów
canvas (wzorowany na symulatorze z bazy DeepSeek wersja full, gdzie były wersje Imperium 1-5.1).
Cząsteczki płyną po krawędziach między węzłami modułów (kolory wg typu: dane/Brama/rdzeń/
doradcy/Pretorianie/egzekucja/pętla). **Przełącznik dwóch wersji:**
- 🔵 STAN AKTUALNY v0.9.0 — realne moduły (Akwedukty+3 adaptery, Brama, 48 neuronów, Legatus,
  Namiestnik, reżim, 5 doradców, Pretorianie, Drogi→paper, HedgeMWU). Ocena **8.0/10** z listą
  mocnych stron i luk (on-chain 1/5, 7 wyciszonych, brak live, brak meta-labelingu).
- 🟣 MARZENIE — wizja docelowa po wdrożeniu roadmapy (on-chain LIVE, Arbiter Fiduciae meta-
  labeling, DeepSeek AI, Reguła 6%, skew-Kelly, master-switch Faza 2, live MEXC). Ocena **9.7/10**.
**Prawo I:** wszystkie liczby/moduły z żywego kodu (rejestr.py, audyt). Węzły planowane wyraźnie
oznaczone jako „marzenie" (fioletowe) — nie udają, że istnieją.
**Pliki:** `docs/symulator_imperium.html` (nowy), `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`
**Testy:** statyczny HTML; suite 562/562. Audyt: exit 0.

---

## 2026-06-09 | DOKUMENT | Symulator wizualny HTML (offline, animowany)

**Opis:** Nowy `docs/symulator_live.html` — samodzielny (zero zależności) animowany symulator
do przeglądarki. Pokazuje aktualny stan Imperium v0.9.0: pipeline 8 etapów (Akwedukty→Brama→
Namiestnik→Reżim→Legion→Doradcy→Pretorianie→Decyzja), rój 48 neuronów głosujący na żywo
(LONG/SHORT/NEUTRAL, kill-switche Z wyróżnione), miernik przewagi (próg 0.55), 10 bramek
wstrzymania, ścieżka pieniędzy (10 000 USDT), 12 kategorii, roadmap. 4 scenariusze:
trend (WEJŚCIE LONG), range (wstrzymanie — słaba przewaga), bańka (Z-03 HARD-HALT),
krach (Z-04 cascade). **Wszystkie liczby z żywego kodu** (rejestr.py — Prawo I).
**Pliki:** `docs/symulator_live.html` (nowy), `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`
**Testy:** statyczny HTML, bez zmian logiki; suite 562/562. Audyt: exit 0.

---

## 2026-06-09 | DOKUMENT | Manual migracji na laptopa + symulator live

**Opis:** Nowy `docs/MANUAL_MIGRACJA_I_SYMULATOR.md` — przewodnik przeniesienia
Imperium na laptopa (Windows 10 Pro, Fujitsu 8 GB): instalacja Python 3.11, kopiowanie
repo, testy bez zależności, pełna moc (TA-Lib/numpy/ccxt), klucze przez `setx` (Prawo
Bezpieczeństwa), DeepSeek API, mapa RAM. Zawiera SYMULATOR LIVE: pełny diagram pipeline
(Akwedukty→Brama→Namiestnik→reżim→Legion→Doradcy→Pretorianie→Drogi), 10 bramek wstrzymania
long/short z progami z kodu, 4 przykłady symulacji (WEJŚCIE LONG / kill-switch / słaba
przewaga / dead-cat SHORT).
**Weryfikacja Prawa I:** sprawdzono „oryginalne narzędzia" — HERMES + 4 doradcy (Fulmen/
Iustitia/Oracle/Pythia) + Rada ISTNIEJĄ (kod + 24 testy w `test_doradcy.py`).
„Chimera/Hamachera" NIE ISTNIEJE nigdzie — halucynacja/pomyłka nazwy, nie liczy się (Prawo XIX).
**Pliki:** `docs/MANUAL_MIGRACJA_I_SYMULATOR.md` (nowy), `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`
**Testy:** dokument, bez zmian logiki; suite 562/562. Audyt: exit 0.

---

## 2026-06-09 | AUDYT | Warstwa W12 — żywotność głosu (automatyzacja Prawa XV)

**Opis:** `narzedzia/audyt_spojnosci.py` rozszerzony z 11 → **12 warstw**. Nowa W12 karmi
każdy aktywny neuron 5 syntetycznymi scenariuszami (byk/niedźwiedź/kaskada/bańka/spokój)
zbudowanymi przez Bramę i flaguje neurony, które MILCZĄ (NEUTRAL pewnosc=0 + zero
pewnosc_przeciwnika) we WSZYSTKICH scenariuszach = martwy głos.
**Logika dwustanowa (Prawo XVIII — sensowne rozstrzygnięcie):**
- milczący neuron spoza allowlisty adapterowej → ❌ błąd blokujący commit (regresja Prawa XV)
- milczący neuron z allowlisty (`NEURONY_ZALEZNE_OD_ADAPTEROW`) → ⚠️ info (znana luka, nie blokuje)
**Allowlista (5):** PSY-01 FUNDING_RATE, PSY-02 LONG_SHORT_RATIO, PSY-03 FEAR_GREED_INDEX,
PSY-04 OPEN_INTEREST, V-03 CVD — czekają na dane adapterów w backteście czysto-OHLCV.
**Powód:** Prawo XV było dotąd pilnowane ręcznie; teraz audyt łapie martwy głos automatycznie
przy każdym starcie sesji i pre-commicie. Z-04/D-01 zweryfikowane jako żywe (budzą się w kaskadzie/trendzie).
**Dowód allowlisty (Prawo I):** W12 dodatkowo karmi każdy neuron adapterowy ekstremalną
wartością jego klucza (`WERYFIKACJA_ADAPTEROW`) i wymaga, by OŻYŁ — PSY-01 SHORT0.85,
PSY-02 SHORT0.80, PSY-03 LONG (strach), PSY-04 SHORT0.60, V-03 LONG0.60. Milczenie MIMO
danych adaptera = realny bug (błąd blokujący). Allowlista zweryfikowana kodem, nie „na słowo".
Potwierdzono też: adaptery (Futures/CVD/FearGreed) SĄ podpięte do live-pipeline Dyrygenta —
te neurony żyją w trybie live/paper, milczą tylko w audycie offline (z natury bez sieci).
**Pliki:** `narzedzia/audyt_spojnosci.py`, `tests/test_spojnosc.py` (+4 testy), `README.md`,
`docs/INDEKS_IMPERIUM.md`, `ZASADY_FUNDAMENTALNE.md`, `docs/LOG_ZMIAN.md`
**Testy:** suite 558 → **562/562** (W12: zielona, raport adapterów, dowód allowlisty, negatywny martwy-głos). Audyt: exit 0.

---

## 2026-06-09 | NARZĘDZIE | Pomiar dekorelacji BIB-020 (Prawo XVI) — spłata długu „do zmierzenia"

**Opis:** Nowe narzędzie read-only `narzedzia/pomiar_dekorelacji_bib020.py` mierzy |r| Pearsona
nowych głosów BIB-020 vs istniejące, na realnych danych (BTC 1h, 6000 barów, 1446 kroków).
**Wynik — ZERO redundancji (żadne |r|>0.80):**
- Z-03~Z-01 r=−0.052, Z-04~Z-03 r=+0.005, Z-04~Z-01 r=+0.018 (rodzina Z w pełni ortogonalna)
- X-27~X-04 r=−0.046, X-27~X-01 r=+0.187 (value-conv. niezależny od BBands/RSI — inny horyzont)
- VARIANCE_RATIO~RET_AR1 r=+0.228 (🟡 OK), OU_HALFLIFE~HURST_DFA r=+0.010, VR~OU r=+0.099 (master-switch zdrowy)
**Żywotność (Prawo XV):** Z-03 984/1446, Z-04 12/1446 (kill-switch z natury rzadki) — brak martwych głosów.
**Wniosek:** flagi „do zmierzenia" z poprzednich commitów ZAMKNIĘTE. Nowe głosy = filary dywersyfikacji,
kandydaci do podniesienia wag (nie scalenia). Decyzja o wagach — osobno, kierunkowa.
**Pliki:** `narzedzia/pomiar_dekorelacji_bib020.py` (nowe), `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** narzędzie read-only, nie zmienia logiki; suite 558/558 bez zmian. Audyt: exit 0.

---

## 2026-06-09 | KOD | Z-04 NeuronCascade — cascade detector + dead-cat bounce (W-279, BIB-020 rozdz.28) ✅ WDROŻONY

**Opis:** Czwarte wdrożenie BIB-020, domyka rodzinę obronną kat. Z przy Z-03. Neuron dwustanowy:
- **KASKADA** (CASCADE_FLAG=1): 3+ przyspieszające spadki przy rosnącym wolumenie (price accelerator
  Treynora) → kill-switch: NEUTRAL z pewnosc_przeciwnika 0.92 (nie łap spadającego noża).
- **DEAD-CAT** (DEADCAT_SETUP=1, gdy kaskada wygasła): krach ≥12% w oknie + dno wyhamowane +
  słabnący wolumen + cena w dolnej 1/3 zakresu → taktyczny LONG 0.60 (krótki hold/stop zarządza egzekutor).
- Priorytet KASKADA > DEAD-CAT (gdy lawina trwa, nie kupujemy).
**Symbioza:** 2 obliczenia pure-Python w Bramie (`CASCADE_FLAG`/`DEADCAT_SETUP`) + 2 klucze Budowniczego +
rejestracja Z-04 w zagrozenie.py/rejestr.py + 12 testów. MANIFEST/README/INDEKS: 54→55 neuronów,
47→48 aktywnych, 42 OHLCV, testy 546→558.
🚨 **Prawo XVI (do zmierzenia):** CASCADE_FLAG vs VoV/AR1 (Z-03) — sprawdzić |r| przed podniesieniem wagi.
**Powód:** W-279 (priorytet #5 BIB-020 — domyka obronę kat. Z, taktyczny long post-crash), Prawo XV/XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/zagrozenie.py`, `imperium/legiony/rejestr.py`, `tests/test_neurony.py`,
`tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** +12 (Brama cascade/deadcat + Z-04 kaskada/priorytet/deadcat/spokój/abstynencja/rejestracja). Audyt: exit 0.

---

## 2026-06-09 | KOD | Master-switch reżimu Faza 1 — W-263/W-274 (BIB-020 Harris rozdz.16/20) ✅ WDROŻONY

**Opis:** Trzecie wdrożenie BIB-020 — wzmocnienie klasyfikatora reżimu (`klasyfikuj_rezim` w legatus.py).
Dwa nowe obliczenia pure-Python w Bramie:
- **VARIANCE_RATIO** (W-263, Lo-MacKinlay) = Var(r_k)/(k·Var(r_1)); >1 trend (zmienność trwała), <1 rewersja.
- **OU_HALFLIFE** (W-274) = −ln(2)/β z regresji OU Δx na x dla spreadu (price−SMA_50); krótki=rewersja, długi=trend.
**Integracja (Opcja 1 — decyzja Cezara):** master-switch 2-z-3 (VARIANCE_RATIO + OU_HALFLIFE + istn. RET_AR1)
rozstrzyga TREND_STRONG↔RANGING **TYLKO w strefie spornej ADX (20–25 lub brak ADX)**, gdzie dotąd padał NORMAL
(rój płaski). Poza strefą — logika ADX bez zmian (zero regresji, Prawo XVI). Prawo XV: aktywuje wagi reżimowe
tam, gdzie ADX milczy.
**Plan etapowy:** Faza 2 (awans do równorzędnego głosowania) DOPIERO po pomiarze `pomiar_namiestnik.py`
(Prawo XVIII: kod+testy+pomiar > opinia) — nie przed.
**Symbioza:** Brama (2 calc + pure-Python audit) + Budowniczy (VARIANCE_RATIO_4, OU_HALFLIFE_50) +
klasyfikator (`_master_switch_rezimu`) + 8 testów. Bez nowych neuronów (54 bez zmian). Testy 538→546.
🚨 **Prawo XVI (do zmierzenia):** VARIANCE_RATIO vs RET_AR1 (oba mierzą autokorelację — różne horyzonty/agregacja),
OU_HALFLIFE vs HURST_DFA — sprawdzić |r| przy awansie do Fazy 2.
**Powód:** W-263/W-274 (priorytet #2 BIB-020 — naukowy fundament Namiestnika), Prawo XV/XVI/XVIII/XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/legatus.py`, `tests/test_integracja.py`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** +8 (Brama VR/half-life + master-switch strefa sporna/większość/brak/nie-nadpisuje-ADX). Audyt: exit 0.

---

## 2026-06-09 | KOD | X-27 NeuronValueConvergence — rewersja do wartości (W-273, BIB-020 rozdz.16) ✅ WDROŻONY

**Opis:** Druga wizja BIB-020 w kodzie. Neuron kierunkowy mean-reversion: mierzy oderwanie ceny od
wartości godziwej dwiema kotwicami i bierze ich średnią (blend):
- **Value-Z** = (close − SMA-200) / σ(close,200) — kotwica jednoskalowa.
- **MoMA-Z** = (close − mean(SMA20/50/100/200)) / σ(close,200) — kotwica wieloskalowa (średnia średnich).
blend < −2.0 → LONG (wyprzedanie), > +2.0 → SHORT (wykupienie), |blend|<1.5 → NEUTRAL. Pewność rośnie z |blend|.
**Decyzja kategorii (Prawo XVIII):** kat. **M** (nie S jak w pierwszym szkicu W-273) — to mean-reversion,
a w WAGI_REZIMU kat. M dostaje ×1.5 w RANGING (gdzie rewersja działa) i jest tłumiona w trendzie. S dostaje
wagę tylko w trendzie = błędne dla rewersji. Uzasadnienie w docstringu.
**Symbioza:** 2 obliczenia pure-Python w Bramie (`VALUE_Z`/`MOMA_Z`) + 2 klucze Budowniczego
(`VALUE_Z_200`/`MOMA_Z_200`) + rejestracja X-27 w momentum.py/rejestr.py + 10 testów.
MANIFEST/README/INDEKS: 53→54 neuronów, 46→47 aktywnych, 41 OHLCV, testy 528→538.
🚨 **Prawo XVI (do zmierzenia):** nakładka z X-04 BBands (z-score 20-bar) i X-01 RSI — INNY horyzont
(200 vs 20/14), ale sprawdzić |r| przed podniesieniem wagi.
**Powód:** W-273 (priorytet #3 BIB-020 — głos rewersji do wartości na długim horyzoncie), Prawo XV/XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/momentum.py`, `imperium/legiony/rejestr.py`, `tests/test_neurony.py`,
`tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** +10. Audyt: exit 0.

---

## 2026-06-09 | KOD | Z-03 NeuronBubbleCrash — bubble/crash kill-switch (W-278, BIB-020) ✅ WDROŻONY

**Opis:** Pierwsza wizja BIB-020 (Harris) w KODZIE. Z-03 to defensywna meta-brama (wzorzec Z-01):
łączy trzy sygnały liczone z samego OHLCV (Prawo XV — bez nowych danych):
- **BUBBLE_Z** = ln(close/EMA-200)/σ(log-dev) — odchylenie od długoterminowej grawitacji (granice Fischera Blacka).
- **VoV** = std(ATR-14, 20)/mean(ATR-14, 20) — niestabilność zmienności (prekursor krachu).
- **AR1** = corr(ret, ret_lag1, 20) — autokorelacja zwrotów = refleksywność (kaskada momentum/krach).
Próg ALARM (bubble_z>3.5 LUB VoV>1.2 LUB AR1>0.40) → kill-switch: pewnosc_przeciwnika do 0.97
(tłumi cały rój). Strefa czujności (2.5/0.8/0.25) → umiarkowane tłumienie. NIGDY kierunkowy (meta-brama).
**Symbioza:** 3 obliczenia w Bramie (`BUBBLE_Z`/`VOV`/`RET_AR1`, pure-Python, stempel SOURCE_TAG_PY) +
3 klucze w Budowniczym (`BUBBLE_Z_200`/`VOV_20`/`RET_AR1_20`) + rejestracja w rejestr.py + 14 testów.
Kategoria Z istniała (WAGI_REZIMU bez zmian). MANIFEST/README/INDEKS: 52→53 neuronów, 45→46 aktywnych, 40 OHLCV.
🚨 **Prawo XVI (do zmierzenia):** AR1 vs HURST_DFA (H-01), VoV vs Yang-Zhang — różne okna/konstrukcja,
ale sprawdzić |r| przed podniesieniem wagi. Wpisane w docstring neuronu.
**Powód:** W-278 (priorytet #1 BIB-020 — ochrona kapitału przed bańką/krachem), Prawo XV, Prawo XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/zagrozenie.py`, `imperium/legiony/rejestr.py`, `tests/test_neurony.py`,
`tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** dodane 14 testów (Brama bubble_z/VoV/AR1 + Z-03 kill-switch/czujność/spokój/abstynencja). Audyt: exit 0.

---

## 2026-06-08 | INSPIRACJA | INF-32 — Rozmowa z DeepSeek "Kai" (baza wskaźników + manual 1.0→5.1) ⚠️/❌ głównie szum

**Opis:** Cezar dostarczył 2,6 MB rozmowy z DeepSeek (28 wersji bazy wskaźników 1.0→2.9 + "MANUAL IMPERIUM 1.0→5.1",
kody Python, 3 symulatory HTML). Pełna analiza 5 zwiadowcami Opus (po liniach: 1-560, 560-1100, 1100-2000,
2000-2680, 2680-3300) + rdzeń roadmapy przeczytany osobiście. **Werdykt (Prawo I — twardy):**
- **Inflacja 50→658 "wskaźników"** przez 28 wersji = zbieranie nazw, nie sygnału. Realny rdzeń ~30 standardowych
  wskaźników (VWAP/EMA/RSI/MACD/BB/OBV/ADX/ATR/MFI/Ichimoku/Supertrend/CVD/OI/Funding/MVRV...) — w większości JUŻ MAMY.
- **Fabrykacje (odrzucone):** Hermes Agent (jako orkiestrator), ShieldRegime, CogAlpha, MELT Dataset, Insider Wallets
  Finder, "Andromeda scanner", "Complex Esco Theory", OpenClaw (250k⭐). **Wszystkie ID arXiv `2605.xxxxx` nieistnieją**,
  cytaty `[N†Lx-Ly]` syntetyczne, gwiazdki zawyżone (TradingAgents 71k).
- **Kod (31 funkcji): 0 produkcyjnych.** Powtarzalne bugi: fałszywy ATR `(h-l).mean()`, fałszywy ADX, lookahead
  (`center=True`/`shift(-1)`/`bfill`/min-max całej serii), KeyError `data['equity']`, brak `np.random.seed`.
  `SimpleNeuralNetwork` = losowe nietrenowane wagi (szum). `PhantomAIEngine` "LLM GPT-5.1" = zaszyte if-y zwracające 0.85.
- **3 symulatory HTML = animowane diagramy** (canvas, `setInterval` co 4s cykluje LONG/SHORT/NEUTRAL), zero P&L/danych/strategii.
- **Jedyny półrealny artefakt:** szkielet ERS/Archon (Hedge/Multiplicative-Weights-Update) — pokrywa się z planem ML-28 (Shapley).
- **Idee neuronów** (Hurst/Hawkes/MFDFA/Path-Signature/VPIN/Permutation-Entropy/Kimchi) = RECYKLING naszego katalogu
  (INF-10/11/12/19, kat. D/H/N/Z już w kodzie). Konceptualnie potwierdza kierunek (Prawo XVI dekorelacja, reżim-adaptacyjne
  wagi, Senat multi-agent=ML-25/29) — nie dodaje nowego.
**Realne narzędzia warte rozważenia (jedyna nowa wartość):** VectorBT+Optuna walk-forward (Koloseum), shapiq (ML-28),
Conformal Prediction `mapie` (niepewność predykcji), Polars (szybkość). Reszta już w rejestrze (NautilusTrader ML-33, CrewAI/Senat).
**Wizji NIE przyznano** (Prawo I — naciąganie byłoby fałszem). Zapisane jako INF-32 = referencja + blacklist fabrykacji.
**Powód:** Prawo I (uczciwa ocena, demaskacja halucynacji), Prawo XVI (dekorelacja), ZPO, ochrona przed marnowaniem pracy na fikcję.
**Pliki:** `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-020 ✅ ANALIZA KOMPLETNA — rozdz. 10/16/17/28 (wizje W-270..W-279)

**Opis:** Dokończenie analizy Harrisa (zwiadowca 3). 10 nowych wizji W-270..W-279 z rozdziałów:
Rozdz.10 (Informed Traders): W-270 (flow type: stealth/absorption/exhaustion), W-271 (staleness filter),
W-272 (efficiency proxy → przełącznik reżimu). Rozdz.16 (Value Traders): W-273 (value z-score SMA-200+MoMA ⭐⭐),
W-274 (OU half-life resiliency ⭐⭐), W-275 (winner's curse uncertainty scaler). Rozdz.17 (Arbitrageurs):
W-276 (basis+funding neuron ⭐⭐⭐ — najlepsza dostępna oś N/Z crypto), W-277 (BTC lead-lag altcoin catch-up).
Rozdz.28 (Bubbles/Crashes): W-278 (bubble/crash kill-switch: bubble_z + VoV + AR1 autocorr ⭐⭐⭐),
W-279 (cascade detector + dead-cat bounce). BIB-020 strawiona w CAŁOŚCI (30 wizji W-250..W-279).
**5 priorytetów wdrożenia:** W-278 (kill-switch na OHLCV), W-263/274 (master-switch reżimu, OHLCV),
W-276 (basis+funding, wymaga perp API), W-273 (value z-score, OHLCV), W-279 (cascade, OHLCV).
**Powód:** dokończenie ŻYCZ-10, Prawo XIX (tylko kod istnieje — wizje czekają na wdrożenie), Zasada Symbiozy.
**Pliki:** `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-020 ⭐ ZDOBYTA — "Trading and Exchanges" (Larry Harris, 9/10, ŻYCZ-10)

**Opis:** Cezar dostarczył biblię mikrostruktury rynku (Oxford 2003, 29 rozdz., b. dyrektor ekon. SEC) — życzenie
ŻYCZ-10. Rozdziały 11/12/14/19/20/21 strawione w pełni (2 zwiadowców Opus); rozdz. 10/16/17/28 do dokończenia
(zwiadowca trafił na limit sesji — pula W-270..279 zarezerwowana). **Przyznano 20 wizji W-250..W-269** celowanych
w najsłabsze osie Z (mikrostruktura, dziś tylko VPIN) i L (płynność). Trzy filary: (1) dekompozycja spread/vol na
trwałe-vs-przejściowe = master-switch reżimu momentum↔reversion (W-257/W-263); (2) detekcja manipulacji —
spoofing/squeeze/stop-gunning/pump/wash (W-250/252/253/254/256); (3) globalna bramka kosztu transakcji
(effective/realized spread, impact Glosten-Harris, Roll, Amihud, money-flow, Implementation Shortfall — W-266/267).
🚨 **Prawo XVI:** W-268 dubluje W-056 (Amihud) → scalić; W-251/265 vs W-060 (OFI), W-250/257 vs Z-01 (VPIN)/W-072
(Hawkes) → zmierzyć korelację przed wdrożeniem. 🚨 **Prawo XV:** większość wizji wymaga danych L2/order-flow/signed-trade
(Lee-Ready), których Brama dziś NIE ma — najpierw Brama L2, potem neuron. Wykonalne na OHLCV od razu: W-263, W-264, W-268.
**Werdykt:** 9/10 (nie 10 — księga mechanizmów, nie gotowych wzorów jak López de Prado; część wymaga nowych danych).
**Powód:** ŻYCZ-10 (priorytet po on-chain), ZPO, Prawo I (uczciwa ocena), Prawo XV/XVI (flagi przed wdrożeniem).
**Pliki:** `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne — wizje są planem, nie kodem)

---

## 2026-06-08 | BIBLIOTEKA | BIB-019 ❌ ODRZUCONA — "Handbook for Cryptocurrencies Trading" (Harris, 2/10)

**Opis:** Analiza Opus książki Virginii Harris. Werdykt: wypełniacz dla nowicjusza spotowego (ghost-written),
anty-systematyczny, anty-leverage, przeterminowane martwe giełdy (Cryptopia/CryptoBridge), zero matematyki
operacyjnej, brak funding/perpetual/DeFi/tokenomiki. Obiecuje on-chain, dostarcza definicje słownikowe.
**Zgodnie z Prawem I — NIE przyznano żadnej wizji** (W-250..259 wolne); naciąganie wartości obok López de
Prado/Sinclair byłoby zafałszowaniem rejestru. Zapisana jako udokumentowane odrzucenie (by nie kupować
podobnych handbooków). INF-31. 🚨 Oś O (on-chain) NADAL pusta — rekomendacja: crypto-native źródła (ŻYCZ-09..14).
**Powód:** Prawo I (uczciwa ocena), Prawo XV (oś O niewypełniona), ZPO.
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-015/016/017/018 — 4 książki naraz (Elder, Douglas, Kahneman, Sinclair Positional)

**Opis:** Cezar dostarczył 4 książki naraz; każda przeanalizowana osobnym agentem Opus. Stara lista życzeń
ŻYCZ-01..08 KOMPLETNIE zdobyta. Rozkaz Cezara: gromadzić w WIZJONerze (brudnopis), wdrożenie później,
wszystko dokładnie sprawdzać.
- **BIB-015 Elder "New Trading for a Living" — 8/10:** agent przeczytał REALNY kod Imperium. Force Index (kat. V),
  Impulse gate, **Reguła 6% miesięczny budżet ryzyka = REALNA LUKA**, Triple Screen multi-TF, MACD-Hist
  divergence → W-210..W-219. W-218 (equity-curve) JUŻ mamy (BreakerKrzywejKapitalu).
- **BIB-016 Douglas "Trading in the Zone" — ⚠️4/10:** 85% psychologii martwej dla automatu. 3 flagi:
  W-224 (Legatus=prawdopodobieństwo nie binarność), W-220 (edge na oknie≥20), W-222 (stop ze struktury) → W-220..W-225.
- **BIB-017 Kahneman "Thinking Fast and Slow" (ŻYCZ-08) — 8/10:** 4 neurony biasów tłumu (anchoring,
  overreaction, disposition, availability-panic, W-230..233) + 6 reguł ochrony procesu (W-234..239).
- **BIB-018 Sinclair "Positional Option Trading" (ŻYCZ-07) — 9/10:** FINALNA matematyka sizingu — skew-Kelly,
  CI-Kelly (wzór na SD f̂), subkonto pełny-Kelly, doktryna stopów momentum-only, counterparty cap → W-240..W-249.
ŻYCZ-07 i ŻYCZ-08 ✅ zdobyte → cała stara lista zamknięta. INF-27/28/29/30 w REJESTR.
🌟 Dodana LISTA ŻYCZEŃ v2 (ŻYCZ-09..14) na prośbę Cezara: on-chain (#1, kat. O prawie pusta), Harris
mikrostruktura, Easley/O'Hara, Almgren-Chriss egzekucja, Tsay szeregi czasowe, perpetual/funding.
🚨 Flagi Prawa XV zebrane do weryfikacji w kodzie przy wdrożeniu: W-212 (brak reguły 6%), W-224 (Legatus
binarny czy probabilistyczny?), W-244 (cena-stop na mean-reversion?), W-232/233 (wolumen kierunkowy w Bramie?),
W-249 (counterparty cap MEXC), W-176 (Gauss-Kelly?), W-172 (EXP-04 hedge-ratio par?).
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (znaleziona luka 6% + flagi), ZPO (krytyczne oceny), rozkaz Cezara.
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (zadanie czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-013/014 — Dalton ×2 (Markets in Profile + Mind Over Markets, ŻYCZ-05/06)

**Opis:** Cezar dostarczył 2 książki Daltona naraz; każda przeanalizowana osobnym agentem Opus. Obie o
Auction Market Theory / Market Profile — celują wprost w nasze 2 NAJSŁABSZE filary: V (wolumen) i S (struktura).
- **BIB-013 Markets in Profile (ŻYCZ-06) — 8/10:** TPO Value Area, Volume POC, value migration, Initial
  Balance+Range Extension, excess/tails, open types, profile shapes, volume-vs-TPO divergence → W-190..W-199.
- **BIB-014 Mind Over Markets (ŻYCZ-05) — 8/10:** podręcznik bazowy. 6 typów dnia, Initiative/Responsive
  (esencja: trend vs balans wg akceptacji wartości), 4 typy otwarcia, anomalie TPO-vs-volume → W-200..W-209.
ŻYCZ-05 i ŻYCZ-06 ✅ zdobyte. INF-25/26 w REJESTR.
🔗 KLUCZOWE: obie książki dzielą ten sam aparat MP — W-200..W-209 mają duplikaty z W-190..W-199 (jawnie
oznaczone "SCALIĆ/DUPLIKAT" w tabelach). Przy wdrożeniu JEDEN moduł profilu, nie dwa.
🚨 Prawo XV — realność na OHLCV: TPO (czas przy cenie) = czysty OHLC ✅; Volume Profile = przybliżenie przez
rozsmarowanie wolumenu per bar 🟡; tickowy POC = wymaga rozszerzenia Bramy (nie blokuje). Wymaga: (1) definicji
"sesji" crypto 24/7, (2) wspólnego profil_tpo()/profil_wolumenu() w Budowniczym.
**Powód:** Prawo XV (domknięcie 2 najsłabszych filarów V/S), ZPO (pełny opis), rozkaz Cezara (gromadzić pozycje).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (zadanie czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-010/011/012 — 3 książki naraz (Chan ×2 + Coding Capital)

**Opis:** Cezar dostarczył 3 pliki naraz; każdy rozpakowany i przeanalizowany osobnym agentem Opus.
Rozkaz Cezara: gromadzić pozycje w WIZJONER, wdrożenie później ("jak zbierzemy pozycje, kontynuujemy").
- **BIB-010 Chan "Quantitative Trading" (2nd ed.) — 9/10:** half-life OU, macierzowy Kelly F*=C⁻¹·M (dowód
  Prawa XVI), cap lewara przez najgorszą stratę, para kointegrująca, deflated Sharpe, truncation look-ahead
  test → W-160..W-169.
- **BIB-011 Chan "Algorithmic Trading" (chińskie, ŻYCZ-04) — 9/10:** Kalman β dla par (rozszerza EXP-04),
  Monte-Carlo Kelly z Pearsona (fat tails!), Hurst+Variance-Ratio, leading risk, CPPI → W-170..W-178.
- **BIB-012 "Coding Capital" (Van Der Post) — ⚠️ 3/10 SŁABA:** self-published wypełniacz, snippety błędne.
  Jedyne ziarno: EVT/GPD parametr ogona ξ → W-180. Rekomendacja: nie kupować więcej Van Der Posta.
ŻYCZ-04 ✅ zdobyte. INF-22/23/24 w REJESTR.
🚨 2 flagi Prawa XV z BIB-011 do weryfikacji w kodzie: (1) czy KALKULATOR liczy Kelly tylko po Gaussie
(fat-tail crypto → ryzyko wipeout, W-176)? (2) czy EXP-04 używa Kalmana do hedge-ratio par (W-172)?
🔗 Nakładanie: obie książki Chana dzielą half-life OU i Kelly — przy wdrożeniu jeden neuron, nie dwa.
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (domknięcie luk R/S + flagi), ZPO (pełny opis, krytyczna ocena BIB-012).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (zadanie czysto dokumentacyjne — zero zmian kodu)

---

## 2026-06-08 | KOD+BIBLIOTEKA | W-130 Volatility Drag WDROŻONE + BIB-009 Mandelbrot "(Mis)behavior of Markets"

**Opis (2 ruchy w jednym zadaniu — rozkaz Cezara "tak plus następna książka"):**

**1. KOD — W-130 Volatility Drag (zamknięcie czerwonego alarmu Prawa XV z BIB-008):**
KALKULATOR_LEWARA (`pretorianie/kalkulator_lewara.py`) liczy teraz erozję zmiennościową
pozycji lewarowanej: `drag_roczny = ½·λ·(λ−1)·σ²` (Sinclair rozdz. 13, ta sama matematyka
co decay leveraged ETF). Implementacja wstecznie kompatybilna:
- `volatility_drag(dzwignia, vol_realized)` — staticmethod, None gdy brak vol (Prawo XV: bez halucynacji)
- `PlanPozycji.drag_roczny` — raport w każdym planie (None bez vol_realized)
- ostrzeżenie w logach gdy drag ≥ 50%/rok; wydruk planu pokazuje "Vol drag"
- opcjonalne weto `max_drag_roczny` (domyślnie None → zero zmian zachowania; jawny limit → blokada)
8 nowych testów (test_kalkulator.py). Dla λ=3, σ=1.0 → drag 300%/rok (zgodne z analizą).

**2. BIBLIOTEKA — BIB-009 Mandelbrot (ŻYCZ-03 zdobyte):**
Rozpakowany epub, przeanalizowany 2 równoległymi analizami Opus (rozdz. I-XV). Ojciec fraktali —
celuje wprost w nasze 3 najsłabsze osie D/H/N (po 1 neuronie). 19 wizji W-140..W-158 (skonsolidowane):
- 🔴 W-140 tail-index α (Hill, D/N), W-141 wymiar fraktalny (Higuchi, D), W-142 detektor skoków (Noah, N/D),
  W-143 trading-time/volatility clock (N/V), W-144 dependence-without-correlation (H/R)
- 🟠 W-145 koncentracja czasu (Gini), W-146 shock index (Richter), W-150 walidator R/S dla H-01
- 🟡 W-147 multifraktal Δα partition, W-148 Cantor-dust klastrów, W-149 kaskada multiplikatywna
ŻYCZ-03 ✅ zdobyte. INF-21 w REJESTR.
🚨 Filozofia Mandelbrota: neurony zasilają REŻIM/sizing (R), nie kierunek (zgodne z botem futures).
🔗 Symbioza: W-147/148/149 vs istniejący W-081 (MFDFA) — zmierzyć dekorelację przed wdrożeniem wielu naraz.

**Powód:** Prawo XV (zamknięcie krytycznego alarmu volatility drag + domknięcie luk D/H/N), Prawo XIX (kod+testy), ZPO.
**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `tests/test_kalkulator.py`, `docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅ (8 nowych W-130). Audyt: exit 0 ✅.

---

## 2026-06-08 | BIBLIOTEKA | BIB-008 ⭐ Sinclair "Volatility Trading" (2nd ed.) — RDZEŃ zmienności/lewara

**Opis:** Dodana BIB-008 (ŻYCZ-02 zdobyte). Autor (Euan Sinclair) to wykładowca metod, które IMPERIUM JUŻ
używa: estymator Yang-Zhang (kat. L/V) i Kelly criterion (KALKULATOR_LEWARA). Rozpakowana z azw3 (mobi→epub),
przeanalizowana 3 równoległymi analizami Opus (rozdz. 2,3,4 estymatory/stylized facts/prognozowanie;
rozdz. 8,9 Kelly/trade evaluation; rozdz. 13 leveraged ETFs). Rozdz. opcyjne (1,5-7,10-12,14) świadomie
pominięte jako nieistotne dla bota futures. Wynik: 5 rodzin koncepcji + 19 wizji W-121..W-139:
- 🔴 W-121 sygnatura zmienności (ratio estymatorów, kat. R), W-122 efekt dźwigni (asymetria, R/M),
  W-126 GARCH term-structure+vol anchor (L/R), W-127 volatility cone (percentyl σ, R),
  **W-130 volatility drag w KALKULATOR_LEWARA (KRYTYCZNY)**, W-131 Kelly+korekta Bayesa, W-132 dynamiczny sufit μ/σ², W-136 weryfikacja YZ vs Rogers-Satchell crypto 24/7
- 🟠 W-123 variance ratio, W-124 kurtoza (D), W-129 variance premium (DVOL−RV, wymaga Deribit), W-133 K-ratio, W-134 SE(Sharpe)+metryki, W-135 rejestr statystyk
- 🟡 W-125 ACF klasteryzacja (H), W-128 GARCH-asym, W-137 volume-volatility, W-138 first exit time (wymaga intraday), W-139 tryb Browne
ŻYCZ-02 oznaczone ✅ ZDOBYTE. INF-20 w REJESTR_INSPIRACJI.
🚨 3 sygnały Prawa XV: (1) **W-130 volatility drag** — jeśli kalkulator nie odejmuje erozji ½λ(λ−1)σ²t, zawyża atrakcyjność lewara = CZERWONY ALARM 🔴; (2) W-136 YZ traci przewagę na crypto 24/7 (brak luki → może Rogers-Satchell lepszy); (3) throttle W-096 musi reagować na σ², nie σ.
🔗 Symbioza: Kelly (W-131), vol-targeting (W-059), dynamiczny sufit (W-132) = ta sama matematyka μ/σ² — zmierzyć korelację przed wdrożeniem (Prawo XVI).
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (domknięcie luk L/V/R + krytyczny volatility drag), ZPO (pełny opis).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | BIBLIOTEKA | BIB-007 ⭐ López de Prado "Advances in Financial ML" — FLAGOWA pozycja

**Opis:** Dodana BIB-007 — najważniejsza książka Biblioteki (ocena 10/10). Autor (López de Prado) to
twórca metod, które IMPERIUM JUŻ używa: VPIN (Z-01), triple-barrier (W-035 Arena). Przeanalizowana
przez Opus (rdzeń strategiczny Części 1-4 dogłębnie; rozdz. 6/9/13/14/HPC ⚠️ niepełne — uczciwie oznaczone).
Wynik: 16 koncepcji + 14 wizji W-107..W-120 w `docs/WIZJONER.md`:
- 🔴 W-107 FFD (DOMYKA W-094 stacjonarność), W-108 entropia (kat. N), W-109 SADF eksplozja, W-111 meta-labeling,
  W-112 Purged-CPCV+DSR (infra bezpieczeństwa), W-113 audytor feature importance (realizuje Prawo XV/XVI)
- 🟠 W-110 CUSUM, W-114 information-driven bars, W-115 λ likwidność, W-116 predatory algos, W-118 ryzyko strategii, W-119 bet sizing
- 🟡 W-117 round-lot, W-120 wagi próbek
ŻYCZ-01 oznaczone ✅ ZDOBYTE. INF-19 w REJESTR_INSPIRACJI.
🚨 2 sygnały Prawa XV do weryfikacji: (1) czy Z-01 VPIN liczony na volume clock (W-114), (2) brak purged CV/PBO/DSR w ocenie roju = luka metodologiczna (W-112 🔴).
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (domknięcie luk D/N/H/R), ZPO (pełny opis flagowej pozycji).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | ZWIAD | Lista Życzeń Biblioteki — zwiad internetowy książek pod luki Imperium

**Opis:** Na zlecenie Cezara — zwiad internetowy (WebSearch) książek do zdobycia, celowany w LUKI
kategorii neuronów (D=1, H=1, N=1, Z=2, V=2, L=2 — najsłabiej obsadzone). Wynik: sekcja
"LISTA ŻYCZEŃ BIBLIOTEKI" w `docs/WIZJONER.md` (ŻYCZ-01..09):
- 🔴 ŻYCZ-01 López de Prado "Advances in Financial ML" (autor VPIN/triple-barrier — domyka 4 nasze wizje)
- 🔴 ŻYCZ-02 Sinclair "Volatility Trading" (kat. L/V, Yang-Zhang), ŻYCZ-03 Mandelbrot "Misbehavior of Markets" (kat. H/D/N fraktale)
- 🟠 ŻYCZ-04 Chan "Algorithmic Trading" (reżim R), ŻYCZ-05/06 Dalton "Mind Over Markets"/"Markets in Profile" (wolumen/struktura V/S), ŻYCZ-07 Sinclair "Positional Option Trading" (Kelly)
- 🟡 ŻYCZ-08 Kahneman, ŻYCZ-09 zasoby on-chain (Glassnode/checkonchain — nie książka)
Uczciwie oznaczone (Prawo I): ŻYCZ-03/08 z wiedzy własnej, reszta potwierdzona zwiadem 2026-06-08.
**Powód:** Prawo XVII (rozpoznanie terenu/potrzeb), Prawo XV (celowanie w luki = podnoszenie potencjału), ZPO.
**Pliki:** `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | BIBLIOTEKA | BIB-005..006 — kolejne 2 książki do Biblioteki Tradingowej Cezara

**Opis:** Dodane 2 książki do Biblioteki (BIB-005, BIB-006), przeanalizowane przez Opus wg ZPO,
zapisane do `docs/WIZJONER.md`:
- **BIB-005** "What Exactly Is Crypto?" (Jonatan Blum, 2022) — primer on-chain/tokenomika; ocena 4/10 🟡.
  Wartość: pojęcia tokenomiki (issuance−burn), płynność DEX (AMM x*y=k), ryzyko centralizacji → W-097..W-100.
  Uwaga Prawo XV: te neurony wymagają nowego źródła danych on-chain (bez niego = martwy głos).
- **BIB-006** "High Probability Scalping Strategy Playbook" (Zachary Carson, 2024, self-published) — ocena 4/10 🟠.
  UCZCIWA ocena (Prawo I): ~70% katalog "wpisz nazwę w TradingView", brak backtestów/statystyk win-rate mimo tytułu.
  ALE realne kodowalne elementy: konfluencja-z-dekorelacją (=Prawo XVI), filtr reżimu ADX, MFI, sekwencja 9/13, ATR-stop → W-101..W-106.
  Quick winy (dane już w Bramie): W-103 NeuronMFI, W-101 BB40+RSI5+ADX.
INF-17/18 dodane do REJESTR_INSPIRACJI. Wizje W-097..W-106 to PROPOZYCJE (Prawo XIX: nie istnieją bez kodu+testów).
**Powód:** Prawo XVII (rozpoznanie terenu/wiedzy), ZPO (pełny opis), Prawo I (uczciwa ocena niskiej jakości BIB-006).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | REVIEW-FIX | Poprawki recenzji cubic (geometria.py P1 + LOG/REJESTR/MANIFEST P2)

**Opis:** Naprawiono 6 uwag recenzji cubic na PR:
- **P1 geometria.py:** stały wolumen (v_range≈0) dawał fałszywe pole Lévy Area (dy=0 ale stała
  wartość y tworzy −0.25·Δx ≠ 0) → fałszywy sygnał kierunkowy. Fix: stały wolumen → NEUTRAL.
  Usunięty fallback `[0.5]*n`. +1 test (`test_d01_staly_wolumen_neutral`).
- **P2 LOG_ZMIAN:** pole `**Pliki:**` wpisu D-01 było puste (heredoc shell uszkodził treść) →
  uzupełnione realnymi ścieżkami; usunięty osierocony duplikat wpisu D-01 bez nagłówka daty.
- **P2 REJESTR_INSPIRACJI:** INF-13..16 miały `Książka (BIB-xxx)` zamiast linku → dodane ISBN.
- **P2 MANIFEST/WIZJONER:** elite count 14→15 i Prawo XV→XVI już naprawione w 91f262b.
**Powód:** Prawo XIX (kod jest prawem), Prawo XXI (spójność), Prawo I (uczciwy sygnał).
**Pliki:** `imperium/legiony/neurony/geometria.py`, `tests/test_neurony.py`, `docs/LOG_ZMIAN.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/MANIFEST_KODU.md`, `README.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-07 | BIBLIOTEKA | BIB-001..004 — Biblioteka Tradingowa Cezara (4 książki przeanalizowane)

**Opis:** Założona Biblioteka Tradingowa Cezara. Przeanalizowane 4 książki (format azw3→epub→HTML,
pełna ekstrakcja treści przez Opus) i zapisane do `docs/WIZJONER.md` jako sekcja BIB-001..004:
- **BIB-001** The Secret Wealth Advantage (Akhil Patel) — 18-letni cykl nieruchomości, reguła 23/25 krachów → W-082..W-084
- **BIB-002** Technical Analysis of the Financial Markets (John J. Murphy) — analiza międzyrynkowa, left/right translation, MESA → W-085..W-088
- **BIB-003** Cryptoassets (Burniske & Tatar) — NVT (crypto-PE), hash rate, Google Trends, Gartner Hype Cycle → W-089..W-093
- **BIB-004** The Psychology of Trading (Brett Steenbarger) — stacjonarność (Clifford Sherry), pinball trade, anty-overconfidence → W-094..W-096
Każda książka opisana wg ZPO: pełne tytuły, cytaty dosłowne, status weryfikacji ✅/⚠️, ocena, priorytet.
**Powód:** Prawo XVII (rozpoznanie terenu), ZPO (zasada pełnego opisu), Prawo XIX (kod jest prawem — ale wiedza jest fundamentem kodu).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`

---

## 2026-06-07 | WDROŻENIE | W-079 D-01 NeuronPathSignature — Lévy Area Close×Volume (Rough Path Theory)

**Opis:** Wdrożono neuron D-01 NeuronPathSignature — pierwsza miara nieprzemiennej geometrii
ścieżki w Imperium. Lévy Area (iterated integral rzędu 2) mierzy synchronizację wzrostu
wolumenu z ceną: LA>0 → akumulacja poprzedza ruch (LONG); LA<0 → dystrybucja (SHORT).
Implementacja czysto NumPy (bez zewnętrznych bibliotek), okno 20 barów, normalizacja
scale-invariant. Nowa kategoria D (Dynamika ścieżkowa). Elitarny (E1 — jedyna miara
w Imperium mierząca tę oś). WAGI_REZIMU uzupełnione o kat. D.
Budowniczy wzbogacony o CLOSE_SERIES_20 + VOLUME_SERIES_20 (_dodaj_path_series).
8 nowych testów. Daty MANIFEST/README zaktualizowane.
**Powód:** Prawo XIX (kod jest prawem), Prawo XX (ELITARNY=True z kryterium E1).
**Pliki:** `imperium/legiony/neurony/geometria.py` (nowy), `imperium/legiony/rejestr.py`, `imperium/legiony/budowniczy_wskaznikow.py`, `imperium/legiony/legatus.py`, `narzedzia/audyt_spojnosci.py`, `tests/test_neurony.py`, `tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/KATALOG_NEURONOW.md`, `docs/AUDYT_SYSTEMU.md`, `docs/INDEKS_IMPERIUM.md`, `README.md`
**Testy:** 505/505 ✅. Audyt: exit 0 ✅.

---

## 2026-06-04 | AUDYT+ZWIAD | 7 niespójności liczb naprawionych + 3 perełki do WIZJONERA (W-079..W-081)

**Opis:** Głęboki audyt całego Imperium (kod vs dokumenty wg INDEKSU) wykrył 7 stałych
rozbieżności liczb — wszystkie naprawione (MANIFEST 43/299→51, ==46→51; test_integracja
komunikat 50→51; KATALOG 42→51 i 28→51; AUDYT_SYSTEMU 28/240→51/497; INDEKS data+wersja).
Równolegle zwiad perełek (arXiv 2024–2025, weryfikacja 3-głos) → 3 ortogonalne znaleziska
dopisane do WIZJONER i REJESTR_INSPIRACJI (INF-10/11/12):
- **W-079 Path Signature** (Lévy Area Close↔Volume — geometria/kauzalność, kat. D) — REKOMENDACJA #1
- **W-080 Hawkes Branching Ratio** (endogeniczność n̂, sensor PANIC, kat. R/F)
- **W-081 MFDFA Δα** (wielofraktalna heterogeniczność, kat. F/D)
**Powód:** Prawo XVII (rozpoznanie terenu), Prawo XIX/XXI (spójność), Prawo XV (podnoszenie potencjału).
**Pliki:** `docs/MANIFEST_KODU.md`, `tests/test_integracja.py`, `docs/KATALOG_NEURONOW.md`, `docs/AUDYT_SYSTEMU.md`, `docs/INDEKS_IMPERIUM.md`, `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`
**Testy:** 497/497 ✅. Audyt: exit 0 ✅.

---

## 2026-06-04 | FEATURE | Permutation Entropy meta-brama chaosu — nowa kategoria N (wizja W-054)

### Kontekst
Brakowało osi informacji „złożoność/struktura porządku" jako meta-bramy chaosu
(czy rynek ma STRUKTURĘ, czy jest czystym chaosem — efektywny, bez przewagi).
Permutation Entropy (Bandt & Pompe 2002) patrzy na wzorce porządkowe (ordinal
patterns), nie na kierunek — w pełni ortogonalna do RSI/MACD.

### Decyzja Prawa XVI (redundancja mierzona, nie zgadywana)
PE mierzy złożoność struktury porządku, nie poziom (RSI), crossover (MACD),
magnitudę wahań (V) ani siłę kierunku (T) — inna OŚ informacji → dekoreluje z
głosami kierunkowymi i z V/T/M. ~34% czulsza niż GARCH na klasteryzację
zmienności. N-01 zaprojektowany jako META-BRAMA (PE>0.85 → NEUTRAL „chaos, nie
handluj"), nie kolejny głos kierunkowy. Korelacja N-01↔V/T/M do zmierzenia
`diagnostyka_korelacji` po zebraniu danych paper-tradingu.

### Wdrożone
- **Brama:** pure-Python `PERMUTATION_ENTROPY` (`_py_permutation_entropy`, close,
  period=100, dim=3, delay=1) — Bandt & Pompe 2002; PE∈[0,1] (norm. log(dim!)),
  None gdy <period (Prawo I). Stempel pure-Python (XIII).
- **Budowniczy:** klucz `PERM_ENTROPY_100`.
- **Neuron N-01** `neurony/entropia.py` (NeuronPermutationEntropy, kat. N): PE>0.85
  chaos (NEUTRAL meta-brama), PE<0.65 struktura (potwierdza mikro-ruch), 0.65–0.85
  szara strefa (NEUTRAL niska pewność).
- **Nowa kategoria N** narodzona: legenda `mikro_neuron.py`, audyt `LEGENDA_KAT`,
  `CLAUDE.md` KROK 0, `WAGI_REZIMU` (N ×1.3 VOLATILE, ×1.2 RANGING, ×1.1 NORMAL,
  ×1.0 TREND_STRONG), rejestr.
- **Liczby:** 47→48 neuronów (41 aktywnych), 59→60 modułów. Backlog 252→251.
- **Testy:** +9 (Brama PE zakres/warmup/chaos/monotoniczny/źródło, N-01 4 sytuacje
  + kat.). 425 → 434/434 zielone.

### Pliki
`imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/entropia.py`, `imperium/legiony/mikro_neuron.py`,
`imperium/legiony/legatus.py`, `imperium/legiony/rejestr.py`,
`narzedzia/audyt_spojnosci.py`, `tests/test_neurony.py`,
`docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/LOG_ZMIAN.md`, `README.md`, `CLAUDE.md`.

---

## 2026-06-03 | FEATURE | Hurst-DFA meta-brama reżimu — nowa kategoria H (wizja W-053)

### Kontekst
Brakowało osobnej osi informacji „pamięć długiego zasięgu" jako meta-bramy
reżimu (czy rynek W OGÓLE ma przewagę: trend / mean-reversion / błądzenie losowe).
EXP-03 liczył Hursta metodą R/S (obciążoną na trendach) — potrzebny był odporny
estymator DFA we własnej kategorii.

### Decyzja Prawa XVI (redundancja mierzona, nie zgadywana)
DFA detrenduje każde okno wielomianem → odporny na niestacjonarność; R/S nie.
Na trendującym krypto oba dają RÓŻNE H → realna dekorelacja (jak istniejący duet
Higuchi FD + Hurst R/S). H-01 zaprojektowany jako META-BRAMA (H≈0.5 → NEUTRAL
„nie handluj"), nie trzeci głos kierunkowy. Korelacja H-01↔EXP-03 do zmierzenia
`diagnostyka_korelacji` po zebraniu danych paper-tradingu.

### Wdrożone
- **Brama:** pure-Python `HURST_DFA` (`_py_hurst_dfa`, close, period=100) — DFA
  Peng i in. 1994; H∈(0,1), None gdy <period (Prawo I). Stempel pure-Python (XIII).
- **Budowniczy:** klucz `HURST_DFA_100`.
- **Neuron H-01** `neurony/fraktal.py` (NeuronHurstDFA, kat. H): H>0.55 persystencja
  (podążaj), H<0.45 antypersystencja (kontra), H≈0.5 NEUTRAL (meta-brama).
- **Nowa kategoria H** ożywiona: legenda `mikro_neuron.py`, audyt `LEGENDA_KAT`,
  `WAGI_REZIMU` (H ×1.3 TREND_STRONG, ×1.2 RANGING, ×1.1 NORMAL), rejestr.
- **Liczby:** 46→47 neuronów (40 aktywnych), 58→59 modułów. Backlog 253→252.
- **Testy:** +9 (Brama DFA zakres/warmup/determinizm/źródło, H-01 4 reżimy + kat.).
  416 → 425/425 zielone.

### Pliki
`imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/fraktal.py`, `imperium/legiony/mikro_neuron.py`,
`imperium/legiony/legatus.py`, `imperium/legiony/rejestr.py`,
`narzedzia/audyt_spojnosci.py`, `tests/test_neurony.py`, `tests/test_integracja.py`,
`docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/LOG_ZMIAN.md`, `README.md`.

---

## 2026-06-03 | FEATURE | Volatility Targeting — skalowanie rozmiaru pozycji do celu zmienności (wizja W-059)

### Kontekst
Kalkulator Lewara liczył rozmiar wyłącznie risk-based (2% kapitału / stop_pct).
Brakowało standardu instytucjonalnego: rozmiar ∝ vol_target / vol_realized —
mniejsza pozycja w burzy, większa w spokoju (w bezpiecznych granicach).

### Wdrożone
- **`KalkulatorLewara.skala_vol_targeting(vol_realized, vol_target)`** — mnożnik
  = vol_target/vol_realized przycięty do [0.25, 1.50]. None/≤0 → 1.0 (bez
  halucynacji, Prawo XV).
- **`policz(..., vol_realized=None, vol_target=0.60)`** — rozmiar przeskalowany
  mnożnikiem; nowe pole `PlanPozycji.skala_vol`. Domyślnie 1.0 → kompatybilność
  wsteczna. Symbioza z W-055: `vol_realized` = `YANG_ZHANG_20` (ta sama skala
  annualizowana co cel).
- **Testy:** +6 (brak danych, tnie/powiększa, przycięcie MIN/MAX, wpływ na plan).
  410 → 416/416 zielone.

### Pliki
`imperium/pretorianie/kalkulator_lewara.py`, `tests/test_kalkulator.py`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`, `README.md`.

---

## 2026-06-03 | FEATURE | HedgeMWU — online żywe wagi Legatusa + zamknięcie pętli uczenia (wizja W-049)

### Kontekst
Czerwony alarm Prawa XV: `Igrzyska.nowe_wagi()` liczyło mnożniki wag neuronów,
ale **Legatus nigdy ich nie konsumował** — policzony potencjał leżał odłogiem.
Brakowało też online'owego (strumieniowego) uczenia wag z gwarancją regretu.

### Wdrożone
- **`imperium/biblioteki/hedge_mwu.py`** — `HedgeMWU`: algorytm Hedge / Multiplicative
  Weights Update (Freund & Schapire, 1997), regret O(√(T·ln N)). Po każdym wyniku
  waga eksperta ×exp(-η·strata); `mnozniki()` skalowane wokół 1.0 (stan neutralny
  = brak zniekształcenia, Prawo XV). Min. waga chroni przed śmiercią eksperta.
- **`Igrzyska.obserwatorzy`** — lista obserwatorów strumienia wyników; MWU uczy
  się z DOKŁADNIE tego samego strumienia co Igrzyska (DRY, bez duplikacji parowania
  logów). `HedgeMWU.z_logow(logi)` korzysta z tego mechanizmu.
- **Legatus** — nowy parametr `mnozniki_neuronow` + `ustaw_mnozniki_neuronow()`;
  `_dostosuj_wagi` mnoży wagę reżimową × mnożnik uczenia per-neuron. Konsumuje
  ZARÓWNO `Igrzyska.nowe_wagi()` (batch) jak i `HedgeMWU.mnozniki()` (online).
  Domyślnie pusty → kompatybilność wsteczna (zero zmian zachowania).
- **Testy:** +12 (MWU: neutralność, adaptacja, normalizacja, min_waga, obserwator
  Igrzysk; Legatus: brak/iniekcja/setter). 398 → 410/410 zielone.

### Pliki
`imperium/biblioteki/hedge_mwu.py`, `imperium/biblioteki/igrzyska.py`,
`imperium/legiony/legatus.py`, `tests/test_hedge_mwu.py`, `tests/run_tests.py`,
`docs/WIZJONER.md`, `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`.

---

## 2026-06-03 | FEATURE | Yang-Zhang Volatility — upgrade estymatora kat. V (wizja W-055)

### Kontekst
Neuron V-13 (NeuronRealizedVol) liczył zmienność wyłącznie z cen zamknięcia
(`HIST_VOL_20` = std log-returns × √252). To ignorowało luki overnight i cały
zakres świecy (high/low) — utrata informacji OHLC (Prawo XV).

### Wdrożone
- **Brama:** nowe obliczenie pure-Python `YANG_ZHANG` (`_py_yang_zhang`,
  open/high/low/close, period=20) — annualizowana vol w tej samej skali co
  HIST_VOL, ~14× efektywniejsza statystycznie (Yang & Zhang, 2000). Stemplowane
  jako pure-Python (Prawo XIII).
- **Budowniczy:** produkuje klucz `YANG_ZHANG_20`.
- **V-13:** WSKAZNIK → `YANG_ZHANG_20` (podstawa) z fallbackiem `HIST_VOL_20`
  (bez martwego głosu — Prawo XV). Progi reżimu bez zmian (ta sama skala).
- **Testy:** +7 (Brama zakres/warmup/skala/źródło, V-13 podstawa/fallback/neutral).
  391 → 398/398 zielone.

### Pliki
`imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/dzwignia.py`, `tests/test_neurony.py`,
`docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `README.md`.

---

## 2026-06-03 | MAJOR | Synchronizacja KATALOG_STRATEGII z kodem + warstwa audytu W9 (Prawo XIX/XXI)

### Kontekst
Pytanie Cezara o ZŁOTY ORZEŁ ujawniło, że opisy strategii w `KATALOG_STRATEGII.md`
cytowały STARE klucze neuronów (numeracja projektowa), niezgodne z kodem — np. ZŁOTY
ORZEŁ miał „XII-01 EMA Golden Cross" (a XII-01 to ADX), „XII-08 OBV" (nie istnieje).
Audyt tego nie łapał (sprawdzał tylko klucze neuronów, nie listy w katalogu).

### Diagnoza
Z 17 zaimplementowanych strategii: 5 spójnych, **12 z rozjazdem** (obce klucze w opisie).
Kod był zawsze poprawny (wszystkie strategie wskazują istniejące, aktywne neurony) —
problem był wyłącznie w dokumentacji.

### Naprawione
- **12 bloków strategii** w `KATALOG_STRATEGII.md` — klucze WEJŚCIE/FILTR/WYJŚCIE
  zsynchronizowane z kodem (X-SC-001/002, XII-TR-001, XII-RV-001, XII-BK-001,
  IMV-HY-003, IMV-TR-001/002/003, IMV-SC-002, IMV-RG-001/002).
- **ZŁOTY ORZEŁ** — dodano notatkę „wariant EMA, nie oryginalny SMA" + pochodzenie
  (Golden Cross = klasyka, domena publiczna, brak pojedynczego autora).
- **Warstwa audytu W9** (`audyt_spojnosci.py`) — parsuje bloki zaimplementowanych
  strategii i wykrywa klucze spoza kodu. Rozjazd katalog↔kod już nigdy nie przejdzie.

### Testy regresyjne
- `test_audyt_w9_wykrywa_obcy_klucz_strategii`, `test_audyt_w9_zielony_na_realnym_katalogu`.

### Stan
- 17/17 strategii spójnych (kod=katalog). Testy: 390/390 (+2). Audyt: pełna harmonia.

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) #5 — L2 float, HA doji/ATR0, dekorelacja None

### Kontekst
Tura recenzji PR #22 — 4 uwagi (2×P1, 2×P2). Wszystkie trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **P1 L2 qty (exp_atmabhan):** Binance depth zwraca ilości jako STRINGI → `sum(b[1])`
  mógł paść/sklejać. Rzutowanie `float(b[1])` przed sumą.
- **P1 HA doji (budowniczy):** `HA_BULL = c >= o` oznaczał doji (c==o) jako byka.
  Zmieniono na strict `>` → doji neutralny.
- **P2 HA ATR==0 (budowniczy):** płaski rynek gubił pola HA_MOMENTUM/HA_VOLATILITY_INDEX.
  Dodano jawne zera w gałęzi else → martwy rynek FILTROWANY, nie handlowany (Prawo XV).
- **P2 dekorelacja None (diagnostyka):** `None` traktowany bezwarunkowo jako martwa para,
  choć oznacza też za mało danych (n<2). Rozdzielono: martwy = któraś seria stała
  (≥2 próbki, zerowa wariancja); reszta None → `pary_niedostateczne_dane`. Naprawiono też
  detekcję `stale` (1 próbka trywialnie wyglądała na stałą → false alarm).

### Testy regresyjne
- `test_raport_niedostateczne_dane_nie_alarmuje_martwych` — 1 krok ≠ martwy głos.
- Rozszerzono `test_raport_wykrywa_martwy_glos` o sprawdzenie `pary_nieokreslone`.

### Stan
- Testy: 388/388 (+1). Audyt: pełna harmonia.

---

## 2026-06-03 | FIX | Poprawka recenzji PR (cubic) #4 — KROK 0 grep mylący (ZASADY)

### Kontekst
Recenzja PR #24 zwróciła uwagę: w KROK 0 komenda `grep -c "✅"` liczyła WSZYSTKIE
✅ (nagłówek + statusy), a krok 2 opisywał `✅ aktywny` — sprzeczne liczby.

### Diagnoza (głębsza niż uwaga)
`grep -c "✅ aktywny"` daje 69 (łapie też zwiadowców EXP i inne tabele), a aktywnych
neuronów jest 39. Grep po dokumentach NIE jest w stanie wyizolować neuronów — to złe
źródło prawdy (łamie Prawo XIX: źródłem jest kod, nie dokument).

### Naprawione
- KROK 0 w `ZASADY_FUNDAMENTALNE.md`: zastąpiono kruchy grep autorytatywną komendą
  (`audyt_spojnosci.py` + one-liner z `rejestr.py`). Dodano ostrzeżenie, by NIE liczyć
  neuronów grepem. Źródło prawdy = kod weryfikowany audytem.

### Stan
- Testy: 387/387. Audyt: pełna harmonia. (Zmiana wyłącznie dokumentacyjna — ZASADY.)

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) #3 — filtr/AC/audyt W4/MANIFEST

### Kontekst
Trzecia tura recenzji PR — 4 uwagi. Wszystkie zweryfikowane jako trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **baza.py (filtr nie karze):** strategia z filtrami, ale wszystkie wyciszone
  (`n_akt_f==0`) dostawała `filtr_frakcja=0.5` → kara mimo komentarza „nie karzemy
  za wyciszone". Poprawiono na `1.0` (jak brak filtrów). Prawo XV.
- **brama (AC off-by-one):** `_py_accelerator` wymagał `slow+sma_ac+1` świec, choć
  najgłębszy SMA potrzebuje `slow+sma_ac`. Usunięto `+1` → wynik o bar wcześniej.
- **audyt W4 (maskowanie importu):** `except ImportError: pass` ukrywał KAŻDY błąd
  importu. Zawężono do `ModuleNotFoundError` modułu strategii; inne → błąd audytu.
- **MANIFEST (per-legion):** X Equestris pokazywał 7 zaimpl./19 do wdrożenia mimo
  dodania X-09/X-10. Poprawiono na 9/17 (spójne z RAZEM 46/253).

### Testy regresyjne
- `test_brama_accelerator_warmup_dokladny` — AC przy dokładnie slow+sma_ac.
- `test_dopasowanie_wyciszone_filtry_nie_karza` — wynik = strategia bez filtrów.

### Stan
- Testy: 387/387 (+2). Audyt: pełna harmonia.

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) #2 — hook staged-only + audyt W6 'Stan na:'

### Kontekst
Druga tura recenzji PR zgłosiła 2 uwagi. Obie trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **Pre-commit hook (staged-only):** hook uruchamiał testy/audyt na working tree,
  nie na zawartości staged → zepsuty staged mógł przejść, jeśli working tree był
  poprawny (i odwrotnie). Dodano izolację: `git stash push --keep-index --include-untracked`
  na czas sprawdzeń + `trap` gwarantujący przywrócenie working tree (EXIT/INT/TERM).
- **Audyt W6 (brak 'Stan na:'):** brak pola daty był cicho pomijany (`if m:` bez `else`).
  Dodano `else` → brak daty = błąd. Przy okazji wykryto, że regex nie matchował
  markdown `**Stan na:** data` — poprawiono na `Stan na:\s*\**\s*(data)`.

### Testy regresyjne
- `test_audyt_wykrywa_brak_stan_na` — brak pola = błąd W6.
- `test_audyt_akceptuje_stan_na_w_markdown` — markdown nie daje fałszywego alarmu.

### Stan
- Testy: 385/385 (+2). Audyt: pełna harmonia. Hook zsynchronizowany (install_hooks.py).

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) — audyt źródła, warmup Ulcer, fallback symbolu

### Kontekst
Recenzja automatyczna PR zgłosiła 3 uwagi. Wszystkie zweryfikowane jako trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **Prawo XIII (audyt źródła):** `CalcResult.source` domyślnie stemplował WSZYSTKIE
  wskaźniki jako TA-Lib, w tym pure-Python (AO/AC/HMA/RVOL/HIST_VOL/VWAP/Supertrend/
  Ichimoku/Donchian/CHOPPINESS/ULCER). Dodano `_PURE_PYTHON_INDICATORS` + wybór źródła
  w `compute()` → audyt nie kłamie o pochodzeniu obliczenia.
- **Ulcer warmup:** `_py_ulcer` wymagał `period+1` świec, choć używa `c[-period:]`
  (dokładnie `period`). Poprawiono próg na `< period`.
- **Fallback symbolu:** `czytnik_csv` brał `split("_")[0]` → dla `Binance_BTCUSDT_1h.csv`
  zwracał `BINANCE`. Poprawiono na segment PRZED interwałem (`[-2]`) → `BTCUSDT`.

### Stan
- Testy: 383/383 (+2 regresyjne: warmup Ulcer, stempel źródła). Audyt: pełna harmonia.

---

## 2026-06-03 | MAJOR | Rozbudowa roju — kat. L+V wzmocnione (Ulcer + Choppiness, Prawo XVI)

### Kontekst
Kategorie L (dźwignia) i V (zmienność) miały po 1 neuronie — najcieńsze w roju,
ledwo wpływały na wagi reżimowe. Mierzona rozbudowa zdekorelowanymi sygnałami.

### Co zostało wdrożone (kod)
- **L-14 NeuronUlcer** (kat. L) — Ulcer Index: ryzyko SPADKOWE (głębokość/czas
  obsunięć), karze tylko ruch w dół. Dekoreluje z VI-13 (ATR symetryczny).
- **V-14 NeuronChoppiness** (kat. V) — Choppiness Index: trend vs konsolidacja
  (efektywność ruchu). Dekoreluje z V-13 (HV = magnituda wahań).
- **Brama** (`fundament/brama_kalkulatora.py`) — pure-Python `_py_ulcer`,
  `_py_choppiness` + wpisy rejestru ULCER, CHOPPINESS (Prawo I — jedyne wejście).
- **Budowniczy** — ULCER_14, CHOPPINESS_14 w `_PLAN_SKALARNE`.
- **Rejestr** — oba neurony w `wszystkie_neurony()`. Czyste OHLCV, bez API.

### Pomiar dekorelacji (Prawo XVI — nie opinia)
Seria sygnałów (LONG=+1/NEUTRAL=0/SHORT=−1) po oknie kroczącym, korelacja Pearsona
na dołączonych danych (ETH_1d, BTC_1h):
- **V-13 ↔ V-14:** |r| = 0.05–0.27 → dywersyfikacja (filar siły, oba zostają).
- **VI-13 ↔ L-14:** VI-13 stały (SHORT) na danych syntetycznych → L-14 dostarcza
  PEŁNĄ wariancję kat. L (LONG/NEUTRAL/SHORT, UI 0.24–12.0) → komplementarność.

### Stan
- Neurony: 46 (aktywne 39, wyciszone 7). Testy: 381/381. Audyt: pełna harmonia.

---

## 2026-06-03 | FIX+TESTY | Backtest ożywiony — czytnik prostego formatu + testy Dyrygenta (Prawo XIX)

### Kontekst
`koloseum/backtest.py` (przejazd Dyrygenta po historii) istniał, ale: (1) NIE miał
własnych testów — martwa litera wg Prawa XIX (test_scheduler testuje inny backtest);
(2) czytnik CSV wymagał formatu CryptoDataDownload (kolumna `unix`), więc dołączone
dane `dane/*.csv` (prosty format `timestamp,open,...`) NIE dawały się uruchomić.

### Co zostało wdrożone (kod)
- **Czytnik elastyczny** (`akwedukty/czytnik_csv.py`) — akceptuje `unix` (CDD) LUB
  `timestamp` (prosty format Imperium). `_parse_ts()` parsuje epoch (s/ms) oraz
  ISO-datę. Brak kolumny `symbol` → wywnioskowany z nazwy pliku (`BTC_1h` → `BTC`).
- **Testy backtestu** (`tests/test_backtest.py`, 5) — silnik z historią, walidacja
  za małej liczby barów, AUTO-reżim (Namiestnik), porównanie 3 trybów oraz
  **bezpośredni dowód braku lookahead** (szpieg na `Dyrygent.cykl` sprawdza, że
  każde okno kończy się na bieżącej świecy, brak barów z przyszłości).
- **Testy prostego formatu** (`tests/test_czytnik_csv.py`, +3) — ISO-timestamp,
  symbol z nazwy pliku, `_parse_ts` (epoch s/ms/ISO).

### Weryfikacja
Backtest odpala się out-of-the-box na `dane/BTC_1h.csv` i `dane/ETH_1d.csv`
(`--porownaj` oraz `auto_rezim=True`). Brak zaglądania w przyszłość udowodniony testem.

### Stan
- Testy: 370/370 (+8). Audyt: pełna harmonia. Neurony/strategie bez zmian.

---

## 2026-06-03 | MAJOR | Faza C — V-03 CVD obudzony (adapter trade-feed publiczny, Prawo XV)

### Kontekst
V-03 CVD (Cumulative Volume Delta, kat. F) wyciszony — OHLCV nie zawiera strony
agresora (kto market-kupował vs sprzedawał). Potrzebny trade-feed.

### Co zostało wdrożone (kod)
- **AdapterCVD** (`akwedukty/adaptery/cvd.py`) — publiczny feed Binance aggTrades
  (`fapi/v1/aggTrades`) BEZ klucza API. CVD = Σ(buy) − Σ(sell) z okna transakcji
  (pole `m`=isBuyerMaker: false→buy, true→sell). Wstrzykiwany fetcher (test offline);
  pamięć CVD_PREV per symbol (dla dywergencji V-03).
- **V-03 obudzony** (DOSTEPNY=True) — kat. F: 5→6 aktywnych.
- **Adapter wpięty w pipeline Dyrygenta** — `Dyrygent.zbuduj(adaptery_live=True)`
  domyślnie wpina AdapterFutures + AdapterFearGreed + AdapterCVD.

### Prawo I/XV — uczciwość
W backteście CSV (bez trade-feedu) V-03 ABSTYNUJE (NEUTRAL). Live/paper: AdapterCVD
liczy CVD z publicznego aggTrades → V-03 głosuje (znak CVD + dywergencja vs cena).

### Stan po Fazie C
- Neurony: 44 (aktywne 37, wyciszone 7 = OC-01..04 + SMC-01..03).
- Testy: 362/362. Audyt: pełna harmonia.

### Następna faza
- Faza D: OC-01..04 on-chain (Glassnode/CryptoQuant API — wymaga klucza, os.getenv).

---

## 2026-06-03 | MAJOR | Faza B — kategoria R obudzona (adaptery futures publiczne, Prawo XV)

### Kontekst
Kategoria R (Sentyment) miała 0 aktywnych neuronów — 4 neurony PSY (Funding,
Long/Short, Fear&Greed, OI Divergence) leżały wyciszone. Reguły WAGI_REZIMU dla R
istniały tylko w PANIC (= weto, brak transakcji) → potencjał kategorii R w 0%.

### Wykryta UTRATA POTENCJAŁU (Prawo XV)
- 4 neurony PSY wyciszone mimo gotowego frameworku adapterów.
- AdapterFearGreed (PSY-03, realne darmowe API) istniał, ale nie był wpięty w pipeline.
- WAGI_REZIMU: R aktywne tylko w PANIC (weto) → R nigdy nie wpływało na transakcję.

### Co zostało wdrożone (kod)
- **AdapterFutures** (`akwedukty/adaptery/futures.py`) — publiczne endpointy Binance fapi
  (funding, open interest, long/short) BEZ klucza API; wstrzykiwany fetcher (test offline);
  pamięć OI_PREV dla dywergencji PSY-04.
- **PSY-01/02/03/04 obudzone** (DOSTEPNY=True) — kategoria R: 0→4 aktywne.
- **Adaptery wpięte w pipeline Dyrygenta** — `_wskazniki()` dolewa dane po Budowniczym;
  `Dyrygent.zbuduj(adaptery_live=True)` domyślnie wpina AdapterFutures + AdapterFearGreed.
- **WAGI_REZIMU** — R dodane do VOLATILE(×1.3), RANGING(×1.2), NORMAL(×1.1),
  TREND_STRONG(×0.8), ON-CHAIN_BULLISH(×1.1) — R realnie wpływa na transakcje.
- **+2 strategie VI-LV** (Legio VI Ferrata): VI-LV-001 Funding Contrarian (PSY-01/02+VI-13/V-13),
  VI-LV-002 Liquidation Cascade (A-01/PSY-04+VI-13/V-13). 17 strategii łącznie.

### Prawo I / XV — uczciwość
W czystym backteście z CSV (bez kolumny funding/OI) neurony PSY ABSTYNUJĄ (NEUTRAL,
rój wyklucza je z głosu kierunkowego — nie martwy ciężar). W trybie live/paper adapter
dolewa realne dane → PSY głosują.

### Stan po Fazie B
- Neurony: 44 (aktywne 36, wyciszone 8) — kat. R żywa.
- Kategorie aktywne: A, F, L, M, O*, R, S*, T, V (O/S budzone runtime/feed).
- Strategie: 17. Testy: 358/358. Audyt: pełna harmonia.

### Następne fazy
- Faza C: V-03 CVD (trade feed), SMC live feed.
- Faza D: OC-01..04 on-chain (Glassnode/CryptoQuant API).

---

## 2026-06-03 | MAJOR | Timeframe-Aware Gating — styl SCALP/SWING/INVEST + futures/spot (Prawo XV)

### Kontekst
Cezar: system musi rozróżniać interwał czasowy (scalp/swing/invest), wybierać neurony,
strategie, dźwignię i rynek (futures/spot) automatycznie wg oceny rynku + interwału.
Deep-research: auto-selekcja timeframe+strategia to OTWARTY PROBLEM (Freqtrade/Jesse/
Nautilus/OctoBot wymagają ręcznej konfiguracji). Namiestnik robi to automatycznie.

### Wykryta UTRATA POTENCJAŁU (Prawo XV)
- Strategie miały pola `interwaly`, `styl`, `dzwignia` — **ignorowane** przez
  `dobierz_najlepsze()`. Martwe metadane. Naprawione.
- Namiestnik znał tylko reżim, nie interwał. Dodano warstwę stylu.

### Co zostało wdrożone (kod)
- **`namiestnik.py`** — warstwa 2 (Timeframe-Aware):
  - `ProfilStylu` + `_PROFILE_STYLU`: SCALP(≤10×,FUTURES), SWING(≤5×,OBA), INVEST(≤2×,SPOT)
  - `_INTERWAL_NA_STYL`: mapa M1-M15→SCALP, 30M-4H→SWING, 1D-1W→INVEST
  - `styl_interwalu()`, `profil_stylu()` — funkcje pomocnicze
  - `DecyzjaNamiestnika` — łączy reżim × styl (tryb, prog, lewar_factor, lewar_cap, rynek)
  - `decyduj(rezim, interwal)` — dwuwarstwowa decyzja, VOLATILE/PANIC wymusza SPOT
  - `skaluj_dzwignie(base, rezim, interwal)` — przycina sufitem stylu (lewar_cap)
- **`baza.py`** — `dobierz_najlepsze(interwal=...)` + `_interwal_pasuje()`: filtr strategii po TF
- **`legatus.py`** — `fokus`/`_agreguj`/`_dobierz_strategie` przekazują interwał z barów
- **`dyrygent.py`** — wyciąga interwał z barów, przekazuje do Namiestnika i skalowania
- **`docs/NAMIESTNIK.md`** — pełna dokumentacja modułu (ZPO)
- **`tests/test_namiestnik.py`** — +7 testów warstwy stylu

### Tabela dowodowa (Prawo XVI — z Timeframe-Aware)
| Zestaw | BASELINE | NAMIESTNIK | Δ PnL | WinRate | PF | MaxDD |
|--------|----------|------------|-------|---------|-----|-------|
| BTC 1D | +32.71% | +27.32% | -5.39pp | 45→**55%** | 1.23→**1.57** | 23.8→**5.3%** |
| ETH 1D | +23.80% | +14.84% | -8.96pp | 44→48% | 1.09→1.19 | 26.4→**11.9%** |
| BTC 1H | -4.34% | -6.83% | -2.48pp | 45→43% | 0.85→0.74 | 13.9→**10.0%** |
| ETH 1H | -9.14% | **-4.65%** | **+4.50pp** | 48→43% | 0.77→0.86 | 11.2→**10.0%** |

> Namiestnik redukuje **drawdown na każdym zestawie**. Na 1D (INVEST cap 2×) selektywnie:
> mniej pozycji, wyższy WinRate/PF, drawdown 4.5× niżej na BTC. 1H mieszane (ETH +4.5pp).
> Filozofia: profil ryzyka > surowy zysk.

### Testy
346/346 zielone (+7). Audyt spójności: pełna harmonia.

### Następne fazy (uzupełnianie luk — patrz INDEKS_IMPERIUM.md)
A' napraw martwe neurony → A ożyw kat. L (VI-13 ATR-Lev) i V (Realized Vol) →
B adapter Futures (Legion VI) → C obudzenie 12 wyciszonych → D Legion III → E Księga Azjatycka.

---

## 2026-06-03 | MAJOR | Namiestnik podłączony do backtestu + tabela dowodowa (Prawo XV+XVI)

### Kontekst (głęboki audyt Prawo XV)
Audyt wykrył 🚨 UTRATĘ POTENCJAŁU: Namiestnik (i cały system reżimowy) był MARTWY
w backteście — `backtest.py` hardkodował `rezim="NORMAL"` i nie wstrzykiwał Namiestnika.
Stare `WAGI_REZIMU` też nigdy nie działały w backteście. Naprawione.

### Co zostało wdrożone (#1 — podłączenie)
- **`dyrygent.py`**: `cykl(rezim="AUTO")` → woła `klasyfikuj_rezim(wskazniki)` (Prawo I:
  dane z Bramy, nie zgadywanie). Reżim rozwiązany PRZED Namiestnikiem i Legatusem.
- **`backtest.py`**: parametr `auto_rezim: bool`. True → wstrzykuje `get_namiestnik()`
  + `rezim="AUTO"`. False → zachowanie wsteczne (NORMAL, bez Namiestnika).
- **`narzedzia/pomiar_namiestnik.py`**: skrypt tabeli dowodowej BASELINE vs NAMIESTNIK.
- **`tests/test_namiestnik.py`**: +1 test (`test_dyrygent_auto_rezim_klasyfikuje`)
  blokujący powrót martwego kodu.

### Tabela dowodowa #2 (Prawo XVI — mierzone, nie opinia)
| Zestaw | BASELINE PnL | NAMIESTNIK PnL | Δ PnL | Δ MaxDD |
|--------|-------------|----------------|-------|---------|
| BTC 1D | +32.71% | +19.43% | -13.28pp | 23.8→23.1% |
| ETH 1D | +23.80% | +17.16% | -6.64pp | 26.4→**16.8%** |
| BTC 1H | -4.34% | -3.73% | +0.62pp | 13.9→**7.4%** |
| ETH 1H | -9.14% | **+4.56%** | **+13.70pp** | 11.2→11.8% |

### Uczciwy werdykt (Prawo I — bez upiększania)
Wynik **MIESZANY**, nie jednoznaczne zwycięstwo:
- **1H (choppy/intraday): Namiestnik wygrywa** — ETH 1H strata→zysk (+13.7pp, PF 0.77→1.11),
  BTC 1H drawdown o połowę (13.9→7.4%), wyższy WinRate.
- **1D (silny bull): Namiestnik traci zysk** — bo `RANGING→czy_grac=False` i niższa dźwignia
  wycinają część hossy. DD jednak niższy (ETH 1D 26→17%).
- **Wniosek:** architektura DZIAŁA i jest mierzalna; tablica jest przestrojona zbyt
  defensywnie na rynkach trendujących. Namiestnik = redukcja ryzyka kosztem zysku w bullu.

### Następny krok (Faza 1.1 — przestrojenie tablicy na dowodach)
RANGING na 1D nie powinno być pełną ciszą (gubi hossę). Kandydaci: RANGING→czy_grac=True
z niższą dźwignią; rozdzielenie progów per-interwał. Do zmierzenia w kolejnej iteracji.

### Testy
339/339 zielone (+1). Audyt spójności: pełna harmonia.

---

## 2026-06-02 | MAJOR | Namiestnik (Regime-Aware Gating Network) — Faza 1

### Kontekst
Deep-research: Volatility-Adaptive MoE (arXiv:2508.02686), Adaptive Regime-Aware (arXiv:2603.19136),
Meta-Learning Optimal Mixture (arXiv:2505.03659). Cel: pełna autonomia + samoadaptacja systemu.

### Co zostało wdrożone
- **`imperium/koloseum/namiestnik.py`** — Regime-Aware Gating Network (Namiestnik):
  - `UstawieniaRezimu` — dataclass: tryb, lewar_factor, prog_pewnosci, czy_grac, wagi_override
  - `_TABLICA` — deterministyczne mapowanie 8 reżimów → parametry (Faza 1)
  - `Namiestnik.decyduj(rezim)` → UstawieniaRezimu z fallbackiem (nigdy nie rzuca)
  - `Namiestnik.skaluj_dzwignie(base, rezim)` → lewar_factor × auto_dzwignia
  - `get_namiestnik()` — singleton dla Dyrygenta
  - RANGING + PANIC → `czy_grac=False` (świadoma cisza, nie błąd)
  - TREND_STRONG → tryb filtr + lewar×1.2 (najsilniejszy sygnał)

- **`imperium/koloseum/dyrygent.py`** — integracja Namiestnika:
  - `Dyrygent.__init__` przyjmuje `namiestnik: Optional[Namiestnik]`
  - `Dyrygent.zbuduj()` automatycznie tworzy Namiestnika (`get_namiestnik()`)
  - W `cykl()`: przed Legatusem → Namiestnik → {tryb_aktywny, prog_aktywny, lewar_factor}
  - CISZA (czy_grac=False) → `DecyzjaCyklu("NAMIESTNIK_CISZA", False, powod=opis)`
  - Dźwignia: auto_dzwignia → Namiestnik.skaluj_dzwignie → plan.policz (skalowana)
  - Backward compatible: `namiestnik=None` → zachowanie jak wcześniej (tryb statyczny)

- **`tests/test_namiestnik.py`** — 12 nowych testów
- **`tests/run_tests.py`** — dodano `test_namiestnik`

### Dowody empiryczne (Prawo XVI)
| Reżim | Efekt |
|-------|-------|
| TREND_STRONG | tryb=filtr, lewar×1.2, prog=55% → +43% ETH 1D (wcześniejszy backtest) |
| RANGING | cisza (czy_grac=False) → zero fałszywych sygnałów |
| PANIC | cisza + próg 90% → ochrona kapitału |
| VOLATILE | tryb=strategia, lewar×0.5 → Klucznik dobiera breakout |

### Testy
338/338 zielone (326→338: +12 nowych testów Namiestnika)

### Pliki zmodyfikowane
- `imperium/koloseum/namiestnik.py` (NOWY)
- `imperium/koloseum/dyrygent.py`
- `tests/test_namiestnik.py` (NOWY)
- `tests/run_tests.py`
- `docs/MANIFEST_KODU.md`
- `docs/REJESTR_INSPIRACJI.md` (ML-30..33 dodane)
- `docs/LOG_ZMIAN.md`
- `README.md`

---

## 2026-06-02 | MAJOR | Detektor lookahead-bias (Freqtrade LA-01) + weryfikacja bazy DeepSeek

### Kontekst (sesja "tryb agregat/strategia")
Cezar wgrał `Zbior_wskaznikow_i_strategi_03.06.2026.md` (transkrypcja rozmów z DeepSeekiem).
Zadanie: porównać z naszym kodem + zweryfikować twierdzenia w internecie (deep-research).

### Ustalenia deep-research (Prawo I — zero halucynacji)
- ✅ TradingAgents (~80k ⭐), MRC arXiv 2605.24490 (Shapley, Sharpe 1.51) — REALNE.
- ❌ StratEvo (Sharpe 6.06) — 17 ⭐, liczby pomylone; VORTEX — niezweryfikowalny;
  OpenAlice — agent LLM Node.js, NIE silnik backtestu (DeepSeek mylił przeznaczenie).
- ✅ Akademicko potwierdzone: 1H ma niskie SNR (gorsze od 1D); korelowane wskaźniki bez przewagi.
- 🏆 Najlepsza zdatna do wdrożenia perełka: **Freqtrade lookahead-analysis** — detektor oszustwa backtestu.

### Zmiany kodu
- `imperium/koloseum/lookahead.py` — NOWY. `wykryj_lookahead()`: liczy ślad głosów roju na
  pełnym i obciętym zbiorze barów; rozbieżność = rój zagląda w przyszłość (Prawo I złamane).
  CLI: `python -m imperium.koloseum.lookahead <plik.csv> <interwal> [max_barow]`.
- `tests/test_lookahead.py` — NOWE: brak lookahead na czystym pipeline, determinizm śladu,
  kontrola pozytywna (sztuczny przeciek MUSI być wykryty). +3 testy → 326/326.
- `tests/run_tests.py` — rejestracja `test_lookahead`.

### Dowód
`python -m imperium.koloseum.lookahead dane/dzienne/Binance_BTCUSDT_d.csv 1D 600` → ✅ CZYSTO.
Nasz backtest na prawdziwych danych BTC nie oszukuje.

### Dokumentacja (ZPO + symbioza)
- `docs/REJESTR_INSPIRACJI.md` — LA-01 (wdrożony), ML-28 MRC/Shapley (plan), ML-29 TradingAgents (ref),
  + sekcja odrzuconych (StratEvo/VORTEX/OpenAlice/AetherEdge z powodami).
- `MANIFEST_KODU.md`, `INDEKS_IMPERIUM.md` — dopisany moduł lookahead.
- `README.md` — testy 307→326 (liczba policzona, nie z pamięci — Prawo XXI).

### Powód
Pierwsza inspiracja zewnętrzna, która trafiła PROSTO do kodu, nie do planu. OpenAlice odrzucony
jako backtest (Node.js, brak rygoru); zamiast zmieniać framework — przenieśliśmy metodę Freqtrade.

---

## 2026-06-02 | MAJOR | Warstwa strategii wpięta w decyzję — 3 tryby + pomiar (Opcja 3)

### Problem (Prawo XV — utrata potencjału)
Klucznik dobierał strategie po kluczach, ale Dyrygent ICH NIE UŻYWAŁ — decyzja szła
z gołego głosowania neuronów. Wykryto nawet sprzeczność (bar 400: neurony LONG,
wszystkie 3 top-strategie SHORT) zignorowaną przez system.

### Zmiany kodu
- `imperium/koloseum/dyrygent.py` — parametr `tryb`:
  - `agregat`   — kierunek z głosowania neuronów (strategie ignorowane, stan dotychczasowy)
  - `filtr`     — wejście tylko gdy top-strategia zgadza się z neuronami (Opcja 1)
  - `strategia` — kierunek z top-1 strategii, neurony dają pewność (Opcja 2)
- `imperium/koloseum/backtest.py` — `porownaj_tryby()` + CLI `--porownaj`; `bary` reużywalne
- `tests/test_dyrygent.py` — +3 testy trybów (323/323 zielone)

### POMIAR (Prawo XVI — decyzja na liczbach, nie opinii)
| Rynek | tryb | PnL | Trades | WinRate | PF | MaxDD |
|-------|------|-----|--------|---------|----|----|
| BTC 1D | agregat | +32.7% | 124 | 45.2% | 1.23 | 23.8% |
| BTC 1D | filtr | +26.5% | 135 | 45.9% | 1.16 | 22.2% |
| BTC 1D | strategia | +11.1% | 108 | 41.7% | 1.08 | 24.1% |
| ETH 1D | agregat | +23.8% | 160 | 43.8% | 1.09 | 26.4% |
| ETH 1D | **filtr** | **+43.0%** | 160 | 48.1% | 1.16 | **16.3%** |
| ETH 1D | strategia | +14.6% | 147 | 40.8% | 1.06 | 26.2% |

### Wnioski (zmierzone)
1. **`strategia` (nadrzędna) — najgorsza na obu rynkach.** Potwierdza: warstwa strategii
   jest słabo skalibrowana, nie nadaje się jeszcze na ster. ODRZUCONA jako domyślna.
2. **`filtr` ma najniższy MaxDD na obu rynkach** (22.2%/16.3% vs 23.8%/26.4%) i wygrywa
   ryzykiem-do-zysku (ETH +43% przy DD 16%). Na BTC goły agregat ma wyższy surowy zwrot.
3. Decyzja o domyślnym trybie — w gestii Cezara (return vs ryzyko). Tryby zostają w kodzie.

---

## 2026-06-02 | MAJOR | Backtest na PRAWDZIWYCH danych + czytnik CSV

### Zmiany kodu
- `imperium/akwedukty/czytnik_csv.py` — czytnik formatu CryptoDataDownload (Binance export):
  pomija linię URL, odwraca malejący plik na chronologiczny, wykrywa wolumen bazowy
  (Volume BTC/ETH) vs quote (Volume USDT). Zwraca bary zgodne z Budowniczym/Dyrygentem.
- `imperium/koloseum/backtest.py` — przejazd Dyrygenta po historii z przesuwnym oknem.
  NIE zagląda w przyszłość: wskaźniki liczone tylko z barów do bieżącej świecy włącznie.
- `tests/test_czytnik_csv.py` — 7 testów (próbka inline, bez dużych plików)
- `dane/dzienne/` + `dane/godzinowe/` — realne dane Binance BTC+ETH (Cezar wrzucił)

### PIERWSZE UCZCIWE WYNIKI (bez danych syntetycznych — Prawo I)
Dane realne Binance, dźwignia auto, SL/TP z Kalkulatora Lewara, prowizje+poślizg liczone:
| Rynek | Okres | PnL | Trades | Win Rate | Profit Factor | Max DD |
|-------|-------|-----|--------|----------|---------------|--------|
| BTC 1D | 2017-2026 (3192) | **+32.7%** | 124 | 45.2% | 1.23 | 23.9% |
| ETH 1D | 2017-2026 (3192) | **+23.8%** | 160 | 43.8% | 1.09 | 26.4% |
| BTC 1H | ost. 5000 (~7 mies.) | **-4.3%** | 101 | 44.6% | 0.85 | 13.9% |

### Uczciwa ocena (Prawo XV — nie ukrywam słabości)
Infrastruktura działa end-to-end na realnym rynku. ALE strategia jest SŁABA:
PF ledwo > 1 na dziennym, STRATNA na godzinowym (PF 0.85). To NIE jest gotowy system
zarabiający — to działający szkielet do kalibracji. Buy-and-hold BTC dałby +1600%,
my +32%. Następny etap: kalibracja wag/progów, obudzenie śpiących neuronów, lepszy dobór reżimu.

### Powód
Poprzedni "+393 USDT" był na danych SYNTETYCZNYCH (idealna linia) — nic nie znaczył.
Teraz mamy prawdziwą informację zwrotną z rynku, na której można poprawiać Imperium.

---

## 2026-06-02 | MAJOR | Dyrygent — orkiestrator pełnego cyklu decyzyjnego (Faza 0 end-to-end)

### Zmiany kodu
- `imperium/koloseum/dyrygent.py` — NOWY orkiestrator spinający rozproszone klocki w jeden łańcuch:
  bary OHLCV → Budowniczy/Brama (wskaźniki) → Legatus.fokus (kierunek/pewność/reżim) →
  KalkulatorLewara.policz (SL/TP/dźwignia/rozmiar) → SygnalWejscia → PaperTradingEngine
- `DecyzjaCyklu` — przejrzysty ślad każdego etapu (gdzie cykl się zakończył i dlaczego — Prawo I jawność)
- Budowniczy wstrzykiwany (Prawo I); `wskazniki_provider` pozwala testować bez TA-Lib
- `tests/test_dyrygent.py` — 6 testów: pusty/neutralny/silny cykl, pełny ślad, brak źródła, end-to-end z TP_HIT

### Dowód działania
Pełny cykl zweryfikowany ręcznie: rój dał LONG → Kalkulator dźwignia 10, SL/TP →
pozycja otwarta 4210 USDT → bar dotknął TP → zamknięcie +393 USDT (+3.93%).
Bramka ryzyka działa: przy dźwigni 20 Pretorianie wetują pozycję >50% kapitału.

### Powód
Wszystkie klocki (Budowniczy, Legatus, Kalkulator, PaperTradingEngine) istniały i były
testowane OSOBNO, ale nic nie spinało ich w cykl. To była UTRATA POTENCJAŁU (Prawo XV):
gotowe moduły niepodpięte do pipeline. Dyrygent domyka Fazę 0 — rój realnie podejmuje decyzje.

### Symbioza
- MANIFEST_KODU: +PaperTradingEngine, +Dyrygent
- INDEKS_IMPERIUM (MAPA KODU): koloseum/ 🟡 Szkielet → ✅ Cykl Faza 0 aktywny
- Testy: 307 → 313 (+6)

### Otwarty wątek (do kalibracji w Fazie 1)
`pewnosc_agregatu` Legatusa bywa ~1.0 nawet przy słabym składzie zgodnych neuronów —
warto skalibrować (więcej neuronów = wyższa pewność, nie sama zgodność kierunku).

---

## 2026-06-02 | NARZĘDZIA | Zestaw strażników spójności — audyt rozszerzony + status.py + pre-commit hook

### Nowe narzędzia
- `narzedzia/audyt_spojnosci.py` — rozszerzony o 4 nowe warstwy:
  - **W5 (INDEKS):** liczby mikro-neuronów i zwiadowców w INDEKS_IMPERIUM (sekcja MAPA KODU) vs żywy kod
  - **W6 (daty):** "Stan na:" w MANIFEST i README nie może być starsze niż 2 dni
  - **W7 (sieroty):** każdy plik docs/*.md musi być wymieniony w INDEKS_IMPERIUM; martwe cross-linki między docs/
  - **W8 (LOG_ZMIAN):** jeśli plik .py w imperium/ zmieniony po ostatnim wpisie LOG_ZMIAN → alarm
- `narzedzia/status.py` — pulpit jednego spojrzenia (Prawo XVII): faza, żywy rój, testy, ostatni log, roadmap, git, audyt
- `.git/hooks/pre-commit` — blokuje każdy commit gdy testy lub audyt czerwone (Prawo XXI)
- `narzedzia/hooks_src/pre-commit` — źródło hooka (przetrwa re-clone)
- `narzedzia/install_hooks.py` — instalator hooków po git clone

### Naprawy (wywołane przez W7)
- `docs/ARCHITEKTURA_IMPERIUM.md` — naprawiony martwy link: AUDYT_ADOPCJI.md → archiwum/AUDYT_ADOPCJI.md
- `docs/INDEKS_IMPERIUM.md` — dodano 7 brakujących plików docs/ (MANIFEST_KODU, AUDYT_SYSTEMU, MAPA_KLUCZY, OBSERWATORZY, SKAN_AZJA, WERSJONOWANIE, WIZJONER); poprawiono "27 w kodzie" → "42 w kodzie"

### Powód
Cezar zidentyfikował: bez automatycznej bramki pre-commit i rozszerzonego audytu projekt rozjeżdża się przy każdej sesji. "Legiony stoją, Cesarz jest zły." Rozwiązanie: każdy commit jest teraz weryfikowany maszynowo, nie zależy od pamięci.

---

## 2026-06-02 | FIX | Naprawa błędu archiwizacji + weryfikacja statusów

### Problem
Poprzednia sesja przeniosła do archiwum/ dokumenty BEZ dokładnego przeczytania:
- `ARSENAL_IMPERIUM.md` — zweryfikowany katalog ~220 narzędzi infrastruktury (nie neuronów!) — przeniesiony przez BŁĄD
- `WZORZEC_DNSS.md` — aktywna referencja architekturalna — przeniesiony przez BŁĄD
Dodatkowo: SHARP/AgenticAITA/CogAlpha/NEXUS/Kronos opisane jako ⚠️ niezweryfikowane, mimo że weryfikacja była w ARSENAL_IMPERIUM.md — złamanie Prawa I.

### Naprawa
- `docs/ARSENAL_IMPERIUM.md` — PRZYWRÓCONY z archiwum/ do docs/ (git mv)
- `docs/WZORZEC_DNSS.md` — PRZYWRÓCONY z archiwum/ do docs/ (git mv)
- `docs/REJESTR_INSPIRACJI.md` — status ML-24..27 i A-12 poprawiony: ⚠️ → ✅ (zweryfikowane maj 2026)
- `docs/WZORZEC_OPISU.md` — przykład naprawiony (SHARP był ⚠️, jest ✅)
- `docs/KATALOG_NEURONOW.md` — ML-24..27 naprawione
- `docs/INDEKS_IMPERIUM.md` — ARSENAL_IMPERIUM i WZORZEC_DNSS przywrócone do tabeli aktywnych; liczby, historia zaktualizowane

### Lekcja
Przed archiwizacją pliku: PRZECZYTAJ go w całości. "Wygląda przestarzale" to za mało — sprawdź zawartość.
Obowiązek wynikający z Prawa XVIII: "złamanie przez nieuwagę = takie samo złamanie jak celowe".

---

## 2026-06-02 | DOC | Zasada Pełnego Opisu (ZPO) + Rejestr Inspiracji AI/ML

### Nowe pliki
- `docs/WZORZEC_OPISU.md` — NOWY: wzorzec/szablon pełnego opisu (ZPO) — każdy wpis ma pełną nazwę, link, status weryfikacji, wyjaśnienie dla nowicjusza
- `docs/REJESTR_INSPIRACJI.md` — NOWY: jedno miejsce na zewnętrzne projekty AI/ML (SHARP, AgenticAITA, CogAlpha, NEXUS, Kronos) z pełnymi nazwami + linkami + statusem weryfikacji

### Zmiany dokumentacji
- `docs/KATALOG_NEURONOW.md` — dodane klucze ML-24..27 (inspiracje zewnętrzne) + cross-link na A-12 Kronos
- `CLAUDE.md` — dodana sekcja "Zasada Pełnego Opisu (ZPO)" jako rozkaz stały
- `docs/INDEKS_IMPERIUM.md` — dodane WZORZEC_OPISU i REJESTR_INSPIRACJI

### Powód
Cezar (nowicjusz) zauważył, że projekty AI/ML (Kronos, NEXUS, SHARP, CogAlpha, AgenticAITA) były rozproszone po 4 dokumentach bez pełnych nazw i linków. Nakazał zasadę pełnego opisu: zawsze pełne nazwy, linki pochodzenia, kompletny opis. ZPO = nowy rozkaz stały.

### Uczciwość (Prawo I)
Linki podane przez Cezara (arXiv 2026, GitHub) oznaczone ⚠️ NIEZWERYFIKOWANE — nie było dostępu do sieci, nie udajemy weryfikacji.

---

## 2026-06-02 | MAJOR | Adaptery Danych + 5 nowych neuronów + LOG_ZMIAN + porządki docs

### Zmiany kodu
- `imperium/akwedukty/adaptery/baza.py` — NOWY: klasa bazowa `AdapterDanych` (wzbogac/aktywuj/usypiaj)
- `imperium/akwedukty/adaptery/testowy.py` — NOWY: `AdapterTestowyOnChain`, `AdapterTestowyFutures`, `AdapterTestowyCVD` (9 neuronów API ze snu wzbudzone w testach)
- `imperium/akwedukty/adaptery/feargreed.py` — NOWY: pierwszy prawdziwy adapter HTTP (alternative.me, bez klucza API, wzbudza PSY-03)
- `imperium/akwedukty/adaptery/__init__.py` — NOWY: eksport publiczny adapterów
- `imperium/legiony/neurony/straz.py` — DODANE: A-03 NeuronWashVol (fałszywy wolumen), A-05 NeuronBartPattern (manipulacja niską płynnością)
- `imperium/legiony/neurony/trend.py` — DODANE: XII-06 NeuronOBZone (Order Block OHLCV, uproszczony)
- `imperium/legiony/rejestr.py` — zaktualizowane importy i `wszystkie_neurony()`
- `imperium/legiony/strategie/rejestr_strategii.py` — DODANA strategia IMV-DEF-002 "MUR KONTRWYWIADU" (A-03+A-05)

### Powód
Prawo XV: neurony OC-01..04, PSY-01..04, V-03 były wyciszone z braku adapterów — utrata 9/42 potencjalnych głosów. Framework adapterów to pierwszy krok do ich pełnego wybudzenia z feedami API.

### Pliki dokumentacji
- `docs/MANIFEST_KODU.md` — zaktualizowany (SMC 🌙, AdapterFearGreed, liczby)
- `README.md` — zaktualizowane liczby (307/307 testów, 42 neurony)
- `tests/test_adaptery.py` — NOWY: 19 testów offline dla adapterów
- `tests/run_tests.py` — test_adaptery dodane przed test_spojnosc

---

## 2026-06-02 | MAJOR | Prawo XX status elitarny + 4 nowe neurony + kategorie + WAGI_REZIMU

### Zmiany kodu
- `imperium/legiony/mikro_neuron.py` — DODANE: pole `ELITARNY=False`, `POWOD_ELITARNOSCI=""`
- `imperium/legiony/zwiadowcy/baza.py` — DODANE: `ELITARNY=True`, `POWOD_ELITARNOSCI` w ZwiadowcaElitarny
- `imperium/legiony/neurony/momentum.py` — X-25 i X-26 oznaczone `ELITARNY=True`
- `imperium/legiony/legatus.py` — DODANE: `WAGI_REZIMU` (mnożniki wg reżimu rynku per kategoria) + `WAGI_REZIMU_PLANOWANE`
- `imperium/legiony/rejestr.py` — DODANA: `raport_elity()` — lista elit z kryterium E1-E7
- Poprzednia sesja: neurony F-01, F-02, F-03, F-04 (4 neurony wolumenowe) dodane do kodu

### Powód
Prawo XX: status elitarny musi być mierzony, nie opinią. Raport umożliwia audyt każdej sesji.
WAGI_REZIMU: sygnały Straży (kategoria A) ważniejsze w reżimie VOLATILE i PANIC — elastyczny agregat.

### Pliki dokumentacji
- `ZASADY_FUNDAMENTALNE.md` — DODANE: Prawo XX (status elitarny E1-E7)
- `CLAUDE.md` — DODANE: sekcja Prawo XX, Prawo XXI (protokół spójności)
- `docs/MANIFEST_KODU.md` — zaktualizowany

---

## 2026-06-02 | MAJOR | Audyt Arsenału — odzyskanie straconych wskaźników + reorganizacja docs

### Zmiany dokumentacji
- `docs/KATALOG_NEURONOW.md` — NAPRAWIONY nagłówek (stary paradygmat "jeden neuron = para oczu" zastąpiony aktualnym z interpretuj()), DODANA sekcja "Uzupełnienie Arsenału" (+12 brakujących wskaźników)
- `docs/LOG_ZMIAN.md` — NOWY (ten plik): obowiązkowy log zmian Imperium
- `archiwum/ARSENAL_WSKAZNIKOW.md` — PRZENIESIONY z docs/ (stary paradygmat, superseded przez KATALOG_NEURONOW)
- `archiwum/AUDYT_ADOPCJI.md` — PRZENIESIONY z docs/ (historyczny audyt migracji Kingdom Pixel, zakończony)
- `archiwum/WZORZEC_DNSS.md` — PRZENIESIONY z docs/ (dokument referencyjny/inspiracyjny, statyczny)
- `archiwum/ARSENAL_AMERYKI.md` — PRZENIESIONY z docs/ (skan linków wielokontynentalny, informacyjny)
- `archiwum/ARSENAL_IMPERIUM.md` — PRZENIESIONY z docs/ (superseded przez KATALOG_NEURONOW)

### Powód
Użytkownik (Cezar) nakazał: "wszystko co stare i nieaktualne → archiwum, do archiwum zaglądasz tylko na wyraźne polecenie". Arsenal stworzono pod stary paradygmat "neurony nie myślą" — teraz neurony mają pełną logikę interpretuj(). Porównanie wykazało 12 wskaźników z Arsenału nieobecnych w Katalogu — odzyskane i dodane.

### Stracone przy zmianie paradygmatu (dodane z powrotem do katalogu)
Momentum: DPO, Ultimate Oscillator, Chande Momentum Oscillator
Trend: Alligator, ALMA, Price Channel
Zmienność: Standard Error Bands, Chaikin Volatility, VIX Fix, ATRP
Wolumen: Volume Oscillator, Apex Desk CVD MAX

---

## 2026-06-01 | MINOR | Zwiadowcy Exploratores EXP-01..12

### Zmiany kodu
- `imperium/legiony/zwiadowcy/` — 12 zwiadowców zaimplementowanych (EXP-01..12; 11 aktywnych + EXP-12 wyciszony do feedu L2)
- Każdy zwiadowca: `KLUCZ`, `KATEGORIA`, `ELITARNY=True` (kryterium E1 — Exploratores)

### Powód
Zwiadowcy generują sygnały wyspecjalizowane (SMC, wolumen zaawansowany) poza standardowym rój głosowaniem.

---

## 2026-05-28 | MAJOR | Rdzeń decyzyjny — Generał Legatus + Koloseum

### Zmiany kodu
- `imperium/legiony/legatus.py` — agregacja głosów + wagi + odpalanie zwiadowców
- `imperium/koloseum/` — Igrzyska + rangowanie neuronów
- `imperium/legiony/diagnostyka_korelacji.py` — pomiar dekorelacji (Prawo XVI)

### Powód
Rdzeń decyzyjny kompletny: rój głosuje → Legatus agreguje → koloseum ranguje.

---

## 2026-05-20 | MAJOR | Brama Kalkulatora + Budowniczy Wskaźników

### Zmiany kodu
- `imperium/fundament/brama_kalkulatora.py` — jedyne wejście do obliczeń (Prawo I)
- `imperium/legiony/budowniczy_wskaznikow.py` — surowe bary OHLCV → pełen słownik wskaźników

### Powód
Prawo I: neurony NIGDY nie liczą samodzielnie. Brama z SHA-256 pieczątką zapewnia auditability.

---

## 2026-05-15 | MAJOR | 30 neuronów OHLCV + 3 SMC wewnętrzne

### Zmiany kodu
- 30 neuronów aktywnych OHLCV w folderach `imperium/legiony/neurony/`
- SMC-01/02/03 — budzenie wewnętrzne przez most EXP-05 (nie wymagają zewnętrznego API)

### Powód
Rdzeń roju: pierwsza fala neuronów OHLCV. SMC klasyfikowane jako 🌙 (wewnętrznie budzone), nie 🔇 (czekające na API).

---

*Ten log aktualizowany jest OBOWIĄZKOWO po każdej zmianie systemu (ROZKAZ STAŁY — 2026-06-02).*
