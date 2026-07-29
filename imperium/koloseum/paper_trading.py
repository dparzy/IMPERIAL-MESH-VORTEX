"""
🏛️ IMV-ORI | Paper Trading Engine — symulator bez realnych pieniędzy.
Wykonuje wirtualne transakcje na podstawie sygnałów Legatusa.
Loguje każdy trade do Pamięci Absolutnej, dostarcza dane dla Igrzysk.

Tryby zamknięcia pozycji:
  SL_HIT    — cena dotknęła stop-loss
  TRAIL_HIT — cena dotknęła trailing stop (W-351, blokada zysku po ruchu)
  TP_HIT    — cena dotknęła take-profit
  LIQUIDATION — cena dotknęła poziom likwidacji
  TIMEOUT   — pozycja otwarta zbyt długo (max_bars)
  MANUAL    — zamknięcie ręczne (np. Bezpiecznik AOA)
  REVERSAL  — Legatus zmienił kierunek
"""

import uuid
import time
from dataclasses import dataclass
from typing import List, Optional, Dict
from pathlib import Path

from imperium.biblioteki.pamiec_absolutna import ImperiumLog, PamiecAbsolutna, TypLogu


# ─── Stałe ───────────────────────────────────────────────────────────────────

PROWIZJA_TAKER_PCT = 0.0005   # 0.05% taker fee (MEXC Futures standard)
SLIPPAGE_PCT = 0.0003         # 0.03% poślizg (konserwatywny)
MAX_BARS_OTWARCIA = 48        # Maks. liczba świec bez TP/SL → TIMEOUT

# Trailing stop (W-351, diagnoza 2026-06-19: zyskowne pozycje oddawały szczyt
# zysku do bara TIMEOUT — brak mechanizmu blokady zysku). MFE było liczone, ale
# nieużywane do wyjścia → utrata potencjału (Prawo XV). Trailing uzbraja się
# dopiero po znaczącym ruchu korzystnym i oddaje tylko ułamek szczytu.
TRAILING_AKTYWACJA_PCT = 0.04   # uzbrój trailing gdy ruch korzystny na cenie ≥ 4%
TRAILING_GIVEBACK_FRAC = 0.35   # po uzbrojeniu oddaj max 35% szczytu (blokuje 65%)


# ─── Struktury danych ─────────────────────────────────────────────────────────

@dataclass
class BarData:
    """Jedna świeca OHLCV."""
    timestamp: int   # Unix ms
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str = ""
    interwal: str = ""


@dataclass
class SygnalWejscia:
    """Sygnał wejścia z Legatusa / ręczny."""
    symbol: str
    interwal: str
    kierunek: str        # "LONG" / "SHORT"
    pewnosc: float       # 0.0–1.0
    cena_wejscia: float
    stop_loss: float
    take_profit: float
    dzwignia: int = 1
    rozmiar_usdt: float = 100.0
    rezim: str = "NORMAL"
    sesja_id: str = ""
    powody: str = ""


@dataclass
class OtwartaPozycja:
    """Aktywna pozycja w paper trading."""
    pozycja_id: str
    symbol: str
    interwal: str
    kierunek: str
    cena_wejscia: float
    stop_loss: float
    take_profit: float
    cena_likwidacji: float
    rozmiar_usdt: float
    dzwignia: int
    kapital_zablokowany: float  # margin w USDT
    prowizja_wejscia: float
    timestamp_wejscia: int
    sesja_id: str = ""
    bar_count: int = 0          # ile świec minęło od wejścia
    mae_pct: float = 0.0        # Maximum Adverse Excursion
    mfe_pct: float = 0.0        # Maximum Favorable Excursion
    rezim: str = "NORMAL"
    sygnaly_json: str = ""
    # Trailing stop (W-351) — szczyt korzystnej ceny + dynamiczny stop blokujący zysk
    szczyt_cena: float = 0.0       # najlepsza osiągnięta cena (high LONG / low SHORT)
    trailing_stop: float = 0.0     # poziom trailing (0.0 = nieuzbrojony)
    trailing_aktywny: bool = False


