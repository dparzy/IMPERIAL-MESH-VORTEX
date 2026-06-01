"""
🏛️ IMV-ORI | HERMES — Information Auditor
Weryfikuje jakość i świeżość informacji przed decyzją Cesarza.
Completeness, freshness, hash integrity, VPIN, high-impact events.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class WerdyktHermes(str, Enum):
    CZYSTE = "CZYSTE"            # Dane kompletne, świeże, hash OK
    ZANIECZYSZCZONE = "ZANIECZYSZCZONE"  # Ostrzeżenie — dane wątpliwe
    NIEKOMPLETNE = "NIEKOMPLETNE"        # Blokada — brak kluczowych danych


@dataclass
class DaneHermes:
    kompletnosc_danych: float    # 0.0–1.0: jaki % wymaganych pól ma wartości
    interwal_minut: int          # Interwał w minutach (np. 60 dla 1H)
    wiek_danych_minut: int       # Ile minut temu były ostatnie dane
    hash_ok: bool                # SHA-256 zgadza się z zapisem w PamięciAbsolutnej
    vpin: float                  # VPIN-01: > 0.75 = toksyczny order flow
    minuty_do_eventu: Optional[int] = None  # Ile minut do HIGH_IMPACT macro event


KOMPLETNOSC_MIN = 0.80
SWIEZE_MNOZNIK = 2       # dane nie starsze niż 2×interwał
VPIN_PROG = 0.75
EVENT_BUFOR_MINUT = 30


@dataclass
class OcenaHermes:
    werdykt: WerdyktHermes
    kompletnosc: float
    vpin: float
    hash_ok: bool
    ostrzezenia: List[str] = field(default_factory=list)
    powod: str = ""

    @property
    def pozytywny(self) -> bool:
        return self.werdykt in (WerdyktHermes.CZYSTE, WerdyktHermes.ZANIECZYSZCZONE)


class Hermes:
    """
    🌐 Doradca IV — HERMES (Information Auditor)
    Sprawdza jakość informacji ZANIM Cesarz podejmie decyzję.
    NIEKOMPLETNE → blokada (jak IUSTITIA BLOKADA = veto Rady).
    """

    def ocen(self, dane: DaneHermes) -> OcenaHermes:
        blokady: List[str] = []
        ostrzezenia: List[str] = []

        # 1. Kompletność danych
        if dane.kompletnosc_danych < KOMPLETNOSC_MIN:
            blokady.append(
                f"Dane niekompletne: {dane.kompletnosc_danych:.0%} < {KOMPLETNOSC_MIN:.0%}"
            )

        # 2. Świeżość danych
        limit_wiek = dane.interwal_minut * SWIEZE_MNOZNIK
        if dane.wiek_danych_minut > limit_wiek:
            blokady.append(
                f"Dane zbyt stare: {dane.wiek_danych_minut}min > {limit_wiek}min (2×{dane.interwal_minut})"
            )

        # 3. Hash integrity
        if not dane.hash_ok:
            blokady.append("Hash SHA-256 niezgodny — dane mogły zostać zmodyfikowane")

        # 4. High-impact macro event
        if dane.minuty_do_eventu is not None and dane.minuty_do_eventu <= EVENT_BUFOR_MINUT:
            blokady.append(
                f"HIGH_IMPACT event za {dane.minuty_do_eventu}min — hold do zakończenia"
            )

        # 5. VPIN (toksyczny order flow)
        if dane.vpin > VPIN_PROG:
            ostrzezenia.append(
                f"VPIN={dane.vpin:.2f} > {VPIN_PROG} — toksyczny order flow, spread poszerzy się"
            )

        if blokady:
            return OcenaHermes(
                werdykt=WerdyktHermes.NIEKOMPLETNE,
                kompletnosc=dane.kompletnosc_danych,
                vpin=dane.vpin,
                hash_ok=dane.hash_ok,
                ostrzezenia=blokady,
                powod=" | ".join(blokady),
            )

        if ostrzezenia:
            return OcenaHermes(
                werdykt=WerdyktHermes.ZANIECZYSZCZONE,
                kompletnosc=dane.kompletnosc_danych,
                vpin=dane.vpin,
                hash_ok=dane.hash_ok,
                ostrzezenia=ostrzezenia,
                powod=" | ".join(ostrzezenia),
            )

        return OcenaHermes(
            werdykt=WerdyktHermes.CZYSTE,
            kompletnosc=dane.kompletnosc_danych,
            vpin=dane.vpin,
            hash_ok=dane.hash_ok,
            powod=f"Hash✓, dane={dane.kompletnosc_danych:.0%}, VPIN={dane.vpin:.2f} — czyste",
        )
