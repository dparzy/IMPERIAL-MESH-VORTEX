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
from imperium.koloseum.skaner_okazji import SkanerOkazji
from imperium.pretorianie.sizing_przekonania import SizingPrzekonania
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
    mtf_konfluencja: bool = False,
    mtf_weto_przeciwtrend: bool = False,
    mierz_ic: bool = False,
    kalibruj_prog: bool = False,
    zbieraj_sygnaly: bool = False,
    zbieraj_pelne_sygnaly: bool = False,
    wazenie_ic: bool = False,
    wagi_ic: "Optional[Dict[str, float]]" = None,
    wagi_ic_prog: float = 0.0,
    wagi_ic_skaluj: bool = True,
    ucz_mwu_strategii: bool = False,
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
    mtf_konfluencja:        W-384 (opt-in, domyślnie False → zero zmiany zachowania) —
                brama konfluencji wyższych TF na poziomie roju (mnoznik pewności/sizingu).
    mtf_weto_przeciwtrend:  W-384 (opt-in) — twarde weto wejść przeciw wyższym TF.
    """
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.rejestr import zbuduj_legatusa

    if bary is None:
        bary = wczytaj_csv(sciezka, interwal=interwal, limit=max_barow)
    if len(bary) <= okno:
        raise ValueError(f"Za mało barów ({len(bary)}) dla okna {okno}")

    symbol = bary[0]["symbol"]
    legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True)
    # W-361 A/B na P&L (opt-in, domyślnie OFF → zero zmiany zachowania). Wagi IC liczone
    # WYŁĄCZNIE na TRAIN (poza tym backtestem) i podane z zewnątrz — zero look-ahead.
    if wagi_ic:
        legatus.ustaw_wagi_ic(wagi_ic, wlacz=wazenie_ic,
                              prog_ic=wagi_ic_prog, skaluj_ic=wagi_ic_skaluj)
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
    # W-384 Konfluencja MTF (opt-in, A/B) — domyślnie False, zero zmiany zachowania.
    dyrygent.mtf_konfluencja = mtf_konfluencja
    dyrygent.mtf_weto_przeciwtrend = mtf_weto_przeciwtrend
    rezim_arg = "AUTO" if auto_rezim else "NORMAL"

    # ML-36 Bramka konformalna (opt-in, A/B) — podnosi próg pewności po serii strat.
    if kalibruj_prog:
        from imperium.legiony.kalibrator_konformalny import BramkaPewnosciKonformalna
        dyrygent.bramka_kalibr = BramkaPewnosciKonformalna(cel_trafnosci=min_pewnosc)

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

    # W-362 strategy-MWU (opt-in): online MWU keyed strategy_id, uczony ZREALIZOWANYM P&L
    # zamkniętych trade'ów (atrybucja: top-strategia przy wejściu). Mnożniki wracają do
    # Legatusa → dobór strategii waży się realnym zyskiem (naprawa luki z ANALIZA_AUTODOBOR).
    mwu_strat = None
    strat_pozycji: Dict[str, str] = {}
    if ucz_mwu_strategii:
        from imperium.biblioteki.hedge_mwu import HedgeMWU
        mwu_strat = HedgeMWU(eta=0.3)

    # W-385 Pomiar IC roju (opt-in, Prawo XVI): Spearman(sygnał_neuronu_t, zwrot_{t+h}).
    # Mierzy realną przewagę predykcyjną KAŻDEGO neuronu (w tym NEWS-01..04, gdy mają feed).
    # Zero look-ahead: sygnał_t paruje z PRZYSZŁYM zwrotem; rejestr po decyzji.
    kol_ic = None
    if mierz_ic:
        from imperium.legiony.metryki_ic import KolektorIC
        kol_ic = KolektorIC()

    # W-355 Kolektor sygnałów dla Feature Importance (opt-in): per bar {neuron: kierunek}
    # + etykieta forward = znak zwrotu NASTĘPNEGO baru (bez look-ahead w decyzji — etykieta
    # tylko do POMIARU ważności po fakcie). Zasila raport_waznosci() (MDA/SFI, López de Prado).
    hist_sygnalow: List[Dict[str, str]] = []
    hist_wynikow: List[int] = []
    # W-361 A/B na żywo: pełne SygnalNeuronu per bar (kierunek+pewnosc_finalna+waga) —
    # potrzebne do replayu przez realny Legatus._agreguj OFF vs ON. Opt-in (pamięciożerne).
    hist_pelne: list = []

    wejscia = 0
    weta = 0
    krzywa_equity: List[float] = []   # equity po każdym barze (dla bramki W-282)
    for i in range(okno, len(bary)):
        biezacy = bary[i]
        okno_barow = bary[i - okno: i + 1]   # do bieżącej świecy włącznie (bez przyszłości)

        # 1. Aktualizuj otwarte pozycje bieżącą świecą
        zamkniete = engine.przetworz_bar(_bar_data(biezacy))
        krzywa_equity.append(engine.kapital_calkowity)

        # ML-36: karm bramkę konformalną wynikiem zamknięć (bez look-ahead — znany teraz).
        if dyrygent.bramka_kalibr is not None and zamkniete:
            for w in zamkniete:
                dyrygent.bramka_kalibr.zaktualizuj(w.pnl_usdt > 0)

        # 1b. PĘTLA UCZENIA: rozlicz neurony z ZAMKNIĘTYCH pozycji (bez look-ahead —
        # wynik znany dopiero teraz), potem świeże mnożniki wracają do Legatusa.
        if mwu is not None and zamkniete:
            for w in zamkniete:
                zyskowny = w.kierunek if w.pnl_usdt > 0 else (
                    "SHORT" if w.kierunek == "LONG" else "LONG")
                for neuron_id, kier in glosy_pozycji.pop(w.pozycja_id, []):
                    mwu.zarejestruj_wynik(neuron_id, kier, zyskowny)
            legatus.ustaw_mnozniki_neuronow(mwu.mnozniki())

        # 1b'. PĘTLA UCZENIA STRATEGII (W-362): rozlicz strategię, która napędziła wejście
        # (atrybucja top-1 przy otwarciu) ZREALIZOWANYM P&L; strata binarna 0=zysk/1=strata.
        if mwu_strat is not None and zamkniete:
            for w in zamkniete:
                sid = strat_pozycji.pop(w.pozycja_id, None)
                if sid is not None:
                    mwu_strat.aktualizuj(sid, 0.0 if w.pnl_usdt > 0 else 1.0)
            legatus.ustaw_wagi_strategii(mwu_strat.mnozniki())

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
            # W-362: zapamiętaj strategię, która napędziła to wejście (top-1 dopasowana)
            if (mwu_strat is not None and decyzja.raport is not None
                    and decyzja.raport.strategie_dopasowane):
                strat_pozycji[decyzja.pozycja_id] = \
                    decyzja.raport.strategie_dopasowane[0].strategia.id
        elif decyzja.etap in ("PRETORIANIE_WETO", "LEGATUS_WETO"):
            weta += 1

        # Pomiar IC (W-385): sygnał_t (kierunek×pewność) + zwrot wejściowy bieżącego baru.
        # Kolektor paruje sygnał_t z zwrotem_{t+h} (przyszłym) — bez look-ahead.
        if kol_ic is not None:
            # Sygnał tylko gdy jest raport; ZWROT rejestrujemy KAŻDY bar — inaczej
            # brakujący bar (weto/HALT bez raportu) rozjeżdża horyzonty forward-zwrotu.
            if decyzja.raport is not None:
                kol_ic.rejestruj_sygnal({
                    s.neuron_id: (s.pewnosc if s.kierunek == "LONG"
                                  else -s.pewnosc if s.kierunek == "SHORT" else 0.0)
                    for s in decyzja.raport.sygnaly})
            poprz = bary[i - 1]["close"]
            kol_ic.rejestruj_zwrot(biezacy["close"] / poprz - 1 if poprz else 0.0)

        # W-355: zbierz sygnały + etykietę forward (znak zwrotu następnego baru).
        if zbieraj_sygnaly and decyzja.raport is not None and i < len(bary) - 1:
            hist_sygnalow.append({s.neuron_id: s.kierunek for s in decyzja.raport.sygnaly})
            nast = bary[i + 1]["close"]
            hist_wynikow.append(1 if nast > biezacy["close"] else -1)
            # Pełne sygnały RÓWNOLEGLE do hist_wynikow (te same bary) — replay A/B (W-361).
            if zbieraj_pelne_sygnaly:
                hist_pelne.append(list(decyzja.raport.sygnaly))

    if zbieraj_sygnaly:
        engine.historia_sygnalow = hist_sygnalow
        engine.historia_wynikow = hist_wynikow
        if zbieraj_pelne_sygnaly:
            engine.historia_pelnych_sygnalow = hist_pelne

    # Pomiar IC (W-385): dołącz raport do silnika (Prawo XVI — przewaga mierzona).
    if kol_ic is not None:
        engine.ic_srednie = kol_ic.ic_srednie()
        engine.ic_warunkowy = kol_ic.ic_srednie(tylko_glosy=True)  # tylko bary z głosem
        engine.ic_pelne = kol_ic.ic()
        engine.ic_kolektor = kol_ic

    # 3. Zamknij pozostałe otwarte po ostatniej cenie
    ostatnia_cena = {symbol: bary[-1]["close"]}
    zamkniete_koncowe = engine.zamknij_wszystkie(ostatnia_cena, powod="MANUAL")
    # W-362 (Cubic P3): pozycje domknięte MANUAL na ostatnim barze też rozliczają strategy-MWU —
    # inaczej learner gubi ostatnie zrealizowane trade'y (te same reguły atrybucji co w pętli).
    if mwu_strat is not None and zamkniete_koncowe:
        for w in zamkniete_koncowe:
            sid = strat_pozycji.pop(w.pozycja_id, None)
            if sid is not None:
                mwu_strat.aktualizuj(sid, 0.0 if w.pnl_usdt > 0 else 1.0)
        legatus.ustaw_wagi_strategii(mwu_strat.mnozniki())
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


def wagi_inwerse_vol(
    bary_per: "Dict[str, List[Dict[str, Any]]]",
    okno_vol: int = 60,
) -> "Dict[str, float]":
    """
    Opcja B — volatility-adjusted allocation: wagi odwrotnie proporcjonalne do
    ruchomej zmienności (σ dziennych zwrotów close z pierwszych `okno_vol` barów).

    Normalizowane do sumy 1.0. Para z σ=0 dostaje wagę równą innym.
    Cel: redukuje dominację wysokozmiennych par (DOGE 4× bardziej zmienny niż BTC),
    poprawia Sharpe portfela (więcej risk-parity, mniej luck-of-symbol).

    Prawo I: liczy tylko z dostępnych barów historycznych — bez look-ahead.
    """
    import math
    sigmy = {}
    for sym, bary in bary_per.items():
        # Pierwsze okno_vol barów — to okres warmup PRZED startem handlu,
        # gwarantuje kauzalność (Prawo I: brak look-ahead).
        zamkniecia = [float(b["close"]) for b in bary[:okno_vol] if b.get("close")]
        if len(zamkniecia) < 10:
            sigmy[sym] = 1.0
            continue
        zwroty = [zamkniecia[i] / zamkniecia[i - 1] - 1 for i in range(1, len(zamkniecia))]
        mean = sum(zwroty) / len(zwroty)
        wariancja = sum((r - mean) ** 2 for r in zwroty) / max(1, len(zwroty) - 1)
        sigmy[sym] = math.sqrt(wariancja) if wariancja > 0 else 1.0

    inv = {sym: 1.0 / s for sym, s in sigmy.items()}
    suma = sum(inv.values())
    return {sym: round(v / suma, 6) for sym, v in inv.items()}


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
    wagi: "Optional[Dict[str, float]]" = None,
    # W-299 Synapsy Reżimowe — opt-in, domyślnie False (zero kosztu na backteście
    # gdzie nowy model ma mało historii). True → każdy symbol uczy własny graf par.
    synapsy_rezimowe: bool = False,
    # W-303 HedgeMWU — online multiplicative weights update (W-049). True → Legatus
    # każdego symbolu ma własny MWU uczący wagi neuronów strumieniowo po trade'cie.
    mwu_learning: bool = False,
    # W-307 Igrzyska — batch ranking (accuracy/stability/ranga). True → per-symbol
    # kumulatywne statystyki neuronów. Gdy oba mwu+igrzyska: mnożniki łączone (×).
    igrzyska_learning: bool = False,
    # W-309 KsięgaWad — prewencyjny filtr wad setupu (rezim/interwal). True → per-symbol
    # księga uczy się z zamknięć i ostrzega/wetuje powtarzalnie stratne setupy.
    ksiega_wad: bool = False,
    # W-314 Filtr Asymetrii Reżimu — weto na rynku bocznym (ADX niski) i dla słabych
    # wejść kontr-trendowych. Czysty OHLCV (CLOSE/EMA_200/ADX_14). True → per-symbol.
    filtr_asymetrii: bool = False,
    # W-317 TRYB NAJLEPSZE — Skaner Okazji jako brama selekcji: zamiast „każda para
    # gra", w każdym tyku rankujemy koszyk i wpuszczamy do wejścia TYLKO TOP-N
    # najmocniejszych okazji. Exity działają niezależnie. Domyślnie OFF (zero regresji).
    tryb_skaner: bool = False,
    skaner_top_n: int = 3,
    skaner_min_adx: float = 20.0,
    skaner_min_ts: float = 0.0,      # W-324: brama TS (0=wył.); np. 0.01 = ≥1% ruchu
    # W-318 Sizing Przekonania — w trybie skanera mnoży budżet pozycji przez siłę
    # okazji (mocniejsza okazja = większa stawka). Bez tego sama selekcja przycina
    # gruby ogon. Domyślnie OFF.
    sizing_przekonania: bool = False,
    # W-319 Compounding (pula łupów) — budżet sizingu liczony od BIEŻĄCEGO equity,
    # nie od kapitału startowego. Zysk reinwestowany w większe pozycje (wzrost
    # geometryczny). Domyślnie OFF (stały sizing = liniowy wzrost, łatwiejsza ocena edge).
    compounding: bool = False,
    # W-325 GUBERNATOR — homeostatyczny sterownik globalnej ekspozycji portfela.
    # Po skanerze i bezpieczniku DD dokłada JEDEN globalny mnożnik [floor,ceiling]
    # z agregatu koszyka (pewność top-okazji × wyrazistość lidera × stan DD). Płynna
    # histereza postaw. Domyślnie OFF (neutralny ≈1.0 w stanie bazowym, Prawo XV).
    gubernator: bool = False,
    # W-323 Profil Stylu — gdy podany (SCALP/SWING/INVEST), każdy Legatus dostaje
    # DEDYKOWANY zestaw neuronów (neurony_dla_trybu), nie pełne 70. None = pełny rój.
    styl: "Optional[str]" = None,
    # W-351 Trailing Stop — blokuje zysk po ruchu korzystnym (MFE było liczone, ale
    # nieużywane do wyjścia → utrata potencjału, Prawo XV). Domyślnie OFF (zero regresji).
    trailing: bool = False,
    # W-cache: prekalkuluj wskaźniki dla wszystkich par równolegle przed pętlą.
    # Eliminuje redundantne wywołania TA-Lib (zysk ~5-8×). n_jobs=None → auto cpu_count.
    cache_wskaznikow: bool = False,
    cache_n_jobs: Optional[int] = None,
    # W-sentyment: historyczny funding/OI/L-S do POMIARU PSY-01/02/04 w backteście
    # (Prawo XVI). {sym: {ts_baru: {FUNDING_RATE, OPEN_INTEREST, OPEN_INTEREST_PREV,
    # LONG_SHORT_RATIO}}}. Buduj przez sentyment_historyczny.forward_fill_na_bary.
    # None = PSY abstynują (jak dotąd, zero regresji).
    sentyment_per: "Optional[Dict[str, Dict[int, Dict[str, Any]]]]" = None,
) -> PaperTradingEngine:
    """
    💎 W-290 SILNIK PORTFELOWY — koszyk N par w JEDNEJ sesji, wspólny kapitał.

    Realizuje ROADMAP Faza 3 "Kostka Rubika": rój gra koszykiem, nie jedną parą.
    Pomiar 2026-06-11 dowiódł, że portfel 5 par przechodzi Etap I (Sharpe>1.0).

    pliki: {symbol: ścieżka_csv}. interwal wspólny.
    wagi:  opcjonalny dict {symbol: waga} (suma 1.0) — alokacja kapitału per para.
           None = równe wagi (1/N). Opcja B: wagi_inwerse_vol() dla risk-parity.

    Mechanika (Prawo I — bez look-ahead):
      • Jeden wspólny PaperTradingEngine (kapitał dzielony; max N pozycji naraz).
      • Per-para Dyrygent współdzielący silnik; sizing wg kapital × waga_pary.
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

    # Opcja B: wagi portfela (equal-weight lub zewnętrzne/vol-adjusted)
    if wagi is None:
        wagi_akt = {sym: 1.0 / n for sym in bary_per}
    else:
        suma_wag = sum(wagi.get(sym, 1.0 / n) for sym in bary_per)
        wagi_akt = {sym: wagi.get(sym, 1.0 / n) / suma_wag for sym in bary_per}

    engine = PaperTradingEngine(kapital_startowy=kapital_startowy,
                                sesja_id=f"BT-PORTFEL-{n}x-{interwal}",
                                max_otwartych=n,   # każda para max 1 pozycja
                                trailing=trailing)
    budowniczy = BudowniczyWskaznikow()
    namiestnik = get_namiestnik() if auto_rezim else None
    rezim_arg = "AUTO" if auto_rezim else "NORMAL"

    # RADAR RYNKU (W-292, rozwój W-291): wielowymiarowy kontekst lidera+koszyka
    # (BTC_TREND, BTC_DOMINANCJA, PRZEPLYW_KAPITALU, STRES_KORELACJI) wstrzykiwany
    # do KAŻDEJ pary. Liczony przyczynowo z barów DO bieżącej świecy (Prawo I).
    import bisect as _bs
    from imperium.legiony.radar_rynku import (RadarRynku, frakcja_korelacyjna,
                                              rezim_risk_off)
    from imperium.legiony.przekroj_koszyka import cross_sectional_rs as _cross_sectional_rs
    _radar = RadarRynku()
    _RADAR_OGON = 200   # ogon serii wystarczający dla wszystkich okien radaru
    _RS_LOOKBACK = 24   # okno zwrotu dla cross-sectional RS (~4 dni na 4h)
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
        legatus = zbuduj_legatusa(min_neuronow=5, min_przewaga=0.55, aktywuj_smc=True, styl=styl)
        d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                     budowniczy=budowniczy, min_pewnosc=min_pewnosc, tryb=tryb,
                     namiestnik=namiestnik, breaker_krzywej=False,  # breaker wspólny
                     filtr_asymetrii=filtr_asymetrii)
        d.kapital_sizing = kapital_startowy * wagi_akt[sym]
        # 🗡️ PRAEDA (W-291): tryb łupieżczy — auto-skalowana agresja w POTWIERDZONYCH
        # okazjach (confluence). Aktywny tylko gdy DD normalny (bezpieczeństwo > chciwość).
        if tryb_lupiezcy:
            from imperium.pretorianie.praeda import Okazjon
            d.okazjon = Okazjon()
        # W-299 Synapsy Reżimowe: per-symbol graf koalicji par neuronów warunkowany
        # reżimem × dekorelacja. Uczy się przez cały backtest — para dobrych duetów
        # w TREND_STRONG kumuluje synaps, pary która systematycznie mylą = redukcja.
        if synapsy_rezimowe:
            from imperium.biblioteki.synapsy_rezimowe import SynapsyRezimowe
            d.legatus.synapsy = SynapsyRezimowe()
        if mwu_learning:
            from imperium.biblioteki.hedge_mwu import HedgeMWU
            d.legatus.mwu = HedgeMWU()
        if igrzyska_learning:
            from imperium.biblioteki.igrzyska import Igrzyska as _Igrzyska
            d._igrzyska = _Igrzyska()
        if ksiega_wad:
            from imperium.cesarz.ksiega_wad import KsiegaWad as _KsiegaWad
            d.ksiega_wad = _KsiegaWad()
        dyrygenci[sym] = d

    # W-cache: prekalkuluj wskaźniki dla wszystkich par przed pętlą.
    # Każdy symbol obliczany raz (równolegle) → pętla robi tylko lookup dict.
    _wsk_cache: "Optional[Dict[str, Dict[int, Dict]]]" = None
    if cache_wskaznikow:
        from imperium.legiony.budowniczy_wskaznikow import prekalkuluj_portfel
        logger.info("[Portfel] Prekalkuluję wskaźniki (cache_wskaznikow=True, n_jobs=%s)...", cache_n_jobs)
        _wsk_cache = prekalkuluj_portfel(bary_per, okno=okno, n_jobs=cache_n_jobs)
        # Wstrzyknij jako wskazniki_provider do każdego Dyrygenta
        for sym, d in dyrygenci.items():
            _sym_cache = _wsk_cache[sym]
            d.wskazniki_provider = lambda bary, _c=_sym_cache: _c.get(
                int(bary[-1]["timestamp"]) if bary and bary[-1].get("timestamp") is not None else -1, {}
            )
        logger.info("[Portfel] Cache gotowy — %d symboli.", len(_wsk_cache))

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

    # W-317 TRYB NAJLEPSZE: skaner okazji + cache snapshotów wskaźników per symbol.
    # Snapshot symbolu aktualizujemy tylko na JEGO tyku (świeży bar) → ranking O(N)/tyk.
    skaner = SkanerOkazji(min_adx=skaner_min_adx, min_bezwzgledny_ts=skaner_min_ts) if tryb_skaner else None
    sizer = SizingPrzekonania() if (tryb_skaner and sizing_przekonania) else None
    # W-325 GUBERNATOR — jeden sterownik na CAŁY portfel (nie per-para). Karmiony
    # agregatem rankingu skanera w każdym tyku; działa tylko w trybie skanera.
    gub = None
    if gubernator and tryb_skaner:
        from imperium.koloseum.gubernator import Gubernator, rozrzut_ocen
        gub = Gubernator()
    snapshot_per: "Dict[str, Dict[str, Any]]" = {}
    for ts, sym, i in os_czasu:
        bary = bary_per[sym]
        engine.przetworz_bar(_bar_data(bary[i]))
        eq = engine.kapital_calkowity
        equity_dnia[ts // _DZ] = eq
        frakcja_breaker = 1.0
        if breaker is not None:
            breaker.aktualizuj(eq)
            frakcja_breaker = breaker.frakcja_pozycji()
            # W-313: HALT nie blokuje totalnie — frakcja_halt (0.1×) zapobiega deadlockowi
            if frakcja_breaker <= 0.0:
                continue
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
            # Opcja A: przekaż StanRynku do Dyrygenta → Namiestnik decyduj_z_radarem
            dyrygenci[sym].stan_rynku = stan
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

        # C-01 CROSS-SECTIONAL RS (W-335): z-score zwrotu tego symbolu vs koszyk, do ts
        # (przyczynowo). Tylko ogon (lookback+1) per symbol → O(lookback)/tyk. Neuron
        # C-01 czyta CROSS_RS z kontekst_dodatkowy. Wstawione PO radarze (radar nadpisuje
        # kontekst), by RS nie zginął.
        if len(bary_per) >= 2:
            close_koszyk = {}
            for s in bary_per:
                k = _bs.bisect_right(_ts_arr[s], ts)
                if k >= 1:
                    lo = max(0, k - _RS_LOOKBACK - 1)
                    close_koszyk[s] = _close[s][lo:k]
            rs_map = _cross_sectional_rs(close_koszyk, lookback=_RS_LOOKBACK)
            if sym in rs_map:
                dyrygenci[sym].kontekst_dodatkowy["CROSS_RS"] = rs_map[sym]

        # W-sentyment: wstrzyknij historyczny funding/OI/L-S dla TEGO baru (Prawo XVI).
        # Forward-fillowany kauzalnie (ts ≤ bar) → PSY-01/02/04 budzą się w backteście.
        # Po radarze i RS (kontekst może być nadpisany przez radar), by sentyment przetrwał.
        # WAŻNE: czyść klucze sentymentu PRZED update — bez tego (gdy radar nie wstaje,
        # np. koszyk bez BTC) stary funding z poprzedniego baru zostaje w kontekście
        # i neuron głosuje na nieaktualnych danych zamiast spać (stale-data, Prawo XV).
        if sentyment_per is not None:
            kontekst = dyrygenci[sym].kontekst_dodatkowy
            for _k in ("FUNDING_RATE", "OPEN_INTEREST", "OPEN_INTEREST_PREV", "LONG_SHORT_RATIO",
                       "DVOL_INDEX"):
                kontekst.pop(_k, None)
            sent = sentyment_per.get(sym, {}).get(int(ts))
            if sent:
                kontekst.update(sent)

        okno_barow = bary[i - okno: i + 1]

        # W-317 TRYB NAJLEPSZE: zaktualizuj snapshot tego symbolu i sprawdź, czy jest
        # w TOP-N okazji koszyka. Jeśli NIE — brak nowego wejścia (exity już zrobione
        # w przetworz_bar). To zmienia system z „N botów" w „łowcę najlepszych okazji".
        conviction_mult = 1.0
        gub_mult = 1.0
        if skaner is not None:
            if _wsk_cache is not None and sym in _wsk_cache:
                snapshot_per[sym] = _wsk_cache[sym].get(int(ts), {})
            else:
                snapshot_per[sym] = budowniczy.zbuduj(okno_barow)
            ranking = skaner.skanuj(snapshot_per)
            top = ranking[:skaner_top_n]
            if sym not in {o.symbol for o in top}:
                continue   # nie w TOP-N → nie polujemy na tę okazję teraz
            # W-318: większa stawka na mocniejszej okazji (przekonanie = score znormalizowany
            # min-max w całym rankingu koszyka w tym tyku). Bez tego selekcja przycina ogon.
            scores = [o.score for o in ranking] if ranking else []
            if sizer is not None and len(ranking) >= 2:
                smin, smax = min(scores), max(scores)
                this = next(o.score for o in top if o.symbol == sym)
                conv = (this - smin) / (smax - smin) if smax > smin else 1.0
                conviction_mult = sizer.mnoznik(conv)
            # W-325 GUBERNATOR: globalny mnożnik z agregatu koszyka (pewność lidera ×
            # wyrazistość rankingu × stan DD). Jeden ster na całą flotę, płynna histereza.
            if gub is not None and scores:
                # Konwikcja = BEZWZGLĘDNA siła lidera (score sumy z-score'ów, lider=ranking[0]),
                # squashowana do [0,1]: score≥3 (mocny setup) → pełna pewność. Nie min-max
                # (lider zawsze=1.0 — zdegenerowane), lecz absolutna jakość najlepszej okazji.
                konw = max(0.0, min(1.0, ranking[0].score / 3.0))
                stan_g = gub.ocen(konwikcja_koszyka=konw,
                                  rozrzut_okazji=rozrzut_ocen(scores),
                                  dd_frakcja=frakcja_breaker,
                                  breadth=len(ranking) / max(1, n))
                gub_mult = stan_g.mnoznik

        # Sizing par: budżet × frakcja DD-control × ster korelacyjny × przekonanie × gubernator.
        # W-319 compounding: baza = bieżące equity (pula łupów) zamiast kapitału startowego.
        baza_kapitalu = engine.kapital_calkowity if compounding else kapital_startowy
        dyrygenci[sym].kapital_sizing = (baza_kapitalu * wagi_akt[sym]
                                         * frakcja_breaker * frakcja_stres
                                         * conviction_mult * gub_mult)
        dyrygenci[sym].cykl(sym, okno_barow, rezim=rezim_arg, timestamp=ts)

    # Domknij otwarte po ostatniej cenie każdej pary
    ostatnie = {sym: bary_per[sym][-1]["close"] for sym in bary_per}
    engine.zamknij_wszystkie(ostatnie, powod="MANUAL")
    if os_czasu:
        equity_dnia[os_czasu[-1][0] // _DZ] = engine.kapital_calkowity
    engine.krzywa_equity = [equity_dnia[d] for d in sorted(equity_dnia)]

    # W-323c SCOREBOARD KONTRYBUCJI — scal Igrzyska wszystkich par w jeden ranking
    # neuronów (accuracy/stability/wynik) i dołącz do silnika. Mierzona baza do
    # strojenia NEURONY_STYLU danymi, nie intuicją (Prawo I). Opt-in: igrzyska_learning.
    if igrzyska_learning:
        from imperium.biblioteki.igrzyska import Igrzyska as _Igrzyska, StatystykaNeuronu as _Stat
        scalone = _Igrzyska()
        _POLA = ("tp", "fp", "long_trafne", "long_total", "short_trafne",
                 "short_total", "flipy", "sygnaly", "contribution_sum",
                 "timeliness_sum", "contribution_n")
        for d in dyrygenci.values():
            ig = getattr(d, "_igrzyska", None)
            if ig is None:
                continue
            for klucz, st in ig.statystyki.items():
                if klucz not in scalone.statystyki:
                    scalone.statystyki[klucz] = _Stat(klucz=klucz)
                tgt = scalone.statystyki[klucz]
                for pole in _POLA:
                    setattr(tgt, pole, getattr(tgt, pole) + getattr(st, pole))
        engine.ranking_neuronow = scalone.ranking()
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
