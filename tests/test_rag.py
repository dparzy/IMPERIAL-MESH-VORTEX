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
    # wstaw testowe dane
    tekst = (
        "Kelly criterion is a formula for position sizing. "
        "GARCH model estimates conditional volatility regime. "
        "Kyle lambda measures market impact and liquidity. "
        "Mean reversion strategy buys oversold assets. "
    )
    chunki = podziel_na_chunki(tekst * 10, max_slow=50, overlap=10)
    for nr, c in enumerate(chunki):
        conn.execute(
            "INSERT INTO fragmenty (zrodlo, tytul, nr_chunk, tekst) VALUES (?,?,?,?)",
            ("test.md", "Test", nr, c),
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
