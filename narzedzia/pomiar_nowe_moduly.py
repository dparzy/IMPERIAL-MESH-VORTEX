"""
🔬 POMIAR NOWYCH MODUŁÓW (Prawo XVI) — EXP-13/14/15 + OC-06/08.

Odpowiada na pytanie Cezara: czy nowe moduły NIOSĄ NOWĄ INFORMACJĘ, czy dublują
istniejące? (Prawo XVI: redundancja mierzona, nie zgadywana.)

Dwa pomiary na realnych danych (Binance 4h, ~18k barów):
  1. DEKORELACJA — korelacja sygnałów EXP-13/14/15 vs reszta zwiadowców.
     |ρ|>0.80 → redundancja (waga w dół); |ρ|<0.20 → filar siły (zachować).
  2. IC (Information Coefficient, W-369) — Spearman(sygnał_t, zwrot_{t+h}).
     IC mierzy SKILL: IC≈0 = szum, IC>0.03 = realna przewaga predykcyjna.

Uruchom: python narzedzia/pomiar_nowe_moduly.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np

from imperium.akwedukty.czytnik_csv import wczytaj_csv
from imperium.legiony.rejestr import wszyscy_zwiadowcy
from imperium.legiony.diagnostyka_korelacji import (
    raport_dekorelacji, zbierz_sygnaly_zwiadowcow,
)
from imperium.legiony.metryki_ic import _spearman

NOWE = {"EXP-13", "EXP-14", "EXP-15"}
OKNO = 60
HORYZONTY = (1, 6, 30)

# Pełna matryca: 5 par × 3 interwały (wszystko co mamy w repo).
PARY = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]
INTERWALY = {
    "1h": "dane/godzinowe/Binance_{p}_1h.csv",
    "4h": "dane/4h/Binance_{p}_4h.csv",
    "1d": "dane/dzienne/Binance_{p}_d.csv",
}


def _zwroty_forward(bary, okno, h, krok=1):
    """Forward return zwrot_{t+h} dla każdego kroku okna (wyrównane z sygnałami).
    krok = to samo próbkowanie co zbierz_sygnaly_zwiadowcow (range(okno, n+1, krok))."""
    closes = [float(b["close"]) for b in bary]
    zwroty = []
    for koniec in range(okno, len(bary) + 1, krok):
        idx = koniec - 1            # bieżący bar (ostatni w oknie)
        if idx + h < len(closes):
            zwroty.append(closes[idx + h] / closes[idx] - 1.0)
        else:
            zwroty.append(None)
    return zwroty


def _ic_modulu(serie, bary, nowy, krok=1):
    """IC modułu dla każdego horyzontu (lub None)."""
    if nowy not in serie or not serie[nowy]:
        return [None] * len(HORYZONTY)
    syg = np.array(serie[nowy], dtype=float)
    out = []
    for h in HORYZONTY:
        zwr = _zwroty_forward(bary, OKNO, h, krok=krok)
        pary = [(s, z) for s, z in zip(syg, zwr) if z is not None and not np.isnan(s)]
        if len(pary) < 30 or np.std([p[0] for p in pary]) < 1e-10:
            out.append(None)
        else:
            out.append(_spearman(np.array([p[0] for p in pary]),
                                 np.array([p[1] for p in pary])))
    return out


MAX_BAROW = 6000   # limit na plik (1h ma 76k — ścinamy do ostatnich 6k dla szybkości)
KROK = 3           # próbkowanie okna (kompromis szybkość/dokładność)


def _pomiar_jednego(sciezka, interwal):
    """Zwraca (dekorelacja_max{mod:|ρ|}, ic{mod:[ic_h...]}) dla jednego pliku."""
    bary = wczytaj_csv(sciezka, interwal=interwal)
    if len(bary) < OKNO + max(HORYZONTY) + 50:
        return None, None, 0
    if len(bary) > MAX_BAROW:
        bary = bary[-MAX_BAROW:]
    zwiadowcy = wszyscy_zwiadowcy()
    raport = raport_dekorelacji(bary, zwiadowcy, okno=OKNO, krok=KROK)
    dekor = {}
    for nowy in NOWE:
        kor = []
        for klucz, k in raport["macierz"].items():
            a, b = klucz.split("~")
            if (a == nowy or b == nowy) and k is not None:
                kor.append(abs(k))
        dekor[nowy] = max(kor) if kor else None
    serie = zbierz_sygnaly_zwiadowcow(bary, zwiadowcy, okno=OKNO, krok=KROK)
    ic = {nowy: _ic_modulu(serie, bary, nowy, krok=KROK) for nowy in NOWE}
    return dekor, ic, len(bary)


def _fmt(v):
    return f"{v:+.3f}" if v is not None else "  n/a "


def main():
    base = os.path.join(os.path.dirname(__file__), "..")
    print("POMIAR MATRYCOWY: 5 par × 3 interwały (Prawo XVI + Prawo I)\n")

    # agregacja IC i dekorelacji po wszystkich (para,TF)
    agg_dekor = {m: [] for m in NOWE}
    agg_ic = {m: {h: [] for h in HORYZONTY} for m in NOWE}

    for interwal, wzor in INTERWALY.items():
        print("=" * 78)
        print(f" INTERWAŁ {interwal}")
        print("=" * 78)
        naglowek = f"{'para':9} {'moduł':8} {'max|ρ|':>8}  " + \
                   "  ".join(f"IC(h={h})" for h in HORYZONTY)
        print(naglowek)
        for para in PARY:
            sciezka = os.path.join(base, wzor.format(p=para))
            if not os.path.exists(sciezka):
                print(f"{para:9} BRAK PLIKU {sciezka}")
                continue
            try:
                dekor, ic, n = _pomiar_jednego(sciezka, interwal)
            except Exception as e:
                print(f"{para:9} BŁĄD: {e}")
                continue
            if dekor is None:
                print(f"{para:9} za mało barów ({n})")
                continue
            for nowy in sorted(NOWE):
                mx = dekor.get(nowy)
                ics = ic.get(nowy, [None] * len(HORYZONTY))
                print(f"{para:9} {nowy:8} {(_fmt(mx) if mx is not None else '  n/a '):>8}  " +
                      "   ".join(_fmt(v) for v in ics))
                if mx is not None:
                    agg_dekor[nowy].append(mx)
                for h, v in zip(HORYZONTY, ics):
                    if v is not None:
                        agg_ic[nowy][h].append(v)
        print()

    # ── PODSUMOWANIE ZBIORCZE ─────────────────────────────────────────────
    print("=" * 78)
    print(" PODSUMOWANIE ZBIORCZE (średnia po wszystkich parach i interwałach)")
    print("=" * 78)
    for nowy in sorted(NOWE):
        d = agg_dekor[nowy]
        d_txt = f"max|ρ| śr={np.mean(d):.3f} (n={len(d)})" if d else "brak (martwy)"
        ic_txt = " | ".join(
            f"IC(h={h})={np.mean(agg_ic[nowy][h]):+.3f}" if agg_ic[nowy][h] else f"IC(h={h})=n/a"
            for h in HORYZONTY
        )
        print(f"  {nowy}: {d_txt}  →  {ic_txt}")

    print("\n  INTERPRETACJA:")
    print("  • |ρ|>0.80 redundancja | |IC|>0.03 realny skill | martwy = wyciszyć")
    print("=" * 78)


if __name__ == "__main__":
    main()
