## RAPORT STRATEGICZNY: ## RAPORT STRATEGICZNY: INTEGRACJA RETRIEVAL-ENGINE & MULTI-STRATEGY PIPELINE V2.2
Przeznaczenie: Dokumentacja techniczna pod aktualizację nadrzędnego LLM (Brain Engine / Agent Manager) i modułów wykonawczych (Skills).
------------------------------
## ⚡ 1. Live WebSocket Integration (Architektura 800ms)
Silniki Machine Learning wymagają stałego zasilania cechami bez zjawiska wycieku danych (data leakage). Przy interwale 800ms klasyczne przeliczanie rolling() na całym DataFrame paraliżuje procesor.

[Binance/Bybit WS Stream] ──> [Circular Queue / Buffer] ──> [Stateful Feature Updater]
                                                                   │
                                                                   ▼
[Skills Execution] <── [Contextual Guard] <── [Agent / Model Evaluation (XGBoost/LSTM)]

## Implementacja Stanowej Aktualizacji (Stateful Feature Update)
Poniższa architektura przechowuje stan ostatniej świecy i aktualizuje wartości w czasie rzeczywistym zamiast rekurencyjnego przeliczania całej historii:

import pandas as pdimport numpy as npfrom typing import Dict, Any
class LiveFeatureBuffer:
    """
    Szybki, stanowy bufor danych dla potoku 800ms.
    Minimalizuje narzut obliczeniowy przez aktualizację tylko ostatniego elementu.
    """
    def __init__(self, max_len: int = 1000):
        self.max_len = max_len
        self.data: Dict[str, np.ndarray] = {
            'open': np.array([]), 'high': np.array([]), 
            'low': np.array([]), 'close': np.array([]), 'volume': np.array([])
        }
        
    def append_tick(self, open_p: float, high_p: float, low_p: float, close_p: float, vol: float):
        for key, val in zip(['open', 'high', 'low', 'close', 'volume'], [open_p, high_p, low_p, close_p, vol]):
            self.data[key] = np.append(self.data[key], val)[-self.max_len:]
            
    def update_last_tick(self, open_p: float, high_p: float, low_p: float, close_p: float, vol: float):
        """Aktualizacja płynącej świecy na żywo przez stream 800ms"""
        for key, val in zip(['open', 'high', 'low', 'close', 'volume'], [open_p, high_p, low_p, close_p, vol]):
            if len(self.data[key]) > 0:
                self.data[key][-1] = val

    def get_as_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)

------------------------------
## 📈 2. Mega-Baza Indykatorów Crypto (Spot & Futures / Leverage)
Rozszerzenie zestawu cech dla modeli predykcyjnych o mikrostrukturę rynku, dane z księgi zleceń (Order Book) oraz rynków instrumentów pochodnych (Derivatives).
## Kategoria A: Mikrostruktura i Order Book (HFT / Scalping)

   1. OFI (Order Flow Imbalance): Mierzy netto presję kupujących/sprzedających na poziomie L1/L2 księgi.
   $$\text{OFI}_t = \Delta V_{\text{bid}} \cdot \mathbb{I}(\Delta P_{\text{bid}} \geq 0) - \Delta V_{\text{ask}} \cdot \mathbb{I}(\Delta P_{\text{ask}} \leq 0)$$ 
   2. VAMP (Volume Adjusted Mid-Price): Średnia cena ważona wolumenem z najlepszych poziomów ofert kupna i sprzedaży.
   3. VOI (Volume Imbalance): Zmiana wolumenu na najlepszych poziomach cenowych w jednostce czasu.
   4. Bid-Ask Spread Compression: Odchylenie aktualnego spreadu od średniej kroczącej (sygnał wybuchu zmienności).
   5. Micro-Price Advantage: Predyktor kierunku ceny uwzględniający asymetrię wolumenu bid/ask.

