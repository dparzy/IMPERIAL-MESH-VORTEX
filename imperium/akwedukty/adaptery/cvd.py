"""
📊 AdapterCVD — most danych trade-feed: Binance aggTrades PUBLICZNE → V-03.

Źródło (DARMOWE, BEZ KLUCZA API — publiczny feed transakcji futures):
  • Agg Trades: GET https://fapi.binance.com/fapi/v1/aggTrades?symbol=BTCUSDT&limit=1000
    Każdy rekord ma pole "m" (isBuyerMaker) + "q" (ilość):
      m == false → agresorem był KUPUJĄCY (market buy)  → wolumen BUY
      m == true  → agresorem był SPRZEDAJĄCY (market sell) → wolumen SELL
    CVD (Cumulative Volume Delta) = Σ(buy) − Σ(sell) z okna ostatnich transakcji.

DLACZEGO BINANCE PUBLIC (Prawo bezpieczeństwa):
  aggTrades nie wymaga klucza ani podpisu — publiczny strumień transakcji.
  OHLCV nie zawiera strony agresora; CVD jest jedyną drogą do "kto był silniejszy".
  Gdy przejdziemy na MEXC z kluczem — klucz WYŁĄCZNIE z os.getenv, nigdy w kodzie.

WSTRZYKIWANY FETCHER (Prawo XIX: kod+testy zanim coś "istnieje"):
  `pobierz()` deleguje pobranie surowego JSON do `self._fetcher(url)`.
  - produkcja: domyślny `_fetch_http` (urllib, stdlib — zero nowych zależności)
  - testy: wstrzykujemy fetcher zwracający próbkę → pełny test OFFLINE.

CVD_PREV (Prawo I — bez halucynacji):
  Adapter pamięta poprzednią wartość CVD per symbol (między cyklami). Przy
  pierwszym odczycie CVD_PREV = CVD (brak dywergencji — V-03 patrzy na znak CVD).

PRAWO XV: budzi V-03 tylko gdy adapter podpięty i dostarcza dane.
"""

import json
import logging
from typing import Dict, Any, Optional

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.wolumen import NeuronCVD

logger = logging.getLogger("Adapter")


class AdapterCVD(AdapterDanych):
    """
    Most do V-03 NeuronCVD. Liczy CVD z publicznego feedu aggTrades (Binance fapi).
    Dostarcza CVD i CVD_PREV (pamięć poprzedniego odczytu dla dywergencji).
    """
    NAZWA = "CVD(binance-public)"
    KLUCZE = ["CVD", "CVD_PREV"]
    _NEURONY = (NeuronCVD,)
    _POWOD_USPIENIA = "Wymaga publicznego trade-feedu (Binance aggTrades / MEXC). Adapter odpięty."

    URL_AGG = "https://fapi.binance.com/fapi/v1/aggTrades?symbol={s}&limit={lim}"

    def __init__(self, fetcher=None, timeout: int = 8, limit: int = 1000):
        """
        fetcher: opcjonalny callable(url:str) -> str (surowy JSON). Domyślnie HTTP.
        limit:   ile ostatnich aggTrades brać do okna CVD (max 1000 na Binance).
        """
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout
        self.limit = limit
        self._cvd_poprzednie: Dict[str, float] = {}  # pamięć CVD per symbol

    def _fetch_http(self, url: str) -> str:
        """Domyślne pobranie surowego JSON (urllib, stdlib — bez nowych zależności)."""
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

    def pobierz(self, symbol: str) -> Dict[str, Any]:
        """
        Zwraca {CVD, CVD_PREV} z okna ostatnich aggTrades. CVD None gdy dane
        brak/uszkodzone (wzbogac() pominie None — V-03 abstynuje, nie fałszuje).
        """
        s = (symbol or "BTCUSDT").upper().replace("/", "")
        wynik: Dict[str, Any] = {"CVD": None, "CVD_PREV": None}

        try:
            raw = json.loads(self._fetcher(self.URL_AGG.format(s=s, lim=self.limit)))
        except Exception as e:
            logger.warning(f"[Adapter:CVD] aggTrades {s} padł: {e}")
            return wynik

        if not isinstance(raw, list) or not raw:
            return wynik

        buy = sell = 0.0
        for t in raw:
            try:
                qty = float(t.get("q"))
            except (TypeError, ValueError):
                continue
            if t.get("m") is True:      # buyer maker → agresor SPRZEDAJĄCY
                sell += qty
            else:                       # agresor KUPUJĄCY
                buy += qty

        cvd = buy - sell
        wynik["CVD"] = cvd
        # CVD_PREV: poprzedni odczyt; przy pierwszym = bieżący (brak dywergencji)
        wynik["CVD_PREV"] = self._cvd_poprzednie.get(s, cvd)
        self._cvd_poprzednie[s] = cvd
        return wynik
