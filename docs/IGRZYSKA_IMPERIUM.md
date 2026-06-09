# 🏟️ IGRZYSKA IMPERIUM — System Rywalizacji i Rang

> *"Per certamen ad gloriam."* — Przez rywalizację do chwały.
>
> Każdy neuron, każdy legion, każdy senator walczy o pierwsze miejsce.
> Igrzyska sprawiają, że maszyna sama siebie doskonali — bez rozkazu z zewnątrz.

---

## 🎯 FILOZOFIA SYSTEMU

**Cel Igrzysk:**
1. Nagradzać najlepszych — automatyczne zwiększanie wag wygrywającym
2. Karać gorszych — redukcja wag, okres próbny, relegacja
3. Stworzyć samomotywującą się maszynę — system się sam kalibruje
4. Dać Cesarzowi jasny obraz — kto jest godny zaufania, kto zawodzi

**Trzy Areny Igrzysk:**

| Arena | Uczestnicy | Metryki | Częstotliwość |
|-------|-----------|---------|---------------|
| 🧬 **Arena Neuronów** | Mikro-neurony (299 w katalogu, 55 w kodzie) | Accuracy, Precision, F1, Contribution | Co 24h rolling |
| ⚔️ **Arena Legionów** | 4 Legiony + dywizje | Sharpe, WinRate, MaxDD, Calmar | Co tydzień |
| 🏛️ **Arena Senatu** | Senatorzy (głosy LONG/SHORT) | Głosowania vs wynik, kalibracja | Po każdym trade |

---

## 🧬 ARENA NEURONÓW

### Metryki Oceny Neuronu

Każdy neuron zbiera statystyki swoich sygnałów. Oceniany jest **wkład w trafność** — nie to czy sam miał rację, ale czy pomógł agregowanemu sygnałowi wygrać.

```
WYNIK_NEURONU = 0.30 × Accuracy
              + 0.25 × Precision_dominant
              + 0.20 × Contribution_Score    ← jak bardzo zmienił wynik agregacji
              + 0.15 × Timeliness            ← czy sygnał przyszedł przed ruchem
              + 0.10 × Stability             ← brak "migotania" (flip-flop)

Accuracy        = (TP + TN) / Total_signals
Precision       = TP / (TP + FP)
Contribution    = |pewnosc_z_neuronem - pewnosc_bez_neuronu|
Timeliness      = 1.0 jeśli sygnał ≥ 1 interwał przed ruchem, 0.5 jeśli jednocześnie
Stability       = 1 - (liczba_flipow / łączne_sygnały)
```

### System Rang Neuronów (Cursus Honorum Neuronalis)

| Ranga | Nazwa Łacińska | Polska | Próg WYNIK_NEURONU | Przywileje |
|-------|----------------|--------|---------------------|------------|
| 🏅 **V** | *Tiro* | Nowicjusz | < 0.45 | Waga ×0.5, tryb obserwacji |
| 🥉 **IV** | *Miles* | Żołnierz | 0.45–0.59 | Waga ×0.8, normalny udział |
| 🥈 **III** | *Optio* | Zastępca | 0.60–0.72 | Waga ×1.0, standard |
| 🥇 **II** | *Centurion* | Centurion | 0.73–0.84 | Waga ×1.3, +0.5 do bazowej wagi |
| 🏆 **I** | *Primus Pilus* | Pierwszy Włócznik | 0.85–0.92 | Waga ×1.6, raport do Senatu |
| 🌟 **S** | *Aquilifer* | Niosący Orła | ≥ 0.93 | Waga ×2.0, ZŁOTY HEŁM |

### Nagrody i Kary Neuronów

**🪖 ZŁOTY HEŁM** *(Cassis Aurea)*
- Przyznawany miesięcznie najlepszemu neuronowi (najwyższy WYNIK_NEURONU)
- Waga neuronu podwójona na następny miesiąc
- Wpisany do `PANTEON_NEURONOW.md` (Hall of Fame)
- Wagi innych neuronów tej samej kategorii wzmacniane +10%

**⚔️ SREBRNA WŁÓCZNIA** *(Hasta Argentea)*
- Dla neuronu z najwyższym Contribution_Score (zmienił wynik agregacji najbardziej)
- Typ "wildcard" — nawet słabszy neuron może wygrać tę nagrodę

