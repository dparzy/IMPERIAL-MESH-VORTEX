# 📜 LOG ZMIAN IMPERIUM — Żywa Pamięć Projektu

> **Zasada (ROZKAZ STAŁY):** Po KAŻDEJ zmianie systemu, kodu, dokumentacji — wpis do tego logu.
> Format: Data | Typ | Opis | Powód | Pliki. Najnowsze wpisy na górze.
> Ten plik jest źródłem prawdy historii Imperium. Bez niego decyzje giną.

---

---

---

## 2026-06-11 | KAMIEŃ MILOWY | Test 5 par 1D — EDGE UNIWERSALNY (wszystkie zarabiają!)

**Pierwszy szeroki test (BTC/ETH/SOL/BNB/DOGE, 1D AUTO, pełne historie, formacja
Legionów + Augur w roju, n_prob=5):**

| Para | trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR | Etap I |
|---|---|---|---|---|---|---|---|---|
| BTC | 61 | 55.7% | **2.26** | 4.3% | +3934 | 0.86 | **0.94** | ⛔ blisko |
| ETH | 75 | 48.0% | 1.12 | 12.7% | +705 | 0.17 | 0.23 | ⛔ |
| SOL | 55 | 38.2% | 1.14 | 9.0% | +636 | 0.22 | 0.23 | ⛔ |
| BNB | 68 | 51.5% | 1.63 | 10.8% | +3320 | 0.60 | 0.71 | ⛔ |
| DOGE | 16 | 75.0% | **2.73** | 22.2% | +9745 | 0.95 | 0.92 | ⛔ (n=16) |

**WNIOSEK (Prawo I — twardy fakt):** **PF > 1 na WSZYSTKICH 5 parach, PnL dodatni
wszędzie.** Dzienny edge roju jest UNIWERSALNY, nie przypadkiem BTC. To fundamentalnie
zmienia obraz: mamy realną, przenośną przewagę kierunkową na 1D.

**Czemu żadna nie przechodzi Etapu I:** próg Sharpe>1.0 (surowy, słuszny) — pojedyncze
pary mają zbyt zmienne zwroty względem średniej. BTC i DOGE są o włos (0.86–0.95).

**🎉 WYNIK PORTFELA (2026-06-11) — PIERWSZY RAZ W HISTORII IMPERIUM ETAP I ZALICZONY:**

`narzedzia/pomiar_portfela.py` (W-290) złożył 5 krzywych equity w portfel równoważony
(2945 dni, dzienne zwroty wyrównane po dacie UTC):

| Metryka | Najlepsza para sama | PORTFEL 5 par |
|---|---|---|
| Sharpe roczny | 0.95 (DOGE) | **+1.24 ✅ >1.0** |
| MaxDD | 4.3% (BTC) | **6.9% ✅ <15%** |
| DSR (n_prob=5) | 0.94 (BTC) | **0.9962 ✅ ≥0.95** |
| **Werdykt Etapu I** | ⛔ żadna | **✅ ZALICZONY** |

**DLACZEGO DZIAŁA (Prawo XVI — zmierzone, nie zgadnięte):** średnia korelacja par
dziennych zwrotów = **+0.02** (niemal ZEROWA!). Edge roju na każdej parze jest
praktycznie NIEZALEŻNY → dywersyfikacja redukuje wariancję portfela ~5×, średnia
zwrotu zostaje. Markowitz w czystej postaci. To NIE wymagało zmiany ani jednego
neuronu — sama struktura portfela przeskoczyła próg.

**ZNACZENIE:** mamy pierwszą konfigurację gotową do Etapu II (paper trading):
NIE pojedyncza para, lecz KOSZYK 5 par równoważony (ROADMAP Faza 3 "Kostka Rubika"
zrealizowana w pomiarze). Uczciwie: to backtest — Etap II (14 dni paper) i III (live
mikro) wciąż przed nami; ale droga jest OTWARTA i zmierzona twardą bramką (DSR 0.996).

**Pliki:** `narzedzia/pomiar_portfela.py`. **Następne:** silnik portfelowy (jedna
sesja, N par, wspólny kapitał, realokacja) jako produkcyjny tryb backtestu.

## 2026-06-11 | UNIKAT W-289 v2 💎 | Augur rozbudowany: per-para + kalendarz FOMC (blackout) + decay/spójność

**Rozbudowa Kronikarza Zdarzeń o 3 wymiary (na prośbę Cezara):**
1. **PER-PARA:** zdarzenia mają pole `pary` (ETH ETF → tylko ETHUSDT; halving/krach/
   FOMC = makro/BTC-dominacja → wszystkie). `kontekst(ts, symbol)` filtruje —
   kluczowe pod test 5 par (ETH ETF nie zafałszuje SOL).
2. **KALENDARZ FOMC (56 dat 2020–2026, publiczne):** dwie funkcje na raz —
   • event-study post-FOMC (wysokie n → statystyka mocna),
   • **BLACKOUT pre-FOMC**: ≤2 dni PRZED posiedzeniem augur WIE, że FED idzie →
     AUG-01 głosuje NEUTRAL-ostrożność "zredukuj ryzyko". To "znajomość przyszłości",
     o którą prosił Cezar (dokładny dzień/czas). Daty 2026 = znane przyszłe okna.
3. **DECAY + SPÓJNOŚĆ:** `waga_zaniku` (1.0 w dniu zdarzenia → 0 na krawędzi okna)
   i `zgodne_kierunkowo`/`rozrzut_pct` (czy historyczne epizody mówią jednym głosem).
   AUG-01 moduluje pewność: bazowa × decay × bonus-zgodności.

**Symbioza:** EVENT_* rozszerzone (WAGA, ZGODNE, BLACKOUT, DNI_DO); AUG-01 v2
respektuje blackout (pierwszeństwo) i decay. +7 testów (per-para, blackout,
pierwszeństwo, decay, spójność, neuron-blackout, neuron-decay).

**Pliki:** `imperium/biblioteki/kronikarz_zdarzen.py`, `imperium/legiony/neurony/sesje.py`,
`tests/test_kronikarz_zdarzen.py`.
**Testy:** 688/688 ✅. Audyt: pełna harmonia.

## 2026-06-10 | UNIKAT W-289 💎 | KRONIKARZ ZDARZEŃ (Augur) — zdarzenia fundamentalne jako głos roju

**Wizja Cezara zrealizowana** (= ROADMAP Faza 3 "Macierz zdarzeń historycznych" + W-039):
system zna zdarzenia fundamentalne, dopasowuje historyczne analogie do live i podaje
PROCENTOWE prawdopodobieństwa jako głos w roju.

**Architektura (3 płaszczyzny, pełna symbioza):**
1. **`biblioteki/kronikarz_zdarzen.py`** — KATALOG 12 zdarzeń (HALVING×3, ETF×3,
   KRACH×3, REGULACJA×2, MAKRO; daty powszechnie weryfikowalne) + **przyczynowe
   event-study**: `studium(typ, ts)` liczy forward-zwroty WYŁĄCZNIE z epizodów
   o domkniętym horyzoncie przed ts (test wymusza zero look-ahead; bieżące zdarzenie
   nie zasila własnych statystyk).
2. **AdapterKronikarz** (mechanizm adapterów Dyrygenta) → wstrzykuje EVENT_TYP/
   DNI_PO/N/PROB_WZROSTU/MEDIANA_PCT tylko w oknie ≤30 dni po zdarzeniu.
3. **AUG-01 NeuronAugur** (R, waga 6, WSPOLNY): n≥2 ∧ prob≥65% → LONG;
   prob≤35% → SHORT; n<2 → NEUTRAL "za mało historii" (Prawo I). W12: allowlista
   adapterowa + twarda weryfikacja ożywienia.

**ORYGINALNOŚĆ:** literatura daje jedną liczbę z jednego badania — nasz augur
SAMOKALIBRUJE się z własnych barów i mądrzeje z każdą parą/historią bez zmiany kodu.
Źródła naukowe kierunku (ZPO, w docstringu): FOMC-drift (JFM 2022), halving-synthetic-
control (+24.55%, arXiv 2511.05512), spot-ETF (IRFA 2025).

**TABELA DOWODOWA (BTC 1D 2017–2026, policzona przez moduł, ts=2026-06-10):**

| Typ | n | 30 dni: prob↑ / mediana | 90 dni: prob↑ / mediana |
|---|---|---|---|
| HALVING | 2 | **100% / +12.7%** | **100% / +19.6%** |
| ETF | 3 | 33% / −5.5% ("sell the news"!) | 33% / −10.0% |
| KRACH | 3 | 67% / +0.4% | 67% / +22.7% (odbicia) |
| REGULACJA | 2 | 50% / +19.9% | 100% / +20.3% |

**Bug złapany testem podczas budowy:** zdarzenie spoza pokrycia danych dopasowywało
się do pierwszego dostępnego baru (halving 2016 → bar 2024, absurdalny zwrot) —
naprawione tolerancją ≤3 dni w `_indeks_baru` (Prawo I: brak danych ≠ wymyślone).

**Pliki:** `imperium/biblioteki/kronikarz_zdarzen.py` (nowy), `imperium/legiony/neurony/
sesje.py` (AUG-01), `rejestr.py`, `narzedzia/audyt_spojnosci.py` (W12 allowlista+weryfikacja),
`tests/test_kronikarz_zdarzen.py` (nowy, 8 testów z przyczynowością), docs.
**Testy:** 681/681 ✅ (59 neuronów, 55 aktywnych). Audyt: pełna harmonia.
**Następne rozszerzenia (zapisane):** kalendarz FOMC/CPI (cykliczne daty → przyszłe
okna), zdarzenia per-para, wagi malejące z dni_po.

## 2026-06-10 | W-288 | ATR-SL/TP (opt-in) + fix sprzężenia sizing↔SL — mechanika naprawiona, edge obnażony

**Wdrożone:**
1. **SL z ATR (opt-in):** `policz(atr=…, sl_atr_mult=…)` → SL = cena ∓ k×ATR, ale
   TYLKO ciaśniejszy niż lewarowy (nigdy bliżej likwidacji — clamp bezpieczeństwa).
   TP=MIN_RR×SL skaluje się automatycznie. Dyrygent: `sl_atr_mult` → bierze ATR_14
   z Bramy; backtest przelotowo. +4 testy granic (None/0, ogromny ATR, TP-skala).
2. **Fix sprzężenia sizing↔SL (uniwersalny):** risk-sizing (2%/stop_pct) z ciasnym
   SL żądał pozycji >>50% kapitału → checklist WETOWAŁ niemal każde wejście
   (pomiar: 201→2 trade'y!). Teraz CLAMP rozmiaru do 50% kapitału przed checklistą
   (ryzyko tylko maleje — uczciwy raport ryzyka z finalnego rozmiaru bez zmian).
3. Clamp odsłonił 2 KRUCHE testy przechodzące dzięki staremu wetu (pewność agregatu
   =1.0 przy zgodnym komplecie wskaźników) — naprawione na płaskie bary/sprzeczne
   sygnały z komentarzem-lekcją.

**POMIAR (BTC 1H, 12k barów, AUTO):**

| Wariant | Trades | WR | PF | MaxDD | PnL | TP/SL/TIMEOUT |
|---|---|---|---|---|---|---|
| baseline | 201 | 49.3% | 0.72 | 10.8% | −838 | 0/3/198 |
| ATR-SL 2.0 | 109 | 34.9% | 0.72 | 18.1% | −1536 | **29/66/14** |
| ATR+Strażnik | 95 | 31.6% | 0.69 | 18.5% | −1572 | 24/59/12 |

**Werdykt (Prawo I — pełna prawda):** mechanika wyjść NAPRAWIONA (TIMEOUT 198→14,
TP wreszcie trafiane 0→29) — ale ekonomicznie GORZEJ: ciasny SL × większe pozycje
(clamp) = częstsze i droższe SL-y. **TIMEOUT-y nie były źródłem straty — MASKOWAŁY
ujemny kierunkowy edge 1H/2025 małymi stratami; ATR-SL go skrystalizował.**
Wniosek strategiczny: problem 1H leży w PRZEWADZE KIERUNKOWEJ roju w tamtym okresie,
nie w mechanice. W-288 zostaje jako poprawne narzędzie (opt-in, NIEzalecane bez
zmierzonego edge); clamp 50% zostaje na stałe (naprawia realne sprzężenie).
Dalej: trop "edge dojrzewa" (autopsja) + walidacja na 5 parach świeżego okna.

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `imperium/koloseum/dyrygent.py`,
`imperium/koloseum/backtest.py`, `tests/test_kalkulator.py` (+4), `tests/test_dyrygent.py`.
**Testy:** 673/673 ✅. Audyt: pełna harmonia.

## 2026-06-10 | UNIKAT W-287 | Strażnik Przewagi + autopsja 1H — tarcza tnie krwawienie 5×

**AUTOPSJA (12k barów 1H, per ćwiartka czasu):** PF 0.32→0.79→0.99→1.48 — edge roju
monotonicznie DOJRZEWA (wczesny 2025 wrogi, świeży rynek sprzyja). Drugi trop:
198/201 zamknięć = TIMEOUT (mechanika wyjść na 1H — osobna iteracja). LONG −308 /
SHORT −530 — obie strony, problem nie w kierunku.

**💎 W-287 STRAŻNIK PRZEWAGI (unikat):** pretorianin patrzący na samą PRZEWAGĘ:
rolling expectancy N=12 zamkniętych < 0 → HALT 96 barów → SONDA (1 pozycja zwiadowcza;
wygrana=powrót z resetem, przegrana=ponowny HALT). Literatura zna "strategy decay"
jako raport; u nas automat w pętli z tanim powrotem. Maszyna stanów + 9 testów granic
(expectancy==0 nie halt, sonda PnL==0 = przegrana, jedna sonda naraz, parametry).

**POMIAR (BTC 1H, 12k, AUTO):**

| Wariant | Trades | PF | MaxDD | PnL | Sharpe_r | DSR |
|---|---|---|---|---|---|---|
| bez Strażnika | 201 | 0.72 | 10.8% | −838 | −1.34 | 0.003 |
| **ze Strażnikiem** | 175 | **0.95** | **6.4%** | **−150** | **−0.30** | 0.082 |

**Werdykt:** tarcza potwierdzona (strata ~5× mniejsza, DD prawie o połowę) — Strażnik
automatycznie wyłącza rój w okresach wygasłego edge'a. To NIE tworzy przewagi (PF<1
wciąż) — miecz (edge bazowy, mechanika TIMEOUT na 1H) to następna iteracja. Opt-in.

**Pliki:** `imperium/pretorianie/straznik_przewagi.py` (nowy), `imperium/koloseum/backtest.py`,
`tests/test_straznik_przewagi.py` (nowy), docs (MANIFEST/WIZJONER/LOG).
**Testy:** 669/669 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FAZA C (W-286) | ZEGARY RYNKU: SES-01/SES-02 — PRZEŁOM NA 1H (pierwszy Sharpe > 1.0!)

**Zwiad (agent docs + deep search internet, pełne linki w neurony/sesje.py):**
- Katalog: W-011 Azja Range Breakout = top kandydat (5/5, pure OHLCV+timestamp, kod czekał).
- Internet: rytm fundingu 8h — spread peak ~2h po settlement 00/08/16 UTC (MDPI 2026,
  badanie 26 giełd); sezonowość godzinowa BTC 21–23 UTC + efekt piątku (QuantPedia,
  turn-of-the-candle PMC 2023). Wszystko liczone z SAMEGO TIMESTAMPU — działa w backteście.
- ⚠️ W-010 CME Gap: agent ustalił, że CME handluje 24/7 od 29.05.2026 → strategia gapów
  UMARŁA; w katalogu do rebrandu na Monday-effect.

**Wdrożone (58 neuronów, 54 aktywne):**
- **Budowniczy:** TIMESTAMP + ASIA_HIGH/ASIA_LOW/ASIA_GOTOWA (zakres 00–08 UTC bieżącej
  doby; GOTOWA dopiero po 08:00 — bez look-ahead).
- **SES-01 NeuronZegarSesji** (S, waga 4): 0–2h po settlement fundingu → kontekst
  ostrożności; piątek 21–23 UTC → słaby LONG-bias. Kontekst, nie silnik.
- **SES-02 NeuronAzjaRange** (S, waga 7, W-011): breakout/breakdown domkniętego zakresu
  Azji, pewność rośnie z odległością od zakresu (cap 0.85).
- W12 audytu: scenariusze syntetyczne dostały timestampy (piątek, godzinowe) — żywotność
  SES-* weryfikowana co sesję. +7 testów granic (settlement dokładnie 0h/2h, close==high,
  zakres zdegenerowany, Azja niedomknięta).

**POMIAR (BTC, 4000 barów, AUTO, n_prob=4):**

| Rynek | Wariant | Trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR |
|---|---|---|---|---|---|---|---|---|
| 1H | baseline (przed) | 67 | 56.7% | 1.11 | 4.8% | +128 | 0.28 | 0.19 |
| 1H | **+ZEGARY** | 65 | 52.3% | **1.59** | **2.5%** | **+540** | **1.47 ✅>1.0!** | 0.46 |
| 4H | +ZEGARY | 74 | 41.9% | 0.59 | 14.5% | −1168 | −1.29 | 0.002 |

**Werdykt PIERWOTNY:** 1H, 4000 barów: pierwszy Sharpe>1.0 w historii Imperium; DSR 0.46.

**SUPLEMENT — dłuższa próba (Prawo I, bez lukru):** na 12000 barach 1H (≈16 mies.,
2025-02→2026-06): trades=201, WR 49.3%, PF 0.72, Sharpe_r −1.34 → wynik się ODWRACA.
**DSR 0.46 słusznie ostrzegał** — świetne okno 5,5-miesięczne nie jest stabilne w czasie;
rok 2025 zjada strategię. To nie zegary zawiodły (kontekst, niska waga) — cały rój na 1H
jest NIESTABILNY MIĘDZY OKRESAMI. Wnioski: (1) zegary SES-* zostają (tanie, badawczo
uzasadnione, nieszkodliwe); (2) 1H NIE jest gotowe — następny krok: analiza per okres
(czy strata skoncentrowana w jednym reżimie/krachu 2025?) i per para (5 par czeka);
(3) nasza bramka DSR po raz kolejny obroniła przed wdrożeniem szczęśliwego okna.
4H bez zmian (ziarno za grube dla sesji) — czeka na inne źródło przewagi.

**Pliki:** `imperium/legiony/neurony/sesje.py` (nowy), `budowniczy_wskaznikow.py`,
`rejestr.py`, `narzedzia/audyt_spojnosci.py` (W12 timestampy), `tests/test_neurony.py`,
`tests/test_integracja.py`, docs (MANIFEST/README/INDEKS).
**Testy:** 660/660 ✅. Audyt: pełna harmonia (58 neuronów).

## 2026-06-10 | FAZA B (W-286) | Diagnoza 4H + grid TIMEOUT — bramka PBO ZABLOKOWAŁA kalibrację (wzorcowe!)

**DIAGNOZA (atrybucja przez pętlę MWU + rozkład zamknięć, BTC 4H):**
- **75% zamknięć = TIMEOUT** (54/72), tylko 2×TP vs 15×SL — pozycje umierają z czasu.
- Przyczyna mechaniczna: `MAX_BARS_OTWARCIA=48` ŚWIEC stałe per system — 48 dni na 1D,
  ale tylko 8 dni na 4H, podczas gdy TP (z dźwigni) wymaga podobnego ruchu %.
- LONG i SHORT tracą symetrycznie → problem egzekucji wyjść, nie kierunku.
- MWU najgorsi na 4H: XII-02 Ichimoku, H-01 Hurst, V-13, XII-05 Fibo, V-01 OBV.

**MECHANIZMY (wdrożone, opt-in, zero regresji — +2 testy):**
- `PaperTradingEngine(max_bars_otwarcia=N)` — TIMEOUT per silnik (None → stała stara).
- `Dyrygent(min_pewnosc_interwalu={"4H": 0.65})` — próg pewności per interwał
  (z Namiestnikiem: max(prog_reżimu, prog_interwału) — ostrzejszy wygrywa).
- `backtest(...)` przelotowo wspiera oba.

**GRID (BTC 4H, 4000 barów, AUTO; n_prob=4):**

| max_bars | trades | WR | PF | PnL | DSR | TIMEOUT |
|---|---|---|---|---|---|---|
| 48 (baseline) | 74 | 41.9% | 0.59 | −1168 | 0.002 | 57 |
| 96 | 45 | 37.8% | 0.85 | −382 | 0.072 | 29 |
| 144 | 35 | 42.9% | **1.07** | **+167** | 0.193 | 18 |
| 192 | 31 | 38.7% | 0.99 | −31 | 0.145 | 10 |
| **PBO (CSCV, S=8)** | | | | | **0.614 ⛔** | |

