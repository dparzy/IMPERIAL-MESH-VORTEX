"""
W-383: PIN (Probability of Informed Trading) jako zwiadowca (O'Hara BIB-032, INF-44).

EXP-15 | Estymuje proporcję transakcji od inwestorów Z INFORMACJĄ na podstawie
asymetrii buy/sell volume (tick-rule proxy z OHLCV — jak EXP-14 Kyle's Lambda).

Wysoki PIN → rynek „wie coś czego my nie wiemy" (adverse selection) → ostrożność.
Komplementarny do VPIN (Z-01: imbalance) i Kyle's Lambda (EXP-14: price impact).
Prawo XVI: mierzy korelację z tymi sygnałami live i ostrzega gdy redundantny.
"""

from __future__ import annotations

import time
import logging
from typing import List, Dict, Any

import numpy as np

from imperium.legiony.zwiadowcy.baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych
from imperium.legiony.mikrostruktura import pin_metoda_momentow

logger = logging.getLogger("Exploratores")


class ZwiadowcaPIN(ZwiadowcaElitarny):
    """
    EXP-15 | PIN — Probability of Informed Trading (W-383, O'Hara BIB-032).

    Buduje buy/sell volume z OHLCV przez tick-rule proxy (BTP=(close-low)/(high-low)),
    następnie liczy PIN metodą momentów (mikrostruktura.pin_metoda_momentow).

    HIGH_PIN → dużo informed trading → NEUTRAL z wysoką pewnoscia_przeciwnika
               (tłumi rój — handel przeciw poinformowanym jest groźny).
    """

    KLUCZ = "EXP-15"
    LEGION = "EXPLORATORES"
    WSKAZNIK = "PIN"
    KATEGORIA = "L"
    WAGA = 6
    WYMAGA_BAROW = 30
    TYP_DANYCH = TypDanych.OHLCV
    OPIS_METODY = (
        "PIN (Probability of Informed Trading) metodą momentów na buy/sell z tick-rule. "
        "Komplementarny do VPIN (Z-01). BIB-032 O'Hara rozdz. 3."
    )
    ELITARNY = True
    POWOD_ELITARNOSCI = "E1: Exploratores — PIN metodą momentów w pure numpy (BIB-032 O'Hara)"

    _PROG_WYSOKI = 0.35      # PIN > 0.35 → podwyższony udział informed
    _PROG_EKSTREMALNY = 0.55  # PIN > 0.55 → silny adverse selection

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        t0 = time.time()
        ok, msg = self._waliduj_bary(bary)
        if not ok:
            return self._brak_danych(msg)

        closes = np.array(self._pobierz_close(bary), dtype=float)
        highs = np.array(self._pobierz_high(bary), dtype=float)
        lows = np.array(self._pobierz_low(bary), dtype=float)
        volumes = np.array(self._pobierz_volume(bary), dtype=float)

        ranges = highs - lows
        with np.errstate(divide="ignore", invalid="ignore"):
            btp = np.where(ranges > 1e-10, (closes - lows) / ranges, 0.5)
        buy_vol = btp * volumes
        sell_vol = volumes - buy_vol

        wynik = pin_metoda_momentow(buy_vol, sell_vol)
        pin = wynik["pin"]

        if np.isnan(pin):
            return self._brak_danych("PIN nieobliczalny (za mało danych)")

        diag = {
            "main_value": pin,
            "pin": pin,
            "epsilon": wynik["epsilon"],
            "informed_flow": wynik["informed_flow"],
        }

        if pin >= self._PROG_EKSTREMALNY:
            # silny adverse selection → tłumimy rój (NEUTRAL + wysoka przeciwnika)
            pewnosc_p = round(min(0.85, 0.60 + (pin - self._PROG_EKSTREMALNY) * 1.0), 4)
            raport = self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=[f"🚨 PIN={pin:.3f} EKSTREMALNY — silny informed trading, "
                        f"tłumię rój (adverse selection)"],
                diagnostics=diag, n_barow=len(bary),
                pewnosc_metody=1.0, czas_ms=(time.time() - t0) * 1000,
            )
            raport.sygnal.pewnosc_przeciwnika = pewnosc_p
            raport.sygnal.policz_finalna()
            return raport

        if pin >= self._PROG_WYSOKI:
            pewnosc_p = round(min(0.55, 0.30 + (pin - self._PROG_WYSOKI) * 1.0), 4)
            raport = self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=[f"⚠️ PIN={pin:.3f} podwyższony — umiarkowany informed trading"],
                diagnostics=diag, n_barow=len(bary),
                pewnosc_metody=1.0, czas_ms=(time.time() - t0) * 1000,
            )
            raport.sygnal.pewnosc_przeciwnika = pewnosc_p
            raport.sygnal.policz_finalna()
            return raport

        return self._buduj_raport(
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=[f"PIN={pin:.3f} niski — flow zdominowany przez płynność (nie info)"],
            diagnostics=diag, n_barow=len(bary),
            pewnosc_metody=1.0, czas_ms=(time.time() - t0) * 1000,
        )
