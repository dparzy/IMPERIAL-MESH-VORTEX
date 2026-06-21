"""
🧠 START_UCZENIE.PY — Imperium z pełnym uczeniem (PAPER + wszystkie warstwy adaptacyjne).

Dla nowicjusza: to samo paper trading, ale z włączonym uczeniem roju. System
zapamiętuje co działa w danym reżimie rynku i adaptuje wagi neuronów między sesjami.
Nadal ZERO prawdziwych pieniędzy. Używaj gdy już rozumiesz podstawy (start.py).

JAK URUCHOMIĆ:
    python skrypty/start_uczenie.py

CO ROBIĄ WARSTWY UCZENIA:
    synapsy   — pamięć reżimowa (co działa w TREND vs RANGING vs PANIC)
    mwu       — online uczenie wag neuronów (po każdym trade)
    igrzyska  — ranking neuronów po skuteczności
    ksiega_wad— filtr wad setupu z poprzednich błędów

PANEL: http://localhost:8777    ZATRZYMANIE: Ctrl+C
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)

from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live


cfg = KonfigPetliLive(
    symbole=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
    interwal="4H",
    kapital_startowy=10_000.0,
    paper=True,

    # ── Warstwy uczenia (pełna moc adaptacji) ──
    synapsy=True,          # pamięć reżimowa per para
    mwu=True,              # online uczenie wag (HedgeMWU)
    igrzyska=True,         # ranking neuronów po accuracy
    ksiega_wad=True,       # filtr wad setupu
    filtr_asymetrii=True,  # weto na rynku bocznym/kontr-trendzie

    # ── Widoczność ──
    dashboard=True,        # panel webowy
    monitor=True,          # panel TUI w terminalu
)


if __name__ == "__main__":
    print("=" * 60)
    print("🧠  IMPERIUM — PEŁNE UCZENIE (paper + adaptacja)")
    print("=" * 60)
    print(f"   Pary:     {cfg.symbole}")
    print(f"   Uczenie:  synapsy + mwu + igrzyska + ksiega_wad")
    print(f"   Panel:    http://localhost:{cfg.dashboard_port}")
    print("=" * 60)
    print("   Stan uczenia zapisuje się w logs/ (cross-session)")
    print("   Zatrzymanie: Ctrl+C")
    print("=" * 60)

    try:
        handluj_live(cfg)
    except KeyboardInterrupt:
        print("\n👋 Zatrzymano. Stan uczenia zapisany. Do zobaczenia, Cezarze.")
