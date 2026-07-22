"""Testy organu PORTITOR (pre-flight środowiska u wrót sesji — B1).

Nacisk (Reguła Test-Granic): obecność kluczy API (unset/pusty/whitespace/ustawiony —
NIGDY wartość), dryf fingerprintu vs baseline (pojawienie/zniknięcie/zmiana wersji/Python),
alarmy (krytyczna zależność brak, DEEPSEEK brak), round-trip baseline, odporność świeżości.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.pretorianie import portitor as pt  # noqa: E402


# ── _klucze_api: granice obecności (Bezpieczeństwo: tylko obecność) ───────────

def test_klucze_unset_daja_false(monkeypatch):
    for nazwa, _ in pt.KLUCZE_API:
        monkeypatch.delenv(nazwa, raising=False)
    assert all(not k["obecny"] for k in pt._klucze_api())


def test_klucz_ustawiony_daje_true(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-cokolwiek")
    kk = {k["nazwa"]: k["obecny"] for k in pt._klucze_api()}
    assert kk["DEEPSEEK_API_KEY"] is True


def test_klucz_pusty_i_whitespace_to_brak(monkeypatch):
    """Granica: pusty string i same spacje = brak (nie „ustawiony na pusto")."""
    monkeypatch.setenv("MEXC_API_KEY", "")
    monkeypatch.setenv("MEXC_SECRET", "   ")
    kk = {k["nazwa"]: k["obecny"] for k in pt._klucze_api()}
    assert kk["MEXC_API_KEY"] is False and kk["MEXC_SECRET"] is False


def test_klucze_api_nie_ujawniaja_wartosci(monkeypatch):
    """Bezpieczeństwo NIENARUSZALNE: struktura zwraca bool obecności, nie wartość klucza."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "TAJNA-WARTOSC-123")
    for k in pt._klucze_api():
        assert set(k) == {"nazwa", "obecny", "skutek"}
        assert "TAJNA-WARTOSC-123" not in json.dumps(k, ensure_ascii=False)


# ── _dryf_pol: granice porównania fingerprintu ───────────────────────────────

def test_dryf_identyczny_pusty():
    fp = {"python": "3.11.9", "pakiety": {"numpy": "2.4.6"}}
    assert pt._dryf_pol(fp, dict(fp)) == []


def test_dryf_zmiana_pythona():
    base = {"python": "3.11.9", "pakiety": {}}
    live = {"python": "3.12.0", "pakiety": {}}
    z = pt._dryf_pol(base, live)
    assert len(z) == 1 and "3.11.9" in z[0] and "3.12.0" in z[0]


def test_dryf_pakiet_pojawil_sie_i_znikl():
    base = {"python": "x", "pakiety": {"numpy": "2.4.6", "ccxt": "4.5.0"}}
    live = {"python": "x", "pakiety": {"numpy": "2.5.0", "requests": "2.34.2"}}
    z = pt._dryf_pol(base, live)
    tekst = " ".join(z)
    assert "numpy" in tekst and "2.4.6" in tekst and "2.5.0" in tekst   # zmiana wersji
    assert "ccxt" in tekst and "brak" in tekst                           # zniknął
    assert "requests" in tekst                                           # pojawił się


# ── _alarmy: granice actionable ──────────────────────────────────────────────

def _mig(deps, klucze_present):
    return {
        "zaleznosci": [{"nazwa": n, "krytyczny": k, "obecny": o} for n, k, o in deps],
        "klucze_api": [{"nazwa": n, "obecny": o, "skutek": "s"} for n, o in klucze_present],
    }


def test_alarm_gdy_krytyczna_zaleznosc_brak():
    mig = _mig([("numpy", True, False), ("pandas", False, False)],
               [("DEEPSEEK_API_KEY", True)])
    a = pt._alarmy(mig)
    assert any("numpy" in x for x in a)
    assert not any("pandas" in x for x in a)   # niekrytyczna nie alarmuje


def test_brak_alarmu_gdy_wszystko_krytyczne_obecne():
    mig = _mig([("numpy", True, True), ("talib", True, True)],
               [("DEEPSEEK_API_KEY", True)])
    assert pt._alarmy(mig) == []


def test_alarm_deepseek_brak_ale_mexc_nie():
    mig = _mig([("numpy", True, True)],
               [("DEEPSEEK_API_KEY", False), ("MEXC_API_KEY", False)])
    a = pt._alarmy(mig)
    assert any("DEEPSEEK_API_KEY" in x for x in a)
    assert not any("MEXC" in x for x in a)     # MEXC brak = informacyjne (faza paper)


# ── baseline round-trip + wykryj_dryf pierwszy ───────────────────────────────

def test_baseline_zapis_odczyt(tmp_path, monkeypatch):
    plik = tmp_path / "portitor_baseline.json"
    monkeypatch.setattr(pt, "BAZA_BASELINE", plik)
    fp = {"python": "3.11.9", "pakiety": {"numpy": "2.4.6"}}
    pt.zapisz_baseline(fp)
    assert pt.wczytaj_baseline() == fp


def test_wykryj_dryf_pierwszy_gdy_brak_baseline(tmp_path, monkeypatch):
    monkeypatch.setattr(pt, "BAZA_BASELINE", tmp_path / "nie_ma.json")
    wynik = pt.wykryj_dryf()
    assert wynik["pierwszy"] is True and wynik["zmiany"] == []


def test_wczytaj_baseline_uszkodzony_daje_none(tmp_path, monkeypatch):
    plik = tmp_path / "b.json"
    plik.write_text("{ uszkodzony json", encoding="utf-8")
    monkeypatch.setattr(pt, "BAZA_BASELINE", plik)
    assert pt.wczytaj_baseline() is None


# ── odporność + smoke ────────────────────────────────────────────────────────

def test_swiezosc_danych_zwraca_liste():
    """Nie rzuca; każdy element ma interwał i (opcjonalnie) wiek_dni."""
    d = pt._swiezosc_danych()
    assert isinstance(d, list)
    for x in d:
        assert "interwal" in x and "najnowsza" in x and "wiek_dni" in x


def test_banner_i_raport_nie_rzucaja():
    assert "PORTITOR" in pt.banner()
    assert "PORTITOR" in pt.raport()


def test_migawka_ma_komplet_pol():
    m = pt.migawka_srodowiska()
    assert set(m) >= {"python", "platforma", "zaleznosci", "klucze_api", "dane", "znacznik"}


def test_fingerprint_pomija_klucze_i_dane():
    """Fingerprint dryfu = tylko Python + pakiety (klucze/dane zmienne z natury)."""
    fp = pt._fingerprint(pt.migawka_srodowiska())
    assert set(fp) == {"python", "pakiety"}
