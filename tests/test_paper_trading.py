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


def test_wynik_zamkniecia_niesie_timestamp_wejscia():
    """W-312: zamknięty trade przenosi timestamp_wejscia (walk-forward OOS)."""
    e = _engine(kapital=50_000.0)
    e.wejdz(_sygnal("BTCUSDT"), timestamp=1_700_000_000_000)
    wyniki = e.zamknij_wszystkie({"BTCUSDT": 105.0})
    assert len(wyniki) == 1
    assert wyniki[0].timestamp_wejscia == 1_700_000_000_000


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


# ─── Trailing stop (W-351) — Reguła Test-Granic ───────────────────────────────

def _engine_trail(kapital: float = 10_000.0) -> PaperTradingEngine:
    return PaperTradingEngine(kapital_startowy=kapital, sesja_id="TRAIL", trailing=True)


def test_trailing_off_domyslnie_brak_regresji():
    """trailing=False (domyślnie) → stary tor: zysk oddany do TIMEOUT, nie TRAIL."""
    e = _engine()                      # trailing OFF
    assert e.trailing is False
    e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=200.0, sl=50.0, dzwignia=2))
    powody = []
    for _ in range(48):
        for w in e.przetworz_bar(_bar(h=110.0, l=99.0, c=100.0)):
            powody.append(w.powod_zamkniecia)
    assert powody == ["TIMEOUT"], "bez trailingu winner ma wygasnąć przez TIMEOUT"


def test_trailing_uzbraja_i_blokuje_zysk_long():
    """LONG: ruch +6% uzbraja trailing; retrace → TRAIL_HIT z zyskiem."""
    e = _engine_trail()
    poz = e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=300.0, sl=50.0, dzwignia=2))
    we = poz.cena_wejscia
    e.przetworz_bar(_bar(h=we * 1.06, l=we, c=we * 1.05))   # +6% → armed
    assert poz.trailing_aktywny is True
    stop = poz.trailing_stop
    zamkniete = e.przetworz_bar(_bar(h=we * 1.055, l=stop - 0.01, c=stop))
    assert len(zamkniete) == 1
    assert zamkniete[0].powod_zamkniecia == "TRAIL_HIT"
    assert zamkniete[0].pnl_usdt > 0, "trailing musi zablokować zysk, nie stratę"


def test_trailing_prog_osiagniety_uzbraja():
    """Granica: ruch == próg (TRAILING_AKTYWACJA_PCT, warunek >=) UZBRAJA trailing."""
    from imperium.koloseum.paper_trading import TRAILING_AKTYWACJA_PCT
    e = _engine_trail()
    poz = e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=300.0, sl=50.0, dzwignia=2))
    we = poz.cena_wejscia
    # minimalny high osiągający próg (>= po stronie float); +epsilon kasuje szum mnożenia
    e.przetworz_bar(_bar(h=we * (1 + TRAILING_AKTYWACJA_PCT) + 1e-6, l=we, c=we))
    assert poz.trailing_aktywny is True


def test_trailing_ponizej_progu_nie_uzbraja():
    """Granica: tuż poniżej progu NIE uzbraja — żadnego TRAIL_HIT przedwcześnie."""
    from imperium.koloseum.paper_trading import TRAILING_AKTYWACJA_PCT
    e = _engine_trail()
    poz = e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=300.0, sl=50.0, dzwignia=2))
    we = poz.cena_wejscia
    e.przetworz_bar(_bar(h=we * (1 + TRAILING_AKTYWACJA_PCT - 0.001), l=we, c=we))  # tuż pod progiem
    assert poz.trailing_aktywny is False
    zamkniete = e.przetworz_bar(_bar(h=we * 1.02, l=we * 1.005, c=we * 1.01))
    assert zamkniete == [], "nieuzbrojony trailing nie zamyka pozycji"


def test_trailing_short_lustrzane():
    """SHORT: ruch -6% (korzystny) uzbraja; odbicie → TRAIL_HIT z zyskiem."""
    e = _engine_trail()
    poz = e.wejdz(_sygnal(kierunek="SHORT", wejscie=100.0, tp=50.0, sl=150.0, dzwignia=2))
    we = poz.cena_wejscia
    e.przetworz_bar(_bar(h=we, l=we * 0.94, c=we * 0.95))   # -6% favorable → armed
    assert poz.trailing_aktywny is True
    stop = poz.trailing_stop
    zamkniete = e.przetworz_bar(_bar(h=stop + 0.01, l=we * 0.945, c=stop))
    assert len(zamkniete) == 1
    assert zamkniete[0].powod_zamkniecia == "TRAIL_HIT"
    assert zamkniete[0].pnl_usdt > 0


def test_trailing_stop_tylko_sie_zaciska():
    """Monotonia: po szczycie +10% trailing nie cofa się przy niższym high."""
    e = _engine_trail()
    poz = e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=400.0, sl=50.0, dzwignia=2))
    we = poz.cena_wejscia
    e.przetworz_bar(_bar(h=we * 1.10, l=we * 1.05, c=we * 1.09))   # szczyt +10%
    stop_po_szczycie = poz.trailing_stop
    e.przetworz_bar(_bar(h=we * 1.07, l=stop_po_szczycie + 0.01, c=we * 1.068))  # niższy high
    assert poz.trailing_stop == stop_po_szczycie, "stop nie może się rozluźnić"


