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

## Do dokończenia (pozostałe pozycje do re-weryfikacji)

- Fin-R1 / Agentar-Fin-R1, FinGPT (C1#2/3) — miały linki, wstępnie realne; potwierdzić aktualność.
- RL-GNN (C1#5), agentowe: Gödel Agent, OmniAgent, Recursive Flow, Galaxy, thoughtful-agents (pip).
- Reszta 17 propozycji wrzutni + wszelkie inne „⚠️ szukać / odrzucone jako nierealne" w docs.

**Zasada:** przy każdej takiej pozycji — najpierw `WebSearch` (bieżący miesiąc), potem werdykt.
