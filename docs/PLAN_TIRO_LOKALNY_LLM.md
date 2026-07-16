# 🎓 PLAN TIRO — Lokalny Hybrydowy LLM-Uczeń Imperium

> **Stan na:** 2026-07-16 · **Status:** projekt zatwierdzony kierunkowo przez Cezara, wdrażany etapami
> **Architekt:** VITRUVIUSZ (Opus) · **Zwiad:** Sonnet (web) + Hyginus (DeepSeek, plik `wrzutnia/zrodla danych i inne.md`)
> **Rzymskie imię:** **TIRO** (łac. *tiro* — rekrut/uczeń w szkoleniu; docelowo awansuje przez stopnie)

## 🎯 Wizja Cezara (dosłownie)

Zbudować lokalny, hybrydowy model LLM działający na sprzęcie Imperium, który **uczy się jako UCZEŃ**
od nauczycieli (Hyginus/DeepSeek od newsów + Vitruviusz/Opus jako architekt), stopniowo nabiera
umiejętności, aż będzie na tyle dobry, by **przejąć nasze role** — a w miarę rozwoju sprzętu lokalnego
dołożyć kolejne modele i **całkowicie przejść na lokalne zarządzanie** (zero kosztów API, pełna prywatność).

## 🖥️ Twarda rzeczywistość sprzętu (CENSOR, Prawo I — zmierzone, nie zgadnięte)

| Komponent | Realny stan | Konsekwencja |
|---|---|---|
| CPU | Intel i5-4200M — Haswell **2013**, 2 rdzenie / 4 wątki, AVX2 (brak AVX-512) | inferencja tylko-CPU, wolna, ale llama.cpp ma build `haswell` |
| RAM | 16 GB DDR3 (~9 GB wolne) | budżet modelu ~6–10 GB → 1–8B Q4 |
| GPU | Intel HD 4600 (brak CUDA) | **bezużyteczna do LLM** — brak akceleracji i treningu lokalnego |
| Klasa CENSORA | **PEDES** (ranga 1/4) | model 1–3B na żywo / 7–8B wsadowo w tle |

**Werdykt feasibility (Sędzia Opus po weryfikacji web):** ten laptop to **STACJA INFERENCJI, nie treningu.**
- Fine-tuning LoRA/QLoRA **NIE działa CPU-only** (Unsloth wymaga GPU NVIDIA) → **trening = darmowy Google Colab T4**.

### 📏 E1 — POMIAR TWARDY (2026-07-16, `llama-bench` b10041, Prawo I — koniec estymacji)

Silnik `llama.cpp` sam wybrał backend **`ggml-cpu-haswell.dll`** → AVX2 potwierdzony na żywo.
Metoda: `llama-bench -p 512 -n 128 -r 3`, maszyna bezczynna (żadnego obciążenia w tle — inaczej pomiar fałszywy).

| Model | Wątki | Prompt `pp512` | Generacja `tg128` | Werdykt |
|---|---|---|---|---|
| **Qwen3-1.7B** Q4_K_M (1.19 GiB, 2.03 B) | 2 | 23.97 ± 1.31 t/s | **9.64 ± 0.40 t/s** | ✅ **na żywo** (szybciej niż człowiek czyta) |
| Qwen3-1.7B Q4_K_M | 4 | 25.23 ± 0.29 t/s | 9.49 ± 0.25 t/s | HT nie pomaga (szum) |
| **Qwen3-4B** Q4_K_M (2.32 GiB, 4.02 B) | 2 | 9.29 ± 0.27 t/s | 4.39 ± 0.06 t/s | ⚠️ **tylko wsadowo** |
| Qwen3-4B Q4_K_M | 4 | 10.17 ± 0.14 t/s | **4.86 ± 0.11 t/s** | HT daje ~10% |

