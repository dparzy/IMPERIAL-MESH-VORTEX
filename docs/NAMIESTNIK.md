# 🏛️ NAMIESTNIK — Regime + Timeframe-Aware Gating Network

> **Stan na:** 2026-06-03 · **Status:** ✅ aktywny w kodzie (`imperium/koloseum/namiestnik.py`)
> **Testy:** pokryty w `tests/test_namiestnik.py` · **Faza:** 1 (deterministyczna)

---

## 📐 Pełna nazwa (ZPO)

- **Namiestnik** = Regime-Aware + Timeframe-Aware **Gating Network** (sieć bramkująca świadoma reżimu i interwału).
- **Gating Network** — wzorzec z **MoE (Mixture of Experts)**: lekka sieć decyduje, którego „eksperta" (tryb/strategię/dźwignię) użyć dla bieżącego stanu.
- Rola: **meta-kontroler** — nie handluje sam, tylko ustawia parametry dla reszty łańcucha.

## 🔗 Inspiracje (zweryfikowane — `REJESTR_INSPIRACJI.md`)

| Klucz | Praca | Link | Rola |
|-------|-------|------|------|
| ML-30 | Volatility-Adaptive MoE (Adaptive Market Intelligence) | https://arxiv.org/abs/2508.02686 | reżim przełącza eksperta |
| ML-31 | Adaptive Regime-Aware Prediction (Transformer+RL) | https://arxiv.org/abs/2603.19136 | wzorzec reżimu |
| ML-32 | Meta-Learning Optimal Mixture of Strategies | https://arxiv.org/abs/2505.03659 | MAML (Faza 3) |
| ML-28 | MRC / Shapley dynamic weighting | https://arxiv.org/abs/2605.24490 | wagi online (Faza 2) |

> **Deep-research (2026-06-03):** auto-selekcja **timeframe + strategia wg reżimu** to
> **otwarty problem** — Freqtrade, Jesse, NautilusTrader, OctoBot wymagają ręcznej
> konfiguracji per styl. Namiestnik robi to automatycznie = przewaga konkurencyjna.

---

## 🧠 Jak działa — dwie warstwy

```
bary (OHLCV + interwal)
   │
   ▼
klasyfikuj_rezim(wskazniki) ──► rezim  (TREND_STRONG / RANGING / VOLATILE / NORMAL)
   │                                       │
   │   interwal ──► styl_interwalu() ──► styl (SCALP / SWING / INVEST)
   │                                       │
   ▼                                       ▼
        ┌─────────── NAMIESTNIK.decyduj(rezim, interwal) ───────────┐
        │  Warstwa 1 (reżim):  tryb, lewar_factor, prog, czy_grac,  │
        │                       wagi_override                        │
        │  Warstwa 2 (styl):   lewar_cap, rynek (futures/spot),      │
        │                       mnoznik_progu                        │
        └────────────────────────┬──────────────────────────────────┘
                                 ▼
              DecyzjaNamiestnika  (połączone parametry)
                                 ▼
              Legatus + Klucznik → Kalkulator (dźwignia ≤ lewar_cap) → pozycja
```

### Warstwa 1 — Reżim (CO robić)

| Reżim | tryb | lewar_factor | próg | gra? | Uzasadnienie |
|-------|------|-------------|------|------|--------------|
| TREND_STRONG | filtr | ×1.2 | 55% | ✅ | silny trend — filtr strategii, pełna dźwignia |
| TREND_WEAK | agregat | ×0.7 | 60% | ✅ | słaby trend — ostrożnie |
| RANGING | agregat | ×0.4 | 72% | 🛑 | konsolidacja — stój z boku |
| VOLATILE | strategia | ×0.5 | 65% | ✅ | Klucznik wybiera strategię |
| PANIC | agregat | ×0.1 | 90% | 🛑 | obrona kapitału |
| NORMAL | agregat | ×0.8 | 60% | ✅ | ostrożny agregat |
| ON-CHAIN_BULLISH | filtr | ×1.1 | 58% | ✅ | sygnały on-chain (czeka na feed) |
| SMC_ACTIVE | strategia | ×0.9 | 62% | ✅ | struktura SMC (czeka na feed) |

