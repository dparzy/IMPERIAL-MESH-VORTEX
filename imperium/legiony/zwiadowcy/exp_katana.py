"""
🔱 IMV-ADO | EXP-06 Katana Scalper Pro — zaawansowany skalpel z redukcją szumu

Adoptowane z: Katana Scalper Pro (Yuki Miyake, MT4, $199)
Seal: IMV-ADO v1.0 — poprawiony i rozszerzony na potrzeby Imperium

Naprawione błędy oryginału:
  1. HA_Open rekurencyjne: (HA_Open[-1] + HA_Close[-1]) / 2 — nie (Open[-1]+Close[-1])/2
     Oryginał twierdził "100% No-Repaint" ale używał buggy formuły = kłamstwo.
     Naprawione: identyczny algorytm jak EXP-02.
  2. MTF rozszerzone: nie tylko rolling max/min 20 barów, ale też 50-barowa ocena
     struktury trendu (HH/HL = uptrend, LL/LH = downtrend)

Dlaczego Exploratores (nie MikroNeuron):
  HA_Open wymaga rekurencji przez całą serię — Brama daje tylko snapshot.
  ATR Deviation, momentum wielopoziomowe, MTF = wymagają OHLCV series.

Główne cechy:
  - Redukcja szumu: HA + adaptacyjny filtr zmienności ATR/ATR_MA
  - Multi-Horizon Inertia: momentum z 20-bar i 50-bar okna
  - Filtr reżimu: Trending vs Choppy (ATR_ratio > 1 = Trending)
  - Potrójne potwierdzenie: HA kolor + Price_momentum + HA_momentum
  - Signal_Strength = |Price_Momentum| / ATR (siła względem zmienności)
"""

import math
from typing import List, Dict, Any, Tuple, Optional

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


# ── Pomocnicze ────────────────────────────────────────────────────────────────

def _oblicz_ha(bary: List[Dict]) -> List[Dict]:
    """
    Rekurencyjny Heiken Ashi — bez repainting.
    Identyczny algorytm jak EXP-02 (współdzielona prawda).
    """
    ha = []
    for i, b in enumerate(bary):
        ha_close = (b.get("open", 0) + b.get("high", 0) +
                    b.get("low", 0) + b.get("close", 0)) / 4
        if i == 0:
            ha_open = (b.get("open", 0) + b.get("close", 0)) / 2
        else:
            ha_open = (ha[i - 1]["ha_open"] + ha[i - 1]["ha_close"]) / 2
        ha.append({
            "ha_open": ha_open,
            "ha_close": ha_close,
            "bull": ha_close >= ha_open,
        })
    return ha


def _atr_series(bary: List[Dict]) -> List[float]:
    """ATR jako seria True Range wartości (do rolling mean)."""
    trs = [0.0]
    for i in range(1, len(bary)):
        h = bary[i].get("high", 0)
        l = bary[i].get("low", 0)
        pc = bary[i - 1].get("close", 0)
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return trs


def _rolling_mean(values: List[float], period: int, idx: int) -> Optional[float]:
    """Rolling mean kończący na idx (włącznie)."""
    start = max(0, idx - period + 1)
    window = values[start:idx + 1]
    if len(window) < period // 2:
        return None
    return sum(window) / len(window)


def _wykryj_rezim(bary: List[Dict], atr_period: int = 14,
                  vol_period: int = 20) -> Tuple[str, float]:
    """
    Adaptacyjny filtr zmienności: ATR / ATR_MA.
    Ratio > 1 = Trending (wysoka zmienność), ≤ 1 = Choppy.
    Zwraca: (rezim, ratio)
    """
    trs = _atr_series(bary)
    n = len(bary) - 1  # ostatni indeks

    atr = _rolling_mean(trs, atr_period, n)
    if atr is None:
        return "UNKNOWN", 1.0

    # ATR_MA: rolling mean of ATR values (przybliżenie — używamy TR bezpośrednio)
    # Bierzemy dwa okna: bieżące ATR i jego MA z vol_period
    atr_values = [
        _rolling_mean(trs, atr_period, i)
        for i in range(max(0, n - vol_period), n + 1)
    ]
    atr_values = [v for v in atr_values if v is not None]
    if not atr_values:
        return "UNKNOWN", 1.0

    atr_ma = sum(atr_values) / len(atr_values)
    if atr_ma == 0:
        return "UNKNOWN", 1.0

    ratio = atr / atr_ma
    rezim = "TRENDING" if ratio > 1.0 else "CHOPPY"
    return rezim, ratio


def _mtf_trend(bary: List[Dict], window_short: int = 20,
               window_long: int = 50) -> str:
    """
    Multi-Horizon Inertia Synchronization (naprawione MTF).
    Używa dwóch okien HH/LL zamiast tylko jednego.
    Zwraca: "UP", "DOWN", "NEUTRAL"
    """
    if len(bary) < window_short:
        return "NEUTRAL"

    closes = [b.get("close", 0) for b in bary]
    highs = [b.get("high", 0) for b in bary]
    lows = [b.get("low", 0) for b in bary]

    # Okno krótkie (20) — dominujący bias
    short_slice_h = highs[-window_short:-1] if len(bary) >= window_short else highs[:-1]
    short_slice_l = lows[-window_short:-1] if len(bary) >= window_short else lows[:-1]
    if not short_slice_h:
        return "NEUTRAL"

    hh_short = max(short_slice_h)
    ll_short = min(short_slice_l)
    last_close = closes[-1]

    # Okno długie (50) — wyższy timeframe
    if len(bary) >= window_long:
        long_slice_h = highs[-window_long:-1]
        long_slice_l = lows[-window_long:-1]
        hh_long = max(long_slice_h)
        ll_long = min(long_slice_l)
        long_up = last_close > hh_long
        long_down = last_close < ll_long
    else:
        long_up = long_down = False

    short_up = last_close > hh_short
    short_down = last_close < ll_short

    # Zgodność obu okien = silniejszy sygnał
    if short_up and (long_up or not long_down):
        return "UP"
    if short_down and (long_down or not long_up):
        return "DOWN"
    return "NEUTRAL"


