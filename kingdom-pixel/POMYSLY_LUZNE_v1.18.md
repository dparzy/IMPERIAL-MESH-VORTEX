# 💭 POMYSŁY LUŹNE — DELTA v1.18
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.18). Tylko nowości.

## v1.18 (30.05.2026) — LINK-DIVE: NautilusTrader + Hummingbot (silniki egzekucji)

### ✅ NautilusTrader (github: nautechsystems/nautilus_trader) — TOPOWY silnik egzekucji
- Production-grade, **rdzeń w Rust** (tokio) + API Python (PyO3). ~17k★, wydania **co 2 tyg**. Multi-asset/multi-venue (FX/akcje/futures/opcje/krypto), **nanosekundowa rozdzielczość**, sub-mikrosekundowa latencja, deterministyczny (powtarzalne reruny).
- 🔑 **Parytet backtest ↔ LIVE: ta sama strategia, BEZ zmian kodu** — rozwiązuje klasyczne źródło błędów przy paper→live. Wprost nasza drabina paper→live.
- Backtest dość szybki, by **trenować agentów RL / Evolution Strategies** w platformie. Strumień 5 mln wierszy/s, dane > RAM. Zaawansowane zlecenia (post-only, reduce-only, OCO, OTO), short/margin. Redis, Docker.
- = warstwa **Drogi/Ręce** (egzekucja) + Rust (Twoja wizja). ⚠️ Stroma krzywa nauki; to silnik, NIE alfa. Open-source: single-node (bez UI/orkiestracji rozproszonej — celowo).

### ✅ Hummingbot (github: hummingbot/hummingbot) — lider MM/arbitraż (INNA nisza)
- Apache 2.0, **$34 mld wolumenu userów/rok, 140+ venues**, 40+ CEX/DEX. Lokalny, szyfruje klucze API.
- Core: **Pure Market Making, Cross-Exchange MM, AMM Arbitrage** + community (grid, funding-rate arb, DCA). Quants Lab (backtest).
- Nowość: **Condor + Hummingbot API + MCP** → zarządzanie **flotami agentów AI** (Hummingbot = warstwa egzekucji) → ciekawe pod nasz rój/multi-bota.
- ⚠️ Uczciwie: jego rdzeń to **market-making + arbitraż** — INNA gra niż nasza strategia kierunkowa (trend/momentum). Świetny, jeśli kiedyś pójdziemy w MM/arb; do kierunkowej lepiej Freqtrade/Nautilus. Testimoniale „$2 mld" = marketing — ostrożnie. MM jest kapitało/latencjo-chłonne i konkurencyjne.

### 🪜 Warstwa egzekucji — porównanie
**Freqtrade** (start, batteries-included crypto) → **NautilusTrader** (poważny, Rust, parytet live, multi-asset) → **Hummingbot** (MM/arbitraż, flota agentów). Różne tiery/nisze — bierzemy wg potrzeby, bez duplikacji.

## 📍 POSTĘP — link-diving (13): …RegimeNAS·DoWhy·Parrondo·**NautilusTrader·Hummingbot** ✅.
⏭️ Zostały m.in.: EvoAgentX, Pandas-TA, Kronos-demo (na żywo) — albo wracamy do czytania dokumentu IMV do końca.
