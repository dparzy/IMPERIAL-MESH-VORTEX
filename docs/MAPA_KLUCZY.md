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

*Stan na: 2026-06-02 | Źródło prawdy: `imperium/legiony/rejestr.py` → `wszystkie_neurony()`*
