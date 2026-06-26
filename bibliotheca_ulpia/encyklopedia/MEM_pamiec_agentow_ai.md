# 🧠 MEM — Pamięć agentów AI | Encyklopedia Imperium

> **Stan na:** 2026-06-25 | **Ważność:** ⭐⭐⭐⭐⭐ (krytyczny — ciągłość Imperium między sesjami)
> **Co to jest:** dział o PAMIĘCI sztucznych agentów (LLM) — jak Imperium pamięta między
> sesjami, jak robi to rynek (FinMem/Mem0/Hermes/Zep) i gdzie mamy przewagę. Spina temat,
> który dotąd był rozproszony po 8 modułach kodu i 4 dokumentach (luka Prawo XV — naprawiona).
> **Karmi (moduły):** centrum_pamieci, pamiec_sesji, kronika_czatu, pamiec_absolutna,
> pamiec_refleksyjna (cesarz/), ksiega_wad (cesarz/) · **Źródła rynku:** REJESTR_INSPIRACJI MEM-01..04.
> **Kanon książkowy:** BIB-033 Huyen · BIB-034 Infante · BIB-035 Iusztin&Labonne · BIB-036 Alto (§8).

## 📑 SPIS TREŚCI
1. [Dlaczego pamięć to problem (dla nowicjusza)](#1-dlaczego-pamięć-to-problem)
2. [Architektura pamięci Imperium (5 warstw)](#2-architektura-pamięci-imperium)
3. [Scoring i zanik warstwowy (jak wybieramy co pamiętać)](#3-scoring-i-zanik-warstwowy)
4. [Rynek pamięci AI (zweryfikowane prace)](#4-rynek-pamięci-ai)
5. [Nasz unikat (czego nie ma rynek)](#5-nasz-unikat)
6. [Backlog (kandydaci do wdrożenia)](#6-backlog)
7. [Mapa: warstwa → moduł kodu](#7-mapa-warstwa--moduł-kodu)
8. [Kanon książkowy — esencja BIB-033..036](#8-kanon-książkowy)

---

## 1. DLACZEGO PAMIĘĆ TO PROBLEM

Model LLM (jak Claude) ma **skończone okno kontekstu** — po wyczerpaniu „zapomina"
początek rozmowy (kompakcja). W chmurze dochodzi drugi problem: **kontener jest ulotny** —
po okresie bezczynności znika, a repozytorium klonuje się od nowa. Bez trwałej pamięci
każda sesja zaczynałaby od zera: te same pytania, te same błędy, zero ciągłości.

Rozwiązanie Imperium: **pamięć poza modelem, wersjonowana gitem.** Wszystko, co warto
pamiętać, zapisujemy do plików w repo → commit niesie historię do każdej maszyny i do chmury.
Hook `SessionStart` wstrzykuje skondensowaną pamięć na starcie KAŻDEJ sesji.

---

## 2. ARCHITEKTURA PAMIĘCI IMPERIUM

Pięć warstw, każda samodzielna, spięta fasadą `centrum_pamieci.py` (W-360 v3):

| Warstwa | Moduł | Co pamięta | Trwałość |
|---------|-------|------------|----------|
| **W1** | `pamiec_absolutna.py` | logi SYGNAŁÓW/TRADE/ANALIZA/TEST (MAE/MFE) | JSONL |
| **W2** | `bibliotheca_ulpia/` | RAG semantyczny (41/42 książek + encyklopedia) | FTS5 |
| **W3** | `pamiec_sesji.py` | LEKCJE z sesji + PROFIL Cezara (markdown) | git |
| **W3b** | `kronika_czatu.py` | PEŁNY DIALOG (destylat transkryptów) | git |
| **(~)** | `imperium/cesarz/pamiec_refleksyjna.py` | refleksja narracyjna po seriach transakcji (W-295) | JSONL |
| **(~)** | `imperium/cesarz/ksiega_wad.py` | prewencja powtarzania błędów | JSONL |
| **WYCOFANY** | ~~`mnemosyne.py`~~ | SQLite trade-learning zastąpiony przez pamiec_refleksyjna + ksiega_wad (Prawo XVI) | — |

Wejście dla hooka startowego: `centrum_pamieci.podsumowanie_startowe()` → profil Cezara +
Top-k scored lekcji + alarm przepełnienia + statystyki kroniki. Cross-layer search
(`szukaj_wszedzie`) odpytuje lekcje (W3) i kronikę (W3b) jednym zapytaniem.

**Stan (policzony, Prawo XIX, 2026-06-22):** 8 lekcji w PAMIEC.md · 100 sesji / ~6,0 MB
dialogu w `bibliotheca_ulpia/dane/kronika/` · testy całości 1740/1740.

---

## 3. SCORING I ZANIK WARSTWOWY

Co pamiętać „na wierzchu"? Scoring **Generative Agents** (Park et al., arXiv:2304.03442)
+ **4. wymiar reżimowy** (UNIKAT Imperium, MEM-06):

```
score = recency × importance × relevance × regime_match
```

- **recency** — wykładniczy zanik od daty lekcji (świeże ważą więcej),
- **importance** — heurystyka słów kluczowych bez LLM (bug/odkrycie/prawo = ważniejsze), 0.3–1.0,
- **relevance** — podobieństwo Jaccarda do zapytania (offline, bez wektorów), 0.0–1.0,
- **regime_match** (UNIKAT) — 1.0 gdy wspomnienie z bieżącego reżimu / bez tagu; `_DAMPEN_REZIM`
  (0.4) gdy z innego reżimu. `rezim_biezacy=''` → 1.0 (wyłączone, wstecznie kompatybilne).

**🎯 Pamięć Reżimowa (regime-conditioned retrieval) — czego NIE ma konkurencja:** Mem0, Zep/Graphiti,
Letta, A-Mem są domenowo-ślepe (retrieval = semantyka + recency + ewent. czas). ŻADEN nie wie, że
ważność wspomnienia tradingowego zależy od reżimu rynku. Lekcja „kupuj dołki" z hossy (TREND_STRONG)
jest aktywnie szkodliwa w bessie/krachu. Warunkujemy retrieval na bieżącym reżimie (z `klasyfikuj_rezim`
/Gubernatora): logi W1 mają jawne pole `rezim` (dopasowanie precyzyjne), lekcje W3 — token z treści.
Naprawia „regime-stale bug" (otwarty problem rynku) u źródła. CLI: `szukaj "..." --rezim TREND_STRONG`.

**Zanik warstwowy (adopcja FinMem, arXiv:2311.13743):** tempo zaniku ZALEŻY od ważności.
Rutyna (i=0.3) → 0.99/dzień (half-life ~69 dni); lekcja krytyczna (i=1.0, „utrata
potencjału") → 0.999/dzień (half-life ~690 dni). **Nasz unikat:** funkcja CIĄGŁA zaniku
vs 3 dyskretne kubełki FinMem. Naprawia UTRATĘ POTENCJAŁU: wcześniej jeden zanik 0.995 dla
wszystkich — lekcja o krytycznym bugu znikała tak szybko jak notatka o profilu.

---

## 4. RYNEK PAMIĘCI AI

Zweryfikowane prace (linki + ID arXiv potwierdzone na żywo — Prawo I). Pełny ZPO:
`docs/REJESTR_INSPIRACJI.md` § Klaster Pamięci (MEM-01..04).

| Klucz | Praca | Link | Rdzeń | Mamy? |
|-------|-------|------|-------|-------|
| MEM-01 | **FinMem** — Layered Memory Trading Agent | [2311.13743](https://arxiv.org/abs/2311.13743) | 3-warstwowa pamięć z różnym zanikiem + charakter | ✅ zanik warstwowy |
| MEM-02 | **FinAgent** — Multimodal Foundation Agent | [2402.18485](https://arxiv.org/abs/2402.18485) | dual-level reflection + diversified retrieval | ⚠️ plan |
| MEM-03 | **Mem0** — Scalable Long-Term Memory | [2504.19413](https://arxiv.org/abs/2504.19413) | extract→consolidate→retrieve, –90% token | ⚠️ scope+CRUD ✅ |
| MEM-04 | **A-Mem** — Agentic Memory (Zettelkasten) | [2502.12110](https://arxiv.org/abs/2502.12110) | atomowe notatki, auto-linki, ewolucja | ❌ kandydat |

Dodatkowy kontekst (analiza w `docs/ANALIZA_HERMES_I_PAMIEC.md`): **Hermes Agent**
(MEMORY.md/USER.md, NousResearch), **Zep/Graphiti** (bi-temporal knowledge graph,
arXiv:2501.13956), **CoALA** (episodic/semantic/procedural), **MemGPT** (paging kontekstu).

---

## 5. NASZ UNIKAT

Czego NIE ma rynek (sprawdzone w scanie 2026-06-22):

1. **Pamięć rynku + pamięć deweloperska w jednym, w git.** FinMem/FinAgent pamiętają
   RYNEK. My pamiętamy rynek + CAŁY dialog z Cezarem + lekcje + profil — wszystko
   wersjonowane gitem, przeżywa kompakcję i wygaśnięcie kontenera chmury.
2. **Zanik warstwowy ciągły** (funkcja ważności) zamiast 3 dyskretnych kubełków FinMem.
3. **Etyka falsyfikacji (Prawo I) wbudowana w pipeline** — każde źródło z linkiem i
   uczciwym „⚠️ niezweryfikowany"; rejestr blacklistuje fabrykacje (StratEvo, VORTEX...).
4. **Profil użytkownika ⊥ środowisko** (PROFIL_CEZARA.md = USER.md Hermesa, oddzielony
   od PAMIEC_SESJI = środowisko/MEMORY.md).

---

## 6. BACKLOG

> Wzorce z rynku, jeszcze NIE kod (Prawo XIX — nic nie „istnieje" bez kodu+testów).

| Priorytet | Pozycja | Źródło | Co da |
|-----------|---------|--------|-------|
| ⭐⭐⭐ | Dual-level reflection (low: rynek / high: wynik) | MEM-02 FinAgent | ostrzejsze lekcje z transakcji |
| ⭐⭐⭐ | Auto-konsolidacja/dedup lekcji o tym samym temacie | MEM-03 Mem0 | mniej szumu, –token |
| ⭐⭐ | Metadana reżimu per-lekcja (naprawa regime-stale) | scan 2026-06-22 | trafność przy zmianie reżimu |
| ⭐ | Auto-linkowanie powiązanych lekcji (Zettelkasten) | MEM-04 A-Mem | sieć wiedzy (wymaga embeddingów) |

---

## 7. MAPA: WARSTWA → MODUŁ KODU

```
SessionStart hook
   └─ centrum_pamieci.podsumowanie_startowe()   ← fasada (W-360 v3)
        ├─ pamiec_sesji.lekcje() + profil_cezara()      (W3, git)
        ├─ kronika_czatu.statystyki() + szukaj()         (W3b, git)
        ├─ score_lekcji() = recency×importance×relevance  (Generative Agents)
        └─ _decay_dla_waznosci()                          (FinMem layered decay)

Pętla decyzyjna / trading
   ├─ pamiec_absolutna             → logi sygnałów/trade (W1, JSONL)
   ├─ imperium/cesarz/pamiec_refleksyjna → lekcje narracyjne do promptu Senatu/Cesarza (W-295)
   ├─ imperium/cesarz/ksiega_wad   → prewencja powtórzeń błędów
   └─ bibliotheca_ulpia (RAG)      → wiedza semantyczna (W2, FTS5)
   UWAGA: mnemosyne.py wycofany — zastąpiony przez pamiec_refleksyjna + ksiega_wad (Prawo XVI)
```

---

## 8. KANON KSIĄŻKOWY

Cztery książki o inżynierii aplikacji LLM i agentów AI — bezpośrednie źródło dla działu MEM,
Bibliotheca-RAG i doradcy DeepSeek. Esencja wyciśnięta z pełnych tekstów (Prawo XIX —
analiza na żywo, nie z pamięci). Pełny opis (ZPO): pełna nazwa, ISBN, link, weryfikacja.

| BIB | Autor | Tytuł | Wyd. | ISBN | Format | Weryfikacja |
|-----|-------|-------|------|------|--------|-------------|
| 033 | Chip Huyen | AI Engineering: Building Applications with Foundation Models | O'Reilly 2025 | [978-1-098-16630-4](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) | EPUB | ✅ ISBN w pliku |
| 034 | Roberto Infante | AI Agents and Applications: With LangChain, LangGraph, and MCP | Manning 2025 | [978-1-63343-654-1](https://www.manning.com/books/ai-agents-and-applications) | EPUB | ✅ ISBN+autor zweryf. web |
| 035 | Paul Iusztin & Maxime Labonne | LLM Engineer's Handbook | Packt 2024 | [978-1-83620-007-9](https://www.packtpub.com/en-us/product/llm-engineers-handbook-9781836200079) | AZW3 | ⚠️ ekstrakcja AZW3 częściowa |
| 036 | Valentina Alto | Building LLM Powered Applications | Packt 2024 | [978-1-83546-231-7](https://www.packtpub.com/en-us/product/building-llm-powered-applications-9781835462317) | EPUB | ✅ ISBN w pliku |

> **Kontekst (Prawo I):** R. Infante (BIB-034) pracuje dla londyńskiego hedge fundu i buduje
> agentów do analizy ilościowej — to nasza dziedzina. Książki używają OpenAI/LangChain/Chroma
> w przykładach; dla Imperium liczy się ARCHITEKTURA (wzorce), nie konkretny dostawca.

### 8.1 BIB-033 Huyen — trójwarstwowa pamięć (fundament teoretyczny)

Najważniejsza dla MEM. Huyen (rozdz. 6 „Memory") definiuje **trzy mechanizmy pamięci agenta**,
które wprost mapują się na naszą architekturę:

1. **Wiedza wewnętrzna** (internal) — w wagach modelu z treningu (= wagi DeepSeek). Stała.
2. **Pamięć krótkoterminowa** (short-term) — okno kontekstu, bieżąca sesja/bar. Szybka, ograniczona.
3. **Pamięć długoterminowa** (long-term) — zewnętrzne dane przez retrieval (= RAG). Trwała,
   usuwalna bez ruszania modelu.

**Reguła routingu informacji** (idea #1 do zapamiętania): esencjalne dla wszystkich zadań →
wiedza wewnętrzna; rzadko potrzebne → długoterminowa (RAG); natychmiastowe/kontekstowe →
krótkoterminowa. **System pamięci = zarządzanie (co gdzie) + retrieval (jak wyciągnąć).**

Strategie przycinania krótkoterminowej (wprost do `centrum_pamieci`):
- **FIFO** — proste, ale „fatally wrong": wczesne wiadomości (deklaracja celu/reżimu) niosą
  najwięcej informacji. 🚨 To dokładnie pułapka, którą nasz zanik warstwowy (§3) omija.
- **Podsumowanie** (kompresja rozmowy) + śledzenie nazwanych encji.
- **Reflection** (Liu et al. 2023): po akcji agent decyduje WSTAW / SCAL / ZASTĄP sprzeczne lub
  przestarzałe — wzorzec aktualizacji pamięci po decyzji neuronów.
- **Alokacja kontekstu:** rezerwa % okna na retrieval long-term (np. 30%), reszta short-term.

**RAG = długoterminowa pamięć modelu.** Retriever (term-based BM25 vs embedding-based dense)
→ **hybryda** łączy zalety. Vector search = najbliżsi sąsiedzi → ANN (FAISS, HNSW/LSH).
Ewaluacja: **context precision / context recall**, ranking NDCG/MAP/MRR, embeddingi → MTEB.
**Reranking wg świeżości** — Huyen wprost wymienia „stock market analysis" jako przypadek
time-weighted rerankingu (most do doradcy HERMES audytującego świeżość danych).

**Reguła RAG vs fine-tuning** (idea #2): błędy *information-based* (fakty) → RAG; *behavior-based*
(forma/styl) → fine-tuning. Dla danych rynkowych (z natury świeżych) RAG bije fine-tuning.

**Compound mistakes** (idea #3): 0,95/krok → 60% po 10 krokach, 0,6% po 100. Twardy argument
za krótkimi łańcuchami decyzyjnymi + guardraile + Reguła Test-Granic.

### 8.2 BIB-034 Infante — stan grafu jako pamięć (LangGraph)

**Trzy zakresy pamięci:** short-term (sesja), long-term-user (między sesjami), long-term-app
(wspólna dla wszystkich). Książka świadomie pomija dwa ostatnie jako „system-specific" —
**to luka, którą Imperium wypełnia samo** (nasza wielowarstwowa pamięć w git).

**Kluczowa idea: stan grafu = pamięć, nie lista wiadomości.** Checkpoint = snapshot CAŁEGO
stanu (historia + wyniki narzędzi + zmienne + metadane), zapisywany po każdym węźle. Daje za
darmo: (1) **state rehydration po awarii** (wznowienie bez powtarzania drogich kroków),
(2) **human-in-the-loop** (pauza→zatwierdzenie→wznowienie), (3) kontekst wielowątkowy.
Sesja = `thread_id`; backend produkcyjny = PostgreSQL.

**Wzorce wieloagentowe (dla Senatu):** **Router** (one-way: pytanie → jeden agent → koniec)
vs **Supervisor** („agent of agents": orkiestrator odpytuje doradców wielokrotnie, łączy
i rozumuje nad cząstkowymi wynikami). Senat wielogłosowy = Supervisor; **wymaga mocniejszego
modelu-orkiestratora** (konsekwencja kosztowa). **MCP** (Model Context Protocol, Anthropic) —
standaryzuje integrację narzędzi u źródła: dane Imperium (Brama, baza neuronów, wskaźniki)
wystawione raz jako serwery MCP zamiast adaptera per-neuron.

### 8.3 BIB-035 Iusztin & Labonne — RAG produkcyjny + FTI (LLMOps)

⚠️ Ekstrakcja AZW3 częściowa (czytelny TOC + sekcje RAG; reszta to szum binarny). Pewne:

**Architektura FTI (Feature / Training / Inference)** — trzy niezależne pipeline'y spięte
feature store + model registry; lek na monolit ML, każdy skalowalny osobno. Szkielet dla
rozdzielenia pamięci / treningu / decyzji w Imperium.

**RAG = dwa rozdzielone pipeline'y:** *ingestion* (dane → chunking → embedding → vector DB)
i *inference* (retrieval → augmentacja → generacja). Vector store = **Qdrant** + metadane
(pre-filtering). Embedder wg **MTEB** (start: `all-MiniLM-L6-v2` na CPU; domenowy: INSTRUCTOR
lub fine-tuning). **Hybrid search (alpha)** — łączy semantykę z exact-match (łapie tickery!).
**Reranking cross-encoderem** (`ms-marco`) — największy skok jakości RAG przy małym koszcie:
retrieval daje kandydatów (szybko), cross-encoder wybiera trafne (dokładnie). Cykl modelu:
SFT → ewaluacja → **DPO** (preference, tańsze niż RLHF) → optymalizacja inferencji → deploy.

### 8.4 BIB-036 Alto — taksonomia pamięci konwersacyjnej (LangChain)

Najbardziej konkretna mapa typów pamięci (dla `centrum_pamieci`):

- **BufferMemory** — wszystko dosłownie (wierne, drogie, rośnie bez końca).
- **BufferWindowMemory** — przesuwne okno K ostatnich tur.
- **TokenBufferMemory** — okno limitowane tokenami, nie turami.
- **SummaryMemory** — streszcza rozmowę przez LLM (długie dialogi, stratne).
- **SummaryBufferMemory** — hybryda: świeże dosłownie + stare streszczone (najlepszy kompromis).
- **EntityMemory** — fakty o encjach (osoba/instrument/reżim) budowane w czasie.
- **KGMemory** — trójki podmiot–predykat–dopełnienie w grafie wiedzy („neuron X → kategoria Y").
- **VectorStore memory** — interakcje jako wektory, retrieval top-K (semantyczna, niechronologiczna).

**Brak uniwersalnego przepisu** — warstwuj świadomie. **CONDENSE_QUESTION pattern**: przed
retrievalem scal historię + bieżące pytanie w jedno samodzielne zapytanie (bez tego RAG gubi
follow-upy). **3 warstwy mitygacji halucynacji:** model (fine-tune) / metaprompt (grounding:
„jeśli nie wiesz — powiedz") / UX (cytowanie źródeł).

### 8.5 MAPA WIEDZA → KOD IMPERIUM (synteza 4 książek)

| Koncept | Źródło | Gdzie w Imperium |
|---------|--------|------------------|
| Trójwarstwowa pamięć (internal/short/long) | Huyen r.6 | szkielet `centrum_pamieci` (wagi DeepSeek / kontekst / RAG) |
| Reguła routingu wg częstości użycia | Huyen r.6 | polityka co→która warstwa pamięci |
| Reflection (wstaw/scal/zastąp sprzeczne) | Huyen r.6 | aktualizacja lekcji po decyzji (zgodne z Prawem XVIII) |
| Pułapka FIFO (wczesne = najważniejsze) | Huyen r.6 | uzasadnienie zaniku warstwowego §3 (nie czysty FIFO) |
| Reranking wg świeżości („stock market") | Huyen r.6 | Bibliotheca-RAG waży świeżość; most do HERMES |
| Hybrid search (term+embedding, alpha) | Huyen r.6 / Iusztin r.10 | Bibliotheca-RAG: BM25 (klucze/tickery) + dense (semantyka) |
| Reranking cross-encoderem | Iusztin r.10 | Bibliotheca-RAG: tani retrieval → precyzyjny rerank top-K |
| context precision/recall, MTEB, NDCG | Huyen r.6 / Iusztin r.8 | metryki ewaluacji Bibliotheca (Prawo XX/XXI — mierzone) |
| Stan grafu = pamięć (checkpoint) | Infante r.14 | model pełnego stanu sesji; rehydration po awarii pipeline'u |
| Router vs Supervisor | Infante r.12 | Senat = Supervisor (wielokrotne odpytanie + synteza) |
| MCP (narzędzia u źródła) | Infante r.13 | wystaw Bramę/neurony/wskaźniki jako serwery MCP |
| Architektura FTI | Iusztin r.1 | rozdzielenie Feature/Training/Inference pipeline |
| CONDENSE_QUESTION | Alto r.6 | scalanie historii+pytania przed retrievalem Bibliotheca |
| Taksonomia pamięci (Buffer/Summary/Entity/KG) | Alto r.5 | warstwy `centrum_pamieci`: okno / summary / encje / KG |
| RAG vs fine-tuning (info vs behavior) | Huyen r.7 | decyzja kierunkowa dla DeepSeek (Cezar, Prawo XVIII) |
| Compound mistakes (0,95ⁿ) | Huyen r.6 | krótkie łańcuchy + guardraile + Test-Granic |
| 3 warstwy mitygacji halucynacji | Alto r.12 | metaprompt groundingowy + walidacja odpowiedzi DeepSeek |
| Guardraile wyjścia + retry + fallback | Huyen r.10 | walidacja formatu sygnału doradcy (JSON + retry) |

🚨 **PRAWO XV — potencjał do wykorzystania:** Bibliotheca-RAG (W2) jest dziś zaplanowana, nie
wdrożona. Książki dają gotowy blueprint: ingestion⊥inference, hybryda BM25+dense, reranking
cross-encoderem, reranking wg świeżości, context precision/recall jako metryki. To konkretna
ścieżka domknięcia W2 (patrz dział IMP → Bibliotheca-RAG).

---

*VITRUVIUSZ — "Agent bez pamięci to nie agent, tylko echo. My zapisujemy echo do kamienia
(git), a kamień przeżywa każdą sesję."*
