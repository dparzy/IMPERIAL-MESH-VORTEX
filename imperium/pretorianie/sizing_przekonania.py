"""
Sizing Przekonania (W-318) — większa stawka na mocniejszej okazji.

DLA NOWICJUSZA: symulacja 9-letnia pokazała, że sama SELEKCJA najlepszych okazji
(TOP-N) daje MNIEJ zysku niż granie wszystkim — bo przycina „gruby ogon" (rzadkie
ale ogromne pompy, np. DOGE), nie kompensując tego większą stawką. Wizja Cezara jest
inna: „mało trade'ów, ale z WIĘKSZYM lewarem/stawką na najlepszych". Ten moduł to
realizuje: im mocniejsza okazja (większe przekonanie), tym większy mnożnik kapitału.

Zasada (conviction-based sizing): przekonanie ∈ [0,1] → mnożnik stawki ∈ [min, max]:
  • przekonanie = prog_neutralny  → mnożnik 1.0 (stawka bazowa)
  • przekonanie → 1.0             → mnożnik rośnie liniowo do max_mnoznik (betuj dużo)
  • przekonanie → 0.0             → mnożnik maleje do min_mnoznik (betuj mało)

Plus FRACTIONAL KELLY jako principled backbone (Kelly: f = (b·p − q)/b; half-Kelly
= ×0.5 to standard profesjonalistów — ~75% wzrostu przy dużo mniejszym drawdownie).

Źródła: Kelly criterion (Zerodha, Coriva); fractional Kelly (enlightenedstocktrading);
conviction sizing (completetradersedge). ⚠️ progi (max 3×, half-Kelly) do kalibracji
walk-forward/live — nie peer-review na konkretnych liczbach.
"""

from dataclasses import dataclass


@dataclass
class SizingPrzekonania:
    """
    min_mnoznik:     dolny mnożnik stawki przy zerowym przekonaniu (np. 0.5×).
    max_mnoznik:     górny mnożnik stawki przy pełnym przekonaniu (np. 3.0×).
    prog_neutralny:  przekonanie, przy którym mnożnik = 1.0 (stawka bazowa).
    """
    min_mnoznik: float = 0.5
    max_mnoznik: float = 3.0
    prog_neutralny: float = 0.5

    def mnoznik(self, przekonanie: float) -> float:
        """Mapuje przekonanie ∈ [0,1] na mnożnik stawki ∈ [min_mnoznik, max_mnoznik]."""
        p = max(0.0, min(1.0, przekonanie))
        if p >= self.prog_neutralny:
            zakres = 1.0 - self.prog_neutralny
            t = (p - self.prog_neutralny) / zakres if zakres > 1e-9 else 0.0
            return round(1.0 + t * (self.max_mnoznik - 1.0), 4)
        t = p / self.prog_neutralny if self.prog_neutralny > 1e-9 else 0.0
        return round(self.min_mnoznik + t * (1.0 - self.min_mnoznik), 4)

    @staticmethod
    def kelly_frakcja(p_wygranej: float, rr: float, frakcja: float = 0.5) -> float:
        """
        Fractional Kelly. f* = (b·p − q)/b, gdzie b=rr (Risk:Reward), p=win, q=1−p.
        Wynik przycięty do ≥0 (nie betujemy przy ujemnej przewadze) i ×frakcja
        (half-Kelly domyślnie — ochrona przed błędem estymaty p).
        """
        if rr <= 0:
            return 0.0
        p = max(0.0, min(1.0, p_wygranej))
        q = 1.0 - p
        f = (rr * p - q) / rr
        return round(max(0.0, f) * frakcja, 4)
