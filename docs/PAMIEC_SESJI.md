---

## Ostatnia aktualizacja: 2026-07-20
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

### 2026-07-20 — Błędy krytyczne złapane przez eskalację modelu
Dwa bugi w petla_live.py ('1H'→ccxt NotSupported, brak __main__) wykryte podczas eskalacji przy rutynowym teście paper. Potwierdza skuteczność płynnego wyboru modelu.

### 2026-07-20 — Stos Hyginusa U1–U4 gotowy, U5 odrzucony
W sesji 56ea4ea2 zakończono implementację U1 (korpus biblioteki anty-echo), U2 (FTS fix crash-buga na myślnikach + query-expansion + hybrid), U3 (self-critique), U4 (świadomość systemu z 22 lukami). U5 (otwarta wiedza modelu) odrzucony na stałe – Prawo I zakazuje halucynacji.

### 2026-07-20 — Bug w audycie przeoczony przez martwy wzorzec
Linia 259 audytu zawierała jedyny subprocess.run bez encoding – trzy pozostałe naprawiono w 2026-07-17, ale tę przeoczono, bo wzorzec 'kodowanie' leżał martwy w checkliście.

### 2026-07-20 — Mechanizm zasiewu połyka regex z checklisty
Funkcja 'zasiej_startowe' cicho ignoruje pole 'regex' wpisu w checkliście – wzorce w Księdze Wad nigdy nie skanowały. Przyczyna: domyślna inicjalizacja pomija nieobowiązkowe klucze.

### 2026-07-21 — Niespójność licznika memory a rzeczywista liczba wpisów na dysku
Metoda dodaj_checklist() zwiększała licznik w pamięci (52), ale wpis nie zapisywał się do pliku (zostało 51). Zapisz() jest osobną metodą, co powoduje cichą utratę danych. Naprawiono przez jawne wywołanie zapisz() po dodaniu.

### 2026-07-21 — Ukryta zależność od monkeypatch w runnerze Imperium
Testy PEDES przechodzą pod pytest, ale padają pod własnym runnerem Imperium, którego shim monkeypatch nie ma metody setitem. Naprawiono bez zależności od shimu.

### 2026-07-21 — dodaj_checklist() zwraca True, ale wpis nie zapisuje się na dysku
dodaj_checklist() inkrementuje licznik w pamięci, ale zapis na dysk wymaga osobnego wywołania zapisz(). To pułapka – stan pamięci może być niezgodny z dyskiem.

### 2026-07-21 — Błędny wpis o czasie gnicia runbooka – 9 dni zamiast 'pół roku'
W LOG_ZMIAN i pamięci napisano, że runbook gnił 'pół roku'. Zmierzono dokładnie: 9 dni. Sprostowano u źródła (ledgery, pamięć).

### 2026-07-21 — Testy padają pod runnerem Imperium przez brak setitem w shimie monkeypatch
Testy zielone pod pytest, ale padają pod własnym runnerem – shim monkeypatch nie ma setitem. Naprawiono bez zależności od shimu.

### 2026-07-21 — zapisz() gubi nieznane pola istniejącego wpisu – cicha utrata danych
Metoda zapisz() w pamięci proceduralnej nadpisywała tylko znane pola, gubiąc nieznane. Odkryto podczas adversarialnego przeglądu kodu. Naprawiono.

### 2026-07-21 — Cichy audyt – hook nie drukował wyniku przy uruchomieniu
Audyt złapał nowy organ w trzech warstwach naraz (W11, W15, W17), ale hook nie wyświetlił wyniku. To klasa 'mechanizm, który przy awarii wygląda na sprawny' – naprawiono.

### 2026-07-20 — Zawartość pliku w wrzutni
Plik z wrzutnia to dump rozmów z Hyginusem (DeepSeek) zawierający research hybrydy LLM: modele 3B, LoRA, LARSA/AlphaQuanter, Fin-R1, Unsloth/QLoRA, fine-tuning na chmurze. Wątek hybrydy-ucznia od linii 2163.

