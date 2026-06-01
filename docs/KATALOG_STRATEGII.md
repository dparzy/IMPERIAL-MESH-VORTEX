# 📖 KATALOG STRATEGII IMPERIUM

> **Strategia = nazwana kolekcja neuronów w konkretnej konfiguracji.**
> Jak neuron = jeden wskaźnik, tak strategia = przepis złożony z wielu neuronów.
> System automatycznie dobiera strategię z katalogu pasującą do bieżącego "odcisku palca" rynku.

---

## 🔑 KLUCZ NUMERACJI STRATEGII

```
[LEGION]-[STYL]-[NUMER]

Legiony:
  X   = Legio X Equestris (Scalp)
  XII = Legio XII Fulminata (Swing)
  III = Legio III Augusta (Invest)
  VI  = Legio VI Ferrata (Leverage)
  IMV = Imperium Vortex (multi-legion, syntetyczne)

Style:
  TR = Trend (podążanie za trendem)
  RV = Reversal (odwrócenie)
  BK = Breakout (wybicie)
  RG = Range (handel w kanale)
  SC = Scalp (ultra-krótkie)
  MC = Macro (fundamentalna)
  LV = Leverage (lewarowane)
  HY = Hybrid (kombinacja stylów)

Numer: 001, 002, ... (kolejny w kategorii)
```

**Przykład:** `X-SC-001` = Legio X (Scalp), styl Scalp, numer 001

---

## 🧬 FORMAT STRATEGII

Każda strategia zawiera:

| Pole | Opis |
|------|------|
| **ID** | Klucz wg numeracji powyżej |
| **Nazwa** | Poetycka nazwa (tradycja Imperium) |
| **Twórca** | Trader/koncepcja źródłowa |
| **Legion** | Główny legion |
| **Interwał** | Timeframe(y) |
| **Warunki rynku** | Gdzie strategia działa najlepiej |
| **Neurony WEJŚCIE** | Lista neuronów — ich sygnały wyzwalają wejście |
| **Neurony WYJŚCIE** | Lista neuronów — ich sygnały wyzwalają wyjście |
| **Neurony FILTR** | Lista neuronów — muszą potwierdzić przed wejściem |
| **Dźwignia** | Zakres dźwigni |
| **R:R** | Minimalny Risk:Reward |
| **Wyniki historyczne** | Po przejściu przez Koloseum |
| **Status** | SZKIC / TESTOWANA / AKTYWNA / EMERYTOWANA |

---

## ⚔️ STRATEGIE LEGIO X EQUESTRIS (Scalp, M1–M15)

### X-SC-001 | "PIORUN CEZARA" | Trend Scalp
**Twórca:** IMV (syntetyczna)
**Interwał:** M5
**Warunki:** ADX > 25, wyraźny trend jednokierunkowy

**Neurony WEJŚCIE (wszystkie muszą być zgodne):**
- `X-01` EMA(9/21) cross → kierunek trendu
- `X-02` StochRSI < 20 (LONG) lub > 80 (SHORT) → momentum ekstremum
- `X-05` OrderFlow — Bid/Ask Imbalance → potwierdzenie presji

**Neurony FILTR (minimum 2/3 potwierdzenia):**
- `X-03` CVD → kto kontroluje rynek
- `X-04` VWAP → cena powyżej/poniżej VWAP

**Neurony WYJŚCIE:**
- `X-06` ATR×1.5 → dynamiczny stop-loss
- StochRSI > 70 (dla LONG) → sygnał wyjścia

**Dźwignia:** 5×–10×
**R:R:** minimum 1:2
**Status:** SZKIC

---

### X-SC-002 | "TORPEDA VWAP" | VWAP Bounce
**Twórca:** Strategia klasyczna (popularna wśród day-traderów)
**Interwał:** M5, M15
**Warunki:** Zakres dzienny, ruch od VWAP

**Neurony WEJŚCIE:**
- `X-04` VWAP Bounce — cena odbija od VWAP
- `X-02` StochRSI w ekstremum w momencie odbicia
- `X-05` OrderFlow — presja zgodna z odbiciem

**Neurony FILTR:**
- `X-01` EMA(9/21) — trend powinien wspierać odbicie

**Neurony WYJŚCIE:**
- Powrót do VWAP z przeciwnej strony
- `X-06` ATR stop

**Dźwignia:** 3×–7×
**R:R:** 1:1.5 minimum
**Status:** SZKIC

---

## ⚖️ STRATEGIE LEGIO XII FULMINATA (Swing, 4H–1D)

### XII-TR-001 | "ZŁOTY ORZEŁ" | Golden Cross Swing
**Twórca:** Klasyczna strategia giełdowa (Golden Cross)
**Interwał:** 4H, 1D
**Warunki:** EMA(50) przebija EMA(200) od dołu (Golden Cross)

