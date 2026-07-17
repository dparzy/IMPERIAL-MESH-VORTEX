---
kategoria: ACTA
typ: acta
zastapiony_przez: docs/ARCHITEKTURA_IMPERIUM.md
wlasciciel: imperium/akwedukty/kwatermistrz_danych.py, imperium/biblioteki/kronikarz.py, imperium/biblioteki/mnemosyne.py, imperium/cesarz/titan_mind.py, imperium/drogi/nexus_hub.py, imperium/fundament/brama_kalkulatora.py, imperium/fundament/kuznia_narzedzi.py, imperium/koloseum/backtest.py, imperium/koloseum/monte_carlo.py, imperium/legiony/pierwszy_zwiadowca.py, imperium/legiony/roj_sygnalow.py, imperium/pretorianie/aegis_tarcza.py, imperium/pretorianie/lustro_prawdy.py, imperium/senat/meta_kora.py, imperium/swiatynie/kartograf.py, imperium/swiatynie/web_dashboard.py
stan_na: 2026-05-31
powod_istnienia: "Wersja narracyjna/dydaktyczna architektury — dla nowicjusza (Cezara): tłumaczy PO CO każdy organ istnieje, z przykładowym dialogiem (Zwiadowca 1 mówi 'DŁUGO...', Frakcja Byków vs N"
dlug: "🚨 opisuje nieistniejący kod: war_lancer.py, sala_wojenna.py, koloseum/valhalla.py"
---
# 🏛️ MAPA PRZEPŁYWU IMPERIUM — kto z kim, co robi, jak decyduje

> # 📜 ACTA — WIZJA ZAŁOŻYCIELSKA z 2026-05-31. NIE OPISUJE DZISIEJSZEGO IMPERIUM.
>
> **Stan faktyczny → [`ARCHITEKTURA_IMPERIUM.md`](ARCHITEKTURA_IMPERIUM.md).**
>
> Ten dokument to **prawda swojego czasu** (Prawo I: historii nie falsyfikujemy) — zapis tego,
> jak wyobrażaliśmy sobie Imperium na starcie. Zweryfikowane 2026-07-17 wobec kodu:
>
> | Twierdzi | Rzeczywistość |
> |---|---|
> | „Oczy (Wszechoko) — 🔴 Plan, do zbudowania" | `oczy/wszechoko.py` istnieje (145 linii) |
> | „Koloseum (Valhalla) — 🟡 Szkielet" | koloseum ma **16 modułów**; `valhalla.py` **nigdy nie istniał** |
> | „Senat — 🟡 Szkielet, debata do zaprojektowania" | `senat/meta_kora.py` istnieje (203 linie) |
> | „Zwiadowca 1..4" | **87 neuronów** i **15 zwiadowców** w rejestrze |
> | `drogi/war_lancer.py`, `swiatynie/sala_wojenna.py` | **nie istnieją** (realnie: `oms.py`/`real_order_router.py`, `web_dashboard.py`) |
>
> **Dlaczego zdegradowany, a nie skasowany:** to jedyny narracyjny zapis *po co* powstał każdy
> organ — wartość historyczna i dydaktyczna. Ale jako dokument **żywy** uczył Cezara systemu,
> który nie istnieje, więc był gorszy niż jego brak. Zdegradowany do ACTA 2026-07-17.
>
> **Następca dydaktyczny (KOREKTA 2026-07-17):** twierdziłem tu, że Imperium nie ma
> narracyjnego przewodnika po aktualnej architekturze. **To było moje twierdzenie bez
> weryfikacji — i było fałszywe.** Taki przewodnik istnieje:
> [`MANUAL_MIGRACJA_I_SYMULATOR.md`](MANUAL_MIGRACJA_I_SYMULATOR.md) § 2 — pełny przepływ
> cyklu decyzyjnego, 10 bramek wstrzymania z progami zweryfikowanymi wobec kodu, ścieżka
> pieniędzy. Zwięzła mapa architektury → [`ARCHITEKTURA_IMPERIUM.md`](ARCHITEKTURA_IMPERIUM.md).

> **Giełda docelowa:** MEXC (główna)
> **Instrumenty:** BTC (priorytet), ETH, alts, nowe tokeny
> **Tryb:** Paper trading → Live (po walidacji)
> **Zasada nadrzędna:** Zero duplikatów. Każdy moduł ma JEDNO zadanie. Żadna informacja nie ginie.

---

## 🗺️ MAPA STRUKTURY (kto jest kim)

