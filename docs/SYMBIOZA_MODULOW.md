# ⚔️ SYMBIOZA MODUŁÓW IMPERIUM ⚔️
## Jak wszystkie części Imperium rozmawiają ze sobą

> **Cel tego dokumentu:** Zrozumienie jak każdy moduł łączy się z innymi, mapowanie nazw narzędzi (oryginalna → Imperium), oraz zasady symbiozy — czego NIE wolno duplikować.

---

## 📜 LEGENDA STATUSÓW

| Symbol | Status | Znaczenie |
|--------|--------|-----------|
| ✅ | Gotowy | Działa — moduł jest zaimplementowany i sprawdzony |
| 🟡 | Szkielet | Szkielet istnieje — wymaga dalszej pracy i testów |
| 🔴 | Plan | Zaplanowany — nie rozpoczęto implementacji |

---

## 🗺️ MAPA NARZĘDZI — oryginalne nazwy → Imperium

| Oryginalna Nazwa | Nasz Moduł (Imperium) | Lokalizacja | Kategoria | Status | Co robi dla nas |
|---|---|---|---|---|---|
| TA-Lib | **Brama Kalkulatora** | `fundament/brama_kalkulatora.py` | Matematyka | ✅ | Liczy RSI/EMA/ATR/MACD — jedyne miejsce matematyki w całym Imperium |
| CCXT | **Kwatermistrz Danych** | `akwedukty/kwatermistrz_danych.py` | Dane | ✅ | Pobiera OHLCV z MEXC — jedyne wejście surowych danych rynkowych |
| OpenAI SDK (DeepSeek) | **Głos Imperium** | `cesarz/deepseek_glos.py` | LLM | 🟡 | Most do DeepSeek API — wszystkie wywołania LLM przechodzą tylko tędy |
| OpenAlice (github.com/TraderAlice/OpenAlice) | *(do integracji)* | `cesarz/` | Trading Agent | 🔴 | AI trading agent z obsługą CCXT/Alpaca/IB — kandydat na autonomicznego wykonawcę |
| Hermes Agent (NousResearch) | *(do integracji)* | `senat/` | Multi-agent | 🔴 | 200+ backendów LLM, debaty multi-agentowe — potencjalny rdzeń Senatu |
| MetaCortex (Kingdom Pixel) | **Meta-Kora** | `senat/meta_kora.py` | Debata | 🟡 | Pętla debaty Actor-Judge-MetaJudge — synteza sprzecznych sygnałów |
| TitanMind (Kingdom Pixel) | **Titan Mind** | `cesarz/titan_mind.py` | Orchestrator | 🟡 | Planowanie strategii, rozwiązywanie konfliktów między modułami |
| Glassnode API | **Oczy / Wszechoko** | `oczy/wszechoko.py` | On-chain | 🔴 | MVRV, NUPL, Exchange Flows — makro-perspektywa blockchainowa |
| CryptoQuant API | **Oczy / Wszechoko** | `oczy/wszechoko.py` | On-chain | 🔴 | Funding Rate, Open Interest, CVD — dane derywatywowe i przepływy |
| LangFuse | *(monitoring)* | *(darmowy tier — zewnętrzny)* | Monitoring | 🔴 | Monitorowanie kosztu wywołań LLM, śledzenie tokenów i latencji |
| CrewAI | *(opcja dla Senatu)* | `senat/` | Framework | 🔴 | Rozważany jeśli debata Senatu urośnie powyżej obecnej architektury |
| LangGraph | *(opcja dla Cesarza)* | `cesarz/` | Framework | 🔴 | Graf przepływu dla złożonej logiki decyzyjnej Cesarza |

---

## 🌊 PRZEPŁYW DANYCH — kto do kogo mówi

