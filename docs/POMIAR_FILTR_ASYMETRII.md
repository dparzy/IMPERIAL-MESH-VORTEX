# 📐 POMIAR FILTRA ASYMETRII REŻIMU (W-314) — dowód OOS (Prawo XVI)

> **Stan na:** 2026-06-13 · **Metoda:** A/B backtest portfelowy na oknie OOS · **Status:** ✅ przewaga zmierzona

## Cel

Zmierzyć, czy Filtr Asymetrii Reżimu faktycznie poprawia wynik — **Prawo XVI:
przewaga mierzona, nie zgadywana.** Filtr podnosi próg pewności w rynku bocznym
(ADX niski) i dla wejść kontr-trendowych.

## Tło — dlaczego w ogóle (odkrycie OOS)

Pomiar kierunków na świeżym oknie ujawnił rozdźwięk in-sample vs OOS:

| | Pełna historia (in-sample) | Ostatnie 20 mies. (OOS) |
|---|---|---|
| Okres | 2017-08 → 2026-06 | 2024-10 → 2026-06 |
| BTC start→koniec | $4 350 → $63 086 (**+1350%**) | $62 561 → $63 086 (**+0,8%**) |
| Charakter | wielka hossa 9 lat | **płaski chop** |
| BASELINE PnL | +26 152$ (5 par) | **−386$** (3 pary) |

**Wniosek:** stare „+26k" jechało na trendzie hossy. Na płaskim rynku rój **traci**,
bo wchodzi za często w chopie — prowizje + whipsaw zjadają cienką przewagę. Warstwy
adaptacyjne tego nie ratują (synapsy+mwu: −373$ vs baseline −386$). Split kierunków
**zbalansowany 51% LONG / 49% SHORT** — SHORT nie jest martwym głosem (Prawo XV OK).

## Warunki pomiaru

- Koszyk 3 par: BTCUSDT, ETHUSDT, SOLUSDT
- Interwał 4H, okno 200, kapitał 10 000$
- Okno OOS: ostatnie 3000 barów (2024-10-13 → 2026-06-08) — rynek boczny
- A/B: baseline vs baseline + filtr (jedyna różnica = filtr)

## Wyniki A/B

| Konfig | Trade | PnL | **PnL/trade** | WR | LONG PnL | SHORT PnL |
|---|---|---|---|---|---|---|
| BASELINE | 171 | −386$ | −2,3 | 41% | −465$ (WR 39%) | +79$ (WR 43%) |
| **+ FILTR ASYMETRII** | 170 | **−238$** | **−1,4** | 41% | −370$ (WR 40%) | +132$ (WR 43%) |

**Delta:** strata mniejsza o **38%** (−386 → −238$), PnL/trade z −2,3 do −1,4.
Oba kierunki poprawione (LONG +95$, SHORT +53$) przy praktycznie tej samej liczbie
trade'ów (filtr zmienia KTÓRE wejścia, nie ich liczbę — w portfelu 1-pozycja/symbol
weto jednego wejścia przesuwa całą dalszą sekwencję).

## Interpretacja

- ✅ **Filtr działa** — tnie krwawienie w rynku bez trendu o ~38% OOS.
- ⚠️ **Uczciwie (Prawo I): wynik wciąż ujemny.** Filtr redukuje stratę na brutalnym
  chopie, NIE zamienia rynku bocznego w zyskowny — i nie taki jest jego cel.
- 🎯 **Logika potwierdzona:** największy upływ kapitału był w chopie (ADX niski),
  dokładnie tam, gdzie filtr podnosi poprzeczkę.

## Podstawa literaturowa

- **Time-Series Momentum** — Moskowitz, Ooi, Pedersen (2012), *Journal of Financial
  Economics*: trade'y zgodne z trendem niosą wyższą oczekiwaną stopę zwrotu niż
  kontr-trendowe → asymetria progu kierunku.
  https://www.sciencedirect.com/science/article/abs/pii/S0304405X11002613
- **ADX (Average Directional Index)** — J. Welles Wilder (1978), *New Concepts in
  Technical Trading Systems*: ADX < 20-25 = brak trendu, ≥ 25 = trend wyraźny.

## Status wdrożenia

- Kod: `imperium/pretorianie/filtr_asymetrii.py` (`FiltrAsymetriiRezimu`)
- Wpięcie: opt-in (OFF) na `Dyrygent` / `Dyrygent.zbuduj` / `backtest_portfel` / `petla_live`
- Testy: `tests/test_filtr_asymetrii.py` (15 testów granic) + integracja w `test_zbuduj_warstwy.py`
- Czysty OHLCV (CLOSE/EMA_200/ADX_14) — nigdy martwy głos w backteście (kontrast: PSY-01/02/04 czekają na feed futures)

## Następny krok (rekomendacja)

- Walk-forward: ucz progi (prog_kontr/prog_range) na 2017–2023, testuj 2024–2026 —
  potwierdzić, że progi nie są przeuczone na to konkretne okno.
- Rozważyć włączenie w produkcji (decyzja Cezara — Prawo XVIII) po walk-forward.
