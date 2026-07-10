"""
Filtr Ekonomiczny (ECON — market price of risk) — brama „zbyt dobre, by było prawdziwe".

DLA NOWICJUSZA: rynki nie rozdają darmowego obiadu. Jeśli sizing dostaje zakład, który
IMPLIKUJE nierealnie wysoką nagrodę-za-ryzyko (np. „wygram w 90% przy wypłacie 5:1"), to
prawie na pewno błąd estymaty — przeuczone p albo zawyżone RR — a nie realna okazja. Ten
filtr WETUJE takie zakłady, ZANIM Kelly policzy z nich gigantyczną stawkę.

PODSTAWA (ARTEMIS, arXiv 2603.18107 — „A Neuro-Symbolic Framework for Economically
Constrained Market Dynamics", marzec 2026): jednym z dwóch ograniczeń ekonomicznych jest
kara MARKET PRICE OF RISK, która OGRANICZA chwilowy współczynnik Sharpe'a modelu — sygnał
implikujący Sharpe ponad ekonomicznie wiarygodny pułap jest odrzucany. Tu realizujemy tę
zasadę DETERMINISTYCZNIE (bez sieci neuronowej — filozofia Bramy Kalkulatora): liczymy
Sharpe POJEDYNCZEGO ZAKŁADU z (p, RR) i porównujemy z pułapem λ_max.
  Link: https://arxiv.org/abs/2603.18107  (⚠️ pełny tekst niezweryfikowany — abstrakt potwierdzony)

MATEMATYKA (czysty OHLCV-agnostyk — działa na samych p i RR):
  Wynik zakładu w jednostkach R (ryzyko = 1R):
    wygrana:  +RR  z prawdopodobieństwem p
    przegrana: −1   z prawdopodobieństwem (1−p)
  Oczekiwana przewaga:   edge = p·RR − (1−p)          [E[R]]
  Drugi moment:          E[R²] = p·RR² + (1−p)
  Wariancja:             var = E[R²] − edge²
  Sharpe zakładu:        S = edge / √var               (nagroda-za-ryzyko zakładu)

WETO (monotoniczna ostrożność — filtr tylko ZAOSTRZA, nigdy nie luzuje):
  • edge ≤ 0            → brak przewagi ekonomicznej (nie betujemy ujemnego EV),
  • S > λ_max           → market price of risk przekroczony („too good to be true"),
  → dozwolone = False. W innym razie przepuszcza.

ABSTYNENCJA (Prawo XV): RR ≤ 0 → PRZEPUŚĆ (brak sensownego zakładu; nie wetujemy przy
niewiedzy — lepiej nie filtrować niż filtrować na ślepo). Uwaga: zdegenerowana wariancja
(p=0 lub p=1) NIE jest abstynencją — p=0 to pewna strata (weto: edge≤0), p=1 to pewna
wygrana (weto: skrajny market price of risk). Abstynencja dotyczy wyłącznie RR≤0.

WPIĘCIE (ZASADA WPIĘCIA W ŚCIEŻKĘ DECYZYJNĄ): opt-in, domyślnie OFF. `SizingPrzekonania.
kelly_frakcja(..., filtr_ekonomiczny=None)` bez filtra zachowuje się IDENTYCZNIE jak dawniej.
λ_max do KALIBRACJI areną (A/B) — domyślny 2.0 dobrany zachowawczo (patrz test granic).

Użycie:
    f = FiltrEkonomiczny()
    w = f.ocen(p_wygranej=0.9, rr=5.0)
    if not w.dozwolone:
        ...  # weto, powód w w.powod, S w w.sharpe_zakladu
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class WerdyktEkonomiczny:
    """Wynik oceny filtra: czy zakład ekonomicznie wiarygodny + diagnostyka."""
    dozwolone: bool
    powod: str
    edge: float            # oczekiwana przewaga w jednostkach R (E[R])
    sharpe_zakladu: float  # S = edge/√var (0.0 gdy abstynencja/degeneracja)
    prog_lambda: float     # pułap market price of risk, z którym porównano


@dataclass
class FiltrEkonomiczny:
    """
    Brama market-price-of-risk (ECON) na ekonomii zakładu.

    lambda_max:  pułap Sharpe'a POJEDYNCZEGO zakładu. Powyżej → weto „zbyt dobre".
                 Zachowawczy domyślny 2.0: przepuszcza wiarygodne (p=0.7, RR=3 → S≈0.98),
                 wetuje nierealne (p=0.9, RR=5 → S≈2.44). Do kalibracji areną.
    """
    lambda_max: float = 2.0

    def ocen(self, p_wygranej: float, rr: float) -> WerdyktEkonomiczny:
        # Abstynencja (Prawo XV): RR niedodatnie = brak sensownego zakładu → przepuść.
        if rr <= 0:
            return WerdyktEkonomiczny(True, "RR ≤ 0 — abstynencja (brak zakładu)",
                                      0.0, 0.0, self.lambda_max)

        p = max(0.0, min(1.0, p_wygranej))
        q = 1.0 - p
        edge = p * rr - q                       # E[R]
        e_r2 = p * rr * rr + q                   # E[R²]
        var = e_r2 - edge * edge                 # Var[R] ≥ 0 dla p∈[0,1], RR>0

        # 1. Brak przewagi ekonomicznej SPRAWDZAMY PIERWSZY — pewna strata (p=0, var=0)
        #    to weto, nie abstynencja. Kolejność ma znaczenie (test granicy p=0).
        if edge <= 0.0:
            sharpe = edge / math.sqrt(var) if var > 1e-12 else -math.inf
            return WerdyktEkonomiczny(
                False, f"brak przewagi ekonomicznej (edge {edge:.3f} ≤ 0) — nie betujemy ujemnego EV",
                edge, sharpe, self.lambda_max)

        # 2. edge > 0 przy zdegenerowanej wariancji ⇒ p=1 (pewna wygrana) — skrajny
        #    „too good to be true" → weto (market price of risk).
        if var <= 1e-12:
            return WerdyktEkonomiczny(
                False, "pewna wygrana (p=1) — ekonomicznie niewiarygodne (market price of risk)",
                edge, math.inf, self.lambda_max)

        sharpe = edge / math.sqrt(var)

        if sharpe > self.lambda_max:
            return WerdyktEkonomiczny(
                False, f"market price of risk przekroczony (Sharpe zakładu {sharpe:.2f} "
                       f"> λ_max {self.lambda_max:.2f}) — zbyt dobre, by było prawdziwe",
                edge, sharpe, self.lambda_max)

        return WerdyktEkonomiczny(
            True, f"ekonomicznie wiarygodne (edge {edge:.3f}, Sharpe {sharpe:.2f} ≤ {self.lambda_max:.2f})",
            edge, sharpe, self.lambda_max)