### Warstwa 2 — Styl interwałowy (JAK na tym TF)

Deep-research praktyków → progi/lewary per styl:

| Styl | Interwały | lewar_cap | rynek | mnoznik_progu | Uzasadnienie |
|------|-----------|-----------|-------|---------------|--------------|
| **SCALP** | M1–M15 | ≤10× | FUTURES | ×0.95 | szybkie wejścia, wysoka dźwignia |
| **SWING** | 30M–4H | ≤5× | OBA | ×1.00 | zbalansowane |
| **INVEST** | 1D–1W | ≤2× | SPOT | ×1.10 | selektywne, niska/zero dźwigni |

**Reguła obronna:** w reżimie `VOLATILE`/`PANIC` rynek wymuszony na **SPOT** nawet dla scalpu (zero ryzyka likwidacji w chaosie).

---

## 📊 Tabela dowodowa (Prawo XVI — `narzedzia/pomiar_namiestnik.py`)

Po dodaniu Timeframe-Aware (1D→INVEST cap 2×):

| Zestaw | Wariant | PnL % | Trades | WinRate | PF | MaxDD |
|--------|---------|-------|--------|---------|-----|-------|
| BTC 1D | BASELINE | +32.71% | 124 | 45.2% | 1.23 | 23.8% |
| BTC 1D | **NAMIESTNIK** | +27.32% | 67 | **55.2%** | **1.57** | **5.3%** |
| ETH 1D | BASELINE | +23.80% | 160 | 43.8% | 1.09 | 26.4% |
| ETH 1D | **NAMIESTNIK** | +14.84% | 79 | 48.1% | 1.19 | **11.9%** |
| BTC 1H | BASELINE | -4.34% | 101 | 44.6% | 0.85 | 13.9% |
| BTC 1H | **NAMIESTNIK** | -6.83% | 90 | 43.3% | 0.74 | **10.0%** |
| ETH 1H | BASELINE | -9.14% | 102 | 48.0% | 0.77 | 11.2% |
| ETH 1H | **NAMIESTNIK** | **-4.65%** | 89 | 42.7% | 0.86 | **10.0%** |

> **Wzorzec:** Namiestnik z Timeframe-Aware **redukuje drawdown na KAŻDYM zestawie**.
> Na 1D (INVEST cap 2×) handluje selektywnie: mniej pozycji, wyższy WinRate, PF,
> a **drawdown spada 4.5× na BTC (23.8→5.3%)** i 2.2× na ETH (26.4→11.9%).
> Na 1H wynik mieszany (ETH +4.5pp, BTC -2.5pp), ale DD wszędzie niżej.
> Filozofia: profil ryzyka > surowy zysk (przygotowanie pod dźwignię i kapitał realny).

---

## 🗺️ Fazy rozwoju

- **Faza 1 (✅ teraz):** deterministyczna tablica reżim × styl.
- **Faza 2 (Shapley/MRC, arXiv:2605.24490):** wagi reżimów uczone online z atrybucji.
- **Faza 3 (MAML, arXiv:2505.03659):** meta-uczenie selekcji strategii per reżim.
- **MTF (multi-timeframe):** wyższy TF = bias, niższy TF = wejście (deep-research: 2/3 TF zgody).

---

## 🔌 API (dla programisty)

```python
from imperium.koloseum.namiestnik import get_namiestnik

nam = get_namiestnik()
d = nam.decyduj(rezim="TREND_STRONG", interwal="1D")
#  d.styl="INVEST", d.tryb="filtr", d.lewar_cap=2, d.rynek="SPOT",
#  d.prog_pewnosci=0.605, d.czy_grac=True

lewar = nam.skaluj_dzwignie(dzwignia_base=10, rezim="TREND_STRONG", interwal="1D")
#  → przycięte do lewar_cap=2

print(nam.raport())   # tablica reżimów + profile stylu
```

---

*„Namiestnik nie poluje — Namiestnik mówi łowcom, jak dziś polować."*
*— NAMIESTNIK.md | Faza 1 | 2026-06-03*
