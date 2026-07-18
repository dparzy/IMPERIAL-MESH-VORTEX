---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/biblioteki/pamiec_absolutna.py, imperium/biblioteki/kronikarz.py
stan_na: 2026-07-17
powod_istnienia: "Jedyny dokument opisujący schemat rekordu `ImperiumLog` (atomowa jednostka pamięci transakcyjnej — Warstwa 1 pamięci) wraz z realnym API zapisu/odczytu i jawną listą luk wobec deklaracji Prawa IX."
dublet_rozstrzygniety: docs/ARCHITEKTURA_IMPERIUM.md — Architektura wymienia kronikarz.py jako organ w mapie systemu (jedno zdanie roli); tutaj żyje SCHEMAT rekordu i API zapisu. Podział ról świadomy, nie dublet treści.
---
# 🧠 PAMIĘĆ ABSOLUTNA — Warstwa 1 (logi transakcyjne)

> *"Quod non scribitur, non factum est."* — Co nie jest zapisane, nie zostało zrobione.

**Status kod-vs-plan (ZPO — Zasada Pełnego Opisu):** ✅ = działa w kodzie na branchu ·
🔴 = plan/wizja, kodu NIE MA.
Weryfikacja mechaniczna wobec kodu: **2026-07-17** (`stan_na`). Każde twierdzenie niżej ma
oznaczenie statusu — dokument bez tego zmusza czytelnika do zgadywania, co jest gotowe.

---

## 🎯 PO CO TO JEST

`ImperiumLog` to **DNA jednej decyzji** — atomowy rekord: co widziały neurony, co orzekł
Legatus, co zrobiła pozycja. Warstwa 1 z 13 warstw pamięci (mapa: [`MAPA_PAMIECI.md`](./MAPA_PAMIECI.md)).

Dzięki niej możemy: ✅ odtworzyć skład głosów przy dowolnym trade (`sygnaly_json`), ✅ zmierzyć
jakość wyjścia (MAE/MFE), ✅ zasilić Centrum Pamięci cross-layer (`centrum_pamieci` czyta
TRADE_CLOSE z tej warstwy), 🔴 porównać kwartały jednym zapytaniem (brak Interrogatora — niżej).

---

## 📦 SCHEMAT REKORDU — `ImperiumLog` ✅

**<!-- LICZBA:pola_logu -->68<!-- /LICZBA --> pól** (liczba wstrzykiwana z `dataclasses.fields`
— Warstwa 15; nie wpisuj jej ręcznie). Źródło: [`pamiec_absolutna.py`](../imperium/biblioteki/pamiec_absolutna.py).

Grupy pól — nazwy **dokładnie takie jak w kodzie** (Prawo XXI: żadnych aliasów):

| Grupa | Pola |
|---|---|
| **Identyfikacja** | `log_id` (UUID4, auto) · `log_typ` · `sesja_id` · `sekwencja` · `timestamp_utc` (ISO 8601 UTC, auto) |
| **Kontekst rynku** | `symbol` · `interwal` · `cena_open/high/low/close` · `wolumen` · `rezim` · `sesja_rynkowa` · `btc_dominacja` · `funding_rate` |
| **Neurony** | `neurony_aktywne` · `neurony_long` · `neurony_short` · `neurony_neutral` · `sygnaly_json` · **`top3_long`** · **`top3_short`** |
| **Legatus** | `legatus_kierunek` · `legatus_pewnosc` · `legatus_sila_long` · `legatus_sila_short` · `legatus_weto` · `legatus_powod_weta` |
| **Senat** | `senat_aktywny` · `senat_wynik` · `senat_populares` · `senat_optimates` · `senat_runda` |
| **Plan pozycji** | `plan_aktywny` · `kierunek_pozycji` · `cena_wejscia` · `dzwignia` · `cena_likwidacji` · `stop_loss` · `take_profit` · `rozmiar_usdt` · `ryzyko_usdt` · `rr_ratio` |
| **Egzekucja** | `trade_id` · `trade_status` · `cena_wykonania` · `slippage_pct` · `prowizja_usdt` · `kapital_przed` · `kapital_po` · `pnl_usdt` · `pnl_pct` · `czas_trwania_min` · `powod_zamkniecia` · **`mae_pct`** · **`mfe_pct`** |
| **Źródła (kanały)** | `kanaly_aktywne` · `on_chain_snapshot` · `sentyment_snapshot` · `macro_snapshot` (JSON-stringi) |
| **Jakość danych** | `hash_sha256` (⚠️ patrz LUKA 1) · `bramka_wersja` · `kompletnosc_danych` |
| **Metadane** | `wersja_systemu` · `strategia_id` · `igrzyska_wagi` · `notatka` |

