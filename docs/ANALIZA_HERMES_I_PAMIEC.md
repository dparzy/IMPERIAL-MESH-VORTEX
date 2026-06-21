# 🧠 ANALIZA: HERMES AGENT vs PAMIĘĆ IMPERIUM + STATUS KSIĄŻEK

> **Stan na:** 2026-06-20 · **Gałąź:** `claude/sleepy-fermi-dsdE4`
> Odpowiedź na pytanie Cezara: czy mamy pamięć absolutną jak „Hermes agent", co mówią
> nasze książki, co możemy dodać/ulepszyć. Dokument ŻYWY — źródło ciągłości (Prawo IX).

---

## ⚠️ CZĘŚĆ 1 — PRAWDA O „HERMES AGENT" (Prawo I, zero halucynacji)

Są **DWIE różne rzeczy** o nazwie Hermes — nie pomyl ich:

### 1A. „Hermes Agent" jako orkiestrator tradingowy = ❌ FABRYKACJA (już wykryta)

W `REJESTR_INSPIRACJI.md` (INF-32) jest udokumentowane: rozmowa z DeepSeek „Kai"
(plik 2,6 MB, analizowany przez 5 zwiadowców Opus) podawała „Hermes Agent" jako
gotowy **orkiestrator handlowy** z cudownymi właściwościami. **To była fabrykacja** —
obok ShieldRegime, CogAlpha-jako-kod, MELT Dataset, nieistniejących arXiv `2605.xxxxx`.
Nie ma takiego repozytorium tradingowego. **Nie wdrażamy go i nie cytujemy jako fakt.**

### 1B. „Hermes Agent" Nous Research = ✅ REALNY (ale to asystent osobisty, nie bot)

Po głębokim researchu w sieci (2026-06-20) znalazłem **prawdziwy** Hermes Agent:
- **Autor:** Nous Research — https://hermes-agent.nousresearch.com
- **Czym jest:** osobisty asystent AI (jak Claude Code), **NIE bot tradingowy**
- **5 filarów:** Memory (pamięć), Skills (umiejętności), Soul (tożsamość),
  Crons (zadania cykliczne), Self-improving loop (pętla samodoskonalenia)

**To jest to, co Cię zachwyciło — i słusznie.** Jego architektura PAMIĘCI jest świetna
i warto się nią inspirować. Poniżej dokładnie jak działa i co z tego MAMY, a czego NIE.

---

## 🔬 CZĘŚĆ 2 — JAK DZIAŁA PAMIĘĆ HERMES AGENT (Nous Research)

Źródła: dokumentacja Nous Research + analizy (MindStudio, Mervin Praison, glukhov.org).

| Mechanizm Hermes | Opis |
|---|---|
| **Bounded curated memory** | Pamięć ograniczona i kuratorowana — nie wszystko, tylko istotne (preferencje, projekty, środowisko, nauczone fakty) |
| **Frozen snapshot na start** | Na początku sesji pamięć wstrzykiwana do system promptu jako „zamrożony" snapshot |
| **Self-managed memory tool** | Agent SAM zarządza pamięcią — dodaje / zastępuje / usuwa wpisy przez `memory tool` |
| **Storage `~/.hermes/memories/`** | Pliki na dysku, trwałe między sesjami |
| **Skills = pamięć proceduralna** | Gdy rozwiąże nietrywialny workflow → zapisuje jako „skill" do ponownego użycia |
| **SOUL.md** | Plik tożsamości — pierwszy w system prompcie (kim agent jest) |
| **Self-improving loop** | Uczy się gdy aktywnie korygujesz błędy (pasywnie trochę, aktywnie — wzrost składany) |
| **8 pluginów pamięci zewnętrznej** | Honcho, OpenViking, Mem0, Hindsight, Holographic, RetainDB, ByteRover, Supermemory — dodają: graf wiedzy, wyszukiwanie semantyczne, auto-ekstrakcję faktów, modelowanie użytkownika między sesjami |

**Istota:** pamięć **wielowarstwowa** (hot/warm/cold), **trwała**, **samozarządzana**,
i sprzężona z **uczeniem** (skills + loop).

---

