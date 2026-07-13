# PAMIĘĆ SESJI — W-360

> **Cel:** trwała pamięć między sesjami — mapa podpięć, lekcje, priorytety.
> Aktualizuj PO każdej sesji. Wczytywana przez SessionStart hook.
> Indeksowana w RAG jako korpus `pamiec` (plik .md → `bibliotheca_ulpia/dane/`).

## Ostatnia aktualizacja: 2026-06-30

---

## 🗺️ PEŁNA MAPA PODPIĘĆ DO LOKALA (Cezar, 2026-06-21)

### A. MCP Servers dla Claude Code

| ID | Serwer | Status | Priorytet | Co daje |
|----|--------|--------|-----------|---------|
| A1 | **GitHub MCP** | ✅ działa (cloud) | — | PR, issues, CI |
| A2 | **Memory MCP** 💎 | ✅ natywny (imperium/biblioteki/pamiec_sesji.py + hook) | — | Trwała pamięć między sesjami (ROZWIĄZUJE W-360) |
| A3 | **Bibliotheca-RAG MCP** 💎 | ✅ zbudowany (W-360 RAG v2) | — | Szukaj w 42 książkach + encyklopedii + docs (indeks do przebudowy po BIB-033..042) |
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

### 2026-06-30 — TA-Lib wymagany przez Bramę Kalkulatora
Brama Kalkulatora celowo odmawia startu bez TA-Lib (Prawo I). Na Windows 2026 pip install TA-Lib działa, fallback: wheels z github.com/cgohlke/talib-build.

### 2026-06-30 — Mieszanie zasad Kingdom Pixel z Imperium = chaos
Kopiowanie 79 zasad z Kingdom Pixel do Imperium powodowało konflikt. Rozwiązanie: stworzenie 14 Praw Imperium od zera, bez kontaminacji.

### 2026-06-30 — Bug: loader nie działa po zmianie struktury folderów
Po przeniesieniu modułów z płaskiej struktury do folderów rzymskich, pierwszy_zwiadowca.py szukał plików po starych nazwach. Naprawiono przez użycie względnych ścieżek do nowych lokalizacji.

### 2026-06-30 — 403 Push Permission Error
Początkowe pushy nie działały z powodu błędnych uprawnień GitHub App. Użytkownik naprawił uprawnienia, push ostatecznie powiódł się.

### 2026-06-30 — Bug: __pycache__ śledzone w git
Po kompilacji brama_kalkulatora.py, pliki cache zostały przypadkowo commitowane. Naprawiono przez git rm i dodanie .gitignore.

### 2026-06-30 — Bug: cross-module loader po zmianie struktury folderów
Po przeniesieniu modułów z płaskiej struktury do folderów rzymskich, loader w pierwszy_zwiadowca.py szukał starych nazw. Naprawiono przez użycie względnych ścieżek.

### 2026-06-30 — OpenAlice i Hermes Agent zweryfikowane jako realne narzędzia
OpenAlice (4600★ GitHub) i Hermes Agent (Nous Research) to rzeczywiste narzędzia AI tradingowe, a nie halucynacje. Zostały dodane do ARSENAL_IMPERIUM.md jako zweryfikowane.

### 2026-06-30 — Permutation Entropy >0.85 = chaos → NEUTRAL
NeuronPermEntropy (N-01): PE>0.85 → NEUTRAL 'chaos', PE<0.65 → podąża za mikro-ruchem, mid → NEUTRAL niska pewność. Meta-gate nie głosuje kierunkowo przy wysokiej entropii.

### 2026-06-30 — VPIN neuron nigdy nie jest kierunkowy
NeuronToxicFlow (Z-01) zawsze zwraca NEUTRAL kierunek. Jego rola to tylko tłumienie roju przez pewnosc_przeciwnika gdy VPIN>0.7. Nigdy nie głosuje na stronę.

### 2026-06-30 — kapital_calkowity = free + locked margin (true equity)
BezpiecznikKrzywejKapitalu używał tylko wolnego kapitału, co fałszywie triggerowało REDUCED przy otwarciu pozycji (margin przechodzi free→locked). Poprawiono: kapital_calkowity = self.kapital + sum(p.kapital_zablokowany).

