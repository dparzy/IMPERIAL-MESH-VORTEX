"""
╔══════════════════════════════════════════════════════════════════╗
║  N-NEURON-001 — RÓJ SYGNAŁÓW (Signal Swarm)                        ║
║  IMPERIUM — adaptacja z Kingdom Pixel (Jack)                               ║
╠══════════════════════════════════════════════════════════════════╣
║  CO TO: wiele "neuronów-sygnałów" głosuje ważoną wagą; wejście    ║
║  tylko przy KONSENSUSIE. Realizacja wizji Komendanta "rój neuronów"║
║  + filtr reżimu (technika trend-following funduszy 2026).         ║
║                                                                    ║
║  NEURONY (close-only, liczone przez Bramę — Prawo I):           ║
║   N1 Trend     — cena > EMA(fast)                                 ║
║   N2 Momentum  — RSI w zdrowym pasmie (low..high)                 ║
║   N3 Reżim     — cena > EMA(long) ORAZ EMA(long) ROŚNIE           ║
║                  (bot nie wchodzi w bessę/boczniak — koniec       ║
║                   whipsawu, który zabił nas na 1H)                ║
║                                                                    ║
║  Filozofia (quant 2026): nie "który sygnał ma rację", tylko       ║
║  "jak bardzo ufać każdemu teraz" → wagi + próg konsensusu.        ║
║  Rozszerzalny: dokładasz kolejne neurony = rośnie rój.            ║
║                                                                    ║
║  CHANGELOG:                                                        ║
║   v1.0 (2026-05-30) — 3 neurony, ważony głos, neuron reżimu.      ║
╚══════════════════════════════════════════════════════════════════╝
"""
from dataclasses import dataclass, field
from typing import Dict, Tuple
import numpy as np


@dataclass
class RojSygnalow:
    rsi_low: float = 50.0
    rsi_high: float = 70.0
    regime_period: int = 200        # długa EMA = "duży trend" (reżim)
    slope_lookback: int = 20        # przez ile świec mierzymy nachylenie długiej EMA
    # wagi neuronów: (trend, momentum, reżim). Reżim cięższy — to on chroni.
    weights: Tuple[float, float, float] = (1.0, 1.0, 1.5)
    threshold: float = 2.5          # min. suma głosów "za", by wejść (z 3.5 max)

    def votes(self, price: float, ema_fast: float, rsi: float,
              ema_long: float, ema_long_prev: float) -> Tuple[float, Dict[str, bool]]:
        """Zwraca (wynik_ważony, słownik_neuronów). NaN → neuron milczy (False)."""
        n1 = (not np.isnan(ema_fast)) and price > ema_fast
        n2 = (not np.isnan(rsi)) and (self.rsi_low < rsi < self.rsi_high)
        n3 = ((not np.isnan(ema_long)) and (not np.isnan(ema_long_prev))
              and price > ema_long and ema_long > ema_long_prev)
        w_t, w_m, w_r = self.weights
        score = n1 * w_t + n2 * w_m + n3 * w_r
        return score, {"trend": n1, "momentum": n2, "rezim": n3}

    def entry_ok(self, price: float, ema_fast: float, rsi: float,
                 ema_long: float, ema_long_prev: float) -> bool:
        """Czy rój zgadza się na wejście (konsensus >= próg)?"""
        score, _ = self.votes(price, ema_fast, rsi, ema_long, ema_long_prev)
        return score >= self.threshold

    @property
    def max_score(self) -> float:
        return float(sum(self.weights))


# ── Demo (uruchom: python NEURON-001_RojSygnalow.py) ──
if __name__ == "__main__":
    roj = RojSygnalow()
    print(f"Rój: {len(roj.weights)} neurony | max głos {roj.max_score} | próg {roj.threshold}")
    # przykład: trend+momentum, ale reżim spadkowy (długa EMA opada) → BLOKADA
    s, n = roj.votes(price=100, ema_fast=95, rsi=60, ema_long=105, ema_long_prev=110)
    print(f"  Trend+momentum, ale reżim w dół: głos={s} → wejście={roj.entry_ok(100,95,60,105,110)} | {n}")
    # przykład: wszystko za (reżim w górę) → WEJŚCIE
    s2, n2 = roj.votes(price=100, ema_fast=95, rsi=60, ema_long=90, ema_long_prev=85)
    print(f"  Wszystko za (reżim w górę):   głos={s2} → wejście={roj.entry_ok(100,95,60,90,85)} | {n2}")
