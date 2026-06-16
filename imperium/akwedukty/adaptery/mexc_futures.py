"""
🔥 AdapterMEXCFutures — most danych futures z MEXC (PUBLICZNE contract API) → PSY-01/04.

DLACZEGO MEXC, nie Binance (Prawo I — poprawność dla LIVE):
  AdapterFutures (futures.py) ciągnie funding/OI z Binance fapi. Ale Cezar handluje
  na MEXC — funding, który FAKTYCZNIE PŁACI, to funding MEXC, nie Binance. Dla PSY-01
  (contrarian na ekstremalnym fundingu) sygnał musi pochodzić z giełdy, na której
  trzymana jest pozycja. Ten adapter daje funding/OI rodzime dla MEXC.

Źródła (DARMOWE, BEZ KLUCZA API — publiczne endpointy contract.mexc.com):
  • Funding Rate:  GET https://contract.mexc.com/api/v1/contract/funding_rate/{SYMBOL}
                   → data.fundingRate (float, np. 0.0001).  SYMBOL = "BTC_USDT".
  • Ticker (OI):   GET https://contract.mexc.com/api/v1/contract/ticker?symbol={SYMBOL}
                   → data.holdVol (open interest kontraktów).

ZAKRES (Prawo XV — uczciwie, bez halucynacji):
  MEXC nie ma łatwego PUBLICZNEGO globalnego long/short account ratio jak Binance.
  Dlatego ten adapter budzi PSY-01 (Funding) i PSY-04 (OI). PSY-02 (Long/Short)
  pozostaje przy AdapterFutures (sentyment rynkowy jest cross-giełdowy — OK).

BEZPIECZEŃSTWO (NIENARUSZALNE): endpointy publiczne — bez klucza. Gdy dojdą zlecenia
  podpisane, klucze WYŁĄCZNIE z os.getenv (MEXC_API_KEY/MEXC_SECRET), nigdy w kodzie.

WSTRZYKIWANY FETCHER: `pobierz()` deleguje do `self._fetcher(url)` — produkcja: urllib
  (stdlib), testy: mock URL→próbka → pełny test OFFLINE, deterministyczny, bez sieci.

OPEN_INTEREST_PREV (Prawo I): pamięta poprzednie OI per symbol (dla PSY-04 dywergencji).
  Pierwszy odczyt: OI_PREV = OI (brak dywergencji — PSY-04 abstynuje).
"""

import json
import logging
from typing import Dict, Any, Optional

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.psychologia import NeuronFundingExtreme, NeuronOIDiv

logger = logging.getLogger("Adapter")


class AdapterMEXCFutures(AdapterDanych):
    """
    Most do PSY-01 (Funding) i PSY-04 (Open Interest) z rodzimego MEXC contract API.
    Dane z publicznych endpointów contract.mexc.com — bez klucza API.
    """
    NAZWA = "MEXCFutures(mexc-public)"
    KLUCZE = ["FUNDING_RATE", "OPEN_INTEREST", "OPEN_INTEREST_PREV"]
    _NEURONY = (NeuronFundingExtreme, NeuronOIDiv)
    _POWOD_USPIENIA = "Wymaga publicznego contract API MEXC. Adapter odpięty."

    URL_FUNDING = "https://contract.mexc.com/api/v1/contract/funding_rate/{s}"
    URL_TICKER = "https://contract.mexc.com/api/v1/contract/ticker?symbol={s}"

    def __init__(self, fetcher=None, timeout: int = 8):
        """fetcher: opcjonalny callable(url)->str (surowy JSON). Domyślnie HTTP urllib."""
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout
        self._oi_poprzednie: Dict[str, float] = {}

    def _fetch_http(self, url: str) -> str:
        """Pobranie surowego JSON (urllib, stdlib — bez nowych zależności)."""
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

    @staticmethod
    def _na_symbol_mexc(symbol: str) -> str:
        """'BTCUSDT' / 'BTC/USDT' → 'BTC_USDT' (format contract MEXC)."""
        s = (symbol or "BTC_USDT").upper().replace("/", "").replace("_", "")
        if s.endswith("USDT") and len(s) > 4:
            return s[:-4] + "_USDT"
        return s

    @staticmethod
    def _bezpieczny_float(d: dict, klucz: str) -> Optional[float]:
        wart = d.get(klucz)
        if wart is None:
            return None
        try:
            return float(wart)
        except (TypeError, ValueError):
            return None

    def pobierz(self, symbol: str) -> Dict[str, Any]:
        """
        Zwraca {FUNDING_RATE, OPEN_INTEREST, OPEN_INTEREST_PREV}. Każdy None gdy dane
        brak/uszkodzone (wzbogac() pominie None — neuron abstynuje, nie fałszuje).
        """
        s = self._na_symbol_mexc(symbol)
        wynik: Dict[str, Any] = {
            "FUNDING_RATE": None, "OPEN_INTEREST": None, "OPEN_INTEREST_PREV": None,
        }

        # Funding rate (MEXC zawija dane w {"success":true,"data":{...}})
        try:
            raw = json.loads(self._fetcher(self.URL_FUNDING.format(s=s)))
            data = raw.get("data", raw) if isinstance(raw, dict) else {}
            wynik["FUNDING_RATE"] = self._bezpieczny_float(data, "fundingRate")
        except Exception as e:
            logger.warning(f"[Adapter:MEXCFutures] funding {s} padł: {e}")

        # Open Interest z tickera (holdVol) + pamięć poprzedniej wartości
        try:
            raw = json.loads(self._fetcher(self.URL_TICKER.format(s=s)))
            data = raw.get("data", raw) if isinstance(raw, dict) else {}
            oi = self._bezpieczny_float(data, "holdVol")
            if oi is not None:
                wynik["OPEN_INTEREST"] = oi
                wynik["OPEN_INTEREST_PREV"] = self._oi_poprzednie.get(s, oi)
                self._oi_poprzednie[s] = oi
        except Exception as e:
            logger.warning(f"[Adapter:MEXCFutures] ticker/OI {s} padł: {e}")

        return wynik
