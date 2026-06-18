"""
W-331 — testy RealOrderRouter (offline, MockExchange — bez sieci, bez kluczy API).

Prawo XXI + Reguła Test-Granic:
  - brak kluczy → EnvironmentError (granica: żaden sekret w kodzie)
  - wejście LONG/SHORT → CCXT create_order wywołany z poprawnymi parametrami
  - wejście blokowane (brak kapitału) → CCXT NIE wywołany
  - błąd CCXT przy wejściu → pozycja papierowa żyje, log ERROR
  - wyjście przez _zamknij (SL/TP/MANUAL) → CCXT wywołany reduceOnly
  - błąd CCXT przy wyjściu → wynik papierowy zwrócony, log ERROR
  - zamknij_wszystkie → każda pozycja osobno wysłana
  - raport_real → poprawne liczniki
"""

import pytest
from imperium.drogi.real_order_router import RealOrderRouter, _zbuduj_mexc
from imperium.koloseum.paper_trading import SygnalWejscia


# ── Mock Exchange ─────────────────────────────────────────────────────────────

class MockExchange:
    """Imituje minimalny interfejs CCXT bez sieci."""

    def __init__(self, fail_on: str = "", pozycje=None):
        self.orders: list = []
        self.fail_on = fail_on  # "entry" | "exit" | "positions" | "" (nigdy)
        self._pozycje = pozycje or []

    def fetch_positions(self):
        if self.fail_on == "positions":
            raise ConnectionError("Mock: fetch_positions niedostępny")
        return self._pozycje

    def create_order(self, symbol, type, side, amount, params=None):
        params = params or {}
        is_reduce = params.get("reduceOnly", False)
        if self.fail_on == "entry" and not is_reduce:
            raise ConnectionError("Mock: exchange niedostępny")
        if self.fail_on == "exit" and is_reduce:
            raise ConnectionError("Mock: exchange niedostępny")
        oid = f"ORD-{len(self.orders)+1:04d}"
        self.orders.append({"id": oid, "symbol": symbol, "side": side, "amount": amount, **params})
        return {"id": oid, "status": "closed", "filled": amount}


def _router(exchange=None, kapital=5000.0, fail_on="") -> RealOrderRouter:
    ex = exchange or MockExchange(fail_on=fail_on)
    return RealOrderRouter(kapital_startowy=kapital, exchange=ex)


def _sygnal(sym="BTCUSDT", kierunek="LONG", cena=50000.0, rozmiar=1000.0, dzwignia=5.0):
    return SygnalWejscia(
        symbol=sym, kierunek=kierunek, cena_wejscia=cena,
        pewnosc=0.75,
        rozmiar_usdt=rozmiar, dzwignia=dzwignia,
        stop_loss=cena * 0.97 if kierunek == "LONG" else cena * 1.03,
        take_profit=cena * 1.06 if kierunek == "LONG" else cena * 0.94,
        interwal="4h",
    )


# ── Testy ─────────────────────────────────────────────────────────────────────

def test_brak_kluczy_rzuca_environment_error():
    """Granica: brak kluczy → EnvironmentError zamiast cichego błędu."""
    import os
    backup_key = os.environ.pop("MEXC_API_KEY", None)
    backup_sec = os.environ.pop("MEXC_SECRET", None)
    try:
        with pytest.raises(EnvironmentError, match="MEXC_API_KEY"):
            _zbuduj_mexc()
    finally:
        if backup_key is not None:
            os.environ["MEXC_API_KEY"] = backup_key
        if backup_sec is not None:
            os.environ["MEXC_SECRET"] = backup_sec


def test_brak_ccxt_rzuca_import_error():
    """Granica: brak ccxt → ImportError z instrukcją pip install."""
    import sys
    original = sys.modules.get("ccxt")
    sys.modules["ccxt"] = None  # type: ignore[assignment]
    try:
        with pytest.raises((ImportError, AttributeError, TypeError)):
            _zbuduj_mexc()
    finally:
        if original is None:
            sys.modules.pop("ccxt", None)
        else:
            sys.modules["ccxt"] = original


def test_wejscie_long_wywoluje_ccxt_buy():
    ex = MockExchange()
    r = _router(ex)
    poz = r.wejdz(_sygnal(kierunek="LONG"))
    assert poz is not None
    assert len(ex.orders) == 1
    assert ex.orders[0]["side"] == "buy"
    assert ex.orders[0]["symbol"] == "BTCUSDT"


