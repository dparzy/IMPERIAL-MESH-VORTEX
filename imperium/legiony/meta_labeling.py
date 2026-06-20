"""
W-337 | B-01 Meta-labeling — bet-sizing layer nad Legatusem.

DLA NOWICJUSZA: Legatus daje KIERUNEK (LONG/SHORT) z pewnością 0-100%. Ale to nie mówi
NIC o tym, ILE postawić. Meta-labeling (López de Prado, AFML Ch3) dodaje DRUGI MODEL:
„Czy mój sygnał pierwotny tym razem ma rację? Jeśli tak — ile postawić?"

Wynik: bet_size ∈ [0.0, 1.0] — mnożnik rozmiaru pozycji.
  - 0.0 → meta-model mówi „nie wchodzę" (niska trafność historyczna w tym kontekście)
  - 1.0 → „wchodzę pełną pozycją" (wysoka pewność zagregowana)
  - [0.3..0.7] → skaluje pozycję (F. Kelly fraction)

Implementacja:
  MetaLabelingScorer — online logistic regression (bez scikit-learn, czyste Python/math).
  Trenuje na parach (cechy_raportu → wynik: 1=dobry_sygnał, 0=zły_sygnał).
  Cechy: pewnosc_agregatu, sila_long, sila_short, log_aktywnych, log_zgodnych.
  Wynik jest podawany przez użytkownika (np. czy pozycja skończyła się zyskiem).

Brak lookahead (Prawo I): bet_size w kroku t używa wyłącznie historii do t-1.
Brak scikit-learn: logistic regression zaimplementowana ręcznie (SGD online).

Źródło: López de Prado, Advances in Financial Machine Learning, Ch3 — Meta-labeling.
  https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086
  (⚠️ pełny tekst niezweryfikowany — opis rozdziału potwierdzony)
"""

import math
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger("MetaLabeling")


# ─── Cechy raportu Legatusa ───────────────────────────────────────────────────

@dataclass
class CechyMeta:
    """Wektor cech wejściowych dla meta-modelu (wyciągnięty z RaportLegatusa)."""
    pewnosc_agregatu: float      # dominujący kierunek
    sila_long: float             # surowa siła LONG (nie-znormalizowana)
    sila_short: float            # surowa siła SHORT
    log_aktywnych: float         # log(aktywnych_neuronow + 1)
    log_zgodnych: float          # log(zgodnych_neuronow + 1)
    roznica_sil: float           # |sila_long - sila_short| / (sila_long + sila_short + 1e-9)

    @staticmethod
    def z_raportu(raport) -> "CechyMeta":
        """Buduje CechyMeta z RaportLegatusa (duck typing — nie importujemy Legatusa)."""
        p = float(raport.pewnosc_agregatu)
        sl = float(raport.sila_long)
        ss = float(raport.sila_short)
        n = max(1, int(raport.aktywnych_neuronow))
        z = max(0, int(raport.zgodnych_neuronow))
        razem = sl + ss + 1e-9
        return CechyMeta(
            pewnosc_agregatu=p,
            sila_long=sl,
            sila_short=ss,
            log_aktywnych=math.log(n + 1),
            log_zgodnych=math.log(z + 1),
            roznica_sil=abs(sl - ss) / razem,
        )

    def jako_wektor(self) -> List[float]:
        return [
            self.pewnosc_agregatu,
            self.sila_long,
            self.sila_short,
            self.log_aktywnych,
            self.log_zgodnych,
            self.roznica_sil,
        ]


# ─── Online logistic regression (SGD) ────────────────────────────────────────

def _sigmoid(x: float) -> float:
    """Sigmoid klamkowany dla stabilności numerycznej."""
    x = max(-30.0, min(30.0, x))
    return 1.0 / (1.0 + math.exp(-x))


class _LogisticSGD:
    """
    Logistyczna regresja online (SGD, learning rate = stała).
    D=6 cech (CechyMeta.jako_wektor()), bias włączony.
    Inicjalizacja zerami (bet_size = 0.5 przed pierwszym treningiem — agnostyczne).
    """

    def __init__(self, lr: float = 0.05, l2: float = 0.001):
        self._D = 6
        self._lr = lr
        self._l2 = l2
        self._w: List[float] = [0.0] * self._D
        self._b: float = 0.0
        self._n_prob = 0  # liczba próbek

    def przewiduj(self, x: List[float]) -> float:
        """P(dobry_sygnal | cechy). Przed pierwszym treningiem zwraca 0.5."""
        logit = self._b + sum(wi * xi for wi, xi in zip(self._w, x))
        return _sigmoid(logit)

    def ucz(self, x: List[float], y: int) -> None:
        """
        Jedna aktualizacja SGD. y ∈ {0, 1}: 1=dobry_sygnal (zysk), 0=zły.
        Gradient logistic loss + L2 regularization.
        """
        p = self.przewiduj(x)
        err = p - y
        # gradient descent
        self._b -= self._lr * err
        for i, xi in enumerate(x):
            self._w[i] -= self._lr * (err * xi + self._l2 * self._w[i])
        self._n_prob += 1

    @property
    def wyuczony(self) -> bool:
        return self._n_prob >= 10  # minimalny próg wiarygodności

    @property
    def liczba_prob(self) -> int:
        return self._n_prob


