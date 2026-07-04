"""
🔬 WALK-FORWARD IC — czy skill neuronu jest STABILNY w czasie (Prawo XVI, OOS).

Pojedynczy IC (raport_ic.py) mówi ILE, ale nie czy to POWTARZALNE. Neuron może mieć
wysoki IC bo trafił w jeden reżim, a w innym się myli (przeuczenie do okresu). Walk-forward
dzieli historię na K KOLEJNYCH okien i mierzy IC WARUNKOWY w każdym osobno:

  • STABILNY skill  → IC ma ten sam ZNAK w większości okien (np. ≥75%) → prawdziwa przewaga.
  • PRZEUCZONY      → IC skacze między + a − → to szum jednego okresu, NIE ufać.

Neurony (reguły) nie są trenowane per-okno, więc każde okno jest OOS z natury — brak
look-ahead. Reuse: `czytnik_csv` + `backtest(mierz_ic, ic_warunkowy)`.

WERDYKT per neuron:
  ROBUST   — |średni IC| > prog, spójność znaku ≥ prog_spojnosci, ≥ min_okien okien
  NIEPEWNY — za mało okien / mieszany znak
  SZUM     — |średni IC| < prog

Użycie:
  python narzedzia/walk_forward_ic.py dane/4h/Binance_BTCUSDT_4h.csv 4h --okna 4
  python narzedzia/walk_forward_ic.py --glob "dane/4h/Binance_*_4h.csv" 4h --okna 4
"""

from __future__ import annotations

import argparse
import glob as _glob
import logging
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _ic_per_okno(bary, interwal, okna, okno_backtest, max_barow=None):
    """Zwraca {neuron_id: [IC_okno1, IC_okno2, ...]} — IC warunkowy per okno."""
    from imperium.koloseum.backtest import backtest
    if max_barow:
        bary = bary[-max_barow:]
    n = len(bary)
    rozmiar = n // okna
    per_neuron: dict = {}
    for k in range(okna):
        seg = bary[k * rozmiar: (k + 1) * rozmiar] if k < okna - 1 else bary[k * rozmiar:]
        if len(seg) <= okno_backtest + 30:      # za mało barów na decyzje w oknie
            continue
        print(f"    okno {k + 1}/{okna} ({len(seg)} barów)...", file=sys.stderr, flush=True)
        try:
            eng = backtest("x", interwal, bary=seg, mierz_ic=True, okno=okno_backtest)
        except Exception as e:  # noqa: BLE001
            print(f"    ⚠️ okno {k + 1}: {e}", file=sys.stderr, flush=True)
            continue
        ic = getattr(eng, "ic_warunkowy", {}) or {}
        for nid, v in ic.items():
            if v == v:   # nie-NaN
                per_neuron.setdefault(nid, []).append(v)
    return per_neuron


def analizuj(per_neuron, prog=0.03, prog_spojnosci=0.75, min_okien=3):
    """Dla każdego neuronu: średni IC, spójność znaku, werdykt."""
    wynik = []
    for nid, ics in per_neuron.items():
        if len(ics) < 2:
            continue
        sredni = statistics.mean(ics)
        znak = 1 if sredni >= 0 else -1
        zgodne = sum(1 for v in ics if (v >= 0) == (znak > 0))
        spojnosc = zgodne / len(ics)
        if len(ics) >= min_okien and abs(sredni) >= prog and spojnosc >= prog_spojnosci:
            werdykt = "ROBUST" + (" (odwróć)" if sredni < 0 else "")
        elif abs(sredni) < prog:
            werdykt = "szum"
        else:
            werdykt = "niepewny"
        wynik.append({"neuron": nid, "ic": round(sredni, 4), "okien": len(ics),
                      "spojnosc": round(spojnosc, 2), "werdykt": werdykt})
    wynik.sort(key=lambda x: (x["werdykt"].startswith("ROBUST"), abs(x["ic"])), reverse=True)
    return wynik


def raport(pliki, interwal, okna=4, okno_backtest=250, max_barow=None) -> str:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    agg: dict = {}
    for i, plik in enumerate(pliki, 1):
        print(f"  [{i}/{len(pliki)}] {Path(plik).name}", file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠️ {Path(plik).name}: {e}", file=sys.stderr, flush=True)
            continue
        per = _ic_per_okno(bary, interwal, okna, okno_backtest, max_barow=max_barow)
        for nid, ics in per.items():
            agg.setdefault(nid, []).extend(ics)   # IC z okien × pary razem
    ranking = analizuj(agg)
    if not ranking:
        return "🔬 WALK-FORWARD IC — brak wystarczających danych."
    linie = [f"🔬 WALK-FORWARD IC — {len(pliki)} par × {okna} okien, {len(ranking)} neuronów",
             "   ROBUST = |IC|>0.03 + ten sam znak w ≥75% okien (skill stabilny, nie przeuczony)",
             "",
             f"   {'NEURON':<10} {'śr.IC':>8} {'okien':>6} {'spójn':>6}  werdykt"]
    robust = [r for r in ranking if r["werdykt"].startswith("ROBUST")]
    for r in (robust or ranking)[:20]:
        linie.append(f"   {r['neuron']:<10} {r['ic']:>+8.4f} {r['okien']:>6} "
                     f"{r['spojnosc']:>6.0%}  {r['werdykt']}")
    linie.append("")
    linie.append(f"   ✅ ROBUST: {len(robust)} | ⚪ szum/niepewne: {len(ranking) - len(robust)}")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Walk-forward IC (Prawo XVI, OOS)")
    p.add_argument("plik", nargs="?", help="pojedynczy CSV (lub użyj --glob)")
    p.add_argument("interwal")
    p.add_argument("--glob", default=None, help="wzorzec wielu par")
    p.add_argument("--okna", type=int, default=4)
    p.add_argument("--okno-backtest", type=int, default=250)
    p.add_argument("--max-barow", type=int, default=None)
    args = p.parse_args()
    if args.glob:
        pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    elif args.plik:
        pliki = [args.plik]
    else:
        print("Podaj plik CSV albo --glob wzorzec"); sys.exit(1)
    if not pliki:
        print("Brak plików."); sys.exit(1)
    print(raport(pliki, args.interwal, okna=args.okna,
                 okno_backtest=args.okno_backtest, max_barow=args.max_barow))
