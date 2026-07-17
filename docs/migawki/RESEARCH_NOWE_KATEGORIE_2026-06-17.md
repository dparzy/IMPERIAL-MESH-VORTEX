---
kategoria: ACTA
typ: acta
wlasciciel: imperium/legiony/meta_labeling.py, imperium/legiony/neurony/przekroj.py, imperium/legiony/neutralizacja.py
stan_na: 2026-06-17
powod_istnienia: "Głęboki research 6-kątowy (APAC, konkursy quant, repozytoria, prace naukowe, patenty, książki) mający zidentyfikować nowe kategorie sygnałów zdekorelowane z istniejącymi 72 neurona"
---
# 🔬 DEEP RESEARCH — Nowe kategorie i sygnały (2026-06-17)

> **STATUS: RESEARCH / PLAN — NIE KOD.** Prawo XIX: nic nie „istnieje" bez kodu+testów.
> Ten dokument to **rejestr kandydatów** z głębokiego skanu (6 kątów: APAC, konkursy
> quant, repozytoria, prace naukowe, patenty, książki). Każdy wpis: źródło + status
> weryfikacji + mapowanie do naszych 13 kategorii + wymagane dane.
>
> ⚠️ **Uczciwość weryfikacji (Prawo I):** środowisko badawcze miało zablokowany
> fetch (HTTP 403 na arxiv/SSRN/Google Patents/Kaggle). Tytuły/ID/autorzy potwierdzone
> przez wyniki wyszukiwania, ale **pełne teksty NIE były czytane**. Każde arXiv ID i numer
> patentu należy potwierdzić przed wpisaniem do REJESTR_INSPIRACJI.md jako ✅.

---

## 🧭 PUNKT WYJŚCIA — co już mamy

72 neurony, 13 kategorii: **M**(Momentum) **T**(Trend) **F**(Flow/Volume)
**R**(Regime/Sentiment) **Z**(Threat/likwidacje) **S**(Structure/SMC) **O**(On-chain)
**A**(Anti-manip) **L**(Leverage) **V**(Volatility) **H**(Hurst/fraktale)
**N**(Entropy/info) **D**(Geometry/signatures).

Już zaimplementowane techniki bliskie tematom researchu (NIE dublujemy):
VPIN, Hurst/DFA, permutation entropy, Yang-Zhang vol, path signatures (Levy area),
Amihud, Pi-Cycle, Kimchi/P2P premium, Asian-session implied vol, Japanese retail
contrarian, Lunar New Year, cross-venue volume divergence, triple-barrier (idea).

---

## 🚨 NAJWAŻNIEJSZE ODKRYCIE — luki strukturalne (zbieżność wszystkich 6 kątów)

Trzy luki pojawiły się **niezależnie w wielu źródłach** — to nie pojedyncze neurony,
to **całe brakujące osie informacji**:

### LUKA 1 — Brak warstwy PRZEKROJOWEJ (cross-sectional / panel)
Wszystkie 72 neurony to **szeregi czasowe pojedynczego aktywa**. Nie mamy ani jednego
sygnału „relative strength" — siła ETH względem koszyka, ranking momentum przekrojowo.
Skoro handlujemy 5+ par, to **strukturalnie zdekorelowana, darmowa informacja** (OHLCV).
- Źródła: Trend Factor cross-section (JFQA 2024, S0022109024000747); Cross-sectional
  interactions (IRFA 2025, S1057521924007415); TS+CS momentum (Han/Kang/Ryu 2024).
- **Propozycja: NOWA KATEGORIA `C` = Cross-sectional / Relative Strength.**

### LUKA 2 — Brak warstwy META (bet-sizing / pewność / dekorelacja)
Mamy głosowanie kierunkowe, ale nic co mierzy „czy nasz zagregowany głos ma rację"
i ile postawić. To meta-warstwa NAD rojem, nie 73. neuron.
- **Meta-labeling** (López de Prado AFML Ch3): wtórny model przewiduje czy sygnał
  pierwotny jest trafny → rozmiar pozycji ∈ [0,1]. OHLCV. Zbieżne: konkursy + książki.
- **Neutralizacja/dekorelacja** (Numerai FNC): regresja każdego sygnału na resztę,
  zostaw residuum → gwarantuje wkład tylko ortogonalnej części. **Wprost realizuje
  Prawo XVI.** Mnoży wartość wszystkich 72.
- **MP-denoising** (López de Prado MLAM Ch2): Marčenko-Pastur czyści macierz korelacji
  do sizingu wieloskładnikowego.
- **Propozycja: NOWA KATEGORIA `B` = Bet-sizing / Meta / Pewność** (warstwa nad Legatusem).

