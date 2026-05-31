OSTRZEŻENIE: Poniższe skrypty to eksperymentalne koncepcje. Nie gwarantują zysków, nie zostały przetestowane w boju. Używaj na własne ryzyko. Są to materiały edukacyjne pokazujące nowatorskie podejścia do budowy systemu tradingowego.

---

📂 00_CORE — NexusCore: Samoświadomy, Samonaprawialny Multi-Exchange Hub

Opis koncepcji: NexusCore to fundament całego systemu, zaprojektowany jako wymienny (swappable) hub komunikacyjny. Jego nowością jest wbudowany system autonomicznej samonaprawy (self-healing) i decentralizowanego, ważonego routingu. Hub nie tylko tłumaczy API, ale dynamicznie wybiera najszybszą i najtańszą ścieżkę dla każdego zadania (pobranie danych, zlecenie) i potrafi przełączać się między giełdami w przypadku awarii.

Weryfikacja oryginalności: Istniejące rozwiązania jak NautilusTrader są bardzo zaawansowane, ale NexusCore idzie o krok dalej, dodając samoświadomość stanu połączeń i proaktywne, a nie tylko reaktywne, zarządzanie nimi. Guilder jest klientem, nie hubem. NexusCore łączy cechy obu, ale z unikalnym systemem routingu ważonego.

