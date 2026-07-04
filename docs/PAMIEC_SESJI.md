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

### 2026-06-25 — Głęboki audyt przypisania książek: 42/42 pokryte, 4 sieroty naprawione
Cezar zlecił audyt przypisania wszystkich książek do działów. Macierz pokrycia (plik↔dział) wykryła 3 prawdziwe sieroty + 1 brak w Kanonie INDEX. Każdą przeczytano agentem przed przypisaniem (ZPO, nie z tytułu). BIB-001 Patel (978-0-85719-857-0)→MAK (18-letni cykl nieruchomości, MAK 🔲→🚧+esencja)+BAN. BIB-012 Coding Capital (979-8-87385-994-8)→ALG+IMP. BIB-024 Lowe (self-pub ⚠️)→ONC ⭐1 z oznaczeniem ANTYWZORCA (uśrednianie w dół vs Reguła 6%). BIB-005 Blum→dopisany do Kanonu INDEX (był w ONC). Wynik: 42/42, zero sierot. Lekcja metodologiczna: „sierota wg INDEX_MAIOR" ≠ „sierota faktyczna" — sprawdzaj WSZYSTKIE pliki działów, nie tylko Kanon (BIB-005 był w ONC, fałszywie wyglądał na sierotę).

### 2026-06-25 — Kanon 36→42: 6 klasyków → LEW/TRD/PSY/RSK
Cezar wgrał BIB-037..042 (Hull, Schwager, Lefèvre, Bernstein, Taleb, Jorion). Ekstrakcja EPUB + 6 agentów → esencja do działów. ISBN zweryf. (Prawo I; Bernstein/Taleb przez web bo plik Taleba=bundel Incerto). Esencja: Hull — margin call dopłaca do INITIAL nie maintenance, Lehman 31:1, ⚠️ Hull NIE pokrywa crypto perpetual/funding. Schwager — undertrade, korelacja pozycji codziennie (Prawo XVI), proces>wynik. Lefèvre — sit tight, anty-uśrednianie, hope/fear odwrócone, anty-tip=Prawo I. Bernstein — loss aversion uzasadnia twardy HALT + 3 pułapki regresji do średniej. Taleb — magnituda>częstotliwość, survivorship bias→DSR/PBO, katastrofa nieobecna w danych→bezpieczniki ogona. Jorion — Expected Shortfall>VaR dla grubych ogonów krypto, EWMA λ=0.94, backtest VaR strefy Basel. Symbioza 36→42 w 8 plikach.