```
╔══════════════════════════════════════════════════════════════╗
║                    👑 CESARZ (Decydent)                      ║
║              cesarz/titan_mind.py                            ║
║   Widzi całą debatę → decyduje: LONG / SHORT / CZEKAJ        ║
╚══════════════════╦═══════════════════════════════════════════╝
                   ║ słucha debaty
    ╔══════════════╩═══════════════════╗
    ║      🏛️ SENAT (Debata)           ║
    ║      senat/meta_kora.py          ║
    ║  Dwie frakcje walczą o rację:    ║
    ║  ⚔️  FRAKCJA BYKÓW (za LONG)     ║
    ║  ⚔️  FRAKCJA NIEDŹWIEDZI (za SHORT)║
    ║  Każda zbiera DOWODY, nie opinie ║
    ╚═══╦══════════════════════════╦══╝
        ║ sygnały                  ║ weto/filtr
        ║                   ╔══════╩═════════════╗
        ║                   ║ 🛡️ PRETORIANIE     ║
        ║                   ║ pretorianie/        ║
        ║                   ║ aegis_tarcza.py     ║
        ║                   ║ lustro_prawdy.py    ║
        ║                   ║ Strażnicy. Jeśli    ║
        ║                   ║ ryzyko za duże →    ║
        ║                   ║ WETO. Zawsze.       ║
        ║                   ╚══════════════════════╝
        ║
╔═══════╩══════════════════════════════════════╗
║          ⚔️ LEGIONY (Zwiadowcy/Boty)          ║
║          legiony/pierwszy_zwiadowca.py        ║
║          legiony/roj_sygnalow.py              ║
║                                               ║
║  To są GENERATORY SYGNAŁÓW.                  ║
║  Każdy zwiadowca specjalizuje się inaczej:   ║
║                                               ║
║  🔍 Zwiadowca 1 → trend-following (EMA/RSI)  ║
║  🔍 Zwiadowca 2 → momentum / breakout        ║
║  🔍 Zwiadowca 3 → sentyment / newsy          ║
║  🔍 Zwiadowca 4 → on-chain (wieloryby, flow) ║
║  🔍 Zwiadowca N → (dodajemy z czasem)        ║
║                                               ║
║  WAŻNE: każdy ma INNE zadanie, nie duplikują ║
╚═══════╦══════════════════════════════════════╝
        ║ pyta o wskaźniki
╔═══════╩══════════════════════════════════════╗
║       🧮 FUNDAMENT — BRAMA KALKULATORA       ║
║       fundament/brama_kalkulatora.py          ║
║       fundament/kuznia_narzedzi.py            ║
║                                               ║
║  JEDYNE miejsce gdzie liczymy matematykę.    ║
║  RSI, EMA, ATR, MACD → tu i nigdzie indziej ║
║  Prawo I: AI nie liczy. Brama liczy.         ║
║  Zwraca JSON z pieczątkę SHA-256.            ║
╚═══════╦══════════════════════════════════════╝
        ║ dostarcza dane surowe
╔═══════╩══════════════════════════════════════╗
║       🚰 AKWEDUKTY (Dane)                    ║
║       akwedukty/kwatermistrz_danych.py        ║
║                                               ║
║  Jedno wejście danych do całego systemu.     ║
║  Źródła: MEXC API (CCXT) → CSV → Syntetyczne║
║  Format wyjściowy: zawsze taki sam (OHLCV)  ║
╚══════════════════════════════════════════════╝
```

---

## 🔄 PRZEPŁYW SYGNAŁU — krok po kroku

```
1. AKWEDUKTY pobierają dane OHLCV z MEXC (BTC/ETH/alts)
        ↓
2. BRAMA KALKULATORA liczy wskaźniki (RSI, EMA, ATR...)
   → zwraca JSON: { "RSI": 67.3, "EMA_fast": 43210, ... }
        ↓
3. LEGIONY (zwiadowcy) czytają JSON i generują sygnały
   Zwiadowca 1: "DŁUGO — trend wzrostowy, RSI nie wyprzedany"
   Zwiadowca 2: "KRÓTKO — momentum spada, divergencja"
   Zwiadowca 3: "NEUTRAL — newsy mieszane"
        ↓
4. PRETORIANIE sprawdzają czy w ogóle wolno handlować
   - ATR za duże? → CZEKAJ (circuit breaker)
   - Seria strat? → PAUZA
   - Ryzyko ok? → przepuść dalej
        ↓
5. SENAT zbiera wszystkie sygnały i organizuje debatę
   FRAKCJA BYKÓW: "RSI nie przewyższony, EMA golden cross, flow wielorybów pozytywny"
   FRAKCJA NIEDŹWIEDZI: "momentum spada, funding rate wysoki, wolumen spada"
   → SENAT tworzy RAPORT DEBATY (wszyscy mówią, nikt nie milczy)
        ↓
6. CESARZ czyta pełny raport i decyduje
   → LONG / SHORT / CZEKAJ + uzasadnienie
   (Cesarz korzysta z DeepSeek API lub innego LLM)
        ↓
7. DROGI wykonują zlecenie na MEXC
   nexus_hub.py → routing → war_lancer.py → egzekucja
        ↓
8. BIBLIOTEKI zapisują wynik
   kronikarz.py → logi
   mnemosyne.py → pamięć transakcji
        ↓
9. ŚWIĄTYNIE rysują wykres
   kartograf.py → PNG
   sala_wojenna.py → dashboard (później)
        ↓
10. KOLOSEUM testuje w tle
    valhalla.py → backtest każdej nowej strategii zanim wejdzie do boju
```

---

## 🚫 ZASADA SYMBIOZA — nie duplikacja

