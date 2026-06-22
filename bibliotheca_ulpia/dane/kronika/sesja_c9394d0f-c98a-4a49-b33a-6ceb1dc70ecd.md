# Kronika sesji c9394d0f-c98a-4a49-b33a-6ceb1dc70ecd

## 🧑 Cezar
This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.

Summary:
1. Primary Request and Intent:

The user (Komendant Pixel) is building **IMPERIUM** — an AI crypto trading system with Roman Empire architecture. This session continued from prior context where basic infrastructure existed. The explicit requests this session:

- Build Generał/Legatus module (missing coordinator between Legions and Senate)
- Build Kalkulator Lewara (liquidation price calculator, must run before any leveraged position)
- Build Katalog Strategii (strategy catalog like neuron catalog, mapped to neurons)
- Integrate uploaded "Księga Strategii — Azjatycki Skan Rynku" (STR-001→STR-170) into catalog
- Search internet for more strategies from world-class traders
- Continue searching for more neurons and strategies (ongoing, most recent request)

**Critical security constraint (verbatim):** API KEY NEVER IN CODE, NEVER IN CHAT — ONLY IN ENVIRONMENT VARIABLES (`setx DEEPSEEK_API_KEY "twój-klucz"`). DeepSeek API uses `[ZREDAGOWANO]

**Working branch:** `claude/sleepy-fermi-dsdE4`
**Repository:** `dparzy/imperial-mesh-vortex`

2. Key Technical Concepts:

- **Mikro-neurony**: Single-purpose agents (LONG/SHORT/NEUTRAL), each watches one indicator. `KLUCZ`, `LEGION`, `WSKAZNIK`, `KATEGORIA`, `WAGA` attributes
- **SygnalNeuronu**: Standardized signal schema with `pewnosc`, `pewnosc_przeciwnika`, `pewnosc_finalna`, `hash_danych`, `waga`, `kierunek`, `powody`
- **4 Legiony**: Equestris (Scalp M1-M15), Fulminata (Swing 4H-1D), Augusta (Invest 1D-1W), Ferrata (Leverage)
- **12+ Special Divisions**: AI/ML, Straż (anti-manipulation), Breadth, Order Book, Arbitraż, Reżim/Makro, Sentyment, Wieloryby, Entropia, SMC/ICT, Perły, Czas/Sesje (new)
- **Generał Legatus**: Aggregates signals from 287+ neurons, classifies market regime, two modes (SKANER/FOKUS), sends RaportLegatusa to Senate
- **SKANER mode**: All neurons active, scans watchlist, finds best target (top 3)
- **FOKUS mode**: All neurons focused on one symbol
- **RaportLegatusa**: dataclass with symbol, tryb, rezim, kierunek, sila_long, sila_short, pewnosc_agregatu, aktywnych_neuronow, zgodnych_neuronow, sygnaly, weto, powod_weta
- **Kalkulator Lewara**: Must run before any leveraged position. LONG: `Entry × (1 - 1/Leverage + 0.005)`. SHORT: `Entry × (1 + 1/Leverage - 0.005)`. Stop-loss at 50% to liquidation.
- **PlanPozycji**: dataclass with cena_wejscia, dzwignia, cena_likwidacji, stop_loss, take_profit, rozmiar_usdt, ryzyko_usdt, rr_ratio, bufor_likwidacji_pct, checklist_ok
- **Dynamic leverage**: pewnosc <0.55 → 0×, <0.65 → 2×, <0.75 → 5×, <0.85 → 10×, <0.92 → 15×, ≥0.92 → 20×. Regime multipliers: VOLATILE×0.5, PANIC×0.1, RANGING×0.7, TREND_STRONG×1.2
- **Zasada 2% kapitału**: Max 2% risk per trade on any leveraged position
- **R:R minimum 1:2**: Always
- **Prawo I**: Neurons never calculate — they interpret results from Brama (TA-Lib gate)
- **Zasada Symbiozy**: No duplication, each module covers different angle
- **Katalog Strategii format**: ID (LEGION-STYL-NUM) + Neurony WEJŚCIE + Neurony FILTR + Neurony WYJŚCIE + Dźwignia + R:R + Status
- **Strategy numbering**: `[LEGION]-[STYL]-[NUM]` e.g. `X-SC-001`. Styles: TR/RV/BK/RG/SC/MC/LV/HY
- **Market Fingerprint (OdciskPalca)**: rezim, interwal, kierunek, pewnosc, funding, wolumen_vs_avg, atr_vs_avg, dominacja_btc — for auto-matching strategies
- **Druckenmiller Mode**: pewnosc >0.92 → dźwignia ×1.5, rozmiar up to 5% (exception to 2% rule)
- **Regime weights**: TREND_STRONG boosts T×1.5/M×1.2, RANGING boosts M×1.5/V×1.3, VOLATILE cuts all×0.7/boosts A×2.0, PANIC only A×3.0
- **DeepSeek API**: OpenAI-compatible, `base_url="https://api.deepseek.com/v1"`, model `deepseek-chat`
- **Koloseum/Arena rules**: 30d backtest, Sharpe >1, MaxDD <15%, WinRate >45%, min 30 trades

3. Files and Code Sections:

- **`imperium/legiony/legatus.py`** — NEW file. Generał Legatus coordinator.
  ```python
  @dataclass
  class RaportLegatusa:
      symbol: str; tryb: str; rezim: str; kierunek: str
      sila_long: float; sila_short: float; pewnosc_agregatu: float
      aktywnych_neuronow: int; zgodnych_neuronow: int
      sygnaly: List[SygnalNeuronu]
      weto: bool = False; powod_weta: str = ""
      timestamp: float = field(default_factory=time.time)

  class Legatus:
      def __init__(self, neurony, min_neuronow=5, min_przewaga=0.55)
      def fokus(self, symbol, wskazniki, rezim="NORMAL") -> RaportLegatusa
      def skaner(self, watchlista, pobierz_wskazniki, rezim) -> List[KandydatAktywa]
      def _agreguj(...) -> RaportLegatusa  # weighted sum LONG vs SHORT
      def _dostosuj_wagi(sygnaly, rezim) -> List[SygnalNeuronu]  # regime multipliers
  ```
  Import fix: `try: from .mikro_neuron import ... except ImportError: from mikro_neuron import ...`
  Demo tested ✅: BTCUSDT FOKUS → LONG 100%

- **`imperium/pretorianie/kalkulator_lewara.py`** — NEW file. Liquidation calculator.
  ```python
  OPLATA_UTRZYMANIA = 0.005  # 0.5% — Binance/MEXC standard
  MAX_RYZYKO = 0.02  # 2% capital max per trade
  MIN_RR = 2.0  # minimum Risk:Reward 1:2
  
  @dataclass
  class PlanPozycji:
      symbol, kierunek, cena_wejscia, dzwignia, cena_likwidacji
      stop_loss, take_profit, rozmiar_usdt, ryzyko_usdt, rr_ratio
      bufor_likwidacji_pct, checklist_ok, powod_veto
  
  class KalkulatorLewara:
      def policz(symbol, kierunek, cena_wejscia, dzwignia, kapital_usdt, pewnosc, rezim, pretorianie_ok) -> PlanPozycji
      def _likwidacja(cena, kierunek, dzwignia) -> float  # LONG: cena*(1-1/dz+0.005)
      def _stop_loss(cena, likwidacja, kierunek) -> float  # 50% drogi do likwidacji
      @staticmethod def auto_dzwignia(pewnosc, rezim) -> int
      def drukuj_plan(plan) -> None  # formatted box output
  ```
  Demo tested ✅: BTC LONG 10× → Plan OK, ETH SHORT auto-dźwignia 5× VOLATILE → Plan OK

- **`docs/GENERAL_LEGATUS.md`** — NEW doc. Architecture of Generał Legatus.
  - SKANER vs FOKUS modes explained with pseudocode
  - Aggregation algorithm (5 steps)
  - Regime weight table (TREND_STRONG/RANGING/VOLATILE/PANIC)
  - Minimum filter: 5+ neurons, >55% dominance, no PANIC
  - Implementation plan Faza 0→2

- **`docs/KALKULATOR_LEWARA.md`** — NEW doc. Liquidation mathematics.
  - Formulas for LONG/SHORT liquidation
  - Table: leverage 2×-50× → liquidation distance (BTC=$100K example)
  - Stop-loss placement (50% to liquidation = 50% buffer)
  - Position sizing (2% rule)
  - Dynamic leverage vs confidence table
  - 10-point Praetorian checklist
  - Full Python skeleton: `KalkulatorLewara.policz()`

- **`docs/KATALOG_STRATEGII.md`** — NEW doc, GREW substantially. ~85+ strategies total.
  - Numbering system: `[LEGION]-[STYL]-[NUM]`
  - Initial 12 strategies (Legions + world traders)
  - Section A-K: Asian Book strategies (35+ from STR-001→170)
  - Section L-R: World masters (Larry Williams, Weinstein, PTJ, Covel, Clenow, Fuller, Druckenmiller)
  - Section T-Z: Brandt, ICT, Cash&Carry, Sentiment, Bots, Elliott/Wolfe, Pairs Trading
  - Auto-matching algorithm using OdciskPalca dataclass
  - Koloseum results table

- **`docs/KATALOG_NEURONOW.md`** — MODIFIED. 261 → 274 → 287 neurons.
  - Skan II (+13): MP-01/02/03 (Market Profile), CVD-D, WR-14, PA-PINBAR/INSIDE/FAKEY, MVRV-Z, NVT-S, RHODL, MAK-COT, XII-MOM
  - Skan III (+13): PAT-01 ChartPattern, ICT-FVG, ICT-DISP, EW-01 Elliott, WW-01 Wolfe, SES-01 KillZone, SENT-FG, SENT-SOC, PAIR-01, PAIR-02, BASIS-01, CORR-01
  - New division: ⏰ Czas/Sesji (KillZone timer)

- **`docs/README.md`** — UPDATED with all new docs (GENERAL_LEGATUS, KALKULATOR_LEWARA, KATALOG_STRATEGII, updated KATALOG_NEURONOW count 287)

4. Errors and Fixes:

- **ImportError in legatus.py**: `from .mikro_neuron import ...` failed when run directly (relative import). Fixed with try/except: `try: from .mikro_neuron import ... except ImportError: from mikro_neuron import ...`
- **git pathspec error**: Running `git add docs/...` without being in repo root. Fixed by prefixing `cd /home/user/IMPERIAL-MESH-VORTEX &&`

5. Problem Solving:

- **Strategy mapping**: Applied "symbiosis principle" — only strategies that produce signals or risk rules were catalogued. Hardware (FPGA/DPDK), languages (Mojo/Zig), and execution frameworks go to ROADMAP as technical layer.
- **Asian Book parsing**: 493 lines across versions 1.0-2.0, STR-001→STR-170. Filtered: kept only strategies with signal/rule logic, excluded pure infrastructure entries.
- **Neuron deduplication**: MVRV-Z added as improved version of existing III-01 (MVRV-Ratio), noted that it uses standard deviation normalization.
- **Architecture discovery**: AgenticAITA (4 agents debating = Analyst/Risk/Executor/Scheduler) confirmed alignment with our Senate pattern. Parrondo Paradox = exact philosophy of Kameleon (alternating strategies by regime).

6. All User Messages:

- "jestes" — (context from prior session, checking in)
- "ok mam" — confirmed seeing files
- "nie mam dostepu narazie jestem w pracy" — at work
- "i jak" — checking progress
- "dawaj wiecej masz przeciesz ten plik ze wskaznikami i podzialem na kategorie" — expand neurons
- "tak kolejne neurony zgodnie z naszymi zasadami szukaj i dodawaj" — continue adding
- "dawaj po koleji wszystkie sekcje do konca zgodnie z zasadami" — scan all sections
- [Long voice-to-text message] — Tryb SKANER vs FOKUS, Generał/Legatus, dynamiczna dźwignia, Kalkulator Likwidacji, Katalog Strategii, własne wskaźniki, szukaj neurony
- "jestes" — continuing session
- "do tego co miales w pliku wskazniki tez sa strategie i znane strategie ludzi gieldy znani gracze dzialaj wszystko zgodnie z zasadami dawaj wszystko plus wyszukaj wiecej zgodnych w internecie" — integrate uploaded Asian Book + web search
- "@file do tego co miales w pliku wskazniki tez sa strategie i znane strategie ludzi gieldy znani graczee dzialaj wszystko zgodnie z zasadami dawaj wszystko plus wyszukaj wiecej zgodnych w internecie" — attach file version of same
- "pk super dalesz szukaj neurony i strategie zgodnie z naszymi zasadami dawaj wiecej" — continue searching
- "ok szukaj dalej wszystko zdodnie naszymi zasadami" — continue searching (MOST RECENT)

7. Pending Tasks:

- **Continue searching for neurons and strategies** — most recent explicit request, ongoing
- Areas NOT yet scanned:
  - Options strategies (Greeks deeper, Vanna-Volga, skew trading)
  - DeFi metrics (TVL, yield farming, liquidity mining signals)
  - Narrative/sector rotation (L1 vs L2, AI tokens, RWA)
  - ML feature engineering for trading (feature importance, SHAP)
  - Market making strategies
  - VSA — Volume Spread Analysis (Tom Williams method)
  - Jesse Stine (mega-trend momentum)
  - Tom Dante (price action pro)
  - Adam Grimes (systematic modern approach)
  - Howard Marks (market cycles + risk theory)
  - Peter Lynch (GARP — fundamental+technical hybrid)
  - Momentum factor (academic: Jegadeesh-Titman)
  - Mean reversion (academic: Poterba-Summers)
  - Breadth indicators (McClellan Oscillator, TRIN/TICK)
  - Intermarket analysis (DXY, bonds, gold vs crypto)
- **Test DeepSeek API** — when user has computer access (set DEEPSEEK_API_KEY env var)
- **Install TA-Lib** on Windows 10 (Fujitsu 8GB)
- **Await strategy file** (user may send more)
- **Implement AOA kill-switch** 30% drawdown in kalkulator_lewara.py (currently 10%)
- **Implement fractional Kelly** in position sizing
- **PR creation** — if user asks for it (current branch has all commits, no PR created yet)

8. Current Work:

Immediately before this summary request, the user said "ok szukaj dalej wszystko zgodnie naszymi zasadami" — continue searching for more neurons and strategies. The last completed work was **Skan III** which added:
- 15 new strategies (Brandt, ICT, Cash&Carry, Elliott/Wolfe, Pairs Trading, Grid/DCA/Mean Reversion, Fear&Greed, PTJ, Weinstein, Larry Williams, Clenow, Fuller, Druckenmiller)
- 13 new neurons (PAT-01, ICT-FVG, ICT-DISP, EW-01, WW-01, SES-01, SENT-FG, SENT-SOC, PAIR-01, PAIR-02, BASIS-01, CORR-01 — bringing total from 274 → **287**)
- Committed as `343a463` to branch `claude/sleepy-fermi-dsdE4`

Current catalog state:
- **287 neurons** across 17 categories (including new Czas/Sesji division)
- **~85+ strategies** in KATALOG_STRATEGII.md
- Catalog growing, 3 scan iterations completed

9. Optional Next Step:

Per user's most recent explicit request: **"ok szukaj dalej wszystko zgodnie naszymi zasadami"**

Next Skan IV should cover areas not yet searched:
- **Options metrics**: GEX deeper, put/call ratio, skew, term structure
- **Intermarket**: DXY, US10Y bonds, gold correlation signals
- **VSA** (Volume Spread Analysis — Tom Williams, better than OBV alone)
- **Breadth indicators**: McClellan Oscillator, TRIN, TICK, Advance/Decline
- **Howard Marks** — market cycle theory (risk-on/risk-off signal)
- **Sector/narrative rotation** — L1/L2/AI/DeFi/RWA rotations
- **Academic momentum factor** (Jegadeesh-Titman 12-1 month momentum)
- **DeFi-specific**: TVL, protocol revenue, staking yield spread

Each finding: map to neurons, map to strategy, follow symbiosis principle (no duplicates, only genuine signal neurons).

If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /root/.claude/projects/-home-user-IMPERIAL-MESH-VORTEX/7b169881-f787-4cf5-b192-fe119e52f190.jsonl
Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

## 🏛️ Claude
Uruchomiłem Skan IV w tle — przeszukuje VSA, breadth indicators, intermarket, opcje, DeFi, Jesse Stine, Adam Grimes. Poczekam na wyniki i zaktualizuję katalogi neuronów i strategii.

## 🧑 Cezar
<task-notification>
<task-id>a4b2f7f56fd99aa48</task-id>
<tool-use-id>toolu_01Qh561SzavXi4zNL41xmnWz</tool-use-id>
<output-file>/tmp/claude-0/-home-user-IMPERIAL-MESH-VORTEX/7b169881-f787-4cf5-b192-fe119e52f190/tasks/a4b2f7f56fd99aa48.output</output-file>
<status>completed</status>
<summary>Agent "Skan IV research - neurons and strategies" completed</summary>
<result>Perfect. Now I have comprehensive information across all the areas you requested. Let me compile this into a structured, actionable report.

---

# COMPREHENSIVE TRADING NEURON SIGNALS &amp; STRATEGIES FOR CRYPTO

## PART 1: VOLUME &amp; PRICE STRUCTURE SIGNALS

### 1. VSA (Volume Spread Analysis) - Tom Williams Method
**Core Methodology:** Pattern-based analysis of three components: volume, spread (range), price position within range

**Foundational Laws:**
- **Law of Effort vs Result:** Volume effort must match price movement result. High volume/small spread = rejection/weakness
- **Law of Supply &amp; Demand:** Rising prices + falling volume = No Demand (BEARISH). Falling prices + falling volume = No Supply (BULLISH)
- **Law of Cause &amp; Effect:** Proportional relationship between volume effort and resulting trend strength

**Specific Signals (Pattern Recognition):**

| Signal | Setup | Interpretation | Market Regime | R:R Profile |
|--------|-------|-----------------|-----------------|-------------|
| **No Supply** | Narrow spread + low volume + close in upper half during downtrend/after selloff | Sellers exhausted, reversal imminent | Oversold conditions, capitulation bottoms | 1:3 (high probability low-risk) |
| **No Demand** | Rising price + falling volume | Weak bullish move, pullback likely | Overbought rallies, distribution phases | 1:2 (fade signal) |
| **Upthrust** | Wide spread up + close in lower third + high volume above prior high | False breakout to trap buyers; short-term reversal | Resistance tests, breakout failures | 1:2 (counter-trend) |
| **Test** (Test of Supply) | Retest of prior high/low on lower volume + close in upper/lower third | Smart money accumulating, confirming trend | Accumulation zones, retests | 1:3 (high quality) |
| **Stopping Volume** | Climactic volume + wider spread + reversal candle | Capitulation, exhaustion, reversal imminent | Extremes (tops/bottoms) | 1:4 (very high probability) |
| **Shakeout** | Aggressive move through support/resistance + low volume + quick reversal back inside | Stop-hunt, weak traders flushed | Liquidation events, gap-fills | 1:2.5 |

**Calculation Notes:** VSA lacks strict mathematical formula - it's qualitative pattern recognition. Key metric: Volume against 20-period average (&gt;1.5x is notable)

**Best For:** Crypto spot trading, swing entries, support/resistance retests

**Weakness:** Subjective interpretation, requires visual analysis, difficult to backtest mechanically

Sources: [Volume Spread Analysis Stockgro](https://www.stockgro.club/blogs/trading/volume-spread-analysis/), [Algorithmic VSA PyQuantLab](https://pyquantlab.medium.com/volume-spread-analysis-vsa-strategy-quantifying-market-action-for-trading-signals-with-rolling-9aa57fb79fe9)

---

### 2. Volume Profile &amp; VPOC (Volume Point of Control)
**Calculation:** Histogram of volume traded at each price level over a time period

**Key Components:**
- **VPOC:** Price level with highest cumulative volume (fair value)
- **Value Area (VA):** Price range containing 70% of total volume
- **VAH (Value Area High):** Upper boundary of 70% volume zone
- **VAL (Value Area Low):** Lower boundary of 70% volume zone

**Signals:**

| Signal | Calculation | Setup | Threshold |
|--------|-------------|-------|-----------|
| **VAL Bounce** | Price falls to VAL, bounces back into VA | Support confirmation | Price touches VAL = LONG setup |
| **VAH Rejection** | Price rallies to VAH, rejected back into VA | Resistance confirmation | Price rejected from VAH 2x = SHORT setup |
| **Virgin POC** (High Probability Rejection) | Previous VPOC never retested | Price moves toward untested VPOC | Price within 1% of virgin VPOC = reversal zone |
| **Value Area Breakout** | Price breaks above VAH on volume | Bullish structural breakout | Volume &gt; 1.5x average + price &gt; VAH = LONG signal |
| **Value Area Breakdown** | Price breaks below VAL on volume | Bearish structural breakdown | Volume &gt; 1.5x average + price &lt; VAL = SHORT signal |

**Best For:** Range-bound markets, breakout confirmation, scalping support/resistance

**Regime:** Works best in consolidation phases, false breakout detection

Sources: [Volume Profile Trading Complete Trader's Edge](https://completetradersedge.com/volume-profile-trading-guide/), [VPOC Inflection Points](https://tradeproacademy.com/uncovering-volume-profile-inflection-points-a-complete-guide)

---

## PART 2: BREADTH &amp; MARKET STRUCTURE INDICATORS

### 3. McClellan Oscillator (Adapted for Crypto Breadth)
**Calculation:**
```
Net Advances (NA) = Advancing Coins - Declining Coins
19-day EMA(NA) = NA × 0.10 + Prior_19EMA × 0.90
39-day EMA(NA) = NA × 0.05 + Prior_39EMA × 0.95
McClellan Oscillator = 19-day EMA - 39-day EMA
```

**Signals:**

| Signal | Threshold | Interpretation | Regime |
|--------|-----------|-----------------|---------|
| **Bullish Crossover** | MO crosses above 0 from below | 19d EMA crosses 39d EMA; short-term strength &gt; intermediate | Early uptrend confirmation |
| **Extreme Bullish** | MO &gt; +600 | Overbought breadth, potential pullback coming | Top formations |
| **Extreme Bearish** | MO &lt; -600 | Oversold breadth, potential bounce coming | Bottom formations |
| **Divergence (Bullish)** | Price new low, MO higher than prior low | Breadth weakness despite price weakness | Capitulation/reversal |
| **Divergence (Bearish)** | Price new high, MO lower than prior high | Breadth weakness despite price strength | Distribution/reversal |

**Crypto Application:** Track top 40 cryptocurrencies instead of S&amp;P 500. Use as confirmation signal only (not standalone)

**Weakness:** Highly volatile in crypto, amplifies noise; works best as divergence detector

Sources: [McClellan Oscillator Wikipedia](https://en.wikipedia.org/wiki/McClellan_oscillator), [Crypto McClellan QuantifiedStrategies](https://www.quantifiedstrategies.com/mcclellan-oscillator-and-summation-index/)

---

### 4. Market Microstructure: Order Flow Imbalance &amp; VPIN
**Definition:** Ratio of informed to uninformed trading activity; measures probability of adverse selection against liquidity providers

**VPIN (Volume-Synchronized Probability of Informed Trading) Calculation:**
```
For each volume bucket (e.g., $1M notional):
Order Imbalance (OI) = |Buy Volume - Sell Volume| / Total Volume
VPIN = Sum(OI over N buckets) / N

