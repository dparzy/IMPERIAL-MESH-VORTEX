"""
W-354 — TradingView Webhook Receiver (Prawo XV — potencjał na żywo).

Odbiera alerty HTTP POST /webhook/tv z TradingView Pine Script.
Zero zewnętrznych zależności (stdlib tylko).

PINE SCRIPT TEMPLATE (wklej do TradingView → Add Alert → Webhook URL):
────────────────────────────────────────────────────────────────────────
//@version=5
strategy("Imperium Webhook", overlay=true)

// Wyślij bar przy każdym zamknięciu świecy:
alertcondition(barstate.isconfirmed, title="Bar zamknięty")

// W Alert Message:
// {
//   "symbol": "{{ticker}}",
//   "interwal": "{{interval}}",
//   "akcja": "NEUTRAL",
//   "cena": {{close}},
//   "czas": "{{time}}",
//   "open": {{open}}, "high": {{high}}, "low": {{low}},
//   "close": {{close}}, "volume": {{volume}},
//   "sekret": "TWOJ_SEKRET"
// }
────────────────────────────────────────────────────────────────────────

Bezpieczeństwo:
  - sekret: opcjonalne hasło w JSON payloadzie (Prawo bezpieczeństwa — klucze
    tylko w env zmiennych). Ustaw WEBHOOK_TV_SEKRET=... w środowisku.
  - Domyślnie bind 127.0.0.1 — panel nie wychodzi na świat.
  - Gdy wystawiasz na publiczne IP (np. przez ngrok/Cloudflare Tunnel):
    OBOWIĄZKOWO ustaw WEBHOOK_TV_SEKRET w środowisku.

Użycie w pętli live:
    serwer = SerwerDashboard(port=8777)
    odbiornik = OdbiornikWebhook()
    serwer.podepnij_webhook(odbiornik)
    serwer.start()

    # Pętla live co bar:
    for alert in odbiornik.pobierz_wszystkie():
        # alert.jako_bar() → dict z open/high/low/close/volume
        print(alert.symbol, alert.akcja, alert.cena)
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("WebhookTV")


# ─── Alert ────────────────────────────────────────────────────────────────────

@dataclass
class AlertTV:
    """Sparsowany alert z TradingView (jedno zdarzenie = jeden bar lub sygnał)."""
    symbol: str
    interwal: str   # "1","5","15","60","240","D","W" — period TradingView
    akcja: str      # "LONG" / "SHORT" / "NEUTRAL"
    cena: float
    czas: str       # ISO-8601 lub Unix ms (string z TV)
    otwarcie: float = 0.0
    szczyt: float = 0.0
    dolina: float = 0.0
    zamkniecie: float = 0.0
    wolumen: float = 0.0
    meta: Dict[str, Any] = field(default_factory=dict)

    def jako_bar(self) -> Dict[str, float]:
        """Konwertuje alert na format baru dla Budowniczego wskaźników."""
        c = self.zamkniecie or self.cena
        return {
            "open":   self.otwarcie or c,
            "high":   self.szczyt or c,
            "low":    self.dolina or c,
            "close":  c,
            "volume": self.wolumen,
        }

    def jako_swiec_json(self) -> Dict[str, Any]:
        """Format wykresu świecowego (Lightweight Charts)."""
        c = self.zamkniecie or self.cena
        return {
            "time": self.czas,
            "open":  self.otwarcie or c,
            "high":  self.szczyt or c,
            "low":   self.dolina or c,
            "close": c,
        }


# ─── Parser ───────────────────────────────────────────────────────────────────

_ALIASY_AKCJI: Dict[str, str] = {
    "buy": "LONG",   "long": "LONG",   "1": "LONG",
    "sell": "SHORT", "short": "SHORT", "-1": "SHORT",
    "neutral": "NEUTRAL", "0": "NEUTRAL", "hold": "NEUTRAL",
    "close": "NEUTRAL",
}


def parsuj_alert_tv(body: bytes, sekret: Optional[str] = None) -> Optional[AlertTV]:
    """
    Parsuje ciało HTTP POST z TradingView.
    Akceptuje JSON (TV wysyła Content-Type: text/plain z JSON w body).
    sekret: gdy podany — body musi zawierać pole 'sekret' o tej wartości.
    Zwraca AlertTV lub None przy błędzie.
    """
    try:
        dane: Dict[str, Any] = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("[WebhookTV] Nieprawidłowy JSON: %s (%.100s)", exc, body[:100])
        return None
    if not isinstance(dane, dict):
        logger.warning("[WebhookTV] JSON nie jest obiektem (type=%s)", type(dane).__name__)
        return None

    if sekret and dane.get("sekret") != sekret:
        logger.warning("[WebhookTV] Nieprawidłowy sekret — alert odrzucony.")
        return None

    symbol = str(dane.get("symbol", dane.get("ticker", "???"))).upper().strip()
    interwal = str(dane.get("interwal", dane.get("interval", dane.get("timeframe", "?"))))
    akcja_raw = str(dane.get("akcja", dane.get("action", dane.get("signal", "NEUTRAL")))).lower().strip()
    akcja = _ALIASY_AKCJI.get(akcja_raw, akcja_raw.upper())

    def _f(*klucze: str) -> float:
        for k in klucze:
            v = dane.get(k)
            if v is not None:
                try:
                    return float(v)
                except (TypeError, ValueError):
                    pass
        return 0.0

    cena = _f("cena", "price", "close")
    zamkniecie = _f("zamkniecie", "close", "cena", "price")

    return AlertTV(
        symbol=symbol,
        interwal=interwal,
        akcja=akcja,
        cena=cena,
        czas=str(dane.get("czas", dane.get("time", dane.get("timestamp", "")))),
        otwarcie=_f("otwarcie", "open"),
        szczyt=_f("szczyt", "high"),
        dolina=_f("dolina", "low"),
        zamkniecie=zamkniecie,
        wolumen=_f("wolumen", "volume", "vol"),
        meta={
            k: v for k, v in dane.items()
            if k not in {
                "symbol", "ticker", "interwal", "interval", "timeframe",
                "akcja", "action", "signal", "cena", "price",
                "czas", "time", "timestamp",
                "open", "high", "low", "close", "volume", "vol",
                "otwarcie", "szczyt", "dolina", "zamkniecie", "wolumen",
                "sekret",
            }
        },
    )


# ─── Bufor alertów ────────────────────────────────────────────────────────────

_MAX_HISTORIA_NA_SYMBOL = 500   # świece na wykresie
_MAX_KOLEJKA = 5_000


class OdbiornikWebhook:
    """
    Thread-safe bufor alertów TradingView.
    DashboardHandler (wątek HTTP) → dodaj_raw(); pętla live → pobierz_wszystkie().

    Bezpieczeństwo: sekret pobierany z WEBHOOK_TV_SEKRET (env) — nigdy hardcode.
    """

    def __init__(self, rozmiar: int = _MAX_KOLEJKA, sekret: Optional[str] = None):
        if sekret is None:
            sekret = os.getenv("WEBHOOK_TV_SEKRET") or None
        self._sekret = sekret
        self._q: queue.Queue[AlertTV] = queue.Queue(maxsize=rozmiar)
        self._lock = threading.Lock()
        # historia per symbol (symbol → lista AlertTV), ostatnie _MAX_HISTORIA_NA_SYMBOL
        self._historia: Dict[str, List[AlertTV]] = {}
        # liczniki
        self._lacznie: int = 0
        self._bledy: int = 0

    # ── Dodawanie (wątek HTTP) ────────────────────────────────────────────────

    def dodaj_raw(self, body: bytes) -> bool:
        """Parsuje surowe body POST i dodaje. Zwraca True jeśli OK."""
        alert = parsuj_alert_tv(body, self._sekret)
        if alert is None:
            with self._lock:
                self._bledy += 1
            return False
        return self.dodaj(alert)

    def dodaj(self, alert: AlertTV) -> bool:
        """Dodaje sparsowany alert. Zwraca True jeśli OK."""
        try:
            self._q.put_nowait(alert)
        except queue.Full:
            logger.warning("[WebhookTV] Kolejka pełna — alert pominięty (%s)", alert.symbol)
            return False
        with self._lock:
            hist = self._historia.setdefault(alert.symbol, [])
            hist.append(alert)
            if len(hist) > _MAX_HISTORIA_NA_SYMBOL:
                self._historia[alert.symbol] = hist[-_MAX_HISTORIA_NA_SYMBOL:]
            self._lacznie += 1
        logger.debug("[WebhookTV] Alert: %s %s @%.4f", alert.symbol, alert.akcja, alert.cena)
        return True

    # ── Odczyt (pętla live) ───────────────────────────────────────────────────

    def pobierz_wszystkie(self) -> List[AlertTV]:
        """Non-blocking: zwraca i usuwa wszystkie oczekujące alerty z kolejki."""
        alerty: List[AlertTV] = []
        while True:
            try:
                alerty.append(self._q.get_nowait())
            except queue.Empty:
                break
        return alerty

    # ── Historia (do wykresu) ─────────────────────────────────────────────────

    def historia(self, symbol: str) -> List[AlertTV]:
        """Kopia historii alertów dla symbolu (do renderowania wykresu)."""
        with self._lock:
            return list(self._historia.get(symbol.upper(), []))

    def swiecze_json(self, symbol: str) -> List[Dict[str, Any]]:
        """Lista świec w formacie Lightweight Charts (time/open/high/low/close)."""
        return [a.jako_swiec_json() for a in self.historia(symbol)]

    def symbole(self) -> List[str]:
        """Lista wszystkich symboli z odebranych alertów (posortowana)."""
        with self._lock:
            return sorted(self._historia.keys())

    @property
    def lacznie(self) -> int:
        return self._lacznie

    @property
    def bledy(self) -> int:
        return self._bledy

    def statystyki(self) -> Dict[str, Any]:
        """Podsumowanie do /stan.json (dashboard)."""
        return {
            "lacznie_alertow": self._lacznie,
            "bledy_parsowania": self._bledy,
            "symbole": self.symbole(),
            "w_kolejce": self._q.qsize(),
        }
