---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/pretorianie/kalkulator_lewara.py
stan_na: 2026-07-17
powod_istnienia: "Jedyny dokument z pełną 'matematyką przeżycia' pozycji lewarowanej — od ceny likwidacji przez stop-loss, dynamiczną dźwignię, zarządzanie kapitałem (2%), take-profit, checklist Pretorianów"
---
# ⚖️ KALKULATOR LEWARA — Matematyka Przeżycia

> **Zasada Żelazna:** Zanim wejdziesz w pozycję lewarowaną — MUSISZ znać dokładną cenę likwidacji.
> Jeśli system nie policzy likwidacji → pozycja NIE wchodzi. Bezwzględnie.

> **⚠️ Jak czytać (weryfikacja wobec kodu 2026-07-17).** Bloki `python` poniżej są
> **ilustracją wzoru, nie kopią kodu** — źródłem prawdy jest zawsze
> [`kalkulator_lewara.py`](../imperium/pretorianie/kalkulator_lewara.py). Poprzednia wersja
> (2026-06-04) podawała funkcję `policz_dzwignie()`, której **nie ma w kodzie**, i twierdziła,
> że w reżimie PANIC handlujemy dźwignią 1× — **realnie PANIC to ZERO pozycji** (kod jest
> ostrożniejszy niż był ten opis). Sprostowane niżej; dopisano też sekcję §11 z mechanizmami
> ryzyka, których dokument w ogóle nie znał (Reguła 6% Eldera, sizing frakcyjny po DD,
> volatility drag, Kelly ze skośnością, SL oparty na ATR).

---

## 📐 WZORY PODSTAWOWE

### Cena Likwidacji (Isolated Margin)

```
LONG:  Likwidacja = Cena_Wejścia × (1 - 1/Dźwignia + Opłata_Utrzymania)
SHORT: Likwidacja = Cena_Wejścia × (1 + 1/Dźwignia - Opłata_Utrzymania)
```

**Uproszczone (Opłata_Utrzymania ≈ 0.5%):**
```
LONG:  Likwidacja ≈ Cena_Wejścia × (1 - 1/Dźwignia + 0.005)
SHORT: Likwidacja ≈ Cena_Wejścia × (1 + 1/Dźwignia - 0.005)
```

### Przykład (BTC = 100 000 USDT, dźwignia 10×):
```
LONG:  100 000 × (1 - 0.10 + 0.005) = 100 000 × 0.905 = 90 500 USDT
SHORT: 100 000 × (1 + 0.10 - 0.005) = 100 000 × 1.095 = 109 500 USDT
```

---

## 📊 TABELA LIKWIDACJI — BTC = 100 000 USDT

| Dźwignia | Ruch do likwidacji LONG | Cena likwidacji LONG | Ruch do likwidacji SHORT | Cena likwidacji SHORT |
|----------|------------------------|---------------------|------------------------|----------------------|
| 2×  | -49.5% | 50 500 | +49.5% | 149 500 |
| 5×  | -19.5% | 80 500 | +19.5% | 119 500 |
| 10× | -9.5%  | 90 500 | +9.5%  | 109 500 |
| 15× | -6.2%  | 93 800 | +6.2%  | 106 200 |
| 20× | -4.5%  | 95 500 | +4.5%  | 104 500 |
| 50× | -1.5%  | 98 500 | +1.5%  | 101 500 |

> **Uwaga:** Przy 20× wystarczy ruch o 4.5% aby stracić wszystko. Krypto często robi to w minuty.

---

## 🛡️ STOP-LOSS — Relacja do Likwidacji

**Zasada Żelazna II:** Stop-loss ZAWSZE między ceną wejścia a ceną likwidacji.
Nigdy nie pozwalamy, żeby cena dotarła do likwidacji.

```
LONG:
  Cena Wejścia ──────── STOP-LOSS ──────── LIKWIDACJA
                 ← bufor bezpieczeństwa →
                 minimum 20% odległości do likwidacji

SHORT:
  LIKWIDACJA ──────── STOP-LOSS ──────── Cena Wejścia
```