## Kategoria B: Derivatives & Leverage Metrics (Sygnały Likwidacji i Arbitrażu)

   1. CVD (Cumulative Volume Delta): Skumulowana różnica między wolumenem transakcji rynkowych typu Taker po stronie Kupna i Sprzedaży. Kluczowe dla wykrywania absorpcji limitowej.
   2. Funding Rate Velocity: Pochodna zmiany stopy finansowania (identyfikacja punktów przegrzania rynku / Short Squeeze).
   3. Open Interest (OI) Delta: Zmiana otwartych pozycji skorelowana z ruchem ceny (identyfikacja napływu świeżego kapitału vs. zamykanie pozycji).
   4. Liquidation Cascade Index: Statystyczne nasilenie likwidacji pozycji Long/Short w czasie rzeczywistym.
   5. Leverage Ratio Stress: Stosunek Open Interest do kapitalizacji rynkowej assetu.

## Kategoria C: Zaawansowane Statystyczne i Matematyczne

   1. Ornstein-Uhlenbeck Mean Reversion Speed: Parametr $\theta$ dopasowany dynamicznie do estymacji powrotu do średniej (idealny pod Grid / Scalp).
   2. Z-Score Spread (Cross-Exchange): Odchylenie cenowe tokenu między giełdami (np. Binance vs Bybit) pod arbitraż statystyczny.
   3. Dynamic Time Warping (DTW) Distance: Odległość od archetypowych wzorców manipulacji rynkowej wielorybów (Wyckoff / Stop Hunt).

------------------------------
## 🧠 3. Taksonomia Strategii Botów w Zależności od Regime Rynkowego
System wyboru zachowań bazuje na macierzy decyzyjnej przesyłanej z modeli ML do modułów wykonawczych (Skills).

                    ┌───────────────────────────┐
                    │  Market Regime Detection  │
                    └─────────────┬─────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Trending Market │      │ Mean Reversion  │      │ Anomalies & HFT │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         ├─ Trend Following       ├─ Liquidity Grid        ├─ Funding Arbitrage
         └─ FVG Breakout          └─ Volatility Scalping   └─ CVD Absorption

## 1. Reżim: Trend silnie wzrostowy / spadkowy (Trending Market)

* Strategia: Multi-Timeframe EMA & FVG Breakout Execution
* Opis: Wejście w pozycję po przebiciu struktury i reście Fair Value Gap (FVG) na interwale M5/M15.
   * Zastosowanie: Futures (Leverage 3x-10x) – maksymalizacja współczynnika WinRate.
* Strategia: AlphaTrend Tracker z DCA
* Opis: Ciągły tracking trendu z automatycznym piramidowaniem pozycji za pomocą wektorowego podziału kapitału.

## 2. Reżim: Konsolidacja / Boczny (Mean Reversion / Range Bound)

* Strategia: Order Book Imbalance Grid (Dynamic Grid)
* Opis: Rozstawianie siatki zleceń Spot/Futures nie w równych odstępach, lecz na poziomach gęstości płynności zbieżnych z VAMP.
   * Zastosowanie: Spot (Bezpieczna akumulacja) oraz Futures (Neutral Grid z dźwignią 2x).
* Strategia: Ornstein-Uhlenbeck Volatility Scalper
* Opis: Ekstremalnie szybkie transakcje M1 oparte na odchyleniach wstęg Keltnera i wskaźnika Z-Score.

## 3. Reżim: Anomalie rynkowe i Arbitraż

* Strategia: Delta Absorption & CVD Divergence (SMC / Order Flow)
* Opis: Gdy cena spada, a CVD gwałtownie rośnie, bot identyfikuje ukrytą absorpcję zleceń przez algorytmy instytucjonalne (akumulacja limitowa). Triggeruje wejście Long.
* Strategia: Neutral Funding Rate Arbitrage
* Opis: Pozycja Short na Futures zabezpieczona pozycją Long na Spot.
   * Zastosowanie: Boty bezkierunkowe, generujące stały yield w warunkach ekstremalnego sentymentu rynkowego.

