# 📚 BIBLIOTHECA ULPIA — Księgozbiór Imperium

> Biblioteka Trajana (Bibliotheca Ulpia) była największą biblioteką cesarskiego Rzymu.
> Tu żyje wiedza źródłowa Imperium: **<!-- LICZBA:ksiazki -->115<!-- /LICZBA --> ksiąg** (BIB-xxx),
> encyklopedia operacyjna i vademecum. Karmi RAG, Hyginusa (zwiad) i Szkołę TIRO.

## ⚠️ ZASADA NR 1 — binaria ksiąg TYLKO LOKALNIE (decyzja Cezara 2026-07-11)

**Pliki książek (`.pdf/.epub/.azw3/.mobi/.djvu`) NIGDY nie idą do git.** Są za duże i komercyjne —
zostają wyłącznie na dysku laptopa. Do repozytorium (i chmury) trafia **tylko wersjonowany
`dane/tekst_cache/`** — czysty tekst wyekstraktowany z ksiąg, źródło RAG. Dzięki temu Claude w
chmurze przeszukuje treść bez posiadania plików.

```
KSIĄŻKA.pdf  ──(ekstrakcja, lokalnie)──►  dane/tekst_cache/*.txt  ──(git)──►  RAG chmura
   [tylko laptop]                              [wersjonowany]
```

## 🗂️ Struktura

| Ścieżka | Co | W git? |
|---|---|---|
| `BIB-001 … BIB-116` | księgozbiór źródłowy (autor + tytuł w nazwie) | ❌ tylko lokal |
| `dane/tekst_cache/` | tekst wyekstraktowany — źródło RAG | ✅ wersjonowany |
| `dane/katalog_ksiag.json` | katalog metadanych (autor, tytuł, format, ISBN z calibre) | ✅ |
| `encyklopedia/` | tematyczna biblia wiedzy operacyjnej — start: [`INDEX_MAIOR.md`](encyklopedia/INDEX_MAIOR.md) | ✅ |
| `vademecum/` | szybkie ściągi (checklisty, wzory) — 1 strona/temat | ✅ |
| `dane/*.jsonl` | ledgery Imperium (kronika, dziennik, TIRO, CODEX) | ✅ |

## 🔧 Pipeline — jedna komenda, ZERO tokenów Claude

Całą ciężką pracę robią narzędzia deterministyczne lokalnie; Claude potem odpytuje RAG chirurgicznie
(płaci tylko za zwrócone fragmenty, nie za czytanie całych ksiąg):

```bash
python -m narzedzia.przygotuj_biblioteke     # cache + indeks RAG + katalog metadanych
```

Wymaga (laptop): **calibre** (`ebook-convert`, `ebook-meta`) — czyta też `.djvu`, `djvutxt` zbędny.

## 🔭 Kto czyta bibliotekę

- **HYGINUS** (`narzedzia/bibliotekarz.py`, DeepSeek) — zwiadowca: czyta fragmenty RAG per temat,
  proponuje KANDYDATÓW (neurony/strategie), cytuje źródło `BIB-xxx`. **⚠️ KANDYDAT ≠ PRAWDA** —
  DeepSeek halucynuje 94–96% z pamięci, więc pracuje WYŁĄCZNIE z fragmentów (grounding).
- **VITRUVIUSZ** (Opus) — sędzia: weryfikuje kandydatów, odrzuca halucynacje, rozstrzyga arena (pomiar).
- **NOTARIUS** — przy każdym wywołaniu DeepSeek zapisuje parę `prompt→odpowiedź` = surowiec Szkoły **TIRO**.

## ➕ Jak dodać księgę (na laptopie)

1. Skopiuj plik do `bibliotheca_ulpia/` w formacie **`BIB-XXX_Autor_Tytuł-z-myślnikami.ext`**
   (autor = nazwisko; 2 autorów łączone myślnikiem; ASCII bez diakrytyki). Wzór:
   ```
   BIB-116_Pearl_Causality-Models-Reasoning-and-Inference.epub
   ```
2. `python -m narzedzia.przygotuj_biblioteke` — zbuduje cache + RAG + katalog.
3. Zacommituj **tylko tekst** (nie binarium):
   ```bash
   git add bibliotheca_ulpia/dane/tekst_cache/ bibliotheca_ulpia/dane/katalog_ksiag.json
   git commit -m "biblioteka: BIB-XXX <autor> <tytuł>"
   ```
   Plik binarny zostaje lokalnie (`.gitignore`). Push wykonuje Cezar.

---

> 🔄 **Ten README jest ŻYWY** — liczba ksiąg `<!-- LICZBA:ksiazki -->` jest wstrzykiwana z katalogu
> (`python narzedzia/tabularium.py liczby --zapisz`), więc nie może się rozjechać. Resztę treści
> aktualizuj przy KAŻDEJ zmianie struktury/pipeline (rozkaz Cezara 2026-07-21 — dokument nie może gnić).
