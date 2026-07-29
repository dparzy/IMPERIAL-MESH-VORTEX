---
kategoria: CONSILIUM
typ: zywy
wlasciciel: imperium/oczy/censor_sprzetu.py
stan_na: 2026-07-29
powod_istnienia: "Projekt organu INGENIUM — mierzalny wskaźnik rozwoju Imperium (IQ IMPERII): 7 kategorii liczonych z kodu i ledgerów, nie z deklaracji. Zamiar Cezara z 2026-07-29, nie fakt — kod jeszcze nie istnieje"
---

# 🧠 INGENIUM — CENZOR ROZUMU IMPERIUM (projekt organu)

> **Status: ZAMIAR, nie kod.** Ten dokument jest planem (kategoria CONSILIUM). Dopóki nie
> powstanie 🔴 `imperium/oczy/ingenium.py` (plan) z testami, **Imperium nie ma miernika IQ**
> — i żadna liczba stąd nie ma prawa pojawić się w raportach jako fakt (Prawo XIX).
> Bramka W16 wyłapała ten cytat już przy pierwszym zapisie dokumentu i słusznie: ścieżka
> do nieistniejącego modułu musi być **jawnie** oznaczona jako plan, inaczej po tygodniu
> nikt nie odróżni zamiaru od faktu.

**Myśl Cezara (2026-07-29, verbatim co do sensu):** *stworzyć inteligencję naszego rozwoju —
organ żywy, który analizuje i monitoruje postęp wg ściśle określonych kategorii, ocenia
współpracę organów, mierzy jak szybko się uczymy, co wiemy dziś a co wiedzieliśmy wczoraj,
jak to wpłynęło na decyzje, czy organizm jest zdrowy, czy mamy systemy obronne, czy giełda
nas pokona, czy w pełni wykorzystujemy możliwości, czy testujemy wg najlepszych standardów,
czy znamy procedury i regulaminy rynku — i porównuje nas z konkurencją, dając parcie do
podniesienia IQ.*

**Nazwa rzymska (ZASADA NOMENKLATURY):** *ingenium* = wrodzona zdolność umysłu, bystrość.
Organ nazywa się **INGENIUM**, a jego wynik **IQ IMPERII**. Imię jest dobrane do funkcji:
rzymski **cenzor** nie chwalił obywateli — **przydzielał ich do klas na podstawie spisu
majątku**. Tak samo ten organ: nie ocenia, ile Imperium *chce* znaczyć, tylko ile **da się
policzyć**.

---

## 1. Czym jest „inteligencja" dla Imperium (definicja operacyjna)

Nie „ile wiemy", tylko **jak szybko zamieniamy doświadczenie w lepszą decyzję**. Rozbicie
na cztery mierzalne własności — każda musi mieć źródło w kodzie albo ledgerze:

| Własność | Pytanie kontrolne | Gdzie już mamy dane |
|---|---|---|
| **Tempo uczenia** | co wiemy dziś, czego nie wiedzieliśmy wczoraj? | W1 (SYGNAŁ+TRADE_CLOSE), wagi MWU, lekcje W3 |
| **Wpływ na decyzję** | czy ta wiedza **zmieniła** wybór, czy tylko przybyła? | mnożniki Legatusa, weta Pretorianów, A/B w CODEX |
| **Uczciwość korekty** | czy potrafimy obalić własne twierdzenie? | INDEX FALSORUM, Księga Wad, LEX TALIONIS |
| **Sprzężenie organów** | czy organy **współpracują**, czy tylko istnieją? | cenzus adapterów, Prawo XV (moduł bez czytelnika) |

---

## 2. Siedem kategorii oceny (każda 0–100 albo `NIEZNANE`)

> **Reguła nadrzędna:** brak danych daje `NIEZNANE`, **nigdy 0 i nigdy oszacowanie**.
> Zero znaczy „zmierzono i wyszło źle"; nieznane znaczy „nie mamy prawa mówić".

### I. DISCIPLINA — tempo uczenia
Przyrost wpisów W1 z atrybucją, liczba neuronów z policzonym IC, zmiana wag MWU między
wachtami, nowe lekcje W3, liczba obalonych własnych twierdzeń (INDEX FALSORUM).
*Podkategorie:* przyswajanie · retencja (czy lekcja przeżyła 30 dni) · korekta.

