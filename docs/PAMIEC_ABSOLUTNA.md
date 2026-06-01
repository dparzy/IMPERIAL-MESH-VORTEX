# 🧠 PAMIĘĆ ABSOLUTNA — System Logowania Imperium

> *"Quod non scribitur, non factum est."* — Co nie jest zapisane, nie zostało zrobione.
>
> Każdy sygnał, każda analiza, każdy trade, każdy test musi zostawić ślad.
> Bez Pamięci Absolutnej nie wiemy co działało, co zawiodło, i dlaczego.

---

## 🎯 FILOZOFIA

Pamięć Absolutna to nie zwykły log. To **DNA każdej decyzji systemu**.

Dzięki niej możemy:
- Porównać układ neuronów sprzed 6 miesięcy z dzisiejszym
- Sprawdzić które źródło informacji (kanał) wpłynęło na decyzję
- Odtworzyć dokładnie ten sam stan systemu z przeszłości (deterministic replay)
- Zasilić Igrzyska — bez logów nie ma rankingów
- Debugować: "Co się stało w BTC 2026-03-15 o 14:32 kiedy system wszedł SHORT?"

---

## 📦 SCHEMAT REKORDU — `ImperiumLog`

Każdy rekord to **jeden sygnał/decyzja** — atomowa jednostka pamięci.

```python
@dataclass
class ImperiumLog:
    # === IDENTYFIKACJA ===
    log_id: str          # UUID4 — unikalny klucz rekordu
    log_typ: str         # SYGNAŁ / TRADE_OPEN / TRADE_CLOSE / ANALIZA / TEST / SENAT / WETO / IGRZYSKA
    sesja_id: str        # UUID sesji tradingowej (łączy powiązane logi)
    sekwencja: int       # numer w ramach sesji (1, 2, 3...)
    timestamp_utc: str   # ISO 8601, zawsze UTC

    # === KONTEKST RYNKU ===
    symbol: str          # "BTCUSDT"
    interwal: str        # "M5", "1H", "4H", "1D"
    cena_open: float
    cena_high: float
    cena_low: float
    cena_close: float
    wolumen: float
    rezim: str           # TREND_STRONG / RANGING / VOLATILE / PANIC / NORMAL
    sesja_rynkowa: str   # AZJA / LONDYN / NOWY_JORK / OFF_HOURS
    btc_dominacja: float # dominacja BTC w % w chwili sygnału
    funding_rate: float  # aktualna stawka funding (0.0 = neutralna)

    # === NEURONY AKTYWNE ===
    neurony_aktywne: int          # ile neuronów głosowało
    neurony_long: int             # ile dało LONG
    neurony_short: int            # ile dało SHORT
    neurony_neutral: int          # ile dało NEUTRAL
    sygnaly_json: str             # JSON: lista {klucz, kierunek, pewnosc, waga}
    top3_neurony_long: str        # klucze 3 najsilniejszych neuronów LONG
    top3_neurony_short: str       # klucze 3 najsilniejszych neuronów SHORT

    # === AGREGACJA LEGATUSA ===
    legatus_kierunek: str         # LONG / SHORT / NEUTRAL
    legatus_pewnosc: float        # 0.0–1.0
    legatus_sila_long: float
    legatus_sila_short: float
    legatus_weto: bool
    legatus_powod_weta: str

    # === SENAT (jeśli aktywny) ===
    senat_aktywny: bool
    senat_wynik: str              # LONG / SHORT / NEUTRAL / BRAK_ZGODY
    senat_populares: float        # siła frakcji Popularów
    senat_optimates: float        # siła frakcji Optymatów
    senat_runda: int              # która runda debaty

    # === PLAN POZYCJI (Kalkulator Lewara) ===
    plan_aktywny: bool
    kierunek_pozycji: str
    cena_wejscia: float
    dzwignia: int
    cena_likwidacji: float
    stop_loss: float
    take_profit: float
    rozmiar_usdt: float
    ryzyko_usdt: float
    rr_ratio: float

    # === TRADE EXECUTION (jeśli TRADE_OPEN / TRADE_CLOSE) ===
    trade_id: str                 # ID zlecenia na giełdzie
    trade_status: str             # PAPER / LIVE / TEST
    cena_wykonania: float         # rzeczywista cena wejścia
    slippage_pct: float           # cena_wejscia vs cena_wykonania
    prowizja_usdt: float
    kapital_przed: float
    kapital_po: float             # (przy TRADE_CLOSE)
    pnl_usdt: float               # (przy TRADE_CLOSE)
    pnl_pct: float                # (przy TRADE_CLOSE)
    czas_trwania_min: int         # (przy TRADE_CLOSE)
    powod_zamkniecia: str         # TP / SL / MANUAL / WETO / TIMEOUT

    # === ŹRÓDŁA INFORMACJI (Kanały) ===
    kanaly_aktywne: str           # JSON: lista aktywnych kanałów w tej chwili
    # Przykład: ["MEXC_FEED", "FUNDAMENT_GATE", "OCZY_NEWSY", "DEFI_TVL"]
    on_chain_snapshot: str        # JSON: klucze on-chain w chwili sygnału
    # Przykład: {"MVRV": 2.1, "NVT": 45, "funding": 0.0002, "TVL_vel": 0.08}
    sentyment_snapshot: str       # JSON: {"FearGreed": 62, "SocialVol": "normal"}
    macro_snapshot: str           # JSON: {"DXY": 104.2, "US10Y": 4.3, "Gold": 2340}

    # === JAKOŚĆ DANYCH ===
    hash_sha256: str              # SHA-256 z Bramki — weryfikacja integralności
    bramka_wersja: str            # wersja Calculator Gate
    kompletnosc_danych: float     # % wskaźników które miały dane (0–1)

    # === METADANE SYSTEMU ===
    wersja_systemu: str           # "v0.3.2"
    strategia_id: str             # "XII-RV-003" lub "auto" jeśli auto-dobór
    igrzyska_wagi: str            # JSON: {klucz_neuronu: waga} — wagi z Igrzysk
    notatka: str                  # opcjonalna notatka operatora lub AI
```

