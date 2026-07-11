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

# Import odporny na dwa konteksty: (a) pakiet z rootem na ścieżce (testy, `python -m`),
# (b) mcp_server, który wrzuca na sys.path SAM katalog `narzedzia/rag` i robi `from szukaj ...`.
try:
    from narzedzia.rag import katalog
except ImportError:  # pragma: no cover — ścieżka mcp_server / bezpośredni `python szukaj.py`
    import katalog  # type: ignore[no-redef]

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
    korpus: str = "biblioteka"


def _ma_korpus(conn: sqlite3.Connection) -> bool:
    kolumny = {r[1] for r in conn.execute("PRAGMA table_info(fragmenty)").fetchall()}
    return "korpus" in kolumny


def _fts_szukaj(
    conn: sqlite3.Connection, zapytanie: str, topk: int, korpus: str | None = None
) -> list[Wynik]:
    ma_kor = _ma_korpus(conn)
    kol_kor = "f.korpus" if ma_kor else "'biblioteka' AS korpus"
    warunek = ""
    params: list = [zapytanie]
    if korpus and ma_kor:
        warunek = "AND f.korpus = ?"
        params.append(korpus)
    params.append(topk * 3)
    rows = conn.execute(
        f"""
        SELECT f.id, f.zrodlo, f.tytul, f.nr_chunk, f.tekst,
               bm25(fts) AS score, {kol_kor}
        FROM fts
        JOIN fragmenty f ON fts.rowid = f.id
        WHERE fts MATCH ? {warunek}
        ORDER BY score
        LIMIT ?
        """,
        params,
    ).fetchall()
    # bm25() zwraca ujemne wartości — mniejsza = lepsza
    return [Wynik(*r) for r in rows]


def _wektor_szukaj(
    conn: sqlite3.Connection, zapytanie: str, topk: int, model, korpus: str | None = None
) -> list[Wynik]:
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
    # bierzemy z zapasem (korpus filtruje pozniej)
    kandydaci = scored[: topk * 5] if korpus else scored[:topk]
    top_ids = [fid for _, fid in kandydaci]
    if not top_ids:
        return []

    ma_kor = _ma_korpus(conn)
    kol_kor = "korpus" if ma_kor else "'biblioteka' AS korpus"
    placeholders = ",".join("?" * len(top_ids))
    frag_rows = conn.execute(
        f"SELECT id, zrodlo, tytul, nr_chunk, tekst, {kol_kor} "
        f"FROM fragmenty WHERE id IN ({placeholders})",
        top_ids,
    ).fetchall()

    id_to_sim = {fid: sim for sim, fid in kandydaci}
    wyniki = [
        Wynik(r[0], r[1], r[2], r[3], r[4], id_to_sim.get(r[0], 0.0), r[5])
        for r in frag_rows
    ]
    if korpus and ma_kor:
        wyniki = [w for w in wyniki if w.korpus == korpus]
    wyniki.sort(key=lambda x: -x.score)
    return wyniki[:topk]


