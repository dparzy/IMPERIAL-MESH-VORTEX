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


def test_ponowny_zapis_tego_samego_rekordu_nie_falszuje_odcisku(tmp_path):
    """GRANICA (wada z recenzji 2026-08-05): `zapisz()` bumpowało `sekwencja` przy KAŻDYM
    wywołaniu, a hasz nadpisywało tylko gdy pusty — a `sekwencja` wchodzi do hasza. Efekt:
    po drugim zapisie NIENARUSZONY rekord czytał się jako zmodyfikowany. Bezpiecznik zapalający
    się zawsze jest tak samo martwy jak ten, który nie zapala się nigdy."""
    pa = PA.PamiecAbsolutna(katalog=tmp_path)
    log = _log()
    pa.zapisz(log)
    assert PA.zweryfikuj(log) is True
    sekwencja_po_pierwszym = log.sekwencja

    pa.zapisz(log)                                   # retry / przepisanie tego samego obiektu
    assert log.sekwencja == sekwencja_po_pierwszym, "rekord z odciskiem zachowuje SWOJĄ sekwencję"
    assert PA.zweryfikuj(log) is True, "nikt nie tknął treści — werdykt 'zmodyfikowany' to fałsz"


def test_podmiana_tresci_miedzy_zapisami_nadal_wykryta(tmp_path):
    """Druga strona granicy: cisza po ponownym zapisie nie może oznaczać ślepoty."""
    pa = PA.PamiecAbsolutna(katalog=tmp_path)
    log = _log()
    pa.zapisz(log)
    log.pnl_usdt = 999.0                             # celowo psuję treść po nadaniu odcisku
    pa.zapisz(log)
    assert PA.zweryfikuj(log) is False


def test_nowe_rekordy_wciaz_dostaja_rosnace_sekwencje(tmp_path):
    """Naprawa nie może zabić numeracji: RÓŻNE rekordy tej samej sesji nadal rosną."""
    pa = PA.PamiecAbsolutna(katalog=tmp_path)
    a, b = _log(), _log()
    pa.zapisz(a)
    pa.zapisz(b)
    assert (a.sekwencja, b.sekwencja) == (1, 2)


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


# ── 5. GRANICA W PEŁNYM CYKLU: ODCISK Z NAJPÓŹNIEJSZEGO PUNKTU MUTACJI ───────────
# Wada z recenzji 2026-08-05: odcisk powstawał w `_wskazniki()`, a `cykl()` linijkę dalej
# robił `wskazniki.update(kontekst_dodatkowy)` (RADAR: BTC_TREND/DOMINANCJA/PRZEPLYW).
# Z flagą ON KAŻDA świeca orzekała BRUDNE i blokowała wejście — bezpiecznik zapalający się
# zawsze. Testy niżej idą przez PRAWDZIWY `cykl()`, bo wada mieszkała między metodami,
# a nie w żadnej z nich osobno; test jednej metody nie mógł jej zobaczyć.

def _bary_testowe(n=60, start=100.0, krok=0.5):
    bary, cena = [], start
    for i in range(n):
        o, c = cena, cena + krok
        bary.append({"open": o, "high": c + 0.2, "low": o - 0.2, "close": c,
                     "volume": 1000.0 + i, "symbol": "BTCUSDT", "interwal": "1H"})
        cena = c
    return bary


def _dyrygent_zywy(wskazniki, **kw):
    from imperium.koloseum.paper_trading import PaperTradingEngine
    from imperium.pretorianie.kalkulator_lewara import KalkulatorLewara
    from imperium.legiony.rejestr import zbuduj_legatusa
    return Dyrygent(
        legatus=zbuduj_legatusa(min_neuronow=1, min_przewaga=0.1, aktywuj_smc=False),
        kalkulator=KalkulatorLewara(),
        engine=PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="D11"),
        wskazniki_provider=lambda bary: dict(wskazniki),
        min_pewnosc=0.1, **kw,
    )


WSK_BAZA = {"CLOSE": 100.0, "RSI_14": 55.0}
KONTEKST_RADARU = {"BTC_TREND": 1.0, "BTC_DOMINANCJA": 0.52, "PRZEPLYW_KAPITALU": 0.3}


def test_kontekst_radaru_nie_orzeka_brudne():
    """Komplet PO dolaniu kontekstu — ten, na którym głosuje rój — musi być czysty."""
    d = _dyrygent_zywy(WSK_BAZA, weryfikuj_integralnosc=True)
    d.kontekst_dodatkowy = dict(KONTEKST_RADARU)
    d.cykl("BTCUSDT", _bary_testowe())
    komplet = {**WSK_BAZA, **KONTEKST_RADARU}
    assert d._integralnosc_wskaznikow(komplet) is True, \
        "odcisk wzięty PRZED dolaniem kontekstu → każda świeca BRUDNA i wejście zablokowane"


def test_bez_kontekstu_odcisk_tez_zgodny():
    """Ścieżka bez RADARU nie może się zepsuć przy okazji naprawy tej z RADAREM."""
    d = _dyrygent_zywy(WSK_BAZA, weryfikuj_integralnosc=True)
    d.cykl("BTCUSDT", _bary_testowe())
    assert d._integralnosc_wskaznikow(dict(WSK_BAZA)) is True


def test_mutacja_po_dolaniu_kontekstu_NADAL_wykryta():
    """Druga strona granicy — celowo psuję wskaźniki po ustaleniu odcisku: bezpiecznik,
    który po naprawie przestałby zapalać się w ogóle, byłby tą samą wadą od drugiej strony."""
    d = _dyrygent_zywy(WSK_BAZA, weryfikuj_integralnosc=True)
    d.kontekst_dodatkowy = dict(KONTEKST_RADARU)
    d.cykl("BTCUSDT", _bary_testowe())
    brudne = {**WSK_BAZA, **KONTEKST_RADARU, "RSI_14": 99.0}
    assert d._integralnosc_wskaznikow(brudne) is False