**Zasada:** Moduł może być wielozadaniowy i skomplikowany. Ale żaden moduł nie może robić
dokładnie tego samego co inny. Moduły mają się **uzupełniać**, nie kopiować.

### ✅ Dobra redundancja (symbioza)

Przykład — śledzenie wielorybów (jeden moduł to za mało):
```
oczy/wszechoko.py
    ├── Zwiad A: top 100 walletów on-chain (ruchy BTC/ETH)
    ├── Zwiad B: CEX inflow/outflow (wpłaty na giełdy = możliwa sprzedaż)
    ├── Zwiad C: celebryci i influencerzy (Twitter/X on-chain powiązania)
    └── Zwiad D: funding rate + open interest (sentiment futures)
```
Każdy patrzy gdzie indziej. Razem dają PEŁNY OBRAZ. Nikt nie powiela.

Przykład — Senat (debata):
```
senat/meta_kora.py
    ├── Agent BYKÓW: aktywnie szuka argumentów ZA LONG
    └── Agent NIEDŹWIEDZI: aktywnie szuka argumentów ZA SHORT
```
Czytają te same dane — ale każdy filtruje pod swój kąt. Wynik: Cesarz widzi oba światy.

### ❌ Zła redundancja (duplikacja do usunięcia)

```
❌ 5 modułów sprawdza to samo konto na Twitterze
❌ 3 moduły liczą RSI z tych samych danych
❌ 2 moduły wysyłają ten sam alert do logów
❌ Zwiadowca 1 i Zwiadowca 2 używają identycznej strategii EMA
```

### 🔑 Klucz do decyzji: "Co unikalnego wnosi ten moduł?"

Przed dodaniem nowego modułu/narzędzia pytamy:
1. Co ten moduł widzi/robi czego inne NIE robią?
2. Jaką lukę wypełnia w systemie?
3. Czy jego wynik trafia do kogoś kto go realnie używa?

Jeśli odpowiedź brzmi "robi to samo co X, tylko trochę inaczej" → NIE dodajemy.

---

## 🏛️ SENAT SZCZEGÓŁOWO — jak działa debata

```
               SENAT
        ┌──────────────────┐
        │   FRAKCJA BYKÓW  │  ← zbiera WSZYSTKIE argumenty ZA LONG
        │   (agent long)   │    • wskaźniki techniczne pro-long
        │                  │    • newsy pozytywne
        │                  │    • on-chain: napływ na giełdy
        └────────┬─────────┘
                 │ obaj czytają te same dane
        ┌────────┴─────────┐
        │FRAKCJA NIEDŹWIEDZI│ ← zbiera WSZYSTKIE argumenty ZA SHORT
        │  (agent short)   │    • wskaźniki techniczne pro-short
        │                  │    • newsy negatywne
        │                  │    • on-chain: odpływ z giełd, wieloryby sprzedają
        └────────┬─────────┘
                 │
        ┌────────┴─────────┐
        │  RAPORT DEBATY   │ ← Senat kompiluje oba stanowiska
        │  (oba głosy)     │    Format: { long_args: [...], short_args: [...],
        │                  │             siła_sygnałów: {long: 7/10, short: 4/10} }
        └────────┬─────────┘
                 │
              CESARZ decyduje
```

**Dlaczego tak?** Bo chcemy żeby Cesarz ZAWSZE widział oba punkty widzenia. Nie tylko "kup" — ale też "oto argumenty przeciwko". To chroni przed halucynacjami AI.

---

## 📊 INSTRUMENTY (co handlujemy)

| Priorytet | Instrument | Uwagi |
|-----------|------------|-------|
| 1 (główny) | **BTC/USDT** | Zawsze monitorowany |
| 2 | **ETH/USDT** | Zawsze monitorowany |
| 3 | **Wybrane alts** | Top 10-20 wg wolumenu na MEXC |
| 4 | **Nowe tokeny** | Moduł wykrywania (ostrożnie!) |

---

## 📍 STAN OBECNY (co działa, co nie)

| Moduł | Stan | Co brakuje |
|-------|------|-----------|
| Brama Kalkulatora | ✅ Gotowy | Tylko TA-Lib na Twoim PC |
| Kwatermistrz Danych | ✅ Gotowy | MEXC API key |
| Pierwszy Zwiadowca | ✅ Gotowy | TA-Lib + dane |
| Aegis Tarcza | ✅ Gotowy | — |
| Kartograf | ✅ Gotowy | — |
| Kronikarz | ✅ Gotowy | — |
| Cesarz (Titan Mind) | 🟡 Szkielet | DeepSeek API key |
| Senat (Meta Kora) | 🟡 Szkielet | Debata do zaprojektowania |
| Drogi (Nexus, War Lancer) | 🟡 Szkielet | MEXC API + walidacja |
| Oczy (Wszechoko) | 🔴 Plan | Do zbudowania |
| Koloseum (Valhalla) | 🟡 Szkielet | Rozbudowa |

---

*VITRUVIUSZ, architekt Imperium*
*"Każdy kamień ma swoje miejsce. Żaden kamień nie robi cudzej roboty."*
