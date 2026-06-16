# 🔍 GŁĘBOKI AUDYT IMPERIUM — wizja „łowcy okazji" vs rzeczywistość kodu

> **Stan na:** 2026-06-14 · **Metoda:** audyt 4-frontowy (kod skanera/tryby, kod zdarzeń/prawdopodobieństwo, dokumenty, research internetowy) + weryfikacja własna · **Autor:** sesja audytowa na rozkaz Cezara

## 0. Sedno — reframe oceny (rozkaz Cezara 2026-06-14)

**NIE oceniamy systemu przez „9 lat jednej waluty, słaby okres → strata".** To błędna miara.
Imperium ma być **ŁOWCĄ OKAZJI wielowalutowym**:

- skanuje WIELE coinów naraz, **rankuje najlepsze okazje** i wybiera kilka-kilkanaście najlepszych,
- różne tryby: **skalp / swing / invest / spot** dobierane do sytuacji,
- **mało trade'ów o wysokiej pewności** (nie 1300/mies.), z **podkręconym lewarem** na najmocniejszych,
- decyzja **long / short / spot / invest**, **% kapitału**, a zysk → **pula łupów (compounding)**,
- łapanie **gwałtownych ruchów 20-30%/doba** i **dołków na wielu interwałach** (1m/5m/15m/1h/4h/1d),
- krótkie interwały i finalna kalibracja → **na LIVE z auto-uczeniem**.

Pełny backtest 9-letni jednej waluty służy tylko walidacji mechaniki, NIE jest werdyktem o zyskowności.

---

## 1. CO ISTNIEJE I DZIAŁA (filary wizji — zweryfikowane w kodzie)

| Element wizji | Status | Dowód w kodzie |
|---|---|---|
| **Radar wielowalutowy** | ✅ żywy, wpięty | `radar_rynku.py` (BTC_TREND, BTC_DOMINACJA, PRZEPLYW_KAPITALU, STRES_KORELACJI); wpięty `dyrygent.py`, `petla_live.py`, konsumowany przez neurony |
| **Tryby skalp/swing/invest** | 🟡 częściowo | `namiestnik.py` `ProfilStylu` + `_INTERWAL_NA_STYL` (SCALP lewar≤10/FUTURES, SWING≤5/OBA, INVEST≤2/SPOT); wpięte w skalowanie lewara |
| **Lewar od pewności** | ✅ | `kalkulator_lewara.auto_dzwignia` (0→2→5→10→15→20×) × reżim × Namiestnik × cap stylu |
| **Kierunek long/short** | ✅ | agregat neuronów w `dyrygent.cykl`, split zmierzony 51/49 (W-314) |
| **Wykrywanie pomp (przed)** | ✅ | `Z-02 NeuronPumpDetect` — cicha akumulacja przed pumpem (vol-spike+wąska świeca+OBV) |
| **Silnik zdarzeń (Augur)** | ✅ kod / 🚨 martwy live | `kronikarz_zdarzen.py` — katalog zdarzeń, kalendarz FOMC 2026, event-study, `prob_wzrostu`; neuron AUG-01 |
| **Kelly / sizing** | ✅ | `iustitia.py` half-Kelly + portfolio heat; `kalkulator_lewara.skew_kelly` |
| **Pamięć cross-session** | ✅ read-path żywy | `pamiec_refleksyjna.py` + `ksiega_wad.ucz_z_pamieci()` bootstrap w `petla_live.py:214` |
| **Auto-uczenie online** | 🟡 częściowo | MWU + Synapsy live; Igrzyska + Drift gotowe ale domyślnie OFF |
| **Tryb łupieżczy (Praeda)** | 🟡 opt-in OFF | `praeda.py` — auto-skalowana agresja w confluence |
| **Filtr Asymetrii Reżimu** | ✅ nowy (W-314) | tnie krwawienie w chopie −38% OOS |

**Wniosek:** aparat PER-PARA jest mocny i kompletny. Radar to najlepiej zrealizowany element wizji.

---

## 2. 🚨 NAJWIĘKSZA LUKA — brak skanera/rankingu okazji (serce wizji)

**System jest dziś „N równoległych botów jednowalutowych", NIE „łowcą najlepszych okazji w koszyku".**

- `backtest_portfel` i `petla_live.handluj_live` iterują po WSZYSTKICH parach; każda gra niezależnie.
- `max_otwartych = len(symbole)` → zero selekcji, każdy symbol może mieć pozycję jednocześnie.
- Alokacja = equal-weight lub inverse-vol (`wagi_inwerse_vol`) — **NIE ranking jakości okazji**.
- „Ranking" w kodzie (Igrzyska) dotyczy neuronów (accuracy), nie okazji rynkowych.

**Brakuje warstwy nadrzędnej, która:** skanuje koszyk → liczy scoring każdego setupu →
sortuje → wybiera TOP-N → tylko te wchodzą. To dokładnie różnica między „puszczeniem w
automacie na jednej walucie" (czego Cezar NIE chce) a „łowcą okazji" (czego chce).

---

## 3. LUKI SZCZEGÓŁOWE (czerwone alarmy Prawa XV)

