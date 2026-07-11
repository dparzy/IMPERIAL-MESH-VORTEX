# 🤖 RLA — Uczenie ze wzmocnieniem i deep learning | Encyklopedia Imperium

> **Stan na:** 2026-07-11 | **Ważność:** ⭐⭐⭐⭐ (wysoki — fundament AI Imperium)
> **Status:** ✅ DOMKNIĘTY — DL (BIB-068 Goodfellow, pdf) z pliku; RL (BIB-067 Sutton-Barto)
> **wyekstrahowany** (djvu→cache przez calibre, w RAG — **tekst czysty**, dobra jakość OCR).
> Esencja zweryfikowana `biblioteka_szukaj`. Styk RL↔`hedge_mwu` ugruntowany w NASZYM kodzie (Prawo I).
> **Co to jest:** dział o uczeniu, które PODEJMUJE DECYZJE w czasie — RL (agent ↔ środowisko,
> nagroda) i sieci głębokie jako aproksymatory. Teoria za MWU (online learning), przyszłymi
> agentami RL i wrzutniowymi kandydatami grafowymi.
> **Karmi:** hedge_mwu (online MWU), Legatus (wagi reżimowe), MEM (pamięć agenta), przyszli agenci RL.

## 📑 SPIS TREŚCI
1. Deep learning — po co głębia (Goodfellow, ✅ z pliku)
2. Regularyzacja i generalizacja (dlaczego DL nie musi przeuczać)
3. Uczenie ze wzmocnieniem — szkielet (✅ Sutton-Barto ekstrakt djvu)
4. Most do `hedge_mwu`: online learning i minimalizacja regretu (✅ z kodu)
5. Wpływ na Imperium (co mamy / do wdrożenia)
6. Źródła

---

## 1. DEEP LEARNING — PO CO GŁĘBIA (BIB-068 Goodfellow)

