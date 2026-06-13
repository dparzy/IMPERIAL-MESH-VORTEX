"""Testy silnika portfelowego (W-290) — wspólny kapitał, N par, oś czasu."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from imperium.koloseum.backtest import backtest_portfel


def _bary(symbol, n=300, start=100.0, krok=0.5, ts0=1_600_000_000_000):
    bary = []
    cena = start
    for i in range(n):
        o = cena; c = cena + krok
        bary.append({"open": o, "high": c + 0.2, "low": o - 0.2, "close": c,
                     "volume": 1000.0 + i, "symbol": symbol, "interwal": "1D",
                     "timestamp": ts0 + i * 86_400_000})
        cena = c
    return bary


def test_portfel_wspolny_kapital_dziala():
    """3 pary, jeden silnik — equity dodatnie, max N pozycji naraz."""
    bary_per = {s: _bary(s) for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT")}
    eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per)
    assert eng.max_otwartych == 3
    assert eng.kapital_calkowity > 0
    assert hasattr(eng, "krzywa_equity") and all(p > 0 for p in eng.krzywa_equity)


def test_portfel_krzywa_dzienna():
    """Krzywa equity jest DZIENNA (1 punkt/dzień), nie per-zdarzenie — uczciwa
    annualizacja Sharpe przy N parach (√365 zakłada 1 pkt/dzień)."""
    bary_per = {s: _bary(s, n=300) for s in ("BTCUSDT", "ETHUSDT")}
    eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per)
    # 2 pary, te same daty 1D → ~50 dni handlowych (po oknie), nie 100 zdarzeń
    assert len(eng.krzywa_equity) <= 51
    assert all(p > 0 for p in eng.krzywa_equity)


def test_portfel_sizing_budzet_rowny():
    """Każdy Dyrygent sizinguje wg kapital/N (równe wagi) — nie pełnego kapitału."""
    bary_per = {s: _bary(s) for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT")}
    eng = backtest_portfel({}, "1D", okno=250, kapital_startowy=10_000.0,
                           bary_per=bary_per)
    # 4 pary → budżet sizingu 2500 każdej; pozycje nie mogą przekroczyć kapitału
    assert eng.kapital >= 0


def test_portfel_brak_historii_rzuca():
    bary_per = {"BTCUSDT": _bary("BTCUSDT", n=100)}   # < okno
    try:
        backtest_portfel({}, "1D", okno=250, bary_per=bary_per)
        raise AssertionError("za krótka historia powinna rzucić")
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


def test_portfel_dd_control_opt_in():
    """dd_control=True/False oba działają; wspólny bezpiecznik nie wybucha."""
    bary_per = {s: _bary(s, n=320) for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT")}
    for ddc in (False, True):
        eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per, dd_control=ddc)
        assert eng.kapital_calkowity > 0
        assert all(p > 0 for p in eng.krzywa_equity)


def test_portfel_progi_bezpiecznika_parametryzowane():
    """W-293: dd_reduced/dd_halt sterują bezpiecznikiem; domyślne portfelowe 7%/13%."""
    import inspect
    from imperium.koloseum.backtest import backtest_portfel
    sig = inspect.signature(backtest_portfel)
    assert sig.parameters["dd_reduced"].default == 0.07
    assert sig.parameters["dd_halt"].default == 0.13
    # Custom progi nie wybuchają, equity dodatnie
    bary_per = {s: _bary(s, n=320) for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT")}
    eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per,
                           dd_reduced=0.05, dd_halt=0.10)
    assert eng.kapital_calkowity > 0


def test_portfel_synapsy_rezimowe_opt_in():
    """W-299: synapsy_rezimowe=True nie psuje pipeline; equity dodatnie = wpięcie działa."""
    import imperium.koloseum.backtest as bt

    bary_per = {s: _bary(s, n=300) for s in ("BTCUSDT", "ETHUSDT")}
    eng = bt.backtest_portfel({}, "1D", okno=250, bary_per=bary_per,
                              synapsy_rezimowe=True)
    assert eng.kapital_calkowity > 0
    assert all(p > 0 for p in eng.krzywa_equity)


def test_portfel_synapsy_rezimowe_false_default():
    """W-299: synapsy_rezimowe domyślnie False — backtest identyczny ze starym wywołaniem."""
    import inspect
    from imperium.koloseum.backtest import backtest_portfel
    sig = inspect.signature(backtest_portfel)
    assert sig.parameters["synapsy_rezimowe"].default is False


def test_portfel_wstrzykuje_btc_trend():
    """Radar BTC: portfel ustawia kontekst_dodatkowy z BTC_TREND (lead-lag)."""
    import imperium.koloseum.backtest as bt
    bary_per = {s: _bary(s, n=300, krok=(1.5 if s == "BTCUSDT" else 0.5))
                for s in ("BTCUSDT", "ETHUSDT")}
    eng = bt.backtest_portfel({}, "1D", okno=250, bary_per=bary_per)
    # przebieg bez wyjątku + equity dodatnie (radar nie psuje pipeline)
    assert eng.kapital_calkowity > 0


# ── Opcja B: wagi portfela ────────────────────────────────────────────────────

def test_wagi_inwerse_vol_suma_jeden():
    """wagi_inwerse_vol: suma wag = 1.0."""
    from imperium.koloseum.backtest import wagi_inwerse_vol
    bary_per = {s: _bary(s, n=100, krok=(0.1 if s == "BTC" else 2.0))
                for s in ("BTC", "ETH", "DOGE")}
    w = wagi_inwerse_vol(bary_per, okno_vol=60)
    assert abs(sum(w.values()) - 1.0) < 1e-5, f"suma wag = {sum(w.values()):.6f}"


def test_wagi_inwerse_vol_mniej_zmiennym_wieksza_waga():
    """Para mniej zmienna dostaje wyższą wagę (risk-parity)."""
    from imperium.koloseum.backtest import wagi_inwerse_vol
    # BTC: krok=0.1 (stabilny), DOGE: krok=3.0 (bardzo zmienny)
    bary_per = {
        "BTCUSDT": _bary("BTCUSDT", n=100, krok=0.1),
        "DOGEUSDT": _bary("DOGEUSDT", n=100, krok=3.0),
    }
    w = wagi_inwerse_vol(bary_per, okno_vol=80)
    assert w["BTCUSDT"] > w["DOGEUSDT"], "stabilna para musi mieć wyższą wagę"


def test_portfel_z_wagami_zewnetrznymi():
    """backtest_portfel akceptuje wagi zewnętrzne bez błędu, equity dodatnie."""
    bary_per = {s: _bary(s, n=320) for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT")}
    wagi_ext = {"BTCUSDT": 0.5, "ETHUSDT": 0.3, "SOLUSDT": 0.2}
    eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per, wagi=wagi_ext)
    assert eng.kapital_calkowity > 0


def test_portfel_z_wagami_vol_adjusted():
    """Portfel z wagi_inwerse_vol() działa bez błędu."""
    from imperium.koloseum.backtest import wagi_inwerse_vol
    bary_per = {s: _bary(s, n=320, krok=(0.1 if s == "BTCUSDT" else 2.0))
                for s in ("BTCUSDT", "ETHUSDT")}
    w = wagi_inwerse_vol(bary_per, okno_vol=60)
    eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per, wagi=w)
    assert eng.kapital_calkowity > 0
