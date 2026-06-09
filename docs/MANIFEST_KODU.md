# 🔱 MANIFEST KODU IMPERIUM — Kontrola Prawa XIX

> **Jedyne oficjalne źródło prawdy** o tym, ile kodu naprawdę istnieje w Imperium.
> **Zasada:** `✅` = kod + testy na branchu `claude/sleepy-fermi-dsdE4`. `🔴` = tylko katalog.
> **Aktualizacja:** w tym samym commicie co kod. Nieaktualny MANIFEST = złamanie Prawa XIX.
> **Klucze w MANIFEST = klucze w kodzie (KLUCZ w klasie).** Żadnych aliasów ani starych nazw.

**Stan na:** 2026-06-09 · **Gałąź:** `claude/sleepy-fermi-dsdE4`
**Zaimplementowane:** 55 neuronów (zarejestrowane w roju) + 12 zwiadowców = **67 modułów w kodzie**
**Aktywne / wyciszone:** 48 aktywnych + 7 wyciszonych, z czego:
  • **42 czyste OHLCV** (M/T/F/A/L/V/H/N/Z/O) — liczą z barów bez żadnego API (w tym V-14 Choppiness, L-14 Ulcer, H-01 Hurst-DFA, N-01 Permutation Entropy, Z-01 VPIN ToxicFlow, Z-03 Bubble/Crash kill-switch, Z-04 Cascade/Dead-Cat, X-27 Value Convergence, OC-05 WashTrading, D-01 PathSignature)
  • **4 kat. R obudzone (Faza B)** — PSY-01/02/04 z AdapterFutures (Binance fapi publiczne, bez klucza), PSY-03 z AdapterFearGreed (alternative.me) — wpięte w pipeline Dyrygenta
  • **1 kat. F obudzony (Faza C)** — V-03 CVD z AdapterCVD (Binance aggTrades publiczne, bez klucza)
  • **3 budzone WEWNĘTRZNIE** (SMC-01/02/03) — liczą z barów przez most EXP-05, ożywają w żywym Legatusie (`zbuduj_legatusa`), **bez żadnego API**
  • **4 wymaga ZEWNĘTRZNEGO API on-chain** (OC-01..04) — Glassnode/CryptoQuant (Faza D)
**Elitarne (Prawo XX):** 15 (3 neurony + 12 zwiadowców)
**W katalogu:** 299 neuronów + 12 zwiadowców = **311 zaplanowanych**
**Do wdrożenia:** 244 neuronów

> **Metoda liczenia (Prawo XIX):** liczba = klasy `Neuron*(MikroNeuron)` zarejestrowane
> w `imperium/legiony/rejestr.py` (`wszystkie_neurony()`), zweryfikowane testem
> `test_rejestr_wszystkie_neurony` (== 55). NIE liczymy klas-sierot poza rojem.
> **Audyt 2026-06-02:** MANIFEST używał starych kluczy (M-RSI, T-ADX, V-OBV, S-OB, P-FG, O-MVRV).
> Naprawiono — wszystkie klucze zsynchronizowane z kodem (KLUCZ w klasie Pythona).

---

## 🔬 ZWIADOWCY EXPLORATORES (12/12 w kodzie) — wszyscy 🎖️ elitarni (E1)

> **Prawo XX:** każdy Exploratores = ELITARNY=True z definicji klasy (kryterium E1 — własna matematyka poza Bramą).

