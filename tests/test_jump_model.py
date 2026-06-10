"""
Testy Statistical Jump Model (W-281) — detektor reżimu z karą za skok.
Reguła Test-Granic: λ=0, λ ogromne, za mało barów, zerowa wariancja cechy.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.legiony.jump_model import JumpModel  # noqa: E402

RNG = np.random.default_rng(11)


def _dane_dwurezimowe(n1=120, n2=120):
    """Reżim A: dryf +, niska vol. Reżim B: dryf −, wysoka vol."""
    a = RNG.normal(0.004, 0.01, n1)
    b = RNG.normal(-0.004, 0.03, n2)
    zwroty = np.concatenate([a, b])
    vol = np.concatenate([np.full(n1, 0.01), np.full(n2, 0.03)])
    vol = vol * RNG.normal(1.0, 0.05, n1 + n2)
    cechy = np.column_stack([zwroty, vol])
    return zwroty, cechy


def test_wykrywa_dwa_rezimy():
    """Model odnajduje granicę między reżimami (±10 barów tolerancji)."""
    zwroty, cechy = _dane_dwurezimowe()
    jm = JumpModel(n_stanow=2, kara_skoku=20.0)
    stany = jm.dopasuj(cechy)
    # stan dominujący w 1. połowie ≠ stan dominujący w 2. połowie
    s1 = np.bincount(stany[:100]).argmax()
    s2 = np.bincount(stany[140:]).argmax()
    assert s1 != s2, "dwa reżimy muszą dostać różne stany"
    # mało skoków = trwałość (cała idea jump modelu)
    assert jm.liczba_skokow(stany) <= 6, \
        f"reżimy mają być trwałe, skoków: {jm.liczba_skokow(stany)}"


def test_kara_zero_migocze_kara_duza_usztywnia():
    """Granice λ: λ=0 → dużo skoków (k-means); λ ogromna → zero skoków."""
    _, cechy = _dane_dwurezimowe(80, 80)
    luzny = JumpModel(n_stanow=2, kara_skoku=0.0)
    sztywny = JumpModel(n_stanow=2, kara_skoku=1e6)
    sk_luzny = luzny.liczba_skokow(luzny.dopasuj(cechy))
    sk_sztywny = sztywny.liczba_skokow(sztywny.dopasuj(cechy))
    assert sk_sztywny == 0, "λ→∞ musi dać jeden stan na zawsze"
    assert sk_luzny > sk_sztywny, "λ=0 musi skakać częściej niż λ→∞"


def test_nazwij_stany_bull_bear():
    """Stan o najwyższym średnim zwrocie → BULL, najniższym → BEAR."""
    zwroty, cechy = _dane_dwurezimowe()
    jm = JumpModel(n_stanow=2, kara_skoku=20.0)
    stany = jm.dopasuj(cechy)
    nazwy = jm.nazwij_stany(zwroty, stany)
    assert set(nazwy.values()) == {"BULL", "BEAR"}
    stan_pierwszej_polowy = np.bincount(stany[:100]).argmax()
    assert nazwy[int(stan_pierwszej_polowy)] == "BULL", \
        "reżim z dodatnim dryfem musi być nazwany BULL"


def test_trzy_stany_neutral():
    """3 stany → środkowy dostaje NEUTRAL (konwencja Cortese et al. 2023)."""
    zwroty = np.concatenate([RNG.normal(0.005, 0.01, 80),
                             RNG.normal(0.0, 0.01, 80),
                             RNG.normal(-0.005, 0.01, 80)])
    cechy = np.column_stack([zwroty,
                             np.concatenate([np.full(80, .01), np.full(80, .015),
                                             np.full(80, .02)])])
    jm = JumpModel(n_stanow=3, kara_skoku=15.0)
    stany = jm.dopasuj(cechy)
    nazwy = jm.nazwij_stany(zwroty, stany)
    assert "NEUTRAL" in nazwy.values()
    assert "BULL" in nazwy.values() and "BEAR" in nazwy.values()


def test_za_malo_barow_rzuca():
    """Granica długości: < n_stanow·5 barów → ValueError."""
    jm = JumpModel(n_stanow=3)
    try:
        jm.dopasuj(RNG.normal(0, 1, (10, 2)))
        raise AssertionError("powinno rzucić ValueError")
    except ValueError:
        pass


def test_zerowa_wariancja_cechy_nie_wybucha():
    """Kolumna stała (σ=0) nie produkuje NaN (granica standaryzacji)."""
    _, cechy = _dane_dwurezimowe(60, 60)
    cechy = np.column_stack([cechy, np.ones(len(cechy))])  # martwa cecha
    jm = JumpModel(n_stanow=2, kara_skoku=10.0)
    stany = jm.dopasuj(cechy)
    assert not np.isnan(jm.centroidy).any()
    assert len(stany) == len(cechy)


def test_parametry_graniczne_rzucaja():
    """n_stanow<2 i λ<0 odrzucone na wejściu."""
    try:
        JumpModel(n_stanow=1)
        raise AssertionError("n_stanow=1 powinno rzucić")
    except ValueError:
        pass
    try:
        JumpModel(kara_skoku=-1.0)
        raise AssertionError("λ<0 powinno rzucić")
    except ValueError:
        pass


def test_przypisz_ostatni_nowy_bar():
    """Nowy bar trafia do sensownego stanu po dopasowaniu."""
    zwroty, cechy = _dane_dwurezimowe()
    jm = JumpModel(n_stanow=2, kara_skoku=20.0)
    stany = jm.dopasuj(cechy)
    nazwy = jm.nazwij_stany(zwroty, stany)
    stan_bull = jm.przypisz_ostatni([0.004, 0.01])   # cechy jak reżim BULL
    stan_bear = jm.przypisz_ostatni([-0.004, 0.03])  # cechy jak reżim BEAR
    assert nazwy[stan_bull] == "BULL"
    assert nazwy[stan_bear] == "BEAR"


def test_przypisz_przed_dopasowaniem_rzuca():
    try:
        JumpModel().przypisz_ostatni([0.0, 0.0])
        raise AssertionError("powinno rzucić RuntimeError")
    except RuntimeError:
        pass


def test_determinizm_seed():
    """Ten sam seed → identyczne stany (powtarzalność = Prawo I)."""
    _, cechy = _dane_dwurezimowe()
    s1 = JumpModel(n_stanow=2, kara_skoku=20.0, seed=3).dopasuj(cechy)
    s2 = JumpModel(n_stanow=2, kara_skoku=20.0, seed=3).dopasuj(cechy)
    assert np.array_equal(s1, s2)


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items())
          if k.startswith("test_") and callable(v)]
    bledy = 0
    for nazwa, f in fn:
        try:
            f()
            print(f"  ✅ {nazwa}")
        except Exception as e:
            bledy += 1
            print(f"  ❌ {nazwa}: {e}")
    print(f"\n{len(fn)-bledy}/{len(fn)} zaliczone")
    sys.exit(1 if bledy else 0)
