"""
Konwerter/cache tekstu książek — auto-convert problematycznych formatów, raz, z zapisem.

PROBLEM (Prawo XV): formaty jak **djvu** wymagają zewnętrznego narzędzia (calibre `ebook-convert`
lub `djvutxt`), którego NIE MA w chmurze — więc Shreve/Sutton-Barto/Aronson są tam nieczytelne.
Wielkie książki konwertują się wolno; robienie tego przy każdej ekstrakcji marnuje czas.

ROZWIĄZANIE (Prawo XVI — NIE nowy konwerter, lecz CACHE nad istniejącym): `ekstraktor.ekstrahuj`
już używa calibre jako fallbacku. Ta warstwa dokłada tylko brakujący element — **cache tekstu**
kluczowany HASZEM TREŚCI pliku:
  1. Cache trafiony → zwróć tekst natychmiast (działa też BEZ calibre — kluczowe dla chmury).
  2. Cache pusty → `ekstraktor.ekstrahuj` (konwertuje via calibre gdy trzeba) → zapisz do cache.

SPÓJNOŚĆ MIĘDZY MASZYNAMI (Prawo XVII): hasz treści = ten sam plik → ten sam cache na każdej
maszynie. Laptop (z calibre) konwertuje książki RAZ; cały cache jest WERSJONOWANY (decyzja Cezara
2026-07-11), więc **chmura czyta tekst bez calibre i bez binariów** — binaria książek żyją tylko
lokalnie, poza gitem (ryzyko praw autorskich). To trwałe odblokowanie CAŁEJ biblioteki, nie tylko djvu.

GRACEFUL (Prawo XV): bez calibre i bez cache → zwraca "" (abstynencja), nie wysypuje pipeline.

Użycie:
  from narzedzia.rag.konwerter import ekstrahuj_z_cache
  tekst = ekstrahuj_z_cache(Path("bibliotheca_ulpia/BIB-065_...djvu"))
  # CLI: python -m narzedzia.rag.konwerter --buduj   # prekonwertuj wszystkie książki do cache
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / "bibliotheca_ulpia" / "dane" / "tekst_cache"
BIBLIOTEKA = ROOT / "bibliotheca_ulpia"

# Poniżej tylu znaków traktujemy ekstrakcję jako NIEUDANĄ (nie cache'ujemy pustych/błędnych) —
# chroni przed utrwaleniem "" gdy calibre chwilowo niedostępny.
MIN_ZNAKOW_CACHE = 200
FORMATY_KSIAG = {".epub", ".pdf", ".azw3", ".mobi", ".djvu"}


def _klucz(path: Path) -> str:
    """Hasz treści pliku (16 znaków sha1) — stabilny między maszynami."""
    return hashlib.sha1(path.read_bytes()).hexdigest()[:16]


# Windows: MAX_PATH = 260 znaków. Ścieżka cache to CACHE_DIR + stem + "__" + hasz16 + ".txt",
# a przy zapisie atomowym dochodzi jeszcze ".tmp" — pod ten NAJDŁUŻSZY wariant liczymy budżet.
# Zapas 1 znak na bezpieczeństwo. (Realny przypadek 2026-07-16: książka wrzucona bez zmiany nazwy
# — „Market Microstructure Theory -- Maureen O'Hara, Maureen O'Hara -- 1_ publ_ in paperback…" —
# dała ścieżkę 282 znaków i wywaliła CAŁY pipeline.)
LIMIT_SCIEZKI = 259


def sciezka_cache(path: Path) -> Path:
    """
    `<stem>__<hasz>.txt` — czytelna nazwa + hasz gwarantujący zgodność treści.

    Stem SKRACAMY **tylko gdy** pełna ścieżka nie mieści się w limicie systemu (Windows MAX_PATH).
    Warunkowo, nie zawsze — bo bezwarunkowe skracanie zmieniłoby nazwy WSZYSTKICH istniejących
    plików cache, osierociło je i wymusiło rekonwersję całej biblioteki (71 książek przez calibre).
    Skrócenie jest bezpieczne: o zgodności treści decyduje HASZ, nie nazwa; stem jest tylko
    dla czytelności człowieka.
    """
    h = _klucz(path)
    kandydat = CACHE_DIR / f"{path.stem}__{h}.txt"
    # Mierzymy wariant .tmp (najdłuższy): to on wywala się przy zapisie atomowym.
    nadmiar = len(str(kandydat)) + len(".tmp") - LIMIT_SCIEZKI
    if nadmiar > 0:
        # Zostaw min. 8 znaków stemu — nazwa ma nadal coś znaczyć dla człowieka.
        stem = path.stem[:max(8, len(path.stem) - nadmiar)]
        kandydat = CACHE_DIR / f"{stem}__{h}.txt"
    return kandydat


def ekstrahuj_z_cache(path: Path, min_znakow: int = MIN_ZNAKOW_CACHE) -> str:
    """
    Tekst książki z CACHE (jeśli jest) lub przez `ekstraktor.ekstrahuj` (z zapisem do cache).
    Cache trafiony działa BEZ calibre — dzięki temu chmura czyta djvu prekonwertowane na laptopie.
    Pustej/nieudanej ekstrakcji (< min_znakow) NIE cache'ujemy (Prawo I — nie utrwalamy braku).
    """
    cache = sciezka_cache(path)
    if cache.exists():
        return cache.read_text(encoding="utf-8", errors="replace")

    # Import lokalny: ekstraktor działa też uruchamiany bezpośrednio z narzedzia/rag.
    try:
        from narzedzia.rag.ekstraktor import ekstrahuj
    except ImportError:  # pragma: no cover — kontekst z narzedzia/rag na sys.path
        from ekstraktor import ekstrahuj  # type: ignore[no-redef]

    tekst = ekstrahuj(path)
    if len(tekst) >= min_znakow:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # Zapis ATOMOWY (recenzja): przerwanie w środku write_text zostawiało częściowy plik,
        # który przy następnym trafieniu byłby serwowany jako pełny tekst (i, po zacommitowaniu,
        # truł chmurę uciętą książką). tmp → os.replace jest atomowe na jednym systemie plików.
        tmp = cache.with_suffix(".txt.tmp")
        tmp.write_text(tekst, encoding="utf-8")
        os.replace(tmp, cache)
    return tekst


def buduj_cache(katalog: Path = BIBLIOTEKA) -> dict:
    """
    Prekonwertuje WSZYSTKIE książki do cache (uruchom na laptopie z calibre). Pasek postępu
    na stderr (Prawo XXIV). Zwraca {plik: liczba_znaków}. Pomija już scache'owane (idempotentne).

    GRACEFUL PER KSIĄŻKA (Prawo XV — naprawione 2026-07-16): błąd JEDNEJ książki nie może zabić
    biegu po pozostałych. Wcześniej wyjątek leciał w górę i przerywał cały pipeline — realnie
    zdarzyło się: jedna nazwa 190 znaków (książka wrzucona bez zmiany nazwy) → ścieżka 282 znaki
    → FileNotFoundError na 71/71 → padło `przygotuj_biblioteke` mimo 70 poprawnie przerobionych.
    Moduł obiecywał w docstringu „nie wysypuje pipeline" — i tego nie dotrzymywał.
    """
    pliki = sorted(p for p in katalog.iterdir()
                   if p.is_file() and p.suffix.lower() in FORMATY_KSIAG)
    wynik: dict = {}
    bledy: dict = {}
    for i, p in enumerate(pliki, 1):
        stan = "cache" if sciezka_cache(p).exists() else "konwersja"
        print(f"\r  [konwerter] {i}/{len(pliki)} [{stan}] {p.name[:44]:44}",
              end="", file=sys.stderr, flush=True)
        try:
            wynik[p.name] = len(ekstrahuj_z_cache(p))
        except Exception as e:  # noqa: BLE001 — jedna zła książka ≠ koniec biegu (Prawo XV)
            wynik[p.name] = 0
            bledy[p.name] = f"{type(e).__name__}: {e}"
    print("", file=sys.stderr)
    puste = [k for k, v in wynik.items() if v < MIN_ZNAKOW_CACHE]
    print(f"  [konwerter] scache'owano {len(wynik) - len(puste)}/{len(wynik)} "
          f"| nieudane (brak narzędzia?): {puste or 'brak'}", file=sys.stderr)
    if bledy:
        # Głośno, ale bez zabijania biegu — Cezar ma WIEDZIEĆ, że coś nie weszło do RAG.
        print(f"  [konwerter] 🚨 BŁĘDY ({len(bledy)}) — te książki NIE weszły do RAG:",
              file=sys.stderr)
        for nazwa, blad in bledy.items():
            print(f"      • {nazwa}: {blad}", file=sys.stderr)
    return wynik


if __name__ == "__main__":
    if "--buduj" in sys.argv:
        buduj_cache()
    else:
        print("Użycie: python -m narzedzia.rag.konwerter --buduj  "
              "(prekonwertuj książki do cache; na laptopie z calibre)", file=sys.stderr)
