"""Testy DISCIPULUS (narzedzia/ab_ucz_mwu.py) — A/B zamkniętej pętli uczenia.

Reguła Test-Granic (Prawo XXI): każdy PRÓG werdyktu ma test po obu stronach granicy
(p=0.05, minimum par konkluzywnych, Δ=0), bo to progi decydują, czy mechanizm wejdzie
w ścieżkę decyzyjną. Dodatkowo pilnujemy dwóch wad z lekcji poprzednich wacht:
  • klucz cache musi nieść PODPIS KONFIGURACJI (inaczej resume podmienia wyniki),
  • przycinanie serii idzie OD KOŃCA (inaczej portfel miesza bar z 2024 z barem z 2026).
Backtest nie jest tu uruchamiany — testy mają być szybkie i deterministyczne.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.ab_ucz_mwu import (  # noqa: E402
    _MIN_PAR_KONKLUZYWNYCH,
    _zwroty_z_equity,
    klucz_biegu,
    p_dwumianowy,
    portfel_zwrotow,
    statystyki_zbiorcze,
    wczytaj_cache,
    werdykt,
    zapisz_cache,
)


# ── test znaku (dwumianowy dokładny) ──────────────────────────────────────────

def test_p_dwumianowy_brak_roznic_to_jedynka():
    """n=0 → 1.0: brak różnic jest brakiem dowodu, nie dowodem braku."""
    assert p_dwumianowy(0, 0) == 1.0


def test_p_dwumianowy_komplet_wygranych():
    # 10/10 przy rzucie monetą: 2·(1/1024) = 0.001953125
    assert abs(p_dwumianowy(10, 10) - 2 / 1024) < 1e-12


def test_p_dwumianowy_remis_to_jedynka():
    assert p_dwumianowy(5, 10) == 1.0


def test_p_dwumianowy_symetryczny():
    """Test dwustronny nie może faworyzować kierunku."""
    for n in (7, 12, 15):
        for k in range(n + 1):
            assert abs(p_dwumianowy(k, n) - p_dwumianowy(n - k, n)) < 1e-12


def test_p_dwumianowy_granica_005():
    """GRANICA: 8/10 daje p>0.05, 9/10 daje p<0.05 — bramka musi je rozróżniać."""
    assert p_dwumianowy(8, 10) > 0.05
    assert p_dwumianowy(9, 10) < 0.05


def test_p_dwumianowy_odrzuca_k_poza_zakresem():
    try:
        p_dwumianowy(5, 3)
    except ValueError:
        return
    raise AssertionError("k>n powinno podnieść ValueError")


# ── zwroty i portfel ──────────────────────────────────────────────────────────

def test_zwroty_z_equity_dlugosc_i_wartosci():
    z = _zwroty_z_equity([100.0, 110.0, 99.0])
    assert len(z) == 2 and abs(z[0] - 0.1) < 1e-12 and abs(z[1] + 0.1) < 1e-12
    assert _zwroty_z_equity([100.0]) == []
    assert _zwroty_z_equity([]) == []


def test_zwroty_z_equity_zerowy_kapital_nie_wywala():
    assert _zwroty_z_equity([0.0, 5.0]) == [0.0]


def test_portfel_usrednia_pary():
    w = [{"zwroty_off": [0.0, 0.2], "zwroty_on": [0.0, 0.4]},
         {"zwroty_off": [0.0, 0.0], "zwroty_on": [0.0, 0.0]}]
    off, on, dl = portfel_zwrotow(w)
    assert dl == 2
    assert off == [0.0, 0.1] and on == [0.0, 0.2]


def test_portfel_przycina_od_konca():
    """Krótsza para wyznacza długość, a z dłuższej bierzemy NAJŚWIEŻSZE bary."""
    w = [{"zwroty_off": [9.0, 9.0, 0.2], "zwroty_on": [9.0, 9.0, 0.2]},
         {"zwroty_off": [0.4], "zwroty_on": [0.4]}]
    off, on, dl = portfel_zwrotow(w)
    assert dl == 1
    # gdyby przycinało od początku, wyszłoby (9.0+0.4)/2 = 4.7
    assert abs(off[0] - 0.3) < 1e-12 and abs(on[0] - 0.3) < 1e-12


def test_portfel_bez_serii_zwraca_pustke():
    assert portfel_zwrotow([{"zwroty_off": [], "zwroty_on": []}]) == ([], [], 0)


def test_statystyki_pustej_listy_krzycza_zamiast_dzielic_przez_zero():
    """GRANICA (recenzja 2026-07-29): brak par to błąd wołającego, nie wynik —
    ValueError z nazwą problemu bije ZeroDivisionError z wnętrza średniej."""
    try:
        statystyki_zbiorcze([], n_prob=4)
    except ValueError as e:
        assert "brak par" in str(e)
        return
    raise AssertionError("pusta lista powinna podnieść ValueError")


# ── klucz cache (podpis konfiguracji) ─────────────────────────────────────────

def test_klucz_rozroznia_kazdy_wymiar_konfiguracji():
    baza = klucz_biegu("BTC.csv", "4h", "agregat", 250, 400, 1000)
    warianty = [
        klucz_biegu("BTC.csv", "1H", "agregat", 250, 400, 1000),
        klucz_biegu("BTC.csv", "4h", "filtr", 250, 400, 1000),
        klucz_biegu("BTC.csv", "4h", "agregat", 300, 400, 1000),
        klucz_biegu("BTC.csv", "4h", "agregat", 250, 500, 1000),
        klucz_biegu("BTC.csv", "4h", "agregat", 250, 400, 600),
    ]
    assert len(set(warianty)) == len(warianty)
    assert baza not in warianty


# ── cache ─────────────────────────────────────────────────────────────────────

def test_cache_zapis_i_odczyt(tmp_path=None):
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        sciezka = Path(d) / "podkatalog" / "cache.json"
        zapisz_cache({"k": {"ret_off": 0.1}}, sciezka)
        assert wczytaj_cache(sciezka) == {"k": {"ret_off": 0.1}}


def test_uszkodzony_cache_nie_wywraca_biegu():
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as d:
        sciezka = Path(d) / "cache.json"
        sciezka.write_text("{to nie jest json", encoding="utf-8")
        assert wczytaj_cache(sciezka) == {}
        # lista też nie jest mapą wyników — ma dać pustkę, nie wybuch
        sciezka.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        assert wczytaj_cache(sciezka) == {}


def test_brak_pliku_cache_to_pusty_slownik():
    from pathlib import Path
    assert wczytaj_cache(Path("nie_ma_takiego_pliku_ab_ucz_mwu.json")) == {}


# ── werdykt (progi) ───────────────────────────────────────────────────────────

def _st(**kw):
    baza = {"par": 10, "rozne": 10, "lepsze": 9, "delta": 0.05, "p_znak": 0.01,
            "baza_pelna": True,
            "dsr_on": {"ok": True, "dsr": 0.97}, "pbo": {"ok": True, "pbo": 0.05}}
    baza.update(kw)
    return baza


def test_werdykt_bez_wplywu_to_alarm_nie_remis():
    tok, zdanie = werdykt(_st(rozne=0))
    assert tok == "BEZ_WPLYWU"
    assert "Prawo XV" in zdanie


def test_werdykt_bez_wplywu_nie_pada_z_malej_proby():
    """GRANICA (recenzja 2026-07-29): alarm o martwym mechanizmie wymaga PRÓBY.
    Jedna para bez różnicy to brak dowodu, nie dowód martwoty."""
    tok, zdanie = werdykt(_st(par=1, rozne=0, lepsze=0))
    assert tok == "NIEKONKLUZYWNE"
    assert "nie zmienił ani jednej decyzji" in zdanie   # informacja zostaje, alarm nie


def test_werdykt_niepelna_baza_zawsze_niekonkluzywna():
    """Gdy ŻADNA para nie ma progu trade'ów, liczby wolno pokazać — ale nie wolno
    z nich orzekać; inaczej fallback odtwarza wadę, którą próg miał wykluczyć."""
    tok, zdanie = werdykt(_st(baza_pelna=False))
    assert tok == "NIEKONKLUZYWNE"
    assert "anegdota" in zdanie


def test_werdykt_granica_minimum_par():
    """GRANICA: par < minimum → NIEKONKLUZYWNE; dokładnie minimum → już sądzimy."""
    assert werdykt(_st(par=_MIN_PAR_KONKLUZYWNYCH - 1,
                       rozne=_MIN_PAR_KONKLUZYWNYCH - 1,
                       lepsze=_MIN_PAR_KONKLUZYWNYCH - 1))[0] == "NIEKONKLUZYWNE"
    assert werdykt(_st(par=_MIN_PAR_KONKLUZYWNYCH))[0] != "NIEKONKLUZYWNE"


def test_werdykt_granica_delty_zero():
    """GRANICA: Δ=0 przy istniejących różnicach to NIE jest 'pomaga'."""
    assert werdykt(_st(delta=0.0))[0] == "SZKODZI"
    assert werdykt(_st(delta=-0.01))[0] == "SZKODZI"
    assert werdykt(_st(delta=1e-9))[0] == "POMAGA"


def test_werdykt_pomaga_wymaga_wszystkich_bramek():
    assert werdykt(_st())[0] == "POMAGA"


def test_werdykt_granica_p_005():
    """GRANICA: p=0.05 NIE przechodzi (wymagane <0.05), p tuż poniżej przechodzi."""
    tok, zdanie = werdykt(_st(p_znak=0.05))
    assert tok == "SLABE" and "test znaku" in zdanie
    assert werdykt(_st(p_znak=0.0499))[0] == "POMAGA"


def test_werdykt_slabe_gdy_dsr_lub_pbo_czerwone():
    tok, zdanie = werdykt(_st(dsr_on={"ok": False, "dsr": 0.61}))
    assert tok == "SLABE" and "DSR" in zdanie
    tok, zdanie = werdykt(_st(pbo={"ok": False, "pbo": 0.44}))
    assert tok == "SLABE" and "PBO" in zdanie


def test_werdykt_slabe_wymienia_wszystkie_braki():
    """Raport ma pokazać KOMPLET powodów, nie pierwszy z brzegu."""
    _, zdanie = werdykt(_st(p_znak=0.4, dsr_on={"ok": False, "dsr": 0.2},
                            pbo={"ok": False, "pbo": 0.5}))
    assert "test znaku" in zdanie and "DSR" in zdanie and "PBO" in zdanie
