"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Lustro Prawdy (The Truth Mirror) — Walidacja Kontradyktoryjna v1.1     ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ        ║
║  Geneza: persona Shinsō (深層) — dorobek zintegrowany do Imperium           ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-BRAIN-073  (numer do potwierdzenia wg ZBADANE)             |
| Nazwa oryginalna    | Lustro Prawdy (The Truth Mirror) — autor: Shinsō            |
| Nazwa w Imperium    | Lustro Prawdy                                                 |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/BRAIN-073_LustroPrawdy.py           |
| Kategoria           | BRAIN / Walidacja kontradyktoryjna sygnałów                  |
| Wpływ na Imperium   | Warstwa obrony: każdy sygnał jest "atakowany" przez          |
|                     | adwersarza przed egzekucją. Rozszerza Guardrails i Prawo I.|
| Powiązane moduły    | N-EYES-028 (OmniSight), N-SHIELDS-205 (AegisShield),         |
|                     | N-BRAIN-026 (MetaCortex)                                     |

────────────────────────────── STATUS REALNOŚCI (Prawo I) ─────────────────────────
UCZCIWIE: to NIE jest trenowana sieć GAN, mimo nazwy. To lekki HEURYSTYCZNY
scorer kontradyktoryjny: liniowy dyskryminator + adwersarz (dot-product + sigmoid)
oraz czarna lista oparta na podobieństwie kosinusowym. Wagi są losowe na starcie,
więc moduł zwraca SZUM, dopóki nie nauczy się na realnych wynikach (train_on_outcome).
Wartościowy jako szkielet/koncept; do produkcji wymaga prawdziwego treningu na
oznaczonych danych (np. z N-MEM-206 Mnemosyne / LanceDB).

CHANGELOG:
  v1.1 (2026-05-28, Kingdom Pixel) — integracja: metryczka Zasada 11, uczciwy opis
        (heurystyka zamiast "GAN"), ostrzeżenie przy braku cech, demo z ziarnem.
  v1.0 (Shinsō) — wersja oryginalna.
═════════════════════════════════════════════════════════════════════════════════════
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("LustroPrawdy")

FEATURE_DIM = 64


@dataclass
class Signal:
    """Struktura sygnału tradingowego."""
    symbol: str
    action: str                     # "BUY" | "SELL" | "HOLD"
    confidence: float               # 0.0 – 1.0
    source: str                     # źródło sygnału (np. "Klucz Kodowy S1")
    reasons: List[str] = field(default_factory=list)
    features: Optional[np.ndarray] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = datetime.now().timestamp()


@dataclass
class AdversarialResult:
    """Wynik kontradyktoryjnej walidacji."""
    signal: Signal
    is_valid: bool
    adversary_confidence: float     # pewność adwersarza, że sygnał jest FAŁSZYWY
    attack_points: List[str]        # słabe punkty znalezione przez adwersarza
    final_confidence: float         # ostateczna pewność po walidacji
    verdict: str                    # "PASSED" | "REJECTED" | "NEUTRAL"


