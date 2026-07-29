"""
Testy FABERA (imperium/fundament/faber.py) — Kowal Imperium: narzędzia zewnętrzne.

POWÓD ISTNIENIA MODUŁU I TYCH TESTÓW (zmierzone 2026-07-28): `shutil.which("ebook-convert")`
zwracał None przy zainstalowanym calibre (poza PATH sesji), a potok ekstrakcji odpowiadał
na to pustym tekstem — nieodróżnialnym od „książka bez treści". 13 plików .djvu wypadłoby
po cichu z RAG. Testy pilnują OBU połówek lekarstwa: znaleźć w znanym miejscu ORAZ krzyczeć,
gdy nie ma czego znaleźć.

REGUŁA TEST-GRANIC (Prawo XXI): każdy próg ma test po obu stronach — tu progiem jest
„czy brak narzędzia realnie kosztuje pliki" (0 dotkniętych = cisza, 1 dotknięty = alarm).
"""

import os
import tempfile
from pathlib import Path

from imperium.fundament import faber


def _katalog_z_plikami(nazwy) -> Path:
    d = Path(tempfile.mkdtemp())
    for n in nazwy:
        (d / n).write_text("x", encoding="utf-8")
    return d


def _binarka(katalog: Path, nazwa: str) -> Path:
    """Tworzy plik udający binarkę (na Windows z .exe — tak jej szuka FABER)."""
    plik = katalog / (nazwa + (".exe" if os.name == "nt" else ""))
    plik.write_text("", encoding="utf-8")
    if os.name != "nt":
        plik.chmod(0o755)
    return plik


# ── ZNAJDOWANIE ──────────────────────────────────────────────────────────────
def test_sciezka_z_path_ma_pierwszenstwo(monkeypatch):
    """To, co Cezar ustawił w PATH, wygrywa ze znanymi lokalizacjami wpisanymi w kodzie."""
    faber.wyczysc_cache()
    monkeypatch.setattr(faber.shutil, "which", lambda n: r"C:\z_patha\ebook-convert.exe")
    assert faber.sciezka("ebook-convert") == Path(r"C:\z_patha\ebook-convert.exe")


def test_sciezka_ze_znanego_katalogu_gdy_which_milczy(monkeypatch):
    """Sedno naprawy: which() nic nie wie, a narzędzie LEŻY w znanym miejscu."""
    faber.wyczysc_cache()
    d = Path(tempfile.mkdtemp())
    _binarka(d, "ebook-convert")
    monkeypatch.setattr(faber.shutil, "which", lambda n: None)
    monkeypatch.setitem(os.environ, faber.ENV_KATALOGI, str(d))
    znaleziona = faber.sciezka("ebook-convert")
    assert znaleziona is not None and znaleziona.parent == d


def test_sciezka_none_gdy_nigdzie_nie_ma(monkeypatch):
    """GRANICA: katalog istnieje, ale binarki w nim NIE MA → None (nie zgadujemy ścieżki)."""
    faber.wyczysc_cache()
    pusty = Path(tempfile.mkdtemp())
    monkeypatch.setattr(faber.shutil, "which", lambda n: None)
    monkeypatch.setitem(os.environ, faber.ENV_KATALOGI, str(pusty))
    monkeypatch.setattr(faber, "NARZEDZIA", {"ebook-convert": {
        "pakiet": "calibre", "rola": "test", "formaty": set(),
        "krytyczne": True, "katalogi_win": [], "katalogi_posix": []}})
    assert faber.sciezka("ebook-convert") is None


def test_cache_wynikow_i_odswiezenie(monkeypatch):
    """Wynik jest cache'owany (buduj_cache pyta 208×), ale `odswiez=True` pyta na nowo."""
    faber.wyczysc_cache()
    wolania = []

    def which(n):
        wolania.append(n)
        return None

    monkeypatch.setattr(faber.shutil, "which", which)
    monkeypatch.setitem(os.environ, faber.ENV_KATALOGI, "")
    faber.sciezka("djvutxt")
    faber.sciezka("djvutxt")
    assert len(wolania) == 1
    faber.sciezka("djvutxt", odswiez=True)
    assert len(wolania) == 2


