# ⚖️ KALKULATOR LEWARA — Matematyka Przeżycia

> **Zasada Żelazna:** Zanim wejdziesz w pozycję lewarowaną — MUSISZ znać dokładną cenę likwidacji.
> Jeśli system nie policzy likwidacji → pozycja NIE wchodzi. Bezwzględnie.

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

**Korektory reżimu rynku:**
- VOLATILE: dźwignia ÷ 2 (zawsze)
- PANIC: dźwignia = 1× maksymalnie
- RANGING + sygnał odwrócenia: dźwignia ×0.7
- TREND_STRONG + kierunek zgodny: dźwignia ×1.2 (do max dla poziomu)

### Wzór na Dźwignię Dynamiczną

```python
def policz_dzwignie(pewnosc: float, rezim: str, pretorianie_ok: bool) -> int:
    if not pretorianie_ok:
        return 0  # Veto = brak pozycji

    # Baza z tabeli
    if pewnosc < 0.55:   return 0
    elif pewnosc < 0.65: dzwignia_baza = 2
    elif pewnosc < 0.75: dzwignia_baza = 5
    elif pewnosc < 0.85: dzwignia_baza = 10
    elif pewnosc < 0.92: dzwignia_baza = 15
    else:                dzwignia_baza = 20

    # Korekta reżimu
    korektor = {
        "VOLATILE": 0.5,
        "PANIC": 0.1,
        "RANGING": 0.7,
        "TREND_STRONG": 1.2,
        "NORMAL": 1.0,
        "ON-CHAIN_BULLISH": 1.1,
    }.get(rezim, 1.0)

    dzwignia = int(dzwignia_baza * korektor)
    return min(max(dzwignia, 1), 20)  # clamp 1–20
```

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

## ✅ CHECKLIST PRZED WEJŚCIEM (Pretorianie sprawdzają)

```
□ Cena likwidacji policzona?
□ Stop-Loss ustawiony (min 20% bufora od likwidacji)?
□ Rozmiar pozycji ≤ 2% kapitału?
□ R:R ≥ 1:2?
□ Funding Rate < 0.05% (LONG) lub > -0.03% (SHORT)?
□ ATR w normie (< 2× średniej)?
□ Seria strat < 3 z rzędu?
□ Drawdown < 10%?
□ Dźwignia zgodna z pewności agregatu?
□ WSZYSTKO ✅ → pozycja może wejść
□ COKOLWIEK ❌ → VETO — czekaj
```

---

## 📁 Plik kodu: `imperium/pretorianie/kalkulator_lewara.py`

```python
from dataclasses import dataclass

@dataclass
class PlanPozycji:
    symbol: str
    kierunek: str          # LONG / SHORT
    cena_wejscia: float
    dzwignia: int
    cena_likwidacji: float
    stop_loss: float
    take_profit: float
    rozmiar_usdt: float
    ryzyko_usdt: float     # max strata w USDT
    rr_ratio: float        # Risk:Reward
    checklist_ok: bool
    powod_veto: str        # "" jeśli OK

class KalkulatorLewara:
    OPLATE_UTRZYMANIA = 0.005  # 0.5% — typowe dla Binance/MEXC

    def policz(self, symbol: str, kierunek: str, cena_wejscia: float,
               dzwignia: int, kapital_usdt: float,
               pewnosc_agregatu: float, rezim: str) -> PlanPozycji:
        ...
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
