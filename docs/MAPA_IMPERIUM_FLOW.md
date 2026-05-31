# 🏛️ MAPA PRZEPŁYWU IMPERIUM — kto z kim, co robi, jak decyduje

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

## 🚫 ZASADA ZERO DUPLIKATÓW

| Zadanie | KTO to robi | Kto NIE robi |
|---------|-------------|--------------|
| Pobieranie danych | Akwedukty (kwatermistrz) | Nikt inny |
| Liczenie matematyki | Fundament (brama) | Nikt inny |
| Generowanie sygnałów | Legiony (zwiadowcy) | Nikt inny |
| Zarządzanie ryzykiem | Pretorianie (aegis) | Nikt inny |
| Debata/konsensus | Senat (meta_kora) | Nikt inny |
| Decyzja końcowa | Cesarz (titan_mind) | Nikt inny |
| Egzekucja zlecenia | Drogi (nexus, war_lancer) | Nikt inny |
| Pamięć/logi | Biblioteki (kronikarz, mnemosyne) | Nikt inny |
| Wizualizacja | Świątynie (kartograf, sala_wojenna) | Nikt inny |
| Backtest/walidacja | Koloseum (valhalla) | Nikt inny |

**Redundancja TAK ale tylko tam gdzie ma sens:**
- Kilku zwiadowców w Legionach → OK (różne strategie, uzupełniają się)
- Kilku agentów w Senacie → OK (frakcja BYKÓW vs NIEDŹWIEDZI)
- Dwa strażniki w Pretorianach → OK (aegis=ryzyko, lustro=walidacja)

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
