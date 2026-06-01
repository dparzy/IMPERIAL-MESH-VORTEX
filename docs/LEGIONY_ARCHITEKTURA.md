# ⚔️ LEGIONY — Cztery Armie Imperium

> **Zasada:** Każdy Legion = inny styl tradingu = inne interwały = inne wskaźniki.
> Żaden Legion nie duplikuje pracy drugiego. Razem pokrywają CAŁY rynek.
>
> **Mikro-neurony:** Każdy Legion to rój małych wyspecjalizowanych agentów.
> Jeden neuron = jeden wskaźnik. Wiele neuronów = jeden Legion = pełny obraz.

---

## 🏛️ CZTERY LEGIONY — nazwy i role

| Legion | Historyczny odpowiednik | Styl | Interwał | Priorytet |
|--------|------------------------|------|----------|-----------|
| **Legio X Equestris** (Dziesiąty Konny) | Najlepsza jazda Cezara | Scalp | M1–M15 | Szybkość |
| **Legio XII Fulminata** (Dwunasty Błyskawica) | Wschodni legion walki | Swing | 4H–1D | Równowaga |
| **Legio III Augusta** (Trzeci Augustowski) | Garnizon, stabilizacja | Invest/Spot | 1D–1W | Bezpieczeństwo |
| **Legio VI Ferrata** (Szósty Żelazny) | Żelazna pancerna | Leverage/Futures | Zmienne | Dźwignia |

---

## ⚡ LEGIO X EQUESTRIS — Konny (Scalp)

**Motto:** *"Szybki cios zanim wróg się obróci."*
**Interwał:** M1, M5, M15
**Kapitał:** mały, wiele trades/dzień

### Mikro-neurony (wyspecjalizowane agenty)

| ID | Neuron | Wskaźnik | Co obserwuje |
|----|--------|----------|--------------|
| X-01 | Neuron EMA | EMA(9/21) cross | Kierunek trendu na M5 |
| X-02 | Neuron StochRSI | Stochastic RSI | Szybkie sygnały w ekstremach |
| X-03 | Neuron CVD | Cumulative Volume Delta | Kto kontroluje rynek (kupujący/sprzedający) |
| X-04 | Neuron VWAP | VWAP Bounce | Magnes cenowy dnia |
| X-05 | Neuron OrderFlow | Bid/Ask Imbalance | Mikrostruktura — presja natychmiastowa |
| X-06 | Neuron ATR-Stop | ATR × 1.5 | Dynamiczny stop-loss |

**Filtr wejścia:** ADX > 20 (jest trend) + wolumen > średnia × 1.2

---

## ⚖️ LEGIO XII FULMINATA — Błyskawica (Swing)

**Motto:** *"Uderzamy rzadko, ale celnie."*
**Interwał:** 4H, 1D
**Kapitał:** średni, kilka trades/tydzień

### Mikro-neurony

| ID | Neuron | Wskaźnik | Co obserwuje |
|----|--------|----------|--------------|
| XII-01 | Neuron EMA | EMA(50/200) golden/death cross | Główny kierunek trendu |
| XII-02 | Neuron MACD | MACD histogram | Zmiany momentum |
| XII-03 | Neuron Bollinger | BB squeeze/breakout | Kompresja → wybicie |
| XII-04 | Neuron Supertrend | Supertrend + ADX | Kierunek + siła trendu |
| XII-05 | Neuron Fibo | Fibonacci S/R | Poziomy wsparcia/oporu |
| XII-06 | Neuron SMC | BOS/CHoCH, Order Blocks | Ślady smart money |
| XII-07 | Neuron RSI-Div | RSI + dywergencje | Ukryte sygnały odwrócenia |
| XII-08 | Neuron OBV | On-Balance Volume | Potwierdzenie wolumenem |

**Filtr wejścia:** EMA(200) jako tło + ATR-based stop-loss

---

## 🏰 LEGIO III AUGUSTA — Augustowski (Invest/Spot)

**Motto:** *"Garnizon trwa. Cierpliwość to broń."*
**Interwał:** 1D, 1W
**Kapitał:** duży, strategie tygodniowe/miesięczne

### Mikro-neurony

| ID | Neuron | Wskaźnik | Co obserwuje |
|----|--------|----------|--------------|
| III-01 | Neuron MVRV | MVRV Ratio | Globalny szczyt/dołek (>3.7 drogo) |
| III-02 | Neuron NUPL | NUPL | Faza cyklu (>0.75 euforia, <0 kapitulacja) |
| III-03 | Neuron PiCycle | Pi Cycle Top/Bottom | Szczyty cyklu halvingowego |
| III-04 | Neuron ExchangeFlow | Exchange Netflow | Presja sprzedażowa na giełdy |
| III-05 | Neuron SOPR | SOPR | Realizacja zysków/strat |
| III-06 | Neuron Halving | Halving Cycle | Pozycja w 4-letnim cyklu |
| III-07 | Neuron AltSeason | Altcoin Season Index | Rotacja BTC→alts |
| III-08 | Neuron M2 | Global M2 Liquidity | Makro (przesunięcie ~105 dni vs BTC) |

**Filtr wejścia:** Minimum 2 wskaźniki on-chain potwierdzają strefę akumulacji