**🛡️ TARCZA SPARTANA** *(Scutum Spartanum)*
- Dla neuronu z najwyższą Stability (zero flip-flopów przez cały miesiąc)
- Ważna w PANIKU i VOLATILE — stabilność = bezcenna

**⬇️ RELEGACJA** — Neuron z WYNIK < 0.40 przez 14 dni z rzędu:
1. Ostrzeżenie (żółta flaga): waga ×0.3
2. Kolejne 7 dni bez poprawy: tryb hibernacji (nie głosuje)
3. Kolejne 7 dni: usunięcie z aktywnego roju, przejście do `archiwum_neuronow/`

---

## ⚔️ ARENA LEGIONÓW

### Metryki Oceny Legionu

Każdy Legion to zbiór neuronów + ich strategii. Oceniany jako całość.

```
WYNIK_LEGIONU = 0.35 × Sharpe_ratio        (> 1.5 = bardzo dobry)
              + 0.25 × Calmar_ratio         (Roczny_zwrot / MaxDD)
              + 0.20 × Win_rate             (> 55% cel)
              + 0.20 × Profit_factor        (Gross_profit / Gross_loss, > 1.5 cel)

Wartości bazowe dla oceny (per 30 dni rolling):
  Sharpe   > 2.0  →  1.0 punktów | > 1.5 → 0.8 | > 1.0 → 0.6 | < 0.5 → 0.2
  Calmar   > 3.0  →  1.0 punktów | > 2.0 → 0.8 | > 1.0 → 0.6 | < 0.5 → 0.2
  WinRate  > 65%  →  1.0 punktów | > 55% → 0.8 | > 45% → 0.6 | < 40% → 0.2
  ProfFact > 2.0  →  1.0 punktów | > 1.5 → 0.8 | > 1.2 → 0.6 | < 1.0 → 0.2
```

### System Rang Legionów

| Ranga | Symbol | Polska | Próg WYNIK_LEGIONU | Status |
|-------|--------|--------|---------------------|--------|
| 🔴 | *Legio Damnata* | Legion Przeklęty | < 0.40 | Zawieszony — Generał Legatus investiguje |
| 🟡 | *Legio Probata* | Legion na Próbie | 0.40–0.59 | Ograniczone pozycje (50% normalnej dźwigni) |
| 🟢 | *Legio Ordinaria* | Legion Zwykły | 0.60–0.74 | Standard |
| 🔵 | *Legio Triumphalis* | Legion Triumfujący | 0.75–0.87 | +20% do alokacji kapitału |
| 🌟 | *Legio Invicta* | Legion Niezwyciężony | ≥ 0.88 | ZŁOTA ZBROJA, max alokacja |

### Nagrody Legionów

**🛡️ ZŁOTA ZBROJA** *(Lorica Aurea)*
- Miesięcznie — najlepszy WYNIK_LEGIONU
- Legion dostaje +30% alokacji kapitału na następny miesiąc
- Wpisany do `TRIUMPHI.md` (historia triumfów)

**🦅 ORZEŁ LEGIONOWY** *(Aquila Legionis)*
- Dla Legionu z najwyższym Sharpe ratio (jakość zwrotów)

**⛨ TARCZA NIEPOKONANYCH** *(Clypeus Invictorum)*
- Dla Legionu z najniższym MaxDD (ochrona kapitału)

---

## 🏛️ ARENA SENATU

### Metryki Oceny Senatora

Senator = agent (Populares/Optimates) głosujący LONG/SHORT/NEUTRAL.

```
WYNIK_SENATORA = 0.40 × Kalibracja         ← pewność vs rzeczywistość
               + 0.30 × Trafnosc_glosow    ← ile głosów okazało się trafnych
               + 0.20 × Roznicowanie       ← jak różni się od większości (diversification)
               + 0.10 × Szybkosc           ← pierwsza analiza przed innymi

Kalibracja (Brier Score odwrócony):
  "Powiedziałem LONG z pewnością 80%, BTC wzrósł" → kalibracja dobra
  "Powiedziałem LONG z pewnością 80%, BTC spadł" → kalibracja zła

Roznicowanie:
  Senator który mówi coś innego niż 70%+ reszty i ma rację
  → dostaje bonus × 1.5 (wartościowa opinia mniejszości)
```

### System Rang Senatorów

