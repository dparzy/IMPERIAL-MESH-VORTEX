---
kategoria: DISCIPLINA
typ: zywy
wlasciciel: imperium/koloseum/backtest.py, imperium/koloseum/paper_trading.py, imperium/koloseum/petla_live.py, imperium/koloseum/walidacja.py
stan_na: 2026-07-17
powod_istnienia: "Jedyne miejsce z **kryteriami zaliczenia Etapu II** (Sharpe≥1.0, MaxDD<15%, DSR≥0.95, WR≥55% lub PF>1.5, ≥100 trades) i drabiną Etapów II→IIb→III→IV. Ta bramka „kiedy wolno przejść"
---
# 📋 PAPER TRADING MEXC — Instrukcja Krok po Kroku (Etap II)

> **Etap II Koloseum:** system przechodzi z backtestu (Etap I ✅) do symulacji live.
> Paper trading = prawdziwe dane MEXC, fałszywe pieniądze — bez ryzyka kapitału.
> **Cel Etapu II:** 30 dni × DSR≥0.95, Sharpe≥1.0, MaxDD<15% — dopiero wtedy Etap III (real).

---

## 📌 WYMAGANIA (przed uruchomieniem)

| Element | Wymaganie | Status |
|---------|-----------|--------|
| RAM | ≥16 GB | ✅ **15.88 GB** zmierzone (`imperium/oczy/censor_sprzetu.py`, klasa PEDES) |
| Python | 3.10+ z ta-lib | ✅ |
| Testy | wszystkie zielone (`python tests/run_tests.py`) | ✅ |
| Klucz API MEXC | read-only (spot/futures) | ⏳ do konfiguracji |
| Klucz API DeepSeek | opcjonalny (AI advisor) | ⏳ |

---

## 🔑 KROK 1 — Utwórz klucz API MEXC (read-only)

1. Zaloguj się na **mexc.com** → **Profil** → **API Management**
2. Kliknij **"Create API Key"**
3. Nadaj nazwę: `IMPERIAL_MESH_READ`
4. Uprawnienia: zaznacz tylko **"Read Only"** — NIE zaznaczaj Trade/Withdraw
5. Wpisz IP swojego laptopa (opcjonalne ale zalecane)
6. Skopiuj `API Key` i `Secret Key`

⚠️ **BEZPIECZEŃSTWO (Prawo CLAUDE.md):**
- KLUCZE NIGDY W KODZIE, NIGDY W CHACIE
- Ustaw jako zmienne środowiskowe (nie w pliku):

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("MEXC_API_KEY", "tutaj_twoj_klucz", "User")
[Environment]::SetEnvironmentVariable("MEXC_SECRET", "tutaj_twoj_secret", "User")
```

**Linux/Mac:**
```bash
echo 'export MEXC_API_KEY="tutaj_twoj_klucz"' >> ~/.bashrc
echo 'export MEXC_SECRET="tutaj_twoj_secret"' >> ~/.bashrc
source ~/.bashrc
```

**Weryfikacja:**
```bash
python -c "import os; print('OK' if os.getenv('MEXC_API_KEY') else 'BRAK')"
```

---

## 📡 KROK 2 — Połącz AdapterFeed z MEXC

Pakiet: `imperium/akwedukty/adaptery/` (nie pojedynczy plik — `futures.py`, `cvd.py`, `feargreed.py`, `news_llm.py` …)

Adaptery już napisane, czekają na klucze. Weryfikacja:

```bash
python -c "
import os
from imperium.akwedukty.adaptery.futures import AdapterFutures
from imperium.akwedukty.adaptery.feargreed import AdapterFearGreed
print('AdapterFutures:', AdapterFutures().pobierz('BTCUSDT'))
print('FearGreed:', AdapterFearGreed().pobierz('BTCUSDT'))
"
```

Jeśli zwraca dane (nie None dla wszystkiego) → adaptery żywe.

---

## 📊 KROK 3 — Pobierz dane live z MEXC

Dane live przez publiczne REST API (bez klucza):

```python
# Przykład pobierania barów OHLCV
import requests

def pobierz_bary_mexc(symbol: str, interwal: str = "1d", limit: int = 500) -> list:
    """
    Publiczne API MEXC — bez klucza API.
    interwal: "1m","5m","15m","30m","1h","4h","1d","1w"
    """
    url = "https://api.mexc.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interwal, "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    bary = []
    for b in r.json():
        bary.append({
            "timestamp": int(b[0]),
            "open": float(b[1]),
            "high": float(b[2]),
            "low": float(b[3]),
            "close": float(b[4]),
            "volume": float(b[5]),
            "symbol": symbol,
            "interwal": interwal.upper(),
        })
    return bary

