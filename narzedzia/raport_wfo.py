"""
🔄 RAPORT WFO — Walk-Forward Optimization parametrów (W-345, Pardo).

Odkopuje `imperium/koloseum/walk_forward.py` (był gotowy + testy, bez wejścia — Prawo XV).
Optymalizuje próg `min_pewnosc` na oknie IS (in-sample), egzaminuje na OOS (out-of-sample),
przesuwa okno i powtarza. Werdykt z OOS (Prawo I): WFE = Sharpe_OOS / Sharpe_IS.

  • WFE > 0.5  → ROBUST (parametry generalizują, nie przeuczone — próg Pardo)
  • WFE ~0/<0 → PRZEUCZONY (IS świetny, OOS słaby)

To jedyna uczciwa obrona przed przeuczeniem PARAMETRÓW (różne od walk_forward_ic, który
mierzy stabilność IC neuronów — tu stroimy próg wejścia). Reuse: `optymalizuj` (DSR-guided).

Dane rynkowe LOKALNE (poza gitem) — uruchamiaj u siebie (WFO jest ciężkie — kilka minut):
    python narzedzia/raport_wfo.py dane/4h/Binance_BTCUSDT_4h.csv 4h
    python narzedzia/raport_wfo.py dane/dzienne/Binance_ETHUSDT_d.csv 1d --is 500 --oos 150
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def ewaluator_backtest(interwal: str, okno: int = 60):
    """Zwraca ewaluator(bary, params) -> (kapitał, zwroty per bar) na wycinku."""
    from imperium.koloseum.backtest import backtest

    def ev(bary, params):
        eng = backtest("x", interwal, bary=list(bary), okno=okno, auto_rezim=True,
                       min_pewnosc=float(params.get("min_pewnosc", 0.55)))
        eq = list(getattr(eng, "krzywa_equity", []) or [])
        zwroty = [eq[i] / eq[i - 1] - 1 for i in range(1, len(eq)) if eq[i - 1]]
        return float(getattr(eng, "kapital_calkowity", 0.0)), zwroty
    return ev


def raport_pliku(bary, interwal: str, rozmiar_is: int, rozmiar_oos: int,
                 okno: int, n_iteracji: int, lo: float, hi: float) -> str:
    from imperium.koloseum.optymalizator import PrzestrzeńParam
    from imperium.koloseum.walk_forward import walk_forward
    rap = walk_forward(
        list(bary), ewaluator_backtest(interwal, okno=okno),
        przestrzenie=[PrzestrzeńParam("min_pewnosc", lo, hi)],
        rozmiar_is=rozmiar_is, rozmiar_oos=rozmiar_oos, n_iteracji=n_iteracji)
    cv = rap.stabilnosc_parametrow.get("min_pewnosc", 0.0)
    return "\n".join([
        f"   werdykt: {rap.werdykt}  ({rap.powod})",
        f"   okien: {rap.n_okien} | WFE śr: {rap.wfe_srednia:+.3f} | "
        f"OOS Sharpe: {rap.oos_sharpe_zagregowany:+.3f} | CV(min_pewnosc): {cv:.2f}",
    ])


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Raport WFO parametrów (W-345, Pardo)")
    p.add_argument("plik")
    p.add_argument("interwal")
    p.add_argument("--is", dest="rozmiar_is", type=int, default=500)
    p.add_argument("--oos", type=int, default=150)
    p.add_argument("--okno", type=int, default=60)
    p.add_argument("--iteracje", type=int, default=30)
    p.add_argument("--lo", type=float, default=0.45)
    p.add_argument("--hi", type=float, default=0.75)
    args = p.parse_args()
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    try:
        bary = wczytaj_csv(args.plik, args.interwal)
    except Exception as e:  # noqa: BLE001
        print(f"Nie wczytano {args.plik}: {e}")
        sys.exit(1)
    print(f"🔄 RAPORT WFO — {Path(args.plik).name} ({len(bary)} barów), "
          f"IS={args.rozmiar_is} OOS={args.oos}, okno={args.okno}")
    print(raport_pliku(bary, args.interwal, args.rozmiar_is, args.oos,
                       args.okno, args.iteracje, args.lo, args.hi))
