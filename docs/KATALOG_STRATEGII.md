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

# 🌍 MISTRZOWIE ŚWIATA — Strategie z WebSearch (v2.1)

> Źródło: Wyszukiwanie internetowe, czerwiec 2026.
> Zasada: wyciągamy działającą logikę → mapujemy na neurony Imperium.

---

## 📈 L. Larry Williams — COT + Williams %R + Sezonowość

### IMV-TR-004 | "INSIDERZY COT" | Williams COT Seasonal System
**Twórca:** Larry Williams (trader od 1970s, World Cup Champion)
**Interwał:** 1D | **Warunki:** sezonowe okno + ekstremum COT + %R sygnał

**Logika COT (Commitment of Traders):**
- Spekulanci rekordowo LONG + Commercials rekordowo SHORT → kontrariański SHORT
- Commercials (producenci/hedgers) wiedzą więcej niż spekulanci → śledź Commercials

**Neurony WEJŚCIE (wszystkie 3 warunki muszą być spełnione):**
- `MAK-COT` *(nowy neuron — Makro/Geo)* COT Extreme — commercials vs speculators spread
- `XII-07-WR` Williams %R(14) < -80 (wyprzedanie) → LONG lub > -20 (wykupienie) → SHORT
- `III-06` Halving Cycle / sezonowość → w historycznie silnym oknie sezonowym

**Neurony FILTR:**
- `III-08` M2 Global Liquidity → makro wspiera kierunek

**Zasada Bailout Exit:** wyjście przy pierwszym zyskownym otwarciu kolejnego dnia.

**Dźwignia:** 1×–3× | **R:R:** 1:3 | **Status:** SZKIC
**Nowy Neuron:** `MAK-COT` (Makro/Geo, waga 8) → *do dodania do KATALOG_NEURONOW.md*

---

## 📊 M. Stan Weinstein — Stage Analysis (4 Fazy)

### III-MC-002 | "CZTERY PORY ROKU" | Weinstein Stage Analysis
**Twórca:** Stan Weinstein ("Secrets for Profiting in Bull and Bear Markets", 1988)
**Interwał:** 1W (tygodniowy — "oath" 30W SMA) | **Warunki:** cykl 4 faz

**Cztery fazy:**
| Faza | Opis | 30W SMA | Akcja |
|------|------|---------|-------|
| 1 — Basing | Konsolidacja po spadkach | Spłaszcza się | Czekaj, akumuluj dyskretnie |
| 2 — Advancing | Wybicie powyżej SMA, wzrost | Rosnące | KUPUJ — tu jest zysk |
| 3 — Distribution | Plateau, spłaszczenie SMA | Zwalnia | Redukuj, szukaj wyjścia |
| 4 — Declining | Poniżej malejącego SMA | Malejące | NIGDY nie trzymaj (Weinstein: "złóż przysięgę") |

**Neurony WEJŚCIE (przejście Fazy 1→2):**
- `XII-01-W` EMA(200) tygodniowy → cena powyżej rosnącej SMA30W
- `XII-08` OBV rosnący → wolumen potwierdza wybicie z bazy
- `III-07` AltSeason Index → sektor rotacji

**Neurony WYJŚCIE (sygnał Fazy 3):**
- `XII-01` EMA cross w dół lub SMA30W spłaszcza → wychodzić
- `XII-07` RSI-Div niedźwiedzia → ostrzeżenie

**Dźwignia:** 1× SPOT | **R:R:** 1:5+ | **Status:** SZKIC

---

## 🦅 N. Paul Tudor Jones — 200D MA + Turning Points + 5:1 R:R

### IMV-TR-005 | "WIKING NA SKRAJU" | PTJ Macro Turning Points
**Twórca:** Paul Tudor Jones (Tudor Investment, 1987 Crash Prophet, +30 lat bez straty)
**Interwał:** 1D–1W | **Warunki:** cena na kluczowym turning point + 200D MA

**Trzy żelazne zasady PTJ:**
1. **200D MA jako north star** — nie wchodzić w cokolwiek poniżej 200D. Wyjście gdy cena przebija poniżej 200D (bez dyskusji).
2. **5:1 R:R minimum** — ryzykujesz 1%, celujesz w 5%. Możesz mylić się 4 razy z 5 i wciąż zarabiać.
3. **Odwrócenia > momentum** — "najlepsze pieniądze są na turning pointach, nie w środku trendu"

**Neurony WEJŚCIE:**
- `XII-01` EMA(200D) → cena powraca powyżej po korekcie (retest 200D = turning point)
- `XII-07` RSI-Div + ekstrema → identyfikacja turning point
- `III-08` M2 + makro → macro alignment

**Neurony FILTR:**
- `VI-01` FundingRate → emocje rynku (PTJ kontrariański przy ekstremach sentymentu)
- ADX < 20 (rynek zastygnięty) → czekaj na wyraźny sygnał

**Zarządzanie pozycją (PTJ):** wchodzi małą pozycją na turning point, dokłada (pyramiding) dopiero gdy rynek potwierdza kierunek.

**Dźwignia:** 1×–5× | **R:R:** 1:5 minimum | **Status:** SZKIC — priorytetowa

---

## 🔁 O. Michael Covel / Richard Dennis — Trend Following System

### IMV-TR-006 | "ŻELAZNA FALA" | Covel Systematic Trend Following
**Twórca:** Michael Covel (Trend Following), syntetyzuje Dennis/Eckhardt/Seykota/Marcus
**Interwał:** 1D | **Warunki:** wyraźny trend z niskim szumem

