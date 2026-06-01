"""
🔱 IMV-ADO | EXP-07 A-TLP Scalper — breakout z kanału zmienności (Donchian + ATR)

Adoptowane z: Generic A-TLP Scalper
Seal: IMV-ADO v1.0 — naprawiony i wzmocniony na potrzeby Imperium

Naprawione błędy oryginału:
  1. PRAWDZIWY ATR: oryginał liczył (high-low).rolling.mean() = zaniżony przy gapach.
     Naprawione: True Range = max(H-L, |H-prevC|, |L-prevC|).
  2. BREAKOUT TYLKO NA PRZEBICIU: oryginał dawał signal na każdym barze powyżej progu
     (fałszywe sygnały gdy cena trwa nad progiem). Naprawione: wymagamy by poprzedni
     bar był WEWNĄTRZ kanału (świeży breakout).
  3. FILTR REŻIMU AKTYWNY: oryginał miał zakomentowany filtr ADX = breakouty w
     konsolidacji. Naprawione: ATR_ratio (TRENDING/CHOPPY) blokuje słabe breakouty.
  4. USUNIĘTY MARTWY PARAMETR: breakout_pct był zdefiniowany ale nieużywany.

Dlaczego Exploratores:
  Kanał Donchian (rolling max/min) + prawdziwy ATR wymagają serii barów.
  Detekcja świeżego przebicia wymaga poprzedniego stanu kanału.

Logika:
  channel_top    = max(high) z channel_period barów (bez bieżącego)
  channel_bottom = min(low)  z channel_period barów (bez bieżącego)
  target_up   = channel_top + atr_mult × ATR
  target_down = channel_bottom - atr_mult × ATR
  LONG  gdy close przebija target_up   ORAZ poprzedni close był < poprzedni target_up
  SHORT gdy close przebija target_down ORAZ poprzedni close był > poprzedni target_down
"""

from typing import List, Dict, Any, Tuple, Optional

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _atr_series(bary: List[Dict]) -> List[float]:
    """Prawdziwy True Range — uwzględnia previous close (naprawia błąd oryginału)."""
    trs = [bary[0].get("high", 0) - bary[0].get("low", 0)] if bary else []
    for i in range(1, len(bary)):
        h = bary[i].get("high", 0)
        l = bary[i].get("low", 0)
        pc = bary[i - 1].get("close", 0)
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return trs


def _atr_at(trs: List[float], idx: int, period: int = 14) -> float:
    """ATR (rolling mean TR) kończący na idx włącznie."""
    start = max(0, idx - period + 1)
    window = trs[start:idx + 1]
    return sum(window) / len(window) if window else 0.0


def _kanal(bary: List[Dict], idx: int, period: int) -> Tuple[float, float]:
    """
    Kanał Donchian dla bara idx: max(high)/min(low) z period POPRZEDNICH barów
    (nie wliczamy bieżącego — by przebicie było mierzone względem przeszłości).
    """
    start = max(0, idx - period)
    if start >= idx:
        return bary[idx].get("high", 0), bary[idx].get("low", 0)
    highs = [b.get("high", 0) for b in bary[start:idx]]
    lows = [b.get("low", 0) for b in bary[start:idx]]
    return max(highs), min(lows)


class ZwiadowcaTLP(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-07 A-TLP Scalper
    Breakout z kanału zmienności z prawdziwym ATR i filtrem reżimu.
    """
    KLUCZ = "EXP-07"
    WSKAZNIK = "ATLP_SCALPER"
    LEGION = "SCALP"
    KATEGORIA = "T"  # Breakout = trend-following
    WAGA = 7

    CHANNEL_PERIOD: int = 20
    ATR_PERIOD: int = 14
    ATR_MULT: float = 1.5
    VOL_RATIO_MIN: float = 0.9   # poniżej = CHOPPY → blokuj breakout
    WYMAGA_BAROW: int = 30

    def analizuj(self, bary: List[Dict]) -> RaportZwiadowcy:
        if len(bary) < self.WYMAGA_BAROW:
            return self._brak_danych(
                f"Za mało barów: {len(bary)} < {self.WYMAGA_BAROW}"
            )

        trs = _atr_series(bary)
        n = len(bary) - 1  # bieżący bar

        # ATR bieżący i jego MA (filtr reżimu)
        atr = _atr_at(trs, n, self.ATR_PERIOD)
        atr_ma_vals = [_atr_at(trs, i, self.ATR_PERIOD)
                       for i in range(max(0, n - self.CHANNEL_PERIOD), n + 1)]
        atr_ma = sum(atr_ma_vals) / len(atr_ma_vals) if atr_ma_vals else atr
        vol_ratio = atr / atr_ma if atr_ma > 0 else 1.0
        rezim = "TRENDING" if vol_ratio >= self.VOL_RATIO_MIN else "CHOPPY"

        # Kanał + progi bieżące
        top, bottom = _kanal(bary, n, self.CHANNEL_PERIOD)
        target_up = top + self.ATR_MULT * atr
        target_down = bottom - self.ATR_MULT * atr

        # Kanał + progi poprzednie (do detekcji ŚWIEŻEGO przebicia)
        top_prev, bottom_prev = _kanal(bary, n - 1, self.CHANNEL_PERIOD)
        atr_prev = _atr_at(trs, n - 1, self.ATR_PERIOD)
        target_up_prev = top_prev + self.ATR_MULT * atr_prev
        target_down_prev = bottom_prev - self.ATR_MULT * atr_prev

        close = bary[n].get("close", 0)
        close_prev = bary[n - 1].get("close", 0)

        # Świeży breakout: bieżący przebija, poprzedni był wewnątrz
        long_breakout = close > target_up and close_prev <= target_up_prev
        short_breakout = close < target_down and close_prev >= target_down_prev

        powody = [
            f"close={close:.4f}",
            f"target_up={target_up:.4f}",
            f"target_down={target_down:.4f}",
            f"ATR={atr:.4f}",
            f"Rezim={rezim}(×{vol_ratio:.2f})",
        ]

        diag = {"main_value": close, "atr": atr, "vol_ratio": vol_ratio}

        # Filtr reżimu: nie handluj breakoutów w konsolidacji
        if rezim == "CHOPPY":
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=[f"Zablokowany: CHOPPY (ATR_ratio={vol_ratio:.2f} < {self.VOL_RATIO_MIN})"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        if long_breakout:
            # Siła = jak głęboko przebił próg względem ATR
            sila = min(1.0, (close - target_up) / atr) if atr > 0 else 0.5
            pewnosc = min(0.85, 0.60 + sila * 0.25)
            return self._buduj_raport(
                kierunek="LONG", pewnosc=pewnosc,
                powody=[f"A-TLP BREAKOUT UP: close przebił {target_up:.4f} (świeże)"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        if short_breakout:
            sila = min(1.0, (target_down - close) / atr) if atr > 0 else 0.5
            pewnosc = min(0.85, 0.60 + sila * 0.25)
            return self._buduj_raport(
                kierunek="SHORT", pewnosc=pewnosc,
                powody=[f"A-TLP BREAKOUT DOWN: close przebił {target_down:.4f} (świeże)"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        return self._buduj_raport(
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=["Brak świeżego przebicia kanału"] + powody,
            diagnostics=diag, n_barow=len(bary),
        )
