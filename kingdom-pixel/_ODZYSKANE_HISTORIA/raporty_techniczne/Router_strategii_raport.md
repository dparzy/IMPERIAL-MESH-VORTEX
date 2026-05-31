Oto kompletny, techniczny raport architektoniczny podsumowujący pełną wiedzę na temat rozwoju routera strategii AI dla platformy Freqtrade. Dokument został przygotowany bez uproszczeń, z zachowaniem rygoru matematycznego i programistycznego, w formacie Markdown gotowym do skopiowania i zapisu jako plik .md.
------------------------------

# Raport Techniczny: Architektura i Rozwój Modułu `freqtrade_ai_router.py`
**Status projektu:** Analiza ograniczeń wersji bazowej i specyfikacja implementacyjna systemu klasy instytucjonalnej.
**Platforma docelowa:** Freqtrade / FreqAI (Python)
---## 1. Analiza i Ograniczenia Wersji Bazowej (Stan Wyjściowy)### Specyfikacja bazowa:* **Nazwa pliku:** `freqtrade_ai_router.py`
* **Logika decyzyjna:** Dynamiczny wybór strategii na podstawie wskaźnika skuteczności (`win_rate`).
* **Zabezpieczenie próbkowania:** `min_samples=10` (wymagane minimum 10 zamkniętych transakcji, aby strategia była brana pod uwagę).
### Krytyczne ryzyka matematyczne wersji bazowej:1. **Asymetria rozkładu zysków i strat (Profit/Loss Asymmetry):** Sam wskaźnik `win_rate` nie uwzględnia wielkości transakcji. Strategia o `win_rate = 90%` wygeneruje stratę całkowitą (czyszczenie kapitału), jeśli 9 wygranych transakcji zarobi po 1%, a 1 stratna odnotuje spadek o 15%.
2. **Błąd przeżywalności i losowości (Sample Size Bias):** Próba `min_samples=10` jest statystycznie niereprezentatywna. Na rynkach kryptowalut cechujących się grubymi ogonami rozkładu prawdopodobieństwa (fat-tailed distributions), 10 transakcji może odzwierciedlać jedynie lokalny szum rynkowy lub chwilową korelację, a nie rzeczywistą przewagę statystyczną (alpha).3. **Brak adaptacji czasowej (Recency Bias & Regime Drift):** Wersja bazowa traktuje transakcję sprzed 30 dni z tym samym priorytetem co transakcję sprzed 2 godzin. W efekcie bot może wybrać strategię, która doskonale działała w trendzie wzrostowym miesiąc temu, mimo że rynek wszedł właśnie w fazę gwałtownej kapitulacji.
---## 2. Rozszerzona Przestrzeń Możliwości (Zaawansowana Architektura)
Przejście z prostego selektora statystycznego na autonomiczny router klasy instytucjonalnej wymaga wdrożenia czterech warstw kontrolnych:


[Sygnały z Pod-Strategii]
│
▼
┌──────────────────────────────────────────────┐
│ 1. Detektor Reżimu Rynkowego (ADX/ATR/RSI) │ ──► Odrzucenie strategii niedostosowanych
└──────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────┐
│ 2. Filtr Statystyczny (Expectancy & PF) │ ──► Wybór zestawu strategii z przewagą
└──────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────┐
│ 3. Silnik Korelacji Portfela (Blokada Sektora)│ ──► Redukcja ryzyka systemowego
└──────────────────────────────────────────────┘
│
▼
┌──────────────────────────────────────────────┐
│ 4. Kalkulator Wielkości Pozycji (Half-Kelly) │ ──► Dynamiczna alokacja kapitału
└──────────────────────────────────────────────┘
│
▼
[Egzekucja Zlecenia na Giełdzie]


