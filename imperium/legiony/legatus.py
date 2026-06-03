"""
Generał Legatus — koordynator między Legionami a Senatem.

Zbiera sygnały ze wszystkich aktywnych neuronów, filtruje szum,
klasyfikuje reżim rynku i przekazuje zagregowany raport do Senatu.

Dwa tryby:
  SKANER — skanuje listę aktywów, szuka najlepszej okazji
  FOKUS  — wszystkie neurony na jeden cel
"""

import time
import logging
from dataclasses import dataclass, field
from typing import List, Optional
try:
    from .mikro_neuron import SygnalNeuronu, MikroNeuron, Roj
except ImportError:
    from mikro_neuron import SygnalNeuronu, MikroNeuron, Roj

logger = logging.getLogger("Legatus")


@dataclass
class RaportLegatusa:
    symbol: str
    tryb: str                      # SKANER / FOKUS
    rezim: str                     # TREND_STRONG / RANGING / VOLATILE / PANIC / NORMAL
    kierunek: str                  # LONG / SHORT / NEUTRAL
    sila_long: float               # 0.0–1.0
    sila_short: float              # 0.0–1.0
    pewnosc_agregatu: float        # finalna siła dominującego kierunku
    aktywnych_neuronow: int
    zgodnych_neuronow: int
    rezim_zrodlo: str = "manual"   # "auto" gdy klasyfikator wykrył, "manual" gdy podany z zewnątrz
    sygnaly: List[SygnalNeuronu] = field(default_factory=list)
    strategie_dopasowane: list = field(default_factory=list)  # top DopasowanieStrategii
    weto: bool = False
    powod_weta: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class KandydatAktywa:
    symbol: str
    wynik: float
    kierunek: str
    raport: Optional[RaportLegatusa] = None


# ─── Wagi reżimowe dla kategorii neuronów ─────────────────────────────────────

# Wagi reżimowe wg KATEGORII neuronu (legenda: M=Momentum T=Trend V=Zmienność
# F=Flow/Wolumen O=On-chain L=Leverage R=Sentyment S=Struktura A=Anty-manipulacja).
#
# Prawo XXI — spójność kategorii:
#   AKTYWNE kategorie w kodzie (2026-06-02): A F M O R S T
#   PLANOWANE (pre-zarejestrowane na przyszłe neurony):
#     L = Leverage          (brak neuronu — reguła czeka na wdrożenie)
#     V = Zmienność         (EXP-04/EXP-12 mają V, ale są wyciszone — reguła uśpiona)
#   Po wdrożeniu pierwszego neuronu z KAT=L/V → reguła automatycznie ożyje.
#   A = Anty-manipulacja OŻYWIONA 2026-06-02 (A-01 Stop Hunt, A-02 Wick Rejection).
WAGI_REZIMU = {
    "TREND_STRONG":    {"T": 1.5, "M": 1.2, "S": 1.3, "O": 0.7, "L": 0.8, "R": 0.8},
    "RANGING":         {"M": 1.5, "F": 1.2, "T": 0.5, "R": 1.2},
    "VOLATILE":        {"A": 2.0, "V": 1.5, "R": 1.3, "L": 0.3, "_default": 0.7},
    "PANIC":           {"A": 3.0, "R": 1.5, "_default": 0.1},
    "NORMAL":          {"R": 1.1},
    "ON-CHAIN_BULLISH":{"O": 2.0, "L": 0.8, "R": 1.1},
    "SMC_ACTIVE":      {"S": 2.0, "F": 1.2, "T": 1.1},
}

# Kategorie planowane (pre-zarejestrowane) — nie alarmuj na nie w KROK 0
WAGI_REZIMU_PLANOWANE: set = set()  # L i V zaimplementowane (VI-13, V-13)


