"""
Testy Refleksji Pamięci (W9 — sprzeczności + przedawnienie, W-360 v9).

Weryfikuje:
  • _kierunek() — wykrywa realizację (+) vs negację/plan (-),
  • wykryj_sprzecznosci() — ROZSTRZYGNIĘTE (- →+) vs SPRZECZNE (+ →-),
  • wykryj_przedawnienia() — stare otwarte pomysły bez realizacji,
  • anti-utrwalanie: moduł tylko zgłasza (nie ma metod kasujących),
  • granice: brak wspólnych tematów, ten sam dzień, neutralny kierunek.
"""

from imperium.biblioteki import refleksja_pamieci as rp


def test_kierunek_pozytyw_negatyw():
    assert rp._kierunek("wdrożona zmierzona gotowe") == "+"
    assert rp._kierunek("NIE zaimplementowana planowane") == "-"
    assert rp._kierunek("opis neutralny bez markera") is None
    assert rp._kierunek("wdrożona ale odrzucona") is None   # oba → niejednoznaczne


def test_sprzecznosc_rozstrzygniete(monkeypatch):
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"numba", "viterbi"}, "kierunek": "-",
         "opis": "Numba niezrobiona", "zrodlo": "wizje", "status": ""},
        {"data": "2026-06-28", "tematy": {"numba", "viterbi"}, "kierunek": "+",
         "opis": "Numba wdrożona", "zrodlo": "wizje", "status": ""},
    ])
    w = rp.wykryj_sprzecznosci()
    assert len(w) == 1
    assert w[0]["typ"] == "ROZSTRZYGNIĘTE"
    assert "2026-06-01" in w[0]["wczesny"] and "2026-06-28" in w[0]["pozny"]


def test_sprzecznosc_realna(monkeypatch):
    """Wcześniej + (zrobione), później - (cofnięte) → SPRZECZNE."""
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"portfel", "koszyk"}, "kierunek": "+",
         "opis": "Portfel wdrożony", "zrodlo": "wizje", "status": ""},
        {"data": "2026-06-20", "tematy": {"portfel", "koszyk"}, "kierunek": "-",
         "opis": "Portfel odrzucony", "zrodlo": "wizje", "status": ""},
    ])
    w = rp.wykryj_sprzecznosci()
    assert w and w[0]["typ"] == "SPRZECZNE"


def test_dziennik_narracja_nie_daje_falszywej_sprzecznosci(monkeypatch):
    """Prawo I (pomiar 2026-07-12): narracja Dziennika nie jest flipem statusu.
    Wpis wizji '+' i wpis dziennika '-' o wspólnych tematach NIE tworzą sprzeczności —
    domyślnie liczymy tylko ze źródeł statusowych (wizje). To gasi 92 fałszywe pozytywy."""
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"portfel", "koszyk"}, "kierunek": "+",
         "opis": "Portfel wdrożony", "zrodlo": "wizje", "status": "WDROŻONA"},
        {"data": "2026-06-20", "tematy": {"portfel", "koszyk"}, "kierunek": "-",
         "opis": "decyzje: nie robimy portfela na razie", "zrodlo": "dziennik", "status": ""},
    ])
    assert rp.wykryj_sprzecznosci() == []                       # domyślnie: tylko wizje
    # jawne rozszerzenie źródeł DZIAŁA (świadome włączenie dziennika)
    w = rp.wykryj_sprzecznosci(zrodla={"wizje", "dziennik"})
    assert w and w[0]["typ"] == "SPRZECZNE"


def test_brak_wspolnych_tematow_brak_sprzecznosci(monkeypatch):
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"numba", "viterbi"}, "kierunek": "-",
         "opis": "a", "zrodlo": "wizje", "status": ""},
        {"data": "2026-06-28", "tematy": {"portfel", "koszyk"}, "kierunek": "+",
         "opis": "b", "zrodlo": "wizje", "status": ""},
    ])
    assert rp.wykryj_sprzecznosci() == []


def test_ten_sam_dzien_pomijany(monkeypatch):
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"numba", "viterbi"}, "kierunek": "-",
         "opis": "a", "zrodlo": "wizje", "status": ""},
        {"data": "2026-06-01", "tematy": {"numba", "viterbi"}, "kierunek": "+",
         "opis": "b", "zrodlo": "wizje", "status": ""},
    ])
    assert rp.wykryj_sprzecznosci() == []


def test_przedawnienie_stary_pomysl(monkeypatch, tmp_path):
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("POMYSŁ", "Stary niezrealizowany pomysł xyz", "opis", plik=plik, data="2026-01-01")
    monkeypatch.setattr(rw, "PLIK_DOMYSLNY", plik)
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [])   # brak realizacji
    prz = rp.wykryj_przedawnienia(dni=21)
    assert prz and prz[0]["wiek_dni"] > 21
    assert "xyz" in prz[0]["opis"]


def test_przedawnienie_zrealizowany_nie_wisi(monkeypatch, tmp_path):
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("POMYSŁ", "Pomysł alfa beta gamma", "zrobić alfa beta", plik=plik, data="2026-01-01")
    monkeypatch.setattr(rw, "PLIK_DOMYSLNY", plik)
    # późniejsza realizacja na tych tematach
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"alfa", "beta", "gamma"}, "kierunek": "+",
         "opis": "zrobione", "zrodlo": "wizje", "status": ""},
    ])
    assert rp.wykryj_przedawnienia(dni=21) == []


def test_anti_utrwalanie_brak_metod_kasujacych():
    """Trustworthy reflection: moduł NIE ma metod kasujących/nadpisujących pamięć."""
    for nazwa in dir(rp):
        assert not any(z in nazwa.lower() for z in ("usun", "kasuj", "nadpisz", "delete", "remove"))


def test_raport_startowy_pusty_gdy_nic(monkeypatch):
    monkeypatch.setattr(rp, "wykryj_sprzecznosci", lambda *a, **k: [])
    monkeypatch.setattr(rp, "wykryj_przedawnienia", lambda *a, **k: [])
    assert rp.raport_startowy() == ""
