# 🔱 MANIFEST KODU IMPERIUM — Kontrola Prawa XIX

> **Jedyne oficjalne źródło prawdy** o tym, ile kodu naprawdę istnieje w Imperium.
> **Zasada:** `✅` = kod + testy na branchu `claude/sleepy-fermi-dsdE4`. `🔴` = tylko katalog.
> **Aktualizacja:** w tym samym commicie co kod. Nieaktualny MANIFEST = złamanie Prawa XIX.

**Stan na:** 2026-06-02 · **Gałąź:** `claude/sleepy-fermi-dsdE4`
**Zaimplementowane:** 32 neurony (zarejestrowane w roju) + 12 zwiadowców = **44 moduły w kodzie**
**Aktywne / wyciszone:** 20 aktywnych (czyste OHLCV) + 12 wyciszonych (API/feed)
**W katalogu:** 299 neuronów + 12 zwiadowców = **311 zaplanowanych**
**Do wdrożenia:** 267 neuronów

> **Metoda liczenia (Prawo XIX):** liczba = klasy `Neuron*(MikroNeuron)` zarejestrowane
> w `imperium/legiony/rejestr.py` (`wszystkie_neurony()`), zweryfikowane testem
> `test_rejestr_wszystkie_neurony` (== 32). NIE liczymy klas-sierot poza rojem.
> **Audyt 2026-06-01:** wykryto 2 neurony-sieroty w `mikro_neuron.py` (X-02 StochRSI,
> VI-01 FundingRate). Naprawa: X-02 promowany do roju; VI-01 wycofany (redundancja).
> **Faza 1 (2026-06-01):** ożywiono 4 neurony z katalogu na czystym OHLCV (aktywne):
> X-08 Awesome, X-11 RVOL, X-17 TRIX, X-18 Donchian — zdekorelowane (Prawo XVI).

---

## 🔬 ZWIADOWCY EXPLORATORES (12/12 w kodzie) — wszyscy 🎖️ elitarni (E1)

> **Prawo XX:** każdy Exploratores = ELITARNY=True z definicji klasy (kryterium E1 — własna matematyka poza Bramą).

| KLUCZ | Klasa | Plik | Status | Opis |
|-------|-------|------|--------|------|
| EXP-01 🎖️ | ZwiadowcaHiguchi | `zwiadowcy/exp_higuchi.py` | ✅ aktywny | Fraktalny wymiar Higuchi (E1) |
| EXP-02 🎖️ | ZwiadowcaHAScalper | `zwiadowcy/exp_ha_scalper.py` | ✅ aktywny | Heiken Ashi pattern (E1) |
| EXP-03 🎖️ | ZwiadowcaHurst | `zwiadowcy/exp_hurst.py` | ✅ aktywny | Wykładnik Hursta (E1) |
| EXP-04 🎖️ | ZwiadowcaKalman | `zwiadowcy/exp_kalman.py` | ✅ aktywny | Filtr Kalmana (E1) |
| EXP-05 🎖️ | ZwiadowcaSMC | `zwiadowcy/exp_smc.py` | ✅ aktywny | Smart Money Concepts (E1) |
| EXP-06 🎖️ | ZwiadowcaKatana | `zwiadowcy/exp_katana.py` | ✅ aktywny | Katana Scalper (IMV-ADO 🔱, E1+E5) |
| EXP-07 🎖️ | ZwiadowcaTLP | `zwiadowcy/exp_tlp.py` | ✅ aktywny | A-TLP breakout (IMV-ADO 🔱, E1+E5) |
| EXP-08 🎖️ | ZwiadowcaNightTurbo | `zwiadowcy/exp_night.py` | ✅ aktywny | Night Turbo (IMV-ADO 🔱, E1+E5) |
| EXP-09 🎖️ | ZwiadowcaLiquiditySweep | `zwiadowcy/exp_sweep.py` | ✅ aktywny | Liquidity Sweep SMC (IMV-ADO 🔱, E1+E5) |
| EXP-10 🎖️ | ZwiadowcaDisplacement | `zwiadowcy/exp_displacement.py` | ✅ aktywny | Structural Displacement (IMV-ADO 🔱, E1+E5) |
| EXP-11 🎖️ | ZwiadowcaDynamic | `zwiadowcy/exp_dynamic.py` | ✅ aktywny | Dynamic Pro + spread guard (IMV-ADO 🔱, E1+E5) |
| EXP-12 🎖️ | ZwiadowcaAtmabhan | `zwiadowcy/exp_atmabhan.py` | 🔇 wyciszony (L2 feed) | AP-Mode microstructure (IMV-ADO 🔱, E1+E5) |

