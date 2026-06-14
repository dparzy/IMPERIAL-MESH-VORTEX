# 🎯 TRYBY IMPERIUM + ŁOWCA OKAZJI — propozycja architektury trybów

> **Stan na:** 2026-06-14 · **Status:** propozycja do decyzji Cezara (Prawo XVIII) · **Kontekst:** wizja „kilka trybów, jeden = NAJLEPSZE"

## Filozofia (rozkaz Cezara)

System ma **wyłapywać najlepsze okazje ze WSZYSTKICH możliwych walut** i grać tylko
tymi najmocniejszymi — kilka trade'ów w tygodniu, lewar i spot, w pełni automatycznie.
To ma być **tryb NAJLEPSZE** — jeden z kilku trybów pracy Imperium. Cel: najlepszy,
unikatowy, niepowtarzalny system w tym kierunku.

## Propozycja: 5 trybów Imperium

| # | Tryb | Co robi | Interwały | Lewar/Rynek | Częstotliwość | Status kodu |
|---|------|---------|-----------|-------------|---------------|-------------|
| 1 | **NAJLEPSZE** 🏆 (Łowca Okazji) | Skanuje cały koszyk, ranking okazji, bierze TOP-N najmocniejszych górek/dołków | dowolne (skan cross-asset) | lewar + spot, dobierany do siły | **kilka/tydzień**, wysoka pewność | 🟡 skaner gotowy (W-316), wpięcie W-317 (TERAZ) |
| 2 | **SKALP** ⚡ | Szybkie wejścia na krótkich interwałach, wiele małych trade'ów | 1m/5m/15m | futures, lewar ≤10× | wiele/dzień | 🟡 styl SCALP w Namiestniku; brak danych <1h w backteście |
| 3 | **SWING** 🌊 | Klasyczne swingi, trend + korekta | 4H/1D | oba, lewar ≤5× | kilka/tydzień | ✅ rdzeń (Namiestnik SWING) |
| 4 | **POZYCJA/INVEST** 🏛️ | Akumulacja długoterminowa, składanie kapitału | 1D/1W | spot, lewar ≤2× | kilka/miesiąc | 🟡 styl INVEST; brak realnej egzekucji spot |
| 5 | **OBRONA** 🛡️ (Risk-off) | W kaskadzie/krachu: spot, minimalna ekspozycja, czeka na okazję | dowolne | spot, lewar 1× | rzadko, defensywnie | 🟡 rygiel_ryzyka + breaker krzywej (częściowo) |

**Rekomendacja:** zacząć od trybu **NAJLEPSZE** (serce wizji, najwyższa wartość),
potem dopracować SKALP (wymaga danych krótkointerwałowych — Etap C, live).

## Tryb NAJLEPSZE — mechanika (W-316 + W-317)

1. **Skan koszyka** (SkanerOkazji): co tyk ranking wszystkich walut wg opportunity
   score = cross-sectional z-score (momentum/relative-strength + ADX + wolumen + zmienność).
2. **Selekcja TOP-N**: do wejścia dopuszczone tylko N najmocniejszych okazji (reszta czeka).
3. **Głosowanie roju**: na dopuszczonej walucie neurony głosują kierunek (Z-05 łapie
   górki→SHORT i dołki→LONG, reszta roju potwierdza).
4. **Filtry**: Asymetria Reżimu (W-314) odsiewa chop, Pretorianie liczą lewar/SL/TP.
5. **Sizing**: lewar i % kapitału skalowane siłą okazji × pewnością (docelowo fractional Kelly).
6. **Compounding**: zysk → pula łupów → większy kapitał na kolejne okazje (Etap B4, do zrobienia).

## Czego brakuje (neurony) — do trybu NAJLEPSZE

| Brak | Po co | Priorytet |
|---|---|---|
| **Neuron Relative Strength cross-asset** | rdzeń skanera już to liczy, ale jako neuron głosujący wzmocniłby ranking | ŚREDNI |
| **Neuron Multi-Timeframe Confluence** | potwierdzenie dołka/szczytu na 1h+4h+1d naraz (wyższa pewność) | WYSOKI |
| **Neuron Breakout/Range-Expansion** | wyłapywanie startu ruchu (BB squeeze→expansion); X-12 częściowo | ŚREDNI |
| **Neuron Katalizator (Augur)** | AUG-01 istnieje, ale AdapterKronikarz odpięty live → martwy | WYSOKI (tani) |
| **Kategoria K (makro/DXY/intermarket)** | kontekst makro dla wejść (risk-on/off) | NISKI |
| **Neuron Funding/OI realny** | PSY-01/02/04 czekają na feed futures live | ŚREDNI (live) |

## Czego brakuje (strategie/moduły)