### 2026-06-30 — Interval normalization bug: '5m'.upper() ≠ 'M5'
Strategie używają formatu 'M5', a interwał z backtestu po .upper() daje '5M'. Naprawiono przez _normalizuj_interwal() w baza.py konwertujące '5m'→'M5', '1h'→'H1' itd.

### 2026-06-30 — CME Gap traci znaczenie od maja 2026
CME uruchamia handel 24/7 od 29 maja 2026, co eliminuje klasyczny gap weekendowy. Strategia CME Gap staje się historyczna – należy ją oznaczyć jako IMV-EXP i przygotować archiwizację.

### 2026-06-30 — TA-Lib blokerem dla 9 modułów
Brak TA-Lib uniemożliwia uruchomienie 9 modułów systemu. Wymagane pip install TA-Lib. Zidentyfikowano jako jedyny zewnętrzny bloker.

### 2026-06-30 — TA-Lib blokerem 9 modułów
Brak TA-Lib (pip install TA-Lib) uniemożliwia uruchomienie 9 modułów systemu. To najważniejsza zależność do odblokowania.

### 2026-06-30 — Brama Kalkulatora wymaga TA-Lib do startu
CalculatorGateway celowo odmawia startu bez TA-Lib (Prawo I - Zero halucynacji). Każde obliczenie logowane z SHA-256 audit stamp (Prawo XIII).

### 2026-06-30 — TA-Lib na Windows 10: pip install działa w 2026
Współczesna instalacja TA-Lib na Windows jest prostsza — pip install TA-Lib często działa, fallback do wheeli z github.com/cgohlke/talib-build.

### 2026-06-30 — Mieszanie zasad Kingdom Pixel z Imperium źródłem chaosu
Root cause chaosu w poprzedniej sesji: próba kopiowania 79 zasad z Kingdom Pixel do Imperium. Rozwiązanie: stworzenie od nowa 14 Praw Imperium, zero cross-kontaminacji.

### 2026-06-30 — Bug: loader szukał starych nazw po reorganizacji folderów
Po przeniesieniu modułów do struktury rzymskich dzielnic, pierwszy_zwiadowca.py szukał plików po starych nazwach (np. CORE-006_CalculatorGateway.py) w swoim folderze. Naprawiono przez aktualizację ścieżek względnych.

### 2026-06-30 — Słabość ręcznego parametru reżimu
Przetestowano 3 scenariusze rynkowe — system wymaga automatycznego klasyfikatora reżimu, bo ręczne ustawianie jest zawodne i nie skalowalne.

### 2026-06-30 — Audyt W6: brak Stan na = błąd, markdown tolerowany
Dodano else dla braku 'Stan na:'. Regex toleruje **Stan na:** data.

### 2026-06-30 — Pre-commit: stash isolation dla staged
Dodano git stash push --keep-index --include-untracked + trap przywracający working tree. Testy działają na staged, nie na working tree.

### 2026-06-30 — HA doji: strict > zamiast >=
HA_BULL = c > o (nie >=) — doji neutralny, nie byczy.

### 2026-06-30 — Diagnostyka: 1 próbka nie dowodzi martwoty
Detekcja stałej serii wymaga len(v) >= 2. Pojedyncza próbka trafia do pary_niedostateczne_dane.

### 2026-06-30 — Czytnik symbol z nazwy pliku: split('_')[-2]
Fallback symbol z nazwy pliku Binance_BTCUSDT_1h dawał BINANCE przez split('_')[0]. Poprawiono na [-2].

### 2026-06-30 — Ulcer Index warmup: period zamiast period+1
Funkcja _py_ulcer() używa c[-period:] więc potrzebuje tylko period próbek, a nie period+1. Poprawiono warunek warmup.

### 2026-06-30 — SkalowanieFrakcjaDD: ciągłe skalowanie pozycji od DD
frakcja = max(min_frakcja, min(1.0, 1.0 - dd/prog_max)). Domyślnie prog_max=20%, min_frakcja=10%. Wpływa na rozmiar pozycji przez frakcja_dd w PlanPozycji.

