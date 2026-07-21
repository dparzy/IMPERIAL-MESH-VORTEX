"""Testy Bibliotekarza-Zwiadowcy (narzedzia/bibliotekarz.py) — dyscyplina i cząstki.

Nie dotykamy DeepSeek API (koszt) — testujemy pure logic + ścieżkę dry-run (glos=None)."""
import sys
import os
import json
from collections import namedtuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "narzedzia", "rag"))

import narzedzia.bibliotekarz as bib
from narzedzia.bibliotekarz import (
    _fragmenty_tekst, scout_temat, _SYSTEM, _topk_arg, _tematy_ukonczone,
    _fts_bezpieczne, rozwin_zapytanie, krytyka_kandydatow,
)

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


def test_topk_arg_odrzuca_poza_zakresem():
    # Cubic P2: --topk poza [1, _TOPK_MAX] → błąd zanim ruszy RAG/płatne API (granice).
    import argparse
    import pytest
    assert _topk_arg("6") == 6 and _topk_arg("1") == 1 and _topk_arg("20") == 20
    for zly in ("0", "-3", "21", "9999"):
        with pytest.raises(argparse.ArgumentTypeError):
            _topk_arg(zly)


def test_scout_domyslnie_korpus_biblioteka(monkeypatch):
    # U1 (anty-echo, Prawo XVI): scout domyślnie czyta TYLKO korpus 'biblioteka' (książki),
    # nie 'dane'/'docs'. Sprawdzamy, że korpus jest forwardowany do RAG i domyślnie = biblioteka.
    import szukaj as szukaj_mod
    zebrane = {}

    def fake_szukaj(temat, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        zebrane["korpus"] = korpus
        return []

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)
    scout_temat(None, "mean reversion", topk=3, tryb="fts")
    assert zebrane["korpus"] == "biblioteka"          # domyślnie tylko książki
    scout_temat(None, "mean reversion", topk=3, tryb="fts", korpus=None)
    assert zebrane["korpus"] is None                  # override: None = bez filtra (dawne zachowanie)


def test_tematy_ukonczone_pomija_dry(tmp_path, monkeypatch):
    # Cubic P2: dedup liczy realny zwiad (ok/pusto, stare bez statusu), ale NIE dry-run.
    kol = tmp_path / "kolejka.jsonl"
    kol.write_text(
        json.dumps({"temat": "realny", "status": "ok"}) + "\n"
        + json.dumps({"temat": "podglad", "status": "dry"}) + "\n"
        + json.dumps({"temat": "stary_bez_statusu"}) + "\n",
        encoding="utf-8")
    monkeypatch.setattr(bib, "KOLEJKA", kol)
    done = _tematy_ukonczone()
    assert "realny" in done and "stary_bez_statusu" in done
    assert "podglad" not in done          # dry-run nie blokuje realnego zwiadu


class _FakeGlos:
    """Atrapa GlosImperium — nie dotyka API. Zwraca ustaloną odpowiedź lub rzuca błąd."""
    def __init__(self, odp=None, blad=False):
        self._odp, self._blad = odp, blad

    def zapytaj(self, system, tresc, temperatura=0.7):
        if self._blad:
            raise RuntimeError("API down")
        return self._odp


def test_fts_bezpieczne_sanityzuje_i_nie_wywala():
    # U2: myślniki/słowa-klucze FTS5 nie mogą wywalić MATCH — sanityzacja do słów złączonych OR.
    assert _fts_bezpieczne("momentum trend-following breakout") == "momentum OR trend OR following OR breakout"
    assert _fts_bezpieczne("mean reversion") == "mean OR reversion"
    assert _fts_bezpieczne("!!!") == "!!!"      # brak słów → oryginał (nie tworzymy pustego MATCH)