def _signal_strength(price_momentum: float, atr: float) -> float:
    """Siła sygnału względem zmienności, clipped [0, 1]."""
    if atr <= 0:
        return 0.0
    return min(1.0, abs(price_momentum) / atr)


# ── Zwiadowca ─────────────────────────────────────────────────────────────────

class ZwiadowcaKatana(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-06 Katana Scalper Pro
    Pełna implementacja Katana Scalper Pro z poprawionym HA i rozszerzonym MTF.
    """
    KLUCZ = "EXP-06"
    WSKAZNIK = "KATANA_SCALPER"
    LEGION = "SCALP"
    KATEGORIA = "M"  # Momentum-based scalper
    WAGA = 7

    # Progi
    MIN_STRENGTH: float = 0.5       # minimalna siła sygnału (0-1)
    ATR_PERIOD: int = 14
    VOL_PERIOD: int = 20
    WYMAGA_BAROW: int = 30

    def analizuj(self, bary: List[Dict]) -> RaportZwiadowcy:
        if len(bary) < self.WYMAGA_BAROW:
            return self._brak_danych(
                f"Za mało barów: {len(bary)} < {self.WYMAGA_BAROW}"
            )

        # 1. Heiken Ashi (rekurencyjny — bez repainting)
        ha = _oblicz_ha(bary)
        ha_curr = ha[-1]
        ha_prev = ha[-2]

        # 2. Price momentum (ostatnia świeca)
        close_curr = bary[-1].get("close", 0)
        close_prev = bary[-2].get("close", 0)
        price_momentum = close_curr - close_prev
        ha_momentum = ha_curr["ha_close"] - ha_prev["ha_close"]

        # 3. ATR
        trs = _atr_series(bary)
        atr = _rolling_mean(trs, self.ATR_PERIOD, len(bary) - 1) or 0.0

        # 4. Reżim rynkowy
        rezim, vol_ratio = _wykryj_rezim(bary, self.ATR_PERIOD, self.VOL_PERIOD)

        # 5. MTF trend (Multi-Horizon Inertia)
        mtf = _mtf_trend(bary)

        # 6. Generowanie sygnału
        ha_bull = ha_curr["bull"]
        ha_bear = not ha_curr["bull"]
        strength = _signal_strength(price_momentum, atr)

        # Warunki bazowe
        base_buy = ha_bull and price_momentum > 0 and ha_momentum > 0
        base_sell = ha_bear and price_momentum < 0 and ha_momentum < 0

        # Filtry: reżim + siła + MTF
        buy_ok = base_buy and rezim == "TRENDING" and strength >= self.MIN_STRENGTH and mtf != "DOWN"
        sell_ok = base_sell and rezim == "TRENDING" and strength >= self.MIN_STRENGTH and mtf != "UP"

        powody = [
            f"HA={'BULL' if ha_bull else 'BEAR'}",
            f"Price_Mom={price_momentum:+.4f}",
            f"HA_Mom={ha_momentum:+.4f}",
            f"Strength={strength:.2f}",
            f"ATR={atr:.4f}",
            f"Rezim={rezim}(×{vol_ratio:.2f})",
            f"MTF={mtf}",
        ]

        diag = {"main_value": strength, "atr": atr, "vol_ratio": vol_ratio}

        if buy_ok:
            pewnosc = 0.55 + strength * 0.30  # 0.55..0.85
            return self._buduj_raport(
                kierunek="LONG", pewnosc=min(0.85, pewnosc),
                powody=[f"Katana BUY: HA BULL + momentum + Trending + MTF={mtf}"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )
        if sell_ok:
            pewnosc = 0.55 + strength * 0.30
            return self._buduj_raport(
                kierunek="SHORT", pewnosc=min(0.85, pewnosc),
                powody=[f"Katana SELL: HA BEAR + momentum + Trending + MTF={mtf}"] + powody,
                diagnostics=diag, n_barow=len(bary),
            )

        # Brak sygnału — raportuj powód
        if rezim == "CHOPPY":
            powod_blok = f"Zablokowany: CHOPPY (ATR_ratio={vol_ratio:.2f})"
        elif strength < self.MIN_STRENGTH:
            powod_blok = f"Zbyt słaby sygnał: strength={strength:.2f} < {self.MIN_STRENGTH}"
        elif mtf == "DOWN" and base_buy:
            powod_blok = "MTF DOWN blokuje BUY"
        elif mtf == "UP" and base_sell:
            powod_blok = "MTF UP blokuje SELL"
        else:
            powod_blok = "Brak potrójnego potwierdzenia HA+Price_Mom+HA_Mom"

        return self._buduj_raport(
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=[powod_blok] + powody,
            diagnostics=diag, n_barow=len(bary),
        )
