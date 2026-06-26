# 🏛️ ONC — On-chain i Krypto | Encyklopedia Imperium

> **Stan na:** 2026-06-25 | **Ważność:** ⭐⭐⭐ (średni — unikat krypto, dane wymagają feedów)
> **Dla nowicjusza (ZPO):** on-chain to dane Z BLOCKCHAINA (nie z giełdy) — ile BTC się
> przemieszcza, po jakiej cenie kupiono monety, ile leży na giełdach. To „rentgen" sieci,
> niedostępny w tradycyjnych rynkach. Krypto ma fundamenty, których akcje nie mają: podaż
> zaprogramowaną kodem (halvingi), przejrzysty przepływ kapitału.

## 📑 SPIS TREŚCI
1. [Fundamenty Bitcoina (Ammous)](#1-fundamenty)
2. [Halvingi i model podaży](#2-halvingi)
3. [Metryki on-chain](#3-metryki-onchain)
4. [Cykle rynkowe krypto](#4-cykle)
5. [Wpływ na Imperium](#5-wpływ-na-imperium)
6. [Źródła](#6-źródła)

---

## 1. FUNDAMENTY (Ammous, BIB-030 *Bitcoin Standard*)

- **Twardy pieniądz:** BTC ma zaprogramowaną, malejącą podaż (max 21M). Stock-to-flow rośnie.
- **Sound money thesis:** wartość z niemożności inflacji (przeciwieństwo fiat).
- **Saliency dla tradingu:** podaż jest PRZEWIDYWALNA (kod), popyt — nie. Szok podażowy
  (halving) jest znany z góry → rynek go dyskontuje, ale historycznie z opóźnieniem.

---

## 2. HALVINGI I MODEL PODAŻY

- **Halving:** co ~210 000 bloków (~4 lata) nagroda za blok spada o połowę → szok podażowy.
- **Daty kotwic (block height → timestamp):** genesis 2009, halvingi 2012/2016/2020/2024.
- **Stock-to-Flow (S2F):** podaż / roczna emisja. Rośnie skokowo po każdym halvingu.
- **W Imperium (OC-06..08):** `szacuj_block_height(timestamp)` — interpolacja między kotwicami,
  ekstrapolacja 10 min/blok. S2F, dni do halvingu, inflacja roczna.
- **Status:** ⏳ wymagają REALNEGO timestampu z barów (audyt ma sztuczny ts z ery 1970 →
  block 0). Ożywają na realnych danych z datami (W-377/378/379).

---

## 3. METRYKI ON-CHAIN

| Metryka | Co mierzy | Sygnał |
|---------|-----------|--------|
| **MVRV** | cena rynkowa / cena realizowana | >3.7 szczyt, <1 dno |
| **SOPR** | zysk/strata wydawanych monet | >1 zyski realizowane, <1 kapitulacja |
| **Puell Multiple** | przychód górników vs średnia | ekstrema = cykle |
| **Exchange netflow** | napływ/odpływ z giełd | napływ = presja podaży (sprzedaż) |
| **Realized cap** | wartość wg ceny ostatniego ruchu | „prawdziwa" kapitalizacja |
| **Dormancy / HODL waves** | wiek wydawanych monet | smart money behavior |

**Status w Imperium (OC-01..04):** ⏳ wyciszone — wymagają API on-chain (Glassnode/CryptoQuant free tier).

---

## 4. CYKLE RYNKOWE KRYPTO

- **4-letni cykl halvingowy:** historycznie akumulacja → bull post-halving → szczyt → bear.
- **Pi-Cycle Top:** przecięcie 111 DMA i 350 DMA×2 — historyczny wskaźnik szczytu.
  **W Imperium: Z-07 kill-switch** (wymaga ≥350 barów 1D).
- **Dominacja BTC:** kapitał rotuje BTC → alty (alt season) i z powrotem (risk-off).
  **W Imperium: RADAR-02** (⏳ czeka na CoinGecko).

---

## 5. WPŁYW NA IMPERIUM

### Co mamy (kod):
- **OC-06..08** — S2F, dni do halvingu, inflacja podaży (⏳ realny timestamp)
- **OC-01..04** — MVRV, SOPR, Puell, netflow (⏳ API on-chain)
- **Z-07 Pi-Cycle** — kill-switch szczytu (⏳ ≥350 barów 1D)
- **RADAR-02/03** — dominacja BTC, przepływ kapitału (⏳ feedy)
- `budowniczy_wskaznikow._dodaj_btc_onchain` — dodaje BTC_BLOCK_HEIGHT z timestampu

### 🚨 Prawo XV — ożywić:
1. ⭐⭐⭐ **OC-06..08 na realnych barach** — gdy bary mają realne daty (już działa mechanizm)
2. ⭐⭐⭐ **Glassnode free tier** → OC-01..04 (4 martwe neurony on-chain)
3. ⭐⭐⭐ **CoinGecko** → RADAR-02 dominacja BTC
4. ⭐⭐ **Z-07 Pi-Cycle** na pełnej historii 1D (≥350 barów)

---

## 6. ŹRÓDŁA
- BIB-030 Ammous — *The Bitcoin Standard* (fundamenty, twardy pieniądz)
- BIB-029 Bashir — *Mastering Blockchain* (technika)
- BIB-003 Burniske & Tatar — *Cryptoassets* (wycena)
- BIB-005 Blum — *What Exactly Is Crypto* (self-pub 2022, ISBN ⚠️ brak — wprowadzenie/glosariusz
  ONC dla nowicjusza; ⭐⭐, poboczny **DEF**)
- **BIB-024 Lowe** — *Bitcoin and Cryptocurrency Trading for Beginners* (self-pub, ISBN ⚠️ brak)
  ⭐ 1/5 — poziom 0 (jak kupić BTC na Coinbase/eToro). 🚨 Zawiera ANTYWZORZEC: „uśrednianie
  w dół" (EMA buy-the-dip) — SPRZECZNE z dyscypliną stop-loss i Regułą 6% Imperium. Trzymać
  jako referencję nowicjusza, NIE jako źródło logiki handlowej. Poboczny **RSK** (wallet security).
- Powiązane: **TRD** (krypto-natywni), **RSK**, **ALG**, **DEF**
