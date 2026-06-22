# 🏛️ IMP — Ulepszenia Imperium | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐⭐ (krytyczny — to mapa rozwoju)
> **Co to jest:** dział, w którym wiedza z całej biblioteki przekłada się WPROST na
> konkretne ulepszenia kodu Imperium. Każda pozycja: co, dlaczego, ważność, status.
> To roboczy backlog rozwoju — żywy, aktualizowany po każdej sesji.

## 📑 SPIS TREŚCI
1. [Stan obecny Imperium](#1-stan-obecny)
2. [Lekcje z pomiarów (co już wiemy)](#2-lekcje-z-pomiarów)
3. [Backlog ulepszeń (priorytetyzowany)](#3-backlog-ulepszeń)
4. [Bibliotheca-RAG — plan](#4-bibliotheca-rag)
5. [Mapa: dział wiedzy → moduł kodu](#5-mapa-wiedza--kod)

---

## 1. STAN OBECNY

> Liczby z audytu (Prawo XIX — policzone, nie z pamięci). Stan: 2026-06-21.

- **Neurony:** 81 (aktywne 75, wyciszone 6)
- **Zwiadowcy (Exploratores):** 15 (aktywni 13, wyciszeni 2: EXP-12 L2, EXP-15 PIN)
- **Elitarne (Prawo XX):** 18
- **Strategie:** 20 · **Testy:** 1648/1648 · **Audyt:** ✅ pełna harmonia
- **Kategorie:** A, C, D, F, H, K, L, M, N, O, R, S, T, V, Z

🚨 **UTRATA POTENCJAŁU (Prawo XV) — 19 modułów czeka na adaptery:**
PSY-01..04 (futures feed), RADAR-01..05 (radar rynku), V-03 (CVD), NEWS-01 (LLM/RSS),
OC-06..08 (timestamp on real bars), AUG-01 (event), C-01 (cross-sectional), X-28 (MTF), Z-06/07.

---

## 2. LEKCJE Z POMIARÓW

Twarde wnioski z sesji 2026-06-21 (zapisane w LOG_ZMIAN, tu skondensowane):

| Lekcja | Dowód | Konsekwencja |
|--------|-------|--------------|
| IC EXP-13/14 ~0.25-0.30 NIE jest predykcją | backward-IC ≈ forward-IC (\|Δ\|<0.05) | EXP-13/14 = **filtry reżimu**, nie sygnały wejścia |
| Wysokie IC nie z nakładania | --nienakladajace: IC stabilne | overlap obalony |
| Brak twardego look-ahead bugu | --przesuniecie: IC płaskie z lagiem | kod czysty od leaku przyszłości |
| GARCH = stan zmienności, Kyle = stan płynności | teoria + pomiar zgodne | użyć jako kontekst sizingu |
| MTF gate NIE poprawia wyników ogólnie | backtest A/B, 6 mies. → MTF gorsze (DSR<0.95) | MTF **OFF** jako domyślne — potwierdzone |
| MTF gate = **tarcza niedźwiedzia** (bear shield) | per-reżim 2021-2026: BEAR_2022 spektakularny | MTF pomaga TYLKO w trendzie spadkowym; szkodzi w bull/range |

### 📊 Szczegółowe wyniki per-reżim MTF (KROK B, 2026-06-21)

| Reżim | Okno | Baseline (OFF) | MTF (ON) | Różnica | Wniosek |
|-------|------|----------------|----------|---------|---------|
| BULL_2021 | 2021-01 → 2021-12 | lepszy | gorszy | MTF szkodzi | blokuje silne longi |
| BEAR_2022 | 2022-01 → 2022-12 | strata | zysk | **MTF ratuje** ⭐ | tarcza przed trendem ↓ |
| RANGE_2023 | 2023-01 → 2023-12 | lepszy | gorszy | MTF szkodzi | blokuje mean-reversion |
| RECENT_25-26 | 2025-01 → 2026-06 | lepszy | gorszy | MTF szkodzi | brak dominującego trendu ↓ |

**Kluczowy wniosek:** MTF gate ≠ „lepsza jakość sygnału" — to **weto dla trendów ↓**.
Właściwe użycie: **warunkowe weto niedźwiedzie** (tylko gdy BTC-trend = BEAR), nie globalna brama.
Wymaga walidacji na 2018/2025 bear markets zanim implementacja przez Namiestnika.

**Reguła wyniesiona (kandydat do CLAUDE.md):** każdy nowy moduł z wysokim IC →
OBOWIĄZKOWO backward-IC zanim uznamy za predyktor. Tani test, chroni przed iluzorycznym edge.

---

## 3. BACKLOG ULEPSZEŃ

### 🥇 Teraz (darmowe, wysoki wpływ)
| # | Ulepszenie | Ważność | Dlaczego | Status |
|---|-----------|---------|----------|--------|
| 1 | **Binance Futures public feed** → PSY-01/02/04, V-03 | ⭐⭐⭐⭐⭐ | ożywia 4+ martwe neurony, DARMOWE bez klucza, Prawo XV | 🔲 |
| 2 | **Cache sygnałów + multiprocessing** w pomiarach | ⭐⭐⭐⭐ | sweep 8 min → ~40 s; przyspiesza KAŻDY przyszły pomiar | 🔲 |
| 3 | **EXP-13 jako adaptacyjny limit lewara** | ⭐⭐⭐⭐⭐ | właściwe użycie filtra reżimu (werdykt backward-IC) | 🔲 |
| 4 | **Memory MCP** (pamięć między sesjami) | ⭐⭐⭐⭐ | wizja Hermesa, oszczędność tokenów | 🔲 |

### 🥈 Wkrótce (z kluczami)
| # | Ulepszenie | Ważność | Status |
|---|-----------|---------|--------|
| 5 | Telegram bot (alerty na telefon) | ⭐⭐⭐⭐ | ⏳ kod W-341 |
| 6 | DeepSeek API → NEWS-01 sentyment | ⭐⭐⭐ | ⏳ placeholder |
| 7 | Fear&Greed feed → PSY-03 | ⭐⭐⭐ | ⏳ feargreed.py |

### 🥉 Później (rozbudowa)
| # | Ulepszenie | Ważność | Status |
|---|-----------|---------|--------|
| 8 | Replay-mode (paper trading na historii) | ⭐⭐⭐⭐ | 🔲 |
| 9 | Glassnode free → OC-01..04 | ⭐⭐⭐ | 🔲 |
| 10 | Deribit DVOL (implikowana zmienność) | ⭐⭐⭐⭐ | 🔲 |
| 11 | Coinglass multi-exchange funding | ⭐⭐⭐ | 🔲 |
| 12 | MEXC API egzekucja (PO backteście+paper!) | ⭐⭐⭐⭐⭐ | ⏳ RealOrderRouter |

---

## 4. BIBLIOTHECA-RAG

> **Następny krok po skompletowaniu encyklopedii** (uzgodnione 2026-06-21).
> Cel: pamięć semantyczna biblioteki dla Claude (chmura) i lokalnego Claude.

### Problem
Teraz każda analiza książki = parsowanie całego pliku epub/pdf (kilka MB, drogie w
tokenach i czasie). Pytanie „co O'Hara mówi o PIN?" wymaga przeczytania całej BIB-032.

### Rozwiązanie: RAG (Retrieval-Augmented Generation)
1. **Indeksacja (raz):** podziel książki + encyklopedię na fragmenty (chunks ~500-1000
   słów), policz embeddingi, zapisz w lokalnej bazie wektorowej (np. SQLite + sqlite-vec,
   albo Chroma/FAISS — czysto lokalnie, bez chmury).
2. **Zapytanie:** „co Tsay mówi o GARCH?" → embedding pytania → top-k najbliższych
   fragmentów → odpowiedź z cytatem i źródłem (BIB-xxx, strona/sekcja).
3. **Integracja:** wystawić jako MCP server → Claude Code (lokalny i chmura) odpytuje
   `biblioteka_szukaj("PIN microstructure")` zamiast czytać pliki.

### Architektura (propozycja, czysto lokalna)
```
narzedzia/rag/
├── indeksuj.py          # parsuje BIB-*, encyklopedię → chunks → embeddingi → baza
├── szukaj.py            # zapytanie → top-k fragmentów
├── mcp_server.py        # wystawia jako MCP tool dla Claude Code
└── baza_wiedzy.db       # SQLite z wektorami (gitignore jeśli duża, lub LFS)
```

### Decyzje do podjęcia (przy starcie RAG):
- **Model embeddingów:** lokalny (sentence-transformers, darmowy, offline) vs API
  (OpenAI/Voyage, lepszy ale płatny). Rekomendacja: lokalny na start.
- **Parsowanie:** epub/pdf/azw3/mobi/djvu — mieszane formaty. Potrzebny uniwersalny
  ekstraktor tekstu (np. `unstructured`, `pymupdf`, `ebooklib`).
- **Czy commitować bazę:** baza wektorowa może być duża → prawdopodobnie gitignore +
  skrypt odtwarzający z książek (indeksuj.py jest deterministyczny).

### Ważność: ⭐⭐⭐⭐ (wysoki — trwała pamięć wiedzy, oszczędność tokenów)

---

## 5. MAPA: DZIAŁ WIEDZY → MODUŁ KODU

| Dział | Główne moduły Imperium |
|-------|------------------------|
| LEW (lewar/futures) | KalkulatorLewara, Gubernator, PSY-01/04, Z-01..07 |
| TRD (traderzy) | architektura roju, Senat, RADAR, sizing |
| RSK (ryzyko) | Reguła 6%, HALT, Z-*, DSR/PBO |
| PSY (psychologia) | PSY-01..04, Senat (eliminacja emocji) |
| MKS (mikrostruktura) | EXP-12/14/15, V-03 CVD, Kyle's λ, PIN |
| ONC (on-chain) | OC-01..08, RADAR-02/03 |
| ALG (algorytmy/ML) | denoising, HRP, metryki IC, GARCH, kointegracja |
| STR (strategie) | rejestr_strategii (20 strategii) |

---

> **Aktualizacja:** po każdej sesji z nowym modułem/lekcją → dopisz tutaj i w INDEX_MAIOR.
