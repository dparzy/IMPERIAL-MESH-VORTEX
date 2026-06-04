# 🧬 KATALOG MIKRO-NEURONÓW — Rój Imperium (299)

> **Źródło:** Pełny skan bazy wskaźników krypto (v1.0–3.0) + przegląd rynku 2026-06-01
> **Wzorzec:** DNSS (79-agentowy rój) — my idziemy dalej: 42 zaimplementowane, 299 skatalogowanych
> **Zasada (AKTUALNA — Prawo I + XIX):** Każdy neuron ma `interpretuj(wskazniki: dict) → SygnalNeuronu`.
> Czyta WYŁĄCZNIE z Bramy Kalkulatora (Prawo I). Nie liczy sam. Zero halucynacji (Prawo XV).
> Rój głosuje, Generał Legatus agreguje sygnał z wagami reżimowymi. Kod = prawda, katalog = plan.
>
> **Jak czytać klucz neuronu:**
> `[LEGION]-[NUMER]` + kategoria + waga
> Przykład: `X-02 | M | W7` = Legio X, neuron 2, Momentum, waga ważności 7
>
> **Kategorie:** M=Momentum, T=Trend, V=Zmienność, F=Flow/Wolumen, O=On-chain, L=Leverage, S=Struktura(SMC), A=Anty-manipulacja
> **Nowe:** K=Makro/Intermarket, E=Entropia/AI, R=Reżim/Sentyment, G=Geo/Regionalne
>
> ⚠️ **UWAGA — klucze w kodzie vs. katalog:**
> Klucze w tabelach poniżej oznaczone `✅` = zgodne z kodem (implementacja gotowa).
> Klucze bez oznaczenia = plan (brak kodu). Klucze `🔴` = planowane, numer zarezerwowany.
> **Pełna mapa rozbieżności:** `docs/MAPA_KLUCZY.md` — używaj jej gdy piszesz strategie.
> **Źródło prawdy kluczy:** `from imperium.legiony.rejestr import wszystkie_neurony`

---

## 📊 PODSUMOWANIE ROJU

| Legion | Nazwa | Styl | Neurony | Cel docelowy |
|--------|-------|------|---------|--------------|
| X | Equestris (Konny) | Scalp M1-M15 | 24 | 30+ |
| XII | Fulminata (Błyskawica) | Swing 4H-1D | 32 | 35+ |
| III | Augusta (Augustowski) | Invest 1D-1W | 38 | 40+ |
| VI | Ferrata (Żelazny) | Leverage | 19 | 20+ |
| ⚖️ | Neurony Wspólne (Anty-manip + Makro) | wszystkie | 16 | 20+ |
| **RAZEM (rdzeń legionów)** | | | **129** | **145+** |

> **142 w rdzeniu legionów + 132 w dywizjach specjalnych = 274 łącznie** (v2.1 — skan mistrzów świata + 2026).
> Pełne podsumowanie wszystkich dywizji na końcu dokumentu ("WIELKIE PODSUMOWANIE").
> 3,3× więcej niż DNSS (79). Lista żywa, rośnie.
> Ostatnia aktualizacja: 2026-06-01 (CAŁA baza wskaźników 1.0–3.0 przeskanowana)

---

## ⚡ LEGIO X EQUESTRIS — Konny (Scalp, M1-M15)

**Motto:** *"Szybki cios zanim wróg się obróci."*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| X-01 ✅ | RSI | RSI 14 | Wykupienie/wyprzedanie (klasyk) | W7 |
| X-02 ✅ | StochRSI | Stochastic RSI | Ekstrema wykupienia/wyprzedania | W6 |
| X-03 ✅ | MACD | MACD histogram | Zmiany momentum (konwergencja/dywergencja) | W7 |
| X-04 ✅ | BBands | Bollinger Bands | Zakres cenowy — ściskanie i wybicia | W7 |
| X-05 ✅ | EMA Cross | EMA(9/21) cross | Kierunek mikro-trendu M5 | W7 |
| X-06 ✅ | Williams %R | Williams %R | Szybkie ekstrema — wyprzedzający RSI | W5 |
| X-07 🔴 | ATR-Stop | ATR×1.5 dynamiczny SL | Dynamiczny stop-loss | W9 |
| X-08 | Awesome Osc | Awesome Oscillator | Momentum 5 vs 34 SMA | W5 |
| X-09 | Accelerator | Accelerator Oscillator | Przyspieszenie momentum | W4 |
| X-10 | HMA | Hull Moving Average | Szybki trend, mało opóźnienia | W6 |
| X-11 | RVOL | Relative Volume | Czy ruch ma wsparcie wolumenu | W7 |
| X-12 | BB Squeeze | Bollinger Squeeze M5 | Kompresja → wybicie scalp | W6 |
| X-13 | Taker CVD | Spot Taker CVD | Agresywny popyt/podaż | W7 |
| X-14 | CVD Absorb | CVD Absorption | Punkty zwrotne (absorpcja) | W6 |
| X-15 | Net Volume | Net Volume / BoP | Presja kupna/sprzedaży | W5 |
| X-16 | Volume Profile | POC/VAH/VAL M15 | Mikro poziomy S/R | W7 |
| X-17 | TRIX | TRIX szybki | Momentum z wygładzaniem | W4 |
| X-18 | Donchian | Donchian Channel M15 | Wybicia krótkoterminowe | W5 |

**Filtr Legionu:** ADX>20 (jest trend) + RVOL>1.2 (wolumen potwierdza)

---

## ⚖️ LEGIO XII FULMINATA — Błyskawica (Swing, 4H-1D)

**Motto:** *"Uderzamy rzadko, ale celnie."*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| XII-01 ✅ | ADX | ADX 14 | Siła trendu — filtr (>25 = trend) | W9 |
| XII-02 ✅ | Ichimoku | Ichimoku Cloud | Trend+S/R+momentum (5 linii) | W8 |
| XII-03 ✅ | EMA Major | EMA(50/200) golden/death cross | Główny kierunek trendu | W9 |
| XII-04 ✅ | Supertrend | Supertrend+ADX | Kierunek + siła trendu | W8 |
| XII-05 | Fibo | Fibonacci retracement | Poziomy S/R | W7 |
| XII-06 | SMC-OB | Order Blocks | Strefy smart money | W7 |
| XII-07 | RSI-Div | RSI + dywergencje | Ukryte odwrócenia | W7 |
| XII-08 | OBV | On-Balance Volume | Potwierdzenie wolumenem | W6 |
| XII-09 | Ichimoku | Ichimoku Cloud | Trend+S/R+momentum (5 linii) | W8 |
| XII-10 | ADX | ADX (>25 silny) | FILTR siły trendu | W8 |
| XII-11 | Parabolic SAR | Parabolic SAR | Kierunek + trailing stop | W6 |
| XII-12 | Aroon | Aroon | Początek i siła trendu | W5 |
| XII-13 | Keltner | Keltner Channels | Trend + zakres (EMA+ATR) | W6 |
| XII-14 | CCI | Commodity Channel Index | Odchylenie od średniej | W5 |
| XII-15 | SMC-BOS | BOS/CHoCH | Zmiana struktury rynku | W7 |
| XII-16 | SMC-FVG | Fair Value Gap | Luki do wypełnienia | W6 |
| XII-17 | Liquidity Sweep | Liquidity Sweep | Zgarnięcie płynności | W7 |
| XII-18 | VWMA | Volume-Weighted MA | Trend z potwierdzeniem wolumenu | W6 |
| XII-19 | CVD-Zones | CVD Zones & Divergence | Strefy S/D (75%+ skuteczność) | W7 |
| XII-20 | A/D | Accumulation/Distribution | Akumulacja/dystrybucja | W6 |
| XII-21 | Breadth | Crypto Breadth Engine | Siła rynku (top 40 coinów) | W6 |
| XII-22 | Dominance | FlowTrinity Rotation | Rotacja BTC/Stable/Alt | W7 |

**Filtr Legionu:** EMA(200) jako tło kierunku + ATR-based stop-loss + ADX>25

---

## 🏰 LEGIO III AUGUSTA — Augustowski (Invest/Spot, 1D-1W)

