"""
W-335 C-01 | Cross-sectional Relative Strength — liczony na poziomie KOSZYKA.

Tylko pętla portfelowa (petla_live / backtest_portfel) widzi wszystkie symbole naraz,
więc to ona liczy z-score zwrotu każdego aktywa względem koszyka i wstrzykuje do
wskaźników jako CROSS_RS (neuron C-01 go czyta). Bez koszyka (1 aktywo) → pusty dict.

Brak lookahead (Prawo I): RS w barze t liczony WYŁĄCZNIE ze zwrotów do bara t.
"""

import math
from typing import Dict, List


def zwrot_lookback(zamkniecia: List[float], lookback: int) -> float | None:
    """Zwrot procentowy za ostatnie `lookback` barów. None gdy za mało danych."""
    if len(zamkniecia) < lookback + 1:
        return None
    stary = zamkniecia[-lookback - 1]
    nowy = zamkniecia[-1]
    if stary <= 0:
        return None
    return (nowy - stary) / stary


def cross_sectional_rs(
    close_per_symbol: Dict[str, List[float]],
    lookback: int = 24,
) -> Dict[str, float]:
    """
    Z-score zwrotu każdego symbolu względem koszyka.

    close_per_symbol: {symbol: [zamknięcia...]} — pełna seria do bara bieżącego.
    lookback:         okno zwrotu (np. 24 bary = ~4 dni na 4h).

    Zwraca {symbol: z_score}. Symbole bez wystarczających danych są pomijane.
    Gdy <2 symbole z danymi lub zerowa wariancja koszyka → pusty dict (brak przewagi
    przekrojowej do zmierzenia — Prawo I: nie udawaj sygnału z jednego punktu).
    """
    zwroty: Dict[str, float] = {}
    for sym, close in close_per_symbol.items():
        z = zwrot_lookback(close, lookback)
        if z is not None:
            zwroty[sym] = z

    if len(zwroty) < 2:
        return {}

    wartosci = list(zwroty.values())
    n = len(wartosci)
    srednia = sum(wartosci) / n
    war = sum((w - srednia) ** 2 for w in wartosci) / n
    # Próg epsilon, nie ==0: identyczne zwroty dają wariancję ~1e-34 (błąd float),
    # co bez progu produkowałoby fałszywe z-score ±1.0 z czystego szumu numerycznego.
    if war <= 1e-18:
        return {}  # koszyk porusza się ~identycznie — brak rozróżnienia przekrojowego
    sd = math.sqrt(war)
    return {sym: (z - srednia) / sd for sym, z in zwroty.items()}