---

## 📁 STRUKTURA PLIKÓW PAMIĘCI

```
imperium/biblioteki/pamiec/
├── logi/
│   ├── 2026/
│   │   ├── 06/
│   │   │   ├── 2026-06-01_BTCUSDT_sygnaly.jsonl    ← JSONL: jeden rekord/linia
│   │   │   ├── 2026-06-01_BTCUSDT_trades.jsonl
│   │   │   └── 2026-06-01_sesja_001.jsonl
├── igrzyska/
│   │   ├── 2026-06-01_wyniki_neuronow.json          ← dzienny ranking neuronów
│   │   ├── 2026-06-01_wyniki_legionow.json
│   │   └── panteon/
│   │       ├── PANTEON_NEURONOW.md
│   │       ├── TRIUMPHI.md
│   │       └── ALBUM_SENATUS.md
├── sesje/
│   │   └── sesja_001_summary.json                  ← podsumowanie sesji tradingowej
├── analizy/
│   │   └── walk_forward/
│   │       └── wf_2026-06_wyniki.json
└── indeks.json                                     ← szybki indeks sesji/dat/symboli
```

**Format JSONL** — jeden log = jedna linia JSON. Efektywny, streamowalny, łatwy do grep.

---

## 🔍 SYSTEM ZAPYTAŃ (Kronikarz v2 — Interrogator)

Interfejs do przeszukiwania Pamięci Absolutnej:

