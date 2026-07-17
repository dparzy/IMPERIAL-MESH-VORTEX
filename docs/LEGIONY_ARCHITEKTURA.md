---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/legiony/mikro_neuron.py, imperium/legiony/neurony/dzwignia.py, imperium/legiony/neurony/momentum.py, imperium/legiony/neurony/onchain.py, imperium/legiony/neurony/struktura.py, imperium/legiony/neurony/trend.py, imperium/legiony/neurony/wolumen.py
stan_na: 2026-07-17
powod_istnienia: "Kanoniczne źródło nazewnictwa 4 Legionów (rzymskie nazwy: Legio X Equestris/Scalp, XII Fulminata/Swing, III Augusta/Invest, VI Ferrata/Leverage) + przypisanie konkretnych ID neuron"
---
# ⚔️ LEGIONY — Cztery Armie Imperium

> # 🚨 KOREKTA 2026-07-17 — ROSTERY NEURONÓW USUNIĘTE (były w 86% fałszywe)
>
> Ten dokument wymieniał **28 identyfikatorów neuronów** przypisanych do czterech legionów.
> Zweryfikowane mechanicznie wobec `rejestr.wszystkie_neurony()`:
>
> | | |
> |---|---|
> | zgodne z kodem | **4 z 28** |
> | zła nazwa | **9** — np. `X-01` opisany jako „Neuron EMA", a w kodzie to **RSI (14)**; `X-05` jako „OrderFlow", a to **EMA Cross (9/21)** |
> | **ID nieistniejące w kodzie** | **15** — w tym **CAŁY roster Legio III** (`III-01..III-07`) |
>
> **Schemat „prefiks klucza = legion" UMARŁ.** W kodzie: `X-*` 17 neuronów, `XII-*` 7,
> `VI-*` 1, **`III-*` ZERO**. Pozostałe ~60 neuronów ma prefiksy **funkcyjne**
> (`OC-*` on-chain, `PSY-*`, `RADAR-*`, `NEWS-*`, `SMC-*`, `Z-*` meta-bramy …),
> które w podziale na cztery legiony się nie mieszczą. Rój organizuje się dziś przez
> **KATEGORIA** (15 liter) — nie przez numer legionu.
>
> **Rostery usunięte, nie „poprawione"** — ich przepisanie zduplikowałoby
> [`MAPA_KLUCZY.md`](MAPA_KLUCZY.md), jedyne źródło prawdy klucz↔kod (audyt W14 wymusza
> pokrycie **każdego** klucza). Dwie listy tych samych kluczy rozjadą się ponownie —
> dokładnie tak, jak ta (Prawo XVI). Stara treść żyje w historii gita.
>
> **Co ZOSTAJE w tym dokumencie:** metafora czterech legionów (żywa w nazwie organu
> `imperium/legiony/`), schemat sygnału neuronu, współpraca z Senatem, weto Pretorianów.
> **Aktualny spis neuronów → [`MAPA_KLUCZY.md`](MAPA_KLUCZY.md)** ·
> **stan kodu → [`MANIFEST_KODU.md`](MANIFEST_KODU.md)** (Prawo XIX).


> **Zasada:** Każdy Legion = inny styl tradingu = inne interwały = inne wskaźniki.
> Żaden Legion nie duplikuje pracy drugiego. Razem pokrywają CAŁY rynek.
>
> **Mikro-neurony:** Każdy Legion to rój małych wyspecjalizowanych agentów.
> Jeden neuron = jeden wskaźnik. Wiele neuronów = jeden Legion = pełny obraz.

---

## 🏛️ CZTERY LEGIONY — nazwy i role

| Legion | Historyczny odpowiednik | Styl | Interwał | Priorytet |
|--------|------------------------|------|----------|-----------|
| **Legio X Equestris** (Dziesiąty Konny) | Najlepsza jazda Cezara | Scalp | M1–M15 | Szybkość |
| **Legio XII Fulminata** (Dwunasty Błyskawica) | Wschodni legion walki | Swing | 4H–1D | Równowaga |
| **Legio III Augusta** (Trzeci Augustowski) | Garnizon, stabilizacja | Invest/Spot | 1D–1W | Bezpieczeństwo |
| **Legio VI Ferrata** (Szósty Żelazny) | Żelazna pancerna | Leverage/Futures | Zmienne | Dźwignia |

---

## ⚡ LEGIO X EQUESTRIS — Konny (Scalp)

**Motto:** *"Szybki cios zanim wróg się obróci."*
**Interwał:** M1, M5, M15
**Kapitał:** mały, wiele trades/dzień

### Mikro-neurony

> Roster usunięty 2026-07-17 (był fałszywy — patrz baner na górze).
> **Aktualne neurony tego legionu → [`MAPA_KLUCZY.md`](MAPA_KLUCZY.md)** (jedyne źródło prawdy klucz↔kod, pilnowane przez audyt W14).


## ⚖️ LEGIO XII FULMINATA — Błyskawica (Swing)

**Motto:** *"Uderzamy rzadko, ale celnie."*
**Interwał:** 4H, 1D
**Kapitał:** średni, kilka trades/tydzień

### Mikro-neurony

> Roster usunięty 2026-07-17 (był fałszywy — patrz baner na górze).
> **Aktualne neurony tego legionu → [`MAPA_KLUCZY.md`](MAPA_KLUCZY.md)** (jedyne źródło prawdy klucz↔kod, pilnowane przez audyt W14).


## 🏰 LEGIO III AUGUSTA — Augustowski (Invest/Spot)

