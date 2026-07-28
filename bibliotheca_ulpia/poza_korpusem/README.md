# 📤 POZA KORPUSEM — książki świadomie trzymane poza RAG

**Stan na:** 2026-07-28

Pliki tutaj **zostają w bibliotece, ale nie wchodzą do korpusu RAG**. Mechanizm jest
darmowy i nie wymagał ani linijki kodu: `konwerter.buduj_cache()` używa `iterdir()`,
który **nie schodzi do podkatalogów**, a `indeksuj` bierze wyłącznie to, co jest
w `dane/tekst_cache/`. Plik nieprzetworzony nigdy nie trafi do indeksu.

Decyzja odwracalna jednym przeniesieniem z powrotem do `bibliotheca_ulpia/`.

## Dlaczego coś tu trafia

Nie dlatego, że plik jest zły technicznie — te są sprawne. Dlatego, że **nie niesie
nowej informacji dla Imperium** (Prawo XVI) albo należy do innej dziedziny.

| Plik | Powód |
|---|---|
| `BIB-301_West_Winning-Algorithmic-Trading-Strategies.epub` | Odsyła do cudzych skryptów z TradingView Community („search for … by the TradingView user millerrh"); podtytuł *„…Systems that Work For Trading the Markets In 2026!"*. Gatunek, który plan biblioteki wyklucza świadomie |
| `BIB-303_Sorensen_Statistical-Learning-in-Genetics-2nd-ed.pdf` | Statystyka w **genetyce**. Metody (bayesowskie, MCMC, kroswalidacja, regularyzacja) mamy z mocniejszych źródeł: BIB-139 ESL, BIB-140 ISL, BIB-142 Gelman, BIB-143 McElreath. Zostaje słownictwo genomiczne jako szum w wynikach |

⚠️ **Numery BIB zostają nadane** — pozycje figurują w `docs/PLAN_ROZBUDOWY_BIBLIOTEKI.md`
ze statusem „poza korpusem". Nie zwalniamy numeru, żeby nie przenumerowywać spisu.