Typical: Calculate over 1000-contract buckets, average over 100 buckets
```

**Signals:**

| Metric | Formula | Threshold | Signal |
|--------|---------|-----------|--------|
| **High VPIN** | VPIN &gt; 0.75 | High asymmetric info flow | Flash crash risk, spike imminent |
| **Low VPIN** | VPIN &lt; 0.25 | Balanced informed/uninformed | Safe liquidity zone |
| **Order Imbalance Extreme** | \|Buy Vol - Sell Vol\| / Total Vol | &gt; 0.8 | Strong directional pressure, momentum continuation |
| **VWAP Deviation** | (Last Price - VWAP) / VWAP | &gt; 1% | Pressure from large player, mean-reversion risk |
| **Trade Flow vs Order Flow** | (Executed trades) - (Pending orders) | Executed &gt; Orders | Informed traders active, follow the trade |

**Best For:** Intraday scalping, flash crash avoidance, large execution planning

**Regime:** All regimes; higher predictive power during volatile sessions

Sources: [Order Flow Toxicity Medium](https://the-kingfisher.medium.com/bitcoins-toxic-order-flow-tof-acab6b4a983a), [Explainable Patterns Cryptocurrency Microstructure arxiv](https://arxiv.org/html/2602.00776v1)

---

## PART 3: OPTIONS MARKET SIGNALS

### 5. GEX (Gamma Exposure) &amp; Dealer Hedging
**Calculation:**
```
GEX = Gamma × Open Interest × S × S × 0.01
    = Σ(Gamma_option × OI_option × Strike²) across all strikes

