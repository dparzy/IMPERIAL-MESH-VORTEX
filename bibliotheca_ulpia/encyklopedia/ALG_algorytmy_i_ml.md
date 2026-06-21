# 🏛️ ALG — Algorytmy i Machine Learning | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐ (wysoki — mózg analityczny roju)
> **Dla nowicjusza (ZPO):** to dział o tym, jak Imperium PRZETWARZA dane w decyzje —
> statystyka, ML, walidacja. Kluczowa lekcja całego działu: **łatwo oszukać samego siebie**
> (overfitting, leak, fałszywy edge). Połowa pracy to budowa modelu, druga połowa to
> udowodnienie, że nie kłamie.

## 📑 SPIS TREŚCI
1. [Prawo fundamentalne (IC, IR, breadth)](#1-prawo-fundamentalne)
2. [Denoising macierzy korelacji](#2-denoising)
3. [HRP — alokacja](#3-hrp)
4. [Szeregi czasowe i GARCH](#4-szeregi-czasowe)
5. [Pułapki ML w finansach](#5-pułapki-ml)
6. [Walidacja: jak nie oszukać siebie](#6-walidacja)
7. [Wpływ na Imperium](#7-wpływ-na-imperium)
8. [Źródła](#8-źródła)

---

## 1. PRAWO FUNDAMENTALNE (Grinold & Kahn, BIB-025)

```
IR = IC × √breadth
```
- **IC (Information Coefficient):** korelacja prognozy z realizacją (Spearman(sygnał, zwrot)).
  IC>0.05 w finansach to już dużo. IC~0 = szum.
- **breadth:** liczba niezależnych zakładów (par × niezależnych decyzji).
- **IR (Information Ratio):** jakość strategii = skill × √(liczba prób).

**Lekcja Imperium (2026-06-21):** wysokie IC (~0.30) NIE znaczy edge — backward-IC
udowodnił, że EXP-13/14 to deskryptory reżimu, nie predyktory. **IC trzeba walidować
asymetrią czasową (forward vs backward), zanim uznamy za skill.** Kandydat na regułę CLAUDE.md.

---

## 2. DENOISING (López de Prado, BIB-023)

Macierz korelacji z danych rynkowych jest pełna szumu (zwłaszcza przy małej próbie).
- **Marčenko-Pastur:** rozkład wartości własnych czystego szumu → wartości poza nim = sygnał.
- **Denoising:** „spłaszcz" wartości własne w paśmie szumu, zachowaj sygnałowe.
- **W Imperium:** `denoising_macierzy.py` — czyści macierz przed alokacją/dekorelacją.

---

## 3. HRP — Hierarchical Risk Parity (López de Prado)

Alokacja portfelowa odporna na szum (lepsza niż Markowitz, który eksploduje przy
niestabilnej macierzy):
1. **Klastrowanie** (single-linkage) po odległości korelacyjnej d=√(½(1−ρ))
2. **Quasi-diagonalizacja** (seriation) — układa skorelowane aktywa obok siebie
3. **Rekursywna bisekcja** — alokuje kapitał odwrotnie do wariancji klastrów

**W Imperium:** `denoising_macierzy.hrp_wagi(cov, klucze)`. Patrz też dział RSK.

---

## 4. SZEREGI CZASOWE I GARCH (Tsay, BIB-031)

- **GARCH(1,1):** modeluje zmienność warunkową — klastrowanie zmienności (spokój→spokój, burza→burza).
- **GJR-GARCH:** dodaje efekt dźwigni (spadki podnoszą zmienność bardziej niż wzrosty).
- **W Imperium (EXP-13):** GJR-GARCH(1,1) grid-search log-likelihood w czystym numpy.
- **Werdykt:** GARCH mierzy STAN zmienności = filtr reżimu, nie predyktor kierunku.

---

## 5. PUŁAPKI ML W FINANSACH (López de Prado, BIB-007)

| Pułapka | Mechanizm | Obrona |
|---------|-----------|--------|
| **Overfitting** | model dopasowany do szumu | DSR, PBO, walk-forward |
| **Look-ahead leak** | użycie przyszłej info | --przesuniecie test, audyt pipeline |
| **Survivorship bias** | tylko ocalałe aktywa w danych | pełny uniwersum historyczny |
| **Multiple testing** | testujesz 1000 strategii, 1 „działa" | DSR koryguje o liczbę prób |
| **Non-IID** | próbki nakładające się/skorelowane | --nienakladajace, purged CV |
| **Reżim** | edge tylko w jednym reżimie | test wieloreżimowy (jak MTF re-test) |

---

## 6. WALIDACJA (jak nie oszukać siebie)

To esencja całego działu — narzędzia, które Imperium realnie używa:
- **DSR (Deflated Sharpe Ratio):** Sharpe skorygowany o liczbę testowanych konfiguracji. Próg ≥0.95.
- **PBO (Prob. of Backtest Overfitting):** combinatorially-symmetric cross-validation.
- **Backward-IC:** asymetria czasowa — czy sygnał przewiduje czy opisuje (lekcja 2026-06-21).
- **Walk-forward / OOS:** trenuj na przeszłości, testuj na nieznanej przyszłości.
- **Test wieloreżimowy:** czy edge trzyma w bull/bear/range (re-test MTF w toku).

---

## 7. WPŁYW NA IMPERIUM

### Co mamy (kod):
- `metryki_ic.py` — IC, prawo fundamentalne IR=IC·√breadth, KolektorIC
- `denoising_macierzy.py` — Marčenko-Pastur denoising + HRP
- `diagnostyka_korelacji.py` — raport dekorelacji (Prawo XVI)
- `mikrostruktura.py` — Engle-Granger kointegracja, ADF
- EXP-13 GARCH, EXP-14 Kyle's λ
- `pomiar_nowe_moduly.py` — IC matrycowy + kontrole (overlap/lag/backward)

### 🚨 Do wdrożenia (Prawo XV):
1. ⭐⭐⭐⭐ **Backward-IC jako stała reguła** — każdy nowy moduł z wysokim IC przechodzi test asymetrii
2. ⭐⭐⭐⭐ **Cache sygnałów + multiprocessing** w pomiarach (sweep 8min→40s)
3. ⭐⭐⭐ **Purged/embargoed CV** dla backtestów (López de Prado) — eliminuje leak na granicy okien

---

## 8. ŹRÓDŁA
- BIB-007 López de Prado — *Advances in Financial ML* (DSR, PBO, purged CV, leak)
- BIB-023 López de Prado — *ML for Asset Managers* (denoising, HRP)
- BIB-031 Tsay — *Analysis of Financial Time Series* (GARCH, ARIMA)
- BIB-025 Grinold & Kahn — *Active Portfolio Management* (prawo fundamentalne)
- BIB-026 Jansen — *ML for Algorithmic Trading*
- Powiązane: **RSK**, **MKS**, **STR**
