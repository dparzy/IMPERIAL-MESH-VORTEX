---
kategoria: CONSILIUM
typ: zywy
wlasciciel: narzedzia/bibliotekarz.py, narzedzia/przygotuj_biblioteke.py
stan_na: 2026-07-28
powod_istnienia: "PEŁNY spis biblioteki Imperium: 307 pozycji (BIB-001..307) — 69 posiadanych fundamentów, 234 pozycje rozbudowy, każda ze statusem posiadania i obecności w RAG."
---
# 📚 BIBLIOTHECA ULPIA — PEŁNY SPIS: BIB-001 … BIB-307

## 🗂️ STAN PRZETWORZENIA — ZMIERZONY 2026-07-28 (nie z pamięci)

🚨 **POPRZEDNI WPIS TEGO ROZDZIAŁU BYŁ NIEAKTUALNY O 90 KSIĄŻEK.** Głosił „115 plików BIB, wszystkie
wyekstraktowane + w RAG + skatalogowane" — i to była prawda **2026-07-21**. Od tego czasu Cezar dograł
90 tytułów, a `przygotuj_biblioteke.py` **nie był ani razu uruchomiony**. Dokument o tym milczał, bo
**żadna warstwa audytu nie pilnuje księgozbioru** (Warstwa 11 dotyczy `imperium/biblioteki/`, czyli
modułów kodu, nie ksiąg). Audyt drukował „pełna harmonia" przy 43% biblioteki poza zasięgiem RAG.

| Warstwa | Ile | Skąd zmierzone |
|---|---|---|
| Pliki książek na dysku | **207 w korpusie** + 2 poza | `bibliotheca_ulpia/*.{epub,pdf,azw3,mobi,djvu}` |
| Zgodne ze schematem nazw | **209 / 209** ✅ | naprawione 2026-07-28 (było 114) |
| **Opisane w tym dokumencie** | **209 / 209** ✅ | naprawione 2026-07-28 (było 133 — brakowało całego fundamentu BIB-001..069) |
| W katalogu metadanych | **115** | `katalog_ksiag.json` |
| W cache tekstu | **117** | `tekst_cache/*.txt` — +2 z naszego OCR (BIB-136, BIB-155) | `tekst_cache/*.txt` |
| **Wyszukiwalne w RAG** | **115** | `baza_wiedzy.db` → 37 331 fragmentów |
| **POZA RAG (dograne, nieprzetworzone)** | **92** | 614 MB — czekają na `przygotuj_biblioteke.py` (+2 świadomie wyłączone) | 614 MB — czekają na `przygotuj_biblioteke.py` |

**Podział 307 pozycji spisu:**

| Blok | Pozycji | Mamy plik | W RAG | Fragmentów |
|---|---|---|---|---|
| **BIB-001..069** — fundament | 69 | **69** ✅ | **69** ✅ | 27 829 |
| **BIB-070..274** — rozbudowa | 205 | 133 | 46 | 9 368 |
| **BIB-275..300** — Consilium (osądzone) | 26 | 0 | 0 | — |
| **BIB-301..307** — dołożone poza planem | 7 | **7** (2 poza korpusem) | 0 | — |
| **RAZEM** | **307** | **209** | **115** | **37 197** |

*(37 197 to fragmenty samych książek; korpus `biblioteka` w RAG ma 37 253 — różnicę 56 dają
pliki encyklopedii i vademecum.)*

Do zdobycia zostaje **69 pozycji** rdzenia (BIB-205..274 bez martwego slotu 262) + 26 pozycji
Consilium. Martwe sloty odsyłaczowe, które pliku nie wymagają: **198, 199, 262, 296**.

**Charakter 90 nowych: kanon przyczynowości, szeregów czasowych, mikrostruktury, teorii gier i
ryzyka ekstremalnego** — czyli źródła, na których stoją nasze neurony (Kyle, Engle-ARCH,
Hamilton-reżimy, Rabiner-HMM, Kelly-Thorp).

**Plan katalogowania esencji — 4 etapy, po jednej sesji (ZASADA ANALIZY CZĄSTKOWEJ — cząstkowo,
zapisywalnie, wznawialnie; Hyginus=DeepSeek tani zwiad → kolejka JSONL, Opus=sędzia całej partii):**

| Etap | Klaster | Książki | Esencja czego |
|---|---|---|---|
| **1** | LLM/TIRO fundamenty | BIB-080–093 (14) | jak trenować TIRO: transformer→distillation→LoRA/QLoRA→RAG |
| **2** | LLM optymalizacja/alignment | BIB-094–099 (6) | scaling, Chinchilla, InstructGPT, DPO, GPTQ, spec-decoding |
| **3** | Graph Neural Networks | BIB-100–107 (8) | kandydaci dla grafu pamięci W8 / synaps reżimowych |
| **4** | RL + przyczynowość | BIB-108–116 (9) | kandydaci sizing / decyzje sekwencyjne |

Każdy etap kończy się zapisem kandydatów do kolejki (JSONL w git) — bieg, który padnie, wznawia się
od pierwszej niezapisanej książki. Wpięcie kandydata w kod dopiero po pomiarze areny (KANDYDAT≠PRAWDA).



> **Stan na:** 2026-07-16 · **Autor listy:** VITRUVIUSZ (Opus) · **Rozkaz Cezara:** „rozbuduj bibliotekę,
> dawaj do 200 pozycji lub więcej, niech nasz LLM się uczy"
> **Stan w chwili pisania listy (2026-07-16):** 69 książek (BIB-001..069) · **Ta lista:** 205 pozycji (BIB-070..274)
> **Stan ZMIERZONY 2026-07-28:** 209 plików na dysku (207 w korpusie + 2 świadomie poza) · 115 w RAG · 90 czeka na ekstrakcję · +26 pozycji
> Consilium (BIB-275..300) i 7 dołożonych (BIB-301..307) — razem **238 pozycji planu (BIB-070..307)**.

## 🔴 CZYTAJ NAJPIERW — status weryfikacji (Prawo I, ZPO)

