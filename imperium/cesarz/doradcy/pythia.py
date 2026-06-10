"""
🏛️ IMV-ORI | PYTHIA — Probabilistic Advisor
Fingerprint matching — szuka podobnych historycznych setupów i liczy p(zysk).
OdciskPalca = (rezim, interwal, kierunek, pewnosc_bin, funding_bin, atr_bin)
"""

import statistics
from dataclasses import dataclass
from enum import Enum
from typing import List


class WerdyktPythia(str, Enum):
    KORZYSTNE = "HISTORYCZNIE KORZYSTNE"
    NEUTRALNE = "NEUTRALNE"
    NIEKORZYSTNE = "HISTORYCZNIE NIEKORZYSTNE"
    MILCZENIE = "MILCZENIE"  # < 10 podobnych setupów


@dataclass
class OdciskPalca:
    """Odcisk palca setupu — używany do fingerprint matching."""
    rezim: str              # "TREND_STRONG" / "RANGING" / "VOLATILE"
    interwal: str           # "1H" / "4H" / "1D"
    kierunek: str           # "LONG" / "SHORT"
    pewnosc_bin: int        # 1=50-60%, 2=60-70%, 3=70-80%, 4=80-90%, 5=90-100%
    funding_bin: int        # 0=negatywny (<-0.01%), 1=neutralny, 2=wysoki (>0.05%)
    atr_bin: int            # 1=niski, 2=normalny, 3=wysoki (relative to 30d avg)


@dataclass
class WpisHistorii:
    """Uproszczony wpis z PamięciAbsolutnej potrzebny PYTHII."""
    odcisk: OdciskPalca
    pnl_pct: float


@dataclass
class OcenaPythia:
    werdykt: WerdyktPythia
    p_zysk: float
    avg_pnl: float
    median_pnl: float
    n_podobnych: int
    powod: str = ""

    @property
    def pozytywny(self) -> bool:
        return self.werdykt in (WerdyktPythia.KORZYSTNE, WerdyktPythia.NEUTRALNE, WerdyktPythia.MILCZENIE)


MIN_SETUPOW = 10
P_ZYSK_KORZYSTNE = 0.60
P_ZYSK_NIEKORZYSTNE = 0.45


def _pewnosc_bin(pewnosc: float) -> int:
    if pewnosc >= 0.90:
        return 5
    if pewnosc >= 0.80:
        return 4
    if pewnosc >= 0.70:
        return 3
    if pewnosc >= 0.60:
        return 2
    return 1


def _funding_bin(funding_rate: float) -> int:
    if funding_rate < -0.0001:
        return 0
    if funding_rate > 0.0005:
        return 2
    return 1


def _atr_bin(atr_current: float, atr_30d_avg: float) -> int:
    if atr_30d_avg <= 0:
        return 2
    ratio = atr_current / atr_30d_avg
    if ratio < 0.7:
        return 1
    if ratio > 1.3:
        return 3
    return 2


def buduj_odcisk(
    rezim: str, interwal: str, kierunek: str,
    pewnosc: float, funding_rate: float,
    atr_current: float, atr_30d_avg: float,
) -> OdciskPalca:
    return OdciskPalca(
        rezim=rezim, interwal=interwal, kierunek=kierunek,
        pewnosc_bin=_pewnosc_bin(pewnosc),
        funding_bin=_funding_bin(funding_rate),
        atr_bin=_atr_bin(atr_current, atr_30d_avg),
    )


def _odcisk_pasuje(wpis: WpisHistorii, obecny: OdciskPalca, tolerancja: int = 1) -> bool:
    """Tolerancja = ile pól bin może się różnić (0 = dokładne, 1 = fuzzy)."""
    o = wpis.odcisk
    # Wymagane dopasowania (bez tolerancji)
    if o.rezim != obecny.rezim:
        return False
    if o.kierunek != obecny.kierunek:
        return False
    # Binne dopasowania z tolerancją
    roznice = (
        abs(o.pewnosc_bin - obecny.pewnosc_bin)
        + abs(o.funding_bin - obecny.funding_bin)
        + abs(o.atr_bin - obecny.atr_bin)
    )
    return roznice <= tolerancja


class Pythia:
    """
    🧮 Doradca V — PYTHIA (Probabilistic Advisor)
    Wymaga WpisHistorii z PamięciAbsolutnej (ostatnie 90d+).
    Jeśli < 10 podobnych setupów → MILCZENIE (nie blokuje).
    """

    def ocen(self, obecny: OdciskPalca, historia: List[WpisHistorii]) -> OcenaPythia:
        podobne = [w for w in historia if _odcisk_pasuje(w, obecny, tolerancja=1)]

        if len(podobne) < MIN_SETUPOW:
            return OcenaPythia(
                werdykt=WerdyktPythia.MILCZENIE,
                p_zysk=0.0, avg_pnl=0.0, median_pnl=0.0,
                n_podobnych=len(podobne),
                powod=f"Za mało historii: {len(podobne)}/{MIN_SETUPOW} podobnych setupów — PYTHIA milczy",
            )

        pnl_lista = [w.pnl_pct for w in podobne]
        p_zysk = sum(1 for p in pnl_lista if p > 0) / len(pnl_lista)
        avg_pnl = sum(pnl_lista) / len(pnl_lista)
        median_pnl = statistics.median(pnl_lista)

        if p_zysk > P_ZYSK_KORZYSTNE and avg_pnl > 0.5:
            werdykt = WerdyktPythia.KORZYSTNE
            powod = f"p(zysk)={p_zysk:.0%}, avg={avg_pnl:.2f}%, median={median_pnl:.2f}%, n={len(podobne)}"
        elif p_zysk < P_ZYSK_NIEKORZYSTNE:
            werdykt = WerdyktPythia.NIEKORZYSTNE
            powod = f"p(zysk)={p_zysk:.0%} < {P_ZYSK_NIEKORZYSTNE:.0%} — historycznie słabe — rozważ odwrót"
        else:
            werdykt = WerdyktPythia.NEUTRALNE
            powod = f"p(zysk)={p_zysk:.0%} — neutralne historycznie, n={len(podobne)}"

        return OcenaPythia(
            werdykt=werdykt, p_zysk=round(p_zysk, 3),
            avg_pnl=round(avg_pnl, 3), median_pnl=round(median_pnl, 3),
            n_podobnych=len(podobne), powod=powod,
        )
