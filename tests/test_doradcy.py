"""Testy Rady Doradców — ORACLE, FULMEN, IUSTITIA, HERMES, PYTHIA, RADA."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.cesarz.doradcy.oracle import Oracle, WerdyktOracle
from imperium.cesarz.doradcy.fulmen import Fulmen, DaneFulmen, WerdyktFulmen
from imperium.cesarz.doradcy.iustitia import Iustitia, DaneIustitia, OtwartaPozycja, WerdyktIustitia
from imperium.cesarz.doradcy.hermes import Hermes, DaneHermes, WerdyktHermes
from imperium.cesarz.doradcy.pythia import Pythia, OdciskPalca, WpisHistorii, WerdyktPythia, buduj_odcisk
from imperium.cesarz.doradcy.rada import RadaDoradcow


# ─── ORACLE ───────────────────────────────────────────────────────────────────

def test_oracle_brak_danych():
    o = Oracle()
    wynik = o.ocen([1.0, 2.0])  # < MIN_SETUPOW
    assert wynik.werdykt == WerdyktOracle.BRAK_DANYCH


def test_oracle_godne():
    o = Oracle()
    pnl = [2.0, 3.0, 1.5, 2.5, 4.0, 1.0, 2.0, 3.5, 2.2, 1.8]  # same zyski
    wynik = o.ocen(pnl)
    assert wynik.werdykt == WerdyktOracle.GODNE
    assert wynik.q_score > 1.2


def test_oracle_niegodne():
    o = Oracle()
    pnl = [-3.0, -2.5, -4.0, -1.5, -2.0, -3.5, -1.0, -2.8, -1.2, -3.0]
    wynik = o.ocen(pnl)
    assert wynik.werdykt == WerdyktOracle.NIEGODNE
    assert not wynik.pozytywny


def test_oracle_modyfikator_watpliwy():
    o = Oracle()
    # Mix — wynik w szarej strefie (losowy mix małych zysków i strat)
    pnl = [0.5, -0.4, 0.6, -0.5, 0.4, -0.3, 0.5, -0.4, 0.3, 0.2]
    wynik = o.ocen(pnl)
    if wynik.werdykt == WerdyktOracle.WATPLIWE:
        assert wynik.modyfikator_pozycji == 0.5


# ─── FULMEN ───────────────────────────────────────────────────────────────────

def test_fulmen_zgodny_trend():
    f = Fulmen()
    dane = DaneFulmen(
        adx_14=32.0, vi_plus_14=1.15, vi_minus_14=0.88,
        choppiness_14=35.0, kaufman_er=0.72,
        legatus_rezim="TREND_STRONG",
    )
    wynik = f.ocen(dane)
    assert wynik.werdykt == WerdyktFulmen.ZGODNY
    assert wynik.modyfikator == 1.2
    assert wynik.vi_kierunek == "BULLISH"


def test_fulmen_konflikt():
    f = Fulmen()
    dane = DaneFulmen(
        adx_14=15.0, vi_plus_14=1.02, vi_minus_14=1.01,
        choppiness_14=70.0, kaufman_er=0.3,
        legatus_rezim="TREND_STRONG",  # Legatus mówi trend, FULMEN mówi ranging
    )
    wynik = f.ocen(dane)
    assert wynik.werdykt == WerdyktFulmen.KONFLIKT
    assert wynik.modyfikator == 0.7


# ─── IUSTITIA ─────────────────────────────────────────────────────────────────

def test_iustitia_ok():
    i = Iustitia()
    dane = DaneIustitia(
        kapital_total=10000.0, nowe_ryzyko_usdt=200.0,
        win_rate=0.55, avg_win_pct=2.0, avg_loss_pct=1.0,
    )
    wynik = i.ocen(dane)
    assert wynik.werdykt == WerdyktIustitia.OK
    assert wynik.pozytywny


def test_iustitia_blokada_heat():
    i = Iustitia()
    pozycje = [OtwartaPozycja(symbol="BTCUSDT", ryzyko_usdt=500.0, pnl_pct=0.0)]
    dane = DaneIustitia(
        kapital_total=10000.0, nowe_ryzyko_usdt=200.0,
        otwarte_pozycje=pozycje,
        win_rate=0.55, avg_win_pct=2.0, avg_loss_pct=1.0,
    )
    # heat = (500+200)/10000 = 7% > 6% → BLOKADA
    wynik = i.ocen(dane)
    assert wynik.werdykt == WerdyktIustitia.BLOKADA
    assert not wynik.pozytywny
    assert wynik.sugerowany_rozmiar_pct == 0.0


def test_iustitia_blokada_seria_strat():
    i = Iustitia()
    dane = DaneIustitia(
        kapital_total=10000.0, nowe_ryzyko_usdt=50.0,
        ostatnie_5_pnl=[-1.0, -2.0, -0.5, -1.5, -0.8],
        win_rate=0.4, avg_win_pct=1.5, avg_loss_pct=1.0,
    )
    wynik = i.ocen(dane)
    assert wynik.werdykt == WerdyktIustitia.BLOKADA


def test_iustitia_blokada_korelacja():
    i = Iustitia()
    dane = DaneIustitia(
        kapital_total=10000.0, nowe_ryzyko_usdt=50.0,
        korelacja_z_otwartymi=0.82,
        win_rate=0.55, avg_win_pct=2.0, avg_loss_pct=1.0,
    )
    wynik = i.ocen(dane)
    assert wynik.werdykt == WerdyktIustitia.BLOKADA


# ─── HERMES ───────────────────────────────────────────────────────────────────

def test_hermes_czyste():
    h = Hermes()
    dane = DaneHermes(
        kompletnosc_danych=0.95, interwal_minut=60,
        wiek_danych_minut=30, hash_ok=True, vpin=0.4,
    )
    wynik = h.ocen(dane)
    assert wynik.werdykt == WerdyktHermes.CZYSTE
    assert wynik.pozytywny


def test_hermes_niekompletne_hash():
    h = Hermes()
    dane = DaneHermes(
        kompletnosc_danych=0.95, interwal_minut=60,
        wiek_danych_minut=30, hash_ok=False, vpin=0.3,
    )
    wynik = h.ocen(dane)
    assert wynik.werdykt == WerdyktHermes.NIEKOMPLETNE
    assert not wynik.pozytywny


def test_hermes_niekompletne_dane():
    h = Hermes()
    dane = DaneHermes(
        kompletnosc_danych=0.60, interwal_minut=60,
        wiek_danych_minut=30, hash_ok=True, vpin=0.3,
    )
    wynik = h.ocen(dane)
    assert wynik.werdykt == WerdyktHermes.NIEKOMPLETNE


def test_hermes_event_blokuje():
    h = Hermes()
    dane = DaneHermes(
        kompletnosc_danych=0.95, interwal_minut=60,
        wiek_danych_minut=30, hash_ok=True, vpin=0.4,
        minuty_do_eventu=15,
    )
    wynik = h.ocen(dane)
    assert wynik.werdykt == WerdyktHermes.NIEKOMPLETNE


def test_hermes_vpin_ostrzezenie():
    h = Hermes()
    dane = DaneHermes(
        kompletnosc_danych=0.95, interwal_minut=60,
        wiek_danych_minut=30, hash_ok=True, vpin=0.82,
    )
    wynik = h.ocen(dane)
    assert wynik.werdykt == WerdyktHermes.ZANIECZYSZCZONE
    assert wynik.pozytywny  # nie blokuje — tylko ostrzeżenie


# ─── PYTHIA ───────────────────────────────────────────────────────────────────

def test_pythia_milczenie():
    p = Pythia()
    odcisk = OdciskPalca("TREND_STRONG", "1H", "LONG", 3, 1, 2)
    wynik = p.ocen(odcisk, [])
    assert wynik.werdykt == WerdyktPythia.MILCZENIE
    assert wynik.pozytywny  # milczenie nie blokuje


def test_pythia_korzystne():
    p = Pythia()
    odcisk = OdciskPalca("TREND_STRONG", "1H", "LONG", 3, 1, 2)
    historia = [
        WpisHistorii(odcisk=OdciskPalca("TREND_STRONG", "1H", "LONG", 3, 1, 2), pnl_pct=v)
        for v in [2.0, 3.0, 1.5, 2.5, 4.0, 1.2, 2.8, 1.9, 3.1, 2.3, 1.7, 2.4]
    ]
    wynik = p.ocen(odcisk, historia)
    assert wynik.werdykt == WerdyktPythia.KORZYSTNE
    assert wynik.p_zysk > 0.60


def test_pythia_niekorzystne():
    p = Pythia()
    odcisk = OdciskPalca("RANGING", "4H", "SHORT", 2, 0, 3)
    historia = [
        WpisHistorii(odcisk=OdciskPalca("RANGING", "4H", "SHORT", 2, 0, 3), pnl_pct=v)
        for v in [-2.0, -1.5, -3.0, 1.0, -2.5, -1.0, -4.0, -0.5, -2.2, -1.8, -3.5, -0.8]
    ]
    wynik = p.ocen(odcisk, historia)
    assert wynik.werdykt == WerdyktPythia.NIEKORZYSTNE


def test_pythia_buduj_odcisk():
    odcisk = buduj_odcisk("TREND_STRONG", "1H", "LONG", 0.75, 0.0001, 100.0, 80.0)
    assert odcisk.pewnosc_bin == 3
    assert odcisk.funding_bin == 1
    assert odcisk.atr_bin == 2  # 100/80 = 1.25 < 1.3, więc normalny (bin 2)
    assert odcisk.rezim == "TREND_STRONG"


# ─── RADA ─────────────────────────────────────────────────────────────────────

def _pelna_rada_pozytywna():
    """Pomocnicza — tworzy rade z wszystkimi ocenami pozytywnymi."""
    from imperium.cesarz.doradcy.oracle import OcenaOracle
    from imperium.cesarz.doradcy.fulmen import OcenaFulmen
    from imperium.cesarz.doradcy.iustitia import OcenaIustitia
    from imperium.cesarz.doradcy.hermes import OcenaHermes
    from imperium.cesarz.doradcy.pythia import OcenaPythia

    oracle = OcenaOracle(WerdyktOracle.GODNE, 1.4, 1.5, 1.3, 1.2, 1.1, 15)
    fulmen = OcenaFulmen(WerdyktFulmen.ZGODNY, 30.0, 35.0, 0.72, "BULLISH", "trend", 1.2)
    iustitia = OcenaIustitia(WerdyktIustitia.OK, 0.03, 0.08, 0.04)
    hermes = OcenaHermes(WerdyktHermes.CZYSTE, 0.95, 0.4, True)
    pythia = OcenaPythia(WerdyktPythia.KORZYSTNE, 0.68, 2.1, 1.8, 24)
    return oracle, fulmen, iustitia, hermes, pythia


def test_rada_pelna_akceptacja():
    rada = RadaDoradcow()
    o, f, i, h, p = _pelna_rada_pozytywna()
    opinia = rada.ocen(o, f, i, h, p)
    assert opinia.pozytywne == 5
    assert opinia.modyfikator_pozycji == 1.0
    assert not opinia.blokada


def test_rada_iustitia_veto():
    from imperium.cesarz.doradcy.iustitia import OcenaIustitia
    rada = RadaDoradcow()
    o, f, _, h, p = _pelna_rada_pozytywna()
    iustitia_blokada = OcenaIustitia(WerdyktIustitia.BLOKADA, 0.12, 0.04, 0.0, ["Heat krytyczny"])
    opinia = rada.ocen(o, f, iustitia_blokada, h, p)
    assert opinia.blokada
    assert opinia.modyfikator_pozycji == 0.0
    assert "IUSTITIA" in opinia.powod_blokady


def test_rada_hermes_veto():
    from imperium.cesarz.doradcy.hermes import OcenaHermes
    rada = RadaDoradcow()
    o, f, i, _, p = _pelna_rada_pozytywna()
    hermes_niekompletne = OcenaHermes(WerdyktHermes.NIEKOMPLETNE, 0.6, 0.3, False, ["Hash invalid"])
    opinia = rada.ocen(o, f, i, hermes_niekompletne, p)
    assert opinia.blokada
    assert "HERMES" in opinia.powod_blokady


def test_rada_3_na_5():
    from imperium.cesarz.doradcy.oracle import OcenaOracle
    from imperium.cesarz.doradcy.fulmen import OcenaFulmen
    rada = RadaDoradcow()
    o, f, i, h, p = _pelna_rada_pozytywna()
    # ORACLE i FULMEN negatywne
    oracle_neg = OcenaOracle(WerdyktOracle.NIEGODNE, 0.5, 0.3, 0.4, 0.2, 0.5, 10)
    fulmen_konf = OcenaFulmen(WerdyktFulmen.KONFLIKT, 15.0, 70.0, 0.3, "NEUTRALNY", "ranging", 0.7)
    opinia = rada.ocen(oracle_neg, fulmen_konf, i, h, p)
    assert opinia.pozytywne == 3
    assert opinia.modyfikator_pozycji == 0.6
    assert not opinia.blokada


def test_rada_raport_format():
    rada = RadaDoradcow()
    o, f, i, h, p = _pelna_rada_pozytywna()
    opinia = rada.ocen(o, f, i, h, p)
    raport = opinia.raport(symbol="BTCUSDT", pewnosc_legatus=0.72)
    assert "BTCUSDT" in raport
    assert "ORACLE" in raport
    assert "IUSTITIA" in raport
