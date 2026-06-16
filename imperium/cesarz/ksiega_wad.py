"""
📕 KSIĘGA WAD — prewencyjny filtr powtarzalnych błędów (W-309).

Wyekstrahowana z Mnemosyne (N-MEM-206 `book_of_flaws`) jako JEDYNA niereduntantna
zdolność tamtego modułu — reszta Mnemosyne (trade-learning) mierzalnie dublowała
PamięćRefleksyjną (W-295, Prawo XVI). Tu zostaje tylko to, czego PamięćRefleksyjna
NIE umie: spojrzenie W PRZÓD — blokada wejścia w setup, który systematycznie tracił.

DLA NOWICJUSZA:
  • PamięćRefleksyjna = pamięć NARRACYJNA (opisuje, co było — patrzy wstecz).
  • KsięgaWad        = pamięć PREWENCYJNA (wetuje, co się nie udaje — patrzy w przód).

Mechanizm (bez nowego magazynu — uczy się z tego samego strumienia zamknięć):
  1. Każde zamknięcie → `zarejestruj(rezim, interwal, pnl)` aktualizuje statystykę
     sygnatury setupu (np. "RANGING/4H").
  2. Sygnatura staje się WADĄ gdy: ≥ min_prob prób ORAZ wskaźnik strat ≥ prog_wady.
  3. `sprawdz(rezim, interwal)` przed wejściem → CZYSTO / OSTRZEŻENIE / WETO.

Domyślnie tylko OSTRZEGA (weto wymaga jawnego prog_weta). Wpięcie do Dyrygenta
jest opt-in (domyślnie OFF — Prawo XV: warstwa adaptacyjna, zero zmiany zachowania).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


def _sygnatura(rezim: str, interwal: str) -> str:
    """Klucz setupu — reżim × interwał. Rozszerzalne o dalsze wymiary kontekstu."""
    return f"{rezim}/{interwal}"


@dataclass
class StatWady:
    """Statystyka jednej sygnatury setupu (np. 'RANGING/4H')."""
    sygnatura: str
    n_prob: int = 0
    n_strat: int = 0
    laczny_pnl: float = 0.0

    def zarejestruj(self, pnl: float) -> None:
        # Break-even (pnl == 0) liczy się jako próba, ale nie jako strata —
        # spójnie z MWU/Igrzyska/Synapsy (pnl_sign=0 → neutralny, Prawo XV/XVI).
        self.n_prob += 1
        self.laczny_pnl += pnl
        if pnl < 0:
            self.n_strat += 1

    @property
    def wskaznik_strat(self) -> float:
        return self.n_strat / self.n_prob if self.n_prob > 0 else 0.0


@dataclass
class WerdyktWady:
    """Wynik prewencyjnego sprawdzenia setupu przed wejściem."""
    czy_wada: bool
    poziom: str            # "CZYSTO" | "OSTRZEŻENIE" | "WETO"
    powod: str
    wskaznik_strat: float
    n_prob: int

    @property
    def blokada(self) -> bool:
        return self.poziom == "WETO"


class KsiegaWad:
    """
    Rejestr powtarzalnych wad setupów — prewencyjny filtr wejść.

    Użycie:
        kw = KsiegaWad()
        kw.zarejestruj("RANGING", "4H", pnl=-50.0)   # online, po każdym zamknięciu
        w = kw.sprawdz("RANGING", "4H")              # przed wejściem
        if w.blokada: ...                            # weto
    """

    def __init__(self, prog_wady: float = 0.65, min_prob: int = 5,
                 prog_weta: Optional[float] = None):
        """
        prog_wady: wskaźnik strat ≥ tej wartości → sygnatura to WADA (ostrzeżenie).
        min_prob:  minimalna liczba prób zanim sygnatura może zostać wadą
                   (Prawo XVI — decyzja na pomiarze, nie na 1-2 próbkach).
        prog_weta: wskaźnik strat ≥ tej wartości → WETO (blokada wejścia).
                   None → księga nigdy nie wetuje, tylko ostrzega (domyślnie bezpieczne).
        """
        assert 0.0 <= prog_wady <= 1.0, "prog_wady ∈ [0,1]"
        assert min_prob >= 1, "min_prob ≥ 1"
        if prog_weta is not None:
            assert prog_wady <= prog_weta <= 1.0, "prog_weta ∈ [prog_wady, 1]"
        self.prog_wady = prog_wady
        self.min_prob = min_prob
        self.prog_weta = prog_weta
        self._staty: Dict[str, StatWady] = {}

    # ── uczenie ────────────────────────────────────────────────────────────────

    def zarejestruj(self, rezim: str, interwal: str, pnl: float) -> None:
        """Online: jedno zamknięcie aktualizuje statystykę sygnatury setupu."""
        sig = _sygnatura(rezim, interwal)
        if sig not in self._staty:
            self._staty[sig] = StatWady(sygnatura=sig)
        self._staty[sig].zarejestruj(pnl)

    def ucz_z_pamieci(self, pamiec) -> int:
        """
        Bootstrap z istniejącej PamięciRefleksyjnej (zamiast nowego magazynu).
        Czyta lekcje i odtwarza statystyki strat per (rezim/interwal).
        Zwraca liczbę przetworzonych lekcji. Prawo XVI — jedno źródło danych.
        """
        n = 0
        for lekcja in pamiec.wczytaj_wszystkie():
            # Lekcja agreguje serię — używamy jej łącznego pnl jako jednego sygnału
            # kierunkowego dla sygnatury (zysk/strata serii w danym reżimie).
            self.zarejestruj(lekcja.rezim, lekcja.interwal, lekcja.pnl_usdt)
            n += 1
        return n

    # ── prewencja ──────────────────────────────────────────────────────────────

    def sprawdz(self, rezim: str, interwal: str) -> WerdyktWady:
        """Sprawdza setup PRZED wejściem. CZYSTO / OSTRZEŻENIE / WETO."""
        sig = _sygnatura(rezim, interwal)
        stat = self._staty.get(sig)
        if stat is None or stat.n_prob < self.min_prob:
            n = stat.n_prob if stat else 0
            return WerdyktWady(
                czy_wada=False, poziom="CZYSTO",
                powod=f"{sig}: za mało prób ({n}<{self.min_prob}) — brak werdyktu",
                wskaznik_strat=stat.wskaznik_strat if stat else 0.0, n_prob=n,
            )
        ws = stat.wskaznik_strat
        if self.prog_weta is not None and ws >= self.prog_weta:
            return WerdyktWady(
                czy_wada=True, poziom="WETO",
                powod=f"{sig}: strat {ws:.0%} ≥ próg weta {self.prog_weta:.0%} "
                      f"({stat.n_strat}/{stat.n_prob}, PnL {stat.laczny_pnl:+.1f}$)",
                wskaznik_strat=ws, n_prob=stat.n_prob,
            )
        if ws >= self.prog_wady:
            return WerdyktWady(
                czy_wada=True, poziom="OSTRZEŻENIE",
                powod=f"{sig}: strat {ws:.0%} ≥ próg wady {self.prog_wady:.0%} "
                      f"({stat.n_strat}/{stat.n_prob}, PnL {stat.laczny_pnl:+.1f}$)",
                wskaznik_strat=ws, n_prob=stat.n_prob,
            )
        return WerdyktWady(
            czy_wada=False, poziom="CZYSTO",
            powod=f"{sig}: strat {ws:.0%} < próg {self.prog_wady:.0%} — setup zdrowy",
            wskaznik_strat=ws, n_prob=stat.n_prob,
        )

    # ── raport ─────────────────────────────────────────────────────────────────

    def wady(self) -> List[Tuple[str, float, int]]:
        """Lista wykrytych wad: (sygnatura, wskaźnik_strat, n_prob), najgorsze pierwsze."""
        wykryte = [
            (s.sygnatura, s.wskaznik_strat, s.n_prob)
            for s in self._staty.values()
            if s.n_prob >= self.min_prob and s.wskaznik_strat >= self.prog_wady
        ]
        wykryte.sort(key=lambda x: x[1], reverse=True)
        return wykryte

    def raport(self) -> Dict[str, object]:
        """Pełny raport księgi — do inspekcji po sesji/backteście."""
        return {
            "n_sygnatur": len(self._staty),
            "wady": [
                {"sygnatura": sig, "wskaznik_strat": round(ws, 4), "n_prob": n}
                for sig, ws, n in self.wady()
            ],
            "prog_wady": self.prog_wady,
            "prog_weta": self.prog_weta,
            "min_prob": self.min_prob,
        }