### 2026-07-20 — Parametry Fujitsu Lifebook E754
CPU i5-4200M Haswell 2013, 2 rdzenie/4 wątki, 2.5 GHz. RAM 16 GB (9 GB wolne). GPU Intel HD 4600 1 GB – bezużyteczne do LLM. Inferencja tylko CPU, maksymalny model 3-8B mocno skwantyzowany.

### 2026-07-20 — Testy 1648/1648 zielone – kod stabilny
Po wymuszeniu UTF-8 testy przechodzą w 100%. Fałszywy alarm w aktualizuj.ps1 wynikał z kodowania konsoli (cp1250 nie obsługuje emoji).

### 2026-07-20 — Luka pokrycia 4h – tylko 10 par zamiast 15
Pomiar wykazuje brak plików 4h dla BNB/BTC/DOGE/ETH/SOL. Wpływa na redukcję kombinacji do 40 zamiast potencjalnych 45.

### 2026-07-20 — EXP-14 Kyle: bardzo niska korelacja + wysoki IC
Średnie max|ρ| = 0.087 (prawie ortogonalny do reszty roju), IC = 0.301/0.302/0.308. Silny wkład informacyjny bez redundancji.

### 2026-07-20 — EXP-13 GARCH: niska dekorelacja + stabilny skill
Średnie max|ρ| = 0.141 (poniżej progu 0.20), IC = 0.247/0.245/0.254 dla h=1/6/30. Potwierdza filar siły i realny sygnał predykcyjny na wszystkich parach.

### 2026-07-20 — IC EXP-13/14 podejrzanie wysoki – możliwy artefakt autokorelacji
IC ~0.25-0.30, podczas gdy typowe IC >0.05 jest rzadkie. Wskazuje to na możliwość łapania autokorelacji zmienności, a nie czystego forward-return. Wymaga kontroli na nienakładających się zwrotach.

### 2026-07-20 — EXP-15 PIN martwy na wszystkich parach
Pomiar potwierdził, że EXP-15 (PIN) nie generuje sygnału na żadnej z 40 kombinacji (15 par × 3 TF). Już wcześniej wyciszony (DOSTEPNY=False), ale weryfikacja usztywnia decyzję.

### 2026-07-20 — Potrójna symbioza audit-sigilium: mechanizm wykrywa własne organy w wielu warstwach
Audyt W11/W15/W17 złapał nowe sigilium (runbook, licznik w README, rekord w codicilu) – symbioza działa przeciw autorowi. Wymusza to ostrożność przy dodawaniu nowych elementów.

### 2026-07-20 — Runbooki W11 gniją – nieaktualna treść i duplikacja CLAUDE.md
Runbooki W11 zawierają własną, ręcznie wpisaną treść (np. 'git push -u origin') zamiast pobierać kroki z CLAUDE.md – jedynego źródła prawdy. Ponadto funkcja dodaj() dedupuje po nazwie, co uniemożliwia aktualizację istniejącego runbooku.

### 2026-07-20 — Winget dostępny jako narzędzie do instalacji
Na laptopie Cezara dostępne jest winget (Windows Package Manager) – może służyć do cichej instalacji djvulibre i innych narzędzi bez uruchamiania interaktywnych instalatorów.

### 2026-07-20 — djvu wymaga djvutxt (djvulibre), nie calibre
Konwersja djvu do tekstu wymaga narzędzia 'djvutxt' z djvulibre; calibre historycznie nie czyta djvu. Wszystkie 5 ksiąg do domknięcia QNT/RLA/Aronson to djvu – calibre jest dla nich bezużyteczne.

### 2026-07-20 — Hotspoty: _py_supertrend i _py_volume_profile
Czysto-pythonowe pętle O(okno) na wskaźnikach supertrend i volume_profile są ciężkie (okno 251, wiele symboli). Kandydaci do wektoryzacji numpy.

### 2026-07-20 — prekalkuluj_portfel – brak zysku algorytmicznego
Funkcja wykonuje tę samą pracę per-bar co backtest pojedynczy, tylko równolegle (1.4× przyspieszenia). Nie zmniejsza złożoności, tylko maskuje problem.