| Brak | Po co | Priorytet |
|---|---|---|
| **Wpięcie skanera do pętli** (W-317) | bez tego tryb NAJLEPSZE nie istnieje w praktyce | **NAJWYŻSZY (TERAZ)** |
| **Bayesian P(sukces) per setup** | skalibrowane prawdopodobieństwo zamiast „pewności" (Beta-Binomial) | WYSOKI |
| **Compounding / pula łupów** | reinwestycja zysku → wzrost kapitału | WYSOKI |
| **Backtest cross-sectional** | właściwa miara łowcy (czy skaner wybrał zwycięzców?) | WYSOKI |
| **Realna egzekucja spot/invest** | tryby 4 i 5 dziś tylko deklaratywne | ŚREDNI |
| **Auto-kalibracja progów na live** | self-tuning min_adx/top_n/progi pewności | ŚREDNI (live, Etap C) |

## Wynik symulacji trybu NAJLEPSZE (9 lat, 5 walut) — Prawo XVI/I

| Konfig | Trade | PnL | Kapitał końcowy | WR |
|---|---|---|---|---|
| BASELINE (każda para gra) | 2870 | +52 789$ | 62 659$ | 49% |
| TRYB NAJLEPSZE (skaner TOP-2 + filtr + min_pewnosc 0.62) | 2247 | +24 135$ | 34 032$ | 45% |
| **TRYB NAJLEPSZE + CONVICTION (skaner TOP-3 + Sizing Przekonania)** | **2665** | **+64 976$** | **74 782$** | 46% |
| **PEŁNY STACK + COMPOUNDING (TOP-3 + Conviction + pula łupów, W-319)** | **2665** | **+892 295$** | **902 295$** | 46% |

**Compounding (W-319) — wynik i uczciwe zastrzeżenie (Prawo I):** reinwestycja zysku
(sizing z `kapital_calkowity`, nie ze stałego startu) daje **10 000$ → 902 295$ = 90.2x**
w 9 lat. To geometryczny efekt składania na tej samej serii trade'ów (2665, WR 46%).
⚠️ **Wynik jest gruboogonowy i zależny od DOGE** (meme-pumpy tworzą prawie cały zysk),
liczony **bez prowizji/poślizgu/finansowania lewara** i bez limitu płynności — to dowód
mechaniki (składanie działa), NIE obietnica 90x na żywo. Sufit ekspozycji per okazja
(Prawo XXV) i koszty realne obetną tę liczbę; traktujemy ją jako górną granicę potencjału.

**Rozkład per coin (BASELINE):** DOGE +52 327$ (1316 tr) ← prawie cały zysk; ETH +545,
BTC +194, SOL +47, BNB −324. **Zysk jest GRUBO-OGONOWY: meme/alt pumpy (DOGE).**

### 🚨 Lekcja (uczciwie, Prawo I): selekcja BEZ amplifikacji daje MNIEJ

Tryb NAJLEPSZE jak skonfigurowany zarobił mniej niż baseline. Powód:
- TOP-2 + filtry przycięły DOGE (1316→880 tr, +52327→+23803$) — **wycięto gruby ogon**.
- Spadła też jakość per-trade na DOGE (39,8→27,0$/tr) — filtry nieskalibrowane pod meme.
- Filtry POPRAWIŁY maruderów (BNB −324→+77, ETH/SOL lekko lepiej per-trade), ale strata
  na zwycięzcy przeważyła.

**Wniosek:** wizja „mało trade'ów, większy lewar na najlepszych" wymaga DWÓCH rzeczy
naraz: (1) selekcji TOP-N **oraz** (2) **amplifikacji stawki/lewara na wyselekcjonowanych**
(conviction sizing). Sama selekcja przycina gruby ogon → mniej zysku.

### ✅ Potwierdzenie: selekcja + CONVICTION bije baseline (W-318)

Po dołożeniu Sizing Przekonania (TOP-3, większa stawka na mocniejszej okazji):
- **+64 976$ vs baseline +52 789$ = +23% więcej zysku** przy **MNIEJSZEJ liczbie trade'ów**
  (2665 vs 2870) — dokładnie wizja „mniej, ale lepiej".
- **Wszystkie waluty na plusie** (BNB z −324$ baseline → +238$; ETH/SOL/BTC poprawione).
- DOGE wzmocniony (+63 562 vs +52 327 baseline) — postawiliśmy WIĘCEJ na najmocniejszego.

**To dowód tezy (Prawo XVI):** wybierz najlepsze okazje I postaw na nie więcej =
więcej zysku, mniej trade'ów, gruby ogon zachowany i wzmocniony zamiast przycięty.

> Backtest 9-letni jednowalutowy to NIE werdykt (reframe audytu) — ale pokazuje,
> gdzie jest przewaga: w grubym ogonie pomp altów, którego nie wolno odfiltrować,
> a NALEŻY na nim postawić więcej (conviction sizing).
