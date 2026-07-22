"""
⬇️ NUNTIUS MERCATUS (Posłaniec Rynku) — POBIERACZ BINANCE: świece dowolnego interwału z publicznego API (bez klucza).

Nazwa: wcześniej `pobierz_4h_binance.py`. Zmieniona 2026-07-20, gdy moduł przestał
dotyczyć wyłącznie 4h — nazwa pliku też jest dokumentacją i też potrafi skłamać.

POWÓD ROZSZERZENIA (2026-07-20): agregacja 5m/15m z naszych danych minutowych wyszła
czysta (0 barów poza siatką, 200/200 zgodnych z Binance), ale ujawniła, że `dane/minutowe/`
kończy się **2022-07-27** — dane mają prawie 4 lata. Nie da się więc dołożyć 15m do tabeli
porównania interwałów liczonej na oknie 2024→2026, bo mieszałoby to efekt interwału
z efektem zupełnie innego reżimu rynku. Trzeba dociągnąć świeże 1m.

Klasa wady do zapamiętania: **plik istnieje, więc zakłada się, że jest aktualny**.
Dane starzeją się tak samo jak kod i dokumenty.

Zapis w formacie CryptoDataDownload (czytnik_csv czyta go wprost), nagłówek mówi prawdę
o źródle: `https://www.binance.com`.

WZNAWIALNOŚĆ (ZASADA ANALIZY CZĄSTKOWEJ): gdy plik docelowy już istnieje, domyślnie
dociągamy TYLKO brakującą końcówkę (od ostatniego bara), zamiast pobierać wszystko od zera.
Bieg przerwany w połowie nie zaczyna od nowa.

Uruchom:
    python narzedzia/pobierz_binance.py --interwal 4h --pary XRP,ADA --od 2021-01-01
    python narzedzia/pobierz_binance.py --interwal 1m --pary BTCUSDT,ETHUSDT --od 2024-01-01
    python narzedzia/pobierz_binance.py --interwal 1m --pary BTCUSDT --od-nowa
"""
import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Brak requests — zainstaluj: pip install requests")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 1000                       # maksimum Binance na żądanie
# Tempo zapytań. Limit Binance (waga 5/żądanie, budżet 6000/min) pozwalałby na ~0.05 s,
# ale trzy biegi w tle padły dziś przy intensywnym ruchu sieciowym — HIPOTEZA (nie dowód):
# własne dobijanie się do API dusi łącze, po którym rozmawia klient. Zwalniamy świadomie:
# ~3 żądania/s zamiast ~7. Koszt: dwukrotnie dłuższe pobieranie. Zysk: bieg dochodzi do końca.
PRZERWA_S = 0.35

# etykieta → (ms, katalog, sufiks pliku)
INTERWALY = {
    "1m":  (60_000,     "dane/minutowe",  "_minute"),
    "5m":  (300_000,    "dane/5m",        "_5m"),
    "15m": (900_000,    "dane/15m",       "_15m"),
    "1h":  (3_600_000,  "dane/godzinowe", "_1h"),
    "4h":  (14_400_000, "dane/4h",        "_4h"),
    "1d":  (86_400_000, "dane/dzienne",   "_d"),
}


def pobierz_klines(symbol: str, interval: str, limit: int = LIMIT) -> list:
    """Ostatnie `limit` świec (bez paginacji)."""
    r = requests.get("https://api.binance.com/api/v3/klines",
                     params={"symbol": symbol, "interval": interval, "limit": limit},
                     timeout=30)
    r.raise_for_status()
    return r.json()


def _plik_checkpointu(symbol: str, interval: str) -> Path:
    return ROOT / "dane" / "_checkpoint" / f"{symbol}_{interval}.jsonl"


def _wczytaj_checkpoint(sciezka: Path) -> dict:
    """Świece pobrane w poprzednich (także PRZERWANYCH) biegach. {ts: kline}."""
    if not sciezka.exists():
        return {}
    out: dict = {}
    for ln in sciezka.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            k = json.loads(ln)
            out[int(k[0])] = k
        except (json.JSONDecodeError, ValueError, IndexError, TypeError):
            continue          # ucięta ostatnia linia po zabiciu procesu — pomijamy
    return out