### II. SALUS — zdrowie organizmu
Testy zielone/czerwone, audyt exit, dług gnicia dokumentów, dług honorowy, **martwe głosy**
(neuron zawsze NEUTRAL), moduły bez czytelnika, świeżość danych per interwał.
*Podkategorie:* wydolność · gnicie · martwe organy.

### III. PRAESIDIUM — odporność i obrona
Liczba warstw bramki i **ile z nich zweryfikowano mutacją** (dziś: 8 prób, 7 skutecznych),
pokrycie zdarzeń hooka (dziś **4 z 31**), weta Pretorianów na 100 wejść, breaker krzywej,
zachowanie przy zerwanym łączu i przy brudnych danych.
*Podkategorie:* bramki · odporność na dane · odporność na awarię.

### IV. PERITIA — biegłość rynkowa (czy giełda nas pokona)
IC per neuron × reżim × interwał, hit rate, P&L **OOS**, DSR, PBO, walk-forward efficiency,
MAE/MFE, zachowanie w reżimach (TREND/RANGE/VOLATILE), wynik vs buy&hold.
*Podkategorie:* skill · stabilność · przetrwanie w złym reżimie.

### V. DILIGENTIA — procedury i standardy
Czy checklista istnieje **i czy była wykonana** (sigla: apertio/clausura/limes), pokrycie
runbookami, ile procedur ma test, ile wyników trafia do CODEX, zgodność z regulaminami
giełdy (limity, tick size, funding, ograniczenia API).
*Podkategorie:* kompletność procedur · egzekwowanie · zgodność z rynkiem.

### VI. COMMUNIO — współpraca organów ⭐
**Sedno myśli Cezara: Imperium nie jest sumą organów, tylko ich sprzężeniem.** Miary:
odsetek modułów faktycznie wpiętych w pipeline (cenzus adapterów), liczba par organ→organ
z realnym przepływem danych, **redundancja mierzona** (Prawo XVI: |korelacja| > 0,80 =
dublet, < 0,20 = filar), liczba ogniw łańcucha, które milczą.
*Podkategorie:* wpięcie · przepływ · nieredundantność.

### VII. AEMULATIO — miejsce wobec konkurencji
Porównanie z Freqtrade / Hummingbot / Jesse wyłącznie po **weryfikowalnych** osiach:
lata live, wolumen, liczba giełd, pokrycie testami, obecność DSR/PBO/purged-CV/meta-labelingu,
warstwy pamięci. **Uczciwie w obie strony:** dziś przegrywamy na track recordzie live
(oni lata, my zero realnych orderów), wygrywamy na warstwie walidacji i pamięci.

---

## 3. Zasady nienaruszalne tego organu (inaczej stanie się laurką)

1. **Każda składowa liczona z KODU albo LEDGERA.** Zero liczb wpisanych ręcznie —
   ta sama choroba, którą leczyły Warstwy 15/17/20/23.
2. **`NIEZNANE` to wynik.** Kategoria bez pomiaru nie dostaje punktów „z rozsądku".
3. **Mierzymy DELTĘ, nie tylko stan.** „IQ 137" bez historii jest fikcją; wartość ma
   *o ile urosło i po czym*. Organ zapisuje własną historię i pokazuje trend.
4. **PRAWO GOODHARTA — najważniejsze ograniczenie.** Gdy miernik staje się celem, przestaje
   być miarą. Dlatego **IQ IMPERII nigdy nie steruje decyzją automatycznie** — nie wolno mu
   wpiąć się w ścieżkę wejścia/wyjścia z pozycji ani w dobór wag. Jest **lustrem, nie
   kierownicą**. Podnoszenie wyniku wolno robić wyłącznie przez naprawę tego, co wynik mierzy.
5. **Antywskaźnik obowiązkowy.** Każda kategoria musi mieć zapisane, **jak można ją oszukać**
   (np. DISCIPLINA rośnie od samego dopisywania lekcji — więc liczy się lekcja, która
   **zmieniła decyzję**, nie lekcja zapisana).
6. **Wynik ma być spadalny.** Miernik, który nigdy nie spada, nie mierzy — chwali.

---

## 4. Co da się policzyć OD RAZU, a co wymaga budowy (stan 2026-07-29)

