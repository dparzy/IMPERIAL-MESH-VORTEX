"""
🏛️ AdapterStablecoin — podaż stablecoinów (K-03, DefiLlama).

Źródło: DefiLlama `stablecoins.llama.fi/stablecoincharts/all` — DARMOWE, bez klucza API.
  Total circulating USD-pegged stablecoin supply (USDT+USDC+...). Proxy „suchego prochu"
  = kapitał gotowy wejść w krypto.

DLACZEGO (walidacja pomiarem, 2026-07-15): 7-dniowa % zmiana podaży ma IC +0.05..+0.10
  @7-30d na zwroty BTC (DODATNI — druk stablecoinów = napływ = bullish flow). Zmierzone
  narzedzia/pomiar_stablecoin_ic.py (AERARIUM) PRZED wpięciem (Prawo I, ZASADA WPIĘCIA).

Sygnał = DELTA (7d % zmiana), nie poziom (poziom trenduje → niestacjonarny). Adapter
pobiera ostatnie ~14 dni i liczy zmianę supply_teraz/supply_7d_temu − 1 → STABLE_FLOW.

OPT-IN: adapter wpinany TYLKO za flagą --stablecoin (domyślnie OFF). Bez niego K-03
abstynuje (Prawo XV). Walidacja WSTĘPNA — wpięcie na stałe po A/B (Prawo XVIII).

WSTRZYKIWANY FETCHER (Prawo XIX): testy wstrzykują mock JSON → pełny test OFFLINE.
"""

import json
import logging
from datetime import datetime, timezone

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.makro import NeuronStablecoinFlow

logger = logging.getLogger("Adapter")


class AdapterStablecoin(AdapterDanych):
    """Most do K-03 NeuronStablecoinFlow. Dostarcza STABLE_FLOW (7d % zmiana podaży)."""
    NAZWA = "Stablecoin(DefiLlama)"
    KLUCZE = ["STABLE_FLOW"]
    _NEURONY = (NeuronStablecoinFlow,)
    _POWOD_USPIENIA = "Wymaga zewnętrznego API podaży stablecoinów (DefiLlama) — opt-in --stablecoin."

    URL = "https://stablecoins.llama.fi/stablecoincharts/all"
    DELTA_DNI = 7

    def __init__(self, fetcher=None, timeout: int = 12):
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout

    def _fetch_http(self) -> str:
        import urllib.request
        req = urllib.request.Request(self.URL, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

    @staticmethod
    def _dzien(ts) -> str:
        ts = int(ts)
        return datetime.fromtimestamp((ts / 1000) if ts > 1e12 else ts,
                                      tz=timezone.utc).strftime("%Y-%m-%d")

    def pobierz(self, symbol: str = "") -> dict:
        """
        Zwraca {"STABLE_FLOW": float} (7d % zmiana total supply) lub {"STABLE_FLOW": None}.
        Sentyment globalny (cały rynek) — `symbol` ignorowany.
        """
        try:
            raw = json.loads(self._fetcher())
            supply = {}
            for r in (raw if isinstance(raw, list) else []):
                v = (r.get("totalCirculatingUSD") or {}).get("peggedUSD")
                if v:
                    supply[self._dzien(r["date"])] = float(v)
            if len(supply) < self.DELTA_DNI + 1:
                return {"STABLE_FLOW": None}
            dni = sorted(supply)
            teraz = supply[dni[-1]]
            wstecz = supply[dni[max(0, len(dni) - 1 - self.DELTA_DNI)]]
            if wstecz <= 0:
                return {"STABLE_FLOW": None}
            return {"STABLE_FLOW": float(teraz / wstecz - 1.0)}
        except Exception as e:
            logger.warning(f"[Adapter:Stablecoin] pobranie padło: {e}")
            return {"STABLE_FLOW": None}
