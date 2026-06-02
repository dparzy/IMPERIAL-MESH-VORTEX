"""
🏛️ NAMIESTNIK — Regime-Aware Gating Network (Meta-Controller).

Architektura inspirowana:
  • Volatility-Adaptive MoE (arXiv:2508.02686, 2025) — reżim przełącza eksperta
  • Adaptive Regime-Aware Prediction (arXiv:2603.19136) — autoencoder + RL dla reżimu
  • Meta-Learning Optimal Mixture (arXiv:2505.03659) — MAML dynamiczna selekcja
  • MRC/Shapley (arXiv:2605.24490) — wagi dynamiczne z atrybutem Shapleya (Faza 2)

Rola w łańcuchu decyzyjnym:
    bary
      │
      ▼
    klasyfikuj_rezim() → rezim
      │
      ▼
  [NAMIESTNIK]  ◄──── Punkt adaptacji: reżim → {tryb, wagi, lewar, próg, pas}
      │
      ▼
    Legatus + Klucznik → Kalkulator → pozycja

FAZA 1 (bieżąca): Deterministyczna tablica reżim→parametry.
FAZA 2 (Shapley): Online learning wag z arXiv:2605.24490 (MRC).
FAZA 3 (MAML):    Meta-learning selekcji strategii z arXiv:2505.03659.

Prawo I: Namiestnik NIE liczy wskaźników. Dostaje gotowy reżim od klasyfikatora.
Prawo XV: Gdy rezim=PANIC lub czy_grac=False → cisza (świadoma, nie błąd).
Prawo XVI: Parametry taablicy mają tabele dowodową w docs/MANIFEST_KODU.md.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import logging

logger = logging.getLogger("Namiestnik")


@dataclass
class UstawieniaRezimu:
    """
    Kompletny zestaw parametrów dla jednego reżimu rynku.

    tryb:           jak Dyrygent używa Klucznika ('agregat' / 'filtr' / 'strategia')
    lewar_factor:   mnożnik dźwigni względem auto_dzwignia (0.3 = defensywnie)
    prog_pewnosci:  minimalny próg pewności agregatu do wejścia w pozycję
    czy_grac:       False = stój z boku (RANGING, PANIC) — świadoma cisza
    wagi_override:  opcjonalne nadpisanie kategorycznych wag w WAGI_REZIMU
    opis:           czytelny powód dla DecyzjaCyklu.powod
    """
    tryb: str
    lewar_factor: float
    prog_pewnosci: float
    czy_grac: bool
    wagi_override: Optional[Dict[str, float]] = None
    opis: str = ""

    def __post_init__(self):
        assert self.tryb in ("agregat", "filtr", "strategia"), \
            f"Nieznany tryb Namiestnika: {self.tryb}"
        assert 0.0 < self.lewar_factor <= 2.0, \
            f"lewar_factor poza zakresem: {self.lewar_factor}"
        assert 0.5 <= self.prog_pewnosci <= 1.0, \
            f"prog_pewnosci poza zakresem: {self.prog_pewnosci}"


# ─── Tablica reżimów (Faza 1 — deterministyczna) ─────────────────────────────
#
# Dowody empiryczne (Prawo XVI — Prawo XVI: 12 backtestów 2026-06-02):
#   TREND_STRONG  → filtr +43% ETH 1D (tryb filtr potwierdził przewagę nad agregatem)
#   RANGING       → agregat daje za dużo sygnałów, prog 0.72 redukuje szum
#   VOLATILE      → strategia przełącza na Klucznik (breakout/volatility strategies)
#   PANIC         → stop (2026-06-02: zawsze trap wejście w PANIC)
#   NORMAL        → agregat + lewar 0.8 (ostrożnie, brak pewności reżimu)
#
# lewar_factor mnoży wynik auto_dzwignia(pewnosc, rezim) z KalkulatorLewara.
# prog_pewnosci zastępuje Dyrygent.min_pewnosc dla tego reżimu.
_TABLICA: Dict[str, UstawieniaRezimu] = {
    "TREND_STRONG": UstawieniaRezimu(
        tryb="filtr",
        lewar_factor=1.2,
        prog_pewnosci=0.55,
        czy_grac=True,
        wagi_override={"T": 1.5, "M": 1.2, "S": 1.3, "O": 0.7},
        opis="Silny trend — filtr strategii, pełna dźwignia",
    ),
    "TREND_WEAK": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.7,
        prog_pewnosci=0.60,
        czy_grac=True,
        opis="Słaby trend — agregat, obniżona dźwignia",
    ),
    "RANGING": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.4,
        prog_pewnosci=0.72,
        czy_grac=False,
        wagi_override={"M": 1.5, "F": 1.2, "T": 0.4},
        opis="Rynek w konsolidacji — stój z boku (zbyt wiele fałszywych sygnałów)",
    ),
    "VOLATILE": UstawieniaRezimu(
        tryb="strategia",
        lewar_factor=0.5,
        prog_pewnosci=0.65,
        czy_grac=True,
        wagi_override={"A": 2.0, "V": 1.5, "L": 0.3},
        opis="Wysoka zmienność — Klucznik wybiera strategię, ostrożna dźwignia",
    ),
    "PANIC": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.1,
        prog_pewnosci=0.90,
        czy_grac=False,
        opis="Reżim PANIC — pełna cisza (kapitał chroniony)",
    ),
    "NORMAL": UstawieniaRezimu(
        tryb="agregat",
        lewar_factor=0.8,
        prog_pewnosci=0.60,
        czy_grac=True,
        opis="Normalny rynek — ostrożny agregat",
    ),
    "ON-CHAIN_BULLISH": UstawieniaRezimu(
        tryb="filtr",
        lewar_factor=1.1,
        prog_pewnosci=0.58,
        czy_grac=True,
        wagi_override={"O": 2.0, "L": 0.8},
        opis="Sygnały on-chain bycze — filtr, wzmocnione wagi O",
    ),
    "SMC_ACTIVE": UstawieniaRezimu(
        tryb="strategia",
        lewar_factor=0.9,
        prog_pewnosci=0.62,
        czy_grac=True,
        wagi_override={"S": 2.0, "F": 1.2, "T": 1.1},
        opis="Aktywna struktura SMC — Klucznik + wagi S",
    ),
}

# Fallback gdy reżim nieznany
_FALLBACK = UstawieniaRezimu(
    tryb="agregat",
    lewar_factor=0.5,
    prog_pewnosci=0.65,
    czy_grac=True,
    opis="Nieznany reżim — ultraostrożny fallback",
)


class Namiestnik:
    """
    Gating Network: reżim → kompletny zestaw parametrów dla jednego cyklu.

    Użycie w Dyrygencie:
        namiestnik = Namiestnik()
        ustaw = namiestnik.decyduj(raport.rezim)
        if not ustaw.czy_grac:
            return DecyzjaCyklu(symbol, "NAMIESTNIK_CISZA", False, powod=ustaw.opis)
        # ... dalej z ustaw.tryb, ustaw.prog_pewnosci, ustaw.lewar_factor
    """

    def __init__(self, tablica: Optional[Dict[str, UstawieniaRezimu]] = None) -> None:
        self._tablica = tablica if tablica is not None else _TABLICA

    def decyduj(self, rezim: str) -> UstawieniaRezimu:
        """Zwraca UstawieniaRezimu dla podanego reżimu. Nigdy nie rzuca wyjątku."""
        ustaw = self._tablica.get(rezim)
        if ustaw is None:
            logger.warning(f"[Namiestnik] Nieznany reżim '{rezim}' → fallback ostrożny")
            return _FALLBACK
        return ustaw

    def skaluj_dzwignie(self, dzwignia_base: int, rezim: str) -> int:
        """
        Aplikuje lewar_factor do obliczonej przez KalkulatorLewara dźwigni.
        Wynik: int w przedziale [1, 20].
        """
        ustaw = self.decyduj(rezim)
        scaled = int(round(dzwignia_base * ustaw.lewar_factor))
        return max(1, min(scaled, 20))

    def tablica_rezimu(self) -> Dict[str, UstawieniaRezimu]:
        """Pełna tablica do inspekcji / diagnostyki."""
        return dict(self._tablica)

    def raport(self) -> str:
        """Czytelny raport tablicy dla logów / dashboardu."""
        linie = ["🏛️ NAMIESTNIK — Tablica reżimów (Faza 1):"]
        for rezim, u in self._tablica.items():
            gra = "✅ GRAJ" if u.czy_grac else "🛑 CISZA"
            linie.append(
                f"  {rezim:<20} │ {gra} │ tryb={u.tryb:<10} │ "
                f"lewar×{u.lewar_factor:.1f} │ próg={u.prog_pewnosci:.0%}"
            )
        return "\n".join(linie)


# ─── Singleton dla użycia w Dyrygencie ───────────────────────────────────────
_instancja: Optional[Namiestnik] = None


def get_namiestnik() -> Namiestnik:
    """Zwraca globalny singleton Namiestnika (bez wielokrotnej inicjalizacji)."""
    global _instancja
    if _instancja is None:
        _instancja = Namiestnik()
    return _instancja
