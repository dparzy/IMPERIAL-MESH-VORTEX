---
kategoria: DISCIPLINA
typ: zywy
wlasciciel: narzedzia/rag/indeksuj.py
stan_na: 2026-07-18
powod_istnienia: "Instrukcja włączenia pełnej mocy RAG lokalnie (FTS5 od ręki, wektory opcjonalnie)"
dublet_rozstrzygniety: docs/START_LOKAL.md — SETUP_LOKALNY to PEŁNA instrukcja RAG (wektory, calibre, MCP, korpusy, formaty książek); START_LOKAL wspomina `indeksuj.py` jako JEDEN krok w ogólnym starcie lokalnym. Świadomy podział: głęboki setup RAG vs skrócony start, nie dublet treści.
---
# 🔧 Bibliotheca-RAG — Setup na maszynie lokalnej (Cezar)

> **⚠️ Weryfikacja 2026-07-18.** Komendy (`indeksuj.py --bez-wektorow/--tylko-nowe/--korpus`)
> i MCP (`biblioteka_szukaj`/`biblioteka_info`) zgadzają się z kodem ✅. Zaktualizowano liczby
> książek (było „41/42" → dziś <!-- LICZBA:ksiazki -->115<!-- /LICZBA -->) i oznaczono sekcję
> wydajności jako pomiar DATOWANY. **Wektory nadal niezbudowane** (baza w trybie FTS) — patrz
> `docs/MAPA_PAMIECI.md`.

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

### 2. Książki azw3/mobi (Kindle) — wymagają calibre

Z <!-- LICZBA:ksiazki -->115<!-- /LICZBA --> tytułów: **9 to Kindle** (7 azw3 + 2 mobi) —
wymagają **calibre**; reszta (epub/pdf/djvu) indeksuje się od razu:

```bash
# Linux:   sudo apt install calibre
# macOS:   brew install --cask calibre
# Windows: https://calibre-ebook.com/download

# weryfikacja:
ebook-convert --version
python narzedzia/rag/indeksuj.py    # teraz azw3/mobi też się zindeksują
```

Bez calibre indeksują się epub/pdf/djvu (70 tytułów). *(calibre CZYTA też djvu — osobny
`djvulibre`/`djvutxt` nie jest konieczny, gdy masz calibre.)*

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
| `biblioteka` | <!-- LICZBA:ksiazki -->115<!-- /LICZBA --> książek + encyklopedia + vademecum | wiedza zewnętrzna (autorzy) |
| `dane` | `bibliotheca_ulpia/dane/` (CSV/JSON/notatki) | dane tematyczne, wyniki |
| `docs` | dokumentacja Imperium (`docs/*.md`) | "co mamy w kodzie" |

Filtruj wyszukiwanie: `szukaj.py "..." --korpus docs` (tylko nasza dokumentacja)
lub `--korpus biblioteka` (tylko książki). Bez flagi → wszystkie naraz.

**Zasada:** `biblioteka` = wiedza świata, `docs` = mapa naszego systemu. Encyklopedia
jest mostem (mapuje wiedzę na nasze moduły, np. "Kyle's λ → EXP-14").

## Wydajność (pomiar DATOWANY — chmura, 35 plików, ~czerwiec 2026)

*To pomiar swojego czasu, nie dzisiejsza baza (dziś ~29,7k fragmentów / 104 źródła):*
- Pełna indeksacja 35 plików (epub/pdf + encyklopedia): **~24 s** → 7339 fragmentów
- Przyrostowa gdy nic nie zmienione: **~0.8 s**
- Dodanie korpusu docs (45 plików): **~1.2 s** → +421 fragmentów
- Wyszukiwanie FTS: **<0.1 s**

## Baza danych

`baza_wiedzy.db` jest w `.gitignore` (odtwarzalna deterministycznie przez `indeksuj.py`).
Nie commitujemy jej — każdy odtwarza lokalnie z książek + dokumentów.

> **BIB-032 O'Hara** (PDF): to skan obrazowy — narzędzia OCR zwracają bełkot dla tego pliku.
> Esencja książki jest dostępna w `encyklopedia/MKS_mikrostruktura_rynku.md`.
> Indeks RAG: <!-- LICZBA:ksiazki -->115<!-- /LICZBA --> książek + encyklopedia (FTS5). Wektory:
> wymagają modelu embeddingów (huggingface.co) — nadal NIEZBUDOWANE, baza w trybie FTS-only.
