---
kategoria: FORMA
typ: zywy
wlasciciel: —
stan_na: 2026-07-28
powod_istnienia: "Gotowa do skopiowania lista nazw plików (konwencja `BIB-XXX_Autor_Tytul.ext`) dla całej listy BIB-070..306, żeby Cezar mógł szybko nazwać pobrane pliki bez przepisywania z tabel PL"
---
# 📋 NAZWY PLIKÓW — BIB-070..306 (gotowe do wklejenia)

> **Stan na:** 2026-07-28 · Konwencja: `BIB-XXX_Nazwisko(-Nazwisko)_Tytul-Z-Myslnikami.ext`
> Rozszerzenie dopisz **faktyczne** (`.pdf` / `.epub` / `.mobi` / `.azw3` / `.djvu`).
> Katalog docelowy: `bibliotheca_ulpia/` · Potem: `python narzedzia/przygotuj_biblioteke.py`
>
> Legenda: ⚠️ = pozycja do potwierdzenia (czy dzieło istnieje w tym wydaniu) · Szczegóły: `PLAN_ROZBUDOWY_BIBLIOTEKI.md`

## 🔄 AKTUALIZACJA 2026-07-28 — co się zmieniło od 2026-07-16

🚨 **Ten dokument miał treść wpisaną ręcznie i przez to zgnił** — to ta sama klasa, co runbook W11
i CENSUS ORGANORUM. Poniżej stan **zmierzony z dysku**, nie przepisany.

- **208 plików** w `bibliotheca_ulpia/` · **208/208 zgodnych ze schematem** (2026-07-28 poprawiono
  93 nazwy; wcześniej 88 miało spację zamiast `_` i brak autora).
- **PIĘĆ MARTWYCH SLOTÓW ZOSTAŁO WYPEŁNIONYCH** i **nie są już wolne**:
  `083` (Svensén-Bishop, rozwiązania PRML) · `127` (Shumway-Stoffer) · `138` (Tsay, wielowymiarowe) ·
  `165` (de Jong-Rindi) · `166` (Luenberger-Ye). **Wolne zostają tylko: 198, 199, 262, 296.**
- **Nowe zakresy:** `275..300` (propozycje Consilium, osądzone) · `301..306` (pliki dołożone
  poza planem: West, Gutierrez, Sorensen, Chingnun Lee, Dymarski, Wood).
- **93 pliki czekają na `przygotuj_biblioteke.py`** — są na dysku, nie ma ich w RAG.

⚠️ **Nazwy poniżej są PROPOZYCJĄ dla pozycji, których jeszcze nie mamy.** Dla pozycji już
posiadanych **źródłem prawdy jest dysk**, nie ta lista:
```powershell
Get-ChildItem bibliotheca_ulpia -File | Where-Object Extension -match 'epub|pdf|azw3|mobi|djvu' | Select-Object -ExpandProperty Name
```

> ✅ **Priorytet 0 domknięty 2026-07-16:** BIB-070..079 w RAG (wtedy 79 książek, 29 699 fragmentów).
> Treść każdej zweryfikowana CZYTANIEM, nie nazwą. Stan bieżący RAG: **115 książek, 37 331 fragmentów.**

## ⭐ PRIORYTET 0 — bierz najpierw (zamykają zerowe luki)

