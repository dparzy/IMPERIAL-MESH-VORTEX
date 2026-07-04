# 🏛️ IMPERIAL MESH VORTEX

> **Imperium Cesarza Pixel** — autonomiczny system tradingowy AI.
> Lokalny, samouczący się rój neuronów, który poluje na rynku jak armia z jasnym łańcuchem dowodzenia.

> **Stan na:** 2026-07-04 · **Testy:** patrz `python tests/run_tests.py` · **Faza:** PętlaLive + Synapsy Reżimowe + PamięćRefleksyjna + Radar + Paper Trading Etap II + Filtr Asymetrii (W-314) + RealOrderRouter/dry-run (W-331/332) + sync pozycji (W-333) + progi adaptacyjne (W-334) + meta-warstwy B: Neutralizacja + Meta-labeling (W-337) + detektory reżimu: CUSUM/BOCPD/FracDiff (W-336/338/339) + vol-gate Jump Model opt-in (W-340) + **niezawodność warunkowa per-reżim (W-341, Prawo XXIII) + LiveMonitor/TelegramAlert (W-341, Prawo XXIV) + MECHANIZM przewagi (W-342, Prawo XXII) + godło SVG (W-342) + Debata Senatu Byk/Niedźwiedź/Cenzor (W-343)**.

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
| **Mikro-neurony** | **84 zaimplementowane** (78 aktywnych: OHLCV momentum/trend/wolumen + SES-01/02 + 3 SMC + 6 kat. R + NEWS-01 + V-03 CVD + Z-01..05 brama obronna + X-27 Value + X-28 MTF Confluence + OC-05 WashTrading + **W-322: V-06 Delta Divergence, V-07 Anchored VWAP, VP-01 Volume Profile/VPOC, Z-06 Amihud Illiquidity, Z-07 Pi Cycle Top** + **W-329: RADAR-04 kaskada korelacyjna + RADAR-05 lead-lag BTC→alty** + **W-335: C-01 Cross-sectional Relative Strength** + **W-336: CP-01 CUSUM change-point** + **W-338: BOCPD-01 Bayesian change-point** + **W-339: N-02 Fractional Differentiation**; 4 czeka na on-chain API) |
| **Zwiadowcy Exploratores (EXP)** | **15** (EXP-01..15; 13 aktywnych + 2 wyciszone do feedu) |
| **Brama Kalkulatora** | jedyne wejście do matematyki wskaźników (Prawo I) |
| **Budowniczy Wskaźników** | most: surowe bary → komplet wskaźników dla neuronów (z HA, Ichimoku, MACD…) |
| **Generał Legatus** | agregacja głosów + wagi reżimowe + odpalanie zwiadowców |
| **Igrzyska / Koloseum** | rywalizacja i rangowanie neuronów |
| **Diagnostyka korelacji** | pomiar redundancji sygnałów (Prawo XVI) |
| **Status elitarny** | **15 elitarnych** modułów mierzonych kryterium E1–E7 (Prawo XX): X-25, X-26, D-01 + 15 zwiadowców |
| **Monte Carlo / Optymalizator / Pamięć Refleksyjna / Drift Adapter** | W-293/294/295/296 — antyoverfitting + samouczenie Brain |
| **Testy** | `python tests/run_tests.py` (bieżąca liczba — nie hardkodujemy, by nie przeterminować) ✅ |

**Katalog projektowy** (`docs/KATALOG_NEURONOW.md`) opisuje **299 neuronów** docelowo — to mapa drogowa, nie kod. Różnica (299 − 76) = backlog do zbudowania (partiami, z pomiarem dekorelacji).

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

## 🗺️ Mapa Imperium (realne foldery w `imperium/`)

```
👑 cesarz/       — mózg decyzyjny, 5 Doradców, PamięćRefleksyjna   (9)
🏛️ senat/        — debata / konsensus                              (2)
⚔️ legiony/      — 84 neuronów + 15 zwiadowców + Legatus + Radar     (40)
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
python tests/run_tests.py     # wszystkie zielone, bez zależności zewnętrznych
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