| Kategoria | Gotowe źródło | Czego brakuje |
|---|---|---|
| DISCIPLINA | W1 (46 wpisów), wagi MWU (37), INDEX FALSORUM (8) | historii między wachtami — potrzebny zapis migawek |
| SALUS | testy 3082, audyt 23 warstwy, LEX TALIONIS, PORTITOR | miary „martwych głosów" per neuron na żywych danych |
| PRAESIDIUM | bramka + wynik mutacji, hooki 4/31 | regularnego, nie doraźnego testu mutacyjnego |
| PERITIA | backtest, DSR/PBO/WFO, CODEX (11 A/B, 4 IC) | wyników OOS na wielu parach — to jest krok 3 |
| DILIGENTIA | sigla, runbooki W11, CODEX | pomiaru **wykonania** checklisty, nie jej istnienia |
| COMMUNIO | cenzus adapterów (20/22), diagnostyka korelacji | grafu przepływów organ→organ |
| AEMULATIO | notatki o konkurencji | jednego, wersjonowanego arkusza porównania |

**Wniosek:** ~60% składowych ma już źródło. Organ jest w zasięgu jednej–dwóch wacht,
**pod warunkiem że zacznie od kategorii, które mają dane** (SALUS, PRAESIDIUM, COMMUNIO),
a resztę uczciwie oznaczy jako `NIEZNANE`, aż krok 3 dostarczy pomiarów rynkowych.

---

## 5. Kolejność budowy (rekomendacja Architekta)

1. **Szkielet + 3 kategorie z danymi** (SALUS, PRAESIDIUM, COMMUNIO) + zapis migawki do
   historii → pierwsza DELTA po drugiej wachcie.
2. **PERITIA** — dopiero po kroku 3 obiegu (A/B `ucz_mwu` na wielu parach/oknach).
3. **DISCIPLINA** — gdy będą co najmniej dwie migawki do porównania.
4. **DILIGENTIA + AEMULATIO** — na końcu, bo wymagają decyzji Cezara o standardach
   i o tym, z kim naprawdę się porównujemy.

---

## 6. Stosunek do czterech kroków rozwoju (aktualizacja po decyzji Cezara)

Wcześniejsza rekomendacja Architekta brzmiała: (1) substrat = A/B `ucz_mwu`, (2) esencja
operacyjna per kategoria, (3) pętla auto-poszukiwania, (4) domknięcie RAG. **INGENIUM tych
kroków NIE zastępuje — trzy z nich zostają bez zmian, a jeden się z nim ZLEWA.**

| Krok | Status po dołożeniu INGENIUM |
|---|---|
| **1. Substrat — A/B `ucz_mwu`** | **bez zmian, nadal pierwszy.** INGENIUM bez tego pomiaru ma kategorię PERITIA pustą (`NIEZNANE`) |
| **2. Esencja operacyjna per kategoria** | **ZLEWA SIĘ z INGENIUM.** IC × reżim × interwał, hit rate, MAE/MFE, klastry korelacji to dokładnie surowiec kategorii PERITIA i COMMUNIO — to jedna budowa, nie dwie. Osobny „organ esencji" byłby drugim źródłem prawdy (Prawo XVI) |
| **3. Pętla auto-poszukiwania** | **bez zmian co do treści, z jednym NOWYM ograniczeniem:** pętli nie wolno optymalizować pod IQ. Miernik i poszukiwacz muszą być rozdzielone, inaczej system zacznie hodować własną ocenę zamiast wyniku (Prawo Goodharta, §3.4) |
| **4. Domknięcie RAG (91 książek + wektory)** | **bez zmian.** Karmi hipotezy, nie oceny — biblioteka nie wchodzi do IQ jako punkty za samo posiadanie książek |

**Ryzyko rośnie, nie maleje.** Backtest kosztuje ~25 s, więc automat znajdzie tysiące
„wzorców", z których większość będzie szumem (data dredging). Dołożenie MIERNIKA do
SZYBKIEGO POSZUKIWACZA to klasyczna kombinacja, w której system zaczyna optymalizować
wskaźnik zamiast wyniku. Warunek nienaruszalny pozostaje ten sam: **żaden auto-odkryty
wzorzec nie wchodzi do decyzji bez OOS + DSR/PBO/purged-CV/walk-forward.**

---

## 7. CHARAKTER ORGANU — sędzia, nie chwalca (rozkaz Cezara 2026-07-29)

