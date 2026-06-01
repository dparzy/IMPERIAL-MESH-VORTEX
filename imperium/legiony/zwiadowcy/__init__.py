"""
🏛️ IMV-ORI | Dywizja Zwiadowców Elitarnych — Legio EXPLORATORES

Elitarna dywizja z rozszerzonymi uprawnieniami i własną skalą oceniania.

Różnice od zwykłych MikroNeuronów:
  - Mogą liczyć wskaźniki samodzielnie (Prawo I nie obowiązuje)
  - Przyjmują surowe dane OHLCV (List[BarData]), nie dict z Bramy
  - Własna skala Igrzysk: próg AQUILIFER = 0.88 (trudniej), ale waga max ×2.5
  - Sygnały oznaczone LEGION="EXPLORATORES" — Legatus może ważyć inaczej
  - Minimalna liczba barów wejściowych: WYMAGA_BAROW (zwykle 20-200)
"""

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych
from .igrzyska_exploratores import IgrzyskaExploratores, RangaExploratores
from .exp_higuchi import ZwiadowcaHiguchiFD
from .exp_ha_scalper import ZwiadowcaHAScalper
from .exp_hurst import ZwiadowcaHurst
from .exp_kalman import ZwiadowcaKalmanATR
from .exp_smc import ZwiadowcaSMC, aktywuj_neurony_smc
from .exp_katana import ZwiadowcaKatana
from .exp_tlp import ZwiadowcaTLP

__all__ = [
    "ZwiadowcaElitarny", "RaportZwiadowcy", "TypDanych",
    "IgrzyskaExploratores", "RangaExploratores",
    "ZwiadowcaHiguchiFD", "ZwiadowcaHAScalper",
    "ZwiadowcaHurst", "ZwiadowcaKalmanATR",
    "ZwiadowcaSMC", "aktywuj_neurony_smc",
    "ZwiadowcaKatana", "ZwiadowcaTLP",
]
