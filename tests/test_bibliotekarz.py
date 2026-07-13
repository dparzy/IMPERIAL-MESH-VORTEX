"""Testy Bibliotekarza-Zwiadowcy (narzedzia/bibliotekarz.py) — dyscyplina i cząstki.

Nie dotykamy DeepSeek API (koszt) — testujemy pure logic + ścieżkę dry-run (glos=None)."""
import sys
import os
import json
from collections import namedtuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "narzedzia", "rag"))

from narzedzia.bibliotekarz import _fragmenty_tekst, scout_temat, _SYSTEM

_FakeWynik = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")


def test_fragmenty_tekst_cytuje_zrodlo_i_przycina():
    w = _FakeWynik("BIB-010", "Chan", 122, "x" * 2000, -1.0, "biblioteka")
    txt = _fragmenty_tekst([w])
    assert "BIB-010" in txt and "Chan" in txt and "chunk 122" in txt
    # tekst przycięty do 900 znaków (ochrona kontekstu/tokenów)
    assert txt.count("x") == 900


def test_system_prompt_wymusza_dyscypline():
    # ŻELAZNE ZASADY: hipoteza nie fakt, cytuj źródło, jak zmierzyć, nie konfabuluj
    for fraza in ["HIPOTEZA", "BIB-xxx", "ZMIERZYĆ", "konfabuluj"]:
        assert fraza in _SYSTEM


def test_scout_dry_run_nie_wola_api():
    # glos=None → ścieżka dry-run: zwraca dict bez wywołania DeepSeek (RAG realny, szybki FTS)
    czastka = scout_temat(None, "mean reversion", topk=3, tryb="fts")
    assert czastka["temat"] == "mean reversion"
    assert "kandydaci" in czastka and "ts" in czastka
    assert czastka["kandydaci"] in ("(dry-run — DeepSeek pominięty)", "(brak fragmentów RAG)")


def test_czastka_jest_json_serializowalna():
    czastka = {"temat": "x", "zrodla": ["BIB-001"], "kandydaci": "⚠️ kandydat", "ts": 1.0}
    odczyt = json.loads(json.dumps(czastka, ensure_ascii=False))
    assert odczyt["kandydaci"] == "⚠️ kandydat" and odczyt["zrodla"] == ["BIB-001"]
