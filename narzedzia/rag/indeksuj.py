#!/usr/bin/env python3
"""
Bibliotheca-RAG: indeksacja ksiazek + encyklopedii + (opcjonalnie) dokumentow Imperium.

Uzycie:
    python narzedzia/rag/indeksuj.py                      # pelna reindeksacja biblioteki
    python narzedzia/rag/indeksuj.py --tylko-nowe         # PRZYROSTOWO (tylko nowe/zmienione)
    python narzedzia/rag/indeksuj.py --korpus wszystko    # biblioteka + dane/ + docs/
    python narzedzia/rag/indeksuj.py --korpus docs        # tylko dokumentacja Imperium
    python narzedzia/rag/indeksuj.py --tylko-enc          # tylko encyklopedia (szybkie)
    python narzedzia/rag/indeksuj.py --bez-wektorow       # tylko FTS (bez modelu/sieci)

Korpusy (--korpus):
    biblioteka  (domyslny) — ksiazki BIB-* + encyklopedia + vademecum + bibliotheca_ulpia/dane/
    docs        — dokumentacja Imperium (docs/*.md) jako osobne zrodlo
    wszystko    — biblioteka + docs

Tryby:
    pelny (domyslny)   — kasuje baze i buduje od zera (deterministyczny)
    --tylko-nowe       — przyrostowy: po hashu pliku, tylko nowe/zmienione reindeksowane

Baza:
- FTS5 (szybki fulltext BM25) — zawsze
- Tabela wektorow (embeddingi) — gdy sentence-transformers + model dostepne
"""
from __future__ import annotations
import argparse
import hashlib
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BIBLIOTEKA = ROOT / "bibliotheca_ulpia"
# Wyekstrahowany tekst książek — JEDYNE źródło RAG dla książek. Binaria (epub/pdf/djvu/…)
# żyją tylko lokalnie, poza gitem (decyzja Cezara 2026-07-11: ryzyko praw autorskich + 504 MB);
# repo niesie sam tekst, więc chmura buduje pełny RAG bez binariów i bez calibre.
CACHE_KSIAG = BIBLIOTEKA / "dane" / "tekst_cache"
DOCS = ROOT / "docs"
DEFAULT_BAZA = ROOT / "narzedzia" / "rag" / "baza_wiedzy.db"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Dane tematyczne (nie-książki) w bibliotheca_ulpia/dane/ — indeksowane wprost przez ekstraktor.
SUF_DANE = ("*.md", "*.txt", "*.csv", "*.json")

sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))
from ekstraktor import ekstrahuj, podziel_na_chunki, wyczysc  # noqa: E402
try:
    from narzedzia.rag import katalog  # noqa: E402
