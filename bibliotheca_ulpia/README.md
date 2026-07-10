# 📚 Biblioteka Imperium — Bibliotheca Ulpia

Wrzuć tu pliki epub/pdf/azw3 — Claude Code je przeczyta i wyciągnie esencję
(neurony, strategie, W-xxx) zgodnie z Zasadą Pełnego Opisu (ZPO).

## 🗂️ Struktura biblioteki
- **`BIB-001..069`** — kanon źródłowy (69 książek, pliki epub/pdf/azw3/mobi/djvu)
- **`encyklopedia/`** — tematyczna biblia wiedzy operacyjnej (działy LEW/TRD/IMP/...),
  z oceną ważności i wprost wskazanym wpływem na kod. Start: [`encyklopedia/INDEX_MAIOR.md`](encyklopedia/INDEX_MAIOR.md)
- **`vademecum/`** — szybkie ściągi (checklisty, wzory) — 1 strona na temat
- **`dane/katalog_ksiag.json`** — strukturalny katalog książek (autor, tytuł, format;
  z calibre także tagi/język/rok/ISBN). Buduje: `python -m narzedzia.rag.metadane_ksiag`

## 📖 Katalog metadanych (calibre jako backend, nie MCP)
`narzedzia/rag/metadane_ksiag.py` buduje `dane/katalog_ksiag.json`. Bez calibre parsuje
nazwy plików (autor/tytuł/format). Z zainstalowanym **calibre** (`ebook-meta`) dokłada
tagi, język, rok wydania, wydawcę, ISBN — karmiąc RAG i katalog bez redundantnego MCP
(ZASADA MCP: własny RAG już szuka w treści; calibre dokłada tylko metadane).

> Encyklopedia jest **żywa**: aktualizowana po każdej nowej książce/lekcji (Prawo XVII),
> pamiętana przez Claude (chmura) i lokalnego Claude. Następny krok: warstwa
> Bibliotheca-RAG (pamięć semantyczna — patrz `encyklopedia/IMP_ulepszenia_imperium.md`).

## Format nazwy pliku
```
BIB-022_Lopez-de-Prado_ML-Asset-Managers.epub
BIB-023_Harris_Trading-Exchanges.pdf
```
## Limit rozmiaru GitHub: 100 MB na plik (epub/pdf zwykle 2-15 MB — OK)

## Jak wrzucić (na laptopie, w folderze imperial-mesh-vortex):
```
git checkout claude/sleepy-fermi-dsdE4
git pull
# skopiuj plik epub/pdf do tego folderu (bibliotheca_ulpia/)
git add bibliotheca_ulpia/nazwa-pliku.epub
git commit -m "dodaj ksiazke BIB-022"
git push
```
Potem napisz mi "masz nową książkę w bibliotheca_ulpia/" — przeczytam i wrócę z esencją.