**Motto:** *"Garnizon trwa. Cierpliwość to broń."*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| III-01 | MVRV | MVRV Ratio | Globalny szczyt/dołek (>3.7 drogo) | W9 |
| III-02 | NUPL | NUPL | Faza cyklu (>0.75 euforia, <0 kapitulacja) | W9 |
| III-03 | Pi Cycle | Pi Cycle Top/Bottom | Szczyty cyklu (MA111 vs MA350×2) | W8 |
| III-04 | Netflow | Exchange Netflow | Presja sprzedażowa na giełdy | W8 |
| III-05 | SOPR | SOPR | Realizacja zysków/strat | W7 |
| III-06 | Halving | Halving Cycle | Pozycja w 4-letnim cyklu | W8 |
| III-07 | AltSeason | Altcoin Season Index | Rotacja BTC→alts (>75 altseason) | W7 |
| III-08 | M2 Liquidity | Global M2 (offset ~105 dni) | Makro płynność vs BTC | W8 |
| III-09 | Realized Price | Realized Price | Średni koszt bazy inwestorów | W7 |
| III-10 | NVT | NVT Ratio | Przewartościowanie sieci | W6 |
| III-11 | Reserve Risk | Reserve Risk | Okna akumulacji | W7 |
| III-12 | RHODL | RHODL Ratio | Ruchy starych HODLerów | W6 |
| III-13 | CDD | Coin Days Destroyed | Aktywacja uśpionych monet | W6 |
| III-14 | Active Addr | Active Addresses | Zdrowie i adopcja sieci | W6 |
| III-15 | Hashrate | Hashrate | Bezpieczeństwo sieci | W5 |
| III-16 | Whale Ratio | Exchange Whale Ratio | Aktywność wielorybów | W7 |
| III-17 | OTC Balance | OTC Desk Balance | Presja przed ralllami | W6 |
| III-18 | Stablecoin Vel | Stablecoin Velocity | Akumulacja vs aktywny trading | W6 |
| III-19 | Ulcer Index | Ulcer Index | Ryzyko spadkowe (drawdown) | W5 |
| III-20 | Pring K | Pring's Special K | Długoterminowe cykle | W5 |

**Filtr Legionu:** Min. 2 wskaźniki on-chain potwierdzają strefę (akumulacja/dystrybucja)

---

## 🔥 LEGIO VI FERRATA — Żelazny (Leverage/Futures) ⚠️

**Motto:** *"Żelazna dyscyplina albo śmierć."*
**⚠️ NAJWYŻSZE RYZYKO — Pretorianie mają WETO.**

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| VI-01 | Funding | Funding Rate | Przeważenie long/short (>0.03% za dużo longów) | W9 |
| VI-02 | OI | Open Interest | Potwierdzenie siły trendu futures | W8 |
| VI-03 | Liq Heatmap | Liquidation Heatmap | Poziomy kaskadowych likwidacji | W9 |
| VI-04 | Long/Short | Long/Short Ratio | Sentyment, ekstrema = odwrócenie | W7 |
| VI-05 | Lev Z-Score | Leverage Z-Score | Ekstremalne lewarowanie rynku | W8 |
| VI-06 | Max Pain | Max Pain | Magnes cenowy opcji | W6 |
| VI-07 | GEX | Gamma Exposure | Poziomy przyciągania/odpychania | W6 |
| VI-08 | OI+Funding | OI+Funding Composite | Ryzyko short/long squeeze | W8 |
| VI-09 | Liq Estimator | Liquidation Levels Estimator | Zarządzanie ryzykiem likwidacji | W8 |
| VI-10 | Basis | Futures Basis (premia) | Contango/backwardation | W6 |
| VI-11 | Taker LS | Taker Buy/Sell Ratio | Agresja na futures | W6 |
| VI-12 | Premium Idx | Premium Index | Odchylenie od spot | W5 |
| VI-13 | ATR-Lev | ATR (dla dźwigni) | Dynamiczny stop pod dźwignię | W9 |
| VI-14 | Squeeze Det | Squeeze Detector | Wykrycie zbliżającego się squeeze | W7 |

**Filtr Legionu (OBOWIĄZKOWY):**
- Funding Rate < 0.05% (brak ekstremalnego przeważenia)
- Pozycja ≤ 2% kapitału
- Stop-loss ZAWSZE przed wejściem
- Pretorianie MUSZĄ przepuścić

---

## ⚖️ NEURONY WSPÓLNE — Anty-manipulacja (wszystkie legiony)

> Te neurony chronią cały rój przed oszustwami rynku. Filtrują sygnały ZANIM trafią do Senatu.
> Szczegóły manipulacji: `docs/REGULAMINY_I_MANIPULACJE.md`

| Klucz | Neuron | Zadanie | Waga |
|-------|--------|---------|------|
| A-01 ✅ | StopHunt | Wykrywa polowanie na stop-lossy (knot + szybki powrót) | W8 |
| A-02 ✅ | WickRejection | Odrzucenie poziomu długim knotem (pin bar) — kod OHLCV. *Katalogowy FakeWall (księga L2) → przeniesiony, czeka na feed.* | W7 |
| A-03 | WashVol | Wykrywa fałszywy wolumen (wolumen ≠ ruch ceny) | W7 |
| A-08 🔴 | FakeWall | Fałszywe ściany w księdze zleceń (wymaga feedu L2) | W7 |
| A-04 | Spoofing | Wykrywa migoczące zlecenia (order book flickering) | W6 |
| A-05 | BartPattern | Wykrywa manipulację na niskiej płynności (noc/weekend) | W6 |
| A-06 | LiqCascade | Wykrywa inżynierię kaskady likwidacji (push do klastrów) | W8 |
| A-07 | MultiTF | Weryfikuje sygnał na wielu interwałach (manipulacja zwykle na 1) | W8 |

---

## 🧮 ZASADA PRAWA I — neuron nie liczy sam

```
Neuron NIGDY nie liczy wskaźnika samodzielnie.
   ↓
Pyta BRAMĘ KALKULATORA (fundament/brama_kalkulatora.py)
   ↓
Brama liczy (TA-Lib) → zwraca JSON + pieczątka SHA-256
   ↓
Neuron tylko INTERPRETUJE wynik → produkuje SygnalNeuronu
```

Schemat `SygnalNeuronu` → patrz `docs/LEGIONY_ARCHITEKTURA.md`.

---

## 📈 DROGA ROZWOJU ROJU

| Etap | Liczba neuronów | Status |
|------|-----------------|--------|
| Faza 0 | 3 (EMA+RSI+ATR) | ✅ Działa |
| **Teraz (katalog)** | **81 skatalogowanych** | 📋 Zaprojektowane |
| Faza 1 | 81 zaimplementowanych + testowanych w Arenie | 🟡 Cel |
| Faza 4 | System sam dodaje nowe neurony | 🔴 Autonomia |

> **Zasada:** Każdy neuron z katalogu wchodzi do boju TYLKO po teście w Koloseum.
> Nie implementujemy 81 naraz. Po jednym, kalibrujemy, sprawdzamy w Arenie (Prawo VII).

---

## 🔍 GDZIE SZUKAMY NOWYCH NEURONÓW

Rój rośnie. Alchemik Imperium (Claude) stale obserwuje:
- GitHub (nowe biblioteki wskaźników)
- TradingView (nowe publiczne skrypty Pine)
- Badania naukowe (arXiv — entropia, ML w tradingu)
- Społeczności (nowe koncepty SMC/ICT, on-chain)

Gdy pojawi się coś czego NIE mamy w katalogu → zgłaszamy lukę → badamy → testujemy w Arenie → dodajemy.

---

---

## ⚡ LEGIO X EQUESTRIS — Rozszerzenie (Scalp, v1.2+)

*Nowe neurony z bazy v1.2 i v1.3 — zaawansowany order flow i AI scalp*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| X-19 | BubbleFlow | Bubble Flow Tron System | Wykrywa absorpcję wolumenu + silne pchnięcie kierunkowe na M15 | W7 |
| X-20 | AIOrderFlow | AI Probabilistic OrderFlow Scalper | 3-czynnikowy scoring: OI imbalance + struktura + RSI bias | W7 |
| X-21 | FlowMatrix | Flow Matrix Pro (CartelConsole) | Instytucjonalne nierównowagi order flow na danych tickowych | W8 |
| X-22 | BigTrades | BigTrades Quant Analyzer | Detekcja absorpcji ważonej wolumenem + aktywność inst. | W7 |
| X-23 | AetherVol | AetherEdge Volume Surge Detector | Klasyfikuje skoki wolumenu REALNY/SZUM + BUY/SELL | W6 |
| X-24 | WicklessC | xGhozt Wickless Candles | Świece bez knotów → wyczerpanie i słabe ruchy cenowe | W5 |
| X-25 | ATRDeviation 🔱 | Arsi Smart Buy Sell (odtworzony+naprawiony) | Z-score odchylenia ceny od średniej znorm. ATR. DWA tryby: RANGING→mean-rev, TREND→momentum (Kameleon). MinDisplacement 1.0 ATR, filtr ADX. ZAIMPLEMENTOWANY w kodzie | W6 |
| X-26 | HAScalper 🔱 | MSX Hybrid Heiken Scalper (odtworzony+naprawiony) | Kolor+kształt świec HA (bez repainting) + momentum. Filtr Volatility_Index (ATR/MidMA20) blokuje konsolidację. DWA tryby: aggressive/conservative. Naprawiona tautologia oryginału. ZAIMPLEMENTOWANY | W7 |

