#!/usr/bin/env python3
"""
Bibliotheca-RAG: wyszukiwanie semantyczne + FTS.

Uzycie:
    python narzedzia/rag/szukaj.py "GARCH volatility regime"
    python narzedzia/rag/szukaj.py "Kyle lambda liquidity" --topk 5 --tryb fts
    python narzedzia/rag/szukaj.py "PIN informed trading" --topk 3 --tryb wektor

Tryby:
    hybrid  (domyslny) — FTS + wektor, reranking przez polaczone wyniki
    fts     — tylko pelnotekstowy BM25
    wektor  — tylko embeddingi (cos sim)
"""
from __future__ import annotations
import argparse
import sqlite3
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BAZA = ROOT / "narzedzia" / "rag" / "baza_wiedzy.db"
DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class Wynik(NamedTuple):
    id: int
    zrodlo: str
    tytul: str
    nr_chunk: int
    tekst: str
    score: float


def _fts_szukaj(conn: sqlite3.Connection, zapytanie: str, topk: int) -> list[Wynik]:
    rows = conn.execute(
        """
        SELECT f.id, f.zrodlo, f.tytul, f.nr_chunk, f.tekst,
               bm25(fts) AS score
        FROM fts
        JOIN fragmenty f ON fts.rowid = f.id
        WHERE fts MATCH ?
        ORDER BY score
        LIMIT ?
        """,
        (zapytanie, topk * 3),
    ).fetchall()
    # bm25() zwraca ujemne wartości — mniejsza = lepsza
    return [Wynik(*r) for r in rows]


def _wektor_szukaj(conn: sqlite3.Connection, zapytanie: str, topk: int, model) -> list[Wynik]:
    import numpy as np

    qvec = model.encode([zapytanie], show_progress_bar=False)[0].astype("float32")
    qvec /= (np.linalg.norm(qvec) + 1e-9)

    rows = conn.execute(
        "SELECT w.fragment_id, w.wektor FROM wektory w"
    ).fetchall()

    scored: list[tuple[float, int]] = []
    for fid, blob in rows:
        vec = np.frombuffer(blob, dtype="float32").copy()
        vec /= (np.linalg.norm(vec) + 1e-9)
        sim = float(qvec @ vec)
        scored.append((sim, fid))

    scored.sort(reverse=True)
    top_ids = [fid for _, fid in scored[:topk]]
    if not top_ids:
        return []

    placeholders = ",".join("?" * len(top_ids))
    frag_rows = conn.execute(
        f"SELECT id, zrodlo, tytul, nr_chunk, tekst FROM fragmenty WHERE id IN ({placeholders})",
        top_ids,
    ).fetchall()

    id_to_sim = {fid: sim for sim, fid in scored[:topk]}
    wyniki = [Wynik(*r, id_to_sim.get(r[0], 0.0)) for r in frag_rows]
    wyniki.sort(key=lambda x: -x.score)
    return wyniki


def szukaj(
    zapytanie: str,
    topk: int = 5,
    tryb: str = "hybrid",
    baza: Path = DEFAULT_BAZA,
    model_name: str = DEFAULT_MODEL,
    cichy: bool = False,
) -> list[Wynik]:
    if not baza.exists():
        print(f"[RAG] Baza nie istnieje: {baza}\nUruchom najpierw: python narzedzia/rag/indeksuj.py", file=sys.stderr)
        return []

    conn = sqlite3.connect(str(baza))

    model = None
    if tryb in ("wektor", "hybrid"):
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(model_name)
        except ImportError:
            if tryb == "wektor":
                print("[RAG] brak sentence-transformers, przełączam na FTS", file=sys.stderr)
                tryb = "fts"

    # sprawdź czy są wektory
    has_vecs = conn.execute("SELECT COUNT(*) FROM wektory").fetchone()[0] > 0
    if tryb in ("wektor", "hybrid") and not has_vecs:
        tryb = "fts"
        if not cichy:
            print("[RAG] Brak wektorów w bazie, używam FTS", file=sys.stderr)

    if tryb == "fts":
        wyniki = _fts_szukaj(conn, zapytanie, topk)[:topk]
    elif tryb == "wektor":
        wyniki = _wektor_szukaj(conn, zapytanie, topk, model)[:topk]
    else:  # hybrid
        fts_wyniki = _fts_szukaj(conn, zapytanie, topk)
        vec_wyniki = _wektor_szukaj(conn, zapytanie, topk, model)
        # połącz po ID, preferuj te które wystąpiły w obu
        seen: dict[int, Wynik] = {}
        bonus_ids = {w.id for w in fts_wyniki} & {w.id for w in vec_wyniki}
        for w in fts_wyniki + vec_wyniki:
            if w.id not in seen:
                seen[w.id] = w
        # bonus dla wyników w obu listach (reranking)
        wyniki = sorted(seen.values(), key=lambda x: (x.id not in bonus_ids, -x.score))[:topk]

    conn.close()
    return wyniki


def formatuj(wyniki: list[Wynik], zapytanie: str = "") -> str:
    if not wyniki:
        return f"[RAG] Brak wyników dla: {zapytanie!r}"
    linie = [f"[RAG] Wyniki dla: {zapytanie!r} ({len(wyniki)})\n"]
    for i, w in enumerate(wyniki, 1):
        linie.append(f"{'='*60}")
        linie.append(f"#{i} | {w.tytul} ({w.zrodlo}, chunk #{w.nr_chunk}) | score={w.score:.4f}")
        linie.append(f"{'-'*60}")
        preview = w.tekst[:600].replace("\n", " ")
        if len(w.tekst) > 600:
            preview += "..."
        linie.append(preview)
    return "\n".join(linie)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Wyszukiwanie Bibliotheca-RAG")
    ap.add_argument("zapytanie", nargs="+", help="Zapytanie tekstowe")
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--tryb", choices=["hybrid", "fts", "wektor"], default="hybrid")
    ap.add_argument("--baza", default=str(DEFAULT_BAZA))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()
    q = " ".join(args.zapytanie)
    wyniki = szukaj(q, args.topk, args.tryb, Path(args.baza), args.model)
    print(formatuj(wyniki, q))