`log_id`, `sekwencja` i `timestamp_utc` mają wartości domyślne — reszta jest opcjonalna
(dataclass z domyślnymi), więc **kompletność rekordu zależy od modułu, który go tworzy**.

### Typy logu — `TypLogu` ✅

`SYGNAL` (wartość `"SYGNAŁ"`) · `TRADE_OPEN` · `TRADE_CLOSE` · `ANALIZA` · `TEST` · `SENAT` ·
`WETO` · `IGRZYSKA` · `DORADCY`.

**Realnie zapisywane są 3 z 9** (zmierzone grepem po `TypLogu.` w `imperium/`):
`TRADE_CLOSE` (paper_trading), `ANALIZA` (scheduler), `TRADE_OPEN`/`SYGNAL` (fabryki niżej).
Pozostałe (`TEST`, `SENAT`, `WETO`, `IGRZYSKA`, `DORADCY`) — 🔴 **zdefiniowane, nieużywane**.

---

## 🔧 REALNE API ✅

```python
from imperium.biblioteki.pamiec_absolutna import (
    PamiecAbsolutna, ImperiumLog, TypLogu, log_sygnal, log_trade_open,
)

pamiec = PamiecAbsolutna()                    # katalog: $IMPERIUM_LOG_DIR lub imperium/biblioteki/pamiec/logi
sciezka = pamiec.zapisz(log)                  # dopisuje linię JSONL, nadaje `sekwencja`
logi    = pamiec.wczytaj(symbol="BTCUSDT", data="2026-07-17", log_typ="TRADE_CLOSE")
podsum  = pamiec.podsumowanie_sesji(sesja_id, logi)   # agregat: PnL/liczby per sesja

log = log_sygnal(sesja_id, symbol, interwal, raport, rezim="NORMAL")  # z RaportLegatusa
log = log_trade_open(sesja_id, plan, kapital, trade_id="", status="PAPER")  # z PlanPozycji
```

`ImperiumLog.to_json()` / `ImperiumLog.from_json(s)` — serializacja rekordu.
Katalog nadpisywalny zmienną środowiskową **`IMPERIUM_LOG_DIR`** (tak robią testy).

**Kto zapisuje (wpięcie w pipeline — Prawo XV):** ✅ `koloseum/paper_trading.py` (TRADE_CLOSE
z MAE/MFE) · ✅ `drogi/scheduler.py` (ANALIZA) · ✅ czyta: `biblioteki/centrum_pamieci.py`
(cross-layer W1), `biblioteki/kustosz_pamieci.py` (inwentarz warstw).

---

## 📁 STRUKTURA PLIKÓW

**Realnie tworzone przez kod** ✅ — wyłącznie drzewo logów, rok/miesiąc z daty rekordu:

```
imperium/biblioteki/pamiec/logi/<rok>/<mies>/<data>_<symbol>_<typ>.jsonl
   np. 2026/06/2026-06-01_BTCUSDT_sygnał.jsonl      ← typ = TypLogu.lower()
       2026/06/2026-06-01_BTCUSDT_trade_close.jsonl
```

Nazwa pliku powstaje z `f"{data}_{symbol}_{typ.lower()}.jsonl"` — dla `SYGNAL` daje to
`_sygnał.jsonl` (z polskim znakiem, bo wartość enuma to `"SYGNAŁ"`).

🔴 **NIE ISTNIEJĄ** (były opisane jako gotowe do 2026-07-17 — nieprawda): katalogi
`igrzyska/`, `sesje/`, `analizy/walk_forward/`, plik `indeks.json`, pliki panteonu
(`PANTEON_NEURONOW.md`, `TRIUMPHI.md`, `ALBUM_SENATUS.md`). Rankingi neuronów żyją dziś
w arenie (`arena_wyniki.db`) i w Igrzyskach (`biblioteki/igrzyska.py`), nie w tym drzewie.

---

## 🔍 SYSTEM ZAPYTAŃ — 🔴 PLAN (Kronikarz v2 „Interrogator")

**Nie istnieje.** Do 2026-07-17 ten dokument prezentował `kronikarz.zapytaj(...)`,
`kronikarz.porownaj_okresy(...)` i `kronikarz.replay_sesji(...)` jako gotowe API — w kodzie
nie ma żadnej z tych funkcji (zweryfikowane grepem: 0 trafień).