Positive GEX = Dealers long gamma (stabilizing, dampen volatility)
Negative GEX = Dealers short gamma (amplifying, accelerate moves)
```

**Dealer Gamma Positioning:**

| GEX Level | Dealer Posture | Market Impact | Trading Signal |
|-----------|----------------|-----------------|-----------------|
| **Positive GEX** | Long gamma (market makers) | Sellers during rallies, buyers on dips → Volatility suppression | Fade extreme moves; mean-reversion setup |
| **Negative GEX** | Short gamma (traders) | Buyers during rallies, sellers on dips → Amplification | Follow momentum; trend continuation |
| **Gamma Flip (0 level)** | Structural transition | Price level where hedging flips from stabilizing to amplifying | Critical pivot; direction breakout above/below |
| **Call Wall** | High gamma calls | Dynamic resistance; dealers force bids to prevent losses | Rejection zone, short setup |
| **Put Wall** | High gamma puts | Dynamic support; dealers force offers to prevent losses | Bounce zone, long setup |

**Gamma Bleed &amp; Expiration:**
```
Gamma Acceleration = Gamma increase as option → expiration
ATM option 1 day to expiry: Gamma ≈ 5-10x gamma at 30 days
At expiration: Gamma → infinity (discrete jump risk)

Signal: OPEX (Weekly/Monthly) + Negative GEX = Highest volatility risk
```

**Term Structure Signal:**
- **Contango (normal):** Near-term IV &lt; Long-term IV = calm market, expect vol increase
- **Backwardation (inverted):** Near-term IV &gt; Long-term IV = fear premium, expect mean-reversion

**Best For:** Swing trade entry/exit timing, expiration week hedging, volatility regime identification

**Regime:** All; most predictive during OPEX weeks and negative GEX extremes

Sources: [GEX SpotGamma](https://spotgamma.com/gamma-exposure-gex/), [Gamma Exposure Dealer Hedging](https://mottcapitalmanagement.com/gamma-exposure-gex-often-drives-short-term-market-moves/)

---

### 6. Volatility Skew (25-Delta Risk Reversal)
**Calculation:**
```
25-Delta Skew = IV(25Δ Put) - IV(25Δ Call)
Risk Reversal (RR) = IV(25Δ Put) / IV(25Δ Call)

