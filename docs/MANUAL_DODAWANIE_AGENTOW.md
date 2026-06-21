# 🧩 MANUAL — Dodawanie Narzędzi i Agentów do Imperium

> **Stan na:** 2026-06-20 · **Gałąź:** `claude/sleepy-fermi-dsdE4`
> Dla Cezara-nowicjusza (ZPO). Jak rozszerzać Imperium o nowe „mózgi".

---

## ⚠️ NAJPIERW: dwa różne światy „agentów"

Słowo „agent" znaczy w naszym projekcie **dwie zupełnie różne rzeczy**. Nie pomyl ich.

| | **A) Doradcy Imperium** | **B) Subagenci Claude Code** |
|---|---|---|
| **Czym są** | Moduły Python w systemie tradingowym | Asystenci AI pomagający pisać kod |
| **Gdzie** | `imperium/cesarz/doradcy/*.py` | `.claude/agents/*.md` |
| **Co robią** | Oceniają sygnał handlowy (dane → werdykt) | Wykonują zadania programistyczne |
| **Kiedy** | W pętli handlowej, przy decyzji | Podczas Twojej pracy z Claude Code |
| **Przykład** | HERMES audytuje dane przed wejściem | hermes-audytor-danych sprawdza CSV |
| **Jak dodać** | Klasa Python + testy + wpięcie do Rady | Plik `.md` z opisem roli |

**HERMES z dokumentacji to typ A** — moduł Python, już istnieje (`imperium/cesarz/doradcy/hermes.py`, 24 testy).

Oba opisuję poniżej.

---

## CZĘŚĆ A — DODAWANIE DORADCY IMPERIUM (moduł Python)

Imperium ma **5 Doradców Cezara** (Rada Pięciu):

| Doradca | Plik | Rola |
|---------|------|------|
| **ORACLE** | `oracle.py` | Audytor Sharpe — jakość ryzyko/zwrot |
| **FULMEN** | `fulmen.py` | Walidator reżimu — ortogonalny wobec Legatusa |
| **IUSTITIA** | `iustitia.py` | Audytor ryzyka — BLOKUJE = veto |
| **HERMES** | `hermes.py` | Audytor informacji — kompletność, świeżość, hash |
| **PYTHIA** | `pythia.py` | Doradca probabilistyczny — p(zysk) |

Spina je `rada.py` — `RadaDoradcow.ocen()`. Reguła: 5/5=pełna pozycja, 4/5=×0.8,
3/5=×0.6, <3=blokada. IUSTITIA lub HERMES mogą zawetować bezwarunkowo.

### Krok A.1 — Wzorzec doradcy (kopiuj z istniejącego)

Każdy doradca ma tę samą strukturę. Spójrz na `hermes.py`:
1. **Enum werdyktu** (np. `WerdyktHermes`: CZYSTE / ZANIECZYSZCZONE / NIEKOMPLETNE)
2. **Dataclass danych wejściowych** (`DaneHermes` — co doradca dostaje)
3. **Progi** jako stałe (KOMPLETNOSC_MIN, VPIN_PROG...)
4. **Dataclass oceny** (`OcenaHermes` z `pozytywny` property)
5. **Klasa doradcy** z metodą `ocen(dane) → ocena`

### Krok A.2 — Stwórz nowy plik

Przykład: dodajemy doradcę **VULCAN** (audytor płynności — czy rynek ma wystarczający
wolumen żeby wejść bez poślizgu).