---

## ⚖️ LEGIO XII FULMINATA — Rozszerzenie (Swing, v1.2+)

*Nowe neurony: SMC instytucjonalne, ICT, wielointerwałowe hybrydowe*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| XII-23 | SMC-Full | SMC Institutional Order Flow | BOS/CHoCH + OB + FVG + Liq Sweeps + Premium/Discount zones | W8 |
| XII-24 | RaidReverse | Raid & Reverse Liquidity Engine | Sweepy płynności + potwierdzenie Market Structure Shift | W8 |
| XII-25 | ICT-Turtle | ICT Turtle Soup | Fałszywe wybicia poprzednich szczytów/dołków | W7 |
| XII-26 | SMT-Div | P1asebo SMT+ Divergence | Dywergencja BTC vs IBIT/MSTR/NQ → strefy odwrócenia | W7 |
| XII-27 | Trinity | Trinity Codes Harmonic Flow | EMA 111/333/666/798 + MFI z progami pump/dump + box 444 | W7 |
| XII-28 | ContIdx | Continuation Index (Ehlers) | Filtry Laguerre — wczesna identyfikacja trendu, zakres -1..+1 | W7 |
| XII-29 | ZenithSMC | Zenith Market Structure (ICT) | Wielomodelowy BOS/CHoCH/OB/FVG wizualizacja | W6 |
| XII-30 | MTFBias | MTF Market Structure Bias | Multi-timeframe alignment — filtr handlu przeciw trendowi | W7 |
| XII-31 | VolProfExt | Volume Profile HVN/LVN Extension | HVN/LVN rzutowane w przyszłość jako S/R | W6 |
| XII-32 | AuroraComp | Aurora Compass (NVI-weighted VP) | Profile wolumenu ważone NVI — ślady instytucjonalne | W6 |

---

## 🏰 LEGIO III AUGUSTA — Rozszerzenie (Invest, v1.2+)

*Nowe neurony: on-chain zaawansowane, makro, sezonowość, AI/on-chain kompozyty*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| III-21 | GUSI | GUSI Pro (Adaptive Cycle Risk) | Kompozyt on-chain 0-100: >97 szczyt, <2.5 akumulacja | W9 |
| III-22 | M2Corr | Global M2 Liquidity (offset 105d) | Makropłynność vs BTC z przesunięciem 105 dni | W8 |
| III-23 | Wyckoff | ADCI Wyckoff Cycle Index | Faza cyklu: 0-3=akumulacja, 30-70=trend, 70-100=dystrybucja | W8 |
| III-24 | Season | BTC Monthly Returns Heatmap | Historyczna sezonowość miesięczna → warunki rynkowe | W7 |
| III-25 | PiOscil | AV BTC Pi Cycle Oscillator | Oscylator Pi Cycle + ATH/halving markers | W8 |
| III-26 | WhaleWatch | Unusual Whales Crypto Premium | Whale activity + derivatives sentiment tracking | W7 |
| III-27 | OTCDesk | Bitcoin Total OTC Desk Balance | Odpływy OTC → często poprzedzają ralle | W7 |
| III-28 | DXYInv | DXY Inverse Correlation | USD spada → krypto rośnie (risk-on/off) | W7 |
| III-29 | ISM-DOM | BTC Dominance vs ISM PMI | Słabość ekonomiczna → BTC dominacja rośnie | W6 |
| III-30 | MVRV-Z | MVRV Z-Score (DEMA smoothed) | Znormalizowany MVRV jako sygnał trendowy | W8 |
| III-31 | NUPL-Z | SD Median NUPL-Z | NUPL w postaci trend-following, potwierdzenie on-chain | W8 |
| III-32 | NVT-Sig | NVT Signal (Glassnode) | Kapitalizacja vs wolumen transferów → over/undervaluation | W7 |
| III-33 | SmartFlow | Smart Money Flow (Exchange + TVL) | Kompozyt: exchange flows + TVL → smart money tracking | W7 |
| III-34 | FG-Quant | Advanced Fear & Greed (Quant v6) | Smart money vs retail dystrybucja, skala 0-100 | W6 |
| III-35 | Breadth40 | Crypto Market Breadth Engine (40 coins) | Ile z top 40 krypto w trendzie wzrostowym | W7 |
| III-36 | BreadthRisk | Crypto Breadth Risk Planner | Czy koszyk szeroko uczestniczy vs wewnętrznie słabnie | W7 |
| III-37 | FlowTrin | FlowTrinity Capital Rotation | Rotacja BTC/Stable/Alt — dominance oscillators + histogram | W8 |
| III-38 | OTCReversal | OTC Desk Flow Reversal Strategy | OTC odpływy + niski MVRV → smart money absorbuje | W7 |

---

## 🔥 LEGIO VI FERRATA — Rozszerzenie (Leverage, v1.3+)

*Nowe neurony: instytucjonalne strategie opcyjne, delta-neutral, GEX*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| VI-15 | DeltaNeutral | Delta-Neutral Funding Arbitrage | Long spot + short perpetual → zysk z funding (8-20% APY) | W6 |
| VI-16 | GEX-Dealer | Gamma Exposure Dealer Hedging | GEX+ → dealerzy tłumią zmienność; GEX- → accelerują | W8 |
| VI-17 | OI-Fund-Comp | OI + Funding Composite (v2) | Ryzyko squeeze z dynamicznym progiem | W8 |
| VI-18 | BigTrades-F | BigTrades na Futures | Duże transakcje futures → aktywność inst. na dźwigni | W7 |
| VI-19 | FlowMatLev | Flow Matrix Pro (Futures) | Nierównowagi order flow specyficznie dla futures | W7 |

---

## ⚖️ NEURONY WSPÓLNE — Rozszerzenie (Makro + AI + Geo)

> Nowe kategorie: K=Makro/Intermarket, E=Entropia/AI, R=Reżim/Sentyment, G=Geo/Regionalne, N=Entropia/Informacja (Permutation Entropy — meta-brama chaosu, W-054)

| Klucz | Kat | Neuron | Zadanie | Waga |
|-------|-----|--------|---------|------|
| A-08 | K | CECP Entropy | Complexity-Entropy plane — reżim chaotyczny vs efektywny | W6 |
| A-09 | K | Intermarket DICT | Korelacje w czasie rzeczywistym: akcje/obligacje/commodities/krypto | W7 |
| A-10 | A | Inst. Order Flow Det. | Wykrywa dystrybucję vs absorpcję instytucjonalną | W7 |
| A-11 | E | AetherEdge KNN | KNN na 6-dim fingerprint rynku → prawdopodobieństwo kierunkowe | W7 |
| A-12 | E | Kronos K-Line LLM | Open-source model bazowy K-line (AAAI 2026) — predykcja szeregów · pełny opis: REJESTR_INSPIRACJI.md | W6 |
| A-13 | R | CFGI Sentiment | Indeks sentymentu co 15min (wolumen+zmienność+dominacja+wieloryby) | W6 |
| A-14 | R | MTPI OTHERS.D | Siła trendu całego segmentu alt (spoza top 10) — 8 sygnałów | W6 |
| A-15 | G | Kimchi Premium | Premia koreańska BTC/ETH → rotacja kapitału azjatyckiego | W5 |
| A-16 | G | BTC Regional Premiums | Premia giełdowa: Korea/Japonia/Chiny/USD → geograficzny sentyment | W5 |

---

## 🤖 NEURONY AI/ML — Nowa dywizja (Faza 2+)

> Te neurony wymagają modeli ML — wdrożenie w Fazie 2, teraz skatalogowane.
> Źródło: baza wskaźników v1.6, badania arXiv/Springer 2025-2026.

| Klucz | Neuron | Model/Metoda | Zadanie | Waga |
|-------|--------|--------------|---------|------|
| ML-01 | CNN-LSTM | Hybrid CNN-LSTM (Springer 2026) | Prognoza kierunku ceny, ~45% ROI na M1, wdrożony przez CCXT | W7 |
| ML-02 | TFT | Temporal Fusion Transformer | Multi-asset (BTC+ETH+BNB+DeFi) z on-chain + RSI/MACD/SOPR | W7 |
| ML-03 | NNParam | Neural Net Parametric Labeling | 400+ kryptowalut, 6 lat historii BTC/ETH, generalizacja wzorców | W6 |
| ML-04 | AetherTri | AetherEdge Triaxial Consensus | Trend+Momentum+Volatility + Q-learning self-tuning na 4H/1D | W7 |
| ML-05 | SpecialK | Special K Enhanced (Pring) | Composite multi-cycle oscylator z kompresją k=0.5 dla krypto | W6 |
| ML-06 | FEVA | Fractal Entropy Volatility | Multifraktal + teoria informacji → ukryte wzorce zmienności | W5 |
| ML-07 | NonCausal | Crypto Non-Causality Suite | "Future-smoothed" struktury rynku → nieuniknione atraktory | W5 |

