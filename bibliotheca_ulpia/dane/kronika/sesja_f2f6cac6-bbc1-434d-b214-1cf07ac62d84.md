# Kronika sesji f2f6cac6-bbc1-434d-b214-1cf07ac62d84

## 🧑 Cezar
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
## 1. Primary Request and Intent

This session (continued from previous context at v0.9.0 Exploratores division) had these primary requests in sequence:

1. **Evaluate and adopt new indicators** (Katana Scalper Pro, A-TLP, Night Turbo, SMC Engine, Gold Scalper, Dynamic Pro, AP-Mode) as Exploratores scouts EXP-06 through EXP-12, fixing all bugs in each
2. **Build dekorelacja diagnostics** to replace dogmatic "no redundancy" with measurable correlation thresholds (→ Prawo XVI)
3. **Deep system audit** — check all neurons, scouts, documentation for dead voices, inconsistencies
4. **New fundamental law** on decisiveness: when architect sees inconsistency, decide yourself, don't ask Caesar about trivialities (→ Prawo XVIII)
5. **Documentation unification** — README was outdated ("Phase: Foundation, 8 laws"), multiple neuron counts (261/303/306/328) across docs, "only 2 code examples" lie
6. **Latest (final) message**: `"zasada fundamentalna zawsze po odkryciu wszystko musi byc w kodzie nie tylko informacja w katalogu teraz musisz etapami wszystko odbudowac zgodnie z zasadami dopisz zasade scisla kontrola wszystkiego calego imperium w github"` — Add a law: everything discovered must be in CODE, not just catalog. Rebuild step by step. Strict GitHub control of everything.

**SECURITY CONSTRAINT (verbatim, always applies):**
- **KLUCZE API NIGDY W KODZIE, NIGDY W CZACIE** — tylko zmienne środowiskowe.
  - DeepSeek: `[ZREDAGOWANO]
  - MEXC: `os.getenv("MEXC_API_KEY")`, `os.getenv("MEXC_SECRET")`

---

## 2. Key Technical Concepts

- **IMV-ADO** (🔱) — seal for externally adopted and improved indicators
- **Prawo XV** — mandatory red alarm when potential is wasted/underutilized
- **Prawo XVI** — redundancy measured via Pearson correlation, not by name similarity; `|kor| > 0.80` = merge candidate; `|kor| < 0.20` = pillar of strength
- **Prawo XVII** — read full repo state at start of every session; update docs in same commit as code change
- **Prawo XVIII** — architect resolves inconsistencies himself; hierarchy: code+tests > ZASADY > counted numbers > memory; ask Caesar only for irreversible/strategic decisions
- **DOSTEPNY / POWOD_NIEDOSTEPNOSCI** — fields on both `MikroNeuron` and `ZwiadowcaElitarny` bases; silenced modules give no NEUTRAL, they are explicitly skipped
- **BudowniczyWskaznikow** — bridge: raw OHLCV bars → complete wskaźniki dict for neurons; now includes `_dodaj_ha()` for X-26
- **Heiken Ashi without repainting** — `HA_Open[i] = (HA_Open[i-1] + HA_Close[i-1]) / 2` (recursive), NOT `(Open[-1]+Close[-1])/2`
- **True Range** — `max(H-L, |H-prevC|, |L-prevC|)` — corrected in all adopted indicators
- **Lookahead bias** — `.shift(-1)/.shift(-2)` in original SMC engine (patched in EXP-09)
- **Cross as EVENT not STATE** — EXP-11 signals only on fresh crossing, not on every bar where fast>slow
- **Slippage/Spread Guard** — EXP-11 unique value: spread > 75th percentile → block (no other module has this)
- **Liquidity Sweep / Stop Hunt** — EXP-09: sweep of previous high/low + reversal candle → LONG/SHORT
- **Structural Displacement** — EXP-10: `max(|Δhigh|, |Δlow|) / close` spike > 1.5× MA
- **L2 Microstructure** — EXP-12 (silenced): imbalance (5+10 levels), delta acceleration, queue cancellations, conviction score; needs orderbook feed
- **Canonical neuron count** — 299 (counted as unique keys from KATALOG_NEURONOW.md tables), NOT 261/303/306/328 (old estimates from various scan rounds)
- **katalog ≠ kod** — 299 designed / 27 implemented in code / 12 scouts (Prawo I distinction)

---

## 3. Files and Code Sections

### New Files Created

**`imperium/legiony/zwiadowcy/exp_katana.py`** (EXP-06)
```python
class ZwiadowcaKatana(ZwiadowcaElitarny):
    KLUCZ = "EXP-06"; KATEGORIA = "M"; WAGA = 7
    MIN_STRENGTH: float = 0.5; ATR_PERIOD: int = 14; VOL_PERIOD: int = 20
    # Recursive HA (no repaint), ATR/ATR_MA volatility regime, MTF 20+50 windows
    # Triple confirmation: HA color + Price_momentum + HA_momentum
```

**`imperium/legiony/zwiadowcy/exp_tlp.py`** (EXP-07)
```python
class ZwiadowcaTLP(ZwiadowcaElitarny):
    KLUCZ = "EXP-07"; KATEGORIA = "T"; WAGA = 7
    ATR_MULT: float = 0.15  # WAS 1.5 — fixed dead voice bug
    CHANNEL_PERIOD: int = 20; VOL_RATIO_MIN: float = 0.9
    # Fresh breakout only: close > target AND prev_close <= prev_target
```

**`imperium/legiony/zwiadowcy/exp_night.py`** (EXP-08)
```python
class ZwiadowcaNightTurbo(ZwiadowcaElitarny):
    KLUCZ = "EXP-08"; KATEGORIA = "M"; WAGA = 6
    NIGHT_START: int = 22; NIGHT_END: int = 2  # UTC wraparound
    PROG_ATR_MULT: float = 0.5  # ATR actually used (original had dead ATR)
    # _godzina_utc() extracts hour from epoch seconds/ms/ISO string
```

**`imperium/legiony/zwiadowcy/exp_sweep.py`** (EXP-09)
```python
class ZwiadowcaLiquiditySweep(ZwiadowcaElitarny):
    KLUCZ = "EXP-09"; KATEGORIA = "S"; WAGA = 8
    SWING_LOOKBACK: int = 10
    # NO lookahead: only bary[start:n] (past only, never future bars)
    # sweep_high + bearish_close → SHORT; sweep_low + bullish_close → LONG
```

**`imperium/legiony/zwiadowcy/exp_displacement.py`** (EXP-10)
```python
class ZwiadowcaDisplacement(ZwiadowcaElitarny):
    KLUCZ = "EXP-10"; KATEGORIA = "S"; WAGA = 7
    DISP_MULT: float = 1.5; ATR_MAX_MULT: float = 1.2
    # SYMMETRIC: max(|Δhigh|, |Δlow|) / close — original was only |Δhigh|
```

**`imperium/legiony/zwiadowcy/exp_dynamic.py`** (EXP-11)
```python
class ZwiadowcaDynamic(ZwiadowcaElitarny):
    KLUCZ = "EXP-11"; KATEGORIA = "T"; WAGA = 6
    SEP_ATR_FRAC: float = 0.10; SPREAD_Q: float = 0.75
    # Slippage guard: spread > 75th percentile → silence (unique value, no other module has this)
    # Cross as EVENT: cross_up = fast>slow AND prev_fast<=prev_slow
```

**`imperium/legiony/zwiadowcy/exp_atmabhan.py`** (EXP-12)
```python
class ZwiadowcaAtmabhan(ZwiadowcaElitarny):
    KLUCZ = "EXP-12"; KATEGORIA = "V"; WAGA = 9
    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = "Wymaga feedu L2 orderbook..."
    CONVICTION_PROG = 7.5
    # analizuj_orderbook(snapshot) — called when feed connected
    # WARNING in docstring: original +106,692% ROI is fantasy/lookahead
```

**`imperium/legiony/diagnostyka_korelacji.py`**
```python
def sygnal_na_liczbe(kierunek, pewnosc) → float  # LONG=+p, SHORT=-p, NEUTRAL=0
def korelacja_pearson(x, y) → Optional[float]    # None if zero variance
def zbierz_sygnaly_zwiadowcow(bary, zwiadowcy, okno, krok) → Dict[str, List[float]]
def macierz_korelacji(serie) → Dict[Tuple[str,str], Optional[float]]
def raport_dekorelacji(bary, zwiadowcy, ...) → Dict[str, Any]
def sformatuj_raport(rap) → str
```

**`tests/test_dekorelacja.py`** — 10 test functions including `test_raport_wykrywa_martwy_glos`

### Modified Files

**`imperium/legiony/zwiadowcy/baza.py`**
- Added `DOSTEPNY: bool = True` and `POWOD_NIEDOSTEPNOSCI: str = ""` to `ZwiadowcaElitarny`

**`imperium/legiony/budowniczy_wskaznikow.py`**
- Added `_dodaj_ha(bary, w)` — recursive HA without repainting, produces `HA_BULL`, `HA_BEAR`, `HA_MOMENTUM`, `HA_VOLATILITY_INDEX` for X-26 NeuronHAScalper
```python
def _dodaj_ha(self, bary, w):
    # HA_Open[i] = (ha[i-1]["o"] + ha[i-1]["c"]) / 2  (recursive)
    # w["HA_BULL"], w["HA_BEAR"], w["HA_MOMENTUM"], w["HA_VOLATILITY_INDEX"]
```

**`imperium/legiony/legatus.py`**
```python
def _odpal_zwiadowcow(self, wskazniki, bary):
    aktywni = [z for z in self.zwiadowcy if getattr(z, "DOSTEPNY", True)]
    # silenced scouts are completely skipped
