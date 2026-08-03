"""
Testy LUSTRUM — organ mierzący POŻYTEK organów (CORONA A).

Co pilnujemy (Reguła Test-Granic — każdy próg ma test granicy):
  • pożytek to SUMA WAŻONA pięciu świadectw, nigdy jeden sygnał,
  • cztery werdykty Cezara (ZOSTAW / WPIAC / ZBADAC / ARCHIWUM) i kto decyduje,
  • zegar karencji liczy się od PIERWSZEGO podejrzenia zapisanego w ledgerze,
  • powrót do służby KASUJE zegar jawnym rekordem, nie ciszą,
  • HONESTA MISSIO nigdy nie nadaje się automatycznie,
  • czytanie nie ma skutków ubocznych — zegar rusza dopiero `znacz()`.
"""

import json
import tempfile
from datetime import date, timedelta
from pathlib import Path

from imperium.pretorianie import lustrum as lu


def _sygn(**nadpisz):
    """Świadek bez żadnego pożytku — testy dokładają po jednym sygnale."""
    baza = {"wolacze_prod": 0, "wolacze_test": 0, "cli": False,
            "w_dokumentach": False, "w_ledgerze": False}
    baza.update(nadpisz)
    return baza


# ── POŻYTEK ─────────────────────────────────────────────────────────────────────

def test_pozytek_bez_swiadectw_to_zero():
    assert lu.pozytek(_sygn()) == 0.0


def test_pozytek_komplet_swiadectw_to_jeden():
    """GRANICA górna: pięć wag ma sumować się dokładnie do 1.0, nie 0.99 ani 1.01."""
    pelny = _sygn(wolacze_prod=3, wolacze_test=2, cli=True,
                  w_dokumentach=True, w_ledgerze=True)
    assert lu.pozytek(pelny) == 1.0


def test_pozytek_liczy_ISTNIENIE_wolacza_nie_ich_liczbe():
    """Dziesięciu wołaczy nie czyni modułu dziesięć razy potrzebniejszym.

    Gdyby waga rosła z liczbą, moduł-narzędzie wołany wszędzie (np. helper) zawsze
    biłby organ wołany raz w jedynym miejscu, w którym ma sens — a to nie jest miara
    pożytku, tylko popularności.
    """
    assert lu.pozytek(_sygn(wolacze_prod=1)) == lu.pozytek(_sygn(wolacze_prod=99))


def test_zaden_pojedynczy_sygnal_nie_wystarcza_do_uniewinnienia():
    """Sedno organu: to była wada wersji jednosygnałowej (100% fałszywek 2026-08-04)."""
    for sygnal in ("cli", "w_dokumentach", "w_ledgerze"):
        assert lu.pozytek(_sygn(**{sygnal: True})) < lu.PROG_AKTYWNY


def test_sam_wolacz_produkcyjny_juz_uniewinnia():
    """GRANICA progu: 0.40 to DOKŁADNIE waga wołacza — próg jest domknięty od dołu."""
    assert lu.pozytek(_sygn(wolacze_prod=1)) == lu.PROG_AKTYWNY
    assert lu.wniosek(_sygn(wolacze_prod=1), lu.PROG_AKTYWNY) == "ZOSTAW"


def test_przyrzad_reczny_cli_plus_docs_nie_trafia_do_archiwum():
    """ZMIERZONE 2026-08-04: 25/25 sierot miało CLI i wzmiankę w docs.

    Narzędzie wołane z wiersza poleceń z definicji nie ma wołacza w kodzie. Gdyby
    trafiało do ARCHIWUM, organ kazałby wycofać 25 zdrowych przyrządów pomiarowych.
    """
    s = _sygn(cli=True, w_dokumentach=True)
    assert lu.wniosek(s, lu.pozytek(s)) == "ZBADAC"


# ── CZTERY WERDYKTY ─────────────────────────────────────────────────────────────