---

## 📊 AKTUALIZACJA PODSUMOWANIA (po rozszerzeniu)

| Legion | v1.0 | Po rozszerzeniu | Wzrost |
|--------|------|-----------------|--------|
| X (Scalp) | 18 | 24 | +6 |
| XII (Swing) | 22 | 32 | +10 |
| III (Invest) | 20 | 38 | +18 |
| VI (Leverage) | 14 | 19 | +5 |
| Wspólne/Anty-manip | 7 | 16 | +9 |
| AI/ML (nowa dywizja) | 0 | 7 | +7 |
| **RAZEM** | **81** | **136** | **+55** |

> **136 neuronów** skatalogowanych łącznie (nie licząc duplikatów z bazy v1.3).
> Każdy neuron przed wdrożeniem przechodzi przez Koloseum (Prawo VI).

---

---

# 🌊 WIELKA FALA — pełny skan bazy (sekcje 15–25)

> Przeskanowano CAŁĄ bazę wskaźników (6154 linii, wersje 1.0–3.0).
> Zgodnie z zasadą symbiozy wyłuskano TYLKO neurony sygnałowe (coś co obserwuje
> rynek i daje LONG/SHORT/NEUTRAL). Pominięto: hackathony, kanały Discord/Telegram,
> polskie/azjatyckie źródła edukacyjne, frameworki automatyzacji, platformy danych.

---

## 🤖 DYWIZJA AI/ML — Sztuczna Inteligencja (Faza 2+)

*Modele predykcyjne, sieci neuronowe, transformery, agenci LLM. Wymagają treningu — wdrożenie w Fazie 2.*

| Klucz | Neuron | Model/Metoda | Zadanie | Waga |
|-------|--------|--------------|---------|------|
| ML-08 | DeepAlpha-V11 | BiLSTM+Attention (72 cechy) | Sygnał kierunkowy, walk-forward, 84,6% accuracy | W7 |
| ML-09 | CryptoKOL-Quant | LLM destylacja 99 KOL → 87 czynników | Kompozytowy sygnał BULLISH/BEARISH z konsensusu | W6 |
| ML-10 | VibeTrader | Model dyfuzyjny + vision LLM | Generuje przyszłe świece, sygnał przez analizę pikseli | W5 |
| ML-11 | LARSA | RL + LLM regime-switching | Przełącza reżimy i decyduje z uzasadnieniem | W6 |
| ML-12 | AIMegatron | Kalman + k-NN + ML | Przekonanie bycze/niedźwiedzie | W6 |
| ML-13 | DecoKAN | DWT + KAN mixery | Dekompozycja sygnału, najniższe MSE BTC/ETH/XMR | W6 |
| ML-14 | MAPPO-SLSTM | Multi-agent DRL + LSTM | Wieloagentowa optymalizacja portfela | W6 |
| ML-15 | TFT-ACB | TFT+BiLSTM+XGBoost ensemble | Prognoza ceny zamknięcia BTC | W6 |
| ML-16 | Synthesizer | Transformer zmienności | Prognoza ekstremalnych skoków zmienności BTC | W6 |
| ML-17 | NN-ScalpV6 | Ensemble 3 sieci MTF | Sygnały scalpingowe na wielu interwałach | W6 |
| ML-18 | AIndicate | Random Forest | Buy/Sell/Hold z RSI/MACD/StochRSI/EMA/BB + pewność | W6 |
| ML-19 | GusProto | 17 cech + Adaptive SuperTrend + SMC | Sygnały trendu online | W6 |
| ML-20 | MultiLLM-RL | LLM feature extractor + PPO | Multi-asset, IC > 0,15 | W6 |
| ML-21 | ChaosForecast | ARIMA + teoria chaosu + ATR | Buy/Sell/Hold heurystyczny | W5 |
| ML-22 | TradeFM | Generatywny model fundamentowy | Trade-flow i mikrostruktura rynku | W6 |
| ML-23 | AutoQuant | Autonomiczna pętla LLM | Iteracyjna ewolucja strategii FreqTrade | W5 |

### 🔭 Inspiracje zewnętrzne — pełne opisy w `docs/REJESTR_INSPIRACJI.md`

> Projekty badawcze AI/ML z pełnymi nazwami, linkami i statusem weryfikacji (Zasada Pełnego Opisu).
> ✅ Zweryfikowane w ARSENAL_IMPERIUM.md (maj 2026, 3 zwiadowców) — patrz REJESTR_INSPIRACJI.md.

| Klucz | Pełna nazwa | Źródło | Rola |
|-------|-------------|--------|------|
| ML-24 | SHARP — Self-Evolving Rubric Policy | arxiv.org/abs/2605.06822 | Warstwa audytu nad Cesarzem (W-009) ✅ ARSENAL_IMPERIUM.md |
| ML-25 | AgenticAITA — Multi-Agent Reasoning | arxiv.org/abs/2605.12532 | Wzorzec Senatu (debata 4 ról) ✅ ARSENAL_IMPERIUM.md |
| ML-26 | CogAlpha — Cognitive Alpha Factory | arxiv.org/abs/2511.18850 | Auto-generowanie neuronów (W-024) ✅ ARSENAL_IMPERIUM.md |
| ML-27 | NEXUS — Self-Evolving Market AI | github.com/The-R4V3N/Nexus | Wzorzec autonomii Faza 4 ✅ ARSENAL_IMPERIUM.md |

---

## 🛡️ DYWIZJA STRAŻY — Anty-manipulacja rozszerzona

*Wykrywanie oszustw rynku — rozszerzenie neuronów A-01..A-07. Obrona, nie atak.*

| Klucz | Neuron | Metoda | Zadanie | Waga |
|-------|--------|--------|---------|------|
| A-17 | MicrostrMCP | BOCPD bayesowski | Wykrywa spoofing, layering, wash trading | W8 |
| A-18 | VPIN-Flow | PIN/VPIN/Kyle's λ | Detekcja informed-flow (Foresight Flow) | W7 |
| A-19 | IcebergPred | XGBoost | Przewiduje ukryte zlecenia iceberg | W6 |
| A-20 | PumpDumpML | 2-stopniowy ML | Wykrywa pump&dump (volume spike + burst + buy wall) | W8 |
| A-21 | WashGraph | Analiza grafów + SCC | Wykrywa wash trading w sieci traderów | W7 |
| A-22 | ShieldRegime | Kinematyka ceny | Pump&dump + wash trade index | W7 |
| A-23 | Autoencoder | Autoencoder + IsolationForest | Anomalie cenowe BTC/USDT | W6 |
| A-24 | TEMG-TTA | Temporal Motif Graph | Anomalie OOD w transakcjach blockchain | W6 |
| A-25 | CrypticCadence | Detekcja anomalii wolumenu | Skoki/spadki = manipulacja lub flash krach | W7 |
| A-26 | Benford | Prawo Benforda | Rozkład pierwszej cyfry → manipulacja | W6 |
| A-27 | AMMA | Autonomiczny agent mikrostruktury | Spoofing + dystrybucja inst. co 0,5s | W7 |
| A-28 | InsiderTrack | DBSCAN klastrowanie | Insider trading (świeże portfele) | W6 |
| A-29 | FraudGNN | Spatio-temporal GNN | Schematy pump&dump | W6 |
| A-30 | PumpSense | ML Telegram P&D | Pump&dump w czasie rzeczywistym | W6 |

---

## 📊 DYWIZJA SZEROKOŚCI — Market Breadth

*Mierzy uczestnictwo całego rynku, nie pojedynczego aktywa. Głównie Invest/Makro.*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| B-01 | Breadth-SRG | Crypto Breadth (Scimitar) | Rosnące vs spadające monety = siła wewnętrzna | W7 |
| B-02 | Breadth-Astral | Triple Mode (16 aktywów) | 3 metryki strukturalne uczestnictwa | W7 |
| B-03 | Breadth-Peach | Crypto Breadth (Peachain) | Rotacja BTC↔alty, alt season vs dominacja BTC | W7 |
| B-04 | AD-Ratio | Advance-Decline Ratio | Nowe maks vs min: >3:1 silny, <1:2 ostrożność | W6 |
| B-05 | MemeSeason | Meme Season Score | 6 czynników cyklu memecoinów → rotacja | W5 |
| B-06 | MultiPCA | Multi-Crypto PCA | Aktywa zachowujące się inaczej niż rynek (dywergencje) | W6 |
| B-07 | SectorRot | Sector Rotation (7 narracji) | Relative strength 7 sektorów krypto 0-100 | W7 |

---

