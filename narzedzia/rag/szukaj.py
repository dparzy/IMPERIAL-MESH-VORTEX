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
import re
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


_RE_SLOWO_FTS = re.compile(r"[0-9A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+")

# SŁOWA PUSTE — odsiewane PRZED złożeniem zapytania OR.
# Powód ZMIERZONY (QUAESITOR, 30 pytań known-item, 2026-07-30), nie estetyczny:
#     OR ze słowami pustymi:  RAZEM @5 66,7% | OPISOWE @5 33,3% | 323 ms
#     OR bez słów pustych:    RAZEM @5 80,0% | OPISOWE @5 60,0% | 143 ms
# Zysk +26,7 pp na pytaniach OPISOWYCH i 2,3× szybciej. Mechanizm jest zrozumiały:
# `how`, `to`, `the`, `me` występują w KAŻDYM fragmencie korpusu, więc w składni OR
# szukają wszędzie i rozcieńczają ranking BM25 — pytanie o adverse selection zwracało
# Schwagera i Thalera zamiast mikrostruktury rynku.
# UCZCIWIE: na @10 wariant bez słów pustych wypadł o 3,3 pp GORZEJ (jedno pytanie
# z trzydziestu) — przy tej próbce to szum. Rozstrzyga @5, bo tyle bierze `mcp_server`.
# Do potwierdzenia na dużym zbiorze z indeksów książek (pozycja A10 w PLAN WACHT).
# Zbiór celowo MAŁY i angielsko-polski: usuwamy tylko słowa bez treści wyszukiwawczej,
# nigdy terminów domenowych (`volume`, `risk`, `trend` zostają).
_SLOWA_PUSTE = frozenset("""
a an the and or but if then than that this these those of in on at to for from by with
without about into over under again further is are was were be been being do does did
doing have has had having i me my we our us you your he she it its they them their
what which who whom whose how when where why all any both each few more most other
some such no nor not only own same so too very can will just should now as
i oraz albo lub ale jesli to ze ta te ten tych tym o w na do dla od przez z ze bez
jest sa byl byla bylo byc czy jak kiedy gdzie dlaczego co ktory ktora ktore kto
nie tak juz tez tylko bardzo moze mozna sie
""".split())


def sanityzuj_fts(zapytanie: str, skladnia: str = "or") -> str:
    """JEDNO ŹRÓDŁO PRAWDY dla składni zapytania FTS5. Zwraca bezpieczne zapytanie.

    ────────────────────────────────────────────────────────────────────────────
    DLACZEGO TU, A NIE U WOŁAJĄCYCH (naprawa u źródła, 2026-07-30)

    Sanityzacja istniała w Imperium w TRZECH kopiach — `bibliotekarz._fts_bezpieczne`
    (stosowana), `quaesitor._fts_or` (kopia) — i BRAKOWAŁO jej w `mcp_server`, czyli
    na ścieżce, którą Architekt czyta bibliotekę. Każdy wołał ją u siebie, więc jeden
    wołający został pominięty. To ta sama klasa, którą naprawialiśmy przy
    `normalizuj_interwal`: łatanie w miejscu wywołania zawsze zostawia następnego.

    ZMIERZONE NA 30 PYTANIACH known-item (QUAESITOR, pierwszy bieg 2026-07-30):
        składnia AND (surowy MATCH, ścieżka MCP):  recall@5 16,7% | opisowe 0,0%
        składnia OR  (ścieżka HYGINUSA):           recall@5 66,7% | opisowe 33,3%
    Czterokrotna różnica, a na pytaniach OPISOWYCH surowy AND daje ZERO trafień na 15.
    Koszt: 434 ms vs 25 ms na zapytanie — nieistotny przy szukaniu w bibliotece.

    Domyślny MATCH FTS5 łączy słowa niejawnym AND, więc długie pytanie wymaga
    WSZYSTKICH słów w jednym fragmencie. OR poszerza recall, a BM25 i tak wypycha
    na górę fragmenty zawierające WIĘCEJ terminów — ranking robi robotę, którą
    twardy AND robił przez odrzucanie.

    Sanityzacja naprawia też KLASĘ AWARII, nie tylko trafność: surowy tekst
    z myślnikiem wywala MATCH (`no such column: labeling` — realnie złapane
    w pierwszym biegu QUAESITORA), a u HYGINUSA udokumentowane jako „temat cicho ginął".

    `skladnia="surowa"` zostawia zapytanie NIETKNIĘTE — dla wołających, którzy
    świadomie budują składnię FTS (prefiksy, frazy w cudzysłowach, NEAR).
    """
    if skladnia == "surowa":
        return zapytanie
    slowa = _RE_SLOWO_FTS.findall(zapytanie or "")
    if not slowa:
        return zapytanie
    # Odsiewamy słowa puste, ALE nigdy nie zwracamy pustki: pytanie złożone wyłącznie
    # z nich (np. „how to do it") lepiej wyszukać dosłownie niż nie wyszukać wcale.
    tresciwe = [w for w in slowa if w.lower() not in _SLOWA_PUSTE]
    uzyte = tresciwe or slowa
    return (" OR " if skladnia == "or" else " ").join(uzyte)


