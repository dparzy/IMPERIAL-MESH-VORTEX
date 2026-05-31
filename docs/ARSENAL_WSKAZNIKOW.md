# 🧮 ARSENAŁ WSKAŹNIKÓW — 157 narzędzi → mikro-neurony Imperium

> **Źródło:** Baza Wskaźników i Strategii Crypto v1.0–1.3 (DeepSeek)
> **Pełna surowa kopia:** `archiwum/Baza_wskaznikow_strategii_oryginal.md`
> **Łącznie:** 157+ pozycji (wskaźniki + strategie + mistrzowie + narzędzia)
>
> **Jak to czytać:** Każdy wskaźnik = potencjalny **mikro-neuron** w Legionie.
> Każda kategoria = obszar specjalizacji. Każdy styl = osobny Legion.
> **To jest otwarte** — wybieramy najlepsze dla nas, reszta w rezerwie.

---

## 🏛️ MAPOWANIE: kategoria → legion → kto liczy

| Kategoria wskaźników | Legion (styl) | Liczy | Mikro-neurony |
|---------------------|---------------|-------|---------------|
| Momentum (11) | wszystkie | Brama (TA-Lib) | Neuron RSI, Neuron MACD, Neuron Stoch... |
| Trend (18) | swing + invest | Brama (TA-Lib) | Neuron EMA, Neuron Ichimoku, Neuron ADX... |
| Zmienność (9) | scalp + leverage | Brama (TA-Lib) | Neuron ATR, Neuron Bollinger... |
| Wolumen/Flow (17) | scalp + swing | Brama + dane order flow | Neuron OBV, Neuron CVD, Neuron RVOL... |
| On-Chain (18) | invest | Oczy (Glassnode/CryptoQuant API) | Neuron MVRV, Neuron Exchange Flow... |
| Leverage/Futures (10) | leverage | Oczy + Brama | Neuron Funding Rate, Neuron OI, Neuron Liq Heatmap |

> **Zasada Prawa I:** Każdy neuron NIE liczy sam. Pyta Bramę. Brama liczy (TA-Lib),
> zwraca JSON + pieczątkę SHA-256. Neuron tylko INTERPRETUJE wynik.

---

## ⚔️ LEGIONY WG STYLU (interwały)

| Legion | Styl | Interwał | Kluczowe wskaźniki/strategie |
|--------|------|----------|------------------------------|
| **Scalp** (szybki oddział szturmowy) | Scalping | M1–M15 | EMA(9/21) cross, Stoch RSI, CVD, VWAP Bounce, Order Flow |
| **Swing** (wyważony) | Swing | 4H–1D | EMA(50/200) cross, MACD, Bollinger, Supertrend+ADX, Fibo, SMC |
| **Invest** (stabilny garnizon) | HODL/Spot | 1D–1W | MVRV, NUPL, Pi Cycle, DCA+On-chain, Halving Cycle |
| **Leverage** (żelazna jazda) | Futures/dźwignia | zmienne | Funding Rate, Open Interest, Liquidation Heatmap, Long/Short Ratio, GEX |

---

## 📊 KATEGORIA 1 — MOMENTUM (oscylatory, 11)

Mierzą siłę i szybkość zmian ceny. **Najlepsze dla: scalp + swing.**

| Wskaźnik | Zastosowanie | Styl |
|----------|--------------|------|
| **RSI** | dywergencje, wykupienie >70 / wyprzedanie <30 | uniwersalny |
| **MACD** | zmiany trendu (EMA12 vs EMA26) | swing, invest |
| **Stochastic RSI** | szybkie sygnały w ekstremach | scalp, swing |
| Williams %R | ekstrema wykupienia/wyprzedania | scalp |
| CCI | odchylenie od średniej | uniwersalny |
| TRIX | momentum z wygładzaniem | uniwersalny |
| DPO | cykle cenowe (bez trendu) | swing, invest |
| Ultimate Oscillator | momentum z 3 interwałów | uniwersalny |
| Awesome Oscillator | momentum (5 vs 34 SMA) | scalp, swing |
| Accelerator Oscillator | przyspieszenie momentum | scalp, swing |
| Chande Momentum | kierunek i siła momentum | uniwersalny |

