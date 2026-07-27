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


def test_eksportuj_reeksport_gdy_zrodlo_swiezsze():
    """
    Regresja UTRATA POTENCJAŁU (Prawo XV): aktywna sesja, która ROŚNIE, musi być
    re-destylowana — nie zamrożona na pierwszym eksporcie. Granica: mtime źródła > mtime celu.
    """
    import os
    import time
    zrodlo = Path(tempfile.mkdtemp())
    src = _jsonl([
        {"message": {"role": "user", "content": "start"}},
        {"message": {"role": "assistant", "content": "ok"}},
    ], d=str(zrodlo))
    cel = Path(tempfile.mkdtemp())
    s1 = kc.eksportuj(zrodlo, cel)
    assert s1["zapisane"] == 1
    md = cel / "sesja_sesja1.md"

    # cofnij mtime celu w przeszłość, by źródło było jednoznacznie świeższe
    stary = time.time() - 1000
    os.utime(str(md), (stary, stary))

    # dopisz dalszy dialog (sesja urosła) i ponów eksport
    src.write_text(src.read_text(encoding="utf-8") + "\n" + json.dumps(
        {"message": {"role": "user", "content": "v5 most chmura-lokal"}}), encoding="utf-8")
    s2 = kc.eksportuj(zrodlo, cel)
    assert s2["zaktualizowane"] == 1, f"Oczekiwano re-eksportu, got {s2}"
    assert "v5 most chmura-lokal" in md.read_text(encoding="utf-8")


def test_eksportuj_pomija_gdy_cel_swiezszy():
    """Granica odwrotna: gdy cel jest świeższy niż źródło → pomija (brak zbędnego zapisu)."""
    import os
    import time
    zrodlo = Path(tempfile.mkdtemp())
    _jsonl([
        {"message": {"role": "user", "content": "a"}},
        {"message": {"role": "assistant", "content": "b"}},
    ], d=str(zrodlo))
    cel = Path(tempfile.mkdtemp())
    kc.eksportuj(zrodlo, cel)
    # ustaw cel w przyszłość (świeższy niż źródło)
    md = cel / "sesja_sesja1.md"
    przyszlosc = time.time() + 1000
    os.utime(str(md), (przyszlosc, przyszlosc))
    s = kc.eksportuj(zrodlo, cel)
    assert s["pominiete"] == 1 and s["zaktualizowane"] == 0


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


def test_szukaj_po_slowach_nie_cala_fraza():
    """
    Regresja KRYTYCZNA (Prawo XV, 2026-06-28): wyszukiwarka MUSI działać po słowach.
    Bug: 'numba JIT wydajność' (cała fraza) → 0 trafień, choć linie o tym istnieją.
    """
    import tempfile
    cel = Path(tempfile.mkdtemp())
    (cel / "sesja_aaa.md").write_text(
        "## 🏛️ Claude\nRozważamy numba do przyspieszenia wskaźników GARCH\n",
        encoding="utf-8")
    # cała fraza wieloslowna — nie istnieje jako ciągły substring, ale słowa tak
    wyniki = kc.szukaj("numba wydajność wskaźniki", cel=cel)
    assert wyniki, "Wyszukiwarka po słowach nie znalazła linii (regresja bug-frazy)"
    assert wyniki[0]["trafienia"] >= 1


def test_szukaj_ranking_wiecej_slow_wyzej():
    """Linia z większą liczbą trafionych słów jest wyżej."""
    import tempfile
    cel = Path(tempfile.mkdtemp())
    (cel / "sesja_aaa.md").write_text(
        "## x\nnumba jit wydajność wskaźniki razem\nsamo wskaźniki tutaj\n",
        encoding="utf-8")
    wyniki = kc.szukaj("numba wydajność wskaźniki", cel=cel)
    assert wyniki[0]["trafienia"] >= wyniki[-1]["trafienia"]


# ── Redakcja katalogu domowego (cubic PR #134, P0) ────────────────────────────

def test_redaguje_katalog_domowy_we_wszystkich_zapisach():
    """PII i przenośność: transkrypty niosą ścieżki narzędziowe z NAZWĄ KONTA.

    Zmierzone 2026-07-27: 277 wystąpień w 30 plikach kroniki trafiło do repo. Organ
    redakcji ISTNIAŁ, ale pilnował wyłącznie kluczy API — klasa „bramka o wąskim zasięgu".

    Ta sama ścieżka żyje w transkrypcie w TRZECH postaciach naraz (proza, ucieczka JSON,
    separator POSIX). Test trzyma wszystkie trzy, bo wzorzec łapiący jedną meldowałby
    sukces przy dwóch dalej wyciekających — „milczenie udające wynik"."""
    B = chr(92)
    dom = str(Path.home())
    for wariant in (dom + B + "AppData" + B + "Local",
                    dom.replace(B, B + B) + B + B + "AppData",
                    dom.replace(B, "/") + "/AppData/Local"):
        wynik = kc._redaguj(wariant)
        assert dom.lower() not in wynik.lower(), f"wyciek katalogu domowego: {wariant!r}"
        assert dom.replace(B, "/").lower() not in wynik.lower(), f"wyciek POSIX: {wariant!r}"
        assert "~" in wynik, f"brak podstawienia w {wariant!r}"


def test_redakcja_nie_rusza_sciezek_repo():
    """Zawężenie w drugą stronę byłoby równie złe: ścieżki repo są UŻYTECZNE w kronice
    (mówią, którego pliku dotyczy rozmowa) i nie zawierają danych osobowych."""
    B = chr(92)
    sciezka = "C:" + B + "Projekty" + B + "imperial-mesh-vortex" + B + "narzedzia" + B + "x.py"
    assert kc._redaguj(sciezka) == sciezka


def test_redakcja_sekretow_dziala_dalej():
    """Rozszerzenie zasięgu nie ma prawa osłabić tego, co organ pilnował wcześniej."""
    assert "[ZREDAGOWANO]" in kc._redaguj("api_key=sk-abcdefghijklmnopqrstuvwx")


def test_wzorzec_domu_znosi_dom_bez_nazwy_konta_w_kodzie():
    """Mechanizm wyprowadza dom z `Path.home()`, NIGDY z wpisanej nazwy konta — inaczej
    utrwalilibyśmy w kodzie dokładnie tę daną, którą usuwamy. Test dowodzi, że wzorzec
    działa dla DOWOLNEGO domu, nie tylko dla maszyny, na której powstał."""
    B = chr(92)
    wz = kc._wzorzec_domu("D:" + B + "Users" + B + "ktos-inny")
    assert wz.search("D:" + B + "Users" + B + "ktos-inny" + B + "plik.txt")
    assert wz.search("D:/Users/ktos-inny/plik.txt")
    assert not wz.search("D:" + B + "Users" + B + "kto-inny")
