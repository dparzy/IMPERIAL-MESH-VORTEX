"""
Porównanie TF na TYM SAMYM oknie czasowym (izolacja: interwał vs okno).
Cap 1h = MAX_BAROW barów/parę; 4h = MAX_BAROW/4; 1d = MAX_BAROW/24 — ten sam zakres
kalendarzowy, więc różnica wyniku to efekt INTERWAŁU, nie długości historii.
Prawo I: rozdziela efekt interwału od efektu okna (DOGE 2021 poza oknem 3.4 lat).

Rozszerzone 2026-07-20 (hipoteza interwału po A/B DVOL): dodane 1d, CLI (--pary/--bary/
--interwaly), pasek postępu (Prawo XXIV) i werdykt porównawczy. Powód: A/B DVOL na 1H
dał ROI −5.49% w OBU ramionach (pełna era, BTC+ETH) przy dodatnim ROI na 4H/1D — pytanie
„czy problemem jest sam interwał, nie sygnał" wymaga pomiaru na identycznej konfiguracji.

Uruchom:
  python narzedzia/sym_porownanie_tf.py                        # domyślnie 5 par, 30k barów 1h
  python narzedzia/sym_porownanie_tf.py --pary BTCUSDT,ETHUSDT --bary 19471
  python narzedzia/sym_porownanie_tf.py --interwaly 1h,4h,1d --podglad
"""
import argparse
import datetime as dt
import logging
import os
import sys
import time

logging.disable(logging.CRITICAL)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imperium.akwedukty.czytnik_csv import wczytaj_csv  # noqa: E402
from imperium.koloseum.backtest import backtest_portfel  # noqa: E402

# katalog + sufiks pliku + MINUTY interwału. Liczba barów skalowana przez minuty, nie przez
# dzielnik całkowity — inaczej interwały KRÓTSZE niż godzina (15m, 5m) dawałyby dzielnik
# ułamkowy i dzielenie całkowite ucinałoby okno do zera (zmierzone 2026-07-20 przy dokładaniu
# profilu SCALP, którego nigdy nie testowaliśmy, bo nie było plików 5m/15m).
INTERWALY = {
    "5m":  ("dane/5m", "_5m", 5),
    "15m": ("dane/15m", "_15m", 15),
    "1h":  ("dane/godzinowe", "_1h", 60),
    "4h":  ("dane/4h", "_4h", 240),
    "1d":  ("dane/dzienne", "_d", 1440),
}
PARY_DOMYSLNE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "DOGEUSDT"]
MAX_BAROW = int(os.getenv("MAX_BAROW", "30000"))  # 1h barów/parę

# Konfiguracja IDENTYCZNA dla każdego interwału — inaczej porównanie mierzyłoby konfig,
# nie interwał. (Uwaga: to NIE jest konfiguracja z ab_dvol.py — tam top_n=2 bez compoundingu;
# liczby stąd porównuj MIĘDZY interwałami, nie z wynikami A/B Tier-1.)
BAZA = dict(tryb_skaner=True, skaner_top_n=3, sizing_przekonania=True,
            compounding=True, filtr_asymetrii=True)


def _pliki(pary, interwal):
    sub, suf, _ = INTERWALY[interwal]
    return {s: f"{sub}/Binance_{s}{suf}.csv" for s in pary}


def wspolne_okno(pary, interwaly, bary_1h):
    """Zakres dat WSPÓLNY dla wszystkich interwałów i par: [max(startów), min(końców)].

    Powód (zmierzone 2026-07-20): cięcie po LICZBIE BARÓW zakłada, że każdy plik kończy się
    w tym samym momencie — a nie kończy. Pliki 1D sięgały 2026-06-18, a świeżo pobrane 15m
    2026-07-20, więc „to samo okno" różniło się o miesiąc i mieszało efekt interwału z efektem
    innego wycinka rynku. Dokładnie ta wada, którą to narzędzie miało eliminować.
    """
    konce, starty = [], []
    for interwal in interwaly:
        for sym, sc in _pliki(pary, interwal).items():
            b = wczytaj_csv(sc, interwal=interwal, limit=2)
            if not b:
                continue
            konce.append(b[-1]["timestamp"])
            pierwszy = wczytaj_csv(sc, interwal=interwal, limit=None)[0]["timestamp"]
            starty.append(pierwszy)
    if not konce:
        return None, None
    do_ms = min(konce)
    od_ms = max(max(starty), do_ms - bary_1h * 3_600_000)
    return od_ms, do_ms


def _bieg(pary, interwal, limit, nr, ile, okno=None):
    pliki = _pliki(pary, interwal)
    print(f"[{nr}/{ile}] {interwal}: wczytuję {len(pary)} par (cap {limit} barów/parę)...",
          file=sys.stderr, flush=True)
    bary_per = {}
    zakresy = []
    for sym, sc in pliki.items():
        b = wczytaj_csv(sc, interwal=interwal, limit=None if okno else limit)
        if okno:
            od_ms, do_ms = okno
            b = [x for x in b if od_ms <= x["timestamp"] <= do_ms]
        bary_per[sym] = b
        if b:
            zakresy.append((b[0]["timestamp"], b[-1]["timestamp"]))
    okno = None
    if zakresy:
        od = dt.datetime.utcfromtimestamp(min(z[0] for z in zakresy) / 1000).date()
        do = dt.datetime.utcfromtimestamp(max(z[1] for z in zakresy) / 1000).date()
        okno = (od, do)
        n = len(next(iter(bary_per.values())))
        print(f"[{nr}/{ile}] {interwal}: okno {od} → {do} | {n} barów/parę — liczę backtest...",
              file=sys.stderr, flush=True)
    t0 = time.time()
    eng = backtest_portfel(pliki, interwal=interwal, bary_per=bary_per, **BAZA)
    s = eng.podsumowanie()
    roi = (s.kapital_koncowy / s.kapital_startowy - 1) * 100
    print(f"[{nr}/{ile}] {interwal}: gotowe w {time.time() - t0:.0f}s → ROI {roi:+.2f}%",
          file=sys.stderr, flush=True)
    return {"interwal": interwal, "roi": roi, "trades": s.total_trades,
            "wr": s.win_rate, "pnl": s.total_pnl_usdt, "maxdd": s.max_drawdown_pct,
            "okno": okno, "barow": len(next(iter(bary_per.values()))) if bary_per else 0}


