# 💭 POMYSŁY LUŹNE — DELTA v1.15
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.15). Tylko nowości.

## v1.15 (30.05.2026) — LINK-DIVE: FinRL + OpenBB

### ✅ FinRL (github: AI4Finance-Foundation/FinRL) — RL dla tradingu (warstwa UCZENIA)
- Pierwszy open-source framework **deep reinforcement learning (DRL)** dla finansów. Recenzowany (NeurIPS 2020, ACM ICAIF'21), aktywny (v0.3.8 III.2026; FinRL-X @ PAKDD 2026). Apache 2.0.
- Agent uczy się decyzji przez interakcję z rynkiem (algos: PPO, SAC, DDPG, A2C, TD3, DQN). Modułowy, wiele rynków (akcje + krypto przez FinRL-Meta), backtest + metryki. Ekosystem: FinRL-Meta (setki środowisk), ElegantRL, FinRL-X (produkcyjny, 2026).
- ⚠️ **Uczciwie:** DRL w LIVE jest NOTORYCZNIE trudne — agenci RL przeuczają się na środowiskach historycznych i słabo generalizują na niestacjonarny rynek na żywo. Świetne do badań/eksperymentów (warstwa uczenia/ewolucji), ale **NIE magiczny przycisk zysku** — wysokie ryzyko overfittingu. Repo: „edukacyjne, nie porada".

### ✅ OpenBB (github: OpenBB-finance/OpenBB) — warstwa DANYCH dla OCZU
- Open-source „Bloomberg" (vs $24k/rok). ~50k userów, $8.5M seed, realna firma (CEO Didier Lopes).
- **„Connect once, consume everywhere":** jeden adapter do **100+ źródeł danych** (yfinance, FMP, SEC EDGAR, **FRED makro**, Polygon…) → czyste Pandas DataFrames. Surfaces: Python, REST API, **MCP (dla agentów AI!)**, Excel.
- Dane: ceny, opcje, **filings SEC**, **makro (FRED)**, fundamenty — zunifikowane → wprost **OCZY: warstwa makro (5) + korelacje (6) + kalendarz makro**.
- ⚠️ **Licencja AGPL v3 = viralny copyleft:** dla NASZEGO osobistego/self-hosted użytku OK (suwerenność danych, lokalnie). Gdybyśmy kiedyś oferowali jako usługę klientom → trzeba otworzyć własny kod albo kupić licencję komercyjną. Dla krypto uzupełnić **CCXT/CoinGecko** (OpenBB mocniejszy w makro/akcjach/fundamentach).

### 🎯 Wniosek
FinRL = warstwa uczenia (badawczo; ostrożnie z overfit/live). OpenBB = solidna, lokalna warstwa danych makro/fundamentów dla OCZU (100+ źródeł, MCP). Oba realne, oba „edukacyjne / na własne ryzyko".

## 📍 POSTĘP — link-diving: Kronos·NEXUS·TradingAgents·Freqtrade·VectorBT·**FinRL·OpenBB** ✅.
⏭️ Następne: FinCrew (reality-check), RegimeNAS, DoWhy, Parrondo.
