"""
🕐⚔️📊 BACKTEST A/B MTF PER REŻIM (W-384) — czy brama pomaga w TRENDZIE, szkodzi w RANGE?

Rozszerzenie backtest_ab_mtf.py: ten sam A/B (mtf=False vs True), ale rozbity na
4 OKNA REŻIMOWE, bo hipoteza Cezara jest WARUNKOWA reżimem:
  • brama konfluencji POWINNA pomagać w trendzie (wycina kontrtrend) →
  • i SZKODZIĆ w range (wycina dobre mean-reversion).

Dane: pełna historia 4h (paginacja pobierz_4h_binance.py --od 2021-01-01), 5 par z
pełnym pokryciem 2021 (BTC/ETH/BNB/XRP/ADA — SOL odpada, listing VIII 2021).
Baza 4h, okno=400 → brama ocenia trend DZIENNY (główny trend).

OGRANICZENIE (Prawo I): 5 par, okna ~5 mies./reżim (~500–600 barów decyzyjnych) —
indykatywne. Reżimy wybrane po charakterze ceny, nie przez klasyfikator (przejrzystość).

Uruchom: python narzedzia/backtest_ab_mtf_rezimy.py
"""

import importlib.util
import json
import logging
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest            # noqa: E402
from imperium.koloseum.walidacja import deflated_sharpe    # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv     # noqa: E402

# Reużycie helperów metryk z siostrzanego narzędzia (ten sam katalog).
_spec = importlib.util.spec_from_file_location(
    "ab_base", os.path.join(os.path.dirname(__file__), "backtest_ab_mtf.py"))
ab = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ab)

INTERWAL = "4H"
OKNO = 400
ab.OKNO = OKNO   # wyrównaj OKNO helperów (_zwroty_po_ts korzysta z ab.OKNO)
FOLDER = "dane/4h"
PARY = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]

# Okna reżimowe (UTC). ~5 mies. każde. Dobrane po charakterze ceny crypto.
REZIMY = {
    "BULL_2021  (trend↑)":  ("2021-01-01", "2021-05-31"),
    "BEAR_2022  (trend↓)":  ("2022-04-01", "2022-08-31"),
    "RANGE_2023 (bok)":     ("2023-07-01", "2023-11-30"),
    "RECENT_25-26 (mix)":   ("2025-12-15", "2026-06-15"),
}


def _ms(data: str) -> int:
    return int(datetime.strptime(data, "%Y-%m-%d")
               .replace(tzinfo=timezone.utc).timestamp() * 1000)


def _tnij(bary, start_ms, end_ms):
    return [b for b in bary if start_ms <= int(b["timestamp"]) <= end_ms]


def _metryki_okna(pliki: dict, start_ms: int, end_ms: int, mtf: bool) -> dict:
    """Backtest wszystkich par na wycinku reżimu dla jednej konfiguracji."""
    streamy, staty = {}, {}
    for para, plik in pliki.items():
        bary = wczytaj_csv(plik, interwal=INTERWAL)
        wycinek = _tnij(bary, start_ms, end_ms)
        if len(wycinek) <= OKNO + 20:
            continue
        eng = backtest("", INTERWAL, bary=wycinek, okno=OKNO, tryb="agregat",
                       auto_rezim=True, mtf_konfluencja=mtf, mtf_weto_przeciwtrend=mtf)
        staty[para] = eng.podsumowanie()
        streamy[para] = ab._zwroty_po_ts(eng, wycinek)
    if not staty:
        return None
    kap_start = sum(s.kapital_startowy for s in staty.values())
    kap_end = sum(s.kapital_koncowy for s in staty.values())
    trades = sum(s.total_trades for s in staty.values())
    wins = sum(s.winning_trades for s in staty.values())
    port, _ = ab._portfel(streamy)
    dsr = deflated_sharpe(port, n_prob=2)
    return {
        "pnl_pct": (kap_end / kap_start - 1.0) * 100 if kap_start else 0.0,
        "trades": trades,
        "win_rate": (wins / trades) if trades else 0.0,
        "sharpe": ab._sharpe(port),
        "maxdd": ab._maxdd(port),
        "dsr": dsr["dsr"],
        "n_par": len(staty),
    }


def _fpctd(v):
    return f"{v:+.2f}%" if isinstance(v, (int, float)) else str(v)


def _f2(v):
    return f"{v:.2f}" if isinstance(v, float) else str(v)


def _fpct(v):
    return f"{v:.1%}" if isinstance(v, float) else str(v)


def _fi(v):
    return f"{int(v)}" if isinstance(v, (int, float)) else str(v)


def main():
    base = os.path.join(os.path.dirname(__file__), "..")
    pliki = {p: os.path.join(base, FOLDER, f"Binance_{p}_4h.csv") for p in PARY}
    pliki = {p: s for p, s in pliki.items() if os.path.exists(s)}
    print(f"⚔️📊 BACKTEST A/B MTF PER REŻIM (W-384) — {len(pliki)} par × {INTERWAL}, okno={OKNO}")
    print("   Brama ocenia trend DZIENNY. Hipoteza: pomaga w trendzie, szkodzi w range.\n")

    wyniki = {}
    for label, (d0, d1) in REZIMY.items():
        s_ms, e_ms = _ms(d0), _ms(d1)
        A = _metryki_okna(pliki, s_ms, e_ms, mtf=False)
        B = _metryki_okna(pliki, s_ms, e_ms, mtf=True)
        wyniki[label] = {"baseline": A, "mtf": B, "okno": (d0, d1)}

    with open(os.path.join(base, "ab_mtf_rezimy_metryki.json"), "w", encoding="utf-8") as f:
        json.dump(wyniki, f, ensure_ascii=False, indent=2)

    print("=" * 78)
    for label, w in wyniki.items():
        A, B = w["baseline"], w["mtf"]
        d0, d1 = w["okno"]
        print(f"\n▣ REŻIM {label}   [{d0} … {d1}]")
        if A is None or B is None:
            print("   (za mało danych w oknie — pominięto)")
            continue
        print(f"   {'metryka':16} {'BASELINE':>10} {'MTF':>10} {'Δ':>10}")
        ab._wiersz("PnL [%]", A["pnl_pct"], B["pnl_pct"], _fpctd, "wiecej")
        ab._wiersz("Transakcje", A["trades"], B["trades"], _fi, None)
        ab._wiersz("Win rate", A["win_rate"], B["win_rate"], _fpct, "wiecej")
        ab._wiersz("Sharpe", A["sharpe"], B["sharpe"], _f2, "wiecej")
        ab._wiersz("MaxDD", A["maxdd"], B["maxdd"], _fpct, "mniej")
        ab._wiersz("DSR (n=2)", A["dsr"], B["dsr"], _f2, "wiecej")
    print("\n" + "=" * 78)
    print("  KLUCZ HIPOTEZY: MTF ✅ MaxDD w BULL/BEAR (trend) i 🔻 w RANGE = hipoteza potwierdzona.")
    print("  ✅ = MTF lepiej | 🔻 = MTF gorzej | ≈ = bez zmian")
    print("=" * 78)


if __name__ == "__main__":
    main()