### 2026-07-20 — Redundancja w wma (_py_hma) – 930 wywołań/tick
Wewnętrzna pętla _py_hma wywołuje wma wielokrotnie (4.5M wywołań, 65.5s cumtime), co jest głównym źródłem stałej liniowej. Optymalizacja: prekalkulacja lub użycie numpy.

### 2026-07-20 — Backtest liniowy, nie O(n²)
Pomiary profili dla 500-1600 barów wykazały stały ms/tick (~66ms), co oznacza skalowanie O(n·okno), nie kwadratowe. Premisa planu naprawy była błędna.

### 2026-07-20 — CODEX: 30 sugestii na 46 rekordów - dominacja sugestii
Z 46 rekordów CODEX-u 30 to sugestie (A/B 11, IC 4, pomiary 1). Proporcja sugeruje, że system gromadzi głównie nierozstrzygnięte pomysły, a nie faktyczne pomiary czy decyzje. Może to wskazywać na potrzebę przeglądu i priorytetyzacji.

### 2026-07-20 — Runbooki W11 gniją przez deduplikację po nazwie
Runbook 'Bezpieczny commit' zawiera nieaktualny krok 'git push -u', a funkcja dodaj() uniemożliwia aktualizację przez deduplikację po nazwie. Każda procedura raz zapisana pozostaje niezmienna, co prowadzi do gnicia treści.

### 2026-07-20 — Tempo przetwarzania WF-IC
~2 min/para (15 par ~30 min). BTC/ETH cięższe. Można szacować czas przyszłych uruchomień.

### 2026-07-20 — Wynik WF-IC dla 15 par 4h
32/49 neuronow ROBUST, 17 szum/niepewne. Czołówka: EXP-13, SMC-01, V-02/V-13/V-14, rodzina X-*. UWAGA: EXP-13 (6 okien), SMC-01 (5), V-13 (3) maja malo okien -> ROBUST slabiej podparty niz X-17/X-01 (25 okien).

### 2026-07-20 — Buforowanie stdout w Pythonie
Raport WF-IC jest buforowany do końca; aby widzieć postęp na żywo, należy uruchomić skrypt z flagą -u (unbuffered).

### 2026-07-20 — Output hooka startowego ucięty przez harness
Output hooka startowego (25,5 KB) został ucięty, powodując utratę kluczowej informacji (Dziennik następny krok) z pierwszego okna. Konieczna optymalizacja objętości.

### 2026-07-20 — Asymetria otwarcia i zamknięcia sesji
Otwarcie sesji nie ma egzekwowanej checklisty, w przeciwieństwie do 9-krokowej checklisty zamknięcia. Ryzyko pominięcia kluczowych kroków startu.

### 2026-07-20 — Testy >2 min na starym Fujitsu – bez limitu czasowego
Testy trwają ponad 2 minuty ze względu na słaby sprzęt. Nie dawać limitu timeoutu. Uruchamiać w tle i cyklicznie sprawdzać, czy bieg żyje. Procedura zapisana w pamięci długoterminowej.

### 2026-07-20 — Testy na starym Fujitsu trwają >2 minuty — normalne
Testy (2584) zajmują ponad 2 minuty na starym sprzęcie. Nie dawaj limitu czasu, uruchamiaj w tle i cyklicznie sprawdzaj, czy żyje. Zapamiętane na stałe, nie wracamy do tematu.

### 2026-06-30 — KROK 0 ujawnił błąd w liczeniu neuronów w MANIFEST
MANIFEST pokazywał 45 aktywnych, podczas gdy grep wykazał ~16. Przyczyna: zwiadowcy i infrastruktura liczone jako neurony. Nauczka: ujednolicić sposób liczenia.

### 2026-06-30 — Podczas implementacji pomijano aktualizację dokumentacji modułowej (KALKULATOR_LEWARA.md, IGRZYSKA_IMPERIUM.md, GENERAL_LEGATUS.md)
Użytkownik zwrócił uwagę, że dokumentacje specyficzne dla modułów nie były aktualizowane ani egzekwowane przez audyt_spojnosci.py. Nakazano audyt wszystkich dokumentów z indeksu.

