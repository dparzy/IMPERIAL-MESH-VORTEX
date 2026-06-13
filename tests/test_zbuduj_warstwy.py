"""
W-304: Fabryka Dyrygent.zbuduj() odblokowuje warstwy adaptacyjne (Prawo XV).

Audyt utraty potencjału wykazał: DriftAdapter, RadaDoradcow, SynapsyRezimowe
i HedgeMWU były wpięte w logikę konstruktora/cyklu, ale produkcyjna fabryka
nigdy ich nie tworzyła → martwe w petla_live. Teraz są opt-in (domyślnie OFF).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def _ma_talib():
    try:
        import talib  # noqa: F401
        return True
    except ImportError:
        return False


def test_zbuduj_domyslnie_warstwy_off():
    """Domyślnie wszystkie warstwy adaptacyjne wyłączone — zero zmian zachowania."""
    if not _ma_talib():
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    assert d.drift_adapter is None
    assert d.rada_doradcow is None
    assert d.legatus.synapsy is None
    assert d.legatus.mwu is None


def test_zbuduj_drift_opt_in():
    """drift=True → DriftAdapter zainstalowany i podpięty."""
    if not _ma_talib():
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False, drift=True)
    assert d.drift_adapter is not None
    assert type(d.drift_adapter).__name__ == "DriftAdapter"


def test_zbuduj_rada_opt_in():
    """rada=True → RadaDoradcow zainstalowana i podpięta."""
    if not _ma_talib():
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False, rada=True)
    assert d.rada_doradcow is not None
    assert type(d.rada_doradcow).__name__ == "RadaDoradcow"


def test_zbuduj_synapsy_opt_in():
    """synapsy=True → Legatus.synapsy ustawiony na SynapsyRezimowe."""
    if not _ma_talib():
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False, synapsy=True)
    assert d.legatus.synapsy is not None
    assert type(d.legatus.synapsy).__name__ == "SynapsyRezimowe"


def test_zbuduj_mwu_opt_in():
    """mwu=True → Legatus.mwu ustawiony na HedgeMWU."""
    if not _ma_talib():
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False, mwu=True)
    assert d.legatus.mwu is not None
    assert type(d.legatus.mwu).__name__ == "HedgeMWU"


def test_zbuduj_wszystkie_warstwy_razem():
    """Wszystkie cztery warstwy razem — koegzystencja bez konfliktu."""
    if not _ma_talib():
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False, drift=True, rada=True,
                        synapsy=True, mwu=True)
    assert d.drift_adapter is not None
    assert d.rada_doradcow is not None
    assert d.legatus.synapsy is not None
    assert d.legatus.mwu is not None


def test_zbuduj_sygnatura_ma_nowe_parametry():
    """Sygnatura zbuduj() wystawia 4 nowe opt-in parametry, domyślnie False."""
    from imperium.koloseum.dyrygent import Dyrygent
    import inspect
    sig = inspect.signature(Dyrygent.zbuduj)
    for p in ("drift", "rada", "synapsy", "mwu"):
        assert p in sig.parameters, f"brak parametru {p}"
        assert sig.parameters[p].default is False, f"{p} musi domyślnie być False"
