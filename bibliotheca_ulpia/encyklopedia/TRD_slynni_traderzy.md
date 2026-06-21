# 🏛️ TRD — Słynni Traderzy | Encyklopedia Imperium

> **Stan na:** 2026-06-21 | **Ważność:** ⭐⭐⭐⭐ (wysoki — sprawdzone w boju techniki)
> **Dla nowicjusza (ZPO):** to lista legend tradingu z dokładnym opisem ICH techniki
> i — co najważniejsze — **przypisaniem do konkretnego modułu/strategii Imperium**.
> Nie „ciekawostki", tylko mapa: czego nauczył nas każdy mistrz i gdzie to żyje w kodzie.

## 📑 SPIS TREŚCI
1. [Macro & trend](#1-macro--trend)
2. [Systematic & quant](#2-systematic--quant)
3. [Short-term & momentum](#3-short-term--momentum)
4. [Psychologia & dyscyplina](#4-psychologia--dyscyplina)
5. [Krypto-natywni](#5-krypto-natywni)
6. [Negatywne wzorce (czego NIE robić)](#6-negatywne-wzorce)
7. [Mapa: trader → moduł Imperium](#7-mapa-trader--moduł)
8. [Źródła](#8-źródła)

---

## 1. MACRO & TREND

### Paul Tudor Jones ⭐⭐⭐⭐⭐
- **Styl:** macro, trend-following z obsesyjną kontrolą ryzyka
- **Kluczowa technika:** 200-dniowa średnia jako filtr reżimu („nic poniżej 200 MA nie kupuję"); asymetria 5:1 (ryzyko:zysk)
- **Cytat:** *„Nie myśl o zarabianiu — myśl o ochronie tego, co masz."*
- **→ Imperium:** RADAR-01 (BTC_TREND jako filtr reżimu), asymetria R:R w strategiach wyjścia

### Stanley Druckenmiller ⭐⭐⭐⭐⭐
- **Styl:** macro, koncentracja kapitału
- **Kluczowa technika:** *„To nie czy masz rację — to ile zarabiasz gdy masz rację, i ile tracisz gdy się mylisz."* Ładuje pozycję gdy ma przewagę, minimalizuje gdy nie.
- **→ Imperium:** dynamiczny sizing / Gubernator (W-325) — rozmiar skaluje się z pewnością

### George Soros ⭐⭐⭐⭐
- **Styl:** refleksywność, macro
- **Kluczowa technika:** teza → test pozycją → eskalacja gdy rynek potwierdza, szybkie cięcie gdy nie
- **→ Imperium:** Senat (próg pewności przed wejściem), skalowanie pozycji

### Larry Hite ⭐⭐⭐⭐
- **Styl:** systematic trend (Mint)
- **Kluczowa technika:** *„Nigdy nie ryzykuj >1% na transakcję."* Mechaniczne reguły, zero emocji.
- **→ Imperium:** stały % ryzyka w sizingu, Reguła 6%

---

## 2. SYSTEMATIC & QUANT

### Jim Simons (Renaissance) ⭐⭐⭐⭐⭐
- **Styl:** czysto ilościowy, krótkoterminowy, statystyczny
- **Kluczowa technika:** setki słabych, nieskorelowanych sygnałów łączonych w jeden silny (prawo wielkich liczb); brutalna walka z overfittingiem
- **→ Imperium:** **cała architektura roju** — wiele neuronów (słabych głosów) → Legatus agreguje. Prawo XVI (dekorelacja), prawo fundamentalne IR=IC·√breadth (W-369)

### Ed Thorp ⭐⭐⭐⭐⭐
- **Styl:** matematyczny edge (blackjack → rynki)
- **Kluczowa technika:** Kelly criterion (optymalny sizing przy znanej przewadze); szukanie mierzalnego edge'u
- **→ Imperium:** sizing oparty na przewadze, mierzenie edge (metryki IC, DSR/PBO)

### Cliff Asness (AQR) ⭐⭐⭐⭐
- **Styl:** faktorowy (value, momentum, carry)
- **Kluczowa technika:** dywersyfikacja po nieskorelowanych faktorach; momentum jako faktor
- **→ Imperium:** kategorie neuronów (M/T/V/F/O...) jako faktory; dekorelacja (Prawo XVI)

### Ernie Chan ⭐⭐⭐⭐
- **Styl:** retail quant, mean-reversion + momentum
- **Kluczowa technika:** rygor backtestu, kointegracja par (stat-arb)
- **→ Imperium:** Engle-Granger kointegracja (mikrostruktura.py), dyscyplina backtestu (DSR/PBO)

---

## 3. SHORT-TERM & MOMENTUM

### Linda Raschke ⭐⭐⭐⭐
- **Styl:** krótkoterminowy momentum/mean-reversion
- **Kluczowa technika:** „80-20", pierwsze cofnięcie po momentum; setupy 2-3 barowe
- **→ Imperium:** neurony momentum (X-25/26), reżim krótkoterminowy

### Jesse Livermore ⭐⭐⭐⭐
- **Styl:** klasyczny spekulant, tape reading
- **Kluczowa technika:** pivot points, *„czekaj na potwierdzenie, nie antycypuj"*; piramidowanie zyskownych pozycji
- **→ Imperium:** Senat (potwierdzenie przed wejściem), skalowanie pozycji w zysku

### Larry Williams ⭐⭐⭐
- **Styl:** krótkoterminowy, sezonowość + COT
- **Kluczowa technika:** Commitment of Traders (pozycjonowanie dużych graczy) jako flow
- **→ Imperium:** RADAR-03 (przepływ kapitału), PSY-02 (long/short ratio)

### Mark Minervini ⭐⭐⭐
- **Styl:** momentum akcji (SEPA)
- **Kluczowa technika:** trend template (cena > MA50 > MA150 > MA200), wejście na sile
- **→ Imperium:** struktura EMA w MTF konfluencji (W-384, `_kierunek_trendu`)

---

## 4. PSYCHOLOGIA & DYSCYPLINA

### Mark Douglas ⭐⭐⭐⭐
- **Książka:** BIB-016 *Trading in the Zone*
- **Kluczowa myśl:** myślenie probabilistyczne; każda transakcja to jedna z serii, nie wyrok
- **→ Imperium:** podejście statystyczne (nie „ta jedna transakcja"), DSR/PBO

### Brett Steenbarger ⭐⭐⭐
- **Książka:** BIB-004 *Psychology of Trading*
- **Kluczowa myśl:** trader jako sportowiec — rutyna, przegląd, kontrola stanu
- **→ Imperium:** PSY neurony, dziennik/LOG_ZMIAN jako przegląd

### Daniel Kahneman ⭐⭐⭐⭐
- **Książka:** BIB-017 *Thinking Fast and Slow*
- **Kluczowa myśl:** System 1 (szybki, emocjonalny) vs System 2 (wolny, logiczny); błędy poznawcze
- **→ Imperium:** **cały sens automatyzacji** — rój = System 2 bez emocji; Senat eliminuje impulsywność

### Ed Seykota ⭐⭐⭐⭐
- **Styl:** systematic trend, pionier komputerowego tradingu
- **Cytat:** *„Tnij straty, tnij straty, tnij straty — i pozwól zyskom rosnąć."*
- **→ Imperium:** bezpieczniki Z-*, trailing wyjścia

---

## 5. KRYPTO-NATYWNI

### Arthur Hayes (BitMEX) ⭐⭐⭐⭐
- **Wkład:** perpetual swap, basis trade, mistrz funding
- **→ Imperium:** PSY-01 funding jako sygnał (szczegóły → dział LEW)

### Su Zhu / Kyle Davies (3AC) ⚠️ ⭐ (negatywny)
- **Wkład:** jak NIE robić — nadmierny lewar, brak hedgingu, bankructwo 2022
- **→ Imperium:** uzasadnienie nienaruszalnych limitów i HALT (dział RSK)

### Anonimowi on-chain whale'e ⭐⭐⭐
- **Wkład:** smart money tracking (Nansen, Arkham)
- **→ Imperium:** OC neurony (netflow, MVRV), RADAR-03 przepływ

---

## 6. NEGATYWNE WZORCE (czego NIE robić)
| Przykład | Błąd | Lekcja zakodowana |
|----------|------|-------------------|
| 3AC | over-leverage + brak hedge | twarde limity, HALT |
| LTCM | nadmierna pewność modelu + lewar | DSR/PBO, pokora wobec ogonów (Mandelbrot, BIB-009) |
| Nick Leeson | brak nadzoru, ukrywanie strat | transparentny LOG, audyt |
| Retail FOMO | wejście na szczycie hype | Pi-Cycle kill-switch (Z-07), fear&greed (PSY-03) |

---

## 7. MAPA: TRADER → MODUŁ IMPERIUM

| Moduł Imperium | Inspiracja (trader) |
|----------------|---------------------|
| Architektura roju (wiele słabych sygnałów) | Simons (Renaissance) |
| Gubernator / dynamiczny sizing | Druckenmiller, Thorp (Kelly) |
| RADAR-01 trend filter | Paul Tudor Jones (200 MA) |
| Senat (próg pewności) | Livermore, Soros |
| Reguła 6% / HALT / Z-* | PTJ, Seykota, Hite, Larry Hite |
| Dekorelacja (Prawo XVI) | Asness (faktory), Simons |
| Kointegracja par | Ernie Chan |
| MTF konfluencja (EMA stack) | Minervini (trend template) |
| Automatyzacja bez emocji | Kahneman (System 1 vs 2) |
| PSY-01 funding | Arthur Hayes |
| Pokora wobec ogonów | Mandelbrot, LTCM (anty-wzór) |

---

## 8. ŹRÓDŁA
- BIB-015 Elder — *New Trading for a Living*
- BIB-028 Narang — *Inside the Black Box* (systematic)
- BIB-010/011 Chan — *Quantitative/Algorithmic Trading*
- BIB-016 Douglas, BIB-017 Kahneman, BIB-004 Steenbarger (psychologia)
- *Market Wizards* (Schwager) — kanon wywiadów z traderami [⚠️ niezweryfikowany w bibliotece — kandydat do dodania]
- Powiązane działy: **LEW**, **RSK**, **PSY**, **STR**
