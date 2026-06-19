"""Testy Igrzysk — scoring neuronów, rangi, Złoty Hełm, integracja z logami."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.igrzyska import (
    Igrzyska, StatystykaNeuronu, okresl_range, _przeciwny,
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


# ── Prawo XXIII — Niezawodność Warunkowa per-reżim ────────────────────────────

def test_rezim_stat_tracking():
    """Reżim jest trackowany osobno w stats_per_rezim."""
    ig = Igrzyska()
    ig.zarejestruj_wynik("X-01", "LONG", "LONG", rezim="TREND_STRONG")
    ig.zarejestruj_wynik("X-01", "LONG", "LONG", rezim="TREND_STRONG")
    ig.zarejestruj_wynik("X-01", "LONG", "SHORT", rezim="RANGING")
    stat = ig.statystyki["X-01"]
    assert "TREND_STRONG" in stat.stats_per_rezim
    assert stat.stats_per_rezim["TREND_STRONG"].tp == 2
    assert stat.stats_per_rezim["TREND_STRONG"].total == 2
    assert "RANGING" in stat.stats_per_rezim
    assert stat.stats_per_rezim["RANGING"].tp == 0
    assert stat.stats_per_rezim["RANGING"].total == 1


def test_niezawodnosc_per_rezim_min_probka():
    """Reżimy z < 3 próbkami są pomijane w raporcie (szum)."""
    ig = Igrzyska()
    # 2 próbki w TREND_STRONG — poniżej progu
    ig.zarejestruj_wynik("X-02", "LONG", "LONG", rezim="TREND_STRONG")
    ig.zarejestruj_wynik("X-02", "LONG", "LONG", rezim="TREND_STRONG")
    # 3 próbki w RANGING — powyżej progu
    for _ in range(3):
        ig.zarejestruj_wynik("X-02", "SHORT", "SHORT", rezim="RANGING")
    raport = ig.niezawodnosc_per_rezim()
    assert "X-02" in raport
    assert "TREND_STRONG" not in raport["X-02"]   # za mało próbek
    assert "RANGING" in raport["X-02"]
    assert raport["X-02"]["RANGING"]["accuracy"] == 1.0


def test_najlepszy_rezim():
    """Najlepszy reżim = reżim z najwyższą accuracy (min 3 próbki)."""
    ig = Igrzyska()
    # TREND_STRONG: 4/4 = 100%
    for _ in range(4):
        ig.zarejestruj_wynik("X-03", "LONG", "LONG", rezim="TREND_STRONG")
    # RANGING: 1/4 = 25%
    ig.zarejestruj_wynik("X-03", "LONG", "LONG", rezim="RANGING")
    for _ in range(3):
        ig.zarejestruj_wynik("X-03", "LONG", "SHORT", rezim="RANGING")
    ranking = ig.ranking()
    wpis = next(w for w in ranking if w["klucz"] == "X-03")
    assert wpis["najlepszy_rezim"] == "TREND_STRONG"


def test_mnozniki_warunkowe_bonus():
    """Neuron z accuracy >=70% w danym reżimie dostaje bonus x1.2."""
    ig = Igrzyska()
    # Neuron X-04: 8/10 = 80% w TREND_STRONG
    for _ in range(8):
        ig.zarejestruj_wynik("X-04", "LONG", "LONG", rezim="TREND_STRONG")
    for _ in range(2):
        ig.zarejestruj_wynik("X-04", "LONG", "SHORT", rezim="TREND_STRONG")
    bazowy = ig.nowe_wagi()["X-04"]
    warunkowy = ig.mnozniki_warunkowe("TREND_STRONG")["X-04"]
    assert warunkowy == round(bazowy * 1.2, 3)


def test_mnozniki_warunkowe_kara():
    """Neuron z accuracy <40% w danym reżimie dostaje karę x0.8."""
    ig = Igrzyska()
    # Neuron X-05: 1/4 = 25% w RANGING
    ig.zarejestruj_wynik("X-05", "LONG", "LONG", rezim="RANGING")
    for _ in range(3):
        ig.zarejestruj_wynik("X-05", "LONG", "SHORT", rezim="RANGING")
    bazowy = ig.nowe_wagi()["X-05"]
    warunkowy = ig.mnozniki_warunkowe("RANGING")["X-05"]
    assert warunkowy == round(bazowy * 0.8, 3)


def test_mnozniki_warunkowe_bez_danych_rezimu():
    """Neuron bez danych per-reżim dostaje bazowy mnożnik (bez zmian)."""
    ig = Igrzyska()
    # Rejestracja BEZ rezim
    for _ in range(5):
        ig.zarejestruj_wynik("X-06", "LONG", "LONG")
    bazowy = ig.nowe_wagi()["X-06"]
    warunkowy = ig.mnozniki_warunkowe("TREND_STRONG")["X-06"]
    assert warunkowy == bazowy


def test_bez_rezim_nie_crashuje():
    """zarejestruj_wynik bez rezim=None nie crashuje — backward compatible."""
    ig = Igrzyska()
    ig.zarejestruj_wynik("X-07", "LONG", "LONG")  # brak rezim — OK
    assert "X-07" in ig.statystyki
    assert ig.statystyki["X-07"].stats_per_rezim == {}


# ── W-352: Persystencja cross-session ─────────────────────────────────────────

def test_igrzyska_zapisz_wczytaj_roundtrip():
    """Statystyki przeżywają zapis → wczytaj → rangi identyczne."""
    import tempfile, os
    ig = Igrzyska()
    for _ in range(8):
        ig.zarejestruj_wynik("X-01", "LONG", "LONG", rezim="TREND_STRONG")
    for _ in range(2):
        ig.zarejestruj_wynik("X-01", "SHORT", "LONG", rezim="TREND_STRONG")
    ranking_przed = ig.ranking()[0]
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        sciezka = f.name
    try:
        ig.zapisz(sciezka)
        ig2 = Igrzyska()
        ig2.wczytaj(sciezka)
        ranking_po = ig2.ranking()[0]
        assert ranking_po["klucz"] == ranking_przed["klucz"]
        assert abs(ranking_po["wynik"] - ranking_przed["wynik"]) < 1e-6
        assert "TREND_STRONG" in ig2.statystyki["X-01"].stats_per_rezim
    finally:
        os.unlink(sciezka)


def test_igrzyska_wczytaj_nieistniejacy_plik_nie_crashuje():
    """Wczytanie nieistniejącego pliku → puste statystyki (nie crash)."""
    ig = Igrzyska()
    ig.wczytaj("/tmp/nieistniejacy_igrzyska_8324982.json")
    assert ig.statystyki == {}


def test_igrzyska_akumuluje_po_wczytaniu():
    """Nowe wyniki dokładają się do wczytanej historii."""
    import tempfile, os
    ig = Igrzyska()
    for _ in range(6):
        ig.zarejestruj_wynik("X-03", "LONG", "LONG")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        sciezka = f.name
    try:
        ig.zapisz(sciezka)
        ig2 = Igrzyska()
        ig2.wczytaj(sciezka)
        ig2.zarejestruj_wynik("X-03", "LONG", "LONG")
        assert ig2.statystyki["X-03"].sygnaly == 7
    finally:
        os.unlink(sciezka)
