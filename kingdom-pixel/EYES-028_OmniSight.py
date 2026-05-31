"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        OmniSight — Bayesian Fusion On-Chain + OrderBook v2.0                ║
║  Autor: Jack (Wizjoner, Architekt, Wynalazca, Magik)                        ║
║  Licencja: Kingdom Pixel — wszelkie prawa autorskie                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA (Zasada 11) ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-EYES-028                                                    |
| Nazwa oryginalna    | OmniSight — Bayesian Fusion On-Chain + OrderBook             |
| Nazwa w Królestwie  | OmniSight (Wszechoko)                                         |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/EYES-028_OmniSight.py                |
| Kategoria           | EYES / Percepcja, detekcja manipulacji                       |
| Wpływ na Królestwo  | Warstwa percepcji rynku; po naprawie poprawnie wykrywa       |
|                     | manipulację (znormalizowany posterior Bayesa).               |
| Powiązane moduły    | N-BRAIN-026, N-SHIELDS-205, N-CORE-005                       |

CHANGELOG:
  v2.0 (2026-05-28) — BUGFIX (Zasada 2 — Prawda). Stary kod liczył
        `posterior = P(E|M)·P(M)` BEZ normalizacji przez dowód. Z priorem 0.05
        posterior był zawsze ≤ ~0.045 → próg 0.5 nieosiągalny → manipulacja
        PRAKTYCZNIE NIGDY niewykrywana. Wprowadzono pełny wzór Bayesa z
        prawdopodobieństwem dowodu (likelihood także pod hipotezą "CLEAN").
  v1.0 — wersja wyjściowa (błędny posterior).

Mechanizm:
1. FUZJA BAYESOWSKA — P(Manip | OnChain, OrderBook) z poprawną normalizacją.
2. DETEKCJA MANIPULACJI — porównanie hipotez Manip vs Clean.
3. WHALE ALERT — wykrywanie ruchów wielorybów w czasie rzeczywistym.
═════════════════════════════════════════════════════════════════════════════════════
"""

import logging
from typing import Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("OmniSight")


@dataclass
class OnChainSignal:
    large_transfer: bool; whale_active: bool; exchange_inflow: float


@dataclass
class OrderBookSignal:
    bid_wall: float; ask_wall: float; cvd_delta: float; spread_pct: float


@dataclass
class FusionResult:
    manipulation_probability: float; signal: str; confidence: float


class BayesianFusionEngine:
    def __init__(self, prior_manipulation: float = 0.05):
        # P(Manipulacja) — bazowe prawdopodobieństwo a priori.
        self.p_manipulation = prior_manipulation

    @staticmethod
    def _clamp(x: float, lo: float = 0.05, hi: float = 0.95) -> float:
        return min(hi, max(lo, x))

    def likelihood_onchain_given_manipulation(self, onchain: OnChainSignal) -> float:
        score = 0.0
        if onchain.large_transfer: score += 0.3
        if onchain.whale_active: score += 0.3
        score += min(0.4, onchain.exchange_inflow * 0.1)
        return self._clamp(score)

    def likelihood_orderbook_given_manipulation(self, ob: OrderBookSignal) -> float:
        score = 0.0
        if ob.spread_pct > 0.5: score += 0.3
        if abs(ob.cvd_delta) > 100: score += 0.4
        if ob.ask_wall > ob.bid_wall * 2: score += 0.2
        return self._clamp(score)

    def fuse(self, onchain: OnChainSignal, orderbook: OrderBookSignal) -> FusionResult:
        # Likelihoody pod hipotezą MANIPULACJA
        lm_oc = self.likelihood_onchain_given_manipulation(onchain)
        lm_ob = self.likelihood_orderbook_given_manipulation(orderbook)
        # Likelihoody pod hipotezą CLEAN (model komplementarny, też w [0.05, 0.95])
        lc_oc = self._clamp(1.0 - lm_oc)
        lc_ob = self._clamp(1.0 - lm_ob)

        # Założenie warunkowej niezależności sygnałów:
        # P(E|M) = P(OnChain|M)·P(OB|M),  P(E|¬M) = P(OnChain|¬M)·P(OB|¬M)
        evidence_manip = lm_oc * lm_ob * self.p_manipulation
        evidence_clean = lc_oc * lc_ob * (1.0 - self.p_manipulation)

        # Pełny wzór Bayesa z NORMALIZACJĄ przez całkowite prawdopodobieństwo dowodu:
        # P(M|E) = P(E|M)P(M) / [P(E|M)P(M) + P(E|¬M)P(¬M)]
        posterior = evidence_manip / (evidence_manip + evidence_clean + 1e-12)

        if posterior > 0.5:
            signal = "MANIPULATION_DETECTED"
        elif posterior > 0.2:
            signal = "SUSPICIOUS"
        else:
            signal = "CLEAN"

        logger.info(f"[OmniSight] P(Manipulacja) = {posterior:.3f} → {signal}")
        return FusionResult(manipulation_probability=posterior, signal=signal, confidence=posterior)


class WhaleDetector:
    def __init__(self, threshold_usd: float = 1_000_000):
        self.threshold = threshold_usd; self.whale_alert_count = 0

    def scan_transaction(self, amount_usd: float, from_exchange: bool) -> Optional[str]:
        if amount_usd >= self.threshold:
            self.whale_alert_count += 1
            direction = "INFLOW" if from_exchange else "OUTFLOW"
            alert = f"🐋 WHALE ALERT: ${amount_usd:,.0f} {direction}"
            logger.warning(alert)
            return alert
        return None


def main():
    logger.info("=== OmniSight v2.0 Demo (poprawny Bayes) ===")
    fusion = BayesianFusionEngine()
    whale = WhaleDetector()

    onchain = OnChainSignal(large_transfer=True, whale_active=True, exchange_inflow=5.0)
    ob = OrderBookSignal(bid_wall=10.0, ask_wall=50.0, cvd_delta=200.0, spread_pct=0.8)

    result = fusion.fuse(onchain, ob)
    logger.info(f"Wynik fuzji: {result.signal} (P={result.manipulation_probability:.3f})")

    # Kontrola: czysty rynek powinien dać CLEAN
    clean_oc = OnChainSignal(large_transfer=False, whale_active=False, exchange_inflow=0.0)
    clean_ob = OrderBookSignal(bid_wall=20.0, ask_wall=20.0, cvd_delta=5.0, spread_pct=0.05)
    clean_res = fusion.fuse(clean_oc, clean_ob)
    logger.info(f"Kontrola (czysty rynek): {clean_res.signal} (P={clean_res.manipulation_probability:.3f})")

    whale.scan_transaction(2_500_000, False)
    print("\n✅ OmniSight v2.0 — demo zakończone (posterior Bayesa naprawiony).")


if __name__ == "__main__":
    main()