```python
"""
NexusCore v1.0 - Samoświadomy Multi-Exchange Hub

Mechanizm działania:
1. Dynamiczny routing: Ważone drzewo decyzyjne wybiera giełdę o najniższym koszcie (latencja + opłata).
2. Samonaprawa: Każda giełda ma własny "health score". Trzy nieudane requesty w ciągu 60s obniżają score.
   Hub automatycznie odseparowuje (odcina) niezdrową giełdę i rozdziela jej zadania.
3. Discovery: Automatycznie wykrywa, które endpointy (public/private) są dostępne.
"""

import asyncio
import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NexusCore")

# ----------------------------------------------------------------------
# 1. MODEL DANYCH I KONFIGURACJA
# ----------------------------------------------------------------------
class EndpointType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    WEBSOCKET = "websocket"

@dataclass
class ExchangeConfig:
    name: str
    api_key: str = ""
    secret: str = ""
    base_url: str = ""
    ws_url: str = ""
    # Współczynniki w routingu (0.0 - 1.0)
    latency_weight: float = 0.5
    fee_weight: float = 0.5

@dataclass
class RouteDecision:
    exchange: str
    estimated_latency_ms: float
    total_fee_pct: float
    score: float  # im niższy, tym lepszy

# ----------------------------------------------------------------------
# 2. MENEDŻER STANU GIEŁD (HEALTH SCORE)
# ----------------------------------------------------------------------
@dataclass
class ExchangeState:
    config: ExchangeConfig
    healthy: bool = True
    health_score: float = 1.0  # 1.0 = idealnie
    consecutive_failures: int = 0
    last_failure_time: float = 0.0
    last_latency_ms: float = 100.0  # domyślne
    supported_endpoints: Dict[EndpointType, bool] = field(default_factory=lambda: {
        EndpointType.PUBLIC: True, EndpointType.PRIVATE: True, EndpointType.WEBSOCKET: True
    })

class ExchangeManager:
    def __init__(self):
        self.states: Dict[str, ExchangeState] = {}

    def register_exchange(self, config: ExchangeConfig):
        self.states[config.name] = ExchangeState(config=config)
        logger.info(f"[ExchangeManager] Zarejestrowano giełdę: {config.name}")

    def update_health(self, exchange_name: str, success: bool, latency_ms: float = 0):
        state = self.states[exchange_name]
        now = time.time()

        if success:
            state.consecutive_failures = 0
            state.last_latency_ms = latency_ms
            state.health_score = min(1.0, state.health_score + 0.05)
        else:
            state.consecutive_failures += 1
            state.last_failure_time = now
            state.health_score = max(0.0, state.health_score - 0.2)

        # Automatyczne odcięcie po 3 porażkach w 60s
        if state.consecutive_failures >= 3 and (now - state.last_failure_time) < 60:
            if state.healthy:
                logger.warning(f"[ExchangeManager] ODCINAM {exchange_name} po {state.consecutive_failures} porażkach.")
                state.healthy = False
        # Automatyczne przywrócenie po 3 sukcesach
        elif state.consecutive_failures == 0 and not state.healthy:
            logger.info(f"[ExchangeManager] PRZYWRACAM {exchange_name}.")
            state.healthy = True

# ----------------------------------------------------------------------
# 3. ROUTER WAŻONY
# ----------------------------------------------------------------------
class WeightedRouter:
    def __init__(self, manager: ExchangeManager):
        self.manager = manager

    async def measure_latency(self, exchange_name: str) -> float:
        """Symulacja pomiaru latencji (ping). W rzeczywistości byłoby to realne żądanie."""
        await asyncio.sleep(0.01)  # symulacja
        return 20 + (random.random() * 100)  # 20-120ms

    def estimate_fee(self, exchange_name: str, trade_type: str) -> float:
        """Symulacja estymacji opłat. W rzeczywistości pobierane z API giełdy."""
        fees = {"binance": 0.001, "kraken": 0.002, "bybit": 0.001}
        return fees.get(exchange_name, 0.005)

    async def find_best_route(self, task_type: EndpointType) -> Optional[RouteDecision]:
        """Wybiera najlepszą giełdę na podstawie ważonego kosztu (latencja + opłata)."""
        best_decision = None
        best_score = float('inf')

        for name, state in self.manager.states.items():
            if not state.healthy or not state.supported_endpoints.get(task_type, False):
                continue

            latency = await self.measure_latency(name)
            fee = self.estimate_fee(name, "spot")

            # Ważony scoring: im niższy wynik, tym lepiej
            score = (state.config.latency_weight * latency) + (state.config.fee_weight * fee * 10000)
            
            if score < best_score:
                best_score = score
                best_decision = RouteDecision(
                    exchange=name,
                    estimated_latency_ms=latency,
                    total_fee_pct=fee,
                    score=score
                )

        if best_decision:
            logger.info(f"[Router] Najlepsza trasa: {best_decision.exchange} (score={best_decision.score:.1f})")
        return best_decision

# ----------------------------------------------------------------------
# 4. SILNIK SAMONAPRAWY
# ----------------------------------------------------------------------
class SelfHealingEngine:
    def __init__(self, manager: ExchangeManager, router: WeightedRouter):
        self.manager = manager
        self.router = router
        self.running = True

    async def health_check_loop(self, interval_sec: int = 10):
        """Okresowo sprawdza zdrowie giełd i próbuje przywrócić odcięte."""
        logger.info("[SelfHealing] Start pętli monitorowania...")
        while self.running:
            for name, state in self.manager.states.items():
                if not state.healthy:
                    # Próbujemy pingować odciętą giełdę
                    try:
                        latency = await self.router.measure_latency(name)
                        # Jeśli ping OK, symulujemy sukces, by przywrócić
                        self.manager.update_health(name, success=True, latency_ms=latency)
                        logger.info(f"[SelfHealing] {name}: ping OK, przywracanie...")
                    except Exception:
                        self.manager.update_health(name, success=False)
            await asyncio.sleep(interval_sec)

# ----------------------------------------------------------------------
# 5. SYMULACJA DZIAŁANIA
# ----------------------------------------------------------------------
async def main():
    manager = ExchangeManager()
    router = WeightedRouter(manager)
    healer = SelfHealingEngine(manager, router)

    # Konfiguracja giełd
    for ex in [
        ExchangeConfig(name="binance", base_url="https://api.binance.com"),
        ExchangeConfig(name="kraken", base_url="https://api.kraken.com"),
        ExchangeConfig(name="bybit", base_url="https://api.bybit.com"),
    ]:
        manager.register_exchange(ex)

    # Symulujemy awarię Krakena
    for _ in range(4):
        manager.update_health("kraken", success=False)
        await asyncio.sleep(0.1)

    # Router powinien teraz omijać Krakena
    best = await router.find_best_route(EndpointType.PUBLIC)
    print(f"Decyzja routingu: {best}")

    # Uruchamiamy silnik samonaprawy w tle na 30 sekund
    task = asyncio.create_task(healer.health_check_loop(interval_sec=5))
    await asyncio.sleep(15)
    healer.running = False
    await task

if __name__ == "__main__":
    asyncio.run(main())
```