### 2026-06-30 — Wash Trading Detection: Benford chi² + round-number clustering
Wash score = sqrt(benford_score * rounding_score). Benford: chi2_obs/20.09 capped 1.0. Rounding: (round_frac-0.20)/0.20 clamped [0,1]. Prog ostrzeżenia 0.35, silny 0.65.

### 2026-06-30 — CalcResult vs float w testach HURST_DFA
HURST_DFA zwraca obiekt CalcResult, nie float. Należy używać r.value, nie r.

### 2026-06-30 — Pewność vs pewność_finalna w testach
W teście Z-02 asercja musi być na s.pewnosc (>=0.55), a nie s.pewnosc_finalna, bo ta uwzględnia WAGĘ.

### 2026-06-30 — Format Katalogu Strategii
ID: [LEGION]-[STYL]-[NUM] (np. X-SC-001). Style: TR/RV/BK/RG/SC/MC/LV/HY. Każda strategia ma: Neurony WEJŚCIE, FILTR, WYJŚCIE, Dźwignia, R:R, Status.

### 2026-06-30 — Zasada 2% kapitału i R:R minimum 1:2
Max ryzyko 2% kapitału na transakcję lewarowaną. Wymagany stosunek Risk:Reward minimum 1:2. Wyjątek: Druckenmiller Mode (pewnosc >0.92) pozwala na 5% kapitału i dźwignia ×1.5.

### 2026-06-30 — Dynamiczna dźwignia od pewności i reżimu
pewnosc <0.55→0x, <0.65→2x, <0.75→5x, <0.85→10x, <0.92→15x, >=0.92→20x. Mnożniki reżimu: VOLATILE×0.5, PANIC×0.1, RANGING×0.7, TREND_STRONG×1.2.

### 2026-06-30 — Wzór ceny likwidacji LONG/SHORT
LONG: Entry * (1 - 1/Leverage + 0.005). SHORT: Entry * (1 + 1/Leverage - 0.005). Stop-loss = 50% drogi do likwidacji. OPLATA_UTRZYMANIA = 0.005 (Binance/MEXC).

### 2026-06-30 — ImportError w legatus.py przy uruchomieniu bezpośrednim
Relative import from .mikro_neuron fails gdy plik uruchamiany bezpośrednio. Rozwiązanie: try/except z fallbackiem do from mikro_neuron import.

### 2026-06-30 — Format CSV CryptoDataDownload wymaga specjalnego czytnika
Pliki CSV z CDD mają pierwszy wiersz URL, nagłówek w drugim, dane malejąco, timestamp w ms. Kolumna wolumenu bazowego to 'Volume' (nie 'Volume USDT'). Czytnik CSV musi to obsługiwać.

### 2026-06-30 — Klucznik ignorowany przez Dyrygenta (Prawo XV)
Dyrygent nie używał wyników Klucznika (strategii) — kierunek i pewność pochodziły wyłącznie z neuronów. Naprawiono: dodano logikę trybów (agregat/filtr/strategia) uwzględniającą DopasowanieStrategii.

### 2026-06-30 — RSI Div delta 2.0 zbyt wysoka dla daily
Na sąsiednich daily RSI rzadko zmienia się o >2 pkt. Zmieniono próg z 2.0 na 0.3.

### 2026-06-30 — Bug: neuron zwraca NEUTRAL gdy brak danych w BramaKalkulatora
MikroNeuron.interpretuj() zwraca SygnalNeuronu z wartoscia NEUTRAL jesli wskaznik nie istnieje w dict Brama. To powoduje ciche bledy w strategiach - nalezy dodac walidacje i warning.

### 2026-06-30 — Slabosc: reczny parametr rezimu w strategiach
Testy na 3 scenariuszach rynkowych wykazaly, ze reczne podawanie rezimu (NORMAL, TREND_STRONG itp.) jest slabym punktem. Nastepny krok: automatyczny klasyfikator rezimu.

