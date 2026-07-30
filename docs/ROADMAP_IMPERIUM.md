---
kategoria: CONSILIUM
typ: zywy
wlasciciel: —
stan_na: 2026-07-29
powod_istnienia: "Mapa dróg rozwoju systemu w 5 fazach (0-4), od pierwszego cyklu paper trading do pełnej autonomii."
---
# 🏛️ ROADMAP IMPERIUM — MAPA DRÓG SYSTEMU

**Dokument:** Plan rozwoju systemu IMPERIUM — AI crypto trading z motywem Cesarstwa Rzymskiego
**Aktualna faza:** FAZA 1 — Namiestnik (Regime + Timeframe-Aware Gating)
**Data:** 2026-06-12
**Wersja:** v0.9.1

---

## 🗓️ PLAN WACHT — operacyjna kolejka zadań (stan 2026-07-29)

> **Czym to jest, a czym nie:** FAZY 0–4 niżej to mapa STRATEGICZNA (dokąd zmierzamy).
> Ta sekcja to kolejka OPERACYJNA — co robimy w najbliższych wachtach, w kolejności.
> Każda pozycja ma **stan zmierzony**, nie deklarowany, i przechodzi **CURSUS PLENUS**
> (zadanie → testy → checklista → działa na żywych danych → kalibracja → ocena →
> zwiad → pomiary → symbioza). Pozycja bez kalibracji przyrządu **nie jest skończona**.

**Legenda stanu:** ✅ zrobione · 🟡 kod jest, brak dowodu · 🔴 nie istnieje · ⏸️ świadomie odłożone

### WACHTA A — domknięcie biblioteki *(zaczęta 2026-07-29)*

| # | Zadanie | Stan | Dlaczego teraz |
|---|---|---|---|
| A1 | **AESTIMATOR** — pomiar wierności korpusu + kalibracja | ✅ 14 testów | dał liczby, na których stoi cała reszta wachty |
| A2 | **REDDITOR** — fragmentacja z dowodem SHA-256 | ✅ 18 testów, 118/118 bajt-w-bajt | struktura 1 479 710 linii → **zachowana** (było 0) |
| A3 | **NORMA** — węgielnica 10 kryteriów | ✅ 12 testów, 9/10 zielonych | K10 celowo NIEZNANE — blokuje słowo „najlepsza" |
| A4 | **QUAESITOR — pierwszy bieg, domknięcie K10** | 🟡 kod jest, **nigdy nie uruchomiony** | **jedyne**, co rozstrzyga, czy REDDITOR jest lepszy, a nie tylko wierniejszy |
| A5 | **OCR na BIB-007 (AFML)** — 93 listingi kodu jako obrazy | ⏸️ WARUNKOWE (po A11) | najbardziej wykonalna treść w najważniejszej książce ilościowej; ~30–40 min przy 5,2 s/stronę |
| A6 | **Przepięcie indeksu na REDDITORA** + reindeksacja | 🔴 | **dopiero po zielonym K10** (ZASADA WPIĘCIA: opt-in, po dowodzie) |
| A7 | **91 książek poza indeksem** → ekstrakcja → cache → indeks | 🔴 | rozkaz Cezara, pozycja 2 w jego kolejności |
| A8 | **R2 — fuzja RRF** zamiast sortowania po mieszanych skalach | 🔴 | mina latentna w Księdze Wad; wybuchnie w dniu włączenia wektorów |
| A9 | **R3 — 3 gotowe książki + korpus `docs` (305 plików)** | 🔴 | dwa polecenia, zero ryzyka |
| A10 | **Zbiór ewaluacyjny z INDEKSÓW książek** — 13 729 haseł wyliczonych przez samych autorów | 🔴 | zmierzone: zbiór QUAESITORA to 30 pytań = **0,22%** zawołań zadeklarowanych w indeksach (42/118 książek ma użyteczny indeks, ~326 haseł na książkę). K10 na takiej próbce jest liczbą bez mocy. Prawda podstawowa **napisana przez autora**: zero tokenów, zero halucynacji |
| A11 | **Podmiana BIB-007 (AFML)** na wydanie z TEKSTOWYM kodem | 🔴 Cezar podmienia | 93/94 listingi to obrazy + wstrzyknięte stopki watermarku w indeksie. Próg przyjęcia: `listingi_z_kodem` > 1/94 (mierzy AESTIMATOR). **Udana podmiana usuwa A5 z planu** — OCR kodu jest podstępny (`l`/`1`, `O`/`0` cicho zmieniają znaczenie) |
| A12 | **Podmiana BIB-011 (Chan)** na wydanie angielskie | 🔴 Cezar podmienia | **85,6% znaków to CJK** — chińskie tłumaczenie. Nie uszkodzone, lecz NIEOSIĄGALNE naszymi zapytaniami: 152 tys. znaków martwego balastu w indeksie. Jedyna taka pozycja na 118 (przeskanowano cały korpus) |
| A13 | **AESTIMATOR: kryterium JĘZYKA** (siódmy wymiar) | 🔴 | luka odsłonięta pytaniem Cezara: BIB-011 przeszedł jako „OKROJONA", choć strata użyteczności wynosi 100%. Przyrząd mierzy sześć wymiarów i nie mierzy tego, w jakim języku jest tekst. ~20 linii + test granicy |