```
BIB-070_Vaswani-et-al_Attention-Is-All-You-Need.pdf                                    ✅ MAMY
BIB-071_Easley-Lopez-de-Prado-OHara_Flow-Toxicity-and-Liquidity-in-a-High-Frequency-World.pdf  ✅ MAMY
BIB-073_Boyd-Vandenberghe_Convex-Optimization.pdf                                      ✅ MAMY
BIB-074_Boyd-Vandenberghe_Additional-Exercises-for-Convex-Optimization.pdf             ✅ MAMY
BIB-075_Nakamoto_Bitcoin-A-Peer-to-Peer-Electronic-Cash-System.epub          ✅ MAMY
BIB-076_Buterin_Ethereum-Whitepaper.pdf  ✅ MAMY
BIB-077_Daian-et-al_Flash-Boys-2.0-Frontrunning-in-Decentralized-Exchanges.pdf  ✅ MAMY
BIB-078_Adams-et-al_Uniswap-v3-Core.pdf  ✅ MAMY
BIB-079_Gneiting-Raftery_Strictly-Proper-Scoring-Rules-Prediction-and-Estimation.pdf  ✅ MAMY
```
✅ **BIB-072 — JUŻ W BIBLIOTECE** (2026-07-16), Cezar odnalazł kupiony egzemplarz 2. edycji:
```
BIB-072_Hyndman-Athanasopoulos_Forecasting-Principles-and-Practice-2nd-ed.pdf
```
257 fragmentów w RAG. 
## 🤖 Transformery / LLM / NLP — pod TIRO

```
BIB-080_Jurafsky-Martin_Speech-and-Language-Processing-3rd-ed.pdf
BIB-081_Tunstall-von-Werra-Wolf_Natural-Language-Processing-with-Transformers.epub
BIB-082_Rothman_Transformers-for-Natural-Language-Processing.epub
BIB-084_Devlin-et-al_BERT-Pre-training-of-Deep-Bidirectional-Transformers.pdf
BIB-085_Brown-et-al_Language-Models-are-Few-Shot-Learners.pdf
BIB-086_Hu-et-al_LoRA-Low-Rank-Adaptation-of-Large-Language-Models.pdf
BIB-087_Dettmers-et-al_QLoRA-Efficient-Finetuning-of-Quantized-LLMs.pdf
BIB-088_Hinton-Vinyals-Dean_Distilling-the-Knowledge-in-a-Neural-Network.pdf
BIB-089_Wei-et-al_Chain-of-Thought-Prompting-Elicits-Reasoning.pdf
BIB-090_Wang-et-al_Self-Consistency-Improves-Chain-of-Thought-Reasoning.pdf
BIB-091_Zhou-et-al_LIMA-Less-Is-More-for-Alignment.pdf
BIB-092_Lewis-et-al_Retrieval-Augmented-Generation.pdf
BIB-093_Raschka_Build-a-Large-Language-Model-From-Scratch.epub
BIB-094_Kaplan-et-al_Scaling-Laws-for-Neural-Language-Models.pdf
BIB-095_Hoffmann-et-al_Training-Compute-Optimal-Large-Language-Models.pdf
BIB-096_Ouyang-et-al_Training-Language-Models-to-Follow-Instructions.pdf
BIB-097_Rafailov-et-al_Direct-Preference-Optimization.pdf
BIB-098_Frantar-et-al_GPTQ-Accurate-Post-Training-Quantization.pdf
BIB-099_Leviathan-et-al_Fast-Inference-from-Transformers-via-Speculative-Decoding.pdf
```

## 🕸️ Graph Neural Networks

```
BIB-100_Hamilton_Graph-Representation-Learning.pdf
BIB-101_Wu-Cui-Pei-Zhao_Graph-Neural-Networks-Foundations-Frontiers-and-Applications.pdf
BIB-102_Labonne_Hands-On-Graph-Neural-Networks-Using-Python.epub
BIB-103_Kipf-Welling_Semi-Supervised-Classification-with-Graph-Convolutional-Networks.pdf
BIB-104_Velickovic-et-al_Graph-Attention-Networks.pdf
BIB-105_Battaglia-et-al_Relational-Inductive-Biases-Deep-Learning-and-Graph-Networks.pdf
BIB-106_Barabasi_Network-Science.pdf
BIB-107_Newman_Networks-An-Introduction.pdf
```

## 🎮 Reinforcement Learning praktyczny

