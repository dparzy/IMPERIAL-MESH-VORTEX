# 📊 POMIAR WARSTW ADAPTACYJNYCH — ablacja (Prawo XVI)

> **Stan na:** 2026-06-13 · **Metoda:** backtest portfelowy in-sample · **Status:** ⚠️ in-sample, wymaga OOS

## Cel

Zmierzyć, która z 4 warstw adaptacyjnych (W-299/303/307/309) faktycznie poprawia
wynik, a która jest kosmetyką lub redundancją. **Prawo XVI: redundancja mierzona, nie zgadywana.**

## Warunki pomiaru

- Koszyk 5 par: BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, DOGEUSDT
- Interwał 4H, okno 200, kapitał startowy 10 000$, pełna historia (in-sample)
- Każda warstwa testowana OSOBNO względem baseline (ablacja)
- Walidacja Monte Carlo (shuffle, 400 symulacji) per konfiguracja

## Wyniki

| Konfig | trade | PnL$ | **PnL/trade** | WR | MaxDD_p95 | edge_ok |
|---|---|---|---|---|---|---|
| BASELINE | 524 | +26 152 | +49,9 | 52% | 10,3% | ✅ |
| **synapsy** (W-299) | 531 | +34 213 | **+64,4** | 53% | 10,9% | ✅ |
| **mwu** (W-303) | 879 | +73 028 | **+83,1** | 55% | 10,6% | ✅ |
| igrzyska (W-307) | 542 | +29 953 | +55,3 | 51% | 9,8% | ✅ |
| ksiega_wad (W-309) | 524 | +26 152 | +49,9 | 52% | 10,3% | ✅ |
| WSZYSTKIE razem | 1148 | +102 135 | +89,0 | 55% | 12,4% | ✅ |

## Interpretacja (przez PnL/trade — koryguje confound liczby trade'ów)

- 🥇 **synapsy** — liczba trade'ów bez zmian (531 vs 524), efektywność **+29%**.
  Czysta jakość koalicji neuronów, nie wolumen. **Najmocniejszy dowód realnej przewagi.**
- 🥈 **mwu** — efektywność **+66%** + więcej trade'ów (+68%). Działa, częściowo przez wolumen.
- ⚠️ **igrzyska** — efektywność tylko +11%, WR -1pp. Wątpliwa samodzielnie; prawdopodobnie
  nakłada się z mwu (oba przeważają neurony — patrz nota W-307 o komplementarności).
- ➖ **ksiega_wad** — zero zmiany. Bezpieczny default (`prog_weta=None` → ostrzega, nie wetuje;
  w backteście brak bootstrapu z pamięci — świadomie, by uniknąć lookahead, Prawo I).
  Wartość ujawnia się dopiero z ustawionym `prog_weta` lub w pętli live z cross-session pamięcią.

## 🚨 Zastrzeżenie (Prawo I — bez fałszywej weryfikacji)

**To pomiar IN-SAMPLE na pełnej historii.** Monte Carlo waliduje stabilność edge
względem kolejności trade'ów, ale NIE koryguje biasu trendu (BTC 2017→2026 wzrostowo).
Wzrost PnL przy `mwu` jest częściowo napędzany podwojeniem liczby trade'ów w rynku
historycznie rosnącym.

**Zanim warstwy zostaną włączone w produkcji (decyzja Cezara) — wymagany walk-forward OOS:**
ucz na 2017–2023, testuj 2024–2026. Dopiero przewaga OOS jest dowodem, nie ta tabela.

## Wniosek roboczy

- **synapsy + mwu** to kandydaci do walk-forward OOS (oba pokazują przewagę per-trade).
- **igrzyska** — zmierzyć, czy dokłada coś ponad mwu, czy jest redundantna (Prawo XVI).
- **ksiega_wad** — przetestować z `prog_weta` ustawionym (np. 0.75) i z bootstrapem pamięci.
