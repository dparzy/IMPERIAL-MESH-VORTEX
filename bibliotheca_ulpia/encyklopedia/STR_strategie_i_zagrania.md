# 🏛️ STR — Strategie i Zagrania | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐ (wysoki — to repertuar bojowy roju)
> **Dla nowicjusza (ZPO):** strategia = kompletny plan: kiedy WEJŚĆ (sygnał), kiedy
> WYJŚĆ (cel/stop), ile RYZYKOWAĆ (sizing), w jakich WARUNKACH działa (reżim). Sam sygnał
> to nie strategia. Imperium ma 20 strategii w `rejestr_strategii.py` — tu encyklopedia
> rodzin strategii i jak je dobierać do reżimu.

## 📑 SPIS TREŚCI
1. [Rodziny strategii](#1-rodziny-strategii)
2. [Anatomia strategii](#2-anatomia)
3. [Dobór do reżimu](#3-dobór-do-reżimu)
4. [Setupy klasyczne](#4-setupy-klasyczne)
5. [Multi-timeframe](#5-multi-timeframe)
6. [Wpływ na Imperium](#6-wpływ-na-imperium)
7. [Źródła](#7-źródła)

---

## 1. RODZINY STRATEGII

| Rodzina | Logika | Działa w | Ryzyko |
|---------|--------|----------|--------|
| **Trend-following** | kupuj siłę, sprzedawaj słabość | trend | whipsaw w range |
| **Mean-reversion** | kupuj przecenę, sprzedawaj wykup | range | katastrofa w trendzie |
| **Breakout** | wejdź na wybiciu z konsolidacji | przejście reżimu | fakeout |
| **Momentum** | to co rosło, rośnie dalej | trend wczesny/średni | nagłe odwroty |
| **Stat-arb / pairs** | kointegracja, neutralny kierunkowo | każdy (market-neutral) | rozpad relacji |
| **Carry / funding** | zbieraj funding/premie | spokojny | ogon (tail risk) |
| **Scalping** | wiele małych zysków, HFT | płynny, wąski spread | koszty/prowizje |

**Kluczowa prawda:** żadna strategia nie działa zawsze. Trend-following i mean-reversion
to przeciwieństwa — wybór zależy od REŻIMU (stąd waga filtra reżimu, np. EXP-13/14).

---

## 2. ANATOMIA STRATEGII

Każda kompletna strategia Imperium ma (rejestr_strategii.py):
- **Wejście:** klucze sygnałów wyzwalających
- **Filtr:** warunki kontekstu (reżim, trend wyższego TF)
- **Wyjście:** cel zysku, stop, trailing, czasowe
- **Sizing:** % ryzyka, mnożniki (Gubernator, Senat, MTF)
- **Reżim docelowy:** w jakich warunkach włączona

---

## 3. DOBÓR DO REŻIMU

| Reżim | Sygnał reżimu | Preferowana strategia |
|-------|---------------|----------------------|
| Trend ↑ | EMA50>EMA200, ADX>25, RADAR-01 | trend-following, momentum, breakout long |
| Trend ↓ | EMA50<EMA200, ADX>25 | trend-following short, unikaj long |
| Range | ADX<20, niska zmienność GARCH | mean-reversion, carry |
| Wysoka zmienność | GARCH wysoki (EXP-13) | redukcja sizingu, szerszy SL |
| Cienka płynność | Amihud wysoki (Z-06), Kyle wysoki (EXP-14) | ostrożność, mniejsze pozycje |

**Lekcja z KROKU B (2026-06-21):** brama MTF szkodziła w reżimie mean-reversion (I-VI 2026),
bo wzmacniała wejścia trendowe przeciw dominującej rewersji. **Dobór strategii do reżimu
to nie luksus — to różnica między zyskiem a stratą.**

---

## 4. SETUPY KLASYCZNE

- **Pullback w trendzie:** wejście na cofnięciu do EMA/wsparcia w trendzie (Raschke „80-20")
- **Breakout z wolumenem:** wybicie poziomu + potwierdzenie wolumenem (inaczej fakeout)
- **Trend template (Minervini):** cena>MA50>MA150>MA200 — wejście na sile
- **Mean-reversion na ekstremach:** RSI<30/>70 + Bollinger + niska zmienność
- **Dywergencja:** cena nowy szczyt, oscylator/CVD nie → wyczerpanie
- **Market profile (Dalton):** value area, point of control jako poziomy decyzji

---

## 5. MULTI-TIMEFRAME

- **Zasada:** kierunek z wyższego TF, timing z niższego. Nie handluj przeciw głównemu trendowi.
- **W Imperium (W-384):** brama konfluencji MTF — EMA50/200 + MACD na zagregowanych barach.
- **Status:** opt-in **OFF** (backtest KROK B: na jednym reżimie szkodzi). Re-test wieloreżimowy w toku.
- **Lekcja:** MTF to nie zawsze „lepiej" — w mean-reversion brama trendowa może szkodzić.

---

## 6. WPŁYW NA IMPERIUM

### Co mamy:
- **20 strategii** w `rejestr_strategii.py` (34 klucze, Klucznik spójny)
- **Profile stylu (W-323):** SCALP / SWING / INVEST
- **Senat** — agregacja głosów, próg pewności
- **MTF konfluencja (W-384)** — brama wyższego TF (OFF)
- **Gubernator (W-325)** — globalny mnożnik wg reżimu

### 🚨 Do wdrożenia (Prawo XV):
1. ⭐⭐⭐⭐ **Przełącznik strategii wg reżimu** — auto-wybór trend vs mean-reversion na podstawie
   ADX/GARCH (EXP-13 jako detektor reżimu — jego właściwe użycie!)
2. ⭐⭐⭐ **Re-test MTF wieloreżimowy** — czy brama pomaga w trendzie (w toku, lokal + paginacja)
3. ⭐⭐⭐ **Carry/funding strategia** — gdy PSY-01 funding feed ożyje

---

## 7. ŹRÓDŁA
- BIB-002 Murphy — *Technical Analysis of Financial Markets* (kanon TA)
- BIB-013/014 Dalton — *Markets in Profile / Mind Over Markets* (market profile)
- BIB-006/021 — scalping setupy
- BIB-019 Harris — *Handbook for Cryptocurrencies Trading*
- BIB-010/011 Chan — strategie ilościowe
- Powiązane: **TRD**, **LEW**, **RSK**, **ALG**