**Neurony WEJŚCIE:**
- `XII-01` EMA(50/200) Golden Cross → główny sygnał
- `XII-04` Supertrend LONG → potwierdzenie
- `XII-08` OBV rośnie → wolumen potwierdza

**Neurony FILTR:**
- `XII-02` MACD histogram > 0 → momentum rośnie
- `XII-07` RSI bez dywergencji niedźwiedzich

**Neurony WYJŚCIE:**
- `XII-01` Death Cross lub EMA(50) ponownie poniżej EMA(200)
- `XII-04` Supertrend zmienia kierunek

**Dźwignia:** 1×–3× (swing — ostrożnie)
**R:R:** 1:3 minimum (długie trzymanie)
**Status:** SZKIC

---

### XII-RV-001 | "BUMERANG SENATU" | RSI Divergence Reversal
**Twórca:** Klasyczna analiza techniczna — divergence trading
**Interwał:** 4H
**Warunki:** Wyraźna dywergencja RSI przy ekstremach

**Neurony WEJŚCIE:**
- `XII-07` RSI + ukryta dywergencja → główny sygnał odwrócenia
- `XII-05` Fibonacci S/R — cena na kluczowym poziomie
- `XII-06` SMC — CHoCH (Change of Character) potwierdza

**Neurony FILTR:**
- `XII-03` Bollinger — kompresja zakończona (squeeze release)
- `XII-08` OBV — wolumen potwierdzający odwrócenie

**Neurony WYJŚCIE:**
- RSI powraca do strefy neutralnej (40–60)
- `XII-05` Kolejny poziom Fibonacci jako cel

**Dźwignia:** 2×–5×
**R:R:** 1:2.5
**Status:** SZKIC

---

### XII-BK-001 | "PIORUNOWA BRAMA" | Bollinger Squeeze Breakout
**Twórca:** John Bollinger + klasyczny squeeze play
**Interwał:** 4H, 1D
**Warunki:** BB squeeze (ściskanie), następnie gwałtowne wybicie

**Neurony WEJŚCIE:**
- `XII-03` Bollinger Squeeze → kompresja zmienności
- `XII-04` Supertrend + ADX rosnący → kierunek wybicia
- `XII-08` OBV wybicie → wolumen potwierdza

**Neurony FILTR:**
- `XII-01` EMA(50/200) → ogólny trend (wchodzimy w kierunku trendu)
- `XII-02` MACD — zgodny z kierunkiem wybicia

**Neurony WYJŚCIE:**
- BB rozszerza się do normalnego zakresu
- Momentum MACD słabnie

**Dźwignia:** 3×–8×
**R:R:** 1:2
**Status:** SZKIC

---

## 🏰 STRATEGIE LEGIO III AUGUSTA (Invest/Spot, 1D–1W)

### III-MC-001 | "KUMULACJA IMPERIUM" | On-chain Accumulation
**Twórca:** Willy Woo, Glassnode methodology
**Interwał:** 1D, 1W
**Warunki:** MVRV < 1, NUPL < 0 (strefa akumulacji)

**Neurony WEJŚCIE (minimum 3/4 potwierdzenia):**
- `III-01` MVRV < 1.0 → rynek poniżej wartości
- `III-02` NUPL < 0 → kapitulacja/akumulacja
- `III-05` SOPR < 1 → sprzedający realizują straty (koniec kapitulacji)
- `III-04` Exchange Netflow ujemny → BTC opuszcza giełdy (HODLing)

**Neurony FILTR:**
- `III-06` Halving Cycle — early/mid cykl
- `III-08` Global M2 Liquidity rośnie (makro wspiera)

**Neurony WYJŚCIE:**
- `III-01` MVRV > 3.7 → euforia/szczyt
- `III-02` NUPL > 0.75 → rynek przegrzany
- `III-03` Pi Cycle Top — sygnał szczytu

**Dźwignia:** 1× (SPOT — bez dźwigni w investingu)
**R:R:** 1:5+ (długi horyzont)
**Status:** SZKIC

---

## 🔥 STRATEGIE LEGIO VI FERRATA (Leverage/Futures)

### VI-LV-001 | "ŻELAZNY KLIN" | Funding Rate Contrarian
**Twórca:** IMV (syntetyczna) — kontrariańska strategia lewara
**Interwał:** 15M–1H
**Warunki:** Ekstremalne funding rate + sygnał odwrócenia

**Neurony WEJŚCIE:**
- `VI-01` FundingRate > 0.05% → za dużo longów (wchodzimy SHORT)
- `VI-04` Long/Short Ratio ekstremalne → sentyment przekupiony
- `VI-03` LiqHeatmap — duże skupisko liquidacji powyżej ceny

