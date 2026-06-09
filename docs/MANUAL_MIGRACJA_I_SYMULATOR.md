# 🖥️ MANUAL MIGRACJI NA LAPTOPA + SYMULATOR LIVE

> **Stan na:** 2026-06-09 · **Gałąź:** `claude/sleepy-fermi-dsdE4`
> Dokument dla Cezara-nowicjusza (ZPO): jak przenieść całe Imperium na laptopa
> Fujitsu (Windows 10 Pro, 8 GB RAM) i jak NAPRAWDĘ działa pipeline w live.

---

## 1. ✅ WERYFIKACJA „ORYGINALNYCH NARZĘDZI" (Prawo I — bez halucynacji)

Sprawdzone w kodzie 2026-06-09. Co istnieje realnie, a co było mitem:

| Narzędzie | Status | Plik | Rola |
|---|---|---|---|
| **HERMES** | ✅ ISTNIEJE | `imperium/cesarz/doradcy/hermes.py` | Audytor informacji — kompletność, świeżość, hash, VPIN, eventy makro |
| **FULMEN** | ✅ ISTNIEJE | `imperium/cesarz/doradcy/fulmen.py` | Walidator reżimu — ortogonalny wobec Legatusa |
| **IUSTITIA** | ✅ ISTNIEJE | `imperium/cesarz/doradcy/iustitia.py` | Audytor ryzyka — BLOKUJE = automatyczne veto |
| **ORACLE** | ✅ ISTNIEJE | `imperium/cesarz/doradcy/oracle.py` | Audytor Sharpe — jakość ryzyko/zwrot |
| **PYTHIA** | ✅ ISTNIEJE | `imperium/cesarz/doradcy/pythia.py` | Doradca probabilistyczny — fingerprint matching, p(zysk) |
| **RADA** | ✅ ISTNIEJE | `imperium/cesarz/doradcy/rada.py` | Zbiera werdykty 5 doradców w jedną rekomendację |
| ~~CHIMERA / HAMACHERA~~ | ❌ NIE ISTNIEJE | — | **Brak w kodzie i docs. Halucynacja lub pomyłka nazwy.** Nie liczy się (Prawo I/XIX). |

**5 Doradców Cezara to realne „oryginalne narzędzia"** — mają kod + 24 testy
(`tests/test_doradcy.py`). To NIE jest ściema. Chimera/Hamachera — nie znaleziono
ani śladu; jeśli pojawiła się w rozmowie, to była niezweryfikowana propozycja, nie kod.

---

## 2. 🔄 SYMULATOR LIVE — JAK IMPERIUM MYŚLI W CZASIE RZECZYWISTYM

### 2.1. Pełny przepływ jednego cyklu decyzyjnego

```
                       ┌─────────────────────────────────────────┐
   ŚWIECA (OHLCV) ───► │ AKWEDUKTY (akwedukty/)                   │
   z giełdy/CSV        │  • czytnik danych + ADAPTERY:            │
                       │    AdapterFutures (funding/OI/LS)        │
                       │    AdapterCVD (buy−sell)                 │
                       │    AdapterFearGreed (sentyment)          │
                       └────────────────┬────────────────────────┘
                                        ▼
                       ┌─────────────────────────────────────────┐
                       │ FUNDAMENT — BRAMA KALKULATORA            │
                       │  (fundament/brama_kalkulatora.py)        │
                       │  jedyne miejsce liczenia (Prawo I)       │
                       │  81 wskaźników, każdy z hashem SHA-256   │
                       └────────────────┬────────────────────────┘
                                        ▼  wskazniki{}
                       ┌─────────────────────────────────────────┐
                       │ NAMIESTNIK — ustawia reżim sesji         │
                       │  tryb (SCALP/SWING/INVEST), prog,        │
                       │  lewar_cap, futures/spot, czy_grac?      │
                       └────────────────┬────────────────────────┘
                                        ▼
                       ┌─────────────────────────────────────────┐
                       │ klasyfikuj_rezim()                       │
                       │  VOLATILE→TREND→RANGING→[master-switch]  │
                       │  →NORMAL  (legatus.py)                   │
                       └────────────────┬────────────────────────┘
                                        ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │ LEGION — 48 aktywnych mikro-neuronów głosuje równolegle             │
   │  każdy: kierunek (LONG/SHORT/NEUTRAL) + pewnosc + pewnosc_przeciwnika│
   │  WAGI_REZIMU mnożą głosy wg reżimu (T×1.5 w trendzie, M×1.5 w range) │
   │  HedgeMWU — żywe wagi: neuron co kłamie → cichnie (biblioteki/)      │
   │  META-BRAMY Z-01..Z-04 (VPIN/pump/bubble/cascade) tłumią rój         │
   │    przez pewnosc_przeciwnika — kill-switche                          │
   └────────────────────────────────┬───────────────────────────────────┘
                                     ▼  raport agregatu (Legatus.fokus)
                       ┌─────────────────────────────────────────┐
                       │ DORADCY CEZARA (cesarz/doradcy/)         │
                       │  HERMES  — dane czyste?                  │
                       │  FULMEN  — reżim potwierdzony?           │
                       │  IUSTITIA— ryzyko OK? (BLOKUJE=veto)     │
                       │  ORACLE  — Sharpe setupu?                │
                       │  PYTHIA  — p(zysk) z historii?           │
                       │  RADA    — łączy 5 werdyktów             │
                       └────────────────┬────────────────────────┘
                                        ▼
                       ┌─────────────────────────────────────────┐
                       │ PRETORIANIE (pretorianie/)               │
                       │  Kalkulator lewara: vol-targeting,       │
                       │   volatility-drag, Kelly, lewar_cap      │
                       │  Bezpiecznik krzywej kapitału (HALT/RED) │
                       │  Bezpiecznik AOA (drawdown ≥30% = stop)  │
                       └────────────────┬────────────────────────┘
                                        ▼
                            DECYZJA CYKLU: WEJŚCIE / WSTRZYMANIE
                                        ▼
                       ┌─────────────────────────────────────────┐
                       │ DROGI (drogi/) → giełda MEXC (live/paper)│
                       │ ŚWIĄTYNIE (swiatynie/) → dashboard       │
                       └─────────────────────────────────────────┘
```

