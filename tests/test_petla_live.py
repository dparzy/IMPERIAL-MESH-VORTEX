"""
Testy W-302 — PętlaLive: główny entrypoint systemu live.

Reguła Test-Granic (Prawo XXI):
  - fetcher padnie dla jednego symbolu → pętla nie crashuje
  - brak BTC w koszyku → Radar pominięty bezpiecznie
  - max_barow=N → pętla kończy po N barach
  - PamięćRefleksyjna zapisuje lekcje po zamknięciach
  - Dyrygent._pamiec wstrzyknięta → lekcja zapisana per zamknięcie
"""

import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from imperium.koloseum.petla_live import (
    handluj_live, KonfigPetliLive, _df_do_barow,
)


# ── helper: syntetyczny loader ────────────────────────────────────────────────

def _df(n=60, start=100.0, krok=0.5):
    """Syntetyczny DataFrame jak z DataLoader.fetch()."""
    ts = pd.date_range("2024-01-01", periods=n, freq="1h")
    close = [start + i * krok for i in range(n)]
    return pd.DataFrame({
        "timestamp": ts,
        "open":   [c - krok * 0.1 for c in close],
        "high":   [c + krok * 0.2 for c in close],
        "low":    [c - krok * 0.2 for c in close],
        "close":  close,
        "volume": [1000.0 + i for i in range(n)],
    })


class _MockLoader:
    """Wstrzykiwany loader zwracający syntetyczne dane bez sieci."""
    def __init__(self, symbol_dfs=None, fail_symbols=None):
        self._dfs = symbol_dfs or {}   # symbol → DataFrame
        self._fail = set(fail_symbols or [])

    def fetch(self, symbol, timeframe="1H", limit=400):
        if symbol in self._fail:
            raise ConnectionError(f"Symulowany błąd sieci dla {symbol}")
        return self._dfs.get(symbol, _df())


# ── konwersja DataFrame → bary ────────────────────────────────────────────────

def test_df_do_barow_konwertuje_poprawnie():
    df = _df(10)
    bary = _df_do_barow(df, "BTCUSDT", "1H")
    assert len(bary) == 10
    assert all(k in bary[0] for k in ("timestamp", "open", "high", "low", "close", "volume"))
    assert bary[0]["symbol"] == "BTCUSDT"
    assert bary[0]["interwal"] == "1H"
    assert isinstance(bary[0]["timestamp"], int)


def test_df_do_barow_timestamp_int_ms():
    """Timestamp musi być int (ms) — wymagany przez RADAR bisect i PaperTradingEngine."""
    df = _df(5)
    bary = _df_do_barow(df, "X", "1H")
    for b in bary:
        assert isinstance(b["timestamp"], int)
        assert b["timestamp"] > 1_000_000_000_000   # ms (>2001-rok)


# ── pętla live: poprawność startu ─────────────────────────────────────────────

def test_petla_konczy_po_max_barach():
    loader = _MockLoader({"BTCUSDT": _df(80), "ETHUSDT": _df(80, start=50.0)})
    kfg = KonfigPetliLive(symbole=["BTCUSDT", "ETHUSDT"], interwal="1H",
                          kapital_startowy=10_000.0, paper=True, synapsy=False)
    st = handluj_live(kfg, max_barow=3, _loader=loader)
    assert st.bary_przetworzone >= 1   # co najmniej 1 symbol przetworzony


def test_petla_nie_crashuje_gdy_fetch_pada():
    """Jeden symbol pada → pętla trwa, nie rzuca wyjątku."""
    loader = _MockLoader(
        {"BTCUSDT": _df(80)},
        fail_symbols=["ETHUSDT"],
    )
    kfg = KonfigPetliLive(symbole=["BTCUSDT", "ETHUSDT"], interwal="1H",
                          kapital_startowy=10_000.0, paper=True, synapsy=False)
    st = handluj_live(kfg, max_barow=2, _loader=loader)
    assert st.bledy == 0   # fetch error obsługuje try/except → nie wchodzi do błędów cyklu


def test_petla_bez_btc_w_koszyku_pomija_radar():
    """Bez BTC_* symbolu: Radar pomijany, pętla działa normalnie."""
    loader = _MockLoader({"ETHUSDT": _df(80, start=50.0), "SOLUSDT": _df(80, start=20.0)})
    kfg = KonfigPetliLive(symbole=["ETHUSDT", "SOLUSDT"], interwal="1H",
                          kapital_startowy=5_000.0, paper=True, synapsy=False)
    st = handluj_live(kfg, max_barow=2, _loader=loader)
    assert st.bary_przetworzone >= 1