def main():
    ap = argparse.ArgumentParser(description="Porównanie interwałów na tym samym oknie")
    ap.add_argument("--pary", default=",".join(PARY_DOMYSLNE),
                    help="lista par po przecinku (domyślnie 5 par)")
    ap.add_argument("--bary", type=int, default=MAX_BAROW,
                    help="cap barów 1h/parę; pozostałe interwały skalowane do TEGO SAMEGO okna")
    ap.add_argument("--interwaly", default="1d,4h,1h",
                    help="które interwały porównać (domyślnie 1d,4h,1h — od najtańszego)")
    ap.add_argument("--podglad", action="store_true",
                    help="zapisz zero-tokenowy podgląd w Kapitolu (HTML + wykres + link)")
    ap.add_argument("--wyrownaj-daty", action="store_true", default=True,
                    help="tnij po WSPÓLNYM zakresie DAT, nie po liczbie barów (domyślnie tak)")
    ap.add_argument("--bez-wyrownania", dest="wyrownaj_daty", action="store_false",
                    help="stare zachowanie: cap po liczbie barów (zakresy mogą się rozjechać)")
    args = ap.parse_args()

    pary = [p.strip().upper() for p in args.pary.split(",") if p.strip()]
    interwaly = [i.strip().lower() for i in args.interwaly.split(",") if i.strip()]
    zle = [i for i in interwaly if i not in INTERWALY]
    if zle:
        raise SystemExit(f"Nieznane interwały: {zle}. Dostępne: {sorted(INTERWALY)}")

    lata = args.bary / 24 / 365
    print(f"⚙️  Porównanie interwałów na TYM SAMYM oknie (~{lata:.1f} lat), "
          f"{len(pary)} par: {', '.join(pary)}")
    print(f"   Konfiguracja identyczna dla każdego interwału: {BAZA}\n")

    t0 = time.time()
    okno = wspolne_okno(pary, interwaly, args.bary) if args.wyrownaj_daty else None
    if okno and okno[0]:
        print(f"   Okno WSPÓLNE (wyrównane po datach): "
              f"{dt.datetime.utcfromtimestamp(okno[0] / 1000):%Y-%m-%d} → "
              f"{dt.datetime.utcfromtimestamp(okno[1] / 1000):%Y-%m-%d}\n", flush=True)
    wyniki = []
    for nr, interwal in enumerate(interwaly, 1):
        # --bary podawane w jednostce 1h; skalujemy przez MINUTY interwału, żeby każdy
        # bieg objął ten sam zakres kalendarzowy (15m → ×4 barów, 1d → ÷24).
        limit = max(1, args.bary * 60 // INTERWALY[interwal][2])
        wyniki.append(_bieg(pary, interwal, limit, nr, len(interwaly), okno))

    print("=" * 72)
    print(" PORÓWNANIE INTERWAŁÓW — to samo okno kalendarzowe, ta sama konfiguracja")
    print("=" * 72)
    print(f" {'interwał':10} {'ROI%':>9} {'maxDD%':>8} {'trades':>8} {'win rate':>10} {'barów/parę':>11}")
    for w in sorted(wyniki, key=lambda x: -x["roi"]):
        print(f" {w['interwal']:10} {w['roi']:>9.2f} {w['maxdd']:>8.2f} {w['trades']:>8} "
              f"{w['wr']:>9.1%} {w['barow']:>11}")
    print("-" * 72)

    najlepszy = max(wyniki, key=lambda x: x["roi"])
    najgorszy = min(wyniki, key=lambda x: x["roi"])
    stratne = [w for w in wyniki if w["roi"] < 0]
    print(f" Najlepszy: {najlepszy['interwal']} ({najlepszy['roi']:+.2f}%) | "
          f"najgorszy: {najgorszy['interwal']} ({najgorszy['roi']:+.2f}%) | "
          f"rozpiętość {najlepszy['roi'] - najgorszy['roi']:.2f} pp")
    if stratne:
        print(f" ⚠️ STRATNE interwały: {', '.join(w['interwal'] for w in stratne)} "
              "— testowanie sygnałów na stratnym interwale to szukanie przewagi w przegranej grze.")
    else:
        print(" ✅ Każdy badany interwał dodatni na tym oknie.")
    print("=" * 72)
    print(f"⏱️  Czas: {time.time() - t0:.0f}s")

    if args.podglad:
        from narzedzia.kapitol_podglad import raport_interwalow
        p = raport_interwalow(wyniki, pary, args.bary)
        print(f"🏛️ Podgląd Kapitolu: {p}")
        print(f"   Link: {p.as_uri()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