def pobierz_klines_zakres(symbol: str, interval: str, start_ms: int,
                          do_ms: int | None = None, pasek: bool = True) -> list:
    """Paginacja od `start_ms` do teraz (lub `do_ms`). Rosnąco, zdeduplikowane po open-time.

    WZNAWIALNOŚĆ RZECZYWISTA (naprawione 2026-07-20 po własnej wpadce): każda pobrana
    strona ląduje NATYCHMIAST w `dane/_checkpoint/<symbol>_<interwal>.jsonl`. Wcześniej
    wynik siedział wyłącznie w pamięci i zapisywał się dopiero na końcu — bieg zabity na
    10% (140 tys. świec BTC) stracił WSZYSTKO. To łamało ZASADĘ ANALIZY CZĄSTKOWEJ:
    „bieg, który umiera, NIE traci nic". Wznawialność między biegami ZAKOŃCZONYMI działa
    tylko wtedy, gdy nie jest potrzebna.
    """
    krok = INTERWALY[interval][0]
    koniec = do_ms if do_ms is not None else int(time.time() * 1000)
    oczekiwane = max(1, (koniec - start_ms) // krok)

    ckpt = _plik_checkpointu(symbol, interval)
    widziane = {t: k for t, k in _wczytaj_checkpoint(ckpt).items() if start_ms <= t <= koniec}
    if widziane:
        print(f"   ↻ checkpoint: {len(widziane)} świec z przerwanego biegu — wznawiam",
              file=sys.stderr, flush=True)
    cur = max(widziane) + krok if widziane else start_ms

    ckpt.parent.mkdir(parents=True, exist_ok=True)
    t0, pobrane_teraz = time.time(), 0
    with open(ckpt, "a", encoding="utf-8") as f_ckpt:
        while cur <= koniec:
            try:
                batch = pobierz_klines_od(symbol, interval, cur)
            except Exception as e:
                print(f"\n   ⚠️ przerwa w pobieraniu ({type(e).__name__}) — {len(widziane)} świec "
                      "w checkpoincie; uruchom ponownie, dociągnie resztę",
                      file=sys.stderr, flush=True)
                break
            if not batch:
                break
            for k in batch:
                ts = int(k[0])
                if ts <= koniec and ts not in widziane:
                    widziane[ts] = k
                    f_ckpt.write(json.dumps(k, ensure_ascii=False) + "\n")
            f_ckpt.flush()                       # na dysk PRZED następnym żądaniem
            pobrane_teraz += len(batch)
            nastepny = int(batch[-1][0]) + krok
            if len(batch) < LIMIT or nastepny <= cur:
                break
            cur = nastepny
            if pasek and pobrane_teraz % (LIMIT * 5) < LIMIT:
                tempo = pobrane_teraz / max(time.time() - t0, 1e-9)
                eta = (oczekiwane - len(widziane)) / max(tempo, 1e-9)
                print(f"\r   … {symbol} {interval}: {len(widziane)}/{oczekiwane} świec "
                      f"({100 * len(widziane) / oczekiwane:.0f}%) — ETA {eta / 60:.1f} min",
                      end="", file=sys.stderr, flush=True)
            time.sleep(PRZERWA_S)
    if pasek:
        print(file=sys.stderr)
    return [widziane[t] for t in sorted(widziane)]


def pobierz_klines_od(symbol: str, interval: str, start_ms: int) -> list:
    r = requests.get("https://api.binance.com/api/v3/klines",
                     params={"symbol": symbol, "interval": interval,
                             "startTime": start_ms, "limit": LIMIT}, timeout=30)
    r.raise_for_status()
    return r.json()


def _ostatni_ts(sciezka: Path) -> int | None:
    """Znacznik NAJNOWSZEGO bara w istniejącym pliku (format CDD: malejąco)."""
    if not sciezka.exists():
        return None
    try:
        with open(sciezka, encoding="utf-8", newline="") as f:
            w = list(csv.reader(f))
        i = next(k for k, r in enumerate(w) if r and r[0].strip().lower() in ("unix", "timestamp"))
        tsy = []
        for r in w[i + 1:]:
            try:
                tsy.append(int(float(r[0])))
            except (ValueError, IndexError):
                continue
        return max(tsy) if tsy else None
    except Exception:
        return None


def zapisz_csv(symbol: str, klines: list, sciezka: Path) -> None:
    """Format CryptoDataDownload (malejąco), nagłówek = PRAWDZIWE źródło.

    Przed NADPISANIEM istniejącego pliku robi kopię i mówi, co zastępuje — ta sama straż
    co w `narzedzia/agreguj_bary.py`. Powód (2026-07-20): dane leżą poza gitem, więc bez
    kopii nadpisanie jest nieodwracalne, a zakresy dat potrafią się NIE pokrywać
    (dane minutowe miały 2019-2022, dociągane 2024+ — scalenie ich nie połączy, zastąpi).
    """
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    if sciezka.exists():
        import shutil
        kopie = sciezka.parent.parent / "_kopie"
        kopie.mkdir(parents=True, exist_ok=True)
        stempel = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        kopia = kopie / f"{sciezka.name}.{stempel}.przed-pobraniem.bak"
        shutil.copy2(sciezka, kopia)
        print(f"   💾 kopia przed nadpisaniem: {kopia.relative_to(ROOT)}",
              file=sys.stderr, flush=True)
    with open(sciezka, "w", newline="", encoding="utf-8") as f:
        f.write("https://www.binance.com\n")
        w = csv.writer(f)
        baza = symbol[:-4] if symbol.endswith("USDT") else symbol
        w.writerow(["Unix", "Date", "Symbol", "Open", "High", "Low", "Close",
                    f"Volume {baza}", "Volume USDT", "tradecount"])
        for k in reversed(klines):        # Binance rosnąco → CDD malejąco
            ts_ms = int(k[0])
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            w.writerow([ts_ms, dt.strftime("%Y-%m-%d %H:%M:%S"), symbol,
                        k[1], k[2], k[3], k[4], k[5], k[7], int(k[8])])


def _wczytaj_surowe(sciezka: Path) -> list:
    """Istniejące świece z pliku → format klines (do scalenia z dociągniętymi)."""
    if not sciezka.exists():
        return []
    with open(sciezka, encoding="utf-8", newline="") as f:
        w = list(csv.reader(f))
    try:
        i = next(k for k, r in enumerate(w) if r and r[0].strip().lower() in ("unix", "timestamp"))
    except StopIteration:
        return []
    out = []
    for r in w[i + 1:]:
        try:
            out.append([int(float(r[0])), r[3], r[4], r[5], r[6], r[7], 0, r[8], int(float(r[9]))])
        except (ValueError, IndexError):
            continue
    return sorted(out, key=lambda k: k[0])


def main() -> int:
    ap = argparse.ArgumentParser(description="Pobieranie świec z publicznego API Binance")
    ap.add_argument("--interwal", default="4h", choices=list(INTERWALY))
    ap.add_argument("--pary", required=True,
                    help="pary po przecinku; 'BTC' i 'BTCUSDT' równoważne")
    ap.add_argument("--od", metavar="YYYY-MM-DD", help="data początkowa (paginacja)")
    ap.add_argument("--do", metavar="YYYY-MM-DD", help="data końcowa (domyślnie: teraz)")
    ap.add_argument("--od-nowa", action="store_true",
                    help="pobierz od zera zamiast dociągać końcówkę do istniejącego pliku")
    args = ap.parse_args()

    krok, katalog, sufiks = INTERWALY[args.interwal]
    pary = [p.strip().upper() for p in args.pary.split(",") if p.strip()]
    pary = [p if p.endswith("USDT") else f"{p}USDT" for p in pary]
    do_ms = (int(datetime.strptime(args.do, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
             if args.do else None)

    print(f"⬇️ Binance {args.interwal} | {len(pary)} par: {', '.join(pary)}", flush=True)
    ok = 0
    for nr, symbol in enumerate(pary, 1):
        cel = ROOT / katalog / f"Binance_{symbol}{sufiks}.csv"
        istniejace = [] if args.od_nowa else _wczytaj_surowe(cel)
        ostatni = None if args.od_nowa else _ostatni_ts(cel)

        if ostatni and not args.od:
            start_ms = ostatni + krok
            print(f"[{nr}/{len(pary)}] {symbol}: plik ma {len(istniejace)} świec do "
                  f"{datetime.fromtimestamp(ostatni / 1000, tz=timezone.utc):%Y-%m-%d %H:%M} "
                  "— dociągam końcówkę", flush=True)
        elif args.od:
            start_ms = int(datetime.strptime(args.od, "%Y-%m-%d")
                           .replace(tzinfo=timezone.utc).timestamp() * 1000)
            istniejace = []          # jawny zakres → pobieramy go w całości
            print(f"[{nr}/{len(pary)}] {symbol}: pobieram od {args.od}", flush=True)
        else:
            start_ms = None
            print(f"[{nr}/{len(pary)}] {symbol}: ostatnie {LIMIT} świec", flush=True)

        try:
            nowe = (pobierz_klines_zakres(symbol, args.interwal, start_ms, do_ms)
                    if start_ms is not None else pobierz_klines(symbol, args.interwal))
        except Exception as e:
            print(f"[{nr}/{len(pary)}] {symbol}: BŁĄD {type(e).__name__}: {e}", flush=True)
            continue

        znane_wczesniej = {int(k[0]) for k in istniejace}
        scalone = {int(k[0]): k for k in istniejace}
        scalone.update({int(k[0]): k for k in nowe})
        klines = [scalone[t] for t in sorted(scalone)]
        # Liczymy PRZYROST wobec tego, co plik już miał — nie długość zwróconej listy.
        # (Wcześniej raport mówił „dociągnięto 193" także wtedy, gdy wszystko przyszło
        #  z checkpointu i nie poszło ani jedno żądanie do API.)
        przyrost = sum(1 for t in scalone if t not in znane_wczesniej)
        if not klines:
            print(f"[{nr}/{len(pary)}] {symbol}: brak świec — plik NIETKNIĘTY", flush=True)
            continue
        zapisz_csv(symbol, klines, cel)
        zakres = (f"{datetime.fromtimestamp(klines[0][0] / 1000, tz=timezone.utc):%Y-%m-%d}"
                  f" → {datetime.fromtimestamp(klines[-1][0] / 1000, tz=timezone.utc):%Y-%m-%d}")
        print(f"[{nr}/{len(pary)}] {symbol}: {len(klines)} świec ({zakres}), "
              f"nowych w pliku: {przyrost}", flush=True)
        ok += 1
    print(f"\nGotowe: {ok}/{len(pary)} par.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
