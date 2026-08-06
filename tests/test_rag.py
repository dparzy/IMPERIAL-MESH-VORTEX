"""
Testy Bibliotheca-RAG (narzedzia/rag/).
Sprawdzaja ekstraktor i wyszukiwanie FTS na testowej minibazie.
"""
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))

# ── ekstraktor ──────────────────────────────────────────────────────────────

def test_ekstraktor_md():
    from ekstraktor import ekstrahuj, podziel_na_chunki, wyczysc
    p = ROOT / "bibliotheca_ulpia" / "encyklopedia" / "RSK_zarzadzanie_ryzykiem.md"
    tekst = wyczysc(ekstrahuj(p))
    assert "Kelly" in tekst
    assert "Sharpe" in tekst
    chunki = podziel_na_chunki(tekst, max_slow=200, overlap=40)
    assert len(chunki) >= 1
    for c in chunki:
        assert len(c.split()) >= 20


# ── _epub: odporność na kruchość ebooklib (Prawo XV) ─────────────────────────
# Realny bug 2026-07-16 (BIB-075, whitepaper Bitcoina): ebooklib 0.20.0 robi
#   nav_node = html_node.xpath("//nav[@*='toc']")[0]
# bez zabezpieczenia → IndexError na POPRAWNYM epubie, który ma nawigację bez elementu
# oznaczonego 'toc'. Efekt: 0 znaków, książka cicho nie wchodzi do RAG.

# `_epub` importuje ebooklib LENIWIE (wewnątrz funkcji — brak twardej zależności przy imporcie),
# więc łatamy prawdziwy moduł `ebooklib.epub`: `from ebooklib import epub` wiąże OBIEKT modułu,
# a `epub.read_epub` rozwiązuje się dopiero przy wywołaniu — patch zadziała.

def _ebooklib_epub_albo_pomin():
    """Zwraca `ebooklib.epub` albo POMIJA test — `ebooklib` to zależność OPCJONALNA.

    Zmierzone 2026-07-26: te trzy testy oblewały pakiet w chmurze (`ModuleNotFoundError`),
    choć nie było czego naprawiać — `ekstraktor._epub` importuje ebooklib LENIWIE i nie ma
    go w requirements. Test podmienia PRAWDZIWY moduł, więc gałęzi nie da się wymusić bez
    niego (inaczej niż przy `plotext`). Brak zasobu to POMINIĘCIE, nie porażka i nie zieleń
    — `SkipTest` jest głośno liczony przez runner Imperium i honorowany przez pytest.
    """
    try:
        from ebooklib import epub as epub_mod
    except ImportError as e:
        import unittest
        raise unittest.SkipTest(f"ebooklib nieobecny (zależność opcjonalna): {e}") from e
    return epub_mod


def test_epub_ebooklib_pada_fallback_na_calibre(monkeypatch):
    """Wyjątek z ebooklib MUSI przełączyć na calibre, nie zwrócić pustki."""
    import ekstraktor as ex
    epub_mod = _ebooklib_epub_albo_pomin()

    def wybuch(*a, **kw):
        raise IndexError("list index out of range")   # dokładnie bug ebooklib 0.20.0

    monkeypatch.setattr(epub_mod, "read_epub", wybuch)
    monkeypatch.setattr(ex, "_calibre", lambda p: "TEKST Z CALIBRE")
    assert ex._epub(Path("nieistotna.epub")) == "TEKST Z CALIBRE"


def test_epub_pusty_wynik_bez_wyjatku_tez_fallback(monkeypatch):
    """
    GRANICA: ebooklib potrafi ZWRÓCIĆ PUSTKĘ bez rzucania wyjątku (żaden ITEM_DOCUMENT
    nierozpoznany). Cicha strata jest gorsza od głośnej (Prawo XV) — też fallback.
    """
    import ekstraktor as ex
    epub_mod = _ebooklib_epub_albo_pomin()

    class _PustaKsiazka:
        def get_items_of_type(self, _typ):
            return []

    monkeypatch.setattr(epub_mod, "read_epub", lambda *a, **kw: _PustaKsiazka())
    monkeypatch.setattr(ex, "_calibre", lambda p: "TEKST Z CALIBRE")
    assert ex._epub(Path("nieistotna.epub")) == "TEKST Z CALIBRE"


