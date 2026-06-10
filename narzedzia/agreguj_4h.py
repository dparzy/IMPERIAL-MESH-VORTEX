"""
🧱 AGREGATOR 4H — buduje bary 4H z plików 1H (dane/godzinowe → dane/4h).

DLA NOWICJUSZA: 1 bar 4H = 4 kolejne bary 1H wyrównane do siatki UTC
(00:00, 04:00, 08:00...): open pierwszego, close ostatniego, high=max,
low=min, volume=suma. Niekompletne okna (luki w danych / końcówka) są
ODRZUCANE — niepełny bar to fałszywy bar (Prawo I).

Uruchom:  python narzedzia/agreguj_4h.py
Wyjście:  dane/4h/Binance_<PARA>_4h.csv (prosty format Imperium:
          timestamp,open,high,low,close,volume — czytnik czyta go wprost).
"""

import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402

CZTERY_H_MS = 4 * 3600 * 1000


def agreguj_4h(bary_1h: list) -> list:
    """Agreguje bary 1H w 4H po siatce UTC. Zwraca tylko KOMPLETNE okna (4/4)."""
    grupy = {}
    for b in bary_1h:
        klucz = (b["timestamp"] // CZTERY_H_MS) * CZTERY_H_MS
        grupy.setdefault(klucz, []).append(b)
    wynik = []
    for klucz in sorted(grupy):
        g = sorted(grupy[klucz], key=lambda x: x["timestamp"])
        if len(g) != 4:
            continue  # luka lub końcówka — odrzucamy niepełne okno
        wynik.append({
            "timestamp": klucz,
            "open": g[0]["open"],
            "high": max(x["high"] for x in g),
            "low": min(x["low"] for x in g),
            "close": g[-1]["close"],
            "volume": sum(x["volume"] for x in g),
        })
    return wynik


def main():
    root = os.path.join(os.path.dirname(__file__), "..")
    os.makedirs(os.path.join(root, "dane", "4h"), exist_ok=True)
    for sciezka in sorted(glob.glob(os.path.join(root, "dane", "godzinowe",
                                                 "Binance_*_1h.csv"))):
        para = os.path.basename(sciezka).replace("_1h.csv", "")
        bary = wczytaj_csv(sciezka, interwal="1H")
        b4 = agreguj_4h(bary)
        cel = os.path.join(root, "dane", "4h", f"{para}_4h.csv")
        with open(cel, "w", encoding="utf-8") as f:
            f.write("timestamp,open,high,low,close,volume\n")
            for b in b4:
                f.write(f"{b['timestamp']},{b['open']},{b['high']},"
                        f"{b['low']},{b['close']},{b['volume']}\n")
        print(f"{para}: {len(bary)} × 1H → {len(b4)} × 4H "
              f"(odrzucone niepełne: {len(bary)//4 - len(b4) + 1})")


if __name__ == "__main__":
    main()
