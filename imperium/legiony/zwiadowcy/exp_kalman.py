"""
🎯 IMV-EXP | EXP-04 Kalman Filter ATR — adaptacyjny filtr trendu

DLACZEGO W EXPLORATORES:
  Filtr Kalmana jest REKURENCYJNY — stan x[i] zależy od x[i-1] przez wszystkie bary.
  Brama może dać ATR z TA-Lib, ale nie może dać Kalmana bez historii stanu.
  Nawet 1 bar wstecz jest niewystarczający — Kalman "rozgrzewa" się przez kilkanaście barów.

CZYM SĄ ULEPSZONE WZGLĘDEM ZWYKŁEGO ATR:
  Zwykły ATR (TA-Lib) = prosta lub EMA z True Range. Reaguje jednakowo na szum i prawdziwy ruch.
  Kalman ATR = obserwuje True Range przez model liniowy z kowariancją szumu procesowego (Q)
  i szumu pomiaru (R). Adaptuje się: gdy rynek jest spokojny → Q/R małe → filter wygładza.
  Gdy rynek jest zmienny → Q/R duże → filter szybciej podąża za zmianami.

  Praktycznie: lepsza detekcja breakoutów (nagłe zwiększenie filtrego TR = volatility spike).
  Mniejsze fałszywe sygnały w konsolidacji (filter wygładza losowe skoki).

SYGNAŁ DLA LEGATUSA:
  Momentum = (close[-1] - kalman_midline) / kalman_atr
  momentum > 1.5 → LONG (silne wybicie ponad filtr)
  momentum < -1.5 → SHORT
  kalman_atr spike > 2× 20-period avg → VOLATILITY_ALERT w diagnostics
"""

import math
import time
from typing import List, Dict, Any, Tuple

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


def _kalman_filter_1d(
    observations: List[float],
    q: float = 0.01,   # szum procesowy (jak szybko zmienia się "prawdziwy" stan)
    r: float = 1.0,    # szum pomiaru (jak dużo szumu ma obserwacja)
) -> List[float]:
    """
    Jednowymiardowy filtr Kalmana dla serii skalowej.
    Zwraca wygładzoną serię (same długości co observations).

    Model: x_k = x_{k-1} + w_k  (w_k ~ N(0,Q))
           z_k = x_k + v_k      (v_k ~ N(0,R))

    Małe Q = wolna adaptacja (silne wygładzanie).
    Duże Q = szybka adaptacja (śledzi obserwacje blisko).
    """
    if not observations:
        return []

    x = observations[0]  # inicjalizacja stanu = pierwsza obserwacja
    p = 1.0              # inicjalizacja kowariancji błędu estymacji
    filtered = []

    for z in observations:
        # Predykcja
        p_pred = p + q
        # Korekcja (Kalman Gain)
        k_gain = p_pred / (p_pred + r)
        x = x + k_gain * (z - x)
        p = (1 - k_gain) * p_pred
        filtered.append(x)

    return filtered


def _true_range_series(bary: List[Dict]) -> List[float]:
    """True Range dla każdego baru (poza pierwszym)."""
    trs = []
    for i in range(1, len(bary)):
        h = bary[i].get("high", 0)
        l = bary[i].get("low", 0)
        prev_c = bary[i - 1].get("close", 0)
        trs.append(max(h - l, abs(h - prev_c), abs(l - prev_c)))
    return trs


def _kalman_atr(bary: List[Dict], q: float = 0.005, r: float = 0.8) -> Tuple[float, List[float]]:
    """
    Oblicza Kalman-ATR z serii OHLCV.
    Zwraca (ostatnia_wartość_kalman_atr, pełna_seria_kalman_atr).
    """
    trs = _true_range_series(bary)
    if not trs:
        return 0.0, []
    filtered = _kalman_filter_1d(trs, q=q, r=r)
    return filtered[-1], filtered


def _kalman_midline(bary: List[Dict], q: float = 0.01, r: float = 2.0) -> float:
    """
    Kalman-wygładzona cena środkowa (HL/2 lub close).
    Stabilna linia odniesienia dla momentum.
    """
    mids = [(b.get("high", 0) + b.get("low", 0)) / 2 for b in bary]
    if not mids:
        return 0.0
    filtered = _kalman_filter_1d(mids, q=q, r=r)
    return filtered[-1]