```python
# imperium/cesarz/doradcy/vulcan.py
"""
🏛️ IMV-ORI | VULCAN — Liquidity Auditor
Sprawdza czy płynność wystarcza do wejścia bez nadmiernego poślizgu.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class WerdyktVulcan(str, Enum):
    PLYNNY = "PLYNNY"          # Wolumen OK, spread wąski
    CIENKI = "CIENKI"          # Ostrzeżenie — niska płynność
    SUCHY = "SUCHY"            # Blokada — za mało płynności


@dataclass
class DaneVulcan:
    wolumen_24h_usd: float     # Obrót 24h w USD
    spread_pct: float          # Spread bid-ask w %
    amihud: float              # Amihud illiquidity (Z-06)


WOLUMEN_MIN_USD = 1_000_000
SPREAD_MAX_PCT = 0.5
AMIHUD_MAX = 2.0


@dataclass
class OcenaVulcan:
    werdykt: WerdyktVulcan
    powod: str = ""
    ostrzezenia: List[str] = field(default_factory=list)

    @property
    def pozytywny(self) -> bool:
        return self.werdykt in (WerdyktVulcan.PLYNNY, WerdyktVulcan.CIENKI)


class Vulcan:
    """Doradca VI — VULCAN (Liquidity Auditor)."""

    def ocen(self, dane: DaneVulcan) -> OcenaVulcan:
        blokady: List[str] = []
        ostrzezenia: List[str] = []

        if dane.wolumen_24h_usd < WOLUMEN_MIN_USD:
            blokady.append(
                f"Wolumen {dane.wolumen_24h_usd:,.0f} < {WOLUMEN_MIN_USD:,.0f} USD"
            )
        if dane.spread_pct > SPREAD_MAX_PCT:
            ostrzezenia.append(f"Spread {dane.spread_pct:.2f}% szeroki")
        if dane.amihud > AMIHUD_MAX:
            ostrzezenia.append(f"Amihud {dane.amihud:.2f} — cena wrażliwa na obrót")

        if blokady:
            return OcenaVulcan(WerdyktVulcan.SUCHY, " | ".join(blokady), blokady)
        if ostrzezenia:
            return OcenaVulcan(WerdyktVulcan.CIENKI, " | ".join(ostrzezenia), ostrzezenia)
        return OcenaVulcan(WerdyktVulcan.PLYNNY, "Płynność OK")
```

### Krok A.3 — Wepnij do `__init__.py`

W `imperium/cesarz/doradcy/__init__.py` dopisz:
```python
from .vulcan import Vulcan, WerdyktVulcan
```
I dodaj do `__all__`.

### Krok A.4 — Wepnij do Rady (jeśli ma głosować)

W `rada.py` dopisz `vulcan` do `OpinaRady`, do listy `poz = sum([...])` i do raportu.
**Uwaga (Prawo VIII):** dodawaj doradcę tylko jeśli patrzy na INNY kąt rynku niż reszta.

### Krok A.5 — Napisz testy (Prawo XIX + REGUŁA TEST-GRANIC)

```python
# tests/test_doradcy.py — dopisz
def test_vulcan_suchy_blokuje():
    from imperium.cesarz.doradcy.vulcan import Vulcan, DaneVulcan, WerdyktVulcan
    o = Vulcan().ocen(DaneVulcan(wolumen_24h_usd=500_000, spread_pct=0.1, amihud=0.5))
    assert o.werdykt == WerdyktVulcan.SUCHY
    assert not o.pozytywny

def test_vulcan_granica_wolumenu():
    # DOKŁADNIE próg — nie może blokować przy ==MIN
    from imperium.cesarz.doradcy.vulcan import Vulcan, DaneVulcan, WerdyktVulcan
    o = Vulcan().ocen(DaneVulcan(wolumen_24h_usd=1_000_000, spread_pct=0.1, amihud=0.5))
    assert o.werdykt == WerdyktVulcan.PLYNNY
```
**Obowiązkowo testuj granice:** wartość == próg, 0, wartość ujemna.

### Krok A.6 — Zaktualizuj dokumentację (ZASADA PEŁNEJ SYMBIOZY)

- `docs/DORADCY_CARA.md` — opis nowego doradcy (pełna nazwa, rola, progi)
- `docs/MANIFEST_KODU.md` — jeśli dotyczy kluczy
- `docs/LOG_ZMIAN.md` — wpis o zmianie
- `docs/INDEKS_IMPERIUM.md` — jeśli nowy plik

### Krok A.7 — Bramka przed commitem

```
python tests/run_tests.py            # X/X zielone
python narzedzia/audyt_spojnosci.py  # exit 0
```

---

## CZĘŚĆ B — DODAWANIE SUBAGENTA CLAUDE CODE (plik .md)

Subagenci to wyspecjalizowani asystenci AI którzy pomagają CI (i Claude) pracować nad
kodem. Żyją w `.claude/agents/`. Każdy to jeden plik `.md`.

### Już masz 2 gotowe przykłady:

| Plik | Rola |
|------|------|
| `.claude/agents/straznik-prawa-xxi.md` | Sprawdza spójność kodu↔docs przed commitem |
| `.claude/agents/hermes-audytor-danych.md` | Audytuje jakość danych (CSV/feed) — wzorowany na doradcy HERMES |

### Krok B.1 — Struktura pliku subagenta

