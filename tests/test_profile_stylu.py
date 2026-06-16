"""
Testy W-323 — profile stylu gry (NEURONY_STYLU + neurony_dla_trybu).

Prawo XXI (Reguła Test-Granic): spójność mapy z kodem (zero sierot/braków),
poprawność filtra, walidacja nieznanego stylu, uniwersalność bezpieczników.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_mapa_pokrywa_wszystkie_neurony():
    """Prawo XXI: każdy z neuronów w kodzie ma wpis w NEURONY_STYLU (zero sierot/braków)."""
    from imperium.legiony.rejestr import raport_profili
    r = raport_profili()
    assert r["sieroty_w_mapie"] == [], f"Sieroty (w mapie, brak w kodzie): {r['sieroty_w_mapie']}"
    assert r["braki_w_mapie"] == [], f"Braki (w kodzie, brak w mapie): {r['braki_w_mapie']}"


def test_kazdy_styl_niepusty_i_mniejszy_od_pelni():
    """Każdy styl ma neurony, ale mniej niż pełne 70 (różnicowanie realne)."""
    from imperium.legiony.rejestr import neurony_dla_trybu, wszystkie_neurony
    pelnia = len(wszystkie_neurony())
    for styl in ("SCALP", "SWING", "INVEST"):
        ile = len(neurony_dla_trybu(styl))
        assert 0 < ile < pelnia, f"{styl}: {ile} neuronów (oczekiwano 0<x<{pelnia})"


def test_wartosci_stylow_tylko_dozwolone():
    """Każda krotka w mapie zawiera wyłącznie SCALP/SWING/INVEST (brak literówek)."""
    from imperium.legiony.rejestr import NEURONY_STYLU, WSZYSTKIE_STYLE
    for klucz, style in NEURONY_STYLU.items():
        assert len(style) >= 1, f"{klucz}: pusta krotka stylów"
        for s in style:
            assert s in WSZYSTKIE_STYLE, f"{klucz}: nieznany styl {s!r}"


def test_nieznany_styl_rzuca():
    """Granica: nieznany styl → ValueError, nie cichy pusty wynik."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    for zly in ("XXX", "scal", "", "DAYTRADE"):
        try:
            neurony_dla_trybu(zly)
            assert False, f"Styl {zly!r} powinien rzucić ValueError"
        except ValueError:
            pass


def test_styl_case_insensitive():
    """'swing'/'SWING'/'Swing' dają ten sam zestaw (normalizacja)."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    a = {n.KLUCZ for n in neurony_dla_trybu("swing")}
    b = {n.KLUCZ for n in neurony_dla_trybu("SWING")}
    c = {n.KLUCZ for n in neurony_dla_trybu("Swing")}
    assert a == b == c


def test_bezpieczniki_uniwersalne_we_wszystkich_stylach():
    """Bezpieczniki/anty-manip (Z-01, A-01, N-01) głosują w KAŻDYM stylu."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    uniwersalne = {"Z-01", "A-01", "A-02", "N-01"}
    for styl in ("SCALP", "SWING", "INVEST"):
        klucze = {n.KLUCZ for n in neurony_dla_trybu(styl)}
        brak = uniwersalne - klucze
        assert not brak, f"{styl}: brak uniwersalnych bezpieczników {brak}"


def test_onchain_tylko_invest():
    """On-chain (OC-*) gra TYLKO w INVEST (wolne fundamenty), nie w scalp/swing."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    oc = {"OC-01", "OC-02", "OC-03", "OC-04", "OC-05"}
    scalp = {n.KLUCZ for n in neurony_dla_trybu("SCALP")}
    swing = {n.KLUCZ for n in neurony_dla_trybu("SWING")}
    invest = {n.KLUCZ for n in neurony_dla_trybu("INVEST")}
    assert not (oc & scalp), f"On-chain w SCALP: {oc & scalp}"
    assert not (oc & swing), f"On-chain w SWING: {oc & swing}"
    assert oc <= invest, f"On-chain brakuje w INVEST: {oc - invest}"


def test_pi_cycle_tylko_invest():
    """Z-07 Pi Cycle (kill-switch szczytu cyklu, ≥350 barów 1D) tylko INVEST."""
    from imperium.legiony.rejestr import NEURONY_STYLU
    assert NEURONY_STYLU["Z-07"] == ("INVEST",)


def test_scalp_oscylatory_obecne():
    """X-26 HA Scalper i V-03 CVD (czysty scalp) są w SCALP, nie w INVEST."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    scalp = {n.KLUCZ for n in neurony_dla_trybu("SCALP")}
    invest = {n.KLUCZ for n in neurony_dla_trybu("INVEST")}
    assert "X-26" in scalp and "V-03" in scalp
    assert "X-26" not in invest and "V-03" not in invest


def test_zbuduj_legatusa_ze_stylem():
    """zbuduj_legatusa(styl=...) daje dedykowany zestaw, None = pełnia."""
    from imperium.legiony.rejestr import zbuduj_legatusa, neurony_dla_trybu, wszystkie_neurony
    sw = zbuduj_legatusa(styl="SWING", aktywuj_smc=False)
    assert len(sw.roj.neurony) == len(neurony_dla_trybu("SWING"))
    pelny = zbuduj_legatusa(aktywuj_smc=False)
    assert len(pelny.roj.neurony) == len(wszystkie_neurony())
