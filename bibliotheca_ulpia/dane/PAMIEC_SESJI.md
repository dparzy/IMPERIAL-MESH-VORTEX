# PAMIĘĆ SESJI — W-360

> **Cel:** trwała pamięć między sesjami — mapa podpięć, lekcje, priorytety.
> Aktualizuj PO każdej sesji. Wczytywana przez SessionStart hook.
> Indeksowana w RAG jako korpus `pamiec` (plik .md → `bibliotheca_ulpia/dane/`).

## Ostatnia aktualizacja: 2026-06-22

---

## 🗺️ PEŁNA MAPA PODPIĘĆ DO LOKALA (Cezar, 2026-06-21)

### A. MCP Servers dla Claude Code

| ID | Serwer | Status | Priorytet | Co daje |
|----|--------|--------|-----------|---------|
| A1 | **GitHub MCP** | ✅ działa (cloud) | — | PR, issues, CI |
| A2 | **Memory MCP** 💎 | ✅ natywny (imperium/biblioteki/pamiec_sesji.py + hook) | — | Trwała pamięć między sesjami (ROZWIĄZUJE W-360) |
| A3 | **Bibliotheca-RAG MCP** 💎 | ✅ zbudowany (W-360 RAG v2) | — | Szukaj w 36 książkach + encyklopedii + docs (indeks do przebudowy po BIB-033..036) |
| A4 | **Filesystem MCP** 🔵 | ⏳ opcjonalny | niski | Dostęp do plików lokalnych bez Read tool |
| A5 | **Fetch/Web MCP** 🔵 | ⏳ opcjonalny | niski | WebFetch przez MCP |
| A6 | **Sequential-Thinking MCP** 💎 | ⏳ nie skonfigurowany | średni | Ustrukturyzowane rozumowanie krok po kroku |
| A7 | **SQLite MCP** ⚡ | ⏳ nie skonfigurowany | średni | Zapytania SQL do wyników backtestów bezpośrednio |

### A2. Wydajność — WĄSKIE GARDŁO CPU (backtest 8 min → ~40 s)

| Optymalizacja | Zysk | Priorytet |
|---------------|------|-----------|
| **Cache sygnałów** ⚡ | ~5-7× szybszy | 🥇 NAJWYŻSZY |
| **multiprocessing po parach** ⚡ | ~6-8× szybszy | 🥇 NAJWYŻSZY |
| **Snapshot sygnałów .npy** ⚡ | eliminacja re-kalkulacji | wysoki |
| **Numba/JIT na GARCH** ⚡ | ~3-4× na wskaźnikach | wysoki |

Razem: sweep z **8 minut → ~30-40 sekund**.

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
