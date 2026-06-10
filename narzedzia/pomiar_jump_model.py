"""
📊 POMIAR JUMP MODEL (W-281) — tabela dowodowa przed Fazą 3 master-switcha.

Prawo XVIII: wpięcie JumpModel do klasyfikuj_rezim() TYLKO po pomiarze przewagi.
To narzędzie mierzy na realnych danych (BTC/ETH), bez look-ahead:

  1. PRZYCZYNOWY walk-forward: co KROK barów fitujemy JM na ostatnich OKNO
     barach; między refitami nowe bary klasyfikuje przypisz_ostatni()
     (najbliższy centroid). Stan baru t znamy w chwili t (bez przyszłości).
  2. MIARA PREDYKCYJNA: średni zwrot baru t+1 po stanie z baru t.
     Dobry detektor: BULL(t) → wyższy zwrot t+1 niż BEAR(t). Separacja
     BULL−BEAR w bps = twarda, ekonomiczna miara.
  3. TRWAŁOŚĆ: liczba zmian stanu / 100 barów (mniej = mniej kosztów przełączeń).
  4. BASELINE: ten sam pomiar dla reżimu ADX (TREND gdy ADX>25 i DI+>DI−=bull).

Uruchom:  python narzedzia/pomiar_jump_model.py
"""

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.legiony.jump_model import JumpModel  # noqa: E402

ZESTAWY = [
    ("BTC 1D", "dane/dzienne/Binance_BTCUSDT_d.csv"),
    ("ETH 1D", "dane/dzienne/Binance_ETHUSDT_d.csv"),
]
OKNO = 250          # bary historii do fitu
KROK = 20           # refit co tyle barów
KARA = 30.0         # λ jump-penalty
N_STANOW = 3


def wczytaj(plik):
    sciezka = os.path.join(os.path.dirname(__file__), "..", plik)
    bary = []
    with open(sciezka, encoding="utf-8") as f:
        # format CryptoDataDownload: 1. linia = URL, 2. = nagłówek
        pierwsza = f.readline()
        if "http" not in pierwsza.lower():
            f.seek(0)
        for row in csv.DictReader(f):
            klucze = {k.lower(): k for k in row}
            try:
                bary.append({
                    "unix": float(row[klucze.get("unix", "unix")]),
                    "close": float(row[klucze["close"]]),
                    "high": float(row[klucze["high"]]),
                    "low": float(row[klucze["low"]]),
                    "volume": float(row[
                        klucze.get("volume btc") or klucze.get("volume eth")
                        or klucze.get("volume usdt") or klucze["volume"]]),
                })
            except (ValueError, KeyError):
                continue
    # CryptoDataDownload daje od NAJNOWSZYCH — sortuj rosnąco po czasie (Prawo I)
    bary.sort(key=lambda b: b["unix"])
    return bary


def cechy_z_barow(bary):
    closes = np.array([b["close"] for b in bary])
    zwroty = np.diff(closes) / closes[:-1]
    vol20 = np.array([zwroty[max(0, i - 19):i + 1].std()
                      for i in range(len(zwroty))])
    return zwroty, np.column_stack([zwroty, vol20])


def adx_rezimy(bary, okres=14):
    """Baseline: ADX/DI z TA-Lib → +1 (trend bull), -1 (trend bear), 0 (ranging)."""
    import talib
    h = np.array([b["high"] for b in bary], dtype=float)
    lo = np.array([b["low"] for b in bary], dtype=float)
    c = np.array([b["close"] for b in bary], dtype=float)
    adx = talib.ADX(h, lo, c, timeperiod=okres)
    dip = talib.PLUS_DI(h, lo, c, timeperiod=okres)
    dim = talib.MINUS_DI(h, lo, c, timeperiod=okres)
    stany = np.zeros(len(c), dtype=int)
    silny = adx > 25
    stany[silny & (dip > dim)] = 1
    stany[silny & (dip <= dim)] = -1
    return stany[1:]  # wyrównanie do zwrotów