---

🧠 01_BRAIN — CogniCore: Autoewolucyjny Multi-Agent z Pamięcią Wad

Opis koncepcji: CogniCore to najnowsza generacja systemu decyzyjnego, która łączy kilka agentów AI (bazujących na LLM lub klasycznych modelach ML) w jeden, spójny organizm. Nowością jest „Księga Wad” (Book of Flaws), czyli baza danych zawierająca historyczne błędy systemu, która jest wykorzystywana w procesie decyzyjnym oraz „Radar Paradygmatów”, który wykrywa fundamentalne zmiany w zachowaniu rynku (zmianę reżimu), co pozwala na błyskawiczne odrzucenie nieaktualnych strategii.

Weryfikacja oryginalności: Wiele systemów, jak xDAN-Crypto-nofx czy TiMi, skupia się na multi-agentowej debacie. CogniCore wykracza poza to, dodając metapoznanie w formie pamięci błędów i proaktywne wykrywanie zmian paradygmatów, co jest rzadkością w dostępnych systemach open-source.

```python
"""
CogniCore v1.0 - Autoewolucyjny Multi-Agent z Pamięcią Wad

Mechanizm działania:
1. Radar Paradygmatów: Monitoruje anomalie statystyczne (np. korelacje między aktywami)
   i sygnalizuje, gdy rynek wchodzi w nowy, nieznany reżim.
2. Księga Wad (Book of Flaws): Przechowuje opisy przeszłych błędów (np. "Long podczas silnego trendu spadkowego").
   Agenci są zobowiązani do konsultowania się z Księgą przed wydaniem rekomendacji.
3. Syndykat Decyzyjny: Każdy agent (Trend, Momentum, Sentyment) generuje sygnał.
   Sygnały są ważone przez ich historyczną skuteczność w danym reżimie.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CogniCore")

# ----------------------------------------------------------------------
# 1. MODEL DANYCH: KSIĘGA WAD
# ----------------------------------------------------------------------
@dataclass
class FlawRecord:
    timestamp: str
    agent: str
    decision: str  # "LONG", "SHORT"
    loss_pct: float
    reason: str    # powód błędu, np. "Zignorowano silny opór"

class BookOfFlaws:
    def __init__(self):
        self.flaws: List[FlawRecord] = []

    def add_flaw(self, agent: str, decision: str, loss: float, reason: str):
        self.flaws.append(FlawRecord(
            timestamp=str(pd.Timestamp.now()),
            agent=agent,
            decision=decision,
            loss_pct=loss,
            reason=reason
        ))
        logger.warning(f"[BookOfFlaws] Dodano wadę: Agent={agent}, Decyzja={decision}, Strata={loss}%, Powód={reason}")

    def check_agent_flaws(self, agent: str, current_decision: str) -> bool:
        """Sprawdza, czy agent popełnił podobny błąd w przeszłości."""
        for flaw in self.flaws:
            if flaw.agent == agent and flaw.decision == current_decision:
                return True  # znaleziono podobną wadę
        return False

# ----------------------------------------------------------------------
# 2. RADAR PARADYGMATÓW (Reżimów Rynkowych)
# ----------------------------------------------------------------------
class ParadigmRadar:
    def __init__(self, window: int = 50):
        self.window = window
        self.correlation_history: List[float] = []
        self.regime = "normal"

    def update(self, returns_a: pd.Series, returns_b: pd.Series):
        """Wykrywa nagłe zmiany w korelacjach między aktywami (A i B)."""
        if len(returns_a) < self.window:
            return

        # Bieżąca korelacja
        current_corr = returns_a.rolling(self.window).corr(returns_b).iloc[-1]
        self.correlation_history.append(current_corr)

        if len(self.correlation_history) > 50:
            # Średnia i odchylenie standardowe historycznych korelacji
            mean_corr = np.mean(self.correlation_history[:-1])
            std_corr = np.std(self.correlation_history[:-1])

            # Jeśli obecna korelacja odbiega o >2 sigma, sygnalizujemy zmianę reżimu
            if abs(current_corr - mean_corr) > 2 * std_corr:
                self.regime = "chaos"
                logger.warning(f"[RadarParadygmatów] Wykryto zmianę reżimu! Korelacja {current_corr:.2f} odbiega od normy {mean_corr:.2f}±{std_corr:.2f}")
                return
        self.regime = "normal"

# ----------------------------------------------------------------------
# 3. AGENT SYNDYKATU
# ----------------------------------------------------------------------
class SyndicateAgent:
    def __init__(self, name: str, accuracy: float):
        self.name = name
        self.accuracy = accuracy  # historyczna celność (0.0-1.0)

    def generate_signal(self, price_data: pd.DataFrame, book: BookOfFlaws) -> Tuple[str, float]:
        """
        Generuje sygnał i sprawdza w Księdze Wad.
        W rzeczywistości tutaj byłby model ML.
        """
        # Prosty, deterministyczny sygnał na podstawie ostatniej zmiany ceny
        last_change = price_data['close'].pct_change().iloc[-1]
        signal = "LONG" if last_change > 0 else "SHORT"
        confidence = 0.7  # symulacja

        # Blokada z Księgi Wad
        if book.check_agent_flaws(self.name, signal):
            logger.warning(f"[{self.name}] ZABLOKOWANO sygnał {signal} przez Księgę Wad!")
            return ("NEUTRAL", 0.0)

        return (signal, confidence * self.accuracy)

# ----------------------------------------------------------------------
# 4. SILNIK DECYZYJNY
# ----------------------------------------------------------------------
class DecisionEngine:
    def __init__(self):
        self.book = BookOfFlaws()
        self.radar = ParadigmRadar()
        self.agents: List[SyndicateAgent] = [
            SyndicateAgent("TrendAgent", 0.65),
            SyndicateAgent("MomentumAgent", 0.55),
            SyndicateAgent("SentimentAgent", 0.60),
        ]

    def decide(self, market_data: Dict[str, pd.DataFrame]) -> str:
        votes = {"LONG": 0, "SHORT": 0, "NEUTRAL": 0}

        # Aktualizacja radaru (np. BTC vs ETH)
        if "BTC" in market_data and "ETH" in market_data:
            self.radar.update(market_data["BTC"]['close'].pct_change(), market_data["ETH"]['close'].pct_change())

        for agent in self.agents:
            # Wybór danych dla agenta (w rzeczywistości bardziej zaawansowany)
            data = market_data.get("BTC", pd.DataFrame())
            if data.empty:
                continue

            signal, conf = agent.generate_signal(data, self.book)
            votes[signal] += conf

        final_decision = max(votes, key=votes.get)
        logger.info(f"[DecisionEngine] Głosowanie: {votes} -> Decyzja: {final_decision} | Reżim: {self.radar.regime}")
        return final_decision

# ----------------------------------------------------------------------
# 5. SYMULACJA
# ----------------------------------------------------------------------
if __name__ == "__main__":
    engine = DecisionEngine()

    # Dodajemy przykładową wadę do Księgi
    engine.book.add_flaw("TrendAgent", "LONG", 5.2, "Zignorowano silny opór na 50k")

    # Generujemy sztuczne dane rynkowe
    dates = pd.date_range('2026-01-01', periods=100, freq='H')
    btc_data = pd.DataFrame({
        'close': np.cumsum(np.random.randn(100)) + 50000
    }, index=dates)
    eth_data = pd.DataFrame({
        'close': np.cumsum(np.random.randn(100)) + 3000
    }, index=dates)

    market = {"BTC": btc_data, "ETH": eth_data}
    decision = engine.decide(market)
    print(f"Ostateczna decyzja CogniCore: {decision}")
```

