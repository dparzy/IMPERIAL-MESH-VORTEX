"""
🔱 IMV-ADO | EXP-12 Atmabhan — mikrostruktura L2 orderbook (AP-Mode)

Adoptowane z: AP-Mode / Atmabhan Pandit v3.0 (Shrikant Bhosale)
Seal: IMV-ADO v1.0 — adoptowane z KRYTYCZNYM zastrzeżeniem

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 OSTRZEŻENIE (Prawo XV — prawda dla Cezara):
  Oryginalny backtest AP-Mode raportował +106,692% ROI, Sharpe 22.04, 93.2% WR.
  TE LICZBY SĄ NIEWIARYGODNE — Sharpe > 3 jest już podejrzany, 22 nie istnieje
  w realnym tradingu. To sygnatura lookahead/overfittingu/nierealistycznych
  fillów. NIE WOLNO ufać tym wynikom. Adoptujemy KONCEPT mikrostruktury, nie
  obietnicę zysków. Każdy sygnał EXP-12 wymaga walidacji na realnym feedzie.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DLACZEGO DOSTEPNY=False:
  EXP-12 czyta L2 orderbook (głębokość 20, bid/ask wolumeny, kolejki). OHLCV
  tego NIE zawiera. Bez feedu orderbook zwiadowca dostawałby martwy NEUTRAL —
  to byłoby kłamstwo (złamanie Prawa XV). Dlatego jest jawnie wyciszony do czasu
  podpięcia feedu L2 (Binance Depth20@100ms / Pi42 / MEXC depth).

  Po podpięciu feedu: ustaw DOSTEPNY=True i wołaj analizuj_orderbook(snapshot).

KONCEPT (mikrostruktura termodynamiczna — komplementarny, unikalny w Imperium):
  Żaden inny moduł nie czyta orderbooka. EXP-12 wnosi:
  1. L2 imbalance (5 i 10 poziomów): (bid_vol - ask_vol)/(bid_vol + ask_vol)
  2. Delta imbalance acceleration: druga różnica imbalance (przyspieszenie presji)
  3. Queue cancellations: spadek wolumenu na best bid/ask (wycofanie/spoofing)
  4. Conviction score: ważona suma sygnałów → próg 7.5/10 do wejścia

Struktura snapshotu orderbook (gdy feed podpięty):
  {
    "bids": [[cena, wolumen], ...],  # malejąco po cenie, [0] = best bid
    "asks": [[cena, wolumen], ...],  # rosnąco po cenie, [0] = best ask
    "timestamp": int,
  }
"""

from typing import List, Dict, Any, Optional

from .baza import ZwiadowcaElitarny, RaportZwiadowcy, TypDanych


_POWOD_L2 = (
    "Wymaga feedu L2 orderbook (Binance Depth20@100ms / Pi42 / MEXC depth). "
    "OHLCV nie zawiera danych o głębokości rynku. Aktywuje się po podpięciu "
    "feedu orderbook — wtedy ustaw DOSTEPNY=True i wołaj analizuj_orderbook()."
)


def _imbalance(bids: List, asks: List, poziomy: int) -> float:
    """
    L2 imbalance dla N poziomów: (bid_vol - ask_vol) / (bid_vol + ask_vol).
    Zakres [-1, 1]. >0 = presja kupna, <0 = presja sprzedaży.
    """
    bid_vol = sum(b[1] for b in bids[:poziomy]) if bids else 0.0
    ask_vol = sum(a[1] for a in asks[:poziomy]) if asks else 0.0
    razem = bid_vol + ask_vol
    if razem <= 0:
        return 0.0
    return (bid_vol - ask_vol) / razem


def _delta_acceleration(historia_imb: List[float]) -> float:
    """
    Przyspieszenie imbalance = druga różnica skończona.
    accel = (imb[t] - imb[t-1]) - (imb[t-1] - imb[t-2])
          = imb[t] - 2*imb[t-1] + imb[t-2]
    """
    if len(historia_imb) < 3:
        return 0.0
    return historia_imb[-1] - 2 * historia_imb[-2] + historia_imb[-3]


def _queue_cancellation(best_teraz: float, best_poprzednio: float) -> float:
    """
    Wykrywa wycofanie z kolejki best bid/ask.
    Zwraca względny spadek wolumenu (0 = brak, >0 = wycofanie/spoofing).
    """
    if best_poprzednio <= 0:
        return 0.0
    spadek = (best_poprzednio - best_teraz) / best_poprzednio
    return max(0.0, spadek)