# ── PATH ─────────────────────────────────────────────────────────────────────
def test_zapewnij_path_dopisuje_i_jest_idempotentne(monkeypatch):
    """Katalog trafia na POCZĄTEK PATH, a drugie wywołanie NIE dokłada go ponownie."""
    faber.wyczysc_cache()
    d = Path(tempfile.mkdtemp())
    _binarka(d, "tesseract")
    monkeypatch.setattr(faber.shutil, "which", lambda n: None)
    monkeypatch.setitem(os.environ, faber.ENV_KATALOGI, str(d))
    monkeypatch.setitem(os.environ, "PATH", "/istniejacy")

    faber.zapewnij_path(["tesseract"])
    po_pierwszym = os.environ["PATH"]
    assert po_pierwszym.startswith(str(d))

    faber.zapewnij_path(["tesseract"])
    assert os.environ["PATH"] == po_pierwszym


def test_zapewnij_path_nie_wywala_sie_na_braku(monkeypatch):
    """Brak narzędzia nie może wysypać przygotowania PATH — zwraca None dla tej pozycji."""
    faber.wyczysc_cache()
    monkeypatch.setattr(faber.shutil, "which", lambda n: None)
    monkeypatch.setitem(os.environ, faber.ENV_KATALOGI, str(Path(tempfile.mkdtemp())))
    assert faber.zapewnij_path(["djvutxt"])["djvutxt"] is None


# ── GŁOŚNOŚĆ (Prawo XV — cisza jest gorsza od błędu) ─────────────────────────
def test_wymagaj_rzuca_z_instrukcja_naprawy(monkeypatch):
    faber.wyczysc_cache()
    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    try:
        faber.wymagaj("ebook-convert")
    except faber.BrakNarzedzia as e:
        assert "ebook-convert" in str(e) and faber.ENV_KATALOGI in str(e)
    else:
        raise AssertionError("brak narzędzia MUSI rzucać — cisza była właśnie tą wadą")


def test_alarm_gdy_brak_krytycznego_i_sa_dotkniete_pliki(monkeypatch):
    """GRANICA GÓRNA: 1 plik w dotkniętym formacie → alarm."""
    faber.wyczysc_cache()
    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    katalog = _katalog_z_plikami(["BIB-001_X.djvu"])
    a = faber.alarmy(katalog)
    assert len(a) == 1 and "ebook-convert" in a[0]


def test_brak_alarmu_gdy_zero_dotknietych_plikow(monkeypatch):
    """GRANICA DOLNA: 0 plików w dotkniętym formacie → CISZA (hałas uczy ignorować alarmy)."""
    faber.wyczysc_cache()
    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    katalog = _katalog_z_plikami(["notatka.md"])
    assert faber.alarmy(katalog) == []


def test_brak_niekrytycznego_nie_alarmuje(monkeypatch):
    """djvutxt jest niekrytyczny: calibre czyta .djvu (zmierzone 3× w wachcie biblio28)."""
    faber.wyczysc_cache()

    def sciezka(n, odswiez=False):
        return None if n == "djvutxt" else Path("/jest")

    monkeypatch.setattr(faber, "sciezka", sciezka)
    assert faber.alarmy(_katalog_z_plikami(["BIB-065_Shreve.djvu"])) == []


def test_migawka_liczy_dotkniete_pliki(monkeypatch):
    faber.wyczysc_cache()
    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    katalog = _katalog_z_plikami(["a.djvu", "b.epub", "c.pdf", "d.txt"])
    mig = faber.migawka(katalog)
    po_nazwie = {n["nazwa"]: n for n in mig["narzedzia"]}
    assert po_nazwie["ebook-convert"]["dotkniete_pliki"] == 2      # .djvu + .epub
    assert po_nazwie["tesseract"]["dotkniete_pliki"] == 1          # .pdf
    assert po_nazwie["ebook-meta"]["dotkniete_pliki"] == 0         # bez formatów


def test_banner_pokazuje_stan_kazdego_narzedzia(monkeypatch):
    faber.wyczysc_cache()
    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    b = faber.banner(_katalog_z_plikami(["notatka.md"]))
    assert "FABER" in b and "ebook-convert✗" in b