def test_rozwin_zapytanie_sanityzuje_i_fallback():
    # U2: rozszerzenie zwraca same słowa; pusta/błędna odpowiedź → fallback na temat (Prawo XV).
    g = _FakeGlos(odp="mean-reversion, bands! overextension zscore")
    assert rozwin_zapytanie(g, "mean reversion") == "mean reversion bands overextension zscore"
    assert rozwin_zapytanie(_FakeGlos(odp="   "), "temat X") == "temat X"    # pusto → temat
    assert rozwin_zapytanie(_FakeGlos(blad=True), "temat Y") == "temat Y"    # błąd API → temat


def test_scout_rozwin_uzywa_rozszerzonego_zapytania(monkeypatch):
    # U2: gdy rozwin=True i jest glos — RAG idzie na ROZSZERZONYM (sanityzowanym) zapytaniu, nie surowym.
    import szukaj as szukaj_mod
    zebrane = {}

    def fake_szukaj(q, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        zebrane["q"] = q
        return []

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)
    cz = scout_temat(_FakeGlos(odp="momentum breakout volatility"), "momentum", topk=3, rozwin=True)
    assert cz["zapytanie"] == "momentum breakout volatility"      # rozszerzone zachowane w rekordzie
    assert zebrane["q"] == "momentum OR breakout OR volatility"   # do FTS poszło sanityzowane OR


def test_krytyka_kandydatow_fallback_na_blad():
    # U3: błąd API krytyki nie może przekreślić cząstki — zwraca komunikat, nie wyjątek (Prawo XV).
    out = krytyka_kandydatow(_FakeGlos(blad=True), "jakiś kandydat", [])
    assert "niedostępna" in out


def test_scout_krytyka_dodaje_dowody_przeciw(monkeypatch):
    # U3: krytyka=True → drugie retrieval (dowody PRZECIW) + pole 'krytyka' w cząstce.
    from collections import namedtuple
    import szukaj as szukaj_mod
    W = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")
    zapytania = []

    def fake_szukaj(q, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        zapytania.append(q)
        return [W("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")]

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)
    cz = scout_temat(_FakeGlos(odp="ocena hipotez"), "momentum", topk=3, krytyka=True)
    assert cz["status"] == "ok"
    assert cz.get("krytyka") == "ocena hipotez"          # pole krytyki obecne
    assert len(zapytania) == 2                           # główne + kontra (osobne retrieval)
    assert "risk" in zapytania[1] and "failure" in zapytania[1]   # kontra-sufiks w drugim zapytaniu


def test_kontekst_systemu_ma_luki_i_antydup():
    # U4: blok świadomości zawiera instrukcję anty-duplikatów (Prawo XVI) i sekcję luk —
    # albo pusty string, gdy rejestr niedostępny (graceful, Prawo XV). Bez brittle na konkretny klucz.
    from narzedzia.bibliotekarz import _kontekst_systemu
    blok = _kontekst_systemu()
    assert blok == "" or ("Prawo XVI" in blok and "LUKI" in blok and "ISTNIEJĄCE" in blok)


def test_scout_swiadomosc_wstrzykuje_kontekst(monkeypatch):
    # U4: swiadomosc=True dokłada blok świadomości do treści dla DeepSeeka; OFF → nie dokłada.
    from collections import namedtuple
    import szukaj as szukaj_mod
    W = namedtuple("W", "zrodlo tytul nr_chunk tekst score korpus")
    monkeypatch.setattr(szukaj_mod, "szukaj",
                        lambda *a, **k: [W("BIB-001", "Chan", 1, "tekst", -1.0, "biblioteka")])
    monkeypatch.setattr(bib, "_kontekst_systemu", lambda: "\nSENTINEL_KTX")
    zebrane = {}

    class G:
        def zapytaj(self, system, tresc, temperatura=0.7):
            zebrane["tresc"] = tresc
            return "kand"

    scout_temat(G(), "momentum", topk=3, swiadomosc=True)
    assert "SENTINEL_KTX" in zebrane["tresc"]              # ON → kontekst dołączony
    scout_temat(G(), "momentum", topk=3, swiadomosc=False)
    assert "SENTINEL_KTX" not in zebrane["tresc"]          # OFF → bez kontekstu