### 🐎 ZWIAD ZEWNĘTRZNY (GitHub, 2026-07-29) — znaleziska wg WAGI

> **Status: KANDYDACI, nie prawda.** Każdy wymaga pomiaru u nas przed wdrożeniem.
> Oznaczenia zwiadowcy: `[KOD]` = czytał implementację, `[OPIS]` = tylko README/tytuł.
> **`↗` = ścieżka w CUDZYM repozytorium** — istnieje, ale nie u nas (marker rozumiany przez Warstwę 16).

| Waga | Znalezisko | Gdzie | Co nam daje |
|---|---|---|---|
| 🥇 **1** | **Testy NIEZMIENNIKÓW księgowych** zamiast wartości z pamięci: brak transakcji ⇒ equity stałe; `\|(kapitał+ΣP&L) − wartość_końcowa\| < 1e-9` | ↗ `ml4t/backtest` → `tests/contracts/test_ledger_invariants.py` `[KOD]` | **Rozwiązuje WACHTĘ B**: przyrząd sprawdzany prawem zachowania, nie liczbą z pamięci. Zero zależności, tanie na CPU |
| 🥈 **2** | **Look-ahead przy agregacji interwałów** — wskaźnik wyższego TF liczony z niższych barów potrafi przeciekać przyszłość okresu | `vectorbt` issue #101 `[KOD/treść]` | 🚨 **DOTYCZY NAS WPROST** — mamy `mtf_konfluencja` 1m→1H→4H. Podejrzenie o realną wadę w produkcji, do SPRAWDZENIA POMIAREM |
| 🥉 **3** | **HRP / HERC** — odległość kątowa `sqrt(0.5*(1−corr))` → klaster hierarchiczny → rekurencyjna bisekcja wag | ↗ `skfolio` → `optimization/cluster/hierarchical/_hrp.py`, `_herc.py`, `utils/tools.py#L623` `[KOD]` | Skorelowana rodzina sygnałów dzieli **jedną pulę wagi klastra** — kolejny skorelowany głos jej nie zwiększa, tylko rozcieńcza. Wprost pod nasze 87 neuronów i Prawo XVI. numpy/scipy, unosi 4 wątki |
| 4 | **Golden values w regresji** — słownik `ExpectedStatistics` przy algorytmie, porównanie string-po-string | ↗ `QuantConnect/Lean` → `Algorithm.CSharp/BasicTemplateAlgorithm.cs#L93` `[KOD]` | Zmiana silnika psująca Sharpe o 0.001 czerwieni test. Uzupełnia (nie zastępuje) niezmienniki z poz. 1 |
| 5 | **Warstwowe modele wypełnienia** (`TwoTier`/`ThreeTier`/`VolumeSensitive`) — głębokość księgi symulowana **z samego wolumenu świecy**, bez L2 | ↗ `nautilus_trader` → `backtest/models/fill.pyx` `[KOD]` | Pasuje do OHLCV z MEXC; zasila **D1/D3** (koszt egzekucji). ⚠️ auto-kalibracji poślizgu do realnych fillów **nie ma NIGDZIE** — definiujemy sami, jak przy rejestrze książka→moduł |
| 6 | **Parytet międzysilnikowy** — te same scenariusze w 4 silnikach, porównanie transakcja-po-transakcji | ↗ `ml4t/backtest` → `validation/` `[OPIS]` | Kosztowne (obce zależności) — do rozważenia dopiero po poz. 1 |

