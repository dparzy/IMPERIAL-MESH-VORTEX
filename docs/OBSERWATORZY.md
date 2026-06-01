# 👁️ OBSERWATORZY IMPERIUM — Mapa Źródeł Informacji

> *"Qui bene nuntiat, bene imperat."* — Kto dobrze donosi, dobrze rządzi.
>
> Każda informacja docierająca do Cesarza przechodzi przez sieć Obserwatorów.
> Wiemy SKĄD pochodzi, jak STARA jest, jak WIARYGODNA i co z nią zrobić.

---

## 🗺️ MAPA OBSERWATORÓW

```
╔══════════════════════════════════════════════════════════════════════╗
║                    👁️  SIEĆ OBSERWATORÓW IMPERIUM                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  Warstwa I:   OCZY (dane rynkowe, OHLCV, order book, funding)        ║
║  Warstwa II:  USZY (sentiment, newsy, social, makro)                  ║
║  Warstwa III: WIESZCZOWIE (on-chain, whale tracker, options flow)     ║
║  Warstwa IV:  SZPIEDZY (CME, dark pool, VPIN, korelacje zewnętrzne)  ║
║  Warstwa V:   HEROLD (agregacja → Brama → Legatus)                   ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 👁️ WARSTWA I — OCZY (Dane Rynkowe)

### Źródła OHLCV + Tick Data

| # | Źródło | Interwały | Opóźnienie | Status | Moduł |
|---|--------|-----------|------------|--------|-------|
| 1 | **MEXC WebSocket** | 1m, 5m, 15m, 1H, 4H, 1D | Realtime | 🔑 Czeka na klucz | `akwedukty/nexus_hub.py` |
| 2 | **MEXC REST API** | wszystkie | ~1s | 🔑 Czeka na klucz | `akwedukty/nexus_hub.py` |
| 3 | **Kwatermistrz (CSV)** | dowolny | offline | ✅ Działa | `akwedukty/kwatermistrz_danych.py` |
| 4 | **Binance** (faza 2) | wszystkie | Realtime | 🟠 Prowincja | `akwedukty/multi_exchange.py` |
| 5 | **OKX** (faza 2) | wszystkie | Realtime | 🟠 Prowincja | `akwedukty/multi_exchange.py` |
| 6 | **Bybit** (faza 2) | wszystkie | Realtime | 🟠 Prowincja | `akwedukty/multi_exchange.py` |

### Dane Order Book

| # | Źródło | Dane | Opóźnienie | Neuron |
|---|--------|------|------------|--------|
| 1 | MEXC WebSocket | Bid/Ask L2, 20 poziomów | Realtime | `OB-01` Order Book Imbalance |
| 2 | MEXC WebSocket | CVD (Cumulative Volume Delta) | Realtime | `CVD-01` CVD Divergence |
| 3 | MEXC WebSocket | Trades stream (taker buy/sell) | Realtime | `VPIN-01` Toxicity |
| 4 | Wyliczane z ticks | Large Orders (>50K USDT) | ~1s | `OB-04` Large Order Detection |

### Funding Rate + Open Interest

| # | Źródło | Dane | Interwał | Neuron |
|---|--------|------|----------|-------|
| 1 | MEXC Futures | Funding Rate | 8H | `SES-01` FundingRate |
| 2 | Coinglass API | Funding Rate all exchanges | 8H | `ARB-01` Funding Arb |
| 3 | MEXC Futures | Open Interest | 1H | `OI-01` OI Divergence |
| 4 | Coinglass API | Long/Short Ratio | 1H | `LSR-01` L/S Ratio |

---

## 👂 WARSTWA II — USZY (Sentiment + Newsy)

### Newsy i Sentiment

| # | Źródło | Typ danych | Opóźnienie | Neuron | Status |
|---|--------|-----------|------------|-------|-------|
| 1 | **CryptoPanic API** | Newsy krypto, byki/niedźwiedzie | 1-5min | `NEWS-01` | 🟠 Wymaga API key |
| 2 | **Santiment** | Social volume, MVRV-Z, NVT | 1H | `MVRV-01`, `NVT-01` | 🟠 Płatne |
| 3 | **LunarCrush** | Social scores, Galaxy Score | 1H | `SOC-01` | 🟠 API key |
| 4 | **Twitter/X API v2** | BTC/ETH mentions, influencers | 15min | `SOC-02` | 🟠 API key |
| 5 | **Reddit API (PRAW)** | r/bitcoin, r/ethtrader — upvotes | 30min | `SOC-03` | 🟠 Free |
| 6 | **Fear & Greed Index** | CNN Index (0-100) | 1D | `PSY-03` F&G | ✅ Free REST |
| 7 | **Alternative.me** | F&G daily | 1D | `PSY-03` | ✅ Free |

### Makro

| # | Źródło | Dane | Interwał | Neuron | Status |
|---|--------|------|----------|-------|-------|
| 1 | **DXY** (Investing/Yahoo) | USD Index | 1D | `MAC-01` DXY | 🟠 Scraping/feed |
| 2 | **TradingEconomics** | CPI, Fed Funds Rate | miesięczny | `MAC-02` Macro | 🟠 API key |
| 3 | **Forex Factory** | Kalendarz событий | dzienny | `HERMES` event checker | 🟠 Scraping |
| 4 | **FedWatch Tool (CME)** | P(podwyżka stóp) | weekly | `MAC-03` FedWatch | 🟠 Scraping |

---

## 🔮 WARSTWA III — WIESZCZOWIE (On-Chain + Smart Money)

### On-Chain (Bitcoin/Ethereum)

| # | Źródło | Dane | Interwał | Neuron | Status |
|---|--------|------|----------|-------|-------|
| 1 | **Glassnode** | MVRV-Z, SOPR, Puell, Coindays | 1D | `OC-01..05` | 🟠 Płatne (Tier 1 free) |
| 2 | **IntoTheBlock** | Large Tx, In/Out Money | 1H | `OC-06` | 🟠 API key |
| 3 | **CryptoQuant** | Exchange netflow, Miner flow | 1H | `OC-07` | 🟠 Płatne |
| 4 | **Etherscan API** | Whale wallets, gas price | Realtime | `OC-08` | ✅ Free tier |
| 5 | **Blockchain.info** | BTC mempool, tx count | Realtime | `OC-09` | ✅ Free |

### Whale Tracker

| # | Źródło | Dane | Neuron | Status |
|---|--------|------|-------|-------|
| 1 | **Whale Alert API** | Duże transfery >500K USD | `WH-01` Whale Move | 🟠 API key (free tier) |
| 2 | **Arkham Intelligence** | Labeled wallets, exchange inflows | `WH-02` Arkham | 🟠 API key |
| 3 | **Nansen** | Smart Money flows, DEX trades | `WH-03` Nansen | 🟠 Płatne |

### Options Flow (Derywaty)

| # | Źródło | Dane | Neuron | Status |
|---|--------|------|-------|-------|
| 1 | **Deribit API** | IV, Put/Call ratio, GEX, skew | `OPT-01..04` | ✅ Free REST |
| 2 | **Laevitas** | Options analytics, Max Pain | `OPT-05` Max Pain | 🟠 Częściowo płatne |
| 3 | **Greeks.live** | GEX, term structure | `OPT-03` GEX | 🟠 Free/limited |

---

## 🕵️ WARSTWA IV — SZPIEDZY (Niestandardowe Sygnały)

### CME Futures (Historyczne — zmiana 29.05.2026)

| # | Źródło | Dane | Neuron | Status |
|---|--------|------|-------|-------|
| 1 | **CME Group API** | BTC/ETH futures OHLCV | `SES-03` CME Gap | ⚠️ CME 24/7 od 29.05.2026 — Gap zanika |
| 2 | **Quandl/CBOE** | Historyczne luki piątek-niedziela | `SES-03` | 🟠 Dane historyczne tylko |

### Dark Pool + Korelacje Zewnętrzne

| # | Źródło | Dane | Neuron | Status |
|---|--------|------|-------|-------|
| 1 | **FINRA TRACE** | Obligacje korporacyjne, BBB spread | `COR-01` Credit Spread | 🟠 Dostępne z opóźnieniem |
| 2 | **FRED API** | VIX, TED spread, 10Y yield | `MAC-04` VIX | ✅ Free API |
| 3 | **SPY/QQQ** (Yahoo Finance) | Korelacja krótkoterminowa | `COR-02` Risk-Off | ✅ Free |
| 4 | **DeFi Pulse** | TVL protokołów, defi vs cex | `DEF-01..03` | 🟠 Częściowo płatne |

### Asymetria Informacji (Giełdy)

| # | Dane | Obliczane z | Neuron |
|---|------|------------|-------|
| 1 | VPIN (toxicity) | Taker buy/sell z WebSocket | `VPIN-01` |
| 2 | Płynność bid-ask spread | L2 order book | `OB-02` Liquidity |
| 3 | Spoofing detection | Order placement/cancel ratio | `ANTI-01` Spoofing |
| 4 | Wash trading ratio | Repetitive exact trades | `ANTI-02` Wash |
| 5 | Market cap / DEX TVL ratio | CoinGecko + Defillama | `DEF-03` |

---

## 📣 WARSTWA V — HEROLD (Agregacja → Brama)

```
[OCZY]        MEXC WebSocket → OHLCV, OB, CVD, Funding
[USZY]        CryptoPanic/F&G → News, Sentiment
[WIESZCZOWIE] Glassnode/Deribit → On-chain, Options
[SZPIEDZY]    FRED/Yahoo → VIX, korelacje, DXY
      ↓
