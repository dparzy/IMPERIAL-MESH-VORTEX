"""Testy Pamięci Proceduralnej (W11 — CoALA procedural, W-360 v11)."""

from imperium.biblioteki import pamiec_proceduralna as pp


def test_dodaj_i_pobierz(tmp_path):
    plik = tmp_path / "p.jsonl"
    assert pp.dodaj("Zrób X", ["krok1", "krok2"], "x,robienie", plik=plik)
    pr = pp.pobierz("Zrób X", plik=plik)
    assert pr and pr["kroki"] == ["krok1", "krok2"]
    assert "x" in pr["wyzwalacz"]


def test_dedup_nazwy(tmp_path):
    plik = tmp_path / "p.jsonl"
    assert pp.dodaj("Proc", ["a"], plik=plik) is True
    assert pp.dodaj("Proc", ["b"], plik=plik) is False
    assert len(pp.wszystkie(plik=plik)) == 1


def test_szukaj_po_slowach(tmp_path):
    plik = tmp_path / "p.jsonl"
    pp.dodaj("Dodać neuron", ["klasa", "rejestr"], "neuron,mikroneuron", plik=plik)
    pp.dodaj("Commit", ["testy", "push"], "commit,push", plik=plik)
    w = pp.szukaj("jak dodać neuron", plik=plik)
    assert w and w[0]["nazwa"] == "Dodać neuron"


def test_szukaj_puste(tmp_path):
    plik = tmp_path / "p.jsonl"
    assert pp.szukaj("", plik=plik) == []


def test_zasiej_idempotentne(tmp_path):
    plik = tmp_path / "p.jsonl"
    n1 = pp.zasiej(plik=plik)
    n2 = pp.zasiej(plik=plik)        # drugi raz: nic nowego (dedup)
    assert n1 >= 4 and n2 == 0


def test_raport_startowy(tmp_path):
    plik = tmp_path / "p.jsonl"
    assert pp.raport_startowy(plik=plik) == ""   # pusto
    pp.dodaj("X", ["k"], plik=plik)
    assert "proceduralna" in pp.raport_startowy(plik=plik)
