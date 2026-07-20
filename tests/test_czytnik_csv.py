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


def test_unix_mikrosekundy_normalizowane():
    """Brud CDD 2025+: unix w µs (>1e14) → ÷1000 do ms (granica heurystyki)."""
    from imperium.akwedukty.czytnik_csv import _parse_ts
    assert _parse_ts("1741734000000000") == 1741734000000   # µs → ms
    assert _parse_ts("1741734000000") == 1741734000000      # ms zostaje
    assert _parse_ts("1741734000") == 1741734000000         # s → ms


def test_duplikaty_timestamp_deduplikowane(tmp_sciezka=None):
    """Wiersze µs+ms tej samej świecy → po normalizacji zostaje jedna."""
    import tempfile, os
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    tresc = (
        "https://www.CryptoDataDownload.com\n"
        "Unix,Date,Symbol,Open,High,Low,Close,Volume BTC,Volume USDT,tradecount\n"
        "1741734000000000,2025-03-11,BTCUSDT,1,2,0.5,1.5,10,15,5\n"
        "1741734000000,2025-03-11,BTCUSDT,1,2,0.5,1.6,11,16,6\n"
        "1741737600000,2025-03-11,BTCUSDT,2,3,1.5,2.5,12,17,7\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write(tresc); sciezka = f.name
    try:
        bary = wczytaj_csv(sciezka, interwal="1H")
        assert len(bary) == 2, f"duplikat µs/ms ma zniknąć, jest {len(bary)}"
        assert bary[0]["timestamp"] == 1741734000000
    finally:
        os.unlink(sciezka)


def test_agregacja_4h_kompletne_okna():
    """Agregator 4H: OHLCV poprawne, niepełne okna odrzucone (Prawo I)."""
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "narzedzia"))
    from agreguj_4h import agreguj_4h, CZTERY_H_MS
    h = 3600 * 1000
    # 4 pełne godziny od północy + 2 luźne (niepełne okno) → 1 bar 4H
    bary = [
        {"timestamp": 0*h, "open": 10, "high": 12, "low": 9,  "close": 11, "volume": 1},
        {"timestamp": 1*h, "open": 11, "high": 15, "low": 10, "close": 14, "volume": 2},
        {"timestamp": 2*h, "open": 14, "high": 14, "low": 8,  "close": 9,  "volume": 3},
        {"timestamp": 3*h, "open": 9,  "high": 10, "low": 9,  "close": 10, "volume": 4},
        {"timestamp": 4*h, "open": 10, "high": 11, "low": 10, "close": 11, "volume": 5},
        {"timestamp": 5*h, "open": 11, "high": 12, "low": 11, "close": 12, "volume": 6},
    ]
    w = agreguj_4h(bary)
    assert len(w) == 1, "niepełne okno (2/4 barów) musi być odrzucone"
    b = w[0]
    assert b["timestamp"] == 0 and b["open"] == 10 and b["close"] == 10
    assert b["high"] == 15 and b["low"] == 8 and b["volume"] == 10
    assert CZTERY_H_MS == 4 * h


def test_realne_dane_1h_laduja_sie():
    """
    W-320 (Prawo XV/XIX): gdy dane 1h (dane/godzinowe/) są dostępne LOKALNIE, ładują się
    poprawnie — dowód, że Tryb NAJLEPSZY ma realny interwał krótszy niż 4H (priorytet Cezara).

    Dane CSV żyją POZA repo (decyzja Cezara 2026-07-04: `dane/**/*.csv` w .gitignore) —
    na świeżym klonie / CI plików nie ma, więc test pomija się (brak danych = abstynencja,
    Prawo XV; nie fałszywy czerwony — audyt K1 2026-07-11). Waliduje KAŻDY obecny plik.
    """
    import os as _os
    import sys as _sys
    katalog = _os.path.join(_os.path.dirname(__file__), "..", "dane", "godzinowe")
    pary = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
    znalezione = 0
    for para in pary:
        sciezka = _os.path.join(katalog, f"Binance_{para}_1h.csv")
        if not _os.path.exists(sciezka):
            continue
        znalezione += 1
        bary = wczytaj_csv(sciezka, interwal="1h", limit=500)
        assert len(bary) > 0, f"{para}: brak barów 1h"
        # Chronologia rosnąca + OHLC sensowne (high >= low, close > 0)
        assert bary[0]["timestamp"] < bary[-1]["timestamp"]
        for b in bary[:50]:
            assert b["high"] >= b["low"] > 0
            assert b["interwal"] == "1h"
    if znalezione == 0:
        print("  [skip] test_realne_dane_1h: brak lokalnych CSV 1h "
              "(dane poza repo — decyzja 2026-07-04)", file=_sys.stderr)


