"""
🪙 AdapterUSD — siła dolara (K-04 MONETA, Frankfurter FX).

Źródło: Frankfurter API (frankfurter.app) — DARMOWE, bez klucza (wymaga User-Agent).
  Indeks siły USD = geom. średnia (USD/EUR × USD/JPY × USD/GBP) — ~83% koszyka DXY.

DLACZEGO (walidacja pomiarem, 2026-07-15/16): z-score poziomu USD na oknie 120d ma IC
  -0.17 @14d, -0.27 @30d na zwroty BTC (silny USD vs ~6-mies. zakres → bearish BTC,
  BTC-DXY inverse). Zmierzone narzedzia/pomiar_usd_ic.py (MONETA) + kontrola formy:
  surowy poziom działa, EMA20-momentum (forma K-01) = SZUM → K-04 to INNA informacja
  niż K-01 (Prawo XVI). Sygnał wolny (makro-reżim, tygodnie-miesiąc).

USD_ZSCORE = (USD_teraz − mean_120d) / std_120d. Adapter pobiera ~180 dni historii FX
  i liczy bieżący z-score. OPT-IN --usd (domyślnie OFF, A/B przed włączeniem na stałe).

WSTRZYKIWANY FETCHER (Prawo XIX): testy wstrzykują mock JSON → pełny test OFFLINE.
"""

import json
import logging

from imperium.akwedukty.adaptery.baza import AdapterDanych
from imperium.legiony.neurony.makro import NeuronUSDStrength

logger = logging.getLogger("Adapter")


class AdapterUSD(AdapterDanych):
    """Most do K-04 NeuronUSDStrength. Dostarcza USD_ZSCORE (siła USD vs 120d zakres)."""
    NAZWA = "USD(Frankfurter)"
    KLUCZE = ["USD_ZSCORE"]
    _NEURONY = (NeuronUSDStrength,)
    _POWOD_USPIENIA = "Wymaga zewnętrznego API FX (Frankfurter) — opt-in --usd."

    OKNO = 120
    URL = "https://api.frankfurter.app/{od}..{do}?base=USD&symbols=EUR,JPY,GBP"

    def __init__(self, fetcher=None, timeout: int = 12):
        self._fetcher = fetcher or self._fetch_http
        self.timeout = timeout

    def _fetch_http(self) -> str:
        import urllib.request
        from datetime import datetime, timedelta, timezone
        do = datetime.now(timezone.utc)
        od = do - timedelta(days=self.OKNO + 70)   # zapas na weekendy/święta FX
        url = self.URL.format(od=od.strftime("%Y-%m-%d"), do=do.strftime("%Y-%m-%d"))
        req = urllib.request.Request(url, headers={"User-Agent": "IMV/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode()

    def pobierz(self, symbol: str = "") -> dict:
        """
        Zwraca {"USD_ZSCORE": float} (z-score siły USD vs 120d) lub {"USD_ZSCORE": None}.
        Sygnał globalny (makro) — `symbol` ignorowany.
        """
        try:
            import numpy as np
            r = json.loads(self._fetcher()).get("rates", {})
            days = sorted(r)
            if len(days) < 60:
                return {"USD_ZSCORE": None}
            base = r[days[0]]
            idx = []
            for dd in days:
                v = r[dd]
                if all(k in v and k in base and base[k] for k in ("EUR", "JPY", "GBP")):
                    idx.append(float(np.cbrt((v["EUR"] / base["EUR"]) *
                                             (v["JPY"] / base["JPY"]) *
                                             (v["GBP"] / base["GBP"]))))
            if len(idx) < 60:
                return {"USD_ZSCORE": None}
            okno = idx[-self.OKNO:] if len(idx) > self.OKNO else idx
            s = float(np.std(okno))
            if s < 1e-9:
                return {"USD_ZSCORE": None}
            return {"USD_ZSCORE": float((idx[-1] - np.mean(okno)) / s)}
        except Exception as e:
            logger.warning(f"[Adapter:USD] pobranie padło: {e}")
            return {"USD_ZSCORE": None}