### 2026-06-30 — Archiwizacja bez przeczytania pliku prowadzi do utraty ważnych danych
ARSENAL_IMPERIUM (zweryfikowany katalog ~220 narzędzi) i WZORZEC_DNSS (referencja architektury) zostały błędnie zarchiwizowane. Wymusiło to dodanie Zasady Archiwizacji do CLAUDE.md.

### 2026-06-30 — DeepSeek zawyża możliwości – weryfikacja przez deep-research
Wiele twierdzeń DeepSeek z Zbior_wskaznikow_i_strategi okazało się błędnych lub przesadzonych. Zweryfikowano zewnętrznymi źródłami – system musi opierać się na mierzonych faktach (Prawo XVI).

### 2026-06-30 — Zbyt sztywne progi powodują martwe neurony
BB Squeeze 4%→2.5%, RSI Div delta 2.0→0.3, Bart Pattern 30%→10% – neurony zwracały 100% NEUTRAL. Po korekcie zaczęły generować sygnały.

### 2026-06-30 — Golden Cross w IMPERIUM to wariant EMA
Strategia ZŁOTY ORZEŁ używa EMA 50/200, nie kanonicznego SMA. Zapisano w dokumentacji jako wariant EMA. Wyjaśniono brak aktywacji na DOGE (death cross w całym oknie backtestu).

### 2026-06-30 — Filtr kara w baza.py: wyciszone filtry nie karzą
Gdy n_akt_f==0 (wszystkie neurony FILTR wyciszone), strategia otrzymywała karę 0.5. Poprawiono na 1.0 – neuron FILTR nieobecny nie powinien karać (Prawo XV).

### 2026-06-30 — Audyt źródła pure-Python w Bramie: brakowało _PURE_PYTHON_INDICATORS
Wszystkie wskaźniki w Bramie miały źródło TA-Lib. Dodano zbiór _PURE_PYTHON_INDICATORS (11 wskaźników) i warunek SOURCE_TAG_PY w compute(). Naprawiono rozróżnienie źródła dla wskaźników własnych.

### 2026-06-30 — Naprawiono ImportError w legatus.py
Przy bezpośrednim uruchomieniu legatus.py występował błąd względnego importu z .mikro_neuron. Rozwiązano przez try/except: próbuje import względny, w razie błędu przechodzi na absolutny.

### 2026-06-30 — KalkulatorLewara używa pewnosc_agregatu – błąd strukturalny
KalkulatorLewara pobiera pewnosc_agregatu z Legatusa, ale ta wartość jest zawsze ~1.0, więc leverage jest maksymalny. Należy oddzielić pewność agregatu od wielkości pozycji lub wprowadzić Namiestnika.

### 2026-06-30 — pewnosc_agregatu ≈ 1.0 – główna przyczyna strat
Stała wartość pewności bliska 1.0 prowadzi do maksymalnego lewara w KalkulatorzeLewara, co powoduje ciasne stop-lossy i wiele małych strat. To fundamentalny błąd w agregacji – nie ma zróżnicowania sygnałów.

### 2026-06-30 — W6 milczące pominięcie przy braku 'Stan na:'
Audyt W6 nie raportował błędu gdy brak 'Stan na:'. Dodano else skutkujący błędem oraz rozszerzono regex na markdown.

### 2026-06-30 — Proces deduplikacji neuronów
Podczas skanowania agent otrzymał instrukcję deduplikacji, co pozwoliło osiągnąć ostateczną liczbę 261 unikalnych neuronów zamiast potencjalnie większej liczby powtórzeń.

### 2026-06-30 — Push wymaga uprawnień Read & Write
Błąd 403 przy push do GitHub oznacza, że sesja Claude nie ma uprawnień zapisu do repozytorium. Konieczna zmiana uprawnień w GitHub Settings/Installations.

### 2026-06-30 — Push zablokowany przez 403 - brak uprawnień
Środowisko Claude Code web nie ma uprawnień do pushowania do repozytorium IMPERIAL-MESH-VORTEX (błąd 403). Wymagane skonfigurowanie GitHub App Claude Code z dostępem Read & Write w github.com/settings/installations.