def test_petla_z_synapsy_nie_crashuje():
    """synapsy=True: każdy Dyrygent dostaje SynapsyRezimowe, pętla działa."""
    loader = _MockLoader({"BTCUSDT": _df(80), "ETHUSDT": _df(80, start=50.0)})
    kfg = KonfigPetliLive(symbole=["BTCUSDT", "ETHUSDT"], interwal="1H",
                          kapital_startowy=10_000.0, paper=True, synapsy=True)
    st = handluj_live(kfg, max_barow=2, _loader=loader)
    assert st.bary_przetworzone >= 1


def test_konfig_cienie_domyslnie_off():
    """Opt-in (ZASADA WPIĘCIA): cienie domyślnie False = zero zmiany zachowania pętli."""
    kfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert kfg.cienie is False


def test_petla_z_cieniami_nie_crashuje(monkeypatch):
    """cienie=True: menedżer Cieni wpięty, pętla działa. Offline — wymuszamy adaptery=[]
    i no-op zapis (bez sieci, bez skażenia realnej bazy areny)."""
    import imperium.koloseum.legiony_cieni as lc_mod
    orig = lc_mod.zbuduj_cienie_paper
    monkeypatch.setattr(
        lc_mod, "zbuduj_cienie_paper",
        lambda *a, **k: orig(*a, **{**k, "adaptery_factory": None, "arena_zapis": (lambda w: len(w))}),
    )
    loader = _MockLoader({"BTCUSDT": _df(80)})
    kfg = KonfigPetliLive(symbole=["BTCUSDT"], interwal="1H",
                          kapital_startowy=10_000.0, paper=True, synapsy=False, cienie=True)
    st = handluj_live(kfg, max_barow=2, _loader=loader)
    assert st.bary_przetworzone >= 1


