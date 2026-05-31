# 💭 POMYSŁY LUŹNE — DELTA v1.14
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.14). Tylko nowości.

## v1.14 (30.05.2026) — LINK-DIVE: Freqtrade + VectorBT (oba REALNE, dojrzałe, wprost dla nas)

### ✅ Freqtrade (github: freqtrade/freqtrade) — możliwa BAZA bota
- Od **2017**, ~49k gwiazdek, wydania **miesięczne** (v2026.3). Python, open-source, **self-hosted, 100+ giełd (CCXT)**.
- Backtest (lata OHLCV, P&L, drawdown) · **Hyperopt** (auto-optymalizacja parametrów — tysiące backtestów → najlepsza konfiguracja = nasza KALIBRACJA) · **FreqAI** (ML na historii → sygnały) · **dry-run = paper** · Telegram/webUI.
- 🔎 Ma **lookahead-analysis + recursive-analysis** → wykrywanie lookahead-bias / **overfittingu** (wprost nasz problem!).
- Werdykt: realna **baza pod bota albo wzorzec** — robi sporo tego, co my ręcznie (paper, koszty, drawdown, kalibracja). ⚠️ „edukacyjne, na własne ryzyko", wymaga Pythona + utrzymania.

### ✅ VectorBT (github: polakowo/vectorbt) — silnik pod auto-config tester
- **Najszybszy open-source backtest: 1 mln zleceń w 70–100 ms** (Numba + opcjonalny Rust).
- **Testuje TYSIĄCE konfiguracji / okresów / monet w SEKUNDY** (multi-asset, multi-interwał) → **wprost Twój „automat testujący wszystkie konfiguracje + dziennik"** (wizja v1.9).
- **Walk-forward optimization** (robustness) → **anti-overfitting** (złoty standard walidacji). Koszty + poślizg. TA-Lib/Pandas-TA. QuantStats (Sharpe, DD).
- Przykład PRO: BTC/USDT+ETH/USDT, **~20 000 konfiguracji MACD w <30 s**, mapa win-rate vs parametry.
- Werdykt: idealny silnik pod **nasz multi-coin tester + bezpieczną walidację**.

### 🎯 Wniosek
**Freqtrade + VectorBT = gotowa, sprawdzona INFRASTRUKTURA** (paper, backtest, kalibracja, **walk-forward**) — nie musimy wynajdywać koła. To **uprząż, nie alfa** — edge zostaje w NASZEJ strategii + Mózgu. Oba lokalne/darmowe = niezależność. Oba uczciwie ostrzegają „na własne ryzyko".

## 📍 POSTĘP — link-diving: Kronos ✅ · NEXUS ✅ · TradingAgents ✅ · Freqtrade ✅ · VectorBT ✅.
⏭️ Następne: FinRL, FinCrew, OpenBB, RegimeNAS, DoWhy.
