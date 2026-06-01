"""
🔱 IMV-ADO | EXP-02 HA Scalper Full — pełna implementacja MSX Hybrid Heiken Scalper

Dlaczego w Exploratores (nie w MikroNeuron):
  Pełna wersja HA Scalper oblicza HA_Open jako (prev_HA_Open + prev_HA_Close)/2 —
  to rekurencyjna zależność od całej historii, nie pojedynczego baru.
  Brama może dać snapshot (jeden bar), ale Exploratores daje pełną serię →
  dokładniejszy HA bez przybliżeń.

  Wersja X-26 w momentum.py = uproszczona (Brama daje gotowe HA_BULL/HA_BEAR).
  Ta wersja = pełna (liczy HA sama z surowych OHLCV).

Ulepszenia względem oryginału MSX:
  1. HA bez repainting — obliczamy HA_Open rekurencyjnie z surowych OHLC
  2. Volatility_Index = ATR_14/MidPrice_MA20 — dynamiczny filtr zmienności
  3. Naprawiony błąd tautologii warunku potwierdzenia
  4. Tryb aggressive/conservative jako parametr instancji
  5. Filtr reżimu blokuje sygnały w konsolidacji
"""

import math
import time
from typing import List, Dict, Any, Optional

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _atr(bary: List[Dict], period: int = 14) -> float:
    """ATR z surowych OHLCV — pure Python."""
    if len(bary) < 2:
        return 0.0
    trs = []
    for i in range(1, len(bary)):
        h = bary[i].get("high", 0)
        l = bary[i].get("low", 0)
        prev_c = bary[i - 1].get("close", 0)
        tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
        trs.append(tr)
    last_n = trs[-period:] if len(trs) >= period else trs
    return sum(last_n) / len(last_n) if last_n else 0.0


def _mid_price_ma(bary: List[Dict], window: int = 20) -> float:
    """MidPrice MA — (High+Low)/2, rolling mean."""
    mids = [(b.get("high", 0) + b.get("low", 0)) / 2 for b in bary]
    last_n = mids[-window:] if len(mids) >= window else mids
    return sum(last_n) / len(last_n) if last_n else 0.0


def _oblicz_ha(bary: List[Dict]) -> List[Dict]:
    """
    Oblicza Heiken Ashi bez repainting z surowych OHLCV.
    HA_Open[0] = (Open[0] + Close[0]) / 2 — inicjalizacja
    HA_Open[i] = (HA_Open[i-1] + HA_Close[i-1]) / 2 — rekurencja
    """
    ha = []
    for i, b in enumerate(bary):
        ha_close = (b.get("open", 0) + b.get("high", 0) + b.get("low", 0) + b.get("close", 0)) / 4
        if i == 0:
            ha_open = (b.get("open", 0) + b.get("close", 0)) / 2
        else:
            ha_open = (ha[i - 1]["ha_open"] + ha[i - 1]["ha_close"]) / 2
        ha_high = max(b.get("high", 0), ha_open, ha_close)
        ha_low = min(b.get("low", 0), ha_open, ha_close)
        ha.append({
            "ha_open": ha_open, "ha_close": ha_close,
            "ha_high": ha_high, "ha_low": ha_low,
            "mid": (ha_high + ha_low) / 2,
        })
    return ha


class ZwiadowcaHAScalper(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.1 | EXP-02 HA Scalper Full
    Pełna implementacja MSX Hybrid Heiken Scalper z rekurencyjnym HA.
    """
    KLUCZ = "EXP-02"
    WSKAZNIK = "HA_SCALPER_FULL"
    KATEGORIA = "M"
    WAGA = 8
    WYMAGA_BAROW = 25       # min. 25 barów dla stabilnego HA
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = ("Pełny MSX HA Scalper z rekurencyjnym HA_Open (wymaga serii). "
                   "Brama nie może dostarczyć HA_Open bez historii — stąd Exploratores.")

    # Progi Volatility_Index wg reżimu
    VOL_MIN_RANGING = 0.008
    VOL_MIN_TREND = 0.003

    def __init__(self, tryb: str = "aggressive") -> None:
        super().__init__()
        self.tryb = tryb  # "aggressive" lub "conservative"

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()

        ok, komunikat = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(komunikat)

        # Oblicz HA z pełnej historii (bez repainting)
        ha = _oblicz_ha(bary)
        cur = ha[-1]
        prev = ha[-2] if len(ha) >= 2 else cur

        # ATR i Volatility_Index
        atr = _atr(bary, period=14)
        mid_ma = _mid_price_ma(bary, window=20)
        vol_idx = atr / mid_ma if mid_ma > 0 else 0.0

        # Momentum (znormalizowany ATR)
        momentum = ((cur["mid"] - prev["mid"]) / atr) if atr > 0 else 0.0

        # Kierunek HA
        ha_bull = cur["ha_close"] > cur["ha_open"]
        ha_bear = cur["ha_close"] < cur["ha_open"]

        czas_ms = (time.time() - t0) * 1000
        pewnosc_metody = sum(1 for b in bary if b.get("close", 0) > 0) / len(bary)

        diagnostics = {
            "main_value": vol_idx,
            "ha_open": round(cur["ha_open"], 6),
            "ha_close": round(cur["ha_close"], 6),
            "ha_bull": ha_bull,
            "ha_bear": ha_bear,
            "momentum_atr": round(momentum, 4),
            "vol_idx": round(vol_idx, 5),
            "atr": round(atr, 6),
            "mid_ma20": round(mid_ma, 6),
        }

        # Filtr zmienności (blokuje konsolidację)
        vol_min = self.VOL_MIN_RANGING  # konserwatywny próg domyślnie
        if vol_idx < vol_min:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=[f"HA: VolIdx={vol_idx:.5f} < {vol_min} — konsolidacja, brak sygnału"],
                diagnostics=diagnostics, n_barow=len(bary),
                pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
                ostrzezenia=["Zbyt niska zmienność — sygnał pominięty"],
            )

        # Bazowa pewność wg trybu
        pewnosc_baz = 0.65 if self.tryb == "aggressive" else 0.55

        if ha_bull:
            pewnosc = pewnosc_baz + (0.15 if momentum > 0 else -0.15)
            powody = [
                f"HA BULL (rekurencyjny): open={cur['ha_open']:.4f} close={cur['ha_close']:.4f}",
                f"Momentum={momentum:+.3f} ATR {'↑ potwierdzenie' if momentum > 0 else '↓ sprzeczny'}",
                f"VolIdx={vol_idx:.5f} | tryb={self.tryb}",
            ]
            return self._buduj_raport(
                "LONG", max(0.0, pewnosc), powody, diagnostics,
                n_barow=len(bary), pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
            )

        if ha_bear:
            pewnosc = pewnosc_baz + (0.15 if momentum < 0 else -0.15)
            powody = [
                f"HA BEAR (rekurencyjny): open={cur['ha_open']:.4f} close={cur['ha_close']:.4f}",
                f"Momentum={momentum:+.3f} ATR {'↓ potwierdzenie' if momentum < 0 else '↑ sprzeczny'}",
                f"VolIdx={vol_idx:.5f} | tryb={self.tryb}",
            ]
            return self._buduj_raport(
                "SHORT", max(0.0, pewnosc), powody, diagnostics,
                n_barow=len(bary), pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
            )

        return self._buduj_raport(
            "NEUTRAL", 0.0, ["HA Doji — brak dominacji"],
            diagnostics, n_barow=len(bary),
            pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
        )
