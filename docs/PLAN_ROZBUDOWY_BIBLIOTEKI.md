# 📚 PLAN ROZBUDOWY BIBLIOTEKI — BIB-070 … BIB-274

> **Stan na:** 2026-07-16 · **Autor listy:** VITRUVIUSZ (Opus) · **Rozkaz Cezara:** „rozbuduj bibliotekę,
> dawaj do 200 pozycji lub więcej, niech nasz LLM się uczy"
> **Mamy dziś:** 69 książek (BIB-001..069) · **Ta lista:** 205 pozycji (BIB-070..274)

## 🔴 CZYTAJ NAJPIERW — status weryfikacji (Prawo I, ZPO)

Numery BIB nadane **przeze mnie, jednorazowo i spójnie** — nie przez DeepSeeka. (Poprzednia lista
z `wrzutnia/Mapa-kluczy calosc plus.md` miała **sześć sprzecznych numeracji**, dziesiątki pozycji
z autorem „–" i fabrykowane cytowania — patrz `docs/` + pamięć `lista-ksiazek-deepseek-smiec`.)

**Legenda pewności — czytaj dosłownie, nie udaję weryfikacji:**
| Znak | Znaczenie |
|---|---|
| ✅ | **Kanon** — dzieło, którego istnienia jestem pewien (klasyk, wielokrotnie wydawany). Rok/wydanie **potwierdź przed zakupem**. |
| ⚠️ | **Do weryfikacji** — pozycja prawdopodobna, ale NIE potwierdzona w tej sesji. Sprawdź przed wydaniem pieniędzy. |
| 🆓 | **Otwarta — JEST PLIK od autora/wydawcy/arXiv.** Wolno pobrać. Bierzemy pierwsze. |
| 📖 | **Tylko do czytania online — BRAK pliku i BRAK otwartej licencji.** ⛔ **NIE wchodzi do RAG.** |

🚨 **KOREKTA 2026-07-16 (mój błąd, Prawo I):** pierwotnie miałem jeden znacznik 🆓 i **mieszałem
dwie różne rzeczy** — „darmowe do czytania" ≠ „wolno pobrać". Przykład, na którym to wyszło:
**Hyndman FPP3** jest darmowa do czytania na otexts.com, ale OTexts **nie daje PDF/EPUB** i strona
**nie ma otwartej licencji** (brak CC). Zeskrobanie jej HTML-a do `tekst_cache` byłoby wrzuceniem
pełnego tekstu chronionego dzieła **do gita** — a nasz `.gitignore` wyrzucił binaria książek
dokładnie przez „ryzyko praw autorskich komercyjnych tytułów". Decyzja Cezara 2026-07-16: **nie ściągać.**

⚠️ **Statusu 🆓 przy POZOSTAŁYCH pozycjach NIE zweryfikowałem pozycja-po-pozycji.** Pewne otwarte
(autor/wydawca sam daje plik): **arXiv** (Attention, LoRA, QLoRA, Hinton-distylacja, LIMA, Flash Boys 2.0,
speculative decoding), **Boyd** (Stanford), **Hastie ESL** (Stanford), **Hernán & Robins**, whitepapery
**Bitcoin/Ethereum**, **MacKay**. Reszta 🆓 = **do sprawdzenia przed pobraniem** — może się okazać
📖 jak FPP3. Nie zgaduj: sprawdź licencję na stronie źródła.

⚠️ **Mój cutoff wiedzy to styczeń 2026** — pozycje z 2025/2026 są z natury mniej pewne. Żadna data
wydania na tej liście nie jest zweryfikowana w tej sesji; traktuj rok jako orientacyjny.

**Zasada doboru (LIMA dla książek):** preferuję **kanon nad nowość** — 200 prawdziwych, cytowanych
dzieł uczy lepiej niż 400 modnych tytułów. Uczeń TIRO nauczy się tego, co mu damy.

---

## 🎯 Priorytet 0 — WEŹ DZIŚ (darmowe, wypełniają zerowe luki)

| BIB | Autor | Tytuł | Dlaczego teraz |
|---|---|---|---|
| 070 | Vaswani i in. | *Attention Is All You Need* (2017) 🆓 ✅ | Fundament transformerów — **wprost pod TIRO**. arXiv:1706.03762 |
| 071 | Easley, López de Prado, O'Hara | *Flow Toxicity and Liquidity in a High-Frequency World* (RFS 2012) 🆓 ✅ | **Źródło naszego neuronu Z-01 (VPIN)** — mamy neuron, nie mamy źródła |
| 072 | Hyndman, Athanasopoulos | *Forecasting: Principles and Practice* (**2nd ed.**) ✅ **W BIBLIOTECE** | ✅ **ZAINDEKSOWANA 2026-07-16** — Cezar ma **kupiony** egzemplarz (PDF, 2. edycja) z własnego dysku. 257 fragmentów w RAG, korpus 27 959 → 28 535. Kanon prognozowania — domyka zerową lukę (mamy WFO i Sybillę z Brierem, nie mieliśmy teorii). ⚠️ Uwaga na przyszłość: **downloadowalna wersja FPP jest PŁATNA** (OTexts: „Buy a print or downloadable version"); darmowe jest tylko czytanie online — nie ściągać z serwisów typu dokumen.pub. 3. edycja różni się głównie przejściem `forecast`→`fable` (R), dla nas bez znaczenia |
| 073 | Boyd, Vandenberghe | *Convex Optimization* 🆓 ✅ | Darmowy PDF (Stanford) — fundament sizingu/portfela |
| 074 | Goodfellow i in. | — mamy (BIB-068) | — |
| 075 | Daspremont i in. / Nakamoto | *Bitcoin: A Peer-to-Peer Electronic Cash System* 🆓 ✅ | Whitepaper źródłowy — 9 stron, mamy o nim książki, nie mamy jego |
| 076 | Buterin i in. | *Ethereum Whitepaper* 🆓 ✅ | j.w. — źródło zamiast opracowań |
| 077 | Daian i in. | *Flash Boys 2.0: Frontrunning in Decentralized Exchanges…* (2019) 🆓 ✅ | **Kanoniczne źródło o MEV** — zero u nas |
| 078 | Adams i in. | *Uniswap v3 Core* (whitepaper) 🆓 ⚠️ | Mechanika AMM u źródła |
| 079 | Gneiting, Raftery | *Strictly Proper Scoring Rules, Prediction, and Estimation* (JASA 2007) 🆓 ✅ | **Teoria pod Brier/Sybillę** — mamy Księgi Sybillińskie, nie mamy teorii |

---

## 🤖 Transformery / LLM / NLP — **pod TIRO** (BIB-080..099)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 080 | Jurafsky, Martin | *Speech and Language Processing* (3rd ed.) 🆓 ✅ | Darmowy draft — biblia NLP |
| 081 | Tunstall, von Werra, Wolf | *Natural Language Processing with Transformers* ✅ | Praktyka HuggingFace |
| 082 | Rothman | *Transformers for Natural Language Processing* ⚠️ | |
| 083 | Vaswani → patrz BIB-070 | — | |
| 084 | Devlin i in. | *BERT: Pre-training of Deep Bidirectional Transformers* 🆓 ✅ | arXiv |
| 085 | Brown i in. | *Language Models are Few-Shot Learners* (GPT-3) 🆓 ✅ | arXiv |
| 086 | Hu i in. | *LoRA: Low-Rank Adaptation of Large Language Models* 🆓 ✅ | **Wprost nasza metoda treningu (E4)** |
| 087 | Dettmers i in. | *QLoRA: Efficient Finetuning of Quantized LLMs* 🆓 ✅ | **Nasza ścieżka na RTX 4050** |
| 088 | Hinton i in. | *Distilling the Knowledge in a Neural Network* 🆓 ✅ | **Fundament distylacji = Filar 2 TIRO** |
| 089 | Wei i in. | *Chain-of-Thought Prompting…* 🆓 ✅ | arXiv |
| 090 | Wang i in. | *Self-Consistency Improves Chain of Thought Reasoning* 🆓 ✅ | **Teoria pod nasz konsensus próbek** |
| 091 | Zhou i in. | *LIMA: Less Is More for Alignment* 🆓 ✅ | **Źródło naszej zasady „1000 doskonałych > 50000 miernych"** |
| 092 | Lewis i in. | *Retrieval-Augmented Generation…* 🆓 ✅ | Fundament naszego RAG |
| 093 | Raschka | *Build a Large Language Model (From Scratch)* ⚠️ | |
| 094 | Kaplan i in. | *Scaling Laws for Neural Language Models* 🆓 ✅ | Dlaczego mały model ma sufit |
| 095 | Hoffmann i in. | *Training Compute-Optimal LLMs* (Chinchilla) 🆓 ✅ | |
| 096 | Ouyang i in. | *Training LMs to follow instructions with human feedback* (InstructGPT) 🆓 ✅ | |
| 097 | Rafailov i in. | *Direct Preference Optimization (DPO)* 🆓 ✅ | Alternatywa dla RLHF |
| 098 | Frantar i in. | *GPTQ: Accurate Post-Training Quantization* 🆓 ✅ | Kwantyzacja — nasz Q4_K_M |
| 099 | Leviathan i in. | *Fast Inference from Transformers via Speculative Decoding* 🆓 ✅ | **Źródło dźwigni, którą chcemy zmierzyć** |

## 🕸️ Graph Neural Networks — **luka zerowa** (BIB-100..107)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 100 | Hamilton | *Graph Representation Learning* 🆓 ✅ | Darmowy PDF autora |
| 101 | Wu, Cui, Pei, Zhao | *Graph Neural Networks: Foundations, Frontiers, and Applications* ⚠️ | |
| 102 | Labonne | *Hands-On Graph Neural Networks Using Python* ⚠️ | Praktyka |
| 103 | Kipf, Welling | *Semi-Supervised Classification with Graph Convolutional Networks* 🆓 ✅ | Fundament GCN |
| 104 | Veličković i in. | *Graph Attention Networks* 🆓 ✅ | |
| 105 | Battaglia i in. | *Relational inductive biases, deep learning, and graph networks* 🆓 ✅ | |
| 106 | Barabási | *Network Science* 🆓 ✅ | Darmowy online — sieci jako zjawisko |
| 107 | Newman | *Networks: An Introduction* ✅ | Kanon |

## 🎮 Reinforcement Learning praktyczny — mamy tylko teorię (BIB-108..115)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 108 | Lapan | *Deep Reinforcement Learning Hands-On* (3rd ed.) ⚠️ | Praktyka: DQN/PPO/RLHF |
| 109 | Graesser, Keng | *Foundations of Deep Reinforcement Learning* ⚠️ | |
| 110 | Mnih i in. | *Human-level control through deep RL* (DQN, Nature 2015) ✅ | |
| 111 | Schulman i in. | *Proximal Policy Optimization Algorithms* 🆓 ✅ | PPO |
| 112 | Silver i in. | *Deterministic Policy Gradient Algorithms* ⚠️ | |
| 113 | Szepesvári | *Algorithms for Reinforcement Learning* 🆓 ✅ | Zwięzły kanon |
| 114 | Bertsekas | *Reinforcement Learning and Optimal Control* ⚠️ | |
| 115 | Powell | *Approximate Dynamic Programming* ⚠️ | |

## 🔗 Wnioskowanie przyczynowe — **luka zerowa** (BIB-116..123)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 116 | Pearl | *Causality: Models, Reasoning, and Inference* (2nd ed.) ✅ | **Kanon absolutny** |
| 117 | Pearl, Glymour, Jewell | *Causal Inference in Statistics: A Primer* ✅ | Łagodniejsze wejście |
| 118 | Pearl, Mackenzie | *The Book of Why* ✅ | Popularne, dobre na start |
| 119 | Peters, Janzing, Schölkopf | *Elements of Causal Inference* 🆓 ✅ | Darmowy PDF (MIT Press) |
| 120 | Angrist, Pischke | *Mostly Harmless Econometrics* ✅ | Przyczynowość empiryczna |
| 121 | Hernán, Robins | *Causal Inference: What If* 🆓 ✅ | Darmowy PDF autorów |
| 122 | Imbens, Rubin | *Causal Inference for Statistics…* ✅ | |
| 123 | Cunningham | *Causal Inference: The Mixtape* 🆓 ✅ | Darmowy online |

## 📊 Ekonometria, szeregi czasowe, prognozowanie (BIB-124..141)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 124 | Hamilton | *Time Series Analysis* ✅ | Kanon (nie mylić z GNN-Hamiltonem) |
| 125 | Box, Jenkins, Reinsel | *Time Series Analysis: Forecasting and Control* ✅ | |
| 126 | Brockwell, Davis | *Introduction to Time Series and Forecasting* ✅ | |
| 127 | Hyndman → BIB-072 | — | |
| 128 | Campbell, Lo, MacKinlay | *The Econometrics of Financial Markets* ✅ | Kanon |
| 129 | Cochrane | *Asset Pricing* ✅ | |
| 130 | Engle | *Autoregressive Conditional Heteroscedasticity…* (ARCH) ✅ | Źródło GARCH |
| 131 | Bollerslev | *Generalized ARCH* ✅ | |
| 132 | Hamilton | *A New Approach to the Economic Analysis of Nonstationary Time Series…* ✅ | **Regime-switching u źródła** |
| 133 | Zivot, Wang | *Modeling Financial Time Series with S-PLUS* ⚠️ | |
| 134 | Lütkepohl | *New Introduction to Multiple Time Series Analysis* ✅ | VAR |
| 135 | Enders | *Applied Econometric Time Series* ✅ | |
| 136 | Diebold, Mariano | *Comparing Predictive Accuracy* ✅ | **Test przewagi prognoz — pod nasze A/B** |
| 137 | Rabiner | *A Tutorial on Hidden Markov Models…* 🆓 ✅ | HMM u źródła |
| 138 | Tsay → mamy (BIB-031) | — | |
| 139 | Hastie, Tibshirani, Friedman | *The Elements of Statistical Learning* 🆓 ✅ | Darmowy PDF — kanon ML |
| 140 | James i in. | *An Introduction to Statistical Learning* 🆓 ✅ | Darmowy PDF |
| 141 | Murphy | *Probabilistic Machine Learning: An Introduction* / *Advanced Topics* ⚠️ | Drafty bywają darmowe |

## 🎲 Statystyka bayesowska i niepewność (BIB-142..151)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 142 | Gelman i in. | *Bayesian Data Analysis* (3rd ed.) 🆓 ✅ | Darmowy PDF — kanon |
| 143 | McElreath | *Statistical Rethinking* (2nd ed.) ✅ | Najlepsze wejście w Bayesa |
| 144 | Kruschke | *Doing Bayesian Data Analysis* ✅ | |
| 145 | Sivia, Skilling | *Data Analysis: A Bayesian Tutorial* ⚠️ | |
| 146 | Jaynes | *Probability Theory: The Logic of Science* ✅ | Filozofia + matematyka |
| 147 | MacKay | *Information Theory, Inference, and Learning Algorithms* 🆓 ✅ | Darmowy PDF — **teoria informacji + ML w jednym** |
| 148 | Cover, Thomas | *Elements of Information Theory* ✅ | Kanon teorii informacji |
| 149 | Efron, Tibshirani | *An Introduction to the Bootstrap* ✅ | **Pod nasze testy istotności** |
| 150 | Shafer, Vovk | *Algorithmic Learning in a Random World* ⚠️ | **Predykcja konformalna — mamy bramkę ML-36!** |
| 151 | Angelopoulos, Bates | *A Gentle Introduction to Conformal Prediction* 🆓 ✅ | arXiv — nowsze wejście |

## 🏛️ Mikrostruktura i egzekucja (BIB-152..165)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 152 | Bouchaud, Bonart, Donier, Gould | *Trades, Quotes and Prices* ✅ | **Kanon mikrostruktury XXI w.** |
| 153 | Almgren, Chriss | *Optimal Execution of Portfolio Transactions* 🆓 ✅ | Fundament egzekucji |
| 154 | Kyle | *Continuous Auctions and Insider Trading* ✅ | Model Kyle'a u źródła |
| 155 | Glosten, Milgrom | *Bid, Ask and Transaction Prices…* ✅ | |
| 156 | Avellaneda, Stoikov | *High-frequency trading in a limit order book* 🆓 ✅ | **Kanon market makingu** |
| 157 | Lehalle, Laruelle | *Market Microstructure in Practice* ✅ | |
| 158 | Guéant | *The Financial Mathematics of Market Liquidity* ⚠️ | |
| 159 | Johnson | *Algorithmic Trading and DMA* ✅ | |
| 160 | Foucault, Pagano, Röell | *Market Liquidity: Theory, Evidence, Policy* ✅ | |
| 161 | Madhavan | *Market Microstructure: A Survey* 🆓 ⚠️ | |
| 162 | Easley i in. | *The Microstructure of the Flash Crash* ⚠️ | |
| 163 | Menkveld | *High-Frequency Trading and the New Market Makers* ⚠️ | |
| 164 | Budish, Cramton, Shim | *The High-Frequency Trading Arms Race* ✅ | Batch auctions |
| 165 | Hasbrouck → mamy (BIB-044) | — | |

## 📐 Optymalizacja i portfel (BIB-166..177)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 166 | Boyd → BIB-073 | — | |
| 167 | Nocedal, Wright | *Numerical Optimization* ✅ | Kanon |
| 168 | Markowitz | *Portfolio Selection* (1952) ✅ | Źródło teorii portfela |
| 169 | Meucci | *Risk and Asset Allocation* ✅ | |
| 170 | Michaud | *Efficient Asset Management* ⚠️ | |
| 171 | Ang | *Asset Management: A Systematic Approach to Factor Investing* ✅ | |
| 172 | Ilmanen | *Expected Returns* ✅ | |
| 173 | Ilmanen | *Investing Amid Low Expected Returns* ⚠️ | |
| 174 | Kelly | *A New Interpretation of Information Rate* (1956) 🆓 ✅ | **Kryterium Kelly'ego u źródła — pod sizing** |
| 175 | Thorp | *The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market* 🆓 ✅ | Kelly w praktyce |
| 176 | MacLean, Thorp, Ziemba | *The Kelly Capital Growth Investment Criterion* ⚠️ | |
| 177 | Carver | *Systematic Trading* ✅ | Kompletna metodologia — realna luka |

## ⚠️ Ryzyko ekstremalne i grube ogony (BIB-178..187)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 178 | Embrechts, Klüppelberg, Mikosch | *Modelling Extremal Events* ✅ | **Kanon EVT** |
| 179 | McNeil, Frey, Embrechts | *Quantitative Risk Management* ✅ | Kanon QRM |
| 180 | Coles | *An Introduction to Statistical Modeling of Extreme Values* ✅ | |
| 181 | Taleb | *The Black Swan* ✅ | Mamy tylko *Fooled by Randomness* |
| 182 | Taleb | *Antifragile* ✅ | **Nasza doktryna wznawialności wprost stąd** |
| 183 | Taleb | *Skin in the Game* ✅ | |
| 184 | Taleb | *Dynamic Hedging* ✅ | Techniczny Taleb |
| 185 | Taleb | *Statistical Consequences of Fat Tails* 🆓 ✅ | Darmowy — techniczny |
| 186 | Sornette | *Why Stock Markets Crash* ✅ | Ekonofizyka krachów |
| 187 | Rebonato | *Plight of the Fortune Tellers* ⚠️ | |

## 🎯 Teoria gier i mechanizmy — **luka zerowa** (BIB-188..197)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 188 | von Neumann, Morgenstern | *Theory of Games and Economic Behavior* ✅ | **Kanon absolutny** |
| 189 | Fudenberg, Tirole | *Game Theory* ✅ | Standard akademicki |
| 190 | Osborne, Rubinstein | *A Course in Game Theory* 🆓 ✅ | Darmowy PDF |
| 191 | Myerson | *Game Theory: Analysis of Conflict* ✅ | |
| 192 | Binmore | *Game Theory: A Very Short Introduction* ✅ | ⚠️ **DeepSeek zmyślił tytuł „An Introduction" — to jest właściwy** |
| 193 | Krishna | *Auction Theory* ✅ | Pod aukcje/MEV |
| 194 | Milgrom | *Putting Auction Theory to Work* ✅ | |
| 195 | Nisan i in. | *Algorithmic Game Theory* 🆓 ✅ | Darmowy PDF |
| 196 | Roth | *Who Gets What — and Why* ✅ | Projektowanie rynków |
| 197 | Schelling | *The Strategy of Conflict* ✅ | |

## ₿ Krypto zaawansowane, DeFi, MEV (BIB-198..211)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 198 | Nakamoto → BIB-075 | — | |
| 199 | Daian i in. → BIB-077 | — | |
| 200 | Narayanan i in. | *Bitcoin and Cryptocurrency Technologies* 🆓 ✅ | Darmowy — Princeton |
| 201 | Werner i in. | *SoK: Decentralized Finance (DeFi)* 🆓 ✅ | Systematyzacja DeFi |
| 202 | Angeris, Chitra | *Improved Price Oracles: Constant Function Market Makers* 🆓 ✅ | **Matematyka AMM** |
| 203 | Angeris i in. | *An Analysis of Uniswap Markets* 🆓 ✅ | |
| 204 | Qin, Zhou, Gervais | *Quantifying Blockchain Extractable Value* 🆓 ✅ | MEV mierzalnie |
| 205 | Buterin i in. | *Ethereum Yellow Paper* (Wood) 🆓 ✅ | Specyfikacja EVM |
| 206 | Di Maggio | *Blockchain, Crypto and DeFi* ⚠️ | |
| 207 | Schär | *Decentralized Finance: On Blockchain- and Smart Contract-Based Financial Markets* 🆓 ✅ | St. Louis Fed |
| 208 | Makarov, Schoar | *Trading and Arbitrage in Cryptocurrency Markets* 🆓 ✅ | **Arbitraż krypto empirycznie** |
| 209 | Gudgeon i in. | *DeFi Protocols for Loanable Funds* 🆓 ⚠️ | |
| 210 | Xu i in. | *SoK: Decentralized Exchanges with Automated Market Maker Protocols* 🆓 ✅ | |
| 211 | Eskandari i in. | *SoK: Transparent Dishonesty: Front-Running Attacks on Blockchain* 🆓 ⚠️ | |

## 🧠 Decyzje, kalibracja, osąd (BIB-212..221)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 212 | Tetlock, Gardner | *Superforecasting* ✅ | **Kalibracja prognoz — pod Sybillę** |
| 213 | Tetlock | *Expert Political Judgment* ✅ | |
| 214 | Silver | *The Signal and the Noise* ✅ | |
| 215 | Kahneman, Sibony, Sunstein | *Noise: A Flaw in Human Judgment* ✅ | |
| 216 | Gigerenzer | *Risk Savvy* ✅ | |
| 217 | Klein | *Sources of Power* ⚠️ | Decyzje eksperckie |
| 218 | Savage | *The Foundations of Statistics* ✅ | Teoria decyzji u źródła |
| 219 | Brier | *Verification of Forecasts Expressed in Terms of Probability* (1950) 🆓 ✅ | **Źródło naszego Brier score** |
| 220 | Mauboussin | *More Than You Know* ⚠️ | |
| 221 | Mauboussin | *The Success Equation* ✅ | Szczęście vs umiejętność |

## 🌐 Systemy złożone, ekonofizyka, ABM (BIB-222..231)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 222 | Mantegna, Stanley | *An Introduction to Econophysics* ✅ | |
| 223 | Bouchaud, Potters | *Theory of Financial Risk and Derivative Pricing* ✅ | |
| 224 | Sornette | *Critical Phenomena in Natural Sciences* ⚠️ | |
| 225 | Mitchell | *Complexity: A Guided Tour* ✅ | |
| 226 | Arthur | *Complexity and the Economy* ⚠️ | |
| 227 | Farmer | *Making Sense of Chaos* ⚠️ | ABM w ekonomii |
| 228 | Epstein, Axtell | *Growing Artificial Societies* ⚠️ | |
| 229 | Miller, Page | *Complex Adaptive Systems* ✅ | |
| 230 | Holland | *Hidden Order / Adaptation in Natural and Artificial Systems* ✅ | Fundament algorytmów adaptacyjnych |
| 231 | Page | *The Model Thinker* ✅ | **Wiele modeli > jeden — nasza doktryna roju** |

## 🛠️ Inżynieria: systemy tradingowe, dane, ML w produkcji (BIB-232..245)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 232 | Kleppmann | *Designing Data-Intensive Applications* ✅ | **Kanon systemów danych** |
| 233 | Huyen | *Designing Machine Learning Systems* ✅ | Mamy jej *AI Engineering*, nie to |
| 234 | Burkov | *Machine Learning Engineering* ⚠️ | |
| 235 | Lakshmanan i in. | *Machine Learning Design Patterns* ⚠️ | |
| 236 | Géron | *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow* ✅ | Kanon praktyki |
| 237 | Raschka i in. | *Machine Learning with PyTorch and Scikit-Learn* ✅ | |
| 238 | McKinney | *Python for Data Analysis* ✅ | pandas u źródła |
| 239 | Ramalho | *Fluent Python* ✅ | Jakość naszego kodu |
| 240 | Percival, Gregory | *Architecture Patterns with Python* 🆓 ✅ | Darmowy online |
| 241 | Beazley, Jones | *Python Cookbook* ✅ | |
| 242 | Gorelick, Ozsvald | *High Performance Python* ✅ | **Pod nasze wąskie gardła CPU** |
| 243 | Nygard | *Release It!* ✅ | Odporność systemów produkcyjnych |
| 244 | Beyer i in. | *Site Reliability Engineering* 🆓 ✅ | Darmowy — Google |
| 245 | Fowler | *Refactoring* (2nd ed.) ✅ | |

## 📰 Dane alternatywne i sentyment (BIB-246..253)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 246 | Denev, Amen | *The Book of Alternative Data* ✅ | Kanon alt-danych |
| 247 | Kolanovic, Krishnamachari | *Big Data and AI Strategies* (JPM 2017) 🆓 ✅ | Legendarny raport |
| 248 | Tetlock (Paul C.) | *Giving Content to Investor Sentiment* 🆓 ✅ | **Sentyment newsów u źródła — pod NEWS-01** |
| 249 | Loughran, McDonald | *When Is a Liability Not a Liability?* 🆓 ✅ | **Słownik sentymentu finansowego** |
| 250 | Baker, Wurgler | *Investor Sentiment in the Stock Market* 🆓 ✅ | |
| 251 | Bollen, Mao, Zeng | *Twitter mood predicts the stock market* 🆓 ✅ | Klasyk (i ostrzeżenie o replikacji) |
| 252 | Araci | *FinBERT: Financial Sentiment Analysis with Pre-trained Language Models* 🆓 ✅ | |
| 253 | Ke, Kelly, Xiu | *Predicting Returns with Text Data* 🆓 ⚠️ | |

## 📈 Uzupełnienia tradingowe i klasyka (BIB-254..274)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 254 | Tharp | *Trade Your Way to Financial Freedom* ✅ | Position sizing |
| 255 | Schwager | *The New Market Wizards* ✅ | Mamy tylko pierwszy tom |
| 256 | Schwager | *Hedge Fund Market Wizards* ✅ | |
| 257 | Schwager | *Unknown Market Wizards* ✅ | |
| 258 | Covel | *Trend Following* ✅ | |
| 259 | Faith | *Way of the Turtle* ✅ | |
| 260 | Clenow | *Following the Trend* ✅ | |
| 261 | Clenow | *Trading Evolved* ⚠️ | Python + backtesting |
| 262 | Chan | *Quantitative Trading* → mamy (BIB-010) | — |
| 263 | Pardo | *The Evaluation and Optimization of Trading Strategies* ✅ | **WFO u źródła — mamy WFO!** |
| 264 | Bailey, López de Prado | *The Deflated Sharpe Ratio* 🆓 ✅ | **Mamy DSR w kodzie, nie mamy źródła** |
| 265 | Bailey i in. | *Pseudo-Mathematics and Financial Charlatanism* 🆓 ✅ | Backtest overfitting |
| 266 | Harvey, Liu, Zhu | *…and the Cross-Section of Expected Returns* 🆓 ✅ | Multiple testing w finansach |
| 267 | Fama, French | *Common Risk Factors in the Returns on Stocks and Bonds* ✅ | Faktory u źródła |
| 268 | Jegadeesh, Titman | *Returns to Buying Winners and Selling Losers* ✅ | **Momentum u źródła** |
| 269 | Asness, Moskowitz, Pedersen | *Value and Momentum Everywhere* 🆓 ✅ | |
| 270 | Moskowitz, Ooi, Pedersen | *Time Series Momentum* 🆓 ✅ | |
| 271 | Lo | *Adaptive Markets* ✅ | **Rynki adaptacyjne — nasza doktryna reżimów** |
| 272 | Lo, MacKinlay | *A Non-Random Walk Down Wall Street* ✅ | |
| 273 | Malkiel | *A Random Walk Down Wall Street* ✅ | Kontrargument (Prawo XVI: słuchaj drugiej strony) |
| 274 | Wilmott | *Paul Wilmott Introduces Quantitative Finance* ✅ | |

---

## 🔌 Jak wpiąć do RAG (nie wymaga kodu — wszystko już jest)

1. **Nazwij plik dokładnie:** `BIB-XXX_Autor_Tytul-Z-Myslnikami.ext` (ext: epub/pdf/mobi/azw3/djvu).
   Numer z tej listy. Katalog: `bibliotheca_ulpia/`.
2. **Jedna komenda** (Calibre Portable w PATH — patrz pamięć `calibre-portable-djvu`):
   ```powershell
   $env:PATH = "C:\Calibre Portable\Calibre;$env:PATH"
   python narzedzia/przygotuj_biblioteke.py
   ```
   Spina: konwersja→`tekst_cache` (wersjonowany, więc chmura czyta bez binariów) → indeks FTS
   → katalog metadanych. **Zero tokenów LLM.**
3. **Binaria książek NIE wchodzą do gita** (`.gitignore` — prawa autorskie + rozmiar). Wersjonujemy
   sam wyekstrahowany tekst.
4. **Potem żniwo:** `python narzedzia/bibliotekarz.py --pelny --temat "..."` → NOTARIUS zbiera pary
   automatycznie (3/temat). Postęp widać w panelu 🎓 Szkoła TIRO na dashboardzie.

## ⚖️ Uczciwe zastrzeżenia (Prawo I)

- **Rok/wydawca żadnej pozycji nie jest zweryfikowany w tej sesji.** ✅ = pewny, że dzieło istnieje;
  NIE = pewny szczegółów bibliograficznych. Sprawdź przed zakupem.
- **⚠️ = sprawdź, zanim wydasz pieniądze.** Nie udaję, że wiem.
- **Darmowe (🆓) bierz pierwsze** — jest ich tu ~60 i obejmują wszystkie zerowe luki
  (transformery, GNN, przyczynowość, teoria gier, MEV, konformalna).
- **Nie ma tu ani jednej pozycji Reactive Publishing** (Van Der Post/Preston/Munrow) — świadomie.
- Lista celowo **kanon-ciężka**: uczeń TIRO nauczy się tego, co mu damy. LIMA działa też na książki.
