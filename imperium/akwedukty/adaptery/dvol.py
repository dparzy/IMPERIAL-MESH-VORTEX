"""
😱 AdapterDVOL — indeks strachu opcji (PSY-05, Deribit DVOL).

Źródło: Deribit public API `get_volatility_index_data` — DARMOWE, bez klucza API.
  DVOL = implikowana zmienność opcji BTC/ETH („crypto VIX"), miernik strachu rynku.

DLACZEGO (walidacja pomiarem, 2026-07-15): DVOL POZIOM ma IC +0.16 @7d na zwroty BTC
  (kontrariański — wysoki strach = okazja LONG), zgodnie z Sinclair/VIX. Zmierzone przez
  narzedzia/pomiar_dvol_ic.py (PAVOR) PRZED wpięciem (Prawo I, ZASADA WPIĘCIA).

OPT-IN (ZASADA WPIĘCIA W ŚCIEŻKĘ DECYZYJNĄ): adapter wpinany TYLKO za flagą (--dvol,
  domyślnie OFF). Bez niego PSY-05 abstynuje (Prawo XV) — zero wpływu na decyzje aż
  do walidacji A/B. Walidacja WSTĘPNA (~16-23 mies. historii, jeden reżim).

WSTRZYKIWANY FETCHER (Prawo XIX): `pobierz()` deleguje do `self._fetcher(waluta)`.
  - produkcja: `_fetch_http` (urllib, stdlib — zero nowych zależności)
  - testy: wstrzykujemy mock zwracający próbkę JSON → pełny test OFFLINE.

BEZPIECZEŃSTWO: API bez klucza. Gdyby wymagało — klucz WYŁĄCZNIE z os.getenv.
"""

import json
import logging
import time

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.psychologia import NeuronDVOL

logger = logging.getLogger("Adapter")


class AdapterDVOL(AdapterDanych):
    """
    Most do PSY-05 NeuronDVOL. Dostarcza DVOL_INDEX (implikowana zmienność opcji).
    Indeks globalny per waluta bazowa — `symbol` mapowany na BTC/ETH (domyślnie BTC).
    """
    NAZWA = "DVOL(Deribit)"
    KLUCZE = ["DVOL_INDEX"]
    _NEURONY = (NeuronDVOL,)
    _POWOD_USPIENIA = "Wymaga zewnętrznego API opcji (Deribit DVOL) — opt-in --dvol."

    URL = ("https://www.deribit.com/api/v2/public/get_volatility_index_data"
           "?currency={cur}&start_timestamp={start}&end_timestamp={end}&resolution=3600")

    def __init__(self, fetcher=None, timeout: int = 8):
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout

    def _waluta(self, symbol: str) -> str:
        s = (symbol or "").upper()
        return "ETH" if s.startswith("ETH") else "BTC"

    def _fetch_http(self, waluta: str = "BTC") -> str:
        """Pobiera surowy JSON DVOL z Deribit (ostatnie ~24h, resolution 1h)."""
        import urllib.request
        end = int(time.time() * 1000)
        start = end - 24 * 3600 * 1000
        url = self.URL.format(cur=waluta, start=start, end=end)
        req = urllib.request.Request(url, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

    def pobierz(self, symbol: str = "") -> dict:
        """
        Zwraca {"DVOL_INDEX": float} (ostatnia wartość close) lub {"DVOL_INDEX": None}
        gdy danych brak/uszkodzone (wzbogac() pominie None — neuron śpi dalej).
        """
        try:
            surowe = self._fetcher(self._waluta(symbol))
            d = json.loads(surowe)
            data = (d.get("result") or {}).get("data") or []
            if not data:
                return {"DVOL_INDEX": None}
            # rekord: [timestamp, open, high, low, close]; bierzemy ostatni close
            close = data[-1][4]
            return {"DVOL_INDEX": float(close) if close is not None else None}
        except Exception as e:
            logger.warning(f"[Adapter:DVOL] pobranie padło: {e}")
            return {"DVOL_INDEX": None}
