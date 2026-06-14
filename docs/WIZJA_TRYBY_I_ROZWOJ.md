# 🔱 WIZJA: TRYBY OPERACYJNE + ROZWÓJ POTENCJAŁU

> **Stan na:** 2026-06-14 · **Status:** wizja Cezara + propozycja architektury (do decyzji, Prawo XVIII)
> **Cel nadrzędny:** największy zysk przy płynnym powiększaniu kapitału — obracać kapitałem,
> dorzucać zysk do zamówień, gonić za płynnością, uciekać przed likwidacją. Wszystko
> płynne, skalibrowane, zsynchronizowane przez Bramę kodową (zero halucynacji modeli).

## 🎯 TRYB 1 — NAJLEPSZY Z NAJLEPSZYCH (Łowca Okazji) — BUDOWANY ✅

Cel: **najlepszy win-rate i największy zysk** na futures z lewarem (auto-kalibracja),
działający na WSZYSTKICH interwałach (skalp/swing/invest), płynnie dobierający neurony
i strategie z bazy, z auto-uczeniem i auto-modyfikacją.

**Potok (zaimplementowany w tej sesji):**
1. **Skan koszyka** — SkanerOkazji rankuje wszystkie waluty (W-316)
2. **Selekcja TOP-N** — tylko najmocniejsze okazje wchodzą (W-317)
3. **Conviction sizing** — większa stawka na mocniejszej okazji (W-318)
4. **Compounding** — zysk → pula łupów → większe pozycje (W-319)
5. **Detektor górek/dołków** — Z-05 dwukierunkowy: szczyt→SHORT, dołek→LONG (W-315)
6. **Filtry przeżycia** — Asymetria Reżimu (W-314), breaker krzywej, reguła 6%