def _conviction_score(imb5: float, imb10: float, accel: float,
                      cancel_bid: float, cancel_ask: float) -> tuple:
    """
    Conviction score [0, 10] + kierunek.
    Łączy imbalance (oba poziomy), przyspieszenie i cancellations.
    Zwraca (score, kierunek).
    """
    # Komponent kierunkowy: imbalance ważony (5-poziomowy ma większą wagę — bliżej spreadu)
    kierunkowy = 0.6 * imb5 + 0.4 * imb10
    # Przyspieszenie wzmacnia, gdy zgodne z kierunkiem
    if (kierunkowy > 0 and accel > 0) or (kierunkowy < 0 and accel < 0):
        kierunkowy += 0.5 * accel
    # Cancellations: wycofanie z ask = byczo (sprzedający uciekają), z bid = niedźwiedzio
    kierunkowy += 0.3 * (cancel_ask - cancel_bid)

    # Skala na [0, 10] — imbalance w [-1,1], więc ×10 daje pełny zakres.
    # Silny imbalance (|0.75|) → 7.5 = próg konwikcji. accel/cancel mogą dobić wyżej.
    score = min(10.0, abs(kierunkowy) * 10.0)
    kierunek = "LONG" if kierunkowy > 0 else ("SHORT" if kierunkowy < 0 else "NEUTRAL")
    return score, kierunek


class ZwiadowcaAtmabhan(ZwiadowcaElitarny):
    """
    🔱 IMV-ADO v1.0 | EXP-12 Atmabhan — mikrostruktura L2 orderbook.
    WYCISZONY (DOSTEPNY=False) do czasu podpięcia feedu orderbook.
    """
    KLUCZ = "EXP-12"
    WSKAZNIK = "L2_MICROSTRUCTURE"
    KATEGORIA = "V"  # wolumen/przepływ (najbliższa kategoria mikrostruktury)
    WAGA = 9         # silny sygnał gdy dostępny — najbliżej egzekucji
    TYP_DANYCH = TypDanych.ORDER_BOOK
    WYMAGA_BAROW = 1

    DOSTEPNY = False
    POWOD_NIEDOSTEPNOSCI = _POWOD_L2

    CONVICTION_PROG = 7.5  # próg z config.json AP-Mode

    def __init__(self) -> None:
        super().__init__()
        self._historia_imb5: List[float] = []
        self._prev_best_bid_vol: float = 0.0
        self._prev_best_ask_vol: float = 0.0

    def analizuj(self, bary: List[Dict[str, Any]]) -> RaportZwiadowcy:
        """
        Z OHLCV nie da się policzyć mikrostruktury — zwraca brak danych.
        Prawdziwa analiza idzie przez analizuj_orderbook(snapshot).
        """
        return self._brak_danych(
            "EXP-12 wymaga snapshotu L2 orderbook (DOSTEPNY=False). " + _POWOD_L2
        )

    def analizuj_orderbook(self, snapshot: Dict[str, Any]) -> RaportZwiadowcy:
        """
        Główna analiza mikrostruktury z snapshotu L2 orderbook.
        Wołać po podpięciu feedu (i ustawieniu DOSTEPNY=True).

        snapshot: {"bids": [[cena, vol], ...], "asks": [[cena, vol], ...], "timestamp": int}
        """
        bids = snapshot.get("bids") or []
        asks = snapshot.get("asks") or []
        if not bids or not asks:
            return self._brak_danych("Pusty orderbook (brak bidów lub asków)")

        imb5 = _imbalance(bids, asks, 5)
        imb10 = _imbalance(bids, asks, 10)

        self._historia_imb5.append(imb5)
        if len(self._historia_imb5) > 100:
            self._historia_imb5.pop(0)
        accel = _delta_acceleration(self._historia_imb5)

        best_bid_vol = bids[0][1]
        best_ask_vol = asks[0][1]
        cancel_bid = _queue_cancellation(best_bid_vol, self._prev_best_bid_vol)
        cancel_ask = _queue_cancellation(best_ask_vol, self._prev_best_ask_vol)
        self._prev_best_bid_vol = best_bid_vol
        self._prev_best_ask_vol = best_ask_vol

        score, kierunek = _conviction_score(imb5, imb10, accel, cancel_bid, cancel_ask)

        powody = [
            f"imbalance_5={imb5:+.3f}",
            f"imbalance_10={imb10:+.3f}",
            f"delta_accel={accel:+.4f}",
            f"cancel_bid={cancel_bid:.3f} cancel_ask={cancel_ask:.3f}",
            f"conviction={score:.2f}/10 (prog={self.CONVICTION_PROG})",
        ]
        diag = {
            "main_value": imb5, "imbalance_10": imb10,
            "delta_accel": accel, "conviction": score,
        }

        # Próg konwikcji — poniżej brak wejścia (jak w AP-Mode)
        if score < self.CONVICTION_PROG:
            return self._buduj_raport(
                kierunek="NEUTRAL", pewnosc=0.0,
                powody=[f"Conviction {score:.2f} < {self.CONVICTION_PROG} — brak przewagi mikrostruktury"] + powody,
                diagnostics=diag, n_barow=1,
            )

        # Pewność skalowana konwikcją powyżej progu
        pewnosc = min(0.90, 0.60 + (score - self.CONVICTION_PROG) / 10.0)
        return self._buduj_raport(
            kierunek=kierunek, pewnosc=pewnosc,
            powody=[f"MIKROSTRUKTURA L2: conviction {score:.2f} → {kierunek}"] + powody,
            diagnostics=diag, n_barow=1,
        )
