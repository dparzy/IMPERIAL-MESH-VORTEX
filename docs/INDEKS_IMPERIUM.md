# 👑 IMPERIUM — MASTER INDEX

```
██╗███╗   ███╗██████╗ ███████╗██████╗ ██╗██╗   ██╗███╗   ███╗
██║████╗ ████║██╔══██╗██╔════╝██╔══██╗██║██║   ██║████╗ ████║
██║██╔████╔██║██████╔╝█████╗  ██████╔╝██║██║   ██║██╔████╔██║
██║██║╚██╔╝██║██╔═══╝ ██╔══╝  ██╔══██╗██║██║   ██║██║╚██╔╝██║
██║██║ ╚═╝ ██║██║     ███████╗██║  ██║██║╚██████╔╝██║ ╚═╝ ██║
╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
```

> **"Non numeris, sed intelligentia vincimus."**
> *(Nie liczbami, lecz inteligencją zwyciężamy.)*

---

| Właściwość       | Wartość                          |
|------------------|----------------------------------|
| **Projekt**      | IMPERIUM — AI Crypto Trading     |
| **Motto**        | Roma non est facta die una       |
| **Wersja**       | v0.1.0                           |
| **Faza**         | 🟡 Faza 0 — Paper Trading        |
| **Data**         | 2026-06-01                       |
| **Giełda główna**| MEXC (konto zweryfikowane)       |
| **Rdzeń AI**     | DeepSeek LLM via API             |

> 📝 **ŻYWY DOKUMENT** — aktualizowany po każdej sesji pracy. Jeśli coś się zmienia w projekcie, ten plik zmienia się pierwszy.

---

## 🗺️ MAPA DOKUMENTÓW

Wszystkie dokumenty projektu w jednym miejscu. Punkt wejścia dla każdego, kto chce zrozumieć IMPERIUM.

| # | Plik | Opis | Status |
|---|------|------|--------|
| 1 | `INDEKS_IMPERIUM.md` | **Ten plik.** Master Index — nawigacja po całym projekcie | ✅ Aktywny |
| 2 | `ARCHITEKTURA_IMPERIUM.md` | Pełna mapa architektury systemu — warstwy, moduły, przepływ | ✅ Aktywny |
| 3 | `MAPA_IMPERIUM_FLOW.md` | Przepływ sygnału krok po kroku — od danych do zlecenia | ✅ Aktywny |
| 4 | `LEGIONY_ARCHITEKTURA.md` | 4 Legiony + mikro-neurony + schemat sygnałów | ✅ Aktywny |
| 5 | `ARSENAL_WSKAZNIKOW.md` | 157 wskaźników przypisanych do Legionów | ✅ Aktywny |
| 6 | `ARSENAL_IMPERIUM.md` | Katalog ~320 narzędzi (realne / niepewne / halucynacje) | ✅ Aktywny |
| 7 | `ARSENAL_AMERYKI.md` | 690 linków z 50+ krajów — globalna mapa zasobów | ✅ Aktywny |
| 8 | `PLAN_DEEPSEEK.md` | Plan integracji DeepSeek API — klucz, testy, prompt | ✅ Aktywny |
| 9 | `WZORZEC_DNSS.md` | Wzorzec DNSS (rój 79 agentów, Calculator Pattern) | ✅ Aktywny |
| 10 | `AUDYT_ADOPCJI.md` | 17 modułów migrowanych z Kingdom Pixel — audyt adopcji | ✅ Aktywny |
| 11 | `SYMBIOZA_MODULOW.md` | Interakcje modułów i mapowanie narzędzi | 🔗 Link |
| 12 | `ROADMAP_IMPERIUM.md` | Roadmapa rozwoju i wersjonowanie | 🔗 Link |

---

## 🏛️ MAPA KODU

Struktura katalogów projektu — co gdzie mieszka i w jakim stanie.

| Katalog | Rola w Imperium | Moduł | Status |
|---------|-----------------|-------|--------|
| `imperium/akwedukty/` | Rurociąg danych — pobieranie świec z MEXC przez CCXT | Akwedukty (Data Pipeline) | ✅ Gotowy |
| `imperium/fundament/` | Brama Kalkulatora — TA-Lib oblicza wskaźniki, SHA-256 podpisuje | Calculator Gate | ✅ Gotowy |
| `imperium/legiony/` | Legiony Zwiadowcze — generatory sygnałów (4 legiony + mikro-neurony) | Scout Legions | 🟡 Szkielet |
| `imperium/pretorianie/` | Pretorianie — weto ryzyka, ochrona kapitału | Risk Praetorians | ✅ Gotowy |
| `imperium/senat/` | Senat — debata Popularów vs Optymantów nad sygnałem | Senate Debate | 🟡 Szkielet |
| `imperium/cesarz/` | Cesarz — DeepSeek LLM podejmuje ostateczną decyzję | Emperor (LLM) | 🟡 Szkielet |
| `imperium/drogi/` | Drogi — wykonanie zlecenia na MEXC (Via Romana) | Order Execution | 🟡 Szkielet |
| `imperium/biblioteki/` | Biblioteki — logi, pamięć, historia transakcji | Logs & Memory | ✅ Gotowy |
| `imperium/swiatynie/` | Świątynie — wykresy, dashboard, wizualizacje | Charts & Dashboard | 🟡 Szkielet |
| `imperium/koloseum/` | Koloseum — arena backtestów, testowanie strategii | Backtesting Arena | 🟡 Szkielet |
| `imperium/oczy/` | Oczy — newsy, sentyment, dane on-chain | News & Sentiment | 🔴 Planowany |