| KLUCZ | Klasa | Plik | KAT | Status | Opis |
|-------|-------|------|-----|--------|------|
| EXP-01 🎖️ | ZwiadowcaHiguchi | `zwiadowcy/exp_higuchi.py` | E | ✅ aktywny | Fraktalny wymiar Higuchi (E1) |
| EXP-02 🎖️ | ZwiadowcaHAScalper | `zwiadowcy/exp_ha_scalper.py` | M | ✅ aktywny | Heiken Ashi pattern (E1) |
| EXP-03 🎖️ | ZwiadowcaHurst | `zwiadowcy/exp_hurst.py` | E | ✅ aktywny | Wykładnik Hursta (E1) |
| EXP-04 🎖️ | ZwiadowcaKalman | `zwiadowcy/exp_kalman.py` | V | ✅ aktywny | Filtr Kalmana (E1) |
| EXP-05 🎖️ | ZwiadowcaSMC | `zwiadowcy/exp_smc.py` | S | ✅ aktywny | Smart Money Concepts (E1) |
| EXP-06 🎖️ | ZwiadowcaKatana | `zwiadowcy/exp_katana.py` | M | ✅ aktywny | Katana Scalper (IMV-ADO 🔱, E1+E5) |
| EXP-07 🎖️ | ZwiadowcaTLP | `zwiadowcy/exp_tlp.py` | M | ✅ aktywny | A-TLP breakout (IMV-ADO 🔱, E1+E5) |
| EXP-08 🎖️ | ZwiadowcaNightTurbo | `zwiadowcy/exp_night.py` | M | ✅ aktywny | Night Turbo (IMV-ADO 🔱, E1+E5) |
| EXP-09 🎖️ | ZwiadowcaLiquiditySweep | `zwiadowcy/exp_sweep.py` | S | ✅ aktywny | Liquidity Sweep SMC (IMV-ADO 🔱, E1+E5) |
| EXP-10 🎖️ | ZwiadowcaDisplacement | `zwiadowcy/exp_displacement.py` | S | ✅ aktywny | Structural Displacement (IMV-ADO 🔱, E1+E5) |
| EXP-11 🎖️ | ZwiadowcaDynamic | `zwiadowcy/exp_dynamic.py` | M | ✅ aktywny | Dynamic Pro + spread guard (IMV-ADO 🔱, E1+E5) |
| EXP-12 🎖️ | ZwiadowcaAtmabhan | `zwiadowcy/exp_atmabhan.py` | F | 🔇 wyciszony (L2 feed) | AP-Mode microstructure (IMV-ADO 🔱, E1+E5) |

---

## ⚡ NEURONY ZAIMPLEMENTOWANE (55/299)

> **Klucze = dokładnie te, które widać w `n.KLUCZ` w kodzie.** Żadnych aliasów.
> Kolumna KAT = `n.KATEGORIA` (litera) wg legendy: M=Momentum T=Trend V=Zmienność
> F=Flow/Wolumen O=On-chain L=Leverage R=Reżim S=Struktura A=Anty-manipulacja

### Plik: `neurony/momentum.py`

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| X-01 | NeuronRSI | M | 6 | ✅ aktywny | RSI_14 | — |
| X-02 | NeuronStochRSI | M | 6 | ✅ aktywny | STOCHRSI | — |
| X-03 | NeuronMACD | M | 7 | ✅ aktywny | MACD | — |
| X-04 | NeuronBBands | M | 5 | ✅ aktywny | BBANDS | — |
| X-05 | NeuronEMACross | T | 6 | ✅ aktywny | EMA_CROSS | — |
| X-06 | NeuronWilliamsR | M | 4 | ✅ aktywny | WILLIAMS_R | — |
| X-08 | NeuronAwesome | M | 5 | ✅ aktywny | AO | — |
| X-09 | NeuronAccelerator | M | 4 | ✅ aktywny | AC | — |
| X-17 | NeuronTRIX | M | 4 | ✅ aktywny | TRIX | — |
| X-12 | NeuronBBSqueeze | M | 6 | ✅ aktywny | BB_UPPER | — |
| X-25 🔱 | NeuronATRDeviation | M | 6 | ✅ aktywny | ATR_DEVIATION | E4+E5 |
| X-26 🔱 | NeuronHAScalper | M | 7 | ✅ aktywny | HA_SCALPER | E4+E5+E7 |
| X-27 | NeuronValueConvergence | M | 6 | ✅ aktywny | VALUE_Z_200 | rewersja do wartości: Value-Z+MoMA-Z (W-273, BIB-020 Harris rozdz.16) |

### Plik: `neurony/trend.py`

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| XII-01 | NeuronADX | T | 7 | ✅ aktywny | ADX_14 | — |
| XII-02 | NeuronIchimoku | T | 8 | ✅ aktywny | ICHIMOKU | — |
| XII-03 | NeuronEMA50_200 | T | 9 | ✅ aktywny | EMA_50_200 | — |
| XII-04 | NeuronSupertrend | T | 7 | ✅ aktywny | SUPERTREND | — |
| XII-05 | NeuronFibonacci | T | 6 | ✅ aktywny | DONCHIAN | — |
| XII-06 | NeuronOBZone | T | 6 | ✅ aktywny | CLOSE_PREV | — |
| XII-07 | NeuronRSIDiv | T | 7 | ✅ aktywny | RSI_14 | — |
| X-18 | NeuronDonchian | T | 5 | ✅ aktywny | DONCHIAN | — |
| X-10 | NeuronHMA | T | 6 | ✅ aktywny | HMA | — |

