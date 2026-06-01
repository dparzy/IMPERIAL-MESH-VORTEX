"""Testy Igrzysk — scoring neuronów, rangi, Złoty Hełm, integracja z logami."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.igrzyska import (
    Igrzyska, StatystykaNeuronu, okresl_range, _przeciwny, PROG_INFAMII,
)


def test_okresl_range_aquilifer():
    nazwa, mnoznik = okresl_range(0.95)
    assert nazwa == "Aquilifer"
    assert mnoznik == 2.0


def test_okresl_range_tiro():
    nazwa, mnoznik = okresl_range(0.20)
    assert nazwa == "Tiro"
    assert mnoznik == 0.5


def test_accuracy_perfekcyjna():
    stat = StatystykaNeuronu(klucz="X-01")
    for _ in range(10):
        stat.zarejestruj("LONG", "LONG")  # zawsze trafny
    assert stat.accuracy == 1.0


def test_accuracy_zerowa():
    stat = StatystykaNeuronu(klucz="X-99")
    for _ in range(10):
        stat.zarejestruj("LONG", "SHORT")  # zawsze pudło
    assert stat.accuracy == 0.0


def test_stability_flip_flop():
    stat = StatystykaNeuronu(klucz="X-07")
    kierunki = ["LONG", "SHORT", "LONG", "SHORT", "LONG", "SHORT"]
    for k in kierunki:
        stat.zarejestruj(k, "LONG")
    assert stat.stability < 0.5, "Ciągły flip-flop = niska stabilność"


def test_stability_stala():
    stat = StatystykaNeuronu(klucz="X-06")
    for _ in range(10):
        stat.zarejestruj("LONG", "LONG")
    assert stat.stability == 1.0, "Brak zmian = pełna stabilność"


def test_zloty_helm_dla_najlepszego():
    ig = Igrzyska()
    for _ in range(20):
        ig.zarejestruj_wynik("DOBRY", "LONG", "LONG")     # 100% trafny
        ig.zarejestruj_wynik("SLABY", "LONG", "SHORT")    # 0% trafny
    helm = ig.zloty_helm()
    assert helm["klucz"] == "DOBRY", "Najlepszy neuron dostaje Złoty Hełm"


def test_lista_infamii_lapie_slabych():
    ig = Igrzyska()
    for _ in range(10):
        ig.zarejestruj_wynik("ZDRAJCA", "LONG", "SHORT")  # zawsze pudło
    infamia = ig.lista_infamii()
    assert any(w.klucz == "ZDRAJCA" for w in infamia), "Słaby neuron na Liście Infamii"


def test_nowe_wagi_mapa():
    ig = Igrzyska()
    for _ in range(20):
        ig.zarejestruj_wynik("X-01", "LONG", "LONG")
    wagi = ig.nowe_wagi()
    assert "X-01" in wagi
    assert wagi["X-01"] >= 1.0, "Trafny neuron dostaje mnożnik >= 1.0"


def test_integracja_z_logami():
    """Integracja z ImperiumLog z Pamięci Absolutnej."""
    from imperium.biblioteki.pamiec_absolutna import ImperiumLog, TypLogu
    import json

    sygnal = ImperiumLog(
        log_typ=TypLogu.SYGNAL, sesja_id="test-1", symbol="BTCUSDT",
        interwal="1H", legatus_kierunek="LONG",
        sygnaly_json=json.dumps([
            {"k": "X-01", "d": "LONG", "p": 0.8, "w": 7},
            {"k": "X-99", "d": "SHORT", "p": 0.6, "w": 5},
        ])
    )
    trade = ImperiumLog(
        log_typ=TypLogu.TRADE_CLOSE, sesja_id="test-1", symbol="BTCUSDT",
        interwal="1H", pnl_pct=2.5,  # wygrany LONG
    )

    ig = Igrzyska()
    ig.przetworz_logi([sygnal, trade])

    # X-01 mówił LONG, trade LONG wygrał → trafny
    assert ig.statystyki["X-01"].tp == 1
    # X-99 mówił SHORT, zyskowny był LONG → pudło
    assert ig.statystyki["X-99"].fp == 1


def test_przeciwny():
    assert _przeciwny("LONG") == "SHORT"
    assert _przeciwny("SHORT") == "LONG"