# ── PROBATOR wpięty w plon (warstwa 1 anty-halucynacyjna, 0 tokenów) ────────────

def _fake_szukaj_bib006(monkeypatch, zrodlo="BIB-006_Carson_Scalping.epub", chunk=8):
    """Podstawia RAG zwracający JEDEN znany fragment — wiemy dokładnie, co model 'dostał'."""
    import szukaj as szukaj_mod

    def fake_szukaj(q, topk=5, tryb="hybrid", cichy=False, korpus=None, **kw):
        return [_FakeWynik(zrodlo, "Carson — Scalping", chunk, "tekst", -1.0, "biblioteka")]

    monkeypatch.setattr(szukaj_mod, "szukaj", fake_szukaj)


def test_probator_czysty_gdy_model_cytuje_podane_zrodlo(monkeypatch):
    """Cytat zgodny z tym, co podano → werdykt CZYSTY, cząstka bez alarmu."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat 1 wg BIB-006 chunk 8."), "momentum", topk=3)
    assert cz["probator"]["status"] == "CZYSTY" and cz["probator"]["czysty"] is True


def test_probator_lapie_zrodlo_ktorego_nie_podano(monkeypatch):
    """RDZEŃ: model powołuje się na książkę, której NIE dostał → halucynacja citation.
    Cząstka niesie ostrzeżenie do kolejki, którą czyta sędzia-Opus."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat wg BIB-047 Kaufman."), "momentum", topk=3)
    assert cz["probator"]["status"] == "PODEJRZANY"
    assert cz["probator"]["obce_zrodla"] == ["BIB-047"]


def test_probator_domyslnie_wlaczony_i_wylaczalny(monkeypatch):
    """Domyślnie ON (deterministyczny, bez kosztu); da się wyłączyć bez zmiany reszty plonu."""
    _fake_szukaj_bib006(monkeypatch)
    zap = scout_temat(_FakeGlos(odp="Kandydat wg BIB-006."), "momentum", topk=3)
    bez = scout_temat(_FakeGlos(odp="Kandydat wg BIB-006."), "momentum", topk=3, probator=False)
    assert "probator" in zap and "probator" not in bez
    assert zap["kandydaci"] == bez["kandydaci"]         # plon identyczny — organ tylko OPISUJE


def test_probator_nie_zmienia_kandydatow_ani_statusu(monkeypatch):
    """ZASADA WPIĘCIA: organ jest monotonicznie ostrożny — dokłada werdykt, nic nie odrzuca."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat wg BIB-999 (wymyślony)."), "momentum", topk=3)
    assert cz["status"] == "ok"                         # cząstka NADAL trafia do kolejki
    assert cz["kandydaci"] == "Kandydat wg BIB-999 (wymyślony)."


def test_probator_bada_takze_krytyke(monkeypatch):
    """Krytyka to też plon modelu — bada się ją wobec WŁASNYCH fragmentów kontra."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Ocena wg BIB-777."), "momentum", topk=3, krytyka=True)
    assert cz["probator_krytyka"]["obce_zrodla"] == ["BIB-777"]


def test_czastka_z_probatorem_jest_json_serializowalna(monkeypatch):
    """Cząstka idzie do JSONL — werdykt nie może wnieść obiektu nieserializowalnego."""
    _fake_szukaj_bib006(monkeypatch)
    cz = scout_temat(_FakeGlos(odp="Kandydat wg BIB-006 chunk 8."), "momentum", topk=3)
    assert json.loads(json.dumps(cz, ensure_ascii=False))["probator"]["status"] == "CZYSTY"


def test_dry_run_nie_dostaje_werdyktu(monkeypatch):
    """Granica: bez odpowiedzi modelu nie ma czego badać — brak pola, nie fałszywy alarm."""
    _fake_szukaj_bib006(monkeypatch)
    assert "probator" not in scout_temat(None, "momentum", topk=3)
