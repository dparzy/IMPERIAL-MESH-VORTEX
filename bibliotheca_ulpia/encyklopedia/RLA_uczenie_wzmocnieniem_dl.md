# 🤖 RLA — Uczenie ze wzmocnieniem i deep learning | Encyklopedia Imperium

> **Stan na:** 2026-07-11 | **Ważność:** ⭐⭐⭐⭐ (wysoki — fundament AI Imperium)
> **Status:** 🚧 CZĘŚCIOWY — DL (BIB-068 Goodfellow, pdf) ugruntowany z pliku; RL (BIB-067
> Sutton-Barto) w formacie **djvu — ⚠️ PENDING** ekstrakcji na laptopie (`djvutxt` niedostępny
> w chmurze). Styk RL↔`hedge_mwu` ugruntowany w NASZYM kodzie (nie w książce — Prawo I).
> **Co to jest:** dział o uczeniu, które PODEJMUJE DECYZJE w czasie — RL (agent ↔ środowisko,
> nagroda) i sieci głębokie jako aproksymatory. Teoria za MWU (online learning), przyszłymi
> agentami RL i wrzutniowymi kandydatami grafowymi.
> **Karmi:** hedge_mwu (online MWU), Legatus (wagi reżimowe), MEM (pamięć agenta), przyszli agenci RL.

## 📑 SPIS TREŚCI
1. Deep learning — po co głębia (Goodfellow, ✅ z pliku)
2. Regularyzacja i generalizacja (dlaczego DL nie musi przeuczać)
3. Uczenie ze wzmocnieniem — szkielet (⚠️ Sutton-Barto pending djvu)
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

## 3. UCZENIE ZE WZMOCNIENIEM — szkielet (⚠️ BIB-067 Sutton-Barto, PENDING djvu)

> **Prawo I:** poniższe to KANONICZNY szkielet RL do WERYFIKACJI po ekstrakcji Sutton-Barto na
> laptopie — nie cytuję z pliku (djvu nieczytelny w chmurze). Plan (do uzupełnienia esencją):
> MDP (stan/akcja/nagroda), polityka i funkcja wartości, **eksploracja vs eksploatacja**,
> multi-armed bandit, TD-learning, Q-learning, regret. To domknięcie na laptopie (`djvutxt`).

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
3. ⭐⭐⭐ **Domknięcie RL na laptopie** ⚠️ — ekstrakcja Sutton-Barto (`djvutxt`) → pełna esencja §3.

> **Prawo XVI:** RLA (decyzje sekwencyjne) ⊥ ALG (ML dla cech) ⊥ MEM (pamięć agenta). Agent RL
> wymaga pamięci → silny styk z MEM (FinMem/A-Mem).

---

## 6. ŹRÓDŁA (ZPO)

- **BIB-068 Goodfellow, Bengio, Courville** — *Deep Learning*, MIT Press 2016,
  ISBN 978-0-262-03561-3. ✅ (ekstrakcja z pliku) — curse of dimensionality, distributed
  representation, CNN/RNN, regularyzacja (rozdz. 7), SGD, representation learning.
- **BIB-067 Sutton, Barto** — *Reinforcement Learning: An Introduction*, 2. wyd., MIT Press 2018.
  ⚠️ **PENDING** — plik djvu, ekstrakcja na laptopie (`djvutxt`). Kanon RL: MDP, wartość/polityka,
  eksploracja-eksploatacja, TD/Q-learning, bandit/regret (most do hedge_mwu).

> **Granica (Prawo XVI):** RLA = uczenie decyzji sekwencyjnych. ML klasyczny cech → **ALG**.
> Pamięć agenta → **MEM**. Rachunek stochastyczny pod modele → **QNT**.

---
*Wypełniono częściowo 2026-07-11: DL (Goodfellow) z pliku + most hedge_mwu z kodu (Prawo I).
RL (Sutton-Barto) — 🚧 do domknięcia po ekstrakcji djvu na laptopie. KANDYDACI ⚠️ → walidacja areną.*
