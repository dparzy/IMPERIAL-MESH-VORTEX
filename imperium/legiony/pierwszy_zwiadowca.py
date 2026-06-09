"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   PaperBot RSI+EMA — Pierwszy Zwiadowca (pełny cykl) v1.1                    ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                            ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-STRAT-001                                                  |
| Nazwa oryginalna    | PaperBot RSI+EMA (oryginał Kingdom Pixel)                   |
| Nazwa w Imperium    | Pierwszy Zwiadowca                                           |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/STRAT-001_PaperBot_RSI_EMA.py        |
| Kategoria           | STRAT / Strategia demonstracyjna (paper trading)            |
| Wpływ na Imperium   | PEŁNY CYKL Fazy 0 w jednym uruchomieniu: dane → decyzja →    |
|                     | ryzyko → wykres → raport. Spina 5 modułów.                  |
| Powiązane moduły    | N-DATA-001, N-CORE-006, N-SHIELDS-205, N-VIZ-001, N-LOG-001 |

────────────────────────── UCZCIWIE (Prawo I) ─────────────────────────
Bot NA NIBY (paper). Zero prawdziwych pieniędzy. Strategia prosta i edukacyjna —
wyniki NIE przewidują realnych zysków. Cel: zobaczyć i zrozumieć pełny cykl.

CYKL (jedno uruchomienie robi wszystko):
  1. Ładowarka (N-DATA-001) — dane z biblioteki / MEXC / syntetyczne
  2. Brama (N-CORE-006)     — liczy RSI i EMA (Prawo I)
  3. Strategia             — trend-following (cena>EMA + RSI 50–70; wyjście EMA/RSI/stop/take)
  4. AegisShield (N-SHIELDS-205) — ryzyko, circuit breaker
  5. Kartograf (N-VIZ-001) — wykres PNG
  6. Kronikarz (N-LOG-001) — raport + dziennik (dla diagnozy Jacka)

CHANGELOG:
  v1.7 (2026-05-29) — WYDAJNOSC: wskazniki liczone RAZ przez Brame (compute_series),
        O(n) zamiast O(n^2). Gotowe na 1h/1m. Wynik identyczny (regresja OK).
  v1.6 (2026-05-29) — LOCK-IN po walidacji Krok 5: "zyski rosna" (take-profit OFF)
        domyslnie. Pobil benchmark na BTC i ETH, w obu epokach, odporny na EMA 30-100.
  v1.5 (2026-05-29) — dodany max drawdown + benchmark kup-i-trzymaj.
  v1.4 (2026-05-29) — KALIBRACJA krok 3: circuit breaker z ODBICIEM. Po serii strat
        bot pauzuje N świec (cooldown_bars), resetuje tarczę i WRACA do gry, zamiast
        umierać na zawsze. (AegisShield jest czasowy/live — w backteście liczymy w świecach.)
  v1.3 (2026-05-29) — KALIBRACJA krok 2: prowizje round-trip (0,1%/stronę).
  v1.2 (2026-05-29) — KALIBRACJA krok 1: realistyczne wyjścia (STOP/TAKE na progu).
  v1.1 (2026-05-29) — INTEGRACJA: dane z Ładowarki (biblioteka), auto-wykres
        (Kartograf), auto-raport (Kronikarz). Rejestr indeksów świec i krzywej kapitału.
  v1.0 (2026-05-28) — bazowy cykl Brama + AegisShield.
