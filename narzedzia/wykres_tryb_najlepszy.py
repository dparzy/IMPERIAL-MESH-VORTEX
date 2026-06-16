"""
Wykres „Tryb Najlepszy" (W-317..W-319) — jak wygląda pełny stack.
Liczby z docs/TRYBY_IMPERIUM.md (backtest 9 lat, 5 walut). Prawo I.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(17, 6))

# ── Panel 1: budowa stacku → kapitał końcowy (start 10k) ──
etapy = ["BASELINE\n(każda para)", "TOP-2\n+filtr", "TOP-3\n+Conviction",
         "+Compounding\n(W-319)"]
kapital = [62659, 34032, 74782, 902295]
kolory = ["#7f8c8d", "#e67e22", "#2980b9", "#27ae60"]
b = ax1.bar(etapy, kapital, color=kolory, edgecolor="black")
ax1.set_yscale("log")
ax1.axhline(10000, color="red", ls="--", lw=1, label="start 10 000$")
ax1.set_ylabel("Kapitał końcowy $ (log)", fontsize=11)
ax1.set_title("Budowa Trybu Najlepszego (9 lat, 5 par)\n"
              "selekcja + conviction + składanie", fontsize=11.5)
for bar, k in zip(b, kapital):
    mult = k / 10000
    ax1.text(bar.get_x() + bar.get_width() / 2, k * 1.1,
             f"{k:,.0f}$\n({mult:.1f}x)", ha="center", fontsize=9, fontweight="bold")
ax1.legend(fontsize=9)
ax1.grid(True, axis="y", alpha=0.3)

# ── Panel 2: rozkład PnL per coin (BASELINE) — gruby ogon ──
coiny = ["DOGE", "ETH", "BTC", "SOL", "BNB"]
pnl_coin = [52327, 545, 194, 47, -324]
kol2 = ["#27ae60" if p > 0 else "#c0392b" for p in pnl_coin]
b2 = ax2.bar(coiny, pnl_coin, color=kol2, edgecolor="black")
ax2.axhline(0, color="black", lw=1)
ax2.set_ylabel("PnL $ (baseline)", fontsize=11)
ax2.set_title("Zysk jest GRUBO-OGONOWY: DOGE = ~99%\n"
              "(meme/alt pumpy tworzą prawie cały wynik)", fontsize=11.5)
for bar, p in zip(b2, pnl_coin):
    ax2.text(bar.get_x() + bar.get_width() / 2, p + 1500,
             f"+{p:,}" if p > 0 else f"{p:,}", ha="center", fontsize=9)
ax2.grid(True, axis="y", alpha=0.3)

# ── Panel 3: uczciwy reframe — 90.2x to artefakt okna ──
okna = ["Pełne 9 lat\n(z DOGE 2021)", "Ostatnie 3.4 lat\n(bez pompy DOGE)"]
mult = [90.2, 1.06]
b3 = ax3.bar(okna, mult, color=["#27ae60", "#e67e22"], edgecolor="black")
ax3.axhline(1.0, color="red", ls="--", lw=1, label="bez zysku (1.0x)")
ax3.set_ylabel("Mnożnik kapitału", fontsize=11)
ax3.set_title("90.2x to ARTEFAKT pompy DOGE 2021\n"
              "ten sam stack na świeższym oknie: 1.06x (+5.8%)", fontsize=11.5)
for bar, m in zip(b3, mult):
    ax3.text(bar.get_x() + bar.get_width() / 2, m + 1.5,
             f"{m:.2f}x", ha="center", fontsize=11, fontweight="bold")
ax3.legend(fontsize=9)
ax3.grid(True, axis="y", alpha=0.3)

fig.suptitle("IMPERIUM — TRYB NAJLEPSZY (pełny stack 4h): jak wygląda (Prawo I)",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig("docs/wykres_tryb_najlepszy.png", dpi=130)
print("zapisano docs/wykres_tryb_najlepszy.png")
