# 🌏 SKAN AZJA — Perełki z 3100 Linków

> *"Etiam in luto gemma latet."* — Nawet w błocie kryje się klejnot.
>
> Głęboki skan pliku `archiwum/Azjatycki_skan_rynku_3100_links.md` (7106 linii, ~350+ wpisów).
> **NIE patrzyliśmy tylko na TOP 10.** Cztery legiony zwiadowców przeczesały każdą sekcję.
> Zasada symbiozy: tu trafiają TYLKO perełki dodające coś NOWEGO. Duplikaty odrzucone.

---

## ⚠️ UWAGA METODOLOGICZNA — Uczciwość Imperium

Część linków GitHub w źródle wygląda na **fabrykowane/ilustracyjne** (pojedynczy deweloper, brak realnego provenance, klucze typu "VIZ-###"). 

**Zasada:** Bierzemy **TECHNIKĘ**, nie ufamy ślepo URL-owi.
- ✅ **Potwierdzone realne kodbazy:** NautilusTrader, Reflexion, Outlines, CausalNex/DoWhy, LanceDB
- ⚠️ **Techniki realne, URL niepewny:** OFI-Rust, entropy-trading, upbit-shadow — implementujemy ideę od zera
- ❌ **Odrzucone:** komercyjne boty "$15 bonus", Discord/Telegram, eventy, modele-giganty bez metody

---

## 🧬 PEREŁKI → NOWE NEURONY (dodane do katalogu)

| Klucz | Neuron | Źródło (Azja) | Pieczęć | Co kradniemy |
|-------|--------|---------------|---------|--------------|
| HX-01 | Dynamic Hurst Exponent | IND-022 | ⚔️ IMV-INS | Wykładnik Hursta w czasie rzeczywistym: H>0.5 trend, H<0.5 mean-revert. Pamięć długoterminowa rynku (uzupełnia Higuchi ENT-08) |
| LG-01 | Liquidity Grab Detector | 3.122 | ⚔️ IMV-INS | Cena przebija equal highs/lows → zbiera płynność (stopy) → natychmiastowy odwrót. Stop-hunt jako sygnał |
| ZS-01 | Adaptive Z-Score Trigger | GAD-01/AgenticAITA | ⚔️ IMV-INS | Próg Z-score samokalibrujący się do reżimu zmienności (nie sztywne ±2σ) |
| KP-01 | Kimchi/P2P Premium | IND-002, 8.30 | ⚔️ IMV-INS | Spread cen Korea/global + premia P2P (VND/INR/PKR). Nie tylko arbitraż — miernik stresu (rośnie z $10 do $2000+ w panice) |
| CV-01 | Cross-Venue Volume Divergence | KVSI | ⚔️ IMV-INS | Różnica udziału wolumenu giełda regionalna vs globalna — leading indicator |
| HR-01 | Hashrate Divergence | 15.22 | ⚔️ IMV-INS | Zmiany hashrate/poboru mocy górników jako wyprzedzający sygnał BTC |
| IB-01 | Iceberg Detection | BD-10, 2.36 | ⚔️ IMV-INS | Wykrywa ukryte zlecenia iceberg po wzorcu odnawiania głębokości order book → Straż |
| ST-01 | Adaptive SuperTrend | 2.50 | 🔱 IMV-ADO | SuperTrend z adaptacyjnym ATR (dostraja się do zmienności) |
| KAL-01 | Kalman-Adaptive ATR | IND-025 | 🔱 IMV-ADO | Filtr Kalmana wygładza ATR → mniej fałszywych stopów (ulepszenie X-06) |
| IV-01 | APAC Implied Vol Regime | INS-001/FalconX | ⚔️ IMV-INS | Implied vol systematycznie SPADA w sesji azjatyckiej — neuron czasowo-zmiennościowy |
| AD-01 | Absorption-Distribution Index | IND-023 | ⚔️ IMV-INS | Kwantyfikuje absorpcję zleceń (wielki gracz "połyka" podaż) → sygnał wyczerpania |
| JP-01 | Japanese Retail Contrarian | 1.99 | ⚔️ IMV-INS | Indeks zachowań japońskich detalistów jako wskaźnik kontrariański |
| CAL-01 | Asian Calendar Seasonality | G.65 | ⚔️ IMV-INS | Lunar New Year + azjatyckie efekty kalendarzowe (uzupełnia PSY-06 Sezon) |

---

## 📖 PEREŁKI → NOWE STRATEGIE (dodane do katalogu)

| ID | Nazwa | Źródło | Pieczęć | Mechanika |
|----|-------|--------|---------|-----------|
| IMV-HY-007 | "PARADOKS PARRONDA" | BMD-08/STR-125 | 🏛️ IMV-ORI | Łączy DWIE przegrywające strategie (mean-rev + momentum) przez regułę przełączania → ensemble bije buy&hold. Formalizacja filozofii Kameleona |
| IMV-HY-008 | "GRA Z KOWALEM" | HYB-008 | ⚔️ IMV-INS | Teoria gier (tit-for-tat Axelroda) — modeluje market makera jako przeciwnika w iterowanej grze |
| VI-LV-005 | "KASKADA" | LEG-016 | ⚔️ IMV-INS | Poluje na kaskady likwidacji: funding + OI build-up + liquidation heatmap → wejście po overshoot |
| XII-RV-006 | "CYKL AMD" | SES-001..004 | ⚔️ IMV-INS | Accumulation-Manipulation-Distribution: instytucje akumulują, manipulują (stop-hunt), dystrybuują |
| IMV-MC-005 | "PREMIA STRACHU" | IND-002 | ⚔️ IMV-INS | Kimchi Premium jako miernik stresu rynkowego → kierunkowy sygnał sentymentu |

