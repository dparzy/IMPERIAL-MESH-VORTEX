"""Testy Pamięci Absolutnej — zapis/odczyt JSONL, serializacja, podsumowanie sesji."""

import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path
from imperium.biblioteki.pamiec_absolutna import (
    ImperiumLog, PamiecAbsolutna, TypLogu,
)


def test_serializacja_roundtrip():
    log = ImperiumLog(
        log_typ=TypLogu.SYGNAL, sesja_id="s1", symbol="BTCUSDT",
        interwal="1H", legatus_kierunek="LONG", legatus_pewnosc=0.78,
    )
    json_str = log.to_json()
    odtworzony = ImperiumLog.from_json(json_str)
    assert odtworzony.symbol == "BTCUSDT"
    assert odtworzony.legatus_pewnosc == 0.78
    assert odtworzony.log_id == log.log_id


def test_zapis_i_odczyt():
    with tempfile.TemporaryDirectory() as tmp:
        pamiec = PamiecAbsolutna(katalog=Path(tmp))
        log = ImperiumLog(
            log_typ=TypLogu.SYGNAL, sesja_id="s1", symbol="ETHUSDT",
            interwal="4H", legatus_kierunek="SHORT",
        )
        pamiec.zapisz(log)
        wczytane = pamiec.wczytaj(symbol="ETHUSDT")
        assert len(wczytane) == 1
        assert wczytane[0].symbol == "ETHUSDT"
        assert wczytane[0].legatus_kierunek == "SHORT"


def test_sekwencja_rosnie():
    with tempfile.TemporaryDirectory() as tmp:
        pamiec = PamiecAbsolutna(katalog=Path(tmp))
        l1 = ImperiumLog(log_typ=TypLogu.SYGNAL, sesja_id="s1", symbol="BTCUSDT", interwal="1H")
        l2 = ImperiumLog(log_typ=TypLogu.SYGNAL, sesja_id="s1", symbol="BTCUSDT", interwal="1H")
        pamiec.zapisz(l1)
        pamiec.zapisz(l2)
        assert l1.sekwencja == 1
        assert l2.sekwencja == 2


def test_podsumowanie_sesji():
    with tempfile.TemporaryDirectory() as tmp:
        pamiec = PamiecAbsolutna(katalog=Path(tmp))
        logi = [
            ImperiumLog(log_typ=TypLogu.TRADE_CLOSE, sesja_id="s1",
                        symbol="BTCUSDT", interwal="1H", pnl_pct=2.0),
            ImperiumLog(log_typ=TypLogu.TRADE_CLOSE, sesja_id="s1",
                        symbol="BTCUSDT", interwal="1H", pnl_pct=-1.0),
            ImperiumLog(log_typ=TypLogu.TRADE_CLOSE, sesja_id="s1",
                        symbol="BTCUSDT", interwal="1H", pnl_pct=3.0),
        ]
        pods = pamiec.podsumowanie_sesji("s1", logi)
        assert pods["trade_count"] == 3
        assert abs(pods["win_rate"] - 2/3) < 0.01  # 2 z 3 wygrane
        assert abs(pods["total_pnl_pct"] - 4.0) < 0.01


def test_filtrowanie_po_symbolu():
    with tempfile.TemporaryDirectory() as tmp:
        pamiec = PamiecAbsolutna(katalog=Path(tmp))
        pamiec.zapisz(ImperiumLog(log_typ=TypLogu.SYGNAL, sesja_id="s1",
                                  symbol="BTCUSDT", interwal="1H"))
        pamiec.zapisz(ImperiumLog(log_typ=TypLogu.SYGNAL, sesja_id="s1",
                                  symbol="ETHUSDT", interwal="1H"))
        btc = pamiec.wczytaj(symbol="BTCUSDT")
        assert all(l.symbol == "BTCUSDT" for l in btc)