### 2.2. Bramki WSTRZYMANIA — kiedy rój NIE wchodzi (long/short)

To są realne progi z kodu (`dyrygent.py` + `legatus.py`). Rój wstrzymuje się, gdy
ZŁAMANA jest którakolwiek bramka — kolejność wykonania:

| # | Bramka | Warunek WEJŚCIA | Powód wstrzymania (kod) |
|---|---|---|---|
| 1 | **Namiestnik** | `czy_grac = True` | sesja wyłączona / poza reżimem gry |
| 2 | **Min. neuronów** | ≥ 5 aktywnych głosów | `Za mało aktywnych neuronów: N < 5` |
| 3 | **Kierunek roju** | LONG lub SHORT (nie NEUTRAL) | `rój neutralny — brak przewagi` |
| 4 | **Przewaga** | `pewnosc ≥ 0.55` (min_przewaga) | `Za słaba przewaga: X% < 55%` |
| 5 | **Próg Namiestnika** | `pewnosc ≥ prog_aktywny` | `pewność X < próg Y (Namiestnik)` |
| 6 | **Meta-bramy Z** | suma pewnosc_przeciwnika nie tłumi | Z-03 bubble / Z-04 cascade / Z-01 VPIN aktywne |
| 7 | **IUSTITIA** | ryzyko zaakceptowane | `IUSTITIA BLOKUJE` = veto ryzyka |
| 8 | **Pretorianie** | brak weta lewara | `weto Pretorianów: <powód>` |
| 9 | **Bezpiecznik krzywej** | stan ≠ HALT | equity-DD breaker: HALT blokuje wejścia |
| 10 | **Bezpiecznik AOA** | drawdown < 30% | `BEZPIECZNIK AOA PRZEPALONY` |

### 2.3. Symulacja LONG vs SHORT vs WSTRZYMANIE (przykłady)

**Przykład A — WEJŚCIE LONG:**
```
Reżim: TREND_STRONG (ADX 32). 48 neuronów: 31 LONG / 6 SHORT / 11 NEUTRAL.
Wagi T×1.5 wzmacniają trendowe. Agregat: LONG pewnosc=0.71 ≥ 0.55 ✅
Z-03 bubble_z=0.8 (spokój), Z-04 brak kaskady. Doradcy: czysto.
Pretorianie: lewar 4× (vol-target), drag OK. → WEJŚCIE LONG 4×.
```

**Przykład B — WSTRZYMANIE mimo sygnału (kill-switch):**
```
Reżim: VOLATILE. 48 neuronów: 28 LONG / 8 SHORT. Agregat LONG=0.68.
ALE Z-03 bubble_z=3.8 (>3.5 HARD-HALT) → pewnosc_przeciwnika=0.95.
Rój stłumiony do NEUTRAL. → WSTRZYMANIE „bańka — kill-switch Z-03".
```

