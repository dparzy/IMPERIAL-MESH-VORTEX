"""
🎯 A/B strategy-MWU (W-362) — czy ważenie strategii realnym P&L poprawia P&L routingu.

Diagnoza (ANALIZA_AUTODOBOR_STRATEGII, A/B warstwy): statyczny dobór strategii (dobierz_najlepsze)
IGNORUJE zrealizowany zysk → routing (tryb strategia/filtr) często przegrywa z baseline. Naprawa ①:
online HedgeMWU keyed strategy_id uczony P&L zamkniętych trade'ów, mnożniki wracają do doboru.

Ten harness mierzy, czy włączenie strategy-MWU poprawia P&L w trybie, gdzie strategie NAPRAWDĘ
rządzą decyzją (tryb=strategia):
  OFF = backtest(tryb=strategia)                        — dobór czysto strukturalny (baseline)
  ON  = backtest(tryb=strategia, ucz_mwu_strategii=True) — dobór ważony online P&L

MWU uczy się ONLINE z JUŻ zamkniętych trade'ów (bez look-ahead) → NIE potrzeba podziału TRAIN/TEST;
pełny backtest, uczciwe porównanie na tych samych barach. Metryka: zwrot %/win-rate/liczba trade.

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ): para → arena (rodzaj='ab_strat_mwu') przed następną;
restart pomija policzone (--force). Pasek postępu na stderr (Prawo XXIV).

Użycie:
  python narzedzia/ab_strategy_mwu.py --max-barow 3000
  python narzedzia/ab_strategy_mwu.py --tryb filtr --max-barow 3000    # test też w trybie filtr
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

_MIN_TRADES = 10


def _metryki(eng) -> dict:
    s = eng.podsumowanie()
    ret = (s.kapital_koncowy / s.kapital_startowy - 1.0) if s.kapital_startowy else 0.0
    return {"ret": ret, "trades": s.total_trades, "wr": s.win_rate}


def analizuj_pare(bary, interwal, tryb="strategia", okno=250, min_barow=800, max_barow=None):
    from imperium.koloseum.backtest import backtest
    if max_barow:
        bary = bary[-max_barow:]
    if len(bary) < min_barow:
        return None
    off = _metryki(backtest("x", interwal, bary=bary, okno=okno, tryb=tryb))
    on = _metryki(backtest("x", interwal, bary=bary, okno=okno, tryb=tryb,
                           ucz_mwu_strategii=True))
    return {
        "bary": len(bary),
        "ret_off": off["ret"], "ret_on": on["ret"],
        "tr_off": off["trades"], "tr_on": on["trades"],
        "wr_off": off["wr"], "wr_on": on["wr"],
    }


def _rodzaj(tryb):
    return f"ab_strat_mwu_{tryb}"


def _nota(nazwa, w) -> str:
    return (f"para={nazwa};bary={w['bary']};retOFF={w['ret_off']:.4f};retON={w['ret_on']:.4f};"
            f"trOFF={w['tr_off']};trON={w['tr_on']};wrOFF={w['wr_off']:.4f};wrON={w['wr_on']:.4f}")


def _klucz(nazwa, interwal, okno, min_barow, max_barow) -> str:
    """Klucz areny = para + PODPIS KONFIGURACJI (Cubic P2). Bez tego zmiana okna/capu/interwału
    raportowała stary wynik pod nową etykietą — resume pomijał tylko RÓWNOWAŻNE eksperymenty."""
    return f"{nazwa}#i={interwal};okno={okno};min={min_barow};max={max_barow or 0}"


def _wczytaj_z_areny(nazwa, rodzaj, klucz):
    from imperium.biblioteki.arena_baza import pytaj_pomiary
    rek = pytaj_pomiary(rodzaj=rodzaj, neuron=klucz, limit=1)
    if not rek:
        return None
    p = dict(kv.split("=", 1) for kv in rek[0]["nota"].split(";") if "=" in kv)
    try:
        return {"para": nazwa, "bary": int(p["bary"]),
                "ret_off": float(p["retOFF"]), "ret_on": float(p["retON"]),
                "tr_off": int(p["trOFF"]), "tr_on": int(p["trON"]),
                "wr_off": float(p["wrOFF"]), "wr_on": float(p["wrON"]), "z_areny": True}
    except (KeyError, ValueError):
        return None


def raport(pliki, interwal, tryb="strategia", okno=250, min_barow=800,
           zapisz=True, max_barow=None, force=False) -> str:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    rodzaj = _rodzaj(tryb)
    per_para = []
    N = len(pliki)
    for i, plik in enumerate(pliki, 1):
        nazwa = Path(plik).name
        klucz = _klucz(nazwa, interwal, okno, min_barow, max_barow)
        if not force:
            z = _wczytaj_z_areny(nazwa, rodzaj, klucz)
            if z is not None:
                per_para.append(z)
                print(f"[{i}/{N}] {nazwa} — z areny: OFF={z['ret_off']:+.1%} ON={z['ret_on']:+.1%} "
                      f"(Δ={z['ret_on']-z['ret_off']:+.1%})", file=sys.stderr, flush=True)
                continue
        print(f"[{i}/{N}] {nazwa} — backtest tryb={tryb} OFF vs ON(mwu)…", file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
            w = analizuj_pare(bary, interwal, tryb=tryb, okno=okno, min_barow=min_barow,
                              max_barow=max_barow)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ {nazwa}: {e}", file=sys.stderr, flush=True)
            continue
        if w is None:
            print(f"[{i}/{N}] {nazwa} — za mało danych.", file=sys.stderr, flush=True)
            continue
        w["para"] = nazwa
        per_para.append(w)
        print(f"[{i}/{N}] {nazwa} — OFF={w['ret_off']:+.1%} ON={w['ret_on']:+.1%} "
              f"(Δ={w['ret_on']-w['ret_off']:+.1%}, tr {w['tr_off']}/{w['tr_on']})",
              file=sys.stderr, flush=True)
        if zapisz:
            zapisz_pomiar(rodzaj, klucz, w["ret_on"] - w["ret_off"], _nota(nazwa, w))
            print(f"    💾 arena: {nazwa} zapisana", file=sys.stderr, flush=True)

    if not per_para:
        return "🎯 A/B strategy-MWU — brak danych."

    konkluz = [p for p in per_para if (p["tr_off"] + p["tr_on"]) >= _MIN_TRADES]
    baza = konkluz or per_para
    # Cubic P2: portfel jako ŚREDNI zwrot/parę — suma % rosłaby z liczbą par (bez sensu jako P&L).
    toff = sum(p["ret_off"] for p in baza) / len(baza)
    ton = sum(p["ret_on"] for p in baza) / len(baza)
    lepsze = sum(1 for p in baza if p["ret_on"] > p["ret_off"])

    linie = [
        f"🎯 A/B strategy-MWU (W-362) — tryb={tryb}, {len(per_para)} par",
        "   OFF = dobór strukturalny | ON = + online MWU ważony P&L. Metryka: zwrot % (pełny backtest)",
        "",
        f"   {'PARA':<26} {'OFF':>8} {'ON':>8} {'Δ':>8} {'tr o/n':>9}",
    ]
    for p in sorted(per_para, key=lambda x: x["ret_on"] - x["ret_off"], reverse=True):
        linie.append(f"   {p['para']:<26} {p['ret_off']:>+7.1%} {p['ret_on']:>+7.1%} "
                     f"{p['ret_on']-p['ret_off']:>+7.1%} {p['tr_off']:>4}/{p['tr_on']:<4}")
    linie += [
        "",
        f"   ▸ PORTFEL (średni zwrot/parę, {len(baza)} par ≥{_MIN_TRADES} trade): "
        f"OFF={toff:+.1%}  ON={ton:+.1%}  Δ={ton-toff:+.1%}",
        f"   ▸ ON > OFF na {lepsze}/{len(baza)} par",
        "",
    ]
    if len(konkluz) < 2:
        linie.append("   ⚠️ WERDYKT: za mało par konkluzywnych — NIEKONKLUZYWNE.")
    elif ton > toff and lepsze * 2 >= len(baza):
        linie.append("   ✅ WERDYKT: strategy-MWU poprawia P&L routingu (ON>OFF, większość par). "
                     "Kandydat do flagi na żywo — decyzja Cezara (Prawo XVIII).")
    elif ton > toff:
        linie.append("   ⚠️ WERDYKT: ON>OFF w equity, ale nie na większości par — niestabilne.")
    else:
        linie.append("   ❌ WERDYKT: strategy-MWU nie poprawia P&L routingu. Samo ważenie P&L "
                     "nie ratuje warstwy strategii — flaga OFF (Prawo XV).")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="A/B strategy-MWU — dobór strategii ważony P&L (W-362)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv")
    # '4H' nie '4h' (2026-07-29): mała litera nie trafiała w klucze słowników Imperium
    # (m.in. formacja legionów Legatusa) i mierzyła rój w konfiguracji, którą produkcja
    # nigdy nie gra. Wyniki tego narzędzia sprzed tej daty pochodzą z etykiety '4h'.
    p.add_argument("--interwal", default="4H")
    p.add_argument("--tryb", default="strategia", choices=["strategia", "filtr"])
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--min-barow", type=int, default=800)
    p.add_argument("--max-barow", type=int, default=3000)
    p.add_argument("--bez-zapisu", action="store_true")
    p.add_argument("--force", action="store_true")
    args = p.parse_args()

    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print("Brak plików."); sys.exit(1)
    print(raport(pliki, args.interwal, tryb=args.tryb, okno=args.okno, min_barow=args.min_barow,
                 zapisz=not args.bez_zapisu, max_barow=args.max_barow, force=args.force))