**Reguły systemu (syntetyczne):**
1. Wejście: cena przebija N-dniowy kanał Donchiana lub EMA cross (breakout)
2. Rozmiar pozycji: fixed fractional — max 2% ryzyka / ATR sizing
3. Stop: zawsze trailing stop oparty na ATR (nigdy stały poziom)
4. Wyjście: odwrócenie kanału (krótsza długość niż wejście)
5. Nie przewiduj — tylko śledź. Trend jest twoim przyjacielem.

**Neurony:**
- `XII-01` EMA(50/200) cross → kierunek trendu
- `XII-04` Supertrend + ADX > 25 → siła i potwierdzenie
- `X-06` ATR → trailing stop i sizing

**Różnica od Turtles (IMV-TR-001):** Covel dopuszcza krótszy interwał sygnału wejścia, Turtles sztywno 20D/55D.

**Dźwignia:** 1×–3× | **R:R:** 1:3+ | **Status:** SZKIC

---

## 📐 P. Andreas Clenow — Volatility-Adjusted Momentum

### IMV-TR-007 | "LOGARYTM CLENOWA" | Volatility-Adjusted Momentum Ranking
**Twórca:** Andreas Clenow ("Stocks on the Move", 2015)
**Interwał:** 1D (rebalancing tygodniowy) | **Warunki:** rynek powyżej 200D SMA

**Unikalna formuła momentum:**
```
Momentum_Score = Slope_90D × R² × Annualization_Factor
(regresja logarytmiczna 90D × determinacja = volatility-adjusted momentum)
```

**Filtr wykluczający (jeśli JEDEN spełniony → skip):**
- cena poniżej 100D MA
- gap > 15% w ostatnich 90 dniach
- rynek (BTC/SPY) poniżej 200D MA → STOP all entries (regime filter)

**Neurony SKANER (tryb SKANER Generała idealne zastosowanie):**
- `XII-01` EMA(200) → regime filter (rynek nad SMA)
- `XII-MOM` *(nowy neuron)* Momentum Score 90D → ranking aktywów
- `XII-04` Supertrend → kierunek

**Implementacja w SKANERZE:** zamiast skanować po pewności neuronów, rankinuj po Momentum Score i wybieraj top 3. Clenow to dokładnie "tryb SKANER" naszego Legatusa.

**Dźwignia:** 1× SPOT | **Rebalans:** tygodniowy | **Status:** SZKIC — priorytet (algorytmiczny, testowalny)
**Nowy Neuron:** `XII-MOM` Momentum Slope×R² (Swing, waga 7) → *do katalogu*

---

## 🕯️ Q. Nial Fuller — Price Action (Pin Bar + Inside Bar)

### IMV-RV-002 | "IGŁA FULLER" | Pin Bar Reversal at Key Level
**Twórca:** Nial Fuller (learntotradethemarket.com, "60-65% win rate na daily")
**Interwał:** 4H, 1D | **Warunki:** pin bar przy kluczowym S/R poziomie

**Kryteria pin bara (MUSZĄ być spełnione):**
- Ogon (wick) ≥ 2/3 całej świecy (≥ 66% zakresu)
- Ciało świecy w górnej 1/3 (bycza) lub dolnej 1/3 (niedźwiedzia)
- Pojawia się na kluczowym poziomie S/R, VWAP, Fibo lub EMA

**Neurony WEJŚCIE:**
- `PA-PINBAR` *(nowy neuron)* Pin Bar Detector — sprawdza geometrię świecy
- `XII-05` Fibonacci S/R → czy pin bar na kluczowym poziomie
- `X-04` VWAP → zgodność z fair value

**Combo Setup — Inside Bar po Pin Barze:**
- Pin bar → Inside Bar (matka-córka) = kompresja przed wybuchem
- Wejście na wybiciu z Inside Bar w kierunku Pin Bara

**Dźwignia:** 2×–5× | **R:R:** 1:2 (daily) | **Status:** SZKIC

### IMV-SC-004 | "MATKA I CÓRKA" | Inside Bar Continuation
**Neurony:** `PA-INSIDE` *(nowy neuron)* Inside Bar Detector, `XII-04` Supertrend (kierunek trendu = kierunek wybiecia)
**Warunki:** wyraźny trend + inside bar = kompresja przed kontynuacją
**Status:** SZKIC

**Nowe Neurony:** `PA-PINBAR` i `PA-INSIDE` (kategoria: S=SMC/Price Action, waga 6) → *do KATALOG_NEURONOW*

---

## 🎯 R. Stanley Druckenmiller — Koncentracja + Makro

### IMV-MC-003 | "BARIBAL" | Druckenmiller Concentrated Macro Bet
**Twórca:** Stanley Druckenmiller (Quantum Fund z Sorosem, 30 lat bez straty rocznej)
**Interwał:** 1W–1M | **Warunki:** wyjątkowa okazja makro + wysoka konwikcja

**Zasady Druckenmillera (REGUŁY PRETORIANÓW dla dużych pozycji):**
1. **Koncentracja** — gdy masz konwikcję, ładujesz duże. "35 pozycji = kłopot. 1 duża = uwaga."
2. **Nie hedguj wątpliwości** — jeśli potrzebujesz hedge, pozycja jest za duża lub zła → zamknij.
3. **Soros-lekcja** — "nie ważne czy masz rację, ważne ILE zarabiasz gdy masz rację"
4. **1-2 wielkie okazje rocznie** — czekaj na nie. Cała reszta to szum.
5. **Nie dywersyfikuj dla zasady** — dywersyfikacja ≠ automatycznie bezpieczeństwo