### 2026-06-30 — Higuchi Fractal Dimension wymaga pełnej serii – niemożliwy w Brama
D≈1.0 = trending, D≈2.0 = ranging/chaotic, D≈1.5 = random walk. Wymaga min. 50 świec do obliczenia – nie da się zredukować do pojedynczej wartości Brama. Uzasadnia wyjątek Prawa I dla Exploratores.

### 2026-06-30 — Konieczność audytu dokumentacji przed dalszym rozwojem
Użytkownik zwrócił uwagę, że dokumentacja nie jest aktualizowana podczas implementacji wizji; nakazał audyt wszystkich dokumentów z INDEKS_IMPERIUM względem kodu i dodanie egzekucji w narzędziu audytu.

### 2026-06-30 — Kruchość hardcodowanych liczników neuronów w testach
Wprowadzenie 47. neuronu złamało testy z hardcoded 46. Konieczne dynamiczne wykrywanie liczby neuronów lub automatyczne generowanie testów.

### 2026-06-30 — Normalizacja interwałów w strategiach
Błąd: 5m.upper() -> '5M' zamiast 'M5'. Dodano funkcję _normalizuj_interwal w baza.py mapującą formaty (5m->M5, 1h->H1 itd.) aby backtesty filtr/strategia działały poprawnie.

### 2026-06-30 — Backtest Arena: conservative SL gdy obie bariery w jednym barze
Jeśli w jednej świecy osiągnięto zarówno TP jak i SL, wynikiem jest SL (konserwatywnie).

### 2026-06-30 — Kategoria S zarezerwowana dla SMC/Struktura
Kategoria S jest już używana przez strukturalne neurony SMC, więc nie można jej użyć dla Sentiment.

### 2026-06-30 — Halucynacje w linkach IMV: defensywne repo i anegdoty
Po weryfikacji ~320 linków przez 3 równoległych agentów okazało się, że core tech stack jest realny, ale część referencji do defensywnych repozytoriów i legend tradingowych była halucynacjami. Zapisano w ARSENAL_IMPERIUM.md.

### 2026-06-30 — Błąd loadera po reorganizacji na strukturę rzymską
Po przeniesieniu modułów do folderów rzymskich (fundament, legiony itp.), loader w pierwy_zwiadowca.py szukał plików po starych nazwach we własnym folderze. Naprawiono przez zmianę na ścieżki względne z importlib.util.spec_from_file_location.

### 2026-06-30 — Signal Signature – struktura sygnału
Każdy sygnał w systemie IMV ma pola: confidence, adversary_confidence, final_confidence, source, reasons. To standard dla wszystkich modułów – umożliwia filtrowanie i debatę senatorską.

