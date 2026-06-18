"""
META-01 (W-335) — testy informacji wzajemnej / VI (redundancja nieliniowa, Prawo XVI).

Reguła Test-Granic: identyczne/niezależne/stała/za-mało-danych + przypadek nieliniowy
(Pearson ~0 a NMI wysokie) — sedno: łapiemy to, czego Pearson nie widzi.
"""

from imperium.legiony.diagnostyka_korelacji import (
    informacja_wzajemna, nmi, variation_of_information,
    raport_informacji_wzajemnej, _dyskretyzuj, _entropia_shannon,
)


# ── Granice podstawowe ───────────────────────────────────────────────────────

def test_dyskretyzuj_stala_seria_none():
    assert _dyskretyzuj([5.0, 5.0, 5.0]) is None
    assert _dyskretyzuj([]) is None


def test_entropia_stala_zero():
    assert _entropia_shannon([1, 1, 1, 1]) == 0.0


def test_entropia_rownomierna_dodatnia():
    assert _entropia_shannon([0, 1, 2, 3]) > 0


def test_mi_za_malo_danych_none():
    assert informacja_wzajemna([1.0], [2.0]) is None
    assert informacja_wzajemna([1.0, 2.0], [3.0]) is None  # różne długości


def test_mi_stala_seria_none():
    assert informacja_wzajemna([1.0] * 10, [1.0, 2.0, 3.0] * 4) is None


def test_nmi_identyczne_serie_jeden():
    x = [float(i % 5) for i in range(50)]
    assert abs(nmi(x, x) - 1.0) < 1e-9


def test_vi_identyczne_serie_zero():
    x = [float(i % 5) for i in range(50)]
    assert variation_of_information(x, x) < 1e-9


def test_nmi_w_zakresie_0_1():
    import random
    random.seed(7)
    x = [random.gauss(0, 1) for _ in range(200)]
    y = [random.gauss(0, 1) for _ in range(200)]
    v = nmi(x, y)
    assert v is not None and 0.0 <= v <= 1.0


def test_vi_w_zakresie_0_1():
    import random
    random.seed(9)
    x = [random.gauss(0, 1) for _ in range(200)]
    y = [random.gauss(0, 1) for _ in range(200)]
    v = variation_of_information(x, y)
    assert v is not None and 0.0 <= v <= 1.0


def test_niezalezne_nmi_niskie():
    """Dwie niezależne serie losowe → NMI blisko 0 (mało wspólnej informacji)."""
    import random
    random.seed(42)
    x = [random.gauss(0, 1) for _ in range(500)]
    y = [random.gauss(0, 1) for _ in range(500)]
    assert nmi(x, y) < 0.3


# ── SEDNO: redundancja nieliniowa, której Pearson nie widzi ──────────────────

def test_redundancja_nieliniowa_pearson_slepy_nmi_widzi():
    """
    y = |x| (V-kształt). Pearson ~0 (symetryczny), ale y jest w pełni zdeterminowane
    przez x → NMI musi być WYSOKIE. To dokładnie luka, którą zamykamy.
    """
    from imperium.legiony.diagnostyka_korelacji import korelacja_pearson
    x = [float(i) for i in range(-100, 101)]  # -100..100
    y = [abs(xi) for xi in x]
    pear = abs(korelacja_pearson(x, y))
    info = nmi(x, y)
    assert pear < 0.2, f"Pearson powinien być ~0, jest {pear}"
    assert info > 0.4, f"NMI powinno wykryć zależność, jest {info}"


def test_raport_flaguje_ukryta_redundancje():
    x = [float(i) for i in range(-60, 61)]
    serie = {
        "A": x,
        "B": [abs(xi) for xi in x],   # nieliniowo zależne od A
        "C": [float((i * 7) % 11) for i in range(121)],  # inne
    }
    rap = raport_informacji_wzajemnej(serie, prog_nmi=0.4, prog_pearson_liniowy=0.5)
    pary = [w["para"] for w in rap["pary_ukryte_redundantne"]]
    assert "A~B" in pary


def test_raport_struktura_i_zakresy():
    serie = {"A": [float(i % 4) for i in range(40)],
             "B": [float((i + 1) % 4) for i in range(40)]}
    rap = raport_informacji_wzajemnej(serie)
    assert rap["liczba_modulow"] == 2
    assert "wszystkie_pary" in rap
    for w in rap["wszystkie_pary"]:
        assert 0.0 <= w["nmi"] <= 1.0


def test_raport_stale_serie_pomija():
    """Stała seria → MI None → para pominięta (nie crashuje, nie udaje wiedzy)."""
    serie = {"A": [1.0] * 30, "B": [float(i % 3) for i in range(30)]}
    rap = raport_informacji_wzajemnej(serie)
    assert rap["pary_ukryte_redundantne"] == []
