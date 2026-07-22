"""
Testy Dziennika Nieśmiertelnego (W6) — oś czasu projektu wstrzykiwana na starcie.

Nacisk na ZWIĘZŁOŚĆ startu (odchudzenie 2026-07-10): warstwowość (N pełnych + reszta
jednolinijkowa) i przycinanie jednolinijkowców. Reguła Test-Granic (Prawo XXI): granice
_skroc i granice slice'owania w os_czasu.
"""

import json
import tempfile
from pathlib import Path

from imperium.biblioteki import dziennik_niesmiertelny as dn


def _plik(wpisy):
    d = Path(tempfile.mkdtemp())
    p = d / "dziennik.jsonl"
    p.write_text("".join(json.dumps(w, ensure_ascii=False) + "\n" for w in wpisy),
                 encoding="utf-8")
    return p


def _wpis(i, dlugosc_co=20):
    return {"data": f"2026-06-{(i % 28) + 1:02d}", "sesja": f"s{i:03d}",
            "co": ["x" * dlugosc_co, "drugi punkt"], "decyzje": ["decyzja A"],
            "nastepny": "krok dalej"}


# ── _skroc: granice ──────────────────────────────────────────────────────────

def test_skroc_krotszy_niz_limit_bez_zmian():
    assert dn._skroc("krótki", 110) == "krótki"


def test_skroc_dokladnie_na_granicy():
    t = "a" * 110
    assert dn._skroc(t, 110) == t          # == limit → bez cięcia (nie < )


def test_skroc_o_jeden_dluzszy_ucina():
    r = dn._skroc("a" * 111, 110)
    assert len(r) == 110 and r.endswith("…")


def test_skroc_zwija_biale_znaki():
    assert dn._skroc("linia\npo  spacjach", 110) == "linia po spacjach"


def test_skroc_pusty():
    assert dn._skroc("", 110) == ""


# ── os_czasu: warstwowość i granice ──────────────────────────────────────────

def test_os_pusty_dziennik():
    p = _plik([])
    assert "pusty" in dn.os_czasu(p)


def test_os_wszystkie_widoczne_mimo_warstw():
    """Kluczowa gwarancja Prawa XV: żadna sesja nie znika, choć starsze są zwięzłe."""
    p = _plik([_wpis(i) for i in range(30)])
    out = dn.os_czasu(p, ostatnie=8)
    for i in range(30):
        assert f"2026-06-{(i % 28) + 1:02d}" in out or f"s{i:03d}" not in out
    # 30 wpisów → 8 pełnych + 22 jednolinijkowe
    assert out.count("→ następny:") == 8       # tylko pełne mają „następny"
    assert out.count("   · ") == 22            # starsze jednolinijkowe


def test_os_ostatnie_wieksze_niz_liczba_wpisow():
    """ostatnie=8, a wpisów 3 → wszystkie pełne, brak jednolinijkowców."""
    p = _plik([_wpis(i) for i in range(3)])
    out = dn.os_czasu(p, ostatnie=8)
    assert out.count("→ następny:") == 3 and "   · " not in out


def test_os_ostatnie_zero_wszystkie_jednolinijkowe():
    """Granica slice: ostatnie=0 NIE może dać pełnych (bug [:-0] == [:0])."""
    p = _plik([_wpis(i) for i in range(5)])
    out = dn.os_czasu(p, ostatnie=0)
    assert "→ następny:" not in out and out.count("   · ") == 5


def test_os_jednolinijkowce_przyciete():
    """Długie pierwsze punkty starszych sesji NIE mogą rozdymać startu."""
    wpisy = [{"data": "2026-06-01", "sesja": "stara", "co": ["Z" * 400], "nastepny": ""}]
    wpisy += [_wpis(i) for i in range(8)]      # 8 pełnych, żeby „stara" była jednolinijkowa
    out = dn.os_czasu(_plik(wpisy), ostatnie=8)
    linia_stara = [ln for ln in out.splitlines() if ln.startswith("   · 2026-06-01:")][0]
    assert "…" in linia_stara and len(linia_stara) < 130


def test_os_default_pelne_stala_dodatnia():
    assert dn.DOMYSLNE_PELNE > 0


def test_skroc_maks_ponizej_dwoch_nie_wybucha():
    """Strażnica: maks<2 dałby tekst[:maks-1] == tekst[:-1] (obcięcie od końca)."""
    assert dn._skroc("abcdef", 0).endswith("…")
    assert dn._skroc("abcdef", 1).endswith("…")
    assert len(dn._skroc("abcdef", 0)) == 2      # podniesione do minimum 2


def test_skroc_toleruje_nie_string():
    """Recenzja cubic PR #118: stary/uszkodzony wpis JSONL może mieć pierwszy punkt „co"
    jako liczbę/None/listę — _skroc koercuje przez str(), nie wywala startu sesji."""
    assert dn._skroc(123, 110) == "123"
    assert dn._skroc(None, 110) == "None"
    assert dn._skroc(["x"], 110) == "['x']"


def test_os_czasu_toleruje_co_nie_string():
    """os_czasu nie może paść, gdy pierwszy punkt „co" w jednolinijkowcu nie jest tekstem."""
    wpisy = [{"data": "2026-06-01", "sesja": "zla", "co": [42], "nastepny": ""}]
    wpisy += [_wpis(i) for i in range(8)]
    out = dn.os_czasu(_plik(wpisy), ostatnie=8)
    assert "42" in out          # liczba pokazana jako tekst, bez wyjątku


# ── banner_nastepny (A2 — banner NASTĘPNEGO KROKU na górze startu) ─────────────

def test_banner_pusty_dziennik():
    """Granica: brak wpisów → komunikat o pustym Dzienniku, nie wyjątek."""
    b = dn.banner_nastepny(_plik([]))
    assert "NASTĘPNY KROK" in b and "pusty" in b


def test_banner_z_nastepnym():
    """Banner pokazuje treść „nastepny" ostatniego wpisu + jego sesję."""
    wpisy = [_wpis(0), {"data": "2026-07-19", "sesja": "abc123",
                        "co": ["x"], "nastepny": "uruchomić realny WFO na BTCUSDT 4h"}]
    b = dn.banner_nastepny(_plik(wpisy))
    assert "uruchomić realny WFO na BTCUSDT 4h" in b and "abc123" in b


def test_banner_brak_pola_nastepny():
    """Granica: ostatni wpis bez „nastepny" (albo puste) → jawny znacznik, nie crash."""
    b = dn.banner_nastepny(_plik([{"data": "2026-07-19", "sesja": "s", "co": ["x"]}]))
    assert "brak" in b.lower()


def test_banner_toleruje_nastepny_nie_string():
    """Odporność jak reszta osi: „nastepny" nie-tekst (liczba/None) nie wywala startu."""
    b = dn.banner_nastepny(_plik([{"data": "2026-07-19", "sesja": "s",
                                   "co": ["x"], "nastepny": 42}]))
    assert "42" in b


def test_banner_jednolinijkowy():
    """Banner MUSI być jedną linią (idzie na górę startu) — długi „nastepny" przycięty."""
    b = dn.banner_nastepny(_plik([{"data": "2026-07-19", "sesja": "s",
                                   "co": ["x"], "nastepny": "Z" * 500}]))
    assert "\n" not in b and "…" in b