## 📖 DYWIZJA KSIĘGI — Order Book Depth

*Głębokość i przepływ księgi zleceń. Głównie Scalp.*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| OB-01 | Multibook | Bitcoin Multibook (Apollo) | Agreguje głębokość z wielu giełd real-time | W7 |
| OB-02 | OBImbalance | Order Book Imbalance (OBI) | Pressure ratio z tick-level → sygnał na ekstremach | W8 |
| OB-03 | LiqSweepAI | Crypto Liquidity AI Bot | Luki, ukryte ściany, sweepy w czasie rzeczywistym | W7 |
| OB-04 | SynthOB | Synthetic OrderBook | Syntetyczna księga z akcji cenowej i wolumenu | W6 |
| OB-05 | L2Viz | Level 2 Visualization | Pełna głębokość L2 podaży/popytu | W6 |
| OB-06 | HorusFlow | Horus Flow (orderbook physics) | L2 physics, tick imbalances, 5-sek delty wielorybów | W7 |
| OB-07 | ImbalanceHM | Imbalance Heatmap (pc75) | Luki w przepływie zleceń jako heatmapa | W6 |
| OB-08 | HawkesLOB | Multivariate Hawkes + LOB | Krótkoterminowe ruchy BTC z procesów Hawkesa | W6 |

---

## 💱 DYWIZJA ABORDAŻU — Arbitraż (Faza 3 — Ekspansja)

*Arbitraż między giełdami i rynkami. Wdrożenie w Fazie 3 (multi-exchange).*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| ARB-01 | BasisAnnual | Cryptoarbitrage Annualized Basis | Zannualizowany basis futures vs spot | W7 |
| ARB-02 | MultiExch | Multi-Exchange Arbitrage Suite | Okazje arbitrażowe między giełdami | W7 |
| ARB-03 | StatArb | Cross-sectional Statistical Arbitrage | Sygnały + walk-forward + portfel | W6 |
| ARB-04 | SpreadPine | Pine Script Arbitrage | Spready 0,3-1,5% między BTC/ETH/USDT | W6 |
| ARB-05 | MEVbot | MEV Arbitrage (Rust+Solidity) | Arbitraż MEV na łańcuchach EVM | W6 |
| ARB-06 | FlashLoan | AI FlashLoan+MEV | Skanuje mempool pod arbitraż DeFi | W5 |
| ARB-07 | FundingArb | Funding Arbitrage Index (1Token) | Ocena funding arbitrage + long-short | W6 |
| ARB-08 | Kimchi-X | Cross-market (Polymarket-Kalshi) | Spready arbitrażowe rynków predykcyjnych | W5 |

---

## 🔄 DYWIZJA WIESZCZÓW — Detekcja Reżimu i Makro

*Wykrywanie stanu rynku, korelacje międzyrynkowe, makropłynność.*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| K-01 | MarkovRegime | Markov Hedge Fund Method | Macierz Bull/Bear/Sideways → bull_prob−bear_prob | W7 |
| K-02 | AdaptRegime | Adaptive Regime Detector 4-State | 4 reżimy bez sztywnych progów (Trend×Vol) | W7 |
| K-03 | Switchtrade | Regime-Aware Trend Flip | Adaptuje reguły flipu wg reżimu | W6 |
| K-04 | AsiaUS | Asia Sell / US Buy Flip | Spread Edge = US − Asia, flip przy zerze | W6 |
| K-05 | TimeXer-M2 | Expert System + M2 | Prognoza BTC z globalną płynnością M2 | W7 |
| K-06 | CBank-Hedge | BTC vs Central Banking (LSTM+SHAP) | Reakcja BTC na jastrzębią/gołębią politykę | W6 |
| K-07 | CryptoCompass | Crypto Compass (QuantEdgeB) | Reżim z momentum/sentymentu top 30 tokenów | W7 |
| K-08 | MacroContext | Macro Context v1 | Korelacje instytucjonalne TradFi↔krypto | W7 |
| K-09 | TripleCorr | Triple Correlation Signal | Korelacja aktywa z 3 konfigurowalnymi | W6 |
| K-10 | TradFiCorr | TradFi Correlation Engine | Złoto/SPX/EUR → wczesny sygnał perp krypto | W7 |
| K-11 | ETFFlow | US ETF Flow Monitor | Napływy/odpływy spot BTC/ETH ETF | W8 |
| K-12 | MMakerCorr | Wintermute/Jane Street Index | Pozycjonowanie największych market makerów | W6 |
| K-13 | CDM-Dom | Comparative Dominance v2.6 | 5 serii dominacji → 6 faz rynkowych | W7 |
| K-14 | Halving-Log | BitcoinPricePrediction (halving) | Cykle halvingu logarytmami | W7 |
| K-15 | BEAM | BTC BEAM Adaptive Multiple | 1400-dniowa SMA jako podłoga cyklu | W7 |
| K-16 | MikeCycle | Mike's Cycle Top/Bottom | 2 z 3 (MVRV-Z, Pi Cycle, Puell) jednocześnie | W8 |
| K-17 | Wyckoff-ADCI | ADCI Wyckoff (rozszerzony) | Faza akumulacja/trend/dystrybucja | W7 |

---

## 😱 DYWIZJA WYROCZNI — Sentyment rozszerzony

*Sentyment z social media, opcji, on-chain. Filtr przed Senatem.*

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| R-01 | SentTracker | Crypto Sentiment Tracker Pro | Reddit/X/TikTok → BUY/SELL/NEUTRAL | W6 |
| R-02 | PulseReddit | PulseReddit Multi-Agent | Dyskusje Reddit vs ceny (+50% w hossie) | W6 |
| R-03 | Santiment | Santiment Social (Greed/Fear) | Extra Greed→korekta, Extra Fear→wzrost (kontra) | W6 |
| R-04 | Polymarket | Polymarket Crypto Assistant | 11 wskaźników Binance flow + Polymarket | W6 |
| R-05 | SkewIndex | Glassnode Skew Index | Asymetria UpVol−DownVol uśmiechu zmienności | W6 |
| R-06 | VRP | Volatility Risk Premium | IV vs RV → opcje drogie czy tanie | W6 |
| R-07 | OISenti-Z | CJ OI Sentiment Z-Score | Z-Score OI → ekstremalny Greed/Fear lewarowania | W7 |
| R-08 | MarketSent | Market-Derived Sentiment | Tweety etykietowane trendami ceny | W5 |
| R-09 | WhaleSent | MasterQuant Sentiment Engine | Aktywność wielorybów → zmiany sentymentu | W6 |

---

## 🐋 DYWIZJA WIELORYBÓW — On-chain rozszerzony

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| O-01 | WhaleML | On-chain Whales ML (78%) | Monitoruje adresy → predykcja BTC + ostrzeżenia | W7 |
| O-02 | HiddenWhale | Hidden Whale Flow (IBIT) | Ukryta akumulacja: spot BTC vs ETF IBIT | W7 |
| O-03 | AegisWhale | Aegis Whale Tracker | Fazy akumulacji/dystrybucji wielorybów | W6 |
| O-04 | WhaleZones | Whale Zones Detector | Strefy aktywności wielorybów | W6 |
| O-05 | ActiveAddr | Active Addresses + Volume | Zdrowie sieci (CryptoQuant) | W6 |

---

## 🌀 DYWIZJA ENTROPII — Modele matematyczne i mikrostruktura

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| E-01 | NCS | Crypto Non-Causality Suite | Strukturalne atraktory zamiast opóźnionych średnich | W5 |
| E-02 | FEVA | Fractal Entropy Volatility | Multifraktal → ukryte wzorce zmienności | W5 |
| E-03 | GARCH | GARCH+Cointegration | Prognoza zmienności BTC/ETH (ARIMA/GARCH/VECM) | W6 |
| E-04 | EGARCH | EGARCH Framework | Wejścia z naruszeń wariancji prognozowanej | W6 |
| E-05 | ProjectY | Market Equilibrium Deviation | Transformer/LSTM anomalie mikrostruktury LOB | W6 |
| E-06 | ExecAlpha | Execution Alphas | Prognoza wolumenu/zmienności/spreadów (slippage) | W6 |
| E-07 | RiskKelly | Vol regime + Kelly | Reżim zmienności ETH → wielkość pozycji Kelly | W7 |

---

