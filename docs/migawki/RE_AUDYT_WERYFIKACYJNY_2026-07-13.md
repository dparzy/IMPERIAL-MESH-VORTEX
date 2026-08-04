---
kategoria: ACTA
typ: acta
wlasciciel: —
bez_wlasciciela: "migawka audytu z dnia w nazwie — prawda swojego czasu"
stan_na: 2026-07-13
powod_istnienia: "Naprawa błędu procesu: Claude odrzucał/wątpił w realne, świeże (post-styczeń-2026) technologie/prace bez weryfikacji WebSearch, bo oceniał z pamięci zamiast sprawdzić internet."
---
# 🔎 RE-AUDYT WERYFIKACYJNY — korekta błędnych odrzuceń (brak weryfikacji web)

> **Stan na:** 2026-07-13 · **Typ:** korekta procesu + rejestru (Prawo I — prawda ponad wygodę)
> **Powód:** Cezar wskazał, że oceniałem pomysły/opcje BEZ weryfikacji najświeższych informacji
> z internetu. Skutek: **odrzucałem lub wątpiłem w REALNE rzeczy** (świeże prace 2025-2026, po
> moim cutoffie ze stycznia 2026). Ten dokument NAPRAWIA rejestr i ustala proces.

---

## Przyczyna źródłowa (Prawo I)

Mój cutoff wiedzy = **styczeń 2026**. Oceniałem post-cutoffowe modele/prace/narzędzia z pamięci,
nazywając je „halucynacją/nieistniejące/nieweryfikowalne" — **bez `WebSearch` na aktualny stan**.
To zafałszowało audyty: prawdziwe i wartościowe opcje zostały błędnie odrzucone.

**Zasada naprawcza (stała, w pamięci):** ZAWSZE weryfikuj najświeższe info z internetu (bieżąca
data) PRZED oceną — zwłaszcza modele LLM, wersje API, prace arXiv, biblioteki, daty wycofań.

## Korekty potwierdzone web (2026-07-13)

| Pozycja | Mój błędny werdykt | Prawda (zweryfikowana) | Źródło |
|---|---|---|---|
| `deepseek-v4-flash` | ❌ „halucynacja, nie zmieniać" | ✅ REALNY (wyd. 2026-04-24); legacy `deepseek-chat`/`reasoner` **wycofane 2026-07-24** → migracja PILNA (zrobiona) | api-docs.deepseek.com |
| **PandaAI** (C1#6) | ⚠️ „liczby niepewne, szukać" | ✅ REALNY — **Rank IC +18.2%, MDD −25.7%** na CSI 300 (dokładnie jak podał DeepSeek) | [arXiv 2606.06823](https://arxiv.org/abs/2606.06823) (2026-06-05) |
| **AgentEvolver** | ⚠️ „[reference] nieweryfikowalne" | ✅ REALNY — self-questioning/navigating/attributing, open-source Python | [arXiv 2511.10395](https://arxiv.org/abs/2511.10395), github modelscope/AgentEvolver |
| **ARTEMIS** (C1#1) | ⚠️ „szukać" | koncepcja REALNA (arbitrage-free neural-SDE), sama nazwa/akronim niepotwierdzony | [arXiv 2105.11053](https://arxiv.org/abs/2105.11053), 2306.16422 |
| **SD-FMM** (C1#4) | ⚠️ „szukać" | obszar REALNY (self-supervised / GNN detekcja manipulacji), sama nazwa niepotwierdzona | arXiv 2411.05815 (review), 2604.24590 |

**Najgroźniejszy błąd:** odrzucenie rady „migruj `deepseek-chat`→`deepseek-v4-flash` przed 24.07"
jako „Halucynacji" (ANALIZA_WRZUTNIA_2026-07-10 §B, wiersz model). Rada była PRAWDZIWA i pilna —
bez niej NEWS/refleksja/auto-lekcja/Bibliotekarz padłyby 24 lipca 2026.

## Co to NIE zmienia (dyscyplina zostaje)

Rehabilitacja ≠ auto-adopcja. Każda pozycja to nadal ⚠️ KANDYDAT: wpięcie opt-in OFF → walidacja
areną/A/B (ZASADA WPIĘCIA, Prawo XVIII). Zmiana jest jedna: **nie odrzucamy prawdy bez sprawdzenia.**
Liczby wydajności z prac (np. Rank IC +18%) to twierdzenia autorów — u NAS prawdą po naszej arenie.

## Re-weryfikacja DOKOŃCZONA (2026-07-13) — pozostałe pozycje

| Pozycja | Werdykt web | Źródło |
|---|---|---|
| **Fin-R1** (C1#2) | ✅ REALNY — 7B (Qwen2.5), 83.65% CFA | [arXiv 2503.16252](https://arxiv.org/abs/2503.16252), HF SUFE-AIFLM-Lab |
| **FinGPT** (C1#3) | ✅ REALNY — open-source finansowy LLM | github AI4Finance-Foundation/FinGPT |
| **Gödel Agent** | ✅ REALNY — rekurencyjna samo-poprawa (monkey-patch runtime) | [arXiv 2410.04444](https://arxiv.org/abs/2410.04444), github Arvid-pku |
| **OmniAgent** | ✅ REALNY — 4 wymiary samoewolucji (opis DeepSeeka 1:1) | github YeQing17-2026/OmniAgent |
| **Recursive Flow** | ✅ REALNY — serwer MCP, dekompozycja zadań | github fritzprix/recursive-flow |
| **Galaxy** | ✅ REALNY — KoRa (proaktywny) + Kernel (meta-agent) 1:1 | [arXiv 2508.03991](https://arxiv.org/abs/2508.03991) |
| **RL-GNN** (C1#5) | koncepcja realna (regime-aware GNN), sama nazwa niepotwierdzona | — |
| **thoughtful-agents** (pip) | ⚠️ NIEPOTWIERDZONY jako pakiet pip — jedyny wątpliwy | — |

**Podsumowanie Re-Audytu:** z ~13 pozycji, które kwestionowałem — **9 potwierdzonych jako REALNE**,
3 to realne koncepcje z niepewną nazwą (ARTEMIS/SD-FMM/RL-GNN), **1 naprawdę wątpliwa**
(thoughtful-agents pip). Trafność DeepSeeka była WYSOKA; moja skepsa — w większości niesłuszna,
bo nie sprawdzałem web. To dokładnie diagnoza Cezara.

**Zasada stała (utrwalona w pamięci):** przy KAŻDEJ ocenie pozycji zewnętrznej — najpierw
`WebSearch` (bieżący miesiąc), potem werdykt. Weryfikacja > pewność siebie.

## Zrehabilitowani ⚠️ KANDYDACI do backlogu (nadal opt-in OFF + arena, ZASADA WPIĘCIA)

Realne i wartościowe, warte rozważenia w kolejnych sesjach (NIE auto-adopcja):
- **PandaAI** (neuro-symbolic closed-loop, Rank IC +18.2%/MDD −25.7%) — spójny z Dyrygentem+refleksją.
- **Fin-R1 / FinGPT** — dedykowany lokalny sentyment → zdejmuje zależność NEWS-01..04 od API.
- **Gödel Agent / OmniAgent / AgentEvolver / Galaxy / Recursive Flow** — cegiełki proaktywności/
  samoewolucji; oceniać przez Prawo XVI (co NIE jest redundantne z tym, co mamy).
- **ARTEMIS/ECON** (arbitrage-free) i **SD-FMM/RL-GNN** — koncepcje realne; szukać konkretnych prac.
