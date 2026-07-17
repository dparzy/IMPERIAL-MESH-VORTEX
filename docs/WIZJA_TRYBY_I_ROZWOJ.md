---
kategoria: CONSILIUM
typ: zywy
wlasciciel: imperium/koloseum/skaner_okazji.py, imperium/legiony/rejestr.py
stan_na: 2026-07-17
powod_istnienia: "Wizja Cezara na 3 tryby operacyjne systemu (NAJLEPSZY/BILANS/OBRONA) plus katalog darmowych API do 'prześwietlania' nowych walut przed wejściem — z weryfikacją, co z wizji już stoi w kodzie"
dublet_rozstrzygniety: docs/KATALOG_NEURONOW.md — Katalog jest SPISEM neuronów (co robi każdy klucz); tutaj żyje WIZJA trybów i kolejka rozwoju (dokąd zmierzamy). Podział ról świadomy, nie dublet treści.
---
# 🔱 WIZJA: TRYBY OPERACYJNE + ROZWÓJ POTENCJAŁU

> **Status:** wizja Cezara + propozycja architektury (do decyzji, Prawo XVIII).
> **Cel nadrzędny:** największy zysk przy płynnym powiększaniu kapitału — obracać kapitałem,
> dorzucać zysk do zamówień, gonić za płynnością, uciekać przed likwidacją. Wszystko
> płynne, skalibrowane, zsynchronizowane przez Bramę kodową (zero halucynacji modeli).

**Weryfikacja wobec kodu: 2026-07-17** (`stan_na`). Wizja ma prawo wybiegać w przód, ale
twierdzenia o STANIE muszą być prawdziwe — poniżej ✅ = zmierzone w kodzie, 🔴 = nadal plan.
Poprzednia wersja (2026-06-14) podawała cztery nieprawdziwe stany — sprostowane niżej.

## 🎯 TRYB 1 — NAJLEPSZY Z NAJLEPSZYCH (Łowca Okazji) — ZBUDOWANY ✅

Cel: **najlepszy win-rate i największy zysk** na futures z lewarem (auto-kalibracja),
działający na WSZYSTKICH interwałach (skalp/swing/invest), płynnie dobierający neurony
i strategie z bazy, z auto-uczeniem i auto-modyfikacją.

**Potok — zweryfikowany w kodzie:**
1. ✅ **Skan koszyka** — `SkanerOkazji` rankuje waluty ([`skaner_okazji.py`](../imperium/koloseum/skaner_okazji.py), W-316)
2. ✅ **Selekcja TOP-N** — tylko najmocniejsze okazje wchodzą (W-317)
3. ✅ **Conviction sizing** — [`pretorianie/sizing_przekonania.py`](../imperium/pretorianie/sizing_przekonania.py) (W-318)
4. ✅ **Compounding** — zysk → pula łupów → większe pozycje (W-319, `koloseum/backtest.py`)
5. ✅ **Detektor górek/dołków** — Z-05 dwukierunkowy: szczyt→SHORT, dołek→LONG (W-315)
6. ✅ **Filtry przeżycia** — Asymetria Reżimu (W-314), breaker krzywej, reguła 6%

**Dowód z 2026-06-14 (9 lat, 5 par):** +64 976$ vs baseline +52 789$ (+23%, mniej trade'ów,
wszystkie pary +). To pomiar swojego czasu — nie odświeżany, patrz `docs/migawki/`.

### 📊 Dane — stan ZMIERZONY 2026-07-17 (sprostowanie)

