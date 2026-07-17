---
kategoria: TABULA
typ: zywy
wlasciciel: —
stan_na: 2026-07-16
powod_istnienia: "Jedno źródło prawdy o zewnętrznych inspiracjach AI/ML (ZPO: pełna nazwa + link + status weryfikacji)"
---
# 🔭 REJESTR INSPIRACJI — Zewnętrzne projekty AI/ML (Faza 2+)

> **Po co ten dokument:** Jedno miejsce na WSZYSTKIE zewnętrzne projekty badawcze i repozytoria,
> które inspirują Imperium — z pełnymi nazwami, linkami i uczciwym statusem weryfikacji.
> **Format:** zgodny z `docs/WZORZEC_OPISU.md` (Zasada Pełnego Opisu).
> **Stan na:** 2026-07-16
>
> ⚠️ **UWAGA O LINKACH (Prawo I — zero halucynacji):**
> Linki podane przez Cezara z datami arXiv 2026 (np. 2605.xxxxx = maj 2026) są oznaczone
> ⚠️ **niezweryfikowane** — NIE otworzyłem ich i NIE potwierdzam, że istnieją. Gdy uzyskam
> dostęp do sieci, zweryfikuję każdy i zmienię status na ✅ lub ❌. Nigdy nie udaję, że sprawdziłem.

> ✅ **AKTUALIZACJA WERYFIKACJI (2026-06-02):** Projekty SHARP, AgenticAITA, CogAlpha, NEXUS, Kronos
> były zweryfikowane przez "3 zwiadowców" w maju 2026 i zapisane w `docs/ARSENAL_IMPERIUM.md` (Część I, tabela CESARZ).
> Błąd poprzedniej sesji: oznaczono je jako ⚠️ mimo że weryfikacja była w archiwum. Naprawione zgodnie z Prawem I.

---

## 📊 SZYBKA TABELA (skrót — pełne opisy niżej)

| # | Klucz | Pełna nazwa | Link | Weryfikacja | Rola w Imperium |
|---|-------|-------------|------|-------------|-----------------|
| 1 | ML-24 | SHARP — Self-Evolving Rubric Policy | arxiv.org/abs/2605.06822 | ✅ zweryfikowany | Warstwa audytu nad Cesarzem |
| 2 | ML-25 | AgenticAITA — Multi-Agent Reasoning | arxiv.org/abs/2605.12532 | ✅ zweryfikowany | Wzorzec Senatu (debata ról) |
| 3 | ML-26 | CogAlpha — Alpha Factory | arxiv.org/abs/2511.18850 | ✅ zweryfikowany | Auto-generowanie neuronów |
| 4 | ML-27 | NEXUS — Self-Evolving Market AI | github.com/The-R4V3N/Nexus | ✅ zweryfikowany | Wzorzec autonomii (Faza 4) |
| 5 | A-12 | Kronos — Foundation Model for K-line | github.com/shiyu-coder/Kronos | ✅ zweryfikowany | Neuron predykcyjny świec |
| 6 | LA-01 | Freqtrade lookahead-analysis | freqtrade.io/en/stable/lookahead-analysis | ✅ **WDROŻONY** | Detektor lookahead-bias w backteście |
| 7 | ML-28 | MRC — Market Regime Council (Shapley) | arxiv.org/abs/2605.24490 | ✅ zweryfikowany | Dynamiczne wagi agentów (plan) |
| 8 | MEM-05 | CoALA — Cognitive Architectures for Language Agents | arxiv.org/abs/2309.02427 | ✅ zweryfikowany | Taksonomia pamięci (robocza W12 + proceduralna W11 + epizodyczna + semantyczna) |
| 9 | MEM-06 | Zep/Graphiti — Temporal Knowledge Graph Memory | arxiv.org/abs/2501.13956 | ✅ zweryfikowany | Graf pamięci W8 (węzły+krawędzie+okno ważności) |
| 10 | MEM-07 | Event-Aware Sentiment Factors (LLM tweets) | arxiv.org/abs/2508.07408 | ✅ zweryfikowany | NEWS-02 taksonomia zdarzeń (kierunek per typ, rumor=kontrariański) |
| 8 | ML-29 | TradingAgents — Multi-Agent LLM | arxiv.org/abs/2412.20138 | ✅ zweryfikowany | Wzorzec Senatu/ról (referencja) |
| 9 | ML-30 | Volatility-Adaptive MoE (Adaptive Market Intelligence) | arxiv.org/abs/2508.02686 | ✅ zweryfikowany | **WDROŻONY** jako Namiestnik TABLICA |
| 10 | ML-31 | Adaptive Regime-Aware Stock Prediction (Transformer+RL) | arxiv.org/abs/2603.19136 | ✅ zweryfikowany | Wzorzec dla Namiestnik Faza 2 |
| 11 | ML-32 | Meta-Learning Optimal Mixture of Strategies | arxiv.org/abs/2505.03659 | ✅ zweryfikowany | Wzorzec MAML dla Namiestnik Faza 3 |
| 12 | ML-33 | NautilusTrader — Rust+Python event-driven | github.com/nautechsystems/nautilus_trader | ✅ zweryfikowany | Wzorzec architektury (referencja) |
| 13 | ML-34 | Multi-Timeframe Confluence (QuantPedia/TrendRider) | quantpedia.com/.../multi-timeframe-trend-strategy | ✅ zweryfikowany | **WDROŻONY** styl SCALP/SWING/INVEST w Namiestniku |
| 14 | ML-35 | Systematic Trend-Following (arXiv 2602.11708) | arxiv.org/abs/2602.11708 | ✅ zweryfikowany | Wzorzec MTF bias-filter (Faza MTF) |
| 14b | ML-36 | Adaptive Conformal Inference (ACI) — Gibbs & Candès | arxiv.org/abs/2106.00170 | ⚠️ impl. własna, pokrycie w testach | **WDROŻONY** `KalibratorKonformalny` — kalibracja pewności roju z gwarancją pokrycia pod dryfem rynku |
| 15 | MEM-01 | FinMem — Layered Memory LLM Trading Agent | arxiv.org/abs/2311.13743 | ✅ zweryfikowany | **WDROŻONY** zanik warstwowy w centrum_pamieci (decay∝ważność) |
| 16 | MEM-02 | FinAgent — Multimodal Foundation Agent (dual reflection) | arxiv.org/abs/2402.18485 | ✅ zweryfikowany | Wzorzec dual-level reflection (plan dla pamiec_refleksyjna) |
| 17 | MEM-03 | Mem0 — Scalable Long-Term Memory (extract→consolidate→retrieve) | arxiv.org/abs/2504.19413 | ✅ zweryfikowany | Wzorzec scope + konsolidacja/dedup (plan centrum_pamieci) |
| 18 | MEM-04 | A-Mem — Agentic Memory (Zettelkasten, auto-linking) | arxiv.org/abs/2502.12110 | ✅ zweryfikowany | Wzorzec auto-linkowania lekcji (plan, kandydat) |
| 19 | MEM-05 | Krajobraz konkurencji 2026 (Mem0/Zep/Letta/A-Mem + MemEvolve/SSGM) | arxiv.org/abs/2501.13956 | ✅ zweryfikowany | Scan rynku — wspólna ślepota domenowa (brak reżimu) |
| 20 | MEM-06 | 🎯 UNIKAT: Pamięć Reżimowa (Regime-Conditioned Retrieval) | (własny — Imperium) | ✅ WDROŻONY | **WDROŻONY** 4. wymiar scoringu: ×regime_match w centrum_pamieci |

> **Odkrycie deep-research (2026-06-03):** auto-selekcja **timeframe + strategia wg reżimu**
> to **OTWARTY PROBLEM** — Freqtrade (informative pairs), Jesse, NautilusTrader, OctoBot
> wymagają RĘCZNEJ konfiguracji per styl. Brak frameworka z auto-przełączaniem reżim×TF
> (stan: czerwiec 2026). Namiestnik (warstwa stylu) robi to automatycznie = przewaga.
> Standardy praktyków wbudowane: SCALP M1-15/lewar 5-10×/futures, SWING 4H-1D/2-5×,
> INVEST 1W/spot-1-2×; Kelly frakcyjny 10-25%; ATR-sizing; VOLATILE→SPOT (obrona).

> **Uwaga:** ML-24..27 to NOWE klucze rezerwowe (dodane 2026-06-02). A-12 Kronos był już w katalogu
> (`KATALOG_NEURONOW.md` linia 314) — tu dostaje pełny opis i link.
> LA-01, ML-28, ML-29 dodane 2026-06-02 po deep-research weryfikacji bazy DeepSeek (sesja "tryb agregat/strategia").

---

## 1️⃣ ML-24 | Samoewoluująca Polityka Rubryk

- **Klucz:** `ML-24`
- **Pełna nazwa (oryginalna):** SHARP — Self-Evolving Rubric Policy
- **Nazwa po polsku:** Samoewoluująca Polityka Rubryk (system, który sam poprawia własne kryteria oceny)
- **Źródło (link):** https://arxiv.org/abs/2605.06822
- **Typ źródła:** praca naukowa (arXiv)
- **Status weryfikacji:** ✅ zweryfikowany — potwierdzony w ARSENAL_IMPERIUM.md (maj 2026, 3 zwiadowców)
- **Kategoria:** E = Entropia/AI
- **Co robi (dla nowicjusza):** zamiast sztywnych reguł, system sam pisze i poprawia kryteria oceny
  swoich decyzji na podstawie tego, co rzeczywiście działało — jak uczeń poprawiający własną ściągę.