```
BIB-108_Lapan_Deep-Reinforcement-Learning-Hands-On-3rd-ed.epub
BIB-109_Graesser-Keng_Foundations-of-Deep-Reinforcement-Learning.epub
BIB-110_Mnih-et-al_Human-Level-Control-Through-Deep-Reinforcement-Learning.pdf
BIB-111_Schulman-et-al_Proximal-Policy-Optimization-Algorithms.pdf
BIB-112_Silver-et-al_Deterministic-Policy-Gradient-Algorithms.pdf
BIB-113_Szepesvari_Algorithms-for-Reinforcement-Learning.pdf
BIB-114_Bertsekas_Reinforcement-Learning-and-Optimal-Control.pdf
BIB-115_Powell_Approximate-Dynamic-Programming.pdf
```

## 🔗 Wnioskowanie przyczynowe

```
BIB-116_Pearl_Causality-Models-Reasoning-and-Inference-2nd-ed.pdf
BIB-117_Pearl-Glymour-Jewell_Causal-Inference-in-Statistics-A-Primer.pdf
BIB-118_Pearl-Mackenzie_The-Book-of-Why.epub
BIB-119_Peters-Janzing-Scholkopf_Elements-of-Causal-Inference.pdf
BIB-120_Angrist-Pischke_Mostly-Harmless-Econometrics.pdf
BIB-121_Hernan-Robins_Causal-Inference-What-If.pdf
BIB-122_Imbens-Rubin_Causal-Inference-for-Statistics-Social-and-Biomedical-Sciences.pdf
BIB-123_Cunningham_Causal-Inference-The-Mixtape.pdf
```

## 📊 Ekonometria, szeregi czasowe, prognozowanie

```
BIB-124_Hamilton_Time-Series-Analysis.pdf
BIB-125_Box-Jenkins-Reinsel_Time-Series-Analysis-Forecasting-and-Control.pdf
BIB-126_Brockwell-Davis_Introduction-to-Time-Series-and-Forecasting.pdf
BIB-128_Campbell-Lo-MacKinlay_The-Econometrics-of-Financial-Markets.pdf
BIB-129_Cochrane_Asset-Pricing.pdf
BIB-130_Engle_Autoregressive-Conditional-Heteroscedasticity.pdf
BIB-131_Bollerslev_Generalized-Autoregressive-Conditional-Heteroskedasticity.pdf
BIB-132_Hamilton_A-New-Approach-to-the-Economic-Analysis-of-Nonstationary-Time-Series.pdf
BIB-133_Zivot-Wang_Modeling-Financial-Time-Series-with-S-PLUS.pdf
BIB-134_Lutkepohl_New-Introduction-to-Multiple-Time-Series-Analysis.pdf
BIB-135_Enders_Applied-Econometric-Time-Series.pdf
BIB-136_Diebold-Mariano_Comparing-Predictive-Accuracy.pdf
BIB-137_Rabiner_A-Tutorial-on-Hidden-Markov-Models.pdf
BIB-139_Hastie-Tibshirani-Friedman_The-Elements-of-Statistical-Learning.pdf
BIB-140_James-Witten-Hastie-Tibshirani_An-Introduction-to-Statistical-Learning.pdf
BIB-141_Murphy_Probabilistic-Machine-Learning-An-Introduction.pdf
```

## 🎲 Statystyka bayesowska i niepewność

```
BIB-142_Gelman-et-al_Bayesian-Data-Analysis-3rd-ed.pdf
BIB-143_McElreath_Statistical-Rethinking-2nd-ed.pdf
BIB-144_Kruschke_Doing-Bayesian-Data-Analysis.pdf
BIB-145_Sivia-Skilling_Data-Analysis-A-Bayesian-Tutorial.pdf
BIB-146_Jaynes_Probability-Theory-The-Logic-of-Science.pdf
BIB-147_MacKay_Information-Theory-Inference-and-Learning-Algorithms.pdf
BIB-148_Cover-Thomas_Elements-of-Information-Theory.pdf
BIB-149_Efron-Tibshirani_An-Introduction-to-the-Bootstrap.pdf
BIB-150_Shafer-Vovk_Algorithmic-Learning-in-a-Random-World.pdf
BIB-151_Angelopoulos-Bates_A-Gentle-Introduction-to-Conformal-Prediction.pdf
```

