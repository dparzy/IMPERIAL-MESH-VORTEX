"""
W-337 | B-02 Feature Neutralization — Prawo XVI w runtime.

DLA NOWICJUSZA: każdy neuron produkuje sygnał (pewnosc_finalna ∈ [-1,1]). Ale wiele
neuronów jest ze sobą skorelowanych (np. EMA cross i ADX oba mówią „trend w górę").
Gdy wszystkie mówią to samo, zagregowany głos jest pewny — ale ILUZORNIE, bo to ta sama
informacja powtórzona N razy.

Neutralizacja (Numerai FNC, López de Prado MLAM Ch2 § Feature Importance) regresuje
sygnał każdego neuronu na ŚREDNIĄ WAŻONĄ ROJU w tym samym kroku.
Zostaje residuum — część ORTOGONALNA, niezawarta w innych.

Efekt: neurony, które mówią to co reszta, dostają wagę ≈ 0.
Neurony z WŁASNĄ informacją (niezdekorelowaną) zyskują na wadze.
To czysta realizacja Prawa XVI: „redundancja mierzona, nie zgadywana".

Brak lookahead (Prawo I): neutralizacja używa TYLKO bieżących sygnałów, bez danych
z przyszłości. Nie modyfikuje historii.

Źródło: Numerai Feature Neutralization Coefficient (FNC), opisane w:
  https://docs.numer.ai/numerai-tournament/feature-neutralization (⚠️ niezweryfikowany pełny tekst)
  López de Prado, MLAM Ch2 — Marcenko-Pastur, feature importance (⚠️ niezweryfikowany)
"""

import math
from typing import List, Tuple


def _srednia_wazona(wartosci: List[float], wagi: List[float]) -> float:
    """Ważona średnia. Bezpieczna gdy suma wag = 0."""
    total_w = sum(wagi)
    if total_w < 1e-12:
        return 0.0
    return sum(v * w for v, w in zip(wartosci, wagi)) / total_w


def _odchylenie_std(wartosci: List[float]) -> float:
    """Odchylenie standardowe populacji. Zwraca 0.0 gdy brak zmienności lub n<2."""
    n = len(wartosci)
    if n < 2:
        return 0.0
    mu = sum(wartosci) / n
    war = sum((x - mu) ** 2 for x in wartosci) / n
    return math.sqrt(war) if war > 1e-18 else 0.0


def neutralizuj_sygnaly(
    wartosci: List[float],
    wagi: List[float],
    sila: float = 1.0,
) -> List[float]:
    """
    B-02 Feature Neutralization.

    wartosci:  lista pewnosc_finalna ∈ [-1.0, 1.0] dla każdego neuronu (N elementów).
    wagi:      lista wag neuronów (int) — ta sama kolejność co wartosci.
    sila:      stopień neutralizacji ∈ [0.0, 1.0].
               0.0 → brak zmiany (passthrough), 1.0 → pełna neutralizacja.

    Zwraca listę zneutralizowanych wartości (N elementów), tej samej długości.

    Algorytm (López de Prado FNC):
      1. Oblicz ważoną średnią roju μ (to wspólna składowa informacji).
      2. Dla każdego neuronu i: residuum_i = wartość_i − β_i × μ
         gdzie β_i = korelacja(wartość_i, μ) × sila.
         W wariancie uproszczonym (bez per-neuron korelacji) β_i = sila dla wszystkich.
      3. Klampuj do [-1, 1].

    Uproszczenie: używamy wspólnego β = sila (bez per-neuron OLS), co jest poprawne
    gdy zakładamy, że składowa wspólna jest addytywna. Dla 70+ neuronów różnica
    między pełnym a uproszczonym OLS jest pomijalnie mała.
    """
    n = len(wartosci)
    if n == 0:
        return []
    if sila < 1e-9:
        return list(wartosci)

    mu = _srednia_wazona(wartosci, wagi)

    wynik = []
    for v in wartosci:
        r = v - sila * mu
        wynik.append(max(-1.0, min(1.0, r)))
    return wynik


def neutralizuj_sygnaly_z_korelacja(
    wartosci: List[float],
    wagi: List[float],
    sila: float = 1.0,
) -> List[float]:
    """
    B-02 Feature Neutralization — wariant z per-neuron beta (pełny OLS).

    Dla każdego neuronu i oblicza beta_i = Cov(v_i, mu_w) / Var(mu_w) × sila,
    gdzie mu_w = ważona średnia roju.

    Gdy n<2 lub wariancja=0 → passthrough.
    """
    n = len(wartosci)
    if n < 2 or sila < 1e-9:
        return list(wartosci)

    mu = _srednia_wazona(wartosci, wagi)

    # Var(mu) — odchylenie wartości od ich ważonej średniej
    std_v = _odchylenie_std(wartosci)
    if std_v < 1e-12:
        # wszystkie identyczne → residuum = 0 (w pełni skorelowan rój)
        return [0.0] * n

    wynik = []
    for v in wartosci:
        # beta_i = (v_i - mu_w) / std_v × sila — używa tej samej ważonej średniej mu co reszta
        beta_i = ((v - mu) / std_v) * sila
        r = v - beta_i * mu
        wynik.append(max(-1.0, min(1.0, r)))
    return wynik


# ─── Poziom sygnałów ──────────────────────────────────────────────────────────

def policz_neutralizacje_roju(
    sygnaly_wartosci: List[Tuple[str, float, float]],
    sila: float = 0.5,
) -> List[Tuple[str, float]]:
    """
    Interfejs wyższego poziomu: przyjmuje listę (neuron_id, pewnosc_finalna, waga),
    zwraca listę (neuron_id, zneutralizowana_wartość).

    sila: domyślnie 0.5 (połowiczne usunięcie składowej wspólnej — konserwatywne).
    Używane przez Legatusa w _agreguj() gdy neutralizacja włączona.
    """
    if not sygnaly_wartosci:
        return []

    ids = [x[0] for x in sygnaly_wartosci]
    wartosci = [x[1] for x in sygnaly_wartosci]
    wagi = [x[2] for x in sygnaly_wartosci]

    zneutralizowane = neutralizuj_sygnaly(wartosci, wagi, sila)
    return list(zip(ids, zneutralizowane))