**Implementacja w Imperium:**
- Gdy `pewnosc_agregatu` > 0.92 + `RaportLegatusa.weto == False` + reżim TREND_STRONG → DRUCKENMILLER MODE: dźwignia ×1.5 powyżej tabeli, rozmiar pozycji do 5% kapitału (zamiast 2%)
- To jest wyjątek od zasady 2% — **TYLKO przy >92% pewności Generała**

**Dźwignia:** do 20× (wyjątkowo) | **R:R:** 1:5+ | **Status:** SZKIC

---

## 📊 S. Nowe Neurony z Przeglądu Rynku 2026

> Zidentyfikowane luki w KATALOG_NEURONOW.md na podstawie przeglądu wskaźników 2026.

### Nowe neurony do dodania do katalogu:

| Klucz | Neuron | Wskaźnik | Dywizja | Waga | Skąd |
|-------|--------|----------|---------|------|------|
| `MP-01` | Neuron TPO POC | TPO Market Profile — Point of Control | Order Book | 8 | 2026 review |
| `MP-02` | Neuron VRVP | Visible Range Volume Profile — VAH/VAL/POC | Order Book | 8 | 2026 review |
| `MP-03` | Neuron Super POC | TPO POC = Volume POC → magnes ceny | Order Book | 9 | 2026 review |
| `CVD-D` | Neuron CVD-Div | CVD Divergence (cena rośnie, CVD spada = ostrzeżenie) | Legio X | 9 | 2026 review |
| `NVT-S` | Neuron NVT Signal | NVT z wstęgami odchylenia std (overbought/oversold) | Legio III | 8 | on-chain 2026 |
| `RHODL` | Neuron RHODL Ratio | Realized HODL waves — long-term holder spending | Legio III | 9 | on-chain 2026 |
| `MAK-COT` | Neuron COT Extreme | Commercial vs Speculator spread ekstremum | Makro/Geo | 8 | Larry Williams |
| `XII-MOM` | Neuron MomScore | Slope×R² regresji 90D (Clenow momentum rank) | Legio XII | 7 | Clenow |
| `PA-PINBAR` | Neuron PinBar | Pin Bar geometryczny detektor (ogon ≥ 66%) | SMC/ICT | 6 | Nial Fuller |
| `PA-INSIDE` | Neuron InsideBar | Inside Bar detektor (matka-córka kompresja) | SMC/ICT | 6 | Nial Fuller |
| `PA-FAKEY` | Neuron Fakey | Fałszywe wybicie z inside bara + reversal | SMC/ICT | 7 | Nial Fuller |
| `WR-14` | Neuron Williams%R | Williams %R(14) ekstrema < -80 / > -20 | Legio X | 6 | Larry Williams |
| `MVRV-Z` | Neuron MVRV-Z | MVRV Z-Score (> 7 = top cyklu, < -0.5 = dołek) | Legio III | 9 | on-chain 2026 |

> **MVRV-Z** to ulepszona wersja MVRV-Ratio (III-01) z uwzględnieniem odchylenia standardowego — dokładniejsza na topach.
> **Super POC (MP-03)** = TPO POC pokrywa się z Volume POC — jeden z najsilniejszych magnesów ceny.
> **CVD-Div (CVD-D)** to rozszerzenie X-03 o wykrywanie dywergencji (kluczowe sygnały).

---

---

# 🌐 SKAN III — Klasyka, Arbitraż, ICT, Boty (v2.2)

> Źródło: WebSearch czerwiec 2026. Pokrywamy: chart patterns, basis trade, ICT, sentyment, boty, fale, stat-arb.

---

## 📐 T. Peter Brandt — Classical Charting (Edwards & Magee)

### IMV-BK-002 | "STARY KARTOGRAF" | Classical Chart Pattern Breakout
**Twórca:** Peter Brandt (40+ lat, szkoła Edwards & Magee, "no indicator soup")
**Interwał:** 1D, 1W | **Warunki:** czysta formacja klasyczna + wybicie z wolumenem

**Formacje (price-only, bez wskaźników):**
- Head & Shoulders (wyczerpanie popytu — break neckline = kapitulacja byków)
- Triangle (symetryczny/wstępujący — kompresja zmienności)
- Rectangle, Double Top/Bottom, Flag/Pennant (measured moves)

**Neurony WEJŚCIE:**
- `PAT-01` *(nowy)* Chart Pattern Detector — H&S, triangle, double top/bottom
- `XII-08` OBV → wolumen MUSI potwierdzić wybicie (institutional conviction)
- `XII-03` Bollinger → kompresja przed wybiciem (triangle = squeeze)

**Zasada Brandta:** wejście na decydującym zamknięciu poza granicą LUB breakout + retest (throwback).
**Ryzyko:** max 1-2% kapitału, stop na invalidacji formacji. Win rate ~50% — zarabia na measured moves.

**Dźwignia:** 2×–5× | **R:R:** measured move (często 1:3+) | **Status:** SZKIC
**Nowy Neuron:** `PAT-01` Chart Pattern Detector (SMC/Struktura, waga 7)

---

## 💰 U. Basis Trade / Cash-and-Carry (Delta-Neutral) — FAZA 3

### IMV-AR-003 | "ŻNIWIARZ FUNDINGU" | Cash-and-Carry Funding Harvest
**Źródło:** WebSearch — delta-neutral cash & carry (10-30% APY 2026, instytucje: Goldman/Citadel)
**Interwał:** ciągły | **Warunki:** dodatni funding rate na perpetualach

