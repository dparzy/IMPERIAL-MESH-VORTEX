"""
🔬 AUDYT DANYCH ŚWIECOWYCH — czy nasze OHLCV mówi prawdę?

Powód (rozkaz Cezara 2026-07-20): część `dane/4h/` powstała z PRZELICZENIA 1h
(`narzedzia/agreguj_4h.py`), więc audyt miał sprawdzić 4h. POMIAR ODWRÓCIŁ PODEJRZENIE:

  • `dane/4h/*.csv`        → źródło **binance.com** — 799/800 barów co do grosza zgodne
  • `dane/godzinowe/*.csv` → źródło **CryptoDataDownload.com** (POŚREDNIK, nie giełda)
    → ETH 2021-01-11 08:00 low = 1063.00, a Binance mówi 1049.01 (knot zgubiony o 1.3%)

Dlaczego to nie kosmetyka: ZAWYŻONY DOŁEK oznacza, że stop-lossy, które w rzeczywistości
by poleciały, w backteście NIE lecą — wynik jest obciążony optymistycznie. Każdy pomiar
na 1H stoi na tych plikach.

WARSTWY (Prawo XVI — każda pyta o co innego, żadna nie zastępuje pozostałych):

  W1 STRUKTURA  — siatka UTC, monotoniczność, duplikaty, sensowność OHLC. Bez sieci.
  W2 KRZYŻOWA   — 1h zagregowane do 4h vs plik 4h. Bez sieci. Darmowy detektor: skoro
                  4h pochodzi z Binance, a 1h od pośrednika, każdy rozjazd wskazuje
                  uszkodzony bar 1h. Widzi TYLKO okres pokryty plikiem 4h.
  W3 ŹRÓDŁO     — porównanie z publicznym API Binance. Jedyna warstwa widząca błąd,
                  który 1h i 4h popełniłyby JEDNAKOWO, i jedyna sięgająca przed 2021.

Uruchom:
    python narzedzia/audyt_danych.py                                  # W1+W2, bez sieci
    python narzedzia/audyt_danych.py --zrodlo --pary BTCUSDT          # + próbka z Binance
    python narzedzia/audyt_danych.py --pelny-skan --pary BTCUSDT      # CAŁY plik vs Binance
    python narzedzia/audyt_danych.py --pelny-skan --pary BTCUSDT --napraw   # + naprawa

Naprawa (`--napraw`): podmienia WYŁĄCZNIE bary rozjechane ze źródłem, resztę zostawia
nietkniętą, a przed zapisem robi kopię (dane/ jest poza gitem — nie ma siatki cofnięcia).
Każda zmieniona wartość jest wypisana. Prawo I: nic nie ginie po cichu.

Kod wyjścia: 0 = czysto, 2 = wykryto rozbieżności.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import shutil
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from narzedzia.agreguj_4h import agreguj_4h  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
KATALOGI = {"1h": ("dane/godzinowe", "_1h"), "4h": ("dane/4h", "_4h")}
MS = {"1h": 3_600_000, "4h": 14_400_000}
KOPIE = os.path.join(ROOT, "dane", "_kopie")
# Ceny porównujemy WZGLĘDNIE — 1e-6 jest poniżej precyzji zapisu, a powyżej szumu float.
TOL_CENY = 1e-6
TOL_WOL = 1e-4


def _rel(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1e-12)


def _czas(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


# ── Binance (publiczne API, bez klucza) ──────────────────────────────────────────

def _klines(symbol: str, interval: str, start_ms: int, limit: int = 1000) -> list:
    import requests
    r = requests.get("https://api.binance.com/api/v3/klines",
                     params={"symbol": symbol, "interval": interval,
                             "startTime": start_ms, "limit": limit}, timeout=30)
    r.raise_for_status()
    return [{"timestamp": int(k[0]), "open": float(k[1]), "high": float(k[2]),
             "low": float(k[3]), "close": float(k[4]), "volume": float(k[5]),
             "quote": float(k[7]), "trades": int(k[8])} for k in r.json()]


def pobierz_zakres(symbol: str, interval: str, od_ms: int, do_ms: int,
                   pasek: bool = True) -> dict:
    """Cała historia [od, do] z Binance, stronicowana. {ts: bar}. Puste = brak sieci."""
    try:
        import requests  # noqa: F401
    except ImportError:
        print("   ⚠️ brak `requests` — warstwa źródłowa pominięta", file=sys.stderr)
        return {}
    krok = MS[interval]
    oczekiwane = max(1, (do_ms - od_ms) // krok + 1)
    out: dict = {}
    cur = od_ms
    while cur <= do_ms:
        try:
            batch = _klines(symbol, interval, cur, 1000)
        except Exception as e:
            print(f"   ⚠️ Binance przerwał ({type(e).__name__}) — mam {len(out)} barów",
                  file=sys.stderr)
            break
        if not batch:
            break
        for b in batch:
            if b["timestamp"] <= do_ms:
                out[b["timestamp"]] = b
        nastepny = batch[-1]["timestamp"] + krok
        if nastepny <= cur:
            break
        cur = nastepny
        if pasek:
            print(f"\r   … {symbol} {interval}: {len(out)}/{oczekiwane} barów z Binance",
                  end="", file=sys.stderr, flush=True)
        time.sleep(0.12)          # łagodnie dla limitów API (waga 5/żądanie)
    if pasek:
        print(file=sys.stderr)
    return out


# ── W1 / W2 ──────────────────────────────────────────────────────────────────────

def audyt_struktury(bary: list, interwal: str) -> list[str]:
    if not bary:
        return ["plik pusty"]
    bledy = []
    krok = MS[interwal]
    poza = [b for b in bary if b["timestamp"] % krok != 0]
    if poza:
        bledy.append(f"{len(poza)} barów POZA siatką UTC {interwal} "
                     f"(pierwszy: {_czas(poza[0]['timestamp'])}) — przesunięta siatka "
                     "fałszuje KAŻDY wskaźnik")
    ts = [b["timestamp"] for b in bary]
    if ts != sorted(ts):
        bledy.append("znaczniki czasu NIE są rosnące")
    if len(set(ts)) != len(ts):
        bledy.append(f"{len(ts) - len(set(ts))} zduplikowanych znaczników czasu")
    for b in bary:
        o, h, l, c, v = b["open"], b["high"], b["low"], b["close"], b["volume"]
        if h < l:
            bledy.append(f"{_czas(b['timestamp'])}: high < low")
            break
        if h < max(o, c) - 1e-9 or l > min(o, c) + 1e-9:
            bledy.append(f"{_czas(b['timestamp'])}: OHLC niespójne (O={o} H={h} L={l} C={c})")
            break
        if v < 0:
            bledy.append(f"{_czas(b['timestamp'])}: ujemny wolumen")
            break
    return bledy


def audyt_krzyzowy(bary_1h: list, bary_4h: list) -> tuple[list[str], list[int]]:
    """1h→4h vs plik 4h. Zwraca (opisy, podejrzane okna 4h w ms)."""
    if not bary_1h or not bary_4h:
        return (["brak pary plików 1h/4h — warstwa krzyżowa pominięta"], [])
    z_1h = {b["timestamp"]: b for b in agreguj_4h(bary_1h)}
    plik = {b["timestamp"]: b for b in bary_4h}
    wspolne = sorted(set(z_1h) & set(plik))
    if not wspolne:
        return (["ZERO wspólnych znaczników — pliki z różnych światów"], [])
    podejrzane = []
    for ts in wspolne:
        a, b = z_1h[ts], plik[ts]
        if any(_rel(a[p], b[p]) > TOL_CENY for p in ("open", "high", "low", "close")):
            podejrzane.append(ts)
    if not podejrzane:
        return ([], [])
    ts = podejrzane[0]
    a, b = z_1h[ts], plik[ts]
    pole = next(p for p in ("open", "high", "low", "close") if _rel(a[p], b[p]) > TOL_CENY)
    return ([f"{len(podejrzane)} okien rozjechanych z plikiem 4h "
             f"(np. {_czas(ts)} {pole}: z naszego 1h={a[pole]} vs 4h={b[pole]}) — "
             f"4h pochodzi z Binance, więc to 1h jest podejrzane"], podejrzane)


# ── W3 + naprawa ─────────────────────────────────────────────────────────────────

def porownaj_ze_zrodlem(nasze: list, zrodlo: dict) -> list[dict]:
    """Lista rozjazdów: {ts, pole, nasze, zrodlo}. Pomija bary spoza pobranego zakresu."""
    rozjazdy = []
    for b in nasze:
        z = zrodlo.get(b["timestamp"])
        if not z:
            continue
        for pole in ("open", "high", "low", "close"):
            if _rel(b[pole], z[pole]) > TOL_CENY:
                rozjazdy.append({"ts": b["timestamp"], "pole": pole,
                                 "nasze": b[pole], "zrodlo": z[pole]})
        if _rel(b["volume"], z["volume"]) > TOL_WOL:
            rozjazdy.append({"ts": b["timestamp"], "pole": "volume",
                             "nasze": b["volume"], "zrodlo": z["volume"]})
    return rozjazdy


def napraw_plik(sciezka: str, zrodlo: dict, tsy: set[int]) -> int:
    """Podmienia WYŁĄCZNIE bary o znacznikach `tsy` na wartości ze źródła.

    Format pliku (CryptoDataDownload/Binance) zachowany 1:1 — kolumny, kolejność wierszy
    i pozostałe pola nietknięte. Przed zapisem kopia w dane/_kopie/ (dane są poza gitem,
    więc bez kopii zmiana byłaby nieodwracalna).
    """
    if not tsy:
        return 0
    os.makedirs(KOPIE, exist_ok=True)
    stempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    kopia = os.path.join(KOPIE, f"{os.path.basename(sciezka)}.{stempel}.bak")
    shutil.copy2(sciezka, kopia)

    with open(sciezka, "r", encoding="utf-8", newline="") as f:
        wiersze = list(csv.reader(f))
    # Nagłówek kolumn to pierwszy wiersz zawierający 'Unix' (przed nim bywa linia z URL).
    idx_naglowka = next(i for i, w in enumerate(wiersze) if w and w[0].strip() == "Unix")
    kolumny = [k.strip() for k in wiersze[idx_naglowka]]
    poz = {k: kolumny.index(k) for k in ("Unix", "Open", "High", "Low", "Close")}
    poz_vol = next((kolumny.index(k) for k in kolumny if k.startswith("Volume ")
                    and not k.endswith("USDT")), None)

    zmienione = 0
    for w in wiersze[idx_naglowka + 1:]:
        if not w or len(w) <= max(poz.values()):
            continue
        try:
            ts = int(float(w[poz["Unix"]]))
        except ValueError:
            continue
        if ts >= 10 ** 12 * 10:      # niektóre pliki mają Unix w sekundach
            ts = ts // 1000
        z = zrodlo.get(ts)
        if ts not in tsy or not z:
            continue
        w[poz["Open"]] = repr(z["open"])
        w[poz["High"]] = repr(z["high"])
        w[poz["Low"]] = repr(z["low"])
        w[poz["Close"]] = repr(z["close"])
        if poz_vol is not None:
            w[poz_vol] = repr(z["volume"])
        zmienione += 1

    with open(sciezka, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(wiersze)
    print(f"      💾 kopia: {os.path.relpath(kopia, ROOT)}")
    return zmienione


def napraw_siatke(sciezka: str, symbol: str, interwal: str, poza: list[int]) -> int:
    """Wymienia CAŁY odcinek objęty barami poza siatką na bary z Binance.

    Inna klasa wady niż zła wartość: bar o 09:28 nie jest „09:00 z błędem" — to agregat
    INNEGO okna (zmierzone 2026-07-20: 43 kolejne bary przesunięte o 28m14s, 2018-02-09
    09:28 → 02-11 03:28, w tych oknach BRAK poprawnych godzinówek, a Binance ma komplet).
    Dlatego podmiana wartości nie wystarcza — trzeba usunąć odcinek i wstawić prawdziwy.
    """
    if not poza:
        return 0
    krok = MS[interwal]
    od = (min(poza) // krok) * krok
    do = (max(poza) // krok) * krok + krok
    print(f"      ⏳ pobieram odcinek {_czas(od)} → {_czas(do)} z Binance...")
    zrodlo = pobierz_zakres(symbol, interwal, od, do)
    if not zrodlo:
        print("      ⚠️ brak danych źródłowych — odcinek NIETKNIĘTY (Prawo I: nie zgadujemy)")
        return 0

    os.makedirs(KOPIE, exist_ok=True)
    stempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    kopia = os.path.join(KOPIE, f"{os.path.basename(sciezka)}.{stempel}.siatka.bak")
    shutil.copy2(sciezka, kopia)

    with open(sciezka, "r", encoding="utf-8", newline="") as f:
        wiersze = list(csv.reader(f))
    i_nag = next(i for i, w in enumerate(wiersze) if w and w[0].strip() == "Unix")
    kolumny = [k.strip() for k in wiersze[i_nag]]
    idx = {k: kolumny.index(k) for k in ("Unix", "Date", "Symbol", "Open", "High", "Low", "Close")}
    i_vol = next((kolumny.index(k) for k in kolumny
                  if k.startswith("Volume ") and not k.endswith("USDT")), None)
    i_quote = next((kolumny.index(k) for k in kolumny if k == "Volume USDT"), None)
    i_tr = next((kolumny.index(k) for k in kolumny if k == "tradecount"), None)

    def _ts(w):
        try:
            return int(float(w[idx["Unix"]]))
        except (ValueError, IndexError):
            return None

    # Wytnij WSZYSTKO z odcinka (i poza siatką, i ewentualne poprawne — inaczej duplikaty).
    glowa, ogon, usuniete = wiersze[:i_nag + 1], [], 0
    for w in wiersze[i_nag + 1:]:
        t = _ts(w)
        if t is not None and od <= t < do:
            usuniete += 1
            continue
        ogon.append(w)

    def _wiersz(b):
        w = [""] * len(kolumny)
        w[idx["Unix"]] = str(b["timestamp"])
        w[idx["Date"]] = datetime.fromtimestamp(
            b["timestamp"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        w[idx["Symbol"]] = symbol
        for k, p in (("Open", "open"), ("High", "high"), ("Low", "low"), ("Close", "close")):
            w[idx[k]] = repr(b[p])
        if i_vol is not None:
            w[i_vol] = repr(b["volume"])
        if i_quote is not None:
            w[i_quote] = repr(b.get("quote", 0.0))
        if i_tr is not None:
            w[i_tr] = str(b.get("trades", 0))
        return w

    nowe = [_wiersz(zrodlo[t]) for t in sorted(zrodlo) if od <= t < do]
    # Plik CryptoDataDownload jest MALEJĄCO (najnowsze na górze) — zachowaj tę konwencję.
    malejaco = len(ogon) > 1 and (_ts(ogon[0]) or 0) > (_ts(ogon[-1]) or 0)
    if malejaco:
        nowe.reverse()
    scalone = sorted(ogon + nowe, key=lambda w: _ts(w) or 0, reverse=malejaco)

    with open(sciezka, "w", encoding="utf-8", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(glowa + scalone)
    print(f"      💾 kopia: {os.path.relpath(kopia, ROOT)}")
    print(f"      🔧 odcinek wymieniony: usunięto {usuniete} wierszy, wstawiono {len(nowe)} "
          f"barów z Binance")
    return len(nowe)


def main() -> int:
    ap = argparse.ArgumentParser(description="Audyt danych świecowych (struktura/krzyżowy/źródło)")
    ap.add_argument("--interwal", choices=["1h", "4h"], default="1h")
    ap.add_argument("--pary", default="", help="ogranicz do par po przecinku")
    ap.add_argument("--zrodlo", action="store_true", help="próbka z Binance (ostatnie N barów)")
    ap.add_argument("--probka", type=int, default=800)
    ap.add_argument("--pelny-skan", action="store_true",
                    help="porównaj CAŁY plik z Binance (wolne: stronicowanie po 1000 barów)")
    ap.add_argument("--napraw", action="store_true",
                    help="podmień rozjechane bary wartościami z Binance (robi kopię)")
    args = ap.parse_args()

    # Naprawa siatki (W1) pobiera swój odcinek ze źródła sama, więc nie wymaga --zrodlo.
    # Naprawa WARTOŚCI wymaga porównania ze źródłem — bez niego nie wiadomo, co poprawiać.
    if args.napraw and not (args.pelny_skan or args.zrodlo):
        print("ℹ️ --napraw bez --pelny-skan/--zrodlo naprawia TYLKO siatkę (W1). "
              "Złe wartości wymagają porównania ze źródłem.\n")

    kat, suf = KATALOGI[args.interwal]
    filtr = {p.strip().upper() for p in args.pary.split(",") if p.strip()}
    pliki = sorted(glob.glob(os.path.join(ROOT, kat, f"Binance_*{suf}.csv")))
    if not pliki:
        return 2

    tryb = "W1+W2" + (" +W3 pełny skan" if args.pelny_skan else (" +W3 próbka" if args.zrodlo else ""))
    print(f"🔬 AUDYT DANYCH {args.interwal.upper()} — {tryb}" +
          ("  ⚙️ TRYB NAPRAWY" if args.napraw else ""))
    print("=" * 80)

    laczne, naprawione = 0, 0
    for sciezka in pliki:
        symbol = os.path.basename(sciezka).replace("Binance_", "").replace(f"{suf}.csv", "")
        if filtr and symbol not in filtr:
            continue
        bary = wczytaj_csv(sciezka, interwal=args.interwal)
        uwagi = [("W1", b) for b in audyt_struktury(bary, args.interwal)]
        poza_siatka = [b["timestamp"] for b in bary if b["timestamp"] % MS[args.interwal] != 0]

        if args.interwal == "1h":
            s4 = os.path.join(ROOT, "dane", "4h", f"Binance_{symbol}_4h.csv")
            b4 = wczytaj_csv(s4, interwal="4h") if os.path.exists(s4) else []
            opisy, _ = audyt_krzyzowy(bary, b4)
            uwagi += [("W2", o) for o in opisy if not o.startswith("brak")]

        rozjazdy = []
        if (args.zrodlo or args.pelny_skan) and bary:
            od = bary[0]["timestamp"] if args.pelny_skan else bary[max(0, len(bary) - args.probka)]["timestamp"]
            zrodlo = pobierz_zakres(symbol, args.interwal, od, bary[-1]["timestamp"])
            if zrodlo:
                rozjazdy = porownaj_ze_zrodlem(bary, zrodlo)
                wspolne = sum(1 for b in bary if b["timestamp"] in zrodlo)
                if rozjazdy:
                    uwagi.append(("W3", f"{len(rozjazdy)} rozjazdów vs Binance "
                                        f"na {wspolne} porównanych barach"))
                else:
                    uwagi.append(("W3", f"__OK__ {wspolne} barów zgodnych z Binance"))

        realne = [(w, t) for w, t in uwagi if not t.startswith("__OK__")]
        print(f"{'❌' if realne else '✅'} {symbol:10} {len(bary):>6} barów | "
              f"{_czas(bary[0]['timestamp']) if bary else '-'} → "
              f"{_czas(bary[-1]['timestamp']) if bary else '-'}")
        for _, t in [(w, t) for w, t in uwagi if t.startswith("__OK__")]:
            print(f"      ✓ {t.replace('__OK__ ', '')}")
        for w, t in realne:
            print(f"      ⚠️ [{w}] {t}")
        for r in rozjazdy[:12]:
            print(f"         {_czas(r['ts'])} {r['pole']:6}: nasze={r['nasze']} → Binance={r['zrodlo']}")
        if len(rozjazdy) > 12:
            print(f"         … i {len(rozjazdy) - 12} dalszych")
        laczne += len(realne)

        if args.napraw and poza_siatka:
            naprawione += napraw_siatke(sciezka, symbol, args.interwal, poza_siatka)
        if args.napraw and rozjazdy:
            n = napraw_plik(sciezka, zrodlo, {r["ts"] for r in rozjazdy})
            naprawione += n
            print(f"      ✅ naprawiono {n} barów z Binance")

    print("=" * 80)
    if args.napraw and naprawione:
        print(f"⚙️ NAPRAWIONO {naprawione} barów (kopie w dane/_kopie/). "
              "Uruchom audyt ponownie, żeby potwierdzić czystość.")
        return 0
    if laczne:
        print(f"❌ WYKRYTO {laczne} rozbieżności — dane wymagają naprawy przed użyciem.")
        return 2
    print("✅ Dane czyste we wszystkich uruchomionych warstwach.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
