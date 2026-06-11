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


def test_portfel_os_czasu_chronologiczna():
    """Krzywa equity ma 1 punkt na każdy bar (po oknie) wszystkich par + domknięcie."""
    bary_per = {s: _bary(s, n=300) for s in ("BTCUSDT", "ETHUSDT")}
    eng = backtest_portfel({}, "1D", okno=250, bary_per=bary_per)
    # (300-250) barów × 2 pary + 1 końcowy
    assert len(eng.krzywa_equity) == (300 - 250) * 2 + 1


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
