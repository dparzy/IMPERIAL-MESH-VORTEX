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
    NeuronWilliamsR, NeuronATRDeviation, NeuronHAScalper, NeuronStochRSI,
    NeuronTRIX, NeuronAwesome, NeuronAccelerator, NeuronBBSqueeze,
    NeuronValueConvergence,
    NeuronKonfluencjaMultiTF,
)
from imperium.legiony.neurony.trend import (
    NeuronADX, NeuronIchimoku, NeuronEMA50_200, NeuronSupertrend, NeuronDonchian,
    NeuronHMA, NeuronFibonacci, NeuronRSIDiv, NeuronOBZone,
)
from imperium.legiony.neurony.sesje import NeuronZegarSesji, NeuronAzjaRange, NeuronAugur, NeuronRadarBTC, NeuronDominacja, NeuronPrzeplyw
from imperium.legiony.neurony.wolumen import (
    NeuronOBV, NeuronVWAP, NeuronCVD, NeuronVolumeAnomaly, NeuronRVOL,
    NeuronForceIndex, NeuronDeltaDivergence, NeuronAnchoredVWAP,
)
from imperium.legiony.neurony.struktura import (
    NeuronOrderBlock, NeuronFVG, NeuronBOS, NeuronVSA, NeuronVolumeProfile,
)
from imperium.legiony.neurony.sentyment import NeuronSentymentNews
from imperium.legiony.neurony.psychologia import (
    NeuronFearGreed, NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv,
)
from imperium.legiony.neurony.onchain import (
    NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow, NeuronWashTrading,
)
from imperium.legiony.neurony.straz import (
    NeuronStopHunt, NeuronWickRejection, NeuronWashVol, NeuronBartPattern,
)
from imperium.legiony.neurony.dzwignia import (
    NeuronATRLev, NeuronRealizedVol, NeuronChoppiness, NeuronUlcer,
)
from imperium.legiony.neurony.fraktal import (
    NeuronHurstDFA,
)
from imperium.legiony.neurony.entropia import (
    NeuronPermutationEntropy,
)
from imperium.legiony.neurony.zagrozenie import (
    NeuronToxicFlow, NeuronPumpDetect, NeuronBubbleCrash, NeuronCascade,
    NeuronDetektorRuchu, NeuronAmihudIlliquidity, NeuronPiCycleTop,
)
from imperium.legiony.neurony.geometria import (
    NeuronPathSignature,
)

# ── Zwiadowcy Exploratores ─────────────────────────────────────────────────────
from imperium.legiony.zwiadowcy import (
    ZwiadowcaHiguchiFD, ZwiadowcaHAScalper, ZwiadowcaHurst,
    ZwiadowcaKalmanATR, ZwiadowcaSMC, aktywuj_neurony_smc,
    ZwiadowcaKatana, ZwiadowcaTLP, ZwiadowcaNightTurbo,
    ZwiadowcaLiquiditySweep, ZwiadowcaDisplacement,
    ZwiadowcaDynamic, ZwiadowcaAtmabhan,
)

logger = logging.getLogger("Rejestr")