Normalized Skew = (RR - MA(RR, 30)) / σ(RR, 30)
```

**Signals:**

| Skew Level | Calculation | Interpretation | Trade Setup |
|------------|-------------|-----------------|-------------|
| **Extreme Positive Skew** | Normalized &gt; +2 STD | Puts overpriced; downside protection expensive | SELL put spreads / Risk reversals (sell puts, buy calls) |
| **Extreme Negative Skew** | Normalized &lt; -2 STD | Calls overpriced; upside expensive relative to downside | SELL call spreads / Buy puts for asymmetric downside |
| **Flat Skew** | RR ≈ 1.0, within 1 STD | Balanced risk perception | Neutral; look for reversal to extremes |
| **Skew Spike** | RR increases 0.3+ in 1 day | Market repricing tail risk | Follow the direction: spike up = sell rally, spike down = buy dip |
| **Skew Divergence** | Price all-time high but skew extreme | Market pricing peak tail risk despite breakout | Short the breakout (false breakout signal) |

**25-Delta Choice:** Represents the "tail" of distribution; more informative than ATM skew

**Best For:** Options directional traders, tail hedge valuation, mean-reversion entries

**Regime:** Works best in ranging/consolidation; less reliable during strong directional moves

Sources: [25-Delta Skew CryptoSlate Bitcoin](https://cryptoslate.com/insights/bitcoins-options-25-delta-skew-signals-ongoing-market-anxiety-near-60000/), [Volatility Skew Risk Reversal StrikeWatch](https://www.strike-watch.com/lab/volatility-skew-25-delta-risk-reversal-directional-signal)

---

### 7. Put/Call Ratio &amp; Sentiment
**Calculation:**
```
Put/Call Ratio (Volume) = Total Put Volume / Total Call Volume
Put/Call Ratio (OI) = Total Put Open Interest / Total Call Open Interest

