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
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Tylko do adnotacji typu — w runtime importowany leniwie w funkcji (unika cyklu)
    from imperium.biblioteki.arena_trzech_bram import RaportAreny

from imperium.akwedukty.czytnik_csv import wczytaj_csv
from imperium.koloseum.dyrygent import Dyrygent
from imperium.koloseum.namiestnik import get_namiestnik
from imperium.koloseum.paper_trading import PaperTradingEngine, BarData
from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara, BezpiecznikKrzywejKapitalu

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
    tryb: str = "agregat",
    bary: Optional[List[Dict[str, Any]]] = None,
    auto_rezim: bool = False,
    ucz_mwu: bool = False,
    min_pewnosc_interwalu: "Optional[Dict[str, float]]" = None,
    max_bars_otwarcia: "Optional[int]" = None,
    straznik_przewagi: bool = False,
    sl_atr_mult: "Optional[float]" = None,
) -> PaperTradingEngine:
    """
    Przejeżdża Dyrygentem po historii. Zwraca silnik z pełną historią zamknięć.

    okno:       ile barów wstecz widzi rój przy każdej decyzji (potrzebne dla EMA_200)
    max_barow:  ogranicz liczbę przetworzonych barów (None = całość)
    tryb:       rola warstwy strategii ("agregat" / "filtr" / "strategia")
    bary:       opcjonalnie gotowe bary (oszczędza ponownego czytania CSV przy porównaniu trybów)
    auto_rezim: True → klasyfikuj_rezim() na każdym barze + Namiestnik steruje
                trybem/dźwignią/progiem (Faza 1 ożywiona). False → stary "NORMAL".
    ucz_mwu:    True → ZAMKNIĘTA PĘTLA UCZENIA (W-049/W-280/W-285.1): każda
                zamknięta pozycja rozlicza neurony, które głosowały przy wejściu
                (HedgeMWUzPamieciaRezimu — Fixed-Share + pamięć per-reżim), a
                mnożniki wag wracają do Legatusa NA BIEŻĄCO. Bez look-ahead:
                uczymy się wyłącznie z już ZAMKNIĘTYCH transakcji.
    """
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.rejestr import zbuduj_legatusa

    if bary is None:
        bary = wczytaj_csv(sciezka, interwal=interwal, limit=max_barow)
    if len(bary) <= okno:
        raise ValueError(f"Za mało barów ({len(bary)}) dla okna {okno}")

    symbol = bary[0]["symbol"]
    legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
    budowniczy = BudowniczyWskaznikow()
    suffix = "-AUTO" if auto_rezim else ""
    engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                sesja_id=f"BT-{symbol}-{interwal}-{tryb}{suffix}",
                                max_bars_otwarcia=max_bars_otwarcia)
    # auto_rezim → wstrzyknij Namiestnika (Regime-Aware Gating); inaczej tryb statyczny.
    namiestnik = get_namiestnik() if auto_rezim else None
    dyrygent = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(),
                        engine=engine, budowniczy=budowniczy,
                        min_pewnosc=min_pewnosc, tryb=tryb, namiestnik=namiestnik,
                        min_pewnosc_interwalu=min_pewnosc_interwalu,
                        sl_atr_mult=sl_atr_mult)
    rezim_arg = "AUTO" if auto_rezim else "NORMAL"

    # 💎 W-287 Strażnik Przewagi (opt-in): HALT gdy rolling expectancy < 0,
    # powrót przez 1-pozycyjną sondę bojową. Patrz pretorianie/straznik_przewagi.py.
    sp = None
    if straznik_przewagi:
        from imperium.pretorianie.straznik_przewagi import StraznikPrzewagi
        sp = StraznikPrzewagi(okno=12, bary_halt=96)

    # Pętla uczenia (opt-in): MWU z pamięcią reżimu + atrybucja głosów per pozycja
    mwu = None
    glosy_pozycji: Dict[str, list] = {}
    if ucz_mwu:
        from imperium.biblioteki.hedge_mwu import HedgeMWUzPamieciaRezimu
        mwu = HedgeMWUzPamieciaRezimu(eta=0.3, alpha_share=0.02)

    wejscia = 0
    weta = 0
    krzywa_equity: List[float] = []   # equity po każdym barze (dla bramki W-282)
    for i in range(okno, len(bary)):
        biezacy = bary[i]
        okno_barow = bary[i - okno: i + 1]   # do bieżącej świecy włącznie (bez przyszłości)

        # 1. Aktualizuj otwarte pozycje bieżącą świecą
        zamkniete = engine.przetworz_bar(_bar_data(biezacy))
        krzywa_equity.append(engine.kapital_calkowity)

        # 1b. PĘTLA UCZENIA: rozlicz neurony z ZAMKNIĘTYCH pozycji (bez look-ahead —
        # wynik znany dopiero teraz), potem świeże mnożniki wracają do Legatusa.
        if mwu is not None and zamkniete:
            for w in zamkniete:
                zyskowny = w.kierunek if w.pnl_usdt > 0 else (
                    "SHORT" if w.kierunek == "LONG" else "LONG")
                for neuron_id, kier in glosy_pozycji.pop(w.pozycja_id, []):
                    mwu.zarejestruj_wynik(neuron_id, kier, zyskowny)
            legatus.ustaw_mnozniki_neuronow(mwu.mnozniki())

        # 1c. Strażnik Przewagi (W-287): tyknięcie + rozliczenie zamkniętych;
        # w HALT/sondzie-w-locie pomijamy decyzję (świadoma cisza, Prawo XV).
        if sp is not None:
            sp.tyknij_bar()
            for w in zamkniete:
                sp.zarejestruj_zamkniecie(w.pnl_usdt)
            if not sp.wolno_wejsc():
                continue

        # 2. Decyzja na podstawie okna
        decyzja = dyrygent.cykl(symbol, okno_barow,
                                rezim=rezim_arg, timestamp=biezacy["timestamp"])
        if sp is not None and decyzja.wszedl:
            sp.zarejestruj_wejscie()
        if mwu is not None:
            # pamięć reżimu indeksowana klasyfikacją z TEGO baru (W-285.1)
            mwu.ustaw_rezim(decyzja.rezim)
        if decyzja.wszedl:
            wejscia += 1
            if mwu is not None and decyzja.raport is not None:
                glosy_pozycji[decyzja.pozycja_id] = [
                    (s.neuron_id, s.kierunek) for s in decyzja.raport.sygnaly
                    if s.kierunek in ("LONG", "SHORT")]
        elif decyzja.etap in ("PRETORIANIE_WETO", "LEGATUS_WETO"):
            weta += 1

    # 3. Zamknij pozostałe otwarte po ostatniej cenie
    ostatnia_cena = {symbol: bary[-1]["close"]}
    engine.zamknij_wszystkie(ostatnia_cena, powod="MANUAL")
    krzywa_equity.append(engine.kapital_calkowity)
    # Krzywa equity per bar — wejście bramki walidacji Koloseum (W-282):
    #   from imperium.koloseum.walidacja import etap_pierwszy_koloseum
    #   werdykt = etap_pierwszy_koloseum(engine.krzywa_equity, engine.podsumowanie())
    engine.krzywa_equity = krzywa_equity
    # Diagnostyka atrybucji (Faza B): raport MWU per neuron dostępny po przebiegu
    engine.mwu = mwu

    logger.info(f"[Backtest] {symbol} {interwal}: {len(bary)} barów, "
                f"{wejscia} wejść, {weta} wet Pretorianów")
    return engine


