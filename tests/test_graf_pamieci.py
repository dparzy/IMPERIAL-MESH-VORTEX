"""
Testy Grafu Pamięci (W8 — połączenia neuronów, W-360 v8).

Weryfikuje:
  • zbuduj_graf() — węzły + krawędzie współwystąpień + okno czasowe,
  • polaczenia() — sąsiedzi wg wagi,
  • centralne() — huby (stopień ważony),
  • sciezka() — BFS najkrótsza ścieżka między pojęciami,
  • granice: pusty graf, encja bez połączeń, brak ścieżki, szum odfiltrowany.
"""


from imperium.biblioteki import graf_pamieci as gp


def _graf_z_wpisow(tmp_path, monkeypatch, wpisy, min_waga=1):
    """Buduje graf z podanych (data, tekst) — podmienia źródła na kontrolowane."""
    monkeypatch.setattr(gp, "_zrodla_wpisow", lambda: wpisy)
    plik = tmp_path / "graf.json"
    return gp.zbuduj_graf(plik=plik, min_waga=min_waga), plik


def test_buduj_wezly_i_krawedzie(tmp_path, monkeypatch):
    g, _ = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "numba viterbi wydajność"),
        ("2026-06-02", "numba jump model"),
    ])
    assert g["n_wezlow"] >= 4          # numba, viterbi, wydajność, jump, model
    assert g["n_krawedzi"] >= 1
    assert "numba" in g["wezly"]


def test_polaczenia_wg_wagi(tmp_path, monkeypatch):
    _, plik = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "numba viterbi"),
        ("2026-06-02", "numba viterbi"),       # waga numba-viterbi = 2
        ("2026-06-03", "numba wydajność"),     # waga numba-wydajność = 1
    ])
    poł = gp.polaczenia("numba", plik=plik)
    assert poł[0]["encja"] == "viterbi"        # najwyższa waga pierwsza
    assert poł[0]["waga"] == 2


def test_okno_czasowe_wezla(tmp_path, monkeypatch):
    g, _ = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "kustosz pamięci"),
        ("2026-06-28", "kustosz organ"),
    ])
    assert g["wezly"]["kustosz"]["pierwszy"] == "2026-06-01"
    assert g["wezly"]["kustosz"]["ostatni"] == "2026-06-28"
    assert g["wezly"]["kustosz"]["liczba"] == 2


def test_centralne_huby(tmp_path, monkeypatch):
    _, plik = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "rdzeń alfa beta"),
        ("2026-06-02", "rdzeń gamma delta"),
        ("2026-06-03", "rdzeń epsilon"),
    ])
    huby = gp.centralne(top=3, plik=plik)
    assert huby[0]["encja"] == "rdzeń"         # łączy się ze wszystkim → hub


def test_sciezka_miedzy_pojeciami(tmp_path, monkeypatch):
    _, plik = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "alfa beta"),
        ("2026-06-02", "beta gamma"),
    ])
    s = gp.sciezka("alfa", "gamma", plik=plik)
    assert s == ["alfa", "beta", "gamma"]      # alfa→beta→gamma


def test_sciezka_brak_polaczenia(tmp_path, monkeypatch):
    _, plik = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "alfa beta"),
        ("2026-06-02", "gamma delta"),         # osobny komponent
    ])
    assert gp.sciezka("alfa", "gamma", plik=plik) == []


def test_pusty_graf_nie_wybucha(tmp_path):
    plik = tmp_path / "brak.json"
    assert gp.polaczenia("cokolwiek", plik=plik) == []
    assert gp.centralne(plik=plik) == []
    assert gp.sciezka("a", "b", plik=plik) == []


def test_szum_odfiltrowany(tmp_path, monkeypatch):
    """Słowa-szum (była, brak, przez) NIE stają się węzłami; realne tokeny tak
    (dwa realne słowa → krawędź → węzły zachowane po filtrze izolowanych)."""
    g, _ = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "numba viterbi była zmierzone przez brak rozważyć"),
    ])
    assert "była" not in g["wezly"]
    assert "brak" not in g["wezly"]
    assert "numba" in g["wezly"] and "viterbi" in g["wezly"]


def test_izolowane_wezly_odfiltrowane(tmp_path, monkeypatch):
    """min_waga>1 usuwa krawędzie-szum ORAZ osierocone węzły (niequeryowalne)."""
    g, _ = _graf_z_wpisow(tmp_path, monkeypatch, [
        ("2026-06-01", "alfa beta"),          # krawędź alfa-beta waga 1
        ("2026-06-02", "gamma delta"),        # krawędź gamma-delta waga 1
        ("2026-06-03", "alfa beta"),          # alfa-beta waga 2
    ], min_waga=2)
    # tylko alfa-beta przetrwa (waga 2); gamma/delta to izolowane węzły → usunięte
    assert "alfa" in g["wezly"] and "beta" in g["wezly"]
    assert "gamma" not in g["wezly"] and "delta" not in g["wezly"]


def test_raport_startowy_nie_wybucha(tmp_path):
    plik = tmp_path / "brak.json"
    r = gp.raport_startowy(plik=plik)
    assert "Graf pamięci" in r