Normalized PCR = (PCR - MA(PCR, 20)) / σ(PCR, 20)
```

**Signals:**

| PCR Level | Threshold | Interpretation | Market Signal |
|-----------|-----------|-----------------|-----------------|
| **Extreme Call Buying** | PCR &lt; 0.5 | Bullish sentiment, complacency | Overbought; fade on strength |
| **Extreme Put Buying** | PCR &gt; 1.5 | Bearish sentiment, panic | Oversold; fade on weakness |
| **Balanced** | PCR = 0.8-1.2 | Neutral; mixed sentiment | Wait for extreme |
| **Put Spike** | PCR jumps +0.4 in 1 day | Panic buying for downside | Buy the dip (contrarian) |
| **Call Surge** | PCR drops to &lt;0.4 | FOMO call buying | Short the rally (contrarian) |

**Context:** More predictive at extremes; lagging indicator (confirm with price action)

**Best For:** Sentiment extremes detection, contrarian fades, hedging strategy

Sources: [Options metrics put call ratio analysis](https://www.gexmetrix.com/blog/volatility-analytics)

---

## PART 4: MOMENTUM &amp; TREND FACTORS

### 8. Jegadeesh-Titman 12-1 Month Cross-Sectional Momentum
**Calculation:**
```
Momentum = Return(t-12 to t-1) - Return(t-1)

For crypto basket:
1. Rank all cryptocurrencies by 12-month returns
2. Top 30% = Long portfolio (winners)
3. Bottom 30% = Short portfolio (losers)
4. Hold for 1 month
5. Rebalance monthly

Cross-Sectional Momentum = Return(Long) - Return(Short)
```

**Signals:**

| Signal | Setup | Threshold | Interpretation |
|--------|-------|-----------|-----------------|
| **Momentum Confirmation** | XCS Mom &gt; 0 for 3+ consecutive months | Price continues trending direction | LONG the top momentum cohort |
| **Momentum Reversal** | XCS Mom flips from +5% to -5% | Mean-reversion likely; losers bounce | Short the winners, long the losers |
| **Momentum Crash** | 12-mo momentum portfolio down 15%+ in 1 month | Winners capitulate; trend broken | EXIT all momentum positions |
| **Momentum Acceleration** | XCS Mom &gt; +10% | Extreme momentum conditions | Start taking profits (fade into rallies) |

**Crypto Nuance:** Traditional momentum weaker in crypto (mixed results). Recommend using 6-month instead of 12-month window (crypto more "mean-reverting" on 12m timescales)

**Best For:** Portfolio rotation, crypto theme rotation (DeFi/L1/AI sector rotation)

**Regime:** Works best in bull markets; reversed/ineffective in mean-reverting bear markets

Sources: [Cross-sectional Momentum Crypto Starkiller Capital](https://www.starkiller.capital/post/cross-sectional-momentum-in-cryptocurrency-markets), [Jegadeesh-Titman 30-year review](https://link.springer.com/article/10.1007/s11408-022-00417-8)

---

### 9. Adam Grimes Failed Breakout &amp; Pullback Momentum
**Setup (Systematic Rules):**

```
1. Identify consolidation range (swing high/low)
2. Wait for breakout above/below range on volume
3. Measure momentum: Use Modified MACD (3-10 oscillator) 
   MACD = 3-EMA - 10-EMA

Failed Breakout Signal:
- Price breaks above resistance on volume + wide spread
- WITHIN SAME BAR, reverses back inside range (spring/failure test)
- MACD does NOT make new high above prior breakout MACD level
- This = "momentum divergence" = rejection

Pullback Momentum Trade:
1. Establish strong trend (price making new highs, MACD new highs)
2. Wait for pullback (price retraces, MACD falls but stays positive)
3. MACD makes higher low (divergence: price retraces, momentum strengthens)
4. MACD crosses above prior pullback low
5. Price breaks above pullback high on volume
= LONG signal (follow direction of original trend)
```

**Signals:**

| Signal | Setup | R:R | Best Regime |
|--------|-------|-----|-------------|
| **Failed Breakout (Short)** | Spring candle + MACD divergence | 1:2 | Consolidation, resistance tests |
| **Pullback Momentum (Long)** | Trend + MACD divergence on pullback | 1:3 | Trending up |
| **Failed Pullback** | Pullback breaks down below prior low with momentum | 1:2.5 | Breakout invalidation |

**Key Rule:** ONLY take pullback trades if MACD makes new highs on the uptrend (confirms momentum direction)

**Best For:** Intraday/swing entries, trend confirmation, false breakout avoidance

**Regime:** Trending markets (90% of signal quality from trend direction)

Sources: [Adam Grimes Pullback Trading](https://www.adamhgrimes.com/trade-pullbacks/), [Adam Grimes Momentum Analysis](https://www.adamhgrimes.com/putting-momentum-work/)

---

### 10. Jesse Livermore Mega-Trend: Volume Surge &amp; Breakout
**Calculation:**
```
Livermore Signal = Volume Increase + Price Breakout + Trend Confirmation

Requirements:
1. Volume Surge: Current candle volume &gt; 10x avg(vol, 20) OR vol &gt; 3x avg
2. Price Spread: Candle range &gt; avg(range, 20) OR close at high
3. Breakout: Price breaks above pivotal point (prior high, round number, zone)
4. Confirmation: Volume increases again next candle AND price holds breakout
5. Trend: At least 5-10 candles of consolidation BEFORE breakout (cause = effect)
```

**Signals:**

| Signal | Setup | Threshold | R:R |
|--------|-------|-----------|-----|
| **Mega-Trend Start** | 10x vol + price breakout on close at high | Vol &gt; 3x avg + close &gt; prior 20 high | 1:4+ |
| **Pivotal Point Breakout** | Price breaks above key resistance (prior swing high, round number like $50k) on volume | Vol &gt; 2x avg + price &gt; prior high | 1:3 |
| **Trend Continuation** | New pullback low, volume dries up, price rallies above pullback high on vol surge | Vol &gt; 1.5x avg | 1:2.5 |
| **Trend Exhaustion** | Climactic volume bar (20x avg) + price breakout followed by reversal next bar | Vol &gt; 10x avg on reversal = opposite signal | 1:1.5 (fade) |

**Key Insight:** The CAUSE (long consolidation + low volume) comes before EFFECT (explosive breakout on volume). Lookback period = consolidation period

**Best For:** Swing entries, major trend starts, breakout above year-highs

**Regime:** All; most powerful at round numbers and macro support/resistance zones

Sources: [Jesse Livermore Trading Strategy QuantifiedStrategies](https://www.quantifiedstrategies.com/jesse-livermore-trading-strategy-backtest-and-performance/), [Crypto Swing Trading Livermore Method](https://medium.com/coinmonks/crypto-swing-trading-like-jesse-livermore-2eb1ec72ac66)

---

## PART 5: INTERMARKET &amp; MACRO SIGNALS

### 11. DXY (US Dollar Index) vs Crypto Correlation
**Calculation:**
```
DXY = US Dollar strength index (basket of 6 major currencies)
Correlation(BTC, DXY) = Pearson correlation(BTC returns, DXY returns) over rolling 30-day window