def test_wejscie_short_wywoluje_ccxt_sell():
    ex = MockExchange()
    r = _router(ex)
    poz = r.wejdz(_sygnal(kierunek="SHORT"))
    assert poz is not None
    assert len(ex.orders) == 1
    assert ex.orders[0]["side"] == "sell"


def test_wejscie_zablokowane_brak_kapitalu_nie_wysyla_do_ccxt():
    """Granica: brak kapitału → PaperTradingEngine odrzuca → CCXT nie wywołany."""
    ex = MockExchange()
    r = _router(ex, kapital=10.0)  # za mało
    poz = r.wejdz(_sygnal(rozmiar=1000.0))
    assert poz is None
    assert len(ex.orders) == 0


def test_blad_ccxt_na_wejsciu_pozycja_papierowa_zyje():
    """Błąd CCXT nie zabija pozycji wirtualnej — P&L tracking działa."""
    r = _router(fail_on="entry")
    poz = r.wejdz(_sygnal())
    assert poz is not None  # papier żyje
    raport = r.raport_real()
    assert raport["bledy_wejscia"] == 1


def test_zamkniecie_sl_wysyla_ccxt_reduce_only():
    """_zamknij (TP/SL) → CCXT create_order z reduceOnly=True."""
    ex = MockExchange()
    r = _router(ex)
    poz = r.wejdz(_sygnal(kierunek="LONG", cena=50000.0))
    assert poz is not None
    assert len(ex.orders) == 1

    wynik = r._zamknij(poz.pozycja_id, 48000.0, "SL")
    assert wynik is not None
    assert len(ex.orders) == 2
    close_order = ex.orders[1]
    assert close_order["reduceOnly"] is True
    assert close_order["side"] == "sell"  # zamknięcie LONG = sell


def test_zamkniecie_short_wysyla_buy_reduce_only():
    ex = MockExchange()
    r = _router(ex)
    poz = r.wejdz(_sygnal(kierunek="SHORT", cena=50000.0))
    assert poz is not None

    wynik = r._zamknij(poz.pozycja_id, 52000.0, "TP")
    assert wynik is not None
    close_order = ex.orders[1]
    assert close_order["side"] == "buy"
    assert close_order["reduceOnly"] is True


def test_blad_ccxt_na_wyjsciu_wynik_papierowy_zwrocony():
    """Błąd CCXT przy zamknięciu → wynik papierowy nadal zwrócony."""
    r = _router(fail_on="exit")
    poz = r.wejdz(_sygnal())
    assert poz is not None
    wynik = r._zamknij(poz.pozycja_id, 51000.0, "TP")
    assert wynik is not None  # papier zdał raport
    assert wynik.pnl_usdt != 0.0 or wynik.powod_zamkniecia == "TP"


def test_zamknij_wszystkie_wysyla_po_jednym_ordenie_na_pozycje():
    ex = MockExchange()
    r = _router(ex, kapital=20_000.0)
    r.wejdz(_sygnal("BTCUSDT", cena=50000.0, rozmiar=1000.0))
    r.wejdz(_sygnal("ETHUSDT", cena=3000.0, rozmiar=1000.0))
    assert len(r.otwarte) == 2

    r.zamknij_wszystkie({"BTCUSDT": 51000.0, "ETHUSDT": 3100.0}, powod="PETLA_STOP")
    # 2 wejścia + 2 wyjścia
    assert len(ex.orders) == 4
    close_orders = [o for o in ex.orders if o.get("reduceOnly")]
    assert len(close_orders) == 2


def test_raport_real_po_zamknieciu_otwarte_zero():
    ex = MockExchange()
    r = _router(ex)
    poz = r.wejdz(_sygnal())
    r._zamknij(poz.pozycja_id, 51000.0, "TP")
    raport = r.raport_real()
    assert raport["otwarte_real"] == 0
    assert raport["bledy_wejscia"] == 0


def test_qty_obliczone_z_rozmiaru_i_ceny():
    """Granica: qty = rozmiar_usdt / cena — sprawdź że nie 0 i nie NaN."""
    ex = MockExchange()
    r = _router(ex)
    r.wejdz(_sygnal(cena=40000.0, rozmiar=800.0))
    qty = ex.orders[0]["amount"]
    expected = round(800.0 / 40000.0, 6)
    assert abs(qty - expected) < 1e-8
    assert qty > 0


# ── Synchronizacja pozycji przy starcie (W-333) ─────────────────────────────

def _poz_mexc(symbol="BTC/USDT:USDT", side="long", entry=50000.0, contracts=0.02,
              leverage=5, liq=None):
    return {
        "symbol": symbol, "side": side, "entryPrice": entry,
        "contracts": contracts, "leverage": leverage,
        "notional": contracts * entry,
        "liquidationPrice": liq,
    }


