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

## 4. 📍 GDZIE JESTEŚMY / DOKĄD IDZIEMY

- **55 neuronów** (48 aktywnych) · **17 strategii** · **6 doradców** · **562 testy** ✅
- Audyt 12-warstwowy pilnuje spójności automatycznie (W12 = żywotność głosu, Prawo XV).
- Następne kroki (Prawo XV, kolejność potencjału): on-chain (kat. O), Reguła 6% (BIB-015),
  BIB-007 de Prado (FFD/meta-labeling), master-switch Faza 2, skew-Kelly (BIB-018).

> Ten dokument jest brudnopisem-przewodnikiem. Po faktycznej migracji zaktualizuj
> „Stan na:" i dopisz wpis do `LOG_ZMIAN.md` (Prawo XVII/XXI).