**Wnioski z pomiaru:**
- **Sufit Fujitsu = 2 rdzenie fizyczne.** Hyperthreading (4 wątki) daje 0% przy 1.7B, ~10% przy 4B — nie ma czego wyciskać.
- **Skalowanie niemal liniowe:** 2× parametrów (2.03B→4.02B) = 2.2× wolniej (9.64→4.39 t/s).
- **Model żywy dziś = Qwen3-1.7B** (~9.6 t/s). Model wsadowy = Qwen3-4B (~4.9 t/s, do nocnej przemiałki newsów).
- ⚠️ **Ekstrapolacja na 8B: ~2.3 t/s** (NIE zmierzone — brak modelu 8B na dysku; zmierzyć, gdy będzie).
- **Twierdzenie Hyginusa „7B @ 10–15 tok/s" = ❌ OBALONE POMIAREM** (~5× zawyżone). Estymacja Opusa (2–5 t/s) ✅ utrzymana.
  To **druga** halucynacja liczbowa Hyginusa (po nieistniejącym „aom-news-4b") → **liczby sprzętowe od DeepSeeka = zawsze hipoteza do pomiaru, nigdy fakt** (ZASADA ZWIADOWCY WIEDZY).

## 🏛️ Architektura TIRO — trzy filary (wszystko opt-in OFF do walidacji, ZASADA WPIĘCIA)

### Filar 1: TIRO-UCZEŃ (inferencja lokalna)
- Silnik: **llama.cpp** (nie Ollama — korekta 2026-07-16). Portable ZIP `llama-b10041-bin-win-cpu-x64`,
  **zero instalacji, zero praw administratora** (wzorzec Calibre Portable). Zawiera `llama-bench` (E1 —
  Ollama go NIE ma) oraz `llama-server.exe` = serwer OpenAI-compatible → to samo trywialne wpięcie w adaptery
  Pythona, które miała dać Ollama. Ollama = opcjonalna wygoda później, nie warunek.
- **Lokalizacja (poza gitem, binaria nie wchodzą do repo):** silnik `C:\TIRO\silnik`, modele `C:\TIRO\modele`.
- Model startowy (**zmierzony**, E1): **Qwen3-1.7B Q4_K_M** — 9.64 t/s, responsywny na żywo.
- Model wsadowy „na noc" (**zmierzony**, E1): **Qwen3-4B Q4_K_M** — 4.86 t/s.
  (Fin-R1 7.6B — kandydat do wpięcia po Nitro; na Fujitsu ekstrapolacja ~2.3 t/s = zbyt wolno nawet wsadowo.)
- Rola startowa: **CICHY DUBLER** — TIRO liczy równolegle do Hyginusa, ale NIE decyduje. Tylko obserwuje i zbiera dane.

### Filar 2: SZKOŁA (teacher → student, knowledge distillation)
- **Nauczyciel distylacji: WYŁĄCZNIE Hyginus/DeepSeek** (korekta prawna 2026-07-16, zwiad web).
  🚨 **Vitruviusz/Opus NIE MOŻE być nauczycielem wag** — regulaminy Anthropic i OpenAI **zakazują**
  trenowania modeli na swoich wyjściach ([Anthropic](https://support.claude.com/en/articles/12326764)).
  DeepSeek **wprost dopuszcza** distylację („training other models") dla użytku niekonkurencyjnego
  ([ToS](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html)) —
  nasz uczeń to wewnętrzny asystent, nie API na sprzedaż → mieścimy się. ⚠️ Nie publikować/sprzedawać TIRO jako osobnego LLM.
  **Vitruviusz zostaje Architektem i Sędzią** (projekt, recenzja, egzamin w arenie) — jego odpowiedzi
  NIE trafiają do zbioru treningowego.
- **Dataset:** pary `prompt → wzorcowa odpowiedź nauczyciela` zapisywane jako JSONL SFT (destylacja przez naśladowanie, nie logity — API nie daje prawdopodobieństw).
- **Trening:** wyłącznie **Google Colab (darmowy T4, ~15–30 h/tydz.)** — LoRA/QLoRA na 1–8B. Lokalnie tylko: scalenie → konwersja `convert_hf_to_gguf.py` → kwantyzacja Q4.
- **Inferencja:** wyłącznie lokalnie.

### Filar 3: EGZAMIN (arena — awans mierzony, nie deklarowany)
- TIRO „awansuje" i przejmuje rolę **dopiero po zielonym A/B** vs nauczyciel (Brier/dokładność sentymentu na realnych danych).
- **Kandydat ≠ prawda** (ZASADA ZWIADOWCY WIEDZY): rozstrzyga pomiar areny/Sybilli, nie deklaracja.
- Wpięcie w ścieżkę decyzyjną = flaga opt-in, włącza Cezar po walidacji (Prawo XVIII).

## 🔭 CENSOR SPRZĘTU — auto-wykrywanie migracji (Prawo XV) ✅ WDROŻONE

`imperium/oczy/censor_sprzetu.py` — organ „oczu" mierzący majątek maszyny:
- Migawka CPU/RAM/GPU (stdlib: ctypes/proc/nvidia-smi, bez psutil).
- Klasy majątkowe (census→classis): **PROLETARIUS → PEDES → EQUES → PRAETOR → CONSUL**.
- Baseline w git → po `git pull` na nowej maszynie porównanie live↔baseline **wykrywa migrację**.
- **Alarm potencjału przy awansie:** „🚨 masz teraz GPU CUDA → trening lokalny realny → MIGRUJ TIRO na większy model / przejmij role nauczycieli."
- Degradacja też (słabsza maszyna → zejdź na mniejszy model).
- CLI: `python -m imperium.oczy.censor_sprzetu {raport|migawka|klasa|zmiana|zatwierdz}`.

**Ścieżka awansu klasą sprzętu → model TIRO:**
| Klasa | Sprzęt | Model TIRO | Trening |
|---|---|---|---|
| PEDES (dziś) | CPU ≥12 GB RAM | **1.7B żywo / 4B wsadowo** (zmierzone E1) | Colab |
| EQUES | GPU CUDA 4–8 GB | 3–8B na GPU | lekki LoRA lokalnie |
| PRAETOR | GPU CUDA 8–24 GB | 7–14B na GPU | pełny LoRA/QLoRA lokalnie |
| CONSUL | GPU CUDA ≥24 GB | 30B+ | pełny fine-tuning lokalny |

### 🖥️ Następny sprzęt: Acer Nitro / RTX 4050 (plan Cezara — „za kilka miesięcy", wymiana klawiatury)

⚠️ **RTX 4050 Laptop GPU ma 6 GB VRAM, nie 8** ([NotebookCheck](https://www.notebookcheck.net/NVIDIA-GeForce-RTX-4050-Laptop-GPU-Benchmarks-and-Specs.675695.0.html)
— Ada Lovelace AD107, 2560 rdzeni CUDA, TGP 35–115 W). Klasa CENSORA: **EQUES**. To zawęża plany:

- ✅ **QLoRA 4-bit na 1–4B** (Qwen3-1.7B / Qwen3-4B / Phi-4-mini) — komfortowo w 6 GB.
- ⚠️ **QLoRA na 7–8B** — na granicy (praktyczne minimum to 8 GB VRAM): krótkie sekwencje, mały batch, wymagany **[Unsloth](https://github.com/unslothai/unsloth)** (~30–50% mniej VRAM, ~2× szybciej niż goły PEFT).
- ❌ **Pełny fine-tune** (nawet 1–3B) — stan optymalizatora nie mieści się. Zawsze LoRA/QLoRA.
- ❌ **MoE** — patrz sekcja Hybryda.
- → **Cięższe treningi nadal na Colab T4 (16 GB, darmowy).** Nitro = trening lekki + szybka inferencja.

**Zmiana jakościowa, nie ilościowa:** dziś nie możemy trenować **niczego** (brak CUDA); po Nitro — LoRA lokalnie.
CENSOR wykryje pojawienie się CUDA **automatycznie** i podniesie alarm Prawa XV z rozkazem migracji (E6).

**„Więcej organów" po Nitro:** uczeń dostaje **osobne adaptery LoRA per rola** (newsy / ocena hipotez / RAG),
przełączane bez trzymania kilku modeli w pamięci naraz — realna ścieżka dokładania narządów w budżecie 6 GB.

## 🧬 HYBRYDA — jak realnie połączyć „najlepsze cechy" (zwiad web 2026-07-16)

Rozkaz Cezara: *„stworzyć unikatowy model zgodny z naszą specyfikacją — hybrydę, wybrać najlepsze cechy
i połączyć w jeden najlepszy model zdolny się uczyć i rozwijać"*. „Hybryda" ma **trzy różne znaczenia
techniczne** — tylko jedno jest dla nas dobre:

| Droga | Co to jest | Werdykt dla Imperium |
|---|---|---|
| **1. Scalanie wag** (model merging) | Uśrednianie wag 2+ modeli: SLERP (Spherical Linear Interpolation), TIES (Trim-Elect Sign-Merge), DARE (Drop And REscale), Task Arithmetic. Narzędzie: [mergekit](https://github.com/arcee-ai/mergekit), 16+ metod, **działa na CPU** (`--lazy-unpickle`) | ⚠️ **Dodatek, nie fundament.** Twarde ograniczenie: **ta sama architektura i kształty tensorów** ([issue #174](https://github.com/arcee-ai/mergekit/issues/174)). Daje **średnią z modeli publicznych** = nic unikalnego. |
| **2. MoE** (Mixture of Experts) z gotowych modeli | `mergekit-moe`/frankenMoE — router + kilku ekspertów ([Labonne](https://huggingface.co/blog/mlabonne/frankenmoe)) | ❌ **ODRZUCONE.** Wszyscy eksperci muszą siedzieć w pamięci **naraz**: MoE 4×7B = ~28B w RAM, nie 7B. Nie mieści się ani w 16 GB RAM Fujitsu, ani w 6 GB VRAM Nitro. |
| **3. Distylacja** (nauczyciel→uczeń) | Uczeń uczy się **naśladować zachowanie** nauczycieli (tak powstały Fin-R1 i seria DeepSeek-R1-Distill) | ✅ **NASZA DROGA.** Brak ograniczenia architektury — uczeń może czerpać od dowolnego nauczyciela. |

### 🎯 Werdykt Architekta: co czyni model NASZYM

Scalanie wag daje to samo, co ma każdy inny na Hugging Face. **Unikalność TIRO nie weźmie się z techniki
łączenia — weźmie się z DANYCH, KTÓRYCH NIKT INNY NIE MA:** wyniki areny, decyzje 87 neuronów, biblioteka
RAG (27 959 fragmentów), werdykty Hyginusa, kronika 102 sesji. Uczeń wytrenowany na *tym* będzie jedynym
modelem na świecie rozumiejącym Imperium. Frankenmerge z trzech modeli z HF nie da tego nigdy.

**→ Hybryda = wspólny szkielet z HF (rodzina Qwen) + distylacja na danych Imperium.** Scalanie wag = opcjonalny
finisz (dolanie wiedzy finansowej Fin-R1), nie fundament.

### 🧱 Kandydaci (zweryfikowani — strony HF otwarte, ⚠️ = niesprawdzone)

| Model | Rozmiar | Baza / architektura | Licencja | Rola |
|---|---|---|---|---|
| [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) | 1.7B | Qwen3 | Apache 2.0 ✅ | **uczeń żywy** (zmierzony 9.64 t/s) |
| [Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) | 4B | Qwen3 | Apache 2.0 ✅ | **uczeń wsadowy** (zmierzony 4.86 t/s) |
| [Fin-R1](https://huggingface.co/SUFE-AIFLM-Lab/Fin-R1) | 7B | **Qwen2.5**-7B-Instruct | ⚠️ niesprawdzona | wiedza finansowa do scalenia (po Nitro) |
| [Bielik](https://huggingface.co/speakleash) | 11B | **Mistral-7B** (depth-upscaled) | ⚠️ komercyjna niesprawdzona | **osobny organ PL** — patrz niżej |

🚨 **Pułapka architektur:** Fin-R1/Qwen3/DeepSeek-R1-Distill są rodziny **Qwen** → scalalne.
**Bielik stoi na Mistralu → NIE DA SIĘ go scalić wagowo** z rodziną Qwen. Wchodzi wyłącznie jako
**osobny organ polskojęzyczny** wywoływany równolegle. ⚠️ Kompatybilność scalania **Qwen2.5 ↔ Qwen3**
(różnice typu QK-norm) **NIEZWERYFIKOWANA** — sprawdzić przed scaleniem Fin-R1.

### 🔄 „Model, który uczy się i rozwija" — brutalny realizm (Prawo I)

**Katastroficzne zapominanie NIE jest rozwiązane w 2026.** LoRA zapomina mniej niż pełny fine-tune,
ale zapomina ([arxiv 2405.09673](https://arxiv.org/html/2405.09673v2)). Metody O-LoRA/LoTA/EProj są
badawcze, wrażliwe na hiperparametry, **nie plug-and-play**. „Model uczy się sam, ciągle, bez zapominania"
= ❌ **marketing/research-only, NIE dla nas.**

**Realny rozwój TIRO — dwie warstwy:**
1. **Pamięć natychmiastowa (RAG)** — uczeń widzi każdą nową lekcję od razu, bez treningu, zero ryzyka zapominania. **Już to mamy zbudowane.**
2. **Rozwój skokowy (LoRA)** — okresowy, bramkowany, wersjonowany re-trening na zebranych parach; podmiana adaptera **dopiero po zielonym egzaminie w arenie**.

Czyli: rozwój **skokami po pomiarze**, nie płynny. Zgodne z ZASADĄ WPIĘCIA (opt-in OFF) i Filarem 3.

## 📋 Roadmapa (etapy, każdy z pomiarem — ZASADA ANALIZY CZĄSTKOWEJ)

- [x] **E0 — CENSOR sprzętu** (auto-detekcja + alarm Prawa XV). ✅ 2026-07-16
- [x] **E1 — Pomiar twardy:** llama.cpp (nie Ollama) + `llama-bench` → REALNE tok/s zmierzone dla 1.7B i 4B na Fujitsu.
      Estymacje zastąpione tabelą pomiarową ↑. Teza Hyginusa „7B @ 10–15 t/s" obalona. ✅ 2026-07-16
- [ ] **E2 — TIRO-uczeń cichy dubler:** adapter `llama-server` obok Hyginusa (opt-in OFF), zbieranie par nauczyciel→odpowiedź do JSONL.
      **Zbieranie par można ruszyć NATYCHMIAST — jest niezależne od sprzętu.** Im wcześniej start, tym większy zbiór zastanie Nitro.
- [ ] **E3 — Pierwszy A/B:** surowy mały model vs DeepSeek na newsach (Brier) — baseline jakości ucznia.
- [ ] **E4 — Szkoła:** trening LoRA w Colab na zebranym datasecie → GGUF → lokalna inferencja.
- [ ] **E5 — Egzamin:** A/B ucznia-po-treningu vs nauczyciel; awans roli tylko po zielonym pomiarze.
- [ ] **E6 — Migracja sprzętu:** gdy CENSOR wykryje GPU → odblokowanie treningu lokalnego i większych modeli.

## ⚠️ Obalone halucynacje DeepSeeka (Prawo I)
- ❌ „aom-news-4b" — **nie istnieje**.
- ❌ „7B @ 10–15 tok/s na tym laptopie" — **OBALONE POMIAREM E1** (2026-07-16): zmierzone 4B = 4.86 t/s,
  ekstrapolacja 8B ≈ 2.3 t/s → Hyginus zawyżył ~5×. Estymacja Opusa (2–5 t/s) potwierdzona.
- ❌ „DeepSeek-V2-Lite ~3.5 GB RAM" — mylące (MoE 15.7B total musi siedzieć w RAM, realnie ~8–9 GB Q4).
- ⚠️ „97% dokładności po fine-tuningu" — niepodparte źródłem.
- ✅ Gemma 4, DeepSeek V4-Flash, Fin-R1 — **realne** (ale dwa pierwsze za duże lokalnie).

## 🔌 MCP-monitor sprzętu (soczewka, nie mózg — ZASADA MCP)
Realne serwery (psutil): `huhabla/mcp-system-monitor` (cross-platform), `seekrays/mcp-monitor`.
**Decyzja o wpięciu = Cezar.** CENSOR i tak czyta sprzęt lokalnie bez MCP — MCP tylko do ciągłego podglądu wydajności podczas biegów uczenia.
