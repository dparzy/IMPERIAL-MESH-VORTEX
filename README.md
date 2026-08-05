---
kategoria: TABULA
typ: zywy
wlasciciel: imperium/legiony/rejestr.py
stan_na: 2026-08-05
powod_istnienia: "Wizytówka Imperium — podaje liczby wprost z kodu (neurony/testy/prawa), więc musi nadążać za rejestrem"
---
# 🏛️ IMPERIAL MESH VORTEX

> **Imperium Cezara Pixel** — autonomiczny, lokalny system tradingowy AI.
> Samouczący się rój neuronów, który poluje na rynku jak armia z jasnym łańcuchem dowodzenia.
> **Doktryna:** wojna = giełda; pierwszy front — **MEXC**; każdy order stawiany z myślą o zysku, a łup (zysk) finansuje lepszy budulec Imperium.

> **Stan na:** 2026-08-05 · **Testy:** `python tests/run_tests.py` (zielone) · **Rój:** <!-- LICZBA:neurony -->87<!-- /LICZBA --> neuronów / <!-- LICZBA:zwiadowcy -->15<!-- /LICZBA --> zwiadowców · **Faza bieżąca:** żywe źródło w [`docs/MANIFEST_KODU.md`](docs/MANIFEST_KODU.md) + [`docs/LOG_ZMIAN.md`](docs/LOG_ZMIAN.md) (nie duplikujemy tu rosnącej listy W-XXX — starzała się i kłamała).

---

## 🎯 Czym jest ten projekt

System tradingowy zbudowany na metaforze **Cesarstwa Rzymskiego** — od Cesarza (mózg AI) po Akwedukty (dane).
Inspirowany realnym projektem **DNSS** (rój 79 agentów AI), ale celuje wyżej: pełna lokalność, pełna autonomia, zero halucynacji.

**Główne założenia:**
- 🧠 Rój mikro-neuronów, które głosują, a Generał Legatus agreguje sygnał
- 💾 Działa lokalnie — matematykę liczy kod (Brama), AI tylko interpretuje
- 🔄 Strategie dobierane do reżimu rynku (wagi reżimowe)
- ✅ Zero halucynacji + jawność potencjału (Prawo XV)

---

## 📊 Co JEST zbudowane (kod + testy) — stan faktyczny

> Rozróżnienie obowiązkowe (Prawo I): **„katalog" = projekt na papierze, „kod" = działa i ma testy.**

