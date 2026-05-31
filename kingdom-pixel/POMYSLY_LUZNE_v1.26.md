# 💭 POMYSŁY LUŹNE — DELTA v1.26
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.26). Tylko nowości. Źródło: skan Ameryki/Afryka/Australia.

## v1.26 (30.05.2026) — NOWY SKAN: filtr LLM (NeMo-Guardrails) + most Rust↔Python (PyO3)

### ✅ NeMo-Guardrails (github: NVIDIA-NeMo/Guardrails) — realny FILTR/strażnik LLM (= „Guardrails" z v1.10 + Lustro Prawdy)
- Open-source (NVIDIA), Python. Przechwytuje wejścia/wyjścia LLM, stosuje konfigurowalne kontrole, blokuje/modyfikuje wg polityk. 5 typów „szyn": input, retrieval, dialog, **execution**, output. Język reguł: **Colang**. Żywy (2026).
- Co daje NAM: **grounding / anti-halucynacja** (wymusza, by wyjście Mózgu było oparte na danych/bazie — wprost nasza PRAWDA + **Lustro Prawdy BRAIN-073**); **bezpieczeństwo egzekucji** (walidacja/sanityzacja wejść narzędzi, monitoring agenta — by zły sygnał nie odpalił transakcji); kontrola tematyczna. Działa z Anthropic/OpenAI/HuggingFace/**lokalny NIM (Llama 3.1 8B)**.
- ⚠️ Precyzyjnie: to guardrails dla LLM-Mózgu (grounding/bezpieczeństwo), **NIE** statystyczne odszumianie sygnałów rynkowych (to robi xgboost/statystyka). Komplementarne — realne wypełnienie „filtra" po stronie LLM.

### ✅ PyO3 + maturin (github: PyO3/pyo3, PyO3/maturin) — KLEJ Cognitive Mesh (Rust↔Python)
- PyO3 = bindings Rust↔Python: natywne moduły Pythona w Ruscie albo wołanie Rusta z Pythona (zarządza GIL, konwersją typów, pamięcią). v0.28, żywy. maturin = build/instalacja (`maturin develop` → crate jako moduł Pythona w venv).
- Wzorzec: **„Python = orkiestracja, Rust = wydajnościowy rdzeń"** = DOKŁADNIE nasz Cognitive Mesh (Mózg Python woła mięśnie Rust). `pyo3-arrow` = integracja Apache Arrow (nasza magistrala Arrow!).
- Wypełnia lukę „jak Python i Rust gadają": **PyO3 = in-process (ciasne, szybkie)** obok **ZeroMQ = między-procesowe/między-językowe (luźne, łączy też Zig)**. Oba mają miejsce.
- ⚠️ Klej/infra, nie alfa. Krzywa nauki (GIL, lifetime'y). Tip: nie wołać Rusta w ciasnej pętli Pythona — przekazać dane raz, iterować w Ruscie; build `--release`.

## 📍 POSTĘP — nowy skan: FinGPT · finBERT · **NeMo-Guardrails · PyO3/maturin** ✅.
⏭️ Kolejka: stable-baselines3 + PettingZoo (RL/multi-agent), giskard (walidacja/anti-overfit), Blankly/lumibot (boty), flow-forecast, FinRobot/ChatDev.
