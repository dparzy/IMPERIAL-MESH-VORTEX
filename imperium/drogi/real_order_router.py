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

    # ── Synchronizacja przy starcie (W-333) ────────────────────────────────────

    def synchronizuj_pozycje(self, interwal: str = "4h") -> int:
        """
        Odczytuje otwarte pozycje z MEXC i odtwarza je w trackingu (Prawo XV).

        KRYTYCZNE dla bezpieczeństwa kapitału: po restarcie procesu engine startuje
        pusty, a na giełdzie mogą wisieć realne pozycje BEZ kontroli SL/TP roju.
        Ta metoda przywraca kontrolę — czyta fetch_positions(), odtwarza
        OtwartaPozycja dla każdej wiszącej pozycji, by przetwarzanie barów
        (SL/TP/likwidacja/timeout) znów nad nią czuwało.

        W dry_run nie ma realnych pozycji do odtworzenia (zlecenia nie szły) —
        zwraca 0. Zwraca liczbę odtworzonych pozycji.
        """
        import time
        import uuid

        if self._dry_run:
            logger.info("[SYNC] dry_run — brak realnych pozycji do odtworzenia.")
            return 0

        try:
            pozycje = self._exchange.fetch_positions()
        except Exception as exc:
            logger.error("[SYNC] fetch_positions padł: %s — engine startuje pusty.", exc)
            return 0

        odtworzone = 0
        for p in pozycje or []:
            try:
                contracts = float(p.get("contracts") or 0.0)
                if contracts <= 0:
                    continue  # zamknięta/pusta
                symbol = p.get("symbol") or p.get("info", {}).get("symbol", "?")
                kierunek = "LONG" if str(p.get("side", "")).lower() == "long" else "SHORT"
                cena_wej = float(p.get("entryPrice") or p.get("info", {}).get("entryPrice") or 0.0)
                dzwignia = max(1, int(float(p.get("leverage") or 1)))  # nigdy 0 (dzielenie)
                notional = float(p.get("notional") or (contracts * cena_wej))
                margin = notional / dzwignia if dzwignia > 0 else notional

                if cena_wej <= 0 or notional <= 0:
                    logger.warning("[SYNC] Pomijam %s — brak ceny/notional.", symbol)
                    continue

                # Likwidacja: z giełdy jeśli jest, inaczej szacunek 100% margin
                likw = p.get("liquidationPrice")
                if likw:
                    likwidacja = float(likw)
                elif kierunek == "LONG":
                    likwidacja = cena_wej * (1 - 1.0 / dzwignia)
                else:
                    likwidacja = cena_wej * (1 + 1.0 / dzwignia)

                # Brak SL/TP z giełdy → sentinele które NIGDY nie odpalą fałszywie
                # na pierwszym barze (granica: take_profit=0.0 dawałby high>=0 → TP_HIT
                # natychmiast dla LONG; stop_loss=0.0 → high>=0 → SL_HIT dla SHORT).
                # Pozycję chroni LIKWIDACJA + TIMEOUT; rój dołoży realny SL przy decyzji.
                if kierunek == "LONG":
                    sl_sync, tp_sync = 0.0, float("inf")       # low<=0 i high>=inf nigdy
                else:
                    sl_sync, tp_sync = float("inf"), 0.0       # high>=inf i low<=0 nigdy

                poz = OtwartaPozycja(
                    pozycja_id=f"SYNC-{uuid.uuid4().hex[:8].upper()}",
                    symbol=symbol,
                    interwal=interwal,
                    kierunek=kierunek,
                    cena_wejscia=cena_wej,
                    stop_loss=sl_sync,
                    take_profit=tp_sync,
                    cena_likwidacji=likwidacja,
                    rozmiar_usdt=notional,
                    dzwignia=dzwignia,
                    kapital_zablokowany=margin,
                    prowizja_wejscia=0.0,
                    timestamp_wejscia=int(time.time() * 1000),
                )
                self.otwarte[poz.pozycja_id] = poz
                self._pozycje_real[poz.pozycja_id] = {
                    "symbol": symbol,
                    "qty": round(contracts, 6),
                    "entry_order_id": "SYNC",
                }
                odtworzone += 1
                logger.warning(
                    "[SYNC] Odtworzono %s %s qty=%.6f wejście=%.6f dźwignia=%dx "
                    "(SL/TP=0 — rój dołoży przy kolejnej decyzji)",
                    symbol, kierunek, contracts, cena_wej, dzwignia,
                )
            except Exception as exc:
                logger.error("[SYNC] Błąd odtwarzania pozycji %s: %s", p, exc)

        logger.info("[SYNC] Odtworzono %d pozycji z MEXC.", odtworzone)
        return odtworzone

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
