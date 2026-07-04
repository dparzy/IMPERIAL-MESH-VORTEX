"""
🎯 KALIBRATOR KONFORMALNY — twarda gwarancja pokrycia dla pewności roju (Prawo XXV).

═══════════════════════════════════════════════════════════════════════════════
ZASADA PEŁNEGO OPISU (ZPO):

Pełna nazwa: Adaptive Conformal Inference (ACI) — adaptacyjne wnioskowanie konformalne.
Źródło: Isaac Gibbs, Emmanuel Candès (2021), „Adaptive Conformal Inference Under
        Distribution Shift", NeurIPS 2021.  https://arxiv.org/abs/2106.00170
Podstawa (split conformal + korekta skończonej próby): Vovk, Gammerman, Shafer,
        „Algorithmic Learning in a Random World" (2005).
Status weryfikacji: ⚠️ implementacja własna wg wzorów z pracy (nie biblioteka zewnętrzna);
        pokrycie zweryfikowane testami (test_kalibrator_konformalny.py).

DLA NOWICJUSZA:
Gdy rój mówi „pewność 0.7" — to jest liczba wyssana z głosowania, NIE gwarancja.
Conformal prediction odwraca pytanie: zamiast „jak bardzo ufam?", liczy „w jakim
przedziale prawda ląduje w X% przypadków?" — z DOWODEM pokrycia. ACI dokłada obronę
przed dryfem rynku: po każdym barze dostraja poziom, żeby długoterminowe pokrycie
trafiało w cel (np. 90%), nawet gdy zmienność skacze (krypto = ciągły dryf).

DLACZEGO UNIKAT (Prawo XVI — nie redundancja):
Meta-labeling daje prawdopodobieństwo, ale NIEskalibrowane. Ten moduł mierzy realne
pokrycie i koryguje — nowa informacja (niepewność z gwarancją), nie kopia istniejącego
sygnału. Dekorelowany: nie generuje kierunku, tylko szerokość zaufania.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import math
from collections import deque


class KalibratorKonformalny:
    """Adaptacyjny kalibrator konformalny (ACI) na strumieniu wyników roju."""

    def __init__(self, cel_pokrycia: float = 0.90, okno: int = 250, gamma: float = 0.01):
        if not 0.0 < cel_pokrycia < 1.0:
            raise ValueError("cel_pokrycia musi być w (0,1), np. 0.90")
        if okno < 1:
            raise ValueError("okno musi być >= 1")
        if gamma <= 0:
            raise ValueError("gamma (krok adaptacji) musi być > 0")
        self.cel_pokrycia = cel_pokrycia
        self.alpha_cel = 1.0 - cel_pokrycia        # docelowy poziom pominięcia
        self.alpha_t = self.alpha_cel              # bieżący (adaptowany) poziom
        self.gamma = gamma
        self._scores: deque[float] = deque(maxlen=okno)

    # ── zbieranie nonconformity scores (|błąd| ≥ 0) ──────────────────────────
    def dodaj_score(self, score: float) -> None:
        """Dokłada nonconformity score (bezwzględny błąd predykcji, ≥ 0)."""
        self._scores.append(abs(float(score)))

    @property
    def n(self) -> int:
        return len(self._scores)

    # ── kwantyl konformalny z korektą skończonej próby ───────────────────────
    def kwantyl(self, alpha: float | None = None) -> float:
        """
        Zwraca konformalny kwantyl nonconformity (promień przedziału).
        Korekta skończonej próby: poziom = ceil((n+1)(1-alpha)) / n (Vovk).
        Brak danych → inf (nie potrafimy zagwarantować pokrycia).
        alpha=0 (100% pokrycia) przy skończonej próbie → inf (uczciwie, Prawo I).
        """
        a = self.alpha_t if alpha is None else alpha
        a = min(1.0, max(0.0, a))
        n = self.n
        if n == 0:
            return math.inf
        posortowane = sorted(self._scores)
        # indeks rangowy (1-based) kwantyla z korektą (n+1)
        ranga = math.ceil((n + 1) * (1.0 - a))
        if ranga > n:
            return math.inf          # nie da się zagwarantować tak wysokiego pokrycia
        if ranga < 1:
            return 0.0               # alpha≈1: zerowy przedział
        return posortowane[ranga - 1]

    def przedzial(self, punkt: float, alpha: float | None = None) -> tuple[float, float]:
        """Przedział predykcyjny [punkt - q, punkt + q] o gwarantowanym pokryciu."""
        q = self.kwantyl(alpha)
        return (punkt - q, punkt + q)

    def pokryty(self, punkt: float, prawda: float, alpha: float | None = None) -> bool:
        """Czy obserwacja `prawda` wpadła w przedział wokół `punkt`?"""
        d, g = self.przedzial(punkt, alpha)
        return d <= prawda <= g

    # ── krok adaptacyjny ACI (Gibbs & Candès) ────────────────────────────────
    def krok(self, pokryty: bool) -> float:
        """
        Aktualizuje alpha_t po obserwacji: alpha_{t+1}=alpha_t+gamma*(alpha_cel-err),
        err=0 gdy pokryte, 1 gdy nie. Miss → alpha maleje → szerszy przedział → więcej
        pokrycia; hit → alpha rośnie → węższy. Długofalowo pokrycie dąży do celu.
        Zwraca nowe alpha_t (przycięte do [0,1]).
        """
        err = 0.0 if pokryty else 1.0
        self.alpha_t = min(1.0, max(0.0, self.alpha_t + self.gamma * (self.alpha_cel - err)))
        return self.alpha_t

    def obserwuj(self, punkt: float, prawda: float) -> bool:
        """Wygodny cykl: policz pokrycie bieżącym przedziałem, zrób krok ACI, dołóż score.
        Zwraca czy było pokryte (przed adaptacją)."""
        czy = self.pokryty(punkt, prawda)
        self.krok(czy)
        self.dodaj_score(prawda - punkt)
        return czy
