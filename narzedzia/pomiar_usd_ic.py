"""
🪙 MONETA — walidacja Tier-1: siła USD (DXY-proxy) vs zwroty BTC (Prawo I + XXIV).

Rzymska *Moneta* = bogini mennicy (świątynia, gdzie bito monety; źródłosłów „money").
Tu: siła dolara = miara światowego fiata prącego na krypto. Zwiad 2026-07-15 (plik źródeł)
wskazał Frankfurter jako darmowe FX bez klucza — makro OD RAZU, bez czekania na FRED.

Indeks siły USD = geom. średnia (USD/EUR × USD/JPY × USD/GBP) znormalizowana do bazy
(EUR/JPY/GBP to ~83% koszyka DXY). Źródło: Frankfurter API (frankfurter.app, DARMOWE,
bez klucza, FX od 2019+; wymaga User-Agent). BTC dzienne: lokalny CSV. Wyrównanie KAUZALNE.

Hipoteza (makro, BTC-DXY inverse): silny USD = odpływ z ryzyka = bearish BTC → IC UJEMNY.
Mierzymy POZIOM (siła) i DELTĘ (zmiana). Wynik (2026-07-15): poziom IC -0.05@7d → -0.11@30d
[SKILL, spójny nn/ov, rośnie z horyzontem]; delta = szum. Poziom = realny dryf makro.

⚠️ Poziom jest persystentny — nn potwierdza ov (nie sam artefakt trendu), a efekt rośnie
monotonicznie z horyzontem (zgodne z makro-dryfem). Wpięcie = opt-in OFF, po A/B.

Uruchom:  python narzedzia/pomiar_usd_ic.py
Opcje:    --od 2019-01-01  --csv dane/dzienne/Binance_BTCUSDT_d.csv  --horyzonty 7 14 30  --arena
"""
import argparse
import bisect
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

URL_FX = "https://api.frankfurter.app/{od}..{do}?base=USD&symbols=EUR,JPY,GBP"
UA = {"User-Agent": "Mozilla/5.0"}
MIN_PAR = 30
PROG_SKILL = 0.03
DELTA_DNI = 7


def _pasek(i, n, opis):
    print(f"\r[{i}/{n}] {opis:<40}", end="", file=sys.stderr, flush=True)
    if i == n:
        print("", file=sys.stderr, flush=True)


def _dzien(ts):
    ts = int(ts)
    return datetime.fromtimestamp((ts / 1000) if ts > 1e12 else ts,
                                  tz=timezone.utc).strftime("%Y-%m-%d")


def _indeks_usd(od: str, do: str, timeout: int = 25) -> dict:
    """Zwraca {dzień: siła_USD} — geom. średnia USD/EUR×USD/JPY×USD/GBP znorm. do bazy."""
    import numpy as np
    url = URL_FX.format(od=od, do=do)
    r = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                          timeout=timeout).read())["rates"]
    days = sorted(r)
    if not days:
        return {}
    base = r[days[0]]
    out = {}
    for day in days:
        v = r[day]
        if all(k in v and k in base and base[k] for k in ("EUR", "JPY", "GBP")):
            out[day] = float(np.cbrt((v["EUR"] / base["EUR"]) *
                                     (v["JPY"] / base["JPY"]) *
                                     (v["GBP"] / base["GBP"])))
    return out


def _wyrownaj(dni, seria: dict):
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
    p = argparse.ArgumentParser(description="MONETA — IC siły USD vs BTC (Tier-1, Prawo I).")
    p.add_argument("--od", default="2019-01-01")
    p.add_argument("--csv", default="dane/dzienne/Binance_BTCUSDT_d.csv")
    p.add_argument("--horyzonty", nargs="+", type=int, default=[7, 14, 30])
    p.add_argument("--arena", action="store_true",
                   help="zapisz IC do arena_wyniki.db (rodzaj=WALIDACJA_USD)")
    a = p.parse_args(argv)

    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    logging.disable(logging.WARNING)
    from imperium.akwedukty.czytnik_csv import wczytaj_csv

    print(f"🪙 MONETA — IC siły USD (DXY-proxy) vs BTC. Horyzonty {a.horyzonty}. "
          f"Pomiar-najpierw (Prawo I).\n")

    _pasek(1, 3, "pobieram FX (Frankfurter)")
    do = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    usd = _indeks_usd(a.od, do)
    _pasek(2, 3, "wczytuję BTC")
    bary = wczytaj_csv(a.csv, interwal="1d")
    _pasek(3, 3, "liczę IC")

    if not usd or not bary:
        print("❌ Brak danych (FX lub CSV) — pomiar niemożliwy (Prawo I).")
        return 1

    dni = [_dzien(b["timestamp"]) for b in bary]
    closes = [b["close"] for b in bary]
    w = _wyrownaj(dni, usd)
    poziom = [w(d) for d in dni]
    delta = []
    for d in dni:
        n = w(d)
        pv = w((datetime.strptime(d, "%Y-%m-%d") - timedelta(days=DELTA_DNI)).strftime("%Y-%m-%d"))
        delta.append((n / pv - 1.0) if (n and pv and pv > 0) else None)

    pokr = sum(1 for x in poziom if x is not None)
    print(f" USD-koszyk (EUR+JPY+GBP): {len(usd)} dni | pokrycie {pokr}/{len(bary)}\n")

    def zwr_fwd(h):
        return [(closes[i + h] / closes[i] - 1.0) if i + h < len(closes) else None
                for i in range(len(closes))]

    wiersze_arena = []
    for nazwa, sygnal, oczek in [("USD_POZIOM", poziom, "- bearish BTC"),
                                 ("USD_DELTA7", delta, "- bearish")]:
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
                wiersze_arena.append(("WALIDACJA_USD", f"{nazwa}_IC_h{h}", float(ic_nn),
                                      f"1d n={n_nn} nn koszyk_EUR_JPY_GBP"))
            print(f"   h={h:>2}: nienakł {f(ic_nn)} (n={n_nn:>4})  nakł {f(ic_ov)} (n={n_ov:>4}){skill}")
        print()

    print(f" |IC|>{PROG_SKILL} + zgodny znak nn/ov = skill. Poziom=makro-dryf (rośnie z horyzontem).")
    if a.arena and wiersze_arena:
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        z = zapisz_pomiary(wiersze_arena)
        print(f" 💾 Arena: zapisano {z} pomiarów (rodzaj=WALIDACJA_USD).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