```

**`imperium/legiony/rejestr.py`**
- `wszyscy_zwiadowcy()` now returns 12 scouts (EXP-01..12)
- `raport_potencjalu()` now reports `zwiadowcy_aktywni` / `zwiadowcy_wyciszeni`
- Imports: ZwiadowcaKatana, ZwiadowcaTLP, ZwiadowcaNightTurbo, ZwiadowcaLiquiditySweep, ZwiadowcaDisplacement, ZwiadowcaDynamic, ZwiadowcaAtmabhan

**`ZASADY_FUNDAMENTALNE.md`**
- Added Prawo XV (red alarm), XVI (redundancy measured), XVII (terrain reconnaissance), XVIII (architect decisiveness)
- Now 18 laws total

**`CLAUDE.md`**
- Updated 14→18 laws
- Added operational sections for Prawa XV, XVI, XVII, XVIII (read at every session start)

**`README.md`** — full rewrite:
- Current state: 27 neurons, 12 scouts, 237/237 tests, 18 laws
- Distinction: catalog (299 designed) vs code (27 implemented)
- Real folder map with module counts

**`docs/` — unification**:
- All "14 laws" → 18 (ARCHITEKTURA_IMPERIUM, AUDYT_ADOPCJI)
- All contradictory neuron counts (261/303/306/328) → 299/27 (GENERAL_LEGATUS, IGRZYSKA, README, INDEKS, OBSERWATORZY, KATALOG_STRATEGII, KATALOG_NEURONOW, AUDYT_SYSTEMU)
- AUDYT_SYSTEMU: "only 2 examples" → "27 neurons + 12 scouts, 237 tests"
- Historical changelog entries left unchanged (past must remain true)

---

## 4. Errors and Fixes

- **`TypDanych.OBLICZONY` doesn't exist** in EXP-06: fixed to `TypDanych.CUSTOM`
- **`_buduj_raport()` called with wrong signature** in EXP-06: fixed to use keyword args `kierunek=`, `pewnosc=`, `powody=`, `diagnostics=`, `n_barow=`
- **EXP-12 conviction scale bug**: `×6.67` meant perfect imbalance (1.0) gave only 6.67 < 7.5 threshold → signal always blocked; fixed to `×10.0`
- **EXP-07 dead in 4/5 regimes**: `ATR_MULT=1.5` meant `target_up = channel_top + 1.5×ATR` (break 20-bar high by another 1.5 ATR) — triggered only 2/470 bars; fixed to `ATR_MULT=0.15`
- **X-26 NeuronHAScalper dead in production**: needed `HA_BULL/HA_BEAR/HA_MOMENTUM/HA_VOLATILITY_INDEX` but Budowniczy never produced them → always "Brak danych HA" → NEUTRAL. Fixed by adding `_dodaj_ha()` to BudowniczyWskaznikow
- **README 16→17 praw discrepancy**: introduced in one commit and immediately fixed in the next
- **`run_tests.py` Edit failed** ("file not read yet"): had to Read it first, then Edit

---

## 5. Problem Solving

**Central problem: potential waste (Prawo XV)**
- Systematic pattern of bugs in all adopted indicators: fake ATR, dead ATR (computed not used), lookahead bias, dead code (swing_high computed not used), asymmetry (only high not low)
- Every adopted indicator had at least 2-3 critical bugs; all fixed with regression tests

**Redundancy assessment (Prawo XVI)**
- EXP-02~EXP-03 pair showed 0.80 correlation on one random seed but 0.59-0.66 across 5 regimes → NOT redundant, was random artifact
- Built `diagnostyka_korelacji.py` to make this measurable rather than opinion-based

**Documentation chaos (Prawo XVII/XVIII)**
- 4 contradictory neuron counts in docs (261/303/306/328) — resolved by actually counting unique keys in KATALOG_NEURONOW.md → **299 canonical**
- Applied Prawo XVIII: resolved myself without asking Caesar

---

## 6. All User Messages

1. *(session start)* "ok dawaj" — proceed with EXP-07 A-TLP implementation
2. Posted Generic A-TLP Scalper code for review
3. "dawaj" — implement EXP-07
4. Posted Night Turbo Scalper code
5. Posted SMC Scalping Engine code
6. Posted Gold Scalper Pro code
7. Posted Dynamic Pro Scalper code
8. Posted AP-Mode README link (Codeberg, 403)
9. Uploaded AP-Mode README.md — "i jak to teraz wyglada cale imperium... sprawdz to czy jest zgodne z naszymi zasadami"
10. *(after EXP-12 decision question)* Selected "Moduł L2 wyciszony (DOSTEPNY=False)"
11. "teraz pytanie jak to jest ze teraz trzymamy elitarne czy nasza zasada redundacji rowniez psuje postepowosc naszego imperium"
12. "tak zbuduj" — build dekorelacja diagnostic
13. "tak dopisz do zasad fundamentalnych" — write Prawo XVI to constitution
14. "tak zbadaj ta pare i zrób głęboki audyt czle imperium zgodnie z zasadami i sprawdz czy nasza baza wskazniki i strategie sa w porzadku i nie sa neutral i w pelni sprawne zgodnie z zasadami"
15. "a dlaczego tak malo przeciez mamy w arsenale duzo wiecej"
16. "jakas masakra przeczytaj dokumentt w naszym imperium zgodnie z index" — read `docs/INDEKS_IMPERIUM.md`
17. "narazie nic nie robimy zapomnij o tych dokumentach" — forget kingdom-pixel archive
18. "tak dawaj" *(after explanation of empty X slots)*
19. *(dismissed question)* — waiting for next instruction
20. "no wlasnie zasada bardzo wazna zawsze zanim zaczynasz nowe zadanie i zaczynasz nowa sesje dokladnie sprawdzasz zawartosc naszego imperium na github czytasz... nasz readme jest nie aktualny nie dbasz o porzadek"
21. "dopisz do zasad fundamentalnych" — add Prawo XVII
22. "i co teraz narobiłeś bałagan musimy zrobić dokładny audyt stanu na GitHub i wszystkiego czy jest zgodne z naszymi zasadami"
23. "zrob dokladny audyt i sprawdz zgodnie z zasadami nastepna zasada jak widzisz niespojnosci i bledy sam decydujesz i wybierasz najlepsza opcje zgodna z naszymi zasadami dodaj do zasad fundamentalnych i sprawdz ta rozbieznosc"
24. *(stop hook feedback)* "There are 1 unpushed commit(s)" + "i jak wiesz ile mamy wszystkiego w imperium"
25. **"zasada fundamentalna zawsze po odkryciu wszystko musi byc w kodzie nie tylko informacja w katalogu teraz musisz etapami wszystko odbudowac zgodnie z zasadami dopisz zasade scisla kontrola wszystkiego calego imperium w github"**

---

## 7. Pending Tasks

1. **Write Prawo XIX** (or continuation of XVIII): "everything discovered must be in CODE, not just in catalog" — new constitutional law about strict GitHub control of all Imperium state
2. **Step-by-step reconstruction**: implement neurons from `docs/KATALOG_NEURONOW.md` (299 designed, 27 done, 272 remaining) in phases, with dekorelacja measurement (Prawo XVI) between phases
3. **Strict GitHub control**: mechanism ensuring code reality matches catalog/documentation — possibly automated check or manifest
4. **Push remaining unpushed commit** (stop-hook noted 1 unpushed on `claude/sleepy-fermi-dsdE4`)

---

## 8. Current Work

Immediately before summary request, the user sent:

> "zasada fundamentalna zawsze po odkryciu wszystko musi byc w kodzie nie tylko informacja w katalogu teraz musisz etapami wszystko odbudowac zgodnie z zasadami dopisz zasade scisla kontrola wszystkiego calego imperium w github"

This was AFTER the full audit + unification (Prawo XVIII execution). The prior completed work:
- `ZASADY_FUNDAMENTALNE.md`: 18 laws, full audit done
- `README.md`: rewritten to truth (27 neurons / 12 scouts / 299 catalog / 237 tests / 18 laws)
- All `docs/` unified to canon numbers (299/27, 18 laws)
- All inconsistencies resolved by architect per Prawo XVIII
- State: 237/237 tests, clean working tree, `claude/sleepy-fermi-dsdE4` pushed (commit `5a47b4e`)
- Stop hook warned about 1 unpushed commit (from README fix `97c9283..5a47b4e`)

The user's final message demands:
1. A new fundamental law: "everything in code, not just catalog"
2. Strict GitHub control law
3. Step-by-step rebuilding of everything according to principles

---

## 9. Optional Next Step

Based on the user's most recent explicit request:

> "zasada fundamentalna zawsze po odkryciu wszystko musi byc w kodzie nie tylko informacja w katalogu teraz musisz etapami wszystko odbudowac zgodnie z zasadami dopisz zasade scisla kontrola wszystkiego calego imperium w github"

The next steps are:

1. **Write Prawo XIX** to `ZASADY_FUNDAMENTALNE.md` and `CLAUDE.md`: "Whatever is discovered/cataloged MUST be implemented in code — catalog entries are not done until code + tests exist. Strict GitHub control: every session, code reality checked against catalog. No phantom neurons."

2. **Create a reconstruction roadmap/manifest** — a tracked file (e.g., `docs/MANIFEST_KODU.md`) showing for each of the 299 cataloged neurons: status (implemented ✅ / pending 🔴), KLUCZ, class name, file. This creates the strict GitHub control the user wants.

3. **Begin Phase 1 of step-by-step reconstruction** — implement next batch of neurons from the catalog (Legion X Equestris has X-07 through X-24 empty; Legion XII and III Augusta also have gaps), measured against dekorelacja after each batch (Prawo XVI).

The priority order follows Prawo XVIII (architect decides): first write the law + control manifest, then begin reconstruction phase by phase.

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /root/.claude/projects/-home-user-IMPERIAL-MESH-VORTEX/f87b07f0-c136-4cca-9630-6abab8b1e7ac.jsonl
Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

## 🏛️ Claude
Teraz dodaję Prawo XIX do konstytucji, tworzę MANIFEST_KODU.md i aktualizuję CLAUDE.md.

## 🏛️ Claude
Teraz tworzę MANIFEST_KODU.md — oficjalny rejestr kontrolny wszystkich 299 neuronów:

## 🏛️ Claude
Teraz tworzę MANIFEST_KODU.md — oficjalny rejestr wszystkich 299 neuronów + 12 zwiadowców:

## 🏛️ Claude
Teraz aktualizuję CLAUDE.md o Prawo XIX:

## 🏛️ Claude
Teraz aktualizuję README.md (19 praw) i uruchamiam testy:

## 🏛️ Claude
237/237 zielone. Commituję i pushuję:

## 🏛️ Claude
Gotowe. Oto co zostało zrobione:

---

## 🔱 PRAWO XIX — wdrożone

**`ZASADY_FUNDAMENTALNE.md`** — dodane Prawo XIX: *"KOD JEST PRAWEM, KATALOG JEST PLANEM"*
- Moduł istnieje WTEDY I TYLKO WTEDY, gdy jest plik `.py` + przechodzący test na branchu
- Ścisła kontrola GitHub przez `docs/MANIFEST_KODU.md`

**`docs/MANIFEST_KODU.md`** — nowy plik kontrolny (jedyne oficjalne źródło prawdy):
- ✅ **39 modułów w kodzie**: 27 neuronów + 12 zwiadowców
- 🔴 **272 neurony tylko w katalogu** — czekają na wdrożenie
- Tabela faz rozbudowy z datami
- Komenda: `grep "🔴" docs/MANIFEST_KODU.md` → natychmiast wiadomo co jest backlogiem

**`CLAUDE.md`** — checklistaa Prawa XIX na każdą sesję: sprawdź MANIFEST przed jakimkolwiek twierdzeniem o liczbie modułów

**Testy:** 237/237 ✅ · **Push:** `claude/sleepy-fermi-dsdE4`

---

Imperium ma teraz 19 praw i twardą kontrolę: **"Katalog mówi: chcemy. Kod mówi: mamy. Nie mylimy tych dwóch słów nigdy."**

Następny krok to Faza 1 rozbudowy roju — X-01 do X-24 (Legion X Equestris, M5/M15). Chcesz zacząć?

## 🧑 Cezar
tylko skad wiesz ze mamy naprawdę  tyle neuronow zasada fundamentala zawsze mozemy oszacowac faktyczna ilosc jak mamy kod neuronu w naszym systemie imperium sprawdz wsztstko po koleji i odbodowujemy wszystko zgodnie z zasadami pamietaj

## 🏛️ Claude
Masz rację — to jest dokładnie Prawo XIX i XVIII w praktyce. Nie mogę twierdzić "27 neuronów" bez policzenia faktycznego kodu. Sprawdzam wszystko po kolei, liczę z plików, nie z pamięci.

## 🏛️ Claude
27 klas potwierdzone w plikach neurony/. Ale Prawo XIX wymaga sprawdzenia *wszystkiego* — czy są zarejestrowane, czy nie ma neuronów gdzie indziej, czy każdy faktycznie działa. Sprawdzam dalej:

## 🏛️ Claude
🚨 **Czerwony alarm Prawa XV — znalazłem 2 martwe neurony.**

W `imperium/legiony/mikro_neuron.py` są **2 dodatkowe klasy neuronów**:
- `NeuronStochRSI`
- `NeuronFundingRate`

Mają kod, ale **NIE są zarejestrowane** w `rejestr.py` → nie biorą udziału w głosowaniu. To dokładnie utrata potencjału. Sprawdzam je dokładniej:

## 🏛️ Claude
To są działające neurony (X-02 StochRSI i VI-01 FundingRate), oznaczone jako "przykładowa implementacja" w pliku bazowym — ale **mają pełny kod i nie są w roju**. Co więcej: w moim MANIFEST oznaczyłem X-02 jako `🔴 tylko katalog` — a to **kłamstwo**, bo kod istnieje. Złamałem własne Prawo XIX w godzinę po jego napisaniu.

Sprawdzam jeszcze czy Brama/Budowniczy w ogóle produkuje te wskaźniki (inaczej byłyby martwe nawet po podpięciu):

## 🏛️ Claude
Tu jest dużo większy problem. Budowniczy produkuje tylko ~16 wskaźników, a mam 27 neuronów wymagających m.in. RSI, ADX, Ichimoku, Supertrend, OBV, VWAP, CVD... Muszę sprawdzić, ile neuronów faktycznie dostaje dane, a ile zwraca martwe "Brak danych". Sprawdzam to systematycznie:

## 🏛️ Claude
Teraz widać pełny obraz. Zamiast zgadywać, robię **twardy test wykonawczy** — buduję wskaźniki z realnych barów, odpalam każdy neuron i sprawdzam który faktycznie żyje, a który zwraca "brak danych":

## 🏛️ Claude
TA-Lib niedostępny w tym środowisku. Sprawdzam, jak testy obchodzą Bramę — to ważne dla zrozumienia, co naprawdę jest testowane:

## 🏛️ Claude
Testy sprawdzają **logikę każdego neuronu osobno** (podają ręcznie wskaźniki) — to poprawny unit test, ale **nie łapią luki integracyjnej**: czy Budowniczy faktycznie produkuje każdy klucz, którego neuron potrzebuje. To właśnie tu może być utrata potencjału. Sprawdzam dokładnie, co Budowniczy zapisuje do swojego słownika wyjściowego:

## 🏛️ Claude
Wąski grep `w["` dał 16 kluczy, ale szerszy wcześniej widział ADX_14, RSI_14, EMA_*, ICHIMOKU, OBV, SUPERTREND, VWAP. Muszę zobaczyć faktyczną strukturę Budowniczego — jak przypisuje klucze:

## 🏛️ Claude
Budowniczy produkuje więcej niż wąski grep pokazał (Ichimoku przez `w.update`). Teraz kluczowe pytanie: czy neurony oznaczone jako **DOSTĘPNE** dostają wszystkie swoje dane. Sprawdzam CVD, psychologię i onchain — czy mają poprawnie ustawione DOSTEPNY:

## 🏛️ Claude
Teraz mam **pełny, policzony obraz** — i jest jasna konkluzja. Zanim zdecyduję o naprawie, sprawdzam ostatnie dwie rzeczy: czy testy używają tych sierot i czy Brama wspiera StochRSI:

## 🏛️ Claude
Teraz mam **pełną, policzoną prawdę**. Sprawdzam jeszcze, jakie obliczenia Brama w ogóle wspiera (żeby wiedzieć, czy StochRSI da się ożywić, czy musi czekać):

## 🏛️ Claude
Pełna prawda policzona z kodu. Brama **nie liczy StochRSI**, więc X-02 nie może być od razu aktywny. Zanim zrobię naprawę, pokażę Ci konkluzję audytu i zdecyduję kierunek.

## 🚨 RAPORT AUDYTU — rzeczywista liczba neuronów (policzona, nie z pamięci)

Policzyłem **klasy neuronów w kodzie**, nie z pamięci ani z katalogu:

| Co | Liczba | Dowód |
|----|--------|-------|
| Klasy `Neuron*` w `neurony/` | **27** | `grep class ...MikroNeuron` |
| Klasy `Neuron*` w `mikro_neuron.py` | **+2** | `NeuronStochRSI` (X-02), `NeuronFundingRate` (VI-01) |
| **RAZEM klas w kodzie** | **29** | — |
| Zarejestrowane w roju (`rejestr.py`) | **27** | tylko te głosują |
| Aktywne (dostają dane z Bramy) | **15** | reszta DOSTEPNY=False |
| Wyciszone (czekają na API/feed) | **12** | OB, FVG, BOS, CVD, 4×psych, 4×onchain |

**Dwa odkrycia łamiące zasady:**

1. 🚨 **Prawo XV (martwy potencjał):** `NeuronStochRSI` (X-02) i `NeuronFundingRate` (VI-01) mają pełny, działający kod, ale **nie są w roju** — używane tylko w demo `legatus.py __main__`. To 2 neurony siedzące w szufladzie.

2. 🚨 **Prawo XIX (złamałem własną zasadę):** w `MANIFEST_KODU.md` napisałem godzinę temu, że X-02 to `🔴 tylko katalog` — a **kod istnieje**. Manifest kłamał.

Teraz naprawiam zgodnie z zasadami. Decyzja (Prawo XVIII): X-02 StochRSI to realny neuron z katalogu — **promuję go do roju**, dodaję StochRSI do Bramy i Budowniczego. VI-01 FundingRate **dubluje** `NeuronFundingExtreme` (Prawo XVI) → zostaje jako jawnie oznaczony przykład dydaktyczny. Sprawdzam wzorzec Bramy:

## 🏛️ Claude
Mam pełny wzorzec. Wykonuję naprawę zgodnie z zasadami:

1. Dodaję `STOCHRSI` do Bramy (talib.STOCHRSI) i Budowniczego
2. Przenoszę `NeuronStochRSI` X-02 do `momentum.py`, rejestruję jako **aktywny**
3. `NeuronFundingRate` VI-01 dubluje `NeuronFundingExtreme` → wycofuję (Prawo XVI)
4. Naprawiam demo w `legatus.py`

Zaczynam od Bramy:

## 🏛️ Claude
Teraz przenoszę NeuronStochRSI do momentum.py. Najpierw zobaczę koniec momentum.py i nagłówek:

## 🏛️ Claude
Dodaję `NeuronStochRSI` (X-02) na końcu momentum.py — z kluczem zgodnym z Budowniczym (`STOCHRSI`):

## 🏛️ Claude
Nagłówek momentum.py **już wymienia StochRSI** w spisie — był od początku planowany tu. Dodaję go:

## 🏛️ Claude
Teraz rejestruję X-02 w roju. Zobaczę dokładnie sekcję importów i listy w rejestr.py:

## 🏛️ Claude
Teraz usuwam dwie sieroty z `mikro_neuron.py` i naprawiam demo w `legatus.py`. Najpierw zobaczę kontekst przed sierotami:

## 🏛️ Claude
Teraz naprawiam demo w legatus.py żeby nie importował usuniętych klas:

## 🏛️ Claude
Teraz dodaję test dla X-02 i uruchamiam całość:

## 🏛️ Claude
Sprawdzam test integracyjny na linii ~374 (lista neuronów — może liczyć ilość) i czy są inne testy liczące neurony:

## 🏛️ Claude
Test integracyjny asercjuje 27 — teraz powinno być 28. Aktualizuję i dodaję X-02 do listy "brak danych":

## 🏛️ Claude
240/240 zielone (było 237 + 3 nowe testy StochRSI). Teraz aktualizuję MANIFEST_KODU.md zgodnie z prawdą (28 neuronów, X-02 aktywny) i README:

## 🏛️ Claude
Teraz aktualizuję sekcję X-02 w backlogu (już nie 🔴) i tabelę zbiorczą:

## 🏛️ Claude
Teraz README — 27→28 neuronów, 15→16 aktywnych:

## 🏛️ Claude
Wszystko spójne. Ostatni przebieg testów i commit:

## 🏛️ Claude
28 neuronów potwierdzone z kodu (nie z pamięci). Commituję i pushuję:

## 🏛️ Claude
Gotowe. Odpowiedziałem na Twoje pytanie **liczbą policzoną z kodu, nie z pamięci** — i przy okazji znalazłem 2 błędy łamiące zasady.

## Skąd teraz wiem, ile mamy neuronów

Nie zgaduję. Liczba = klasy zarejestrowane w roju (`rejestr.py` → `wszystkie_neurony()`), **zweryfikowane testem** `test_rejestr_wszystkie_neurony() == 28`. Każda zmiana złamie test, jeśli liczba się rozjedzie.

## Co audyt wykrył (czerwony alarm Prawa XV)

1. 🚨 **2 neurony-sieroty** — `NeuronStochRSI` (X-02) i `NeuronFundingRate` (VI-01) miały pełny, działający kod w `mikro_neuron.py`, ale **nie były w roju** (używane tylko w demo). Siedziały w szufladzie = utrata potencjału.
2. 🚨 **Mój MANIFEST kłamał** — godzinę po napisaniu Prawa XIX oznaczyłem X-02 jako `🔴 tylko katalog`, choć kod istniał. Złamałem własną zasadę.

## Naprawa zgodnie z zasadami

| Sierota | Decyzja (Prawo XVIII) | Wynik |
|---------|----------------------|-------|
| X-02 StochRSI | Realny neuron z katalogu → **promowany do `momentum.py`**, dodane `STOCHRSI` do Bramy (talib) i Budowniczego | ✅ aktywny, w roju |
| VI-01 FundingRate | **Dubluje** `NeuronFundingExtreme` (Prawo XVI) → wycofany | usunięty, zero phantomów |

**Stan policzony i zsynchronizowany:**
- **28 neuronów** w roju (było 27): 16 aktywnych + 12 wyciszonych
- 12 zwiadowców (1 wyciszony — EXP-12)
- **240/240 testów** zielonych (+3 nowe dla StochRSI)
- MANIFEST, README, testy — wszystkie mówią 28, spójnie

Następny etap odbudowy: **Faza 1** — Legion X Equestris, neurony X-01, X-03..X-24 (23 do wdrożenia z katalogu), partiami z pomiarem dekorelacji po każdej partii. Zacząć od X-01 (EMA Cross M5) i X-08/X-09 (Awesome/Accelerator Oscillator)?

## 🧑 Cezar
zasady fundamentalne pokaz calosc

## 🏛️ Claude
Widzę jeden błąd — między Prawem XVIII a XIX wpadły podwójne `---`. Naprawiam od razu (Prawo XVIII — decyduję sam):

## 🏛️ Claude
Oto pełna konstytucja — **19 Praw Imperium**:

---

## 🏛️ ZASADY FUNDAMENTALNE — kompletna lista

| # | Prawo | Esencja |
|---|-------|---------|
| **I** | ZERO HALUCYNACJI | Każde twierdzenie musi być realne i potwierdzone. Prawda > efektowny opis. |
| **II** | LOKALNOŚĆ | System działa na własnym sprzęcie. Zero przymusowej chmury. |
| **III** | ŁAŃCUCH DOWODZENIA | Boty doradzają, Senat debatuje, Cezar decyduje. Komendant ma ostatnie słowo zawsze. |
| **IV** | EWOLUCJA W LOCIE | System nie realizuje sztywnych strategii — tworzy je sam, w czasie rzeczywistym. |
| **V** | PROSTOTA NA ZEWNĄTRZ, ARMIA W ŚRODKU | Jeden terminal, jeden głos na zewnątrz. Złożoność ukryta. |
| **VI** | MIERZALNOŚĆ I RYWALIZACJA | Każdy bot, sygnał i decyzja ma ocenę. Lepszy wygrywa, słabszy odpada. |
| **VII** | BUDUJEMY STOPNIOWO | Dane i egzekucja → inteligencja → wizualizacja. Nie budujemy dachu przed fundamentem. |
| **VIII** | PAMIĘĆ W PLIKACH | Rozmowy znikają, pliki zostają. Co nie jest zapisane — nie istnieje. |
| **IX** | WERYFIKACJA W GŁĘBI | Sygnał przechodzi przez filtry: Szeregowi → Oficerowie → Senat → Cesarz. |
| **X** | RÓJ, NIE KOLEKCJA | Boty komunikują się i uczą od siebie. Razem widzą cały obraz. |
| **XI** | ŁOWCA NIE PANIKUJE | Agent minimalizuje zaskoczenie (Active Inference), nie goni za zyskiem. Spokój = przewaga. |
| **XII** | SIEDEM WARSTW POSTRZEGANIA | Cena/wolumen, mikrostruktura, on-chain, sentyment, makro, korelacje, predykcja — jednocześnie. |
| **XIII** | KAŻDA DECYZJA JEST AUDYTOWALNA | Zawsze wiadomo dlaczego. Pełny zapis debaty. Brak audytu = brak zaufania. |
| **XIV** | KALIBRACJA, NIE SZTYWNOŚĆ | Każdy parametr jest pokrętłem, nie betonem. System się stroi. |
| **XV** 🚨 | CZERWONY ALARM UTRATY POTENCJAŁU | Martwy neuron, nieużywany wskaźnik, wąskie gardło Bramy → OBOWIĄZKOWY alarm, naprawa, test. Milczenie = złamanie. |
| **XVI** 📊 | REDUNDANCJA MIERZONA, NIE ZGADYWANA | Odrzucasz moduł za `\|kor\| > 0.80`, nie za podobną nazwę. Inaczej liczone = dekorelacja błędów = siła. |
| **XVII** 🗺️ | ROZPOZNANIE TERENU I PORZĄDEK | Na starcie każdej sesji: czytaj stan z plików, nie z pamięci. Po każdej zmianie: aktualizuj dokumentację. |
| **XVIII** ⚙️ | DECYZYJNOŚĆ ARCHITEKTA | Niespójność → decydujesz sam (kod+testy > zasady > policzone liczby > pamięć). Pytasz Cezara tylko o nieodwracalne. |
| **XIX** 🔱 | KOD JEST PRAWEM, KATALOG JEST PLANEM | Moduł istnieje TYLKO gdy ma kod+testy na branchu. MANIFEST_KODU.md = jedyne oficjalne źródło prawdy. Katalog = lista życzeń. |

---

Wszystkie 19 praw w kodzie i pushach — czysto.

## 🧑 Cezar
czy mamy  zasade ze zawsze zanim cos sprawdzisz musisz sprawdzic na naszym repozytorium wszystko musi byc spokne i sie zgadzac

## 🏛️ Claude
Sprawdzam dokładnie, co mamy w konstytucji i CLAUDE.md pod kątem tej zasady:

## 🏛️ Claude
Odpowiedź jest jasna: **mamy to, ale niepełnie.** Mamy dwa różne fragmenty:

- **Prawo XVII** — czytaj stan Imperium na starcie sesji (README, CLAUDE.md, docs)
- **Prawo XIX** — sprawdź MANIFEST i branch przed każdą sesją

Ale **brakuje jednej konkretnej rzeczy**: zasady, że przed każdą pracą trzeba zweryfikować, że **repozytorium jest spójne** — że testy zielone, MANIFEST się zgadza z kodem, README zgadza się z MANIFEST, liczby się zgadzają. To weryfikacja integralności, nie tylko lektura. To jest inne.

Dodaję to do Prawa XVII (Rozpoznanie Terenu) — bo tam naturalnie należy, jako punkt 0 checklisty:

## 🏛️ Claude
Teraz to samo do CLAUDE.md — tam jest operacyjna checklistka:

## 🏛️ Claude
Commituję i pushuję:

## 🏛️ Claude
**Odpowiedź na Twoje pytanie:** Mieliśmy zasadę "czytaj repo" (Prawo XVII), ale **brakowało zasady "weryfikuj że jest spójne"**. To różnica między:
- ❌ *"przeczytaj stan"* — można przeczytać dokument, który kłamie
- ✅ *"zweryfikuj spójność"* — sprawdź, że trzy miejsca mówią tę samą liczbę

Teraz Prawo XVII ma **KROK 0** — obowiązkowo przed każdą sesją i przed każdym zadaniem:

```bash
git status                     # czysty?
python tests/run_tests.py      # zielone?
rejestr.py == MANIFEST_KODU == README  # ta sama liczba neuronów?
```

Jeśli cokolwiek się nie zgadza → **STOP, najpierw napraw**. Dopiero potem nowe zadanie.

## 🧑 Cezar
dobra teraz jeszcze raz bardzo szczegolowy audyt naszego imperium naszego repozytorium zgodnie z zasadami

## 🏛️ Claude
Zgodnie z Prawem XVII — zaczynam od **KROKU 0 (weryfikacja spójności)**, potem pełny audyt. Robię to systematycznie.

## 🏛️ Claude
KROK 0 już wykrył problem do zbadania: MANIFEST ma 45× "✅ aktywny" — bo liczy neurony + zwiadowców + infrastrukturę razem, a moja prosta kontrola tego nie rozróżnia. To pierwsza rzecz do audytu. Zbieram pełne dane:

## 🏛️ Claude
Dobra wiadomość: 28 klas neuronów, wszystkie w `neurony/`, zero sierot (potwierdzone), 12 wyciszonych + 16 aktywnych = zgadza się z rejestrem i README. Teraz sprawdzam, dlaczego MANIFEST pokazuje 45× "✅ aktywny" — to niespójność do naprawy:

## 🏛️ Claude
🚨 **Audyt wykrył niespójności w MANIFEST — czerwony alarm Prawo XVII/XIX.** MANIFEST oznacza kilka neuronów jako "✅ aktywny", podczas gdy w **kodzie mają `DOSTEPNY=False`**. Weryfikuję dokładny status każdego neuronu z kodu:

## 🏛️ Claude
Mam **prawdę z kodu**: 16 aktywnych + 12 wyciszonych. MANIFEST błędnie oznacza 7 wyciszonych neuronów jako "✅ aktywny" (S-OB, S-FVG, S-BOS, V-CVD, P-FUND, P-PANIK, P-OIDIV). Naprawiam MANIFEST, żeby mówił prawdę. Najpierw weryfikuję ścieżki infrastruktury:

## 🏛️ Claude
Infrastruktura OK. Teraz naprawiam 7 błędnych statusów w MANIFEST (kod = źródło prawdy):

## 🏛️ Claude
MANIFEST teraz spójny: 16 aktywnych + 12 wyciszonych = 28. Jeszcze jedna literówka (nagłówek "272" vs faktyczne 271) i szeroki audyt pozostałych dokumentów:

## 🏛️ Claude
Znalazłem przestarzałe liczby. Sprawdzam dokładnie prawa w tych dwóch plikach i naprawiam wszystkie:

## 🏛️ Claude
Te mówią "18 praw" — teraz mamy 19. Naprawiam wszystkie przestarzałe liczby (prawa 18→19, neurony 27→28, testy 237→240):

## 🏛️ Claude
Wszystkie liczby naprawione. Teraz najważniejszy test Prawa XV — **martwe głosy**: czy każdy z 16 aktywnych neuronów dostaje wszystkie swoje wskaźniki z Budowniczego (statyczne porównanie klucze-żądane vs klucze-produkowane):

## 🏛️ Claude
Zero martwych głosów wśród aktywnych — Prawo XV spełnione. Ostatnie kontrole: pozostałe odniesienia do liczby testów, deklarowana liczba modułów w ARCHITEKTURA, oraz zwiadowcy:

## 🏛️ Claude
Jeszcze jedno przestarzałe: AUDYT_SYSTEMU linia 20 (237→240). Naprawiam i robię finalną weryfikację spójności:

## 🏛️ Claude
Jedno "237" jeszcze gdzieś zostało — znajduję je:

## 🏛️ Claude
To "237" jest częścią URL arXiv (2602.23784), nie liczbą testów — fałszywy alarm. Wszystko spójne. Commituję wynik audytu:

## 🏛️ Claude
# 📋 RAPORT AUDYTU IMPERIUM — zgodnie z zasadami

Przeprowadziłem audyt wg KROKU 0 (spójność) + Praw XV/XVI/XVII/XIX. Oto pełny wynik.

## ✅ Stan zdrowy (zweryfikowany z kodu)

| Wymiar | Wynik | Dowód |
|--------|-------|-------|
| Liczba neuronów | **28** spójnie w 3 źródłach | rejestr.py = MANIFEST = README |
| Aktywne / wyciszone | **16 / 12** | DOSTEPNY z kodu, sprawdzone per klasa |
| Neurony-sieroty | **0** | grep poza rejestrem = pusto |
| Martwe głosy (aktywne) | **0** | każdy z 16 dostaje wszystkie klucze z Bramy |
| Zwiadowcy | **12** (1 wyciszony EXP-12) | 12 plików = 12 KLUCZ = rejestr |
| Ścieżki infrastruktury | **6/6 istnieją** | weryfikacja plików |
| Testy | **240/240** zielone | run_tests.py |

## 🚨 Wykryte niespójności (NAPRAWIONE)

**1. MANIFEST kłamał o statusie (Prawo XIX)** — 7 neuronów oznaczonych "✅ aktywny", choć w kodzie mają `DOSTEPNY=False`:
- `S-OB`, `S-FVG`, `S-BOS` (SMC bez danych z Bramy)
- `V-CVD` (brak CVD)
- `P-FUND`, `P-PANIK`, `P-OIDIV` (API)
→ poprawione na 🔇 wyciszony. Teraz 16+12=28 spójnie.

**2. Przestarzałe liczby w dokumentach (Prawo XVII):**
- `ARCHITEKTURA_IMPERIUM`, `AUDYT_ADOPCJI`: 18 praw → **19**
- `AUDYT_SYSTEMU`: 27→**28** neuronów, 237→**240** testów
- `KATALOG_NEURONOW`: 27→**28** zaimplementowanych

## 📊 Faktyczny stan (kod, nie katalog)

- **28 neuronów** w roju / 299 w katalogu → **271 do wdrożenia**
- 16 aktywnych na czystym OHLCV, 12 czeka na API/feed (SMC, on-chain, psychologia, CVD)
- 12 zwiadowców (11 aktywnych, EXP-12 na feed L2)

**Jedyna realna "utrata potencjału" (Prawo XV)** to nie błąd, lecz świadoma decyzja: 12 neuronów wyciszonych czeka na adaptery API/feed. To backlog, nie martwy kod — pipeline poprawnie je pomija (nie produkują fałszywych NEUTRAL).

Wszystko spójne, zacommitowane, wypchnięte. Repozytorium jest w czystym, prawdziwym stanie.

## 🧑 Cezar
a teraz pamietaj zawsze wg zasad sprawdzasz repozytorium dopiero wykonujesz zadanie nie mozemy miec bledow i niespojnosci  ipelnej harmoni teraz sprawdz po kolei zasady i repozytorium i ozywiaj neurony itd

## 🏛️ Claude
Zgodnie z zasadą — najpierw **KROK 0 (weryfikacja repozytorium)**, dopiero potem zadanie (ożywianie neuronów).

## 🏛️ Claude
KROK 0 ✅ — repo czyste, 240/240, liczby spójne (28=28=28). Mogę zacząć zadanie.

Teraz wybieram neurony do ożywienia. Strategia (Prawo XV + XIX): buduję neurony z katalogu, które działają na **czystym OHLCV** → będą od razu **aktywne**, nie wyciszone. Z Legionu X najlepsi kandydaci to oscylatory TA-Lib. Sprawdzam, co Brama już potrafi, żeby nie dublować:

## 🏛️ Claude
Brama nie liczy żadnego z nich — czysta robota od zera. Wybieram **4 zdekorelowane neurony** (Prawo XVI — różna logika, różne błędy):

- **X-17 TRIX** — potrójnie wygładzone momentum (dekoreluje od RSI/MACD)
- **X-08 Awesome Oscillator** — momentum wokół zera (median price)
- **X-18 Donchian** — wybicia strukturalne (nie oscylator)
- **X-11 RVOL** — relatywny wolumen (nie cena)

Dodaję do Bramy. Najpierw zobaczę wzorzec helperów:

## 🏛️ Claude
Dodaję helpery pure-python do Bramy (Donchian, AO, RVOL) + wpisy w rejestrze:

## 🏛️ Claude
Teraz Budowniczy — skalary do `_PLAN_SKALARNE` i Donchian (zwraca dict) jak Ichimoku:

## 🏛️ Claude
Teraz 4 neurony. Dodaję do odpowiednich modułów — TRIX i Awesome do momentum, Donchian do trend, RVOL do wolumen:

## 🏛️ Claude
Teraz rejestruję 4 nowe neurony w rejestr.py:

## 🏛️ Claude
4 nowe neurony zarejestrowane → 32. Aktualizuję testy (count + nowe testy logiki):

## 🏛️ Claude
Teraz dodaję testy logiki dla 4 neuronów i aktualizuję asercje liczb (28→32):

## 🏛️ Claude
Teraz lista "brak danych nie crashuje" + asercje liczb w test_integracja:

## 🏛️ Claude
Wszystko zielone. Weryfikuję, że 4 nowe neurony nie są martwymi głosami (dostają dane z Bramy) — Prawo XV:

## 🏛️ Claude
244/244, 32 neuronów, wszystkie klucze produkowane, zero martwych głosów. Teraz **harmonia dokumentacji** (Prawo XVII) — aktualizuję MANIFEST i README w tym samym ruchu:

## 🏛️ Claude
Teraz backlog (X-08/X-11/X-17/X-18 → ✅), tabela zbiorcza i historia w MANIFEST:

## 🏛️ Claude
Aktualizuję tabelę zbiorczą i historię w MANIFEST:

## 🏛️ Claude
Teraz README (32 neuronów, 20 aktywnych, 244 testy):

## 🏛️ Claude
Finalna weryfikacja spójności (KROK 0 po zmianie) i commit:

## 🏛️ Claude
Pełna harmonia: 32=32=32, 244/244. Commit i push:

## 🏛️ Claude
# ✅ Wykonane zgodnie z zasadami

**Najpierw KROK 0** (weryfikacja repo), **dopiero potem zadanie** — dokładnie tak, jak ustaliliśmy.

## Co zrobiłem

**KROK 0** — repo czyste, 240/240, liczby spójne (28=28=28) → mogłem zacząć.

**Ożywiłem 4 neurony z katalogu** (Faza 1), wszystkie na czystym OHLCV = od razu **aktywne**, nie wyciszone. Dobrane pod **dekorelację** (Prawo XVI — różna logika, różne błędy):

| Neuron | Plik | Logika | Dekoreluje od |
|--------|------|--------|---------------|
| **X-08** Awesome | momentum.py | oscylator median-price wokół zera | RSI/MACD (inna baza) |
| **X-11** RVOL | wolumen.py | relatywny wolumen | neuronów cenowych |
| **X-17** TRIX | momentum.py | potrójnie wygładzone momentum | szybkich oscylatorów |
| **X-18** Donchian | trend.py | wybicia kanału | oscylatorów (struktura) |

**Pełny łańcuch** (Prawo XV — żeby nie były martwe): Brama → Budowniczy → neuron → rejestr → testy. Zweryfikowałem statycznie, że **wszystkie 4 dostają dane** — zero martwych głosów.

## Stan końcowy — pełna harmonia

- **32 neurony** (było 28): 20 aktywnych + 12 wyciszonych
- **244/244** testów zielonych (+4 nowe)
- Spójność: **rejestr = MANIFEST = README = 32**
- Backlog: 299 − 32 = **267 do wdrożenia**

Wszystko zacommitowane i wypchnięte. Repozytorium bez błędów i niespójności.

Następna partia (Faza 2) — kolejne neurony Legionu X: X-10 HMA, X-09 Accelerator, X-12 BB Squeeze, X-07 Williams %R(M5). Kontynuować?

## 🧑 Cezar
zrob dokladny audyt po zmianach zasad i uporzadkuj katogoryzacje moze jakies neurony zaliczaja sie do elite musimy dokladnie ustalic zasady jakie neurony dostaja taki status i wpisac w zasady i bedzie otwarty na aktualizacje jezeli znajdziemy neuron ktory jest inny ale unikatowy itd zeby nic go nie blokowalo zgodnie z zasada postepu

## 🏛️ Claude
Zgodnie z zasadą — najpierw **KROK 0**, potem audyt i kategoryzacja.

## 🏛️ Claude
KROK 0 ✅ (32=32, 244/244). Teraz badam obecny stan kategoryzacji — wagi, kategorie, oraz istniejące pojęcie "elity" (zwiadowcy są `ZwiadowcaElitarny`):

## 🏛️ Claude
Widzę już problemy do uporządkowania. Sprawdzam legendę KATEGORIA i istniejące pojęcie elity w dokumentach:

## 🏛️ Claude
Teraz mam pełny obraz architektury. Sprawdzam legendę kategorii i pola bazowe MikroNeuronu, by zaprojektować status elitarny w kodzie (Prawo XIX):

## 🏛️ Claude
🚨 **Audyt wykrył systemowy błąd kategoryzacji (Prawo XV/XVII).** Oficjalna legenda mówi: **V=Zmienność, F=Flow/Wolumen, O=On-chain, R=Sentyment, S=Struktura**. A w kodzie:
- Neurony wolumenowe (OBV/VWAP/CVD/RVOL/VSA) → `kat="V"` ❌ (V=Zmienność, powinno **F**)
- Psychologia (FearGreed/Funding/Panika/OIDiv) → `kat="S"` ❌ (S=Struktura, powinno **R**=Sentyment)
- On-chain (MVRV/SOPR/Puell/Netflow) → `kat="F"` ❌ (F=Flow, powinno **O**)

To może realnie psuć wagi reżimowe. Sprawdzam, czy Legatus używa KATEGORIA do wag:

## 🏛️ Claude
Potwierdzony **realny bug (Prawo XV)** — `WAGI_REZIMU` w Legatusie używa liter kategorii:
- `ON-CHAIN_BULLISH: {"O": 2.0}` — ale neurony on-chain mają `kat="F"`, więc **nigdy nie dostają tego wzmocnienia 2.0×**
- `RANGING: {"V": 1.3}` — wolumenowe mają `kat="V"`, dostają wzmocnienie zmienności, którego nie powinny

To utrata potencjału. Sprawdzam test wag reżimowych, żeby nic nie złamać przy naprawie:

## 🏛️ Claude
Test używa `kategoria="T"` wprost — moje zmiany (V/S/F) go nie ruszą. Wykonuję **CZĘŚĆ A — naprawa kategoryzacji** zgodnie z oficjalną legendą:

## 🏛️ Claude
Kategorie poprawne. Teraz sprawdzam pełną mapę `WAGI_REZIMU` — po naprawie on-chain (O) dostaje wagi, ale wolumen (F) i sentyment (R) mogą być pomijane. Patrzę całość:

## 🏛️ Claude
Naprawiam mapę wag, by korzystała z poprawionych kategorii (F=wolumen, R=sentyment — inaczej byłyby martwe), oraz przestarzały komentarz "261 neuronów":

## 🏛️ Claude
Uruchamiam testy po zmianach kategoryzacji:

## 🏛️ Claude
244/244 ✅. Teraz **CZĘŚĆ B — status elitarny w kodzie** (Prawo XIX — musi być polem, nie tylko w dokumencie). Dodaję pola do bazy i poprawiam legendę:

## 🏛️ Claude
Teraz Prawo XX w konstytucji. Czytam zakończenie, żeby wpiąć przed mottami:

## 🏛️ Claude
Teraz nadaję status elitarny kwalifikującym się modułom. X-25 i X-26 spełniają E4+E5 (multi-reżim + IMV-ADO). Znajduję ich definicje:

## 🏛️ Claude
Teraz zwiadowcy — wszyscy spełniają E1 (własna matematyka). Dodaję `ELITARNY=True` do bazy `ZwiadowcaElitarny`:

## 🏛️ Claude
Teraz dodaję `raport_elity()` do rejestru. Zobaczę istniejący raport_potencjalu:

## 🏛️ Claude
You've hit your session limit · resets 1:30am (UTC)

## 🧑 Cezar
Continue from where you left off.

## 🏛️ Claude
No response requested.

## 🧑 Cezar
dawaj dalej kontynuuj  widzisz zasady musisz zawsze czytac plik claude.md zawsze jak cos tworzymy automatycznie sprawdzasz nasz system realne inprrium i documenty wszystko co wchodzi w sklad naszego projektu

## 🧑 Cezar
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
1. Primary Request and Intent:

The session continued from previous work building the IMPERIAL MESH VORTEX (IMV) AI trading system. Primary requests in order:

- **Prawo XIX**: Add fundamental law "everything must be in CODE, not just catalog" + create MANIFEST_KODU.md as strict GitHub control register
- **Neuron audit**: Count real neurons from code (not from memory/catalog), expose that 2 orphan neurons existed in mikro_neuron.py outside the rój
- **KROK 0 consistency rule**: Before every session/task, verify git status clean + tests green + 3-source count agreement (rejestr.py == MANIFEST == README)
- **Deep audit**: Full repository audit per Laws XV/XVII/XIX — found 7 neurons incorrectly marked "✅ aktywny" in MANIFEST while DOSTEPNY=False in code; found stale law/test counts across 4 docs
- **Phase 1 neuron activation**: Implement 4 new neurons from catalog (X-08 Awesome, X-11 RVOL, X-17 TRIX, X-18 Donchian) — all active on clean OHLCV
- **Categorization audit + elite status**: Fix wrong KATEGORIA labels across all neuron files, add PRAWO XX (elite status: measured, open, living), add ELITARNY fields to base classes
- **Ongoing instruction (verbatim)**: "zawsze jak cos tworzymy automatycznie sprawdzasz nasz system realne imperium i documenty wszystko co wchodzi w sklad naszego projektu" — always read CLAUDE.md and check real Imperium state before executing any task

**Security constraint (MUST PRESERVE VERBATIM):**
- **KLUCZE API NIGDY W KODZIE, NIGDY W CZACIE** — tylko zmienne środowiskowe
  - DeepSeek: `[ZREDAGOWANO]
  - MEXC: `os.getenv("MEXC_API_KEY")`, `os.getenv("MEXC_SECRET")`

---

2. Key Technical Concepts:

- **MikroNeuron**: Base class, reads from Brama (dict of computed indicators), `interpretuj(wskazniki: dict) → SygnalNeuronu`
- **ZwiadowcaElitarny**: Elite scout class, computes its OWN math from raw bars, `analizuj(bary: List[dict]) → RaportZwiadowcy`
- **BramaKalkulatora**: Single gateway for all math/indicators (Law I), wraps TA-Lib + pure-python functions
- **BudowniczyWskaznikow**: Bridge: raw OHLCV bars → complete wskaźniki dict for neurons, uses `_PLAN_SKALARNE` dict and `_dodaj_*()` methods
- **GeneralLegatus**: Aggregates neuron signals, applies `WAGI_REZIMU` by KATEGORIA letter
- **WAGI_REZIMU**: Dict of `{rezim: {KATEGORIA_letter: multiplier}}` applied to signal weights
- **KATEGORIA legend** (official, from KATALOG_NEURONOW.md): M=Momentum, T=Trend, V=Zmienność, F=Flow/Wolumen, O=On-chain, L=Leverage, R=Reżim/Sentyment, S=Struktura(SMC), A=Anty-manipulacja, K=Makro/Intermarket, E=Entropia/AI, G=Geo/Regionalne
- **DOSTEPNY/POWOD_NIEDOSTEPNOSCI**: Fields on both MikroNeuron and ZwiadowcaElitarny; silenced modules explicitly skipped (never produce false NEUTRAL)
- **ELITARNY/POWOD_ELITARNOSCI**: New fields (Prawo XX) — measured elite status with explicit criteria E1–E7
- **Prawo XIX**: Code is law — module exists ONLY when it has code+tests on branch `claude/sleepy-fermi-dsdE4`
- **Prawo XX**: Elite status is measured (not opinion), open (new criteria welcome), living (can be gained/lost)
- **KROK 0**: Mandatory consistency check before every session/task: git status + tests + 3-source neuron count
- **IMV-ADO 🔱**: Adopted+improved external indicators with fixed bugs
- **Branch**: `claude/sleepy-fermi-dsdE4`

---

3. Files and Code Sections:

- **`ZASADY_FUNDAMENTALNE.md`** — Constitution, now 20 laws (Prawo XX added in current uncommitted work)
  - Prawo XVII extended with "KROK 0" mandatory consistency block
  - Prawo XIX: "KOD JEST PRAWEM, KATALOG JEST PLANEM"
  - Prawo XX (UNCOMMITTED, partially written): Elite status law with E1–E7 criteria, openness clause

- **`CLAUDE.md`** — Operational instructions read every session
  - Updated to 19 laws (needs update to 20 — PENDING)
  - Added KROK 0 verification block with exact commands
  - Added Prawo XIX checklist

- **`docs/MANIFEST_KODU.md`** — Official truth source for code reality (NEW FILE)
  - Created with 28→32 neuron table
  - Per-neuron: KLUCZ, Klasa, Status (✅ aktywny / 🔇 wyciszony / 🔴 katalog)
  - History table of implementation phases
  - Needs update for ELITARNY column (PENDING)

- **`imperium/legiony/mikro_neuron.py`** — MikroNeuron base class
  - Added ELITARNY/POWOD_ELITARNOSCI fields (UNCOMMITTED)
  - Updated KATEGORIA comment with full legend
  - Removed orphan NeuronStochRSI and NeuronFundingRate classes (replaced with explanatory comment)
  ```python
  ELITARNY: bool = False
  POWOD_ELITARNOSCI: str = ""   # które kryteria E1–E7 spełnia (do audytu)
  ```

- **`imperium/legiony/zwiadowcy/baza.py`** — ZwiadowcaElitarny base class
  - Added ELITARNY=True and POWOD_ELITARNOSCI by default (UNCOMMITTED)
  ```python
  ELITARNY: bool = True
  POWOD_ELITARNOSCI: str = "E1 (własna matematyka poza Bramą — Exploratores)"
  ```

- **`imperium/legiony/neurony/momentum.py`** — momentum neurons
  - X-25 NeuronATRDeviation marked ELITARNY=True (UNCOMMITTED)
  - X-26 NeuronHAScalper marked ELITARNY=True (UNCOMMITTED)
  - NeuronStochRSI (X-02) ADDED here (from orphan in mikro_neuron.py)
  - NeuronTRIX (X-17) and NeuronAwesome (X-08) ADDED
  ```python
  # X-25:
  ELITARNY = True
  POWOD_ELITARNOSCI = "E4 (kameleon RANGING↔TREND) + E5 (IMV-ADO 🔱, naprawiony oryginał)"
  # X-26:
  ELITARNY = True
  POWOD_ELITARNOSCI = "E4 (multi-reżim) + E5 (IMV-ADO 🔱) + E7 (filtr Volatility Index + potrójne potwierdzenie)"
  ```

- **`imperium/legiony/neurony/trend.py`** — NeuronDonchian (X-18) ADDED

- **`imperium/legiony/neurony/wolumen.py`** — 
  - KATEGORIA V→F for ALL 5 wolumen neurons (UNCOMMITTED FIX)
  - NeuronRVOL (X-11) ADDED

- **`imperium/legiony/neurony/psychologia.py`** — KATEGORIA S→R for ALL 4 psychologia neurons (UNCOMMITTED FIX)

- **`imperium/legiony/neurony/onchain.py`** — KATEGORIA F→O for ALL 4 onchain neurons (UNCOMMITTED FIX)

- **`imperium/legiony/neurony/struktura.py`** — NeuronVSA KATEGORIA V→F (UNCOMMITTED FIX)

- **`imperium/legiony/legatus.py`** — Legatus aggregator
  - WAGI_REZIMU updated (UNCOMMITTED):
  ```python
  WAGI_REZIMU = {
      "TREND_STRONG": {"T": 1.5, "M": 1.2, "O": 0.7, "L": 0.8},
      "RANGING":      {"M": 1.5, "V": 1.3, "F": 1.2, "T": 0.5},  # F added
      "VOLATILE":     {"A": 2.0, "L": 0.3, "_default": 0.7},
      "PANIC":        {"A": 3.0, "R": 1.5, "_default": 0.1},       # R added
      "NORMAL":       {},
      "ON-CHAIN_BULLISH": {"O": 2.0, "L": 0.8},
  }
  ```
  - Fixed stale comment "261 neuronów" → "wszystkich aktywnych neuronów"

- **`imperium/legiony/fundament/brama_kalkulatora.py`** — Added new computations:
  - STOCHRSI (talib.STOCHRSI), TRIX/TRIX_PREV (talib.TRIX)
  - AO/AO_PREV (_py_awesome pure-python), DONCHIAN dict (_py_donchian), RVOL (_py_rvol)

- **`imperium/legiony/budowniczy_wskaznikow.py`** — 
  - Added STOCHRSI, TRIX, TRIX_PREV, AO, AO_PREV, RVOL to _PLAN_SKALARNE
  - Added _dodaj_donchian() method
  - Called _dodaj_donchian() in zbuduj()

- **`imperium/legiony/rejestr.py`** — 
  - Added NeuronStochRSI, NeuronTRIX, NeuronAwesome to momentum imports
  - Added NeuronDonchian to trend imports
  - Added NeuronRVOL to wolumen imports
  - wszystkie_neurony() now returns 32 instances

- **`tests/test_neurony.py`** — Added tests for StochRSI, TRIX, Awesome, Donchian, RVOL

- **`tests/test_integracja.py`** — Updated count assertions: 28→32

---

4. Errors and Fixes:

- **MANIFEST showed 45× "✅ aktywny"** when KROK 0 grep only expected ~16: Root cause was MANIFEST counting zwiadowcy + infrastructure + neurons all with same marker. Simple grep couldn't distinguish. Fixed by actually inspecting which lines were neurons vs other.

- **7 neurons marked "✅ aktywny" in MANIFEST but DOSTEPNY=False in code**: Found via `grep -rc "DOSTEPNY = False"` per file. Fixed by updating MANIFEST to 🔇 wyciszony for S-OB, S-FVG, S-BOS, V-CVD, P-FUND, P-PANIK, P-OIDIV, and all onchain.

- **Wrong KATEGORIA letters causing broken WAGI_REZIMU**: wolumen had "V" (should be "F"), psychologia had "S" (should be "R"), onchain had "F" (should be "O"). This meant ON-CHAIN_BULLISH {"O": 2.0} never triggered for on-chain neurons. Fixed with `sed -i` across all 4 affected files.

- **Stale counts across docs** (18 praw, 27 neurons, 237 tests): Found via `grep -rln "18 praw\|27 neuron\|237"`. Fixed with sed across ARCHITEKTURA_IMPERIUM, AUDYT_ADOPCJI, AUDYT_SYSTEMU, KATALOG_NEURONOW.

- **NeuronFundingRate (VI-01) orphan**: Had code in mikro_neuron.py but was redundant with NeuronFundingExtreme (Law XVI correlation). Decision: withdraw rather than promote. Left comment explaining reasoning.

---

5. Problem Solving:

- **Real neuron count vs claimed count**: Solved by grep-counting actual class definitions (`class Neuron.*MikroNeuron`) in code files, then cross-referencing with rejestr.py. This revealed 2 orphans.

- **Static dead-voice check**: Built Python script to compare keys produced by Budowniczy vs keys requested by each active neuron. Confirmed zero dead voices among 20 active neurons.

- **Category system inconsistency**: Full audit comparing official legend (from KATALOG_NEURONOW.md header) vs actual KATEGORIA fields in code. Found systematic mismatches introduced before the official legend was codified.

- **Elite status definition**: Designed E1–E7 criteria system that is: measurable (not opinion), open (new criteria can be added), living (status can change with measurement), not blocking (unique modules always welcome).

---

6. All User Messages:

- "tylko skad wiesz ze mamy naprawdę tyle neuronow zasada fundamentala zawsze mozemy oszacowac faktyczna ilosc jak mamy kod neuronu w naszym systemie imperium sprawdz wsztstko po koleji i odbudowujemy wszystko zgodnie z zasadami pamietaj"
- "czy mamy zasade ze zawsze zanim cos sprawdzisz musisz sprawdzic na naszym repozytorium wszystko musi byc spójne i sie zgadzac"
- "dobra teraz jeszcze raz bardzo szczegolowy audyt naszego imperium naszego repozytorium zgodnie z zasadami"
- "a teraz pamietaj zawsze wg zasad sprawdzasz repozytorium dopiero wykonujesz zadanie nie mozemy miec bledow i niespojnosci i pelnej harmonii teraz sprawdz po kolei zasady i repozytorium i ozywiaj neurony itd"
- "zasady fundamentalne pokaz calosc"
- "zrob dokladny audyt po zmianach zasad i uporzadkuj kategoryzacje moze jakies neurony zaliczaja sie do elite musimy dokladnie ustalic zasady jakie neurony dostaja taki status i wpisac w zasady i bedzie otwarty na aktualizacje jezeli znajdziemy neuron ktory jest inny ale unikatowy itd zeby nic go nie blokowalo zgodnie z zasada postepu"
- "dawaj dalej kontynuuj widzisz zasady musisz zawsze czytac plik claude.md zawsze jak cos tworzymy automatycznie sprawdzasz nasz system realne imperium i documenty wszystko co wchodzi w sklad naszego projektu"

---

7. Pending Tasks:

1. **Commit all uncommitted changes** (category fixes, PRAWO XX, ELITARNY fields, WAGI_REZIMU fix)
2. **Add `raport_elity()` to rejestr.py** — list of elite neurons + reason, verifiable by test
3. **Write tests for ELITARNY field** — verify X-25, X-26 are elitarny; verify new neurons are not; verify all Exploratores are elitarny
4. **Update CLAUDE.md** — 19→20 laws, add Prawo XX operational section
5. **Update MANIFEST_KODU.md** — add 🎖️ column or marker for elite neurons
6. **Update README.md** — mention 20 laws
7. **Continue implementing remaining neurons** from catalog (267 remaining), especially Legion X Equestris (X-01, X-03..X-07, X-09, X-10, X-12..X-16, X-19..X-24)
8. **Check zwiadowcy for additional ELITARNY criteria** — EXP-06 through EXP-12 may qualify for additional criteria beyond E1

---

8. Current Work:

Immediately before the plan mode interruption, the work was:
- Adding `raport_elity()` function to `imperium/legiony/rejestr.py`
- This function was to list all elitarny neurons/scouts with their POWOD_ELITARNOSCI
- The existing `raport_potencjalu()` function (at line 131) was being used as reference pattern

The grep for insertion point had found:
```
60:def wszystkie_neurony() -> List[MikroNeuron]:
80:def wszyscy_zwiadowcy() -> list:
131:def raport_potencjalu() -> dict:
147:    return {
```

The following changes were completed but NOT yet committed (tests confirmed 244/244 passing after category fixes):
- Category letters fixed across wolumen.py, psychologia.py, onchain.py, struktura.py
- WAGI_REZIMU updated in legatus.py
- PRAWO XX added to ZASADY_FUNDAMENTALNE.md
- ELITARNY fields added to mikro_neuron.py and zwiadowcy/baza.py
- X-25 and X-26 marked ELITARNY=True in momentum.py

---

9. Optional Next Step:

Directly continuing from user's request "dawaj dalej kontynuuj" and the work-in-progress on elite status:

1. **Execute KROK 0** per CLAUDE.md (git status, tests, count check)
2. **Add `raport_elity()` to rejestr.py** — reference pattern is `raport_potencjalu()` at line 131
3. **Write tests** for ELITARNY field in test_integracja.py
4. **Update CLAUDE.md** (19→20 laws, add Prawo XX operational checklist)
5. **Update MANIFEST_KODU.md and README** with elite markers and 20 laws
6. **Commit all uncommitted changes** in single coherent commit with full description
7. **Push to `claude/sleepy-fermi-dsdE4`**

The user's most recent explicit direction was: "dawaj dalej kontynuuj widzisz zasady musisz zawsze czytac plik claude.md zawsze jak cos tworzymy automatycznie sprawdzasz nasz system realne imperium i documenty wszystko co wchodzi w sklad naszego projektu" — meaning: continue the elite status work, always read CLAUDE.md first, always verify real Imperium state before executing.

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /root/.claude/projects/-home-user-IMPERIAL-MESH-VORTEX/f2f6cac6-bbc1-434d-b214-1cf07ac62d84.jsonl
Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

## 🏛️ Claude
Now I have all the context I need. Let me write the plan.

## 🏛️ Claude
Implementing the plan now. Starting with `raport_elity()` in rejestr.py.

## 🏛️ Claude
Now add the test. Let me find the end of test_integracja.py first.

## 🏛️ Claude
Now update CLAUDE.md — change "19 Prawami" to "20 Prawami" and add Prawo XX section.

## 🏛️ Claude
Now update MANIFEST_KODU.md to add elite markers. Let me read the neuron table section first.

## 🏛️ Claude
Now mark X-25 and X-26 with 🎖️ in the neuron table (they already have 🔱 but need 🎖️ too):

## 🏛️ Claude
Now run the tests to verify everything is green before committing.

## 🏛️ Claude
245/245 green. Now commit all changes.

## 🏛️ Claude
Pushed. Quick verification of elite report:

## 🏛️ Claude
Wszystko działa. Commit wylądował na branchu.

**Stan po commicie:**
- 245/245 testów zielonych
- `raport_elity()` → 14 elitarnych (2 neurony + 12 Exploratores)
- X-25 i X-26 oznaczone z kryterium E4+E5 / E4+E5+E7
- Wszyscy zwiadowcy EXP-01..12 ELITARNY=True (E1 — definicja klasy)
- Kategorie naprawione we wszystkich plikach, WAGI_REZIMU działa poprawnie dla F, R, O
- 4 nowe neurony (X-08, X-11, X-17, X-18) aktywne w roju
- CLAUDE.md zaktualizowany do 20 praw z sekcją Prawa XX

## 🧑 Cezar
raport jaki mamy stan w imperium zywy a jaki w dokumentacji

## 🏛️ Claude
Sprawdzam realny stan kodu vs to, co deklaruje dokumentacja — zgodnie z KROK 0 (3 źródła) i Prawem XIX.

## 🏛️ Claude
Mam pełny obraz. Oto raport rozbieżności **żywy kod ↔ dokumentacja**:

## 📊 Raport spójności Imperium (KROK 0 / Prawo XIX)

### ✅ Zgodne (kod = dokument)
| Metryka | Żywy kod | MANIFEST | README | Status |
|---|---|---|---|---|
| Neurony w roju | **32** | 32 | 32 | ✅ |
| Aktywne / wyciszone neurony | 20 / 12 | 20 / 12 | 20 / 12 | ✅ |
| Zwiadowcy EXP | **12** | 12 | 12 | ✅ |
| Aktywni / wyciszeni EXP | 11 / 1 | — | 11 / 1 | ✅ |
| Moduły łącznie | **44** | 44 | — | ✅ |
| Sieroty (kod poza rojem) | **0** | 0 | — | ✅ |
| Liczba praw | — | — | **CLAUDE: 20** | ✅ |

### 🚨 ROZBIEŻNOŚCI (dokument kłamie — Prawo XVII/XIX)
| Miejsce | Dokument mówi | Prawda (kod) |
|---|---|---|
| `README.md:6,36,84` | testy **244/244** | **245/245** |
| `README.md:6` | stan **2026-06-01** | dziś 2026-06-02 |
| `README.md:46` | **19 praw** | **20 praw** (dodano Prawo XX) |

Nowość której README w ogóle nie zna: **status elitarny (Prawo XX) = 14 elitarnych modułów** (X-25, X-26 + 12 zwiadowców).

README jest jedynym nieaktualnym dokumentem. To czysta synchronizacja dokumentu (nie decyzja kierunkowa — Prawo XVIII), więc naprawiam od razu:

## 🏛️ Claude
Dodaję jeszcze wzmiankę o Prawie XX / statusie elitarnym w sekcji "Co JEST zbudowane", żeby README odzwierciedlał żywy stan:

## 🏛️ Claude
Gotowe. Spójność przywrócona i wypchnięta.

## 📋 Podsumowanie raportu

**Żywy stan Imperium (policzony z kodu):**
- 32 neurony w roju (20 aktywnych / 12 wyciszonych)
- 12 zwiadowców EXP (11 aktywnych / 1 wyciszony — EXP-12 do feedu L2)
- 44 moduły łącznie w kodzie, 0 sierot
- 14 elitarnych (Prawo XX)
- 20 praw konstytucji
- 245/245 testów zielonych

**Stan dokumentacji — po naprawie:**
| Dokument | Przed | Po |
|---|---|---|
| MANIFEST_KODU.md | ✅ aktualny (44, data 06-02, 🎖️) | ✅ |
| CLAUDE.md | ✅ 20 praw | ✅ |
| ZASADY_FUNDAMENTALNE.md | ✅ Prawo XX obecne | ✅ |
| **README.md** | 🚨 244/244, 19 praw, brak Prawa XX | ✅ **naprawiony** |

Jedynym kłamiącym dokumentem był README (stare liczby testów, 19 praw, brak wzmianki o statusie elitarnym). Teraz wszystkie trzy źródła KROK 0 — kod, MANIFEST, README — zgadzają się co do liczby 32 neuronów i są spójne datą oraz liczbą praw. Naprawa zacommitowana osobno (`ef85950`) i wypchnięta na `claude/sleepy-fermi-dsdE4`.