def test_epub_dziala_gdy_ebooklib_ok(monkeypatch):
    """Gdy ebooklib działa — NIE wołamy calibre (nie płacimy za konwersję bez powodu)."""
    import ekstraktor as ex
    epub_mod = _ebooklib_epub_albo_pomin()

    class _Item:
        def get_content(self):
            return b"<html><body><p>Tresc ksiazki</p></body></html>"

    class _Ksiazka:
        def get_items_of_type(self, _typ):
            return [_Item()]

    def _nie_wolaj(p):
        raise AssertionError("calibre NIE powinno być wołane, gdy ebooklib działa")

    monkeypatch.setattr(epub_mod, "read_epub", lambda *a, **kw: _Ksiazka())
    monkeypatch.setattr(ex, "_calibre", _nie_wolaj)
    assert "Tresc ksiazki" in ex._epub(Path("nieistotna.epub"))


def test_ekstraktor_api():
    # Sprawdza że ekstraktor ma właściwe publiczne funkcje (bez ładowania dużych plików)
    from ekstraktor import ekstrahuj, podziel_na_chunki, wyczysc
    assert callable(ekstrahuj)
    assert callable(podziel_na_chunki)
    assert callable(wyczysc)
    # wyczysc usuwa nadmiarowe spacje
    assert wyczysc("a  b\n\n\nc") == "a b\n\nc"


def test_podzial_overlap():
    from ekstraktor import podziel_na_chunki
    slowa = " ".join([f"w{i}" for i in range(500)])
    chunki = podziel_na_chunki(slowa, max_slow=100, overlap=20)
    assert len(chunki) >= 4
    # chunki powinny sie nakladac
    pierwsze = chunki[0].split()
    drugie = chunki[1].split()
    wspolne = set(pierwsze[-20:]) & set(drugie[:20])
    assert len(wspolne) > 0


def test_podzial_overlap_rowny_max():
    # overlap == max_slow nie moze dawac nieskonczonej petli
    from ekstraktor import podziel_na_chunki
    slowa = " ".join([f"w{i}" for i in range(100)])
    chunki = podziel_na_chunki(slowa, max_slow=50, overlap=50)
    assert len(chunki) >= 1
    assert len(chunki) < 200  # nie moze byc nieskonczony


# ── baza FTS ─────────────────────────────────────────────────────────────────

def _stworz_testowa_baze(tmp_path: Path) -> Path:
    from ekstraktor import podziel_na_chunki
    baza = tmp_path / "test.db"
    conn = sqlite3.connect(str(baza))
    conn.execute("""
        CREATE TABLE fragmenty (
            id INTEGER PRIMARY KEY, zrodlo TEXT, tytul TEXT,
            korpus TEXT NOT NULL DEFAULT 'biblioteka',
            nr_chunk INTEGER, tekst TEXT, meta TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE fts
        USING fts5(tekst, zrodlo UNINDEXED, tytul UNINDEXED,
                   content='fragmenty', content_rowid='id')
    """)
    conn.execute("""
        CREATE TABLE wektory (fragment_id INTEGER PRIMARY KEY, wektor BLOB)
    """)
    conn.execute("CREATE INDEX idx_zrodlo ON fragmenty(zrodlo)")
    # wstaw testowe dane (dwa korpusy)
    tekst = (
        "Kelly criterion is a formula for position sizing. "
        "GARCH model estimates conditional volatility regime. "
        "Kyle lambda measures market impact and liquidity. "
        "Mean reversion strategy buys oversold assets. "
    )
    chunki = podziel_na_chunki(tekst * 10, max_slow=50, overlap=10)
    for nr, c in enumerate(chunki):
        conn.execute(
            "INSERT INTO fragmenty (zrodlo, tytul, korpus, nr_chunk, tekst) VALUES (?,?,?,?,?)",
            ("test.md", "Test", "biblioteka", nr, c),
        )
    # jeden fragment w korpusie docs
    conn.execute(
        "INSERT INTO fragmenty (zrodlo, tytul, korpus, nr_chunk, tekst) VALUES (?,?,?,?,?)",
        ("docs.md", "Docs", "docs", 0,
         "Gubernator GARCH regime multiplier neuron Imperium dokumentacja kodu"),
    )
    conn.commit()
    conn.execute("INSERT INTO fts(fts) VALUES('rebuild')")
    conn.commit()
    conn.close()
    return baza


def test_fts_szukaj_podstawowy():
    with tempfile.TemporaryDirectory() as tmp:
        baza = _stworz_testowa_baze(Path(tmp))
        from szukaj import szukaj  # type: ignore[import]
        wyniki = szukaj("Kelly criterion", topk=3, tryb="fts", baza=baza, cichy=True)
        assert len(wyniki) > 0
        assert any("Kelly" in w.tekst for w in wyniki)


