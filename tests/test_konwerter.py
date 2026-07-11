"""
Testy warstwy cache tekstu książek (konwerter.py).

Cache trafiony musi działać BEZ narzędzia konwersji (odblokowanie djvu w chmurze).
Nieudanej ekstrakcji (< MIN_ZNAKOW_CACHE) NIE cache'ujemy (Prawo I — nie utrwalamy braku).
"""

import tempfile
from pathlib import Path

from narzedzia.rag import konwerter as kv


def _srodowisko():
    """Świeży CACHE_DIR w tempie — patchujemy globalny, bo sciezka_cache czyta go w locie."""
    d = Path(tempfile.mkdtemp())
    kv.CACHE_DIR = d / "tekst_cache"
    return d


def _plik_txt(tresc: str) -> Path:
    p = Path(tempfile.mkdtemp()) / "BIB-999_Test_Ksiazka.txt"
    p.write_text(tresc, encoding="utf-8")
    return p


def test_klucz_deterministyczny():
    p = _plik_txt("abc")
    assert kv._klucz(p) == kv._klucz(p) and len(kv._klucz(p)) == 16


def test_sciezka_cache_format():
    _srodowisko()
    p = _plik_txt("x")
    s = kv.sciezka_cache(p)
    assert s.name.startswith("BIB-999_Test_Ksiazka__") and s.suffix == ".txt"


def test_miss_ekstrahuje_i_zapisuje_cache():
    _srodowisko()
    p = _plik_txt("A" * 500)              # .txt czyta ekstraktor bez calibre
    tekst = kv.ekstrahuj_z_cache(p)
    assert "AAA" in tekst
    assert kv.sciezka_cache(p).exists()   # cache zapisany


def test_hit_czyta_z_cache_bez_ekstrakcji():
    _srodowisko()
    p = _plik_txt("A" * 500)
    kv.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    # ręcznie wstawiamy INNĄ treść do cache — dowód, że hit czyta cache, nie plik
    kv.sciezka_cache(p).write_text("TRESC_Z_CACHE", encoding="utf-8")
    assert kv.ekstrahuj_z_cache(p) == "TRESC_Z_CACHE"


def test_pusta_ekstrakcja_nie_jest_cache():
    """Krótki plik (< MIN_ZNAKOW_CACHE) nie zostaje utrwalony w cache."""
    _srodowisko()
    p = _plik_txt("krótko")               # < 200 znaków
    kv.ekstrahuj_z_cache(p)
    assert not kv.sciezka_cache(p).exists()


def test_format_bez_narzedzia_zwraca_pusto_i_nie_cache():
    """djvu bez djvutxt/calibre → '' (abstynencja), bez utrwalania braku."""
    _srodowisko()
    p = Path(tempfile.mkdtemp()) / "BIB-999_Fake.djvu"
    p.write_bytes(b"AT&TFORM....niby-djvu")   # nie jest realnym djvu
    tekst = kv.ekstrahuj_z_cache(p)
    assert tekst == "" and not kv.sciezka_cache(p).exists()


def test_zapis_atomowy_bez_smieci_tmp():
    """Po zapisie cache: pełna treść i ZERO plików .tmp (zapis atomowy os.replace)."""
    _srodowisko()
    p = _plik_txt("Z" * 1000)
    kv.ekstrahuj_z_cache(p)
    cache = kv.sciezka_cache(p)
    assert cache.exists() and len(cache.read_text(encoding="utf-8")) >= 1000
    assert not cache.with_suffix(".txt.tmp").exists()          # brak śmiecia tmp
    assert list(kv.CACHE_DIR.glob("*.tmp")) == []              # w ogóle brak .tmp