| Komponent | Stan w kodzie |
|-----------|---------------|
| **Mikro-neurony** | **<!-- LICZBA:neurony -->87<!-- /LICZBA --> zaimplementowane** (<!-- LICZBA:neurony_aktywne -->81<!-- /LICZBA --> aktywnych: OHLCV momentum/trend/wolumen + SES-01/02 + 3 SMC + 6 kat. R + NEWS-01 + V-03 CVD + Z-01..05 brama obronna + X-27 Value + X-28 MTF Confluence + OC-05 WashTrading + **W-322: V-06 Delta Divergence, V-07 Anchored VWAP, VP-01 Volume Profile/VPOC, Z-06 Amihud Illiquidity, Z-07 Pi Cycle Top** + **W-329: RADAR-04 kaskada korelacyjna + RADAR-05 lead-lag BTC→alty** + **W-335: C-01 Cross-sectional Relative Strength** + **W-336: CP-01 CUSUM change-point** + **W-338: BOCPD-01 Bayesian change-point** + **W-339: N-02 Fractional Differentiation** + **PSY-05 DVOL strach opcji (opt-in --dvol, IC +0.16@7d) + K-03 Stablecoin flow (opt-in --stablecoin, IC +0.05..0.10) + K-04 USD strength (opt-in --usd, IC -0.27@30d)**; 4 czeka na on-chain API) |
| **Zwiadowcy Exploratores (EXP)** | **<!-- LICZBA:zwiadowcy -->15<!-- /LICZBA -->** (EXP-01..15; 13 aktywnych + 2 wyciszone do feedu) |
| **Brama Kalkulatora** | jedyne wejście do matematyki wskaźników (Prawo I) |
| **Budowniczy Wskaźników** | most: surowe bary → komplet wskaźników dla neuronów (z HA, Ichimoku, MACD…) |
| **Generał Legatus** | agregacja głosów + wagi reżimowe + odpalanie zwiadowców + ważenie IC opt-in (W-361, domyślnie OFF) |
| **Strategie (przepisy)** | **<!-- LICZBA:strategie -->20<!-- /LICZBA --> zmapowanych** na żywe klucze neuronów (`rejestr_strategii.py`; status **SZKIC** — przepisy, nie zwalidowane); Legatus dobiera TOP pasujące do sygnałów. Pełny opis: `docs/KATALOG_STRATEGII.md` |
| **Igrzyska / Koloseum** | rywalizacja i rangowanie neuronów |
| **Diagnostyka korelacji** | pomiar redundancji sygnałów (Prawo XVI) |
| **Status elitarny** | **<!-- LICZBA:elity -->18<!-- /LICZBA --> elitarnych** modułów mierzonych kryterium E1–E7 (Prawo XX): X-25, X-26, D-01 (3 neurony) + 15 zwiadowców |
| **Monte Carlo / Optymalizator / Pamięć Refleksyjna / Drift Adapter** | W-293/294/295/296 — antyoverfitting + samouczenie Brain |
| **Testy** | `python tests/run_tests.py` (bieżąca liczba — nie hardkodujemy, by nie przeterminować) ✅ |

**Katalog projektowy** (`docs/KATALOG_NEURONOW.md`) opisuje **299 neuronów** docelowo — to mapa drogowa, nie kod. Różnica (299 − 87) = 212 backlog do zbudowania (partiami, z pomiarem dekorelacji).

---

## 📂 Struktura projektu

