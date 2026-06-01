"""
📊 IMV-DIAG | Diagnostyka Dekorelacji — macierz korelacji sygnałów modułów

ROLA (Prawo XV — mierzyć, nie zgadywać):
  Zasada „brak redundancji" była dotąd stosowana po PODOBIEŃSTWIE (ten sam
  wskaźnik = odrzuć). To błąd: redundancja szkodzi tylko gdy sygnały są
  SKORELOWANE (te same błędy w tych samych momentach). Dwa podobne moduły
  liczone inaczej mogą DEKORELOWAĆ błędy = wartość, nie szum.

  Ten moduł zamienia dogmat w liczbę: na serii barów zbiera wektory sygnałów
  każdego zwiadowcy, liczy macierz korelacji Pearsona i raportuje:
    - pary NADMIAROWO skorelowane (>prog) → kandydaci do scalenia / wagi w dół
    - pary DYWERSYFIKUJĄCE (niska/ujemna korelacja) → filar siły Imperium

  Dzięki temu decyzja „redundancja czy postęp" jest jawna dla Cezara.

Uwaga: działa na zwiadowcach EXP (pure Python, bez TA-Lib) — czyli dokładnie tam,
gdzie pojawiło się pytanie o redundancję elitarnych. Neurony wymagają Bramy
(TA-Lib), więc nie są tu zbierane (mogą być dodane gdy Brama dostępna).
"""

import logging
import math
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("DiagKorelacji")


def sygnal_na_liczbe(kierunek: str, pewnosc: float) -> float:
    """
    Mapuje sygnał na liczbę dla korelacji:
      LONG  → +pewnosc
      SHORT → -pewnosc
      NEUTRAL → 0.0
    Pewność jako amplituda — mocniejszy sygnał waży więcej.
    """
    if kierunek == "LONG":
        return abs(pewnosc)
    if kierunek == "SHORT":
        return -abs(pewnosc)
    return 0.0


def korelacja_pearson(x: List[float], y: List[float]) -> Optional[float]:
    """
    Współczynnik korelacji Pearsona — pure Python.
    Zwraca None gdy któryś wektor ma zerową wariancję (stały sygnał) lub za mało
    danych — wtedy korelacja jest nieokreślona (nie udawaj 0).
    """
    n = len(x)
    if n < 2 or n != len(y):
        return None
    sx = sum(x)
    sy = sum(y)
    mx = sx / n
    my = sy / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    vx = sum((xi - mx) ** 2 for xi in x)
    vy = sum((yi - my) ** 2 for yi in y)
    if vx <= 0 or vy <= 0:
        return None  # stały wektor — korelacja nieokreślona
    return cov / math.sqrt(vx * vy)


def zbierz_sygnaly_zwiadowcow(
    bary: List[Dict[str, Any]],
    zwiadowcy: list,
    okno: int = 60,
    krok: int = 1,
) -> Dict[str, List[float]]:
    """
    Przesuwa okno po serii barów i zbiera sygnał każdego zwiadowcy w każdym kroku.

    bary:   pełna seria OHLCV (im dłuższa, tym wiarygodniejsza korelacja).
    okno:   ile barów widzi zwiadowca w danym kroku (jego kontekst).
    krok:   co ile barów przesuwamy okno (1 = każdy bar).

    Zwraca {KLUCZ: [wartości sygnału w kolejnych krokach]}.
    Pomija zwiadowców wyciszonych (DOSTEPNY=False) — nie mają danych.
    """
    aktywni = [z for z in zwiadowcy if getattr(z, "DOSTEPNY", True)]
    serie: Dict[str, List[float]] = {z.KLUCZ: [] for z in aktywni}

    if len(bary) < okno:
        return serie

    for koniec in range(okno, len(bary) + 1, krok):
        wycinek = bary[koniec - okno:koniec]
        for z in aktywni:
            try:
                raport = z.analizuj(wycinek)
                wartosc = sygnal_na_liczbe(raport.kierunek, raport.pewnosc)
            except Exception as e:
                logger.error(f"[DiagKorelacji] {z.KLUCZ} analizuj() padł: {e}")
                wartosc = 0.0
            serie[z.KLUCZ].append(wartosc)
    return serie


