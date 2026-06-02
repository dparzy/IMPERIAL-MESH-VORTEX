"""
🔍 DETEKTOR LOOKAHEAD-BIAS — strażnik uczciwości backtestu.

Inspiracja: Freqtrade `lookahead-analysis`
(https://www.freqtrade.io/en/stable/lookahead-analysis/) — zweryfikowana
2026-06-02 w badaniu deep-research (REJESTR_INSPIRACJI.md, poz. LA-01).

Idea (Freqtrade, przeniesiona na rój Imperium):
    Sygnał na barze `i` MUSI być identyczny niezależnie od tego, czy w zbiorze
    danych istnieją bary PO `i`, czy nie. Jeśli odcięcie przyszłości zmienia
    decyzję na barze przeszłym — pipeline zagląda w przyszłość (lookahead-bias).

Metoda:
    1. Policz ślad głosów roju na PEŁNYM zbiorze barów (kierunek + pewność na barze i).
    2. Policz ten sam ślad na zbiorze OBCIĘTYM do `odciecie` barów.
    3. Dla wspólnego zakresu (i < odciecie) głosy muszą być identyczne co do bitu.
    4. Każda rozbieżność = czerwony alarm (Prawo I: rój nie może znać przyszłości).

To weryfikacja niezmiennika okna `bary[i-okno:i+1]` z backtest.py — jeśli ktoś
kiedyś przypadkiem policzy wskaźnik z całej serii (np. normalizacja min/max po
całości), ten test to wychwyci.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("Lookahead")

# Tolerancja numeryczna — głosy liczone z tych samych barów muszą być
# identyczne; drobny epsilon chroni przed szumem float przy reorderze sum.
_EPS = 1e-9


def _slad_glosow(
    bary: List[Dict[str, Any]],
    okno: int,
    symbol: str,
    legatus,
    budowniczy,
    rezim: str = "NORMAL",
) -> Dict[int, Tuple[str, float]]:
    """
    Dla każdego baru i >= okno liczy głos roju (kierunek, pewność_agregatu)
    z okna `bary[i-okno:i+1]` — czyli wyłącznie z przeszłości i teraźniejszości.

    Zwraca: {i: (kierunek, pewnosc)}.
    """
    slad: Dict[int, Tuple[str, float]] = {}
    for i in range(okno, len(bary)):
        okno_barow = bary[i - okno: i + 1]
        wskazniki = budowniczy.zbuduj(okno_barow)
        raport = legatus.fokus(symbol, wskazniki, rezim=rezim, bary=okno_barow)
        slad[i] = (raport.kierunek, float(raport.pewnosc_agregatu))
    return slad


def _swiezy_roj(aktywuj_smc: bool = True):
    """Buduje świeży, deterministyczny komplet Legatus + Budowniczy."""
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.rejestr import zbuduj_legatusa
    legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55,
                              aktywuj_smc=aktywuj_smc)
    return legatus, BudowniczyWskaznikow()


def wykryj_lookahead(
    bary: List[Dict[str, Any]],
    okno: int = 250,
    odciecie: Optional[int] = None,
    symbol: Optional[str] = None,
    aktywuj_smc: bool = True,
) -> List[Dict[str, Any]]:
    """
    Sprawdza, czy rój nie zagląda w przyszłość.

    bary:     pełna seria OHLCV (chronologicznie, jak z czytnik_csv).
    okno:     ile barów wstecz widzi rój przy każdej decyzji.
    odciecie: do ilu barów obciąć "przyszłość" (domyślnie 75% długości).
    symbol:   nazwa instrumentu (domyślnie z barów).

    Zwraca listę rozbieżności (pustą = brak lookahead). Każda rozbieżność to
    dict: {bar, pelny: (kier,pew), uciety: (kier,pew)}.
    """
    if len(bary) <= okno + 2:
        raise ValueError(f"Za mało barów ({len(bary)}) dla okna {okno}")
    if odciecie is None:
        odciecie = max(okno + 2, int(len(bary) * 0.75))
    if odciecie >= len(bary):
        raise ValueError(f"Odcięcie {odciecie} >= liczba barów {len(bary)}")
    if symbol is None:
        symbol = bary[0].get("symbol", "?")

    # Dwa niezależne, świeże roje — żeby stan jednego nie wyciekał do drugiego.
    legatus_pelny, bud_pelny = _swiezy_roj(aktywuj_smc)
    legatus_ucz, bud_ucz = _swiezy_roj(aktywuj_smc)

    slad_pelny = _slad_glosow(bary, okno, symbol, legatus_pelny, bud_pelny)
    slad_ucany = _slad_glosow(bary[:odciecie], okno, symbol, legatus_ucz, bud_ucz)

    rozbieznosci: List[Dict[str, Any]] = []
    for i in slad_ucany:                       # wspólny zakres: i < odciecie
        kier_p, pew_p = slad_pelny[i]
        kier_u, pew_u = slad_ucany[i]
        if kier_p != kier_u or abs(pew_p - pew_u) > _EPS:
            rozbieznosci.append({
                "bar": i,
                "pelny": (kier_p, pew_p),
                "uciety": (kier_u, pew_u),
            })

    if rozbieznosci:
        logger.error(f"[Lookahead] 🚨 {len(rozbieznosci)} rozbieżności — rój zagląda w przyszłość!")
    else:
        logger.info(f"[Lookahead] ✅ {len(slad_ucany)} barów sprawdzonych, zero przecieku przyszłości")
    return rozbieznosci


def raport_lookahead(sciezka: str, interwal: str, okno: int = 250,
                     max_barow: Optional[int] = None) -> bool:
    """
    CLI-friendly: wczytuje CSV, uruchamia detektor, drukuje werdykt.
    Zwraca True gdy czysto (brak lookahead), False gdy wykryto przeciek.
    """
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    bary = wczytaj_csv(sciezka, interwal=interwal, limit=max_barow)
    rozb = wykryj_lookahead(bary, okno=okno)
    print(f"\n{'═'*70}")
    print(f"  🔍 DETEKTOR LOOKAHEAD — {sciezka} ({interwal}, {len(bary)} barów)")
    print(f"{'═'*70}")
    if not rozb:
        print(f"  ✅ CZYSTO — zero przecieku przyszłości (Prawo I zachowane)")
    else:
        print(f"  🚨 LOOKAHEAD-BIAS — {len(rozb)} rozbieżności:")
        for r in rozb[:10]:
            print(f"     bar {r['bar']}: pełny={r['pelny']} ≠ ucięty={r['uciety']}")
    print(f"{'═'*70}\n")
    return not rozb


def main():
    import sys
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("Rój").setLevel(logging.ERROR)
    if len(sys.argv) < 3:
        print("Użycie: python -m imperium.koloseum.lookahead <plik.csv> <interwal> [max_barow]")
        sys.exit(1)
    sciezka, interwal = sys.argv[1], sys.argv[2]
    max_barow = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
    czysto = raport_lookahead(sciezka, interwal, max_barow=max_barow)
    sys.exit(0 if czysto else 1)


if __name__ == "__main__":
    main()
