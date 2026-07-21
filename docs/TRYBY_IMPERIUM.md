---
kategoria: CONSILIUM
typ: zywy
wlasciciel: imperium/koloseum/namiestnik.py, narzedzia/kalibracja_1h.py, narzedzia/kalibracja_1h_v2.py, narzedzia/sym_porownanie_tf.py
stan_na: 2026-07-21
powod_istnienia: "Jedyne miejsce z **twardym, zmierzonym werdyktem o interwale 1H** — że rój nie ma na nim dodatniego edge'u i że zaostrzanie progów asymptotuje przy ~−2.5%, nigdy nie przekraczając zera"
---
# 🎯 TRYBY IMPERIUM + ŁOWCA OKAZJI — propozycja architektury trybów

> **Status:** propozycja do decyzji Cezara (Prawo XVIII) · **Kontekst:** wizja „kilka trybów, jeden = NAJLEPSZE"

> **⚠️ Jak czytać (weryfikacja wobec kodu 2026-07-18).** Dwie warstwy:
> • **Pomiary 1H** (sekcje W-321b/c/c-v2/c-v3) to **POMIARY DATOWANE z czerwca 2026** — prawda
>   swojego czasu, **nie odświeżane** (Prawo I). Werdykt „1H bez robustnego edge'u" nadal stoi.
> • **Listy „czego brakuje"** były aktualne 2026-06-14 i **zdążyły się zestarzeć** — **6 z 6
>   braków neuronowych już powstało** (C-01, X-28, kategoria K, AUG-01+Kronikarz, X-12, PSY).
>   Sprostowane niżej. To ten sam wzorzec co RS-X w ANALIZA_NEURONY: „brak" opisany jako
>   otwarty, gdy neuron żył już od tygodni.

## Filozofia (rozkaz Cezara)

System ma **wyłapywać najlepsze okazje ze WSZYSTKICH możliwych walut** i grać tylko
tymi najmocniejszymi — kilka trade'ów w tygodniu, lewar i spot, w pełni automatycznie.
To ma być **tryb NAJLEPSZE** — jeden z kilku trybów pracy Imperium. Cel: najlepszy,
unikatowy, niepowtarzalny system w tym kierunku.

## Propozycja: 5 trybów Imperium

| # | Tryb | Co robi | Interwały | Lewar/Rynek | Częstotliwość | Status kodu |
|---|------|---------|-----------|-------------|---------------|-------------|
| 1 | **NAJLEPSZE** 🏆 (Łowca Okazji) | Skanuje cały koszyk, ranking okazji, bierze TOP-N najmocniejszych górek/dołków | dowolne (skan cross-asset) | lewar + spot, dobierany do siły | **kilka/tydzień**, wysoka pewność | 🟡 skaner gotowy (W-316), wpięcie W-317 (TERAZ) |
| 2 | **SKALP** ⚡ | Szybkie wejścia na krótkich interwałach, wiele małych trade'ów | 1m/5m/15m | futures, lewar ≤10× | wiele/dzień | 🟡 styl SCALP w Namiestniku; dane <1h SĄ (1m: 10+ par, 5m/15m: BTC+ETH), ale profil SCALP (RSI 4–7, lewar 10×) NIEPRZETESTOWANY — pomiar interwałów trzymał konfigurację swing, nie scalping |
| 3 | **SWING** 🌊 | Klasyczne swingi, trend + korekta | 4H/1D | oba, lewar ≤5× | kilka/tydzień | ✅ rdzeń (Namiestnik SWING) |
| 4 | **POZYCJA/INVEST** 🏛️ | Akumulacja długoterminowa, składanie kapitału | 1D/1W | spot, lewar ≤2× | kilka/miesiąc | 🟡 styl INVEST; brak realnej egzekucji spot |
| 5 | **OBRONA** 🛡️ (Risk-off) | W kaskadzie/krachu: spot, minimalna ekspozycja, czeka na okazję | dowolne | spot, lewar 1× | rzadko, defensywnie | 🟡 rygiel_ryzyka + breaker krzywej (częściowo) |

