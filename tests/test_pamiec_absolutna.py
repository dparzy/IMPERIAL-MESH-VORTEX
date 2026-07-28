

# ── Symbol w nazwie pliku: notacja ccxt nie może rozjechać ścieżki (2026-07-29) ──

def test_symbol_ccxt_nie_rozjezdza_sciezki():
    """
    Zmierzone: `BTC/USDT:USDT` (notacja kontraktów ccxt — używają jej adaptery giełdowe)
    dawało ścieżkę `logs/2026/07/2026-07-28_BTC/USDT:USDT_trade_close.jsonl` →
    FileNotFoundError. Wada spała, dopóki do W1 pisała tylko jedna ścieżka; w żywym
    paper-tradingu wywróciłaby DOMYKANIE pozycji.
    """
    import tempfile
    from pathlib import Path

    from imperium.biblioteki.pamiec_absolutna import ImperiumLog, PamiecAbsolutna, TypLogu

    kat = Path(tempfile.mkdtemp())
    pam = PamiecAbsolutna(katalog=kat)
    pam.zapisz(ImperiumLog(log_typ=TypLogu.TRADE_CLOSE, sesja_id="S1",
                           symbol="BTC/USDT:USDT", interwal="4H", pnl_usdt=1.0))

    pliki = list(kat.rglob("*.jsonl"))
    assert len(pliki) == 1
    assert "/" not in pliki[0].name and ":" not in pliki[0].name


def test_odczyt_po_symbolu_ccxt_znajduje_wlasny_plik():
    """GRANICA drugiej strony: zapis sanityzuje, więc odczyt MUSI sanityzować tak samo."""
    import tempfile
    from pathlib import Path

    from imperium.biblioteki.pamiec_absolutna import ImperiumLog, PamiecAbsolutna, TypLogu

    kat = Path(tempfile.mkdtemp())
    pam = PamiecAbsolutna(katalog=kat)
    pam.zapisz(ImperiumLog(log_typ=TypLogu.TRADE_CLOSE, sesja_id="S1",
                           symbol="BTC/USDT:USDT", interwal="4H", pnl_usdt=1.0))

    assert len(pam.wczytaj(symbol="BTC/USDT:USDT")) == 1     # dane są I widać je
    assert len(pam.wczytaj(symbol="ETH/USDT:USDT")) == 0     # filtr nadal filtruje