**Przykład C — WSTRZYMANIE (za słaba przewaga):**
```
Reżim: RANGING. 48 neuronów: 19 LONG / 17 SHORT / 12 NEUTRAL.
Agregat: LONG pewnosc=0.52 < 0.55. → WSTRZYMANIE „za słaba przewaga".
Rój nie zgaduje przy braku konsensusu — to cecha, nie błąd.
```

**Przykład D — SHORT w krachu (Z-04 dead-cat):**
```
Reżim: PANIC. Kaskada 4 spadków. Z-04 CASCADE_FLAG=1 → zamyka longi, halt.
Po 3 barach bez kaskady: DEADCAT_SETUP=1 → Z-04 taktyczny LONG 0.60 (max 6 barów).
PSY-01 funding ekstremalny → SHORT 0.85 (jeśli adapter live).
```

---

## 3. 🛠️ MANUAL INSTALACJI NA LAPTOPIE (Windows 10 Pro, Fujitsu 8 GB)

### Krok 0 — Co przenosisz
Całe repozytorium ma **24 MB** (bez `.git`). To czysty Python — działa wszędzie.

### Krok 1 — Zainstaluj Pythona 3.11
- Pobierz: https://www.python.org/downloads/release/python-31115/
- Przy instalacji ZAZNACZ **„Add Python to PATH"**.
- Sprawdź w PowerShell: `python --version` → `Python 3.11.x`

### Krok 2 — Skopiuj repozytorium
**Opcja A (zalecana) — przez Git:**
```powershell
git clone <URL_repo> IMPERIAL-MESH-VORTEX
cd IMPERIAL-MESH-VORTEX
git checkout claude/sleepy-fermi-dsdE4
```
**Opcja B — pendrive/dysk:** skopiuj cały folder, pomiń `__pycache__` i `.git` jeśli brak miejsca.

### Krok 3 — Testy DZIAŁAJĄ BEZ instalacji zależności (Prawo I)
```powershell
python tests\run_tests.py        # powinno: 562/562 zielone
python narzedzia\audyt_spojnosci.py   # powinno: exit 0, pełna harmonia
```
> Runner testów nie wymaga numpy/TA-Lib — graceful fallback. To pierwszy dowód, że migracja się udała.

### Krok 4 — Pełna moc (opcjonalnie, gdy chcesz live)
```powershell
pip install -r requirements.txt
```
- **numpy, pandas** — instalują się czysto na 8 GB.
- **TA-Lib** — na Windows najłatwiej z gotowego wheela (pip install ta-lib lub wheel z unofficial binaries). Bez TA-Lib Brama używa czystego Pythona — system działa, tylko wolniej.
- **ccxt** — adaptery giełd (MEXC).
- **matplotlib** — dashboard.

### Krok 5 — Klucze API (NIGDY w kodzie — Prawo Bezpieczeństwa)
W PowerShell (trwale, `setx`):
```powershell
setx DEEPSEEK_API_KEY "twoj_klucz"
setx MEXC_API_KEY "twoj_klucz"
setx MEXC_SECRET "twoj_sekret"
```
> Po `setx` zamknij i otwórz nowy terminal. Klucze czytane przez `os.getenv(...)`.

### Krok 6 — DeepSeek (doradca AI) — gdy dokupisz RAM/podłączysz API
- Klient zgodny z OpenAI: `openai>=1.0`, `api_key=os.getenv("DEEPSEEK_API_KEY")`.
- 8 GB wystarczy do uruchomienia klienta API (DeepSeek liczy w chmurze, nie lokalnie).
- Lokalny LLM (gdyby kiedyś) wymagałby dużo więcej RAM — API to właściwa droga na Fujitsu.

### Krok 7 — Claude Code na Windows (gdy chcesz mnie lokalnie)
- Claude Code działa jako CLI w terminalu + rozszerzenia VS Code / JetBrains.
- Na Windows 10 Pro: przez terminal (PowerShell/WSL). Hook `SessionStart` uruchomi audyt automatycznie.

### Mapa pamięci RAM (8 GB → +8 GB)
| Zadanie | RAM | Na 8 GB? |
|---|---|---|
| Testy + audyt | < 0.5 GB | ✅ z zapasem |
| Backtest OHLCV (CSV) | ~1–2 GB | ✅ |
| Live z adapterami + dashboard | ~2–3 GB | ✅ |
| DeepSeek API (klient) | < 0.5 GB | ✅ (liczy chmura) |
| Po dokupieniu 16 GB | — | komfort + większe backtesty równolegle |