**Neurony FILTR:**
- `VI-02` Open Interest rośnie → pozycje narastają (gotowe do squeeze)
- `VI-05` Leverage Z-Score > 2σ → rynek ekstremalnie lewarowany

**Neurony WYJŚCIE:**
- FundingRate normalizuje się < 0.02%
- `VI-03` Heatmap — poziom likwidacji osiągnięty

**Dźwignia:** 5×–15× (zależnie od pewności)
**R:R:** 1:2
**Pretorianie:** OBOWIĄZKOWE WETO jeśli funding > 0.08%
**Status:** SZKIC

---

### VI-LV-002 | "KASKADA STALOWA" | Liquidation Cascade Hunt
**Twórca:** IMV (na podstawie obserwacji rynku futures)
**Interwał:** 15M
**Warunki:** Duże skupiska likwidacji widoczne na heatmapie

**Neurony WEJŚCIE:**
- `VI-03` LiqHeatmap — wyraźna kaskada likwidacji tuż powyżej/poniżej
- `VI-02` Open Interest wysoki → dużo pozycji do likwidacji
- `X-05` OrderFlow — presja w kierunku kaskady

**Neurony FILTR:**
- `VI-01` FundingRate neutralny (nie wchodzimy przy ekstremalnym fundingu)
- `XII-04` Supertrend → kierunek ogólny

**Neurony WYJŚCIE:**
- Po osiągnięciu poziomu kaskady
- `X-06` ATR stop

**Dźwignia:** 10×–20× (krótka pozycja, szybkie wyjście)
**R:R:** 1:1.5 (szybka transakcja)
**⚠️ RYZYKO NAJWYŻSZE**
**Status:** SZKIC

---

## 🌌 STRATEGIE IMPERIUM VORTEX (Multi-legion)

### IMV-HY-001 | "TRIUMWIRAT" | Multi-Legion Confluence
**Twórca:** VITRUVIUSZ / IMV
**Interwał:** M15 (wejście) + 4H (kontekst) + 1D (makro)
**Warunki:** Wszystkie 3 interwały zgodne

**Neurony WEJŚCIE (z 3 różnych legionów — pełna zgodność):**
- SCALP: `X-01` EMA cross + `X-02` StochRSI ekstremum
- SWING: `XII-04` Supertrend kierunek + `XII-02` MACD histogram
- INVEST: `III-01` MVRV strefa + `III-08` M2 kierunek

**Neurony FILTR (Dywizje Specjalne):**
- `STR-01` Stop Hunt Detector (Straż) → brak manipulacji
- `OB-01` Order Book Imbalance → wolumen potwierdza

**Neurony WYJŚCIE:**
- Sygnał wyjścia z DWÓCH legionów jednocześnie

**Dźwignia:** 3×–7× (ostrożność przy multi-legion)
**R:R:** 1:3
**Status:** SZKIC — priorytetowa do testowania

---

## 📈 STRATEGIE ŚWIATOWYCH TRADERÓW (Adaptacje)

### IMV-HY-002 | "METODA WYCKOFFA" | Wyckoff Accumulation/Distribution
**Twórca:** Richard Wyckoff (1873–1934)
**Interwał:** 4H, 1D
**Warunki:** Faza akumulacji lub dystrybucji widoczna na wykresie

**Neurony kluczowe:**
- `XII-06` SMC/Order Blocks → ślady smart money (modern Wyckoff)
- `XII-08` OBV → wolumen faz Wyckoffa
- `VI-02` Open Interest → interes instytucjonalny
- `XII-07` RSI + dywergencje → Springs/Upthrusts

**Fazy Wyckoffa:**
1. Phase A — Zatrzymanie trendu (SOPR < 1, NUPL spada)
2. Phase B — Budowanie pozycji (OBV rośnie dyskretnie)
3. Phase C — Spring/Shakeout (STR-01 Straż — manipulacja!)
4. Phase D — Potwierdzenie (EMA cross, MACD)
5. Phase E — Markup (wejście!)

**Dźwignia:** 1×–5×
**Status:** SZKIC

---

### IMV-HY-003 | "ICHIMOKU SHOGUN" | Ichimoku Full System
**Twórca:** Goichi Hosoda (1930s), adaptacja dla crypto
**Interwał:** 4H, 1D
**Warunki:** Wyraźna chmura Ichimoku, cena powyżej/poniżej

**Neurony kluczowe:**
- `XII-TR-ICH` *(planowany)* Ichimoku Cloud pozycja
- `XII-01` EMA trend → zgodność z chmurą
- `XII-08` OBV → wolumenowe potwierdzenie
- `X-02` StochRSI → timing wejścia

**Sygnały Ichimoku:**
- TK Cross (Tenkan-Kijun) + powyżej chmury → LONG
- Chikou powyżej historycznej ceny → potwierdzenie
- Kumo (chmura) cienka → słabszy sygnał