**Rekomendacja:** zacząć od trybu **NAJLEPSZE** (serce wizji, najwyższa wartość),
potem dopracować SKALP. Dane krótkointerwałowe **już są na dysku** (`dane/minutowe/` 10+ par,
`dane/5m` + `dane/15m` dla BTC/ETH) — brakuje nie danych, lecz **testu profilu SCALP na
własnych warunkach** (RSI 4–7, lewar ≤10×, model kosztów futures). Uwaga (Prawo I,
kandydat≠prawda): dotychczasowy pomiar interwałów (4h/1d/1h/15m) trzymał JEDNĄ konfigurację
— mierzył swing na krótkim interwale, **nie** scalping; wniosek „interwał X stratny" dotyczy
tamtej konfiguracji, nie profilu SCALP, który pozostaje niezmierzony.

## Tryb NAJLEPSZE — mechanika (W-316 + W-317)

1. **Skan koszyka** (SkanerOkazji): co tyk ranking wszystkich walut wg opportunity
   score = cross-sectional z-score (momentum/relative-strength + ADX + wolumen + zmienność).
2. **Selekcja TOP-N**: do wejścia dopuszczone tylko N najmocniejszych okazji (reszta czeka).
3. **Głosowanie roju**: na dopuszczonej walucie neurony głosują kierunek (Z-05 łapie
   górki→SHORT i dołki→LONG, reszta roju potwierdza).
4. **Filtry**: Asymetria Reżimu (W-314) odsiewa chop, Pretorianie liczą lewar/SL/TP.
5. **Sizing**: lewar i % kapitału skalowane siłą okazji × pewnością (docelowo fractional Kelly).
6. **Compounding**: zysk → pula łupów → większy kapitał na kolejne okazje (Etap B4, do zrobienia).

## ✅ Neurony „do trybu NAJLEPSZE" — WSZYSTKIE 6 JUŻ POWSTAŁY (sprostowanie 2026-07-18)

Ta lista była listą braków 2026-06-14. Zmierzone dziś — **żaden już nie brakuje:**

| Dawny „brak" | Stan w kodzie |
|---|---|
| Relative Strength cross-asset | ✅ **C-01** `NeuronRelativeStrength` (kat. C, od 2026-06-17) |
| Multi-Timeframe Confluence | ✅ **X-28** `NeuronKonfluencjaMultiTF` |
| Breakout/Range-Expansion | ✅ **X-12** (DOSTEPNY) |
| Katalizator (Augur) | ✅ **AUG-01** — a AdapterKronikarz jest **wpięty** (`neurony/sesje.py`), nie „martwy" |
| Kategoria K (makro/DXY) | ✅ **K-01…K-04** — kategoria żywa (DXY, Gold/BTC, stablecoiny) |
| Funding/OI | ✅ **PSY-01/02/04** (DOSTEPNY) |

> To nie znaczy, że tryb NAJLEPSZE jest gotowy — neurony istnieją, ale **skaner wciąż nie jest
> wpięty w pętlę decyzyjną** (niżej). Znaczy tylko, że „brakującego budulca" nie ma; brakuje spoiwa.

## Czego brakuje NAPRAWDĘ (strategie/moduły — zweryfikowane 2026-07-18)

| Pozycja | Stan | Uwaga |
|---|---|---|
| **Wpięcie skanera do pętli decyzyjnej** (W-317) | 🔴 **nadal brak** | `SkanerOkazji` żyje i działa **tylko w `backtest.py`** — nie ma go w `dyrygent.py` ani `petla_live.py`. To wciąż warunek istnienia trybu NAJLEPSZE na żywo. |
| **Conviction sizing** (W-318) | ✅ **JEST** | `pretorianie/sizing_przekonania.py` — opt-in (ZASADA WPIĘCIA, domyślnie OFF) |
| **Compounding / pula łupów** | ✅ **JEST** | dyrygent sizinguje z `engine.kapital_calkowity` (nie ze stałego startu) |
| **Bayesian P(sukces) per setup** (Beta-Binomial) | 🔴 **brak** | Sybilla liczy Brier/kalibrację proroctw o SOBIE, ale to nie P(sukces) pojedynczego setupu |
| **Realna egzekucja spot/invest** | 🔴 brak | tryby 4 i 5 wciąż deklaratywne |
| **Auto-kalibracja progów na live** | 🔴 brak | self-tuning min_adx/top_n (Etap C) |

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

