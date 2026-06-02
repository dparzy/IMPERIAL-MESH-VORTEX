"""
🧪 Adaptery TESTOWE (mock) — dane syntetyczne dla 3 domen API, działają offline.

CEL (Prawo XIX: kod+testy zanim coś "istnieje"):
  Pozwalają zweryfikować CAŁY mechanizm wybudzania end-to-end BEZ prawdziwego API,
  bez kluczy, bez sieci. Gdy podepniemy realne API, podmieniamy tylko `pobierz()`
  na wersję uderzającą w MEXC/Glassnode — interfejs i reszta pipeline bez zmian.

SCENARIUSZE:
  Każdy adapter przyjmuje `scenariusz` sterujący wartościami, by w testach
  wymusić konkretny kierunek głosu neuronu (np. "kapitulacja" → OC-01 LONG).
  Dane są deterministyczne (te same wejścia → te same wyjścia, Prawo I).

DOMENY (pokrywają 9 wyciszonych neuronów wymagających API):
  OnChain  → OC-01..04  (Glassnode/CryptoQuant)
  Futures  → PSY-01..04 (MEXC futures + sentyment)
  CVD      → V-03       (trade feed buy/sell z MEXC)
"""

from imperium.akwedukty.adaptery.baza import AdapterDanych

from imperium.legiony.neurony.onchain import (
    NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
)
from imperium.legiony.neurony.psychologia import (
    NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed, NeuronOIDiv,
)
from imperium.legiony.neurony.wolumen import NeuronCVD


class AdapterTestowyOnChain(AdapterDanych):
    """
    Mock on-chain (OC-01..04). Scenariusze:
      "kapitulacja" — dno cyklu (MVRV-Z niski, SOPR<1, Puell niski, netflow ujemny→LONG)
      "euforia"     — szczyt bańki (MVRV-Z wysoki, SOPR>1, Puell wysoki, netflow dodatni→SHORT)
      "neutralny"   — środek cyklu
    """
    NAZWA = "OnChain(mock)"
    KLUCZE = ["MVRV_Z_SCORE", "SOPR", "SOPR_PREV", "PUELL_MULTIPLE",
              "EXCHANGE_NETFLOW_BTC", "EXCHANGE_NETFLOW_MA7"]
    _NEURONY = (NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow)
    _POWOD_USPIENIA = "Wymaga on-chain API (Glassnode/CryptoQuant). Podepnij adapter w pobierz_wskazniki()."

    def __init__(self, scenariusz: str = "kapitulacja"):
        self.scenariusz = scenariusz

    def pobierz(self, symbol: str) -> dict:
        if self.scenariusz == "kapitulacja":
            return {
                "MVRV_Z_SCORE": -0.8,         # < -0.5 → LONG (kapitulacja)
                "SOPR": 0.96, "SOPR_PREV": 0.94,  # < 1 → straty realizowane
                "PUELL_MULTIPLE": 0.4,        # niski → dno górników
                "EXCHANGE_NETFLOW_BTC": -5000,    # odpływ z giełd → akumulacja
                "EXCHANGE_NETFLOW_MA7": -3000,
            }
        if self.scenariusz == "euforia":
            return {
                "MVRV_Z_SCORE": 6.5,          # > 6 → szczyt bańki → SHORT
                "SOPR": 1.08, "SOPR_PREV": 1.10,
                "PUELL_MULTIPLE": 4.5,        # wysoki → euforia górników
                "EXCHANGE_NETFLOW_BTC": 8000,     # napływ na giełdy → dystrybucja
                "EXCHANGE_NETFLOW_MA7": 6000,
            }
        return {  # neutralny
            "MVRV_Z_SCORE": 2.0, "SOPR": 1.0, "SOPR_PREV": 1.0,
            "PUELL_MULTIPLE": 1.5,
            "EXCHANGE_NETFLOW_BTC": 100, "EXCHANGE_NETFLOW_MA7": 120,
        }


