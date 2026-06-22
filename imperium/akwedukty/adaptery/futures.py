"""
🔥 AdapterFutures — most danych futures: Binance fapi PUBLICZNE → PSY-01/02/04.

Źródła (DARMOWE, BEZ KLUCZA API — publiczne endpointy rynku futures):
  • Funding Rate:   GET https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT
                    → pole "lastFundingRate" (string, np. "0.00010000")
  • Open Interest:  GET https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT
                    → pole "openInterest" (string)
  • Long/Short:     GET https://fapi.binance.com/futures/data/globalLongShortAccountRatio
                    ?symbol=BTCUSDT&period=5m&limit=1
                    → pole "longAccount" (string, 0-1 = frakcja kont LONG)

DLACZEGO BINANCE PUBLIC (decyzja zgodna z Prawem bezpieczeństwa):
  Te endpointy NIE wymagają klucza API ani podpisu — to publiczne dane rynku.
  Zero ryzyka bezpieczeństwa, idealne do obudzenia kategorii R (sentyment) bez
  konfiguracji kluczy. Gdy przejdziemy na MEXC z kluczem — klucz WYŁĄCZNIE z
  os.getenv (MEXC_API_KEY/MEXC_SECRET), nigdy w kodzie.

WSTRZYKIWANY FETCHER (Prawo XIX: kod+testy zanim coś "istnieje"):
  `pobierz()` deleguje pobranie surowych JSON-ów do `self._fetcher(url)`.
  - produkcja: domyślny `_fetch_http` (urllib, stdlib — zero nowych zależności)
  - testy: wstrzykujemy fetcher zwracający próbki JSON → pełny test OFFLINE,
           deterministyczny, bez sieci.

OPEN_INTEREST_PREV (Prawo I — bez halucynacji):
  Adapter pamięta poprzednią wartość OI per symbol (między cyklami). Przy
  pierwszym odczycie OI_PREV = OI (brak dywergencji — PSY-04 abstynuje).

PRAWO XV: budzi PSY-01/02/04 tylko gdy adapter podpięty i dostarcza dane.
  PSY-03 (Fear&Greed) ma osobny AdapterFearGreed — sentyment globalny, nie futures.
"""

import json
import logging
from typing import Dict, Any, Optional

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.psychologia import (
    NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv,
)

logger = logging.getLogger("Adapter")


