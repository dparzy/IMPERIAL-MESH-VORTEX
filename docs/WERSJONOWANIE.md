# 🏺 WERSJONOWANIE I PIECZĘĆ IMPERIUM

> *"Omnia mutantur, nihil interit."* — Wszystko się zmienia, nic nie ginie.
>
> Każda zmiana zostawia ślad. Każdy moduł ma paszport.
> System wie KIEDY, CO, DLACZEGO i z CZEGO powstało.

---

## 🔖 SYSTEM NUMERACJI WERSJI

```
IMPERIUM vX.Y.Z — CODENAME

X = Major (zmiana architektury, nowy legion, nowy moduł główny)
Y = Minor (nowe neurony, strategie, dokumenty, rozbudowa)
Z = Patch (poprawki, testy, aktualizacje danych)

Przykłady:
  v0.1.0  — Inicjalizacja, pierwsze moduły
  v0.2.0  — Legatus + Kalkulator Lewara
  v0.3.0  — Igrzyska + Pamięć Absolutna + Doradcy
  v0.4.0  — (następna) Paper Trading Engine live
  v1.0.0  — Faza 0 pełna: paper trading działa produkcyjnie
  v2.0.0  — Faza 1: live trading MEXC
```

---

## 🏺 PIECZĘĆ IMPERIUM — Oznaczenia Modułów

Każdy moduł/neuron/strategia nosi **jedno z pięciu oznaczeń**:

| Symbol | Nazwa | Znaczenie |
|--------|-------|-----------|
| `🏛️ IMV-ORI` | *Originale Imperii* | **Nasz oryginał** — stworzony od zera w Imperium, nie ma odpowiednika |
| `🔱 IMV-ADO` | *Adoptatum* | Zaadoptowane i **znacząco ulepszone** — oryginał istnieje, ale nasz jest lepszy |
| `⚔️ IMV-INS` | *Inspiratum* | Zainspirowane przez zewnętrzne źródło — logika podobna, implementacja nasza |
| `📜 IMV-POR` | *Portatum* | Przeniesione z Kingdom Pixel (migracja, audyt w AUDYT_ADOPCJI.md) |
| `🔬 IMV-EXP` | *Experimentale* | W fazie eksperymentalnej — testowane w Koloseum, niezatwierdzone |

### Jak oznaczyć w kodzie:
```python
class NeuronWaddahAttar(MikroNeuron):
    """
    🔱 IMV-ADO v1.0 | Waddah Attar Explosion — nasza implementacja
    Oryginał: Waddah Attar (TradingView, zamknięty kod)
    Nasze ulepszenie: dodano filtr reżimu + integracja z Igrzyskami
    Wersja: v1.0 | Data: 2026-06-01
    """
    KLUCZ = "WA-01"
    LEGION = "XII"
```

---

## 📋 CHANGELOG IMPERIUM

### Format wpisu:
```
## [vX.Y.Z] — YYYY-MM-DD — CODENAME
### Dodano
- [MODUŁ] opis (pieczęć: IMV-ORI/ADO/INS)
### Zmieniono
- [MODUŁ] stara → nowa funkcja
### Naprawiono
- [MODUŁ] opis buga i fix
### Zastąpiono
- [STARY] → [NOWY] powód zmiany
### Wycofano
- [MODUŁ] powód + przeniesiono do: archiwum/
```

---

## 📜 HISTORIA WERSJI

### [v0.4.0] — 2026-06-01 — *"Certamen Vivum"*
*(Żywa Rywalizacja)*

#### Dodano
- `🏛️ IMV-ORI` `igrzyska.py` — silnik rywalizacji neuronów (W-002): scoring wg wzoru WYNIK_NEURONU, rangi Tiro→Aquilifer, Złoty Hełm, Lista Infamii, mnożniki wag dla Legatusa, integracja z Pamięcią Absolutną
- `🏛️ IMV-ORI` `BezpiecznikKapitalu` w `kalkulator_lewara.py` (W-028) — circuit-breaker AOA: 30% obsunięcia od szczytu → blokada wszystkich pozycji do ręcznego resetu
- `tests/` — pierwszy zestaw testów (28 testów, 0 zależności zewnętrznych): test_kalkulator (12), test_igrzyska (11), test_pamiec (5) + `run_tests.py`
- Skan VI psychologia (PSY-01..06) + odtworzone wskaźniki (WA-01, MC-01, NN-01)
- Skan VII Azja (+13 neuronów, +5 strategii) → `SKAN_AZJA.md`
- `AUDYT_SYSTEMU.md`, `WERSJONOWANIE.md`, `WIZJONER.md`

#### Naprawiono
- `KATALOG_NEURONOW.md` — usunięto zduplikowane przestarzałe tabele podsumowania (315→306 leftover)

#### Zmieniono
- Neurony 287 → **328**, strategie ~85 → **~108**, wizje → **28** (2 zaimplementowane)
- **Luka #1 z audytu zamknięta:** projekt ma teraz testy (było ZERO)

---

### [v0.3.0] — 2026-06-01 — *"Memoria et Certamen"*
*(Pamięć i Rywalizacja)*

