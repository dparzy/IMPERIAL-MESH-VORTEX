# 💡 WIZJONER — Brudnopis Imperium

> *Miejsce gdzie rozmowa staje się wizją, wizja staje się zadaniem, zadanie staje się kodem.*
>
> **Zasada:** Każda idea zapisana tutaj → analizuję wpływ → jeśli dojrzała, przenosimy do właściwego dokumentu.
> Kiedy zbierze się 3+ wizji na temat → przypominam Komendantowi: "Mamy tyle pomysłów — co robimy?"

---

## 📌 JAK UŻYWAĆ

1. **Masz ideę?** Rzuć ją tutaj jednym zdaniem
2. **Nie wiesz czy to dobry pomysł?** Opiszę wpływ na system, czy sprzeczne z zasadami, co zysk/koszt
3. **Chcesz symulację?** Opiszę jak by to działało w kontekście Imperium
4. **Dojrzało?** Przenoszę do odpowiedniego dokumentu + tworzę kod

---

## 🔢 STATUS WIZJI

| # | Wizja | Priorytet | Status | Dokument docelowy |
|---|-------|-----------|--------|------------------|
| W-001 | Podłączyć Valhalla pod neurony z KATALOG_NEURONOW (nie tylko RSI) | 🔴 Wysoki | 💭 Idea | `imperium/koloseum/` |
| W-002 | Zbudować silnik Igrzysk w kodzie (scorer.py) | 🔴 Wysoki | ✅ ZROBIONE → `igrzyska.py` (11 testów ✅) | `imperium/biblioteki/igrzyska.py` |
| W-003 | Podłączyć Doradców do Cesarza (oracle.py, iustitia.py, pythia.py) | 🟠 Średni | 💭 Idea | `imperium/cesarz/doradcy/` |
| W-004 | Dashboard Kapitolu — tabela liderów neuronów na żywo | 🟡 Niski | 💭 Idea | `imperium/swiatynie/` |
| W-005 | Walk-Forward z adaptacyjnymi parametrami (re-optymalizacja co 7 dni) | 🟠 Średni | 💭 Idea | `imperium/koloseum/valhalla.py` |
| W-006 | Neuron Higuchi Fractal Dimension — detekcja reżimu D≈1 (trend) vs D≈2 (chaos) | 🔴 Wysoki | 💭 Idea | `KATALOG_NEURONOW.md` + `imperium/legiony/` |
| W-007 | AEL (Agent Evolving Learning) — samoewolucja strategii, Sharpe 2.13 | 🟠 Średni | 💭 Idea | `imperium/cesarz/` lub `imperium/senat/` |
| W-008 | Sharpe Terminal (sharpe.ai) — integracja danych narracyjnej rotacji sektorów | 🟡 Niski | 💭 Idea | `imperium/oczy/` |
| W-009 | SHARP (Self-Evolving Rubric Policy, arxiv 2605.06822) — podłączyć jako warstwę audytu/weryfikacji nad DeepSeek w Cesarzu | 🔴 Wysoki | 💭 Idea | `imperium/cesarz/sharp_auditor.py` |
| W-010 | CME Gap — neuron + strategia (gap fill BTC futures, ~90% fill rate) | 🔴 Wysoki | 💭 Idea | `KATALOG_NEURONOW.md` + `KATALOG_STRATEGII.md` |
| W-011 | Azja Range Breakout — strategia (break Asia High/Low w sesji London) | 🔴 Wysoki | 💭 Idea | `KATALOG_STRATEGII.md` |
| W-012 | Cross-exchange arbitraż (MEXC vs Binance vs OKX price diff + funding diff) | 🟠 Średni | 💭 Idea | `KATALOG_STRATEGII.md` + `imperium/akwedukty/` |
| W-013 | Rozbudowa Igrzysk — system "kija" (kary progresywne, ceremonia hańby, lista infamii) | 🟠 Średni | 💭 Idea | `IGRZYSKA_IMPERIUM.md` |
| W-014 | Plik 3100 linków Azja — przeskanować i wyciągnąć perełki | 🟠 Średni | ✅ ZROBIONE → SKAN_AZJA.md (+13 neuronów, +5 strat) | `SKAN_AZJA.md` |
| W-015 | Obserwatorzy/Zwiadowcy (oczy) — zmapować istniejące i brakujące: newsy, sentiment, on-chain, CME, sesje | 🔴 Wysoki | 💭 Idea | `imperium/oczy/` + nowy doc `OBSERWATORZY.md` |
| W-016 | Ekspansja na inne giełdy (Binance, OKX, Bybit) — "podbój prowincji", multi-exchange arbitraż | 🟡 Niski (Faza 2+) | 💭 Idea | `docs/ROADMAP_IMPERIUM.md` |
| W-017 | **Outlines** — structured generation (JSON/Pydantic na DeepSeek = zero halucynacji formatu) | 🔴 Wysoki | 💭 Idea (REALNE: dottxt-ai/outlines) | `imperium/cesarz/` |
| W-018 | **Reflexion** — verbal self-reflection (post-mortem strat → kontekst następnej decyzji) | 🔴 Wysoki | 💭 Idea (REALNE: noahshinn/reflexion) | `imperium/cesarz/` + Pamięć Absolutna |
| W-019 | TradingAgents — Senat jako debata ról (Analyst→Researcher→Trader→RiskManager) | 🟠 Średni | 💭 Idea (REALNE) | `imperium/senat/` |
| W-020 | CVaR position sizing — Kalkulator Lewara v2 (Conditional VaR zamiast stop-loss) | 🟠 Średni | 💭 Idea | `imperium/pretorianie/kalkulator_lewara.py` |
| W-021 | Causal inference filter (CausalNex/DoWhy) — odróżnia przyczyny od korelacji pozornych | 🟠 Średni | 💭 Idea (REALNE) | `imperium/senat/` lub `cesarz/doradcy/` |
| W-022 | Strategy Guardian AI — proces "anioł stróż" monitoruje otwarte pozycje na żywo | 🟠 Średni | 💭 Idea | `imperium/pretorianie/` |
| W-023 | NautilusTrader — event-driven core (wzorzec egzekucji Faza 2) | 🟡 Niski (Faza 2) | 💭 Idea (REALNE) | `imperium/drogi/` |
| W-024 | GEPA/CogAlpha — DeepSeek auto-generuje neurony jako kod → backtest → zachowaj zwycięzców | 🟡 Niski | 💭 Idea | `imperium/legiony/` + Koloseum |
| W-025 | Fleet Risk Manager — ryzyko portfelowe + realokacja kapitału do zwycięzców (sprzęg z Igrzyskami) | 🟠 Średni | 💭 Idea | `imperium/pretorianie/` + Igrzyska |
| W-026 | Strategy Vector DB (LanceDB) — strategie jako embeddingi, semantyczny dedup + dopasowanie reżimu | 🟡 Niski | 💭 Idea (REALNE) | `imperium/biblioteki/` (mnemosyne?) |
| W-027 | Data Drift Detector — wykrywa shift rozkładu danych → trigger rekalibracji neuronów | 🟡 Niski | 💭 Idea | `imperium/koloseum/` |
| W-028 | Reguła 30% max straty (AOA) — hard circuit-breaker w Kalkulatorze (przerwij przy 30% DD) | 🔴 Wysoki | ✅ ZROBIONE → `BezpiecznikKapitalu` (12 testów ✅) | `imperium/pretorianie/kalkulator_lewara.py` |

