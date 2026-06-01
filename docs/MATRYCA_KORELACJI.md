# 🏛️ MATRYCA KORELACJI — IMPERIUM

> *"Roma non uno die aedificata est"* — Rzym nie powstał w jeden dzień. Tak samo ta matryca.

## 🧩 Koncept Kostki Rubika

Wyobraź sobie **Kostkę Rubika**. Każdy ruch obraca jedną oś, a kolory mieszają się w nowe układy. Tak właśnie działa IMPERIUM.

Każdy **wskaźnik** × **interwał** × **typ zagrania** × **reżim rynku** × **waga ważności** tworzy unikalną kombinację. Liczba możliwych konfiguracji jest **ogromna** — większa niż liczba atomów w obserwowalnym wszechświecie, dokładnie jak przestrzeń ruchów w Go, którą okiełznał AlphaGo.

Nie da się policzyć tego ręcznie. Ale da się **uporządkować w spójny system**, który:
1. Rejestruje każdą kombinację jako klucz,
2. Mierzy jej historyczną skuteczność,
3. Stopniowo uczy się, **które obroty kostki układają zwycięski wzór**.

Ten dokument to **SZABLON / SCHEMAT** tej nauki. Jest to **żywy dokument** — będzie wypełniany prawdziwymi danymi w miarę jak system się uczy (Faza 4: Samouczenie).

---

## 🎲 WYMIARY KOSTKI (Osie Rotacji)

Pięć osi, które obracają się niezależnie i tworzą każdą konfigurację bojową Legionów.

| Oś | Nazwa | Wartości | Opis |
|----|-------|----------|------|
| **Oś 1** | 📊 Wskaźnik | 157 dostępnych | Pełny arsenał wskaźników technicznych, on-chain i futures |
| **Oś 2** | ⏱️ Interwał | M1, M5, M15, 1H, 4H, 1D, 1W | Skala czasowa obserwacji |
| **Oś 3** | ⚔️ Typ zagrania | Scalp / Swing / Invest / Leverage | Charakter operacji bojowej |
| **Oś 4** | 🌊 Reżim rynku | Trend ↑ / Trend ↓ / Konsolidacja / Wysoka zmienność | Aktualny stan pola bitwy |
| **Oś 5** | ⚖️ Waga ważności | 1–10 (dynamiczna) | Jak mocno dany sygnał wpływa na decyzję — zmienna w czasie |

### Mapowanie Legionów na osie

| Legion | Typ zagrania | Główne interwały |
|--------|--------------|------------------|
| 🐎 **Legio X Equestris** | Scalp | M1 – M15 |
| ⚡ **Legio XII Fulminata** | Swing | 4H – 1D |
| 🏛️ **Legio III Augusta** | Invest / Spot | 1D – 1W |
| 🛡️ **Legio VI Ferrata** | Leverage / Futures | dowolne + Funding/OI |

---

## 🔑 SYSTEM NUMERACJI I KLUCZY

Każdy wskaźnik otrzymuje **klucz bojowy** w formacie:

```
[LITERA KATEGORII] - [NUMER 001-157] - W[WAGA 1-10]
```

**Przykład:** `M-001-W7` = wskaźnik Momentum nr 001 z wagą ważności 7.

### Litery kategorii

| Litera | Kategoria | Opis |
|--------|-----------|------|
| **M** | Momentum | Pęd, siła ruchu |
| **T** | Trend | Kierunek dominujący |
| **V** | Volatility (Zmienność) | Rozrzut, ryzyko |
| **F** | Flow / Volume | Przepływ, wolumen |
| **O** | On-Chain | Dane blockchainowe |
| **L** | Leverage / Futures | Dźwignia, kontrakty |

> ⚠️ Waga w kluczu jest **zmienna w czasie** i zależna od warunków rynku. `M-001-W7` dziś może jutro być `M-001-W4`, jeśli wskaźnik zacznie zawodzić w danym reżimie.

### Przykładowa tablica kluczy (15 wskaźników)

