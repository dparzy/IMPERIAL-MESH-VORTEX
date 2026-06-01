"""
🏛️ IMV-ORI | Scheduler — cykliczne uruchamianie pętli Imperium.
Co N minut pobiera dane → sygnały → agregacja → decyzja → log.

Tryby:
  LIVE     — ciągła pętla z opóźnieniem (do użytku po podłączeniu MEXC)
  BACKTEST — uruchom na liście historycznych barów (BarData[])
  ONCE     — jednorazowe uruchomienie (debug)

Bezpieczniki:
  - Bezpiecznik AOA: jeśli przepalony → pętla działa ale nie otwiera pozycji
  - Max błędów z rzędu: 5 → pauza 60s (nie zatrzymuje systemu)
  - Graceful shutdown: Ctrl+C → zamknij otwarte pozycje po cenie rynkowej
"""

import time
import signal
import logging
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Dict, Any

from imperium.biblioteki.pamiec_absolutna import ImperiumLog, PamiecAbsolutna, TypLogu
from imperium.pretorianie.kalkulator_lewara import BezpiecznikKapitalu

logger = logging.getLogger("Scheduler")


# ─── Konfiguracja ─────────────────────────────────────────────────────────────

class TrybSchedulera(str, Enum):
    LIVE = "LIVE"
    BACKTEST = "BACKTEST"
    ONCE = "ONCE"


@dataclass
class KonfiguracjaSchedulera:
    interwal_s: int = 60             # Co ile sekund odpytywać (LIVE)
    max_bledow_z_rzędu: int = 5      # Po ilu błędach → pauza PAUZA_S
    pauza_po_bledach_s: int = 60     # Pauza po max błędach
    log_kazdy_cykl: bool = True      # Loguj każdą iterację
    sesja_id: str = ""
    symbole: List[str] = field(default_factory=lambda: ["BTCUSDT"])
    interwal_rynkowy: str = "1H"     # Interwał danych (1m, 5m, 15m, 1H, 4H)


@dataclass
class StatystykiSchedulera:
    cykli_total: int = 0
    cykli_ok: int = 0
    cykli_blad: int = 0
    sygnaly_wygenerowane: int = 0
    pozycje_otwarte: int = 0
    pozycje_zamkniete: int = 0
    czas_start: float = 0.0

    @property
    def uptime_s(self) -> float:
        return time.time() - self.czas_start if self.czas_start > 0 else 0.0


# ─── Callback typy ────────────────────────────────────────────────────────────

# Callback pobierania danych: (symbol, interwal) → dict z danymi OHLCV
TFetchData = Callable[[str, str], Optional[Dict[str, Any]]]

# Callback sygnałów: (dane) → {"kierunek": "LONG"/"SHORT"/"NEUTRAL", "pewnosc": float}
TGenerateSygnal = Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]

# Callback wykonania: (sygnal) → bool (czy otwarto pozycję)
TExecute = Callable[[Dict[str, Any]], bool]


# ─── Główna klasa ─────────────────────────────────────────────────────────────