### Plik: `neurony/wolumen.py`

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| V-01 | NeuronOBV | F | 7 | ✅ aktywny | OBV | — |
| V-02 | NeuronVWAP | F | 8 | ✅ aktywny | VWAP | — |
| V-03 | NeuronCVD | F | 8 | ✅ aktywny (AdapterCVD) | CVD | — |
| V-04 | NeuronVolumeAnomaly | F | 6 | ✅ aktywny | VOLUME_ANOMALY | — |
| X-11 | NeuronRVOL | F | 7 | ✅ aktywny | RVOL | — |

### Plik: `neurony/struktura.py`

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| SMC-01 | NeuronOrderBlock | S | 8 | 🌙 budzony wewnętrznie (most EXP-05) | ORDER_BLOCK | — |
| SMC-02 | NeuronFVG | S | 7 | 🌙 budzony wewnętrznie (most EXP-05) | FVG | — |
| SMC-03 | NeuronBOS | S | 9 | 🌙 budzony wewnętrznie (most EXP-05) | BOS_MSS | — |

> **🌙 = budzony wewnętrznie (NIE wymaga API).** SMC-01/02/03 są `DOSTEPNY=False` w stanie
> statycznym, ale `zbuduj_legatusa()` wywołuje `aktywuj_neurony_smc()` → `DOSTEPNY=True`,
> a EXP-05 `wstrzyknij()` dostarcza strefy OB/FVG/BOS z **samych barów OHLCV**.
> W żywym pipeline te 3 neurony GŁOSUJĄ w pełni. Audyt statyczny liczy je jako wyciszone
> tylko dlatego, że bada klasy przed zbudowaniem Legatusa — to NIE jest brak danych z API.
| VSA-01 | NeuronVSA | F | 8 | ✅ aktywny | VSA | — |

### Plik: `neurony/psychologia.py`

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| PSY-01 | NeuronFundingExtreme | R | 8 | ✅ aktywny (AdapterFutures) | FUNDING_EXTREME | — |
| PSY-02 | NeuronPanikaDetal | R | 7 | ✅ aktywny (AdapterFutures) | LS_RATIO | — |
| PSY-03 | NeuronFearGreed | R | 7 | ✅ aktywny (AdapterFearGreed) | FEAR_GREED | — |
| PSY-04 | NeuronOIDiv | R | 7 | ✅ aktywny (AdapterFutures) | OI_DIVERGENCE | — |

### Plik: `neurony/onchain.py`

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| OC-01 | NeuronMVRV | O | 9 | 🔇 wyciszony (API on-chain) | MVRV_Z | — |
| OC-02 | NeuronSOPR | O | 8 | 🔇 wyciszony (API on-chain) | SOPR | — |
| OC-03 | NeuronPuellMultiple | O | 7 | 🔇 wyciszony (API on-chain) | PUELL_MULTIPLE | — |
| OC-04 | NeuronExchangeNetflow | O | 8 | 🔇 wyciszony (API on-chain) | EXCHANGE_NETFLOW | — |
| OC-05 | NeuronWashTrading | O | 8 | ✅ aktywny (OHLCV) | WASH_SCORE_100 | W-061 |

### Plik: `neurony/straz.py` (Dywizja Anty-Manipulacji — KAT A)

