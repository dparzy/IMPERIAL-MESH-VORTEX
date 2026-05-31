# 💭 POMYSŁY LUŹNE — DELTA v1.19
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.19). Tylko nowości.

## v1.19 (30.05.2026) — LINK-DIVE: TradeFM + mapa pozostałych linków

### ✅ TradeFM (arXiv 2602.23784, II.2026) — model fundacyjny MIKROSTRUKTURY (frontier)
- **524M-param generatywny Transformer = model fundacyjny dla przepływu zleceń (trade-flow) i mikrostruktury.** Uczony na **miliardach zdarzeń transakcyjnych z >9000 akcji.** Autorzy z **JPMorgan AI Research** (m.in. Manuela Veloso) — poważne, instytucjonalne.
- Uniwersalna tokenizacja + cechy skalo-niezmiennicze → generalizacja cross-asset bez kalibracji per-aktywo. Zintegrowany **deterministyczny symulator rynku**; rollouty odtwarzają „stylized facts" (grube ogony, klastrowanie zmienności, brak autokorelacji zwrotów). 2–3× mniejszy błąd dystrybucji niż Compound Hawkes; zero-shot na rynki APAC.
- Dla nas: to **symulator/generator mikrostruktury (poziom tick/zleceń), na AKCJACH** — inna granularność niż nasze świece, nie krypto. Świetne do realistycznej **symulacji rynku / danych syntetycznych / testów egzekucji**; NIE sygnał alfa kierunkowy. ⚠️ Preprint (nierecenzowany), błąd dystrybucji/perplexity ≠ zysk.
- 📌 Porównanie: **Kronos** (świece, krypto, fine-tune) jest dla nas BARDZIEJ wprost niż TradeFM (mikrostruktura, akcje). Oba potwierdzają trend: modele fundacyjne wchodzą do tradingu.

### 🗺️ MAPA POZOSTAŁYCH LINKÓW TOP (uczciwie — sygnał vs szum)
Przeskanowałem realne URL-e z sekcji TOP. **Większość reszty to SZUM:** fora (bitcointalk, wilmott, naver), dokumentacje giełd (binance/bybit/upbit API), blogi, strony nie-ang., parę śmieci (Jaffa.Net, bhutan-hydro-mining.bt). Realne, jeszcze nieruszone tropy:
- **arXiv 2026:** 2511.18850, 2605.05580, 2605.06822, 2605.12532, 2508.04656 (do wyrywkowego sprawdzenia).
- **ClickHouse** (hurtownia danych — realna, już w naszym stacku), **alpaca.markets** (API tradingowe US, mało krypto), TradingView „Quantum Kinetic Candles" (skrypt-wskaźnik).

### 🧭 REKOMENDACJA (uczciwa)
Zostało **mało PRAWDZIWYCH gemów** w linkach — najlepsze już wyłowiliśmy (Kronos, TradingAgents, Nautilus, VectorBT, DoWhy, RegimeNAS…). Proponuję: jeszcze wyrywkowo 2–3 papiery arXiv 2026, a potem **dokończyć czytanie dokumentu IMV** (wpisy rozmów 111–129+ i ogon) — tam pewnie więcej Twojej wizji niż w resztkach linków.

## 📍 POSTĘP — link-diving (14): …NautilusTrader·Hummingbot·**TradeFM** ✅.
⏭️ Opcje: (A) 2–3 papiery arXiv 2026; (B) dokończyć dokument IMV.
