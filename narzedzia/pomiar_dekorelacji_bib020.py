"""
📊 Pomiar dekorelacji wizji BIB-020 (Prawo XVI — spłata długu „do zmierzenia").

Mierzy |korelacja| Pearsona między NOWYMI głosami z biblii Harrisa (Z-03, Z-04,
X-27 oraz wskaźniki master-switcha VARIANCE_RATIO/OU_HALFLIFE) a istniejącymi
głosami, które flagowaliśmy jako możliwe nakładki:

  • Z-03 (bubble_z/VoV/AR1)         vs  Z-01 VPIN
  • Z-04 (CASCADE/DEAD-CAT)         vs  Z-03, Z-01
  • X-27 (Value-Z/MoMA-Z)           vs  X-04 BBands, X-01 RSI
  • VARIANCE_RATIO / OU_HALFLIFE    vs  RET_AR1, HURST_DFA  (wskaźniki, nie neurony)

Prawo XVI:
  |r| > 0.80 → redundancja (kandydat do scalenia / wagi w dół)
  |r| < 0.20 → filar siły (zachować, dywersyfikuje)
  zerowa wariancja → martwy głos (czerwony alarm Prawa XV)

To NARZĘDZIE POMIAROWE (read-only) — nie zmienia kodu, tylko raportuje dla Cezara.
Uruchom: python narzedzia/pomiar_dekorelacji_bib020.py [ścieżka_csv] [limit_barów]
"""

import sys
import os
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.akwedukty.czytnik_csv import wczytaj_csv
from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow
from imperium.legiony.diagnostyka_korelacji import korelacja_pearson

# Neurony do zmierzenia + ich podejrzane nakładki
from imperium.legiony.neurony.zagrozenie import (
    NeuronToxicFlow, NeuronBubbleCrash, NeuronCascade,
)
from imperium.legiony.neurony.momentum import (
    NeuronValueConvergence, NeuronBBands, NeuronRSI,
)

DOMYSLNY_CSV = "dane/godzinowe/Binance_BTCUSDT_1h.csv"


def sygnal_na_liczbe(s) -> float:
    """
    Głos → liczba na osi [-1, +1].
    LONG=+pewność, SHORT=−pewność. Dla meta-bram (NEUTRAL z pewnosc_przeciwnika)
    bierzemy −przeciwnik (siła tłumienia jako sygnał obronny).
    """
    if s.kierunek == "LONG":
        return float(s.pewnosc)
    if s.kierunek == "SHORT":
        return -float(s.pewnosc)
    # NEUTRAL — meta-brama wyraża się przez pewnosc_przeciwnika
    return -float(getattr(s, "pewnosc_przeciwnika", 0.0))


def zbierz_serie_neuronow(bary: List[Dict[str, Any]], neurony: list,
                          okno: int = 220, krok: int = 4) -> Dict[str, List[float]]:
    """Przesuwa okno po barach, buduje wskaźniki przez Bramę, zbiera głos każdego neuronu."""
    bud = BudowniczyWskaznikow()
    serie: Dict[str, List[float]] = {n.KLUCZ: [] for n in neurony}
    if len(bary) < okno:
        return serie
    for koniec in range(okno, len(bary) + 1, krok):
        wycinek = bary[koniec - okno:koniec]
        wskazniki = bud.zbuduj(wycinek)
        for n in neurony:
            try:
                s = n.interpretuj(wskazniki)
                serie[n.KLUCZ].append(sygnal_na_liczbe(s))
            except Exception:
                serie[n.KLUCZ].append(0.0)
    return serie


def zbierz_serie_wskaznikow(bary: List[Dict[str, Any]], klucze: List[str],
                            okno: int = 220, krok: int = 4) -> Dict[str, List[float]]:
    """Zbiera surowe wartości wskaźników Bramy (dla par wskaźnik-wskaźnik)."""
    bud = BudowniczyWskaznikow()
    serie: Dict[str, List[float]] = {k: [] for k in klucze}
    if len(bary) < okno:
        return serie
    for koniec in range(okno, len(bary) + 1, krok):
        wycinek = bary[koniec - okno:koniec]
        wskazniki = bud.zbuduj(wycinek)
        for k in klucze:
            v = wskazniki.get(k)
            serie[k].append(float(v) if v is not None else 0.0)
    return serie


def _ocena(r: Optional[float]) -> str:
    if r is None:
        return "BRAK (zerowa wariancja? — sprawdź martwy głos)"
    a = abs(r)
    if a > 0.80:
        return "🔴 REDUNDANCJA (|r|>0.80 — scalić / waga w dół)"
    if a < 0.20:
        return "🟢 FILAR (|r|<0.20 — dywersyfikuje, zachować)"
    return "🟡 OK (umiarkowana — niezależny sygnał)"


def main():
    sciezka = sys.argv[1] if len(sys.argv) > 1 else DOMYSLNY_CSV
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    print("📊 POMIAR DEKORELACJI BIB-020 (Prawo XVI)")
    print(f"   Dane: {sciezka} | ostatnie {limit} barów\n")

    bary = wczytaj_csv(sciezka, limit=limit)
    print(f"   Wczytano {len(bary)} barów.\n")

    # ── Pary neuron-neuron ──
    neurony = [NeuronToxicFlow(), NeuronBubbleCrash(), NeuronCascade(),
               NeuronValueConvergence(), NeuronBBands(), NeuronRSI()]
    serie_n = zbierz_serie_neuronow(bary, neurony)
    n_krokow = len(next(iter(serie_n.values()))) if serie_n else 0
    print(f"   Kroków pomiarowych: {n_krokow}\n")

    pary_neurony = [
        ("Z-03", "Z-01"),   # bubble/crash vs VPIN
        ("Z-04", "Z-03"),   # cascade vs bubble/crash
        ("Z-04", "Z-01"),   # cascade vs VPIN
        ("X-27", "X-04"),   # value convergence vs BBands
        ("X-27", "X-01"),   # value convergence vs RSI
    ]
    print("── PARY NEURON–NEURON ─────────────────────────────────────")
    for a, b in pary_neurony:
        r = korelacja_pearson(serie_n.get(a, []), serie_n.get(b, []))
        rs = f"{r:+.3f}" if r is not None else "None"
        print(f"  {a} ~ {b}:  r={rs}   {_ocena(r)}")

    # ── Pary wskaźnik-wskaźnik (master-switch) ──
    klucze_w = ["VARIANCE_RATIO_4", "OU_HALFLIFE_50", "RET_AR1_20", "HURST_DFA_100"]
    serie_w = zbierz_serie_wskaznikow(bary, klucze_w)
    pary_wsk = [
        ("VARIANCE_RATIO_4", "RET_AR1_20"),
        ("OU_HALFLIFE_50", "HURST_DFA_100"),
        ("VARIANCE_RATIO_4", "OU_HALFLIFE_50"),
    ]
    print("\n── PARY WSKAŹNIK–WSKAŹNIK (master-switch reżimu) ──────────")
    for a, b in pary_wsk:
        r = korelacja_pearson(serie_w.get(a, []), serie_w.get(b, []))
        rs = f"{r:+.3f}" if r is not None else "None"
        print(f"  {a} ~ {b}:  r={rs}   {_ocena(r)}")

    print("\n✅ Pomiar zakończony. |r|>0.80 → scalić; |r|<0.20 → filar; brak wariancji → alarm XV.")


if __name__ == "__main__":
    main()
