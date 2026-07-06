"""Testy Raportu Żalu (narzedzia/raport_zalu.py) — Kronika Żyć Nieprzeżytych, Prawo I/XV."""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia import raport_zalu as rz
from imperium.biblioteki.arena_baza import zapisz_pomiar


# ─── Parsowanie reżimu z noty ────────────────────────────────────────────────

def test_rezim_z_noty_format_cienia():
    assert rz._rezim_z_noty("BTCUSDT TREND_STRONG") == "TREND_STRONG"


def test_rezim_z_noty_format_live():
    assert rz._rezim_z_noty("4h RANGING bar3") == "RANGING"


def test_rezim_z_noty_fallback_normal():
    assert rz._rezim_z_noty("cokolwiek bez rezimu") == "NORMAL"
    assert rz._rezim_z_noty("") == "NORMAL"


# ─── Brak danych ─────────────────────────────────────────────────────────────

def test_pusta_baza_brak_cieni(tmp_path):
    dane = rz.zbierz_zal(db_path=tmp_path / "a.db")
    assert dane["cienie"] == [] and dane["real_zamkniec"] == 0
    assert "brak danych CIEN_PNL" in rz.raport_tekst(dane)


# ─── Żal: znane wartości ─────────────────────────────────────────────────────

def _seed(db):
    # real: średnia 1.0 w TREND
    zapisz_pomiar("LIVE_PNL", "BTCUSDT", 1.0, "4h TREND_STRONG bar1", db_path=db)
    zapisz_pomiar("LIVE_PNL", "BTCUSDT", 1.0, "4h TREND_STRONG bar2", db_path=db)
    # cień bez_wet: średnia 3.0 w TREND → żal +2.0 (weta kosztują)
    zapisz_pomiar("CIEN_PNL", "bez_wet", 2.0, "BTCUSDT TREND_STRONG", db_path=db)
    zapisz_pomiar("CIEN_PNL", "bez_wet", 4.0, "BTCUSDT TREND_STRONG", db_path=db)


def test_zal_dodatni_kosztuje(tmp_path):
    db = tmp_path / "a.db"
    _seed(db)
    dane = rz.zbierz_zal(db_path=db, min_barow=1)
    cien = next(c for c in dane["cienie"] if c["cien"] == "bez_wet")
    assert cien["ogolem"]["zal"] == 2.0                      # 3.0 − 1.0
    assert "KOSZTUJĄ" in cien["ogolem"]["werdykt"]           # interpretacja bez_wet, żal>0


def test_zal_ujemny_ratuje(tmp_path):
    db = tmp_path / "a.db"
    zapisz_pomiar("LIVE_PNL", "BTCUSDT", 5.0, "4h NORMAL bar1", db_path=db)
    zapisz_pomiar("CIEN_PNL", "bez_wet", -2.0, "BTCUSDT NORMAL", db_path=db)
    dane = rz.zbierz_zal(db_path=db, min_barow=1)
    og = dane["cienie"][0]["ogolem"]
    assert og["zal"] == -7.0 and "CHRONIĄ" in og["werdykt"]  # żal<0 → weta chronią


def test_per_rezim_rozbicie(tmp_path):
    db = tmp_path / "a.db"
    _seed(db)
    dane = rz.zbierz_zal(db_path=db, min_barow=1)
    cien = next(c for c in dane["cienie"] if c["cien"] == "bez_wet")
    trend = next(r for r in cien["per_rezim"] if r["rezim"] == "TREND_STRONG")
    assert trend["zal"] == 2.0 and trend["n_cien"] == 2 and trend["n_real"] == 2


# ─── Guard próby (Prawo I) ───────────────────────────────────────────────────

def test_za_malo_barow_bez_werdyktu(tmp_path):
    db = tmp_path / "a.db"
    _seed(db)                                    # tylko 2 zamknięcia
    dane = rz.zbierz_zal(db_path=db, min_barow=100)
    og = dane["cienie"][0]["ogolem"]
    assert og["zal"] is None and og["werdykt"] == "za mało danych"


def test_brak_real_w_rezimie_bez_werdyktu(tmp_path):
    db = tmp_path / "a.db"
    # cień ma dane w VOLATILE, real NIE ma → brak podstawy porównania
    zapisz_pomiar("CIEN_PNL", "prog_surowy", 1.0, "BTCUSDT VOLATILE", db_path=db)
    zapisz_pomiar("LIVE_PNL", "BTCUSDT", 1.0, "4h NORMAL bar1", db_path=db)
    dane = rz.zbierz_zal(db_path=db, min_barow=1)
    cien = dane["cienie"][0]
    vol = next(r for r in cien["per_rezim"] if r["rezim"] == "VOLATILE")
    assert vol["zal"] is None and vol["n_real"] == 0


# ─── CLI ─────────────────────────────────────────────────────────────────────

def test_main_zwraca_zero(tmp_path):
    import io
    from contextlib import redirect_stdout
    db = tmp_path / "a.db"
    _seed(db)
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = rz.main(["--db", str(db), "--min-barow", "1"])
    assert rc == 0
    out = buf.getvalue()
    assert "KRONIKA ŻYĆ NIEPRZEŻYTYCH" in out and "bez_wet" in out
