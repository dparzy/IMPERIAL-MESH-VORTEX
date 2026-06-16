"""
Testy neuronu X-28 NeuronKonfluencjaMultiTF (W-321) + MTF wskaźników z Budowniczego.
Reguła Test-Granic (Prawo XXI): zero/None, graniczne progi, trwałość.
"""
from imperium.legiony.neurony.momentum import NeuronKonfluencjaMultiTF


def _n():
    return NeuronKonfluencjaMultiTF()


def _w(**kw):
    base = {"CLOSE": 50000.0, "RSI_14": 55.0, "EMA_21": 49000.0}
    base.update(kw)
    return base


# ── Brak danych wyższego TF ────────────────────────────────────────────────

def test_brak_4h_i_1d_abstynuje():
    s = _n().interpretuj(_w())
    assert s.kierunek == "NEUTRAL"
    assert s.pewnosc == 0.0


def test_tylko_4h_dostepne_2z2_long():
    """Gdy 1D brak, wystarczą 2/2 TF (local+4H) LONG."""
    s = _n().interpretuj(_w(
        MTF_4H_RSI_14=60.0, MTF_4H_EMA_50=48000.0,  # RSI>50 i EMA below close → LONG
    ))
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.62


# ── Konfluencja LONG 3/3 TF ─────────────────────────────────────────────────

def test_3z3_long_wysoka_pewnosc():
    s = _n().interpretuj(_w(
        RSI_14=60.0, EMA_21=48000.0,
        MTF_4H_RSI_14=65.0, MTF_4H_EMA_50=47000.0,
        MTF_1D_RSI_14=58.0, MTF_1D_EMA_50=46000.0,
    ))
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.80


def test_3z3_short_wysoka_pewnosc():
    s = _n().interpretuj({
        "CLOSE": 40000.0,
        "RSI_14": 40.0, "EMA_21": 42000.0,
        "MTF_4H_RSI_14": 38.0, "MTF_4H_EMA_50": 43000.0,
        "MTF_1D_RSI_14": 35.0, "MTF_1D_EMA_50": 44000.0,
    })
    assert s.kierunek == "SHORT"
    assert s.pewnosc == 0.80


# ── Konfluencja 2/3 TF ───────────────────────────────────────────────────────

def test_2z3_long_pewnosc_062():
    """Local=NEUTRAL, 4H=LONG, 1D=LONG → 2/2 kierunkowych → LONG."""
    s = _n().interpretuj({
        "CLOSE": 50000.0,
        "RSI_14": 50.0,   # dokładnie na granicy → neutral (nie bullish z EMA)
        "EMA_21": 50001.0,   # close < EMA → niedźwiedzi → neutral per metodę
        "MTF_4H_RSI_14": 60.0, "MTF_4H_EMA_50": 47000.0,
        "MTF_1D_RSI_14": 55.0, "MTF_1D_EMA_50": 46000.0,
    })
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.62


def test_2z3_short_pewnosc_062():
    s = _n().interpretuj({
        "CLOSE": 40000.0,
        "RSI_14": 50.0, "EMA_21": 39999.0,  # local neutral
        "MTF_4H_RSI_14": 40.0, "MTF_4H_EMA_50": 42000.0,
        "MTF_1D_RSI_14": 42.0, "MTF_1D_EMA_50": 43000.0,
    })
    assert s.kierunek == "SHORT"
    assert s.pewnosc == 0.62


# ── Sprzeczne TF → NEUTRAL ────────────────────────────────────────────────────

def test_sprzeczne_tf_neutral():
    """1h=LONG, 4H=SHORT → sprzeczność → NEUTRAL."""
    s = _n().interpretuj({
        "CLOSE": 50000.0,
        "RSI_14": 65.0, "EMA_21": 48000.0,   # LONG
        "MTF_4H_RSI_14": 35.0, "MTF_4H_EMA_50": 52000.0,  # SHORT
    })
    assert s.kierunek == "NEUTRAL"


# ── Granice RSI = dokładnie 50 ────────────────────────────────────────────────

def test_rsi_dokladnie_50_ema_rowne_close_neutral():
    """RSI=50 (nie bullish) + EMA = close (niedirekconalne) → NEUTRAL (0 bull, 0 bear)."""
    n = _n()
    kier = n._kierunek_tf(50.0, 50000.0, 50000.0)
    assert kier == "NEUTRAL"


def test_rsi_dokladnie_50_ema_powyzej_close_short():
    """RSI=50 (nie bullish) + EMA > close (bear EMA) → SHORT (1 bear > 0 bull)."""
    n = _n()
    kier = n._kierunek_tf(50.0, 51000.0, 50000.0)
    assert kier == "SHORT"


def test_rsi_50plus_epsilon_bullish():
    n = _n()
    kier = n._kierunek_tf(50.01, 49000.0, 50000.0)
    assert kier == "LONG"


# ── None w danych MTF ─────────────────────────────────────────────────────────

def test_mtf_4h_rsi_none_ale_ema_ok():
    """Gdy RSI=None ale EMA dostępne — 1 sygnał bull = LONG."""
    n = _n()
    kier = n._kierunek_tf(None, 49000.0, 50000.0)  # close > EMA → 1 bull
    assert kier == "LONG"


def test_obydwa_none_neutral():
    n = _n()
    kier = n._kierunek_tf(None, None, 50000.0)
    assert kier == "NEUTRAL"


# ── Budowniczy produkuje MTF wskaźniki ───────────────────────────────────────

def test_budowniczy_produkuje_mtf_dla_1h():
    """Budowniczy dla barów 1h z interwalem '1h' produkuje MTF_4H_* (Prawo XIX)."""
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    import random
    random.seed(7)
    bary = []
    c = 50000.0
    for i in range(200):
        c *= (1 + random.gauss(0.0001, 0.01))
        bary.append({"open": c * 0.999, "high": c * 1.005, "low": c * 0.998,
                     "close": c, "volume": 100 + i, "interwal": "1h"})
    b = BudowniczyWskaznikow()
    w = b.zbuduj(bary)
    assert "MTF_4H_RSI_14" in w, "Budowniczy powinien produkować MTF_4H_RSI_14 dla barów 1h"
    assert "MTF_4H_EMA_50" in w
    assert w["MTF_4H_RSI_14"] is not None
    assert 0 < w["MTF_4H_RSI_14"] < 100


def test_budowniczy_brak_mtf_dla_1d():
    """Bary 1d nie mają krótszego TF do agregacji — MTF klucze nieobecne lub None."""
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    import random
    random.seed(7)
    bary = []
    c = 50000.0
    for i in range(200):
        c *= (1 + random.gauss(0.0001, 0.01))
        bary.append({"open": c * 0.999, "high": c * 1.005, "low": c * 0.998,
                     "close": c, "volume": 100 + i, "interwal": "1d"})
    b = BudowniczyWskaznikow()
    w = b.zbuduj(bary)
    assert w.get("MTF_4H_RSI_14") is None


def test_budowniczy_brak_mtf_bez_interwalu():
    """Bez pola 'interwal' w barach — brak MTF (bezpieczna abstynencja)."""
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    import random
    random.seed(7)
    bary = []
    c = 50000.0
    for i in range(200):
        c *= (1 + random.gauss(0.0001, 0.01))
        bary.append({"open": c * 0.999, "high": c * 1.005, "low": c * 0.998,
                     "close": c, "volume": 100 + i})
    b = BudowniczyWskaznikow()
    w = b.zbuduj(bary)
    assert w.get("MTF_4H_RSI_14") is None
