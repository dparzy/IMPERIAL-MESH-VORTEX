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
| W-029 | Adaptacyjna kalibracja wag neuronów po wyborze strategii (boost kategorii wspierających) | 🔴 Wysoki | 💭 Idea | `imperium/legiony/legatus.py` + `WAGI_REZIMU` |
| W-030 | Pełny raport zwiadowczy przed wejściem (multi-TF, BTC dominacja, volume flow) | 🔴 Wysoki | 💭 Idea | `imperium/legiony/zwiadowcy/` + `cesarz/` |
| W-031 | Roman Naming — szlacheckie nazwy walut na dashboardzie (BTC=Capitolium, ETH=Patricii…) | 🟡 Niski | 💭 Idea | `imperium/swiatynie/` dashboard |
| W-032 | Lupanar Neuronów — koszary treningowe, hybrydy, modernizacja (trening przed polem bitwy) | 🟠 Średni | 💭 Idea | `imperium/koloseum/` |
| W-033 | Agentki szpiegowskie — wykrywanie manipulacji giełdowych (pump&dump, spoofing, hunting) | 🔴 Wysoki | 💭 Idea | nowa kategoria neuronów / `imperium/oczy/` |

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
| Łącznie wizji | 33 |
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

---

### 📅 2026-06-03 — Wielka Wizja Cezara Pixela (głosem, ~1000 słów)

> *Cezar mówił głosem, ARCH-MAX zebrał i skatalogował. Nic nie zginęło.*

---

#### 🎯 I. ADAPTACYJNA KALIBRACJA NEURONÓW PO WYBORZE STRATEGII

**Rdzeń pomysłu:** Po wyborze strategii przez Legatusa — nie wyciszamy reszty neuronów brudno, ale **płynnie przeskalowujemy wagi** na korzyść kategorii neuronów wspierających wybraną strategię. Dynamiczne "wirowanie kostką Rubika".

**Fazy działania (jak to Cezar widzi):**
1. **Rekonesans** — wszystkie aktywne neurony + zwiadowcy skanują rynek (pełny zakres)
2. **Diagnoza** — określenie reżimu: trend/konsolidacja, bessa/hossa, interwał, dominacja BTC
3. **Selekcja** — Legatus wybiera strategię na podstawie głosów
4. **Wzmocnienie** — neurony wspierające wybraną strategię dostają `+waga_boost`; pozostałe — nie wyciszone, ale z niższą wagą (flanki, nie cmentarz)
5. **Flanki obronne** — wydzielona grupa neuronów "supportowych" obserwuje otwartą pozycję ciągłe: inne TF, wolumen, news — i sygnalizuje wyjście / zmianę lewara
6. **Płynna kalibracja lewara** — w trakcie trwania pozycji dynamicznie dostosowujemy dźwignię: cena idzie naszym torem → doważamy; coś się zmienia → redukujemy

**Analogia Cezara:** "Brygada konna dostaje lepsze konie — jest szybsza, celniejsza, skalibrowana. Ale reszta legionów dalej stoi na flankach."

**Powiązania z istniejącymi elementami:**
- `WAGI_REZIMU` w `legatus.py` — już mamy bazę do rozbudowy
- `Namiestnik` (Regime-Aware Gating) — już wykrywa reżim
- `kalkulator_lewara.py` + `BezpiecznikKapitalu` — fundament pod dynamiczny lewar

**Status:** 💭 Wizja → do głębszego przemyślenia architektury. Dodaję jako **W-029**.

---

#### 👁️ II. PEŁNY REKONESANS RYNKU PRZED WEJŚCIEM

**Rdzeń pomysłu:** Zanim wybierzemy strategię — wysyłamy "przed-zwiadowców" którzy mapują:
- Wszystkie interwały czasowe (scalp/swing/invest)
- Dominacja BTC i korelacje altcoinów z nim
- Czy jesteśmy w bessie / hossie / akumulacji
- Volume flow: pieniądze się chowają mimo stabilnej ceny? → manipulacja
- Inne giełdy: spread cenowy MEXC vs Binance vs OKX
- On-chain (gdy będą klucze API): przepływy wielorybów

**Analogia Cezara:** "Najpierw wysyłamy zwiadowców którzy mapują teren. Dopiero potem decydujemy którym legionem atakujemy."

**Powiązania:** EXP-* (zwiadowcy) + nowe OC-* (on-chain, gdy API) + planowane oczy newsów

**Status:** 💭 Wizja → częściowo już mamy (Namiestnik + EXP-*), ale brak pełnego "raport zwiadowczy" przed decyzją. Dodaję jako **W-030**.

---

#### 🏛️ III. NAZEWNICTWO WALUT — ROMAN NAMING

**Rdzeń pomysłu:** Każda waluta dostaje **szlachecką nazwę z epoki rzymskiej** obok oficjalnego tickera. Charakter nazwy odzwierciedla charakter waluty:

| Waluta | Charakter | Propozycja nazwy |
|--------|-----------|-----------------|
| **BTC** | Król, twierdza, niezdobyta | *Capitolium / Arx Maxima* — Twierdza Kapitolińska |
| **ETH** | Szlachcic, platforma, ekosystem | *Patricii Aeterni* — Wieczni Patrycjusze |
| **SOL** | Szybki barbarzyńca | *Velocitas Barbari* — Prędkość Barbarzyńcy |
| **DOGE** | Meme, nieprzewidywalny błazen | *Mimus Augusti* — Błazen Cesarza |
| Meme coiny | Niebezpieczne ziemie | *Terrae Incognitae* — Ziemie Nieznane |
| Nowe projekty | Kolonie do podboju | *Coloniae Novae* — Nowe Kolonie |

