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
from typing import Optional

from openai import OpenAI  # DeepSeek kompatybilny z OpenAI

logger = logging.getLogger("GlosImperium")


def _napraw_zepsuty_cert_env() -> None:
    """
    Zabezpieczenie (Prawo XV): gdy SSL_CERT_FILE/SSL_CERT_DIR wskazuje na plik/katalog,
    który NIE ISTNIEJE, httpx/openai wywala się FileNotFoundError zanim dojdzie do API
    (realny przypadek Cezara 2026-07-01: leftover C:\\...\\Temp\\cacert.pem). Usuwamy taki
    martwy wpis z env → biblioteki wracają do domyślnych certów (certifi). Nie ruszamy
    poprawnych ścieżek — tylko nieistniejące.
    """
    # SSL_CERT_FILE = pojedynczy plik. SSL_CERT_DIR = lista katalogów (os.pathsep) —
    # nie kasuj jeśli CHOĆ JEDEN komponent istnieje (nie psuj enterprise CA-bundle).
    for zmienna, sprawdz, lista in (("SSL_CERT_FILE", os.path.isfile, False),
                                    ("SSL_CERT_DIR", os.path.isdir, True)):
        sciezka = os.environ.get(zmienna)
        if not sciezka:
            continue
        czesci = sciezka.split(os.pathsep) if lista else [sciezka]
        if not any(sprawdz(c) for c in czesci if c):
            logger.warning(f"[GlosImperium] {zmienna}='{sciezka}' nie wskazuje na istniejącą "
                           "ścieżkę — usuwam z env (fallback na domyślne certyfikaty).")
            os.environ.pop(zmienna, None)