class Scheduler:
    """
    🏛️ IMV-ORI | Scheduler — pętla operacyjna Imperium.

    Użycie (LIVE):
        scheduler = Scheduler(config, fetch_fn, sygnal_fn, execute_fn)
        scheduler.uruchom()  # blokuje; Ctrl+C = graceful shutdown

    Użycie (BACKTEST):
        for wynik in scheduler.backtest(lista_barow):
            print(wynik)

    Użycie (ONCE):
        wynik = scheduler.jednorazowo()
    """

    def __init__(
        self,
        config: KonfiguracjaSchedulera,
        fetch_fn: Optional[TFetchData] = None,
        sygnal_fn: Optional[TGenerateSygnal] = None,
        execute_fn: Optional[TExecute] = None,
        bezpiecznik: Optional[BezpiecznikKapitalu] = None,
        pamiec: Optional[PamiecAbsolutna] = None,
    ) -> None:
        self.config = config
        self.fetch_fn = fetch_fn or _mock_fetch
        self.sygnal_fn = sygnal_fn or _mock_sygnal
        self.execute_fn = execute_fn or _mock_execute
        self.bezpiecznik = bezpiecznik
        self.pamiec = pamiec
        self.stats = StatystykiSchedulera()
        self._running = False
        self._bledy_z_rzędu = 0

    # ── Tryb LIVE ─────────────────────────────────────────────────────────────

    def uruchom(self) -> None:
        """Startuje pętlę LIVE. Blokuje do Ctrl+C lub wywołania zatrzymaj()."""
        self._running = True
        self.stats.czas_start = time.time()
        signal.signal(signal.SIGINT, self._graceful_shutdown)
        signal.signal(signal.SIGTERM, self._graceful_shutdown)

        logger.info(f"Scheduler START | sesja={self.config.sesja_id} | interwał={self.config.interwal_s}s")
        print(f"\n⚔️  SCHEDULER IMPERIUM URUCHOMIONY")
        print(f"   Sesja:    {self.config.sesja_id}")
        print(f"   Symbole:  {', '.join(self.config.symbole)}")
        print(f"   Interwał: co {self.config.interwal_s}s | Ctrl+C = zamknij gracefully\n")

        while self._running:
            self._wykonaj_cykl()
            if self._running:
                time.sleep(self.config.interwal_s)

        logger.info(f"Scheduler STOP | cykli={self.stats.cykli_total}")

    def zatrzymaj(self) -> None:
        self._running = False

    # ── Tryb BACKTEST ─────────────────────────────────────────────────────────

    def backtest(self, lista_danych: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Uruchamia sygnal_fn na każdym elemencie listy_danych.
        Zwraca listę wyników (jeden dict na bar).
        lista_danych: [{"symbol": "BTCUSDT", "close": 65000, ...}, ...]
        """
        self.stats.czas_start = time.time()
        wyniki = []
        for i, dane in enumerate(lista_danych):
            try:
                sygnal = self.sygnal_fn(dane)
                wykonano = False
                if sygnal and sygnal.get("kierunek") != "NEUTRAL":
                    if self._bezpiecznik_ok():
                        wykonano = self.execute_fn(sygnal)
                        if wykonano:
                            self.stats.pozycje_otwarte += 1

                wyniki.append({
                    "bar_idx": i,
                    "symbol": dane.get("symbol", ""),
                    "sygnal": sygnal,
                    "wykonano": wykonano,
                })
                self.stats.cykli_ok += 1
            except Exception as e:
                wyniki.append({"bar_idx": i, "error": str(e)})
                self.stats.cykli_blad += 1
            self.stats.cykli_total += 1
        return wyniki

    # ── Tryb ONCE ─────────────────────────────────────────────────────────────

    def jednorazowo(self) -> Dict[str, Any]:
        """Jeden cykl — przydatny do debugowania."""
        self.stats.czas_start = time.time()
        return self._wykonaj_cykl()

    # ── Wewnętrzne ─────────────────────────────────────────────────────────────

    def _wykonaj_cykl(self) -> Dict[str, Any]:
        self.stats.cykli_total += 1
        wynik: Dict[str, Any] = {"cykl": self.stats.cykli_total, "symbole": {}}

        try:
            if self.config.log_kazdy_cykl:
                logger.debug(f"Cykl #{self.stats.cykli_total} START")

            for symbol in self.config.symbole:
                dane = self.fetch_fn(symbol, self.config.interwal_rynkowy)
                if not dane:
                    wynik["symbole"][symbol] = {"status": "NO_DATA"}
                    continue

                sygnal = self.sygnal_fn(dane)
                if not sygnal:
                    wynik["symbole"][symbol] = {"status": "NO_SIGNAL"}
                    continue

                self.stats.sygnaly_wygenerowane += 1
                wykonano = False

                if sygnal.get("kierunek") not in ("LONG", "SHORT"):
                    wynik["symbole"][symbol] = {"status": "NEUTRAL", "sygnal": sygnal}
                elif not self._bezpiecznik_ok():
                    wynik["symbole"][symbol] = {"status": "BEZPIECZNIK_AOA", "sygnal": sygnal}
                else:
                    wykonano = self.execute_fn(sygnal)
                    if wykonano:
                        self.stats.pozycje_otwarte += 1
                    wynik["symbole"][symbol] = {"status": "EXECUTED" if wykonano else "SKIPPED", "sygnal": sygnal}

                if self.pamiec:
                    self._log_cykl(symbol, dane, sygnal, wykonano)

            self.stats.cykli_ok += 1
            self._bledy_z_rzędu = 0
            wynik["ok"] = True

        except Exception as e:
            self.stats.cykli_blad += 1
            self._bledy_z_rzędu += 1
            wynik["ok"] = False
            wynik["error"] = str(e)
            logger.error(f"Błąd cyklu #{self.stats.cykli_total}: {e}\n{traceback.format_exc()}")

            if self._bledy_z_rzędu >= self.config.max_bledow_z_rzędu:
                logger.warning(f"Pauza {self.config.pauza_po_bledach_s}s po {self._bledy_z_rzędu} błędach z rzędu")
                time.sleep(self.config.pauza_po_bledach_s)
                self._bledy_z_rzędu = 0

        return wynik

    def _bezpiecznik_ok(self) -> bool:
        if self.bezpiecznik and self.bezpiecznik.przepalony:
            logger.warning("Bezpiecznik AOA przepalony — blokada nowych pozycji")
            return False
        return True

    def _graceful_shutdown(self, signum, frame) -> None:
        print("\n\n⚠️  Ctrl+C — Scheduler zatrzymuje się gracefully...")
        logger.info("SIGINT/SIGTERM odebrany — graceful shutdown")
        self._running = False

    def _log_cykl(self, symbol: str, dane: Dict, sygnal: Optional[Dict], wykonano: bool) -> None:
        if not self.pamiec:
            return
        log = ImperiumLog(
            log_typ=TypLogu.ANALIZA,
            sesja_id=self.config.sesja_id,
            symbol=symbol,
            interwal=self.config.interwal_rynkowy,
            cena_close=float(dane.get("close", 0)),
            rezim=str(dane.get("rezim", "NORMAL")),
            legatus_kierunek=sygnal.get("kierunek", "") if sygnal else "",
            legatus_pewnosc=float(sygnal.get("pewnosc", 0)) if sygnal else 0.0,
        )
        self.pamiec.zapisz(log)

    def drukuj_status(self) -> None:
        s = self.stats
        print(f"\n📊 Scheduler Status | Uptime: {s.uptime_s:.0f}s")
        print(f"   Cykle: {s.cykli_total} (ok={s.cykli_ok}, błędy={s.cykli_blad})")
        print(f"   Sygnały: {s.sygnaly_wygenerowane} | Pozycje: +{s.pozycje_otwarte} otwartych")


# ─── Mock callbacki (do testów i demo) ────────────────────────────────────────

def _mock_fetch(symbol: str, interwal: str) -> Dict[str, Any]:
    """Mock fetch — zwraca dane losowe dla testów."""
    import random
    base = {"BTCUSDT": 65000.0, "ETHUSDT": 3500.0}.get(symbol, 100.0)
    close = base * (1 + random.uniform(-0.02, 0.02))
    return {
        "symbol": symbol, "interwal": interwal,
        "close": round(close, 2), "open": base,
        "high": round(close * 1.01, 2), "low": round(close * 0.99, 2),
        "volume": random.randint(100, 10000),
        "rezim": "TREND_STRONG",
    }


def _mock_sygnal(dane: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Mock sygnal — zawsze NEUTRAL (bezpieczny default)."""
    return {"kierunek": "NEUTRAL", "pewnosc": 0.0, "symbol": dane.get("symbol")}


def _mock_execute(sygnal: Dict[str, Any]) -> bool:
    return False


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")

    config = KonfiguracjaSchedulera(
        interwal_s=2,
        sesja_id="DEMO-SCHEDULER",
        symbole=["BTCUSDT", "ETHUSDT"],
        interwal_rynkowy="1H",
        log_kazdy_cykl=True,
    )

    scheduler = Scheduler(config)

    # Backtest na 5 fikcyjnych barach
    print("=== TRYB BACKTEST (5 barów) ===")
    dane_mock = [
        {"symbol": "BTCUSDT", "close": 65000 + i * 100, "rezim": "TREND_STRONG"}
        for i in range(5)
    ]
    wyniki = scheduler.backtest(dane_mock)
    for w in wyniki:
        print(f"  Bar {w['bar_idx']}: {w.get('sygnal', {}).get('kierunek', '?')} | ok={w.get('error') is None}")
    scheduler.drukuj_status()

    # ONCE
    print("\n=== TRYB ONCE ===")
    wynik = scheduler.jednorazowo()
    print(f"  Cykl wynik: {wynik}")
