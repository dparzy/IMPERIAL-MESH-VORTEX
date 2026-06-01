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

## 📝 LISTA OCZEKIWANYCH STRATEGII (do katalogu)

*Komendant dostarczy plik ze strategiami — zostaną skatalogowane wg powyższego formatu.*

Poszukiwane strategie od:
- **Larry Williams** — Williams %R, COT traders
- **Linda Bradford Raschke** — rhythm patterns, oscillator combos
- **Mark Minervini** — SEPA (Specific Entry Point Analysis)
- **Stan Weinstein** — Stage Analysis (4 stages)
- **Jesse Livermore** — pivotal points, position sizing
- **Paul Tudor Jones** — macro turning points
- **Michael Covel** — trend following systems
- **Andreas Clenow** — systematic momentum
- **Nial Fuller** — price action setups
- **Al Brooks** — price action bars

---

*"Strategia bez neuronu to plan bez żołnierzy. Neuron bez strategii to żołnierz bez rozkazu."* — VITRUVIUSZ
