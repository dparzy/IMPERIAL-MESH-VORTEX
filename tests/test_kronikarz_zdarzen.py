"""Testy Kronikarza Zdarzeń (W-289) — przyczynowość, studium, adapter, neuron."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imperium.biblioteki.kronikarz_zdarzen import (
    KronikarzZdarzen, AdapterKronikarz, KATALOG_ZDARZEN, _ts, _D,
)
from imperium.legiony.neurony.sesje import NeuronAugur

T0 = _ts(2024, 4, 20)   # halving #4


def _bary_wokol(ts_zdarzenia, dni_przed=40, dni_po=40, start=100.0, krok=1.0):
    """Bary dzienne: cena rośnie o `krok`/dzień (deterministyczny forward)."""
    bary = []
    cena = start
    for i in range(-dni_przed, dni_po + 1):
        bary.append({"timestamp": ts_zdarzenia + i * _D, "close": cena})
        cena += krok
    return bary


def test_katalog_poprawny():
    """Katalog: znane typy, ts rosnące w ramach typu, niepuste opisy."""
    assert len(KATALOG_ZDARZEN) >= 10
    for z in KATALOG_ZDARZEN:
        assert z["typ"] in {"HALVING", "ETF", "KRACH", "REGULACJA", "MAKRO"}
        assert z["opis"] and z["ts"] > _ts(2015, 1, 1)


def test_studium_liczy_forward_zwrot():
    """Cena na T0=100 (start 60 + 40 dni×1), forward 30d → 130 → +30%."""
    bary = _bary_wokol(T0, start=60.0)
    kr = KronikarzZdarzen(bary, horyzont_dni=30)
    st = kr.studium("HALVING", T0 + 35 * _D)
    assert st["n"] == 1 and st["prob_wzrostu"] == 100.0
    assert abs(st["mediana_pct"] - 30.0) < 1.0


def test_studium_przyczynowosc():
    """Pytanie o moment PRZED domknięciem horyzontu → zdarzenie wykluczone (n=0)."""
    bary = _bary_wokol(T0)
    kr = KronikarzZdarzen(bary, horyzont_dni=30)
    assert kr.studium("HALVING", T0 + 29 * _D)["n"] == 0, \
        "zdarzenie z niedomkniętym horyzontem NIE może zasilać statystyk (look-ahead!)"
    assert kr.studium("HALVING", T0 + 30 * _D)["n"] in (0, 1)  # granica
    assert kr.studium("HALVING", T0 + 31 * _D)["n"] == 1


def test_kontekst_okno_wplywu():
    """W oknie ≤30 dni po zdarzeniu → kontekst; po 31 dniach → None (granica)."""
    bary = _bary_wokol(T0)
    kr = KronikarzZdarzen(bary, okno_wplywu_dni=30)
    ctx = kr.kontekst(T0 + 5 * _D)
    assert ctx is not None and ctx["typ"] == "HALVING" and ctx["dni_po"] == 5.0
    # data CZYSTA (2027-06-01): >30 dni po ostatnim FOMC 2026-12-16, kalendarz
    # kończy się w 2026 → cisza augura.
    assert kr.kontekst(_ts(2027, 6, 1)) is None


def test_kontekst_nie_zasila_sam_siebie():
    """Statystyki w oknie halvingu 2024 liczą TYLKO wcześniejsze halvingi."""
    # bary obejmujące halving 2020 i 2024 (syntetyczne, wzrostowe)
    bary = _bary_wokol(_ts(2020, 5, 11), dni_przed=10, dni_po=40) + \
           _bary_wokol(T0, dni_przed=10, dni_po=10, start=500.0)
    kr = KronikarzZdarzen(bary, okno_wplywu_dni=30, horyzont_dni=30)
    ctx = kr.kontekst(T0 + 5 * _D)
    assert ctx["studium"]["n"] == 1, \
        f"tylko halving 2020 może zasilać (2016 poza barami, 2024 trwa), n={ctx['studium']['n']}"


def test_adapter_wzbogaca_i_milczy():
    bary = _bary_wokol(T0)
    ad = AdapterKronikarz(bary)
    w = {"TIMESTAMP": T0 + 3 * _D}
    ad.wzbogac(w)
    assert w["EVENT_TYP"] == "HALVING" and "EVENT_PROB_WZROSTU" in w
    # T0−100d = 2024-01-11 = 1 dzień PO ETF spot → adapter SŁUSZNIE mówi (ETF)!
    w_etf = {"TIMESTAMP": T0 - 100 * _D}
    ad.wzbogac(w_etf)
    assert w_etf.get("EVENT_TYP") == "ETF", "dzień po ETF = okno ETF (katalog działa)"
    w2 = {"TIMESTAMP": _ts(2027, 6, 1)}  # czysto: >30d po ostatnim zdarzeniu
    ad.wzbogac(w2)
    assert "EVENT_TYP" not in w2, "poza oknem adapter MILCZY (Prawo XV)"
    ad.wzbogac({})   # brak TIMESTAMP → bez wybuchu


def test_neuron_augur_granice():
    n = NeuronAugur()
    assert n.interpretuj({}).kierunek == "NEUTRAL"
    # za mało historii (n=1) → NEUTRAL z kontekstem
    s = n.interpretuj({"EVENT_TYP": "HALVING", "EVENT_DNI_PO": 5.0,
                       "EVENT_N": 1, "EVENT_PROB_WZROSTU": 100.0})
    assert s.kierunek == "NEUTRAL" and "za mało" in s.powody[0]
    # n=2, prob 100 → LONG; prob dokładnie 65 → LONG (granica włączona)
    assert n.interpretuj({"EVENT_TYP": "ETF", "EVENT_DNI_PO": 2.0,
                          "EVENT_N": 2, "EVENT_PROB_WZROSTU": 65.0}).kierunek == "LONG"
    # prob dokładnie 35 → SHORT; 50 → NEUTRAL
    assert n.interpretuj({"EVENT_TYP": "KRACH", "EVENT_DNI_PO": 2.0,
                          "EVENT_N": 3, "EVENT_PROB_WZROSTU": 35.0}).kierunek == "SHORT"
    assert n.interpretuj({"EVENT_TYP": "MAKRO", "EVENT_DNI_PO": 2.0,
                          "EVENT_N": 3, "EVENT_PROB_WZROSTU": 50.0}).kierunek == "NEUTRAL"


def test_parametry_graniczne():
    try:
        KronikarzZdarzen([], okno_wplywu_dni=0); raise AssertionError("ma rzucić")
    except ValueError:
        pass


if __name__ == "__main__":
    fn = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    bl = 0
    for nm, f in fn:
        try:
            f(); print(f"  ✅ {nm}")
        except Exception as e:
            bl += 1; print(f"  ❌ {nm}: {e}")
    sys.exit(1 if bl else 0)


# ── v2: per-para, FOMC blackout, decay, spójność ─────────────────────────────

def test_per_para_etf_filtruje():
    """ETH ETF (2024-05-23) widoczny dla ETHUSDT, NIE dla SOLUSDT."""
    from imperium.biblioteki.kronikarz_zdarzen import KronikarzZdarzen, _ts, _D
    ts = _ts(2024, 5, 25)   # 2 dni po ETH ETF
    bary = [{"timestamp": ts + i * _D, "close": 100.0} for i in range(-400, 40)]
    kr = KronikarzZdarzen(bary, okno_wplywu_dni=30)
    eth = kr.kontekst(ts, symbol="ETHUSDT")
    sol = kr.kontekst(ts, symbol="SOLUSDT")
    assert eth is not None and eth["typ"] == "ETF"
    # SOL: nie ma ETF w oknie; może trafić FOMC 2024-05-01 (24d) — ale NIE ETF
    assert sol is None or sol["typ"] != "ETF"


def test_fomc_blackout_przed_posiedzeniem():
    """1 dzień PRZED FOMC → blackout=True (system wie, że FED idzie)."""
    from imperium.biblioteki.kronikarz_zdarzen import KronikarzZdarzen, _ts, _D
    fomc = _ts(2025, 6, 18) + 19 * 3_600_000
    ts = fomc - 1 * _D   # dzień przed
    bary = [{"timestamp": _ts(2025, 6, 18) + i * _D, "close": 100.0}
            for i in range(-400, 40)]
    kr = KronikarzZdarzen(bary, blackout_dni=2)
    ctx = kr.kontekst(ts)
    assert ctx is not None and ctx["blackout"] is True and ctx["typ"] == "FOMC"
    assert ctx["dni_do"] > 0


def test_blackout_ma_pierwszenstwo_nad_oknem():
    """Gdy jednocześnie okno-po i blackout-przed → blackout wygrywa (ostrożność)."""
    from imperium.biblioteki.kronikarz_zdarzen import KronikarzZdarzen, _ts, _D
    # FOMC 2024-04-30? brak; weź parę blisko: FOMC 2024-05-01 i halving 2024-04-20.
    # ts = 2024-04-30: 10 dni po halvingu (okno) ORAZ 1 dzień przed FOMC 05-01.
    ts = _ts(2024, 4, 30)
    bary = [{"timestamp": _ts(2024, 4, 20) + i * _D, "close": 100.0}
            for i in range(-400, 60)]
    kr = KronikarzZdarzen(bary, okno_wplywu_dni=30, blackout_dni=2)
    ctx = kr.kontekst(ts)
    assert ctx["blackout"] is True and ctx["typ"] == "FOMC"


def test_decay_maleje_z_dni_po():
    """waga_zaniku: 1.0 w dniu zdarzenia → maleje liniowo do krawędzi okna."""
    from imperium.biblioteki.kronikarz_zdarzen import KronikarzZdarzen, _ts, _D
    t0 = _ts(2024, 4, 20)
    bary = [{"timestamp": t0 + i * _D, "close": 100.0} for i in range(-400, 40)]
    kr = KronikarzZdarzen(bary, okno_wplywu_dni=30)
    w0 = kr.kontekst(t0)["waga_zaniku"]
    w15 = kr.kontekst(t0 + 15 * _D)["waga_zaniku"]
    assert w0 > w15 > 0.0 and w0 <= 1.0


def test_studium_zgodnosc_i_rozrzut():
    """zgodne_kierunkowo=True gdy wszystkie epizody w tę samą stronę; rozrzut≥0."""
    from imperium.biblioteki.kronikarz_zdarzen import KronikarzZdarzen, _ts, _D
    # bary stale rosnące → każdy forward-zwrot dodatni → zgodne
    t = _ts(2024, 6, 1)
    bary = []
    cena = 50.0
    for i in range(-1200, 40):
        bary.append({"timestamp": t + i * _D, "close": cena}); cena += 0.5
    kr = KronikarzZdarzen(bary, horyzont_dni=30)
    st = kr.studium("FOMC", t + 35 * _D)
    assert st["n"] >= 2 and st["zgodne_kierunkowo"] is True
    assert st["rozrzut_pct"] is not None and st["rozrzut_pct"] >= 0.0


def test_neuron_blackout_neutralny_ostrozny():
    """AUG-01 w blackout → NEUTRAL z podwyższoną pewnością ostrożności."""
    n = NeuronAugur()
    s = n.interpretuj({"EVENT_TYP": "FOMC", "EVENT_BLACKOUT": True,
                       "EVENT_DNI_DO": 1.0, "EVENT_DNI_PO": -1.0})
    assert s.kierunek == "NEUTRAL" and s.pewnosc >= 0.5
    assert "BLACKOUT" in s.powody[0]


def test_neuron_decay_modeluje_pewnosc():
    """Mniejsza waga_zaniku → niższa pewność (świeże zdarzenie mocniej)."""
    n = NeuronAugur()
    baza = {"EVENT_TYP": "HALVING", "EVENT_N": 3, "EVENT_PROB_WZROSTU": 100.0,
            "EVENT_DNI_PO": 1.0, "EVENT_ZGODNE": True, "EVENT_BLACKOUT": False}
    swiezy = n.interpretuj({**baza, "EVENT_WAGA": 1.0})
    stary = n.interpretuj({**baza, "EVENT_WAGA": 0.3})
    assert swiezy.kierunek == stary.kierunek == "LONG"
    assert swiezy.pewnosc > stary.pewnosc
