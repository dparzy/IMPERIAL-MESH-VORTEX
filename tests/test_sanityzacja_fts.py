#!/usr/bin/env python3
"""
Testy SANITYZACJI ZAPYTANIA FTS — jedynego źródła prawdy dla składni wyszukiwania.

DLACZEGO ISTNIEJĄ: sanityzacja żyła w Imperium w TRZECH kopiach
(`bibliotekarz._fts_bezpieczne`, `quaesitor._fts_or`) i BRAKOWAŁO jej w `mcp_server` —
czyli na ścieżce, którą Architekt czyta bibliotekę. Cena tego rozproszenia została
ZMIERZONA pierwszym biegiem QUAESITORA (30 pytań known-item, 2026-07-30):

    ścieżka bez sanityzacji (surowy MATCH):  recall@5 16,7% | opisowe  0,0%
    ścieżka z sanityzacją OR:                recall@5 66,7% | opisowe 33,3%
    OR bez słów pustych (wdrożone):          recall@5 80,0% | opisowe 60,0%

Testy poniżej pilnują trzech rzeczy, których złamanie cofnęłoby ten zysk po cichu:
  1. surowy tekst z myślnikiem NIE MOŻE wywalić MATCH (klasa `no such column: …`),
  2. słowa puste MUSZĄ być odsiewane, ale NIGDY do pustego zapytania,
  3. `skladnia="surowa"` musi zostawiać zapytanie nietknięte — inaczej wołający
     budujący świadomie składnię FTS (frazy, NEAR) dostałby ją zniszczoną.
"""

from __future__ import annotations