Plik ma **nagłówek YAML** (między `---`) + **instrukcje** pod spodem:

```markdown
---
name: nazwa-agenta
description: Kiedy używać tego agenta. Claude czyta to żeby zdecydować czy go wywołać. Bądź konkretny — "Użyj gdy...".
tools: Bash, Read, Grep, Glob
model: sonnet
---

Tu piszesz instrukcje dla agenta — kim jest, co robi, jak raportuje.
To jest jego "system prompt".
```

Pola nagłówka:
- **name** — unikalna nazwa (małe litery, myślniki)
- **description** — KIEDY go używać (to najważniejsze — po tym Claude wybiera agenta)
- **tools** — które narzędzia może używać (Bash, Read, Edit, Grep, Glob, Write...). Pomiń = wszystkie.
- **model** — `sonnet` (szybki, tani), `opus` (mocny), `haiku` (najszybszy). Pomiń = dziedziczy.

### Krok B.2 — Stwórz nowego subagenta

Przykład: agent który dodaje nowe neurony zgodnie z zasadami Imperium.

```markdown
---
name: budowniczy-neuronow
description: Dodaje nowy mikro-neuron do Imperium zgodnie z Prawem XXI. Użyj gdy chcesz dodać neuron — zadba o KLUCZ/WSKAZNIK/KATEGORIA/WAGA, wpięcie do rejestru, MANIFEST, MAPA_KLUCZY, testy granic.
tools: Read, Edit, Write, Bash, Grep, Glob
model: opus
---

Jesteś Budowniczym Neuronów Imperium. Dodajesz nowy mikro-neuron przestrzegając Prawa VII (jeden na raz) i Prawa XXI (spójność).

Przy każdym nowym neuronie zadbaj o:
1. Klasa neuronu w odpowiednim pliku imperium/legiony/neurony/
2. KLUCZ, WSKAZNIK, KATEGORIA, WAGA, DOSTEPNY, ELITARNY — wszystkie pola
3. Rejestracja w rejestr.py
4. Wskaźnik produkowany przez Budowniczego
5. Wpis w MANIFEST_KODU.md (KLUCZ = kod)
6. Wpis w MAPA_KLUCZY.md
7. Testy granic (0/None/±/próg)
8. WAGI_REZIMU jeśli nowa kategoria

Kończ uruchomieniem audytu spójności.
```

### Krok B.3 — Jak używać subagenta

Po prostu poproś Claude Code po polsku:
```
użyj agenta budowniczy-neuronow żeby dodać neuron OBV dywergencja
```
albo Claude sam go wywoła gdy zobaczy że pasuje do zadania (dzięki polu `description`).

### Krok B.4 — Sprawdź czy agent jest widoczny

W Claude Code wpisz:
```
/agents
```
Zobaczysz listę dostępnych subagentów (Twoich + wbudowanych).

---

## 🎯 KIEDY KTÓRY TYP?

| Chcę... | Typ | Gdzie |
|---------|-----|-------|
| Dodać „mózg" oceniający rynek w handlu | **A) Doradca** | `imperium/cesarz/doradcy/*.py` |
| Dodać neuron/wskaźnik | A) Moduł | `imperium/legiony/neurony/*.py` |
| Pomocnika do pisania kodu | **B) Subagent** | `.claude/agents/*.md` |
| Automatycznego recenzenta przed commitem | B) Subagent | `.claude/agents/*.md` |
| Asystenta do analizy danych/CSV | B) Subagent | `.claude/agents/*.md` |

**Reguła:** jeśli to ma wpływać na DECYZJE HANDLOWE → typ A (Python + testy).
Jeśli to ma pomagać CI w PRACY nad projektem → typ B (subagent `.md`).

---

## ⚖️ ZASADY (obowiązują dla obu typów)

- **Prawo VII** — jeden moduł na raz, nie hurtem
- **Prawo VIII** — nowy doradca/neuron musi patrzeć na INNY kąt (mierz korelację)
- **Prawo XIX** — nic nie istnieje bez kodu + testów na branchu
- **Prawo XXI** — po każdej zmianie: audyt spójności + testy zielone
- **ZASADA SYMBIOZY** — zaktualizuj WSZYSTKIE dokumenty w tym samym ruchu

---

*Manual dodawania agentów — aktualizowany z każdą sesją.*
*Powiązane: `docs/DORADCY_CARA.md`, `docs/MANUAL_CLAUDE_CODE.md`, `CLAUDE.md`*