### LUKA 3 — Brak MIKROSTRUKTURY z księgi zleceń (L2)
Najmocniejsza zdekorelowana przewaga w mikrostrukturze (OFI, book imbalance, WAP,
hidden-liquidity, Hawkes-on-LOB) **wymaga feedu L2 depth** — którego dziś NIE pobieramy.
MEXC udostępnia depth przez websocket. To koszt danych, ale otwiera całą oś.
- **Propozycja: NOWA KATEGORIA `U` = Microstructure / Liquidity-state** (gdy wepniemy L2).

---

## 📊 KANDYDACI WG KOSZTU DANYCH

### 🟢 TIER 1 — tylko OHLCV (budujemy najtaniej, zero nowego feedu)

| Kand. | Technika | Kat. | Źródło | Dlaczego zdekorelowane |
|-------|----------|------|--------|------------------------|
| C-01 | Cross-sectional relative strength / ranking momentum | **C (nowa)** | JFQA 2024 S0022109024000747 ⚠️ | panel vs szereg — ortogonalne do każdego sygnału pojedynczego aktywa |
| B-01 | Meta-labeling (triple-barrier + wtórny model) | **B (nowa)** | AFML Ch3 ✅(rozdz.) | mierzy trafność zagregowanego głosu, nie kierunek |
| B-02 | Feature neutralization (Prawo XVI w kodzie) | **B (nowa)** | Numerai FNC ⚠️ | usuwa skorelowaną część każdego sygnału |
| R-new1 | Statistical Jump Model (regime, mniej whipsaw niż HMM) | R | arXiv 2402.05272 ✅(ID) | klasyfikator reżimu z karą za skok — inny estymator niż nasze H/N |
| R-new2 | SADF/CUSUM — test eksplozywności (bańka) | R/Z | AFML Ch17 ✅(rozdz.) | charakter procesu (mean-rev→eksplozja), nie kierunek |
| R-new3 | BOCPD — Bayesian online change-point (run-length posterior) | R | Adams&MacKay 2007 ✅ | per-bar prawdopodobieństwo zmiany rozkładu — przyczynowe |
| N-new1 | Fractional differentiation (stacjonarność + pamięć) | N/H | AFML Ch5 ✅(rozdz.) | zachowuje długą pamięć, którą zwykłe zwroty niszczą |
| F-new1 | Information-driven bars (volume/dollar/imbalance bars) | F | AFML (zegar wolumenowy) ✅ | próbkowanie po wolumenie, nie czasie — inna oś |
| V-new1 | Session vol term-structure + "Monday Asia open" | V | RQFA 2024 s11156-024-01304-1 ⚠️ | sezonowość pory dnia/tygodnia, ortogonalna do poziomu ceny |
| Z-new1 | Peg-sensitive stablecoin stress (7 wskaźników, half-life pega) | Z/V | SSRN 5772240 ⚠️ | mikro-mechanika pega aktywa kwotującego, nie trend |

### 🟡 TIER 2 — jeden DARMOWY dodatkowy feed

| Kand. | Technika | Kat. | Feed | Źródło |
|-------|----------|------|------|--------|
| R-new4 | KVSI — Korean Venue Share (udział wolumenu Upbit vs global) | R/F | Upbit public API (vol) | MDPI Systems 14(1):111 ⚠️ |
| O-new1 | Stablecoin FX-basis (USDT/CNY,VND,INR vs FX oficjalny) | O / Macro | OTC/P2P quotes | BIS WP 1340 ⚠️ |
| IV-01 | DVOL term-structure slope (skew opcyjny, Asian-hours) | **IV (nowa)** | Deribit DVOL (darmowe API) | ORL 2024 S0167637724000713 ✅; Deribit spec |
| Z-new2 | Stablecoin tail-spillover (QVAR network anchors/amplifiers) | Z | multi-stablecoin tickers | arXiv 2602.18820 ⚠️ |

### 🔴 TIER 3 — wymaga feedu L2 order-book (MEXC depth websocket)

| Kand. | Technika | Kat. | Źródło |
|-------|----------|------|--------|
| U-01 | Order-Flow Imbalance (OFI, signed queue changes) | **U (nowa)** | hftbacktest (4.2k★) ✅; Cont et al. |
| U-02 | Liquidity imbalance / market urgency / price pressure | U/F | Optiver Trading-at-Close (repo) ✅ |
| U-03 | WAP + realized-vol mikrostrukturalne (Optiver RV) | U/V | Optiver RV repo michaelpoluektov/orvp ✅ |
| U-04 | Hidden-liquidity estimator (iceberg/reserve) | U/S | patent US8140416B2 ✅ (⚠️ JPMorgan — tylko KONCEPT) |
| P-01 | Hawkes self-excitation (trade-arrival clustering) | **P (nowa)** | `tick` lib X-DataInitiative (547★) ✅ |

### ⚫ TIER 4 — feed on-chain
| Kand. | Technika | Kat. | Źródło |
|-------|----------|------|--------|
| Z-new3 | Cross-protocol liquidation Hawkes (branching ratio) | Z/O | SSRN 6508318 ✅(ID) |
| O-new2 | APAC grassroots adoption flow (India/Vietnam) | O/R | Chainalysis 2025 ⚠️ (komercyjne — użyć darmowego substytutu) |