---

## 4. 💰 ŚCIEŻKA PIENIĘDZY — jak kapitał płynie przez Imperium

Liczby z realnego kodu (`pretorianie/kalkulator_lewara.py`).

### 4.1. Matematyka rozmiaru pozycji (krok po kroku)

Założenie: kapitał 10 000 USDT, BTCUSDT LONG, vol_realized=80% rocznie.

```
Krok 1 — Baza ryzyka (stały parametr: 2% kapitału na transakcję)
   ryzyko_usdt = 10 000 × 0.02 = 200 USDT

Krok 2 — Stop-loss (domyślnie ATR × multiplikator → np. stop = 1.5%)
   rozmiar_bazowy = ryzyko_usdt / stop_pct = 200 / 0.015 = 13 333 USDT

Krok 3 — Volatility Targeting (W-059: skala = vol_target / vol_realized)
   vol_target = 40% (domyślny cel)
   skala_vol  = 0.40 / 0.80 = 0.50   (clamped do [0.25, 4.0])
   rozmiar    = 13 333 × 0.50 = 6 667 USDT

Krok 4 — Lewar cap (Namiestnik: lewar_cap np. 5×)
   max_pozycja = 10 000 × 5 = 50 000 USDT  →  6 667 < 50 000 ✅

Krok 5 — Bezpiecznik krzywej (W-062)
   NORMAL → frakcja = 1.0  → 6 667 × 1.0 = 6 667 USDT
   REDUCED → frakcja = 0.5 → 6 667 × 0.5 = 3 334 USDT
   HALT    → frakcja = 0.0 → 0 USDT (blokada)

Krok 6 — Frakcja DD (W-063, ciągła, nie skokowa)
   DD = 10% → frakcja_dd ≈ 0.75 → 6 667 × 0.75 = 5 000 USDT

Krok 7 — Volatility Drag (W-130, Sinclair)
   drag = ½ × lewar × (lewar−1) × vol² = ½×4×3×0.64 = 3.84% / rok
   gdy drag > 20%/rok → WETO kalkulator (veto_lewar)

   WYNIK KOŃCOWY: 5 000 USDT pozycji (ok. 0.05 BTC przy cenie 100 000)
```

### 4.2. Diagram ścieżki pieniędzy

```
  KAPITAŁ: 10 000 USDT (equity curve śledzona przez Pretorianów)
       │
       ▼
  ┌────────────────────────────────────────────────────────┐
  │ 1. ryzyko = 2% kapitału = 200 USDT (na transakcję)    │
  └────────────────────┬───────────────────────────────────┘
                       │
                       ▼
  ┌────────────────────────────────────────────────────────┐
  │ 2. rozmiar = ryzyko / stop% (ATR-based)               │
  │    → BRUTTO: 13 333 USDT (lewar nominalny ~1.33×)     │
  └────────────────────┬───────────────────────────────────┘
                       │
              ×0.50 (vol zbyt wysoka?)
                       ▼
  ┌────────────────────────────────────────────────────────┐
  │ 3. Vol-targeting skaluje w dół / w górę               │
  │    niska vol → rozmiar rośnie (max ×4); wysoka → maleje│
  │    → 6 667 USDT                                       │
  └────────────────────┬───────────────────────────────────┘
                       │
              ×0.75 (DD = 10%)
                       ▼
  ┌────────────────────────────────────────────────────────┐
  │ 4. Frakcja DD (ciągła) + Bezpiecznik krzywej          │
  │    DD 0–10% → normalna gra; 10–20% → przycina;        │
  │    ≥20% HALT — zero nowych wejść                      │
  │    → 5 000 USDT                                       │
  └────────────────────┬───────────────────────────────────┘
                       │
              lewar_cap check?
                       ▼
  ┌────────────────────────────────────────────────────────┐
  │ 5. Lewar cap (Namiestnik: np. 5×) = max 50 000 USDT  │
  │    5 000 < 50 000 → OK (bez przycinania)              │
  │    drag > 20%/rok → WETO (nie wchodzisz)             │
  │    → PLAN POZYCJI: 5 000 USDT, lewar 0.5×, stop 1.5% │
  └────────────────────┬───────────────────────────────────┘
                       │
                       ▼
           ZLECENIE → giełda MEXC (drogi/)
```

---

## 5. ⏱️ TIMELINE JEDNEJ TRANSAKCJI (od sygnału do zamknięcia)