def klasyfikuj_rezim(wskazniki: dict) -> str:
    """
    Automatyczny klasyfikator reżimu rynku z gotowych wskaźników Bramy.

    Priorytety (od najsilniejszego):
      VOLATILE  → ATR_DEVIATION > 2.5  (rynek bardzo rozchwiany)
      TREND_STRONG → ADX_14 > 25       (wyraźny trend)
      RANGING   → ADX_14 < 20 + wąskie BB (konsolidacja)
      NORMAL    → domyślnie

    Prawo I: TYLKO czyta z wskazniki dict, nie liczy własnej matematyki.
    Prawo XVI: progi zmierzone (nie zgadywane) na standardowych parametrach TA.
    """
    adx = wskazniki.get("ADX_14")
    atr_dev = wskazniki.get("ATR_DEVIATION")
    bb_upper = wskazniki.get("BB_UPPER")
    bb_lower = wskazniki.get("BB_LOWER")
    bb_middle = wskazniki.get("BB_MIDDLE")

    # VOLATILE: ekstremalnie wysoka zmienność
    if atr_dev is not None and atr_dev > 2.5:
        return "VOLATILE"

    # TREND_STRONG: ADX powyżej progu trendu
    if adx is not None and adx > 25:
        return "TREND_STRONG"

    # RANGING: ADX wskazuje brak trendu + wąskie wstęgi Bollingera
    if adx is not None and adx < 20:
        if bb_upper is not None and bb_lower is not None and bb_middle is not None:
            szerokosc = (bb_upper - bb_lower) / (bb_middle + 1e-9)
            if szerokosc < 0.04:  # BB węższe niż 4% mid-price → konsolidacja
                return "RANGING"
        return "RANGING"  # sam ADX < 20 wystarczy

    return "NORMAL"


