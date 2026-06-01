"""
🏛️ IMV-ORI | ZwiadowcaElitarny — bazowa klasa Dywizji Exploratores

KLUCZOWE RÓŻNICE od MikroNeuronu:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  MikroNeuron:         analizuj(wskazniki: dict)  → czyta z Bramy
  ZwiadowcaElitarny:   analizuj(bary: List[dict]) → liczy SAM z surowych danych

Prawo I dla Exploratores (inne niż dla legionów):
  "Zwiadowca sam wybiera narzędzie — liczy to, czego Brama nie umie."
  Przykłady: Higuchi FD, Kalman Filter, własne ML scoring, multi-bar patterns.

Wymagania implementacji:
  - KLUCZ:        "EXP-XX" (prefiks EXP, nie X/XII/VI)
  - WYMAGA_BAROW: int — ile barów historycznych potrzeba (min. 20)
  - OPIS_METODY:  str — co oblicza i dlaczego tego nie ma w Bramie
  - analizuj():   przyjmuje List[dict] z kluczami: open/high/low/close/volume/timestamp
                  zwraca RaportZwiadowcy

RaportZwiadowcy zawiera:
  - SygnalNeuronu (kompatybilny z Legatusem — LEGION="EXPLORATORES")
  - diagnostics: dict z własnymi obliczonymi wartościami (do logów + debug)
  - pewnosc_metody: float — ile barów miało dane (jakość wejścia 0.0-1.0)
"""

import time
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional

from imperium.legiony.mikro_neuron import SygnalNeuronu

logger = logging.getLogger("Exploratores")


class TypDanych(str, Enum):
    """Jakiego typu dane przetwarza zwiadowca."""
    OHLCV = "OHLCV"              # Surowe świece
    TICK = "TICK"                # Dane tickowe
    ORDER_BOOK = "ORDER_BOOK"    # Głębokość rynku
    ON_CHAIN = "ON_CHAIN"        # Blockchain data
    MULTI_TF = "MULTI_TF"        # Wiele interwałów naraz
    CUSTOM = "CUSTOM"            # Własny format


@dataclass
class RaportZwiadowcy:
    """
    Pełny raport z analizy ZwiadowcyElitarnego.
    Kompatybilny z Legatusem przez pole `sygnal`.
    """
    sygnal: SygnalNeuronu                         # Standardowy sygnał → Legatus
    diagnostics: Dict[str, Any] = field(default_factory=dict)  # Własne wartości
    pewnosc_metody: float = 1.0                   # Jakość danych wejściowych (0-1)
    n_barow_uzytych: int = 0                      # Ile barów faktycznie przetworzono
    czas_obliczen_ms: float = 0.0                 # Czas obliczeń (monitoring perf.)
    ostrzezenia: List[str] = field(default_factory=list)

    @property
    def kierunek(self) -> str:
        return self.sygnal.kierunek

    @property
    def pewnosc(self) -> float:
        return self.sygnal.pewnosc_finalna

    def __str__(self) -> str:
        return (f"[{self.sygnal.neuron_id}] {self.kierunek} "
                f"p={self.pewnosc:.2f} | metoda={self.pewnosc_metody:.0%} | "
                f"diagnostics={self.diagnostics}")


