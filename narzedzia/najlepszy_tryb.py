"""
🏆 NAJLEPSZY TRYB IMPERIUM — Skaner Okazji + Gubernator + Regime-Aware + Compounding.

Jeden skrypt: skanuje WSZYSTKIE dostepne pary w dane/4h/ i dane/godzinowe/,
wybiera tylko NAJLEPSZE okazje co swiece, otwiera wynik w przegladarce.

Parametry uzyte (sprawdzone, najlepszy wynik na 5 parach +270%):
  - tryb_skaner=True    → wybor TOP-3 okazji z calego koszyka co swiece
  - skaner_top_n=3      → maksymalnie 3 otwarte pozycje naraz
  - skaner_min_adx=20   → tylko monety z wyraznym trendem (ADX >= 20)
  - skaner_min_ts=0.01  → moneta musi ruszyc >=1% zeby wejsc (dry powder)
  - gubernator=True     → kontrola globalnej ekspozycji (W-325)
  - compounding=True    → zyski sa reinwestowane
  - auto_rezim=True     → Namiestnik klasyfikuje rynek (TREND/PANIC/RANGING...)

UZYCIE (w folderze repo):
    python narzedzia/najlepszy_tryb.py             # 4h, wszystkie dostepne pary
    python narzedzia/najlepszy_tryb.py --1h        # 1h zamiast 4h
    python narzedzia/najlepszy_tryb.py --top 5     # TOP-5 zamiast TOP-3
    python narzedzia/najlepszy_tryb.py --nofile    # nie otwieraj przegladarki
"""
import argparse
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

from imperium.koloseum.backtest import backtest_portfel


# ── helpers HTML/SVG (zero zaleznosci, inline) ─────────────────────────────

def _svg_krzywa(equity: list, szer: int = 920, wys: int = 320) -> str:
    if len(equity) < 2:
        return "<p>Za mało transakcji.</p>"
    lo, hi = min(equity), max(equity)
    roz = (hi - lo) or 1.0
    mh, mw = 20, 50
    pw, ph = szer - 2 * mw, wys - 2 * mh

    def x(i): return mw + pw * i / (len(equity) - 1)
    def y(v): return mh + ph * (1 - (v - lo) / roz)

    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(equity))
    yb = y(equity[0])
    kol = "#33d17a" if equity[-1] >= equity[0] else "#e01b24"
    area = f"{mw},{mh+ph} " + pts + f" {mw+pw},{mh+ph}"
    return (f'<svg viewBox="0 0 {szer} {wys}" width="100%" '
            f'style="background:#11151c;border-radius:10px">'
            f'<polyline points="{area}" fill="{kol}22" stroke="none"/>'
            f'<line x1="{mw}" y1="{yb:.1f}" x2="{mw+pw}" y2="{yb:.1f}" '
            f'stroke="#555" stroke-dasharray="4 4"/>'
            f'<polyline points="{pts}" fill="none" stroke="{kol}" stroke-width="2"/>'
            f'<text x="{mw}" y="{mh-6}" fill="#888" font-size="11">max {hi:,.0f}</text>'
            f'<text x="{mw}" y="{mh+ph+15}" fill="#888" font-size="11">min {lo:,.0f}</text>'
            f'</svg>')


def _kafel(et: str, val: str, kol: str = "#e6e6e6") -> str:
    return (f'<div style="background:#1a212b;border-radius:10px;padding:14px 18px;min-width:150px">'
            f'<div style="color:#7a8a9a;font-size:12px;text-transform:uppercase">{et}</div>'
            f'<div style="color:{kol};font-size:24px;font-weight:600;margin-top:4px">{val}</div></div>')


