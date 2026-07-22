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


def test_pomysl_nie_przeczy_wdrozonemu(monkeypatch):
    """Granica (10/10 FP z 2026-07-18): późniejszy „−" będący POMYSŁEM/KANDYDATEM
    nie jest regresem wobec wdrożonego — bez twardej negacji para NIE powstaje."""
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-30", "tematy": {"hurst", "h-01"}, "kierunek": "+",
         "opis": "Dodano neuron H-01 (Hurst-DFA)", "zrodlo": "wizje", "status": "WDROŻONA"},
        {"data": "2026-07-15", "tematy": {"hurst", "h-01"}, "kierunek": "-",
         "opis": "Time-Morph — adaptacyjny interwal (kand. #25)", "zrodlo": "wizje",
         "status": "POMYSŁ"},
    ])
    assert rp.wykryj_sprzecznosci() == []


def test_twarda_negacja_w_statusie_nadal_sprzeczna(monkeypatch):
    """Granica dopełniająca: realne ODRZUCENIE po wdrożeniu MUSI zostać złapane."""
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [
        {"data": "2026-06-01", "tematy": {"portfel", "koszyk"}, "kierunek": "+",
         "opis": "Portfel wdrożony", "zrodlo": "wizje", "status": "WDROŻONA"},
        {"data": "2026-06-20", "tematy": {"portfel", "koszyk"}, "kierunek": "-",
         "opis": "Portfel", "zrodlo": "wizje", "status": "ODRZUCONA"},
    ])
    w = rp.wykryj_sprzecznosci()
    assert w and w[0]["typ"] == "SPRZECZNE"


def test_stoplista_tnie_slowa_funkcyjne():
    """Granica: 'jako'/'decyzja'/'moduł'/'budowa' NIE są tematami — to one spinały
    obce wpisy w pary („Odrzucono Zig" ↔ „Budowa ważenia IC", zmierzone 2026-07-18)."""
    t = rp._tematy("Budowa ważenia głosów jako nowa decyzja modułu")
    assert not ({"jako", "nowa", "decyzja", "budowa"} & t)
    assert "ważenia" in t or "głosów" in t          # realne tematy zostają


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


def test_zawieszenie_wycisza_alarm_od_daty_decyzji(monkeypatch, tmp_path):
    """GRANICA: świeżo ZAWIESZONY stary wpis NIE wisi — alarm da się wyciszyć decyzją.

    Bug (2026-07-20): wiek liczono od `data` (utworzenia), więc wpis odłożony DZIŚ,
    a założony 24 dni temu, natychmiast wracał jako „⏳ wisi, zdecyduj". Alarmu nie
    dało się wyciszyć decyzją — a taki alarm uczy ignorowania alarmów.
    """
    from datetime import date

    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("POMYSŁ", "Wektory semantyczne delta epsilon", "opis", plik=plik,
             data="2026-01-01")
    monkeypatch.setattr(rw, "PLIK_DOMYSLNY", plik)
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [])

    assert rp.wykryj_przedawnienia(dni=21), "przed decyzją wpis MA wisieć"

    rw.zmien_status("Wektory semantyczne delta epsilon", "ZAWIESZONA", plik=plik)
    wpis = rw.wszystkie(plik=plik)[0]
    assert wpis["data_statusu"] == date.today().isoformat(), "decyzja musi być datowana"
    assert rp.wykryj_przedawnienia(dni=21) == [], "po decyzji alarm milknie"


def test_zawieszenie_wraca_do_przegladu_po_oknie(monkeypatch, tmp_path):
    """GRANICA druga: odłożenie to PARKOWANIE, nie kasowanie — po oknie wraca.

    Bez tego naprawa zamieniłaby jeden błąd (nie da się wyciszyć) na gorszy
    (wyciszenie na zawsze — pomysł ginie po cichu, złamanie Prawa XV).
    """
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("POMYSŁ", "Parkowany pomysł zeta eta", "opis", plik=plik, data="2026-01-01")
    monkeypatch.setattr(rw, "PLIK_DOMYSLNY", plik)
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [])
    rw.zmien_status("Parkowany pomysł zeta eta", "ZAWIESZONA", plik=plik)

    # Decyzja sprzed 40 dni → okno 21 dni minęło, pomysł wraca do przeglądu.
    wpisy = rw.wszystkie(plik=plik)
    wpisy[0]["data_statusu"] = "2026-06-01"
    rw._nadpisz(wpisy, plik)
    assert rp.wykryj_przedawnienia(dni=21), "zaparkowany pomysł musi wrócić po oknie"


def test_stary_wpis_bez_daty_statusu_zachowuje_sie_jak_dawniej(monkeypatch, tmp_path):
    """Wsteczna zgodność: wpisy sprzed zmiany nie mają `data_statusu` → fallback na `data`."""
    from imperium.biblioteki import rejestr_wizji as rw
    plik = tmp_path / "w.jsonl"
    rw.dodaj("POMYSŁ", "Wpis archaiczny theta jota", "opis", plik=plik, data="2026-01-01")
    wpisy = rw.wszystkie(plik=plik)
    wpisy[0]["status"] = "ZAWIESZONA"      # zawieszony PRZED wprowadzeniem pola
    wpisy[0].pop("data_statusu", None)
    rw._nadpisz(wpisy, plik)
    monkeypatch.setattr(rw, "PLIK_DOMYSLNY", plik)
    monkeypatch.setattr(rp, "_wpisy_statusowe", lambda: [])
    assert rp.wykryj_przedawnienia(dni=21), "brak pola → wiek od utworzenia (jak dawniej)"


def test_anti_utrwalanie_brak_metod_kasujacych():
    """Trustworthy reflection: moduł NIE ma metod kasujących/nadpisujących pamięć."""
    for nazwa in dir(rp):
        assert not any(z in nazwa.lower() for z in ("usun", "kasuj", "nadpisz", "delete", "remove"))


def test_raport_startowy_pusty_gdy_nic(monkeypatch):
    monkeypatch.setattr(rp, "wykryj_sprzecznosci", lambda *a, **k: [])
    monkeypatch.setattr(rp, "wykryj_przedawnienia", lambda *a, **k: [])
    assert rp.raport_startowy() == ""
