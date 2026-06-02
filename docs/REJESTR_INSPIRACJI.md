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

---

## 📊 SZYBKA TABELA (skrót — pełne opisy niżej)

| # | Klucz | Pełna nazwa | Link | Weryfikacja | Rola w Imperium |
|---|-------|-------------|------|-------------|-----------------|
| 1 | ML-24 | SHARP — Self-Evolving Rubric Policy | arxiv.org/abs/2605.06822 | ⚠️ niezweryf. | Warstwa audytu nad Cesarzem |
| 2 | ML-25 | AgenticAITA — Multi-Agent Reasoning | arxiv.org/abs/2605.12532 | ⚠️ niezweryf. | Wzorzec Senatu (debata ról) |
| 3 | ML-26 | CogAlpha — Alpha Factory | arxiv.org/abs/2511.18850 | ⚠️ niezweryf. | Auto-generowanie neuronów |
| 4 | ML-27 | NEXUS — Self-Evolving Market AI | github.com/The-R4V3N/Nexus | ⚠️ niezweryf. | Wzorzec autonomii (Faza 4) |
| 5 | A-12 | Kronos — Foundation Model for K-line | github.com/shiyu-coder/Kronos | ⚠️ niezweryf. | Neuron predykcyjny świec |

> **Uwaga:** ML-24..27 to NOWE klucze rezerwowe (dodane 2026-06-02). A-12 Kronos był już w katalogu
> (`KATALOG_NEURONOW.md` linia 314) — tu dostaje pełny opis i link.

---

## 1️⃣ ML-24 | Samoewoluująca Polityka Rubryk

- **Klucz:** `ML-24`
- **Pełna nazwa (oryginalna):** SHARP — Self-Evolving Rubric Policy
- **Nazwa po polsku:** Samoewoluująca Polityka Rubryk (system, który sam poprawia własne kryteria oceny)
- **Źródło (link):** https://arxiv.org/abs/2605.06822
- **Typ źródła:** praca naukowa (arXiv)
- **Status weryfikacji:** ⚠️ niezweryfikowany — podany przez Cezara, NIE sprawdziłem (data 2026-05 z przyszłości)
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
- **Status weryfikacji:** ⚠️ niezweryfikowany — podany przez Cezara, NIE sprawdziłem
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
- **Status weryfikacji:** ⚠️ niezweryfikowany — podany przez Cezara, NIE sprawdziłem
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
- **Status weryfikacji:** ⚠️ niezweryfikowany — podany przez Cezara, NIE sprawdziłem czy repo istnieje
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
- **Status weryfikacji:** ⚠️ niezweryfikowany — repo prawdopodobnie realne, ale NIE potwierdziłem
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

*VITRUVIUSZ — "Pięć obietnic z przyszłości. Zapisane z linkiem i uczciwym 'jeszcze nie sprawdziłem' —
to jest pamięć, nie marzenie."*
