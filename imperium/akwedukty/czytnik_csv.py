"""
📜 CZYTNIK CSV — wczytuje historyczne dane rynkowe do barów Imperium.

Format docelowy: CryptoDataDownload (Binance export), np.:

    https://www.CryptoDataDownload.com          ← linia 1 (URL, pomijana)
    Unix,Date,Symbol,Open,High,Low,Close,Volume BTC,Volume USDT,tradecount
    1779840000000,2026-05-27,BTCUSDT,75930.01,...,16877.77,1270680262.9,3367068
    ...                                          ← dane MALEJĄCO (najnowsze na górze)

Zasady:
  • Prawo I — czytnik NIE liczy wskaźników, tylko parsuje surowe OHLCV.
  • Dane wyjściowe SĄ chronologiczne (rosnąco wg czasu) — backtest idzie od
    przeszłości do teraźniejszości, więc odwracamy malejący plik CDD.
  • Wolumen bazowy: kolumna "Volume <ASSET>" (np. Volume BTC), NIE "Volume USDT".
  • Zwraca List[dict] zgodny z BudowniczyWskaznikow i Dyrygentem.

Użycie:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    bary = wczytaj_csv("dane/godzinowe/Binance_BTCUSDT_1h.csv", interwal="1H")
    # bary[0] = najstarszy, bary[-1] = najnowszy
"""

import csv
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("CzytnikCSV")

# Nagłówki CryptoDataDownload (wielkość liter ignorowana przy dopasowaniu)
_KOL_UNIX = "unix"
_KOL_TIMESTAMP = "timestamp"   # prosty format Imperium (ISO-data lub epoch)
_KOL_DATE = "date"
_KOL_SYMBOL = "symbol"
_KOL_OPEN = "open"
_KOL_HIGH = "high"
_KOL_LOW = "low"
_KOL_CLOSE = "close"
_KOL_VOL_QUOTE = "volume usdt"   # wolumen w USDT — NIE używamy jako 'volume'
_KOL_TRADES = "tradecount"


def _znajdz_naglowek(plik) -> tuple:
    """
    Pomija ewentualną linię URL i zwraca (lista_kolumn_lower, reader_ustawiony_na_dane).
    CryptoDataDownload zaczyna od linii z 'http' — wtedy nagłówek jest w 2. linii.
    """
    pierwszy = plik.readline()
    if pierwszy.strip().lower().startswith("http"):
        linia_naglowka = plik.readline()
    else:
        linia_naglowka = pierwszy
    kolumny = [k.strip().lower() for k in linia_naglowka.rstrip("\n").split(",")]
    return kolumny


def _parse_ts(surowy: str) -> int:
    """
    Parsuje znacznik czasu na epoch w milisekundach.

    Obsługuje:
      • epoch (sekundy lub milisekundy) jako liczba — format CryptoDataDownload,
      • ISO-datę ('2026-05-15 17:10:21.514319+00:00') — prosty format Imperium.

    Heurystyka epoch: > 1e14 → MIKROsekundy (÷1000), > 1e12 → ms, inaczej sekundy.
    (CryptoDataDownload od ~2025 miesza w plikach 1h wiersze w µs i ms — realny
    brud danych wykryty 2026-06-10: ~700 wierszy/parę z unixem ×1000 za dużym.)
    """
    surowy = surowy.strip()
    try:
        liczba = float(surowy)
        if liczba > 1e14:        # mikrosekundy (brud CDD)
            return int(liczba / 1000)
        return int(liczba) if liczba > 1e12 else int(liczba * 1000)
    except ValueError:
        pass
    # ISO-data → epoch ms (UTC). 'Z' normalizujemy do +00:00.
    iso = surowy.replace("Z", "+00:00")
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def _indeks_wolumenu_bazowego(kolumny: List[str]) -> Optional[int]:
    """
    Wolumen bazowy = kolumna 'Volume <ASSET>' (np. 'volume btc'), różna od 'volume usdt'.
    Zwraca indeks lub None.
    """
    for i, k in enumerate(kolumny):
        if k.startswith("volume") and k != _KOL_VOL_QUOTE:
            return i
    return None


