"""
Przygotuj Bibliotekę LOKALNIE — jedna komenda, ZERO tokenów Claude.

FILOZOFIA OSZCZĘDNOŚCI TOKENÓW (lekcja: świeży start > wznawianie, SCIAGA §2c):
całą CIĘŻKĄ pracę z książkami robimy LOKALNIE narzędziami deterministycznymi (0 tokenów LLM),
a Claude potem odpytuje RAG chirurgicznie — płaci tylko za zwrócone fragmenty, nie za czytanie
całych książek. Ten skrypt spina trzy kroki, które wcześniej trzeba było odpalać osobno:

  1. KONWERSJA + CACHE (`konwerter --buduj`) — djvu/azw3/mobi/pdf/epub → tekst w cache
     (calibre/djvutxt; 0 tokenów). Trafienie cache działa potem BEZ narzędzia.
  2. INDEKS RAG (`indeksuj --korpus biblioteka`) — tekst → SQLite FTS/wektory (0 tokenów).
  3. KATALOG METADANYCH (`metadane_ksiag`) — autor/tytuł/tagi (0 tokenów).

Po tym Claude (chmura lub lokal) używa MCP `biblioteka_szukaj` — TANIO.

Wymaga (na laptopie): calibre (`ebook-convert`, `ebook-meta`) + djvulibre (`djvutxt`) dla djvu.
Bez nich: kroki działają dla formatów czytelnych bez narzędzi (epub/pdf), djvu abstynuje.

Użycie:
  python -m narzedzia.przygotuj_biblioteke            # pełne: cache + indeks + katalog
  python -m narzedzia.przygotuj_biblioteke --tylko-cache   # sam cache (bez indeksu RAG)
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _narzedzie(nazwa: str) -> bool:
    return shutil.which(nazwa) is not None


def _krok(opis: str) -> None:
    print(f"\n{'=' * 64}\n▶ {opis}\n{'=' * 64}", file=sys.stderr, flush=True)


def main() -> int:
    tylko_cache = "--tylko-cache" in sys.argv

    print("🏛️  PRZYGOTUJ BIBLIOTEKĘ — praca lokalna, 0 tokenów Claude", file=sys.stderr)
    # Diagnoza narzędzi (informacyjnie — Prawo XV: brak narzędzia = abstynencja, nie błąd).
    for n in ("ebook-convert", "ebook-meta", "djvutxt"):
        print(f"   {'✅' if _narzedzie(n) else '⚠️  brak'} {n}", file=sys.stderr)

    _krok("1/3 Konwersja + cache tekstu książek")
    from narzedzia.rag import konwerter
    wynik = konwerter.buduj_cache()
    puste = [k for k, v in wynik.items() if v < konwerter.MIN_ZNAKOW_CACHE]

    if not tylko_cache:
        _krok("2/3 Indeks RAG (biblioteka)")
        subprocess.run([sys.executable, str(ROOT / "narzedzia" / "rag" / "indeksuj.py"),
                        "--korpus", "biblioteka"], check=False)

        _krok("3/3 Katalog metadanych książek")
        subprocess.run([sys.executable, "-m", "narzedzia.rag.metadane_ksiag"],
                       cwd=str(ROOT), check=False)

    _krok("GOTOWE")
    print(f"   Scache'owano: {len(wynik) - len(puste)}/{len(wynik)} książek.", file=sys.stderr)
    if puste:
        print(f"   ⚠️  Nieczytelne (brak narzędzia? zainstaluj calibre/djvulibre): "
              f"{', '.join(sorted(puste))[:200]}", file=sys.stderr)
        print("   Djvu (Shreve/Sutton-Barto/Aronson) wymaga `djvutxt` (pakiet djvulibre).",
              file=sys.stderr)
    print("\n   💡 Cache tekstu jest WERSJONOWANY (źródło RAG dla chmury). Po zbudowaniu commituj:\n"
          "      git add bibliotheca_ulpia/dane/tekst_cache/ && git commit\n"
          "      (binaria książek zostają lokalnie, poza repo — decyzja Cezara 2026-07-11).",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