## 🧱 DYWIZJA STRUKTURY — SMC/ICT rozszerzony

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| S-01 | EscoTheory | Complex Esco Theory | Diagonalne szyny, konfluencje, kompresja, płynność | W7 |
| S-02 | SmartPrinter | Smart Money Printer | Konfluencja BoS/CHoCH/ROI/Fibo/EMA/flow | W7 |
| S-03 | NexusMS | Nexus Market Structure | Fraktalna identyfikacja BoS/CHoCH | W6 |
| S-04 | FVGScorer | Data-Backed FVG Quality | Rankinguje FVG wg historycznej skuteczności | W7 |
| S-05 | QuarterSeq | Quarter Sequence Chains (Daye) | 7 poziomów cyklu → fazy Q1-Q4 | W6 |
| S-06 | BlockCandles | Block of Candles (BoC) | Grupuje świece w bloki supply/demand | W6 |
| S-07 | OBProxies | Order Blocks + Flow Proxies | OB/FVG wg SMC/ICT | W6 |
| S-08 | Model2026 | 2026 Model (HedgeFi) | Struktura rynku + sesje (NY AM) | W6 |

---

## 💎 DYWIZJA PERŁ — Pojedyncze wyspecjalizowane neurony

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| P-01 | AdaptRSI | AetherEdge Adaptive Smart RSI | RSI uczy realnych poziomów OB/OS per instrument | W7 |
| P-02 | ArtemisRSI | Artemis Adaptive RSI | Samostrojący RSI + klasyfikator reżimu + AI dywergencja | W7 |
| P-03 | BTCipher | The Bitcoin Cipher (WaveTrend) | Statystycznie istotne przejścia momentum OB/OS | W6 |
| P-04 | NakedPOC | Naked POC (Peak Tolerance) | Świece 85% szczytu wolumenu → flow instytucjonalny | W6 |
| P-05 | LowVolExtr | BTC Low Volume Extremum | Szczyty/dna przy niskim wolumenie + długi knot | W6 |
| P-06 | COIL | COIL (staircase) | Cicha akumulacja przed dużym ruchem (5 warunków) | W6 |
| P-07 | EvilMACD | Evil MACD System | MACD + filtr trendu multi-TF | W5 |
| P-08 | QuantEngine | QuantEngine AI | 6 wskaźników + scoring AI −100..+100 | W6 |
| P-09 | FTTBBma | FTT Plus BBMA | Bollinger + 3-świecowy momentum → odwrócenie | W5 |
| P-10 | MARS | Metrika Asset Risk Score | Prawdopodobieństwo zdarzeń katastroficznych aktywa | W6 |

---

## 📊 WIELKIE PODSUMOWANIE (po pełnym skanie)

| Dywizja / Legion | Neurony |
|------------------|---------|
| ⚡ Legio X Equestris (Scalp) | 24 |
| ⚖️ Legio XII Fulminata (Swing) | 32 |
| 🏰 Legio III Augusta (Invest) | 38 |
| 🔥 Legio VI Ferrata (Leverage) | 19 |
| ⚖️ Wspólne anty-manip + makro | 16 |
| 🤖 Dywizja AI/ML | 23 |
| 🛡️ Dywizja Straży (anty-manip) | 30 |
| 📊 Dywizja Szerokości (breadth) | 7 |
| 📖 Dywizja Księgi (order book) | 8 |
| 💱 Dywizja Abordażu (arbitraż) | 8 |
| 🔄 Dywizja Wieszczów (reżim/makro) | 17 |
| 😱 Dywizja Wyroczni (sentyment) | 9 |
| 🐋 Dywizja Wielorybów (on-chain) | 5 |
| 🌀 Dywizja Entropii (matematyka) | 7 |
| 🧱 Dywizja Struktury (SMC/ICT) | 8 |
| 💎 Dywizja Perł (wyspecjalizowane) | 10 |
| **RAZEM (szacunek skanu I-IV)** | **261** |

> **299 neuronów skatalogowanych** (zweryfikowane policzeniem unikalnych kluczy; wcześniejsze szacunki 261/328 były nieuzgodnione). 28 zaimplementowanych w kodzie.
> Cała baza wskaźników przeskanowana (sekcje 1.0–3.0). Zero luk.
> Każdy neuron przed bojem przechodzi przez Koloseum (Prawo VI).

---

## 🆕 SKAN RYNKU 2026 + MISTRZOWIE ŚWIATA — Nowe Neurony (+13)

> Źródło: Przegląd wskaźników krypto 2026 + strategie legendarnych traderów.
> Katalog rośnie — rój nigdy nie jest kompletny.

### ⚡ Rozszerzenie Dywizji Order Book — Market Profile

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| MP-01 | Neuron TPO POC | TPO Market Profile — Point of Control | Poziom gdzie rynek spędził najwięcej CZASU = silny S/R | W8 |
| MP-02 | Neuron VRVP | Visible Range Volume Profile (VAH/VAL/POC) | Poziomy gdzie rynek spędził najwięcej WOLUMENU | W8 |
| MP-03 | Neuron Super POC | TPO POC = Volume POC (zbieżność) | "Supermagnes" — TPO i wolumen zgadzają się → ekstremalnie silny S/R | W9 |

### 📊 Rozszerzenie Legio X (Scalp)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| CVD-D | Neuron CVD-Dywergencja | Cumulative Volume Delta Divergence | Cena robi nowe high, CVD nie → ukryte osłabienie, sygnał odwrócenia | W9 |
| WR-14 | Neuron Williams%R | Williams %R(14) | %R < -80 = wyprzedanie (LONG), %R > -20 = wykupienie (SHORT) | W6 |

### 🧱 Rozszerzenie Dywizji SMC/ICT — Price Action

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| PA-PINBAR | Neuron PinBar | Pin Bar Detektor (ogon ≥ 2/3 świecy) | Sygnał odwrócenia przy kluczowych poziomach (Nial Fuller) | W6 |
| PA-INSIDE | Neuron InsideBar | Inside Bar Detektor (świeca wewnątrz matki) | Kompresja przed wybiciem → kontynuacja trendu | W6 |
| PA-FAKEY | Neuron Fakey | Fałszywe wybicie z Inside Bar | Fake breakout + powrót = pułapka dla słabych graczy | W7 |

### 🏛️ Rozszerzenie Legio III Augusta (On-Chain)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| MVRV-Z | Neuron MVRV-ZScore | MVRV Z-Score (sigma-znormalizowany) | > 7 = szczyt cyklu, < -0.5 = dno. Precyzyjniejszy niż III-01 | W9 |
| NVT-S | Neuron NVT-Signal | NVT Signal z wstęgami odchylenia std | Bitcoin sieć "za drogo" (wysokie NVT = overbought) | W8 |
| RHODL | Neuron RHODL | Realized HODL Waves — long-term holder spending | LTH zaczynają sprzedawać → sygnał zbliżającego się szczytu | W9 |

### 🌍 Rozszerzenie Dywizji Makro/Geo

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| MAK-COT | Neuron COT-Extreme | Commitment of Traders — Commercial vs Speculator spread | Commercials rekordowo przeciwni → odwrócenie (Larry Williams metoda) | W8 |

### ⚖️ Rozszerzenie Legio XII (Swing)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| XII-MOM | Neuron MomScore | Momentum Score = Slope(90D) × R² | Volatility-adjusted momentum ranking (Clenow) — rankinuje aktywa | W7 |

---

## 🆕 SKAN III — Klasyka, ICT, Sentyment, Fale, Stat-Arb (+13)

> Źródło: WebSearch czerwiec 2026 — Brandt, ICT (Huddleston), Elliott/Wolfe, pairs trading, boty.

### 🧱 Rozszerzenie Dywizji Struktury (SMC/ICT/Price Action)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| PAT-01 | Neuron ChartPattern | Klasyczne formacje (H&S, triangle, double top/bottom) | Detekcja formacji Edwards&Magee (Peter Brandt) + measured move | W7 |
| ICT-FVG | Neuron FairValueGap | Fair Value Gap (3-świecowa luka imbalance) | Strefa nierównowagi ceny = magnes powrotu (ICT) | W7 |
| ICT-DISP | Neuron Displacement | Displacement (agresywny ruch impulsowy) | Potwierdza intencję smart money, tworzy FVG | W7 |
| EW-01 | Neuron ElliottWave | Elliott Wave Counter (5-3 struktura) | Auto-liczenie fal impulsowych i korekcyjnych | W6 |
| WW-01 | Neuron WolfeWave | Wolfe Wave (5-falowy wzorzec równowagi) | Wykrywa punkt odwrócenia w kanale falowym | W6 |

### ⏰ Nowa pod-dywizja: Czas/Sesje

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| SES-01 | Neuron KillZone | Session/Killzone Timer (Azja/Londyn/NY) | Aktywność instytucji max w kill zones (NY 8-11 EST) | W6 |
| SES-02 | Neuron AzjaRange | Asia Range High/Low (00:00–08:00 UTC) | Wyznacza zakres sesji azjatyckiej — breakout w Londynie = silny sygnał | W8 |
| SES-03 | Neuron CMEGap | CME Gap Detector (BTC/ETH futures) | Sunday open vs Friday close > 0.5% → 77% fill rate → kontrariański sygnał w kierunku luki | W8 |