def test_trailing_cena_zamkniecia_na_poziomie_stopu():
    """TRAIL_HIT zamyka po cenie trailing_stop (minus slippage), nie po bar.close."""
    from imperium.koloseum.paper_trading import SLIPPAGE_PCT
    e = _engine_trail()
    poz = e.wejdz(_sygnal(kierunek="LONG", wejscie=100.0, tp=400.0, sl=50.0, dzwignia=2))
    we = poz.cena_wejscia
    e.przetworz_bar(_bar(h=we * 1.10, l=we * 1.05, c=we * 1.09))   # armed
    stop = poz.trailing_stop
    zamkniete = e.przetworz_bar(_bar(h=we * 1.07, l=stop - 1.0, c=stop - 0.5))  # low przebija stop
    assert zamkniete[0].powod_zamkniecia == "TRAIL_HIT"
    oczekiwana = round(stop * (1 - SLIPPAGE_PCT), 6)
    assert abs(zamkniete[0].cena_zamkniecia - oczekiwana) < 1e-6


# ── W1: KAŻDE zamknięcie musi zostawić ślad (naprawa 2026-07-29) ─────────────

def _engine_z_pamiecia(tmpdir):
    from imperium.koloseum.paper_trading import PaperTradingEngine
    return PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="TEST-W1",
                              log_dir=tmpdir, zrodlo="TEST")


def test_zamkniecie_na_koniec_biegu_trafia_do_w1():
    """
    Zmierzone przy pierwszym biegu zapisującym W1: silnik miał 23 zamknięcia, pamięć 22.
    Pozycja domknięta przez `zamknij_wszystkie` ginęła — logowała tylko ścieżka bara.
    """
    import tempfile
    from pathlib import Path

    from imperium.biblioteki.pamiec_absolutna import PamiecAbsolutna
    from imperium.koloseum.paper_trading import SygnalWejscia

    kat = Path(tempfile.mkdtemp())
    eng = _engine_z_pamiecia(kat)
    eng.wejdz(SygnalWejscia("BTCUSDT", "4H", "LONG", 0.8, 60000.0, 58000.0, 65000.0, 5, 1000.0))
    wyniki = eng.zamknij_wszystkie({"BTCUSDT": 61000.0}, powod="KONIEC_BIEGU")

    assert len(wyniki) == 1
    logi = PamiecAbsolutna(katalog=kat).wczytaj()
    assert len(logi) == len(eng.historia_zamkniec) == 1     # zero cichych strat
    assert logi[0].powod_zamkniecia == "KONIEC_BIEGU"


def test_zrodlo_wpisu_odroznia_backtest_od_paper():
    """Etykieta pochodzenia jedzie RAZEM z danymi — inaczej backtest udaje rzeczywistość."""
    import tempfile
    from pathlib import Path

    from imperium.biblioteki.pamiec_absolutna import PamiecAbsolutna
    from imperium.koloseum.paper_trading import SygnalWejscia

    kat = Path(tempfile.mkdtemp())
    eng = _engine_z_pamiecia(kat)
    eng.wejdz(SygnalWejscia("ETHUSDT", "4H", "LONG", 0.8, 3000.0, 2900.0, 3300.0, 5, 500.0))
    eng.zamknij_wszystkie({"ETHUSDT": 3100.0})
    assert PamiecAbsolutna(katalog=kat).wczytaj()[0].trade_status == "TEST"


def test_brak_log_dir_nie_pisze_do_w1():
    """GRANICA: bez `log_dir` silnik NIE dotyka W1 (domyślne zachowanie bez regresji)."""
    from imperium.koloseum.paper_trading import PaperTradingEngine, SygnalWejscia

    eng = PaperTradingEngine(kapital_startowy=1000.0, sesja_id="BEZ-W1")
    eng.wejdz(SygnalWejscia("BTCUSDT", "4H", "LONG", 0.8, 60000.0, 58000.0, 65000.0, 5, 100.0))
    assert eng.zamknij_wszystkie({"BTCUSDT": 61000.0}) and eng._pamiec is None


def test_zamkniecie_bez_bara_zachowuje_interwal():
    """Recenzja 2026-07-29: `zamknij_wszystkie` zapisywało do W1 pusty interwał, choć zna go
    z otwartej pozycji — a to systematycznie ostatnie trade'y biegu, więc analiza per
    interwał dostawała obciążenie nielosowe."""
    import tempfile
    from pathlib import Path as _P

    from imperium.biblioteki.pamiec_absolutna import PamiecAbsolutna
    from imperium.koloseum.paper_trading import SygnalWejscia

    kat = _P(tempfile.mkdtemp())
    eng = _engine_z_pamiecia(kat)
    eng.wejdz(SygnalWejscia("BTCUSDT", "4H", "LONG", 0.8, 60000.0, 58000.0, 65000.0, 5, 1000.0))
    eng.zamknij_wszystkie({"BTCUSDT": 61000.0}, powod="KONIEC_BIEGU")
    assert PamiecAbsolutna(katalog=kat).wczytaj()[0].interwal == "4H"
