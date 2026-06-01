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
| 🧬 **Arena Neuronów** | Mikro-neurony (303+) | Accuracy, Precision, F1, Contribution | Co 24h rolling |
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

*— IGRZYSKA_IMPERIUM.md | v1.0 | 2026-06-01*
