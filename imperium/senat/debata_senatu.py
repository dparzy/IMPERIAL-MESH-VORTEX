"""
Debata Senatu (W-343) — jawna debata Byk / Niedźwiedź / Cenzor-Ryzyka.

Inspiracja: trójwarstwowe systemy multi-agent (Bull / Bear / Risk Supervisor),
które w badaniach 2026 (BlackRock/Columbia) biją pojedyncze modele LLM.
Tu — czysty Python, zero zależności, operuje na GŁOSACH ROJU (nie na LLM).

Różnica wobec MetaCortex (N-BRAIN-026): tamten to generyczny MoA z TA-Lib,
niepodpięty do pipeline. Ten Senat czyta sygnały neuronów + ich MECHANIZM
(Prawo XXII) i routuje je do trzech senatorów, którzy się spierają.

Rola:
  • SenatorByk      — zbiera dowody PRO-LONG (trend/momentum/breakout)
  • SenatorNiedzwiedz — zbiera dowody PRO-SHORT
  • Cenzor (Ryzyko) — patrzy WYŁĄCZNIE na risk_filter + reżim; ma prawo WETA
  • KonsulSenatu    — waży argumenty, stosuje weto Cenzora → werdykt + protokół

Zasada: Cenzor nie prognozuje kierunku — pilnuje, by nie wejść w pułapkę
(toksyczny flow, kaskada, manipulacja, panika). To trzeci, niezależny głos.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


# Mechanizmy „bycze" (sprzyjają kierunkowi sygnału) vs „obronne" (Cenzor)
_MECH_KIERUNKOWE = {"trend", "mean_rev", "breakout", "stat_arb", "vol_signal"}
_MECH_OBRONNE = {"risk_filter"}
_MECH_KONTEKST = {"regime", "event"}


@dataclass
class GlosNeuronu:
    """Lekki widok sygnału neuronu na potrzeby debaty."""
    klucz: str
    kierunek: str        # LONG/SHORT/NEUTRAL
    pewnosc: float       # [0,1]
    waga: float
    mechanizm: str = "trend"
    kategoria: str = "?"


@dataclass
class ArgumentSenatora:
    senator: str
    stanowisko: str      # LONG/SHORT/WSTRZYMAJ
    sila: float          # [0,1]
    uzasadnienie: str
    dowody: List[str] = field(default_factory=list)


@dataclass
class WerdyktSenatu:
    kierunek: str           # LONG/SHORT/NEUTRAL
    pewnosc: float
    weto_cenzora: bool
    powod_weta: str
    protokol: List[ArgumentSenatora] = field(default_factory=list)
    mnoznik_ryzyka: float = 1.0   # [0,1] — Cenzor może zmniejszyć rozmiar

    def streszczenie(self) -> str:
        weto = " ⛔WETO" if self.weto_cenzora else ""
        return f"{self.kierunek} @ {self.pewnosc:.0%}{weto} (ryzyko×{self.mnoznik_ryzyka:.2f})"


# ─── Senatorowie ──────────────────────────────────────────────────────────────

class SenatorByk:
    """Adwokat strony LONG. Zbiera kierunkowe głosy LONG, mierzy ich siłę."""

    def przemow(self, glosy: List[GlosNeuronu]) -> ArgumentSenatora:
        long_glosy = [g for g in glosy
                      if g.kierunek == "LONG" and g.mechanizm in _MECH_KIERUNKOWE]
        sila = sum(g.pewnosc * g.waga for g in long_glosy)
        dowody = [f"{g.klucz}({g.mechanizm},{g.pewnosc:.0%})"
                  for g in sorted(long_glosy, key=lambda x: -x.pewnosc * x.waga)[:5]]
        n = len(long_glosy)
        uzas = (f"{n} neuronów kierunkowych za LONG (siła ważona {sila:.1f})"
                if n else "brak kierunkowych dowodów na LONG")
        return ArgumentSenatora("Byk", "LONG", sila, uzas, dowody)


class SenatorNiedzwiedz:
    """Adwokat strony SHORT."""

    def przemow(self, glosy: List[GlosNeuronu]) -> ArgumentSenatora:
        short_glosy = [g for g in glosy
                       if g.kierunek == "SHORT" and g.mechanizm in _MECH_KIERUNKOWE]
        sila = sum(g.pewnosc * g.waga for g in short_glosy)
        dowody = [f"{g.klucz}({g.mechanizm},{g.pewnosc:.0%})"
                  for g in sorted(short_glosy, key=lambda x: -x.pewnosc * x.waga)[:5]]
        n = len(short_glosy)
        uzas = (f"{n} neuronów kierunkowych za SHORT (siła ważona {sila:.1f})"
                if n else "brak kierunkowych dowodów na SHORT")
        return ArgumentSenatora("Niedźwiedź", "SHORT", sila, uzas, dowody)


class Cenzor:
    """
    Strażnik Ryzyka (Risk Supervisor). Patrzy WYŁĄCZNIE na neurony risk_filter
    i reżim. Nie prognozuje kierunku — decyduje, czy w ogóle bezpiecznie wchodzić.

    prog_weta: jeśli ważona siła alarmów ≥ prog_weta → WETO (cisza).
    Inaczej: skaluje rozmiar pozycji w dół proporcjonalnie do poziomu zagrożenia.
    """

    def __init__(self, prog_weta: float = 12.0):
        self.prog_weta = prog_weta

    def przemow(self, glosy: List[GlosNeuronu],
                rezim: str = "NORMAL") -> ArgumentSenatora:
        alarmy = [g for g in glosy
                  if g.mechanizm in _MECH_OBRONNE
                  and g.kierunek != "NEUTRAL"
                  and g.pewnosc > 0]
        sila_alarmow = sum(g.pewnosc * g.waga for g in alarmy)
        dowody = [f"{g.klucz}({g.pewnosc:.0%})"
                  for g in sorted(alarmy, key=lambda x: -x.pewnosc * x.waga)[:5]]

        # Reżim PANIC = automatyczny silny mnożnik alarmu
        if rezim == "PANIC":
            sila_alarmow += self.prog_weta  # gwarantuje weto
            dowody.insert(0, "REŻIM:PANIC")

        if sila_alarmow >= self.prog_weta:
            return ArgumentSenatora(
                "Cenzor", "WSTRZYMAJ", min(1.0, sila_alarmow / self.prog_weta),
                f"WETO — poziom zagrożenia {sila_alarmow:.1f} ≥ próg {self.prog_weta}",
                dowody,
            )
        uzas = (f"podwyższone ryzyko {sila_alarmow:.1f} — redukcja rozmiaru"
                if alarmy else "brak alarmów ryzyka — droga wolna")
        return ArgumentSenatora("Cenzor", "WSTRZYMAJ" if False else "OK",
                                sila_alarmow, uzas, dowody)


# ─── Konsul — przewodniczący debaty ───────────────────────────────────────────

class KonsulSenatu:
    """
    Przewodniczy debacie: zbiera argumenty trzech senatorów, waży Byka vs
    Niedźwiedzia, stosuje weto/redukcję Cenzora → WerdyktSenatu z protokołem.
    """

    def __init__(self, prog_weta_cenzora: float = 12.0,
                 prog_przewagi: float = 0.0):
        self.byk = SenatorByk()
        self.niedzwiedz = SenatorNiedzwiedz()
        self.cenzor = Cenzor(prog_weta=prog_weta_cenzora)
        self.prog_przewagi = prog_przewagi

    def obraduj(self, glosy: List[GlosNeuronu],
                rezim: str = "NORMAL") -> WerdyktSenatu:
        arg_byk = self.byk.przemow(glosy)
        arg_bear = self.niedzwiedz.przemow(glosy)
        arg_cenzor = self.cenzor.przemow(glosy, rezim=rezim)
        protokol = [arg_byk, arg_bear, arg_cenzor]

        # Werdykt kierunkowy: silniejsza strona wygrywa
        razem = arg_byk.sila + arg_bear.sila + 1e-9
        if arg_byk.sila > arg_bear.sila:
            kierunek = "LONG"
            pewnosc = arg_byk.sila / razem
        elif arg_bear.sila > arg_byk.sila:
            kierunek = "SHORT"
            pewnosc = arg_bear.sila / razem
        else:
            kierunek = "NEUTRAL"
            pewnosc = 0.0

        # Próg przewagi — za słaba dominacja = NEUTRAL
        if kierunek != "NEUTRAL" and pewnosc < self.prog_przewagi:
            kierunek = "NEUTRAL"
            pewnosc = 0.0

        # Weto Cenzora
        weto = arg_cenzor.stanowisko == "WSTRZYMAJ"
        powod_weta = arg_cenzor.uzasadnienie if weto else ""
        if weto:
            kierunek = "NEUTRAL"
            pewnosc = 0.0
            mnoznik = 0.0
        else:
            # Redukcja rozmiaru proporcjonalna do poziomu alarmów (nie weta)
            mnoznik = max(0.3, 1.0 - arg_cenzor.sila / self.cenzor.prog_weta)

        return WerdyktSenatu(
            kierunek=kierunek,
            pewnosc=round(pewnosc, 4),
            weto_cenzora=weto,
            powod_weta=powod_weta,
            protokol=protokol,
            mnoznik_ryzyka=round(mnoznik, 3),
        )

    def drukuj_protokol(self, werdykt: WerdyktSenatu) -> None:
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          🏛️  PROTOKÓŁ DEBATY SENATU                       ║")
        print("╠══════════════════════════════════════════════════════════╣")
        for arg in werdykt.protokol:
            ikona = {"Byk": "🐂", "Niedźwiedź": "🐻", "Cenzor": "⚖️"}.get(arg.senator, "•")
            print(f"║ {ikona} {arg.senator:<11} [{arg.stanowisko:<9}] siła={arg.sila:.1f}")
            print(f"║    {arg.uzasadnienie}")
            if arg.dowody:
                print(f"║    dowody: {', '.join(arg.dowody)}")
        print("╠══════════════════════════════════════════════════════════╣")
        print(f"║ WERDYKT: {werdykt.streszczenie()}")
        if werdykt.weto_cenzora:
            print(f"║ ⛔ {werdykt.powod_weta}")
        print("╚══════════════════════════════════════════════════════════╝")


# ─── Adapter: RaportLegatusa → głosy debaty ───────────────────────────────────

def glosy_z_raportu(raport, mapa_mechanizmow: Optional[Dict[str, str]] = None,
                    mapa_kategorii: Optional[Dict[str, str]] = None
                    ) -> List[GlosNeuronu]:
    """
    Buduje listę GlosNeuronu z RaportLegatusa (lub dowolnego obiektu z .sygnaly).
    mapa_mechanizmow: {klucz: mechanizm} (z rejestr.MECHANIZMY).
    """
    mapa_mechanizmow = mapa_mechanizmow or {}
    mapa_kategorii = mapa_kategorii or {}
    glosy = []
    for s in getattr(raport, "sygnaly", []):
        klucz = getattr(s, "klucz_neuronu", None) or getattr(s, "klucz", "?")
        glosy.append(GlosNeuronu(
            klucz=klucz,
            kierunek=getattr(s, "kierunek", "NEUTRAL"),
            pewnosc=getattr(s, "pewnosc_finalna", None) or getattr(s, "pewnosc", 0.0),
            waga=getattr(s, "waga", 1.0),
            mechanizm=mapa_mechanizmow.get(klucz, "trend"),
            kategoria=mapa_kategorii.get(klucz, getattr(s, "kategoria", "?")),
        ))
    return glosy


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    glosy = [
        GlosNeuronu("X-03", "LONG", 0.80, 8, "trend", "M"),
        GlosNeuronu("XII-03", "LONG", 0.72, 7, "trend", "T"),
        GlosNeuronu("V-01", "LONG", 0.60, 6, "trend", "F"),
        GlosNeuronu("X-01", "SHORT", 0.55, 6, "mean_rev", "M"),
        GlosNeuronu("Z-01", "SHORT", 0.40, 6, "risk_filter", "Z"),
        GlosNeuronu("A-01", "SHORT", 0.30, 5, "risk_filter", "A"),
    ]
    konsul = KonsulSenatu()

    print("\n=== Scenariusz 1: trend byczy, niskie ryzyko ===")
    w = konsul.obraduj(glosy, rezim="TREND_STRONG")
    konsul.drukuj_protokol(w)

    print("\n=== Scenariusz 2: PANIC → weto Cenzora ===")
    w2 = konsul.obraduj(glosy, rezim="PANIC")
    konsul.drukuj_protokol(w2)