### 2026-06-30 — DeepSeek API klucz NIGDY w kodzie ani w czacie
Zasada bezpieczeństwa: klucz DeepSeek API musi być tylko w zmiennych środowiskowych. W kodzie użyto [ZREDAGOWANO] jako placeholder. Dotyczy to wszystkich plików w Imperium.

### 2026-06-30 — JG z GUSI Pro/Omni-Wave to ten sam JG co DNSS
Odkryto, że 'R.G. JG' (twórca GUSI Pro, Omni-Wave w bazie wskaźników) to prawdopodobnie ta sama osoba co twórca systemu DNSS (79 agentów). Potwierdza to linię Calculator Pattern.

### 2026-06-30 — Zasada symbiozy zamiast zero duplikatów
Moduły mogą być wielofunkcyjne, jeśli każdy pokrywa INNY aspekt (np. 4 moduły wielorybów każdy na inne dane). Złe = 5 modułów czytających ten sam kanał. Test: 'Co unikalnego wnosi ten moduł?'

### 2026-06-30 — OpenAlice i Hermes Agent to realne narzędzia
Zweryfikowano, że OpenAlice (4600★ GitHub) i Hermes Agent (Nous Research, 200+ LLM backends) istnieją i są aktywnymi projektami. Wcześniejsze oznaczenie jako 'niezweryfikowane' było błędne.

### 2026-06-30 — Kategoria Z już zajęta przez zagrożenie
Kategoria Z (Zagrożenie) zarezerwowana dla VPIN meta-bramy (Z-01) i PumpDetect (Z-02). Sentiment nie może użyć Z.

### 2026-06-30 — Prawo XV: Bez martwych głosów – neuron bez API zawsze NEUTRAL
Nie dodawać neuronów wymagających niedostępnego API – będą zawsze NEUTRAL, co psuje agregację. Zweryfikowano wszystkie nowe neurony pod kątem dostępności wskaźników.

### 2026-06-30 — Prawo XIX: Kod jest Prawem – klucze katalogu muszą zgadzać się z kodem
Audyt ujawnił rozbieżności między KATALOG_NEURONOW.md a kodem. Utworzono MAPA_KLUCZY.md jako kanoniczne mapowanie. Klucznik weryfikuje DOSTEPNY=True.

### 2026-06-30 — NeuronPumpDetect Z-02: 3 warunki OHLCV
Warunek 1: VOLUME/VOLUME_MA20 w [1.5, 4.0]; Warunek 2: (HIGH-LOW)/ATR_14 < 0.75; Warunek 3: OBV > OBV_EMA_20*(1+0.005). Siła = 0.55+0.30*(vol*0.4+zakr*0.3+obv*0.3). Kierunek LONG.

### 2026-06-30 — Triple Barrier: SL wygrywa przy jednoczesnym trafieniu TP i SL
W metodzie oznacz_bariera, jeśli TP i SL są trafione w tej samej świecy, wygrywa SL (konserwatywnie). timeliness = 1.0 - (bar_nr-1)/max(max_bary-1, 1).

### 2026-06-30 — Meta-gate defensive neurons zawsze NEUTRAL kierunek
Neurony obronne (Z-01, N-01, H-01, OC-05) ustawiają pewnosc_przeciwnika zamiast kierunku, wywołują s.policz_finalna() — to wzorzec dla wszystkich bram obronnych.

### 2026-07-10 — Ważenie IC podnosi rój ponad 50% na każdej parze OOS
Wynik B (ważony IC) = 51.8% globalnie, bije A o +3.6pp i przekracza 50% na KAŻDEJ z 5 par OOS. Potwierdza hipotezę B: wąskie gardło = agregacja.

### 2026-07-10 — Równa waga = 48.2% odtwarza diagnozę triady 48.3%
Pomiar hipotezy B na 5 parach 4h OOS daje globalnie 48.2% dla równej wagi, co odtwarza diagnozę triady 48.3% co do promila — walidacja pomiaru.

### 2026-07-10 — Katalog scratchpad nie istniał — redirect padł
Przy uruchamianiu biegów równoległych katalog scratchpad nie istniał, co spowodowało ciche niepowodzenie zapisu. Po utworzeniu katalogu bieg działa poprawnie.

