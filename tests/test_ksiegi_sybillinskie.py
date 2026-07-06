"""Testy Ksiąg Sybillińskich (imperium/biblioteki/ksiegi_sybillinskie.py) — Prawo I + XXI.

Testy granic: P∈{0,1}, horyzont dokładnie na progu, nierozstrzygalne, niemutowalność P,
rozstrzyganie z areny, Brier, krzywa kalibracji. Wszystko offline na tmp JSONL + tmp DB.
"""

import logging
logging.disable(logging.CRITICAL)
import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki import ksiegi_sybillinskie as ks


# ─── Tworzenie + walidacja ───────────────────────────────────────────────────

def test_dodaj_zwraca_id_i_zapisuje(tmp_path):
    plik = tmp_path / "p.jsonl"
    sid = ks.dodaj("NEWS-01 ożyje", 0.7, 200, metryka="IC", neuron="NEWS-01",
                   prog=0.02, kierunek="abs>=", plik=plik)
    assert sid == "SYB-0001"
    wpisy = ks._wczytaj(plik)
    assert len(wpisy) == 1 and wpisy[0]["status"] == ks.OTWARTE
    assert wpisy[0]["P"] == 0.7


def test_id_rosnie(tmp_path):
    plik = tmp_path / "p.jsonl"
    ks.dodaj("a", 0.5, 1, plik=plik)
    assert ks.dodaj("b", 0.5, 1, plik=plik) == "SYB-0002"


def test_P_skrajne_dozwolone(tmp_path):
    plik = tmp_path / "p.jsonl"
    assert ks.dodaj("pewne 0", 0.0, 1, plik=plik)     # P=0 dozwolone
    assert ks.dodaj("pewne 1", 1.0, 1, plik=plik)     # P=1 dozwolone


def test_P_poza_zakresem_rzuca(tmp_path):
    plik = tmp_path / "p.jsonl"
    for zle in (-0.01, 1.01):
        try:
            ks.dodaj("x", zle, 1, plik=plik)
            assert False, f"P={zle} powinno rzucić"
        except ValueError:
            pass


def test_horyzont_ujemny_rzuca(tmp_path):
    try:
        ks.dodaj("x", 0.5, -1, plik=tmp_path / "p.jsonl")
        assert False
    except ValueError:
        pass


def test_puste_twierdzenie_rzuca(tmp_path):
    try:
        ks.dodaj("   ", 0.5, 1, plik=tmp_path / "p.jsonl")
        assert False
    except ValueError:
        pass


def test_dedup_pomija_duplikat(tmp_path):
    plik = tmp_path / "p.jsonl"
    ks.dodaj("To samo", 0.5, 1, plik=plik)
    assert ks.dodaj("to samo", 0.6, 2, plik=plik) is None   # case-insensitive dedup
    assert len(ks._wczytaj(plik)) == 1


# ─── Horyzont (granica dokładna) ─────────────────────────────────────────────

def test_horyzont_dokladnie_na_progu_rozliczalny(tmp_path):
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("x", 0.5, 10, plik=plik, data=utw.isoformat())
    # dzień PRZED progiem — jeszcze otwarte
    assert ks.do_rozliczenia(teraz=utw + timedelta(days=9), plik=plik) == 0
    # DOKŁADNIE na progu (>=) — już rozliczalne
    assert ks.do_rozliczenia(teraz=utw + timedelta(days=10), plik=plik) == 1


# ─── Rozstrzyganie z areny ───────────────────────────────────────────────────

def _arena(tmp_path):
    return tmp_path / "arena.db"


