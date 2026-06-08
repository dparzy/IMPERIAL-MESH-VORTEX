# 📜 LOG ZMIAN IMPERIUM — Żywa Pamięć Projektu

> **Zasada (ROZKAZ STAŁY):** Po KAŻDEJ zmianie systemu, kodu, dokumentacji — wpis do tego logu.
> Format: Data | Typ | Opis | Powód | Pliki. Najnowsze wpisy na górze.
> Ten plik jest źródłem prawdy historii Imperium. Bez niego decyzje giną.

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
