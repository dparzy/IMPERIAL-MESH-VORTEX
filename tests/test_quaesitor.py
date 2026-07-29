#!/usr/bin/env python3
"""
Testy QUAESITORA — organu mierzącego JAKOŚĆ WYSZUKIWANIA w Bibliotheca-RAG.

DLACZEGO ISTNIEJĄ: QUAESITOR ma dostarczyć jedyną liczbę rozstrzygającą kryterium K10
w NORMIE — czyli zdecydować, czy przepinamy indeks na REDDITORA i czy budujemy wektory.
Wszedł do repozytorium bez ani jednego testu, a recenzja własna (2026-07-29) znalazła
w nim DWA realne błędy, których bramka nie widziała:

  1. klucz `recall@10` trzymał `rec(min(10, topk))`, a raport drukował stałe etykiety —
     bieg z `--topk 3` pokazywał recall@3 w kolumnie podpisanej „@10";
  2. `sqlite3.OperationalError` był zamieniany na pustą listę i przy domyślnym
     `postep=False` awaria zapytania wchodziła do metryk jako zwykły brak trafienia,
     bez śladu w raporcie.

Oba są przypięte niżej. Testy NIE dotykają prawdziwej bazy — metryki liczymy na
sztucznych przypadkach o znanej z góry odpowiedzi, bo tylko wtedy „poprawny wynik"
jest faktem (LEX TALARUS).
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
for p in (KORZEN, KORZEN / "narzedzia" / "rag"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import quaesitor as Q  # noqa: E402


class _W:
    """Atrapa wyniku wyszukiwania — liczy się wyłącznie pole `zrodlo`."""

    def __init__(self, zrodlo: str):
        self.zrodlo = zrodlo


# ── Identyfikator BIB ─────────────────────────────────────────────────────────

def test_bib_wyciaga_identyfikator():
    assert Q._bib("BIB-007_Lopez-de-Prado_Advances__abc.epub") == "BIB-007"


def test_bib_na_nie_ksiazce_zwraca_pusty():
    assert Q._bib("docs/ROADMAP.md") == ""
    assert Q._bib("") == ""
    assert Q._bib(None) == ""


# ── Składnia OR (ścieżka HYGINUSA) ────────────────────────────────────────────

def test_fts_or_laczy_slowa_alternatywa():
    assert Q._fts_or("flow toxicity VPIN") == "flow OR toxicity OR VPIN"


def test_fts_or_bez_slow_zwraca_wejscie():
    assert Q._fts_or("!!!") == "!!!"


# ── Pozycja trafienia ─────────────────────────────────────────────────────────

def test_pozycja_jest_1_indeksowana():
    wyniki = [_W("BIB-001_A__x.epub"), _W("BIB-007_B__y.epub")]
    assert Q._pozycja_trafienia(wyniki, ("BIB-007",)) == 2


def test_pozycja_brak_trafienia_to_None():
    assert Q._pozycja_trafienia([_W("BIB-001_A__x.epub")], ("BIB-099",)) is None


def test_pozycja_bierze_PIERWSZE_dopuszczalne_zrodlo():
    """Zbiór celów, nie jeden cel — trafienie w drugą dopuszczalną książkę to trafienie."""
    wyniki = [_W("BIB-155_G__x.epub"), _W("BIB-161_M__y.epub")]
    assert Q._pozycja_trafienia(wyniki, ("BIB-161", "BIB-155")) == 1


# ── Metryki: progi liczone z topk, nie wpisane na sztywno ─────────────────────

def _ocen_na_atrapie(monkeypatch, trafienia: list[int | None], topk: int) -> dict:
    """Uruchamia `ocen` na sztucznym zbiorze o ZNANYCH pozycjach trafień."""
    zbior = tuple(
        {"id": f"P{i}", "klasa": "doslowna", "pytanie": f"pytanie {i}",
         "zrodla_ok": ("BIB-001",)}
        for i in range(len(trafienia))
    )
    kolejka = list(trafienia)

    def fake_szukaj(q, topk, tryb, baza, cichy, skladnia="or"):
        poz = kolejka.pop(0)
        wyniki = [_W(f"BIB-{900 + j}__x.epub") for j in range(topk)]
        if poz is not None and poz <= topk:
            wyniki[poz - 1] = _W("BIB-001_Cel__x.epub")
        return wyniki

    import szukaj as modul_szukaj
    monkeypatch.setattr(modul_szukaj, "szukaj", fake_szukaj)
    monkeypatch.setattr(Q, "zaindeksowane", lambda baza=None: {"BIB-001"})
    return Q.ocen(topk=topk, zbior=zbior)


def test_progi_recall_pochodza_z_topk(monkeypatch):
    """Sedno błędu #1: przy topk=3 nie wolno raportować recall@10."""
    w = _ocen_na_atrapie(monkeypatch, [1, 2, 3], topk=3)
    assert w["globalne"]["progi"] == [1, 3], w["globalne"]["progi"]
    assert 10 not in w["globalne"]["recall"]


