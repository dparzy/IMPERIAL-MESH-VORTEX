"""
🏛️ IMV-ORI | FULMEN — Regime Validator
Niezależna weryfikacja reżimu rynkowego zestawem ORTOGONALNYM wobec Legatusa.
ADX + Vortex + Choppiness + Kaufman ER
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class WerdyktFulmen(str, Enum):
    ZGODNY = "ZGODNY"        # Reżim potwierdzony — wzmocnienie ×1.2
    NEUTRALNY = "NEUTRALNY"  # Nie można jednoznacznie potwierdzić
    KONFLIKT = "KONFLIKT"    # Reżim sprzeczny z Legatusem — ostrzeżenie


@dataclass
class DaneFulmen:
    """Wskaźniki wymagane przez FULMEN — niezależne od zestawu Legatusa."""
    adx_14: float           # ADX(14): > 25 = trend, < 20 = ranging
    vi_plus_14: float       # Vortex VI+(14)
    vi_minus_14: float      # Vortex VI-(14)
    choppiness_14: float    # Choppiness Index: < 38.2 = trend, > 61.8 = chop
    kaufman_er: float       # Kaufman Efficiency Ratio: > 0.6 = efektywny ruch
    legatus_rezim: str      # Reżim zgłoszony przez Legatusa (np. "TREND_STRONG")


@dataclass
class OcenaFulmen:
    werdykt: WerdyktFulmen
    adx: float
    choppiness: float
    kaufman_er: float
    vi_kierunek: str        # "BULLISH" / "BEARISH" / "NEUTRALNY"
    fulmen_rezim: str       # Reżim wg FULMEN
    modyfikator: float      # 1.2 zgodny, 1.0 neutralny, 0.7 konflikt
    powod: str = ""

    @property
    def pozytywny(self) -> bool:
        return self.werdykt in (WerdyktFulmen.ZGODNY, WerdyktFulmen.NEUTRALNY)


_REZIM_MAPA = {
    "TREND_STRONG": "trend",
    "TREND_WEAK": "trend",
    "RANGING": "ranging",
    "VOLATILE": "volatile",
    "UNKNOWN": "unknown",
}


class Fulmen:
    """
    ⚡ Doradca II — FULMEN (Regime Validator)
    Używa zestawu wskaźników ORTOGONALNEGO wobec Legatusa.
    Wymaga DaneFulmen z żywymi danymi z Bramki.
    """

    ADX_TREND_PROG = 25.0
    ADX_RANGING_PROG = 20.0
    CHOPPINESS_TREND = 38.2
    CHOPPINESS_CHOP = 61.8
    ER_EFEKTYWNY = 0.6

    def ocen(self, dane: DaneFulmen) -> OcenaFulmen:
        # Określ reżim wg FULMEN
        jest_trend = (
            dane.adx_14 > self.ADX_TREND_PROG
            and dane.choppiness_14 < self.CHOPPINESS_TREND
            and dane.kaufman_er > self.ER_EFEKTYWNY
        )
        jest_ranging = (
            dane.adx_14 < self.ADX_RANGING_PROG
            or dane.choppiness_14 > self.CHOPPINESS_CHOP
        )

        if jest_trend:
            fulmen_rezim = "trend"
        elif jest_ranging:
            fulmen_rezim = "ranging"
        else:
            fulmen_rezim = "volatile"

        # Kierunek wg Vortex
        if dane.vi_plus_14 > dane.vi_minus_14 + 0.05:
            vi_kierunek = "BULLISH"
        elif dane.vi_minus_14 > dane.vi_plus_14 + 0.05:
            vi_kierunek = "BEARISH"
        else:
            vi_kierunek = "NEUTRALNY"

        # Porównaj z Legatusem
        legatus_typ = _REZIM_MAPA.get(dane.legatus_rezim, "unknown")

        if legatus_typ == "unknown" or fulmen_rezim == "volatile":
            werdykt = WerdyktFulmen.NEUTRALNY
            modyfikator = 1.0
            powod = f"FULMEN: {fulmen_rezim} — nie można potwierdzić jednoznacznie"
        elif legatus_typ == fulmen_rezim:
            werdykt = WerdyktFulmen.ZGODNY
            modyfikator = 1.2
            powod = f"Reżim zgodny: LEGATUS={dane.legatus_rezim}, FULMEN={fulmen_rezim} [ADX={dane.adx_14:.1f}, Chop={dane.choppiness_14:.1f}]"
        else:
            werdykt = WerdyktFulmen.KONFLIKT
            modyfikator = 0.7
            powod = f"KONFLIKT reżimu: LEGATUS={dane.legatus_rezim} vs FULMEN={fulmen_rezim} — ostrożność"

        return OcenaFulmen(
            werdykt=werdykt,
            adx=round(dane.adx_14, 2),
            choppiness=round(dane.choppiness_14, 2),
            kaufman_er=round(dane.kaufman_er, 3),
            vi_kierunek=vi_kierunek,
            fulmen_rezim=fulmen_rezim,
            modyfikator=modyfikator,
            powod=powod,
        )
