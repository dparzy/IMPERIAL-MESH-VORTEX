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


def test_rozmiary_stylow_wlacznosc():
    """Zasada włączności (W-323b): SCALP/SWING węższe (bez on-chain+Pi), INVEST = pełnia."""
    from imperium.legiony.rejestr import neurony_dla_trybu, wszystkie_neurony
    pelnia = len(wszystkie_neurony())
    assert 0 < len(neurony_dla_trybu("SCALP")) < pelnia
    assert 0 < len(neurony_dla_trybu("SWING")) < pelnia
    # INVEST zawiera on-chain + Pi Cycle → pełny skład (zasada włączności)
    assert len(neurony_dla_trybu("INVEST")) == pelnia


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


def test_onchain_feed_tylko_invest():
    """On-chain wymagające feedu (OC-01..04) tylko INVEST; OC-05 (wash, OHLCV) uniwersalny."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    oc_feed = {"OC-01", "OC-02", "OC-03", "OC-04"}
    scalp = {n.KLUCZ for n in neurony_dla_trybu("SCALP")}
    swing = {n.KLUCZ for n in neurony_dla_trybu("SWING")}
    invest = {n.KLUCZ for n in neurony_dla_trybu("INVEST")}
    assert not (oc_feed & scalp), f"On-chain-feed w SCALP: {oc_feed & scalp}"
    assert not (oc_feed & swing), f"On-chain-feed w SWING: {oc_feed & swing}"
    assert oc_feed <= invest, f"On-chain-feed brakuje w INVEST: {oc_feed - invest}"
    assert "OC-05" in scalp and "OC-05" in swing, "OC-05 (OHLCV wash) winien być uniwersalny"


def test_pi_cycle_tylko_invest():
    """Z-07 Pi Cycle (kill-switch szczytu cyklu, ≥350 barów 1D) tylko INVEST."""
    from imperium.legiony.rejestr import NEURONY_STYLU
    assert NEURONY_STYLU["Z-07"] == ("INVEST",)


def test_momentum_flow_cross_tf():
    """W-323b: X-26 HA Scalper i V-03 CVD są uniwersalne (działają cross-TF, pomiar A/B)."""
    from imperium.legiony.rejestr import neurony_dla_trybu
    for styl in ("SCALP", "SWING", "INVEST"):
        klucze = {n.KLUCZ for n in neurony_dla_trybu(styl)}
        assert "X-26" in klucze and "V-03" in klucze, f"{styl}: brak X-26/V-03 (winny być cross-TF)"


def test_backtest_styl_sygnatura():
    """backtest_portfel akceptuje styl= (W-323) bez błędu sygnaturowego."""
    import inspect
    from imperium.koloseum.backtest import backtest_portfel
    assert "styl" in inspect.signature(backtest_portfel).parameters


def test_scoreboard_merge_sumuje_liczniki():
    """W-323c: scalanie Igrzysk przez sumę liczników daje poprawną accuracy łączną."""
    from imperium.biblioteki.igrzyska import StatystykaNeuronu
    # Para A: 6/10 trafnych; Para B: 4/10 trafnych → łącznie 10/20 = 50%
    a = StatystykaNeuronu(klucz="X-01", tp=6, fp=4, sygnaly=10)
    b = StatystykaNeuronu(klucz="X-01", tp=4, fp=6, sygnaly=10)
    merged = StatystykaNeuronu(klucz="X-01")
    for pole in ("tp", "fp", "sygnaly"):
        setattr(merged, pole, getattr(a, pole) + getattr(b, pole))
    assert merged.tp == 10 and merged.fp == 10
    assert abs(merged.accuracy - 0.5) < 1e-9


def test_zbuduj_legatusa_ze_stylem():
    """zbuduj_legatusa(styl=...) daje dedykowany zestaw, None = pełnia."""
    from imperium.legiony.rejestr import zbuduj_legatusa, neurony_dla_trybu, wszystkie_neurony
    sw = zbuduj_legatusa(styl="SWING", aktywuj_smc=False)
    assert len(sw.roj.neurony) == len(neurony_dla_trybu("SWING"))
    pelny = zbuduj_legatusa(aktywuj_smc=False)
    assert len(pelny.roj.neurony) == len(wszystkie_neurony())
