"""
Testy W-354 — TradingView Webhook Receiver.
Prawo XXI: testy granic + happy path + bezpieczeństwo sekret.
"""

import json

from imperium.swiatynie.webhook_tradingview import (
    AlertTV,
    OdbiornikWebhook,
    parsuj_alert_tv,
)


# ─── parsuj_alert_tv ──────────────────────────────────────────────────────────

def test_parsuj_poprawny_json():
    body = json.dumps({
        "symbol": "BTCUSDT", "interwal": "60", "akcja": "buy",
        "cena": 67500.0, "czas": "2026-01-01T12:00:00Z",
        "open": 67000.0, "high": 68000.0, "low": 66500.0,
        "close": 67500.0, "volume": 1234.5,
    }).encode()
    alert = parsuj_alert_tv(body)
    assert alert is not None
    assert alert.symbol == "BTCUSDT"
    assert alert.interwal == "60"
    assert alert.akcja == "LONG"     # "buy" → "LONG"
    assert alert.cena == 67500.0
    assert alert.wolumen == 1234.5


def test_parsuj_aliasy_akcji():
    for raw, expected in [("sell", "SHORT"), ("SELL", "SHORT"), ("long", "LONG"),
                          ("neutral", "NEUTRAL"), ("hold", "NEUTRAL"), ("0", "NEUTRAL"),
                          ("1", "LONG"), ("-1", "SHORT")]:
        body = json.dumps({"symbol": "X", "akcja": raw}).encode()
        a = parsuj_alert_tv(body)
        assert a is not None, f"parsowanie None dla akcja={raw}"
        assert a.akcja == expected, f"akcja={raw} → {a.akcja}, oczekiwano {expected}"


def test_parsuj_nieprawidlowy_json():
    assert parsuj_alert_tv(b"nie-json") is None
    assert parsuj_alert_tv(b"") is None
    assert parsuj_alert_tv(b"null") is None


def test_parsuj_sekret_poprawny():
    body = json.dumps({"symbol": "X", "sekret": "tajne"}).encode()
    assert parsuj_alert_tv(body, sekret="tajne") is not None


def test_parsuj_sekret_niepoprawny():
    body = json.dumps({"symbol": "X", "sekret": "ZLE"}).encode()
    assert parsuj_alert_tv(body, sekret="tajne") is None


def test_parsuj_brak_sekret_gdy_wymagany():
    body = json.dumps({"symbol": "X"}).encode()
    assert parsuj_alert_tv(body, sekret="tajne") is None


def test_parsuj_brak_wszystkich_pol_daje_defaults():
    body = json.dumps({}).encode()
    a = parsuj_alert_tv(body)
    assert a is not None
    assert a.symbol == "???"
    assert a.cena == 0.0
    assert a.akcja == "NEUTRAL"


def test_parsuj_aliasy_pol_tradingview():
    # TV wysyła ticker zamiast symbol, interval zamiast interwal
    body = json.dumps({
        "ticker": "ETHUSDT", "interval": "240", "action": "SELL",
        "price": 3500.0, "time": "1234567890000",
    }).encode()
    a = parsuj_alert_tv(body)
    assert a is not None
    assert a.symbol == "ETHUSDT"
    assert a.interwal == "240"
    assert a.akcja == "SHORT"
    assert a.cena == 3500.0


# ─── AlertTV.jako_bar ─────────────────────────────────────────────────────────

def test_jako_bar_pelne_dane():
    a = AlertTV("BTC", "60", "LONG", 100.0, "t",
                otwarcie=99.0, szczyt=101.0, dolina=98.0, zamkniecie=100.5, wolumen=500.0)
    b = a.jako_bar()
    assert b["open"] == 99.0
    assert b["high"] == 101.0
    assert b["low"] == 98.0
    assert b["close"] == 100.5
    assert b["volume"] == 500.0


def test_jako_bar_fallback_na_cena():
    # Bez zamkniecia → fallback na cena
    a = AlertTV("BTC", "60", "NEUTRAL", 50.0, "t")
    b = a.jako_bar()
    assert b["close"] == 50.0
    assert b["open"] == 50.0


# ─── OdbiornikWebhook ─────────────────────────────────────────────────────────

def _alert(sym="BTCUSDT", akcja="LONG", cena=100.0) -> AlertTV:
    return AlertTV(sym, "60", akcja, cena, "2026-01-01T00:00:00Z",
                   otwarcie=99.0, szczyt=101.0, dolina=98.0, zamkniecie=cena, wolumen=1.0)


def test_odbiornik_dodaj_i_pobierz():
    o = OdbiornikWebhook()
    o.dodaj(_alert("BTCUSDT", "LONG", 100.0))
    o.dodaj(_alert("ETHUSDT", "SHORT", 3500.0))
    alerty = o.pobierz_wszystkie()
    assert len(alerty) == 2
    # kolejka opróżniona
    assert o.pobierz_wszystkie() == []


def test_odbiornik_pusta_kolejka_nie_crashuje():
    o = OdbiornikWebhook()
    assert o.pobierz_wszystkie() == []


