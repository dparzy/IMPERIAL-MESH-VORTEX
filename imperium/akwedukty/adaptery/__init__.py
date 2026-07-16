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
from imperium.akwedukty.adaptery.futures import AdapterFutures
from imperium.akwedukty.adaptery.mexc_futures import AdapterMEXCFutures
from imperium.akwedukty.adaptery.cvd import AdapterCVD
from imperium.akwedukty.adaptery.news_llm import AdapterNewsLLM
from imperium.akwedukty.adaptery.dvol import AdapterDVOL
from imperium.akwedukty.adaptery.stablecoin import AdapterStablecoin
from imperium.akwedukty.adaptery.usd_sila import AdapterUSD

__all__ = [
    "AdapterDanych",
    "AdapterTestowyOnChain",
    "AdapterTestowyFutures",
    "AdapterTestowyCVD",
    "AdapterFearGreed",
    "AdapterFutures",
    "AdapterMEXCFutures",
    "AdapterCVD",
    "AdapterNewsLLM",
    "AdapterDVOL",
    "AdapterStablecoin",
    "AdapterUSD",
]