def szukaj(
    zapytanie: str,
    topk: int = 5,
    tryb: str = "hybrid",
    baza: Path = DEFAULT_BAZA,
    model_name: str = DEFAULT_MODEL,
    cichy: bool = False,
    korpus: str | None = None,
    autor: str | None = None,
    tag: str | None = None,
) -> list[Wynik]:
    """
    autor/tag (OPT-IN, domyślnie None): filtr po katalogu książek (metadane_ksiag.py).
    Bez filtra zachowanie IDENTYCZNE jak dawniej. Z filtrem: nadpobieramy kandydatów
    i zostawiamy tylko książki pasujące metadanymi (autor/tag jako podciąg, insensitive).
    """
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
    if tryb in ("wektor", "hybrid") and (not has_vecs or model is None):
        tryb = "fts"
        if not cichy:
            print("[RAG] Brak wektorów/modelu, używam FTS", file=sys.stderr)

    # Przy aktywnym filtrze katalogowym nadpobieramy — część kandydatów odpadnie po metadanych.
    filtr_aktywny = bool(autor or tag)
    pobierz = max(topk * 20, 100) if filtr_aktywny else topk

    if tryb == "fts":
        wyniki = _fts_szukaj(conn, zapytanie, pobierz, korpus)[:pobierz]
    elif tryb == "wektor":
        wyniki = _wektor_szukaj(conn, zapytanie, pobierz, model, korpus)[:pobierz]
    else:  # hybrid
        fts_wyniki = _fts_szukaj(conn, zapytanie, pobierz, korpus)
        vec_wyniki = _wektor_szukaj(conn, zapytanie, pobierz, model, korpus)
        # połącz po ID, preferuj te które wystąpiły w obu
        seen: dict[int, Wynik] = {}
        bonus_ids = {w.id for w in fts_wyniki} & {w.id for w in vec_wyniki}
        for w in fts_wyniki + vec_wyniki:
            if w.id not in seen:
                seen[w.id] = w
        # bonus dla wyników w obu listach (reranking)
        wyniki = sorted(seen.values(), key=lambda x: (x.id not in bonus_ids, -x.score))[:pobierz]

    conn.close()

    if filtr_aktywny:
        kat = katalog.wczytaj_katalog()
        if not kat:
            # Katalog niedostępny (np. chmura bez `metadane_ksiag`) — NIE udajemy pustych wyników
            # przez predykat odrzucający wszystko (recenzja cubic PR#119). Pomijamy filtr autor/tag
            # i zwracamy trafienia treściowe; użytkownik wie, że filtr był nieaktywny.
            if not cichy:
                print("[RAG] Filtr autor/tag pominięty — brak katalogu książek. Zbuduj na laptopie: "
                      "python -m narzedzia.rag.metadane_ksiag", file=sys.stderr)
        else:
            # Tagi/rok wymagają calibre; na katalogu bez tagów filtr --tag zawsze dałby puste
            # (wygląda na zepsute). Wtedy pomijamy SAM tag, ale filtr autora zostaje aktywny.
            ma_tagi = any(m.get("tagi") for m in kat.values())
            tag_efektywny = tag if ma_tagi else None
            if tag and not ma_tagi and not cichy:
                print("[RAG] Filtr --tag nieaktywny: katalog nie ma tagów. Uruchom na laptopie "
                      "z calibre: python -m narzedzia.rag.metadane_ksiag", file=sys.stderr)
            wyniki = [w for w in wyniki if katalog.pasuje_filtr(w.zrodlo, kat, autor, tag_efektywny)]
    return wyniki[:topk]


def formatuj(wyniki: list[Wynik], zapytanie: str = "") -> str:
    if not wyniki:
        return f"[RAG] Brak wyników dla: {zapytanie!r}"
    kat = katalog.wczytaj_katalog()
    linie = [f"[RAG] Wyniki dla: {zapytanie!r} ({len(wyniki)})\n"]
    for i, w in enumerate(wyniki, 1):
        linie.append(f"{'='*60}")
        meta = katalog.opis_metadanych(w.zrodlo, kat)
        meta = f"  · {meta}" if meta else ""
        linie.append(
            f"#{i} | [{w.korpus}] {w.tytul} ({w.zrodlo}, chunk #{w.nr_chunk}) | score={w.score:.4f}{meta}"
        )
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
    ap.add_argument("--korpus", choices=["biblioteka", "dane", "docs"], default=None,
                    help="ogranicz do korpusu (domyslnie: wszystkie)")
    ap.add_argument("--autor", default=None, help="filtr po autorze z katalogu ksiag (podciag)")
    ap.add_argument("--tag", default=None, help="filtr po tagu z katalogu ksiag (podciag)")
    ap.add_argument("--baza", default=str(DEFAULT_BAZA))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()
    q = " ".join(args.zapytanie)
    wyniki = szukaj(q, args.topk, args.tryb, Path(args.baza), args.model,
                    korpus=args.korpus, autor=args.autor, tag=args.tag)
    print(formatuj(wyniki, q))