| KLUCZ | Klasa | KAT | WAGA | Status | WSKAZNIK (Brama) | 🎖️ |
|-------|-------|-----|------|--------|-----------------|-----|
| A-01 | NeuronStopHunt | A | 8 | ✅ aktywny | DONCHIAN | — |
| A-02 | NeuronWickRejection | A | 7 | ✅ aktywny | OPEN | — |
| A-03 | NeuronWashVol | A | 6 | ✅ aktywny | VOLUME | — |
| A-05 | NeuronBartPattern | A | 6 | ✅ aktywny | CLOSE_PREV | — |
| VI-13 | NeuronATRLev | L | 8 | ✅ aktywny | ATR_14 | — |
| L-14 | NeuronUlcer | L | 7 | ✅ aktywny | ULCER_14 | — |
| V-13 | NeuronRealizedVol | V | 7 | ✅ aktywny | YANG_ZHANG_20 | fallback HIST_VOL_20 |
| V-14 | NeuronChoppiness | V | 7 | ✅ aktywny | CHOPPINESS_14 | — |
| H-01 | NeuronHurstDFA | H | 7 | ✅ aktywny | HURST_DFA_100 | meta-brama reżimu (DFA) |
| N-01 | NeuronPermutationEntropy | N | 7 | ✅ aktywny | PERM_ENTROPY_100 | meta-brama chaosu (PE) |
| Z-01 | NeuronToxicFlow | Z | 8 | ✅ aktywny | VPIN_50 | meta-brama obronna (VPIN) |
| Z-02 | NeuronPumpDetect | Z | 7 | ✅ aktywny | OBV | akumulacja przed pumpem (W-042) |
| Z-03 | NeuronBubbleCrash | Z | 9 | ✅ aktywny | BUBBLE_Z_200 | bubble/crash kill-switch: bubble_z+VoV+AR1 (W-278, BIB-020 Harris rozdz.28) |
| Z-04 | NeuronCascade | Z | 8 | ✅ aktywny | CASCADE_FLAG | kill-switch kaskady + dead-cat bounce LONG (W-279, BIB-020 Harris rozdz.28) |
| D-01 | NeuronPathSignature | D | 7 | ✅ aktywny 🎖️ | CLOSE_SERIES_20 | Lévy Area Close×Volume — geometria ścieżki (W-079) |

> **Litera A ożywiona** (2026-06-02): reguły WAGI_REZIMU dla A (VOLATILE ×2.0,
> PANIC ×3.0) były pre-zarejestrowane — teraz mają realne neurony. Prawo XV.
> Dekorelacja (Prawo XVI): A-01↔A-02 r=+0.24, A↔RSI |r|<0.15 — filary nowej informacji.

> **Kat. L i V wzmocnione** (2026-06-03): L-14 Ulcer Index (ryzyko spadkowe) +
> V-14 Choppiness Index (trend vs konsolidacja). Pomiar dekorelacji (Prawo XVI):
> V-13↔V-14 |r|=0.05–0.27 (dywersyfikacja), VI-13↔L-14 — VI-13 stały na danych
> testowych, L-14 dostarcza pełną wariancję kat. L (komplementarność). Czyste OHLCV.

