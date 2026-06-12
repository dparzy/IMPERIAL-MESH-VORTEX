"""
📊💎 POMIAR PORTFELA (W-290) — czy dywersyfikacja 5 par przekracza próg Sharpe?

ODKRYCIE 2026-06-11: rój ma DODATNI edge na 1D na WSZYSTKICH 5 parach (PF>1),
ale żadna pojedyncza para nie przechodzi Etapu I (Sharpe<1.0 — zwroty zbyt zmienne).

HIPOTEZA (klasyka portfelowa, Markowitz; ROADMAP Faza 3 "Kostka Rubika"): złożenie
N częściowo nieskorelowanych dodatnich strumieni daje Sharpe portfela WYŻSZY niż
średnia z osobna — bo wariancja portfela maleje z dekorelacją, a średnia nie.
  Sharpe_portfela ≈ Sharpe_śr / √(śr_korelacja)  (dla równych wag/vol)

Metoda (Prawo I — z realnych krzywych equity, bez look-ahead):
  1. Backtest każdej pary → krzywa equity per bar (z timestampami barów).
  2. Dzienne zwroty equity, wyrównane po dacie UTC (unia osi czasu).
  3. Portfel równoważony: zwrot_t = średnia dostępnych par tego dnia.
  4. Sharpe annualizowany + DSR (W-282) + MaxDD + macierz korelacji par.

Uruchom: python narzedzia/pomiar_portfela.py
"""

import logging
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest          # noqa: E402
from imperium.koloseum.walidacja import deflated_sharpe  # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv   # noqa: E402

PARY = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
OKNO = 250
_D = 86_400_000


def krzywa_z_timestampami(plik, interwal="1D"):
    """Backtest pary → {dzien_utc: equity} (dzień = timestamp//doba)."""
    bary = wczytaj_csv(plik, interwal=interwal)
    if len(bary) <= OKNO:
        return {}
    eng = backtest("", interwal, bary=bary, tryb="agregat", auto_rezim=True)
    eq = eng.krzywa_equity
    # krzywa_equity[i] odpowiada bary[OKNO+i] (ostatni punkt = po domknięciu, pomijamy)
    ts = [int(b["timestamp"]) for b in bary[OKNO:]]
    out = {}
    for i, e in enumerate(eq[:len(ts)]):
        out[ts[i] // _D] = e
    return out


def dzienne_zwroty(krzywa: dict) -> dict:
    """{dzien: equity} → {dzien: zwrot} (po kolejnych dniach z equity)."""
    dni = sorted(krzywa)
    zwroty = {}
    for j in range(1, len(dni)):
        e0, e1 = krzywa[dni[j - 1]], krzywa[dni[j]]
        if e0 > 0:
            zwroty[dni[j]] = e1 / e0 - 1.0
    return zwroty


def sharpe_roczny(zwroty: list) -> float:
    z = np.asarray(zwroty, dtype=float)
    sd = z.std(ddof=1)
    return float(z.mean() / sd * math.sqrt(365)) if sd > 0 else 0.0


def maxdd(zwroty: list) -> float:
    krzywa = np.cumprod(1 + np.asarray(zwroty, dtype=float))
    szczyt = np.maximum.accumulate(krzywa)
    return float(((szczyt - krzywa) / szczyt).max())


def main():
    print("📊 POMIAR PORTFELA (W-290) — 5 par 1D, równoważony, AUTO\n")
    streamy = {}
    for p in PARY:
        kr = krzywa_z_timestampami(f"dane/dzienne/Binance_{p}_d.csv")
        z = dzienne_zwroty(kr)
        if z:
            streamy[p] = z
            print(f"  {p:9} dni z equity: {len(z)}  Sharpe_r={sharpe_roczny(list(z.values())):+.2f}")

    # Unia dni → portfel równoważony (średnia dostępnych par tego dnia)
    wszystkie_dni = sorted(set().union(*[set(z) for z in streamy.values()]))
    port = []
    for d in wszystkie_dni:
        dzis = [streamy[p][d] for p in streamy if d in streamy[p]]
        if dzis:
            port.append(sum(dzis) / len(dzis))

    sr = sharpe_roczny(port)
    dsr = deflated_sharpe(port, n_prob=len(PARY))
    print(f"\n=== PORTFEL RÓWNOWAŻONY ({len(port)} dni) ===")
    print(f"  Sharpe roczny: {sr:+.2f}")
    print(f"  MaxDD:         {maxdd(port):.1%}")
    print(f"  DSR (n_prob={len(PARY)}): {dsr['dsr']}  => "
          f"{'✅ ETAP I (Sharpe>1 i DSR≥0.95)' if sr > 1.0 and dsr['ok'] else '⛔ jeszcze nie'}")

    # Macierz korelacji (Prawo XVI — dywersyfikacja mierzona)
    print("\n=== KORELACJE par (dzienne zwroty, wspólne dni) ===")
    klucze = list(streamy)
    print("           " + "  ".join(f"{k[:4]:>6}" for k in klucze))
    korr_poza = []
    for a in klucze:
        wiersz = []
        for b in klucze:
            wsp = sorted(set(streamy[a]) & set(streamy[b]))
            if len(wsp) > 5:
                va = np.array([streamy[a][d] for d in wsp])
                vb = np.array([streamy[b][d] for d in wsp])
                c = float(np.corrcoef(va, vb)[0, 1]) if va.std() and vb.std() else 0.0
            else:
                c = float("nan")
            wiersz.append(c)
            if a != b and not math.isnan(c):
                korr_poza.append(c)
        print(f"  {a[:9]:9} " + "  ".join(f"{c:+.2f}".rjust(6) for c in wiersz))
    if korr_poza:
        print(f"\n  Średnia korelacja par: {sum(korr_poza)/len(korr_poza):+.2f} "
              f"(niższa = mocniejsza dywersyfikacja, Prawo XVI)")


if __name__ == "__main__":
    main()