def generuj_html(engine, pliki: dict, interwal: str, top_n: int) -> str:
    stats = engine.podsumowanie()
    hist = engine.historia_zamkniec
    equity = [engine.kapital_startowy] + [w.kapital_po for w in hist]

    pnl = stats.kapital_koncowy - stats.kapital_startowy
    pnl_pct = pnl / stats.kapital_startowy * 100 if stats.kapital_startowy else 0
    kol = "#33d17a" if pnl >= 0 else "#e01b24"
    z = "+" if pnl >= 0 else ""

    kafle = "".join([
        _kafel("Kapitał start", f"{stats.kapital_startowy:,.0f}"),
        _kafel("Kapitał end", f"{stats.kapital_koncowy:,.0f}", kol),
        _kafel("PnL", f"{z}{pnl:,.0f} ({z}{pnl_pct:.1f}%)", kol),
        _kafel("Trades", f"{stats.total_trades}"),
        _kafel("Win Rate", f"{stats.win_rate*100:.1f}%"),
        _kafel("Profit Factor", f"{stats.profit_factor:.2f}"),
        _kafel("Max Drawdown", f"{stats.max_drawdown_pct*100:.1f}%", "#e5a50a"),
        _kafel("Prowizje", f"{sum(w.prowizja_usdt for w in hist):,.0f} USDT", "#888"),
    ])

    # top 5 walut wg PnL
    wg_sym: dict = {}
    for w in hist:
        wg_sym.setdefault(w.symbol, []).append(w.pnl_usdt)
    sym_stats = sorted(
        [(s, sum(v), len(v), sum(1 for x in v if x > 0) / len(v) * 100) for s, v in wg_sym.items()],
        key=lambda x: -x[1]
    )
    sym_rows = ""
    for sym, total, cnt, wr in sym_stats:
        kp = "#33d17a" if total >= 0 else "#e01b24"
        sym_rows += (f'<tr><td>{sym}</td><td style="color:{kp}">{total:+.2f}</td>'
                     f'<td>{cnt}</td><td>{wr:.0f}%</td></tr>')

    # ostatnie 25 transakcji
    wiersze = ""
    for w in hist[-25:][::-1]:
        kp = "#33d17a" if w.pnl_usdt >= 0 else "#e01b24"
        wiersze += (f'<tr><td>{w.symbol}</td><td>{w.kierunek}</td>'
                    f'<td>{w.cena_wejscia:.4f}</td><td>{w.cena_zamkniecia:.4f}</td>'
                    f'<td style="color:{kp}">{w.pnl_usdt:+.2f}</td>'
                    f'<td style="color:{kp}">{w.pnl_pct*100:+.2f}%</td>'
                    f'<td>{w.czas_trwania_bar}</td>'
                    f'<td style="color:#888">{w.powod_zamkniecia}</td></tr>')

    pary_str = ", ".join(pliki.keys())
    teraz = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'''<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">
<title>Imperium — Najlepszy Tryb [{interwal}]</title>
<style>
  body{{margin:0;background:#0b0e13;color:#e6e6e6;font-family:-apple-system,Segoe UI,sans-serif}}
  .w{{max-width:1000px;margin:0 auto;padding:28px}}
  h1{{font-size:22px;margin:0 0 4px}}
  .sub{{color:#7a8a9a;font-size:13px;margin-bottom:22px}}
  .kf{{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:24px}}
  table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}}
  th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid #1f2733}}
  th{{color:#7a8a9a;text-transform:uppercase;font-size:11px;letter-spacing:.5px}}
  h2{{font-size:15px;color:#c9d4e0;margin:26px 0 6px}}
  .badge{{display:inline-block;background:#1f3355;color:#6ea8fe;border-radius:6px;
           padding:3px 10px;font-size:12px;margin-right:6px}}
</style></head><body><div class="w">
<h1>🏆 Imperium — Najlepszy Tryb (Skaner Okazji)</h1>
<div class="sub">
  <span class="badge">Skaner TOP-{top_n}</span>
  <span class="badge">Gubernator</span>
  <span class="badge">Regime-Aware</span>
  <span class="badge">Compounding</span>
  <span class="badge">{interwal}</span>
  · {len(pliki)} par · {teraz}
</div>
<div style="color:#7a8a9a;font-size:12px;margin-bottom:16px">Pary: {pary_str}</div>
<div class="kf">{kafle}</div>
<h2>📈 Krzywa kapitału ({len(equity)} punktów)</h2>
{_svg_krzywa(equity)}
<h2>🏅 Wyniki per waluta</h2>
<table><thead><tr><th>Symbol</th><th>PnL USDT</th><th>Trades</th><th>Win Rate</th></tr></thead>
<tbody>{sym_rows}</tbody></table>
<h2>📋 Ostatnie 25 transakcji</h2>
<table><thead><tr><th>Symbol</th><th>Kier</th><th>Wejście</th><th>Wyjście</th>
<th>PnL USDT</th><th>PnL %</th><th>Bary</th><th>Powód</th></tr></thead>
<tbody>{wiersze}</tbody></table>
<p style="color:#556;margin-top:30px;font-size:12px">
  ⚖️ Prawo I — wynik historyczny ≠ gwarancja przyszłości.<br>
  Max ryzyko per trade: 2% kapitału. Lewar auto (2×–20× wg pewności roju).
</p>
</div></body></html>'''


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Najlepszy tryb Imperium — Skaner Okazji")
    p.add_argument("--1h",      dest="interwał_1h", action="store_true", help="użyj danych 1h zamiast 4h")
    p.add_argument("--top",     type=int, default=3, help="ile najlepszych okazji naraz (domyślnie 3)")
    p.add_argument("--kapital", type=float, default=10_000.0)
    p.add_argument("--okno",    type=int, default=250)
    p.add_argument("--nofile",  action="store_true", help="nie otwieraj przeglądarki")
    args = p.parse_args()

    if args.interwał_1h:
        folder, interwal, sufiks = "dane/godzinowe", "1H", "_1h.csv"
    else:
        folder, interwal, sufiks = "dane/4h", "4H", "_4h.csv"

    # Automatycznie znajdz wszystkie dostepne pliki CSV
    pliki = {}
    for f in sorted(Path(folder).glob("*.csv")):
        if f.name.endswith(sufiks):
            # wyciagnij symbol: Binance_BTCUSDT_4h.csv → BTCUSDT
            czesc = f.stem.split("_")
            symbol = czesc[-2] if len(czesc) >= 2 else czesc[0]
            pliki[symbol.upper()] = str(f)

    if not pliki:
        print(f"Brak plików CSV w {folder}/ (oczekiwany sufiks: {sufiks})")
        print("Pobierz dane: python narzedzia/pobierz_4h_binance.py")
        sys.exit(1)

    print("\n🏆 NAJLEPSZY TRYB IMPERIUM")
    print(f"   Interwał : {interwal}")
    print(f"   Pary     : {len(pliki)} ({', '.join(pliki.keys())})")
    print(f"   Top-N    : {args.top} najlepszych okazji naraz")
    print(f"   Kapitał  : {args.kapital:,.0f} USDT")
    print("\n▶ Uruchamiam backtest (może potrwać 2-5 minut)...\n")

    engine = backtest_portfel(
        pliki,
        interwal=interwal,
        okno=args.okno,
        kapital_startowy=args.kapital,
        tryb_skaner=True,
        skaner_top_n=args.top,
        skaner_min_adx=20.0,
        skaner_min_ts=0.01,
        gubernator=True,
        compounding=True,
        auto_rezim=True,
        mwu_learning=True,       # W-303 per-coin: każda waluta uczy się własnych wag neuronów
        igrzyska_learning=True,  # W-307 per-coin: ranking accuracy/stability per symbol
        synapsy_rezimowe=True,   # W-299 per-coin: koalicje par neuronów warunkowane reżimem
    )

    engine.drukuj_raport()

    out_dir = Path("raporty")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"najlepszy_tryb_{interwal}_{len(pliki)}par.html"
    out.write_text(generuj_html(engine, pliki, interwal, args.top), encoding="utf-8")
    sciezka_abs = str(out.resolve())
    print(f"\n✅ Dashboard: {sciezka_abs}")
    if not args.nofile:
        webbrowser.open(f"file://{sciezka_abs}")
        print("   (otwarto w przeglądarce)")


if __name__ == "__main__":
    main()
