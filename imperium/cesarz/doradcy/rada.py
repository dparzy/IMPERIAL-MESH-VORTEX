"""
🏛️ IMV-ORI | RadaDoradcow — Orchestrator Rady Pięciu Doradców
Reguły głosowania: 5/5=pełna pozycja, 4/5=ok, 3/5=50%, <3=blokada.
IUSTITIA BLOKADA lub HERMES NIEKOMPLETNE = veto bezwarunkowe.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .oracle import OcenaOracle, WerdyktOracle
from .fulmen import OcenaFulmen, WerdyktFulmen
from .iustitia import OcenaIustitia, WerdyktIustitia
from .hermes import OcenaHermes, WerdyktHermes
from .pythia import OcenaPythia, WerdyktPythia


@dataclass
class OpinaRady:
    oracle: OcenaOracle
    fulmen: OcenaFulmen
    iustitia: OcenaIustitia
    hermes: OcenaHermes
    pythia: OcenaPythia

    pozytywne: int = 0
    modyfikator_pozycji: float = 1.0  # 1.0 / 0.8 / 0.6 / 0.0
    blokada: bool = False
    powod_blokady: str = ""
    decyzja: str = ""

    def raport(self, symbol: str = "", pewnosc_legatus: float = 0.0) -> str:
        linia = "═" * 70
        def fmt(nazwa: str, werdykt: str, szczegol: str) -> str:
            return f"  {nazwa:<10} .......... {werdykt:<20} [{szczegol}]"

        oracle_det = f"Q={self.oracle.q_score:.3f}"
        fulmen_det = f"ADX={self.fulmen.adx:.1f}, Chop={self.fulmen.choppiness:.1f}"
        iust_det = f"Heat={self.iustitia.portfolio_heat:.1%}"
        hermes_det = f"Hash{'✓' if self.hermes.hash_ok else '✗'}, VPIN={self.hermes.vpin:.2f}"
        pythia_det = f"p={self.pythia.p_zysk:.0%}, n={self.pythia.n_podobnych}"

        linie = [
            f"╔{'═'*68}╗",
            f"║{'🔮 RADA DORADCÓW CESARSKICH — OPINIA':^68}║",
            f"║  Symbol: {symbol:<15} Pewność Legatus: {pewnosc_legatus:.0%}{' ':>25}║",
            f"╠{'═'*68}╣",
            f"║{fmt('ORACLE', self.oracle.werdykt.value, oracle_det):<68}║",
            f"║{fmt('FULMEN', self.fulmen.werdykt.value, fulmen_det):<68}║",
            f"║{fmt('IUSTITIA', self.iustitia.werdykt.value, iust_det):<68}║",
            f"║{fmt('HERMES', self.hermes.werdykt.value, hermes_det):<68}║",
            f"║{fmt('PYTHIA', self.pythia.werdykt.value, pythia_det):<68}║",
            f"╠{'═'*68}╣",
            f"║  WYNIK RADY: {self.pozytywne}/5 POZYTYWNYCH  {'→ ' + self.decyzja:<50}║",
        ]
        if self.blokada and self.powod_blokady:
            linie.append(f"║  ⚠️  {self.powod_blokady[:62]:<62}  ║")
        linie.append(f"╚{'═'*68}╝")
        return "\n".join(linie)


class RadaDoradcow:
    """
    Orchestrator Rady Pięciu Doradców.
    Przyjmuje gotowe oceny (każdy doradca wywołany osobno z własnymi danymi).
    """

    def ocen(
        self,
        oracle: OcenaOracle,
        fulmen: OcenaFulmen,
        iustitia: OcenaIustitia,
        hermes: OcenaHermes,
        pythia: OcenaPythia,
    ) -> OpinaRady:
        opinia = OpinaRady(
            oracle=oracle, fulmen=fulmen,
            iustitia=iustitia, hermes=hermes, pythia=pythia,
        )

        # Veto bezwarunkowe — IUSTITIA BLOKADA lub HERMES NIEKOMPLETNE
        if iustitia.werdykt == WerdyktIustitia.BLOKADA:
            opinia.blokada = True
            opinia.powod_blokady = f"IUSTITIA VETO: {iustitia.powod}"
            opinia.modyfikator_pozycji = 0.0
            opinia.pozytywne = 0
            opinia.decyzja = "CESARZ BLOKUJE — IUSTITIA VETO"
            return opinia

        if hermes.werdykt == WerdyktHermes.NIEKOMPLETNE:
            opinia.blokada = True
            opinia.powod_blokady = f"HERMES VETO: {hermes.powod}"
            opinia.modyfikator_pozycji = 0.0
            opinia.pozytywne = 0
            opinia.decyzja = "CESARZ BLOKUJE — HERMES NIEKOMPLETNE"
            return opinia

        # Zlicz pozytywne (PYTHIA MILCZENIE = neutralne, nie blokuje)
        poz = sum([
            oracle.pozytywny,
            fulmen.pozytywny,
            iustitia.pozytywny,
            hermes.pozytywny,
            pythia.pozytywny,
        ])
        opinia.pozytywne = poz

        if poz >= 5:
            opinia.modyfikator_pozycji = 1.0
            opinia.decyzja = "CESARZ MOŻE DZIAŁAĆ — pełna pozycja"
        elif poz == 4:
            opinia.modyfikator_pozycji = 0.8
            opinia.decyzja = "WEJŚCIE OK — standardowa pozycja (×0.8)"
        elif poz == 3:
            opinia.modyfikator_pozycji = 0.6
            opinia.decyzja = "WEJŚCIE OK — zmniejszona pozycja 50% (×0.6)"
        else:
            opinia.blokada = True
            opinia.modyfikator_pozycji = 0.0
            opinia.decyzja = f"CESARZ BLOKUJE — tylko {poz}/5 pozytywnych"

        return opinia
