---

## Ostatnia aktualizacja: 2026-07-27
kategoria: TABULA
typ: zywy
wlasciciel: imperium/biblioteki/pamiec_sesji.py
stan_na: 2026-07-18
powod_istnienia: "Mapa podpięć 13 warstw pamięci + lekcje — ciągłość między sesjami (W-360)"
---
# PAMIĘĆ SESJI — W-360

> **Cel:** trwała pamięć między sesjami — mapa podpięć, lekcje, priorytety.
> Aktualizuj PO każdej sesji. Wczytywana przez SessionStart hook.
> Indeksowana w RAG jako korpus `pamiec` (plik .md → `bibliotheca_ulpia/dane/`).

> **⚠️ Weryfikacja 2026-07-18.** Sekcje **map podpięć** (MCP/feedy/egzekucja) i **lekcje** to
> zapis DATOWANY — prawda swojego czasu, nie odświeżana (Prawo I). Sekcja **STAN BIEŻĄCY** na
> dole była ręczna i utknęła („1720 testów, 81 neuronów, 2026-06-22") — przeniesiona na liczby
> WSTRZYKIWANE (W15), więc już nie zamarznie.

---

## 🗺️ PEŁNA MAPA PODPIĘĆ DO LOKALA (Cezar, 2026-06-21)

### A. MCP Servers dla Claude Code

| ID | Serwer | Status | Priorytet | Co daje |
|----|--------|--------|-----------|---------|
| A1 | **GitHub MCP** | ✅ działa (cloud) | — | PR, issues, CI |
| A2 | **Memory MCP** 💎 | ✅ natywny (imperium/biblioteki/pamiec_sesji.py + hook) | — | Trwała pamięć między sesjami (ROZWIĄZUJE W-360) |
| A3 | **Bibliotheca-RAG MCP** 💎 | ✅ zbudowany (W-360 RAG v2) | — | Szukaj w <!-- LICZBA:ksiazki -->115<!-- /LICZBA --> książkach + encyklopedii + docs (tryb FTS; wektory niezbudowane — patrz MAPA_PAMIECI) |
| A4 | **Filesystem MCP** 🔵 | ⏳ opcjonalny | niski | Dostęp do plików lokalnych bez Read tool |
| A5 | **Fetch/Web MCP** 🔵 | ⏳ opcjonalny | niski | WebFetch przez MCP |
| A6 | **Sequential-Thinking MCP** 💎 | ⏳ nie skonfigurowany | średni | Ustrukturyzowane rozumowanie krok po kroku |
| A7 | **SQLite MCP** ⚡ | ⏳ nie skonfigurowany | średni | Zapytania SQL do wyników backtestów bezpośrednio |

### A2. Wydajność — WĄSKIE GARDŁO CPU (zmierzone, nie zgadywane — Prawo XXI)

| Optymalizacja | Zysk (zmierzony) | Status |
|---------------|------------------|--------|
| **Cache wskaźników** (`cache_wskaznikow`, `prekalkuluj_portfel` multiprocessing) | **~1.4×** (3 pary/400 barów, wyniki IDENTYCZNE) | ✅ wdrożone + wpięte w sweepy AB (2026-06-28) |
| **multiprocessing po parach (pętla portfela)** | — | ❌ NIEMOŻLIWE: portfel dzieli kapitał między pary → równoległość łamie semantykę |
| **Snapshot sygnałów .npy** ⚡ | eliminacja re-kalkulacji | ⏳ wysoki |
| **Numba/JIT na GARCH** ⚡ | ~3-4× na wskaźnikach | ⏳ wysoki |

**Korekta (2026-06-28):** wcześniejsze „6-8×" było aspiracyjne. Pomiar: cache wskaźników
daje **1.4×** (prekalkulacja równoległa; pętla barów dominuje czas i pozostaje seryjna,
bo pary współdzielą kapitał portfela). Realny dalszy zysk wymaga Numba/JIT na wskaźnikach
lub snapshotu sygnałów — nie zrównoleglenia pętli portfela.

### B. Dane wejściowe (feedy rynkowe)

| Feed | Dane | Koszt | Status | Neurony które ożywią |
|------|------|-------|--------|---------------------|
| **Binance public** | OHLCV 1h/4h/1d, funding, OI, L/S ratio | darmowy | ✅ adapter live + backfill historyczny | PSY-01, PSY-02, PSY-04, V-03, RADAR-01-05 (7+) |
| **Fear & Greed** (alternative.me) | Indeks 0-100 | darmowy | ⏳ brak adaptera | PSY-03 |
| **DeepSeek API** | LLM: news sentyment, adversarial gate | klucz | ⏳ klucz gotowy | NEWS-01 |
| **RSS/CryptoPanic** 💎 | News sentyment bez API key | darmowy | ⏳ brak adaptera | NEWS-01 (częściowo) |
| **CoinGecko** 🔵 | on-chain, market cap | darmowy (limit) | ⏳ opcjonalny | OC-* |
| **Glassnode** | on-chain premium | ⏳ płatny | niska | OC-* |
| **TradingView webhook** | alerty cenowe → trigger | darmowy | ⏳ opcjonalny | zewnętrzny trigger |
| **Binance WebSocket** | real-time tick | darmowy | ⏳ po paper trading | live mode |
| **Coinglass** 💎 | multi-exchange funding aggregate | darmowy | ⏳ brak adaptera | PSY-01 (lepszy niż Binance) |
| **Deribit DVOL** 💎 | implikowana zmienność krypto | darmowy | ⏳ brak adaptera | nowy neuron DVOL |

### C. Egzekucja

| Giełda | Klucze | Status | Uwagi |
|--------|--------|--------|-------|
| **MEXC** | MEXC_API_KEY + MEXC_SECRET | ⏳ klucze gotowe | Paper trading → live; W-341 |
| **Bybit** 🔵 | — | ⏳ opcjonalny | alternatywa |
| **Binance** 🔵 | — | ⏳ opcjonalny | alternatywa |
| **CCXT** 💎 | — | ⏳ wrapper | unifikuje wszystkie giełdy |

### D. Output / Monitoring

| Kanał | Status | Co wysyła |
|-------|--------|-----------|
| **Telegram Bot** | ⏳ kod gotowy (W-341) | alerty sygnałów na telefon |
| **Telegram bidirectional** 💎 | ⏳ po bocie | komendy z telefonu → Imperium |
| **Dashboard HTML** 💎 | 🔵 opcjonalny | live P&L, sygnały |
| **Discord webhook** 🔵 | ⏳ opcjonalny | alerty alternatywne |
| **Grafana+Prometheus** 💎 | ⏳ zaawansowany | metryki systemowe |
| **Daily email** 🔵 | ⏳ opcjonalny | raport dzienny |

---

## 📋 ZALECANA KOLEJNOŚĆ WDROŻEŃ

```
1. ⚡ Cache sygnałów + multiprocessing  → 8 min → ~40 s (ROI: każda sesja backtestowa)
2. 📡 Binance public feeds              → 7+ martwych neuronów ożywa (Prawo XV)
3. 💎 Memory MCP                        → trwała pamięć (ROZWIĄZUJE W-360)
4. 📱 Telegram Bot                       → alerty na telefon (W-341, kod gotowy)
5. 🤖 DeepSeek API                      → NEWS-01, adversarial gate
6. 🔁 Replay-mode                       → paper trading na historii w przyspieszeniu
7. 💰 MEXC API egzekucja               → live trading
8. 📊 Glassnode/CoinGecko/DVOL/Coinglass → pełne on-chain + zmienność
```

---

## 💎 UNIKALNE KLEJNOTY (wg Cezara)

- **Sequential-Thinking MCP** — Claude myśli krok po kroku (lepsza jakość decyzji)
- **SQLite MCP** — zapytania SQL do backtestu w locie (bez pisania kodu)
- **Memory MCP** — pamięć między sesjami (koniec utraty kontekstu)
- **Coinglass** — funding z wielu giełd naraz (lepsza jakość PSY-01)
- **Deribit DVOL** — implikowana zmienność krypto (nowy wymiar ryzyka)
- **Telegram bidirectional** — komendy z telefonu → Imperium (pełna autonomia)

---

## 📚 LEKCJE Z SESJI

### 2026-07-27 — Mała liczba okien a wynik ROBUST w WF-IC
Neurony EXP-13 (6 okien), SMC-01 (5), V-13 (3) otrzymały status ROBUST, ale są słabiej podparte niż X-17 (25 okien). Wymaga adnotacji o liczbie okien w werdykcie.

### 2026-07-27 — Detektor duplikatów Hyginusa
W systemie istnieje gotowy detektor duplikatów oparty na Jaccardzie bi-gramów, ale nie jest używany. Stanowi darmowe narzędzie do filtracji kandydatów.

### 2026-07-27 — Brak embeddingów w RAG
sentence-transformers nie jest zainstalowany. RAG działa wyłącznie na czystym FTS – bez semantycznego podobieństwa.

### 2026-07-27 — Nowa klasa wady w meldunkach
Sekcja niepewności obok twierdzenia pewnego nie koryguje tezy głównej – twierdzenie wygrywa, bo czyta się pierwsze. Zgłoszono do Księgi Wad.

### 2026-07-27 — Priorytet zwiadów zewnętrznych FRUMENTARIUS
Kosztują ~74k tokenów i potwierdzają znane problemy – powinny być P1, nie P0. Sąd nad kolejką Hyginusa (35 cząstek) to realna produkcja etykiet i ma pierwszeństwo.

### 2026-07-27 — dodaj_checklist nie zapisuje na dysk
dodaj_checklist() zwraca True i inkrementuje licznik w pamięci, ale nie wywołuje zapisz() – wpis nie trafia na dysk. Naprawiono przez dodanie zapisu.

### 2026-07-27 — Niezgodność testów: pytest vs runner Imperium
Testy zielone pod pytest, ale padły pod runnerem Imperium z powodu braku setitem w shim monkeypatch. Naprawiono bez zależności od shimu.

### 2026-07-27 — Błąd w ocenie czasu gnicia – 9 dni zamiast pół roku
W LOG_ZMIAN i pamięci napisano 'pół roku', a faktyczny czas od utworzenia runbooka wynosił 9 dni. Błąd wykryty przy liczeniu dla podglądu Kapitolu – poprawiono we wszystkich miejscach.

### 2026-07-27 — Asymetria testów: pytest vs runner Imperium
Test przeszedł pod pytest, ale padł pod własnym runnerem Imperium przez brak `monkeypatch.setitem` w shimie. Wykryto rozjazd narzędzi – naprawiono przez uniezależnienie od shimu.

### 2026-07-27 — Bieg testów #1 nieważny – równoległość z mutacjami
Testy startowały przed zmianą W22 i biegły w tle podczas sed-owania mutacji. Wynik '55 z 73' i exit 0 od tail, nie od testów. Ważny tylko bieg #2 wystartowany po wszystkich zapisach.

### 2026-07-27 — Mutacja przeżyła przez luźny próg asercji
Test zasięgu miał asercję 'zbadane >= 8+40', co przepuściło zawężenie z 73 do 65 dokumentów. Wymieniono na równość z liczbą policzoną ze źródła. Obie klasy do Księgi Wad. Nota nie wystawiona (błąd nie dostarczony).

### 2026-07-26 — Aerarium – filtrować obce projekty Claude
Obecność jednego obcego katalogu projektu Claude powoduje, że aerarium raportuje jego pamięć i koszty jako własne, zamiast zwrócić no match. Należy filtrować, aby uniknąć fałszywych danych.

### 2026-07-26 — Kronika sesji – zakaz bezwzględnych ścieżek z nazwą użytkownika
Linie z absolutnymi ścieżkami desktopu (~\Desktop\) ujawniają PII i strukturę katalogów. Używać zmiennych środowiskowych lub przechowywać referencje wewnątrz repozytorium dla przenośności.

### 2026-07-26 — Regime-stale bug: pamięć branżowa ślepa na reżim rynku
Wszystkie istniejące systemy pamięci (Mem0/Zep/Letta/A-Mem) są domenowo-ślepe – wydobywają lekcje z bull marketu podczas bessy. Nasza poprawka: × regime_match w scoringu.

### 2026-07-26 — Rozjazd repo z chmurą przez hooki po obu stronach
Od wspólnego punktu e2cb846 chmura dorobiła 2 commity (sync+migawka), lokalnie 2 (auto: sync pamięci). Hooki commitują same po obu stronach – dwa ciągi wyrosły z tego samego pnia.

### 2026-07-20 — Błąd replikacji wiedzy – Claude sam nie stosuje własnych procedur
W poprzednich sesjach wielokrotnie brakowało aktualizacji dokumentów i ledgera, mimo że Claude tworzył procedury (np. ALMA, OBSERWATORY). To klasyczny błąd replikacji wiedzy – Claude tworzy narzędzia, ale sam ich nie używa.

### 2026-07-20 — Cztery zmysły działają na żywych danych
Potwierdzono, że adaptery FearGreed (23), RSS (30 nagłówków), PSY (funding, CVD) i V (CVD) generują głosy. V-03 (CVD)→LONG, PSY-03 (FearGreed=23)→LONG kontrariańsko, NEWS-01→LONG. Abstynencje legalne (Prawo XV).

### 2026-07-20 — Błąd cache/resume kluczowany tylko nazwą pliku w harnessach A/B
Harnessy A/B (ab_tryb_strategii, ab_strategy_mwu, ab_wazenie_ic, ab_pnl_wazenie_ic) używają tylko nazwy pliku jako klucza cache, ignorując parametry konfiguracji.

### 2026-07-20 — Brak flagi --dashboard w CLI – utrata potencjału
Konfig pętli live posiada pola dashboard, ale CLI __main__ nie eksponowało odpowiedniej flagi. Cel P0 (obserwacja live) nie był osiągalny przez CLI. Naprawiono przez refaktoryzację i dodanie flagi.

### 2026-07-20 — Wniosek per-reżim: BEAR=tarcza, reszta szkodzi
W reżimie BEAR stosowanie tarczy (zabezpieczenia) jest korzystne; w pozostałych reżimach tarcza przynosi straty.

### 2026-07-20 — Ekstraktor – kolizja plików scratcha przy równoległej konwersji
ekstraktor.py:149 – kasowanie istniejącego pliku biblioteki przez równoczesne zapisy .calibre-tmp.txt. Fix edc657f nie domknięty.

### 2026-07-20 — Cache djvu nie podpięty do RAG – utrata potencjału (Prawo XV)
konwerter.py:70 – cache djvu zbudowany poprzednio nie jest używany przy indeksowaniu. Chmura nadal woła djvutxt/calibre i gubi djvu.

### 2026-07-20 — Hook startowy powoduje brudny working tree w dwóch plikach
Pliki bibliotheca_ulpia/dane/wizje_i_decyzje.jsonl oraz docs/PAMIEC_SESJI.md są modyfikowane przez hook startowy, co powoduje, że git working tree nie jest w 100% czysty. To normalny churn pamięci, a nie zmiana kodu.

### 2026-07-20 — 22 neurony czekają na adaptery/dane (Prawo XV)
Rodziny NEWS-*, PSY-*, RADAR-*, OC-06/07/08, C-01, V-03, Z-06/Z-07 nie mają jeszcze feedów i abstynują świadomie zgodnie z Prawem XV. To znany, udokumentowany stan, a nie regresja.

### 2026-07-21 — Archium lekcji ma inny nagłówek – szukaj() nie widzi schłodzonych
Po schłodzeniu lekcje trafiają do archiwum z innym nagłówkiem, ale moduł szukaj() używa własnego parsera, który go nie rozpoznaje. Luka w wyszukiwalności pamięci – wymaga ujednolicenia parsera lub wzbogacenia searcha.

### 2026-07-20 — Normalny churn pamięci w plikach dokumentacji
Dwa pliki (wizje_i_decyzje.jsonl, PAMIEC_SESJI.md) zostały zmienione przez hook startowy – to standardowe odświeżanie pamięci sesji, nie zmiana kodu.

### 2026-07-21 — Podkreślnik jako znak słowny w regexie BIB
Użycie \b w regexie dla identyfikatorów BIB nie zamyka się na podkreślniku (jest znakiem słownym). Testy złapały błąd - naprawiono wzorzec.

### 2026-07-20 — API-widma – istnienie w docs ≠ istnienie w kodzie
Błąd klasy API-widma: dokumentacja indeksu/manualu zawiera komendy do plików, które nie istnieją lub zmieniły nazwę. Zweryfikowano na 9 kandydatach – 3 prawdziwe widma. W16 precyzyjnie odróżnia widma od supresji (dydaktyka, wizje, negacje).

### 2026-07-20 — 1003 z 1301 odwolan do dokumentow to kronika sesji
Przenoszenie zywych dokumentow tworzy martwe linki w historii (Prawa I nie wolno poprawiac). Rozklad asymetryczny: zywe maja 1-19 odwolan, kronika 58-63. Przenoszenie jest drogie.

### 2026-07-21 — Test negatywny PROBATORA wykrył błąd graniczny z '_'
Znak '_' jest traktowany jako słowny przez \b, co powodowało fałszywe dopasowanie przy identyfikatorze BIB-006_Carson. Poprawiono test, nie organ – zastosowano inny separator.

### 2026-07-21 — Model cytuje nazwiskiem autora, nie identyfikatorem BIB
Probator zgłaszał fałszywy alarm BEZ_CYTATU gdy model użył nazwiska (np. Hull) zamiast ID. Poprawiono test, nie organ – to realne użycie, a nie błąd weryfikacji.

### 2026-07-20 — Testy wzrosły o dokładnie 7 — potwierdzenie biegnięcia
Po dodaniu 7 testów granicznych licznik wzrósł z 2620 do 2627. To dowód, że testy naprawdę biegły (nie zostały cicho pominięte jak w poprzedniej sesji). Lekcja o zwykłych def test_* zamiast unittest.TestCase wdrożona.

### 2026-07-20 — Pieczątka audytu input_len kłamała — łamanie Prawa XIII
Log pokazał input_len=100, gdy wynik policzono z 80 barów (ciche obcięcie zip). Narusza Prawo XIII (audytowalność) i Prawo I. Zapisano NOTĘ w LEX TALIONIS, CORONA spłacona: strażnik + uodpornienie klasy z wpisem do Księgi Wad.

### 2026-07-20 — LEX TALIONIS: błąd pieczątki = NOTA + CORONA (łata + mechanizm)
Kłamiąca pieczątka input_len to zatwierdzony błąd Imperium (Prawo XIII). Spłacono NOTĘ 5/5 CORONĄ: strażnik + uodpornienie klasy + wpis do Księgi Wad. ZASADA CENSORA: łata nie wystarczy, trzeba mechanizm.

### 2026-07-20 — Skan klasy błędu – 0 innych wystąpień
Po naprawie buga argparse przeskanowano cały kod – 0 innych % w help-stringach. Klasa domknięta, brak epidemii.

### 2026-07-20 — Latentny bug: % w help-stringu argparse
W pomiar_stablecoin_ic.py help-string zawierał % zmiany, co powoduje ValueError przy --help (argparse próbuje formatować). Naprawiono przez podwojenie %.

### 2026-07-20 — Eskalacja przy rutynowym teście złapała krytyczne bugi
Dwa bugi (ccxt NotSupported blokujący pętlę live, brak __main__ w petla_live.py) zostały znalezione dzięki eskalacji do Opusa podczas rutynowego testu paper. Potwierdza skuteczność zasady eskalacji.

### 2026-07-20 — Audyt startowy: 22 neurony ŻYWE ale NIEZMIERZONE
Audyt ujawnił 22 neurony zależne od adapterów (AUG-01, NEWS-01..04, PSY-01..04, RADAR-01..05, OC-06..08, V-03, X-28, Z-06/07) wpięte w pętlę live, ale bez pomiaru w paper. Stanowią największą utratę potencjału.

### 2026-07-20 — Wzorzec kodowania nie skanował przez rok
Regex na subprocess text=True bez encoding istniał od sesji 2026-07-17, ale leżał martwy w checkliście. Po przeniesieniu do listy wzorców od razu złapał realny bug w audycie.

### 2026-07-20 — Wzorzec _ok=True działa bez fałszywek poza testami
Skaner szukający '_ok=True' łapie 35 fałszywek (exist_ok) na 36 trafień, ale po ograniczeniu do imperium/ i narzedzia/ ma zero fałszywek i trafia bug. Testy są poza zakresem.

### 2026-07-20 — Błędy krytyczne złapane przez eskalację modelu
Dwa bugi w petla_live.py ('1H'→ccxt NotSupported, brak __main__) wykryte podczas eskalacji przy rutynowym teście paper. Potwierdza skuteczność płynnego wyboru modelu.

### 2026-07-20 — Stos Hyginusa U1–U4 gotowy, U5 odrzucony
W sesji 56ea4ea2 zakończono implementację U1 (korpus biblioteki anty-echo), U2 (FTS fix crash-buga na myślnikach + query-expansion + hybrid), U3 (self-critique), U4 (świadomość systemu z 22 lukami). U5 (otwarta wiedza modelu) odrzucony na stałe – Prawo I zakazuje halucynacji.

### 2026-07-20 — Bug w audycie przeoczony przez martwy wzorzec
Linia 259 audytu zawierała jedyny subprocess.run bez encoding – trzy pozostałe naprawiono w 2026-07-17, ale tę przeoczono, bo wzorzec 'kodowanie' leżał martwy w checkliście.

### 2026-07-21 — Niespójność licznika memory a rzeczywista liczba wpisów na dysku
Metoda dodaj_checklist() zwiększała licznik w pamięci (52), ale wpis nie zapisywał się do pliku (zostało 51). Zapisz() jest osobną metodą, co powoduje cichą utratę danych. Naprawiono przez jawne wywołanie zapisz() po dodaniu.

### 2026-07-21 — dodaj_checklist() zwraca True, ale wpis nie zapisuje się na dysku
dodaj_checklist() inkrementuje licznik w pamięci, ale zapis na dysk wymaga osobnego wywołania zapisz(). To pułapka – stan pamięci może być niezgodny z dyskiem.

### 2026-07-21 — Błędny wpis o czasie gnicia runbooka – 9 dni zamiast 'pół roku'
W LOG_ZMIAN i pamięci napisano, że runbook gnił 'pół roku'. Zmierzono dokładnie: 9 dni. Sprostowano u źródła (ledgery, pamięć).

### 2026-07-21 — zapisz() gubi nieznane pola istniejącego wpisu – cicha utrata danych
Metoda zapisz() w pamięci proceduralnej nadpisywała tylko znane pola, gubiąc nieznane. Odkryto podczas adversarialnego przeglądu kodu. Naprawiono.

### 2026-07-20 — prekalkuluj_portfel – brak zysku algorytmicznego
Funkcja wykonuje tę samą pracę per-bar co backtest pojedynczy, tylko równolegle (1.4× przyspieszenia). Nie zmniejsza złożoności, tylko maskuje problem.

### 2026-07-20 — Redundancja w wma (_py_hma) – 930 wywołań/tick
Wewnętrzna pętla _py_hma wywołuje wma wielokrotnie (4.5M wywołań, 65.5s cumtime), co jest głównym źródłem stałej liniowej. Optymalizacja: prekalkulacja lub użycie numpy.

### 2026-07-20 — Backtest liniowy, nie O(n²)
Pomiary profili dla 500-1600 barów wykazały stały ms/tick (~66ms), co oznacza skalowanie O(n·okno), nie kwadratowe. Premisa planu naprawy była błędna.

### 2026-07-20 — Output hooka startowego ucięty przez harness
Output hooka startowego (25,5 KB) został ucięty, powodując utratę kluczowej informacji (Dziennik następny krok) z pierwszego okna. Konieczna optymalizacja objętości.

### 2026-07-20 — Testy >2 min na starym Fujitsu – bez limitu czasowego
Testy trwają ponad 2 minuty ze względu na słaby sprzęt. Nie dawać limitu timeoutu. Uruchamiać w tle i cyklicznie sprawdzać, czy bieg żyje. Procedura zapisana w pamięci długoterminowej.

### 2026-06-30 — KROK 0 ujawnił błąd w liczeniu neuronów w MANIFEST
MANIFEST pokazywał 45 aktywnych, podczas gdy grep wykazał ~16. Przyczyna: zwiadowcy i infrastruktura liczone jako neurony. Nauczka: ujednolicić sposób liczenia.

### 2026-06-30 — DeepSeek zawyża możliwości – weryfikacja przez deep-research
Wiele twierdzeń DeepSeek z Zbior_wskaznikow_i_strategi okazało się błędnych lub przesadzonych. Zweryfikowano zewnętrznymi źródłami – system musi opierać się na mierzonych faktach (Prawo XVI).

### 2026-06-30 — Golden Cross w IMPERIUM to wariant EMA
Strategia ZŁOTY ORZEŁ używa EMA 50/200, nie kanonicznego SMA. Zapisano w dokumentacji jako wariant EMA. Wyjaśniono brak aktywacji na DOGE (death cross w całym oknie backtestu).

### 2026-06-30 — Filtr kara w baza.py: wyciszone filtry nie karzą
Gdy n_akt_f==0 (wszystkie neurony FILTR wyciszone), strategia otrzymywała karę 0.5. Poprawiono na 1.0 – neuron FILTR nieobecny nie powinien karać (Prawo XV).

### 2026-06-30 — Naprawiono ImportError w legatus.py
Przy bezpośrednim uruchomieniu legatus.py występował błąd względnego importu z .mikro_neuron. Rozwiązano przez try/except: próbuje import względny, w razie błędu przechodzi na absolutny.

### 2026-06-30 — KalkulatorLewara używa pewnosc_agregatu – błąd strukturalny
KalkulatorLewara pobiera pewnosc_agregatu z Legatusa, ale ta wartość jest zawsze ~1.0, więc leverage jest maksymalny. Należy oddzielić pewność agregatu od wielkości pozycji lub wprowadzić Namiestnika.

### 2026-06-30 — pewnosc_agregatu ≈ 1.0 – główna przyczyna strat
Stała wartość pewności bliska 1.0 prowadzi do maksymalnego lewara w KalkulatorzeLewara, co powoduje ciasne stop-lossy i wiele małych strat. To fundamentalny błąd w agregacji – nie ma zróżnicowania sygnałów.

### 2026-06-30 — Push wymaga uprawnień Read & Write
Błąd 403 przy push do GitHub oznacza, że sesja Claude nie ma uprawnień zapisu do repozytorium. Konieczna zmiana uprawnień w GitHub Settings/Installations.

### 2026-06-30 — Push zablokowany przez 403 - brak uprawnień
Środowisko Claude Code web nie ma uprawnień do pushowania do repozytorium IMPERIAL-MESH-VORTEX (błąd 403). Wymagane skonfigurowanie GitHub App Claude Code z dostępem Read & Write w github.com/settings/installations.

### 2026-06-30 — Normalizacja interwałów w strategiach
Błąd: 5m.upper() -> '5M' zamiast 'M5'. Dodano funkcję _normalizuj_interwal w baza.py mapującą formaty (5m->M5, 1h->H1 itd.) aby backtesty filtr/strategia działały poprawnie.

### 2026-06-30 — Backtest Arena: conservative SL gdy obie bariery w jednym barze
Jeśli w jednej świecy osiągnięto zarówno TP jak i SL, wynikiem jest SL (konserwatywnie).

### 2026-06-30 — Błąd loadera po reorganizacji na strukturę rzymską
Po przeniesieniu modułów do folderów rzymskich (fundament, legiony itp.), loader w pierwy_zwiadowca.py szukał plików po starych nazwach we własnym folderze. Naprawiono przez zmianę na ścieżki względne z importlib.util.spec_from_file_location.

### 2026-06-30 — Błąd cross-module loader po reorganizacji folderów
Po przeniesieniu modułów do struktury rzymskiej, loader szukał plików po starych nazwach. Naprawiono przez aktualizację ścieżek względnych w pierwszym_zwiadowca.py.

### 2026-06-30 — klasyfikuj_rezim() zwraca tylko 4 stany, brak TREND_WEAK/PANIC/ON-CHAIN_BULLISH/SMC_ACTIVE
Funkcja klasyfikacji reżimu ograniczona do TREND_STRONG, RANGING, VOLATILE, NORMAL. Brakuje stanów przewidzianych w dokumentacji.

### 2026-06-30 — Bug W7 audytu fałszywie flaguje URL z .md w domenie
W7 audyt markerował zewnętrzne URL zawierające '.md' w domenie (np. www.mdpi.com) jako martwe linki, blokując commit. Naprawiono przez dodanie warunku pomijającego zewnętrzne protokoły (http/https/mailto/ftp) na początku href.

### 2026-06-30 — Dekorelacja V-13 i V-14 potwierdza dywersyfikację
Korelacja między NeuronChoppiness (V-14) a poprzednim wskaźnikiem zmienności |r|=0.05–0.27, co spełnia Prawo XVI (unikamy redundancji).

### 2026-06-30 — Brak pola kategoria na SygnalNeuronu uniemożliwiał agregację wag reżimu
Pole 'kategoria' nie istniało w SygnalNeuronu, przez co WAGI_REZIMU były martwym kodem. Dodano pole i przekazywanie z KATEGORII neuronu – teraz wagi reżimu działają poprawnie.

### 2026-06-30 — Brak Stan na: w W6 to błąd, nie pominięcie
Audyt spojności W6 milcząco pomijał bloki bez 'Stan na:'. Dodano jawne else zgłaszające błąd. RegExp rozszerzony o markdown `**Stan na:**`.

### 2026-06-30 — Błąd edycji README z powodu niedopasowania tekstu
Próba edycji pliku README przez narzędzie `edit` nie powiodła się, ponieważ szukany fragment nieznacznie różnił się od faktycznej treści. Rozwiązanie: ponowne odczytanie pliku i użycie dokładnego tekstu.

### 2026-06-30 — Utrata potencjału: Klucznik ignorowany przez Dyrygenta
Prawo XV: Klucznik obliczał strategie, ale Dyrygent ich nie używał. Naprawiono przez dodanie trybów uwzględniających strategię.

### 2026-06-30 — Prawo XV: nie dodawać neuronów z niedostępnym API
Potwierdzono zasadę, że neurony wymagające nieistniejącego API zawsze zwracają NEUTRAL. W tej sesji dodano tylko neurony korzystające z dostępnych wskaźników (Donchian, RSI, BB).

### 2026-07-10 — Regime-stale bug – problem branżowy z pamięcią niezależną od reżimu
Odkryto, że konkurencyjne systemy pamięci nie uwzględniają reżimu rynku, co powoduje wyciąganie nieodpowiednich lekcji (np. z hossy podczas bessy). Nasza implementacja Pamięci Reżimowej rozwiązuje to przez wymiar regime_match w scoringu.

### 2026-06-30 — Naprawiono ImportError w legatus.py przez try/except
Relatywny import z .mikro_neuron powodował błąd przy bezpośrednim uruchomieniu. Rozwiązanie: try/except z importem absolutnym jako fallback. Wzorzec do powielenia w nowych modułach.

### 2026-06-30 — TA-Lib wymagany przez Bramę Kalkulatora
Brama Kalkulatora celowo odmawia startu bez TA-Lib (Prawo I). Na Windows 2026 pip install TA-Lib działa, fallback: wheels z github.com/cgohlke/talib-build.

### 2026-06-30 — Interval normalization bug: '5m'.upper() ≠ 'M5'
Strategie używają formatu 'M5', a interwał z backtestu po .upper() daje '5M'. Naprawiono przez _normalizuj_interwal() w baza.py konwertujące '5m'→'M5', '1h'→'H1' itd.

### 2026-06-30 — Brama Kalkulatora wymaga TA-Lib do startu
CalculatorGateway celowo odmawia startu bez TA-Lib (Prawo I - Zero halucynacji). Każde obliczenie logowane z SHA-256 audit stamp (Prawo XIII).

### 2026-06-30 — Słabość ręcznego parametru reżimu
Przetestowano 3 scenariusze rynkowe — system wymaga automatycznego klasyfikatora reżimu, bo ręczne ustawianie jest zawodne i nie skalowalne.

### 2026-06-30 — Audyt W6: brak Stan na = błąd, markdown tolerowany
Dodano else dla braku 'Stan na:'. Regex toleruje **Stan na:** data.

### 2026-06-30 — Dynamiczna dźwignia od pewności i reżimu
pewnosc <0.55→0x, <0.65→2x, <0.75→5x, <0.85→10x, <0.92→15x, >=0.92→20x. Mnożniki reżimu: VOLATILE×0.5, PANIC×0.1, RANGING×0.7, TREND_STRONG×1.2.

### 2026-06-30 — Klucznik ignorowany przez Dyrygenta (Prawo XV)
Dyrygent nie używał wyników Klucznika (strategii) — kierunek i pewność pochodziły wyłącznie z neuronów. Naprawiono: dodano logikę trybów (agregat/filtr/strategia) uwzględniającą DopasowanieStrategii.

### 2026-06-30 — Bug: neuron zwraca NEUTRAL gdy brak danych w BramaKalkulatora
MikroNeuron.interpretuj() zwraca SygnalNeuronu z wartoscia NEUTRAL jesli wskaznik nie istnieje w dict Brama. To powoduje ciche bledy w strategiach - nalezy dodac walidacje i warning.

### 2026-06-30 — Prawo XV: Bez martwych głosów – neuron bez API zawsze NEUTRAL
Nie dodawać neuronów wymagających niedostępnego API – będą zawsze NEUTRAL, co psuje agregację. Zweryfikowano wszystkie nowe neurony pod kątem dostępności wskaźników.

### 2026-06-30 — Prawo XIX: Kod jest Prawem – klucze katalogu muszą zgadzać się z kodem
Audyt ujawnił rozbieżności między KATALOG_NEURONOW.md a kodem. Utworzono MAPA_KLUCZY.md jako kanoniczne mapowanie. Klucznik weryfikuje DOSTEPNY=True.

### 2026-07-10 — Pełny backtest 18k barów × 5 par pada na timeout
Pełny przebieg 18k barów × 5 par jest za wolny i przekracza limit 600s. Potwierdza to ZASADĘ ANALIZY CZĄSTKOWEJ: trzeba cap barów + cząstkowanie z zapisem do areny.

### 2026-06-30 — Błąd warmup Accelerator: slow+sma_ac+1
Funkcja _py_accelerator miała zbędne +1 w warmup, co powodowało off-by-one. Usunięto.

### 2026-07-10 — Recenzent łapie granice brudnych danych i ścieżek awaryjnych
Cubic na PR #118 znalazł kilkanaście realnych bugów w kodzie, który przeszedł mój adversarial przegląd. Wzorzec: łapie to, czego NIE testuję z góry — dane wejściowe nie-string/None/liczba (np. _skroc na co0=int), ścieżki AWARYJNE (fallback hooka gubi wydruk), martwe wzorce po round-tripie przez JSONL, daty/liczby zanieczyszczające miary podobieństwa. Lekcja: przed pushem testować BRUDNE WEJŚCIE i ŚCIEŻKĘ BŁĘDU, nie tylko happy path.

### 2026-06-30 — Prawo I: Neurony nie liczą, Brama liczy
MikroNeurony tylko interpretują gotowe wskaźniki (metoda interpretuj()), nigdy nie obliczają. Obliczenia wykonuje Brama Kalkulatora (TA-Lib). To fundamentalna zasada architektury IMPERIUM.

### 2026-06-30 — Prawo XV: Utrata potencjału Klucznika
Klucznik obliczał strategie, ale Dyrygent je ignorował. Strategie nie wpływały na decyzje. Naprawiono przez dodanie trybów: agregat (ignoruje strategie), filtr (strategia blokuje konflikt), strategia (strategia narzuca kierunek).

### 2026-06-30 — Hurst-DFA vs R/S: dekorelowane na krypto trendującym
Prawo XVI: DFA i R/S dają nieskorelowane wyniki na trendującym krypto. Potwierdzono empirycznie, że to nie redundancja.

### 2026-06-30 — Yang-Zhang traci 7-14× informacji vs std(close)
Używanie std(close) zamiast estymatora Yang-Zhang (OHLC) marnuje potencjał volatility. Narusza Prawo XV. Należy zastąpić w obliczeniach.

### 2026-06-30 — Filtr nieobecny nie karze strategii
n_akt_f==0 dawało filtr_frakcja=0.5 karząc strategię. Zmieniono na 1.0 (Prawo XV).

### 2026-06-30 — Zombie neurons zwracają NEUTRAL gdy Brama nie dostarcza kluczy
Neurony z DOSTEPNY=False zawsze zwracały NEUTRAL, maskując brak integracji. Wykryto przez Prawo XV. Naprawiono: Roj.zbierz_sygnaly() pomija DOSTEPNY=False, dodano POWOD_NIEDOSTEPNOSCI.

### 2026-06-30 — Prawo I: Zero halucynacji matematycznych
AI nigdy nie oblicza matematyki. Kod (TA-Lib, C) oblicza RSI/EMA/ATR → JSON 'answer key' → AI tylko interpretuje. Brama Kalkulatora nie uruchomi się bez TA-Lib.

## 🔄 STAN BIEŻĄCY (liczby wstrzykiwane z kodu — W15, nie zamarzają)

- **Testy:** `python tests/run_tests.py` (nie hardkodujemy — liczba rośnie co sesję)
- **Neurony:** <!-- LICZBA:neurony -->87<!-- /LICZBA --> (aktywne <!-- LICZBA:neurony_aktywne -->81<!-- /LICZBA -->, wyciszone 6) | **Zwiadowcy:** <!-- LICZBA:zwiadowcy -->15<!-- /LICZBA -->
- **Elitarne (Prawo XX):** <!-- LICZBA:elity -->18<!-- /LICZBA -->
- **Branch:** `claude/sleepy-fermi-dsdE4`
- **Pamięć:** 13 warstw + organ W7 (mapa: `docs/MAPA_PAMIECI.md`); Centrum Pamięci v5