**Mechanika (rynkowo-neutralna):**
- LONG spot BTC + SHORT perpetual BTC (ta sama wielkość) → ruch ceny się znosi
- Zysk = zbierany funding rate (early 2026 BTC ~0.51%/8h = >70% annualized w szczytach)

**Neurony:**
- `VI-01` FundingRate → musi być dodatni i wysoki
- `ARB-02` Funding Spread → różnica fundingu między giełdami
- `VI-02` Open Interest → płynność do wejścia/wyjścia

**RYZYKO (Pretorianie monitorują):** funding może flipnąć ujemny w 1 interwale → pozycja z dochodu staje się kosztem. Wyjście gdy funding < 0.01%/8h przez 24h.

**Dźwignia:** 1× (delta-neutral) | **APY:** 10-30% | **Status:** FAZA 3 (multi-exchange)

---

## 🎯 V. ICT — Inner Circle Trader (Michael Huddleston)

### IMV-HY-006 | "SMART MONEY ICT" | Liquidity Grab + FVG + Order Block
**Twórca:** Michael J. Huddleston (ICT) — odczyt zachowań instytucji
**Interwał:** M15–1H (kill zones) | **Warunki:** sweep płynności → FVG → wejście

**Koncepty ICT (mapowanie na neurony):**
| Koncept ICT | Neuron Imperium |
|-------------|-----------------|
| Liquidity Grab/Sweep | `STR-01` Stop Hunt Detector (Straż) |
| Fair Value Gap (FVG) | `ICT-FVG` *(nowy)* — 3-świecowa luka imbalance |
| Order Block | `XII-06` SMC (Order Blocks) |
| BOS/CHoCH/MSS | `XII-06` SMC (Market Structure) |
| Kill Zone (sesje) | `SES-01` *(nowy)* Session/Killzone timer |
| Displacement | `ICT-DISP` *(nowy)* — agresywny ruch impulsowy |

**Sekwencja wejścia (ICT 2026 model):**
1. Cena wbija w pool płynności (sweep stopów) → `STR-01`
2. Displacement — agresywny ruch tworzy FVG → `ICT-FVG`
3. Powrót do FVG/Order Block = Optimal Trade Entry → wejście
4. Kill zone NY 8-11 EST = max aktywność instytucji → `SES-01`

**Dźwignia:** 3×–10× | **R:R:** 1:3+ | **Status:** SZKIC — priorytet (synergiczne z naszą Strażą)
**Nowe Neurony:** `ICT-FVG` (Fair Value Gap), `ICT-DISP` (Displacement), `SES-01` (Killzone timer)

---

## 😱 W. Sentyment — Fear & Greed + Crowd Positioning

### IMV-RV-003 | "KONTRA TŁUMU" | Fear & Greed Contrarian
**Źródło:** WebSearch — Crypto Fear & Greed Index (volatility 25% + momentum 25% + social + dominacja + trends)
**Interwał:** 1D | **Warunki:** ekstremum sentymentu

**Zasada kontrariańska (Warren Buffett crypto):**
- F&G < 20 (Extreme Fear) → strefa kupna (krew na ulicach)
- F&G > 80 (Extreme Greed) → strefa sprzedaży (euforia)

**Neurony:**
- `SENT-FG` *(nowy)* Fear & Greed Index — agregat sentymentu
- `VI-04` Long/Short Ratio → crowded longs = ryzyko spadku, crowded shorts = ryzyko wybicia
- `VI-01` FundingRate → emocje rynku futures
- `SENT-SOC` *(nowy)* Social Volume → hype mediów społecznościowych

**Dźwignia:** 2×–5× | **R:R:** 1:2 | **Status:** SZKIC
**Nowe Neurony:** `SENT-FG` (Fear&Greed), `SENT-SOC` (Social Volume)

---

## 🤖 X. Boty — Grid / DCA / Mean Reversion

### IMV-RG-004 | "SIATKA KAMELEONA" | Grid Trading Bot
**Źródło:** WebSearch — grid bot (sideways/choppy markets)
**Interwał:** dowolny | **Warunki:** rynek RANGING (boczny, brak trendu)

**Mechanika:** staggered buy/sell orders w zdefiniowanym kanale. Zarabia na oscylacji.
**Neurony FILTR (Generał aktywuje TYLKO w reżimie RANGING):**
- ADX < 20 → brak trendu (warunek konieczny dla grid)
- `XII-03` Bollinger → granice kanału = granice siatki
- `ENT-01` Shannon Entropy → wysoka entropia = chop = grid działa

**Parametry:** upper/lower bound, liczba poziomów (gęstość siatki), kapitał/poziom.
**⚠️ Pretorianie:** grid + trend = katastrofa. Wyłączyć gdy ADX > 25 (reżim TREND).
**Dźwignia:** 1×–3× | **Status:** SZKIC

### IMV-MC-004 | "MRÓWKA DCA" | DCA + Safety Orders
**Źródło:** WebSearch — DCA bot z safety orders
**Mechanika:** kupno stałych kwot w interwałach; safety orders przy spadkach (uśrednianie).
**Neurony:** `III-01` MVRV (strefa akumulacji), `SENT-FG` (kupuj strach)
**⚠️ Pretorianie:** to NIE martyngał — safety orders mają twardy limit (Martingale Blocker IMV-RISK-002).
**Status:** SZKIC