def backtest_portfel(
    pliki: "Dict[str, str]",
    interwal: str,
    okno: int = 250,
    kapital_startowy: float = 10_000.0,
    min_pewnosc: float = 0.55,
    tryb: str = "agregat",
    auto_rezim: bool = True,
    dd_control: bool = True,
    tryb_lupiezcy: bool = False,
    ster_korelacyjny: bool = False,
    rygiel_ryzyka: bool = False,
    dd_reduced: float = 0.07,
    dd_halt: float = 0.13,
    bary_per: "Optional[Dict[str, List[Dict[str, Any]]]]" = None,
) -> PaperTradingEngine:
    """
    💎 W-290 SILNIK PORTFELOWY — koszyk N par w JEDNEJ sesji, wspólny kapitał.

    Realizuje ROADMAP Faza 3 "Kostka Rubika": rój gra koszykiem, nie jedną parą.
    Pomiar 2026-06-11 dowiódł, że portfel 5 par (korelacja ~0) przechodzi Etap I
    (Sharpe 1.24), choć żadna para sama nie (Sharpe<1).

    pliki: {symbol: ścieżka_csv}. interwal wspólny.
    Mechanika (Prawo I — bez look-ahead):
      • Jeden wspólny PaperTradingEngine (kapitał dzielony; max N pozycji naraz).
      • Per-para Dyrygent współdzielący silnik; sizing wg kapital/N (równe wagi).
      • Chronologiczna unia osi czasu: każdy bar (ts, symbol) przetwarzany w
        kolejności czasu — najpierw aktualizacja otwartych, potem decyzja roju
        na oknie barów DANEJ pary do bieżącej świecy włącznie.
    Zwraca silnik z `krzywa_equity` (equity po każdym tyknięciu) — gotowe pod
    `etap_pierwszy_koloseum`.
    """
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.rejestr import zbuduj_legatusa

    if bary_per is None:
        bary_per = {sym: wczytaj_csv(sc, interwal=interwal)
                    for sym, sc in pliki.items()}
    bary_per = {s: b for s, b in bary_per.items() if len(b) > okno}
    if not bary_per:
        raise ValueError("Brak par z wystarczającą historią")
    n = len(bary_per)

    engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                sesja_id=f"BT-PORTFEL-{n}x-{interwal}",
                                max_otwartych=n)   # każda para max 1 pozycja
    budowniczy = BudowniczyWskaznikow()
    namiestnik = get_namiestnik() if auto_rezim else None
    rezim_arg = "AUTO" if auto_rezim else "NORMAL"
    budzet_pary = kapital_startowy / n   # równe wagi (Markowitz)

    # RADAR RYNKU (W-292, rozwój W-291): wielowymiarowy kontekst lidera+koszyka
    # (BTC_TREND, BTC_DOMINANCJA, PRZEPLYW_KAPITALU, STRES_KORELACJI) wstrzykiwany
    # do KAŻDEJ pary. Liczony przyczynowo z barów DO bieżącej świecy (Prawo I).
    import bisect as _bs
    from imperium.legiony.radar_rynku import (RadarRynku, frakcja_korelacyjna,
                                              rezim_risk_off)
    _radar = RadarRynku()
    _RADAR_OGON = 200   # ogon serii wystarczający dla wszystkich okien radaru
    _btc_sym = next((s for s in bary_per if s.upper().startswith("BTC")), None)
    # Precompute per-symbol serie (close/vol/ts) raz — tnie się bisectem co tyk.
    _close = {s: [float(x["close"]) for x in b] for s, b in bary_per.items()}
    _vol = {s: [float(x.get("volume", 0.0)) for x in b] for s, b in bary_per.items()}
    _ts_arr = {s: [int(x["timestamp"]) for x in b] for s, b in bary_per.items()}

    # DD-control portfela (W-290/293): JEDEN wspólny BezpiecznikKrzywejKapitalu na
    # poziomie koszyka. Progi PORTFELOWE ciaśniejsze niż single-para W-062 (20%):
    # REDUCED@7% → ×0.5 sizingu, HALT@13% → blokada wejść. POWÓD (polityka ryzyka,
    # nie curve-fit): 5 jednoczesnych skorelowanych pozycji wymaga ciaśniejszej
    # kontroli equity niż jedna para. POMIAR 2026-06-11 (Prawo I): HALT 20%→13%
    # przeniósł portfel przez Etap I (MaxDD 20.2%→<15%, ok=False→True) i PODNIÓSŁ
    # WSZYSTKO (PnL +39477→+42369, Sharpe 1.41→1.46, PF 2.19→2.67) — wcześniejsze
    # ucięcie krwawienia zachowuje kapitał do składania. DSR=1.0 (edge realny).
    breaker = None
    if dd_control:
        breaker = BezpiecznikKrzywejKapitalu(prog_dd_reduced=dd_reduced,
                                             prog_dd_halt=dd_halt)

    dyrygenci = {}
    for sym in bary_per:
        legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
        d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                     budowniczy=budowniczy, min_pewnosc=min_pewnosc, tryb=tryb,
                     namiestnik=namiestnik, breaker_krzywej=False)  # breaker wspólny
        d.kapital_sizing = budzet_pary
        # 🗡️ PRAEDA (W-291): tryb łupieżczy — auto-skalowana agresja w POTWIERDZONYCH
        # okazjach (confluence). Aktywny tylko gdy DD normalny (bezpieczeństwo > chciwość).
        if tryb_lupiezcy:
            from imperium.pretorianie.praeda import Okazjon
            d.okazjon = Okazjon()
        dyrygenci[sym] = d

    # Chronologiczna oś: (timestamp, symbol, indeks_baru) — tylko bary po oknie.
    os_czasu = []
    for sym, bary in bary_per.items():
        for i in range(okno, len(bary)):
            os_czasu.append((int(bary[i]["timestamp"]), sym, i))
    os_czasu.sort(key=lambda x: x[0])

    # Equity zapisywane per KALENDARZOWY DZIEŃ (ostatnia wartość w dniu), NIE per
    # zdarzenie: przy N parach ~N zdarzeń/dzień fałszowałoby annualizację Sharpe
    # (√365 zakłada 1 punkt/dzień). Prawo I — uczciwy współczynnik czasu.
    _DZ = 86_400_000
    equity_dnia: "Dict[int, float]" = {}
    for ts, sym, i in os_czasu:
        bary = bary_per[sym]
        engine.przetworz_bar(_bar_data(bary[i]))
        eq = engine.kapital_calkowity
        equity_dnia[ts // _DZ] = eq
        frakcja_breaker = 1.0
        if breaker is not None:
            breaker.aktualizuj(eq)
            if breaker.halt:
                continue   # blokada nowych wejść (świadoma cisza, Prawo XV)
            frakcja_breaker = breaker.frakcja_pozycji()
        # PRAEDA: chciwość dozwolona TYLKO gdy bezpiecznik w stanie NORMAL (DD < próg).
        if tryb_lupiezcy:
            dyrygenci[sym].praeda_dd_normal = (breaker is None or breaker.stan == "NORMAL")
        # RADAR RYNKU: skan koszyka do ts (przyczynowo, bez look-ahead). Każda seria
        # ucięta bisectem do świec ≤ ts — żadnej przyszłości w kontekście.
        frakcja_stres = 1.0
        if _btc_sym is not None:
            # Tylko OGON serii (≤_RADAR_OGON barów) — radar patrzy na ostatnie ~90.
            # Ucięcie z dołu czyni skan O(1)/tyk zamiast O(n) (koniec kwadratu).
            jb = _bs.bisect_right(_ts_arr[_btc_sym], ts)
            btc_slice = _close[_btc_sym][max(0, jb - _RADAR_OGON):jb]
            alty_close, alty_vol = {}, {}
            for s in bary_per:
                if s == _btc_sym:
                    continue
                k = _bs.bisect_right(_ts_arr[s], ts)
                if k >= 1:
                    lo = max(0, k - _RADAR_OGON)
                    alty_close[s] = _close[s][lo:k]
                    alty_vol[s] = _vol[s][lo:k]
            stan = _radar.skanuj(btc_slice, alty_close, alty_vol)
            dyrygenci[sym].kontekst_dodatkowy = stan.jako_wskazniki()
            # 🛡️ STER KORELACYJNY (W-292, OPT-IN) — czynnik 1/√(1+(N-1)ρ) z teorii portfela.
            # POMIAR 2026-06-11 (Prawo I): na trwale skorelowanym koszyku krypto (ρ≈0.8
            # zawsze) działa jak ~stały haircut ×0.5 → tnie PnL o połowę, a MaxDD% (ratio,
            # niezmienny pod skalowaniem) zostaje 20%. Dlatego DOMYŚLNIE OFF — nie blokujemy
            # potencjału (Prawo XV). Zostaje jako opcja dla koszyków zdekorelowanych.
            if ster_korelacyjny:
                frakcja_stres = frakcja_korelacyjna(n, stan.stres_korelacji)
            # 🚦 RYGIEL RYZYKA (W-293): stanowy de-risk — w reżimie risk-off (kaskada
            # ∧ odpływ ∧ BTC↓) wstrzymaj NOWE wejścia, by ominąć zły okres (atakuje
            # MaxDD u źródła, w przeciwieństwie do równomiernego cięcia z W-292).
            if rygiel_ryzyka:
                risk_off, _ = rezim_risk_off(stan)
                if risk_off:
                    continue   # świadoma cisza (Prawo XV) — nie wchodzimy w lawinę
        # Sizing par: równy budżet × frakcja DD-control × ster korelacyjny (świeżo co tyk).
        dyrygenci[sym].kapital_sizing = budzet_pary * frakcja_breaker * frakcja_stres
        okno_barow = bary[i - okno: i + 1]
        dyrygenci[sym].cykl(sym, okno_barow, rezim=rezim_arg, timestamp=ts)

    # Domknij otwarte po ostatniej cenie każdej pary
    ostatnie = {sym: bary_per[sym][-1]["close"] for sym in bary_per}
    engine.zamknij_wszystkie(ostatnie, powod="MANUAL")
    if os_czasu:
        equity_dnia[os_czasu[-1][0] // _DZ] = engine.kapital_calkowity
    engine.krzywa_equity = [equity_dnia[d] for d in sorted(equity_dnia)]
    return engine


def backtest_arena(
    sciezka: str,
    interwal: str,
    okno: int = 250,
    kapital_startowy: float = 10_000.0,
    max_barow: Optional[int] = None,
    min_pewnosc: float = 0.55,
    tryb: str = "agregat",
    tp_pct: float = 0.02,
    sl_pct: float = 0.01,
    max_bary_bariery: int = 20,
    bary: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[PaperTradingEngine, "RaportAreny"]:
    """
    Backtest z Areną Trzech Bram (W-035): każdy sygnał dostaje obiektywną etykietę
    potrójnej bariery (TP/SL/CZAS), co pozwala Igrzyskom uczciwie ocenić neurony.

    Parametry Arena:
      tp_pct            frakcja take-profit od ceny wejścia (domyślnie 2%)
      sl_pct            frakcja stop-loss od ceny wejścia (domyślnie 1%)
      max_bary_bariery  bariera czasowa (domyślnie 20 barów)

    Zwraca (engine, raport_areny). RaportAreny zawiera:
      - win_rate_tp, sygnaly_tp/sl/czas
      - kontryb_neuronow: {klucz: contribution} dla Igrzysk

    Uzasadnienie "look-ahead" dla bariery: w backteście bary przyszłe są znane.
    Bariera służy TYLKO do etykietowania historycznego — nie wchodzi do logiki handlu.
    Deklarujemy to wprost (Prawo I — Zero Halucynacji).
    """
    from imperium.biblioteki.arena_trzech_bram import oznacz_bariera, RaportAreny
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.rejestr import zbuduj_legatusa

    if bary is None:
        bary = wczytaj_csv(sciezka, interwal=interwal, limit=max_barow)
    if len(bary) <= okno:
        raise ValueError(f"Za mało barów ({len(bary)}) dla okna {okno}")

    symbol = bary[0]["symbol"]
    legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
    budowniczy = BudowniczyWskaznikow()
    engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                sesja_id=f"BT-ARENA-{symbol}-{interwal}-{tryb}")
    dyrygent = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(),
                        engine=engine, budowniczy=budowniczy,
                        min_pewnosc=min_pewnosc, tryb=tryb)
    raport = RaportAreny()

    for i in range(okno, len(bary)):
        biezacy = bary[i]
        okno_barow = bary[i - okno: i + 1]

        engine.przetworz_bar(_bar_data(biezacy))

        decyzja = dyrygent.cykl(symbol, okno_barow,
                                rezim="NORMAL", timestamp=biezacy["timestamp"])

        if decyzja.wszedl and decyzja.kierunek in ("LONG", "SHORT"):
            cena_wejscia = biezacy["close"]
            bary_przyszle = bary[i + 1: i + 1 + max_bary_bariery]
            wynik = oznacz_bariera(
                kierunek=decyzja.kierunek,
                cena_wejscia=cena_wejscia,
                bary_przyszle=bary_przyszle,
                tp_pct=tp_pct,
                sl_pct=sl_pct,
                max_bary=max_bary_bariery,
            )
            sygnaly_json = None
            if hasattr(decyzja, "sygnaly_json"):
                sygnaly_json = decyzja.sygnaly_json
            raport.zarejestruj(wynik, sygnaly_json)

    ostatnia_cena = {symbol: bary[-1]["close"]}
    engine.zamknij_wszystkie(ostatnia_cena, powod="MANUAL")
    return engine, raport


def porownaj_tryby(sciezka: str, interwal: str, max_barow: Optional[int] = None,
                   tryby=("agregat", "filtr", "strategia")) -> Dict[str, Any]:
    """
    Przejeżdża ten sam zestaw barów w każdym trybie i zwraca tabelę porównawczą.
    Prawo XVI: decyzja o roli strategii podjęta na pomiarze, nie na opinii.
    """
    bary = wczytaj_csv(sciezka, interwal=interwal, limit=max_barow)
    symbol = bary[0]["symbol"]
    wyniki = {}
    for tryb in tryby:
        eng = backtest(sciezka, interwal, max_barow=max_barow, tryb=tryb, bary=bary)
        st = eng.podsumowanie()
        st.oblicz(eng.historia_zamkniec)
        wyniki[tryb] = st

    # Tabela
    print(f"\n{'═'*78}")
    print(f"  📊 PORÓWNANIE TRYBÓW — {symbol} {interwal} ({len(bary)} barów)")
    print(f"{'═'*78}")
    print(f"  {'Tryb':<12}{'PnL %':>10}{'Trades':>9}{'WinRate':>10}{'PF':>8}{'MaxDD':>9}")
    print(f"  {'-'*70}")
    for tryb, st in wyniki.items():
        pnl_pct = (st.kapital_koncowy / st.kapital_startowy - 1) * 100
        print(f"  {tryb:<12}{pnl_pct:>+9.2f}%{st.total_trades:>9}"
              f"{st.win_rate:>9.1%}{st.profit_factor:>8.2f}{st.max_drawdown_pct:>8.1%}")
    print(f"{'═'*78}\n")
    return wyniki


def main():
    logging.basicConfig(level=logging.WARNING,
                        format="%(asctime)s | %(levelname)s | %(message)s")
    logging.getLogger("Rój").setLevel(logging.ERROR)

    if len(sys.argv) < 3:
        print("Użycie: python -m imperium.koloseum.backtest <plik.csv> <interwal> [max_barow] [--porownaj|tryb]")
        sys.exit(1)

    sciezka = sys.argv[1]
    interwal = sys.argv[2]
    max_barow = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None

    if "--porownaj" in sys.argv:
        porownaj_tryby(sciezka, interwal, max_barow=max_barow)
        return

    tryb = "agregat"
    for t in ("agregat", "filtr", "strategia"):
        if t in sys.argv:
            tryb = t
    auto = "--auto" in sys.argv
    ucz = "--ucz" in sys.argv
    engine = backtest(sciezka, interwal, max_barow=max_barow, tryb=tryb,
                      auto_rezim=auto, ucz_mwu=ucz)
    engine.drukuj_raport()

    # Werdykt Etapu I Koloseum (ROADMAP Arena × W-282) — każdy backtest CLI
    # kończy się jawnym TAK/NIE na awans do paper tradingu (Prawo I).
    from imperium.koloseum.walidacja import etap_pierwszy_koloseum
    st = engine.podsumowanie()
    st.oblicz(engine.historia_zamkniec)
    w = etap_pierwszy_koloseum(engine.krzywa_equity, st, interwal=interwal)
    if w["ok"]:
        print(f"\n🏟️ ETAP I KOLOSEUM: ✅ ZALICZONY (Sharpe_r={w['sharpe_roczny']}, "
              f"DSR={w['dsr']}) — strategia może iść do Etapu II (paper).")
    else:
        print(f"\n🏟️ ETAP I KOLOSEUM: ⛔ ODRZUCONY — {w['powod']} "
              f"(Sharpe_r={w['sharpe_roczny']}, DSR={w['dsr']})")


if __name__ == "__main__":
    main()
