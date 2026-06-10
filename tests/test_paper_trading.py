"""Testy Paper Trading Engine — wejścia, wyjścia, PnL, statystyki sesji."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.paper_trading import (
    PaperTradingEngine, SygnalWejscia, BarData,
)


def _engine(kapital: float = 10_000.0) -> PaperTradingEngine:
    return PaperTradingEngine(kapital_startowy=kapital, sesja_id="TEST")


def _sygnal(symbol="BTCUSDT", kierunek="LONG", wejscie=100.0, sl=95.0, tp=110.0, dzwignia=5, usdt=1000.0):
    return SygnalWejscia(symbol, "1H", kierunek, 0.75, wejscie, sl, tp, dzwignia, usdt)


def _bar(symbol="BTCUSDT", o=100.0, h=115.0, l=94.0, c=110.0):
    return BarData(0, o, h, l, c, 1000.0, symbol, "1H")


# ─── Wejście / blokady ────────────────────────────────────────────────────────

def test_wejscie_otwiera_pozycje():
    e = _engine()
    poz = e.wejdz(_sygnal())
    assert poz is not None
    assert len(e.otwarte) == 1


def test_brak_kapitalu_blokuje():
    e = _engine(kapital=50.0)  # za mało na margin
    poz = e.wejdz(_sygnal(usdt=1000.0, dzwignia=5))  # margin = 200 > 50
    assert poz is None
    assert len(e.otwarte) == 0


def test_duplikat_symbolu_blokuje():
    e = _engine()
    e.wejdz(_sygnal())
    poz2 = e.wejdz(_sygnal())  # ten sam symbol BTC
    assert poz2 is None
    assert len(e.otwarte) == 1


def test_max_otwartych_blokuje():
    e = PaperTradingEngine(kapital_startowy=50_000.0, sesja_id="T", max_otwartych=2)
    e.wejdz(_sygnal(symbol="BTCUSDT"))
    e.wejdz(_sygnal(symbol="ETHUSDT"))
    poz3 = e.wejdz(_sygnal(symbol="SOLUSDT"))
    assert poz3 is None
    assert len(e.otwarte) == 2


# ─── Wyzwalacze zamknięcia ─────────────────────────────────────────────────────

def test_tp_hit_long():
    e = _engine()
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=110.0, sl=95.0))
    bar = _bar(h=111.0, l=99.0, c=110.0)
    zamkniete = e.przetworz_bar(bar)
    assert len(zamkniete) == 1
    assert zamkniete[0].powod_zamkniecia == "TP_HIT"
    assert zamkniete[0].pnl_usdt > 0


def test_sl_hit_long():
    e = _engine()
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=110.0, sl=95.0))
    bar = _bar(h=101.0, l=94.0, c=99.0)
    zamkniete = e.przetworz_bar(bar)
    assert len(zamkniete) == 1
    assert zamkniete[0].powod_zamkniecia == "SL_HIT"
    assert zamkniete[0].pnl_usdt < 0


def test_tp_hit_short():
    e = _engine()
    e.wejdz(_sygnal(kierunek="SHORT", wejscie=100.0, sl=106.0, tp=90.0))
    bar = _bar(h=101.0, l=89.0, c=92.0)
    zamkniete = e.przetworz_bar(bar)
    assert len(zamkniete) == 1
    assert zamkniete[0].powod_zamkniecia == "TP_HIT"
    assert zamkniete[0].pnl_usdt > 0


def test_sl_hit_short():
    e = _engine()
    e.wejdz(_sygnal(kierunek="SHORT", wejscie=100.0, sl=106.0, tp=90.0))
    bar = _bar(h=107.0, l=99.0, c=105.0)
    zamkniete = e.przetworz_bar(bar)
    assert len(zamkniete) == 1
    assert zamkniete[0].powod_zamkniecia == "SL_HIT"
    assert zamkniete[0].pnl_usdt < 0


def test_timeout():
    e = _engine()
    from imperium.koloseum.paper_trading import MAX_BARS_OTWARCIA
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=200.0, sl=50.0))  # tp/sl nieosiągalne
    bar_neutralny = _bar(h=101.0, l=99.0, c=100.0)
    wyniki = []
    for _ in range(MAX_BARS_OTWARCIA + 1):
        wyniki.extend(e.przetworz_bar(bar_neutralny))
    assert len(wyniki) == 1
    assert wyniki[0].powod_zamkniecia == "TIMEOUT"


def test_likwidacja_long():
    e = _engine()
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=120.0, sl=85.0, dzwignia=10))
    # Likwidacja LONG przy 1/dzwignia = 10% od wejścia w dół
    bar = _bar(h=102.0, l=89.0, c=90.0)  # l=89 < likwidacja ~90
    zamkniete = e.przetworz_bar(bar)
    # Może trafić SL lub LIQ zaleznie od poziomu
    assert len(zamkniete) == 1


# ─── PnL i MAE/MFE ───────────────────────────────────────────────────────────

def test_pnl_zysk_logiczny():
    e = _engine()
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=110.0, sl=95.0, dzwignia=5, usdt=1000.0))
    zamkniete = e.przetworz_bar(_bar(h=112.0, l=99.0, c=111.0))
    w = zamkniete[0]
    assert w.pnl_usdt > 0
    assert w.kapital_po > w.kapital_przed - w.prowizja_usdt  # nawet po prowizji zysk


def test_mae_mfe_aktualizowane():
    e = _engine()
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=200.0, sl=50.0, dzwignia=1, usdt=500.0))
    # Pierwsza świeca: rośnie do 105, spada do 97
    e.przetworz_bar(_bar(h=105.0, l=97.0, c=102.0))
    poz = list(e.otwarte.values())[0]
    assert poz.mfe_pct > 0  # poszła w górę
    assert poz.mae_pct > 0  # była też w dół


def test_kapital_wraca_po_tp():
    e = _engine(kapital=10_000.0)
    kapital_przed_wejsciem = e.kapital
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=110.0, sl=95.0, dzwignia=5, usdt=1000.0))
    assert e.kapital < kapital_przed_wejsciem  # margin zablokowany
    e.przetworz_bar(_bar(h=112.0, l=99.0, c=111.0))
    assert e.kapital > kapital_przed_wejsciem  # po TP: margin + zysk


# ─── Statystyki sesji ─────────────────────────────────────────────────────────

def test_statystyki_win_rate():
    e = _engine(kapital=50_000.0)
    # 2 wygrane, 1 przegrana
    for s, bary in [
        (_sygnal("BTCUSDT", "LONG", 100, 95, 110, 5, 500), [_bar("BTCUSDT", h=112, l=99, c=111)]),
        (_sygnal("ETHUSDT", "LONG", 100, 95, 110, 5, 500), [_bar("ETHUSDT", h=112, l=99, c=111)]),
        (_sygnal("SOLUSDT", "LONG", 100, 95, 110, 5, 500), [_bar("SOLUSDT", h=101, l=93, c=96)]),
    ]:
        e.wejdz(s)
        for b in bary:
            e.przetworz_bar(b)
    stats = e.podsumowanie()
    assert stats.total_trades == 3
    assert stats.winning_trades == 2
    assert abs(stats.win_rate - 2/3) < 0.01


def test_statystyki_max_drawdown():
    e = _engine(kapital=50_000.0)
    # 3 przegrane z rzędu
    e = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="DD-TEST", max_otwartych=5)
    for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        e.wejdz(_sygnal(sym, "LONG", 100, 95, 110, 5, 500))
        e.przetworz_bar(_bar(sym, h=101, l=93, c=96))  # SL
    stats = e.podsumowanie()
    assert stats.max_drawdown_pct > 0
    assert stats.losing_trades == 3


def test_zamknij_wszystkie():
    e = _engine(kapital=50_000.0)
    e.wejdz(_sygnal("BTCUSDT"))
    e.wejdz(_sygnal("ETHUSDT"))
    assert len(e.otwarte) == 2
    wyniki = e.zamknij_wszystkie({"BTCUSDT": 105.0, "ETHUSDT": 98.0})
    assert len(wyniki) == 2
    assert len(e.otwarte) == 0


def test_kapital_calkowity_stabilny_przy_otwarciu():
    """
    Prawo XV: kapital_calkowity (wolny + zablokowany margin) NIE spada przy
    otwarciu pozycji — margin przenosi się z wolnego do zablokowanego, suma stała.
    To naprawia martwy breaker krzywej (W-062), który wcześniej dostawał sam
    wolny kapitał i mylił utylizację depozytu z drawdownem.
    """
    e = _engine(kapital=10_000.0)
    przed = e.kapital_calkowity
    assert abs(przed - 10_000.0) < 1e-6
    e.wejdz(_sygnal("BTCUSDT", "LONG", 100, 95, 110, 5, 1000.0))
    # Wolny kapitał spada (margin + prowizja zablokowane), ale całkowity prawie stały
    assert e.kapital < przed                      # wolny spadł
    # Całkowity spada tylko o prowizję wejścia (margin wrócił jako zablokowany)
    assert abs(e.kapital_calkowity - przed) < przed * 0.01


def test_kapital_calkowity_odzwierciedla_strate():
    """kapital_calkowity po zamknięciu stratnej pozycji = startowy − strata − prowizje."""
    e = _engine(kapital=10_000.0)
    e.wejdz(_sygnal("BTCUSDT", "LONG", 100, 95, 110, 5, 1000.0))
    e.przetworz_bar(_bar("BTCUSDT", o=100, h=101, l=93, c=96))  # SL trafiony → strata
    assert len(e.otwarte) == 0
    # Po zamknięciu całkowity = wolny (brak otwartych) i poniżej startowego
    assert e.kapital_calkowity == e.kapital
    assert e.kapital_calkowity < 10_000.0


def test_max_bars_otwarcia_per_engine():
    """FAZA B: TIMEOUT konfigurowalny per silnik; None → stała globalna."""
    from imperium.koloseum.paper_trading import MAX_BARS_OTWARCIA
    e_def = _engine()
    assert e_def.max_bars_otwarcia == MAX_BARS_OTWARCIA
    e_dlugi = PaperTradingEngine(kapital_startowy=10_000, sesja_id="T",
                                 max_bars_otwarcia=144)
    e_dlugi.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=200.0,
                                sl=50.0, dzwignia=2))
    # 100 barów bez TP/SL — przy limicie 144 pozycja ŻYJE (przy 48 by umarła)
    for i in range(100):
        e_dlugi.przetworz_bar(_bar(h=101.0, l=99.0, c=100.0))
    assert len(e_dlugi.otwarte) == 1, "limit 144 nie może zamknąć po 100 barach"
    for i in range(50):
        e_dlugi.przetworz_bar(_bar(h=101.0, l=99.0, c=100.0))
    assert len(e_dlugi.otwarte) == 0, "po 150 barach TIMEOUT musi zamknąć"