import sys
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[1]
for p in (KORZEN, KORZEN / "narzedzia" / "rag"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from szukaj import sanityzuj_fts  # noqa: E402


# ── Składnia OR ───────────────────────────────────────────────────────────────

def test_or_laczy_slowa_tresciwe():
    assert sanityzuj_fts("VPIN flow toxicity", "or") == "VPIN OR flow OR toxicity"


def test_or_usuwa_myslnik_ktory_wywalal_match():
    """Realny bug: 'trend-following' dawał OperationalError 'no such column: following'."""
    wynik = sanityzuj_fts("momentum trend-following breakout", "or")
    assert "-" not in wynik
    assert wynik == "momentum OR trend OR following OR breakout"


def test_or_odsiewa_slowa_puste():
    """Sedno pomiaru: 'how/to/the/me' szukają w KAŻDYM fragmencie i rozcieńczają ranking."""
    wynik = sanityzuj_fts("how to tell if the people know something", "or")
    for pusty in ("how", "to", "if", "the"):
        assert f" {pusty} " not in f" {wynik} ", f"słowo puste '{pusty}' przeżyło"
    assert "tell" in wynik and "people" in wynik


def test_terminy_domenowe_NIE_sa_slowami_pustymi():
    """Kontrola negatywna: gdyby zbiór puchł, zaczęlibyśmy gubić treść."""
    wynik = sanityzuj_fts("volume risk trend regime volatility", "or")
    for termin in ("volume", "risk", "trend", "regime", "volatility"):
        assert termin in wynik


def test_pytanie_z_samych_slow_pustych_nie_daje_pustki():
    """Lepiej wyszukać dosłownie niż nie wyszukać wcale (Prawo XV: cisza to strata)."""
    wynik = sanityzuj_fts("how to do it", "or")
    assert wynik.strip() != ""
    assert "OR" in wynik


def test_polskie_slowa_puste_tez_odsiane():
    wynik = sanityzuj_fts("jak rozpoznac zmiane rezimu na rynku", "or")
    assert "jak" not in wynik.split(" OR ")
    assert "rozpoznac" in wynik and "rezimu" in wynik


def test_polskie_znaki_diakrytyczne_przezywaja():
    assert "płynność" in sanityzuj_fts("płynność rynku", "or")


# ── Składnia AND (do porównań/ramion A/B) ─────────────────────────────────────

def test_and_laczy_spacja_bez_operatora():
    wynik = sanityzuj_fts("VPIN flow toxicity", "and")
    assert "OR" not in wynik
    assert wynik == "VPIN flow toxicity"


def test_and_tez_jest_sanityzowane():
    """AND bez sanityzacji wywalał MATCH — tryb porównawczy nie może się sypać z tego powodu."""
    assert "-" not in sanityzuj_fts("trend-following", "and")


# ── Składnia SUROWA — świadome budowanie zapytania FTS ────────────────────────

def test_surowa_nie_tyka_zapytania():
    """Wołający budujący frazę/NEAR/prefiks musi dostać swoje zapytanie nietknięte."""
    q = '"order flow" NEAR/5 toxicity'
    assert sanityzuj_fts(q, "surowa") == q


def test_surowa_zachowuje_nawet_niebezpieczna_skladnie():
    q = "trend-following"
    assert sanityzuj_fts(q, "surowa") == q


# ── Przypadki brzegowe ────────────────────────────────────────────────────────

def test_puste_wejscie_nie_wybucha():
    assert sanityzuj_fts("", "or") == ""
    assert sanityzuj_fts(None, "or") is None


def test_same_znaki_interpunkcyjne_wracaja_bez_zmian():
    assert sanityzuj_fts("!!! ???", "or") == "!!! ???"


def test_domyslna_skladnia_to_OR():
    """Domyślna wartość jest wyborem ZMIERZONYM (80,0% vs 16,7% recall@5) — nie wygodą."""
    assert sanityzuj_fts("VPIN flow") == "VPIN OR flow"


# ── Jedno źródło prawdy: kopie MUSZĄ delegować ────────────────────────────────

def test_bibliotekarz_deleguje_do_jednego_zrodla():
    from narzedzia.bibliotekarz import _fts_bezpieczne
    q = "momentum trend-following the breakout"
    assert _fts_bezpieczne(q) == sanityzuj_fts(q, "or")


def test_quaesitor_deleguje_do_jednego_zrodla():
    import quaesitor
    q = "how to detect adverse selection"
    assert quaesitor._fts_or(q) == sanityzuj_fts(q, "or")


def test_topk_cli_odrzuca_wartosci_poza_zakresem():
    """Klasa z Księgi Wad: argument sterujący kosztem bez walidacji zakresu.

    Gołe `type=int` przyjmowało 0 (zapytanie zwracające nic BEZ wyjaśnienia) oraz
    wartości absurdalne — a przy filtrze katalogowym `szukaj` nadpobiera ×20, więc
    duże topk zamieniało zapytanie w pełny skan korpusu.
    """
    import argparse

    from szukaj import _topk_cli
    for zly in ("0", "-1", "101", "abc"):
        try:
            _topk_cli(zly)
        except argparse.ArgumentTypeError:
            continue
        raise AssertionError(f"topk={zly!r} powinien zostać odrzucony")


def test_topk_cli_przyjmuje_granice_zakresu():
    from szukaj import _topk_cli
    assert _topk_cli("1") == 1
    assert _topk_cli("100") == 100


def test_sciezka_MCP_dostaje_sanityzacje_bez_wlasnego_kodu(monkeypatch):
    """REGRESJA dla dziury, która kosztowała 63 pp recallu.

    `mcp_server` nie sanityzował nic — i nie powinien, bo robi to `szukaj`. Ten test
    pilnuje, że wołanie z MCP dociera do FTS ZE ZŁOŻONĄ składnią OR, mimo że w samym
    `mcp_server` nie ma ani jednej linii o składni. Gdyby ktoś kiedyś dodał domyślne
    `skladnia="surowa"` w łańcuchu, ten test upadnie zamiast po cichu wrócić do 16,7%.
    """
    import mcp_server
    import szukaj as szukaj_mod
    widziane = {}

    def fake_fts(conn, zapytanie, topk, korpus=None):
        widziane["q"] = zapytanie
        return []

    monkeypatch.setattr(szukaj_mod, "_fts_szukaj", fake_fts)
    monkeypatch.setattr(szukaj_mod, "_wektor_szukaj",
                        lambda conn, zapytanie, topk, model, korpus=None: [])
    if not szukaj_mod.DEFAULT_BAZA.exists():
        import pytest
        pytest.skip("brak bazy RAG na tej maszynie — pomiar ścieżki wymaga indeksu")

    mcp_server._szukaj("how to detect trend-following breakout", topk=5, tryb="fts")
    assert "OR" in widziane["q"], "ścieżka MCP znów idzie surowym MATCH-em"
    assert "-" not in widziane["q"], "myślnik przeżył — wróciła klasa 'no such column'"
    assert "how" not in widziane["q"].split(" OR "), "słowa puste znów rozcieńczają ranking"
