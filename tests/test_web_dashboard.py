"""Testy web dashboard (W-346) — routing, serializacja, Roman Naming, e2e serwer."""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.swiatynie.web_dashboard import (
    nazwa_rzymska, stan_do_json, obsluz_sciezke, SerwerDashboard, _PustyStan,
)
from imperium.swiatynie.live_monitor import StanDashboardu, StanPozycji, StanNeuronu


# ── Roman Naming (W-031) ─────────────────────────────────────────────────────

def test_nazwa_rzymska_btc():
    assert nazwa_rzymska("BTCUSDT") == "Capitolium"


def test_nazwa_rzymska_eth_sol():
    assert nazwa_rzymska("ETHUSDT") == "Patricii Aeterni"
    assert nazwa_rzymska("SOLUSDT") == "Velocitas Barbari"


def test_nazwa_rzymska_nieznana_pusta():
    assert nazwa_rzymska("FOOUSDT") == ""


def test_nazwa_rzymska_perp_i_usd():
    assert nazwa_rzymska("BTC_USDT") == "Capitolium"
    assert nazwa_rzymska("DOGEUSD") == "Mimus Augusti"


# ── stan_do_json ─────────────────────────────────────────────────────────────

def _stan_przyklad():
    return StanDashboardu(
        symbol="BTCUSDT", rezim="TREND_STRONG", kierunek_legatus="LONG",
        pewnosc=0.72, kapital=11000.0, kapital_start=10000.0,
        postawa_gubernatora="AGRESYWNY",
        pozycje=[StanPozycji(symbol="BTCUSDT", kierunek="LONG", wejscie=50000,
                             aktualny=51000, wielkosc=1000, sl=49000, tp=53000)],
        neurony_top=[StanNeuronu(klucz="X-03", kierunek="LONG", pewnosc=0.8, waga=7)],
        bary_przetworzone=42, decyzje_wejscia=3, weta=1, bledy=0,
    )


def test_stan_do_json_pola():
    d = stan_do_json(_stan_przyklad())
    assert d["rezim"] == "TREND_STRONG"
    assert d["kapital"] == 11000.0
    assert abs(d["zysk_pct"] - 10.0) < 1e-6  # (11000-10000)/10000
    assert d["decyzje_wejscia"] == 3


def test_stan_do_json_pozycja_pnl():
    d = stan_do_json(_stan_przyklad())
    poz = d["pozycje"][0]
    assert poz["rzymska"] == "Capitolium"
    # LONG 50000→51000 = +2%
    assert abs(poz["pnl_pct"] - 2.0) < 1e-6


def test_stan_do_json_neurony():
    d = stan_do_json(_stan_przyklad())
    assert d["neurony_top"][0]["klucz"] == "X-03"


def test_stan_do_json_zero_kapital_start_bez_dzielenia():
    """GRANICA: kapital_start=0 → zysk_pct=0, nie dzielenie przez zero."""
    d = stan_do_json(StanDashboardu(kapital=100.0, kapital_start=0.0))
    assert d["zysk_pct"] == 0.0


def test_stan_do_json_pusty_stan():
    """_PustyStan serializuje się bez błędu (Prawo XV — panel działa przed 1. barem)."""
    d = stan_do_json(_PustyStan())
    assert d["pozycje"] == []
    assert d["rezim"] == "OCZEKIWANIE"


# ── Routing (obsluz_sciezke — czysty, bez gniazda) ───────────────────────────

def test_routing_strona_glowna():
    status, ctype, body = obsluz_sciezke("/", _stan_przyklad())
    assert status == 200
    assert "text/html" in ctype
    assert b"KAPITOL IMPERIUM" in body


def test_routing_stan_json():
    status, ctype, body = obsluz_sciezke("/stan.json", _stan_przyklad())
    assert status == 200
    assert "application/json" in ctype
    d = json.loads(body)
    assert d["symbol"] == "BTCUSDT"


def test_routing_godlo_svg():
    status, ctype, body = obsluz_sciezke("/godlo.svg", _stan_przyklad())
    assert status == 200
    assert "svg" in ctype
    assert body.startswith(b"<svg") or b"<svg" in body


def test_routing_tiro_json():
    """Panel Szkoły TIRO — postęp zbierania par przez NOTARIUSA."""
    status, ctype, body = obsluz_sciezke("/tiro.json", _stan_przyklad())
    assert status == 200
    assert "application/json" in ctype
    d = json.loads(body)
    assert "par" in d and "postep" in d
    assert {"cel", "procent", "brakuje", "opis"} <= set(d["postep"])


def test_routing_tiro_nie_zalezy_od_stanu_petli():
    """
    GRANICA: zbiór rośnie od KAŻDEGO wywołania Hyginusa (zwiad, auto-lekcje), nie tylko
    podczas handlu — panel musi działać także z pustym stanem pętli.
    """
    status, _, body = obsluz_sciezke("/tiro.json", _PustyStan())
    assert status == 200
    assert "par" in json.loads(body)


def test_routing_tiro_nie_wywraca_sie_gdy_notarius_pada(monkeypatch):
    """
    ŻELAZNA ZASADA panelu pobocznego: awaria NOTARIUSA nie może wywrócić dashboardu —
    Cezar ma dalej widzieć pozycje i neurony, nawet gdy pisarz ma problem.
    """
    import imperium.biblioteki.notarius as notarius

    def wybuch(*a, **kw):
        raise RuntimeError("dysk spłonął")

    monkeypatch.setattr(notarius, "statystyki", wybuch)
    status, _, body = obsluz_sciezke("/tiro.json", _stan_przyklad())
    assert status == 200                      # nie 500 — panel zwraca sensowną pustkę
    d = json.loads(body)
    assert d["par"] == 0 and "blad" in d


def test_html_zawiera_panel_tiro():
    _, _, body = obsluz_sciezke("/", _stan_przyklad())
    assert "Szkoła TIRO".encode("utf-8") in body
    assert b"tiro-pasek" in body              # pasek postępu (Prawo XXIV)


def test_routing_404():
    status, _, _ = obsluz_sciezke("/nieznane", _stan_przyklad())
    assert status == 404


def test_routing_ignoruje_query():
    """Query string nie psuje routingu (/stan.json?t=123 → stan.json)."""
    status, ctype, _ = obsluz_sciezke("/stan.json?t=123", _stan_przyklad())
    assert status == 200 and "json" in ctype


# ── E2E serwer (efemeryczny port) ────────────────────────────────────────────

def test_serwer_start_aktualizuj_stop():
    import urllib.request
    serwer = SerwerDashboard(port=0)  # port 0 = system przydziela wolny
    serwer.start()
    try:
        port = serwer._serwer.server_address[1]
        serwer.aktualizuj(_stan_przyklad())
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/stan.json", timeout=5) as r:
            d = json.loads(r.read())
        assert d["rezim"] == "TREND_STRONG"
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as r:
            assert b"KAPITOL" in r.read()
    finally:
        serwer.stop()
    assert serwer._serwer is None


def test_serwer_podwojny_start_bezpieczny():
    serwer = SerwerDashboard(port=0)
    serwer.start()
    try:
        serwer.start()  # drugi start — no-op, bez crashu
        assert serwer._serwer is not None
    finally:
        serwer.stop()


def test_konfigpetli_ma_pola_dashboard():
    """KonfigPetliLive ma pola dashboard/dashboard_port (domyślnie OFF)."""
    from imperium.koloseum.petla_live import KonfigPetliLive
    cfg = KonfigPetliLive(symbole=["BTCUSDT"])
    assert cfg.dashboard is False
    assert cfg.dashboard_port == 8777