@dataclass
class WynikZamkniecia:
    """Wynik zamkniętej pozycji."""
    pozycja_id: str
    symbol: str
    kierunek: str
    cena_wejscia: float
    cena_zamkniecia: float
    pnl_usdt: float
    pnl_pct: float               # % zwrotu z kapitału zablokowanego
    prowizja_usdt: float
    mae_pct: float
    mfe_pct: float
    czas_trwania_bar: int
    powod_zamkniecia: str
    kapital_przed: float
    kapital_po: float
    # W-312: znacznik wejścia (Unix ms) — umożliwia analizę czasową zamkniętych
    # trade'ów (walk-forward OOS, filtrowanie po okresie). 0 = brak danych.
    timestamp_wejscia: int = 0
    # Reżim rynku w chwili wejścia (z Pozycji) — dla arena-logu i analizy per-reżim.
    rezim: str = "NORMAL"
    # Interwał pozycji (z Pozycji). Potrzebny, bo zamknięcia spoza ścieżki bara nie mają
    # `BarData`, a bez tego pola trafiały do W1 z pustym interwałem — i to systematycznie
    # te same trade'y (ostatnie w biegu), więc analiza per interwał dostawała obciążenie
    # nielosowe (recenzja 2026-07-29).
    interwal: str = ""


@dataclass
class StatystykiSesji:
    """Zagregowane statystyki sesji paper trading."""
    sesja_id: str
    kapital_startowy: float
    kapital_koncowy: float
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl_usdt: float = 0.0
    total_prowizje: float = 0.0
    max_drawdown_pct: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0
    avg_czas_bar: float = 0.0

    def oblicz(self, wyniki: List[WynikZamkniecia]) -> None:
        if not wyniki:
            return
        self.total_trades = len(wyniki)
        wygrane = [w for w in wyniki if w.pnl_usdt > 0]
        przegrane = [w for w in wyniki if w.pnl_usdt <= 0]
        self.winning_trades = len(wygrane)
        self.losing_trades = len(przegrane)
        self.win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0.0
        self.total_pnl_usdt = sum(w.pnl_usdt for w in wyniki)
        self.total_prowizje = sum(w.prowizja_usdt for w in wyniki)
        self.kapital_koncowy = self.kapital_startowy + self.total_pnl_usdt
        gross_zyski = sum(w.pnl_usdt for w in wygrane)
        gross_straty = abs(sum(w.pnl_usdt for w in przegrane))
        self.profit_factor = gross_zyski / gross_straty if gross_straty > 0 else gross_zyski
        self.avg_win_pct = sum(w.pnl_pct for w in wygrane) / len(wygrane) if wygrane else 0.0
        self.avg_loss_pct = sum(w.pnl_pct for w in przegrane) / len(przegrane) if przegrane else 0.0
        self.best_trade_pct = max((w.pnl_pct for w in wyniki), default=0.0)
        self.worst_trade_pct = min((w.pnl_pct for w in wyniki), default=0.0)
        self.avg_czas_bar = sum(w.czas_trwania_bar for w in wyniki) / self.total_trades
        # MaxDD
        kapital = self.kapital_startowy
        szczyt = kapital
        max_dd = 0.0
        for w in wyniki:
            kapital += w.pnl_usdt
            if kapital > szczyt:
                szczyt = kapital
            dd = (szczyt - kapital) / szczyt if szczyt > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
        self.max_drawdown_pct = round(max_dd, 4)


# ─── Silnik Paper Trading ─────────────────────────────────────────────────────

