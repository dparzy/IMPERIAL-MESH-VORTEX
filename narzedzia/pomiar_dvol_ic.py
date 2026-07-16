"""
😱 PAVOR — pomiar IC indeksu strachu DVOL (Prawo I + XXIV). Walidacja Tier-1 alt-danych.

Rzymski *Pavor* = bóstwo strachu/paniki (towarzysz Marsa). Tu: DVOL = indeks zmienności
implikowanej opcji BTC/ETH (Deribit) = „crypto VIX", miernik strachu rynku. Zwiad 2026-07-15
wskazał opcje jako niewykorzystaną warstwę derywatów. Mierzymy IC dwóch sygnałów:

  1. POZIOM DVOL — hipoteza (Sinclair/VIX): wysoki strach = kontrariański bullish (kup strach).
     IC = Spearman(DVOL_t, zwrot_BTC_{t→t+h}) — oczekiwany DODATNI.
  2. DELTA DVOL (7d %) — hipoteza: narastanie strachu = bearish momentum. Oczekiwany UJEMNY.

Źródło: Deribit public API `get_volatility_index_data` (DARMOWE, bez klucza, resolution 1D).
BTC dzienne: lokalny CSV. Wyrównanie KAUZALNE (DVOL z dnia ≤ bar).

⚠️ ZASTRZEŻENIE: endpoint zwraca ~16 mies. historii (jeden reżim rynkowy) — walidacja WSTĘPNA.
Wynik potwierdzać na dłuższej historii, gdy dostępna. Wpięcie = opt-in OFF, dopiero po A/B.

Wynik (BTC 1d, 2026-07-15): poziom IC +0.10 @7d (bullish, spójny nn/ov); delta IC -0.11 @7d
(bearish, spójny nn/ov) — oba SKILL na horyzoncie tygodniowym.

Uruchom:  python narzedzia/pomiar_dvol_ic.py
Opcje:    --waluta BTC  --csv dane/dzienne/Binance_BTCUSDT_d.csv  --horyzonty 1 7 14  --arena
"""
import argparse
import bisect
import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

URL_DVOL = ("https://www.deribit.com/api/v2/public/get_volatility_index_data"
            "?currency={cur}&start_timestamp={start}&end_timestamp={end}&resolution=1D")
MIN_PAR = 30
PROG_SKILL = 0.03
DELTA_DNI = 7


def _pasek(i, n, opis):
    print(f"\r[{i}/{n}] {opis:<40}", end="", file=sys.stderr, flush=True)
    if i == n:
        print("", file=sys.stderr, flush=True)


def _dzien(ts) -> str:
    ts = int(ts)
    return datetime.fromtimestamp((ts / 1000) if ts > 1e12 else ts,
                                  tz=timezone.utc).strftime("%Y-%m-%d")


def _pobierz_dvol(waluta: str, dni_wstecz: int = 700, timeout: int = 20) -> dict:
    """Zwraca {dzień: DVOL_close}. Deribit public, bez klucza."""
    end = int(time.time() * 1000)
    start = end - dni_wstecz * 86400 * 1000
    url = URL_DVOL.format(cur=waluta.upper(), start=start, end=end)
    r = json.loads(urllib.request.urlopen(url, timeout=timeout).read())
    data = r.get("result", {}).get("data", [])
    return {_dzien(x[0]): float(x[4]) for x in data if x[4]}   # [ts,open,high,low,close]


def _wyrownaj(dni, seria: dict):
    """Kauzalny forward-fill wartości dziennej do dni barów (wartość z dnia ≤ bar)."""
    sd = sorted(seria)
    sts = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() for d in sd]

    def w(dstr):
        t = datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
        i = bisect.bisect_right(sts, t) - 1
        return seria[sd[i]] if i >= 0 else None
    return w


def _ic(sig, zwr, krok):
    import numpy as np
    from imperium.legiony.metryki_ic import _spearman
    pary = [(sig[i], zwr[i]) for i in range(0, len(sig), krok)
            if sig[i] is not None and zwr[i] is not None]
    if len(pary) < MIN_PAR:
        return None, len(pary)
    x = np.array([p[0] for p in pary], dtype=float)
    y = np.array([p[1] for p in pary], dtype=float)
    if np.std(x) < 1e-12:
        return None, len(pary)
    return _spearman(x, y), len(pary)


