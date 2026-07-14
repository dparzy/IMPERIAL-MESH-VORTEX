# 🔭 PLON HYGINUSA — osąd sędziego (Vitruviusz), 2026-07-14

> **Snapshot datowany (Prawo I).** Pierwszy realny bieg Hyginusa po komplecie U1–U4 (`--pelny`:
> query-expansion + self-critique + świadomość systemu). 4 tematy celujące w luki + siłę mikrostruktury
> (BIB-032/007). Wszyscy kandydaci to **⚠️ HIPOTEZY — prawdą DOPIERO po arenie** (ZASADA WPIĘCIA, opt-in OFF).
> Źródło surowe: `docs/KOLEJKA_HIPOTEZ_BIBLIOTEKARZ.jsonl` (gitignore). Sędzia: Vitruviusz (Opus).

## Werdykt kluczowy
**Prawie każdy kandydat jest DATA-GATED** — wymaga feedu/adaptera (order-flow, COT/CFTC, perp+spot
volume, sentyment newsów, opcje). To znaczy: plon Hyginusa to **priorytetowa lista „jaką alfę zbudować,
gdy dodamy który feed"** — spina lukę Prawa XV (22 milczące moduły) z konkretnym, ugruntowanym w książkach modułem.

## TIER A — najsilniejsi (ugruntowani, wypełniają realną lukę, nieredundantni)
| Kandydat | Typ | Źródło | Luka/feed | Krytyka U3 (dowody przeciw) |
|----------|-----|--------|-----------|------------------------------|
| **VPIN_TOKSYCZNOŚĆ** | neuron | BIB-007 (AFML, Easley 2011) | brak modułu toksyczności; feed: order-flow/OI+volume | Andersen&Bondarenko 2013 krytykują predykcję flash-crash; próg 0.9 arbitralny → **SŁABE** |
| **COT_SENTIMENT_INDEX** | neuron | BIB-047/002/015 (Kaufman/Murphy/Elder) | PSY/RADAR; feed: CFTC COT (tyg., 3-dniowy lag) | brak krytyki założeń w tekście; ryzyko overfittingu progu + lag publikacji → **SŁABE** |
| **Euforia Dźwigni** (perp/spot vol) | koncepcja/sygnał | BIB-059 (Kindleberger) | brak _LEVERAGE_EUPHORIA_; feed: perp+spot volume | brak danych do progu 15:1; brak dowodów przeciw = ostrożność |

## TIER B — interesujący, słabsi/wymagają danych
- **Sentiment Intensity Scoring** (rozszerza NEWS-01 o skalę siły) — U3: **ZERO dowodów przeciw = możliwa stronniczość potwierdzenia** (nie dowód słuszności). Feed: sentyment newsów.
- **PUT_CALL_RATIO_MA** — sentyment opcyjny (nowa kategoria), feed: opcje (trudne w krypto).
- **Sentiment PCA/ICA Factors** — U3: BIB-026 ostrzega o wrażliwości wyników. Słabszy.
- **OI_PERSISTENCJA** — autokorelacja OI; U3: „konieczny, non-sufficient" — to raczej filtr do VPIN niż osobny neuron.

## TIER C — redundantni (Prawo XVI — U3 złapał)
- **Napływ Kapitału Spekulacyjnego** — U3: ≈ **OC-04 netflow + RADAR-03** → nadmiarowy (rozszerzenie progu/filtra).
- **SPECULATOR_COMMERCIAL_SPREAD** — pokrywa się z COT_SENTIMENT_INDEX.

## Rekomendacja
1. **TIER A → backlog areny** jako ⚠️ kandydaci, każdy SPIĘTY z odpowiednim feedem (P2 dane alternatywne).
   Kolejność wdrożenia zależy od dostępności feedu, nie od atrakcyjności hipotezy.
2. **TIER B** — trzymać, wrócić po walidacji TIER A.
3. **TIER C** — odrzucić lub zmierzyć korelację (jeśli |r|>0.8 z OC-04/RADAR-03 → scalić/waga w dół).
4. Żaden nie wchodzi do kodu bez pomiaru areny (IC/WFO/DSR). U3 pokazał wartość: łapie overfitting, redundancję, confirmation bias — sędzia potwierdza.

## P0b — żniwo wrzutni (osobny tor, NIE trading)
6 nieprzerobionych tur (12 lip) z `wrzutnia/Mapa-kluczy calosc plus.md` to **idee infrastrukturalne**, nie kandydaci
tradingowi: frameworki proaktywności/samorozwoju (Thoughtful Agents, Gödel/OmniAgent/AgentEvolver/Recursive
Flow/Galaxy — część rehabilitowana 13 lip) + 5 proponowanych modułów (NOSTRADAMUS≈Namiestnik, ETER≈konformal/
Gubernator sizing, ARIADNA=przyczynowość, TERMINATOR=auto-healing, TIME-MORPH≈mapowanie interwału Namiestnika) +
porady Claude Code/PowerShell. **Większość pokrywa istniejące organy (Prawo XVI)** — wymaga osobnego przeglądu
redundancji, NIE areny tradingowej. Nie mieszać z plonem Hyginusa.