## 🏛️ Mikrostruktura i egzekucja

```
BIB-152_Bouchaud-Bonart-Donier-Gould_Trades-Quotes-and-Prices.pdf
BIB-153_Almgren-Chriss_Optimal-Execution-of-Portfolio-Transactions.pdf
BIB-154_Kyle_Continuous-Auctions-and-Insider-Trading.pdf
BIB-155_Glosten-Milgrom_Bid-Ask-and-Transaction-Prices.pdf
BIB-156_Avellaneda-Stoikov_High-Frequency-Trading-in-a-Limit-Order-Book.pdf
BIB-157_Lehalle-Laruelle_Market-Microstructure-in-Practice.pdf
BIB-158_Gueant_The-Financial-Mathematics-of-Market-Liquidity.pdf
BIB-159_Johnson_Algorithmic-Trading-and-DMA.pdf
BIB-160_Foucault-Pagano-Roell_Market-Liquidity-Theory-Evidence-Policy.pdf
BIB-161_Madhavan_Market-Microstructure-A-Survey.pdf
BIB-162_Easley-Lopez-de-Prado-OHara_The-Microstructure-of-the-Flash-Crash.pdf
BIB-163_Menkveld_High-Frequency-Trading-and-the-New-Market-Makers.pdf
BIB-164_Budish-Cramton-Shim_The-High-Frequency-Trading-Arms-Race.pdf
```

## 📐 Optymalizacja i portfel

```
BIB-167_Nocedal-Wright_Numerical-Optimization.pdf
BIB-168_Markowitz_Portfolio-Selection.pdf
BIB-169_Meucci_Risk-and-Asset-Allocation.pdf
BIB-170_Michaud_Efficient-Asset-Management.pdf
BIB-171_Ang_Asset-Management-A-Systematic-Approach-to-Factor-Investing.pdf
BIB-172_Ilmanen_Expected-Returns.pdf
BIB-173_Ilmanen_Investing-Amid-Low-Expected-Returns.epub
BIB-174_Kelly_A-New-Interpretation-of-Information-Rate.pdf
BIB-175_Thorp_The-Kelly-Criterion-in-Blackjack-Sports-Betting-and-the-Stock-Market.pdf
BIB-176_MacLean-Thorp-Ziemba_The-Kelly-Capital-Growth-Investment-Criterion.pdf
BIB-177_Carver_Systematic-Trading.epub
```

## ⚠️ Ryzyko ekstremalne i grube ogony

```
BIB-178_Embrechts-Kluppelberg-Mikosch_Modelling-Extremal-Events.pdf
BIB-179_McNeil-Frey-Embrechts_Quantitative-Risk-Management.pdf
BIB-180_Coles_An-Introduction-to-Statistical-Modeling-of-Extreme-Values.pdf
BIB-181_Taleb_The-Black-Swan.epub
BIB-182_Taleb_Antifragile.epub
BIB-183_Taleb_Skin-in-the-Game.epub
BIB-184_Taleb_Dynamic-Hedging.pdf
BIB-185_Taleb_Statistical-Consequences-of-Fat-Tails.pdf
BIB-186_Sornette_Why-Stock-Markets-Crash.pdf
BIB-187_Rebonato_Plight-of-the-Fortune-Tellers.epub
```

## 🎯 Teoria gier i mechanizmy

```
BIB-188_von-Neumann-Morgenstern_Theory-of-Games-and-Economic-Behavior.pdf
BIB-189_Fudenberg-Tirole_Game-Theory.pdf
BIB-190_Osborne-Rubinstein_A-Course-in-Game-Theory.pdf
BIB-191_Myerson_Game-Theory-Analysis-of-Conflict.pdf
BIB-192_Binmore_Game-Theory-A-Very-Short-Introduction.epub
BIB-193_Krishna_Auction-Theory.pdf
BIB-194_Milgrom_Putting-Auction-Theory-to-Work.pdf
BIB-195_Nisan-Roughgarden-Tardos-Vazirani_Algorithmic-Game-Theory.pdf
BIB-196_Roth_Who-Gets-What-and-Why.epub
BIB-197_Schelling_The-Strategy-of-Conflict.pdf
```