class ZwiadowcaKalmanATR(ZwiadowcaElitarny):
    """
    🎯 IMV-EXP | EXP-04 Kalman Filter ATR — adaptacyjna zmienność + momentum
    Filtr Kalmana na True Range daje gładsza niż standardowy ATR bez opóźnienia EMA.
    """
    KLUCZ = "EXP-04"
    WSKAZNIK = "KALMAN_ATR"
    KATEGORIA = "M"
    WAGA = 8
    WYMAGA_BAROW = 30
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = (
        "Kalman Filter na True Range = adaptacyjny ATR bez opóźnienia EMA. "
        "Momentum = (close - Kalman_midline) / Kalman_ATR. "
        "Wymaga rekurencji przez całą historię — niemożliwe w jednym barze Bramy."
    )

    MOMENTUM_PROG = 1.5     # |momentum| > prog → sygnał
    SPIKE_MNOZNIK = 2.0     # kalman_atr > spike_mnoznik * avg → alert zmienności

    # Parametry Kalmana — skalibrowane do krypto 1H
    Q_ATR = 0.005   # wolna adaptacja TR (ATR nie skacze przy każdym barze)
    R_ATR = 0.8
    Q_MID = 0.010   # szybsza adaptacja midline
    R_MID = 2.0

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()

        ok, komunikat = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(komunikat)

        katr, katr_series = _kalman_atr(bary, q=self.Q_ATR, r=self.R_ATR)
        kmid = _kalman_midline(bary, q=self.Q_MID, r=self.R_MID)
        close = float(bary[-1].get("close", 0))
        czas_ms = (time.time() - t0) * 1000

        # Średni Kalman-ATR z ostatnich 20 barów (do detekcji spike)
        avg_katr = sum(katr_series[-20:]) / len(katr_series[-20:]) if katr_series else 1.0

        # Momentum = odchylenie znormalizowane przez zmienność
        momentum = (close - kmid) / katr if katr > 0 else 0.0

        # Detekcja spike zmienności
        volatility_spike = katr > self.SPIKE_MNOZNIK * avg_katr

        pewnosc_metody = sum(1 for b in bary if b.get("close", 0) > 0) / len(bary)
        diagnostics = {
            "main_value": round(momentum, 4),
            "kalman_atr": round(katr, 6),
            "kalman_midline": round(kmid, 4),
            "momentum": round(momentum, 4),
            "avg_katr_20": round(avg_katr, 6),
            "volatility_spike": volatility_spike,
            "spike_ratio": round(katr / avg_katr, 3) if avg_katr > 0 else 0.0,
        }

        ostrzezenia = []
        if volatility_spike:
            ostrzezenia.append(
                f"VOLATILITY SPIKE: Kalman-ATR={katr:.4f} to {katr/avg_katr:.1f}× powyżej średniej"
            )

        if momentum > self.MOMENTUM_PROG:
            pewnosc = min(0.90, 0.65 + (momentum - self.MOMENTUM_PROG) * 0.10)
            return self._buduj_raport(
                kierunek="LONG",
                pewnosc=round(pewnosc, 4),
                powody=[
                    f"Momentum={momentum:+.2f} > +{self.MOMENTUM_PROG} — cena powyżej Kalman midline",
                    f"Kalman-ATR={katr:.4f} | midline={kmid:.2f}",
                ],
                diagnostics=diagnostics, n_barow=len(bary),
                pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
                ostrzezenia=ostrzezenia,
            )

        if momentum < -self.MOMENTUM_PROG:
            pewnosc = min(0.90, 0.65 + (abs(momentum) - self.MOMENTUM_PROG) * 0.10)
            return self._buduj_raport(
                kierunek="SHORT",
                pewnosc=round(pewnosc, 4),
                powody=[
                    f"Momentum={momentum:+.2f} < -{self.MOMENTUM_PROG} — cena poniżej Kalman midline",
                    f"Kalman-ATR={katr:.4f} | midline={kmid:.2f}",
                ],
                diagnostics=diagnostics, n_barow=len(bary),
                pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
                ostrzezenia=ostrzezenia,
            )

        return self._buduj_raport(
            kierunek="NEUTRAL",
            pewnosc=0.0,
            powody=[f"Momentum={momentum:+.2f} w strefie neutralnej (±{self.MOMENTUM_PROG})"],
            diagnostics=diagnostics, n_barow=len(bary),
            pewnosc_metody=pewnosc_metody, czas_ms=czas_ms,
            ostrzezenia=ostrzezenia,
        )
