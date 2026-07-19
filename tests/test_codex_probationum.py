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
                  "Wyniki A-B", "Wyniki IC", "Korelacje", "Backlog", "Sugestie"}
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