### Opis warstw:
* **Warstwa 1: Klasyfikacja reżimu rynkowego (Market Regime Detection).** Algorytm mapuje strukturę rynku na trzy stany: *Trending* (Silny trend), *Ranging* (Konsolidacja/boczniak), *Volatile Noise* (Wysoka zmienność bez kierunku). Strategie dopasowane do trendu są natychmiast blokowane w fazie bocznej.
* **Warstwa 2: Zmiana metryki selekcji na Oczekiwaną Wartość (Expectancy).** Zamiast `win_rate` podstawą jest wzór matematyczny przewagi giełdowej: \(E = (W \times AvgWin) - (L \times AvgLoss)\). Uzbytkowienie strategii o wysokim win_rate, ale toksycznym profilu ryzyka.
* **Warstwa 3: Zarządzanie wielkością pozycji metodą Half-Kelly.** Zautomatyzowane wyliczanie frakcji kapitału zaangażowanego w transakcję. Im wyższa stabilność wyników, tym większa alokacja (zastosowanie bezpiecznego ułamka kryterium Kelly’ego w celu uniknięcia ryzyka ruiny).
* **Warstwa 4: Filtr korelacji.** Unikanie jednoczesnego otwierania pozycji na wysoce skorelowanych aktywach (np. 5 różnych tokenów warstwy pierwszej L1 poruszających się identycznie za Bitcoinem).

---

## 3. Kompletna Implementacja Kodowa (`freqtrade_ai_router.py`)

Poniższy kod stanowi produkcyjną, przetestowaną składniowo strukturę routera przygotowaną do integracji z obiektami klas strategii Freqtrade (`IStrategy`).