Signal = Correlation * DXY momentum
```

**Signals:**

| Condition | Correlation | DXY Move | Crypto Signal | Confidence |
|-----------|-------------|----------|---------------|------------|
| **Negative Correlation** | r = -0.6 to -0.8 | DXY rising (+2%+ per week) | BTC bearish; reduce longs | High (traditional regime) |
| **Positive Correlation** | r = +0.4 to +0.8 | DXY rising BUT BTC rising | BTC bullish; strong dollar = inflows | Very High (2026 ETF era) |
| **Correlation Flip** | |r| crosses 0 in 20d window | Structural regime change | Beware of whipsaws; reduce position size | Medium (2-3 week lag) |
| **DXY Extreme** | DXY &gt; 105 or &lt; 95 | Extreme valuation | Crypto likely at opposite extreme | High |
| **Risk-Off Signal** | DXY rising + credit spreads widening | Liquidity crunch | Both DXY and crypto sell-off likely | Very High |

**2026 Update:** Historical inverse correlation weakened; Bitcoin now trades like risk-on asset (moves with stocks) alongside institutional ETF inflows. Monitor DXY as macro backdrop, not primary driver.

**Best For:** Macro regime identification, correlation breakdownbeta hedge, macro portfolio construction

Sources: [DXY Bitcoin Correlation Analysis OSL 2026](https://www.osl.com/hk-en/academy/article/the-us-dollar-index-vs-bitcoin-why-the-inverse-correlation-matters), [Bitcoin vs DXY MacroMicro](https://en.macromicro.me/charts/84646/BITCOIN-vs-US-DOLLAR-INDEX-DXY)

---

### 12. Howard Marks Market Cycle Theory - Dumb Money Entry Signals
**Framework:** Market cycles move from undervaluation → overvaluation across 4 phases

**Signals (Contrarian Indicators of Cycle Position):**

| Cycle Phase | Signal | Setup | Action |
|-------------|--------|-------|--------|
| **Phase 1: Capitulation/Panic (Cycle Bottom)** | "Greatest risk is belief there's no risk" reversal → "Only risk is panic" | Extreme pessimism: All media bearish, short volume &gt; long, fear index extreme (VIX-equiv &gt; 70), weak hands selling at losses | **ACCUMULATE** (highest conviction longs) |
| **Phase 2: Recovery (Smart Money Enters)** | Price rising but sentiment still negative; "smart money getting in while dumb money exiting" | Price up 30%+, technical breakouts, but retail still fearful; low retail inflows; high shorts capitulating | **CONTINUE LONGS**, add on pullbacks |
| **Phase 3: Prosperity (Momentum Crowd Enters = DUMB MONEY)** | "Widespread risk tolerance is greatest harbinger of declines" | Retail FOMO, media euphoria, every retail trader bullish, valuations stretched, easy money in trend | **REDUCE EXPOSURE**, start taking profits |
| **Phase 4: Excess (Cycle Top)** | "New intoxicating rationale that can't be justified on fundamentals" | Irrational valuations (BTC at 20x GDP, shitcoin P/E infinite), leverage maxed, margin calls pending, no skeptics left | **HEDGE / EXIT**, go defensive |

**Specific "Dumb Money" Entry Signals:**
```
Dumb Money Score = 
  0.3 × (Retail Call/Put Ratio - 30d MA) / σ 
  + 0.2 × (Retail Flows % of total / 30d MA)
  + 0.25 × (1 - Media Bearish Mentions / Total Mentions) 
  + 0.25 × (Risk Appetite Index - 50d MA)

If Dumb Money Score &gt; +2.0 STD = Peak euphoria = SHORT setup
If Dumb Money Score &lt; -2.0 STD = Peak panic = LONG setup
```

**Best For:** Macro portfolio positioning, 3-6 month timeframe, limiting losses at tops

**Regime:** Works in cyclical assets (crypto, tech, growth); less effective in defensive sectors

Sources: [Mastering Market Cycle Howard Marks Novel Investor](https://novelinvestor.com/notes/mastering-the-market-cycle-by-howard-marks/), [Howard Marks GuroFocus](https://www.gurufocus.com/news/834361/howard-marks-where-in-the-cycle-are-we)

---

## PART 6: DEFI-SPECIFIC SIGNALS

### 13. TVL Velocity &amp; Protocol Revenue Momentum
**Calculation:**
```
TVL Velocity = (Current TVL - TVL 30 days ago) / TVL 30 days ago
Protocol Revenue Momentum = (Revenue Last 7d - Revenue Prev 7d) / Revenue Prev 7d
TVL Inflection = TVL(t) &gt; SMA(TVL, 30) AND TVL slope positive for 3+ days
```

**Signals:**

| Signal | Formula | Threshold | Interpretation | Action |
|--------|---------|-----------|-----------------|--------|
| **TVL Acceleration** | Velocity &gt; +10% / week | Sustained inflows &gt; 2 weeks | Protocol gaining traction; capital influx | **LONG token** (fundamental strength) |
| **TVL Reversal** | Velocity flips from +5% to -5% | 3-day ma TVL crosses below 30d ma | Capital rotation out; protocol losing appeal | **REDUCE / SHORT token** |
| **Revenue Explosion** | Week-over-week revenue &gt; +30% | Sustainable &gt; 2 weeks | Fee-generating protocol; real utilization | **LONG on fundamentals** + look for TVL follow-on |
| **Revenue Decline** | Week-over-week revenue &lt; -20% | If &gt; 2 weeks = trend | Protocol economics deteriorating | **SHORT or neutral** |
| **Stablecoin Inflow** | Stablecoin TVL on chain rising | Rising % of total TVL to 60%+ | Risk-on sentiment; yield farming mode | Expect TVL-driven price moves |
| **Bridge Anomaly** | Unusual bridge activity (deposits/withdrawals) | 5x normal flow in 1 hour | Whale movement; either accumulation or exodus | Confirm with social signals |

**Market Structure:** TVL changes 1-2 weeks before token price typically reflects. Monitor as leading indicator.

**Best For:** DeFi protocol rotation, L1 selection (which chain's TVL growing), yield farming risk assessment

**Regime:** Works best in DeFi seasons (bull market crypto); less effective in bear markets

Sources: [DefiLlama TVL Protocol Revenue 2026](https://www.dextools.io/tutorials/how-to-use-defillama-defi-tvl-stablecoin-revenue-tutorial-2026), [DeFi Market Stats PatentPC](https://patentpc.com/blog/defi-market-stats-tvl-protocol-growth-user-trends)

---

### 14. Staking Yield Spread vs Lending Rates
**Calculation:**
```
Staking Yield Spread = Staking Reward Rate - Lending Rate (borrowed rate)
Yield Curve Slope = Rate(30d) - Rate(90d)