def test_fts_brak_wynikow():
    with tempfile.TemporaryDirectory() as tmp:
        baza = _stworz_testowa_baze(Path(tmp))
        from szukaj import szukaj  # type: ignore[import]
        wyniki = szukaj("xyzzy_nie_istnieje_zzz", topk=3, tryb="fts", baza=baza, cichy=True)
        assert wyniki == []


def test_fts_topk():
    with tempfile.TemporaryDirectory() as tmp:
        baza = _stworz_testowa_baze(Path(tmp))
        from szukaj import szukaj  # type: ignore[import]
        wyniki = szukaj("volatility", topk=2, tryb="fts", baza=baza, cichy=True)
        assert len(wyniki) <= 2


def test_szukaj_bez_bazy():
    with tempfile.TemporaryDirectory() as tmp:
        from szukaj import szukaj  # type: ignore[import]
        baza_nieistniejaca = Path(tmp) / "ghost.db"
        wyniki = szukaj("test", topk=3, tryb="fts", baza=baza_nieistniejaca, cichy=True)
        assert wyniki == []


def test_formatuj():
    with tempfile.TemporaryDirectory() as tmp:
        baza = _stworz_testowa_baze(Path(tmp))
        from szukaj import szukaj, formatuj  # type: ignore[import]
        wyniki = szukaj("GARCH", topk=2, tryb="fts", baza=baza, cichy=True)
        tekst = formatuj(wyniki, "GARCH")
        assert "GARCH" in tekst or "Wyniki dla" in tekst


def test_filtr_korpusu():
    with tempfile.TemporaryDirectory() as tmp:
        baza = _stworz_testowa_baze(Path(tmp))
        from szukaj import szukaj  # type: ignore[import]
        # GARCH wystepuje i w biblioteka i w docs
        w_docs = szukaj("GARCH", topk=5, tryb="fts", baza=baza, cichy=True, korpus="docs")
        assert all(w.korpus == "docs" for w in w_docs)
        assert any("Gubernator" in w.tekst for w in w_docs)
        w_bib = szukaj("GARCH", topk=5, tryb="fts", baza=baza, cichy=True, korpus="biblioteka")
        assert all(w.korpus == "biblioteka" for w in w_bib)


def test_korpus_w_wyniku():
    with tempfile.TemporaryDirectory() as tmp:
        baza = _stworz_testowa_baze(Path(tmp))
        from szukaj import szukaj  # type: ignore[import]
        wyniki = szukaj("Kelly", topk=2, tryb="fts", baza=baza, cichy=True)
        assert all(hasattr(w, "korpus") for w in wyniki)
        assert all(w.korpus for w in wyniki)


# ── ekstraktor: formaty danych tematycznych ──────────────────────────────────

def test_ekstraktor_csv():
    from ekstraktor import ekstrahuj
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "dane.csv"
        p.write_text("symbol,strategia,wynik\nBTC,trend,zysk\nETH,range,strata\n", encoding="utf-8")
        tekst = ekstrahuj(p)
        assert "Kolumny" in tekst
        assert "BTC" in tekst
        assert "trend" in tekst


def test_ekstraktor_json():
    from ekstraktor import ekstrahuj
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "dane.json"
        p.write_text('{"neuron": "EXP-14", "opis": "Kyle lambda", "waga": 1.5}', encoding="utf-8")
        tekst = ekstrahuj(p)
        assert "EXP-14" in tekst
        assert "Kyle lambda" in tekst


def test_ekstraktor_txt():
    from ekstraktor import ekstrahuj
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "notatka.txt"
        p.write_text("Lekcja z backtestu: MTF gate to tarcza bessy.", encoding="utf-8")
        tekst = ekstrahuj(p)
        assert "tarcza bessy" in tekst


def test_ekstraktor_csv_pusty():
    from ekstraktor import ekstrahuj
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusty.csv"
        p.write_text("", encoding="utf-8")
        assert ekstrahuj(p) == ""


def test_ekstraktor_json_uszkodzony():
    from ekstraktor import ekstrahuj
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "zly.json"
        p.write_text("{nie jest json", encoding="utf-8")
        assert ekstrahuj(p) == ""