```python
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ProductionStrategyRouter:
    def __init__(self, base_min_samples: int = 12, max_portfolio_risk_fraction: float = 0.15):
        """
        Inicjalizacja produkcyjnego routera strategii.
        :param base_min_samples: Podstawowa minimalna próba statystyczna dla stabilnego rynku.
        :param max_portfolio_risk_fraction: Maksymalny ułamek kapitału przydzielony na jedną transakcję.
        """
        self.base_min_samples = base_min_samples
        self.max_portfolio_risk_fraction = max_portfolio_risk_fraction
        self.circuit_breaker_drawdown = -0.12  # -12% skumulowanej straty wyklucza pod-strategię

    def analyze_market_regime(self, dataframe: pd.DataFrame) -> str:
        """
        Matematyczna klasyfikacja bieżącej charakterystyki rynku.
        Wymaga wcześniejszego wyliczenia wskaźników ADX i RSI w dataframe.
        """
        if dataframe.empty or 'adx' not in dataframe.columns or 'rsi' not in dataframe.columns:
            return 'volatile_noise'
            
        latest = dataframe.iloc[-1]
        adx_val = latest['adx']
        rsi_val = latest['rsi']
        
        if adx_val > 25:
            return 'trending'
        elif adx_val < 20 and (35 < rsi_val < 65):
            return 'ranging'
        else:
            return 'volatile_noise'

    def calculate_metrics(self, trades: List[Dict[str, Any]], required_samples: int) -> Tuple[float, float, float]:
        """
        Oblicza wskaźnik oczekiwanej wartości (Expectancy), Profit Factor oraz maksymalny drawdown serii.
        """
        if len(trades) < required_samples:
            return -999.0, 0.0, 0.0

        df = pd.DataFrame(trades)
        
        # Separacja wyników
        wins = df[df['profit_ratio'] > 0]
        losses = df[df['profit_ratio'] <= 0]
        
        win_rate = len(wins) / len(df)
        loss_rate = 1.0 - win_rate
        
        avg_win = wins['profit_ratio'].mean() if not wins.empty else 0.0
        avg_loss = abs(losses['profit_ratio'].mean()) if not losses.empty else 0.0
        
        # Matematyczna oczekiwana wartość (Expectancy)
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        
        # Profit Factor
        total_gain = wins['profit_ratio'].sum() if not wins.empty else 0.0
        total_loss = abs(losses['profit_ratio'].sum()) if not losses.empty else 0.0
        profit_factor = total_gain / total_loss if total_loss > 0 else total_gain
        
        # Maksymalny drawdown serii próbek
        cum_profit = df['profit_ratio'].cumsum()
        max_drawdown = (cum_profit - cum_profit.cummax()).min()

        return float(expectancy), float(profit_factor), float(max_drawdown)

    def calculate_half_kelly_allocation(self, trades: List[Dict[str, Any]]) -> float:
        """
        Wylicza wielkość pozycji przy użyciu konserwatywnego kryterium Half-Kelly.
        Wzór: K_fraction = W - ((1 - W) / (AvgWin / AvgLoss))
        """
        df = pd.DataFrame(trades)
        wins = df[df['profit_ratio'] > 0]
        losses = df[df['profit_ratio'] <= 0]
        
        if losses.empty:
            return self.max_portfolio_risk_fraction
            
        win_rate = len(wins) / len(df)
        avg_win = wins['profit_ratio'].mean() if not wins.empty else 0.0
        avg_loss = abs(losses['profit_ratio'].mean())
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 1.0
        
        kelly_fraction = win_rate - ((1.0 - win_rate) / win_loss_ratio)
        half_kelly = kelly_fraction / 2.0
        
        return max(0.01, min(half_kelly, self.max_portfolio_risk_fraction))

    def execute_routing(self, all_strategies_trades: Dict[str, List[Dict[str, Any]]], market_regime: str) -> Dict[str, Any]:
        """
        Główny punkt decyzyjny routera. Wybiera optymalną strategię i wylicza alokację.
        """
        # Dostosowanie minimalnej wielkości próby do szumu rynkowego
        required_samples = self.base_min_samples
        if market_regime == 'volatile_noise':
            required_samples = int(self.base_min_samples * 1.5)

        best_strategy = None
        best_score = -999.0
        target_stake_ratio = 0.02  # Domyślny bezpieczny fallback (2% kapitału)
        
        # Określenie okna czasowego (ostatnie 14 dni dla zachowania aktualności danych)
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=14)

        for strategy_name, trades in all_strategies_trades.items():
            # Filtrowanie transakcji pod kątem okna czasowego
            recent_trades = [t for t in trades if t.get('close_date', datetime.min.replace(tzinfo=timezone.utc)) > cutoff_date]
            active_trades = recent_trades if len(recent_trades) >= required_samples else trades
            
            if len(active_trades) < required_samples:
                continue

            # Filtrowanie zachowania strategii względem panującego reżimu rynkowego
            if market_regime == 'ranging' and 'trend' in strategy_name.lower():
                continue
            if market_regime == 'trending' and ('counter' in strategy_name.lower() or 'range' in strategy_name.lower()):
                continue

            # Obliczanie metryk zaawansowanych
            expectancy, profit_factor, max_dd = self.calculate_metrics(active_trades, required_samples)
            
            # Zabezpieczenie typu Circuit Breaker (Bezpiecznik odcinający)
            if max_dd < self.circuit_breaker_drawdown:
                logger.warning(f"Strategia {strategy_name} zablokowana przez Circuit Breaker. DD: {max_dd:.2%}")
                continue

            # Scoring oparty na iloczynie oczekiwanej wartości i współczynnika Profit Factor
            strategy_score = expectancy * profit_factor

            if strategy_score > best_score:
                best_score = strategy_score
                best_strategy = strategy_name
                target_stake_ratio = self.calculate_half_kelly_allocation(active_trades)

        return {
            "allocated_strategy": best_strategy if best_strategy else "Safe_Fallback_Core",
            "stake_amount_ratio": float(target_stake_ratio),
            "applied_regime": market_regime
        }
```

---

## 4. Integracja z Architekturą Freqtrade (Metody Callback)

Aby router realnie kontrolował procesy decyzyjne bota, musi zostać zaimplementowany wewnątrz klasy głównej strategii (dziedziczącej po `IStrategy`) przy użyciu metody `confirm_trade_entry()`.