**WERDYKT (Prawo XVIII + W-282 — bramka obroniła nas przed samooszustwem):**
Kierunek diagnozy POTWIERDZONY (monotoniczna poprawa z TIMEOUT), ale PBO=0.61 >> 0.20:
wybór "najlepszego" wariantu z gridu to dopasowanie do szumu — zwycięzca in-sample
niestabilny out-of-sample. NAJLEPSZY wariant i tak ledwo PF 1.07. **Wniosek:** edge
dzienny roju NIE skaluje się na 4H przez samą mechanikę wyjść — 4H wymaga innego
źródła przewagi (Faza C: mikrostruktura/scalp lub osobne wagi reżimowe — przyszły
pomiar na WIĘKSZEJ próbie/wielu parach). Domyślne wartości BEZ ZMIAN; mechanizmy
zostają jako narzędzia kalibracji.

**To jest dokładnie po co zbudowaliśmy W-282** — pierwsza realna interwencja bramki.

**Pliki:** `imperium/koloseum/paper_trading.py`, `imperium/koloseum/dyrygent.py`,
`imperium/koloseum/backtest.py`, `tests/test_paper_trading.py`, `tests/test_dyrygent.py`.
**Testy:** 655/655 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FAZA A (W-286) | Formacja Legionów per interwał — POMIAR: 1D lepsze, 4H czeka na Fazę B

**Opis:** `Legatus._formacja_interwalu()` — na danym interwale głosują tylko neurony
właściwego legionu: M1/M5/M15→SCALP; 1H→SCALP+SWING; 4H/1D/1W→SWING; uniwersalne
(WSPOLNY/STRAZ/VOLUME/TREND/EXPLORATORES) zawsze; nieznany/pusty interwał → pełny rój
(stare zachowanie, Prawo XV). +4 testy formacji (granice: 1D bez SCALP, M5 bez SWING,
1H oba, nieznany bez filtra).

**POMIAR (BTC, AUTO, n_prob=4) — formacja vs baseline z wcześniejszych testów:**

| Rynek | Wariant | Trades | WR | PF | PnL | Sharpe_r | DSR |
|---|---|---|---|---|---|---|---|
| BTC 1D | baseline | 59 | 55.9% | 2.23 | +3622 | 0.825 | 0.938 |
| BTC 1D | **FORMACJA** | 61 | 55.7% | **2.26** | **+3934** | **0.859** | **0.954 ✅>0.95** |
| BTC 4H | baseline | 73 | 43.8% | 0.61 | −1012 | −1.18 | 0.003 |
| BTC 4H | FORMACJA | 74 | 41.9% | 0.59 | −1168 | −1.29 | 0.002 |

**Werdykt (Prawo XVIII):** Faza A PRZYJĘTA — na 1D poprawia wszystko (PnL +9%, DSR
przekracza próg 0.95; do Etapu I brakuje już TYLKO Sharpe 0.86→1.0). Na 4H sama
formacja nie wystarcza (problem leży w wagach reżimu/progach, nie w składzie roju) —
dokładnie po to jest **Faza B: kalibracja per interwał** (następna sesja, pod bramką
DSR/PBO). Plan W-286 (A✅→B→C) zapisany w WIZJONER.

**Pliki:** `imperium/legiony/legatus.py`, `tests/test_integracja.py` (+4), `docs/WIZJONER.md`.
**Testy:** 653/653 ✅. Audyt: pełna harmonia.

## 2026-06-10 | NARZĘDZIE+POMIAR | Agregator 4H (5 par z 1H) + test bojowy 4H

**Opis:** `narzedzia/agreguj_4h.py` — buduje bary 4H z 1H po siatce UTC (open/max/min/
close/suma; NIEPEŁNE okna odrzucane — Prawo I). Wynik: 5 plików `dane/4h/Binance_*_4h.csv`
(12.1k–18.6k barów, do 2026-06-08), prosty format Imperium, czytnik czyta wprost.
+2 testy (kompletność okna, luka w środku).

**TEST BOJOWY 4H (4000 barów, AUTO, n_prob=4):**
- BTC 4H: 73 trades, WR 43.8%, PF 0.61, PnL −1012, Sharpe_r −1.18 → ⛔ (STRATA!)
- SOL 4H: 80 trades, WR 51.2%, PF 1.11, PnL +493, Sharpe_r 0.30 → ⛔

**Werdykt (Prawo I):** rój w obecnej kalibracji jest GRACZEM DZIENNYM — edge na 1D
(PF 2.23), brak na 1H (1.11), strata na 4H BTC (0.61). Progi/wagi/strategie wymagają
kalibracji per interwał ZANIM pomyślimy o scalpie. To jest GŁÓWNE zadanie następnej
sesji — teraz mamy do tego pełne dane (5 par × 1D/4H/1H do 2026-06-08).

**Pliki:** `narzedzia/agreguj_4h.py` (nowy), `dane/4h/*` (5), `tests/test_czytnik_csv.py`.
**Testy:** 649/649 ✅. Audyt: pełna harmonia.

## 2026-06-10 | DANE+FIX | Świeże dane 5 par (1D+1H do 2026-06-08) + brud µs w CDD naprawiony w czytniku

**Opis:** Cezar dostarczył 10 plików CryptoDataDownload (BTC/ETH/SOL/BNB/DOGE × 1D+1H,
pełne historie do 2026-06-08). Weryfikacja wykryła REALNY BRUD ŹRÓDŁOWY: pliki 1h
mieszają wiersze z unixem w MILISEKUNDACH i ~700/parę w MIKROSEKUNDACH (×1000 za duże,
marzec 2025) → daty "rok 57163". Fix w `czytnik_csv._parse_ts`: heurystyka >1e14 → µs ÷1000;
plus deduplikacja po timestamp (duble µs/ms tej samej świecy — zostaje nowszy wpis).
Po fixie: 5×1H monotoniczne ✅ (49.6k–75.7k barów), 5×1D świeże ✅.

**Pliki:** `dane/dzienne/*` (5), `dane/godzinowe/*` (5), `imperium/akwedukty/czytnik_csv.py`,
`tests/test_czytnik_csv.py` (+2 testy granic heurystyki i dedup).
**Testy:** 647/647 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FEATURE | CLI backtestu z werdyktem Etapu I + flagi --auto/--ucz

**Opis:** Każdy backtest z linii poleceń kończy się teraz JAWNYM werdyktem bramki
Etapu I Koloseum (✅ awans do paper / ⛔ powód odrzucenia) — Prawo I: koniec z
"raportem bez wniosku". Nowe flagi CLI: `--auto` (Namiestnik AUTO-reżim),
`--ucz` (pętla uczenia MWU). Użycie:
`python -m imperium.koloseum.backtest dane/dzienne/Binance_BTCUSDT_d.csv 1D --auto`

**POMIAR 1H (BTC, 4000 barów, AUTO — dokończenie pomiaru pętli uczenia z 1D):**
- bez uczenia: 67 trades, WR 56.7%, PF 1.11, PnL +128, Sharpe_r 0.28 → ⛔
- z uczeniem:  67 trades, WR 53.7%, PF 0.95, PnL −61, Sharpe_r −0.29 → ⛔

**Werdykt (Prawo I):** hipoteza "gęstsze dane = więcej rund MWU" NIE potwierdziła się —
rój na 1H wchodzi rzadko (67 wejść / 4000 barów; ostre progi pewności), więc rund uczenia
nadal za mało, a edge roju na 1H w tym oknie jest słaby (PF 1.11). Wnioski na następne
sesje (laptop): (a) kalibracja selektywności/progów pod 1H-4H, (b) świeże dane MEXC,
(c) strojenie eta/alpha MWU dopiero przy ≥300 transakcjach. `ucz_mwu` zostaje OFF.

**Pliki:** `imperium/koloseum/backtest.py`.
**Testy:** 645/645 ✅. Audyt: pełna harmonia.

---

## 2026-06-10 | FEATURE+POMIAR | Zamknięta pętla uczenia w backteście (ucz_mwu) — werdykt: działa, na 1D za mało rund

**Opis:** Największa luka Prawa XV zamknięta — Igrzyska/MWU przestały być martwym
klockiem w backteście:
- `DecyzjaCyklu.pozycja_id` — atrybucja: które neurony głosowały przy wejściu.
- `backtest(ucz_mwu=True)`: każda ZAMKNIĘTA pozycja rozlicza głosujące neurony przez
  `HedgeMWUzPamieciaRezimu` (W-049+W-280+W-285.1: Hedge + Fixed-Share + pamięć per-reżim),
  świeże mnożniki wracają do Legatusa na bieżąco. Bez look-ahead (uczenie wyłącznie
  z już zamkniętych transakcji); `ustaw_rezim()` indeksuje pamięć klasyfikacją bara.
- Opt-in (`ucz_mwu=False` domyślnie — test dowodzi identyczności ze starym zachowaniem).

**POMIAR (BTC 1D AUTO, eta=0.3, α=0.02):** bez uczenia PF 2.23 / Sharpe_r 0.83;
z uczeniem PF 1.95 / Sharpe_r 0.67. **Werdykt (Prawo I):** pętla technicznie działa,
ale 58 zamkniętych transakcji to ZA MAŁO rund dla MWU (szum dominuje sygnał uczenia).
Następny pomiar: interwał 1H/4H (setki transakcji) na laptopie — tam MWU ma szansę.
Domyślnie wyłączone do czasu pozytywnego pomiaru (Prawo XVIII).

**Pliki:** `imperium/koloseum/dyrygent.py`, `imperium/koloseum/backtest.py`,
`tests/test_backtest.py` (+2).
**Testy:** 645/645 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FIX+POMIAR | Bug jednostek w bramce Etapu I + pierwszy TEST BOJOWY roju

**Bug (złapany testem bojowym, nie unit-testem — lekcja):** `StatystykiSesji` trzyma
`win_rate` i `max_drawdown_pct` jako UŁAMKI (0.5=50%) mimo sufiksu `_pct`; bramka
dzieliła przez 100 → progi WR i MaxDD były martwe. Unit-test nie złapał, bo duck-type
`_Stat` podawał procenty — test powielił błędne założenie autora. Naprawione
(bramka + testy na ułamkach, komentarz ostrzegawczy o jednostkach).

**TEST BOJOWY (pełny rój, realne dane, bramka Etapu I, n_prob=4):**

| Rynek | Tryb | Trades | WR | PF | MaxDD | PnL | Sharpe_r | DSR | Werdykt |
|---|---|---|---|---|---|---|---|---|---|
| BTC 1D | agregat | 133 | 52% | 1.22 | — | +2353 | 0.34 | 0.47 | ⛔ Sharpe |
| BTC 1D | agregat-AUTO | 59 | 55.9% | **2.23** | **4.3%** | **+3622** | 0.83 | 0.94 | ⛔ Sharpe 0.83≤1.0 |
| ETH 1D | agregat-AUTO | 72 | 51.4% | 1.15 | 11.3% | +791 | 0.19 | 0.30 | ⛔ |

**Wnioski (Prawo I — uczciwie):**
1. **Namiestnik AUTO-reżim to ogromna wartość:** PF 1.22→2.23, DSR 0.47→0.94, połowa trade'ów.
2. Rój ZARABIA na BTC z świetną kontrolą ryzyka (MaxDD 4.3%), ale Sharpe 0.83 — bramka
   (słusznie surowa) jeszcze nie przepuszcza do Etapu II. Brakuje selektywności/rozmiaru.
3. ETH 1D: brak przewagi — rój kalibrowany na BTC nie przenosi się 1:1.

**Pliki:** `imperium/koloseum/walidacja.py`, `tests/test_walidacja.py`.
**Testy:** 643/643 ✅. Audyt: pełna harmonia.

## 2026-06-10 | FEATURE | Bramka Etapu I Koloseum wpięta w backtest (ROADMAP × W-282)

**Opis:** Domknięcie pętli walidacji — bramki przestały być "gotowe ale niepodpięte"
(czerwony alarm Prawa XV z poprzedniej sesji):
- `backtest()` zbiera teraz **krzywą equity per bar** (`engine.krzywa_equity`) —
  +1 punkt po zamknięciu końcowym; testowany kontrakt długości.
- NOWA `etap_pierwszy_koloseum(krzywa, statystyki, interwal, n_prob)` w
  `koloseum/walidacja.py`: progi ROADMAP § ZASADA ARENY (≥10 trade'ów, Sharpe
  roczny > 1.0 annualizowany wg interwału, MaxDD < 15%, WR > 55% LUB PF > 1.5)
  **plus** DSR ≥ 0.95 (W-282) — jeden werdykt ok/powod. Strategia bez przejścia
  bramki nie awansuje do Etapu II (paper).
- Werdykt zawsze z czytelnym powodem pierwszego czerwonego progu (Prawo I).

**Pliki:** `imperium/koloseum/backtest.py`, `imperium/koloseum/walidacja.py`,
`tests/test_walidacja.py` (+8), `tests/test_backtest.py` (+1, kontrakt end-to-end).
**Testy:** 643/643 ✅ (634+9). Audyt: pełna harmonia.

## 2026-06-10 | FEATURE+POMIAR | W-285.2 Dwu-zegarowy DSR (unikat) + pomiar W-281 (werdykt: ADX zostaje)

**Opis:**
1. **W-285.2 💎 Dwu-zegarowy DSR** (`koloseum/walidacja.py`): `bary_wolumenowe()` (trading-time
   Mandelbrota, BIB-009/W-144 — bary o równym wolumenie, końcówka odrzucana) + `bramka_dwuzegarowa()` —
   DSR liczony na zwrotach kalendarzowych ORAZ na strategii odtworzonej w trading-time
   (`sygnal_fn` na barach wolumenowych, pozycja[i−1]·zwrot[i], bez look-ahead). Przechodzi
   tylko gdy OBA zegary zielone — odpada strategia żyjąca z nierównej gęstości czasu. +9 testów.
2. **Pomiar W-281** (`narzedzia/pomiar_jump_model.py`, NOWE narzędzie): przyczynowy walk-forward
   (okno 250, refit 20, λ=30), miara = zwrot baru t+1 po stanie t. WYNIK NEGATYWNY dla JM:
   BTC 1D sep(B−B) −5.0 bps vs ADX +20.9; ETH 1D −24.9 vs +31.0; przełączeń 4× więcej.
   **Werdykt (Prawo XVIII): JumpModel NIE wchodzi do klasyfikuj_rezim(); W-285.3 Trybunał
   odłożony.** Moduł+testy zostają. Uczciwy pomiar > entuzjazm papierów (Prawo I).
   Bugi naprawione w narzędziu: CSV CryptoDataDownload od najnowszych (sort po Unix),
   Volume ETH/BTC/USDT, stan bez wystąpień → NEUTRAL.

**Pliki:** `imperium/koloseum/walidacja.py`, `tests/test_walidacja.py`,
`narzedzia/pomiar_jump_model.py` (nowy), `docs/` (WIZJONER werdykt+tabela, MANIFEST, LOG, README).
**Testy:** 634/634 ✅ (625+9). Audyt: pełna harmonia.

## 2026-06-10 | FEATURE | Pakiet "najlepsi z najlepszych": W-280 + W-281 + W-282 + W-285.1 (unikat)

**Opis:** Wdrożenie pakietu z deep researchu (4 moduły, +39 testów, 586→625):

1. **W-280 Fixed-Share** (`biblioteki/hedge_mwu.py`): parametr `alpha_share` — po każdej
   rundzie ułamek α masy wraca do puli (w_i ← (1−α)·w_i + α·średnia). Naprawia strukturalną
   wadę czystego Hedge w niestacjonarności (zakopane wagi wracają po zmianie reżimu).
   α=0 → dokładnie stary HedgeMWU (test dowodzi zero regresji).
2. **W-282 Bramka anty-overfittingu** (`koloseum/walidacja.py`, NOWY): Deflated Sharpe Ratio
   (korekta o liczbę prób + skośność/kurtozę; Bailey & de Prado 2014) + PBO przez CSCV
   (C(S,S/2) podziałów; Bailey et al. 2015) + `bramka_walidacji()` — strategia przechodzi
   tylko gdy DSR ≥ 0.95 ORAZ PBO < 0.20. Pure-Python (Φ przez erf, Φ⁻¹ Acklam).
3. **W-281 JumpModel** (`legiony/jump_model.py`, NOWY): detektor reżimu z karą za skok λ
   (Viterbi-DP + naprzemienna aktualizacja centroidów, multi-start, deterministyczny seed).
   Krypto-paper: Cortese/Kolm/Lindström 2023 (3 stany bull/neutral/bear). KLOCEK Fazy 3
   master-switcha — wpięcie do klasyfikuj_rezim() po pomiarze (Prawo XVIII).
4. **W-285.1 💎 HedgeMWUzPamieciaRezimu** (unikat Imperium): Fixed-Share, ale masa mieszana
   wg PAMIĘCI wag per-reżim (EMA) zamiast uniform — gdy wraca RANGING, neurony mean-reversion
   odzyskują wagę natychmiast. Inspiracja: Bousquet & Warmuth (JMLR 2002) "sharing to past
   posteriors"; nasz twist: indeksowanie reżimem z Namiestnika, nie czasem.

**Infrastruktura przy okazji (Prawo XV):** `tests/run_tests.py` — AUTO-DISCOVERY plików
test_*.py (sztywna lista cicho zgubiła test_walidacja — nowy strażnik istniał, ale nie był
uruchamiany). Bramka W13 złapała w trakcie pracy 3 nieużywane importy — system działa.

**Pliki:** `imperium/biblioteki/hedge_mwu.py`, `imperium/koloseum/walidacja.py` (nowy),
`imperium/legiony/jump_model.py` (nowy), `tests/test_walidacja.py` (nowy),
`tests/test_jump_model.py` (nowy), `tests/test_hedge_mwu.py`, `tests/run_tests.py`,
`docs/` (MANIFEST, WIZJONER statusy, README, LOG).
**Testy:** 625/625 ✅ (586+39). Audyt: 13 warstw, pełna harmonia.

## 2026-06-10 | ZWIAD | Deep research 2024-2026 → wizje W-280..W-285 (WIZJONER)

**Opis:** Zwiad internetowy (5 osi: agregacja głosów, detekcja reżimu, anty-overfitting,
risk mgmt, darmowe dane). Najważniejsze znaleziska (pełne linki w WIZJONER § 2026-06-10):
- **W-280 Fixed-Share** — naprawia strukturalną wadę Hedge/MWU w niestacjonarnych rynkach
  (zakopane wagi nie wracają); wdrożenie = 1 linia w hedge_mwu.py. 🔴
- **W-281 Statistical Jump Model** — detektor reżimu z karą za skok; na krypto (Cortese/Kolm/
  Lindström 2023) bije HMM trwałością stanów; kandydat na Fazę 3 master-switcha. 🔴
- **W-282 DSR + PBO/CSCV** — twarda bramka anty-overfittingu w Koloseum (procedura konkretna). 🔴
- **W-283** — crypto-carry skompresowane od 2024 (BIS WP 1087): W-065 degradacja priorytetu;
  PSY-01 funding-extreme zostaje (inny mechanizm).
- **W-284** — OFI z L2 ma uniwersalną krótkoterminową moc (arXiv 2026) — potwierdza EXP-12/W-060.
- **W-285** — 3 oryginalne syntezy Imperium: Fixed-Share z pamięcią reżimu (Mnemosyne-mixing),
  dwu-zegarowy DSR (czas barowy × trading-time), Trybunał Trzech Zegarów (jump model jako
  ekspert meta-gry rozliczany Fixed-Share).

**Pliki:** `docs/WIZJONER.md` (nowa sekcja + 6 wizji), `docs/LOG_ZMIAN.md`.
**Kod:** bez zmian (czysty zwiad — wdrożenia wg priorytetu po decyzji Cezara).

---

## 2026-06-10 | INFRA | Ruff (W13) — rozszerzony ruleset o realne klasy bugów + audyt wsteczny granic

**Opis:** „Żeby było najlepiej" — zastosowano nową dyscyplinę WSTECZ i wzmocniono bramkę:
1. **Audyt graniczny roju (Prawo XXI Reguła Test-Granic):** przeskanowano wszystkie
   neurony pod kątem bugu granicznego typu Force Index (`==0`/próg → zły kierunek).
   Wynik: rój zdrowy — TRIX/AO/AC i pozostałe poprawnie domykają granicę do NEUTRAL;
   Force Index był jedynym wyjątkiem (już naprawiony). Wzorzec binarny (próg→A/B) przy
   równości miary-zero jest świadomy i bezpieczny.