### 😱 Rozszerzenie Dywizji Wyroczni (sentyment)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| SENT-FG | Neuron FearGreed | Crypto Fear & Greed Index (0-100) | < 20 = kupuj strach, > 80 = sprzedawaj chciwość (kontrariański) | W7 |
| SENT-SOC | Neuron SocialVolume | Social Media Volume/Hype | Ekstremalny hype = szczyt lokalny (kontrariański) | W6 |

### 🔀 Rozszerzenie Dywizji Arbitrażu (Faza 3)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| PAIR-01 | Neuron PairZScore | Z-Score spreadu pary (BTC/ETH) | Z > +2 = short/long para, oczekuj powrotu do średniej | W8 |
| PAIR-02 | Neuron Cointegration | Test kointegracji ADF/Johansen | Potwierdza czy para nadaje się do pairs tradingu | W7 |

### 📖 Rozszerzenie Dywizji Order Book / Leverage

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| BASIS-01 | Neuron Basis | Spot-Perp Basis (cash & carry) | Dodatni basis + funding = okazja delta-neutral | W7 |
| CORR-01 | Neuron Correlation | Korelacja krocząca aktywów | Rozpad korelacji = okazja pairs / dywersyfikacja | W6 |

---

## 🔭 SKAN IV — VSA, Intermarket, Opcje, DeFi, Sektory (2026-06-01)

> Nowe neurony z prac badawczych: VSA, Volume Profile, VPIN, GEX, Skew, Pairs/Momentum cross-sectional, DeFi TVL, Howard Marks cykl, DXY, L1/L2 RS, Bid-Ask Spread. Łącznie +16 neuronów.

### 📈 Rozszerzenie Dywizji Struktury (VSA)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| VSA-01 | Neuron NoSupply | VSA No Supply (wąski spread + niski vol + zamknięcie w górnej połowie na spadku) | Sprzedający wyczerpani → sygnał LONG | W8 |
| VSA-02 | Neuron NoDemand | VSA No Demand (rosnąca cena + spadający vol) | Słaby ruch wzrostowy → sygnał SHORT | W7 |
| VSA-03 | Neuron Upthrust | VSA Upthrust (wybicie nad opór + zamknięcie w dolnej 1/3 + wysoki vol) | Fałszywy breakout, pułapka na kupujących → SHORT | W8 |
| VSA-04 | Neuron StoppingVol | VSA Stopping Volume (kulminacyjny vol + świeca odwrotu) | Kapitulacja, wyczerpanie trendu → kontrariańskie wejście | W9 |
| VP-01 | Neuron VPOC | Volume Point of Control (cena z największym vol w sesji) | VPOC jako magnes / pivot → filtr wejść | W7 |
| VP-02 | Neuron ValueArea | Value Area High/Low (70% vol) | VAH = opór dynamiczny, VAL = wsparcie dynamiczne | W7 |

### 🔬 Rozszerzenie Dywizji Order Book (mikrostruktura)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| VPIN-01 | Neuron VPIN | Volume-Synchronized Probability of Informed Trading | VPIN > 0.75 = ryzyko flash-crash / gwałtownego ruchu | W9 |
| SPREAD-01 | Neuron BidAskSpread | Bid-Ask Spread jako % ceny mid, znormalizowany | Spread > +2σ = unikaj scalpu; spread < -2σ = dobra płynność | W6 |

### 📉 Rozszerzenie Dywizji Opcji (nowa gałąź)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| GEX-01 | Neuron GammaFlip | GEX Gamma Exposure — poziom zmiany znaku dealerów (Positive → Negative) | Poniżej GEX flip = tryb amplifikacji, powyżej = tłumienie vol | W9 |
| SKEW-01 | Neuron VolSkew | 25-Delta Risk Reversal (IV Put 25Δ / IV Call 25Δ, znorm. z-score 30d) | Skew > +2σ = drogie puty → sprzedaj strach; < -2σ = drogie calle → sprzedaj euforie | W8 |
| PCR-01 | Neuron PutCall | Put/Call Ratio (vol + OI), znorm. z-score 20d | PCR < 0.5 = komplacencja → SHORT sygnał kontrariański; PCR > 1.5 = panika → LONG | W7 |

### 🌐 Rozszerzenie Dywizji Wieszczów (makro/intermarket)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| DXY-01 | Neuron DXYCorr | Korelacja krocząca 30d BTC vs DXY (Pearson r) | r < -0.6 + DXY rośnie = presja na BTC; r flip = zmiana reżimu | W7 |
| HM-01 | Neuron MarksCykl | Howard Marks Dumb Money Score (kompozyt: PCR + retail flows + media sentym.) | Score > +2σ = szczyt euforii → SHORT; < -2σ = dno paniki → LONG | W8 |

### 🌱 Rozszerzenie Dywizji DeFi (On-chain, nowa gałąź)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| TVL-01 | Neuron TVLVelocity | TVL Velocity = (TVL_t - TVL_t-30) / TVL_t-30 | > +10%/tydzień = napływ kapitału → LONG token; flips ujemny = NEUTRAL/SHORT | W7 |

### 🌀 Rozszerzenie Dywizji Entropii (fraktal)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| ENT-08 | Neuron Higuchi | Higuchi Fractal Dimension (HFD, D = 1.0–2.0) | D ≈ 1.0 = rynek trendujący (TREND), D ≈ 2.0 = rynek chaotyczny/ranging. Szybsza detekcja reżimu niż ADX/Choppiness. Wyniki HFT QUARTET: Sharpe > 2.5, WR 70-80%. | W9 |

### 🔄 Rozszerzenie Dywizji Arbitrażu (sektor/narracja)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| RS-01 | Neuron L1L2RS | Relative Strength: L1 vs L2 (ratio SMA20) | L1 > L2 trend = rotacja do L1; L2 > L1 = rotacja L2 | W6 |
| XCS-01 | Neuron CrossMom | Cross-sectional Momentum 12-1m (ranking 6m returns krypto) | TOP 30% koszyków = LONG; BOTTOM 30% = SHORT; crash = exit | W7 |

---

## 🧠 SKAN VI — Psychologia Rynku + Odtwarzalne Wskaźniki Zamknięte (2026-06-01)

> Źródło: behavioral finance research + reverse-engineering znanych zamkniętych wskaźników.
> Pieczęć: ⚔️ IMV-INS (zainspirowane) lub 🔱 IMV-ADO (ulepszone).

### 😱 Rozszerzenie Dywizji Wyroczni (psychologia / behawioryzm)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| PSY-01 | Neuron FOMO | FOMO Score = funding >0.1% + vol >2× avg + social spike >300%/7d | 5-składnikowy ensemble (87% accuracy histor.) → LONG crowded → SHORT kontrariański | W8 |
| PSY-02 | Neuron Kapitulacja | Capitulation Detector: vol >2× avg + wide candle + close w dolnej 1/4 + recovery next bar | Panikowe dno → kontrariański LONG | W9 |
| PSY-03 | Neuron LossAversion | Liquidation Cascade: >$50M likwidacji w 1h + overshooting 1-3% | Po kaskadzie → scalp kontrariański (revert) | W8 |
| PSY-04 | Neuron Stado | Herding Signal: >70% retail LONG (Coinglass/CryptoQuant) | Tłum po jednej stronie → SHORT kontrariański (+50% siły w rynku niedźwiedzia) | W7 |
| PSY-05 | Neuron Anchor | Round Number Anchor: cena ±0.3% od okrągłej liczby ($100k/$50k/$10k) | Strefa oporu/wsparcia — nie wchodzić w środku, czekać na potwierdzenie | W6 |
| PSY-06 | Neuron Sezon | Seasonal Pattern: Grudzień hist. 6/8 lat pozytywny, Styczeń mieszany | Słaby sygnał — tylko jako filtr makro, nie samodzielny | W3 |

### 🔱 Nowa Dywizja: Odtwarzalne Wskaźniki (IMV-ADO/INS)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| WA-01 | Neuron WaddahAttar | Waddah Attar Explosion: Trend=(MACD_curr-MACD_prev)×sens; Explosion=BB_upper-BB_lower | Trend > Explosion = silny kierunek (kup/sprzedaj); Dead Zone = brak sygnału | W8 |
| MC-01 | Neuron MarketCipher | Market Cipher B core: WaveTrend (WT1/WT2) + MFI + RSI + StochRSI + VWAP momentum | Zielona kropka gdy wszystkie 5 zbieżne w oversold = silny LONG | W8 |
| NN-01 | Neuron NNFX | NNFX Baseline: MA(200) + 2 potwierdzenia (RSI + MACD) + Vol (ATR) + Exit (PSAR) | Kupuj gdy Baseline + oba potwierdzenia + vol ALIGNED; wychodzi na Exit | W7 |

---

