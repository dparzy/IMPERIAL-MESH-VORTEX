# 🏛️ IMPERIAL MESH VORTEX

> **Imperium Cesarza Pixel** — autonomiczny system tradingowy AI.
> Lokalny, samouczący się rój neuronów, który poluje na rynku jak armia z jasnym łańcuchem dowodzenia.

> **Stan na:** 2026-06-13 · **Testy:** 883/883 zielone · **Faza:** PętlaLive (entrypoint) + Synapsy Reżimowe + PamięćRefleksyjna + Radar wpięty + Paper Trading Etap II.

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
| **Mikro-neurony** | **63 zaimplementowane** (59 aktywnych: 37 OHLCV + SES-01 ZegarSesji + SES-02 AzjaRange + V-05 Force Index Eldera + 3 SMC (OrderBlock/FVG/BOS) + 6 kat. R + NEWS-01 Sentyment LLM + V-03 CVD + V-14 Choppiness + L-14 Ulcer + H-01 Hurst-DFA + N-01 Permutation Entropy + Z-01 VPIN ToxicFlow + Z-03 Bubble/Crash kill-switch + Z-04 Cascade/Dead-Cat + X-27 Value Convergence + OC-05 WashTrading, Z-02 PumpDetect przez adaptery publiczne; 4 czeka na on-chain API) |
| **Zwiadowcy Exploratores (EXP)** | **12** (EXP-01..12; 11 aktywnych + EXP-12 wyciszony do feedu L2) |
| **Brama Kalkulatora** | jedyne wejście do matematyki wskaźników (Prawo I) |
| **Budowniczy Wskaźników** | most: surowe bary → komplet wskaźników dla neuronów (z HA, Ichimoku, MACD…) |
| **Generał Legatus** | agregacja głosów + wagi reżimowe + odpalanie zwiadowców |
| **Igrzyska / Koloseum** | rywalizacja i rangowanie neuronów |
| **Diagnostyka korelacji** | pomiar redundancji sygnałów (Prawo XVI) |
| **Status elitarny** | **15 elitarnych** modułów mierzonych kryterium E1–E7 (Prawo XX): X-25, X-26, D-01 + 12 zwiadowców |
| **Monte Carlo / Optymalizator / Pamięć Refleksyjna / Drift Adapter** | W-293/294/295/296 — antyoverfitting + samouczenie Brain |
| **Testy** | `python tests/run_tests.py` → **835/835** ✅ |

**Katalog projektowy** (`docs/KATALOG_NEURONOW.md`) opisuje **299 neuronów** docelowo — to mapa drogowa, nie kod. Różnica (299 − 63) = backlog do zbudowania (partiami, z pomiarem dekorelacji).

---

## 📂 Struktura projektu

| Folder / Plik | Zawartość |
|---------------|-----------|
| **[ZASADY_FUNDAMENTALNE.md](ZASADY_FUNDAMENTALNE.md)** | Konstytucja — **21 praw**, których zawsze przestrzegamy |
| **[CLAUDE.md](CLAUDE.md)** | Instrukcje stałe (czytane co sesję): Prawa XV–XVIII, bezpieczeństwo, git |
| **imperium/** | Żywy kod systemu (patrz mapa niżej) |
| **docs/** | Dokumentacja + katalogi projektowe (neurony, strategie, arsenał) |
| **tests/** | Testy bez zależności: `python tests/run_tests.py` |
| **archiwum/** | Surowa, oryginalna wizja |
| **kingdom-pixel/** | Archiwum poprzedniego projektu (NIE wchodzi do żywego systemu bez decyzji) |

---

## 🗺️ Mapa Imperium (realne foldery w `imperium/`)

```
👑 cesarz/       — mózg decyzyjny, 5 Doradców, PamięćRefleksyjna   (9)
🏛️ senat/        — debata / konsensus                              (2)
⚔️ legiony/      — 63 neurony + 12 zwiadowców + Legatus + Radar     (40)
🏟️ koloseum/     — Dyrygent, PętlaLive, Backtest portfela, Namiestnik (11)
🛡️ pretorianie/  — bezpieczeństwo, kalkulator lewara, Praeda        (5)
🏗️ akwedukty/    — pipeline danych + adaptery API (Futures/F&G/CVD/News) (8)
🛤️ drogi/        — API i egzekucja (NexusHub)                       (3)
🎨 swiatynie/    — dashboard / wizualizacja                         (2)
📚 biblioteki/   — pamięć, MWU, SynapsyRezimowe, KronikarzZdarzeń   (8)
👁️ oczy/         — obserwatorzy / źródła                            (1)
🧮 fundament/    — Brama Kalkulatora                                (2)
```

---

## 🚦 Status

🟢 **Rdzeń decyzyjny działa** — rój neuronów głosuje, Legatus agreguje, testy zielone.
🔄 **W toku:** rozbudowa roju z katalogu (zdekorelowana, partiami — Prawo XVI), adaptery API/feed (obudzenie wyciszonych neuronów i EXP-12).

---

## 🧪 Uruchomienie testów

```bash
python tests/run_tests.py     # 835/835, bez zależności zewnętrznych
```

---

## 👥 Role

| Imię | Rola |
|------|------|
| **Komendant / Cezar** (Ty) | Ostatnie słowo należy zawsze do Ciebie. |
| **Architekt Imperium** | Projektuje, buduje, porządkuje — i mówi prawdę o stanie (Prawo I, XV). |

---

> 👑 *"Prawdziwy łowca nie panikuje. On rozumie, co się dzieje — i poluje."*
> 📊 *"Mniej, ale prawdziwie. Katalog to plan, kod to fakt."*