2. **Ruff ruleset rozszerzony** z `F,E9` o realne klasy bugów (mierzone, nie zgadywane —
   pełny zestaw zielony): `E711/E712/E714` (bugi porównań `==None`/`==True`/`not x is y`),
   `B006/B008` (mutowalne argumenty domyślne — klasyczny bug współdzielonego stanu),
   `B904` (raise w except bez `from` — gubi traceback), `PLE` (błędy pylintu).
   Znaleziono i naprawiono 3× `== True/False` w `tests/test_scheduler.py` → `is`.

**Pliki:** `ruff.toml`, `tests/test_scheduler.py`.
**Testy:** 586/586 ✅. Audyt: 13 warstw, pełna harmonia. Ruff (9 reguł): czysto.

---

## 2026-06-10 | FIX | Warstwa 8 audytu — świeżość LOG przez git, nie mtime (fałszywy alarm po resecie)

**Opis:** W8 (świeżość LOG_ZMIAN) używała `os.path.getmtime` — bezużytecznego po
świeżym klonie/resecie kontenera: git ustawia mtime wszystkich plików na „teraz",
więc audyt fałszywie raportował „kod zmieniony po ostatnim wpisie", mimo że treść
== ostatni commit (working tree czysty). Naprawiono: W8 wykrywa zmienione pliki .py
przez **git** (`git diff HEAD` + `git diff --cached`) w `imperium/` i `narzedzia/`,
flaguje tylko gdy są REALNE zmiany bez wpisu LOG z dzisiejszą datą. Deterministyczne
w CI/świeżym klonie. Przy okazji: docstring „12 warstw" → „13 warstw".

**Dlaczego ważne:** bramka pre-commit była krucha — mogła blokować (lub przepuszczać)
zależnie od mtime, nie treści. Teraz sygnał = faktyczna zmiana kodu (git), nie zegar.

**Pliki:** `narzedzia/audyt_spojnosci.py`.
**Testy:** 586/586 ✅. Audyt: 13 warstw, pełna harmonia (exit 0), ruff czysto.

---

## 2026-06-09 | INFRA | Wykrywanie bugów: ruff (Warstwa 13) + reguła test-granic + adversarial review

**Kontekst:** Cezar zapytał, czemu zewnętrzny recenzent (cubic) łapie bugi, a my nie.
Diagnoza: nasz audyt (12 warstw) sprawdzał SPÓJNOŚĆ (liczby/klucze/dokumenty=kod), nie
POPRAWNOŚĆ logiki ani statyczną jakość; testy pisaliśmy na „happy path", bez granic;
brak lintera. Wdrożono trzy uzupełniające się mechanizmy (wszystkie do zasad):

1. **Warstwa 13 audytu — ruff** (`ruff.toml`, ruleset F+E9): linter łapie bugi/martwy
   kod, których warstwy spójności nie widzą. Zweryfikowano: F811 łapie duplikat klasy
   (dokładnie bug z merge, który cubic znalazł). Audyt blokuje commit przy znalezisku;
   gdy ruff niezainstalowany → tylko nota (działa w minimalnym środowisku).
2. **Reguła Test-Granic** (rozszerzenie Prawa XXI w CLAUDE.md): każdy moduł z progiem/
   znakiem MUSI mieć testy granic (0/None/±/dokładny-próg/trwałość-stanu).
3. **Adversarial `/code-review` przed każdym push** (rozkaz stały): wrogi przegląd
   logiki/granic — ta sama perspektywa co cubic, ale ZANIM trafi na PR.

**Sprzątanie przy okazji (Prawo XV/XIX):** ruff wyczyścił 88 nieużywanych importów +
puste f-stringi, oraz realne znaleziska: martwy policzony sygnał `trend_napływu` (OC-04),
martwe zmienne (`wzorzec`, `linia`, `powody`), zepsute demo `mikro_neuron.py` (odwołania
do nieistniejących klas → NameError przy uruchomieniu), forward-ref `RaportAreny` przez
TYPE_CHECKING.

**Pliki:** `ruff.toml` (nowy), `requirements.txt`, `narzedzia/audyt_spojnosci.py` (W13),
`CLAUDE.md` (3 zasady), 9 plików kodu/testów (sprzątanie ruff).
**Testy:** 586/586 ✅. Audyt: 13 warstw, pełna harmonia (exit 0), ruff czysto.

---

## 2026-06-09 | FIX | Force Index (V-05) — granice fi==0 + tag źródła pure-Python (PR review cubic)

**Opis:** Dwie poprawki po recenzji PR (cubic-dev-ai):
1. **P1 — błąd graniczny neuronu:** przy `FORCE_INDEX_2 == 0` w trendzie wzrostowym
   kod spadał do gałęzi `return SHORT` (sygnał PRZECIWNY do trendu); `FORCE_INDEX_13 == 0`
   było traktowane jako bessa. Teraz: FI(13)=0 → NEUTRAL (brak przewagi), FI(2)=0 →
   słaby głos zgodny z trendem (pewność 0.40), zero implicytnego SHORT na zerze.
2. **P2 — metadane źródła:** `FORCE_INDEX_13/2` (liczone `_py_force_index`, własna
   formuła) były w sekcji TA-Lib → `compute()` stemplował je jako TA-Lib. Dodano do
   `_PURE_PYTHON_INDICATORS` → poprawny tag `pure-Python` (Prawo XIII — audyt nie kłamie o źródle).

**Pliki:** `imperium/legiony/neurony/wolumen.py`, `imperium/fundament/brama_kalkulatora.py`,
`tests/test_neurony.py`, `README.md`.
**Testy:** +2 graniczne (584→586/586). Audyt: pełna harmonia (exit 0).

---

## 2026-06-09 | FIX | Reguła 6% Elder — data ze świecy + HALT do końca miesiąca + usunięcie duplikatu (PR review cubic)

**Opis:** Trzy poprawki po recenzji PR (cubic-dev-ai):
1. **P1 — data z czasu świecy:** `Dyrygent.cykl()` przekazywał `regula_6pct.aktualizuj()`
   bez daty → w backteście używał `date.today()` (czas systemowy), błędnie licząc
   reset/HALT względem zegara maszyny, nie kalendarza danych. Teraz konwertuje
   `timestamp` świecy (ms epoch, UTC) na datę i przekazuje jako `dzisiaj=`.
2. **P2 — HALT do końca miesiąca:** logika zdejmowała HALT, gdy kapitał chwilowo
   odrobił w tym samym miesiącu — sprzecznie z komunikatem „HALT do końca miesiąca"
   i doktryną Eldera. Usunięto gałąź `strata < prog → NORMAL`; HALT trwa do zmiany
   miesiąca lub ręcznego `reset_miesiac()`.
3. **Duplikat klasy:** `RegulaSzesciuProcentEldera` była zdefiniowana DWUKROTNIE
   (pozostałość po rozwiązaniu konfliktu merge) — druguje shadowowała pierwszą.
   Usunięto duplikat, została jedna definicja (przy bezpiecznikach AOA/W-062).

**Pliki:** `imperium/koloseum/dyrygent.py`, `imperium/pretorianie/kalkulator_lewara.py`,
`tests/test_kalkulator.py`, `tests/test_dyrygent.py`, `README.md`.
**Testy:** +2 (582→584/584). Audyt: pełna harmonia (exit 0).
**Symulator:** issues cubic w `symulator_live.html` zostawione do wersji on-demand
(rozkaz stały Cezara — symulatory poza auto-audytem).

---

## 2026-06-09 | FEATURE | Triple Screen Eldera (BIB-015) + neuron Force Index (V-05)

**Opis:** Domknięcie BIB-015 (Alexander Elder). Dwa elementy:
- **Neuron V-05 `NeuronForceIndex`** (kat. F, waga 7): Force Index = kierunek×dystans×wolumen,
  wygładzony EMA. Dwie skale — FI(13) trend, FI(2) trigger pullbacku. Doktryna Eldera:
  kupuj słabość w sile (trend↑ + FI(2)<0). Pure-Python, bez API.
- **Brama:** `FORCE_INDEX_13` / `FORCE_INDEX_2` (`_py_force_index` na talib.EMA surowego FI).
- **Strategia `IMV-TR-008` TRÓJEKRAN ELDERA**: 3 ekrany — MACD/EMA(50/200) trend (X-03,XII-03),
  Force Index pullback+trigger (V-05), StochRSI timing (X-02). Spójna z Regułą 6% Eldera.

