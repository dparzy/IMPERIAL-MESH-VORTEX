"""Testy PRAETORIUM (imperium/swiatynie/praetorium.py) — Kwatera Główna Imperatora.

Reguła Test-Granic (Prawo XXI): renderer jest CZYSTĄ funkcją, więc testujemy granice
bez serwera i przeglądarki. Rdzeń kontraktu = UCZCIWOŚĆ (Prawo I): gdy źródła brak,
kokpit MUSI powiedzieć „BRAK DANYCH", a nie narysować wypełniacz wyglądający na pomiar.
"""
from imperium.swiatynie.praetorium import (BRAK, ZYWE, _bezpiecznie,
                                            render_praetorium)


def _stan_min():
    return {
        "imperator": "CEZAR PIXEL", "czas": "2026-07-19 20:00",
        "roj": {"neurony": 87, "neurony_aktywne": 81, "zwiadowcy": 15,
                "strategie": 20, "elity": 18, "zrodlo": ZYWE},
        "organy": {"dane": [("⚔️", "legiony", 67)], "zrodlo": ZYWE},
        "honor": {"noty": 5, "korony": 5, "saldo": 0, "dlug": 0, "zrodlo": ZYWE},
        "rynek": {"zrodlo": BRAK, "powod": "brak połączenia z giełdą (MEXC)"},
    }


def test_render_zwraca_pelny_html():
    h = render_praetorium(_stan_min())
    assert h.startswith("<!doctype html>")
    assert "PRAETORIUM" in h
    assert h.rstrip().endswith("</html>")


def test_rynek_bez_zrodla_mowi_brak_danych_i_nie_zmysla_liczb():
    """Prawo I: brak giełdy → jawny komunikat, ZERO wypełniacza udającego pomiar."""
    h = render_praetorium(_stan_min())
    assert "BRAK DANYCH" in h
    assert "Front milczy" in h
    assert "brak połączenia z giełdą (MEXC)" in h


def test_rynek_zywy_pokazuje_pozycje():
    stan = _stan_min()
    stan["rynek"] = {
        "zrodlo": ZYWE, "kapital": "12 480 USDT", "pnl": 2.4, "postawa": "NORMALNY",
        "pozycje": [{"para": "BTC/USDT", "kierunek": "LONG", "wejscie": "64100", "wynik": 2.4}],
    }
    h = render_praetorium(stan)
    assert "BTC/USDT" in h
    assert "ŻYWE" in h
    assert "+2.40%" in h


def test_rynek_zywy_bez_pozycji_nie_wywala_sie():
    stan = _stan_min()
    stan["rynek"] = {"zrodlo": ZYWE, "kapital": "0", "pnl": 0.0,
                     "postawa": "NORMALNY", "pozycje": []}
    h = render_praetorium(stan)
    assert "brak otwartych pozycji" in h


def test_pnl_ujemny_ma_klase_strata():
    stan = _stan_min()
    stan["rynek"] = {"zrodlo": ZYWE, "kapital": "1", "pnl": -3.1,
                     "postawa": "OBRONA", "pozycje": []}
    h = render_praetorium(stan)
    assert "strata" in h
    assert "-3.10%" in h


def test_dlug_honorowy_zero_jest_zielony():
    h = render_praetorium(_stan_min())
    assert "DŁUG HONOROWY: 0 — czysto" in h
    assert "z-ok" in h


def test_dlug_honorowy_niezerowy_jest_alarmem():
    stan = _stan_min()
    stan["honor"]["dlug"] = 2
    h = render_praetorium(stan)
    assert "2 niespłacony" in h
    assert "z-al" in h


def test_pusty_stan_nie_wywala_renderu():
    """Granica: całkiem pusty słownik — kokpit ma się wyrenderować, nie rzucić."""
    h = render_praetorium({})
    assert "PRAETORIUM" in h
    assert "BRAK DANYCH" in h


def test_brak_organow_mowi_wprost():
    stan = _stan_min()
    stan["organy"] = {"dane": [], "zrodlo": BRAK}
    h = render_praetorium(stan)
    assert "brak danych o organach" in h


