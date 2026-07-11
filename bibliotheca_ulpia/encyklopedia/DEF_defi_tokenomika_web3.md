# ⛓️ DEF — DeFi, tokenomika i Web3 | Encyklopedia Imperium

> **Stan na:** 2026-07-11 | **Ważność:** ⭐⭐⭐ (średni — mechanizmy on-chain odrębne od ONC)
> **Status:** ✅ WYPEŁNIONY (BIB-069 Voshmgir + BIB-054 Antonopoulos-Wood, ekstrakcja z plików — Prawo I).
> **Dla nowicjusza (ZPO):** dział o ekonomii tokenów i zdecentralizowanych finansach — smart
> kontrakty, pule płynności (AMM), staking, lending, derywaty on-chain, projektowanie zachęt.
> Odrębny od **ONC** (fundamenty Bitcoin/blockchain): DEF to **WARSTWA APLIKACJI** i inżynieria
> ekonomiczna. Dla Imperium: źródło nowych klas danych (funding perpetuali, głębokość AMM,
> stabilność stablecoinów) i nowych ryzyk (flash-ataki, depeg).
> **Karmi:** PSY-01 Funding Rate, PSY-04 Open Interest (perpetuale), OC-* (kontekst on-chain),
> przyszłe neurony DeFi, Senat (ryzyko protokołu), Straż A-* (flash-manipulacja).

## 📑 SPIS TREŚCI
1. Token i projektowanie zachęt (Voshmgir)
2. Pieniądz z atrybutem: stablecoiny i Impossible Trinity
3. DEX/AMM — cena bez księgi zleceń
4. Lending, over-collateral, flash loans (i flash-ataki)
5. Derywaty on-chain: perpetuale, syntetyki
6. Ethereum jako maszyna: gas, oracle, composability (Antonopoulos-Wood)
7. Wpływ na Imperium (co mamy / do wdrożenia)
8. Źródła

---

## 1. TOKEN I PROJEKTOWANIE ZACHĘT (BIB-069 Voshmgir)

Voshmgir dzieli tokeny wg funkcji: **pieniądz** (płatniczy), **pieniądz z atrybutami** (asset
tokens/NFT — security, nieruchomości, energia, dane, uwaga, CO2), tokeny użytkowe. Projektowanie
systemu tokenowego to **cztery inżynierie**: **techniczna, ekonomiczna, etyczna, prawna**. Kluczowa
teza: token to nie „coin" — to **programowalna zachęta**, która steruje zachowaniem sieci. Dla
tradingu: emisja/spalanie/staking-yield kształtują podaż i presję cenową (tokenomika = fundament).

## 2. PIENIĄDZ Z ATRYBUTEM — stablecoiny i Impossible Trinity

Stablecoiny wg zabezpieczenia: **fiat-collateralized** (USDT/USDC), **commodity**, **crypto-
collateralized** (over-collateral, DAI), **algorithmic** (najbardziej kruche), oraz **CBDC**.
**Impossible Trinity** stablecoinów: nie da się mieć jednocześnie pełnej **decentralizacji**,
**stabilności peg** i **efektywności kapitału** — coś się poświęca. Dla Imperium: **depeg
stablecoina = sygnał stresu systemowego** (kandydat na reżim — patrz §7).

## 3. DEX / AMM — cena bez księgi zleceń

Decentralized Exchanges = **Automated Market Makers**: cena wynika z krzywej puli (np. x·y=k),
nie z księgi zleceń. Wyzwania: poślizg, **impermanent loss**, front-running/MEV. Głębokość puli i
nierównowaga rezerw niosą sygnał podobny do order-book imbalance — ale **on-chain, publiczny**.

## 4. LENDING, OVER-COLLATERAL, FLASH LOANS

Tokenizowane pożyczki wymagają **over-collateralization** (brak scoringu tożsamości). **Flash loans**
= pożyczka i spłata w JEDNEJ transakcji (bez zabezpieczenia) — potężny prymityw, ale i wektor
**flash-ataków** (manipulacja ceną oracle w ramach jednej tx). Dla Imperium: flash-atak to
on-chain manipulacja → sygnał dla Straży (A-*), pokrewny wash-tradingowi (OC-05).

## 5. DERYWATY ON-CHAIN: perpetuale, syntetyki

