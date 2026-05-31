# 💭 POMYSŁY LUŹNE — DELTA v1.12
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.12). Tylko nowości.

## v1.12 (30.05.2026) — ODKRYCIA Z WEJŚCIA W LINKI (część 1)
> Zmiana trybu: do tej pory czytałem TYLKO dokument IMV (opisy linków). Od teraz **WCHODZĘ w linki** (search → fetch) i szukam tego, czego w dokumencie NIE ma.

### ✅ KRONOS (github: shiyu-coder/Kronos) — PRAWDZIWY GEM
Czego dokument NIE mówił, a znalazłem w środku:
- Pierwszy open-source **model fundacyjny dla świec (K-line)** — i **recenzowany, przyjęty na AAAI 2026** (mocny sygnał wiarygodności, nie hobby).
- Trenowany na **12 mld świec z 45 giełd**; decoder-only Transformer + specjalny tokenizer OHLCV → tokeny.
- Zero-shot: prognoza ceny, **prognoza zmienności**, generowanie syntetycznych świec. (Ich benchmark: RankIC +93% vs czołowy TSFM — ich liczby.)
- **ŻYWE demo** (shiyu-coder.github.io/Kronos-demo): prognoza BTC/USDT aktualizowana co godzinę (ostatnia 30.05.2026), Monte Carlo + przedział niepewności. **Fine-tuning dostępny → da się dotrenować na NASZYCH danych.**
- ⚠️ Repo SAMO przyznaje: ich strategia to „baza", produkcja wymaga sizingu/ryzyka, backtest musi liczyć koszty/poślizg. **RankIC (skill prognozy) ≠ zysk po kosztach.**
- **Werdykt:** realny kandydat na komponent „predykcja / rozumienie wykresu" (warstwa 7 OCZU). Solidny, żywy, otwarty. Sceptycyzm co do zysku — ale to nie hype.

### ⚠️ NEXUS (github: The-R4V3N/Nexus) — REALITY CHECK
- Dokument sprzedał go jako mocny „self-evolving, przepisuje własny kod, trzy umysły". Realność w środku: **mały projekt hobbystyczny** — autor ma **6 gwiazdek ŁĄCZNIE na 26 projektach**. Koncept: „zaczął od 10 reguł + 1 prompt — przepisuje oba co sesję". Ciekawe, ale **nieudowodnione, znikoma trakcja.**
- **Lekcja:** wejście w link = weryfikacja. Dokument potrafi przesadzić. Nie przeceniać.

### Przy okazji (do sprawdzenia później)
- **EvoAgentX** — open-source framework samo-ewoluujących agentów (auto-generuje workflow multi-agent). Warte sceptycznego spojrzenia.

### 🔧 Metoda link-divingu
search → fetch → wyciągam to, czego NIE ma w dokumencie. Idziemy po **najwartościowszych** linkach (nie 220 na ślepo). Wiele będzie martwych / hype / mało wartych — to też wynik.

## 📍 POSTĘP
- Audyt 7 raportów IMV: ✅ (v1.5–v1.11).
- **Link-diving rozpoczęty (v1.12):** Kronos ✅, NEXUS ✅.
- ⏭️ Następne high-value linki: TradingAgents, Freqtrade, FinRL, VectorBT, FinCrew, OpenBB, RegimeNAS.