except ImportError:  # pragma: no cover — kontekst z narzedzia/rag na sys.path
    import katalog  # type: ignore[no-redef]  # noqa: E402


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fragmenty (
            id       INTEGER PRIMARY KEY,
            zrodlo   TEXT NOT NULL,
            tytul    TEXT NOT NULL,
            korpus   TEXT NOT NULL DEFAULT 'biblioteka',
            nr_chunk INTEGER NOT NULL,
            tekst    TEXT NOT NULL,
            meta     TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts
        USING fts5(tekst, zrodlo UNINDEXED, tytul UNINDEXED, content='fragmenty', content_rowid='id')
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wektory (
            fragment_id INTEGER PRIMARY KEY REFERENCES fragmenty(id),
            wektor      BLOB NOT NULL
        )
    """)
    # rejestr plikow dla trybu przyrostowego
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pliki (
            zrodlo TEXT PRIMARY KEY,
            hash   TEXT NOT NULL,
            korpus TEXT NOT NULL DEFAULT 'biblioteka',
            ts     REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_zrodlo ON fragmenty(zrodlo)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_korpus ON fragmenty(korpus)")
    conn.commit()


def _migruj_schema(conn: sqlite3.Connection) -> bool:
    """Zwraca True gdy baza ma stary schemat (brak kolumny korpus/tabeli pliki)."""
    kolumny = {r[1] for r in conn.execute("PRAGMA table_info(fragmenty)").fetchall()}
    if not kolumny:
        return False  # pusta baza, _init_db zrobi swoje
    return "korpus" not in kolumny


def _wyczysc_db(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM wektory")
    conn.execute("DELETE FROM fts")
    conn.execute("DELETE FROM fragmenty")
    conn.execute("DELETE FROM pliki")
    conn.commit()


def _hash_pliku(p: Path) -> str:
    h = hashlib.sha256()
    h.update(str(p.stat().st_size).encode())
    h.update(str(int(p.stat().st_mtime)).encode())
    return h.hexdigest()[:16]


def _usun_zrodlo(conn: sqlite3.Connection, zrodlo: str) -> None:
    """Usuwa wszystkie fragmenty (i wektory) danego zrodla — przed reindeksacja."""
    ids = [r[0] for r in conn.execute("SELECT id FROM fragmenty WHERE zrodlo=?", (zrodlo,))]
    if ids:
        ph = ",".join("?" * len(ids))
        conn.execute(f"DELETE FROM wektory WHERE fragment_id IN ({ph})", ids)
        conn.execute("DELETE FROM fragmenty WHERE zrodlo=?", (zrodlo,))
    conn.commit()


def _dodaj_fragmenty(
    conn: sqlite3.Connection, zrodlo: str, tytul: str, korpus: str, chunki: list[str]
) -> list[int]:
    ids = []
    for nr, tekst in enumerate(chunki):
        cur = conn.execute(
            "INSERT INTO fragmenty (zrodlo, tytul, korpus, nr_chunk, tekst) VALUES (?,?,?,?,?)",
            (zrodlo, tytul, korpus, nr, tekst),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    return ids


def _zbierz_pliki(korpus: str, tylko_enc: bool) -> list[tuple[Path, str]]:
    """Zwraca liste (sciezka, korpus)."""
    pliki: list[tuple[Path, str]] = []

    if korpus in ("biblioteka", "wszystko"):
        if not tylko_enc:
            # KSIĄŻKI: indeksujemy z CACHE tekstu (tekst_cache/*.txt), NIE z binariów — te są
            # tylko lokalnie (patrz CACHE_KSIAG). `zrodlo` odtwarzamy do nazwy binarnej z katalogu
            # w pętli (_zrodlo_z_cache), by wzbogacenie/filtr autor-tag działały jak dotąd.
            if CACHE_KSIAG.is_dir():
                pliki += [(p, "biblioteka") for p in sorted(CACHE_KSIAG.glob("*.txt"))]
            # dane tematyczne (csv/json/txt/md) w bibliotheca_ulpia/dane/ — glob NIE-rekurencyjny,
            # więc podkatalog tekst_cache/ nie jest tu łapany (książki wchodzą wyżej, dokładnie raz).
            dane_dir = BIBLIOTEKA / "dane"
            if dane_dir.is_dir():
                for suf in SUF_DANE:
                    pliki += [(p, "dane") for p in sorted(dane_dir.glob(suf))]
        # encyklopedia + vademecum .md (zawsze w korpusie biblioteka)
        for folder in ("encyklopedia", "vademecum"):
            pliki += [(p, "biblioteka") for p in sorted((BIBLIOTEKA / folder).glob("*.md"))]

    if korpus in ("docs", "wszystko"):
        pliki += [(p, "docs") for p in sorted(DOCS.glob("*.md"))]

    return pliki


def _tytul(nazwa: str) -> str:
    """Tytuł z nazwy źródła (str). `BIB-XXX_Autor_Tytul(.ext)` → `Autor — Tytul`."""
    n = Path(nazwa).stem
    # BIB-XXX_Autor_Tytul → Autor — Tytul
    if n.startswith("BIB-"):
        parts = n.split("_", 2)
        if len(parts) == 3:
            return f"{parts[1]} — {parts[2].replace('-', ' ')}"
        if len(parts) == 2:
            return parts[1].replace("-", " ")
    return n.replace("_", " ").replace("-", " ")


def _mapa_stem_plik() -> dict[str, str]:
    """Mapa `stem książki` → `nazwa pliku binarnego` z katalogu (katalog_ksiag.json).
    Pozwala odtworzyć `zrodlo` = nazwa binarna (zgodna z katalogiem/filtrem) przy indeksowaniu
    z cache tekstu, mimo że binaria nie są wersjonowane. Brak katalogu → {} (graceful)."""
    return {Path(plik).stem: plik for plik in katalog.wczytaj_katalog()}


def _zrodlo_z_cache(cache_path: Path, mapa: dict[str, str]) -> str:
    """`zrodlo` książki odtworzone z pliku cache `<stem>__<hash>.txt`.
    Preferuje nazwę binarną z katalogu (wzbogacenie/filtr działają jak dla binariów); brak
    w katalogu → sam stem (książka i tak zindeksowana — Prawo XV: żadnego martwego głosu)."""
    stem = cache_path.stem
    if "__" in stem:
        stem = stem.rsplit("__", 1)[0]
    return mapa.get(stem, stem)


def _zaladuj_model(model_name: str, bez_wektorow: bool):
    if bez_wektorow:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        print(f"[RAG] Ładuję model: {model_name}...")
        model = SentenceTransformer(model_name)
        print("[RAG] Model gotowy ✅")
        return model
    except ImportError:
        print("[RAG] sentence-transformers niedostępne — tylko FTS")
    except Exception as e:
        print(f"[RAG] Model niedostępny ({type(e).__name__}) — tylko FTS")
    return None


def indeksuj(
    baza: Path = DEFAULT_BAZA,
    model_name: str = DEFAULT_MODEL,
    tylko_enc: bool = False,
    bez_wektorow: bool = False,
    korpus: str = "biblioteka",
    tylko_nowe: bool = False,
) -> dict:
    baza.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(baza))

    # migracja starego schematu: jesli brak kolumny korpus → przebuduj od zera
    if baza.exists() and _migruj_schema(conn):
        print("[RAG] Stary schemat bazy — przebudowuję strukturę.")
        for t in ("wektory", "fts", "fragmenty", "pliki"):
            conn.execute(f"DROP TABLE IF EXISTS {t}")
        conn.commit()
        tylko_nowe = False  # pelna reindeksacja po migracji

    _init_db(conn)
    if not tylko_nowe:
        _wyczysc_db(conn)

    model = _zaladuj_model(model_name, bez_wektorow)
    pliki = _zbierz_pliki(korpus, tylko_enc)
    print(f"[RAG] Korpus={korpus} | plików: {len(pliki)} | tryb={'przyrostowy' if tylko_nowe else 'pełny'}")

    znane_hashe: dict[str, str] = {}
    if tylko_nowe:
        znane_hashe = {r[0]: r[1] for r in conn.execute("SELECT zrodlo, hash FROM pliki")}

    mapa_ksiag = _mapa_stem_plik()   # stem → nazwa binarna: odtworzenie zrodla książek z cache

    total_chunks = 0
    pominiete = 0
    przetworzone = 0
    t0 = time.time()
    for p, kor in pliki:
        # Cache książek (tekst_cache/) → zrodlo = nazwa binarna z katalogu (zgodność z filtrem/
        # wzbogaceniem). Pozostałe źródła (dane tematyczne, dokumenty .md) → nazwa pliku jak dotąd.
        zrodlo = _zrodlo_z_cache(p, mapa_ksiag) if p.parent.name == "tekst_cache" else p.name
        h = _hash_pliku(p)

        if tylko_nowe and znane_hashe.get(zrodlo) == h:
            pominiete += 1
            continue

        print(f"  → {zrodlo} [{kor}] ...", end=" ", flush=True)
        tekst = wyczysc(ekstrahuj(p))
        if not tekst.strip():
            print("pominięto (brak tekstu)")
            continue
        chunki = podziel_na_chunki(tekst)
        if not chunki:
            print("pominięto (0 chunków)")
            continue

        # tryb przyrostowy: usun stare fragmenty tego zrodla przed dodaniem nowych
        if tylko_nowe:
            _usun_zrodlo(conn, zrodlo)

        ids = _dodaj_fragmenty(conn, zrodlo, _tytul(zrodlo), kor, chunki)

        if model is not None:
            import numpy as np
            vecs = model.encode(chunki, show_progress_bar=False, batch_size=32)
            for fid, vec in zip(ids, vecs):
                conn.execute(
                    "INSERT OR REPLACE INTO wektory (fragment_id, wektor) VALUES (?,?)",
                    (fid, np.array(vec, dtype="float32").tobytes()),
                )

        conn.execute(
            "INSERT OR REPLACE INTO pliki (zrodlo, hash, korpus, ts) VALUES (?,?,?,?)",
            (zrodlo, h, kor, time.time()),
        )
        conn.commit()
        total_chunks += len(chunki)
        przetworzone += 1
        print(f"{len(chunki)} chunków")

    # przebuduj FTS na koniec (raz — szybsze niz po kazdym pliku)
    conn.execute("INSERT INTO fts(fts) VALUES('rebuild')")
    conn.commit()

    dt = time.time() - t0
    stat = {
        "fragmenty_nowe": total_chunks,
        "pliki_przetworzone": przetworzone,
        "pliki_pominiete": pominiete,
        "czas_s": round(dt, 1),
    }
    print(
        f"\n[RAG] Gotowe: +{total_chunks} fragmentów, {przetworzone} plików, "
        f"{pominiete} bez zmian, {dt:.1f}s → {baza}"
    )
    conn.close()
    return stat


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Indeksacja Bibliothecy-RAG")
    ap.add_argument("--baza", default=str(DEFAULT_BAZA))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--korpus", choices=["biblioteka", "docs", "wszystko"], default="biblioteka")
    ap.add_argument("--tylko-enc", action="store_true", help="tylko encyklopedia (szybkie)")
    ap.add_argument("--tylko-nowe", action="store_true", help="PRZYROSTOWO — tylko nowe/zmienione pliki")
    ap.add_argument("--bez-wektorow", action="store_true", help="tylko FTS, bez embeddingow")
    args = ap.parse_args()
    indeksuj(
        Path(args.baza),
        args.model,
        args.tylko_enc,
        args.bez_wektorow,
        args.korpus,
        args.tylko_nowe,
    )
