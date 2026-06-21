# 🏛️ LEW — Futury i Lewar | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐⭐ (krytyczny — bezpośrednio dotyka kapitału)
> **Dla nowicjusza (ZPO):** lewar (dźwignia) = pożyczasz kapitał, by handlować większą
> pozycją niż masz. 10× lewar = 1000 USD steruje pozycją 10 000 USD. Zysk ×10, ale i
> strata ×10 — i jest **likwidacja**: gdy strata zje Twój depozyt, giełda zamyka pozycję siłą.

## 📑 SPIS TREŚCI
1. [Mechanika futures i lewara](#1-mechanika)
2. [Techniki i zagrania lewarem](#2-techniki-i-zagrania)
3. [Jak lewarem grają mistrzowie](#3-mistrzowie-lewara)
4. [Pułapki, które zabijają konto](#4-pułapki)
5. [Wpływ na Imperium](#5-wpływ-na-imperium) ← najważniejsze
6. [Źródła](#6-źródła)

---

## 1. MECHANIKA

### Kontrakt futures (perpetual / wieczysty)
Najpopularniejszy w krypto: **perpetual swap** — futures bez daty wygaśnięcia. Cena
trzymana przy spocie przez **funding rate** (opłata co 8h między longami a shortami).

| Pojęcie | Co znaczy | Dlaczego ważne |
|---------|-----------|----------------|
| **Margin** | depozyt zabezpieczający pozycję | im mniejszy względem pozycji, tym wyższy lewar i ryzyko |
| **Initial margin** | wpłata na otwarcie | = wielkość pozycji / lewar |
| **Maintenance margin** | minimum, by pozycja żyła | spadek poniżej → likwidacja |
| **Liquidation price** | cena, przy której tracisz depozyt | **liczyć ZAWSZE przed wejściem** |
| **Funding rate** | opłata long↔short co 8h | dodatni = longowie płacą shortom (rynek byczy) |
| **Mark price** | cena „uczciwa" do likwidacji | chroni przed manipulacją last price |
| **Cross margin** | cały kapitał broni pozycji | mniejsze ryzyko likwidacji, większe ryzyko konta |
| **Isolated margin** | tylko przypisany margin broni | likwidacja = strata tylko tego marginu |
| **Open Interest (OI)** | suma otwartych kontraktów | rosnący OI + rosnąca cena = silny trend |

### Wzór na cenę likwidacji (uproszczony, isolated, long)
```
liq_price ≈ entry × (1 − 1/lewar + maintenance_margin_rate)
```
- 10× long, wejście 100, MMR 0.5% → likwidacja ≈ 90.5 (spadek ~9.5%)
- 20× long → likwidacja ≈ 95.5 (spadek ~4.5%) ← cienki margines błędu!
- **Im wyższy lewar, tym bliżej ceny stoi likwidacja.** To jest cały sekret ryzyka lewara.

### Funding rate jako sygnał (nie tylko koszt)
- **Skrajnie dodatni funding** (np. >0.1%/8h) = rynek przelewarowany na long → ryzyko long squeeze
- **Skrajnie ujemny** = przelewarowany short → paliwo na short squeeze
- To **sentyment lewara** — Imperium używa tego w PSY-01 (FUNDING_RATE).

---

## 2. TECHNIKI I ZAGRANIA

### A. Skalowanie lewara do horyzontu (żelazna reguła)
| Styl | Horyzont | Rozsądny lewar | SL | Uzasadnienie |
|------|----------|----------------|-----|--------------|
| Scalp | min–godziny | 10–20× | bardzo ciasny (0.3–0.8%) | krótki czas = mała ekspozycja na ogon |
| Swing | dni | 3–5× | 2–5% | dłuższy czas = więcej szumu do przetrwania |
| Pozycja/invest | tygodnie+ | 1–2× lub spot | szeroki/strukturalny | trend ma „oddychać" |

> **Zasada Imperium (Gubernator W-325):** lewar/rozmiar skaluje się do reżimu
> zmienności. Wysoka zmienność → lewar w dół (mniejsza pozycja), nie w górę.

### B. Konkretne zagrania
1. **Trend-following z trailing SL** — wchodzisz z trendem (potwierdzonym wyższym TF),
   lewar umiarkowany, SL podążający za ceną. Najbezpieczniejsze użycie lewara.
2. **Breakout scalp** — wybicie z konsolidacji, wysoki lewar, ciasny SL pod poziomem
   wybicia. Wymaga potwierdzenia wolumenem (inaczej fakeout).
3. **Basis trade (cash-and-carry)** — long spot + short perpetual gdy funding dodatni →
   zbierasz funding, neutralny kierunkowo. Arthur Hayes uczynił z tego sztukę.
4. **Funding farming** — pozycja po „taniej" stronie fundingu, zbierasz opłatę co 8h.
5. **Hedge spot+futures** — masz spot, otwierasz short futures na czas korekty zamiast
   sprzedawać spot (oszczędność podatkowa/prowizyjna).
6. **Mean-reversion na ekstremach fundingu** — gdy funding skrajny, zakład na squeeze
   przeciwnej strony. Wysokie ryzyko, tylko z ciasnym SL.

### C. Sizing pozycji (matematyka, nie emocje)
**Reguła stałego ryzyka:** ryzykuj stały % konta na transakcję (np. 1–2%), niezależnie od lewara.
```
rozmiar_pozycji = (kapitał × %ryzyka) / (dystans_do_SL w %)
```
Przykład: 10 000 USD, ryzyko 1% (=100 USD), SL 2% od wejścia → pozycja 5 000 USD.
Lewar jest wtedy POCHODNĄ sizingu, nie odwrotnie. **To odróżnia profesjonalistę od hazardzisty.**

---

## 3. MISTRZOWIE LEWARA

> Pełna lista traderów (wszystkie style) → dział **TRD**. Tu tylko ci, których
> wkład dotyczy konkretnie lewara/futures/sizingu.

| Trader | Wkład w temat lewara | Lekcja dla Imperium |
|--------|----------------------|---------------------|
| **Arthur Hayes** (BitMEX) | spopularyzował perpetual swap i basis trade; mistrz funding arbitrage | PSY-01 funding jako sygnał, nie tylko koszt |
| **Stanley Druckenmiller** | „wielkość pozycji > trafność" — koncentruje gdy ma przewagę, minimalizuje gdy nie | sizing dynamiczny / Gubernator |
| **Paul Tudor Jones** | obsesja na punkcie kontroli ryzyka: „nie myśl o zarabianiu, myśl o ochronie tego, co masz" | Reguła 6%, HALT |
| **Ed Seykota** | „elementy dobrego tradingu: tnij straty, tnij straty, tnij straty" | bezpieczniki Z-01..07 |
| **3AC (Three Arrows)** | ⚠️ NEGATYWNY przykład: nadmierny lewar + brak hedgingu = bankructwo (2022) | dlaczego twardy HALT i limity są nienaruszalne |
| **Larry Hite** | „nigdy nie ryzykuj więcej niż 1% na transakcję" | stały % ryzyka |

---

## 4. PUŁAPKI

| Pułapka | Mechanizm | Obrona Imperium |
|---------|-----------|-----------------|
| **Cascade liquidation** | likwidacje napędzają likwidacje → flash crash | RADAR-04 stres korelacji, detektor kaskady (W-329) |
| **Funding drain** | trzymasz long w byczym rynku, funding zjada zysk | PSY-01 monitoruje funding |
| **Stop hunt** | cena „dotyka" Twój SL przy okrągłym poziomie i wraca | SL nie na okrągłych liczbach, mark price nie last |
| **Over-leverage** | 50–125× = likwidacja przy 0.8–2% ruchu = ruletka | limity lewara, sizing wg ryzyka |
| **Rewenge trading** | po stracie zwiększasz lewar, by „odrobić" | Reguła 6% / HALT psychologiczny |
| **Ignorowanie wyższego TF** | scalp long pod opór 4h/1d = wejście pod nóż | MTF konfluencja (W-384) |

---

## 5. WPŁYW NA IMPERIUM

### Co już mamy (kod istnieje):
- **KalkulatorLewara** — dobiera lewar do warunków (pretorianie/kalkulator_lewara.py)
- **Gubernator (W-325)** — globalny mnożnik rozmiaru wg reżimu (floor 0.5× / ceiling 1.3×)
- **Z-01..07** — bezpieczniki (płynność, zmienność, kaskada, Pi-Cycle szczyt)
- **PSY-01..04** — funding, long/short ratio, fear&greed, OI (⏳ czekają na AdapterFutures)
- **Reguła 6%** — twardy HALT po serii strat
- **RADAR-04** — stres korelacji / detektor kaskady likwidacji (W-329)
- **MTF konfluencja (W-384)** — brama wyższego TF (testowana w KROKU B)

### 🚨 UTRATA POTENCJAŁU (Prawo XV) — do ożywienia:
| Moduł | Stan | Co odblokowuje | Ważność |
|-------|------|----------------|---------|
| PSY-01 FUNDING_RATE | ⏳ czeka na feed | sentyment lewara = realny sygnał | ⭐⭐⭐⭐ |
| PSY-04 OPEN_INTEREST | ⏳ czeka na feed | siła trendu (OI+cena) | ⭐⭐⭐⭐ |
| PSY-02 LONG_SHORT_RATIO | ⏳ czeka na feed | pozycjonowanie tłumu | ⭐⭐⭐ |

**Wszystkie trzy ożywają z Binance Futures public API (DARMOWE, bez klucza).**
To najtańszy duży skok jakości — patrz dział IMP.

### 💡 Co można jeszcze wdrożyć (propozycje z oceną):
1. ⭐⭐⭐⭐⭐ **Adaptacyjny limit lewara wg zmienności** — automatyczne cięcie max
   lewara gdy GARCH (EXP-13!) wykrywa wysoki reżim zmienności. **Tu EXP-13 znajduje
   swoje prawdziwe zastosowanie jako filtr reżimu** (zgodnie z werdyktem backward-IC).
2. ⭐⭐⭐⭐ **Funding-aware sizing** — zmniejsz long gdy funding skrajnie dodatni
   (drogi do trzymania + ryzyko squeeze).
3. ⭐⭐⭐ **Liquidation heatmap** — szacowanie klastrów cen likwidacji jako wsparcie/opór.

---

## 6. ŹRÓDŁA
- BIB-008 Sinclair — *Volatility Trading* (zmienność, sizing)
- BIB-018 Sinclair — *Positional Option Trading*
- BIB-027 Aldridge — *High-Frequency Trading* (mikrostruktura, impact)
- BIB-020 Harris — *Trading and Exchanges* (mechanika rynku)
- Powiązane działy: **RSK** (ryzyko), **MKS** (mikrostruktura), **TRD** (traderzy)