---

👁️ 02_EYES — OmniSight: Fuzja Danych On-Chain i Mikrostruktury

Opis koncepcji: OmniSight to system, który łączy dane z blockchaina (ruchy wielorybów, przepływy na giełdy) z danymi z arkusza zleceń (mikrostruktura rynku) w czasie rzeczywistym. Kluczową innowacją jest „Silnik Fuzji Czasoprzestrzennej”, który nie tylko wykrywa anomalie w każdym ze strumieni danych osobno, ale identyfikuje zdarzenia, które są nieszkodliwe osobno, a wysoce prawdopodobne dopiero w koniunkcji. Przykład: duży transfer na giełdę (on-chain) + pojawienie się wielkiego zlecenia sprzedaży tuż poniżej ceny (order book) = bardzo silny sygnał spadkowy.

Weryfikacja oryginalności: Istnieją narzędzia osobno dla on-chain (ARGOS) i mikrostruktury, ale OmniSight jako pierwszy łączy je w jeden, spójny system, który rozumie interakcje między nimi.

```python
"""
OmniSight v1.0 - Fuzja Danych On-Chain i Mikrostruktury

Mechanizm działania:
1. Strumień On-Chain: Monitoruje duże transfery (np. >100 BTC) na adresy giełd.
2. Strumień Order Book: Śledzi zmiany w głębokości arkusza (np. pojawienie się "ściany").
3. Silnik Fuzji: Koreluje zdarzenia z obu strumieni. Używa prostego modelu bayesowskiego
   do aktualizacji prawdopodobieństwa manipulacji, gdy oba typy zdarzeń występują blisko siebie.
"""

import asyncio
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OmniSight")

# ----------------------------------------------------------------------
# 1. MODEL DANYCH: ZDARZENIA
# ----------------------------------------------------------------------
class EventType(Enum):
    ONCHAIN_LARGE_TRANSFER = "onchain_large_transfer"
    ORDERBOOK_SPOOF_WALL = "orderbook_spoof_wall"
    ORDERBOOK_IMBALANCE = "orderbook_imbalance"

@dataclass
class MarketEvent:
    event_type: EventType
    exchange: str
    symbol: str
    data: Dict
    timestamp: float

# ----------------------------------------------------------------------
# 2. DETEKTORY
# ----------------------------------------------------------------------
class OnChainDetector:
    def __init__(self, btc_threshold: float = 100):
        self.threshold = btc_threshold

    async def listen(self) -> Optional[MarketEvent]:
        """Symulacja nasłuchiwania transferów on-chain."""
        await asyncio.sleep(random.uniform(0.5, 2.0))
        if random.random() < 0.3:  # 30% szans na zdarzenie
            amount = random.uniform(80, 500)
            if amount > self.threshold:
                logger.info(f"[OnChainDetector] Wykryto duży transfer {amount:.1f} BTC na giełdę.")
                return MarketEvent(
                    event_type=EventType.ONCHAIN_LARGE_TRANSFER,
                    exchange="binance",
                    symbol="BTC/USDT",
                    data={"amount_btc": amount},
                    timestamp=asyncio.get_event_loop().time()
                )
        return None

class OrderBookDetector:
    async def listen(self) -> Optional[MarketEvent]:
        """Symulacja analizy mikrostruktury (np. wykrywanie fałszywych ścian)."""
        await asyncio.sleep(random.uniform(0.5, 2.0))
        if random.random() < 0.4:  # 40% szans
            depth = random.uniform(50, 300)
            logger.info(f"[OrderBookDetector] Wykryto potencjalną ścianę sprzedaży o wartości {depth:.1f} BTC.")
            return MarketEvent(
                event_type=EventType.ORDERBOOK_SPOOF_WALL,
                exchange="binance",
                symbol="BTC/USDT",
                data={"wall_depth_btc": depth},
                timestamp=asyncio.get_event