class GlosImperium:
    """Most do DeepSeek. Jedyne wejście LLM w Imperium."""

    # Migracja V4 (potwierdzone api-docs.deepseek.com, 2026): legacy `deepseek-chat` i
    # `deepseek-reasoner` WYCOFANE 2026-07-24 → nowe id V4. base_url bez zmian.
    #   deepseek-chat     → deepseek-v4-flash (non-thinking, tani ~$0.14/1M in)
    #   deepseek-reasoner → deepseek-v4-flash thinking / deepseek-v4-pro (premium)
    MODELE = {
        "szybki": "deepseek-v4-flash",   # tani, do debaty Senatu + zwiad Bibliotekarza
        "mysliciel": "deepseek-v4-pro",  # premium reasoning, do decyzji Cesarza
    }

    def __init__(self, model: str = "deepseek-v4-flash"):
        klucz = os.getenv("DEEPSEEK_API_KEY")
        if not klucz:
            raise EnvironmentError(
                "Brak DEEPSEEK_API_KEY w zmiennych środowiskowych!\n"
                "Windows: setx DEEPSEEK_API_KEY \"twój-klucz\"\n"
                "Linux/Mac: export DEEPSEEK_API_KEY=\"twój-klucz\"\n"
                "NIGDY nie wklejaj klucza bezpośrednio w kod."
            )
        _napraw_zepsuty_cert_env()   # broni przed martwym SSL_CERT_FILE (Prawo XV)
        self.client = OpenAI(
            api_key=klucz,
            base_url="https://api.deepseek.com/v1",
        )
        self.model = model
        # Ustawiane po KAŻDYM udanym wywołaniu (patrz zapytaj). None = jeszcze nie pytano
        # albo API nie podało zużycia — mierzący ma odróżnić „brak danych" od „zero kosztu".
        self.ostatnie_zuzycie = None
        self.ostatni_model: Optional[str] = None
        logger.info(f"[GlosImperium] Zainicjalizowany. Model: {self.model}")

    def zapytaj(self, system_prompt: str, tresc: str, temperatura: float = 0.7,
                profil: Optional[str] = None, model: Optional[str] = None,
                thinking: Optional[dict] = None,
                reasoning_effort: Optional[str] = None) -> str:
        """
        Wysyła pytanie do DeepSeek. Zwraca odpowiedź jako string.

        Po udanej odpowiedzi para `prompt → odpowiedź` trafia do NOTARIUSA (surowiec Szkoły
        TIRO, Filar 2). Most jest jedynym wejściem LLM w Imperium, więc jedno wpięcie tutaj
        łapie WSZYSTKICH wołających (newsy, auto-lekcje, zwiad) — bez zmian u nich.
        Zapis jest czysto obserwacyjny: nie dotyka ścieżki decyzyjnej i NIGDY nie może
        wywrócić wywołania API (patrz `notarius` — żelazna zasada).

        DOBÓR GŁĘBOKOŚCI PER WYWOŁANIE (2026-07-21, rozkaz o rozbudowie Hyginusa):
        `profil` oddaje decyzję DISPENSATOROWI (Szafarzowi) — „zwiad" kupuje objętość tanio,
        „osad" kupuje premium reasoning. Jawne `model`/`thinking`/`reasoning_effort`
        NADPISUJĄ profil, bo wołający wie więcej niż tabela. Bez żadnego z tych argumentów
        zachowanie jest IDENTYCZNE jak przed zmianą — model z `__init__`, zero dodatkowych
        pól w żądaniu (wsteczna zgodność: wszyscy dotychczasowi wołający nie widzą różnicy).

        Parametry niestandardowe idą przez `extra_body`, bo `thinking` nie należy do
        schematu OpenAI. Błąd API celowo NIE jest łykany: cicho zignorowany tryb oznaczałby
        płacenie za rozumowanie, którego nie dostajemy (albo odwrotnie) — a to dokładnie
        klasa „mechanizm, który przy awarii wygląda na sprawny".
        """
        param: dict = {}
        if profil is not None:
            from imperium.cesarz.dispensator import dobierz
            param.update(dobierz(profil))
        if model is not None:
            param["model"] = model
        if thinking is not None:
            param["thinking"] = thinking
        if reasoning_effort is not None:
            param["reasoning_effort"] = reasoning_effort

        # Model FAKTYCZNIE użyty — nie ten z __init__. Bez tego NOTARIUS opisywałby pary
        # nauczyciela cudzą nazwą, a TIRO uczyłby się z metryką wskazującą inny model.
        uzyty_model = param.pop("model", self.model)
        extra = {k: v for k, v in param.items() if v is not None}

        try:
            odp = self.client.chat.completions.create(
                model=uzyty_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": tresc},
                ],
                temperature=temperatura,
                **({"extra_body": extra} if extra else {}),
            )
            odpowiedz = odp.choices[0].message.content
            # ZUŻYCIE OSTATNIEGO WYWOŁANIA — bez tego DISPENSATOR.koszt_usd nie miał czym
            # liczyć: cennik i wzór istniały, a FAKTYCZNE `usage` szło do kosza, więc koszt
            # profilu dało się wyłącznie oszacować (Prawo XV: zdolność zbudowana, niekarmiona).
            # Świadomie jako STAN INSTANCJI, nie zmiana typu zwracanego: żaden z dotychczasowych
            # wołających nie widzi różnicy (wsteczna zgodność), a mierzący ma dostęp do prawdy.
            self.ostatnie_zuzycie = getattr(odp, "usage", None)
            self.ostatni_model = uzyty_model
        except Exception as e:
            logger.error(f"[GlosImperium] Błąd API (model={uzyty_model}, tryb={extra}): {e}")
            raise

        self._protokoluj(system_prompt, tresc, odpowiedz, temperatura, uzyty_model)
        return odpowiedz

    def _protokoluj(self, system_prompt: str, tresc: str, odpowiedz: str,
                    temperatura: float, model: Optional[str] = None) -> None:
        """
        Oddaj parę pisarzowi (TIRO/E2). Świadomie łykamy KAŻDY wyjątek, łącznie z ImportError:
        gdyby organu zabrakło albo dysk odmówił, nauczyciel ma mówić dalej. Protokół jest
        dodatkiem do mowy, nigdy jej warunkiem.

        `model` to model FAKTYCZNIE użyty w tym wywołaniu (może różnić się od `self.model`,
        odkąd DISPENSATOR dobiera go per zadanie). Etykieta nauczyciela musi zgadzać się
        z tym, kto naprawdę mówił — inaczej TIRO uczy się z fałszywym opisem źródła.
        """
        try:
            from imperium.biblioteki.notarius import zapisz_pare
            zapisz_pare(system_prompt=system_prompt, tresc=tresc, odpowiedz=odpowiedz,
                        model=model or self.model, temperatura=temperatura)
        except Exception as e:  # noqa: BLE001 — awaria pisarza ≠ awaria mostu
            logger.warning(f"[GlosImperium] Notarius nie zapisał pary: {e}")

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