### Schemat ustawiania Stop-Lossa

```python
# Dla LONG:
odleglosc_likwidacji = cena_wejscia - cena_likwidacji
stop_loss = cena_wejscia - (odleglosc_likwidacji * 0.5)  # 50% drogi do likwidacji

# Dla SHORT:
odleglosc_likwidacji = cena_likwidacji - cena_wejscia
stop_loss = cena_wejscia + (odleglosc_likwidacji * 0.5)  # 50% drogi do likwidacji
```

### Przykład (BTC 100 000, LONG 10×):
```
Likwidacja: 90 500 USDT
Odległość do likwidacji: 9 500 USDT (9.5%)
Stop-loss: 100 000 - (9 500 × 0.5) = 95 250 USDT
Stop-loss chroni: 47 500 / (9 500 + 47 500) USDT  ✅
```

---

## 🔥 DYNAMICZNA DŹWIGNIA — Płynna Regulacja

Dźwignia NIE jest stała. Generał dostosowuje ją do siły sygnału.

### Tabela Dźwigni vs Pewność Sygnału

| Pewność Agregatu | Dźwignia Rekomendowana | Uzasadnienie |
|------------------|----------------------|--------------|
| < 0.55 | 0× (nie handluj) | Zbyt mało pewności — szum |
| 0.55–0.65 | 1×–2× | Słaby sygnał — minimalne ryzyko |
| 0.65–0.75 | 2×–5× | Dobry sygnał — ostrożna dźwignia |
| 0.75–0.85 | 5×–10× | Silny sygnał — standardowa dźwignia |
| 0.85–0.92 | 10×–15× | Bardzo silny — zwiększona dźwignia |
| > 0.92 | 15×–20× | Wyjątkowy sygnał — maksymalna dźwignia |

**Korektory reżimu rynku (mnożniki — zgodne z kodem):**
- VOLATILE: ×0.5 · **PANIC: ×0.1** · RANGING: ×0.7 · TREND_STRONG: ×1.2 · NORMAL: ×1.0 · ON-CHAIN_BULLISH: ×1.1

