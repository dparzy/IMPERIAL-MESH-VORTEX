"""Testy generatora CODEX_PROBATIONUM (rejestr testów w Excelu).

Rdzeń `zbierz_arkusze()` testowany BEZ openpyxl; zapis .xlsx tylko gdy biblioteka
dostępna (`pytest.importorskip`). Reguła Test-Granic: pusty ledger, uszkodzona linia,
parser korelacji, zgodność liczby neuronów z żywym rejestrem.
"""
import logging
import os
import sys

logging.disable(logging.CRITICAL)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest  # noqa: E402
from narzedzia import codex_probationum as cp  # noqa: E402


def test_zbierz_arkusze_ma_wszystkie_arkusze():
    """12 arkuszy o oczekiwanych nazwach, każdy z nagłówkiem."""
    ark = cp.zbierz_arkusze()
    oczekiwane = {"README", "Neurony", "Zwiadowcy", "Strategie", "Neurony x Strategie",
                  "Adaptery", "Waluty x Interwaly", "Interwaly -> Styl",
                  "Wyniki A-B", "Wyniki IC", "Korelacje", "Backlog", "Sugestie",
                  "Momenty modelu"}
    assert oczekiwane <= set(ark), f"brak arkuszy: {oczekiwane - set(ark)}"
    for nazwa, wiersze in ark.items():
        assert len(wiersze) >= 1, f"arkusz {nazwa} bez nagłówka"


def test_neurony_zgodne_z_zywym_rejestrem():
    """Liczba wierszy neuronów = liczba neuronów w kodzie (Prawo XXI — nie z pamięci)."""
    from imperium.legiony.rejestr import wszystkie_neurony
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    ark = cp.zbierz_arkusze()
    assert len(ark["Neurony"]) - 1 == len(wszystkie_neurony())     # -1 = nagłówek
    assert len(ark["Strategie"]) - 1 == len(wszystkie_strategie())


def test_legenda_kategorii_kompletna():
    """KAT_NAZWA pokrywa KAŻDĄ kategorię żywego kodu (w tym C i D — fix ZPO)."""
    from imperium.legiony.rejestr import wszystkie_neurony
    kat_kodu = {n.KATEGORIA for n in wszystkie_neurony()}
    brak = kat_kodu - set(cp.KAT_NAZWA)
    assert not brak, f"legenda nie pokrywa kategorii kodu: {brak}"
    assert "C" in cp.KAT_NAZWA and "D" in cp.KAT_NAZWA


def test_wczytaj_ledger_pusty(tmp_path):
    """Granica: brak pliku → []; pusty plik → []."""
    assert cp._wczytaj_ledger(tmp_path / "nie_ma.jsonl") == []
    pusty = tmp_path / "pusty.jsonl"
    pusty.write_text("", encoding="utf-8")
    assert cp._wczytaj_ledger(pusty) == []


def test_wczytaj_ledger_pomija_uszkodzona_linie(tmp_path):
    """Granica: uszkodzona linia JSON nie zabija odczytu (Prawo I)."""
    p = tmp_path / "l.jsonl"
    p.write_text('{"typ":"AB","neuron":"X-01"}\n{ uszkodzone\n\n{"typ":"IC","neuron":"Y"}\n',
                 encoding="utf-8")
    rek = cp._wczytaj_ledger(p)
    assert len(rek) == 2 and rek[0]["neuron"] == "X-01"


def test_parsuj_korelacje_regex():
    """Parser wyłuskuje pary 'A ~ B | ... | +0.972' z tabeli markdown."""
    # regex działa na realnym MATRYCA; tu sprawdzamy sam wzorzec na syntetyce
    import re
    wzor = re.compile(r"\|\s*\*{0,2}([A-Z][\w-]+)\s*~\s*([A-Z][\w-]+)\*{0,2}\s*\|"
                      r"[^|]*\|\s*\*{0,2}([+-]?\d\.\d+)\*{0,2}\s*\|")
    m = wzor.search("| **V-13 ~ VI-13** | Yang-Zhang ~ ATR | **+1.000** | identyczny |")
    assert m and m.group(1) == "V-13" and m.group(2) == "VI-13" and float(m.group(3)) == 1.0