| Nazwa | Numer | Kategoria | Klucz bazowy | Główne zastosowanie |
|-------|-------|-----------|--------------|---------------------|
| RSI | 001 | M | `M-001-W7` | Wykupienie / wyprzedanie |
| MACD | 002 | M | `M-002-W7` | Pęd i przecięcia |
| EMA | 003 | T | `T-003-W8` | Kierunek trendu, golden/death cross |
| Supertrend | 004 | T | `T-004-W7` | Filtr trendu, stop dynamiczny |
| Ichimoku | 005 | T | `T-005-W6` | Pełny obraz trendu, chmura |
| ATR | 006 | V | `V-006-W6` | Pomiar zmienności, sizing |
| Bollinger Bands | 007 | V | `V-007-W7` | Ekstrema, ściśnięcie |
| VWAP | 008 | F | `F-008-W7` | Średnia ważona wolumenem |
| OBV | 009 | F | `F-009-W6` | Akumulacja / dystrybucja |
| CVD | 010 | F | `F-010-W7` | Delta wolumenu, dywergencje |
| MVRV | 011 | O | `O-011-W8` | Wycena vs koszt nabycia |
| NUPL | 012 | O | `O-012-W8` | Niezrealizowane zyski/straty |
| Funding Rate | 013 | L | `L-013-W7` | Koszt utrzymania pozycji |
| Open Interest (OI) | 014 | L | `L-014-W7` | Zaangażowany kapitał |
| Liquidation Heatmap | 015 | L | `L-015-W6` | Klastry likwidacji, magnesy cenowe |

> 🏛️ Pełny arsenał liczy **157 wskaźników** — powyżej Centurioni reprezentujący swoje kohorty.

---

## 🤝 MACIERZ KORELACJI SYGNAŁÓW

Gdy sygnały **nakładają się i potwierdzają**, pewność rośnie. To skoordynowany atak Legionów.

| Kombinacja | Warunek | Wniosek | Siła |
|------------|---------|---------|------|
| RSI + Bollinger + OBV | RSI<30 + dolne pasmo BB + OBV rośnie | 🟢 Silny LONG (odbicie) | **8/10** |
| EMA + MACD + RVOL | Golden cross + MACD>0 + RVOL>1.5 | 🟢 Potwierdzony trend wzrostowy | **9/10** |
| Funding + OI + RSI | Funding>0.05% + OI rośnie + RSI>75 | 🔴 Ostrzeżenie long squeeze → SHORT | **7/10** |
| MVRV + Netflow + NUPL | MVRV<1 + Exchange Netflow ujemny + NUPL<0 | 🟢 Strefa akumulacji INVEST | **9/10** |
| MVRV + NUPL + Pi Cycle | MVRV>3.7 + NUPL>0.75 + Pi Cycle Top | 🔴 Szczyt cyklu, wyjście | **9/10** |
| CVD + Volume Profile | CVD dywergencja + POC odrzucony | 🟡 Odwrócenie | **7/10** |
| Liq Heatmap + OI | Klaster likwidacji powyżej + OI rośnie | 🟢 Magnes cenowy w górę | **6/10** |
| Supertrend + EMA + ATR | Supertrend ↑ + cena>EMA200 + ATR malejący | 🟢 Stabilny trend, niskie ryzyko | **8/10** |
| Ichimoku + MACD | Cena nad chmurą + MACD przecięcie ↑ | 🟢 Potwierdzony swing LONG | **8/10** |
| VWAP + CVD + Volume | Cena odbija od VWAP + CVD rośnie + wzrost wolumenu | 🟢 Wejście intraday LONG | **7/10** |
| Funding + OI (spadek) | Funding ujemny + OI maleje + RSI<25 | 🟢 Kapitulacja, odbicie short squeeze | **7/10** |
| Death cross + Netflow | Death cross + Exchange Netflow dodatni (napływ na giełdy) | 🔴 Dystrybucja, presja podażowa | **8/10** |

---

## ⚔️ MACIERZ KONFLIKTÓW

Gdy sygnały **przeczą sobie**, pewność spada. Mądry wódz **czeka** — *festina lente* (spiesz się powoli).

