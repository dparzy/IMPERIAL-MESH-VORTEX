# 🔧 Bibliotheca-RAG — Setup na maszynie lokalnej (Cezar)

> **Dla nowicjusza (ZPO):** RAG = pamięć semantyczna biblioteki. Zamiast czytać całą
> książkę (drogie w tokenach), Claude pyta bazę "co X mówi o Y?" i dostaje gotowe fragmenty
> z podaniem źródła. Ten plik to instrukcja, jak włączyć PEŁNĄ moc lokalnie.

## Co działa od razu (zero instalacji)

FTS5 (wyszukiwanie pełnotekstowe BM25) jest wbudowane w Pythona (`sqlite3`).
Działa bez sieci, bez modeli, bez bibliotek zewnętrznych:

```bash
python narzedzia/rag/indeksuj.py --bez-wektorow   # zbuduj bazę (FTS)
python narzedzia/rag/szukaj.py "Kelly criterion sizing"
```

## Pełna moc — 2 rzeczy do dodania lokalnie

### 1. Wektory semantyczne (synonimy, parafrazy)

W chmurze HuggingFace jest zablokowane (403) → działa tylko FTS. Lokalnie masz sieć:

```bash
pip install sentence-transformers
python narzedzia/rag/indeksuj.py     # pobierze model all-MiniLM-L6-v2 (raz, ~80 MB)
python narzedzia/rag/szukaj.py "jak duże zlecenie rusza ceną" --tryb hybrid
```

Model `all-MiniLM-L6-v2` jest darmowy, offline po pierwszym pobraniu. Tryb `hybrid`
łączy FTS (dokładne terminy) + wektory (znaczenie) → najlepsze wyniki.

**Różnica:** FTS znajdzie "Kyle lambda" tylko gdy te słowa są w tekście. Wektor znajdzie
też "miara wpływu zlecenia na cenę" — bo rozumie znaczenie, nie tylko słowa.

### 2. Książki azw3/mobi (15 z 32 tytułów)

Formaty Kindle (azw3/mobi) wymagają **calibre**:

```bash
# Linux:   sudo apt install calibre
# macOS:   brew install --cask calibre
# Windows: https://calibre-ebook.com/download

# weryfikacja:
ebook-convert --version
python narzedzia/rag/indeksuj.py    # teraz azw3/mobi też się zindeksują
```

Bez calibre indeksują się tylko epub/pdf/djvu (17 tytułów). djvu wymaga `djvulibre`
(`apt install djvulibre-bin`, daje `djvutxt`).

## Konfiguracja MCP (Claude Code odpytuje RAG sam)

Dodaj do `.claude/settings.json` (lub `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "biblioteka": {
      "command": "python",
      "args": ["narzedzia/rag/mcp_server.py"]
    }
  }
}
```

Po restarcie Claude Code ma narzędzia:
- `biblioteka_szukaj(zapytanie, topk, tryb, korpus)` — szuka w bibliotece
- `biblioteka_info()` — statystyki bazy

## Dodawanie nowej wiedzy

| Co dodajesz | Gdzie | Komenda |
|-------------|-------|---------|
| Nowa książka | `bibliotheca_ulpia/BIB-XXX_Autor_Tytul.epub` | `indeksuj.py --tylko-nowe` |
| Dział encyklopedii | `bibliotheca_ulpia/encyklopedia/XYZ_temat.md` | `indeksuj.py --tylko-nowe` |
| Dane tematyczne (CSV/JSON/notatki) | `bibliotheca_ulpia/dane/*.csv\|json\|txt\|md` | `indeksuj.py --tylko-nowe` |
| Dokumentacja Imperium do RAG | `docs/*.md` (już istnieje) | `indeksuj.py --korpus wszystko --tylko-nowe` |

**`--tylko-nowe`** = tryb przyrostowy: indeksuje TYLKO nowe/zmienione pliki (po hashu
rozmiar+mtime), reszta pomijana. Przy 200 książkach to sekundy zamiast minut.

## Korpusy (warstwy wiedzy)

| Korpus | Zawartość | Po co |
|--------|-----------|-------|
| `biblioteka` | 32 książki + encyklopedia + vademecum | wiedza zewnętrzna (autorzy) |
| `dane` | `bibliotheca_ulpia/dane/` (CSV/JSON/notatki) | dane tematyczne, wyniki |
| `docs` | dokumentacja Imperium (`docs/*.md`) | "co mamy w kodzie" |

Filtruj wyszukiwanie: `szukaj.py "..." --korpus docs` (tylko nasza dokumentacja)
lub `--korpus biblioteka` (tylko książki). Bez flagi → wszystkie naraz.

**Zasada:** `biblioteka` = wiedza świata, `docs` = mapa naszego systemu. Encyklopedia
jest mostem (mapuje wiedzę na nasze moduły, np. "Kyle's λ → EXP-14").

## Wydajność (zmierzone w chmurze, FTS)

- Pełna indeksacja 35 plików (epub/pdf + encyklopedia): **~24 s** → 7339 fragmentów
- Przyrostowa gdy nic nie zmienione: **~0.8 s**
- Dodanie korpusu docs (45 plików): **~1.2 s** → +421 fragmentów
- Wyszukiwanie FTS: **<0.1 s**

## Baza danych

`baza_wiedzy.db` jest w `.gitignore` (odtwarzalna deterministycznie przez `indeksuj.py`).
Nie commitujemy jej — każdy odtwarza lokalnie z książek + dokumentów.
