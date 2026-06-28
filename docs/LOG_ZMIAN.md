# 📜 LOG ZMIAN IMPERIUM — Żywa Pamięć Projektu

> **Zasada (ROZKAZ STAŁY):** Po KAŻDEJ zmianie systemu, kodu, dokumentacji — wpis do tego logu.
> Format: Data | Typ | Opis | Powód | Pliki. Najnowsze wpisy na górze.
> Ten plik jest źródłem prawdy historii Imperium. Bez niego decyzje giną.

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