# ─── MetaLabelingScorer — główna klasa ───────────────────────────────────────

@dataclass
class WynikMeta:
    """Wynik meta-oceny dla jednego raportu Legatusa."""
    bet_size: float                   # ∈ [0.0, 1.0] — mnożnik rozmiaru pozycji
    pewnosc_meta: float               # P(dobry_sygnal) z meta-modelu ∈ [0.0, 1.0]
    wyuczony: bool                    # czy model ma ≥10 próbek treningowych
    liczba_prob: int                  # próbek treningowych dotychczas
    powod: str = ""                   # diagnostyka
    timestamp: float = field(default_factory=time.time)


class MetaLabelingScorer:
    """
    B-01 Meta-labeling scorer (online, bez zewnętrznych zależności).

    Użycie:
      scorer = MetaLabelingScorer()
      # po każdym raporcie Legatusa:
      wynik = scorer.ocen(raport_legatusa)
      # po zamknięciu pozycji (znamy wynik):
      scorer.zaktualizuj(raport_legatusa, zysk=True)  # True=zysk, False=strata

    bet_size = Kelly fraction × pewnosc_meta × saturacja(aktywnych_neuronow).
    Przed wyuczeniem: bet_size = pewnosc_agregatu (passthrough z Legatusa).
    """

    def __init__(
        self,
        lr: float = 0.05,
        l2: float = 0.001,
        min_bet: float = 0.0,
        max_bet: float = 1.0,
    ):
        self._model = _LogisticSGD(lr=lr, l2=l2)
        self._min_bet = min_bet
        self._max_bet = max_bet

    def ocen(self, raport) -> WynikMeta:
        """
        Oblicz bet_size dla bieżącego raportu Legatusa.
        Brak lookahead: używa wyłącznie wag nauczonych do tej chwili.
        """
        if raport.weto or raport.kierunek == "NEUTRAL":
            return WynikMeta(
                bet_size=0.0,
                pewnosc_meta=0.0,
                wyuczony=self._model.wyuczony,
                liczba_prob=self._model.liczba_prob,
                powod="WETO lub NEUTRAL — bet_size=0",
            )

        cechy = CechyMeta.z_raportu(raport)
        x = cechy.jako_wektor()
        p_meta = self._model.przewiduj(x)

        # Kelly fraction: f = 2p − 1, klamkowane do [0,1]
        kelly = max(0.0, 2.0 * p_meta - 1.0)
        kelly_bet = kelly * float(raport.pewnosc_agregatu)
        passthrough = float(raport.pewnosc_agregatu)

        # Płynna interpolacja przez pierwsze WARMUP_N próbek — eliminuje skok przy progu
        _WARMUP_N = 20
        alpha = min(1.0, self._model.liczba_prob / _WARMUP_N)
        bet = (1.0 - alpha) * passthrough + alpha * kelly_bet
        powod = (
            f"Pre-trening α={alpha:.2f} ({self._model.liczba_prob}/{_WARMUP_N})"
            if alpha < 1.0
            else f"Meta P={p_meta:.3f}, Kelly={kelly:.3f}, Legatus={raport.pewnosc_agregatu:.3f}"
        )

        bet = max(self._min_bet, min(self._max_bet, bet))
        return WynikMeta(
            bet_size=round(bet, 4),
            pewnosc_meta=round(p_meta, 4),
            wyuczony=self._model.wyuczony,
            liczba_prob=self._model.liczba_prob,
            powod=powod,
        )

    def zaktualizuj(self, raport, zysk: bool) -> None:
        """
        Dodaj próbkę treningową po zamknięciu pozycji.
        zysk=True (1) → sygnał był dobry, False (0) → zły.
        Ignoruje NEUTRAL/WETO (nie ma czego uczyć).
        """
        if raport.weto or raport.kierunek == "NEUTRAL":
            return
        cechy = CechyMeta.z_raportu(raport)
        self._model.ucz(cechy.jako_wektor(), 1 if zysk else 0)
        logger.debug(
            "MetaLabeling update: kierunek=%s zysk=%s próbki=%d",
            raport.kierunek, zysk, self._model.liczba_prob,
        )

    @property
    def wyuczony(self) -> bool:
        return self._model.wyuczony

    @property
    def liczba_prob(self) -> int:
        return self._model.liczba_prob

    def diagnostyka(self) -> dict:
        """Diagnostyka stanu modelu (do logów i audytów)."""
        return {
            "wyuczony": self._model.wyuczony,
            "liczba_prob": self._model.liczba_prob,
            "wagi": [round(w, 4) for w in self._model._w],
            "bias": round(self._model._b, 4),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# W-359 | Bet Sizing LdP — Gaussian CDF + averaging + dyskretyzacja (AFML Ch. 10)
# ═══════════════════════════════════════════════════════════════════════════════

"""
Ulepszony bet sizing per López de Prado (AFML Ch. 10, §10.2-10.4).

Trzy uzupełnienia nad istniejącym Kelly:

1. GAUSSIAN CDF MAPPING (§10.2):
   m = 2·Φ(z) − 1,  gdzie z = (p − 1/K) / √(p·(1-p))
   Zamiast liniowego Kelly 2p-1, mapuje przez CDF normalną:
   • p=0.5 → z=0 → m=0 (neutral)
   • p=0.6 → m≈0.32 vs Kelly 0.20 (mocniej skaluje przy większej pewności)
   • p=1.0 → m=1.0 (pełna pozycja)
   Bardziej agresywna w środku, ta sama granica 0/1.

2. AVERAGING ACTIVE BETS (§10.3):
   Gdy masz N aktywnych pozycji, ich sugerowane rozmiary uśredniaj → niższy
   turnover, mniej przehandlowania. Zamiast skakać bet_size co bar — stopniowe
   wygładzanie przez bufor aktywnych pozycji.

3. SIZE DISCRETIZATION (§10.4):
   m* = round(m / d) × d   np. d=0.1 → m∈{0, 0.1, 0.2,...,1.0}
   Eliminuje mikrodrgania (0.731 → 0.73 → zlecenie, 0.734 → znowu 0.73 = brak ruchu).
   Drastycznie redukuje koszty transakcyjne.
"""


def _phi(x: float) -> float:
    """Dystrybuanta N(0,1) przez erf (stdlib, bez scipy)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bet_size_ldp(
    p: float,
    k: int = 2,
    dyskretyzacja: float = 0.05,
) -> float:
    """
    Bet size z prawdopodobieństwa klasyfikatora przez CDF normalną (AFML §10.2).

    Parametry:
      p              — P(dobry sygnał) ∈ [0, 1]
      k              — liczba klas (2 = binary: dobry/zły)
      dyskretyzacja  — krok zaokrąglenia (0.05 → {0, 0.05, 0.10,...,1.0})

    Zwraca: m ∈ [0, 1] — rozmiar betu.
    """
    p = max(0.0, min(1.0, p))
    pvar = p * (1.0 - p)
    if pvar <= 0:
        m = 1.0 if p >= 0.5 else 0.0
    else:
        z = (p - 1.0 / k) / math.sqrt(pvar)
        m = max(0.0, 2.0 * _phi(z) - 1.0)

    if dyskretyzacja > 0:
        m = round(m / dyskretyzacja) * dyskretyzacja

    return round(min(1.0, max(0.0, m)), 4)


class BuforAktywnych:
    """
    Averaging Active Bets (AFML §10.3) — wygładza bet_size przez uśrednianie
    sugerowanych rozmiarów dla nakładających się pozycji.

    Użycie:
      bufor = BuforAktywnych(max_pozycji=10)
      bufor.dodaj("BTCUSDT", 0.8)
      m = bufor.srednia()   # uśredniona wielkość
      bufor.zamknij("BTCUSDT")
    """

    def __init__(self, max_pozycji: int = 20) -> None:
        self._aktywne: Dict[str, float] = {}
        self._max = max_pozycji

    def dodaj(self, symbol: str, bet_size: float) -> None:
        """Dodaje lub aktualizuje bet_size dla symbolu."""
        if len(self._aktywne) >= self._max and symbol not in self._aktywne:
            logger.warning("[BuforAktywnych] Bufor pełny (%d) — %s pominięty", self._max, symbol)
            return
        self._aktywne[symbol] = bet_size

    def zamknij(self, symbol: str) -> None:
        """Usuwa symbol po zamknięciu pozycji."""
        self._aktywne.pop(symbol, None)

    def srednia(self) -> float:
        """Uśredniony bet_size aktywnych pozycji (averaging active bets)."""
        if not self._aktywne:
            return 0.0
        return sum(self._aktywne.values()) / len(self._aktywne)

    def bet_dla(self, symbol: str) -> float:
        """Bieżący bet_size dla symbolu (lub 0.0 jeśli nieaktywny)."""
        return self._aktywne.get(symbol, 0.0)

    def aktywne(self) -> Dict[str, float]:
        return dict(self._aktywne)