## 🌏 SKAN VII — Perełki z Azji (3100 linków, 2026-06-01)

> Źródło: `archiwum/Azjatycki_skan_rynku_3100_links.md` — pełny skan 7106 linii.
> Szczegóły i pieczęcie: `docs/SKAN_AZJA.md`. Tu tylko genuine nowości (symbioza — bez duplikatów).

### 🌀 Rozszerzenie Dywizji Entropii (matematyka reżimu)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| HX-01 | Neuron Hurst | Dynamic Hurst Exponent (H, 0–1) | H>0.5 = trend (pamięć dodatnia), H<0.5 = mean-revert, H≈0.5 = random walk. Uzupełnia Higuchi | W8 |
| ZS-01 | Neuron AdaptZScore | Adaptive Z-Score (próg samokalibrujący do zmienności) | Wejście gdy Z przekroczy adaptacyjny próg (nie sztywne ±2σ) | W7 |

### 🧱 Rozszerzenie Dywizji Struktury (liquidity / order flow)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| LG-01 | Neuron LiquidityGrab | Liquidity Grab / Stop-Hunt Detector | Cena przebija equal H/L → zbiera stopy → odwrót. Sygnał reversal | W8 |
| AD-01 | Neuron Absorption | Absorption-Distribution Index | Wielki gracz "połyka" podaż przy stałej cenie → wyczerpanie ruchu | W7 |

### 📈 Rozszerzenie Trendu/Zmienności (adaptacyjne — IMV-ADO)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| ST-01 | Neuron AdaptSuperTrend | Adaptive SuperTrend (ATR adaptacyjny) | Trend follow z dostrojeniem do zmienności | W7 |
| KAL-01 | Neuron KalmanATR | Kalman-Adaptive ATR | Filtr Kalmana wygładza ATR → mniej fałszywych stopów (ulepszenie X-06) | W7 |

### 🔀 Rozszerzenie Arbitrażu/Makro (cross-venue)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| KP-01 | Neuron KimchiPremium | Kimchi/P2P Premium (Korea/global + P2P spread) | Miernik stresu rynkowego + kierunkowy sentyment (premia rośnie w panice) | W7 |
| CV-01 | Neuron VenueDivergence | Cross-Venue Volume Divergence | Różnica udziału wolumenu giełda regionalna vs globalna = leading indicator | W6 |

### 🐋 Rozszerzenie Wielorybów (on-chain górnicy)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| HR-01 | Neuron Hashrate | Hashrate Divergence | Zmiany hashrate/poboru mocy górników jako wyprzedzający sygnał ceny | W6 |

### 🛡️ Rozszerzenie Straży (anty-manipulacja)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| IB-01 | Neuron Iceberg | Iceberg/Hidden Order Detection | Wykrywa ukryte zlecenia po wzorcu odnawiania głębokości order book | W7 |

### 📉 Rozszerzenie Opcji/Czasu (vol regime)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| IV-01 | Neuron APACVol | APAC Implied Vol Regime | Implied vol systematycznie spada w sesji azjatyckiej — neuron czasowo-zmiennościowy | W6 |

### 😱 Rozszerzenie Wyroczni (sentyment azjatycki)

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| JP-01 | Neuron JpRetail | Japanese Retail Contrarian Index | Zachowania japońskich detalistów jako wskaźnik kontrariański | W6 |
| CAL-01 | Neuron AsiaCalendar | Asian Calendar Seasonality (Lunar New Year) | Azjatyckie efekty kalendarzowe (uzupełnia PSY-06 Sezon) | W4 |

---

## 📊 TABELA PODSUMOWUJĄCA (zaktualizowana v3.0)

| Grupa / Dywizja | Liczba |
|-----------------|--------|
| Legio X Equestris (Scalp) | **26** |
| Legio XII Fulminata (Swing) | **33** |
| Legio III Augusta (Invest/On-Chain) | **41** |
| Legio VI Ferrata (Leverage) | 19 |
| Wspólne (multi-legion + adaptacyjne ST/Kalman) | 16 + 2 = **18** |
| 🤖 Dywizja AI/ML | 23 |
| 🛡️ Dywizja Straży (anty-manipulacja + Iceberg) | 30 + 1 = **31** |
| 📊 Dywizja Breadth (szerokość) | 7 |
| 📖 Dywizja Order Book | **14** |
| 🔀 Dywizja Arbitrażu (Faza 3 + Kimchi/Venue) | 12 + 2 = **14** |
| 🔄 Dywizja Wieszczów (reżim/makro) | **20** |
| 😱 Dywizja Wyroczni (sentyment + psych + Azja) | 17 + 2 = **19** |
| 🐋 Dywizja Wielorybów (on-chain + Hashrate) | 5 + 1 = **6** |
| 🌀 Dywizja Entropii (matematyka + fraktal + Hurst/Z) | 8 + 2 = **10** |
| 🧱 Dywizja Struktury (SMC/ICT/VSA + LiqGrab/Absorb) | 22 + 2 = **24** |
| ⏰ Dywizja Czasu/Sesji | **3** |
| 💎 Dywizja Perł (wyspecjalizowane) | 10 |
| 📉 Dywizja Opcji (+ APAC Vol) | 3 + 1 = **4** |
| 🌱 Dywizja DeFi | **1** |
| 🔱 Dywizja Odtworzonych (IMV-ADO/INS) | **3** |
| **RAZEM (szacunek po Skan VII; kanon zweryfikowany = 299)** | **328** |

> **299 neuronów skatalogowanych** (kanon — policzone). Skan VII Azja dorzucił m.in.: Hurst, AdaptZScore, LiquidityGrab, Absorption, AdaptSuperTrend, KalmanATR, KimchiPremium, VenueDivergence, Hashrate, Iceberg, APACVol, JpRetail, AsiaCalendar).
> Pełne pieczęcie i odrzucone duplikaty: `docs/SKAN_AZJA.md`.

---

## 🔍 UZUPEŁNIENIE ARSENAŁU — Wskaźniki odzyskane (stracone przy zmianie paradygmatu)

> Podczas przejścia z modelu "neuron jako czujnik" na "neuron z interpretuj()" część wskaźników
> z pierwotnego Arsenału (v1.0-1.3) nie trafiła do katalogu. Odzyskane 2026-06-02.
> Klucze rezerwowe — implementacja po dekorelacji (Prawo XVI).

### 📊 Momentum — uzupełnienie

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| MOM-DPO | Neuron DPO | Detrended Price Oscillator | Cykle cenowe bez trendu (usuwa trend ze średniej) | W4 |
| MOM-UO | Neuron UltOscil | Ultimate Oscillator (7/14/28) | Momentum z 3 interwałów — mniej fałszywych sygnałów | W5 |
| MOM-CMO | Neuron ChandeMom | Chande Momentum Oscillator | Kierunek i siła momentum (±100) | W5 |

### 📈 Trend — uzupełnienie

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| TR-ALIG | Neuron Alligator | Williams Alligator (3 SMMA: 5/8/13) | Uśpiony/aktywny/jedzący trend — klasyk Williamsa | W6 |
| TR-ALMA | Neuron ALMA | Adaptive LSMA (ALMA) | Szybki trend z minimalnym opóźnieniem i niskim szumem | W5 |
| TR-PCHAN | Neuron PriceChannel | Price Channel (Donchian variant) | Wybicia historycznych S/R (kanał cenowy) | W5 |

### 🌊 Zmienność — uzupełnienie

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| VOL-SEB | Neuron StdErrBands | Standard Error Bands | Jakość trendu — wąskie pasma = silny trend, szerokie = szum | W5 |
| VOL-CHVOL | Neuron ChaikinVol | Chaikin Volatility (EMA(H-L)) | Zmiany zmienności — spike = potencjalne odwrócenie | W5 |
| VOL-VFIX | Neuron VIXFix | VIX Fix krypto (min(close,14)/close) | Strach rynkowy krypto — spike = dno paniki (kontrariański) | W6 |
| VOL-ATRP | Neuron ATRP | ATR jako % ceny (ATRP) | Stop-loss jako procent ceny — lepsza normalizacja między instrumentami | W4 |

### 💰 Wolumen/Flow — uzupełnienie

| Klucz | Neuron | Wskaźnik | Zadanie | Waga |
|-------|--------|----------|---------|------|
| F-VOLOSCIL | Neuron VolOscil | Volume Oscillator (fast/slow EMA vol) | Zmiany aktywności wolumenowej — odchylenie od baseline | W5 |
| F-APEXCVD | Neuron ApexCVD | Apex Desk CVD MAX | Kto kontroluje rynek (ekstremalna presja kupna/sprzedaży) | W6 |

---

*VITRUVIUSZ — "Trzysta dwadzieścia osiem par oczu jednego organizmu. Imperium nie ma ślepego pola."*
