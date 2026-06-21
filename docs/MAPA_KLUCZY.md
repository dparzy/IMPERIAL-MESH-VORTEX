# 🗺️ MAPA KLUCZY — Katalog ↔ Kod

> **Cel:** Jeden plik który rozwiązuje wszelkie nieporozumienia między planami (katalog)
> a żywym kodem. **Kod jest prawem (Prawo XIX)** — klucze z kolumny "Klucz w kodzie"
> są obowiązujące przy pisaniu strategii i w testach.
>
> **Dla nowicjusza:** Gdy piszesz strategię i chcesz użyć RSI — szukasz tu wiersz
> z "RSI" i bierzesz wartość z kolumny "Klucz w kodzie". To jest jedyna poprawna wartość.

---

## ⚡ LEGIO X EQUESTRIS (Scalp)

| Klucz w kodzie | Klasa w kodzie | Co robi | Klucz w katalogu | Uwaga |
|---|---|---|---|---|
| **X-01** | NeuronRSI | RSI 14 — wykupienie/wyprzedanie | X-01 w kat. = EMA Cross ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **X-02** | NeuronStochRSI | Stochastic RSI — ekstrema | X-02 ✅ | Zgodny |
| **X-03** | NeuronMACD | MACD histogram — momentum | X-03 w kat. = CVD ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **X-04** | NeuronBBands | Bollinger Bands — zakres/wybicie | X-04 w kat. = VWAP ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **X-05** | NeuronEMACross | EMA(9/21) cross — kierunek | X-05 w kat. = OrderFlow ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **X-06** | NeuronWilliamsR | Williams %R — szybkie ekstrema | X-06 w kat. = ATR-Stop ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **X-08** | NeuronAwesome | Awesome Oscillator — momentum | X-08 ✅ | Zgodny |
| **X-09** | NeuronAccelerator | Accelerator — przyspieszenie | X-09 ✅ | Zgodny |
| **X-10** | NeuronHMA | Hull MA — szybki trend | X-10 ✅ | Zgodny |
| **X-11** | NeuronRVOL | Relative Volume — wolumen | X-11 ✅ | Zgodny |
| **X-17** | NeuronTRIX | TRIX — momentum wygładzone | X-17 ✅ | Zgodny |
| **X-12** | NeuronBBSqueeze | Bollinger Squeeze — detektor kompresji | X-12 ✅ | Zgodny |
| **X-18** | NeuronDonchian | Donchian Channel — wybicia | X-18 ✅ | Zgodny |
| **X-25** 🔱 | NeuronATRDeviation | ATR Z-score Kameleon (LONG/SHORT) | X-25 ✅ | Elitarny |
| **X-26** 🔱 | NeuronHAScalper | Heiken Ashi + zmienność | X-26 ✅ | Elitarny |

**Numery wolne w X (zaplanowane, brak kodu):**
X-07 → Williams %R (ale kod X-06=WilliamsR — X-07 czeka na inny wskaźnik)
X-12 BB Squeeze, X-13 Taker CVD, X-14 CVD Absorb, X-15 Net Volume, X-16 Volume Profile,
X-19..X-24 (planowane EXP), X-27..X-30 (rezerwa)

---

## 🌩️ LEGIO XII FULMINATA (Swing)

| Klucz w kodzie | Klasa w kodzie | Co robi | Klucz w katalogu | Uwaga |
|---|---|---|---|---|
| **XII-01** | NeuronADX | ADX — siła trendu | XII-01 w kat. = EMA Major ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **XII-02** | NeuronIchimoku | Ichimoku Cloud — trend+S/R | XII-02 w kat. = MACD ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **XII-03** | NeuronEMA50_200 | EMA(50/200) Golden/Death Cross | XII-03 w kat. = Bollinger ❌ | **ROZBIEŻNOŚĆ** — kat. zaktualizowany |
| **XII-04** | NeuronSupertrend | Supertrend — kierunek trendu | XII-04 ✅ | Zgodny |
| **XII-05** | NeuronFibonacci | Fibonacci retracement — złota strefa | XII-05 ✅ | Zgodny |
| **XII-07** | NeuronRSIDiv | RSI dywergencja — odwrócenia | XII-07 ✅ | Zgodny |