def test_odbiornik_dodaj_raw_poprawny():
    o = OdbiornikWebhook()
    body = json.dumps({"symbol": "SOLUSDT", "akcja": "buy", "cena": 150.0}).encode()
    ok = o.dodaj_raw(body)
    assert ok is True
    assert o.lacznie == 1
    alerty = o.pobierz_wszystkie()
    assert len(alerty) == 1
    assert alerty[0].symbol == "SOLUSDT"


def test_odbiornik_dodaj_raw_bledny_json():
    o = OdbiornikWebhook()
    ok = o.dodaj_raw(b"nie-json")
    assert ok is False
    assert o.bledy == 1
    assert o.pobierz_wszystkie() == []


def test_odbiornik_historia():
    o = OdbiornikWebhook()
    for i in range(5):
        o.dodaj(_alert("BTCUSDT", "LONG", float(100 + i)))
    hist = o.historia("BTCUSDT")
    assert len(hist) == 5
    assert hist[0].cena == 100.0
    assert hist[-1].cena == 104.0


def test_odbiornik_historia_nieznany_symbol():
    o = OdbiornikWebhook()
    assert o.historia("XXXXUSDT") == []


def test_odbiornik_symbole():
    o = OdbiornikWebhook()
    o.dodaj(_alert("BTCUSDT"))
    o.dodaj(_alert("ETHUSDT"))
    o.dodaj(_alert("BTCUSDT"))
    syms = o.symbole()
    assert "BTCUSDT" in syms
    assert "ETHUSDT" in syms


def test_odbiornik_swiecze_json():
    o = OdbiornikWebhook()
    o.dodaj(_alert("BTCUSDT", "LONG", 100.0))
    s = o.swiecze_json("BTCUSDT")
    assert len(s) == 1
    assert "time" in s[0]
    assert "open" in s[0]
    assert s[0]["close"] == 100.0


def test_odbiornik_statystyki():
    o = OdbiornikWebhook()
    o.dodaj(_alert())
    o.dodaj_raw(b"bledny")
    st = o.statystyki()
    assert st["lacznie_alertow"] == 1
    assert st["bledy_parsowania"] == 1
    assert isinstance(st["symbole"], list)


# ─── obsluz_sciezke + obsluz_post ────────────────────────────────────────────

def test_dashboard_post_webhook_tv():
    from imperium.swiatynie.web_dashboard import obsluz_post
    o = OdbiornikWebhook()
    body = json.dumps({"symbol": "BTCUSDT", "cena": 100.0}).encode()
    status, _, resp_body = obsluz_post("/webhook/tv", body, o)
    assert status == 200
    resp = json.loads(resp_body)
    assert resp["ok"] is True


def test_dashboard_post_bledny_json():
    from imperium.swiatynie.web_dashboard import obsluz_post
    o = OdbiornikWebhook()
    status, _, resp_body = obsluz_post("/webhook/tv", b"zle", o)
    assert status == 400
    resp = json.loads(resp_body)
    assert resp["ok"] is False


def test_dashboard_post_brak_odbiornika():
    from imperium.swiatynie.web_dashboard import obsluz_post
    status, _, _ = obsluz_post("/webhook/tv", b"{}", None)
    assert status == 503


def test_dashboard_post_nieznana_sciezka():
    from imperium.swiatynie.web_dashboard import obsluz_post
    status, _, _ = obsluz_post("/inny/endpoint", b"{}", None)
    assert status == 404


def test_dashboard_get_wykresy_json():
    from imperium.swiatynie.web_dashboard import obsluz_sciezke

    class _PustyStan:
        symbol = "BTCUSDT"; rezim = "NORMAL"; kierunek_legatus = "NEUTRAL"
        pewnosc = 0.0; kapital = 0.0; kapital_start = 0.0
        postawa_gubernatora = "NORMALNY"; bary_przetworzone = 0
        decyzje_wejscia = 0; weta = 0; bledy = 0; pozycje = []; neurony_top = []

    o = OdbiornikWebhook()
    o.dodaj(_alert("BTCUSDT", "LONG", 100.0))
    status, ctype, body = obsluz_sciezke("/wykresy/BTCUSDT.json", _PustyStan(), o)
    assert status == 200
    dane = json.loads(body)
    assert len(dane) == 1
    assert dane[0]["close"] == 100.0


def test_dashboard_stan_json_zawiera_webhook():
    from imperium.swiatynie.web_dashboard import obsluz_sciezke

    class _S:
        symbol = "?"; rezim = "?"; kierunek_legatus = "NEUTRAL"
        pewnosc = 0.0; kapital = 0.0; kapital_start = 0.0
        postawa_gubernatora = "NORMALNY"; bary_przetworzone = 0
        decyzje_wejscia = 0; weta = 0; bledy = 0; pozycje = []; neurony_top = []

    o = OdbiornikWebhook()
    o.dodaj(_alert())
    status, _, body = obsluz_sciezke("/stan.json", _S(), o)
    dane = json.loads(body)
    assert "webhook" in dane
    assert dane["webhook"]["lacznie_alertow"] == 1
