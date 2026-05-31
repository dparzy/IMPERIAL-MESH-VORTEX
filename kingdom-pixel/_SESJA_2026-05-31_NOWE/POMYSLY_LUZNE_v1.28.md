# 💭 POMYSŁY LUŹNE — DELTA v1.28
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.28). Tylko nowości. Źródło: skan Ameryki/Europa/Afryka/Australia. Dedup vs ZBADANE: 0 trafień (wszystkie nowe). Status Z77: **[TROP]** = znane publicznie, **niezweryfikowane w naszym repo** (kod nie uruchomiony).

## v1.28 (31.05.2026) — INFRA DANYCH & SZYNA ZDARZEŃ (Faza 0 vs skala)

### ✅ Polars [TROP] (github: pola-rs/polars, MIT) — DataFrame w Rust
- Wielowątkowy, lazy, oszczędny RAM. Na 8 GB Fujitsu robi to, na czym **pandas się dławi**.
- Dla nas: kandydat do `DATA-001` (Ładowarka) i obróbki danych w backtestach. Trafia wprost w Fazę 0 (słaby sprzęt).

### ✅ DuckDB [TROP] (github: duckdb/duckdb, MIT) — „SQLite analityki" (OLAP in-process)
- Zero serwera, czyta Parquet/Arrow bezpośrednio, SQL na danych większych niż RAM.
- Dla nas: lokalna analiza danych historycznych i wyników Poligonu (Z17) — **idealne Faza 0**, nic nie trzeba stawiać.

### ✅ Apache Arrow [TROP] (github: apache/arrow, Apache 2.0) — kolumnowy format pamięci (zero-copy)
- Spoiwo: Polars ↔ DuckDB ↔ pandas bez kopiowania. Standard branżowy, **infrastruktura, nie alfa**.

### ✅ NATS [TROP] (github: nats-io/nats-server, Apache 2.0) — lekka szyna komunikatów
- Dla nas: **realny kandydat pod `N-CORE-02 EventBus` (Z12.3)** — lekki, chodzi na słabym sprzęcie, prostszy start niż Kafka.

### ⚠️ Ciężka artyleria — NIE na Fujitsu (Faza 2+, wieloserwerowo):
- **ClickHouse** (Apache 2.0) / **QuestDB** (Apache 2.0) — bazy time-series do danych tickowych live. Świetne, ale głodne RAM/CPU. Dopiero gdy wejdziemy na tick-data.
- **Apache Kafka** (Apache 2.0) / **Redpanda** (⚠️ **BSL 1.1 — NIE czysty open-source**, licencja źródłowo-dostępna) — szyny skali. Na teraz overkill; NATS wystarczy.

## 📍 POSTĘP — warstwa danych Faza 0: Polars + DuckDB + Arrow; EventBus: NATS ✅.
⏭️ Kolejka: realizm backtestu (mikrostruktura/LOB + walidacja faktorów) → v1.29.
