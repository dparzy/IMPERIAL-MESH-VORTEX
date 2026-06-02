"""
😱 AdapterFearGreed — PIERWSZY prawdziwy adapter API (PSY-03).

Źródło: alternative.me Fear & Greed Index — DARMOWE, bez klucza API.
  GET https://api.alternative.me/fng/?limit=1
  Odpowiedź: {"data":[{"value":"40","value_classification":"Fear",...}], ...}

DLACZEGO TEN PIERWSZY (decyzja zatwierdzona przez Cezara):
  - darmowe, bez klucza → zero ryzyka bezpieczeństwa, idealny pierwszy test na żywo
  - budzi dokładnie 1 neuron (PSY-03) → granularne, czyste wybudzenie
  - sentyment globalny (strach/chciwość rynku) → kontrariański sygnał

WSTRZYKIWANY FETCHER (Prawo XIX: kod+testy zanim coś "istnieje"):
  `pobierz()` deleguje pobranie surowego JSON do `self._fetcher()`.
  - produkcja: domyślny `_fetch_http` (urllib, stdlib — zero nowych zależności)
  - testy: wstrzykujemy fetcher zwracający próbkę JSON → pełny test OFFLINE,
           deterministyczny, bez sieci (zgodnie z runnerem "bez zależności")

BEZPIECZEŃSTWO: to API nie wymaga klucza. Gdyby wymagało — klucz WYŁĄCZNIE
  z os.getenv, nigdy w kodzie (Prawo bezpieczeństwa).

PRAWO XV: budzi PSY-03 tylko gdy adapter podpięty i dostarcza FEAR_GREED_INDEX.
"""

import json
import logging

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.psychologia import NeuronFearGreed

logger = logging.getLogger("Adapter")


class AdapterFearGreed(AdapterDanych):
    """
    Most do PSY-03 NeuronFearGreed. Dostarcza FEAR_GREED_INDEX (0-100) z alternative.me.
    Sentyment jest globalny (cały rynek krypto) — `symbol` jest ignorowany.
    """
    NAZWA = "FearGreed(alternative.me)"
    KLUCZE = ["FEAR_GREED_INDEX"]
    _NEURONY = (NeuronFearGreed,)
    _POWOD_USPIENIA = "Wymaga zewnętrznego API sentymentu (alternative.me / CoinGlass)."

    URL = "https://api.alternative.me/fng/?limit=1"

    def __init__(self, fetcher=None, timeout: int = 8):
        """
        fetcher: opcjonalny callable() -> str (surowy JSON). Domyślnie HTTP (urllib).
                 W testach wstrzykujemy mock zwracający próbkę → pełny test offline.
        timeout: limit czasu HTTP w sekundach.
        """
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout

    def _fetch_http(self) -> str:
        """Domyślne pobranie surowego JSON z alternative.me (urllib, stdlib)."""
        import urllib.request
        req = urllib.request.Request(self.URL, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

    def pobierz(self, symbol: str = "") -> dict:
        """
        Zwraca {"FEAR_GREED_INDEX": float 0-100} lub {"FEAR_GREED_INDEX": None}
        gdy danych brak/uszkodzone (wzbogac() pominie None — neuron śpi dalej).
        """
        surowe = self._fetcher()
        d = json.loads(surowe)
        data = d.get("data") or []
        if not data:
            logger.warning("[Adapter:FearGreed] pusta sekcja 'data' w odpowiedzi API")
            return {"FEAR_GREED_INDEX": None}
        wartosc = data[0].get("value")
        if wartosc is None:
            return {"FEAR_GREED_INDEX": None}
        return {"FEAR_GREED_INDEX": float(wartosc)}