## 📈 KATEGORIA 2 — TREND (18)

Kierunek i siła trendu. **Najlepsze dla: swing + invest.**

| Wskaźnik | Zastosowanie | Styl |
|----------|--------------|------|
| **SMA / EMA** | kierunek trendu | uniwersalny |
| **Ichimoku Cloud** | trend + S/R + momentum (5 linii) | swing, invest |
| **ADX** | siła trendu (>25 silny) — FILTR | uniwersalny |
| **Supertrend** | kierunek + dynamiczny stop-loss | swing |
| Aroon | początek i siła trendu | uniwersalny |
| Parabolic SAR | kierunek + stop-loss | swing |
| Alligator | uśpiony/aktywny trend | uniwersalny |
| HMA / ALMA | szybki trend, mało opóźnienia | scalp, swing |
| VWMA | trend z potwierdzeniem wolumenu | uniwersalny |
| Price Channel | wybicia S/R | swing |
| Continuation Index (Ehlers) | wczesna identyfikacja trendu | uniwersalny |
| Pring's Special K | długoterminowe cykle | invest |
| **SMC Indicators** (BOS/CHoCH, Order Blocks, FVG) | ślady smart money | swing |
| Crypto Breadth Engine | siła rynku (40 top coinów) | swing, invest |
| FlowTrinity (Dominance Rotation) | rotacja BTC/Stable/Alt | uniwersalny |

## 🌊 KATEGORIA 3 — ZMIENNOŚĆ (9)

Zakres i tempo wahań. **Najlepsze dla: scalp + leverage (stop-lossy).**

| Wskaźnik | Zastosowanie | Styl |
|----------|--------------|------|
| **ATR** | dynamiczne stop-lossy | uniwersalny |
| **Bollinger Bands** | wykupienie/wyprzedanie, wybicia | uniwersalny |
| Keltner Channels | trend + zakres (EMA+ATR) | swing |
| Donchian Channels | wybicia i trendy | swing |
| ATRP | stop-loss jako % ceny | uniwersalny |
| Standard Error Bands | jakość trendu | swing |
| Chaikin Volatility | zmiany zmienności | uniwersalny |
| VIX Fix | strach rynkowy, odwrócenia | uniwersalny |
| Ulcer Index | ryzyko spadkowe | invest |

## 💰 KATEGORIA 4 — WOLUMEN / ORDER FLOW (17)

Siła rynku przez aktywność. **Najlepsze dla: scalp + swing.**

| Wskaźnik | Zastosowanie | Styl |
|----------|--------------|------|
| **OBV** | potwierdzanie trendu wolumenem | uniwersalny |
| **CVD** (Cumulative Volume Delta) | order flow, kto kontroluje rynek | scalp, swing |
| **Volume Profile** (POC/VAH/VAL) | kluczowe poziomy S/R | uniwersalny |
| **RVOL** | czy ruch ma wsparcie wolumenu | uniwersalny |
| Accumulation/Distribution | akumulacja/dystrybucja | uniwersalny |
| Volume Oscillator | zmiany aktywności | uniwersalny |
| Net Volume / PVT / BoP | presja kupna/sprzedaży | uniwersalny |
| Spot Taker CVD (CryptoQuant) | agresywny popyt/podaż | scalp, swing |
| CVD Zones & Divergence Pro | strefy S/D + dywergencje (75%+ skutecz.) | scalp, swing |
| CVD Absorption | punkty zwrotne (absorpcja) | scalp |
| Apex Desk CVD MAX | kto kontroluje rynek | scalp |

## ⛓️ KATEGORIA 5 — ON-CHAIN (18)

Dane z blockchaina. **Najlepsze dla: invest (cykle).** Wymaga API (Glassnode/CryptoQuant).