- **Jak interpretuje:** to nie zwykły neuron głosujący — to WARSTWA AUDYTU nad decyzjami Cesarza (DeepSeek).
  Podnosi/obniża zaufanie do głosów na podstawie ich historycznej trafności.
- **Dane wejściowe:** historia decyzji roju + ich wyniki (zysk/strata)
- **Skąd dane:** Pamięć Absolutna (`imperium/biblioteki/`) + wyniki Koloseum
- **Status implementacji:** 🔴 tylko plan (wizja W-009)
- **Faza wdrożenia:** Faza 2+ (wymaga LLM / API)
- **Powód:** rój ma dziś stałe wagi reżimowe; SHARP pozwoliłby im uczyć się z własnych błędów.
- **Ryzyko / ograniczenia:** wymaga LLM (koszt API), ryzyko przeuczenia, trudny do audytu — uwaga na Prawo I!
- **Powiązania:** W-009 (WIZJONER), Reflexion (W-018), ML-08 DeepAlpha

---

## 2️⃣ ML-25 | Wieloagentowe Rozumowanie

- **Klucz:** `ML-25`
- **Pełna nazwa (oryginalna):** AgenticAITA — Agentic AI Trading Architecture (Multi-Agent Reasoning)
- **Nazwa po polsku:** Wieloagentowa Architektura Tradingowa (kilku agentów AI debatuje przed decyzją)
- **Źródło (link):** https://arxiv.org/abs/2605.12532
- **Typ źródła:** praca naukowa (arXiv)
- **Status weryfikacji:** ✅ zweryfikowany — potwierdzony w ARSENAL_IMPERIUM.md (maj 2026, 3 zwiadowców)
- **Kategoria:** E = Entropia/AI (architektura, nie pojedynczy sygnał)
- **Co robi (dla nowicjusza):** zamiast jednej AI decydującej, kilku wyspecjalizowanych agentów
  (Analityk, Menedżer Ryzyka, Egzekutor, Planista) rozmawia i ściera poglądy — dopiero potem decyzja.
- **Jak interpretuje:** to wzorzec dla SENATU Imperium — nie głosuje jako neuron, lecz definiuje
  JAK Senat ma debatować (podział ról, kolejność głosu, weto Menedżera Ryzyka).
- **Dane wejściowe:** sygnały roju neuronów + kontekst reżimu
- **Skąd dane:** agregat z Generała Legatusa
- **Status implementacji:** 🔴 tylko plan — częściowo pokrywa się z istniejącym Senatem
- **Faza wdrożenia:** Faza 2 (architektura Senatu)
- **Powód:** Senat Imperium jest dziś prosty; AgenticAITA daje gotowy wzorzec debaty 4 ról.
- **Ryzyko / ograniczenia:** więcej agentów = wolniej i drożej (każdy to wywołanie LLM)
- **Powiązania:** `imperium/senat/`, IMV-AI-004 (KATALOG_STRATEGII), TradingAgents (W-019)

---

## 3️⃣ ML-26 | Fabryka Alf

- **Klucz:** `ML-26`
- **Pełna nazwa (oryginalna):** CogAlpha — Cognitive Alpha Factory
- **Nazwa po polsku:** Poznawcza Fabryka Alf (system generujący nowe sygnały tradingowe — "alfy" — automatycznie)
- **Źródło (link):** https://arxiv.org/abs/2511.18850
- **Typ źródła:** praca naukowa (arXiv)
- **Status weryfikacji:** ✅ zweryfikowany — potwierdzony w ARSENAL_IMPERIUM.md (maj 2026, 3 zwiadowców)
- **Kategoria:** E = Entropia/AI
- **Co robi (dla nowicjusza):** "alfa" to przewaga rynkowa / sygnał dający zysk. CogAlpha sam wymyśla
  nowe sygnały (jako kod), testuje je na historii i zachowuje tylko te, które działają.
- **Jak interpretuje:** to nie neuron — to FABRYKA neuronów. Generuje kandydatów → backtest w Koloseum
  → zwycięzcy wchodzą do roju (Prawo VI: każdy nowy neuron przechodzi przez Arenę).
- **Dane wejściowe:** dane historyczne OHLCV + wskaźniki z Bramy
- **Skąd dane:** Brama Kalkulatora + dane historyczne
- **Status implementacji:** 🔴 tylko plan (wizja W-024)
- **Faza wdrożenia:** Faza 4 (autonomia — system sam dodaje neurony)
- **Powód:** docelowo rój ma rosnąć sam; CogAlpha to silnik tego wzrostu.
- **Ryzyko / ograniczenia:** ryzyko przeuczenia (alfy działające tylko na historii), koszt obliczeń
- **Powiązania:** W-024, GEPA (SKAN_AZJA), IMV-AI-002 (KATALOG_STRATEGII), Koloseum (Prawo VI)

---

## 4️⃣ ML-27 | Samoewoluująca AI Rynkowa

- **Klucz:** `ML-27`
- **Pełna nazwa (oryginalna):** NEXUS — Self-Evolving Market AI
- **Nazwa po polsku:** Samoewoluująca AI Rynkowa (system, który przepisuje własny kod, by się ulepszać)
- **Źródło (link):** https://github.com/The-R4V3N/Nexus
- **Typ źródła:** repozytorium (GitHub)
- **Status weryfikacji:** ✅ zweryfikowany — potwierdzony w ARSENAL_IMPERIUM.md (maj 2026, 3 zwiadowców)
- **Kategoria:** E = Entropia/AI (autonomia)
- **Co robi (dla nowicjusza):** najbardziej zaawansowany pomysł — AI, która sama analizuje swoje wyniki
  i przepisuje własny kod, żeby działać lepiej. To kierunek docelowy całego Imperium.
- **Jak interpretuje:** to nie neuron — to WZORZEC AUTONOMII (jak DNSS). Inspiruje architekturę
  `imperium/cesarz/` + Koloseum: system, który sam decyduje co budować.
- **Dane wejściowe:** cały stan systemu + wyniki
- **Skąd dane:** całe Imperium
- **Status implementacji:** 🔴 tylko plan / inspiracja architekturalna (jak DNSS, nie neuron)
- **Faza wdrożenia:** Faza 4 (pełna autonomia)
- **Powód:** punkt docelowy wizji — samoewoluujące Imperium. Dziś za wcześnie, ale wytycza kierunek.
- **Ryzyko / ograniczenia:** AI przepisująca własny kod = ogromne ryzyko (Prawo I, Prawo XV) —
  wymaga twardych bezpieczników zanim w ogóle ruszymy.
- **Powiązania:** IMV-AI-001 (KATALOG_STRATEGII), WZORZEC_DNSS (archiwum), AEL (W-007)

---

## 5️⃣ A-12 | Model Bazowy Świec K-line

- **Klucz:** `A-12` (już istniejący w `KATALOG_NEURONOW.md` linia 314 — tu pełny opis + link)
- **Pełna nazwa (oryginalna):** Kronos — Foundation Model for K-line (candlestick) data
- **Nazwa po polsku:** Model Bazowy Świec (rodzaj "GPT" wytrenowany na świecach giełdowych zamiast tekstu)
- **Źródło (link):** https://github.com/shiyu-coder/Kronos
- **Typ źródła:** repozytorium (GitHub) + publikacja (wg katalogu: AAAI 2026)
- **Status weryfikacji:** ✅ zweryfikowany — potwierdzony w ARSENAL_IMPERIUM.md (maj 2026, 3 zwiadowców)
- **Kategoria:** E = Entropia/AI
- **Co robi (dla nowicjusza):** tak jak ChatGPT przewiduje następne słowo, Kronos przewiduje następne
  świece (ruch ceny) na podstawie wzorców z milionów wykresów.
- **Jak interpretuje:** przewiduje kierunek następnych świec → LONG jeśli prognoza wzrostu,
  SHORT jeśli spadku, NEUTRAL jeśli niepewność wysoka.
- **Dane wejściowe:** historia świec OHLCV (open/high/low/close/volume)
- **Skąd dane:** Brama Kalkulatora (dane już są — to plus!)
- **Status implementacji:** 🔴 plan (skatalogowany jako A-12, brak kodu)
- **Faza wdrożenia:** Faza 2 (wymaga załadowania wytrenowanego modelu — GPU lub inference API)
- **Waga:** W6 (pomocniczy — predykcja ML jako jeden z wielu głosów, nie wyrocznia)
- **Powód:** jedyny z piątki działający WYŁĄCZNIE na danych OHLCV, które już mamy — najłatwiejszy
  do podłączenia z całej grupy ML. Dobry pierwszy kandydat do Fazy 2.
- **Ryzyko / ograniczenia:** wymaga modelu (rozmiar, RAM/GPU — Fujitsu 8GB może nie udźwignąć lokalnie,
  rozważyć inference API), ryzyko nadmiernego zaufania predykcji (Prawo XV — to jeden głos, nie prawda).
- **Powiązania:** A-12 (KATALOG_NEURONOW), IMV-AI-008 (KATALOG_STRATEGII), dywizja Entropii

---

## 🧭 PODSUMOWANIE — co z tym robimy (dla nowicjusza)

