# 📋 PAPER TRADING MEXC — Instrukcja Krok po Kroku (Etap II)

> **Etap II Koloseum:** system przechodzi z backtestu (Etap I ✅) do symulacji live.
> Paper trading = prawdziwe dane MEXC, fałszywe pieniądze — bez ryzyka kapitału.
> **Cel Etapu II:** 30 dni × DSR≥0.95, Sharpe≥1.0, MaxDD<15% — dopiero wtedy Etap III (real).

---

## 📌 WYMAGANIA (przed uruchomieniem)

| Element | Wymaganie | Status |
|---------|-----------|--------|
| RAM | ≥16 GB | ⏳ upgrade laptopa |
| Python | 3.10+ z ta-lib | ✅ |
| Testy | 743/743 zielone | ✅ |
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

Plik: `imperium/akwedukty/adaptery.py`

Adaptery już napisane, czekają na klucze. Weryfikacja:

```bash
python -c "
import os
from imperium.akwedukty.adaptery import AdapterFutures, AdapterFearGreed
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

```python
"""
narzedzia/paper_trading_live.py — główna pętla paper trading.

Uruchomienie:
    python narzedzia/paper_trading_live.py

Zatrzymanie:
    Ctrl+C (gracja: zamknie pozycje po ostatniej cenie)
"""
import os
import sys
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/paper_trading.log"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("PaperLoop")

# ── Konfiguracja ──────────────────────────────────────────────────────────────
PARY = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]
INTERWAL = "1D"               # "4H" dla swing, "1D" dla invest
KAPITAL_STARTOWY = 10_000.0   # wirtualny USD
OKNO = 250                    # tyle barów do budowania wskaźników
PRZERWA_S = 3600              # sprawdzaj co godzinę (dla 1D: co 6h)

# ── Zbuduj system ─────────────────────────────────────────────────────────────
from imperium.koloseum.backtest import backtest_portfel, wagi_inwerse_vol
from imperium.koloseum.paper_trading import PaperTradingEngine

# Pobierz historię (warmup)
def pobierz_bary(symbol, interwal, limit=500):
    import requests
    url = "https://api.mexc.com/api/v3/klines"
    r = requests.get(url, params={"symbol": symbol, "interval": interwal.lower(), "limit": limit}, timeout=10)
    r.raise_for_status()
    return [{"timestamp": int(b[0]), "open": float(b[1]), "high": float(b[2]),
             "low": float(b[3]), "close": float(b[4]), "volume": float(b[5]),
             "symbol": symbol, "interwal": interwal} for b in r.json()]

log.info("Pobieranie danych warmup...")
bary_per = {sym: pobierz_bary(sym, INTERWAL, limit=OKNO + 50) for sym in PARY}

# Vol-adjusted weights (Opcja B)
wagi = wagi_inwerse_vol(bary_per, okno_vol=60)
log.info(f"Wagi portfela: {', '.join(f'{s}: {w:.1%}' for s,w in wagi.items())}")

# Uruchom backtest na historii → inicjalizuj PaperTradingEngine
eng = backtest_portfel({}, INTERWAL, kapital_startowy=KAPITAL_STARTOWY,
                       dd_control=True, bary_per=bary_per, wagi=wagi)
log.info(f"Warmup OK | Equity start: {eng.kapital_calkowity:.0f} USD")

# ── Pętla Live ────────────────────────────────────────────────────────────────
while True:
    try:
        log.info("Nowy cykl live...")
        bary_per = {sym: pobierz_bary(sym, INTERWAL, limit=OKNO + 5) for sym in PARY}
        # Uruchom jedną iterację (ostatni bar)
        eng2 = backtest_portfel({}, INTERWAL, kapital_startowy=eng.kapital_calkowity,
                                dd_control=True, bary_per=bary_per, wagi=wagi)
        st = eng2.podsumowanie()
        log.info(f"Equity: {eng2.kapital_calkowity:.0f} | Trades: {st.total_trades} | WR: {st.win_rate:.1%} | PF: {st.profit_factor:.2f}")
        time.sleep(PRZERWA_S)
    except KeyboardInterrupt:
        log.info("Zatrzymanie — zamykam pozycje...")
        break
    except Exception as e:
        log.error(f"Błąd cyklu: {e}")
        time.sleep(60)
```

---

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
