# 🏛️ IMPERIUM — kod projektu

Działający kod aktualnego projektu, ułożony wg **metafory Cesarstwa Rzymskiego**.
Odrębny od `kingdom-pixel/` (osobny projekt) — *Imperium i Kingdom Pixel nie mieszają się.*

> **Pochodzenie (Prawo I):** moduły zaadaptowane z działającej implementacji projektu
> Kingdom Pixel (autor: Jack). Kod logiki bez zmian, wszystkie 17 modułów kompiluje się czysto.
> Pełny audyt adopcji: [docs/AUDYT_ADOPCJI.md](../docs/AUDYT_ADOPCJI.md).

## 🗺️ Mapa Imperium → moduły

| Folder | Rola (metafora) | Moduły | Prawa |
|--------|-----------------|--------|-------|
| **fundament/** | Rdzeń deterministyczny | `brama_kalkulatora.py`, `kuznia_narzedzi.py` | I, IX, XIII |
| **cesarz/** | Orkiestracja, harmonogram | `titan_mind.py` | III, XIV |
| **senat/** | Debata wieloagentowa | `meta_kora.py` | IX, XIII |
| **legiony/** | Boty strategiczne (wykonanie) | `pierwszy_zwiadowca.py`, `roj_sygnalow.py` | IV, VI, X |
| **pretorianie/** | Bezpieczeństwo i walidacja | `aegis_tarcza.py`, `lustro_prawdy.py` | I, IX |
| **akwedukty/** | Pipeline danych (OHLCV) | `kwatermistrz_danych.py` | II |
| **oczy/** | Wielowarstwowe postrzeganie | `wszechoko.py` | XII |
| **drogi/** | API, routing, egzekucja | `nexus_hub.py`, `war_lancer.py` | III, XIII |
| **swiatynie/** | Wizualizacja i dashboard | `kartograf.py`, `sala_wojenna.py` | V |
| **biblioteki/** | Pamięć i kroniki | `mnemosyne.py`, `kronikarz.py` | VIII, XIII |
| **koloseum/** | Arena testów (backtest) | `valhalla.py` | VI, VII |

## ⚠️ Uwaga (Prawo I — Zero halucynacji)

Wewnątrz modułów pozostały odwołania do starych "Zasad" (np. Zasada 75) z Kingdom Pixel.
To **legacy** — mapowanie na prawa Imperium jest w audycie. Przepiszemy nagłówki
moduł po module, gdy będziemy nad każdym realnie pracować (Prawo VII — stopniowo,
jedna rzecz na raz). Najważniejszy moduł (Brama) już przepisany w pełni.

## 🚦 Status realny (nie hype)

Z audytu Kingdom Pixel: tylko **`brama_kalkulatora` jest w pełni zaadaptowana**.
Reszta to **sprawdzony kod-baza** — kompiluje się, ale wymaga walidacji w działaniu
na realnych danych. `pierwszy_zwiadowca` (STRAT-001) ma **ostrzeżenie**: wyniki były
na danych syntetycznych, bez slippage → traktujemy jako *wstępny paper-test*, nie
"zwalidowaną strategię". Szczegóły w audycie.