**Planowane XII (brak kodu):**
XII-05 Fibonacci, XII-06 SMC-OB, XII-07 RSI-Div, XII-08 OBV,
XII-09 Ichimoku (jest jako XII-02 w kodzie), XII-10 ADX (jest jako XII-01),
XII-11..XII-32 — wielka lista czeka na wdrożenie

---

## 🌊 WOLUMEN (V-XX)

| Klucz w kodzie | Klasa w kodzie | Co robi | W katalogu | Uwaga |
|---|---|---|---|---|
| **V-01** | NeuronOBV | OBV — potwierdzenie wolumenem | Katalog: XII-08 = OBV ❌ | Kod używa V-01, nie XII-08 |
| **V-02** | NeuronVWAP | VWAP — magnes cenowy | Katalog: X-04 = VWAP ❌ | Kod używa V-02 |
| **V-03** | NeuronCVD | CVD — kto kontroluje | Katalog: X-03 = CVD ❌ | Kod V-03 **WYCISZONY** (brak feedu) |
| **V-04** | NeuronVolumeAnomaly | Anomalia wolumenu | Brak w katalogu | Do dodania |
| **X-11** | NeuronRVOL | Relative Volume | X-11 ✅ | Zgodny |
| **VSA-01** | NeuronVSA | VSA No Supply/Demand | Katalog: VSA-01 ✅ | Zgodny |

---

## 🏛️ STRUKTURA / SMC (Smart Money Concepts)

| Klucz w kodzie | Klasa w kodzie | Co robi | W katalogu | Dostępny |
|---|---|---|---|---|
| **SMC-01** | NeuronOrderBlock | Strefy Order Block | XII-06 SMC-OB | ❌ WYCISZONY |
| **SMC-02** | NeuronFVG | Fair Value Gap | XII-16 SMC-FVG | ❌ WYCISZONY |
| **SMC-03** | NeuronBOS | BOS/CHoCH | XII-15 SMC-BOS | ❌ WYCISZONY |

*Wyciszone = wymagają stref od ZwiadowcaSMC. Ożywią się gdy dostarczymy feed barów + aktywujemy SMC.*

---

## 🧠 PSYCHOLOGIA / SENTYMENT (PSY-XX)

| Klucz w kodzie | Klasa w kodzie | Co robi | W katalogu | Dostępny |
|---|---|---|---|---|
| **PSY-01** | NeuronFundingExtreme | Funding Rate ekstremum | Brak PSY w kat. głównym | ❌ WYCISZONY |
| **PSY-02** | NeuronPanikaDetal | Panika drobnych graczy | Brak PSY w kat. głównym | ❌ WYCISZONY |
| **PSY-03** | NeuronFearGreed | Fear & Greed Index | PSY-01 FOMO w kat. ≈ podobny | ❌ WYCISZONY |
| **PSY-04** | NeuronOIDiv | OI Divergence | PSY-04 Stado w kat. ≈ podobny | ❌ WYCISZONY |

*Wyciszone = wymagają API (CryptoQuant, Coinglass, etc.)*

---

## ⛓️ ON-CHAIN (OC-XX)

| Klucz w kodzie | Klasa w kodzie | Co robi | W katalogu | Dostępny |
|---|---|---|---|---|
| **OC-01** | NeuronMVRV | MVRV Ratio (wycena on-chain) | III-01 MVRV | ❌ WYCISZONY |
| **OC-02** | NeuronSOPR | SOPR (realized profit) | III-05 SOPR | ❌ WYCISZONY |
| **OC-03** | NeuronPuellMultiple | Puell Multiple (mining) | III-08 Puell | ❌ WYCISZONY |
| **OC-04** | NeuronExchangeNetflow | Exchange Netflow | III-04 Netflow | ❌ WYCISZONY |

