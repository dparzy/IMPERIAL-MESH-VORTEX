"""
W-309: KsięgaWad — prewencyjny filtr powtarzalnych wad setupów.

Wyekstrahowana z Mnemosyne (book_of_flaws) jako jedyna niereduntantna zdolność.
Testy: logika progów (test granic Prawa XXI), bootstrap z PamięciRefleksyjnej,
wpięcie do Dyrygenta (opt-in, weto przed wejściem).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.cesarz.ksiega_wad import KsiegaWad, StatWady, _sygnatura


# ─── Logika statystyki ────────────────────────────────────────────────────────

def test_sygnatura_format():
    assert _sygnatura("RANGING", "4H") == "RANGING/4H"


def test_stat_break_even_liczy_probe_nie_strate():
    """pnl == 0 → próba +1, strata +0 (spójne z MWU/Synapsy — Prawo XV/XVI)."""
    s = StatWady("X")
    s.zarejestruj(0.0)
    assert s.n_prob == 1
    assert s.n_strat == 0
    assert s.wskaznik_strat == 0.0


def test_stat_strata_i_zysk():
    s = StatWady("X")
    s.zarejestruj(-10.0)   # strata
    s.zarejestruj(5.0)     # zysk
    assert s.n_prob == 2
    assert s.n_strat == 1
    assert s.wskaznik_strat == 0.5


# ─── Progi: test granic (Prawo XXI — Reguła Test-Granic) ──────────────────────

def test_ponizej_min_prob_brak_werdyktu():
    """< min_prob prób → CZYSTO niezależnie od strat (decyzja na pomiarze)."""
    kw = KsiegaWad(prog_wady=0.5, min_prob=5)
    for _ in range(4):
        kw.zarejestruj("RANGING", "4H", -100.0)   # same straty, ale tylko 4 próby
    w = kw.sprawdz("RANGING", "4H")
    assert w.poziom == "CZYSTO"
    assert w.czy_wada is False
    assert w.n_prob == 4


def test_dokladnie_min_prob_aktywuje_werdykt():
    """Granica: dokładnie min_prob prób → werdykt już obowiązuje."""
    kw = KsiegaWad(prog_wady=0.6, min_prob=5)
    for _ in range(5):
        kw.zarejestruj("RANGING", "4H", -100.0)   # 5/5 strat = 100%
    w = kw.sprawdz("RANGING", "4H")
    assert w.czy_wada is True
    assert w.n_prob == 5


def test_dokladnie_prog_wady_jest_wada():
    """Granica: wskaźnik strat == prog_wady → WADA (≥, nie >)."""
    kw = KsiegaWad(prog_wady=0.6, min_prob=5)
    # 3 straty / 5 prób = 0.6 dokładnie
    for pnl in (-1.0, -1.0, -1.0, 1.0, 1.0):
        kw.zarejestruj("RANGING", "4H", pnl)
    w = kw.sprawdz("RANGING", "4H")
    assert w.wskaznik_strat == 0.6
    assert w.czy_wada is True
    assert w.poziom == "OSTRZEŻENIE"


def test_ponizej_prog_wady_czysto():
    """Granica: wskaźnik strat tuż pod progiem → CZYSTO."""
    kw = KsiegaWad(prog_wady=0.6, min_prob=5)
    # 2 straty / 5 = 0.4 < 0.6
    for pnl in (-1.0, -1.0, 1.0, 1.0, 1.0):
        kw.zarejestruj("RANGING", "4H", pnl)
    w = kw.sprawdz("RANGING", "4H")
    assert w.czy_wada is False
    assert w.poziom == "CZYSTO"


def test_weto_tylko_gdy_prog_weta_ustawiony():
    """prog_weta=None → nigdy WETO, tylko OSTRZEŻENIE (domyślnie bezpieczne)."""
    kw = KsiegaWad(prog_wady=0.5, min_prob=5, prog_weta=None)
    for _ in range(10):
        kw.zarejestruj("RANGING", "4H", -100.0)   # 100% strat
    w = kw.sprawdz("RANGING", "4H")
    assert w.poziom == "OSTRZEŻENIE"
    assert w.blokada is False


def test_weto_aktywne_powyzej_prog_weta():
    """Granica: wskaźnik strat ≥ prog_weta → WETO (blokada)."""
    kw = KsiegaWad(prog_wady=0.5, min_prob=5, prog_weta=0.8)
    for _ in range(10):
        kw.zarejestruj("RANGING", "4H", -100.0)   # 100% ≥ 80%
    w = kw.sprawdz("RANGING", "4H")
    assert w.poziom == "WETO"
    assert w.blokada is True


def test_miedzy_wada_a_weto_to_ostrzezenie():
    """prog_wady ≤ ws < prog_weta → OSTRZEŻENIE, nie WETO."""
    kw = KsiegaWad(prog_wady=0.5, min_prob=4, prog_weta=0.9)
    # 3 straty / 4 = 0.75 — między 0.5 a 0.9
    for pnl in (-1.0, -1.0, -1.0, 1.0):
        kw.zarejestruj("RANGING", "4H", pnl)
    w = kw.sprawdz("RANGING", "4H")
    assert w.poziom == "OSTRZEŻENIE"
    assert w.blokada is False


def test_nieznana_sygnatura_czysto():
    """Setup nigdy nie widziany → CZYSTO."""
    kw = KsiegaWad()
    w = kw.sprawdz("NIGDY", "1H")
    assert w.poziom == "CZYSTO"
    assert w.n_prob == 0


# ─── Bootstrap z PamięciRefleksyjnej (Prawo XVI — jedno źródło danych) ─────────

def test_ucz_z_pamieci():
    """ucz_z_pamieci() odtwarza statystyki z lekcji PamięciRefleksyjnej."""
    import tempfile
    from imperium.cesarz.pamiec_refleksyjna import PamiecRefleksyjna
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        plik = f.name
    try:
        pam = PamiecRefleksyjna(plik=plik)
        # 5 stratnych serii w RANGING/4H
        for _ in range(5):
            pam.zapisz_wynik([-10.0], rezim="RANGING", interwal="4H")
        kw = KsiegaWad(prog_wady=0.6, min_prob=5)
        n = kw.ucz_z_pamieci(pam)
        assert n == 5
        w = kw.sprawdz("RANGING", "4H")
        assert w.czy_wada is True
    finally:
        os.unlink(plik)


# ─── Raport ───────────────────────────────────────────────────────────────────

def test_raport_struktura():
    kw = KsiegaWad(prog_wady=0.6, min_prob=3)
    for _ in range(3):
        kw.zarejestruj("RANGING", "4H", -100.0)
    for _ in range(3):
        kw.zarejestruj("TREND", "4H", 100.0)
    rap = kw.raport()
    assert rap["n_sygnatur"] == 2
    wady_sig = [w["sygnatura"] for w in rap["wady"]]
    assert "RANGING/4H" in wady_sig
    assert "TREND/4H" not in wady_sig   # zyskowny setup nie jest wadą


# ─── Wpięcie do Dyrygenta (opt-in) ────────────────────────────────────────────

def test_zbuduj_ksiega_wad_domyslnie_off():
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    assert d.ksiega_wad is None


def test_zbuduj_ksiega_wad_aktywna():
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.cesarz.ksiega_wad import KsiegaWad as KW
    d = Dyrygent.zbuduj(adaptery_live=False, ksiega_wad=True)
    assert isinstance(d.ksiega_wad, KW)


def test_raport_ksiegi_wad_bez_ksiegi_none():
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    d = Dyrygent.zbuduj(adaptery_live=False)
    assert d.raport_ksiegi_wad() is None


def test_dyrygent_uczy_ksiege_z_zamkniec():
    """Integracja: zamknięcia w silniku → KsięgaWad uczy się sygnatur setupu."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.legiony.mikro_neuron import SygnalNeuronu

    d = Dyrygent.zbuduj(adaptery_live=False, ksiega_wad=True)
    s = SygnalNeuronu(neuron_id="T-01", legion="TREND", wskaznik="T-01", wartosc=1.0,
                      kierunek="LONG", pewnosc=0.8, waga=3, kategoria="T")
    # Symuluj 5 stratnych zamknięć w RANGING/4H
    class _W:
        def __init__(self, pid, pnl):
            self.pozycja_id = pid; self.pnl_pct = pnl
    for i in range(5):
        pid = f"pos-{i}"
        d._synapsy_pending[pid] = ([s], "RANGING", "LONG", "4H")
        d.engine.historia_zamkniec.append(_W(pid, -5.0))
    d._aktualizuj_synapsy()
    w = d.ksiega_wad.sprawdz("RANGING", "4H")
    assert w.czy_wada is True
    assert w.n_prob == 5


def test_petla_ksiega_wad_wpieta():
    """W-309: cfg.ksiega_wad=True → Dyrygent w pętli dostaje KsięgaWad."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.petla_live import _buduj_dyrygencie, KonfigPetliLive
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.cesarz.ksiega_wad import KsiegaWad as KW

    engine = PaperTradingEngine(kapital_startowy=10_000.0)
    kfg = KonfigPetliLive(symbole=["BTCUSDT"], interwal="1H",
                          synapsy=False, ksiega_wad=True)
    d = _buduj_dyrygencie(["BTCUSDT"], kfg, engine)["BTCUSDT"]
    assert isinstance(d.ksiega_wad, KW)


def test_petla_ksiega_wad_domyslnie_off():
    from imperium.koloseum.petla_live import KonfigPetliLive
    kfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert kfg.ksiega_wad is False


def test_backtest_ksiega_wad_sygnatura():
    """backtest_portfel() akceptuje ksiega_wad=True (sygnatura)."""
    import inspect
    from imperium.koloseum.backtest import backtest_portfel
    sig = inspect.signature(backtest_portfel)
    assert "ksiega_wad" in sig.parameters
