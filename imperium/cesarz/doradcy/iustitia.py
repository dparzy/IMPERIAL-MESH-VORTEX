"""
🏛️ IMV-ORI | IUSTITIA — Risk Auditor
Niezależna ocena ryzyka portfela. IUSTITIA BLOKUJE = automatyczne veto.
Portfolio heat, korelacja, drawdown rate, Kelly fraction.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class WerdyktIustitia(str, Enum):
    OK = "OK"                    # Ryzyko akceptowalne
    OSTRZEZENIE = "OSTRZEŻENIE"  # Ryzyko wysokie — zmniejsz pozycję
    BLOKADA = "BLOKADA"          # Veto bezwarunkowe


@dataclass
class OtwartaPozycja:
    symbol: str
    ryzyko_usdt: float       # Kwota ryzyka w USDT (stop-loss odległość × rozmiar)
    pnl_pct: float           # Bieżące PnL%


@dataclass
class DaneIustitia:
    kapital_total: float
    nowe_ryzyko_usdt: float              # Ryzyko proponowanej pozycji
    otwarte_pozycje: List[OtwartaPozycja] = field(default_factory=list)
    ostatnie_5_pnl: List[float] = field(default_factory=list)  # pnl_pct ostatnich 5 trade'ów
    korelacja_z_otwartymi: float = 0.0  # max korelacja nowego z otwartymi
    win_rate: float = 0.5
    avg_win_pct: float = 1.0
    avg_loss_pct: float = 1.0


@dataclass
class OcenaIustitia:
    werdykt: WerdyktIustitia
    portfolio_heat: float
    kelly_fraction: float
    sugerowany_rozmiar_pct: float  # % kapitału (0.0 = blokuj)
    ostrzezenia: List[str] = field(default_factory=list)
    powod: str = ""

    @property
    def pozytywny(self) -> bool:
        return self.werdykt != WerdyktIustitia.BLOKADA


HEAT_MAX = 0.06        # 6% kapitału → blokada nowych
HEAT_CRITICAL = 0.10  # 10% → wymagane zamknięcie najsłabszej
CORR_MAX = 0.75        # Korelacja > 75% = de facto podwójny zakład
COOLING_PERIOD_LOSSES = 5  # 5 z rzędu strat = 24h cooling


class Iustitia:
    """
    ⚖️ Doradca III — IUSTITIA (Risk Auditor)
    IUSTITIA BLOKADA = automatyczne veto dla całej Rady Doradców.
    """

    def ocen(self, dane: DaneIustitia) -> OcenaIustitia:
        ostrzezenia: List[str] = []
        blokada_powody: List[str] = []

        # 1. Portfolio heat
        heat_biezacy = sum(p.ryzyko_usdt for p in dane.otwarte_pozycje)
        heat_po_wejsciu = (heat_biezacy + dane.nowe_ryzyko_usdt) / dane.kapital_total

        if heat_po_wejsciu > HEAT_CRITICAL:
            blokada_powody.append(
                f"Portfolio heat krytyczny: {heat_po_wejsciu:.1%} > {HEAT_CRITICAL:.0%}"
            )
        elif heat_po_wejsciu > HEAT_MAX:
            blokada_powody.append(
                f"Portfolio heat przekroczony: {heat_po_wejsciu:.1%} > {HEAT_MAX:.0%}"
            )

        # 2. Korelacja z otwartymi pozycjami
        if dane.korelacja_z_otwartymi > CORR_MAX:
            blokada_powody.append(
                f"Korelacja {dane.korelacja_z_otwartymi:.2f} > {CORR_MAX} — de facto podwójny zakład"
            )

        # 3. Seria strat — cooling period
        if len(dane.ostatnie_5_pnl) >= COOLING_PERIOD_LOSSES:
            all_loss = all(p < 0 for p in dane.ostatnie_5_pnl[-COOLING_PERIOD_LOSSES:])
            if all_loss:
                blokada_powody.append(
                    f"Seria {COOLING_PERIOD_LOSSES} strat z rzędu — 24h cooling period"
                )

        # 4. Kelly fraction
        kelly = self._kelly(dane.win_rate, dane.avg_win_pct, dane.avg_loss_pct)
        half_kelly = kelly * 0.5
        proponowany_pct = dane.nowe_ryzyko_usdt / dane.kapital_total
        if proponowany_pct > half_kelly and half_kelly > 0:
            ostrzezenia.append(
                f"Pozycja {proponowany_pct:.1%} > Half Kelly {half_kelly:.1%} — zmniejsz"
            )

        # Werdykt
        if blokada_powody:
            return OcenaIustitia(
                werdykt=WerdyktIustitia.BLOKADA,
                portfolio_heat=round(heat_po_wejsciu, 4),
                kelly_fraction=round(half_kelly, 4),
                sugerowany_rozmiar_pct=0.0,
                ostrzezenia=blokada_powody,
                powod=" | ".join(blokada_powody),
            )

        if ostrzezenia:
            return OcenaIustitia(
                werdykt=WerdyktIustitia.OSTRZEZENIE,
                portfolio_heat=round(heat_po_wejsciu, 4),
                kelly_fraction=round(half_kelly, 4),
                sugerowany_rozmiar_pct=round(half_kelly, 4),
                ostrzezenia=ostrzezenia,
                powod=" | ".join(ostrzezenia),
            )

        return OcenaIustitia(
            werdykt=WerdyktIustitia.OK,
            portfolio_heat=round(heat_po_wejsciu, 4),
            kelly_fraction=round(half_kelly, 4),
            sugerowany_rozmiar_pct=round(min(proponowany_pct, half_kelly), 4),
            powod=f"Heat={heat_po_wejsciu:.1%}, Kelly={half_kelly:.1%} — ryzyko akceptowalne",
        )

    @staticmethod
    def _kelly(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Half Kelly: (p×b - q) / b gdzie b = avg_win/avg_loss."""
        if avg_loss <= 0:
            return 0.0
        b = avg_win / avg_loss
        q = 1.0 - win_rate
        kelly = (win_rate * b - q) / b
        return max(0.0, kelly)