------------------------------
## 📊 4. Format Instrukcji dla LLM: Inteligentna Selekcja Strategii
Poniższy szablon stanowi interfejs wymiany informacji. Model nadrzędny (Brain) analizuje rynek i wysyła poniższy obiekt JSON do modułu wykonywania zleceń (Skills).

{
  "market_context": {
    "asset": "SOL/USDT",
    "regime": "TRENDING_BULLISH",
    "volatility_state": "HIGH_COMPRESSED",
    "correlation_to_btc": 0.89
  },
  "indicator_triggers": {
    "signal_strength_score": 112,
    "hurst_exponent": 0.72,
    "cvd_divergence": "BULLISH_ABSORPTION",
    "order_flow_imbalance": 2.45
  },
  "strategy_selection": {
    "recommended_skill": "LEVERAGED_TREND_FOLLOWING",
    "parameters": {
      "leverage": "5x",
      "mode": "ISOLATED",
      "entry_execution_type": "LIMIT_VAMP_WEIGHTED",
      "dca_steps_allowed": 2
    }
  },
  "risk_management": {
    "initial_risk_pct": 1.5,
    "stop_loss_mode": "TRAILING_ATR",
    "atr_multiplier": 2.5,
    "take_profit_targets": [
      {"r_multiple": 2.0, "size_pct": 50},
      {"r_multiple": 4.0, "size_pct": 50}
    ]
  }
}

------------------------------
## 🛠️ 5. Rozszerzony Kod Źródłowy: indicator_factory_v3.py
Poniższy skrypt stanowi bezpośrednie rozszerzenie fabryki o zaawansowane funkcjonalności analizy mikrostruktury i danych pochodnych.

