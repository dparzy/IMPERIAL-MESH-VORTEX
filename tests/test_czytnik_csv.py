"""
Testy czytnika CSV — parsowanie danych CryptoDataDownload do barów Imperium.
Używa małej próbki inline (bez zależności od dużych plików danych).
"""

import os
import tempfile

from imperium.akwedukty.czytnik_csv import wczytaj_csv

# Próbka w formacie CryptoDataDownload: linia URL + nagłówek + 3 wiersze MALEJĄCO
PROBKA = """https://www.CryptoDataDownload.com
Unix,Date,Symbol,Open,High,Low,Close,Volume BTC,Volume USDT,tradecount
1502928000002,2017-08-19,BTCUSDT,4300.0,4400.0,4250.0,4380.0,100.5,440000.0,300
1502928000001,2017-08-18,BTCUSDT,4285.0,4320.0,4260.0,4300.0,90.0,387000.0,250
1502928000000,2017-08-17,BTCUSDT,4261.48,4485.39,4200.74,4285.08,795.15,3454770.05,3427
"""


def _zapisz_probke(tekst=PROBKA):
    f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    f.write(tekst)
    f.close()
    return f.name


def test_wczytaj_podstawowy():
    p = _zapisz_probke()
    try:
        bary = wczytaj_csv(p, interwal="1D")
        assert len(bary) == 3
        # Klucze OHLCV obecne
        for k in ("timestamp", "open", "high", "low", "close", "volume", "symbol", "interwal"):
            assert k in bary[0], f"brak klucza {k}"
    finally:
        os.unlink(p)


def test_chronologia_rosnaca():
    """Plik CDD jest malejąco — czytnik musi odwrócić na rosnąco."""
    p = _zapisz_probke()
    try:
        bary = wczytaj_csv(p, interwal="1D")
        assert bary[0]["timestamp"] < bary[-1]["timestamp"]
        # Najstarszy = 2017-08-17 (open 4261.48)
        assert bary[0]["open"] == 4261.48
        # Najnowszy = 2017-08-19 (close 4380.0)
        assert bary[-1]["close"] == 4380.0
    finally:
        os.unlink(p)


def test_wolumen_bazowy_nie_quote():
    """volume = Volume BTC (bazowy), nie Volume USDT."""
    p = _zapisz_probke()
    try:
        bary = wczytaj_csv(p, interwal="1D")
        najstarszy = bary[0]
        assert najstarszy["volume"] == 795.15        # Volume BTC
        assert najstarszy["volume_quote"] == 3454770.05  # Volume USDT
    finally:
        os.unlink(p)


def test_interwal_dopisany():
    p = _zapisz_probke()
    try:
        bary = wczytaj_csv(p, interwal="1H")
        assert all(b["interwal"] == "1H" for b in bary)
    finally:
        os.unlink(p)


def test_limit_zwraca_najnowsze():
    p = _zapisz_probke()
    try:
        bary = wczytaj_csv(p, interwal="1D", limit=2)
        assert len(bary) == 2
        # limit + chronologicznie = ostatnie 2 (najnowsze)
        assert bary[-1]["close"] == 4380.0
        assert bary[0]["close"] == 4300.0
    finally:
        os.unlink(p)


def test_brak_pliku_rzuca():
    try:
        wczytaj_csv("nie_istnieje_xyz.csv")
        assert False, "powinien rzucić FileNotFoundError"
    except FileNotFoundError:
        pass


# Prosty format Imperium: nagłówek 'timestamp' + ISO-data (rosnąco, jak dane/*.csv)
PROBKA_PROSTA = """timestamp,open,high,low,close,volume
2026-05-19 21:10:21.521895+00:00,3000.0,3022.7,2997.6,3010.0,83.5
2026-05-19 22:10:21.521895+00:00,3010.0,3025.0,3005.0,3018.0,67.6
2026-05-19 23:10:21.521895+00:00,3018.0,3040.0,3015.0,3035.0,71.2
"""


def test_prosty_format_timestamp_iso():
    """Prosty format 'timestamp,open,...' z ISO-datą — backtest na dołączonych danych."""
    p = _zapisz_probke(PROBKA_PROSTA)
    try:
        bary = wczytaj_csv(p, interwal="1H")
        assert len(bary) == 3
        assert bary[0]["open"] == 3000.0
        assert bary[-1]["close"] == 3035.0
        # ISO-data sparsowana na epoch ms (dodatnia, monotoniczna)
        assert bary[0]["timestamp"] > 0
        assert bary[0]["timestamp"] < bary[-1]["timestamp"]
    finally:
        os.unlink(p)


def test_prosty_format_symbol_z_nazwy_pliku():
    """Brak kolumny 'symbol' → symbol z segmentu PRZED interwałem w nazwie pliku."""
    import tempfile as _tf
    katalog = _tf.mkdtemp()
    # Dwa formaty nazw: 'BTC_1h.csv' → BTC, 'Binance_BTCUSDT_1h.csv' → BTCUSDT
    for nazwa, oczekiwany in [("BTC_1h.csv", "BTC"), ("Binance_BTCUSDT_1h.csv", "BTCUSDT")]:
        sciezka = os.path.join(katalog, nazwa)
        with open(sciezka, "w", encoding="utf-8") as fh:
            fh.write(PROBKA_PROSTA)
        bary = wczytaj_csv(sciezka, interwal="1H")
        assert bary[0]["symbol"] == oczekiwany, f"{nazwa} → {bary[0]['symbol']} ≠ {oczekiwany}"
        os.unlink(sciezka)
    os.rmdir(katalog)


def test_parse_ts_epoch_i_iso():
    """_parse_ts: epoch sekund, epoch ms i ISO-data dają epoch ms."""
    from imperium.akwedukty.czytnik_csv import _parse_ts
    assert _parse_ts("1502928000") == 1502928000000        # sekundy → ms
    assert _parse_ts("1502928000000") == 1502928000000     # już ms
    assert _parse_ts("2017-08-17T00:00:00+00:00") == 1502928000000  # ISO UTC


def test_eth_naglowek_volume_eth():
    """Kolumna wolumenu zmienia nazwę (Volume ETH) — wykrycie po pozycji, nie nazwie stałej."""
    tekst = PROBKA.replace("Volume BTC", "Volume ETH").replace("BTCUSDT", "ETHUSDT")
    p = _zapisz_probke(tekst)
    try:
        bary = wczytaj_csv(p, interwal="1D")
        assert bary[0]["symbol"] == "ETHUSDT"
        assert bary[0]["volume"] == 795.15  # nadal wolumen bazowy (Volume ETH)
    finally:
        os.unlink(p)