**Legenda:** ✅ Gotowy — działa produkcyjnie | 🟡 Szkielet — struktura istnieje, wypełnianie w toku | 🔴 Planowany — jeszcze nie rozpoczęty

---

## ⚖️ PRAWA IMPERIUM

Nienaruszalne zasady. Złamanie któregokolwiek Prawa = błąd architektoniczny.

**Prawo I — Lex Calculi**
> AI nie oblicza. Bramka oblicza (TA-Lib). AI interpretuje wyłącznie zweryfikowane liczby.

**Prawo II — Lex Unitatis**
> Jeden punkt wejścia dla danych. Jeden punkt wejścia dla LLM. Brak równoległych kanałów.

**Prawo III — Lex Sigilli**
> Każdy sygnał niesie dowód SHA-256 z Bramki. Sygnał bez pieczęci = sygnał odrzucony.

**Prawo IV — Lex Veto**
> Pretorianie mają WETO. Żadna pozycja bez ich zgody. Nawet Cesarz im nie rozkazuje.

**Prawo V — Lex Arcani**
> Klucze API NIGDY w kodzie. Wyłącznie zmienne środowiskowe. Zawsze.

**Prawo VI — Lex Kolossei**
> Każde nowe narzędzie testowane w Koloseum jako pierwsze. Nigdy prosto na live.

**Prawo VII — Lex Gradus**
> Budujemy stopniowo. Jeden neuron na raz. Pośpiech = chaos = straty.

**Prawo VIII — Lex Diversitatis**
> Bez zbędnego powielania. Każdy moduł pokrywa INNY kąt widzenia rynku.

**Prawo IX — Lex Memoriae**
> Nic nie ginie. Każda wiedza trafia do `docs/`. Dokumentacja jest częścią kodu.

---

## 🏺 GIEŁDY

| Giełda | Rola | Status konta | Faza |
|--------|------|--------------|------|
| **MEXC** | Giełda główna — wykonanie zleceń, pobieranie danych | ✅ Konto zweryfikowane | Faza 0+ |
| Inne (TBD) | Ekspansja — arbitraż między giełdami | 🔴 Planowane | Faza 2+ |

---

## ⚔️ LEGIONY

Cztery Legiony Zwiadowcze — każdy widzi rynek inaczej.

| # | Nazwa Łacińska | Styl Analizy | Timeframe | Specjalizacja |
|---|----------------|--------------|-----------|---------------|
| I | **Legio Prima — Fulminata** | Momentum & Trend | 1m–15m | Szybkie ruchy, breakouty, wolumen |
| II | **Legio Secunda — Augusta** | Mean Reversion | 1h–4h | RSI, oversold/overbought, powrót do średniej |
| III | **Legio Tertia — Gallica** | Structure & Patterns | 4h–1D | Formacje świecowe, S/R, fale Elliotta |
| IV | **Legio Quarta — Scythica** | Macro & Sentiment | 1D–1W | Trendy makro, on-chain, cykl rynkowy |

> Szczegóły mikro-neuronów i schematu sygnałów → `LEGIONY_ARCHITEKTURA.md`

---

## 🗺️ NASTĘPNE KROKI

Priorytety w kolejności. Jedno zadanie na raz (Prawo VII).

| # | Zadanie | Moduł | Priorytet |
|---|---------|-------|-----------|
| 1 | ⚡ Ustaw `DEEPSEEK_API_KEY` w zmiennych środowiskowych | Cesarz | 🔴 Krytyczny |
| 2 | 🧪 Uruchom `python imperium/cesarz/deepseek_glos.py` — test połączenia | Cesarz | 🔴 Krytyczny |
| 3 | 🔄 Uruchom pełny cykl Fazy 0 na realnych danych (paper trading) | Cały system | 🟠 Wysoki |
| 4 | 🖥️ Zainstaluj TA-Lib na Windows 10 (Fujitsu 8GB RAM) | Fundament | 🟠 Wysoki |
| 5 | 🧬 Rozbuduj mikro-neurony do 79+ agentów | Legiony | 🟡 Średni |
| 6 | 🏟️ Zbuduj Koloseum — arena backtestów z historycznych danych | Koloseum | 🟡 Średni |

---

## 📡 SZYBKA DIAGNOSTYKA

```bash
# Sprawdź czy klucz DeepSeek jest ustawiony
echo $DEEPSEEK_API_KEY

# Test połączenia z DeepSeek
python imperium/cesarz/deepseek_glos.py

# Test pobierania danych z MEXC
python imperium/akwedukty/mexc_feed.py

# Test Bramki Kalkulatora
python imperium/fundament/calculator_gate.py

# Status pretorianów
python imperium/pretorianie/veto_check.py
```

---

## 📜 HISTORIA WERSJI

| Wersja | Data | Zmiana |
|--------|------|--------|
| v0.1.0 | 2026-06-01 | Inicjalizacja INDEKS_IMPERIUM — Master Index stworzony |

---

*Roma non est facta die una. Imperium buduje się neuron po neuronie.*

*— INDEKS_IMPERIUM.md | Aktualizowany z każdą sesją | Faza 0 — Paper Trading*
