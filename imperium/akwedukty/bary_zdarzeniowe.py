"""
W-356 | Bary Zdarzeniowe: Tick / Volume / Dollar / Imbalance Bars (AFML Ch. 2).

DLA NOWICJUSZA: Standardowe świece 1h/4h próbkują po CZASIE — powstają niezależnie
od tego, czy rynek był aktywny czy uśpiony. To jak fotografowanie co godzinę bez
względu na to, czy coś się dzieje.

López de Prado: próbkuj po ZDARZENIACH — jeden bar = stała ilość informacji:
  • Tick bars    — co N transakcji (każdy trade = 1 tick)
  • Volume bars  — co N jednostek wolumenu (np. co 100 BTC)
  • Dollar bars  — co N USD obrotu (np. co 10M USDT) ← ZALECANE: homoskedastyczne

Zalety vs bary czasowe (udowodnione empirycznie przez LdP):
  1. Homoskedastyczność — zmienność stała między barami (lepsza dla ML)
  2. Zbliżone do IID — lepsze własności statystyczne
  3. Synchronizacja z informacją — więcej barów w aktywnych sesjach,
     mniej podczas ciszy (bary czasowe marnują próbki na szum)
  4. Normalność zwrotów — grubsze ogony przez bary czasowe vs dollar bars

Dollar bars są najlepsze: neutralizują volatility clustering i uwzględniają
price impact (1 BTC za $100 ≠ 1 BTC za $60000 pod względem informacji).

Imbalance bars (zaawansowane):
  Próbkują gdy skumulowana nierównowaga Buy/Sell przekroczy oczekiwanie E[T].
  Adaptacyjne: więcej barów przy asymetrii przepływu (insider trading!).
  Wymagają danych tick-by-tick z side (buy/sell).

Użycie:
    from imperium.akwedukty.bary_zdarzeniowe import dollar_bars, volume_bars, tick_bars

    # Z danych OHLCV (aproksymacja — brak prawdziwych ticków)
    bary_d = dollar_bars(ohlcv_lista, prog_dolarow=10_000_000)

    # Z surowych ticków (websocket feed)
    bary_d = dollar_bars_z_tickow(ticki, prog_dolarow=10_000_000)

Źródło: López de Prado, AFML (2018), Ch. 2, §2.3-2.5.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger("BaryZdarzeniowe")


# ─── Struktury ────────────────────────────────────────────────────────────────

@dataclass
class Tick:
    """Pojedyncza transakcja z websocket trade feed."""
    timestamp: int     # Unix ms
    cena: float
    wolumen: float
    strona: int = 0    # +1 = buy (taker), -1 = sell, 0 = nieznana


@dataclass
class BarZdarzeniowy:
    """
    Bar zdarzeniowy (tick/volume/dollar) — format zgodny z resztą Imperium
    (ten sam dict-format co OHLCV loader, plus dodatkowe pola).
    """
    timestamp: int       # Unix ms — czas PIERWSZEGO ticku w barze
    timestamp_end: int   # Unix ms — czas OSTATNIEGO ticku
    open: float
    high: float
    low: float
    close: float
    volume: float        # suma wolumenu
    dollar_volume: float # suma cena * wolumen (USD)
    n_ticks: int         # liczba transakcji w barze
    # Nierównowaga (do imbalance bars)
    buy_volume: float = 0.0
    sell_volume: float = 0.0
    # Typ baru
    typ: str = "dollar"  # "tick" / "volume" / "dollar" / "imbalance"

    def jako_dict(self) -> Dict[str, Any]:
        """Format zgodny z bary_per z pętli live."""
        return {
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "dollar_volume": self.dollar_volume,
            "n_ticks": self.n_ticks,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "typ_bara": self.typ,
        }


# ─── Budowniczy barów (stream) ────────────────────────────────────────────────

class _BudowniczyBara:
    """Akumuluje ticki i emituje gotowy bar gdy osiągnięty prog."""

    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._ts_start: int = 0
        self._ts_end: int = 0
        self._open = self._high = self._low = self._close = 0.0
        self._vol = self._dv = 0.0
        self._n = 0
        self._buy_vol = self._sell_vol = 0.0
        self._pusty = True

    def dodaj(self, tick: Tick) -> None:
        if self._pusty:
            self._ts_start = tick.timestamp
            self._open = self._high = self._low = tick.cena
            self._pusty = False
        self._ts_end = tick.timestamp
        self._high = max(self._high, tick.cena)
        self._low = min(self._low, tick.cena)
        self._close = tick.cena
        self._vol += tick.wolumen
        self._dv += tick.cena * tick.wolumen
        self._n += 1
        if tick.strona == 1:
            self._buy_vol += tick.wolumen
        elif tick.strona == -1:
            self._sell_vol += tick.wolumen

    def emit(self, typ: str = "dollar") -> BarZdarzeniowy:
        bar = BarZdarzeniowy(
            timestamp=self._ts_start,
            timestamp_end=self._ts_end,
            open=self._open, high=self._high,
            low=self._low, close=self._close,
            volume=round(self._vol, 8),
            dollar_volume=round(self._dv, 2),
            n_ticks=self._n,
            buy_volume=round(self._buy_vol, 8),
            sell_volume=round(self._sell_vol, 8),
            typ=typ,
        )
        self._reset()
        return bar

    @property
    def pusty(self) -> bool:
        return self._pusty


# ─── Bary z ticków ────────────────────────────────────────────────────────────

def tick_bars_z_tickow(ticki: List[Tick], n: int = 1000) -> List[BarZdarzeniowy]:
    """
    Tick bars: jeden bar = co N transakcji.
    n=1000 → jeden bar na każde 1000 trade'ów.
    """
    bud = _BudowniczyBara()
    wynik: List[BarZdarzeniowy] = []
    for tick in ticki:
        bud.dodaj(tick)
        if bud._n >= n:
            wynik.append(bud.emit("tick"))
    return wynik


def volume_bars_z_tickow(ticki: List[Tick], prog: float = 100.0) -> List[BarZdarzeniowy]:
    """
    Volume bars: jeden bar = co `prog` jednostek wolumenu.
    prog=100 → jeden bar na każde 100 BTC.
    """
    bud = _BudowniczyBara()
    wynik: List[BarZdarzeniowy] = []
    for tick in ticki:
        bud.dodaj(tick)
        if bud._vol >= prog:
            wynik.append(bud.emit("volume"))
    return wynik


def dollar_bars_z_tickow(ticki: List[Tick], prog: float = 10_000_000.0) -> List[BarZdarzeniowy]:
    """
    Dollar bars: jeden bar = co `prog` USD obrotu (cena × wolumen).
    prog=10M → jeden bar na każde 10 mln USDT. Zalecane przez LdP.
    """
    bud = _BudowniczyBara()
    wynik: List[BarZdarzeniowy] = []
    for tick in ticki:
        bud.dodaj(tick)
        if bud._dv >= prog:
            wynik.append(bud.emit("dollar"))
    return wynik


# ─── Aproksymacja z OHLCV (gdy brak danych tickowych) ────────────────────────

def _ohlcv_do_tickow(bar: Dict, n_syntetycznych: int = 4) -> List[Tick]:
    """
    Aproksymuje ticki z baru OHLCV (syntetyczne ticki).
    Używa ścieżki: open → high/low (zmienna) → close.
    Tylko do wstępnego testowania — LdP zaleca prawdziwe dane tickowe.
    """
    ts = int(bar.get("timestamp", 0))
    o = float(bar.get("open", 0))
    h = float(bar.get("high", 0))
    l = float(bar.get("low", 0))
    c = float(bar.get("close", 0))
    v = float(bar.get("volume", 0))
    v_per = v / n_syntetycznych if n_syntetycznych > 0 else v
    dt = 1000  # 1 sekunda między syntetycznymi tickami

    # Ścieżka OHLC: open, high (jeśli bullish), low, close / lub odwrotnie
    if c >= o:
        ceny = [o, l, h, c]   # bullish: open → low → high → close
    else:
        ceny = [o, h, l, c]   # bearish: open → high → low → close

    return [
        Tick(timestamp=ts + i * dt, cena=p, wolumen=v_per)
        for i, p in enumerate(ceny[:n_syntetycznych])
    ]


def dollar_bars(
    bary_ohlcv: List[Dict],
    prog_dolarow: float = 10_000_000.0,
) -> List[BarZdarzeniowy]:
    """
    Dollar bars z listy barów OHLCV (aproksymacja).
    Przydatne gdy brak prawdziwych danych tickowych.

    Ostrzeżenie (Prawo I): to aproksymacja — prawdziwe dollar bars wymagają
    danych trade-by-trade z websocket (Tick.cena, Tick.wolumen per transakcja).
    """
    ticki: List[Tick] = []
    for bar in bary_ohlcv:
        ticki.extend(_ohlcv_do_tickow(bar))
    result = dollar_bars_z_tickow(ticki, prog_dolarow)
    logger.debug(
        "[BaryZdarzeniowe] Dollar bars: %d OHLCV → %d dollar bars (prog=%.0f USD)",
        len(bary_ohlcv), len(result), prog_dolarow,
    )
    return result


def volume_bars(
    bary_ohlcv: List[Dict],
    prog_wolumenu: float = 100.0,
) -> List[BarZdarzeniowy]:
    """Volume bars z OHLCV (aproksymacja). Patrz ostrzeżenie w dollar_bars()."""
    ticki: List[Tick] = []
    for bar in bary_ohlcv:
        ticki.extend(_ohlcv_do_tickow(bar))
    result = volume_bars_z_tickow(ticki, prog_wolumenu)
    logger.debug(
        "[BaryZdarzeniowe] Volume bars: %d OHLCV → %d volume bars (prog=%.2f)",
        len(bary_ohlcv), len(result), prog_wolumenu,
    )
    return result


def tick_bars(
    bary_ohlcv: List[Dict],
    prog_tickow: int = 1000,
) -> List[BarZdarzeniowy]:
    """Tick bars z OHLCV (aproksymacja, 4 syntetyczne ticki per bar OHLCV)."""
    ticki: List[Tick] = []
    for bar in bary_ohlcv:
        ticki.extend(_ohlcv_do_tickow(bar))
    result = tick_bars_z_tickow(ticki, prog_tickow)
    return result


# ─── Imbalance Bars ───────────────────────────────────────────────────────────

def imbalance_bars_z_tickow(
    ticki: List[Tick],
    oczekiwana_dl_inicjalna: int = 200,
    alpha: float = 0.1,
) -> List[BarZdarzeniowy]:
    """
    Volume Imbalance Bars (AFML §2.5): próbkowanie gdy |Σ buy_vol − Σ sell_vol| ≥ E[T]·|E[b]|.

    E[T] = oczekiwana długość baru (ewoluuje z alpha jako EWMA).
    E[b] = oczekiwana wartość buy/sell imbalance per tick (EWMA).

    Bardziej aktywne bary gdy silna asymetria Buy/Sell → detekcja informatywnych flow'ów.
    Wymaga danych z polem strona (+1/-1); bez tego wolumen całkowity użyty.
    """
    if not ticki:
        return []

    # Inicjalizacja EWMA
    e_t = float(oczekiwana_dl_inicjalna)
    # Oczekiwana "imbalance" na tick (buy - sell per unit volume)
    e_b_plus = 0.5   # procent buy volume
    e_b_minus = 0.5  # procent sell volume

    bud = _BudowniczyBara()
    wynik: List[BarZdarzeniowy] = []
    theta = 0.0        # skumulowana nierównowaga

    def _b(tick: Tick) -> float:
        """Znak tiku: +vol jeśli buy, -vol jeśli sell, 0 jeśli nieznane."""
        if tick.strona == 1:
            return tick.wolumen
        if tick.strona == -1:
            return -tick.wolumen
        # Brak strony — tick rule (porównaj z poprzednią ceną)
        return 0.0

    prog = max(1.0, e_t * abs(e_b_plus - e_b_minus))
    bary_w_bar: List[float] = []   # długości poprzednich barów (do EWMA e_t)
    imb_w_bar: List[float] = []    # |theta| z poprzednich barów (do EWMA e_b)

    for tick in ticki:
        bud.dodaj(tick)
        b_t = _b(tick)
        theta += b_t
        bary_w_bar.append(b_t)

        if abs(theta) >= prog:
            bar = bud.emit("imbalance")
            wynik.append(bar)

            n_cur = len(bary_w_bar)
            imb_cur = abs(theta)
            imb_w_bar.append(imb_cur)
            bary_w_bar.clear()

            # EWMA aktualizacja E[T] i E[b]
            e_t = (1 - alpha) * e_t + alpha * n_cur
            e_imb = (1 - alpha) * (e_b_plus - e_b_minus) + alpha * (theta / max(1, n_cur))
            e_b_plus = max(0.0, min(1.0, 0.5 + e_imb / 2))
            e_b_minus = 1.0 - e_b_plus

            theta = 0.0
            prog = max(1.0, e_t * abs(e_b_plus - e_b_minus))

    logger.debug(
        "[BaryZdarzeniowe] Imbalance bars: %d ticków → %d barów", len(ticki), len(wynik)
    )
    return wynik


# ─── Statystyki barów ─────────────────────────────────────────────────────────

def statystyki_barow(bary: List[BarZdarzeniowy]) -> Dict[str, float]:
    """
    Podstawowe statystyki jakości barów (do porównania z barami czasowymi).
    LdP: dobre bary → niski CV wolumenu, skośność bliżej 0.
    """
    if not bary:
        return {}
    import math
    dvs = [b.dollar_volume for b in bary]
    ns = [b.n_ticks for b in bary]
    mean_dv = sum(dvs) / len(dvs)
    mean_n = sum(ns) / len(ns)
    # Coefficient of Variation (CV) = std/mean — im niższy tym lepiej (homoskedastyczność)
    var_dv = sum((x - mean_dv) ** 2 for x in dvs) / max(1, len(dvs))
    var_n = sum((x - mean_n) ** 2 for x in ns) / max(1, len(ns))
    cv_dv = math.sqrt(var_dv) / (mean_dv + 1e-9)
    cv_n = math.sqrt(var_n) / (mean_n + 1e-9)
    return {
        "n_barow": len(bary),
        "mean_dollar_volume": round(mean_dv, 0),
        "cv_dollar_volume": round(cv_dv, 4),
        "mean_n_ticks": round(mean_n, 1),
        "cv_n_ticks": round(cv_n, 4),
    }
