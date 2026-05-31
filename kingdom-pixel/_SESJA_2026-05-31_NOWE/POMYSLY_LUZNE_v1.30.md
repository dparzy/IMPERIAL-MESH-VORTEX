# 💭 POMYSŁY LUŹNE — DELTA v1.30
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.30). Tylko nowości. Status Z77: **[TROP]** = znane publicznie, niezweryfikowane w repo. Dedup vs ZBADANE: 0 trafień.

## v1.30 (31.05.2026) — MULTI-AGENT (z kolejki) + forecasting DL

### ✅ Frameworki orkiestracji wielu agentów LLM [TROP]
- **CrewAI** (github: joaomdmoura/crewAI, MIT) — role + zadania + „załoga". Najprostszy start.
- **Autogen** (github: microsoft/autogen, MIT — do potwierdzenia) — konwersacje agent↔agent, dojrzały.
- **MetaGPT** (github: geekan/MetaGPT, MIT) — agenci jako „firma" (PM, dev, QA).
- **ChatDev** (github: OpenBMB/ChatDev, Apache 2.0) — agentowy „software house".
- Dla nas: mapują na wizję **organizmu** (Mózg-Decydent + zwiadowcy) i `TitanMind`/N-ORCH. Najbliżej: CrewAI dla prostej orkiestracji researchu.

### ⚠️ TWARDE zastrzeżenia (zanim się zachłyśniemy):
1. **Drogie tokenowo i WOLNE** → NIGDY na gorącej ścieżce egzekucji (latency Z22.4). To nie jest miejsce na decyzje live w milisekundach.
2. To warstwa **BADAWCZA/STRATEGICZNA** — research nocą, generowanie hipotez strategii, audyt — nie silnik tradingu.
3. **Halucynacje** → muszą działać za Bramą Z75 (każda liczba z kalkulatora, nie z LLM) + guardrails. LLM proponuje, forteca liczy (Z35).
- 👉 Werdykt: **orkiestracja researchu, nie alfa egzekucji.** Realny dopiero gdy mamy stabilny rdzeń Fazy 0.

### ✅ FlowForecast [TROP] (github: AIStream-Peelout/flow-forecast) — DL do szeregów czasowych (transformery)
- ⚠️ **Licencja GPL-3.0 (copyleft!)** — uwaga, „zaraża" kod pochodny. Do potwierdzenia przed użyciem w zamkniętym repo.
- ⚠️ Ten sam realizm co RL (FinRL, v1.15): DL na cenach **przeucza się**, generalizacja trudna. **Infrastruktura, nie alfa.**
- 💡 Lżejsze/dojrzalsze alternatywy do skanu: Darts, NeuralForecast, StatsForecast (klasyka często bije DL na szeregach finansowych).

## 📍 POSTĘP — multi-agent zmapowany jako warstwa researchu (z hamulcami) ✅; forecasting DL — sceptycznie.
⏭️ Kolejka: POMYSŁY LUŹNE — kreatywne połączenia perełek → v1.31.
