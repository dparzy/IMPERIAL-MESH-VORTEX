"""
🔱 IMV-ADO | EXP-11 Dynamic Scalper — cross MA z bramką jakości egzekucji

Adoptowane z: Dynamic Pro Scalper v2.1 (slippage protection)
Seal: IMV-ADO v1.0 — naprawiony i wzmocniony na potrzeby Imperium

Naprawione błędy oryginału:
  1. PRAWDZIWY ATR: True Range z previous close zamiast (high-low).rolling.mean().
  2. ATR FAKTYCZNIE UŻYWANY: oryginał liczył atr i NIGDY go nie używał (martwy kod).
     Naprawione: separacja MA musi przekraczać frakcję ATR (anty-whipsaw) — sygnał
     tylko gdy MA rozjechały się znacząco względem zmienności.
  3. CROSS JAKO ZDARZENIE, nie stan: oryginał dawał signal na KAŻDYM barze gdy
     ma_fast > ma_slow (ciągły sygnał = nie scalp). Naprawione: sygnał tylko na
     ŚWIEŻYM przecięciu (poprzedni bar miał odwrotną relację MA).

Wartość unikalna (czego nie ma żaden inny moduł Imperium):
  SLIPPAGE / SPREAD GUARD — bramka jakości egzekucji. Gdy bieżący spread
  (proxy: range/close) przekracza 75. percentyl z 50 barów, fill byłby drogi
  → sygnał wyciszony. To chroni kapitał przed handlem w złych warunkach
  egzekucji (cienki rynek, szeroki spread). Komplementarne do wszystkich
  pozostałych zwiadowców — może być wzorcem do reużycia.

Uwaga (Prawo XV): sama część cross MA jest zbliżona do NeuronEMACross — dlatego
EXP-11 wnosi wartość przez bramkę egzekucji + ATR-potwierdzoną separację, nie przez
sam crossover. Bez tego byłaby to redundancja.
"""

from typing import List, Dict, Any

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _atr_series(bary: List[Dict]) -> List[float]:
    """Prawdziwy True Range — uwzględnia previous close."""
    trs = [bary[0].get("high", 0) - bary[0].get("low", 0)] if bary else []
    for i in range(1, len(bary)):
        h = bary[i].get("high", 0)
        l = bary[i].get("low", 0)
        pc = bary[i - 1].get("close", 0)
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return trs


def _atr_at(trs: List[float], idx: int, period: int) -> float:
    start = max(0, idx - period + 1)
    window = trs[start:idx + 1]
    return sum(window) / len(window) if window else 0.0


def _sma_at(closes: List[float], idx: int, period: int) -> float:
    start = max(0, idx - period + 1)
    window = closes[start:idx + 1]
    return sum(window) / len(window) if window else 0.0


def _percentyl(values: List[float], q: float) -> float:
    """Percentyl liniowy (q w [0,1]) — pure Python."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    poz = q * (len(s) - 1)
    dol = int(poz)
    frac = poz - dol
    if dol + 1 < len(s):
        return s[dol] + frac * (s[dol + 1] - s[dol])
    return s[dol]


class ZwiadowcaDynamic(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-11 Dynamic Scalper
    Cross MA jako zdarzenie + ATR-separacja + bramka jakości egzekucji (spread).
    """
    KLUCZ = "EXP-11"
    WSKAZNIK = "DYNAMIC_CROSS"
    LEGION = "SCALP"
    KATEGORIA = "T"  # trend-following (cross)
    WAGA = 6

    FAST_MA: int = 5
    SLOW_MA: int = 10
    ATR_PERIOD: int = 14
    SEP_ATR_FRAC: float = 0.10   # separacja MA > 10% ATR (anty-whipsaw)
    SPREAD_OKNO: int = 50
    SPREAD_Q: float = 0.75       # spread > 75. percentyl = drogi fill → blokuj
    WYMAGA_BAROW: int = 55

    def analizuj(self, bary: List[Dict]) -> RaportZwiadowcy:
        if len(bary) < self.WYMAGA_BAROW:
            return self._brak_danych(
                f"Za mało barów: {len(bary)} < {self.WYMAGA_BAROW}"
            )

        n = len(bary) - 1
        closes = [b.get("close", 0) for b in bary]

        ma_fast = _sma_at(closes, n, self.FAST_MA)
        ma_slow = _sma_at(closes, n, self.SLOW_MA)
        ma_fast_prev = _sma_at(closes, n - 1, self.FAST_MA)
        ma_slow_prev = _sma_at(closes, n - 1, self.SLOW_MA)

        trs = _atr_series(bary)
        atr = _atr_at(trs, n, self.ATR_PERIOD)

        # Bramka jakości egzekucji (spread guard)
        spready = [
            (b.get("high", 0) - b.get("low", 0)) / b.get("close", 1)
            if b.get("close", 0) else 0.0
            for b in bary[-self.SPREAD_OKNO:]
        ]
        spread_curr = spready[-1] if spready else 0.0
        prog_spread = _percentyl(spready, self.SPREAD_Q)
        spread_zly = spread_curr > prog_spread

        # Cross jako ZDARZENIE
        cross_up = ma_fast > ma_slow and ma_fast_prev <= ma_slow_prev
        cross_down = ma_fast < ma_slow and ma_fast_prev >= ma_slow_prev

        # Separacja względem ATR (anty-whipsaw)
        separacja = abs(ma_fast - ma_slow)
        sep_ok = atr > 0 and separacja > self.SEP_ATR_FRAC * atr

        powody = [
            f"ma_fast={ma_fast:.4f} ma_slow={ma_slow:.4f}",
            f"cross_up={cross_up} cross_down={cross_down}",
            f"separacja={separacja:.4f} (prog={self.SEP_ATR_FRAC * atr:.4f}, ok={sep_ok})",
            f"spread={spread_curr:.5f} (prog75={prog_spread:.5f}, zly={spread_zly})",
            f"ATR={atr:.4f}",
        ]
        diag = {"main_value": ma_fast - ma_slow, "atr": atr}

        # BRAMKA EGZEKUCJI — perełka oryginału, zachowana i naprawiona
        if spread_zly:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["SLIPPAGE GUARD: spread > 75. percentyl — zły fill, sygnał wyciszony"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        if not (cross_up or cross_down):
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Brak świeżego przecięcia MA"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        if not sep_ok:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Separacja MA < frakcji ATR — ryzyko whipsaw, pomijam"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        sila = min(1.0, separacja / atr) if atr > 0 else 0.5
        pewnosc = min(0.80, 0.55 + sila * 0.25)

        if cross_up:
            return self._buduj_raport(
                kierunek="LONG", pewnosc=pewnosc,
                powody=[f"CROSS UP {self.FAST_MA}/{self.SLOW_MA} + separacja ATR OK + spread czysty → LONG"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        return self._buduj_raport(
            kierunek="SHORT", pewnosc=pewnosc,
            powody=[f"CROSS DOWN {self.FAST_MA}/{self.SLOW_MA} + separacja ATR OK + spread czysty → SHORT"] + powody,
            diagnostics=diag, n_barow=len(bary),
        )