## ₿ Krypto zaawansowane, DeFi, MEV

```
BIB-200_Narayanan-et-al_Bitcoin-and-Cryptocurrency-Technologies.pdf
BIB-201_Werner-et-al_SoK-Decentralized-Finance-DeFi.pdf
BIB-202_Angeris-Chitra_Improved-Price-Oracles-Constant-Function-Market-Makers.pdf
BIB-203_Angeris-et-al_An-Analysis-of-Uniswap-Markets.pdf
BIB-204_Qin-Zhou-Gervais_Quantifying-Blockchain-Extractable-Value.pdf
BIB-205_Wood_Ethereum-Yellow-Paper.pdf
BIB-206_Di-Maggio_Blockchain-Crypto-and-DeFi.epub
BIB-207_Schar_Decentralized-Finance-On-Blockchain-and-Smart-Contract-Based-Financial-Markets.pdf
BIB-208_Makarov-Schoar_Trading-and-Arbitrage-in-Cryptocurrency-Markets.pdf
BIB-209_Gudgeon-et-al_DeFi-Protocols-for-Loanable-Funds.pdf
BIB-210_Xu-et-al_SoK-Decentralized-Exchanges-with-Automated-Market-Maker-Protocols.pdf
BIB-211_Eskandari-et-al_SoK-Transparent-Dishonesty-Front-Running-Attacks-on-Blockchain.pdf
```

## 🧠 Decyzje, kalibracja, osąd

```
BIB-212_Tetlock-Gardner_Superforecasting.epub
BIB-213_Tetlock_Expert-Political-Judgment.epub
BIB-214_Silver_The-Signal-and-the-Noise.epub
BIB-215_Kahneman-Sibony-Sunstein_Noise-A-Flaw-in-Human-Judgment.epub
BIB-216_Gigerenzer_Risk-Savvy.epub
BIB-217_Klein_Sources-of-Power.epub
BIB-218_Savage_The-Foundations-of-Statistics.pdf
BIB-219_Brier_Verification-of-Forecasts-Expressed-in-Terms-of-Probability.pdf
BIB-220_Mauboussin_More-Than-You-Know.epub
BIB-221_Mauboussin_The-Success-Equation.epub
```

## 🌐 Systemy złożone, ekonofizyka, ABM

```
BIB-222_Mantegna-Stanley_An-Introduction-to-Econophysics.pdf
BIB-223_Bouchaud-Potters_Theory-of-Financial-Risk-and-Derivative-Pricing.pdf
BIB-224_Sornette_Critical-Phenomena-in-Natural-Sciences.pdf
BIB-225_Mitchell_Complexity-A-Guided-Tour.epub
BIB-226_Arthur_Complexity-and-the-Economy.epub
BIB-227_Farmer_Making-Sense-of-Chaos.epub
BIB-228_Epstein-Axtell_Growing-Artificial-Societies.pdf
BIB-229_Miller-Page_Complex-Adaptive-Systems.pdf
BIB-230_Holland_Adaptation-in-Natural-and-Artificial-Systems.pdf
BIB-231_Page_The-Model-Thinker.epub
```

## 🛠️ Inżynieria: systemy, dane, ML w produkcji

