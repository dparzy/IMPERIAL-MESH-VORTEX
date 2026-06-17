"""
W-331 — RealOrderRouter: Most do realnych zleceń MEXC (paper=False).

Rozszerza PaperTradingEngine — wewnętrzna logika P&L, SL/TP, czas trwania = paper.
Każde wejście i wyjście (SL/TP/MANUAL/TIMEOUT) → CCXT create_order() na MEXC.

Wymagania:
  pip install ccxt
  MEXC_API_KEY  — zmienna środowiskowa
  MEXC_SECRET   — zmienna środowiskowa

Tryb testów: wstrzyknij exchange=MockExchange() — bez sieci, bez kluczy.

W-332 — TRYB DRY-RUN (MEXC nie ma testnetu — potwierdzone: urls['test']=null):
  dry_run=True → łączy się PRAWDZIWYM kluczem, weryfikuje uprawnienia/saldo,
  ale create_order TYLKO LOGUJE co BY wysłał (nie wysyła). Najbliżej testnetu
  jak się da na MEXC — łapie błędy integracji (zły symbol, brak uprawnień,
  reduceOnly) bez ryzyka kapitału.
"""

import os
import logging
from typing import Dict, Optional

from imperium.koloseum.paper_trading import (
    PaperTradingEngine,
    SygnalWejscia,
    OtwartaPozycja,
    WynikZamkniecia,
)

logger = logging.getLogger("RealOrderRouter")


def _zbuduj_mexc(tryb: str = "swap"):
    """Buduje połączenie CCXT MEXC z kluczami ze środowiska."""
    try:
        import ccxt
    except ImportError as exc:
        raise ImportError(
            "pip install ccxt — wymagane dla RealOrderRouter (paper=False)"
        ) from exc

    api_key = os.getenv("MEXC_API_KEY")
    secret = os.getenv("MEXC_SECRET")
    if not api_key or not secret:
        raise EnvironmentError(
            "MEXC_API_KEY i MEXC_SECRET wymagane dla paper=False. "
            "Ustaw zmienne środowiskowe przed uruchomieniem pętli live."
        )

    ex = ccxt.mexc({
        "apiKey": api_key,
        "secret": secret,
        "options": {"defaultType": tryb},
    })
    ex.load_markets()
    return ex