| Projekt | Typ roli | Kiedy realnie | Trudność |
|---------|----------|---------------|----------|
| **Kronos** (A-12) | Neuron predykcyjny | Faza 2 — **pierwszy kandydat** (dane OHLCV już mamy) | 🟡 średnia |
| **SHARP** (ML-24) | Warstwa audytu Cesarza | Faza 2 | 🔴 trudna (LLM) |
| **AgenticAITA** (ML-25) | Wzorzec Senatu | Faza 2 | 🟠 architektura |
| **CogAlpha** (ML-26) | Fabryka neuronów | Faza 4 | 🔴 trudna |
| **NEXUS** (ML-27) | Wzorzec autonomii | Faza 4 (najdalej) | 🔴 bardzo trudna |

**Zasada (Prawo VII — buduj stopniowo):** nie ruszamy żadnego, dopóki rdzeń OHLCV (Faza 0/1) nie jest
stabilny i skalibrowany. Gdy nadejdzie czas — zaczynamy od **Kronosa** (najłatwiejszy, dane już są).

**Następny krok (gdy zechcesz):** zweryfikować linki w sieci → zmienić status na ✅/❌ → przy ✅
ewentualnie zacząć szkic kodu dla A-12 Kronos w Fazie 2.

---

---

## 6️⃣ Dodatkowe projekty zweryfikowane — CESARZ/SENAT (z ARSENAL_IMPERIUM.md)

> Źródło: `docs/ARSENAL_IMPERIUM.md` — Część I TOP 100, weryfikacja maj 2026.
> Status: ✅ zweryfikowane.