**Co Kronikarz ma naprawdę** ✅ ([`kronikarz.py`](../imperium/biblioteki/kronikarz.py)):
jedną metodę `Kronikarz.zapisz(report: RunReport)` — zapis podsumowania BIEGU (bot, wersja,
parametry, trades, kapitał, win_rate, drawdown), a nie przeszukiwanie logów. To inny organ
niż Interrogator: **rejestrator biegu, nie wyszukiwarka historii**.

**Czym filtrować dziś** ✅: `PamiecAbsolutna.wczytaj(symbol=, data=, log_typ=)` — filtr po
nazwie pliku, bez zapytań po reżimie/pewności/zakresie dat. Bogatsze pytania do historii
obsługuje Centrum Pamięci (`centrum_pamieci szukaj`) i arena.

---

## 📊 METRYKI PER-TRADE

✅ **W kodzie:** `mae_pct` / `mfe_pct` (Maximum Adverse/Favorable Excursion) — wypełniane
przez `paper_trading` przy każdym TRADE_CLOSE, razem z `pnl_pct`, `prowizja_usdt`,
`powod_zamkniecia`, `czas_trwania_min`. MAE/MFE to materiał do optymalizacji SL/TP.

🔴 **Nie istnieje:** `efficiency_ratio` (pnl / MFE), `rezim_wejscia`/`rezim_wyjscia` jako
osobne pola, snapshot wag Igrzysk przy wejściu (`igrzyska_wagi` jest polem, ale nikt go nie
wypełnia). Efficiency ratio da się policzyć z `pnl_pct`/`mfe_pct` po fakcie — nie jest zapisywane.

---

## 🚨 LUKI ZMIERZONE 2026-07-17 (Prawo XV — utrata potencjału)

**LUKA 1 — łańcuch integralności SHA-256 jest przerwany na całej długości.**
Brama liczy pieczątkę audytu dla każdego wskaźnika (`CalcResult.sha256`,
[`brama_kalkulatora.py`](../imperium/fundament/brama_kalkulatora.py)) ✅ — ale:
- `ImperiumLog.hash_sha256` **nigdy nie jest wypełniany** (0 przypisań w całej bazie kodu);
- doradca Hermes ma bramkę `hash_ok` opisaną jako „SHA-256 zgadza się z zapisem w Pamięci
  Absolutnej", a [`dyrygent.py`](../imperium/koloseum/dyrygent.py) podaje jej **`hash_ok=True`
  na sztywno** — bramka integralności, która zawsze przepuszcza, nie jest bramką;
- Prawo IX (niżej) wymienia `hash_sha256` jako pole OBOWIĄZKOWE — **kod łamie własne prawo**.

Zapisane w Księdze Wad Kodu jako klasa `bramka-zawsze-przepuszcza`. Naprawa = osobne zadanie
(wpięcie hash Bramy w log + realna weryfikacja u Hermesa wg ZASADY WPIĘCIA: opt-in OFF).

**LUKA 2 — 6 z 9 typów logu bez producenta:** `TEST` (miał rejestrować okna WFO —
Walk-Forward Optimization, optymalizacja krocząca: [`walk_forward.py`](../imperium/koloseum/walk_forward.py)
liczy własny raport i **nie zapisuje** ImperiumLog), `SENAT`, `WETO`, `IGRZYSKA`, `DORADCY`,
`SYGNAL` poza fabryką. Deklarowany łańcuch „Senat→SENAT, Pretorianie→WETO, Igrzyska→IGRZYSKA"
jest 🔴 planem, nie działaniem.

---

## 🏺 PRAWO IX — Lex Memoriae

> „Każdy sygnał, każda analiza, każdy trade musi pozostawić ImperiumLog.
> Moduł bez logu = moduł bez dowodu istnienia."

**Minimalny zestaw wg prawa:** `log_id`, `log_typ`, `sesja_id`, `timestamp_utc`, `symbol`,
`hash_sha256` — z czego pierwsze pięć jest realnie wypełniane ✅, a `hash_sha256` nie (LUKA 1).
Prawo pozostaje celem; ten dokument nie udaje, że jest już spełnione (Prawo I).

---

*"Historia est magistra vitae."*

*— PAMIEC_ABSOLUTNA.md | v2.0 (weryfikacja wobec kodu) | 2026-07-17*
