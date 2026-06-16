"""
Wykresy kalibracji 1h (W-321c) — wizualizacja zamiast samych tabel.
Generuje PNG: (1) selektywność→rentowność, (2) porównanie TF na tym samym oknie.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Komplet 14 konfiguracji 1h (okno ~1.4 lat, cap 12k): (adx, pew, topn, trades, wr, pnl%)
DANE = [
    (20, 0.55, 3, 929, 46.8, -12.8),  # baseline
    (20, 0.65, 3, 922, 46.5, -12.5),
    (28, 0.55, 3, 769, 45.6, -10.1),
    (28, 0.65, 3, 754, 45.2, -10.1),
    (28, 0.65, 2, 694, 45.8,  -9.4),
    (36, 0.55, 3, 487, 43.7,  -9.3),
    (36, 0.65, 3, 480, 42.9, -10.7),
    (36, 0.70, 2, 430, 44.2,  -6.4),
    (36, 0.75, 1, 337, 40.4, -11.2),
    (45, 0.70, 2, 217, 41.9,  -5.9),
    (45, 0.70, 1, 172, 41.9,  -6.5),
    (50, 0.75, 1,  94, 42.6,  -3.4),
    (55, 0.75, 1,  62, 46.8,  -2.6),
    (60, 0.75, 1,  27, 48.1,  -2.5),
]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.2))

# ── Panel 1: selektywność (liczba trade'ów) → rentowność, kolor = ADX ──
trades = [d[3] for d in DANE]
pnl = [d[5] for d in DANE]
adx = [d[0] for d in DANE]
sc = ax1.scatter(trades, pnl, c=adx, s=130, cmap="viridis",
                 edgecolors="black", linewidths=0.6, zorder=3)
ax1.axhline(0, color="green", lw=1.4, ls="--", label="próg rentowności (0%)")
ax1.set_xscale("log")
ax1.set_xlabel("Liczba trade'ów (skala log) — mniej = ostrzejszy filtr →", fontsize=11)
ax1.set_ylabel("PnL %", fontsize=11)
ax1.set_title("1h: skrajna selektywność dociska stratę, ale NIE przekracza zera\n"
              "(asymptota ~−2.5%, gradient się wypłaszcza)", fontsize=11.5)
cbar = fig.colorbar(sc, ax=ax1)
cbar.set_label("min ADX (siła trendu)", fontsize=10)
# adnotacje kluczowych punktów
ax1.annotate("baseline (config 4h)\nadx20 top3: −12.8%", (929, -12.8),
             textcoords="offset points", xytext=(-10, 14), fontsize=8.5,
             ha="center", arrowprops=dict(arrowstyle="->", color="gray"))
ax1.annotate("najlepszy: adx60 top1\n−2.5% (tylko 27 tr = szum)", (27, -2.5),
             textcoords="offset points", xytext=(35, -32), fontsize=8.5,
             arrowprops=dict(arrowstyle="->", color="gray"))
ax1.grid(True, alpha=0.3)
ax1.legend(loc="lower right", fontsize=9)

# ── Panel 2: TF na tym samym oknie 2022→2026 (~3.4 lat) ──
tf_label = ["4h\n(722 tr)", "1h\n(2347 tr)"]
tf_pnl = [5.8, -9.8]
kolory = ["#2a9d4f" if p > 0 else "#c0392b" for p in tf_pnl]
bary = ax2.bar(tf_label, tf_pnl, color=kolory, edgecolor="black", width=0.55)
ax2.axhline(0, color="black", lw=1)
ax2.set_ylabel("PnL %", fontsize=11)
ax2.set_title("Pełny stack na TYM SAMYM oknie (2022→2026, ~3.4 lat)\n"
              "4h dodatni, 1h ujemny — interwał, nie tylko okno", fontsize=11.5)
for b, p in zip(bary, tf_pnl):
    ax2.text(b.get_x() + b.get_width() / 2, p + (0.4 if p > 0 else -0.9),
             f"{p:+.1f}%", ha="center", fontsize=12, fontweight="bold")
ax2.text(0.5, 0.92, "(90.2x na pełnych 9 latach = artefakt pompy DOGE 2021,\n"
         "nie powtarzalna przewaga)", transform=ax2.transAxes, ha="center",
         fontsize=8.5, style="italic", color="gray")
ax2.grid(True, axis="y", alpha=0.3)

fig.suptitle("IMPERIUM W-321c — kalibracja 1h vs 4h (Prawo I: zmierzone, nie zgadnięte)",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("docs/wykres_kalibracja_1h.png", dpi=130)
print("zapisano docs/wykres_kalibracja_1h.png")
