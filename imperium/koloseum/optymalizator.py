"""
🔬 OPTYMALIZATOR HIPERPARAMETRÓW — DSR-guided parameter search (W-294).

Inspiracja: Freqtrade (hyperopt), Jesse (Optuna+Ray 2025), arXiv 2412.20138.

DLA NOWICJUSZA: "hyperopt" to szukanie najlepszych parametrów systemu:
jak wysoki próg pewności? jak szerokie okno wskaźników? jak duży ATR-stoploss?
PROBLEM: wybór najlepszego z 100 wariantów zawsze wygeneruje "zwycięzcę" przez
szczęście (selection bias), nawet czysty szum! Dlatego Imperium używa DSR
(Deflated Sharpe Ratio) jako funkcji celu — DSR KARZE za liczbę prób, przez
co szuka parametrów z PRAWDZIWĄ przewagą, nie z przewagą z losowania.

Algorytm: Latin Hypercube Sampling (lepsze pokrycie przestrzeni niż losowanie)
+ selekcja elitarna. Bez zewnętrznych zależności — czyste Python/numpy.

Użycie:
    from imperium.koloseum.optymalizator import optymalizuj, PrzestrzeńParam

    def cel(p):
        engine = backtest(..., min_pewnosc=p['min_pewnosc'], okno=int(p['okno']))
        zwroty = np.diff(engine.krzywa_equity) / engine.krzywa_equity[:-1]
        return float(engine.kapital_calkowity), list(zwroty)

    przestrzenie = [
        PrzestrzeńParam('min_pewnosc', 0.45, 0.75),
        PrzestrzeńParam('okno', 150, 350, krok=25.0),
    ]
    raport = optymalizuj(cel, przestrzenie, n_iteracji=100)
    print(raport.najlepsze_parametry, raport.najlepszy_dsr)
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from imperium.koloseum.walidacja import deflated_sharpe


@dataclass
class PrzestrzeńParam:
    """Definicja zakresu jednego parametru hiperoptymalizacji."""
    nazwa: str
    minimum: float
    maksimum: float
    krok: Optional[float] = None  # None → ciągły; podaj dla dyskretnych (np. okno)


@dataclass
class WynikIteracji:
    """Wynik jednej iteracji optymalizacji."""
    parametry: Dict[str, float]
    dsr: float
    sharpe: float
    n_prob: int
    ok: bool


@dataclass
class RaportOptymalizacji:
    """Pełny raport po zakończeniu optymalizacji."""
    najlepsze_parametry: Dict[str, float]
    najlepszy_dsr: float
    najlepszy_sharpe: float
    n_iteracji: int
    n_udanych: int        # ile przeszło DSR ≥ 0.95
    historia: List[WynikIteracji] = field(default_factory=list)
    ok: bool = False
    czas_s: float = 0.0


def _mapuj_lhs(v01: float, psp: PrzestrzeńParam) -> float:
    """Mapuje wartość LHS [0, 1] na zakres parametru."""
    if psp.krok is not None:
        kroki = round((psp.maksimum - psp.minimum) / psp.krok)
        if kroki < 1:
            return psp.minimum
        i = min(int(v01 * (kroki + 1)), kroki)
        return round(psp.minimum + i * psp.krok, 10)
    return float(psp.minimum + v01 * (psp.maksimum - psp.minimum))


def optymalizuj(
    funkcja_celu: Callable[[Dict[str, float]], Tuple[Any, List[float]]],
    przestrzenie: List[PrzestrzeńParam],
    n_iteracji: int = 100,
    seed: Optional[int] = 42,
    verbose: bool = False,
) -> RaportOptymalizacji:
    """
    DSR-guided random search z Latin Hypercube Sampling.

    funkcja_celu(params) → (kapital_koncowy, lista_zwrotow_per_bar):
        Twoja funkcja backtestu. Przykład:
        lambda p: (eng.kapital_calkowity, list(np.diff(eng.krzywa_equity)/eng.krzywa_equity[:-1]))
        gdzie eng = backtest(..., min_pewnosc=p['min_pewnosc'])

    przestrzenie: lista PrzestrzeńParam.
    n_iteracji:   liczba prób (≥ 50 zalecane). Większa = lepszy coverage,
                  ale DSR będzie surowszy (koryguje selection bias przez n_prob).
    seed:         dla reprodukowalności.
    verbose:      drukuj wyniki każdej iteracji.

    ZASADA: DSR jako cel zamiast Sharpe. Przy 100 próbach DSR podnosi poprzeczkę
    o ~0.4 SR — naturalny filtr przypadkowych zwycięzców.
    """
    if not przestrzenie:
        raise ValueError("Brak przestrzeni parametrów")
    n_dim = len(przestrzenie)
    rng = np.random.default_rng(seed)
    historia: List[WynikIteracji] = []
    start = time.time()

    # Latin Hypercube Sampling: każdy wymiar podzielony na n_iteracji równych stref,
    # jedna próbka z każdej strefy, losowo przesortowane → lepsze pokrycie
    lhs = np.zeros((n_iteracji, n_dim))
    for d in range(n_dim):
        perms = rng.permutation(n_iteracji)
        lhs[:, d] = (perms + rng.random(n_iteracji)) / n_iteracji

    for it in range(n_iteracji):
        parametry: Dict[str, float] = {
            psp.nazwa: _mapuj_lhs(float(lhs[it, d]), psp)
            for d, psp in enumerate(przestrzenie)
        }
        try:
            _, zwroty = funkcja_celu(parametry)
            n_prob_teraz = it + 1  # uczciwa liczba prób = korekta selection bias
            dsr_r = deflated_sharpe(zwroty, n_prob=n_prob_teraz)
            sh = dsr_r.get("sharpe") or 0.0
            dsr_val = dsr_r.get("dsr") or 0.0
            wynik = WynikIteracji(
                parametry=parametry,
                dsr=round(dsr_val, 4),
                sharpe=round(sh if sh is not None else 0.0, 4),
                n_prob=n_prob_teraz,
                ok=bool(dsr_r.get("ok")),
            )
        except Exception:
            wynik = WynikIteracji(
                parametry=parametry, dsr=0.0, sharpe=0.0, n_prob=it + 1, ok=False,
            )
        historia.append(wynik)
        if verbose:
            status = "✅" if wynik.ok else "❌"
            print(f"[{it + 1:3d}/{n_iteracji}] {status} DSR={wynik.dsr:.3f} "
                  f"SR={wynik.sharpe:.3f} {parametry}")

    najlepszy = max(historia, key=lambda w: w.dsr)
    n_udanych = sum(1 for w in historia if w.ok)

    return RaportOptymalizacji(
        najlepsze_parametry=najlepszy.parametry,
        najlepszy_dsr=najlepszy.dsr,
        najlepszy_sharpe=najlepszy.sharpe,
        n_iteracji=n_iteracji,
        n_udanych=n_udanych,
        historia=historia,
        ok=najlepszy.ok,
        czas_s=round(time.time() - start, 2),
    )