def test_wniosek_WPIAC_gdy_otestowany_ale_nieuzywany():
    """Pierwsza pozycja checklisty Prawa XV: gotowy, ale niepodpięty = MAJĄTEK."""
    s = _sygn(wolacze_test=2, w_dokumentach=True)
    assert lu.wniosek(s, lu.pozytek(s)) == "WPIAC"


def test_wniosek_ARCHIWUM_dopiero_przy_zerze_swiadectw():
    s = _sygn()
    assert lu.wniosek(s, lu.pozytek(s)) == "ARCHIWUM"


def test_kazdy_werdykt_wskazuje_ORGAN_DECYDUJACY():
    """Rozkaz Cezara: organ ma ZGŁASZAĆ decydentowi, nie wyrokować sam."""
    for werdykt, (ikona, decydent) in lu.WERDYKTY.items():
        assert ikona, f"{werdykt} bez ikony"
        assert decydent, f"{werdykt} bez wskazanego decydenta"
    assert "XVI" in lu.WERDYKTY["ZBADAC"][1], "SCALIĆ musi iść do pomiaru korelacji"


# ── ZEGAR KARENCJI ──────────────────────────────────────────────────────────────

def test_stopien_bez_historii_to_PODEJRZANY_nie_karencja():
    assert lu.stopien(0.0, {"podejrzany_od": None, "zwolniony": False}) == "PODEJRZANY"


def test_karencja_dokladnie_w_dniu_progu():
    """GRANICA: KARENCJA_DNI ma być domknięte od dołu (>=), nie ominięte o jeden dzień."""
    dzis = date(2026, 8, 4)
    start = dzis - timedelta(days=lu.KARENCJA_DNI)
    hist = {"podejrzany_od": start.isoformat(), "zwolniony": False}
    assert lu.stopien(0.0, hist, dzis=dzis) == "KARENCJA"

    o_dzien_za_wczesnie = {"podejrzany_od": (start + timedelta(days=1)).isoformat(),
                           "zwolniony": False}
    assert lu.stopien(0.0, o_dzien_za_wczesnie, dzis=dzis) == "PODEJRZANY"


def test_zepsuta_data_NIE_AWANSUJE_do_karencji():
    """Śmieć w ledgerze nie może pchnąć modułu bliżej wycofania (bezpieczna strona)."""
    hist = {"podejrzany_od": "wkrótce", "zwolniony": False}
    assert lu.stopien(0.0, hist) == "PODEJRZANY"
    assert lu.stopien(0.0, {"podejrzany_od": None, "zwolniony": False}) == "PODEJRZANY"


def test_honesta_missio_bije_wszystko_ale_tylko_z_ledgera():
    """Zwolnienie ze służby NIGDY nie wynika z pomiaru — wyłącznie z zatwierdzenia."""
    assert lu.stopien(1.0, {"podejrzany_od": None, "zwolniony": True}) == "HONESTA_MISSIO"
    assert lu.stopien(0.0, {"podejrzany_od": None, "zwolniony": False}) != "HONESTA_MISSIO"


def test_pozytek_powyzej_progu_daje_AKTYWNY_mimo_starego_podejrzenia():
    hist = {"podejrzany_od": "2020-01-01", "zwolniony": False}
    assert lu.stopien(0.9, hist) == "AKTYWNY"


# ── LEDGER (append-only) ────────────────────────────────────────────────────────

def _ledger(tmp, rekordy):
    p = Path(tmp) / "lustrum.jsonl"
    p.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rekordy) + "\n",
                 encoding="utf-8")
    return p


def test_historia_powrot_do_sluzby_KASUJE_zegar():
    """Moduł, który znów służy, zaczyna od zera — inaczej karencja naliczałaby się
    za czasy, gdy narzędzie było już z powrotem w użyciu."""
    with tempfile.TemporaryDirectory() as tmp:
        lu.LEDGER = _ledger(tmp, [
            {"data": "2026-01-01", "modul": "a.py", "stopien": "PODEJRZANY"},
            {"data": "2026-02-01", "modul": "a.py", "stopien": "AKTYWNY"},
        ])
        assert lu.historia("a.py")["podejrzany_od"] is None


