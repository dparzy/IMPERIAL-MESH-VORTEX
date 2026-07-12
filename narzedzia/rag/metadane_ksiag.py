"""
Metadane Ksiąg (Bibliotheca Ulpia) — strukturalny katalog książek dla RAG i katalogu.

LUKA (Prawo XVI — zmierzona): RAG indeksuje TREŚĆ (FTS), ale metadane książki to dziś
wyłącznie `tytul` sparsowany z nazwy pliku (BIB-NNN_Autor_Tytul). Brak autora, tagów,
języka, roku, ISBN, wydawcy, serii — czyli tego, co pozwala FILTROWAĆ i KATALOGOWAĆ.

ROZWIĄZANIE (calibre jako BACKEND, nie MCP — decyzja Cezara 2026-07-10): calibre
`ebook-meta` wyciąga bogate metadane z każdego formatu (epub/azw3/mobi/pdf/djvu). Karmi
to nasz istniejący RAG i katalog Bibliotheki — bez dodawania redundantnego serwera MCP
(ZASADA MCP: MCP wchodzi tylko gdy dokłada NOWĄ zdolność; własny RAG już szuka w treści).

DWA POZIOMY (graceful degradation — jak abstynencja neuronów, Prawo XV):
  1. ZAWSZE: parsowanie nazwy pliku `BIB-NNN_Autor_Tytul.ext` → {bib, autor, tytul, format}.
  2. GDY calibre obecny: `ebook-meta` dokłada tagi/język/rok/ISBN/wydawcę/serię.
Bez calibre katalog nadal powstaje (uboższy) — nie blokujemy się na braku narzędzia.

Wynik: `bibliotheca_ulpia/dane/katalog_ksiag.json` — lista wpisów, wersjonowana (mały JSON).

Użycie:
  python -m narzedzia.rag.metadane_ksiag            # zbuduj/odśwież katalog
  python -m narzedzia.rag.metadane_ksiag --podglad  # wypisz bez zapisu
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
BIBLIOTEKA_DIR = ROOT / "bibliotheca_ulpia"
KATALOG_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "katalog_ksiag.json"

FORMATY_KSIAG = {".epub", ".pdf", ".azw3", ".mobi", ".djvu"}

# Markery „brak danych" z ebook-meta (calibre) — po angielsku i po polsku (locale!).
# djvu bez osadzonych metadanych: calibre zwraca Author="Nieznany" i Title=echo nazwy
# pliku. Bez tego sita autor='Nieznany' NADPISYWAŁ dobrego autora z nazwy (Prawo XV:
# filtr autor= nie łapał Shreve/Aronson/Kissell). Patrz test_parser_pomija_nieznany.
_WARTOSCI_PUSTE = {"unknown", "nieznany", "nieznane", "nieznana", "unknown author"}

# Mapa etykiet `ebook-meta` → nasze klucze. `ebook-meta` drukuje linie „Klucz : Wartość".
_ETYKIETY = {
    "Title": "tytul",
    "Author(s)": "autor",
    "Tags": "tagi",
    "Languages": "jezyk",
    "Published": "wydano",
    "Publisher": "wydawca",
    "Series": "seria",
    "Identifiers": "identyfikatory",
}


def parsuj_nazwe(nazwa: str) -> dict:
    """
    Fallback bez calibre: `BIB-NNN_Autor_Tytul-z-myslnikami.ext` → strukturalny wpis.
    Zawsze zwraca komplet kluczy (puste gdy nie dało się sparsować) — stabilny kontrakt.
    """
    stem = Path(nazwa).stem
    fmt = Path(nazwa).suffix.lower().lstrip(".")
    m = re.match(r"^(BIB-\d+)_([^_]+)_(.+)$", stem)
    if not m:
        return {"bib": "", "autor": "", "tytul": stem.replace("-", " ").strip(),
                "format": fmt, "plik": nazwa}
    bib, autor, tytul = m.group(1), m.group(2), m.group(3)
    return {
        "bib": bib,
        "autor": autor.replace("-", " ").strip(),
        "tytul": tytul.replace("-", " ").strip(),
        "format": fmt,
        "plik": nazwa,
    }


def _calibre_dostepny() -> bool:
    """Czy `ebook-meta` (calibre) jest w PATH?"""
    try:
        subprocess.run(["ebook-meta", "--version"], capture_output=True, timeout=10, check=True)
        return True
    except Exception:
        return False


def parsuj_wyjscie_ebook_meta(stdout: str) -> dict:
    """
    Czysty parser wyjścia `ebook-meta` (testowalny bez calibre). Linie „Etykieta : wartość"
    → nasze klucze wg _ETYKIETY. Pomija puste i „Unknown". Wartość może mieć „ : " w środku
    (np. podtytuł) — partition po PIERWSZYM separatorze zachowuje resztę.
    """
    wynik: dict = {}
    for linia in stdout.splitlines():
        if " : " not in linia:
            continue
        etykieta, _, wartosc = linia.partition(" : ")
        klucz = _ETYKIETY.get(etykieta.strip())
        wartosc = wartosc.strip()
        if klucz and wartosc and wartosc.lower() not in _WARTOSCI_PUSTE:
            wynik[klucz] = wartosc
    return wynik


def _tytul_echo_nazwy(tytul: str) -> bool:
    """
    Czy `tytul` z calibre to tylko ECHO nazwy pliku (djvu bez metadanych → Title=
    "BIB-022 Kissell ..."). Realny tytuł książki nigdy nie zaczyna się od naszego
    prefiksu katalogowego BIB-NNN. Chroni przed nadpisaniem dobrego tytułu z nazwy.
    """
    return bool(re.match(r"^BIB-\d", tytul.strip(), re.IGNORECASE))


def metadane_calibre(path: Path) -> dict:
    """Bogate metadane z `ebook-meta`. Zwraca {} gdy calibre nieobecny lub błąd (abstynencja)."""
    try:
        r = subprocess.run(["ebook-meta", str(path)], capture_output=True, timeout=60, check=True)
    except Exception:
        return {}
    return parsuj_wyjscie_ebook_meta(r.stdout.decode("utf-8", errors="replace"))


def zbuduj_katalog(katalog_dir: Path = BIBLIOTEKA_DIR, podglad: bool = False) -> list[dict]:
    """
    Buduje katalog wszystkich BIB-* w bibliotece. Filename-fallback zawsze; calibre wzbogaca.
    Pasek postępu (Prawo XXIV) na stderr — 69 książek to nie jest chwila.
    """
    pliki = sorted(p for p in katalog_dir.iterdir()
                   if p.is_file() and p.suffix.lower() in FORMATY_KSIAG)
    calibre = _calibre_dostepny()
    print(f"  [metadane] {len(pliki)} książek | calibre: {'JEST' if calibre else 'brak (fallback nazw)'}",
          file=sys.stderr)

    katalog: list[dict] = []
    for i, p in enumerate(pliki, 1):
        wpis = parsuj_nazwe(p.name)
        if calibre:
            bogate = metadane_calibre(p)
            # Nazwa pliku (BIB-NNN_Autor_Tytul) jest AUTORYTATYWNA dla autora i tytułu —
            # odrzucamy echo nazwy w tytule z calibre (djvu). Autor='Nieznany' już odsiany
            # w parserze. Pozostałe pola (tagi/jezyk/rok/wydawca/seria) calibre wzbogaca.
            if _tytul_echo_nazwy(bogate.get("tytul", "")):
                bogate.pop("tytul", None)
            wpis.update({k: v for k, v in bogate.items() if v})
        katalog.append(wpis)
        print(f"\r  [metadane] {i}/{len(pliki)} {p.name[:48]:48}", end="", file=sys.stderr, flush=True)
    print("", file=sys.stderr)

    katalog.sort(key=lambda w: w.get("bib", ""))
    if not podglad:
        KATALOG_PLIK.parent.mkdir(parents=True, exist_ok=True)
        KATALOG_PLIK.write_text(
            json.dumps({"n": len(katalog), "calibre": calibre, "ksiegi": katalog},
                       ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  [metadane] zapisano {KATALOG_PLIK.relative_to(ROOT)} ({len(katalog)} wpisów)",
              file=sys.stderr)
    return katalog


if __name__ == "__main__":
    podglad = "--podglad" in sys.argv
    kat = zbuduj_katalog(podglad=podglad)
    if podglad:
        for w in kat:
            extra = f" · tagi: {w['tagi']}" if w.get("tagi") else ""
            print(f"  {w.get('bib',''):8} {w.get('autor','?'):22} — {w.get('tytul','')[:44]}{extra}")
