---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/cesarz/doradcy/fulmen.py, imperium/cesarz/doradcy/hermes.py, imperium/cesarz/doradcy/iustitia.py, imperium/cesarz/doradcy/oracle.py, imperium/cesarz/doradcy/pythia.py, imperium/cesarz/doradcy/rada.py
stan_na: 2026-07-17
powod_istnienia: "Jedyny dokument opisujący 'drugą opinię' Cesarza — radę 5 doradców (Oracle/Fulmen/Iustitia/Hermes/Pythia) oceniających każde wejście niezależnie od Legatusa i Senatu"
---
# 🔮 DORADCY CARA — Niezależna Rada Cesarska

> *"Audi alteram partem."* — Wysłuchaj drugiej strony.
>
> Pięcioro doradców ocenia wejście własnymi miarami. Mówią prawdę. Nie zależy im na wyniku
> głosowania Legatusa ani Senatu.

> **⚠️ Weryfikacja wobec kodu 2026-07-17.** Wzory i progi wszystkich pięciorga **zgadzają się
> z kodem** ✅. Rozjechało się to, co je *spina*: klasa `CesarzZDoradcami` i metoda
> `wezwij_doradcow()` **nigdy nie istniały**, a opisane niżej „warunki automatycznej aktywacji"
> to była wizja, nie kod. Sprostowane w tej sekcji.

---

## 🎯 KIEDY WZYWANA JEST RADA — flaga, nie warunki (sprostowanie)

**Realnie (zmierzone):** Rada to **opt-in dyrygenta** — `Dyrygent(..., rada=True)` tworzy
`RadaDoradcow()`, a jedyny warunek w pętli to `if self.rada_doradcow is not None:`
([`dyrygent.py:540`](../imperium/koloseum/dyrygent.py)). Gdy włączona — ocenia **każde**
kandydujące wejście. Gdy wyłączona — nie ocenia żadnego. **Nie ma stanów pośrednich.**

> 🔴 **Czego NIE MA** (poprzednia wersja podawała to jako działający mechanizm):
> nie istnieje aktywacja przy „Senacie podzielonym `abs(Populares−Optimates) < 0.15`",
> przy „WETO Legatusa", w „szarej strefie pewności 0.55–0.65" ani w „reżimie VOLATILE/PANIC".
> Nie istnieje też ręczne wywołanie `cesarz.wezwij_doradcow(powod)` — **ani ta metoda, ani
> klasa `CesarzZDoradcami`** (0 trafień w kodzie). To była lista życzeń.
>
> Warunkowe wzywanie (tylko w sytuacjach spornych) zostaje **postulatem** 🔵 — dziś Rada jest
> albo dla wszystkich wejść, albo dla żadnego.

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
FULMEN karmiony jest (dyrygent → DaneFulmen) — progi zgodne z kodem ✅:
  - ADX_14 > 25          → trend potwierdzony   (ADX_TREND_PROG = 25.0)
  - DI_PLUS / DI_MINUS   → kierunek trendu      (pola nazwane vi_plus_14/vi_minus_14)
  - CHOPPINESS_14 < 38.2 → rynek trendujący     (CHOPPINESS_TREND = 38.2)
  - KAUFMAN_ER_10 > 0.6  → ruch efektywny

Weryfikacja krzyżowa:
  Jeśli Legatus: TREND_STRONG, FULMEN: RANGING → KONFLIKT → ostrzeżenie
  Jeśli oba zgodne → potwierdzenie reżimu
```

> ⚠️ **„Vortex" nie istnieje — sprostowanie 2026-07-17.** Dokument obiecywał `VI+/VI- (Vortex 14)`.
> W kodzie **nie ma żadnego wskaźnika Vortex** (0 trafień). Pola `DaneFulmen.vi_plus_14/vi_minus_14`
> są karmione **`DI_PLUS`/`DI_MINUS`** (Directional Indicator Wildera) — dyrygent nazywa to wprost
> *„DI+/DI- jako proxy VI"*. Nazwa pola została z niezrealizowanego zamiaru.

> 🚨 **Ortogonalność jest CZĘŚCIOWA, nie pełna (Prawo XVI — zmierzone).** Obietnica „zestaw
> ortogonalny (inny niż Legatus)" nie ma pokrycia w połowie przypadków: **2 z 4** wskaźników
> FULMENA to **dokładnie te same** wskaźniki, którymi już głosują neurony Legatusa:
>
> | Wskaźnik FULMENA | Neuron Legatusa na tym samym wskaźniku |
> |---|---|
> | `ADX_14` | **XII-01** `NeuronADX` (KAT=T) |
> | `CHOPPINESS_14` | **V-14** `NeuronChoppiness` (KAT=V) |
> | `DI_PLUS`/`DI_MINUS` | — (brak neuronu) |
> | `KAUFMAN_ER_10` | — (brak neuronu) |
>
> To **nie jest** pełna redundancja: Fulmen zadaje tym liczbom **inne pytanie** (jaki REŻIM?)
> niż neurony (jaki KIERUNEK?). Ale „niezależna weryfikacja" czerpiąca w połowie z tego samego
> pomiaru jest słabszą kontrolą, niż sugerował ten dokument — jeśli `ADX_14` jest przekłamany,
> myli się i neuron, i jego „niezależny" audytor. Zmierzyć dekorelacją (Prawo XVI) przed
> ewentualną wymianą na prawdziwie ortogonalny zestaw.

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
Sprawdza (progi zgodne z kodem ✅):
  - Kompletność danych: kompletnosc_danych < 0.80 → ostrzeżenie   (KOMPLETNOSC_MIN = 0.8)
  - Świeżość danych: nie starsze niż 2×interwał                   (SWIEZE_MNOZNIK = 2)
  - Spójność hashów: hash_ok                                       (⚠️ patrz alarm niżej)
  - Konflikt informacji: HIGH_IMPACT event w < 30 min → hold      (EVENT_BUFOR_MINUT = 30)
  - Płynność: VPIN > 0.75 → "toksyczny order flow"                (VPIN_PROG = 0.75)

Wynik: "CZYSTE" / "ZANIECZYSZONE" / "NIEKOMPLETNE"
```

