"""Testy D1.1 — bramki integralności, która do 2026-08-05 nie mogła się zapalić.

Stan sprzed naprawy: `dyrygent.py` wołał doradcę Hermesa z `hash_ok` jako STAŁĄ prawdziwą,
a pole `ImperiumLog.hash_sha256` miało **zero przypisań w całej bazie kodu**. Hermes ma
gałąź `if not hash_ok → NIEKOMPLETNE`, więc łańcuch WYGLĄDAŁ na zamknięty, nie mając czego
porównywać — martwy głos udający bezpiecznik (Prawo XV), przy Prawie IX wymieniającym to
pole jako obowiązkowe.

Najważniejsze testy to te o GRANICY „brak dowodu":
  • rekord bez hasza → `False`, nie `True`,
  • weryfikacja bez odcisku odniesienia → `False`, nie `True`.
Gdyby któryś z nich zaczął zwracać `True`, wróciłaby dokładnie ta sama wada pod nową nazwą.
"""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from imperium.biblioteki import pamiec_absolutna as PA  # noqa: E402
from imperium.koloseum.dyrygent import Dyrygent  # noqa: E402


def _log(**nadpisz):
    dane = {"symbol": "BTCUSDT", "log_typ": PA.TypLogu.SYGNAL, "sesja_id": "test",
            "interwal": "4H"}
    dane.update(nadpisz)
    return PA.ImperiumLog(**dane)


# ── 1. ODCISK REKORDU ────────────────────────────────────────────────────────────

def test_hash_deterministyczny():
    log = _log()
    assert PA.policz_hash(log) == PA.policz_hash(log)


def test_hash_nie_zalezy_od_samego_pola_hasza():
    """Gdyby hasz wchodził do własnego wyliczenia, weryfikacja nie mogłaby przejść NIGDY."""
    log = _log()
    przed = PA.policz_hash(log)
    log.hash_sha256 = "cokolwiek"
    assert PA.policz_hash(log) == przed


def test_hash_zmienia_sie_przy_zmianie_tresci():
    a = _log()
    odcisk = PA.policz_hash(a)
    a.pnl_usdt = 123.45
    assert PA.policz_hash(a) != odcisk


# ── 2. GRANICA: BRAK DOWODU NIE JEST DOWODEM NIEWINNOŚCI ─────────────────────────

def test_rekord_bez_hasza_nie_jest_zweryfikowany():
    """Rekordy sprzed naprawy mają puste pole — nie wolno ich ogłaszać czystymi."""
    assert PA.zweryfikuj(_log()) is False


def test_rekord_z_haszem_przechodzi():
    log = _log()
    log.hash_sha256 = PA.policz_hash(log)
    assert PA.zweryfikuj(log) is True


def test_podmiana_tresci_po_zapisie_wykryta():
    log = _log()
    log.hash_sha256 = PA.policz_hash(log)
    log.kapital_po = 999.0
    assert PA.zweryfikuj(log) is False


# ── 3. ZAPIS WYPEŁNIA POLE, KTÓRE MIAŁO ZERO PRZYPISAŃ ───────────────────────────

def test_zapisz_wypelnia_hash(tmp_path):
    pa = PA.PamiecAbsolutna(katalog=tmp_path)
    log = _log()
    assert log.hash_sha256 == ""
    pa.zapisz(log)
    assert log.hash_sha256, "pole `hash_sha256` musi być wypełnione przy zapisie (Prawo IX)"
    assert PA.zweryfikuj(log) is True


def test_zapisz_nie_nadpisuje_cudzego_hasza(tmp_path):
    """Rekord przepisywany (migracja/import) zachowuje odcisk ŹRÓDŁA — inaczej podmiana
    treści uwierzytelniałaby się sama, czyli wracałaby naprawiana tu klasa."""
    pa = PA.PamiecAbsolutna(katalog=tmp_path)
    log = _log(hash_sha256="odcisk-z-innego-systemu")
    pa.zapisz(log)
    assert log.hash_sha256 == "odcisk-z-innego-systemu"


def test_zapisany_rekord_odczytuje_sie_jako_zweryfikowany(tmp_path):
    """Pełna pętla: zapis → odczyt z dysku → weryfikacja. Hasz liczony PO nadaniu
    sekwencji, więc odczytany rekord musi się zgadzać co do znaku."""
    pa = PA.PamiecAbsolutna(katalog=tmp_path)
    pa.zapisz(_log())
    wczytane = pa.wczytaj(symbol="BTCUSDT")
    assert len(wczytane) == 1
    assert PA.zweryfikuj(wczytane[0]) is True


# ── 4. DYRYGENT — OPT-IN OFF ZNACZY ZERO ZMIANY DECYZJI ──────────────────────────

def _dyrygent(flaga, odcisk):
    """Lekki zastępnik `self` — testujemy JEDNĄ metodę, nie budowę całego Dyrygenta."""
    return SimpleNamespace(weryfikuj_integralnosc=flaga, _odcisk_wskaznikow=odcisk,
                           odcisk_wskaznikow=Dyrygent.odcisk_wskaznikow)


WSK = {"RSI_14": 55.0, "ATR_14": 1.2}


def test_flaga_off_zachowuje_dzisiejsze_zachowanie():
    """GRANICA WPIĘCIA: dopóki A/B nie potwierdzi, ani jedna decyzja nie może się zmienić."""
    ja = _dyrygent(False, None)
    assert Dyrygent._integralnosc_wskaznikow(ja, WSK) is True


def test_flaga_on_zgodny_odcisk_przechodzi():
    ja = _dyrygent(True, Dyrygent.odcisk_wskaznikow(WSK))
    assert Dyrygent._integralnosc_wskaznikow(ja, WSK) is True


def test_flaga_on_zmienione_wskazniki_wykryte():
    ja = _dyrygent(True, Dyrygent.odcisk_wskaznikow(WSK))
    assert Dyrygent._integralnosc_wskaznikow(ja, {**WSK, "RSI_14": 99.0}) is False


def test_flaga_on_bez_odcisku_orzeka_brudne():
    """Druga granica „braku dowodu": bez odniesienia NIE WOLNO orzec „czyste"."""
    ja = _dyrygent(True, None)
    assert Dyrygent._integralnosc_wskaznikow(ja, WSK) is False


def test_odcisk_niezalezny_od_kolejnosci_kluczy():
    """Słownik budują Budowniczy i adaptery — odcisk ma świadczyć o TREŚCI, nie o kolejności."""
    a = Dyrygent.odcisk_wskaznikow({"A": 1, "B": 2})
    b = Dyrygent.odcisk_wskaznikow({"B": 2, "A": 1})
    assert a == b


def test_odcisk_znosi_wartosci_niestandardowe():
    """`default=str` — pole nowego typu nie może wywrócić liczenia odcisku."""
    from datetime import datetime
    assert Dyrygent.odcisk_wskaznikow({"kiedy": datetime(2026, 8, 5)})