---

## 🛡️ ANTI-MANIPULACJA — patenty (filtry chroniące kategorię F)
Wszystkie jako **KONCEPT** (nie kopiujemy roszczeń); status własności sprawdzić.
- **US20040024691A1** (ABANDONED — wolne): wash-trade / round-robin detection → kat. **A**.
- **US20150081505A1** (CME): fuzja order-flow + social-media anomaly → **A+R**.
- **US20090157451A1** (GE): collusion linked-account → **A**.
- US20140149273A1 (ABANDONED — wolne): synchronizowany microstructure feature appliance → **U**.

---

## 🎯 REKOMENDACJA KOLEJNOŚCI (Prawo I — każdy przez A/B)

1. **B-02 Neutralization** — najwyższa dźwignia: realizuje Prawo XVI, mnoży wartość 72
   neuronów, OHLCV-only, operuje na naszych własnych sygnałach. Buduj pierwsze.
2. **C-01 Cross-sectional RS** — nowa oś informacji, darmowa (handlujemy koszyk).
3. **B-01 Meta-labeling** — warstwa sizingu pewności nad Legatusem.
4. **R-new1 Jump Model + R-new3 BOCPD** — twardszy detektor reżimu (mniej whipsaw).
5. **Tier-2 feedy** (DVOL, KVSI) — gdy Tier-1 zmierzone.
6. **Tier-3 L2** — decyzja kierunkowa: czy wpinamy MEXC depth websocket (otwiera kat. U/P).

**Każdy kandydat:** kod+test+A/B (ON vs OFF) → tylko jeśli delta>0 wchodzi (Prawo I/XVI).
Pełne opisy wg ZPO (rozwinięcia skrótów, link, status) przy wdrażaniu → REJESTR_INSPIRACJI.md.

---

## 🧰 DODATEK — narzędzia META i WALIDACJI (ulepszają to, co mamy)

Nie są to neurony — to infrastruktura, która podnosi jakość całego roju. Kilka wprost
realizuje nasze Prawa (XVI redundancja, XXI spójność/brak fałszywej przewagi):

| Kand. | Narzędzie | Rola | Źródło | Po co |
|-------|-----------|------|--------|-------|
| META-01 | **Variation-of-Information + Clustered Feature Importance** | upgrade `diagnostyka_korelacji` | MLAM; SSRN 3517595 ✅ | VI łapie **nieliniową** redundancję, którą Pearson \|ρ\|>0.80 PRZEGAPIA. Bezpośrednie wzmocnienie Prawa XVI |
| META-02 | **PBO/CSCV + Deflated Sharpe Ratio** | strażnik przeuczenia | AFML Ch11-12 ✅ | P(backtest przeuczony) + Sharpe zdyskontowany liczbą prób. Realizuje Prawo XXI (zero fabrykowanej przewagi). Wdrożyć PRZED meta-labelingiem |
| META-03 | **HRP (Hierarchical Risk Parity)** | alokacja wag WAGI_REZIMU | AFML Ch16; SSRN 2708678 ✅ | wagi z klastrowania drzewiastego, działa na osobliwej macierzy (nasze neurony są mocno skorelowane) |
| META-04 | **Sequential Bootstrap (uniqueness weighting)** | utility treningu | AFML Ch4 ✅ | koryguje autokorelację nakładających się etykiet — warunek uczciwego meta-labelingu |
| L-new1 | **Kyle's Lambda** (impact per signed flow) | nowy wymiar płynności | Harris; Cartea; Easley (Cornell) ✅ | λ = nachylenie Δcena~signed-volume. Płynność/elastyczność, NIE kierunek; różny facet niż VPIN (toxyczność) i Amihud (unsigned) |
| I-01 | **Almgren-Chriss + square-root impact law** | warstwa egzekucji | Almgren&Chriss 1999; Bouchaud ✅ | harmonogram cięcia zlecenia (most realny $50!), ortogonalny do sygnałów kierunkowych |
| A-new1 | **Covariance-inflection kill-switch** (KONCEPT) | alarm kaskady | patent EP3243183A1 ⚠️ Morgan Stanley — ENCUMBERED, tylko idea | inflekcja kowariancji flow vs realne fille → auto-halt; wczesny sygnał vs nasze Z |

**Uwaga (META-01/02):** to najtańsze i najbezpieczniejsze ulepszenia — operują na naszych
własnych danych, zero nowego feedu, i bezpośrednio wzmacniają governance (Prawo XVI/XXI).
Dobry kandydat „pierwszy ruch" obok B-02 Neutralization.

*Stan na: 2026-06-17 | Źródło: deep research 6-kątowy (APAC/konkursy/repo/papers/patenty/książki) | Status: RESEARCH, nie kod (Prawo XIX)*