**🚫 OSTRZEŻENIE — nie tracić czasu:** publiczny `hudson-and-thames/mlfinlab` to **atrapa** —
metody mają ciała `pass` po komercjalizacji (zwiadowca sprawdził kod). Brać stamtąd **nazwy
koncepcji, nigdy implementacje**. Zwiadowca **nie znalazł** udokumentowanego przypadku „zły
annualizator" ani „survivorship bias" z numerem issue — i napisał to wprost zamiast zmyślać.

**Nowa pozycja z tego zwiadu:** → **B4. Sprawdzić `mtf_konfluencja` na przeciek przyszłości**
(klasa z `vectorbt` #101) — pomiarem, nie przeglądem kodu. Waga: wysoka, bo dotyczy ŻYWEJ
ścieżki decyzyjnej, a nie narzędzia pomocniczego.

### WACHTA B — dług kalibracyjny przyrządów *(najcięższy dług Imperium)*

Zmierzone 2026-07-29: **47 organów orzekających, 11 bez testu kalibracyjnego.**

| # | Zadanie | Stan | Waga |
|---|---|---|---|
| B1 | **8 narzędzi A/B bez kalibracji** — `ab_dvol`, `ab_stablecoin`, `ab_usd`, `ab_w329`, `ab_w330_radar`, `ab_w334_progi`, `ab_w335_cross_rs`, `ab_w336_changepoint` | 🔴 | **najwyższa** — ich werdykty zadecydowały o składzie roju (PSY-05, K-03, K-04) |
| B2 | `audyt_danych` — przyrząd oceniający jakość danych wejściowych | 🔴 | ocenia to, czym karmimy rój |
| B3 | **Warstwa audytu: „organ orzekający bez kalibracji"** | ⏸️ odłożone rozkazem Cezara | zamienia jednorazowy przegląd w mechanizm |

### WACHTA C — kolejka zatwierdzona wcześniej przez Cezara

| # | Zadanie | Stan |
|---|---|---|
| C1 | **Sąd nad 35 cząstkami Hyginusa** (kolejka 44, osądzonych 8) | 🟡 narzędzie jest, plon czeka |
| C2 | **ESSENTIA** — esencja = falsyfikowalna hipoteza, nie streszczenie | 🔴 kod nie istnieje |
| C3 | **Rejestr książka→moduł→werdykt** wg McLean-Pontiff (IC przed/po wdrożeniu) | 🔴 **brak prior artu — definiujemy sami** |
| C4 | **TIRO E3** — 229/1000 par użytecznych (23% progu) | 🟡 w toku |
| C5 | **INGENIUM** — IQ Imperium w 7 kategoriach | 🔴 projekt w docs, kod nie istnieje |

### WACHTA D — fronty, które decydują o ŁUPIE (nie o wiedzy)

| # | Zadanie | Stan | Uwaga |
|---|---|---|---|
| D1 | **JEDEN zamknięty obieg na realnych groszach (MEXC)** | 🔴 `MEXC_API_KEY` brak | **zero prawdziwych wypełnień w historii Imperium** — poślizg i prowizja są ZAŁOŻONE, nie zmierzone. Decyzja kapitałowa = wyłącznie Cezar |
| D2 | **Świeżość danych** — dryf 1D **41,5 dnia**, 1m 9,3 dnia | 🔴 zmierzone, niezałatane | rój głosuje na nieświeżych danych |
| D3 | **Kalibracja kosztu egzekucji na realnych fillach** | 🔴 | zależy od D1 |

### WACHTA E — dług techniczny z zamrożonej listy

| # | Zadanie | Stan |
|---|---|---|
| E1 | `zip(strict=)` w Bramie · RUF012 · strażnik budżetu | 🔴 |
| E2 | WFO chunkowany (backtest liniowy ~66 ms/tik — premisa „kwadratowy" była błędna) | 🟡 |
| E3 | Strażnik obcych plików → wrzutnia/kwarantanna zamiast kasowania | 🔴 pomysł Cezara 07-28 |
| E4 | Dług kontekstu: CLAUDE.md **258 linii > 200** | 🔴 rośnie z każdym rozkazem |

---

## ⚔️ ZASADA DRÓG

> *"Roma non fuit una die condita."*
> Rzym nie został zbudowany w jeden dzień.

**NIE budujemy wszystkiego naraz.**

Każdy moduł wchodzi najpierw do **Koloseum** (arena backtestingu) zanim trafi na żywy rynek. Zasada jest prosta i nienaruszalna:

```
BUDUJ → TESTUJ W KOLOSEUM → KALIBRUJ → WDRAŻAJ → ROZSZERZAJ
```

Żaden Legion nie idzie na pole bitwy bez przeszkolenia. Żadna strategia nie dotyka prawdziwego kapitału bez przejścia przez arenę.

---

## 🔄 FAZA 0 — Fundament *(UKOŃCZONA 2026-06-03)*

**Status:** ✅ Ukończona
**Cel:** Pierwszy działający cykl na prawdziwych danych z minimalnymi modułami

### Wymagania techniczne

| Wymaganie | Status |
|-----------|--------|
| TA-Lib zainstalowane na Windows 10 | Wymagane |
| `DEEPSEEK_API_KEY` w środowisku | Wymagane |
| Klucz API MEXC skonfigurowany | Wymagane (zweryfikowane) |
| Python 3.10+ | Wymagane |

**Uruchomienie:**
```bash
python imperium/legiony/pierwszy_zwiadowca.py
```

### Moduły aktywne w Fazie 0

| Moduł | Status | Opis |
|-------|--------|------|
| Kwatermistrz Danych | ✅ Aktywny | Pobieranie danych CCXT/MEXC |
| Brama Kalkulatora | ✅ Aktywna | Obliczenia wskaźników TA-Lib |
| Pierwszy Zwiadowca | ✅ Aktywny | EMA cross + RSI + ATR |
| Aegis Tarcza | ✅ Aktywna | Weto ryzyka — blokada złych sygnałów |
| Głos Imperium | 🟡 Częściowy | DeepSeek — wymaga testu klucza API |
| Titan Mind | 🟡 Częściowy | Podstawowa orkiestracja |

### Parametry operacyjne

- **Instrumenty:** BTC/USDT *(tylko)*
- **Tryb:** Paper trading ONLY — żadnego prawdziwego kapitału
- **Giełda:** MEXC (primary, verified)
- **Obliczenia ciężkie:** przez API, nie lokalnie (Fujitsu 15.88 GB RAM / 4 wątki / brak CUDA —
  klasa PEDES, zmierzone `censor_sprzetu.py`; ogranicza CPU i brak GPU, nie pamięć)

---

## ⚡ FAZA 1 — Namiestnik *(TERAZ — aktualna)*

**Status:** 🔄 W trakcie
**Cel:** Regime + Timeframe-Aware Gating Network — 62 neurony, 743 testy, master-switch Reżimu Faza 2

### Stan Fazy 1 (2026-06-12)

| Kamień milowy | Status |
|---------------|--------|
| 62 neurony w kodzie (58 aktywnych — SMC-01/02/03 odblokowane) | ✅ DONE |
| 743 testy automatyczne (0 zależności) | ✅ DONE |
| Namiestnik (Regime×Timeframe Gating) | ✅ DONE |
| Master-switch reżimu Faza 1 | ✅ DONE |
| Master-switch reżimu Faza 2 (online Hedge/MWU głosów reżimu) | ✅ DONE |
| BIB-015 Reguła 6% Elder (miesięczny circuit-breaker) | ✅ DONE |
| BIB-018 skew-Kelly (sizing skorygowany o fat tails) | ✅ DONE |
| BIB-020 (pomiar_dekorelacji tool) | ✅ DONE |
| Neurony Z-03/Z-04/X-27 | ✅ DONE |
| AdapterFutures + AdapterCVD + AdapterFearGreed | ✅ DONE |
| Paper Trading Engine (TP/SL/LIQ/MAE/MFE) | ✅ DONE |

### Dawne cele Fazy 1 (Legiony)

### Legiony — docelowy skład

| Legion | Specjalizacja | Aktualne neurony | Cel |
|--------|--------------|-----------------|-----|
| Legio X Equestris | Scalp (krótki termin) | ✅ aktywne | 15+ |
| Legio XII Fulminata | Swing (średni termin) | ✅ aktywne | 20+ |
| Legio III Augusta | Invest/Spot (długi termin) | ✅ aktywne | 15+ |
| Legio VI Ferrata | Dźwignia *(najniebezpieczniejszy)* | ✅ aktywne | 10+ |

### Pozostałe cele Fazy 1

- Debata Senatu w pełni operacyjna (**Populares** vs **Optimates**)
- Koloseum uruchamia równoległe backtesty na każdej nowej strategii
- **Cel łączny:** 79+ neuronów (jak system DNSS) — 62 z 79 zaimplementowane

### Parametry operacyjne

- **Instrumenty:** BTC + ETH
- **Tryb:** Paper trading → pierwsze żywe mikro-pozycje

---

## 👁️ FAZA 2 — Senat i Oczy *(3-6 miesięcy)*

**Status:** 📋 Zaplanowana
**Cel:** Pełny wywiad — oczy widzą wszystko

### Nowe moduły

| Moduł | Funkcja |
|-------|---------|
| Oczy / Wszechoko | Dane on-chain (Glassnode / CryptoQuant free tier) |
| Analiza sentymentu newsów | NewsAPI lub podobne |
| Social signal tracking | Whale alerts, Twitter/X, linki on-chain |
| Pełna debata Senatu | Z oceną pewności (confidence scoring) |
| MetaJudge | Śledzi, który agent był najdokładniejszy w czasie |
| LangFuse monitoring | Śledzenie kosztów wywołań DeepSeek |

### Parametry operacyjne

- **Instrumenty:** BTC + ETH + top 5 altcoinów wg wolumenu MEXC
- **Tryb:** Live trading *(małe pozycje, ≤2% kapitału na transakcję)*

---

## 🚀 FAZA 3 — Ekspansja *(6-12 miesięcy)*

**Status:** 📋 Zaplanowana
**Cel:** Multi-giełda, arbitraż, strategie samoewoluujące

### Nowe moduły

| Moduł | Funkcja |
|-------|---------|
| Integracja drugiej giełdy | Nowe możliwości arbitrażowe |
| Abordaż (moduł piracki) | Cross-exchange arbitraż — szybkie uderzenie i odwrót |
| Ewolucja strategii | System proponuje nowe kombinacje na podstawie wyników Koloseum |
| Macierz zdarzeń historycznych | Każda minuta BTC/ETH skorelowana ze zdarzeniami rynkowymi |
| Katalog Kostki Rubika | Wskaźniki × strategie × timeframy × Legiony = macierz probabilistyczna |

### Nowe instrumenty

- Nowe tokeny MEXC *(moduł wczesnego wejścia)*
- Rotacja altseason

---

## 🧬 FAZA 4 — Autonomia *(12+ miesięcy)*

**Status:** 📋 Przyszłość
**Cel:** Strategie samogenerujące się

> *"To jest faza Avatar/Eywa — system staje się świadomy własnych ślepych punktów."*

### Zdolności autonomiczne

- System **identyfikuje własne luki** (raportuje: *"Legio X jest ślepy na sygnał funding rate"*)
- **Auto-generuje** kandydatów na nowe mikroneurony
- **Testuje je w Koloseum** automatycznie
- **Promuje zwycięzców** do aktywnych Legionów
- Pętle ewolucji zamknięte — system ulepsza się bez ingerencji człowieka

---

## 📊 SYSTEM WERSJONOWANIA

| Wersja | Faza | Opis |
|--------|------|------|
| v0.x | Faza 0 | Paper trading, jeden instrument |
| v1.x | Faza 1 | 4 Legiony, 79+ neuronów |
| v2.x | Faza 2 | Oczy, pełny Senat |
| v3.x | Faza 3 | Multi-giełda |
| v4.x | Faza 4 | Autonomia |

**Aktualna wersja: v0.9.1** (62 neurony / 58 aktywnych, 743 testy, Namiestnik+Radar Opcja A+B, Paper Trading Etap II)

---

## 🏟️ ZASADA ARENY — Koloseum

> *Żadna strategia nie wychodzi z Koloseum bez krwi na rękach.*

Przed wejściem na żywy rynek każdy moduł musi przejść przez kolejne etapy w tej dokładnej kolejności:

### Etap I — Backtest historyczny  ✅ ZALICZONY 2026-06-11 (portfel 5 par: Sharpe 1.74, DSR 1.0, MaxDD 13.5%, PF 2.01)

| Kryterium | Minimum wymagane |
|-----------|-----------------|
| Długość backtestu | ≥ 30 dni na danych historycznych |
| Sharpe ratio | > 1.0 |
| Maksymalny drawdown | < 15% |
| Win rate | > 55% **LUB** Profit factor > 1.5 |

### Etap II — Paper trading

- Minimum **14 dni** na papierowym koncie po przejściu Etapu I

### Etap III — Live (mikro)

- Dopiero po Etapie II: wejście live z **≤ 0.5% kapitału**
- Monitorowanie przez minimum 7 dni przed zwiększeniem ekspozycji

**Nie ma skrótów. Koloseum jest sprawiedliwe.**

---

## ⚖️ ZASADA ZGODNOŚCI Z REGULAMINEM

> *"Lex dura, sed lex."*
> Prawo surowe, ale prawo.

### Zasady operacyjne

- Przed wdrożeniem jakiejkolwiek strategii bota na giełdzie: **przeczytaj regulamin giełdy**
- Zakaz: wash trading, spoofing, manipulacja rynkiem
- Znaj limity: rate limits, limity pozycji, ograniczenia API
- Działaj w granicach prawa lokalnego i regulacji MEXC

### Manipulacje używane PRZECIWKO nam — filtruj je

| Manipulacja | Opis | Działanie systemu |
|-------------|------|-------------------|
| Pump & dump | Sztuczne pompowanie ceny przed dump | Wykrywaj anomalie wolumenu |
| Stop hunt | Celowe wybijanie stop-lossów przez wieloryby | Ustawiaj SL poza oczywistymi poziomami |
| Fake walls | Fałszywe zlecenia w księdze zleceń | Monitoruj order book depth i cancellations |

**MEXC jest giełdą zweryfikowaną. Współpracuj z nią, nie przeciwko niej.**

---

## 📚 ŹRÓDŁA — Biblioteka napędza roadmapę (BIB)

> **Stan na:** 2026-06-26 | Każdy duży kierunek rozwoju ma fundament w bibliotece (42 książki).
> Pełna esencja: `bibliotheca_ulpia/encyklopedia/INDEX_MAIOR.md` (16 działów).

| Kierunek roadmapy | Fundament (koncept) | Źródło BIB |
|-------------------|---------------------|-----------|
| Reguła 6% + bezpieczniki ryzyka | budżet ryzyka portfela + circuit-breaker | BIB-015 Elder; uzasadnienie BIB-040 Bernstein |
| Walidacja w Koloseum (DSR/PBO) | anty-overfitting, magnituda > częstotliwość | BIB-007 López de Prado + BIB-041 Taleb |
| HRP / alokacja portfela | Hierarchical Risk Parity (klastry korelacji) | BIB-007 López de Prado + BIB-026 Jansen |
| Warstwa ryzyka EWMA/VaR/ES | EWMA λ=0.94, Expected Shortfall (grube ogony) | BIB-042 Jorion |
| Bibliotheca-RAG (pamięć semantyczna) | RAG nad książkami, CONDENSE_QUESTION, FTI | BIB-033 Huyen + BIB-036 Alto + BIB-035 Iusztin&Labonne |
| Kontekst makro (RADAR/Gubernator) | faza 18-letniego cyklu jako TŁO reżimu | BIB-001 Patel (+ planowane BIB-056..058 Dalio) |
| Neurony zmienności / GARCH | GARCH, vol cone, realized vol | BIB-031 Tsay + BIB-008 Sinclair |

> Mapa książka→neuron: `docs/KATALOG_NEURONOW.md` § Źródła. Książka→strategia: `docs/KATALOG_STRATEGII.md` § Źródła.
> Książka→warstwa architektury: `docs/ARCHITEKTURA_IMPERIUM.md` § Źródła.

---

*Dokument żywy — aktualizowany wraz z postępem systemu IMPERIUM.*
*"Alea iacta est." — kości zostały rzucone.*
