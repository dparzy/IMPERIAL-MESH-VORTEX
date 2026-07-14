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

## 🌐 Web-recenzja Sonnet 5 (triada: DeepSeek→Opus→web, 2026-07-14)

Trzecia noga triady — Sonnet 5 z internetem, niezależnie, ze źródłami. **Wszyscy TIER A → OSTROŻNIE**
(nikt PRZED, nikt ODRZUĆ). Recenzja OSTRZEJSZA niż mój wstępny osąd — kluczowe korekty:

- **VPIN → OSTROŻNIE.** Andersen-Bondarenko (2013/2014) POWAŻNIE obalili predykcję flash-crash: VPIN
  osiąga szczyt PO krachu, nie przed; po kontroli intensywności obrotu **gorszy niż zwykły VIX**.
  Bucket-size arbitralny, |OI| gubi kierunek. → wdrażać tylko wersję SYGNOWANĄ (Andersen-Bondarenko) + A/B.
  Dane: CoinAPI/Binance WS (dostępne). [Kellogg: The Trouble with VPIN]
- **COT_SENTIMENT_INDEX → OSTROŻNIE dla CRYPTO / PRZED dla par tradycyjnych.** KRYTYCZNE: CFTC COT
  praktycznie NIE obejmuje krypto — tylko CME BTC/ETH futures, zero altów/spot/perp. Tygodniowy, z lagiem.
  → wartość dla bota crypto ograniczona do BTC/ETH; sensowny dla forex/commodities.
- **Euforia Dźwigni → OSTROŻNIE.** Próg 15:1 niepotwierdzony; w realnych krachach (Luna, FTX) perp/spot
  SPADAŁ (delewarowanie), nie rósł. **Lepsze, równie dostępne alternatywy: funding rate + Estimated
  Leverage Ratio (ELR = OI/rezerwy giełd, CryptoQuant).** → zastąpić/uzupełnić, próg liczyć empirycznie (kwantyl).
  Dane: CoinGlass (darmowy dashboard perp/spot), funding z API giełd.

**Upshot dla bota CRYPTO (nowa wiedza z web):** najlepsza droga to **funding rate + ELR (OI/rezerwy)**
— lepiej ugruntowane niż surowy perp/spot i **mapują się na nasze luki PSY-01..04** (funding/LS/OI).
COT schodzi w dół (krypto minimalne). VPIN zostaje, ale wersja sygnowana + obowiązkowe A/B. Wszyscy: opt-in OFF.

## P0b — żniwo wrzutni (osobny tor, NIE trading)
6 nieprzerobionych tur (12 lip) z `wrzutnia/Mapa-kluczy calosc plus.md` to **idee infrastrukturalne**, nie kandydaci
tradingowi: frameworki proaktywności/samorozwoju (Thoughtful Agents, Gödel/OmniAgent/AgentEvolver/Recursive
Flow/Galaxy — część rehabilitowana 13 lip) + 5 proponowanych modułów (NOSTRADAMUS≈Namiestnik, ETER≈konformal/
Gubernator sizing, ARIADNA=przyczynowość, TERMINATOR=auto-healing, TIME-MORPH≈mapowanie interwału Namiestnika) +
porady Claude Code/PowerShell. **Większość pokrywa istniejące organy (Prawo XVI)** — wymaga osobnego przeglądu
redundancji, NIE areny tradingowej. Nie mieszać z plonem Hyginusa.
