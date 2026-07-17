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


def _plik_o_stemie(stem: str, tresc: str = "A" * 500) -> Path:
    p = Path(tempfile.mkdtemp()) / f"{stem}.txt"
    p.write_text(tresc, encoding="utf-8")
    return p


# Realistyczna „długa nazwa": Windows dopuszcza do 255 znaków na CZŁON nazwy, więc plik
# źródłowy o takiej nazwie DA się utworzyć — dopiero pełna ścieżka cache (katalog + stem +
# hasz + .txt.tmp) przekracza MAX_PATH=260. Dokładnie tak wyglądał realny bug (stem 190 zn.).
_DLUGI_STEM = "M" * 190


# ── GRANICE LIMIT_SCIEZKI (Windows MAX_PATH) — realny bug z 2026-07-16 ────────

def test_krotka_nazwa_stem_nietkniety():
    """
    GRANICA: poniżej limitu stem NIE jest skracany. Kluczowe dla wstecznej zgodności —
    skrócenie stemów zmieniłoby nazwy istniejącego cache i wymusiło rekonwersję 71 książek.
    """
    _srodowisko()
    p = _plik_o_stemie("BIB-999_Test_Krotka")
    assert kv.sciezka_cache(p).name.startswith("BIB-999_Test_Krotka__")


def test_dluga_nazwa_miesci_sie_w_limicie():
    """
    Realny przypadek: książka wrzucona bez zmiany nazwy („Market Microstructure Theory --
    Maureen O'Hara, Maureen O'Hara -- 1_ publ_ in paperback…") → ścieżka 282 znaki → padał
    CAŁY pipeline. Po naprawie: mieści się, łącznie z wariantem .tmp (zapis atomowy).
    """
    _srodowisko()
    p = _plik_o_stemie("Market Microstructure Theory -- Maureen OHara, Maureen OHara -- 1_ publ_ "
                       "in paperback, Malden, Mass, 2005 -- Blackwell Publishing Limited -- "
                       "isbn13 9780631207610 -- 0861bc93e677ce61e1619")
    s = kv.sciezka_cache(p)
    assert len(str(s)) + len(".tmp") <= kv.LIMIT_SCIEZKI
    assert s.suffix == ".txt"


def test_dluga_nazwa_zachowuje_hasz_i_czytelnosc():
    """Skracamy stem, ale hasz (gwarant zgodności treści) i sens nazwy zostają."""
    _srodowisko()
    p = _plik_o_stemie(_DLUGI_STEM)
    s = kv.sciezka_cache(p)
    assert s.name.endswith(f"__{kv._klucz(p)}.txt")     # hasz nietknięty — on decyduje o zgodności
    assert s.name.startswith("MMMMMMMM")                # min. 8 znaków stemu dla człowieka


def test_dluga_nazwa_cache_dziala_end_to_end():
    """Granica realna: po skróceniu zapis+odczyt cache MUSI działać (to tu leciał FileNotFoundError)."""
    _srodowisko()
    p = _plik_o_stemie(_DLUGI_STEM, "B" * 500)
    tekst = kv.ekstrahuj_z_cache(p)                     # zapis atomowy przez .tmp
    assert "BBB" in tekst
    assert kv.sciezka_cache(p).exists()
    assert kv.ekstrahuj_z_cache(p) == tekst             # trafienie cache
    assert list(kv.CACHE_DIR.glob("*.tmp")) == []       # bez śmieci


def test_rozne_dlugie_nazwy_nie_koliduja():
    """GRANICA kolizji: skrócone stemy mogą być IDENTYCZNE — od rozróżnienia jest hasz treści."""
    _srodowisko()
    a = _plik_o_stemie(_DLUGI_STEM, "tresc A" + "A" * 500)
    b = _plik_o_stemie(_DLUGI_STEM, "tresc B" + "B" * 500)
    assert kv.sciezka_cache(a) != kv.sciezka_cache(b)   # ten sam stem, inny hasz → inny plik


# ── GRACEFUL: jedna zła książka nie zabija biegu (Prawo XV) ──────────────────

def test_buduj_cache_nie_pada_na_jednej_zlej_ksiazce(monkeypatch):
    """
    Realny bug 2026-07-16: wyjątek na 71/71 zabił CAŁY `przygotuj_biblioteke` mimo 70 książek
    przerobionych poprawnie. Moduł obiecywał w docstringu „nie wysypuje pipeline" — łamał to.
    """
    d = _srodowisko()
    biblioteka = d / "biblioteka"
    biblioteka.mkdir(parents=True)
    for nazwa in ("BIB-901_A_Dobra.txt", "BIB-902_B_Zla.txt", "BIB-903_C_Dobra.txt"):
        (biblioteka / nazwa).write_text("A" * 500, encoding="utf-8")
    monkeypatch.setattr(kv, "FORMATY_KSIAG", {".txt"})

    oryginal = kv.ekstrahuj_z_cache

    def kapryśna(path, *a, **kw):
        if "Zla" in path.name:
            raise OSError("symulacja: dysk/ścieżka odmawia")
        return oryginal(path, *a, **kw)

    monkeypatch.setattr(kv, "ekstrahuj_z_cache", kapryśna)

    wynik = kv.buduj_cache(biblioteka)                  # NIE MOŻE rzucić
    assert len(wynik) == 3                              # wszystkie trzy w raporcie
    assert wynik["BIB-902_B_Zla.txt"] == 0              # zła oznaczona jako pusta
    assert wynik["BIB-901_A_Dobra.txt"] >= 500          # dobre przerobione mimo złej
    assert wynik["BIB-903_C_Dobra.txt"] >= 500          # także PO złej — bieg nie przerwany


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
