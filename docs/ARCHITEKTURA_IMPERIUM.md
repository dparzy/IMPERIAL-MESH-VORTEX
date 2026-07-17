---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/akwedukty/kwatermistrz_danych.py, imperium/biblioteki/hedge_mwu.py, imperium/biblioteki/igrzyska.py, imperium/biblioteki/kronikarz.py, imperium/biblioteki/mnemosyne.py, imperium/biblioteki/notarius.py, imperium/cesarz/titan_mind.py, imperium/drogi/nexus_hub.py, imperium/fundament/brama_kalkulatora.py, imperium/fundament/kuznia_narzedzi.py, imperium/koloseum/backtest.py, imperium/koloseum/haruspex.py, imperium/koloseum/monte_carlo.py, imperium/koloseum/walidacja.py, imperium/koloseum/walk_forward.py, imperium/legiony/pierwszy_zwiadowca.py, imperium/legiony/roj_sygnalow.py, imperium/oczy/censor_sprzetu.py, imperium/oczy/wszechoko.py, imperium/pretorianie/aegis_tarcza.py, imperium/pretorianie/lustro_prawdy.py, imperium/senat/meta_kora.py, imperium/swiatynie/kartograf.py, imperium/swiatynie/specula_swiec.py, imperium/swiatynie/web_dashboard.py
stan_na: 2026-07-16
powod_istnienia: "Jedna strona spinająca 25 Praw z realnym kodem — jedyne miejsce z tabelą 'dzielnica → plik → rola → prawa' + diagram przepływu sygnału + mapowanie warstw architektury na źródła bib"
dlug: "🚨 opisuje nieistniejący kod: drogi/war_lancer.py, swiatynie/sala_wojenna.py, koloseum/valhalla.py"
---
# 🏛️ ARCHITEKTURA IMPERIUM — pełna mapa

> **Stan na:** 2026-07-16 · **Po co:** Jedno miejsce, które spina **25 Praw** z **realnym kodem**
> (160 modułów .py, 87 neuronów). Pokazuje, jak Cesarstwo jest zbudowane i którędy płynie sygnał.
> Liczby **policzone z kodu**, nie z pamięci (Prawo XXI reguła 8).

---

## 🗺️ Mapa dzielnic (kod → rola → prawa)

```
👑 CESARZ          cesarz/        titan_mind            decyzja, harmonogram   [III, XIV]
🏛️ SENAT           senat/         meta_kora             debata agentów         [IX, XIII]
⚔️ LEGIONY          legiony/       pierwszy_zwiadowca    boty, pełny cykl       [IV, VI]
                                   roj_sygnalow          konsensus sygnałów     [X, IX]
🛡️ PRETORIANIE     pretorianie/   aegis_tarcza          ryzyko, circuit breaker[IX]
                                   lustro_prawdy         walidacja adwersarialna[I, IX]
🚰 AKWEDUKTY        akwedukty/     kwatermistrz_danych   dane OHLCV (CCXT/CSV)  [II]
👁️ OCZY            oczy/          wszechoko             percepcja wielowarstwowa[XII]
                                   censor_sprzetu        cenzus majątku maszyny → klasa+alarm[XV]
🛤️ DROGI            drogi/         nexus_hub             multi-exchange routing [III, XIII]
                                   war_lancer            egzekucja HF           [III]
🎨 ŚWIĄTYNIE       swiatynie/     kartograf             wykresy PNG            [V]
                                   sala_wojenna          dashboard             [V]
                                   specula               świece OHLC w terminalu[V, XXIV]
📚 BIBLIOTEKI      biblioteki/    mnemosyne             pamięć transakcji      [VIII, XIII]
                                   kronikarz             logi, dziennik         [XIII]
                                   igrzyska              ranking batch + observer pattern [XV]
                                   hedge_mwu             MWU online learning (W-049)     [XV, XVI]
                                   notarius              stenograf słów Nauczyciela → pary
                                                         prompt→odpowiedź = surowiec Szkoły
                                                         TIRO (E2)              [I, XV, XXIV]
🧮 FUNDAMENT       fundament/     brama_kalkulatora     jedyne wejście do mat. [I, IX, XIII]
                                   kuznia_narzedzi       kanoniczne wskaźniki   [I]
🏟️ KOLOSEUM        koloseum/      valhalla              backtest, Monte Carlo  [VI, VII]
                                   haruspex              predykcja reżimu (Markow) — ⚠️ falsyfikowany pomiarem [I, XVI]
```

---

## 🔄 Jak płynie sygnał (cykl decyzyjny)

