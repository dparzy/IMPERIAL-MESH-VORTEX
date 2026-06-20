"""
🏛️ START.PY — Najprostsze uruchomienie Imperium (PAPER TRADING).

Dla nowicjusza: to symulacja. ZERO prawdziwych pieniędzy. Tu zaczynasz.

JAK URUCHOMIĆ (z głównego folderu imperial-mesh-vortex):
    python skrypty/start.py

ZATRZYMANIE: naciśnij Ctrl+C w terminalu.

PO URUCHOMIENIU: otwórz w przeglądarce http://localhost:8777
"""

import logging

# Logi w terminalu (żebyś widział co rój robi)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)

from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live


# ─── USTAWIENIA — tu zmieniasz co chcesz ─────────────────────────────────────

cfg = KonfigPetliLive(
    # Pary które śledzisz (możesz dodać/usunąć):
    symbole=["BTCUSDT", "ETHUSDT"],

    # Interwał świec: "1m","5m","15m","30m","1H","2H","4H","6H","1D"
    interwal="1H",

    # Wirtualny kapitał (paper — nie prawdziwy):
    kapital_startowy=10_000.0,

    # SYMULACJA — zostaw True dopóki nie wiesz dokładnie co robisz:
    paper=True,

    # Panel webowy na http://localhost:8777
    dashboard=True,
)


# ─── URUCHOMIENIE ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("🏛️  IMPERIUM — PAPER TRADING (symulacja)")
    print("=" * 60)
    print(f"   Pary:     {cfg.symbole}")
    print(f"   Interwał: {cfg.interwal}")
    print(f"   Kapitał:  {cfg.kapital_startowy:,.0f} USDT (wirtualny)")
    print(f"   Panel:    http://localhost:{cfg.dashboard_port}")
    print("=" * 60)
    print("   Zatrzymanie: Ctrl+C")
    print("=" * 60)

    try:
        handluj_live(cfg)
    except KeyboardInterrupt:
        print("\n👋 Zatrzymano. Do zobaczenia, Cezarze.")
