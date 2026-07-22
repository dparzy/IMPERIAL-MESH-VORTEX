"""
🧱 CONFLATOR TEMPORUM (Zlewacz Interwałów) — AGREGATOR BARÓW: buduje wyższy interwał z niższego (1m→5m/15m, 1h→4h).

DLA NOWICJUSZA: 1 bar wyższego interwału = N kolejnych barów niższego, wyrównanych do
siatki UTC (dla 4h: 00:00, 04:00, 08:00…). open pierwszego, close ostatniego, high=max,
low=min, volume=suma. Niekompletne okna (luki w danych / końcówka) są ODRZUCANE —
niepełny bar to fałszywy bar (Prawo I).

Nazwa: wcześniej `agreguj_4h.py`. Zmieniona 2026-07-20, gdy moduł przestał dotyczyć
wyłącznie 4h — nazwa pliku też jest dokumentacją i też potrafi skłamać.

POWÓD ROZSZERZENIA (2026-07-20): mamy dane 1-minutowe (14 par, ~1450 dni), ale ZERO
plików 5m/15m — a Namiestnik (W-323) mapuje M1–M15 na profil SCALP. Czyli cały profil
SCALP nigdy nie był testowany, bo nie było na czym. Zmierzona zależność 1d +9.80% /
4h +3.93% / 1h −4.38% daje falsyfikowalną prognozę: 15m i 5m powinny wyjść JESZCZE
gorzej. Jeśli wyjdą lepiej — teza o interwale upada i trzeba ją odwołać.

Uruchom:
    python narzedzia/agreguj_bary.py --z 1h --do 4h                  # wszystkie pary
    python narzedzia/agreguj_bary.py --z 1m --do 15m --pary BTCUSDT,ETHUSDT
    python narzedzia/agreguj_bary.py --z 1m --do 5m,15m --pary BTCUSDT
"""

import argparse
import glob
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402

MINUTA_MS = 60_000
CZTERY_H_MS = 4 * 3600 * 1000          # zachowane: używa go audyt_danych.py

# etykieta → (minuty, katalog, sufiks pliku)
INTERWALY = {
    "1m":  (1,    "dane/minutowe",  "_minute"),
    "5m":  (5,    "dane/5m",        "_5m"),
    "15m": (15,   "dane/15m",       "_15m"),
    "1h":  (60,   "dane/godzinowe", "_1h"),
    "4h":  (240,  "dane/4h",        "_4h"),
    "1d":  (1440, "dane/dzienne",   "_d"),
}