### 2026-07-10 — Pełny backtest 18k barów × 5 par pada na timeout
Pełny przebieg 18k barów × 5 par jest za wolny i przekracza limit 600s. Potwierdza to ZASADĘ ANALIZY CZĄSTKOWEJ: trzeba cap barów + cząstkowanie z zapisem do areny.

### 2026-06-30 — 12/17 bloków strategii miało błędne klucze w KATALOGU
Stare klucze projektowe (np. XII-08) nie istniały w kodzie. Audyt W9 wykrywa obce klucze w blokach zaimplementowanych strategii. Wszystkie 17 zsynchronizowane.

### 2026-06-30 — Binance depth zwraca stringi a nie floaty
L2 order book od Binance ma ceny i wolumeny jako stringi. Dodano float(b[1]) i float(a[1]) w exp_atmabhan._imbalance().

### 2026-06-30 — Diagnostyka fałszywie alarmowała martwe neurony
Pary z 1 próbką były klasyfikowane jako 'martwe' (len(set)==1). Dodano wymóg >=2 próbek do detekcji stałej serii. Nowy klucz: pary_niedostateczne_dane.

### 2026-06-30 — Golden Cross: wariant EMA, nie oryginalny SMA
Strategia ZŁOTY ORZEŁ używa EMA50/EMA200, a nie kanonicznego SMA50/SMA200. Odnotowano w katalogu.

### 2026-06-30 — Diagnostyka korelacji: 1 próbka fałszywie uznawana za martwą
len(set)==1 dla 1 próbki dawało false positive. Wymagane ≥2 próbki do detekcji stałej serii.

### 2026-06-30 — Błąd warmup Accelerator: slow+sma_ac+1
Funkcja _py_accelerator miała zbędne +1 w warmup, co powodowało off-by-one. Usunięto.

### 2026-06-30 — pewnosc_agregatu ≈ 1.0 to root cause strat
KalkulatorLewara używa pewnosc_agregatu do wyznaczania dźwigni, ale zawsze ≈1.0 → max leverage → ciasne stop lossy → wiele małych strat. To jest pierwotna przyczyna wszystkich strat systemu.

### 2026-07-10 — Recenzent łapie granice brudnych danych i ścieżek awaryjnych
Cubic na PR #118 znalazł kilkanaście realnych bugów w kodzie, który przeszedł mój adversarial przegląd. Wzorzec: łapie to, czego NIE testuję z góry — dane wejściowe nie-string/None/liczba (np. _skroc na co0=int), ścieżki AWARYJNE (fallback hooka gubi wydruk), martwe wzorce po round-tripie przez JSONL, daty/liczby zanieczyszczające miary podobieństwa. Lekcja: przed pushem testować BRUDNE WEJŚCIE i ŚCIEŻKĘ BŁĘDU, nie tylko happy path.

### 2026-06-30 — Prawo I: Neurony nie liczą, Brama liczy
MikroNeurony tylko interpretują gotowe wskaźniki (metoda interpretuj()), nigdy nie obliczają. Obliczenia wykonuje Brama Kalkulatora (TA-Lib). To fundamentalna zasada architektury IMPERIUM.

### 2026-06-30 — Wolumen bazowy: Volume BTC/ETH ≠ Volume USDT
W plikach CDD kolumna 'Volume BTC' lub 'Volume ETH' to wolumen w kryptowalucie, a nie w USDT. Czytnik CSV wykrywa kolumnę zaczynającą się od 'volume' i różną od 'volume usdt' jako bazową.

### 2026-06-30 — Format CryptoDataDownload: linia URL i dane malejąco
Pliki CSV z CryptoDataDownload mają pierwszą linię z URL-em, drugą z nagłówkami, dane są w kolejności malejącej (od najnowszych do najstarszych). Czytnik CSV automatycznie pomija URL i odwraca kolejność na rosnącą.