def pomiar_jm(zwroty, cechy):
    """Walk-forward stany JM: +1 BULL, -1 BEAR, 0 NEUTRAL (przyczynowo)."""
    t = len(zwroty)
    stany = np.zeros(t, dtype=int)
    jm = None
    nazwy = {}
    for i in range(OKNO, t):
        if (i - OKNO) % KROK == 0:
            jm = JumpModel(n_stanow=N_STANOW, kara_skoku=KARA,
                           n_startow=4, max_iter=20)
            s_hist = jm.dopasuj(cechy[i - OKNO:i])
            nazwy = jm.nazwij_stany(zwroty[i - OKNO:i], s_hist)
        k = jm.przypisz_ostatni(cechy[i])
        # stan bez wystąpień w historii fitu nie ma nazwy → traktuj jako NEUTRAL
        stany[i] = {"BULL": 1, "BEAR": -1, "NEUTRAL": 0}[nazwy.get(k, "NEUTRAL")]
    return stany


def separacja(stany, zwroty):
    """Średni zwrot t+1 po stanie t (bps) + liczba przełączeń/100 barów."""
    nast = zwroty[1:]
    s = stany[:-1]
    aktywne = s != 0
    wynik = {}
    for nazwa, wart in (("BULL", 1), ("BEAR", -1), ("NEUTRAL", 0)):
        maska = s == wart
        wynik[nazwa] = float(nast[maska].mean() * 1e4) if maska.any() else None
    przelaczenia = int((np.diff(stany[OKNO:]) != 0).sum())
    n_aktywnych = max(1, len(stany) - OKNO)
    wynik["przelaczen_na_100"] = round(100.0 * przelaczenia / n_aktywnych, 1)
    wynik["pokrycie_pct"] = round(100.0 * aktywne[OKNO:].mean(), 1)
    return wynik


def main():
    print("📊 POMIAR JUMP MODEL vs baseline ADX (zwrot t+1 po stanie t, bps)")
    print(f"   okno={OKNO}, refit co {KROK}, λ={KARA}, stany={N_STANOW}\n")
    for etykieta, plik in ZESTAWY:
        bary = wczytaj(plik)
        if len(bary) < OKNO + 100:
            print(f"{etykieta}: za mało barów ({len(bary)}) — pomijam")
            continue
        zwroty, cechy = cechy_z_barow(bary)
        jm_st = pomiar_jm(zwroty, cechy)
        jm_w = separacja(jm_st, zwroty)
        wiersz = (f"{etykieta} ({len(bary)} barów)\n"
                  f"  JUMP MODEL : BULL→{_f(jm_w['BULL'])} | BEAR→{_f(jm_w['BEAR'])} | "
                  f"NEUTRAL→{_f(jm_w['NEUTRAL'])} | sep(B−B)={_sep(jm_w)} bps | "
                  f"przełączeń/100={jm_w['przelaczen_na_100']}")
        try:
            adx_st = adx_rezimy(bary)
            adx_w = separacja(adx_st, zwroty)
            wiersz += (f"\n  ADX baseline: BULL→{_f(adx_w['BULL'])} | BEAR→{_f(adx_w['BEAR'])} | "
                       f"NEUTRAL→{_f(adx_w['NEUTRAL'])} | sep(B−B)={_sep(adx_w)} bps | "
                       f"przełączeń/100={adx_w['przelaczen_na_100']}")
        except ImportError:
            wiersz += "\n  ADX baseline: TA-Lib niedostępny — pominięty"
        print(wiersz + "\n")


def _f(x):
    return "—" if x is None else f"{x:+.1f}"


def _sep(w):
    if w["BULL"] is None or w["BEAR"] is None:
        return "—"
    return f"{w['BULL'] - w['BEAR']:+.1f}"


if __name__ == "__main__":
    main()
