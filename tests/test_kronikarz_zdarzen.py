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
    assert kr.kontekst(T0 + 31 * _D) is None
    assert kr.kontekst(T0 - 1 * _D) is None, "PRZED zdarzeniem brak okna (bez wróżenia)"


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
    w2 = {"TIMESTAMP": T0 - 200 * _D}    # 2023-10-03 — żadnego zdarzenia w oknie
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