| Ranga | Tytuł | Polska | Próg WYNIK_SENATORA |
|-------|-------|--------|---------------------|
| 🟤 | *Tribunus Plebis* | Trybun Ludu | < 0.45 |
| ⚪ | *Senator Ordinarius* | Senator Zwykły | 0.45–0.60 |
| 🔵 | *Senator Consularis* | Senator Konsularny | 0.61–0.75 |
| 🟡 | *Praetor* | Pretor | 0.76–0.87 |
| 🔴 | *Consul* | Konsul | ≥ 0.88 |
| 🌟 | *Princeps Senatus* | Pierwszy Senator | najwyższy w miesiącu |

**🏺 PURPURA SENATU** *(Toga Purpurea)*
- Dla Princeps Senatus — senator miesiąca
- Jego waga głosu ×2.0 w następnym miesiącu
- Zapisany w `ALBUM_SENATUS.md`

---

## 📊 TABELA LIDERÓW — KAPITOL (Dashboard)

```
╔══════════════════════════════════════════════════════════════════════╗
║                    🏛️  KAPITOL IMPERIUM — LIDERZY                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  Neuron Miesiąca: [KLUCZ]  [NAZWA]  ........  🪖 ZŁOTY HEŁM         ║
║  Legion Miesiąca: [NAZWA]  [WYNIK]  ........  🛡️ ZŁOTA ZBROJA       ║
║  Senator Miesiąca: [ID]   [WYNIK]  ........  🏺 PURPURA SENATU      ║
╠══════════════════════════════════════════════════════════════════════╣
║  TOP 5 Neuronów (Aquilifer):                                         ║
║   1. [klucz] [nazwa] [wynik] [ranga]                                 ║
║   2. ...                                                             ║
║                                                                      ║
║  RELEGOWANI (hibernacja):                                            ║
║   - [klucz] [nazwa] — powód — data relegacji                         ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## ⚡ KIJ I MARCHEWKA — System Pełny

> *"Praemia et poenae duces exercitus sunt."* — Nagrody i kary są wodzami armii.

Samo nagradzanie nie wystarczy. Kara musi boleć — inaczej system się nie kalibruje.

---

### 🥕 MARCHEWKA (nagrody — już zdefiniowane powyżej):
- Złoty Hełm, Srebrna Włócznia, Tarcza Spartana (neurony)
- Złota Zbroja, Orzeł Legionowy (legiony)
- Purpura Senatu (senatorzy)
- Automatyczne zwiększenie wag i alokacji kapitału

---

### 🪄 KIJ — System Kar Progresywnych

#### Poziomy Hańby (Neuron)

| Poziom | Trigger | Kara | Nazwa |
|--------|---------|------|-------|
| ⚠️ **Ostrzeżenie** | WYNIK < 0.45 przez 7 dni | Waga ×0.5, żółta flaga w logu | *Ignominia* |
| 🔴 **Infamia** | WYNIK < 0.40 przez 14 dni | Waga ×0.2, wpis na Listę Infamii | *Infamia Publica* |
| ⚫ **Hibernacja** | Brak poprawy 7 dni po Infamii | Nie głosuje, obserwuje cicho | *Exilium Temporale* |
| 💀 **Relegacja** | Brak poprawy 7 dni po Hibernacji | Usunięty do `archiwum_neuronow/` | *Damnatio Memoriae* |

#### Ceremonia Hańby *(Cerimonia Ignominiae)*

Gdy neuron trafia na Listę Infamii, system generuje **Raport Hańby**:
```
╔══════════════════════════════════════════════════════════╗
║         ⚫ LISTA INFAMII — RAPORT HAŃBY                  ║
║  Neuron: [KLUCZ] [NAZWA]                                 ║
║  WYNIK: [X.XX] | Próg: 0.40 | Dni poniżej: [N]          ║
║  Najczęstszy błąd: [np. "flip-flop w RANGING reżimie"]   ║
║  Waga obniżona: [stara] → [nowa]                         ║
║  Status: INFAMIA | Szansa na rehabilitację: [dni]        ║
╚══════════════════════════════════════════════════════════╝
```

#### Zasada Pokuty *(Lex Paenitentiae)*

Neuron relegowany może wrócić przez:
1. **7 dni obserwacji** — śledzi rynek, nie głosuje, uczy się
2. **7 dni warunkowych** — głosuje z wagą ×0.3, wynik monitorowany co 24h
3. **Przywrócenie** — jeśli WYNIK ≥ 0.55 przez 7 dni → pełny powrót ze statusem *"Restitutus"*
4. **Podwójna czujność** — przez następny miesiąc próg relegacji podniesiony do 0.45 (surowszy nadzór)

---

### ⚡ KIJ DLA LEGIONÓW

| Sytuacja | Kara |
|----------|------|
| WYNIK_LEGIONU < 0.40 przez 14 dni | Legio Damnata — zawieszony, zero nowych pozycji |
| MaxDD > 20% w miesiącu | Natychmiastowe zamrożenie do wyjaśnienia przez Legatusa |
| 3× z rzędu ujemny tydzień | Przegląd strategii — mandatory Koloseum re-test |
| WinRate < 35% przez miesiąc | Redukcja alokacji do 25% normalnej |

**Rytuał Pokuty Legionu** *(Supplicatio)*:
Po relegacji Legion musi "wygrać 3 tygodnie z rzędu" z WinRate > 50% zanim wróci do pełnej alokacji. Każdy tydzień poniżej normy resetuje licznik.

---

### ⚡ KIJ DLA SENATORÓW

| Sytuacja | Kara |
|----------|------|
| WYNIK_SENATORA < 0.40 | Waga głosu ×0.3 ("Senator Milczący") |
| 5× z rzędu błędne głosowanie | Czasowe zawieszenie z głosowania (48h) |
| Kalibracja < 0.30 (mówi 90% pewności ale zawsze się myli) | Waga stała ×0.1 przez tydzień |

---

### 📋 LISTA INFAMII — Format Wpisu

Plik `imperium/biblioteki/igrzyska/LISTA_INFAMII.jsonl`:
```json
{
  "timestamp": "2026-06-01T10:00:00Z",
  "typ": "NEURON",
  "klucz": "X-07",
  "nazwa": "Williams %R",
  "wynik_14d": 0.38,
  "powod": "flip-flop w RANGING — 23 zmiany kierunku w 7 dni",
  "kara": "INFAMIA",
  "waga_przed": 5,
  "waga_po": 1,
  "rehabilitacja_mozliwa_od": "2026-06-08"
}
```

---

## 🏆 PANTEON — Hall of Fame

### `PANTEON_NEURONOW.md` — Złote Hełmy historyczne
Każdy wpis zawiera: miesiąc, klucz neuronu, wynik, najważniejszą zasługę.

### `TRIUMPHI.md` — Triumfy Legionów
Format Triumf Rzymski: legion, data, powód triumfu, metryki które go uzasadniły.

### `ALBUM_SENATUS.md` — Purpury Senatu
Historia najlepszych głosowań senatorów z dokładnymi cytatami analiz.

---

## ⚙️ MECHANIZM AUTOMATYCZNY

### Auto-kalibracja wag po Igrzyskach

```python
# Po każdym cyklu (24h dla neuronów, 7d dla legionów):
def aktualizuj_wagi_po_igrzyskach(wyniki: dict) -> dict:
    for klucz, wynik in wyniki.items():
        ranga = okresl_range(wynik)
        mnoznik = MNOZNIKI_RANG[ranga]         # z tabeli rang powyżej
        nowa_waga = round(bazowa_waga[klucz] * mnoznik)
        nowa_waga = max(1, min(10, nowa_waga)) # clamp 1-10
    return nowe_wagi

