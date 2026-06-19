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
from imperium.legiony.neurony.sesje import NeuronZegarSesji, NeuronAzjaRange, NeuronAugur, NeuronRadarBTC, NeuronDominacja, NeuronPrzeplyw, NeuronStresKorelacji, NeuronLeadBTC
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
    NeuronPermutationEntropy, NeuronFracDiff,
)
from imperium.legiony.neurony.zagrozenie import (
    NeuronToxicFlow, NeuronPumpDetect, NeuronBubbleCrash, NeuronCascade,
    NeuronDetektorRuchu, NeuronAmihudIlliquidity, NeuronPiCycleTop,
)
from imperium.legiony.neurony.geometria import (
    NeuronPathSignature,
)
from imperium.legiony.neurony.przekroj import (
    NeuronRelativeStrength,
)
from imperium.legiony.neurony.rezim_zmiana import (
    NeuronChangePoint, NeuronBOCPD,
)
from imperium.legiony.neurony.makro import (
    NeuronDXYTrend, NeuronGoldBTC,
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


# ── MECHANIZM przewagi (Prawo XXII — prawdziwa dekorelacja sygnałów) ────────────
# Jedno źródło prawdy: każdy KLUCZ → typ przewagi (nie dane wejściowe).
# Wartości: trend / mean_rev / breakout / event / regime / stat_arb / risk_filter / vol_signal
# Dwa neurony o tym samym MECHANIZM w tej samej KATEGORIA = kandydat do scalenia (Prawo XVI+XXII).
MECHANIZMY: dict = {
    # Momentum (M/T) — oscylatory vs podążanie
    "X-01": "mean_rev",   # RSI oversold/overbought
    "X-02": "mean_rev",   # StochRSI
    "X-03": "trend",      # MACD
    "X-04": "mean_rev",   # Bollinger Bands (powrót do środka)
    "X-05": "trend",      # EMA cross
    "X-06": "trend",      # Williams %R momentum
    "X-08": "trend",      # TRIX
    "X-09": "trend",      # Awesome Oscillator
    "X-10": "trend",      # (T)
    "X-11": "trend",      # (F-momentum wolumenowe)
    "X-12": "breakout",   # BB Squeeze (ekspansja zmienności)
    "X-17": "trend",      # Accelerator
    "X-18": "trend",      # (T)
    "X-25": "vol_signal", # ATR-Deviation
    "X-26": "trend",      # HA-Scalper
    "X-27": "mean_rev",   # Value Convergence
    "X-28": "trend",      # MTF Confluence
    # Trend (XII)
    "XII-01": "regime",   # ADX (siła trendu = meta)
    "XII-02": "trend",    # Ichimoku
    "XII-03": "trend",    # EMA50/200 (golden/death cross)
    "XII-04": "trend",    # Supertrend
    "XII-05": "mean_rev", # Fibonacci retracement
    "XII-06": "trend",    # Donchian/HMA trend
    "XII-07": "mean_rev", # RSI Divergence
    # Wolumen/Flow (F/V)
    "V-01": "trend",      # OBV
    "V-02": "mean_rev",   # VWAP (powrót do VWAP)
    "V-03": "trend",      # CVD
    "V-04": "breakout",   # Volume Anomaly
    "V-05": "trend",      # Force Index
    "V-06": "mean_rev",   # Delta Divergence
    "V-07": "mean_rev",   # Anchored VWAP
    "VP-01": "mean_rev",  # Volume Profile/VPOC (S/R magnet)
    "VSA-01": "event",    # Volume Spread Analysis
    "V-13": "vol_signal", # Realized Vol
    "V-14": "regime",     # Choppiness Index
    # Struktura / Sesje (S)
    "SES-01": "event",    # Zegar Sesji
    "SES-02": "breakout", # Azja Range breakout
    "SMC-01": "mean_rev", # Order Block
    "SMC-02": "mean_rev", # Fair Value Gap
    "SMC-03": "breakout", # Break of Structure
    # Radar / Augur (R/Z) — meta-kontekst
    "AUG-01": "event",    # Augur (zdarzenia fundamentalne)
    "RADAR-01": "regime", # BTC Trend
    "RADAR-02": "regime", # BTC Dominacja
    "RADAR-03": "regime", # Przepływ kapitału
    "RADAR-04": "risk_filter",  # Stres korelacji (kaskada)
    "RADAR-05": "regime", # Lead-lag BTC→alty
    # Psychologia (R)
    "PSY-01": "mean_rev", # Funding extreme (contrarian)
    "PSY-02": "mean_rev", # Long/Short ratio
    "PSY-03": "mean_rev", # Fear & Greed
    "PSY-04": "mean_rev", # OI Divergence
    # Sentyment (R)
    "NEWS-01": "event",   # News sentyment
    # On-chain (O)
    "OC-01": "mean_rev",  # MVRV
    "OC-02": "mean_rev",  # SOPR
    "OC-03": "mean_rev",  # Puell Multiple
    "OC-04": "event",     # Exchange Netflow
    "OC-05": "risk_filter",  # Wash Trading
    # Anty-manipulacja (A)
    "A-01": "risk_filter",  # Stop Hunt
    "A-02": "risk_filter",  # Wick Rejection
    "A-03": "risk_filter",  # Wash Volume
    "A-05": "risk_filter",  # Bart Pattern
    # Dźwignia/Zmienność (L/V)
    "VI-13": "risk_filter", # ATR Leverage
    "L-14": "risk_filter",  # Ulcer Index
    # Meta-bramy badawcze (H/N/Z/D/C)
    "H-01": "regime",     # Hurst-DFA
    "N-01": "regime",     # Permutation Entropy
    "N-02": "regime",     # FracDiff
    "Z-01": "risk_filter", # ToxicFlow VPIN
    "Z-02": "risk_filter", # Pump Detect
    "Z-03": "risk_filter", # Bubble/Crash
    "Z-04": "risk_filter", # Cascade
    "Z-05": "risk_filter", # Detektor Klimaksu
    "Z-06": "risk_filter", # Amihud Illiquidity
    "Z-07": "mean_rev",   # Pi Cycle Top
    "D-01": "regime",     # Path Signature (Lévy Area)
    "C-01": "stat_arb",   # Cross-sectional Relative Strength
    # Zmiana reżimu (R)
    "CP-01": "regime",    # CUSUM change-point
    "BOCPD-01": "regime", # Bayesian change-point
    # Makro/Intermarket (K)
    "K-01": "macro",      # DXY momentum
    "K-02": "macro",      # Gold/BTC ratio
}

# Mechanizmy zwiadowców Exploratores (EXP) — wszyscy meta/struktura
MECHANIZMY_ZWIADOWCY: dict = {
    "EXP-01": "regime",     # Higuchi FD
    "EXP-02": "trend",      # HA Scalper
    "EXP-03": "regime",     # Hurst
    "EXP-04": "vol_signal", # Kalman ATR
    "EXP-05": "mean_rev",   # SMC
    "EXP-06": "breakout",   # Katana
    "EXP-07": "trend",      # TLP
    "EXP-08": "event",      # Night Turbo
    "EXP-09": "breakout",   # Liquidity Sweep
    "EXP-10": "breakout",   # Displacement
    "EXP-11": "regime",     # Dynamic
    "EXP-12": "event",      # Atmabhan (L2)
}


def _wstrzyknij_mechanizm(neurony: list) -> list:
    """Prawo XXII — nadaje każdemu neuronowi jego MECHANIZM z mapy (jedno źródło prawdy)."""
    for n in neurony:
        mech = MECHANIZMY.get(n.KLUCZ)
        if mech:
            n.MECHANIZM = mech
    return neurony


def wszystkie_neurony() -> List[MikroNeuron]:
    """Tworzy instancje wszystkich zaimplementowanych neuronów."""
    return _wstrzyknij_mechanizm([
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
        NeuronDominacja(), NeuronPrzeplyw(), NeuronStresKorelacji(), NeuronLeadBTC(),
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
        # Entropia/Pamięć (N) — PE meta-brama chaosu (N-01) + FracDiff persystencja (N-02, W-339)
        NeuronPermutationEntropy(), NeuronFracDiff(),
        # Zagrożenie (Z) — VPIN meta-brama obronna (Z-01) + PumpDetect kierunkowy (Z-02)
        # + Bubble/Crash kill-switch (Z-03, W-278) + Cascade/Dead-Cat (Z-04, W-279), BIB-020 rozdz. 28
        NeuronToxicFlow(), NeuronPumpDetect(), NeuronBubbleCrash(), NeuronCascade(),
        # + Detektor Ruchu Klimaksowego dwukierunkowy (Z-05, W-315): szczyt→SHORT, dołek→LONG
        NeuronDetektorRuchu(),
        # Amihud Illiquidity (Z-06, meta-brama płynności) + Pi Cycle Top (Z-07, kill-switch szczytu) — W-322
        NeuronAmihudIlliquidity(), NeuronPiCycleTop(),
        # Geometria ścieżki (D) — Lévy Area Close×Volume, Rough Path Theory (W-079)
        NeuronPathSignature(),
        # Przekrój koszyka (C) — Cross-sectional Relative Strength (C-01, W-335)
        NeuronRelativeStrength(),
        # Zmiana reżimu (R) — CUSUM change-point (CP-01, W-336) + BOCPD Bayesowski (BOCPD-01, W-338)
        NeuronChangePoint(), NeuronBOCPD(),
        # Makro/Intermarket (K) — DXY trend (K-01, W-085 Murphy) + Gold/BTC ratio (K-02, W-089)
        NeuronDXYTrend(), NeuronGoldBTC(),
    ])


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


def raport_mechanizmow() -> dict:
    """
    Prawo XXII — diagnostyka dekorelacji wg MECHANIZMU przewagi.
    Grupuje neurony po (KATEGORIA, MECHANIZM) i wskazuje skupiska redundancji.
    Dwa+ aktywne neurony o tym samym (KATEGORIA, MECHANIZM) = kandydaci do pomiaru
    korelacji (Prawo XVI) i ewentualnego scalenia.
    """
    neurony = [n for n in wszystkie_neurony() if n.DOSTEPNY]
    rozklad: dict = {}
    pary: dict = {}
    for n in neurony:
        mech = getattr(n, "MECHANIZM", "trend")
        rozklad[mech] = rozklad.get(mech, 0) + 1
        klucz = (n.KATEGORIA, mech)
        pary.setdefault(klucz, []).append(n.KLUCZ)

    skupiska = {
        f"{kat}/{mech}": klucze
        for (kat, mech), klucze in pary.items()
        if len(klucze) >= 2
    }
    return {
        "rozklad_mechanizmow": dict(sorted(rozklad.items(), key=lambda x: -x[1])),
        "liczba_mechanizmow": len(rozklad),
        "skupiska_redundancji": skupiska,   # (KATEGORIA/MECHANIZM) → [klucze] gdy ≥2
        "neuronow_aktywnych": len(neurony),
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
# DLA NOWICJUSZA: nie każdy neuron ma sens na każdym interwale. Ale UWAGA — pomiar
# (W-323 A/B) obalił intuicję „dedykacja przez wykluczenie". Wycięcie z 4h neuronów
# oznaczonych „tylko-scalp" (HA Scalper *elitarny*, CVD, sesje) ZAŁAMAŁO wynik (−8.48pp):
# momentum/flow DZIAŁAJĄ cross-TF. Lekcja: wykluczamy neuron ze stylu TYLKO gdy jest
# STRUKTURALNIE NIEZDOLNY na tym interwale (brak danych / wskaźnik liczony na złym TF),
# nie „bo wydaje się szybki/wolny". Domyślnie INCLUDE (zasada włączności).
#
# ZASADA WŁĄCZNOŚCI (W-323b, Prawo I):
#   • Neuron należy do WSZYSTKICH stylów (_U), CHYBA że pomiar/struktura nakazuje inaczej.
#   • Wykluczenia DANE-uzasadnione (nie opinia):
#       - OC-01..04 (MVRV/SOPR/Puell/Netflow): wymagają feedu on-chain → WYCISZONE
#         (DOSTEPNY=False) na czystym OHLCV; sens tylko w INVEST (1D-1W z danymi łańcucha).
#       - Z-07 Pi Cycle: SMA-111 vs 2×SMA-350 to sygnał CYKLU dziennego; na 4h/1h to szum
#         (111 barów 4h ≈ 18 dni ≠ cykl) → tylko INVEST.
#   • Wszystko inne — momentum/trend/flow/struktura/sentyment/bezpieczniki — uniwersalne,
#     bo udowodniono cross-TF wartość lub to obrona działająca zawsze.
#
# Różnicowanie SCALP↔SWING: NA RAZIE wspólny aktywny skład (brak pomiaru per-neuron, a
# zgadywanie szkodzi — W-323). Rozdzielimy DOPIERO gdy scoreboard kontrybucji per styl da
# dowód (Prawo I). To „tablica do żonglowania" — strojona pomiarem, nie intuicją.
# Prawo XXI: KAŻDY z 70 neuronów MUSI tu być (audyt sprawdza brak sierot/braków).
#
# Style: "SCALP" (M1-1h), "SWING" (4h-1D), "INVEST" (1D-1W; +on-chain +cykl).

STYL_SCALP = "SCALP"
STYL_SWING = "SWING"
STYL_INVEST = "INVEST"
WSZYSTKIE_STYLE: tuple = (STYL_SCALP, STYL_SWING, STYL_INVEST)

# Uniwersalny = działa/broni na każdym interwale (zasada włączności — domyślny).
_U = WSZYSTKIE_STYLE
_INV = (STYL_INVEST,)   # tylko inwestycja (on-chain feed / cykl dzienny)

NEURONY_STYLU: dict = {
    # Momentum (M) — oscylatory + Value-Z: cross-TF (pomiar: działają też na 4h)
    "X-01": _U, "X-02": _U, "X-03": _U, "X-04": _U, "X-06": _U, "X-08": _U,
    "X-09": _U, "X-12": _U, "X-17": _U, "X-25": _U, "X-26": _U, "X-27": _U,
    # Trend (T) — EMA/HMA/ADX/Ichimoku/Supertrend/Donchian/MTF/Fib/OB/RSIdiv: cross-TF
    "X-05": _U, "X-10": _U, "X-18": _U, "X-28": _U,
    "XII-01": _U, "XII-02": _U, "XII-03": _U, "XII-04": _U,
    "XII-05": _U, "XII-06": _U, "XII-07": _U,
    # Wolumen/Flow (F) — OBV/VWAP/CVD/anomalia/ForceIndex/Delta/AVWAP/VSA/RVOL: cross-TF
    "V-01": _U, "V-02": _U, "V-03": _U, "V-04": _U, "V-05": _U, "V-06": _U,
    "V-07": _U, "VSA-01": _U, "X-11": _U,
    # Struktura/SMC (S) — sesje/FVG/OB/BOS/VPOC: cross-TF (sesje istotne też na 4h)
    "SES-01": _U, "SES-02": _U, "SMC-01": _U, "SMC-02": _U, "SMC-03": _U, "VP-01": _U,
    # On-chain (O) — OC-01..04 wymagają feedu łańcucha → tylko INVEST; OC-05 (wash, OHLCV) uniwersalny
    "OC-01": _INV, "OC-02": _INV, "OC-03": _INV, "OC-04": _INV, "OC-05": _U,
    # Reżim/Sentyment (R) — futures/Fear&Greed/RADAR/news/augur: kontekst na każdym TF
    "PSY-01": _U, "PSY-02": _U, "PSY-03": _U, "PSY-04": _U,
    "RADAR-01": _U, "RADAR-02": _U, "RADAR-03": _U, "RADAR-04": _U, "RADAR-05": _U, "AUG-01": _U, "NEWS-01": _U,
    # Meta-bramy reżimu/chaosu (H/N/V/D/L) — klasyfikują każdy interwał
    "H-01": _U, "N-01": _U, "N-02": _U, "V-13": _U, "V-14": _U, "D-01": _U, "L-14": _U, "VI-13": _U,
    # Anty-manipulacja (A) — uniwersalna obrona
    "A-01": _U, "A-02": _U, "A-03": _U, "A-05": _U,
    # Zagrożenie (Z) — bezpieczniki uniwersalne; Pi Cycle (Z-07) to cykl dzienny → tylko INVEST
    "Z-01": _U, "Z-02": _U, "Z-03": _U, "Z-04": _U, "Z-05": _U, "Z-06": _U, "Z-07": _INV,
    # Przekrój koszyka (C) — Cross-sectional RS, uniwersalny (zależy od koszyka, nie TF)
    "C-01": _U,
    # Zmiana reżimu (R) — CUSUM (CP-01) + BOCPD Bayesowski (BOCPD-01), oba uniwersalne
    "CP-01": _U, "BOCPD-01": _U,
    # Makro/Intermarket (K) — DXY i Gold/BTC: dane na poziomie 1D, ożywają przy makro CSV
    # INVEST bo dane makro mają sens na dłuższych horyzontach (nie SCALP 1m)
    "K-01": _INV, "K-02": _INV,
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