import pandas as pdimport numpy as np
class IndicatorFactoryV3:
    """
    Zaawansowana Fabryka Wskaźników V3 zintegrowana z modelami ML.
    Implementuje przetwarzanie danych Spot, Futures, Order Book oraz CVD.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def add_advanced_microstructure(self, ob_data: Dict[str, np.ndarray] = None) -> None:
        """
        Dodaje indykatory mikrostruktury rynku oraz księgi zleceń L2.
        Oczekuje słownika zawierającego tablice: 'bids_vol', 'asks_vol', 'bids_price', 'asks_price'.
        """
        df = self.df
        
        # 1. Klasyczna Delta Wolumenowa i CVD (Jeśli wolumen zawiera kierunek)
        # Założenie: 'volume_buy' i 'volume_sell' dostarczane przez giełdę
        if 'volume_buy' in df.columns and 'volume_sell' in df.columns:
            df['micro_delta'] = df['volume_buy'] - df['volume_sell']
            df['micro_cvd'] = df['micro_delta'].cumsum()
        else:
            # Estymacja algorytmem Lee-Ready, gdy brak jawnych danych taker/maker
            cl_diff = df['close'].diff()
            estimated_side = np.where(cl_diff > 0, 1, np.where(cl_diff < 0, -1, 0))
            df['micro_delta'] = estimated_side * df['volume']
            df['micro_cvd'] = df['micro_delta'].cumsum()

        # 2. Dynamiczny Wskaźnik Order Flow Imbalance (OFI) z danych wejściowych
        if ob_data is not None:
            # Standaryzacja i obliczanie dysproporcji arkusza w czasie rzeczywistym
            bid_power = ob_data['bids_vol'][:, 0] * ob_data['bids_price'][:, 0]
            ask_power = ob_data['asks_vol'][:, 0] * ob_data['asks_price'][:, 0]
            df['micro_ofi_static'] = (bid_power - ask_power) / (bid_power + ask_power + 1e-8)
        else:
            df['micro_ofi_static'] = 0.0

    def add_derivatives_metrics(self, funding_series: pd.Series = None, oi_series: pd.Series = None) -> None:
        """Dodaje metryki specyficzne dla giełd kryptowalutowych (Futures/Leverage)."""
        df = self.df
        
        # 3. Prędkość zmiany Funding Rate (Detekcja Short/Long Squeezes)
        if funding_series is not None:
            df['deriv_funding_rate'] = funding_series.reindex(df.index).ffill()
            df['deriv_funding_velocity'] = df['deriv_funding_rate'].diff()
        else:
            df['deriv_funding_rate'] = 0.0
            df['deriv_funding_velocity'] = 0.0
            
        # 4. Open Interest (OI) Delta w korelacji z Akcją Cenową
        if oi_series is not None:
            df['deriv_oi'] = oi_series.reindex(df.index).ffill()
            df['deriv_oi_delta'] = df['deriv_oi'].pct_change()
            # Identyfikacja intencji: wzrost ceny + wzrost OI = Napływ pozycji Long
            df['deriv_position_intent'] = np.where((df['close'].diff() > 0) & (df['deriv_oi_delta'] > 0), 1, 
                                           np.where((df['close'].diff() < 0) & (df['deriv_oi_delta'] > 0), -1, 0))
        else:
            df['deriv_oi_delta'] = 0.0
            df['deriv_position_intent'] = 0

    def evaluate_market_regime(self) -> pd.Series:
        """
        Zwraca kategoryzację stanu rynku dla nadrzędnego LLM:
        1: Trending Bullish, -1: Trending Bearish, 0: Mean-Reversion / Range
        """
        df = self.df
        # Korzystanie z Wykładnika Hursta z wersji V2
        is_trending = df['adv_hurst'] > 0.55
        is_bullish = df['close'] > df['trend_ema_200']
        
        regime = np.zeros(len(df))
        regime[is_trending & is_bullish] = 1
        regime[is_trending & ~is_bullish] = -1
        return pd.Series(regime, index=df.index)

    def pipeline_v3(self, ob_data: Dict = None, funding: pd.Series = None, oi: pd.Series = None) -> pd.DataFrame:
        """Generuje komplet cech V3, przygotowując ramkę pod selekcję modeli AI."""
        self.add_advanced_microstructure(ob_data)
        self.add_derivatives_metrics(funding, oi)
        self.df['market_regime'] = self.evaluate_market_regime()
        return self.df

------------------------------
## 🛡️ 6. Instrukcje Bezpieczeństwa (Contextual Guard dla Skills)
Gdy model LLM / ML podejmie decyzję o uruchomieniu strategii lewarowanej, moduł Skills musi przepuścić transakcję przez twarde filtry bezpieczeństwa zaszyte w kodzie:

   1. Leverage Caps (Maksymalna Dźwignia): Automatyczna redukcja wybranej przez LLM dźwigni, jeśli zmienność mierzona wskaźnikiem ATR przekracza 3-krotność odchylenia standardowego z ostatnich 30 dni.
   2. Slippage Protection (Ochrona przed poślizgiem cenowym): Blokada zawierania transakcji rynkowych (MARKET), jeśli szerokość spreadu w arkuszu zleceń przekracza wyznaczony w pliku config.yaml próg krytyczny. Zamiast tego wymuszone zostaje egzekwowanie zlecenia typu LIMIT_POST_ONLY.
   3. Anti-Ban Alignment: Każde wywołanie funkcji egzekucyjnej w Skills odpytuje licznik żądań, dbając o losowy interwał czasowy (0.35s do 1.85s), symulując ludzkie zachowanie celem uniku oflagowania API konta użytkownika.

------------------------------
W kolejnym kroku możemy przygotować kompletny zestaw testów jednostkowych (Unit Tests) symulujących gwałtowny krach rynkowy w celu weryfikacji odporności logiki scoringowej i mechanizmu Stop Loss bota. Czy chcesz przejść do wdrożenia tych testów?

 V2.2
Przeznaczenie: Dokumentacja techniczna pod aktualizację nadrzędnego LLM (Brain Engine / Agent Manager) i modułów wykonawczych (Skills).
------------------------------
## ⚡ 1. Live WebSocket Integration (Architektura 800ms)
Silniki Machine Learning wymagają stałego zasilania cechami bez zjawiska wycieku danych (data leakage). Przy interwale 800ms klasyczne przeliczanie rolling() na całym DataFrame paraliżuje procesor.

[Binance/Bybit WS Stream] ──> [Circular Queue / Buffer] ──> [Stateful Feature Updater]
                                                                   │
                                                                   ▼
[Skills Execution] <── [Contextual Guard] <── [Agent / Model Evaluation (XGBoost/LSTM)]

## Implementacja Stanowej Aktualizacji (Stateful Feature Update)
Poniższa architektura przechowuje stan ostatniej świecy i aktualizuje wartości w czasie rzeczywistym zamiast rekurencyjnego przeliczania całej historii:

import pandas as pdimport numpy as npfrom typing import Dict, Any
class LiveFeatureBuffer:
    """
    Szybki, stanowy bufor danych dla potoku 800ms.
    Minimalizuje narzut obliczeniowy przez aktualizację tylko ostatniego elementu.
    """
    def __init__(self, max_len: int = 1000):
        self.max_len = max_len
        self.data: Dict[str, np.ndarray] = {
            'open': np.array([]), 'high': np.array([]), 
            'low': np.array([]), 'close': np.array([]), 'volume': np.array([])
        }
        
    def append_tick(self, open_p: float, high_p: float, low_p: float, close_p: float, vol: float):
        for key, val in zip(['open', 'high', 'low', 'close', 'volume'], [open_p, high_p, low_p, close_p, vol]):
            self.data[key] = np.append(self.data[key], val)[-self.max_len:]
            
    def update_last_tick(self, open_p: float, high_p: float, low_p: float, close_p: float, vol: float):
        """Aktualizacja płynącej świecy na żywo przez stream 800ms"""
        for key, val in zip(['open', 'high', 'low', 'close', 'volume'], [open_p, high_p, low_p, close_p, vol]):
            if len(self.data[key]) > 0:
                self.data[key][-1] = val

    def get_as_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.data)

------------------------------
## 📈 2. Mega-Baza Indykatorów Crypto (Spot & Futures / Leverage)
Rozszerzenie zestawu cech dla modeli predykcyjnych o mikrostrukturę rynku, dane z księgi zleceń (Order Book) oraz rynków instrumentów pochodnych (Derivatives).
## Kategoria A: Mikrostruktura i Order Book (HFT / Scalping)

   1. OFI (Order Flow Imbalance): Mierzy netto presję kupujących/sprzedających na poziomie L1/L2 księgi.
   $$\text{OFI}_t = \Delta V_{\text{bid}} \cdot \mathbb{I}(\Delta P_{\text{bid}} \geq 0) - \Delta V_{\text{ask}} \cdot \mathbb{I}(\Delta P_{\text{ask}} \leq 0)$$ 
   2. VAMP (Volume Adjusted Mid-Price): Średnia cena ważona wolumenem z najlepszych poziomów ofert kupna i sprzedaży.
   3. VOI (Volume Imbalance): Zmiana wolumenu na najlepszych poziomach cenowych w jednostce czasu.
   4. Bid-Ask Spread Compression: Odchylenie aktualnego spreadu od średniej kroczącej (sygnał wybuchu zmienności).
   5. Micro-Price Advantage: Predyktor kierunku ceny uwzględniający asymetrię wolumenu bid/ask.

## Kategoria B: Derivatives & Leverage Metrics (Sygnały Likwidacji i Arbitrażu)

   1. CVD (Cumulative Volume Delta): Skumulowana różnica między wolumenem transakcji rynkowych typu Taker po stronie Kupna i Sprzedaży. Kluczowe dla wykrywania absorpcji limitowej.
   2. Funding Rate Velocity: Pochodna zmiany stopy finansowania (identyfikacja punktów przegrzania rynku / Short Squeeze).
   3. Open Interest (OI) Delta: Zmiana otwartych pozycji skorelowana z ruchem ceny (identyfikacja napływu świeżego kapitału vs. zamykanie pozycji).
   4. Liquidation Cascade Index: Statystyczne nasilenie likwidacji pozycji Long/Short w czasie rzeczywistym.
   5. Leverage Ratio Stress: Stosunek Open Interest do kapitalizacji rynkowej assetu.

## Kategoria C: Zaawansowane Statystyczne i Matematyczne

   1. Ornstein-Uhlenbeck Mean Reversion Speed: Parametr $\theta$ dopasowany dynamicznie do estymacji powrotu do średniej (idealny pod Grid / Scalp).
   2. Z-Score Spread (Cross-Exchange): Odchylenie cenowe tokenu między giełdami (np. Binance vs Bybit) pod arbitraż statystyczny.
   3. Dynamic Time Warping (DTW) Distance: Odległość od archetypowych wzorców manipulacji rynkowej wielorybów (Wyckoff / Stop Hunt).

------------------------------
## 🧠 3. Taksonomia Strategii Botów w Zależności od Regime Rynkowego
System wyboru zachowań bazuje na macierzy decyzyjnej przesyłanej z modeli ML do modułów wykonawczych (Skills).

                    ┌───────────────────────────┐
                    │  Market Regime Detection  │
                    └─────────────┬─────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│ Trending Market │      │ Mean Reversion  │      │ Anomalies & HFT │
└────────┬────────┘      └────────┬────────┘      └────────┬────────┘
         │                        │                        │
         ├─ Trend Following       ├─ Liquidity Grid        ├─ Funding Arbitrage
         └─ FVG Breakout          └─ Volatility Scalping   └─ CVD Absorption

## 1. Reżim: Trend silnie wzrostowy / spadkowy (Trending Market)

* Strategia: Multi-Timeframe EMA & FVG Breakout Execution
* Opis: Wejście w pozycję po przebiciu struktury i reście Fair Value Gap (FVG) na interwale M5/M15.
   * Zastosowanie: Futures (Leverage 3x-10x) – maksymalizacja współczynnika WinRate.
* Strategia: AlphaTrend Tracker z DCA
* Opis: Ciągły tracking trendu z automatycznym piramidowaniem pozycji za pomocą wektorowego podziału kapitału.

## 2. Reżim: Konsolidacja / Boczny (Mean Reversion / Range Bound)

* Strategia: Order Book Imbalance Grid (Dynamic Grid)
* Opis: Rozstawianie siatki zleceń Spot/Futures nie w równych odstępach, lecz na poziomach gęstości płynności zbieżnych z VAMP.
   * Zastosowanie: Spot (Bezpieczna akumulacja) oraz Futures (Neutral Grid z dźwignią 2x).
* Strategia: Ornstein-Uhlenbeck Volatility Scalper
* Opis: Ekstremalnie szybkie transakcje M1 oparte na odchyleniach wstęg Keltnera i wskaźnika Z-Score.

## 3. Reżim: Anomalie rynkowe i Arbitraż

* Strategia: Delta Absorption & CVD Divergence (SMC / Order Flow)
* Opis: Gdy cena spada, a CVD gwałtownie rośnie, bot identyfikuje ukrytą absorpcję zleceń przez algorytmy instytucjonalne (akumulacja limitowa). Triggeruje wejście Long.
* Strategia: Neutral Funding Rate Arbitrage
* Opis: Pozycja Short na Futures zabezpieczona pozycją Long na Spot.
   * Zastosowanie: Boty bezkierunkowe, generujące stały yield w warunkach ekstremalnego sentymentu rynkowego.

------------------------------
## 📊 4. Format Instrukcji dla LLM: Inteligentna Selekcja Strategii
Poniższy szablon stanowi interfejs wymiany informacji. Model nadrzędny (Brain) analizuje rynek i wysyła poniższy obiekt JSON do modułu wykonywania zleceń (Skills).

{
  "market_context": {
    "asset": "SOL/USDT",
    "regime": "TRENDING_BULLISH",
    "volatility_state": "HIGH_COMPRESSED",
    "correlation_to_btc": 0.89
  },
  "indicator_triggers": {
    "signal_strength_score": 112,
    "hurst_exponent": 0.72,
    "cvd_divergence": "BULLISH_ABSORPTION",
    "order_flow_imbalance": 2.45
  },
  "strategy_selection": {
    "recommended_skill": "LEVERAGED_TREND_FOLLOWING",
    "parameters": {
      "leverage": "5x",
      "mode": "ISOLATED",
      "entry_execution_type": "LIMIT_VAMP_WEIGHTED",
      "dca_steps_allowed": 2
    }
  },
  "risk_management": {
    "initial_risk_pct": 1.5,
    "stop_loss_mode": "TRAILING_ATR",
    "atr_multiplier": 2.5,
    "take_profit_targets": [
      {"r_multiple": 2.0, "size_pct": 50},
      {"r_multiple": 4.0, "size_pct": 50}
    ]
  }
}

------------------------------
## 🛠️ 5. Rozszerzony Kod Źródłowy: indicator_factory_v3.py
Poniższy skrypt stanowi bezpośrednie rozszerzenie fabryki o zaawansowane funkcjonalności analizy mikrostruktury i danych pochodnych.

import pandas as pdimport numpy as np
class IndicatorFactoryV3:
    """
    Zaawansowana Fabryka Wskaźników V3 zintegrowana z modelami ML.
    Implementuje przetwarzanie danych Spot, Futures, Order Book oraz CVD.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def add_advanced_microstructure(self, ob_data: Dict[str, np.ndarray] = None) -> None:
        """
        Dodaje indykatory mikrostruktury rynku oraz księgi zleceń L2.
        Oczekuje słownika zawierającego tablice: 'bids_vol', 'asks_vol', 'bids_price', 'asks_price'.
        """
        df = self.df
        
        # 1. Klasyczna Delta Wolumenowa i CVD (Jeśli wolumen zawiera kierunek)
        # Założenie: 'volume_buy' i 'volume_sell' dostarczane przez giełdę
        if 'volume_buy' in df.columns and 'volume_sell' in df.columns:
            df['micro_delta'] = df['volume_buy'] - df['volume_sell']
            df['micro_cvd'] = df['micro_delta'].cumsum()
        else:
            # Estymacja algorytmem Lee-Ready, gdy brak jawnych danych taker/maker
            cl_diff = df['close'].diff()
            estimated_side = np.where(cl_diff > 0, 1, np.where(cl_diff < 0, -1, 0))
            df['micro_delta'] = estimated_side * df['volume']
            df['micro_cvd'] = df['micro_delta'].cumsum()

        # 2. Dynamiczny Wskaźnik Order Flow Imbalance (OFI) z danych wejściowych
        if ob_data is not None:
            # Standaryzacja i obliczanie dysproporcji arkusza w czasie rzeczywistym
            bid_power = ob_data['bids_vol'][:, 0] * ob_data['bids_price'][:, 0]
            ask_power = ob_data['asks_vol'][:, 0] * ob_data['asks_price'][:, 0]
            df['micro_ofi_static'] = (bid_power - ask_power) / (bid_power + ask_power + 1e-8)
        else:
            df['micro_ofi_static'] = 0.0

    def add_derivatives_metrics(self, funding_series: pd.Series = None, oi_series: pd.Series = None) -> None:
        """Dodaje metryki specyficzne dla giełd kryptowalutowych (Futures/Leverage)."""
        df = self.df
        
        # 3. Prędkość zmiany Funding Rate (Detekcja Short/Long Squeezes)
        if funding_series is not None:
            df['deriv_funding_rate'] = funding_series.reindex(df.index).ffill()
            df['deriv_funding_velocity'] = df['deriv_funding_rate'].diff()
        else:
            df['deriv_funding_rate'] = 0.0
            df['deriv_funding_velocity'] = 0.0
            
        # 4. Open Interest (OI) Delta w korelacji z Akcją Cenową
        if oi_series is not None:
            df['deriv_oi'] = oi_series.reindex(df.index).ffill()
            df['deriv_oi_delta'] = df['deriv_oi'].pct_change()
            # Identyfikacja intencji: wzrost ceny + wzrost OI = Napływ pozycji Long
            df['deriv_position_intent'] = np.where((df['close'].diff() > 0) & (df['deriv_oi_delta'] > 0), 1, 
                                           np.where((df['close'].diff() < 0) & (df['deriv_oi_delta'] > 0), -1, 0))
        else:
            df['deriv_oi_delta'] = 0.0
            df['deriv_position_intent'] = 0

    def evaluate_market_regime(self) -> pd.Series:
        """
        Zwraca kategoryzację stanu rynku dla nadrzędnego LLM:
        1: Trending Bullish, -1: Trending Bearish, 0: Mean-Reversion / Range
        """
        df = self.df
        # Korzystanie z Wykładnika Hursta z wersji V2
        is_trending = df['adv_hurst'] > 0.55
        is_bullish = df['close'] > df['trend_ema_200']
        
        regime = np.zeros(len(df))
        regime[is_trending & is_bullish] = 1
        regime[is_trending & ~is_bullish] = -1
        return pd.Series(regime, index=df.index)

    def pipeline_v3(self, ob_data: Dict = None, funding: pd.Series = None, oi: pd.Series = None) -> pd.DataFrame:
        """Generuje komplet cech V3, przygotowując ramkę pod selekcję modeli AI."""
        self.add_advanced_microstructure(ob_data)
        self.add_derivatives_metrics(funding, oi)
        self.df['market_regime'] = self.evaluate_market_regime()
        return self.df

