"""Testy Kapitol Podgląd (Speculum Probationis) — zero-tokenowy podgląd testu."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia.kapitol_podglad import render_html, _svg_slupki


def test_render_zawiera_spec_i_tytul():
    html = render_html(
        "Test X",
        spec=[("Para", "BTCUSDT"), ("Interwał", "1H")],
        wykresy=[{"tytul": "W1", "jednostka": "ms", "slupki": [("a", 10.0)]}],
        werdykt="OK")
    assert "<!doctype html>" in html.lower()
    assert "Test X" in html
    assert "BTCUSDT" in html and "1H" in html   # spec wyszczególniona
    assert "<svg" in html                        # wykres inline SVG
    assert "OK" in html                          # werdykt


def test_svg_puste_slupki_nie_wywala():
    out = _svg_slupki([], "ms")
    assert "Brak danych" in out and "<svg" not in out


def test_svg_skaluje_do_max():
    # największy słupek ma pełną szerokość obszaru (pw = 900-60-90 = 750)
    out = _svg_slupki([("mały", 25.0), ("duży", 100.0)], "ms/tick")
    assert 'width="750.0"' in out          # duży = 100/100 * 750
    assert "25.00 ms/tick" in out and "100.00 ms/tick" in out


def test_render_escapuje_html():
    html = render_html("T", spec=[("k", "<b>x</b>")], wykresy=[], werdykt=None)
    assert "&lt;b&gt;x&lt;/b&gt;" in html   # brak wstrzyknięcia HTML
    assert "<b>x</b>" not in html


def test_svg_kolor_domyslny_gdy_brak():
    out = _svg_slupki([("a", 5.0)], "j")   # bez koloru → domyślny
    assert "#4c9be3" in out


def test_kazdy_raport_daje_sie_wygenerowac(tmp_path, monkeypatch):
    """Każdy zarejestrowany raport musi się zbudować — także uruchamiany JAKO SKRYPT.

    Zmierzone 2026-07-21: raport `plon_hyginusa` czytający liczby z żywego rejestru padał
    na `ModuleNotFoundError: narzedzia` przy wywołaniu `python narzedzia/kapitol_podglad.py`,
    bo korzeń repo nie jest wtedy na sys.path. Pod pytestem był zielony — czyli test
    sprawdzał tryb, którego Cezar NIE używa."""
    import subprocess
    from narzedzia.kapitol_podglad import _RAPORTY

    korzen = os.path.join(os.path.dirname(__file__), "..")
    for nazwa in _RAPORTY:
        r = subprocess.run(
            [sys.executable, os.path.join("narzedzia", "kapitol_podglad.py"), nazwa],
            cwd=korzen, capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**os.environ, "KAPITOL_NOOPEN": "1"},
        )
        assert r.returncode == 0, f"raport '{nazwa}' padł jako skrypt:\n{r.stderr[-600:]}"
