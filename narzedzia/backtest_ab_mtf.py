"""
🕐⚔️ BACKTEST A/B — Konfluencja Multi-Timeframe (W-384) jako arbiter pieniężny.

Pytanie Cezara: czy WIDZENIE wyższych TF (brama MTF na poziomie roju) poprawia wynik?
Hipoteza Cezara (2026-06-21): najlepszy efekt MTF to NIŻSZY drawdown (wycięte wejścia
przeciw głównemu trendowi), nie wyższy zysk.

DWA PRZEBIEGI na tej samej historii (Prawo I — uczciwe A/B, identyczne bary):
  • BASELINE: mtf_konfluencja=False (obecne domyślne)
  • MTF:      mtf_konfluencja=True + mtf_weto_przeciwtrend=True (brama aktywna)

BAZA = 4h, OKNO = 400. Dlaczego: stos MTF dla 4h to {"1d":6}, a ocena trendu wymaga
≥60 barów wyższego TF → 400 barów 4h / 6 = 66 barów dziennych ≥ 60 ⇒ brama OCENIA
TREND DZIENNY = naturalny „główny trend" z hipotezy Cezara. (Na 1d/okno=250 brama
byłaby bezczynna — 35 barów tygodniowych < 60 — pomiar martwy, Prawo XV.)

OGRANICZENIE (Prawo I, jawnie): pliki 4h to ~1000 barów = ~6 mies. (I–VI 2026), więc
~12 transakcji/parę. To pomiar INDYKATYWNY (kierunkowy), nie ostateczny — mała próba
i pojedynczy reżim. DSR/PBO liczone na tym oknie.

Walidacja: DSR (deflated Sharpe, selection-bias) + PBO/CSCV (overfitting selekcji par).

Uruchom: python narzedzia/backtest_ab_mtf.py
"""

import glob
import logging
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest            # noqa: E402
from imperium.koloseum.walidacja import deflated_sharpe, pbo_cscv  # noqa: E402
from imperium.akwedukty.czytnik_csv import wczytaj_csv     # noqa: E402

INTERWAL = "4H"
OKNO = 400
FOLDER = "dane/4h"
BARY_NA_ROK = 6 * 365   # annualizacja Sharpe dla 4h (6 świec/dobę)


def _wykryj_pare(nazwa: str) -> str:
    baza = os.path.basename(nazwa).upper()
    m = re.search(r"([A-Z0-9]{2,}(?:USDT|USDC|BUSD|USD))", baza)
    return m.group(1) if m else baza


def _odkryj_pliki(base: str) -> dict:
    pliki = {}
    for p in sorted(glob.glob(os.path.join(base, FOLDER, "*.csv"))):
        pliki[_wykryj_pare(p)] = p
    return pliki


def _zwroty_po_ts(engine, bary) -> dict:
    """krzywa_equity[i] ↔ bary[OKNO+i]; zwracamy {timestamp: zwrot_baru} (kauzalnie)."""
    eq = engine.krzywa_equity
    ts = [int(b["timestamp"]) for b in bary[OKNO:]]
    eqmap = {ts[i]: e for i, e in enumerate(eq[:len(ts)])}
    dni = sorted(eqmap)
    zwroty = {}
    for j in range(1, len(dni)):
        e0, e1 = eqmap[dni[j - 1]], eqmap[dni[j]]
        if e0 > 0:
            zwroty[dni[j]] = e1 / e0 - 1.0
    return zwroty


def _sharpe(z) -> float:
    z = np.asarray(z, dtype=float)
    sd = z.std(ddof=1) if len(z) > 1 else 0.0
    return float(z.mean() / sd * math.sqrt(BARY_NA_ROK)) if sd > 0 else 0.0


def _maxdd(z) -> float:
    if len(z) == 0:
        return 0.0
    kr = np.cumprod(1 + np.asarray(z, dtype=float))
    szczyt = np.maximum.accumulate(kr)
    return float(((szczyt - kr) / szczyt).max())


def _run_config(pliki: dict, mtf: bool) -> dict:
    """Przebieg po wszystkich parach dla jednej konfiguracji. Zwraca metryki + strumienie."""
    streamy, staty = {}, {}
    for para, plik in pliki.items():
        bary = wczytaj_csv(plik, interwal=INTERWAL)
        if len(bary) <= OKNO:
            continue
        eng = backtest("", INTERWAL, bary=bary, okno=OKNO, tryb="agregat",
                       auto_rezim=True, mtf_konfluencja=mtf, mtf_weto_przeciwtrend=mtf)
        staty[para] = eng.podsumowanie()
        streamy[para] = _zwroty_po_ts(eng, bary)
    return {"streamy": streamy, "staty": staty}


def _portfel(streamy: dict):
    dni = sorted(set().union(*[set(z) for z in streamy.values()])) if streamy else []
    port = []
    for d in dni:
        vs = [streamy[p][d] for p in streamy if d in streamy[p]]
        if vs:
            port.append(sum(vs) / len(vs))
    return port, dni


def _macierz_par(streamy: dict, dni: list) -> np.ndarray:
    """T×N: kolumna = strumień zwrotów pary (brak baru → 0, czyli flat)."""
    cols = [[streamy[p].get(d, 0.0) for d in dni] for p in sorted(streamy)]
    return np.asarray(cols, dtype=float).T


