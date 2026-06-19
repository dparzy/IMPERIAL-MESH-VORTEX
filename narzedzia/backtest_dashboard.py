"""
📊 BACKTEST DASHBOARD — uruchamia backtest i renderuje wynik w przeglądarce.

Filozofia Imperium: ZERO ZALEŻNOŚCI. Krzywą kapitału rysujemy jako inline SVG
(bez matplotlib), raport to samowystarczalny HTML. Po wygenerowaniu plik otwiera
się sam w domyślnej przeglądarce.

Backtest (imperium/koloseum/backtest.py) drukuje raport do terminala i zwraca
silnik z pełną `historia_zamkniec`. Z niej odtwarzamy krzywą equity (kapital_po
po każdej zamkniętej pozycji) i statystyki sesji.

UŻYCIE:
    python narzedzia/backtest_dashboard.py dane/4h/Binance_BTCUSDT_4h.csv 4H
    python narzedzia/backtest_dashboard.py dane/godzinowe/Binance_ETHUSDT_1h.csv 1H --okno 500
    python narzedzia/backtest_dashboard.py dane/4h/Binance_BTCUSDT_4h.csv 4H --auto

Flagi:
    --okno N     okno barów (domyślnie 250)
    --kapital N  kapitał startowy USDT (domyślnie 10000)
    --auto       włącz klasyfikację reżimu + Namiestnika (Regime-Aware Gating)
    --nofile     nie otwieraj przeglądarki (tylko zapis HTML)
"""
import argparse
import os
import sys
import webbrowser
from datetime import datetime, timezone

from imperium.koloseum.backtest import backtest


def _svg_krzywa(equity: list, szer: int = 920, wys: int = 320) -> str:
    """Rysuje krzywą kapitału jako inline SVG (zero zależności)."""
    if len(equity) < 2:
        return '<p style="color:#888">Za mało transakcji na wykres.</p>'
    lo, hi = min(equity), max(equity)
    rozpieto = (hi - lo) or 1.0
    mh, mw = 20, 50  # marginesy
    pw, ph = szer - 2 * mw, wys - 2 * mh

    def x(i):
        return mw + pw * i / (len(equity) - 1)

    def y(v):
        return mh + ph * (1 - (v - lo) / rozpieto)

    punkty = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(equity))
    start = equity[0]
    # linia bazowa (kapitał startowy)
    yb = y(start)
    kolor = "#33d17a" if equity[-1] >= start else "#e01b24"
    # wypełnienie pod krzywą
    obszar = f"{mw},{mh+ph} " + punkty + f" {mw+pw},{mh+ph}"
    return f'''<svg viewBox="0 0 {szer} {wys}" width="100%" style="background:#11151c;border-radius:10px">
  <polyline points="{obszar}" fill="{kolor}22" stroke="none"/>
  <line x1="{mw}" y1="{yb:.1f}" x2="{mw+pw}" y2="{yb:.1f}" stroke="#555" stroke-dasharray="4 4"/>
  <polyline points="{punkty}" fill="none" stroke="{kolor}" stroke-width="2"/>
  <text x="{mw}" y="{mh-6}" fill="#888" font-size="11">max {hi:,.0f}</text>
  <text x="{mw}" y="{mh+ph+15}" fill="#888" font-size="11">min {lo:,.0f}</text>
  <text x="{mw+pw-90}" y="{yb-6:.1f}" fill="#777" font-size="11">start {start:,.0f}</text>
</svg>'''


def _kafel(etykieta: str, wartosc: str, kolor: str = "#e6e6e6") -> str:
    return (f'<div style="background:#1a212b;border-radius:10px;padding:14px 18px;min-width:140px">'
            f'<div style="color:#7a8a9a;font-size:12px;text-transform:uppercase;letter-spacing:.5px">{etykieta}</div>'
            f'<div style="color:{kolor};font-size:24px;font-weight:600;margin-top:4px">{wartosc}</div></div>')


