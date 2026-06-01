# 🔮 DORADCY CARA — Niezależna Rada Cesarska

> *"Audi alteram partem."* — Wysłuchaj drugiej strony.
>
> Gdy Senat jest podzielony, gdy sygnały się kłócą, gdy ryzyko jest wysokie —
> Cesarz wzywa Niezależnych Doradców. Mówią prawdę. Nie zależy im na wyniku głosowania.

---

## 🎯 KIEDY CESARZ WZYWA DORADCÓW

Doradcy aktywowani automatycznie gdy:
1. Senat podzielony: abs(Populares - Optimates) < 0.15 (zbyt blisko, spór)
2. Legatus WETO, ale Cesarz chce second opinion
3. Pewność agregatu w przedziale 0.55–0.65 (szara strefa)
4. Reżim VOLATILE lub sytuacja nadzwyczajna (PANIC)
5. Operator manualnie wywołuje: `cesarz.wezwij_doradcow(powod)`

---

## 🏛️ SKŁAD RADY DORADCÓW

### 🔮 Doradca I — ORACLE (Sharpe Auditor)

**Zadanie:** Ocenia jakość ryzyko-zwrot propozycji wejścia w odniesieniu do historii.

```
Metryki które liczy:
- Sharpe ratio ostatnich 20 podobnych setupów
- Sortino ratio (tylko downside volatility)
- Calmar ratio (roczny zwrot / MaxDD)
- Omega ratio (P(zysk)/P(strata) ważone wartością)

Formuła werdyktu ORACLE:
  Q_score = 0.3×Sharpe + 0.25×Sortino + 0.25×Calmar + 0.2×Omega

  Q_score > 1.2 → ORACLE mówi: "GODNE" (potwierdza wejście)
  Q_score 0.8–1.2 → "WĄTPLIWE" (zmniejsz pozycję o 50%)
  Q_score < 0.8 → "NIEGODNE" (blokuje wejście)
```

**Dane źródłowe:** Pamięć Absolutna (ImperiumLog, ostatnie 90 dni).

---

### ⚡ Doradca II — FULMEN (Regime Validator)

**Zadanie:** Niezależna weryfikacja reżimu rynkowego. Jeśli Legatus mówi TREND_STRONG,
FULMEN sprawdza z innym zestawem wskaźników.

```
FULMEN używa zestawu ortogonalnego (innego niż Legatus):
  - ADX (14) > 25 → trend potwierdzony
  - VI+/VI- (Vortex 14) → kierunek trendu
  - Choppiness Index < 38.2 → rynek trendujący (nie choppy)
  - Efficiency Ratio Kaufmana > 0.6 → ruch efektywny

Weryfikacja krzyżowa:
  Jeśli Legatus: TREND_STRONG, FULMEN: RANGING → KONFLIKT → Cesarz dostaje ostrzeżenie
  Jeśli oba zgodne → Cesarz dostaje zielone światło z wagą ×1.2
```

---

### ⚖️ Doradca III — IUSTITIA (Risk Auditor)

**Zadanie:** Niezależna ocena ryzyka całego portfolio (portfolio heat).

```
Sprawdza:
  - Portfolio Heat = Σ(ryzyko_usdt otwartych pozycji) / kapital_total
    Jeśli > 6% → IUSTITIA blokuje nowe wejście
    Jeśli > 10% → IUSTITIA nakazuje zamknięcie najsłabszej pozycji

  - Correlation Risk: czy nowe wejście jest skorelowane z otwartymi?
    Jeśli Corr(nowy, otwarty) > 0.75 → de facto podwójny zakład → veto

  - Drawdown Rate: jeśli ostatnie 5 trade'ów all-loss → 24h cooling period

  - Kelly Fraction Check: czy rozmiar pozycji ≤ 0.5 × Kelly?
    Kelly = (p × b - q) / b
    p = Win_rate, b = avg_win/avg_loss, q = 1-p
    Full Kelly: nigdy. Max = Half Kelly.
```

---

### 🌐 Doradca IV — HERMES (Information Auditor)

**Zadanie:** Weryfikuje jakość i świeżość informacji zanim Cesarz podejmie decyzję.

```
Sprawdza:
  - Kompletność danych: kompletnosc_danych w ImperiumLog < 0.80 → ostrzeżenie
  - Świeżość danych: czy wskaźniki oparte na danych nie starszych niż 2×interwał
  - Spójność hashów: hash_sha256 z Bramki musi być zweryfikowany
  - Konflikt informacji: jeśli Oczy(Newsy) dają HIGH_IMPACT event w < 30 min → hold
  - Płynność: VPIN-01 > 0.75 → HERMES ostrzega "toksyczny order flow"

Wynik: "CZYSTE ŹRÓDŁA" / "ZANIECZYSZONE" / "NIEKOMPLETNE"
```

---

### 🧮 Doradca V — PYTHIA (Probabilistic Advisor)

**Zadanie:** Oblicza rachunek prawdopodobieństwa na podstawie historycznych podobnych setupów.

