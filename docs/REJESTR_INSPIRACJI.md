# 🔭 REJESTR INSPIRACJI — Zewnętrzne projekty AI/ML (Faza 2+)

> **Po co ten dokument:** Jedno miejsce na WSZYSTKIE zewnętrzne projekty badawcze i repozytoria,
> które inspirują Imperium — z pełnymi nazwami, linkami i uczciwym statusem weryfikacji.
> **Format:** zgodny z `docs/WZORZEC_OPISU.md` (Zasada Pełnego Opisu).
> **Stan na:** 2026-06-02
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
| 8 | ML-29 | TradingAgents — Multi-Agent LLM | arxiv.org/abs/2412.20138 | ✅ zweryfikowany | Wzorzec Senatu/ról (referencja) |
| 9 | ML-30 | Volatility-Adaptive MoE (Adaptive Market Intelligence) | arxiv.org/abs/2508.02686 | ✅ zweryfikowany | **WDROŻONY** jako Namiestnik TABLICA |
| 10 | ML-31 | Adaptive Regime-Aware Stock Prediction (Transformer+RL) | arxiv.org/abs/2603.19136 | ✅ zweryfikowany | Wzorzec dla Namiestnik Faza 2 |
| 11 | ML-32 | Meta-Learning Optimal Mixture of Strategies | arxiv.org/abs/2505.03659 | ✅ zweryfikowany | Wzorzec MAML dla Namiestnik Faza 3 |
| 12 | ML-33 | NautilusTrader — Rust+Python event-driven | github.com/nautechsystems/nautilus_trader | ✅ zweryfikowany | Wzorzec architektury (referencja) |
| 13 | ML-34 | Multi-Timeframe Confluence (QuantPedia/TrendRider) | quantpedia.com/.../multi-timeframe-trend-strategy | ✅ zweryfikowany | **WDROŻONY** styl SCALP/SWING/INVEST w Namiestniku |
| 14 | ML-35 | Systematic Trend-Following (arXiv 2602.11708) | arxiv.org/abs/2602.11708 | ✅ zweryfikowany | Wzorzec MTF bias-filter (Faza MTF) |

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

*VITRUVIUSZ — "Pięć obietnic z przyszłości. Zapisane z linkiem i uczciwym 'jeszcze nie sprawdziłem' —
to jest pamięć, nie marzenie."*

*LA-01 dopisany przez deep-research 2026-06-02: pierwsza inspiracja, która z miejsca trafiła do KODU,
nie do planu. Freqtrade nauczył nas, jak sprawdzić, czy nasz backtest nie kłamie — i sprawdza.*