| Klucz | Pełna nazwa | Link | Rola w Imperium | Faza |
|-------|-------------|------|-----------------|------|
| INF-01 | TradeFM — 524M Market Foundation Model (J.P. Morgan AI Research) | https://arxiv.org/abs/2602.23784 | Neuron ML: foundation model rynkowy (analogia do Kronos, ale od JP Morgan) | Faza 2 |
| INF-02 | AlphaCrafter — Multi-Agent Alpha Generation | https://arxiv.org/abs/2605.05580 | Fabryka alf wieloagentowa — alternatywa/uzupełnienie CogAlpha | Faza 3 |
| INF-03 | AI Scientist (Sakana AI) — autonomiczny badacz naukowy | https://github.com/SakanaAI/AI-Scientist | Wzorzec auto-generowania eksperymentów — inspiracja dla Fazy 4 | Faza 4 |
| INF-04 | FinRL — Reinforcement Learning dla finansów (Columbia Univ.) | https://github.com/AI4Finance-Foundation/FinRL | Bot tradingowy RL — wzorzec dla legionów w Fazie 2 | Faza 2 |
| INF-05 | NautilusTrader — event-driven trading core (Rust/Python) | https://github.com/nautechsystems/nautilus_trader | Silnik egzekucji (Drogi) — wzorzec dla `imperium/drogi/` Faza 2 | Faza 2 |
| INF-06 | LangGraph — multi-agent orchestration (LangChain) | https://github.com/langchain-ai/langgraph | Orkiestrator agentów Senatu (zamiast ręcznego kodu) | Faza 2 |
| INF-07 | Reflexion — verbal self-reflection agent (Noah Shinn) | https://github.com/noahshinn/reflexion | Feedback loop Cesarza — uczy się z własnych błędów (W-018) | Faza 2 |
| INF-08 | Outlines — structured generation (dottxt-ai) | https://github.com/dottxt-ai/outlines | Zero-hallucination JSON output dla DeepSeek (W-017) | Faza 1 |
| INF-09 | Guardrails AI — LLM output validation | https://github.com/guardrails-ai/guardrails | Pretorianie AI — weto nad halucynacjami LLM | Faza 1 |
| INF-10 | Path Signature Transform — Rough Path Signature (Chen's Iterated Integrals, Lyons 1998) | https://arxiv.org/pdf/1307.7244 | Neuron geometrii ścieżki: Lévy Area Close↔Volume = kolejność przyczynowa (W-079, kat. D) | Faza 1 |
| INF-11 | Hawkes Branching Ratio — samowzmacniający proces punktowy (Hardiman & Bouchaud, Phys. Rev. E 2014) | https://arxiv.org/abs/1403.5227 | Neuron endogeniczności: n̂→1 = rynek krytyczny (kaskada PANIC), sensor reżimu (W-080, kat. R/F) | Faza 1 |
| INF-12 | MFDFA — Multifractal Detrended Fluctuation Analysis (Rydin Gorjão et al., SoftwareX 2021) | https://arxiv.org/pdf/2104.10470 | Neuron wielofraktalny: szerokość spektrum Δα = heterogeniczność fluktuacji, early-warning (W-081, kat. F/D) | Faza 1 |
| INF-13 | "The Secret Wealth Advantage" — Akhil Patel (2023) | ISBN 978-1804090060 (BIB-001) | 18-letni cykl nieruchomości: reguła 23/25 krachów przy Peak/Summit, prawo renty ekonomicznej → W-082..W-084 (NeuronFazyCyklu18, StrategiaFazowa) | Faza 2 |
| INF-14 | "Technical Analysis of the Financial Markets" — John J. Murphy (1999) | ISBN 978-0735200661 (BIB-002) | Analiza międzyrynkowa, left/right translation cyklu, MESA (adaptacyjny detektor długości cyklu) → W-085..W-088 | Faza 2 |
| INF-15 | "Cryptoassets" — Chris Burniske & Jack Tatar (2017) | ISBN 978-1260026672 (BIB-003) | NVT (Network Value to Transactions, crypto-PE), hash rate, Google Trends jako detektor euforii, Gartner Hype Cycle → W-089..W-093 | Faza 2 |
| INF-16 | "The Psychology of Trading" — Brett N. Steenbarger (2003) | ISBN 978-0471267614 (BIB-004) | Stacjonarność Clifforda Sherry'ego (zmiana procesu generującego), pinball trade (nieudany breakout), anty-overconfidence throttle → W-094..W-096 | Faza 2 |
| INF-17 | "What Exactly Is Crypto?" — Jonatan Blum (2022) | thecryptobook.xyz (BIB-005) | Tokenomika (issuance−burn), szok podażowy unlock/vesting, płynność DEX (AMM x*y=k), ryzyko centralizacji/governance → W-097..W-100 (wymaga danych on-chain) | Faza 3 |
| INF-18 | "High Probability Scalping Strategy Playbook" — Zachary Carson (2024) | self-published, Amazon KDP ⚠️ ASIN niezweryfikowany (BIB-006) | Konfluencja-z-dekorelacją (=Prawo XVI), filtr reżimu ADX (trend/range), MFI, sekwencja 9/13 (DeMark), ATR-stop → W-101..W-106 | Faza 2 |
| INF-19 ⭐ | "Advances in Financial Machine Learning" — Marcos López de Prado (2018) | ISBN 978-1119482086 (BIB-007) | **Autor VPIN (Z-01) i triple-barrier (W-035).** FFD/fractional differentiation (domyka W-094), meta-labeling, purged CV+embargo, CPCV, PBO, Deflated Sharpe, feature importance MDI/MDA/SFI, entropia (Kontoyiannis), SADF structural breaks → W-107..W-120 | Faza 1-2 |
| INF-20 ⭐ | "Volatility Trading" (2nd ed.) — Euan Sinclair (2013) | ISBN 978-1118347133 (BIB-008) | **Wykładowca Yang-Zhang (kat. L/V — mamy!) i Kelly (KALKULATOR_LEWARA).** Rodzina estymatorów (Parkinson/Garman-Klass/Rogers-Satchell)→sygnatura zmienności, GARCH(1,1)+vol anchor+volatility cone, Kelly μ/σ²+fractional+korekta Bayesa (w+1)/(N+2), **volatility drag −½λ(λ−1)σ²t** (krytyczny dla bota lewarowanego), K-ratio/SE(Sharpe), variance premium (DVOL−RV, wymaga Deribit) → W-121..W-139. ⚠️ crypto 24/7: YZ traci przewagę nad Rogers-Satchell (brak luki). **W-130 volatility drag WDROŻONE w kodzie 2026-06-08.** | Faza 1-2 |
| INF-21 ⭐ | "The (Mis)behavior of Markets" — Benoît Mandelbrot & Richard Hudson (2004) | ISBN 978-0465043576 (BIB-009) | **Ojciec geometrii fraktalnej — fundament osi H-01/D-01/W-081.** Efekt Józefa (long memory/Hurst R/S), efekt Noego (grube ogony/power law α/skoki), multifraktalność (widmo Δα/MMAR/kaskady), trading-time deformation, dependence-without-correlation. Celuje w nasze 3 najsłabsze osie D/H/N → W-140..W-158. Filozofia: prognozuj zmienność/reżim, nie kierunek | Faza 2 |
| INF-22 ⭐ | "Quantitative Trading" (2nd ed.) — Ernest P. Chan | ISBN — (BIB-010) | **Praktyk algo.** Half-life Ornstein-Uhlenbeck (skala czasowa rewersji), macierzowy Kelly F*=C⁻¹·M (matematyczny dowód Prawa XVI), cap lewara przez najgorszą stratę, para kointegrująca (ADF/CADF z-score), deflated Sharpe + min. długość backtestu, truncation look-ahead test → W-160..W-169 | Faza 1-2 |
| INF-23 ⭐ | "Algorithmic Trading: Winning Strategies" — Ernest Chan (2013) | ISBN 978-1118460146 (BIB-011, ŻYCZ-04) | Kalman β dla par kointegrowanych (rozszerza EXP-04), **Monte-Carlo Kelly z rozkładu Pearsona** (fat-tail awareness — Gauss-Kelly = ruina na crypto!), Hurst+Variance-Ratio (Lo-MacKinlay), leading risk indicators, CPPI → W-170..W-178. 🚨 2 flagi Prawa XV do weryfikacji w kodzie | Faza 1-2 |
| INF-24 | "Coding Capital" — Strauss & Van Der Post (2024) | (BIB-012) | ⚠️ SŁABA 3/10 (self-published, snippety błędne). Jedyne ziarno: EVT/GPD parametr kształtu ogona ξ → W-180 | Faza 2 |
| INF-25 ⭐ | "Markets in Profile" — James F. Dalton (2007) | ISBN 978-0470039090 (BIB-013, ŻYCZ-06) | **Auction Market Theory — wprost w najsłabsze filary V/S.** TPO Value Area (70%/POC), Initial Balance+Range Extension, value migration (trend wartości vs bracket), excess/tails, open types, profile shapes, **volume-vs-TPO divergence** (filar siły Prawa XVI) → W-190..W-199. TPO=czysty OHLC; volume profile=przybliżenie | Faza 2 |
| INF-26 ⭐ | "Mind Over Markets" — James F. Dalton (1990/2013) | ISBN 978-1118531730 (BIB-014, ŻYCZ-05) | Podręcznik bazowy Market Profile. 6 typów dnia, **Initiative vs Responsive** (trend vs balans wg akceptacji wartości — esencja), 4 typy otwarcia, anomalie TPO-vs-volume → W-200..W-209. ⚠️ silne nakładanie z BIB-013 → przy wdrożeniu jeden moduł. Wymaga agregacji krótkich świec do VAP | Faza 2 |
| INF-27 ⭐ | "The New Trading for a Living" — Alexander Elder (2014) | (BIB-015) | Force Index (cena×wolumen, kat. V), Impulse System gate, **Reguła 6% miesięczny budżet ryzyka (LUKA!)**, Triple Screen multi-TF, MACD-Hist divergence → W-210..W-219. Agent zweryfikował kod: W-218 equity-curve JUŻ mamy | Faza 1-2 |
| INF-28 | "Trading in the Zone" — Mark Douglas (2000) | (BIB-016) | ⚠️ 4/10 psychologia (85% martwa dla automatu). Cenne flagi: W-224 (Legatus=prawdopodobieństwo nie binarność), W-220 (edge na oknie≥20), W-222 (stop ze struktury) → W-220..W-225 | Faza 2 |
| INF-29 ⭐ | "Thinking, Fast and Slow" — Daniel Kahneman (2011) | (BIB-017, ŻYCZ-08) | Biasy TŁUMU jako neurony (anchoring/overreaction/**disposition effect**/availability-panic, W-230..233) + reguły ochrony procesu (min. próbka, shrinkage+deflated Sharpe, WYSIATI/martwy głos, anty-martingale, W-234..239). Disposition = tradeable nieefektywność | Faza 2 |
| INF-30 ⭐ | "Positional Option Trading" — Euan Sinclair (2020) | ISBN 978-1119583516 (BIB-018, ŻYCZ-07) | FINALNA matematyka sizingu (uściśla BIB-008): **skew-adjusted Kelly** (3. moment), **CI-Kelly wzór na SD(f̂)** + skalowanie pod P(over-bet), subkonto pełny-Kelly, trailing% subkonto, **doktryna stopów: cena-stop tylko dla momentum** (na mean-rev szkodzi!), counterparty cap (MEXC) → W-240..W-249 | Faza 1-2 |

| INF-31 | "Handbook for Cryptocurrencies Trading" — Virginia Harris | (BIB-019) | ❌ ODRZUCONA 2/10 — wypełniacz dla nowicjusza spotowego, anty-systematyczny/anty-leverage, przeterminowane martwe giełdy, zero matematyki, brak funding/perp/DeFi/on-chain. Wizji NIE przyznano (Prawo I). Rekomendacja: porzucić handbooki detaliczne pod oś O → kierunek ŻYCZ-09..14 | — |

| INF-32 | Rozmowa z DeepSeek "Kai" — "Kompleksowa baza wskaźników i strategii crypto" (28 wersji 1.0→2.9 + manual 1.0→5.1) | plik dostarczony 2026-06-08 (2,6 MB, 5 zwiadowców Opus) | ⚠️/❌ W WIĘKSZOŚCI SZUM (Prawo I). Inflacja 50→658 "wskaźników" = zbieranie nazw (zamknięte skrypty TradingView, projekty hackathonowe, tytuły papierów, agenci AI). **Werdykt potrójny:** (1) ✅ REALNY RDZEŃ ~30 standardowych wskaźników — w większości JUŻ MAMY; (2) ✅ realne narzędzia warte noty: CrewAI, AutoGen, LangGraph, VectorBT, Optuna, shapiq, Conformal Prediction (mapie), Polars, Glassnode/Santiment/Dune; (3) ❌ FABRYKACJE — Hermes Agent (jako orkiestrator), ShieldRegime, CogAlpha, MELT Dataset, Insider Wallets Finder, wszystkie ID arXiv `2605.xxxxx` (nieistniejące), cytaty `[N†Lx-Ly]` (syntetyczne), gwiazdki (TradingAgents 71k, OpenClaw 250k). **Kod (31 funkcji): 0 produkcyjnych**, ~12 trywialne TA z bugami (fałszywy ATR/ADX, lookahead, KeyError `equity`), ~10 throwaway/crash. `SimpleNeuralNetwork`=losowe wagi bez treningu, `PhantomAIEngine`="LLM" = zaszyte if-y. 3 symulatory HTML = animowane diagramy, NIE symulatory. Idee neuronów (Hurst/Hawkes/MFDFA/Path-Sig/VPIN/Kimchi) = RECYKLING naszego katalogu (INF-10/11/12/19). **Jedyny półrealny artefakt: szkielet ERS/Archon (Hedge/MWU weighting)** — pokrywa się z planem ML-28 (Shapley). Konceptualnie potwierdza nasz kierunek (dekorelacja=Prawo XVI, reżim-adaptacyjne wagi, multi-agent Senat=ML-25/29), nie dodaje nowego. **Wizji NIE przyznano** — wszystko wartościowe już w rejestrze | — (referencja/blacklist) |

| INF-33 | "High Win Rate Day Trading Setups" — autor anonimowy (self-published, 2023) | brak ISBN (BIB-021), plik .azw3 dostarczony 2026-06-19 (~35 kB tekstu) | ⚠️ NISKA 3/10 (Prawo I). Detaliczny katalog 9 skryptów-wskaźników TradingView community (UT Bot, HalfTrend, AlphaTrend, KDJ Whale Pump, Bjorgum MTF MA, Gaussian Loxx, TTF, Reversal Finder, Zero-Lag MACD) + 7 mechanicznych strategii scalp/mean-rev (BB+UT, MFI+HMA, RSI(5)+BB+ADX, Pivot+Williams%R…). **Zero backtestów, "70%+ win rate" bez dowodu** (nie powtarzamy jako fakt). ~80% pokrywa się z rojem (BB X-04, RSI X-01, Williams%R X-06, HMA X-10, ADX XII-01, Choppiness V-14, Supertrend XII-04≈AlphaTrend/HalfTrend). MFI już skatalogowany w INF-18 (BIB-006, W-101..W-106). **Jedyne realne ziarno: Kaufman Efficiency Ratio** (rdzeń KAMA) — zainspirował odkrycie martwego wejścia: doradca Fulmen używał `kaufman_er>0.6` jako 1 z 3 warunków TRENDU, ale Budowniczy nigdy go nie liczył (stały default 0.5 = martwy głos, Prawo XV). **→ W-353 WDROŻONE:** `KAUFMAN_ER` w Bramie + `KAUFMAN_ER_10` w Budowniczym + wpięcie w Dyrygenta. Reszta = referencja | ✅ W-353 (Kaufman ER) wdrożone |

| INF-34 | "Optimal Trading Strategies" — Robert Kissell & Morton Glantz (2003) | (BIB-022, plik .djvu dostarczony 2026-06-20, 783k znaków OCR) | ⚠️ 4/10 dla bota crypto. Kanon Transaction Cost Analysis (TCA) i optymalnej egzekucji (Almgren-Chriss). **W ~80% nieadekwatne dla małego kapitału** — market impact ma sens tylko gdy zlecenie to znaczący % wolumenu; przy małym kapitale na płynnych parach MEXC impact znikomy (sam Kissell definiuje impact = f(rozmiar/wolumen)). **Esencja:** Implementation Shortfall (IS = cena_realizacji − cena_decyzji), market impact temporary vs permanent, Trader's Dilemma (impact vs timing risk), VWAP/TWAP/POV, efficient trading frontier. **NAKŁADKA (Prawo XVI):** IS = **już W-267** (Perold, z BIB-020); market-impact gate = **już W-266/W-269** (BIB-020). **Jedyne realnie nowe ziarno: EXEC-01** — slippage zależny od płynności (`k·σ·√(rozmiar/ADV)+spread/2`) zamiast stałego `slippage_pct` (🚨 Prawo XV: stały slippage = utrata potencjału). Reszta = potwierdza kierunek BIB-020, nie dodaje | ⚠️ EXEC-01 kandydat; reszta = duplikat W-266/267/269 |

| INF-35 ⭐ | "Machine Learning for Asset Managers" — Marcos López de Prado (2020) | ISBN 978-1108792899 (BIB-023, .pdf dostarczony 2026-06-20, 152 str.) | ✅ **8/10 — SKARB, ten sam autor co BIB-007.** Krótka, gęsta, każdy rozdz. ma snippet Python. **Celuje wprost w nasze 2 udokumentowane luki** (ANALIZA_HERMES: brak wyszukiwania podobieństwa + brak dekorelacji macierzowej). Nasze neurony = "aktywa", macierz korelacji ich głosów = problem który ta książka rozwiązuje. **NOWE vs BIB-007:** (1) **Denoising** macierzy kowariancji (Marchenko-Pastur + KDE) — bije Ledoit-Wolf shrinkage; (2) **Detoning** (usuń ton rynkowy); (3) **Distance metrics** — korelacja NIE jest metryką; **Variation of Information** `VI=H[X]+H[Y]−2I[X,Y]` łapie zależności NIELINIOWE (uogólnienie Pearsona); (4) **ONC** (Optimal Number of Clusters, K-Means+silhouette); (5) **NCO/HRP** (Nested Clustered Optimization, RMSE −47-55% vs Markowitz); (6) feature importance NA KLASTRACH. **JUŻ MAMY (nie powielać):** triple-barrier/CUSUM/purged-kfold/bet-sizing (W-355..359), Deflated Sharpe+PBO+CSCV (W-282, `koloseum/walidacja.py`). 🚨 **Prawo XV:** `diagnostyka_korelacji` mierzy TYLKO Pearsona liniowo → redundancja nieliniowa między głosami dziś niewidoczna. **→ Wizje W-364..W-368** (patrz niżej) | ✅ esencja; W-364..368 zaplanowane |

| INF-36 | "Bitcoin and Cryptocurrency Trading for Beginners" — Lowe | (BIB-024, .epub dostarczony 2026-06-20, 191k znaków) | ❌ **ODRZUCONA 1/10 — niżej niż INF-31.** Poradnik życiowy "jak nie zgubić hasła" z TA doklejonym na kilka stron (~60% to bezpieczeństwo haseł, historia Satoshiego, opisy giełd, NFT). "10 strategii" = redundancja nazewnicza (Strategy 5="Buy the Dip", 8="Hedging again"), zero progów/reguł. **Błędy merytoryczne:** odwrócony opis korpusu świecy japońskiej, "strategie działają nawet gdy BTC spada do zera". Datowana (BTC "$8000", era ICO). **Zero ziarna** (jedyny kandydat OBV/dywergencje już w roju, bez formuł). **Wizji NIE przyznano** (Prawo I, jak INF-31) | ❌ odrzucona, archiwum |


| INF-37 ⭐ | "Active Portfolio Management" (+ "Advances in Active Portfolio Management") — Grinold & Kahn | (BIB-025, .pdf dostarczony 2026-06-21, 477 str.) | ✅ **9/10 — FUNDAMENT QUANT.** Prawo Fundamentalne Aktywnego Zarządzania: **IR = IC · √breadth = TC · IC · √BR**. IC = Spearman(sygnał_neuronu_t, zwrot_{t+h}) ∈ [−1,1], zdrowe IC ≤ 0.2. Breadth = liczba niezależnych zakładów (≈ klastry ONC). TC = Transfer Coefficient = corr(idealny_portfel, portfel_po_ograniczeniach). Alpha = vol · IC · score. **Dlaczego krytyczne dla Imperium:** po raz pierwszy mamy matematyczny dowód, że rój 78 neuronów jest lepszy od 1 — ale tylko gdy sygnały są NIEZALEŻNE (breadth). Prawo XVI + W-366 ONC = ten sam warunek. Nasze neurony = "strategie alpha", IC = miara ich kalibracji. **Zidentyfikowane luki:** (1) brak IC per-neuron, (2) brak IR roju, (3) TC niezmierzony. **→ W-369..373** | ✅ W-369 (IC), W-370 (breadth), W-371 (IR) wdrożone 2026-06-21 |

| INF-38 | "Machine Learning for Algorithmic Trading" (2nd ed.) — Stefan Jansen | (BIB-026, .mobi dostarczony 2026-06-21, 1254 str., 1.63M znaków) | ⚠️ **5/10 — WZORZEC INŻYNIERSKI ale nie nasz stos.** ~100% sklearn/torch/zipline — niedostępne w produkcji. **Jedyne numpy-feasible ziarno:** (1) **IC Scorer** = `rank_ic = spearman(sygnał_t, zwrot_{t+h})` — konwerguje z INF-37! Potwierdza że IC jest branżowym standardem; (2) **HRP Allocator** = hierarchical risk parity w numpy (kandydat W-374). **Architektura ML:** Jansen oddziela "feature engineering" (sygnały) od "ML model" (wagi) — odwzorowuje nasz podział neuron/Senat. Potwierdza: ML należy do WAŻENIA sygnałów (warstwa Senatu), NIE do generowania. | ⚠️ IC Scorer = nakładka na INF-37; ✅ HRP W-374 wdrożone (denoising_macierzy.hrp_wagi) |

| INF-39 | "High-Frequency Trading: A Practical Guide" (2nd ed.) — Irene Aldridge | (BIB-027, .pdf dostarczony 2026-06-21, 299 str.) | ⚠️ **4/10 — HFT infrastruktura niedostępna.** ~80% = colocation, order book L2 w μs, FPGA, dark pools — nieadekwatne dla MEXC REST/WS małego kapitału. **Realne ziarno:** (1) **Kyle's Lambda** `λ = Δp/Δv` — miara Impact/Likiditiness; lekki kandydat gdy mamy ticker+volume; (2) potwierdza Z-01/Z-03/Z-04/Z-06/RADAR. **Prawo XVI nakazuje:** zmierzyć korelację Kyle's Lambda vs Z-06 Amihud zanim wdrożymy — jeśli |ρ|>0.8 = redundancja, odpuść. | ⚠️ Kyle's Lambda = kandydat W-374b po teście Prawa XVI |

| INF-40 | "Inside the Black Box: A Simple Guide to Systematic Investing" (2nd ed.) — Rishi Narang | (BIB-028, .epub dostarczony 2026-06-21, ~350 str.) | ✅ **7/10 — AUDYT ARCHITEKTONICZNY.** 8 kategorii alpha (trend/mean-rev/technical-sentiment/value/growth/supply-demand/quality/tactical) = mapa audytu roju: mamy trend ✅, mean-rev ✅, brak quality ⚠️, brak supply-demand ⚠️ (OI/futures basis). **ML teza:** ML należy do WAŻENIA sygnałów (potwierdza INF-38). **3 krytyczne insighty:** (1) **Point-in-time data** — dane historyczne muszą odzwierciedlać co WTEDY było dostępne; (2) **Parameter plateau** — nie wybieraj lokalnego max Sharpe, wybieraj płaskowyż odporny na perturbacje (Punkt B); (3) **Transaction cost model** — nasz stały `slippage_pct` = zbyt prosty (konwerguje z INF-34 EXEC-01). **Architektura:** Alpha→Risk→Execution→Data = odzwierciedla Imperium. | ✅ audyt kategorii alpha; W-375 (point-in-time) kandydat |

> **📗 BIB-020 (Harris "Trading and Exchanges") — UWAGA SPÓJNOŚCI:** fizyczny plik epub dodano 2026-06-20,
> ale **książka była już w pełni przeżyta** w `docs/WIZJONER.md` (ŻYCZ-10, 9/10, pula wizji W-250..W-279,
> dekorelacja zmierzona `narzedzia/pomiar_dekorelacji_bib020.py`). **5 wizji JUŻ W KODZIE:** X-27 (W-273),
> Z-03 (W-278), Z-04 (W-279), VARIANCE_RATIO (W-263), OU_HALFLIFE (W-274). Nie ma osobnego wpisu INF —
> jego dom to WIZJONER (większa pula niż mieści tabela INF). To wyjaśnia lukę numeracji BIB-020 w tabeli.

---

## 🔟 WIZJE BIB-023 (López de Prado ML for Asset Managers) — W-364..W-368

> Zamykają 2 luki pamięci z `ANALIZA_HERMES_I_PAMIEC.md`. Kolejność kumulatywna (Prawo VII).

| Wizja | Opis | Cel / moduł | Status |
|---|---|---|---|
| **W-364** ⭐ | **Variation of Information** — nieliniowa miara podobieństwa głosów neuronów (`VI=H[X]+H[Y]−2I[X,Y]`). Łapie redundancję nieliniową (dwa głosy ρ≈0 ale wysokie I[X,Y]). | `diagnostyka_korelacji.py` | ✅ **JUŻ BYŁO** — `variation_of_information()`, `informacja_wzajemna()`, `nmi()`, `raport_informacji_wzajemnej()` + testy `test_informacja_wzajemna.py` (odkrycie spójności 2026-06-20: agent mylił MANIFEST z kodem) |
| **W-365** | **Denoising macierzy korelacji** (Marchenko-Pastur + KDE) — odszum macierz ZANIM policzymy dekorelację. Wartości własne ≤ λ⁺ = szum → constant residual eigenvalue. | `denoising_macierzy.py` | ✅ **WDROŻONE + WPIĘTE** 2026-06-20 — `denoise_macierz()`, `mp_pdf()`, `znajdz_max_eval()`; **WPIĘTE w żywy przepływ:** `KolektorKorelacjiNeuronow.korelacje_denoised()` → Dyrygent zasila SynapsyRezimowe odszumioną macierzą (flaga `denoising_korelacji`, bezpieczny fallback) |
| **W-366** | **ONC clustering** — auto-grupowanie skorelowanych neuronów (K-Means na metryce `√(½(1−ρ))` + silhouette, auto-k). | `denoising_macierzy.py` | ✅ **WDROŻONE** 2026-06-20 — `klastruj_onc()` (K-Means+silhouette w czystym numpy) |
| **W-367** | **NCO wag neuronów** — podnosi alokację do poziomu macierzowego: klastruj → alokuj wewnątrz/między klastrami (odporne na klątwę Markowitza). | `denoising_macierzy.py` | ✅ **WDROŻONE** 2026-06-20 — `nco_wagi()`, `_wagi_min_wariancji()` |
| **W-368** | **Detoning** — usuń „ton rynkowy" (dominujący czynnik wspólny) przed klastrowaniem → wzmacnia zdekorelowane głosy. | `denoising_macierzy.py` | ✅ **WDROŻONE** 2026-06-20 — `detone_macierz()` |

---


---

## 📚 BIB-029..032 (Blockchain/TimeSeries/Microstructure) — INF-41..44

| Nr | Książka | Ocena | Werdykt | Wdrożone |
|---|---|---|---|---|
| **INF-41** ❌ | Bashir — "Mastering Blockchain" (4th ed., BIB-029) | **2/10** | Podręcznik DApp/Solidity/DeFi — zero on-chain analytics (brak MVRV/SOPR/NVT/NUPL/Glassnode). Jedyne ziarno: Health Factor `HF=Σ(col·thr)/debt` i AMM `x·y=k` — architektura DEX, nie sygnały. Wizji NIE przyznano. | — |
| **INF-42** | Ammous — "The Bitcoin Standard" (BIB-030) | **3/10** | Ekonomia austriacka, nie trading. 95% filozofia monetarna. Jedyne numpy-feasible: 3 deterministyczne neurony z block_height — S2F, DAYS_TO_HALVING, SUPPLY_INFLATION. Stock-to-Flow opisany konceptualnie (bez formuły predykcyjnej — model Plan B 2019 to osobny artykuł). | ✅ OC-06/07/08 wdrożone (W-377..379) |
| **INF-43** ⭐ | Tsay — "Analysis of Financial Time Series" (3rd ed., BIB-031) | **9/10** | SKARB. Kompletny podręcznik szeregów finansowych. GARCH(1,1) rekurencja Bollersleva = zwykła pętla numpy (bez scipy). GJR-GARCH, EGARCH, VAR/VECM, Markov-Switching. Zamknął martwą wizję W-126. | ✅ EXP-13 GJR-GARCH(1,1) wdrożony (W-376) |
| **INF-44** | O'Hara — "Market Microstructure Theory" (BIB-032) | **8/10** | Fundament teorii VPIN/PIN/Kyle's Lambda. Kyle λ = OLS nachylenie Δp∼netflow. PIN metodą momentów (numpy.linalg.solve — bez scipy). Glosten-Harris decomposition: spread = transakcyjny + adverse selection. Poprawa VPIN: ważenie wolumenem. | ✅ EXP-14 Kyle's Lambda wdrożony (W-380) |


---

## 🔟 WIZJE BIB-031/032 (Tsay + O'Hara) — W-381/382 + HRP W-374

| Wizja | Opis | Moduł | Status |
|---|---|---|---|
| **W-374** | **HRP — Hierarchical Risk Parity** (López de Prado 2016, Jansen BIB-026). Alokacja z dendrogramu: odległość √(½(1−ρ)) → single-linkage → quasi-diagonalizacja → recursive bisection. NIE odwraca macierzy → odporna na klątwę Markowitza. Dopełnia NCO (W-367). | `denoising_macierzy.py` → `hrp_wagi()` | ✅ **WDROŻONE** 2026-06-21 — single-linkage + seriation + bisection w pure numpy. 7 testów (sumują do 1, dodatnie, preferuje niską wariancję). |
| **W-381** | **PIN — Probability of Informed Trading** (Easley-O'Hara, BIB-032). Procent transakcji od inwestorów Z INFORMACJĄ. Metoda momentów: ε=min(buy,sell) baza szumu, informed=\|buy−sell\| asymetria, PIN=informed/(informed+2ε). Komplementarny do VPIN (Z-01: imbalance vs PIN: proporcja). | `mikrostruktura.py` → `pin_metoda_momentow()` | ✅ **WDROŻONE** 2026-06-21 — bez scipy (metoda momentów). 5 testów granic. |
| **W-382** | **Engle-Granger kointegracja par** (Tsay BIB-031 rozdz. 8). Dwustopniowo: OLS log(a)∼log(b) → spread; ADF na spreadzie. Skointegrowane → z-score spreadu = sygnał stat-arb (z<−2 LONG a/SHORT b). Próg ADF −3.4 (anty-spurious). | `mikrostruktura.py` → `kointegracja_engle_granger()` | ✅ **WDROŻONE** 2026-06-21 — Engle-Granger + ADF w pure numpy. 7 testów (skointegrowane vs spurious random walks). |

| **W-377..379 obudzenie** | OC-06/07/08 **OŻYWIONE** — `BTC_BLOCK_HEIGHT` szacowany z timestampu baru (interpolacja po kotwicach halvingów, normalizacja ms→s, bez sieci). 3 martwe głosy → aktywne (Prawo XV). | `budowniczy_wskaznikow._dodaj_btc_onchain()` + `onchain.szacuj_block_height()` | ✅ **WDROŻONE** 2026-06-21 — działa w backteście i live. 14 testów. |
| **W-383** | **EXP-15 PIN scout** — wpięcie W-381 PIN do roju jako zwiadowca. Buy/sell z tick-rule OHLCV → PIN metodą momentów. Wysoki PIN → tłumi rój (pewnosc_przeciwnika). Komplementarny do VPIN Z-01 + Kyle EXP-14. | `zwiadowcy/exp_pin.py` | ✅ **WDROŻONE** 2026-06-21 — 5 testów granic. |

> **Uwaga (Prawo XVI):** W-381 PIN i W-382 kointegracja to BIBLIOTEKI (funkcje), nie neurony —
> czekają na wpięcie jako zwiadowcy/sygnały gdy pętla portfelowa dostarczy dane par + aggTrades.
> HRP (W-374) dostępne dla alokacji wag w Senacie obok NCO (W-367).

---

## 🔟 WIZJE BIB-025 (Grinold & Kahn — Fundamental Law) — W-369..373

> Zamykają lukę kalibracji sygnałów: mierzymy jakość każdego neuronu indywidualnie (IC) oraz roju (IR).

| Wizja | Opis | Cel / moduł | Status |
|---|---|---|---|
| **W-369** ⭐ | **IC per-neuron** — Information Coefficient = `Spearman(sygnał_t, zwrot_{t+h})` dla h∈{1,5,21}. Miara kalibracji sygnału: IC=0 = losowy, IC=0.1 = dobry, IC>0.2 = podejrzany (overfitting). | `metryki_ic.py` → `KolektorIC` | ✅ **WDROŻONE** 2026-06-21 — `KolektorIC`, `_spearman()`, testy granic (NaN, stała seria, pusta baza). 17 testów zielone. |
| **W-370** | **Breadth** — liczba niezależnych zakładów = `len(klastruj_onc(corr_denoised).klastry)`. Wykorzystuje W-366 ONC bezpośrednio. | `metryki_ic.py` → `prawo_fundamentalne()` | ✅ **WDROŻONE** 2026-06-21 — `prawo_fundamentalne()` wylicza breadth z ONC lub fallback do `len(neurony)`. |
| **W-371** | **IR roju** = `IC_śr · √breadth`. Rozkłada słaby IR na dwa pytania: "mamy IC?" vs "mamy breadth?". Diagnostyka: IC_NISKI / BREADTH_NISKI / IR_DOBRY / IR_SREDNI / IR_SLABY. | `metryki_ic.py` → `prawo_fundamentalne()` | ✅ **WDROŻONE** 2026-06-21 — pełny raport z diagnozą. Sortowanie neuronów wg |IC| malejąco. |
| **W-372** | **Alpha kalibrowany** = `vol · IC · score` — przelicza surowe sygnały na spodziewane zwroty w %. Wymaga stabilnego IC (≥60 obserwacji). | `metryki_ic.py` | 🔵 PLANOWANE — Faza 2 (po zebraniu danych produkcyjnych) |
| **W-373** | **Transfer Coefficient** = `corr(idealny_portfel_alpha, portfel_po_ograniczeniach)` — mierzy ile alpha tracimy przez ograniczenia (min_notional, size_cap). | `metryki_ic.py` | 🔵 PLANOWANE — Faza 2 (backtest diagnostic) |


## 📖 NASTĘPNE KSIĄŻKI — lista życzeń (ŻYCZ, do wrzucenia do `bibliotheca_ulpia/`)

> Rekomendacje pod nasze udokumentowane luki — NIE powielać tego co mamy (Prawo VIII/XVI).
> Wrzuć plik epub/pdf/azw3, nazwij `BIB-0XX_Autor_Tytul.ext`, napisz „masz nową książkę".

| ŻYCZ | Książka | Po co (luka którą zamyka) | Priorytet |
|---|---|---|---|
| **ŻYCZ-15** ✅ | Grinold & Kahn — "Active Portfolio Management" | **DOSTARCZONA** jako BIB-025. Wizje W-369..371 wdrożone (IC/breadth/IR). → INF-37 ⭐ | ✅ BIB-025 |
| **ŻYCZ-16** ✅ | Rishi Narang — "Inside the Black Box" | **DOSTARCZONA** jako BIB-028. Audyt architektoniczny ukończony. → INF-40 | ✅ BIB-028 |
| **ŻYCZ-17** ✅ | Irene Aldridge — "High-Frequency Trading" | **DOSTARCZONA** jako BIB-027. Kyle's Lambda = kandydat W-374b (czeka test Prawa XVI). → INF-39 | ✅ BIB-027 |
| **ŻYCZ-18** ✅ | Stefan Jansen — "Machine Learning for Algorithmic Trading" | **DOSTARCZONA** jako BIB-026. IC Scorer konwerguje z INF-37; HRP = kandydat W-374. → INF-38 | ✅ BIB-026 |

> **Po co BIB-020 Harris jest już „domknięty":** patrz nota spójności wyżej (WIZJONER, W-250..279).

---

> **Pełna lista (~220 narzędzi):** `docs/ARSENAL_IMPERIUM.md` — schemat architektoniczny + tabele weryfikacyjne.

---

## 7️⃣ LA-01 | Detektor Lookahead-Bias (Freqtrade) — ✅ WDROŻONY

- **Klucz:** `LA-01`
- **Pełna nazwa (oryginalna):** Freqtrade `lookahead-analysis` (Look-Ahead Bias Analysis)
- **Nazwa po polsku:** Detektor zaglądania w przyszłość (analiza błędu wyprzedzania)
- **Źródło (link):** https://www.freqtrade.io/en/stable/lookahead-analysis/
- **Typ źródła:** dokumentacja open-source (framework Freqtrade, Python)
- **Status weryfikacji:** ✅ zweryfikowany 2026-06-02 (deep-research) — narzędzie realne, opisane, używane produkcyjnie
- **Co robi (dla nowicjusza):** lookahead-bias to gdy backtest „oszukuje" — podejmuje decyzję na
  barze przeszłym, ale korzysta z danych z przyszłości (których w realu jeszcze by nie było). Wtedy
  wyniki backtestu są fałszywie dobre. Freqtrade wykrywa to, uruchamiając backtest na pełnych danych
  i na danych obciętych, a potem porównując, czy sygnały na wspólnym zakresie są identyczne.
- **Jak działa w Imperium:** `imperium/koloseum/lookahead.py` — liczy ślad głosów roju na pełnym i
  obciętym zbiorze barów; każda rozbieżność = czerwony alarm (Prawo I: rój nie może znać przyszłości).
- **Status implementacji:** ✅ **W KODZIE** — `wykryj_lookahead()` + 3 testy (`tests/test_lookahead.py`)
- **Faza wdrożenia:** Faza 0 (backtest) — gotowe
- **Powód:** OpenAlice (badany jako alternatywa) NIE ma rygoru backtestu; Freqtrade tak. Przenieśliśmy
  jego metodę weryfikacji do naszego silnika zamiast zmieniać framework.
- **Dowód:** `python -m imperium.koloseum.lookahead dane/dzienne/Binance_BTCUSDT_d.csv 1D 600` → ✅ CZYSTO
- **Powiązania:** `backtest.py` (niezmiennik okna), Prawo I, Prawo XXI

---

## 8️⃣ ML-28 | Market Regime Council — dynamiczne wagi Shapley (plan)

- **Klucz:** `ML-28`
- **Pełna nazwa (oryginalna):** MRC — Market Regime Council for Dynamic Credit Assignment in Multi-Agent LLM Decision Systems
- **Nazwa po polsku:** Rada Reżimu Rynkowego (dynamiczne przypisanie zasług metodą Shapleya)
- **Źródło (link):** https://arxiv.org/abs/2605.24490
- **Typ źródła:** praca naukowa (arXiv, preprint maj 2026)
- **Status weryfikacji:** ✅ zweryfikowany 2026-06-02 (deep-research) — papier istnieje, wyniki: Sharpe 1.51,
  CR 440.1% na 1037 dniach / 13 aktywach krypto. UWAGA: preprint nierecenzowany, brak replikacji stron trzecich.
- **Co robi (dla nowicjusza):** zamiast dawać każdemu neuronowi równy głos (nasz „agregat"), oblicza
  ile NAPRAWDĘ wnosi każdy agent do wspólnego sukcesu (wartości Shapleya z teorii gier) i tak ważą głosy.
  Mnożniki zależne od reżimu zmieniają autorytet agenta zależnie od fazy rynku.
- **Jak pasuje do Imperium:** to naukowy następca naszego prostego głosowania w Legatusie — wagi nie stałe
  (WAGI_REZIMU), tylko uczone z historii trafności. Rozwiązuje problem `pewnosc_agregatu ≈ 1.0` (zawsze max lewar).
- **Status implementacji:** 🔴 tylko plan (kandydat na Fazę 2 — następca WAGI_REZIMU)
- **Faza wdrożenia:** Faza 2
- **Powód:** jedyna naukowo udokumentowana metoda dynamicznego ważenia agentów znaleziona w badaniu.
- **Ryzyko / ograniczenia:** dokładny Shapley = koszt wykładniczy (N agentów → 2^N koalicji); preprint niereplikowany.
- **Powiązania:** Legatus `_agreguj`, WAGI_REZIMU, Prawo XVI (redundancja mierzona)

---

## 9️⃣ ML-29 | TradingAgents — wieloagentowy framework LLM (referencja)

- **Klucz:** `ML-29`
- **Pełna nazwa (oryginalna):** TradingAgents — Multi-Agents LLM Financial Trading Framework (Tauric Research)
- **Nazwa po polsku:** Agenci Handlowi — wieloagentowy framework LLM do handlu
- **Źródło (link):** https://arxiv.org/abs/2412.20138 | https://github.com/TauricResearch/TradingAgents
- **Typ źródła:** praca naukowa (arXiv) + repozytorium open-source (~80 000 ⭐, autor: Yijia Xiao i in.)
- **Status weryfikacji:** ✅ zweryfikowany 2026-06-02 (deep-research) — DeepSeek podał 71 400 ⭐ (zaniżone,
  realnie ~80k). 7 ról: Fundamentalny, Sentymentu, Newsów, Techniczny, Badacz, Trader, Risk Manager. Debata byk vs niedźwiedź.
- **Co robi (dla nowicjusza):** symuluje cały fundusz hedgingowy — agenci LLM o różnych rolach debatują
  (byk kontra niedźwiedź) zanim podejmą decyzję. Testowany głównie na AKCJACH, nie krypto.
- **Jak pasuje do Imperium:** wzorzec referencyjny dla Senatu/Doradców Cezara (debata ról przed decyzją).
- **Status implementacji:** 🔴 referencja architektoniczna (nie kopiujemy — mamy własny Senat)
- **Faza wdrożenia:** Faza 2+ (inspiracja)
- **Powód:** najpopularniejszy zweryfikowany framework multi-agent; potwierdza nasz kierunek (role + debata).
- **Ryzyko / ograniczenia:** LLM-heavy (koszt API); wyniki krypto niepotwierdzone w papierze.
- **Powiązania:** Senat, DORADCY_CARA.md, ML-25 AgenticAITA

> **🚩 Odrzucone w badaniu 2026-06-02 (Prawo I — nie wszystko z DeepSeeka jest prawdą):**
> - **StratEvo** (rzekomo Sharpe 6.06) — realnie 17 ⭐, liczby pomylone akcje/krypto, brak replikacji. ❌ nie wdrażamy.
> - **VORTEX** (LabLab Milan) — niezweryfikowalny, brak projektu o tej nazwie w źródłach. ❌
> - **OpenAlice** (rzekomo do backtestu) — to agent LLM w Node.js, NIE silnik backtestu. ❌ niekompatybilny.
> - **AetherEdge** — realny wskaźnik TradingView, ale opis „RL agenci" przesadzony. ⚠️ tylko jako idea konsensusu.

---

## 🧠 KLASTER PAMIĘCI (MEM-01..04) — scan rynku „mem0 i pamięć absolutna" (2026-06-22)

Deep-research na żądanie Cezara: „FinMem/FinAgent to nasza dziedzina — czy to mamy?".
Wszystkie ID arXiv zweryfikowane na żywo (WebSearch, czerwiec 2026). Prawo I — zero fabrykacji.

### MEM-01 | FinMem — Layered Memory LLM Trading Agent
- **Pełna nazwa:** FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design
- **Źródło (link):** https://arxiv.org/abs/2311.13743 | github.com/pipiku915/FinMem-LLM-StockTrading
- **Status weryfikacji:** ✅ zweryfikowany (AAAI-SS 2024; autor Yangyang Yu i in.)
- **Co robi (dla nowicjusza):** agent LLM do tradingu z pamięcią 3-warstwową (płytka/średnia/głęboka),
  KAŻDA z innym tempem zaniku. Ważne wydarzenia rynkowe „spadają głębiej" i żyją dłużej; rutyna
  zanika szybko. Plus moduł charakteru (profiling) — odpowiednik naszego PROFIL_CEZARA.md.
- **Co z tego mamy:** ✅ **WDROŻONE** — `centrum_pamieci._decay_dla_waznosci()` realizuje zanik
  warstwowy jako funkcję CIĄGŁĄ ważności (nasz unikat vs 3 dyskretne kubełki FinMem). Lekcja
  krytyczna zanika ~10× wolniej niż rutynowa. Wcześniej: jeden zanik 0.995 dla wszystkich =
  UTRATA POTENCJAŁU (Prawo XV). Profiling już mieliśmy (PROFIL_CEZARA.md, W-360 v2).
- **Status implementacji:** ✅ aktywny (centrum_pamieci.py, testy granic zaniku)
- **Powiązania:** centrum_pamieci.py (W-360 v3), pamiec_refleksyjna.py (W-295), MEM-02

### MEM-02 | FinAgent — Multimodal Foundation Agent (dual-level reflection)
- **Pełna nazwa:** A Multimodal Foundation Agent for Financial Trading: Tool-Augmented, Diversified, and Generalist (FinAgent)
- **Źródło (link):** https://arxiv.org/abs/2402.18485 (KDD 2024; Wentao Zhang, Bo An i in., NTU)
- **Status weryfikacji:** ✅ zweryfikowany
- **Co robi (dla nowicjusza):** agent multimodalny (liczby+tekst+wykresy) z DWUPOZIOMOWĄ refleksją:
  niski poziom (refleksja nad ceną/rynkiem) + wysoki poziom (refleksja nad WYNIKIEM własnych
  transakcji). Do tego „diversified memory retrieval" — osobne pamięci pobierane niezależnie.
- **Co z tego mamy:** ⚠️ CZĘŚCIOWO — `pamiec_refleksyjna.py` robi refleksję jednopoziomową
  (narracja po serii transakcji). Brak rozdziału low/high-level. **Kandydat do wdrożenia:**
  rozdzielić refleksję „co zrobił rynek" od „co zrobiłem ja" (plan, nie kod — Prawo XIX).
- **Status implementacji:** 🔴 wzorzec (plan rozbudowy pamiec_refleksyjna)
- **Powiązania:** pamiec_refleksyjna.py, MEM-01

### MEM-03 | Mem0 — Scalable Long-Term Memory
- **Pełna nazwa:** Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory
- **Źródło (link):** https://arxiv.org/abs/2504.19413 (Chhikara, Khant i in., 2025; mem0.ai)
- **Status weryfikacji:** ✅ zweryfikowany (–90% kosztu tokenów, –91% p95 latencji vs pełny kontekst)
- **Co robi (dla nowicjusza):** pipeline pamięci EXTRACT→CONSOLIDATE→RETRIEVE: wyłuskuje istotne
  fakty z rozmowy, KONSOLIDUJE (deduplikuje, rozwiązuje konflikty „stary fakt vs nowy"),
  potem pobiera. Wariant grafowy łapie relacje. Multi-level scope (sesja/user/agent).
- **Co z tego mamy:** ⚠️ CZĘŚCIOWO — mamy scope (`lekcje_scope`, Mem0-style) + CRUD
  (`usun/aktualizuj_lekcje`). Brak AUTOMATYCZNEJ konsolidacji/dedup/rozwiązywania konfliktów —
  dziś robimy to ręcznie. **Kandydat:** auto-dedup lekcji o tym samym temacie (plan).
- **Status implementacji:** ⚠️ częściowo wdrożony (scope+CRUD ✅; auto-konsolidacja 🔴 plan)
- **Powiązania:** centrum_pamieci.py (scope), pamiec_sesji.py (CRUD)

### MEM-04 | A-Mem — Agentic Memory (Zettelkasten)
- **Pełna nazwa:** A-MEM: Agentic Memory for LLM Agents
- **Źródło (link):** https://arxiv.org/abs/2502.12110 (Rutgers, Ant Group, Salesforce; 2025)
- **Status weryfikacji:** ✅ zweryfikowany
- **Co robi (dla nowicjusza):** pamięć w stylu Zettelkasten — każda notatka jest „atomowa", ma
  auto-generowane słowa kluczowe/tagi/LINKI do innych notatek. Nowa notatka może AKTUALIZOWAĆ
  kontekst starych (ewolucja sieci wiedzy). Brak sztywnych, predefiniowanych operacji pamięci.
- **Co z tego mamy:** ❌ NIE — nasze lekcje są płaskie (lista markdown), bez auto-linkowania.
  **Kandydat odległy:** linkowanie powiązanych lekcji (np. „bug GARCH" ↔ „speedup GARCH").
- **Status implementacji:** 🔴 wzorzec (kandydat, niski priorytet — wymaga embeddingów lub LLM)
- **Powiązania:** bibliotheca_ulpia/ (RAG ma już embeddingi — możliwa baza pod auto-linki)

### MEM-05 | Krajobraz konkurencji 2026 (scan na żądanie Cezara, 2026-06-26)

Deep-research „czy da się lepszą pamięć od konkurencji". Stan rynku (2026):
- **Mem0** (https://arxiv.org/abs/2504.19413, ECAI 2025) — ekstrakcja wektorowa + multi-signal
  retrieval; benchmark LoCoMo. Token-efficient single-pass hierarchiczna ekstrakcja (kwi 2026).
- **Zep / Graphiti** (https://arxiv.org/abs/2501.13956) — **temporalny graf wiedzy**: rozwiązywanie
  konfliktów po metadanych czasowych, inkrementalne aktualizacje, stan historyczny bi-temporalny.
- **Letta / MemGPT** — pamięć OS-owa: core (RAM) / recall / archival, samo-edycja kontekstu.
- **A-Mem** (https://arxiv.org/abs/2502.12110) — Zettelkasten auto-linking przez embeddingi.
- **Nowe 2026:** MemEvolve/EvolveMem (meta-ewolucja pamięci, https://arxiv.org/pdf/2512.18746),
  SSGM — Stability & Safety Governed Memory (governance ewoluującej pamięci, arXiv 2603.11768).

> **WSPÓLNA ŚLEPOTA KONKURENCJI:** wszystkie są **domenowo-agnostyczne**. Retrieval = podobieństwo
> semantyczne + recency + (Zep) ważność czasowa. ŻADEN nie wie, że ważność wspomnienia
> TRADINGOWEGO zależy od **reżimu rynku**. Lekcja „kupuj dołki" z hossy jest aktywnie szkodliwa
> w bessie — a cosine/temporal retrieval i tak ją wyciągnie.

### MEM-06 | 🎯 UNIKAT IMPERIUM — Pamięć Reżimowa (Regime-Conditioned Retrieval) ✅ WDROŻONY

- **Co to (dla nowicjusza):** dokładamy **4. wymiar** do scoringu Generative Agents.
  Było: `recency × importance × relevance`. Jest: `× regime_match`. Wspomnienie z tego samego
  reżimu co BIEŻĄCY (z `klasyfikuj_rezim`/Gubernatora) → pełna waga; z innego → tłumione
  (`_DAMPEN_REZIM=0.4`); bez tagu reżimu → neutralne 1.0 (nie karzemy lekcji ogólnych).
- **Dlaczego lepsze od konkurencji:** to jedyny znany nam system, który **warunkuje retrieval
  pamięci na reżimie rynku**. Naprawia „regime-stale bug" (otwarty problem rynku) u źródła:
  pamięć nie wyciąga bańkowych lekcji w krachu. Logi W1 mają JAWNE pole `rezim` → dopasowanie
  precyzyjne (nie zgadywane z tekstu); lekcje W3 — token reżimu wykrywany z treści.
- **Status implementacji:** ✅ KOD + TESTY — `centrum_pamieci.py` (`score_lekcji`, `szukaj_wszedzie`,
  `top_lekcji`, `_regime_match`, `_wykryj_rezim`), CLI `szukaj --rezim`, +9 testów granic.
  Wstecznie kompatybilne (`rezim_biezacy=''` → funkcja wyłączona).
- **Powiązania:** legatus.klasyfikuj_rezim (źródło reżimu), pamiec_absolutna (pole rezim),
  MEM-01 FinMem (zanik), MEM-03 Mem0 (scope). Backlog: metadana reżimu per-lekcja w PAMIEC.md.

> **🎯 NASZ UNIKAT (pełny):** (1) **Pamięć Reżimowa** — retrieval warunkowany reżimem (MEM-06,
> nikt na rynku tego nie ma); (2) pamięć tradingowa + **sesja deweloperska w git** + **etyka
> falsyfikacji (Prawo I)** w pipeline; (3) **zanik warstwowy ciągły** (nie 3 kubełki FinMem);
> (4) cross-layer search łączy lekcje (W3) + kronikę (W3b) + logi PnL/MAE/MFE (W1) jednym
> zapytaniem. FinMem/FinAgent pamiętają RYNEK; my pamiętamy rynek + dialog + lekcje + profil,
> wersjonowane gitem (przeżywa kompakcję i wygaśnięcie kontenera) — i warunkowane reżimem.

---

*VITRUVIUSZ — "Pięć obietnic z przyszłości. Zapisane z linkiem i uczciwym 'jeszcze nie sprawdziłem' —
to jest pamięć, nie marzenie."*

*LA-01 dopisany przez deep-research 2026-06-02: pierwsza inspiracja, która z miejsca trafiła do KODU,
nie do planu. Freqtrade nauczył nas, jak sprawdzić, czy nasz backtest nie kłamie — i sprawdza.*