def generuj_html(engine, sciezka: str, interwal: str) -> str:
    stats = engine.podsumowanie()
    hist = engine.historia_zamkniec
    equity = [engine.kapital_startowy] + [w.kapital_po for w in hist]

    pnl = stats.kapital_koncowy - stats.kapital_startowy
    pnl_pct = pnl / stats.kapital_startowy * 100 if stats.kapital_startowy else 0
    kolor_pnl = "#33d17a" if pnl >= 0 else "#e01b24"
    znak = "+" if pnl >= 0 else ""

    kafle = "".join([
        _kafel("Kapitał start", f"{stats.kapital_startowy:,.0f}"),
        _kafel("Kapitał end", f"{stats.kapital_koncowy:,.0f}", kolor_pnl),
        _kafel("PnL", f"{znak}{pnl:,.0f} ({znak}{pnl_pct:.2f}%)", kolor_pnl),
        _kafel("Trades", f"{stats.total_trades}"),
        _kafel("Win Rate", f"{stats.win_rate*100:.1f}%"),
        _kafel("Profit Factor", f"{stats.profit_factor:.2f}"),
        _kafel("Max Drawdown", f"{stats.max_drawdown_pct*100:.1f}%", "#e5a50a"),
    ])

    # ostatnie 20 transakcji
    wiersze = ""
    for w in hist[-20:][::-1]:
        kp = "#33d17a" if w.pnl_usdt >= 0 else "#e01b24"
        wiersze += (f'<tr><td>{w.symbol}</td><td>{w.kierunek}</td>'
                    f'<td>{w.cena_wejscia:.4f}</td><td>{w.cena_zamkniecia:.4f}</td>'
                    f'<td style="color:{kp}">{w.pnl_usdt:+.2f}</td>'
                    f'<td style="color:{kp}">{w.pnl_pct*100:+.2f}%</td>'
                    f'<td>{w.czas_trwania_bar}</td><td style="color:#888">{w.powod_zamkniecia}</td></tr>')

    teraz = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'''<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">
<title>Imperium — Backtest {os.path.basename(sciezka)}</title>
<style>
  body{{margin:0;background:#0b0e13;color:#e6e6e6;font-family:-apple-system,Segoe UI,Roboto,sans-serif}}
  .wrap{{max-width:980px;margin:0 auto;padding:28px}}
  h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#7a8a9a;font-size:13px;margin-bottom:22px}}
  .kafle{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px}}
  table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:10px}}
  th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid #1f2733}}
  th{{color:#7a8a9a;text-transform:uppercase;font-size:11px;letter-spacing:.5px}}
  h2{{font-size:15px;color:#c9d4e0;margin:26px 0 6px}}
</style></head><body><div class="wrap">
  <h1>🏟️ Imperium — Raport Backtestu</h1>
  <div class="sub">{os.path.basename(sciezka)} · interwał {interwal} · sesja {engine.sesja_id} · {teraz}</div>
  <div class="kafle">{kafle}</div>
  <h2>📈 Krzywa kapitału ({len(equity)} punktów)</h2>
  {_svg_krzywa(equity)}
  <h2>📋 Ostatnie 20 transakcji</h2>
  <table><thead><tr><th>Symbol</th><th>Kier</th><th>Wejście</th><th>Wyjście</th>
  <th>PnL USDT</th><th>PnL %</th><th>Bary</th><th>Powód</th></tr></thead>
  <tbody>{wiersze}</tbody></table>
  <p style="color:#556;margin-top:30px;font-size:12px">Prawo I — backtest bez look-ahead.
  Wynik historyczny ≠ gwarancja przyszłości.</p>
</div></body></html>'''


def main():
    p = argparse.ArgumentParser(description="Backtest + dashboard HTML")
    p.add_argument("sciezka", help="ścieżka do pliku CSV")
    p.add_argument("interwal", help="etykieta interwału, np. 4H / 1H / 1D")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--kapital", type=float, default=10_000.0)
    p.add_argument("--auto", action="store_true", help="Regime-Aware Gating (Namiestnik)")
    p.add_argument("--nofile", action="store_true", help="nie otwieraj przeglądarki")
    args = p.parse_args()

    if not os.path.exists(args.sciezka):
        print(f"Brak pliku: {args.sciezka}")
        sys.exit(1)

    print(f"▶ Backtest {args.sciezka} [{args.interwal}] okno={args.okno} auto={args.auto} ...")
    engine = backtest(args.sciezka, args.interwal, okno=args.okno,
                      kapital_startowy=args.kapital, auto_rezim=args.auto)
    engine.drukuj_raport()

    html = generuj_html(engine, args.sciezka, args.interwal)
    out_dir = "raporty"
    os.makedirs(out_dir, exist_ok=True)
    nazwa = os.path.splitext(os.path.basename(args.sciezka))[0]
    out = os.path.join(out_dir, f"backtest_{nazwa}_{args.interwal}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    sciezka_abs = os.path.abspath(out)
    print(f"\n✅ Dashboard zapisany: {sciezka_abs}")
    if not args.nofile:
        webbrowser.open(f"file://{sciezka_abs}")
        print("   (otwarto w przeglądarce)")


if __name__ == "__main__":
    main()
