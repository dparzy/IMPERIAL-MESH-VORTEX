# 💭 POMYSŁY LUŹNE — DELTA v1.27
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.27). Tylko nowości. Źródło: skan Ameryki/Afryka/Australia.

## v1.27 (30.05.2026) — NOWY SKAN: giskard (walidacja modeli) + SB3/PettingZoo (RL/multi-agent)

### ✅ giskard (github: Giskard-AI) — testowanie/walidacja modeli ML i LLM (Apache 2.0)
- Open-source, „magiczny" skan automatycznie wykrywa: **biasy, halucynacje, dryf danych (data drift), słabości odporności (robustness), wyciek danych, prompt injection.** Dla tabel/NLP/LLM. Integruje HuggingFace/MLflow/W&B. LLM-as-judge, Groundedness, OWASP LLM Top 10. Finansowany m.in. przez KE; współpraca z DeepMind.
- Dla nas: walidacja NASZYCH modeli (klasyfikator reżimu `xgboost`, predyktory ML, LLM-Mózg) — zwłaszcza **wykrywanie DRYFU** (reżim się zmienił → model przestarzały) + robustness (czy model pęka na zaburzonych wejściach) + grounding LLM (komplementarne z NeMo-Guardrails).
- 💡 **Ważne rozróżnienie walidacji:** giskard = **QA modelu** (czy model zdrowy: bias/dryf/halucynacja/robustness). VectorBT walk-forward + Freqtrade lookahead = **czy STRATEGIA trzyma out-of-sample**. Dwie RÓŻNE, komplementarne warstwy — potrzebujemy obu.

### ✅ stable-baselines3 + PettingZoo (warstwa RL / multi-agent)
- **SB3** (DLR-RM) = niezawodne implementacje algorytmów RL w PyTorch (PPO, SAC, DQN, A2C, TD3, DDPG), prosty interfejs. Fundament, na którym stoją frameworki typu FinRL. **Jednoagentowy.**
- **PettingZoo** (Farama) = standard **multi-agent RL (MARL)** — jak Gymnasium, ale dla wielu agentów. Kompatybilny z SB3/RLlib. SuperSuit = preprocessing.
- Dla nas: jeśli pójdziemy w RL — SB3 to czysty fundament. PettingZoo — jeśli chcemy **multi-agentowe uczenie/rywalizację** (roje Kobra/Lilia/Cień jako agenci, albo **Arena rywalizacji strategii = SOR** z v1.9).
- ⚠️ Ten sam realizm co FinRL: RL w live przeucza się, generalizacja trudna. **Infrastruktura, nie alfa.** MARL = dodatkowa złożoność — tylko gdy naprawdę pójdziemy w uczenie wielu agentów.

## 📍 POSTĘP — nowy skan: FinGPT·finBERT·NeMo-Guardrails·PyO3·**giskard·SB3/PettingZoo** ✅.
⏭️ Kolejka: Blankly/lumibot (boty), flow-forecast (DL forecasting), FinRobot/ChatDev (multi-agent).
