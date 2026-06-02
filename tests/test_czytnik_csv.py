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
