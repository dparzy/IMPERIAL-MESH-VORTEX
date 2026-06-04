# ⚔️ GENERAŁ LEGATUS — Koordynator Między Legionami a Senatem

> **Rola:** Generał to brakujące ogniwo między 4 Legionami a Senatem.
> Legiony produkują sygnały neuronów. Senat debatuje i decyduje.
> **Generał zbiera, filtruje, agreguje i przekazuje** — bez niego Senat tonie w szumie.

---

## 🏛️ MIEJSCE W ARCHITEKTURZE

```
[Legio X — Scalp]      ─┐
[Legio XII — Swing]    ─┤
[Legio III — Invest]   ─┤──→ [ GENERAŁ LEGATUS ] ──→ [ SENAT ]──→ [ CESARZ ]
[Legio VI — Leverage]  ─┤         ↑ filtruje                          ↓
[12 Dywizji Specjalnych]┘    ↑ agreguje                           DECYZJA
                              ↑ ocenia reżim                   LONG/SHORT/CZEKAJ
                              ↑ wybiera tryb (SKANER/FOKUS)
```

**Generał NIE decyduje.** Generał PRZYGOTOWUJE dane dla Senatu.

---

## 🔭 DWA TRYBY OPERACYJNE

### TRYB SKANER — "Szukaj najlepszej okazji"

**Kiedy:** Brak aktywnej pozycji, szukamy punktu wejścia
**Co robi:**
- Aktywuje WSZYSTKIE skatalogowane neurony (299 w katalogu, 47 w kodzie)
- Skanuje całą watchlistę (BTC, ETH, SOL, BNB, top alts)
- Dla każdego aktywa liczy `wynik_skaner` = suma ważona sygnałów
- Wybiera 3 najlepszych kandydatów → przekazuje do Senatu

```python
# Pseudokod trybu SKANER
class TrybSkaner:
    def wykonaj(self, watchlista: list[str]) -> list[KandydatAktywa]:
        kandydaci = []
        for symbol in watchlista:
            wskazniki = brama.pobierz_wszystkie(symbol)
            sygnaly = roj_pelny.zbierz_sygnaly(wskazniki)
            wynik = self._score(sygnaly)
            kandydaci.append(KandydatAktywa(symbol, wynik, sygnaly))
        return sorted(kandydaci, key=lambda x: x.wynik, reverse=True)[:3]
```

### TRYB FOKUS — "Maksimum uwagi na jeden cel"

**Kiedy:** Symbol wybrany (przez Skanera lub przez Komendanta ręcznie)
**Co robi:**
- Wszystkie neurony kierują na **jeden symbol**
- Zwiększa wagę neuronów odpowiednich dla danego aktywa
  - BTC → on-chain neurony ×1.5 wagi
  - Alts → wolumenowe i sentiment ×1.5 wagi
  - Futures → lewarowe neurony aktywne
- Generuje pełny raport dla Senatu

```python
# Pseudokod trybu FOKUS
class TrybFokus:
    def wykonaj(self, symbol: str, typ: str = "spot") -> RaportLegatusa:
        wskazniki = brama.pobierz_wszystkie(symbol)
        sygnaly = roj_pelny.zbierz_sygnaly(wskazniki)
        sygnaly = self._dostosuj_wagi(sygnaly, symbol, typ)
        return self._agreguj(symbol, sygnaly)
```

---

## 📊 AGREGACJA SYGNAŁÓW — Algorytm Generała

### Krok 1 — Zbierz sygnały ze wszystkich aktywnych neuronów

```python
sygnaly_long  = [s for s in sygnaly if s.kierunek == "LONG"]
sygnaly_short = [s for s in sygnaly if s.kierunek == "SHORT"]
sygnaly_neutral = [s for s in sygnaly if s.kierunek == "NEUTRAL"]
```

### Krok 2 — Policz ważoną siłę każdego kierunku

```python
sila_long  = sum(s.pewnosc_finalna * s.waga for s in sygnaly_long)
sila_short = sum(s.pewnosc_finalna * s.waga for s in sygnaly_short)
razem      = sila_long + sila_short + 1e-9  # unikaj dzielenia przez 0
przewaga_long  = sila_long  / razem  # 0.0–1.0
przewaga_short = sila_short / razem  # 0.0–1.0
```

### Krok 3 — Klasyfikacja reżimu rynku

| Warunek | Reżim | Akcja |
|---------|-------|-------|
| ADX > 25, EMA układające się | TREND_STRONG | Neurony trendowe ×1.3 wagi |
| ATR > 2× norma | VOLATILE | Redukuj pewność wszystkich o 30% |
| ADX < 20, BB squeeze | RANGING | Neurony oscylacyjne ×1.3 wagi |
| Funding > 0.05% | OVERHEATED | Ostrzeżenie Pretorianów |
| VIX/BVOL > 80 | PANIC | CZEKAJ — nie handluj |

### Krok 4 — Filtr minimum

Senat dostaje sygnał TYLKO gdy:
- Minimum **5 neuronów** zgodnych w jednym kierunku
- Ważona przewaga > **55%** (nie handlujemy na szumie)
- Żaden Pretorianin nie nałożył WETO