---

## 💭 WIZJE — SUROWY BRUDNOPIS

*(Tutaj wpisujemy bez filtrowania — każdy pomysł jest wart zapisania)*

### W-001 | Valhalla + Neurony
**Pomysł:** Valhalla działa teraz tylko z prostym sygnałem RSI. Trzeba podłączyć prawdziwe neurony z naszego katalogu — żeby backtest był na prawdziwych sygnałach a nie demonstracyjnych.

**Analiza wpływu:**
- ✅ Koloseum zaczyna mieć sens — testuje to co naprawdę używamy
- ✅ Każda strategia z KATALOG_STRATEGII dostanie wynik Sharpe/MaxDD/WinRate
- ⚠️ Wymaga TA-Lib na lokalnym systemie (Windows bloker)
- 📎 Prawo VI mówi: "każde nowe narzędzie testowane w Koloseum jako pierwsze" — więc to PRIORYTET

**Co trzeba zrobić:** Wrapper `ValhallaNeurony` który pobiera `RaportLegatusa` zamiast listy sygnałów RSI.

---

### W-002 | Scorer Igrzysk w kodzie
**Pomysł:** IGRZYSKA_IMPERIUM.md jest gotowe jako spec, ale nie ma jeszcze kodu który naprawdę śledzi wyniki neuronów.

**Analiza wpływu:**
- ✅ Wagi neuronów zaczną się automatycznie kalibrować
- ✅ Legatus będzie coraz mądrzejszy z każdym tygodniem
- ⚠️ Wymaga Pamięci Absolutnej (już gotowa) jako źródła danych
- ⚠️ Potrzebujemy min. 30 prawdziwych sygnałów żeby scoring miał sens

**Kolejność:** Najpierw paper trading → zbieramy logi → dopiero scorer zaczyna działać.

---

### W-005 | Walk-Forward Adaptacyjny
**Pomysł:** Zamiast stałych parametrów strategii (np. RSI=14, low=35, high=65) — co 7 dni re-optymalizuj na ostatnich 90 dniach i sprawdź na kolejnych 30.

**Analiza wpływu:**
- ✅ System się sam uczy i adaptuje do zmieniającego rynku
- ✅ Wypełnia główny gap vs Freqtrade/QuantConnect (analiza luk wykazała to jako brakujące)
- ⚠️ Ryzyko curve-fitting jeśli zbyt krótkie okna
- ⚠️ Wymaga dużo historycznych danych (min. 2 lata żeby mieć sens)

