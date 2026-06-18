"""
W-336 | CUSUM change-point detector — wykrywa, że REŻIM właśnie się zmienił.

DLA NOWICJUSZA: większość neuronów mówi „jest trend/range". Ten mówi co innego:
„WŁAŚNIE nastąpiła ZMIANA — przełom strukturalny w dynamice cen". CUSUM (Cumulative
Sum, Page 1954; filtr zdarzeń López de Prado AFML Ch17) kumuluje znormalizowane
zwroty: gdy suma w górę przebije próg h → przełom byczy, w dół → przełom niedźwiedzi.
Po przebiciu licznik się zeruje (świeży start).

To informacja ortogonalna do momentum (Prawo XVI): momentum mierzy SIŁĘ trwającego
ruchu; CUSUM-break mierzy MOMENT przełamania — sygnał wczesny, nie podążający.

Brak lookahead (Prawo I): w barze t używa wyłącznie zwrotów do bara t.
Źródło: Page (1954) CUSUM; López de Prado, Advances in Financial ML, Ch.17 (CUSUM filter).
"""

import math
from typing import List, Optional, Tuple


def _zwroty(close: List[float]) -> List[float]:
    """Zwroty procentowe bar-do-bara. Pomija pary z niedodatnią ceną bazową."""
    out = []
    for i in range(1, len(close)):
        prev = close[i - 1]
        if prev > 0:
            out.append((close[i] - prev) / prev)
        else:
            out.append(0.0)
    return out


def cusum_break(
    close: List[float],
    prog_h: float = 5.0,
    min_barow: int = 20,
    okno_swiezosci: int = 3,
) -> Tuple[Optional[str], float]:
    """
    Wykrywa przełom CUSUM w OSTATNICH `okno_swiezosci` barach serii.

    close:           seria zamknięć (najnowsze na końcu).
    prog_h:          próg przebicia (w jednostkach odchyleń std skumulowanych zwrotów).
    min_barow:       minimalna długość serii — inaczej (None, 0.0) (Prawo I).
    okno_swiezosci:  ile ostatnich kroków uznajemy za „świeży" przełom (sygnał wczesny).

    Zwraca (kierunek, sila):
      ("LONG",  s)  — świeży przełom w górę (nowy reżim byczy)
      ("SHORT", s)  — świeży przełom w dół
      (None, 0.0)   — brak świeżego przełomu lub za mało danych
    sila ∈ (0,1] rośnie z nadwyżką ponad próg, klamrowana.
    """
    if len(close) < min_barow + 1:
        return None, 0.0
    r = _zwroty(close)
    n = len(r)
    if n < min_barow:
        return None, 0.0

    sr = sum(r) / n
    war = sum((x - sr) ** 2 for x in r) / n
    if war <= 1e-18:
        return None, 0.0  # płaska seria — brak zmienności, brak przełomu
    sd = math.sqrt(war)

    s_pos = 0.0
    s_neg = 0.0
    # Krok, w którym nastąpił ostatni przełom, oraz jego kierunek
    ostatni_krok = None
    ostatni_kier = None
    ostatnia_nadwyzka = 0.0
    for idx, x in enumerate(r):
        z = (x - sr) / sd
        s_pos = max(0.0, s_pos + z)
        s_neg = min(0.0, s_neg + z)
        if s_pos > prog_h:
            ostatni_krok = idx
            ostatni_kier = "LONG"
            ostatnia_nadwyzka = s_pos - prog_h
            s_pos = 0.0
            s_neg = 0.0
        elif s_neg < -prog_h:
            ostatni_krok = idx
            ostatni_kier = "SHORT"
            ostatnia_nadwyzka = -s_neg - prog_h
            s_pos = 0.0
            s_neg = 0.0

    if ostatni_krok is None:
        return None, 0.0
    # Świeżość: przełom w ostatnich `okno_swiezosci` krokach (r ma indeksy 0..n-1)
    if ostatni_krok < n - okno_swiezosci:
        return None, 0.0
    sila = min(1.0, 0.30 + ostatnia_nadwyzka * 0.20)
    return ostatni_kier, sila