**Status:** SZKIC — wymaga nowego neuronu Ichimoku

---

### IMV-TR-001 | "STRATEGIA TURTLES" | Donchian Channel Breakout
**Twórca:** Richard Dennis / William Eckhardt (1983, Turtle Traders)
**Interwał:** 1D
**Warunki:** Wybicie 20-dniowego/55-dniowego kanału Donchiana

**Neurony kluczowe:**
- `XII-BK-DON` *(planowany)* Donchian Channel Breakout
- `XII-08` OBV → wolumen wybicia
- `III-08` M2 Liquidity → makro kontekst
- `X-06` ATR → wielkość pozycji (N = ATR)

**Zasady Turtles:**
- Wejście: wybicie 20-dniowego high/low
- Stop: 2N od wejścia (N = ATR20)
- Wyjście: wybicie 10-dniowego kanału w przeciwnym kierunku

**Dźwignia:** 1×–2×
**R:R:** 1:4+
**Status:** SZKIC

---

### IMV-RV-001 | "KONTRA SOROS" | Macro Reversal
**Twórca:** George Soros — teoria reflexivity, adaptacja crypto
**Interwał:** 1D, 1W
**Warunki:** Ekstremalne odchylenie od wartości fundamentalnej

**Neurony kluczowe:**
- `III-01` MVRV ekstremum (>3.7 lub <0.5)
- `III-08` M2 Global Liquidity → odwrócenie makro
- `VI-01` FundingRate ekstremum
- `AI-01` *(AI/ML)* → anomalia statystyczna w danych

**Zasada Sorosa:** Rynek przesadza w obu kierunkach. Extrem + zmiana narracji = okazja.

**Status:** SZKIC — wymaga neuronów AI/ML

---

# 📚 KSIĘGA AZJATYCKA — Strategie ze Skanu Rynku (STR-001 → STR-170)

> Źródło: `Księga Strategii i Taktyk — Azjatycki Skan Rynku` (v1.0–v2.0, 3000+ linków).
> **Zasada symbiozy:** nie kopiujemy linków — wyciągamy DZIAŁAJĄCĄ logikę i mapujemy na neurony.
> Każda strategia dostaje ID Imperium + odnośnik do źródła STR-xxx.
> Filtr: pomijamy czysty sprzęt/infrastrukturę (FPGA, DPDK, KDB-X) — to warstwa wykonania, nie sygnał.

---

## 🔬 A. Mikrostruktura i Sesje (Azja/Londyn/NY)

### IMV-SC-002 | "WSCHÓD SŁOŃCA" | Asian Session Liquidity Reversion
**Źródło:** STR-001, STR-006 (Session Liquidity Reversion, Asian Sunrise)
**Interwał:** M15–1H | **Warunki:** fałszywe wybicie z zakresu sesji azjatyckiej
**Neurony WEJŚCIE:**
- `STR-01` Stop Hunt Detector (Straż) → wykrywa fałszywe wybicie poza zakres sesji
- `X-04` VWAP → powrót do fair value
- `X-05` OrderFlow → wejście płynności
**Neurony FILTR:** `X-03` CVD (kto przejmuje kontrolę po wybiciu)
**Dźwignia:** 3×–7× | **R:R:** 1:2 | **Status:** SZKIC

### IMV-HY-004 | "CYKL AMD" | Accumulation-Manipulation-Distribution
**Źródło:** STR-002, STR-004 (AMD Absorption, FVG+Turtle Soup+Sessions)
**Interwał:** 1H–4H | **Warunki:** cykl AMD z konfiguracją sesyjną
**Neurony:** `XII-06` SMC (Order Blocks, FVG), `STR-01` Straż (manipulacja), `X-03` CVD (absorpcja), `XII-05` Fibo (fair value gap targets)
**Status:** SZKIC

---

## 🐋 B. Akumulacja, Dystrybucja, Wieloryby

### IMV-MC-002 | "CICHA AKUMULACJA" | Whale Accumulation Tracker
**Źródło:** STR-009, STR-075, STR-076, STR-077 (Korean Whales, Deep3, DexOne)
**Interwał:** 1D–1W | **Warunki:** wieloryby akumulują altcoiny w ciszy
**Neurony WEJŚCIE:**
- `WHL-01` Whale Netflow (Wieloryby) → duże portfele akumulują
- `III-04` Exchange Netflow ujemny → coiny opuszczają giełdy
- `XII-08` OBV rośnie dyskretnie → wolumen potwierdza
**Neurony FILTR:** `III-05` SOPR < 1 (sprzedający w stracie → koniec kapitulacji)
**Status:** SZKIC

