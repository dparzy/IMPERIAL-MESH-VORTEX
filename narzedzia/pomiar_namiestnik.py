"""
📊 POMIAR NAMIESTNIKA — tabela dowodowa przed/po (Prawo XVI).

Porównuje dwa światy na tych samych barach:
  BASELINE   — rezim="NORMAL" na sztywno, bez Namiestnika (stan sprzed naprawy)
  NAMIESTNIK — rezim="AUTO" (klasyfikuj_rezim) + Namiestnik steruje tryb/lewar/próg

Uruchom:  python narzedzia/pomiar_namiestnik.py
"""

import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.disable(logging.CRITICAL)

from imperium.koloseum.backtest import backtest  # noqa: E402

# (etykieta, ścieżka, interwał, limit barów)
ZESTAWY = [
    ("BTC 1D", "dane/dzienne/Binance_BTCUSDT_d.csv", "1D", None),
    ("ETH 1D", "dane/dzienne/Binance_ETHUSDT_d.csv", "1D", None),
    ("BTC 1H", "dane/godzinowe/Binance_BTCUSDT_1h.csv", "1H", 5000),
    ("ETH 1H", "dane/godzinowe/Binance_ETHUSDT_1h.csv", "1H", 5000),
]


def _statystyki(eng):
    st = eng.podsumowanie()
    st.oblicz(eng.historia_zamkniec)
    pnl = (st.kapital_koncowy / st.kapital_startowy - 1) * 100
    return {
        "pnl": pnl,
        "trades": st.total_trades,
        "wr": st.win_rate,
        "pf": st.profit_factor,
        "dd": st.max_drawdown_pct,
    }


def main():
    print(f"\n{'═'*86}")
    print("  📊 POMIAR NAMIESTNIKA — BASELINE (NORMAL) vs NAMIESTNIK (AUTO) — Prawo XVI")
    print(f"{'═'*86}")
    print(f"  {'Zestaw':<10}{'Wariant':<12}{'PnL %':>10}{'Trades':>9}"
          f"{'WinRate':>10}{'PF':>8}{'MaxDD':>9}")
    print(f"  {'-'*78}")

    for etykieta, sciezka, interwal, limit in ZESTAWY:
        from imperium.akwedukty.czytnik_csv import wczytaj_csv
        bary = wczytaj_csv(sciezka, interwal=interwal, limit=limit)

        base = _statystyki(backtest(sciezka, interwal, tryb="agregat",
                                    auto_rezim=False, bary=bary))
        naz = _statystyki(backtest(sciezka, interwal, tryb="agregat",
                                   auto_rezim=True, bary=bary))

        print(f"  {etykieta:<10}{'BASELINE':<12}{base['pnl']:>+9.2f}%{base['trades']:>9}"
              f"{base['wr']:>9.1%}{base['pf']:>8.2f}{base['dd']:>8.1%}")
        delta = naz['pnl'] - base['pnl']
        print(f"  {'':<10}{'NAMIESTNIK':<12}{naz['pnl']:>+9.2f}%{naz['trades']:>9}"
              f"{naz['wr']:>9.1%}{naz['pf']:>8.2f}{naz['dd']:>8.1%}"
              f"   Δ={delta:+.2f}pp")
        print(f"  {'-'*78}")

    print(f"{'═'*86}\n")


if __name__ == "__main__":
    main()
