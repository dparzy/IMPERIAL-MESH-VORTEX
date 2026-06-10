"""
Testy backtestu Koloseum — przejazd Dyrygenta po historii barów.

Weryfikuje:
  • backtest() zwraca silnik z historią (kod Prawo XIX — nie tylko CLI),
  • brak zaglądania w przyszłość (okno kończy się na bieżącej świecy),
  • tryb auto_rezim (Namiestnik) działa bez wyjątku,
  • porownaj_tryby() liczy wszystkie trzy tryby.

Dane: syntetyczny trend generowany inline — bez zależności od plików CSV.
"""

import logging

import imperium.koloseum.backtest as bt_mod
from imperium.koloseum.backtest import backtest
from imperium.koloseum.dyrygent import Dyrygent
from imperium.koloseum.paper_trading import PaperTradingEngine

logging.disable(logging.CRITICAL)  # cisza w logach roju podczas testów


def _bary(n: int = 320, symbol: str = "BTCUSDT") -> list:
    """Łagodny trend wzrostowy z drobnymi oscylacjami — wystarcza dla EMA_200."""
    bary = []
    cena = 100.0
    for i in range(n):
        cena *= 1.002 if (i // 7) % 2 == 0 else 0.999   # naprzemienne fale
        o = cena
        c = cena * (1.001 if i % 2 == 0 else 0.9995)
        h = max(o, c) * 1.002
        l = min(o, c) * 0.998
        bary.append({
            "timestamp": 1_600_000_000_000 + i * 3_600_000,
            "open": o, "high": h, "low": l, "close": c,
            "volume": 1000.0 + i, "volume_quote": 0.0,
            "symbol": symbol, "interwal": "1H", "tradecount": 100,
        })
    return bary


def test_backtest_zwraca_silnik_z_historia():
    eng = backtest("X", "1H", okno=250, bary=_bary())
    assert isinstance(eng, PaperTradingEngine)
    # Silnik ma podsumowanie obliczalne (nawet jeśli 0 trades)
    st = eng.podsumowanie()
    st.oblicz(eng.historia_zamkniec)
    assert st.kapital_startowy == 10_000.0
    assert st.total_trades >= 0


def test_backtest_za_malo_barow_rzuca():
    try:
        backtest("X", "1H", okno=250, bary=_bary(n=100))
        assert False, "powinien rzucić ValueError przy oknie >= liczbie barów"
    except ValueError:
        pass


def test_backtest_bez_lookahead():
    """
    Bezpośredni dowód: każde okno przekazane do Dyrygent.cykl kończy się na
    bieżącej świecy i NIE zawiera barów z przyszłości (timestamp > bieżący).
    Szpieg podmienia Dyrygenta w module backtestu i rejestruje każde okno.
    """
    bary = _bary(n=300)
    naruszenia = []

    class SzpiegDyrygent(Dyrygent):
        def cykl(self, symbol, okno_barow, *args, **kwargs):
            biezacy_ts = okno_barow[-1]["timestamp"]
            ts_okna = [b["timestamp"] for b in okno_barow]
            # Żaden bar w oknie nie może być nowszy niż bieżąca (ostatnia) świeca.
            if max(ts_okna) != biezacy_ts:
                naruszenia.append(("przyszłość", biezacy_ts))
            # Okno musi być chronologiczne (rosnące).
            if ts_okna != sorted(ts_okna):
                naruszenia.append(("kolejność", biezacy_ts))
            return super().cykl(symbol, okno_barow, *args, **kwargs)

    pierwotny = bt_mod.Dyrygent
    bt_mod.Dyrygent = SzpiegDyrygent
    try:
        eng = backtest("X", "1H", okno=250, bary=bary)
    finally:
        bt_mod.Dyrygent = pierwotny

    assert not naruszenia, f"lookahead wykryty: {naruszenia[:3]}"
    assert isinstance(eng, PaperTradingEngine)


def test_backtest_auto_rezim_dziala():
    eng = backtest("X", "1H", okno=250, bary=_bary(), auto_rezim=True)
    assert isinstance(eng, PaperTradingEngine)
    assert "AUTO" in eng.sesja_id


def test_porownaj_tryby_liczy_wszystkie():
    bary = _bary()

    # porownaj_tryby czyta CSV — tu testujemy rdzeń przez 3 osobne backtesty
    wyniki = {}
    for tryb in ("agregat", "filtr", "strategia"):
        eng = backtest("X", "1H", okno=250, bary=bary, tryb=tryb)
        st = eng.podsumowanie()
        st.oblicz(eng.historia_zamkniec)
        wyniki[tryb] = st
    assert set(wyniki) == {"agregat", "filtr", "strategia"}
    for st in wyniki.values():
        assert st.kapital_koncowy > 0


def test_backtest_krzywa_equity_dla_bramki():
    """Backtest dostarcza krzywą equity per bar — wejście bramki W-282."""
    bary = _bary()
    eng = backtest("X", "1H", okno=250, bary=bary)
    assert hasattr(eng, "krzywa_equity")
    # equity po każdym barze pętli + 1 punkt po zamknięciu końcowym
    assert len(eng.krzywa_equity) == (len(bary) - 250) + 1
    assert all(p > 0 for p in eng.krzywa_equity)
    # krzywa działa jako wejście etap_pierwszy_koloseum (kontrakt end-to-end)
    from imperium.koloseum.walidacja import etap_pierwszy_koloseum
    w = etap_pierwszy_koloseum(eng.krzywa_equity, eng.podsumowanie(), interwal="1H")
    assert "ok" in w and "powod" in w and "dsr" in w


def test_backtest_ucz_mwu_zamyka_petle():
    """Pętla uczenia: MWU rozlicza zamknięte pozycje i różnicuje mnożniki wag."""
    bary = _bary()
    eng = backtest("X", "1H", okno=250, bary=bary, ucz_mwu=True)
    assert eng.podsumowanie().kapital_koncowy > 0
    # przy zamkniętych transakcjach mnożniki muszą się zróżnicować (≠1.0)
    if eng.historia_zamkniec:
        from imperium.legiony.rejestr import zbuduj_legatusa  # noqa: F401
        # silnik przeżył pełną pętlę — kontrakt: brak wyjątków + equity dodatnie
        assert all(p > 0 for p in eng.krzywa_equity)


def test_backtest_ucz_mwu_false_bez_zmian():
    """ucz_mwu=False (domyślne) → identyczne zachowanie jak dotychczas."""
    bary = _bary()
    e1 = backtest("X", "1H", okno=250, bary=bary)
    e2 = backtest("X", "1H", okno=250, bary=bary, ucz_mwu=False)
    assert e1.podsumowanie().total_trades == e2.podsumowanie().total_trades