> Strategia Wyckoffa = **IMV-HY-002** (już w katalogu wyżej). STR-007/STR-008 potwierdzają.

---

## 💱 C. Arbitraż i Anomalie Lokalne (Faza 3)

### IMV-AR-001 | "PREMIA KIMCHI" | Kimchi Premium Arbitrage
**Źródło:** STR-011, STR-014 (Kimchi Premium, DexCexRadar)
**Interwał:** Tick–1M | **Warunki:** różnica cen giełdy KR vs globalne
**Neurony:** `ARB-01` Cross-Exchange Spread, `ARB-02` Funding Spread
**Dźwignia:** 1× (arbitraż delta-neutral) | **Status:** FAZA 3 (multi-exchange)

### IMV-AR-002 | "ARBITRAŻ JENA" | BOJ Yen Carry Arbitrage
**Źródło:** STR-012 (Bitcoin vs Gold Yen Arbitrage)
**Neurony:** `MAK-01` BOJ/DXY (Makro), `III-08` M2 Liquidity
**Status:** FAZA 3

---

## 🧠 D. Psychologia i Zarządzanie Ryzykiem (REGUŁY ŻELAZNE)

> Te strategie to nie sygnały wejścia — to **prawa Pretorianów** wpisane na stałe w Kalkulator Lewara.

### REGUŁA AOA — "Nigdy więcej niż 30% straty"
**Źródło:** STR-018, STR-030 ($5K→$300M na BitMEX)
**Implementacja:** Pretorianie — twardy limit. Drawdown > 30% kapitału = STOP TRADING całkowity.
**Status:** ✅ DO WDROŻENIA w `kalkulator_lewara.py` (obecnie limit 10% — dodać twardy kill-switch 30%)

### REGUŁA BNF — "Rynek to system do czytania, nie do przewidywania"
**Źródło:** STR-019, STR-032 (Takashi Kotegawa $13K→$153M)
**Implementacja:** filozofia neuronów — interpretują dane (Prawo I), nie wróżą. Mean-reversion od ekstremów.

### REGUŁA MR. MILLION — "Im szybciej chcesz zarobić, tym wolniej musisz działać"
**Źródło:** STR-020, STR-031 ($200→$100M)
**Implementacja:** filtr cierpliwości Generała — minimum 5 zgodnych neuronów + przewaga >55%. Nie handlujemy szumu.

### REGUŁA KELLY — Position Sizing
**Źródło:** STR-033 (Chiński student $1K→$1.5M, Kelly-based sizing, Bayesian updating)
**Implementacja:** rozszerzyć `policz_rozmiar_pozycji()` o frakcję Kelly'ego ograniczoną do 2% (fractional Kelly).

### REGUŁA BUDŻETU RYZYKA — proporcjonalność do zmienności
**Źródło:** STR-058 (CXOBE — risk budget ∝ volatility)
**Implementacja:** rozmiar pozycji odwrotnie proporcjonalny do ATR (już częściowo w Kalkulatorze).

---

## 🏆 E. Klasyczne Techniki Mistrzów

### IMV-TR-002 | "PUDEŁKO DARVASA" | Darvas Box Theory
**Źródło:** STR-024 (Nicolas Darvas Box Theory)
**Interwał:** 1D | **Warunki:** cena buduje "pudełka" konsolidacji, wybicie w górę
**Neurony:** `XII-03` Bollinger (zakres pudełka), `XII-08` OBV (wolumen wybicia), `X-06` ATR (wysokość pudełka)
**Zasada:** kupuj wybicie szczytu pudełka, stop pod dołem pudełka. **Status:** SZKIC

### IMV-RG-001 | "STREET SMARTS" | Connors-Raschke Reversals
**Źródło:** WebSearch — Linda Raschke & Larry Connors "Street Smarts" (20+ setupów)
**Interwał:** M15–4H | **Warunki:** range, wyczerpanie momentum
**Neurony:** `X-02` StochRSI (ekstrema), `XII-07` RSI-Div (dywergencje), `X-04` VWAP (powrót do średniej)
**Kluczowe setupy:** "Holy Grail" (ADX>30 + pullback do EMA20), "Turtle Soup" (false breakout 20-dni)
**Status:** SZKIC — priorytet (sprawdzone setupy)

### IMV-TR-003 | "MISTRZ MINERVINI" | SEPA Momentum
**Źródło:** WebSearch — Mark Minervini "Think & Trade Like a Champion" (SEPA)
**Interwał:** 1D | **Warunki:** Trend Template (cena > MA50 > MA150 > MA200, wszystkie rosnące)
**Neurony:** `XII-01` EMA(50/200) układ, `XII-04` Supertrend, `XII-08` OBV (potwierdzenie wolumenem VCP — Volatility Contraction Pattern)
**Status:** SZKIC