class PaperTradingEngine:
    """
    🏛️ IMV-ORI | Silnik Paper Trading — pełny symulator bez realnych pieniędzy.

    Użycie:
        engine = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="SES-001")
        for bar in dane_historyczne:
            engine.przetworz_bar(bar)
            if sygnal_z_legatusa:
                engine.wejdz(sygnal)
        stats = engine.podsumowanie()
        stats.oblicz(engine.historia_zamkniec)
    """

    def __init__(
        self,
        kapital_startowy: float = 10_000.0,
        sesja_id: str = "",
        log_dir: Optional[Path] = None,
        max_otwartych: int = 3,
        max_bars_otwarcia: "int | None" = None,
        trailing: bool = False,
        zrodlo: str = "PAPER",
    ) -> None:
        self.kapital = kapital_startowy
        self.kapital_startowy = kapital_startowy
        self.sesja_id = sesja_id or f"PAPER-{uuid.uuid4().hex[:8].upper()}"
        self.max_otwartych = max_otwartych
        # Trailing stop (W-351) — domyślnie OFF (zero regresji dla istniejących sesji)
        self.trailing = trailing
        # FAZA B (W-286): TIMEOUT per interwał — 48 świec to 48 dni na 1D, ale
        # tylko 8 dni na 4H (diagnoza 2026-06-10: 75% zamknięć 4H = TIMEOUT).
        # None → stała globalna (stare zachowanie, zero regresji).
        self.max_bars_otwarcia = max_bars_otwarcia or MAX_BARS_OTWARCIA

        self.otwarte: Dict[str, OtwartaPozycja] = {}   # pozycja_id → pozycja
        self.historia_zamkniec: List[WynikZamkniecia] = []

        # POCHODZENIE WPISU W1 (2026-07-29): dotąd KAŻDY log szedł jako "PAPER", więc
        # gdyby backtest zaczął pisać do W1, jego wyniki byłyby NIEODRÓŻNIALNE od paper-live.
        # Uczenie się na własnym backteście jak na rzeczywistości to falsyfikacja przez
        # pomieszanie źródeł — etykieta musi jechać razem z danymi, nie obok nich.
        self.zrodlo = zrodlo
        self._pamiec = PamiecAbsolutna(katalog=log_dir) if log_dir else None

    @property
    def kapital_calkowity(self) -> float:
        """
        Prawdziwe equity roju = kapitał wolny + suma zablokowanych depozytów
        otwartych pozycji. W przeciwieństwie do `self.kapital` (tylko wolny),
        NIE spada sztucznie przy otwarciu pozycji (margin przenosi się z wolnego
        do zablokowanego, suma stała). Równe kapital_startowy + zrealizowany PnL.

        To jest właściwa krzywa kapitału dla Equity-Curve Circuit Breakera (W-062):
        breaker ma reagować na realne zyski/straty, nie na utylizację depozytu.
        """
        return self.kapital + sum(p.kapital_zablokowany for p in self.otwarte.values())

    # ── Wejście ────────────────────────────────────────────────────────────────

    def wejdz(self, sygnal: SygnalWejscia, timestamp: Optional[int] = None) -> Optional[OtwartaPozycja]:
        """Otwiera wirtualną pozycję. Zwraca pozycję lub None jeśli blokada."""
        if len(self.otwarte) >= self.max_otwartych:
            return None

        # Sprawdź duplikaty symbolu
        if any(p.symbol == sygnal.symbol for p in self.otwarte.values()):
            return None

        margin = sygnal.rozmiar_usdt / sygnal.dzwignia
        if margin > self.kapital:
            return None  # brak kapitału

        prowizja = sygnal.rozmiar_usdt * PROWIZJA_TAKER_PCT
        cena_wykonania = sygnal.cena_wejscia * (
            1 + SLIPPAGE_PCT if sygnal.kierunek == "LONG" else 1 - SLIPPAGE_PCT
        )

        # Poziom likwidacji (uproszczony: 100% margin przy danej dźwigni)
        if sygnal.kierunek == "LONG":
            likwidacja = cena_wykonania * (1 - 1.0 / sygnal.dzwignia)
        else:
            likwidacja = cena_wykonania * (1 + 1.0 / sygnal.dzwignia)

        pozycja = OtwartaPozycja(
            pozycja_id=f"PT-{uuid.uuid4().hex[:8].upper()}",
            symbol=sygnal.symbol,
            interwal=sygnal.interwal,
            kierunek=sygnal.kierunek,
            cena_wejscia=cena_wykonania,
            stop_loss=sygnal.stop_loss,
            take_profit=sygnal.take_profit,
            cena_likwidacji=likwidacja,
            rozmiar_usdt=sygnal.rozmiar_usdt,
            dzwignia=sygnal.dzwignia,
            kapital_zablokowany=margin,
            prowizja_wejscia=prowizja,
            timestamp_wejscia=timestamp or int(time.time() * 1000),
            sesja_id=sygnal.sesja_id or self.sesja_id,
            rezim=sygnal.rezim,
        )

        self.kapital -= (margin + prowizja)
        self.otwarte[pozycja.pozycja_id] = pozycja
        return pozycja

    # ── Przetwarzanie świecy ───────────────────────────────────────────────────

    def przetworz_bar(self, bar: BarData) -> List[WynikZamkniecia]:
        """Sprawdza wszystkie otwarte pozycje dla danej świecy. Zwraca listę zamkniętych."""
        zamkniete: List[WynikZamkniecia] = []
        do_zamkniecia: List[str] = []

        for pid, poz in self.otwarte.items():
            if poz.symbol != bar.symbol:
                continue
            poz.bar_count += 1

            # Aktualizuj MAE/MFE
            if poz.kierunek == "LONG":
                ruch_niekorzystny = (poz.cena_wejscia - bar.low) / poz.cena_wejscia
                ruch_korzystny = (bar.high - poz.cena_wejscia) / poz.cena_wejscia
            else:
                ruch_niekorzystny = (bar.high - poz.cena_wejscia) / poz.cena_wejscia
                ruch_korzystny = (poz.cena_wejscia - bar.low) / poz.cena_wejscia

            poz.mae_pct = max(poz.mae_pct, ruch_niekorzystny)
            poz.mfe_pct = max(poz.mfe_pct, ruch_korzystny)

            # Trailing stop (W-351) — wyzwalamy po poziomie ustalonym w POPRZEDNICH
            # barach (nie znamy ścieżki intrabar: high który uzbraja trailing mógł
            # paść PO low — więc bar uzbrajający nie może sam się zamknąć trailingiem).
            armed_przed = poz.trailing_aktywny
            stop_przed = poz.trailing_stop
            if self.trailing:
                self._aktualizuj_trailing(poz, bar)

            # Sprawdź wyzwalacze (kolejność: LIQ > SL > TRAIL > TP > TIMEOUT)
            powod = self._sprawdz_wyzwalacze(poz, bar, armed_przed, stop_przed)
            if powod:
                # TRAIL zamyka po poziomie z POCZĄTKU bara (to on został przebity),
                # nie po ewentualnie zacieśnionym w tym barze — pesymizm wykonania.
                if powod == "TRAIL_HIT":
                    poz.trailing_stop = stop_przed
                do_zamkniecia.append((pid, powod, bar))

        for pid, powod, bar in do_zamkniecia:
            wynik = self._zamknij(pid, self._cena_zamkniecia(self.otwarte[pid], powod, bar), powod)
            if wynik:
                zamkniete.append(wynik)
                if self._pamiec:
                    self._log_zamkniecie(wynik, bar)

        return zamkniete

    # ── Zamknięcie ─────────────────────────────────────────────────────────────

    def zamknij_manualnie(self, pozycja_id: str, cena: float, powod: str = "MANUAL") -> Optional[WynikZamkniecia]:
        if pozycja_id not in self.otwarte:
            return None
        wynik = self._zamknij(pozycja_id, cena, powod)
        if wynik:                       # W1 musi znać KAŻDE zamknięcie, nie tylko te z bara
            self._log_zamkniecie(wynik)
        return wynik

    def zamknij_wszystkie(self, cena_ostatnia: Dict[str, float], powod: str = "MANUAL") -> List[WynikZamkniecia]:
        wyniki = []
        for pid in list(self.otwarte.keys()):
            poz = self.otwarte[pid]
            cena = cena_ostatnia.get(poz.symbol, poz.cena_wejscia)
            w = self._zamknij(pid, cena, powod)
            if w:
                self._log_zamkniecie(w)  # domknięcie biegu też jest wynikiem (było gubione)
                wyniki.append(w)
        return wyniki

    # ── Statystyki ─────────────────────────────────────────────────────────────

    def podsumowanie(self) -> StatystykiSesji:
        stats = StatystykiSesji(
            sesja_id=self.sesja_id,
            kapital_startowy=self.kapital_startowy,
            kapital_koncowy=self.kapital,
        )
        stats.oblicz(self.historia_zamkniec)
        return stats

    def drukuj_raport(self) -> None:
        stats = self.podsumowanie()
        linia = "═" * 64
        print(f"\n{linia}")
        print(f"  📊 PAPER TRADING — Sesja {self.sesja_id}")
        print(linia)
        print(f"  Kapitał start: {stats.kapital_startowy:>10.2f} USDT")
        print(f"  Kapitał end:   {stats.kapital_koncowy:>10.2f} USDT")
        pnl_pct = (stats.kapital_koncowy / stats.kapital_startowy - 1) * 100
        print(f"  PnL:           {stats.total_pnl_usdt:>+10.2f} USDT  ({pnl_pct:+.2f}%)")
        print(f"  Trades:        {stats.total_trades} (W:{stats.winning_trades} / L:{stats.losing_trades})")
        print(f"  Win Rate:      {stats.win_rate:.1%}")
        print(f"  Profit Factor: {stats.profit_factor:.2f}")
        print(f"  Avg Win:       {stats.avg_win_pct:>+.2f}%   Avg Loss: {stats.avg_loss_pct:>+.2f}%")
        print(f"  Best Trade:    {stats.best_trade_pct:>+.2f}%   Worst:    {stats.worst_trade_pct:>+.2f}%")
        print(f"  Max Drawdown:  {stats.max_drawdown_pct:.2%}")
        print(f"  Avg czas:      {stats.avg_czas_bar:.1f} świec")
        print(f"  Prowizje:      {stats.total_prowizje:.2f} USDT")
        print(linia)

    # ── Wewnętrzne ─────────────────────────────────────────────────────────────

    def _aktualizuj_trailing(self, poz: OtwartaPozycja, bar: BarData) -> None:
        """
        W-351 — aktualizuje szczyt korzystnej ceny i poziom trailing stop.
        Uzbraja się dopiero po ruchu korzystnym ≥ TRAILING_AKTYWACJA_PCT, potem
        podąża za szczytem, oddając max TRAILING_GIVEBACK_FRAC zysku. Stop tylko
        się zaciska (monotonicznie) — nigdy nie cofa się przeciw pozycji.
        """
        we = poz.cena_wejscia
        if poz.kierunek == "LONG":
            poz.szczyt_cena = bar.high if poz.szczyt_cena == 0.0 else max(poz.szczyt_cena, bar.high)
            zysk_szczyt = (poz.szczyt_cena - we) / we
            if zysk_szczyt >= TRAILING_AKTYWACJA_PCT:
                nowy = poz.szczyt_cena - (poz.szczyt_cena - we) * TRAILING_GIVEBACK_FRAC
                poz.trailing_stop = nowy if not poz.trailing_aktywny else max(poz.trailing_stop, nowy)
                poz.trailing_aktywny = True
        else:  # SHORT
            poz.szczyt_cena = bar.low if poz.szczyt_cena == 0.0 else min(poz.szczyt_cena, bar.low)
            zysk_szczyt = (we - poz.szczyt_cena) / we
            if zysk_szczyt >= TRAILING_AKTYWACJA_PCT:
                nowy = poz.szczyt_cena + (we - poz.szczyt_cena) * TRAILING_GIVEBACK_FRAC
                poz.trailing_stop = nowy if not poz.trailing_aktywny else min(poz.trailing_stop, nowy)
                poz.trailing_aktywny = True

    def _sprawdz_wyzwalacze(self, poz: OtwartaPozycja, bar: BarData,
                            trail_armed: bool = False, trail_stop: float = 0.0) -> Optional[str]:
        """
        Sprawdza czy pozycja powinna być zamknięta. Kolejność: LIQ > SL > TRAIL > TP > TIMEOUT.
        trail_armed/trail_stop = stan trailingu na POCZĄTKU bara (W-351) — bar uzbrajający
        nie wyzwala trailingu (brak wiedzy o ścieżce intrabar).
        """
        if poz.kierunek == "LONG":
            if bar.low <= poz.cena_likwidacji:
                return "LIQUIDATION"
            if bar.low <= poz.stop_loss:
                return "SL_HIT"
            if trail_armed and bar.low <= trail_stop:
                return "TRAIL_HIT"
            if bar.high >= poz.take_profit:
                return "TP_HIT"
        else:  # SHORT
            if bar.high >= poz.cena_likwidacji:
                return "LIQUIDATION"
            if bar.high >= poz.stop_loss:
                return "SL_HIT"
            if trail_armed and bar.high >= trail_stop:
                return "TRAIL_HIT"
            if bar.low <= poz.take_profit:
                return "TP_HIT"

        if poz.bar_count >= self.max_bars_otwarcia:
            return "TIMEOUT"
        return None

    def _cena_zamkniecia(self, poz: OtwartaPozycja, powod: str, bar: BarData) -> float:
        """Wyznacza cenę zamknięcia z uwzględnieniem slippage."""
        if powod == "SL_HIT":
            cena = poz.stop_loss
        elif powod == "TRAIL_HIT":
            cena = poz.trailing_stop
        elif powod == "TP_HIT":
            cena = poz.take_profit
        elif powod == "LIQUIDATION":
            cena = poz.cena_likwidacji
        else:
            cena = bar.close

        # Slippage przy zamknięciu (niekorzystny dla gracza)
        if poz.kierunek == "LONG":
            return cena * (1 - SLIPPAGE_PCT)
        else:
            return cena * (1 + SLIPPAGE_PCT)

    def _zamknij(self, pozycja_id: str, cena_zamkniecia: float, powod: str) -> Optional[WynikZamkniecia]:
        poz = self.otwarte.pop(pozycja_id, None)
        if not poz:
            return None

        prowizja_wyjscia = poz.rozmiar_usdt * PROWIZJA_TAKER_PCT
        prowizja_total = poz.prowizja_wejscia + prowizja_wyjscia

        # PnL obliczony na wartości pozycji (lewarowanej)
        if poz.kierunek == "LONG":
            pnl_raw = (cena_zamkniecia - poz.cena_wejscia) / poz.cena_wejscia * poz.rozmiar_usdt
        else:
            pnl_raw = (poz.cena_wejscia - cena_zamkniecia) / poz.cena_wejscia * poz.rozmiar_usdt

        pnl_netto = pnl_raw - prowizja_total
        pnl_pct = pnl_netto / poz.kapital_zablokowany if poz.kapital_zablokowany > 0 else 0.0

        kapital_przed = self.kapital + poz.kapital_zablokowany
        self.kapital = kapital_przed + pnl_netto

        wynik = WynikZamkniecia(
            pozycja_id=pozycja_id,
            symbol=poz.symbol,
            kierunek=poz.kierunek,
            cena_wejscia=round(poz.cena_wejscia, 6),
            cena_zamkniecia=round(cena_zamkniecia, 6),
            pnl_usdt=round(pnl_netto, 4),
            pnl_pct=round(pnl_pct, 4),
            prowizja_usdt=round(prowizja_total, 4),
            mae_pct=round(poz.mae_pct, 4),
            mfe_pct=round(poz.mfe_pct, 4),
            czas_trwania_bar=poz.bar_count,
            powod_zamkniecia=powod,
            kapital_przed=round(kapital_przed, 4),
            kapital_po=round(self.kapital, 4),
            timestamp_wejscia=poz.timestamp_wejscia,
            rezim=getattr(poz, "rezim", "NORMAL"),
            interwal=getattr(poz, "interwal", ""),
        )
        self.historia_zamkniec.append(wynik)
        return wynik

    def zapisz_log(self, log) -> None:
        """
        Wpis do W1 z zewnątrz (Dyrygent loguje SYGNAŁ) — cichy no-op bez `log_dir`.

        Silnik jest JEDYNYM posiadaczem uchwytu do Pamięci Absolutnej, więc to on
        przyjmuje wpisy. Dzięki temu opt-in `log_dir` steruje CAŁYM zapisem do W1
        z jednego miejsca — a nie każdy wołający osobno decyduje, czy pisać.
        """
        if self._pamiec:
            self._pamiec.zapisz(log)

    def _log_zamkniecie(self, wynik: WynikZamkniecia, bar: "Optional[BarData]" = None) -> None:
        """
        Wpis TRADE_CLOSE do W1. `bar` opcjonalny (naprawa 2026-07-29).

        POWÓD ZMIERZONY: logowała WYŁĄCZNIE ścieżka `przetworz_bar`, a `zamknij_wszystkie`
        i `zamknij_manualnie` — nie. Pierwszy bieg zapisujący W1 dał 23 zamknięcia w silniku
        i **22 w pamięci**: pozycja domknięta na końcu biegu znikała bez śladu. Cicha strata
        w warstwie, która ma być źródłem prawdy o wynikach, jest gorsza niż brak warstwy.
        Bez bara bierzemy cenę i interwał z samego wyniku — dane są, tylko innym wejściem.
        """
        if not self._pamiec:
            return
        log = ImperiumLog(
            log_typ=TypLogu.TRADE_CLOSE,
            sesja_id=self.sesja_id,
            symbol=wynik.symbol,
            interwal=bar.interwal if bar is not None else wynik.interwal,
            cena_close=bar.close if bar is not None else wynik.cena_zamkniecia,
            cena_wejscia=wynik.cena_wejscia,
            pnl_usdt=wynik.pnl_usdt,
            pnl_pct=wynik.pnl_pct,
            powod_zamkniecia=wynik.powod_zamkniecia,
            mae_pct=wynik.mae_pct,
            mfe_pct=wynik.mfe_pct,
            czas_trwania_min=wynik.czas_trwania_bar,
            kapital_przed=wynik.kapital_przed,
            kapital_po=wynik.kapital_po,
            prowizja_usdt=wynik.prowizja_usdt,
            trade_id=wynik.pozycja_id,
            trade_status=self.zrodlo,
        )
        self._pamiec.zapisz(log)


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = PaperTradingEngine(kapital_startowy=10_000.0, sesja_id="DEMO-001")

    # Symuluj 3 transakcje z historycznymi danymi mock
    transakcje = [
        # (sygnal, bary po wejściu)
        (
            SygnalWejscia("BTCUSDT", "1H", "LONG", 0.75, 65000.0, 63500.0, 68000.0, 5, 1000.0),
            [BarData(0, 65100, 68200, 64800, 68100, 1000, "BTCUSDT", "1H")],  # TP_HIT
        ),
        (
            SygnalWejscia("ETHUSDT", "4H", "SHORT", 0.70, 3500.0, 3600.0, 3200.0, 3, 500.0),
            [BarData(0, 3480, 3620, 3400, 3550, 800, "ETHUSDT", "4H"),
             BarData(0, 3550, 3610, 3180, 3580, 900, "ETHUSDT", "4H")],  # TP_HIT bar 2
        ),
        (
            SygnalWejscia("BTCUSDT", "1H", "LONG", 0.60, 64000.0, 62000.0, 67000.0, 5, 800.0),
            [BarData(0, 63900, 64200, 61800, 63000, 700, "BTCUSDT", "1H")],  # SL_HIT
        ),
    ]

    for sygnal, bary in transakcje:
        poz = engine.wejdz(sygnal)
        if poz:
            for bar in bary:
                zamkniete = engine.przetworz_bar(bar)
                if zamkniete:
                    w = zamkniete[0]
                    znak = "✅" if w.pnl_usdt > 0 else "❌"
                    print(f"{znak} {w.symbol} {w.kierunek} → {w.powod_zamkniecia} | PnL: {w.pnl_usdt:+.2f} USDT ({w.pnl_pct:+.1%})")

    engine.drukuj_raport()
