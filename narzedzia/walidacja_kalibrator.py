"""
🔬 WALIDACJA KALIBRATORA — A/B progu pewności: baza vs bramka konformalna (ML-36).

Odpala backtest DWA razy na tych samych świecach: `kalibruj_prog=False` (baza) i `=True`
(bramka konformalna podnosi próg po serii strat). Porównuje trades / win-rate / PnL / DD.
Bramka TYLKO zaostrza, więc oczekujemy: mniej wejść, wyższy (lub równy) win-rate, ochrona
kapitału w słabych okresach. To jest „walidacja przed wdrożeniem" — włączasz `kalibruj_prog`
w configu DOPIERO gdy tabela to potwierdzi (Prawo I: decyzja z pomiaru, nie z wiary).

Dane rynkowe są LOKALNE (poza gitem) — uruchamiaj na laptopie:
    python narzedzia/walidacja_kalibrator.py
    python narzedzia/walidacja_kalibrator.py --glob "dane/dzienne/*_d.csv" --interwal 1d
"""
from __future__ import annotations

import argparse
import glob as _glob
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _metryki(eng) -> dict:
    st = eng.podsumowanie()
    return {"trades": len(eng.historia_zamkniec),
            "win_rate": st.win_rate, "pnl": st.total_pnl_usdt,
            "dd": getattr(st, "max_drawdown_pct", 0.0)}


def porownaj(pliki, interwal: str, okno: int = 250, max_barow=None) -> str:
    from imperium.koloseum.backtest import backtest
    agg = {"baza": {"trades": 0, "pnl": 0.0, "win_num": 0.0, "win_den": 0, "dd": 0.0},
           "kalib": {"trades": 0, "pnl": 0.0, "win_num": 0.0, "win_den": 0, "dd": 0.0}}
    n = len(pliki)
    pominiete = 0
    for i, plik in enumerate(pliki, 1):
        print(f"  [{i}/{n}] {Path(plik).name}...", file=sys.stderr, flush=True)
        # Uruchom OBA tryby; agreguj parę TYLKO gdy oba się udały — fair na tej samej próbie (cubic P1).
        wyniki = {}
        for tryb, flaga in (("baza", False), ("kalib", True)):
            try:
                eng = backtest(plik, interwal, okno=okno, max_barow=max_barow,
                               auto_rezim=True, kalibruj_prog=flaga)
                wyniki[tryb] = _metryki(eng)
            except Exception as e:  # noqa: BLE001 — pojedyncza para nie wywala raportu
                print(f"    ⚠️ {tryb} {Path(plik).name}: {e}", file=sys.stderr, flush=True)
        if "baza" not in wyniki or "kalib" not in wyniki:
            pominiete += 1
            continue   # niesparowane — nie zaśmiecaj A/B połową danych
        for tryb in ("baza", "kalib"):
            m = wyniki[tryb]
            agg[tryb]["trades"] += m["trades"]
            agg[tryb]["pnl"] += m["pnl"]
            agg[tryb]["win_num"] += m["win_rate"] * m["trades"]
            agg[tryb]["win_den"] += m["trades"]
            agg[tryb]["dd"] = max(agg[tryb]["dd"], m["dd"])   # najgorsze obsunięcie w koszyku

    def wr(a):
        return a["win_num"] / a["win_den"] if a["win_den"] else 0.0
    b, k = agg["baza"], agg["kalib"]
    sparowane = n - pominiete
    linie = [f"🔬 WALIDACJA KALIBRATORA — {sparowane}/{n} par sparowanych, interwał {interwal}",
             "   (bramka konformalna TYLKO zaostrza próg — mniej wejść, celuje w wyższy win-rate + niższy DD)",
             ""]
    if pominiete:
        linie.append(f"   ⚠️ {pominiete} par pominięto (jeden z trybów padł) — poza A/B.")
        linie.append("")
    linie += [f"   {'metryka':<14}{'BAZA':>12}{'KALIBRACJA':>14}",
              f"   {'trades':<14}{b['trades']:>12}{k['trades']:>14}",
              f"   {'win_rate':<14}{wr(b):>11.1%}{wr(k):>13.1%}",
              f"   {'PnL [$]':<14}{b['pnl']:>12.0f}{k['pnl']:>14.0f}",
              f"   {'maxDD [%]':<14}{b['dd']:>11.1%}{k['dd']:>13.1%}",
              ""]
    # Werdykt (uczciwy, Prawo I): win-rate ≥, PnL chroniony ORAZ DD nie gorszy.
    lepszy_wr = wr(k) >= wr(b)
    ochrona_pnl = k["pnl"] >= b["pnl"] or (b["pnl"] < 0 and k["pnl"] > b["pnl"])
    ochrona_dd = k["dd"] <= b["dd"] + 1e-9
    if lepszy_wr and ochrona_pnl and ochrona_dd:
        linie.append("   ✅ WALIDACJA OK — wyższy win-rate, chroni PnL i DD. Można włączyć kalibruj_prog=True.")
    elif (lepszy_wr or ochrona_pnl) and ochrona_dd:
        linie.append("   ⚠️ CZĘŚCIOWA — część kryteriów spełniona (DD OK). Rozważ dłuższą/wieloreżimową próbę.")
    else:
        linie.append("   ❌ BRAK KORZYŚCI / gorszy DD — NIE włączaj; przetestuj na innych danych/reżimach.")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Walidacja A/B bramki konformalnej (ML-36)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--max-barow", type=int, default=None)
    args = p.parse_args()
    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print(f"Brak plików dla wzorca: {args.glob} (dane są lokalne — pobierz je najpierw)")
        sys.exit(1)
    print(porownaj(pliki, args.interwal, okno=args.okno, max_barow=args.max_barow))