**Dowód (9 lat, 5 par):** +64 976$ vs baseline +52 789$ (+23%, mniej trade'ów, wszystkie pary +).

**Czego brakuje do pełni Trybu 1:**
- 🟢 **Interwał 1h — JEST i działa (W-320)**: mamy ~76k barów 1h/parę (5 par,
  `dane/godzinowe/`) — czytnik je obsługuje, test ładowania zielony, symulacja 1h w toku.
  (Wcześniejsza diagnoza „tylko 4H/1D" była błędna — Prawo XV: dane leżały nieużyte.)
- 🔴 **Interwały bardzo krótkie (1m/5m/15m)** — `dane/minutowe/` puste; bez nich skalp
  nie widzi najlepszego momentu w obrębie godziny. **Najwyższy priorytet danych.**
- 🟡 Neurony bazowe per interwał — które neurony są najlepsze dla danego TF, kalibracja składu roju per interwał.
- 🟡 Bayesian P(sukces) per setup (skalibrowane prawdopodobieństwo, nie tylko „pewność").

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

**Wymaga:** AdapterKronikarz live (zdarzenia), neurony sentymentu/newsów (NEWS-01 + feed),
detektor dna multi-TF, realnej egzekucji spot.

## 🔐 TRYB 3 — PRZEŁĄCZNIK Z AUTORYZACJĄ (propozycja) 🔵

Płynne przełączanie trybów (NAJLEPSZY ↔ BILANS ↔ OBRONA), ale zmiany **wrażliwe**
(realny kapitał, włączenie lewara, zmiana trybu na żywo) wymagają **hasła/autoryzacji Cezara**:
- `os.getenv("IMPERIUM_AUTH")` — hasło z env (NIGDY w kodzie, zgodnie z zasadą bezpieczeństwa).
- Tryb może przełączać się AUTOMATYCZNIE wg reżimu rynku (risk-on → NAJLEPSZY, risk-off →
  OBRONA/BILANS), ale wejście w tryb lewarowany na żywo = brama autoryzacji.
- Log każdej zmiany trybu (audytowalność).

## 📜 PROPOZYCJA NOWYCH ZASAD (rozwój potencjału)

- **Prawo XXII — Płynność ponad balastem:** żaden moduł nie wchodzi do gorącej pętli,
  jeśli nie wnosi mierzalnej informacji (Prawo XVI) — system ma być lekki i szybki, nie obciążony.
- **Prawo XXIII — Prześwietlenie przed wejściem:** zanim Imperium zagra NOWĄ walutą, musi
  mieć jej kartę: typ, twórca, zaufanie, płynność, ryzyko scamu (tabela narzędzi niżej).
- **Prawo XXIV — Ucieczka przed likwidacją:** każdy trade lewarowany ma policzoną cenę
  likwidacji i bufor; pogoń za płynnością nigdy nie kosztem ryzyka likwidacji (już częściowo: kalkulator_lewara).
- **Prawo XXV — Obracanie kapitałem:** zysk płynnie reinwestowany (compounding W-319),
  ale z sufitem ekspozycji per okazja (anti-tail) — chciwość pod kontrolą breakera.

## 🔍 NARZĘDZIA DO PRZEŚWIETLANIA WALUT (research 2026-06-14, darmowe API)

> Cel: zanim wejdziemy w nową walutę — automatyczna „karta waluty" (Prawo XXIII).
> Wszystkie poniższe mają DARMOWE API REST/JSON (system lokalny).

| # | Narzędzie | Co dostarcza | Darmowe API | Rola |
|---|-----------|--------------|-------------|------|
| 1 | **CoinGecko** (api.coingecko.com) | market cap, kategoria, opis, data startu, twórcy, tickers/płynność | ✅ 10k kredytów/mc | rdzeń metadanych + płynność |
| 2 | **GoPlus Security** (gopluslabs.io) | honeypot, podatki buy/sell, uprawnienia ownera, rozkład holderów (EVM+Solana) | ✅ bez klucza | twarda brama ryzyka scamu |
| 3 | **RugCheck** (api.rugcheck.xyz) | safety score Solana, LP locked/burned, mint authority | ✅ bez klucza | ryzyko memecoinów Solana |
| 4 | **DefiLlama** (api-docs.defillama.com) | TVL, wolumen DEX, fees, revenue (350+ chainów) | ✅ bez klucza, bez limitu | fundamenty (realny projekt vs pusty) |
| 5 | **GeckoTerminal** (geckoterminal.com/api) | płynność puli DEX dla świeżych tokenów | ✅ darmowy | płynność on-chain pre-listing |

**Pominąć na start** (straciły darmowe API): LunarCrush (sentyment — tylko płatne),
CryptoPanic (newsy — darmowy plan wycofany od 04.2026). Sentyment dodać później.

**Próg decyzyjny karty waluty:** GoPlus/RugCheck = bramka twarda (czerwony flag → STOP),
CoinGecko+DefiLlama = ocena jakości (cap/płynność/TVL). To nowy adapter `AdapterKartaWaluty`.

## 🗺️ KOLEJKA ROZWOJU (priorytet)

1. **Dane bardzo krótkich interwałów** (1m/5m/15m) — 1h JUŻ wpięty (W-320); brakuje sub-godzinnych do skalpu.
2. **AdapterKronikarz live** + Bayesian P(sukces) — Tryb 1 i 2.
3. **AdapterKartaWaluty** (CoinGecko+GoPlus+DefiLlama) — Prawo XXIII, gra na wielu walutach.
4. **Tryb BILANS** (spot/invest opportunity) + przełącznik z autoryzacją.
5. **Sprzątanie kodu** (audyt zdrowia — osobny raport): usunąć martwe/zduplikowane, scalić, odchudzić.
6. **Rozbudowa roju** z katalogu (200+ neuronów) per interwał, z pomiarem dekorelacji (Prawo XVI).

> Sekcje „wynik pełnej symulacji" i „audyt zdrowia kodu" — uzupełniane po zakończeniu pomiarów.