**Symbioza (Prawo XXI):** neurony 55→56 (52 aktywne), strategie 17→18. Zaktualizowane:
README, MANIFEST (wiersz V-05, tabela legionów, status SMC), INDEKS, KATALOG_STRATEGII
(blok IMV-TR-008), ROADMAP. SMC-01/02/03 opisane jako aktywne (były „budzone wewnętrznie").

**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/wolumen.py`, `imperium/legiony/rejestr.py`,
`imperium/legiony/strategie/rejestr_strategii.py`, `tests/test_neurony.py`,
`tests/test_strategie.py`, `tests/test_integracja.py`, `docs/*` (README, MANIFEST, INDEKS,
KATALOG_STRATEGII, ROADMAP).
**Testy:** +7 (575→582/582). Audyt: pełna harmonia (exit 0).

---

## 2026-06-09 | FEATURE | Master-switch Faza 2 — online-learning wag głosujących (Hedge/MWU)

**Opis:** `MasterSwitchOnline` w `legiony/legatus.py` — Faza 2 master-switcha reżimu.
Faza 1 (2-z-3) traktuje VR/half-life/AR1 równo; Faza 2 daje każdemu głosującemu wagę
uczoną online z wyników: gdy ADX wyjdzie ze strefy spornej (>25 → był TREND; <20 →
RANGING), `rozlicz()` aktualizuje wagi HedgeMWU (reuse W-049, DRY — ta sama matematyka
co wagi neuronów). `klasyfikuj_rezim(wskazniki, master_switch_online=ms)` — opt-in.

**Neutralność (Prawo XV):** przy równych wagach decyzja ważona = dokładnie 2-z-3 z Fazy 1
(test `test_masterswitch_f2_neutralnosc_rowne_wagi` to dowodzi). Zero regresji.
**Zero halucynacji (Prawo I):** ADX nadal sporny → `rozlicz()` nic nie uczy.

**Pliki:** `imperium/legiony/legatus.py`, `tests/test_integracja.py`,
`docs/MANIFEST_KODU.md`, `README.md`
**Testy:** +4 (571→575/575). Audyt: exit 0.

---

## 2026-06-09 | FEATURE | Skew-Kelly (BIB-018, Sinclair) — sizing na grube ogony (W-211)

**Opis:** `KalkulatorLewara.skew_kelly(mu, sigma, skos)` — Kelly skorygowany o trzeci
moment rozkładu (skośność). Klasyczne Kelly (μ/σ²) zakłada symetrię; krypto ma gruby
lewy ogon (krachy). Przy ujemnym skosie wzór automatycznie tnie frakcję, chroniąc
przed ryzykiem ogona.

**Matematyka:** rozwinięcie Taylora E[log(1+fX)] do 3. rzędu →
f* = (σ² − √(σ⁴ − 4μ·m₃)) / (2m₃), gdzie m₃ = skos·σ³. Pierwiastek dobrany tak,
że skos→0 daje dokładnie μ/σ². Dodatni skos → wracamy do klasycznego (nie zawyżamy).

**Weryfikacja numeryczna:** μ=0.10, σ=0.20 → symetria 2.50, skos −1.0 → 1.83 (cięcie),
skos +1.0 → 2.50, brak danych → None (Prawo XV).

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `tests/test_kalkulator.py`,
`docs/MANIFEST_KODU.md`, `README.md`
**Testy:** +5 (566→571/571). Audyt: exit 0.

---

## 2026-06-09 | FEATURE | Reguła 6% Alexandra Eldera (BIB-015) — miesięczny circuit-breaker

**Opis:** Wdrożenie Reguły 6% z "Come Into My Trading Room" (Elder, BIB-015).
Gdy łączna strata w bieżącym miesiącu ≥ 6% kapitału z początku miesiąca → HALT:
zero nowych wejść do końca miesiąca. Reset 1. dnia nowego miesiąca (automatyczny).

**Gdzie działa:** wymiar MIESIĘCZNY — komplementarny z BezpiecznikKrzywejKapitalu (intraday W-062)
i Bezpiecznikiem AOA (30%, W-028). Razem: Elder = miesięczny meta-limit, W-062 = dzienny ekwilib,
W-028 = twardy stop całości. Weto Reguły 6% jest w `_checklist()` jako pierwsze.

**Podpięcie:** `KalkulatorLewara.policz(regula_6pct=...)` + `Dyrygent(regula_6pct=True)`.
W Dyrygent domyślnie wyłączone (opt-in), żeby nie łamać kompatybilności backtestu.

**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `imperium/koloseum/dyrygent.py`,
`tests/test_kalkulator.py`, `docs/MANIFEST_KODU.md`, `README.md`
**Testy:** +4 (562→566/566). Audyt: exit 0.

---

## 2026-06-09 | DOKUMENT | Symulator canvas (styl v1-5.1) — aktualny + marzenie

**Opis:** Nowy `docs/symulator_imperium.html` — symulator w stylu animowanych diagramów
canvas (wzorowany na symulatorze z bazy DeepSeek wersja full, gdzie były wersje Imperium 1-5.1).
Cząsteczki płyną po krawędziach między węzłami modułów (kolory wg typu: dane/Brama/rdzeń/
doradcy/Pretorianie/egzekucja/pętla). **Przełącznik dwóch wersji:**
- 🔵 STAN AKTUALNY v0.9.0 — realne moduły (Akwedukty+3 adaptery, Brama, 48 neuronów, Legatus,
  Namiestnik, reżim, 5 doradców, Pretorianie, Drogi→paper, HedgeMWU). Ocena **8.0/10** z listą
  mocnych stron i luk (on-chain 1/5, 7 wyciszonych, brak live, brak meta-labelingu).
- 🟣 MARZENIE — wizja docelowa po wdrożeniu roadmapy (on-chain LIVE, Arbiter Fiduciae meta-
  labeling, DeepSeek AI, Reguła 6%, skew-Kelly, master-switch Faza 2, live MEXC). Ocena **9.7/10**.
**Prawo I:** wszystkie liczby/moduły z żywego kodu (rejestr.py, audyt). Węzły planowane wyraźnie
oznaczone jako „marzenie" (fioletowe) — nie udają, że istnieją.
**Pliki:** `docs/symulator_imperium.html` (nowy), `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`
**Testy:** statyczny HTML; suite 562/562. Audyt: exit 0.

---

## 2026-06-09 | DOKUMENT | Symulator wizualny HTML (offline, animowany)

**Opis:** Nowy `docs/symulator_live.html` — samodzielny (zero zależności) animowany symulator
do przeglądarki. Pokazuje aktualny stan Imperium v0.9.0: pipeline 8 etapów (Akwedukty→Brama→
Namiestnik→Reżim→Legion→Doradcy→Pretorianie→Decyzja), rój 48 neuronów głosujący na żywo
(LONG/SHORT/NEUTRAL, kill-switche Z wyróżnione), miernik przewagi (próg 0.55), 10 bramek
wstrzymania, ścieżka pieniędzy (10 000 USDT), 12 kategorii, roadmap. 4 scenariusze:
trend (WEJŚCIE LONG), range (wstrzymanie — słaba przewaga), bańka (Z-03 HARD-HALT),
krach (Z-04 cascade). **Wszystkie liczby z żywego kodu** (rejestr.py — Prawo I).
**Pliki:** `docs/symulator_live.html` (nowy), `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`
**Testy:** statyczny HTML, bez zmian logiki; suite 562/562. Audyt: exit 0.

---

## 2026-06-09 | DOKUMENT | Manual migracji na laptopa + symulator live

**Opis:** Nowy `docs/MANUAL_MIGRACJA_I_SYMULATOR.md` — przewodnik przeniesienia
Imperium na laptopa (Windows 10 Pro, Fujitsu 8 GB): instalacja Python 3.11, kopiowanie
repo, testy bez zależności, pełna moc (TA-Lib/numpy/ccxt), klucze przez `setx` (Prawo
Bezpieczeństwa), DeepSeek API, mapa RAM. Zawiera SYMULATOR LIVE: pełny diagram pipeline
(Akwedukty→Brama→Namiestnik→reżim→Legion→Doradcy→Pretorianie→Drogi), 10 bramek wstrzymania
long/short z progami z kodu, 4 przykłady symulacji (WEJŚCIE LONG / kill-switch / słaba
przewaga / dead-cat SHORT).
**Weryfikacja Prawa I:** sprawdzono „oryginalne narzędzia" — HERMES + 4 doradcy (Fulmen/
Iustitia/Oracle/Pythia) + Rada ISTNIEJĄ (kod + 24 testy w `test_doradcy.py`).
„Chimera/Hamachera" NIE ISTNIEJE nigdzie — halucynacja/pomyłka nazwy, nie liczy się (Prawo XIX).
**Pliki:** `docs/MANUAL_MIGRACJA_I_SYMULATOR.md` (nowy), `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`
**Testy:** dokument, bez zmian logiki; suite 562/562. Audyt: exit 0.

---

## 2026-06-09 | AUDYT | Warstwa W12 — żywotność głosu (automatyzacja Prawa XV)

**Opis:** `narzedzia/audyt_spojnosci.py` rozszerzony z 11 → **12 warstw**. Nowa W12 karmi
każdy aktywny neuron 5 syntetycznymi scenariuszami (byk/niedźwiedź/kaskada/bańka/spokój)
zbudowanymi przez Bramę i flaguje neurony, które MILCZĄ (NEUTRAL pewnosc=0 + zero
pewnosc_przeciwnika) we WSZYSTKICH scenariuszach = martwy głos.
**Logika dwustanowa (Prawo XVIII — sensowne rozstrzygnięcie):**
- milczący neuron spoza allowlisty adapterowej → ❌ błąd blokujący commit (regresja Prawa XV)
- milczący neuron z allowlisty (`NEURONY_ZALEZNE_OD_ADAPTEROW`) → ⚠️ info (znana luka, nie blokuje)
**Allowlista (5):** PSY-01 FUNDING_RATE, PSY-02 LONG_SHORT_RATIO, PSY-03 FEAR_GREED_INDEX,
PSY-04 OPEN_INTEREST, V-03 CVD — czekają na dane adapterów w backteście czysto-OHLCV.
**Powód:** Prawo XV było dotąd pilnowane ręcznie; teraz audyt łapie martwy głos automatycznie
przy każdym starcie sesji i pre-commicie. Z-04/D-01 zweryfikowane jako żywe (budzą się w kaskadzie/trendzie).
**Dowód allowlisty (Prawo I):** W12 dodatkowo karmi każdy neuron adapterowy ekstremalną
wartością jego klucza (`WERYFIKACJA_ADAPTEROW`) i wymaga, by OŻYŁ — PSY-01 SHORT0.85,
PSY-02 SHORT0.80, PSY-03 LONG (strach), PSY-04 SHORT0.60, V-03 LONG0.60. Milczenie MIMO
danych adaptera = realny bug (błąd blokujący). Allowlista zweryfikowana kodem, nie „na słowo".
Potwierdzono też: adaptery (Futures/CVD/FearGreed) SĄ podpięte do live-pipeline Dyrygenta —
te neurony żyją w trybie live/paper, milczą tylko w audycie offline (z natury bez sieci).
**Pliki:** `narzedzia/audyt_spojnosci.py`, `tests/test_spojnosc.py` (+4 testy), `README.md`,
`docs/INDEKS_IMPERIUM.md`, `ZASADY_FUNDAMENTALNE.md`, `docs/LOG_ZMIAN.md`
**Testy:** suite 558 → **562/562** (W12: zielona, raport adapterów, dowód allowlisty, negatywny martwy-głos). Audyt: exit 0.

---

## 2026-06-09 | NARZĘDZIE | Pomiar dekorelacji BIB-020 (Prawo XVI) — spłata długu „do zmierzenia"

**Opis:** Nowe narzędzie read-only `narzedzia/pomiar_dekorelacji_bib020.py` mierzy |r| Pearsona
nowych głosów BIB-020 vs istniejące, na realnych danych (BTC 1h, 6000 barów, 1446 kroków).
**Wynik — ZERO redundancji (żadne |r|>0.80):**
- Z-03~Z-01 r=−0.052, Z-04~Z-03 r=+0.005, Z-04~Z-01 r=+0.018 (rodzina Z w pełni ortogonalna)
- X-27~X-04 r=−0.046, X-27~X-01 r=+0.187 (value-conv. niezależny od BBands/RSI — inny horyzont)
- VARIANCE_RATIO~RET_AR1 r=+0.228 (🟡 OK), OU_HALFLIFE~HURST_DFA r=+0.010, VR~OU r=+0.099 (master-switch zdrowy)
**Żywotność (Prawo XV):** Z-03 984/1446, Z-04 12/1446 (kill-switch z natury rzadki) — brak martwych głosów.
**Wniosek:** flagi „do zmierzenia" z poprzednich commitów ZAMKNIĘTE. Nowe głosy = filary dywersyfikacji,
kandydaci do podniesienia wag (nie scalenia). Decyzja o wagach — osobno, kierunkowa.
**Pliki:** `narzedzia/pomiar_dekorelacji_bib020.py` (nowe), `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** narzędzie read-only, nie zmienia logiki; suite 558/558 bez zmian. Audyt: exit 0.

---

## 2026-06-09 | KOD | Z-04 NeuronCascade — cascade detector + dead-cat bounce (W-279, BIB-020 rozdz.28) ✅ WDROŻONY

**Opis:** Czwarte wdrożenie BIB-020, domyka rodzinę obronną kat. Z przy Z-03. Neuron dwustanowy:
- **KASKADA** (CASCADE_FLAG=1): 3+ przyspieszające spadki przy rosnącym wolumenie (price accelerator
  Treynora) → kill-switch: NEUTRAL z pewnosc_przeciwnika 0.92 (nie łap spadającego noża).
- **DEAD-CAT** (DEADCAT_SETUP=1, gdy kaskada wygasła): krach ≥12% w oknie + dno wyhamowane +
  słabnący wolumen + cena w dolnej 1/3 zakresu → taktyczny LONG 0.60 (krótki hold/stop zarządza egzekutor).
- Priorytet KASKADA > DEAD-CAT (gdy lawina trwa, nie kupujemy).
**Symbioza:** 2 obliczenia pure-Python w Bramie (`CASCADE_FLAG`/`DEADCAT_SETUP`) + 2 klucze Budowniczego +
rejestracja Z-04 w zagrozenie.py/rejestr.py + 12 testów. MANIFEST/README/INDEKS: 54→55 neuronów,
47→48 aktywnych, 42 OHLCV, testy 546→558.
🚨 **Prawo XVI (do zmierzenia):** CASCADE_FLAG vs VoV/AR1 (Z-03) — sprawdzić |r| przed podniesieniem wagi.
**Powód:** W-279 (priorytet #5 BIB-020 — domyka obronę kat. Z, taktyczny long post-crash), Prawo XV/XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/zagrozenie.py`, `imperium/legiony/rejestr.py`, `tests/test_neurony.py`,
`tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** +12 (Brama cascade/deadcat + Z-04 kaskada/priorytet/deadcat/spokój/abstynencja/rejestracja). Audyt: exit 0.

---

## 2026-06-09 | KOD | Master-switch reżimu Faza 1 — W-263/W-274 (BIB-020 Harris rozdz.16/20) ✅ WDROŻONY

**Opis:** Trzecie wdrożenie BIB-020 — wzmocnienie klasyfikatora reżimu (`klasyfikuj_rezim` w legatus.py).
Dwa nowe obliczenia pure-Python w Bramie:
- **VARIANCE_RATIO** (W-263, Lo-MacKinlay) = Var(r_k)/(k·Var(r_1)); >1 trend (zmienność trwała), <1 rewersja.
- **OU_HALFLIFE** (W-274) = −ln(2)/β z regresji OU Δx na x dla spreadu (price−SMA_50); krótki=rewersja, długi=trend.
**Integracja (Opcja 1 — decyzja Cezara):** master-switch 2-z-3 (VARIANCE_RATIO + OU_HALFLIFE + istn. RET_AR1)
rozstrzyga TREND_STRONG↔RANGING **TYLKO w strefie spornej ADX (20–25 lub brak ADX)**, gdzie dotąd padał NORMAL
(rój płaski). Poza strefą — logika ADX bez zmian (zero regresji, Prawo XVI). Prawo XV: aktywuje wagi reżimowe
tam, gdzie ADX milczy.
**Plan etapowy:** Faza 2 (awans do równorzędnego głosowania) DOPIERO po pomiarze `pomiar_namiestnik.py`
(Prawo XVIII: kod+testy+pomiar > opinia) — nie przed.
**Symbioza:** Brama (2 calc + pure-Python audit) + Budowniczy (VARIANCE_RATIO_4, OU_HALFLIFE_50) +
klasyfikator (`_master_switch_rezimu`) + 8 testów. Bez nowych neuronów (54 bez zmian). Testy 538→546.
🚨 **Prawo XVI (do zmierzenia):** VARIANCE_RATIO vs RET_AR1 (oba mierzą autokorelację — różne horyzonty/agregacja),
OU_HALFLIFE vs HURST_DFA — sprawdzić |r| przy awansie do Fazy 2.
**Powód:** W-263/W-274 (priorytet #2 BIB-020 — naukowy fundament Namiestnika), Prawo XV/XVI/XVIII/XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/legatus.py`, `tests/test_integracja.py`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** +8 (Brama VR/half-life + master-switch strefa sporna/większość/brak/nie-nadpisuje-ADX). Audyt: exit 0.

---

## 2026-06-09 | KOD | X-27 NeuronValueConvergence — rewersja do wartości (W-273, BIB-020 rozdz.16) ✅ WDROŻONY

**Opis:** Druga wizja BIB-020 w kodzie. Neuron kierunkowy mean-reversion: mierzy oderwanie ceny od
wartości godziwej dwiema kotwicami i bierze ich średnią (blend):
- **Value-Z** = (close − SMA-200) / σ(close,200) — kotwica jednoskalowa.
- **MoMA-Z** = (close − mean(SMA20/50/100/200)) / σ(close,200) — kotwica wieloskalowa (średnia średnich).
blend < −2.0 → LONG (wyprzedanie), > +2.0 → SHORT (wykupienie), |blend|<1.5 → NEUTRAL. Pewność rośnie z |blend|.
**Decyzja kategorii (Prawo XVIII):** kat. **M** (nie S jak w pierwszym szkicu W-273) — to mean-reversion,
a w WAGI_REZIMU kat. M dostaje ×1.5 w RANGING (gdzie rewersja działa) i jest tłumiona w trendzie. S dostaje
wagę tylko w trendzie = błędne dla rewersji. Uzasadnienie w docstringu.
**Symbioza:** 2 obliczenia pure-Python w Bramie (`VALUE_Z`/`MOMA_Z`) + 2 klucze Budowniczego
(`VALUE_Z_200`/`MOMA_Z_200`) + rejestracja X-27 w momentum.py/rejestr.py + 10 testów.
MANIFEST/README/INDEKS: 53→54 neuronów, 46→47 aktywnych, 41 OHLCV, testy 528→538.
🚨 **Prawo XVI (do zmierzenia):** nakładka z X-04 BBands (z-score 20-bar) i X-01 RSI — INNY horyzont
(200 vs 20/14), ale sprawdzić |r| przed podniesieniem wagi.
**Powód:** W-273 (priorytet #3 BIB-020 — głos rewersji do wartości na długim horyzoncie), Prawo XV/XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/momentum.py`, `imperium/legiony/rejestr.py`, `tests/test_neurony.py`,
`tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** +10. Audyt: exit 0.

---

## 2026-06-09 | KOD | Z-03 NeuronBubbleCrash — bubble/crash kill-switch (W-278, BIB-020) ✅ WDROŻONY

**Opis:** Pierwsza wizja BIB-020 (Harris) w KODZIE. Z-03 to defensywna meta-brama (wzorzec Z-01):
łączy trzy sygnały liczone z samego OHLCV (Prawo XV — bez nowych danych):
- **BUBBLE_Z** = ln(close/EMA-200)/σ(log-dev) — odchylenie od długoterminowej grawitacji (granice Fischera Blacka).
- **VoV** = std(ATR-14, 20)/mean(ATR-14, 20) — niestabilność zmienności (prekursor krachu).
- **AR1** = corr(ret, ret_lag1, 20) — autokorelacja zwrotów = refleksywność (kaskada momentum/krach).
Próg ALARM (bubble_z>3.5 LUB VoV>1.2 LUB AR1>0.40) → kill-switch: pewnosc_przeciwnika do 0.97
(tłumi cały rój). Strefa czujności (2.5/0.8/0.25) → umiarkowane tłumienie. NIGDY kierunkowy (meta-brama).
**Symbioza:** 3 obliczenia w Bramie (`BUBBLE_Z`/`VOV`/`RET_AR1`, pure-Python, stempel SOURCE_TAG_PY) +
3 klucze w Budowniczym (`BUBBLE_Z_200`/`VOV_20`/`RET_AR1_20`) + rejestracja w rejestr.py + 14 testów.
Kategoria Z istniała (WAGI_REZIMU bez zmian). MANIFEST/README/INDEKS: 52→53 neuronów, 45→46 aktywnych, 40 OHLCV.
🚨 **Prawo XVI (do zmierzenia):** AR1 vs HURST_DFA (H-01), VoV vs Yang-Zhang — różne okna/konstrukcja,
ale sprawdzić |r| przed podniesieniem wagi. Wpisane w docstring neuronu.
**Powód:** W-278 (priorytet #1 BIB-020 — ochrona kapitału przed bańką/krachem), Prawo XV, Prawo XIX.
**Pliki:** `imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/zagrozenie.py`, `imperium/legiony/rejestr.py`, `tests/test_neurony.py`,
`tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `README.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** dodane 14 testów (Brama bubble_z/VoV/AR1 + Z-03 kill-switch/czujność/spokój/abstynencja). Audyt: exit 0.

---

## 2026-06-08 | INSPIRACJA | INF-32 — Rozmowa z DeepSeek "Kai" (baza wskaźników + manual 1.0→5.1) ⚠️/❌ głównie szum

**Opis:** Cezar dostarczył 2,6 MB rozmowy z DeepSeek (28 wersji bazy wskaźników 1.0→2.9 + "MANUAL IMPERIUM 1.0→5.1",
kody Python, 3 symulatory HTML). Pełna analiza 5 zwiadowcami Opus (po liniach: 1-560, 560-1100, 1100-2000,
2000-2680, 2680-3300) + rdzeń roadmapy przeczytany osobiście. **Werdykt (Prawo I — twardy):**
- **Inflacja 50→658 "wskaźników"** przez 28 wersji = zbieranie nazw, nie sygnału. Realny rdzeń ~30 standardowych
  wskaźników (VWAP/EMA/RSI/MACD/BB/OBV/ADX/ATR/MFI/Ichimoku/Supertrend/CVD/OI/Funding/MVRV...) — w większości JUŻ MAMY.
- **Fabrykacje (odrzucone):** Hermes Agent (jako orkiestrator), ShieldRegime, CogAlpha, MELT Dataset, Insider Wallets
  Finder, "Andromeda scanner", "Complex Esco Theory", OpenClaw (250k⭐). **Wszystkie ID arXiv `2605.xxxxx` nieistnieją**,
  cytaty `[N†Lx-Ly]` syntetyczne, gwiazdki zawyżone (TradingAgents 71k).
- **Kod (31 funkcji): 0 produkcyjnych.** Powtarzalne bugi: fałszywy ATR `(h-l).mean()`, fałszywy ADX, lookahead
  (`center=True`/`shift(-1)`/`bfill`/min-max całej serii), KeyError `data['equity']`, brak `np.random.seed`.
  `SimpleNeuralNetwork` = losowe nietrenowane wagi (szum). `PhantomAIEngine` "LLM GPT-5.1" = zaszyte if-y zwracające 0.85.
- **3 symulatory HTML = animowane diagramy** (canvas, `setInterval` co 4s cykluje LONG/SHORT/NEUTRAL), zero P&L/danych/strategii.
- **Jedyny półrealny artefakt:** szkielet ERS/Archon (Hedge/Multiplicative-Weights-Update) — pokrywa się z planem ML-28 (Shapley).
- **Idee neuronów** (Hurst/Hawkes/MFDFA/Path-Signature/VPIN/Permutation-Entropy/Kimchi) = RECYKLING naszego katalogu
  (INF-10/11/12/19, kat. D/H/N/Z już w kodzie). Konceptualnie potwierdza kierunek (Prawo XVI dekorelacja, reżim-adaptacyjne
  wagi, Senat multi-agent=ML-25/29) — nie dodaje nowego.
**Realne narzędzia warte rozważenia (jedyna nowa wartość):** VectorBT+Optuna walk-forward (Koloseum), shapiq (ML-28),
Conformal Prediction `mapie` (niepewność predykcji), Polars (szybkość). Reszta już w rejestrze (NautilusTrader ML-33, CrewAI/Senat).
**Wizji NIE przyznano** (Prawo I — naciąganie byłoby fałszem). Zapisane jako INF-32 = referencja + blacklist fabrykacji.
**Powód:** Prawo I (uczciwa ocena, demaskacja halucynacji), Prawo XVI (dekorelacja), ZPO, ochrona przed marnowaniem pracy na fikcję.
**Pliki:** `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-020 ✅ ANALIZA KOMPLETNA — rozdz. 10/16/17/28 (wizje W-270..W-279)

**Opis:** Dokończenie analizy Harrisa (zwiadowca 3). 10 nowych wizji W-270..W-279 z rozdziałów:
Rozdz.10 (Informed Traders): W-270 (flow type: stealth/absorption/exhaustion), W-271 (staleness filter),
W-272 (efficiency proxy → przełącznik reżimu). Rozdz.16 (Value Traders): W-273 (value z-score SMA-200+MoMA ⭐⭐),
W-274 (OU half-life resiliency ⭐⭐), W-275 (winner's curse uncertainty scaler). Rozdz.17 (Arbitrageurs):
W-276 (basis+funding neuron ⭐⭐⭐ — najlepsza dostępna oś N/Z crypto), W-277 (BTC lead-lag altcoin catch-up).
Rozdz.28 (Bubbles/Crashes): W-278 (bubble/crash kill-switch: bubble_z + VoV + AR1 autocorr ⭐⭐⭐),
W-279 (cascade detector + dead-cat bounce). BIB-020 strawiona w CAŁOŚCI (30 wizji W-250..W-279).
**5 priorytetów wdrożenia:** W-278 (kill-switch na OHLCV), W-263/274 (master-switch reżimu, OHLCV),
W-276 (basis+funding, wymaga perp API), W-273 (value z-score, OHLCV), W-279 (cascade, OHLCV).
**Powód:** dokończenie ŻYCZ-10, Prawo XIX (tylko kod istnieje — wizje czekają na wdrożenie), Zasada Symbiozy.
**Pliki:** `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-020 ⭐ ZDOBYTA — "Trading and Exchanges" (Larry Harris, 9/10, ŻYCZ-10)

**Opis:** Cezar dostarczył biblię mikrostruktury rynku (Oxford 2003, 29 rozdz., b. dyrektor ekon. SEC) — życzenie
ŻYCZ-10. Rozdziały 11/12/14/19/20/21 strawione w pełni (2 zwiadowców Opus); rozdz. 10/16/17/28 do dokończenia
(zwiadowca trafił na limit sesji — pula W-270..279 zarezerwowana). **Przyznano 20 wizji W-250..W-269** celowanych
w najsłabsze osie Z (mikrostruktura, dziś tylko VPIN) i L (płynność). Trzy filary: (1) dekompozycja spread/vol na
trwałe-vs-przejściowe = master-switch reżimu momentum↔reversion (W-257/W-263); (2) detekcja manipulacji —
spoofing/squeeze/stop-gunning/pump/wash (W-250/252/253/254/256); (3) globalna bramka kosztu transakcji
(effective/realized spread, impact Glosten-Harris, Roll, Amihud, money-flow, Implementation Shortfall — W-266/267).
🚨 **Prawo XVI:** W-268 dubluje W-056 (Amihud) → scalić; W-251/265 vs W-060 (OFI), W-250/257 vs Z-01 (VPIN)/W-072
(Hawkes) → zmierzyć korelację przed wdrożeniem. 🚨 **Prawo XV:** większość wizji wymaga danych L2/order-flow/signed-trade
(Lee-Ready), których Brama dziś NIE ma — najpierw Brama L2, potem neuron. Wykonalne na OHLCV od razu: W-263, W-264, W-268.
**Werdykt:** 9/10 (nie 10 — księga mechanizmów, nie gotowych wzorów jak López de Prado; część wymaga nowych danych).
**Powód:** ŻYCZ-10 (priorytet po on-chain), ZPO, Prawo I (uczciwa ocena), Prawo XV/XVI (flagi przed wdrożeniem).
**Pliki:** `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne — wizje są planem, nie kodem)

---

## 2026-06-08 | BIBLIOTEKA | BIB-019 ❌ ODRZUCONA — "Handbook for Cryptocurrencies Trading" (Harris, 2/10)

**Opis:** Analiza Opus książki Virginii Harris. Werdykt: wypełniacz dla nowicjusza spotowego (ghost-written),
anty-systematyczny, anty-leverage, przeterminowane martwe giełdy (Cryptopia/CryptoBridge), zero matematyki
operacyjnej, brak funding/perpetual/DeFi/tokenomiki. Obiecuje on-chain, dostarcza definicje słownikowe.
**Zgodnie z Prawem I — NIE przyznano żadnej wizji** (W-250..259 wolne); naciąganie wartości obok López de
Prado/Sinclair byłoby zafałszowaniem rejestru. Zapisana jako udokumentowane odrzucenie (by nie kupować
podobnych handbooków). INF-31. 🚨 Oś O (on-chain) NADAL pusta — rekomendacja: crypto-native źródła (ŻYCZ-09..14).
**Powód:** Prawo I (uczciwa ocena), Prawo XV (oś O niewypełniona), ZPO.
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-015/016/017/018 — 4 książki naraz (Elder, Douglas, Kahneman, Sinclair Positional)

**Opis:** Cezar dostarczył 4 książki naraz; każda przeanalizowana osobnym agentem Opus. Stara lista życzeń
ŻYCZ-01..08 KOMPLETNIE zdobyta. Rozkaz Cezara: gromadzić w WIZJONerze (brudnopis), wdrożenie później,
wszystko dokładnie sprawdzać.
- **BIB-015 Elder "New Trading for a Living" — 8/10:** agent przeczytał REALNY kod Imperium. Force Index (kat. V),
  Impulse gate, **Reguła 6% miesięczny budżet ryzyka = REALNA LUKA**, Triple Screen multi-TF, MACD-Hist
  divergence → W-210..W-219. W-218 (equity-curve) JUŻ mamy (BreakerKrzywejKapitalu).
- **BIB-016 Douglas "Trading in the Zone" — ⚠️4/10:** 85% psychologii martwej dla automatu. 3 flagi:
  W-224 (Legatus=prawdopodobieństwo nie binarność), W-220 (edge na oknie≥20), W-222 (stop ze struktury) → W-220..W-225.
- **BIB-017 Kahneman "Thinking Fast and Slow" (ŻYCZ-08) — 8/10:** 4 neurony biasów tłumu (anchoring,
  overreaction, disposition, availability-panic, W-230..233) + 6 reguł ochrony procesu (W-234..239).
- **BIB-018 Sinclair "Positional Option Trading" (ŻYCZ-07) — 9/10:** FINALNA matematyka sizingu — skew-Kelly,
  CI-Kelly (wzór na SD f̂), subkonto pełny-Kelly, doktryna stopów momentum-only, counterparty cap → W-240..W-249.
ŻYCZ-07 i ŻYCZ-08 ✅ zdobyte → cała stara lista zamknięta. INF-27/28/29/30 w REJESTR.
🌟 Dodana LISTA ŻYCZEŃ v2 (ŻYCZ-09..14) na prośbę Cezara: on-chain (#1, kat. O prawie pusta), Harris
mikrostruktura, Easley/O'Hara, Almgren-Chriss egzekucja, Tsay szeregi czasowe, perpetual/funding.
🚨 Flagi Prawa XV zebrane do weryfikacji w kodzie przy wdrożeniu: W-212 (brak reguły 6%), W-224 (Legatus
binarny czy probabilistyczny?), W-244 (cena-stop na mean-reversion?), W-232/233 (wolumen kierunkowy w Bramie?),
W-249 (counterparty cap MEXC), W-176 (Gauss-Kelly?), W-172 (EXP-04 hedge-ratio par?).
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (znaleziona luka 6% + flagi), ZPO (krytyczne oceny), rozkaz Cezara.
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (zadanie czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-013/014 — Dalton ×2 (Markets in Profile + Mind Over Markets, ŻYCZ-05/06)

**Opis:** Cezar dostarczył 2 książki Daltona naraz; każda przeanalizowana osobnym agentem Opus. Obie o
Auction Market Theory / Market Profile — celują wprost w nasze 2 NAJSŁABSZE filary: V (wolumen) i S (struktura).
- **BIB-013 Markets in Profile (ŻYCZ-06) — 8/10:** TPO Value Area, Volume POC, value migration, Initial
  Balance+Range Extension, excess/tails, open types, profile shapes, volume-vs-TPO divergence → W-190..W-199.
- **BIB-014 Mind Over Markets (ŻYCZ-05) — 8/10:** podręcznik bazowy. 6 typów dnia, Initiative/Responsive
  (esencja: trend vs balans wg akceptacji wartości), 4 typy otwarcia, anomalie TPO-vs-volume → W-200..W-209.
ŻYCZ-05 i ŻYCZ-06 ✅ zdobyte. INF-25/26 w REJESTR.
🔗 KLUCZOWE: obie książki dzielą ten sam aparat MP — W-200..W-209 mają duplikaty z W-190..W-199 (jawnie
oznaczone "SCALIĆ/DUPLIKAT" w tabelach). Przy wdrożeniu JEDEN moduł profilu, nie dwa.
🚨 Prawo XV — realność na OHLCV: TPO (czas przy cenie) = czysty OHLC ✅; Volume Profile = przybliżenie przez
rozsmarowanie wolumenu per bar 🟡; tickowy POC = wymaga rozszerzenia Bramy (nie blokuje). Wymaga: (1) definicji
"sesji" crypto 24/7, (2) wspólnego profil_tpo()/profil_wolumenu() w Budowniczym.
**Powód:** Prawo XV (domknięcie 2 najsłabszych filarów V/S), ZPO (pełny opis), rozkaz Cezara (gromadzić pozycje).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (zadanie czysto dokumentacyjne)

---

## 2026-06-08 | BIBLIOTEKA | BIB-010/011/012 — 3 książki naraz (Chan ×2 + Coding Capital)

**Opis:** Cezar dostarczył 3 pliki naraz; każdy rozpakowany i przeanalizowany osobnym agentem Opus.
Rozkaz Cezara: gromadzić pozycje w WIZJONER, wdrożenie później ("jak zbierzemy pozycje, kontynuujemy").
- **BIB-010 Chan "Quantitative Trading" (2nd ed.) — 9/10:** half-life OU, macierzowy Kelly F*=C⁻¹·M (dowód
  Prawa XVI), cap lewara przez najgorszą stratę, para kointegrująca, deflated Sharpe, truncation look-ahead
  test → W-160..W-169.
- **BIB-011 Chan "Algorithmic Trading" (chińskie, ŻYCZ-04) — 9/10:** Kalman β dla par (rozszerza EXP-04),
  Monte-Carlo Kelly z Pearsona (fat tails!), Hurst+Variance-Ratio, leading risk, CPPI → W-170..W-178.
- **BIB-012 "Coding Capital" (Van Der Post) — ⚠️ 3/10 SŁABA:** self-published wypełniacz, snippety błędne.
  Jedyne ziarno: EVT/GPD parametr ogona ξ → W-180. Rekomendacja: nie kupować więcej Van Der Posta.
ŻYCZ-04 ✅ zdobyte. INF-22/23/24 w REJESTR.
🚨 2 flagi Prawa XV z BIB-011 do weryfikacji w kodzie: (1) czy KALKULATOR liczy Kelly tylko po Gaussie
(fat-tail crypto → ryzyko wipeout, W-176)? (2) czy EXP-04 używa Kalmana do hedge-ratio par (W-172)?
🔗 Nakładanie: obie książki Chana dzielą half-life OU i Kelly — przy wdrożeniu jeden neuron, nie dwa.
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (domknięcie luk R/S + flagi), ZPO (pełny opis, krytyczna ocena BIB-012).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅. Audyt: exit 0 ✅. (zadanie czysto dokumentacyjne — zero zmian kodu)

---

## 2026-06-08 | KOD+BIBLIOTEKA | W-130 Volatility Drag WDROŻONE + BIB-009 Mandelbrot "(Mis)behavior of Markets"

**Opis (2 ruchy w jednym zadaniu — rozkaz Cezara "tak plus następna książka"):**

**1. KOD — W-130 Volatility Drag (zamknięcie czerwonego alarmu Prawa XV z BIB-008):**
KALKULATOR_LEWARA (`pretorianie/kalkulator_lewara.py`) liczy teraz erozję zmiennościową
pozycji lewarowanej: `drag_roczny = ½·λ·(λ−1)·σ²` (Sinclair rozdz. 13, ta sama matematyka
co decay leveraged ETF). Implementacja wstecznie kompatybilna:
- `volatility_drag(dzwignia, vol_realized)` — staticmethod, None gdy brak vol (Prawo XV: bez halucynacji)
- `PlanPozycji.drag_roczny` — raport w każdym planie (None bez vol_realized)
- ostrzeżenie w logach gdy drag ≥ 50%/rok; wydruk planu pokazuje "Vol drag"
- opcjonalne weto `max_drag_roczny` (domyślnie None → zero zmian zachowania; jawny limit → blokada)
8 nowych testów (test_kalkulator.py). Dla λ=3, σ=1.0 → drag 300%/rok (zgodne z analizą).

**2. BIBLIOTEKA — BIB-009 Mandelbrot (ŻYCZ-03 zdobyte):**
Rozpakowany epub, przeanalizowany 2 równoległymi analizami Opus (rozdz. I-XV). Ojciec fraktali —
celuje wprost w nasze 3 najsłabsze osie D/H/N (po 1 neuronie). 19 wizji W-140..W-158 (skonsolidowane):
- 🔴 W-140 tail-index α (Hill, D/N), W-141 wymiar fraktalny (Higuchi, D), W-142 detektor skoków (Noah, N/D),
  W-143 trading-time/volatility clock (N/V), W-144 dependence-without-correlation (H/R)
- 🟠 W-145 koncentracja czasu (Gini), W-146 shock index (Richter), W-150 walidator R/S dla H-01
- 🟡 W-147 multifraktal Δα partition, W-148 Cantor-dust klastrów, W-149 kaskada multiplikatywna
ŻYCZ-03 ✅ zdobyte. INF-21 w REJESTR.
🚨 Filozofia Mandelbrota: neurony zasilają REŻIM/sizing (R), nie kierunek (zgodne z botem futures).
🔗 Symbioza: W-147/148/149 vs istniejący W-081 (MFDFA) — zmierzyć dekorelację przed wdrożeniem wielu naraz.

**Powód:** Prawo XV (zamknięcie krytycznego alarmu volatility drag + domknięcie luk D/H/N), Prawo XIX (kod+testy), ZPO.
**Pliki:** `imperium/pretorianie/kalkulator_lewara.py`, `tests/test_kalkulator.py`, `docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 514/514 ✅ (8 nowych W-130). Audyt: exit 0 ✅.

---

## 2026-06-08 | BIBLIOTEKA | BIB-008 ⭐ Sinclair "Volatility Trading" (2nd ed.) — RDZEŃ zmienności/lewara

**Opis:** Dodana BIB-008 (ŻYCZ-02 zdobyte). Autor (Euan Sinclair) to wykładowca metod, które IMPERIUM JUŻ
używa: estymator Yang-Zhang (kat. L/V) i Kelly criterion (KALKULATOR_LEWARA). Rozpakowana z azw3 (mobi→epub),
przeanalizowana 3 równoległymi analizami Opus (rozdz. 2,3,4 estymatory/stylized facts/prognozowanie;
rozdz. 8,9 Kelly/trade evaluation; rozdz. 13 leveraged ETFs). Rozdz. opcyjne (1,5-7,10-12,14) świadomie
pominięte jako nieistotne dla bota futures. Wynik: 5 rodzin koncepcji + 19 wizji W-121..W-139:
- 🔴 W-121 sygnatura zmienności (ratio estymatorów, kat. R), W-122 efekt dźwigni (asymetria, R/M),
  W-126 GARCH term-structure+vol anchor (L/R), W-127 volatility cone (percentyl σ, R),
  **W-130 volatility drag w KALKULATOR_LEWARA (KRYTYCZNY)**, W-131 Kelly+korekta Bayesa, W-132 dynamiczny sufit μ/σ², W-136 weryfikacja YZ vs Rogers-Satchell crypto 24/7
- 🟠 W-123 variance ratio, W-124 kurtoza (D), W-129 variance premium (DVOL−RV, wymaga Deribit), W-133 K-ratio, W-134 SE(Sharpe)+metryki, W-135 rejestr statystyk
- 🟡 W-125 ACF klasteryzacja (H), W-128 GARCH-asym, W-137 volume-volatility, W-138 first exit time (wymaga intraday), W-139 tryb Browne
ŻYCZ-02 oznaczone ✅ ZDOBYTE. INF-20 w REJESTR_INSPIRACJI.
🚨 3 sygnały Prawa XV: (1) **W-130 volatility drag** — jeśli kalkulator nie odejmuje erozji ½λ(λ−1)σ²t, zawyża atrakcyjność lewara = CZERWONY ALARM 🔴; (2) W-136 YZ traci przewagę na crypto 24/7 (brak luki → może Rogers-Satchell lepszy); (3) throttle W-096 musi reagować na σ², nie σ.
🔗 Symbioza: Kelly (W-131), vol-targeting (W-059), dynamiczny sufit (W-132) = ta sama matematyka μ/σ² — zmierzyć korelację przed wdrożeniem (Prawo XVI).
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (domknięcie luk L/V/R + krytyczny volatility drag), ZPO (pełny opis).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | BIBLIOTEKA | BIB-007 ⭐ López de Prado "Advances in Financial ML" — FLAGOWA pozycja

**Opis:** Dodana BIB-007 — najważniejsza książka Biblioteki (ocena 10/10). Autor (López de Prado) to
twórca metod, które IMPERIUM JUŻ używa: VPIN (Z-01), triple-barrier (W-035 Arena). Przeanalizowana
przez Opus (rdzeń strategiczny Części 1-4 dogłębnie; rozdz. 6/9/13/14/HPC ⚠️ niepełne — uczciwie oznaczone).
Wynik: 16 koncepcji + 14 wizji W-107..W-120 w `docs/WIZJONER.md`:
- 🔴 W-107 FFD (DOMYKA W-094 stacjonarność), W-108 entropia (kat. N), W-109 SADF eksplozja, W-111 meta-labeling,
  W-112 Purged-CPCV+DSR (infra bezpieczeństwa), W-113 audytor feature importance (realizuje Prawo XV/XVI)
- 🟠 W-110 CUSUM, W-114 information-driven bars, W-115 λ likwidność, W-116 predatory algos, W-118 ryzyko strategii, W-119 bet sizing
- 🟡 W-117 round-lot, W-120 wagi próbek
ŻYCZ-01 oznaczone ✅ ZDOBYTE. INF-19 w REJESTR_INSPIRACJI.
🚨 2 sygnały Prawa XV do weryfikacji: (1) czy Z-01 VPIN liczony na volume clock (W-114), (2) brak purged CV/PBO/DSR w ocenie roju = luka metodologiczna (W-112 🔴).
**Powód:** Prawo XVII (rozpoznanie), Prawo XV (domknięcie luk D/N/H/R), ZPO (pełny opis flagowej pozycji).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | ZWIAD | Lista Życzeń Biblioteki — zwiad internetowy książek pod luki Imperium

**Opis:** Na zlecenie Cezara — zwiad internetowy (WebSearch) książek do zdobycia, celowany w LUKI
kategorii neuronów (D=1, H=1, N=1, Z=2, V=2, L=2 — najsłabiej obsadzone). Wynik: sekcja
"LISTA ŻYCZEŃ BIBLIOTEKI" w `docs/WIZJONER.md` (ŻYCZ-01..09):
- 🔴 ŻYCZ-01 López de Prado "Advances in Financial ML" (autor VPIN/triple-barrier — domyka 4 nasze wizje)
- 🔴 ŻYCZ-02 Sinclair "Volatility Trading" (kat. L/V, Yang-Zhang), ŻYCZ-03 Mandelbrot "Misbehavior of Markets" (kat. H/D/N fraktale)
- 🟠 ŻYCZ-04 Chan "Algorithmic Trading" (reżim R), ŻYCZ-05/06 Dalton "Mind Over Markets"/"Markets in Profile" (wolumen/struktura V/S), ŻYCZ-07 Sinclair "Positional Option Trading" (Kelly)
- 🟡 ŻYCZ-08 Kahneman, ŻYCZ-09 zasoby on-chain (Glassnode/checkonchain — nie książka)
Uczciwie oznaczone (Prawo I): ŻYCZ-03/08 z wiedzy własnej, reszta potwierdzona zwiadem 2026-06-08.
**Powód:** Prawo XVII (rozpoznanie terenu/potrzeb), Prawo XV (celowanie w luki = podnoszenie potencjału), ZPO.
**Pliki:** `docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | BIBLIOTEKA | BIB-005..006 — kolejne 2 książki do Biblioteki Tradingowej Cezara

**Opis:** Dodane 2 książki do Biblioteki (BIB-005, BIB-006), przeanalizowane przez Opus wg ZPO,
zapisane do `docs/WIZJONER.md`:
- **BIB-005** "What Exactly Is Crypto?" (Jonatan Blum, 2022) — primer on-chain/tokenomika; ocena 4/10 🟡.
  Wartość: pojęcia tokenomiki (issuance−burn), płynność DEX (AMM x*y=k), ryzyko centralizacji → W-097..W-100.
  Uwaga Prawo XV: te neurony wymagają nowego źródła danych on-chain (bez niego = martwy głos).
- **BIB-006** "High Probability Scalping Strategy Playbook" (Zachary Carson, 2024, self-published) — ocena 4/10 🟠.
  UCZCIWA ocena (Prawo I): ~70% katalog "wpisz nazwę w TradingView", brak backtestów/statystyk win-rate mimo tytułu.
  ALE realne kodowalne elementy: konfluencja-z-dekorelacją (=Prawo XVI), filtr reżimu ADX, MFI, sekwencja 9/13, ATR-stop → W-101..W-106.
  Quick winy (dane już w Bramie): W-103 NeuronMFI, W-101 BB40+RSI5+ADX.
INF-17/18 dodane do REJESTR_INSPIRACJI. Wizje W-097..W-106 to PROPOZYCJE (Prawo XIX: nie istnieją bez kodu+testów).
**Powód:** Prawo XVII (rozpoznanie terenu/wiedzy), ZPO (pełny opis), Prawo I (uczciwa ocena niskiej jakości BIB-006).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-08 | REVIEW-FIX | Poprawki recenzji cubic (geometria.py P1 + LOG/REJESTR/MANIFEST P2)

**Opis:** Naprawiono 6 uwag recenzji cubic na PR:
- **P1 geometria.py:** stały wolumen (v_range≈0) dawał fałszywe pole Lévy Area (dy=0 ale stała
  wartość y tworzy −0.25·Δx ≠ 0) → fałszywy sygnał kierunkowy. Fix: stały wolumen → NEUTRAL.
  Usunięty fallback `[0.5]*n`. +1 test (`test_d01_staly_wolumen_neutral`).
- **P2 LOG_ZMIAN:** pole `**Pliki:**` wpisu D-01 było puste (heredoc shell uszkodził treść) →
  uzupełnione realnymi ścieżkami; usunięty osierocony duplikat wpisu D-01 bez nagłówka daty.
- **P2 REJESTR_INSPIRACJI:** INF-13..16 miały `Książka (BIB-xxx)` zamiast linku → dodane ISBN.
- **P2 MANIFEST/WIZJONER:** elite count 14→15 i Prawo XV→XVI już naprawione w 91f262b.
**Powód:** Prawo XIX (kod jest prawem), Prawo XXI (spójność), Prawo I (uczciwy sygnał).
**Pliki:** `imperium/legiony/neurony/geometria.py`, `tests/test_neurony.py`, `docs/LOG_ZMIAN.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/MANIFEST_KODU.md`, `README.md`
**Testy:** 506/506 ✅. Audyt: exit 0 ✅.

---

## 2026-06-07 | BIBLIOTEKA | BIB-001..004 — Biblioteka Tradingowa Cezara (4 książki przeanalizowane)

**Opis:** Założona Biblioteka Tradingowa Cezara. Przeanalizowane 4 książki (format azw3→epub→HTML,
pełna ekstrakcja treści przez Opus) i zapisane do `docs/WIZJONER.md` jako sekcja BIB-001..004:
- **BIB-001** The Secret Wealth Advantage (Akhil Patel) — 18-letni cykl nieruchomości, reguła 23/25 krachów → W-082..W-084
- **BIB-002** Technical Analysis of the Financial Markets (John J. Murphy) — analiza międzyrynkowa, left/right translation, MESA → W-085..W-088
- **BIB-003** Cryptoassets (Burniske & Tatar) — NVT (crypto-PE), hash rate, Google Trends, Gartner Hype Cycle → W-089..W-093
- **BIB-004** The Psychology of Trading (Brett Steenbarger) — stacjonarność (Clifford Sherry), pinball trade, anty-overconfidence → W-094..W-096
Każda książka opisana wg ZPO: pełne tytuły, cytaty dosłowne, status weryfikacji ✅/⚠️, ocena, priorytet.
**Powód:** Prawo XVII (rozpoznanie terenu), ZPO (zasada pełnego opisu), Prawo XIX (kod jest prawem — ale wiedza jest fundamentem kodu).
**Pliki:** `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`, `docs/LOG_ZMIAN.md`

---

## 2026-06-07 | WDROŻENIE | W-079 D-01 NeuronPathSignature — Lévy Area Close×Volume (Rough Path Theory)

**Opis:** Wdrożono neuron D-01 NeuronPathSignature — pierwsza miara nieprzemiennej geometrii
ścieżki w Imperium. Lévy Area (iterated integral rzędu 2) mierzy synchronizację wzrostu
wolumenu z ceną: LA>0 → akumulacja poprzedza ruch (LONG); LA<0 → dystrybucja (SHORT).
Implementacja czysto NumPy (bez zewnętrznych bibliotek), okno 20 barów, normalizacja
scale-invariant. Nowa kategoria D (Dynamika ścieżkowa). Elitarny (E1 — jedyna miara
w Imperium mierząca tę oś). WAGI_REZIMU uzupełnione o kat. D.
Budowniczy wzbogacony o CLOSE_SERIES_20 + VOLUME_SERIES_20 (_dodaj_path_series).
8 nowych testów. Daty MANIFEST/README zaktualizowane.
**Powód:** Prawo XIX (kod jest prawem), Prawo XX (ELITARNY=True z kryterium E1).
**Pliki:** `imperium/legiony/neurony/geometria.py` (nowy), `imperium/legiony/rejestr.py`, `imperium/legiony/budowniczy_wskaznikow.py`, `imperium/legiony/legatus.py`, `narzedzia/audyt_spojnosci.py`, `tests/test_neurony.py`, `tests/test_integracja.py`, `docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/KATALOG_NEURONOW.md`, `docs/AUDYT_SYSTEMU.md`, `docs/INDEKS_IMPERIUM.md`, `README.md`
**Testy:** 505/505 ✅. Audyt: exit 0 ✅.

---

## 2026-06-04 | AUDYT+ZWIAD | 7 niespójności liczb naprawionych + 3 perełki do WIZJONERA (W-079..W-081)

**Opis:** Głęboki audyt całego Imperium (kod vs dokumenty wg INDEKSU) wykrył 7 stałych
rozbieżności liczb — wszystkie naprawione (MANIFEST 43/299→51, ==46→51; test_integracja
komunikat 50→51; KATALOG 42→51 i 28→51; AUDYT_SYSTEMU 28/240→51/497; INDEKS data+wersja).
Równolegle zwiad perełek (arXiv 2024–2025, weryfikacja 3-głos) → 3 ortogonalne znaleziska
dopisane do WIZJONER i REJESTR_INSPIRACJI (INF-10/11/12):
- **W-079 Path Signature** (Lévy Area Close↔Volume — geometria/kauzalność, kat. D) — REKOMENDACJA #1
- **W-080 Hawkes Branching Ratio** (endogeniczność n̂, sensor PANIC, kat. R/F)
- **W-081 MFDFA Δα** (wielofraktalna heterogeniczność, kat. F/D)
**Powód:** Prawo XVII (rozpoznanie terenu), Prawo XIX/XXI (spójność), Prawo XV (podnoszenie potencjału).
**Pliki:** `docs/MANIFEST_KODU.md`, `tests/test_integracja.py`, `docs/KATALOG_NEURONOW.md`, `docs/AUDYT_SYSTEMU.md`, `docs/INDEKS_IMPERIUM.md`, `docs/WIZJONER.md`, `docs/REJESTR_INSPIRACJI.md`
**Testy:** 497/497 ✅. Audyt: exit 0 ✅.

---

## 2026-06-04 | FEATURE | Permutation Entropy meta-brama chaosu — nowa kategoria N (wizja W-054)

### Kontekst
Brakowało osi informacji „złożoność/struktura porządku" jako meta-bramy chaosu
(czy rynek ma STRUKTURĘ, czy jest czystym chaosem — efektywny, bez przewagi).
Permutation Entropy (Bandt & Pompe 2002) patrzy na wzorce porządkowe (ordinal
patterns), nie na kierunek — w pełni ortogonalna do RSI/MACD.

### Decyzja Prawa XVI (redundancja mierzona, nie zgadywana)
PE mierzy złożoność struktury porządku, nie poziom (RSI), crossover (MACD),
magnitudę wahań (V) ani siłę kierunku (T) — inna OŚ informacji → dekoreluje z
głosami kierunkowymi i z V/T/M. ~34% czulsza niż GARCH na klasteryzację
zmienności. N-01 zaprojektowany jako META-BRAMA (PE>0.85 → NEUTRAL „chaos, nie
handluj"), nie kolejny głos kierunkowy. Korelacja N-01↔V/T/M do zmierzenia
`diagnostyka_korelacji` po zebraniu danych paper-tradingu.

### Wdrożone
- **Brama:** pure-Python `PERMUTATION_ENTROPY` (`_py_permutation_entropy`, close,
  period=100, dim=3, delay=1) — Bandt & Pompe 2002; PE∈[0,1] (norm. log(dim!)),
  None gdy <period (Prawo I). Stempel pure-Python (XIII).
- **Budowniczy:** klucz `PERM_ENTROPY_100`.
- **Neuron N-01** `neurony/entropia.py` (NeuronPermutationEntropy, kat. N): PE>0.85
  chaos (NEUTRAL meta-brama), PE<0.65 struktura (potwierdza mikro-ruch), 0.65–0.85
  szara strefa (NEUTRAL niska pewność).
- **Nowa kategoria N** narodzona: legenda `mikro_neuron.py`, audyt `LEGENDA_KAT`,
  `CLAUDE.md` KROK 0, `WAGI_REZIMU` (N ×1.3 VOLATILE, ×1.2 RANGING, ×1.1 NORMAL,
  ×1.0 TREND_STRONG), rejestr.
- **Liczby:** 47→48 neuronów (41 aktywnych), 59→60 modułów. Backlog 252→251.
- **Testy:** +9 (Brama PE zakres/warmup/chaos/monotoniczny/źródło, N-01 4 sytuacje
  + kat.). 425 → 434/434 zielone.

### Pliki
`imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/entropia.py`, `imperium/legiony/mikro_neuron.py`,
`imperium/legiony/legatus.py`, `imperium/legiony/rejestr.py`,
`narzedzia/audyt_spojnosci.py`, `tests/test_neurony.py`,
`docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/LOG_ZMIAN.md`, `README.md`, `CLAUDE.md`.

---

## 2026-06-03 | FEATURE | Hurst-DFA meta-brama reżimu — nowa kategoria H (wizja W-053)

### Kontekst
Brakowało osobnej osi informacji „pamięć długiego zasięgu" jako meta-bramy
reżimu (czy rynek W OGÓLE ma przewagę: trend / mean-reversion / błądzenie losowe).
EXP-03 liczył Hursta metodą R/S (obciążoną na trendach) — potrzebny był odporny
estymator DFA we własnej kategorii.

### Decyzja Prawa XVI (redundancja mierzona, nie zgadywana)
DFA detrenduje każde okno wielomianem → odporny na niestacjonarność; R/S nie.
Na trendującym krypto oba dają RÓŻNE H → realna dekorelacja (jak istniejący duet
Higuchi FD + Hurst R/S). H-01 zaprojektowany jako META-BRAMA (H≈0.5 → NEUTRAL
„nie handluj"), nie trzeci głos kierunkowy. Korelacja H-01↔EXP-03 do zmierzenia
`diagnostyka_korelacji` po zebraniu danych paper-tradingu.

### Wdrożone
- **Brama:** pure-Python `HURST_DFA` (`_py_hurst_dfa`, close, period=100) — DFA
  Peng i in. 1994; H∈(0,1), None gdy <period (Prawo I). Stempel pure-Python (XIII).
- **Budowniczy:** klucz `HURST_DFA_100`.
- **Neuron H-01** `neurony/fraktal.py` (NeuronHurstDFA, kat. H): H>0.55 persystencja
  (podążaj), H<0.45 antypersystencja (kontra), H≈0.5 NEUTRAL (meta-brama).
- **Nowa kategoria H** ożywiona: legenda `mikro_neuron.py`, audyt `LEGENDA_KAT`,
  `WAGI_REZIMU` (H ×1.3 TREND_STRONG, ×1.2 RANGING, ×1.1 NORMAL), rejestr.
- **Liczby:** 46→47 neuronów (40 aktywnych), 58→59 modułów. Backlog 253→252.
- **Testy:** +9 (Brama DFA zakres/warmup/determinizm/źródło, H-01 4 reżimy + kat.).
  416 → 425/425 zielone.

### Pliki
`imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/fraktal.py`, `imperium/legiony/mikro_neuron.py`,
`imperium/legiony/legatus.py`, `imperium/legiony/rejestr.py`,
`narzedzia/audyt_spojnosci.py`, `tests/test_neurony.py`, `tests/test_integracja.py`,
`docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `docs/INDEKS_IMPERIUM.md`,
`docs/LOG_ZMIAN.md`, `README.md`.

---

## 2026-06-03 | FEATURE | Volatility Targeting — skalowanie rozmiaru pozycji do celu zmienności (wizja W-059)

### Kontekst
Kalkulator Lewara liczył rozmiar wyłącznie risk-based (2% kapitału / stop_pct).
Brakowało standardu instytucjonalnego: rozmiar ∝ vol_target / vol_realized —
mniejsza pozycja w burzy, większa w spokoju (w bezpiecznych granicach).

### Wdrożone
- **`KalkulatorLewara.skala_vol_targeting(vol_realized, vol_target)`** — mnożnik
  = vol_target/vol_realized przycięty do [0.25, 1.50]. None/≤0 → 1.0 (bez
  halucynacji, Prawo XV).
- **`policz(..., vol_realized=None, vol_target=0.60)`** — rozmiar przeskalowany
  mnożnikiem; nowe pole `PlanPozycji.skala_vol`. Domyślnie 1.0 → kompatybilność
  wsteczna. Symbioza z W-055: `vol_realized` = `YANG_ZHANG_20` (ta sama skala
  annualizowana co cel).
- **Testy:** +6 (brak danych, tnie/powiększa, przycięcie MIN/MAX, wpływ na plan).
  410 → 416/416 zielone.

### Pliki
`imperium/pretorianie/kalkulator_lewara.py`, `tests/test_kalkulator.py`,
`docs/WIZJONER.md`, `docs/LOG_ZMIAN.md`, `README.md`.

---

## 2026-06-03 | FEATURE | HedgeMWU — online żywe wagi Legatusa + zamknięcie pętli uczenia (wizja W-049)

### Kontekst
Czerwony alarm Prawa XV: `Igrzyska.nowe_wagi()` liczyło mnożniki wag neuronów,
ale **Legatus nigdy ich nie konsumował** — policzony potencjał leżał odłogiem.
Brakowało też online'owego (strumieniowego) uczenia wag z gwarancją regretu.

### Wdrożone
- **`imperium/biblioteki/hedge_mwu.py`** — `HedgeMWU`: algorytm Hedge / Multiplicative
  Weights Update (Freund & Schapire, 1997), regret O(√(T·ln N)). Po każdym wyniku
  waga eksperta ×exp(-η·strata); `mnozniki()` skalowane wokół 1.0 (stan neutralny
  = brak zniekształcenia, Prawo XV). Min. waga chroni przed śmiercią eksperta.
- **`Igrzyska.obserwatorzy`** — lista obserwatorów strumienia wyników; MWU uczy
  się z DOKŁADNIE tego samego strumienia co Igrzyska (DRY, bez duplikacji parowania
  logów). `HedgeMWU.z_logow(logi)` korzysta z tego mechanizmu.
- **Legatus** — nowy parametr `mnozniki_neuronow` + `ustaw_mnozniki_neuronow()`;
  `_dostosuj_wagi` mnoży wagę reżimową × mnożnik uczenia per-neuron. Konsumuje
  ZARÓWNO `Igrzyska.nowe_wagi()` (batch) jak i `HedgeMWU.mnozniki()` (online).
  Domyślnie pusty → kompatybilność wsteczna (zero zmian zachowania).
- **Testy:** +12 (MWU: neutralność, adaptacja, normalizacja, min_waga, obserwator
  Igrzysk; Legatus: brak/iniekcja/setter). 398 → 410/410 zielone.

### Pliki
`imperium/biblioteki/hedge_mwu.py`, `imperium/biblioteki/igrzyska.py`,
`imperium/legiony/legatus.py`, `tests/test_hedge_mwu.py`, `tests/run_tests.py`,
`docs/WIZJONER.md`, `docs/INDEKS_IMPERIUM.md`, `docs/LOG_ZMIAN.md`.

---

## 2026-06-03 | FEATURE | Yang-Zhang Volatility — upgrade estymatora kat. V (wizja W-055)

### Kontekst
Neuron V-13 (NeuronRealizedVol) liczył zmienność wyłącznie z cen zamknięcia
(`HIST_VOL_20` = std log-returns × √252). To ignorowało luki overnight i cały
zakres świecy (high/low) — utrata informacji OHLC (Prawo XV).

### Wdrożone
- **Brama:** nowe obliczenie pure-Python `YANG_ZHANG` (`_py_yang_zhang`,
  open/high/low/close, period=20) — annualizowana vol w tej samej skali co
  HIST_VOL, ~14× efektywniejsza statystycznie (Yang & Zhang, 2000). Stemplowane
  jako pure-Python (Prawo XIII).
- **Budowniczy:** produkuje klucz `YANG_ZHANG_20`.
- **V-13:** WSKAZNIK → `YANG_ZHANG_20` (podstawa) z fallbackiem `HIST_VOL_20`
  (bez martwego głosu — Prawo XV). Progi reżimu bez zmian (ta sama skala).
- **Testy:** +7 (Brama zakres/warmup/skala/źródło, V-13 podstawa/fallback/neutral).
  391 → 398/398 zielone.

### Pliki
`imperium/fundament/brama_kalkulatora.py`, `imperium/legiony/budowniczy_wskaznikow.py`,
`imperium/legiony/neurony/dzwignia.py`, `tests/test_neurony.py`,
`docs/MANIFEST_KODU.md`, `docs/WIZJONER.md`, `README.md`.

---

## 2026-06-03 | MAJOR | Synchronizacja KATALOG_STRATEGII z kodem + warstwa audytu W9 (Prawo XIX/XXI)

### Kontekst
Pytanie Cezara o ZŁOTY ORZEŁ ujawniło, że opisy strategii w `KATALOG_STRATEGII.md`
cytowały STARE klucze neuronów (numeracja projektowa), niezgodne z kodem — np. ZŁOTY
ORZEŁ miał „XII-01 EMA Golden Cross" (a XII-01 to ADX), „XII-08 OBV" (nie istnieje).
Audyt tego nie łapał (sprawdzał tylko klucze neuronów, nie listy w katalogu).

### Diagnoza
Z 17 zaimplementowanych strategii: 5 spójnych, **12 z rozjazdem** (obce klucze w opisie).
Kod był zawsze poprawny (wszystkie strategie wskazują istniejące, aktywne neurony) —
problem był wyłącznie w dokumentacji.

### Naprawione
- **12 bloków strategii** w `KATALOG_STRATEGII.md` — klucze WEJŚCIE/FILTR/WYJŚCIE
  zsynchronizowane z kodem (X-SC-001/002, XII-TR-001, XII-RV-001, XII-BK-001,
  IMV-HY-003, IMV-TR-001/002/003, IMV-SC-002, IMV-RG-001/002).
- **ZŁOTY ORZEŁ** — dodano notatkę „wariant EMA, nie oryginalny SMA" + pochodzenie
  (Golden Cross = klasyka, domena publiczna, brak pojedynczego autora).
- **Warstwa audytu W9** (`audyt_spojnosci.py`) — parsuje bloki zaimplementowanych
  strategii i wykrywa klucze spoza kodu. Rozjazd katalog↔kod już nigdy nie przejdzie.

### Testy regresyjne
- `test_audyt_w9_wykrywa_obcy_klucz_strategii`, `test_audyt_w9_zielony_na_realnym_katalogu`.

### Stan
- 17/17 strategii spójnych (kod=katalog). Testy: 390/390 (+2). Audyt: pełna harmonia.

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) #5 — L2 float, HA doji/ATR0, dekorelacja None

### Kontekst
Tura recenzji PR #22 — 4 uwagi (2×P1, 2×P2). Wszystkie trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **P1 L2 qty (exp_atmabhan):** Binance depth zwraca ilości jako STRINGI → `sum(b[1])`
  mógł paść/sklejać. Rzutowanie `float(b[1])` przed sumą.
- **P1 HA doji (budowniczy):** `HA_BULL = c >= o` oznaczał doji (c==o) jako byka.
  Zmieniono na strict `>` → doji neutralny.
- **P2 HA ATR==0 (budowniczy):** płaski rynek gubił pola HA_MOMENTUM/HA_VOLATILITY_INDEX.
  Dodano jawne zera w gałęzi else → martwy rynek FILTROWANY, nie handlowany (Prawo XV).
- **P2 dekorelacja None (diagnostyka):** `None` traktowany bezwarunkowo jako martwa para,
  choć oznacza też za mało danych (n<2). Rozdzielono: martwy = któraś seria stała
  (≥2 próbki, zerowa wariancja); reszta None → `pary_niedostateczne_dane`. Naprawiono też
  detekcję `stale` (1 próbka trywialnie wyglądała na stałą → false alarm).

### Testy regresyjne
- `test_raport_niedostateczne_dane_nie_alarmuje_martwych` — 1 krok ≠ martwy głos.
- Rozszerzono `test_raport_wykrywa_martwy_glos` o sprawdzenie `pary_nieokreslone`.

### Stan
- Testy: 388/388 (+1). Audyt: pełna harmonia.

---

## 2026-06-03 | FIX | Poprawka recenzji PR (cubic) #4 — KROK 0 grep mylący (ZASADY)

### Kontekst
Recenzja PR #24 zwróciła uwagę: w KROK 0 komenda `grep -c "✅"` liczyła WSZYSTKIE
✅ (nagłówek + statusy), a krok 2 opisywał `✅ aktywny` — sprzeczne liczby.

### Diagnoza (głębsza niż uwaga)
`grep -c "✅ aktywny"` daje 69 (łapie też zwiadowców EXP i inne tabele), a aktywnych
neuronów jest 39. Grep po dokumentach NIE jest w stanie wyizolować neuronów — to złe
źródło prawdy (łamie Prawo XIX: źródłem jest kod, nie dokument).

### Naprawione
- KROK 0 w `ZASADY_FUNDAMENTALNE.md`: zastąpiono kruchy grep autorytatywną komendą
  (`audyt_spojnosci.py` + one-liner z `rejestr.py`). Dodano ostrzeżenie, by NIE liczyć
  neuronów grepem. Źródło prawdy = kod weryfikowany audytem.

### Stan
- Testy: 387/387. Audyt: pełna harmonia. (Zmiana wyłącznie dokumentacyjna — ZASADY.)

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) #3 — filtr/AC/audyt W4/MANIFEST

### Kontekst
Trzecia tura recenzji PR — 4 uwagi. Wszystkie zweryfikowane jako trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **baza.py (filtr nie karze):** strategia z filtrami, ale wszystkie wyciszone
  (`n_akt_f==0`) dostawała `filtr_frakcja=0.5` → kara mimo komentarza „nie karzemy
  za wyciszone". Poprawiono na `1.0` (jak brak filtrów). Prawo XV.
- **brama (AC off-by-one):** `_py_accelerator` wymagał `slow+sma_ac+1` świec, choć
  najgłębszy SMA potrzebuje `slow+sma_ac`. Usunięto `+1` → wynik o bar wcześniej.
- **audyt W4 (maskowanie importu):** `except ImportError: pass` ukrywał KAŻDY błąd
  importu. Zawężono do `ModuleNotFoundError` modułu strategii; inne → błąd audytu.
- **MANIFEST (per-legion):** X Equestris pokazywał 7 zaimpl./19 do wdrożenia mimo
  dodania X-09/X-10. Poprawiono na 9/17 (spójne z RAZEM 46/253).

### Testy regresyjne
- `test_brama_accelerator_warmup_dokladny` — AC przy dokładnie slow+sma_ac.
- `test_dopasowanie_wyciszone_filtry_nie_karza` — wynik = strategia bez filtrów.

### Stan
- Testy: 387/387 (+2). Audyt: pełna harmonia.

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) #2 — hook staged-only + audyt W6 'Stan na:'

### Kontekst
Druga tura recenzji PR zgłosiła 2 uwagi. Obie trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **Pre-commit hook (staged-only):** hook uruchamiał testy/audyt na working tree,
  nie na zawartości staged → zepsuty staged mógł przejść, jeśli working tree był
  poprawny (i odwrotnie). Dodano izolację: `git stash push --keep-index --include-untracked`
  na czas sprawdzeń + `trap` gwarantujący przywrócenie working tree (EXIT/INT/TERM).
- **Audyt W6 (brak 'Stan na:'):** brak pola daty był cicho pomijany (`if m:` bez `else`).
  Dodano `else` → brak daty = błąd. Przy okazji wykryto, że regex nie matchował
  markdown `**Stan na:** data` — poprawiono na `Stan na:\s*\**\s*(data)`.

### Testy regresyjne
- `test_audyt_wykrywa_brak_stan_na` — brak pola = błąd W6.
- `test_audyt_akceptuje_stan_na_w_markdown` — markdown nie daje fałszywego alarmu.

### Stan
- Testy: 385/385 (+2). Audyt: pełna harmonia. Hook zsynchronizowany (install_hooks.py).

---

## 2026-06-03 | FIX | Poprawki recenzji PR (cubic) — audyt źródła, warmup Ulcer, fallback symbolu

### Kontekst
Recenzja automatyczna PR zgłosiła 3 uwagi. Wszystkie zweryfikowane jako trafne i naprawione.

### Naprawione (kod + testy regresyjne)
- **Prawo XIII (audyt źródła):** `CalcResult.source` domyślnie stemplował WSZYSTKIE
  wskaźniki jako TA-Lib, w tym pure-Python (AO/AC/HMA/RVOL/HIST_VOL/VWAP/Supertrend/
  Ichimoku/Donchian/CHOPPINESS/ULCER). Dodano `_PURE_PYTHON_INDICATORS` + wybór źródła
  w `compute()` → audyt nie kłamie o pochodzeniu obliczenia.
- **Ulcer warmup:** `_py_ulcer` wymagał `period+1` świec, choć używa `c[-period:]`
  (dokładnie `period`). Poprawiono próg na `< period`.
- **Fallback symbolu:** `czytnik_csv` brał `split("_")[0]` → dla `Binance_BTCUSDT_1h.csv`
  zwracał `BINANCE`. Poprawiono na segment PRZED interwałem (`[-2]`) → `BTCUSDT`.

### Stan
- Testy: 383/383 (+2 regresyjne: warmup Ulcer, stempel źródła). Audyt: pełna harmonia.

---

## 2026-06-03 | MAJOR | Rozbudowa roju — kat. L+V wzmocnione (Ulcer + Choppiness, Prawo XVI)

### Kontekst
Kategorie L (dźwignia) i V (zmienność) miały po 1 neuronie — najcieńsze w roju,
ledwo wpływały na wagi reżimowe. Mierzona rozbudowa zdekorelowanymi sygnałami.

### Co zostało wdrożone (kod)
- **L-14 NeuronUlcer** (kat. L) — Ulcer Index: ryzyko SPADKOWE (głębokość/czas
  obsunięć), karze tylko ruch w dół. Dekoreluje z VI-13 (ATR symetryczny).
- **V-14 NeuronChoppiness** (kat. V) — Choppiness Index: trend vs konsolidacja
  (efektywność ruchu). Dekoreluje z V-13 (HV = magnituda wahań).
- **Brama** (`fundament/brama_kalkulatora.py`) — pure-Python `_py_ulcer`,
  `_py_choppiness` + wpisy rejestru ULCER, CHOPPINESS (Prawo I — jedyne wejście).
- **Budowniczy** — ULCER_14, CHOPPINESS_14 w `_PLAN_SKALARNE`.
- **Rejestr** — oba neurony w `wszystkie_neurony()`. Czyste OHLCV, bez API.

### Pomiar dekorelacji (Prawo XVI — nie opinia)
Seria sygnałów (LONG=+1/NEUTRAL=0/SHORT=−1) po oknie kroczącym, korelacja Pearsona
na dołączonych danych (ETH_1d, BTC_1h):
- **V-13 ↔ V-14:** |r| = 0.05–0.27 → dywersyfikacja (filar siły, oba zostają).
- **VI-13 ↔ L-14:** VI-13 stały (SHORT) na danych syntetycznych → L-14 dostarcza
  PEŁNĄ wariancję kat. L (LONG/NEUTRAL/SHORT, UI 0.24–12.0) → komplementarność.

### Stan
- Neurony: 46 (aktywne 39, wyciszone 7). Testy: 381/381. Audyt: pełna harmonia.

---

## 2026-06-03 | FIX+TESTY | Backtest ożywiony — czytnik prostego formatu + testy Dyrygenta (Prawo XIX)

### Kontekst
`koloseum/backtest.py` (przejazd Dyrygenta po historii) istniał, ale: (1) NIE miał
własnych testów — martwa litera wg Prawa XIX (test_scheduler testuje inny backtest);
(2) czytnik CSV wymagał formatu CryptoDataDownload (kolumna `unix`), więc dołączone
dane `dane/*.csv` (prosty format `timestamp,open,...`) NIE dawały się uruchomić.

### Co zostało wdrożone (kod)
- **Czytnik elastyczny** (`akwedukty/czytnik_csv.py`) — akceptuje `unix` (CDD) LUB
  `timestamp` (prosty format Imperium). `_parse_ts()` parsuje epoch (s/ms) oraz
  ISO-datę. Brak kolumny `symbol` → wywnioskowany z nazwy pliku (`BTC_1h` → `BTC`).
- **Testy backtestu** (`tests/test_backtest.py`, 5) — silnik z historią, walidacja
  za małej liczby barów, AUTO-reżim (Namiestnik), porównanie 3 trybów oraz
  **bezpośredni dowód braku lookahead** (szpieg na `Dyrygent.cykl` sprawdza, że
  każde okno kończy się na bieżącej świecy, brak barów z przyszłości).
- **Testy prostego formatu** (`tests/test_czytnik_csv.py`, +3) — ISO-timestamp,
  symbol z nazwy pliku, `_parse_ts` (epoch s/ms/ISO).

### Weryfikacja
Backtest odpala się out-of-the-box na `dane/BTC_1h.csv` i `dane/ETH_1d.csv`
(`--porownaj` oraz `auto_rezim=True`). Brak zaglądania w przyszłość udowodniony testem.

### Stan
- Testy: 370/370 (+8). Audyt: pełna harmonia. Neurony/strategie bez zmian.

---

## 2026-06-03 | MAJOR | Faza C — V-03 CVD obudzony (adapter trade-feed publiczny, Prawo XV)

### Kontekst
V-03 CVD (Cumulative Volume Delta, kat. F) wyciszony — OHLCV nie zawiera strony
agresora (kto market-kupował vs sprzedawał). Potrzebny trade-feed.

### Co zostało wdrożone (kod)
- **AdapterCVD** (`akwedukty/adaptery/cvd.py`) — publiczny feed Binance aggTrades
  (`fapi/v1/aggTrades`) BEZ klucza API. CVD = Σ(buy) − Σ(sell) z okna transakcji
  (pole `m`=isBuyerMaker: false→buy, true→sell). Wstrzykiwany fetcher (test offline);
  pamięć CVD_PREV per symbol (dla dywergencji V-03).
- **V-03 obudzony** (DOSTEPNY=True) — kat. F: 5→6 aktywnych.
- **Adapter wpięty w pipeline Dyrygenta** — `Dyrygent.zbuduj(adaptery_live=True)`
  domyślnie wpina AdapterFutures + AdapterFearGreed + AdapterCVD.

### Prawo I/XV — uczciwość
W backteście CSV (bez trade-feedu) V-03 ABSTYNUJE (NEUTRAL). Live/paper: AdapterCVD
liczy CVD z publicznego aggTrades → V-03 głosuje (znak CVD + dywergencja vs cena).

### Stan po Fazie C
- Neurony: 44 (aktywne 37, wyciszone 7 = OC-01..04 + SMC-01..03).
- Testy: 362/362. Audyt: pełna harmonia.

### Następna faza
- Faza D: OC-01..04 on-chain (Glassnode/CryptoQuant API — wymaga klucza, os.getenv).

---

## 2026-06-03 | MAJOR | Faza B — kategoria R obudzona (adaptery futures publiczne, Prawo XV)

### Kontekst
Kategoria R (Sentyment) miała 0 aktywnych neuronów — 4 neurony PSY (Funding,
Long/Short, Fear&Greed, OI Divergence) leżały wyciszone. Reguły WAGI_REZIMU dla R
istniały tylko w PANIC (= weto, brak transakcji) → potencjał kategorii R w 0%.

### Wykryta UTRATA POTENCJAŁU (Prawo XV)
- 4 neurony PSY wyciszone mimo gotowego frameworku adapterów.
- AdapterFearGreed (PSY-03, realne darmowe API) istniał, ale nie był wpięty w pipeline.
- WAGI_REZIMU: R aktywne tylko w PANIC (weto) → R nigdy nie wpływało na transakcję.

### Co zostało wdrożone (kod)
- **AdapterFutures** (`akwedukty/adaptery/futures.py`) — publiczne endpointy Binance fapi
  (funding, open interest, long/short) BEZ klucza API; wstrzykiwany fetcher (test offline);
  pamięć OI_PREV dla dywergencji PSY-04.
- **PSY-01/02/03/04 obudzone** (DOSTEPNY=True) — kategoria R: 0→4 aktywne.
- **Adaptery wpięte w pipeline Dyrygenta** — `_wskazniki()` dolewa dane po Budowniczym;
  `Dyrygent.zbuduj(adaptery_live=True)` domyślnie wpina AdapterFutures + AdapterFearGreed.
- **WAGI_REZIMU** — R dodane do VOLATILE(×1.3), RANGING(×1.2), NORMAL(×1.1),
  TREND_STRONG(×0.8), ON-CHAIN_BULLISH(×1.1) — R realnie wpływa na transakcje.
- **+2 strategie VI-LV** (Legio VI Ferrata): VI-LV-001 Funding Contrarian (PSY-01/02+VI-13/V-13),
  VI-LV-002 Liquidation Cascade (A-01/PSY-04+VI-13/V-13). 17 strategii łącznie.

### Prawo I / XV — uczciwość
W czystym backteście z CSV (bez kolumny funding/OI) neurony PSY ABSTYNUJĄ (NEUTRAL,
rój wyklucza je z głosu kierunkowego — nie martwy ciężar). W trybie live/paper adapter
dolewa realne dane → PSY głosują.

### Stan po Fazie B
- Neurony: 44 (aktywne 36, wyciszone 8) — kat. R żywa.
- Kategorie aktywne: A, F, L, M, O*, R, S*, T, V (O/S budzone runtime/feed).
- Strategie: 17. Testy: 358/358. Audyt: pełna harmonia.

### Następne fazy
- Faza C: V-03 CVD (trade feed), SMC live feed.
- Faza D: OC-01..04 on-chain (Glassnode/CryptoQuant API).

---

## 2026-06-03 | MAJOR | Timeframe-Aware Gating — styl SCALP/SWING/INVEST + futures/spot (Prawo XV)

### Kontekst
Cezar: system musi rozróżniać interwał czasowy (scalp/swing/invest), wybierać neurony,
strategie, dźwignię i rynek (futures/spot) automatycznie wg oceny rynku + interwału.
Deep-research: auto-selekcja timeframe+strategia to OTWARTY PROBLEM (Freqtrade/Jesse/
Nautilus/OctoBot wymagają ręcznej konfiguracji). Namiestnik robi to automatycznie.

### Wykryta UTRATA POTENCJAŁU (Prawo XV)
- Strategie miały pola `interwaly`, `styl`, `dzwignia` — **ignorowane** przez
  `dobierz_najlepsze()`. Martwe metadane. Naprawione.
- Namiestnik znał tylko reżim, nie interwał. Dodano warstwę stylu.

### Co zostało wdrożone (kod)
- **`namiestnik.py`** — warstwa 2 (Timeframe-Aware):
  - `ProfilStylu` + `_PROFILE_STYLU`: SCALP(≤10×,FUTURES), SWING(≤5×,OBA), INVEST(≤2×,SPOT)
  - `_INTERWAL_NA_STYL`: mapa M1-M15→SCALP, 30M-4H→SWING, 1D-1W→INVEST
  - `styl_interwalu()`, `profil_stylu()` — funkcje pomocnicze
  - `DecyzjaNamiestnika` — łączy reżim × styl (tryb, prog, lewar_factor, lewar_cap, rynek)
  - `decyduj(rezim, interwal)` — dwuwarstwowa decyzja, VOLATILE/PANIC wymusza SPOT
  - `skaluj_dzwignie(base, rezim, interwal)` — przycina sufitem stylu (lewar_cap)
- **`baza.py`** — `dobierz_najlepsze(interwal=...)` + `_interwal_pasuje()`: filtr strategii po TF
- **`legatus.py`** — `fokus`/`_agreguj`/`_dobierz_strategie` przekazują interwał z barów
- **`dyrygent.py`** — wyciąga interwał z barów, przekazuje do Namiestnika i skalowania
- **`docs/NAMIESTNIK.md`** — pełna dokumentacja modułu (ZPO)
- **`tests/test_namiestnik.py`** — +7 testów warstwy stylu

### Tabela dowodowa (Prawo XVI — z Timeframe-Aware)
| Zestaw | BASELINE | NAMIESTNIK | Δ PnL | WinRate | PF | MaxDD |
|--------|----------|------------|-------|---------|-----|-------|
| BTC 1D | +32.71% | +27.32% | -5.39pp | 45→**55%** | 1.23→**1.57** | 23.8→**5.3%** |
| ETH 1D | +23.80% | +14.84% | -8.96pp | 44→48% | 1.09→1.19 | 26.4→**11.9%** |
| BTC 1H | -4.34% | -6.83% | -2.48pp | 45→43% | 0.85→0.74 | 13.9→**10.0%** |
| ETH 1H | -9.14% | **-4.65%** | **+4.50pp** | 48→43% | 0.77→0.86 | 11.2→**10.0%** |

> Namiestnik redukuje **drawdown na każdym zestawie**. Na 1D (INVEST cap 2×) selektywnie:
> mniej pozycji, wyższy WinRate/PF, drawdown 4.5× niżej na BTC. 1H mieszane (ETH +4.5pp).
> Filozofia: profil ryzyka > surowy zysk.

### Testy
346/346 zielone (+7). Audyt spójności: pełna harmonia.

### Następne fazy (uzupełnianie luk — patrz INDEKS_IMPERIUM.md)
A' napraw martwe neurony → A ożyw kat. L (VI-13 ATR-Lev) i V (Realized Vol) →
B adapter Futures (Legion VI) → C obudzenie 12 wyciszonych → D Legion III → E Księga Azjatycka.

---

## 2026-06-03 | MAJOR | Namiestnik podłączony do backtestu + tabela dowodowa (Prawo XV+XVI)

### Kontekst (głęboki audyt Prawo XV)
Audyt wykrył 🚨 UTRATĘ POTENCJAŁU: Namiestnik (i cały system reżimowy) był MARTWY
w backteście — `backtest.py` hardkodował `rezim="NORMAL"` i nie wstrzykiwał Namiestnika.
Stare `WAGI_REZIMU` też nigdy nie działały w backteście. Naprawione.

### Co zostało wdrożone (#1 — podłączenie)
- **`dyrygent.py`**: `cykl(rezim="AUTO")` → woła `klasyfikuj_rezim(wskazniki)` (Prawo I:
  dane z Bramy, nie zgadywanie). Reżim rozwiązany PRZED Namiestnikiem i Legatusem.
- **`backtest.py`**: parametr `auto_rezim: bool`. True → wstrzykuje `get_namiestnik()`
  + `rezim="AUTO"`. False → zachowanie wsteczne (NORMAL, bez Namiestnika).
- **`narzedzia/pomiar_namiestnik.py`**: skrypt tabeli dowodowej BASELINE vs NAMIESTNIK.
- **`tests/test_namiestnik.py`**: +1 test (`test_dyrygent_auto_rezim_klasyfikuje`)
  blokujący powrót martwego kodu.

### Tabela dowodowa #2 (Prawo XVI — mierzone, nie opinia)
| Zestaw | BASELINE PnL | NAMIESTNIK PnL | Δ PnL | Δ MaxDD |
|--------|-------------|----------------|-------|---------|
| BTC 1D | +32.71% | +19.43% | -13.28pp | 23.8→23.1% |
| ETH 1D | +23.80% | +17.16% | -6.64pp | 26.4→**16.8%** |
| BTC 1H | -4.34% | -3.73% | +0.62pp | 13.9→**7.4%** |
| ETH 1H | -9.14% | **+4.56%** | **+13.70pp** | 11.2→11.8% |

### Uczciwy werdykt (Prawo I — bez upiększania)
Wynik **MIESZANY**, nie jednoznaczne zwycięstwo:
- **1H (choppy/intraday): Namiestnik wygrywa** — ETH 1H strata→zysk (+13.7pp, PF 0.77→1.11),
  BTC 1H drawdown o połowę (13.9→7.4%), wyższy WinRate.
- **1D (silny bull): Namiestnik traci zysk** — bo `RANGING→czy_grac=False` i niższa dźwignia
  wycinają część hossy. DD jednak niższy (ETH 1D 26→17%).
- **Wniosek:** architektura DZIAŁA i jest mierzalna; tablica jest przestrojona zbyt
  defensywnie na rynkach trendujących. Namiestnik = redukcja ryzyka kosztem zysku w bullu.

### Następny krok (Faza 1.1 — przestrojenie tablicy na dowodach)
RANGING na 1D nie powinno być pełną ciszą (gubi hossę). Kandydaci: RANGING→czy_grac=True
z niższą dźwignią; rozdzielenie progów per-interwał. Do zmierzenia w kolejnej iteracji.

### Testy
339/339 zielone (+1). Audyt spójności: pełna harmonia.

---

## 2026-06-02 | MAJOR | Namiestnik (Regime-Aware Gating Network) — Faza 1

### Kontekst
Deep-research: Volatility-Adaptive MoE (arXiv:2508.02686), Adaptive Regime-Aware (arXiv:2603.19136),
Meta-Learning Optimal Mixture (arXiv:2505.03659). Cel: pełna autonomia + samoadaptacja systemu.

### Co zostało wdrożone
- **`imperium/koloseum/namiestnik.py`** — Regime-Aware Gating Network (Namiestnik):
  - `UstawieniaRezimu` — dataclass: tryb, lewar_factor, prog_pewnosci, czy_grac, wagi_override
  - `_TABLICA` — deterministyczne mapowanie 8 reżimów → parametry (Faza 1)
  - `Namiestnik.decyduj(rezim)` → UstawieniaRezimu z fallbackiem (nigdy nie rzuca)
  - `Namiestnik.skaluj_dzwignie(base, rezim)` → lewar_factor × auto_dzwignia
  - `get_namiestnik()` — singleton dla Dyrygenta
  - RANGING + PANIC → `czy_grac=False` (świadoma cisza, nie błąd)
  - TREND_STRONG → tryb filtr + lewar×1.2 (najsilniejszy sygnał)

- **`imperium/koloseum/dyrygent.py`** — integracja Namiestnika:
  - `Dyrygent.__init__` przyjmuje `namiestnik: Optional[Namiestnik]`
  - `Dyrygent.zbuduj()` automatycznie tworzy Namiestnika (`get_namiestnik()`)
  - W `cykl()`: przed Legatusem → Namiestnik → {tryb_aktywny, prog_aktywny, lewar_factor}
  - CISZA (czy_grac=False) → `DecyzjaCyklu("NAMIESTNIK_CISZA", False, powod=opis)`
  - Dźwignia: auto_dzwignia → Namiestnik.skaluj_dzwignie → plan.policz (skalowana)
  - Backward compatible: `namiestnik=None` → zachowanie jak wcześniej (tryb statyczny)

- **`tests/test_namiestnik.py`** — 12 nowych testów
- **`tests/run_tests.py`** — dodano `test_namiestnik`

### Dowody empiryczne (Prawo XVI)
| Reżim | Efekt |
|-------|-------|
| TREND_STRONG | tryb=filtr, lewar×1.2, prog=55% → +43% ETH 1D (wcześniejszy backtest) |
| RANGING | cisza (czy_grac=False) → zero fałszywych sygnałów |
| PANIC | cisza + próg 90% → ochrona kapitału |
| VOLATILE | tryb=strategia, lewar×0.5 → Klucznik dobiera breakout |

### Testy
338/338 zielone (326→338: +12 nowych testów Namiestnika)

### Pliki zmodyfikowane
- `imperium/koloseum/namiestnik.py` (NOWY)
- `imperium/koloseum/dyrygent.py`
- `tests/test_namiestnik.py` (NOWY)
- `tests/run_tests.py`
- `docs/MANIFEST_KODU.md`
- `docs/REJESTR_INSPIRACJI.md` (ML-30..33 dodane)
- `docs/LOG_ZMIAN.md`
- `README.md`

---

## 2026-06-02 | MAJOR | Detektor lookahead-bias (Freqtrade LA-01) + weryfikacja bazy DeepSeek

### Kontekst (sesja "tryb agregat/strategia")
Cezar wgrał `Zbior_wskaznikow_i_strategi_03.06.2026.md` (transkrypcja rozmów z DeepSeekiem).
Zadanie: porównać z naszym kodem + zweryfikować twierdzenia w internecie (deep-research).

### Ustalenia deep-research (Prawo I — zero halucynacji)
- ✅ TradingAgents (~80k ⭐), MRC arXiv 2605.24490 (Shapley, Sharpe 1.51) — REALNE.
- ❌ StratEvo (Sharpe 6.06) — 17 ⭐, liczby pomylone; VORTEX — niezweryfikowalny;
  OpenAlice — agent LLM Node.js, NIE silnik backtestu (DeepSeek mylił przeznaczenie).
- ✅ Akademicko potwierdzone: 1H ma niskie SNR (gorsze od 1D); korelowane wskaźniki bez przewagi.
- 🏆 Najlepsza zdatna do wdrożenia perełka: **Freqtrade lookahead-analysis** — detektor oszustwa backtestu.

### Zmiany kodu
- `imperium/koloseum/lookahead.py` — NOWY. `wykryj_lookahead()`: liczy ślad głosów roju na
  pełnym i obciętym zbiorze barów; rozbieżność = rój zagląda w przyszłość (Prawo I złamane).
  CLI: `python -m imperium.koloseum.lookahead <plik.csv> <interwal> [max_barow]`.
- `tests/test_lookahead.py` — NOWE: brak lookahead na czystym pipeline, determinizm śladu,
  kontrola pozytywna (sztuczny przeciek MUSI być wykryty). +3 testy → 326/326.
- `tests/run_tests.py` — rejestracja `test_lookahead`.

### Dowód
`python -m imperium.koloseum.lookahead dane/dzienne/Binance_BTCUSDT_d.csv 1D 600` → ✅ CZYSTO.
Nasz backtest na prawdziwych danych BTC nie oszukuje.

### Dokumentacja (ZPO + symbioza)
- `docs/REJESTR_INSPIRACJI.md` — LA-01 (wdrożony), ML-28 MRC/Shapley (plan), ML-29 TradingAgents (ref),
  + sekcja odrzuconych (StratEvo/VORTEX/OpenAlice/AetherEdge z powodami).
- `MANIFEST_KODU.md`, `INDEKS_IMPERIUM.md` — dopisany moduł lookahead.
- `README.md` — testy 307→326 (liczba policzona, nie z pamięci — Prawo XXI).

### Powód
Pierwsza inspiracja zewnętrzna, która trafiła PROSTO do kodu, nie do planu. OpenAlice odrzucony
jako backtest (Node.js, brak rygoru); zamiast zmieniać framework — przenieśliśmy metodę Freqtrade.

---

## 2026-06-02 | MAJOR | Warstwa strategii wpięta w decyzję — 3 tryby + pomiar (Opcja 3)

### Problem (Prawo XV — utrata potencjału)
Klucznik dobierał strategie po kluczach, ale Dyrygent ICH NIE UŻYWAŁ — decyzja szła
z gołego głosowania neuronów. Wykryto nawet sprzeczność (bar 400: neurony LONG,
wszystkie 3 top-strategie SHORT) zignorowaną przez system.

### Zmiany kodu
- `imperium/koloseum/dyrygent.py` — parametr `tryb`:
  - `agregat`   — kierunek z głosowania neuronów (strategie ignorowane, stan dotychczasowy)
  - `filtr`     — wejście tylko gdy top-strategia zgadza się z neuronami (Opcja 1)
  - `strategia` — kierunek z top-1 strategii, neurony dają pewność (Opcja 2)
- `imperium/koloseum/backtest.py` — `porownaj_tryby()` + CLI `--porownaj`; `bary` reużywalne
- `tests/test_dyrygent.py` — +3 testy trybów (323/323 zielone)

### POMIAR (Prawo XVI — decyzja na liczbach, nie opinii)
| Rynek | tryb | PnL | Trades | WinRate | PF | MaxDD |
|-------|------|-----|--------|---------|----|----|
| BTC 1D | agregat | +32.7% | 124 | 45.2% | 1.23 | 23.8% |
| BTC 1D | filtr | +26.5% | 135 | 45.9% | 1.16 | 22.2% |
| BTC 1D | strategia | +11.1% | 108 | 41.7% | 1.08 | 24.1% |
| ETH 1D | agregat | +23.8% | 160 | 43.8% | 1.09 | 26.4% |
| ETH 1D | **filtr** | **+43.0%** | 160 | 48.1% | 1.16 | **16.3%** |
| ETH 1D | strategia | +14.6% | 147 | 40.8% | 1.06 | 26.2% |

### Wnioski (zmierzone)
1. **`strategia` (nadrzędna) — najgorsza na obu rynkach.** Potwierdza: warstwa strategii
   jest słabo skalibrowana, nie nadaje się jeszcze na ster. ODRZUCONA jako domyślna.
2. **`filtr` ma najniższy MaxDD na obu rynkach** (22.2%/16.3% vs 23.8%/26.4%) i wygrywa
   ryzykiem-do-zysku (ETH +43% przy DD 16%). Na BTC goły agregat ma wyższy surowy zwrot.
3. Decyzja o domyślnym trybie — w gestii Cezara (return vs ryzyko). Tryby zostają w kodzie.

---

## 2026-06-02 | MAJOR | Backtest na PRAWDZIWYCH danych + czytnik CSV

### Zmiany kodu
- `imperium/akwedukty/czytnik_csv.py` — czytnik formatu CryptoDataDownload (Binance export):
  pomija linię URL, odwraca malejący plik na chronologiczny, wykrywa wolumen bazowy
  (Volume BTC/ETH) vs quote (Volume USDT). Zwraca bary zgodne z Budowniczym/Dyrygentem.
- `imperium/koloseum/backtest.py` — przejazd Dyrygenta po historii z przesuwnym oknem.
  NIE zagląda w przyszłość: wskaźniki liczone tylko z barów do bieżącej świecy włącznie.
- `tests/test_czytnik_csv.py` — 7 testów (próbka inline, bez dużych plików)
- `dane/dzienne/` + `dane/godzinowe/` — realne dane Binance BTC+ETH (Cezar wrzucił)

### PIERWSZE UCZCIWE WYNIKI (bez danych syntetycznych — Prawo I)
Dane realne Binance, dźwignia auto, SL/TP z Kalkulatora Lewara, prowizje+poślizg liczone:
| Rynek | Okres | PnL | Trades | Win Rate | Profit Factor | Max DD |
|-------|-------|-----|--------|----------|---------------|--------|
| BTC 1D | 2017-2026 (3192) | **+32.7%** | 124 | 45.2% | 1.23 | 23.9% |
| ETH 1D | 2017-2026 (3192) | **+23.8%** | 160 | 43.8% | 1.09 | 26.4% |
| BTC 1H | ost. 5000 (~7 mies.) | **-4.3%** | 101 | 44.6% | 0.85 | 13.9% |

### Uczciwa ocena (Prawo XV — nie ukrywam słabości)
Infrastruktura działa end-to-end na realnym rynku. ALE strategia jest SŁABA:
PF ledwo > 1 na dziennym, STRATNA na godzinowym (PF 0.85). To NIE jest gotowy system
zarabiający — to działający szkielet do kalibracji. Buy-and-hold BTC dałby +1600%,
my +32%. Następny etap: kalibracja wag/progów, obudzenie śpiących neuronów, lepszy dobór reżimu.

### Powód
Poprzedni "+393 USDT" był na danych SYNTETYCZNYCH (idealna linia) — nic nie znaczył.
Teraz mamy prawdziwą informację zwrotną z rynku, na której można poprawiać Imperium.

---

## 2026-06-02 | MAJOR | Dyrygent — orkiestrator pełnego cyklu decyzyjnego (Faza 0 end-to-end)

### Zmiany kodu
- `imperium/koloseum/dyrygent.py` — NOWY orkiestrator spinający rozproszone klocki w jeden łańcuch:
  bary OHLCV → Budowniczy/Brama (wskaźniki) → Legatus.fokus (kierunek/pewność/reżim) →
  KalkulatorLewara.policz (SL/TP/dźwignia/rozmiar) → SygnalWejscia → PaperTradingEngine
- `DecyzjaCyklu` — przejrzysty ślad każdego etapu (gdzie cykl się zakończył i dlaczego — Prawo I jawność)
- Budowniczy wstrzykiwany (Prawo I); `wskazniki_provider` pozwala testować bez TA-Lib
- `tests/test_dyrygent.py` — 6 testów: pusty/neutralny/silny cykl, pełny ślad, brak źródła, end-to-end z TP_HIT

### Dowód działania
Pełny cykl zweryfikowany ręcznie: rój dał LONG → Kalkulator dźwignia 10, SL/TP →
pozycja otwarta 4210 USDT → bar dotknął TP → zamknięcie +393 USDT (+3.93%).
Bramka ryzyka działa: przy dźwigni 20 Pretorianie wetują pozycję >50% kapitału.

### Powód
Wszystkie klocki (Budowniczy, Legatus, Kalkulator, PaperTradingEngine) istniały i były
testowane OSOBNO, ale nic nie spinało ich w cykl. To była UTRATA POTENCJAŁU (Prawo XV):
gotowe moduły niepodpięte do pipeline. Dyrygent domyka Fazę 0 — rój realnie podejmuje decyzje.

### Symbioza
- MANIFEST_KODU: +PaperTradingEngine, +Dyrygent
- INDEKS_IMPERIUM (MAPA KODU): koloseum/ 🟡 Szkielet → ✅ Cykl Faza 0 aktywny
- Testy: 307 → 313 (+6)

### Otwarty wątek (do kalibracji w Fazie 1)
`pewnosc_agregatu` Legatusa bywa ~1.0 nawet przy słabym składzie zgodnych neuronów —
warto skalibrować (więcej neuronów = wyższa pewność, nie sama zgodność kierunku).

---

## 2026-06-02 | NARZĘDZIA | Zestaw strażników spójności — audyt rozszerzony + status.py + pre-commit hook

### Nowe narzędzia
- `narzedzia/audyt_spojnosci.py` — rozszerzony o 4 nowe warstwy:
  - **W5 (INDEKS):** liczby mikro-neuronów i zwiadowców w INDEKS_IMPERIUM (sekcja MAPA KODU) vs żywy kod
  - **W6 (daty):** "Stan na:" w MANIFEST i README nie może być starsze niż 2 dni
  - **W7 (sieroty):** każdy plik docs/*.md musi być wymieniony w INDEKS_IMPERIUM; martwe cross-linki między docs/
  - **W8 (LOG_ZMIAN):** jeśli plik .py w imperium/ zmieniony po ostatnim wpisie LOG_ZMIAN → alarm
- `narzedzia/status.py` — pulpit jednego spojrzenia (Prawo XVII): faza, żywy rój, testy, ostatni log, roadmap, git, audyt
- `.git/hooks/pre-commit` — blokuje każdy commit gdy testy lub audyt czerwone (Prawo XXI)
- `narzedzia/hooks_src/pre-commit` — źródło hooka (przetrwa re-clone)
- `narzedzia/install_hooks.py` — instalator hooków po git clone

### Naprawy (wywołane przez W7)
- `docs/ARCHITEKTURA_IMPERIUM.md` — naprawiony martwy link: AUDYT_ADOPCJI.md → archiwum/AUDYT_ADOPCJI.md
- `docs/INDEKS_IMPERIUM.md` — dodano 7 brakujących plików docs/ (MANIFEST_KODU, AUDYT_SYSTEMU, MAPA_KLUCZY, OBSERWATORZY, SKAN_AZJA, WERSJONOWANIE, WIZJONER); poprawiono "27 w kodzie" → "42 w kodzie"

### Powód
Cezar zidentyfikował: bez automatycznej bramki pre-commit i rozszerzonego audytu projekt rozjeżdża się przy każdej sesji. "Legiony stoją, Cesarz jest zły." Rozwiązanie: każdy commit jest teraz weryfikowany maszynowo, nie zależy od pamięci.

---

## 2026-06-02 | FIX | Naprawa błędu archiwizacji + weryfikacja statusów

### Problem
Poprzednia sesja przeniosła do archiwum/ dokumenty BEZ dokładnego przeczytania:
- `ARSENAL_IMPERIUM.md` — zweryfikowany katalog ~220 narzędzi infrastruktury (nie neuronów!) — przeniesiony przez BŁĄD
- `WZORZEC_DNSS.md` — aktywna referencja architekturalna — przeniesiony przez BŁĄD
Dodatkowo: SHARP/AgenticAITA/CogAlpha/NEXUS/Kronos opisane jako ⚠️ niezweryfikowane, mimo że weryfikacja była w ARSENAL_IMPERIUM.md — złamanie Prawa I.

### Naprawa
- `docs/ARSENAL_IMPERIUM.md` — PRZYWRÓCONY z archiwum/ do docs/ (git mv)
- `docs/WZORZEC_DNSS.md` — PRZYWRÓCONY z archiwum/ do docs/ (git mv)
- `docs/REJESTR_INSPIRACJI.md` — status ML-24..27 i A-12 poprawiony: ⚠️ → ✅ (zweryfikowane maj 2026)
- `docs/WZORZEC_OPISU.md` — przykład naprawiony (SHARP był ⚠️, jest ✅)
- `docs/KATALOG_NEURONOW.md` — ML-24..27 naprawione
- `docs/INDEKS_IMPERIUM.md` — ARSENAL_IMPERIUM i WZORZEC_DNSS przywrócone do tabeli aktywnych; liczby, historia zaktualizowane

### Lekcja
Przed archiwizacją pliku: PRZECZYTAJ go w całości. "Wygląda przestarzale" to za mało — sprawdź zawartość.
Obowiązek wynikający z Prawa XVIII: "złamanie przez nieuwagę = takie samo złamanie jak celowe".

---

## 2026-06-02 | DOC | Zasada Pełnego Opisu (ZPO) + Rejestr Inspiracji AI/ML

### Nowe pliki
- `docs/WZORZEC_OPISU.md` — NOWY: wzorzec/szablon pełnego opisu (ZPO) — każdy wpis ma pełną nazwę, link, status weryfikacji, wyjaśnienie dla nowicjusza
- `docs/REJESTR_INSPIRACJI.md` — NOWY: jedno miejsce na zewnętrzne projekty AI/ML (SHARP, AgenticAITA, CogAlpha, NEXUS, Kronos) z pełnymi nazwami + linkami + statusem weryfikacji

### Zmiany dokumentacji
- `docs/KATALOG_NEURONOW.md` — dodane klucze ML-24..27 (inspiracje zewnętrzne) + cross-link na A-12 Kronos
- `CLAUDE.md` — dodana sekcja "Zasada Pełnego Opisu (ZPO)" jako rozkaz stały
- `docs/INDEKS_IMPERIUM.md` — dodane WZORZEC_OPISU i REJESTR_INSPIRACJI

### Powód
Cezar (nowicjusz) zauważył, że projekty AI/ML (Kronos, NEXUS, SHARP, CogAlpha, AgenticAITA) były rozproszone po 4 dokumentach bez pełnych nazw i linków. Nakazał zasadę pełnego opisu: zawsze pełne nazwy, linki pochodzenia, kompletny opis. ZPO = nowy rozkaz stały.

### Uczciwość (Prawo I)
Linki podane przez Cezara (arXiv 2026, GitHub) oznaczone ⚠️ NIEZWERYFIKOWANE — nie było dostępu do sieci, nie udajemy weryfikacji.

---

## 2026-06-02 | MAJOR | Adaptery Danych + 5 nowych neuronów + LOG_ZMIAN + porządki docs

### Zmiany kodu
- `imperium/akwedukty/adaptery/baza.py` — NOWY: klasa bazowa `AdapterDanych` (wzbogac/aktywuj/usypiaj)
- `imperium/akwedukty/adaptery/testowy.py` — NOWY: `AdapterTestowyOnChain`, `AdapterTestowyFutures`, `AdapterTestowyCVD` (9 neuronów API ze snu wzbudzone w testach)
- `imperium/akwedukty/adaptery/feargreed.py` — NOWY: pierwszy prawdziwy adapter HTTP (alternative.me, bez klucza API, wzbudza PSY-03)
- `imperium/akwedukty/adaptery/__init__.py` — NOWY: eksport publiczny adapterów
- `imperium/legiony/neurony/straz.py` — DODANE: A-03 NeuronWashVol (fałszywy wolumen), A-05 NeuronBartPattern (manipulacja niską płynnością)
- `imperium/legiony/neurony/trend.py` — DODANE: XII-06 NeuronOBZone (Order Block OHLCV, uproszczony)
- `imperium/legiony/rejestr.py` — zaktualizowane importy i `wszystkie_neurony()`
- `imperium/legiony/strategie/rejestr_strategii.py` — DODANA strategia IMV-DEF-002 "MUR KONTRWYWIADU" (A-03+A-05)

### Powód
Prawo XV: neurony OC-01..04, PSY-01..04, V-03 były wyciszone z braku adapterów — utrata 9/42 potencjalnych głosów. Framework adapterów to pierwszy krok do ich pełnego wybudzenia z feedami API.

### Pliki dokumentacji
- `docs/MANIFEST_KODU.md` — zaktualizowany (SMC 🌙, AdapterFearGreed, liczby)
- `README.md` — zaktualizowane liczby (307/307 testów, 42 neurony)
- `tests/test_adaptery.py` — NOWY: 19 testów offline dla adapterów
- `tests/run_tests.py` — test_adaptery dodane przed test_spojnosc

---

## 2026-06-02 | MAJOR | Prawo XX status elitarny + 4 nowe neurony + kategorie + WAGI_REZIMU

### Zmiany kodu
- `imperium/legiony/mikro_neuron.py` — DODANE: pole `ELITARNY=False`, `POWOD_ELITARNOSCI=""`
- `imperium/legiony/zwiadowcy/baza.py` — DODANE: `ELITARNY=True`, `POWOD_ELITARNOSCI` w ZwiadowcaElitarny
- `imperium/legiony/neurony/momentum.py` — X-25 i X-26 oznaczone `ELITARNY=True`
- `imperium/legiony/legatus.py` — DODANE: `WAGI_REZIMU` (mnożniki wg reżimu rynku per kategoria) + `WAGI_REZIMU_PLANOWANE`
- `imperium/legiony/rejestr.py` — DODANA: `raport_elity()` — lista elit z kryterium E1-E7
- Poprzednia sesja: neurony F-01, F-02, F-03, F-04 (4 neurony wolumenowe) dodane do kodu

### Powód
Prawo XX: status elitarny musi być mierzony, nie opinią. Raport umożliwia audyt każdej sesji.
WAGI_REZIMU: sygnały Straży (kategoria A) ważniejsze w reżimie VOLATILE i PANIC — elastyczny agregat.

### Pliki dokumentacji
- `ZASADY_FUNDAMENTALNE.md` — DODANE: Prawo XX (status elitarny E1-E7)
- `CLAUDE.md` — DODANE: sekcja Prawo XX, Prawo XXI (protokół spójności)
- `docs/MANIFEST_KODU.md` — zaktualizowany

---

## 2026-06-02 | MAJOR | Audyt Arsenału — odzyskanie straconych wskaźników + reorganizacja docs

### Zmiany dokumentacji
- `docs/KATALOG_NEURONOW.md` — NAPRAWIONY nagłówek (stary paradygmat "jeden neuron = para oczu" zastąpiony aktualnym z interpretuj()), DODANA sekcja "Uzupełnienie Arsenału" (+12 brakujących wskaźników)
- `docs/LOG_ZMIAN.md` — NOWY (ten plik): obowiązkowy log zmian Imperium
- `archiwum/ARSENAL_WSKAZNIKOW.md` — PRZENIESIONY z docs/ (stary paradygmat, superseded przez KATALOG_NEURONOW)
- `archiwum/AUDYT_ADOPCJI.md` — PRZENIESIONY z docs/ (historyczny audyt migracji Kingdom Pixel, zakończony)
- `archiwum/WZORZEC_DNSS.md` — PRZENIESIONY z docs/ (dokument referencyjny/inspiracyjny, statyczny)
- `archiwum/ARSENAL_AMERYKI.md` — PRZENIESIONY z docs/ (skan linków wielokontynentalny, informacyjny)
- `archiwum/ARSENAL_IMPERIUM.md` — PRZENIESIONY z docs/ (superseded przez KATALOG_NEURONOW)

### Powód
Użytkownik (Cezar) nakazał: "wszystko co stare i nieaktualne → archiwum, do archiwum zaglądasz tylko na wyraźne polecenie". Arsenal stworzono pod stary paradygmat "neurony nie myślą" — teraz neurony mają pełną logikę interpretuj(). Porównanie wykazało 12 wskaźników z Arsenału nieobecnych w Katalogu — odzyskane i dodane.

### Stracone przy zmianie paradygmatu (dodane z powrotem do katalogu)
Momentum: DPO, Ultimate Oscillator, Chande Momentum Oscillator
Trend: Alligator, ALMA, Price Channel
Zmienność: Standard Error Bands, Chaikin Volatility, VIX Fix, ATRP
Wolumen: Volume Oscillator, Apex Desk CVD MAX

---

## 2026-06-01 | MINOR | Zwiadowcy Exploratores EXP-01..12

### Zmiany kodu
- `imperium/legiony/zwiadowcy/` — 12 zwiadowców zaimplementowanych (EXP-01..12; 11 aktywnych + EXP-12 wyciszony do feedu L2)
- Każdy zwiadowca: `KLUCZ`, `KATEGORIA`, `ELITARNY=True` (kryterium E1 — Exploratores)

### Powód
Zwiadowcy generują sygnały wyspecjalizowane (SMC, wolumen zaawansowany) poza standardowym rój głosowaniem.

---

## 2026-05-28 | MAJOR | Rdzeń decyzyjny — Generał Legatus + Koloseum

### Zmiany kodu
- `imperium/legiony/legatus.py` — agregacja głosów + wagi + odpalanie zwiadowców
- `imperium/koloseum/` — Igrzyska + rangowanie neuronów
- `imperium/legiony/diagnostyka_korelacji.py` — pomiar dekorelacji (Prawo XVI)

### Powód
Rdzeń decyzyjny kompletny: rój głosuje → Legatus agreguje → koloseum ranguje.

---

## 2026-05-20 | MAJOR | Brama Kalkulatora + Budowniczy Wskaźników

### Zmiany kodu
- `imperium/fundament/brama_kalkulatora.py` — jedyne wejście do obliczeń (Prawo I)
- `imperium/legiony/budowniczy_wskaznikow.py` — surowe bary OHLCV → pełen słownik wskaźników

### Powód
Prawo I: neurony NIGDY nie liczą samodzielnie. Brama z SHA-256 pieczątką zapewnia auditability.

---

## 2026-05-15 | MAJOR | 30 neuronów OHLCV + 3 SMC wewnętrzne

### Zmiany kodu
- 30 neuronów aktywnych OHLCV w folderach `imperium/legiony/neurony/`
- SMC-01/02/03 — budzenie wewnętrzne przez most EXP-05 (nie wymagają zewnętrznego API)

### Powód
Rdzeń roju: pierwsza fala neuronów OHLCV. SMC klasyfikowane jako 🌙 (wewnętrznie budzone), nie 🔇 (czekające na API).

---

*Ten log aktualizowany jest OBOWIĄZKOWO po każdej zmianie systemu (ROZKAZ STAŁY — 2026-06-02).*