class AdapterFutures(AdapterDanych):
    """
    Most do PSY-01 (Funding), PSY-02 (Long/Short), PSY-04 (Open Interest).
    Dane z publicznych endpointów Binance fapi — bez klucza API.
    """
    NAZWA = "Futures(binance-public)"
    KLUCZE = ["FUNDING_RATE", "LONG_SHORT_RATIO", "OPEN_INTEREST", "OPEN_INTEREST_PREV"]
    _NEURONY = (NeuronFundingExtreme, NeuronPanikaDetal, NeuronOIDiv)
    _POWOD_USPIENIA = "Wymaga publicznego API futures (Binance fapi / MEXC). Adapter odpięty."

    URL_FUNDING = "https://fapi.binance.com/fapi/v1/premiumIndex?symbol={s}"
    URL_OI = "https://fapi.binance.com/fapi/v1/openInterest?symbol={s}"
    URL_LS = ("https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
              "?symbol={s}&period=5m&limit=1")

    # ── Endpointy HISTORYCZNE (W-cache/backfill — pomiar PSY w backteście) ──
    # Funding: pełna historia od startu kontraktu (8h interwał), do 1000/zapytanie.
    URL_FUNDING_HIST = ("https://fapi.binance.com/fapi/v1/fundingRate"
                        "?symbol={s}&limit={limit}")
    # OI/LS history: TYLKO ostatnie ~30 dni (ograniczenie Binance), period konfig.
    URL_OI_HIST = ("https://fapi.binance.com/futures/data/openInterestHist"
                   "?symbol={s}&period={period}&limit={limit}")
    URL_LS_HIST = ("https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
                   "?symbol={s}&period={period}&limit={limit}")

    def __init__(self, fetcher=None, timeout: int = 8):
        """
        fetcher: opcjonalny callable(url:str) -> str (surowy JSON). Domyślnie HTTP.
                 W testach wstrzykujemy mock mapujący URL → próbka → test offline.
        """
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout
        self._oi_poprzednie: Dict[str, float] = {}  # pamięć OI per symbol

    def _fetch_http(self, url: str) -> str:
        """Domyślne pobranie surowego JSON (urllib, stdlib — bez nowych zależności)."""
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

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
        Zwraca {FUNDING_RATE, LONG_SHORT_RATIO, OPEN_INTEREST, OPEN_INTEREST_PREV}.
        Każdy klucz None gdy dane brak/uszkodzone (wzbogac() pominie None — neuron
        śpi/abstynuje, nie fałszuje sygnału). Symbol np. "BTCUSDT".
        """
        s = (symbol or "BTCUSDT").upper().replace("/", "")
        wynik: Dict[str, Any] = {
            "FUNDING_RATE": None, "LONG_SHORT_RATIO": None,
            "OPEN_INTEREST": None, "OPEN_INTEREST_PREV": None,
        }

        # Funding rate
        try:
            d = json.loads(self._fetcher(self.URL_FUNDING.format(s=s)))
            wynik["FUNDING_RATE"] = self._bezpieczny_float(d, "lastFundingRate")
        except Exception as e:
            logger.warning(f"[Adapter:Futures] funding {s} padł: {e}")

        # Long/Short account ratio → frakcja LONG (0-1)
        try:
            raw = json.loads(self._fetcher(self.URL_LS.format(s=s)))
            rekord = raw[0] if isinstance(raw, list) and raw else (raw if isinstance(raw, dict) else {})
            wynik["LONG_SHORT_RATIO"] = self._bezpieczny_float(rekord, "longAccount")
        except Exception as e:
            logger.warning(f"[Adapter:Futures] long/short {s} padł: {e}")

        # Open Interest + pamięć poprzedniej wartości (dla PSY-04 dywergencji)
        try:
            d = json.loads(self._fetcher(self.URL_OI.format(s=s)))
            oi = self._bezpieczny_float(d, "openInterest")
            if oi is not None:
                wynik["OPEN_INTEREST"] = oi
                # OI_PREV: poprzedni odczyt; przy pierwszym = bieżący (brak dywergencji)
                wynik["OPEN_INTEREST_PREV"] = self._oi_poprzednie.get(s, oi)
                self._oi_poprzednie[s] = oi
        except Exception as e:
            logger.warning(f"[Adapter:Futures] open interest {s} padł: {e}")

        return wynik

    # ── BACKFILL HISTORYCZNY (Prawo XVI — mierz PSY-01/02/04, nie zgaduj) ──────

    def pobierz_historie(
        self, symbol: str, limit: int = 1000, period: str = "1h"
    ) -> "list[dict]":
        """
        Pobiera historię funding (pełną) + OI/LS (ostatnie ~30 dni) z Binance public.

        Zwraca listę rekordów posortowaną rosnąco po timestamp:
          [{"timestamp": ms, "FUNDING_RATE": f, "OPEN_INTEREST": oi,
            "LONG_SHORT_RATIO": ls}, ...]
        Każde pole może być None (osobne osie czasu — funding co 8h, OI/LS wg period).
        Surowe punkty; forward-fill do osi barów robi `dolacz_sentyment_do_barow`.
        """
        s = (symbol or "BTCUSDT").upper().replace("/", "")
        rekordy: "dict[int, dict]" = {}

        # Funding (pełna historia, 8h)
        try:
            raw = json.loads(self._fetcher(self.URL_FUNDING_HIST.format(s=s, limit=limit)))
            for r in (raw if isinstance(raw, list) else []):
                ts = int(r.get("fundingTime", 0))
                if ts:
                    rekordy.setdefault(ts, {})["FUNDING_RATE"] = self._bezpieczny_float(r, "fundingRate")
        except Exception as e:
            logger.warning(f"[Adapter:Futures] funding-hist {s} padł: {e}")

        # Open Interest history (~30 dni)
        try:
            raw = json.loads(self._fetcher(self.URL_OI_HIST.format(s=s, period=period, limit=limit)))
            for r in (raw if isinstance(raw, list) else []):
                ts = int(r.get("timestamp", 0))
                if ts:
                    rekordy.setdefault(ts, {})["OPEN_INTEREST"] = self._bezpieczny_float(r, "sumOpenInterest")
        except Exception as e:
            logger.warning(f"[Adapter:Futures] oi-hist {s} padł: {e}")

        # Long/Short ratio history (~30 dni)
        try:
            raw = json.loads(self._fetcher(self.URL_LS_HIST.format(s=s, period=period, limit=limit)))
            for r in (raw if isinstance(raw, list) else []):
                ts = int(r.get("timestamp", 0))
                if ts:
                    rekordy.setdefault(ts, {})["LONG_SHORT_RATIO"] = self._bezpieczny_float(r, "longAccount")
        except Exception as e:
            logger.warning(f"[Adapter:Futures] ls-hist {s} padł: {e}")

        return [
            {"timestamp": ts,
             "FUNDING_RATE": v.get("FUNDING_RATE"),
             "OPEN_INTEREST": v.get("OPEN_INTEREST"),
             "LONG_SHORT_RATIO": v.get("LONG_SHORT_RATIO")}
            for ts, v in sorted(rekordy.items())
        ]