### IMV-SC-003 | "DWULISTNY PULLBACK" | Al Brooks M2B/M2S
**Źródło:** WebSearch — Al Brooks (Two-legged Pullback to MA, 5-min charts)
**Interwał:** M5 | **Warunki:** trend + dwunożny pullback do EMA20
**Neurony:** `X-01` EMA(9/21) (kierunek+pullback), `X-05` OrderFlow (siła odbicia), `X-02` StochRSI (timing)
**Zasada Brooksa:** institutional piggybacking — wchodzimy po pullbacku w kierunku trendu. **Status:** SZKIC

### IMV-RG-002 | "RYTM LIVERMORE'A" | Pivotal Points
**Źródło:** WebSearch — Jesse Livermore (pivotal points, pyramiding)
**Interwał:** 1D | **Neurony:** `XII-05` Fibo (kluczowe poziomy), `XII-03` Bollinger (breakout), `PYR` Pyramiding Manager (STR-133)
**Status:** SZKIC

---

## 🚨 F. Wykrywanie Anomalii i Manipulacji (Straż)

> Mapują się na istniejącą dywizję Straż w `KATALOG_NEURONOW.md`.

### IMV-DEF-001 | "TARCZA WASH" | Wash Trading Detection
**Źródło:** STR-071, STR-072, STR-073 (NTU/Lund/Columbia — wash trading)
**Neurony:** `STR-WASH` (anomalne częstotliwości transakcji), `OB-01` Order Book (fałszywe ściany), analiza sieciowa
**Funkcja:** filtr — jeśli wolumen jest sztuczny, neurony wolumenowe tracą wagę. **Status:** SZKIC

### IMV-DEF-002 | "GÓRA LODOWA" | Iceberg Order Detector
**Źródło:** STR-120 (META_quant 4D Iceberg Detector)
**Neurony:** `OB-02` Iceberg (ukryte zlecenia), `X-05` OrderFlow
**Funkcja:** wykrywa duże ukryte zlecenia instytucji → sygnał kierunku smart money. **Status:** SZKIC

### IMV-DEF-003 | "OBROŁA ORACLE" | Oracle Manipulation Defense
**Źródło:** STR-100, STR-101 (Oracle front-run, Hot Wallet drain)
**Funkcja:** czysto obronna — ochrona kapitału, nie sygnał. **Status:** FAZA 3 (DeFi)

---

## 🌀 G. Detekcja Reżimu (serce Generała)

> Te strategie zasilają klasyfikację reżimu w `legatus.py` (`_dostosuj_wagi`).

### IMV-REG-001 | "ENTROPIA SHANNONA" | Entropy-Based Regime Switching
**Źródło:** STR-092 (Entropy-Based Regime, bez AI)
**Funkcja:** wykrywa reżim (TREND/RANGING) z entropii Shannona ceny. Niska entropia = trend, wysoka = chaos.
**Neurony:** `ENT-01` Shannon Entropy (Entropia) | **Status:** SZKIC — priorytet (prosty, elegancki)

