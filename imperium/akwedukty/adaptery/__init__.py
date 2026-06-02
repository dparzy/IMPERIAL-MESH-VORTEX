"""
🔌 Adaptery Danych — most między zewnętrznym API a rojem neuronów.

Eksport publiczny: baza + adaptery testowe (mock) dla trzech domen danych,
które dziś trzymają 9 neuronów wyciszonych (Prawo XV: zero martwych głosów).
"""

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.akwedukty.adaptery.testowy import (
    AdapterTestowyOnChain,
    AdapterTestowyFutures,
    AdapterTestowyCVD,
)
from imperium.akwedukty.adaptery.feargreed import AdapterFearGreed

__all__ = [
    "AdapterDanych",
    "AdapterTestowyOnChain",
    "AdapterTestowyFutures",
    "AdapterTestowyCVD",
    "AdapterFearGreed",
]
