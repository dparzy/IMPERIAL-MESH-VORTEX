"""Testy KsiegaWadKodu (pamięć wzorców błędów + skaner) — z granicami."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from imperium.biblioteki.ksiega_wad_kodu import (
    WZORCE_STARTOWE,
    CHECKLIST_STARTOWA,
    KsiegaWadKodu,
    zasiej_startowe,
)


def test_dodaj_i_skanuj(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert k.dodaj("odpornosc", r"eval\(", "użycie eval", "nie używaj eval")
    trafienia = k.skanuj("x = eval('2+2')\n")
    assert len(trafienia) == 1 and trafienia[0]["linia"] == 1


def test_dodaj_duplikat_regex_odrzucony(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert k.dodaj("a", r"foo", "o1", "l1") is True
    assert k.dodaj("a", r"foo", "o2", "l2") is False   # ten sam regex → nie dubluj
    assert len(k.wszystkie()) == 1


def test_dodaj_pusty_lub_zly_regex_rzuca(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    with pytest.raises(ValueError):
        k.dodaj("a", "", "opis", "lekcja")       # pusty regex
    with pytest.raises(ValueError):
        k.dodaj("a", r"(niezamkniety", "o", "l")  # błędny regex


def test_skanuj_brak_trafien(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    k.dodaj("a", r"eval\(", "o", "l")
    assert k.skanuj("czysty = kod()\n") == []


def test_skanuj_numer_linii(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    k.dodaj("a", r"BUG", "o", "l")
    assert k.skanuj("linia1\nlinia2\nBUG tutaj\n")[0]["linia"] == 3


def test_persystencja_zapis_odczyt(tmp_path):
    sciezka = tmp_path / "k.jsonl"
    k = KsiegaWadKodu(sciezka)
    k.dodaj("a", r"foo", "o", "l", "src")
    k.zapisz()
    k2 = KsiegaWadKodu(sciezka)           # świeże wczytanie
    assert len(k2.wszystkie()) == 1 and k2.wszystkie()[0]["zrodlo"] == "src"


def test_zasiej_startowe_idempotentne(tmp_path):
    sciezka = tmp_path / "k.jsonl"
    n1 = zasiej_startowe(sciezka)
    assert n1 == len(WZORCE_STARTOWE) + len(CHECKLIST_STARTOWA)   # wzorce + checklista
    n2 = zasiej_startowe(sciezka)          # drugi raz nic nie dodaje (dedup regex + opis)
    assert n2 == 0


def test_wzorce_startowe_maja_poprawne_regexy():
    import re
    for w in WZORCE_STARTOWE:
        re.compile(w["regex"])             # nie rzuca = poprawny


def test_wzorzec_startowy_lapie_order_by_id(tmp_path):
    zasiej_startowe(tmp_path / "k.jsonl")
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert any(t["kat"] == "kontrakt" for t in k.skanuj('conn.execute("... ORDER BY id DESC LIMIT ?")'))


# ── Żywotność wzorców (recenzja cubic PR #118, P2) ───────────────────────────
# Wzorzec, który nie trafia w żaden kod, jest gorszy niż jego brak: daje złudzenie
# ochrony. Wpis `podobienstwo` miał nadmiernie zescapowane klamry po round-tripie przez
# JSONL (`\d\{2,\}`) i milczał. Tu trzymamy dowód, że wzorce z tej sesji żyją.

_KOD_Z_WADA_PODOBIENSTWO = (
    'def sygnatura_lekcji(tytul, tresc):\n'
    '    tokeny = re.findall(r"\d{2,}", tytul + tresc)   # daty wchodzą do sygnatury!\n'
)
_KOD_NAPRAWIONY = (
    '_WZOR_DATY = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")\n'
    'def sygnatura_lekcji(tytul, tresc):\n'
    '    tekst = _WZOR_DATY.sub(" ", f"{tytul} {tresc}")\n'
    '    tokeny = _WZOR_TOKENU.findall(tekst)\n'
)
_KOD_Z_WADA_CACHE = (
    'for linia in plik.read_text().splitlines():\n'
    '    znaczniki.update(linia.split())   # hasz i ID w jednym zbiorze\n'
)


def test_kazdy_wzorzec_ksiegi_sie_kompiluje():
    import re as _re
    for w in KsiegaWadKodu().wszystkie():
        _re.compile(w["regex"])          # re.error => test czerwony


def test_wzorzec_podobienstwa_zyje():
    traf = [t for t in KsiegaWadKodu().skanuj(_KOD_Z_WADA_PODOBIENSTWO)
            if t["kat"] == "podobienstwo"]
    assert traf, "wzorzec 'podobienstwo' martwy — nie trafia w kod, dla którego powstał"


def test_wzorzec_podobienstwa_milczy_gdy_daty_wycinane():
    traf = [t for t in KsiegaWadKodu().skanuj(_KOD_NAPRAWIONY) if t["kat"] == "podobienstwo"]
    assert not traf, "fałszywy alarm na kodzie, który wycina daty przed tokenizacją"


def test_wzorzec_cache_zyje():
    traf = [t for t in KsiegaWadKodu().skanuj(_KOD_Z_WADA_CACHE) if t["kat"] == "cache"]
    assert traf, "wzorzec 'cache' martwy — nie trafia w kod, dla którego powstał"


# ── cubic PR#122: nowe wzorce regex (żyje + milczy) + warstwa checklisty ─────────

def test_wzorzec_klucz_areny_zyje_i_milczy():
    k = KsiegaWadKodu()
    bug = "rek = pytaj_pomiary(rodzaj=_RODZAJ, neuron=nazwa, limit=1)"
    fix = "rek = pytaj_pomiary(rodzaj=rodzaj, neuron=klucz, limit=1)"
    assert any(t["kat"] == "cache" for t in k.skanuj(bug)), "wzorzec klucza areny martwy"
    assert not any(t["kat"] == "cache" for t in k.skanuj(fix)), "fałszywy alarm na kluczu z config"


def test_wzorzec_arg_liczbowy_zyje_i_milczy():
    k = KsiegaWadKodu()
    bug = 'p.add_argument("--topk", type=int, default=6)'
    fix = 'p.add_argument("--topk", type=_topk_arg, default=6)'
    inny = 'p.add_argument("--okno", type=int, default=250)'   # inny arg — bez walidacji OK
    assert any(t["kat"] == "granice" for t in k.skanuj(bug)), "wzorzec --topk martwy"
    assert not any(t["kat"] == "granice" and "kosztem" in t["lekcja"] for t in k.skanuj(fix))
    assert not any("kosztem" in t["lekcja"] for t in k.skanuj(inny)), "nie łapiemy zwykłych argów liczbowych"


def test_checklista_nie_auto_skanuje(tmp_path):
    # Pozycja checklisty (pusty regex) NIE może trafiać w kod — inaczej pusty regex łapie wszystko.
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert k.dodaj_checklist("kierunek", "flip bez propagacji", "propaguj kierunek efektywny")
    assert k.skanuj('cokolwiek = "SHORT" if x == "LONG" else "LONG"\n') == []
    assert k.skanuj("") == []


def test_dodaj_checklist_dedup_po_opisie(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert k.dodaj_checklist("a", "ten sam opis", "l1") is True
    assert k.dodaj_checklist("a", "ten sam opis", "l2") is False   # dedup po opisie
    assert len(k.checklista()) == 1


def test_dodaj_checklist_wymaga_opisu_i_lekcji(tmp_path):
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    with pytest.raises(ValueError):
        k.dodaj_checklist("a", "", "lekcja")
    with pytest.raises(ValueError):
        k.dodaj_checklist("a", "opis", "")


def test_zasiej_dodaje_checkliste_i_partycjonuje(tmp_path):
    zasiej_startowe(tmp_path / "k.jsonl")
    k = KsiegaWadKodu(tmp_path / "k.jsonl")
    assert len(k.wzorce()) == len(WZORCE_STARTOWE)
    assert len(k.checklista()) == len(CHECKLIST_STARTOWA)
    assert len(k.wszystkie()) == len(WZORCE_STARTOWE) + len(CHECKLIST_STARTOWA)
    # wzorce mają regex, checklista nie — rozłączność
    assert all(w["regex"] for w in k.wzorce())
    assert all(not w["regex"] for w in k.checklista())


def test_checklist_startowa_ma_komplet_pol():
    for c in CHECKLIST_STARTOWA:
        assert c["opis"] and c["lekcja"] and c["kat"]