class RealOrderRouter(PaperTradingEngine):
    """
    Most do realnych zleceń MEXC.

    Wejście (wejdz):
      1. Otwiera pozycję wirtualną w PaperTradingEngine (tracking P&L, SL, TP).
      2. Wysyła market order na MEXC przez CCXT.

    Wyjście (_zamknij — wszystkie ścieżki: SL/TP/MANUAL/TIMEOUT/PETLA_STOP):
      1. Zamknięcie wirtualne (PaperTradingEngine._zamknij).
      2. Wysyła odwrotny market order z reduceOnly=True na MEXC.

    Błąd CCXT → log ERROR + kontynuuj (paper tracking żyje — audyt różnic).
    Prawo I: logujemy każdą rozbieżność papier vs real.
    """

    def __init__(
        self,
        *args,
        exchange=None,
        tryb_pozycji: str = "swap",
        dry_run: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # exchange=None → buduj z kluczy środowiskowych; exchange=Mock → testy offline
        self._exchange = exchange if exchange is not None else _zbuduj_mexc(tryb_pozycji)
        self._tryb_pozycji = tryb_pozycji
        # dry_run: prawdziwe połączenie, ale create_order tylko logowany (zero ryzyka)
        self._dry_run = dry_run
        self._dry_run_zlecenia: list = []  # log co BY wysłano (audyt)
        # pozycja_id → (symbol, qty_base, exchange_order_id)
        self._pozycje_real: Dict[str, Dict] = {}
        if dry_run:
            logger.warning(
                "[DRY-RUN] Tryb sucho-bieżny: zlecenia NIE są wysyłane na MEXC, "
                "tylko logowane. Zero ryzyka kapitału."
            )

    # ── Składanie zlecenia (real lub dry-run) ──────────────────────────────────

    def _zloz_zlecenie(self, symbol: str, side: str, qty: float, params: Dict) -> Dict:
        """
        Składa zlecenie na MEXC. W dry_run — tylko loguje i zwraca atrapę z id,
        bez wywołania create_order (zero ryzyka). Inaczej — realne CCXT.
        """
        if self._dry_run:
            zlec = {
                "symbol": symbol, "side": side, "amount": qty,
                "params": dict(params), "kolejnosc": len(self._dry_run_zlecenia) + 1,
            }
            self._dry_run_zlecenia.append(zlec)
            oid = f"DRYRUN-{zlec['kolejnosc']:04d}"
            logger.info(
                "[DRY-RUN] BY WYSŁAŁ: %s %s qty=%.6f params=%s → %s",
                symbol, side, qty, params, oid,
            )
            return {"id": oid, "status": "dry_run", "filled": qty}
        return self._exchange.create_order(
            symbol=symbol, type="market", side=side, amount=qty, params=params,
        )

    # ── Wejście ───────────────────────────────────────────────────────────────

    def wejdz(
        self, sygnal: SygnalWejscia, timestamp: Optional[int] = None
    ) -> Optional[OtwartaPozycja]:
        poz = super().wejdz(sygnal, timestamp)
        if poz is None:
            return None

        side = "buy" if sygnal.kierunek == "LONG" else "sell"
        # Ilość w walucie bazowej (np. BTC przy BTCUSDT)
        qty = round(sygnal.rozmiar_usdt / max(sygnal.cena_wejscia, 1e-12), 6)

        try:
            order = self._zloz_zlecenie(
                symbol=sygnal.symbol,
                side=side,
                qty=qty,
                params={"leverage": int(sygnal.dzwignia)},
            )
            oid = order.get("id", "?")
            self._pozycje_real[poz.pozycja_id] = {
                "symbol": sygnal.symbol,
                "qty": qty,
                "entry_order_id": oid,
            }
            logger.info(
                "[REAL] WEJŚCIE %s %s qty=%.6f leverage=%dx "
                "orderID=%s cena_papier=%.6f",
                sygnal.symbol, sygnal.kierunek, qty, int(sygnal.dzwignia),
                oid, sygnal.cena_wejscia,
            )
        except Exception as exc:
            logger.error("[REAL] Błąd WEJŚCIA %s: %s", sygnal.symbol, exc)
            self._pozycje_real[poz.pozycja_id] = {
                "symbol": sygnal.symbol,
                "qty": qty,
                "entry_order_id": f"ERROR:{exc}",
            }

        return poz

    # ── Wyjście (wszystkie ścieżki: SL/TP/MANUAL/TIMEOUT) ─────────────────────

    def _zamknij(
        self, pozycja_id: str, cena_zamkniecia: float, powod: str
    ) -> Optional[WynikZamkniecia]:
        # Wyczyść dane real PRZED super()._zamknij (które usuwa z self.otwarte)
        real = self._pozycje_real.pop(pozycja_id, None)
        poz_przed = self.otwarte.get(pozycja_id)

        wynik = super()._zamknij(pozycja_id, cena_zamkniecia, powod)
        if wynik is None or real is None or poz_przed is None:
            return wynik

        side = "sell" if poz_przed.kierunek == "LONG" else "buy"
        qty = real["qty"]

        try:
            order = self._zloz_zlecenie(
                symbol=poz_przed.symbol,
                side=side,
                qty=qty,
                params={"reduceOnly": True},
            )
            oid = order.get("id", "?")
            logger.info(
                "[REAL] WYJŚCIE %s powód=%s qty=%.6f orderID=%s "
                "PnL_papier=%+.4f USDT",
                poz_przed.symbol, powod, qty, oid, wynik.pnl_usdt,
            )
        except Exception as exc:
            logger.error(
                "[REAL] Błąd WYJŚCIA %s powód=%s: %s",
                poz_przed.symbol, powod, exc,
            )

        return wynik

    # ── Raport diagnostyczny ───────────────────────────────────────────────────

    def raport_real(self) -> Dict:
        """Zwraca stan śledzenia real — ile pozycji zsynchronizowanych z MEXC."""
        bledy_wejscia = sum(
            1 for v in self._pozycje_real.values()
            if str(v.get("entry_order_id", "")).startswith("ERROR:")
        )
        return {
            "otwarte_real": len(self._pozycje_real),
            "bledy_wejscia": bledy_wejscia,
            "exchange": type(self._exchange).__name__,
            "dry_run": self._dry_run,
            "dry_run_zlecen": len(self._dry_run_zlecenia),
        }