Każda transakcja żyje przez te fazy. Czasy orientacyjne dla interwału 1H:

```
T=0  SYGNAŁ
     Świeca 1H zamknięta → akwedukty dostarczają OHLCV + dane adapterów
     → Brama liczy 81 wskaźników (SHA-256 hash na każdy — audit trail)
     → Namiestnik: tryb SWING, reżim TREND_STRONG
     → 48 neuronów głosuje: 29L/7S/12N, pewnosc=0.68 ≥ 0.55 ✅
     → Z-03/Z-04/Z-01: brak kill-switch ✅
     → RADA: czysto (Hermes OK, Fulmen OK, Iustitia OK, Oracle OK, Pythia p=0.63)
     → Kalkulator: 5 000 USDT pozycji, stop 1.5%, lewar 0.5×

T=0  WEJŚCIE LONG (ccxt → MEXC)
     Pamięć Absolutna zapisuje: symbol, cena_wejscia, rozmiar, pewnosc,
     reżim, wskaźniki (snapshot), odcisk_palca (fingerprint)

T+1H..T+nH  MONITORING (każda świeca)
     Rój głosuje na nowo — sygnał może odwrócić kierunek
     IUSTITIA sprawdza ryzyko portfela w każdym cyklu
     MAE (Maximum Adverse Excursion) — najgorszy punkt świecy rejestrowany
     MFE (Maximum Favorable Excursion) — najlepszy punkt świecy rejestrowany
     Bezpiecznik krzywej śledzi equity — gdy DD rośnie, frakcja maleje

─── SCENARIUSZ A: zysk ─────────────────────────────────────────────
T+6H  WYJŚCIE (take-profit lub odwrócenie sygnału)
      Rój: SHORT 0.71 → Legatus → WYJŚCIE + nowy kierunek?
      Pamięć Absolutna zapisuje: MAE, MFE, P&L, czas trwania
      HedgeMWU aktualizuje wagi: neurony które głosowały poprawnie → +waga
      PYTHIA dodaje fingerprint do historii → p(zysk) dla podobnych setupów rośnie

─── SCENARIUSZ B: stop ─────────────────────────────────────────────
T+2H  Cena spada 1.5% → STOP-LOSS uderza
      Strata: 5 000 × 0.015 = 75 USDT = 0.75% kapitału (✅ mieści się w 2% ryzyko)
      Pamięć Absolutna: P&L = −75, MAE = −1.5%
      HedgeMWU: neurony SHORT miały rację → +waga; LONG → −waga (mała korekta)
      Equity: 10 000 → 9 925 USDT (DD = 0.75% → bezpieczniki spokojne)

─── SCENARIUSZ C: breaker krzywej ─────────────────────────────────
T+8H  Po serii strat DD osiąga 18% → REDUCED (rozmiar ×0.5)
T+10H DD = 21% → HALT (zero nowych wejść)
      System żyje, audytuje, głosuje — ale NIE otwiera pozycji
      Wyjście z HALT: gdy DD spada poniżej 10% (histereza — nie migocze na granicy)
```

### Gdzie jest każda informacja po transakcji

| Dane | Gdzie zapisane | Do czego służy |
|---|---|---|
| MAE/MFE, P&L | `Pamięć Absolutna` | Walk-forward, replay sesji, PYTHIA |
| Wagi neuronów | `HedgeMWU` (w pamięci) | Które neurony kłamały → cichną |
| Fingerprint setupu | `PYTHIA.historia` | p(zysk) dla podobnych sytuacji w przyszłości |
| Hash wskaźników | `Brama (SHA-256)` | Audit trail — nie ma halucynacji w danych |
| Equity curve | `BezpiecznikKrzywej` | DD monitor — HALT gdy za źle |

---

## 6. 📍 GDZIE JESTEŚMY / DOKĄD IDZIEMY

- **55 neuronów** (48 aktywnych) · **17 strategii** · **6 doradców** · **562 testy** ✅
- Audyt 12-warstwowy pilnuje spójności automatycznie (W12 = żywotność głosu, Prawo XV).
- Następne kroki (Prawo XV, kolejność potencjału): on-chain (kat. O), Reguła 6% (BIB-015),
  BIB-007 de Prado (FFD/meta-labeling), master-switch Faza 2, skew-Kelly (BIB-018).

> Ten dokument jest brudnopisem-przewodnikiem. Po faktycznej migracji zaktualizuj
> „Stan na:" i dopisz wpis do `LOG_ZMIAN.md` (Prawo XVII/XXI).
