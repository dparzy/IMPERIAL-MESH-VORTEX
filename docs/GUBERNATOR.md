---
kategoria: FORMA
typ: zywy
wlasciciel: imperium/koloseum/gubernator.py, tests/test_gubernator.py
stan_na: 2026-06-16
powod_istnienia: "Jedyny dokument opisujący homeostatyczny sterownik globalnej ekspozycji CAŁEGO portfela (5 par naraz) — odróżnia się od innych warstw regulacji (HedgeMWU=per-neuron, Synapsy Reżimo"
---
# 🧭 GUBERNATOR — Homeostatyczny Sterownik Portfela (W-325)

> **Status kod-vs-plan:** ✅ KOD + TESTY na branchu `claude/sleepy-fermi-dsdE4`
> (`imperium/koloseum/gubernator.py`, `tests/test_gubernator.py` — 16 testów).
> **Stan na:** 2026-06-16.

## Pełna nazwa i pochodzenie (ZPO)

**GUBERNATOR** — łac. *gubernator* = sternik / zarządca prowincji; jednocześnie
termin z teorii sterowania: **regulator** (ang. *governor*), jak odśrodkowy
regulator Watta utrzymujący stałe obroty maszyny parowej. Tutaj: jedna dłoń na
sterze **całej floty 5 par naraz** — utrzymuje zdrową globalną ekspozycję portfela.

## Problem, który rozwiązuje (dla nowicjusza)

Imperium miało wiele **lokalnych** rządów, ale żadnego **globalnego**:

| Warstwa | Co reguluje | Zasięg |
|---------|-------------|--------|
| HedgeMWU | wagę każdego neuronu | per-neuron |
| Synapsy Reżimowe | pary neuronów × reżim | per-para neuronów |
| Namiestnik | włącz/wyłącz parę walut | per-para walut |
| Bezpiecznik DD | cięcie sizingu przy obsunięciu | reaktywny, portfel |
| **GUBERNATOR** | **globalną ekspozycję całej floty** | **proaktywny, portfel** |

Bezpiecznik DD tylko **tnie** w dół przy stracie (reaktywny). Gubernator działa
**proaktywnie i dwustronnie**: gdy okazje są wyraźne a kapitał zdrowy — pozwala
flocie **przyspieszyć** (mnożnik > 1, ekspansja); gdy rynek to „papka" albo trwa
obsunięcie — **ściąga ster** (mnożnik < 1, obrona / kwarantanna).

## Unikalna właściwość (czego nie ma konkurencja)

Sygnałem pewności jest **ROZRZUT OCEN SKANERA** — meta-cecha z *własnej niezgody
zespołu*. To **meta-labeling** Marcosa Lópeza de Prado (*Advances in Financial
Machine Learning*, 2018), ale zastosowany na poziomie **PORTFELA**, nie pojedynczego
modelu:

- **duży rozrzut** ocen → jest **wyraźny lider** koszyka → wysoka pewność → ekspansja
- **mały rozrzut** → wszystkie pary podobnie mdłe → niska pewność → obrona

Żaden znany system retail/open-source nie używa **wewnętrznej dyspersji rankingu
okazji** jako homeostatycznego regulatora globalnego ryzyka z histerezą stanów.

## Jak działa — homeostaza z histerezą

1. **Wejścia** (wszystkie liczalne w pętli, bez look-ahead):
   - `konwikcja_koszyka` ∈ [0,1] — bezwzględna siła lidera (score skanera / 3.0, squash)
   - `rozrzut_okazji` ∈ [0,1] — dyspersja ocen `(max − mediana)/(max − min)`
   - `dd_frakcja` — stan bezpiecznika DD (1.0 = zdrowo, < 1 = obsunięcie)
   - `breadth` ∈ [0,1] — ułamek par z żywą okazją
2. **Zdrowie koszyka** = 0.55·konwikcja + 0.30·rozrzut + 0.15·breadth
3. **Maszyna postaw z histerezą** (margines progu gasi *trzepotanie*):

   `KWARANTANNA → OBRONA → OSTROŻNY → NORMALNY → EKSPANSJA`

4. **Mnożnik** ∈ [floor, ceiling] (domyślnie 0.5×–1.3×), **wygładzany wykładniczo**
   (ster rusza płynnie, nie skacze).

## Nadrzędność ochrony kapitału

- `dd_frakcja ≤ prog_kwarantanna_dd` → **KWARANTANNA** (mnożnik = floor) — bez wyjątków.
- `dd_frakcja < prog_obrona_dd` → co najwyżej **OBRONA**; ekspansja zablokowana mimo
  wysokiej pewności. *Bezpieczeństwo > chciwość.*

## Neutralność (Prawo XV)

Dla wejścia neutralnego (konwikcja ≈ 0.5, rozrzut ≈ 0, kapitał zdrowy) zwraca
mnożnik **≈ 1.0** → portfel działa jak bez Gubernatora. Audyt spójności weryfikuje
to przy każdej sesji (Warstwa 1). Domyślnie **OPT-IN** w backteście (`gubernator=False`).

## Integracja

```python
backtest_portfel(..., tryb_skaner=True, gubernator=True)
# w pętli sizingu, po skanerze i bezpieczniku DD:
#   kapital_sizing *= stan_g.mnoznik
```

Gubernator działa **tylko w trybie skanera** (potrzebuje rankingu koszyka).

## Pomiar (Prawo I)

A/B: `narzedzia/ab_w325.py` — pełny stack TRYB NAJLEPSZY (TOP-3 + conviction +
compounding) na 4h, 5 par, ON vs OFF. Wynik: patrz `docs/LOG_ZMIAN.md` § W-325.