### 2026-06-25 — Kanon 32→36: 4 książki LLM/agentów → dział MEM
Cezar wgrał BIB-033..036 (Huyen *AI Engineering*, Infante *AI Agents and Applications*, Iusztin&Labonne *LLM Engineer's Handbook*, Alto *Building LLM Powered Applications*). Pełna analiza: ekstrakcja EPUB/AZW3 + 4 równoległe agenty → esencja do MEM §8 (mapa 17 konceptów→kod). Prawo I: zweryfikowano ISBN-y; BIB-034 to **Roberto** Infante (nie Michael), ISBN 978-1-63343-654-1, hedge-fund quant. Esencja: Huyen — 3-warstwowa pamięć (internal/short/long) + pułapka FIFO (uzasadnia nasz zanik warstwowy) + reranking wg świeżości („stock market") + RAG>fine-tuning dla świeżych danych + compound mistakes 0,95ⁿ. Infante — stan grafu=pamięć (checkpoint), Router vs Supervisor (Senat=Supervisor, mocniejszy model), MCP. Iusztin — FTI + hybrid search (BM25+dense łapie tickery) + reranking cross-encoderem (największy zysk RAG). Alto — taksonomia pamięci (Buffer/Summary/Entity/KG) + CONDENSE_QUESTION. 🚨 Prawo XV: gotowy blueprint domknięcia Bibliotheca-RAG (W2). UWAGA techniczna: `git checkout origin/main -- ` nadpisuje pliki lokalne — książki były na branchu roboczym, nie main; sync przez merge (nie reset --hard, blokuje auto-mode).

### 2026-06-22 — FinMem layered decay wdrożony + scan rynku pamięci (MEM-01..04)
Pytanie Cezara: czy mamy FinMem/FinAgent. Weryfikacja na żywo (WebSearch): FinMem=2311.13743 (NASZ KOD cytował błędnie 2408.14900 → naprawione, Prawo I), FinAgent=2402.18485, Mem0=2504.19413, A-Mem=2502.12110. WDROŻONE: zanik warstwowy FinMem w centrum_pamieci._decay_dla_waznosci() — tempo zaniku zależy od ważności (i=0.3→0.99 płytka, i=1.0→0.999 głęboka). Naprawia UTRATA POTENCJAŁU (Prawo XV): wcześniej lekcja krytyczna zanikała tak szybko jak rutyna (jeden 0.995). Nasz unikat: funkcja CIĄGŁA vs 3 kubełki FinMem. Rejestr: MEM-01 wdrożony, MEM-02 dual-reflection (plan), MEM-03 Mem0 auto-konsolidacja (plan), MEM-04 A-Mem auto-linki (kandydat). Unikat Imperium: pamięć rynku + pełny dialog+lekcje+profil w git (przeżywa kompakcję), brak na rynku. 4 testy granic zaniku. _DECAY martwy usunięty.

### 2026-06-22 — Centrum Pamięci W-360 v3 + rynek mem0 scan
centrum_pamieci.py: hub wszystkich 5 warstw pamięci. Scoring Generative Agents (Park et al. 2304.03442): score=recency×importance×relevance, recency=0.995^dni, importance=heurystyka słów kluczowych (0.3-1.0), relevance=Jaccard (0.5 gdy puste). top_lekcji() → sorted scored nie ostatnie-N. szukaj_wszedzie() → W3 lekcje + W3b kronika w jednym zapytaniu. lekcje_scope() → Mem0-style filtr. Rynek: FinMem (2311.13743) 3-tier short/mid/long; TradingGPT (2309.03736) per-agent recency+relevancy+importance; Memex(RL) (2603.04257) episodic+semantic; From Knowing to Doing (2605.28359) raw logs > summaries; Zep/Graphiti (2501.13956) bi-temporal invalidation; regime-stale bug: cosine retrieval traci skuteczność przy zmianie reżimu → potrzeba temporal decay + regime label metadata; kronika_czatu.py: 100 sesji 5.99MB w repo → git niesie całą historię do chmury.

### 2026-06-22 — Pamięć v2: CRUD + profil Cezara + Kronika Czatu (vs Hermes/Zep/Mem0)
- Porównanie z konkurencją (Hermes MEMORY.md/USER.md, Zep/Graphiti bi-temporal KG, Cognee ECL, Mem0 ADD/UPDATE/DELETE/NOOP, MemGPT paging, Generative Agents recency·importance·relevance)
- Wniosek: nasza Warstwa 3 zbiegła się architektonicznie z Hermesem (markdown rdzeń + FTS5). Zaadoptowane braki:
- (1) CRUD pamięci: usun_lekcje()/aktualizuj_lekcje() — wcześniej tylko append (UTRATA POTENCJAŁU, Prawo XV)
- (2) limit zwięzłości LIMIT_ZNAKOW_LEKCJA=1200 (Hermes-style twardy błąd) + alarm_przepelnienia sekcji
- (3) profil_cezara() = odpowiednik USER.md (model użytkownika ⊥ środowisko) → docs/PROFIL_CEZARA.md, wstrzykiwany na starcie
- (4) kronika_czatu.py: destyluje 148MB transkryptów ~/.claude → 6MB czystego dialogu w repo (git niesie historię lokal↔chmura, rozwiązuje ulotność kontenera). Redakcja kluczy API. Przyrostowa. Wpięta w hook.
- Do rozważenia później: bi-temporal invalidation (Zep), recency·importance·relevance scoring (Generative Agents), RAPTOR tree-summary

### 2026-06-21 — Memory MCP natywny (pamiec_sesji.py)
- Zamiast zewnętrznego Node Memory MCP (nietestowalny w chmurze) → natywny moduł Python (Prawo XIX: kod+testy)
- imperium/biblioteki/pamiec_sesji.py: lekcje()/dopisz_lekcje()/szukaj()/mapa_podpiec()/podsumowanie_startowe()
- Źródło prawdy: docs/PAMIEC_SESJI.md (markdown — czytelny dla Cezara, w git, indeksowany w RAG korpus dane)
- Wpięte do SessionStart hook: mapa + 3 ostatnie lekcje wyświetlane na starcie KAŻDEJ sesji → koniec utraty kontekstu w kompakcji
- Warstwa 3 pamięci (Warstwa 1=transakcje/Mnemosyne, Warstwa 2=RAG/książki, Warstwa 3=ciągłość sesji)
- 12 testów (granice: pusty plik, brak sekcji, dopisanie do nieistniejącej sekcji, roundtrip)

### 2026-06-21 — Bibliotheca-RAG v1 + v2
- RAG zbudowany: FTS5 (BM25) + opcjonalne wektory, 7760 fragmentów, 80 źródeł
- Korpusy: `biblioteka` (32 książki), `dane` (CSV/JSON/TXT), `docs` (dokumentacja Imperium)
- Tryb przyrostowy (`--tylko-nowe`): 24s → 0.8s gdy brak zmian
- Bug: infinite loop w `podziel_na_chunki` gdy `overlap == max_slow` → fix: `overlap = min(overlap, max_slow - 1)`
- HuggingFace zablokowany w chmurze (403) → tylko FTS w cloud; wektory działają lokalnie
- MCP server: `biblioteka_szukaj(zapytanie, topk, tryb, korpus)` + `biblioteka_info()`

### 2026-06-21 — Speedup backtestu 2.9× (GARCH + BOCPD)
- Profiler (cProfile): wąskie gardło to NIE TA-Lib (23%), lecz GJR-GARCH recursion (34.5%) i BOCPD (18.9%) — czyste Python loops
- GARCH: scipy.signal.lfilter (IIR w C) zamiast Python for-loop → 2.6×
- BOCPD: scipy.special.gammaln wektorowy zamiast 531K math.lgamma calls + numpy log_w
- Numba zablokowana w chmurze (pip timeout) → numpy/scipy zamiast JIT
- cache_wskaznikow (opt-in, multiprocessing): prekalkulacja wskaźników per symbol
- Wynik: 30.1s → 10.5s (2 pary × 150 barów)

### 2026-06-21 — Backfill sentymentu (PSY-01/02/04 mierzalne w backteście)
- ODKRYCIE: adaptery futures/feargreed/cvd JUŻ istnieją i są wpięte do petla_live + factory Dyrygenta. Neurony PSY żyją LIVE, ale abstynują w backteście (brak historii)
- Luka Prawa XVI: PSY-01/02/04 nigdy nie zmierzone (tylko live, niemierzalne)
- Rozwiązanie: AdapterFutures.pobierz_historie() (Binance /fapi/v1/fundingRate pełna historia + openInterestHist/L-S ~30 dni), forward_fill_na_bary() kauzalny, narzedzia/backfill_sentyment.py (CSV cache), backtest_portfel(sentyment_per=...)
- Funding ma PEŁNĄ historię; OI/L-S tylko ostatnie ~30 dni (limit Binance)
- Cezar odpala backfill lokalnie (sieć), potem backtest mierzy czy PSY dodają przewagę

### 2026-06-21 — MTF bear-shield finding (KROK B backtest)
- MTF gate NIE poprawia wyników globalnie (Sharpe BULL_2021: 0.95→0.71, RANGE_2023: 0.65→0.47)
- MTF gate = TARCZA NIEDŹWIEDZIA (BEAR_2022: Sharpe -0.31→+0.14, MaxDD -89%→-67%)
- Wniosek: warunkowe weto niedźwiedzie przez Namiestnika (wymaga walidacji 2018/2025 najpierw)
- EXP-13/14 backward-IC ≈ forward-IC (|Δ|<0.05) → opisują reżim, nie przewidują kierunku

---

## 🔄 STAN BIEŻĄCY (auto-aktualizuj każdą sesję)

- **Testy:** 1720/1720 ✅ (2026-06-22)
- **Neurony:** 81 (aktywne 75, wyciszone 6) | **Zwiadowcy:** 15 (aktywni 13)
- **Elitarne (Prawo XX):** 18
- **Branch:** `claude/sleepy-fermi-dsdE4`
- **Ostatni commit:** 7a0dbf8 — W-360 Memory MCP natywny (pamiec_sesji.py)
- **Pamięć v2 (2026-06-22):** CRUD lekcji + profil Cezara (USER.md-style) + Kronika Czatu (100 sesji destylatu w repo)