Goodfellow-Bengio-Courville: DL powstał, by pokonać **curse of dimensionality** — liczba możliwych
konfiguracji rośnie WYKŁADNICZO z liczbą zmiennych, więc klasyczne metody „na sąsiedztwie" zawodzą
w wysokich wymiarach. Rozwiązanie: **distributed representation** (cechy składane, nie tablicowane)
i **głębia** (kompozycja warstw = wykładnicze zyski reprezentacji). Architektury: feedforward,
**CNN** (konwolucja + pooling jako „infinitely strong prior" o lokalności/niezmienniczości),
**RNN** (modelowanie sekwencji, encoder-decoder). **Representation learning:** transfer learning,
pretraining — model uczy się cech, nie tylko dopasowania.

## 2. REGULARYZACJA I GENERALIZACJA

Cały rozdz. 7 Goodfellowa to **regularyzacja** = wszystko, co poprawia błąd testowy kosztem
treningowego: **parameter norm penalties** (L1/L2 jako constrained optimization), **dataset
augmentation**, **noise robustness**, wczesne zatrzymanie. **SGD (stochastic gradient descent)** to
koń roboczy. Dla Imperium lekcja jest ta sama co w RSK/ALG: **głębia bez regularyzacji = przeuczenie**
— spójne z naszym rdzeniem anty-overfittingu (DSR/PBO/purged-CV, López de Prado).

## 3. UCZENIE ZE WZMOCNIENIEM — szkielet (✅ BIB-067 Sutton-Barto, EKSTRAKT djvu)

> **Prawo I:** Sutton-Barto wyekstrahowane (calibre) i w RAG — **tekst czysty** (dobra jakość OCR,
> inaczej niż math-heavy Shreve). Poniższe zweryfikowane przez `biblioteka_szukaj` (chunki #74/#99/#103).

- **MDP (Markov Decision Process):** agent ↔ środowisko przez sygnał **nagrody**; stan/akcja/nagroda,
  cel = maksymalizacja oczekiwanego **zdyskontowanego zwrotu**.
- **Funkcja wartości i równanie Bellmana:** wartość stanu spełnia *self-consistency condition given by
  the Bellman equation*. **Równanie optymalności Bellmana:** wartość stanu pod optymalną polityką =
  oczekiwany zwrot za **najlepszą akcję** z tego stanu (bez odwołania do konkretnej polityki). Operator
  `max` czyni je nieliniowym — brak formy zamkniętej, stąd metody iteracyjne. Optymalna polityka jest
  **zachłanna** względem v*.
- **Eksploracja vs eksploatacja:** rdzeń problemu; **contextual bandits** (associative search) —
  korzeń w Thorndike'owym *Law of Effect* (skojarzenie stan→akcja, warunkowanie instrumentalne).
- **TD-learning (temporal-difference):** rozwiązuje równanie optymalności Bellmana **używając
  faktycznie doświadczonych przejść zamiast znajomości oczekiwanych** (*bootstrapping*) — most między
  Monte Carlo (pełny epizod) a programowaniem dynamicznym. Dalej: **Sarsa** (on-policy), **Q-learning**
  (off-policy).
- **Praktyka uczenia:** adaptacyjne kroki (step sizes), momentum / Polyak-Ruppert averaging,
  **weighted importance sampling** (niższa wariancja niż zwykły IS — rozdz. 5).

## 4. MOST DO `hedge_mwu` — online learning i regret (✅ z KODU Imperium)

To ugruntowane w naszym kodzie (`imperium/biblioteki/hedge_mwu.py`), nie w książce: **MWU
(Multiplicative Weights Update)** to algorytm online learning z gwarancją **minimalizacji regretu** —
rodzina, do której należy problem **multi-armed bandit** z RL. Imperium używa go do **adaptacyjnego
ważenia** (ekspertów/neuronów): wagi rosną multiplikatywnie za trafność, maleją za błąd, bez
założeń o stacjonarności. To RL „light" — decyzja sekwencyjna z uczeniem — już DZIAŁA w kodzie.
Sutton-Barto dostarczy formalnej teorii regretu/banditów pod ten moduł (po ekstrakcji).

---

## 5. WPŁYW NA IMPERIUM

### Co mamy:
- **hedge_mwu** (online MWU, minimalizacja regretu) — działający „RL light" do ważenia (§4).
- **Legatus** (wagi reżimowe) + **meta_labeling** (B-01) — warstwa uczenia nad rojem.
- **Anty-overfitting** (DSR/PBO/purged-CV) — regularyzacja w duchu Goodfellowa (§2).

### 🚨 Do wdrożenia (Prawo XV — KANDYDACI ⚠️, walidacja areną):
1. ⭐⭐⭐⭐ **GIFT — RL portfela** (z listy wrzutni, poz. C2#11) ⚠️ — agent PPO alokujący kapitał;
   Sutton-Barto to jego kanon. Buduje na hedge_mwu. Wymaga walidacji A/B (opt-in OFF).
2. ⭐⭐⭐ **DL jako aproksymator** (grafowe kandydaty wrzutni: RL-GNN/RHGN/FDPGNN) ⚠️ —
   Goodfellow to fundament. **UWAGA (Brama Kalkulatora):** DL = czarna skrzynka; wchodzi TYLKO
   tam, gdzie deterministyka nie wystarcza, po walidacji (nie zastępuje matematyki Bramy).
3. ✅ **Domknięcie RL** — Sutton-Barto wyekstrahowany (calibre) i w RAG; esencja §3 zweryfikowana
   (`biblioteka_szukaj`). Pełna teoria regretu/banditów pod hedge_mwu dostępna do dalszego zwiadu.

> **Prawo XVI:** RLA (decyzje sekwencyjne) ⊥ ALG (ML dla cech) ⊥ MEM (pamięć agenta). Agent RL
> wymaga pamięci → silny styk z MEM (FinMem/A-Mem).

---

## 6. ŹRÓDŁA (ZPO)

- **BIB-068 Goodfellow, Bengio, Courville** — *Deep Learning*, MIT Press 2016,
  ISBN 978-0-262-03561-3. ✅ (ekstrakcja z pliku) — curse of dimensionality, distributed
  representation, CNN/RNN, regularyzacja (rozdz. 7), SGD, representation learning.
- **BIB-067 Sutton, Barto** — *Reinforcement Learning: An Introduction*, 2. wyd., MIT Press 2018.
  ✅ **EKSTRAKT** (djvu→cache, calibre; tekst czysty — zweryfikowany `biblioteka_szukaj`). Kanon RL:
  MDP, funkcja wartości + równanie (optymalności) Bellmana, eksploracja-eksploatacja / contextual
  bandits, TD / Sarsa / Q-learning, importance sampling (most do hedge_mwu).

> **Granica (Prawo XVI):** RLA = uczenie decyzji sekwencyjnych. ML klasyczny cech → **ALG**.
> Pamięć agenta → **MEM**. Rachunek stochastyczny pod modele → **QNT**.

---
*Domknięto 2026-07-11: DL (Goodfellow) z pliku + RL (Sutton-Barto) wyekstrahowany (calibre, djvu→cache,
tekst czysty) i w RAG — esencja §3 zweryfikowana `biblioteka_szukaj` (MDP, Bellman, TD/Q-learning,
bandits). Most hedge_mwu z kodu (Prawo I). KANDYDACI wdrożeniowi ⚠️ (GIFT/RL-GNN) → walidacja areną.*