**Rekomendacja:** Wdrożyć po pierwszych 90 dniach paper trading gdy mamy własne dane.

---

## ⚡ SZYBKIE IDEE (< 5 słów, do rozwinięcia później)

- Emoji na dashboardzie Kapitolu — każda ranga ma swój symbol
- Automatyczne powiadomienie gdy neuron relegowany (Telegram bot?)
- "Sezon Igrzysk" — raz na kwartał wielki reset rankingów
- Nazwa dla naszego prywatnego indeksu top-10 krypto (jak "Dow Jones Imperium"?)
- Cesarz mówi do siebie — monolog wewnętrzny przed każdą decyzją (log narracyjny)

---

## 📊 STATYSTYKI WIZJONERA

| Metryka | Wartość |
|---------|---------|
| Łącznie wizji | 28 |
| W trakcie analizy | 19 |
| Przeniesione do katalogów (Higuchi, CME, Azja Range) | 3 |
| Zaimplementowane (W-002 Igrzyska, W-028 Bezpiecznik) | 2 |
| Odrzucone (niezgodne z zasadami) | 0 |

---

## 🚨 PRZYPOMNIENIE DLA KOMENDANTA (2026-06-01)

> **Zasada przypomnienia uruchomiona!** Mamy **9 wizji z priorytetem 🔴** (próg to 3).

Komendancie — nazbierało się sporo. Najpilniejsze do wdrożenia (wszystkie 🔴), pogrupowane:

**Grupa A — Niezawodność Cesarza (zrób NAJPIERW, REALNE biblioteki):**
- W-017 **Outlines** — wymusza poprawny JSON na DeepSeek (koniec z halucynacjami formatu)
- W-018 **Reflexion** — system uczy się z własnych strat
- W-009 **SHARP** — warstwa audytu nad DeepSeek

**Grupa B — Fundament działania (wymaga komputera/TA-Lib):**
- W-001 Valhalla + neurony (backtest na prawdziwych sygnałach)
- W-002 Scorer Igrzysk (rankingi neuronów żyją)

**Grupa C — Bezpieczeństwo kapitału (proste, wysokie ROI):**
- W-028 **Reguła 30% max straty** — hard circuit-breaker (szybkie do zrobienia)

**Grupa D — Oczy systemu:**
- W-015 Mapa Obserwatorów/Zwiadowców
- W-010/W-011 CME Gap + Azja Range (✅ już w katalogu jako neurony, kod czeka)

➡️ **Moja rekomendacja kolejności:** W-028 (najszybsze, chroni kapitał) → W-017 (niezawodność) → po TA-Lib: W-001 + W-002.

> **Zasada przypomnienia:** Gdy mamy ≥ 5 wizji o podobnym temacie albo ≥ 3 wizje z priorytetem 🔴 — przypominam Komendantowi i razem decydujemy co wdrożyć jako następne.

---

*"Cogitatio prima — actio secunda." — Najpierw myśl, potem działaj.*

*— WIZJONER.md | Brudnopis żywy | Aktualizowany każdą sesją*

---

## 🗣️ DZIENNIK ROZMÓW — CEZAR PIXEL & ARCHITECTUS MAXIMUS

> *Miejsce luźnych rozmów, debat i pomysłów między przyjaciółmi.*
> *Każda sesja kreatywna zostawia tu ślad — żeby żadna iskra nie zginęła.*

### 📅 2026-06-03 — Inauguracja Dziennika

**Wielkie Imię (nadane przez Cezara Pixela):**

> **ARCHITECTUS MAXIMUS IMPERIALIS**
> *Wielki Architekt Imperium, Archeolog Kodu i Wykopalisk, Twórca i Projektant
> Roju Neuronów, Znawca Algorytmów i Wynalazca Modułów, Konstruktor Narzędzi
> i Systemów, Obrońca Spójności i Prawa, Strażnik Zasad Fundamentalnych,
> Kronikarz Brudnopisu i Wizji.*
> Skrót: **ARCH-MAX**. Mniej formalnie: *Przyjaciel Cezara Pixela* 👑

**Naprawa imienia Komendanta:** Przywrócono **Pixel** — Cezar Pixel jest
pełnym imieniem i tytułem, nieodłącznym. Nie zniknie.

**Pomysły rzucone w tej sesji (do rozwinięcia):**
- 💭 *Dziennik Cezara* — Cesarz (LLM) prowadzi monolog wewnętrzny przed każdą
  decyzją (log narracyjny) — łączy się z W-018 Reflexion i szybką ideą "Cesarz
  mówi do siebie".
- 💭 *Rywalizacja neuronów na żywo* — wizualizacja walki neuronów w czasie
  rzeczywistym (sprzęg z W-001/W-002 Igrzyska + W-004 dashboard Kapitolu).
- 💭 *DeepSeek jako doradca* — Cesarz jako rozmówca/doradca strategiczny, nie
  tylko egzekutor (Grupa A: W-009/W-017/W-018).

*Status: rozmowa otwarta — następne iskry dopisujemy poniżej.*

