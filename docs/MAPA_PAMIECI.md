---
kategoria: TABULA
typ: zywy
wlasciciel: imperium/biblioteki/centrum_pamieci.py, imperium/biblioteki/dziennik_niesmiertelny.py, imperium/biblioteki/graf_pamieci.py, imperium/biblioteki/kronika_czatu.py, imperium/biblioteki/kustosz_pamieci.py, imperium/biblioteki/pamiec_absolutna.py, imperium/biblioteki/pamiec_proceduralna.py, imperium/biblioteki/pamiec_proweniencji.py, imperium/biblioteki/pamiec_robocza.py, imperium/biblioteki/pamiec_sesji.py, imperium/biblioteki/refleksja_pamieci.py, imperium/biblioteki/rejestr_wizji.py, imperium/biblioteki/srodowisko_pamieci.py, imperium/biblioteki/zapominanie.py
stan_na: 2026-07-17
powod_istnienia: "Jedyne miejsce konsolidujące 13(+1 nadrzędny=W7) warstw pamięci Claude/Imperium w jedną taksonomię, z mapowaniem na model CoALA (arXiv:2309.02427) i na 'domknięte problemy granicy 2026'"
---
# 🗺️ MAPA PAMIĘCI IMPERIUM — Centrum Pamięci W-360 v5

> **Jedno źródło prawdy o architekturze pamięci.** Konsolidacja 13 warstw (+1 organ nadrzędny W7).
> Liczby policzone z kodu (`python -m imperium.biblioteki.kustosz_pamieci`), nie z pamięci.

> **⚠️ Sprostowanie 2026-07-17 (weryfikacja wobec kodu).** Poprzednia wersja tytułowała się
> „**v13**" — to była pomyłka: **13 to liczba WARSTW, nie numer wersji.** Centrum Pamięci jest
> w **v5** (`centrum_pamieci.py`: „W-360 v5", ostatnie v5 z 2026-06-26 — Pełna Symbioza + Most
> Chmura↔Lokal). Sprostowano też „42 książek" → realnie <!-- LICZBA:ksiazki -->79<!-- /LICZBA -->
> (liczba była ZASZYTA w czterech miejscach kodu i tu; teraz liczy ją
> `srodowisko_pamieci.ksiazki_w_bazie()` i wstrzykuje W15).

## 📜 Czym jest Centrum Pamięci

Zunifikowany system pamięci ciągłości między sesjami Claude (chmura i lokal). Fasadą jest
`centrum_pamieci.py` (`szukaj_wszedzie` = cross-layer), nadrzędnym organem `kustosz_pamieci.py`
(W7) — zarządza, kataloguje, kompresuje, routuje. Wszystko deterministyczne (bez API),
przeżywa przez **git** (storage bezgraniczny), z **bounded context** na starcie.

## 🧱 13 warstw (pełna taksonomia + unikaty)

| Klucz | Moduł | Rola | Typ CoALA | Źródło/Unikat |
|-------|-------|------|-----------|---------------|
| **W1** | `pamiec_absolutna` | logi transakcji (PnL/MAE/MFE/reżim) | epizodyczna | ImperiumLog |
| **W2** | RAG (`narzedzia/rag`) | wiedza z <!-- LICZBA:ksiazki -->79<!-- /LICZBA --> książek + encyklopedia (FTS — ⚠️ wektory **niezbudowane**, patrz niżej) | semantyczna | FTS5 BM25 |
| **W3** | `pamiec_sesji` | lekcje z sesji + profil Cezara | semantyczna | scoring GA |
| **W3b** | `kronika_czatu` | pełny dialog (re-eksport rosnący, szukaj po słowach) | epizodyczna | git-persisted |
| **W4** | `rejestr_wizji` | wizje/decyzje/pomysły/zmiany (scored + dedup) | semantyczna | reżim + GA |
| **W5** | `srodowisko_pamieci` | most chmura↔lokal + manifest | meta | **UNIKAT środowiskowy** |
| **W6** | `dziennik_niesmiertelny` | dożywotnia oś czasu (wstrzykiwana w całości) | epizodyczna | **anti-blindness** |
| **W7** | `kustosz_pamieci` | NADRZĘDNY ORGAN: katalog + kompresja + routing | organ | **UNIKAT organ** |
| **W8** | `graf_pamieci` | połączenia neuronów (temporal KG, waga≥2) | relacyjna | à la Zep/Graphiti |
| **W9** | `refleksja_pamieci` | sprzeczności + przedawnienia (tylko zgłasza) | refleksyjna | **trustworthy reflection** |
| **W10** | `zapominanie` | learned forgetting (wartościowe, safe) | meta | **safe forgetting** |
| **W11** | `pamiec_proceduralna` | runbooki JAK wykonać zadanie | proceduralna | CoALA |
| **W12** | `pamiec_robocza` | aktywny cel bieżącego cyklu | robocza | CoALA |
| **W13** | `pamiec_proweniencji` | ślad pochodzenia „skąd to wiemy" | meta | provenance-aware |