> 🚨 **Prawo XV — bramka hashów HERMESA nie może się zapalić (zmierzone 2026-07-17).**
> Hermes ma gałąź `if not dane.hash_ok → BRUDNE`, ale [`dyrygent.py:911`](../imperium/koloseum/dyrygent.py)
> podaje mu **`hash_ok=True` na sztywno**. Powód jest głębszy niż jedna linia: Brama liczy
> `CalcResult.sha256` per wskaźnik, ale `ImperiumLog.hash_sha256` **nie jest wypełniany przez
> NIC** (0 przypisań w bazie) — nie ma czego z czym porównać, więc literał `True` zabetonował
> lukę. **„Spójność hashów" jest dziś martwą literą.** Ten sam alarm opisany w
> [`PAMIEC_ABSOLUTNA.md`](./PAMIEC_ABSOLUTNA.md) (LUKA 1); w Księdze Wad jako klasa
> `bezpiecznik`. Naprawa = osobne zadanie (Hermes stoi na ścieżce decyzyjnej → ZASADA WPIĘCIA,
> opt-in OFF + A/B).

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

**Reguły głosowania Rady — `RadaDoradcow.ocen()` (zweryfikowane ✅):**

| Pozytywnych | `modyfikator_pozycji` | Skutek |
|---|---|---|
| 5/5 | **1.0** | pełna pozycja |
| 4/5 | **0.8** | wejście ok, pozycja ×0.8 |
| 3/5 | **0.6** | wejście ok, pozycja ×0.6 |
| ≤ 2/5 | **0.0** | `blokada=True` → dyrygent zwraca `RADA_WETO` |

- **IUSTITIA BLOKUJE** lub **HERMES ZANIECZYSZONE** → natychmiastowe weto, `pozytywne=0`
  (bez liczenia reszty).
- **PYTHIA MILCZENIE** (< 10 podobnych setupów) = **neutralne, nie blokuje** ✅ — zgodnie
  z „brak danych ≠ zły sygnał" (Prawo I).

> ⚠️ **„3/5 → 50% pozycji" to nieścisłość** — realny mnożnik to **×0.6**, nie ×0.5. Ta sama
> pomyłka siedzi w komentarzu kodu („zmniejszona pozycja 50% (×0.6)"). Liczy się `0.6`.

---

## 🔗 REALNA INTEGRACJA — Dyrygent, nie „Cesarz z Doradcami"

> 🔴 **Klasa `CesarzZDoradcami` NIE ISTNIEJE** (0 trafień w kodzie) — ani ona, ani
> `podejmij_decyzje()`, ani `_wymagani_doradcy()`, ani `wezwij_doradcow()`. Poprzednia wersja
> dokumentu prezentowała ten blok jako działającą integrację. **Nie ma też wywołania DeepSeeka
> w ścieżce Rady** — Rada jest w 100% deterministyczna (zero LLM).

Prawdziwy przepływ ([`dyrygent.py`](../imperium/koloseum/dyrygent.py)): każdy doradca jest
wołany **osobno, własnymi danymi**, a `RadaDoradcow` tylko zlicza gotowe oceny.

```python
# 1. Włączenie (opt-in przy budowie dyrygenta)
dyrygent = Dyrygent.zbuduj(..., rada=True)      # rada=False → Rada w ogóle nie działa

# 2. W pętli, dla KAŻDEGO kandydata na wejście (dyrygent._opinia_rady):
ocena_oracle   = Oracle().ocen(pnl_hist)                      # historia PnL sesji
ocena_fulmen   = Fulmen().ocen(DaneFulmen(adx_14=..., ...))   # wskaźniki z Budowniczego
ocena_iustitia = Iustitia().ocen(DaneIustitia(...))           # otwarte pozycje z engine
ocena_hermes   = Hermes().ocen(DaneHermes(...))               # kompletność/VPIN (hash_ok=True ⚠️)
ocena_pythia   = Pythia().ocen(odcisk, historia_pythia)       # fingerprint matching

opinia = RadaDoradcow().ocen(ocena_oracle, ocena_fulmen,
                             ocena_iustitia, ocena_hermes, ocena_pythia)

# 3. Skutek w dyrygencie:
if opinia.blokada:                       # < 3/5 lub IUSTITIA/HERMES weto
    return DecyzjaCyklu(..., "RADA_WETO")
if opinia.modyfikator_pozycji < 1.0:     # 3/5 lub 4/5 → przelicz plan mniejszą pozycją
    plan = kalkulator.policz(..., mnoznik_rozmiaru=opinia.modyfikator_pozycji)
```

**`OpinaRady`** (realne pola): `oracle` · `fulmen` · `iustitia` · `hermes` · `pythia` ·
`pozytywne` · `modyfikator_pozycji` · `blokada` · `powod_blokady` · `decyzja`.

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