def macierz_korelacji(serie: Dict[str, List[float]]) -> Dict[Tuple[str, str], Optional[float]]:
    """
    Liczy korelację Pearsona dla każdej pary modułów.
    Zwraca {(klucz_a, klucz_b): korelacja} dla a < b (bez duplikatów i przekątnej).
    """
    klucze = sorted(serie.keys())
    wynik: Dict[Tuple[str, str], Optional[float]] = {}
    for i in range(len(klucze)):
        for j in range(i + 1, len(klucze)):
            a, b = klucze[i], klucze[j]
            wynik[(a, b)] = korelacja_pearson(serie[a], serie[b])
    return wynik


def raport_dekorelacji(
    bary: List[Dict[str, Any]],
    zwiadowcy: list,
    okno: int = 60,
    krok: int = 1,
    prog_redundancji: float = 0.80,
    prog_dywersyfikacji: float = 0.20,
) -> Dict[str, Any]:
    """
    Pełny raport dekorelacji dla Cezara (Prawo XV).

    prog_redundancji:    |korelacja| > prog → para nadmiarowa (kandydat do scalenia)
    prog_dywersyfikacji: |korelacja| < prog → para dywersyfikująca (filar siły)

    Zwraca dict z listami par i surową macierzą — gotowy do logu/dashboardu.
    """
    serie = zbierz_sygnaly_zwiadowcow(bary, zwiadowcy, okno=okno, krok=krok)
    macierz = macierz_korelacji(serie)

    redundantne = []
    dywersyfikujace = []
    martwe = []  # stały sygnał (korelacja nieokreślona) — sam w sobie utrata potencjału

    for (a, b), kor in macierz.items():
        if kor is None:
            martwe.append((a, b))
            continue
        if abs(kor) > prog_redundancji:
            redundantne.append((a, b, round(kor, 3)))
        elif abs(kor) < prog_dywersyfikacji:
            dywersyfikujace.append((a, b, round(kor, 3)))

    # Moduły zawsze NEUTRAL w całym oknie (zerowa wariancja) = martwy głos
    stale = [k for k, v in serie.items() if v and len(set(v)) == 1]

    redundantne.sort(key=lambda t: -abs(t[2]))
    dywersyfikujace.sort(key=lambda t: abs(t[2]))

    return {
        "liczba_modulow": len(serie),
        "liczba_krokow": len(next(iter(serie.values()))) if serie else 0,
        "pary_redundantne": redundantne,
        "pary_dywersyfikujace": dywersyfikujace,
        "pary_nieokreslone": martwe,
        "moduly_stale": stale,
        "prog_redundancji": prog_redundancji,
        "prog_dywersyfikacji": prog_dywersyfikacji,
        "macierz": {f"{a}~{b}": (round(k, 3) if k is not None else None)
                    for (a, b), k in macierz.items()},
    }


def sformatuj_raport(rap: Dict[str, Any]) -> str:
    """Czytelny tekst raportu dekorelacji — do konsoli/logu."""
    linie = []
    linie.append("📊 RAPORT DEKORELACJI ZWIADOWCÓW (Prawo XV)")
    linie.append(f"  Modułów: {rap['liczba_modulow']}, kroków: {rap['liczba_krokow']}")

    if rap["moduly_stale"]:
        linie.append(f"\n🚨 MARTWE GŁOSY (zawsze NEUTRAL w oknie): {rap['moduly_stale']}")
        linie.append("   → UTRATA POTENCJAŁU: moduł nic nie wnosi na tych danych.")

    linie.append(f"\n🔴 PARY NADMIAROWE (|kor| > {rap['prog_redundancji']}):")
    if rap["pary_redundantne"]:
        for a, b, k in rap["pary_redundantne"]:
            linie.append(f"   {a} ~ {b}: {k:+.3f}  → kandydat do scalenia / wagi w dół")
    else:
        linie.append("   (brak — dobrze, mało nadmiarowości)")

    linie.append(f"\n🟢 PARY DYWERSYFIKUJĄCE (|kor| < {rap['prog_dywersyfikacji']}):")
    if rap["pary_dywersyfikujace"]:
        for a, b, k in rap["pary_dywersyfikujace"]:
            linie.append(f"   {a} ~ {b}: {k:+.3f}  → filar siły (niezależna informacja)")
    else:
        linie.append("   (brak — sygnały podobne, rozważ większą różnorodność)")

    return "\n".join(linie)
