# 💭 POMYSŁY LUŹNE — DELTA v1.25
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.25). Tylko nowości.
> **Nowe źródło:** skan Ameryki + Afryka + Australia/Pacyfik (6264 linie, po krajach). Wchodzę w linki, szukam tego, czego NIE mamy. Duplikaty pomijam.

## v1.25 (30.05.2026) — NOWY SKAN: warstwa SENTYMENTU/NLP OCZU (luka wypełniona)
> OCZY warstwa 4 (sentyment) była dotąd tylko opisana. Teraz konkretne, realne narzędzia.

### ✅ finBERT (github: ProsusAI/finbert) — lekki klasyfikator sentymentu (standard branżowy)
- BERT dotrenowany na finansach → sentyment tekstu: pozytywny / neutralny / negatywny (softmax). **~1,6 mln pobrań/mc** = standard. Lekki, szybki, **lokalny**.
- Użycie: news/nagłówki/social → score sentymentu → sygnał (np. long-short wg sentymentu). Wprost **OCZY warstwa 4**.
- 🪙 Dla KRYPTO: pokrewny **CryptoBERT** (sentyment krypto) — lepszy do naszego rynku niż finBERT (akcje/EN).
- ⚠️ EN-only, trenowany na danym okresie (może nie łapać nowego żargonu), sentyment = JEDEN input, nie alfa.

### ✅ FinGPT (github: AI4Finance-Foundation/FinGPT) — open-source finansowy LLM (lekki LoRA)
- Otwarta alternatywa dla BloombergGPT. **Lekki fine-tuning LoRA** → tani, działa na skromnym sprzęcie (Twój!). RLHF → personalizacja (poziom ryzyka, styl). Recenzowany (IJCAI/NeurIPS 2023+), żywy (HuggingFace, 2026). Ekosystem AI4Finance: FinGPT + FinRL + FinRobot + FinNLP.
- Zastosowania: analiza sentymentu, FinGPT-Forecaster, robo-doradztwo, łączenie z danymi/newsami na żywo (grounding).
- Dla nas: **lokalny, wyspecjalizowany model finansowy NLP** (niezależność — przetwarzanie newsów bez API). Cięższy niż finBERT = głębsza analiza. ⚠️ Forecaster: prognoza ≠ zysk; LLM może halucynować → trzymać przy danych (grounding) + walidacja.

### 🎯 Wniosek
**OCZY warstwa 4 (sentyment/NLP)** = dwa tiery: **finBERT/CryptoBERT** (lekki, szybki score) + **FinGPT** (głęboka analiza/LLM). Oba lokalne, realne, dotąd ich konkretnie NIE mieliśmy. Sentyment = jeden głos do Klucza Kodowego, nie wyrocznia.

### ♻️ Duplikaty w nowym skanie (NIE dodajemy): FinRL, FinRL-Meta, OpenBB, ClickHouse — już mamy.

## 📍 POSTĘP — nowy skan: FinGPT ✅, finBERT ✅.
⏭️ Kolejka NOWYCH (nie-duplikaty): NeMo-Guardrails (filtr klucza), pyo3/maturin (most Rust↔Python = Cognitive Mesh), stable-baselines3 + PettingZoo (RL/multi-agent), Blankly/lumibot (boty), giskard (walidacja ML/anti-overfit), flow-forecast, FinRobot/ChatDev (multi-agent).
