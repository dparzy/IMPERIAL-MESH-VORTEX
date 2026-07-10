"""
Katalog książek jako SOCZEWKA nad RAG — wzbogaca wyniki wyszukiwania o metadane.

Łączy `bibliotheca_ulpia/dane/katalog_ksiag.json` (autor/tytuł/tagi/rok/ISBN — patrz
`metadane_ksiag.py`) z wynikami RAG po NAZWIE PLIKU: RAG zapisuje `zrodlo = p.name`
(np. „BIB-007_Lopez-de-Prado_...epub"), a katalog kluczuje po tym samym `plik`.

Dwa zastosowania w `szukaj.py`:
  1. WZBOGACENIE — do nagłówka wyniku dopisujemy autora/rok/tagi (widać, z jakiej książki).
  2. FILTR — `szukaj(..., autor=..., tag=...)` ogranicza wyniki do książek pasujących
     metadanymi (dziś RAG umie tylko treść; to nowa zdolność — filtr po katalogu).

GRACEFUL (Prawo XV): brak pliku katalogu → {} (wzbogacenie puste, filtr nieaktywny nic nie
psuje). Źródła spoza katalogu (dokumenty .md) po prostu nie mają metadanych — to nie błąd.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
KATALOG_PLIK = ROOT / "bibliotheca_ulpia" / "dane" / "katalog_ksiag.json"


def wczytaj_katalog(plik: Path | None = None) -> dict[str, dict]:
    """Katalog jako mapa `nazwa_pliku → metadane`. {} gdy brak/uszkodzony (graceful).

    Ścieżka rozwiązywana w czasie WYWOŁANIA (nie w domyślnym argumencie) — dzięki temu
    podmiana `katalog.KATALOG_PLIK` (np. w testach) działa też dla wywołań bez argumentu.
    """
    plik = plik or KATALOG_PLIK
    if not plik.exists():
        return {}
    try:
        data = json.loads(plik.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return {w["plik"]: w for w in data.get("ksiegi", []) if w.get("plik")}


def opis_metadanych(zrodlo: str, katalog: dict[str, dict]) -> str:
    """
    Zwięzły opis metadanych źródła do nagłówka wyniku ('' gdy źródła nie ma w katalogu —
    np. dokument .md). Format: „Autor · 2018 · tagi: Finance, ML".
    """
    m = katalog.get(zrodlo)
    if not m:
        return ""
    czesci: list[str] = []
    if m.get("autor"):
        czesci.append(str(m["autor"]))
    if m.get("wydano"):
        czesci.append(str(m["wydano"])[:4])          # sam rok z daty ISO
    if m.get("tagi"):
        czesci.append(f"tagi: {m['tagi']}")
    return " · ".join(czesci)


def pasuje_filtr(zrodlo: str, katalog: dict[str, dict],
                 autor: str | None = None, tag: str | None = None) -> bool:
    """
    Czy źródło pasuje do filtra autor/tag (podciąg, case-insensitive)?
    Brak filtra → True (przepuszcza wszystko). Filtr aktywny + źródło spoza katalogu
    (np. dokument) → False: filtr dotyczy KSIĄŻEK, więc dokumenty odpadają świadomie.
    """
    if not autor and not tag:
        return True
    m = katalog.get(zrodlo)
    if not m:
        return False
    if autor and autor.lower() not in str(m.get("autor", "")).lower():
        return False
    if tag and tag.lower() not in str(m.get("tagi", "")).lower():
        return False
    return True