## 🧠 Pokrycie taksonomii CoALA (arXiv:2309.02427) — KOMPLETNE

- **robocza** → W12 · **epizodyczna** → W1/W3b/W6 · **semantyczna** → W2/W3/W4 · **proceduralna** → W11

## 🌍 Domknięte problemy granicy 2026 (arXiv:2603.07670)

- **trustworthy reflection** → W9 (zgłasza, nie utrwala) · **contradiction handling** → W9
- **learned forgetting** → W10 (wartościowe, odwracalne) · **memory blindness** → W6 + W7

## 🏆 Unikaty (kombinacja, której nie ma żaden konkurent)

1. **Reżimowa** (W3/W4) — scoring × dopasowanie reżimu rynku (Mem0/Zep są domenowo ślepe)
2. **Środowiskowa** (W5) — ta sama pamięć: chmura FTS / lokal wektory
3. **Anti-blindness** (W6) — pełna oś wstrzykiwana, nie retrieval (gwarancja, nie statystyka)
4. **Organ nadrzędny** (W7) — kompresja zimnej warstwy wciąż przeszukiwalna (22×)
5. **Graf temporalny** (W8) — połączenia neuronów z oknem ważności
6. **Trustworthy reflection + safe forgetting** (W9/W10) — wg granicy, z zabezpieczeniem anty-utrwalania

## 🔌 Jeden punkt wejścia

```python
from imperium.biblioteki import centrum_pamieci as pm
pm.szukaj_wszedzie("zapytanie", rezim_biezacy="TREND_STRONG")   # cross-layer
# lub nadrzędnie przez organ:
from imperium.biblioteki import kustosz_pamieci as ku
ku.mapa(); ku.census(); ku.szukaj("zapytanie")
```

## ⚖️ Decyzje konsolidacyjne (Prawo XVI — mierzone)

- **Graf waga≥2:** persistowany graf tnie jednorazowe współwystąpienia (szum) →
  30833→883 krawędzi, 3.74MB→0.18MB (95% mniej), ostrzejszy. Funkcja `zbuduj_graf` nadal
  przyjmuje `min_waga` (testy/małe próbki używają 1).
- **W12 i W13 bez własnych plików** — czytają z innych warstw (zero redundancji danych).
- **Zero scalania modułów** — pomiar wykazał, że każda warstwa pełni odrębną rolę CoALA/granicy;
  nie ma dwóch warstw o tym samym sygnale (brak redundancji do usunięcia).

## 🖥️ Lokalny upgrade — 🚨 NIEWYKONANY (zmierzone 2026-07-17, Prawo I)

**Stan faktyczny, nie zamiar:** środowisko = **lokal**, a mimo to `wektory = 0` w bazie RAG
(`srodowisko_pamieci.raport_dostepnosci()` → `rag_tryb: "FTS"`, `model_embeddings: False`).
Poprzednia wersja sugerowała, że tryb FTS to ograniczenie *chmury* („lokalnie: wektory") —
**lokalnie też ich nie ma.** RAG działa dziś wyłącznie na FTS5/BM25 (keyword), nie semantycznie.

| Miara (zmierzone) | Wartość |
|---|---|
| Fragmenty w RAG | 29 699 |
| Źródła łącznie | 104 (<!-- LICZBA:ksiazki -->79<!-- /LICZBA --> książek BIB-* + 25 plików encyklopedii) |
| **Wektory** | **0** ← semantyka nieaktywna |
| `model_embeddings` (sentence-transformers) | **False** ← brak pakietu |

Odblokowanie (kroki podaje też `srodowisko_pamieci.instrukcja_lokal()`):
```bash
git pull && pip install -r requirements.txt        # w tym sentence-transformers
python narzedzia/rag/indeksuj.py --korpus wszystko  # zbuduj wektory
```
→ odblokowałoby semantyczne wektory (W2) i drogę do semantycznych krawędzi grafu (W8).
**Nie jest to zrobione** — dopóki `rag_wektory = 0`, każde zdanie o „semantycznym RAG"
jest planem, nie stanem. Alarm zgłasza sam kod: `_alarmy()` → *„LOKALNIE TO STRATA"*.
