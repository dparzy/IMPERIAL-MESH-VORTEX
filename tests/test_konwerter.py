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


def test_zly_plik_przy_OBECNYM_narzedziu_zwraca_pusto_i_nie_cache(monkeypatch):
    """
    Abstynencja należy się ZŁEMU PLIKOWI, nie brakującemu narzędziu (rozróżnienie z 2026-07-28).

    Test jawnie udaje, że narzędzie JEST — wcześniej wynik zależał od tego, czy maszyna ma
    calibre: zielony na laptopie Cezara, czerwony w chmurze. Test, którego werdykt zmienia
    środowisko, nie broni niczego.
    """
    from narzedzia.rag import ekstraktor

    _srodowisko()
    monkeypatch.setattr(ekstraktor, "_calibre", lambda p: "")   # narzędzie jest, plik zły
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


# ── FABER W POTOKU: brak narzędzia jest GŁOŚNY, nie pusty (Prawo XV, 2026-07-28) ──

def test_calibre_rzuca_gdy_brak_binarki(monkeypatch):
    """
    Sedno naprawy: dawniej `_calibre` zwracał "" na KAŻDY wyjątek, więc „nie ma calibre"
    wyglądało identycznie jak „książka bez tekstu". Zmierzone tego dnia: which() nie widział
    calibre'a mimo instalacji → 13 plików .djvu wypadłoby po cichu z RAG.
    """
    from imperium.fundament import faber
    from narzedzia.rag import ekstraktor

    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    p = _plik_txt("x")
    try:
        ekstraktor._calibre(p)
    except faber.BrakNarzedzia:
        return
    raise AssertionError("brak calibre MUSI być słyszalny, a nie zwracać pusty tekst")


def test_ekstrahuj_nie_zjada_braku_narzedzia(monkeypatch):
    """Szeroki `except` w `ekstrahuj` nie może uciszyć braku narzędzia (dotyczy CAŁEGO biegu)."""
    from imperium.fundament import faber
    from narzedzia.rag import ekstraktor

    monkeypatch.setattr(faber, "sciezka", lambda n, odswiez=False: None)
    udawany_djvu = Path(tempfile.mkdtemp()) / "BIB-900_Test.djvu"
    udawany_djvu.write_bytes(b"AT&TFORM")
    try:
        ekstraktor.ekstrahuj(udawany_djvu)
    except faber.BrakNarzedzia:
        return
    raise AssertionError("BrakNarzedzia musi lecieć w górę, nie kończyć się pustym stringiem")


def test_buduj_cache_liczy_brak_narzedzia_osobno(monkeypatch):
    """Brak binarki nie może być raportowany jako „208 uszkodzonych książek"."""
    from imperium.fundament import faber

    d = _srodowisko()
    biblioteka = d / "biblioteka2"
    biblioteka.mkdir(parents=True)
    for nazwa in ("BIB-911_A.txt", "BIB-912_B.txt"):
        (biblioteka / nazwa).write_text("A" * 500, encoding="utf-8")
    monkeypatch.setattr(kv, "FORMATY_KSIAG", {".txt"})

    def bez_narzedzia(path, *a, **kw):
        raise faber.BrakNarzedzia("symulacja: brak ebook-convert")

    monkeypatch.setattr(kv, "ekstrahuj_z_cache", bez_narzedzia)
    wynik = kv.buduj_cache(biblioteka)          # NIE MOŻE rzucić
    assert wynik == {"BIB-911_A.txt": 0, "BIB-912_B.txt": 0}


# ── OCR jako opt-in OFF (ZASADA WPIĘCIA) — 5.2 s/stronę na PEDES ─────────────

def _pdf_udawany() -> Path:
    p = Path(tempfile.mkdtemp()) / "BIB-970_Skan.pdf"
    p.write_bytes(b"%PDF-1.4 nie-prawdziwy")
    return p


def test_ocr_domyslnie_wylaczony(monkeypatch):
    """Bez flagi tesseract NIE rusza: 98 plików .pdf × 5.2 s/stronę zamieniłoby bieg w godziny."""
    from narzedzia.rag import ekstraktor

    _srodowisko()

    def wybuch(*a, **kw):
        raise AssertionError("OCR ruszył mimo ocr=False — opt-in przestał być opt-in")

    monkeypatch.setattr(ekstraktor, "_pdf_ocr", wybuch)
    assert kv.ekstrahuj_z_cache(_pdf_udawany()) == ""


def test_ocr_wlaczony_ratuje_skan(monkeypatch):
    """Z flagą: PDF poniżej progu idzie na OCR, a odzyskany tekst trafia do cache."""
    from narzedzia.rag import ekstraktor

    _srodowisko()
    monkeypatch.setattr(ekstraktor, "_pdf_ocr", lambda p, *a, **kw: "T" * 500)
    p = _pdf_udawany()
    assert kv.ekstrahuj_z_cache(p, ocr=True) == "T" * 500
    assert kv.sciezka_cache(p).exists()          # odzyskany skan zostaje utrwalony


def test_ocr_nie_rusza_na_progu(monkeypatch):
    """GRANICA: dokładnie MIN_ZNAKOW_CACHE znaków to SUKCES — OCR byłby marnotrawstwem."""
    from narzedzia.rag import ekstraktor

    _srodowisko()
    monkeypatch.setattr(ekstraktor, "ekstrahuj", lambda p: "x" * kv.MIN_ZNAKOW_CACHE)

    def wybuch(*a, **kw):
        raise AssertionError("OCR ruszył przy tekście DOKŁADNIE na progu (to nie jest porażka)")

    monkeypatch.setattr(ekstraktor, "_pdf_ocr", wybuch)
    assert len(kv.ekstrahuj_z_cache(_pdf_udawany(), ocr=True)) == kv.MIN_ZNAKOW_CACHE


def test_ocr_rusza_ponizej_progu(monkeypatch):
    """GRANICA: o jeden znak za mało → OCR (druga strona tego samego progu)."""
    from narzedzia.rag import ekstraktor

    _srodowisko()
    monkeypatch.setattr(ekstraktor, "ekstrahuj", lambda p: "x" * (kv.MIN_ZNAKOW_CACHE - 1))
    monkeypatch.setattr(ekstraktor, "_pdf_ocr", lambda p, *a, **kw: "O" * 500)
    assert kv.ekstrahuj_z_cache(_pdf_udawany(), ocr=True) == "O" * 500


def test_ocr_tylko_dla_pdf(monkeypatch):
    """Skan to problem PDF-a; .epub poniżej progu ma inną przyczynę i OCR jej nie naprawi."""
    from narzedzia.rag import ekstraktor

    _srodowisko()
    monkeypatch.setattr(ekstraktor, "ekstrahuj", lambda p: "")

    def wybuch(*a, **kw):
        raise AssertionError("OCR ruszył na formacie innym niż PDF")

    monkeypatch.setattr(ekstraktor, "_pdf_ocr", wybuch)
    epub = Path(tempfile.mkdtemp()) / "BIB-971_X.epub"
    epub.write_bytes(b"PK")
    assert kv.ekstrahuj_z_cache(epub, ocr=True) == ""