### 2026-06-30 — DeepSeek API – endpoint i bezpieczeństwo klucza
DeepSeek API jest kompatybilny z OpenAI (base_url: https://api.deepseek.com/v1). Klucz API musi być wyłącznie w zmiennych środowiskowych, nigdy w kodzie ani czacie.

### 2026-06-30 — Błąd cross-module loader po reorganizacji folderów
Po przeniesieniu modułów do struktury rzymskiej, loader szukał plików po starych nazwach. Naprawiono przez aktualizację ścieżek względnych w pierwszym_zwiadowca.py.

### 2026-06-30 — Separacja Kingdom Pixel od Imperium
Mieszanie zasad Kingdom Pixel (79 Zasad) z Imperium powodowało chaos. Rozwiązanie: Imperium ma własne 14 Praw, Kingdom Pixel jest archiwizowany i nigdy nie modyfikowany.

### 2026-06-30 — klasyfikuj_rezim() zwraca tylko 4 stany, brak TREND_WEAK/PANIC/ON-CHAIN_BULLISH/SMC_ACTIVE
Funkcja klasyfikacji reżimu ograniczona do TREND_STRONG, RANGING, VOLATILE, NORMAL. Brakuje stanów przewidzianych w dokumentacji.

### 2026-06-30 — Neurony martwe: XII-07, X-12, A-05 (100% NEUTRAL)
Trzy neurony (RSI_14 trend, BB_UPPER, CLOSE_PREV) wykazały 100% NEUTRAL w analizie 500-barowej. Wymagają diagnostyki lub wyłączenia.

### 2026-06-30 — Bug W7 audytu fałszywie flaguje URL z .md w domenie
W7 audyt markerował zewnętrzne URL zawierające '.md' w domenie (np. www.mdpi.com) jako martwe linki, blokując commit. Naprawiono przez dodanie warunku pomijającego zewnętrzne protokoły (http/https/mailto/ftp) na początku href.

### 2026-06-30 — Synchronizacja liczników w testach przy dodawaniu neuronów
W-053 dodał 47. neuron (H-01), ale testy miały zakodowane 46 – konieczność aktualizacji hardcoded wartości w test_integracja.py. Lekcja: każda zmiana liczby neuronów wymaga przeglądu testów.

### 2026-06-30 — Audyt dokumentacji wymaga egzekwowania
Użytkownik nakazał: przed dalszymi wdrożeniami należy zaktualizować wszystkie dokumenty z INDEKS_IMPERIUM i dodać ich sprawdzanie do audyt_spojnosci.py. Obecnie sprawdzane tylko 7 z ~32 plików.

### 2026-06-30 — Dekorelacja V-13 i V-14 potwierdza dywersyfikację
Korelacja między NeuronChoppiness (V-14) a poprzednim wskaźnikiem zmienności |r|=0.05–0.27, co spełnia Prawo XVI (unikamy redundancji).

### 2026-06-30 — Niezgodność stanu MANIFEST z kodem
7 neuronów oznaczonych jako aktywne w MANIFEST_KODU.md, ale w kodzie miały DOSTEPNY=False. Poprawiono oznakowanie na 'wyciszony'.

### 2026-06-30 — Znalezione 2 neurony sieroty w mikro_neuron.py
NeuronStochRSI i NeuronFundingRate znajdowały się poza rojem neuronów, nie były importowane przez rejestr. Zostały przeniesione do odpowiednich plików.

### 2026-06-30 — Wartości mocków muszą mieścić się w zakresach detekcji neuronów
Podczas tworzenia testów okazało się, że mocki muszą precyzyjnie trafiać w progi neuronów (np. FUNDING_RATE > 0.001, LONG_SHORT_RATIO między 0 a 1). Niewłaściwe wartości powodują fałszywe wyniki.

### 2026-06-30 — Brak pola kategoria na SygnalNeuronu uniemożliwiał agregację wag reżimu
Pole 'kategoria' nie istniało w SygnalNeuronu, przez co WAGI_REZIMU były martwym kodem. Dodano pole i przekazywanie z KATEGORII neuronu – teraz wagi reżimu działają poprawnie.

### 2026-06-30 — Brak Stan na: w W6 to błąd, nie pominięcie
Audyt spojności W6 milcząco pomijał bloki bez 'Stan na:'. Dodano jawne else zgłaszające błąd. RegExp rozszerzony o markdown `**Stan na:**`.

### 2026-06-30 — Błąd edycji README z powodu niedopasowania tekstu
Próba edycji pliku README przez narzędzie `edit` nie powiodła się, ponieważ szukany fragment nieznacznie różnił się od faktycznej treści. Rozwiązanie: ponowne odczytanie pliku i użycie dokładnego tekstu.

### 2026-06-30 — Utrata potencjału: Klucznik ignorowany przez Dyrygenta
Prawo XV: Klucznik obliczał strategie, ale Dyrygent ich nie używał. Naprawiono przez dodanie trybów uwzględniających strategię.

### 2026-06-30 — API key tylko w zmiennych środowiskowych
Klucz API DeepSeek nie może być umieszczany w kodzie ani w czacie, tylko w environment variable (setx). Bezpieczeństwo.

### 2026-06-30 — Prawo XV: nie dodawać neuronów z niedostępnym API
Potwierdzono zasadę, że neurony wymagające nieistniejącego API zawsze zwracają NEUTRAL. W tej sesji dodano tylko neurony korzystające z dostępnych wskaźników (Donchian, RSI, BB).

### 2026-06-30 — Bezpieczeństwo klucza API DeepSeek – tylko env vars
Klucz API DeepSeek NIGDY nie może być w kodzie ani w czacie. Powinien być przechowywany w zmiennych środowiskowych. Kod w PLAN_DEEPSEEK.md zawiera placeholder do zastąpienia.

### 2026-07-10 — BIB-032 O'Hara – OCR garbage, nieindeksowany
Książka w formacie skanowanych obrazów PDF – OCR generuje śmieci. Zgodnie z Prawem I (zero fabricacji) nie została włączona do RAG.

### 2026-07-10 — Regime-stale bug – problem branżowy z pamięcią niezależną od reżimu
Odkryto, że konkurencyjne systemy pamięci nie uwzględniają reżimu rynku, co powoduje wyciąganie nieodpowiednich lekcji (np. z hossy podczas bessy). Nasza implementacja Pamięci Reżimowej rozwiązuje to przez wymiar regime_match w scoringu.

### 2026-06-30 — Naprawiono ImportError w legatus.py przez try/except
Relatywny import z .mikro_neuron powodował błąd przy bezpośrednim uruchomieniu. Rozwiązanie: try/except z importem absolutnym jako fallback. Wzorzec do powielenia w nowych modułach.

### 2026-06-30 — TA-Lib wymagany przez Bramę Kalkulatora
Brama Kalkulatora celowo odmawia startu bez TA-Lib (Prawo I). Na Windows 2026 pip install TA-Lib działa, fallback: wheels z github.com/cgohlke/talib-build.

### 2026-06-30 — Bug: __pycache__ śledzone w git
Po kompilacji brama_kalkulatora.py, pliki cache zostały przypadkowo commitowane. Naprawiono przez git rm i dodanie .gitignore.

### 2026-06-30 — VPIN neuron nigdy nie jest kierunkowy
NeuronToxicFlow (Z-01) zawsze zwraca NEUTRAL kierunek. Jego rola to tylko tłumienie roju przez pewnosc_przeciwnika gdy VPIN>0.7. Nigdy nie głosuje na stronę.

### 2026-06-30 — Interval normalization bug: '5m'.upper() ≠ 'M5'
Strategie używają formatu 'M5', a interwał z backtestu po .upper() daje '5M'. Naprawiono przez _normalizuj_interwal() w baza.py konwertujące '5m'→'M5', '1h'→'H1' itd.

### 2026-06-30 — Brama Kalkulatora wymaga TA-Lib do startu
CalculatorGateway celowo odmawia startu bez TA-Lib (Prawo I - Zero halucynacji). Każde obliczenie logowane z SHA-256 audit stamp (Prawo XIII).

### 2026-06-30 — Słabość ręcznego parametru reżimu
Przetestowano 3 scenariusze rynkowe — system wymaga automatycznego klasyfikatora reżimu, bo ręczne ustawianie jest zawodne i nie skalowalne.

### 2026-06-30 — Audyt W6: brak Stan na = błąd, markdown tolerowany
Dodano else dla braku 'Stan na:'. Regex toleruje **Stan na:** data.

### 2026-06-30 — HA doji: strict > zamiast >=
HA_BULL = c > o (nie >=) — doji neutralny, nie byczy.

### 2026-06-30 — Format Katalogu Strategii
ID: [LEGION]-[STYL]-[NUM] (np. X-SC-001). Style: TR/RV/BK/RG/SC/MC/LV/HY. Każda strategia ma: Neurony WEJŚCIE, FILTR, WYJŚCIE, Dźwignia, R:R, Status.

### 2026-06-30 — Dynamiczna dźwignia od pewności i reżimu
pewnosc <0.55→0x, <0.65→2x, <0.75→5x, <0.85→10x, <0.92→15x, >=0.92→20x. Mnożniki reżimu: VOLATILE×0.5, PANIC×0.1, RANGING×0.7, TREND_STRONG×1.2.

### 2026-06-30 — Klucznik ignorowany przez Dyrygenta (Prawo XV)
Dyrygent nie używał wyników Klucznika (strategii) — kierunek i pewność pochodziły wyłącznie z neuronów. Naprawiono: dodano logikę trybów (agregat/filtr/strategia) uwzględniającą DopasowanieStrategii.

### 2026-06-30 — Bug: neuron zwraca NEUTRAL gdy brak danych w BramaKalkulatora
MikroNeuron.interpretuj() zwraca SygnalNeuronu z wartoscia NEUTRAL jesli wskaznik nie istnieje w dict Brama. To powoduje ciche bledy w strategiach - nalezy dodac walidacje i warning.

### 2026-06-30 — DeepSeek API klucz NIGDY w kodzie ani w czacie
Zasada bezpieczeństwa: klucz DeepSeek API musi być tylko w zmiennych środowiskowych. W kodzie użyto [ZREDAGOWANO] jako placeholder. Dotyczy to wszystkich plików w Imperium.

### 2026-06-30 — Zasada symbiozy zamiast zero duplikatów
Moduły mogą być wielofunkcyjne, jeśli każdy pokrywa INNY aspekt (np. 4 moduły wielorybów każdy na inne dane). Złe = 5 modułów czytających ten sam kanał. Test: 'Co unikalnego wnosi ten moduł?'

### 2026-06-30 — OpenAlice i Hermes Agent to realne narzędzia
Zweryfikowano, że OpenAlice (4600★ GitHub) i Hermes Agent (Nous Research, 200+ LLM backends) istnieją i są aktywnymi projektami. Wcześniejsze oznaczenie jako 'niezweryfikowane' było błędne.

### 2026-06-30 — Prawo XV: Bez martwych głosów – neuron bez API zawsze NEUTRAL
Nie dodawać neuronów wymagających niedostępnego API – będą zawsze NEUTRAL, co psuje agregację. Zweryfikowano wszystkie nowe neurony pod kątem dostępności wskaźników.

### 2026-06-30 — Prawo XIX: Kod jest Prawem – klucze katalogu muszą zgadzać się z kodem
Audyt ujawnił rozbieżności między KATALOG_NEURONOW.md a kodem. Utworzono MAPA_KLUCZY.md jako kanoniczne mapowanie. Klucznik weryfikuje DOSTEPNY=True.

### 2026-06-30 — NeuronPumpDetect Z-02: 3 warunki OHLCV
Warunek 1: VOLUME/VOLUME_MA20 w [1.5, 4.0]; Warunek 2: (HIGH-LOW)/ATR_14 < 0.75; Warunek 3: OBV > OBV_EMA_20*(1+0.005). Siła = 0.55+0.30*(vol*0.4+zakr*0.3+obv*0.3). Kierunek LONG.

### 2026-06-30 — Meta-gate defensive neurons zawsze NEUTRAL kierunek
Neurony obronne (Z-01, N-01, H-01, OC-05) ustawiają pewnosc_przeciwnika zamiast kierunku, wywołują s.policz_finalna() — to wzorzec dla wszystkich bram obronnych.

### 2026-07-10 — Ważenie IC podnosi rój ponad 50% na każdej parze OOS
Wynik B (ważony IC) = 51.8% globalnie, bije A o +3.6pp i przekracza 50% na KAŻDEJ z 5 par OOS. Potwierdza hipotezę B: wąskie gardło = agregacja.

### 2026-07-10 — Równa waga = 48.2% odtwarza diagnozę triady 48.3%
Pomiar hipotezy B na 5 parach 4h OOS daje globalnie 48.2% dla równej wagi, co odtwarza diagnozę triady 48.3% co do promila — walidacja pomiaru.

### 2026-07-10 — Pełny backtest 18k barów × 5 par pada na timeout
Pełny przebieg 18k barów × 5 par jest za wolny i przekracza limit 600s. Potwierdza to ZASADĘ ANALIZY CZĄSTKOWEJ: trzeba cap barów + cząstkowanie z zapisem do areny.

### 2026-06-30 — 12/17 bloków strategii miało błędne klucze w KATALOGU
Stare klucze projektowe (np. XII-08) nie istniały w kodzie. Audyt W9 wykrywa obce klucze w blokach zaimplementowanych strategii. Wszystkie 17 zsynchronizowane.

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
