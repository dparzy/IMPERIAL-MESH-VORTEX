"""Testy SCRIBA CODEX (narzedzia/scriba_codex.py) — appender ledgera CODEX_PROBATIONUM.

Reguła Test-Granic (Prawo XXI): appender decyduje na IDENTYCZNOŚCI rekordu (idempotencja).
Testujemy granice: pusty plik, identyczny rekord (skip), inny wynik (append), inny dzień
(append), schemat pól zgodny z tym, co czyta codex_probationum (bez aliasów).
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import tempfile
from pathlib import Path

from narzedzia.scriba_codex import (zapisz_ab, zapisz_ic, zapisz_sugestia,
                                    zamknij_sugestia,
                                    POLA_AB, POLA_IC, POLA_SUGESTIA)


def _tmp():
    d = tempfile.mkdtemp()
    return Path(d) / "rejestr_testow.jsonl"


def _linie(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_sugestia_dopisuje_i_dedupuje_po_elemencie():
    p = _tmp()
    ok = zapisz_sugestia(element="Sigillum Datae", dzial="reprodukowalnosc",
                         uzasadnienie="hash SHA-256 barow przy wpisie", zgodnosc_imperium="TAK",
                         zrodlo="zwiadowca", sciezka=p)
    assert ok is True
    r = _linie(p)[0]
    assert r["typ"] == "SUGESTIA" and r["status"] == "KANDYDAT"
    assert set(r.keys()) == set(POLA_SUGESTIA)   # schemat 1:1 z codex (Prawo XXI)
    # Ta sama sugestia (element) innego dnia → NIE dubluje (unikat, nie szereg czasowy)
    ok2 = zapisz_sugestia(element="Sigillum Datae", dzial="reprodukowalnosc",
                          uzasadnienie="inny opis", zgodnosc_imperium="TAK",
                          zrodlo="zwiadowca", data="2099-01-01", sciezka=p)
    assert ok2 is False
    assert len(_linie(p)) == 1
    # Inny element → dopisuje
    assert zapisz_sugestia(element="Custos Arcanorum", dzial="bezpieczenstwo",
                           uzasadnienie="skan sekretow", zgodnosc_imperium="TAK",
                           zrodlo="zwiadowca", sciezka=p) is True
    assert len(_linie(p)) == 2


def test_ab_dopisuje_i_liczy_delta():
    p = _tmp()
    ok = zapisz_ab(sygnal="USD/DXY", neuron="K-04", interwal="4H", okno_barow=800,
                   roi_b=4.33, roi_a=4.53, maxdd_delta=0.1, werdykt="POMAGA",
                   zrodlo="ab_usd.py", sciezka=p)
    assert ok is True
    rek = _linie(p)
    assert len(rek) == 1
    r = rek[0]
    assert r["typ"] == "AB"
    assert r["delta_pp"] == 0.2               # roi_a - roi_b, zaokrąglone
    assert set(r.keys()) == set(POLA_AB)       # schemat 1:1 z codex (bez aliasów, Prawo XXI)


def test_ab_idempotentny_ten_sam_rekord():
    p = _tmp()
    kw = dict(sygnal="DVOL", neuron="PSY-05", interwal="1d", okno_barow=600,
              roi_b=1.0, roi_a=2.0, maxdd_delta=0.0, werdykt="POMAGA",
              zrodlo="ab_dvol.py", data="2026-07-19", sciezka=p)
    assert zapisz_ab(**kw) is True
    assert zapisz_ab(**kw) is False            # identyczny bieg tego samego dnia → skip
    assert len(_linie(p)) == 1


def test_ab_inny_wynik_dopisuje():
    p = _tmp()
    base = dict(sygnal="DVOL", neuron="PSY-05", interwal="1d", okno_barow=600,
                maxdd_delta=0.0, werdykt="POMAGA", zrodlo="ab_dvol.py",
                data="2026-07-19", sciezka=p)
    assert zapisz_ab(roi_b=1.0, roi_a=2.0, **base) is True
    assert zapisz_ab(roi_b=1.0, roi_a=3.0, **base) is True   # inny wynik → nowa linia
    assert len(_linie(p)) == 2


def test_ab_inny_dzien_dopisuje():
    p = _tmp()
    base = dict(sygnal="STABLECOIN", neuron="K-03", interwal="1d", okno_barow=600,
                roi_b=1.0, roi_a=2.0, maxdd_delta=0.0, werdykt="POMAGA",
                zrodlo="ab_stablecoin.py", sciezka=p)
    assert zapisz_ab(data="2026-07-18", **base) is True
    assert zapisz_ab(data="2026-07-19", **base) is True      # inny dzień = historia
    assert len(_linie(p)) == 2


def test_ic_schemat_i_zaokraglenie():
    p = _tmp()
    ok = zapisz_ic(sygnal="FUNDING", neuron="C-01", horyzont="6b", ic=-0.123456,
                   tryb="nienakladajace", prog=0.03, werdykt="SKILL",
                   kierunek="kontrariański", zrodlo="pomiar_funding_ic.py", sciezka=p)
    assert ok is True
    r = _linie(p)[0]
    assert r["typ"] == "IC"
    assert r["ic"] == -0.1235                  # zaokrąglone do 4 miejsc
    assert set(r.keys()) == set(POLA_IC)       # schemat 1:1 z codex


def test_ic_idempotentny():
    p = _tmp()
    kw = dict(sygnal="USD/DXY", neuron="K-04", horyzont="30d", ic=-0.11,
              tryb="nienakladajace", prog=0.03, werdykt="SKILL", kierunek="bearish",
              zrodlo="pomiar_usd_ic.py", data="2026-07-19", sciezka=p)
    assert zapisz_ic(**kw) is True
    assert zapisz_ic(**kw) is False
    assert len(_linie(p)) == 1


def test_pusty_plik_tworzy_sie():
    p = _tmp()
    assert not p.exists()
    assert zapisz_ab(sygnal="X", neuron="Z-01", interwal="1d", okno_barow=1,
                     roi_b=0.0, roi_a=0.0, maxdd_delta=0.0, werdykt="NEUTRALNE",
                     zrodlo="t", sciezka=p) is True
    assert p.exists()
    assert len(_linie(p)) == 1


def test_zamknij_sugestia_dopisuje_rekord_zamkniecia():
    """Zamknięcie to NOWA linia z tym samym elementem (Prawo I: historii nie kasujemy)."""
    p = _tmp()
    zapisz_sugestia(element="E1", dzial="Wydajnosc", uzasadnienie="u",
                    zgodnosc_imperium="tak", zrodlo="t", data="2026-07-19", sciezka=p)
    assert zamknij_sugestia(element="E1", powod="teza obalona pomiarem",
                            zrodlo="t", data="2026-07-19", sciezka=p) is True
    linie = _linie(p)
    assert len(linie) == 2                      # oryginał ZOSTAJE
    assert linie[0]["status"] == "KANDYDAT"
    assert linie[1]["status"] == "ZAMKNIETE"
    assert linie[1]["element"] == "E1"
    assert linie[1]["dzial"] == "Wydajnosc"     # kontekst przepisany z oryginału


def test_zamknij_sugestia_nieistniejaca_rzuca():
    p = _tmp()
    try:
        zamknij_sugestia(element="NIE MA", powod="x", zrodlo="t", sciezka=p)
        assert False, "powinien rzucić ValueError dla nieistniejącej sugestii"
    except ValueError:
        pass


def test_zamknij_sugestia_idempotentne():
    p = _tmp()
    zapisz_sugestia(element="E2", dzial="D", uzasadnienie="u",
                    zgodnosc_imperium="tak", zrodlo="t", data="2026-07-19", sciezka=p)
    kw = dict(element="E2", powod="powod", zrodlo="t", data="2026-07-19", sciezka=p)
    assert zamknij_sugestia(**kw) is True
    assert zamknij_sugestia(**kw) is False      # identyczny rekord nie dubluje
    assert len(_linie(p)) == 2


# ── LIMEN FENESTRAE — ranga werdyktu wg pokrycia ery (NOTA N-4f7032a6, 2026-07-20) ──

def test_limen_prog_dokladny():
    """Granica DOKŁADNA: pokrycie == próg → ROZSTRZYGAJACY (>=), tuż pod → WSTEPNY."""
    from narzedzia.scriba_codex import ocen_pokrycie, PROG_REPREZENTATYWNOSCI
    assert PROG_REPREZENTATYWNOSCI == 0.5
    assert ocen_pokrycie(50, 100)["ranga"] == "ROZSTRZYGAJACY"
    assert ocen_pokrycie(49, 100)["ranga"] == "WSTEPNY"


def test_limen_realny_przypadek_ktory_zmylil():
    """REGRESJA: 2000/19471 barów = 10% ery dało werdykt POMAGA, pełna era NEUTRALNE.
    Taki bieg MUSI być oznaczony jako WSTĘPNY, żeby nie zamknął tematu."""
    from narzedzia.scriba_codex import ocen_pokrycie
    w = ocen_pokrycie(2000, 19471)
    assert w["ranga"] == "WSTEPNY"
    assert w["pokrycie"] == 0.103
    assert "10%" in w["nota"]


def test_limen_brak_wiedzy_nie_udaje_pewnosci():
    """Prawo I: nieznana era → NIEZNANE, nie udajemy że werdykt jest pełnowartościowy."""
    from narzedzia.scriba_codex import ocen_pokrycie
    for brak in (None, 0, -5):
        w = ocen_pokrycie(100, brak)
        assert w["ranga"] == "NIEZNANE" and w["pokrycie"] is None


def test_limen_pokrycie_nie_przekracza_stu_procent():
    """Granica: okno większe niż era (np. --bary > dostępne) → pokrycie przycięte do 1.0."""
    from narzedzia.scriba_codex import ocen_pokrycie
    assert ocen_pokrycie(999, 100)["pokrycie"] == 1.0


def test_zapisz_ab_niesie_range_w_rekordzie():
    """Ranga jedzie W REKORDZIE ledgera — nie w pamięci operatora (to był rdzeń wady)."""
    p = _tmp()
    zapisz_ab(sygnal="S", neuron="N", interwal="1H", okno_barow=2000, roi_b=1.0, roi_a=2.0,
              maxdd_delta=0.0, werdykt="POMAGA", zrodlo="t", data="2026-07-20",
              dostepne_barow=19471, sciezka=p)
    rek = _linie(p)[0]
    assert rek["ranga"] == "WSTEPNY"
    assert rek["pokrycie_ery"] == 0.103
    assert "WSTĘPNY" in rek["uwaga"], "ostrzezenie musi byc czytelne w samym rekordzie"


def test_zapisz_ab_bez_ery_nie_wywala_sie():
    """Kompatybilność wsteczna: wywołanie bez `dostepne_barow` (stare narzędzia) działa."""
    p = _tmp()
    zapisz_ab(sygnal="S", neuron="N", interwal="1D", okno_barow=400, roi_b=0.0, roi_a=0.0,
              maxdd_delta=0.0, werdykt="NEUTRALNE", zrodlo="t", data="2026-07-20", sciezka=p)
    assert _linie(p)[0]["ranga"] == "NIEZNANE"
