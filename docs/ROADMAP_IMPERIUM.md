# 🏛️ ROADMAP IMPERIUM — MAPA DRÓG SYSTEMU

**Dokument:** Plan rozwoju systemu IMPERIUM — AI crypto trading z motywem Cesarstwa Rzymskiego
**Aktualna faza:** FAZA 1 — Namiestnik (Regime + Timeframe-Aware Gating)
**Data:** 2026-06-09
**Wersja:** v0.9.0

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
- **Obliczenia ciężkie:** przez API, nie lokalnie (Fujitsu, 8GB RAM)

---

## ⚡ FAZA 1 — Namiestnik *(TERAZ — aktualna)*

**Status:** 🔄 W trakcie
**Cel:** Regime + Timeframe-Aware Gating Network — 55 neuronów, 558 testów, master-switch Reżimu Faza 1

### Stan Fazy 1 (2026-06-09)

| Kamień milowy | Status |
|---------------|--------|
| 55 neuronów w kodzie (48 aktywnych) | ✅ DONE |
| 558 testów automatycznych (0 zależności) | ✅ DONE |
| Namiestnik (Regime×Timeframe Gating) | ✅ DONE |
| Master-switch reżimu Faza 1 | ✅ DONE |
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
- **Cel łączny:** 79+ neuronów (jak system DNSS) — 55 z 79 zaimplementowane

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

**Aktualna wersja: v0.9.0** (55 neuronów, 558 testów, Namiestnik Faza 1)

---

## 🏟️ ZASADA ARENY — Koloseum

> *Żadna strategia nie wychodzi z Koloseum bez krwi na rękach.*

Przed wejściem na żywy rynek każdy moduł musi przejść przez kolejne etapy w tej dokładnej kolejności:

### Etap I — Backtest historyczny

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

*Dokument żywy — aktualizowany wraz z postępem systemu IMPERIUM.*
*"Alea iacta est." — kości zostały rzucone.*