Voshmgir: **perpetual contracts** (bez daty wygaśnięcia), syntetyki, ubezpieczenia. **To jest
bezpośrednie źródło danych dla PSY-01 (Funding Rate) i PSY-04 (Open Interest)** — funding perpetuali
to zmaterializowany sentyment lewara (long-heavy → dodatni funding → ryzyko long-squeeze).

## 6. ETHEREUM JAKO MASZYNA (BIB-054 Antonopoulos-Wood)

- **Proof of Stake, smart kontrakty, DeFi, zero-knowledge** (2. wyd. 2026).
- **Gas / EIP-1559:** base fee (palona) + priority fee. **Gas to termometr zatłoczenia sieci** —
  skok gas = wzmożona aktywność/panika on-chain (kandydat na sygnał stresu).
- **Oracles:** most off-chain→on-chain (immediate-read, publish-subscribe, request-response,
  decentralized). Oracle = punkt zaufania i **wektor ataku** (manipulacja ceny → flash-atak).
- **Composability („money legos"):** prymitywy DeFi składają się w złożone instrumenty — moc, ale
  i **ryzyko systemowe** (jeden protokół pociąga inne — pokrewne contagion z BAN/RADAR-04).

---

## 7. WPŁYW NA IMPERIUM

### Co mamy (styk z kodem):
- **PSY-01 Funding Rate / PSY-04 Open Interest** ← perpetuale (§5) — gdy ożyje AdapterFutures,
  funding/OI to zmaterializowany lewar rynku (dziś czekają na adapter, Prawo XV).
- **OC-05 WashTrading / Straż A-*** ← flash-ataki, manipulacja oracle (§4, §6).
- **OC-06/07/08** ← fundamenty on-chain (dział ONC; DEF to warstwa wyżej).

### 🚨 Do wdrożenia (Prawo XV — KANDYDACI ⚠️, walidacja areną przed włączeniem):
1. ⭐⭐⭐⭐ **Reżim depeg stablecoina** ⚠️ — odchylenie USDT/USDC/DAI od 1.0 jako **sygnał stresu
   systemowego** → globalny de-risk (pokrewny RADAR-04). Deterministyczny, w duchu Bramy.
2. ⭐⭐⭐ **Neuron głębokości/nierównowagi AMM** ⚠️ — on-chain analog order-book imbalance
   (rezerwy puli DEX). Wymaga adaptera danych DEX. Prawo XVI: zmierzyć dekorelację z V-03 CVD.
3. ⭐⭐⭐ **Gas jako termometr sieci** ⚠️ — skok gas EIP-1559 = zatłoczenie/panika → filtr ostrożności.
4. ⭐⭐ **Funding-rate neuron (opłata perpetuali)** ⚠️ — dopełnia PSY-01; skrajny funding = ryzyko
   squeeze (kontrariańsko). Ożywa z AdapterFutures.

> **Prawo XVI:** kandydaci DeFi wymagają NOWYCH adapterów danych (DEX/perp/oracle) — to część
> „22 modułów czekających na adaptery" (Prawo XV). Nie budować głosu skorelowanego z V-03/PSY-*.

---

## 8. ŹRÓDŁA (ZPO)

- **BIB-069 Voshmgir** — *Token Economy: Money, NFTs & DeFi*, 3. wyd. (seria Token Economy),
  BlockchainHub 2023. ✅ (ekstrakcja z pliku) — klasy tokenów, stablecoiny + Impossible Trinity,
  AMM/DEX, lending/flash loans, perpetuale/syntetyki, 4 inżynierie projektowania tokenu.
- **BIB-054 Antonopoulos, Wood, Parisi, Mazza, Pozzolini** — *Mastering Ethereum: Implementing
  Smart Contracts*, 2. wyd., O'Reilly 2026. ✅ — PoS, smart kontrakty, gas/EIP-1559, oracles,
  composability („money legos"), DeFi, zero-knowledge.

> **Granica (Prawo XVI):** DEF (warstwa aplikacji/zachęty) ⊥ ONC (fundamenty Bitcoin/blockchain,
> BIB-003/029/030/053). Jak działa łańcuch → ONC; jak działa protokół/token → DEF. Perpetuale/
> funding jako SYGNAŁ → styk z PSY (dane futures). Ryzyko systemowe/contagion → styk z BAN/RSK.

---
*Wypełniono 2026-07-11 (BIB-069 Voshmgir + BIB-054 Antonopoulos-Wood; ekstrakcja z plików, Prawo I).
KANDYDACI ⚠️ do walidacji areną i wymagają adapterów DeFi (Prawo XV) — arena rozstrzyga.*
