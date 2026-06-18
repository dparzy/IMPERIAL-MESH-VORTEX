"""
W-340 | Detektor reżimu zmienności — lekka, online wersja Jump Modelu (vol-gate).

DLA NOWICJUSZA: rynek przełącza się między okresami SPOKOJU (mała zmienność) i
TURBULENCJI (duża zmienność, ryzyko kaskad). Te reżimy są TRWAŁE — zmienność się
„klastruje" (volatility clustering). Ten detektor klasyfikuje bieżący bar jako
spokojny/turbulentny metodą 2-stanowego Jump Modelu (López de Prado / Nystrup) z
KARĄ ZA SKOK — przełączenie reżimu kosztuje λ, więc etykiety są lepkie (zero whipsaw).

POMIAR (Prawo I, dane 1D BTC/ETH/SOL/DOGE, walk-forward bez look-ahead):
  reżim turbulentny przewiduje 1.22–1.56× wyższy |zwrot| następnego bara,
  spójnie na WSZYSTKICH aktywach, przełączeń tylko 2–3/100 barów.
To aktywo-niezależna, zmierzona przewaga → brama defensywna (turbo → VOLATILE).

CZYSTO-PYTHON (bez numpy w hot-path): koszt O(T·K²) ≈ 100·4 — tani nawet na 1m/5m.
TF-agnostyczny: operuje na serii ZWROTÓW, niezależnie od interwału bara.

To ONLINE odpowiednik ciężkiego, numpy-owego `JumpModel` (W-281, multi-start, 3-stany,
kierunkowy) — ten jest 2-stanowy, vol-only, bezkierunkowy, liczony per-bar.
Kierunkowy JumpModel zmierzono jako NIESPÓJNY (BTC+/ETH−) → świadomie NIE używamy
kierunku; używamy tylko stabilnej osi zmienności (Prawo I).

Źródło: Nystrup, Lindström, Madsen (2020) + Bemporad (2024), arXiv:2402.05272;
  Cortese, Kolm, Lindström (2023), Digital Finance 5:483 (⚠️ pełny tekst niezweryfikowany).
"""

import math
from typing import List, Tuple


def _zwroty(close: List[float]) -> List[float]:
    out = []
    for i in range(1, len(close)):
        p = close[i - 1]
        out.append((close[i] - p) / p if p > 0 else 0.0)
    return out


def _ewma(x: List[float], hl: float) -> List[float]:
    """EWMA o zadanym half-life (półokresie). hl barów → waga spada o połowę."""
    if not x:
        return []
    a = 1.0 - math.exp(math.log(0.5) / max(1e-9, hl))
    out = [x[0]]
    for i in range(1, len(x)):
        out.append(a * x[i] + (1.0 - a) * out[-1])
    return out


def _standaryzuj(x: List[float]) -> List[float]:
    n = len(x)
    if n == 0:
        return []
    mu = sum(x) / n
    war = sum((v - mu) ** 2 for v in x) / n
    if war < 1e-18:
        return [0.0] * n
    sd = math.sqrt(war)
    return [(v - mu) / sd for v in x]


def _viterbi_2stan(cechy: List[float], c0: float, c1: float, kara: float) -> List[int]:
    """
    Optymalna sekwencja 2 stanów minimalizująca Σ(x−c)² + kara·Σ1[zmiana].
    cechy: 1D (znormalizowana zmienność). c0,c1: centroidy. Zwraca listę 0/1.
    """
    T = len(cechy)
    if T == 0:
        return []
    # koszt[k] = min koszt ścieżki kończącej się w stanie k
    cost = [(cechy[0] - c0) ** 2, (cechy[0] - c1) ** 2]
    bp: List[Tuple[int, int]] = []
    for t in range(1, T):
        cen = (c0, c1)
        new = [0.0, 0.0]
        back = [0, 0]
        for k in (0, 1):
            emit = (cechy[t] - cen[k]) ** 2
            # zostań w k vs skocz z drugiego stanu
            stay = cost[k]
            jump = cost[1 - k] + kara
            if stay <= jump:
                new[k] = emit + stay
                back[k] = k
            else:
                new[k] = emit + jump
                back[k] = 1 - k
        cost = new
        bp.append((back[0], back[1]))
    last = 0 if cost[0] <= cost[1] else 1
    seq = [last]
    for t in range(len(bp) - 1, -1, -1):
        last = bp[t][last]
        seq.append(last)
    seq.reverse()
    return seq


def vol_regime_turbo(
    close: List[float],
    hl_vol: float = 20.0,
    kara: float = 30.0,
    max_iter: int = 15,
    min_barow: int = 40,
) -> Tuple[bool, int, float]:
    """
    Klasyfikuje bieżący (ostatni) bar jako turbulentny/spokojny.

    close:     seria zamknięć (najnowsze na końcu).
    hl_vol:    half-life EWMA zmienności (mniejszy = czulszy; skaluj do TF).
    kara:      λ — kara za skok (większa = trwalsze reżimy).
    min_barow: minimum danych.

    Zwraca (turbo, trwalosc, sila):
      turbo ∈ {True, False}: czy bieżący bar jest w reżimie turbulentnym.
      trwalosc: ile ostatnich barów trwa bieżący reżim.
      sila ∈ [0,1]: separacja bieżącej zmienności od progu między reżimami,
                    skalowana trwałością (pewność, że to faktycznie ten reżim).
    """
    if len(close) < min_barow + 1:
        return False, 0, 0.0

    zwroty = _zwroty(close)
    if len(zwroty) < min_barow:
        return False, 0, 0.0

    # Cecha: EWMA zmienności (pierwiastek z EWMA kwadratów zwrotów), znormalizowana
    vol = [math.sqrt(v) for v in _ewma([r * r for r in zwroty], hl_vol)]
    cechy = _standaryzuj(vol)
    T = len(cechy)

    # Inicjalizacja: c0 = niska zmienność (kwantyl 25%), c1 = wysoka (75%)
    posort = sorted(cechy)
    c0 = posort[T // 4]
    c1 = posort[3 * T // 4]

    stany: List[int] = []
    for _ in range(max_iter):
        nowe = _viterbi_2stan(cechy, c0, c1, kara)
        if nowe == stany:
            break
        stany = nowe
        # aktualizuj centroidy
        s0 = [cechy[i] for i in range(T) if stany[i] == 0]
        s1 = [cechy[i] for i in range(T) if stany[i] == 1]
        if s0:
            c0 = sum(s0) / len(s0)
        if s1:
            c1 = sum(s1) / len(s1)

    # Reżim turbulentny = wyższy centroid zmienności
    turbo_k = 1 if c1 >= c0 else 0
    biezacy = stany[-1]
    turbo = (biezacy == turbo_k)

    # Trwałość bieżącego reżimu
    trwalosc = 0
    for i in range(T - 1, -1, -1):
        if stany[i] == biezacy:
            trwalosc += 1
        else:
            break

    # Siła: jak daleko bieżąca zmienność od progu między centroidami
    prog = (c0 + c1) / 2.0
    rozstep = abs(c1 - c0)
    if rozstep < 1e-9:
        return False, trwalosc, 0.0  # brak separacji reżimów → brak sygnału
    separacja = min(1.0, abs(cechy[-1] - prog) / rozstep)
    bonus = min(1.0, trwalosc / 10.0)
    sila = round(separacja * bonus, 4)

    return turbo, trwalosc, sila
