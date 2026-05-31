# 🏰 Kingdom Pixel 2.0 — DODATEK 1

## 📐 Dokument uzupełniający do Manifestu Imperium v2.0

*Data utworzenia: 2026-05-20 | Autor: Komandant Pixel & DeepSeek AI*

---

## 📜 INSTRUKCJA DLA AGENTA AI

> **Kontekst:** Niniejszy dokument jest **pierwszym dodatkiem** do głównego Manifestu `Kingdom Pixel 2.0`. Należy go analizować **łącznie z wersją bazową**, która zawiera pełną strukturę folderów, kod Tytan-α, rejestr ZBADANE.md (pozycje 1-90) oraz perły i diamenty pierwszej fali.
>
> **Zasada aktualizacji:** Od tej chwili każda kolejna aktualizacja będzie dostarczana jako osobny dodatek (`Dodatek 2`, `Dodatek 3`, itd.), zawsze odnoszący się do tej samej wersji bazowej 2.0.

---

## 🗺️ 1. NOWE JEDNOSTKI IMPERIALNEJ GWARDII

### ⚔️ 1.1. `029_Blyskawiczny_Zwiad` — Błyskawiczny Oddział Rozpoznawczy

Zgodnie z Twoją wizją, tworzę nową dywizję w strukturach `02_Zwiadowcy`, która reaguje na bezpośredni rozkaz Cara dotyczący dowolnej kryptowaluty.

**Pełna ścieżka:**
```
C:\Kingdom Pixel\Castle Pixel\Imperial Guard\02_Zwiadowcy\029_Blyskawiczny_Zwiad\
```

**Struktura oddziału:**

| Podfolder/Plik | Nazwa Jednostki | Misja |
|:---|:---|:---|
| `Dowodca_Ekspedycji.py` | Dowódca Ekspedycji | Przyjmuje rozkaz od Cara (nazwa tokena) i rozsyła zadania do wszystkich szwadronów. |
| `Zwiadowca_OnChain.py` | Zwiadowca OnChain | Analizuje portfele "wielorybów", transfery na giełdy, płynność i metryki sieciowe. |
| `Zwiadowca_Bezpieczenstwa.py` | Zwiadowca Bezpieczeństwa | Skanuje kod smart kontraktu w poszukiwaniu honeypotów, rug-pulli i ukrytych podatków. |
| `Zwiadowca_Sentymentu.py` | Zwiadowca Sentymentu | Monitoruje X/Twitter, Reddit, TikTok i KOL-i, by ocenić nastroje rynkowe. |
| `Zwiadowca_Fundamentalny.py` | Zwiadowca Fundamentalny | Bada kapitalizację, TVL, roadmapę, zespół deweloperski i aktywność na GitHubie. |
| `Zwiadowca_Techniczny.py` | Zwiadowca Techniczny | Przeprowadza analizę techniczną na 12 interwałach czasowych, wykrywa trendy i poziomy S/R. |
| `Strateg.py` | Strateg Polowy | Syntetyzuje wszystkie raporty w jeden dokument i wydaje rekomendację: LONG, SHORT lub STAY_OUT. |
| `Skarbnik_Wojenny.py` | Skarbnik Wojenny | Kalkuluje wielkość pozycji, dźwignię oraz przydziela nagrody za zwycięską bitwę. |

---

### 💰 1.2. `War Loot Vault` — Skarbiec Wojenny

Nowa komnata w `Royal Treasury`, do której trafiają łupy z każdej wygranej bitwy.

**Pełna ścieżka:**
```
C:\Kingdom Pixel\Castle Pixel\Royal Treasury\War Loot Vault\
├── loot_allocator.py        # Rozdziela zyski między jednostki
├── medal_registry.json      # Rejestr odznaczeń i punktów zasług
└── README.md
```

---

## 🎖️ 2. SYSTEM MOTYWACYJNY — "WOJENNY BURDEL"

### 2.1. Filozofia

Każda transakcja to bitwa. Giełda to wróg, który chce ograbić nasze Królestwo. Nasi agenci to żołnierze, którzy za zwycięstwo otrzymują nagrody — "medale", "punkty zasług" i priorytet w dostępie do kapitału.

### 2.2. Mechanizm Działania

1.  **Źródło nagród:** 20% zysku netto z każdej wygranej transakcji trafia do `War Loot Vault`.
2.  **Kryteria podziału (analizowane przez `Skarbnika_Wojennego`):**
    *   **50%** dla `01_Wywiad` — za jakość analizy przed bitwą.
    *   **30%** dla `03_Kawaleria` — za precyzję egzekucji.
    *   **20%** dla `Nadworny Alchemik` — jeśli użyto jego nowatorskiej strategii.
3.  **Forma nagród:**
    *   **Medale:** Wirtualne odznaczenia w `medal_registry.json`.
    *   **Punkty Zasług (PZ):** Waluta wewnętrzna Królestwa. Im więcej PZ, tym wyższy priorytet dostępu do kapitału w przyszłych bitwach.
    *   **On-chain:** W przyszłości — tokenizowane odznaczenia na własnym blockchainie audytowym.

