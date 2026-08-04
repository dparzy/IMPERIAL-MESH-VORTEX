---
kategoria: CONSILIUM
typ: zywy
wlasciciel: —
bez_wlasciciela: "tresc zapytan zwiadu — material dla ludzi i modeli, nie opis modulu"
stan_na: 2026-08-02
powod_istnienia: "Gotowe frazy wyszukiwania dla Cezara — zwiad po literaturze celowany w ZMIERZONE luki Imperium, z kryterium oceny trafienia i listą tego, czego NIE szukać."
---
# 🔭 ZWIAD — ZAPYTANIA CELOWANE W NASZE LUKI

**Do czego to jest:** Cezar wrzuca prace do `wrzutnia/`, Architekt je segreguje. Ten dokument
zamienia wrzucanie **losowe** na **celowane**. Każda fraza jest podpięta pod zmierzoną lukę
Imperium i pod pozycję z `ROADMAP_IMPERIUM.md`.

**Zmierzona skuteczność wrzutów losowych (7 plików, 2026-07-30):** 2 złote · 3 srebrne
(2 warunkowe) · 2 odpady. Wniosek: warto wrzucać, ale celowanie powinno podnieść plon.

> ⚠️ **UCZCIWOŚĆ O TYM PRZYRZĄDZIE (LEX TALARUS).** Ta lista została wydana Cezarowi
> **przed zmierzeniem jej samej**. Pierwszy pomiar: fraza z Priorytetu 1 wyciągnęła pracę
> z `q-fin.RM` (ryzyko po stronie giełdy) zamiast kalibracji egzekucji po stronie biorącego —
> **rozkalibrowanie potwierdzone przy n=1**. Frazy oznaczone ✅ były użyte i dały trafienie;
> ❌ dały zły poddział domeny; brak znaku = **jeszcze nieużyte, więc niezmierzone**.

## Jak używać

