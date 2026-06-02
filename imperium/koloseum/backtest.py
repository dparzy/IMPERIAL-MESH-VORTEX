"""
🏟️ BACKTEST — przejazd Dyrygenta po prawdziwej historii rynku.

Łączy czytnik CSV + Budowniczy + Dyrygent + PaperTradingEngine w jeden bieg:

    1. Wczytaj historyczne bary (czytnik_csv)
    2. Przesuwaj okno (np. 250 barów) świeca po świecy
    3. W każdym kroku:
       a) zbuduj wskaźniki z okna (Brama/TA-Lib)
       b) Dyrygent.cykl → ewentualne wejście
       c) engine.przetworz_bar(bieżąca świeca) → aktualizacja/zamknięcie pozycji
    4. Na koniec: zamknij otwarte po ostatniej cenie, drukuj raport

Zasada: backtest NIE zagląda w przyszłość — wskaźniki liczone TYLKO z barów
do bieżącej świecy włącznie (okno kończy się na 'teraz'). Prawo I + uczciwość.

Użycie (CLI):
    python -m imperium.koloseum.backtest dane/dzienne/Binance_BTCUSDT_d.csv 1D
    python -m imperium.koloseum.backtest dane/godzinowe/Binance_BTCUSDT_1h.csv 1H 500
"""

import logging
import sys
from typing import List, Dict, Any, Optional

from imperium.akwedukty.czytnik_csv import wczytaj_csv
from imperium.koloseum.dyrygent import Dyrygent
from imperium.koloseum.paper_trading import PaperTradingEngine, BarData
from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara

logger = logging.getLogger("Backtest")


def _bar_data(b: Dict[str, Any]) -> BarData:
    return BarData(
        timestamp=b["timestamp"], open=b["open"], high=b["high"],
        low=b["low"], close=b["close"], volume=b["volume"],
        symbol=b["symbol"], interwal=b.get("interwal", ""),
    )


def backtest(
    sciezka: str,
    interwal: str,
    okno: int = 250,
    kapital_startowy: float = 10_000.0,
    max_barow: Optional[int] = None,
    min_pewnosc: float = 0.55,
) -> PaperTradingEngine:
    """
    Przejeżdża Dyrygentem po historii. Zwraca silnik z pełną historią zamknięć.

    okno:      ile barów wstecz widzi rój przy każdej decyzji (potrzebne dla EMA_200)
    max_barow: ogranicz liczbę przetworzonych barów (None = całość)
    """
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.rejestr import zbuduj_legatusa

    bary = wczytaj_csv(sciezka, interwal=interwal, limit=max_barow)
    if len(bary) <= okno:
        raise ValueError(f"Za mało barów ({len(bary)}) dla okna {okno}")

    symbol = bary[0]["symbol"]
    legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
    budowniczy = BudowniczyWskaznikow()
    engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                sesja_id=f"BT-{symbol}-{interwal}")
    dyrygent = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(),
                        engine=engine, budowniczy=budowniczy, min_pewnosc=min_pewnosc)

    wejscia = 0
    weta = 0
    for i in range(okno, len(bary)):
        biezacy = bary[i]
        okno_barow = bary[i - okno: i + 1]   # do bieżącej świecy włącznie (bez przyszłości)

        # 1. Aktualizuj otwarte pozycje bieżącą świecą
        engine.przetworz_bar(_bar_data(biezacy))

        # 2. Decyzja na podstawie okna
        decyzja = dyrygent.cykl(symbol, okno_barow,
                                rezim="NORMAL", timestamp=biezacy["timestamp"])
        if decyzja.wszedl:
            wejscia += 1
        elif decyzja.etap in ("PRETORIANIE_WETO", "LEGATUS_WETO"):
            weta += 1

    # 3. Zamknij pozostałe otwarte po ostatniej cenie
    ostatnia_cena = {symbol: bary[-1]["close"]}
    engine.zamknij_wszystkie(ostatnia_cena, powod="MANUAL")

    logger.info(f"[Backtest] {symbol} {interwal}: {len(bary)} barów, "
                f"{wejscia} wejść, {weta} wet Pretorianów")
    return engine


def main():
    logging.basicConfig(level=logging.WARNING,
                        format="%(asctime)s | %(levelname)s | %(message)s")
    logging.getLogger("Rój").setLevel(logging.ERROR)

    if len(sys.argv) < 3:
        print("Użycie: python -m imperium.koloseum.backtest <plik.csv> <interwal> [max_barow]")
        sys.exit(1)

    sciezka = sys.argv[1]
    interwal = sys.argv[2]
    max_barow = int(sys.argv[3]) if len(sys.argv) > 3 else None

    engine = backtest(sciezka, interwal, max_barow=max_barow)
    engine.drukuj_raport()


if __name__ == "__main__":
    main()
