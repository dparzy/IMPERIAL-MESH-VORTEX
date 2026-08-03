---

## Ostatnia aktualizacja: 2026-07-30
kategoria: TABULA
typ: zywy
wlasciciel: imperium/biblioteki/pamiec_sesji.py
stan_na: 2026-07-30
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

### 2026-07-30 — Alarmy procesowe to zadania: 35 cząstek Hyginusa, 20 pomysłów W9, LEKCJA 3
35 cząstek Hyginusa czeka na sędziego (trzeci raz w Top-3 lekcji), 20 pomysłów z refleksji W9 wisi >21 dni, a LEKCJA 3 o zgodności skal wymaga sprawdzenia. To zaległości, nie tapeta.

### 2026-07-30 — CLAUDE.md przekracza limit 200 linii i rośnie ~1 linia/dzień
Konstytucja ma 259 linii (>200) i rośnie liniowo — pełzająca regresja. Część treści trzeba przenieść do skilli na żądanie; potrzebna decyzja kierunkowa Cezara.

### 2026-08-02 — Martwy słownik MECHANIZMY_ZWIADOWCY w rejestrze
Słownik 12 wpisów (rejestr.py:208) nie jest czytany przez żaden kod; mechanizm MECHANIZM trafia tylko do neuronów. Skutek: DISCRIMINATOR i dekorelacja (Prawo XVI) nie obejmują 15 zwiadowców; EXP-13/14 aktywne bez wpisu.

### 2026-07-27 — Testy Warstwy 6 padają przy nieaktualnej dacie 'Stan na:'
Audyt spójności (Warstwa 6) zgłasza błąd, gdy README.md lub docs/MANIFEST_KODU.md deklarują 'Stan na:' starszą niż data ostatniego commitu. Zgodnie z Regułą 9 Prawa XXI to błahostka — naprawiana samodzielnie, bez eskalacji do Cezara.

### 2026-08-01 — Heredoc gubi backslash — instrument kłamie
Regex przekazany przez heredoc tracił backslash, co fałszowało wyniki; przejście na skrypty plikowe. Testy złapały 2 bugi: inline 'cd …; git push' i noun-first closure. Dodano testy graniczne dla fałszywych pozytywów z cytowania w prozie.

### 2026-08-01 — Regex w heredoc gubi backslash — instrument kłamie, nie dane
Przy budowie CORONY regex przez heredoc stracił backslash; przejście na skrypty plikowe ujawniło dwa realne bugi (inline 'cd …; git push', fraza rzeczownikowa) i dwa fałszywe alarmy na cytatach w prozie. Dodano testy graniczne.

### 2026-07-28 — MEXC ✗ – brak realnych orderów i pętla P&L niezamknięta
System nie ma połączenia z MEXC, więc roj jest tylko backtestowany. Największa luka Imperium – pętla P&L→wagi nie działa.

### 2026-07-28 — MEXC ✗ – pętla P&L→wagi wciąż nie zamknięta w żywym rynku
Rój jest backtestowany, 87 neuronów, 22 warstwy audytu, ale brak realnych orderów przez MEXC. To największa luka Imperium: mierzymy tanie, bo drogie jest trudne. Efekt latarni działa.

### 2026-07-27 — Rozwój LLM to skoki po pomiarze, nie nauka w locie
Model ma zamrożone wagi po treningu. Rozwój osiąga się przez RAG (natychmiastowa pamięć) i cykliczne dotrenowanie LoRA po egzaminie na arenie. Awans tylko po zielonym pomiarze.

### 2026-07-27 — Zastosowane zasady projektowe: SYMBIOZA, Prawo XVI, Test-Granic
Wdrożenie respektowało ZASADĘ SYMBIOZY (zmiana nie izolowana), Prawo XVI (jedno źródło prawdy dla wag IC), Regułę Test-Granic (testowanie co może pójść źle).

### 2026-07-27 — Bug: tryb sign-only daje pełną wagę niezmierzonym neuronom mimo IC=0
W legatus.py:515 w trybie sign-only neurony z domyślnym IC=0 nie są wyciszane – otrzymują pełną wagę bazową, co wypacza decyzję.

### 2026-07-27 — 43 cząstki Hyginusa bez sędziego
Największa czynna utrata potencjału – zapłacony zwiad leży odłogiem. Priorytet P0 na następne wachty.

### 2026-07-27 — Kolizja plików scratcha przy równoległej konwersji
Cubic PR#119 P1: ekstraktor.py nadpisuje plik .calibre-tmp.txt z fixu edc657f – kasowanie istniejącego pliku biblioteki przy równoległej konwersji.

