"""
🛰️💎 RADAR BTC — strażnik lidera rynku (W-291, lead-lag).

WIZJA CEZARA: "BTC prowadzi — gdy BTC spada, alty lecą za nim; gdy BTC rośnie, masz
wiatr w plecy. Chcę radar, który obserwuje BTC i główne waluty i mówi: UWAŻAJ /
TERAZ." Realizuje WIZJONER W-071 (Transfer Entropy: BTC→alty), W-085/086 (intermarket
/ siła względna, Murphy BIB-002) — jako KOD, nie ideę.

ZASADA (udokumentowana w literaturze rynku krypto): Bitcoin jest liderem; jego ruchy
wyprzedzają i pociągają altcoiny (lead-lag, wysoka korelacja w stresie). Dlatego stan
BTC to KONTEKST dla każdej decyzji na alcie.

`RadarBTC.trend(close_btc)` → BTC_TREND ∈ [-1, +1]:
  • +1 = BTC w silnym trendzie wzrostowym (wiatr w plecy dla LONG altów)
  •  0 = BTC płaski / niezdecydowany
  • -1 = BTC w silnym spadku (alty lecą za nim — ostrzeżenie/weto LONG-ów)

Czysta matematyka (Prawo I): momentum EMA-short vs EMA-long znormalizowane przez
zmienność → tanh do [-1,1]. Bez API — liczone z barów BTC, które i tak mamy.
"""

import math
from typing import List, Sequence


def _ema(wartosci: Sequence[float], okres: int) -> float:
    """EMA ostatniej wartości (prosty, bez TA-Lib — Radar musi działać wszędzie)."""
    if not wartosci:
        return 0.0
    k = 2.0 / (okres + 1)
    e = wartosci[0]
    for w in wartosci[1:]:
        e = w * k + e * (1 - k)
    return e


class RadarBTC:
    """
    Użycie:
        r = RadarBTC()
        bt = r.trend([b["close"] for b in bary_btc])   # -1..+1
        # inject do wskaźników altów: wskazniki["BTC_TREND"] = bt
    """

    def __init__(self, ema_szybka: int = 10, ema_wolna: int = 30,
                 okno_vol: int = 20):
        if ema_szybka >= ema_wolna:
            raise ValueError("ema_szybka musi być < ema_wolna")
        if okno_vol < 5:
            raise ValueError("okno_vol musi być ≥ 5")
        self.ema_szybka = ema_szybka
        self.ema_wolna = ema_wolna
        self.okno_vol = okno_vol

    def trend(self, close_btc: List[float]) -> "float | None":
        """
        BTC_TREND ∈ [-1,+1] z serii zamknięć BTC. None gdy za mało danych
        (Prawo XV — bez halucynacji; radar milczy zamiast zgadywać).
        """
        c = [float(x) for x in close_btc if x is not None]
        if len(c) < self.ema_wolna + self.okno_vol:
            return None
        es = _ema(c[-self.ema_wolna * 3:], self.ema_szybka)
        ew = _ema(c[-self.ema_wolna * 3:], self.ema_wolna)
        if ew <= 0:
            return None
        # rozjazd EMA znormalizowany zmiennością zwrotów (skala odporna na cenę)
        zwroty = [(c[i] - c[i - 1]) / c[i - 1] for i in range(-self.okno_vol, 0)
                  if c[i - 1] > 0]
        if not zwroty:
            return None
        sd = (sum(z * z for z in zwroty) / len(zwroty)) ** 0.5
        if sd <= 0:
            return 0.0
        rozjazd = (es - ew) / ew
        # 3×sd ruchu EMA ≈ pełny trend → tanh nasyca do ±1
        return max(-1.0, min(1.0, math.tanh(rozjazd / (3 * sd))))
