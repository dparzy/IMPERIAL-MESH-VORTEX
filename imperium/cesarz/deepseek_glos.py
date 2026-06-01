"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       GlosImperium — Most do DeepSeek API v1.0                              ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                                  ║
║  Jedyne wejście LLM w całym Imperium (Prawo: jeden most, nie wiele furtek)  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Zasady:
- KLUCZ ZAWSZE z zmiennej środowiskowej DEEPSEEK_API_KEY (NIGDY w kodzie!)
- DeepSeek NIE liczy matematyki — tylko INTERPRETUJE gotowe liczby z Bramy
- Jeden obiekt GlosImperium — współdzielony przez Cesarza i Senat
"""

import os
import logging
from openai import OpenAI  # DeepSeek kompatybilny z OpenAI

logger = logging.getLogger("GlosImperium")


class GlosImperium:
    """Most do DeepSeek. Jedyne wejście LLM w Imperium."""

    MODELE = {
        "szybki": "deepseek-chat",     # tani, do debaty Senatu
        "mysliciel": "deepseek-reasoner",  # droższy, do decyzji Cesarza
    }

    def __init__(self, model: str = "deepseek-chat"):
        klucz = os.getenv("DEEPSEEK_API_KEY")
        if not klucz:
            raise EnvironmentError(
                "Brak DEEPSEEK_API_KEY w zmiennych środowiskowych!\n"
                "Windows: setx DEEPSEEK_API_KEY \"twój-klucz\"\n"
                "Linux/Mac: export DEEPSEEK_API_KEY=\"twój-klucz\"\n"
                "NIGDY nie wklejaj klucza bezpośrednio w kod."
            )
        self.client = OpenAI(
            api_key=klucz,
            base_url="https://api.deepseek.com/v1",
        )
        self.model = model
        logger.info(f"[GlosImperium] Zainicjalizowany. Model: {self.model}")

    def zapytaj(self, system_prompt: str, tresc: str, temperatura: float = 0.7) -> str:
        """Wysyła pytanie do DeepSeek. Zwraca odpowiedź jako string."""
        try:
            odp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": tresc},
                ],
                temperature=temperatura,
            )
            return odp.choices[0].message.content
        except Exception as e:
            logger.error(f"[GlosImperium] Błąd API: {e}")
            raise

    def test_polaczenia(self) -> bool:
        """Sprawdź czy klucz działa. Uruchom to zanim wpinasz w cykl."""
        try:
            odp = self.zapytaj(
                system_prompt="Jesteś asystentem Imperium. Odpowiadaj krótko.",
                tresc="Powiedz 'Cesarz słyszy' po polsku.",
                temperatura=0.1,
            )
            logger.info(f"[GlosImperium] Test OK: {odp.strip()}")
            print(f"✅ Połączenie z DeepSeek działa! Odpowiedź: {odp.strip()}")
            return True
        except Exception as e:
            print(f"❌ Połączenie NIEUDANE: {e}")
            return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s')
    glos = GlosImperium()
    glos.test_polaczenia()
