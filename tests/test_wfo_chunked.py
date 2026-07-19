"""Testy WFO chunkowanego/wznawialnego — checkpoint, wznawianie, równoważność wyniku."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.koloseum.walk_forward import walk_forward
from imperium.koloseum.optymalizator import PrzestrzeńParam
from narzedzia.wfo_chunked import wczytaj_checkpoint, _wynik_do_dict, _dict_do_wynik


def _bary(n=120):
    return [{"close": 100 + 10 * math.sin(i / 5) + i * 0.1, "timestamp": i} for i in range(n)]


def _fake_ev(bary, params):
    """Deterministyczny ewaluator (bez ciężkiego backtestu) — logika orchestracji."""
    mp = float(params.get("min_pewnosc", 0.5))
    base = sum(b["close"] for b in bary) / max(1, len(bary))
    zwroty = [(b["close"] / prev["close"] - 1) * mp for prev, b in zip(bary, bary[1:])]
    return base * mp, zwroty


_PRZEST = [PrzestrzeńParam("min_pewnosc", 0.4, 0.7)]


def test_checkpoint_roundtrip(tmp_path):
    zebrane = []
    rap = walk_forward(_bary(), _fake_ev, _PRZEST, 30, 10, n_iteracji=3,
                       checkpoint_cb=lambda w, z: zebrane.append(_wynik_do_dict(w, z)))
    assert rap.n_okien == 9  # (120-30)/10 - 0 ... okna 0..8
    ck = tmp_path / "c.jsonl"
    ck.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in zebrane), encoding="utf-8")
    wznow = wczytaj_checkpoint(ck)
    assert len(wznow) == rap.n_okien
    # round-trip zachowuje parametry i sharpe
    w0, z0 = wznow[0]
    assert w0.okno.idx == 0 and isinstance(w0.parametry, dict) and isinstance(z0, list)


def test_wznow_identyczny_i_bez_przeliczania(tmp_path):
    zebrane = []
    rapA = walk_forward(_bary(), _fake_ev, _PRZEST, 30, 10, n_iteracji=3,
                        checkpoint_cb=lambda w, z: zebrane.append(_wynik_do_dict(w, z)))
    ck = tmp_path / "c.jsonl"
    ck.write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in zebrane), encoding="utf-8")
    wznow = wczytaj_checkpoint(ck)

    def ev_raise(*a):
        raise AssertionError("wznowione okno NIE powinno być liczone")

    rapB = walk_forward(_bary(), ev_raise, _PRZEST, 30, 10, n_iteracji=3, wznow=wznow)
    # Identyczny raport z zapisanych cząstek — zero zmiany wyniku
    assert rapB.werdykt == rapA.werdykt
    assert rapB.wfe_srednia == rapA.wfe_srednia
    assert rapB.oos_sharpe_zagregowany == rapA.oos_sharpe_zagregowany
    assert rapB.n_okien == rapA.n_okien
    assert [w.parametry for w in rapB.okna] == [w.parametry for w in rapA.okna]
    assert [w.sharpe_oos for w in rapB.okna] == [w.sharpe_oos for w in rapA.okna]


def test_wznow_czesciowy_liczy_tylko_brakujace(tmp_path):
    # Bieg pełny z licznikiem wywołań ewaluatora
    ile_full = []
    rapFull = walk_forward(_bary(), lambda b, p: (ile_full.append(1), _fake_ev(b, p))[1],
                           _PRZEST, 30, 10, n_iteracji=3)
    n = rapFull.n_okien
    per_okno = len(ile_full) // n   # wywołań ewaluatora na okno (iteracje + IS + OOS)

    # Checkpoint tylko pierwszych 2 okien
    zebrane = []
    walk_forward(_bary(), _fake_ev, _PRZEST, 30, 10, n_iteracji=3,
                 checkpoint_cb=lambda w, z: zebrane.append(_wynik_do_dict(w, z)))
    wznow = {}
    for d in zebrane[:2]:
        w, z = _dict_do_wynik(d)
        wznow[w.okno.idx] = (w, z)

    ile_part = []
    rapPart = walk_forward(_bary(), lambda b, p: (ile_part.append(1), _fake_ev(b, p))[1],
                           _PRZEST, 30, 10, n_iteracji=3, wznow=wznow)
    # Wynik IDENTYCZNY jak pełny
    assert rapPart.wfe_srednia == rapFull.wfe_srednia
    assert rapPart.oos_sharpe_zagregowany == rapFull.oos_sharpe_zagregowany
    assert rapPart.n_okien == rapFull.n_okien
    # Policzone TYLKO brakujące (n-2) okna — 2 wznowione pominięte
    assert len(ile_part) == len(ile_full) - 2 * per_okno


def test_wznow_niedopasowane_okno_przelicza():
    """Obrona: checkpoint z idx pasującym ale INNYMI granicami okna → przelicz (nie ufaj)."""
    from imperium.koloseum.walk_forward import OknoWF, WynikOkna
    bary = _bary()
    # Podstaw fałszywy wpis dla idx=0 z granicami z KOSMOSU (inny podział)
    zly = WynikOkna(okno=OknoWF(idx=0, is_start=999, is_end=1000, oos_start=1000, oos_end=1001),
                    parametry={"min_pewnosc": 0.5}, sharpe_is=9.9, sharpe_oos=9.9,
                    wynik_is=0.0, wynik_oos=0.0, efektywnosc=2.0)
    liczone = []

    def ev_count(b, p):
        liczone.append(1)
        return _fake_ev(b, p)

    rap = walk_forward(bary, ev_count, _PRZEST, 30, 10, n_iteracji=3,
                       wznow={0: (zly, [9.9, 9.9])})
    # idx=0 policzone poprawnie (nie użyto fałszywego sharpe=9.9)
    assert rap.okna[0].sharpe_oos != 9.9
    assert len(liczone) > 0   # ewaluator wywołany dla niedopasowanego okna


def test_wczytaj_checkpoint_pomija_uszkodzone(tmp_path):
    ck = tmp_path / "c.jsonl"
    ck.write_text('{"zepsute": true}\nnie-json\n', encoding="utf-8")
    assert wczytaj_checkpoint(ck) == {}   # antykruchość: uszkodzone linie pominięte, brak wywrotki
    assert wczytaj_checkpoint(tmp_path / "brak.jsonl") == {}  # brak pliku → puste