### IMV-REG-002 | "FALKA" | Wavelet Transform Regime Detector
**Źródło:** STR-116, STR-125 (Wavelet Regime, Mei's Wavelet)
**Funkcja:** transformacja falkowa wykrywa zmianę cyklu/reżimu. **Neurony:** `ENT-02` Wavelet | **Status:** SZKIC

### IMV-REG-003 | "KONSENSUS WIELOINTERWAŁOWY" | Multi-Timeframe Regime Consensus
**Źródło:** STR-128 (MTF Regime Consensus)
**Funkcja:** sygnał DOPIERO gdy reżim zgodny na M15+4H+1D → redukcja fałszywek.
**Implementacja:** rozszerzenie trybu FOKUS Generała o multi-TF. **Status:** SZKIC — priorytet

### IMV-REG-004 | "WCZESNY MIKROSTRUKTURALNY" | Early Microstructure Regime
**Źródło:** STR-121 (Early Microstructure Detection, +18.6 kroków wyprzedzenia)
**Funkcja:** wykrywa reżim w arkuszu zleceń ZANIM cena się załamie. **Neurony:** `OB-03`, `X-05` OrderFlow | **Status:** SZKIC

---

## 📐 H. Zmienność i Fraktale

### IMV-RG-003 | "WYMIAR FRAKTALNY" | Fractal Dimension Volatility
**Źródło:** STR-104 (Fractal Dimension Volatility, "lepszy niż ATR")
**Funkcja:** wymiar fraktalny jako miara zmienności → lepszy sizing niż ATR.
**Neurony:** `ENT-03` Fractal Dimension | **Status:** SZKIC

### IMV-HY-005 | "PARADOKS PARRONDO" | Parrondo's Paradox
**Źródło:** STR-115 (Parrondo — "dwie przegrywające strategie = jedna wygrywająca", ocena 10/10)
**Funkcja:** naprzemienne stosowanie dwóch słabych strategii (np. mean-reversion + momentum) wg reżimu daje przewagę.
**Implementacja:** Generał przełącza strategie wg reżimu — to dokładnie nasza filozofia Kameleona!
**Status:** SZKIC — wysokopriorytetowy koncept teoretyczny

---

## 🤖 I. Strategie AI/ML (Faza 2+, dywizja AI/ML)

| ID Imperium | Źródło | Koncept | Mapowanie |
|-------------|--------|---------|-----------|
| IMV-AI-001 | STR-040/086/121 NEXUS | Samoewoluująca AI, przepisuje własny kod | Faza 4 — auto-tworzenie modułów |
| IMV-AI-002 | STR-042/085/123 CogAlpha | 21-agentowy alpha factory | Wzorzec dla rozbudowy Senatu |
| IMV-AI-003 | STR-088 Reflexion | Agent uczy się przez refleksję nad błędami | Feedback loop wag neuronów |
| IMV-AI-004 | STR-122/404 AgenticAITA | 4 agenci (Analityk/Risk/Egzekutor/Scheduler) debatują | Wzorzec Senatu Imperium ✅ |
| IMV-AI-005 | STR-124 Kazuki Ichimoku AI | Ichimoku + deep learning | Łączy z IMV-HY-003 |
| IMV-AI-006 | STR-065 NextCandle | Rozpoznawanie historycznych formacji świecowych | `AI` neuron pattern-match |
| IMV-AI-007 | STR-117 ArchetypeTrader | RL z prototypami + "mechanizm żalu" | Dopasowanie strategii do prototypu rynku |
| IMV-AI-008 | STR-119 TradeFM / STR-136 Kronos | Foundation model dla świec (GPT dla K-line) | Faza 4 |
| IMV-AI-009 | STR-121 Hallucination Detector | Wykrywanie halucynacji LLM | ✅ Bezpiecznik dla DeepSeek (Prawo I) |
| IMV-AI-010 | STR-127 Confidence Threshold | Odrzuca decyzje AI poniżej progu | ✅ Już w Generale (min_przewaga 0.55) |

> **Strategie filozoficzne** (do architektury, nie sygnały):
> STR-114 Go/MCTS, STR-115 Mushin (無心 pusty umysł), STR-122 Sun Tzu, STR-123 OODA Loop,
> STR-146 Active Inference (Bayesian Brain), STR-099 Wa Harmony Contrarian.

---

## 🎯 J. Risk Management i Egzekucja (do Kalkulatora/Pretorianów)

| ID | Źródło | Funkcja | Status |
|----|--------|---------|--------|
| IMV-RISK-001 | STR-126 Dynamic TP/SL Optimizer | TP/SL dostrojony do reżimu | ✅ rozszerzyć kalkulator_lewara |
| IMV-RISK-002 | STR-131 Martingale Blocker | Wykrywa i blokuje martyngał | ✅ Pretorianie |
| IMV-RISK-003 | STR-133 Pyramiding Manager | Bezpieczne dokładanie do pozycji | SZKIC |
| IMV-RISK-004 | STR-118 AI Safety Layer | Blokuje transakcje łamiące reguły | ✅ Pretorianie (Rust warstwa) |
| IMV-RISK-005 | STR-119 Adaptive Selector | Wybór strategii wg reżimu | ✅ serce Generała Legatusa |

---

## 🥇 K. Studia Przypadków — Legendarni Traderzy (do biblioteki wiedzy)

| Trader | Wynik | Klucz | Lekcja dla Imperium |
|--------|-------|-------|---------------------|
| **AOA** (BitMEX) | $5K → $300M | Max 30% straty, nie kochaj pozycji | Kill-switch 30% |
| **Takashi Kotegawa (BNF)** | $13.6K → $153M | 15h/dzień, analiza świec, mean-reversion | Cierpliwość + ekstrema |
| **Mr. Million (Sihoo Ahn)** | $200 → $100M | "Im szybciej chcesz, tym wolniej działaj" | Filtr cierpliwości |
| **比特皇** | $1.5K → $24M | Ekstremalne skalpowanie M1/M5 | Legio X Equestris |
| **Chiński student** | $1K → $1.5M (Polymarket) | Kelly sizing, Bayesian updating | Position sizing |
| **CZ** (WebSearch) | 1500 BTC @ $600 | Konwikcja + timing cyklu | Legio III Augusta |
| **Bitcoin Whale 2025** (WebSearch) | $54K → $9-10B | Cierpliwość > skalpowanie | HODL macro |
| **Jesse Livermore** | klasyk | Pivotal points, pyramiding, cut losses | Reguły ryzyka |
| **George Soros** | reflexivity | Rynek przesadza w obie strony | IMV-RV-001 |
| **Ray Dalio** | All Weather | Dywersyfikacja, ochrona kryzysowa | Alokacja portfela |

---

## 🔍 AUTOMATYCZNE DOPASOWANIE STRATEGII

Generał porównuje bieżący "odcisk palca" rynku z katalogiem strategii:

### Odcisk Palca Rynku (Market Fingerprint)

```python
@dataclass
class OdciskPalca:
    rezim: str           # TREND/RANGING/VOLATILE/PANIC
    interwal: str        # dominujący interwał sygnałów
    kierunek: str        # LONG/SHORT
    pewnosc: float       # moc sygnału
    funding: float       # funding rate
    wolumen_vs_avg: float # wolumen / średnia
    atr_vs_avg: float    # ATR / norma
    dominacja_btc: float # BTC.D
```

### Algorytm Dopasowania

```python
def dobierz_strategie(odcisk: OdciskPalca, katalog: list[Strategia]) -> list[Strategia]:
    """
    Zwraca 3 najlepiej pasujące strategie z katalogu.
    Pasowanie = ile warunków strategii spełnia obecny odcisk palca.
    """
    wyniki = []
    for strategia in katalog:
        dopasowanie = policz_dopasowanie(odcisk, strategia)
        wyniki.append((strategia, dopasowanie))
    return [s for s, _ in sorted(wyniki, key=lambda x: x[1], reverse=True)[:3]]
```

---

## 📊 WYNIKI KOLOSEUM (Arena testów)

Każda strategia przed aktywacją przechodzi:
- **Backtest:** minimum 30 dni danych historycznych
- **Sharpe Ratio:** > 1.0 (risk-adjusted return)
- **Max Drawdown:** < 15%
- **Win Rate:** > 45% (przy R:R 1:2 wystarczy)
- **Liczba transakcji:** minimum 30 (statystycznie istotne)

| ID | Nazwa | Win Rate | Sharpe | Max DD | Status |
|----|-------|----------|--------|--------|--------|
| X-SC-001 | Piorun Cezara | — | — | — | SZKIC |
| XII-TR-001 | Złoty Orzeł | — | — | — | SZKIC |
| IMV-HY-001 | Triumwirat | — | — | — | SZKIC |

> Wyniki zostaną uzupełnione po przejściu przez Koloseum (Faza 0 → Faza 1).

---

## 📊 PODSUMOWANIE KATALOGU

| Grupa | Strategii | Status |
|-------|-----------|--------|
| Rdzeń Legionów (X/XII/III/VI) | 8 | SZKIC |
| Multi-legion (IMV-HY) | 5 | SZKIC |
| Traderzy świata (Wyckoff/Turtles/Soros…) | 5 | SZKIC |
| Księga Azjatycka — Mikrostruktura/Sesje | 2 | SZKIC |
| Księga Azjatycka — Wieloryby | 1 | SZKIC |
| Księga Azjatycka — Arbitraż (Faza 3) | 2 | FAZA 3 |
| Reguły Ryzyka (AOA/BNF/Kelly) | 5 | DO WDROŻENIA |
| Klasyczne techniki mistrzów | 5 | SZKIC |
| Anomalie i manipulacje (Straż) | 3 | SZKIC |
| Detekcja reżimu (Generał) | 4 | SZKIC |
| Zmienność i fraktale | 2 | SZKIC |
| AI/ML (Faza 2+) | 10 | FAZA 2+ |
| Risk Management | 5 | częściowo ✅ |
| **RAZEM zmapowanych** | **~57** | rośnie |

> Pełna Księga Azjatycka liczy STR-001→STR-170. Wyciągnięto i zmapowano na neurony
> tylko te, które produkują sygnał lub regułę. Sprzęt (FPGA/DPDK), języki (Mojo/Zig)
> i frameworki wykonania trafiają do `ROADMAP_IMPERIUM.md` jako warstwa techniczna.

---

## 🔜 NASTĘPNE ŹRÓDŁA DO PRZESZUKANIA

Strategie nadal poszukiwane (kolejne skany internetu):
- **Larry Williams** — Williams %R, COT traders
- **Stan Weinstein** — Stage Analysis (4 fazy)
- **Paul Tudor Jones** — macro turning points, 200-day MA
- **Michael Covel** — trend following systems
- **Andreas Clenow** — systematic momentum (Stocks on the Move)
- **Nial Fuller** — price action setups (pin bar, inside bar)
- **Peter Brandt** — klasyczne formacje wykresowe
- **Stanley Druckenmiller** — koncentracja + makro

---

*"Strategia bez neuronu to plan bez żołnierzy. Neuron bez strategii to żołnierz bez rozkazu."* — VITRUVIUSZ