def test_escaping_nie_wpuszcza_html():
    """Bezpieczeństwo: wartość z zewnątrz nie może wstrzyknąć znacznika."""
    stan = _stan_min()
    stan["imperator"] = "<script>alert(1)</script>"
    h = render_praetorium(stan)
    assert "<script>alert(1)</script>" not in h
    assert "&lt;script&gt;" in h


def test_rozkazy_sa_nieaktywne_dopoki_front_niepodlaczony():
    """ZASADA WPIĘCIA: przyciski egzekucji nie mogą być klikalne bez świadomej decyzji."""
    h = render_praetorium(_stan_min())
    assert "disabled" in h
    assert "Wydaj order" in h


# ── panele Grupy 1 (PORTITOR/sprzęt, CODEX, Refleksja, Dziennik, treść Not) ──

def test_nastepny_krok_pokazuje_sie_gdy_zywy():
    stan = _stan_min()
    stan["nastepny_krok"] = {"tekst": "🎯 NASTĘPNY KROK: zrobić X", "zrodlo": ZYWE}
    h = render_praetorium(stan)
    assert "zrobić X" in h
    assert "nastepny" in h


def test_nastepny_krok_pusty_nie_rysuje_paska():
    stan = _stan_min()
    stan["nastepny_krok"] = {"tekst": "", "zrodlo": BRAK}
    h = render_praetorium(stan)
    assert 'class="nastepny"' not in h


def test_zaplecze_nigdy_nie_pokazuje_wartosci_klucza():
    """Bezpieczeństwo: na ekran trafia OBECNOŚĆ klucza, nigdy jego wartość."""
    stan = _stan_min()
    stan["zaplecze"] = {"portitor": "deps 6/6 | klucze DEEPSEEK✓ MEXC✗",
                        "klasa": "PEDES", "model_zakres": "1–3B", "zrodlo": ZYWE}
    h = render_praetorium(stan)
    assert "DEEPSEEK✓" in h
    assert "PEDES" in h


def test_zaplecze_brak_mowi_wprost():
    stan = _stan_min()
    stan["zaplecze"] = {"zrodlo": BRAK}
    h = render_praetorium(stan)
    assert "pre-flight niedostępny" in h


def test_codex_i_refleksja_pokazuja_linie():
    stan = _stan_min()
    stan["codex"] = {"linia": "CODEX: 33 rekordów", "zrodlo": ZYWE}
    stan["refleksja"] = {"linia": "Refleksja: 1 pomysł wisi", "zrodlo": ZYWE}
    h = render_praetorium(stan)
    assert "33 rekordów" in h
    assert "1 pomysł wisi" in h


def test_codex_brak_zrodla_nie_udaje_danych():
    stan = _stan_min()
    stan["codex"] = {"zrodlo": BRAK}
    h = render_praetorium(stan)
    assert "ledger niedostępny" in h


def test_ostatnie_noty_pokazuja_tresc():
    stan = _stan_min()
    stan["honor"]["ostatnie"] = [
        {"typ": "NOTA", "id": "N-1", "opis": "martwa gałąź", "data": "2026-07-19"},
        {"typ": "CORONA", "id": "C-1", "opis": "RUF034 w bramce", "data": "2026-07-19"},
    ]
    h = render_praetorium(stan)
    assert "martwa gałąź" in h
    assert "RUF034 w bramce" in h


def test_brak_ostatnich_not_nie_rysuje_karty():
    stan = _stan_min()
    stan["honor"]["ostatnie"] = []
    h = render_praetorium(stan)
    assert "Księga Not — ostatnie wpisy" not in h


def test_bezpiecznie_lapie_wyjatek_zrodla():
    """Jedno padnięte źródło NIE może zabić kokpitu — zwraca wartość domyślną."""
    def pada():
        raise RuntimeError("źródło padło")
    assert _bezpiecznie(pada, {"zrodlo": BRAK}) == {"zrodlo": BRAK}
    assert _bezpiecznie(lambda: "ok") == "ok"


def test_trasa_praetorium_w_web_dashboard():
    """Prawo XVI: kokpit podaje istniejący serwer, nie drugi własny."""
    from imperium.swiatynie.web_dashboard import obsluz_sciezke
    status, ctype, body = obsluz_sciezke("/praetorium", stan=None)
    assert status == 200
    assert "text/html" in ctype
    assert b"PRAETORIUM" in body
