"""
📊 RAPORT IC ROJU — który neuron ma REALNY skill predykcyjny (Prawo XVI/XXV).

Uruchamia backtest(mierz_ic=True) na prawdziwych świecach i agreguje Information
Coefficient (Spearman(sygnał_t, zwrot_{t+h})) per neuron przez wszystkie pary.

INTERPRETACJA (Grinold & Kahn, BIB-025):
  |IC| < 0.02  → szum (brak przewagi)
  |IC| ≈ 0.03+ → realna, choć słaba przewaga predykcyjna
  |IC| > 0.05  → mocny sygnał (rzadkość na krypto)
IC UJEMNE = neuron myli się systematycznie → kandydat do ODWRÓCENIA lub wygaszenia.

To fundament „metod treningowych": wagi neuronów powinny iść za ZMIERZONYM IC, nie za
intuicją. NEWS-01..04 pojawią się z realnym IC dopiero gdy popłynie feed newsów (lokal).

Użycie:
  python narzedzia/raport_ic.py                      # domyślnie 5 par 4h
  python narzedzia/raport_ic.py --glob "dane/dzienne/*_d.csv" --interwal 1d
  python narzedzia/raport_ic.py --top 20
"""

from __future__ import annotations

import argparse
import glob as _glob
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def zbierz_ic(pliki, interwal: str, okno: int = 250, max_barow=None) -> dict:
    """Uruchamia backtest(mierz_ic) na każdym pliku, agreguje IC per neuron (średnia)."""
    from imperium.koloseum.backtest import backtest
    suma: dict = {}
    liczba: dict = {}
    pary = 0
    for plik in pliki:
        try:
            eng = backtest(plik, interwal, okno=okno, max_barow=max_barow, mierz_ic=True)
        except Exception as e:  # noqa: BLE001 — pojedyncza para nie może wywalić raportu
            print(f"  ⚠️ {Path(plik).name}: {e}")
            continue
        ic = getattr(eng, "ic_srednie", {}) or {}
        pary += 1
        for nid, v in ic.items():
            if v == v:   # nie-NaN
                suma[nid] = suma.get(nid, 0.0) + v
                liczba[nid] = liczba.get(nid, 0) + 1
    srednie = {nid: suma[nid] / liczba[nid] for nid in suma}
    return {"ic": srednie, "pary": pary, "pokrycie": liczba}


def _klasa_ic(v: float) -> str:
    a = abs(v)
    if a < 0.02:
        return "szum"
    if a < 0.05:
        return "słaba przewaga"
    return "MOCNY"


def raport(pliki, interwal: str, top: int = 15, okno: int = 250, max_barow=None) -> str:
    w = zbierz_ic(pliki, interwal, okno=okno, max_barow=max_barow)
    ic = w["ic"]
    if not ic:
        return "📊 RAPORT IC — brak danych (żaden neuron nie zebrał próbek IC)."
    ranking = sorted(ic.items(), key=lambda x: abs(x[1]), reverse=True)
    # Uczciwie (Prawo I): IC bardzo wysokie (|IC|>0.2) na krótkich danych = ARTEFAKT
    # rzadkich sygnałów + remisów Spearmana, NIE realny skill (prawdziwy IC krypto ~0.02-0.05).
    # Wiarygodny pomiar wymaga PEŁNEJ historii i kontroli (patrz narzedzia/pomiar_nowe_moduly.py).
    podejrzane = sum(1 for _, v in ranking if abs(v) > 0.2)
    linie = [f"📊 RAPORT IC ROJU — {w['pary']} par, interwał {interwal}, {len(ic)} neuronów zmierzonych",
             "   (IC = Spearman sygnału z przyszłym zwrotem; |IC|>0.03 = realna przewaga)"]
    if podejrzane > len(ranking) // 3:
        linie.append("   ⚠️ WIARYGODNOŚĆ NISKA: dużo |IC|>0.2 = artefakt rzadkich sygnałów/małej próby.")
        linie.append("      Uruchom na PEŁNEJ historii (--max-barow bez limitu, wszystkie pary).")
    linie.append("")
    linie.append(f"   {'NEURON':<10} {'IC':>8}  {'par':>4}  ocena")
    for nid, v in ranking[:top]:
        linie.append(f"   {nid:<10} {v:>+8.4f}  {w['pokrycie'][nid]:>4}  {_klasa_ic(v)}")
    # neurony ujemne (systematyczny błąd — kandydaci do odwrócenia)
    ujemne = [(n, v) for n, v in ranking if v < -0.02]
    if ujemne:
        linie.append("")
        linie.append(f"   ⚠️ IC UJEMNE (kandydaci do odwrócenia/wygaszenia): "
                     f"{', '.join(f'{n}({v:+.3f})' for n, v in ujemne[:8])}")
    news = [n for n in ic if n.startswith("NEWS")]
    linie.append("")
    linie.append(f"   📰 NEWS-01..04: {'zmierzone' if news else 'abstynują (brak feedu — ożyją lokalnie)'}")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)   # wycisz szum Bramy — chcemy sam raport
    p = argparse.ArgumentParser(description="Raport IC roju (Prawo XVI)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv", help="wzorzec plików CSV")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--top", type=int, default=15)
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--max-barow", type=int, default=None)
    args = p.parse_args()
    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print(f"Brak plików dla wzorca: {args.glob}")
        sys.exit(1)
    print(raport(pliki, args.interwal, top=args.top, okno=args.okno, max_barow=args.max_barow))