def test_calibre_output_rozszerzenie_txt_nie_tmp():
    """Regresja (Prawo XV + XXI TEST-GRANIC): _calibre MUSI dać ebook-convert plik wyjściowy
    z rozszerzeniem `.txt`. Poprzednie `.txt.tmp` → calibre widziało format `tmp` i padało
    (`ValueError: No plugin to handle output format: tmp`), CICHO gubiąc wszystkie djvu
    (Kissell/Aronson/Shreve/Sutton-Barto). Test podmienia subprocess.run pod ekstraktorem,
    udając udaną konwersję, i pilnuje kontraktu rozszerzenia + zwrotu tekstu + sprzątania."""
    import importlib
    ekstraktor = importlib.import_module("ekstraktor")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "BIB-999_Fake.djvu"
        src.write_bytes(b"AT&TFORM")
        zapis: dict = {}

        def _fake_run(cmd, **kw):
            out = Path(cmd[2])                       # ebook-convert <src> <out>
            zapis["out"] = out
            out.write_text("TRESC Z CALIBRE " * 20, encoding="utf-8")
            return None                              # check=True nie rzuca — sukces

        # FABER wyciszony razem z subprocess (zmierzone 2026-08-06, pierwszy bieg VALLUM):
        # `_calibre` pyta FABERA o binarkę ZANIM cokolwiek uruchomi, więc na maszynie bez
        # calibre test padał na `BrakNarzedzia` — mimo że sprawdza kontrakt rozszerzenia,
        # do którego prawdziwy calibre nie jest potrzebny. Podmiana (zamiast pominięcia)
        # jest tu LEPSZA: pominięcie oddawałoby pokrycie na każdej maszynie bez calibre,
        # a `_calibre` ma własną gałąź „FABERA brak" i to jej właśnie używamy.
        orig = ekstraktor.subprocess.run
        orig_faber = ekstraktor._faber
        ekstraktor.subprocess.run = _fake_run
        ekstraktor._faber = lambda: None
        try:
            tekst = ekstraktor._calibre(src)
        finally:
            ekstraktor.subprocess.run = orig
            ekstraktor._faber = orig_faber

        out = zapis["out"]
        assert out.suffix == ".txt"                  # granica: format wyjścia = txt
        assert not str(out).endswith(".tmp")         # jawnie: nie regresja `.tmp`
        assert "TRESC Z CALIBRE" in tekst            # zwraca skonwertowany tekst
        assert not out.exists()                      # scratch posprzątany (finally)


def test_calibre_porazka_zwraca_pusto_i_sprzata():
    """Gdy ebook-convert padnie (brak calibre / błąd) — _calibre zwraca '' i nie zostawia śmieci."""
    import importlib
    ekstraktor = importlib.import_module("ekstraktor")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "BIB-999_Fake.djvu"
        src.write_bytes(b"AT&TFORM")

        def _fake_run(cmd, **kw):
            Path(cmd[2]).write_text("polowiczne", encoding="utf-8")  # scratch powstał...
            raise RuntimeError("ebook-convert failed")               # ...ale konwersja padła

        orig = ekstraktor.subprocess.run
        orig_faber = ekstraktor._faber          # patrz komentarz w teście obok — brak calibre
        ekstraktor.subprocess.run = _fake_run   # nie może przesądzać o tym teście
        ekstraktor._faber = lambda: None
        try:
            assert ekstraktor._calibre(src) == ""
        finally:
            ekstraktor.subprocess.run = orig
            ekstraktor._faber = orig_faber
        # brak śmieci .calibre-tmp.txt w katalogu źródła (sprzątanie w finally)
        assert list(Path(tmp).glob("*.calibre-tmp.txt")) == []


# ── indeksacja: korpus + tryb przyrostowy ────────────────────────────────────

def _mini_korpus(tmp: Path) -> Path:
    """Tworzy mini strukturę bibliotheca_ulpia/dane/ do testów indeksacji."""
    dane = tmp / "bib" / "dane"
    dane.mkdir(parents=True)
    (dane / "lekcje.txt").write_text(
        "Kelly criterion sizing. GARCH volatility regime. " * 10, encoding="utf-8"
    )
    return tmp / "bib"


def test_indeksacja_przyrostowa():
    import importlib
    sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))
    indeksuj_mod = importlib.import_module("indeksuj")
    with tempfile.TemporaryDirectory() as tmp:
        tmpp = Path(tmp)
        baza = tmpp / "test.db"
        dane = tmpp / "dane"
        dane.mkdir()
        f1 = dane / "a.txt"
        f1.write_text("Kelly criterion sizing strategy. " * 15, encoding="utf-8")

        # monkeypatch _zbierz_pliki by uzyc naszego folderu
        orig = indeksuj_mod._zbierz_pliki
        indeksuj_mod._zbierz_pliki = lambda korpus, tylko_enc: [(p, "dane") for p in sorted(dane.glob("*.txt"))]
        try:
            s1 = indeksuj_mod.indeksuj(baza=baza, bez_wektorow=True)
            assert s1["pliki_przetworzone"] == 1
            # drugie uruchomienie przyrostowe — nic nowego
            s2 = indeksuj_mod.indeksuj(baza=baza, bez_wektorow=True, tylko_nowe=True)
            assert s2["pliki_przetworzone"] == 0
            assert s2["pliki_pominiete"] == 1
            # dodaj nowy plik
            (dane / "b.txt").write_text("GARCH volatility regime filter. " * 15, encoding="utf-8")
            s3 = indeksuj_mod.indeksuj(baza=baza, bez_wektorow=True, tylko_nowe=True)
            assert s3["pliki_przetworzone"] == 1
            assert s3["pliki_pominiete"] == 1
        finally:
            indeksuj_mod._zbierz_pliki = orig


