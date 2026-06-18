"""Testy LiveMonitor i TelegramAlert (W-341, Prawo XXIV)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.swiatynie.live_monitor import (
    LiveMonitor, TelegramAlert, StanDashboardu, StanPozycji, StanNeuronu,
    _pasek,
)


def _bez_ansi(tekst: str) -> str:
    """Usuń escape codes ANSI z tekstu."""
    import re
    return re.sub(r"\033\[[0-9;]*m", "", tekst)


def test_pasek_pelny():
    assert _pasek(1.0, 10) == "██████████"


def test_pasek_pusty():
    assert _pasek(0.0, 10) == "░░░░░░░░░░"


def test_pasek_polowa():
    p = _pasek(0.5, 10)
    assert p == "█████░░░░░"


def test_pasek_granica_powyzej_jeden():
    p = _pasek(1.5, 8)
    assert p == "████████"


def test_pasek_granica_ponizej_zero():
    p = _pasek(-0.1, 8)
    assert p == "░░░░░░░░"


def test_stan_pozycji_long_pnl():
    p = StanPozycji("BTC", "LONG", 100.0, 110.0, 1000.0)
    assert abs(p.pnl_pct - 0.10) < 1e-9


def test_stan_pozycji_short_pnl():
    p = StanPozycji("ETH", "SHORT", 100.0, 90.0, 500.0)
    assert abs(p.pnl_pct - 0.10) < 1e-9


def test_stan_pozycji_wejscie_zero():
    p = StanPozycji("SOL", "LONG", 0.0, 100.0, 100.0)
    assert p.pnl_pct == 0.0


def test_live_monitor_render_nie_crashuje():
    monitor = LiveMonitor()
    stan = StanDashboardu(
        symbol="BTCUSDT",
        rezim="TREND_STRONG",
        kierunek_legatus="LONG",
        pewnosc=0.75,
        kapital=10000.0,
        kapital_start=10000.0,
    )
    monitor.aktualizuj(stan)
    import io
    from unittest.mock import patch
    with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
        monitor.render(clear=False)
        output = mock_out.getvalue()
    clean = _bez_ansi(output)
    assert "IMPERIAL MESH VORTEX" in clean
    assert "TREND_STRONG" in clean
    assert "LONG" in clean


def test_live_monitor_pokazuje_kapital():
    monitor = LiveMonitor()
    stan = StanDashboardu(kapital=52980.0, kapital_start=50000.0)
    monitor.aktualizuj(stan)
    import io
    from unittest.mock import patch
    with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
        monitor.render(clear=False)
        output = mock_out.getvalue()
    clean = _bez_ansi(output)
    assert "52,980" in clean


def test_live_monitor_pokazuje_neurony():
    monitor = LiveMonitor()
    stan = StanDashboardu(
        neurony_top=[
            StanNeuronu("X-01", "LONG", 0.82, 8.0),
            StanNeuronu("Z-01", "NEUTRAL", 0.0, 5.0),
        ]
    )
    monitor.aktualizuj(stan)
    import io
    from unittest.mock import patch
    with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
        monitor.render(clear=False)
        output = mock_out.getvalue()
    clean = _bez_ansi(output)
    assert "X-01" in clean
    assert "Z-01" in clean


def test_live_monitor_pokazuje_pozycje():
    monitor = LiveMonitor()
    stan = StanDashboardu(
        pozycje=[StanPozycji("ETHUSDT", "SHORT", 3500.0, 3400.0, 1000.0)]
    )
    monitor.aktualizuj(stan)
    import io
    from unittest.mock import patch
    with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
        monitor.render(clear=False)
        output = mock_out.getvalue()
    clean = _bez_ansi(output)
    assert "ETHUSDT" in clean
    assert "SHORT" in clean


def test_telegram_alert_bez_kluczy_nie_crashuje():
    ta = TelegramAlert()
    assert ta.aktywny is False
    # Nie wysyła, nie crashuje — zwraca False
    assert ta.wyslij("test") is False
    assert ta.alert_sygnal("BTC", "LONG", 0.8, "TREND_STRONG", 10000.0) is False
    assert ta.alert_zamkniecie("BTC", 0.05, 10500.0) is False
    assert ta.alert_weto("panika", "PANIC") is False
    assert ta.alert_blad("błąd krytyczny") is False


def test_telegram_alert_aktywny_z_kluczami():
    stary_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    stary_chat = os.environ.get("TELEGRAM_CHAT_ID")
    os.environ["TELEGRAM_BOT_TOKEN"] = "fake_token"
    os.environ["TELEGRAM_CHAT_ID"] = "123456"
    try:
        ta = TelegramAlert()
        assert ta.aktywny is True
    finally:
        if stary_token is None:
            os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        else:
            os.environ["TELEGRAM_BOT_TOKEN"] = stary_token
        if stary_chat is None:
            os.environ.pop("TELEGRAM_CHAT_ID", None)
        else:
            os.environ["TELEGRAM_CHAT_ID"] = stary_chat


def test_stan_dashboardu_domyslny():
    s = StanDashboardu()
    assert s.pozycje == []
    assert s.neurony_top == []
    assert s.pewnosc == 0.0
    assert s.bary_przetworzone == 0
