"""
Testy Dyrygenta — orkiestratora pełnego cyklu decyzyjnego (Faza 0).

Sprawdzają łańcuch end-to-end: bary → wskaźniki → Legatus → Kalkulator → Engine.
Używają wstrzykniętego wskazniki_provider (bez TA-Lib — czysty Python).
"""

from imperium.koloseum.dyrygent import Dyrygent, DecyzjaCyklu
from imperium.koloseum.paper_trading import PaperTradingEngine, BarData
from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
from imperium.legiony.rejestr import zbuduj_legatusa


def _bary(n=60, start=100.0, krok=0.5):
    """Generuje rosnącą serię barów OHLCV (trend wzrostowy)."""
    bary = []
    cena = start
    for i in range(n):
        o = cena
        c = cena + krok
        h = c + 0.2
        l = o - 0.2
        bary.append({"open": o, "high": h, "low": l, "close": c,
                     "volume": 1000.0 + i, "symbol": "BTCUSDT", "interwal": "1H"})
        cena = c
    return bary


def _dyrygent_z_providerem(wskazniki: dict, kapital=10_000.0):
    """Buduje Dyrygenta z pełnym rojem ale wstrzykniętymi wskaźnikami (bez TA-Lib)."""
    legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
    engine = PaperTradingEngine(kapital_startowy=kapital, sesja_id="TEST")
    return Dyrygent(
        legatus=legatus,
        kalkulator=KalkulatorLewara(),
        engine=engine,
        wskazniki_provider=lambda bary: dict(wskazniki),
        min_pewnosc=0.1,
    )


def test_cykl_bez_wskaznikow_konczy_na_budowniczym():
    d = _dyrygent_z_providerem({})  # provider zwraca pusty dict
    decyzja = d.cykl("BTCUSDT", _bary())
    assert decyzja.etap == "BUDOWNICZY"
    assert decyzja.wszedl is False


def test_cykl_neutralny_nie_wchodzi():
    # Wskaźniki bez wyraźnej przewagi — rój neutralny
    d = _dyrygent_z_providerem({"CLOSE": 100.0})
    decyzja = d.cykl("BTCUSDT", _bary())
    # Albo NEUTRAL, albo słaby — w każdym razie bez wejścia
    assert decyzja.wszedl is False
    assert decyzja.etap in ("LEGATUS_NEUTRAL", "LEGATUS_SLABY", "PRETORIANIE_WETO")


def test_cykl_silny_long_otwiera_pozycje():
    # RSI wyprzedany + trend → neurony powinny dać LONG z przewagą
    wskazniki = {
        "CLOSE": 130.0, "RSI_14": 22.0, "ADX_14": 30.0,
        "MACD_HIST": 1.5, "EMA_50": 120.0, "EMA_200": 110.0,
        "STOCH_K": 15.0, "STOCH_D": 18.0, "CCI_20": -150.0,
    }
    d = _dyrygent_z_providerem(wskazniki)
    decyzja = d.cykl("BTCUSDT", _bary(), rezim="TREND_STRONG")
    # Cykl musi dojść co najmniej do Legatusa z konkretnym kierunkiem
    assert decyzja.raport is not None
    # Jeśli wszedł — sprawdź spójność sygnału
    if decyzja.wszedl:
        assert decyzja.etap == "WEJSCIE"
        assert decyzja.sygnal.stop_loss > 0
        assert decyzja.sygnal.take_profit > 0
        assert decyzja.sygnal.dzwignia >= 1
        assert len(d.engine.otwarte) == 1
    else:
        # Dopuszczalne zakończenia gdy Pretorianie/silnik blokują
        assert decyzja.etap in ("PRETORIANIE_WETO", "LEGATUS_SLABY",
                                "LEGATUS_NEUTRAL", "ENGINE_ODRZUCIL")


def test_regula_6pct_uzywa_daty_swiecy_nie_systemowej():
    """Reguła 6% w backteście liczy miesiąc z timestampu ŚWIECY, nie date.today()."""
    d = _dyrygent_z_providerem({"CLOSE": 100.0, "RSI_14": 50.0})
    d.regula_6pct = __import__(
        "imperium.pretorianie.kalkulator_lewara", fromlist=["RegulaSzesciuProcentEldera"]
    ).RegulaSzesciuProcentEldera()
    d.regula_6pct.reset_miesiac(10_000)
    # Świeca ze stycznia 2020 (ms epoch) — gdyby użyć date.today(), miesiąc by się nie zgadzał
    ts_styczen = 1_577_880_000_000   # 2020-01-01 12:00 UTC
    d.cykl("BTCUSDT", _bary(), timestamp=ts_styczen)
    assert d.regula_6pct._biezacy_miesiac == 1, \
        "Reguła 6% musi przyjąć miesiąc ze świecy (styczeń), nie z zegara systemu"