## 🚨 W-321b — POMIAR 1h + porównanie TF na tym samym oknie (Prawo I, UTRATA POTENCJAŁU)

**Pytanie:** czy 90.2x to przewaga strategii, czy artefakt jednego okna? I czy
krótszy interwał (1h, priorytet Cezara) poprawia wynik? Zmierzono — nie zgadywano.

**Metoda:** ten sam pełny stack (TOP-3 + Conviction + Compounding + filtr asymetrii)
na 5 parach, na **identycznym oknie kalendarzowym 2022→2026 (~3.4 lat)** dla obu
interwałów (`narzedzia/sym_porownanie_tf.py`). Cap 1h=30k barów/parę (pełna historia
1h OOM-uje w 15GB — patrz LOG W-321b). Bez prowizji/poślizgu (jak 4h).

| Konfig (to samo okno 2022→2026, ~3.4 lat) | Trade | WR | PnL | Mnożnik |
|---|---|---|---|---|
| **4h** | 722 | 43.8% | **+579$ (+5.8%)** | **1.06x** ✅ |
| **1h** | 2347 | 46.4% | **−977$ (−9.8%)** | **0.90x** ❌ |
| *4h — pełne 9 lat (W-319, dla odniesienia)* | 2665 | 46% | *+892 295$* | *90.2x* |

**Wnioski (Prawo I — twarde, niewygodne):**
1. **90.2x to artefakt grubego ogona DOGE 2021, NIE powtarzalna przewaga.** Ten sam
   stack 4h na ostatnich 3.4 lat (bez pompy DOGE 2021) daje tylko **+5.8%**. Okno
   decyduje o rzędzie wielkości, nie sama strategia.
2. **1h jest GORSZE od 4h na tym samym oknie:** −9.8% vs +5.8%. 3.3× więcej trade'ów
   (2347 vs 722), WR wyższy (46.4% vs 43.8%), ale **edge per-trade jest ujemny** —
   więcej małych strat. A to JESZCZE BEZ prowizji, które na 1h (3.3× obrotu) zabolą
   wynik znacznie mocniej niż na 4h.
3. **Priorytet Cezara (krótkie interwały) z obecną konfiguracją NIE poprawia wyników —
   pogarsza je.** To czerwony alarm UTRATY POTENCJAŁU (Prawo XV): progi/filtry są
   skalibrowane pod 4h i nie przenoszą się na 1h. Zanim 1h wejdzie do gry, wymaga
   własnej kalibracji (min_adx, min_pewnosc, TP/SL, conviction) — inaczej tylko traci.

**Status:** 1h wpięte technicznie i ZMIERZONE, ale **nieopłacalne bez rekalibracji**.
Nie włączamy go do trybu live. Następny krok: osobna kalibracja progów pod 1h.

### W-321c — kalibracja progów 1h (siatka, `narzedzia/kalibracja_1h.py`)

Wykonano kalibrację (8 konfiguracji, okno 2024-11→2026-06 ~1.4 lat, cap 12k barów/parę,
pełny stack). Cel: czy wyższe progi czynią 1h dodatnim? Ranking (po PnL%):

| Konfig (min_adx / min_pewnosc / top_n) | Trade | WR | PnL% |
|---|---|---|---|
| 36 / 0.70 / **top2** | 430 | 44.2% | **−6.4%** (najlepszy) |
| 36 / 0.55 / top3 | 487 | 43.7% | −9.3% |
| 28 / 0.65 / top2 | 694 | 45.8% | −9.4% |
| 28 / 0.65 / top3 | 754 | 45.2% | −10.1% |
| 28 / 0.55 / top3 | 769 | 45.6% | −10.1% |
| 36 / 0.65 / top3 | 480 | 42.9% | −10.7% |
| 20 / 0.65 / top3 | 922 | 46.5% | −12.5% |
| 20 / 0.55 / top3 (baseline) | 929 | 46.8% | −12.8% |

**Wnioski (Prawo I):**
1. **Ostry filtr POŁOWI stratę** (−12.8% → −6.4%), gradient jednoznaczny: więcej
   filtra = mniej straty. ALE **żaden config w siatce nie jest dodatni** — kalibracja
   redukuje stratę, nie tworzy przewagi.
