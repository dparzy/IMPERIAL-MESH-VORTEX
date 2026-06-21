# 🏛️ RSK — Zarządzanie Ryzykiem | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐⭐ (krytyczny — to fundament przetrwania)
> **Dla nowicjusza (ZPO):** zarządzanie ryzykiem to NIE „jak zarobić", lecz „jak NIE
> stracić wszystkiego". 90% traderów upada nie przez złe wejścia, lecz przez brak kontroli
> straty. Pierwsza zasada: przetrwać, by móc grać dalej. Druga: patrz na zasadę pierwszą.

## 📑 SPIS TREŚCI
1. [Hierarchia ryzyka](#1-hierarchia-ryzyka)
2. [Sizing — matematyka przetrwania](#2-sizing)
3. [Stop-loss i wyjścia](#3-stop-loss)
4. [Ryzyko portfelowe](#4-ryzyko-portfelowe)
5. [Ogony i czarne łabędzie](#5-ogony)
6. [Metryki walidacji (DSR/PBO)](#6-metryki)
7. [Wpływ na Imperium](#7-wpływ-na-imperium)
8. [Źródła](#8-źródła)

---

## 1. HIERARCHIA RYZYKA

| Poziom | Ryzyko | Obrona |
|--------|--------|--------|
| Transakcja | strata na jednym wejściu | SL, stały % ryzyka |
| Dzień/seria | seria strat z rzędu | Reguła 6% / HALT dzienny |
| Portfel | skorelowane straty wielu pozycji | limit ekspozycji, dekorelacja |
| Konto | ruina (drawdown nie do odrobienia) | twardy limit DD, kill-switch |
| Systemowy | flash crash, cascade, exchange risk | hedge, dywersyfikacja giełd |

**Matematyka ruiny:** strata 50% wymaga +100% by odrobić; strata 90% → +900%. Im głębszy
DD, tym wykładniczo trudniej wrócić. Dlatego **ochrona DD > maksymalizacja zysku**.

---

## 2. SIZING

### Reguła stałego ryzyka (fundament)
```
rozmiar_pozycji = (kapitał × %ryzyka_na_transakcję) / dystans_do_SL [%]
```
- Standard: 1-2% ryzyka na transakcję. Konserwatywnie: 0.5%.
- Lewar jest POCHODNĄ sizingu, nie celem (patrz dział LEW).

### Kelly Criterion (Ed Thorp)
```
f* = edge / odds = (p·b − q) / b
```
gdzie p=prawdopodobieństwo wygranej, q=1−p, b=stosunek zysk/strata.
- Pełny Kelly jest zbyt agresywny (wysoka wariancja) → praktyka: **½ Kelly lub ¼ Kelly**.
- Wymaga ZNANEGO edge'u — przy niepewnym edge przeszacowanie Kelly = ruina.

### Volatility targeting
Skaluj pozycję odwrotnie do zmienności: wysoka zmienność → mniejsza pozycja.
**Tu EXP-13 (GARCH) ma realne zastosowanie** jako estymator reżimu zmienności (werdykt backward-IC).

---

## 3. STOP-LOSS

| Typ SL | Kiedy | Uwaga |
|--------|-------|-------|
| Stały % | proste setupy | nie na okrągłych liczbach (stop hunt) |
| ATR-based | dostosowany do zmienności | SL = entry − k·ATR |
| Strukturalny | pod swing low / poziom | logiczny, ale szerszy |
| Trailing | trend-following | „pozwól zyskom rosnąć" (Seykota) |
| Czasowy | brak ruchu w X barów → wyjście | kapitał nie powinien stać martwy |

**Zasada:** SL ustalony PRZED wejściem, nie przesuwany pod stratę („nadzieja" zabija konto).

---

## 4. RYZYKO PORTFELOWE

- **Korelacja zabija dywersyfikację:** 10 altów to często 1 zakład na BTC (w stresie korelacje → 1).
- **Limit ekspozycji łącznej:** suma ryzyka otwartych pozycji ≤ próg (np. 6% konta).
- **HRP (Hierarchical Risk Parity, López de Prado)** — alokacja po klastrach korelacji
  zamiast naiwnego 1/N czy niestabilnego Markowitza. **W Imperium: `denoising_macierzy.hrp_wagi`**.
- **Detektor kaskady (RADAR-04):** gdy korelacje skaczą → redukcja ekspozycji.

---

## 5. OGONY (Mandelbrot, BIB-009)

- Rynki NIE są normalne (gaussowskie) — mają **grube ogony** (fat tails). Ruchy „niemożliwe"
  wg rozkładu normalnego zdarzają się regularnie.
- **Konsekwencja:** modele zakładające normalność (VaR gaussowski) niedoszacowują ryzyka.
- **Obrona:** zawsze zakładaj gorszy scenariusz niż model; trzymaj rezerwę; nigdy „all-in".
- LTCM upadło właśnie na ogonie (ruch „6-sigma" wg ich modelu).

---

## 6. METRYKI WALIDACJI

| Metryka | Co mierzy | Próg Imperium |
|---------|-----------|---------------|
| **Sharpe** | zysk/zmienność | >1 dobry, ale podatny na overfitting |
| **DSR (Deflated Sharpe Ratio)** | Sharpe skorygowany o liczbę prób (multiple testing) | ≥0.95 by uznać za realny |
| **PBO (Prob. of Backtest Overfitting)** | szansa, że best-in-sample zawiedzie OOS | niski = dobrze |
| **MaxDD** | największe obsunięcie | im niżej tym lepiej |
| **Calmar** | zysk / MaxDD | >1 zdrowy |

**Lekcja z KROKU B:** baseline i MTF oba miały DSR<0.95 → żaden config nie przeszedł
walidacji. To uczciwe — 6 mies. danych to za mało, by cokolwiek udowodnić.

---

## 7. WPŁYW NA IMPERIUM

### Co mamy:
- **Reguła 6%** — twardy HALT po serii strat
- **Z-01..07** — bezpieczniki (płynność Z-06 Amihud, Pi-Cycle Z-07, kaskada)
- **Gubernator (W-325)** — globalny mnożnik rozmiaru wg reżimu
- **HRP** — alokacja portfelowa (denoising_macierzy.py)
- **DSR/PBO** — walidacja backtestów
- **RADAR-04** — stres korelacji / detektor kaskady

### 🚨 Do wdrożenia (Prawo XV):
1. ⭐⭐⭐⭐⭐ **Volatility-targeted sizing z EXP-13** — pozycja ∝ 1/σ_GARCH (właściwe użycie filtra reżimu)
2. ⭐⭐⭐⭐ **Limit łącznej ekspozycji skorelowanej** — gdy pozycje skorelowane >0.7, traktuj jak jedną
3. ⭐⭐⭐ **Calmar w raporcie backtestu** — obok Sharpe/DSR

---

## 8. ŹRÓDŁA
- BIB-007 López de Prado — *Advances in Financial ML* (DSR, PBO, HRP)
- BIB-009 Mandelbrot — *Misbehavior of Markets* (grube ogony)
- BIB-025 Grinold & Kahn — *Active Portfolio Management*
- Powiązane: **LEW**, **ALG**, **TRD** (Seykota, PTJ, Hite)