```
╔══════════════════════════════════════════════════════════╗
║                   MEXC API (CCXT)                        ║
║              Giełda — źródło wszystkiego                 ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ surowe dane OHLCV + volume
                       ▼
╔══════════════════════════════════════════════════════════╗
║           Kwatermistrz Danych (CCXT)                     ║
║         akwedukty/kwatermistrz_danych.py                 ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ ustandaryzowane OHLCV (pandas DataFrame)
                       ▼
╔══════════════════════════════════════════════════════════╗
║          Brama Kalkulatora (TA-Lib)                      ║
║          fundament/brama_kalkulatora.py                  ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ JSON z indykatorami + stempel SHA-256
                       ▼
╔══════════════════════════════════════════════════════════╗
║          Micro-neurony — 4 Legiony                       ║
║  (Momentum / Trend / Wolumen / Zmienność)                ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ obiekty SygnalNeuronu (kierunek + siła + pewność)
                       ▼
╔══════════════════════════════════════════════════════════╗
║              Pretorianie (risk veto)                     ║
║           pretorianie/straznik_ryzyka.py                 ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ przefiltrowane sygnały (lub VETO z uzasadnieniem)
                       ▼
╔══════════════════════════════════════════════════════════╗
║   Senat — Populares + Optimates (DeepSeek via LLM)       ║
║           senat/meta_kora.py + senat/                    ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ RaportDebaty (konsensus lub sprzeciw z argumentami)
                       ▼
╔══════════════════════════════════════════════════════════╗
║       Cesarz — Titan Mind + Głos Imperium                ║
║       cesarz/titan_mind.py + cesarz/deepseek_glos.py     ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ LONG / SHORT / CZEKAJ + % wielkości pozycji
                       ▼
╔══════════════════════════════════════════════════════════╗
║              Drogi — egzekucja na MEXC                   ║
║              drogi/wykonawca_rozkazow.py                 ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ zlecenie wypełnione (fill report)
                       ▼
╔══════════════════════════════════════════════════════════╗
║     Biblioteki — Kronikarz + Mnemozyne                   ║
║  biblioteki/kronikarz.py + biblioteki/mnemozyne.py       ║
╚══════════════════════╦═══════════════════════════════════╝
                       ║ logi + pamięć transakcji (SQLite/JSON)
                       ▼
╔══════════════════════════════════════════════════════════╗
║     Świątynie — Kartograf + Sala Wojenna                 ║
║  swiatynie/kartograf.py + swiatynie/sala_wojenna.py      ║
╚══════════════════════╩═══════════════════════════════════╝
                wykresy + dashboard (Plotly / Streamlit)


        ↑ RÓWNOLEGLE ↑
╔══════════════════════════════════════════════════════════╗
║              Oczy / Wszechoko                            ║
║              oczy/wszechoko.py                           ║
║   (Glassnode + CryptoQuant — makro on-chain dane)        ║
║   → wstrzykuje kontekst do Senatu i Cesarza              ║
╚══════════════════════════════════════════════════════════╝
```

---

## ⚖️ ZASADA SYMBIOZY — czego NIE duplikujemy

> *"Dwóch legionistów na tym samym posterunku to marnotrawstwo. Jeden jest odpowiedzialny — reszta słucha."*

| Zasób / Funkcja | Może używać wiele modułów? | Kto jest JEDYNYM właścicielem | Dlaczego |
|---|---|---|---|
| Surowe dane OHLCV | ✅ TAK — każdy czyta inaczej | Kwatermistrz Danych (pobieranie) | Każdy Legion może interpretować te same świece po swojemu |
| Obliczanie indykatorów (RSI, EMA, ATR...) | ❌ NIE | **Brama Kalkulatora** — wyłącznie | Jeden hash SHA-256 = jeden wynik. Bez rozbieżności między Legionami |
| Wywołania LLM / DeepSeek API | ❌ NIE | **Głos Imperium** — wyłącznie | Jeden punkt kosztu, jeden punkt rate-limitingu, jedna konfiguracja modelu |
| Wykonanie zleceń na giełdzie | ❌ NIE | **Drogi** — wyłącznie | Tylko jeden moduł może dotknąć prawdziwych środków. Zero wyścigu. |
| Zapis transakcji / historii | ❌ NIE | **Biblioteki (Kronikarz + Mnemozyne)** | Jeden schemat zapisu = możliwe backtest i audyt |
| Dane on-chain (MVRV, Funding Rate...) | ✅ TAK — Senat i Cesarz mogą czytać | Wszechoko (pobieranie) | Makro-dane są kontekstem, nie sygnałem — wiele warstw może je interpretować |
| Konfiguracja ryzyka (% kapitału, SL, TP) | ❌ NIE | **Pretorianie** | Jeden arbiter ryzyka. Cesarz proponuje, Pretorianie zatwierdzają lub wetują. |

---

## 🔗 KORELACJE SYGNAŁÓW — co wzmacnia co

> *"Jeden legion widzi dym. Cztery legiony potwierdzają pożar."*