[KWATERMISTRZ DANYCH]  ← normalizacja, interpolacja, jakość
      ↓
[BRAMA KALKULATORA]    ← TA-Lib: RSI/EMA/ATR/BBands/ADX...
      ↓
[HERMES — Data Auditor] ← hash, kompletność, VPIN, event check
      ↓
[LEGIONY NEURONÓW]     ← neurony dają sygnały (299 katalog / 27 kod)
      ↓
[LEGATUS]              ← agregacja ważona reżimem
      ↓
[SENAT]                ← debata meta-warstwy
      ↓
[DORADCY CARA]         ← ORACLE/FULMEN/IUSTITIA/HERMES/PYTHIA
      ↓
[CESARZ DeepSeek]      ← ostateczna decyzja + prompt
```

---

## 📊 STATYSTYKI SIECI OBSERWATORÓW

| Warstwa | Źródeł łącznie | Bezpłatnych | Wymaga klucza | Status |
|---------|---------------|-------------|---------------|-------|
| I. OCZY | 12 | 3 | 9 | MEXC klucz = 9 odblokowanych |
| II. USZY | 11 | 3 | 8 | Newsy + makro |
| III. WIESZCZOWIE | 12 | 3 | 9 | On-chain kosztuje |
| IV. SZPIEDZY | 9 | 4 | 5 | FRED/Yahoo darmowe |
| **ŁĄCZNIE** | **44** | **13** | **31** | |

**Priorytet klucza MEXC** = odblokuje 9 najważniejszych źródeł warstwy I.
**Priorytet bezpłatnego startu** = FRED API (VIX, yield), Alternative.me (F&G), Deribit (options), Whale Alert free tier.

---

## 🔑 KLUCZE API — Priorytety

| Priorytet | Klucz | Koszt | Odblokowuje | Gdzie ustawić |
|-----------|-------|-------|------------|---------------|
| 🔴 #1 | `MEXC_API_KEY` + `MEXC_SECRET` | Free (wymaga konta) | 9 źródeł warstwy I | `setx MEXC_API_KEY "..."` |
| 🔴 #2 | `DEEPSEEK_API_KEY` | ~$0.14/1M tokens | Cesarz DeepSeek | `setx DEEPSEEK_API_KEY "..."` |
| 🟠 #3 | `WHALE_ALERT_KEY` | Free tier (3 req/min) | Whale moves | `setx WHALE_ALERT_KEY "..."` |
| 🟠 #4 | `CRYPTOPANIC_KEY` | Free tier | Newsy krypto | `setx CRYPTOPANIC_KEY "..."` |
| 🟡 #5 | `GLASSNODE_KEY` | Tier 1 free | On-chain podstawy | `setx GLASSNODE_KEY "..."` |
| 🟡 #6 | `DERIBIT_KEY` | Free | Options flow | — (REST bez klucza) |

---

## 🛡️ PRAWO OBSERWATORA

1. **Każde źródło ma hash** — HERMES weryfikuje integralność danych
2. **Każde źródło ma wiek** — dane starsze niż 2×interwał są blokowane
3. **Każde źródło ma wagę** — im wyższy tier, tym wyższe zaufanie w Igrzyskach
4. **Żaden obserwator nie jest jedynym sędzią** — minimum 3 niezależne źródła na kategorię
5. **Fałszywy obserwator = Lista Infamii** — źródło dające >30% fałszywych sygnałów jest flagowane

---

## 🔗 POWIĄZANIA Z NEURONAMI

| Kategoria Neuronów | Obserwatorzy (warstwy) | Kluczowe źródła |
|-------------------|----------------------|-----------------|
| Momentum (X Equestris) | I (OHLCV, OB) | MEXC WebSocket, RSI/EMA z Bramki |
| Swing (XII Fulminata) | I + II | MEXC + Santiment/F&G |
| Macro (III Augusta) | II + III | Glassnode + FRED + Makro |
| Leverage/Liq (VI Ferrata) | I + III | MEXC OI/Funding + Deribit |
| Anti-manipulation (Straż) | I + IV | VPIN, Spoofing, Wash |
| On-chain (Wieszczowie) | III | Glassnode, Santiment, CryptoQuant |
| Options (Opcji) | III | Deribit, Greeks.live, Laevitas |
| Sentiment (Wyrocznia) | II | CryptoPanic, LunarCrush, F&G, Twitter |

---

*"Oculus qui non videt, manus quae non agit."*
*Oko które nie widzi, ręka która nie działa.*

*— OBSERWATORZY.md | v1.0 | 2026-06-01 | 🏛️ IMV-ORI*