### IMV-RG-005 | "POWRÓT DO ŚREDNIEJ" | RSI Mean Reversion
**Źródło:** WebSearch — mean reversion (RSI<30 buy, return to neutral sell)
**Neurony:** `X-02` StochRSI, `WR-14` Williams%R, `X-04` VWAP (powrót do fair value)
**Warunki:** reżim RANGING | **Status:** SZKIC

---

## 🌊 Y. Fale i Geometria — Elliott / Wolfe / Harmonic

### IMV-RV-004 | "FALA ELLIOTTA" | Elliott Wave + Fibonacci
**Twórca:** Ralph Nelson Elliott (1938, "The Wave Principle")
**Interwał:** 4H–1W | **Warunki:** wyraźna struktura 5-3 fal

**Reguły żelazne Elliotta:**
- Fala 2 nigdy nie cofa >100% fali 1
- Fala 3 nigdy nie jest najkrótsza z impulsowych (1,3,5)
- Fala 4 nie wchodzi w terytorium fali 1

**Neurony:**
- `EW-01` *(nowy)* Elliott Wave Counter (auto-liczenie fal)
- `XII-05` Fibonacci → cele zniesień/rozszerzeń
- `X-02` StochRSI → potwierdzenie końca fali 5 (dywergencja)

**Najlepszy setup:** harmonic pattern na końcu fali 3 lub 5 → łapie cały ruch A-B-C.
**Status:** SZKIC | **Nowy Neuron:** `EW-01` Elliott Wave Counter (Struktura, waga 6)

### IMV-RV-005 | "FALA WOLFE'A" | Wolfe Wave Reversal
**Źródło:** WebSearch — Wolfe Wave (5-falowy wzorzec równowagi)
**Reguły:** fale 3-4 w kanale fal 1-2; Wave 1-2 = Wave 3-4 (symetria); Wave 4 między 1 a 2.
**Neurony:** `WW-01` *(nowy)* Wolfe Wave Detector, `XII-05` Fibonacci
**Status:** SZKIC | **Nowy Neuron:** `WW-01` (Struktura, waga 6)

---

## 📊 Z. Statistical Arbitrage — Pairs Trading (BTC/ETH)

### IMV-AR-004 | "BLIŹNIĘTA" | Cointegration Pairs Trading
**Źródło:** WebSearch — BTC/ETH pairs (16.34% APY, Sharpe 2.45, win 64.74%, beta 0.09-0.18)
**Interwał:** 1H–4H | **Warunki:** dwie skointegrowane kryptowaluty (BTC/ETH)

**Mechanika (rynkowo-neutralna):**
- Śledź spread/ratio BTC vs ETH (test ADF/Johansen na kointegrację)
- Z-Score spreadu > +2 → SHORT BTC, LONG ETH (oczekuj powrotu do średniej)
- Z-Score < -2 → odwrotnie
- Zamknij gdy Z-Score → 0

**Neurony:**
- `PAIR-01` *(nowy)* Pair Z-Score — spread dwóch aktywów w sigma
- `PAIR-02` *(nowy)* Cointegration Test — ADF/Johansen stationarity
- `CORR-01` Correlation (Breadth) → potwierdzenie korelacji par

**Zaleta:** market-neutral (beta ~0.1), zarabia niezależnie od kierunku BTC.
**Dźwignia:** 2×–5× (na obu nogach) | **APY hist.:** 16% Sharpe 2.45 | **Status:** FAZA 3
**Nowe Neurony:** `PAIR-01` (Z-Score par), `PAIR-02` (Cointegration test)

---

## 📊 SKAN IV — VSA, Intermarket, Opcje, DeFi (2026-06-01)

### XII-RV-003 | "WYCZERPANIE WILKA" | VSA Stopping Volume Reversal
**Źródło:** Tom Williams — Volume Spread Analysis
**Interwał:** 15M–4H | **Warunki:** koniec trendu, kulminacyjny vol

**Reguły:**
- Szukaj świecy z WOLUMENEM > 3× średniej 20-dniowej + SZEROKIM spreadem (wlicza Upthrust/SpreadUp)
- Następna świeca zamyka poniżej środka kulminacyjnej (potwierdzenie odwrotu)
- `VSA-04` StoppingVol = sygnał

**Neurony WEJŚCIE:** `VSA-04` StoppingVol  
**Neurony FILTR:** `VSA-01` NoSupply (lub `VSA-02` NoDemand w zależności od kierunku), `X-06` ATR-Stop  
**Neurony WYJŚCIE:** `X-02` StochRSI powrót do neutralnego  
**Dźwignia:** 3×–8× | **R:R:** 1:3 | **Status:** SZKIC

---

### XII-RV-004 | "FAŁSZYWY SZTURM" | VSA Upthrust Rejection
**Źródło:** Tom Williams — VSA Upthrust (False Breakout)
**Interwał:** 1H–4H | **Warunki:** obszary oporu, dystrybucja

**Reguły:**
- Cena wybija ponad kluczowy opór na wysokim vol → zamyka w dolnej 1/3 świecy
- `VSA-03` Upthrust = SHORT sygnał
- Potwierdź: Spread < 3% od strefy

**Neurony WEJŚCIE:** `VSA-03` Upthrust, `VP-02` ValueArea (VAH odrzucenie)  
**Neurony FILTR:** `VSA-02` NoDemand (brak popytu przed wybiciem)  
**Neurony WYJŚCIE:** `VP-01` VPOC (magnes cenowy)  
**Dźwignia:** 5×–10× | **R:R:** 1:2 | **Status:** SZKIC

---