| Sygnał A | vs | Sygnał B | → Rozwiązanie |
|----------|----|----------|----|
| RSI mówi LONG (wyprzedanie) | vs | Funding Rate ekstremalny dodatni | ⏸️ **CZEKAJ** — ryzyko long squeeze |
| Trend EMA LONG | vs | On-chain: dystrybucja wielorybów | 📉 **Zmniejsz pozycję** — smart money wychodzi |
| MACD bullish na 1H | vs | Trend spadkowy na 1D | 🧭 **Priorytet wyższy interwał** — tylko scalp, nie swing |
| Bollinger ściśnięcie (cisza) | vs | OI gwałtownie rośnie | ⚠️ **Przygotuj się na wybicie** — kierunek nieznany, ustaw oba scenariusze |
| Cena nad VWAP | vs | CVD dywergencja niedźwiedzia | 🟡 **Redukuj zaufanie** — ruch bez wsparcia delty |
| Golden cross | vs | MVRV>3.7 (przewartościowanie) | 🛑 **Nie otwieraj INVEST** — późny cykl, tylko krótki swing |
| Liq Heatmap magnes w górę | vs | Death cross + RSI<70 | 🤔 **Mały LONG taktyczny** do klastra, potem wyjście |
| Supertrend LONG | vs | Wysoka zmienność (ATR skok) | 📏 **Zmniejsz dźwignię** — szerszy stop, mniejszy size |

---

## 🌊 REŻIMY RYNKU

Pole bitwy zmienia charakter. W każdym reżimie **inne Legiony i inne wskaźniki dominują**.

| Reżim | Symbol | Dominujące wskaźniki | Strategia | Faworyzowany Legion |
|-------|--------|----------------------|-----------|---------------------|
| **Trend wzrostowy (bull)** | 📈 | EMA, MACD, Supertrend, Ichimoku | Podążaj za trendem, kupuj korekty | XII Fulminata, VI Ferrata |
| **Trend spadkowy (bear)** | 📉 | On-chain (MVRV/NUPL), Funding, Netflow | Ochrona kapitału, krótkie shorty, akumulacja na dnie | III Augusta (DCA), VI Ferrata (short) |
| **Konsolidacja (range)** | ↔️ | Bollinger, RSI ekstrema, Volume Profile, VWAP | Graj od krawędzi do krawędzi | X Equestris |
| **Wysoka zmienność (volatile)** | ⚡ | ATR, Liquidation Heatmap, OI | Redukcja dźwigni, szersze stopy, ostrożność | wszystkie — tryb obronny |

---

## ⚖️ WAGI DYNAMICZNE

> 🧠 **Wagi NIE są stałe.** To serce uczącego się Imperium.

Zasady ewolucji wag:

1. **Waga bazowa** — każdy wskaźnik startuje z wagą przypisaną na podstawie wiedzy eksperckiej (patrz tabela kluczy).
2. **Waga ROŚNIE** ⬆️ — gdy wskaźnik **historycznie trafia** w danym reżimie i interwale.
3. **Waga MALEJE** ⬇️ — gdy wskaźnik **zawodzi** (fałszywe sygnały, niska trafność).
4. **Kontekstowość** — ten sam wskaźnik ma **różne wagi** w różnych reżimach. RSI może mieć wagę 8 w konsolidacji, ale 4 w silnym trendzie.

To jest **fundament samouczenia (Faza 4)**.

### Format zapisu skuteczności (szablon)

> System zapisuje rekordy w postaci:
> *"Wskaźnik **X** w interwale **Y** w reżimie **Z** miał trafność **N%** na próbie **K** sygnałów."*

| Wskaźnik | Interwał | Reżim | Trafność | Próba | Waga aktualna | Trend wagi |
|----------|----------|-------|----------|-------|---------------|------------|
| RSI | M15 | Konsolidacja | _do uzupełnienia_ | _–_ | W7 | _–_ |
| MACD | 4H | Trend ↑ | _do uzupełnienia_ | _–_ | W7 | _–_ |
| MVRV | 1W | Trend ↓ | _do uzupełnienia_ | _–_ | W8 | _–_ |
| Funding Rate | 1H | Wysoka zmienność | _do uzupełnienia_ | _–_ | W7 | _–_ |