MNOZNIKI_RANG = {
    "Tiro":       0.50,
    "Miles":      0.80,
    "Optio":      1.00,
    "Centurion":  1.30,
    "PrimusPilus":1.60,
    "Aquilifer":  2.00,
}
```

### Zasada Zazdrosnych Neuronów

Kiedy neuron widzi że inny ma ZŁOTY HEŁM → jego sygnały dostają automatycznie +5% Timeliness bonus przez 7 dni.  
To napędza rywalizację: **każdy chce być pierwszy**.

### Zasada Pokuty

Neuron relegowany może powrócić przez:
1. 7 dni w trybie "cichej obserwacji" (nie głosuje, ale śledzi)
2. Następnie 7 dni "warunkowego" powrotu (waga ×0.3)
3. Pełne przywrócenie jeśli WYNIK ≥ 0.55 przez 7 dni

---

## 📐 INTEGRACJA Z LEGATUSEM

Generał Legatus automatycznie:
1. Przed każdą agregacją pobiera aktualne wagi z Igrzysk
2. Po każdej sesji tradingowej wysyła feedback do Igrzysk (jaki był wynik)
3. Raz na dobę generuje raport Igrzysk i wysyła do `biblioteki/`

```python
# W legatus.py — rozszerzenie:
def fokus_z_igrzyskami(self, symbol, wskazniki, rezim, igrzyska):
    wagi_live = igrzyska.pobierz_aktualne_wagi()
    for neuron in self.roj.neurony:
        neuron.waga = wagi_live.get(neuron.KLUCZ, neuron.waga)
    return self.fokus(symbol, wskazniki, rezim)
