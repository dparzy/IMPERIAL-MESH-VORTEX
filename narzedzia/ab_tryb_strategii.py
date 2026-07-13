"""
🎯 A/B WARSTWY STRATEGII — czy 20 szkiców (SZKIC) dokłada wartość w ścieżce decyzyjnej.

Kontekst: mamy 20 strategii (rejestr_strategii.py), wszystkie status SZKIC — zmapowane na
żywe neurony, ale ZERO zwalidowanych na P&L (Prawo XV: uśpiony potencjał). Legatus dobiera
je przez dobierz_najlepsze; Dyrygent używa ich zależnie od `tryb`:
  • agregat   — strategie DORADCZE (nie bramkują); kierunek z głosowania neuronów (baseline).
  • filtr     — wejście tylko gdy top-strategia ZGADZA się z neuronami (Opcja 1, zaostrza).
  • strategia — kierunek z top-1 strategii; neurony potwierdzają pewność (Opcja 2).

Ten harness mierzy P&L pełnego backtestu w KAŻDYM trybie i porównuje z baseline (agregat),
by odpowiedzieć: czy warstwa szkiców POMAGA, czy SZKODZI (Prawo I — pomiar, nie wiara).
Strategie to STAŁE przepisy (zero uczonych parametrów) → brak look-ahead, backtest na pełnych
danych (bez podziału TRAIN/TEST). Werdykt na poziomie WARSTWY; atrybucję per-strategia
(które z 20 niosą przewagę) robi osobny krok 2b.

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ): każda para → arena_wyniki.db (rodzaj='ab_tryb_strat')
ZANIM ruszy następna; restart pomija policzone (--force wymusza). Pasek postępu na stderr (Prawo XXIV).

Użycie:
  python narzedzia/ab_tryb_strategii.py                                # 15 par 4h
  python narzedzia/ab_tryb_strategii.py --glob "dane/4h/Binance_*_4h.csv" --max-barow 6000
"""

from __future__ import annotations

import argparse
import glob as _glob
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_RODZAJ = "ab_tryb_strat"
_TRYBY = ("agregat", "filtr", "strategia")
_MIN_TRADES = 10


def _metryki(eng) -> dict:
    s = eng.podsumowanie()
    ret = (s.kapital_koncowy / s.kapital_startowy - 1.0) if s.kapital_startowy else 0.0
    return {"ret": ret, "trades": s.total_trades, "wr": s.win_rate}


def analizuj_pare(bary, interwal, okno=250, min_barow=800, max_barow=None):
    """Zwraca dict z metrykami per tryb dla jednej pary lub None gdy za mało danych."""
    from imperium.koloseum.backtest import backtest

    if max_barow:
        bary = bary[-max_barow:]
    if len(bary) < min_barow:
        return None
    wynik = {"bary": len(bary)}
    for tr in _TRYBY:
        m = _metryki(backtest("x", interwal, bary=bary, okno=okno, tryb=tr))
        wynik[f"ret_{tr}"] = m["ret"]
        wynik[f"tr_{tr}"] = m["trades"]
        wynik[f"wr_{tr}"] = m["wr"]
    return wynik


def _nota(nazwa, w) -> str:
    czesci = [f"para={nazwa}", f"bary={w['bary']}"]
    for tr in _TRYBY:
        czesci.append(f"ret_{tr}={w[f'ret_{tr}']:.4f}")
        czesci.append(f"tr_{tr}={w[f'tr_{tr}']}")
        czesci.append(f"wr_{tr}={w[f'wr_{tr}']:.4f}")
    return ";".join(czesci)


def _wczytaj_z_areny(nazwa):
    from imperium.biblioteki.arena_baza import pytaj_pomiary
    rekordy = pytaj_pomiary(rodzaj=_RODZAJ, neuron=nazwa, limit=1)
    if not rekordy:
        return None
    pola = dict(kv.split("=", 1) for kv in rekordy[0]["nota"].split(";") if "=" in kv)
    try:
        w = {"para": nazwa, "bary": int(pola["bary"]), "z_areny": True}
        for tr in _TRYBY:
            w[f"ret_{tr}"] = float(pola[f"ret_{tr}"])
            w[f"tr_{tr}"] = int(pola[f"tr_{tr}"])
            w[f"wr_{tr}"] = float(pola[f"wr_{tr}"])
        return w
    except (KeyError, ValueError):
        return None