### 2026-06-30 — Prawo XV: Utrata potencjału Klucznika
Klucznik obliczał strategie, ale Dyrygent je ignorował. Strategie nie wpływały na decyzje. Naprawiono przez dodanie trybów: agregat (ignoruje strategie), filtr (strategia blokuje konflikt), strategia (strategia narzuca kierunek).

### 2026-06-30 — DeepSeek chat zawierał wiele błędnych/przesadzonych twierdzeń
Porównano Zbior_wskaznikow_i_strategi_03.06.2026.md z rzeczywistym repozytorium. Wiele twierdzeń DeepSeek o implementacjach było fałszywych. Zweryfikowano przez deep-research.

### 2026-06-30 — Backtest nie ma lookahead-bias na 4 zbiorach Binance
Zweryfikowano na BTC/ETH 1D (3192 bary) i 1H (76k barów) z CryptoDataDownload. Detektor potwierdza brak przecieku. Sliding window 250 barów jest czysty.

### 2026-06-30 — Kanoniczna liczba neuronów: 299
299 unikalnych kluczy z KATALOG_NEURONOW.md, a nie 261/303/306/328 (stare estymaty). 27 zaimplementowanych w kodzie.

### 2026-06-30 — EXP-12 +106,692% ROI to fantazja/lookahead
Oryginalny Atmabhan ma nierealistyczne wyniki z powodu lookahead bias. Wdrożono ostrzeżenie w docstringu.

### 2026-06-30 — Martwy głos ATR_MULT w EXP-07
EXP-07 miał ATR_MULT=1.5 ale ATR nie był używany w logice. Poprawiono na ATR_MULT=0.15 i faktyczne użycie ATR.

### 2026-06-30 — Bug: testy miały hardcoded 46 neuronów po dodaniu 47.
Po dodaniu H-01 testy integracyjne zawierały stałą 46. Naprawiono na 47 w dwóch miejscach. Lekcja: używać len(rejestr.wszystkie_neurony()) zamiast stałych.

### 2026-06-30 — Hurst-DFA vs R/S: dekorelowane na krypto trendującym
Prawo XVI: DFA i R/S dają nieskorelowane wyniki na trendującym krypto. Potwierdzono empirycznie, że to nie redundancja.

### 2026-06-30 — Yang-Zhang ~14x wydajniejszy od std(close)
Drift-independent OHLC volatility estimator. Potwierdzono empirycznie: ~14x więcej próbek niż close-only std(close) przy tej samej długości okna.

### 2026-06-30 — Yang-Zhang traci 7-14× informacji vs std(close)
Używanie std(close) zamiast estymatora Yang-Zhang (OHLC) marnuje potencjał volatility. Narusza Prawo XV. Należy zastąpić w obliczeniach.

### 2026-06-30 — CME gap edge martwy od 2026-05-29
CME uruchomiło 24/7 kontrakty futures na BTC, co eliminuje weekendowe luki cenowe. Nie implementować jako sygnału live.

### 2026-06-30 — W7 audyt fałszywie flaguje zewnętrzne URL-e z .md w domenie
Reguła W7 w audyt_spojnosci.py błędnie oznaczała linki takie jak www.mdpi.com jako martwe, bo zawierają '.md' w domenie. Naprawiono przez pomijanie URL-i z http/https/mailto.

### 2026-06-30 — Filtr nieobecny nie karze strategii
n_akt_f==0 dawało filtr_frakcja=0.5 karząc strategię. Zmieniono na 1.0 (Prawo XV).

### 2026-06-30 — HA doji neutralny i ATR=0
HA_BULL zmieniono z >= na > (doji neutralny). Przy ATR=0 dodano jawne zera dla HA_MOMENTUM i HA_VOLATILITY_INDEX.

### 2026-06-30 — Diagnostyka korelacji fałszywie martwe przy 1 próbce
1 próbka dawała len(set)==1 uznawane za martwe. Wymóg ≥2 próbek do detekcji stałej serii.

### 2026-06-30 — Pre-commit testował working tree zamiast staged
Pre-commit hook testował cały working tree, nie tylko staged. Dodano git stash push --keep-index + trap przywracający.

