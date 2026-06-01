"""
📒 Rejestr Legionu — fabryka pełnego Legatusa z wszystkimi neuronami i zwiadowcami.

ROLA (Prawo XV — potencjał wykorzystany w 100%):
  Jedno miejsce, które:
    1. zbiera WSZYSTKIE zaimplementowane neurony (dostępne i wyciszone)
    2. zbiera WSZYSTKICH zwiadowców Exploratores (EXP-01..05)
    3. aktywuje most SMC (ZwiadowcaSMC budzi SMC-01/02/03)
    4. składa gotowego Legatusa, który faktycznie głosuje pełnym składem

  Bez tego rejestru każda sesja musiałaby ręcznie importować 27 neuronów —
  łatwo o zapomnienie = utrata potencjału. Tu wszystko jest spięte raz.

Użycie:
    from imperium.legiony.rejestr import zbuduj_legatusa
    legatus = zbuduj_legatusa()
    raport = legatus.fokus("BTCUSDT", wskazniki, rezim="TREND_STRONG", bary=bary)
"""

import logging
from typing import List

from imperium.legiony.mikro_neuron import MikroNeuron
from imperium.legiony.legatus import Legatus

# ── Neurony ────────────────────────────────────────────────────────────────────
from imperium.legiony.neurony.momentum import (
    NeuronRSI, NeuronMACD, NeuronBBands, NeuronEMACross,
    NeuronWilliamsR, NeuronATRDeviation, NeuronHAScalper,
)
from imperium.legiony.neurony.trend import (
    NeuronADX, NeuronIchimoku, NeuronEMA50_200, NeuronSupertrend,
)
from imperium.legiony.neurony.wolumen import (
    NeuronOBV, NeuronVWAP, NeuronCVD, NeuronVolumeAnomaly,
)
from imperium.legiony.neurony.struktura import (
    NeuronOrderBlock, NeuronFVG, NeuronBOS, NeuronVSA,
)
from imperium.legiony.neurony.psychologia import (
    NeuronFearGreed, NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv,
)
from imperium.legiony.neurony.onchain import (
    NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow,
)

# ── Zwiadowcy Exploratores ─────────────────────────────────────────────────────
from imperium.legiony.zwiadowcy import (
    ZwiadowcaHiguchiFD, ZwiadowcaHAScalper, ZwiadowcaHurst,
    ZwiadowcaKalmanATR, ZwiadowcaSMC, aktywuj_neurony_smc,
    ZwiadowcaKatana, ZwiadowcaTLP, ZwiadowcaNightTurbo,
)

logger = logging.getLogger("Rejestr")


def wszystkie_neurony() -> List[MikroNeuron]:
    """Tworzy instancje wszystkich zaimplementowanych neuronów."""
    return [
        # Momentum (X)
        NeuronRSI(), NeuronMACD(), NeuronBBands(), NeuronEMACross(),
        NeuronWilliamsR(), NeuronATRDeviation(), NeuronHAScalper(),
        # Trend (XII)
        NeuronADX(), NeuronIchimoku(), NeuronEMA50_200(), NeuronSupertrend(),
        # Wolumen (V)
        NeuronOBV(), NeuronVWAP(), NeuronCVD(), NeuronVolumeAnomaly(),
        # Struktura (SMC/VSA)
        NeuronOrderBlock(), NeuronFVG(), NeuronBOS(), NeuronVSA(),
        # Psychologia (PSY)
        NeuronFearGreed(), NeuronFundingExtreme(), NeuronPanikaDetal(), NeuronOIDiv(),
        # On-chain (OC)
        NeuronMVRV(), NeuronSOPR(), NeuronPuellMultiple(), NeuronExchangeNetflow(),
    ]


def wszyscy_zwiadowcy() -> list:
    """Tworzy instancje wszystkich zwiadowców Exploratores."""
    return [
        ZwiadowcaSMC(),        # PIERWSZY — wstrzykuje strefy (most do SMC)
        ZwiadowcaHiguchiFD(),  # EXP-01 reżim
        ZwiadowcaHAScalper(),  # EXP-02 HA full
        ZwiadowcaHurst(),      # EXP-03 persystencja
        ZwiadowcaKalmanATR(),  # EXP-04 zmienność
        ZwiadowcaKatana(),     # EXP-06 Katana Scalper Pro (IMV-ADO)
        ZwiadowcaTLP(),        # EXP-07 A-TLP Scalper breakout (IMV-ADO)
        ZwiadowcaNightTurbo(), # EXP-08 Night Turbo fade-scalper (IMV-ADO)
    ]


def zbuduj_legatusa(min_neuronow: int = 5, min_przewaga: float = 0.55,
                    aktywuj_smc: bool = True) -> Legatus:
    """
    Składa pełnego Legatusa: wszystkie neurony + zwiadowcy EXP + most SMC.

    aktywuj_smc: gdy True (domyślnie), budzi SMC-01/02/03 — bo ZwiadowcaSMC
                 jest w składzie i będzie wstrzykiwał strefy. Gdy nie podajesz
                 barów do fokus(), zostaw False (inaczej SMC dostaną puste strefy).
    """
    neurony = wszystkie_neurony()
    zwiadowcy = wszyscy_zwiadowcy()

    if aktywuj_smc:
        obudzone = aktywuj_neurony_smc()
        logger.info(f"[Rejestr] Most SMC aktywny — obudzono neurony: {obudzone}")

    legatus = Legatus(
        neurony=neurony,
        min_neuronow=min_neuronow,
        min_przewaga=min_przewaga,
        zwiadowcy=zwiadowcy,
    )

    # Raport startowy — co śpi, co czuwa (Prawo XV — jawność potencjału)
    niedostepne = legatus.roj.lista_niedostepnych()
    aktywne = len(neurony) - len(niedostepne)
    logger.info(
        f"[Rejestr] Legatus gotowy: {aktywne}/{len(neurony)} neuronów aktywnych, "
        f"{len(zwiadowcy)} zwiadowców EXP. Wyciszone (wymagają API/feed): {len(niedostepne)}"
    )
    return legatus


def raport_potencjalu() -> dict:
    """
    Prawo XV — diagnostyka wykorzystania potencjału.
    Zwraca ile neuronów aktywnych, ile wyciszonych i dlaczego.
    """
    neurony = wszystkie_neurony()
    aktywne = [n for n in neurony if n.DOSTEPNY]
    wyciszone = [n for n in neurony if not n.DOSTEPNY]
    return {
        "neurony_lacznie": len(neurony),
        "neurony_aktywne": len(aktywne),
        "neurony_wyciszone": len(wyciszone),
        "zwiadowcy_exp": len(wszyscy_zwiadowcy()),
        "wykorzystanie_pct": round(len(aktywne) / len(neurony) * 100, 1),
        "wyciszone_powody": {n.KLUCZ: n.POWOD_NIEDOSTEPNOSCI for n in wyciszone},
    }
