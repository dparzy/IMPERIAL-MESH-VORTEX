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
DANE = "dane/4h/Binance_BTCUSDT_4h.csv"
OKNO = 60
HORYZONTY = (1, 6, 30)  # 4h, 1d, 5d


def _zwroty_forward(bary, okno, h):
    """Forward return zwrot_{t+h} dla każdego kroku okna (wyrównane z sygnałami)."""
    closes = [float(b["close"]) for b in bary]
    zwroty = []
    for koniec in range(okno, len(bary) + 1):
        idx = koniec - 1            # bieżący bar (ostatni w oknie)
        if idx + h < len(closes):
            zwroty.append(closes[idx + h] / closes[idx] - 1.0)
        else:
            zwroty.append(None)
    return zwroty


def main():
    sciezka = os.path.join(os.path.dirname(__file__), "..", DANE)
    bary = wczytaj_csv(sciezka, interwal="4h")
    print(f"Wczytano {len(bary)} barów 4h ({DANE})\n")

    zwiadowcy = wszyscy_zwiadowcy()

    # ── 1. DEKORELACJA ────────────────────────────────────────────────────
    print("=" * 70)
    print(" 1. DEKORELACJA (Prawo XVI) — czy nowe moduły dublują istniejące?")
    print("=" * 70)
    raport = raport_dekorelacji(bary, zwiadowcy, okno=OKNO, krok=4)
    print(f"Moduły: {raport['liczba_modulow']} | kroki: {raport['liczba_krokow']}\n")

    # Pary z udziałem nowych modułów
    print("Pary z udziałem EXP-13/14/15 (sortowane po |ρ|):")
    pary_nowe = []
    for klucz, k in raport["macierz"].items():
        a, b = klucz.split("~")
        if (a in NOWE or b in NOWE) and k is not None:
            pary_nowe.append((a, b, k))
    pary_nowe.sort(key=lambda t: -abs(t[2]))
    for a, b, k in pary_nowe[:20]:
        flaga = "🔴 REDUNDANCJA" if abs(k) > 0.80 else ("🟢 filar" if abs(k) < 0.20 else "")
        print(f"  {a:8} ~ {b:8}  ρ={k:+.3f}  {flaga}")

    # Werdykt per nowy moduł: max |ρ| z innymi
    print("\nWerdykt per nowy moduł (max |ρ| z dowolnym innym):")
    for nowy in sorted(NOWE):
        kor = [abs(k) for (a, b, k) in pary_nowe if a == nowy or b == nowy]
        if kor:
            mx = max(kor)
            status = "🔴 redundantny" if mx > 0.80 else ("🟢 unikalny" if mx < 0.40 else "🟡 umiarkowany")
            print(f"  {nowy}: max|ρ|={mx:.3f} → {status}")
        else:
            print(f"  {nowy}: brak danych (stały sygnał?)")

    # ── 2. IC (skill) ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(" 2. IC (W-369) — czy nowe moduły mają SKILL predykcyjny?")
    print("=" * 70)
    serie = zbierz_sygnaly_zwiadowcow(bary, zwiadowcy, okno=OKNO, krok=1)

    print(f"{'Moduł':10} " + " ".join(f"IC(h={h})".rjust(10) for h in HORYZONTY))
    for nowy in sorted(NOWE):
        if nowy not in serie or not serie[nowy]:
            print(f"{nowy:10} brak sygnałów")
            continue
        syg = np.array(serie[nowy], dtype=float)
        wiersz = f"{nowy:10} "
        for h in HORYZONTY:
            zwr = _zwroty_forward(bary, OKNO, h)
            pary = [(s, z) for s, z in zip(syg, zwr)
                    if z is not None and not np.isnan(s)]
            if len(pary) < 30 or np.std([p[0] for p in pary]) < 1e-10:
                wiersz += "      n/a "
                continue
            x = np.array([p[0] for p in pary])
            y = np.array([p[1] for p in pary])
            ic = _spearman(x, y)
            wiersz += f"{ic:+.4f}".rjust(10) + " "
        print(wiersz)

    # Baseline: IC kilku ugruntowanych zwiadowców dla porównania
    print("\n  (baseline — ugruntowane moduły dla porównania skali IC):")
    for ref in ("EXP-01", "EXP-03", "EXP-04"):
        if ref not in serie or not serie[ref]:
            continue
        syg = np.array(serie[ref], dtype=float)
        wiersz = f"  {ref:8} "
        for h in HORYZONTY:
            zwr = _zwroty_forward(bary, OKNO, h)
            pary = [(s, z) for s, z in zip(syg, zwr)
                    if z is not None and not np.isnan(s)]
            if len(pary) < 30 or np.std([p[0] for p in pary]) < 1e-10:
                wiersz += "      n/a "
                continue
            ic = _spearman(np.array([p[0] for p in pary]), np.array([p[1] for p in pary]))
            wiersz += f"{ic:+.4f}".rjust(10) + " "
        print(wiersz)

    print("\n" + "=" * 70)
    print(" INTERPRETACJA:")
    print("  • |ρ|>0.80 = redundancja → rozważ wagę w dół lub scalenie")
    print("  • |IC|>0.03 = realny skill predykcyjny (na crypto już dobre)")
    print("  • |IC|≈0 + |ρ| niskie = dywersyfikuje ryzyko, ale nie przewiduje")
    print("  • Sygnały obronne (EXP-15 PIN) mają z natury niski IC kierunkowy —")
    print("    ich wartość to tłumienie roju, nie predykcja kierunku.")
    print("=" * 70)


if __name__ == "__main__":
    main()
