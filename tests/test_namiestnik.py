"""
Testy Namiestnika — Regime-Aware Gating Network (Prawo XVI: mierzone, nie zgadywane).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_namiestnik_import():
    from imperium.koloseum.namiestnik import Namiestnik, get_namiestnik
    n = Namiestnik()
    assert n is not None
    s = get_namiestnik()
    assert s is not None


def test_znane_rezimy_zwracaja_ustawienia():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    rezimy = ["TREND_STRONG", "TREND_WEAK", "RANGING", "VOLATILE", "PANIC", "NORMAL",
              "ON-CHAIN_BULLISH", "SMC_ACTIVE"]
    for r in rezimy:
        u = n.decyduj(r)
        assert u.tryb in ("agregat", "filtr", "strategia"), f"{r}: nieznany tryb {u.tryb}"
        assert 0.0 < u.lewar_factor <= 2.0, f"{r}: lewar_factor poza zakresem"
        assert 0.5 <= u.prog_pewnosci <= 1.0, f"{r}: prog_pewnosci poza zakresem"


def test_cisza_przy_ranging_i_panic():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    assert not n.decyduj("RANGING").czy_grac, "RANGING powinno dać CISZĘ"
    assert not n.decyduj("PANIC").czy_grac, "PANIC powinno dać CISZĘ"


def test_gra_przy_trend_strong():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    assert n.decyduj("TREND_STRONG").czy_grac
    assert n.decyduj("TREND_STRONG").tryb == "filtr"


def test_trend_strong_lewar_wyzszy_niz_normal():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    assert n.decyduj("TREND_STRONG").lewar_factor > n.decyduj("NORMAL").lewar_factor


def test_panic_ma_najwyzszy_prog_i_nie_gra():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    u = n.decyduj("PANIC")
    assert u.prog_pewnosci >= 0.85
    assert not u.czy_grac


def test_fallback_dla_nieznanego_rezimu():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    u = n.decyduj("NIEZNANY_REZIM_XYZ")
    assert u is not None
    assert u.tryb in ("agregat", "filtr", "strategia")
    assert u.lewar_factor < 1.0  # fallback = ostrożny


def test_skaluj_dzwignie():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    # TREND_STRONG: lewar_factor=1.2 → dźwignia rośnie
    d_strong = n.skaluj_dzwignie(10, "TREND_STRONG")
    # PANIC: lewar_factor=0.1 → dźwignia minimalna
    d_panic = n.skaluj_dzwignie(10, "PANIC")
    assert d_strong > d_panic
    assert 1 <= d_strong <= 20
    assert 1 <= d_panic <= 20


def test_tablica_rezimu_zwraca_wszystkie():
    from imperium.koloseum.namiestnik import Namiestnik
    n = Namiestnik()
    t = n.tablica_rezimu()
    assert "TREND_STRONG" in t
    assert "PANIC" in t
    assert len(t) >= 6


def test_raport_zwraca_string():
    from imperium.koloseum.namiestnik import Namiestnik
    r = Namiestnik().raport()
    assert isinstance(r, str)
    assert "NAMIESTNIK" in r
    assert "TREND_STRONG" in r


def test_dyrygent_integracja_namiestnik():
    """Dyrygent z Namiestnikiem: RANGING → CISZA bez wejścia."""
    from imperium.koloseum.namiestnik import Namiestnik
    from imperium.koloseum.dyrygent import Dyrygent
    from unittest.mock import MagicMock

    wskazniki = {"RSI_14": 50.0, "CLOSE": 100.0, "ATR_14": 2.0}

    legatus_mock = MagicMock()
    raport_mock = MagicMock()
    raport_mock.weto = False
    raport_mock.kierunek = "LONG"
    raport_mock.pewnosc_agregatu = 0.65
    raport_mock.rezim = "RANGING"
    raport_mock.powod_weta = ""
    raport_mock.strategie_dopasowane = []
    raport_mock.zgodnych_neuronow = 5
    raport_mock.aktywnych_neuronow = 10
    legatus_mock.fokus.return_value = raport_mock

    engine_mock = MagicMock()
    engine_mock.kapital = 10000.0
    kalk_mock = MagicMock()

    d = Dyrygent(
        legatus=legatus_mock,
        kalkulator=kalk_mock,
        engine=engine_mock,
        wskazniki_provider=lambda _: wskazniki,
        namiestnik=Namiestnik(),
    )

    decyzja = d.cykl("BTCUSDT", [{"close": 100.0}], rezim="RANGING")
    # Namiestnik powinien zablokować dla RANGING
    assert not decyzja.wszedl
    assert "NAMIESTNIK_CISZA" in decyzja.etap or "CISZA" in decyzja.powod


def test_dyrygent_auto_rezim_klasyfikuje():
    """rezim='AUTO' → Dyrygent woła klasyfikuj_rezim() (naprawa martwego kodu, Prawo XV)."""
    from imperium.koloseum.namiestnik import Namiestnik
    from imperium.koloseum.dyrygent import Dyrygent
    from unittest.mock import MagicMock

    # ADX>25 → klasyfikuj_rezim zwraca TREND_STRONG
    wskazniki = {"ADX_14": 30.0, "ATR_DEVIATION": 1.0, "CLOSE": 100.0,
                 "EMA_50": 90.0, "EMA_200": 80.0}

    legatus_mock = MagicMock()
    raport_mock = MagicMock()
    raport_mock.weto = False
    raport_mock.kierunek = "NEUTRAL"  # zatrzyma cykl po Legatusie, ale reżim już ustalony
    raport_mock.pewnosc_agregatu = 0.4
    raport_mock.rezim = "TREND_STRONG"
    raport_mock.powod_weta = ""
    raport_mock.strategie_dopasowane = []
    legatus_mock.fokus.return_value = raport_mock

    engine_mock = MagicMock()
    engine_mock.kapital = 10000.0

    d = Dyrygent(
        legatus=legatus_mock,
        kalkulator=MagicMock(),
        engine=engine_mock,
        wskazniki_provider=lambda _: wskazniki,
        namiestnik=Namiestnik(),
    )

    d.cykl("BTCUSDT", [{"close": 100.0}], rezim="AUTO")
    # Legatus dostał skonkretyzowany reżim, nie "AUTO"
    _, kwargs = legatus_mock.fokus.call_args
    assert kwargs.get("rezim") != "AUTO", "rezim AUTO nie został rozwiązany!"
    assert kwargs.get("rezim") in ("TREND_STRONG", "RANGING", "VOLATILE", "NORMAL")


def test_dyrygent_trend_strong_gra():
    """Dyrygent z Namiestnikiem: TREND_STRONG → tryb filtr aktywny."""
    from imperium.koloseum.namiestnik import Namiestnik
    from imperium.koloseum.dyrygent import Dyrygent
    from unittest.mock import MagicMock

    wskazniki = {"RSI_14": 65.0, "CLOSE": 100.0, "ATR_14": 2.0}

    legatus_mock = MagicMock()
    raport_mock = MagicMock()
    raport_mock.weto = False
    raport_mock.kierunek = "LONG"
    raport_mock.pewnosc_agregatu = 0.75
    raport_mock.rezim = "TREND_STRONG"
    raport_mock.powod_weta = ""
    raport_mock.strategie_dopasowane = []  # brak strategii → STRATEGIA_BRAK w tryb filtr
    raport_mock.zgodnych_neuronow = 7
    raport_mock.aktywnych_neuronow = 10
    legatus_mock.fokus.return_value = raport_mock

    engine_mock = MagicMock()
    engine_mock.kapital = 10000.0
    kalk_mock = MagicMock()
    kalk_mock.auto_dzwignia.return_value = 10

    d = Dyrygent(
        legatus=legatus_mock,
        kalkulator=kalk_mock,
        engine=engine_mock,
        wskazniki_provider=lambda _: wskazniki,
        namiestnik=Namiestnik(),
    )

    decyzja = d.cykl("BTCUSDT", [{"close": 100.0}], rezim="TREND_STRONG")
    # W tryb filtr bez strategii → STRATEGIA_BRAK
    assert decyzja.etap in ("STRATEGIA_BRAK", "WEJSCIE", "PRETORIANIE_WETO",
                            "ENGINE_ODRZUCIL", "BRAK_CENY")