Poprzednia wersja twierdziła: *„🔴 Interwały bardzo krótkie (1m/5m/15m) — `dane/minutowe/`
puste; bez nich skalp nie widzi najlepszego momentu. **Najwyższy priorytet danych**"*.
**To była nieprawda** — i to dokładnie ta klasa błędu, którą ten sam dokument opisał akapit
wyżej przy 1h („dane leżały nieużyte", Prawo XV). Powtórka tej samej pomyłki, tylko piętro niżej.

| Katalog | Realnie (zmierzone) | Zakres | Werdykt |
|---|---|---|---|
| `dane/minutowe/` | **14 par, ~14,9 mln barów 1m** | 2019-07-05 → **2022-07-27** | ✅ SĄ · ⚠️ luka 4 lata do dziś |
| `dane/godzinowe/` | **15 par** (nie 5), 47k–76k barów | 2017-08-17 → 2026-06-18 | ✅ świeże (MATIC urwany 2024-09-09) |

🚨 **Prawo XV — utrata potencjału:** `wczytaj_csv("dane/minutowe/...", interwal="1m")` działa
**bez żadnej zmiany kodu** (dowód runtime 2026-07-17: AVAXUSDT → 145 185 barów w 1,1 s,
chronologia rosnąca, pełne OHLCV + tradecount — format CryptoDataDownload identyczny z 1h,
czytnik normalizuje wielkość liter). Mimo to **żaden moduł nie czyta `dane/minutowe/`** —
zero trafień w `imperium/` i `narzedzia/`. ~14,9 mln barów leży nieużytych.

**Ale to nie jest „wpiąć i grać" (kandydat ≠ prawda):** dane 1m kończą się **2022-07-27**.
Nadają się do **backtestu skalpu na historii 2019–2022** (COVID-krach, hossa 2021, bessa 2022
— materiał na testy reżimowe), **nie** do skalpu live. Do live trzeba dociągnąć świeże 1m.
Priorytet nie brzmi więc „zdobyć dane 1m", tylko: **(a) wpiąć istniejące do backtestu,
(b) dociągnąć świeże do live**.

**Czego jeszcze brakuje do pełni Trybu 1:**
- 🟡 Neurony bazowe per interwał — który skład roju jest najlepszy dla danego TF.
- 🟡 Bayesian P(sukces) per setup — skalibrowane prawdopodobieństwo, nie tylko „pewność".
  Infrastruktura kalibracji częściowo stoi: Sybilla mierzy Brier i krzywą kalibracji
  ([`ksiegi_sybillinskie.py`](../imperium/biblioteki/ksiegi_sybillinskie.py)), ale dotyczy
  proroctw Imperium o SOBIE, nie P(sukces) pojedynczego setupu.

## 💰 TRYB 2 — BILANS (Najlepsza Okazja Spot/Invest) — PROPOZYCJA 🔵

Cel: wejście w **najlepszym momencie** nie na lewarze, lecz na **spocie/inwestycji** —
akumulacja na dnie, wyjście blisko szczytu/ATH. Mniejsze ryzyko, długi horyzont, budowa pozycji.

**Mechanika (proponowana):**
- Ten sam skaner okazji, ale **filtr na ekstrema długoterminowe** (cena nisko względem
  historii, dno potwierdzone na WIELU interwałach + wszystkie kategorie neuronów zgodne).
- Wykorzystanie **danych zewnętrznych** (newsy, sentyment, zdarzenia Augura/Kronikarza) —
  „czy historycznie podobna sytuacja dała wzrost?" (event-study, prob_wzrostu).
- **Predykcja kierunku z wysoką pewnością**: pompa wzrośnie jeszcze / dump blisko maks/ATH /
  cena blisko min → kupuj w dołku (spodziewany lekki spadek + odbicie).
- Brak lewara (spot 1×) lub minimalny → przetrwanie czarnych dni (np. 10 X — „wielki piątek"
  krach; system MUSI takie dni rozpoznawać i NIE łapać noża, a kupować dopiero kapitulację).

**Czego wymaga — sprostowanie 2026-07-17:** poprzednia wersja pisała „Wymaga: AdapterKronikarz
live (zdarzenia), neurony sentymentu/newsów (NEWS-01 + feed)". **Oba już istnieją:**
- ✅ `AdapterKronikarz` — [`kronikarz_zdarzen.py:217`](../imperium/biblioteki/kronikarz_zdarzen.py)
  (Augur, W-289 v2), wpięty: zasila AUG-01 (`EVENT_*`) i `neurony/sesje.py`.
- ✅ Neurony newsów/sentymentu: NEWS-01…NEWS-04 + PSY-01…PSY-05 żyją w roju
  (<!-- LICZBA:neurony -->87<!-- /LICZBA --> neuronów łącznie; cenzus adapterów: 20/22 ŻYWE).

Realnie brakuje: 🔴 **detektora dna multi-TF** i 🔴 **egzekucji spot** (dziś tylko futures/paper).

## 🔐 TRYB 3 — PRZEŁĄCZNIK Z AUTORYZACJĄ — PROPOZYCJA 🔵

Płynne przełączanie trybów (NAJLEPSZY ↔ BILANS ↔ OBRONA), ale zmiany **wrażliwe**
(realny kapitał, włączenie lewara, zmiana trybu na żywo) wymagają **hasła/autoryzacji Cezara**:
- `os.getenv("IMPERIUM_AUTH")` — hasło z env (NIGDY w kodzie, zgodnie z zasadą bezpieczeństwa).
- Tryb może przełączać się AUTOMATYCZNIE wg reżimu rynku (risk-on → NAJLEPSZY, risk-off →
  OBRONA/BILANS), ale wejście w tryb lewarowany na żywo = brama autoryzacji.
- Log każdej zmiany trybu (audytowalność).

🔴 **Kodu nie ma** (zmierzone: brak `IMPERIUM_AUTH` i przełącznika trybów). Pokrewne, co stoi:
profile stylu SCALP/SWING/INVEST (W-323) i Gubernator (W-325) — sterują składem roju i
mnożnikiem ryzyka, ale nie są przełącznikiem trybu z autoryzacją.

## 📜 PROPOZYCJA NOWYCH ZASAD — ⚠️ ROZSTRZYGNIĘTA (numery zajęte)

Poprzednia wersja proponowała Prawa XXII–XXV. **Te numery zostały w międzyczasie nadane
czemu innemu** — propozycja jest martwa w tej formie (Imperium ma dziś 25 Praw):

| Numer | Proponowano tu (2026-06-14) | Realnie nadane (ZASADY_FUNDAMENTALNE) | Los propozycji |
|---|---|---|---|
| XXII | Płynność ponad balastem | **Dekorelacja przewagi, nie danych** | treść pokryta: Prawo XVI + XXII |
| XXIII | Prześwietlenie przed wejściem | **Niezawodność warunkowa** | 🔵 żywy postulat → AdapterKartaWaluty |
| XXIV | Ucieczka przed likwidacją | **Widoczność operacyjna** | ✅ zrealizowane w kodzie: `kalkulator_lewara` (cena likwidacji + bufor) |
| XXV | Obracanie kapitałem | **Przewaga konkurencyjna** | ✅ zrealizowane: compounding W-319 + breaker krzywej |

**Werdykt (Prawo XVIII):** nie nadajemy tych numerów ponownie. Dwie propozycje już żyją jako
KOD (nie potrzebują prawa), jedna jest pokryta istniejącymi prawami, a „Prześwietlenie przed
wejściem" zostaje **postulatem produktowym** (karta waluty niżej), nie nowym prawem — mnożenie
praw bez potrzeby to ten sam błąd co mnożenie dokumentów.

## 🔍 NARZĘDZIA DO PRZEŚWIETLANIA WALUT (research 2026-06-14, darmowe API)

> Cel: zanim wejdziemy w nową walutę — automatyczna „karta waluty".
> Wszystkie poniższe mają DARMOWE API REST/JSON (system lokalny).
> ⚠️ Dostępność API sprawdzona 2026-06-14 i **nieweryfikowana ponownie** — przed wpięciem
> potwierdź aktualny cennik (Prawo I: nie udajemy weryfikacji).

| # | Narzędzie | Co dostarcza | Darmowe API | Stan w kodzie |
|---|-----------|--------------|-------------|---------------|
| 1 | **CoinGecko** (api.coingecko.com) | market cap, kategoria, opis, data startu, twórcy, tickers/płynność | ✅ 10k kredytów/mc | 🔴 brak (jedynie wzmianka w `news_fetcher`) |
| 2 | **GoPlus Security** (gopluslabs.io) | honeypot, podatki buy/sell, uprawnienia ownera, rozkład holderów | ✅ bez klucza | 🔴 brak (0 trafień) |
| 3 | **RugCheck** (api.rugcheck.xyz) | safety score Solana, LP locked/burned, mint authority | ✅ bez klucza | 🔴 brak (0 trafień) |
| 4 | **DefiLlama** (api-docs.defillama.com) | TVL, wolumen DEX, fees, revenue | ✅ bez klucza, bez limitu | ✅ **wpięty, ale w INNEJ roli**: `adaptery/stablecoin.py` → K-03/K-04 (podaż stablecoinów jako sygnał makro), nie jako karta waluty |
| 5 | **GeckoTerminal** (geckoterminal.com/api) | płynność puli DEX dla świeżych tokenów | ✅ darmowy | 🔴 brak (0 trafień) |

**Próg decyzyjny karty waluty:** GoPlus/RugCheck = bramka twarda (czerwony flag → STOP),
CoinGecko+DefiLlama = ocena jakości (cap/płynność/TVL). To nowy adapter `AdapterKartaWaluty`
— 🔴 **nie istnieje** (0 trafień w kodzie).

**O sentymencie:** notatka „pominąć LunarCrush/CryptoPanic (płatne)" pochodzi z 2026-06-14.
Kampania IC Tier-1 (2026-07) poszła inną drogą i **zmierzyła** alternatywy: zwalidowano 4
źródła numeryczne (funding, podaż stablecoinów, DVOL, USD/DXY) → wpięto PSY-05, K-03, K-04
jako opt-in. Szczegóły: `docs/LOG_ZMIAN.md` (wpisy 2026-07) — tam żyje pomiar, nie tutaj.

## 🗺️ KOLEJKA ROZWOJU (zaktualizowana 2026-07-17)

1. **Skalp 1m: wpiąć TO, CO JEST** — 14 par × ~14,9 mln barów leży nieużyte, czytnik je czyta
   od ręki (Prawo XV). Backtest skalpu na 2019–2022; osobno dociągnąć świeże 1m do live.
2. 🔴 **AdapterKartaWaluty** (CoinGecko + GoPlus + DefiLlama) — gra na wielu walutach.
3. 🔴 **Bayesian P(sukces) per setup** — skalibrowane prawdopodobieństwo wejścia.
4. 🔴 **Tryb BILANS** (detektor dna multi-TF + egzekucja spot) + przełącznik z autoryzacją.
5. 🟡 **Sprzątanie kodu i dokumentów** — w toku: dług gnicia Tabularium (13 dokumentów).
6. 🟡 **Rozbudowa roju** per interwał, z pomiarem dekorelacji (Prawo XVI/XXII).

**Zdjęte z kolejki (zrobione):** ~~AdapterKronikarz live~~ — istnieje i jest wpięty (AUG-01).
