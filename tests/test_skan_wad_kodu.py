"""Testy narzędzia SKAN WAD KODU (CLI nad Księgą Wad).

Nacisk na filtr wspólny `_filtruj_py` (współdzielony przez skan zmian i skan ostatniego
commitu — A4) i odporność `_py_ostatni_commit` na brak gita/HEAD~1. Reguła Test-Granic.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.biblioteki.ksiega_wad_kodu import KsiegaWadKodu  # noqa: E402
from narzedzia import skan_wad_kodu as skan  # noqa: E402


# ── _filtruj_py: granice filtra ──────────────────────────────────────────────

def test_filtruj_py_zostawia_imperium_i_narzedzia():
    linie = ["imperium/legiony/mikro_neuron.py", "narzedzia/skan_wad_kodu.py"]
    assert skan._filtruj_py(linie) == set(linie)


def test_filtruj_py_odrzuca_nie_py_i_obce_katalogi():
    linie = ["imperium/a.py", "README.md", "tests/test_x.py", "docs/x.py", "b.py"]
    # tylko .py z imperium/ lub narzedzia/ — tests/ i docs/ i root NIE
    assert skan._filtruj_py(linie) == {"imperium/a.py"}


def test_modul_wzorcow_pominiety_takze_gdy_podany_jawnie(tmp_path):
    """REGRESJA na wadę ZMIERZONĄ 2026-08-03: wykluczenie modułu wzorców stało wyłącznie
    w `_filtruj_py`, czyli na drodze „pliki z gita". Plik podany JAWNIE — tak woła VIGIL
    w hooku PostToolUse — omijał je bokiem i dawał 5 fałszywych trafień z własnych opisów
    wzorców. Reguła obowiązująca przy jednym wejściu, a nieegzekwowana przy drugim, to ta
    sama klasa co kontrakt append-only deklarowany w sześciu organach i pilnowany przez zero.
    """
    ksiega = KsiegaWadKodu(tmp_path / "ksiega.json")
    ksiega.dodaj("test", r"^import ", "wzorzec trafiający w każdy moduł", "lekcja", "test")
    modul_wzorcow = skan.ROOT / "imperium" / "biblioteki" / "ksiega_wad_kodu.py"
    inny_modul = skan.ROOT / "narzedzia" / "skan_wad_kodu.py"

    assert skan.skanuj_pliki([modul_wzorcow], ksiega) == [], \
        "moduł wzorców pomijamy niezależnie od tego, jak trafił do skanu"
    assert skan.skanuj_pliki([inny_modul], ksiega), \
        "KONTROLA: ten sam wzorzec MUSI trafiać w zwykły moduł — inaczej test niczego nie dowodzi"


def test_filtruj_py_nie_decyduje_juz_o_wykluczeniach():
    """Filtr przepuszcza moduł wzorców ŚWIADOMIE: o pominięciu decyduje jedno miejsce
    (`_pomijany` przy skanie). Dwa miejsca rozjechałyby się przy pierwszej zmianie."""
    linie = ["imperium/biblioteki/ksiega_wad_kodu.py", "narzedzia/x.py"]
    assert skan._filtruj_py(linie) == set(linie)


def test_filtruj_py_pusta_lista():
    assert skan._filtruj_py([]) == set()


# ── _py_ostatni_commit: odporność (A4) ───────────────────────────────────────

def test_py_ostatni_commit_zwraca_liste():
    """W realnym repo zwraca listę Path (może pustą); NIGDY nie rzuca — start się nie wywala."""
    wynik = skan._py_ostatni_commit()
    assert isinstance(wynik, list)
    assert all(hasattr(p, "exists") for p in wynik)   # elementy to Path


def test_py_ostatni_commit_brak_gita_nie_rzuca(monkeypatch):
    """Granica: git niedostępny / wyjątek subprocess → [] (Prawo I), nie wyjątek."""
    def _wybuch(*a, **k):
        raise FileNotFoundError("git")
    monkeypatch.setattr(skan.subprocess, "run", _wybuch)
    assert skan._py_ostatni_commit() == []


def test_py_ostatni_commit_kod_bledu_git_daje_pusto(monkeypatch):
    """Granica: pierwszy commit repo (brak HEAD~1) → git zwraca !=0 → [] (nie crash)."""
    class _Wynik:
        returncode = 128
        stdout = ""
    monkeypatch.setattr(skan.subprocess, "run", lambda *a, **k: _Wynik())
    assert skan._py_ostatni_commit() == []