---

## 🏛️ PEREŁKI → ARCHITEKTURA (→ WIZJONER, nie psujemy działającego)

Te idee zmieniają RDZEŃ systemu — idą do Wizjonera na analizę przed wdrożeniem (Prawo VII — stopniowo).

| # | Perełka | Źródło | Status realności | Wpływ |
|---|---------|--------|------------------|-------|
| 🔴 | **Outlines — structured generation** | dottxt-ai/outlines | ✅ REALNE | Wymusza JSON/Pydantic na DeepSeek → ZERO halucynacji formatu. Krytyczne dla niezawodności Cesarza |
| 🔴 | **Reflexion — verbal self-reflection** | noahshinn/reflexion | ✅ REALNE | Agent pisze "post-mortem" każdej straty i wnioski wraca jako kontekst. Warstwa lekcji nad Pamięcią Absolutną |
| 🟠 | **TradingAgents — role-based debate** | TauricResearch | ✅ REALNE | Senat jako komitet ról: Analyst→Researcher→Trader→Risk Manager (debata zamiast płaskiego głosu) |
| 🟠 | **CVaR position sizing** | ZSZRUN Quore | technika | Sizing wg Conditional VaR zamiast zwykłego stop-loss → Kalkulator Lewara v2 |
| 🟠 | **Causal inference filter** | CausalNex/DoWhy | ✅ REALNE | Odróżnia PRAWDZIWE przyczyny od korelacji pozornych → filtr fałszywych sygnałów przed Cesarzem |
| 🟠 | **Strategy Guardian AI** | matteorigodanza | technika | Osobny proces "anioł stróż" monitoruje otwarte pozycje vs plan na żywo, interweniuje |
| 🟡 | **NautilusTrader — event-driven core** | nautechsystems | ✅ REALNE | Rust-core + Python control, multi-venue, zero-copy Arrow. Wzorzec egzekucji Faza 2 |
| 🟡 | **GEPA/CogAlpha — auto-generate neurony** | autoresearch/CogAlpha | technika | DeepSeek generuje kandydatów na neurony jako kod → backtest → zachowaj zwycięzców |
| 🟡 | **Fleet Risk Manager + capital allocator** | RISK-001/002 | technika | Ryzyko portfelowe: limity korelacji + realokacja kapitału do zwycięzców (sprzęgnij z Igrzyskami) |
| 🟡 | **Strategy Vector DB (embeddings)** | LanceDB | ✅ REALNE | Strategie jako embeddingi → semantyczne wyszukiwanie i dedup, dopasowanie do reżimu |
| 🟡 | **Data Drift Detector** | ANAL-001 | technika | Wykrywa shift rozkładu danych → trigger rekalibracji neuronów |
| 🟢 | **Multi-timeframe consensus** | MTPredictor 2.49 | technika | Jeden model nad 5 interwałami, sygnał = konsensus między skalami → upgrade Legatusa |

> Monte Carlo stress-testing (6.71) — **JUŻ MAMY** w Valhalli (`monte_carlo()`). ✅

---

## 🧘 PEREŁKI → PSYCHOLOGIA / RYZYKO

| Perełka | Źródło | Wdrożenie |
|---------|--------|-----------|
| **Reguła 30% max straty** ("nigdy nie kochaj pozycji") | AOA #13 | Hard circuit-breaker w Kalkulatorze Lewara — przerwij wszystko przy 30% obsunięcia kapitału |
| **Collective Sentiment z Weibo/Douyin/KakaoTalk** | 3.69, 2.95 | Źródło danych dla Oczu (azjatyckie media społ. — kontrariański ekstremów) |
| **Cross-cultural emoji sentiment** | PAP-010 | Emoji jako kompaktowe, językowo-niezależne cechy sentymentu (NLP neuron) |

---

## 📊 STATYSTYKA SKANU

| Kategoria | Znalezione | Dodane | Odrzucone (duplikat/marketing) |
|-----------|-----------|--------|-------------------------------|
| Nowe neurony | ~25 kandydatów | **13** | ~12 (już mamy OFI, CVD, FOMO, kapitulację, entropy) |
| Nowe strategie | ~10 kandydatów | **5** | ~5 |
| Architektura | ~16 idei | → WIZJONER (12) | Monte Carlo (już mamy) |
| Psychologia/ryzyko | ~6 | 3 | reszta = duplikaty PSY-01..06 |

> **Skan przeczesał WSZYSTKIE 7106 linii.** Cztery zakresy, czterech zwiadowców.
> Najcenniejsze do wdrożenia NAJPIERW: **Outlines** (niezawodność DeepSeek), **Paradoks Parronda**, **Dynamic Hurst**, **Liquidity Grab**, **Causal inference filter**.

---

*"Zwiadowca nie wraca z pustymi rękami, jeśli umie patrzeć." — VITRUVIUSZ*

*— SKAN_AZJA.md | v1.0 | 2026-06-01*