---

## 🔥 LEGIO VI FERRATA — Żelazny (Leverage/Futures)

**Motto:** *"Żelazna dyscyplina albo śmierć. Dźwignia to miecz obosieczny."*
**Interwał:** 15M–4H (adaptacyjny)
**Kapitał:** MAŁE pozycje, wysoka dźwignia (5×–20×)
**⚠️ RYZYKO NAJWYŻSZE — Pretorianie mają WETO**

### Mikro-neurony

| ID | Neuron | Wskaźnik | Co obserwuje |
|----|--------|----------|--------------|
| VI-01 | Neuron FundingRate | Funding Rate | Przeważenie long/short (>0.03% = za dużo longów) |
| VI-02 | Neuron OI | Open Interest | Potwierdzenie siły trendu futures |
| VI-03 | Neuron LiqHeatmap | Liquidation Heatmap | Poziomy kaskadowych likwidacji |
| VI-04 | Neuron LongShort | Long/Short Ratio | Sentyment, ekstrema = odwrócenie |
| VI-05 | Neuron LevZScore | Leverage Z-Score | Ekstremalne lewarowanie rynku |
| VI-06 | Neuron MaxPain | Max Pain | Magnes cenowy opcji |

**Filtr wejścia (OBOWIĄZKOWY):**
- Funding Rate < 0.05% (brak ekstremalnego przeważenia)
- Pozycja ≤ 2% kapitału całkowitego
- Stop-loss ZAWSZE ustawiony przed wejściem
- Pretorianie MUSZĄ przepuścić (żadnego weto)

---

## 🧬 SCHEMAT SYGNAŁU — co każdy neuron produkuje

Każdy mikro-neuron zwraca ustandaryzowany obiekt:

```python
@dataclass
class SygnalNeuronu:
    neuron_id: str          # np. "X-02" (Legio X, neuron 2)
    legion: str             # "SCALP" / "SWING" / "INVEST" / "LEVERAGE"
    wskaznik: str           # np. "StochRSI"
    wartosc: float          # surowa wartość wskaźnika
    kierunek: str           # "LONG" / "SHORT" / "NEUTRAL"
    pewnosc: float          # 0.0–1.0
    pewnosc_przeciwnika: float  # jak mocne są argumenty AGAINST
    pewnosc_finalna: float  # po uwzględnieniu adversary
    powody: list[str]       # konkretne powody (np. ["RSI=67.3 > 60", "EMA cross UP"])
    timestamp: float        # czas generacji
    hash_danych: str        # SHA-256 z Bramy (dowód nienaruszalności)
```

**Przykład (Neuron X-02, StochRSI):**
```json
{
  "neuron_id": "X-02",
  "legion": "SCALP",
  "wskaznik": "StochRSI",
  "wartosc": 23.4,
  "kierunek": "LONG",
  "pewnosc": 0.75,
  "pewnosc_przeciwnika": 0.2,
  "pewnosc_finalna": 0.68,
  "powody": [
    "StochRSI=23.4 poniżej 20 (strefa wyprzedania)",
    "Momentum odwraca się w górę",
    "CVD potwierdza kupujący przejmują kontrolę"
  ],
  "timestamp": 1748823600.0,
  "hash_danych": "sha256:a3f9..."
}
```

> **Zasada Prawa I:** `wartosc` ZAWSZE pochodzi z Bramy Kalkulatora (TA-Lib).
> Neuron NIGDY nie liczy wskaźnika samodzielnie. Pyta Bramę → interpretuje wynik.

---

## 🔄 JAK LEGIONY WSPÓŁPRACUJĄ Z SENATEM

```
Legio X (Scalp)   ─┐
Legio XII (Swing) ─┤──→ SENAT zbiera sygnały wszystkich Legionów
Legio III (Invest)─┤     Frakcja BYKÓW filtruje tylko LONG-sygnały
Legio VI (Leverage)┘     Frakcja NIEDŹWIEDZI filtruje tylko SHORT-sygnały
                              ↓
                         RAPORT DEBATY
                              ↓
                          CESARZ decyduje
                         (LONG/SHORT/CZEKAJ + %)
```

**Ważne:** Senat dostaje sygnały ze WSZYSTKICH Legionów jednocześnie.
Cesarz nie musi wiedzieć z którego Legionu pochodzi sygnał — widzi tylko argumenty.

---

## ⚔️ PRETORIANIE — WETO dla Legio VI

Przed każdą decyzją Cesarza dotyczącą Legio VI (Leverage):

```
Aegis Tarcza sprawdza:
  1. ATR > 2× norma? → CZEKAJ (za duże wahania)
  2. Seria 3+ strat z rzędu? → PAUZA 24h
  3. Drawdown > 10%? → STOP TRADING
  4. Funding Rate > 0.05%? → VETO dla LONG
  5. Funding Rate < -0.03%? → VETO dla SHORT
```

Jeśli choć jeden warunek spełniony → **pozycja lewarowana NIE WCHODZI**, nawet gdy Cesarz mówi LONG.

---

*VITRUVIUSZ — "Cztery legiony patrzą w cztery strony. Razem nie ma ślepego pola."*
