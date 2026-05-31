"""
╔══════════════════════════════════════════════════════════════════════════════╗
║       Kartograf (The Cartographer) — Wykresy Biegów v1.0                     ║
║  Projekt: IMPERIUM — architekt: VITRUVIUSZ                            ║
║  Zaadaptowano z Kingdom Pixel (autor: Jack) — logika bez zmian                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

────────────────────────────── METRYCZKA ──────────────────────────────
| Pole                | Wartość                                                      |
|---------------------|--------------------------------------------------------------|
| ID                  | N-VIZ-001  (nowa kategoria VIZ — do potwierdzenia w ZBADANE) |
| Nazwa oryginalna    | Cartographer (oryginał Kingdom Pixel)                       |
| Nazwa w Imperium    | Kartograf                                                    |
| Lokalizacja         | DOKUMENTACJA TECHNICZNA/VIZ-001_Kartograf.py                |
| Kategoria           | VIZ / Wizualizacja wyników (PNG)                            |
| Wpływ na Imperium   | OCZY KOMENDANTA: rysuje cenę + EMA + wejścia/wyjścia +       |
|                     | krzywą kapitału. Plik PNG do otwarcia jednym kliknięciem.   |
| Powiązane moduły    | N-STRAT-001 (bot), N-LOG-001 (Kronikarz), N-DATA-001        |

────────────────────────── PO CO TO (dla Komendanta) ───────────────────────────────
Opcja A z naszego menu. Po biegu bot przekazuje tu dane, a Kartograf rysuje obrazek:
górny panel = cena, linia EMA i znaczniki transakcji (zielone wejścia, czerwone
wyjścia); dolny panel = jak rósł/malał Twój kapitał. Otwierasz PNG i wszystko widać.

CHANGELOG:
  v1.0 (2026-05-28) — wykres dwupanelowy (cena+trades, krzywa kapitału), zapis PNG.
═════════════════════════════════════════════════════════════════════════════════════
"""

import os
import logging
from typing import List, Dict, Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")  # tryb bez okna (zapisujemy do pliku)
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)-7s | %(message)s')
logger = logging.getLogger("Kartograf")


def plot_run(prices: List[float], ema: List[Optional[float]], trades: List[Dict],
             equity: List[float], title: str = "Bieg paper-bota", out_path: str = "wykres_biegu.png"):
    """
    prices  : lista cen zamknięcia
    ema      : lista wartości EMA (None w okresie rozgrzewania)
    trades   : lista {entry_idx, entry_price, exit_idx, exit_price, win(bool)}
    equity   : krzywa kapitału (wartość po kolejnych krokach/transakcjach)
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), gridspec_kw={"height_ratios": [3, 1]})

    # ── Panel 1: cena + EMA + transakcje ──
    x = list(range(len(prices)))
    ax1.plot(x, prices, color="#185FA5", lw=1.3, label="Cena")
    ema_x = [i for i, v in enumerate(ema) if v is not None]
    ema_y = [v for v in ema if v is not None]
    if ema_y:
        ax1.plot(ema_x, ema_y, color="#BA7517", lw=1.8, ls="--", label="EMA")
    for t in trades:
        c_in, c_out = t["entry_idx"], t["exit_idx"]
        ax1.scatter([c_in], [t["entry_price"]], marker="^", s=90, color="#639922", edgecolor="#33500f", zorder=5)
        ax1.scatter([c_out], [t["exit_price"]], marker="v", s=90,
                    color="#639922" if t.get("win") else "#E24B4A", edgecolor="#333", zorder=5)
        ax1.plot([c_in, c_out], [t["entry_price"], t["exit_price"]],
                 color=("#639922" if t.get("win") else "#E24B4A"), lw=0.8, alpha=0.6)
    ax1.set_title(title, fontsize=13, fontweight="bold")
    ax1.set_ylabel("cena")
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(alpha=0.25)

    # ── Panel 2: krzywa kapitału ──
    start = equity[0] if equity else 0
    color = "#639922" if (equity and equity[-1] >= start) else "#E24B4A"
    ax2.plot(range(len(equity)), equity, color=color, lw=1.8)
    ax2.axhline(start, color="#999", ls=":", lw=1)
    ax2.fill_between(range(len(equity)), equity, start, color=color, alpha=0.15)
    ax2.set_ylabel("kapitał ($)")
    ax2.set_xlabel("transakcja →")
    ax2.grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    logger.info(f"[Kartograf] Wykres zapisany → {out_path}")
    return out_path


def main():
    logger.info("=== Kartograf v1.0 Demo (przykładowe dane — format wykresu) ===")
    rng = np.random.default_rng(2026)
    prices = [50000.0]
    for _ in range(95):
        prices.append(prices[-1] * (1 + rng.normal(0.0006, 0.018)))
    # proste EMA dla ilustracji (w produkcji z Bramy/TA-Lib)
    ema = [None] * 20 + [float(np.mean(prices[max(0, i - 20):i + 1])) for i in range(20, len(prices))]
    trades = [
        {"entry_idx": 61, "entry_price": prices[61], "exit_idx": 63, "exit_price": prices[63], "win": False},
        {"entry_idx": 64, "entry_price": prices[64], "exit_idx": 71, "exit_price": prices[71], "win": False},
        {"entry_idx": 75, "entry_price": prices[75], "exit_idx": 92, "exit_price": prices[92], "win": False},
    ]
    equity = [50.0, 48.25, 45.98, 45.16]  # przykładowa krzywa kapitału
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wykres_przyklad.png")
    plot_run(prices, ema, trades, equity, title="Przykład: Pierwszy Zwiadowca (paper)", out_path=out)
    print("\n✅ Kartograf v1.0 — demo zakończone. Otwórz wykres_przyklad.png.")


if __name__ == "__main__":
    main()