def test_sync_odtwarza_otwarta_pozycje_z_mexc():
    """Po restarcie: pozycja na MEXC → odtworzona w trackingu (kontrola SL/TP)."""
    ex = MockExchange(pozycje=[_poz_mexc(side="long", entry=50000.0, contracts=0.02)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    n = r.synchronizuj_pozycje(interwal="4h")
    assert n == 1
    assert len(r.otwarte) == 1
    poz = list(r.otwarte.values())[0]
    assert poz.kierunek == "LONG"
    assert poz.cena_wejscia == 50000.0
    assert r.raport_real()["otwarte_real"] == 1


def test_sync_short_kierunek():
    ex = MockExchange(pozycje=[_poz_mexc(side="short", entry=3000.0, contracts=1.0)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    r.synchronizuj_pozycje()
    poz = list(r.otwarte.values())[0]
    assert poz.kierunek == "SHORT"


def test_sync_pomija_pozycje_zerowe():
    """Granica: contracts==0 → pozycja zamknięta, NIE odtwarzamy."""
    ex = MockExchange(pozycje=[
        _poz_mexc(contracts=0.0),
        _poz_mexc(symbol="ETH/USDT:USDT", contracts=1.0, entry=3000.0),
    ])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    n = r.synchronizuj_pozycje()
    assert n == 1  # tylko ta z contracts>0


def test_sync_pomija_pozycje_bez_ceny():
    """Granica: entryPrice==0 → brak danych, pomijamy (nie odtwarzamy śmieci)."""
    ex = MockExchange(pozycje=[_poz_mexc(entry=0.0, contracts=0.02)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    n = r.synchronizuj_pozycje()
    assert n == 0


def test_sync_brak_pozycji_zwraca_zero():
    ex = MockExchange(pozycje=[])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    assert r.synchronizuj_pozycje() == 0
    assert len(r.otwarte) == 0


def test_sync_blad_fetch_positions_nie_wywala():
    """fetch_positions padł → log ERROR, engine startuje pusty (nie crash)."""
    ex = MockExchange(fail_on="positions")
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    n = r.synchronizuj_pozycje()
    assert n == 0


def test_sync_dry_run_nie_odtwarza():
    """dry_run nie składał zleceń → nie ma realnych pozycji do odtworzenia."""
    ex = MockExchange(pozycje=[_poz_mexc(contracts=0.02)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex, dry_run=True)
    n = r.synchronizuj_pozycje()
    assert n == 0


def test_sync_odtworzona_pozycja_zamykalna():
    """Odtworzona pozycja musi być zamykalna (wysyła reduceOnly na MEXC)."""
    ex = MockExchange(pozycje=[_poz_mexc(side="long", entry=50000.0, contracts=0.02)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    r.synchronizuj_pozycje()
    pid = list(r.otwarte.keys())[0]
    wynik = r._zamknij(pid, 51000.0, "MANUAL")
    assert wynik is not None
    close_orders = [o for o in ex.orders if o.get("reduceOnly")]
    assert len(close_orders) == 1
    assert close_orders[0]["side"] == "sell"  # zamknięcie LONG


def test_sync_long_nie_zamyka_sie_na_pierwszym_barze():
    """GRANICA: pozycja SYNC LONG nie może paść przez TP=0 na pierwszym barze."""
    from imperium.koloseum.paper_trading import BarData
    ex = MockExchange(pozycje=[_poz_mexc(side="long", entry=50000.0, contracts=0.02)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    r.synchronizuj_pozycje()
    assert len(r.otwarte) == 1
    bar = BarData(symbol="BTC/USDT:USDT", interwal="4h", timestamp=1,
                  open=50100.0, high=50500.0, low=49800.0, close=50200.0, volume=1.0)
    zamkniete = r.przetworz_bar(bar)
    assert len(zamkniete) == 0, "SYNC LONG nie powinien zamknąć się na zwykłym barze"
    assert len(r.otwarte) == 1


def test_sync_short_nie_zamyka_sie_na_pierwszym_barze():
    """GRANICA: pozycja SYNC SHORT nie może paść przez SL=0 na pierwszym barze."""
    from imperium.koloseum.paper_trading import BarData
    ex = MockExchange(pozycje=[_poz_mexc(side="short", entry=50000.0, contracts=0.02)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    r.synchronizuj_pozycje()
    bar = BarData(symbol="BTC/USDT:USDT", interwal="4h", timestamp=1,
                  open=49900.0, high=50200.0, low=49500.0, close=49800.0, volume=1.0)
    zamkniete = r.przetworz_bar(bar)
    assert len(zamkniete) == 0, "SYNC SHORT nie powinien zamknąć się na zwykłym barze"
    assert len(r.otwarte) == 1


def test_sync_uzywa_liquidation_z_gieldy():
    """Jeśli giełda podaje liquidationPrice — używamy go, nie szacunku."""
    ex = MockExchange(pozycje=[_poz_mexc(side="long", entry=50000.0, liq=45000.0)])
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex)
    r.synchronizuj_pozycje()
    poz = list(r.otwarte.values())[0]
    assert poz.cena_likwidacji == 45000.0


# ── Tryb dry-run (W-332) ────────────────────────────────────────────────────

def test_dry_run_nie_wysyla_zlecen_do_ccxt():
    """Granica: dry_run=True → create_order NIGDY nie wywołany na exchange."""
    ex = MockExchange()
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex, dry_run=True)
    poz = r.wejdz(_sygnal(kierunek="LONG"))
    assert poz is not None  # papier żyje
    assert len(ex.orders) == 0  # NIC nie poszło na giełdę
    raport = r.raport_real()
    assert raport["dry_run"] is True
    assert raport["dry_run_zlecen"] == 1


def test_dry_run_loguje_wejscie_i_wyjscie():
    """dry_run liczy zlecenia wejścia i wyjścia, ale nie wysyła."""
    ex = MockExchange()
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex, dry_run=True)
    poz = r.wejdz(_sygnal(kierunek="LONG", cena=50000.0))
    r._zamknij(poz.pozycja_id, 51000.0, "TP")
    assert len(ex.orders) == 0  # dalej zero realnych
    raport = r.raport_real()
    assert raport["dry_run_zlecen"] == 2  # wejście + wyjście
    assert raport["bledy_wejscia"] == 0


def test_dry_run_zachowuje_pnl_papierowy():
    """dry_run nadal liczy P&L (to symulacja na realnym połączeniu)."""
    ex = MockExchange()
    r = RealOrderRouter(kapital_startowy=5000.0, exchange=ex, dry_run=True)
    poz = r.wejdz(_sygnal(kierunek="LONG", cena=50000.0))
    wynik = r._zamknij(poz.pozycja_id, 52000.0, "TP")
    assert wynik is not None
    assert wynik.pnl_usdt > 0  # LONG 50k→52k = zysk


def test_petla_live_dry_run_uzywa_routera_z_flaga():
    """petla_live paper=False, dry_run=True → RealOrderRouter(dry_run=True)."""
    from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live
    from tests.test_petla_live import _MockLoader

    ex = MockExchange()
    flagi = {}

    class _MockRR(RealOrderRouter):
        def __init__(self, *a, **kw):
            flagi["dry_run"] = kw.get("dry_run")
            kw["exchange"] = ex
            super().__init__(*a, **kw)

    import imperium.drogi.real_order_router as ror_mod
    original = ror_mod.RealOrderRouter
    ror_mod.RealOrderRouter = _MockRR  # type: ignore[assignment]
    try:
        cfg = KonfigPetliLive(
            symbole=["BTCUSDT"], interwal="4h",
            kapital_startowy=1000.0, paper=False, dry_run=True,
        )
        handluj_live(cfg, max_barow=1, _loader=_MockLoader())
    finally:
        ror_mod.RealOrderRouter = original
    assert flagi["dry_run"] is True


def test_petla_live_paper_false_uzywa_real_order_router():
    """petla_live z paper=False instancjonuje RealOrderRouter."""
    from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live
    from tests.test_petla_live import _MockLoader

    ex = MockExchange()

    class _MockRealRouter(RealOrderRouter):
        UZYTY = False
        def __init__(self, *a, **kw):
            kw["exchange"] = ex
            super().__init__(*a, **kw)
            _MockRealRouter.UZYTY = True

    import imperium.drogi.real_order_router as ror_mod
    original = ror_mod.RealOrderRouter

    ror_mod.RealOrderRouter = _MockRealRouter  # type: ignore[assignment]
    try:
        cfg = KonfigPetliLive(
            symbole=["BTCUSDT"],
            interwal="4h",
            kapital_startowy=1000.0,
            paper=False,
        )
        handluj_live(cfg, max_barow=1, _loader=_MockLoader())
    finally:
        ror_mod.RealOrderRouter = original

    assert _MockRealRouter.UZYTY, "RealOrderRouter powinien być użyty przy paper=False"