def _agreguj_metryki(wynik: dict) -> dict:
    staty = wynik["staty"]
    kap_start = sum(s.kapital_startowy for s in staty.values())
    kap_end = sum(s.kapital_koncowy for s in staty.values())
    trades = sum(s.total_trades for s in staty.values())
    wins = sum(s.winning_trades for s in staty.values())
    port, dni = _portfel(wynik["streamy"])
    dsr = deflated_sharpe(port, n_prob=2)   # 2 warianty A/B przetestowane (uczciwie)
    macierz = _macierz_par(wynik["streamy"], dni)
    pbo = pbo_cscv(macierz, s_blokow=8) if macierz.shape[1] >= 2 and macierz.shape[0] >= 16 \
        else {"pbo": None, "powod": "za mało danych"}
    dd_per_para = [s.max_drawdown_pct for s in staty.values()]
    return {
        "pnl_usdt": kap_end - kap_start,
        "pnl_pct": (kap_end / kap_start - 1.0) * 100 if kap_start else 0.0,
        "trades": trades,
        "win_rate": (wins / trades) if trades else 0.0,
        "sharpe_port": _sharpe(port),
        "maxdd_port": _maxdd(port),
        "maxdd_sr_para": float(np.mean(dd_per_para)) if dd_per_para else 0.0,
        "dsr": dsr["dsr"], "dsr_ok": dsr["ok"], "sharpe_raw": dsr.get("sharpe"),
        "pbo": pbo.get("pbo"), "pbo_ok": pbo.get("ok"),
        "n_dni": len(port), "n_par": len(staty),
    }


def _signed(fmt, d):
    """fmt(d) z wymuszonym znakiem '+' dla dodatnich (gdy fmt sam go nie dodaje)."""
    s = fmt(d)
    if isinstance(d, (int, float)) and d > 0 and not s.startswith(("+", "-")):
        s = "+" + s
    return s


def _wiersz(label, a, b, fmt, lepszy=None):
    """Wiersz tabeli A/B z deltą. lepszy: 'mniej'/'wiecej'/None (bez oceny)."""
    d = b - a
    strzalka = ""
    if lepszy == "wiecej":
        strzalka = "✅" if d > 0 else ("🔻" if d < 0 else "≈")
    elif lepszy == "mniej":
        strzalka = "✅" if d < 0 else ("🔻" if d > 0 else "≈")
    print(f"  {label:24} {fmt(a):>12}  {fmt(b):>12}  {_signed(fmt, d):>12} {strzalka}")


def main():
    base = os.path.join(os.path.dirname(__file__), "..")
    pliki = _odkryj_pliki(base)
    if not pliki:
        print(f"BRAK DANYCH w {FOLDER}")
        return
    print(f"⚔️ BACKTEST A/B MTF (W-384) — {len(pliki)} par × {INTERWAL}, okno={OKNO}")
    print("   Baza 4h → brama ocenia TREND DZIENNY (1d). Okno=6 mies. (indykatywne, Prawo I)\n")

    base_w = _run_config(pliki, mtf=False)
    mtf_w = _run_config(pliki, mtf=True)
    A = _agreguj_metryki(base_w)
    B = _agreguj_metryki(mtf_w)

    # Zrzut surowych metryk PRZED drukowaniem — ubezpieczenie: błąd formatu nie kosztuje
    # ponownego 22-min przebiegu (lekcja z bugu F-string sign).
    import json
    with open(os.path.join(base, "ab_mtf_metryki.json"), "w", encoding="utf-8") as fjson:
        json.dump({"baseline": A, "mtf": B}, fjson, ensure_ascii=False, indent=2)

    def f2(v):
        return f"{v:.2f}" if isinstance(v, float) else str(v)

    def fp(v):
        return f"{v:+.1f}" if isinstance(v, (int, float)) else str(v)

    def fpct(v):
        return f"{v:.1%}" if isinstance(v, float) else str(v)

    def fi(v):
        return f"{int(v)}" if isinstance(v, (int, float)) else str(v)

    def fpctd(v):
        return f"{v:+.2f}%" if isinstance(v, (int, float)) else str(v)

    print("=" * 78)
    print(f"  {'METRYKA':24} {'BASELINE':>12}  {'MTF':>12}  {'Δ (MTF−base)':>12}")
    print("=" * 78)
    _wiersz("PnL [USDT]", A["pnl_usdt"], B["pnl_usdt"], fp, "wiecej")
    _wiersz("PnL [%]", A["pnl_pct"], B["pnl_pct"], fpctd, "wiecej")
    _wiersz("Transakcje", A["trades"], B["trades"], fi, None)
    _wiersz("Win rate", A["win_rate"], B["win_rate"], fpct, "wiecej")
    _wiersz("Sharpe portfela", A["sharpe_port"], B["sharpe_port"], f2, "wiecej")
    _wiersz("MaxDD portfela", A["maxdd_port"], B["maxdd_port"], fpct, "mniej")
    _wiersz("MaxDD śr/para", A["maxdd_sr_para"], B["maxdd_sr_para"], fpct, "mniej")
    _wiersz("DSR (n_prob=2)", A["dsr"], B["dsr"], f2, "wiecej")
    if A["pbo"] is not None and B["pbo"] is not None:
        _wiersz("PBO (selekcja par)", A["pbo"], B["pbo"], f2, "mniej")
    print("=" * 78)
    print(f"  Portfel: {A['n_par']} par równoważonych, {A['n_dni']} barów-obserwacji 4h")
    print(f"  Sharpe surowy: base={A['sharpe_raw']}  MTF={B['sharpe_raw']}")
    print("\n  LEGENDA: ✅ = MTF lepiej | 🔻 = MTF gorzej | ≈ = bez zmian")
    print("  Hipoteza Cezara: oczekiwany efekt MTF = niższy MaxDD (✅ w wierszu MaxDD).")
    print("=" * 78)


if __name__ == "__main__":
    main()