def test_agregacja_4h_luka_w_srodku():
    """Luka godzinowa w środku okna → okno 3/4 odrzucone (granica kompletności)."""
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), "..", "narzedzia"))
    from agreguj_4h import agreguj_4h
    h = 3600 * 1000
    bary = [{"timestamp": t*h, "open": 1, "high": 2, "low": 0.5, "close": 1.5,
             "volume": 1} for t in (0, 1, 3)]   # brak godziny 2
    assert agreguj_4h(bary) == []


# ── ŚWIECA NIEDOMKNIĘTA — odcinanie u źródła (2026-07-20) ─────────────────────────

def _plik_z_barami(tmpdir, znaczniki, interwal_kol="1h"):
    """Buduje mini-CSV w formacie CryptoDataDownload z podanymi znacznikami (ms)."""
    import os
    p = os.path.join(tmpdir, f"Binance_TESTUSDT_{interwal_kol}.csv")
    with open(p, "w", encoding="utf-8") as f:
        f.write("https://test\n")
        f.write("Unix,Date,Symbol,Open,High,Low,Close,Volume TEST,Volume USDT,tradecount\n")
        for ts in sorted(znaczniki, reverse=True):      # CDD zapisuje MALEJĄCO
            f.write(f"{ts},2026-01-01 00:00:00,TESTUSDT,100,110,90,105,10,1000,5\n")
    return p


def test_niedomknieta_swieca_odcieta():
    """Bar, którego okres JESZCZE TRWA, ma niepełny wolumen — nie wolno go liczyć."""
    import tempfile, time
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    teraz = int(time.time() * 1000)
    biezacy = (teraz // 3_600_000) * 3_600_000      # świeca tej godziny — wciąż się formuje
    poprzedni = biezacy - 3_600_000
    p = _plik_z_barami(tempfile.mkdtemp(), [poprzedni, biezacy])
    bary = wczytaj_csv(p, interwal="1h")
    assert len(bary) == 1, "bieżąca (niedomknięta) świeca musi zostać odcięta"
    assert bary[-1]["timestamp"] == poprzedni


def test_domknieta_swieca_zostaje():
    """Granica: bar, którego okres SIĘ SKOŃCZYŁ, zostaje nietknięty (nie tniemy historii)."""
    import tempfile, time
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    teraz = int(time.time() * 1000)
    zamkniety = (teraz // 3_600_000) * 3_600_000 - 3_600_000
    p = _plik_z_barami(tempfile.mkdtemp(), [zamkniety - 3_600_000, zamkniety])
    bary = wczytaj_csv(p, interwal="1h")
    assert len(bary) == 2, "zamknięte bary muszą zostać"
    assert bary[-1]["timestamp"] == zamkniety


def test_dane_historyczne_nietkniete():
    """Pliki historyczne (okres dawno zamknięty) — ZERO zmian zachowania."""
    import tempfile
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    stare = [1_600_000_000_000, 1_600_003_600_000, 1_600_007_200_000]
    p = _plik_z_barami(tempfile.mkdtemp(), stare)
    assert len(wczytaj_csv(p, interwal="1h")) == 3


def test_nieznany_interwal_nie_tnie():
    """Prawo I: nie znamy długości okresu → NIE zgadujemy i niczego nie odcinamy."""
    import tempfile, time
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    teraz = int(time.time() * 1000)
    biezacy = (teraz // 3_600_000) * 3_600_000
    p = _plik_z_barami(tempfile.mkdtemp(), [biezacy - 3_600_000, biezacy])
    assert len(wczytaj_csv(p, interwal="")) == 2, "bez etykiety interwału nie tniemy"
    assert len(wczytaj_csv(p, interwal="7h")) == 2, "nieznana etykieta nie tnie"


def test_flaga_wylacza_odcinanie():
    """Dźwignia ucieczki: pomin_niedomkniety=False przywraca stare zachowanie."""
    import tempfile, time
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    teraz = int(time.time() * 1000)
    biezacy = (teraz // 3_600_000) * 3_600_000
    p = _plik_z_barami(tempfile.mkdtemp(), [biezacy - 3_600_000, biezacy])
    assert len(wczytaj_csv(p, interwal="1h", pomin_niedomkniety=False)) == 2


def test_etykieta_wielkosc_liter():
    """Granica: '1H' i '1h' to ten sam interwał (mapa jest case-insensitive)."""
    import tempfile, time
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    teraz = int(time.time() * 1000)
    biezacy = (teraz // 3_600_000) * 3_600_000
    p = _plik_z_barami(tempfile.mkdtemp(), [biezacy - 3_600_000, biezacy])
    assert len(wczytaj_csv(p, interwal="1H")) == 1, "'1H' musi działać jak '1h'"