def raport(pliki, interwal, okno=250, min_barow=800, zapisz=True, max_barow=None, force=False) -> str:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    per_para = []
    N = len(pliki)
    for i, plik in enumerate(pliki, 1):
        nazwa = Path(plik).name
        if not force:
            zapisana = _wczytaj_z_areny(nazwa)
            if zapisana is not None:
                per_para.append(zapisana)
                print(f"[{i}/{N}] {nazwa} — z areny (pomijam): "
                      f"agr={zapisana['ret_agregat']:+.1%} filtr={zapisana['ret_filtr']:+.1%} "
                      f"strat={zapisana['ret_strategia']:+.1%}", file=sys.stderr, flush=True)
                continue
        print(f"[{i}/{N}] {nazwa} — backtest 3 tryby (agregat/filtr/strategia)…",
              file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
            w = analizuj_pare(bary, interwal, okno=okno, min_barow=min_barow, max_barow=max_barow)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ {nazwa}: {e}", file=sys.stderr, flush=True)
            continue
        if w is None:
            print(f"[{i}/{N}] {nazwa} — za mało danych, pomijam.", file=sys.stderr, flush=True)
            continue
        w["para"] = nazwa
        per_para.append(w)
        print(f"[{i}/{N}] {nazwa} — agr={w['ret_agregat']:+.1%} filtr={w['ret_filtr']:+.1%} "
              f"strat={w['ret_strategia']:+.1%} (tr {w['tr_agregat']}/{w['tr_filtr']}/{w['tr_strategia']})",
              file=sys.stderr, flush=True)
        if zapisz:
            # delta = najlepszy z routingu strategii − baseline (dodatnia = warstwa pomaga)
            delta = max(w["ret_filtr"], w["ret_strategia"]) - w["ret_agregat"]
            zapisz_pomiar(_RODZAJ, nazwa, delta, _nota(nazwa, w))
            print(f"    💾 arena: cząstka {nazwa} zapisana", file=sys.stderr, flush=True)

    if not per_para:
        return "🎯 A/B WARSTWY STRATEGII — brak wystarczających danych na żadnej parze."

    total = {tr: sum(p[f"ret_{tr}"] for p in per_para) for tr in _TRYBY}
    filtr_lepszy = sum(1 for p in per_para if p["ret_filtr"] > p["ret_agregat"])
    strat_lepszy = sum(1 for p in per_para if p["ret_strategia"] > p["ret_agregat"])
    n = len(per_para)

    linie = [
        f"🎯 A/B WARSTWY STRATEGII — {n} par (backtest pełny, {len(_TRYBY)} tryby)",
        "   agregat = baseline (strategie doradcze) | filtr = strat∧neurony | strategia = kierunek z strat",
        "",
        f"   {'PARA':<26} {'AGREGAT':>9} {'FILTR':>9} {'STRATEG':>9}  {'tr a/f/s':>12}",
    ]
    for p in sorted(per_para, key=lambda x: x["ret_agregat"], reverse=True):
        linie.append(f"   {p['para']:<26} {p['ret_agregat']:>+8.1%} {p['ret_filtr']:>+8.1%} "
                     f"{p['ret_strategia']:>+8.1%}  {p['tr_agregat']:>3}/{p['tr_filtr']:>3}/{p['tr_strategia']:>3}")
    linie += [
        "",
        f"   ▸ PORTFEL (suma zwrotów): agregat={total['agregat']:+.1%}  "
        f"filtr={total['filtr']:+.1%}  strategia={total['strategia']:+.1%}",
        f"   ▸ filtr > agregat na {filtr_lepszy}/{n} par | strategia > agregat na {strat_lepszy}/{n} par",
        "",
    ]
    # Werdykt (Prawo I). Baseline = agregat. Warstwa pomaga tylko gdy bije baseline w equity.
    najlepszy_routing = max(total["filtr"], total["strategia"])
    if najlepszy_routing > total["agregat"] and max(filtr_lepszy, strat_lepszy) * 2 >= n:
        linie.append("   ✅ WERDYKT: routing strategii bije baseline — warstwa dokłada wartość. "
                     "Krok 2b: atrybucja per-strategia (które z 20 niosą przewagę).")
    elif najlepszy_routing > total["agregat"]:
        linie.append("   ⚠️ WERDYKT: routing bije baseline w equity, ale nie na większości par — "
                     "sygnał niestabilny, drążyć per-strategia (2b) zanim wnioski.")
    else:
        linie.append("   ❌ WERDYKT: żaden tryb strategii nie bije baseline (agregat). 20 szkiców "
                     "jako WARSTWA szkodzi lub jest neutralne — przed promocją SZKIC trzeba je "
                     "przerobić/odchudzić (2b pokaże, które konkretnie ciągną w dół).")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="A/B warstwy strategii — agregat vs filtr vs strategia (P&L)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv", help="wzorzec par CSV")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--min-barow", type=int, default=800, help="min barów, by liczyć parę")
    p.add_argument("--max-barow", type=int, default=6000, help="ogranicz do ostatnich N barów/parę")
    p.add_argument("--bez-zapisu", action="store_true", help="nie zapisuj cząstek do areny")
    p.add_argument("--force", action="store_true", help="przelicz nawet policzone pary")
    args = p.parse_args()

    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print("Brak plików pasujących do wzorca."); sys.exit(1)
    print(raport(pliki, args.interwal, okno=args.okno, min_barow=args.min_barow,
                 zapisz=not args.bez_zapisu, max_barow=args.max_barow, force=args.force))