class TruthMirror:
    """
    Heurystyczny system walidacji kontradyktoryjnej (GAN-inspirowany, nie trenowana sieć).
      - Dyskryminator: liniowy scorer prawdopodobieństwa "prawdziwości" sygnału.
      - Adwersarz: liniowy scorer szukający słabych punktów.
      - Czarna lista: podobieństwo kosinusowe do wzorców historycznych strat.
    Uczenie online przez `train_on_outcome` (nudżowanie wag + rozbudowa czarnej listy).
    """

    def __init__(self, learning_rate: float = 0.01, seed: Optional[int] = None):
        self._rng = np.random.default_rng(seed)
        self.lr = learning_rate
        self.discriminator_weights = self._rng.standard_normal(FEATURE_DIM) * 0.01
        self.adversary_weights = self._rng.standard_normal(FEATURE_DIM) * 0.01
        self.blacklist_patterns: List[np.ndarray] = []
        self.training_history: List[Dict] = []
        self.version = "1.1.0"

    def _extract_features(self, signal: Signal) -> np.ndarray:
        """Ekstrahuje cechy z sygnału. UWAGA: brak cech → wektor losowy (werdykt = szum)."""
        if signal.features is None:
            logger.warning("[LustroPrawdy] Sygnał bez cech — używam wektora losowego; werdykt niemiarodajny.")
            return self._rng.standard_normal(FEATURE_DIM)
        return np.asarray(signal.features, dtype=np.float64)[:FEATURE_DIM]

    @staticmethod
    def _sigmoid(x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    def _discriminate(self, features: np.ndarray) -> float:
        return self._sigmoid(float(np.dot(features, self.discriminator_weights)))

    def _adversarial_attack(self, features: np.ndarray) -> Tuple[float, List[str]]:
        adversary_confidence = self._sigmoid(float(np.dot(features, self.adversary_weights)))
        attack_points = [
            f"Wymiar {i}: anomalna wartość {f:.3f}"
            for i, (f, w) in enumerate(zip(features, self.adversary_weights))
            if abs(f * w) > 0.5
        ]
        return adversary_confidence, attack_points

    def _check_blacklist(self, features: np.ndarray) -> Tuple[bool, float]:
        if not self.blacklist_patterns:
            return False, 0.0
        max_similarity = 0.0
        for pattern in self.blacklist_patterns:
            denom = np.linalg.norm(features) * np.linalg.norm(pattern) + 1e-8
            similarity = float(np.dot(features, pattern) / denom)
            max_similarity = max(max_similarity, similarity)
        return max_similarity > 0.8, max_similarity

    def validate(self, signal: Signal) -> AdversarialResult:
        """Waliduje sygnał przez Lustro Prawdy."""
        features = self._extract_features(signal)
        real_prob = self._discriminate(features)
        adversary_conf, attack_points = self._adversarial_attack(features)
        is_blacklisted, blacklist_similarity = self._check_blacklist(features)

        if is_blacklisted:
            is_valid, verdict = False, "REJECTED"
            final_conf = signal.confidence * (1 - blacklist_similarity)
        elif adversary_conf > 0.7:
            is_valid, verdict = False, "REJECTED"
            final_conf = signal.confidence * 0.1
        elif adversary_conf < 0.3 and real_prob > 0.5:
            is_valid, verdict = True, "PASSED"
            final_conf = min(signal.confidence * (1 + real_prob) / 2, 0.99)
        else:
            is_valid, verdict = True, "NEUTRAL"
            final_conf = signal.confidence * 0.7

        return AdversarialResult(signal, is_valid, adversary_conf, attack_points, final_conf, verdict)

    def train_on_outcome(self, signal: Signal, was_profitable: bool):
        """Uczy Lustro na podstawie wyniku transakcji."""
        features = self._extract_features(signal)
        if was_profitable:
            self.discriminator_weights += self.lr * features * 0.1
        else:
            self.blacklist_patterns.append(features.copy())
            self.adversary_weights += self.lr * features * 0.5
            if len(self.blacklist_patterns) > 1000:
                self.blacklist_patterns = self.blacklist_patterns[-1000:]
        self.training_history.append({
            "timestamp": datetime.now().isoformat(),
            "was_profitable": was_profitable,
            "signal_confidence": signal.confidence,
        })

    def get_statistics(self) -> Dict:
        if not self.training_history:
            return {"status": "No training data"}
        total = len(self.training_history)
        profitable = sum(1 for h in self.training_history if h["was_profitable"])
        return {
            "total_validations": total,
            "profitable_signals": profitable,
            "accuracy": profitable / total if total > 0 else 0,
            "blacklist_size": len(self.blacklist_patterns),
            "version": self.version,
        }


def main():
    logger.info("=== Lustro Prawdy v1.1 Demo (Kingdom Pixel) ===")
    mirror = TruthMirror(learning_rate=0.01, seed=42)
    test_signal = Signal(
        symbol="BTC/USDT", action="BUY", confidence=0.85, source="Klucz Kodowy S1",
        reasons=["RSI=32 (wyprzedanie)", "Delta dodatnia", "Wieloryb akumuluje"],
        features=np.random.default_rng(7).standard_normal(FEATURE_DIM),
    )
    result = mirror.validate(test_signal)
    logger.info(f"Sygnał: {test_signal.action} {test_signal.symbol}")
    logger.info(f"Werdykt: {result.verdict} | Pewność adwersarza (fałsz): {result.adversary_confidence:.2%}")
    logger.info(f"Słabe punkty: {len(result.attack_points)} | Ostateczna pewność: {result.final_confidence:.2%}")
    mirror.train_on_outcome(test_signal, was_profitable=True)
    logger.info(f"Statystyki: {json.dumps(mirror.get_statistics(), ensure_ascii=False)}")
    print("\n✅ Lustro Prawdy v1.1 — demo zakończone.")


if __name__ == "__main__":
    main()