```python
kronikarz.zapytaj(
    symbol="BTCUSDT",
    interwal="1H",
    rezim="TREND_STRONG",
    od="2026-01-01",
    do="2026-06-01",
    typ="TRADE_CLOSE",
    strategia="XII-RV-003",
    min_pewnosc=0.70
)
# → Lista ImperiumLog pasujących do kryteriów

kronikarz.porownaj_okresy(
    okresy=[("2025-Q4", "2026-Q1"), ("2026-Q1", "2026-Q2")],
    metryki=["pnl_pct", "legatus_pewnosc", "slippage_pct"]
)
# → DataFrame z porównaniem tych samych metryk w różnych kwartałach

kronikarz.replay_sesji(sesja_id="abc-123")
# → Odtwórz stan systemu krok po kroku (debugging)
```

---

## 📊 METRYKI PER-TRADE (Rejestr Koloseum)

Dla każdego zamkniętego trade rejestrujemy **kompletne metryki Koloseum**:

```json
{
  "trade_id": "T-2026-06-01-001",
  "symbol": "BTCUSDT",
  "strategia": "XII-TR-004",
  "rezim_wejscia": "TREND_STRONG",
  "rezim_wyjscia": "RANGING",
  "pnl_pct": 2.34,
  "max_adverse_excursion_pct": -0.8,   ← najgorszy moment IN-trade
  "max_favorable_excursion_pct": 3.1,  ← najlepszy moment IN-trade
  "efficiency_ratio": 0.755,           ← pnl / max_favorable (czy dobrze wyszedłeś)
  "slippage_pct": 0.015,
  "prowizja_pct": 0.04,
  "netto_pct": 2.285,
  "czas_trwania_min": 240,
  "neurony_przy_wejsciu": {...},       ← pełny snapshot neuronów
  "igrzyska_wagi_przy_wejsciu": {...}  ← wagi z Igrzysk w tamtej chwili
}
```

**MAE / MFE** (Maximum Adverse/Favorable Excursion) — kluczowe do optymalizacji SL/TP.

---

## 🏃 WALK-FORWARD VALIDATION (Luk zidentyfikowany vs Freqtrade/QuantConnect)

```
Okno treningowe: 90 dni
Okno testowe: 30 dni
Krok: 7 dni (rolling)

Wynik WFO: Sharpe_test / Sharpe_train → powinno być > 0.6
Jeśli < 0.4 → strategia overfittowana → relegacja do archiwum
```

Rejestrujemy każde okno WFO jako osobny rekord `log_typ = "TEST"`.

---

## 🔗 INTEGRACJA Z INNYMI MODUŁAMI

```
Akwedukty → Bramka → SYGNAŁ → ImperiumLog (typ=SYGNAŁ)
     ↓
Legatus agreguje → ImperiumLog (typ=ANALIZA)
     ↓
Senat debatuje → ImperiumLog (typ=SENAT)
     ↓
Pretorianie weto/ok → ImperiumLog (typ=WETO lub WEJŚCIE)
     ↓
Drogi wykonują → ImperiumLog (typ=TRADE_OPEN)
     ↓
Trade zamknięty → ImperiumLog (typ=TRADE_CLOSE)
     ↓
Igrzyska aktualizują rankingi → ImperiumLog (typ=IGRZYSKA)
```

---

## 🏺 PRAWO IX — Lex Memoriae (rozszerzenie)

> "Każdy sygnał, każda analiza, każdy trade musi pozostawić ImperiumLog.
> Moduł bez logu = moduł bez dowodu istnienia.
> Pamięć Absolutna to fundament zaufania do systemu."

**Minimalny wymagany zestaw pól** (każdy moduł MUSI logować):
`log_id`, `log_typ`, `sesja_id`, `timestamp_utc`, `symbol`, `hash_sha256`

**Zalecany zestaw** (dla pełnej diagnostyki): wszystkie pola powyżej.

---

*"Historia est magistra vitae." — Historia jest nauczycielką życia.*

*— PAMIEC_ABSOLUTNA.md | v1.0 | 2026-06-01*
