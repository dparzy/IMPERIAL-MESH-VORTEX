# 🏛️ ARCHITEKTURA IMPERIUM — pełna mapa

> **Po co:** Jedno miejsce, które spina **21 prawami** z **realnym kodem** (17 modułów).
> Pokazuje, jak Cesarstwo jest zbudowane i którędy płynie sygnał.

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
🛤️ DROGI            drogi/         nexus_hub             multi-exchange routing [III, XIII]
                                   war_lancer            egzekucja HF           [III]
🎨 ŚWIĄTYNIE       swiatynie/     kartograf             wykresy PNG            [V]
                                   sala_wojenna          dashboard             [V]
📚 BIBLIOTEKI      biblioteki/    mnemosyne             pamięć transakcji      [VIII, XIII]
                                   kronikarz             logi, dziennik         [XIII]
                                   igrzyska              ranking batch + observer pattern [XV]
                                   hedge_mwu             MWU online learning (W-049)     [XV, XVI]
🧮 FUNDAMENT       fundament/     brama_kalkulatora     jedyne wejście do mat. [I, IX, XIII]
                                   kuznia_narzedzi       kanoniczne wskaźniki   [I]
🏟️ KOLOSEUM        koloseum/      valhalla              backtest, Monte Carlo  [VI, VII]
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

*PRAWDA. Organizm, nie kolekcja. Mniej, ale prawdziwie.*
— VITRUVIUSZ, architekt Imperium
