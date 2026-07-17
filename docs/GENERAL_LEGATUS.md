---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/legiony/legatus.py
stan_na: 2026-07-17
powod_istnienia: "Jedyny dokument opisujący rolę koordynatora między 4 Legionami a Senatem — algorytm agregacji sygnałów (5 kroków), klasyfikację reżimu rynku, dynamiczne wagi reżimowe, i integrację"
---
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
- Aktywuje WSZYSTKIE skatalogowane neurony (299 w katalogu, <!-- LICZBA:neurony -->87<!-- /LICZBA --> w kodzie)
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
| SMC_ACTIVE | S (Smart Money) ×2.0, F (Flow) ×1.2, T (Trend) ×1.1 | — | Struktury instytucjonalne prowadzą |
| NORMAL | H (Hurst) ×1.1 | — | Lekkie wzmocnienie pamięci długiego zasięgu |

### Legenda kategorii neuronów

> **Zweryfikowane wobec kodu 2026-07-17** (`rejestr.wszystkie_neurony()` + docstringi neuronów).
> Poprzednia wersja tej tabeli wymieniała litery **E** i **G**, które **nie istnieją w kodzie**,
> i pomijała **C, D, N, Z** — czyli cztery całe rodziny neuronów z deep-researchu.
> **Bez liczników celowo** (Filar 4): ręcznie wpisana liczba zawsze się rozjedzie —
> aktualny spis: `python -c "from imperium.legiony.rejestr import wszystkie_neurony; ..."`
> albo `docs/MAPA_KLUCZY.md` (jedyne źródło prawdy klucz↔kod).

| Litera | Kategoria | Co mierzy | Przykłady |
|--------|-----------|-----------|-----------|
| **M** | Momentum | pęd ceny (RSI, MACD, StochRSI) | X-01, X-02, X-03 |
| **T** | Trend | kierunek i siła trendu (EMA, ADX, Supertrend) | X-05, X-10, X-18 |
| **V** | Zmienność | reżim zmienności (Realized Volatility Regime) | V-13, V-14 |
| **F** | Flow / Wolumen | przepływ kapitału (CVD, OBV, VSA) | V-01, V-02, V-03 |
| **O** | On-chain | dane blockchain (MVRV, SOPR, Netflow) | OC-01, OC-02, OC-03 |
| **L** | Lewarowanie | ryzyko spadkowe modulujące dźwignię (Ulcer Index) | L-14, VI-13 |
| **R** | Rynki pochodne / reżim | futures, opcje, detektory zmiany reżimu | AUG-01, BOCPD-01, CP-01 |
| **S** | Smart Money (SMC) | struktury rynku (Order Block, BOS, CHoCH) | SMC-01, SES-01 |
| **A** | Anty-manipulacja | polowanie na stop-lossy, fałszywe wybicia | A-01, A-02, A-03 |
| **K** | Korelacja / makro | powiązania międzyrynkowe (DXY Trend, stablecoiny) | K-01, K-03, K-04 |
| **C** | Cross-sectional | siła względna w koszyku (Relative Strength) | C-01 |
| **D** | Geometria ścieżki | Path Signature — Lévy Area (Close×Volume) | D-01 |
| **N** | Meta-bramy: entropia/pamięć | Permutation Entropy Chaos Gate, Fractional Differentiation | N-01, N-02 |
| **H** | Hurst / pamięć długiego zasięgu | Hurst-DFA Regime Gate (H>0.55 persystencja, H<0.45 antypersystencja) | H-01 |
| **Z** | Meta-bramy obronne | tłumią rój przez `pewnosc_przeciwnika` (VPIN ToxicFlow, pump, bubble, cascade) | Z-01, Z-02, RADAR-04 |

---

## 🏗️ STAN IMPLEMENTACJI (zweryfikowany wobec kodu 2026-07-17)

> Ta sekcja była **planem z 2026-06-04** i twierdziła, że „teraz" Generał zbiera sygnały
> z **2 testowych neuronów**. Zweryfikowane: Faza 0 i Faza 1 są **wykonane od dawna**.