```
BIB-232_Kleppmann_Designing-Data-Intensive-Applications.epub
BIB-233_Huyen_Designing-Machine-Learning-Systems.epub
BIB-234_Burkov_Machine-Learning-Engineering.pdf
BIB-235_Lakshmanan-Robinson-Munn_Machine-Learning-Design-Patterns.epub
BIB-236_Geron_Hands-On-Machine-Learning-with-Scikit-Learn-Keras-and-TensorFlow.epub
BIB-237_Raschka-Liu-Mirjalili_Machine-Learning-with-PyTorch-and-Scikit-Learn.epub
BIB-238_McKinney_Python-for-Data-Analysis.epub
BIB-239_Ramalho_Fluent-Python.epub
BIB-240_Percival-Gregory_Architecture-Patterns-with-Python.epub
BIB-241_Beazley-Jones_Python-Cookbook.epub
BIB-242_Gorelick-Ozsvald_High-Performance-Python.epub
BIB-243_Nygard_Release-It.epub
BIB-244_Beyer-et-al_Site-Reliability-Engineering.pdf
BIB-245_Fowler_Refactoring-2nd-ed.epub
```

## 📰 Dane alternatywne i sentyment

```
BIB-246_Denev-Amen_The-Book-of-Alternative-Data.epub
BIB-247_Kolanovic-Krishnamachari_Big-Data-and-AI-Strategies.pdf
BIB-248_Tetlock_Giving-Content-to-Investor-Sentiment.pdf
BIB-249_Loughran-McDonald_When-Is-a-Liability-Not-a-Liability.pdf
BIB-250_Baker-Wurgler_Investor-Sentiment-in-the-Stock-Market.pdf
BIB-251_Bollen-Mao-Zeng_Twitter-Mood-Predicts-the-Stock-Market.pdf
BIB-252_Araci_FinBERT-Financial-Sentiment-Analysis-with-Pre-trained-Language-Models.pdf
BIB-253_Ke-Kelly-Xiu_Predicting-Returns-with-Text-Data.pdf
```

## 📈 Uzupełnienia tradingowe i klasyka

```
BIB-254_Tharp_Trade-Your-Way-to-Financial-Freedom.epub
BIB-255_Schwager_The-New-Market-Wizards.epub
BIB-256_Schwager_Hedge-Fund-Market-Wizards.epub
BIB-257_Schwager_Unknown-Market-Wizards.epub
BIB-258_Covel_Trend-Following.epub
BIB-259_Faith_Way-of-the-Turtle.epub
BIB-260_Clenow_Following-the-Trend.epub
BIB-261_Clenow_Trading-Evolved.epub
BIB-263_Pardo_The-Evaluation-and-Optimization-of-Trading-Strategies.pdf
BIB-264_Bailey-Lopez-de-Prado_The-Deflated-Sharpe-Ratio.pdf
BIB-265_Bailey-Borwein-Lopez-de-Prado-Zhu_Pseudo-Mathematics-and-Financial-Charlatanism.pdf
BIB-266_Harvey-Liu-Zhu_And-the-Cross-Section-of-Expected-Returns.pdf
BIB-267_Fama-French_Common-Risk-Factors-in-the-Returns-on-Stocks-and-Bonds.pdf
BIB-268_Jegadeesh-Titman_Returns-to-Buying-Winners-and-Selling-Losers.pdf
BIB-269_Asness-Moskowitz-Pedersen_Value-and-Momentum-Everywhere.pdf
BIB-270_Moskowitz-Ooi-Pedersen_Time-Series-Momentum.pdf
BIB-271_Lo_Adaptive-Markets.epub
BIB-272_Lo-MacKinlay_A-Non-Random-Walk-Down-Wall-Street.pdf
BIB-273_Malkiel_A-Random-Walk-Down-Wall-Street.epub
BIB-274_Wilmott_Paul-Wilmott-Introduces-Quantitative-Finance.pdf
```

---

## ⚠️ Zanim wkleisz — trzy rzeczy

1. **Rozszerzenia to SUGESTIE** (`.pdf` dla artykułów, `.epub` dla książek). Wpisz to, co realnie
   ściągniesz — `przygotuj_biblioteke.py` obsłuży pdf/epub/mobi/azw3/djvu przez Calibre.
3. **Nazwiska bez polskich/diakrytycznych znaków** (Velickovic, Lutkepohl, Barabasi, Gueant, Schar,
   Kluppelberg, Geron, Szepesvari) — celowo, żeby nazwa pliku była bezpieczna na każdym systemie.
