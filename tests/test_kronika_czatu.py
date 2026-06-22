"""
Testy Kroniki Czatu (W-360) — trwała pamięć całej rozmowy.

Weryfikuje:
  • destyluj_jsonl() wyciąga TYLKO dialog (user+assistant text), odrzuca tool_use/tool_result,
  • redakcja sekretów (klucze API NIGDY w repo — Prawo Bezpieczeństwa),
  • eksportuj() przyrostowy (tylko_nowe pomija istniejące),
  • szukaj() znajduje fragment,
  • granice: pusty plik, brak katalogu, uszkodzona linia JSON.
"""

import json
import tempfile
from pathlib import Path

from imperium.biblioteki import kronika_czatu as kc


def _jsonl(linie, d=None) -> Path:
    d = d or tempfile.mkdtemp()
    p = Path(d) / "sesja1.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in linie), encoding="utf-8")
    return p


def test_destyluj_wyciaga_dialog():
    src = _jsonl([
        {"message": {"role": "user", "content": "Pytanie Cezara"}},
        {"message": {"role": "assistant", "content": [{"type": "text", "text": "Odpowiedź"}]}},
    ])
    d = kc.destyluj_jsonl(src)
    assert len(d) == 2
    assert d[0] == {"rola": "user", "tekst": "Pytanie Cezara"}
    assert d[1]["tekst"] == "Odpowiedź"


def test_destyluj_odrzuca_tool_szum():
    """tool_use / tool_result NIE są dialogiem → pomijane."""
    src = _jsonl([
        {"message": {"role": "user", "content": "pytanie"}},
        {"message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
            {"type": "text", "text": "realny tekst"},
        ]}},
        {"type": "tool_result", "message": {"role": "tool", "content": "wynik"}},
    ])
    d = kc.destyluj_jsonl(src)
    teksty = [x["tekst"] for x in d]
    assert "realny tekst" in teksty
    assert all("ls" not in t for t in teksty)        # komenda narzędzia nie wycieka


def test_redakcja_sekretow():
    """Klucze API muszą być zredagowane zanim trafią do repo."""
    src = _jsonl([
        {"message": {"role": "user", "content": "klucz to sk-abcdef0123456789ABCDEF i koniec"}},
        {"message": {"role": "assistant", "content": "DEEPSEEK_API_KEY=supertajnehaslo123"}},
    ])
    d = kc.destyluj_jsonl(src)
    blob = " ".join(x["tekst"] for x in d)
    assert "sk-abcdef0123456789ABCDEF" not in blob
    assert "supertajnehaslo123" not in blob
    assert "[ZREDAGOWANO]" in blob


def test_destyluj_uszkodzona_linia():
    d = tempfile.mkdtemp()
    p = Path(d) / "sesja1.jsonl"
    p.write_text('{"message":{"role":"user","content":"ok"}}\nTO NIE JSON\n', encoding="utf-8")
    out = kc.destyluj_jsonl(p)
    assert len(out) == 1 and out[0]["tekst"] == "ok"


def test_destyluj_nieistniejacy():
    assert kc.destyluj_jsonl(Path("/nieistnieje/x.jsonl")) == []


def test_eksportuj_i_przyrostowy():
    zrodlo = Path(tempfile.mkdtemp())
    _jsonl([
        {"message": {"role": "user", "content": "cześć"}},
        {"message": {"role": "assistant", "content": "hej"}},
    ], d=str(zrodlo))
    cel = Path(tempfile.mkdtemp())
    s1 = kc.eksportuj(zrodlo, cel)
    assert s1["zapisane"] == 1
    assert (cel / "sesja_sesja1.md").exists()
    # drugi przebieg: nic nowego
    s2 = kc.eksportuj(zrodlo, cel)
    assert s2["zapisane"] == 0 and s2["pominiete"] == 1


def test_eksportuj_pomija_za_krotkie():
    zrodlo = Path(tempfile.mkdtemp())
    _jsonl([{"message": {"role": "user", "content": "tylko jedna"}}], d=str(zrodlo))
    cel = Path(tempfile.mkdtemp())
    s = kc.eksportuj(zrodlo, cel, min_wiadomosci=2)
    assert s["zapisane"] == 0 and s["pominiete"] == 1


def test_szukaj():
    cel = Path(tempfile.mkdtemp())
    (cel / "sesja_abc.md").write_text("# K\n\n## 🧑 Cezar\nszukam GARCH tutaj\n", encoding="utf-8")
    tr = kc.szukaj("garch", cel)
    assert len(tr) == 1
    assert tr[0]["sesja"] == "abc"
    assert "GARCH" in tr[0]["fragment"]


def test_szukaj_brak_katalogu():
    assert kc.szukaj("x", Path("/nieistnieje/kronika")) == []


def test_statystyki():
    cel = Path(tempfile.mkdtemp())
    (cel / "sesja_a.md").write_text("abc", encoding="utf-8")
    st = kc.statystyki(cel)
    assert st["sesje"] == 1 and st["znaki"] == 3