| Wskaźnik | Zastosowanie | Styl |
|----------|--------------|------|
| **MVRV Ratio** | globalne szczyty/dołki (>3.7 drogo, <1 tanio) | invest |
| **NUPL** | fazy cyklu (>0.75 euforia, <0 kapitulacja) | invest |
| **SOPR** | realizacja zysków/strat | invest |
| **Exchange Flows / Netflow** | presja sprzedażowa (napływ na giełdy) | invest |
| **Pi Cycle Top/Bottom** | szczyty cyklu (MA111 vs MA350×2) | invest |
| Realized Price | średni koszt bazy inwestorów | invest |
| NVT Ratio | przewartościowanie sieci | invest |
| Reserve Risk / RHODL / CDD | okna akumulacji, ruchy HODLerów | invest |
| Active Addresses / Hashrate | zdrowie i adopcja sieci | invest |
| Exchange Whale Ratio | aktywność wielorybów | invest |
| OTC Desk Balance | presja przed ralllami | invest |
| Altcoin Season Index | rotacja kapitału (altseason >75) | invest, makro |
| Stablecoin Velocity | akumulacja vs aktywny trading | invest, makro |

## 🔥 KATEGORIA 6 — LEVERAGE / FUTURES (10)

Dedykowane dla dźwigni. **Tylko Legion Leverage.** Wysokie ryzyko!

| Narzędzie | Zastosowanie |
|-----------|--------------|
| **Liquidation Heatmap** | poziomy kaskadowych likwidacji (cele cenowe) |
| **Open Interest (OI)** | potwierdzanie siły trendu |
| **Funding Rate** | przeważenie long/short (>0.03% = za dużo longów) |
| **Long/Short Ratio** | sentyment, ekstrema = odwrócenie |
| OI + Funding Composite | ryzyko short/long squeeze |
| Leverage Z-Score | ekstremalne lewarowanie |
| Gamma Exposure (GEX) | poziomy przyciągania/odpychania (opcje) |
| Max Pain | magnes cenowy przed wygaśnięciem opcji |
| Liquidation Levels Estimator | zarządzanie ryzykiem likwidacji |

---

## 🧠 KATEGORIE ZAAWANSOWANE (v1.3 — instytucjonalne/naukowe)

- **Smart Money Concepts** (SMC, ICT): BOS/CHoCH, Order Blocks, FVG, Liquidity Sweeps
- **Intermarket**: Global M2 Liquidity (przesunięcie 105 dni vs BTC), DXY inverse, BTC Dominance vs ISM PMI
- **Entropia/Złożoność**: Complexity-Entropy Causality Plane, Tsallis Entropy Portfolio
- **Sezonowość**: BTC Monthly Returns Heatmap, Pi Cycle Oscillator, Halving Cycle

> **Uwaga:** Część v1.3 to systemy zamknięte (premium). Inspiracja, nie kopiowanie —
> budujemy własne odpowiedniki (Prawo: oryginalne narzędzia Imperium).

---

## 👑 MISTRZOWIE (wzorce strategii do adaptacji)

| Mistrz | Strategia | Adaptacja krypto |
|--------|-----------|------------------|
| Paul Tudor Jones | TA + ryzyko max 1-2% kapitału | BTC jako hedge |
| Jim Simons | algorytmy statystyczne, big data | HFT, arbitraż stat. |
| Ed Seykota | trend following + ryzyko | EMA cross + trailing stop |
| Bruce Kovner | ATR stop + multi-timeframe | pozycje na wielu interwałach |
| John F. Ehlers | filtry Laguerre, DSP | Continuation Index |
| **R.G. "JG"** | Omni-Wave, GUSI Pro, kompozyty on-chain | **← ten sam JG co DNSS!** modelowanie cyklu BTC |

---

## 🎯 REKOMENDACJA STARTOWA (Faza 0 — co bierzemy najpierw)

Najprostszy zestaw na pierwszy działający cykl (już mamy w kodzie):
- **Trend:** EMA(fast/slow) cross
- **Momentum:** RSI
- **Zmienność:** ATR (stop-loss)

Potem dokładamy po jednym neuronie, testując każdy w **Koloseum (Arenie Gladiatorów)**
zanim wejdzie do boju. Nigdy wszystko naraz (Prawo VII — buduj stopniowo).

---

*VITRUVIUSZ — "157 wskaźników to nie 157 botów. To 157 par oczu jednego organizmu."*