Numery BIB nadane **przeze mnie, jednorazowo i spójnie** — nie przez DeepSeeka. (Poprzednia lista
z `wrzutnia/Mapa-kluczy calosc plus.md` miała **sześć sprzecznych numeracji**, dziesiątki pozycji
z autorem „–" i fabrykowane cytowania — patrz `docs/` + pamięć `lista-ksiazek-deepseek-smiec`.)

**Legenda pewności — czytaj dosłownie, nie udaję weryfikacji:**
| Znak | Znaczenie |
|---|---|
| ✅ | **Kanon** — dzieło, którego istnienia jestem pewien (klasyk, wielokrotnie wydawany). Rok/wydanie **potwierdź przed zakupem**. |
| ⚠️ | **Do weryfikacji** — pozycja prawdopodobna, ale NIE potwierdzona w tej sesji. Sprawdź przed wydaniem pieniędzy. |

⚠️ **Mój cutoff wiedzy to styczeń 2026** — pozycje z 2025/2026 są z natury mniej pewne. Żadna data
wydania na tej liście nie jest zweryfikowana w tej sesji; traktuj rok jako orientacyjny.

**Zasada doboru (LIMA dla książek):** preferuję **kanon nad nowość** — 200 prawdziwych, cytowanych
dzieł uczy lepiej niż 400 modnych tytułów. Uczeń TIRO nauczy się tego, co mu damy.

---

## 📚 FUNDAMENT — BIB-001..069 (biblioteka sprzed tej listy)

🚨 **DOPISANE 2026-07-28 NA ROZKAZ CEZARA — dokument przez 12 dni opisywał tylko przyrost.**
Plan powstał 2026-07-16 jako lista **rozbudowy** (BIB-070+) i milcząco zakładał, że fundament
„wszyscy znają". Efekt: żaden dokument nie zawierał **pełnej listy biblioteki** — 69 książek
istniało wyłącznie jako pliki na dysku i wiersze w `katalog_ksiag.json`. Kto pytał „co mamy?",
dostawał odpowiedź o 234 pozycjach planu, nie o 303 pozycjach Imperium.

**Stan zmierzony 2026-07-28:** 69 plików · **69 w RAG** · **27 829 fragmentów** (74.6% całego
korpusu książkowego). To jedyny blok biblioteki, który jest **w 100% przetworzony** — nowsze
BIB-070+ mają 87 pozycji czekających na ekstrakcję.

Autor i tytuł **odczytane z nazw plików** (zgodnych ze schematem), rok i wydawca z
`katalog_ksiag.json` (calibre), liczba fragmentów z `baza_wiedzy.db`. Nic z pamięci.

### 📈 Analiza techniczna, price action, klasyka tradingu

> Karmi: wskaźniki, EMA/HMA, profil rynku, formacje

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 002 | Murphy | *Technical Analysis of the Financial Markets* (1999) | azw3 | 337 |
| 013 | Dalton | *Markets in Profile* (2010) | epub | 174 |
| 014 | Dalton | *Mind Over Markets* (2013) | epub | 229 |
| 015 | Elder | *The New Trading for a Living* (2014) | epub | 342 |
| 021 | Anon | *High Win Rate Day Trading Setups* (2022) | azw3 | 17 |
| 047 | Kaufman | *Trading Systems and Methods* (2019) | pdf | 1125 |
| 049 | Bulkowski | *Encyclopedia of Chart Patterns* (2021) | epub | 1294 |
| 006 | Carson | *High Probability Scalping Strategy Playbook* (2024) | epub | 36 |
| 001 | Patel | *The Secret Wealth Advantage* (2023) | azw3 | 313 |

### 🧠 Psychologia i dyscyplina tradera

> Karmi: PSY-01..05, Senat, Reguła 6%

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 004 | Steenbarger | *The Psychology of Trading* (2007) | azw3 | 386 |
| 016 | Douglas | *Trading in the Zone* (2010) | epub | 212 |
| 017 | Kahneman | *Thinking Fast and Slow* (2011) | epub | 547 |
| 050 | Douglas | *The Disciplined Trader* (2004) | pdf | 237 |
| 051 | Duke | *Thinking in Bets* (2018) | epub | 235 |
| 052 | Steenbarger | *Trading Psychology 2.0* (2015) | epub | 475 |
| 038 | Schwager | *Market Wizards Interviews with Top Traders* (2018) | epub | 423 |
| 039 | Lefevre | *Reminiscences of a Stock Operator* (2010) | epub | 583 |

### 🔬 Quant, ML i badania ilościowe

> Karmi: rdzeń metodologii: DSR/PBO/purged-CV, meta-labeling, IC

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 007 | Lopez de Prado | *Advances in Financial Machine Learning* (2018) | epub | 293 |
| 010 | Chan | *Quantitative Trading 2nd ed* (2021) | epub | 192 |
| 011 | Chan | *Algorithmic Trading Winning Strategies* | pdf | 17 |
| 023 | Lopez de Prado | *Machine Learning for Asset Managers* (2022) | pdf | 133 |
| 026 | Jansen | *Machine Learning for Algorithmic Trading* (2020) | mobi | 707 |
| 028 | Narang | *Inside the Black Box A Simple Guide to Systematic Investing* (2024) | epub | 392 |
| 031 | Tsay | *Analysis of Financial Time Series* | pdf | 593 |
| 045 | Hilpisch | *Python for Finance* (2018) | epub | 220 |
| 046 | Chan | *Machine Trading* | epub | 222 |
| 048 | Aronson | *Evidence Based Technical Analysis* | djvu | 534 |
| 068 | Goodfellow Bengio Courville | *Deep Learning* (2017) | pdf | 854 |
| 067 | Sutton Barto | *Reinforcement Learning An Introduction 2nd ed* | djvu | 695 |

### 🏛️ Mikrostruktura, HFT i egzekucja

> Karmi: Z-01 VPIN, V-03 CVD, EXP-12/14/15, OMS

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 020 | Harris | *Trading and Exchanges Market Microstructure for Practitioners* (2002) | epub | 885 |
| 022 | Kissell | *Optimal trading strategies* | djvu | 367 |
| 027 | Aldridge | *High Frequency Trading* (2013) | epub | 299 |
| 032 | OHara | *Market Microstructure Theory* (0101) | pdf | 319 |
| 043 | Cartea Jaimungal Penalva | *Algorithmic and High Frequency Trading* (2016) | pdf | 378 |
| 044 | Hasbrouck | *Empirical Market Microstructure* (2007) | pdf | 220 |

### ⚠️ Ryzyko, zmienność, grube ogony

> Karmi: Z-01..07, HALT, ECON/Feynman-Kac

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 008 | Sinclair | *Volatility Trading 2nd ed* (2013) | azw3 | 240 |
| 009 | Mandelbrot Hudson | *The Misbehavior of Markets* (2011) | epub | 289 |
| 018 | Sinclair | *Positional Option Trading* (2020) | epub | 187 |
| 037 | Hull | *Options Futures and Other Derivatives* (2021) | epub | 1165 |
| 041 | Taleb | *Fooled by Randomness* (2016) | epub | 1351 |
| 042 | Jorion | *Value at Risk The New Benchmark* (2007) | epub | 492 |
| 065 | Shreve | *Stochastic Calculus for Finance I Binomial Asset Pricing* | djvu | 172 |
| 066 | Shreve | *Stochastic Calculus for Finance II Continuous Time Models* | djvu | 200 |

### 🌍 Makro, cykle długu, bańki i behawioryzm

> Karmi: RADAR-01..05, Gubernator, Z-03/04/07

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 025 | Grinold Kahn | *Active Portfolio Management* (2020) | epub | 555 |
| 040 | Bernstein | *Against the Gods The Remarkable Story of Risk* (2011) | epub | 354 |
| 056 | Dalio | *Principles for Navigating Big Debt Crises* (2018) | epub | 532 |
| 057 | Dalio | *Principles for Dealing with the Changing World Order* (2021) | epub | 474 |
| 058 | Dalio | *How Countries Go Broke The Big Cycle* (2025) | epub | 338 |
| 059 | Kindleberger Aliber | *Manias Panics and Crashes* | epub | 502 |
| 060 | Shiller | *Irrational Exuberance* (2014) | pdf | 474 |
| 061 | Thaler | *Misbehaving The Making of Behavioral Economics* (2015) | epub | 414 |
| 062 | Chancellor | *Devil Take the Hindmost* (2000) | epub | 422 |
| 063 | MacKay | *Extraordinary Popular Delusions and the Madness of Crowds* (2023) | epub | 848 |
| 064 | Reinhart Rogoff | *This Time Is Different* (2009) | epub | 325 |

### ₿ Krypto, blockchain i tokenomika

> Karmi: OC-01..08, RADAR-02/03, Straż A-*

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 003 | Burniske Tatar | *Cryptoassets* (2017) | azw3 | 330 |
| 005 | Blum | *What Exactly Is Crypto* (2022) | epub | 96 |
| 019 | Harris | *Handbook for Cryptocurrencies Trading* (2022) | epub | 87 |
| 024 | Lowe | *Bitcoin and Cryptocurrency Trading for Beginners* (2021) | epub | 91 |
| 029 | Bashir | *Mastering Blockchain* (2023) | epub | 765 |
| 030 | Ammous | *The Bitcoin Standard* (2018) | epub | 304 |
| 053 | Antonopoulos Harding | *Mastering Bitcoin 3rd ed* (2023) | mobi | 86 |
| 054 | Antonopoulos Wood | *Mastering Ethereum* (2025) | epub | 487 |
| 055 | Popper | *Digital Gold* (2015) | epub | 322 |
| 069 | Voshmgir | *Token Economy 3rd ed* (2023) | epub | 274 |

### 🤖 AI, LLM i agenci

> Karmi: TIRO, RAG, warstwy pamięci W1..W22

| BIB | Autor | Tytuł | Format | Fragm. w RAG |
|---|---|---|---|---|
| 033 | Huyen | *AI Engineering Building Applications with Foundation Models* (2024) | epub | 496 |
| 034 | Infante | *AI Agents and Applications LangChain LangGraph MCP* (2025) | epub | 312 |
| 035 | Iusztin Labonne | *LLM Engineers Handbook* (2024) | azw3 | 86 |
| 036 | Alto | *Building LLM Powered Applications* (2024) | epub | 249 |
| 012 | Strauss van der Post | *Coding Capital* (2024) | epub | 225 |

> ⚖️ **Uczciwie:** ten blok jest **inwentarzem**, nie rekomendacją — te książki już mamy,
> więc znacznik pewności (✅/⚠️/) nie ma tu zastosowania. Przydział do działów encyklopedii
> opisuje `bibliotheca_ulpia/encyklopedia/INDEX_MAIOR.md`. ⚠️ Ta mapa pokrywa **tylko ten blok**
> — 136 nowszych książek nie ma jeszcze przypisanego działu.

---

## 🎯 Priorytet 0 — ✅ **DOMKNIĘTY 2026-07-16** (wszystkie w bibliotece i w RAG)

> Stan: **79 książek, 29 699 fragmentów.** BIB-070..079 zaindeksowane, treść każdej
> **zweryfikowana czytaniem tekstu**, nie nazwy pliku (BIB-073 okazał się zbiorem zadań —
> patrz niżej). Zerowe luki zamknięte: transformery, VPIN, prognozowanie, optymalizacja,
> MEV/DeFi u źródła, reguły punktacji pod Sybillę.

| BIB | Autor | Tytuł | Dlaczego teraz |
|---|---|---|---|
| 070 | Vaswani i in. | *Attention Is All You Need* (2017) ✅ | Fundament transformerów — **wprost pod TIRO**. arXiv:1706.03762 |
| 071 | Easley, López de Prado, O'Hara | *Flow Toxicity and Liquidity in a High-Frequency World* (RFS 2012) ✅ | **Źródło naszego neuronu Z-01 (VPIN)** — mamy neuron, nie mamy źródła |
| 072 | Hyndman, Athanasopoulos | *Forecasting: Principles and Practice* (**2nd ed.**) ✅ **W BIBLIOTECE** | ✅ **ZAINDEKSOWANA 2026-07-16** — Cezar ma **kupiony** egzemplarz (PDF, 2. edycja) z własnego dysku. 257 fragmentów w RAG, korpus 27 959 → 28 535. Kanon prognozowania — domyka zerową lukę (mamy WFO i Sybillę z Brierem, nie mieliśmy teorii). 3. edycja różni się głównie przejściem `forecast`→`fable` (R), dla nas bez znaczenia |
| 073 | Boyd, Vandenberghe | *Convex Optimization* ✅ **W BIBLIOTECE** | ✅ **ZAINDEKSOWANY 2026-07-16** — 734 fragmenty. Plik: `bv_cvxbook.pdf` ze https://web.stanford.edu/~boyd/cvxbook/ |
| 074 | Boyd, Vandenberghe | *Additional Exercises for Convex Optimization* ✅ **W BIBLIOTECE** | ✅ **ZAINDEKSOWANY 2026-07-16** — 517 fragmentów. Numer był wolny (spalony na odsyłacz do Goodfellowa = BIB-068). ⚠️ **PUŁAPKA:** na stronie Boyda leżą OBOK SIEBIE dwa PDF-y; ten zbiór zadań pobrał się zamiast podręcznika i wpadł pod nazwą „Convex-Optimization" — wykryte dopiero czytaniem treści, nie nazwy. Wartość dla TIRO realna: **rozwiązane zadania pokazują rozumowanie krok po kroku**, nie samą teorię |
| 075 | Nakamoto | *Bitcoin: A Peer-to-Peer Electronic Cash System* ✅ **W BIBLIOTECE** | ✅ 10 frag. (⚠️ moja pomyłka w 1. wersji listy: przypisałem współautora „Daspremont" — to **wyłącznie Nakamoto**). 🐞 Ten plik ujawnił bug ebooklib (patrz niżej) |
| 076 | Buterin | *Ethereum Whitepaper* ✅ **W BIBLIOTECE** | ✅ 40 frag. — źródło zamiast opracowań |
| 077 | Daian i in. | *Flash Boys 2.0: Frontrunning in Decentralized Exchanges…* (2019) ✅ **W BIBLIOTECE** | ✅ 42 frag. — **kanoniczne źródło o MEV**, było zero u nas |
| 078 | Adams, Zinsmeister i in. | *Uniswap v3 Core* (2021) ✅ **W BIBLIOTECE** | ✅ 19 frag. — mechanika AMM u źródła (autorzy potwierdzeni treścią: Hayden Adams, Noah Zinsmeister) |
| 079 | Gneiting, Raftery | *Strictly Proper Scoring Rules, Prediction, and Estimation* (JASA 2007) ✅ **W BIBLIOTECE** | ✅ 53 frag. — **teoria pod Brier/Sybillę**; RAG zwraca definicje regularnych reguł punktacji. Mieliśmy Księgi Sybillińskie bez teorii |

### 🐞 Bug ujawniony przy BIB-075 (naprawiony 2026-07-16)
Whitepaper Bitcoina (epub) ekstrahował **0 znaków**. Winowajcą NIE był plik (poprawny epub, 36 plików,
komplet rozdziałów) tylko **`ebooklib` 0.20.0**: robi `html_node.xpath("//nav[@*='toc']")[0]` bez
zabezpieczenia → `IndexError` na epubie, którego nawigacja nie ma elementu oznaczonego `toc`
(standard tego nie wymaga). Naprawa w `narzedzia/rag/ekstraktor.py`: wyjątek **lub pusty wynik** →
fallback na calibre (ten sam wzorzec, którego używa już `_djvu`). Po naprawie: 20 884 znaki, komplet
fraz (peer-to-peer, proof-of-work, double-spend, merkle). 3 testy pilnują regresji.

---

## 🤖 Transformery / LLM / NLP — **pod TIRO** (BIB-080..099)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 080 | Jurafsky, Martin | *Speech and Language Processing* (3rd ed.) ✅ | Darmowy draft — biblia NLP |
| 081 | Tunstall, von Werra, Wolf | *Natural Language Processing with Transformers* ✅ | Praktyka HuggingFace |
| 082 | Rothman | *Transformers for Natural Language Processing* ⚠️ | |
| 083 | Bishop | *Pattern Recognition and Machine Learning* (Springer, Information Science and Statistics) ✅ 📁 **MAMY PLIK** | ✅ **PODRĘCZNIK POTWIERDZONY 2026-07-28** — strona tytułowa *Christopher M. Bishop · Pattern Recognition and Machine Learning*, seria pod redakcją M. Jordana, J. Kleinberga i B. Schölkopfa. **703 s., 1 592 260 zn., 24 602 unikalne słowa.** Kontrola rozstrzygająca: fraza *Solutions to the Exercises* **NIEOBECNA** — czyli to naprawdę podręcznik, nie zbiór rozwiązań. Nazwisko *Svensén* pada wyłącznie w podziękowaniach (pomoc przy rysunkach i składzie LaTeX), nie w autorstwie. **Kanon ML — drugi filar obok Hastie-ESL (BIB-139)** ⏳ poza RAG |
| 084 | Devlin i in. | *BERT: Pre-training of Deep Bidirectional Transformers* ✅ | arXiv |
| 085 | Brown i in. | *Language Models are Few-Shot Learners* (GPT-3) ✅ | arXiv |
| 086 | Hu i in. | *LoRA: Low-Rank Adaptation of Large Language Models* ✅ | **Wprost nasza metoda treningu (E4)** |
| 087 | Dettmers i in. | *QLoRA: Efficient Finetuning of Quantized LLMs* ✅ | **Nasza ścieżka na RTX 4050** |
| 088 | Hinton i in. | *Distilling the Knowledge in a Neural Network* ✅ | **Fundament distylacji = Filar 2 TIRO** |
| 089 | Wei i in. | *Chain-of-Thought Prompting…* ✅ | arXiv |
| 090 | Wang i in. | *Self-Consistency Improves Chain of Thought Reasoning* ✅ | **Teoria pod nasz konsensus próbek** |
| 091 | Zhou i in. | *LIMA: Less Is More for Alignment* ✅ | **Źródło naszej zasady „1000 doskonałych > 50000 miernych"** |
| 092 | Lewis i in. | *Retrieval-Augmented Generation…* ✅ | Fundament naszego RAG |
| 093 | Raschka | *Build a Large Language Model (From Scratch)* ⚠️ | |
| 094 | Kaplan i in. | *Scaling Laws for Neural Language Models* ✅ | Dlaczego mały model ma sufit |
| 095 | Hoffmann i in. | *Training Compute-Optimal LLMs* (Chinchilla) ✅ | |
| 096 | Ouyang i in. | *Training LMs to follow instructions with human feedback* (InstructGPT) ✅ | |
| 097 | Rafailov i in. | *Direct Preference Optimization (DPO)* ✅ | Alternatywa dla RLHF |
| 098 | Frantar i in. | *GPTQ: Accurate Post-Training Quantization* ✅ | Kwantyzacja — nasz Q4_K_M |
| 099 | Leviathan i in. | *Fast Inference from Transformers via Speculative Decoding* ✅ | **Źródło dźwigni, którą chcemy zmierzyć** |

## 🕸️ Graph Neural Networks — **luka zerowa** (BIB-100..107)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 100 | Hamilton | *Graph Representation Learning* ✅ | Darmowy PDF autora |
| 101 | Wu, Cui, Pei, Zhao | *Graph Neural Networks: Foundations, Frontiers, and Applications* ⚠️ | |
| 102 | Labonne | *Hands-On Graph Neural Networks Using Python* ⚠️ | Praktyka |
| 103 | Kipf, Welling | *Semi-Supervised Classification with Graph Convolutional Networks* ✅ | Fundament GCN |
| 104 | Veličković i in. | *Graph Attention Networks* ✅ | |
| 105 | Battaglia i in. | *Relational inductive biases, deep learning, and graph networks* ✅ | |
| 106 | Barabási | *Network Science* ✅ | Darmowy online — sieci jako zjawisko |
| 107 | Newman | *Networks: An Introduction* ✅ | Kanon |

## 🎮 Reinforcement Learning praktyczny — mamy tylko teorię (BIB-108..115)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 108 | Lapan | *Deep Reinforcement Learning Hands-On* (3rd ed.) ⚠️ | Praktyka: DQN/PPO/RLHF |
| 109 | Graesser, Keng | *Foundations of Deep Reinforcement Learning* ⚠️ | |
| 110 | Mnih i in. | *Human-level control through deep RL* (DQN, Nature 2015) ✅ | |
| 111 | Schulman i in. | *Proximal Policy Optimization Algorithms* ✅ | PPO |
| 112 | Silver i in. | *Deterministic Policy Gradient Algorithms* ⚠️ | |
| 113 | Szepesvári | *Algorithms for Reinforcement Learning* ✅ | Zwięzły kanon |
| 114 | Bertsekas | *Reinforcement Learning and Optimal Control* ⚠️ | |
| 115 | Powell | *Approximate Dynamic Programming* ⚠️ | |

## 🔗 Wnioskowanie przyczynowe — **luka zerowa** (BIB-116..123)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 116 | Pearl | *Causality: Models, Reasoning, and Inference* (2nd ed.) ✅ | **Kanon absolutny** |
| 117 | Pearl, Glymour, Jewell | *Causal Inference in Statistics: A Primer* ✅ | Łagodniejsze wejście |
| 118 | Pearl, Mackenzie | *The Book of Why* ✅ | Popularne, dobre na start |
| 119 | Peters, Janzing, Schölkopf | *Elements of Causal Inference* ✅ | Darmowy PDF (MIT Press) |
| 120 | Angrist, Pischke | *Mostly Harmless Econometrics* ✅ | Przyczynowość empiryczna |
| 121 | Hernán, Robins | *Causal Inference: What If* ✅ | Darmowy PDF autorów |
| 122 | Imbens, Rubin | *Causal Inference for Statistics…* ✅ | |
| 123 | Cunningham | *Causal Inference: The Mixtape* ✅ | Darmowy online |

## 📊 Ekonometria, szeregi czasowe, prognozowanie (BIB-124..141)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 124 | Hamilton | *Time Series Analysis* ✅ | Kanon (nie mylić z GNN-Hamiltonem) |
| 125 | Box, Jenkins, Reinsel | *Time Series Analysis: Forecasting and Control* ✅ | |
| 126 | Brockwell, Davis | *Introduction to Time Series and Forecasting* ✅ | |
| 127 | Shumway, Stoffer | *Time Series Analysis and Its Applications: With R Examples* (**4th ed.**) ✅ 📁 **MAMY PLIK** | ✅ **TREŚĆ POTWIERDZONA** (Springer Texts in Statistics, 4. edycja, 6.0 MB). Slot był martwym odsyłaczem „Hyndman → BIB-072"; Consilium wypełniło go sensownie — dokłada **przestrzeń stanów i analizę spektralną**, których Hyndman (BIB-072) nie ma. ⏳ poza RAG |
| 128 | Campbell, Lo, MacKinlay | *The Econometrics of Financial Markets* (Princeton UP 1997, ISBN 0-691-04301-9) ✅ 📁 **MAMY PLIK** | ✅ **POTWIERDZONE 2026-07-28** — strona praw: *Copyright © 1997 by Princeton University Press · Campbell, John Y · Andrew W. Lo · A. Craig MacKinlay*. **1 380 803 zn.** — najgrubszy plon dnia. ⚠️ Format **DJVU**, więc ekstrakcja **wymaga Calibre** (`C:\Calibre Portable\Calibre` w PATH); chmura przeczyta go z wersjonowanego `tekst_cache`. Jakość OCR w treści bardzo dobra (spisy treści miejscami pokiereszowane: *„Event-Stu^ Analysis"*). Kontrola: event study, CAPM, random walk, data-snooping — obecne ⏳ poza RAG |
| 129 | Cochrane | *Asset Pricing* ✅ | |
| 130 | Engle | *Autoregressive Conditional Heteroscedasticity with Estimates of the Variance of United Kingdom Inflation* (Econometrica 1982, 50(4), 987–1007) ✅ 📁 **MAMY PLIK** | ✅ **ORYGINAŁ POTWIERDZONY 2026-07-28** — strona tytułowa: *„Author(s): Robert F. Engle · Source: Econometrica, Jul., 1982, Vol. 50, No. 4"*, JSTOR `stable/1912773`. 22 s., **51 142 zn.** warstwy tekstowej. **Źródło ARCH → nasz EXP-13 GARCH**. Para ze źródłem BIB-131 (Bollerslev 1986) domknięta ⏳ poza RAG |
| 131 | Bollerslev | *Generalized ARCH* ✅ | |
| 132 | Hamilton | *A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle* (Econometrica 1989, 57(2), 357–384) ✅ 📁 **MAMY PLIK** | ✅ **ORYGINAŁ POTWIERDZONY 2026-07-28** — *„Author(s): James D. Hamilton · Econometrica, Mar., 1989, Vol. 57, No. 2"*, JSTOR `stable/1912559`. 29 s., **67 915 zn.** Streszczenie potwierdza treść: *„parameters of an autoregression are viewed as the outcome of a discrete-state **Markov** process"*. **Regime-switching u źródła → Namiestnik + Viterbi Jump Model** ⏳ poza RAG |
| 133 | Zivot, Wang | *Modeling Financial Time Series with S-PLUS* ⚠️ | |
| 134 | Lütkepohl | *New Introduction to Multiple Time Series Analysis* ✅ | VAR |
| 135 | Enders | *Applied Econometric Time Series* ✅ | |
| 136 | Diebold, Mariano | *Comparing Predictive Accuracy* (JBES 1995, 13(3), 253–263) ✅ 📁 **MAMY PLIK** | ✅ **POTWIERDZONE 2026-07-28, ale dopiero PO OCR U NAS.** Plik był skanem ProQuest: 11 stron, **1 298 zn. = stopka *„Reproduced with permission of the copyright owner"* × 11, 32 unikalne słowa**. Po naszym OCR: **49 912 zn. / 3 141 unikalnych słów**. Abstrakt potwierdza treść (*„null hypothesis of no difference in the accuracy of two competing forecasts… loss function need not be quadratic"*). **Test przewagi prognoz — wprost pod nasze A/B** ✅ **w cache, czeka na reindeks** |
| 137 | Rabiner | *A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition* (Proc. IEEE 77(2), 1989, 257–286) ✅ 📁 **MAMY PLIK** | ✅ **ORYGINAŁ POTWIERDZONY 2026-07-28** — nagłówek *„LAWRENCE R. RABINER, FELLOW, IEEE"*, metadane `author=IEEE`. 30 s., **150 305 zn.** Sprawdzone, że niesie **sekcję V „Implementation Issues"**, której brak streszczeniom: skalowanie, wiele sekwencji obserwacji, estymaty początkowe, niedobór danych treningowych. **HMM u źródła → Viterbi Jump Model** ⏳ poza RAG |
| 138 | Tsay | *Multivariate Time Series Analysis: With R and Financial Applications* (2014) ✅ 📁 **MAMY PLIK** | ✅ **TREŚĆ POTWIERDZONA** (Wiley 2014, Booth School, 5.8 MB). Slot był odsyłaczem „Tsay → mamy BIB-031"; to **inna książka tego samego autora** — VAR/VECM/modele czynnikowe, czyli wielowymiarowość, której BIB-031 nie obejmuje. ⏳ poza RAG |
| 139 | Hastie, Tibshirani, Friedman | *The Elements of Statistical Learning* ✅ | Darmowy PDF — kanon ML |
| 140 | James i in. | *An Introduction to Statistical Learning* ✅ | Darmowy PDF |
| 141 | Murphy | *Probabilistic Machine Learning: An Introduction* / *Advanced Topics* ⚠️ | Dwa tomy — wejście i tematy zaawansowane |

## 🎲 Statystyka bayesowska i niepewność (BIB-142..151)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 142 | Gelman i in. | *Bayesian Data Analysis* (3rd ed.) ✅ | Darmowy PDF — kanon |
| 143 | McElreath | *Statistical Rethinking* (2nd ed.) ✅ | Najlepsze wejście w Bayesa |
| 144 | Kruschke | *Doing Bayesian Data Analysis* ✅ | |
| 145 | Sivia, Skilling | *Data Analysis: A Bayesian Tutorial* ⚠️ | |
| 146 | Jaynes | *Probability Theory: The Logic of Science* ✅ | Filozofia + matematyka |
| 147 | MacKay | *Information Theory, Inference, and Learning Algorithms* ✅ | Darmowy PDF — **teoria informacji + ML w jednym** |
| 148 | Cover, Thomas | *Elements of Information Theory* ✅ | Kanon teorii informacji |
| 149 | Efron, Tibshirani | *An Introduction to the Bootstrap* ✅ | **Pod nasze testy istotności** |
| 150 | Shafer, Vovk | *Algorithmic Learning in a Random World* ⚠️ | **Predykcja konformalna — mamy bramkę ML-36!** |
| 151 | Angelopoulos, Bates | *A Gentle Introduction to Conformal Prediction* ✅ | arXiv — nowsze wejście |

## 🏛️ Mikrostruktura i egzekucja (BIB-152..165)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 152 | Bouchaud, Bonart, Donier, Gould | *Trades, Quotes and Prices* ✅ | **Kanon mikrostruktury XXI w.** |
| 153 | Almgren, Chriss | *Optimal Execution of Portfolio Transactions* ✅ | Fundament egzekucji |
| 154 | Kyle | *Continuous Auctions and Insider Trading* (Econometrica 1985, 53(6), 1315–1336) ✅ 📁 **MAMY PLIK** | ✅ **ORYGINAŁ POTWIERDZONY 2026-07-28** — strona tytułowa: *Albert S. Kyle · Econometrica, Vol. 53, No. 6 (Nov., 1985), pp. 1315-1336*. 23 s., **55 676 zn.** To skan, ale **z dobrym OCR**: proza czyta się czysto (żywa pagina *1322 ALBERT S. KYLE*), zniekształcenia tylko na okładce JSTOR. Terminy modelu obecne: market maker, informed trader, noise trader, liquidity, equilibrium. **Model Kyle'a u źródła — fundament mikrostruktury** ⏳ poza RAG |
| 155 | Glosten, Milgrom | *Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders* (JFE 1985) ✅ 📁 **MAMY PLIK** | ✅ **POTWIERDZONE 2026-07-28, ale dopiero PO OCR U NAS.** Plik był skanem Columbia Business School: 30 stron, 560 obrazów, **876 zn. = pieczątka *„COLUMBIA BUSINESS SCHOOL"* × 30, 31 unikalnych słów**. Po naszym OCR: **72 027 zn. / 3 007 unikalnych słów**. Treść potwierdzona (*„proportion of the spread due to adverse selection"*). **Fundament mikrostruktury obok Kyle'a (BIB-154)** ✅ **w cache, czeka na reindeks** |
| 156 | Avellaneda, Stoikov | *High-frequency trading in a limit order book* ✅ | **Kanon market makingu** |
| 157 | Lehalle, Laruelle | *Market Microstructure in Practice* ✅ | |
| 158 | Guéant | *The Financial Mathematics of Market Liquidity* ⚠️ | |
| 159 | Johnson | *Algorithmic Trading & DMA: An Introduction to Direct Access Trading Strategies* (4Myeloma Press 2010) ✅ 📁 **MAMY PLIK** | ✅ **POTWIERDZONE 2026-07-28** — *By Barry Johnson · Copyright © 2010 · Published by 4Myeloma Press, London*. **1 591 009 zn., 26 602 unikalnych słów — nowy rekord biblioteki.** Format **DJVU** (wymaga Calibre). OCR bardzo czysty: `execution` 100% · `order` 100% · `algorithm` 100% · `liquidity` 99.7%. Znak wodny `ForexFinest` ze starego pliku **zniknął** ⏳ poza RAG |
| 160 | Foucault, Pagano, Röell | *Market Liquidity: Theory, Evidence, Policy* ✅ | |
| 161 | Madhavan | *Market Microstructure: A Survey* ⚠️ | |
| 162 | Easley i in. | *The Microstructure of the Flash Crash* ⚠️ | |
| 163 | Menkveld | *High-Frequency Trading and the New Market Makers* ⚠️ | |
| 164 | Budish, Cramton, Shim | *The High-Frequency Trading Arms Race* ✅ | Batch auctions |
| 165 | de Jong, Rindi | *The Microstructure of Financial Markets* (2009) ✅ 📁 **MAMY PLIK** | ✅ **TREŚĆ POTWIERDZONA** (Cambridge UP, metadane autorskie zgodne, 1.1 MB). Slot był odsyłaczem „Hasbrouck → BIB-044"; ta pozycja to **podręcznik graduate** łączący teorię z empirią — inny gatunek niż monografia Hasbroucka. ⏳ poza RAG |

## 📐 Optymalizacja i portfel (BIB-166..177)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 166 | Luenberger, Ye | *Linear and Nonlinear Programming* (**4th ed.**, 2016) ✅ 📁 **MAMY PLIK** | ✅ **TREŚĆ POTWIERDZONA** (Springer ISOR vol. 228, 4. edycja, 6.2 MB). Slot był odsyłaczem „Boyd → BIB-073"; dokłada **stronę algorytmiczną** (simplex, metody wnętrza, dualność), której Boyd — skupiony na wypukłości — nie pokrywa. ⏳ poza RAG |
| 167 | Nocedal, Wright | *Numerical Optimization* ✅ | Kanon |
| 168 | Markowitz | *Portfolio Selection* (1952) ✅ | Źródło teorii portfela |
| 169 | Meucci | *Risk and Asset Allocation* ✅ | |
| 170 | Michaud | *Efficient Asset Management* ⚠️ | |
| 171 | Ang | *Asset Management: A Systematic Approach to Factor Investing* ✅ | |
| 172 | Ilmanen | *Expected Returns* ✅ | |
| 173 | Ilmanen | *Investing Amid Low Expected Returns* ⚠️ | |
| 174 | Kelly | *A New Interpretation of Information Rate* (1956) ✅ | **Kryterium Kelly'ego u źródła — pod sizing** |
| 175 | Thorp | *The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market* (1997) ✅ 📁 **MAMY PLIK** | ✅ **ORYGINAŁ POTWIERDZONY 2026-07-28** — *Edward O. Thorp, Edward O. Thorp and Associates, Newport Beach CA · ©1997 · referat na 10th International Conference on Gambling and Risk Taking, Montreal, czerwiec 1997*. 40 s., **80 230 zn.**, zero stron bez tekstu, mediana 2116 zn./s. Kontrola: Kelly, Blackjack, Sports Betting, capital growth, logarithm, Shannon, Bernoulli — wszystko obecne. ⚠️ OCR **kaleczy wzory** (`P(¥, =-lh)=q`), ale **proza czyta się poprawnie** — a to proza wraca z RAG. **Kelly w praktyce → sizing** ⏳ poza RAG |
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
| 185 | Taleb | *Statistical Consequences of Fat Tails* ✅ | Darmowy — techniczny |
| 186 | Sornette | *Why Stock Markets Crash* ✅ | Ekonofizyka krachów |
| 187 | Rebonato | *Plight of the Fortune Tellers* ⚠️ | |

## 🎯 Teoria gier i mechanizmy — **luka zerowa** (BIB-188..197)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 188 | von Neumann, Morgenstern | *Theory of Games and Economic Behavior* ✅ | **Kanon absolutny** |
| 189 | Fudenberg, Tirole | *Game Theory* (MIT Press) ✅ 📁 **MAMY PLIK** | ✅ **POTWIERDZONE 2026-07-28** — *GAME THEORY · Drew Fudenberg · Jean Tirole · The MIT Press, Cambridge Massachusetts*. **1 477 759 zn.** — rekord biblioteki. Format **DJVU** (wymaga Calibre). ⚠️ **OCR wyraźnie słabszy niż przy BIB-128** — zmierzona czystość terminów: `information` 99.2% · `equilibrium` 96.5% · `beliefs` 95.5% · **`subgame` 88.9%** (34 z 305 wystąpień zepsute na „subgamc"). Znaczy to, że ~11% zapytań o gry podgrywkowe **nie trafi** w FTS. Proza główna czyta się dobrze, gorzej przypisy i drobny druk ⏳ poza RAG |
| 190 | Osborne, Rubinstein | *A Course in Game Theory* ✅ | Darmowy PDF |
| 191 | Myerson | *Game Theory: Analysis of Conflict* ✅ | |
| 192 | Binmore | *Game Theory: A Very Short Introduction* ✅ | ⚠️ **DeepSeek zmyślił tytuł „An Introduction" — to jest właściwy** |
| 193 | Krishna | *Auction Theory* ✅ | Pod aukcje/MEV |
| 194 | Milgrom | *Putting Auction Theory to Work* ✅ | |
| 195 | Nisan i in. | *Algorithmic Game Theory* ✅ | Darmowy PDF |
| 196 | Roth | *Who Gets What — and Why* ✅ | Projektowanie rynków |
| 197 | Schelling | *The Strategy of Conflict* ✅ | |

## ₿ Krypto zaawansowane, DeFi, MEV (BIB-198..211)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 198 | Nakamoto → BIB-075 | — | |
| 199 | Daian i in. → BIB-077 | — | |
| 200 | Narayanan i in. | *Bitcoin and Cryptocurrency Technologies* ✅ | Darmowy — Princeton |
| 201 | Werner i in. | *SoK: Decentralized Finance (DeFi)* ✅ | Systematyzacja DeFi |
| 202 | Angeris, Chitra | *Improved Price Oracles: Constant Function Market Makers* ✅ | **Matematyka AMM** |
| 203 | Angeris i in. | *An Analysis of Uniswap Markets* ✅ | |
| 204 | Qin, Zhou, Gervais | *Quantifying Blockchain Extractable Value* ✅ | MEV mierzalnie |
| 205 | Wood | *Ethereum: A Secure Decentralised Generalised Transaction Ledger* — **Yellow Paper** ✅ | ✏️ **AUTOR POPRAWIONY 2026-07-28** (pytanie Cezara o duplikaty): było „Buterin i in.", a Yellow Paper napisał **Gavin Wood** — Buterin jest autorem *Whitepapera* (BIB-076), to **dwa różne dokumenty**: koncepcja vs formalna specyfikacja EVM. Nie duplikat, ale błędna atrybucja |
| 206 | Di Maggio | *Blockchain, Crypto and DeFi* ⚠️ | |
| 207 | Schär | *Decentralized Finance: On Blockchain- and Smart Contract-Based Financial Markets* ✅ | St. Louis Fed |
| 208 | Makarov, Schoar | *Trading and Arbitrage in Cryptocurrency Markets* ✅ | **Arbitraż krypto empirycznie** |
| 209 | Gudgeon i in. | *DeFi Protocols for Loanable Funds* ⚠️ | |
| 210 | Xu i in. | *SoK: Decentralized Exchanges with Automated Market Maker Protocols* ✅ | |
| 211 | Eskandari i in. | *SoK: Transparent Dishonesty: Front-Running Attacks on Blockchain* ⚠️ | |

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
| 219 | Brier | *Verification of Forecasts Expressed in Terms of Probability* (1950) ✅ | **Źródło naszego Brier score** |
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
| 240 | Percival, Gregory | *Architecture Patterns with Python* ✅ | Darmowy online |
| 241 | Beazley, Jones | *Python Cookbook* ✅ | |
| 242 | Gorelick, Ozsvald | *High Performance Python* ✅ | **Pod nasze wąskie gardła CPU** |
| 243 | Nygard | *Release It!* ✅ | Odporność systemów produkcyjnych |
| 244 | Beyer i in. | *Site Reliability Engineering* ✅ | Darmowy — Google |
| 245 | Fowler | *Refactoring* (2nd ed.) ✅ | |

## 📰 Dane alternatywne i sentyment (BIB-246..253)

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 246 | Denev, Amen | *The Book of Alternative Data* ✅ | Kanon alt-danych |
| 247 | Kolanovic, Krishnamachari | *Big Data and AI Strategies* (JPM 2017) ✅ | Legendarny raport |
| 248 | Tetlock (Paul C.) | *Giving Content to Investor Sentiment* ✅ | **Sentyment newsów u źródła — pod NEWS-01** |
| 249 | Loughran, McDonald | *When Is a Liability Not a Liability?* ✅ | **Słownik sentymentu finansowego** |
| 250 | Baker, Wurgler | *Investor Sentiment in the Stock Market* ✅ | |
| 251 | Bollen, Mao, Zeng | *Twitter mood predicts the stock market* ✅ | Klasyk (i ostrzeżenie o replikacji) |
| 252 | Araci | *FinBERT: Financial Sentiment Analysis with Pre-trained Language Models* ✅ | |
| 253 | Ke, Kelly, Xiu | *Predicting Returns with Text Data* ⚠️ | |

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
| 264 | Bailey, López de Prado | *The Deflated Sharpe Ratio* ✅ | **Mamy DSR w kodzie, nie mamy źródła** |
| 265 | Bailey i in. | *Pseudo-Mathematics and Financial Charlatanism* ✅ | Backtest overfitting |
| 266 | Harvey, Liu, Zhu | *…and the Cross-Section of Expected Returns* ✅ | Multiple testing w finansach |
| 267 | Fama, French | *Common Risk Factors in the Returns on Stocks and Bonds* ✅ | Faktory u źródła |
| 268 | Jegadeesh, Titman | *Returns to Buying Winners and Selling Losers* ✅ | **Momentum u źródła** |
| 269 | Asness, Moskowitz, Pedersen | *Value and Momentum Everywhere* ✅ | |
| 270 | Moskowitz, Ooi, Pedersen | *Time Series Momentum* ✅ | |
| 271 | Lo | *Adaptive Markets* ✅ | **Rynki adaptacyjne — nasza doktryna reżimów** |
| 272 | Lo, MacKinlay | *A Non-Random Walk Down Wall Street* ✅ | |
| 273 | Malkiel | *A Random Walk Down Wall Street* ✅ | Kontrargument (Prawo XVI: słuchaj drugiej strony) |
| 274 | Wilmott | *Paul Wilmott Introduces Quantitative Finance* ✅ | |

---

## ⚖️ SĄD NAD PROPOZYCJAMI CONSILIUM — BIB-275..300 (rozstrzygnięte 2026-07-28)

**Pochodzenie:** blok dopisał cudzy agent (Kun GUI, Consilium), **podpisując się imieniem Architekta**.
2026-07-27 trafił do kwarantanny `wrzutnia/consilium/PLAN_BIBLIOTEKI_propozycje_2026-07-22.md`, bo
`docs/` jest objęte bramkami audytu — 31 niezweryfikowanych pozycji to 31 twierdzeń pod strażą.
Kwarantanna sama wskazała drogę powrotną: **pojedynczo, po weryfikacji**. To jest ta weryfikacja.

> **Plik `wrzutnia/consilium/PLAN_ROZBUDOWY_BIBLIOTEKI_wersja_Hyginusa.md` to NIE nowa praca** —
> to nasz dokument w stanie z **2026-07-26**, czyli SPRZED decyzji o kwarantannie, z tym samym
> blokiem w środku. Diff: 70 linii, treść **znak w znak** identyczna z plikiem kwarantanny.
> Nie ma tam ani jednej pozycji, której nie byłoby w kwarantannie.

### 🔴 ODRZUCONE (pomiar, nie opinia)

| BIB | Pozycja | Powód odrzucenia |
|---|---|---|
| **296** | Farmer — *Making Sense of Chaos* (2024) | **DUBLET — ta sama książka stoi już w planie jako BIB-227.** Wykryte porównaniem autor+tytuł wszystkich 205 pozycji planu z 31 propozycjami. Slot 296 zostaje **wolny** |

### 🟡 PRZYJĘTE Z KOREKTĄ

| BIB | Pozycja | Korekta |
|---|---|---|
| **277** | *Active Inference* (MIT Press 2022) | Autor **NIE „Friston"** — pierwszym autorem jest **Thomas Parr** (Parr, Pezzulo, Friston). Poprawione |
| **289** | Bennett — *Demons, Engines, and the Second Law* (1987) | To **artykuł w *Scientific American***, nie osobna książka — sprostowany gatunek, zostaje ⚠️ |

### ✅ PRZYJĘTE (kanon, istnienie pewne — wydania NIEZWERYFIKOWANE)

**🧠 Neurobiologia decyzji i uczenia (BIB-275..279)**

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 275 | Damasio | *Descartes' Error: Emotion, Reason, and the Human Brain* (1994) ✅ | Emocje jako składnik racjonalnej decyzji — pod doktrynę Senatu |
| 276 | LeDoux | *The Emotional Brain* (1996) ✅ | Mechanizmy strachu i ryzyka — pod Pretorian (bezpieczniki) |
| 277 | Parr, Pezzulo, Friston | *Active Inference: The Free Energy Principle…* (MIT Press 2022) ⚠️ | ✏️ **autor poprawiony** — Consilium pisało samo „Friston" |
| 278 | Hawkins, Blakeslee | *On Intelligence* (2004) ✅ | Memory-prediction framework — kora jako hierarchia predykcyjna |
| 279 | Eagleman | *Incognito: The Secret Lives of the Brain* (2011) ✅ | Procesy nieświadome — analogia do warstw pamięci |

**🧬 Ewolucja, emergencja i samoorganizacja (BIB-280..284)**

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 280 | Kauffman | *At Home in the Universe* (1995) ✅ | „Order for free" na granicy chaosu — teoria pod rój |
| 281 | Kauffman | *The Origins of Order* (1993) ✅ | Fitness landscapes — pod Igrzyska i ranking neuronów |
| 282 | Dawkins | *The Selfish Gene* (1976) ✅ | Memetyka u źródła — replikatory |
| 283 | Wolfram | *A New Kind of Science* (2002) ✅ | Proste reguły → złożone zachowanie |
| 284 | Holland | *Emergence: From Chaos to Order* (1998) ✅ | Uzupełnia BIB-230 (*Hidden Order*) od strony teorii |

**⚛️ Fizyka i informacja (BIB-285..289)**

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 285 | Schrödinger | *What Is Life?* (1944) ✅ | Negentropia — inspiracja pod miary entropii |
| 286 | Prigogine, Stengers | *Order Out of Chaos* (1984) ✅ | Struktury dyssypatywne (Nobel 1977) |
| 287 | Wiener | *Cybernetics* (1948) ✅ | Sprzężenie zwrotne i homeostaza u źródła |
| 288 | von Bertalanffy | *General System Theory* (1968) ✅ | Teoria systemów u źródła |
| 289 | Bennett | *Demons, Engines, and the Second Law* (1987) ⚠️ | ✏️ **korekta gatunku** — to artykuł w *Scientific American*, nie osobna książka |

**📐 Matematyka i algorytmy (BIB-290..294)**

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 290 | Knuth | *The Art of Computer Programming, vol. 1* ✅ | Kanon algorytmiki — priorytet niski dla naszej domeny |
| 291 | Press i in. | *Numerical Recipes* (3rd ed.) ✅ | Algorytmy numeryczne (C++) |
| 292 | Golub, Van Loan | *Matrix Computations* (4th ed.) ✅ | Kanon algebry liniowej |
| 293 | Rasmussen, Williams | *Gaussian Processes for Machine Learning* (2006) ✅ | ⭐ **niepewność wbudowana — pod bramkę konformalną ML-36** |
| 294 | Mohri, Rostamizadeh, Talwalkar | *Foundations of Machine Learning* (2nd ed.) ✅ | ⭐ **granice generalizacji — pod walkę z overfittingiem** |

**🏛️ Ekonomia i rynki (BIB-295..300)**

| BIB | Autor | Tytuł | Uwagi |
|---|---|---|---|
| 295 | Shiller | *Narrative Economics* (2019) ✅ | Narracje napędzają rynki — pod NEWS-01..04 |
| 296 | — | *(slot wolny)* | 🔴 odrzucone jako dublet BIB-227 |
| 297 | Akerlof, Shiller | *Animal Spirits* (2009) ✅ | Psychologia makro — pod PSY-01..05 |
| 298 | Shleifer | *Inefficient Markets* (2000) ✅ | Behawioryzm u źródła — pod neurony kontrariańskie |
| 299 | Barberis, Thaler | *A Survey of Behavioral Finance* (2003) ✅ | ⭐ Systematyczne obciążenia — wersja robocza NBER |
| 300 | Graham, Dodd | *Security Analysis* (1934) ✅ | Kanon analizy fundamentalnej |

### ⚠️ Uczciwe zastrzeżenie do całego bloku (Prawo I)

Sprawdziłem **istnienie dzieł i dublety wobec naszego planu** — to zmierzone. **NIE sprawdzałem
wydań ani lat pozycja-po-pozycji.** Osobno: **priorytet tego bloku jest NISKI**.
Mamy 69 nieodebranych pozycji z rdzenia (BIB-205..274: Tetlock, Pardo, DSR, Kleppmann, alt-dane),
a blok Consilium to w większości **filozofia systemów, nie źródła naszych neuronów**. Trzy pozycje
mają realną wartość operacyjną i tylko one zasługują na priorytet: **293 Rasmussen-Williams**
(niepewność wbudowana — pod bramkę konformalną ML-36), **294 Mohri** (granice generalizacji — pod
walkę z overfittingiem), **299 Barberis-Thaler** (obciążenia — pod PSY-01..05).

---

## 📁 POZYCJE DOŁOŻONE POZA PLANEM — BIB-301..303 (2026-07-28)

Pliki leżały w bibliotece **bez numeru i bez wpisu**, więc były niewidzialne dla katalogu i RAG.
Numery nadane **poza rezerwacją 205..274** (żeby nie zająć slotu przewidzianego na inną książkę).

| BIB | Autor | Tytuł | Werdykt |
|---|---|---|---|
| 301 | West, Thomas | *Winning Algorithmic Trading Strategies* (2025) 📤 **POZA KORPUSEM** | 🔴 **WYŁĄCZONE decyzją Cezara 2026-07-28** → `bibliotheca_ulpia/poza_korpusem/`. Treść zweryfikowana czytaniem: książka **odsyła do cudzych skryptów w TradingView Community** („search for … by the TradingView user millerrh"), a podtytuł brzmi *„…Systems that Work For Trading the Markets In 2026!"*. To gatunek, który ta lista **świadomie wyklucza** (patrz zastrzeżenie o Reactive Publishing). Ryzyko dla TIRO: uczeń nauczy się tego, co mu damy |
| 302 | Gutierrez | *Machine Learning and Data Science: An Introduction with R* 📁 | 🟡 **NISKI PRIORYTET** — wstęp do ML w R, w całości pokryty przez BIB-139 (ESL) i BIB-140 (ISL), które są mocniejsze. Bez szkody, ale i bez nowej informacji (Prawo XVI) |
| 303 | Sorensen | *Statistical Learning in Genetics* (2nd ed., Springer) 📤 **POZA KORPUSEM** | 🔴 **WYŁĄCZONE decyzją Cezara 2026-07-28** → `bibliotheca_ulpia/poza_korpusem/`. **Poza domeną** — statystyka w **genetyce**. Metody bayesowskie owszem, ale przykłady i słownictwo są biologiczne; w RAG będzie szumem przy zapytaniach rynkowych |
| 304 | Chingnun Lee | *Autoregressive Conditional Heteroscedasticity* — Ch. 26, notatki wykładowe (2009) 📁 | 🟢 **PRZYJĘTE — przesunięte tu z BIB-130.** Trafiło pod numer źródła, ale źródłem nie jest: mówi o ARCH w trzeciej osobie („introduced by Engle (1982)"), stopka *„Copy Right by Chingnun Lee ® 2009"*. **Wartość realna dla TIRO**: 25 s. wyprowadzeń ARCH→GARCH→wielowymiarowe, krok po kroku — ten sam argument, którym obroniliśmy BIB-074 (zadania Boyda). 32 444 zn. |
| 305 | Dymarski (red.) | *Hidden Markov Models, Theory and Applications* (InTech 2011, DOI 10.5772/601) ✅ 📁 | 🟢 **PRZYJĘTE — plon uboczny polowania na BIB-137.** 327 s., **864 360 zn.**, zero stron bez tekstu. Praca zbiorowa: HMM **poza rozpoznawaniem mowy** — to jest nowa informacja wobec Rabinera (BIB-137) i Jurafsky'ego (BIB-080). Przyszły dwie kopie; wybrana z repozytorium PW, bo druga miała **8 stron bez warstwy tekstowej** |
| 306 | Wood (Columbia) | *Hidden Markov Models: from the Beginning to the State of the Art* (slajdy wykładowe, 2011) 📁 | 🟡 **PRZYJĘTE WARUNKOWO.** 47 slajdów, tylko **17 456 zn.** (371 zn./slajd — slajdy to hasła, nie proza, więc słaby materiał dla RAG). Broni się **zmierzoną zerową luką**: `hierarchical Dirichlet` 0 · `HDP` 0 · `beam sampling` 0 · `explicit duration` 0 · `nonparametric Bayes` 0 fragmentów w całym RAG. **EDHMM (explicit-duration HMM) dotyka wprost trwałości reżimu** — czyli tego, co robi nasz Namiestnik. Traktować jako **listę lektur**, nie źródło |
| 307 | Svensén, Bishop | *Pattern Recognition and Machine Learning* — **Solutions to the Exercises** (wyd. web 2009) 📁 | 🟢 **PRZYJĘTE — przesunięte tu z BIB-083**, gdy przyszedł właściwy podręcznik. Trafiło pod numer podręcznika, ale jest zbiorem rozwiązań zadań (1.4 MB). **Wartość realna dla TIRO**: rozwiązania pokazują rozumowanie krok po kroku — ten sam argument co przy BIB-074 (zadania Boyda) i BIB-304 (notatki o ARCH) |

---

## 🚨 POZYCJE PROBLEMATYCZNE — pliki, które NIE wejdą do RAG bez interwencji

Zmierzone 2026-07-28 na wszystkich 97 plikach PDF (`fitz`, cały dokument, nie pierwsze strony).
**To są skany obrazowe bez warstwy tekstowej — ekstrakcja zwraca 0 znaków**, więc pipeline je
pominie (`MIN_ZNAKOW_CACHE = 200`) i **nikt się o tym nie dowie**, bo dziś nic tego nie sprawdza.

| BIB | Pozycja | Stron | Tekst | Dlaczego boli |
|---|---|---|---|---|
| ~~**130**~~ | ~~Engle — *ARCH*~~ | 22 | ✅ **51 142 zn.** | ✔️✔️ **DOMKNIĘTE 2026-07-28 przez Cezara, w dwóch krokach.** Krok 1 (04:44): plik z warstwą tekstową, ale to były **notatki wykładowe** Chingnun Lee — złapane czytaniem treści, nie nazwy. Krok 2 (04:54): **prawdziwy Engle 1982 z Econometriki**. Notatki nie poszły do kosza — dostały własny numer **BIB-304** |
| ~~**132**~~ | ~~Hamilton — *Nonstationary Time Series*~~ | 29 | ✅ **67 915 zn.** | ✔️✔️✔️ **DOMKNIĘTE 2026-07-28 za trzecim podejściem.** (1) skan bez OCR, 0 zn.; (2) plik z warstwą tekstową, ale to była **druga kopia Engle 1982** — ten sam artykuł co BIB-130, różnica wyłącznie w znaku wodnym JSTOR (IP + godzina pobrania), 99.35% tekstu identyczne; (3) prawdziwy **Hamilton 1989** |
| ~~**137**~~ | ~~Rabiner — *Tutorial on HMM*~~ | 30 | ✅ **150 305 zn.** | ✔️ **DOMKNIĘTE 2026-07-28 za pierwszym podejściem** — oryginał z *Proceedings of the IEEE*, z kompletną sekcją V o implementacji. Przy okazji tego polowania przyszły 4 dodatkowe pliki: 2 duplikaty skasowane, 2 dostały numery **305** i **306** |
| ~~**154**~~ | ~~Kyle — *Continuous Auctions…*~~ | 23 | ✅ **55 676 zn.** | ✔️ **DOMKNIĘTE 2026-07-28** — ten sam skan, ale **z warstwą OCR**; jakość na tekście merytorycznym dobra |
| ~~**175**~~ | ~~Thorp — *The Kelly Criterion…*~~ | 40 | ✅ **80 230 zn.** | ✔️✔️ **DOMKNIĘTE 2026-07-28 za drugim podejściem.** (1) wymiana 40 s. → 11 s., ale nowy plik też był czystym obrazem — **krótszy ≠ lepszy, liczy się warstwa tekstowa**; (2) wersja z OCR, 0 stron pustych. Wzory pokiereszowane, proza czysta |
| ~~**128**~~ | ~~Campbell, Lo, MacKinlay~~ | — | ✅ **1 380 803 zn.** | ✔️ **DOMKNIĘTE 2026-07-28** — Cezar podmienił **skan PDF na DJVU**. Nowa klasa rozwiązania: nie inny skan tej samej postaci, tylko **inny format**, który niesie tekst. Wymaga Calibre do ekstrakcji |
| ~~**189**~~ | ~~Fudenberg, Tirole — *Game Theory*~~ | — | ✅ **1 477 759 zn.** | ✔️ **DOMKNIĘTE 2026-07-28** — znowu podmiana **PDF → DJVU**, druga tego dnia. ⚠️ OCR gorszy niż w BIB-128 (`subgame` czyste w 88.9%) — używalne, ale nie bezbłędne |
| ~~**159**~~ | ~~Johnson — *Algorithmic Trading and DMA*~~ | — | ✅ **1 591 009 zn.** | ✔️ **DOMKNIĘTE 2026-07-28** — trzecia podmiana **PDF → DJVU** tego dnia i najlepszy plon: 26 602 unikalnych słów, OCR niemal bezbłędny. Stary plik miał **dwie wady naraz**: zepsutą strukturę (225 z 595 stron nieczytelnych) oraz — ✏️ **korekta mojego pomiaru** — raportowane „731 zn." **nie było treścią**, tylko słowem `ForexFinest` powtórzonym 61 razy (znak wodny). Cały stary plik miał **jedno unikalne słowo** |
| ~~**083**~~ | ~~Svensén, Bishop — PRML~~ | 703 | ✅ **1 592 260 zn.** | ✔️ **DOMKNIĘTE 2026-07-28** — Cezar dostarczył **właściwy podręcznik** Bishopa. To jedyna z dziewięciu pozycji, której nie dało się naprawić ani OCR-em, ani zmianą formatu: plik był technicznie bez zarzutu, tylko **był inną książką**. Rozwiązania zadań przeniesione na **BIB-307** |

**Dwie drogi (decyzja Cezara):**
1. **Cezar dostarcza inne wersje plików** (zaproponowane 2026-07-28) — najtańsze, zero ryzyka OCR.
   Potrzebne: **wersje z warstwą tekstową** dla 130, 132, 137, 154, 175, 128, 189; **niepopsuty plik**
   dla 159; **właściwy podręcznik PRML** dla 083 (PDF z Microsoft Research).
2. **OCR u nas** — precedens istnieje: **BIB-032 O'Hara** to też był skan bez warstwy tekstowej
   i przeszedł OCR 2026-07-14 (319 fragmentów w RAG). Działa, ale kosztuje czas na klasie PEDES.

---

## 🔌 Jak wpiąć do RAG (nie wymaga kodu — wszystko już jest)

1. **Nazwij plik dokładnie:** `BIB-XXX_Autor_Tytul-Z-Myslnikami.ext` (ext: epub/pdf/mobi/azw3/djvu).
   Numer z tej listy. Katalog: `bibliotheca_ulpia/`. **Separatorem jest `_`, nie spacja** — 2026-07-28
   doprowadzone do porządku 93 pliki (205/205 zgodnych). ⚠️ Zmiana nazwy binarium **musi iść razem**
   ze zmianą nazwy jego pliku w `tekst_cache/` (`<stem>__<hasz>.txt`) — hasz liczy się z TREŚCI,
   więc zostaje, ale stem osieroci cache i wymusi rekonwersję.
2. **Jedna komenda** (Calibre Portable w PATH — patrz pamięć `calibre-portable-djvu`):
   ```powershell
   $env:PATH = "C:\Calibre Portable\Calibre;$env:PATH"
   python narzedzia/przygotuj_biblioteke.py
   ```
   Spina: konwersja→`tekst_cache` (wersjonowany, więc chmura czyta bez binariów) → indeks FTS
   → katalog metadanych. **Zero tokenów LLM.**
3. **Binaria książek NIE wchodzą do gita** (`.gitignore` — rozmiar: 614 MB). Wersjonujemy
   sam wyekstrahowany tekst.
4. **Potem żniwo:** `python narzedzia/bibliotekarz.py --pelny --temat "..."` → NOTARIUS zbiera pary
   automatycznie (3/temat). Postęp widać w panelu 🎓 Szkoła TIRO na dashboardzie.

## ⚖️ Uczciwe zastrzeżenia (Prawo I)

- **Rok/wydawca żadnej pozycji nie jest zweryfikowany w tej sesji.** ✅ = pewny, że dzieło istnieje;
  NIE = pewny szczegółów bibliograficznych. Sprawdź przed zakupem.
- **⚠️ = sprawdź, zanim wydasz pieniądze.** Nie udaję, że wiem.
- **Nie ma tu ani jednej pozycji Reactive Publishing** (Van Der Post/Preston/Munrow) — świadomie.
  ⚠️ **Wyjątek do rozstrzygnięcia:** BIB-301 (West 2025) należy do tego samego gatunku i wszedł na
  dysk — rekomendacja: nie wpinać do RAG (patrz sekcja BIB-301..303).
- Lista celowo **kanon-ciężka**: uczeń TIRO nauczy się tego, co mu damy. LIMA działa też na książki.
- **Nazwa pliku nie jest dowodem treści** — 2026-07-28 przeczytałem pierwsze strony **wszystkich
  205 plików**. Złapane tym: BIB-011 (było chińskie wydanie, Cezar wymienił na angielskie ✅),
  BIB-083 (zbiór rozwiązań zamiast podręcznika), 8 skanów bez OCR, 1 plik uszkodzony.
  To **trzecia** powtórka klasy „nazwa ≠ treść" (BIB-073 → BIB-011 → BIB-083).
- **⚠️ CYTAT TO NIE AUTORSTWO — pułapka złapana 2026-07-28 przy BIB-132.** Naiwny test „czy plik
  zawiera frazę z tytułu innej pracy" **daje fałszywy alarm**, bo uczciwa praca cytuje inne prace
  w bibliografii: Hamilton 1989 zawiera frazę *„United Kingdom Inflation"* i nazwisko *ENGLE* —
  ale w spisie literatury, nie w nagłówku. **Rozstrzyga pole `Author(s)` na stronie tytułowej
  i streszczenie**, nie samo występowanie frazy. Dwa razy z rzędu (130 i 132) plik z poprawną
  warstwą tekstową okazywał się inną pracą — **obecność tekstu to warunek konieczny, nie wystarczający**.