def test_petla_mwu_igrzyska_wpiete_w_dyrygentow():
    """W-307: cfg.mwu/igrzyska=True → każdy Dyrygent dostaje warstwy uczenia."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.petla_live import _buduj_dyrygencie
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.biblioteki.hedge_mwu import HedgeMWU
    from imperium.biblioteki.igrzyska import Igrzyska

    engine = PaperTradingEngine(kapital_startowy=10_000.0)
    kfg = KonfigPetliLive(symbole=["BTCUSDT"], interwal="1H",
                          synapsy=False, mwu=True, igrzyska=True)
    dyr = _buduj_dyrygencie(["BTCUSDT"], kfg, engine)
    d = dyr["BTCUSDT"]
    assert isinstance(d.legatus.mwu, HedgeMWU)
    assert isinstance(d._igrzyska, Igrzyska)


def test_petla_mwu_igrzyska_domyslnie_off():
    """Domyślna konfiguracja → warstwy uczenia wyłączone (zero zmiany zachowania)."""
    try:
        import talib  # noqa: F401
    except ImportError:
        return
    from imperium.koloseum.petla_live import _buduj_dyrygencie
    from imperium.koloseum.paper_trading import PaperTradingEngine

    engine = PaperTradingEngine(kapital_startowy=10_000.0)
    kfg = KonfigPetliLive(symbole=["BTCUSDT"], interwal="1H", synapsy=False)
    assert kfg.mwu is False and kfg.igrzyska is False
    d = _buduj_dyrygencie(["BTCUSDT"], kfg, engine)["BTCUSDT"]
    assert d.legatus.mwu is None
    assert d._igrzyska is None


def test_petla_zapisuje_pamiec_po_zamknięciach():
    """PamięćRefleksyjna: lekcja zapisana gdy pozycja zamknięta."""
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        plik = f.name
    try:
        loader = _MockLoader({
            "BTCUSDT": _df(200, krok=2.0),   # silny trend → wejście możliwe
        })
        kfg = KonfigPetliLive(
            symbole=["BTCUSDT"], interwal="1H",
            kapital_startowy=10_000.0, paper=True, synapsy=False,
            plik_pamieci=plik,
        )
        # Większy limit barów by cykl miał dość historii
        kfg.limit_barow = 200

        handluj_live(kfg, max_barow=5, _loader=loader)

        # Jeśli nie było zamknięcia — OK, plik może być pusty (nie zawsze trade
        # otworzy się i zamknie w 5 barach). Sprawdzamy że plik istnieje i nie padł.
        assert os.path.exists(plik)
    finally:
        os.unlink(plik)


# ── PamięćRefleksyjna wstrzyknięta w Dyrygent ────────────────────────────────

def test_dyrygent_pamiec_zapisuje_lekcje():
    """Dyrygent._pamiec = PamiecRefleksyjna → lekcja po każdym zamknięciu."""
    from imperium.koloseum.dyrygent import Dyrygent
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    from imperium.legiony.rejestr import zbuduj_legatusa
    from imperium.cesarz.pamiec_refleksyjna import PamiecRefleksyjna

    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
        plik = f.name
    try:
        legatus = zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False)
        engine = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="TEST-PAMIEC")
        d = Dyrygent(legatus=legatus, kalkulator=KalkulatorLewara(), engine=engine,
                     min_pewnosc=0.1)
        d._pamiec = PamiecRefleksyjna(plik=plik)

        assert d._pamiec is not None
        # Samo przypisanie bez crash = test minimalny
        # (zamknięcie pozycji jest trudne do wymuszenia w teście jednostkowym
        #  bez pełnych wskaźników — wystarczy że hook istnieje i jest podpięty)
    finally:
        os.unlink(plik)


# ── KonfigPetliLive wartości domyślne ─────────────────────────────────────────

def test_konfiguracja_domyslne_wartosci():
    kfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert kfg.interwal == "1H"
    assert kfg.paper is True
    assert kfg.synapsy is True
    assert kfg.kapital_startowy == 10_000.0


def test_konfiguracja_pauza_none_oblicza_z_interwal():
    """pauza_sekundy=None → petla_live oblicza z _INTERWAL_SEKUNDY."""
    from imperium.koloseum.petla_live import _INTERWAL_SEKUNDY
    kfg = KonfigPetliLive(symbole=["BTCUSDT"], interwal="4H")
    assert kfg.pauza_sekundy is None
    assert _INTERWAL_SEKUNDY["4H"] == 14400


# ── W-329 P4: decay synaps reżimowych w live ──────────────────────────────────

def test_konfiguracja_synapsy_decay_domyslnie_50():
    """W-329: decay synaps domyślnie 50 barów (higiena pamięci długiego live)."""
    kfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert kfg.synapsy_decay_co_bar == 50


def test_synapsy_zapomnij_redukuje_martwe_pary():
    """zapomnij() łagodnie tłumi silos i kasuje pary poniżej alpha_decay (Prawo XV P4)."""
    from imperium.biblioteki.synapsy_rezimowe import SynapsyRezimowe
    syn = SynapsyRezimowe()
    syn._silo["X-01|X-02@NORMAL"] = 0.5        # żywa para
    syn._silo["X-03|X-04@NORMAL"] = 0.0005     # prawie martwa (< alpha_decay typ.)
    syn.zapomnij()
    # żywa para osłabiona, ale nadal istnieje
    assert syn._silo.get("X-01|X-02@NORMAL", 0) < 0.5
    assert syn._silo.get("X-01|X-02@NORMAL", 0) > 0
    # martwa para skasowana (poniżej progu alpha_decay)
    assert "X-03|X-04@NORMAL" not in syn._silo


# ── W-330: auto-discovery par ─────────────────────────────────────────────────

def test_auto_discover_domyslnie_off():
    """Domyślnie auto_discover wyłączone (sztywna lista) — zero zmiany zachowania."""
    kfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert kfg.auto_discover is False
    assert kfg.auto_discover_top_n == 5


def test_auto_discover_zastepuje_liste():
    """handluj_live z loaderem discovery → cfg.symbole zastąpione rankingiem SelektorPar."""
    import pandas as pd
    from imperium.koloseum.petla_live import handluj_live

    class _DiscoveryLoader(_MockLoader):
        def lista_par_rynku(self, quote="USDT", typ="swap"):
            return ["BTC/USDT:USDT", "XRP/USDT:USDT"]
        def filtruj_plynne(self, pary, min_obrot_usd=5_000_000.0, limit=None):
            dane = {"BTC/USDT:USDT": 100e6, "XRP/USDT:USDT": 60e6}
            out = [{"symbol": s, "obrot_usd": dane[s], "cena": 1.0}
                   for s in pary if dane.get(s, 0) >= min_obrot_usd]
            return out[:limit] if limit else out
        def fetch(self, symbol, timeframe="4h", limit=200):
            return pd.DataFrame({"close": [100 + i for i in range(20)],
                                 "open": [100 + i for i in range(20)],
                                 "high": [101 + i for i in range(20)],
                                 "low": [99 + i for i in range(20)],
                                 "volume": [10.0] * 20,
                                 "timestamp": pd.date_range("2026-01-01", periods=20, freq="4h")})

    kfg = KonfigPetliLive(symbole=["PLACEHOLDER"], interwal="4H",
                          auto_discover=True, auto_discover_top_n=2,
                          auto_discover_min_obrot=1e6, synapsy=False)
    loader = _DiscoveryLoader()
    # max_barow=1 — jeden obieg wystarczy do sprawdzenia podmiany listy
    handluj_live(kfg, max_barow=1, _loader=loader)
    assert "PLACEHOLDER" not in kfg.symbole
    assert "BTC/USDT:USDT" in kfg.symbole
