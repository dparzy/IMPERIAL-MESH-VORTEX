# 💭 POMYSŁY LUŹNE — DELTA v1.29
> **Plik-delta na BAZIE v1.3** (czytać: v1.3 + v1.4…v1.29). Tylko nowości. Status Z77: **[TROP]** = znane publicznie, niezweryfikowane w repo. Dedup vs ZBADANE: 0 trafień.

## v1.29 (31.05.2026) — REALIZM BACKTESTU: czy sygnał ma moc, czy strategia trzyma, czy egzekucja jest realna

### ✅ Alphalens-reloaded [TROP] (github: stefan-jansen/alphalens-reloaded, Apache 2.0) — analiza wartości faktorów
- Mierzy, czy *czynnik/sygnał* ma w ogóle moc predykcyjną: Information Coefficient, zwroty po kwantylach, turnover.
- Dla nas: **filtr PRZED Poligonem (Z17)** — zanim strategia pójdzie na walk-forward, sprawdzamy czy sygnał nie jest szumem. Tania warstwa „pre-walidacji".

### ✅ MlFinLab [TROP] (github: hudson-and-thames/mlfinlab) — ML dla finansów (metody López de Prado)
- Triple-barrier labeling, fractional differentiation, **purged k-fold CV** (anty-lookahead), meta-labeling.
- ⚠️ **Licencja: część funkcji komercyjna/za paywallem** — do potwierdzenia. ALE same metody są publiczne (książka „Advances in Financial ML"). Bierzemy **wiedzę o metodach**, nie zależność od paczki.
- Dla nas: dyscyplina anty-overfit — komplementarne z VectorBT walk-forward + Freqtrade lookahead (v1.14).

### ✅ Symulatory księgi zleceń (LOB) [TROP] — Blueshift, CoinTossX (arXiv)
- Symulują order book → realny **poślizg i market impact**, nie idealizowane fill-e.
- ⚠️ **ZŁOŻONE, badawcze. NIE Faza 0.** Trop pod modelowanie egzekucji (Z35 DIR) — dopiero gdy ruszymy z mikrostrukturą.

### 💡 Mapa trzech warstw walidacji (żeby się nie mylić):
| Warstwa | Pyta o | Narzędzie |
|:--|:--|:--|
| Moc sygnału | „czy faktor cokolwiek przewiduje?" | Alphalens |
| Trwałość strategii | „czy trzyma out-of-sample / inne aktywa?" | VectorBT WF + purged CV |
| Realność egzekucji | „czy fill jest realny po kosztach/poślizgu?" | LOB sim (później) |

## 📍 POSTĘP — łańcuch walidacji domknięty koncepcyjnie: sygnał → strategia → egzekucja ✅.
⏭️ Kolejka: multi-agent (kolejka z v1.27: CrewAI/Autogen/MetaGPT/ChatDev) + forecasting → v1.30.