class Legatus:
    """
    Generał Legatus — agreguje sygnały wszystkich aktywnych neuronów i przekazuje raport Senatowi.

    Użycie:
        legatus = Legatus(neurony=[...], min_neuronow=5, min_przewaga=0.55)
        raport = legatus.fokus("BTCUSDT", wskazniki, rezim="TREND_STRONG")
    """

    def __init__(self, neurony: List[MikroNeuron],
                 min_neuronow: int = 5,
                 min_przewaga: float = 0.55,
                 zwiadowcy: Optional[list] = None,
                 strategie: Optional[list] = None,
                 mnozniki_neuronow: Optional[dict] = None):
        """
        neurony:   lista MikroNeuronów (czytają z dict Bramy).
        zwiadowcy: lista ZwiadowcaElitarny (EXP-XX) — liczą sami z serii barów.
                   Jeśli podani, fokus() odpala ich gdy dostanie `bary`.
                   ZwiadowcaSMC dodatkowo wstrzykuje strefy → budzi SMC-01/02/03.
        strategie: lista Strategia — baza przepisów. Jeśli podana, raport zawiera
                   automatycznie dobrane TOP strategie do bieżących sygnałów (wizja
                   Cezara: sygnały → najbliższa strategia). Brak → pusta lista.
        mnozniki_neuronow: opcjonalny dict {klucz_neuronu: mnoznik} z uczenia wag —
                   źródło: Igrzyska.nowe_wagi() (batch) lub HedgeMWU.mnozniki()
                   (online, wizja W-049). Mnożone NA WIERZCH wag reżimowych.
                   Brak/1.0 → zero zmian (Prawo XV: domyślnie neutralne).
        """
        self.roj = Roj(neurony)
        self.min_neuronow = min_neuronow
        self.min_przewaga = min_przewaga
        self.zwiadowcy = zwiadowcy or []
        self.strategie = strategie or []
        self.mnozniki_neuronow = mnozniki_neuronow or {}

    def ustaw_mnozniki_neuronow(self, mnozniki: dict):
        """
        Aktualizuje mnożniki wag per-neuron (z Igrzysk lub HedgeMWU). Wywoływane
        okresowo (Igrzyska co ~30 dni) lub na bieżąco (MWU online). Prawo XV:
        zamyka pętlę uczenia — policzone wagi faktycznie wpływają na decyzję.
        """
        self.mnozniki_neuronow = mnozniki or {}

    # ── Tryb FOKUS ─────────────────────────────────────────────────────────────

    def fokus(self, symbol: str, wskazniki: dict,
              rezim: str = "NORMAL",
              bary: Optional[list] = None) -> RaportLegatusa:
        """
        Koncentruje wszystkie neurony na jednym symbolu.

        bary: opcjonalna seria OHLCV (List[dict]). Jeśli podana i są zwiadowcy:
              1. ZwiadowcaSMC wstrzykuje strefy do `wskazniki` (budzi neurony SMC)
              2. Każdy zwiadowca EXP liczy własny sygnał z barów
              3. Sygnały EXP dołączają do agregacji obok neuronów
        """
        sygnaly_exp = []
        if bary and self.zwiadowcy:
            sygnaly_exp = self._odpal_zwiadowcow(wskazniki, bary)

        # Auto-klasyfikacja reżimu gdy nie podano wprost (lub podano NORMAL)
        rezim_zrodlo = "manual"
        if rezim == "NORMAL":
            wykryty = klasyfikuj_rezim(wskazniki)
            if wykryty != "NORMAL":
                rezim = wykryty
                rezim_zrodlo = "auto"

        # Interwał z danych — Timeframe-Aware dobór strategii (Prawo XV)
        interwal = bary[-1].get("interwal", "") if bary else ""

        sygnaly = self.roj.zbierz_sygnaly(wskazniki)
        sygnaly = sygnaly + sygnaly_exp
        sygnaly = self._dostosuj_wagi(sygnaly, rezim)
        return self._agreguj(symbol, "FOKUS", rezim, sygnaly, rezim_zrodlo, interwal)

    def _odpal_zwiadowcow(self, wskazniki: dict, bary: list) -> List[SygnalNeuronu]:
        """
        Odpala zwiadowców EXP na serii barów (Prawo XV — potencjał wykorzystany).
        Najpierw ZwiadowcaSMC wstrzykuje strefy (most do SMC), potem reszta liczy sygnały.
        """
        sygnaly = []
        # Zwiadowcy wyciszeni (DOSTEPNY=False) są pomijani — wymagają danych,
        # których pipeline jeszcze nie ma (np. feed L2). Prawo XV: świadome
        # wyciszenie, nie martwy głos.
        aktywni = [z for z in self.zwiadowcy if getattr(z, "DOSTEPNY", True)]
        # Krok 1: zwiadowcy z metodą wstrzyknij() (np. SMC) najpierw wzbogacają dict
        for z in aktywni:
            if hasattr(z, "wstrzyknij"):
                try:
                    z.wstrzyknij(wskazniki, bary)
                except Exception as e:
                    logger.error(f"[Legatus] Zwiadowca {z.KLUCZ} wstrzyknij() padł: {e}")
        # Krok 2: każdy zwiadowca liczy własny raport
        for z in aktywni:
            try:
                raport = z.analizuj(bary)
                sygnaly.append(raport.sygnal)
            except Exception as e:
                logger.error(f"[Legatus] Zwiadowca {z.KLUCZ} analizuj() padł: {e}")
        return sygnaly

    # ── Tryb SKANER ────────────────────────────────────────────────────────────

    def skaner(self, watchlista: List[str],
               pobierz_wskazniki,  # callable(symbol) -> dict
               rezim: str = "NORMAL") -> List[KandydatAktywa]:
        """
        Skanuje listę aktywów. Zwraca top-3 kandydatów.

        pobierz_wskazniki: funkcja (symbol: str) -> dict z wartościami wskaźników
        """
        kandydaci = []
        for symbol in watchlista:
            try:
                wskazniki = pobierz_wskazniki(symbol)
                raport = self.fokus(symbol, wskazniki, rezim)
                kandydaci.append(KandydatAktywa(
                    symbol=symbol,
                    wynik=raport.pewnosc_agregatu,
                    kierunek=raport.kierunek,
                    raport=raport,
                ))
            except Exception as e:
                logger.error(f"[Skaner] Błąd dla {symbol}: {e}")

        kandydaci.sort(key=lambda x: x.wynik, reverse=True)
        return kandydaci[:3]

    # ── Agregacja ──────────────────────────────────────────────────────────────

    def _agreguj(self, symbol: str, tryb: str, rezim: str,
                 sygnaly: List[SygnalNeuronu],
                 rezim_zrodlo: str = "manual",
                 interwal: str = "") -> RaportLegatusa:
        long_s  = [s for s in sygnaly if s.kierunek == "LONG"]
        short_s = [s for s in sygnaly if s.kierunek == "SHORT"]

        sila_l = sum(s.pewnosc_finalna * s.waga for s in long_s)
        sila_s = sum(s.pewnosc_finalna * s.waga for s in short_s)
        razem  = sila_l + sila_s + 1e-9

        prev_l = sila_l / razem
        prev_s = sila_s / razem

        if prev_l >= prev_s:
            kierunek = "LONG"
            pewnosc  = prev_l
            zgodnych = len(long_s)
        else:
            kierunek = "SHORT"
            pewnosc  = prev_s
            zgodnych = len(short_s)

        if pewnosc < 0.5:
            kierunek = "NEUTRAL"

        # Filtr minimum
        weto = False
        powod = ""
        if len(sygnaly) < self.min_neuronow:
            weto = True
            powod = f"Za mało aktywnych neuronów: {len(sygnaly)} < {self.min_neuronow}"
        elif pewnosc < self.min_przewaga and kierunek != "NEUTRAL":
            weto = True
            powod = f"Za słaba przewaga: {pewnosc:.2%} < {self.min_przewaga:.0%}"
        elif rezim == "PANIC":
            weto = True
            powod = "Reżim PANIC — system w trybie obronnym"

        # Wizja Cezara: z bieżących sygnałów dobierz najbliższą strategię z bazy
        # (Timeframe-Aware: filtr po interwale — scalp M5 ≠ swing 1D)
        strategie_dopasowane = self._dobierz_strategie(sygnaly, rezim, interwal)

        return RaportLegatusa(
            symbol=symbol,
            tryb=tryb,
            rezim=rezim,
            kierunek=kierunek if not weto else "NEUTRAL",
            rezim_zrodlo=rezim_zrodlo,
            sila_long=round(prev_l, 4),
            sila_short=round(prev_s, 4),
            pewnosc_agregatu=round(pewnosc, 4),
            aktywnych_neuronow=len(sygnaly),
            zgodnych_neuronow=zgodnych,
            sygnaly=sygnaly,
            strategie_dopasowane=strategie_dopasowane,
            weto=weto,
            powod_weta=powod,
        )

    def _dobierz_strategie(self, sygnaly: List[SygnalNeuronu], rezim: str,
                           interwal: str = "") -> list:
        """
        Most do Dywizji Strategii: mapuje sygnały po kluczu neuronu i pyta silnik
        o TOP pasujące strategie. Brak bazy strategii → pusta lista (bez kosztu).

        interwal: Timeframe-Aware filtr — przepuszcza tylko strategie na ten TF.
        """
        if not self.strategie:
            return []
        try:
            from imperium.legiony.strategie.baza import dobierz_najlepsze
            mapa = {s.neuron_id: s for s in sygnaly}
            return dobierz_najlepsze(self.strategie, mapa, rezim=rezim, top=3,
                                     interwal=interwal)
        except Exception as e:
            logger.error(f"[Legatus] Dobieranie strategii padło: {e}")
            return []

    def _dostosuj_wagi(self, sygnaly: List[SygnalNeuronu],
                       rezim: str) -> List[SygnalNeuronu]:
        """
        Modyfikuje wagi neuronów: mnożnik REŻIMOWY (wg kategorii, WAGI_REZIMU) ×
        mnożnik UCZENIA per-neuron (Igrzyska/HedgeMWU, wizja W-049). Prawo XV —
        wagi ożywione zarówno regułą reżimu, jak i wynikami historycznymi.
        """
        mapa = WAGI_REZIMU.get(rezim, {})
        default = mapa.get("_default", 1.0)
        mn_neuron = self.mnozniki_neuronow
        if not mapa and not mn_neuron:
            return sygnaly

        wynik = []
        for s in sygnaly:
            k = s.kategoria if s.kategoria != "?" else None
            mnoznik_rezim = (mapa.get(k, default) if k else default) if mapa else 1.0
            mnoznik_uczenie = mn_neuron.get(s.neuron_id, 1.0)
            mnoznik = mnoznik_rezim * mnoznik_uczenie
            if mnoznik != 1.0:
                import copy
                s2 = copy.copy(s)
                s2.waga = max(1, min(10, round(s.waga * mnoznik)))
                s2.policz_finalna()
                wynik.append(s2)
            else:
                wynik.append(s)
        return wynik


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

    from imperium.legiony.neurony.momentum import NeuronStochRSI, NeuronRSI

    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')

    neurony = [NeuronStochRSI(), NeuronRSI()]
    legatus = Legatus(neurony, min_neuronow=1, min_przewaga=0.4)

    wskazniki = {"STOCHRSI": 15.0, "RSI_14": 25.0}
    raport = legatus.fokus("BTCUSDT", wskazniki, rezim="TREND_STRONG")

    print(f"\n=== Raport Legatusa: {raport.symbol} ===")
    print(f"Tryb: {raport.tryb} | Reżim: {raport.rezim}")
    print(f"Kierunek: {raport.kierunek} | Pewność: {raport.pewnosc_agregatu:.2%}")
    print(f"Siła LONG: {raport.sila_long:.2%} | Siła SHORT: {raport.sila_short:.2%}")
    print(f"Neurony: {raport.aktywnych_neuronow} aktywnych, {raport.zgodnych_neuronow} zgodnych")
    if raport.weto:
        print(f"⛔ WETO: {raport.powod_weta}")
    else:
        print("✅ Gotowy dla Senatu")