```
   🚰 AKWEDUKTY ── dane OHLCV ──►  🧮 FUNDAMENT (Brama)
   (kwatermistrz)                   liczy RSI/EMA/ATR... (Prawo I)
                                          │  JSON "answer key" + pieczątka
                                          ▼
   👁️ OCZY ── warstwy percepcji ──► ⚔️ LEGIONY (zwiadowcy)
   (wszechoko)                       generują surowe sygnały
                                          │
                                          ▼
   🛡️ PRETORIANIE ── filtr/weto ──► 🏛️ SENAT (debata)        [Prawo IX]
   (aegis, lustro)                   ścierają argumenty
                                          │
                                          ▼
                                   👑 CESARZ (decyzja)        [Prawo III, XIII]
                                   widzi cały zapis debaty
                                          │
                                          ▼
   🛤️ DROGI ── egzekucja ──────────► rynek
   (nexus, war_lancer)
                                          │
                                          ▼
   📚 BIBLIOTEKI (pamięć) + 🎨 ŚWIĄTYNIE (wykres/dashboard)   [Prawo VIII, V]
   🏟️ KOLOSEUM ── testuje strategie zanim wejdą do boju ──    [Prawo VI, VII]
```

---

## 🎯 Cykl bojowy Fazy 0 (to, co realnie się spina dziś)

6 modułów uruchamianych jednym poleceniem (przez `pierwszy_zwiadowca`):

1. **kwatermistrz_danych** → dane (biblioteka / MEXC / syntetyczne)
2. **brama_kalkulatora** → liczy RSI + EMA (Prawo I)
3. **pierwszy_zwiadowca** → strategia trend-following
4. **aegis_tarcza** → ryzyko, circuit breaker
5. **kartograf** → wykres PNG
6. **kronikarz** → raport + dziennik

> Reszta modułów (senat, cesarz, oczy, drogi...) to **sprawdzony kod-baza**,
> jeszcze nie wpięty w cykl. Status uczciwie w [archiwum/AUDYT_ADOPCJI.md](../archiwum/AUDYT_ADOPCJI.md).

---

## ⚠️ Stan realny (Prawo I)

- 🟢 **Brama** — w pełni działa, egzekwuje Prawo I w kodzie.
- 🟡 **Cykl Fazy 0** — kod gotowy i spięty (loader naprawiony po reorganizacji),
  ale **nieuruchomiony na realnych danych** (brak TA-Lib + danych w chmurze).
- 🔴 **`pierwszy_zwiadowca`** — NIE jest "zwalidowaną strategią": dane syntetyczne,
  brak slippage, kruche wyniki. To *wstępny paper-test*. Szczegóły w audycie.

---

## 📚 ŹRÓDŁA — Kanon biblioteki za architekturą (BIB)

> **Po co ta architektura?** Każda warstwa Imperium ma teoretyczne ugruntowanie w bibliotece
> (**79 książek** — policzone 2026-07-16). Tu mapa: warstwa → książka.
> Pełna esencja: `bibliotheca_ulpia/encyklopedia/`.

| Warstwa architektury | Dlaczego tak (koncept) | Źródło BIB |
|----------------------|------------------------|-----------|
| **Brama Kalkulatora** (neuron nie liczy sam) | rozdział obliczeń od interpretacji = pipeline Feature/Inference (FTI) | BIB-035 Iusztin&Labonne (LLM Engineer's Handbook) |
| **Meta-labeling (Arbiter Fiduciae)** | rozdzielenie KIERUNEK vs ROZMIAR/pewność sygnału | BIB-007 López de Prado (AFML) |
| **Arena Trzech Bram** | Triple-Barrier Method (TP/SL/czas) zamiast fixed-horizon | BIB-007 López de Prado (AFML) |
| **Koloseum (walidacja DSR/PBO)** | obrona przed backtest overfitting / data-snooping | BIB-007 López de Prado + BIB-041 Taleb |
| **Senat (debata 4 ról + synteza)** | wzorzec Supervisor (multi-round → synteza), nie prosty Router | BIB-034 Infante (AI Agents) |
| **Gubernator + WAGI_REZIMU** | mnożnik reżimu = kontekst makro/cyklu jako TŁO decyzji | BIB-001 Patel (18-letni cykl) |
| **Centrum Pamięci (W-360 v3)** | warstwowa pamięć agenta + decay wg ważności (FinMem) | BIB-033 Huyen + BIB-036 Alto + arXiv MEM-01..04 |
| **Bezpieczniki (Reguła 6%/HALT)** | budżet ryzyka + loss-aversion → nieprzełamywalny stop | BIB-015 Elder + BIB-040 Bernstein |
| **Kalkulator Lewara (VolatilityDrag/Kelly)** | erozja zmiennościowa + fractional Kelly z korektą estymacji | BIB-008/018 Sinclair |
| **Warstwa ryzyka (EWMA/VaR/ES)** | EWMA λ=0.94, Expected Shortfall dla grubych ogonów | BIB-042 Jorion |

> Mapowanie warstwa→klucz neuronu: `docs/KATALOG_NEURONOW.md` § Źródła. Mapowanie strategii: `docs/KATALOG_STRATEGII.md` § Źródła.

---

*PRAWDA. Organizm, nie kolekcja. Mniej, ale prawdziwie.*
— VITRUVIUSZ, architekt Imperium