def test_ledger_bez_delta_pp_nie_wywraca(monkeypatch):
    """Granica (recenzja 2026-07-18): ręcznie dopisany rekord A/B bez delta_pp
    (albo null) NIE może wywrócić generatora przez format '+' na nie-liczbie."""
    kaleki = [{"typ": "AB", "neuron": "X-01", "interwal": "4H"},          # brak delta_pp
              {"typ": "AB", "neuron": "X-01", "interwal": "1H", "delta_pp": None}]
    monkeypatch.setattr(cp, "_wczytaj_ledger", lambda *a, **k: kaleki)
    ark = cp.zbierz_arkusze()                    # nie może rzucić ValueError/TypeError
    assert "Neurony" in ark


def test_macierz_rol_ma_kolumny_strategii():
    """Macierz Neurony×Strategie: nagłówek = KLUCZ + wszystkie strategie."""
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    ark = cp.zbierz_arkusze()
    naglowek = ark["Neurony x Strategie"][0]
    assert len(naglowek) == 1 + len(wszystkie_strategie())


def test_arkusz_momenty_modelu():
    """Arkusz „Momenty modelu" (druga oś ZASADY OSZCZĘDNOŚCI TOKENÓW): nagłówek 5-kolumnowy
    + wszystkie momenty ze stałej + kolumny moment/tier/dźwignia."""
    ark = cp.zbierz_arkusze()
    mm = ark["Momenty modelu"]
    assert mm[0] == ["Moment sesji", "Zużycie", "Rekomendowany tier", "Dźwignia", "Uwaga"]
    # każdy moment ze stałej jest wierszem (nagłówek + N momentów + stopka)
    momenty_w_arkuszu = {w[0] for w in mm[1:] if w[0]}
    for m in cp.MOMENTY_MODELU:
        assert m[0] in momenty_w_arkuszu
    assert any("Start sesji" in w[0] for w in mm[1:])


def test_podsumowanie_ledger_pusty(tmp_path):
    """Granica: brak ledgera → 0 rekordów, ostatni wynik '—', bez wyjątku (C1)."""
    s = cp.podsumowanie_ledger(tmp_path / "nie_ma.jsonl")
    assert "0 rekordów" in s and "A/B 0" in s and "IC 0" in s and "—" in s


def test_podsumowanie_ledger_liczy_typy(tmp_path):
    """Podsumowanie zlicza A/B, IC, Sugestie i pokazuje najświeższą datę."""
    p = tmp_path / "l.jsonl"
    p.write_text(
        '{"typ":"AB","neuron":"X","data":"2026-07-10"}\n'
        '{"typ":"AB","neuron":"Y","data":"2026-07-18"}\n'
        '{"typ":"IC","neuron":"Z","data":"2026-07-12"}\n'
        '{"typ":"SUGESTIA","element":"nowy arkusz","data":"2026-07-15"}\n',
        encoding="utf-8")
    s = cp.podsumowanie_ledger(p)
    assert "4 rekordów" in s and "A/B 2" in s and "IC 1" in s and "Sugestie 1" in s
    assert "2026-07-18" in s          # max daty, nie ostatnia linia


def test_podsumowanie_ledger_bez_daty(tmp_path):
    """Granica: rekordy bez pola 'data' → nie wywalają max(); ostatni wynik '—'."""
    p = tmp_path / "l.jsonl"
    p.write_text('{"typ":"AB","neuron":"X"}\n', encoding="utf-8")
    s = cp.podsumowanie_ledger(p)
    assert "1 rekordów" in s and s.rstrip().endswith("—")


def _sug(element, status, data, uzasadnienie=""):
    return {"typ": "SUGESTIA", "element": element, "dzial": "d", "status": status,
            "data": data, "uzasadnienie": uzasadnienie, "zrodlo": "test"}