*„Ma nie pluć tylko realnie i prawdziwie oceniać… musi być jak sędzia, jako obserwator
zewnętrzny, audytor, doradca bezstronny i bezgranicznie czysty, szanujący się uznaniem
i nigdy nie kłamie: rosnę, spadamy, nasze IQ właśnie podskoczyło albo spada, coś jest nie
tak, czas na odpoczynek i regenerację Imperium — szukajmy i wyciągajmy wnioski."*

To nie jest ozdobnik. To **kontrakt organu**, z którego wynikają twarde wymagania:

### 7.1 Cztery werdykty — jawne, krótkie, bez ozdób
`ROŚNIEMY` · `STOIMY` · `SPADAMY` · `ALARM`. Każdy **z podaniem powodu i składowej**, która
się poruszyła. Werdykt bez wskazania „która kategoria i o ile" jest zakazany — to byłaby
opinia, nie pomiar.

### 7.2 Sędzia nie może być stroną
- INGENIUM **nie ocenia własnego istnienia** jako sukcesu: dodanie tego organu nie podnosi
  IQ ani o punkt.
- Nikt nie poprawia wyniku **edytując miernik** — składowe pochodzą z ledgerów i kodu
  ZEWNĘTRZNYCH wobec niego (CODEX, W1, Księga Wad, LEX TALIONIS, audyt, cenzus).
- Zmiana progu albo wagi w INGENIUM musi być **jawna w historii migawek**, inaczej ocena
  „urosła" bez powodu w rzeczywistości. Ta sama choroba co ręcznie wpisana liczba.

### 7.3 Nigdy nie kłamie — czyli proweniencja i prawo do milczenia
- Każda składowa niesie **skąd pochodzi** (plik/ledger + data pomiaru).
- Brak danych → `NIEZNANE`. **Nigdy oszacowanie, nigdy „w przybliżeniu".**
- Gdy własna wcześniejsza ocena okaże się błędna, organ **sam ją obala** i zapisuje
  w INDEX FALSORUM — na tych samych prawach co każde inne twierdzenie Imperium.

### 7.4 QUIES — sygnał regeneracji (nowość od Cezara)
Organ ma **obowiązek** powiedzieć „czas na odpoczynek", gdy widzi objawy przemęczenia
systemu — bo one poprzedzają katastrofę i **są mierzalne**:
- rosnący **dług honorowy** (błędy bez kompensujących unikatów),
- seria czerwonych bramek pod rząd,
- **naprawa rodząca wadę** — zmierzone w tej wachcie: fallback przywrócił błąd, który miał
  usunąć; to najostrzejszy objaw zmęczenia, bo wygląda jak postęp,
- rozrost bez sprzężenia: **SALUS rośnie, a COMMUNIO stoi** (przybywa organów, nie przybywa
  współpracy),
- tempo wad na godzinę pracy wyższe niż tempo ich domykania.

Werdykt `QUIES` nie jest porażką — jest **zaleceniem zatrzymania i wyciągnięcia wniosków**,
zanim koszt urośnie. Organ, który potrafi kazać przerwać, jest wart więcej niż taki, który
tylko dopinguje.

### 7.5 Prawo XV wprost w mierniku
**Utrata potencjału jest pozycją liczoną, nie pytaniem retorycznym**: moduły gotowe, ale
niepodpięte; dane zapłacone, a nieużyte; kolejki czekające na sędziego. Dowody z tej jednej
wachty: tesseract **był** zainstalowany i niewidoczny, `log_sygnal` **istniała** bez ani
jednego wywołania, W1 **umiała** pisać i miała 0 plików, 35 cząstek Hyginusa **czeka**
opłaconych. Każda z tych rzeczy to punkt, który INGENIUM ma odejmować **do czasu wpięcia**.

### 7.6 Szacunek buduje się uznaniem, a uznanie — spadkami
Miernik, który tylko rośnie, jest reklamą. **Wiarygodność INGENIUM mierzymy tym, ile razy
pokazał spadek, który potem okazał się słuszny.** Ta liczba (trafne ostrzeżenia / wszystkie
ostrzeżenia) ma być publikowana razem z wynikiem — organ ocenia też **samego siebie**.

> **Zdanie zamykające, żeby nie zgubić proporcji:** miernik nie czyni Imperium mądrzejszym.
> Czyni je **świadomym tego, gdzie jest głupie** — i to jest cała jego wartość.