| # | Luka | Status | Priorytet |
|---|---|---|---|
| L1 | **Skaner + ranking okazji cross-symbol, selekcja TOP-N** | 🔴 BRAK | **NAJWYŻSZY** |
| L2 | **AdapterKronikarz odpięty** → AUG-01 martwy głos, cały Augur nieaktywny live | 🚨 martwy | WYSOKI (tani fix) |
| L3 | **Detektor zaistniałego ruchu 20-30%/doba (ROC) + ocena „gonić czy nie"** | 🔴 BRAK | WYSOKI |
| L4 | **Detektor dołka multi-TF (RSI divergence + wsparcie + confluence)** | 🔴 BRAK | WYSOKI |
| L5 | **Skalibrowane P(sukces) per setup (Bayesian Beta-Binomial) w decyzji** | 🔴 BRAK | ŚREDNI |
| L6 | **Compounding / „pula łupów" — reinwestycja zysku w rozmiar** | 🔴 BRAK modułu | ŚREDNI |
| L7 | **Realna egzekucja SPOT/INVEST** (dziś metadana, wszystko torem lewarowanym) | 🟡 deklaracja | ŚREDNI |
| L8 | **Igrzyska + Drift wyłączone live** — gotowe, nieużyte | 🟡 OFF | NISKI |
| L9 | **Kategorie K (makro/DXY) i G (geo/Azja)** — zero neuronów | 🔴 papier | NISKI |

---

## 4. 🔬 ROZBIEŻNOŚCI DOKUMENT↔KOD (naruszenia Prawa XXI — do auto-naprawy)

Audyt `audyt_spojnosci.py` daje „pełną harmonię", ale **nie sprawdza wewnętrznej spójności
liczb w MANIFEST** — przez co przeszły:

1. **MANIFEST_KODU.md sprzeczny wewnętrznie:** nagłówek „63 neurony", ale dalej „== 60",
   „(60/299)", suma RAZEM „56". Trzy różne liczby (63/60/56) w jednym pliku.
2. **Strategie:** MANIFEST „15 (klucze 20)" vs kod **18 (klucze 26)** (zweryfikowane `wszystkie_strategie()`=18).
3. **README (2026-06-13, 978 testów, 63) wyprzedza MANIFEST (2026-06-12, 743 testy)** i ROADMAP (62 neurony).
4. **KATALOG_NEURONOW.md** nagłówek „299" vs treść „274/142/129".
5. **KATALOG_STRATEGII.md** — 123 strategie, wszystkie status SZKIC (zero przez Koloseum).

**Rekomendacja:** rozszerzyć `audyt_spojnosci.py` o Warstwę 14 (wewnętrzna spójność liczb
w MANIFEST) — by takie rozjazdy łapać automatycznie, nie ręcznie.

---

## 5. 📚 RESEARCH — techniki do implementacji (OHLCV-only, źródła zweryfikowane przez agenta web)

Rekomendowana architektura modułu **ŁOWCA OKAZJI** (potok):

1. **Ranking koszyka** — cross-sectional momentum (zwrot 7/30d, sortuj, top-decyl) + relative
   strength vs BTC + opportunity z-score (momentum+RS+ADX>25+volume). Źródła: FXEmpire,
   CoinGlass RSI Heatmap, stoic.ai.
2. **Filtr anomalii/pomp** — volume z-score (z>3-4), volatility breakout (BB squeeze→expansion).
   Badania: arXiv 2503.08692, 2412.18848 (+90% high & +400% vol; z-score top-5 w 55,8%).
3. **Confluence dołka multi-TF** — bullish RSI divergence + wsparcie + zgodność wielu TF.
   Źródła: LuxAlgo, XS confluence.
4. **Bayesian P(sukces) per setup** — Beta-Binomial, prior Beta(α,β), update po trade;
   `scipy.stats.beta`. Źródła: QuantInsti, Bayesian Kelly.
5. **Sizing** — fractional Kelly (¼-½) × conviction (confluence/Bayes win-rate) + compounding.
   Źródła: Coriva, Zerodha, enlightenedstocktrading.

⚠️ **Weryfikacja (Prawo I):** liczby z badań (55,8%; +90%/+400%; half-Kelly ~75% wzrostu)
pochodzą ze źródeł, NIE zweryfikowane niezależnie — progi trzeba przebacktestować na własnych danych.
Jedyne wąskie gardło danych: anty-pump&dump wymaga order-flow/on-chain (reszta z OHLCV+volume).

---

## 6. REKOMENDOWANA KOLEJNOŚĆ (do decyzji Cezara — Prawo XVIII)

**Etap A (tanie naprawy, pewne, Prawo XV):**
- A1. Wepnij `AdapterKronikarz` do adapterów live → ożywia AUG-01 i cały Augur (L2).
- A2. Napraw rozbieżności MANIFEST/README/ROADMAP (Prawo XXI) + Warstwa 14 audytu.

**Etap B (serce wizji — nowy moduł ŁOWCA OKAZJI):**
- B1. `SkanerOkazji` — ranking koszyka + opportunity score + selekcja TOP-N (L1).
- B2. Detektor ruchu dobowego ROC ±20-30% + detektor dołka multi-TF (L3, L4).
- B3. Bayesian kalibracja P(sukces) per setup z pamięci (L5).
- B4. Compounding / pula łupów (L6).

**Etap C (LIVE + auto-uczenie):**
- włącz Igrzyska/Drift live, podłącz krótkie interwały (15m/5m/1m), auto-kalibracja progów.

**Backtest reframe:** zbuduj **backtest cross-sectional** (dla całego uniwersum w czasie T:
czy skaner wybrał zwycięzców?) zamiast per-para 9-letniego — to właściwa miara łowcy okazji.