> 📝 Tabela wypełniana automatycznie przez system w Fazie 4.

---

## ₿ WPŁYW BTC NA RYNEK

> 👑 *Caesar dux mundi* — BTC jest Cezarem rynku. Większość altów podąża za nim.

Zasady dominacji:

- **BTC prowadzi** — gdy BTC się rusza, większość altcoinów podąża (często z opóźnieniem i mnożnikiem beta).
- **Wyjątek: sezon alt (altseason)** — alty przejmują inicjatywę, kapitał rotuje z BTC do altów. Rzadziej **ETH przejmuje kontrolę** jako lider rotacji.
- **Badanie historyczne** — należy analizować **każdą minutę** wpływu BTC na alty: opóźnienie korelacji, współczynnik beta, momenty zerwania korelacji.

### Tabela: faza rynku → wpływ BTC na alty

| Faza rynku | Zachowanie BTC | Wpływ na alty | Strategia altów |
|------------|----------------|---------------|-----------------|
| 📈 BTC pompuje | Silny wzrost | Alty stoją / lekko spadają (kapitał w BTC) | ⏸️ Czekaj na rotację |
| ↔️ BTC konsoliduje (wysoko) | Stabilny po wzroście | 🚀 Altseason — alty eksplodują | 🟢 Agresywne LONG alty |
| 📉 BTC spada | Silny spadek | Alty spadają mocniej (beta>1) | 🔴 Wyjście / hedge |
| 🩸 BTC krach | Gwałtowny dump | Alty -50%+, masowe likwidacje | 🛑 Cash / akumulacja blue chips |
| 🌅 BTC dno + odbicie | Stabilizacja | Alty z opóźnieniem, najpierw BTC dominacja rośnie | 🏛️ DCA BTC, potem rotacja |

---

## 📜 POWIĄZANIE Z HISTORIĄ

> *"Historia magistra vitae"* — Historia nauczycielką życia.

Każde **wydarzenie historyczne** ma swój powtarzalny **wzorzec**. System ma rozpoznawać:

> 🔮 *"To wygląda jak sytuacja z [data]..."*

### Macierz zdarzeń historycznych (szablon)

| Wydarzenie | Data (przykł.) | Wzorzec przed | Reakcja rynku | Czas trwania | Powtarzalność |
|------------|----------------|---------------|---------------|--------------|---------------|
| Halving BTC | _do uzupełnienia_ | Akumulacja, MVRV<1 | Bull 12-18 mies. po | _–_ | ⭐⭐⭐⭐ |
| Krach (np. COVID, LUNA, FTX) | _do uzupełnienia_ | OI ekstremalny, Funding wysoki | Kaskada likwidacji, -50% | _–_ | ⭐⭐⭐ |
| ETF Approval | _do uzupełnienia_ | Spekulacja, napływy | "Sell the news" lub rajd | _–_ | ⭐⭐⭐ |
| Szczyt cyklu | _do uzupełnienia_ | MVRV>3.7, NUPL>0.75, Pi Cycle Top | Bessa -70%+ | _–_ | ⭐⭐⭐⭐ |
| Dno cyklu | _do uzupełnienia_ | MVRV<1, kapitulacja, NUPL<0 | Akumulacja, odwrócenie | _–_ | ⭐⭐⭐⭐ |

> 📝 Szablon do późniejszego budowania bazy wzorców historycznych. Każdy nowy epizod zasila pamięć Imperium.

---

## 🏛️ Status dokumentu

> ⚠️ **DOKUMENT ŻYWY (LIVING TEMPLATE).**
> Powyższe tabele to **schemat startowy**. W miarę jak Imperium gromadzi dane i przechodzi do **Fazy 4 (Samouczenie)**, wagi, trafności i wzorce będą **wypełniane rzeczywistymi danymi**. Kostka będzie się obracać, aż znajdzie zwycięskie wzory.

*Alea iacta est* — kości zostały rzucone. 🎲

---
*IMPERIUM — System Tradingowy AI | Matryca Korelacji v1.0 (szablon)*