def wszystkie_neurony() -> List[MikroNeuron]:
    """Tworzy instancje wszystkich zaimplementowanych neuronów."""
    return [
        # Momentum (X)
        NeuronRSI(), NeuronMACD(), NeuronBBands(), NeuronEMACross(),
        NeuronWilliamsR(), NeuronATRDeviation(), NeuronHAScalper(), NeuronStochRSI(),
        NeuronTRIX(), NeuronAwesome(), NeuronAccelerator(), NeuronBBSqueeze(),
        # Value convergence (M) — rewersja do wartości godziwej (X-27, W-273, BIB-020 Harris rozdz. 16)
        NeuronValueConvergence(),
        # Multi-TF Confluence (T) — potwierdzenie kierunku na ≥2 interwałach (X-28, W-321)
        NeuronKonfluencjaMultiTF(),
        # Trend (XII)
        NeuronADX(), NeuronIchimoku(), NeuronEMA50_200(), NeuronSupertrend(), NeuronDonchian(),
        NeuronHMA(), NeuronFibonacci(), NeuronRSIDiv(), NeuronOBZone(),
        # Wolumen (V/F)
        NeuronOBV(), NeuronVWAP(), NeuronCVD(), NeuronVolumeAnomaly(), NeuronRVOL(),
        NeuronForceIndex(),
        # Delta Divergence (F, V-06) + Anchored VWAP (F, V-07) — order-flow/swing OHLCV (W-322)
        NeuronDeltaDivergence(), NeuronAnchoredVWAP(),
        # Zegary rynku (SES — Faza C, W-286)
        NeuronZegarSesji(), NeuronAzjaRange(), NeuronAugur(), NeuronRadarBTC(),
        NeuronDominacja(), NeuronPrzeplyw(),
        # Struktura (SMC/VSA)
        NeuronOrderBlock(), NeuronFVG(), NeuronBOS(), NeuronVSA(),
        # Volume Profile / VPOC (S, VP-01) — S/R z wolumenu, swing OHLCV (W-322, Dalton BIB-013)
        NeuronVolumeProfile(),
        # Psychologia (PSY)
        NeuronFearGreed(), NeuronFundingExtreme(), NeuronPanikaDetal(), NeuronOIDiv(),
        # Sentyment newsów (NEWS) — LLM DeepSeek + fallback słownikowy (W-297)
        NeuronSentymentNews(),
        # On-chain (OC) + Wash Trading (OC-05, OHLCV, bez API)
        NeuronMVRV(), NeuronSOPR(), NeuronPuellMultiple(), NeuronExchangeNetflow(),
        NeuronWashTrading(),
        # Straż / Anty-manipulacja (A)
        NeuronStopHunt(), NeuronWickRejection(), NeuronWashVol(), NeuronBartPattern(),
        # Dźwignia (L) + Zmienność (V) — OHLCV, bez API
        NeuronATRLev(), NeuronRealizedVol(), NeuronChoppiness(), NeuronUlcer(),
        # Fraktal (H) — Hurst-DFA meta-brama reżimu, OHLCV bez API
        NeuronHurstDFA(),
        # Entropia (N) — Permutation Entropy meta-brama chaosu, OHLCV bez API
        NeuronPermutationEntropy(),
        # Zagrożenie (Z) — VPIN meta-brama obronna (Z-01) + PumpDetect kierunkowy (Z-02)
        # + Bubble/Crash kill-switch (Z-03, W-278) + Cascade/Dead-Cat (Z-04, W-279), BIB-020 rozdz. 28
        NeuronToxicFlow(), NeuronPumpDetect(), NeuronBubbleCrash(), NeuronCascade(),
        # + Detektor Ruchu Klimaksowego dwukierunkowy (Z-05, W-315): szczyt→SHORT, dołek→LONG
        NeuronDetektorRuchu(),
        # Amihud Illiquidity (Z-06, meta-brama płynności) + Pi Cycle Top (Z-07, kill-switch szczytu) — W-322
        NeuronAmihudIlliquidity(), NeuronPiCycleTop(),
        # Geometria ścieżki (D) — Lévy Area Close×Volume, Rough Path Theory (W-079)
        NeuronPathSignature(),
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
        ZwiadowcaLiquiditySweep(), # EXP-09 Liquidity Sweep stop-hunt (IMV-ADO)
        ZwiadowcaDisplacement(), # EXP-10 Displacement impuls strukturalny (IMV-ADO)
        ZwiadowcaDynamic(),    # EXP-11 Dynamic cross + slippage guard (IMV-ADO)
        ZwiadowcaAtmabhan(),   # EXP-12 L2 mikrostruktura (IMV-ADO, WYCISZONY do feedu L2)
    ]


