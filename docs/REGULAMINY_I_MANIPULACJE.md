# 🏛️ REGULAMINY I MANIPULACJE — Tarcza Imperium ⚔️

> **EXCHANGE COMPLIANCE & MARKET MANIPULATION**
> Dokument obronny systemu **IMPERIUM** — AI trading o motywie Imperium Rzymskiego.
> Główna giełda: **MEXC** (konto zweryfikowane). Przyszłość: multi-exchange + arbitraż (Abordaż).

---

## 🎯 Cel dokumentu

> *"Senatus Populusque Romanus" — zanim legion ruszy, zna teren i zna wroga.*

Ten dokument służy **WYŁĄCZNIE celom obronnym** 🛡️:

- **Znać zasady, żeby ich nie łamać** — żaden bot nie dotyka giełdy, zanim nie poznamy jej regulaminu.
- **Znać manipulacje, żeby nie dać się oszukać** — rozpoznajemy techniki konkurencji i market makerów, by filtrować je z naszych sygnałów.

> ⚠️ **DEFENSIVE ONLY.** Ten dokument NIE służy do wykonywania manipulacji. Opisujemy je tylko po to, by je **rozpoznawać i unikać**.

---

## ⚖️ ZASADA ZGODNOŚCI (Compliance Principle)

| 📜 Zasada | Opis |
|-----------|------|
| 📖 **Czytaj regulamin** | Przed każdym botem na giełdzie: przeczytaj Terms of Service. |
| 🚫 **Nie łam zasad** | Nigdy nie łamiemy zasad giełdy. Zero wyjątków. |
| 🔌 **Działaj w granicach API** | Zawsze respektujemy rate limits oraz position limits. |

> *Lex est lex — prawo jest prawem. Imperium szanuje granice każdej prowincji (giełdy).*

---

## 🟡 MEXC — co musimy sprawdzić

> ⚠️ Poniższe wartości **NIE są założone z góry**. Każdą pozycję należy zweryfikować na **oficjalnej dokumentacji MEXC** (stan na 2026), bo limity, fees i zasady się zmieniają.

| 🔍 Obszar | Co sprawdzić | Status |
|-----------|--------------|--------|
| ⏱️ API rate limits | Ile zapytań na sekundę / na minutę (REST + WebSocket) | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 📏 Position limits | Maksymalna wielkość pozycji (per symbol / per konto) | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 🧾 Dozwolone typy zleceń | market, limit, stop, OCO | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 📈 Futures / dźwignia | Max leverage, zasady margin, funding | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 🤖 Boty / API trading | Dozwolone (TAK na MEXC), ale sprawdzić warunki użycia | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 🔁 Wash trading | **ZABRONIONY** — potwierdzić zapis w regulaminie | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 🪞 Self-trading | Sprawdzić zasady (czy i kiedy dozwolone) | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |
| 💰 Fees | Stawki maker / taker (z uwzględnieniem zniżek) | 🔴 DO WERYFIKACJI na oficjalnej dokumentacji MEXC |

> 🏛️ *Zanim wyślemy pierwsze zlecenie — kwestor (compliance) musi odhaczyć każdy wiersz tej tabeli na zielono.*

---

## 🚫 CZEGO NIGDY NIE ROBIMY (Prohibited — co MY nigdy nie robimy)

| ❌ Praktyka | Dlaczego zabroniona |
|-------------|---------------------|
| 🔁 **Wash trading** (handel sam ze sobą dla fałszywego wolumenu) | Nielegalne, manipulacja rynkiem |
| 🎭 **Spoofing** (fałszywe zlecenia bez zamiaru realizacji) | Nielegalne, oszustwo księgi zleceń |
| 🎈 **Pump & Dump** (sztuczne napompowanie ceny) | Nielegalne, manipulacja ceny |
| 🏃 **Front-running** (wyprzedzanie cudzych zleceń) | Nieetyczne / nielegalne |
| 📚 **Layering** (warstwy fałszywych zleceń) | Manipulacja księgą zleceń |
| 💥 **Przekraczanie rate limits** (atak na API) | Łamanie regulaminu → ban konta |

> ⚔️ *Imperium walczy honorowo. Brudne triki to broń słabych — i droga do bana.*

---

## 🛡️ MANIPULACJE PRZECIW NAM (do rozpoznania i odfiltrowania)