*Wyciszone = wymagają API (Glassnode, CryptoQuant). Katalog używa kluczy III-xx — kod używa OC-xx.*

---

## 🛡️ STRAŻ / ANTY-MANIPULACJA (A-XX) — KATEGORIA A

| Klucz w kodzie | Klasa w kodzie | Co robi | W katalogu | Dostępny |
|---|---|---|---|---|
| **A-01** | NeuronStopHunt | Stop hunt / liquidity sweep (knot + powrót) | A-01 StopHunt ✅ | ✅ aktywny |
| **A-02** | NeuronWickRejection | Odrzucenie poziomu długim knotem (pin bar) | A-02 (kat. FakeWall→A-08) | ✅ aktywny |

> **Litera A ożywiona 2026-06-02.** W WAGI_REZIMU: VOLATILE ×2.0, PANIC ×3.0.
> Dekorelacja (Prawo XVI): A-01↔A-02 r=+0.24, A↔RSI |r|<0.15 — filary nowej informacji.
> Katalogowy A-02 FakeWall (wymaga księgi zleceń L2) przeniesiony na A-08 — czeka na feed.

---

## 🧬 META-BRAMY I NEURONY BADAWCZE (poza klasycznym katalogiem)

> Neurony zrodzone z deep-researchu (kategorie C/D/F-VSA/H/L/N/R/Z) — nie mają
> katalogowego odpowiednika, klucz=klasa w kodzie. Pełne opisy: `MANIFEST_KODU.md`.

| Klucz w kodzie | Klasa w kodzie | KAT | WAGA | Dostępny | WSKAZNIK (Brama) |
|---|---|---|---|---|---|
| C-01 | NeuronRelativeStrength | C | 6 | ✅ | CROSS_RS |
| D-01 | NeuronPathSignature | D | 7 | ✅ | CLOSE_SERIES_20 |
| VSA-01 | NeuronVSA | F | 8 | ✅ | VSA |
| H-01 | NeuronHurstDFA | H | 7 | ✅ | HURST_DFA_100 |
| L-14 | NeuronUlcer | L | 7 | ✅ | ULCER_14 |
| VI-13 | NeuronATRLev | L | 8 | ✅ | ATR_14 |
| N-01 | NeuronPermutationEntropy | N | 7 | ✅ | PERM_ENTROPY_100 |
| N-02 | NeuronFracDiff | N | 6 | ✅ | CLOSE_SERIES_100 |
| AUG-01 | NeuronAugur | R | 6 | ✅ | EVENT_PROB_WZROSTU |
| BOCPD-01 | NeuronBOCPD | R | 6 | ✅ | CLOSE_SERIES_60 |
| CP-01 | NeuronChangePoint | R | 6 | ✅ | CLOSE_SERIES_60 |
| NEWS-01 | NeuronSentymentNews | R | 6 | ✅ | NEWS_SENTYMENT |
| RADAR-01 | NeuronRadarBTC | R | 6 | ✅ | BTC_TREND |
| RADAR-02 | NeuronDominacja | R | 5 | ✅ | BTC_DOMINANCJA |
| RADAR-03 | NeuronPrzeplyw | R | 5 | ✅ | PRZEPLYW_KAPITALU |
| RADAR-04 | NeuronStresKorelacji | Z | 6 | ✅ | STRES_KORELACJI |
| RADAR-05 | NeuronLeadBTC | R | 5 | ✅ | LEAD_BTC |
| Z-01 | NeuronToxicFlow | Z | 8 | ✅ | VPIN_50 |
| Z-02 | NeuronPumpDetect | Z | 7 | ✅ | OBV |
| Z-03 | NeuronBubbleCrash | Z | 9 | ✅ | BUBBLE_Z_200 |
| Z-04 | NeuronCascade | Z | 8 | ✅ | CASCADE_FLAG |
| Z-05 | NeuronDetektorRuchu | Z | 7 | ✅ | CLOSE_SERIES_20 |
| Z-06 | NeuronAmihudIlliquidity | Z | 6 | ✅ | AMIHUD_20 |
| Z-07 | NeuronPiCycleTop | Z | 6 | ✅ | PI_111 |