### 2026-06-30 — Czytnik CSV błędny symbol z nazwy pliku
split('_')[0] dla Binance_BTCUSDT_1h dawało 'BINANCE' zamiast 'BTCUSDT'. Poprawiono na [-2].

### 2026-06-30 — AC warmup off-by-one
Accelerator Oscillator miał zbędne +1 w warmupie (slow+sma_ac+1). Usunięto nadmiar.

### 2026-06-30 — Błąd warmupu Ulcer Index
Ulcer Index wymagał period+1 zamiast period. Poprawiono na c[-period:] co wymaga tylko period próbek.

### 2026-06-30 — Cross jako EVENT w EXP-11
Cross jako EVENT a nie STATE: EXP-11 sygnalizuje tylko przy świeżym przecięciu, nie na każdym barze gdzie fast>slow.

### 2026-06-30 — HA bez repainting: rekurencyjny HA_Open
Heiken Ashi bez repainting wymaga HA_Open[i] = (HA_Open[i-1] + HA_Close[i-1]) / 2, a nie (Open[-1]+Close[-1])/2. Zaimplementowano w _dodaj_ha().

### 2026-06-30 — Stop-hook git-check.sh blokuje dalszą pracę przy niepushniętym commicie
Hook ~/.claude/stop-hook-git-check.sh uniemożliwia kontynuację sesji, dopóki commit nie zostanie wypchnięty. To wymusza rozwiązanie problemu uprawnień przed dalszą pracą.

### 2026-06-30 — Plik >1MB nie może być wypchnięty przez GitHub MCP jako tekst
Próba pusha pliku IMV v05-07 (1.5MB) przez GitHub MCP nie powiodła się z powodu limitu rozmiaru. Duże pliki wymagają pusha przez git lub osobnego uploadu.

### 2026-06-30 — Push przez git blokowany 403 przy braku uprawnień zapisu
Claude Code w środowisku web nie może wypchnąć commita do repozytorium bez nadania uprawnień Read & Write w ustawieniach GitHub. Błąd 403 jest trwały dopóki użytkownik nie zmieni uprawnień przez github.com/settings/installations.

### 2026-06-30 — Kategoria A przeniesiona z PLANOWANE do AKTYWNE
WAGI_REZIMU_PLANOWANE zmienione z {'A','L','V'} na {'L','V'} — kategoria A jest już w kodzie z neuronami Dywizji Straży. WAGI_REZIMU: A ×2.0 (VOLATILE) i ×3.0 (PANIC).

### 2026-06-30 — kategoria na SygnalNeuronu była brakującym polem dla wag reżimowych
WAGI_REZIMU (TREND_STRONG: T×1.5, PANIC: A×3.0) nie działały, bo SygnalNeuronu nie miał pola kategoria. Dodano pole i propagację z KATEGORIA neuronu.

### 2026-06-30 — Brak *_PREV uniemożliwia detekcję crossoverów
Brama nie dostarczała poprzednich wartości (RSI_PREV, EMA_PREV, MACD_HIST_PREV), przez co neurony crossoverowe były martwe. Naprawiono przez _second_last_valid() i rozszerzenie rejestru Bramy.

### 2026-06-30 — Zombie neurons zwracają NEUTRAL gdy Brama nie dostarcza kluczy
Neurony z DOSTEPNY=False zawsze zwracały NEUTRAL, maskując brak integracji. Wykryto przez Prawo XV. Naprawiono: Roj.zbierz_sygnaly() pomija DOSTEPNY=False, dodano POWOD_NIEDOSTEPNOSCI.

### 2026-06-30 — Martwy głos ATR w Night Turbo
Oryginalny Night Turbo miał ATR zdefiniowany ale nieużywany. Poprawiono: PROG_ATR_MULT = 0.5 faktycznie używa ATR.

### 2026-06-30 — Lookahead bias w SMC Engine
Oryginalny SMC engine używał .shift(-1)/.shift(-2) – patrzenie w przyszłość. Poprawiono w EXP-09: tylko bary[start:n] (przeszłość).