| Faza | Zakres | Stan (dowód z kodu) |
|---|---|---|
| **Faza 0** — wersja minimalna | 2 testowe neurony, FOKUS na BTC, suma ważona | ✅ **dawno wykonana** |
| **Faza 1** — wersja pełna | wszystkie neurony, SKANER z watchlistą, klasyfikacja reżimu, raport dla Senatu | ✅ **wykonana** — <!-- LICZBA:neurony_aktywne -->81<!-- /LICZBA --> aktywnych neuronów, tryby SKANER/FOKUS i 7 reżimów w `legatus.py` |
| **Faza 2** — wersja inteligentna | LLM czyta raport, dynamiczna selekcja neuronów, feedback loop wag | 🟡 **częściowo** — feedback loop ŻYJE (HedgeMWU, § niżej); Senat LLM opt-in (`petla_live --senat`); dynamiczna selekcja neuronów **niezbudowana** |

## 💡 ZASADY GENERAŁA

1. **Generał filtruje szum** — Senat nie widzi setek surowych sygnałów. Widzi zagregowany raport.
2. **Generał nie ma opinii** — agreguje matematycznie, nie "uważa".
3. **Generał zna reżim** — dostosowuje wagi do warunków rynkowych.
4. **Generał respektuje Weto** — jeśli Pretorianie mówią STOP, Generał nie przekazuje sygnału dalej.
5. **Tryb dyktuje Komendant** — SKANER lub FOKUS na rozkaz. System nie decyduje sam o trybie.

---

*"Generał nie wygrywa bitew. Generał sprawia, że Cesarz może wygrać."* — VITRUVIUSZ

---

## 🤖 Integracja HedgeMWU — Online Learning (W-049)

Legatus obsługuje per-neuronowe mnożniki uczenia online dostarczane przez `HedgeMWU`
(Multiplicative Weights Update, Freund & Schapire 1997).

### Parametr mnozniki_neuronow

```python
legatus = Legatus(mnozniki_neuronow={"X-01": 1.42, "X-07": 0.63, ...})
# lub po konstrukcji:
legatus.ustaw_mnozniki_neuronow(mwu.mnozniki())
```

- `mnozniki_neuronow: Optional[dict]` — słownik `{KLUCZ_neuronu → float}`.
- Neutralny stan (brak danych): wszystkie mnożniki = 1.0 (brak zniekształcenia).
- Trafni eksperci: > 1.0 | Mylący się: < 1.0.

### Jak _dostosuj_wagi() używa mnożników

```python
# Wewnątrz _dostosuj_wagi():
waga_finalna = waga_rezimu × mnoznik_mwu
# Efekt: neurony trafne w historii mają wyższy głos NIEZALEŻNIE od reżimu.
```

Formuła: `waga_rezimu` (z WAGI_REZIMU) × `mnoznik_mwu` (z HedgeMWU.mnozniki()).
Działają ADDYTYWNIE — reżim i historia uczenia wzmacniają się nawzajem.

### Przepływ danych MWU → Legatus

```
Igrzyska.zarejestruj_wynik()
  └─ obserwatorzy (DRY) → HedgeMWU.zarejestruj_wynik()
       └─ HedgeMWU.mnozniki()
            └─ legatus.ustaw_mnozniki_neuronow(mnozniki)
                 └─ _dostosuj_wagi() → waga_finalna = reżim × MWU
```

Szczegóły algorytmu MWU → `docs/IGRZYSKA_IMPERIUM.md` § HedgeMWU.

---

## 📁 Plik kodu: `imperium/legiony/legatus.py`

> **NIE jest to szkielet** (korekta 2026-07-17 — dokument twierdził tak od 2026-06-04):
> `legatus.py` to **833 linie** żywego kodu — agregacja, 7 reżimów (`WAGI_REZIMU`),
> tryby SKANER/FOKUS, mnożniki MWU, meta-bramy. Progi z tego dokumentu **zweryfikowane**:
> `Legatus(min_neuronow=5, min_przewaga=0.55)` — zgadza się co do wartości (`legatus.py:379`).
