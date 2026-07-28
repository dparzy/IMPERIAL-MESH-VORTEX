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
  python -m narzedzia.przygotuj_biblioteke --ocr           # + OCR skanów (5.2 s/stronę!)

Narzędzia zewnętrzne (calibre/tesseract) odnajduje organ FABER — ręczne dopisywanie
do PATH nie jest już potrzebne. Exit 3 = posiadany format nie ma czym wejść do RAG.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _krok(opis: str) -> None:
    print(f"\n{'=' * 64}\n▶ {opis}\n{'=' * 64}", file=sys.stderr, flush=True)


def main() -> int:
    tylko_cache = "--tylko-cache" in sys.argv

    print("🏛️  PRZYGOTUJ BIBLIOTEKĘ — praca lokalna, 0 tokenów Claude", file=sys.stderr)

    # DIAGNOZA NARZĘDZI PRZEZ FABERA (2026-07-28). Dawniej: `shutil.which(nazwa)` i lista
    # wpisana ręcznie w kodzie. Zmierzone tego dnia: which() zwracał None dla calibre
    # I tesseracta, choć OBA były zainstalowane — po prostu poza PATH sesji. Diagnoza mówiła
    # „⚠️ brak", potok mimo to ruszał i cicho gubił każdy plik wymagający konwersji.
    from imperium.fundament import faber
    faber.zapewnij_path()
    print(faber.raport(ROOT / "bibliotheca_ulpia"), file=sys.stderr)
    alarmy_narzedzi = faber.alarmy(ROOT / "bibliotheca_ulpia")

    _krok("1/3 Konwersja + cache tekstu książek")
    from narzedzia.rag import konwerter
    # --ocr opt-in (domyślnie OFF): 5.2 s/stronę na PEDES. Bez flagi skany trafiają
    # na listę KANDYDATÓW, więc nic nie ginie po cichu, a bieg nie trwa godzinami.
    wynik = konwerter.buduj_cache(ocr="--ocr" in sys.argv)
    puste = [k for k, v in wynik.items() if v < konwerter.MIN_ZNAKOW_CACHE]

    rc = 0
    if not tylko_cache:
        _krok("2/3 Indeks RAG (biblioteka)")
        r_idx = subprocess.run([sys.executable, str(ROOT / "narzedzia" / "rag" / "indeksuj.py"),
                                "--korpus", "biblioteka"])
        if r_idx.returncode != 0:
            # Propagujemy porażkę indeksacji (recenzja cubic PR#119): bez tego skrypt drukował
            # GOTOWE/exit 0 nawet przy nieaktualnej/pustej bazie RAG — wołający (i CI) nie miał
            # jak wykryć zepsutego indeksu, a to on karmi chmurę.
            rc = r_idx.returncode
            print(f"   ❌ Indeksacja RAG nie powiodła się (exit {rc}) — baza może być "
                  "nieaktualna/pusta.", file=sys.stderr)

        _krok("3/3 Katalog metadanych książek")
        # Katalog = WZBOGACENIE (best-effort): wymaga calibre; brak = abstynencja, nie błąd krytyczny.
        subprocess.run([sys.executable, "-m", "narzedzia.rag.metadane_ksiag"], cwd=str(ROOT))

    # Brak narzędzia dla POSIADANYCH formatów to porażka biegu, nie „informacja" (Prawo XV):
    # bez tego skrypt kończył exit 0, gdy część księgozbioru w ogóle nie miała jak wejść
    # do RAG — dokładnie ta klasa, którą naprawiono już dla indeksacji (PR#119).
    if alarmy_narzedzi and rc == 0:
        rc = 3

    _krok("GOTOWE" if rc == 0 else "ZAKOŃCZONE Z BŁĘDEM")
    print(f"   Scache'owano: {len(wynik) - len(puste)}/{len(wynik)} książek.", file=sys.stderr)
    if puste:
        # Nie zgadujemy już „brak narzędzia?" — FABER wie to na pewno i powiedział wyżej.
        print(f"   ⚠️  Nieczytelne ({len(puste)}): {', '.join(sorted(puste))[:200]}",
              file=sys.stderr)
    for a in alarmy_narzedzi:
        print(f"   {a}", file=sys.stderr)
    print("\n   💡 Cache tekstu jest WERSJONOWANY (źródło RAG dla chmury). Po zbudowaniu commituj:\n"
          "      git add bibliotheca_ulpia/dane/tekst_cache/ && git commit\n"
          "      (binaria książek zostają lokalnie, poza repo — decyzja Cezara 2026-07-11).",
          file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
