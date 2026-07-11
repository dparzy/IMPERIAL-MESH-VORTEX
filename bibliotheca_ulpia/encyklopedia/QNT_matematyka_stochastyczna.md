# 🧮 QNT — Matematyka ilościowa i procesy stochastyczne | Encyklopedia Imperium

> **Stan na:** 2026-07-11 | **Ważność:** ⭐⭐⭐⭐ (wysoki — fundament pod modele Imperium)
> **Status:** ✅ DOMKNIĘTY — księgi źródłowe (BIB-065/066 Shreve) **wyekstrahowane** (djvu→cache
> przez calibre na laptopie, w RAG). **Proza pojęciowa zweryfikowana** (`biblioteka_szukaj`);
> **równania z artefaktami OCR** (Prawo I — oddajemy esencję pojęć, nie wzory). Styki z KODEM
> (GARCH, BOCPD, FracDiff, ECON/Feynman-Kac) ugruntowane w repo + w źródle ARTEMIS.
> **Co to jest:** dział o matematycznym rdzeniu finansów ilościowych — rachunek stochastyczny,
> martyngały, wycena bez arbitrażu, modele zmienności. Język, w którym mówią GARCH, BOCPD, ECON.
> Odrębny od ALG (algorytmy/ML) — tu TEORIA procesów.
> **Karmi:** EXP-13 GARCH, BOCPD-01 (zmiana reżimu), N-02 FracDiff, ECON/FiltrEkonomiczny (Feynman-Kac),
> neurony zmienności, arena trzech bram.

## 📑 SPIS TREŚCI
1. Szkielet Shreve I/II (✅ ekstrakt djvu — esencja pojęć zweryfikowana)
2. Brak arbitrażu i Feynman-Kac — fundament ECON (✅ z ARTEMIS + kodu)
3. Zmienność jako proces: GARCH, FracDiff (✅ z kodu)
4. Martyngał → uczciwy backtest (✅ zasada)
5. Wpływ na Imperium (co mamy / do wdrożenia)
6. Źródła

---

## 1. SZKIELET SHREVE I/II (✅ EKSTRAKT djvu — 2026-07-11)

> **Prawo I (uczciwa kalibracja):** djvu wyekstrahowane na laptopie (calibre) i zaindeksowane w RAG.
> **Proza pojęciowa czytelna i zweryfikowana** (poniższe potwierdzone w tekście przez `biblioteka_szukaj`);
> **równania mają artefakty OCR** (symbole matematyczne → krzaki) — dlatego oddajemy ESENCJĘ POJĘĆ,
> nie wzory. Nazwa „Feynman-Kac" **nie przetrwała OCR** w Shreve II (rozdział istnieje w księdze) —
> ten wątek pozostaje ugruntowany w ARTEMIS (§2), nie cytujemy go z pliku.

**Shreve I — model dwumianowy (zweryfikowane w ekstrakcie, chunki #45/#99/#170):**
- **Wycena replikacją i delta-hedging:** cena derywatu = koszt portfela replikującego wypłatę
  (indeks księgi wymienia *delta-hedging formula*, *derivative security European/American*,
  *complete model*, *risk-neutral pricing*).
- **Miara ryzyka-neutralna:** wycena jako zdyskontowana wartość oczekiwana pod miarą, w której
  **zdyskontowany proces ceny jest martyngałem** (*discount process*, *discounted derivative price*).
- **Martyngał w czasie dyskretnym:** proces bez dryfu warunkowego; oczekiwanie **stałe w czasie**
  (M₀ = E[Mₙ]) i własność *multistep-ahead* Mₙ = Eₙ[Mₘ]. Warunkowe oczekiwanie: iterowane
  warunkowanie, *taking out what is known*.
- **Random walk / proces zatrzymany:** symetryczne błądzenie losowe jako martyngał; *frozen/stopped
  process* — czas nie stoi, zamraża się wartość procesu.

**Shreve II — czas ciągły (zweryfikowane w ekstrakcie, chunk #120):**
- **Rachunek Itô / wariacja kwadratowa:** `dB·dB = dt` — sercowa reguła rachunku stochastycznego;
  zmienności i wariacje kwadratowe/krzyżowe **niezmiennicze przy zmianie miary**.
- **Zmiana miary (Girsanov):** *„Martingales may be destroyed or created. Volatilities, quadratic
  variations and cross variations are unaffected."* — przejście miara realna ↔ ryzyko-neutralna;
  reguła Bayesa dla oczekiwań warunkowych pod nową miarą.
- **Black-Scholes / Feynman-Kac:** kanoniczne rozdziały księgi (istnieją), lecz nazwy nie przetrwały
  OCR — ugruntowane w §2 (ARTEMIS, Prawo I), nie z pliku.

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
1. ✅ **Domknięcie QNT** — Shreve I/II wyekstrahowane (calibre) i w RAG; esencja §1 zweryfikowana
   (`biblioteka_szukaj`). Pozostaje ⚠️: równania z artefaktami OCR — do formalnych wzorów sięgamy
   po źródło z czystym tekstem (ARTEMIS dla Feynman-Kac), nie po OCR djvu.
2. ⭐⭐⭐ **Wycena/greeks jeśli wejdą derywaty** ⚠️ — Shreve II jako kanon (opcje/perpetuale, styk DEF).

> **Prawo XVI:** QNT (teoria procesów) ⊥ ALG (algorytmy/ML) ⊥ RSK (zarządzanie ryzykiem).
> López de Prado (BIB-007/023) → ALG/RSK; tu czysta matematyka procesów.

---

## 6. ŹRÓDŁA (ZPO)

- **BIB-065 Shreve** — *Stochastic Calculus for Finance I: The Binomial Asset Pricing Model*,
  Springer 2004, ISBN 978-0-387-40100-3. ✅ **EKSTRAKT** (djvu→cache, calibre; proza zweryfikowana,
  równania OCR-ograniczone). Model dwumianowy, wycena replikacją, miara ryzyka-neutralnego, martyngały.
- **BIB-066 Shreve** — *Stochastic Calculus for Finance II: Continuous-Time Models*, Springer 2004,
  ISBN 978-0-387-40101-0. ✅ **EKSTRAKT** (djvu→cache; proza zweryfikowana — Itô `dB·dB=dt`, Girsanov;
  **Feynman-Kac/Black-Scholes: nazwy nie przetrwały OCR**, ugruntowane w ARTEMIS — Prawo I).
- **Materiał współdzielony (✅ z kodu/źródeł):** ARTEMIS [arXiv 2603.18107](https://arxiv.org/abs/2603.18107)
  (Feynman-Kac → ECON); López de Prado (FracDiff → ALG). GARCH: Tsay *Analysis of Financial Time
  Series* (BIB-031, → ALG).

---
*Domknięto 2026-07-11: Shreve I/II wyekstrahowane (calibre, djvu→cache) i w RAG; esencja pojęć
zweryfikowana przez `biblioteka_szukaj` (martyngał, replikacja, miara ryzyko-neutralna, Itô `dB·dB=dt`,
Girsanov). Prawo I: równania OCR-ograniczone, Feynman-Kac/Black-Scholes ugruntowane w ARTEMIS (nazwy
nie przetrwały OCR w djvu). Styki z kodem (GARCH/BOCPD/FracDiff/ECON) bez zmian.*
