# 📊 ZBADANE.md v3.1 — Rejestr Przebadanych Systemów (PO REJESTRACJI ARCHIWUM)

## Kingdom Pixel | Zasada Anti-duplikat | Autor: Jack

> **Wersja:** 3.1 | **Data:** 2026-05-25 | **Wpisy:** 330 | **Status:** PEŁNY, BEZ PLACEHOLDERÓW
>
> **Licencja:** Jack (Kingdom Pixel) – wszelkie prawa autorskie
>
> **Zmiany v3.1 względem v3.0 (rejestracja archiwum dyskowego Komendanta):**
> - Dodanych **8 nowych wpisów (#323–#330)** — 4 brakujące moduły (N-SHIELDS-04, N-BRAIN-072, N-ORCH-007, N-SHIELDS-06) + 4 dokumenty historyczne/architektoniczne, które Komendant ma fizycznie na dysku.
> - **Zaktualizowano 5 istniejących wpisów (#47, #48, #65, #186, #187)** — dodano oznaczenie „✅ na dysku" i adnotację „Dokumentacja techniczna: …" zgodnie z Zasadą 11 pkt 5.
> - **Skutek dla Suwerenności Wiedzy (Zasada 61):** Pokrycie modułów autorskich plikami fizycznymi wzrosło z 10/~117 (8,5%) do **18/~125 (14,4%)** — 4 nowe moduły mają już dokumentację raportową, ale wymagają jeszcze konwersji do plików `.py` zgodnie z Zasadą 11.
> - **Konsolidacja v3.0 (zachowana):** Wszystkie 322 pierwotne wpisy ZBADANE są fizycznie obecne w tabeli — bez odsyłaczy do poprzednich wersji.
> - **System tomowy (Zasada 60) zachowany:** Tom 01 (#1–#200) — źródła zewnętrzne, Tom 02 (#201–#330) — moduły autorskie i dokumenty.

---

## 📚 STRUKTURA LOGICZNA

| Tom | Wpisy | Zawartość |
|:---|:---|:---|
| **Tom 01** | #001–#200 | Zewnętrzne źródła zbadane: GitHub, arXiv, HuggingFace, dokumentacje API, materiały badawcze |
| **Tom 02** | #201–#330 | Oryginalne moduły Jacka, hybrydy autorskie Królestwa Pixel, dokumenty architektoniczne i historyczne |

---

## 📋 REJESTR PEŁNY (322 wpisy)

### Tom 01 + Tom 02 — wszystkie wpisy w jednej tabeli

| # | URL / Plik | Nazwa | Klasa | Licencja | Kluczowe odkrycia / moduły | 📂 Folder Kingdom Pixel | Data |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | https://github.com/xa-io/Tradingview-Indicators | Tradingview-Indicators | 0 | Pine | N-EYES-22, N-EYES-23, N-TOOLS-21, N-TOOLS-22, N-TOOLS-23 | ⚔️ 02_Zwiadowcy / 07_Saperzy | 2026-05-18 |
| 2 | https://github.com/Degenapetrader/TRUST-BOT | TRUST-BOT | 7 | AGPL-3.0 | N-HANDS-14, N-HANDS-15, ❌ FarmBot=wash | ⚔️ 03_Kawaleria | 2026-05-18 |
| 3 | https://github.com/bitbytelabio/tradingview-rs | tradingview-rs | 64 | MIT | N-EYES-24, N-BACK-10, Replay Mode | ⚔️ 02_Zwiadowcy / 09_Poligon | 2026-05-18 |
| 4 | https://github.com/285729101/quant-engine | quant-engine | 0 | MIT | ✅ DUP (wszystko mamy), zero-dep fallback | — | 2026-05-18 |
| 5 | https://github.com/tesserspace/tesser | tesser | 157 | MIT/Apache | N-HANDS Iceberg, ONNX Runtime, State Reconciliation | ⚔️ 03_Kawaleria / 07_Saperzy | 2026-05-19 |
| 6 | https://github.com/DevomB/Athenas-Pallas | Athenas-Pallas | 0 | MIT | N-HANDS-17 Control Plane API, N-SHIELDS-03 | ⚔️ 03_Kawaleria / 04_Gwardia | 2026-05-19 |
| 7 | https://github.com/thrasher-corp/gocryptotrader | GoCryptoTrader | 3.4k | MIT | N-HANDS-16 SMS Fallback, N-SHIELDS-06 AES256+OTP | ⚔️ 03_Kawaleria / 04_Gwardia | 2026-05-19 |
| 8 | https://github.com/ccxt/ccxt | ccxt | 42.4k | MIT | N-BRAIN-15 WebSocket, MEXC certified✅ | ⚔️ 01_Wywiad | 2026-05-19 |
| 9 | https://github.com/JKorf/CryptoClients.Net | CryptoClients.Net | 42 | MIT | Dynamic credential mgmt, MEXC+BloFin✅ | 📋 Do klasyfikacji | 2026-05-19 |
| 10 | https://github.com/tripolskypetr/node-ccxt-dumper | node-ccxt-dumper | 0 | MIT | N-TOOLS-24 Slope Analyzer, VROC, LLM Markdown | ⚔️ 01_Wywiad / 07_Saperzy | 2026-05-19 |
| 11 | https://github.com/c9s/bbgo | bbgo | 1.6k | AGPL-3.0 | 12 wskaźników, Grid, DCA, ❌ AGPL→koncepty | — | 2026-05-19 |
| 12 | https://github.com/coding-kitties/investing-algorithm-framework | investing-algorithm-framework | 728 | Apache-2.0 | N-BACK-11 HTML Report, N-BRAIN-20 Scaling Rules | ⚔️ 01_Wywiad / 09_Poligon | 2026-05-19 |
| 13 | https://github.com/cryptocj520/crypto-trading-open | crypto-trading-open | 1.6k | ❌ brak | N-BRAIN-18 APR ratings, ❌ Volume Maker=wash | ⚔️ 01_Wywiad / 03_Kawaleria | 2026-05-19 |
| 14 | https://github.com/Mattbusel/FinRL_DeepSeek_Crypto_Trading | LARSA/FinRL_DeepSeek | 9 | MIT | N-BRAIN-21 Multi-Agent Debate, ADWIN drift | ⚔️ 01_Wywiad / 09_Poligon | 2026-05-19 |
| 15 | https://github.com/xiechengmude/xDAN-Crypto-nofx | xDAN-NOFX | 0 | AGPL-3.0 | CoT logging, leaderboard, ❌ AGPL→koncepty | — | 2026-05-19 |
| 16 | https://github.com/stefanoviana/deepalpha | DeepAlpha V11 | 6 | MIT | N-TOOLS-25 Liquidation Estimator, VPIN, BiLSTM | ⚔️ 01_Wywiad / 03_Kawaleria / 04_Gwardia | 2026-05-19 |
| 17 | (plik) NOFX source code | NOFX Go source | — | AGPL-3.0 | N-BRAIN-02 BuildPrompt, DeepSeek temp=0.7 | ⚔️ 01_Wywiad | 2026-05-19 |
| 18 | https://github.com/Patrick-code-Bot/nautilus_AItrader | nautilus_AItrader | 24 | Educational | N-HANDS-03 OCO Redis, Confidence-scaled TP | ⚔️ 03_Kawaleria | 2026-05-19 |
| 19 | https://github.com/decoded-cipher/bitnerve | bitnerve | 3 | MIT | OpenRouter API, multi-LLM endpoint | ⚔️ 01_Wywiad | 2026-05-19 |
| 20 | https://github.com/garagesteve1155/PowerTrader_AI | PowerTrader_AI | 685 | Apache-2.0 | N-BRAIN-20 24hr DCA window, kNN predictor | ⚔️ 01_Wywiad | 2026-05-19 |
| 21 | https://github.com/0x0funky/TradingAgents-crypto | TradingAgents-crypto | 105 | Apache-2.0 | N-BRAIN-21 Tokenomics Analyst, LangGraph DAG | ⚔️ 01_Wywiad | 2026-05-19 |
| 22 | https://github.com/HKUDS/Vibe-Trading | Vibe-Trading | 6.9k | MIT | N-BACK-13 Shadow Account, N-BRAIN-19 MVO | ⚔️ 01_Wywiad / 09_Poligon | 2026-05-19 |
| 23 | https://github.com/ElioIshak/AIndicate | AIndicate | 1 | MIT | ✅ DUP, OC Return feature | — | 2026-05-19 |
| 24 | https://github.com/MShahabSepehri/CryptoMamba | CryptoMamba | 210 | MIT | N-BRAIN-22 Mamba SSM (-36% RMSE vs LSTM) | ⚔️ 01_Wywiad | 2026-05-19 |
| 25 | https://github.com/monicalamagt/crypto-momentum-model | crypto-momentum-model | 0 | ❌ brak | CatBoost, Extreme Momentum Filter | — | 2026-05-19 |
| 26 | https://github.com/0xquqi/crypto-kol-quant | crypto-kol-quant | 31 | MIT | N-EYES-25 KOL Consensus, 200W MA IC+0.297 | ⚔️ 02_Zwiadowcy | 2026-05-19 |
| 27 | https://github.com/195440/nof1.ai | nof1.ai | 611 | AGPL-3.0 | N-SHIELDS-03 3-tier drawdown, ❌ AGPL | ⚔️ 04_Gwardia | 2026-05-19 |
| 28 | https://github.com/python-telegramBot/ai-auto-trading | NexusQuant | 113 | AGPL-3.0 | N-BRAIN-10 8-state market, R-Multiple TP | ⚔️ 01_Wywiad / 03_Kawaleria | 2026-05-19 |
| 29 | https://github.com/alsk1992/CloddsBot | CloddsBot | 194 | MIT | N-SHIELDS-05 GoPlus, MEXC 200x✅ | ⚔️ 04_Gwardia | 2026-05-19 |
| 30 | https://github.com/ronalzhang/Jesse | Jesse+ | 0 | MIT | GARCH, Genetic Algorithm optimization | ⚔️ 07_Saperzy | 2026-05-19 |
| 31 | https://github.com/snndmaa/binance_bot | binance_bot | 0 | ❌ brak | N-EYES-14 Wallet Flow, Ensemble ML | ⚔️ 02_Zwiadowcy / 03_Kawaleria | 2026-05-19 |
| 32 | https://github.com/NB-Group/BTC_Trading | BTC_Trading | 23 | AGPL-3.0 | N-BRAIN-02 VLM Chart Analysis, DeepSeek-R1 | ⚔️ 01_Wywiad | 2026-05-19 |
| 33 | https://github.com/cluster2600/ELVIS | ELVIS | 4 | MIT | N-SHIELDS-06 HashiCorp Vault, Google Trends | ⚔️ 04_Gwardia / 07_Saperzy | 2026-05-19 |
| 34 | https://github.com/HasanNoMore/24-7-fully-automated-Trading-dashboard--Copilot | 24-7 Copilot | 0 | MIT | N-EYES-27 CVD Tracker, TimescaleDB | ⚔️ 02_Zwiadowcy | 2026-05-19 |
| 35 | https://github.com/Alz-Android/crypto-trading-drl | crypto-trading-drl | 1 | MIT | ✅ DUP, GAE PPO=0.95 reference | — | 2026-05-19 |
| 36 | https://github.com/humanplane/cross-market-state-fusion | cross-market-state-fusion | 368 | MIT | N-EYES-27 CVD Acceleration, TemporalEncoder | ⚔️ 01_Wywiad / 02_Zwiadowcy | 2026-05-19 |
| 37 | https://devpost.com/software/argos-ic2tyk | ARGOS (Hackathon) | — | MIT-like | N-EYES-26 Insider Detection, IAS 0-1 | ⚔️ 01_Wywiad / 02_Zwiadowcy | 2026-05-19 |
| 38 | https://github.com/chaoleiyv/polymarket-whale-watcher | polymarket-whale-watcher | 203 | MIT | N-EYES-26 IAS, DeFiLlama TVL | ⚔️ 02_Zwiadowcy | 2026-05-19 |
| 39 | https://github.com/NYTEMODEONLY/polyterm | polyterm | 25 | MIT | N-EYES-14 wallet cluster, DB auto-cleanup | ⚔️ 02_Zwiadowcy / 03_Kawaleria | 2026-05-19 |
| 40 | https://github.com/kadeslabs/kinetic-anomaly-detection-engine-system | KADES | 0 | ❌ PROPRIETARY | ❌ Solana-only, SKIP | — | 2026-05-19 |
| 41 | https://github.com/y3y-tech/DeFi_RiskAndOpt_Platform | DeFi_RiskAndOpt | 0 | ❌ brak | N-TOOLS-25 cascade liquidation, CEX deposit | ⚔️ 02_Zwiadowcy / 07_Saperzy | 2026-05-19 |
| 42 | https://github.com/suislanchez/polymarket-insider-detector | polymarket-insider-detector | 3 | MIT | N-EYES-26 binomial p-value, Sybil detection | ⚔️ 02_Zwiadowcy | 2026-05-19 |
| 43 | https://github.com/0xf3dz/nullcraft | nullcraft | 4 | ❌ brak | BIFROST /setthreshold Telegram | — | 2026-05-19 |
| 44 | https://github.com/DelaneKay/twitter-meme-radar | twitter-meme-radar | 0 | MIT | N-EYES-13 Hype Score, Grok API | ⚔️ 02_Zwiadowcy | 2026-05-19 |
| 45 | https://github.com/benzdriver/AI-BTC-TRADER | AI-BTC-TRADER | 5 | MIT | N-BRAIN-24 Microstructure Engine | ⚔️ 01_Wywiad | 2026-05-19 |
| 46 | https://github.com/mtakrori/crypto-microstructure-trader | crypto-microstructure-trader | 0 | MIT | N-BRAIN-07 stop hunt detection | ⚔️ 01_Wywiad | 2026-05-19 |
| 47 | (plik) nasze_orginalne_pomysły.md ✅ na dysku | NexusCore + CogniCore + OmniSight | — | Jack | N-CORE-04, N-BRAIN-25, N-EYES-28. Dokumentacja techniczna: `nasze_orginalne_pomys_y.md` | ⚔️ 00_Sztab + 01_Wywiad + 02_Zwiadowcy | 2026-05-19 |
| 48 | (plik) nasze_orginalne_pomysły1.md ✅ na dysku | NexGenHub + MetaCortex | — | Jack | N-CORE-05, N-BRAIN-26. Dokumentacja techniczna: `nasze_orginalne_pomys_y1.md` | ⚔️ 00_Sztab + 01_Wywiad | 2026-05-19 |
| 49 | https://github.com/Bender1011001/nautilis-trader-bot | AVES | 2 | MIT | API Budget $4.50, Agent Attribution | ⚔️ 01_Wywiad / 09_Poligon | 2026-05-19 |
| 50 | https://github.com/TauricResearch/TradingAgents | TradingAgents | 73k | Apache-2.0 | N-MEM-04 Trade Learning Record, LangGraph | ⚔️ 01_Wywiad / 05_Archiwum | 2026-05-19 |
| 51 | https://github.com/zhound420/swarm-trader | swarm-trader | 0 | MIT | 12 legendary investor agents, SEC EDGAR | ⚔️ 01_Wywiad | 2026-05-19 |
| 52 | https://github.com/JDxus/ClawQuant | ClawQuant | 45 | MIT | N-MEM-04 Trade Learning Record, Gated Promotion | ⚔️ 01_Wywiad / 05_Archiwum / 09_Poligon | 2026-05-19 |
| 53 | https://github.com/xiechengmude/xDAN-Crypto-nofx | xDAN-Crypto-nofx | 0 | AGPL | ⚠️ DUPLIKAT #15 | — | 2026-05-19 |
| 54 | https://github.com/The-R4V3N/Nexus | Nexus | 0 | MIT | N-BRAIN-27 Axiom Self-Reflection, prompt injection | ⚔️ 01_Wywiad / 04_Gwardia | 2026-05-20 |
| 55 | https://github.com/dietmarwo/autoresearch-trading | autoresearch-trading | 0 | MIT | N-BACK-14 AutoEvolution Engine L7✅ | ⚔️ 09_Poligon | 2026-05-20 |
| 56 | https://github.com/NeuZhou/stratevo | stratevo | 45 | AGPL-3.0 | Arena Mode, NSGA-III, ❌ AGPL | ⚔️ 01_Wywiad / 03_Kawaleria | 2026-05-20 |
| 57 | https://github.com/chencore/autoresearch-crypto | autoresearch-crypto | 51 | MIT | N-BACK-14 ATLAS, GEPA, Maker/Taker fee opt | ⚔️ 03_Kawaleria / 09_Poligon | 2026-05-20 |
| 58 | https://github.com/kb-90/okx-algotrade-agent-x | okx-algotrade-agent-x | 4 | AGPL-3.0 | Config presets, intelligent exit LSTM | ⚔️ 03_Kawaleria | 2026-05-20 |
| 59 | https://github.com/gabrielmaialva33/trading-swarm | trading-swarm | 3 | MIT | 500 concurrent agents, OTP fault tolerance | — | 2026-05-20 |
| 60 | https://github.com/k-abacus/NeuroEvolution-Crypto-Trading-Bot | NeuroEvolution-Crypto | 1 | MIT | ✅ DUP (TF population evolution) | — | 2026-05-20 |
| 61 | https://github.com/mxjoly/trading-robots-factory-cpp | trading-robots-factory-cpp | 2 | MIT | NEAT algorithm C++, HTML fitness reports | — | 2026-05-20 |
| 62 | https://github.com/alex-jb/orallexa-ai-trading-agent | orallexa-ai-trading-agent | 6 | MIT | N-BRAIN-28 Orallexa ML Ensemble (9 modeli) | ⚔️ 01_Wywiad | 2026-05-20 |
| 63 | https://orallexa-ui.vercel.app/ | Orallexa UI (live demo) | — | MIT | ✅ Ten sam system co #62 | — | 2026-05-20 |
| 64 | https://alex-jb.github.io/orallexa-ai-trading-agent/presentation.html | Orallexa Presentation | — | MIT | ✅ Ten sam system co #62 | — | 2026-05-20 |
| 65 | (plik) Tytan_Alpha.md ✅ na dysku | Tytan-α Orkiestrator | — | Jack | N-CORE-06 Tytan-α (Python+Rust+Zig, 6 filarów). Dokumentacja techniczna: `Tytan_Alpha.md` | ⚔️ 00_Sztab + 🗺️ War Council | 2026-05-20 |
| 66 | (plik) Kingdom_Pixel_v1.md | Kingdom Pixel Manifest v1 | — | Jack | N-ALCH-01 Nadworny Alchemik | 🧪 Royal Alchemist | 2026-05-20 |
| 67 | (plik) Kingdom_Pixel_v2_0.md | Kingdom Pixel v2.0 Manifest | — | Jack | Pełna struktura v2.0 | 📋 Do klasyfikacji | 2026-05-20 |
| 68 | (plik) Kingdom_Pixel_v2_0_dodatek1.md | Kingdom Pixel v2.0 Dodatek 1 | — | Jack | 029_Blyskawiczny_Zwiad, War Loot Vault | 📋 Do klasyfikacji | 2026-05-20 |
| 69 | https://arxiv.org/abs/2605.06822 | SHARP | — | arXiv | N-VERIFY-01 Human-Auditable Rubric | ⚔️ 11_Inspekcja | 2026-05-20 |
| 70 | https://arxiv.org/abs/2604.03888 | PolySwarm | — | arXiv | N-ROJ-01, N-EYES-29 KL/JS Divergence | ⚔️ 02_Zwiadowcy / 12_Roj | 2026-05-20 |
| 71 | https://ethglobal.com/showcase/stroke-55s2g | Stroke | — | ETHGlobal | N-SHIELDS-07 Manipulation Profiteer | ⚔️ 04_Gwardia | 2026-05-20 |
| 72 | https://www.emergentmind.com/topics/macrohft-framework | MacroHFT | — | arXiv | N-HANDS-19 Memory-Augmented HFT | ⚔️ 03_Kawaleria | 2026-05-20 |
| 73 | https://iclr.cc/virtual/2024/22156 | FinMem | — | ICLR | N-MEM-05 Layered Memory Agent | ⚔️ 05_Archiwum + 📚 Great Library | 2026-05-20 |
| 74 | https://ethglobal.com/showcase/neurotrade-agents-dritt | NeuroTrade Agents | — | ETHGlobal | N-DIPLOMACY-01 Federated Learning Swarm | 🤝 Diplomacy | 2026-05-20 |
| 75 | https://github.com/RA-CONSULTING/AUREON-QUANTUM-TRADING-SYSTEM-AQTS- | AUREON | — | GitHub | N-KWANT-01 Field-Theoretic Market Model | ⚔️ 14_Kwantowy_Korpus | 2026-05-20 |
| 76 | https://devpost.com/software/trademaxxer | TradeMaxxer | — | ETHGlobal | N-HANDS-20 Sub-500ms News-to-Trade | ⚔️ 03_Kawaleria | 2026-05-20 |
| 77 | https://devpost.com/software/atlas-fp24tr | Atlas | — | ETHGlobal | N-ORCH-05 Macro Decision OS, N-BACK-15 AnalogueEngine | ⚔️ 08_Sztab + 🗺️ War Council | 2026-05-20 |
| 78 | https://pypi.org/project/predikt | predikt | — | PyPI | N-HANDS-21 Polymarket Autonomous Agent | ⚔️ 03_Kawaleria | 2026-05-20 |
| 79 | https://github.com/komako-workshop/digital-oracle | Digital Oracle | — | MIT | N-EYES-30 12-Source Macro Oracle | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 80 | https://github.com/yorkeccak/Polyseer | Polyseer | — | GitHub | N-BRAIN-29 Bayesian Multi-Agent Research | ⚔️ 01_Wywiad | 2026-05-20 |
| 81 | https://lablab.ai/ai-hackathons/ai-trading-agents/hivemind/hivemind-multi-brain-trading-council | HIVEMIND | — | lablab.ai | N-ORCH-06 4-Brain Voting Council | ⚔️ 08_Sztab + 🗺️ War Council | 2026-05-20 |
| 82 | https://www.npmjs.com/package/@spfunctions/cli | @spfunctions/cli | — | npm | N-TOOLS-27 Terminal Prediction Agent | ⚔️ 07_Saperzy | 2026-05-20 |
| 83 | https://github.com/NenoL2001/open-quant-agent | Robin | — | GitHub | N-ALCH-03 Agentic Quant Research | 🧪 Royal Alchemist | 2026-05-20 |
| 84 | https://devpost.com/software/fedsignal | FedSignal | — | Devpost | N-EYES-31 Fed Policy Shock Predictor (75.8%) | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 85 | https://github.com/yunus-0x/meridian | Meridian | — | GitHub | N-TREASURY-01 Autonomous LP Manager | 💰 Royal Treasury | 2026-05-20 |
| 86 | https://ethglobal.com/showcase/alphashield-ebq8u | AlphaShield | — | ETHGlobal | N-VERIFY-02 ZK Trading Credibility | ⚔️ 11_Inspekcja | 2026-05-20 |
| 87 | https://lib.rs/crates/moloch-consensus | Moloch Consensus | — | lib.rs | N-VERIFY-03 Cryptographic Audit Chain (48.7k linii Rust) | ⚔️ 11_Inspekcja | 2026-05-20 |
| 88 | https://github.com/OAPS-Protocol/oaps-v0.1 | OAPS Protocol | — | GitHub | N-VERIFY-04 Open Audit Proof Standard | ⚔️ 11_Inspekcja | 2026-05-20 |
| 89 | https://arxiv.org/abs/2509.09751 | Meta-RL-Crypto | — | arXiv | N-BRAIN-30 Actor-Judge-MetaJudge | ⚔️ 01_Wywiad | 2026-05-20 |
| 90 | https://arxiv.org/abs/2510.15949 | ATLAS (APO) | — | arXiv | N-BRAIN-31 Adaptive Prompt Optimization | ⚔️ 01_Wywiad | 2026-05-20 |
| 91 | https://www.sciencedirect.com/science/article/abs/pii/S0893608026003850 | Logic-Q | — | Neural Networks 2026 | N-BRAIN-32 Neuro-Symbolic Trend Analysis | ⚔️ 01_Wywiad | 2026-05-20 |
| 92 | https://github.com/sachmalan/kalshi-trading-bot | Beast-Mode Kalshi Bot | — | GitHub | N-HANDS-22 5-Agent Kalshi Debate | ⚔️ 03_Kawaleria | 2026-05-20 |
| 93 | https://www.npmjs.com/package/@darksol/autoresearch | @darksol/autoresearch | — | npm | N-ALCH-04 Base DEX AutoEvolution | 🧪 Royal Alchemist | 2026-05-20 |
| 94 | https://github.com/DeepJani05/multi-market-trading-bot | Multi-Market Bot | — | GitHub | N-CORE-07 Event-Driven Multi-Market | ⚔️ 00_Sztab | 2026-05-20 |
| 95 | https://arxiv.org/abs/2604.20949 | Latent Microstructure Regimes | — | arXiv | N-CAUSAL-01 Three-Regime Detector (+18.6 BTC) | ⚔️ 13_Analiza_Przyczynowa | 2026-05-20 |
| 96 | https://arxiv.org/abs/2603.13638 | Causal Signal Engineering | — | arXiv | N-CAUSAL-02 Causal Forward Observables | ⚔️ 13_Analiza_Przyczynowa | 2026-05-20 |
| 97 | https://doi.org/10.5281/ZENODO.19520380 | Project Event Horizon | — | Zenodo | N-CAUSAL-03 Unified Topological-Causal Model (Sharpe 2.362) | ⚔️ 13_Analiza_Przyczynowa | 2026-05-20 |
| 98 | https://arxiv.org/abs/2511.04469 | TNCM-VAE | — | arXiv | N-BACK-16 Causal Counterfactual Generator | ⚔️ 09_Poligon | 2026-05-20 |
| 99 | https://github.com/CapitalOne-Research/PersonaLedger | PersonaLedger | — | GitHub | N-SYNTH-02 Persona-Conditioned LLM (30M transakcji) | ⚔️ 09_Poligon | 2026-05-20 |
| 100 | https://github.com/microsoft/MarS | MarS (Microsoft) | — | GitHub | N-SYNTH-03 Large Market Model Simulator | ⚔️ 09_Poligon | 2026-05-20 |
| 101 | https://arxiv.org/abs/2603.05231 | FairFinGAN | — | arXiv | N-SYNTH-04 Bias-Mitigated WGAN | ⚔️ 09_Poligon | 2026-05-20 |
| 102 | https://github.com/jsyoon0823/TimeGAN | TimeGAN | — | NeurIPS | N-SYNTH-05 Time-Series GAN Reference | ⚔️ 09_Poligon | 2026-05-20 |
| 103 | https://github.com/seallabs/onlyfence | OnlyFence | — | GitHub | N-DEFI-01 Agent Wallet Guardrails | 💰 Royal Treasury + ⚔️ 03_Kawaleria | 2026-05-20 |
| 104 | https://github.com/aaronjmars/agent-credit | Agent Credit | — | GitHub | N-DEFI-02 Credit Delegation (Aave V3) | 💰 Royal Treasury + ⚔️ 03_Kawaleria | 2026-05-20 |
| 105 | https://github.com/David-patrick-chuks/Kyro-Protocol | Kyro Protocol | — | GitHub | N-DEFI-03 Agent-Native Wallet (Stellar) | 💰 Royal Treasury + ⚔️ 03_Kawaleria | 2026-05-20 |
| 106 | https://github.com/consensus-hq/spendos | SpendOS | — | GitHub | N-DEFI-04 Self-Governing Spending Agent | 💰 Royal Treasury + ⚔️ 03_Kawaleria | 2026-05-20 |
| 107 | https://github.com/Uniswap/ai-skills | Uniswap AI Skills | — | GitHub | N-DEFI-05 DEX Agent Plugins (7 pluginów) | 💰 Royal Treasury + ⚔️ 03_Kawaleria | 2026-05-20 |
| 108 | https://github.com/kawacukennedy/kuberna-labs | Kuberna Labs | — | GitHub | N-DEFI-06 Decentralized Agent Execution Rails | 💰 Royal Treasury + ⚔️ 03_Kawaleria | 2026-05-20 |
| 109 | https://github.com/WujiangXu/AEL | AEL | — | COLM 2026 | N-HEAL-01 Two-Timescale Self-Improving Agent (Sharpe 2.13) | 🏰 The Keep / Watchers | 2026-05-20 |
| 110 | https://dev.to/igorganapolsky/i-built-a-self-healing-ai-trading-bot-that-learns-from-every-failure-g94 | Self-Healing Bot | — | dev.to | N-HEAL-02 122+ Documented Failure Lessons | 🏰 The Keep / Watchers | 2026-05-20 |
| 111 | https://github.com/CyberImmortal/clawdrive | ClawDrive | — | GitHub | N-HEAL-03 Self-Evolving AI Survival System | 🏰 The Keep / Watchers | 2026-05-20 |
| 112 | https://lablab.ai/ai-hackathons/ai-trading-agents/apex-trader/apex-trader-autonomous-multi-agent-trading-system | APEX Trader | — | lablab.ai | N-HEAL-04 5-Agent Self-Healing Daemon | 🏰 The Keep / Watchers | 2026-05-20 |
| 113 | https://ieee.nitk.ac.in/project-hydra | Project HYDRA | — | IEEE | N-HEAL-05 Kubernetes-Native Self-Healing | 🏰 The Keep / Watchers | 2026-05-20 |
| 114 | https://github.com/ChartGPU/ChartGPU | ChartGPU | — | MIT | N-DASH-03 WebGPU 50M+ Points (60fps) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 115 | https://brokeret.com/dicharts | diCharts | — | Open Source | N-DASH-04 GPU Candlestick Engine (100K+ świec) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 116 | https://github.com/qqrm/webgpu-candles | webgpu-candles | — | GitHub | N-DASH-05 Rust+WebGPU Candles | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 117 | https://github.com/flowsurface-rs/flowsurface | Flowsurface | — | GPL-3.0 | N-DASH-06 Native GPU Charting (MEXC!) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 118 | https://github.com/DegenSugarBoo/OpenBook | OpenBook | 133 | MIT | N-DASH-07 Bookmap-Style Depth | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 119 | https://crates.io/crates/egui-charts | egui-charts | — | crates.io | N-DASH-08 130+ Indicators Engine | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 120 | https://deepmarket.live | DeepMarket | — | Product Hunt | N-DASH-09 3D Market Ocean (200 aktywów) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 121 | https://github.com/Ashutosh0x/rust-finance | RustFinance Terminal | — | MIT | N-DASH-10 Institutional AI Terminal (TWAP, VWAP) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 122 | https://github.com/IvanWng97/TradingAgents-Telegram | TradingAgents-Telegram | — | MIT | N-DASH-11 Multi-Agent Telegram Wrapper | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 123 | https://github.com/ajadonai/thetickrbot | TheTickrBot v2.0 | — | MIT | N-DASH-12 Full-Featured Telegram Bot | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 124 | https://devpost.com/software/forecast-lens | ForecastLens | — | Devpost | N-DASH-13 Multi-Platform Prediction Dashboard | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 125 | https://www.npmjs.com/package/tigerpaw | Tigerpaw | — | npm | N-DASH-14 Local Notification System | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 126 | https://www.buildix.com | Buildix Orderflow | — | Web | N-DASH-15 Wallet-Attributed CVD (5 giełd) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 127 | https://devpost.com/software/oddsbase | OddsBase | — | Devpost | N-DASH-16 AI-Agent Market Aggregator (25k+ rynków) | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 128 | https://github.com/lorhog1337/kalshi-polymarket-spread | kalshi-polymarket-spread | — | MIT | N-DASH-17 Cross-Platform Spread Monitor | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 129 | https://in.tradingview.com/script/FootprintKenshinC | Footprint (KenshinC) | — | TradingView | N-DASH-18 Optimized Footprint Chart | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 130 | https://blockchain.news | Santiment Top 100 Wallets | — | Web | N-EYES-32 Whale Activity Monitor | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 131 | https://academy.nansen.ai | Nansen CLI | — | Web | N-EYES-33 AI-Powered OnChain Research | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 132 | https://studio.glassnode.com | Glassnode Investor Behavior | — | Web | N-EYES-34 Behavioral Classification | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 133 | https://www.dextools.io | DEXTools Wallet Tracker | — | Web | N-EYES-35 Smart Money Tracker (multi-chain) | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 134 | https://github.com/rookiester/rugpull-scam-token-detection | RugWatch | — | GitHub | N-SHIELDS-08 Real-Time Rugpull Detection (Solana) | ⚔️ 04_Gwardia | 2026-05-20 |
| 135 | https://github.com/Crzisaac/ETHOnline-2025-Hackathon-rug-pull-detector | ChainGuard Intelligence | — | GitHub | N-SHIELDS-09 AI On-Chain Fraud Detection (EVM) | ⚔️ 04_Gwardia | 2026-05-20 |
| 136 | https://github.com/Honeypot-Rug-Detector/.github | Honeypot & Rug Detector | — | GitHub | N-SHIELDS-10 Honeypot Scanner | ⚔️ 04_Gwardia | 2026-05-20 |
| 137 | https://repos.ecosyste.ms | isRug.API | — | Web | N-SHIELDS-11 ERC-20 Risk API | ⚔️ 04_Gwardia | 2026-05-20 |
| 138 | https://www.pulsemcp.com/servers/cryptorugmunch-rug-munch | Rug Munch Intelligence | — | PulseMCP | N-SHIELDS-12 19-Tool Risk Analysis | ⚔️ 04_Gwardia | 2026-05-20 |
| 139 | https://arxiv.org/abs/2503.06614 | LROO Rug Pull Detector | — | arXiv | N-SHIELDS-13 Multimodal Fraud Detection | ⚔️ 04_Gwardia | 2026-05-20 |
| 140 | https://github.com/skyzer/gold-digger | Gold Digger | — | GitHub | N-EYES-36 Compounding KOL Tracker | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 141 | https://apify.com | Crypto Twitter Tracker | — | Apify | N-EYES-37 1000+ Accounts Stream | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 142 | https://apps.apple.com | LunarCrush | — | App Store | N-EYES-38 Social Sentiment Analytics (20k+ aktywów) | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 143 | https://www.bitmart.com | BitMart X Insight | — | Web | N-EYES-39 300+ KOL Tracker | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 144 | https://apify.com/captivated_rank/crypto-sentiment-tracker-pro | Crypto Sentiment Tracker Pro | — | Apify | N-EYES-40 Multi-Platform Sentiment | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 145 | https://skillsmp.com/skills/virattt-dexter-src-skills-x-research-skill-md | x-research Agent Skill | — | SkillsMP | N-EYES-41 X/Twitter Sentiment Briefing | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 146 | https://hexmos.com | web3-research-mcp | — | Hexmos | N-TOOLS-28 Web3 Research Aggregator | ⚔️ 07_Saperzy | 2026-05-20 |
| 147 | https://markets.businessinsider.com | altFINS API | — | BusinessInsider | N-TOOLS-29 150+ Indicators API (2200+ aktywów) | ⚔️ 07_Saperzy | 2026-05-20 |
| 148 | https://github.com/Widiskel/sentient-narrative-agent | Sentient Narrative Agent | — | GitHub | N-BRAIN-33 Narrative Analysis Agent | ⚔️ 01_Wywiad | 2026-05-20 |
| 149 | https://github.com/sanjana-1118/CryptoCurrency_Market_Dashboard | CoinPrism Dashboard | — | GitHub | N-DASH-19 Multi-Metric RT Dashboard | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 150 | https://arxiv.org/abs/2601.04687 | WebCryptoAgent | — | arXiv | N-BRAIN-34 Modality-Specific Agent Fusion | ⚔️ 01_Wywiad | 2026-05-20 |
| 151 | https://bingx.com | BingX AI Claw | — | Web | N-BRAIN-35 Cross-Validated Signal Generator | ⚔️ 01_Wywiad | 2026-05-20 |
| 152 | https://github.com/w2819/gorillionaire | Gorillionaire | — | GitHub | N-REWARD-01 AI Trading Leaderboard | 💰 Royal Treasury / War Loot Vault | 2026-05-20 |
| 153 | https://ethglobal.com/showcase/vibe-team-trading-8j3rj | Vibe Team Trading | — | ETHGlobal | N-REWARD-02 Group Sentiment Profit Share | 💰 Royal Treasury / War Loot Vault | 2026-05-20 |
| 154 | https://ethglobal.com/showcase/ai-pump-fun-qxnm5 | AI Pump Fun | — | ETHGlobal | N-REWARD-03 AI Trading Competition | 💰 Royal Treasury / War Loot Vault | 2026-05-20 |
| 155 | https://www.btcc.com | LeveX Quest System | — | Web | N-REWARD-04 Challenge-Based Rewards | 💰 Royal Treasury / War Loot Vault | 2026-05-20 |
| 156 | https://github.com/cobrababy420/extended-signal-bot | Extended Signal Bot | — | GitHub | N-EYES-42 TradFi Correlation Signals | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 157 | https://www.tradingview.com/script/9vS4tTwV/ | AetherEdge Hybrid AI Bias | — | TradingView | N-EYES-43 KNN+NN Hybrid Prediction | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 158 | https://in.tradingview.com/script/laG128wU/ | AetherEdge All-in-One Dashboard | — | TradingView | N-DASH-20 4-Module AI VERDICT | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 159 | https://github.com/Predictly-MCP-Labs/polymarket-btc-5min-15min-arbitrage-bot | Polymarket BTC Arb Bot | — | GitHub | N-HANDS-23 BTC Up/Down CLOB Bot | ⚔️ 03_Kawaleria | 2026-05-20 |
| 160 | https://ojs.aaai.org/index.php/AAAI/article/view/40166 | ArchetypeTrader | — | AAAI 2026 | N-BRAIN-36 RL Archetype Selection | ⚔️ 01_Wywiad | 2026-05-20 |
| 161 | https://github.com/xlabtg/TONAIAgent/issues/103 | TONAIAgent Treasury Layer | — | GitHub | N-TREASURY-02 Autonomous Fiscal Protocol | 💰 Royal Treasury | 2026-05-20 |
| 162 | https://arxiv.org/abs/2503.11499 | Sovereign-OS | — | arXiv | N-TREASURY-03 Charter-Governed Treasury | 💰 Royal Treasury | 2026-05-20 |
| 163 | https://github.com/SilverstreamsAI/NexusFix | NexusFix | — | GitHub | N-HANDS-24 Sub-100ns FIX Engine (4.17M msg/sec) | ⚔️ 03_Kawaleria | 2026-05-20 |
| 164 | https://github.com/zostaff/poly-arbitrage-bot | Polymarket-Kalshi Arb Bot | — | GitHub | N-HANDS-25 Cross-Platform Prediction Arb | ⚔️ 03_Kawaleria | 2026-05-20 |
| 165 | https://thegraph.com | Arkham (The Graph) | — | Web | N-EYES-44 Decentralized On-Chain Indexing | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 166 | https://diadata.org | DIA Oracles | — | Web | N-EYES-45 Multi-Source Redundant Oracle | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 167 | https://dev.to/autarch | Autarch | — | MIT | AI Strategy Evolution, kod deterministyczny | ⚔️ 10_Korpus_Ewolucyjny | 2026-05-20 |
| 168 | https://dev.to/copyleftdev/... | Rugrat | — | MIT | Skaner bytecode EVM ~3 mikrosekundy | ⚔️ FORENSICS | 2026-05-20 |
| 169 | https://devpost.com/software/agentproof-2bmhx0 | AgentProof | — | Noir ZK | Agent udowadnia reputację (win rate, Sharpe) | ⚔️ 11_Inspekcja | 2026-05-20 |
| 170 | https://www.opentrain.ai | Janus-Q | — | arXiv | Event-driven trading, 62.4k artykułów, 75.8% FED | ⚔️ 02_Zwiadowcy / 029_Blyskawiczny_Zwiad | 2026-05-20 |
| 171 | https://arxiv.org/abs/2603.20456 | Neural HMM with AGA | — | arXiv | Samodostosowująca się uwaga HFT | ⚔️ 13_Analiza_Przyczynowa | 2026-05-20 |
| 172 | https://ethglobal.com/showcase/autocfo-s0gwv | AutoCFO | — | ETHGlobal | Autonomiczny CFO dla skarbców DAO | 💰 Royal Treasury | 2026-05-20 |
| 173 | https://ethglobal.com/showcase/dignitas-npwg4 | Dignitas | — | ETHGlobal | Zdecentralizowany protokół reputacji AI | ⚔️ 11_Inspekcja | 2026-05-20 |
| 174 | https://ethglobal.com/showcase/velvet-arc-iqycu | Velvet Arc | — | ETHGlobal | Autonomiczny skarbiec Uniswap V4 | 💰 Royal Treasury | 2026-05-20 |
| 175 | https://jishuzhan.net/article/... | attas | — | Open Source | Framework autonomicznej współpracy agentów | ⚔️ 08_Strategiczny_Sztab | 2026-05-20 |
| 176 | https://www.utusan.com.my | OneBullEx | — | API | Infrastruktura futures AI | ⚔️ 03_Kawaleria | 2026-05-20 |
| 177 | https://www.bitget.com | CoinAnk | — | Skill | Platforma danych order flow | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 178 | https://medium.com/@KingHenry... | Nexus Quant Framework | — | Open Source | Modułowy framework ilościowy | ⚔️ 09_Poligon | 2026-05-20 |
| 179 | https://arxiv.org/abs/2601.05716 | Kalman-Markov Regime Adapter | — | arXiv | Adaptacyjny filtr Kalmana, 3-stanowy Markow | ⚔️ 13_Analiza_Przyczynowa | 2026-05-20 |
| 180 | https://github.com (Foresight Flow) | Foresight Flow | — | arXiv | Wykrywanie świadomego handlu | ⚔️ 02_Zwiadowcy | 2026-05-20 |
| 181 | https://www.manilatimes.net | RedCloud RAID Engine | — | Enterprise | Silnik AI, dane 6.9 mld $ | 🧪 Royal Alchemist | 2026-05-20 |
| 182 | https://markets.businessinsider.com | Toobit Agent Trade Kit | — | Local | Lokalny zestaw narzędzi, pełna prywatność | ⚔️ 07_Saperzy | 2026-05-20 |
| 183 | https://github.com/MeltedMindz/Dexter | Dexter Protocol | — | MIT | AI-powered zarządzanie płynnością DeFi | 💰 Royal Treasury | 2026-05-20 |
| 184 | https://copernical.com | Photonic Neuron HFT | — | Badania | Neuron fotoniczny, pikosekundowe opóźnienia | ⚔️ 15_Fotoniczny_Oddzial | 2026-05-20 |
| 185 | https://github.com/BastianMIllan/UNIAGENT | UniAgent | — | MIT | Autonomiczny handel na 21+ blockchainach | ⚔️ 03_Kawaleria | 2026-05-20 |
| 186 | (plik) ClawOfRedemption.py ✅ na dysku | Claw of Redemption | — | Jack | N-ALCH-05 Claw of Redemption™. Dokumentacja techniczna: `CLAW_OF_REDEMPTION.md` (dostarczone jako .md zamiast .py — do reformatowania w Fazie 2 zgodnie z Zasadą 11) | 🧪 Royal Alchemist / ClawOfRedemption | 2026-05-20 |
| 187 | (plik) Dowodca_Ekspedycji.py ✅ na dysku | Dowódca Ekspedycji | — | Jack | N-EYES-46 Unified Token Analysis™. Dokumentacja techniczna: `Dowodca_ekspedycji_187.md` (dostarczone jako .md zamiast .py — do reformatowania w Fazie 2) | ⚔️ 02_Zwiadowcy / 029_Blyskawiczny_Zwiad | 2026-05-20 |
| 188 | https://github.com/SLMolenaar/orderbook-simulator-cpp | Orderbook Simulator C++ | — | GitHub | Silnik order book 2.7M orders/sec | ⚔️ 09_Poligon | 2026-05-20 |
| 189 | https://github.com/0xC0FFEE-sudo/HydraFlow-X | HydraFlow-X | — | GitHub | Sub-50μs order-to-wire, DPDK kernel-bypass | ⚔️ 03_Kawaleria | 2026-05-20 |
| 190 | https://github.com/1024Foundation/1024Chain | 1024Chain | — | GitHub | Fork Solany zoptymalizowany pod trading | ⚔️ 03_Kawaleria | 2026-05-20 |
| 191 | https://github.com/joaquinbejar/otc-rfq | OTC RFQ Engine | — | GitHub | Sub-milisekundowa agregacja płynności OTC | ⚔️ 03_Kawaleria | 2026-05-20 |
| 192 | https://papers.cool/arxiv/2605.12532 | AgenticAITA | — | arXiv | Architektura deliberatywna 3 agentów LLM | ⚔️ 08_Sztab + 🗺️ War Council | 2026-05-20 |
| 193 | https://github.com/Open-Finance-Lab/AgenticTrading | AgenticTrading | — | GitHub | Agentowy ekosystem: DAG Planner + pule agentów | ⚔️ 08_Sztab + 🗺️ War Council | 2026-05-20 |
| 194 | https://ethglobal.com/showcase/shawarma-orchestrate | Shawarma Orchestrate | — | ETHGlobal | Supervisor agent + rój z konsensusem | ⚔️ 08_Sztab + 🗺️ War Council | 2026-05-20 |
| 195 | https://github.com/AI4Finance-Foundation/FinRL-Trading | FinRL-X | — | GitHub | AI-native modułowa infrastruktura quant | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 196 | https://github.com/skyliquid22/Quanto | Quanto | — | GitHub | Deterministyczny pipeline RL z audytowalnym manifestem | ⚔️ 00_Sztab | 2026-05-20 |
| 197 | https://github.com/0xcherry/OpenAlice | OpenAlice | — | GitHub (3.1k⭐) | Lokalny agent AI z pamięcią kognitywną | 👑 Car Pixel | 2026-05-20 |
| 198 | https://github.com/TradingGoose/TradingGoose-Studio | TradingGoose Studio | — | GitHub | Platforma AI workflow dla LLM tradingu | ⚔️ 06_Dowodztwo + 👁️ Throne Room | 2026-05-20 |
| 199 | https://github.com/wolfdevil666/kalshi-neural-predictor | Kalshi Neural Predictor | — | GitHub | Sieć neuronowa na 11,400+ zdarzeniach | ⚔️ 01_Wywiad | 2026-05-20 |
| 200 | https://github.com/ivanvgreiff/gamma-scalping-algorithm | Gamma Scalping Algorithm | — | GitHub | Pełna implementacja gamma scalping (BTC/Deribit) | ⚔️ 03_Kawaleria | 2026-05-20 |
| 201 | (plik) nexgen_hub.py | NexGenHub — Samoświadomy Multi-Exchange Core | — | Jack | N-CORE-05, Replikacyjny routing, Virtual OrderBook, 3-tier health | ⚔️ 00_Sztab_Generalny | 2026-05-22 |
| 202 | (plik) metacortex.py | MetaCortex — Samodoskonalący się Agent z Meta-Learningiem | — | Jack | N-BRAIN-26, Aktor-Sędzia-MetaSędzia, Debata MoA, StrategyEvolution | ⚔️ 01_Wywiad | 2026-05-22 |
| 203 | (plik) omnisight.py | OmniSight — Bayesian Fusion Engine | — | Jack | N-EYES-28, Bayesian Fusion On-Chain+OrderBook, WhaleDetector | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 204 | (plik) warlancer.py | WarLancer — High-Frequency Execution Engine | — | Jack | N-HANDS, Sub-500ms execution, Smart Order Routing, Failover Protection | ⚔️ 03_Kawaleria | 2026-05-22 |
| 205 | (plik) aegis_shield.py | AegisShield — Multi-Layer Risk Engine | — | Jack | N-SHIELDS-14, 3-tier drawdown, Circuit Breaker, Daily Loss Limit | ⚔️ 04_Gwardia_Przyboczna | 2026-05-22 |
| 206 | (plik) mnemosyne.py | Mnemosyne — Memory & Trade Learning Record System | — | Jack | N-MEM-04, Trade Learning Record, BookOfFlaws, Persistent Memory | ⚔️ 05_Archiwum | 2026-05-22 |
| 207 | (plik) warroom.py | WarRoom — Dashboard & Command Center | — | Jack | N-DASH, Real-time monitoring 7 botów, Telegram Alerts, Performance Dashboard | ⚔️ 06_Dowodztwo | 2026-05-22 |
| 208 | (plik) toolforge.py | ToolForge — IndicatorFactory v4 + API Toolkit | — | Jack | N-TOOLS, RSI, MACD, BB, ATR, Supertrend, 22 SignalGenerator | ⚔️ 07_Saperzy | 2026-05-22 |
| 209 | (plik) titanmind.py | TitanMind — Strategy Orchestrator & Scheduler | — | Jack | N-ORCH, Strategy Scheduler, Conflict Resolver, Resource Allocator | ⚔️ 08_Strategiczny_Sztab | 2026-05-22 |
| 210 | (plik) valhalla.py | Valhalla — Backtesting & Simulation Arena | — | Jack | N-BACK, Walk-Forward, Monte Carlo 1000 sim, Sharpe/Sortino/Calmar | ⚔️ 09_Poligon_Bojowy | 2026-05-22 |
| 211 | https://github.com/microsoft/qlib | Qlib (Microsoft) | 16k | MIT | N-BACK – AI-specyficzny framework quant, Sharpe +30% vs obecny backtesting | ⚔️ 09_Poligon_Bojowy | 2026-05-22 |
| 212 | https://github.com/vnpy/vnpy | vnpy | 25k | MIT | N-CORE – kompletna platforma tradingowa Python, wspiera MEXC, OKX, Binance | ⚔️ 00_Sztab_Generalny | 2026-05-22 |
| 213 | https://github.com/jindaxiang/akshare | akshare | 9k | MIT | N-EYES – darmowe API do danych finansowych (A-shares, crypto, macro) | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 214 | https://github.com/MtkN1/pybotters | pybotters | — | MIT | N-CORE – japoński async framework multi-exchange, bitFlyer, Liquid | ⚔️ 03_Kawaleria | 2026-05-22 |
| 215 | (model) Qwen2.5 (Alibaba) | Qwen2.5 — Lokalny LLM | — | Apache-2.0 | N-BRAIN – potencjalny fallback dla Ollama, lepszy od DeepSeek na chińskich danych | ⚔️ 01_Wywiad | 2026-05-22 |
| 216 | (plik) kameleon_protocol.py | Kameleon Protocol — Samoświadomość i Adaptacja w RT | — | Jack | N-BRAIN-37, automatyczna zmiana taktyki przy zmianie reżimu, redukcja dźwigni, odsuwanie niesprawnych modułów | ⚔️ 01_Wywiad | 2026-05-22 |
| 217 | (plik) fews.py | FEWS — Fraud Early Warning System | — | Jack | N-EYES-48, przedbitewny zwiad saperski, blokada zaminowanych aktywów (wash trading, honeypot, koncentracja) | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 218 | (plik) dir_protocol.py | DIR Protocol — Decision Intelligence Runtime | — | Jack | N-HANDS-26, oddzielenie intencji od egzekucji, walidacja w piaskownicy, egzekucja atomowa (idempotentność) | ⚔️ 03_Kawaleria | 2026-05-22 |
| 219 | (plik) black_swan_protocol.py | Black Swan Protocol — Tryb CODE_RED | — | Jack | N-SHIELDS-15, detekcja zdarzeń ekstremalnych, Emergency Exit, Market Flatten, Lockdown | ⚔️ 04_Gwardia_Przyboczna | 2026-05-22 |
| 220 | (plik) spoofing_detector.py | Spoofing Detector — Wykrywanie Fałszywych Ścian | — | Jack | N-EYES-47, identyfikacja zleceń-widm, pomiar czasu życia ściany, ignorowanie spoofingu | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 221 | (plik) hybrid_forge.py | Hybrid Forge — Kuźnia Hybryd | — | Jack | N-BACK-18, łączenie weteranów z nowymi modułami, testowanie kombinacji stare+nowe, Cykl Wiecznego Ulepszania | ⚔️ 09_Poligon_Bojowy | 2026-05-22 |
| 222 | (plik) red_team_protocol.py | Red Team Protocol — Czerwona Drużyna | — | Jack | N-RED-01, wewnętrzna jednostka ofensywna, symulowane ataki na własne strategie, szukanie luk | ⚔️ RED_TEAM | 2026-05-22 |
| 223 | (plik) global_social_intelligence_hub.py | N-EYES-49 GLOBAL SOCIAL INTELLIGENCE HUB™ | — | Jack | Multi-Platform Trader Monitor, Trader TrustScore, Ecosystem & Category Mapper (wszystkie kategorie), Historical Price & Correlation Engine, New Project Scout, VIP & Smart Money Tracker (Zasada 46) | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 224 | (plik) vip_global_elite_watcher.py | N-EYES-50 VIP & GLOBAL ELITE WATCHER™ | — | Jack | Global VIP Registry, Portfolio Watcher, Movement vs. Words, Correlation Engine, Commander Alert | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 225 | (plik) sanctum_vault.py | N-KEEP-01 SANCTUM VAULT™ | — | Jack | Bezpieczne przechowywanie kluczy API, seed phrases. AES-256-GCM. Zero dostępu z zewnątrz. | 🏰 The Keep / Sanctum | 2026-05-22 |
| 226 | (plik) the_wall.py | N-KEEP-02 THE WALL™ | — | Jack | Firewall aplikacyjny. Monitorowanie podejrzanych requestów, rate limiting, detekcja ataków. | 🏰 The Keep / Wall | 2026-05-22 |
| 227 | (plik) the_moat.py | N-KEEP-03 THE MOAT™ | — | Jack | Izolacja środowisk. Sandbox dla testowania. Separacja live od test. | 🏰 The Keep / Moat | 2026-05-22 |
| 228 | (plik) the_watchers.py | N-KEEP-04 THE WATCHERS™ | — | Jack | 24/7 monitoring anomalii systemowych. Wycieki pamięci, spadki wydajności. | 🏰 The Keep / Watchers | 2026-05-22 |
| 229 | (plik) tax_guardian.py | N-GUARD-01 TAX GUARDIAN™ | — | Jack | Automatyczne obliczanie podatku od zysków. Raporty podatkowe. Śledzenie kosztów. | 🛡️ Royal Guard / Tax Guardian | 2026-05-22 |
| 230 | (plik) compliance_checker.py | N-GUARD-02 COMPLIANCE CHECKER™ | — | Jack | Zgodność z regulaminem MEXC i przyszłych giełd. Wykrywanie potencjalnych naruszeń. | 🛡️ Royal Guard / Compliance Checker | 2026-05-22 |
| 231 | (plik) valkyrie_engine.py | N-GUARD-03 VALKYRIE ENGINE™ | — | Jack | Zaawansowana analiza ryzyka. Stress testy, VaR, CVaR. | 🛡️ Royal Guard / Valkyrie Risk Engine | 2026-05-22 |
| 232 | (plik) drawdown_sentinel.py | N-GUARD-04 DRAWDOWN SENTINEL™ | — | Jack | Aktywny strażnik drawdownu. Analiza tempa spadku, nie tylko progu. | 🛡️ Royal Guard / Drawdown Guardian | 2026-05-22 |
| 233 | (plik) panic_button.py | N-GUARD-05 PANIC BUTTON™ | — | Jack | Fizyczny lub cyfrowy przycisk. Zamyka wszystkie pozycje, lockdown. | 🛡️ Royal Guard / Emergency Exit | 2026-05-22 |
| 234 | (plik) ally_registry.py | N-DIP-01 ALLY REGISTRY™ | — | Jack | Rejestr zaufanych instancji Tytan-α. Klucze publiczne, historia współpracy. | 🤝 Diplomacy / Allies | 2026-05-22 |
| 235 | (plik) secure_route.py | N-DIP-02 SECURE ROUTE™ | — | Jack | Szyfrowane kanały FMT między instancjami. Wymiana modeli. | 🤝 Diplomacy / Trade_Routes | 2026-05-22 |
| 236 | (plik) treaty_ledger.py | N-DIP-03 TREATY LEDGER™ | — | Jack | Rejestr traktatów. Warunki współpracy, podział zysków, klauzule. | 🤝 Diplomacy / Treaties | 2026-05-22 |
| 237 | (plik) treasury_vault.py | N-VAULT-01 TREASURY VAULT™ | — | Jack | Wielowarstwowy system przechowywania kapitału. Hot/Medium/Cold vaults. | 💰 Royal Treasury / vaults | 2026-05-22 |
| 238 | (plik) genetic_breeder.py | N-EVO-01 GENETIC BREEDER™ | — | Jack | Algorytmy genetyczne. Krzyżowanie strategii, selekcja naturalna. | ⚔️ 10_Korpus_Ewolucyjny | 2026-05-22 |
| 239 | (plik) audit_trail_engine.py | N-VERIFY-05 AUDIT TRAIL ENGINE™ | — | Jack | Automatyczne raporty audytowe. Gotowe dla Oka Stratega (Zasada 33). | ⚔️ 11_Inspekcja | 2026-05-22 |
| 240 | (plik) swarm_coordinator.py | N-ROJ-02 SWARM COORDINATOR™ | — | Jack | Koordynacja 50+ agentów. Dynamiczny podział zadań, konsensus. | ⚔️ 12_Roj | 2026-05-22 |
| 241 | (plik) quantum_inspired_optimizer.py | N-QC-01 QUANTUM INSPIRED OPTIMIZER™ | — | Jack | Algorytmy inspirowane kwantowo. Optymalizacja portfela i selekcji strategii. | ⚔️ 14_Kwantowy_Korpus | 2026-05-22 |
| 242 | (plik) photonic_latency_monitor.py | N-PH-01 PHOTONIC LATENCY MONITOR™ | — | Jack | Monitorowanie i optymalizacja latencji. Wykrywanie mikrosekundowych opóźnień. | ⚔️ 15_Fotoniczny_Oddzial | 2026-05-22 |
| 243 | (plik) agent_insurance_protocol.py | N-SHIELDS-16 AGENT INSURANCE PROTOCOL™ | — | Jack | Autonomiczne ubezpieczanie transakcji. RiskScore Calculator, Insurance Offer Engine, Insurance Vault Manager, Claim Payout Engine, Multi-Agent Reinsurance, Insurance Ledger. Zasada 47. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-22 |
| 244 | (plik) cognitive_swarm_intelligence.py | N-ROJ-03 COGNITIVE SWARM INTELLIGENCE™ | — | Jack | Contextual Trust Engine, Digital Pheromone System (ACO/Stigmergy), Explore-Exploit Balancer (Bee Algorithm), Collective Learning Engine, Swarm Memory, Emergence Detector. Zasada 48. | ⚔️ 12_Roj | 2026-05-22 |
| 245 | (plik) copy_trade_deep_analyzer.py | N-EYES-51 COPY-TRADE DEEP ANALYZER™ | — | Jack | Trader DNA Profiler, Historical P&L Audit, Risk Appetite Classifier, Strategy Pattern Recognition, Psychological Fingerprint, Simulation Engine (Valhalla), Correlation Matrix, Copy Decision Engine (FOLLOW/WATCH/AVOID). Zasada 47. | ⚔️ 02_Zwiadowcy | 2026-05-22 |
| 246 | (plik) mexc_compliance_engine.py | N-SHIELDS-17 MEXC COMPLIANCE ENGINE™ | — | Jack | Monitorowanie limitów API (12 zleceń/sek, 500 żądań/10s). Walidacja KYB. Blokada wash-tradingu i spoofingu. Alertowanie o zbliżaniu się do limitów. Zgodność z Kodeksem Pola Bitwy MEXC. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-22 |
| 247 | (plik) fee_optimizer.py | N-TOOLS-32 FEE OPTIMIZER™ | — | Jack | Automatyczny wybór między Market a Post-Only (oszczędność 33% na prowizjach API futures). Kalkulacja oszczędności. Monitorowanie promocji 0-fee MEXC. Rekomendacje holdingowe MX Token dla zniżek. | ⚔️ 07_Saperzy | 2026-05-22 |
| 248 | (plik) nexus_grid.py | N-CORE-08 NEXUS GRID™ | — | Jack | Rozproszona siatka dowodzenia z shardingiem. Eliminuje wąskie gardło komunikacyjne przy 1152 wskaźnikach i 8 botach. | ⚔️ 00_Sztab_Generalny | 2026-05-23 |
| 249 | (plik) war_chain.py | N-CORE-09 WAR CHAIN PROTOCOL™ | — | Jack | Zapasowy łańcuch dowodzenia na wypadek awarii głównego EventBusa. Aktywuje się po 5s braku odpowiedzi. | ⚔️ 00_Sztab_Generalny | 2026-05-23 |
| 250 | (plik) sequencer.py | N-CORE-10 SEQUENCER ENGINE™ | — | Jack | Deterministyczny sekwencer zdarzeń z niezmiennym logiem (Event Sourcing). | ⚔️ 00_Sztab_Generalny | 2026-05-23 |
| 251 | (plik) dist_orchestrator.py | N-CORE-11 DISTRIBUTED ORCHESTRATOR™ | — | Jack | Rozproszony orkiestrator agentów z replikacją stanu i automatycznym przełączaniem awaryjnym. | ⚔️ 00_Sztab_Generalny | 2026-05-23 |
| 252 | (plik) intelligent_composer.py | N-CORE-12 INTELLIGENT COMPOSER™ | — | Jack | Dynamiczny graf zależności między modułami. Predykcyjne ładowanie klocków LEGO. (Zasada 59) | ⚔️ 00_Sztab_Generalny | 2026-05-23 |
| 253 | (plik) intent_engine.py | N-BRAIN-43 INTENT ENGINE™ | — | Jack | Rozumie intencje Komendanta, nie tylko słowa. Buduje model preferencji użytkownika. | ⚔️ 01_Wywiad | 2026-05-23 |
| 254 | (plik) resilience_engine.py | N-BRAIN-44 RESILIENCE ENGINE™ | — | Jack | Monitoruje zachowanie botów pod kątem "emocjonalnych" błędów (overtrading, revenge trading, FOMO). Automatycznie koryguje strategię. | ⚔️ 01_Wywiad | 2026-05-23 |
| 255 | (plik) shadow_sight.py | N-EYES-53 SHADOW SIGHT™ | — | Jack | Noktowizor. Widzenie "przez ścianę". Wykrywanie ukrytej płynności, dark pooli i akumulacji. | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 256 | (plik) mass_psychology_engine.py | N-EYES-57 MASS PSYCHOLOGY ENGINE™ | — | Jack | Psychologia tłumu. Panika jako okazja, euforia jako ostrzeżenie. FOMO ratio. (Zasada 55) | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 257 | (plik) market_storyteller.py | N-EYES-58 MARKET STORYTELLER™ | — | Jack | Tłumaczy surowe liczby na płynną, ludzką opowieść. Zasila LEGIONA głosem i narracją. | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 258 | (plik) cultural_behavioral_engine.py | N-EYES-59 CULTURAL BEHAVIORAL ENGINE™ | — | Jack | Analiza wpływu kultury i regionu na decyzje traderów. (Zasada 58) | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 259 | (plik) battle_chronicler.py | N-MEM-07 BATTLE CHRONICLER™ | — | Jack | Łączy dane historyczne z teraźniejszością. Automatycznie wyszukuje analogie i generuje raporty przyczynowo-skutkowe. | ⚔️ 05_Archiwum | 2026-05-23 |
| 260 | (plik) the_radar.py | N-DASH-21 THE RADAR™ | — | Jack | Wielowymiarowa wizualizacja pola bitwy. Okręgi radarowe centrów dowodzenia, punkty zapalne, konfluencje wskaźników. | ⚔️ 06_Dowodztwo | 2026-05-23 |
| 261 | (plik) titan_whale_detector.py | N-TOOLS-34 TITAN WHALE DETECTOR™ | — | Jack | Autorska adaptacja koncepcji Big Guy (Pifagor Trade). Wykrywanie wejścia dużych graczy przez spike'i cenowe i wolumenowe. | ⚔️ 07_Saperzy | 2026-05-23 |
| 262 | (plik) oko_prawdy.py | N-TOOLS-1001 OKO PRAWDY™ | — | Jack | **Oryginalny Jack.** Trójwymiarowa Analiza Intencji (Impuls + Reakcja + Inercja). Metryka Prawdy 0-100. Widzi, czy ruch jest autentyczny, czy iluzją. | ⚔️ 07_Saperzy | 2026-05-23 |
| 263 | (plik) darvas_box.py | N-TOOLS-1002 DARVAS BOX™ | — | Jack | Automatyczne strefy akumulacji. Adaptacja metody Nicolasa Darvasa. Sygnał przy wybiciu z boxu. | ⚔️ 07_Saperzy | 2026-05-23 |
| 264 | (plik) grand_indicator_library.py | N-TOOLS-33 GRAND INDICATOR LIBRARY™ | — | Jack | **Enigma.** Centralna biblioteka 1152 wskaźników. Katalogowanie na kluczach cyfrowych. System STANDBY dla nieużywanych wskaźników. | ⚔️ 07_Saperzy | 2026-05-23 |
| 265 | (plik) deterministic_mesh.py | N-CORE-13 DETERMINISTIC EVENT MESH™ | 🥈 Perła | Jack | Nanosekundowy determinizm zdarzeń mikrostrukturalnych. Rozszerza Sequencer Engine o przetwarzanie zdarzeń tickowych z absolutną precyzją czasową. | ⚔️ 00_Sztab_Generalny | 2026-05-23 |
| 266 | (plik) crisis_alpha_engine.py | N-BRAIN-46 CRISIS ALPHA ENGINE™ | 🥈 Perła | Jack | Kontratak w kryzysie. Sharpe 2.8, Beta -0.03. Aktywuje się przy Pulse Score > 60, zarabia na mean-reversion w ekstremalnej zmienności. | ⚔️ 01_Wywiad | 2026-05-23 |
| 267 | (plik) triphase_execution.py | N-BRAIN-47 TRIPHASE EXECUTION ENGINE™ | 🥇 Złoto | Jack | Trójfazowa adaptacja dzienna: Equator Grid (konsolidacja), Momentum Breakout (wybicie), Reversal Gravity (wyczerpanie). | ⚔️ 01_Wywiad | 2026-05-23 |
| 268 | (plik) bayga_optimizer.py | N-BRAIN-48 BAYGA OPTIMIZER™ | 🥇 Złoto | Jack | Hybryda optymalizacji Bayesowskiej (TPE) i algorytmu genetycznego (DE). Auto-znajdowanie najlepszych parametrów strategii. | ⚔️ 01_Wywiad | 2026-05-23 |
| 269 | (plik) liquidity_sweep_master.py | N-BRAIN-49 LIQUIDITY SWEEP MASTER™ | 🥇 Złoto | Jack | Polowanie na liquidity sweep i powrót do zakresu. Max 2% ryzyka. "Survival first, profit second." | ⚔️ 01_Wywiad | 2026-05-23 |
| 270 | (plik) modular_stacking_engine.py | N-BRAIN-50 MODULAR STACKING ENGINE™ | 🥇 Złoto | Jack | Łączenie wielu niezależnie zweryfikowanych mikromodułów w jeden system. Wzorzec z IMC Prosperity 4 (4. globalnie, 1. Europa). | ⚔️ 01_Wywiad | 2026-05-23 |
| 271 | (plik) davey_validation_engine.py | N-BRAIN-51 DAVEY VALIDATION ENGINE™ | 🥇 Złoto | Jack | Walk-Forward + Monte Carlo Multi-Algo. Trzykrotny medalista World Cup of Futures Trading (148%, 107%, 112%). | ⚔️ 01_Wywiad | 2026-05-23 |
| 272 | (plik) institutional_footprint.py | N-BRAIN-52 INSTITUTIONAL FOOTPRINT TRACKER™ | 💎 Diament | Jack | Śledzenie śladów instytucji + AI pattern recognition. Wzorzec: Inna Rosputnia (715.2% kwartalny World Cup). | ⚔️ 01_Wywiad | 2026-05-23 |
| 273 | (plik) pulse_engine.py | N-EYES-60 PULSE ENGINE™ (EKG Rynku) | 🥈 Perła | Jack | Wykrywanie arytmii rynkowej. Pulse Score 0-100. Integruje dane z mikrostruktury, psychologii tłumu i zmienności. | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 274 | (plik) trapped_trader_detector.py | N-EYES-61 TRAPPED TRADER DETECTOR™ | 🥇 Złoto | Jack | Czytanie "uwięzionych" traderów przez Order Flow. Wzorzec: Fabio Valentini (218% w 3 miesiące, 4x finalista World Cup). | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 275 | (plik) neural_correlation_engine.py | N-EYES-62 NEURAL CORRELATION ENGINE™ | 🥈 Perła | Jack | Znajdowanie ukrytych korelacji między aktywami. Masywnie równoległe przetwarzanie. | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 276 | (plik) manifold_market_mapper.py | N-EYES-63 MANIFOLD MARKET MAPPER™ | 🥈 Perła | Jack | Osadzanie rynku na rozmaitościach geometrycznych (torus). Wykrywanie ukrytych struktur cyklicznych. | ⚔️ 02_Zwiadowcy | 2026-05-23 |
| 277 | (plik) impossible_hunter.py | N-BRAIN-058 THE IMPOSSIBLE HUNTER™ | 💎 Diament | Jack | Łowca Niemożliwego – poluje na odwrócenia trendu tylko przy ekstremalnej konfluencji (Pulse Score > 80, Trapped Trader, Spectral Cycle). Wąski SL, mała pozycja. | ⚔️ 01_Wywiad | 2026-05-24 |
| 278 | (plik) dynamic_sector_rotation.py | N-BRAIN-063 DYNAMIC SECTOR ROTATION | 🥇 Złoto | Jack | Dynamiczna rotacja sektorowa – śledzi przepływ kapitału między sektorami (AI, DeFi, RWA) i automatycznie przesuwa alokację. | ⚔️ 01_Wywiad | 2026-05-24 |
| 279 | (plik) momentum_crash_protection.py | N-SHIELDS-021 MOMENTUM CRASH PROTECTION | 💎 Diament | Jack | Ochrona przed krachem momentum – wykrywa oznaki zbliżającego się krachu i natychmiast przełącza boty w tryb defensywny. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-24 |
| 280 | (plik) kingdom_alert_central.py | N-DASH-022 KINGDOM ALERT CENTRAL™ | — | Jack | Scentralizowane centrum alarmowe z 5 poziomami (CODE BLACK/RED/ORANGE/YELLOW/BLUE). Agreguje alerty ze wszystkich modułów. | ⚔️ 06_Dowodztwo | 2026-05-24 |
| 281 | (plik) the_war_table.py | N-DASH-023 THE WAR TABLE™ | — | Jack | Żywy stół wojenny – wizualizuje przepływy kapitału, pozycje botów, alerty i decyzje na żywo w Komnacie Tronowej. | ⚔️ 06_Dowodztwo | 2026-05-24 |
| 282 | (plik) the_holosphere.py | N-DASH-024 THE HOLOSPHERE™ | — | Jack | Trójwymiarowe centrum dowodzenia 360° – strategiczna wizualizacja Królestwa z pełnym zanurzeniem. | ⚔️ 06_Dowodztwo | 2026-05-24 |
| 283 | (plik) hft_micro_sweep.py | N-HANDS-031 HFT MICRO-SWEEP ENGINE™ | 🥇 Złoto | Jack | Mikro-skalpowane wyjście HFT – zamyka 25% pozycji na pierwszym mikro-ruchu, zwiększając win rate. | ⚔️ 03_Kawaleria | 2026-05-24 |
| 284 | (plik) shap_explainability.py | N-VERIFY-006 SHAP EXPLAINABILITY ENGINE™ | 💎 Diament | Jack | Wyjaśnialność decyzji AI – rozkłada każdą prognozę na czynniki pierwsze (SHAP). Wymóg instytucjonalny. | ⚔️ 11_Inspekcja | 2026-05-24 |
| 285 | (plik) demark_td_sequential.py | Tom DeMark TD Sequential | 💎 Diament | Open Source | Wyrocznia Wyczerpania Trendu – sekwencje 9 zamknięć, punkty zwrotne z 68.8% skutecznością. | ⚔️ 07_Saperzy | 2026-05-24 |
| 286 | (plik) kase_devstops.py | Kase DevStops | 🥇 Złoto | Open Source | Tarcza Statystyczna – 4 dynamiczne poziomy stop-loss oparte na odchyleniu ATR. | ⚔️ 07_Saperzy | 2026-05-24 |
| 287 | (plik) classic_indicators_1.py | Pakiet 4 klasycznych wskaźników | 🥇 Złoto | Open Source | CBCI (Lustro RSI), GAPO (Sejsmograf), MAMA (Królowa Adaptacji), ZBT (Młot Thora). | ⚔️ 07_Saperzy | 2026-05-24 |
| 288 | (plik) classic_indicators_2.py | Pakiet 4 nowoczesnych wskaźników | 🥇 Złoto | Open Source | STC (Fuzja MACD), Delta Void (Mapa Płynności), Non-Causality Suite, Rare-Zone Bottom. | ⚔️ 07_Saperzy | 2026-05-24 |
| 289 | (plik) trend_scope_engine.py | N-TOOLS-1170 TREND SCOPE ENGINE™ | 🥇 Złoto | Jack | Japońska metoda analizy prawdopodobieństwa trendu z integracją depth-of-market. Adaptacja z platformy Gogojungle "AI Optimal KING". | ⚔️ 07_Saperzy | 2026-05-24 |
| 290 | (plik) liquidity_gap_detector.py | N-EYES-065 LIQUIDITY GAP DETECTOR™ | 🥇 Złoto | Jack | Wykrywanie luk płynności, ukrytych ścian i sweep eventów na głównych giełdach. Koreańska metoda z crypto-liquidity-ai-trading-bot. | ⚔️ 02_Zwiadowcy | 2026-05-24 |
| 291 | (plik) hft_orderbook_predictor.py | N-BRAIN-065 HFT ORDERBOOK PREDICTOR™ | 💎 Diament | Jack | Predykcja dynamiki księgi zleceń na danych poziomu II (depth trade i quote data). Ensemble klasyfikatorów (RF, XGBoost, LSTM). 575⭐ na GitHub. | ⚔️ 01_Wywiad | 2026-05-24 |
| 292 | (plik) deliberative_loop.py | N-BRAIN-066 DELIBERATIVE LOOP PROTOCOL™ | 💎👑 Diament w Koronie | Jack | W pełni autonomiczna pętla decyzyjna bez treningu offline. Adaptive Z-Score Trigger. Inference Gating Protocol. 157 autonomicznych interwencji w 5 dni. | ⚔️ 01_Wywiad | 2026-05-24 |
| 293 | (plik) risk_first_protocol.py | N-BRAIN-067 RISK-FIRST PROTOCOL™ | 💎 Diament | Jack | Matematyczny filtr bezpieczeństwa dla sygnałów LLM. Odrzuca halucynacje, kara za niebezpieczną ekspozycję, deterministyczny circuit breaker. Cambridge, maj 2026. | ⚔️ 01_Wywiad | 2026-05-24 |
| 294 | (plik) multi_indicator_rl.py | N-BRAIN-068 MULTI-INDICATOR RL AGENT™ | 💎 Diament | Jack | Adaptacyjne zarządzanie portfelem z wielowskaźnikowymi danymi technicznymi i A2C. Testowany na 23 latach danych S&P 500. Guangdong University of Finance. | ⚔️ 01_Wywiad | 2026-05-24 |
| 295 | (plik) options_flow.py | N-EYES-066 OPTIONS FLOW ANALYZER™ | 💎 Diament | Jack | Sygnały z rynku opcji BTC/ETH (Deribit, $31 mld): gamma, skew, put-call ratio, open interest. Wykrywanie gamma squeeze. | ⚔️ 02_Zwiadowcy | 2026-05-24 |
| 296 | (plik) nexus_grid_nautilus.py | N-CORE-08 NEXUS GRID™ (Implementacja) | 🛡️ Infrastruktura | Jack | Rozproszony EventBus oparty na architekturze NautilusTrader (Rust core + Python orchestration). Nanosekundowa deterministyczność, Redis-backed state, identyczna semantyka backtest/live. | ⚔️ 00_Sztab_Generalny | 2026-05-24 |
| 297 | (plik) adaptive_opro.py | ADAPTIVE-OPRO Protocol (Rozszerzenie LEGIONA) | 💎 Diament | Jack | Dynamiczna optymalizacja promptów w czasie rzeczywistym. Adaptive-OPRO, National Technical University of Athens, maj 2026. | ⚔️ 01_Wywiad | 2026-05-24 |
| 298 | (dokument) multi_asset_expansion.md | AriseAlpha + KX Temporal AI + IonQ Quantum | 🥇 Złoto | Dokumentacja | Rozszerzenie N-CORE-07 o akcje i forex. GPU-przyspieszone wyszukiwanie wektorowe (KX+NVIDIA). Kwantowa optymalizacja portfela (IonQ BF-DCQO). | 📋 Do klasyfikacji | 2026-05-24 |
| 299 | (plik) resurrection_engine.py | N-BRAIN-069 THE RESURRECTION ENGINE™ | 💎 Diament | Jack | Automatyczny łowca zapomnianych konfiguracji. Regularnie łączy strategie z Cmentarza z nowymi wskaźnikami, testuje je na Valhalla Arena i zgłasza odkrycia. | 🧪 Royal Alchemist | 2026-05-24 |
| 300 | (plik) crucible_gatekeeper.py | N-BRAIN-070 THE CRUCIBLE GATEKEEPER™ | 🥇 Złoto | Jack | Inteligentny filtr stojący między Kuźnią a Centrum Dowodzenia. Przepuszcza tylko strategie o statystycznie istotnej przewadze. | 🧪 Royal Alchemist | 2026-05-24 |
| 301 | (plik) signal_orchestrator.py | N-BRAIN-071 THE SIGNAL ORCHESTRATOR™ | 💎 Diament | Jack | Dynamiczne ważenie, kategoryzacja i priorytetyzacja sygnałów (Grade A/B/C) na podstawie skuteczności, konsensusu i kontekstu taktycznego. Zasada 72. | ⚔️ 01_Wywiad | 2026-05-24 |
| 302 | (plik) alchemist_prep_lab.py | N-DATA-03 THE ALCHEMIST'S PREP LAB™ | 💎 Diament | Jack | Automatyczne pobieranie, czyszczenie, normalizacja i feature engineering danych z Chronicle Engine dla Kuźni Alchemika. | 📚 Great Library | 2026-05-24 |
| 303 | (plik) venture_capital_allocator.py | N-TREASURY-05 THE VENTURE CAPITAL ALLOCATOR™ | 🥇 Złoto | Jack | Alokator kapitału wysokiego ryzyka. Tworzy Fundusz Eksploracyjny (5-10% zysków) i finansuje testowanie nowych strategii na żywo. | 💰 Royal Treasury | 2026-05-24 |
| 304 | (plik) predictive_breakout_engine.py | N-TOOLS-1171 PREDICTIVE BREAKOUT ENGINE™ | 🥇 Złoto | Jack | Predykcyjny silnik wybić ML. Mapuje instytucjonalną strukturę rynku i oblicza statystyczne prawdopodobieństwo nadchodzących wybić. Adaptacja z GainzAlgo. | ⚔️ 07_Saperzy | 2026-05-24 |
| 305 | (plik) adaptive_vwap_engine.py | N-TOOLS-1172 ADAPTIVE VWAP ENGINE™ | 🥇 Złoto | Jack | Adaptacyjna średnia krocząca z dynamicznym alpha opartym na Efficiency Ratio (ER) i VWAP. Automatycznie redukuje fałszywe sygnały. | ⚔️ 07_Saperzy | 2026-05-24 |
| 306 | (plik) backtest_integrity_guardian.py | N-SHIELDS-023 THE BACKTEST INTEGRITY GUARDIAN™ | 💎 Diament | Jack | Automatyczny strażnik integralności backtestów. Wykrywa look-ahead bias, survivorship bias i wystawia Certyfikat Integralności. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-24 |
| 307 | (plik) strategy_lifecycle_manager.py | N-SHIELDS-024 THE STRATEGY LIFECYCLE MANAGER™ | 🥇 Złoto | Jack | Monitoruje 'starzenie się' strategii. Automatycznie przenosi je przez cykl: Aktywna → Monitorowana → Rezerwowa → Cmentarz → Archiwum Weteranów. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-24 |
| 308 | (dokument) dominion_score_v3.md | DOMINION SCORE™ v3.0 (360°) | 👑 PLATINUM SUPREME | Jack | Nowa metryka potęgi Królestwa. Ocenia 36 wymiarów w 6 mega-filarach. Wynik: 325.5/360 (90.4%). Zastępuje THOR SCORE™. | 🏰 Castle Pixel | 2026-05-24 |
| 309 | (dokument) projekt_chimera_karta.md | Karta Projektu 'Chimera' — Modele Cara i Carycy | 💎 Diament | Jack | Oficjalna dokumentacja składu modeli AI. Car: SmolLM3-3B + DeepScaleR-1.5B + Qwen3-0.6B. Caryca: Qwen3.5-4B. | 📂 Car Pixel | 2026-05-24 |
| 310 | (dokument) artefakty_alchemika.md | 7 Artefaktów Kuźni Alchemika | 💎 Diament | Jack | Dokumentacja 7 artefaktów: CogAlpha, SHARP, FactorEngine, FactorMiner, Hubble, AutoQuant, JaxMARL-HFT. | 🧪 Royal Alchemist | 2026-05-24 |
| 311 | (plik) imperial_arena.py | N-EVO-03 THE IMPERIAL ARENA™ | 💎👑 Diament w Koronie | Jack | Cykliczne igrzyska bojowe. Trójfazowy turniej (Trening → Eliminacje → Finał). Mechanizm genetyczny krzyżujący DNA strategii. Zgodny z Zasadą 74. | 🏟️ 10_Korpus_Ewolucyjny | 2026-05-24 |
| 312 | (plik) adaptive_hedge_guardian.py | N-SHIELDS-025 ADAPTIVE HEDGE GUARDIAN™ | 💎 Diament | Jack | Adaptacyjny hedging HRL z akceleracją GPU. Sharpe 1.89, Sortino 2.43, redukcja ryzyka z 30% do 12%. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-24 |
| 313 | (plik) deep_options_hedge.py | N-SHIELDS-026 DEEP OPTIONS HEDGE ENGINE™ | 💎 Diament | Jack | Głębokie uczenie dla zarządzania ryzykiem opcji krypto. Physics-Informed Neural Networks. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-24 |
| 314 | (plik) bayesian_washout_detector.py | N-SHIELDS-027 BAYESIAN WASHOUT DETECTOR™ | 💎 Diament | Jack | Bayesowski autoenkoder do wykrywania fałszywych transakcji na wielu giełdach jednocześnie. | ⚔️ 04_Gwardia_Przyboczna | 2026-05-24 |
| 315 | (plik) quantum_digital_twin.py | N-BACK-019 QUANTUM DIGITAL TWIN™ | 💎 Diament | Jack | Kwantowy Cyfrowy Bliźniak — wirtualna symulacja rynku do testowania strategii w zmiennych warunkach. | ⚔️ 09_Poligon_Bojowy | 2026-05-24 |
| 316 | (plik) swarm_harmony_protocol.py | N-ROJ-004 SWARM HARMONY PROTOCOL™ | 💎 Diament | Jack | Protokół harmonii roju — eliminuje zakłócenia między agentami przy niespójnych danych. | ⚔️ 12_Roj | 2026-05-24 |
| 317 | (plik) regional_behavioral_profiler.py | N-BRAIN-073 REGIONAL BEHAVIORAL PROFILER™ | 💎 Diament | Jack | Dynamiczna identyfikacja pochodzenia kapitału i automatyczne dostosowanie taktyki do kultury traderów. | ⚔️ 01_Wywiad | 2026-05-24 |
| 318 | (plik) cross_cultural_volatility.py | N-BRAIN-074 CROSS-CULTURAL VOLATILITY PREDICTOR™ | 💎 Diament | Jack | Przewidywanie zmienności wynikającej z otwarcia konkretnych sesji giełdowych na świecie. | ⚔️ 01_Wywiad | 2026-05-24 |
| 319 | (plik) cultural_cycle_master.py | N-BRAIN-075 THE CULTURAL CYCLE MASTER™ | 💎 Diament | Jack | Mapowanie globalnych wydarzeń kulturowych (Księżycowy Nowy Rok, Ramadan) i ich wpływu na płynność. | ⚔️ 01_Wywiad | 2026-05-24 |
| 320 | (plik) global_fomo_fear_detector.py | N-EYES-067 GLOBAL FOMO/FEAR ARBITRAGE DETECTOR™ | 🥇 Złoto | Jack | Wykrywanie różnic psychologicznych między kulturami (Korea vs. USA) w czasie rzeczywistym. | ⚔️ 02_Zwiadowcy | 2026-05-24 |
| 321 | (plik) global_heatmap_overlay.py | N-DASH-025 GLOBAL HEATMAP OVERLAY™ | 🥇 Złoto | Jack | Nowa warstwa wizualna na War Table — pokazuje geograficzne pochodzenie kapitału na żywo. | ⚔️ 06_Dowodztwo | 2026-05-24 |
| 322 | (plik) adaptive_opro.py | ADAPTIVE-OPRO Protocol (Rozszerzenie LEGIONA) | 💎 Diament | Jack | Dynamiczna optymalizacja promptów w czasie rzeczywistym. Adaptive-OPRO, maj 2026. | ⚔️ 01_Wywiad | 2026-05-24 |
| 323 | (plik) pump_dump_shield.py ✅ na dysku | N-SHIELDS-04 PUMP & DUMP SHIELD™ V2.0-NEW | — | Jack | Silnik anty-manipulacyjny: 7 metod detekcji (Wash Trading, Spoofing, Fake Volume, Pump&Dump, Momentum Ignition, Quote Stuffing, Cross-Market Anomalies), score 0-100, Robust Z-Score (MAD), Orderbook Imbalance, Volume Decoupling. Dokumentacja techniczna: `N-SHIELDS-04_raport.md` | ⚔️ 04_Gwardia_Przyboczna | 2026-05-25 |
| 324 | (plik) ensemble_voter.py ✅ na dysku | N-BRAIN-072 Strict Ensemble Voter | — | Jack | Soft Weighted Voting z filtrami anty-halucynacyjnymi: Entropia Shannona (max_entropy=0.40), Leader Anchor, próg pewności (min_confidence=0.65), normalizacja sumy wag. Dokumentacja techniczna: `G_osowanie_modeli_raport.md` | ⚔️ 01_Wywiad | 2026-05-25 |
| 325 | (plik) freqtrade_ai_router.py ✅ na dysku | N-ORCH-007 Freqtrade AI Router (instytucjonalny) | — | Jack | Router strategii AI dla Freqtrade: Detektor Reżimu Rynkowego (ADX/ATR/RSI), Filtr Statystyczny (Expectancy & PF), korekcja Asymetrii Profit/Loss, korekta Recency Bias. Dokumentacja techniczna: `Router_strategii_raport.md` | ⚔️ 08_Strategiczny_Sztab | 2026-05-25 |
| 326 | (plik) intershield_orchestrator.py ✅ na dysku | N-SHIELDS-06 InterShield Orchestrator V3.0-PREMIUM | — | Jack | Zintegrowany system detekcji manipulacji + NeuralCache feedback loop. Wykładnicza blokada (Cool-down = Base × 2^Violation), adaptacyjna rekalibracja progów (NeuralCache → Orchestrator → PumpDumpShield). Pliki: `pump_dump_shield.py`, `neural_cache.py`, `intershield_orchestrator.py`. Rozszerzenie #323. Dokumentacja techniczna: `Pami___wygranych_raport.md` | ⚔️ 04_Gwardia_Przyboczna | 2026-05-25 |
| 327 | (dokument) retrieval_engine_pipeline_V2.2.md ✅ na dysku | Architektura RAG + Multi-Strategy Pipeline V2.2 | — | Jack | Live WebSocket Integration 800ms, LiveFeatureBuffer (stateful), Contextual Guard, integracja Brain Engine + Agent Manager + Skills. Dokumentacja techniczna: `INTEGRACJA_RETRIEVAL-ENGINE_MULTI-STRATEGY_PIPELINE_raport.md` | 🗺️ War Council + 🧪 Royal Alchemist | 2026-05-25 |
| 328 | (dokument) manifest_imperium_v1_historyczny.md ✅ na dysku | Manifest Imperium v1.0 (pre-v1.0 KSIĘGI) | — | Jack & DeepSeek AI | Wczesny manifest projektu sprzed obecnej linii v1.0–v2.2: pełna struktura folderów, Tytan-α dokumentacja, system ikon i herbów, roadmapa 2.0/3.0/4.0, wytyczne dla kolejnego modelu AI. Dokumentacja techniczna: `Kingdom_Pixel_v1.md` | 📚 Great Library / Archiwum | 2026-05-20 |
| 329 | (dokument) manifest_imperium_v2_historyczny.md ✅ na dysku | Manifest Imperium v2.0 (pre-v2.0 KSIĘGI) | — | Komandant Pixel & DeepSeek AI | Wczesny manifest v2.0 (2026-05-20) — wcześniejszy niż KSIEGA_IMPERIUM_v2.0 w obecnej linii. Pełna struktura folderów + instrukcja dla nowego agenta AI. Dokumentacja techniczna: `Kingdom_Pixel_v2_0.md` | 📚 Great Library / Archiwum | 2026-05-20 |
| 330 | (dokument) manifest_imperium_v2_dodatek1.md ✅ na dysku | Manifest Imperium v2.0 — Dodatek 1 | — | Komandant Pixel & DeepSeek AI | Załącznik do #329 — dodatek 1 do Manifestu v2.0. Dokumentacja techniczna: `Kingdom_Pixel_v2_0_dodatek1.md` | 📚 Great Library / Archiwum | 2026-05-20 |

---

## 📊 STATYSTYKI REJESTRU v3.1

| Metryka | Wartość |
|:---|:---|
| **Łącznie wpisów** | **330** (+8 vs v3.0) |
| **Wpisy zewnętrzne (zbadane źródła)** | **200** (#001–#200) |
| **Wpisy autorskie Jacka (moduły N-XX)** | **~121** (#201–#330 z prefiksem `(plik)` lub `(dokument)`) |
| **Wpisy dokumentacyjne** | **9** (#308–#310, #327, #328, #329, #330 + 2 inne) |
| **Pokrycie Suwerennością Wiedzy (Zasada 61)** | **18/~125 ≈ 14,4%** (wzrost z 8,5% w v3.0) |
| **Pokrycie Dokumentacją Techniczną zgodną z Zasadą 11 (.py + metryczka)** | **10/~117 ≈ 8,5%** (bez zmian — nowe pliki są w `.md`, do konwersji w Fazie 2) |
| **Liczba unikalnych ID** | **330** (od 1 do 330, ciągłość zachowana) |
| **Numeracja** | ciągła, bez luk, bez duplikatów |

---

## 🔍 ŹRÓDŁO POSZCZEGÓLNYCH WPISÓW (zgodność z Zasadą 23 — Data Lineage)

| Zakres ID | Źródło rekonstrukcji | Komentarz |
|:---|:---|:---|
| #001–#200 | `ZBADANE_v1.0.md` | Pełna tabela 200 wpisów z pierwszej wersji |
| #201–#215 | `ZBADANE_v1.1.md` | 15 nowych wpisów (m.in. moduły 201–210 oraz 5 pereł azjatyckich) |
| #216–#222 | `ZBADANE_v1.2.md` | 7 nowych wpisów (m.in. KAMELEON, FEWS, DIR Protocol, Spoofing Detector) |
| #223–#242 | `ZBADANE_v1.3.md` | 20 nowych wpisów (m.in. N-EYES-49 Global Social Intel, N-EYES-50 VIP Tracker, hybrydy) |
| #243–#245 | `ZBADANE_v1.4.md` | 3 wpisy (Agent Insurance, Cognitive Swarm, Copy-Trade Deep Analyzer) |
| #246–#247 | `ZBADANE_v1.5.md` | 2 wpisy (MEXC Compliance Engine, Fee Optimizer) |
| #248–#264 | `ZBADANE_v1.6.md` | 17 wpisów (m.in. Nexus Grid, Intent Engine, Mass Psychology Engine) |
| #265–#276 | `ZBADANE_v1.8.md` | 12 wpisów (Deterministic Mesh, Neural HMM AGA, i in.) |
| #277–#288 | `ZBADANE_v1.9.md` | 12 wpisów (Impossible Hunter, Projekt Chimera) |
| #289–#298 | `ZBADANE_v2.0.md` | 10 wpisów (Trend Scope Engine, Liquidity Gap Detector, HFT OrderBook Predictor) |
| **#299–#310** | **CZAT, linie 43251–43310** | **12 wpisów odzyskanych z rozmowy źródłowej** (Resurrection Engine, Crucible Gatekeeper, Signal Orchestrator, Alchemist's Prep Lab, Venture Capital Allocator, Predictive Breakout, Adaptive VWAP, Backtest Integrity Guardian, Strategy Lifecycle Manager, DOMINION SCORE v3.0, Karta Chimera, 7 Artefaktów) |
| #311–#322 | `ZBADANE_v2.2.md` | 12 wpisów (Imperial Arena, Adaptive Hedge Guardian, Quantum Digital Twin, Swarm Harmony, kulturowe) |
| **#323–#330** | **Pliki archiwalne Komendanta (8 plików .md na dysku)** | **8 nowych wpisów (rejestracja archiwum w v3.1):** N-SHIELDS-04 PUMP & DUMP SHIELD, N-BRAIN-072 Ensemble Voter, N-ORCH-007 Freqtrade AI Router, N-SHIELDS-06 InterShield Orchestrator + 4 dokumenty historyczne/architektoniczne |

---

## ⚠️ ZNANE OGRANICZENIA REJESTRU v3.0

1. **Pliki kodu (`DOKUMENTACJA TECHNICZNA`):** Dostarczonych jest 10 plików (#201–#210). Pozostałe ~107 modułów z prefiksem `(plik)` w tabeli ma nazwy plików, ale nie ma jeszcze fizycznych odpowiedników w folderze `DOKUMENTACJA TECHNICZNA`. Realizacja w Fazie 2 planu naprawczego.

2. **Klasy modułów:** Część wpisów ma w polu „Klasa" wartość `—` (myślnik) zamiast oznaczenia klasy (Diament / Złoto / Srebro / Perła). W Fazie 2 należy je sklasyfikować zgodnie z DOMINION SCORE™ v3.0.

3. **Zasada 73 (powiązania):** Wpis #301 odnosi się w treści do „Zasady 73". Po konsolidacji v2 Zasad Fundamentalnych Signal Hierarchy to teraz Zasada **72** (a Zasada 73 to Agent Insurance Protocol). Wpis #301 wymaga drobnej aktualizacji w przyszłej iteracji.

---

## 📋 CHANGELOG (Zasada 49 pkt 2)

| Wersja | Data | Zmiany |
|:---|:---|:---|
| **v3.1** | 2026-05-25 | **Rejestracja archiwum dyskowego Komendanta.** Dodano 8 wpisów (#323–#330): 4 brakujące moduły autorskie (N-SHIELDS-04, N-BRAIN-072, N-ORCH-007, N-SHIELDS-06) + 4 dokumenty (architektura V2.2 retrieval-engine, 3 manifesty historyczne). Zaktualizowano 5 istniejących wpisów (#47, #48, #65, #186, #187) — dodano oznaczenie „✅ na dysku" i adnotację „Dokumentacja techniczna: …" zgodnie z Zasadą 11 pkt 5. Pokrycie Zasady 61 (Suwerenność Wiedzy) wzrosło z 8,5% na 14,4%. |
| **v3.0** | 2026-05-24 | **Konsolidacja po audycie Trybunału Cara (Faza 1, Krok 1.1).** Wszystkie 322 wpisy zebrane fizycznie w jednej tabeli. Usunięte placeholdery typu „Wpisy #X–#Y zachowane w całości — pełna lista w ZBADANE.md vN". Wpisy #299–#310 odzyskane z czatu źródłowego. Dodana sekcja „Źródło poszczególnych wpisów" zgodna z Zasadą 23. Dodany CHANGELOG zgodny z Zasadą 49 pkt 2. |
| **v2.2** | 2026-05-24 | Dodano 12 wpisów (#311–#322): Imperial Arena, Adaptive Hedge Guardian, Quantum Digital Twin, Swarm Harmony i kulturowe. **W pliku zachowany placeholder odsyłający do v2.1.** |
| **v2.1** | 2026-05-24 | Dodano 12 wpisów (#299–#310). **W pliku zerowa tabela — wszystko jako placeholder odsyłający do „poprzedniej odpowiedzi" w czacie.** |
| **v2.0** | 2026-05-24 | Dodano 10 wpisów (#289–#298). Łączna deklaracja: 298 wpisów. |
| **v1.9** | 2026-05-24 | Dodano 12 wpisów (#277–#288). |
| **v1.8** | 2026-05-23 | Dodano 12 wpisów (#265–#276). |
| **v1.7** | 2026-05-23 | Reorganizacja w System Tomowy (Zasada 60). Brak nowych wpisów. |
| **v1.6** | 2026-05-23 | Dodano 17 wpisów (#248–#264). Wprowadzono klasy 💎/🥇/🥈. |
| **v1.5** | 2026-05-22 | Dodano 2 wpisy (#246–#247). Wprowadzono Kodeks Pola Bitwy MEXC. |
| **v1.4** | 2026-05-22 | Dodano 3 wpisy (#243–#245). |
| **v1.3** | 2026-05-22 | Dodano 20 wpisów (#223–#242). **Pierwsze wystąpienie placeholdera** typu „Wpisy #11–#200 zachowane w całości". |
| **v1.2** | 2026-05-21 | Dodano 7 wpisów (#216–#222). |
| **v1.1** | 2026-05-21 | Dodano 15 wpisów (#201–#215). Wprowadzono prefiks `(plik)` dla modułów autorskich. |
| **v1.0** | 2026-05-18 | **Stan startowy: 200 wpisów (#001–#200)** ze zbadanych źródeł zewnętrznych. |

---

*Autor: Jack — Wizjoner, Architekt, Wynalazca, Magik. Kingdom Pixel.*
*Konsolidacja v3.0 zgodna z Raportem Audytu Trybunału Cara z 24 maja 2026 (sekcja 5.1 Faza 1, Krok 1.1).*