### 2026-06-30 — Cross jako EVENT, nie STATE
EXP-11 sygnalizuje tylko przy świeżym przecięciu (fast>slow AND prev_fast<=prev_slow), a nie na każdym barze gdzie fast>slow.

### 2026-06-30 — True Range: poprawna definicja
True Range = max(H-L, |H-prevC|, |L-prevC|). Poprawiono we wszystkich adoptowanych wskaźnikach (EXP-06..12).

### 2026-06-30 — Prawo I: Zero halucynacji matematycznych
AI nigdy nie oblicza matematyki. Kod (TA-Lib, C) oblicza RSI/EMA/ATR → JSON 'answer key' → AI tylko interpretuje. Brama Kalkulatora nie uruchomi się bez TA-Lib.

### 2026-06-30 — Halucynacje w ARSENAL: defensywne repo i anegdoty
Weryfikacja ~320 linków z IMV wykazała halucynacje w klastrze 'defensywnych repozytoriów GitHub' i anegdot tradingowych. Główny stack technologiczny jest prawdziwy.

### 2026-06-30 — Bug: __pycache__ śledzone w gicie
Po kompilacji brama_kalkulatora.py, pliki __pycache__ zostały przypadkowo commitowane. Naprawiono przez git rm --cached i dodanie .gitignore.

### 2026-06-30 — Bug: loader modułów po reorganizacji folderów
Po przeniesieniu modułów z płaskiej struktury do folderów rzymskich, pierwszy_zwiadowca.py szukał plików po starych nazwach. Naprawiono przez użycie względnych ścieżek (../fundament/brama_kalkulatora.py).

### 2026-06-30 — Bug: mieszanie zasad Kingdom Pixel z Imperium
Mieszanie zasad Kingdom Pixel (79 Zasad) z Imperium powodowało chaos. Rozwiązanie: stworzenie 14 Praw Imperium od zera, bez kopiowania. Kingdom Pixel = archiwum, Imperium = aktywne.

### 2026-06-30 — Kategoria R w WAGI_REZIMU istniała tylko w PANIC
Sentyment (R) miał wagę tylko w trybie PANIC (veto). Dodano mnożniki dla VOLATILE (×1.3), RANGING (×1.2), NORMAL (×1.1), TREND_STRONG (×0.8).

### 2026-06-30 — Bart Pattern threshold 30% Donchian zbyt rzadki
Warunek 30% kanału Donchiana występuje ekstremalnie rzadko. Zmieniono na 10%.

### 2026-06-30 — RSI Div threshold 2.0 zbyt wysoki dla sąsiednich barów daily
Delta RSI między sąsiednimi barami daily rzadko przekracza 2 pkt. Zmieniono na 0.3.

### 2026-06-30 — BB Squeeze threshold 4% zbyt restrykcyjny dla BTC daily
Na dziennych barach BTC typowa szerokość BB to 3-8%, próg 4% był praktycznie nieosiągalny. Zmieniono na 2.5%.

### 2026-07-04 — POTRZEBA CEZARA: wizualizacja live (krytyczne)
Cezar czuje się 'jak dziecko we mgle' — brak podglądu wykresów i wizualizacji live jak zachowuje się Imperium. PRIORYTET: dashboardy/wykresy (equity, cena+wejścia/wyjścia, IC ranking, głosy neuronów na żywo). Każde narzędzie ma mieć wyjście WIZUALNE, nie tylko tekst.

## 🔄 STAN BIEŻĄCY (auto-aktualizuj każdą sesję)

- **Testy:** 1720/1720 ✅ (2026-06-22)
- **Neurony:** 81 (aktywne 75, wyciszone 6) | **Zwiadowcy:** 15 (aktywni 13)
- **Elitarne (Prawo XX):** 18
- **Branch:** `claude/sleepy-fermi-dsdE4`
- **Ostatni commit:** 7a0dbf8 — W-360 Memory MCP natywny (pamiec_sesji.py)
- **Pamięć v2 (2026-06-22):** CRUD lekcji + profil Cezara (USER.md-style) + Kronika Czatu (100 sesji destylatu w repo)
