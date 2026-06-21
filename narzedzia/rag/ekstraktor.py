"""
Ekstraktor tekstu z formatów biblioteki (epub, pdf, azw3, mobi, djvu, md).
Zwraca czysty tekst podzielony na akapity/strony.
"""
from __future__ import annotations
import re
import subprocess
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

    book = epub.read_epub(str(path), options={"ignore_ncx": True})
    chunks: list[str] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        p = _Strip()
        p.feed(item.get_content().decode("utf-8", errors="replace"))
        chunks.append(" ".join(p.parts))
    return "\n\n".join(chunks)


def _pdf(path: Path) -> str:
    import fitz  # pymupdf
    doc = fitz.open(str(path))
    pages = [doc[i].get_text() for i in range(len(doc))]
    doc.close()
    return "\n\n".join(pages)


def _md(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _calibre(path: Path) -> str:
    """Fallback: ebook-convert → txt (wymaga calibre)."""
    tmp = path.with_suffix(".txt.tmp")
    try:
        subprocess.run(
            ["ebook-convert", str(path), str(tmp)],
            capture_output=True,
            timeout=60,
            check=True,
        )
        text = tmp.read_text(encoding="utf-8", errors="replace")
        tmp.unlink(missing_ok=True)
        return text
    except Exception:
        tmp.unlink(missing_ok=True)
        return ""


def _djvu(path: Path) -> str:
    try:
        r = subprocess.run(
            ["djvutxt", str(path)],
            capture_output=True,
            timeout=60,
        )
        return r.stdout.decode("utf-8", errors="replace")
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
        if suf in (".md", ".txt"):
            return _md(path)
        if suf in (".azw3", ".mobi"):
            return _calibre(path)
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
