"""Testy generatora godła Imperium (W-342)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import xml.dom.minidom as minidom
from imperium.swiatynie.godlo import (
    generuj_godlo, generuj_favicon, zapisz_godlo, _wir_sciezka, _siatka_wezlow,
)


def test_godlo_zwraca_svg():
    svg = generuj_godlo()
    assert svg.startswith("<?xml")
    assert "<svg" in svg
    assert "</svg>" in svg


def test_godlo_jest_poprawnym_xml():
    """SVG musi być parsowalnym XML (inaczej przeglądarka go odrzuci)."""
    svg = generuj_godlo()
    minidom.parseString(svg)  # rzuci wyjątek jeśli niepoprawny


def test_godlo_zawiera_podpis():
    svg = generuj_godlo(podpis=True)
    assert "IMPERIAL MESH VORTEX" in svg


def test_godlo_bez_podpisu():
    svg = generuj_godlo(podpis=False)
    assert "IMPERIAL MESH VORTEX" not in svg


def test_favicon_jest_mniejszy_i_bez_podpisu():
    svg = generuj_favicon(rozmiar=64)
    assert 'width="64"' in svg
    assert "IMPERIAL MESH VORTEX" not in svg
    minidom.parseString(svg)


def test_rozmiar_respektowany():
    svg = generuj_godlo(rozmiar=512)
    assert 'width="512"' in svg
    assert 'height="512"' in svg


def test_wir_sciezka_ma_punkty():
    sciezka = _wir_sciezka(100, 100, 50, obroty=2.0, punktow=40)
    assert sciezka.startswith("M")
    assert "L" in sciezka
    # 41 punktów (0..40)
    assert sciezka.count(",") == 41


def test_siatka_ma_wezly_i_polaczenia():
    siatka = _siatka_wezlow(100, 100, 50, wezlow=8)
    assert siatka.count("<circle") == 8       # 8 węzłów
    assert "<line" in siatka                    # połączenia


def test_zapisz_godlo_tworzy_plik():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        sciezka = os.path.join(d, "test_godlo.svg")
        wynik = zapisz_godlo(sciezka)
        assert wynik == sciezka
        assert os.path.exists(sciezka)
        with open(sciezka, encoding="utf-8") as f:
            tresc = f.read()
        minidom.parseString(tresc)


def test_godla_w_docs_istnieja():
    """Godło i favicon muszą być w docs/ (commited artifact)."""
    root = os.path.join(os.path.dirname(__file__), "..")
    assert os.path.exists(os.path.join(root, "docs", "godlo_imperium.svg"))
    assert os.path.exists(os.path.join(root, "docs", "godlo_favicon.svg"))