#### Dodano
- `🏛️ IMV-ORI` `IGRZYSKA_IMPERIUM.md` — System rywalizacji: 6 rang neuronów, Złoty Hełm, Złota Zbroja, Purpura Senatu, Kij (Lista Infamii, Ceremonia Hańby, Damnatio Memoriae)
- `🏛️ IMV-ORI` `PAMIEC_ABSOLUTNA.md` + `pamiec_absolutna.py` — ImperiumLog 40+ pól, JSONL, MAE/MFE, walk-forward, replay
- `🏛️ IMV-ORI` `DORADCY_CARA.md` — Oracle/Fulmen/Iustitia/Hermes/Pythia
- `🔬 IMV-EXP` `ENT-08` Higuchi Fractal Dimension — detekcja reżimu D≈1/D≈2 (HFT QUARTET źródło)
- `⚔️ IMV-INS` `SES-02` AzjaRange, `SES-03` CMEGap — neurony sesji i luk CME
- Strategie: XII-RV-005 CME Gap, X-BK-003 Azja Range, IMV-AR-006 Funding Arb, X-SC-005 Asia Scalp
- `AUDYT_SYSTEMU.md` — głęboki audyt stanu systemu
- `WERSJONOWANIE.md` — ten dokument

#### Zmieniono
- `KATALOG_NEURONOW.md` 287 → 306 neuronów (+19 Skan IV+V)
- `KATALOG_STRATEGII.md` ~85 → ~103+ strategii
- `INDEKS_IMPERIUM.md` zaktualizowany do v0.3.0, 22 dokumenty

---

### [v0.2.0] — 2026-06-01 — *"Legatus et Calculus"*
*(Generał i Kalkulator)*

#### Dodano
- `🏛️ IMV-ORI` `legatus.py` — Generał Legatus, SKANER/FOKUS, agregacja ważona reżimem
- `🏛️ IMV-ORI` `kalkulator_lewara.py` — likwidacja, stop-loss, Kelly, auto-dźwignia
- `🏛️ IMV-ORI` `GENERAL_LEGATUS.md`, `KALKULATOR_LEWARA.md`
- `🔬 IMV-EXP` Katalog Strategii (~85 strategii), Katalog Neuronów (287)
- Skan I-IV neuronów: Market Profile, CVD-Div, MVRV-Z, VSA, GEX, Skew, TVL, DXY, HowardMarks

---

### [v0.1.0] — 2026-05-28 — *"Fundamentum"*
*(Fundament)*

#### Dodano
- `📜 IMV-POR` `kwatermistrz_danych.py` — ładowarka danych (z Kingdom Pixel)
- `📜 IMV-POR` `brama_kalkulatora.py` — Calculator Gate TA-Lib (z Kingdom Pixel)
- `📜 IMV-POR` `kronikarz.py`, `mnemosyne.py` — logi, pamięć
- `📜 IMV-POR` `wszechoko.py` (OmniSight), `meta_kora.py`, `valhalla.py`
- `🏛️ IMV-ORI` `mikro_neuron.py` — wzorzec MikroNeuron + NeuronStochRSI, NeuronFundingRate
- Dokumenty bazowe: ARCHITEKTURA, LEGIONY, ARSENAL, PLAN_DEEPSEEK, WZORZEC_DNSS

---

## 🔢 STATYSTYKI PIECZĘCI

| Pieczęć | Moduły | Neurony | Strategie |
|---------|--------|---------|-----------|
| 🏛️ IMV-ORI (Oryginały) | 5 | ~15 | ~20 |
| 🔱 IMV-ADO (Ulepszone) | 0 | 0 | 0 |
| ⚔️ IMV-INS (Inspirowane) | 0 | ~250 | ~80 |
| 📜 IMV-POR (Przeniesione) | 8 | 0 | 0 |
| 🔬 IMV-EXP (Eksperyment) | 0 | ~41 | ~3 |

> **Cel Fazy 1:** 20+ IMV-ORI neuronów (nasze własne, unikalne obliczenia).
> **Cel Fazy 2:** 5+ IMV-ADO (wzięliśmy coś z zewnątrz i ULEPSZYLIŚMY).

---

## 🔄 SYSTEM AKTUALIZACJI MODUŁÓW

### Trigger aktualizacji:
```
WYNIK_IGRZYSKA < 0.40 przez 14 dni → PRZEGLĄD MODUŁU
  → Doradca ORACLE: "Czy historycznie ten moduł był dobry?"
  → Jeśli tak: REKALIBRACJA (nowe parametry)
  → Jeśli nie: RELEGACJA → archiwum/deprecated/[KLUCZ]_v[X].py

NOWY POMYSŁ w WIZJONER → ANALIZA WPŁYWU
  → Czy zastępuje istniejący? → UPGRADE (numer wersji modułu +1)
  → Czy dodaje? → NOWY MODUŁ (nowy klucz)
  → Czy koliduje? → DEBATA w WIZJONER przed wdrożeniem
```

### Format nazwy archiwum:
```
archiwum/deprecated/X-07_WilliamsR_v1.0_relegated_2026-07-15.py
archiwum/deprecated/X-07_WilliamsR_v1.0_relegated_2026-07-15.md  ← post-mortem
```

### Post-mortem relegowanego modułu:
```markdown
# Post-mortem: X-07 Williams %R — Relegowany 2026-07-15

## Powód relegacji
WYNIK_IGRZYSKA = 0.31 przez 21 dni. Główny problem: flip-flop w reżimie RANGING.

## Statystyki życia modułu
- Aktywny od: 2026-05-28 (v0.1.0)
- Łącznie sygnałów: 847
- WinRate: 42%
- Contribution_Score avg: 0.21 (słaby wkład w agregację)

## Co zastąpiło
Neuron WA-01 Waddah Attar (🔱 IMV-ADO) — lepszy w reżimie RANGING

## Lekcja
Williams %R samodzielnie = za dużo szumu. Jako filtr dla innych = może wrócić.
```

---

*"Historia magistra vitae — sed Imperium semper progreditur."*
*Historia jest nauczycielką — ale Imperium zawsze idzie naprzód.*

*— WERSJONOWANIE.md | v1.0 | 2026-06-01*
