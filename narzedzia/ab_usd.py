"""
🪙 A/B USD (K-04 MONETA) — czy IC -0.27@30d przekłada się na PnL? (Prawo I)

Ostatnie ogniwo ZASADY WPIĘCIA dla K-04 (wzór ab_stablecoin). Portfel z USD_ZSCORE
WŁĄCZONYM (sentyment_per wstrzykuje z-score siły USD → K-04 głosuje) vs WYŁĄCZONYM.
Sygnał GLOBALNY (makro) → ta sama wartość dla każdego symbolu. Z-score liczony na
oknie 120d, kauzalnie (USD≤bar). Koszyk 5 par dzienny.

Uruchom: python narzedzia/ab_usd.py
"""
import bisect
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.disable(logging.CRITICAL)

import numpy as np                                              # noqa: E402
from imperium.koloseum.backtest import backtest_portfel        # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv          # noqa: E402

PLIKI = {
    "BTCUSDT": "dane/dzienne/Binance_BTCUSDT_d.csv",
    "ETHUSDT": "dane/dzienne/Binance_ETHUSDT_d.csv",
    "SOLUSDT": "dane/dzienne/Binance_SOLUSDT_d.csv",
    "BNBUSDT": "dane/dzienne/Binance_BNBUSDT_d.csv",
    "DOGEUSDT": "dane/dzienne/Binance_DOGEUSDT_d.csv",
}
BAZA = dict(tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True)
OKNO = 120
URL = "https://api.frankfurter.app/2019-01-01..{do}?base=USD&symbols=EUR,JPY,GBP"


def _dzien(ts):
    ts = int(ts)
    return datetime.fromtimestamp((ts / 1000) if ts > 1e12 else ts,
                                  tz=timezone.utc).strftime("%Y-%m-%d")


def _usd_zscore_series():
    """{dzień: z-score siły USD na oknie 120d} — kauzalnie."""
    do = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    r = json.loads(urllib.request.urlopen(urllib.request.Request(
        URL.format(do=do), headers={"User-Agent": "IMV/1.0"}), timeout=25).read())["rates"]
    days = sorted(r)
    base = r[days[0]]
    idx = {}
    for dd in days:
        v = r[dd]
        if all(k in v and k in base and base[k] for k in ("EUR", "JPY", "GBP")):
            idx[dd] = float(np.cbrt((v["EUR"] / base["EUR"]) *
                                    (v["JPY"] / base["JPY"]) * (v["GBP"] / base["GBP"])))
    sd = sorted(idx)
    vals = [idx[x] for x in sd]
    out = {}
    for i in range(OKNO, len(sd)):
        w = vals[i - OKNO:i]
        s = np.std(w)
        if s > 1e-9:
            out[sd[i]] = float((vals[i] - np.mean(w)) / s)
    return out


def _sentyment(bary_per, zser):
    sd = sorted(zser)
    sts = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() for d in sd]
    out = {}
    for sym, bary in bary_per.items():
        m = {}
        for b in bary:
            t = datetime.strptime(_dzien(b["timestamp"]), "%Y-%m-%d").replace(
                tzinfo=timezone.utc).timestamp()
            i = bisect.bisect_right(sts, t) - 1
            if i >= 0:
                m[int(b["timestamp"])] = {"USD_ZSCORE": zser[sd[i]]}
        out[sym] = m
    return out


def zmierz(bary_per, sentyment_per):
    eng = backtest_portfel(PLIKI, "1d", bary_per={k: list(v) for k, v in bary_per.items()},
                           sentyment_per=sentyment_per, **BAZA)
    s = eng.podsumowanie()
    return (s.kapital_koncowy / s.kapital_startowy - 1) * 100, s.max_drawdown_pct, s.total_trades


def main():
    print("🪙 A/B USD (K-04) — czy IC -0.27@30d daje PnL? 5 par dzienny.\n", flush=True)
    print("[1/3] Frankfurter + z-score 120d...", file=sys.stderr, flush=True)
    zser = _usd_zscore_series()
    if not zser:
        print("❌ Brak danych FX.")
        return 1
    bary = {sym: wczytaj_csv(sc, interwal="1d") for sym, sc in PLIKI.items()}
    sent = _sentyment(bary, zser)
    print(f"[2/3] Bieg B (USD OFF), {len(bary['BTCUSDT'])} barów...", file=sys.stderr, flush=True)
    roi_b, dd_b, tr_b = zmierz(bary, None)
    print("[3/3] Bieg A (USD ON)...", file=sys.stderr, flush=True)
    roi_a, dd_a, tr_a = zmierz(bary, sent)

    print("=" * 66)
    print(" A/B USD — PnL w pełnym roju (5 par, dzienny)")
    print("=" * 66)
    print(f" {'wariant':24} {'ROI%':>8} {'maxDD%':>8} {'trades':>7}")
    print(f" {'B: USD OFF (baseline)':24} {roi_b:>8.2f} {dd_b:>8.2f} {tr_b:>7}")
    print(f" {'A: USD ON (K-04)':24} {roi_a:>8.2f} {dd_a:>8.2f} {tr_a:>7}")
    print("-" * 66)
    d_roi = roi_a - roi_b
    print(f" Δ ROI = {d_roi:+.2f} pp | Δ maxDD = {dd_a - dd_b:+.2f} pp | Δ trades = {tr_a - tr_b:+d}")
    if d_roi > 0.5 and dd_a <= dd_b + 1.0:
        werdykt = "✅ USD POMAGA — kandydat do włączenia (decyzja Cezara)"
    elif d_roi < -0.5:
        werdykt = "❌ SZKODZI — zostaw opt-in OFF"
    else:
        werdykt = "⚖️ NEUTRALNE — zostaw OFF, więcej danych"
    print(f" WERDYKT: {werdykt}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