def test_progi_pelne_przy_topk_10(monkeypatch):
    w = _ocen_na_atrapie(monkeypatch, [1, 5, None], topk=10)
    assert w["globalne"]["progi"] == [1, 5, 10]


def test_recall_liczony_poprawnie(monkeypatch):
    """Prawda znana z góry: trafienia na pozycjach 1, 3 i brak → recall@1=1/3."""
    w = _ocen_na_atrapie(monkeypatch, [1, 3, None], topk=10)
    r = w["globalne"]["recall"]
    assert r[1] == 1 / 3
    assert r[5] == 2 / 3
    assert r[10] == 2 / 3


def test_mrr_liczony_poprawnie(monkeypatch):
    """MRR dla pozycji 1 i 2 = (1/1 + 1/2)/2 = 0.75."""
    w = _ocen_na_atrapie(monkeypatch, [1, 2], topk=10)
    assert abs(w["globalne"]["mrr"] - 0.75) < 1e-9


def test_brak_trafienia_nie_wnosi_do_mrr(monkeypatch):
    w = _ocen_na_atrapie(monkeypatch, [None, None], topk=10)
    assert w["globalne"]["mrr"] == 0.0
    assert w["globalne"]["recall"][1] == 0.0


def test_raport_naglowek_pokazuje_faktyczne_progi(monkeypatch):
    w = _ocen_na_atrapie(monkeypatch, [1, 2, 3], topk=3)
    txt = Q.raport(w)
    assert "recall@3" in txt
    assert "recall@10" not in txt, "etykieta obiecuje próg, którego nie zmierzono"


# ── Awaria zapytania MUSI być widoczna ────────────────────────────────────────

def test_blad_fts_jest_LICZONY_i_widoczny_w_raporcie(monkeypatch):
    """Sedno błędu #2: awaria MATCH nie może udawać zwykłego braku trafień."""
    zbior = ({"id": "P0", "klasa": "doslowna", "pytanie": "a-b",
              "zrodla_ok": ("BIB-001",)},)

    def wybuchowy(q, topk, tryb, baza, cichy, skladnia="or"):
        raise sqlite3.OperationalError('fts5: syntax error near "-"')

    import szukaj as modul_szukaj
    monkeypatch.setattr(modul_szukaj, "szukaj", wybuchowy)
    monkeypatch.setattr(Q, "zaindeksowane", lambda baza=None: {"BIB-001"})

    w = Q.ocen(topk=10, zbior=zbior)
    assert len(w["bledy"]) == 1, w["bledy"]
    assert w["globalne"]["recall"][1] == 0.0     # nadal liczone jako brak — tak działa produkcja
    txt = Q.raport(w)
    assert "WYSYPAŁY" in txt, "raport milczy o awarii, więc zaniżony recall wygląda na winę BM25"


def test_udane_zapytanie_nie_zostawia_bledu(monkeypatch):
    w = _ocen_na_atrapie(monkeypatch, [1], topk=10)
    assert w["bledy"] == []
    assert all(p["blad"] == "" for p in w["przypadki"])


# ── Cel poza indeksem: pomijany, nie karany ───────────────────────────────────

def test_cel_poza_indeksem_jest_pomijany_nie_liczony_jako_porazka(monkeypatch):
    zbior = ({"id": "P0", "klasa": "doslowna", "pytanie": "x", "zrodla_ok": ("BIB-777",)},)
    import szukaj as modul_szukaj
    monkeypatch.setattr(modul_szukaj, "szukaj", lambda **k: [])
    monkeypatch.setattr(Q, "zaindeksowane", lambda baza=None: {"BIB-001"})
    w = Q.ocen(topk=10, zbior=zbior)
    assert len(w["pominiete"]) == 1
    assert w["globalne"]["n"] == 0
    assert w["globalne"]["recall"][1] is None, "pominięty cel nie może zaniżać recallu"


def test_raport_pustego_zbioru_nie_wybucha(monkeypatch):
    import szukaj as modul_szukaj
    monkeypatch.setattr(modul_szukaj, "szukaj", lambda **k: [])
    monkeypatch.setattr(Q, "zaindeksowane", lambda baza=None: set())
    w = Q.ocen(topk=10, zbior=())
    assert "QUAESITOR" in Q.raport(w)


# ── Walidacja topk ────────────────────────────────────────────────────────────

def test_topk_poza_zakresem_odrzucony():
    import argparse
    for zly in ("0", "101", "-3"):
        try:
            Q._topk(zly)
        except argparse.ArgumentTypeError:
            continue
        raise AssertionError(f"topk={zly} powinien zostać odrzucony")


def test_topk_w_zakresie_przyjety():
    assert Q._topk("10") == 10
