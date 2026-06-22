# 🧠 MEM — Pamięć agentów AI | Encyklopedia Imperium

> **Stan na:** 2026-06-22 | **Ważność:** ⭐⭐⭐⭐⭐ (krytyczny — ciągłość Imperium między sesjami)
> **Co to jest:** dział o PAMIĘCI sztucznych agentów (LLM) — jak Imperium pamięta między
> sesjami, jak robi to rynek (FinMem/Mem0/Hermes/Zep) i gdzie mamy przewagę. Spina temat,
> który dotąd był rozproszony po 8 modułach kodu i 4 dokumentach (luka Prawo XV — naprawiona).
> **Karmi (moduły):** centrum_pamieci, pamiec_sesji, kronika_czatu, mnemosyne,
> pamiec_absolutna, pamiec_refleksyjna · **Źródła rynku:** REJESTR_INSPIRACJI MEM-01..04.

## 📑 SPIS TREŚCI
1. [Dlaczego pamięć to problem (dla nowicjusza)](#1-dlaczego-pamięć-to-problem)
2. [Architektura pamięci Imperium (5 warstw)](#2-architektura-pamięci-imperium)
3. [Scoring i zanik warstwowy (jak wybieramy co pamiętać)](#3-scoring-i-zanik-warstwowy)
4. [Rynek pamięci AI (zweryfikowane prace)](#4-rynek-pamięci-ai)
5. [Nasz unikat (czego nie ma rynek)](#5-nasz-unikat)
6. [Backlog (kandydaci do wdrożenia)](#6-backlog)
7. [Mapa: warstwa → moduł kodu](#7-mapa-warstwa--moduł-kodu)

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
| **W1** | `mnemosyne.py` | TRANSAKCJE (trade learning, Book of Flaws) | SQLite |
| **W1** | `pamiec_absolutna.py` | logi SYGNAŁÓW/TRADE/ANALIZA/TEST (MAE/MFE) | JSONL |
| **W2** | `bibliotheca_ulpia/` | RAG semantyczny (32 książki + encyklopedia + kronika) | FTS5+wektory |
| **W3** | `pamiec_sesji.py` | LEKCJE z sesji + PROFIL Cezara (markdown) | git |
| **W3b** | `kronika_czatu.py` | PEŁNY DIALOG (destylat transkryptów) | git |
| **—** | `pamiec_refleksyjna.py` | refleksja narracyjna po seriach transakcji (W-295) | JSONL |

Wejście dla hooka startowego: `centrum_pamieci.podsumowanie_startowe()` → profil Cezara +
Top-k scored lekcji + alarm przepełnienia + statystyki kroniki. Cross-layer search
(`szukaj_wszedzie`) odpytuje lekcje (W3) i kronikę (W3b) jednym zapytaniem.

**Stan (policzony, Prawo XIX, 2026-06-22):** 8 lekcji w PAMIEC.md · 100 sesji / ~6,0 MB
dialogu w `bibliotheca_ulpia/dane/kronika/` · testy całości 1740/1740.

---

## 3. SCORING I ZANIK WARSTWOWY

Co pamiętać „na wierzchu"? Scoring **Generative Agents** (Park et al., arXiv:2304.03442):

```
score = recency × importance × relevance
```

- **recency** — wykładniczy zanik od daty lekcji (świeże ważą więcej),
- **importance** — heurystyka słów kluczowych bez LLM (bug/odkrycie/prawo = ważniejsze), 0.3–1.0,
- **relevance** — podobieństwo Jaccarda do zapytania (offline, bez wektorów), 0.0–1.0.

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
   ├─ mnemosyne                 → pamięć transakcji (W1, SQLite)
   ├─ pamiec_absolutna          → logi sygnałów/trade (W1, JSONL)
   ├─ pamiec_refleksyjna        → lekcje narracyjne do promptu Senatu/Cesarza (W-295)
   └─ bibliotheca_ulpia (RAG)   → wiedza semantyczna (W2)
```

---

*VITRUVIUSZ — "Agent bez pamięci to nie agent, tylko echo. My zapisujemy echo do kamienia
(git), a kamień przeżywa każdą sesję."*
