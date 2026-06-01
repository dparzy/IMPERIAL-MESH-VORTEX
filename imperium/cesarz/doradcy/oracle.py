"""
🏛️ IMV-ORI | ORACLE — Sharpe Auditor
Ocenia jakość ryzyko-zwrot na podstawie historii podobnych setupów.
Q_score = 0.3×Sharpe + 0.25×Sortino + 0.25×Calmar + 0.2×Omega
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class WerdyktOracle(str, Enum):
    GODNE = "GODNE"          # Q > 1.2 — wejście potwierdzone
    WATPLIWE = "WĄTPLIWE"    # Q 0.8–1.2 — zmniejsz pozycję o 50%
    NIEGODNE = "NIEGODNE"    # Q < 0.8 — blokada wejścia
    BRAK_DANYCH = "BRAK_DANYCH"


@dataclass
class OcenaOracle:
    werdykt: WerdyktOracle
    q_score: float
    sharpe: float
    sortino: float
    calmar: float
    omega: float
    n_setupow: int
    powod: str = ""

    @property
    def pozytywny(self) -> bool:
        return self.werdykt in (WerdyktOracle.GODNE, WerdyktOracle.WATPLIWE)

    @property
    def modyfikator_pozycji(self) -> float:
        """Mnożnik rozmiaru pozycji na podstawie werdyktu."""
        if self.werdykt == WerdyktOracle.GODNE:
            return 1.0
        if self.werdykt == WerdyktOracle.WATPLIWE:
            return 0.5
        return 0.0


def _sharpe(returny: List[float], rf: float = 0.0) -> float:
    if len(returny) < 2:
        return 0.0
    n = len(returny)
    mean = sum(returny) / n
    variance = sum((r - mean) ** 2 for r in returny) / (n - 1)
    std = math.sqrt(variance) if variance > 0 else 0.0
    return (mean - rf) / std if std > 0 else 0.0


def _sortino(returny: List[float], rf: float = 0.0) -> float:
    if len(returny) < 2:
        return 0.0
    mean = sum(returny) / len(returny)
    downside = [r for r in returny if r < rf]
    if not downside:
        return 3.0  # brak strat = doskonały
    downside_var = sum((r - rf) ** 2 for r in downside) / len(downside)
    downside_std = math.sqrt(downside_var)
    return (mean - rf) / downside_std if downside_std > 0 else 0.0


def _calmar(returny: List[float]) -> float:
    if not returny:
        return 0.0
    total_return = sum(returny)
    # MaxDD jako procent sumaryczny
    cumulative, peak, max_dd = 0.0, 0.0, 0.0
    for r in returny:
        cumulative += r
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd
    return total_return / max_dd if max_dd > 0 else total_return


def _omega(returny: List[float], prog: float = 0.0) -> float:
    """Omega ratio: suma zysków powyżej progu / suma strat poniżej progu."""
    gains = sum(r - prog for r in returny if r > prog)
    losses = sum(prog - r for r in returny if r <= prog)
    return gains / losses if losses > 0 else gains if gains > 0 else 1.0


class Oracle:
    """
    🔮 Doradca I — ORACLE (Sharpe Auditor)
    Wymaga listy pnl_pct z podobnych historycznych setupów.
    MIN_SETUPOW = 5 (poniżej → BRAK_DANYCH)
    """

    MIN_SETUPOW = 5

    def ocen(self, pnl_historia: List[float]) -> OcenaOracle:
        """
        pnl_historia: lista pnl_pct (procenty, np. [2.1, -0.8, 3.5, ...])
        Pobierana z PamiecAbsolutna — ostatnie 90 dni podobnych setupów.
        """
        if len(pnl_historia) < self.MIN_SETUPOW:
            return OcenaOracle(
                werdykt=WerdyktOracle.BRAK_DANYCH,
                q_score=0.0, sharpe=0.0, sortino=0.0, calmar=0.0, omega=0.0,
                n_setupow=len(pnl_historia),
                powod=f"Za mało historii: {len(pnl_historia)}/{self.MIN_SETUPOW} setupów",
            )

        sharpe = _sharpe(pnl_historia)
        sortino = _sortino(pnl_historia)
        calmar = _calmar(pnl_historia)
        omega = _omega(pnl_historia)

        # Normalizacja — cap values aby nie zawyżały score
        s_norm = max(-2.0, min(3.0, sharpe))
        so_norm = max(-2.0, min(3.0, sortino))
        c_norm = max(-2.0, min(3.0, calmar))
        o_norm = max(0.0, min(3.0, omega))

        q = round(0.30 * s_norm + 0.25 * so_norm + 0.25 * c_norm + 0.20 * o_norm, 3)

        if q > 1.2:
            werdykt = WerdyktOracle.GODNE
            powod = f"Q={q:.3f} > 1.2 — doskonały profil ryzyko-zwrot"
        elif q >= 0.8:
            werdykt = WerdyktOracle.WATPLIWE
            powod = f"Q={q:.3f} w szarej strefie — zmniejsz pozycję o 50%"
        else:
            werdykt = WerdyktOracle.NIEGODNE
            powod = f"Q={q:.3f} < 0.8 — słaby profil historyczny"

        return OcenaOracle(
            werdykt=werdykt, q_score=q,
            sharpe=round(sharpe, 3), sortino=round(sortino, 3),
            calmar=round(calmar, 3), omega=round(omega, 3),
            n_setupow=len(pnl_historia), powod=powod,
        )