def test_historia_bierze_PIERWSZE_podejrzenie_po_ostatnim_powrocie():
    with tempfile.TemporaryDirectory() as tmp:
        lu.LEDGER = _ledger(tmp, [
            {"data": "2026-01-01", "modul": "a.py", "stopien": "PODEJRZANY"},
            {"data": "2026-02-01", "modul": "a.py", "stopien": "AKTYWNY"},
            {"data": "2026-03-01", "modul": "a.py", "stopien": "PODEJRZANY"},
            {"data": "2026-04-01", "modul": "a.py", "stopien": "KARENCJA"},
        ])
        assert lu.historia("a.py")["podejrzany_od"] == "2026-03-01"


def test_uszkodzona_linia_ledgera_nie_wywraca_zegara():
    """GRANICA: jedna zepsuta linia nie może oślepić organu na wszystkie pozostałe."""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "lustrum.jsonl"
        p.write_text('{"data": "2026-01-01", "modul": "a.py", "stopien": "PODEJRZANY"}\n'
                     'to nie jest json\n'
                     '{"data": "2026-01-02", "modul": "b.py", "stopien": "PODEJRZANY"}\n',
                     encoding="utf-8")
        lu.LEDGER = p
        assert lu.historia("a.py")["podejrzany_od"] == "2026-01-01"
        assert lu.historia("b.py")["podejrzany_od"] == "2026-01-02"


def test_brak_ledgera_to_czysta_karta_nie_wyjatek():
    with tempfile.TemporaryDirectory() as tmp:
        lu.LEDGER = Path(tmp) / "nie_istnieje.jsonl"
        assert lu.historia("cokolwiek.py") == {"podejrzany_od": None, "zwolniony": False}


def test_modul_zwolniony_zostaje_zwolniony():
    with tempfile.TemporaryDirectory() as tmp:
        lu.LEDGER = _ledger(tmp, [
            {"data": "2026-01-01", "modul": "a.py", "stopien": "HONESTA_MISSIO"},
        ])
        assert lu.historia("a.py")["zwolniony"] is True


# ── ŹRÓDŁA I SPÓJNOŚĆ ORGANU ────────────────────────────────────────────────────

def test_moduly_pomijaja_init_i_cache():
    sciezki = lu.moduly()
    assert sciezki, "cenzus nie znalazł ani jednego organu"
    assert all(p.name != "__init__.py" for p in sciezki)
    assert all("__pycache__" not in p.parts for p in sciezki)


def test_moduly_sa_posortowane_wynik_deterministyczny():
    assert lu.moduly() == sorted(lu.moduly())


def test_sygnaly_rozdzielaja_wolaczy_produkcyjnych_od_testowych():
    """Pokrycie testem to INNE świadectwo niż realne użycie — sklejenie ich dałoby
    modułowi martwemu w produkcji ten sam wynik co wpiętemu."""
    s = lu.sygnaly(Path(lu.KORZEN) / "imperium" / "pretorianie" / "lustrum.py",
                   korpus={}, dokumenty="", ledger="")
    assert "wolacze_prod" in s and "wolacze_test" in s


def test_wagi_sumuja_sie_do_jednosci():
    """Bez tego pożytek przestałby być liczbą w [0,1] i próg straciłby znaczenie."""
    suma = (lu.WAGA_WOLACZ_PROD + lu.WAGA_CLI + lu.WAGA_DOKUMENT
            + lu.WAGA_LEDGER + lu.WAGA_TEST)
    assert abs(suma - 1.0) < 1e-9


def test_kazdy_stopien_ma_ikone():
    for st in ("AKTYWNY", "PODEJRZANY", "KARENCJA", "HONESTA_MISSIO"):
        assert lu.STOPNIE.get(st)