1. Wejdź na [arxiv.org/search/advanced](https://arxiv.org/search/advanced), zaznacz **All fields**,
   „Date range" od **2025-01-01**. Cudzysłowy zostaw — wymuszają frazę.
2. Te same stringi działają w [Google Scholar](https://scholar.google.com) i
   [huggingface.co/papers](https://huggingface.co/papers).
3. Wklejaj **po jednej**. Wrzucaj **2–4 PDF-y naraz** — zbieżność między pracami dała nam
   więcej niż każda z osobna.
4. **PDF, nie czat.** Zmierzone dwukrotnie: rozmowa z modelem **zdejmuje zastrzeżenia**
   z prac (VeNRA — wyrwany kontekst baseline'u; FinAbstain — usunięta etykieta „simulated").

---

## 🥇 P1 — KOSZT EGZEKUCJI *(największa nieznana dla win rate; ROADMAP D3/D4)*

Poślizg i prowizja są **ZAŁOŻONE, nie zmierzone**. Złe założenie odwraca znak wyniku.

| # | Fraza | Trafienie = |
|---|---|---|
| 1.1 | `slippage model "bar data" OHLCV approximation without order book` | **najważniejsza w całym dokumencie** — model poślizgu bez księgi zleceń, na samych świecach. To jest wprost D4 |
| 1.2 | `"implementation shortfall" retail order size cryptocurrency execution` | koszt z perspektywy **biorącego**, nie giełdy |
| 1.3 | `backtest live trading performance gap execution assumptions crypto` | zmierzony rozjazd backtest↔rzeczywistość |
| 1.4 | `"realized slippage" measurement retail taker orders exchange comparison` | ktoś **zmierzył** poślizg na realnych fillach |
| 1.5 | `"fill probability" limit order execution model crypto futures` | prawdopodobieństwo wypełnienia zlecenia limit — decyduje maker vs taker |
| 1.6 | `"transaction cost" "perpetual futures" funding maker taker net return` | pełny rachunek na perpetualach (prowizja + funding + poślizg) |
| 1.7 ❌ | `"slippage" "calibration" backtest crypto fills` | dała SaR 2603.09164 — **zły poddział**: ryzyko giełdy, nie kalibracja biorącego |

### 📏 POMIAR 2026-08-02 — testowano RDZENIE, nie frazy (i to jest cała lekcja)

Cezar szukał **gołymi terminami**: `implementation shortfall` oraz `slippage` — **bez
kwalifikatorów**, które w tym dokumencie stoją obok nich (`retail`, `cryptocurrency`,
`"bar data" OHLCV`, `without order book`). Dlatego **frazy 1.1, 1.2 i 1.4 pozostają
NIEZMIERZONE** — nie wolno postawić przy nich ani ✅, ani ❌. Zmierzyliśmy co innego
i coś ważniejszego: **jak zachowuje się sam rdzeń**.

| plon | rdzeń | co przyszło | perspektywa |
|---|---|---|---|
| `1205.3482v6` Labadie–Lehalle | *implementation shortfall* | Target Close i IS w ramach Almgren-Chriss | **duże zlecenie instytucjonalne** (35× „market impact", 0× crypto/retail/OHLCV) |
| `2003.04425v1` Çetin–Waelbroeck | *implementation shortfall* | IS przy informed trading | **wymaga księgi L2** (68× „order book") |
| `2603.07752v1` Barzykin (HSBC) | *slippage* | sterowanie poślizgiem i odrzuceniami | **dealer / market maker** |

**Trzy zapytania, trzy prace ze strony DOSTAWCY płynności — a licząc SaR z 1.7: cztery.**
To nie pech, to własność korpusu: literatura o koszcie egzekucji jest pisana **przez
instytucje i dla instytucji**; „retail crypto taker" nie jest w niej przedmiotem badań.

> **Wniosek odwrotny do intuicyjnego — kwalifikatory w tym dokumencie NIE są ozdobą.**
> Pomiar pokazał dokładnie to, przed czym miały bronić dopiski `without order book`
> i `retail`. Gołe terminy sprowadzają zwiad na stronę podażową. Frazy zostają
> **niezmierzone, ale uwiarygodnione** — trzeba je wkleić w CAŁOŚCI, z cudzysłowami.

**Co te prace dały mimo złego poddziału — przez zaprzeczenie:** skoro koszt u Almgren-Chriss
rośnie z **impaktem własnego zlecenia**, a nasze zlecenia rynkiem nie ruszają, to nasz koszt
egzekucji **nie jest problemem optymalizacyjnym** — jest arytmetyką *spread + prowizja +
funding*. Szukaliśmy modelu tam, gdzie wystarczy rachunek; a tego rachunku i tak nie zamkniemy
z literatury, tylko **pomiarem na MEXC** (wraca największa luka: zero realnych zleceń).

**Kandydaci na przeformułowanie P1** (jeszcze nieużyte): `effective spread estimation from
trade data` · `cost of crossing the spread small orders` · `taker fee funding net cost
perpetual retail`.

## 🥇 P2 — WIELKOŚĆ POZYCJI *(podnosi wynik BEZ poprawy trafności)*

Mamy sygnał kierunku i meta-labeling; **nie mamy mostu prawdopodobieństwo → rozmiar**.

| # | Fraza | Trafienie = |
|---|---|---|
| 2.1 | `"bet sizing" "meta-labeling" probability position size` | brakujący most |
| 2.2 | `"fractional Kelly" drawdown constraint cryptocurrency` | Kelly z ograniczeniem obsunięcia (czysty jest zbyt agresywny) |
| 2.3 | `"conformal prediction" "position sizing" OR "risk budgeting" trading` | użycie **naszej** bramki ML-36 do sterowania rozmiarem, nie tylko progiem |
| 2.4 | `"risk of ruin" OR "optimal f" position sizing small account` | ograniczenie od strony ruiny, nie od strony oczekiwanej wartości |

## 🥇 P3 — KIEDY **NIE** WCHODZIĆ *(nasza zagadka: WR 50,6% i strata; ROADMAP F10/F13)*

Trzy z siedmiu wrzutów wskazały tę klasę. Chcemy więcej z tego nurtu.

| # | Fraza | Trafienie = |
|---|---|---|
| 3.1 | `"selective prediction" "risk-coverage" financial forecasting abstention` | krzywa ryzyko–pokrycie: ile pokrycia oddajemy za ile mniej straty |
| 3.2 | `"no-trade" region OR zone reinforcement learning transaction costs` | strefa bezczynności wyprowadzona z kosztów, nie z progu na oko |
| 3.3 | `"over-trading" OR "overtrading" bias algorithmic strategy measurement` | **pomiar** nadmiernego wchodzenia dla systemów regułowych (Atkinson zmierzył dla LLM) |
| 3.4 | `"conservative" offline reinforcement learning finance out-of-distribution` | polityka domyślnie wstrzymująca się przy stanie nieznanym |
| 3.5 | `"opportunity cost" of abstention selective classifier deployment` | druga strona bilansu: co tracimy, wstrzymując się |

## 🥈 P4 — WYCIEK PRZYSZŁOŚCI *(3 z 7 prac: główny tryb awarii; ROADMAP B4 ↑)*

Atkinson zmierzył magnitudę: z wyciekiem **99,4–99,9%** wierności, bez — realistycznie.
Wyciek nie przesuwa wyniku o punkty, **fabrykuje niemal doskonałość**.

| # | Fraza | Trafienie = |
|---|---|---|
| 4.1 | `"look-ahead bias" "multi-timeframe" OR "multiple timeframes" indicator aggregation` | **wprost nasz B4** (`mtf_konfluencja` 1m→1H→4H) |
| 4.2 | `"temporal leakage" audit machine learning pipeline detection` | **mechanizm** wykrywający wyciek, nie checklista |
| 4.3 | `"point-in-time" data reconstruction backtest cryptocurrency` | dyscyplina „tylko to, co było publiczne w chwili decyzji" |
| 4.4 | `"purged" cross-validation embargo combinatorial financial` | mamy purged-CV — szukamy nowszego / ostrzejszego |
| 4.5 | `feature provenance audit cutoff-first truncation before join` | protokół LEAP i jego następcy |

## 🥈 P5 — WAGI SKORELOWANYCH GŁOSÓW *(17 skupisk redundancji; ROADMAP F3/F16)*

`ucz_mwu` **zmierzone jako szkodliwe** (Δ −0,6 pp, PBO ~0,6, flaga OFF). Potrzebny następca.

| # | Fraza | Trafienie = |
|---|---|---|
| 5.1 | `"Shapley value" credit assignment ensemble trading signals regime` | przydział zasługi per reżim |
| 5.2 | `"hierarchical risk parity" OR "HERC" signal clustering correlation alpha combination` | skorelowana rodzina dzieli **jedną pulę wagi** |
| 5.3 | `"alpha combination" decorrelation orthogonalization many weak signals` | jak nie liczyć tego samego osiem razy |
| 5.4 | `"effective number" of bets OR signals concentration Herfindahl portfolio` | podpiera **F16** — `N_eff` dla 87 głosów |
| 5.5 | `multiple testing correction many signals selection bias backtest` | 87 neuronów = 87 testów; korekta na wielokrotność |

## 🥈 P6 — OCENA BEZ WDROŻENIA *(zero realnych zleceń; ROADMAP D5)*

| # | Fraza | Trafienie = |
|---|---|---|
| 6.1 | `"off-policy evaluation" "doubly robust" trading policy returns` | zwrot polityki **bez** wydania zlecenia |
| 6.2 | `"deflated Sharpe ratio" OR "probability of backtest overfitting" multiple testing crypto` | mamy DSR/PBO — szukamy nowszego |
| 6.3 | `synthetic market data generation validation trading strategy` | więcej ścieżek niż daje jedna historia |
| 6.4 | `"walk forward" anchored versus rolling window optimization crypto` | wybór wariantu WFO **z pomiaru**, nie z gustu (nasze E2) |

## 🥉 P7 — RAG, ale WĄSKO *(szerokie już mamy)*

| # | Fraza | Trafienie = |
|---|---|---|
| 7.1 | `"lexical gate" OR "keyword filter" before dense retrieval numeric domain` | kształt naszego **A14** |
| 7.2 | `"table-aware chunking" header propagation units scale document` | propagacja „in millions" — nasze **F8** |
| 7.3 | `"index" OR "back-of-book index" based evaluation set retrieval ground truth` | **nasze A10** — jak ktoś dzielił taki zbiór |
| 7.4 | `"code listing" extraction OCR technical book figure caption retrieval` | 93 listingi z BIB-007 + 11 314 podpisów wykresów |
| 7.5 | `per-chunk confidence score retrieval abstention unaligned` | pole pewności we fragmencie — **F8**, dziś nie mamy go wcale |

## 🥉 P8 — KALIBRACJA PRZYRZĄDÓW *(11 organów bez kalibracji; ROADMAP F7/B1)*

| # | Fraza | Trafienie = |
|---|---|---|
| 8.1 | `"metamorphic testing" machine learning pipeline invariant` | testy niezmiennikowe |
| 8.2 | `"adversarial" perturbation dataset construction evaluate detector faithfulness` | sabotaż programowy jako prawda podstawowa — **nasze F7** |
| 8.3 | `ledger invariant testing backtest engine correctness conservation` | prawo zachowania kapitału jako test |
| 8.4 | `"flip rate" OR sensitivity minimal perturbation classifier evaluation` | czy przyrząd **odwraca** werdykt pod minimalną zmianą |
| 8.5 | `golden values regression testing numerical pipeline tolerance` | zmiana silnika psująca wynik o 0,001 czerwieni test |

---

## ➕ ROZSZERZENIE — kategorie dodane 2026-07-30

## P9 — REŻIM I NIEZAWODNOŚĆ WARUNKOWA *(Prawo XXIII)*

Mamy trafność per reżim; **nie mamy nachylenia degradacji w czasie**.

| # | Fraza | Trafienie = |
|---|---|---|
| 9.1 | `"temporal degradation" model performance slope monitoring deployment` | nachylenie zamiast punktu |
| 9.2 | `regime-conditional strategy performance attribution crypto` | który reżim naprawdę zarabia |
| 9.3 | `"change point detection" online financial time series false alarm rate` | mamy CP-01 i BOCPD-01 — szukamy pomiaru fałszywych alarmów |
| 9.4 | `concept drift detection production model retraining trigger` | **kiedy** przeliczyć wagi, nie „co tydzień" |

## P10 — JAKOŚĆ I ŚWIEŻOŚĆ DANYCH *(D2: dryf 1D 41,5 dnia, 1m 9,3 dnia)*

| # | Fraza | Trafienie = |
|---|---|---|
| 10.1 | `data staleness impact model performance degradation quantification` | ile kosztuje nieświeżość — u nas rój głosuje na starych danych |
| 10.2 | `OHLCV data quality audit gaps outliers crypto exchange comparison` | wykrywanie dziur i wartości odstających (nasz `audyt_danych`, B2) |
| 10.3 | `exchange data discrepancy same asset multiple venues reconciliation` | rozjazd między źródłami — mieliśmy błędy w dniach krachów |

## P11 — PAMIĘĆ SKOJARZENIOWA *(zmierzona luka: brak odruchu skojarzenia)*

Mamy 6 z 7 mechanizmów pamięci; brak **dopełniania wzorca** i **warstwy pewności**.

| # | Fraza | Trafienie = |
|---|---|---|
| 11.1 | `pattern completion associative retrieval agent memory partial cue` | odruch „to już widziałem" bez pełnego zapytania |
| 11.2 | `confidence-weighted memory agent knowledge staleness decay` | pewność i starzenie się faktu |
| 11.3 | `contradiction detection knowledge base agent self-consistency` | nasza Refleksja W9 ma 3 sprzeczności — jak je rozstrzygać automatem |

## P12 — MAŁY MODEL LOKALNY *(TIRO; ROADMAP F1/F15)*

| # | Fraza | Trafienie = |
|---|---|---|
| 12.1 | `small language model structured extraction JSON schema CPU quantized` | TIRO ma ekstrahować, nie gawędzić |
| 12.2 | `abstention refusal small model context insufficient citation grounded` | rodzina OCC-RAG — **F1** |
| 12.3 | `LoRA versus RAG domain adaptation small model measured comparison` | jedyne otwarte pytanie TIRO E4 |
| 12.4 | `quantization accuracy tradeoff Q4 Q5 Q8 measured task degradation` | ile tracimy na Q4 — dziś nie wiemy |

## P13 — SYGNAŁY ALT-DATA *(4 zwalidowane Tier-1; szukamy piątego)*

| # | Fraza | Trafienie = |
|---|---|---|
| 13.1 | `funding rate basis predictive power crypto perpetual returns` | mamy funding — szukamy mocniejszego użycia |
| 13.2 | `liquidation cascade leading indicator open interest crypto` | kaskady jako sygnał wyprzedzający |
| 13.3 | `stablecoin flows OR netflow predictive crypto returns` | mamy stablecoin — walidacja niezależna |
| 13.4 | `information coefficient decay horizon alternative data finance` | jak szybko wygasa przewaga sygnału |

## P14 — MANIPULACJA I OBRONA *(kategoria A: 4 neurony)*

| # | Fraza | Trafienie = |
|---|---|---|
| 14.1 | `stop hunt OR liquidity sweep detection order flow crypto measurement` | mamy A-01 Stop Hunt — szukamy pomiaru trafności |
| 14.2 | `wash trading detection exchange volume authenticity crypto` | ile z wolumenu MEXC jest realne |
| 14.3 | `spoofing layering detection without L2 data proxies` | detekcja bez księgi — nasze ograniczenie danych |

---

## 🚫 CZEGO **NIE** SZUKAĆ — mamy to, zmierzone *(Prawo XVI)*

`RAG survey` · `hybrid BM25 + wektory` (mamy, i A14 to precyzuje) · frameworki multi-agentowe
(TradingAgents, moon-dev, Fractal Debate) · `LangChain` / `LlamaIndex` / `ChromaDB` / `Ollama`
(**Ollama odrzucona pomiarem 2026-07-16**) · `conformal prediction` jako nowość
(**mamy ML-36 wpiętą od 2026-07-05**) · `triple-barrier`, `meta-labeling`, `DSR`, `PBO`,
`purged CV` jako podstawy (mamy na poziomie AFML) · `GARCH` / `VaR` / `ES` · „jak zbudować
bota tradingowego" · `hudson-and-thames/mlfinlab` (**atrapa — ciała metod to `pass`**).

## ✅ JAK OCENIĆ TRAFIENIE W 30 SEKUND

**Odrzuć od razu, jeśli:** zero tabel · same zrzuty ekranu · „survey" w tytule · brak sekcji
ograniczeń · wynik podany bez baseline'u · liczby bez podanego `n`.

> ⚠️ **POPRAWKA KRYTERIUM (2026-08-02) — najpierw rozpoznaj TYP pracy.** Reguła „zero tabel
> = odrzuć" jest skalibrowana na prace **empiryczne (ML/dane)**. Labadie–Lehalle `1205.3482`
> ma **0 tabel i 0 sekcji Limitations** — bo to **matematyka stosowana**, gdzie dowód
> i jawne założenia zastępują tabelę. Zastosowana mechanicznie, reguła odrzuciłaby pracę,
> która dała najważniejszy wniosek tego zwiadu. Dla prac teoretycznych pytaj o **założenia
> modelu i ich osiągalność u nas** (czy potrzebuje L2? czy zakłada impakt własnego zlecenia?),
> nie o liczbę tabel.

**Bierz, jeśli:** jest **tabela ablacji** (kilka wariantów obok siebie) · jest **Limitations /
Threats to validity** · autor pisze **„simulated"** albo **„we defer to follow-up work"** (to
znak, że wie, czego nie wie — **plus, nie minus**) · jest **własny wynik negatywny**.

> **Zmierzone na siedmiu pracach:** oba złote trafienia miały tabelę ablacji **oraz** własny
> wynik negatywny. Jedyny pełny odpad miał **zero tabel i 13 zrzutów ekranu**.

---

*Dokument żywy — po każdym zwiadzie dopisujemy, która fraza dała trafienie (✅), a która zły
poddział domeny (❌). Fraza bez znaku jest **niezmierzona** i nie wolno o niej mówić, że działa.*
