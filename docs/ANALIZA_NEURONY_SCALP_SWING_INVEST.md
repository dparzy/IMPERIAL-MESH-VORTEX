# 🔬 ANALIZA — najlepsze neurony/strategie pod SCALP / SWING / INVEST

> **Cel:** porównać to, co Imperium MA w kodzie (65 neuronów), z najlepszymi praktykami
> z dokumentacji wewnętrznej i z internetu (research 2026-06-15) — i wskazać UNIKATOWE,
> zdekorelowane luki warte wdrożenia, per styl gry.
> **Metoda (Prawo I):** liczby neuronów z `rejestr.wszystkie_neurony()`; techniki zewnętrzne
> z linkami (niżej, sekcja Źródła). **Dekorelacja (Prawo XVI):** kandydat = nowy SYGNAŁ, nie
> nowa nazwa starego. **Stan na:** 2026-06-15.

---

## 1. Co MAMY dziś (per styl)

| Styl | Interwał | Neurony pokrywające (wybór z 65) |
|------|----------|----------------------------------|
| **SCALP** | M1–M15 / 1h | X-26 HA Scalper, X-01 RSI, X-02 StochRSI, V-03 CVD, V-05 Force Index, V-04 Volume Anomaly, X-11 RVOL, Z-01 VPIN, SES-01/02 sesje |
| **SWING** | 4h–1D | X-05 EMA Cross, XII-01 ADX, XII-02 Ichimoku, XII-03 EMA50/200, XII-04 Supertrend, X-18 Donchian, X-10 HMA, X-28 MTF Confluence, X-27 Value-Z, SMC-01/02/03 |
| **INVEST** | 1D–1W | OC-01 MVRV-Z, OC-02 SOPR, OC-03 Puell, OC-04 Netflow, H-01 Hurst, Z-03 Bubble-Z, RADAR-01/02/03 |

**Mocne osie:** momentum (12 neuronów), trend (11), wolumen/flow (7), brama obronna Z (5).
**Słabe osie (z mapy katalogu):** Struktura/SMC w kodzie 16%, On-chain 25%, Reżim/Sentyment 22%,
AI/ML 0%. Mikrostruktura (order-flow per poziom) — brak (czeka na feed L2, EXP-12 wyciszony).

---

## 2. Co znalazłem na zewnątrz (best practices 2025–2026) i czego NAM brakuje

### 🟥 SCALP — mikrostruktura / order-flow
Najlepsze praktyki scalpingu 2025 to **order-flow**: footprint, delta imbalance, stacked
imbalances, **delta divergence** (cena nowy szczyt, delta nie potwierdza → rewersja). Z
literatury ilościowej: **Deep Order-Flow Imbalance** (Kolm/Turiel), **Kyle's lambda**
(impakt cenowy na jednostkę wolumenu), **Amihud illiquidity** (|zwrot|/obrót).

| Technika | Mamy? | Luka |
|---|---|---|
| CVD (delta skumulowana) | ✅ V-03 | — |
| **Delta divergence** (CVD vs cena) | ❌ | tani dodatek do V-03 (OHLCV+CVD) |
| **Amihud illiquidity** (\|ret\|/obrót) | ❌ | **OHLCV-only, unikat, mierzy impakt/płynność** |
| **Kyle's lambda** (impakt cenowy) | ❌ | proxy z OHLCV/trade; pokrewny VPIN ale inna oś |
| Footprint / OFI per poziom | ❌ | wymaga L2 (EXP-12, feed) — Faza feed |

### 🟧 SWING — struktura wolumenowa
Konsensus 2025: **Volume Profile / VPOC / Value Area** (Market Profile, Dalton BIB-013) na 4h/8h
to filar swingu — pokazuje strefy akceptacji ceny (gdzie był wolumen) = realne S/R. Plus
**Anchored VWAP** (VWAP kotwiczony od istotnego pivotu, nie od początku sesji).

