"""
🖼️ WYKRES BACKTESTU — oczy Cezara (Prawo XV: Kartograf był niewpięty = utrata potencjału).

Jedna komenda: backtest → PNG z DWOMA panelami:
  • góra: cena zamknięcia + EMA-50 + znaczniki transakcji (▲ wejście, ▼ wyjście,
    zielone = zysk, czerwone = strata, linia łączy wejście↔wyjście)
  • dół:  krzywa kapitału bar po barze (czy Imperium zarabia, czy krwawi)

Reuse (Prawo XVI): swiatynie/kartograf.plot_run (istniał, ale wpięty tylko
w pierwszy_zwiadowca — teraz służy KAŻDEMU backtestowi) + koloseum/backtest.

Użycie (lokal):
  python narzedzia/wykres_backtestu.py dane/4h/Binance_DOGEUSDT_4h.csv 4h
  python narzedzia/wykres_backtestu.py dane/4h/Binance_BTCUSDT_4h.csv 4h --max-barow 3000
→ zapisuje wykres_DOGEUSDT_4h.png obok repo; otwierasz dwuklikiem.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ema(ceny, okres=50):
    """Prosta EMA (None w rozgrzewce) — tylko do rysunku, nie do decyzji."""
    if len(ceny) < okres:
        return [None] * len(ceny)
    wynik = [None] * (okres - 1)
    k = 2.0 / (okres + 1)
    e = sum(ceny[:okres]) / okres
    wynik.append(e)
    for c in ceny[okres:]:
        e = c * k + e * (1 - k)
        wynik.append(e)
    return wynik


def trades_z_historii(historia, bary):
    """WynikZamkniecia → format Kartografa {entry_idx, entry_price, exit_idx, exit_price, win}."""
    ts2idx = {b["timestamp"]: i for i, b in enumerate(bary)}
    trades = []
    for w in historia:
        e_idx = ts2idx.get(w.timestamp_wejscia)
        if e_idx is None:
            continue   # brak mapowania (np. ts=0) → pomiń na rysunku
        x_idx = min(e_idx + max(w.czas_trwania_bar, 0), len(bary) - 1)
        trades.append({"entry_idx": e_idx, "entry_price": w.cena_wejscia,
                       "exit_idx": x_idx, "exit_price": w.cena_zamkniecia,
                       "win": w.pnl_usdt > 0})
    return trades


def rysuj(plik_csv: str, interwal: str, max_barow=None, okno: int = 250,
          out: str | None = None, auto_rezim: bool = True) -> str:
    """Backtest + PNG. Zwraca ścieżkę zapisanego wykresu."""
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    from imperium.koloseum.backtest import backtest
    from imperium.swiatynie.kartograf import plot_run

    if okno < 1:
        raise ValueError("okno musi być >= 1")
    if max_barow is not None and max_barow < 1:
        raise ValueError("max_barow musi być >= 1 (lub None = całość)")
    bary = wczytaj_csv(plik_csv, interwal)
    if max_barow:
        bary = bary[-max_barow:]
    symbol = bary[0].get("symbol", Path(plik_csv).stem) if bary else "?"
    print(f"  backtest {symbol} {interwal} ({len(bary)} barów)...", file=sys.stderr, flush=True)
    eng = backtest("x", interwal, bary=bary, okno=okno, auto_rezim=auto_rezim)

    ceny = [b["close"] for b in bary]
    trades = trades_z_historii(eng.historia_zamkniec, bary)
    st = eng.podsumowanie()
    tytul = (f"{symbol} {interwal} | trades: {len(trades)} | "
             f"PnL: {st.total_pnl_usdt:+.0f}$ | WR: {st.win_rate:.0%}")
    if out is None:
        out = str(ROOT / f"wykres_{symbol}_{interwal}.png")
    plot_run(ceny, _ema(ceny), trades, list(getattr(eng, "krzywa_equity", [])),
             title=tytul, out_path=out)
    return out


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Backtest → wykres PNG (oczy Cezara)")
    p.add_argument("plik")
    p.add_argument("interwal")
    p.add_argument("--max-barow", type=int, default=None)
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--out", default=None)
    p.add_argument("--bez-auto-rezim", action="store_true")
    args = p.parse_args()
    sciezka = rysuj(args.plik, args.interwal, max_barow=args.max_barow,
                    okno=args.okno, out=args.out, auto_rezim=not args.bez_auto_rezim)
    print(f"🖼️ Wykres zapisany: {sciezka}\n   Otwórz dwuklikiem (PNG).")