# Test
bary = pobierz_bary_mexc("BTCUSDT", "1d", 300)
print(f"Pobrano {len(bary)} barów BTCUSDT 1D")
print(f"Ostatni bar: close={bary[-1]['close']:.0f}")
```

---

## 🤖 KROK 4 — Uruchom Paper Trading Loop

> **NAPRAWIONE 2026-07-17 (Prawo XIX: nic nie istnieje bez kodu).** Ten krok wklejał wcześniej
> ~80 linii źródła `narzedzia/paper_trading_live.py` — **pliku, który NIGDY nie istniał**.
> Instrukcja kazała uruchomić widmo. Realna pętla live istnieje i ma własne CLI:

```bash
python -m imperium.koloseum.petla_live --symbole BTCUSDT ETHUSDT SOLUSDT --interwal 4H --monitor
```

**Domyślnie PAPER** — żadnych realnych zleceń bez jawnej flagi `--real` (która dodatkowo
wymaga `MEXC_API_KEY`). Najważniejsze przełączniki (`--help` pokazuje pełną listę):

| Flaga | Co robi |
|---|---|
| `--symbole BTCUSDT ETHUSDT SOLUSDT` | pary do handlu (domyślne) |
| `--interwal 4H` | interwał świec (domyślnie `1H`; przy `1H` pętla czeka między świecami — **to normalne, nie zawieszenie**) |
| `--kapital 10000` | wirtualny kapitał startowy |
| `--monitor` | panel TUI co bar (Prawo XXIV — widoczność operacyjna) |
| `--dashboard` | Panel Kapitolu w przeglądarce → http://localhost:8777 |
| `--arena-log` | loguje realny PnL zamknięć do areny (`arena_wyniki.db`) — **potrzebne do rozliczenia Etapu II** |
| `--real` | 🚨 REALNE zlecenia MEXC — wyłącznie decyzja Cezara |

Zatrzymanie: `Ctrl+C`. Prostszy start bez zapamiętywania flag: `python skrypty/start.py`.

## 📈 KROK 5 — Monitoruj wyniki (Etap II)

```bash
# Sprawdź krzywe equity i metryki po 30 dniach
python -c "
from imperium.koloseum.backtest import backtest_portfel, wagi_inwerse_vol
from imperium.koloseum.walidacja import deflated_sharpe, etap_pierwszy_koloseum
import json

# Załaduj dane z pliku logów lub ponownie przelicz
# ...
print('Etap II wymaga 30 dni danych live')
"
```

### Kryteria zaliczenia Etapu II (30 dni paper trading):

| Metryka | Próg | Znaczenie |
|---------|------|-----------|
| **Sharpe roczny** | ≥ 1.0 | edge rzeczywisty, nie szum |
| **MaxDD** | < 15% | bezpiecznik portfela trzyma |
| **DSR** | ≥ 0.95 | edge nie jest overfitted |
| **Win Rate** | ≥ 55% LUB PF > 1.5 | przewaga statystyczna |
| **Trades** | ≥ 100 | wystarczająco dużo próbek |

Zaliczenie → dopiero wtedy Etap III (real money, mały kapitał).

---

## 🚦 KROKI DALSZE

| Krok | Opis | Wymaga |
|------|------|--------|
| **Etap II** | Paper trading 30 dni | RAM 16GB, API klucze |
| **Etap IIb** | Aktualizacja wag (MWU online) | Etap II zaliczony |
| **Etap III** | Real trading, 100-500 USD | Etap II ≥ 30 dni ✅ |
| **Etap IV** | Skalowanie + DeepSeek advisor | Etap III ≥ 3 miesiące |

---

## ⚠️ PRZYPOMNIENIE BEZPIECZEŃSTWA

```
KLUCZE API NIGDY W KODZIE, NIGDY W CHACIE — tylko zmienne środowiskowe.
DeepSeek: api_key=os.getenv("DEEPSEEK_API_KEY")
MEXC:     os.getenv("MEXC_API_KEY"), os.getenv("MEXC_SECRET")
```

Read-only klucz = MEXC nie może wykonać żadnej transakcji nawet jeśli system jest zhakowany.
Paper trading = zero ryzyka finansowego nawet przy błędach logiki.

---

> 👑 *"Nie spiesz się. Etap II to trening przed prawdziwą bitwą."*
> 📊 *"30 dni papierowych = 30 dni pewności, że system działa tak jak w backteście."*