------------------------------
## 🛡️ 6. Instrukcje Bezpieczeństwa (Contextual Guard dla Skills)
Gdy model LLM / ML podejmie decyzję o uruchomieniu strategii lewarowanej, moduł Skills musi przepuścić transakcję przez twarde filtry bezpieczeństwa zaszyte w kodzie:

   1. Leverage Caps (Maksymalna Dźwignia): Automatyczna redukcja wybranej przez LLM dźwigni, jeśli zmienność mierzona wskaźnikiem ATR przekracza 3-krotność odchylenia standardowego z ostatnich 30 dni.
   2. Slippage Protection (Ochrona przed poślizgiem cenowym): Blokada zawierania transakcji rynkowych (MARKET), jeśli szerokość spreadu w arkuszu zleceń przekracza wyznaczony w pliku config.yaml próg krytyczny. Zamiast tego wymuszone zostaje egzekwowanie zlecenia typu LIMIT_POST_ONLY.
   3. Anti-Ban Alignment: Każde wywołanie funkcji egzekucyjnej w Skills odpytuje licznik żądań, dbając o losowy interwał czasowy (0.35s do 1.85s), symulując ludzkie zachowanie celem uniku oflagowania API konta użytkownika.

------------------------------
W kolejnym kroku możemy przygotować kompletny zestaw testów jednostkowych (Unit Tests) symulujących gwałtowny krach rynkowy w celu weryfikacji odporności logiki scoringowej i mechanizmu Stop Loss bota. Czy chcesz przejść do wdrożenia tych testów?

