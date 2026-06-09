"""Testy Schedulera — backtest, jednorazowo, bezpiecznik, błędy."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.drogi.scheduler import (
    Scheduler, KonfiguracjaSchedulera,
)
from imperium.pretorianie.kalkulator_lewara import BezpiecznikKapitalu


def _config(**kwargs) -> KonfiguracjaSchedulera:
    defaults = {"interwal_s": 1, "sesja_id": "TEST", "symbole": ["BTCUSDT"], "log_kazdy_cykl": False}
    defaults.update(kwargs)
    return KonfiguracjaSchedulera(**defaults)


def test_backtest_przetwarza_wszystkie_bary():
    scheduler = Scheduler(_config())
    dane = [{"symbol": "BTCUSDT", "close": 65000.0 + i, "rezim": "TREND_STRONG"} for i in range(10)]
    wyniki = scheduler.backtest(dane)
    assert len(wyniki) == 10
    assert scheduler.stats.cykli_total == 10
    assert scheduler.stats.cykli_ok == 10
    assert scheduler.stats.cykli_blad == 0


def test_backtest_liczy_sygnaly():
    counter = {"n": 0}

    def sygnal_fn(dane):
        counter["n"] += 1
        return {"kierunek": "LONG", "pewnosc": 0.75, "symbol": dane["symbol"]}

    execute_counter = {"n": 0}

    def execute_fn(sygnal):
        execute_counter["n"] += 1
        return True

    scheduler = Scheduler(_config(), sygnal_fn=sygnal_fn, execute_fn=execute_fn)
    dane = [{"symbol": "BTCUSDT", "close": 65000.0} for _ in range(5)]
    scheduler.backtest(dane)
    assert counter["n"] == 5
    assert execute_counter["n"] == 5
    assert scheduler.stats.pozycje_otwarte == 5


def test_backtest_neutralny_nie_wykonuje():
    execute_counter = {"n": 0}

    def execute_fn(sygnal):
        execute_counter["n"] += 1
        return True

    scheduler = Scheduler(_config(), execute_fn=execute_fn)  # _mock_sygnal = NEUTRAL
    dane = [{"symbol": "BTCUSDT", "close": 65000.0} for _ in range(5)]
    scheduler.backtest(dane)
    assert execute_counter["n"] == 0


def test_bezpiecznik_blokuje_wykonanie():
    execute_counter = {"n": 0}

    def sygnal_fn(dane):
        return {"kierunek": "LONG", "pewnosc": 0.8, "symbol": dane["symbol"]}

    def execute_fn(sygnal):
        execute_counter["n"] += 1
        return True

    bezpiecznik = BezpiecznikKapitalu(kapital_startowy=10000.0)
    bezpiecznik.aktualizuj(6000.0)  # -40% → przepalony
    assert bezpiecznik.przepalony

    scheduler = Scheduler(_config(), sygnal_fn=sygnal_fn, execute_fn=execute_fn, bezpiecznik=bezpiecznik)
    dane = [{"symbol": "BTCUSDT", "close": 65000.0}]
    wyniki = scheduler.backtest(dane)
    assert execute_counter["n"] == 0
    assert wyniki[0]["sygnal"]["kierunek"] == "LONG"  # sygnal był, ale nie wykonany


def test_bezpiecznik_nowy_pozwala():
    execute_counter = {"n": 0}

    def sygnal_fn(dane):
        return {"kierunek": "LONG", "pewnosc": 0.8, "symbol": dane["symbol"]}

    def execute_fn(sygnal):
        execute_counter["n"] += 1
        return True

    bezpiecznik = BezpiecznikKapitalu(kapital_startowy=10000.0)
    bezpiecznik.aktualizuj(9500.0)  # -5% — nie przepalony
    assert not bezpiecznik.przepalony

    scheduler = Scheduler(_config(), sygnal_fn=sygnal_fn, execute_fn=execute_fn, bezpiecznik=bezpiecznik)
    dane = [{"symbol": "BTCUSDT", "close": 65000.0}]
    scheduler.backtest(dane)
    assert execute_counter["n"] == 1


def test_blad_w_fetch_liczy_cykl_blad():
    def broken_fetch(symbol, interwal):
        raise RuntimeError("Symulowany błąd API")

    scheduler = Scheduler(_config(max_bledow_z_rzędu=10, pauza_po_bledach_s=0), fetch_fn=broken_fetch)
    wynik = scheduler.jednorazowo()
    assert wynik["ok"] == False
    assert scheduler.stats.cykli_blad == 1


def test_jednorazowo_zwraca_wynik():
    scheduler = Scheduler(_config())
    wynik = scheduler.jednorazowo()
    assert "cykl" in wynik
    assert "symbole" in wynik
    assert wynik["ok"] == True


def test_multi_symbol():
    config = _config(symbole=["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    scheduler = Scheduler(config)
    wynik = scheduler.jednorazowo()
    assert "BTCUSDT" in wynik["symbole"]
    assert "ETHUSDT" in wynik["symbole"]
    assert "SOLUSDT" in wynik["symbole"]


def test_brak_danych_nie_crashuje():
    def no_data_fetch(symbol, interwal):
        return None

    scheduler = Scheduler(_config(), fetch_fn=no_data_fetch)
    wynik = scheduler.jednorazowo()
    assert wynik["ok"] == True
    assert wynik["symbole"]["BTCUSDT"]["status"] == "NO_DATA"


def test_statystyki_uptime():
    import time
    scheduler = Scheduler(_config())
    scheduler.stats.czas_start = time.time() - 5.0
    assert scheduler.stats.uptime_s >= 5.0