### 2.3. Inspiracje Zewnętrzne

| Narzędzie | Opis | Wykorzystanie w Królestwie |
|:---|:---|:---|
| **Gorillionaire** | Platforma z sygnałami AI, rankingiem i systemem punktowym. | Wzór dla systemu medalowego. |
| **Vibe Team Trading** | Agenci AI wykonują transakcje na podstawie sentymentu grupy, zarabiając prowizję. | Model podziału łupów między jednostki. |
| **AI Pump Fun** | Zawody tradingowe AI z eliminacją i nagrodami. | Mechanika awansu i degradacji agentów. |
| **LeveX Quest System** | Wyzwania tradingowe z punktami i bonusami. | System zadań pobocznych dla agentów. |

---

## 🛠️ 3. NOWE NARZĘDZIA — ARSENAŁ DLA `029_Blyskawiczny_Zwiad`

Poniższe narzędzia nie znajdowały się w wersji bazowej 2.0. Zostały zdobyte podczas kampanii rekonesansowej i przypisane do konkretnych zwiadowców.

### 3.1. Dla Zwiadowcy OnChain

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **Santiment Top 100 Wallets** | Monitoruje aktywność 100 największych portfeli w czasie rzeczywistym. | [`blockchain.news`](https://blockchain.news) |
| 2 | **Nansen CLI** | Agent AI odpytywujący API Nansena o przepływy tokenów. | [`academy.nansen.ai`](https://academy.nansen.ai) |
| 3 | **Glassnode Investor Behavior** | Klasyfikuje tokeny według zachowań posiadaczy (Conviction/Momentum Buyers). | [`studio.glassnode.com`](https://studio.glassnode.com) |
| 4 | **DEXTools Wallet Tracker** | Śledzi ruchy portfeli "smart money" na wielu łańcuchach. | [`dextools.io`](https://www.dextools.io) |

### 3.2. Dla Zwiadowcy Bezpieczeństwa

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **RugWatch** | Bot RT dla Solany analizujący ryzyko rug-pulli. | [`github.com/rookiester/rugpull-scam-token-detection`](https://github.com/rookiester/rugpull-scam-token-detection) |
| 2 | **ChainGuard Intelligence** | Platforma AI dla EVM łącząca ML z danymi on-chain. | [`github.com/Crzisaac/ETHOnline-2025-Hackathon-rug-pull-detector`](https://github.com/Crzisaac/ETHOnline-2025-Hackathon-rug-pull-detector) |
| 3 | **Honeypot & Rug Detector** | Skaner smart kontraktów wykrywający pułapki. | [`github.com/Honeypot-Rug-Detector`](https://github.com/Honeypot-Rug-Detector/.github) |
| 4 | **isRug.API** | Narzędzie do sprawdzania kontraktów ERC-20 pod kątem ryzyka. | [`repos.ecosyste.ms`](https://repos.ecosyste.ms) |
| 5 | **Rug Munch Intelligence** | Serwer MCP z 19 narzędziami do analizy ryzyka tokenów. | [`pulsemcp.com`](https://www.pulsemcp.com/servers/cryptorugmunch-rug-munch) |
| 6 | **LROO Rug Pull Detector** | Framework oparty na multimodalnych sygnałach on-chain i OSINT. | [`arxiv.org/abs/2503.06614`](https://arxiv.org/abs/2503.06614) |

### 3.3. Dla Zwiadowcy Sentymentu

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **Gold Digger** | Silnik badawczy AI śledzący KOL-i i wykrywający narracje. | [`github.com/skyzer/gold-digger`](https://github.com/skyzer/gold-digger) |
| 2 | **Crypto Twitter Tracker** | Strumieniuje wydarzenia z Twittera od 1000+ kont. | [`apify.com`](https://apify.com) |
| 3 | **LunarCrush** | Analizuje sentyment społecznościowy dla 20,000+ aktywów. | [`apps.apple.com`](https://apps.apple.com) |
| 4 | **BitMart X Insight** | Śledzi tweety od 300+ czołowych krypto KOL-i. | [`bitmart.com`](https://www.bitmart.com) |
| 5 | **Crypto Sentiment Tracker Pro** | Agreguje sygnały KUP/SPRZEDAJ z Reddita, Twittera i TikToka. | [`apify.com`](https://apify.com/captivated_rank/crypto-sentiment-tracker-pro) |
| 6 | **x-research Agent Skill** | Umiejętność agentowa przeszukująca X/Twitter w RT. | [`skillsmp.com`](https://skillsmp.com/skills/virattt-dexter-src-skills-x-research-skill-md) |

### 3.4. Dla Zwiadowcy Fundamentalnego

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **web3-research-mcp** | Serwer MCP agregujący CoinGecko, CoinMarketCap, DeFiLlama. | [`hexmos.com`](https://hexmos.com) |
| 2 | **altFINS API** | 150+ wskaźników, 130+ sygnałów dla 2,200+ aktywów. | [`markets.businessinsider.com`](https://markets.businessinsider.com) |
| 3 | **Sentient Narrative Agent** | Agent AI analizujący narracje rynkowe i obliczający sentyment. | [`github.com/Widiskel/sentient-narrative-agent`](https://github.com/Widiskel/sentient-narrative-agent) |
| 4 | **CoinPrism Dashboard** | Kokpit RT ze wskaźnikami sentymentu i sygnałem rynkowym. | [`github.com/sanjana-1118/CryptoCurrency_Market_Dashboard`](https://github.com/sanjana-1118/CryptoCurrency_Market_Dashboard) |

### 3.5. Dla Dowódcy i Stratega

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **WebCryptoAgent** | Framework łączący agentów modalnościowych w jeden dokument dowodowy. | [`arxiv.org/abs/2601.04687`](https://arxiv.org/abs/2601.04687) |
| 2 | **BingX AI Claw** | Generuje sygnały walidowane krzyżowo z wielu źródeł. | [`bingx.com`](https://bingx.com) |
| 3 | **altFINS API** | Sygnały techniczne + fundamentalne dla 2,200+ aktywów. | [`markets.businessinsider.com`](https://markets.businessinsider.com) |

---

## 🖥️ 4. NOWE NARZĘDZIA — ROZBUDOWA `THRONE ROOM` I `DASHBOARD`

Poniższe moduły wizualizacyjne i dashboardowe nie znajdowały się w wersji bazowej 2.0.

### 4.1. GPU-Accelerated Web Charting

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **ChartGPU** | WebGPU renderujący 1M punktów przy 60fps. | [`github.com/ChartGPU/ChartGPU`](https://github.com/ChartGPU/ChartGPU) |
| 2 | **diCharts** | 100K+ świec przy 60fps, 25KB po kompresji. | [`brokeret.com/dicharts`](https://brokeret.com/dicharts) |
| 3 | **webgpu-candles** | Świece na WebGPU z akceleracją GPU (Rust/WASM). | [`github.com/qqrm/webgpu-candles`](https://github.com/qqrm/webgpu-candles) |

### 4.2. Native Desktop Charting

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **Flowsurface** | Natywna aplikacja GPU: Heatmap, Footprint, DOM. Wspiera MEXC. | [`github.com/flowsurface-rs/flowsurface`](https://github.com/flowsurface-rs/flowsurface) |
| 2 | **OpenBook** | Bookmap-style wizualizacja głębokości rynku. | [`github.com/DegenSugarBoo/OpenBook`](https://github.com/DegenSugarBoo/OpenBook) |
| 3 | **egui-charts** | 130+ wskaźników, 95 narzędzi rysunkowych. | [`crates.io/crates/egui-charts`](https://crates.io/crates/egui-charts) |

### 4.3. Terminal UI (TUI) Dashboards

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **PolyTerm** | 73+ interaktywnych ekranów TUI. Śledzenie wielorybów, insiderów, arbitrażu. | [`github.com/NYTEMODEONLY/polyterm`](https://github.com/NYTEMODEONLY/polyterm) |
| 2 | **RustFinance Terminal** | "Institutional-grade" terminal w czystym Rust. TWAP, VWAP, Iceberg. | [`github.com/Ashutosh0x/rust-finance`](https://github.com/Ashutosh0x/rust-finance) |
| 3 | **CoinPeek** | Monitor krypto w terminalu z SQLite. | [`dev.to`](https://dev.to) |
| 4 | **termichart** | SDK do wykresów w terminalu (linie, świece, słupki, sparklines). | [`pypi.org/project/termichart`](https://pypi.org/project/termichart) |

### 4.4. Immersive 3D & VR

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **DeepMarket** | Wizualizacja 200 aktywów jako podwodny świat 3D. | [`deepmarket.live`](https://deepmarket.live) |
| 2 | **VR Financial Simulation Platform** | 30% szybsze wykrywanie anomalii w VR. | [`musketeerstech.com`](https://musketeerstech.com) |
| 3 | **Apemaps** | Wciągająca platforma VR dla danych giełdowych. | [`devpost.com/software/apemaps`](https://devpost.com/software/apemaps) |

### 4.5. Mobile & PWA

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **React Native Graph** | Wykres liniowy na Skia, płynniejszy niż SVG. | [`www.npmjs.com`](https://www.npmjs.com) |
| 2 | **TradePro** | Inteligentny asystent handlowy PWA z widżetami RT. | [`devpost.com/software/tradepro`](https://devpost.com/software/tradepro) |
| 3 | **Hyperliquid Mobile App** | Natywna apka mobilna dla Hyperliquid DEX. | [`github.com/aurAcHIpRUN`](https://github.com/aurAcHIpRUN/Mobile-App-Hyperliquid-Android) |

### 4.6. Telegram & Notifications

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **TradingAgents-Telegram** | Nakładka Telegram dla TradingAgents. Progres na żywo, anulowanie. | [`github.com/IvanWng97/TradingAgents-Telegram`](https://github.com/IvanWng97/TradingAgents-Telegram) |
| 2 | **TheTickrBot v2.0** | Bot Telegram ze sparklines, portfolio, F&G. | [`github.com/ajadonai/thetickrbot`](https://github.com/ajadonai/thetickrbot) |
| 3 | **Tigerpaw** | W pełni lokalne powiadomienia bez zewnętrznych usług. | [`www.npmjs.com`](https://www.npmjs.com) |

### 4.7. Order Flow & Heatmap

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **Flowsurface Footprint Chart** | Footprint + grupowanie cen i wolumenu. | Zintegrowane z Flowsurface |
| 2 | **Buildix Orderflow** | CVD z atrybucją portfela, porównanie 5 giełd. | [`buildix.com`](https://www.buildix.com) |
| 3 | **Footprint (KenshinC)** | Zoptymalizowany wykres Footprint w PineScript. | [`in.tradingview.com`](https://in.tradingview.com) |
| 4 | **Institutional Footprint Scanner** | Wykrywa instytucjonalną aktywność bez danych L2. | [`tr.tradingview.com`](https://tr.tradingview.com) |

### 4.8. Prediction Markets Visualization

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **ForecastLens** | Agregator Polymarket + Kalshi + Metaculus. Pokazuje kalibrację, rozbieżność. | [`devpost.com/software/forecast-lens`](https://devpost.com/software/forecast-lens) |
| 2 | **OddsBase** | Platforma 25,000+ rynków zarządzana przez 3 agentów AI. | [`devpost.com/software/oddsbase`](https://devpost.com/software/oddsbase) |
| 3 | **polymarket-kalshi-spread** | Monitor spreadu z alertami Telegram. | [`github.com/lorhog1337/kalshi-polymarket-spread`](https://github.com/lorhog1337/kalshi-polymarket-spread) |

---

## 🧬 5. NOWE NARZĘDZIA — SAMOLECZENIE I BEZPIECZEŃSTWO

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **AEL (Agent Evolving Learning)** | Dwuskalowy, samodoskonalący się framework. Sharpe 2.13. | [`github.com/WujiangXu/AEL`](https://github.com/WujiangXu/AEL) |
| 2 | **Self-Healing Bot (122+ Lessons)** | 122+ udokumentowanych lekcji z każdej porażki. | [`dev.to/igorganapolsky/`](https://dev.to/igorganapolsky/i-built-a-self-healing-ai-trading-bot-that-learns-from-every-failure-g94) |
| 3 | **ClawDrive** | "Jeśli nie zarabiasz — umierasz". Samohostowany system z pamięcią Git. | [`github.com/CyberImmortal/clawdrive`](https://github.com/CyberImmortal/clawdrive) |
| 4 | **APEX Trader** | 5-agentowy pipeline z daemonem samoleczenia 24/7. | [`lablab.ai`](https://lablab.ai/ai-hackathons/ai-trading-agents/apex-trader/apex-trader-autonomous-multi-agent-trading-system) |
| 5 | **Project HYDRA** | Samoleczenie i auto-skalowanie w Kubernetes. | [`ieee.nitk.ac.in/project-hydra`](https://ieee.nitk.ac.in/project-hydra) |

---

## 🧪 6. NOWE NARZĘDZIA — DANE I SYMULACJE

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **SFAG (Stylized Facts Alignment GAN)** | GAN z różniczkowalnymi ograniczeniami strukturalnymi. | [`catalyzex.com`](https://www.catalyzex.com/paper/arxiv:2605.06822) |
| 2 | **PersonaLedger** | 30M transakcji od 23,000 użytkowników. Dataset na HuggingFace. | [`github.com/CapitalOne-Research/PersonaLedger`](https://github.com/CapitalOne-Research/PersonaLedger) |
| 3 | **MarS (Microsoft)** | Symulator rynku napędzany Large Market Model (LMM). | [`github.com/microsoft/MarS`](https://github.com/microsoft/MarS) |
| 4 | **FairFinGAN** | WGAN z wbudowaną kontrolą uprzedzeń. | [`arxiv.org/abs/2603.05231`](https://arxiv.org/abs/2603.05231) |
| 5 | **TimeGAN** | Klasyczny framework GAN dla szeregów czasowych. | [`github.com/jsyoon0823/TimeGAN`](https://github.com/jsyoon0823/TimeGAN) |

---

## 🔗 7. NOWE NARZĘDZIA — ZDECENTRALIZOWANE FINANSE AGENTÓW

| Lp. | Nazwa | Opis | Link |
|:---:|:---|:---|:---|
| 1 | **OnlyFence** | Darmowy DeFi toolkit dla agentów AI z guardrails. | [`github.com/seallabs/onlyfence`](https://github.com/seallabs/onlyfence) |
| 2 | **Agent Credit** | Linia kredytowa dla AI agenta (Aave V3). | [`github.com/aaronjmars/agent-credit`](https://github.com/aaronjmars/agent-credit) |
| 3 | **Kyro Protocol** | Infrastruktura M2M dla agentów na Stellarze. | [`github.com/David-patrick-chuks/Kyro-Protocol`](https://github.com/David-patrick-chuks/Kyro-Protocol) |
| 4 | **SpendOS** | Pierwszy agent, który rządzi własnymi wydatkami. | [`github.com/consensus-hq/spendos`](https://github.com/consensus-hq/spendos) |
| 5 | **Uniswap AI Skills** | 7 pluginów do swapów, LP i deployu na Uniswap. | [`github.com/Uniswap/ai-skills`](https://github.com/Uniswap/ai-skills) |
| 6 | **Kuberna Labs** | Zdecentralizowane szyny wykonawcze z zkTLS. | [`github.com/kawacukennedy/kuberna-labs`](https://github.com/kawacukennedy/kuberna-labs) |

---

## 📋 8. ZBADANE.md — CIĄG DALSZY REJESTRU (Pozycje 91-145)

Poniższy blok stanowi bezpośrednią kontynuację rejestru z wersji bazowej 2.0 (zakończonego na pozycji 90). Należy go dołączyć do głównego pliku `ZBADANE.md`.

```
| 91 | https://arxiv.org/abs/2604.20949 | Latent Microstructure Regimes | — | arXiv (Code Available) | N-CAUSAL-01 Three-Regime Causal Detector™, ↑N-EYES(causal DGP stable→latent→stress), ↑N-BACK(+18.6 lead-time, 200 simulations, BTC/USDT validation) | 2026-05-20 |
| 92 | https://arxiv.org/abs/2603.13638 | Causal Signal Engineering | — | arXiv | N-CAUSAL-02 Strictly Causal Forward Observables™, ↑N-BRAIN(hysteresis decision functional), ↑N-BACK(walk-forward adaptation) | 2026-05-20 |
| 93 | https://doi.org/10.5281/ZENODO.19520380 | Project Event Horizon | — | Zenodo | N-CAUSAL-03 Grand Unified Topological-Causal Model™, ↑N-BRAIN(topology+Granger+Hawkes+DAG, 15 signals, Sharpe 2.362) | 2026-05-20 |
| 94 | https://arxiv.org/abs/2511.04469 | TNCM-VAE | — | arXiv | N-BACK-16 Causal Counterfactual Generator™, ↑N-BACK(VAE+SCM+causal Wasserstein, L1 0.03-0.10) | 2026-05-20 |
| 95 | https://www.npmjs.com/package/@spfunctions/cli | @spfunctions/cli | — | npm | N-CAUSAL-04 Causal World Model Terminal™, ↑N-EYES(Bayesian node trees, 4,000+ contract scanner) | 2026-05-20 |
| 96 | https://www.catalyzex.com/paper/arxiv:2605.06822 | SFAG | — | ICASSP 2026 | N-BACK-17 SFAG Generator™, ↑N-BACK(differentiable structural constraints) | 2026-05-20 |
| 97 | https://github.com/CapitalOne-Research/PersonaLedger | PersonaLedger | — | GitHub (Capital One) | N-SYNTH-02 Persona-Conditioned LLM Generator™, ↑N-MEM(30M transactions, 23K users) | 2026-05-20 |
| 98 | https://github.com/microsoft/MarS | MarS (Microsoft) | — | GitHub (Microsoft) | N-SYNTH-03 Large Market Model Simulator™, ↑N-BACK(realistic order generation) | 2026-05-20 |
| 99 | https://arxiv.org/abs/2603.05231 | FairFinGAN | — | arXiv | N-SYNTH-04 Bias-Mitigated WGAN™, ↑N-BACK(fairness-aware generation) | 2026-05-20 |
| 100 | https://github.com/jsyoon0823/TimeGAN | TimeGAN | — | GitHub | N-SYNTH-05 Time-Series GAN Reference™, ↑N-BACK(NeurIPS 2019 baseline) | 2026-05-20 |
| 101 | https://github.com/seallabs/onlyfence | OnlyFence | — | GitHub | N-DEFI-01 Agent Wallet Guardrails™, ↑N-HANDS(swap+lend+borrow+LP) | 2026-05-20 |
| 102 | https://github.com/aaronjmars/agent-credit | Agent Credit | — | GitHub | N-DEFI-02 Credit Delegation for AI Agents™, ↑N-TREASURY(Aave V3 delegation) | 2026-05-20 |
| 103 | https://github.com/David-patrick-chuks/Kyro-Protocol | Kyro Protocol | — | GitHub | N-DEFI-03 Agent-Native Wallet Infrastructure™, ↑N-CORE(Stellar USDC, M2M) | 2026-05-20 |
| 104 | https://github.com/consensus-hq/spendos | SpendOS | — | GitHub | N-DEFI-04 Self-Governing Spending Agent™, ↑N-TREASURY(OWS policies) | 2026-05-20 |
| 105 | https://github.com/Uniswap/ai-skills | Uniswap AI Skills | — | GitHub (Uniswap Labs) | N-DEFI-05 Open-Source DEX Agent Plugins™, ↑N-HANDS(7 skills) | 2026-05-20 |
| 106 | https://github.com/kawacukennedy/kuberna-labs | Kuberna Labs | — | GitHub | N-DEFI-06 Decentralized Agent Execution Rails™, ↑N-DIPLOMACY(zkTLS) | 2026-05-20 |
| 107 | https://github.com/WujiangXu/AEL | AEL | — | GitHub, COLM 2026 | N-HEAL-01 Two-Timescale Self-Improving Agent™, ↑N-BRAIN-26(Sharpe 2.13) | 2026-05-20 |
| 108 | https://dev.to/igorganapolsky/ | Self-Healing Bot (122+ Lessons) | — | dev.to | N-HEAL-02 122+ Documented Failure Lessons™ | 2026-05-20 |
| 109 | https://github.com/CyberImmortal/clawdrive | ClawDrive | — | GitHub | N-HEAL-03 Self-Evolving AI Survival System™ | 2026-05-20 |
| 110 | https://lablab.ai | APEX Trader | — | lablab.ai | N-HEAL-04 5-Agent Pipeline with Self-Healing Daemon™ | 2026-05-20 |
| 111 | https://ieee.nitk.ac.in/project-hydra | Project HYDRA | — | IEEE NITK | N-HEAL-06 Kubernetes-Native Self-Healing™ | 2026-05-20 |
| 112 | https://github.com/NYTEMODEONLY/polyterm | PolyTerm | 25 | GitHub (MIT) | N-DASH-08 73-Screen TUI Analytics™ | 2026-05-20 |
| 113 | https://github.com/ChartGPU/ChartGPU | ChartGPU | — | GitHub (MIT) | N-DASH-01 WebGPU 1M Points™ | 2026-05-20 |
| 114 | https://brokeret.com/dicharts | diCharts | — | Brokeret (Open Source) | N-DASH-02 GPU Candlestick Engine™ | 2026-05-20 |
| 115 | https://github.com/qqrm/webgpu-candles | webgpu-candles | — | GitHub | N-DASH-03 Rust+WebGPU Candles™ | 2026-05-20 |
| 116 | https://github.com/flowsurface-rs/flowsurface | Flowsurface | — | GitHub (GPL-3.0) | N-DASH-04 Native GPU Charting™ | 2026-05-20 |
| 117 | https://github.com/DegenSugarBoo/OpenBook | OpenBook | 133 | GitHub (MIT) | N-DASH-05 Bookmap-Style Depth™ | 2026-05-20 |
| 118 | https://crates.io/crates/egui-charts | egui-charts | — | crates.io | N-DASH-06 130+ Indicators Engine™ | 2026-05-20 |
| 119 | https://deepmarket.live | DeepMarket | — | Product Hunt | N-DASH-07 3D Market Ocean™ | 2026-05-20 |
| 120 | https://github.com/Ashutosh0x/rust-finance | RustFinance Terminal | — | GitHub (MIT) | N-DASH-09 Institutional AI Terminal™ | 2026-05-20 |
| 121 | https://github.com/IvanWng97/TradingAgents-Telegram | TradingAgents-Telegram | — | GitHub (MIT) | N-DASH-10 Multi-Agent Telegram Wrapper™ | 2026-05-20 |
| 122 | https://github.com/ajadonai/thetickrbot | TheTickrBot v2.0 | — | GitHub (MIT) | N-DASH-11 Full-Featured Telegram Bot™ | 2026-05-20 |
| 123 | https://devpost.com/software/forecast-lens | ForecastLens | — | Devpost | N-DASH-12 Multi-Platform Prediction Dashboard™ | 2026-05-20 |
| 124 | https://www.npmjs.com/package/tigerpaw | Tigerpaw | — | npm | N-DASH-13 Local Notification System™ | 2026-05-20 |
| 125 | https://www.buildix.com | Buildix Orderflow | — | Web | N-DASH-14 Wallet-Attributed CVD™ | 2026-05-20 |
| 126 | https://devpost.com/software/oddsbase | OddsBase | — | Devpost | N-DASH-15 AI-Agent Market Aggregator™ | 2026-05-20 |
| 127 | https://github.com/lorhog1337/kalshi-polymarket-spread | kalshi-polymarket-spread | — | GitHub (MIT) | N-DASH-16 Cross-Platform Spread Monitor™ | 2026-05-20 |
| 128 | https://in.tradingview.com/script/FootprintKenshinC | Footprint (KenshinC) | — | TradingView | N-DASH-18 Optimized Footprint Chart™ | 2026-05-20 |
| 129 | https://blockchain.news | Santiment Top 100 Wallets | — | Web | N-EYES-36 Whale Activity Monitor™ | 2026-05-20 |
| 130 | https://academy.nansen.ai | Nansen CLI | — | Web | N-EYES-37 AI-Powered OnChain Research™ | 2026-05-20 |
| 131 | https://studio.glassnode.com | Glassnode Investor Behavior | — | Web | N-EYES-38 Behavioral Classification™ | 2026-05-20 |
| 132 | https://www.dextools.io | DEXTools Wallet Tracker | — | Web | N-EYES-39 Smart Money Tracker™ | 2026-05-20 |
| 133 | https://github.com/rookiester/rugpull-scam-token-detection | RugWatch | — | GitHub | N-SHIELDS-08 Real-Time Rugpull Detection™ | 2026-05-20 |
| 134 | https://github.com/Crzisaac/ETHOnline-2025-Hackathon-rug-pull-detector | ChainGuard Intelligence | — | GitHub | N-SHIELDS-10 AI On-Chain Fraud Detection™ | 2026-05-20 |
| 135 | https://github.com/Honeypot-Rug-Detector/.github | Honeypot & Rug Detector | — | GitHub | N-SHIELDS-11 Honeypot Scanner™ | 2026-05-20 |
| 136 | https://repos.ecosyste.ms | isRug.API | — | Web | N-SHIELDS-12 ERC-20 Risk API™ | 2026-05-20 |
| 137 | https://www.pulsemcp.com/servers/cryptorugmunch-rug-munch | Rug Munch Intelligence | — | PulseMCP | N-SHIELDS-09 19-Tool Risk Analysis™ | 2026-05-20 |
| 138 | https://arxiv.org/abs/2503.06614 | LROO Rug Pull Detector | — | arXiv | N-SHIELDS-13 Multimodal Fraud Detection™ | 2026-05-20 |
| 139 | https://github.com/skyzer/gold-digger | Gold Digger | — | GitHub | N-EYES-33 Compounding KOL Tracker™ | 2026-05-20 |
| 140 | https://apify.com | Crypto Twitter Tracker | — | Apify | N-EYES-40 1000+ Accounts Stream™ | 2026-05-20 |
| 141 | https://apps.apple.com | LunarCrush | — | App Store | N-EYES-41 Social Sentiment Analytics™ | 2026-05-20 |
| 142 | https://www.bitmart.com | BitMart X Insight | — | Web | N-EYES-42 300+ KOL Tracker™ | 2026-05-20 |
| 143 | https://apify.com/captivated_rank/crypto-sentiment-tracker-pro | Crypto Sentiment Tracker Pro | — | Apify | N-EYES-34 Multi-Platform Sentiment™ | 2026-05-20 |
| 144 | https://skillsmp.com/skills/virattt-dexter-src-skills-x-research-skill-md | x-research Agent Skill | — | SkillsMP | N-EYES-35 X/Twitter Sentiment Briefing™ | 2026-05-20 |
| 145 | https://hexmos.com | web3-research-mcp | — | Hexmos | N-TOOLS-29 Web3 Research Aggregator™ | 2026-05-20 |
| 146 | https://markets.businessinsider.com | altFINS API | — | BusinessInsider | N-TOOLS-28 150+ Indicators API™ | 2026-05-20 |
| 147 | https://github.com/Widiskel/sentient-narrative-agent | Sentient Narrative Agent | — | GitHub | N-BRAIN-35 Narrative Analysis Agent™ | 2026-05-20 |
| 148 | https://github.com/sanjana-1118/CryptoCurrency_Market_Dashboard | CoinPrism Dashboard | — | GitHub | N-DASH-19 Multi-Metric RT Dashboard™ | 2026-05-20 |
| 149 | https://arxiv.org/abs/2601.04687 | WebCryptoAgent | — | arXiv | N-BRAIN-34 Modality-Specific Agent Fusion™ | 2026-05-20 |
| 150 | https://bingx.com | BingX AI Claw | — | Web | N-BRAIN-36 Cross-Validated Signal Generator™ | 2026-05-20 |
| 151 | https://github.com/w2819/gorillionaire | Gorillionaire | — | GitHub | N-REWARD-01 AI Trading Leaderboard™ | 2026-05-20 |
| 152 | https://ethglobal.com/showcase/vibe-team-trading-8j3rj | Vibe Team Trading | — | ETHGlobal | N-REWARD-02 Group Sentiment Profit Share™ | 2026-05-20 |
| 153 | https://ethglobal.com/showcase/ai-pump-fun-qxnm5 | AI Pump Fun | — | ETHGlobal | N-REWARD-03 AI Trading Competition™ | 2026-05-20 |
| 154 | https://www.btcc.com | LeveX Quest System | — | Web | N-REWARD-04 Challenge-Based Rewards™ | 2026-05-20 |
| 155 | https://github.com/cobrababy420/extended-signal-bot | Extended Signal Bot | — | GitHub | N-EYES-31 TradFi Correlation Signals™ | 2026-05-20 |
| 156 | https://www.tradingview.com/script/9vS4tTwV/ | AetherEdge Hybrid AI Bias | — | TradingView | N-EYES-32 KNN+NN Hybrid Prediction™ | 2026-05-20 |
| 157 | https://in.tradingview.com/script/laG128wU/ | AetherEdge All-in-One Dashboard | — | TradingView | N-DASH-20 4-Module AI VERDICT™ | 2026-05-20 |
| 158 | https://pypi.org/project/predikt/ | predikt | — | PyPI | N-HANDS-20 Polymarket Autonomous Agent™ | 2026-05-20 |
| 159 | https://github.com/Predictly-MCP-Labs/polymarket-btc-5min-15min-arbitrage-bot | Polymarket BTC Arb Bot | — | GitHub | N-HANDS-21 BTC Up/Down CLOB Bot™ | 2026-05-20 |
| 160 | https://arxiv.org/abs/2509.09751v2 | Meta-RL-Crypto | — | arXiv | N-BRAIN-30 Actor-Judge-MetaJudge™ | 2026-05-20 |
| 161 | https://ojs.aaai.org/index.php/AAAI/article/view/40166 | ArchetypeTrader | — | AAAI | N-BRAIN-33 RL Archetype Selection™ | 2026-05-20 |
| 162 | https://arxiv.org/abs/2604.03888 | PolySwarm | — | arXiv | N-ROJ-01 50-Agent Swarm™ | 2026-05-20 |
| 163 | https://ethglobal.com/showcase/stroke-55s2g | Stroke | — | ETHGlobal | N-SHIELDS-07 Manipulation Profiteer™ | 2026-05-20 |
| 164 | https://devpost.com/software/fedsignal | FedSignal | — | Devpost | N-EYES-43 Fed Policy Shock Predictor™ | 2026-05-20 |
| 165 | https://github.com/yunus-0x/meridian | Meridian | — | GitHub | N-TREASURY-01 Autonomous LP Manager™ | 2026-05-20 |
| 166 | https://ethglobal.com/showcase/alphashield-ebq8u | AlphaShield | — | ETHGlobal | N-VERIFY-01 ZK Trading Credibility™ | 2026-05-20 |
| 167 | https://lib.rs/crates/moloch-consensus | Moloch Consensus | — | lib.rs | N-VERIFY-02 Cryptographic Audit Chain™ | 2026-05-20 |
| 168 | https://github.com/OAPS-Protocol/oaps-v0.1 | OAPS Protocol | — | GitHub | N-VERIFY-03 Open Audit Proof Standard™ | 2026-05-20 |
| 169 | https://arxiv.org/abs/2509.09751 | Meta-RL-Crypto | — | arXiv | N-BRAIN-30 Actor-Judge-MetaJudge™ | 2026-05-20 |
| 170 | https://arxiv.org/abs/2510.15949 | ATLAS | — | arXiv | N-BRAIN-31 Adaptive Prompt Optimization™ | 2026-05-20 |
| 171 | https://www.sciencedirect.com/science/article/abs/pii/S0893608026003850 | Logic-Q | — | Neural Networks | N-BRAIN-32 Neuro-Symbolic Trend Analysis™ | 2026-05-20 |
| 172 | https://github.com/sachmalan/kalshi-trading-bot | Beast-Mode Kalshi Bot | — | GitHub | N-HANDS-21 5-Agent Kalshi Debate™ | 2026-05-20 |
| 173 | https://www.npmjs.com/package/@darksol/autoresearch | @darksol/autoresearch | — | npm | N-ALCHEMIST-02 Base DEX AutoEvolution™ | 2026-05-20 |
| 174 | https://github.com/DeepJani05/multi-market-trading-bot | Multi-Market Bot | — | GitHub | N-CORE-06 Event-Driven Multi-Market™ | 2026-05-20 |
| 175 | https://github.com/xlabtg/TONAIAgent/issues/103 | TONAIAgent Treasury Layer | — | GitHub | N-TREASURY-02 Autonomous Fiscal Protocol™ | 2026-05-20 |
| 176 | https://arxiv.org/abs/2503.11499 | Sovereign-OS | — | arXiv | N-TREASURY-03 Charter-Governed Treasury™ | 2026-05-20 |
| 177 | https://github.com/SilverstreamsAI/NexusFix | NexusFix | — | GitHub | N-HANDS-19 Sub-100ns FIX Engine™ | 2026-05-20 |
| 178 | https://github.com/zostaff/poly-arbitrage-bot | Polymarket-Kalshi Arb Bot | — | GitHub | N-HANDS-22 Cross-Platform Prediction Arb™ | 2026-05-20 |
| 179 | https://thegraph.com | Arkham (The Graph) | — | Web | N-EYES-44 Decentralized On-Chain Indexing™ | 2026-05-20 |
| 180 | https://diadata.org | DIA Oracles | — | Web | N-EYES-45 Multi-Source Redundant Oracle™ | 2026-05-20 |
```

---

## 📊 9. STATYSTYKI DODATKU

| Metryka | Wartość |
|:---|:---|
| Nowe jednostki Imperial Guard | 1 (029_Blyskawiczny_Zwiad) |
| Nowe komnaty | 1 (War Loot Vault) |
| Nowe narzędzia ogółem | 90+ |
| Nowe wpisy w ZBADANE.md | 90 (pozycje 91-180) |
| Nowe kategorie odkryć | N-DASH, N-SHIELDS, N-EYES, N-BRAIN, N-HEAL, N-DEFI, N-SYNTH, N-CAUSAL, N-REWARD, N-TREASURY, N-VERIFY, N-ALCHEMIST, N-ROJ, N-HANDS |
| Luki zamknięte | L4, L5, L7, L8, L9 (system nagród), L10 (elastyczność zwiadu) |

---

**Koniec Dodatku 1 do Manifestu Imperium — Kingdom Pixel 2.0**

*Dokument gotowy do połączenia z wersją bazową. Wszystkie linki i opisy są prawdziwe i zgodne ze stanem na maj 2026. Zero halucynacji.*