> Te techniki stosują **inni** (konkurencja, market makerzy). Musimy je znać, by **nie dać się oszukać**.

| 🎯 Manipulacja | 👁️ Jak wygląda | 🔬 Jak wykrywamy | 🛡️ Obrona |
|----------------|----------------|------------------|-----------|
| 🪤 **Stop Hunt** (polowanie na stop-lossy) | Nagłe wybicie do poziomów stop-loss, potem powrót | Knot świecy + szybki powrót + niskie zamknięcie | Szersze stopy, ATR-based, nie okrągłe poziomy |
| 🧱 **Fake Walls** (fałszywe ściany w księdze) | Duże zlecenia, które znikają przed realizacją | Zlecenie pojawia się/znika bez realizacji | Nie ufać samej głębokości księgi |
| 🎈 **Pump & Dump** | Nagły wzrost wolumenu + ceny na małym coinie | RVOL ekstremalne + brak fundamentów | Unikać low-cap pump |
| 🔁 **Wash Trading** (fałszywy wolumen) | Wolumen nie zgadza się z ruchem ceny | Wolumen wysoki, cena stoi w miejscu | Weryfikacja CVD, real volume |
| 🎭 **Spoofing** | Duże zlecenia znikające w mgnieniu oka | Order book flickering | Order flow analysis |
| 📊 **Bart Pattern** (manipulacja na niskiej płynności) | Kształt litery B / "Bart Simpson" | Gwałtowny ruch + flat + powrót | Ostrożność w nocy/weekend (niska płynność) |
| 🌊 **Liquidation Cascade engineering** | Market maker pcha cenę do klastrów likwidacji | Liquidation Heatmap + nagłe ruchy do klastrów | Unikać wysokiej dźwigni blisko klastrów |

> 🏛️ *Caesar znał każdą sztuczkę wroga, zanim ten ją zastosował. My też.*

---

## 🧹 FILTR ANTY-MANIPULACYJNY (w Legionach, przed Senatem)

Każdy sygnał przechodzi przez **filtr odszumiania**, zanim trafi do decyzji:

1. 🧽 **Odszumianie** — każdy sygnał przechodzi przez filtr odszumiania.
2. 📦 **Wolumen potwierdza ruch?** — sprawdzenie real vs fake volume (CVD, RVOL).
3. 🪤 **Czy to stop-hunt?** — analiza knota + szybkiego powrotu.
4. ⏳ **Weryfikacja wielointerwałowa** — manipulacja często widoczna tylko na jednym TF; sprawdzamy kilka.
5. ✅ **Czysty sygnał → Senat** — dopiero zweryfikowany, czysty sygnał idzie do Senatu.

```
🛰️ Sygnał surowy
      │
      ▼
🧹 FILTR ANTY-MANIPULACYJNY (Legiony)
   ├─ real vs fake volume
   ├─ detekcja stop-hunt
   └─ multi-timeframe check
      │
      ▼
🏛️ SENAT (decyzja) ──► tylko czyste sygnały
```

> *Legiony oczyszczają pole bitwy z mgły wojennej, zanim Senat podejmie decyzję.*

---

## 🗺️ EKSPANSJA — multi-exchange (przyszłość)

| 🚢 Zasada ekspansji | Opis |
|---------------------|------|
| 📖 **Nowa giełda = nowy regulamin** | Każda nowa giełda = nowy regulamin do przeczytania od zera. |
| 🏴‍☠️ **Arbitraż (Abordaż)** | Musi być zgodny z zasadami **OBU** giełd jednocześnie. |
| 💸 **Uwaga na fees** | Różnice w fees potrafią zjeść cały zysk z arbitrażu — liczymy netto. |

**Lista giełd do rozważenia:**
- 🥇 **MEXC** (główna, konto zweryfikowane)
- ➕ Inne giełdy, gdzie user posiada konta — do dodania po weryfikacji regulaminu.

> *Każda podbita prowincja ma własne prawo. Imperium uczy się go, zanim zacznie nią rządzić.*

---

## 🥇 ZASADA ZŁOTA

> ## 💎 *"Lepiej nie wejść w trade niż złamać zasady lub dać się oszukać. Ochrona kapitału i reputacji ponad wszystko."*

🏛️ **SPQR — Senatus Populusque Romanus** ⚔️