## 🏛️ CZĘŚĆ 3 — CO MAMY W IMPERIUM (realny kod, nie plan)

Imperium MA rozbudowaną pamięć absolutną — i w kilku miejscach jest **mocniejsze** niż
Hermes (bo tradingowo wyspecjalizowane). Moduły w `imperium/biblioteki/` (2135 linii kodu):

| Nasz moduł | Linie | Rola | Odpowiednik Hermes |
|---|---|---|---|
| `pamiec_absolutna.py` | 326 | ImperiumLog (JSONL), każdy sygnał/trade/test z hashem SHA-256 | Memory (cold layer) — **mocniejsze: hash integralności + MAE/MFE** |
| `kronikarz.py` | 156 | Zapytania do pamięci (zapytaj, porównaj_okresy, replay) | Retrieval / search |
| `mnemosyne.py` | 129 | Trwała pamięć transakcji + Księga Wad (uczenie z błędów) | Self-improving loop |
| `synapsy_rezimowe.py` | 251 | Uczenie wag PAR neuronów per-reżim (Hebbian × MWU × dekorelacja) | **UNIKAT — Hermes tego nie ma** |
| `igrzyska.py` | 491 | Ranking neuronów per-reżim, mnożniki wag, Lista Infamii | Skills/credit assignment |
| `hedge_mwu.py` | 318 | Online uczenie wag neuronów po każdym trade | Self-improving (online) |
| `arena_trzech_bram.py` | 217 | Triple-barrier (López de Prado) — etykietowanie | — |
| `kronikarz_zdarzen.py` | 247 | Event-study (analiza okien zdarzeń) | Episodic memory |