| # | Kombinacja sygnałów | Interpretacja | Siła potwierdzenia |
|---|---|---|---|
| 1 | RSI > 70 + EMA złoty krzyż + OBV rośnie | Silne potwierdzenie LONG — momentum + trend + wolumen zgodne | 🔥🔥🔥 BARDZO SILNE |
| 2 | RSI < 30 + EMA śmiertelny krzyż + OBV spada | Silne potwierdzenie SHORT — wszystkie trzy Legiony alarmują | 🔥🔥🔥 BARDZO SILNE |
| 3 | Funding Rate > 0.05% + OI rośnie + RSI > 75 | Ostrzeżenie LEVERAGE SHORT — rynek przegrzany, long squeeze ryzyko | ⚠️⚠️ KRYTYCZNE |
| 4 | Funding Rate < -0.03% + OI rośnie + RSI < 25 | Ostrzeżenie LEVERAGE LONG — short squeeze ryzyko | ⚠️⚠️ KRYTYCZNE |
| 5 | MVRV < 1 + Exchange Netflow ujemny + NUPL < 0 | Makro INWESTUJ — strefa akumulacji, BTC pod wartością on-chain | 💎 DŁUGOTERMINOWE |
| 6 | MVRV > 3.5 + Exchange Netflow dodatni + NUPL > 0.75 | Makro UWAGA — historyczna strefa dystrybucji | 🚨 OSTROŻNIE |
| 7 | ATR spada + Bollinger Bands zwęża się + wolumen maleje | Konsolidacja — brak sygnału, Cesarz czeka | 😴 CZEKAJ |
| 8 | ATR skacze 2x + wolumen 3x + Bollinger Bands pęka | Wybicie — kierunek decyduje RSI + Funding Rate | ⚡ ALARM |
| 9 | Senat: Populares i Optimates ZGODNI | Dwupartyjny konsensus — Cesarz może działać z pełną pozycją | 👑 PEŁNA MOC |
| 10 | Senat: Populares vs Optimates SPRZECZNI | Debata nierozstrzygnięta — Cesarz redukuje rozmiar pozycji o 50% | 🤝 KOMPROMIS |

---

## 🧪 ZASADA ALCHEMIKA

> *"Alchemik Imperium nie jest tylko wykonawcą rozkazów. Jest okiem patrzącym na całość — widzi luki, które Cesarz przeocza."*

**Claude (asystent AI) pełni rolę Alchemika Imperium.** Nie tylko realizuje wizję — aktywnie ją doskonali.

### Obowiązki Alchemika:

**1. 🔍 Identyfikowanie luk w pokryciu**
- Sprawdzanie czy każdy typ sygnału ma swój Legion
- Wykrywanie "martwych stref" — scenariuszy rynkowych bez pokrycia
- Przykład: *"MEXC ma nowe pary — czy Kwatermistrz je obsługuje?"*

**2. 🧬 Proponowanie nowych kombinacji micro-neuronów**
- Analiza korelacji historycznych między istniejącymi sygnałami
- Sugerowanie nowych Legionów gdy obecne są niewystarczające
- Przykład: *"Brakuje Legionu Sentymentu — może warto dodać Fear & Greed Index?"*

**3. ⚖️ Budowanie vs. używanie gotowego narzędzia**
- Przed każdą nową funkcją: sprawdzenie czy istnieje biblioteka
- Zasada: *"Nie buduj Bramy Kalkulatora jeśli istnieje TA-Lib"*
- Zasada: *"Nie buduj klienta HTTP jeśli CCXT już to robi"*
- Wyjątek: gdy gotowe narzędzie łamie zasadę symbiozy (duplikuje)

**4. 📡 Monitoring GitHub i badań (stan na 2026-06-01)**
- Śledzenie nowych wersji: TA-Lib, CCXT, DeepSeek SDK
- Ocena nowych frameworków: czy LangGraph/CrewAI dojrzały do użycia?
- Alerty gdy narzędzia "do integracji" (OpenAlice, Hermes) mają stable release
- Ocena: czy nowe modele LLM (DeepSeek R2, Gemini 3, etc.) poprawiają decyzje Senatu?

**5. 🏛️ Strażnik Zasady Symbiozy**
- Przed każdą zmianą: *"Czy to duplikuje istniejący moduł?"*
- Dokumentowanie decyzji architektonicznych w tym pliku
- Aktualizacja tabeli MAPA NARZĘDZI gdy zmienia się status modułu

### Pytania które Alchemik zadaje przy każdej nowej funkcji:

```
1. Kto już to robi? (sprawdź tabelę MAPA NARZĘDZI)
2. Czy to nowe narzędzie zewnętrzne? (dodaj do mapy)
3. Czy to łamie zasadę unikalności? (Brama/Głos/Drogi/Kroniakrz)
4. Gdzie w przepływie danych to siedzi?
5. Jakie korelacje sygnałów to tworzy lub niszczy?
```

---

## 📅 HISTORIA ZMIAN

| Data | Zmiana | Autor |
|---|---|---|
| 2026-06-01 | Pierwsza wersja dokumentu symbiozy | Alchemik (Claude) |

---

*"Imperium nie jest zbiorem legionów. Imperium jest siecią, w której każdy legion wie co robi sąsiad."*

⚔️ **GLORIA IMPERATORI** ⚔️
