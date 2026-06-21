#!/usr/bin/env python3
"""
Bibliotheca-RAG: indeksacja ksiazek + encyklopedii.

Uzycie:
    python narzedzia/rag/indeksuj.py [--baza PATH] [--model MODEL] [--tylko-enc]

Tworzy baze_wiedzy.db z:
- FTS5 (szybki fulltext BM25) — zawsze
- Tabela wektorow (embeddingi) — gdy sentence-transformers dostepne
"""
from __future__ import annotations
import argparse
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BIBLIOTEKA = ROOT / "bibliotheca_ulpia"
DEFAULT_BAZA = ROOT / "narzedzia" / "rag" / "baza_wiedzy.db"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))
from ekstraktor import ekstrahuj, podziel_na_chunki, wyczysc  # noqa: E402


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS fragmenty (
            id       INTEGER PRIMARY KEY,
            zrodlo   TEXT NOT NULL,
            tytul    TEXT NOT NULL,
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_zrodlo ON fragmenty(zrodlo)")
    conn.commit()


def _wyczysc_db(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM wektory")
    conn.execute("DELETE FROM fts")
    conn.execute("DELETE FROM fragmenty")
    conn.commit()


def _dodaj_fragmenty(conn: sqlite3.Connection, zrodlo: str, tytul: str, chunki: list[str]) -> list[int]:
    ids = []
    for nr, tekst in enumerate(chunki):
        cur = conn.execute(
            "INSERT INTO fragmenty (zrodlo, tytul, nr_chunk, tekst) VALUES (?,?,?,?)",
            (zrodlo, tytul, nr, tekst),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    # sync FTS
    conn.execute("INSERT INTO fts(fts) VALUES('rebuild')")
    conn.commit()
    return ids


def _zbierz_pliki(tylko_enc: bool) -> list[Path]:
    pliki: list[Path] = []
    if not tylko_enc:
        for suf in ("*.epub", "*.pdf", "*.azw3", "*.mobi", "*.djvu"):
            pliki += sorted(BIBLIOTEKA.glob(suf))
    # encyklopedia + vademecum .md
    for folder in ("encyklopedia", "vademecum"):
        pliki += sorted((BIBLIOTEKA / folder).glob("*.md"))
    return pliki


def _tytul(p: Path) -> str:
    n = p.stem
    # BIB-XXX_Autor_Tytul → Autor — Tytul
    if n.startswith("BIB-"):
        parts = n.split("_", 2)
        if len(parts) == 3:
            return f"{parts[1]} — {parts[2].replace('-', ' ')}"
        if len(parts) == 2:
            return parts[1].replace("-", " ")
    return n.replace("_", " ").replace("-", " ")


def indeksuj(
    baza: Path = DEFAULT_BAZA,
    model_name: str = DEFAULT_MODEL,
    tylko_enc: bool = False,
    bez_wektorow: bool = False,
) -> None:
    baza.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(baza))
    _init_db(conn)
    _wyczysc_db(conn)

    # model embeddingów
    model = None
    if not bez_wektorow:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"[RAG] Ładuję model: {model_name}...")
            model = SentenceTransformer(model_name)
            print("[RAG] Model gotowy ✅")
        except ImportError:
            print("[RAG] sentence-transformers niedostępne — tylko FTS")

    pliki = _zbierz_pliki(tylko_enc)
    print(f"[RAG] Pliki do indeksacji: {len(pliki)}")

    total_chunks = 0
    t0 = time.time()
    for p in pliki:
        print(f"  → {p.name} ...", end=" ", flush=True)
        tekst = wyczysc(ekstrahuj(p))
        if not tekst.strip():
            print("pominięto (brak tekstu)")
            continue
        chunki = podziel_na_chunki(tekst)
        if not chunki:
            print("pominięto (0 chunków)")
            continue
        tytul = _tytul(p)
        ids = _dodaj_fragmenty(conn, p.name, tytul, chunki)

        if model is not None:
            import numpy as np
            vecs = model.encode(chunki, show_progress_bar=False, batch_size=32)
            for fid, vec in zip(ids, vecs):
                conn.execute(
                    "INSERT OR REPLACE INTO wektory (fragment_id, wektor) VALUES (?,?)",
                    (fid, np.array(vec, dtype="float32").tobytes()),
                )
            conn.commit()

        total_chunks += len(chunki)
        print(f"{len(chunki)} chunków")

    print(f"\n[RAG] Gotowe: {total_chunks} fragmentów w {time.time()-t0:.1f}s → {baza}")
    conn.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Indeksacja Bibliothecy-RAG")
    ap.add_argument("--baza", default=str(DEFAULT_BAZA))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--tylko-enc", action="store_true", help="tylko encyklopedia (szybkie)")
    ap.add_argument("--bez-wektorow", action="store_true", help="tylko FTS, bez embeddingow")
    args = ap.parse_args()
    indeksuj(Path(args.baza), args.model, args.tylko_enc, args.bez_wektorow)