class ZwiadowcaElitarny(ABC):
    """
    Bazowa klasa Dywizji Exploratores.

    NOWE UPRAWNIENIA względem MikroNeuronu:
      ✅ Może liczyć wskaźniki sam (Prawo I nie obowiązuje)
      ✅ Przyjmuje surowe bary OHLCV (nie dict z Bramy)
      ✅ Ma dostęp do historii (wiele barów, nie tylko aktualny)
      ✅ Może używać numpy/pandas wewnętrznie
      ✅ Własna skala Igrzysk (AQUILIFER_PROG = 0.88, waga_max = ×2.5)

    ZACHOWANE ZASADY:
      ✅ API KEY NEVER IN CODE — jeśli wymaga zewnętrznego API → przez env var
      ✅ Sygnał wyjściowy = SygnalNeuronu (kompatybilny z Legatusem)
      ✅ Obsługa pustych/niepełnych danych bez crashu
      ✅ LEGION = "EXPLORATORES" (Legatus może traktować inaczej)
    """

    # Pola wymagane w każdej podklasie
    KLUCZ: str = "EXP-00"
    WSKAZNIK: str = "abstract"
    KATEGORIA: str = "?"
    WAGA: int = 7                 # Exploratores domyślnie wyższa waga (7-10)
    WYMAGA_BAROW: int = 20        # Minimalna historia
    OPIS_METODY: str = ""         # Co liczy i dlaczego nie ma w Bramie
    TYP_DANYCH: TypDanych = TypDanych.OHLCV

    # Stałe klasy — nie nadpisywać
    LEGION: str = "EXPLORATORES"

    # Dostępność (Prawo XV — jawność potencjału). Gdy zwiadowca wymaga danych
    # których pipeline jeszcze nie dostarcza (np. feed L2 orderbook), oznacz go
    # DOSTEPNY=False z czytelnym powodem — Legatus go pominie zamiast karmić
    # martwym NEUTRAL. To NIE jest utrata potencjału, lecz świadome wyciszenie.
    DOSTEPNY: bool = True
    POWOD_NIEDOSTEPNOSCI: str = ""

    def __init__(self) -> None:
        if self.KLUCZ == "EXP-00":
            raise NotImplementedError(f"{type(self).__name__} musi ustawić KLUCZ (EXP-XX).")
        if not self.KLUCZ.startswith("EXP-"):
            raise ValueError(f"Klucz Exploratores musi zaczynać się od 'EXP-', got: {self.KLUCZ}")

    @abstractmethod
    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        """
        Główna metoda analizy.

        bary: lista dict, każdy zawiera:
          {"open": float, "high": float, "low": float,
           "close": float, "volume": float, "timestamp": int}
          Posortowane rosnąco — bary[-1] to NAJNOWSZY.

        Zwraca RaportZwiadowcy z sygnałem kompatybilnym z Legatusem.
        MUSI obsłużyć len(bary) < WYMAGA_BAROW bez crashu.
        """
        ...

    def _waliduj_bary(self, bary: List[Dict[str, Any]]) -> tuple[bool, str]:
        """Sprawdza czy bary są wystarczające. Zwraca (ok, komunikat)."""
        if not bary:
            return False, "Brak barów"
        if len(bary) < self.WYMAGA_BAROW:
            return False, f"Za mało barów: {len(bary)}/{self.WYMAGA_BAROW}"
        wymagane = ("close",)
        for pole in wymagane:
            if pole not in bary[0]:
                return False, f"Brak wymaganego pola '{pole}' w barach"
        return True, "OK"

    def _brak_danych(self, powod: str) -> RaportZwiadowcy:
        """Pomocnik — zwraca NEUTRAL gdy za mało danych (nie crashuje)."""
        sygnal = SygnalNeuronu(
            neuron_id=self.KLUCZ, legion=self.LEGION,
            wskaznik=self.WSKAZNIK, wartosc=None,
            kierunek="NEUTRAL", pewnosc=0.0,
            powody=[f"[{self.KLUCZ}] Brak danych: {powod}"],
            waga=self.WAGA, kategoria=self.KATEGORIA,
        )
        sygnal.policz_finalna()
        return RaportZwiadowcy(
            sygnal=sygnal, pewnosc_metody=0.0, n_barow_uzytych=0,
            ostrzezenia=[powod],
        )

    def _buduj_raport(
        self,
        kierunek: str,
        pewnosc: float,
        powody: List[str],
        diagnostics: Dict[str, Any],
        n_barow: int,
        pewnosc_metody: float = 1.0,
        ostrzezenia: Optional[List[str]] = None,
        czas_ms: float = 0.0,
    ) -> RaportZwiadowcy:
        """Pomocnik — buduje RaportZwiadowcy ze standardowymi metadanymi."""
        sygnal = SygnalNeuronu(
            neuron_id=self.KLUCZ, legion=self.LEGION,
            wskaznik=self.WSKAZNIK, wartosc=diagnostics.get("main_value"),
            kierunek=kierunek, pewnosc=pewnosc,
            powody=powody, waga=self.WAGA, kategoria=self.KATEGORIA,
        )
        sygnal.policz_finalna()
        return RaportZwiadowcy(
            sygnal=sygnal,
            diagnostics=diagnostics,
            pewnosc_metody=pewnosc_metody,
            n_barow_uzytych=n_barow,
            czas_obliczen_ms=czas_ms,
            ostrzezenia=ostrzezenia or [],
        )

    def _pobierz_close(self, bary: List[Dict]) -> List[float]:
        return [float(b.get("close", 0)) for b in bary]

    def _pobierz_high(self, bary: List[Dict]) -> List[float]:
        return [float(b.get("high", 0)) for b in bary]

    def _pobierz_low(self, bary: List[Dict]) -> List[float]:
        return [float(b.get("low", 0)) for b in bary]

    def _pobierz_volume(self, bary: List[Dict]) -> List[float]:
        return [float(b.get("volume", 0)) for b in bary]