---

## ⚡ NEURONY ZAIMPLEMENTOWANE (32/299)

### Plik: `neurony/momentum.py`

| KLUCZ | Klasa | Status | Opis |
|-------|-------|--------|------|
| M-RSI | NeuronRSI | ✅ aktywny | RSI(14) z dywergencją |
| X-02 | NeuronStochRSI | ✅ aktywny | Stochastic RSI %K (Brama: STOCHRSI) |
| X-08 | NeuronAwesome | ✅ aktywny | Awesome Oscillator (median price) |
| X-17 | NeuronTRIX | ✅ aktywny | TRIX potrójnie wygładzone momentum |
| M-MACD | NeuronMACD | ✅ aktywny | MACD crossover |
| M-BB | NeuronBBands | ✅ aktywny | Bollinger Bands squeeze/bounce |
| M-EMA | NeuronEMACross | ✅ aktywny | EMA 9/21 cross |
| M-WR | NeuronWilliamsR | ✅ aktywny | Williams %R ekstrema |
| X-25 🔱🎖️ | NeuronATRDeviation | ✅ aktywny | ATR Z-score kameleon (IMV-ADO, E4+E5) |
| X-26 🔱🎖️ | NeuronHAScalper | ✅ aktywny | HA Scalper bez repainting (IMV-ADO, E4+E5+E7) |

### Plik: `neurony/trend.py`

| KLUCZ | Klasa | Status | Opis |
|-------|-------|--------|------|
| T-ADX | NeuronADX | ✅ aktywny | ADX siła trendu |
| T-ICHI | NeuronIchimoku | ✅ aktywny | Ichimoku cloud |
| T-EMA50 | NeuronEMA50_200 | ✅ aktywny | EMA 50/200 cross |
| T-SUPER | NeuronSupertrend | ✅ aktywny | Supertrend ATR |
| X-18 | NeuronDonchian | ✅ aktywny | Donchian Channel wybicia |

### Plik: `neurony/wolumen.py`

| KLUCZ | Klasa | Status | Opis |
|-------|-------|--------|------|
| V-OBV | NeuronOBV | ✅ aktywny | On-Balance Volume |
| V-VWAP | NeuronVWAP | ✅ aktywny | VWAP bounce |
| X-11 | NeuronRVOL | ✅ aktywny | Relative Volume (wsparcie ruchu) |
| V-CVD | NeuronCVD | 🔇 wyciszony (brak CVD z Bramy) | Cumulative Volume Delta |
| V-VANOM | NeuronVolumeAnomaly | ✅ aktywny | Volume anomaly detection |

### Plik: `neurony/struktura.py`

| KLUCZ | Klasa | Status | Opis |
|-------|-------|--------|------|
| S-OB | NeuronOrderBlock | 🔇 wyciszony (brak danych SMC z Bramy) | Order Block SMC |
| S-FVG | NeuronFVG | 🔇 wyciszony (brak danych SMC z Bramy) | Fair Value Gap |
| S-BOS | NeuronBOS | 🔇 wyciszony (brak danych SMC z Bramy) | Break of Structure |
| S-VSA | NeuronVSA | ✅ aktywny | Volume Spread Analysis |

### Plik: `neurony/psychologia.py`

| KLUCZ | Klasa | Status | Opis |
|-------|-------|--------|------|
| P-FG | NeuronFearGreed | 🔇 wyciszony (API Fear&Greed) | Fear & Greed index |
| P-FUND | NeuronFundingExtreme | 🔇 wyciszony (API funding) | Funding rate ekstrema |
| P-PANIK | NeuronPanikaDetal | 🔇 wyciszony (API/feed) | Panika detalu |
| P-OIDIV | NeuronOIDiv | 🔇 wyciszony (API OI) | OI divergence |

### Plik: `neurony/onchain.py`

| KLUCZ | Klasa | Status | Opis |
|-------|-------|--------|------|
| O-MVRV | NeuronMVRV | 🔇 wyciszony (API on-chain) | MVRV Z-score |
| O-SOPR | NeuronSOPR | 🔇 wyciszony (API on-chain) | SOPR sentiment |
| O-PUELL | NeuronPuellMultiple | 🔇 wyciszony (API on-chain) | Puell Multiple |
| O-NETFLOW | NeuronExchangeNetflow | 🔇 wyciszony (API on-chain) | Exchange netflow |