> **Kat. H ożywiona — Hurst-DFA meta-brama** (2026-06-03, wizja W-053): H-01
> NeuronHurstDFA mierzy pamięć długiego zasięgu metodą DFA (Detrended Fluctuation
> Analysis, Peng i in. 1994) z Bramy (`HURST_DFA_100`). Nowa kategoria H = odrębna
> oś informacji (persystencja vs Trend/Zmienność). Rola meta-bramy: H≈0.5 → NEUTRAL
> („nie handluj, brak przewagi"). KOMPLEMENTARNY (Prawo XVI) do EXP-03 Hurst R/S:
> DFA detrenduje okna → odporny na niestacjonarność, inny estymator tej samej
> wielkości (jak duet Higuchi FD + Hurst R/S). Korelacja H-01↔EXP-03 do zmierzenia
> `diagnostyka_korelacji` po zebraniu danych paper-tradingu. WAGI_REZIMU: H ×1.3
> TREND_STRONG, ×1.2 RANGING, ×1.1 NORMAL.

> **Kat. N narodzona — Permutation Entropy meta-brama chaosu** (2026-06-04, wizja
> W-054): N-01 NeuronPermutationEntropy mierzy złożoność szeregu wzorcami
> porządkowymi (ordinal patterns, Bandt & Pompe 2002, Phys. Rev. Lett. 88:174102)
> z Bramy (`PERM_ENTROPY_100`, dim=3, delay=1, znormalizowana log(dim!) do [0,1]).
> Nowa kategoria N = Entropia/Informacja, odrębna OŚ informacji (struktura porządku
> vs Trend/Zmienność/Momentum) — w pełni ORTOGONALNA do RSI/MACD (Prawo XVI).
> Rola meta-bramy: PE>0.85 → chaos → NEUTRAL („rynek efektywny, nie handluj");
> PE<0.65 → przewidywalność (forbidden patterns) → struktura, potwierdza mikro-ruch.
> ~34% czulsza niż GARCH na klasteryzację zmienności. Czyste OHLCV. Korelacja
> N-01↔V/T/M do zmierzenia `diagnostyka_korelacji`. WAGI_REZIMU: N ×1.3 VOLATILE,
> ×1.2 RANGING, ×1.1 NORMAL, ×1.0 TREND_STRONG.

> **Kat. Z narodzona — VPIN ToxicFlow meta-brama obronna** (2026-06-04, wizja
> W-036): Z-01 NeuronToxicFlow mierzy toksyczność przepływu zleceń metodą VPIN
> (Volume-Synchronized Probability of Informed Trading) przez BVC (Bulk Volume
> Classification) z Bramy (`VPIN_50`, n_buckets=50, proxy barowy). Źródło: Easley,
> López de Prado, O'Hara (2012), Review of Financial Studies 25(5):1457,
> https://doi.org/10.1093/rfs/hhs053. Nowa kategoria Z = Zagrożenie, META-BRAMA
> OBRONNA: NIE wskazuje kierunku (zawsze NEUTRAL), tłumi rój przez
> pewnosc_przeciwnika. VPIN<0.3 → spokój; 0.3–0.7 → czujność (skromne tłumienie);
> VPIN>0.7 → 🚨 toksyczny przepływ, ryzyko kaskady likwidacji → wysokie tłumienie
> („nie wchodź / schodź z lewara"). KOMPLEMENTARNA (Prawo XVI) do kat. A: A wykrywa
> ślad pojedynczej zagrywki, Z mierzy agregat toksyczności przepływu. Czyste OHLCV.
> WAGI_REZIMU: Z ×2.0 PANIC (max obrona), ×1.5 VOLATILE, ×1.1 NORMAL, ×1.0 reszta.

> **V-13 upgrade Yang-Zhang** (2026-06-03, wizja W-055): NeuronRealizedVol czyta
> teraz `YANG_ZHANG_20` (annualizowana vol z pełnego OHLC, ~14× efektywniejszy
> estymator niż close-only) z fallbackiem na `HIST_VOL_20`. Ta sama skala
> (annualized × √252) → progi reżimu bez zmian. Prawo XV: pełne wykorzystanie
> informacji OHLC zamiast samego close. Źródło: Yang & Zhang (2000),
> "Drift-Independent Volatility Estimation Using High, Low, Open, and Close Prices".

---

## 📋 NEURONY DO WDROŻENIA (260 — tylko katalog)

> Źródło: `docs/KATALOG_NEURONOW.md`. Status: `🔴 tylko katalog` — brak kodu.
> Implementacja: etapami, z pomiarem dekorelacji po każdej fazie (Prawo XVI).

### Legion X Equestris — M5/M15 mikro-scalp (priorytet: WYSOKI)

| KLUCZ | Nazwa | Opis | Status |
|-------|-------|------|--------|
| X-02 | StochRSI | Stochastic RSI ekstrema | ✅ kod (momentum.py, aktywny) |
| X-08 | Awesome Osc | Momentum 5 vs 34 SMA | ✅ kod (momentum.py, aktywny) |
| X-11 | RVOL | Relative Volume | ✅ kod (wolumen.py, aktywny) |
| X-17 | TRIX | TRIX szybki | ✅ kod (momentum.py, aktywny) |
| X-18 | Donchian | Donchian Channel M15 | ✅ kod (trend.py, aktywny) |
| X-25 | ATRDeviation 🔱 | ATR Z-score kameleon (IMV-ADO) | ✅ kod (momentum.py, aktywny) |
| X-26 | HAScalper 🔱 | HA Scalper bez repainting (IMV-ADO) | ✅ kod (momentum.py, aktywny) |
| X-01 | EMA Cross | EMA(9/21) kierunek | 🔴 katalog (X-05 EMACross to odpowiednik) |
| X-03 | CVD | Cumulative Volume Delta | ✅ V-03 aktywny (AdapterCVD, Faza C) |
| X-04 | VWAP Bounce | VWAP magnes dnia | 🔴 katalog (V-02 VWAP = odpowiednik) |
| X-05 | OrderFlow | Bid/Ask Imbalance | 🔴 katalog |
| X-06 | ATR-Stop | ATR×1.5 dynamiczny stop | 🔴 katalog |
| X-07 | Williams %R | Szybkie ekstrema | 🔴 katalog (X-06 WilliamsR = odpowiednik) |
| X-09 | Accelerator | Przyspieszenie momentum (2. pochodna AO) | ✅ kod (momentum.py, aktywny) |
| X-10 | HMA | Hull Moving Average | ✅ kod (trend.py, aktywny) |
| X-12 | BB Squeeze | Bollinger Squeeze M5 | 🔴 katalog |
| X-13 | Taker CVD | Spot Taker CVD | 🔴 katalog |
| X-14 | CVD Absorb | CVD Absorption | 🔴 katalog |
| X-15 | Net Volume | Net Volume / BoP | 🔴 katalog |
| X-16 | Volume Profile | POC/VAH/VAL M15 | 🔴 katalog |
| X-19 | BubbleFlow 🔱 | Bubble Flow Tron System | 🔴 katalog |
| X-20 | AIOrderFlow 🔱 | AI Probabilistic OrderFlow | 🔴 katalog |
| X-21 | FlowMatrix 🔱 | Flow Matrix Pro | 🔴 katalog |
| X-22 | BigTrades 🔱 | BigTrades Quant Analyzer | 🔴 katalog |
| X-23 | AetherVol 🔱 | AetherEdge Volume Surge | 🔴 katalog |
| X-24 | WicklessC 🔱 | xGhozt Wickless Candles | 🔴 katalog |

---

### Pozostałe legiony (248 neuronów) — pełen skatalogowany rejestr

> Szczegóły: `docs/KATALOG_NEURONOW.md`. Tu podsumowanie per legion.

| Legion | Skatalogowane | Wdrożone | Do wdrożenia |
|--------|--------------|---------|--------------|
| X Equestris (M5/M15) | 26 | 9 (X-02,X-08,X-09,X-10,X-11,X-17,X-18,X-25,X-26) | 17 |
| III Augusta (H1) | ~45 | 9 (XII-01..04, V-01..04, VSA-01) + PSY-01..04 ✅ (Faza B) + wyciszone: V-03,SMC-01..03 | ~36 |
| XII Fulminata (D1) | ~40 | 4 (OC-01..OC-04, wyciszone) | ~36 |
| Pozostałe legiony | ~188 | 12 (X-01,X-03..X-06 + dalej wg schemy) | ~176 |
| **RAZEM** | **299** | **55** | **244** |

---

## 🔧 MODUŁY INFRASTRUKTURY (poza neuronami)

| Moduł | Plik | Status |
|-------|------|--------|
| BudowniczyWskaznikow | `legiony/budowniczy_wskaznikow.py` | ✅ aktywny |
| GeneralLegatus | `legiony/legatus.py` | ✅ aktywny |
| DiagnostykaKorelacji | `legiony/diagnostyka_korelacji.py` | ✅ aktywny |
| Igrzyska / Koloseum | `koloseum/` | ✅ aktywny |
| BramaKalkulatora | `fundament/brama_kalkulatora.py` | ✅ aktywny |
| KalkulatorLewara | `pretorianie/kalkulator_lewara.py` | ✅ aktywny |
| BezpiecznikKapitalu (twardy circuit-breaker AOA 30%, W-028) | `pretorianie/kalkulator_lewara.py` | ✅ aktywny |
| BezpiecznikKrzywejKapitalu (Equity-Curve Circuit Breaker, W-062) | `pretorianie/kalkulator_lewara.py` | ✅ aktywny |
| Volatility Drag (W-130, Sinclair BIB-008 — erozja ½λ(λ−1)σ² lewara) | `pretorianie/kalkulator_lewara.py` | ✅ aktywny |
| PaperTradingEngine | `koloseum/paper_trading.py` | ✅ aktywny |
| Dyrygent (orkiestrator cyklu end-to-end) | `koloseum/dyrygent.py` | ✅ aktywny |
| Backtest (przejazd po historii) | `koloseum/backtest.py` | ✅ aktywny |
| Detektor Lookahead-bias (Freqtrade LA-01) | `koloseum/lookahead.py` | ✅ aktywny |
| **Namiestnik** (Regime + Timeframe-Aware Gating Network) | `koloseum/namiestnik.py` | ✅ aktywny |
| CzytnikCSV (CryptoDataDownload → bary) | `akwedukty/czytnik_csv.py` | ✅ aktywny |
| Dywizja Strategii (model + silnik) | `legiony/strategie/baza.py` | ✅ aktywny |
| Rejestr Strategii (Klucznik) | `legiony/strategie/rejestr_strategii.py` | ✅ aktywny |
| Framework Adapterów (most API→rój) | `akwedukty/adaptery/baza.py` | ✅ aktywny |
| Adaptery testowe (OnChain/Futures/CVD mock) | `akwedukty/adaptery/testowy.py` | ✅ aktywny (mock) |
| AdapterFearGreed (PSY-03, alternative.me) | `akwedukty/adaptery/feargreed.py` | ✅ aktywny (realne API) |
| AdapterFutures (PSY-01/02/04, Binance fapi publiczne) | `akwedukty/adaptery/futures.py` | ✅ aktywny (realne API, bez klucza) |
| AdapterCVD (V-03, Binance aggTrades publiczne) | `akwedukty/adaptery/cvd.py` | ✅ aktywny (realne API, bez klucza) |

---

## 🗺️ DYWIZJA STRATEGII — Klucznik + silnik dopasowania (Prawo XIX/XXI)

> **Wizja:** neurony wysyłają sygnały → silnik automatycznie dobiera NAJBLIŻSZĄ
> strategię z bazy do bieżącej sytuacji rynku. Potem kalibracja w testach/live.

| Element | Plik | Rola |
|---------|------|------|
| `Strategia` (model) | `strategie/baza.py` | przepis: które neurony, w jakiej roli (wejście/filtr/wyjście) |
| `dobierz_najlepsze()` | `strategie/baza.py` | silnik: sygnały → top-3 pasujące strategie + kierunek |
| `wszystkie_strategie()` | `strategie/rejestr_strategii.py` | 15 strategii zmapowanych na ŻYWE klucze kodu |
| **Wpięcie w Legatusa** | `legiony/legatus.py` | `RaportLegatusa.strategie_dopasowane` — Generał zwraca dobrane strategie w każdym raporcie |

**Klucznik (strażnik spójności):** audyt Warstwa 4 (`narzedzia/audyt_spojnosci.py`)
pilnuje, że KAŻDY klucz w strategii istnieje w kodzie i jest aktywny — żadnych
neuronów-widm. Test: `test_klucznik_strategie_uzywaja_istniejacych_neuronow`.

**Stan:** 15 strategii (klucze: 20 — wszystkie aktywne). Status każdej: SZKIC
(czeka na kalibrację w Koloseum). Strategie z katalogu wymagające nieistniejących
neuronów (OrderFlow, CVD, SMC, on-chain) wejdą gdy te neurony ożyją.

---

## 🔌 FRAMEWORK ADAPTERÓW — most API → rój (model "test teraz → auto-wybudzenie")

> **Wizja (Cezar):** "teraz wersja testowa, a później łatwe auto-wybudzenie".
> Adaptery realizują ten model dla 9 neuronów wymagających zewnętrznego API.
> Wzór skopiowany z mostu SMC (`wstrzyknij()` + `aktywuj_neurony_smc()`).

| Element | Plik | Rola |
|---------|------|------|
| `AdapterDanych` (baza) | `akwedukty/adaptery/baza.py` | `wzbogac()` dolewa dane do dict, `aktywuj()`/`usypiaj()` budzi/usypia neurony domeny |
| `AdapterTestowyOnChain` | `akwedukty/adaptery/testowy.py` | mock OC-01..04 (scenariusze: kapitulacja/euforia/neutralny) |
| `AdapterTestowyFutures` | `akwedukty/adaptery/testowy.py` | mock PSY-01..04 (panika/chciwość/neutralny) |
| `AdapterTestowyCVD` | `akwedukty/adaptery/testowy.py` | mock V-03 (akumulacja/dystrybucja/neutralny) |

**Przepływ (identyczny jak SMC):** `adapter.wzbogac(wskazniki, symbol)` → dict ma
klucze API → `adapter.aktywuj()` budzi neurony → rój głosuje. **Test→produkcja:**
podmieniamy tylko `pobierz()` na wersję uderzającą w MEXC/Glassnode (klucze API
WYŁĄCZNIE z `os.getenv` — Prawo bezpieczeństwa). Interfejs stały → reszta bez zmian.

**Prawo XV:** `aktywuj()` budzi neuron tylko razem z adapterem dostarczającym
jego dane. Bez adaptera neuron śpi (świadomie). `usypiaj()` przywraca stan —
testy nie fałszują statycznego audytu. Testy: `tests/test_adaptery.py` (19).

**Pierwszy prawdziwy adapter:** `AdapterFearGreed` (PSY-03) — darmowe API
alternative.me (bez klucza). `pobierz()` używa wstrzykiwanego fetchera: produkcja
= HTTP urllib (stdlib), testy = mock z próbką JSON (pełny test OFFLINE). Gdy
`FEAR_GREED_INDEX` płynie, PSY-03 ożywa i głosuje kontrariańsko (strach→LONG,
chciwość→SHORT). Wybudzanie granularne: budzi TYLKO PSY-03, nie całą domenę PSY.
**Uwaga środowisko:** wywołanie na żywo wymaga, by polityka sieci zezwoliła na
`api.alternative.me` (w obecnym sandboksie zwraca 403 — kod gotowy, czeka na dostęp).

---

## 📈 HISTORIA FAZY ROZBUDOWY

| Data | Faza | Wdrożone | Łącznie | Uwagi |
|------|------|----------|---------|-------|
| 2026-05-xx | Faza 0 — rdzeń | 21 neuronów | 21 | Momentum/Trend/Wolumen/Struktura/Psychologia/Onchain |
| 2026-05-xx | Adopcja IMV-ADO | +2 neurony (X-25, X-26) | 23 | ATRDeviation + HAScalper |
| 2026-05-xx | Exploratores EXP-01..05 | +5 zwiadowców | 23+5 | Higuchi, HA, Hurst, Kalman, SMC |
| 2026-06-01 | Exploratores EXP-06..12 | +7 zwiadowców | 27+12=39 | Katana, TLP, Night, Sweep, Displacement, Dynamic, Atmabhan(wyciszony) |
| 2026-06-01 | Audyt liczby + X-02 | +1 neuron (StochRSI) | 28+12=40 | Ożywienie sieroty X-02; wycofanie redundantnego VI-01 |
| 2026-06-01 | Faza 1 — ożywienie OHLCV | +4 neurony | 32+12=44 | X-08 Awesome, X-11 RVOL, X-17 TRIX, X-18 Donchian (aktywne) |
| 2026-06-02 | Prawo XX + kategoria fix | 0 nowych | 32+12=44 | Status elitarny; KAT M→F→R→O; WAGI_REZIMU; MANIFEST klucze naprawione |
| 2026-06-02 | Faza 2 — X-09, X-10 | +2 neurony | 34+12=46 | Accelerator + HMA; dekorelacja AC↔AO=+0.23 (Prawo XVI) |
| 2026-06-02 | Faza 3 — XII-05, XII-07, X-12 | +3 neurony | 37+12=49 | Fibonacci, RSI Dywergencja, BB Squeeze; +6 strategii (13 łącznie) |
| 2026-06-02 | Faza 4 — A-01, A-02 (Straż) | +2 neurony | 39+12=51 | Stop Hunt, Wick Rejection; litera A ożywiona (Prawo XV); +1 strategia IMV-DEF-001 (14 łącznie) |
| 2026-06-02 | Faza 5 — A-03, A-05, XII-06 | +3 neurony | 42+12=54 | WashVol, BartPattern (Straż); OBZone (XII) — Order Block OHLCV |
| 2026-06-02 | Faza 6 — Framework Adapterów | +2 moduły | most API→rój | Baza + 3 adaptery testowe (OnChain/Futures/CVD); auto-wybudzanie 9 neuronów API; 13 testów |
| 2026-06-02 | Faza 7 — AdapterFearGreed | +1 moduł | PSY-03 realne API | Pierwszy prawdziwy adapter (alternative.me, bez klucza); wstrzykiwany fetcher; +6 testów offline |
| 2026-06-02 | Dywizja Strategii + Klucznik | +2 moduły | 46+2 | Strategie jako KOD, silnik dopasowania, audyt Warstwa 4 |
| 2026-06-03 | Faza A — kat. L+V + 3 martwe naprawione | +2 neurony | 44+12=56 | VI-13 ATR-Lev (L), V-13 RealizedVol (V); naprawa XII-07/X-12/A-05 |
| 2026-06-03 | **Faza B — kat. R obudzona** | +1 adapter | aktywne 32→36 | AdapterFutures (Binance fapi publiczne) budzi PSY-01/02/04; PSY-03 (FearGreed) wpięty; adaptery w pipeline Dyrygenta; +2 strategie VI-LV (17 łącznie); +9 testów |
| 2026-06-03 | **Faza C — V-03 CVD obudzony** | +1 adapter | aktywne 36→37 | AdapterCVD (Binance aggTrades publiczne, bez klucza) liczy CVD=buy−sell; pamięć CVD_PREV; wpięty w pipeline Dyrygenta; +6 testów offline |
| **Do wdrożenia** | Faza D — on-chain | +0 (4 obudzić) | — | OC-01..04 (Glassnode/CryptoQuant API) |

---

> 🔱 *"Katalog mówi: chcemy. Kod mówi: mamy. Nie mylimy tych dwóch słów nigdy."* — Prawo XIX