### X-SC-004 | "PUSTA KSIĘGA" | Volume Profile VPOC Scalp
**Źródło:** Market Profile / Volume Profile (Peter Steidlmayer)
**Interwał:** M5–M15 | **Warunki:** konsolidacja wokół VPOC

**Reguły:**
- Cena wraca do strefy VPOC dziennego (±0.3%)
- `VP-01` VPOC jako magnes = wejście contra-trendem przy odchyleniu
- Wyjście przy powrocie do VPOC lub VAH/VAL

**Neurony WEJŚCIE:** `VP-01` VPOC, `X-04` VWAP (konwergencja)  
**Neurony FILTR:** `VPIN-01` VPIN < 0.5 (brak toksycznego flow)  
**Neurony WYJŚCIE:** `VP-02` ValueArea granice  
**Dźwignia:** 2×–5× | **R:R:** 1:2 | **Status:** SZKIC

---

### VI-LV-003 | "DETEKTOR TOKSYN" | VPIN Flash Risk Management
**Źródło:** Easley/López de Prado — Volume-Synchronized PIN
**Interwał:** M1–M5 | **Warunki:** wysokie VPIN = exit sygnał

**Reguły:**
- VPIN > 0.75 → natychmiastowe zmniejszenie pozycji lub exit (ryzyko flash-crash)
- VPIN < 0.30 → bezpieczne środowisko, powiększ pozycje
- SPREAD-01 BidAsk > +2σ → dodatkowe potwierdzenie wyjścia

**Neurony WEJŚCIE:** `VPIN-01` VPIN + `SPREAD-01` BidAsk (razem dają sygnał RYZYKO)  
**Funkcja:** Pretoriańska tarcza, nie samodzielna strategia  
**Dźwignia:** redukuje na żądanie | **Status:** PRETORIANIN (zawsze aktywny)

---

### VI-LV-004 | "ZAPORA GAMMA" | GEX Dealer Flip Strategy
**Źródło:** SpotGamma / Mott Capital — Gamma Exposure
**Interwał:** 1H–1D | **Warunki:** rynki z płynnymi opcjami (BTC/ETH)

**Reguły:**
- GEX ujemny (dealerzy short gamma) → amplifikacja ruchów → tendencja trend
- GEX > 0 (dealerzy long gamma) → tłumienie vol → strategia mean-reversion
- GEX Flip Level = kluczowy pivot
- SKEW-01 > +2σ → drogie puty → kontrariański LONG

**Neurony WEJŚCIE:** `GEX-01` GammaFlip  
**Neurony FILTR:** `SKEW-01` VolSkew, `PCR-01` PutCall (kontrariańskie ekstrema)  
**Neurony WYJŚCIE:** powrót GEX do strefy neutralnej  
**Dźwignia:** 5×–20× | **R:R:** 1:2.5 | **Status:** SZKIC (wymaga danych opcji)

---

### IMV-MC-003 | "CYKL MARKSA" | Howard Marks Dumb Money Cycle
**Źródło:** Howard Marks — "Mastering the Market Cycle" (2018)
**Interwał:** 1W–1M | **Warunki:** ekstrema cyklu rynkowego

**Reguły:**
- `HM-01` MarksCykl Score > +2σ → euforia, zbliżamy się do szczytu → redukuj ekspozycję, HEDGE
- `HM-01` Score < -2σ → panika / kapitulacja → AKUMULUJ (silne LONG)
- Potwierdzenie: `SENT-FG` FearGreed skrajny + `PCR-01` PutCall skrajny

**Neurony WEJŚCIE:** `HM-01` MarksCykl (ekstrema cyklu)  
**Neurony FILTR:** `SENT-FG` FearGreed + `PCR-01` PutCall  
**Legio:** III Augusta (Invest) / makro  
**Dźwignia:** 0× (akumulacja) lub hedge | **R:R:** 1:4+ (swing tygodniowy) | **Status:** SZKIC

---

### IMV-MC-004 | "SŁABY DOLAR" | DXY Macro Correlation Signal
**Źródło:** Intermarket Analysis (John Murphy)
**Interwał:** 1D–1W | **Warunki:** reżim korelacji BTC/DXY

**Reguły:**
- `DXY-01` DXYCorr: r < -0.6 + DXY spada 2%+/tydzień → LONG BTC (tradycyjny reżim)
- r > +0.4 + DXY rośnie + BTC rośnie = instytucjonalny napływ → też LONG
- r przeskakuje 0 w 20d oknie = zmiana reżimu → REDUCE SIZE, ostrożność

**Neurony WEJŚCIE:** `DXY-01` DXYCorr  
**Neurony FILTR:** `III-MACRO` (Wieloryby/Reżim) + `HM-01` MarksCykl  
**Dźwignia:** 2×–5× (macro overlay) | **R:R:** 1:3 | **Status:** SZKIC

---

### III-TR-003 | "ZIELONE RZEKI" | TVL Velocity DeFi Protocol Long
**Źródło:** DefiLlama — TVL Velocity + Protocol Revenue
**Interwał:** 1D–1W | **Warunki:** DeFi sezon, rosnący TVL

**Reguły:**
- `TVL-01` TVLVelocity > +10%/tydzień przez 2+ tygodnie → LONG token protokołu
- Revenue Week-over-Week > +30% przez 2+ tygodnie → dodatkowe potwierdzenie
- TVLVelocity flips ujemny → EXIT/NEUTRAL

**Neurony WEJŚCIE:** `TVL-01` TVLVelocity  
**Neurony FILTR:** `SENT-SOC` SocialVolume (hype nie wyprzedza TVL), `III-01` MVRV  
**Neurony WYJŚCIE:** TVLVelocity < 0 lub MVRV > 3.5  
**Dźwignia:** 1×–3× (spot/low lev) | **R:R:** 1:3 | **Status:** SZKIC