---

## 📋 NEURONY DO WDROŻENIA (271 — tylko katalog)

> Źródło: `docs/KATALOG_NEURONOW.md`. Status: `🔴 tylko katalog` — brak kodu.
> Implementacja: etapami, z pomiarem dekorelacji po każdej fazie (Prawo XVI).

### Legion X Equestris — M5/M15 mikro-scalp (priorytet: WYSOKI)

| KLUCZ | Nazwa | Opis | Status |
|-------|-------|------|--------|
| X-01 | EMA Cross | EMA(9/21) kierunek | 🔴 katalog |
| X-02 | StochRSI | Stochastic RSI ekstrema | ✅ kod (momentum.py, aktywny) |
| X-03 | CVD | Cumulative Volume Delta | 🔴 katalog (osobna wersja M5) |
| X-04 | VWAP Bounce | VWAP magnes dnia | 🔴 katalog |
| X-05 | OrderFlow | Bid/Ask Imbalance | 🔴 katalog |
| X-06 | ATR-Stop | ATR×1.5 dynamiczny stop | 🔴 katalog |
| X-07 | Williams %R | Szybkie ekstrema | 🔴 katalog |
| X-08 | Awesome Osc | Momentum 5 vs 34 SMA | ✅ kod (momentum.py, aktywny) |
| X-09 | Accelerator | Przyspieszenie momentum | 🔴 katalog |
| X-10 | HMA | Hull Moving Average | 🔴 katalog |
| X-11 | RVOL | Relative Volume | ✅ kod (wolumen.py, aktywny) |
| X-12 | BB Squeeze | Bollinger Squeeze M5 | 🔴 katalog |
| X-13 | Taker CVD | Spot Taker CVD | 🔴 katalog |
| X-14 | CVD Absorb | CVD Absorption | 🔴 katalog |
| X-15 | Net Volume | Net Volume / BoP | 🔴 katalog |
| X-16 | Volume Profile | POC/VAH/VAL M15 | 🔴 katalog |
| X-17 | TRIX | TRIX szybki | ✅ kod (momentum.py, aktywny) |
| X-18 | Donchian | Donchian Channel M15 | ✅ kod (trend.py, aktywny) |
| X-19 | BubbleFlow 🔱 | Bubble Flow Tron System | 🔴 katalog |
| X-20 | AIOrderFlow 🔱 | AI Probabilistic OrderFlow | 🔴 katalog |
| X-21 | FlowMatrix 🔱 | Flow Matrix Pro | 🔴 katalog |
| X-22 | BigTrades 🔱 | BigTrades Quant Analyzer | 🔴 katalog |
| X-23 | AetherVol 🔱 | AetherEdge Volume Surge | 🔴 katalog |
| X-24 | WicklessC 🔱 | xGhozt Wickless Candles | 🔴 katalog |

> X-25 i X-26 zaimplementowane powyżej (✅).

---

### Pozostałe legiony (248 neuronów) — pełen skatalogowany rejestr

> Szczegóły: `docs/KATALOG_NEURONOW.md`.
> Tu podsumowanie per legion. Rozwijać MANIFEST w miarę wdrożeń.

| Legion | Skatalogowane | Wdrożone | Do wdrożenia |
|--------|--------------|---------|--------------|
| X Equestris (M5/M15) | 26 | 7 (X-02,X-08,X-11,X-17,X-18,X-25,X-26) | 19 |
| III Augusta (H1) | ~45 | 11 (T-ADX..P-OIDIV..V-*..S-*) | ~34 |
| XII Fulminata (D1) | ~40 | 4 (O-MVRV..O-NETFLOW) | ~36 |
| Pozostałe legiony | ~188 | 10 (RSI,MACD,BB,EMACross,WR + WolumenAnomaly) | ~178 |
| **RAZEM** | **299** | **32** | **267** |

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
| **Do wdrożenia** | Faza 2 (X Equestris c.d.) | +19 neuronów | — | X-01,X-03..X-07,X-09,X-10,X-12..X-16,X-19..X-24 |

---

> 🔱 *"Katalog mówi: chcemy. Kod mówi: mamy. Nie mylimy tych dwóch słów nigdy."* — Prawo XIX
