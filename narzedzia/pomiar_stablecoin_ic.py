"""
🏛️ AERARIUM — pomiar IC podaży stablecoinów (Prawo I + XXIV). Walidacja Tier-1 alt-danych.

Rzymskie *aerarium* = skarbiec państwa (rezerwa). Tu: podaż stablecoinów (USDT/USDC/...) =
„skarbiec rynku" / suchy proch. Hipoteza (zwiad 2026-07-15): świeży druk stablecoinów =
kapitał wchodzi → presja popytu → bullish dla BTC. Mierzymy, nie zakładamy (pomiar-najpierw,
ZASADA WPIĘCIA — nic nie wchodzi w ścieżkę decyzyjną bez dowodu IC).

Sygnał = N-dniowa % ZMIANA total stablecoin supply (DefiLlama, DARMOWE, bez klucza). Poziom
trenduje (niestacjonarny) → używamy DELTY (stacjonarnej = flow mennicy/umorzeń). IC =
Spearman(delta_supply_t, zwrot_BTC_{t→t+h}). Wyrównanie KAUZALNE (supply z dnia ≤ bar).

Źródło: https://stablecoins.llama.fi/stablecoincharts/all (bez klucza, ~3150 dni historii).
BTC dzienne: lokalny CSV (dane/dzienne) — długa historia = mocna statystyka.

Wynik walidacji (BTC 1d, 2026-07-15): IC dodatni rosnący z horyzontem — h=7 +0.055,
h=14 +0.104, h=30 +0.085 (nienakładające). Sygnał makro/flow (tygodnie-miesiąc).

Uruchom:  python narzedzia/pomiar_stablecoin_ic.py
Opcje:    --csv dane/dzienne/Binance_BTCUSDT_d.csv  --delta 7  --horyzonty 1 7 14 30  --arena
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

URL_STABLECOINS = "https://stablecoins.llama.fi/stablecoincharts/all"
MIN_PAR = 30
PROG_SKILL = 0.03


def _pasek(i, n, opis):
    print(f"\r[{i}/{n}] {opis:<40}", end="", file=sys.stderr, flush=True)
    if i == n:
        print("", file=sys.stderr, flush=True)


def _dzien(ts) -> str:
    ts = int(ts)
    if ts > 1e12:
        ts //= 1000
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _pobierz_supply(timeout: int = 20) -> dict:
    """Zwraca {dzień 'YYYY-MM-DD': total_stablecoin_supply_USD}. Bez klucza."""
    raw = json.loads(urllib.request.urlopen(URL_STABLECOINS, timeout=timeout).read())
    out = {}
    for r in raw:
        v = r.get("totalCirculatingUSD", {}).get("peggedUSD")
        if v:
            out[_dzien(r["date"])] = float(v)
    return out


def _sygnal_delta(dni, supply, delta_dni):
    """N-dniowa % zmiana supply, wyrównana kauzalnie do dnia baru (supply z dnia ≤ bar)."""
    sorted_days = sorted(supply)
    sup_ts = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
              for d in sorted_days]

    def supply_w(dstr):
        t = datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
        i = bisect.bisect_right(sup_ts, t) - 1
        return supply[sorted_days[i]] if i >= 0 else None

    sig = []
    for d in dni:
        s_now = supply_w(d)
        d_prev = (datetime.strptime(d, "%Y-%m-%d") - timedelta(days=delta_dni)).strftime("%Y-%m-%d")
        s_prev = supply_w(d_prev)
        sig.append((s_now / s_prev - 1.0) if (s_now and s_prev and s_prev > 0) else None)
    return sig


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
    p = argparse.ArgumentParser(description="AERARIUM — IC podaży stablecoinów (Tier-1, Prawo I).")
    p.add_argument("--csv", default="dane/dzienne/Binance_BTCUSDT_d.csv",
                   help="ścieżka do dziennego CSV OHLCV (długa historia)")
    p.add_argument("--delta", type=int, default=7, help="okno %% zmiany supply w dniach")
    p.add_argument("--horyzonty", nargs="+", type=int, default=[1, 7, 14, 30])
    p.add_argument("--arena", action="store_true",
                   help="zapisz IC do arena_wyniki.db (rodzaj=WALIDACJA_STABLECOIN)")
    p.add_argument("--ledger", action="store_true",
                   help="dopisz skill-IC do rejestr_testow.jsonl (CODEX, idempotentnie)")
    a = p.parse_args(argv)

    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    logging.disable(logging.WARNING)
    from imperium.akwedukty.czytnik_csv import wczytaj_csv

    print(f"🏛️ AERARIUM — IC podaży stablecoinów (Tier-1). Delta {a.delta}d, "
          f"horyzonty {a.horyzonty}. Pomiar-najpierw (Prawo I).\n")

    _pasek(1, 3, "pobieram supply (DefiLlama)")
    supply = _pobierz_supply()
    _pasek(2, 3, f"wczytuję BTC ({os.path.basename(a.csv)})")
    bary = wczytaj_csv(a.csv, interwal="1d")
    _pasek(3, 3, "liczę sygnał + IC")

    if not supply or not bary:
        print("❌ Brak danych (supply lub CSV) — pomiar niemożliwy (Prawo I).")
        return 1

    dni = [_dzien(b["timestamp"]) for b in bary]
    closes = [b["close"] for b in bary]
    sig = _sygnal_delta(dni, supply, a.delta)
    pokrycie = sum(1 for s in sig if s is not None)

    print(f" supply: {len(supply)} dni ({min(supply)}→{max(supply)}), "
          f"teraz={max(supply.values())/1e9:.1f}B")
    print(f" BTC: {len(bary)} barów, pokrycie sygnału {pokrycie}/{len(bary)}\n")

    def zwr_fwd(h):
        return [(closes[i + h] / closes[i] - 1.0) if i + h < len(closes) else None
                for i in range(len(closes))]

    print(f"{'horyzont':>9} | {'IC nienakł (n)':>18} | {'IC nakł (n)':>16} | znak")
    print("-" * 62)
    wiersze_arena = []
    wiersze_ledger = []
    skille = 0
    for h in a.horyzonty:
        zwr = zwr_fwd(h)
        ic_nn, n_nn = _ic(sig, zwr, krok=h)
        ic_ov, n_ov = _ic(sig, zwr, krok=1)
        f = lambda v: f"{v:+.4f}" if v is not None else "  n/a "
        if ic_nn is not None:
            znak = "DODATNI (bullish)" if ic_nn > 0 else "UJEMNY (bearish)"
            if abs(ic_nn) > PROG_SKILL:
                skille += 1
                znak += " ✅"
                wiersze_ledger.append((h, float(ic_nn), znak))
            wiersze_arena.append(("WALIDACJA_STABLECOIN", f"STABLECOIN_DELTA{a.delta}_IC_h{h}",
                                  float(ic_nn), f"BTC 1d n={n_nn} nn"))
        else:
            znak = ""
        print(f"{('h='+str(h)):>9} | {f(ic_nn):>10} ({n_nn:>5}) | {f(ic_ov):>8} ({n_ov:>5}) | {znak}")

    print("-" * 62)
    print(f" |IC|>{PROG_SKILL} = skill ({skille}/{len(a.horyzonty)} horyzontów). "
          f"Delta stacjonarna → bez spurious trendu. Nienakładające = uczciwe.")

    if a.arena and wiersze_arena:
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        z = zapisz_pomiary(wiersze_arena)
        print(f" 💾 Arena: zapisano {z} pomiarów (rodzaj=WALIDACJA_STABLECOIN).")
    if a.ledger:
        from narzedzia.scriba_codex import zapisz_ic
        d = sum(zapisz_ic(sygnal="STABLECOIN", neuron="K-03", horyzont=f"{h}d", ic=ic,
                          tryb="nienakladajace", prog=PROG_SKILL, werdykt="SKILL",
                          kierunek=znak.replace(" ✅", ""), zrodlo="pomiar_stablecoin_ic.py",
                          uwaga=f"delta{a.delta}d supply") for h, ic, znak in wiersze_ledger)
        print(f" 🖋️ Ledger: {d}/{len(wiersze_ledger)} skill-IC dopisanych → CODEX")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
