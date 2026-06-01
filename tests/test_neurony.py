"""Testy Neuronów Produkcyjnych — momentum, trend, wolumen, psychologia, on-chain, struktura."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.neurony.momentum import NeuronRSI, NeuronMACD, NeuronBBands, NeuronEMACross, NeuronWilliamsR, NeuronATRDeviation
from imperium.legiony.neurony.trend import NeuronADX, NeuronIchimoku, NeuronEMA50_200, NeuronSupertrend
from imperium.legiony.neurony.wolumen import NeuronOBV, NeuronVWAP, NeuronCVD, NeuronVolumeAnomaly
from imperium.legiony.neurony.psychologia import NeuronFearGreed, NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv
from imperium.legiony.neurony.onchain import NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow
from imperium.legiony.neurony.struktura import NeuronOrderBlock, NeuronFVG, NeuronBOS, NeuronVSA


# ─── MOMENTUM ─────────────────────────────────────────────────────────────────

def test_rsi_wyprzedany():
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": 25.0})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.70


def test_rsi_wykupiony():
    n = NeuronRSI()
    s = n.interpretuj({"RSI_14": 75.0})
    assert s.kierunek == "SHORT"
    assert s.pewnosc >= 0.70


def test_rsi_ekstremalny():
    n = NeuronRSI()
    assert n.interpretuj({"RSI_14": 15.0}).pewnosc == 0.90
    assert n.interpretuj({"RSI_14": 85.0}).pewnosc == 0.90


def test_rsi_brak_danych():
    n = NeuronRSI()
    s = n.interpretuj({})
    assert s.kierunek == "NEUTRAL"


def test_macd_crossover_bull():
    n = NeuronMACD()
    s = n.interpretuj({"MACD": 0.001, "MACD_SIGNAL": 0.0009, "MACD_HIST": 0.0002, "MACD_HIST_PREV": 0.0001})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.65


def test_macd_crossover_bear():
    n = NeuronMACD()
    s = n.interpretuj({"MACD": -0.001, "MACD_SIGNAL": -0.0009})
    assert s.kierunek == "SHORT"


def test_bbands_dotknięcie_dolnej():
    n = NeuronBBands()
    # Cena dokładnie NA dolnej BB lub poniżej → LONG (mean reversion)
    s = n.interpretuj({"CLOSE": 89.0, "BB_UPPER": 110.0, "BB_MIDDLE": 100.0, "BB_LOWER": 90.0})
    assert s.kierunek == "LONG"


def test_bbands_squeeze():
    n = NeuronBBands()
    s = n.interpretuj({"CLOSE": 100.0, "BB_UPPER": 100.5, "BB_MIDDLE": 100.0, "BB_LOWER": 99.5})
    assert s.kierunek == "NEUTRAL"


def test_ema_cross_golden():
    n = NeuronEMACross()
    s = n.interpretuj({"EMA_9": 101.0, "EMA_21": 99.0, "EMA_9_PREV": 98.0, "EMA_21_PREV": 99.5})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.80


def test_williams_r():
    n = NeuronWilliamsR()
    assert n.interpretuj({"WILLIAMS_R": -85.0}).kierunek == "LONG"
    assert n.interpretuj({"WILLIAMS_R": -15.0}).kierunek == "SHORT"
    assert n.interpretuj({"WILLIAMS_R": -50.0}).kierunek == "NEUTRAL"


def test_atr_deviation_szum_ignorowany():
    n = NeuronATRDeviation()
    s = n.interpretuj({"ATR_DEVIATION": 0.5})  # < MinDisplacement 1.0
    assert s.kierunek == "NEUTRAL"


def test_atr_deviation_mean_reversion_short():
    n = NeuronATRDeviation()
    # RANGING + cena daleko NAD średnią → mean-reversion → SHORT (powrót w dół)
    s = n.interpretuj({"ATR_DEVIATION": 2.5, "REZIM": "RANGING"})
    assert s.kierunek == "SHORT"
    assert s.pewnosc == 0.80  # ekstremalne (>= FAR_FACTOR)


def test_atr_deviation_mean_reversion_long():
    n = NeuronATRDeviation()
    # RANGING + cena pod średnią → LONG (powrót w górę)
    s = n.interpretuj({"ATR_DEVIATION": -1.5, "REZIM": "RANGING"})
    assert s.kierunek == "LONG"


def test_atr_deviation_momentum_trend():
    n = NeuronATRDeviation()
    # TREND + cena nad średnią → momentum → LONG (kontynuacja)
    s = n.interpretuj({"ATR_DEVIATION": 2.0, "REZIM": "TREND_STRONG"})
    assert s.kierunek == "LONG"


def test_atr_deviation_adx_decyduje_tryb():
    n = NeuronATRDeviation()
    # Bez reżimu, ADX wysoki → tryb trend → momentum LONG
    s = n.interpretuj({"ATR_DEVIATION": 1.5, "ADX_14": 30.0})
    assert s.kierunek == "LONG"
    # ADX niski → mean-reversion → SHORT
    s2 = n.interpretuj({"ATR_DEVIATION": 1.5, "ADX_14": 15.0})
    assert s2.kierunek == "SHORT"


def test_atr_deviation_brak_danych():
    n = NeuronATRDeviation()
    assert n.interpretuj({}).kierunek == "NEUTRAL"


# ─── TREND ────────────────────────────────────────────────────────────────────

def test_adx_trend_bull():
    n = NeuronADX()
    s = n.interpretuj({"ADX_14": 35.0, "DI_PLUS": 30.0, "DI_MINUS": 20.0})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.70


def test_adx_brak_trendu():
    n = NeuronADX()
    s = n.interpretuj({"ADX_14": 15.0})
    assert s.kierunek == "NEUTRAL"


def test_ichimoku_powyzej_chmury():
    n = NeuronIchimoku()
    s = n.interpretuj({
        "CLOSE": 105.0, "ICHIMOKU_SENKOU_A": 98.0, "ICHIMOKU_SENKOU_B": 95.0,
        "ICHIMOKU_TENKAN": 102.0, "ICHIMOKU_KIJUN": 99.0,
    })
    assert s.kierunek == "LONG"


def test_ema50_200_golden_cross():
    n = NeuronEMA50_200()
    s = n.interpretuj({"EMA_50": 101.0, "EMA_200": 99.0, "EMA_50_PREV": 98.5, "EMA_200_PREV": 99.5})
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.95


def test_supertrend_zmiana():
    n = NeuronSupertrend()
    s = n.interpretuj({"CLOSE": 100.0, "SUPERTREND": 95.0, "SUPERTREND_DIR": 1, "SUPERTREND_DIR_PREV": -1})
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.90


# ─── WOLUMEN ──────────────────────────────────────────────────────────────────

def test_obv_dywergencja_bull():
    n = NeuronOBV()
    s = n.interpretuj({
        "OBV": 50000, "OBV_EMA_20": 40000,
        "CLOSE": 99.0, "CLOSE_PREV": 100.0,  # cena spada ale OBV rośnie
    })
    assert s.kierunek == "LONG"
    assert "DYWERGENCJA" in s.powody[0]


def test_vwap_powyzej():
    n = NeuronVWAP()
    s = n.interpretuj({"CLOSE": 102.0, "VWAP": 100.0})
    assert s.kierunek == "LONG"


def test_vwap_std_extreme():
    n = NeuronVWAP()
    s = n.interpretuj({"CLOSE": 94.0, "VWAP": 100.0, "VWAP_STD": 3.0})
    assert s.kierunek == "LONG"  # ponad -2σ


def test_cvd_dywergencja():
    n = NeuronCVD()
    s = n.interpretuj({"CVD": 5000, "CVD_PREV": 3000, "CLOSE": 99.0, "CLOSE_PREV": 100.0})
    assert s.kierunek == "LONG"  # cena spada ale CVD rośnie


def test_volume_anomaly_potwierdza():
    n = NeuronVolumeAnomaly()
    s = n.interpretuj({"VOLUME": 3500, "VOLUME_MA20": 1000, "CLOSE": 102.0, "CLOSE_PREV": 100.0})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.65


# ─── PSYCHOLOGIA ──────────────────────────────────────────────────────────────

def test_fear_greed_ekstremalny_strach():
    n = NeuronFearGreed()
    s = n.interpretuj({"FEAR_GREED_INDEX": 8})
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.90


def test_fear_greed_chciwosc():
    n = NeuronFearGreed()
    s = n.interpretuj({"FEAR_GREED_INDEX": 92})
    assert s.kierunek == "SHORT"
    assert s.pewnosc == 0.90


def test_funding_ekstremalny():
    n = NeuronFundingExtreme()
    s = n.interpretuj({"FUNDING_RATE": 0.003})  # 0.3% — ekstremalnie wysoki
    assert s.kierunek == "SHORT"
    assert s.pewnosc >= 0.85


def test_panika_detal_crowded_long():
    n = NeuronPanikaDetal()
    s = n.interpretuj({"LONG_SHORT_RATIO": 0.83})  # 83% longów
    assert s.kierunek == "SHORT"
    assert s.pewnosc >= 0.80


def test_oi_div_potwierdzenie_bull():
    n = NeuronOIDiv()
    s = n.interpretuj({"OPEN_INTEREST": 1100, "OPEN_INTEREST_PREV": 1000, "CLOSE": 102.0, "CLOSE_PREV": 100.0})
    assert s.kierunek == "LONG"


# ─── ON-CHAIN ─────────────────────────────────────────────────────────────────

def test_mvrv_kapituacja():
    n = NeuronMVRV()
    s = n.interpretuj({"MVRV_Z_SCORE": -0.7})
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.95


def test_mvrv_banka():
    n = NeuronMVRV()
    s = n.interpretuj({"MVRV_Z_SCORE": 7.5})
    assert s.kierunek == "SHORT"
    assert s.pewnosc == 0.95


def test_sopr_kapituacja():
    n = NeuronSOPR()
    s = n.interpretuj({"SOPR": 0.92})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.85


def test_puell_ekstremalny():
    n = NeuronPuellMultiple()
    assert n.interpretuj({"PUELL_MULTIPLE": 0.4}).kierunek == "LONG"
    assert n.interpretuj({"PUELL_MULTIPLE": 5.0}).kierunek == "SHORT"


def test_netflow_odpływ():
    n = NeuronExchangeNetflow()
    s = n.interpretuj({"EXCHANGE_NETFLOW_BTC": -6000})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.85


# ─── STRUKTURA ────────────────────────────────────────────────────────────────

def test_order_block_bullish():
    n = NeuronOrderBlock()
    s = n.interpretuj({
        "CLOSE": 99.5, "BULL_OB_HIGH": 100.0, "BULL_OB_LOW": 98.0
    })
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.85


def test_fvg_bullish():
    n = NeuronFVG()
    s = n.interpretuj({
        "CLOSE": 100.5, "BULL_FVG_HIGH": 101.0, "BULL_FVG_LOW": 100.0
    })
    assert s.kierunek == "LONG"


def test_bos_mss_bull():
    n = NeuronBOS()
    s = n.interpretuj({"CLOSE": 102.0, "MSS_BULLISH": True})
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.90


def test_bos_tylko_bos():
    n = NeuronBOS()
    s = n.interpretuj({"CLOSE": 102.0, "BOS_BULLISH": True})
    assert s.kierunek == "LONG"
    assert s.pewnosc == 0.75


def test_vsa_stop_volume():
    n = NeuronVSA()
    # Ultra-high volume, zawężony spread, close wysoko
    s = n.interpretuj({
        "HIGH": 101.5, "LOW": 100.5, "CLOSE": 101.4,
        "VOLUME": 5000, "VOLUME_MA20": 1000,
    })
    # spread wąski: 1.0 relative, vol 5× → powinien wykryć anomalię
    assert s.pewnosc > 0


def test_neurony_brak_danych_nie_crashuje():
    """Każdy neuron musi obsłużyć pusty dict."""
    neurony = [
        NeuronRSI(), NeuronMACD(), NeuronBBands(), NeuronEMACross(), NeuronWilliamsR(), NeuronATRDeviation(),
        NeuronADX(), NeuronIchimoku(), NeuronEMA50_200(), NeuronSupertrend(),
        NeuronOBV(), NeuronVWAP(), NeuronCVD(), NeuronVolumeAnomaly(),
        NeuronFearGreed(), NeuronFundingExtreme(), NeuronPanikaDetal(),
        NeuronMVRV(), NeuronSOPR(), NeuronPuellMultiple(), NeuronExchangeNetflow(),
        NeuronOrderBlock(), NeuronFVG(), NeuronBOS(), NeuronVSA(),
    ]
    for n in neurony:
        s = n.interpretuj({})
        assert s is not None
        assert s.kierunek in ("LONG", "SHORT", "NEUTRAL"), f"{n.KLUCZ} zwrócił nieznany kierunek"
