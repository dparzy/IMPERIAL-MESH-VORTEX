"""
🔱 IMV-ADO | EXP-09 Liquidity Sweep — stop-hunt fade scalper (Hit & Run)

Adoptowane z: SMC Scalping Engine ("Hit & Run")
Seal: IMV-ADO v1.0 — naprawiony i wzmocniony na potrzeby Imperium

Naprawione błędy oryginału:
  1. ❌ LOOKAHEAD BIAS (KRYTYCZNY): oryginał liczył swing_high z .shift(-1)/.shift(-2)
     — odwołanie do PRZYSZŁYCH barów. W realtime niewykonalne, w backteście kłamie.
     Naprawione: detekcja sweepu i odwrócenia używa WYŁĄCZNIE zamkniętych barów
     z przeszłości (.shift(1) na rolling max/min).
  2. PRAWDZIWY ATR: True Range z previous close zamiast (high-low).mean().
  3. USUNIĘTY MARTWY KOD: oryginał liczył swing_high/swing_low i ich nie używał
     (signal opierał się tylko na liquidity_sweep). Tu liczymy tylko to, co działa.

Koncept (Liquidity Sweep / Stop Hunt — komplementarny do EXP-05):
  EXP-05 = OB/FVG/BOS/MSS (strefy i struktura).
  EXP-09 = polowanie na płynność (stop hunt) — czego EXP-05 NIE wykrywa.
  Smart money wybija poprzedni swing high (zbiera stopy longów), potem cena
  zawraca w dół = pułapka → SHORT. Lustrzanie dla swing low → LONG.

Logika "Hit & Run":
  sweep_high  = high bieżącego bara > max(high) z lookback barów wstecz (bez bieżącego)
  reversal    = bar zamyka się przeciwnie (sweep high + close<open = fakeout w górę)
  sygnał      = fade kierunku sweepu (sweep high → SHORT, sweep low → LONG)
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


class ZwiadowcaLiquiditySweep(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-09 Liquidity Sweep
    Stop-hunt fade scalper — wykrywa zebranie płynności i odwrócenie.
    """
    KLUCZ = "EXP-09"
    WSKAZNIK = "LIQUIDITY_SWEEP"
    LEGION = "SCALP"
    KATEGORIA = "S"  # Struktura (SMC)
    WAGA = 8

    SWING_LOOKBACK: int = 10
    ATR_PERIOD: int = 14
    WYMAGA_BAROW: int = 20

    def analizuj(self, bary: List[Dict]) -> RaportZwiadowcy:
        if len(bary) < self.WYMAGA_BAROW:
            return self._brak_danych(
                f"Za mało barów: {len(bary)} < {self.WYMAGA_BAROW}"
            )

        n = len(bary) - 1
        bar = bary[n]
        high = bar.get("high", 0)
        low = bar.get("low", 0)
        close = bar.get("close", 0)
        open_ = bar.get("open", 0)

        # Poprzednie ekstrema — TYLKO przeszłość (bez lookahead!)
        # Okno: lookback barów PRZED bieżącym (indeksy n-lookback .. n-1)
        start = max(0, n - self.SWING_LOOKBACK)
        prev_highs = [b.get("high", 0) for b in bary[start:n]]
        prev_lows = [b.get("low", 0) for b in bary[start:n]]
        if not prev_highs:
            return self._brak_danych("Brak okna lookback")

        max_prev_high = max(prev_highs)
        min_prev_low = min(prev_lows)

        trs = _atr_series(bary)
        atr = _atr_at(trs, n, self.ATR_PERIOD)

        # Sweep: bieżący bar wybił poprzednie ekstremum
        sweep_high = high > max_prev_high
        sweep_low = low < min_prev_low

        # Reversal: zamknięcie przeciwne do kierunku wybicia (fakeout)
        bearish_close = close < open_
        bullish_close = close > open_

        powody = [
            f"high={high:.4f} vs max_prev={max_prev_high:.4f}",
            f"low={low:.4f} vs min_prev={min_prev_low:.4f}",
            f"close={close:.4f} open={open_:.4f}",
            f"sweep_high={sweep_high} sweep_low={sweep_low}",
            f"ATR={atr:.4f}",
        ]
        diag = {"main_value": close, "atr": atr}

        # FADE sweep high: zebrano stopy longów, cena zawraca → SHORT
        if sweep_high and bearish_close:
            # Siła: jak daleko wybił ponad ekstremum (względem ATR)
            penetracja = (high - max_prev_high) / atr if atr > 0 else 0.5
            sila = min(1.0, penetracja)
            pewnosc = min(0.85, 0.60 + sila * 0.25)
            return self._buduj_raport(
                kierunek="SHORT", pewnosc=pewnosc,
                powody=[f"LIQUIDITY SWEEP HIGH + odwrócenie (fakeout w górę) → SHORT"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        # FADE sweep low: zebrano stopy shortów, cena zawraca → LONG
        if sweep_low and bullish_close:
            penetracja = (min_prev_low - low) / atr if atr > 0 else 0.5
            sila = min(1.0, penetracja)
            pewnosc = min(0.85, 0.60 + sila * 0.25)
            return self._buduj_raport(
                kierunek="LONG", pewnosc=pewnosc,
                powody=[f"LIQUIDITY SWEEP LOW + odwrócenie (fakeout w dół) → LONG"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        # Sweep bez odwrócenia = możliwy prawdziwy breakout, nie fade
        if sweep_high or sweep_low:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=["Sweep bez odwrócenia świecy — brak fade (możliwy prawdziwy breakout)"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        return self._buduj_raport(
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=["Brak sweepu płynności"] + powody,
            diagnostics=diag, n_barow=len(bary),
        )