> **Meta-warstwy B (nie neurony):** `neutralizacja.py` (B-02), `meta_labeling.py` (B-01),
> `rezim_zmiennosci.py` (vol-gate W-340) — działają NAD Legatusem, nie głosują w roju.

### Uzupełnienia klasycznych legionów (dodane po 2026-06-02)

| Klucz w kodzie | Klasa w kodzie | KAT | WAGA | Dostępny | WSKAZNIK (Brama) |
|---|---|---|---|---|---|
| SES-01 | NeuronZegarSesji | S | 4 | ✅ | ZEGAR_SESJI |
| SES-02 | NeuronAzjaRange | S | 7 | ✅ | ASIA_RANGE |
| X-27 | NeuronValueConvergence | M | 6 | ✅ | VALUE_Z_200 |
| X-28 | NeuronKonfluencjaMultiTF | T | 7 | ✅ | MTF_4H_RSI_14 |
| XII-06 | NeuronOBZone | T | 6 | ✅ | CLOSE_PREV |
| V-05 | NeuronForceIndex | F | 7 | ✅ | FORCE_INDEX |
| V-06 | NeuronDeltaDivergence | F | 5 | ✅ | DELTA_DIV |
| V-07 | NeuronAnchoredVWAP | F | 5 | ✅ | AVWAP |
| V-13 | NeuronRealizedVol | V | 7 | ✅ | YANG_ZHANG_20 |
| V-14 | NeuronChoppiness | V | 7 | ✅ | CHOPPINESS_14 |
| VP-01 | NeuronVolumeProfile | S | 6 | ✅ | VPOC |
| A-03 | NeuronWashVol | A | 6 | ✅ | VOLUME |
| A-05 | NeuronBartPattern | A | 6 | ✅ | CLOSE_PREV |
| OC-05 | NeuronWashTrading | O | 8 | ✅ | WASH_SCORE_100 |
| K-01 | NeuronDXYTrend | K | 5 | 🔇 (dane makro) | DXY_MOM |
| K-02 | NeuronGoldBTC | K | 4 | 🔇 (dane makro) | GOLD_BTC_MOM |

| OC-06 | NeuronS2F | O | 6 | 🔇 (BTC_BLOCK_HEIGHT) | BTC_S2F |
| OC-07 | NeuronDaysToHalving | O | 7 | 🔇 (BTC_BLOCK_HEIGHT) | BTC_DAYS_TO_HALVING |
| OC-08 | NeuronBTCSupplyInflation | O | 5 | 🔇 (BTC_BLOCK_HEIGHT) | BTC_SUPPLY_INFLATION_PCT |
| EXP-13 | ZwiadowcaGARCH | V | 7 | ✅ (OHLCV) | GARCH_SIGMA |
| EXP-14 | ZwiadowcaKyleLambda | L | 6 | ✅ (OHLCV) | KYLE_LAMBDA |

---

## 📋 ZASADA NA PRZYSZŁOŚĆ

> **Gdy piszesz nową strategię:**
> 1. Zajrzyj do tej mapy → weź klucz z kolumny "Klucz w kodzie"
> 2. Sprawdź czy `DOSTEPNY=True` — wyciszony neuron nie głosuje
> 3. Dodaj do `rejestr_strategii.py` → Klucznik automatycznie sprawdzi spójność

> **Gdy dodajesz nowy neuron:**
> 1. Wybierz klucz z wolnych numerów w odpowiednim legionie
> 2. Zaktualizuj tę mapę
> 3. Uruchom `python narzedzia/audyt_spojnosci.py` — musi być exit 0

---

*Stan na: 2026-06-21 | Źródło prawdy: `imperium/legiony/rejestr.py` → `wszystkie_neurony()` (81 neuronów + 14 zwiadowców)*