def test_sugestie_biezace_zwijaja_domkniecie():
    """Domknięcie (nowa linia o tym samym `element`) zastępuje KANDYDATA, nie stoi obok.

    Klasa wady zmierzona 2026-07-21: arkusz wypisywał obie linie płasko, więc zrobione
    zadanie dalej wyglądało na otwarte."""
    ledger = [_sug("A", "KANDYDAT", "2026-07-01"),
              _sug("A", "ZAMKNIETE", "2026-07-21", "wdrożone"),
              _sug("B", "KANDYDAT", "2026-07-05")]
    biezace = cp._sugestie_biezace(ledger)
    assert [r["element"] for r in biezace] == ["A", "B"]      # kolejność pierwszego wpisu
    assert biezace[0]["status"] == "ZAMKNIETE"
    assert biezace[0]["uzasadnienie"] == "wdrożone"           # treść z wpisu domykającego
    assert "KANDYDAT 2026-07-01" in biezace[0]["historia"]    # historia nie ginie (Prawo I)
    assert biezace[1]["historia"] == ""                       # jeden wpis → brak historii


def test_sugestie_biezace_rowna_data_wygrywa_pozniejsza_linia():
    """Granica: ten sam dzień → rozstrzyga kolejność dopisania (append-only)."""
    ledger = [_sug("A", "KANDYDAT", "2026-07-21"), _sug("A", "ZAMKNIETE", "2026-07-21")]
    assert cp._sugestie_biezace(ledger)[0]["status"] == "ZAMKNIETE"


def test_sugestie_biezace_granice_puste_i_bez_elementu():
    """Granica: pusty ledger → []; rekord bez `element` nie wywala (grupuje pod '')."""
    assert cp._sugestie_biezace([]) == []
    assert cp._sugestie_biezace([{"typ": "AB", "neuron": "X"}]) == []
    kaleki = [{"typ": "SUGESTIA", "status": "KANDYDAT", "data": "2026-07-21"}]
    assert len(cp._sugestie_biezace(kaleki)) == 1


def test_otwarta_rozroznia_statusy():
    """STALE/ZABLOKOWANE/OCZEKUJE nadal wymagają uwagi; ZAMKNIETE/ZREALIZOWANE nie."""
    for status in ("KANDYDAT", "OCZEKUJE decyzji Cezara", "ZABLOKOWANE", "STALE", "CZESCIOWO"):
        assert cp._otwarta({"status": status}), status
    for status in ("ZAMKNIETE", "zamkniete", " ZREALIZOWANE ", "ODRZUCONE", "WDROZONE"):
        assert not cp._otwarta({"status": status}), status


def test_podsumowanie_ledger_nie_liczy_domknietych_jako_otwartych(tmp_path):
    """Backlog w podsumowaniu startowym nie może rosnąć od samych domknięć."""
    p = tmp_path / "l.jsonl"
    p.write_text(
        '{"typ":"SUGESTIA","element":"A","status":"KANDYDAT","data":"2026-07-01"}\n'
        '{"typ":"SUGESTIA","element":"A","status":"ZAMKNIETE","data":"2026-07-21"}\n'
        '{"typ":"SUGESTIA","element":"B","status":"KANDYDAT","data":"2026-07-05"}\n',
        encoding="utf-8")
    s = cp.podsumowanie_ledger(p)
    assert "3 rekordów" in s and "Sugestie 2 (otwartych 1)" in s


def test_arkusz_sugestie_bez_duplikatow_na_zywym_ledgerze():
    """Regresja na PRAWDZIWYM ledgerze: każdy `element` dokładnie raz w arkuszu."""
    wiersze = cp.zbierz_arkusze()["Sugestie"]
    assert wiersze[0][-1] == "Historia"
    elementy = [w[0] for w in wiersze[1:]]
    duble = {e for e in elementy if elementy.count(e) > 1}
    assert not duble, f"element powtórzony w arkuszu Sugestie: {duble}"


def test_zapis_xlsx_generuje_arkusze(tmp_path):
    """Zapis .xlsx (tylko gdy openpyxl) → plik istnieje, ma 12 arkuszy, Neurony pełne."""
    load_workbook = pytest.importorskip("openpyxl").load_workbook
    cel = tmp_path / "codex.xlsx"
    cp.zapisz_xlsx(cp.zbierz_arkusze(), cel)
    assert cel.exists()
    wb = load_workbook(cel, read_only=True)
    try:
        assert "Neurony" in wb.sheetnames and "Wyniki A-B" in wb.sheetnames
        assert wb["Neurony"].max_row >= 88          # 87 neuronów + nagłówek
    finally:
        wb.close()