class AdapterTestowyFutures(AdapterDanych):
    """
    Mock futures + sentyment (PSY-01..04). Scenariusze:
      "panika"   — strach ekstremalny (Fear&Greed niski, funding ujemny → kontrariańsko LONG)
      "chciwosc" — euforia (Fear&Greed wysoki, funding dodatni, L/S wysoki → SHORT)
      "neutralny"
    Uwaga: PSY-04 (OIDiv) czyta też CLOSE/CLOSE_PREV — te dostarcza Budowniczy z barów.
    """
    NAZWA = "Futures(mock)"
    KLUCZE = ["FUNDING_RATE", "LONG_SHORT_RATIO", "FEAR_GREED_INDEX",
              "OPEN_INTEREST", "OPEN_INTEREST_PREV"]
    _NEURONY = (NeuronFundingExtreme, NeuronPanikaDetal, NeuronFearGreed, NeuronOIDiv)
    _POWOD_USPIENIA = "Wymaga API futures (MEXC) / sentymentu. Ustaw MEXC_API_KEY i podepnij adapter."

    def __init__(self, scenariusz: str = "panika"):
        self.scenariusz = scenariusz

    def pobierz(self, symbol: str) -> dict:
        if self.scenariusz == "panika":
            return {
                "FUNDING_RATE": -0.0012,      # <= FUNDING_LOW*2 → crowded short → LONG
                "LONG_SHORT_RATIO": 0.20,     # short_pct=80% (tłum w panice) → LONG
                "FEAR_GREED_INDEX": 12,       # ekstremalny strach → contrarian LONG
                "OPEN_INTEREST": 1_200_000, "OPEN_INTEREST_PREV": 1_500_000,  # OI spada
            }
        if self.scenariusz == "chciwosc":
            return {
                "FUNDING_RATE": 0.0015,       # >= FUNDING_HIGH → crowded long → SHORT
                "LONG_SHORT_RATIO": 0.85,     # long_pct=85% (euforia) → SHORT
                "FEAR_GREED_INDEX": 88,       # ekstremalna chciwość → contrarian SHORT
                "OPEN_INTEREST": 1_800_000, "OPEN_INTEREST_PREV": 1_500_000,
            }
        return {  # neutralny
            "FUNDING_RATE": 0.0001, "LONG_SHORT_RATIO": 1.0,
            "FEAR_GREED_INDEX": 50,
            "OPEN_INTEREST": 1_500_000, "OPEN_INTEREST_PREV": 1_500_000,
        }


class AdapterTestowyCVD(AdapterDanych):
    """
    Mock CVD (V-03) — Cumulative Volume Delta z trade feedu (buy vs sell aggressor).
    Scenariusze:
      "akumulacja"  — CVD rośnie (przewaga kupujących agresorów) → LONG
      "dystrybucja" — CVD spada (przewaga sprzedających) → SHORT
      "neutralny"
    """
    NAZWA = "CVD(mock)"
    KLUCZE = ["CVD", "CVD_PREV"]
    _NEURONY = (NeuronCVD,)
    _POWOD_USPIENIA = ("CVD wymaga danych o stronie agresora (buy/sell volume z tick/trade feed). "
                       "OHLCV tego nie zawiera. Aktywuje się przy podpięciu trade feed z MEXC.")

    def __init__(self, scenariusz: str = "akumulacja"):
        self.scenariusz = scenariusz

    def pobierz(self, symbol: str) -> dict:
        if self.scenariusz == "akumulacja":
            return {"CVD": 15000.0, "CVD_PREV": 9000.0}   # dodatni → kupujący dominują → LONG
        if self.scenariusz == "dystrybucja":
            return {"CVD": -4000.0, "CVD_PREV": 2000.0}   # ujemny → sprzedający dominują → SHORT
        return {"CVD": 0.0, "CVD_PREV": 0.0}              # neutralny
