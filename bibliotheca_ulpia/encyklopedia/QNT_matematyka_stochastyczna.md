# 🧮 QNT — Matematyka ilościowa i procesy stochastyczne | Encyklopedia Imperium

> **Stan na:** 2026-07-11 | **Ważność:** ⭐⭐⭐⭐ (wysoki — fundament pod modele Imperium)
> **Status:** 🚧 CZĘŚCIOWY — księgi źródłowe (BIB-065/066 Shreve) w formacie **djvu — ⚠️ PENDING**
> ekstrakcji na laptopie (`djvutxt` niedostępny w chmurze). Styki z KODEM (GARCH, BOCPD, FracDiff,
> ECON/Feynman-Kac) ugruntowane w naszym repo + w zweryfikowanym źródle ARTEMIS (Prawo I).
> **Co to jest:** dział o matematycznym rdzeniu finansów ilościowych — rachunek stochastyczny,
> martyngały, wycena bez arbitrażu, modele zmienności. Język, w którym mówią GARCH, BOCPD, ECON.
> Odrębny od ALG (algorytmy/ML) — tu TEORIA procesów.
> **Karmi:** EXP-13 GARCH, BOCPD-01 (zmiana reżimu), N-02 FracDiff, ECON/FiltrEkonomiczny (Feynman-Kac),
> neurony zmienności, arena trzech bram.

## 📑 SPIS TREŚCI
1. Szkielet Shreve I/II (⚠️ pending djvu — plan do domknięcia)
2. Brak arbitrażu i Feynman-Kac — fundament ECON (✅ z ARTEMIS + kodu)
3. Zmienność jako proces: GARCH, FracDiff (✅ z kodu)
4. Martyngał → uczciwy backtest (✅ zasada)
5. Wpływ na Imperium (co mamy / do wdrożenia)
6. Źródła

---

## 1. SZKIELET SHREVE I/II (⚠️ BIB-065/066, PENDING djvu)

> **Prawo I:** poniższe to KANONICZNY plan do WERYFIKACJI po ekstrakcji Shreve na laptopie —
> nie cytuję z pliku (djvu nieczytelny w chmurze). Do uzupełnienia esencją:
> - **Shreve I (Binomial):** model dwumianowy jako brama do czasu ciągłego, wycena replikacją,
>   miara ryzyka-neutralnego, martyngały w czasie dyskretnym.
> - **Shreve II (Continuous):** ruch Browna, **lemat Itô**, całka stochastyczna, Black-Scholes,
>   **twierdzenie Feynman-Kac**, zmiana miary (Girsanov), struktura terminowa.

## 2. BRAK ARBITRAŻU I FEYNMAN-KAC — fundament ECON (✅ z ARTEMIS + kodu)

To ugruntowane w zweryfikowanym źródle (ARTEMIS, [arXiv 2603.18107](https://arxiv.org/abs/2603.18107))
i w naszym kodzie (`FiltrEkonomiczny`), nie w pliku Shreve: **twierdzenie Feynman-Kac** wyraża
warunek **braku arbitrażu** — oczekiwana zmiana wartości = stopa wolna od ryzyka. To matematyczny
fundament naszego **FiltrEkonomiczny (ECON)**: kara *market price of risk* ogranicza chwilowy
Sharpe, bo w świecie bez arbitrażu nagroda-za-ryzyko jest ograniczona. Shreve II to podręcznikowy
kanon tego twierdzenia — jego pełna esencja domknie ten wątek po ekstrakcji djvu.

## 3. ZMIENNOŚĆ JAKO PROCES: GARCH, FracDiff (✅ z KODU)

Ugruntowane w kodzie Imperium:
- **GARCH (EXP-13, GJR-GARCH)** — zmienność warunkowa: dzisiejsza wariancja zależy od wczorajszych
  szoków i wariancji (klasteryzacja zmienności). Fundament stochastyczny → sizing (RSK) i reżim.
- **Fractional Differentiation (N-02)** — usuwa trend zachowując pamięć długiego zasięgu
  (López de Prado); stacjonarność bez utraty sygnału.
- **BOCPD-01** — Bayesian Online Change-Point Detection: prawdopodobieństwo zmiany reżimu jako
  proces. Shreve dostarcza teorii procesów pod te moduły.

## 4. MARTYNGAŁ → UCZCIWY BACKTEST (✅ zasada)

Kluczowa lekcja QNT dla Imperium: **martyngał** = proces bez przewidywalnego dryfu warunkowego.
Zasada „brak lookahead" w backteście (Prawo I) to operacyjny odpowiednik: sygnał w kroku t używa
wyłącznie informacji do t-1 — inaczej „przewidujemy" przeszłość i łamiemy martyngałowość testu.

---

## 5. WPŁYW NA IMPERIUM

### Co mamy:
- **EXP-13 GARCH, N-02 FracDiff, BOCPD-01** — procesy stochastyczne w kodzie (§3).
- **FiltrEkonomiczny (ECON)** — Feynman-Kac / brak arbitrażu w praktyce (§2).
- **Brak lookahead** (purged-CV, martyngałowość testu) — §4.

### 🚨 Do wdrożenia (Prawo XV — KANDYDACI ⚠️):
1. ⭐⭐⭐⭐ **Domknięcie QNT na laptopie** ⚠️ — ekstrakcja Shreve I/II (`djvutxt`) → pełna esencja
   §1 + formalne uzasadnienie ECON (Feynman-Kac) i modeli zmienności.
2. ⭐⭐⭐ **Wycena/greeks jeśli wejdą derywaty** ⚠️ — Shreve II jako kanon (opcje/perpetuale, styk DEF).

> **Prawo XVI:** QNT (teoria procesów) ⊥ ALG (algorytmy/ML) ⊥ RSK (zarządzanie ryzykiem).
> López de Prado (BIB-007/023) → ALG/RSK; tu czysta matematyka procesów.

---

## 6. ŹRÓDŁA (ZPO)

- **BIB-065 Shreve** — *Stochastic Calculus for Finance I: The Binomial Asset Pricing Model*,
  Springer 2004, ISBN 978-0-387-40100-3. ⚠️ **PENDING** (djvu — ekstrakcja na laptopie). Model
  dwumianowy, wycena replikacją, miara ryzyka-neutralnego.
- **BIB-066 Shreve** — *Stochastic Calculus for Finance II: Continuous-Time Models*, Springer 2004,
  ISBN 978-0-387-40101-0. ⚠️ **PENDING** (djvu). Ruch Browna, Itô, Black-Scholes, **Feynman-Kac**,
  Girsanov — kanon pod ECON i modele zmienności.
- **Materiał współdzielony (✅ z kodu/źródeł):** ARTEMIS [arXiv 2603.18107](https://arxiv.org/abs/2603.18107)
  (Feynman-Kac → ECON); López de Prado (FracDiff → ALG). GARCH: Tsay *Analysis of Financial Time
  Series* (BIB-031, → ALG).

---
*Wypełniono częściowo 2026-07-11: styki z kodem (GARCH/BOCPD/FracDiff/ECON) + Feynman-Kac z ARTEMIS
(Prawo I). Esencja Shreve I/II — 🚧 do domknięcia po ekstrakcji djvu na laptopie.*