**CLAUDE.md + audyt_spojnosci.py + hooki** = nasz odpowiednik SOUL.md + frozen snapshot
(audyt na starcie każdej sesji wstrzykuje stan roju — to nasz „snapshot").

---

## 📊 CZĘŚĆ 4 — PORÓWNANIE: GDZIE WYGRYWAMY, GDZIE MAMY LUKI

### ✅ Gdzie Imperium jest LEPSZE od Hermes (zachować przewagę)
1. **Hash SHA-256** każdego rekordu — integralność danych (Hermes nie ma)
2. **MAE/MFE per-trade** — optymalizacja SL/TP (Hermes to asystent, nie zna tradingu)
3. **Synapsy reżimowe** — reżimowo-warunkowane uczenie zdekorelowanych koalicji (UNIKAT)
4. **Deterministic replay** — odtworzenie dokładnego stanu z przeszłości
5. **24 Prawa + audyt** — twarde bezpieczniki spójności (Hermes ufa LLM-owi)

### 🚨 Gdzie mamy LUKI vs Hermes (UTRATA POTENCJAŁU — Prawo XV)
1. **Brak wyszukiwania SEMANTYCZNEGO** — szukamy po polach (symbol/data/reżim), nie po
   znaczeniu („pokaż podobne sytuacje rynkowe do dziś"). Hermes ma to przez pluginy.
   → *PYTHIA (fingerprint matching) częściowo to robi, ale nie ma indeksu wektorowego.*
2. **Brak grafu wiedzy** — nasze logi to płaski JSONL; brak powiązań „to wynika z tego".
3. **Pamięć proceduralna niejawna** — mamy strategie, ale system nie zapisuje SAM
   „nauczonego workflow" jak Hermes Skills.
4. **Frozen snapshot ubogi** — audyt podaje liczby, ale nie „czego nauczyliśmy się
   w ostatnich 5 sesjach" (lekcje). Brak pliku LEKCJE.md auto-aktualizowanego.
5. **Self-improving loop ręczny** — uczymy się gdy Ty zlecisz; brak automatycznego
   „po każdej sesji zapisz 3 lekcje do pamięci trwałej".

---

## 📚 CZĘŚĆ 5 — KSIĄŻKI: CO MAMY (21 pozycji BIB) I CO Z NICH WYCIĄGNĘLIŚMY

W `REJESTR_INSPIRACJI.md` (INF-13..INF-33) mamy **21 książek skatalogowanych** z esencją.
Status „esencja wyciągnięta" = ✅ (zmapowane na zadania W-xxx), część czeka na wdrożenie.

| BIB | Książka | Esencja → zadania | Status |
|---|---|---|---|
| 001 | Secret Wealth Advantage (Patel) | Cykl 18-letni nieruchomości → W-082..084 | ✅ esencja, plan Faza 2 |
| 002 | Technical Analysis (Murphy) | Analiza międzyrynkowa, MESA → W-085..088 | ✅ esencja |
| 003 | Cryptoassets (Burniske) | NVT, hash rate, hype cycle → W-089..093 | ✅ esencja |
| 004 | Psychology of Trading (Steenbarger) | Stacjonarność, pinball → W-094..096 | ✅ esencja |
| 005 | What Exactly Is Crypto? (Blum) | Tokenomika, unlock/vesting → W-097..100 | ✅ esencja |
| 006 | High Probability Scalping (Carson) | Konfluencja+dekorelacja, DeMark → W-101..106 | ✅ esencja |
| **007** ⭐ | **Advances in Financial ML (López de Prado)** | VPIN, triple-barrier, meta-labeling, purged CV, MDA/SFI → **W-355..359 WDROŻONE** | ✅ **CZĘŚCIOWO W KODZIE** |
| **008** ⭐ | **Volatility Trading (Sinclair)** | Yang-Zhang, Kelly, **volatility drag W-130 WDROŻONE** | ✅ częściowo kod |
| 009 ⭐ | (Mis)behavior of Markets (Mandelbrot) | Hurst, grube ogony, multifraktal → W-140..158 | ✅ esencja |
| 010 ⭐ | Quantitative Trading (Chan) | Half-life OU, macierzowy Kelly → W-160..169 | ✅ esencja |
| 011 ⭐ | Algorithmic Trading (Chan) | Kalman β, Monte-Carlo Kelly → W-170..178 | ✅ esencja |
| 012 | Coding Capital | ⚠️ słaba 3/10, tylko EVT/GPD → W-180 | ✅ oceniona |
| 013 ⭐ | Markets in Profile (Dalton) | TPO Value Area, volume-vs-TPO → W-190..199 | ✅ esencja |
| 014 ⭐ | Mind Over Markets (Dalton) | 6 typów dnia, Initiative vs Responsive → W-200..209 | ✅ esencja |
| 015 ⭐ | New Trading for a Living (Elder) | Force Index, **Reguła 6% LUKA** → W-210..219 | ✅ esencja, część kod |
| 016 | Trading in the Zone (Douglas) | ⚠️ 4/10, Legatus=prawdopodobieństwo → W-220..225 | ✅ oceniona |
| 017 ⭐ | Thinking Fast and Slow (Kahneman) | Biasy tłumu jako neurony → W-230..239 | ✅ esencja |
| 018 ⭐ | Positional Option Trading (Sinclair) | Skew-adjusted Kelly, doktryna stopów → W-240..249 | ✅ esencja |
| 019 | Handbook Crypto Trading (Harris) | ❌ odrzucona 2/10 | ✅ oceniona |
| 021 | High Win Rate Day Trading Setups | ⚠️ 3/10, Kaufman ER → **W-353 WDROŻONE** | ✅ kod |

**Wniosek:** mamy esencję 21 książek. **Najcenniejsze (⭐) to López de Prado (007),
Sinclair (008/018), Chan (010/011), Dalton (013/014), Mandelbrot (009).** Większość
esencji jest zmapowana na zadania, ale **wdrożona w kodzie jest mniejszość** (007 częściowo,
008 drag, 021 Kaufman). **To jest backlog wartości — tu jest nasz wzrost.**

---

## 📖 CZĘŚĆ 6 — JAKĄ KSIĄŻKĘ DODAĆ NASTĘPNIE

Cezar pytał „jaką książkę mam podać". Rekomendacje wg luk (nie powielać tego co mamy):

### Priorytet — pamięć/uczenie (bo o to pytasz)
1. **„Machine Learning for Asset Managers" — López de Prado (2020)** — krótsza, nowsza niż
   BIB-007; rozdziały o **denoising macierzy kowariancji, klastrowaniu, distance metrics** —
   wprost zasila nasze luki: wyszukiwanie podobieństwa + dekorelacja. **TOP rekomendacja.**
2. **„Advances in Active Portfolio Management" — Grinold & Kahn** — Information Ratio,
   fundamental law (IR = IC·√breadth) — matematyka „więcej zdekorelowanych sygnałów = lepiej".

### Priorytet — przewaga konkurencyjna (krypto-specy­ficzne)
3. **„Trading and Exchanges" — Larry Harris** — mikrostruktura rynku (kat. U z RESEARCH_NOWE_KATEGORIE) — order flow, market making, adverse selection.

> **Format dostarczenia:** epub/pdf/azw3 jak poprzednio — wrzuć do `/uploads/`, ja wyciągnę
> esencję jak przy López de Prado (agent Opus czyta całość → mapuje na W-xxx → kod+testy).

---

## 🚀 CZĘŚĆ 7 — PROPOZYCJE: BYĆ LEPSZYM (konkretny plan, Prawo VII — po kolei)

Inspirowane Hermes Agent + nasze luki. Kolejność wg wartość/koszt:

### 🥇 W-360: Plik LEKCJE.md auto-aktualizowany (odpowiednik Hermes Memory)
Po każdej sesji system dopisuje 3 lekcje (co zadziałało / co zawiodło / co dalej).
Wczytywany na starcie jak frozen snapshot Hermesa. **Tani, ogromna ciągłość.**
→ Bezpośrednio rozwiązuje Twój ból: „nic od początku, nic powtarzane".

### 🥈 W-361: Wyszukiwanie podobieństwa rynkowego (semantic-lite)
Rozbudować PYTHIA fingerprint o indeks: „pokaż 10 historycznych sytuacji najbardziej
podobnych do teraz" (wektor cech: reżim, ADX, vol, struktura). Bez ciężkiego ML —
odległość euklidesowa na znormalizowanych cechach. Odpowiednik semantic search Hermesa.

### 🥉 W-362: Pamięć proceduralna (Skills Imperium)
Gdy strategia/setup zadziała powtarzalnie → system zapisuje „przepis" do biblioteki
i proponuje go w podobnym kontekście. Odpowiednik Hermes Skills.

### W-363: Self-improving loop automatyczny
Po N trade'ach automatyczny mini-raport: które neurony tracą trafność (z igrzysk),
auto-propozycja korekty wag → do akceptacji Cezara (Ty autoryzujesz, jak chcesz).

### Faza 2 (gdy DeepSeek key) — z rejestru, już zaplanowane
- **SHARP (ML-24)** — warstwa audytu uczy się trafności głosów
- **Kronos (A-12)** — neuron predykcyjny świec (dane OHLCV już mamy)
- **Books backlog** — wdrażać esencję ⭐ książek w kod (największy nietknięty potencjał)

---

## 🎯 PODSUMOWANIE DLA CEZARA

1. **„Hermes Agent" tradingowy = fabrykacja** (już wiedzieliśmy, INF-32). Ale **realny
   Hermes Agent Nous Research istnieje** — to asystent osobisty z genialną pamięcią 5-filarową.
2. **MAMY mocną pamięć absolutną w kodzie** (8 modułów, 2135 linii) — w hashu, MAE/MFE
   i synapsach reżimowych jesteśmy LEPSI. W semantyce, grafie i auto-lekcjach mamy LUKI.
3. **Mamy 21 książek z esencją** — najcenniejsze ⭐ częściowo wdrożone; backlog = wzrost.
4. **Plan bycia lepszym:** W-360 (auto-lekcje) → W-361 (podobieństwo) → W-362 (skills) →
   wdrażać esencję książek ⭐. Daj DeepSeek key → odblokowuje Fazę 2.
5. **Następna książka:** López de Prado „Machine Learning for Asset Managers" (TOP).

*Quod non scribitur, non factum est — co nie zapisane, nie zrobione. Ten dokument to dowód.*

---
*Źródła web (2026-06-20): hermes-agent.nousresearch.com, MindStudio, Mervin Praison, glukhov.org, github.com/Julian-dev28/hermes-trader, github.com/MemTensor/MemOS*
