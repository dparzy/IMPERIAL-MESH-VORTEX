"""Testy narzędzia SKAN WAD KODU (CLI nad Księgą Wad).

Nacisk na filtr wspólny `_filtruj_py` (współdzielony przez skan zmian i skan ostatniego
commitu — A4) i odporność `_py_ostatni_commit` na brak gita/HEAD~1. Reguła Test-Granic.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narzedzia import skan_wad_kodu as skan  # noqa: E402


# ── _filtruj_py: granice filtra ──────────────────────────────────────────────

def test_filtruj_py_zostawia_imperium_i_narzedzia():
    linie = ["imperium/legiony/mikro_neuron.py", "narzedzia/skan_wad_kodu.py"]
    assert skan._filtruj_py(linie) == set(linie)


def test_filtruj_py_odrzuca_nie_py_i_obce_katalogi():
    linie = ["imperium/a.py", "README.md", "tests/test_x.py", "docs/x.py", "b.py"]
    # tylko .py z imperium/ lub narzedzia/ — tests/ i docs/ i root NIE
    assert skan._filtruj_py(linie) == {"imperium/a.py"}


def test_filtruj_py_wyklucza_sam_modul_wzorcow():
    """Księga wzorców trzyma regexy jako dane → trafiałaby w siebie; musi być wykluczona."""
    linie = ["imperium/biblioteki/ksiega_wad_kodu.py", "narzedzia/x.py"]
    assert skan._filtruj_py(linie) == {"narzedzia/x.py"}


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