> 🚨 **Sprostowanie 2026-07-17 — PANIC.** Poprzednia wersja pisała *„PANIC: dźwignia = 1×
> maksymalnie"*, co sugerowało, że w panice **handlujemy** małą dźwignią. **Nieprawda —
> w PANIC nie wchodzimy wcale:** `_checklist()` wetuje twardo („Reżim PANIC — zero pozycji
> lewarowanych"). Mnożnik ×0.1 nigdy nie decyduje, bo pozycja jest odrzucana wcześniej.
> Kod jest **bezpieczniejszy**, niż głosił ten dokument.

### Wzór na Dźwignię Dynamiczną — `KalkulatorLewara.auto_dzwignia()`

Realna sygnatura (staticmethod; **nie** `policz_dzwignie(...)` i **bez** `pretorianie_ok` —
weto żyje w checkliście, nie tutaj):

```python
@staticmethod
def auto_dzwignia(pewnosc: float, rezim: str = "NORMAL") -> int:
    if pewnosc < 0.55:   baza = 0
    elif pewnosc < 0.65: baza = 2
    elif pewnosc < 0.75: baza = 5
    elif pewnosc < 0.85: baza = 10
    elif pewnosc < 0.92: baza = 15
    else:                baza = 20
    korektor = {"VOLATILE": 0.5, "PANIC": 0.1, "RANGING": 0.7,
                "TREND_STRONG": 1.2, "NORMAL": 1.0, "ON-CHAIN_BULLISH": 1.1}.get(rezim, 1.0)
    return min(max(int(baza * korektor), 1), MAX_DZWIGNIA)   # clamp 1–20
```

> ⚠️ **Granica, która myli (zmierzone):** tabela mówi „< 0.55 → 0× (nie handluj)", ale
> `auto_dzwignia(0.10)` **zwraca 1**, nie 0 — bo `max(..., 1)` przycina do jedynki.
> Słaby sygnał NIE jest odrzucany przez dźwignię, tylko przez **osobne weto w checkliście**
> („Zbyt słaby sygnał: 10% < 55%"). Skutek jest właściwy (pozycja nie wchodzi), ale mechanizm
> jest inny, niż opisywał ten dokument — nie licz na to, że zwrócone `0` gdziekolwiek zablokuje
> wejście, bo `auto_dzwignia` nigdy nie zwraca zera.

---

## 💰 ZARZĄDZANIE KAPITAŁEM — Zasada 2%

**Nigdy nie ryzykujemy więcej niż 2% kapitału całkowitego na jedną pozycję.**

```python
def policz_rozmiar_pozycji(kapital_usdt: float, stop_loss_procent: float,
                            ryzyko_max: float = 0.02) -> float:
    """
    kapital_usdt: cały kapitał portfela
    stop_loss_procent: ile % od wejścia do stop-lossa (np. 0.05 = 5%)
    ryzyko_max: max 2% kapitału na trade
    """
    strata_max = kapital_usdt * ryzyko_max
    rozmiar = strata_max / stop_loss_procent
    return rozmiar
```

### Przykład:
```
Kapitał: 10 000 USDT
Stop-loss: 4.75% od wejścia (BTC 10×, stop przy 95 250)
Max strata: 10 000 × 2% = 200 USDT
Rozmiar pozycji: 200 / 0.0475 = 4 210 USDT
```

---

## 🎯 ROZKAZ FLANKI — Zlecenia Wokół Pozycji

Dla każdej pozycji Kalkulator generuje trzy zlecenia:

```
1. ENTRY — zlecenie wejścia (limit lub market)
2. STOP-LOSS — zlecenie ochrony (always first!)
3. TAKE-PROFIT — cel zysku (R:R minimum 1:2)
```

### Take-Profit (minimum R:R 1:2)

```python
# LONG:
ryzyko = cena_wejscia - stop_loss
take_profit = cena_wejscia + (ryzyko * 2)  # minimum 2:1

# SHORT:
ryzyko = stop_loss - cena_wejscia
take_profit = cena_wejscia - (ryzyko * 2)
```

### Przykład pełny (BTC LONG 10×):
```
Wejście:     100 000 USDT
Stop-Loss:    95 250 USDT (−4.75%)
Likwidacja:   90 500 USDT (−9.5%) ← stop jest zanim tu dotrzemy
Take-Profit: 109 500 USDT (+9.5%) ← R:R = 2:1
```

---

## ✅ CHECKLIST PRZED WEJŚCIEM — `_checklist()` (zweryfikowana 2026-07-17)

**To jest pełna lista wet w kodzie.** Kolejność jak w `_checklist()`; pierwsze trafienie
wygrywa i wypełnia `powod_veto` (a `checklist_ok=False`):

| # | Weto gdy… | Komunikat |
|---|---|---|
| 1 | Breaker krzywej w **HALT** (equity DD ≥ 20%) | `🛑 BREAKER KRZYWEJ: HALT — nowe wejścia wstrzymane` |
| 2 | **Bezpiecznik AOA przepalony** (DD ≥ 30%) | `🛑 BEZPIECZNIK AOA przepalony` — wymaga ręcznego resetu |
| 3 | `pretorianie_ok = False` | `Pretorianie nałożyli VETO (warunki zewnętrzne)` |
| 4 | **`rezim == "PANIC"`** | `Reżim PANIC — zero pozycji lewarowanych` |
| 5 | `dzwignia > 20` (`MAX_DZWIGNIA`) | `Dźwignia N× przekracza max 20×` |
| 6 | **`pewnosc < 0.55`** | `Zbyt słaby sygnał: N% < 55%` |
| 7 | **bufor do likwidacji < 20%** | `Bufor do likwidacji zbyt mały: N% < 20%` |
| 8 | `rozmiar > 50% kapitału` | `Pozycja zbyt duża vs kapitał` |

**Czego w checkliście NIE MA** (poprzednia wersja dokumentu obiecywała te bramki — to była
lista życzeń, nie kod):
- 🔴 **Funding Rate** i 🔴 **ATR < 2× średniej** — kalkulator ich nie wetuje. ATR jest używany,
  ale wyłącznie do *wyliczenia* stop-lossa (`atr` + `sl_atr_mult`, §11), nie jako bramka.
- 🔴 **Seria strat < 3** — nie ma w kalkulatorze (pokrewne: `RegulaSzesciuProcentEldera`, §11).
- ⚠️ **„Rozmiar ≤ 2% kapitału"** — mieszało dwie rzeczy. `MAX_RYZYKO = 0.02` ogranicza **ryzyko**
  (maksymalną stratę na stopie), a nie rozmiar pozycji; checklist wetuje dopiero **rozmiar > 50%
  kapitału**. Przy stopie 4.75% pozycja 2%-ryzyka ma rozmiar ~42% kapitału — i to jest legalne.
- ⚠️ **„Drawdown < 10%"** — 10% DD **nie wetuje**, tylko przełącza breaker w REDUCED (rozmiar ×0.5).
  Weto zaczyna się przy 20% (HALT), a twardy stop AOA przy 30%.
- ⚠️ **„R:R ≥ 1:2"** — `MIN_RR = 2.0` istnieje jako stała i `rr_ratio` jest liczone w planie,
  ale **checklist tego nie wetuje**. Take-profit jest z definicji stawiany na 2×ryzyko, więc
  R:R wychodzi 2:1 z konstrukcji — dopóki nikt nie poda własnego TP.

---

## 📁 Plik kodu: `imperium/pretorianie/kalkulator_lewara.py`

**Pełny `PlanPozycji` (16 pól — zweryfikowane `dataclasses.fields`):**

```python
@dataclass
class PlanPozycji:
    symbol: str
    kierunek: str               # LONG / SHORT
    cena_wejscia: float
    dzwignia: int
    cena_likwidacji: float
    stop_loss: float
    take_profit: float
    rozmiar_usdt: float
    ryzyko_usdt: float          # max strata w USDT
    rr_ratio: float             # Risk:Reward
    bufor_likwidacji_pct: float # ← ile % drogi do likwidacji zostaje za stopem (weto <20%)
    checklist_ok: bool
    powod_veto: str             # "" jeśli OK
    skala_vol: float = 1.0      # volatility targeting (W-059)
    frakcja_breaker: float = 1.0  # equity-curve breaker (W-062): 1.0/0.5/0.0
    frakcja_dd: float = 1.0     # ← drawdown-fractional sizing (W-063)
    drag_roczny: float | None = None   # ← koszt zmienności przy tej dźwigni (§11)
```

**Stałe modułu (zweryfikowane):** `OPLATA_UTRZYMANIA = 0.005` *(uwaga: poprzednia wersja
dokumentu pisała `OPLATE_UTRZYMANIA` — taka nazwa nie istnieje)* · `MAX_DZWIGNIA = 20` ·
`MAX_RYZYKO = 0.02` · `MIN_RR = 2.0` · `MAX_DRAWDOWN_STOP = 0.3` · `VOL_TARGET_DEFAULT = 0.6` ·
`SKALA_VOL_MIN = 0.25` · `SKALA_VOL_MAX = 1.5` · `DRAG_ROCZNY_OSTRZEZENIE = 0.5`.

**Realna sygnatura `policz()`** — wszystkie bezpieczniki wchodzą tu jako opt-in (None = wyłączony):

```python
def policz(self, symbol, kierunek, cena_wejscia, dzwignia, kapital_usdt,
           pewnosc=0.7, rezim="NORMAL", pretorianie_ok=True,
           bezpiecznik=None,          # BezpiecznikKapitalu (AOA W-028, twardy stop 30%)
           vol_realized=None, vol_target=0.6,   # volatility targeting (W-059)
           breaker_krzywej=None,      # BezpiecznikKrzywejKapitalu (W-062)
           skalowanie_dd=None,        # SkalowanieFrakcjaDD (W-063)
           max_drag_roczny=None,      # próg volatility drag (§11)
           regula_6pct=None,          # RegulaSzesciuProcentEldera (§11)
           atr=None, sl_atr_mult=None,   # stop-loss oparty na ATR (§11)
           mnoznik_rozmiaru=1.0) -> PlanPozycji:
```

---

*"Znaj cenę likwidacji zanim wejdziesz. Żołnierz który nie wie gdzie jest przepaść, w nią wpada."* — VITRUVIUSZ

---

## 📐 Volatility Targeting (W-059)

> **Cel:** Rozmiar pozycji rośnie, gdy rynek jest spokojny; maleje, gdy rynek jest zmienny.
> Instytucjonalny standard — pozycja skalowana tak, by ryzyko (mierzone zmiennością) było stałe.

### Stałe

| Stała | Wartość | Znaczenie |
|-------|---------|-----------|
| `VOL_TARGET_DEFAULT` | `0.60` | 60% annualizowanej zmienności — typowy cel portfela krypto |
| `SKALA_VOL_MIN` | `0.25` | Minimalna skala — nigdy nie zejdź poniżej 1/4 bazowego rozmiaru |
| `SKALA_VOL_MAX` | `1.50` | Maksymalna skala — ostrożność ponad chciwość |

### Wzór

```
skala_vol = clip(vol_target / vol_realized, SKALA_VOL_MIN, SKALA_VOL_MAX)
rozmiar_pozycji = rozmiar_bazowy × skala_vol
```

- `vol_realized` — annualizowana realized vol (np. `YANG_ZHANG_20` z Bramy, W-055)
- `vol_target` — cel zmienności portfela (default 60%)
- Wynik przycięty do `[0.25, 1.50]`

**Przykłady:**
```
vol_target=0.60, vol_realized=1.20 → skala = 0.50 (rynek 2× bardziej zmienny → pozycja o połowę mniejsza)
vol_target=0.60, vol_realized=0.30 → skala = 1.50 (rynek 2× spokojniejszy → MAX skala)
vol_target=0.60, vol_realized=0.60 → skala = 1.00 (neutralnie)
```

### PlanPozycji.skala_vol

```python
@dataclass
class PlanPozycji:
    ...
    skala_vol: float = 1.0  # mnożnik volatility-targeting (W-059); 1.0 = brak skalowania
```

Pole `skala_vol` jest zawsze widoczne w raporcie `drukuj_plan()` jako `(vol×X.XX)`.

### Jak policz() przyjmuje parametry vol

```python
def policz(self, symbol, kierunek, cena_wejscia, dzwignia, kapital_usdt,
           pewnosc=0.7, rezim="NORMAL", pretorianie_ok=True,
           bezpiecznik=None,
           vol_realized=None,          # ← None = brak danych = skala 1.0
           vol_target=VOL_TARGET_DEFAULT) -> PlanPozycji:
```

### Zachowanie gdy vol_realized jest None lub ≤ 0

Gdy `vol_realized` jest `None` lub `≤ 0` — `skala_vol` = `1.0` (brak skalowania).
Kompatybilność wsteczna: stary kod bez vol_realized działa identycznie jak przed wdrożeniem W-059.

### Metoda statyczna skala_vol_targeting()

```python
@staticmethod
def skala_vol_targeting(vol_realized: float | None,
                        vol_target: float = VOL_TARGET_DEFAULT) -> float:
    """
    Mnożnik rozmiaru = vol_target / vol_realized, przycięty do [MIN, MAX].
    vol_realized: None/≤0 → skala 1.0 (brak danych → neutralnie).
    """
    if vol_realized is None or vol_realized <= 0 or vol_target <= 0:
        return 1.0
    skala = vol_target / vol_realized
    return max(SKALA_VOL_MIN, min(SKALA_VOL_MAX, skala))
```

### Źródło danych

`vol_realized` dostarcza Brama Kalkulatora jako `YANG_ZHANG_20` (W-055) — ta sama skala annualizowana co `VOL_TARGET_DEFAULT`. Można podać dowolną inną annualizowaną vol (np. 30-dniową realized vol z własnego obliczenia).

---

## 🔻 Equity-Curve Circuit Breaker (W-062)

**Klasa:** `BezpiecznikKrzywejKapitalu` w `imperium/pretorianie/kalkulator_lewara.py`

DLA NOWICJUSZA: ten bezpiecznik traktuje **własną krzywą kapitału roju** jak instrument. Liczy średnią kroczącą (MA = Moving Average) na punktach kapitału i pilnuje obsunięcia (drawdown) od szczytu. Realizacja Prawa XV (ochrona potencjału) w kodzie.

### Trzy stany

| Stan | Warunek | Mnożnik rozmiaru | Wejścia |
|------|---------|------------------|---------|
| **NORMAL** | kapitał ≥ MA **i** DD < `prog_dd_reduced` | ×1.0 | dozwolone |
| **REDUCED** | DD ≥ `prog_dd_reduced` **lub** kapitał < MA (przy pełnym oknie) | ×`frakcja_reduced` (0.5) | dozwolone, połowa rozmiaru |
| **HALT** | DD ≥ `prog_dd_halt` | ×0.0 | **zablokowane** (weto w checklist) |

### Progi (domyślne)

- `okno_ma = 20` — okno MA na krzywej kapitału
- `prog_dd_reduced = 0.10` — 10% DD → REDUCED
- `prog_dd_halt = 0.20` — 20% DD → HALT
- `frakcja_reduced = 0.5` — połowa rozmiaru w REDUCED

### Histereza

Z HALT wychodzimy dopiero gdy DD spadnie **poniżej** `prog_dd_reduced` (nie na samej granicy progu HALT) — żeby nie migotać NORMAL↔HALT na granicy.

### Gdzie się plasuje w stosie ryzyka

Ten bezpiecznik siedzi **PONAD** twardym `BezpiecznikKapitalu` (reguła AOA W-028, twardy STOP przy 30% obsunięciu). Jest warstwą **miększą**, reagującą **wcześniej**: najpierw przycina rozmiar (REDUCED przy 10%), potem wstrzymuje wejścia (HALT przy 20%), zanim AOA przepali się twardo przy 30%.

### Integracja

- `KalkulatorLewara.policz(..., breaker_krzywej=...)` — REDUCED mnoży `rozmiar_usdt` przez `frakcja_pozycji()`; HALT → weto w `_checklist()` (`powod_veto` zawiera "BREAKER KRZYWEJ: HALT").
- `PlanPozycji.frakcja_breaker` — widoczny mnożnik (1.0=NORMAL, 0.5=REDUCED, 0.0=HALT).
- `Dyrygent(breaker_krzywej=True)` — instancjonuje breaker, woła `.aktualizuj(engine.kapital)` w każdym cyklu przed sizingiem i przekazuje do `policz()`. `breaker_krzywej=False` wyłącza (opt-out).

### Źródło

⚠️ To ugruntowana praktyka system-tradingu (traktowanie equity curve jak instrumentu + MA filter), **nie** pojedyncza recenzowana publikacja peer-review.

---

## 11. Mechanizmy, których ten dokument nie znał (dopisane 2026-07-17)

Poniższe **żyją w kodzie od dawna**, a dokument — mieniący się „pełną matematyką przeżycia" —
milczał o nich. Wszystkie są **opt-in** w `policz()` (parametr `None` = wyłączony), zgodnie
z ZASADĄ WPIĘCIA.

### 11a. Reguła 6% Eldera — `RegulaSzesciuProcentEldera` (BIB-015)

Miesięczny meta-limit: gdy strata **od początku miesiąca** ≥ `prog` (domyślnie **6%**) → **HALT**
do nowego miesiąca. Elder: przy takiej stracie umysł przechodzi w tryb „muszę odrobić" i
podejmuje złe decyzje. `aktualizuj(kapital, dzisiaj)` zwraca stan; `reset_miesiac()` startuje
nowy okres. Trzy horyzonty ochrony są **komplementarne**, nie konkurencyjne:

| Warstwa | Horyzont | Próg |
|---|---|---|
| `RegulaSzesciuProcentEldera` | **miesiąc** (najszerszy) | 6% straty miesięcznej → HALT |
| `BezpiecznikKrzywejKapitalu` (W-062) | bieżąca krzywa equity | 10% → REDUCED, 20% → HALT |
| `BezpiecznikKapitalu` (AOA, W-028) | całość kapitału | **30% → twardy stop**, ręczny reset |

> ⚠️ Klasa ta ma udokumentowaną historię buga: *„HALT zdejmowany przy chwilowym odrobieniu"*
> (Reguła Test-Granic w `CLAUDE.md`). Stan, który deklaruje „do końca miesiąca", musi
> faktycznie trwać — stąd testy trwałości stanu.

### 11b. Sizing frakcyjny po drawdownie — `SkalowanieFrakcjaDD` (W-063, Maier-Paape)

**Ciągła** regulacja rozmiaru: `frakcja = max(min_frakcja, 1 − DD/prog_max)`, domyślnie
`prog_max = 0.20`. Uzupełnia skokowy W-062 — usuwa „kliknięcia" między stanami.
Zmierzone (kapitał szczytowy 10 000):

| Drawdown | 0% | 5% | 10% | 20% |
|---|---|---|---|---|
| `frakcja()` | 1.000 | 0.750 | 0.500 | 0.100 |

Widoczne w planie jako `PlanPozycji.frakcja_dd`.

### 11c. Volatility drag — `volatility_drag()` + `DRAG_ROCZNY_OSTRZEZENIE = 0.5`

Annualizowana erozja pozycji lewarowanej: **½·λ·(λ−1)·σ²**. Lewar mnoży zmienność, więc
pozycja traci wartość, **nawet gdy cena bazowa wraca do punktu wyjścia** (ta sama erozja co
w leveraged ETF — Sinclair, BIB-018). Zmierzone przy σ = 0.60 (60% rocznie):

| Dźwignia | 1× | 5× | 10× | 20× |
|---|---|---|---|---|
| drag roczny | **0.0** | 3.60 | 16.2 | **68.4** |

Czytaj to jako ostrzeżenie, nie ciekawostkę: **przy 20× sam drag zjada wielokrotność
kapitału w skali roku.** `max_drag_roczny` w `policz()` pozwala odrzucić taki plan; wynik
ląduje w `PlanPozycji.drag_roczny`. Brak `vol_realized` → `None` (brak danych = brak
halucynacji, Prawo XV).

### 11d. Kelly ze skośnością — `skew_kelly(mu, sigma, skos)` (Sinclair, BIB-018)

Klasyczne Kelly (`f = μ/σ²`) zakłada rozkład symetryczny. Krypto ma **gruby lewy ogon**, więc
przy ujemnej skośności klasyczne Kelly **zawyża** rozmiar. Ten wzór rozwija Kelly do trzeciego
momentu i automatycznie tnie pozycję przy ujemnym skosie; przy `skos = 0` wraca dokładnie do `μ/σ²`.

### 11e. Stop-loss oparty na ATR — `atr` + `sl_atr_mult`

Gdy oba podane (`> 0`), stop liczony jako `cena ∓ sl_atr_mult × ATR` i łączony z buforem
likwidacji **przez wybór ostrożniejszego** (`max` dla LONG / `min` dla SHORT) — nigdy nie
rozluźnia stopa wynikającego z likwidacji, może go tylko zacieśnić.

### 11f. `mnoznik_rozmiaru`

Zewnętrzny mnożnik rozmiaru (domyślnie `1.0`) — wejście dla nadrzędnych regulatorów
(np. Gubernator W-325, conviction sizing W-318), które skalują pozycję poza kalkulatorem.