---

### IMV-AR-005 | "ROTACJA LEGIONÓW" | L1/L2 Relative Strength Rotation
**Źródło:** Sector rotation theory (Sharpe Terminal / CoinGecko 2026)
**Interwał:** 4H–1D | **Warunki:** rynek byka, narracja aktywna

**Reguły:**
- `RS-01` L1L2RS = SMA20(L1 index) / SMA20(L2 index) > poprzednie 20d max → LONG L1, SHORT L2
- RS ratio odwrócone → LONG L2, SHORT L1
- RS > +2σ od 50d MA → fade (reversion to mean)

**Neurony WEJŚCIE:** `RS-01` L1L2RS  
**Neurony FILTR:** `CORR-01` Correlation (sprawdź korelację pary), `SENT-SOC` SocialVolume (narracja)  
**Dźwignia:** 2×–5× (na obu nogach) | **R:R:** 1:2 | **Status:** SZKIC

---

### XII-TR-006 | "IMPET KRZYŻOWY" | Cross-Sectional Momentum 6m
**Źródło:** Jegadeesh-Titman (1993) — dostosowany do krypto (6m zamiast 12m)
**Interwał:** 1D–1W (rebalancing miesięczny) | **Warunki:** rynek byka

**Reguły:**
- Rankuj kryptowaluty po zwrotach 6-miesięcznych (wykluczając ostatni miesiąc)
- TOP 30% = LONG koszyk; BOTTOM 30% = SHORT koszyk (lub neutral)
- Rebalansuj co miesiąc
- `XCS-01` CrossMom Score crash (>-15% miesięcznie) → EXIT wszystkich pozycji momentum

**Neurony WEJŚCIE:** `XCS-01` CrossMom (ranking)  
**Neurony FILTR:** `HM-01` MarksCykl (tylko w bull/early bear), `SENT-FG` FearGreed > 30  
**Dźwignia:** 1×–3× | **R:R:** 1:2.5 | **Status:** SZKIC

---

### X-RV-003 | "CICHY RYNEK" | Bid-Ask Spread Collapse Entry
**Źródło:** Market Microstructure — płynność jako wejście
**Interwał:** M1–M5 | **Warunki:** wysoka płynność (spot Binance/MEXC)

**Reguły:**
- `SPREAD-01` BidAsk < -2σ (spread bardzo wąski) = idealne warunki do scalpu
- Połącz z kierunkiem z `X-03` CVD + `X-04` VWAP
- Wyjście gdy SPREAD-01 rośnie do neutralnego (płynność spada)

**Neurony WEJŚCIE:** `SPREAD-01` BidAsk (collapse = wejście ok), kierunek z `X-03` CVD  
**Neurony FILTR:** `VPIN-01` VPIN < 0.5 (brak toxic flow)  
**Neurony WYJŚCIE:** SPREAD-01 wzrósł > 0 (płynność pogarsza się)  
**Dźwignia:** 5×–20× | **R:R:** 1:1.5 (scalp, częste) | **Status:** SZKIC

---

## 🌅 SKAN V — CME Gaps, Azja Range, Strefy Czasowe, Arbitraż (2026-06-01)

### XII-RV-005 | "LUKA W MURZE" | CME Gap Fill Strategy
**Źródło:** CME Bitcoin/Ethereum Futures — gap fill (historyczne 77% fill rate)
**Interwał:** 1H–4H | **Warunki:** poniedziałek po weekendzie, gap > 0.5%

**Mechanika CME Gap:**
- Futures CME zamykają się w piątek o 17:00 CT, otwierają w niedzielę o 17:00 CT
- Przez ~53h rynek spot działa bez CME → powstaje różnica cen
- Gap = Cena niedzielnego otwarcia CME − Piątkowego zamknięcia CME
- 77% historycznych luk zostaje "wypełnionych" (cena wraca do poziomu luki)

**Reguły wejścia:**
- `SES-03` CMEGap > +0.5% (gap w górę) → cena powinna spaść do fills → **SHORT** do poziomu luki
- `SES-03` CMEGap < -0.5% (gap w dół) → cena powinna wzrosnąć → **LONG** do poziomu luki
- Wejście: NIE od razu po otwarciu, poczekaj na ruch w kierunku przeciwnym do luki (potwierdzenie)
- Wyjście: cena dotknęła poziomu luki (target) lub stop = 1.5× wielkości luki

**⚠️ WAŻNE (maj 2026):** CME uruchomiło handel 24/7 od 29.05.2026 → CME gaps PRZESTAJĄ powstawać. Strategia historyczna — 3 ostatnie luki niezapełnione. Stosuj ostrożnie, monitoruj czy nowe luki nadal się tworzą.

**Neurony WEJŚCIE:** `SES-03` CMEGap  
**Neurony FILTR:** `XII-05` Fibonacci (poziom luki jako fib target), `VPIN-01` VPIN < 0.6  
**Dźwignia:** 3×–8× | **R:R:** 1:2 | **Status:** SZKIC ⚠️ Monitoruj zmianę CME 24/7

---

### X-BK-003 | "PRZEBUDZENIE AZJI" | Asian Range Breakout
**Źródło:** Session-based trading — Asia Range (ICT + SMC adaptacja)
**Interwał:** M15–1H | **Warunki:** Londyn/NY session, po zamknięciu sesji azjatyckiej

