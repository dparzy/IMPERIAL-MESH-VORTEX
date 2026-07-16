"""
😱 A/B DVOL (PSY-05) — czy zwalidowany IC +0.16@7d przekłada się na realny PnL? (Prawo I)

Ostatnie ogniwo ZASADY WPIĘCIA: pomiar dał IC (skill predykcyjny), ale IC ≠ zysk.
Porównujemy portfel z DVOL WŁĄCZONYM (sentyment_per wstrzykuje DVOL_INDEX → PSY-05 głosuje)
vs WYŁĄCZONYM (brak DVOL → PSY-05 abstynuje) na TYM SAMYM oknie (era DVOL ~2024-08+).
Jeśli włączony ≤ wyłączony → DVOL nie pomaga w pełnym roju → NIE włączać na stałe.

Tylko BTC+ETH (Deribit DVOL istnieje dla obu). Interwał dzienny (walidacja była na 7d/daily).
Wyrównanie DVOL→bary KAUZALNE (reużyte z pomiar_dvol_ic / PAVOR).

Uruchom: python narzedzia/ab_dvol.py
"""
import logging
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest_portfel        # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv          # noqa: E402
from narzedzia.pomiar_dvol_ic import _pobierz_dvol, _dzien      # noqa: E402

PLIKI = {
    "BTCUSDT": "dane/dzienne/Binance_BTCUSDT_d.csv",
    "ETHUSDT": "dane/dzienne/Binance_ETHUSDT_d.csv",
}
WALUTA = {"BTCUSDT": "BTC", "ETHUSDT": "ETH"}
BAZA = dict(tryb_skaner=True, skaner_top_n=2, sizing_przekonania=True)


def _sentyment_dvol(bary_per):
    """{sym: {ts_baru: {DVOL_INDEX}}} — kauzalny forward-fill DVOL na bary."""
    import bisect
    out = {}
    for sym, bary in bary_per.items():
        dvol = _pobierz_dvol(WALUTA[sym], dni_wstecz=900)
        if not dvol:
            continue
        sd = sorted(dvol)
        sts = [datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() for d in sd]
        m = {}
        for b in bary:
            t = datetime.strptime(_dzien(b["timestamp"]), "%Y-%m-%d").replace(
                tzinfo=timezone.utc).timestamp()
            i = bisect.bisect_right(sts, t) - 1
            if i >= 0:
                m[int(b["timestamp"])] = {"DVOL_INDEX": dvol[sd[i]]}
        out[sym] = m
    return out


def _bary_era_dvol(sent):
    """Tnij bary do ery DVOL (pierwszy bar z pokryciem DVOL) — uczciwe A/B na tym samym oknie."""
    out = {}
    for sym, sc in PLIKI.items():
        b = wczytaj_csv(sc, interwal="1d")
        pokryte = sent.get(sym, {})
        if pokryte:
            pierwszy = min(pokryte)
            b = [x for x in b if int(x["timestamp"]) >= pierwszy]
        out[sym] = b
    return out


def zmierz(bary_per, sentyment_per):
    eng = backtest_portfel(PLIKI, "1d", bary_per={k: list(v) for k, v in bary_per.items()},
                           sentyment_per=sentyment_per, **BAZA)
    s = eng.podsumowanie()
    roi = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    return roi, s.max_drawdown_pct, s.total_trades


def main():
    print("😱 A/B DVOL (PSY-05) — czy IC +0.16@7d daje PnL? BTC+ETH dzienny, era DVOL.\n", flush=True)
    print("[1/3] pobieram DVOL + buduję sentyment...", file=sys.stderr, flush=True)
    # tymczasowe bary do zbudowania sentymentu (pełne), potem tniemy do ery DVOL
    bary_full = {s: wczytaj_csv(sc, interwal="1d") for s, sc in PLIKI.items()}
    sent = _sentyment_dvol(bary_full)
    if not sent:
        print("❌ Brak DVOL — A/B niemożliwe.")
        return 1
    bary = _bary_era_dvol(sent)
    n = {s: len(b) for s, b in bary.items()}
    print(f"[2/3] okno era-DVOL: {n} barów. Bieg B (DVOL OFF)...", file=sys.stderr, flush=True)
    roi_b, dd_b, tr_b = zmierz(bary, None)
    print("[3/3] Bieg A (DVOL ON)...", file=sys.stderr, flush=True)
    roi_a, dd_a, tr_a = zmierz(bary, sent)

    print("=" * 66)
    print(" A/B DVOL — PnL w pełnym roju (BTC+ETH, dzienny, era DVOL)")
    print("=" * 66)
    print(f" {'wariant':22} {'ROI%':>8} {'maxDD%':>8} {'trades':>7}")
    print(f" {'B: DVOL OFF (baseline)':22} {roi_b:>8.2f} {dd_b:>8.2f} {tr_b:>7}")
    print(f" {'A: DVOL ON (PSY-05)':22} {roi_a:>8.2f} {dd_a:>8.2f} {tr_a:>7}")
    print("-" * 66)
    d_roi = roi_a - roi_b
    print(f" Δ ROI = {d_roi:+.2f} pp | Δ maxDD = {dd_a - dd_b:+.2f} pp | Δ trades = {tr_a - tr_b:+d}")
    if d_roi > 0.5 and dd_a <= dd_b + 1.0:
        werdykt = "✅ DVOL POMAGA — kandydat do włączenia na stałe (decyzja Cezara)"
    elif d_roi < -0.5:
        werdykt = "❌ DVOL SZKODZI — zostaw opt-in OFF / rozważ wyciszenie"
    else:
        werdykt = "⚖️ NEUTRALNE — brak wyraźnej przewagi; zostaw OFF, więcej danych"
    print(f" WERDYKT: {werdykt}")
    print("=" * 66)
    print(" ⚠️ Walidacja WSTĘPNA: era DVOL ~2 lata (jeden reżim). IC≠PnL — to jest ten pomiar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
