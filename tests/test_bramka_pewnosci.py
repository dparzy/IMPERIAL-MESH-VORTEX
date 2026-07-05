"""Testy BramkaPewnosciKonformalna (ML-36) + kontrakty opt-in wpięcia."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from imperium.legiony.kalibrator_konformalny import BramkaPewnosciKonformalna


# ── konstrukcja ──────────────────────────────────────────────────────────────

def test_cel_trafnosci_walidacja():
    for zly in (0.0, 1.0, -0.2, 1.3):
        with pytest.raises(ValueError):
            BramkaPewnosciKonformalna(cel_trafnosci=zly)
    with pytest.raises(ValueError):
        BramkaPewnosciKonformalna(max_podniesienie=-0.1)


# ── zachowanie: tylko zaostrza ───────────────────────────────────────────────

def test_bez_obserwacji_podniesienie_zero():
    b = BramkaPewnosciKonformalna(cel_trafnosci=0.55)
    assert b.podniesienie() == 0.0
    assert b.prog_efektywny(0.55) == 0.55   # zero zmiany dopóki brak danych


def test_seria_strat_podnosi_prog():
    b = BramkaPewnosciKonformalna(cel_trafnosci=0.55, gamma=0.1)
    for _ in range(10):
        b.zaktualizuj(wygrana=False)
    assert b.podniesienie() > 0.0
    assert b.prog_efektywny(0.55) > 0.55    # rój wchodzi RZADZIEJ po stratach


def test_wygrane_nie_luzuja_ponizej_bazy():
    b = BramkaPewnosciKonformalna(cel_trafnosci=0.55, gamma=0.1)
    for _ in range(20):
        b.zaktualizuj(wygrana=True)
    # sukcesy: podniesienie klamrowane do 0 — próg NIGDY poniżej bazowego
    assert b.podniesienie() == 0.0
    assert b.prog_efektywny(0.55) == 0.55


def test_prog_efektywny_nigdy_ponizej_bazy_ani_powyzej_095():
    b = BramkaPewnosciKonformalna(cel_trafnosci=0.6, gamma=0.5, max_podniesienie=0.5)
    for _ in range(50):
        b.zaktualizuj(wygrana=False)
    assert b.prog_efektywny(0.6) >= 0.6
    assert b.prog_efektywny(0.9) <= 0.95     # sufit 0.95


def test_max_podniesienie_respektowane():
    b = BramkaPewnosciKonformalna(cel_trafnosci=0.55, gamma=0.9, max_podniesienie=0.08)
    for _ in range(100):
        b.zaktualizuj(wygrana=False)
    assert b.podniesienie() <= 0.08 + 1e-9


def test_powrot_do_bazy_po_odbiciu_trafnosci():
    b = BramkaPewnosciKonformalna(cel_trafnosci=0.5, gamma=0.2)
    for _ in range(10):
        b.zaktualizuj(wygrana=False)
    podniesione = b.podniesienie()
    assert podniesione > 0
    for _ in range(30):
        b.zaktualizuj(wygrana=True)
    assert b.podniesienie() < podniesione     # wraca w stronę bazy gdy trafność rośnie


# ── kontrakty wpięcia (opt-in, domyślnie OFF) ────────────────────────────────

def test_dyrygent_bramka_domyslnie_none():
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
    engine = PaperTradingEngine(kapital_startowy=1000.0, sesja_id="X")
    d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine)
    assert d.bramka_kalibr is None


def test_backtest_ma_flage_kalibruj_prog():
    import inspect
    from imperium.koloseum.backtest import backtest
    assert "kalibruj_prog" in inspect.signature(backtest).parameters
    assert inspect.signature(backtest).parameters["kalibruj_prog"].default is False


def test_konfig_petli_kalibruj_prog_domyslnie_off():
    from imperium.koloseum.petla_live import KonfigPetliLive
    assert KonfigPetliLive(symbole=["BTCUSDT"]).kalibruj_prog is False