**Mechanika:**
- Sesja azjatycka (00:00–08:00 UTC) = faza konsolidacji, wąski zakres
- Londyn otwiera o 07:00 UTC → instytucje "testują" granice azjatyckiego zakresu
- Przebicie Asia High → LONG (breakout z momentum Londynu)
- Przebicie Asia Low → SHORT (sweep of lows + reversal lub trend continuation)

**Reguły wejścia:**
- Wyznacz `SES-02` AzjaRange (High i Low sesji 00:00–08:00 UTC) na wykresie 15M
- Wejście: OCO powyżej Asia High (+0.1%) i poniżej Asia Low (-0.1%)
- Wyjście: 1.5× szerokości azjatyckiego zakresu od punktu wejścia
- Anuluj zlecenia o 10:00 UTC jeśli żadne nie zostało aktywowane
- **POMIŃ gdy Asia Range > 2% BTC** (za szeroki = słaby R:R)

**Neurony WEJŚCIE:** `SES-02` AzjaRange breakout  
**Neurony FILTR:** `SES-01` KillZone (London active), `X-11` RVOL (wolumen potwierdza breakout)  
**Neurony WYJŚCIE:** 1.5× Asia Range od wejścia lub `X-06` ATR-Stop  
**Dźwignia:** 5×–15× | **R:R:** 1:2 | **Status:** SZKIC

---

### IMV-AR-006 | "PODATEK OD PROWINCJI" | Funding Rate Cross-Exchange Arbitrage
**Źródło:** Funding rate arbitrage (delta-neutral, 10-30% APY)
**Interwał:** 8H (cykl funding: 00:00, 08:00, 16:00 UTC) | **Warunki:** duże rozbieżności funding

**Mechanika delta-neutral:**
- Jeśli Binance Funding > MEXC Funding o > 0.05% per 8h:
  - SHORT perp na Binance (zbierasz funding)
  - LONG perp na MEXC (płacisz mniej)
  - Pozycje się równoważą → zero ryzyko kierunkowe
- Zysk = różnica funding rate × 3 rozliczenia/dzień

**Kalkulacja profitability:**
```
Spread 8h = Funding_Binance - Funding_MEXC
Minimalny opłacalny spread = 0.03% (po prowizjach 2×0.05% = 0.1% round-trip)
Roczna stopa (APY) = Spread_8h × 3 × 365 × 100
Przykład: 0.05% spread × 3 × 365 = 54.75% APY (bez dźwigni)
```

**Neurony WEJŚCIE:** `BASIS-01` Basis + `VI-07` FundingRate (rozbieżność między giełdami)  
**Neurony FILTR:** `SPREAD-01` BidAsk (sprawdź czy spread wykonania nie zjada profitu)  
**Dźwignia:** 1×–3× (delta-neutral) | **R:R:** nie dotyczy (yield strategy) | **Status:** FAZA 2 (wymaga multi-exchange)

---

### X-SC-005 | "SESJA AZJI" | Asia Session Scalp (Vol Spike 01:00 UTC)
**Źródło:** Session microstructure — Tokyo institutional desks, 01:00 EST spike
**Interwał:** M1–M5 | **Warunki:** 00:30–02:00 UTC (Tokyo/HK institutional open)

**Obserwacja:** BTC widzi 2-5% swings podczas NY/Asia overlap (08:00-11:00 GMT = 09:00-12:00 CET).
Spike wolumenu o 01:00 EST (07:00 CET) → wejście instytucji Londynu.

**Reguły:**
- `SES-01` KillZone aktywna (London Kill Zone 07:00–09:00 UTC)
- `X-11` RVOL > 1.5× (ponadnormatywny wolumen)
- Kierunek z `X-03` CVD (kto dominuje w tym oknie)
- Wejście z `X-04` VWAP jako filtrem trendu dnia

**Neurony WEJŚCIE:** `X-11` RVOL spike + `SES-01` KillZone  
**Neurony FILTR:** `X-03` CVD kierunek + `X-04` VWAP  
**Dźwignia:** 5×–20× | **R:R:** 1:1.5 | **Status:** SZKIC

---

## 📊 AKTUALIZACJA PODSUMOWANIA KATALOGU (v2.3)

| Grupa | Strategii | Status |
|-------|-----------|--------|
| Rdzeń Legionów (X/XII/III/VI) | 8 | SZKIC |
| Multi-legion (IMV-HY) | 6 | SZKIC |
| Księga Azjatycka (A-K) | ~35 | SZKIC/FAZA 3 |
| Mistrzowie Świata (L-R) | 9 | SZKIC |
| Klasyka/Arbitraż/ICT/Boty/Fale (T-Z) | 15 | SZKIC/FAZA 3 |
| VSA/VP/VPIN/GEX/Opcje/Makro/DeFi (Skan IV) | 11 | SZKIC |
| CME Gap / Azja Range / Funding Arb / Sesje (Skan V) | 4 | SZKIC |
| Reguły Ryzyka (Pretorianie) | 5+ | DO WDROŻENIA |
| **RAZEM zmapowanych** | **~103+** | rośnie |

**Nowe neurony Skan V (+2):** SES-02 AzjaRange, SES-03 CMEGap → patrz KATALOG_NEURONOW.md (306 łącznie)  
**⚠️ Uwaga CME:** Od 29.05.2026 CME handel 24/7 — strategia CME Gap historyczna, monitoruj.

---

*"Strategia bez neuronu to plan bez żołnierzy. Neuron bez strategii to żołnierz bez rozkazu."* — VITRUVIUSZ
