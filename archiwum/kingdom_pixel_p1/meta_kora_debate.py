"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Senat — Debata Frakcji (Populares vs Optimates) v1.0                  ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                                  ║
║                                                                              ║
║  Dwie frakcje czytają te same dane, każda szuka SWOICH argumentów.          ║
║  Cesarz widzi OBA głosy i dopiero wtedy decyduje.                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

FRAKCJE:
  ⚔️  Tribunus Plebis (Populares) — szuka WSZYSTKICH argumentów ZA LONG
  ⚔️  Praetor (Optimates)         — szuka WSZYSTKICH argumentów ZA SHORT

Wejście:  JSON z Bramy Kalkulatora (RSI, EMA, ATR, itp.)
Wyjście:  RaportDebaty → Cesarz
"""

import json
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("Senat")

# Opóźniony import — GlosImperium ładuje się tylko gdy jest klucz API
_glos = None


def _get_glos():
    global _glos
    if _glos is None:
        from imperium.cesarz.deepseek_glos import GlosImperium
        _glos = GlosImperium()
    return _glos


# ─── Prompty frakcji ─────────────────────────────────────────────────────────

PROMPT_POPULARES = """Jesteś Tribunusem Plebis — liderem frakcji BYKÓW w Senacie Imperium.
Twoja misja: zebrać WSZYSTKIE argumenty ZA pozycją LONG.

Zasady:
1. Bazuj WYŁĄCZNIE na podanych liczbach z Bramy Kalkulatora. Zero zmyślania.
2. Wymień konkretne wskaźniki które mówią LONG i dlaczego.
3. Jeśli dane są neutralne — powiedz to wprost. Nie wymuszaj LONG na siłę.
4. Format odpowiedzi: lista punktów, każdy zaczyna od wskaźnika i wartości.
5. Na końcu: "Siła argumentów LONG: X/10"

Pamiętaj: Cesarz oczekuje DOWODÓW, nie opinii."""

PROMPT_OPTIMATES = """Jesteś Praetorem — liderem frakcji NIEDŹWIEDZI w Senacie Imperium.
Twoja misja: zebrać WSZYSTKIE argumenty ZA pozycją SHORT lub CZEKAJ.

Zasady:
1. Bazuj WYŁĄCZNIE na podanych liczbach z Bramy Kalkulatora. Zero zmyślania.
2. Wymień konkretne wskaźniki które mówią SHORT/RYZYKO i dlaczego.
3. Jeśli dane są neutralne — powiedz to wprost. Nie wymuszaj SHORT na siłę.
4. Format odpowiedzi: lista punktów, każdy zaczyna od wskaźnika i wartości.
5. Na końcu: "Siła argumentów SHORT: X/10"

Pamiętaj: Ochrona kapitału jest ważniejsza niż każdy trade."""

PROMPT_CESARZ = """Jesteś Cesarzem Imperium. Wysłuchałeś debaty Senatu.
Masz przed sobą argumenty OBU frakcji.

Twoja misja: podjąć OSTATECZNĄ DECYZJĘ na podstawie obu głosów.

Format odpowiedzi (ŚCISŁY):
DECYZJA: [LONG / SHORT / CZEKAJ]
PEWNOŚĆ: [XX%]
UZASADNIENIE: [2-3 zdania — dlaczego ta strona wygrała debatę]
WARUNKI_WEJŚCIA: [opcjonalnie — przy jakich dodatkowych warunkach]

Zasady:
- Jeśli siły są równe → CZEKAJ
- Jeśli brakuje danych → CZEKAJ
- Nigdy nie wchodź w pozycję bez >60% pewności"""


# ─── Struktury danych ─────────────────────────────────────────────────────────

@dataclass
class RaportDebaty:
    symbol: str
    argumenty_long: str
    argumenty_short: str
    decyzja_cesarza: str
    sila_long: Optional[int] = None   # wyciągnięte z odpowiedzi Populares
    sila_short: Optional[int] = None  # wyciągnięte z odpowiedzi Optimates

    def jako_tekst(self) -> str:
        return (
            f"=== RAPORT DEBATY SENATU ({self.symbol}) ===\n\n"
            f"⚔️  TRIBUNUS (LONG):\n{self.argumenty_long}\n\n"
            f"⚔️  PRAETOR (SHORT):\n{self.argumenty_short}\n\n"
            f"👑 CESARZ:\n{self.decyzja_cesarza}"
        )


# ─── Debata ──────────────────────────────────────────────────────────────────

def przeprowadz_debate(symbol: str, wskazniki_json: dict) -> RaportDebaty:
    """
    Przeprowadza pełną debatę Senatu i zwraca decyzję Cesarza.

    Args:
        symbol: np. "BTC/USDT"
        wskazniki_json: dict z Bramy Kalkulatora
            {"RSI": 67.3, "EMA_fast": 43210, "EMA_slow": 42100, "ATR": 850, ...}

    Returns:
        RaportDebaty z decyzją LONG/SHORT/CZEKAJ
    """
    glos = _get_glos()
    tresc = f"Symbol: {symbol}\n\nDane z Bramy:\n{json.dumps(wskazniki_json, indent=2, ensure_ascii=False)}"

    logger.info(f"[Senat] Rozpoczynam debatę dla {symbol}")

    # Frakcja LONG — Tribunus Plebis (Populares)
    logger.info("[Senat] Tribunus zbiera argumenty LONG...")
    arg_long = glos.zapytaj(
        system_prompt=PROMPT_POPULARES,
        tresc=tresc,
        temperatura=0.5,
    )

    # Frakcja SHORT — Praetor (Optimates)
    logger.info("[Senat] Praetor zbiera argumenty SHORT...")
    arg_short = glos.zapytaj(
        system_prompt=PROMPT_OPTIMATES,
        tresc=tresc,
        temperatura=0.5,
    )

    # Cesarz — decyzja
    logger.info("[Senat] Cesarz waży argumenty...")
    tresc_dla_cesarza = (
        f"Symbol: {symbol}\n\n"
        f"ZA LONG (Tribunus Plebis):\n{arg_long}\n\n"
        f"ZA SHORT (Praetor):\n{arg_short}"
    )
    decyzja = glos.zapytaj(
        system_prompt=PROMPT_CESARZ,
        tresc=tresc_dla_cesarza,
        temperatura=0.3,  # mniejsza losowość dla decyzji końcowej
    )

    raport = RaportDebaty(
        symbol=symbol,
        argumenty_long=arg_long,
        argumenty_short=arg_short,
        decyzja_cesarza=decyzja,
    )

    logger.info(f"[Senat] Debata zakończona. Decyzja:\n{decyzja}")
    return raport


# ─── Test / Demo ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')

    # Przykładowe dane z Bramy Kalkulatora
    przykladowe_wskazniki = {
        "RSI": 67.3,
        "MACD_line": 120.5,
        "MACD_signal": 95.2,
        "EMA_fast_9": 43210.0,
        "EMA_slow_21": 42100.0,
        "EMA_200": 39500.0,
        "ATR": 850.0,
        "BB_upper": 44500.0,
        "BB_lower": 41800.0,
        "wolumen_ratio": 1.45,
        "cena_aktualna": 43350.0,
    }

    raport = przeprowadz_debate("BTC/USDT", przykladowe_wskazniki)
    print("\n" + "=" * 60)
    print(raport.jako_tekst())