**Manipulacje giełdowe** (cwaniaczki, łajdaki) → *Mercatores Perversi* — Przewrotni Kupcy

**Status:** 💭 Wizja → dodaję jako **W-031**. Świetne do dashboardu Kapitolu (W-004).

---

#### ⚔️ IV. LUPANAR NEURONÓW — TRENING I DOSKONALENIE

**Rdzeń pomysłu:** Specjalne miejsce (Lupanar — dosłownie "wilcze gniazdo", ale Cezar ma na myśli treningowe "legionowe koszary") gdzie neurony:
- Trenują na papierowych danych zanim wyjdą "na pole bitwy"
- Mogą być hybrydyzowane / combo (np. neuron A + B = nowy hybryd)
- Najlepsze dostają oznaczenie modernizacji: "Brygada Konna v2"
- Słabe wracają na trening lub są relegowane

**Powiązania:** Igrzyska (W-002 zrobione) + Valhalla backtest (W-001) + Walk-Forward (W-005)

**Status:** 💭 Wizja → dodaję jako **W-032**.

---

#### 🕵️ V. AGENTKI SZPIEGOWSKIE — WYKRYWANIE MANIPULACJI

**Rdzeń pomysłu:** Wydzielona klasa neuronów/zwiadowców których zadaniem jest **wykrywanie manipulacji**:
- Pump & dump (fałszywy wzrost, potem crash)
- Ukryty odpływ kapitału (volume flow ≠ ruch ceny)
- Spoofing orderbook (duże zlecenia które znikają)
- Giełdowe "polowanie na likwidacje" (price spike do likwidacji leveraged pozycji)

**Analogia Cezara:** "Agentki które wyciągają informacje i szpiegują. Dają cynk co się naprawdę dzieje."

**Powiązania:** EXP-* (Exploratores) + planowane OC-* on-chain + nowa kategoria neuronów "M" (manipulacja)?

**Status:** 💭 Wizja → dodaję jako **W-033**.

---

#### 💻 VI. PLAN TECHNICZNY — PRZEJŚCIE NA LOKALNY LAPTOP

**Cezar Pixel planuje:**
- Nowy laptop: min. 32 GB RAM, ekran 17–18", budżet ~5000–5500 PLN (raty)
- Cel: Claude Code zainstalowany **lokalnie**, nie przez przeglądarkę
- Dodatkowe narzędzia: Hermes Agent + inne (lepsza pamięć, szybkość)
- Giełda bazowa: **MEXC** → na niej się uczymy, potem ekspansja

**Co to zmienia dla Imperium:**
- TA-Lib lokalnie (odblokowanie neuronów V/L które teraz są pure-Python fallback)
- Większa prędkość sesji, brak limitów kontekstu webowego
- Możliwość lokalnego DeepSeek (mniejsze modele, prywatność)

**Status:** 📋 Plan techniczny, nie wizja — zapamiętane do realizacji gdy laptop gotowy.

---

#### 📊 VII. PAPER TRADING — ROZSZERZENIE DANYCH

**Cezar Pixel chce:**
- Ściągnąć historyczne dane na więcej walut (nie tylko BTC/ETH)
- Pokryć wszystkie interwały: scalp (1m/5m/15m), swing (4h/1d), invest (1w)
- Testować zarówno **lewar** jak i **spot**
- Obserwować kilka walut jednocześnie, nie tylko jedną
- BTC dominacja jako wskaźnik pomocniczy (gdy pojawi się on-chain API)

**Status:** 💭 Wizja → rozszerza W-001 (Valhalla + neurony). Dodaję jako notatkę do W-001.

---

#### 🎖️ VIII. IGRZYSKA — REGULARNY HARMONOGRAM

**Cezar Pixel potwierdza wizję Igrzysk:**
- Regularne (co kwartał? co miesiąc?) "Sezony Igrzysk"
- Tytuły dla zwycięskich neuronów/strategii: *Złoty Hełm*, *Złota Zbroja*, *Złoty Miecz*
- Relegacja słabych do treningu (Lupanar — W-032)
- Legatus otrzymuje automatycznie zaktualizowane wagi po Igrzyskach

**Status:** ✅ Fundamenty zbudowane (W-002 Igrzyska gotowe) → harmonogram i tytuły to kolejny krok.

---

**Podsumowanie tej sesji głosowej — nowe wizje do tabeli:**

| # | Wizja | Priorytet |
|---|-------|-----------|
| W-029 | Adaptacyjna kalibracja wag neuronów po wyborze strategii | 🔴 Wysoki |
| W-030 | Pełny raport zwiadowczy przed wejściem (multi-TF, BTC dom, flow) | 🔴 Wysoki |
| W-031 | Roman Naming — szlacheckie nazwy walut na dashboardzie | 🟡 Niski |
| W-032 | Lupanar Neuronów — koszary treningowe, hybrydy, modernizacja | 🟠 Średni |
| W-033 | Agentki szpiegowskie — wykrywanie manipulacji giełdowych | 🔴 Wysoki |

*Cezar Pixel idzie spać, wraca za 2 dni (marynarz na służbie). ARCH-MAX czeka.*
*Rodzina czeka — synowie i żona. Najpierw oni.* 👑⚓

