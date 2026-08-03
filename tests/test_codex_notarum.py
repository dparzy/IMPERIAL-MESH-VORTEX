"""Testy CODEX NOTARUM (LEX TALIONIS) — noty, korony, oko za oko, granice.

Styl zgodny z run_tests.py: funkcje modułowe test_*(tmp_path) + pytest.raises
(NIE unittest.TestCase — runner zbiera tylko funkcje `test_*` z modułu; klasa
TestCase byłaby cicho pominięta i test nie chroniłby niczego).
"""
import pytest

from imperium.biblioteki import codex_notarum as cn


def test_pusty_ledger_zero(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    b = cn.bilans(led)
    assert (b["noty"], b["korony"], b["saldo"]) == (0, 0, 0)
    assert b["dlug_honorowy"] == []


def test_nota_otwiera_dlug(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    cn.dodaj_nota(opis="błąd X", kategoria="doc", zatwierdzenie="Cezar",
                  sesja="s1", sciezka=led)
    b = cn.bilans(led)
    assert b["noty"] == 1
    assert b["saldo"] == -1
    assert len(b["dlug_honorowy"]) == 1


def test_corona_splaca_oko_za_oko(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    nid = cn.dodaj_nota(opis="błąd Y", kategoria="doc", zatwierdzenie="recenzja",
                        sesja="s1", sciezka=led)
    cn.dodaj_corona(opis="unikat Y", kategoria="mechanizm", zatwierdzenie="Cezar",
                    sesja="s1", splaca=nid, sciezka=led)
    b = cn.bilans(led)
    assert (b["noty"], b["korony"], b["saldo"]) == (1, 1, 0)
    assert b["dlug_honorowy"] == []  # dług spłacony


def test_corona_bez_splaty_nie_zamyka_dlugu(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    cn.dodaj_nota(opis="błąd Z", kategoria="kod", zatwierdzenie="pomiar",
                  sesja="s1", sciezka=led)
    cn.dodaj_corona(opis="wolny unikat", kategoria="idea", zatwierdzenie="Cezar",
                    sesja="s1", splaca=None, sciezka=led)
    b = cn.bilans(led)
    assert b["saldo"] == 0  # +1 corona, -1 nota
    assert len(b["dlug_honorowy"]) == 1  # nota wciąż otwarta


def test_zatwierdzenie_wymagane_nota(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    with pytest.raises(ValueError):
        cn.dodaj_nota(opis="bez dowodu", kategoria="x", zatwierdzenie="",
                      sesja="s1", sciezka=led)


def test_zatwierdzenie_wymagane_corona(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    with pytest.raises(ValueError):
        cn.dodaj_corona(opis="bez dowodu", kategoria="x", zatwierdzenie="   ",
                        sesja="s1", sciezka=led)


def test_opis_pusty_odrzucony(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    with pytest.raises(ValueError):
        cn.dodaj_nota(opis="  ", kategoria="x", zatwierdzenie="Cezar",
                      sesja="s1", sciezka=led)


def test_splaca_nieistniejaca_nota_blad(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    with pytest.raises(ValueError):
        cn.dodaj_corona(opis="u", kategoria="x", zatwierdzenie="Cezar",
                        sesja="s1", splaca="N-deadbeef", sciezka=led)


def test_idempotencja_ten_sam_wpis(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    cn.dodaj_nota(opis="dup", kategoria="x", zatwierdzenie="Cezar",
                  sesja="s1", data="2026-07-19", sciezka=led)
    cn.dodaj_nota(opis="dup", kategoria="x", zatwierdzenie="Cezar",
                  sesja="s1", data="2026-07-19", sciezka=led)
    assert cn.bilans(led)["noty"] == 1  # nie zdublowane


def test_id_deterministyczne(tmp_path):
    a = cn._id("NOTA", "abc", "2026-07-19", "s1")
    b = cn._id("NOTA", "abc", "2026-07-19", "s1")
    assert a == b
    assert a.startswith("N-")


def test_raport_bez_dlugu(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    nid = cn.dodaj_nota(opis="e", kategoria="x", zatwierdzenie="Cezar",
                        sesja="s1", sciezka=led)
    cn.dodaj_corona(opis="u", kategoria="x", zatwierdzenie="Cezar",
                    sesja="s1", splaca=nid, sciezka=led)
    assert "BRAK" in cn.raport(led)


def test_raport_z_dlugiem(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    cn.dodaj_nota(opis="e2", kategoria="x", zatwierdzenie="Cezar",
                  sesja="s1", sciezka=led)
    assert "DŁUG HONOROWY" in cn.raport(led)


# ── ODROCZENIE (2026-08-03): decyzja Cezara o przesunięciu spłaty ────────────────

def test_odroczenie_zdejmuje_blokade_ale_nie_dlug(tmp_path):
    """GRANICA: odroczona nota wychodzi z `dlug_honorowy` (nie blokuje commita),
    ale NADAL jest długiem — widocznym w `odroczone` i w raporcie.

    Powód istnienia mechanizmu: LEX TALIONIS wymaga spłaty w tej samej sesji, a Cezar
    rozkazał zamknąć wachtę i zbudować CORONĘ w następnej. Bez tego rekordu jego rozkaz
    byłby niewykonalny bez obchodzenia bramki — a obchodzenie znika bez śladu.
    """
    led = tmp_path / "codex_notarum.jsonl"
    nid = cn.dodaj_nota(opis="wada X", kategoria="x", zatwierdzenie="Cezar",
                        sesja="s1", sciezka=led)
    assert len(cn.dlug_honorowy(led)) == 1

    cn.dodaj_odroczenie(nota=nid, zatwierdzenie="Cezar 2026-08-03",
                        sesja="s1", plan="CORONA A: LUSTRUM w następnej wachcie", sciezka=led)

    assert cn.dlug_honorowy(led) == [], "odroczona nota nie blokuje commita"
    assert [r["id"] for r in cn.odroczone(led)] == [nid], "…ale dług NIE znika"
    assert "ODROCZONE" in cn.raport(led), "raport musi krzyczeć, inaczej to ciche umorzenie"


def test_odroczenie_bez_planu_odrzucone(tmp_path):
    """Odroczenie bez planu spłaty jest umorzeniem pod inną nazwą — odmawiamy."""
    led = tmp_path / "codex_notarum.jsonl"
    nid = cn.dodaj_nota(opis="wada Y", kategoria="x", zatwierdzenie="Cezar",
                        sesja="s1", sciezka=led)
    with pytest.raises(ValueError):
        cn.dodaj_odroczenie(nota=nid, zatwierdzenie="Cezar", sesja="s1", plan="  ",
                            sciezka=led)


def test_odroczenie_nieistniejacej_noty_odrzucone(tmp_path):
    led = tmp_path / "codex_notarum.jsonl"
    with pytest.raises(ValueError):
        cn.dodaj_odroczenie(nota="N-nieistnieje", zatwierdzenie="Cezar", sesja="s1",
                            plan="cokolwiek", sciezka=led)


def test_corona_splaca_takze_note_odroczona(tmp_path):
    """Odroczenie to PRZESUNIĘCIE, nie zwolnienie: korona nadal ją spłaca i dopiero
    wtedy nota znika z obu list."""
    led = tmp_path / "codex_notarum.jsonl"
    nid = cn.dodaj_nota(opis="wada Z", kategoria="x", zatwierdzenie="Cezar",
                        sesja="s1", sciezka=led)
    cn.dodaj_odroczenie(nota=nid, zatwierdzenie="Cezar", sesja="s1",
                        plan="LUSTRUM", sciezka=led)
    cn.dodaj_corona(opis="LUSTRUM", kategoria="x", zatwierdzenie="Cezar",
                    sesja="s2", splaca=nid, sciezka=led)
    assert cn.dlug_honorowy(led) == [] and cn.odroczone(led) == []