def test_zrodlo_z_cache_z_katalogu_i_fallback():
    """_zrodlo_z_cache: plik cache `<stem>__<hash>.txt` → nazwa binarna z katalogu (hit),
    a bez wpisu w katalogu → sam stem (fallback). Rdzeń indeksowania z cache po usunięciu
    binariów z repo (decyzja 2026-07-11)."""
    import importlib
    ix = importlib.import_module("indeksuj")
    mapa = {"BIB-007_LdP_AFML": "BIB-007_LdP_AFML.epub"}
    hit = Path("x/tekst_cache/BIB-007_LdP_AFML__abc1230000000000.txt")
    miss = Path("x/tekst_cache/BIB-999_Nieznana__def4560000000000.txt")
    assert ix._zrodlo_z_cache(hit, mapa) == "BIB-007_LdP_AFML.epub"   # katalog → nazwa binarna
    assert ix._zrodlo_z_cache(miss, mapa) == "BIB-999_Nieznana"        # fallback: sam stem


def test_indeks_ksiazki_z_cache_odtwarza_zrodlo():
    """Książki indeksowane z tekst_cache/*.txt zapisują zrodlo = nazwa binarna (z katalogu),
    NIE nazwę pliku cache. Gwarancja: filtr/wzbogacenie katalogu działają po przeniesieniu
    binariów poza repo (cloud RAG czyta sam tekst)."""
    import importlib
    ix = importlib.import_module("indeksuj")
    with tempfile.TemporaryDirectory() as tmp:
        tmpp = Path(tmp)
        cache = tmpp / "tekst_cache"          # nazwa katalogu MUSI być tekst_cache (warunek pętli)
        cache.mkdir()
        (cache / "BIB-777_Author_Some-Book__deadbeef0badf00d.txt").write_text(
            "Kelly criterion sizing GARCH volatility regime microstructure liquidity. " * 20,
            encoding="utf-8")
        kat = {"BIB-777_Author_Some-Book": "BIB-777_Author_Some-Book.pdf"}
        baza = tmpp / "t.db"
        orig_zbierz, orig_mapa = ix._zbierz_pliki, ix._mapa_stem_plik
        ix._zbierz_pliki = lambda korpus, tylko_enc: [(p, "biblioteka") for p in sorted(cache.glob("*.txt"))]
        ix._mapa_stem_plik = lambda: kat
        try:
            ix.indeksuj(baza=baza, bez_wektorow=True)
        finally:
            ix._zbierz_pliki, ix._mapa_stem_plik = orig_zbierz, orig_mapa
        conn = sqlite3.connect(str(baza))
        zrodla = {r[0] for r in conn.execute("SELECT DISTINCT zrodlo FROM fragmenty")}
        tytuly = {r[0] for r in conn.execute("SELECT DISTINCT tytul FROM fragmenty")}
        conn.close()
        assert zrodla == {"BIB-777_Author_Some-Book.pdf"}, zrodla    # nazwa binarna, nie cache
        assert tytuly == {"Author — Some Book"}, tytuly              # tytuł z odtworzonej nazwy


# ── mcp server ───────────────────────────────────────────────────────────────

def test_mcp_initialize():
    sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))
    from mcp_server import _handle  # type: ignore[import]
    resp = _handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["serverInfo"]["name"] == "bibliotheca-rag"


def test_mcp_tools_list():
    from mcp_server import _handle  # type: ignore[import]
    resp = _handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    names = [t["name"] for t in resp["result"]["tools"]]
    assert "biblioteka_szukaj" in names
    assert "biblioteka_info" in names


def test_mcp_nieznane_narzedzie():
    from mcp_server import _handle  # type: ignore[import]
    resp = _handle({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "nieistniejace", "arguments": {}},
    })
    assert "error" in resp
