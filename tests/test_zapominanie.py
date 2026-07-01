"""
Testy Mądrego Zapominania (W10 — learned forgetting, W-360 v10).

Weryfikuje:
  • wartosc_retencji() — ważność×świeżość + bonus łączności; plany chronione,
  • kandydaci_do_zapomnienia() — niska retencja + wiek; świeże/cenne pominięte,
  • anti-utrwalanie: brak metod kasujących (tylko propozycja),
  • granice: brak daty, status otwarty chroniony, próg.
"""

from datetime import date

from imperium.biblioteki import zapominanie as zp


def test_retencja_swieza_wyzsza_niz_stara():
    swieza = {"tytul": "notatka", "tresc": "x", "data": date.today().isoformat(), "status": ""}
    stara = {"tytul": "notatka", "tresc": "x", "data": "2020-01-01", "status": ""}
    assert zp.wartosc_retencji(swieza, stopnie={}) > zp.wartosc_retencji(stara, stopnie={})


def test_retencja_wazna_wyzsza():
    wazna = {"tytul": "bug krytyczny utrata potencjału", "tresc": "naprawa",
             "data": "2024-01-01", "status": ""}
    blaha = {"tytul": "drobna notatka", "tresc": "nic", "data": "2024-01-01", "status": ""}
    assert zp.wartosc_retencji(wazna, stopnie={}) > zp.wartosc_retencji(blaha, stopnie={})


def test_plan_otwarty_chroniony():
    """POMYSŁ/PLANOWANE dostaje retencję ≥0.5 nawet gdy stary (nie zapominaj niezałatwionego)."""
    stary_plan = {"tytul": "stary pomysł", "tresc": "x", "data": "2020-01-01", "status": "POMYSŁ"}
    assert zp.wartosc_retencji(stary_plan, stopnie={}) >= 0.5


def test_bonus_lacznosci_podnosi_retencje():
    wpis = {"tytul": "numba viterbi", "tresc": "jit", "data": "2024-01-01", "status": ""}
    bez = zp.wartosc_retencji(wpis, stopnie={})
    zlaczony = zp.wartosc_retencji(wpis, stopnie={"numba": 50, "viterbi": 40, "jit": 30})
    assert zlaczony > bez


def test_kandydaci_stara_blaha(monkeypatch):
    monkeypatch.setattr(zp, "_zrodla", lambda: [
        {"zrodlo": "lekcje", "tytul": "drobiazg", "tresc": "nic", "data": "2020-01-01", "status": ""},
    ])
    monkeypatch.setattr(zp, "_stopien_w_grafie", lambda: {})
    kand = zp.kandydaci_do_zapomnienia(prog=0.15, dni=30)
    assert kand and kand[0]["tytul"] == "drobiazg"


def test_kandydaci_swieza_pomijana(monkeypatch):
    monkeypatch.setattr(zp, "_zrodla", lambda: [
        {"zrodlo": "lekcje", "tytul": "drobiazg", "tresc": "nic",
         "data": date.today().isoformat(), "status": ""},
    ])
    monkeypatch.setattr(zp, "_stopien_w_grafie", lambda: {})
    assert zp.kandydaci_do_zapomnienia(prog=0.15, dni=30) == []


def test_kandydaci_cenna_stara_pomijana(monkeypatch):
    """Stara ale WAŻNA (bug/utrata) — nad progiem, nie kandyduje."""
    monkeypatch.setattr(zp, "_zrodla", lambda: [
        {"zrodlo": "lekcje", "tytul": "bug krytyczny utrata potencjału GARCH",
         "tresc": "naprawa szczegóły", "data": "2024-06-01", "status": ""},
    ])
    monkeypatch.setattr(zp, "_stopien_w_grafie", lambda: {})
    kand = zp.kandydaci_do_zapomnienia(prog=0.05, dni=30)
    assert kand == []


def test_brak_daty_pomijany(monkeypatch):
    monkeypatch.setattr(zp, "_zrodla", lambda: [
        {"zrodlo": "wizje", "tytul": "x", "tresc": "y", "data": "", "status": ""},
    ])
    monkeypatch.setattr(zp, "_stopien_w_grafie", lambda: {})
    assert zp.kandydaci_do_zapomnienia() == []


def test_anti_utrwalanie_brak_metod_kasujacych():
    for nazwa in dir(zp):
        assert not any(z in nazwa.lower() for z in ("usun", "kasuj", "nadpisz", "delete", "remove"))


def test_raport_startowy_pusty_gdy_brak(monkeypatch):
    monkeypatch.setattr(zp, "kandydaci_do_zapomnienia", lambda *a, **k: [])
    assert zp.raport_startowy() == ""


# ── GRANICE (Reguła Test-Granic, Prawo XXI) ───────────────────────────────────

def test_kandydaci_dokladnie_prog_wieku(monkeypatch):
    """dni graniczne: wiek == dni → wiek < dni False → NIE pomija (kwalifikuje)."""
    from datetime import date as _d
    data30 = _d.fromordinal(_d.today().toordinal() - 30).isoformat()
    monkeypatch.setattr(zp, "_zrodla", lambda: [
        {"zrodlo": "lekcje", "tytul": "drobiazg", "tresc": "nic", "data": data30, "status": ""}])
    monkeypatch.setattr(zp, "_stopien_w_grafie", lambda: {})
    # prog=0.6 izoluje granicę WIEKU (retencja ~0.22 < 0.6): wiek==30 nie jest pomijany
    assert zp.kandydaci_do_zapomnienia(prog=0.6, dni=30)   # wiek==30 kwalifikuje (>= dni)


def test_kandydaci_prog_zero_nic(monkeypatch):
    """prog=0: r < 0 nigdy prawdziwe → zero kandydatów (retencja zawsze ≥0)."""
    monkeypatch.setattr(zp, "_zrodla", lambda: [
        {"zrodlo": "lekcje", "tytul": "x", "tresc": "y", "data": "2020-01-01", "status": ""}])
    monkeypatch.setattr(zp, "_stopien_w_grafie", lambda: {})
    assert zp.kandydaci_do_zapomnienia(prog=0.0, dni=30) == []


def test_plan_dokladnie_prog_retencji():
    """Plan otwarty: retencja == 0.5 dokładnie (granica max(...,0.5))."""
    stary = {"tytul": "x", "tresc": "y", "data": "2020-01-01", "status": "PLANOWANE"}
    assert zp.wartosc_retencji(stary, stopnie={}) == 0.5