### Krok 5 — Raport dla Senatu

```python
@dataclass
class RaportLegatusa:
    symbol: str
    tryb: str                    # SKANER / FOKUS
    rezim: str                   # TREND_STRONG / RANGING / VOLATILE / PANIC / NORMAL
    sila_long: float             # 0.0–1.0
    sila_short: float            # 0.0–1.0
    przewaga_kierunku: str       # LONG / SHORT / NEUTRAL
    pewnosc_agregatu: float      # finalna pewność po agregacji
    aktywnych_neuronow: int      # ile neuronów dało sygnał
    zgodnych_neuronow: int       # ile neuronów zgodnych z kierunkiem
    sygnaly: List[SygnalNeuronu] # surowe sygnały (Senat może przejrzeć)
    weto_pretorianow: bool       # czy Pretorianie nałożyli VETO
    powod_weta: str              # jeśli VETO — dlaczego
    timestamp: float
```

---

## 🔀 DYNAMICZNE WAGI REŻIMOWE

Generał dostosowuje wagi neuronów do bieżącego reżimu:

| Reżim | Kategoria↑ | Kategoria↓ | Logika |
|-------|-----------|-----------|--------|
| TREND_STRONG | T (Trend) ×1.5, M (Momentum) ×1.2, H (Hurst) ×1.3 | O (On-chain) ×0.7 | Trend is your friend |
| RANGING | M (Momentum) ×1.5, V (Zmienność) ×1.3, H (Hurst) ×1.2 | T (Trend) ×0.5 | Granice kanału |
| VOLATILE | Wszystkie ×0.7, A (Anty-manip) ×2.0 | L (Leverage) ×0.3 | Ostrożność |
| PANIC | A (Anty-manip) ×3.0 | Wszystkie inne ×0.1 | Tylko obrona |
| ON-CHAIN_BULLISH | O (On-chain) ×2.0 | L (Leverage) ×0.8 | Fundamenty mówią |
| NORMAL | H (Hurst) ×1.1 | — | Lekkie wzmocnienie pamięci długiego zasięgu |

### Legenda kategorii neuronów

| Litera | Kategoria | Opis |
|--------|-----------|------|
| M | Momentum | Wskaźniki pędu (RSI, MACD, StochRSI) |
| T | Trend | Wskaźniki trendu (EMA, ADX, Supertrend) |
| V | Zmienność | Wskaźniki zmienności (ATR, BB, Choppiness) |
| F | Flow/Wolumen | Przepływ kapitału (CVD, OBV, OI) |
| O | On-chain | Wskaźniki blockchain (MVRV, SOPR, Netflow) |
| L | Lewarowanie | Wskaźniki ryzyka lewarowego (Funding, ATR-Lev) |
| R | Rynki pochodne | Futures/opcje (Open Interest, Max Pain) |
| S | Smart Money | SMC — struktury rynku (BOS, CHoCH, OB) |
| A | Anty-manipulacja | Wykrywanie manipulacji i fałszywych wybić |
| K | Korelacja | Korelacje i dywergencje między aktywami |
| E | Eksploracja | Eksperymenty i nowe miary (EXP-*) |
| G | Giełdowe | Dane z giełd (wolumeny, płynność) |
| H | Hurst/Pamięć długiego zasięgu | Meta-brama reżimu: H>0.55 persystencja, H<0.45 antypersystencja, H≈0.5 NEUTRAL |

---

## 🏗️ PLAN IMPLEMENTACJI

### Faza 0 (teraz) — Minimalna wersja
- Zbiera sygnały z 2 testowych neuronów (X-02 StochRSI, VI-01 FundingRate)
- Tryb FOKUS na BTC
- Prosty algorytm agregacji (suma ważona)
- Bez DeepSeek — raport tekstowy

### Faza 1 — Pełna wersja
- Wszystkie 79+ neuronów aktywnych
- Tryb SKANER z watchlistą 20 aktywów
- Klasyfikacja reżimu rynku
- Raport JSON dla Senatu

### Faza 2 — Inteligentna wersja
- DeepSeek czyta RaportLegatusa i decyduje jako Senat
- Dinamyczna selekcja neuronów (nie wszystkie zawsze aktywne)
- Feedback loop: które neurony były trafne → ich wagi rosną

---

## 💡 ZASADY GENERAŁA

1. **Generał filtruje szum** — Senat nie widzi setek surowych sygnałów. Widzi zagregowany raport.
2. **Generał nie ma opinii** — agreguje matematycznie, nie "uważa".
3. **Generał zna reżim** — dostosowuje wagi do warunków rynkowych.
4. **Generał respektuje Weto** — jeśli Pretorianie mówią STOP, Generał nie przekazuje sygnału dalej.
5. **Tryb dyktuje Komendant** — SKANER lub FOKUS na rozkaz. System nie decyduje sam o trybie.

---

*"Generał nie wygrywa bitew. Generał sprawia, że Cesarz może wygrać."* — VITRUVIUSZ

---

## 📁 Plik kodu: `imperium/legiony/legatus.py`

> Szkielet kodu — patrz plik implementacji.