def agreguj(bary: list, krok_ms: int) -> list:
    """Agreguje bary do siatki `krok_ms` (UTC). Zwraca tylko KOMPLETNE okna.

    Kompletność liczona z ILOŚCI barów w oknie — okno niepełne (luka w danych albo
    końcówka pliku) jest odrzucane, bo niepełny bar udaje pełny i fałszuje wskaźniki.
    """
    if not bary:
        return []
    krok_zrodla = min((b["timestamp"] - a["timestamp"])
                      for a, b in zip(bary, bary[1:])) if len(bary) > 1 else krok_ms
    na_okno = max(1, krok_ms // max(1, krok_zrodla))

    grupy: dict = {}
    for b in bary:
        grupy.setdefault((b["timestamp"] // krok_ms) * krok_ms, []).append(b)

    wynik = []
    for klucz in sorted(grupy):
        g = sorted(grupy[klucz], key=lambda x: x["timestamp"])
        if len(g) != na_okno:
            continue                      # luka lub końcówka — odrzucamy niepełne okno
        wynik.append({
            "timestamp": klucz,
            "open": g[0]["open"],
            "high": max(x["high"] for x in g),
            "low": min(x["low"] for x in g),
            "close": g[-1]["close"],
            "volume": sum(x["volume"] for x in g),
        })
    return wynik


def agreguj_4h(bary_1h: list) -> list:
    """Zgodność wsteczna — 1h→4h. Woła to `narzedzia/audyt_danych.py`."""
    return agreguj(bary_1h, CZTERY_H_MS)


def _pochodzenie(sciezka: str) -> str:
    """Pierwsza linia pliku CryptoDataDownload/Binance zawiera URL źródła."""
    try:
        with open(sciezka, encoding="utf-8") as f:
            return f.readline().strip()
    except Exception:
        return ""


def _zapisz(cel: str, bary: list) -> None:
    """Zapisuje wynik. Przed NADPISANIEM istniejącego pliku robi kopię i ostrzega.

    Powód (zmierzone 2026-07-20, własna wpadka): testowy bieg na LINKUSDT nadpisał plik
    4h POBRANY z Binance wersją przeliczoną z 1h — bez kopii. Wyszło dobrze tylko dlatego,
    że 1h było już naprawione wobec giełdy; godzinę wcześniej wgrałbym skażone dane bez
    możliwości cofnięcia. To ta sama klasa, którą chwilę wcześniej wpisałem do Księgi Wad
    („plik pochodny nadpisuje oryginał, mieszane pochodzenie w katalogu").
    """
    os.makedirs(os.path.dirname(cel), exist_ok=True)
    if os.path.exists(cel):
        import shutil
        from datetime import datetime, timezone
        kopie = os.path.join(os.path.dirname(os.path.dirname(cel)), "_kopie")
        os.makedirs(kopie, exist_ok=True)
        stempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        kopia = os.path.join(kopie, f"{os.path.basename(cel)}.{stempel}.przed-agregacja.bak")
        shutil.copy2(cel, kopia)
        zrodlo = _pochodzenie(cel)
        if "binance.com" in zrodlo.lower():
            print(f"      ⚠️ NADPISUJESZ plik pobrany z giełdy ({zrodlo}) wersją PRZELICZONĄ "
                  f"— kopia: {os.path.relpath(kopia)}", file=sys.stderr, flush=True)
        else:
            print(f"      💾 kopia przed nadpisaniem: {os.path.relpath(kopia)}",
                  file=sys.stderr, flush=True)
    with open(cel, "w", encoding="utf-8") as f:
        f.write("timestamp,open,high,low,close,volume\n")
        for b in bary:
            f.write(f"{b['timestamp']},{b['open']},{b['high']},"
                    f"{b['low']},{b['close']},{b['volume']}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Agregacja barów do wyższego interwału")
    ap.add_argument("--z", dest="zrodlo", default="1h", choices=list(INTERWALY),
                    help="interwał źródłowy (domyślnie 1h)")
    ap.add_argument("--do", dest="cele", default="4h",
                    help="interwały docelowe po przecinku (np. 5m,15m)")
    ap.add_argument("--pary", default="", help="ogranicz do par po przecinku")
    args = ap.parse_args()

    cele = [c.strip().lower() for c in args.cele.split(",") if c.strip()]
    zle = [c for c in cele if c not in INTERWALY]
    if zle:
        raise SystemExit(f"Nieznane interwały docelowe: {zle}. Dostępne: {sorted(INTERWALY)}")
    min_zrodla = INTERWALY[args.zrodlo][0]
    for c in cele:
        if INTERWALY[c][0] % min_zrodla != 0 or INTERWALY[c][0] <= min_zrodla:
            raise SystemExit(f"'{c}' nie jest całkowitą WIELOKROTNOŚCIĄ '{args.zrodlo}' "
                             "— agregacja niemożliwa bez zgadywania (Prawo I)")

    root = os.path.join(os.path.dirname(__file__), "..")
    _, kat_z, suf_z = (INTERWALY[args.zrodlo][0],) + INTERWALY[args.zrodlo][1:]
    filtr = {p.strip().upper() for p in args.pary.split(",") if p.strip()}
    pliki = sorted(glob.glob(os.path.join(root, kat_z, f"Binance_*{suf_z}.csv")))
    if not pliki:
        raise SystemExit(f"Brak plików źródłowych w {kat_z}")

    zadania = [(p, c) for p in pliki for c in cele
               if not filtr or os.path.basename(p).replace("Binance_", "")
               .replace(f"{suf_z}.csv", "") in filtr]
    print(f"⚙️ Agregacja {args.zrodlo} → {', '.join(cele)} | {len(zadania)} zadań", flush=True)

    for nr, (sciezka, cel_int) in enumerate(zadania, 1):
        para = os.path.basename(sciezka).replace(f"{suf_z}.csv", "")
        t0 = time.time()
        print(f"[{nr}/{len(zadania)}] {para} → {cel_int}: wczytuję…",
              file=sys.stderr, flush=True)
        bary = wczytaj_csv(sciezka, interwal=args.zrodlo)
        wynik = agreguj(bary, INTERWALY[cel_int][0] * MINUTA_MS)
        kat_c, suf_c = INTERWALY[cel_int][1], INTERWALY[cel_int][2]
        _zapisz(os.path.join(root, kat_c, f"{para}{suf_c}.csv"), wynik)
        odrzucone = len(bary) // max(1, INTERWALY[cel_int][0] // min_zrodla) - len(wynik)
        print(f"[{nr}/{len(zadania)}] {para}: {len(bary)} × {args.zrodlo} → "
              f"{len(wynik)} × {cel_int} (niepełnych odrzucono ~{max(0, odrzucone)}) "
              f"— {time.time() - t0:.0f}s", flush=True)
        del bary, wynik            # 1.5 mln barów/parę — zwalniaj przed następną parą
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
