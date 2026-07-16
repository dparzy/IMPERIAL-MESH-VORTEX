"""
Ekstraktor tekstu z formatów biblioteki (epub, pdf, azw3, mobi, djvu, md).
Zwraca czysty tekst podzielony na akapity/strony.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def _epub(path: Path) -> str:
    import ebooklib
    from ebooklib import epub
    from html.parser import HTMLParser

    class _Strip(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts: list[str] = []

        def handle_data(self, data: str):
            self.parts.append(data)

    # ebooklib bywa KRUCHY na POPRAWNYCH epubach — zakłada strukturę, której standard nie wymaga.
    # Realny przypadek (2026-07-16, whitepaper Bitcoina BIB-075): ebooklib 0.20.0 robi
    #   nav_node = html_node.xpath("//nav[@*='toc']")[0]
    # bez zabezpieczenia — epub z nawigacją BEZ elementu oznaczonego 'toc' → IndexError
    # („list index out of range") → ekstrakcja 0 znaków. Plik był w pełni poprawny (36 plików,
    # komplet rozdziałów) — to bug BIBLIOTEKI, nie książki.
    # Fallback na calibre = ten sam wzorzec, którego już używa `_djvu`. Chmura tego nie potrzebuje:
    # laptop konwertuje RAZ, cache jest wersjonowany (patrz docstring konwertera).
    try:
        book = epub.read_epub(str(path), options={"ignore_ncx": True})
        chunks: list[str] = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            p = _Strip()
            p.feed(item.get_content().decode("utf-8", errors="replace"))
            chunks.append(" ".join(p.parts))
        tekst = "\n\n".join(chunks)
    except Exception as e:  # noqa: BLE001 — kruchość ebooklib ≠ zła książka
        print(f"  [WARN] ekstraktor: {path.name} → ebooklib padł ({type(e).__name__}: {e}); "
              "próbuję calibre", file=sys.stderr)
        return _calibre(path)

    # PUSTY wynik BEZ wyjątku też jest porażką (Prawo XV: cicha strata jest gorsza od głośnej) —
    # np. epub, w którym ebooklib nie rozpoznał żadnego ITEM_DOCUMENT. Nie utrwalamy pustki.
    if not tekst.strip():
        print(f"  [WARN] ekstraktor: {path.name} → ebooklib dał 0 znaków; próbuję calibre",
              file=sys.stderr)
        return _calibre(path)
    return tekst


def _pdf(path: Path) -> str:
    import fitz  # pymupdf
    doc = fitz.open(str(path))
    pages = [doc[i].get_text() for i in range(len(doc))]
    doc.close()
    return "\n\n".join(pages)


def _md(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _csv(path: Path) -> str:
    """CSV → tekst: nagłówek + wiersze jako 'kol: wartość' (kontekst dla wyszukiwania)."""
    import csv as _csvmod
    linie: list[str] = []
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        reader = _csvmod.reader(f)
        try:
            naglowek = next(reader)
        except StopIteration:
            return ""
        linie.append("Kolumny: " + ", ".join(naglowek))
        for wiersz in reader:
            pary = [f"{k}: {v}" for k, v in zip(naglowek, wiersz) if v.strip()]
            if pary:
                linie.append(" | ".join(pary))
    return "\n".join(linie)


def _json(path: Path) -> str:
    """JSON → tekst: spłaszczona reprezentacja klucz=wartość (rekurencyjnie)."""
    import json as _jsonmod

    def splaszcz(obj, prefix=""):
        czesci: list[str] = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                czesci += splaszcz(v, f"{prefix}{k}.")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                czesci += splaszcz(v, f"{prefix}{i}.")
        else:
            czesci.append(f"{prefix.rstrip('.')}: {obj}")
        return czesci

    try:
        dane = _jsonmod.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return ""
    return "\n".join(splaszcz(dane))


def _strip_html(html: str) -> str:
    """Usuwa tagi HTML, zwraca czysty tekst (dzieli akapity)."""
    from html.parser import HTMLParser

    class _Strip(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts: list[str] = []

        def handle_data(self, data: str):
            self.parts.append(data)

    p = _Strip()
    p.feed(html)
    return " ".join(p.parts)


def _mobi(path: Path) -> str:
    """azw3/mobi → tekst przez pakiet `mobi` (rozpakowuje do epub/html). Fallback: calibre."""
    try:
        import mobi as _mobimod
    except ImportError:
        return _calibre(path)
    tempdir = None
    try:
        tempdir, fp = _mobimod.extract(str(path))
        fp_path = Path(fp)
        suf = fp_path.suffix.lower()
        if suf == ".epub":
            return _epub(fp_path)
        if suf in (".html", ".htm", ".xhtml"):
            return _strip_html(fp_path.read_text(encoding="utf-8", errors="replace"))
        # nieznany format pojemnika — zbierz wszystkie html z tempdira
        teksty: list[str] = []
        for h in sorted(Path(tempdir).rglob("*.htm*")):
            teksty.append(_strip_html(h.read_text(encoding="utf-8", errors="replace")))
        if teksty:
            return "\n\n".join(teksty)
        return _calibre(path)
    except Exception:
        return _calibre(path)
    finally:
        if tempdir:
            import shutil

            shutil.rmtree(tempdir, ignore_errors=True)


# Timeout konwersji: wielkie książki (Shreve, Sutton-Barto, Kaufman ~2 mln znaków) nie mieszczą
# się w 60 s. 300 s daje margines; koszt płacony raz (potem cache — patrz konwerter.py).
_TIMEOUT_KONWERSJI = 300


def _calibre(path: Path) -> str:
    """Fallback: ebook-convert → txt (wymaga calibre). Uniwersalny konwerter dla djvu/azw3/mobi."""
    # Calibre wybiera format WYJŚCIA po rozszerzeniu pliku docelowego — MUSI być `.txt`
    # (poprzednie `.txt.tmp` → `ValueError: No plugin to handle output format: tmp`, ciche
    # gubienie djvu, Prawo XV). Scratch w KATALOGU TYMCZASOWYM z UNIKALNĄ nazwą (recenzja cubic
    # PR#119): dwie równoległe konwersje tej samej książki nie nadpisują sobie wyjścia, a plik
    # scratcha NIGDY nie koliduje z plikiem biblioteki (dawne `<stem>.calibre-tmp.txt` obok źródła
    # mogło skasować realny plik użytkownika o tej nazwie). Sprzątamy dokładnie ten jeden plik.
    fd, tmp_name = tempfile.mkstemp(suffix=".txt", prefix="calibre_")
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        subprocess.run(
            ["ebook-convert", str(path), str(tmp)],
            capture_output=True,
            timeout=_TIMEOUT_KONWERSJI,
            check=True,
        )
        return tmp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    finally:
        tmp.unlink(missing_ok=True)


def _djvu(path: Path) -> str:
    try:
        r = subprocess.run(
            ["djvutxt", str(path)],
            capture_output=True,
            timeout=_TIMEOUT_KONWERSJI,
        )
        # Sprawdzamy kod wyjścia (recenzja): djvutxt na uszkodzonym pliku potrafi wypluć
        # CZĘŚCIOWY stdout i paść — bez tej kontroli ułamek trafiał do cache jako „prawda".
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode("utf-8", errors="replace")
        return _calibre(path)
    except Exception:
        return _calibre(path)


def ekstrahuj(path: Path) -> str:
    """Zwraca czysty tekst z pliku. Pusty string gdy nie obsługiwany."""
    suf = path.suffix.lower()
    try:
        if suf == ".epub":
            return _epub(path)
        if suf == ".pdf":
            return _pdf(path)
        if suf == ".md":
            return _md(path)
        if suf == ".txt":
            return _txt(path)
        if suf == ".csv":
            return _csv(path)
        if suf == ".json":
            return _json(path)
        if suf in (".azw3", ".mobi"):
            return _mobi(path)
        if suf == ".djvu":
            return _djvu(path)
    except Exception as e:
        print(f"  [WARN] ekstraktor: {path.name} → {e}")
    return ""


def podziel_na_chunki(tekst: str, max_slow: int = 400, overlap: int = 50) -> list[str]:
    """Dzieli tekst na chunki ~max_slow słów z nakładaniem overlap słów."""
    overlap = min(overlap, max_slow - 1)  # gwarancja postępu
    krok = max(1, max_slow - overlap)
    slowa = tekst.split()
    if not slowa:
        return []
    chunki: list[str] = []
    i = 0
    while i < len(slowa):
        chunk = slowa[i : i + max_slow]
        chunki.append(" ".join(chunk))
        i += krok
    return [c for c in chunki if len(c.split()) >= 20]


def wyczysc(tekst: str) -> str:
    """Usuwa powtarzające się spacje/newline."""
    tekst = re.sub(r"[ \t]{2,}", " ", tekst)
    tekst = re.sub(r"\n{3,}", "\n\n", tekst)
    return tekst.strip()