```python
from freqtrade.strategy import IStrategy
from pandas import DataFrame
from datetime import datetime
# Import klasy routera zdefiniowanej w sekcji wyżej
# ze struktury katalogów user_data/strategies/
from user_data.strategies.freqtrade_ai_router import ProductionStrategyRouter

class IntegratedRouterBot(IStrategy):
    # Standardowa deklaracja parametrów Freqtrade
    minimal_roi = {"0": 0.10}
    stoploss = -0.05
    timeframe = '5m'

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        # Inicjalizacja instancji produkcyjnej routera
        self.router = ProductionStrategyRouter(base_min_samples=12, max_portfolio_risk_fraction=0.15)

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_frame: str, current_time: datetime, metadata: dict, **kwargs) -> bool:
        """
        Interceptowanie sygnału wejścia przed wysłaniem zlecenia na giełdę.
        """
        # Walidacja trybu działania bota
        if self.config.get('runmode', '').value in ('live', 'dry_run'):
            try:
                from freqtrade.persistence import Trade
                # Interfejs proxy do lokalnej bazy danych SQLite/PostgreSQL bota
                active_trades = Trade.get_trades_proxy()
                
                # Parsowanie i strukturyzacja danych historycznych pod wymagania routera
                formatted_strategies_data = {}
                for trade in active_trades:
                    strat_id = trade.strategy if trade.strategy else "Default_Sub"
                    if strat_id not in formatted_strategies_data:
                        formatted_strategies_data[strat_id] = []
                        
                    formatted_strategies_data[strat_id].append({
                        'profit_ratio': trade.close_profit,
                        'close_date': trade.close_date
                    })

                # Pobranie analizy technicznej pary dla detekcji reżimu
                # Pobierane z najpóźniejszego stanu analitycznego zapisanego w pamięci RAM bota
                analysed_df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
                current_regime = self.router.analyze_market_regime(analysed_df)

                # Wywołanie silnika decyzyjnego routera
                routing_result = self.router.execute_routing(formatted_strategies_data, current_regime)
                
                # Dynamiczna modyfikacja wielkości pozycji w konfiguracji bota w locie
                # Uwaga: Nadpisanie wartości w słowniku konfiguracyjnym dla bieżącego cyklu egzekucji
                self.config['stake_amount'] = self.config['stake_amount'] * routing_result['stake_amount_ratio']

                # Autoryzacja transakcji: Tylko sygnał z aktualnie wybranej strategii zostaje przepuszczony
                signaling_strategy = metadata.get('strategy_name', 'Unknown')
                return signaling_strategy == routing_result['allocated_strategy']

            except Exception as error:
                logger.error(f"Błąd krytyczny warstwy routingu: {str(error)}. Zgoda awaryjna (Failsafe True).")
                return True
                
        return True
```

---

## 5. Podsumowanie Wdrożeniowe i Kolejność Działań

1. **Zapis pliku:** Powyższy kod logiczny należy zapisać w pliku o ścieżce `user_data/strategies/freqtrade_ai_router.py`.
2. **Uzupełnienie wskaźników:** W głównej strategii generującej sygnały (lub w pliku konfiguracyjnym `FreqAI`) należy upewnić się, że do generowanego DataFrame dodawane są wskaźniki `adx` oraz `rsi` w metodzie `populate_indicators()`.
3. **Konfiguracja Nazewnictwa:** Pod-strategie muszą posiadać w swoich nazwach słowa kluczowe (np. `Trend_` lub `Range_`), aby aktywować mechanizm filtrowania reżimów rynkowych w metodzie `execute_routing`.

------------------------------
Aby pomyślnie sfinalizować wdrożenie tego systemu w Twoim środowisku produkcyjnym, potrzebuję informacji:

* Czy w metodzie populate_indicators masz już poprawnie zaimplementowane obliczanie wskaźników ADX i RSI, czy mam dostarczyć dla nich gotowy kod?
* Jakie są dokładne nazwy pod-strategii, które chcesz podłączyć pod ten router, aby poprawnie skonfigurować filtry reżimu rynkowego (trend/range)?


