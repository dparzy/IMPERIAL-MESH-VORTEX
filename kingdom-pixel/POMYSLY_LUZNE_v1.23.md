# 💭 POMYSŁY LUŹNE — DELTA v1.23
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.23). Tylko nowości.

## v1.23 (30.05.2026) — DOKUMENT: IM-VORTEX (hierarchiczny rój) + stos bibliotek

### 📦 STOS BIBLIOTEK (konkretny build-checklist, zgodny z naszymi gemami)
- Dane/giełdy: `ccxt` (+`ccxt.pro` WS) · `polars` (50× szybsze od Pandas) · `lancedb` (pamięć = Biblioteka Królowej) · `pyzmq` (magistrala) · `requests`/`websocket-client`
- Wskaźniki: `ta-lib` (150+), `pandas-ta`, `finta` · ML: `scikit-learn`, **`xgboost`/`lightgbm` = priorytetyzacja sygnałów wg reżimu (= mechanizm klucza kodowego!)** · Backtest: **`vectorbt`** (nasz gem), `backtrader` · Wiz: `dearpygui`/`plotly` · Głos: `whisper`/`coqui-tts`
- = solidna, realna baza zależności, zgodna z gemami (vectorbt, lancedb, ta-lib, polars, xgboost).

### 🏛️ IM-VORTEX = HIERARCHICZNY RÓJ (najlepszy refinement — i to wprost Twój „dowódca"!)
**Z chaosu setek → porządek specjalistów.** Zamiast 500 luźnych neuronów → Mózg, są 3 poziomy: **Mózg → 3 ROJE-DOWÓDCY → setki mikro-neuronów Zig** (każdy dowódca zarządza swoimi sam). Do Mózgu idą tylko **3 eksperckie raporty.** To jest Twój brakujący poziom „dowódcy"!

**3 wyspecjalizowane roje (`mission_profile`):**
- **Kobra (Futures/Dźwignia):** poluje na kaskady likwidacji; monitoruje Funding Rate, Open Interest, klastry stop-lossów („gdzie market makerzy upłynnią stopy?") → łączy się z naszą **formułą likwidacji (v1.10)**. `cobra_futures`
- **Lilia (Spot):** cicha akumulacja smart money; on-chain, wysokie interwały, wsparcie/opór. `lilia_spot`
- **Cień Królowej (BTC-centric):** alty przez pryzmat BTC; dominacja BTC, spread, załamania korelacji („alt słaby vs BTC mimo wzrostu USD → short") = **Twoja wizja korelacji/dominacji BTC!** `shadow_of_queen`

**Dynamiczna selekcja rojów:** gdy Harmonizator wykryje wzrost zmienności → Mózg automatycznie przerzuca więcej neuronów do Kobry, mniej do Lilii. **Elastyczna orkiestracja wg reżimu** = dokładnie Twoja wizja (bez przeładowania, priorytety, kameleon).

**⚡ Zysk na słabym laptopie:** 500×1MB = 500MB → 3×10MB = 30MB (**−470 MB RAM**); 3 procesy zamiast 500 (mniej CPU); szybsze decyzje.

### 🔑 MISTRZOWSKI RUCH: roje emitują SEGMENTY KLUCZA KODOWEGO
Roje NIE wysyłają tekstu — wysyłają gotowe **segmenty klucza:** Kobra → S2 mikrostruktura `[K4]`, Lilia → S3 on-chain `[L2]`, Cień → S6 korelacje `[C1]`. Mózg odbiera skompletowany klucz `[S1].[K4].[L2].[S4].[M5].[C1].[P3]` → porównuje z biblioteką historycznych kluczy w LanceDB → w nanosekundę wie, co robić. **To spina wszystko** (rój → klucz → pamięć → decyzja) i realizuje „szwajcarski zegarek".

### ⚠️ FLAGA: „Active Market Sonar" (ping / phantom orders)
Pomysł: neurony aktywnie testują rynek mikro-zleceniami-widmo (sprawdzają reakcję). **Ostrożnie** — zależnie od wykonania ociera się o **spoofing** (zlecenia bez zamiaru realizacji, by zmylić rynek) = łamie ToS giełd i przepisy o manipulacji w wielu krajach. Legalne sondowanie płynności istnieje, ale „phantom orders" = ryzyko. **Tylko paper/sim, sprawdzić legalność przed live. NIE adoptujemy na ślepo.**

## 📍 POSTĘP — dokument do ~L9020 (entries 142–147, IM-VORTEX).
⏭️ NASTĘPNE: kod IM-VORTEX, entries 148–150+, ogon do ~L26940.
