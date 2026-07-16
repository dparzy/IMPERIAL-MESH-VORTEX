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
- Realna prędkość: **1–3B → 5–15 tok/s** (codzienny uczeń), **7B → 2–5 tok/s** (wsadowo/nocnie).
- Twierdzenie DeepSeeka „7B @ 10–15 tok/s" = ❌ **zawyżone** (to wynik dla nowoczesnych CPU AVX-512/Apple).
- Fine-tuning LoRA/QLoRA **NIE działa CPU-only** (Unsloth wymaga GPU NVIDIA) → **trening = darmowy Google Colab T4**.

## 🏛️ Architektura TIRO — trzy filary (wszystko opt-in OFF do walidacji, ZASADA WPIĘCIA)

### Filar 1: TIRO-UCZEŃ (inferencja lokalna)
- Silnik: **Ollama** (serwer OpenAI-compatible `localhost:11434` → trywialne wpięcie w adaptery Pythona).
- Model startowy: **1–3B Q4** (kandydaci: Qwen3-1.7B / Llama-3.2-3B / Gemma-3-4B) — responsywny.
- Model wsadowy „na noc": **Fin-R1 7.6B** (gotowe GGUF `bartowski/SUFE-AIFLM-Lab_Fin-R1-GGUF`) do analizy newsów offline.
- Rola startowa: **CICHY DUBLER** — TIRO liczy równolegle do Hyginusa, ale NIE decyduje. Tylko obserwuje i zbiera dane.

### Filar 2: SZKOŁA (teacher → student, knowledge distillation)
- **Nauczyciele:** Hyginus/DeepSeek (newsy/sentyment) + Vitruviusz/Opus (architektura/analiza).
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
| PEDES (dziś) | CPU ≥12 GB RAM | 1–3B żywo / 7B wsadowo | Colab |
| EQUES | GPU CUDA 4–8 GB | 3–8B na GPU | lekki LoRA lokalnie |
| PRAETOR | GPU CUDA 8–24 GB | 7–14B na GPU | pełny LoRA/QLoRA lokalnie |
| CONSUL | GPU CUDA ≥24 GB | 30B+ | pełny fine-tuning lokalny |

## 📋 Roadmapa (etapy, każdy z pomiarem — ZASADA ANALIZY CZĄSTKOWEJ)

- [x] **E0 — CENSOR sprzętu** (auto-detekcja + alarm Prawa XV). ✅ 2026-07-16
- [ ] **E1 — Pomiar twardy:** instal Ollama + `llama-bench` → zmierz REALNE tok/s dla 1B/3B/7B na Fujitsu (zastąp estymacje). Prawo I.
- [ ] **E2 — TIRO-uczeń cichy dubler:** wpięcie Ollama-adaptera obok Hyginusa (opt-in OFF), zbieranie par nauczyciel→odpowiedź do JSONL.
- [ ] **E3 — Pierwszy A/B:** surowy mały model vs DeepSeek na newsach (Brier) — baseline jakości ucznia.
- [ ] **E4 — Szkoła:** trening LoRA w Colab na zebranym datasecie → GGUF → lokalna inferencja.
- [ ] **E5 — Egzamin:** A/B ucznia-po-treningu vs nauczyciel; awans roli tylko po zielonym pomiarze.
- [ ] **E6 — Migracja sprzętu:** gdy CENSOR wykryje GPU → odblokowanie treningu lokalnego i większych modeli.

## ⚠️ Obalone halucynacje DeepSeeka (Prawo I)
- ❌ „aom-news-4b" — **nie istnieje**.
- ❌ „7B @ 10–15 tok/s na tym laptopie" — zawyżone (2–5 realnie).
- ❌ „DeepSeek-V2-Lite ~3.5 GB RAM" — mylące (MoE 15.7B total musi siedzieć w RAM, realnie ~8–9 GB Q4).
- ⚠️ „97% dokładności po fine-tuningu" — niepodparte źródłem.
- ✅ Gemma 4, DeepSeek V4-Flash, Fin-R1 — **realne** (ale dwa pierwsze za duże lokalnie).

## 🔌 MCP-monitor sprzętu (soczewka, nie mózg — ZASADA MCP)
Realne serwery (psutil): `huhabla/mcp-system-monitor` (cross-platform), `seekrays/mcp-monitor`.
**Decyzja o wpięciu = Cezar.** CENSOR i tak czyta sprzęt lokalnie bez MCP — MCP tylko do ciągłego podglądu wydajności podczas biegów uczenia.
