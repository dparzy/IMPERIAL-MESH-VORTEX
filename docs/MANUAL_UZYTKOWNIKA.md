---
kategoria: DISCIPLINA
typ: zywy
wlasciciel: imperium/akwedukty/bary_zdarzeniowe.py, imperium/koloseum/petla_live.py, imperium/legiony/feature_importance.py, imperium/legiony/meta_labeling.py, imperium/legiony/triple_barrier.py, narzedzia/audyt_spojnosci.py, tests/run_tests.py
stan_na: 2026-07-18
powod_istnienia: "Jedyny kompletny przewodnik „od zera do paper tradingu' dla nowicjusza — instalacja Python/TA-Lib, tryby PAPER/DRY-RUN/REAL, pełna tabela pól `KonfigPetliLive`, TradingView+ngrok k"
---
# 📖 MANUAL IMPERIUM — Pełna Instrukcja dla Nowicjusza

> **Stan na:** 2026-07-18
> Wszystko krok po kroku, na laptopie, dla osoby która nigdy tego nie robiła.
> Jak coś nie działa — szukaj sekcji „❓ Problemy" na końcu.

---

## SPIS TREŚCI

1. [Co to w ogóle jest](#1-co-to-jest)
2. [Instalacja od zera (Windows / Mac / Linux)](#2-instalacja)
3. [Pierwsze uruchomienie — test że działa](#3-pierwsze-uruchomienie)
4. [Tryby działania — wszystkie opcje](#4-tryby)
5. [Panel webowy + wykres na żywo](#5-panel)
6. [TradingView krok po kroku](#6-tradingview)
7. [Wszystkie opcje konfiguracji (KonfigPetliLive)](#7-konfiguracja)
8. [Wszystkie komendy](#8-komendy)
9. [Klucze API (bezpieczeństwo)](#9-klucze)
10. [Narzędzia analityczne (AFML W-355..W-359)](#10-afml)
11. [Problemy i rozwiązania](#11-problemy)

---

## 1. CO TO JEST <a name="1-co-to-jest"></a>

Imperium to system tradingowy oparty na **roju <!-- LICZBA:neurony -->87<!-- /LICZBA --> neuronów** — każdy neuron to
osobny „doradca" patrzący na inny aspekt rynku (RSI, wolumen, trend, psychologia,
on-chain...). Legatus zbiera ich głosy i podejmuje decyzję LONG / SHORT / NEUTRAL.

**Trzy tryby pracy:**
- **PAPER** (domyślny) — symulacja, ZERO prawdziwych pieniędzy. Tu zaczynasz.
- **DRY-RUN** — prawdziwy klucz giełdy, ale zlecenia tylko logowane (nie wysyłane).
- **REAL** — prawdziwe zlecenia na giełdzie MEXC (dopiero gdy wszystko sprawdzone).

**Zasada nadrzędna:** zaczynasz ZAWSZE od paper. Nigdy nie idź na real bez tygodni
testów na paper.

---

## 2. INSTALACJA <a name="2-instalacja"></a>

> **Masz już Pythona 3.11+, git i TA-Lib?** Przejdź od razu do kroku 2.3 →

### Krok 2.1 — Zainstaluj Pythona (pomiń jeśli masz już 3.11+)

Imperium działa na **Pythonie 3.11+**.

**Windows:**
1. Wejdź na https://www.python.org/downloads/
2. Pobierz „Python 3.12" (duży żółty przycisk)
3. Uruchom instalator → **WAŻNE: zaznacz ptaszek „Add Python to PATH"** (na dole!)
4. Kliknij „Install Now"

**Mac:**
```bash
# Jeśli masz Homebrew:
brew install python@3.12
# Jeśli nie masz Homebrew — pobierz z python.org jak Windows
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git
```

### Krok 2.2 — Sprawdź że Python działa (pomiń jeśli już masz)

Otwórz terminal (Windows: wpisz „cmd" w menu Start; Mac: „Terminal"):
```bash
python --version
```
Powinno pokazać `Python 3.11.x` lub nowszy. Jeśli błąd — Python nie jest w PATH
(Windows: odinstaluj i zainstaluj ponownie z ptaszkiem „Add to PATH").

### Krok 2.3 — Pobierz Imperium

```bash
git clone https://github.com/dparzy/imperial-mesh-vortex.git
cd imperial-mesh-vortex
```

Jeśli już masz sklonowane — zaktualizuj:
```bash
cd imperial-mesh-vortex
git pull origin main
```

### Krok 2.4 — Stwórz środowisko wirtualne (zalecane)

To izoluje pakiety Imperium od reszty systemu:
```bash
# Windows:
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

Po aktywacji w terminalu zobaczysz `(.venv)` na początku linii. To znaczy że działa.

### Krok 2.5 — Zainstaluj zależności

```bash
pip install -r requirements.txt
```

To instaluje: numpy, pandas, ccxt (giełdy), matplotlib (wykresy),
openai (doradca AI), ruff (kontrola jakości).

> ⚠️ **TA-Lib** — jeśli masz już zainstalowaną (np. z poprzedniej sesji), `pip install`
> ją wykryje i pominie. Jeśli pojawi się błąd:
> - Windows: pobierz gotowy plik `.whl` z https://github.com/cgohlke/talib-build/releases
>   i zainstaluj: `pip install ta_lib‑0.6.0‑cp312‑cp312‑win_amd64.whl`
> - Mac: `brew install ta-lib` PRZED `pip install`
> - Linux: `sudo apt install ta-lib` lub kompilacja ze źródeł
>
> **WAŻNE:** Imperium działa BEZ TA-Lib (graceful fallback — czysty Python).
> Testy przejdą nawet bez niej. TA-Lib tylko przyspiesza i daje pełną precyzję.

---

## 3. PIERWSZE URUCHOMIENIE — TEST ŻE DZIAŁA <a name="3-pierwsze-uruchomienie"></a>

### Krok 3.1 — Uruchom testy

```bash
python tests/run_tests.py
```
Powinno pokazać na końcu: `✅ Wszystkie testy zaliczone — Imperium gotowe.`
(liczbę testów podaje sam runner — nie hardkodujemy jej tu, by się nie przeterminowała).
Jeśli tak — wszystko działa.

### Krok 3.2 — Sprawdź spójność systemu

```bash
python narzedzia/audyt_spojnosci.py
```
Powinno pokazać: `🔬 AUDYT SPÓJNOŚCI (Prawo XXI) — ✅ pełna harmonia`.

Te dwie komendy to Twój „test zdrowia" — uruchamiaj je zawsze gdy coś zmienisz.

---

## 4. TRYBY DZIAŁANIA — WSZYSTKIE OPCJE <a name="4-tryby"></a>

Imperium uruchamia się przez napisanie krótkiego skryptu Pythona. Stwórz plik
`start.py` w głównym folderze i wklej jeden z poniższych przykładów.

### 4.1 — PAPER TRADING (tu zaczynasz)

```python
# start.py — symulacja, zero prawdziwych pieniędzy
from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live

cfg = KonfigPetliLive(
    symbole=["BTCUSDT", "ETHUSDT"],   # pary które śledzisz
    interwal="1H",                     # świece godzinne
    kapital_startowy=10_000.0,         # wirtualne 10k USDT
    paper=True,                        # SYMULACJA
    dashboard=True,                    # panel webowy
)
handluj_live(cfg)
```

Uruchom:
```bash
python start.py
```
Zatrzymanie: **Ctrl+C**.

**Szybciej — bez pisania skryptu (CLI):** ten sam bieg paper z podglądem live jednym poleceniem:
```bash
python -m imperium.koloseum.petla_live --dashboard --monitor --arena-log
```
Podgląd w przeglądarce: **http://127.0.0.1:8777** (port zmienisz `--dashboard-port 9001`).
Flagi obserwacji/pomiaru: `--monitor` panel TUI w terminalu · `--arena-log` mierzy realny PnL
zamknięć do areny · `--cienie` kontrfaktyczny pomiar Legionów Cieni · `--sl-atr-mult 2.0`
realistyczny stop = 2×ATR (zamiast crude stopu z dźwigni).
Flagi zachowania (opt-in OFF): `--senat` Debata Senatu · `--kalibruj-prog` bramka konformalna ·
`--filtr-asymetrii` weto reżimu · `--ksiega-wad` filtr wad setupu · `--funding-mexc` funding MEXC ·
`--mwu` / `--igrzyska` warstwy uczenia · `--min-pewnosc 0.6` próg wejścia.
Test/tempo: `--max-barow 3 --pauza 2`. Pełna lista: `python -m imperium.koloseum.petla_live --help`.

### 4.2 — BACKTEST (test na danych historycznych)

```python
# backtest_test.py
from imperium.koloseum.backtest import backtest
# (backtest wymaga danych historycznych — patrz docs/ po szczegóły API)
```

### 4.3 — DRY-RUN (prawdziwy klucz, fałszywe zlecenia)

```python
cfg = KonfigPetliLive(
    symbole=["BTCUSDT"],
    paper=False,        # używa prawdziwego klucza giełdy
    dry_run=True,       # ale zleceń NIE wysyła, tylko loguje
)
```
Wymaga kluczy MEXC w zmiennych środowiskowych (sekcja 9).

### 4.4 — REAL (prawdziwe zlecenia — UWAGA!)

```python
cfg = KonfigPetliLive(
    symbole=["BTCUSDT"],
    paper=False,
    dry_run=False,      # PRAWDZIWE ZLECENIA NA GIEŁDZIE
    kapital_startowy=100.0,   # zacznij od MAŁEJ kwoty
)
```
> 🚨 **NIE uruchamiaj tego dopóki nie przetestowałeś tygodniami na paper.**

---

## 5. PANEL WEBOWY + WYKRES NA ŻYWO <a name="5-panel"></a>

Gdy ustawisz `dashboard=True`, po uruchomieniu otwórz w przeglądarce:

```
http://localhost:8777
```

Zobaczysz:
- **Wykres świecowy** (gdy podłączysz TradingView — sekcja 6)
- **Kapitał i zysk sesji**
- **Otwarte pozycje** (LONG/SHORT, P&L)
- **Czołowe neurony** — które głosy są najsilniejsze
- **Selector pary i interwału** — przełączasz na żywo
- **Status webhooka** — ile alertów przyszło

Panel odświeża się sam co 2 sekundy. Zmiana portu:
```python
cfg = KonfigPetliLive(..., dashboard=True, dashboard_port=9000)
```

---

## 6. TRADINGVIEW KROK PO KROKU <a name="6-tradingview"></a>

TradingView wysyła Ci sygnały (alerty) z wykresu prosto do roju. Potrzebujesz tunelu,
bo TradingView jest w internecie a Imperium na Twoim laptopie.

### Krok 6.1 — Włącz webhook w Imperium

```python
# start_tv.py
from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live

cfg = KonfigPetliLive(
    symbole=["BTCUSDT"],
    paper=True,
    dashboard=True,      # MUSI być True
    webhook_tv=True,     # włącza odbiornik TradingView
)
handluj_live(cfg)
```
Uruchom: `python start_tv.py`. W logach zobaczysz:
```
[PętlaLive] W-354 Webhook TV aktywny → POST /webhook/tv
```

### Krok 6.2 — Ustaw hasło webhooka (bezpieczeństwo)

**Windows (cmd):**
```cmd
setx WEBHOOK_TV_SEKRET "mojeTajneHaslo123"
```
Potem **zamknij i otwórz terminal na nowo** (setx działa od nowego terminala).

**Mac/Linux:**
```bash
export WEBHOOK_TV_SEKRET="mojeTajneHaslo123"
```
Żeby było trwałe — dodaj tę linię do pliku `~/.bashrc` (Linux) lub `~/.zshrc` (Mac).

### Krok 6.3 — Zainstaluj ngrok (tunel do internetu)

1. Wejdź na https://ngrok.com → zarejestruj się (darmowe)
2. Pobierz ngrok dla swojego systemu
3. Skopiuj swój **Authtoken** z panelu ngrok
4. W terminalu:
```bash
ngrok config add-authtoken WKLEJ_TWOJ_TOKEN
```

### Krok 6.4 — Uruchom tunel (drugi terminal)

Zostaw `python start_tv.py` działające, otwórz **DRUGI terminal**:
```bash
ngrok http 8777
```
ngrok pokaże:
```
Forwarding   https://abc123xyz.ngrok-free.app -> http://localhost:8777
```
**Skopiuj ten adres `https://abc...ngrok-free.app`** — potrzebny w TradingView.

### Krok 6.5 — Skonfiguruj alert w TradingView

1. Wejdź na https://tradingview.com → otwórz wykres pary (np. BTCUSDT)
2. Kliknij ikonę **budzika (Alert)** → **Create Alert**
3. W zakładce **Notifications** zaznacz **Webhook URL** i wklej:
   ```
   https://abc123xyz.ngrok-free.app/webhook/tv
   ```
   (Twój adres z ngrok + `/webhook/tv` na końcu!)
4. W polu **Message** wklej (podmień `mojeTajneHaslo123` na swoje hasło z 6.2):
   ```json
   {
     "symbol": "{{ticker}}",
     "interwal": "{{interval}}",
     "akcja": "NEUTRAL",
     "cena": {{close}},
     "czas": "{{timenow}}",
     "open": {{open}},
     "high": {{high}},
     "low": {{low}},
     "close": {{close}},
     "volume": {{volume}},
     "sekret": "mojeTajneHaslo123"
   }
   ```
5. Kliknij **Create**

> Gotowy szablon znajdziesz też w panelu na `http://localhost:8777` — rozwiń sekcję
> „📡 Konfiguracja TradingView Webhook".

### Krok 6.6 — Sprawdź że działa

**Test ręczny** (bez czekania na świecę) — w trzecim terminalu:
```bash
curl -X POST http://localhost:8777/webhook/tv -H "Content-Type: application/json" -d "{\"symbol\":\"BTCUSDT\",\"akcja\":\"NEUTRAL\",\"cena\":67500,\"close\":67500,\"high\":68000,\"low\":67000,\"open\":67200,\"volume\":1234,\"sekret\":\"mojeTajneHaslo123\",\"czas\":\"2026-06-20T12:00:00Z\"}"
```
Jeśli wróci `{"ok": true, ...}` — działa! W panelu zobaczysz licznik `webhook: 1 alertów`.

### Krok 6.7 — Sygnały BUY/SELL z własnej strategii (zaawansowane)

Jeśli masz strategię w Pine Script i chcesz wysyłać LONG/SHORT zamiast samych barów:
zamień `"akcja": "NEUTRAL"` na `"akcja": "BUY"` lub `"akcja": "SELL"` w odpowiednim
alercie, albo użyj `alert()` w kodzie Pine. Imperium rozumie aliasy:
`buy/long/1` → LONG, `sell/short/-1` → SHORT, `neutral/hold/0` → NEUTRAL.

---

## 7. WSZYSTKIE OPCJE KONFIGURACJI <a name="7-konfiguracja"></a>

Pełna lista pól `KonfigPetliLive` (wszystko opcjonalne poza `symbole`):

| Opcja | Domyślnie | Co robi |
|---|---|---|
| `symbole` | (wymagane) | Lista par, np. `["BTCUSDT", "ETHUSDT"]` |
| `interwal` | `"1H"` | Interwał świec: `1m,3m,5m,15m,30m,1H,2H,4H,6H,1D` |
| `limit_barow` | `400` | Ile świec historii pobierać |
| `kapital_startowy` | `10_000.0` | Kapitał (wirtualny w paper) |
| `min_pewnosc` | `0.55` | Próg pewności do wejścia (0-1) |
| `paper` | `True` | True=symulacja, False=prawdziwe zlecenia |
| `dry_run` | `False` | paper=False+dry_run=True → real klucz, fałszywe zlecenia |
| `auto_rezim` | `True` | Auto-klasyfikacja reżimu rynku |
| `synapsy` | `True` | Pamięć reżimowa per para |
| `mwu` | `False` | Online uczenie wag neuronów (HedgeMWU) |
| `igrzyska` | `False` | Ranking neuronów po accuracy |
| `ksiega_wad` | `False` | Filtr wad setupu z poprzednich lekcji |
| `filtr_asymetrii` | `False` | Weto na rynku bocznym i kontr-trendzie |
| `auto_discover` | `False` | Auto-dobór par z giełdy (płynność×dekorelacja) |
| `auto_discover_top_n` | `5` | Ile par wybrać przy auto_discover |
| `monitor` | `False` | Panel TUI w terminalu |
| `dashboard` | `False` | Panel webowy HTTP |
| `dashboard_port` | `8777` | Port panelu webowego |
| `webhook_tv` | `False` | Odbiornik TradingView (wymaga dashboard=True) |
| `telegram` | `False` | Alerty Telegram (wymaga kluczy w env) |
| `senat` | `False` | Dodatkowa weryfikacja kierunku (Senat Debaty) |

### Przykład „wszystko włączone" (pełna moc uczenia):

```python
cfg = KonfigPetliLive(
    symbole=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    interwal="4H",
    kapital_startowy=10_000.0,
    paper=True,
    synapsy=True,        # pamięć reżimowa
    mwu=True,            # online uczenie wag
    igrzyska=True,       # ranking neuronów
    ksiega_wad=True,     # filtr wad
    filtr_asymetrii=True,
    dashboard=True,      # panel webowy
    webhook_tv=True,     # TradingView
    monitor=True,        # panel TUI
)
handluj_live(cfg)
```

---

## 8. WSZYSTKIE KOMENDY <a name="8-komendy"></a>

| Komenda | Co robi |
|---|---|
| `python tests/run_tests.py` | Uruchom wszystkie testy (sprawdź zdrowie systemu) |
| `python narzedzia/audyt_spojnosci.py` | Sprawdź spójność kodu z dokumentacją |
| `python start.py` | Uruchom swój skrypt tradingowy (paper/live) |
| `python -m ruff check imperium/` | Sprawdź jakość kodu (linter) |
| `git pull origin claude/sleepy-fermi-dsdE4` | Pobierz najnowszy kod |
| `git status` | Zobacz co się zmieniło |
| `ngrok http 8777` | Uruchom tunel do TradingView |
| `Ctrl+C` | Zatrzymaj działającą pętlę |

### Szybki podgląd stanu roju (ile neuronów, kategorie):
```bash
python -c "from imperium.legiony.rejestr import wszystkie_neurony, raport_elity; n=wszystkie_neurony(); print(f'Neurony: {len(n)} | Elitarne: {raport_elity()[\"lacznie_elite\"]}')"
```

---

## 9. KLUCZE API — BEZPIECZEŃSTWO <a name="9-klucze"></a>

> 🔐 **ŻELAZNA ZASADA: klucze API NIGDY w kodzie, NIGDY w czacie. Tylko zmienne środowiskowe.**

Klucze potrzebne TYLKO gdy idziesz na dry-run/real lub chcesz doradcę AI/Telegram.
Na paper trading **nie potrzebujesz żadnych kluczy**.

| Zmienna | Do czego | Gdzie zdobyć |
|---|---|---|
| `MEXC_API_KEY` | Giełda MEXC (real) | mexc.com → API Management |
| `MEXC_SECRET` | Giełda MEXC (real) | tam samo |
| `DEEPSEEK_API_KEY` | Doradca AI | platform.deepseek.com |
| `TELEGRAM_BOT_TOKEN` | Alerty Telegram | @BotFather na Telegramie |
| `TELEGRAM_CHAT_ID` | Alerty Telegram | Twoje ID chatu |
| `WEBHOOK_TV_SEKRET` | Hasło webhooka TradingView | wymyślasz sam |

**Jak ustawić (Windows):**
```cmd
setx MEXC_API_KEY "twoj_klucz"
setx MEXC_SECRET "twoj_sekret"
```
Po `setx` **zamknij i otwórz terminal na nowo**.

**Jak ustawić (Mac/Linux):**
```bash
export MEXC_API_KEY="twoj_klucz"
export MEXC_SECRET="twoj_sekret"
# trwale: dodaj do ~/.bashrc lub ~/.zshrc
```

---

## 10. NARZĘDZIA ANALITYCZNE (AFML W-355..W-359) <a name="10-afml"></a>

Najnowsze moduły z książki López de Prado „Advances in Financial Machine Learning".

### 10.1 — Które neurony faktycznie działają (Feature Importance)

```python
from imperium.legiony.feature_importance import raport_waznosci

# historia_sygnalow: lista snapów [{klucz_neuronu: "LONG"/"SHORT"/"NEUTRAL"}, ...]
# historia_wynikow:  [+1, -1, +1, ...] (+1=cena wzrosła, -1=spadła następny bar)
raport = raport_waznosci(historia_sygnalow, historia_wynikow)
print(raport)                  # tabela z rankingiem MDA + SFI
print(raport.martwe_glosy)     # neurony do wyciszenia
print(raport.redundantne)      # kandydaci do scalenia
```

### 10.2 — Bary dolarowe (lepsze niż czasowe)

```python
from imperium.akwedukty.bary_zdarzeniowe import dollar_bars

# Z danych OHLCV (aproksymacja):
bary = dollar_bars(lista_ohlcv, prog_dolarow=10_000_000)  # bar co 10M USDT
```

### 10.3 — Triple-Barrier (etykietowanie z dynamiczną zmiennością)

```python
from imperium.legiony.triple_barrier import filtr_cusum, triple_barrier

zdarzenia = filtr_cusum(close, h=0.01)          # sampler zdarzeń (1% odchył)
bariery = triple_barrier(close, zdarzenia,
                         k_tp=2.0, k_sl=1.0,     # take-profit 2σ, stop-loss 1σ
                         max_hold=20)             # max 20 barów
```

### 10.4 — Bet sizing López de Prado

```python
from imperium.legiony.meta_labeling import bet_size_ldp

m = bet_size_ldp(p=0.72, dyskretyzacja=0.05)   # wielkość pozycji z prawdopodobieństwa
```

---

## 11. PROBLEMY I ROZWIĄZANIA <a name="11-problemy"></a>

| Problem | Rozwiązanie |
|---|---|
| `python: command not found` | Python nie w PATH. Windows: reinstaluj z ptaszkiem „Add to PATH". Mac/Linux: użyj `python3` |
| `pip install` wywala się na TA-Lib | Pomiń ją — Imperium działa bez. Albo zainstaluj gotowy `.whl` (sekcja 2.5) |
| `ModuleNotFoundError: imperium` | Uruchamiasz z głównego folderu? `cd imperial-mesh-vortex` najpierw |
| Panel nie otwiera się | Sprawdź czy `dashboard=True`; otwórz `http://localhost:8777` (nie https) |
| TradingView: „Webhook error" | Sprawdź czy `python start_tv.py` i `ngrok` nadal działają |
| Webhook: `{"ok": false}` | Hasło `sekret` w TradingView ≠ `WEBHOOK_TV_SEKRET`. Sprawdź czy się zgadzają |
| ngrok URL wygasł | Restart `ngrok http 8777`, zaktualizuj URL w alercie TradingView |
| Wykres pusty | Poczekaj na zamknięcie świecy w TV, lub zrób test curl (6.6) |
| Brak danych w paper | Brak internetu/loadera. Sprawdź połączenie; loader pobiera OHLCV z giełdy |
| Testy czerwone po `git pull` | `pip install -r requirements.txt` (mogły dojść nowe pakiety) |

### Złota reguła debugowania
Gdy coś nie działa:
1. `python tests/run_tests.py` — czy system w ogóle zdrowy?
2. Czytaj logi w terminalu — Imperium pisze co robi
3. Zacznij od najprostszej konfiguracji (sam `symbole` + `paper=True`), dodawaj opcje po jednej

---

## 🎯 ŚCIEŻKA DLA POCZĄTKUJĄCEGO (kolejność)

```
1. Zainstaluj Python + Imperium (sekcja 2)
2. python tests/run_tests.py → wszystko zielone
3. start.py z paper=True, dashboard=True → patrz na panel
4. Obserwuj tydzień, ucz się czytać decyzje roju
5. Podłącz TradingView (sekcja 6) → sygnały na żywo
6. Włącz uczenie: mwu=True, igrzyska=True, synapsy=True
7. Po wielu tygodniach paper → dopiero dry_run
8. Real TYLKO z małym kapitałem i pełnym zrozumieniem
```

**Nie spiesz się. Paper trading jest darmowy i bezpieczny — zostań tam długo.**