| Technika | Mamy? | Luka |
|---|---|---|
| VWAP kroczący | ✅ V-02 | — |
| **Anchored VWAP** (od pivotu/wydarzenia) | ❌ | inna oś niż VWAP sesyjny — kotwica strukturalna |
| **Volume Profile / VPOC + Value Area** | ❌ | **OHLCV+vol, klasyk swingu, S/R z wolumenu** |
| Keltner Channels | ❌ (kat. XII-13) | EMA+ATR kanał — pokrewny BBands, niski priorytet |
| **Cross-sectional Relative Strength** (ranking par) | ❌ | portfelowy — który coin najsilniejszy vs koszyk |

### 🟦 INVEST — cykl i wycena
On-chain mamy częściowo (MVRV/SOPR/Puell/Netflow). Brakuje **price-only** detektorów cyklu,
które są tanie i słynne: **Pi Cycle Top** (111DMA vs 2×350DMA — trafił szczyty 2013/2017/2021),
**pozycja w 4-letnim cyklu halvingu**, oraz **M2 global liquidity** (korelacja z płynnością).

| Technika | Mamy? | Luka |
|---|---|---|
| MVRV-Z, SOPR, Puell, Netflow | ✅ OC-01..04 | — (wymagają on-chain API) |
| **Pi Cycle Top** (111DMA × 2×350DMA) | ❌ | **OHLCV-only kill-switch szczytu cyklu** |
| **Pozycja w cyklu halvingu** (dni od halvingu) | ❌ | z daty — sizing/horyzont wg fazy cyklu |
| M2 Global Liquidity (korelacja) | ❌ (kat. K) | wymaga danych makro (FRED) — Faza makro |

---

## 3. PROPOZYCJE — 6 unikatowych neuronów (wykonalne TERAZ na OHLCV)

Wszystkie poniższe: **(a)** liczone z danych, które już mamy (OHLCV/CVD/data), **(b)** mierzalnie
zdekorelowane od istniejących (inna oś informacji — Prawo XVI), **(c)** pełny opis ZPO.

### SCALP
1. **A-Amihud — Illiquidity / Price-Impact** (kat. Z lub F)
   - Wzór: średnia z |zwrot_baru| / obrót_USDT (okno ~20). Wysoki = cena łatwo się rusza
     na małym wolumenie (krucha płynność, ryzyko poślizgu/manipulacji) → tłum wejścia /
     ostrożność. Niski = głęboka płynność → bezpieczne wejście.
   - Dekorelacja: VPIN mierzy TOKSYCZNOŚĆ flow, Amihud mierzy IMPAKT/płynność — inna oś.
   - Źródło: Amihud (2002) „Illiquidity and stock returns"; SSRN review 2025 (factor liquidity).

2. **DeltaDiv — Delta Divergence** (kat. F, rozszerza V-03 CVD)
   - Cena robi nowy ekstrem, a CVD nie potwierdza → wczesny sygnał rewersji (klasyka footprint).
   - Dekorelacja: V-03 to poziom CVD; tu liczy się DYWERGENCJA cena↔delta (nowa informacja).
   - Źródło: LiteFinance/NinjaTrader order-flow guides 2026.

### SWING
3. **VPOC — Volume Profile / Value Area** (kat. S lub V) ⭐ **najwyższy priorytet swing**
   - Histogram wolumenu po cenie (okno ~100 barów) → POC (cena z max wolumenem) + Value Area
     (70% wolumenu). Cena pod POC = bias long do POC; nad VA-high = wykupienie; w VA = balans.
   - Dekorelacja: nasze S/R to Donchian/BBands (ekstrema ceny); VPOC to S/R z WOLUMENU — różne.
   - Źródło: Dalton „Markets in Profile" (BIB-013); Deepvue/Quantum 2025.

4. **AVWAP — Anchored VWAP** (kat. T/F)
   - VWAP kotwiczony od ostatniego istotnego pivotu (swing high/low) zamiast od początku okna.
   - Dekorelacja: V-02 to VWAP kroczący; kotwica strukturalna daje inny poziom odniesienia.
   - Źródło: Highstrike/XS 2025 anchored-VWAP.