def test_rozlicz_trafione_z_areny(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    db = _arena(tmp_path)
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("IC NEWS-01 ≥ 0.02", 0.7, 5, metryka="IC_WAR", neuron="NEWS-01",
             prog=0.02, kierunek="abs>=", plik=plik, data=utw.isoformat())
    zapisz_pomiar("IC_WAR", "NEWS-01", 0.05, db_path=db)   # 0.05 ≥ 0.02 → trafione
    licz = ks.rozlicz(teraz=utw + timedelta(days=5), db_path=db, plik=plik)
    assert licz["trafione"] == 1 and licz["chybione"] == 0
    assert ks._wczytaj(plik)[0]["status"] == ks.TRAFIONE


def test_rozlicz_chybione_z_areny(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    db = _arena(tmp_path)
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("IC ≥ 0.02", 0.7, 5, metryka="IC_WAR", neuron="X", prog=0.02,
             kierunek="abs>=", plik=plik, data=utw.isoformat())
    zapisz_pomiar("IC_WAR", "X", 0.005, db_path=db)        # 0.005 < 0.02 → chybione
    licz = ks.rozlicz(teraz=utw + timedelta(days=5), db_path=db, plik=plik)
    assert licz["chybione"] == 1
    assert ks._wczytaj(plik)[0]["status"] == ks.CHYBIONE


def test_prog_dokladny_ge_vs_gt(tmp_path):
    """Wartość == próg: '>=' trafia, '>' chybia (granica progu)."""
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    db = _arena(tmp_path)
    utw = date(2026, 1, 1)
    for nazwa, kier, oczek in (("ge", "abs>=", ks.TRAFIONE), ("gt", ">", ks.CHYBIONE)):
        plik = tmp_path / f"p_{nazwa}.jsonl"
        ks.dodaj(f"prog {kier}", 0.5, 1, metryka="M", neuron="N", prog=0.02,
                 kierunek=kier, plik=plik, data=utw.isoformat())
        zapisz_pomiar("M", "N", 0.02, db_path=db, ts=1000.0 + len(nazwa))
        ks.rozlicz(teraz=utw + timedelta(days=1), db_path=db, plik=plik)
        assert ks._wczytaj(plik)[0]["status"] == oczek


def test_nierozstrzygalne_gdy_brak_danych(tmp_path):
    """Brak pomiaru w arenie → NIEROZSTRZYGNIETE (jawnie, nie znika — Prawo I)."""
    db = _arena(tmp_path)
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("brak danych", 0.6, 1, metryka="PUSTO", neuron="NIC", prog=0.1,
             plik=plik, data=utw.isoformat())
    licz = ks.rozlicz(teraz=utw + timedelta(days=1), db_path=db, plik=plik)
    assert licz["nierozstrzygniete"] == 1
    assert ks._wczytaj(plik)[0]["status"] == ks.NIEROZSTRZYGNIETE


def test_przed_horyzontem_nie_rozliczane(tmp_path):
    db = _arena(tmp_path)
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("przyszłość", 0.5, 30, metryka="M", neuron="N", plik=plik, data=utw.isoformat())
    licz = ks.rozlicz(teraz=utw + timedelta(days=5), db_path=db, plik=plik)
    assert licz["rozliczone"] == 0 and licz["otwarte"] == 1
    assert ks._wczytaj(plik)[0]["status"] == ks.OTWARTE


def test_reczne_rozstrzygniecie(tmp_path):
    """Proroctwo bez metryki rozstrzygane ręcznie z wyniku walidacji."""
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    sid = ks.dodaj("walidacja bramki przejdzie", 0.6, 1, plik=plik, data=utw.isoformat())
    licz = ks.rozlicz(teraz=utw + timedelta(days=1), plik=plik, wynik_reczny={sid: True})
    assert licz["trafione"] == 1


# ─── Niemutowalność (falsyfikowalność, Prawo I) ──────────────────────────────

def test_rozlicz_nie_zmienia_P_ani_twierdzenia(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    db = _arena(tmp_path)
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("nietykalne", 0.73, 1, metryka="M", neuron="N", prog=0.0,
             kierunek=">=", plik=plik, data=utw.isoformat())
    zapisz_pomiar("M", "N", 1.0, db_path=db)
    ks.rozlicz(teraz=utw + timedelta(days=1), db_path=db, plik=plik)
    w = ks._wczytaj(plik)[0]
    assert w["P"] == 0.73                     # P nietknięte
    assert w["twierdzenie"] == "nietykalne"   # twierdzenie nietknięte
    assert w["status"] == ks.TRAFIONE and w["zmierzono"] == 1.0


def test_ponowny_rozlicz_nie_rusza_rozstrzygnietych(tmp_path):
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    db = _arena(tmp_path)
    plik = tmp_path / "p.jsonl"
    utw = date(2026, 1, 1)
    ks.dodaj("raz", 0.5, 1, metryka="M", neuron="N", prog=0.0, kierunek=">=",
             plik=plik, data=utw.isoformat())
    zapisz_pomiar("M", "N", 1.0, db_path=db)
    ks.rozlicz(teraz=utw + timedelta(days=1), db_path=db, plik=plik)
    licz2 = ks.rozlicz(teraz=utw + timedelta(days=1), db_path=db, plik=plik)
    assert licz2["rozliczone"] == 0           # już rozstrzygnięte — pomijane


# ─── Brier + kalibracja ──────────────────────────────────────────────────────

def test_brier_none_gdy_pusto(tmp_path):
    assert ks.brier(plik=tmp_path / "p.jsonl") is None


def test_brier_liczy_znane_wartosci(tmp_path):
    """P=1.0 trafione (0²) + P=0.0 chybione (0²) → Brier 0.0 (doskonała samowiedza)."""
    plik = tmp_path / "p.jsonl"
    # dwa proroctwa rozstrzygnięte ręcznie, znane wyniki
    a = ks.dodaj("A", 1.0, 0, plik=plik, data="2026-01-01")
    b = ks.dodaj("B", 0.0, 0, plik=plik, data="2026-01-01")
    ks.rozlicz(teraz=date(2026, 1, 2), plik=plik, wynik_reczny={a: True, b: False})
    wynik = ks.brier(plik=plik)
    assert wynik["n"] == 2 and wynik["brier"] == 0.0
    assert wynik["trafien"] == 1


def test_brier_rzut_moneta(tmp_path):
    """P=0.5, wynik trafiony → (0.5-1)²=0.25."""
    plik = tmp_path / "p.jsonl"
    a = ks.dodaj("A", 0.5, 0, plik=plik, data="2026-01-01")
    ks.rozlicz(teraz=date(2026, 1, 2), plik=plik, wynik_reczny={a: True})
    assert ks.brier(plik=plik)["brier"] == 0.25


def test_krzywa_kalibracji_kubelki(tmp_path):
    plik = tmp_path / "p.jsonl"
    a = ks.dodaj("wysokie P", 1.0, 0, plik=plik, data="2026-01-01")    # kubełek ostatni
    b = ks.dodaj("niskie P", 0.1, 0, plik=plik, data="2026-01-01")     # kubełek pierwszy
    ks.rozlicz(teraz=date(2026, 1, 2), plik=plik, wynik_reczny={a: True, b: False})
    krzywa = ks.krzywa_kalibracji(kubelki=5, plik=plik)
    assert len(krzywa) == 2                        # dwa niepuste kubełki
    # P=1.0 nie wychodzi poza ostatni kubełek (bug graniczny idx == kubelki)
    assert all(g["n"] == 1 for g in krzywa)


def test_krzywa_zero_kubelkow(tmp_path):
    assert ks.krzywa_kalibracji(kubelki=0, plik=tmp_path / "p.jsonl") == []