═════════════════════════════════════════════════════════════════════════════════════
"""

import os
import importlib.util
import logging
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("PierwszyZwiadowca")


def _load_module(filename: str, required: bool = True):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(path):
        if required:
            raise FileNotFoundError(f"Brak wymaganego pliku '{filename}' w folderze.")
        logger.warning(f"[Bot] Brak opcjonalnego modułu '{filename}' — pomijam tę funkcję.")
        return None
    mod_name = os.path.basename(filename)[:-3].replace("-", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Wymagane / opcjonalne moduły Imperium (ścieżki względem dzielnic)
_gw = _load_module("../fundament/brama_kalkulatora.py", required=True)
CalculatorGateway = _gw.CalculatorGateway
_sh = _load_module("../pretorianie/aegis_tarcza.py", required=False)
AegisShield = _sh.AegisShield if _sh else None
_dl = _load_module("../akwedukty/kwatermistrz_danych.py", required=False)
DataLoader = _dl.DataLoader if _dl else None
_vz = _load_module("../swiatynie/kartograf.py", required=False)
plot_run = _vz.plot_run if _vz else None
_lg = _load_module("../biblioteki/kronikarz.py", required=False)
Kronikarz = _lg.Kronikarz if _lg else None
RunReport = _lg.RunReport if _lg else None


@dataclass
class Trade:
    entry_idx: int
    entry_price: float
    exit_idx: int = 0
    exit_price: float = 0.0
    pnl_pct: float = 0.0
    reason: str = ""
    win: bool = False


class PaperBot:
    def __init__(self, capital: float = 50.0, rsi_high: float = 65,
                 ema_period: int = 50, stop_pct: float = 0.03, take_pct: Optional[float] = None,
                 fee_pct: float = 0.001, cooldown_bars: int = 20, roj=None):
        # take_pct=None → "zyski rosną" (domyślne po walidacji Krok 5). Ustaw liczbę, by włączyć take-profit.
        # roj=RojSygnalow() → wejścia przez konsensus roju (z neuronem reżimu). None → klasyczne wejście.
        self.start_capital = capital
        self.balance = capital
        self.rsi_high = rsi_high
        self.ema_period = ema_period
        self.stop_pct = stop_pct
        self.take_pct = take_pct
        self.fee_pct = fee_pct
        self.cooldown_bars = cooldown_bars
        self.roj = roj
        self.gateway = CalculatorGateway()
        self.shield = AegisShield(initial_capital=capital) if AegisShield else None
        self.position: Optional[float] = None
        self.entry_idx = 0
        self.trades: List[Trade] = []
        self.equity: List[float] = [capital]
        self.ema_series: List[Optional[float]] = []
        self.cooldown_left = 0
        self.pauses = 0
        self.halted = False
        self.halted_reason: Optional[str] = None

    def run(self, prices: List[float], data_source: str = "?"):
        self.prices = prices
        self.data_source = data_source
        self.ema_series = [None] * len(prices)
        warmup = self.ema_period + 2
        # Wskaźniki liczone RAZ na całej serii przez Bramę (Prawo I) — szybko, bez lookahead.
        rsi_arr = self.gateway.compute_series("RSI", close=prices, period=14)
        ema_arr = self.gateway.compute_series("EMA", close=prices, period=self.ema_period)
        # neuron reżimu (długa EMA) — liczony tylko gdy gramy rojem; też przez Bramę (Prawo I)
        ema_long_arr = (self.gateway.compute_series("EMA", close=prices, period=self.roj.regime_period)
                        if self.roj is not None else None)
        for i in range(warmup, len(prices)):
            price = float(prices[i])
            rsi = float(rsi_arr[i]); ema = float(ema_arr[i])
            self.ema_series[i] = None if np.isnan(ema) else ema
            if np.isnan(rsi) or np.isnan(ema):
                continue
            if self.cooldown_left > 0:                      # pauza po serii strat
                self.cooldown_left -= 1
                if self.cooldown_left == 0 and self.shield:
                    self.shield.consecutive_losses = 0      # reset tarczy — wracamy do gry
                    self.shield.daily_pnl = 0.0
                    self.shield.daily_reset_time = __import__("time").time()
                continue
            if self.position is None:
                if self.roj is not None:
                    lb = self.roj.slope_lookback
                    elong = float(ema_long_arr[i])
                    elong_prev = float(ema_long_arr[i - lb]) if i >= lb else float("nan")
                    enter = self.roj.entry_ok(price, ema, rsi, elong, elong_prev)
                else:
                    enter = price > ema and 50 < rsi < self.rsi_high + 5
                if enter:
                    self.position = price
                    self.entry_idx = i
            else:
                change = (price - self.position) / self.position
                reason, exec_change = None, change
                if change <= -self.stop_pct:
                    reason, exec_change = "STOP", -self.stop_pct   # realistycznie: wyjście DOKŁADNIE na progu
                elif self.take_pct is not None and change >= self.take_pct:
                    reason, exec_change = "TAKE", self.take_pct     # take-profit tylko jeśli włączony
                elif price < ema:
                    reason = "cena<EMA"                              # główne wyjście: trend się łamie (zyski rosną)
                elif rsi < 45:
                    reason = "RSI<45"
                if reason:
                    self._close(i, exec_change, reason)
        if self.position is not None:
            last = float(prices[-1])
            self._close(len(prices) - 1, (last - self.position) / self.position, "KONIEC DANYCH")
        self._report()

    def _close(self, idx: int, change: float, reason: str):
        exit_price = self.position * (1 + change)
        net = change - 2 * self.fee_pct          # prowizja round-trip: wejście + wyjście
        pnl = self.balance * net
        self.balance += pnl
        win = net > 0
        self.trades.append(Trade(self.entry_idx, self.position, idx, exit_price, round(net * 100, 2), reason, win))
        self.equity.append(self.balance)
        emoji = "✅" if win else "❌"
        logger.info(f"  [{self.entry_idx}→{idx}] {emoji} {net:+.2%} ({reason}) | Saldo ${self.balance:.2f}")
        self.position = None
        if self.shield:
            status = self.shield.update(pnl)
            if status in ("CIRCUIT_BREAKER", "FLATTEN_ALL"):
                self.cooldown_left = self.cooldown_bars
                self.pauses += 1
                self.halted_reason = f"AegisShield {status} (pauza {self.cooldown_bars} świec)"
                logger.warning(f"[Bot] ⏸️ {status} — pauza {self.cooldown_bars} świec, potem wracam.")

    def _report(self):
        n = len(self.trades)
        wins = sum(1 for t in self.trades if t.win)
        wr = wins / n if n else 0.0
        ret = (self.balance - self.start_capital) / self.start_capital
        bh = (self.prices[-1] / self.prices[0] - 1) if self.prices else 0.0  # kup i trzymaj
        # max drawdown — najgłębszy zjazd kapitału od szczytu (na krzywej transakcji)
        peak, mdd = self.equity[0], 0.0
        for e in self.equity:
            peak = max(peak, e)
            if peak > 0:
                mdd = max(mdd, (peak - e) / peak)
        verdict = "POBITY ✅" if ret > bh else "PRZEGRANY ❌ (gorzej niż trzymanie)"
        logger.info("=" * 56)
        logger.info(f"  RAPORT: {n} transakcji | WR {wr:.0%} | ${self.start_capital:.2f}→${self.balance:.2f} ({ret:+.1%})")
        logger.info(f"  BENCHMARK kup-i-trzymaj: {bh:+.1%} | Werdykt: {verdict}")
        logger.info(f"  MAX DRAWDOWN (ryzyko): -{mdd:.1%}")
        logger.info("=" * 56)
        base = os.path.dirname(os.path.abspath(__file__))

        # 5) Wykres (Kartograf)
        if plot_run:
            trades_v = [{"entry_idx": t.entry_idx, "entry_price": t.entry_price,
                         "exit_idx": t.exit_idx, "exit_price": t.exit_price, "win": t.win} for t in self.trades]
            try:
                plot_run(self.prices, self.ema_series, trades_v, self.equity,
                         title=f"Pierwszy Zwiadowca — {self.data_source}",
                         out_path=os.path.join(base, "wykres_biegu.png"))
            except Exception as e:
                logger.warning(f"[Bot] Wykres pominięty: {e}")

        # 6) Raport (Kronikarz)
        if Kronikarz and RunReport:
            rep = RunReport(
                bot="PaperBot", version="v1.7",
                params={"rsi_high": self.rsi_high, "ema_period": self.ema_period,
                        "stop_pct": self.stop_pct, "take_pct": self.take_pct, "fee_pct": self.fee_pct},
                data_source=self.data_source, start_capital=self.start_capital,
                end_capital=self.balance, win_rate=wr, benchmark_pct=bh, max_drawdown=mdd,
                halted_reason=self.halted_reason,
                trades=[{"entry": t.entry_price, "exit": t.exit_price, "pnl_pct": t.pnl_pct, "reason": t.reason}
                        for t in self.trades],
            )
            Kronikarz(out_dir=base).zapisz(rep)


def _get_prices():
    """Pozyskuje ceny: biblioteka → synthetic (offline). Na PC z netem: realne z MEXC."""
    base = os.path.dirname(os.path.abspath(__file__))
    if DataLoader:
        libdir = os.path.join(base, "dane")
        libs = DataLoader.library_list(libdir)
        if "BTC_1h.csv" in libs:
            df = DataLoader.library_load("BTC_1h", libdir)
            return DataLoader.closes(df), "BTC_1h (biblioteka)"
        df = DataLoader.synthetic(n=400)
        return DataLoader.closes(df), "SYNTETYCZNE (offline)"
    # awaryjnie bez Ładowarki
    import numpy as np
    rng = np.random.default_rng(2026)
    p = [50000.0]
    for _ in range(400):
        p.append(p[-1] * (1 + rng.normal(0.0003, 0.018)))
    return p, "SYNTETYCZNE (wewn.)"


def main():
    logger.info("=== Pierwszy Zwiadowca v1.1 — PEŁNY CYKL (paper) ===")
    prices, source = _get_prices()
    logger.info(f"Dane: {source} ({len(prices)} świec)")
    bot = PaperBot(capital=50.0)
    bot.run(prices, data_source=source)
    print("\n✅ Pierwszy Zwiadowca v1.1 — cykl zakończony. Sprawdź wykres_biegu.png i raport.")


if __name__ == "__main__":
    main()