def zbuduj_legatusa(min_neuronow: int = 5, min_przewaga: float = 0.55,
                    aktywuj_smc: bool = True, styl: str = None) -> Legatus:
    """
    Składa pełnego Legatusa: wszystkie neurony + zwiadowcy EXP + most SMC.

    aktywuj_smc: gdy True (domyślnie), budzi SMC-01/02/03 — bo ZwiadowcaSMC
                 jest w składzie i będzie wstrzykiwał strefy. Gdy nie podajesz
                 barów do fokus(), zostaw False (inaczej SMC dostaną puste strefy).
    styl: gdy podany (SCALP/SWING/INVEST, W-323) — Legatus dostaje DEDYKOWANY
          zestaw neuronów dla stylu (neurony_dla_trybu), nie pełne 70. None = pełny rój.
    """
    neurony = neurony_dla_trybu(styl) if styl else wszystkie_neurony()
    zwiadowcy = wszyscy_zwiadowcy()
    from imperium.legiony.strategie.rejestr_strategii import wszystkie_strategie
    strategie = wszystkie_strategie()

    if aktywuj_smc:
        obudzone = aktywuj_neurony_smc()
        logger.info(f"[Rejestr] Most SMC aktywny — obudzono neurony: {obudzone}")

    legatus = Legatus(
        neurony=neurony,
        min_neuronow=min_neuronow,
        min_przewaga=min_przewaga,
        zwiadowcy=zwiadowcy,
        strategie=strategie,
    )

    # Raport startowy — co śpi, co czuwa (Prawo XV — jawność potencjału)
    niedostepne = legatus.roj.lista_niedostepnych()
    aktywne = len(neurony) - len(niedostepne)
    logger.info(
        f"[Rejestr] Legatus gotowy: {aktywne}/{len(neurony)} neuronów aktywnych, "
        f"{len(zwiadowcy)} zwiadowców EXP, {len(strategie)} strategii w bazie. "
        f"Wyciszone (wymagają API/feed): {len(niedostepne)}"
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

    zwiadowcy = wszyscy_zwiadowcy()
    zw_aktywni = [z for z in zwiadowcy if getattr(z, "DOSTEPNY", True)]
    zw_wyciszeni = [z for z in zwiadowcy if not getattr(z, "DOSTEPNY", True)]

    powody = {n.KLUCZ: n.POWOD_NIEDOSTEPNOSCI for n in wyciszone}
    powody.update({z.KLUCZ: z.POWOD_NIEDOSTEPNOSCI for z in zw_wyciszeni})

    return {
        "neurony_lacznie": len(neurony),
        "neurony_aktywne": len(aktywne),
        "neurony_wyciszone": len(wyciszone),
        "zwiadowcy_exp": len(zwiadowcy),
        "zwiadowcy_aktywni": len(zw_aktywni),
        "zwiadowcy_wyciszeni": len(zw_wyciszeni),
        "wykorzystanie_pct": round(len(aktywne) / len(neurony) * 100, 1),
        "wyciszone_powody": powody,
    }


def raport_elity() -> dict:
    """
    Prawo XX — diagnostyka statusu elitarnego.
    Zwraca neurony i zwiadowców ze statusem ELITARNY=True + powody.
    """
    neurony = wszystkie_neurony()
    zwiadowcy = wszyscy_zwiadowcy()

    elite_n = [n for n in neurony if getattr(n, "ELITARNY", False)]
    elite_z = [z for z in zwiadowcy if getattr(z, "ELITARNY", True)]

    return {
        "neurony_elite": [{"klucz": n.KLUCZ, "powod": n.POWOD_ELITARNOSCI} for n in elite_n],
        "zwiadowcy_elite": [{"klucz": z.KLUCZ, "powod": z.POWOD_ELITARNOSCI} for z in elite_z],
        "lacznie_elite": len(elite_n) + len(elite_z),
    }


# ── PROFILE STYLU GRY (W-323) — który neuron głosuje w jakim stylu ───────────────
#
# DLA NOWICJUSZA: nie każdy neuron ma sens na każdym interwale. RSI/StochRSI to
# szybkie oscylatory (scalp/swing); MVRV-Z/SOPR to wolne wskaźniki on-chain (tylko
# inwestycja 1D-1W); Pi Cycle to kill-switch szczytu cyklu (potrzebuje ≥350 barów 1D).
# Zamiast zawsze uruchamiać pełne 70 (rozcieńcza sygnał — patrz W-322/W-322b), wybieramy
# DEDYKOWANY ZESTAW per styl. To NIE wycisza neuronu — on dalej żyje w innych profilach.
#
# Prawo I: to HIPOTEZA WSTĘPNA oparta o naturę wskaźnika + sekcja 1 ANALIZA_NEURONY.
#   Docelowo strojona pomiarem A/B (W-323+) — „z czasem żonglujemy neuronami".
# Prawo XXI: KAŻDY z 70 neuronów MUSI tu być (audyt sprawdza brak sierot/braków).
#   Nowy neuron bez wpisu = błąd spójności (nie wpada cicho do „uniwersalnych").
#
# Style: "SCALP" (M1-1h, szybkie momentum/mikrostruktura), "SWING" (4h-1D, trend/struktura),
#        "INVEST" (1D-1W, makro/cykl/on-chain).

STYL_SCALP = "SCALP"
STYL_SWING = "SWING"
STYL_INVEST = "INVEST"
WSZYSTKIE_STYLE: tuple = (STYL_SCALP, STYL_SWING, STYL_INVEST)

# Uniwersalny = bezpieczniki/reżim/sentyment działające na każdym interwale.
_U = WSZYSTKIE_STYLE
_SC_SW = (STYL_SCALP, STYL_SWING)
_SW_IN = (STYL_SWING, STYL_INVEST)

NEURONY_STYLU: dict = {
    # Momentum (M) — oscylatory: szybkie sygnały scalp+swing; AC i HA czysto scalp
    "X-01": _SC_SW, "X-02": _SC_SW, "X-03": _SC_SW, "X-04": _SC_SW,
    "X-06": _SC_SW, "X-08": _SC_SW, "X-09": (STYL_SCALP,), "X-12": _SC_SW,
    "X-17": _SC_SW, "X-25": _SC_SW, "X-26": (STYL_SCALP,),
    "X-27": _SW_IN,                       # Value-Z: rewersja do wartości godziwej (swing/invest)
    # Trend (T) — wolniejsze: swing/invest; MTF czysto swing; HA-szybkie EMA/HMA scalp+swing
    "X-05": _SC_SW, "X-10": _SC_SW, "X-18": _SW_IN, "X-28": (STYL_SWING,),
    "XII-01": _SW_IN, "XII-02": _SW_IN, "XII-03": _SW_IN, "XII-04": _SW_IN,
    "XII-05": (STYL_SWING,), "XII-06": (STYL_SWING,), "XII-07": (STYL_SWING,),
    # Wolumen/Flow (F) — CVD czysto scalp; OBV swing/invest; reszta scalp+swing lub swing
    "V-01": _SW_IN, "V-02": _SC_SW, "V-03": (STYL_SCALP,), "V-04": _SC_SW,
    "V-05": (STYL_SWING,), "V-06": _SC_SW, "V-07": (STYL_SWING,),
    "VSA-01": (STYL_SWING,), "X-11": _SC_SW,
    # Struktura/SMC (S) — sesje scalp; FVG scalp+swing; OB/BOS/VPOC swing
    "SES-01": (STYL_SCALP,), "SES-02": (STYL_SCALP,),
    "SMC-01": (STYL_SWING,), "SMC-02": _SC_SW, "SMC-03": (STYL_SWING,),
    "VP-01": (STYL_SWING,),
    # On-chain (O) — wolne fundamenty: tylko inwestycja
    "OC-01": (STYL_INVEST,), "OC-02": (STYL_INVEST,), "OC-03": (STYL_INVEST,),
    "OC-04": (STYL_INVEST,), "OC-05": (STYL_INVEST,),
    # Reżim/Sentyment (R) — futures-sentyment scalp+swing; Fear&Greed/RADAR swing+invest
    "PSY-01": _SC_SW, "PSY-02": _SC_SW, "PSY-04": _SC_SW, "PSY-03": _SW_IN,
    "RADAR-01": _SW_IN, "RADAR-02": _SW_IN, "RADAR-03": _SW_IN,
    "AUG-01": _U, "NEWS-01": _U,
    # Meta-bramy reżimu/chaosu (H/N/V/D/L) — uniwersalne (klasyfikują każdy interwał)
    "H-01": _SW_IN, "N-01": _U, "V-13": _U, "V-14": _U, "D-01": _U,
    "L-14": _U, "VI-13": _U,
    # Anty-manipulacja (A) — uniwersalna obrona
    "A-01": _U, "A-02": _U, "A-03": _U, "A-05": _U,
    # Zagrożenie (Z) — bezpieczniki uniwersalne; Bubble swing+invest; Pi Cycle czysto invest
    "Z-01": _U, "Z-02": _U, "Z-03": _SW_IN, "Z-04": _U, "Z-05": _U,
    "Z-06": _SC_SW, "Z-07": (STYL_INVEST,),
}


def neurony_dla_trybu(styl: str) -> List[MikroNeuron]:
    """
    W-323 — zwraca DEDYKOWANY zestaw neuronów dla stylu gry (SCALP/SWING/INVEST).

    Filtruje pełny rój wg NEURONY_STYLU — neuron głosuje tylko gdy `styl` jest w jego
    profilu. Bezpieczniki/reżim (uniwersalne) trafiają do każdego zestawu.
    Prawo XV: to nie wyciszenie — neuron żyje w swoich docelowych stylach.
    """
    styl = styl.upper()
    if styl not in WSZYSTKIE_STYLE:
        raise ValueError(f"Nieznany styl: {styl!r}. Dozwolone: {WSZYSTKIE_STYLE}")
    return [n for n in wszystkie_neurony()
            if styl in NEURONY_STYLU.get(n.KLUCZ, WSZYSTKIE_STYLE)]


def raport_profili() -> dict:
    """W-323 — ile neuronów gra w każdym stylu + sieroty/braki vs kod (Prawo XXI)."""
    klucze_kodu = {n.KLUCZ for n in wszystkie_neurony()}
    klucze_mapy = set(NEURONY_STYLU)
    return {
        "scalp": len(neurony_dla_trybu(STYL_SCALP)),
        "swing": len(neurony_dla_trybu(STYL_SWING)),
        "invest": len(neurony_dla_trybu(STYL_INVEST)),
        "sieroty_w_mapie": sorted(klucze_mapy - klucze_kodu),   # klucz w mapie, brak w kodzie
        "braki_w_mapie": sorted(klucze_kodu - klucze_mapy),      # neuron w kodzie, brak w mapie
    }