Spread Signal = (Spread - MA(Spread, 30)) / σ(Spread, 30)
```

**Signals:**

| Signal | Formula | Threshold | Interpretation |
|--------|---------|-----------|-----------------|
| **Attractive Yield** | Staking &gt; Lending by 5%+ | Spread &gt; 5% APR | Staking becoming competitive; capital attracted |
| **Yield Compression** | Spread falling from 10% to 2% | Week-over-week decline &gt; 2% | Oversupply of staked capital; yields declining |
| **Inverted Yield Curve** | Short-term rates &gt; Long-term rates | 30d yield &gt; 90d | Extreme risk perception; expect reversion |
| **Yield Blowout** | Staking rate spikes (new protocol incentive) | Rate jumps +20%+ in 1 week | Mercenary capital inflow; watch for outflow rug-pull |
| **Normalized Yield** | Spread within historical MA | Between +3% to +8% | Healthy state; sustainable yields |

**Context:** High yields attract capital but unsustainable incentive-driven yields reverse sharply. Monitor protocol emissions schedule.

**Best For:** DeFi protocol selection, liquid staking token evaluation, yield farming timing

Sources: [Forecasting Cryptocurrency Staking Rewards arxiv](https://arxiv.org/pdf/2401.10931)

---

## PART 7: SECTOR ROTATION &amp; NARRATIVE SIGNALS

### 15. L1 vs L2 Relative Strength Rotation
**Calculation:**
```
RS(L1) = SMA(L1 Index Price, 20) / SMA(L2 Index Price, 20)
RS(AI) = SMA(AI Token Index, 20) / SMA(DeFi Index, 20)

Rotation Signal = RS &gt; prior 20-day high OR RS &lt; prior 20-day low
```

**Signals:**

| Narrative Pair | RS Condition | Interpretation | Setup |
|----------------|-------------|-----------------|-------|
| **L1 Leadership** | Solana/Polygon outperforming Ethereum | L1 growth &gt; L2 scaling gains | **LONG SOL/AVAX, SHORT ARB/OP** |
| **L2 Dominance** | Arbitrum/Optimism outperforming mainnet L1s | Layer 2 adoption accelerating; gas arbitrage | **SHORT Solana, LONG Arbitrum** |
| **AI Sector Outperformance** | AI tokens (RNDR, TAO, FET) outperforming DeFi | Narrative rotation to AI compute | **LONG AI cohort**, rotate out of DeFi |
| **DeFi Revival** | DeFi tokens (AAVE, UNI, CRV) breaking out vs AI | Yield farming renewed interest | **LONG DeFi**, reduce AI exposure |
| **Rotation Extreme** | RS at 2 STD from 50-day MA | Mean-reversion likely | **Fade the extreme, go opposite** |

**Narrative Tracker:** 22 tracked narratives (L1, L2, DeFi, AI, RWA, etc.); data refreshes every 30 minutes

**Best For:** Portfolio rotation, sector hedges, relative strength trades

**Regime:** Bull markets; narrative rotation increases in risk-on sentiment

Sources: [Crypto Narratives Sharpe Terminal](https://www.sharpe.ai/products/narratives), [L1 L2 Rotation CoinGecko 2026](https://www.coingecko.com/learn/crypto-narratives)

---

### 16. Bid-Ask Spread as Volatility &amp; Liquidity Signal
**Calculation:**
```
Spread = Ask Price - Bid Price
Spread % = Spread / Midprice × 100

Spread Normalization = (Spread - SMA(Spread, 20)) / σ(Spread, 20)
Spread Momentum = SMA(Spread, 5) - SMA(Spread, 20)
```

**Signals:**

| Signal | Formula | Threshold | Interpretation | Trade Setup |
|--------|---------|-----------|-----------------|-------------|
| **Spread Widening** | Spread % &gt; +2 STD from 20d MA | Spread doubles | Volatility spike; liquidity drying | Reduce position size; avoid scalping |
| **Spread Collapse** | Spread % &lt; -2 STD from 20d MA | Spread &lt;50% average | High liquidity; confidence phase | **Increase position size** |
| **Spread Reversal** | Spread momentum flips + negative | Spread falling 5 candles straight | Reversal likely (false spike) | **Fade the reversal attempt** |
| **Pre-Event Widening** | Spread rises + volume falls | 30 min before news release | Expected volatility; market making risk | **HOLD (don't trade into event)** |
| **Post-Crash Spread** | Spread spikes then collapses in 1 hour | Spread widens then normalizes | Liquidity returned; momentum exhausted | **Contrarian: BUY after crash** |

**Context:** Crypto spreads wider than equities; Binance/FTX much tighter than DEX

**Best For:** Intraday scalping, risk management, position sizing, event trading

**Regime:** All; more pronounced in volatile regimes

Sources: [Bid-Ask Spread Volatility OptionalAlpha](https://optionalpha.com/blog/bid-ask-spread-volatility), [Bid-Ask Spread Market Microstructure DayTraderBusiness](https://www.daytraderbusiness.com/advanced/market-microstructure/how-bid-ask-spread-changes-can-signal-trading-opportunities)

---

## IMPLEMENTATION FRAMEWORK: "MICRO-NEURON" ARCHITECTURE

Each signal above is a **single-purpose neuron** that outputs: `LONG / SHORT / NEUTRAL`

**Suggested Neuron Groupings:**

```
TIER 1 (Primary Direction):
├─ Neuron_VSA (pattern recognition)
├─ Neuron_McClellan (breadth strength)
├─ Neuron_OrderFlow (microstructure pressure)
└─ Neuron_Momentum_12m1m (cross-sectional factor)

TIER 2 (Confirmation/Timing):
├─ Neuron_FailedBreakout (Grimes rejection signal)
├─ Neuron_VolumeProfile_VAL_VAH (support/resistance)
├─ Neuron_GEX_Dealer (options dealer positioning)
└─ Neuron_VPIN_Toxicity (informed trading detection)

TIER 3 (Regime &amp; Context):
├─ Neuron_HowardMarks_Cycle (macro sentiment)
├─ Neuron_DXY_Correlation (macro backdrop)
├─ Neuron_TVL_Velocity (DeFi health)
└─ Neuron_Spread_Widening (volatility regime)

TIER 4 (Sector Rotation):
├─ Neuron_L1_L2_RS (narrative rotation)
├─ Neuron_Volatility_Skew (tail risk)
└─ Neuron_Put_Call_Ratio (sentiment)

VOTING MECHANISM:
1. Count LONG signals across all neurons
2. Count SHORT signals
3. Threshold: If LONG &gt; SHORT + buffer (e.g., 2), output LONG
   If SHORT &gt; LONG + buffer, output SHORT
   If tied/balanced, output NEUTRAL
4. Confidence = (LONG - SHORT) / Total neurons

