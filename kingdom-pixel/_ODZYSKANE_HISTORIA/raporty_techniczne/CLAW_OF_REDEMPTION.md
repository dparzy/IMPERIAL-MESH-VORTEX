```python
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           CLAW OF REDEMPTION — Alchemist's Grace v1.0                       ║
║           Kingdom Pixel | Royal Alchemist Chamber                            ║
║           Autor: Komandant Pixel & DeepSeek AI (koncepcja oryginalna)        ║
║           Licencja: Wyłącznie do celów edukacyjnych                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

FILOZOFIA (ClawDrive Adaptation):
"Jeśli nie zarabiasz — umierasz. Ale śmierć to nie koniec — to narodziny."

Gdy agent Armii poniesie stratę:
1. Zostaje oznaczony jako UPADŁY (Fallen).
2. Musi udać się do Nadwornego Alchemika.
3. Alchemik zleca mu ZADANIE POKUTNE (Redemption Quest):
   - Znalezienie unikalnego składnika (rzadki wzorzec rynkowy, anomalia on-chain,
     nieodkryty sygnał KOL-a, świeża narracja z mediów społecznościowych).
4. Po dostarczeniu składnika i jego pomyślnej WALIDACJI:
   - Alchemik warzy ANTIDOTUM (ochronny buff).
   - Agent otrzymuje REWANŻ (Reinstatement) na ograniczonym kapitale.
   - Jeśli REWANŻ się powiedzie:
     * Generał i Dwór chwalą agenta.
     * Wojenny Burdel zostaje mu przyznany (nagroda).
     * Jego statystyki zostają przywrócone, a reputacja wzrasta.
   - Jeśli REWANŻ się nie powiedzie:
     * Agent trafia na CMENTARZ STRATEGII (permanentna degradacja).

ARCHITEKTURA:
- RedemptionQuest: Definiuje zadanie pokutne.
- AlchemistAntidote: Buff ochronny dający przewagę na czas rewanzu.
- RedemptionEngine: Główny silnik zarządzający całym procesem.
- ValidationOracle: Weryfikuje dostarczone składniki.
- ReinstatementManager: Zarządza procesem przywracania agenta.
- GloryTracker: Śledzi chwałę i nagrody po udanym rewanzu.

STRUKTURA PLIKÓW (do integracji z Kingdom Pixel 2.0):
C:\Kingdom Pixel\Castle Pixel\Royal Alchemist\
├── ClawOfRedemption\
│   ├── __init__.py
│   ├── claw_of_redemption.py    # GŁÓWNY PLIK — TEN KOD
│   ├── validation_oracle.py     # Walidator składników
│   ├── antidote_brewer.py       # Warzelnia antidotum
│   ├── reinstatement_manager.py # Menadżer rewanzu
│   ├── glory_tracker.py         # Świątynia chwały
│   ├── fallen_agents.db         # Baza upadłych agentów
│   ├── ingredient_archive.db    # Archiwum składników
│   └── glory_records.db         # Rekordy chwały

C:\Kingdom Pixel\Castle Pixel\The Keep\Cmentarz_Strategii\
└── exiled_agents.json           # Lista wygnanych agentów

C:\Kingdom Pixel\Castle Pixel\Royal Treasury\War Loot Vault\
└── brothel_access_registry.json # Rejestr dostępu do Burdelu
"""

import hashlib
import json
import logging
import random
import sqlite3
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from uuid import uuid4

# ---------------------------------------------------------------------------
# 1. KONFIGURACJA
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)-30s | %(message)s",
)
logger = logging.getLogger("AlchemistGrace")

# ---------------------------------------------------------------------------
# 2. MODELE DANYCH
# ---------------------------------------------------------------------------


class AgentStatus(Enum):
    """Status agenta w Armii."""

    ACTIVE = "ACTIVE"  # Aktywny, zarabia
    FALLEN = "FALLEN"  # Upadł, musi odkupić winy
    ON_QUEST = "ON_QUEST"  # W trakcie zadania pokutnego
    REINSTATED = "REINSTATED"  # Przywrócony na próbę (rewanż)
    REDEEMED = "REDEEMED"  # W pełni odkupiony
    EXILED = "EXILED"  # Zesłany na Cmentarz Strategii (permanentna degradacja)


class QuestType(Enum):
    """Typ zadania pokutnego."""

    FIND_RARE_PATTERN = "FIND_RARE_PATTERN"  # Znajdź rzadki wzorzec techniczny
    FIND_WHALE_MOVEMENT = "FIND_WHALE_MOVEMENT"  # Wykryj ruch wieloryba
    FIND_SENTIMENT_ANOMALY = "FIND_SENTIMENT_ANOMALY"  # Znajdź anomalię sentymentu
    FIND_NARRATIVE_SHIFT = "FIND_NARRATIVE_SHIFT"  # Wykryj zmianę narracji
    FIND_ONCHAIN_SIGNAL = "FIND_ONCHAIN_SIGNAL"  # Znajdź sygnał on-chain
    FIND_KOL_WHISPER = "FIND_KOL_WHISPER"  # Wyśledź szept KOL-a
    FIND_LATENCY_EDGE = "FIND_LATENCY_EDGE"  # Znajdź okazję arbitrażową
    FIND_RISK_ANOMALY = "FIND_RISK_ANOMALY"  # Znajdź anomalię ryzyka


class AntidoteType(Enum):
    """Typ antidotum (buffa)."""

    LOWER_FEES = "LOWER_FEES"  # Obniżone opłaty przez X godzin
    HIGHER_LEVERAGE = "HIGHER_LEVERAGE"  # Wyższa dozwolona dźwignia
    PRIORITY_EXECUTION = "PRIORITY_EXECUTION"  # Priorytetowa egzekucja zleceń
    EXTENDED_SL = "EXTENDED_SL"  # Szerszy stop-loss (większa tolerancja)
    REDUCED_SLIPPAGE = "REDUCED_SLIPPAGE"  # Mniejszy poślizg
    BOUNTY_MULTIPLIER = "BOUNTY_MULTIPLIER"  # Mnożnik nagród za sukces
    SIGNAL_BOOST = "SIGNAL_BOOST"  # Wzmocnienie sygnałów dla agenta
    SHIELD_OF_GRACE = "SHIELD_OF_GRACE"  # Tarcza chroniąca przed jedną stratą


@dataclass
class FallenAgent:
    """Agent, który upadł i musi odkupić winy."""

    agent_id: str
    agent_name: str
    division: str  # np. "03_Kawaleria", "01_Wywiad"
    fall_reason: str  # Powód upadku
    loss_pct: float  # Procent straty
    fall_timestamp: float
    redemption_attempts: int = 0  # Liczba prób odkupienia
    status: AgentStatus = AgentStatus.FALLEN
    quest: Optional["RedemptionQuest"] = None
    antidote: Optional["AlchemistAntidote"] = None
    reinstatement_capital_pct: float = 0.05  # % kapitału na rewanż


@dataclass
class RedemptionQuest:
    """Zadanie pokutne zlecone przez Alchemika."""

    quest_id: str
    quest_type: QuestType
    description: str
    target_market: str  # Gdzie szukać składnika
    difficulty: int  # 1-10
    deadline_hours: float  # Czas na wykonanie
    required_evidence: Dict[str, Any]  # Wymagane dowody
    assigned_to: str  # agent_id
    assigned_at: float
    completed: bool = False
    delivered_evidence: Optional[Dict[str, Any]] = None
    validation_score: float = 0.0  # 0.0-1.0


@dataclass
class AlchemistAntidote:
    """Antidotum — buff ochronny dla agenta na czas rewanzu."""

    antidote_id: str
    antidote_type: AntidoteType
    description: str
    duration_hours: float  # Czas działania
    buff_multiplier: float  # Mnożnik buffa
    created_at: float
    expires_at: float
    consumed: bool = False


@dataclass
class ReinstatementRecord:
    """Rekord procesu przywracania agenta."""

    record_id: str
    agent_id: str
    quest: RedemptionQuest
    antidote: AlchemistAntidote
    reinstatement_time: float
    capital_allocated: float  # Kapitał przydzielony na rewanż
    capital_limit: float  # Maksymalna dozwolona strata
    success: Optional[bool] = None  # None = w trakcie
    pnl_pct: float = 0.0
    glory_awarded: bool = False
    brothel_access: bool = False  # Czy dostęp do Burdelu przyznany


@dataclass
class GloryRecord:
    """Rekord chwały po udanym rewanzu."""

    agent_id: str
    agent_name: str
    division: str
    redemption_count: int  # Ile razy się odkupił
    quests_completed: int
    antidotes_earned: int
    total_pnl_recovered: float  # Łączny zysk po odkupieniu
    praise_from_general: bool  # Pochwała od Generała
    court_recognition: bool  # Uznanie Dworu
    brothel_reward: bool  # Nagroda z Burdelu
    glory_points: int  # Punkty Chwały
    current_rank: str  # Aktualny tytuł


# ---------------------------------------------------------------------------
# 3. WALIDATOR SKŁADNIKÓW (VALIDATION ORACLE)
# ---------------------------------------------------------------------------


class ValidationOracle:
    """
    Weryfikuje dostarczone przez agenta składniki (informacje).
    Ocenia ich unikalność, wartość i autentyczność.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self._lock = threading.Lock()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ingredient_archive (
                hash TEXT PRIMARY KEY,
                quest_type TEXT,
                discovery_time REAL,
                discoverer_id TEXT,
                validation_score REAL,
                uniqueness_score REAL,
                value_score REAL,
                authenticity_score REAL
            )
        """)
        self.conn.commit()

    def validate(
        self, quest: RedemptionQuest, evidence: Dict[str, Any]
    ) -> Tuple[bool, float, str]:
        """
        Waliduje dostarczone składniki.
        Zwraca: (zaliczone?, wynik_walidacji, powód)
        """
        evidence_hash = self._hash_evidence(evidence)

        # 1. Sprawdzenie autentyczności
        authenticity = self._check_authenticity(quest, evidence)
        if authenticity < 0.5:
            return False, authenticity, "Dowody nieautentyczne lub sfabrykowane."

        # 2. Sprawdzenie unikalności (czy już nie mamy tego składnika)
        uniqueness = self._check_uniqueness(evidence_hash)
        if uniqueness < 0.3:
            return False, uniqueness, "Składnik już znany — nic nowego nie odkryto."

        # 3. Ocena wartości
        value = self._assess_value(quest, evidence)

        # 4. Ostateczny wynik
        total_score = (authenticity * 0.4 + uniqueness * 0.3 + value * 0.3)

        if total_score >= 0.6:
            self._archive_ingredient(
                evidence_hash, quest.quest_type, quest.assigned_to, total_score,
                uniqueness, value, authenticity
            )
            return True, total_score, "Składnik zaakceptowany. Antidotum zostanie uwarzone."
        else:
            return False, total_score, "Składnik niewystarczającej jakości. Spróbuj ponownie."

    def _hash_evidence(self, evidence: Dict) -> str:
        return hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()[:16]

    def _check_authenticity(self, quest: RedemptionQuest, evidence: Dict) -> float:
        """Sprawdza autentyczność dowodów."""
        score = 0.5  # Bazowa ocena

        # Sprawdzenie czy dane nie są zbyt stare
        timestamp = evidence.get("timestamp", 0)
        age_hours = (time.time() - timestamp) / 3600
        if age_hours < 1:
            score += 0.3
        elif age_hours < 24:
            score += 0.1

        # Sprawdzenie czy źródło jest wiarygodne
        source = evidence.get("source", "")
        trusted_sources = ["glassnode", "nansen", "dextools", "santiment", "coinglass",
                           "polymarket", "kalshi", "thegraph", "diadata"]
        if any(ts in source.lower() for ts in trusted_sources):
            score += 0.2

        return min(1.0, score)

    def _check_uniqueness(self, evidence_hash: str) -> float:
        """Sprawdza czy składnik nie został już dostarczony."""
        cursor = self.conn.execute(
            "SELECT COUNT(*) FROM ingredient_archive WHERE hash = ?", (evidence_hash,)
        )
        count = cursor.fetchone()[0]
        if count > 0:
            return 0.0
        # Sprawdzamy podobne (uproszczone)
        cursor = self.conn.execute("SELECT COUNT(*) FROM ingredient_archive")
        total = cursor.fetchone()[0]
        if total == 0:
            return 1.0
        return 0.7 + random.uniform(0.0, 0.3)

    def _assess_value(self, quest: RedemptionQuest, evidence: Dict) -> float:
        """Ocenia wartość składnika."""
        score = 0.5

        # Ilość danych
        data_points = evidence.get("data_points", 0)
        if data_points > 100:
            score += 0.3
        elif data_points > 10:
            score += 0.1

        # Rzadkość wzorca
        rarity = evidence.get("rarity_score", 0.5)
        score += rarity * 0.2

        return min(1.0, score)

    def _archive_ingredient(self, *args):
        with self._lock:
            self.conn.execute(
                "INSERT INTO ingredient_archive VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                args,
            )
            self.conn.commit()


# ---------------------------------------------------------------------------
# 4. WARZELNIA ANTIDOTUM
# ---------------------------------------------------------------------------


class AntidoteBrewer:
    """
    Warzy antidota na podstawie dostarczonych składników.
    Im lepszy składnik, tym silniejszy buff.
    """

    ANTIDOTE_RECIPES = {
        QuestType.FIND_RARE_PATTERN: [
            (AntidoteType.SIGNAL_BOOST, "Wzmocnienie sygnałów z rzadkiego wzorca"),
            (AntidoteType.REDUCED_SLIPPAGE, "Płynniejsze wejścia dzięki znajomości wzorca"),
        ],
        QuestType.FIND_WHALE_MOVEMENT: [
            (AntidoteType.PRIORITY_EXECUTION, "Pierwszeństwo egzekucji za ruchem wieloryba"),
            (AntidoteType.HIGHER_LEVERAGE, "Większa dźwignia na ruchu wieloryba"),
        ],
        QuestType.FIND_SENTIMENT_ANOMALY: [
            (AntidoteType.SIGNAL_BOOST, "Wzmocnienie sygnałów z nastrojów"),
            (AntidoteType.EXTENDED_SL, "Większa tolerancja przy zmiennych nastrojach"),
        ],
        QuestType.FIND_NARRATIVE_SHIFT: [
            (AntidoteType.BOUNTY_MULTIPLIER, "Mnożnik nagród za jazdę na narracji"),
            (AntidoteType.SHIELD_OF_GRACE, "Tarcza przed fałszywą narracją"),
        ],
        QuestType.FIND_ONCHAIN_SIGNAL: [
            (AntidoteType.LOWER_FEES, "Niższe opłaty za wejście na sygnał on-chain"),
            (AntidoteType.PRIORITY_EXECUTION, "Szybka egzekucja przed resztą rynku"),
        ],
        QuestType.FIND_KOL_WHISPER: [
            (AntidoteType.BOUNTY_MULTIPLIER, "Mnożnik nagród za podążanie za KOL-em"),
            (AntidoteType.SHIELD_OF_GRACE, "Tarcza gdy KOL się myli"),
        ],
        QuestType.FIND_LATENCY_EDGE: [
            (AntidoteType.PRIORITY_EXECUTION, "Absolutny priorytet egzekucji"),
            (AntidoteType.REDUCED_SLIPPAGE, "Minimalny poślizg"),
        ],
        QuestType.FIND_RISK_ANOMALY: [
            (AntidoteType.EXTENDED_SL, "Szerszy stop-loss w anomalię"),
            (AntidoteType.SHIELD_OF_GRACE, "Tarcza ochronna na czas anomalii"),
        ],
    }

    def brew(
        self,
        quest: RedemptionQuest,
        validation_score: float,
        duration_hours: float = 24.0,
    ) -> AlchemistAntidote:
        """
        Warzy antidotum na podstawie wykonanego questa.
        """
        recipes = self.ANTIDOTE_RECIPES.get(quest.quest_type, [
            (AntidoteType.SHIELD_OF_GRACE, "Podstawowa tarcza ochronna")
        ])

        # Wybór receptury na podstawie wyniku walidacji
        if validation_score >= 0.9:
            chosen = recipes[0]  # Najlepsza receptura
            multiplier = 2.0
            duration_hours *= 1.5
        elif validation_score >= 0.7:
            chosen = random.choice(recipes)
            multiplier = 1.5
        else:
            chosen = recipes[-1]  # Podstawowa receptura
            multiplier = 1.0

        now = time.time()
        return AlchemistAntidote(
            antidote_id=f"ANTIDOTE-{uuid4().hex[:12].upper()}",
            antidote_type=chosen[0],
            description=chosen[1],
            duration_hours=duration_hours,
            buff_multiplier=multiplier,
            created_at=now,
            expires_at=now + duration_hours * 3600,
        )


# ---------------------------------------------------------------------------
# 5. MENEDŻER REINSTANCJI (REWANŻU)
# ---------------------------------------------------------------------------


class ReinstatementManager:
    """
    Zarządza procesem przywracania agenta do walki.
    """

    def __init__(self, base_capital: float = 100000.0):
        self.base_capital = base_capital
        self.active_reinstatements: Dict[str, ReinstatementRecord] = {}
        self._lock = threading.Lock()

    def grant_reinstatement(
        self,
        agent: FallenAgent,
        quest: RedemptionQuest,
        antidote: AlchemistAntidote,
    ) -> ReinstatementRecord:
        """
        Przyznaje agentowi rewanż z ograniczonym kapitałem.
        """
        capital_pct = min(0.10, agent.reinstatement_capital_pct * (agent.redemption_attempts + 1))
        capital = self.base_capital * capital_pct

        record = ReinstatementRecord(
            record_id=f"REINST-{uuid4().hex[:12].upper()}",
            agent_id=agent.agent_id,
            quest=quest,
            antidote=antidote,
            reinstatement_time=time.time(),
            capital_allocated=capital,
            capital_limit=capital * 0.5,  # Max 50% straty
        )

        with self._lock:
            self.active_reinstatements[agent.agent_id] = record

        logger.info(
            f"[Reinstatement] Agent {agent.agent_name} otrzymuje rewanż! "
            f"Kapitał: ${capital:,.0f} | Antidotum: {antidote.antidote_type.value} "
            f"(x{antidote.buff_multiplier}) | Czas: {antidote.duration_hours}h"
        )

        return record

    def evaluate_reinstatement(
        self, agent_id: str, pnl_pct: float
    ) -> Tuple[bool, str]:
        """
        Ocenia wynik rewanzu.
        """
        with self._lock:
            record = self.active_reinstatements.get(agent_id)
            if not record:
                return False, "Brak aktywnego rewanzu."

            record.pnl_pct = pnl_pct

            # Uwzględniamy buff z antidotum
            adjusted_pnl = pnl_pct * record.antidote.buff_multiplier

            # Czy antidotum jeszcze działa?
            if time.time() > record.antidote.expires_at:
                record.antidote.consumed = True
                adjusted_pnl = pnl_pct  # Bez buffa

            if adjusted_pnl > 0:
                record.success = True
                return True, f"Rewanż udany! PnL: {pnl_pct*100:.2f}% (z buffem: {adjusted_pnl*100:.2f}%)"
            else:
                record.success = False
                return False, f"Rewanż nieudany. Strata: {abs(pnl_pct)*100:.2f}%"

    def finalize_reinstatement(self, agent_id: str):
        """Zamyka proces reinstancji."""
        with self._lock:
            record = self.active_reinstatements.pop(agent_id, None)
        return record


# ---------------------------------------------------------------------------
# 6. ŚWIĄTYNIA CHWAŁY (GLORY TRACKER)
# ---------------------------------------------------------------------------


class GloryTracker:
    """
    Śledzi chwałę, nagrody i uznanie dla odkupionych agentów.
    """

    RANKS = [
        "Rekrut", "Szeregowy", "Kapral", "Sierżant", "Chorąży",
        "Porucznik", "Kapitan", "Major", "Pułkownik", "Generał Brygady",
        "Generał Dywizji", "Marszałek Polny", "Wielki Strateg", "Legenda Imperium",
    ]

    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS glory_records (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT,
                division TEXT,
                redemption_count INTEGER DEFAULT 0,
                quests_completed INTEGER DEFAULT 0,
                antidotes_earned INTEGER DEFAULT 0,
                total_pnl_recovered REAL DEFAULT 0.0,
                praise_from_general INTEGER DEFAULT 0,
                court_recognition INTEGER DEFAULT 0,
                brothel_reward INTEGER DEFAULT 0,
                glory_points INTEGER DEFAULT 0,
                current_rank TEXT DEFAULT 'Rekrut'
            )
        """)
        self.conn.commit()

    def award_glory(self, agent: FallenAgent, record: ReinstatementRecord):
        """Przyznaje chwałę za udany rewanż."""
        glory_points = int(record.pnl_pct * 1000) + record.quest.validation_score * 100
        praise = glory_points > 50
        recognition = glory_points > 100
        brothel = glory_points > 200

        cursor = self.conn.execute(
            "SELECT * FROM glory_records WHERE agent_id = ?", (agent.agent_id,)
        )
        existing = cursor.fetchone()

        if existing:
            self.conn.execute(
                """UPDATE glory_records SET
                   redemption_count = redemption_count + 1,
                   quests_completed = quests_completed + 1,
                   antidotes_earned = antidotes_earned + 1,
                   total_pnl_recovered = total_pnl_recovered + ?,
                   praise_from_general = praise_from_general + ?,
                   court_recognition = court_recognition + ?,
                   brothel_reward = brothel_reward + ?,
                   glory_points = glory_points + ?
                   WHERE agent_id = ?""",
                (record.pnl_pct * 100, 1 if praise else 0, 1 if recognition else 0,
                 1 if brothel else 0, glory_points, agent.agent_id),
            )
        else:
            self.conn.execute(
                """INSERT INTO glory_records VALUES (?, ?, ?, 1, 1, 1, ?, ?, ?, ?, ?, ?)""",
                (agent.agent_id, agent.agent_name, agent.division,
                 record.pnl_pct * 100, 1 if praise else 0, 1 if recognition else 0,
                 1 if brothel else 0, glory_points, self._calculate_rank(glory_points)),
            )

        self.conn.commit()

        if brothel:
            logger.info(
                f"🎖️ WOJENNY BURDEL PRZYZNANY! Agent {agent.agent_name} "
                f"otrzymuje dostęp do Komnaty Rozkoszy za odwagę i odkupienie!"
            )
        if praise:
            logger.info(f"👏 Generał chwali agenta {agent.agent_name}!")
        if recognition:
            logger.info(f"🏛️ Dwór uznaje zasługi agenta {agent.agent_name}!")

    def _calculate_rank(self, glory_points: int) -> str:
        """Oblicza rangę na podstawie punktów chwały."""
        index = min(glory_points // 100, len(self.RANKS) - 1)
        return self.RANKS[index]

    def get_glory(self, agent_id: str) -> Optional[GloryRecord]:
        """Pobiera rekord chwały agenta."""
        cursor = self.conn.execute(
            "SELECT * FROM glory_records WHERE agent_id = ?", (agent_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        return GloryRecord(
            agent_id=row[0], agent_name=row[1], division=row[2],
            redemption_count=row[3], quests_completed=row[4], antidotes_earned=row[5],
            total_pnl_recovered=row[6], praise_from_general=bool(row[7]),
            court_recognition=bool(row[8]), brothel_reward=bool(row[9]),
            glory_points=row[10], current_rank=row[11],
        )


# ---------------------------------------------------------------------------
# 7. GŁÓWNY SILNIK — CLAW OF REDEMPTION
# ---------------------------------------------------------------------------


class ClawOfRedemption:
    """
    Główny silnik systemu odkupienia.
    Zarządza całym cyklem: Upadek → Quest → Antidotum → Rewanż → Chwała/Wygnanie.
    """

    def __init__(self, base_capital: float = 100000.0):
        self.fallen_agents: Dict[str, FallenAgent] = {}
        self.active_quests: Dict[str, RedemptionQuest] = {}
        self.oracle = ValidationOracle()
        self.brewer = AntidoteBrewer()
        self.reinstatement_mgr = ReinstatementManager(base_capital)
        self.glory_tracker = GloryTracker()
        self._lock = threading.Lock()

    # -----------------------------------------------------------------------
    # FAZA 1: UPADEK
    # -----------------------------------------------------------------------
    def mark_as_fallen(
        self, agent_id: str, agent_name: str, division: str,
        loss_reason: str, loss_pct: float,
    ) -> FallenAgent:
        """
        Oznacza agenta jako UPADŁEGO po stracie.
        """
        agent = FallenAgent(
            agent_id=agent_id,
            agent_name=agent_name,
            division=division,
            fall_reason=loss_reason,
            loss_pct=loss_pct,
            fall_timestamp=time.time(),
        )

        with self._lock:
            self.fallen_agents[agent_id] = agent

        logger.warning(
            f"💀 AGENT UPADŁ: {agent_name} ({division}) | "
            f"Strata: {loss_pct*100:.2f}% | Powód: {loss_reason}"
        )
        logger.info(
            f"📜 {agent_name} musi udać się do Nadwornego Alchemika, aby odkupić winy."
        )

        return agent

    # -----------------------------------------------------------------------
    # FAZA 2: ZADANIE POKUTNE
    # -----------------------------------------------------------------------
    def assign_redemption_quest(self, agent: FallenAgent) -> RedemptionQuest:
        """
        Alchemik zleca agentowi zadanie pokutne.
        """
        # Wybór typu questa na podstawie dywizji agenta
        division_quests = {
            "03_Kawaleria": [QuestType.FIND_LATENCY_EDGE, QuestType.FIND_WHALE_MOVEMENT],
            "01_Wywiad": [QuestType.FIND_SENTIMENT_ANOMALY, QuestType.FIND_NARRATIVE_SHIFT,
                          QuestType.FIND_KOL_WHISPER],
            "02_Zwiadowcy": [QuestType.FIND_RARE_PATTERN, QuestType.FIND_ONCHAIN_SIGNAL,
                             QuestType.FIND_RISK_ANOMALY],
            "04_Gwardia_Przyboczna": [QuestType.FIND_RISK_ANOMALY],
            "10_Korpus_Ewolucyjny": [QuestType.FIND_RARE_PATTERN, QuestType.FIND_ONCHAIN_SIGNAL],
        }
        possible_quests = division_quests.get(
            agent.division,
            [QuestType.FIND_RARE_PATTERN, QuestType.FIND_SENTIMENT_ANOMALY],
        )

        quest_type = random.choice(possible_quests)
        difficulty = min(10, 3 + agent.redemption_attempts * 2)
        deadline = max(2.0, 24.0 - agent.redemption_attempts * 4.0)

        quest_descriptions = {
            QuestType.FIND_RARE_PATTERN: "Znajdź na rynku formację techniczną, która wystąpiła mniej niż 5 razy w ostatnim roku.",
            QuestType.FIND_WHALE_MOVEMENT: "Wyśledź ruch wieloryba (>$1M) na giełdę i zgłoś go przed wykonaniem.",
            QuestType.FIND_SENTIMENT_ANOMALY: "Znajdź moment, gdy sentyment społecznościowy jest przeciwny do ruchu ceny.",
            QuestType.FIND_NARRATIVE_SHIFT: "Wykryj nową narrację rynkową, zanim pojawi się w mainstreamowych mediach.",
            QuestType.FIND_ONCHAIN_SIGNAL: "Znajdź sygnał on-chain (np. akumulację), który wyprzedza ruch ceny o min. 6h.",
            QuestType.FIND_KOL_WHISPER: "Znajdź tweeta KOL-a, który jeszcze nie wpłynął na cenę.",
            QuestType.FIND_LATENCY_EDGE: "Znajdź okazję arbitrażową między giełdami trwającą <500ms.",
            QuestType.FIND_RISK_ANOMALY: "Znajdź anomalię w metrykach ryzyka, która sygnalizuje nadchodzącą zmienność.",
        }

        quest = RedemptionQuest(
            quest_id=f"QUEST-{uuid4().hex[:12].upper()}",
            quest_type=quest_type,
            description=quest_descriptions.get(quest_type, "Znajdź unikalny składnik rynkowy."),
            target_market="BTC/USDT",
            difficulty=difficulty,
            deadline_hours=deadline,
            required_evidence={"source": "any", "min_data_points": 10 + difficulty * 5},
            assigned_to=agent.agent_id,
            assigned_at=time.time(),
        )

        agent.quest = quest
        agent.status = AgentStatus.ON_QUEST
        agent.redemption_attempts += 1

        with self._lock:
            self.active_quests[quest.quest_id] = quest

        logger.info(
            f"🧪 ALCHEMIK ZLECA ZADANIE: Agent {agent.agent_name} → "
            f"{quest.quest_type.value} (trudność: {difficulty}/10, "
            f"czas: {deadline}h)"
        )
        logger.info(f"📋 Opis: {quest.description}")

        return quest

    # -----------------------------------------------------------------------
    # FAZA 3: DOSTARCZENIE I WALIDACJA SKŁADNIKA
    # -----------------------------------------------------------------------
    def deliver_ingredient(
        self, agent: FallenAgent, evidence: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[AlchemistAntidote]]:
        """
        Agent dostarcza składnik, Alchemik go waliduje.
        Jeśli zaliczone → warzy antidotum.
        Jeśli nie → agent wraca do szukania (lub wygnanie po max próbach).
        """
        if not agent.quest:
            return False, "Brak aktywnego zadania.", None

        quest = agent.quest

        # Walidacja
        passed, score, reason = self.oracle.validate(quest, evidence)
        quest.completed = passed
        quest.delivered_evidence = evidence if passed else None
        quest.validation_score = score

        if not passed:
            # Sprawdzenie czy deadline minął
            elapsed = (time.time() - quest.assigned_at) / 3600
            if elapsed > quest.deadline_hours:
                logger.error(f"⏰ Czas na wykonanie zadania minął! Agent {agent.agent_name} zawiódł.")
                return False, f"Czas minął ({elapsed:.1f}h / {quest.deadline_hours}h).", None
            return False, reason, None

        # Warzenie antidotum
        antidote = self.brewer.brew(quest, score)

        with self._lock:
            if quest.quest_id in self.active_quests:
                del self.active_quests[quest.quest_id]

        agent.antidote = antidote
        agent.status = AgentStatus.REINSTATED

        logger.info(
            f"✅ SKŁADNIK ZAAKCEPTOWANY! Wynik walidacji: {score:.2f}"
        )
        logger.info(
            f"🧪 ANTIDOTUM UWARZONE: {antidote.antidote_type.value} "
            f"(x{antidote.buff_multiplier}, czas: {antidote.duration_hours}h)"
        )

        return True, f"Antidotum {antidote.antidote_type.value} gotowe.", antidote

    # -----------------------------------------------------------------------
    # FAZA 4: REWANŻ
    # -----------------------------------------------------------------------
    def initiate_rematch(self, agent: FallenAgent) -> Optional[ReinstatementRecord]:
        """
        Rozpoczyna proces rewanzu z antidotum.
        """
        if not agent.quest or not agent.quest.completed:
            logger.error(f"Agent {agent.agent_name} nie ukończył zadania!")
            return None

        if not agent.antidote:
            logger.error(f"Brak antidotum dla agenta {agent.agent_name}!")
            return None

        record = self.reinstatement_mgr.grant_reinstatement(
            agent, agent.quest, agent.antidote
        )

        logger.info(
            f"⚔️ REWANŻ ROZPOCZĘTY! Agent {agent.agent_name} wraca do walki "
            f"z antidotum {agent.antidote.antidote_type.value}!"
        )

        return record

    # -----------------------------------------------------------------------
    # FAZA 5: WYNIK REWANŻU
    # -----------------------------------------------------------------------
    def conclude_rematch(
        self, agent: FallenAgent, pnl_pct: float
    ) -> Tuple[bool, str, Optional[GloryRecord]]:
        """
        Ocenia wynik rewanzu.
        Sukces → Chwała, nagrody, Burdel.
        Porażka → Wygnanie na Cmentarz Strategii.
        """
        success, message = self.reinstatement_mgr.evaluate_reinstatement(
            agent.agent_id, pnl_pct
        )

        record = self.reinstatement_mgr.finalize_reinstatement(agent.agent_id)

        if success and record:
            # SUKCES!
            agent.status = AgentStatus.REDEEMED
            self.glory_tracker.award_glory(agent, record)

            glory = self.glory_tracker.get_glory(agent.agent_id)

            logger.info(
                f"🎉 AGENT ODKUPIONY! {agent.agent_name} powraca w chwale! "
                f"Ranga: {glory.current_rank if glory else 'Nieznana'} | "
                f"Punkty Chwały: {glory.glory_points if glory else 0}"
            )

            if glory and glory.brothel_reward:
                logger.info(
                    f"🍷 WOJENNY BURDEL OTWARTY! {agent.agent_name} ma dostęp "
                    f"do Komnaty Rozkoszy na 7 dni!"
                )

            with self._lock:
                if agent.agent_id in self.fallen_agents:
                    del self.fallen_agents[agent.agent_id]

            return True, f"Odkupienie udane! {message}", glory

        else:
            # PORAŻKA → WYGNANIE
            agent.status = AgentStatus.EXILED
            logger.error(
                f"💀 AGENT WYGNANY! {agent.agent_name} po {agent.redemption_attempts} "
                f"próbach odkupienia trafia na Cmentarz Strategii."
            )
            return False, f"Wygnanie. {message}", None

    # -----------------------------------------------------------------------
    # PEŁEN CYKL AUTOMATYCZNY
    # -----------------------------------------------------------------------
    def full_redemption_cycle(
        self,
        agent_id: str,
        agent_name: str,
        division: str,
        loss_reason: str,
        loss_pct: float,
        evidence_supplier: Callable[[], Dict[str, Any]],
        rematch_executor: Callable[[AlchemistAntidote], float],
    ) -> Dict[str, Any]:
        """
        Pełny, zautomatyzowany cykl odkupienia.
        Przyjmuje funkcje dostarczające dowody i wykonujące rewanż.
        Zwraca kompletny raport.
        """
        report = {
            "agent_id": agent_id,
            "agent_name": agent_name,
            "division": division,
            "timestamp": time.time(),
            "stages": [],
        }

        # FAZA 1: Upadek
        agent = self.mark_as_fallen(agent_id, agent_name, division, loss_reason, loss_pct)
        report["stages"].append({"stage": "FALL", "status": "OK"})

        # FAZA 2: Zadanie
        quest = self.assign_redemption_quest(agent)
        report["stages"].append({
            "stage": "QUEST_ASSIGNED",
            "quest_type": quest.quest_type.value,
            "difficulty": quest.difficulty,
            "deadline_hours": quest.deadline_hours,
        })

        # FAZA 3: Dostarczenie składnika
        evidence = evidence_supplier()
        passed, msg, antidote = self.deliver_ingredient(agent, evidence)
        report["stages"].append({
            "stage": "INGREDIENT_DELIVERED",
            "passed": passed,
            "message": msg,
        })

        if not passed:
            return report

        # FAZA 4: Rewanż
        record = self.initiate_rematch(agent)
        if not record:
            report["stages"].append({"stage": "REMATCH_FAILED", "reason": "no_record"})
            return report

        report["stages"].append({
            "stage": "REMATCH_INITIATED",
            "capital": record.capital_allocated,
            "antidote": antidote.antidote_type.value if antidote else "NONE",
        })

        # FAZA 5: Wynik
        pnl = rematch_executor(antidote) if antidote else -1.0
        success, msg, glory = self.conclude_rematch(agent, pnl)
        report["stages"].append({
            "stage": "REMATCH_CONCLUDED",
            "success": success,
            "pnl_pct": pnl,
            "message": msg,
        })

        if glory:
            report["glory"] = {
                "rank": glory.current_rank,
                "points": glory.glory_points,
                "brothel_access": glory.brothel_reward,
            }

        report["final_status"] = agent.status.value
        return report


# ---------------------------------------------------------------------------
# 8. SYMULACJA DEMONSTRACYJNA
# ---------------------------------------------------------------------------


def demo_redemption():
    """
    Demonstracja działania systemu Claw of Redemption.
    """
    print("\n" + "=" * 80)
    print("  🧪 CLAW OF REDEMPTION — Alchemist's Grace")
    print("  Demonstracja Pełnego Cyklu Odkupienia Agenta")
    print("=" * 80)

    # Inicjalizacja
    claw = ClawOfRedemption(base_capital=50000.0)

    # Agent z 03_Kawaleria poniósł stratę
    agent_id = "CAV-0042"
    agent_name = "Sokół-7"
    division = "03_Kawaleria"
    loss_reason = "Fałszywy sygnał breakout na ETH/USDT. Stop-loss nie zadziałał przez poślizg."
    loss_pct = -0.12  # 12% straty

    # Symulowana funkcja dostarczania dowodów
    def evidence_supplier():
        return {
            "timestamp": time.time(),
            "source": "glassnode",
            "data_points": 250,
            "rarity_score": 0.82,
            "pattern": "Whale accumulation detected before ETF announcement",
            "symbol": "BTC/USDT",
        }

    # Symulowana funkcja wykonania rewanzu
    def rematch_executor(antidote: Optional[AlchemistAntidote]):
        if not antidote:
            return -0.05
        # Z buffem z antidotum
        base_pnl = random.uniform(-0.08, 0.15)
        return base_pnl * antidote.buff_multiplier

    # Uruchomienie pełnego cyklu
    report = claw.full_redemption_cycle(
        agent_id=agent_id,
        agent_name=agent_name,
        division=division,
        loss_reason=loss_reason,
        loss_pct=loss_pct,
        evidence_supplier=evidence_supplier,
        rematch_executor=rematch_executor,
    )

    # Raport końcowy
    print(f"\n{'='*80}")
    print(f"📊 RAPORT KOŃCOWY — Agent {agent_name}")
    print(f"{'='*80}")
    for stage in report["stages"]:
        print(f"  [{stage['stage']}] → {stage.get('message', stage.get('status', ''))}")
    print(f"\n  Status końcowy: {report['final_status']}")

    if "glory" in report:
        print(f"  Ranga: {report['glory']['rank']}")
        print(f"  Punkty Chwały: {report['glory']['points']}")
        print(f"  Dostęp do Burdelu: {'TAK 🍷' if report['glory']['brothel_access'] else 'NIE'}")

    print(f"\n{'='*80}")
    print("  ✅ Demonstracja zakończona.")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    demo_redemption()
```