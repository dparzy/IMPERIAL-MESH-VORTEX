"""
🏛️ A/B STABLECOIN (K-03) — czy IC +0.05..0.10 przekłada się na PnL? (Prawo I)

Ostatnie ogniwo ZASADY WPIĘCIA dla K-03 (wzór ab_dvol). Portfel z STABLE_FLOW WŁĄCZONYM
(sentyment_per wstrzykuje 7d deltę podaży → K-03 głosuje) vs WYŁĄCZONYM, to samo okno.
Sygnał GLOBALNY (podaż stablecoinów = cały rynek) → ta sama wartość dla każdego symbolu.

Koszyk 5 par dzienny (era DefiLlama = pełna historia). Wyrównanie KAUZALNE (supply≤bar).

Uruchom: python narzedzia/ab_stablecoin.py
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
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest_portfel        # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv          # noqa: E402

# Interwał opt-in (rozkaz Cezara 2026-07-16: A/B na 1H/4H). Etykieta „4H"/„1H" trafia do
# Namiestnika (profil stylu per interwał). --od tnie okno (pełna historia intraday × 5 par
# jest nierealna: 1H = ~76k barów/parę). Domyślnie 1d bez okna = zachowanie bez zmian.
INTERWALY = {"1d": ("dane/dzienne", "_d", "1d"),
             "4h": ("dane/4h", "_4h", "4H"),
             "1h": ("dane/godzinowe", "_1h", "1H")}
SYMBOLE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
LABEL = "1d"
OD_TS = None                          # dolna granica timestampu (ms) lub None = pełna historia
PLIKI = {s: f"dane/dzienne/Binance_{s}_d.csv" for s in SYMBOLE}
BAZA = dict(tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True)
DELTA_DNI = 7
URL = "https://stablecoins.llama.fi/stablecoincharts/all"


def _dzien(ts):
    ts = int(ts)
    return datetime.fromtimestamp((ts / 1000) if ts > 1e12 else ts,
                                  tz=timezone.utc).strftime("%Y-%m-%d")


def _delta_supply():
    """{dzień: 7d % zmiana podaży} — kauzalnie z historii DefiLlama."""
    raw = json.loads(urllib.request.urlopen(
        urllib.request.Request(URL, headers={"User-Agent": "IMV/1.0"}), timeout=25).read())
    supply = {}
    for r in raw:
        v = (r.get("totalCirculatingUSD") or {}).get("peggedUSD")
        if v:
            supply[_dzien(r["date"])] = float(v)
    sd = sorted(supply)
    sts = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() for d in sd]

    def w(dstr):
        t = datetime.strptime(dstr, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
        i = bisect.bisect_right(sts, t) - 1
        return supply[sd[i]] if i >= 0 else None
    out = {}
    for d in sd:
        teraz = w(d)
        wstecz = w((datetime.strptime(d, "%Y-%m-%d") - timedelta(days=DELTA_DNI)).strftime("%Y-%m-%d"))
        if teraz and wstecz and wstecz > 0:
            out[d] = teraz / wstecz - 1.0
    return out


def _sentyment(bary_per, delta):
    """{sym: {ts_baru: {STABLE_FLOW}}} — globalny sygnał, ten sam dla każdej pary."""
    sd = sorted(delta)
    sts = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() for d in sd]
    out = {}
    for sym, bary in bary_per.items():
        m = {}
        for b in bary:
            t = datetime.strptime(_dzien(b["timestamp"]), "%Y-%m-%d").replace(
                tzinfo=timezone.utc).timestamp()
            i = bisect.bisect_right(sts, t) - 1
            if i >= 0:
                m[int(b["timestamp"])] = {"STABLE_FLOW": delta[sd[i]]}
        out[sym] = m
    return out


def zmierz(bary_per, sentyment_per):
    eng = backtest_portfel(PLIKI, LABEL, bary_per={k: list(v) for k, v in bary_per.items()},
                           sentyment_per=sentyment_per, **BAZA)
    s = eng.podsumowanie()
    return (s.kapital_koncowy / s.kapital_startowy - 1) * 100, s.max_drawdown_pct, s.total_trades


def main():
    ap = argparse.ArgumentParser(description="A/B STABLECOIN (K-03) na wybranym interwale")
    ap.add_argument("--interwal", choices=list(INTERWALY), default="1d")
    ap.add_argument("--od", default=None, help="okno OD daty YYYY-MM-DD (intraday tnij, np. 2024-08-01)")
    ap.add_argument("--bary", type=int, default=None,
                    help="ogranicz do najnowszych N barów/symbol (backtest O(n²) — Prawo XV)")
    ap.add_argument("--ledger", action="store_true",
                    help="dopisz wynik A/B do rejestr_testow.jsonl (CODEX, idempotentnie)")
    args = ap.parse_args()
    global PLIKI, LABEL, OD_TS
    sub, suf, LABEL = INTERWALY[args.interwal]
    PLIKI = {s: f"{sub}/Binance_{s}{suf}.csv" for s in SYMBOLE}
    if args.od:
        OD_TS = int(datetime.strptime(args.od, "%Y-%m-%d")
                    .replace(tzinfo=timezone.utc).timestamp() * 1000)

    okno = f", okno od {args.od}" if args.od else ""
    print(f"🏛️ A/B STABLECOIN (K-03) — czy IC +0.05..0.10 daje PnL? 5 par {LABEL}{okno}.\n", flush=True)
    print("[1/3] DefiLlama + delta...", file=sys.stderr, flush=True)
    delta = _delta_supply()
    if not delta:
        print("❌ Brak danych DefiLlama.")
        return 1
    # Delta stablecoinów pokrywa ~całą historię BTC (od 2017-12) → używamy pełnych barów;
    # bary bez pokrycia delty (pierwsze dni) po prostu nie dostaną STABLE_FLOW (K-03 abstynuje).
    bary = {sym: wczytaj_csv(sc, interwal=LABEL) for sym, sc in PLIKI.items()}
    if OD_TS is not None:
        bary = {sym: [b for b in bs if int(b["timestamp"]) >= OD_TS] for sym, bs in bary.items()}
    if args.bary:
        bary = {sym: bs[-args.bary:] for sym, bs in bary.items()}
    sent = _sentyment(bary, delta)
    print(f"[2/3] Bieg B (STABLE OFF), {len(bary['BTCUSDT'])} barów...", file=sys.stderr, flush=True)
    roi_b, dd_b, tr_b = zmierz(bary, None)
    print("[3/3] Bieg A (STABLE ON)...", file=sys.stderr, flush=True)
    roi_a, dd_a, tr_a = zmierz(bary, sent)

    print("=" * 66)
    print(f" A/B STABLECOIN — PnL w pełnym roju (5 par, {LABEL})")
    print("=" * 66)
    print(f" {'wariant':24} {'ROI%':>8} {'maxDD%':>8} {'trades':>7}")
    print(f" {'B: STABLE OFF (baseline)':24} {roi_b:>8.2f} {dd_b:>8.2f} {tr_b:>7}")
    print(f" {'A: STABLE ON (K-03)':24} {roi_a:>8.2f} {dd_a:>8.2f} {tr_a:>7}")
    print("-" * 66)
    d_roi = roi_a - roi_b
    print(f" Δ ROI = {d_roi:+.2f} pp | Δ maxDD = {dd_a - dd_b:+.2f} pp | Δ trades = {tr_a - tr_b:+d}")
    if d_roi > 0.5 and dd_a <= dd_b + 1.0:
        werdykt = "✅ STABLECOIN POMAGA — kandydat do włączenia (decyzja Cezara)"
    elif d_roi < -0.5:
        werdykt = "❌ SZKODZI — zostaw opt-in OFF"
    else:
        werdykt = "⚖️ NEUTRALNE — zostaw OFF, więcej danych"
    print(f" WERDYKT: {werdykt}")
    print("=" * 66)
    if args.ledger:
        from narzedzia.scriba_codex import zapisz_ab
        krotki = ("POMAGA" if d_roi > 0.5 and dd_a <= dd_b + 1.0
                  else "SZKODZI" if d_roi < -0.5 else "NEUTRALNE")
        okno_b = len(bary["BTCUSDT"])   # faktyczna liczba barów (po przycięciu --bary/--od)
        dodano = zapisz_ab(sygnal="STABLECOIN", neuron="K-03", interwal=LABEL,
                           okno_barow=okno_b, roi_b=roi_b, roi_a=roi_a,
                           maxdd_delta=dd_a - dd_b, werdykt=krotki,
                           zrodlo=f"ab_stablecoin.py --interwal {args.interwal}"
                           + (f" --bary {args.bary}" if args.bary else ""),
                           uwaga="5 par")
        print(f" 🖋️ Ledger: {'dopisano' if dodano else 'bez zmian (identyczny rekord)'} → CODEX")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