**Motto:** *"Garnizon trwa. Cierpliwość to broń."*
**Interwał:** 1D, 1W
**Kapitał:** duży, strategie tygodniowe/miesięczne

### Mikro-neurony

> Roster usunięty 2026-07-17 (był fałszywy — patrz baner na górze).
> **Aktualne neurony tego legionu → [`MAPA_KLUCZY.md`](MAPA_KLUCZY.md)** (jedyne źródło prawdy klucz↔kod, pilnowane przez audyt W14).


## 🔥 LEGIO VI FERRATA — Żelazny (Leverage/Futures)

**Motto:** *"Żelazna dyscyplina albo śmierć. Dźwignia to miecz obosieczny."*
**Interwał:** 15M–4H (adaptacyjny)
**Kapitał:** MAŁE pozycje, wysoka dźwignia (5×–20×)
**⚠️ RYZYKO NAJWYŻSZE — Pretorianie mają WETO**

### Mikro-neurony

> Roster usunięty 2026-07-17 (był fałszywy — patrz baner na górze).
> **Aktualne neurony tego legionu → [`MAPA_KLUCZY.md`](MAPA_KLUCZY.md)** (jedyne źródło prawdy klucz↔kod, pilnowane przez audyt W14).


## 🧬 SCHEMAT SYGNAŁU — co każdy neuron produkuje

Każdy mikro-neuron zwraca ustandaryzowany obiekt:

```python
@dataclass
class SygnalNeuronu:
    neuron_id: str          # np. "X-02" (Legio X, neuron 2)
    legion: str             # "SCALP" / "SWING" / "INVEST" / "LEVERAGE"
    wskaznik: str           # np. "StochRSI"
    wartosc: float          # surowa wartość wskaźnika
    kierunek: str           # "LONG" / "SHORT" / "NEUTRAL"
    pewnosc: float          # 0.0–1.0
    pewnosc_przeciwnika: float  # jak mocne są argumenty AGAINST
    pewnosc_finalna: float  # po uwzględnieniu adversary
    powody: list[str]       # konkretne powody (np. ["RSI=67.3 > 60", "EMA cross UP"])
    timestamp: float        # czas generacji
    hash_danych: str        # SHA-256 z Bramy (dowód nienaruszalności)
```

**Przykład (Neuron X-02, StochRSI):**
```json
{
  "neuron_id": "X-02",
  "legion": "SCALP",
  "wskaznik": "StochRSI",
  "wartosc": 23.4,
  "kierunek": "LONG",
  "pewnosc": 0.75,
  "pewnosc_przeciwnika": 0.2,
  "pewnosc_finalna": 0.68,
  "powody": [
    "StochRSI=23.4 poniżej 20 (strefa wyprzedania)",
    "Momentum odwraca się w górę",
    "CVD potwierdza kupujący przejmują kontrolę"
  ],
  "timestamp": 1748823600.0,
  "hash_danych": "sha256:a3f9..."
}
```

### Legenda kategorii neuronów (pole `KATEGORIA` w kodzie)

> **Scalona 2026-07-17 — JEDNO ŹRÓDŁO zamiast dwóch (Prawo XVI).** Ten dokument miał własną
> kopię legendy, identycznie fałszywą jak ta w GENERAL_LEGATUS: wymieniała litery **E** i **G**,
> których w kodzie **nie ma**, i pomijała **C, D, N, Z**. Dwie ręczne kopie tej samej tabeli
> rozjechały się w tę samą stronę — dowód, że problemem była kopia, nie autor.
>
> **Pełna legenda 15 kategorii (zweryfikowana wobec `rejestr.wszystkie_neurony()`):**
> → [`GENERAL_LEGATUS.md` § Legenda kategorii neuronów](GENERAL_LEGATUS.md#legenda-kategorii-neuronów)
>
> Tam legenda ma sens — Generał używa `KATEGORIA` jako klucza w `WAGI_REZIMU` (mnożniki wag
> per reżim rynku). Tu byłaby ozdobą do przepisywania przy każdej zmianie roju.

## 🔄 JAK LEGIONY WSPÓŁPRACUJĄ Z SENATEM

```
Legio X (Scalp)   ─┐
Legio XII (Swing) ─┤──→ SENAT zbiera sygnały wszystkich Legionów
Legio III (Invest)─┤     Frakcja BYKÓW filtruje tylko LONG-sygnały
Legio VI (Leverage)┘     Frakcja NIEDŹWIEDZI filtruje tylko SHORT-sygnały
                              ↓
                         RAPORT DEBATY
                              ↓
                          CESARZ decyduje
                         (LONG/SHORT/CZEKAJ + %)
```

**Ważne:** Senat dostaje sygnały ze WSZYSTKICH Legionów jednocześnie.
Cesarz nie musi wiedzieć z którego Legionu pochodzi sygnał — widzi tylko argumenty.

---

## ⚔️ PRETORIANIE — WETO dla Legio VI

Przed każdą decyzją Cesarza dotyczącą Legio VI (Leverage):

```
Aegis Tarcza sprawdza:
  1. ATR > 2× norma? → CZEKAJ (za duże wahania)
  2. Seria 3+ strat z rzędu? → PAUZA 24h
  3. Drawdown > 10%? → STOP TRADING
  4. Funding Rate > 0.05%? → VETO dla LONG
  5. Funding Rate < -0.03%? → VETO dla SHORT
```

Jeśli choć jeden warunek spełniony → **pozycja lewarowana NIE WCHODZI**, nawet gdy Cesarz mówi LONG.

---

*VITRUVIUSZ — "Cztery legiony patrzą w cztery strony. Razem nie ma ślepego pola."*