| Folder / Plik | Zawartość |
|---------------|-----------|
| **[ZASADY_FUNDAMENTALNE.md](ZASADY_FUNDAMENTALNE.md)** | Konstytucja — **25 praw**, których zawsze przestrzegamy |
| **[CLAUDE.md](CLAUDE.md)** | Instrukcje stałe (czytane co sesję): Prawa XV–XVIII, bezpieczeństwo, git |
| **imperium/** | Żywy kod systemu (patrz mapa niżej) |
| **docs/** | Dokumentacja + katalogi projektowe (neurony, strategie, arsenał) |
| **tests/** | Testy bez zależności: `python tests/run_tests.py` |
| **archiwum/** | Surowa, oryginalna wizja |
| **kingdom-pixel/** | Archiwum poprzedniego projektu (NIE wchodzi do żywego systemu bez decyzji) |

---

## 🗺️ Mapa Imperium (realne organy w `imperium/` — liczby plików `.py` wstrzykiwane z żywego kodu)

| Organ | Rola | pliki `.py` |
|---|---|---|
| 👑 **cesarz/** | mózg decyzyjny, 5 Doradców, Pamięć Refleksyjna | <!-- LICZBA:organ_cesarz -->13<!-- /LICZBA --> |
| 🏛️ **senat/** | debata / konsensus (Byk / Niedźwiedź / Cenzor) | <!-- LICZBA:organ_senat -->2<!-- /LICZBA --> |
| ⚔️ **legiony/** | neurony + zwiadowcy + Generał Legatus + Radar | <!-- LICZBA:organ_legiony -->68<!-- /LICZBA --> |
| 🏟️ **koloseum/** | Dyrygent, PętlaLive, Backtest, Namiestnik, Legiony Cieni | <!-- LICZBA:organ_koloseum -->16<!-- /LICZBA --> |
| 🛡️ **pretorianie/** | bezpieczeństwo, kalkulator lewara, Praeda, **PORTITOR** (pre-flight u wrót) | <!-- LICZBA:organ_pretorianie -->19<!-- /LICZBA --> |
| 🏗️ **akwedukty/** | pipeline danych + adaptery API (Futures / F&G / CVD / News) | <!-- LICZBA:organ_akwedukty -->17<!-- /LICZBA --> |
| 🛤️ **drogi/** | API i egzekucja (NexusHub) | <!-- LICZBA:organ_drogi -->4<!-- /LICZBA --> |
| 🎨 **swiatynie/** | **PRAETORIUM** (Kwatera Główna Imperatora) + dashboard / wizualizacja / SPECULA świec | <!-- LICZBA:organ_swiatynie -->7<!-- /LICZBA --> |
| 📚 **biblioteki/** | pamięć W-360, MWU, Synapsy Reżimowe, Kronikarz, RAG | <!-- LICZBA:organ_biblioteki -->29<!-- /LICZBA --> |
| 👁️ **oczy/** | obserwatorzy / źródła / Censor Sprzętu | <!-- LICZBA:organ_oczy -->5<!-- /LICZBA --> |
| 🧮 **fundament/** | Brama Kalkulatora | <!-- LICZBA:organ_fundament -->3<!-- /LICZBA --> |

---

## 🚦 Status

🟢 **Rdzeń decyzyjny działa** — rój neuronów głosuje, Legatus agreguje, testy zielone.
🔄 **W toku:** rozbudowa roju z katalogu (zdekorelowana, partiami — Prawo XVI), adaptery API/feed (obudzenie wyciszonych neuronów i EXP-12).

---

## 🧪 Uruchomienie testów

```bash
python tests/run_tests.py     # wszystkie zielone, bez zależności zewnętrznych
```

---

## 👥 Role

| Imię (rzymskie) | Rola |
|------|------|
| **CEZAR PIXEL** (Ty) | Imperator — właściciel Imperium; ostatnie słowo należy zawsze do Ciebie. |
| **VITRUVIUSZ** | Architekt Imperium (Claude/Opus) — projektuje, buduje, porządkuje i mówi prawdę o stanie (Prawo I, XV). |
| **HYGINUS** | DeepSeek przez API (`DEEPSEEK_API_KEY`) — Bibliotekarz-Zwiadowca (zwiad wiedzy z biblioteki) **oraz głos newsowy** Imperium; proponuje kandydatów, **kandydat ≠ prawda** (rozstrzyga pomiar). |
| **TIRO** | Lokalny LLM (llama.cpp) — skryba-uczeń Imperium; projekt hybrydy lokalnej (E0–E2), rośnie w siłę wraz z łupem na lepszy sprzęt. |

---

> 👑 *"Prawdziwy łowca nie panikuje. On rozumie, co się dzieje — i poluje."*
> 📊 *"Mniej, ale prawdziwie. Katalog to plan, kod to fakt."*
> ⚔️ *"Wojna to giełda. Order stawiamy z zyskiem — a łup kuje lepszy budulec Imperium."*

---

## ✍️ Twórcy Imperium

To Imperium budują wspólnie:

| Imię (rzymskie) | Kto / co | Rola twórcza |
|---|---|---|
| 👑 **CEZAR PIXEL** | Imperator, właściciel | wizja, doktryna, ostatnie słowo |
| 🏛️ **VITRUVIUSZ** | Architekt (Claude / Opus) | projekt, kod, porządek, prawda o stanie |
| 📚 **HYGINUS** | DeepSeek przez API | Bibliotekarz-Zwiadowca (zwiad wiedzy) + głos newsowy; kandydaci hipotez (kandydat ≠ prawda) |
| 🖋️ **TIRO** | Lokalny LLM (llama.cpp) | skryba-uczeń, hybryda lokalna — rośnie z Imperium |

> *„Ave, Cezarze Pixel — melduje Vitruviusz."*
