# 🏛️ MKS — Mikrostruktura Rynku | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐ (wysoki — filar zwiadowców EXP)
> **Dla nowicjusza (ZPO):** mikrostruktura to „anatomia" rynku — JAK powstaje cena z
> pojedynczych zleceń, kto handluje (informed vs noise), jak przepływ zleceń pcha cenę.
> To poziom poniżej świec — tu kryje się przewaga, której nie widać na wykresie.

## 📑 SPIS TREŚCI
1. [Księga zleceń i przepływ](#1-księga-i-przepływ)
2. [Modele teoretyczne](#2-modele)
3. [Kyle's Lambda (impact)](#3-kyles-lambda)
4. [PIN (informed trading)](#4-pin)
5. [CVD i order flow](#5-cvd)
6. [Wpływ na Imperium](#6-wpływ-na-imperium)
7. [Źródła](#7-źródła)

---

## 1. KSIĘGA I PRZEPŁYW

| Pojęcie | Co znaczy | Sygnał |
|---------|-----------|--------|
| **Bid/Ask spread** | różnica kupno/sprzedaż | wąski = płynny, szeroki = ryzyko/illikwidność |
| **Depth (głębokość)** | wolumen na poziomach księgi | cienka księga = łatwy impact |
| **Order flow imbalance** | przewaga kupna/sprzedaży | predyktor krótkoterminowy |
| **Market vs limit order** | agresor (bierze) vs pasywny (daje płynność) | agresja = informed flow |
| **Tick rule** | klasyfikacja buy/sell po kierunku ceny | proxy gdy brak danych o stronie |

---

## 2. MODELE (O'Hara, BIB-032)

- **Glosten-Milgrom:** spread istnieje, bo market maker chroni się przed informed traders.
  Im więcej informed, tym szerszy spread.
- **Kyle (1985):** informed trader handluje tak, by nie zdradzić informacji; cena porusza
  się liniowo z przepływem netto → **λ (lambda) = miara impactu/illikwidności**.
- **Easley-O'Hara (PIN):** szacuje prawdopodobieństwo, że dana transakcja pochodzi od
  informed tradera.

---

## 3. KYLE'S LAMBDA (EXP-14)

**Definicja:** λ = nachylenie regresji Δcena ~ przepływ_netto. Wysokie λ = mały przepływ
mocno rusza ceną = illikwidność / obecność informed flow.

**Status w Imperium (EXP-14):** ✅ aktywny, ale **werdykt backward-IC (2026-06-21): to
miara STANU płynności, nie predyktor kierunku.** IC~0.30 było echem reżimu. Stosować jako:
- adaptacyjny próg (ratio = bieżący impact / mediana — bezwymiarowy, skaluje do każdej pary)
- **filtr reżimu mikrostruktury**: wysoki λ → księga cienka → wchodź ostrożnie, szerszy SL

---

## 4. PIN (EXP-15)

**PIN (Probability of Informed Trading):** odsetek przepływu pochodzącego od informed traderów.

**Status w Imperium (EXP-15):** ⚠️ **wyciszony (DOSTEPNY=False)** — zmierzony jako martwy
na danych OHLCV. PIN to zjawisko tick-level; uśrednianie OHLCV niszczy asymetrię buy/sell
(mean_buy≈mean_sell → PIN≈0, aktywacja 0.1% czasu). **Ożyje z feedem aggTrades** (jak EXP-12 z L2).
To uczciwy przykład Prawa XV: moduł gotowy, ale bez właściwych danych = martwy głos → wyciszony.

---

## 5. CVD I ORDER FLOW

- **CVD (Cumulative Volume Delta):** skumulowana różnica wolumenu agresywnego kupna i sprzedaży.
  Dywergencja CVD vs cena = sygnał wyczerpania trendu.
- **Status (V-03):** ⏳ czeka na AdapterCVD / trade-feed.
- **Footprint / delta:** wolumen po stronie bid/ask na każdym poziomie — granularny order flow.

---

## 6. WPŁYW NA IMPERIUM

### Zwiadowcy mikrostruktury:
| Moduł | Co robi | Status |
|-------|---------|--------|
| EXP-12 (L2 order book) | sygnał z głębokości księgi | ⚠️ wyciszony (brak L2 feed) |
| EXP-14 (Kyle's λ) | impact/illikwidność | ✅ aktywny — **jako filtr reżimu** |
| EXP-15 (PIN) | informed trading | ⚠️ wyciszony (brak tick feed) |
| V-03 (CVD) | volume delta | ⏳ czeka na feed |
| Engle-Granger | kointegracja par (stat-arb) | ✅ mikrostruktura.py |

### 🚨 Prawo XV — co odblokuje feed:
- **Binance aggTrades** (DARMOWE) → ożywia V-03 CVD, częściowo EXP-15 PIN
- **Binance depth/L2 WebSocket** → ożywia EXP-12
- To trzy gotowe moduły czekające tylko na dane — najtańszy skok jakości mikrostruktury.

---

## 7. ŹRÓDŁA
- BIB-032 O'Hara — *Market Microstructure Theory* (kanon)
- BIB-020 Harris — *Trading and Exchanges* (praktyka)
- BIB-027 Aldridge — *High-Frequency Trading*
- BIB-022 Kissell — *Optimal Trading Strategies* (impact)
- Powiązane: **LEW**, **ALG**, **RSK**