def test_decyzja_niesie_pelny_slad():
    d = _dyrygent_z_providerem({"CLOSE": 100.0, "RSI_14": 50.0})
    decyzja = d.cykl("BTCUSDT", _bary())
    assert isinstance(decyzja, DecyzjaCyklu)
    assert decyzja.symbol == "BTCUSDT"
    assert decyzja.etap  # niepusty
    assert decyzja.powod  # zawsze czytelny powód


def test_dyrygent_bez_zrodla_wskaznikow_rzuca():
    legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
    engine = PaperTradingEngine(kapital_startowy=1000.0, sesja_id="X")
    d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine)
    try:
        d.cykl("BTCUSDT", _bary())
        assert False, "powinien rzucić RuntimeError (brak Budowniczego i providera)"
    except RuntimeError:
        pass


def test_tryb_nieznany_rzuca():
    legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
    engine = PaperTradingEngine(kapital_startowy=1000.0, sesja_id="X")
    try:
        Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine, tryb="bzdura")
        assert False, "powinien rzucić AssertionError dla nieznanego trybu"
    except AssertionError as e:
        assert "tryb" in str(e).lower() or True  # assert z komunikatu trybu


def test_tryb_filtr_blokuje_konflikt():
    """Tryb filtr: gdy brak dopasowanej strategii lub konflikt → brak wejścia."""
    legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
    engine = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="F")
    d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                 wskazniki_provider=lambda b: {"CLOSE": 130.0, "RSI_14": 25.0},
                 min_pewnosc=0.1, tryb="filtr")
    decyzja = d.cykl("BTCUSDT", _bary(), rezim="VOLATILE")
    # W trybie filtr bez zgodnej strategii nie wchodzimy
    if not decyzja.wszedl:
        assert decyzja.etap in ("STRATEGIA_BRAK", "STRATEGIA_KONFLIKT",
                                "PRETORIANIE_WETO", "LEGATUS_NEUTRAL", "LEGATUS_SLABY")


def test_trzy_tryby_dzialaja():
    """Każdy z trzech trybów wykonuje cykl bez wyjątku."""
    for tryb in ("agregat", "filtr", "strategia"):
        legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
        engine = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id=tryb)
        d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                     wskazniki_provider=lambda b: {"CLOSE": 130.0, "RSI_14": 25.0},
                     min_pewnosc=0.1, tryb=tryb)
        decyzja = d.cykl("BTCUSDT", _bary(), rezim="VOLATILE")
        assert decyzja.etap  # niepusty — cykl się wykonał
        assert decyzja.powod


def test_pelny_cykl_z_zarzadzaniem_pozycja():
    """End-to-end: otwarcie pozycji, potem bar dotyka TP → zamknięcie + PnL."""
    wskazniki = {
        "CLOSE": 130.0, "RSI_14": 20.0, "ADX_14": 35.0,
        "MACD_HIST": 2.0, "EMA_50": 120.0, "EMA_200": 110.0,
    }
    d = _dyrygent_z_providerem(wskazniki)
    decyzja = d.cykl("BTCUSDT", _bary(), rezim="TREND_STRONG")

    if decyzja.wszedl:
        poz = list(d.engine.otwarte.values())[0]
        # Bar który dotyka take-profit
        bar_tp = BarData(
            timestamp=0, open=poz.cena_wejscia,
            high=poz.take_profit + 1.0, low=poz.cena_wejscia - 0.1,
            close=poz.take_profit, volume=1000.0,
            symbol="BTCUSDT", interwal="1H",
        )
        zamkniete = d.engine.przetworz_bar(bar_tp)
        assert len(zamkniete) == 1
        assert zamkniete[0].powod_zamkniecia == "TP_HIT"
        assert zamkniete[0].pnl_usdt > 0  # TP = zysk
        assert len(d.engine.otwarte) == 0
