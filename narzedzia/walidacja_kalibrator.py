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
            "win_rate": st.win_rate, "pnl": st.total_pnl_usdt}


def porownaj(pliki, interwal: str, okno: int = 250, max_barow=None) -> str:
    from imperium.koloseum.backtest import backtest
    agg = {"baza": {"trades": 0, "pnl": 0.0, "win_num": 0.0, "win_den": 0},
           "kalib": {"trades": 0, "pnl": 0.0, "win_num": 0.0, "win_den": 0}}
    n = len(pliki)
    for i, plik in enumerate(pliki, 1):
        print(f"  [{i}/{n}] {Path(plik).name}...", file=sys.stderr, flush=True)
        for tryb, flaga in (("baza", False), ("kalib", True)):
            try:
                eng = backtest(plik, interwal, okno=okno, max_barow=max_barow,
                               auto_rezim=True, kalibruj_prog=flaga)
            except Exception as e:  # noqa: BLE001 — pojedyncza para nie wywala raportu
                print(f"    ⚠️ {tryb} {Path(plik).name}: {e}", file=sys.stderr, flush=True)
                continue
            m = _metryki(eng)
            agg[tryb]["trades"] += m["trades"]
            agg[tryb]["pnl"] += m["pnl"]
            agg[tryb]["win_num"] += m["win_rate"] * m["trades"]
            agg[tryb]["win_den"] += m["trades"]

    def wr(a):
        return a["win_num"] / a["win_den"] if a["win_den"] else 0.0
    b, k = agg["baza"], agg["kalib"]
    linie = [f"🔬 WALIDACJA KALIBRATORA — {n} par, interwał {interwal}",
             "   (bramka konformalna TYLKO zaostrza próg — mniej wejść, celuje w wyższy win-rate)",
             "",
             f"   {'metryka':<14}{'BAZA':>12}{'KALIBRACJA':>14}",
             f"   {'trades':<14}{b['trades']:>12}{k['trades']:>14}",
             f"   {'win_rate':<14}{wr(b):>11.1%}{wr(k):>13.1%}",
             f"   {'PnL [$]':<14}{b['pnl']:>12.0f}{k['pnl']:>14.0f}",
             ""]
    # Werdykt (uczciwy, Prawo I)
    lepszy_wr = wr(k) >= wr(b)
    ochrona = k["pnl"] >= b["pnl"] or (b["pnl"] < 0 and k["pnl"] > b["pnl"])
    if lepszy_wr and ochrona:
        linie.append("   ✅ WALIDACJA OK — kalibracja poprawia lub chroni. Można włączyć kalibruj_prog=True.")
    elif lepszy_wr or ochrona:
        linie.append("   ⚠️ CZĘŚCIOWA — jedno kryterium spełnione. Rozważ dłuższą/wieloreżimową próbę.")
    else:
        linie.append("   ❌ BRAK KORZYŚCI na tej próbie — NIE włączaj; przetestuj na innych danych/reżimach.")
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