Suggested buffer for crypto: 3-4 signals (crypto is noisier than stocks)
```

---

## MARKET REGIME MATRIX

| Signal | Bull Trend | Bear Trend | Range/Consolidation |
|--------|-----------|-----------|----------------------|
| **VSA** | Favor "No Supply" longs | Favor "Upthrust" fades | All signals useful (VPOC context) |
| **McClellan** | MO &gt; 0 means continuation | MO &lt; 0 means continuation | MO extremes most useful |
| **Order Flow** | VPIN &lt; 0.5 usually safe | VPIN &gt; 0.75 heightens risk | OI imbalance predicts breakout direction |
| **GEX** | Positive GEX suppresses rallies | Negative GEX accelerates declines | Gamma flip = key reversal level |
| **Momentum** | 12m1m positive trend following | 12m1m negative mean-reversion | Reversals strongest in consolidation |
| **Volume Profile** | VAH rejection, VAL bounce | VAL penetration decisive | VPOC acts as magnet |
| **DXY** | Weak dollar supports BTC | Strong dollar pressures BTC | Monitor for regime flip |
| **Howard Marks** | Don't chase late-stage bull | Accumulate on capitulation | Identify cycle inflection |
| **TVL Velocity** | Positive = bullish bias | Negative = defensive | Monitor for 3-week inflection |
| **Bid-Ask Spread** | Tight = good execution | Widens = stop losses tighter | Monitor for event risk |

---

## CRYPTO-SPECIFIC CALIBRATION

**Why Standard Signals Need Adjustment for Crypto:**

1. **Higher Volatility:** VPIN thresholds should be 0.70+ vs 0.60+ for equities; GEX gamma flip more pronounced
2. **Retail Dominance:** Howard Marks cycle signals work but 2-3x faster amplitude; dumb money enters/exits quicker
3. **24/7 Market:** No pre-market setup time; signals layer across multiple timeframes continuously
4. **Leverage + Liquidations:** Order flow microstructure changes during cascade events; spread widens &gt;10x
5. **Narrative Rotation:** Much faster (weeks vs months in equities); L1/L2/AI rotation resets 4-6x per year
6. **DeFi Flash:** Protocol revenue spikes/crashes within days; TVL shifts overnight on hack rumors
7. **Options Skew:** Bitcoin 25-delta skew more extreme (-0.5 to +0.5 vs -0.2 to +0.2 in equities)

**Confidence Modifiers:**

- **BTC/ETH:** Higher confidence on all signals (liquid, established patterns)
- **Mid-cap Altcoins:** 30-40% confidence reduction (thinner order books)
- **Microcaps/Shitcoins:** Do not use (order flow unreliable, manipulation risk)
- **OPEX Weeks:** Increase GEX signal weight 3x; decrease momentum signal weight
- **Post-Hack/FUD:** All signals unreliable for 48h; reset technical levels

---

## SUMMARY: ACTIONABLE SIGNAL CHECKLIST

For a **SINGLE-PURPOSE MICRO-NEURON**, choose from:

| Neuron Name | Calculation Complexity | Data Needs | Crypto Optimization | R:R | Regime |
|-------------|----------------------|-----------|---------------------|-----|---------|
| VSA_NoSupply | Low (visual pattern) | OHLCV + 20-SMA | Direct | 1:3 | Capitulation |
| OrderFlow_VPIN_Toxicity | Medium (volume buckets) | Taker/maker trades | Direct | 1:2 | All |
| GEX_DealerFlip | Medium (gamma calc) | Options chain data | Direct | 1:2.5 | OPEX weeks |
| Skew_25D_Extreme | Low (IV ratio) | Options IV surface | Direct | 1:2 | Range/Reversion |
| Momentum_12m1m | Low (ranking) | 12-month returns | Modify to 6-month | 1:2.5 | Bull/Early Bear |
| FailedBreakout_Grimes | Low (pattern + MACD) | OHLCV + MACD | Direct | 1:2 | Trending |
| TVL_Velocity | Low (% change) | Protocol TVL data | Direct | 1:2 | Bull/DeFi season |
| L1_L2_RS | Low (ratio/RS index) | Protocol TVL data | Direct | 1:1.5 | Narrative rotation |
| BidAsk_Volatility | Low (spread ratio) | Order book best bid/ask | Direct | 1:1 | All |
| HowardMarks_Dumb_Money | Medium (composite score) | News sentiment + flows | Adjust for 2x speed | 1:3 | Cycle extremes |

**Recommended Starting Implementation:** 3 neurons
1. **Trend Core:** VSA_NoSupply OR Momentum_12m1m (pick one)
2. **Confirmation:** FailedBreakout_Grimes OR GEX_DealerFlip
3. **Context:** TVL_Velocity (if DeFi focused) OR DXY_Correlation (if macro focused)

**Upgrade Path:** Add neurons one at a time; track correlation with existing neurons to avoid redundancy.

---

**Sources Summary:**

- [Volume Spread Analysis Stockgro](https://www.stockgro.club/blogs/trading/volume-spread-analysis/)
- [Algorithmic VSA Medium](https://pyquantlab.medium.com/volume-spread-analysis-vsa-strategy-quantifying-market-action-for-trading-signals-with-rolling-9aa57fb79fe9)
- [Volume Profile Trading Complete Trader's Edge](https://completetradersedge.com/volume-profile-trading-guide/)
- [McClellan Oscillator QuantifiedStrategies](https://www.quantifiedstrategies.com/mcclellan-oscillator-and-summation-index/)
- [Order Flow Toxicity Medium](https://the-kingfisher.medium.com/bitcoins-toxic-order-flow-tof-acab6b4a983a)
- [Explainable Patterns Cryptocurrency Microstructure arxiv](https://arxiv.org/html/2602.00776v1)
- [GEX Dealer Hedging Mott Capital](https://mottcapitalmanagement.com/gamma-exposure-gex-often-drives-short-term-market-moves/)
- [Volatility Skew 25-Delta StrikeWatch](https://www.strike-watch.com/lab/volatility-skew-25-delta-risk-reversal-directional-signal)
- [Cross-sectional Momentum Starkiller Capital](https://www.starkiller.capital/post/cross-sectional-momentum-in-cryptocurrency-markets)
- [Adam Grimes Pullback Trading](https://www.adamhgrimes.com/trade-pullbacks/)
- [Jesse Livermore Strategy QuantifiedStrategies](https://www.quantifiedstrategies.com/jesse-livermore-trading-strategy-backtest-and-performance/)
- [DXY Bitcoin Correlation OSL 2026](https://www.osl.com/hk-en/academy/article/the-us-dollar-index-vs-bitcoin-why-the-inverse-correlation-matters)
- [Howard Marks Cycle Novel Investor](https://novelinvestor.com/notes/mastering-the-market-cycle-by-howard-marks/)
- [DefiLlama TVL 2026 Tutorial](https://www.dextools.io/tutorials/how-to-use-defillama-defi-tvl-stablecoin-revenue-tutorial-2026)
- [Crypto Narratives Rotation Sharpe Terminal](https://www.sharpe.ai/products/narratives)
- [Bid-Ask Spread Volatility Signal OptionalAlpha](https://optionalpha.com/blog/bid-ask-spread-volatility)</result>
<usage><subagent_tokens>44700</subagent_tokens><tool_uses>28</tool_uses><duration_ms>168328</duration_ms></usage>
</task-notification>

## 🏛️ Claude
You've hit your session limit · resets 6:40am (UTC)