def _topk_cli(s: str) -> int:
    """`--topk` z walidacją zakresu 1..100 (Reguła Test-Granic).

    Gołe `type=int` przyjmowało 0 (zapytanie zwracające nic bez słowa wyjaśnienia)
    i wartości absurdalnie duże (nadpobieranie ×20 przy filtrze katalogowym robiło
    z tego pełny skan korpusu). Klasa z Księgi Wad: „argument sterujący kosztem
    bez walidacji zakresu" — złapana skanem 2026-07-30 na tej właśnie linii.
    """
    try:
        v = int(s)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"topk musi być liczbą całkowitą: {s!r}") from e
    if not 1 <= v <= 100:
        raise argparse.ArgumentTypeError(f"topk poza zakresem 1..100: {v}")
    return v


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
    skladnia: str = "or",
) -> list[Wynik]:
    """
    autor/tag (OPT-IN, domyślnie None): filtr po katalogu książek (metadane_ksiag.py).
    Bez filtra zachowanie IDENTYCZNE jak dawniej. Z filtrem: nadpobieramy kandydatów
    i zostawiamy tylko książki pasujące metadanymi (autor/tag jako podciąg, insensitive).

    skladnia (domyślnie "or"): sanityzacja zapytania FTS5 w JEDNYM miejscu —
    patrz `sanityzuj_fts`. Domyślne "or" jest wyborem ZMIERZONYM, nie wygodą:
    recall@5 66,7% vs 16,7% dla surowego AND, a na pytaniach opisowych 33,3% vs 0,0%
    (QUAESITOR, 30 pytań known-item, 2026-07-30). Wołający, którzy sami budują
    składnię FTS (frazy, prefiksy, NEAR), przekazują "surowa".
    """
    zapytanie = sanityzuj_fts(zapytanie, skladnia)
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
    ap.add_argument("--topk", type=_topk_cli, default=5,
                    help="ile wyników (1..100)")
    ap.add_argument("--tryb", choices=["hybrid", "fts", "wektor"], default="hybrid")
    # Parametr istniał w `szukaj()` i nie był dostępny z CLI — zdolność niepodpięta
    # (Prawo XV). „surowa" potrzebna do porównań i do świadomej składni FTS.
    ap.add_argument("--skladnia", choices=["or", "and", "surowa"], default="or",
                    help="składnia zapytania FTS (domyślnie or — zmierzone recall@5 80%% vs 17%%)")
    ap.add_argument("--korpus", choices=["biblioteka", "dane", "docs"], default=None,
                    help="ogranicz do korpusu (domyslnie: wszystkie)")
    ap.add_argument("--autor", default=None, help="filtr po autorze z katalogu ksiag (podciag)")
    ap.add_argument("--tag", default=None, help="filtr po tagu z katalogu ksiag (podciag)")
    ap.add_argument("--baza", default=str(DEFAULT_BAZA))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()
    q = " ".join(args.zapytanie)
    wyniki = szukaj(q, args.topk, args.tryb, Path(args.baza), args.model,
                    korpus=args.korpus, autor=args.autor, tag=args.tag,
                    skladnia=args.skladnia)
    print(formatuj(wyniki, q))