```

---

*"Agonem vincit qui meretur." — Igrzyska wygrywa ten, kto na to zasługuje.*

*— IGRZYSKA_IMPERIUM.md | v1.1 | 2026-06-04*

---

## 🤖 HedgeMWU — Online Learning (W-049)

> **Co to jest:** Multiplicative Weights Update (MWU) — algorytm online uczenia się z teoretyczną
> gwarancją regretu O(√(T·ln N)).
> Źródło: Freund & Schapire (1997) — https://doi.org/10.1006/jcss.1997.1504

### Gdzie: `imperium/biblioteki/hedge_mwu.py`

**Klasa:** `HedgeMWU(eta=0.5)`

- `eta` — tempo uczenia (>0); domyślnie 0.5 (rozsądny balans szybkości i stabilności)
- `min_waga` — podłoga wagi (ekspert nigdy nie umiera całkowicie, może wrócić do łask)

### Jak działa

Każdy neuron to "ekspert". Po każdym rozstrzygniętym trade'cie:
- Neuron który trafił kierunek → waga utrzymana
- Neuron który się pomylił → waga mnożona przez `exp(-η)` (wykładnicze obniżenie)

Po wielu rundach wagi samoistnie wyłaniają najlepsze neurony — bez ręcznego strojenia.

### Różnica od Igrzysk (oba są komplementarne, Prawo XVI)

| | Igrzyska | HedgeMWU |
|-|----------|----------|
| Tryb | BATCH (np. co 30 dni) | ONLINE (po każdym wyniku) |
| Rangi | Dyskretne (Tiro→Aquilifer) | Ciągłe wagi |
| Gwarancja | Brak (empiryczna) | Regret O(√(T·ln N)) |
| Informacja | Kompleksowy WYNIK_NEURONU | Czysta trafność kierunku |

### Integracja przez Igrzyska.obserwatorzy (wzorzec DRY)

```python
ig = Igrzyska()
mwu = HedgeMWU(eta=0.5)
ig.obserwatorzy.append(mwu)   # MWU dostaje ten sam strumień wyników

ig.przetworz_logi(logi)       # → zarejestruj_wynik() notyfikuje wszystkich obserwatorów
```

Pole `Igrzyska.obserwatorzy: list` — każdy obiekt na liście musi implementować
`zarejestruj_wynik(klucz, kierunek, zyskowny_kierunek, contribution, timeliness)`.
DRY: logika parowania SYGNAŁ↔TRADE_CLOSE nie jest duplikowana — MWU dostaje dokładnie
ten sam strumień wyników co Igrzyska.

### HedgeMWU.mnozniki() → dict[klucz → float]

```python
mnozniki = mwu.mnozniki()
# → {"X-01": 1.42, "X-02": 1.01, "X-07": 0.63, ...}
# Neutralny stan (równe wagi, brak danych): wszystkie = 1.0
# Trafni eksperci: > 1.0 | Mylący się: < 1.0
```

Stan neutralny (brak historii lub równe wagi) zwraca `1.0` dla każdego neuronu —
Legatus działa jak bez MWU (Prawo XV: brak zniekształcenia przy braku danych).

### Jak Legatus konsumuje mnożniki

```python
legatus.ustaw_mnozniki_neuronow(mwu.mnozniki())
# Wewnętrznie _dostosuj_wagi() mnoży: waga_finalna = waga_rezimu × mnoznik_mwu
```

Metoda `ustaw_mnozniki_neuronow(mnozniki: dict)` przechowuje mnożniki w `Legatus`.
Przy kolejnej agregacji `_dostosuj_wagi()` mnoży wagę reżimową przez per-neuronowy
mnożnik online-uczenia — efekt: trafne neurony mają zawsze wyższy głos.

### Zapis z logów historycznych

```python
mwu = HedgeMWU.z_logow(logi, eta=0.5)
# → buduje MWU ze strumienia logów, używa tej samej logiki co Igrzyska (DRY)
```