def wczytaj_csv(sciezka: str, interwal: str = "",
                limit: Optional[int] = None,
                chronologicznie: bool = True) -> List[Dict[str, Any]]:
    """
    Wczytuje plik CSV CryptoDataDownload → lista barów OHLCV.

    sciezka:        ścieżka do pliku .csv
    interwal:       etykieta interwału dopisywana do każdego baru ("1H", "1D"...)
    limit:          jeśli podany, zwraca tylko ostatnie N barów (po sortowaniu chronologicznym)
    chronologicznie: True = bary[0] najstarszy, bary[-1] najnowszy (domyślnie)

    Zwraca: List[dict] z kluczami:
        timestamp (int, ms), open, high, low, close, volume (bazowy),
        volume_quote (USDT), symbol, interwal, tradecount
    """
    if not os.path.exists(sciezka):
        raise FileNotFoundError(f"Brak pliku danych: {sciezka}")

    with open(sciezka, encoding="utf-8") as f:
        kolumny = _znajdz_naglowek(f)

        # Mapa nazwa_kolumny → indeks
        idx = {k: i for i, k in enumerate(kolumny)}
        # Kolumna czasu: 'unix' (CryptoDataDownload) LUB 'timestamp' (prosty format).
        i_czas = idx.get(_KOL_UNIX, idx.get(_KOL_TIMESTAMP))
        wymagane = [_KOL_OPEN, _KOL_HIGH, _KOL_LOW, _KOL_CLOSE]
        brakujace = [k for k in wymagane if k not in idx]
        if i_czas is None:
            brakujace.insert(0, f"{_KOL_UNIX}|{_KOL_TIMESTAMP}")
        if brakujace:
            raise ValueError(f"CSV {sciezka} — brak wymaganych kolumn: {brakujace} "
                             f"(znalezione: {kolumny})")

        i_vol = _indeks_wolumenu_bazowego(kolumny)
        i_vol_quote = idx.get(_KOL_VOL_QUOTE)
        i_sym = idx.get(_KOL_SYMBOL)
        i_trades = idx.get(_KOL_TRADES)
        # Brak kolumny 'symbol' (prosty format) → wywnioskuj z nazwy pliku.
        # Symbol to segment PRZED interwałem: 'BTC_1h'→'BTC', 'Binance_BTCUSDT_1h'→'BTCUSDT'.
        _czesci = os.path.splitext(os.path.basename(sciezka))[0].split("_")
        symbol_z_pliku = (_czesci[-2] if len(_czesci) >= 2 else _czesci[0]).upper()

        bary: List[Dict[str, Any]] = []
        reader = csv.reader(f)
        for wiersz in reader:
            if not wiersz or len(wiersz) <= max(i_czas, idx[_KOL_CLOSE]):
                continue
            try:
                bar = {
                    "timestamp": _parse_ts(wiersz[i_czas]),
                    "open":  float(wiersz[idx[_KOL_OPEN]]),
                    "high":  float(wiersz[idx[_KOL_HIGH]]),
                    "low":   float(wiersz[idx[_KOL_LOW]]),
                    "close": float(wiersz[idx[_KOL_CLOSE]]),
                    "volume": float(wiersz[i_vol]) if i_vol is not None else 0.0,
                    "volume_quote": float(wiersz[i_vol_quote]) if i_vol_quote is not None else 0.0,
                    "symbol": wiersz[i_sym] if i_sym is not None else symbol_z_pliku,
                    "interwal": interwal,
                    "tradecount": int(float(wiersz[i_trades])) if i_trades is not None and wiersz[i_trades] else 0,
                }
            except (ValueError, IndexError) as e:
                logger.debug(f"[CzytnikCSV] pominięto wiersz: {e}")
                continue
            bary.append(bar)

    # Deduplikacja po timestamp (wiersze µs po normalizacji dublują świece ms;
    # zostaje OSTATNI wpis = nowszy w pliku CDD). Potem sort rosnąco.
    unikalne = {}
    for b in bary:
        unikalne[b["timestamp"]] = b
    bary = list(unikalne.values())
    # CryptoDataDownload jest malejąco → sortuj rosnąco po czasie
    if chronologicznie:
        bary.sort(key=lambda b: b["timestamp"])

    if limit is not None and limit > 0:
        bary = bary[-limit:] if chronologicznie else bary[:limit]

    logger.info(f"[CzytnikCSV] {sciezka}: wczytano {len(bary)} barów "
                f"({interwal or 'brak interwału'})")
    return bary
