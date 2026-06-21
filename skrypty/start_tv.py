"""
📡 START_TV.PY — Imperium + TradingView na żywo (PAPER TRADING + webhook).

Dla nowicjusza: to symulacja Z sygnałami z TradingView. Nadal ZERO prawdziwych pieniędzy.

ZANIM URUCHOMISZ — ustaw hasło webhooka (raz):
    Windows:   setx WEBHOOK_TV_SEKRET "mojeTajneHaslo123"   (potem nowy terminal)
    Mac/Linux: export WEBHOOK_TV_SEKRET="mojeTajneHaslo123"

JAK URUCHOMIĆ (z głównego folderu):
    python skrypty/start_tv.py

POTEM (drugi terminal):
    ngrok http 8777
    → skopiuj adres https://....ngrok-free.app i wklej w TradingView Alert
      jako Webhook URL z dopiskiem /webhook/tv

PANEL: http://localhost:8777  (tam jest gotowy szablon dla TradingView)
ZATRZYMANIE: Ctrl+C
"""

import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)

from imperium.koloseum.petla_live import KonfigPetliLive, handluj_live


# ─── USTAWIENIA ───────────────────────────────────────────────────────────────

cfg = KonfigPetliLive(
    symbole=["BTCUSDT", "ETHUSDT"],
    interwal="1H",
    kapital_startowy=10_000.0,
    paper=True,            # SYMULACJA
    dashboard=True,        # panel webowy — MUSI być True dla webhooka
    webhook_tv=True,       # odbiornik TradingView
)


# ─── URUCHOMIENIE ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sekret = os.getenv("WEBHOOK_TV_SEKRET")

    print("=" * 60)
    print("📡  IMPERIUM + TRADINGVIEW (paper + webhook)")
    print("=" * 60)
    print(f"   Pary:     {cfg.symbole}")
    print(f"   Panel:    http://localhost:{cfg.dashboard_port}")
    print(f"   Webhook:  http://localhost:{cfg.dashboard_port}/webhook/tv")
    if sekret:
        print(f"   Sekret:   ustawiony ✅ (WEBHOOK_TV_SEKRET)")
    else:
        print("   Sekret:   ⚠️  BRAK! Ustaw WEBHOOK_TV_SEKRET w środowisku")
        print("             (bez niego każdy może wysłać fałszywy sygnał)")
    print("=" * 60)
    print("   Następny krok (drugi terminal):  ngrok http 8777")
    print("   Zatrzymanie: Ctrl+C")
    print("=" * 60)

    try:
        handluj_live(cfg)
    except KeyboardInterrupt:
        print("\n👋 Zatrzymano. Do zobaczenia, Cezarze.")
