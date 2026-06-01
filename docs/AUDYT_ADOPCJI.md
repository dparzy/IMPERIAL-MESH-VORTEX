# 🔍 AUDYT ADOPCJI — Kingdom Pixel → Imperium

> **Po co:** Pełny, uczciwy zapis adopcji 17 modułów kodu z projektu Kingdom Pixel
> do Imperium. Zgodnie z Prawem I (Zero halucynacji) — mówimy też o tym, co jest słabe.
> **Zasada porządkowa:** adoptujemy KOD, **nie adoptujemy ZASAD** (Imperium ma własne 19 praw).
> **Stan kodu:** wszystkie 17 modułów kompiluje się czysto (`py_compile`, 0 błędów).

---

## 1. 📋 Mapowanie modułów

| Oryginał (Kingdom Pixel) | Moduł w Imperium | Folder | Rola | Prawa |
|--------------------------|------------------|--------|------|-------|
| CORE-006 CalculatorGateway | `brama_kalkulatora.py` | fundament | Jedyne wejście do matematyki | I, IX, XIII |
| TOOLS-208 ToolForge | `kuznia_narzedzi.py` | fundament | Kanoniczne, deterministyczne wskaźniki | I |
| ORCH-209 TitanMind | `titan_mind.py` | cesarz | Orkiestrator + harmonogram strategii | III, XIV |
| BRAIN-026 MetaCortex | `meta_kora.py` | senat | Debata agentów (Aktor–Sędzia–MetaSędzia) | IX, XIII |
| STRAT-001 PaperBot RSI+EMA | `pierwszy_zwiadowca.py` | legiony | Pierwszy bot, pełny cykl Fazy 0 | IV, VI |
| NEURON-001 RojSygnalow | `roj_sygnalow.py` | legiony | Rój sygnałów, wejście przy konsensusie | X, IX |
| SHIELDS-205 AegisShield | `aegis_tarcza.py` | pretorianie | Wielowarstwowy silnik ryzyka, circuit breaker | IX |
| BRAIN-073 LustroPrawdy | `lustro_prawdy.py` | pretorianie | Walidacja kontradyktoryjna sygnałów | I, IX |
| DATA-001 DataLoader | `kwatermistrz_danych.py` | akwedukty | Realne dane OHLCV (CCXT) + import CSV | II |
| EYES-028 OmniSight | `wszechoko.py` | oczy | Percepcja: on-chain + orderbook (Bayesian fusion) | XII |
| CORE-005 NexGenHub | `nexus_hub.py` | drogi | Multi-exchange core, routing z audytem | III, XIII |
| HANDS-204 WarLancer | `war_lancer.py` | drogi | Silnik egzekucji wysokiej częstotliwości | III |
| VIZ-001 Kartograf | `kartograf.py` | swiatynie | Wykresy biegów (PNG) — oczy Komendanta | V |
| DASH-207 WarRoom | `sala_wojenna.py` | swiatynie | Dashboard / centrum dowodzenia | V |
| MEM-206 Mnemosyne | `mnemosyne.py` | biblioteki | Pamięć trwała + uczenie z transakcji | VIII, XIII |
| LOG-001 Kronikarz | `kronikarz.py` | biblioteki | Logi + dziennik postępu (raport po biegu) | XIII |
| BACK-210 Valhalla | `valhalla.py` | koloseum | Arena testów: backtest, Monte Carlo, walk-forward | VI, VII |

---

## 2. 🗺️ Mapowanie starych Zasad → Prawa Imperium

Wewnątrz modułów są odwołania do "Zasad" Kingdom Pixel. **Nie adoptujemy ich jako zasad** —
ale dla czytelności kodu oto tłumaczenie najczęstszych:

| Stara Zasada (Kingdom Pixel) | Prawo Imperium | Treść |
|------------------------------|----------------|-------|
| Zasada 75 (Brama Kalkulatora) | **Prawo I** | Kod liczy, AI interpretuje |
| Zasada 23 (Data Lineage) | **Prawo XIII** | Każda decyzja audytowalna |
| Zasada 11 (Metryczka) | — | Konwencja dokumentacyjna (zostaje jako styl) |
| Zasada 76 (Dedup) | **Prawo V** | Mniej, ale prawdziwie |
| Zasada 2 (Prawda) | **Prawo I** | Zero halucynacji |
| Zasada 70 (Kontrolowany postęp) | **Prawo VII** | Stopniowo, jedna rzecz na raz |

> Nagłówki modułów przepiszemy na prawa Imperium **moduł po module**, gdy będziemy
> nad każdym realnie pracować (Prawo VII). Brama Kalkulatora — już przepisana w 100%.

---

## 3. ⚠️ Stan realny i ostrzeżenia (Prawo I)

Z wewnętrznego audytu Kingdom Pixel (autor: Jack, 31.05.2026) — przenoszę uczciwie:

- 🟢 **Brama Kalkulatora** — w pełni zaadaptowana, egzekwuje Prawo I w kodzie (bez TA-Lib nie startuje).
- 🔴 **`pierwszy_zwiadowca` (STRAT-001)** — **NIE jest "zwalidowaną strategią"**:
  - wyniki na danych **syntetycznych** (brak realnych CSV),
  - brak modelowania **poślizgu (slippage)** i spreadu,
  - dzika rozrzutność wyników (od −94% do +9026%) = sygnał **kruchości**, nie przewagi.
  - **Etykieta:** *wstępny paper-test na danych dziennych, wymaga walidacji out-of-sample + koszty.*
- 🟠 **Pozostałe moduły** — kompilują się, ale działanie logiki **NIEZWERYFIKOWANE** na realnych
  danych (brak biblioteki C TA-Lib, danych i sieci w środowisku audytu). Kompilacja ≠ poprawność.
- 🟢 **Metoda jest zdrowa** — kod realnie istnieje, Brama egzekwuje dyscyplinę, audyty są bezlitosne wobec siebie.

---

## 4. ✅ Co dało się zrobić, czego nie

**Zrobione:**
- 17 modułów skopiowanych do struktury Imperium (10 folderów wg metafory).
- Wszystkie kompilują się czysto.
- Kingdom Pixel **nietknięty** jako backup (Prawo VIII — nic nie ginie).
- Zasady Kingdom Pixel **świadomie pominięte** (Imperium ma własne 19 praw).

**Do zrobienia (kolejka, Prawo VII):**
1. Przepisać nagłówki modułów na prawa Imperium (po jednym).
2. Wgrać realne dane (CSV) i dodać slippage do `pierwszy_zwiadowca`.
3. Zweryfikować w działaniu moduły poza Bramą (uruchomić, nie deklarować).
4. Reklasyfikować STRAT-001 z "zwalidowany" na "wstępny paper-test".

---

*PRAWDA. Adoptujemy kod, nie dogmaty. Mniej, ale prawdziwie.*
— VITRUVIUSZ, architekt Imperium