2. **ADX to dominujący lewar** (20→36 tnie 929→487 trade'ów i −12.8→−9.3%). top2 vs
   top3 pomaga modestnie. **min_pewnosc prawie nie kąsa** sam (929→922 przy 0.55→0.65)
   — większość sygnałów ma już wysoką pewność; dopiero w combo z top2+adx36+0.70 dobija.
3. Gradient sugeruje, że jeszcze ostrzejszy filtr (adx≥45, top1) MOŻE przekroczyć zero
   — zmierzone w batchu „push harder" (W-321c-v2, `narzedzia/kalibracja_1h_v2.py`).

### W-321c-v2 — „push harder" (najostrzejsze filtry, to samo okno 1.4 lat)

| Konfig (min_adx / min_pewnosc / top_n) | Trade | WR | PnL% |
|---|---|---|---|
| **50 / 0.75 / top1** | **94** | 42.6% | **−3.4%** (najlepszy ze WSZYSTKICH 13 konfig) |
| 45 / 0.70 / top2 | 217 | 41.9% | −5.9% |
| 36 / 0.70 / top2 | 430 | 44.2% | −6.4% |
| 45 / 0.70 / top1 | 172 | 41.9% | −6.5% |
| 36 / 0.75 / top1 | 337 | 40.4% | −11.2% |

**Werdykt kalibracji (Prawo I — z korektą wcześniejszej tezy):** wbrew pierwotnemu
wnioskowi „top1 gorszy", top1 nie jest jednostajnie zły — zależy od ostrości ADX:
- przy umiarkowanym ADX top1 wpuszcza za dużo i traci mocno (adx36/top1 = −11.2%, 337 tr),
- przy **ekstremalnym ADX** top1 jest NAJLEPSZY (adx50/top1 = **−3.4%**, tylko 94 tr).

Prawdziwym lewarem jest **skrajna selektywność** — handluj tylko przy bardzo silnym
trendzie (ADX≥50) i tylko jedną, najlepszą okazję. To zbliża 1h do progu rentowności
(z −12.8% baseline do −3.4%), ale **wciąż na minusie**.

⚠️ **Zastrzeżenie istotności (Prawo I):** −3.4% liczone na **94 trade'ach / 1.4 lat**
(≈1.3/tydz.) — próbka mała, wynik w granicach szumu, NIE robustny edge.

**Probe adx≥55/60 (W-321c-v3 — domyka pytanie „czy przekroczy zero"):**
| Konfig | Trade | WR | PnL% |
|---|---|---|---|
| adx≥55 / 0.75 / top1 | 62 | 46.8% | −2.6% |
| adx≥60 / 0.75 / top1 | 27 | 48.1% | −2.5% |

**Gradient się WYPŁASZCZA i NIE przekracza zera:** adx50 −3.4% → adx55 −2.6% → adx60 −2.5%
(asymptota ~−2.5%), a liczba trade'ów zapada się 94→62→27. Przy 27 trade'ach przewaga
byłaby i tak nieodróżnialna od przypadku. **Definitywnie: 1h nie da się doprowadzić do
plusa samym zaostrzaniem progów.** Wizualizacja: `docs/wykres_kalibracja_1h.png`.

**🚨 KONKLUZJA 1h (UTRATA POTENCJAŁU zmierzona, Prawo XV):** rój w obecnym kształcie
**nie ma robustnego dodatniego edge'u na 1h**. Skrajna selektywność asymptotuje przy ~−2.5%
(na garstce trade'ów), nigdy nie przekraczając zera. Neurony/progi są strukturalnie
dopasowane do 4h+ (trend, swing), nie do mikrostruktury 1h. **Rekomendacja:** NIE używać 1h
z obecnym rojem jako trybu dochodowego. Ścieżki na przyszłość (jeśli 1h ma być priorytetem):
(a) neurony mikrostrukturalne dedykowane 1h, (b) model kosztów (1h ma wielokrotnie wyższy
obrót — prowizje dobiją), (c) **zostać na 4h, gdzie stack jest dodatni (+5.8% na tym samym
oknie)** — rekomendowane.

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
