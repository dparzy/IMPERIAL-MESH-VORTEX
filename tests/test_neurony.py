"""Testy Neuronów Produkcyjnych — momentum, trend, wolumen, psychologia, on-chain, struktura."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.neurony.momentum import NeuronRSI, NeuronMACD, NeuronBBands, NeuronEMACross, NeuronWilliamsR, NeuronATRDeviation, NeuronHAScalper, NeuronStochRSI, NeuronTRIX, NeuronAwesome, NeuronAccelerator, NeuronBBSqueeze
from imperium.legiony.neurony.trend import NeuronADX, NeuronIchimoku, NeuronEMA50_200, NeuronSupertrend, NeuronDonchian, NeuronHMA, NeuronFibonacci, NeuronRSIDiv, NeuronOBZone
from imperium.legiony.neurony.straz import NeuronStopHunt, NeuronWickRejection, NeuronWashVol, NeuronBartPattern
from imperium.legiony.neurony.wolumen import NeuronOBV, NeuronVWAP, NeuronCVD, NeuronVolumeAnomaly, NeuronRVOL
from imperium.legiony.neurony.psychologia import NeuronFearGreed, NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv
from imperium.legiony.neurony.onchain import NeuronMVRV, NeuronSOPR, NeuronPuellMultiple, NeuronExchangeNetflow
from imperium.legiony.neurony.struktura import NeuronOrderBlock, NeuronFVG, NeuronBOS, NeuronVSA
from imperium.legiony.neurony.dzwignia import NeuronChoppiness, NeuronUlcer


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


def test_stochrsi_wyprzedany_long():
    n = NeuronStochRSI()
    s = n.interpretuj({"STOCHRSI": 15.0})
    assert s.kierunek == "LONG"
    s2 = n.interpretuj({"STOCHRSI": 5.0})
    assert s2.kierunek == "LONG" and s2.pewnosc == 0.85


def test_stochrsi_wykupiony_short():
    n = NeuronStochRSI()
    assert n.interpretuj({"STOCHRSI": 85.0}).kierunek == "SHORT"
    assert n.interpretuj({"STOCHRSI": 95.0}).pewnosc == 0.85


def test_stochrsi_neutral_i_brak_danych():
    n = NeuronStochRSI()
    assert n.interpretuj({"STOCHRSI": 50.0}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).pewnosc == 0.0


def test_trix_przeciecie_zera():
    n = NeuronTRIX()
    s = n.interpretuj({"TRIX": 0.002, "TRIX_PREV": -0.001})
    assert s.kierunek == "LONG" and s.pewnosc == 0.80
    s2 = n.interpretuj({"TRIX": -0.002, "TRIX_PREV": 0.001})
    assert s2.kierunek == "SHORT" and s2.pewnosc == 0.80
    # bez przecięcia, tylko znak
    assert n.interpretuj({"TRIX": 0.003, "TRIX_PREV": 0.002}).kierunek == "LONG"
    assert n.interpretuj({}).kierunek == "NEUTRAL"


def test_awesome_oscillator():
    n = NeuronAwesome()
    # przecięcie zera w górę
    assert n.interpretuj({"AO": 0.5, "AO_PREV": -0.2}).kierunek == "LONG"
    assert n.interpretuj({"AO": -0.5, "AO_PREV": 0.2}).kierunek == "SHORT"
    # nad zerem i rośnie
    assert n.interpretuj({"AO": 1.0, "AO_PREV": 0.5}).kierunek == "LONG"
    assert n.interpretuj({}).kierunek == "NEUTRAL"


def test_accelerator_przyspieszenie():
    n = NeuronAccelerator()
    # przecięcie zera w górę = LONG
    assert n.interpretuj({"AC": 0.3, "AC_PREV": -0.1}).kierunek == "LONG"
    assert n.interpretuj({"AC": -0.3, "AC_PREV": 0.1}).kierunek == "SHORT"
    # nad zerem i rośnie
    assert n.interpretuj({"AC": 0.5, "AC_PREV": 0.2}).kierunek == "LONG"
    # pod zerem i opada
    assert n.interpretuj({"AC": -0.5, "AC_PREV": -0.2}).kierunek == "SHORT"
    assert n.interpretuj({}).kierunek == "NEUTRAL"


def test_hma_nachylenie():
    n = NeuronHMA()
    # HMA rośnie + cena nad HMA = LONG mocny
    s = n.interpretuj({"HMA": 101.0, "HMA_PREV": 100.0, "CLOSE": 102.0})
    assert s.kierunek == "LONG" and s.pewnosc == 0.70
    # HMA opada + cena pod HMA = SHORT mocny
    s2 = n.interpretuj({"HMA": 99.0, "HMA_PREV": 100.0, "CLOSE": 98.0})
    assert s2.kierunek == "SHORT" and s2.pewnosc == 0.70
    # HMA rośnie bez potwierdzenia ceną = LONG słabszy
    assert n.interpretuj({"HMA": 101.0, "HMA_PREV": 100.0, "CLOSE": 99.0}).kierunek == "LONG"
    assert n.interpretuj({}).kierunek == "NEUTRAL"


def test_donchian_wybicie():
    n = NeuronDonchian()
    s = n.interpretuj({"CLOSE": 105.0, "DONCHIAN_UPPER": 104.0, "DONCHIAN_LOWER": 96.0})
    assert s.kierunek == "LONG" and s.pewnosc == 0.75
    s2 = n.interpretuj({"CLOSE": 95.0, "DONCHIAN_UPPER": 104.0, "DONCHIAN_LOWER": 96.0})
    assert s2.kierunek == "SHORT"
    # w kanale
    assert n.interpretuj({"CLOSE": 100.0, "DONCHIAN_UPPER": 104.0, "DONCHIAN_LOWER": 96.0}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).kierunek == "NEUTRAL"


def test_rvol_wsparcie_wolumenu():
    n = NeuronRVOL()
    # wysoki RVOL + ruch w górę
    s = n.interpretuj({"RVOL": 2.0, "CLOSE": 101.0, "CLOSE_PREV": 100.0})
    assert s.kierunek == "LONG"
    s2 = n.interpretuj({"RVOL": 3.0, "CLOSE": 99.0, "CLOSE_PREV": 100.0})
    assert s2.kierunek == "SHORT" and s2.pewnosc == 0.75
    # niski RVOL → neutralny
    assert n.interpretuj({"RVOL": 0.5, "CLOSE": 101.0, "CLOSE_PREV": 100.0}).kierunek == "NEUTRAL"
    assert n.interpretuj({}).kierunek == "NEUTRAL"


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


# ─── HA SCALPER (X-26) ────────────────────────────────────────────────────────

def test_ha_scalper_bull_z_momentum():
    n = NeuronHAScalper()
    s = n.interpretuj({"HA_BULL": True, "HA_BEAR": False, "HA_MOMENTUM": 0.05,
                        "HA_VOLATILITY_INDEX": 0.015, "REZIM": "TREND_STRONG"})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.70


def test_ha_scalper_bear_z_momentum():
    n = NeuronHAScalper()
    s = n.interpretuj({"HA_BULL": False, "HA_BEAR": True, "HA_MOMENTUM": -0.05,
                        "HA_VOLATILITY_INDEX": 0.015, "REZIM": "TREND_STRONG"})
    assert s.kierunek == "SHORT"
    assert s.pewnosc >= 0.70


def test_ha_scalper_slaby_sygnal_sprzeczny_momentum():
    n = NeuronHAScalper()
    # Świeca bycza ale momentum spada — obniżona pewność
    s = n.interpretuj({"HA_BULL": True, "HA_BEAR": False, "HA_MOMENTUM": -0.02,
                        "HA_VOLATILITY_INDEX": 0.015, "REZIM": "TREND_STRONG"})
    assert s.kierunek == "LONG"
    assert s.pewnosc < 0.65  # obniżona


def test_ha_scalper_konsolidacja_blokuje():
    n = NeuronHAScalper()
    # RANGING + niski Volatility_Index → NEUTRAL (ochrona przed konsolidacją)
    s = n.interpretuj({"HA_BULL": True, "HA_BEAR": False, "HA_MOMENTUM": 0.05,
                        "HA_VOLATILITY_INDEX": 0.003, "REZIM": "RANGING"})
    assert s.kierunek == "NEUTRAL"


def test_ha_scalper_trend_niski_vol_dozwolony():
    n = NeuronHAScalper()
    # W trendzie niższy próg volatility (0.003 vs 0.008)
    s = n.interpretuj({"HA_BULL": True, "HA_BEAR": False, "HA_MOMENTUM": 0.04,
                        "HA_VOLATILITY_INDEX": 0.005, "REZIM": "TREND_STRONG"})
    assert s.kierunek == "LONG"  # dozwolony w trendzie


def test_ha_scalper_doji_neutral():
    n = NeuronHAScalper()
    s = n.interpretuj({"HA_BULL": False, "HA_BEAR": False, "HA_MOMENTUM": 0.0,
                        "HA_VOLATILITY_INDEX": 0.015})
    assert s.kierunek == "NEUTRAL"


def test_ha_scalper_brak_danych():
    n = NeuronHAScalper()
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
        NeuronRSI(), NeuronMACD(), NeuronBBands(), NeuronEMACross(), NeuronWilliamsR(), NeuronATRDeviation(), NeuronHAScalper(), NeuronStochRSI(), NeuronTRIX(), NeuronAwesome(),
        NeuronADX(), NeuronIchimoku(), NeuronEMA50_200(), NeuronSupertrend(), NeuronDonchian(),
        NeuronOBV(), NeuronVWAP(), NeuronCVD(), NeuronVolumeAnomaly(), NeuronRVOL(),
        NeuronFearGreed(), NeuronFundingExtreme(), NeuronPanikaDetal(),
        NeuronMVRV(), NeuronSOPR(), NeuronPuellMultiple(), NeuronExchangeNetflow(),
        NeuronOrderBlock(), NeuronFVG(), NeuronBOS(), NeuronVSA(),
    ]
    for n in neurony:
        s = n.interpretuj({})
        assert s is not None
        assert s.kierunek in ("LONG", "SHORT", "NEUTRAL"), f"{n.KLUCZ} zwrócił nieznany kierunek"


# ─── Prawo XV: X-26 HAScalper nie może być martwym głosem ─────────────────────

def test_budowniczy_produkuje_ha_dla_x26():
    """
    REGRESJA Prawa XV: X-26 NeuronHAScalper czyta HA_BULL/HA_BEAR/HA_MOMENTUM/
    HA_VOLATILITY_INDEX. Budowniczy MUSI je produkować — inaczej X-26 jest martwy.
    """
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
    from imperium.legiony.neurony.momentum import NeuronHAScalper

    bud = BudowniczyWskaznikow.__new__(BudowniczyWskaznikow)
    n = NeuronHAScalper()

    def bary_kier(up=True, m=40):
        out = []; p = 100.0
        for i in range(m):
            p += (0.8 if up else -0.8)
            out.append({"open": p - 0.4, "high": p + 0.5, "low": p - 0.6, "close": p})
        return out

    # Bycza seria → HA klucze obecne + X-26 daje LONG
    w_up = {}
    bud._dodaj_ha(bary_kier(True), w_up)
    assert w_up.get("HA_BULL") is True
    assert w_up.get("HA_BEAR") is False
    assert "HA_MOMENTUM" in w_up
    assert "HA_VOLATILITY_INDEX" in w_up
    assert n.interpretuj(w_up).kierunek == "LONG"

    # Niedźwiedzia seria → X-26 daje SHORT
    w_dn = {}
    bud._dodaj_ha(bary_kier(False), w_dn)
    assert w_dn.get("HA_BEAR") is True
    assert n.interpretuj(w_dn).kierunek == "SHORT"


# ─── STRAŻ / ANTY-MANIPULACJA (KAT A) ─────────────────────────────────────────

def test_a01_stop_hunt_bull():
    """A-01: knot przebił dół kanału, close wrócił nad → LONG (kontra na sweep)."""
    n = NeuronStopHunt()
    w = {"HIGH": 105, "LOW": 88, "CLOSE": 99, "DONCHIAN_UPPER": 110, "DONCHIAN_LOWER": 90}
    s = n.interpretuj(w)
    assert s.kierunek == "LONG"
    assert s.pewnosc > 0.5


def test_a01_stop_hunt_bear():
    """A-01: knot przebił szczyt, close wrócił pod → SHORT."""
    n = NeuronStopHunt()
    w = {"HIGH": 112, "LOW": 95, "CLOSE": 101, "DONCHIAN_UPPER": 110, "DONCHIAN_LOWER": 90}
    s = n.interpretuj(w)
    assert s.kierunek == "SHORT"


def test_a01_stop_hunt_neutral():
    """A-01: cena w kanale, brak sweepu → NEUTRAL."""
    n = NeuronStopHunt()
    w = {"HIGH": 105, "LOW": 95, "CLOSE": 100, "DONCHIAN_UPPER": 110, "DONCHIAN_LOWER": 90}
    assert n.interpretuj(w).kierunek == "NEUTRAL"


def test_a02_wick_rejection_long():
    """A-02: długi dolny knot + małe ciało → odrzucenie dołu → LONG."""
    n = NeuronWickRejection()
    w = {"OPEN": 100, "CLOSE": 101, "HIGH": 102, "LOW": 92}
    s = n.interpretuj(w)
    assert s.kierunek == "LONG"


def test_a02_wick_rejection_short():
    """A-02: długi górny knot + małe ciało → odrzucenie góry → SHORT."""
    n = NeuronWickRejection()
    w = {"OPEN": 100, "CLOSE": 99, "HIGH": 108, "LOW": 98}
    s = n.interpretuj(w)
    assert s.kierunek == "SHORT"


def test_a02_wick_brak_danych():
    """A-02: brak OPEN → NEUTRAL (bezpieczny fallback)."""
    n = NeuronWickRejection()
    assert n.interpretuj({"HIGH": 100, "LOW": 90, "CLOSE": 95}).kierunek == "NEUTRAL"


def test_brama_ulcer_bez_obsuniec():
    """Brama: rosnąca seria (zero drawdownu) → Ulcer Index = 0."""
    from imperium.fundament.brama_kalkulatora import _py_ulcer
    rosnaca = [100 + i for i in range(30)]
    assert _py_ulcer(rosnaca, period=14) == 0.0


def test_brama_ulcer_z_obsunieciem():
    """Brama: seria z obsunięciem → Ulcer Index > 0."""
    from imperium.fundament.brama_kalkulatora import _py_ulcer
    seria = [100] * 10 + [90, 85, 80, 75, 70, 80, 90]  # wyraźny drawdown
    ui = _py_ulcer(seria, period=14)
    assert ui is not None and ui > 0


def test_brama_choppiness_zakres():
    """Brama: Choppiness Index mieści się w 0–100 i istnieje na realnej serii."""
    from imperium.fundament.brama_kalkulatora import _py_choppiness
    import math
    h = [100 + math.sin(i / 3) * 5 for i in range(30)]
    l = [v - 3 for v in h]
    c = [(hi + lo) / 2 for hi, lo in zip(h, l)]
    chop = _py_choppiness(h, l, c, period=14)
    assert chop is not None and 0 <= chop <= 100


def test_brama_choppiness_za_malo_danych():
    """Brama: za mało barów → None (bezpieczny fallback, brak halucynacji)."""
    from imperium.fundament.brama_kalkulatora import _py_choppiness
    assert _py_choppiness([1, 2], [0, 1], [1, 2], period=14) is None


def test_brama_ulcer_dokladnie_period():
    """Brama: Ulcer potrzebuje DOKŁADNIE `period` świec (nie period+1) — warmup."""
    from imperium.fundament.brama_kalkulatora import _py_ulcer
    seria = [100 - i for i in range(14)]   # dokładnie 14 świec, period=14
    assert _py_ulcer(seria, period=14) is not None
    assert _py_ulcer(seria[:13], period=14) is None  # 13 < 14 → None


def test_brama_yang_zhang_zakres():
    """Brama (W-055): Yang-Zhang zwraca annualizowaną vol > 0 na realnej serii OHLC."""
    from imperium.fundament.brama_kalkulatora import _py_yang_zhang
    import math, random
    random.seed(7)
    o, h, l, c = [], [], [], []
    cena = 100.0
    for _ in range(40):
        op = cena
        cl = op * (1 + random.gauss(0, 0.02))
        hi = max(op, cl) * (1 + abs(random.gauss(0, 0.01)))
        lo = min(op, cl) * (1 - abs(random.gauss(0, 0.01)))
        o.append(op); h.append(hi); l.append(lo); c.append(cl)
        cena = cl
    yz = _py_yang_zhang(o, h, l, c, period=20)
    assert yz is not None and yz > 0, "Yang-Zhang musi dać dodatnią annualizowaną vol"


def test_brama_yang_zhang_za_malo_danych():
    """Brama (W-055): < period+1 świec → None (bez halucynacji, Prawo I)."""
    from imperium.fundament.brama_kalkulatora import _py_yang_zhang
    o = h = l = c = [100, 101, 102]
    assert _py_yang_zhang(o, h, l, c, period=20) is None


def test_brama_yang_zhang_skala_jak_hist_vol():
    """Brama (W-055): YZ i HIST_VOL są w tej samej skali (annualized) — rząd wielkości zgodny."""
    from imperium.fundament.brama_kalkulatora import _py_yang_zhang, _py_hist_vol
    import random
    random.seed(11)
    o, h, l, c = [], [], [], []
    cena = 100.0
    for _ in range(60):
        op = cena
        cl = op * (1 + random.gauss(0, 0.03))
        hi = max(op, cl) * (1 + abs(random.gauss(0, 0.015)))
        lo = min(op, cl) * (1 - abs(random.gauss(0, 0.015)))
        o.append(op); h.append(hi); l.append(lo); c.append(cl)
        cena = cl
    yz = _py_yang_zhang(o, h, l, c, period=20)
    hv = _py_hist_vol(c, period=20)
    # Ta sama skala: obie annualizowane, stosunek w rozsądnym przedziale (nie rząd wielkości).
    assert 0.2 < yz / hv < 5.0, f"YZ ({yz:.3f}) i HV ({hv:.3f}) muszą być tej samej skali"


def test_brama_audyt_zrodlo_yang_zhang_pure_python():
    """Prawo XIII: YANG_ZHANG stemplowany jako pure-Python (nie TA-Lib)."""
    from imperium.fundament.brama_kalkulatora import CalculatorGateway, SOURCE_TAG_PY
    import random
    random.seed(3)
    o, h, l, c = [], [], [], []
    cena = 100.0
    for _ in range(40):
        op = cena; cl = op * (1 + random.gauss(0, 0.02))
        o.append(op); h.append(max(op, cl) * 1.01); l.append(min(op, cl) * 0.99); c.append(cl)
        cena = cl
    r = CalculatorGateway().compute("YANG_ZHANG", open=o, high=h, low=l, close=c, period=20)
    assert r.source == SOURCE_TAG_PY, "YANG_ZHANG musi być pure-Python w audycie"


def test_v13_uzywa_yang_zhang_jako_podstawy():
    """V-13 (W-055): czyta YANG_ZHANG_20 jako podstawę, opis sygnalizuje źródło YZ."""
    from imperium.legiony.neurony.dzwignia import NeuronRealizedVol
    s = NeuronRealizedVol().interpretuj({"YANG_ZHANG_20": 0.20, "HIST_VOL_20": 0.99})
    assert s.kierunek == "LONG", "YZ=20% < 30% → niska vol → LONG (ignoruje HV fallback)"
    assert any("YZ=" in p for p in s.powody), "opis musi sygnalizować estymator Yang-Zhang"


def test_v13_fallback_hist_vol():
    """V-13 (W-055): brak YANG_ZHANG_20 → fallback HIST_VOL_20 (bez martwego głosu, Prawo XV)."""
    from imperium.legiony.neurony.dzwignia import NeuronRealizedVol
    s = NeuronRealizedVol().interpretuj({"HIST_VOL_20": 0.95})
    assert s.kierunek == "SHORT", "HV=95% → ekstremalna → SHORT"
    assert any("HV=" in p for p in s.powody), "fallback musi sygnalizować źródło HV"


def test_v13_brak_obu_zrodel_neutral():
    """V-13 (W-055): brak YZ i HV → NEUTRAL (abstynencja, Prawo I)."""
    from imperium.legiony.neurony.dzwignia import NeuronRealizedVol
    assert NeuronRealizedVol().interpretuj({}).kierunek == "NEUTRAL"


def test_brama_audyt_zrodlo_pure_python():
    """Prawo XIII: pure-Python wskaźniki stemplowane jako pure-Python, nie TA-Lib."""
    from imperium.fundament.brama_kalkulatora import (
        CalculatorGateway, SOURCE_TAG_PY, SOURCE_TAG)
    import math
    brama = CalculatorGateway()
    h = [100 + math.sin(i/3)*5 for i in range(30)]
    l = [v - 3 for v in h]; c = [(a+b)/2 for a, b in zip(h, l)]
    r_chop = brama.compute("CHOPPINESS", high=h, low=l, close=c)
    r_ulcer = brama.compute("ULCER", close=c)
    assert r_chop.source == SOURCE_TAG_PY, "CHOPPINESS musi być pure-Python w audycie"
    assert r_ulcer.source == SOURCE_TAG_PY, "ULCER musi być pure-Python w audycie"
    # Kontrola: RSI nadal TA-Lib
    r_rsi = brama.compute("RSI", close=c, period=14)
    assert r_rsi.source == SOURCE_TAG, "RSI musi pozostać TA-Lib"


def test_brama_accelerator_warmup_dokladny():
    """AC: potrzebuje DOKŁADNIE slow+sma_ac świec (off-by-one naprawiony)."""
    from imperium.fundament.brama_kalkulatora import _py_accelerator
    import random
    random.seed(1)
    h = [100 + random.gauss(0, 2) for _ in range(39)]  # slow=34 + sma_ac=5 = 39
    l = [v - 1 for v in h]
    assert _py_accelerator(h, l)[0] is not None, "39 świec wystarcza (slow+sma_ac)"
    assert _py_accelerator(h[:38], l[:38])[0] is None, "38 < 39 → None"


def test_v14_choppiness_trend():
    """V-14: CHOP < 38.2 → silny trend → LONG."""
    s = NeuronChoppiness().interpretuj({"CHOPPINESS_14": 30.0})
    assert s.kierunek == "LONG"
    assert s.pewnosc >= 0.55


def test_v14_choppiness_konsolidacja():
    """V-14: CHOP > 61.8 → piła/konsolidacja → SHORT."""
    s = NeuronChoppiness().interpretuj({"CHOPPINESS_14": 70.0})
    assert s.kierunek == "SHORT"


def test_v14_choppiness_brak_danych():
    """V-14: brak CHOPPINESS_14 → NEUTRAL (abstynencja)."""
    assert NeuronChoppiness().interpretuj({}).kierunek == "NEUTRAL"


def test_l14_ulcer_plytki():
    """L-14: UI < 1% → płytkie obsunięcia → LONG (bezpieczna dźwignia)."""
    s = NeuronUlcer().interpretuj({"ULCER_14": 0.5})
    assert s.kierunek == "LONG"


def test_l14_ulcer_ekstremalny():
    """L-14: UI > 8% → ekstremalne ryzyko spadkowe → SHORT silny."""
    s = NeuronUlcer().interpretuj({"ULCER_14": 12.0})
    assert s.kierunek == "SHORT"
    assert s.pewnosc >= 0.75


def test_l14_ulcer_brak_danych():
    """L-14: brak ULCER_14 → NEUTRAL (abstynencja)."""
    assert NeuronUlcer().interpretuj({}).kierunek == "NEUTRAL"


def test_lv_kategorie_aktywne():
    """Kategorie L i V mają po min. 2 aktywne neurony (Prawo XV — nie martwa litera)."""
    from imperium.legiony.rejestr import wszystkie_neurony
    from imperium.legiony.legatus import WAGI_REZIMU_PLANOWANE
    neu = wszystkie_neurony()
    for kat in ("L", "V"):
        zywe = [n for n in neu if n.KATEGORIA == kat and n.DOSTEPNY]
        assert len(zywe) >= 2, f"Kategoria {kat} powinna mieć min. 2 aktywne neurony"
        assert kat not in WAGI_REZIMU_PLANOWANE, f"{kat} ożywiona — nie w PLANOWANE"


def test_a_kategoria_aktywna():
    """Litera A musi być żywa w roju i NIE w PLANOWANE (Prawo XV/XXI)."""
    from imperium.legiony.rejestr import wszystkie_neurony
    from imperium.legiony.legatus import WAGI_REZIMU_PLANOWANE
    kat_a = [n for n in wszystkie_neurony() if n.KATEGORIA == "A"]
    assert len(kat_a) >= 2, "Powinny być min. 2 neurony anty-manipulacji"
    assert all(n.DOSTEPNY for n in kat_a), "Neurony A muszą być aktywne (żywy głos)"
    assert "A" not in WAGI_REZIMU_PLANOWANE, "A już ożywiona — nie może być w PLANOWANE"


# ─── NOWE NEURONY FAZY 2-3 ────────────────────────────────────────────────────

def test_xii05_fibonacci():
    """XII-05: cena powyżej 61.8% kanału → LONG (silny trend)."""
    n = NeuronFibonacci()
    w = {"CLOSE": 108, "DONCHIAN_UPPER": 110, "DONCHIAN_LOWER": 90, "CLOSE_PREV": 107}
    s = n.interpretuj(w)
    assert s.kierunek == "LONG"


def test_xii07_rsi_div_bear():
    """XII-07: cena rośnie ale RSI spada → niedźwiedzia dywergencja → SHORT."""
    n = NeuronRSIDiv()
    w = {"RSI_14": 60, "RSI_PREV": 70, "CLOSE": 105, "CLOSE_PREV": 100}
    s = n.interpretuj(w)
    assert s.kierunek == "SHORT"


def test_xii07_rsi_div_bull():
    """XII-07: cena spada ale RSI rośnie → bycza dywergencja → LONG."""
    n = NeuronRSIDiv()
    w = {"RSI_14": 40, "RSI_PREV": 30, "CLOSE": 95, "CLOSE_PREV": 100}
    s = n.interpretuj(w)
    assert s.kierunek == "LONG"


def test_x12_bb_squeeze():
    """X-12: wąskie wstęgi BB + cena w górnej połowie → LONG bias."""
    n = NeuronBBSqueeze()
    w = {"BB_UPPER": 101, "BB_LOWER": 99.5, "BB_MIDDLE": 100.2, "CLOSE": 100.8, "ATR_DEVIATION": 0.8}
    s = n.interpretuj(w)
    assert s.kierunek == "LONG"


def test_x12_bb_brak_squeeze():
    """X-12: szerokie wstęgi → NEUTRAL (brak ściśnięcia)."""
    n = NeuronBBSqueeze()
    w = {"BB_UPPER": 110, "BB_LOWER": 90, "BB_MIDDLE": 100, "CLOSE": 105, "ATR_DEVIATION": 1.5}
    assert n.interpretuj(w).kierunek == "NEUTRAL"


# ─── A-03 NeuronWashVol ────────────────────────────────────────────────────────

def test_a03_washvol_bearish():
    """A-03: wysoki wolumen + mała świeca + zamknięcie wyżej → dystrybucja → SHORT."""
    n = NeuronWashVol()
    w = {
        "VOLUME": 5000, "VOLUME_MA20": 1000,  # spike ×5
        "OPEN": 100.0, "HIGH": 100.5, "LOW": 99.8, "CLOSE": 100.3,  # mała świeca, c>o
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,  # zakres 20 → frakcja 0.035 < 0.4
    }
    s = n.interpretuj(w)
    assert s.kierunek == "SHORT", f"Dystrybucja powinna dać SHORT, dostałem {s.kierunek}"


def test_a03_washvol_bullish():
    """A-03: wysoki wolumen + mała świeca + zamknięcie niżej → akumulacja → LONG."""
    n = NeuronWashVol()
    w = {
        "VOLUME": 5000, "VOLUME_MA20": 1000,
        "OPEN": 100.3, "HIGH": 100.5, "LOW": 99.8, "CLOSE": 99.9,  # c<o
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,
    }
    s = n.interpretuj(w)
    assert s.kierunek == "LONG", f"Akumulacja powinna dać LONG, dostałem {s.kierunek}"


def test_a03_washvol_normalny_wolumen():
    """A-03: normalny wolumen → NEUTRAL (brak prania)."""
    n = NeuronWashVol()
    w = {
        "VOLUME": 1100, "VOLUME_MA20": 1000,  # spike ×1.1 — za mały
        "OPEN": 100.0, "HIGH": 100.2, "LOW": 99.9, "CLOSE": 100.1,
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,
    }
    assert n.interpretuj(w).kierunek == "NEUTRAL"


# ─── A-05 NeuronBartPattern ────────────────────────────────────────────────────

def test_a05_bart_bull_crash():
    """A-05: duży wzrost w PREV, ale CURRENT zamknął poniżej OPEN_PREV → SHORT."""
    n = NeuronBartPattern()
    # Poprzedni bar: rósł od 95 → 105 (ciało 10, kanał 20 → 50%)
    # Bieżący bar: zamknął na 94 (poniżej OPEN_PREV=95) → powrót
    w = {
        "CLOSE": 94.0, "OPEN_PREV": 95.0, "CLOSE_PREV": 105.0,
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,
    }
    s = n.interpretuj(w)
    assert s.kierunek == "SHORT", f"Bull Bart → SHORT, dostałem {s.kierunek}"


def test_a05_bart_bear_pump():
    """A-05: duży spadek w PREV, ale CURRENT zamknął powyżej OPEN_PREV → LONG."""
    n = NeuronBartPattern()
    w = {
        "CLOSE": 106.0, "OPEN_PREV": 105.0, "CLOSE_PREV": 95.0,
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,
    }
    s = n.interpretuj(w)
    assert s.kierunek == "LONG", f"Bear Bart → LONG, dostałem {s.kierunek}"


def test_a05_bart_brak_danych():
    """A-05: brak CLOSE_PREV → NEUTRAL."""
    n = NeuronBartPattern()
    assert n.interpretuj({"CLOSE": 100.0}).kierunek == "NEUTRAL"


# ─── XII-06 NeuronOBZone ──────────────────────────────────────────────────────

def test_xii06_ob_bullish():
    """XII-06: poprzedni bar bearish + current powyżej OPEN_PREV → bullish OB → LONG."""
    n = NeuronOBZone()
    # PREV: open=105, close=95 (bearish, ciało 10, kanał 20 → 50%)
    # CURRENT: close=107 > OPEN_PREV=105 → przebicie strefy OB
    w = {
        "CLOSE": 107.0, "OPEN_PREV": 105.0, "CLOSE_PREV": 95.0,
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,
    }
    s = n.interpretuj(w)
    assert s.kierunek == "LONG", f"Bullish OB → LONG, dostałem {s.kierunek}"


def test_xii06_ob_bearish():
    """XII-06: poprzedni bar bullish + current poniżej OPEN_PREV → bearish OB → SHORT."""
    n = NeuronOBZone()
    w = {
        "CLOSE": 93.0, "OPEN_PREV": 95.0, "CLOSE_PREV": 105.0,
        "DONCHIAN_UPPER": 110.0, "DONCHIAN_LOWER": 90.0,
    }
    s = n.interpretuj(w)
    assert s.kierunek == "SHORT", f"Bearish OB → SHORT, dostałem {s.kierunek}"


def test_xii06_ob_brak_danych():
    """XII-06: brak OPEN_PREV → NEUTRAL."""
    n = NeuronOBZone()
    assert n.interpretuj({"CLOSE": 100.0}).kierunek == "NEUTRAL"