### 2026-07-27 — Cache djvu niepodpięty do RAG
Cubic PR#119 P1: cache djvu zbudowany wcześniej nie jest używany przez indeksowanie RAG – chmura dalej woła djvutxt/calibre i gubi djvu. Prawo XV – utrata potencjału.

### 2026-07-30 — Kod QUAESITORA przetrwał reinstalację, ale bez testów i poza gitem
330 linii, CLI działa, ale brak testów i nieśledzony. Formalnie organ nie istnieje (Prawo XIX). Wymaga domknięcia testami i commitem.

### 2026-07-27 — 14,9 mln barów 1m nieużytych od 2022
Czytnik odbiera 14,9 mln świec 1-minutowych, ale dane kończą się 2022-07-27 – backtest działa, live nie używa tych danych.

### 2026-07-27 — Większość odwołań do dokumentów to kronika sesji (historia)
1003 z 1301 odwołań do docs/*.md to historia, której nie wolno przepisywać (Prawo I). Przenoszenie żywych dokumentów tworzy martwe linki; przenoszenie migawek jest tanie.

### 2026-07-27 — Mnemosyne.py wycofany – błędnie oznaczony jako aktywny W1
Plik mnemosyne.py był oznaczony w dokumentacji jako warstwa W1, ale w rzeczywistości jest wycofany (Prawo XVI) – zastąpiony przez pamiec_refleksyjna i ksiega_wad. Poprawiono.

### 2026-07-27 — Brak __main__ w petla_live.py – bug live
W petla_live.py brakowało bloku __main__, co blokowało pętlę live przy rutynowym teście. Wykryte dzięki eskalacji przy anomalii.

### 2026-07-27 — Bug FTS na myślnikach – ciche ginięcie tematów
W FTS bibliotekarza bug crash na myślnikach powodował ciche giniecie tematów (np. 'momentum trend-following'). Naprawiony przez _fts_bezpieczne.

### 2026-07-27 — 43 cząstki Hyginusa bez sędziego (zapłacony zwiad niewykorzystany)
Kolejka Hyginusa zawiera 43 cząstki czekające na sąd (poprzednio 33). To zapłacony, ale niewykorzystany zwiad, co narusza Prawo XV. Priorytet najniższy (ostatnie w kolejce).

### 2026-07-29 — Wrażliwość interwału na wielkość liter zmienia decyzje
Etykieta interwału (np. '4h' vs '4H') jest case-sensitive w Legatus._formacja_interwalu - cicho zmienia wyniki backtestu. Przyczyna: słownik mapujący interwały. Naprawiono przez dodanie aliasów i normalizację.

### 2026-07-27 — Backtest liniowy O(n·okno), nie O(n²)
Pomiar cProfile wykazał stały ~66 ms/tick dla okna 251 barów. Skalowanie liniowe, nie kwadratowe. Poprzednia diagnoza o O(n²) była błędna.

### 2026-07-27 — Prawdziwy sprawca kwadratu: _py_hma (pętla w pętli wma)
Wewnętrzna pętla w _py_hma wywołuje wma wielokrotnie (4,5 mln wywołań na 2700 ticków), dając O(period²) dla tego jednego wskaźnika. Reszta backtestu jest liniowa.

### 2026-07-27 — Błąd w ocenie czasu gnicia – 9 dni zamiast pół roku
W LOG_ZMIAN i pamięci napisano 'pół roku', a faktyczny czas od utworzenia runbooka wynosił 9 dni. Błąd wykryty przy liczeniu dla podglądu Kapitolu – poprawiono we wszystkich miejscach.

### 2026-07-27 — Mutacja przeżyła przez luźny próg asercji
Test zasięgu miał asercję 'zbadane >= 8+40', co przepuściło zawężenie z 73 do 65 dokumentów. Wymieniono na równość z liczbą policzoną ze źródła. Obie klasy do Księgi Wad. Nota nie wystawiona (błąd nie dostarczony).

### 2026-07-26 — Aerarium – filtrować obce projekty Claude
Obecność jednego obcego katalogu projektu Claude powoduje, że aerarium raportuje jego pamięć i koszty jako własne, zamiast zwrócić no match. Należy filtrować, aby uniknąć fałszywych danych.

### 2026-07-26 — Kronika sesji – zakaz bezwzględnych ścieżek z nazwą użytkownika
Linie z absolutnymi ścieżkami desktopu (~\Desktop\) ujawniają PII i strukturę katalogów. Używać zmiennych środowiskowych lub przechowywać referencje wewnątrz repozytorium dla przenośności.

### 2026-07-26 — Regime-stale bug: pamięć branżowa ślepa na reżim rynku
Wszystkie istniejące systemy pamięci (Mem0/Zep/Letta/A-Mem) są domenowo-ślepe – wydobywają lekcje z bull marketu podczas bessy. Nasza poprawka: × regime_match w scoringu.

### 2026-07-20 — Błąd replikacji wiedzy – Claude sam nie stosuje własnych procedur
W poprzednich sesjach wielokrotnie brakowało aktualizacji dokumentów i ledgera, mimo że Claude tworzył procedury (np. ALMA, OBSERWATORY). To klasyczny błąd replikacji wiedzy – Claude tworzy narzędzia, ale sam ich nie używa.

### 2026-07-20 — Cztery zmysły działają na żywych danych
Potwierdzono, że adaptery FearGreed (23), RSS (30 nagłówków), PSY (funding, CVD) i V (CVD) generują głosy. V-03 (CVD)→LONG, PSY-03 (FearGreed=23)→LONG kontrariańsko, NEWS-01→LONG. Abstynencje legalne (Prawo XV).

### 2026-07-20 — Błąd cache/resume kluczowany tylko nazwą pliku w harnessach A/B
Harnessy A/B (ab_tryb_strategii, ab_strategy_mwu, ab_wazenie_ic, ab_pnl_wazenie_ic) używają tylko nazwy pliku jako klucza cache, ignorując parametry konfiguracji.

### 2026-07-20 — Brak flagi --dashboard w CLI – utrata potencjału
Konfig pętli live posiada pola dashboard, ale CLI __main__ nie eksponowało odpowiedniej flagi. Cel P0 (obserwacja live) nie był osiągalny przez CLI. Naprawiono przez refaktoryzację i dodanie flagi.

### 2026-07-20 — Ekstraktor – kolizja plików scratcha przy równoległej konwersji
ekstraktor.py:149 – kasowanie istniejącego pliku biblioteki przez równoczesne zapisy .calibre-tmp.txt. Fix edc657f nie domknięty.

### 2026-07-20 — Cache djvu nie podpięty do RAG – utrata potencjału (Prawo XV)
konwerter.py:70 – cache djvu zbudowany poprzednio nie jest używany przy indeksowaniu. Chmura nadal woła djvutxt/calibre i gubi djvu.

### 2026-07-20 — 22 neurony czekają na adaptery/dane (Prawo XV)
Rodziny NEWS-*, PSY-*, RADAR-*, OC-06/07/08, C-01, V-03, Z-06/Z-07 nie mają jeszcze feedów i abstynują świadomie zgodnie z Prawem XV. To znany, udokumentowany stan, a nie regresja.

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

### 2026-07-21 — Błędny wpis o czasie gnicia runbooka – 9 dni zamiast 'pół roku'
W LOG_ZMIAN i pamięci napisano, że runbook gnił 'pół roku'. Zmierzono dokładnie: 9 dni. Sprostowano u źródła (ledgery, pamięć).

### 2026-07-20 — prekalkuluj_portfel – brak zysku algorytmicznego
Funkcja wykonuje tę samą pracę per-bar co backtest pojedynczy, tylko równolegle (1.4× przyspieszenia). Nie zmniejsza złożoności, tylko maskuje problem.

### 2026-07-20 — Backtest liniowy, nie O(n²)
Pomiary profili dla 500-1600 barów wykazały stały ms/tick (~66ms), co oznacza skalowanie O(n·okno), nie kwadratowe. Premisa planu naprawy była błędna.

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

### 2026-06-30 — Błąd loadera po reorganizacji na strukturę rzymską
Po przeniesieniu modułów do folderów rzymskich (fundament, legiony itp.), loader w pierwy_zwiadowca.py szukał plików po starych nazwach we własnym folderze. Naprawiono przez zmianę na ścieżki względne z importlib.util.spec_from_file_location.

### 2026-06-30 — Błąd cross-module loader po reorganizacji folderów
Po przeniesieniu modułów do struktury rzymskiej, loader szukał plików po starych nazwach. Naprawiono przez aktualizację ścieżek względnych w pierwszym_zwiadowca.py.

### 2026-06-30 — Bug W7 audytu fałszywie flaguje URL z .md w domenie
W7 audyt markerował zewnętrzne URL zawierające '.md' w domenie (np. www.mdpi.com) jako martwe linki, blokując commit. Naprawiono przez dodanie warunku pomijającego zewnętrzne protokoły (http/https/mailto/ftp) na początku href.

### 2026-06-30 — Dekorelacja V-13 i V-14 potwierdza dywersyfikację
Korelacja między NeuronChoppiness (V-14) a poprzednim wskaźnikiem zmienności |r|=0.05–0.27, co spełnia Prawo XVI (unikamy redundancji).

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

### 2026-06-30 — Audyt W6: brak Stan na = błąd, markdown tolerowany
Dodano else dla braku 'Stan na:'. Regex toleruje **Stan na:** data.

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