def main(argv=None):
    p = argparse.ArgumentParser(description="PAVOR — IC indeksu strachu DVOL (Tier-1, Prawo I).")
    p.add_argument("--waluta", default="BTC")
    p.add_argument("--csv", default="dane/dzienne/Binance_BTCUSDT_d.csv")
    p.add_argument("--horyzonty", nargs="+", type=int, default=[1, 7, 14])
    p.add_argument("--arena", action="store_true",
                   help="zapisz IC do arena_wyniki.db (rodzaj=WALIDACJA_DVOL)")
    a = p.parse_args(argv)

    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    logging.disable(logging.WARNING)
    from imperium.akwedukty.czytnik_csv import wczytaj_csv

    print(f"😱 PAVOR — IC indeksu strachu DVOL ({a.waluta}, Tier-1). "
          f"Horyzonty {a.horyzonty}. Pomiar-najpierw (Prawo I).\n")

    _pasek(1, 3, f"pobieram DVOL {a.waluta} (Deribit)")
    dvol = _pobierz_dvol(a.waluta)
    _pasek(2, 3, "wczytuję BTC")
    bary = wczytaj_csv(a.csv, interwal="1d")
    _pasek(3, 3, "liczę IC")

    if not dvol or not bary:
        print("❌ Brak danych (DVOL lub CSV) — pomiar niemożliwy (Prawo I).")
        return 1

    dni = [_dzien(b["timestamp"]) for b in bary]
    closes = [b["close"] for b in bary]
    w = _wyrownaj(dni, dvol)
    poziom = [w(d) for d in dni]
    delta = []
    for d in dni:
        n = w(d)
        pv = w((datetime.strptime(d, "%Y-%m-%d") - timedelta(days=DELTA_DNI)).strftime("%Y-%m-%d"))
        delta.append((n / pv - 1.0) if (n and pv and pv > 0) else None)

    pokr = sum(1 for x in poziom if x is not None)
    print(f" DVOL: {len(dvol)} dni ({min(dvol)}→{max(dvol)}) | pokrycie {pokr}/{len(bary)}")
    print(" ⚠️ Historia ~16 mies. (jeden reżim) — walidacja WSTĘPNA.\n")

    def zwr_fwd(h):
        return [(closes[i + h] / closes[i] - 1.0) if i + h < len(closes) else None
                for i in range(len(closes))]

    wiersze_arena = []
    for nazwa, sygnal, oczek in [("DVOL_POZIOM", poziom, "+bullish"),
                                 ("DVOL_DELTA7", delta, "-bearish")]:
        print(f" {nazwa} (oczek. {oczek}) → IC zwroty BTC:")
        for h in a.horyzonty:
            zwr = zwr_fwd(h)
            ic_nn, n_nn = _ic(sygnal, zwr, krok=h)
            ic_ov, n_ov = _ic(sygnal, zwr, krok=1)
            f = lambda v: f"{v:+.4f}" if v is not None else "  n/a "
            skill = ""
            if ic_nn is not None and ic_ov is not None and abs(ic_nn) > PROG_SKILL \
                    and (ic_nn > 0) == (ic_ov > 0) and abs(ic_ov) > PROG_SKILL:
                skill = " ✅ (spójny)"
                wiersze_arena.append(("WALIDACJA_DVOL", f"{nazwa}_IC_h{h}", float(ic_nn),
                                      f"{a.waluta} 1d n={n_nn} nn"))
            print(f"   h={h:>2}: nienakł {f(ic_nn)} (n={n_nn:>4})  nakł {f(ic_ov)} (n={n_ov:>4}){skill}")
        print()

    print(f" |IC|>{PROG_SKILL} + zgodny znak nn/ov = skill. Poziom=kontrariański, delta=momentum.")
    if a.arena and wiersze_arena:
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        z = zapisz_pomiary(wiersze_arena)
        print(f" 💾 Arena: zapisano {z} pomiarów (rodzaj=WALIDACJA_DVOL).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