```python
# Algorytm "Podobieństwo Układu" (Fingerprint Matching):
def znajdz_podobne_setupy(obecny: OdciskPalca, historia: List[ImperiumLog], top_n=20):
    """
    Odcisk Palca = (rezim, interwal, kierunek, pewnosc_bin, funding_bin, atr_bin)
    Binning: pewnosc → [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
             funding → [negatywny, neutralny, wysoki]
             ATR → [niski, normalny, wysoki]
    """
    podobne = [log for log in historia if odcisk_pasuje(log, obecny, tolerancja=1)]
    return podobne[:top_n]

# Z podobnych setupów PYTHIA liczy:
wyniki = znajdz_podobne_setupy(obecny_odcisk, pamiec_absolutna)
p_zysk = len([w for w in wyniki if w.pnl_pct > 0]) / len(wyniki)
avg_pnl = mean([w.pnl_pct for w in wyniki])
median_pnl = median([w.pnl_pct for w in wyniki])

# Werdykt:
# p_zysk > 0.60 i avg_pnl > 0.5% → PYTHIA: "HISTORYCZNIE KORZYSTNE"
# p_zysk 0.45–0.60 → "NEUTRALNE"
# p_zysk < 0.45 → "HISTORYCZNIE NIEKORZYSTNE — rozważ odwrót"
```

**Minimalna historia:** 10 podobnych setupów. Jeśli mniej → PYTHIA milczy (brak danych).

---

## 🗣️ FORMAT RAPORTU DORADCÓW

```
╔══════════════════════════════════════════════════════════════════════╗
║          🔮 RADA DORADCÓW CESARSKICH — OPINIA                        ║
║  Symbol: BTCUSDT | Setup: XII-TR-004 | Pewność Legatus: 72%          ║
╠══════════════════════════════════════════════════════════════════════╣
║  ORACLE  (Sharpe Auditor) .......... GODNE      [Q=1.34]            ║
║  FULMEN  (Regime Validator) ........ ZGODNY     [ADX=31 trend OK]   ║
║  IUSTITIA (Risk Auditor) ........... OK         [Heat=3.2%, Kelly✓] ║
║  HERMES  (Info Auditor) ............ CZYSTE     [Hash✓, VPIN=0.41]  ║
║  PYTHIA  (Probabilistic) ........... KORZYSTNE  [p=0.63, n=24]      ║
╠══════════════════════════════════════════════════════════════════════╣
║  WYNIK RADY:  4/5 POZYTYWNYCH → CESARZ MOŻE DZIAŁAĆ                 ║
║  Sugestia: Wejście potwierdzone. Rozważ +10% do pozycji (ORACLE).   ║
╚══════════════════════════════════════════════════════════════════════╝
```

**Reguły głosowania Rady:**
- 5/5 pozytywnych → Cesarz może wejść pełną pozycją
- 4/5 pozytywnych → Wejście ok, standardowa pozycja
- 3/5 pozytywnych → Wejście ok, 50% pozycji
- 2/5 lub mniej pozytywnych → CESARZ BLOKUJE (nawet jeśli Senat mówi LONG)
- Każde IUSTITIA BLOKUJE = automatyczny veto bez liczenia reszty

---

## 🔗 INTEGRACJA Z CESARZEM (DeepSeek)

```python
class CesarzZDoradcami:
    def __init__(self, legatus, senat, doradcy, kalkulator, pamiec):
        self.doradcy = doradcy  # [Oracle, Fulmen, Iustitia, Hermes, Pythia]

    def podejmij_decyzje(self, raport_legatusa, senat_wynik, kapital):
        # 1. Sprawdź czy wzywa doradców
        if self._wymagani_doradcy(raport_legatusa, senat_wynik):
            opinie = [d.ocen(raport_legatusa, self.pamiec) for d in self.doradcy]
            pozytywne = sum(1 for o in opinie if o.wynik == "POZYTYWNY")
            if pozytywne < 3:
                return Decyzja(akcja="BRAK", powod="Rada Doradców odrzuciła")
            modyfikator = pozytywne / 5  # 3/5=0.6, 4/5=0.8, 5/5=1.0
        else:
            modyfikator = 1.0

        # 2. Wywołaj DeepSeek LLM z kontekstem
        prompt = self._buduj_prompt(raport_legatusa, senat_wynik, opinie)
        odpowiedz = deepseek_api.call(prompt)
        return self._parsuj_decyzje(odpowiedz, modyfikator)
```

---

## 📊 ŹRÓDŁA DANYCH DORADCÓW

| Doradca | Główne źródło | Dane z Pamięci | Dane live |
|---------|--------------|----------------|-----------|
| ORACLE | ImperiumLog (historia) | Ostatnie 90d trade'ów | Bieżący setup |
| FULMEN | Fundament/Bramka | Nie | ADX, VI, Choppiness |
| IUSTITIA | ImperiumLog (otwarte) | Otwarte pozycje | Portfolio heat live |
| HERMES | Wszystkie kanały | Hash'e historyczne | Hash live, VPIN |
| PYTHIA | ImperiumLog (wszystkie) | Podobne setupy (90d+) | Obecny odcisk palca |

---

*"Consilium principis sapiens facit." — Mądre rady czynią mądrego władcę.*

*— DORADCY_CARA.md | v1.0 | 2026-06-01*