5. **RS-X — Cross-Sectional Relative Strength** (kat. R, portfelowy)
   - Ranking siły każdej pary vs koszyk (zwrot względny N-barowy) → wspiera Skaner Okazji
     („kupuj najsilniejsze"). Wpina się w TRYB NAJLEPSZY (selekcja TOP-N).
   - Dekorelacja: RADAR-02 to dominacja BTC (makro); RS-X to ranking względny W koszyku.
   - Źródło: SSRN 2025 factor review (momentum/cross-sectional w krypto).

### INVEST
6. **PiCycle — Pi Cycle Top** (kat. O/Z, price-only) ⭐ **kill-switch szczytu**
   - Gdy 111-dniowa MA przecina od dołu 2×350-dniowa MA → historyczny sygnał szczytu cyklu
     (2013/2017/2021, potem spadki 52–86%). Czysty OHLCV, działa na 1D.
   - Dekorelacja: OC-01 MVRV to wycena on-chain; Pi Cycle to geometria średnich cenowych — inna oś.
   - Źródło: Newhedge / Pintu Academy 2025 (Pi Cycle Top).

---

## 4. Rekomendacja priorytetów (Prawo XV — największy potencjał najpierw)

| Priorytet | Neuron | Styl | Wykonalność | Powód |
|---|---|---|---|---|
| 🥇 1 | **VPOC (Volume Profile)** | SWING | OHLCV teraz | filar swingu, brak u nas struktury wolumenowej |
| 🥈 2 | **Amihud Illiquidity** | SCALP | OHLCV teraz | unikat, tania obrona przed poślizgiem/manipulacją |
| 🥉 3 | **Pi Cycle Top** | INVEST | OHLCV teraz | słynny kill-switch szczytu, zero kosztu danych |
| 4 | Delta Divergence | SCALP | mamy CVD | tani dodatek, wczesna rewersja |
| 5 | Anchored VWAP | SWING | OHLCV teraz | kotwica strukturalna |
| 6 | Cross-Sectional RS | SWING/portfel | OHLCV teraz | wzmacnia Skaner Okazji (TRYB NAJLEPSZY) |

**Plan dekorelacji (Prawo XVI):** każdy nowy neuron PO wdrożeniu przepuścić przez
`diagnostyka_korelacji.raport_dekorelacji` — zostawić tylko te z |r|<0.8 vs istniejące.

**Czego NIE robić teraz:** footprint/OFI per poziom (wymaga L2 feed), M2/makro (wymaga FRED),
AI/ML kat. E (Faza 2+) — wszystkie zablokowane danymi/zakresem, nie pomysłem.

---

## 5. Źródła (research 2026-06-15)
- [LiteFinance — Order Flow / Footprint 2026](https://www.litefinance.org/blog/for-beginners/trading-strategies/order-flow-trading-with-footprint-charts/)
- [traders.mba — Order Flow Imbalance Scalping](https://traders.mba/support/order-flow-imbalance-scalping/)
- [Deepvue — Volume Profile Strategies](https://deepvue.com/indicators/volume-profile-strategies/)
- [Highstrike — Mastering VWAP 2025](https://highstrike.com/vwap/)
- [XS — Anchored VWAP](https://www.xs.com/en/blog/anchored-vwap/)
- [Newhedge — Bitcoin Pi Cycle Top](https://newhedge.io/bitcoin/pi-cycle-top-indicator)
- [Pintu Academy — BTC Top Cycle Indicators](https://pintu.co.id/en/academy/post/bitcoin-top-cycle-indicator)
- [SSRN — Quantitative Alpha in Crypto Markets (review 2025)](https://papers.ssrn.com/sol3/Delivery.cfm/5225612.pdf?abstractid=5225612&mirid=1)
- [Frontiers — Microstructure Alpha in Crypto (2026)](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2026.1811716/full)
- [QuantPedia — Deep Order Flow Imbalance](https://quantpedia.com/how-to-use-deep-order-flow-imbalance/)

---

## 6. POMIAR DEKORELACJI po wdrożeniu (W-322, Prawo XVI — mierzone, nie zgadywane)

5 z 6 propozycji wdrożono (Cross-Sectional RS odłożony — wymaga cross-symbol w pętli).
Pomiar na 220 barach 4h BTC (`narzedzia/dekorelacja_w322.py`), sygnał = kierunek×pewność:

| Neuron | Aktywny | max \|r\| | Werdykt |
|--------|---------|-----------|---------|
| V-06 Delta Divergence | 59/220 | 0.41 (vs X-03 MACD) | ✅ czysta dekorelacja |
| V-07 Anchored VWAP | 147/220 | 0.54 (vs XII-02 Ichimoku) | ✅ czysta dekorelacja |
| VP-01 Volume Profile | 133/220 | **0.85** (vs XII-01 ADX, r=−0.85) | ⚠️ graniczna — do OOS na innych parach |
| Z-06 Amihud | 0/220 | — (stały) | uśpiony: BTC 4h płynny (warunkowy, ożywa przy cienkiej księdze) |
| Z-07 Pi Cycle Top | 0/220 | — (stały) | uśpiony: brak szczytu cyklu w oknie (ożywa na cross 111/350) |

**Wnioski (Prawo XVI):**
- V-06, V-07 — niosą NOWĄ informację (|r|<0.8), filary dywersyfikacji. Zostają z pełną wagą.
- VP-01 — graniczna antykorelacja z ADX (−0.85) NA JEDNYM oknie/parze. To NIE jest dowód
  redundancji (jedno okno ≠ robustny pomiar — Prawo XVI). Zostaje, oznaczony do pomiaru
  na 5 parach OOS przed ewentualną korektą wagi. Mechanicznie VPOC (struktura wolumenu)
  ≠ ADX (siła trendu) — wysokie |r| tu może być specyfiką trendowego okna BTC.
- Z-06, Z-07 — warunkowe/uśpione w tym oknie (zgodnie z naturą: Amihud ożywa przy kruchej
  płynności, Pi Cycle na szczycie cyklu). Dowód żywotności: WERYFIKACJA_ADAPTEROW w audycie.

---

## 7. A/B IMPAKT na TRYB NAJLEPSZY (W-322, Prawo I — zmierzony, nie założony)

Pełny stack 4h, to samo okno 2022→2026 (7500 barów/parę), `narzedzia/ab_w322.py`
(monkey-patch `wszystkie_neurony` — czyste A/B 65 vs 70):

| Wariant | Trade | WR | PnL |
|---------|-------|-----|-----|
| PRZED (65, bez W-322) | 722 | 43.8% | **+5.79%** |
| PO (70, z W-322) | 717 | 43.8% | **+5.19%** |
| **IMPAKT** | −5 | = | **−0.59 pp** |

**Wniosek (Prawo I — niewygodny, ale prawdziwy):** dodanie 5 nowych neuronów NIE poprawiło
TRYBU NAJLEPSZEGO na 4h — lekko pogorszyło (−0.6 pp, poziom szumu). PRZED odtworzył
dokładnie udokumentowane +5.8% (W-321b) → patch i pomiar wiarygodne.

**Dlaczego (mechanizm):** Z-06 Amihud (defensywny, tłumi przy cienkiej płynności) uciął
5 trade'ów — a na tym gruboogonowym backteście ucinanie trade'ów ucina ekspozycję na ogon
DOGE (ta sama lekcja co W-318: filtr ↓ryzyko, ale ↓gruby ogon). Pozostałe (VP/Delta/AVWAP)
to neurony rewersji/struktury, lekko rozcieńczyły selekcję trend-following na 4h.

**Decyzja (Prawo XV/XVI):** neurony ZOSTAJĄ aktywne (są zdekorelowane — niosą nową
informację; −0.6pp to szum; celują w warunki NIEOBECNE w tym oknie: Amihud→cienka płynność,
Pi Cycle→szczyt cyklu 1D, VP/Delta/AVWAP→swing-rewersja). ALE: **nie zakładamy ich korzyści
na 4h trend-following**. Realna wartość wymaga (a) wagowania reżimowego (WAGI_REZIMU — dać im
wagę tam gdzie działają), lub (b) pomiaru w ich docelowym stylu (scalp/invest). Auto-założenie
„więcej neuronów = lepiej" zostało SFALSYFIKOWANE pomiarem.
