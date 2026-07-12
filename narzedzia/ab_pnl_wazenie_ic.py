"""
💰 A/B NA P&L — ważenie głosów IC w PEŁNEJ ścieżce decyzyjnej (W-361, hipoteza B).

Poprzedni pomiar (narzedzia/ab_wazenie_ic.py) mierzył SAM ZNAK agregatu Legatusa (+3.3pp OOS),
z wyłączonym wetem progowym (min_przewaga=0.0). To konieczne, ale NIEwystarczające: realny zysk
rodzi się dopiero po wecie (min_przewaga=0.55), sizingu, SL/TP i bramkach reżimu. Tu mierzymy
rzecz, która NAPRAWDĘ decyduje — P&L pełnego backtestu OFF vs ON. Dopiero zielony P&L uzasadni
wpięcie w runtime + przełącznik (ZASADA WPIĘCIA, decyzja Cezara — Prawo XVIII).

METODA (OOS, zero look-ahead — ZASADA WPIĘCIA + Prawo I):
  1. Podział czasowy bary → TRAIN (`frac`) / TEST (reszta = OOS).
  2. IC kierunkowy per-neuron z TRAIN: backtest(TRAIN, zbieraj_sygnaly) → oblicz_wagi_ic
     (kanoniczna, jedno źródło prawdy). Wagi liczone WYŁĄCZNIE z przeszłości.
  3. Pełny backtest na TEST DWA razy — identyczna konfiguracja, różni się tylko flaga:
       OFF = wazenie_ic=False (bazowa ścieżka — domyślne zachowanie Imperium)
       ON  = wazenie_ic=True, wagi_ic z TRAIN (Legatus.ustaw_wagi_ic w backtescie)
  4. Metryki z engine.podsumowanie(): zwrot % (kapitał końcowy), liczba transakcji,
     win-rate, profit factor. Δ = zwrot_ON − zwrot_OFF.
  5. Werdykt: ON leczy P&L gdy suma equity ON > OFF ORAZ ON>OFF na większości par
     z DOSTATECZNĄ liczbą transakcji (mało trade'ów = niekonkluzywne, nie werdykt).

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ): każda para → arena_wyniki.db (rodzaj='ab_pnl_ic')
ZANIM ruszy następna; restart pomija policzone (--force wymusza). Pasek postępu na stderr
(Prawo XXIV). TEST używa `okno` barów z ogona TRAIN jako rozgrzewki wskaźników (nie etykiet —
zero look-ahead w decyzji), by nie tracić barów testowych na warmup.

Użycie:
  python narzedzia/ab_pnl_wazenie_ic.py                                 # 5 par 4h
  python narzedzia/ab_pnl_wazenie_ic.py --glob "dane/4h/Binance_*_4h.csv" --interwal 4h
  python narzedzia/ab_pnl_wazenie_ic.py --frac 0.6 --max-barow 6000 --force
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

_RODZAJ = "ab_pnl_ic"
# Minimalna liczba transakcji (OFF+ON łącznie), by para liczyła się do werdyktu —
# garść trade'ów to szum, nie dowód (Prawo I: pomiar, nie anegdota).
_MIN_TRADES = 10


def _metryki(eng) -> dict:
    """Zwrot %, liczba transakcji, win-rate, profit factor z podsumowania silnika."""
    s = eng.podsumowanie()
    ret = (s.kapital_koncowy / s.kapital_startowy - 1.0) if s.kapital_startowy else 0.0
    return {"ret": ret, "trades": s.total_trades, "wr": s.win_rate, "pf": s.profit_factor}


def analizuj_pare(bary, interwal, frac=0.6, okno=250, min_trade_barow=400, max_barow=None):
    """Zwraca dict z metrykami OFF/ON na TEST (OOS) dla jednej pary lub None gdy za mało danych."""
    from imperium.koloseum.backtest import backtest
    from imperium.legiony.legatus import oblicz_wagi_ic

    if max_barow:
        bary = bary[-max_barow:]
    n = len(bary)
    podzial = int(n * frac)
    # TRAIN musi zmieścić okno + trochę decyzji; TEST musi mieć okno rozgrzewki + decyzje.
    if podzial <= okno + 50 or (n - podzial) < min_trade_barow:
        return None

    bary_train = bary[:podzial]
    bary_test = bary[podzial - okno:]          # okno barów TRAIN = rozgrzewka wskaźników (nie etykiet)

    # 1) IC z TRAIN (tylko kierunki + etykiety forward — bez pełnych sygnałów, szybciej).
    eng_tr = backtest("x", interwal, bary=bary_train, okno=okno, zbieraj_sygnaly=True)
    dir_tr = getattr(eng_tr, "historia_sygnalow", []) or []
    wyn_tr = getattr(eng_tr, "historia_wynikow", []) or []
    if len(dir_tr) < 50:
        return None
    wagi_ic = oblicz_wagi_ic(dir_tr, wyn_tr)
    if not wagi_ic:
        return None

    # 2) Pełny backtest TEST OFF vs ON — identyczna konfiguracja, różni się tylko flaga.
    eng_off = backtest("x", interwal, bary=bary_test, okno=okno)
    eng_on = backtest("x", interwal, bary=bary_test, okno=okno,
                      wazenie_ic=True, wagi_ic=wagi_ic)
    m_off, m_on = _metryki(eng_off), _metryki(eng_on)
    return {
        "bary_test": n - podzial,
        "ret_off": m_off["ret"], "ret_on": m_on["ret"],
        "trades_off": m_off["trades"], "trades_on": m_on["trades"],
        "wr_off": m_off["wr"], "wr_on": m_on["wr"],
        "pf_off": m_off["pf"], "pf_on": m_on["pf"],
        "neuronow_wazonych": len(wagi_ic),
    }


def _status_werdyktu(n_konkluzywne, baza_n, total_off, total_on, lepsze) -> str:
    """Czysta logika werdyktu (Prawo I — z P&L). Wyodrębniona do testów granic."""
    if n_konkluzywne < 2:
        return ("⚠️ WERDYKT: za mało par z dostateczną liczbą transakcji — NIEKONKLUZYWNE. "
                "Zwiększ --max-barow lub liczbę par; nie zmieniaj flagi na tak cienkiej próbie.")
    if total_on > total_off and lepsze * 2 >= baza_n:
        return ("✅ WERDYKT: ważenie IC poprawia P&L OOS (equity ON>OFF, większość par). "
                "Kandydat do wpięcia w runtime + flaga na żywo — decyzja Cezara (Prawo XVIII).")
    if total_on > total_off:
        return ("⚠️ WERDYKT: equity ON>OFF, ale nie na większości par — sygnał niestabilny. "
                "Warto poszerzyć próbę zanim ruszać runtime.")
    return ("❌ WERDYKT: ważenie IC NIE poprawia P&L (equity ON≤OFF). Przewaga znaku "
            "(+3.3pp) jest zjadana przez weto/sizing — zostawić flagę OFF (Prawo XV: "
            "moduł zwalidowany, ale nie wpinamy bez korzyści w kasie).")


def _nota(nazwa, frac, w) -> str:
    return (f"para={nazwa};frac={frac};test={w['bary_test']};"
            f"retOFF={w['ret_off']:.4f};retON={w['ret_on']:.4f};"
            f"trOFF={w['trades_off']};trON={w['trades_on']};"
            f"wrOFF={w['wr_off']:.4f};wrON={w['wr_on']:.4f};"
            f"pfOFF={w['pf_off']:.4f};pfON={w['pf_on']:.4f}")


def _wczytaj_z_areny(nazwa):
    """Wznawialność: odczytaj policzoną cząstkę z areny (nota → dict) lub None."""
    from imperium.biblioteki.arena_baza import pytaj_pomiary
    rekordy = pytaj_pomiary(rodzaj=_RODZAJ, neuron=nazwa, limit=1)
    if not rekordy:
        return None
    pola = dict(kv.split("=", 1) for kv in rekordy[0]["nota"].split(";") if "=" in kv)
    try:
        return {
            "para": nazwa,
            "bary_test": int(pola["test"]),
            "ret_off": float(pola["retOFF"]), "ret_on": float(pola["retON"]),
            "trades_off": int(pola["trOFF"]), "trades_on": int(pola["trON"]),
            "wr_off": float(pola["wrOFF"]), "wr_on": float(pola["wrON"]),
            "pf_off": float(pola["pfOFF"]), "pf_on": float(pola["pfON"]),
            "z_areny": True,
        }
    except (KeyError, ValueError):
        return None


def raport(pliki, interwal, frac=0.6, okno=250, min_trade_barow=400,
           zapisz=True, max_barow=None, force=False) -> str:
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
                d = zapisana["ret_on"] - zapisana["ret_off"]
                print(f"[{i}/{N}] {nazwa} — z areny (pomijam): "
                      f"OFF={zapisana['ret_off']:+.1%} ON={zapisana['ret_on']:+.1%} "
                      f"(Δ={d:+.1%})", file=sys.stderr, flush=True)
                continue
        print(f"[{i}/{N}] {nazwa} — TRAIN→IC + backtest TEST OFF/ON…",
              file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
            w = analizuj_pare(bary, interwal, frac=frac, okno=okno,
                              min_trade_barow=min_trade_barow, max_barow=max_barow)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ {nazwa}: {e}", file=sys.stderr, flush=True)
            continue
        if w is None:
            print(f"[{i}/{N}] {nazwa} — za mało danych, pomijam.", file=sys.stderr, flush=True)
            continue
        w["para"] = nazwa
        per_para.append(w)
        d = w["ret_on"] - w["ret_off"]
        print(f"[{i}/{N}] {nazwa} — OFF={w['ret_off']:+.1%} ON={w['ret_on']:+.1%} "
              f"(Δ={d:+.1%}, tr OFF/ON={w['trades_off']}/{w['trades_on']}, test={w['bary_test']})",
              file=sys.stderr, flush=True)
        if zapisz:
            zapisz_pomiar(_RODZAJ, nazwa, d, _nota(nazwa, frac, w))
            print(f"    💾 arena: cząstka {nazwa} zapisana", file=sys.stderr, flush=True)

    if not per_para:
        return "💰 A/B P&L WAŻENIE IC — brak wystarczających danych na żadnej parze."

    # Agregat portfelowy: każda para startuje z tym samym kapitałem → suma zwrotów = equity portfela.
    konkluzywne = [p for p in per_para if (p["trades_off"] + p["trades_on"]) >= _MIN_TRADES]
    baza = konkluzywne or per_para
    total_off = sum(p["ret_off"] for p in baza)
    total_on = sum(p["ret_on"] for p in baza)
    lepsze = sum(1 for p in baza if p["ret_on"] > p["ret_off"])
    tr_off = sum(p["trades_off"] for p in per_para)
    tr_on = sum(p["trades_on"] for p in per_para)

    linie = [
        f"💰 A/B P&L WAŻENIE IC — PEŁNY backtest (W-361) — {len(per_para)} par, OOS (frac={frac})",
        "   OFF = bazowa ścieżka | ON = + ważenie IC. Metryka: zwrot % TEST (weto/sizing/SL aktywne)",
        "",
        f"   {'PARA':<26} {'OFF%':>8} {'ON%':>8} {'Δ%':>8} {'trOFF':>6} {'trON':>6} {'wrON':>6}",
    ]
    for p in sorted(per_para, key=lambda x: x["ret_on"] - x["ret_off"], reverse=True):
        d = p["ret_on"] - p["ret_off"]
        linie.append(f"   {p['para']:<26} {p['ret_off']:>+7.1%} {p['ret_on']:>+7.1%} "
                     f"{d:>+7.1%} {p['trades_off']:>6} {p['trades_on']:>6} {p['wr_on']:>5.0%}")
    linie += [
        "",
        f"   ▸ PORTFEL (suma zwrotów, {len(baza)} par konkluzywnych ≥{_MIN_TRADES} trade): "
        f"OFF={total_off:+.1%}  ON={total_on:+.1%}  Δ={total_on - total_off:+.1%}",
        f"   ▸ ON > OFF na {lepsze}/{len(baza)} parach | transakcje łącznie OFF/ON={tr_off}/{tr_on}",
        "",
    ]
    # Werdykt (Prawo I — z pomiaru P&L, nie z trafności znaku). Decyzja o flagi = Cezar.
    linie.append("   " + _status_werdyktu(len(konkluzywne), len(baza), total_off, total_on, lepsze))
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="A/B P&L ważenie IC — pełny backtest (W-361, OOS)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv", help="wzorzec par CSV")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--frac", type=float, default=0.6, help="udział TRAIN (reszta = OOS test)")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--min-trade-barow", type=int, default=400, help="min barów TEST, by liczyć parę")
    p.add_argument("--max-barow", type=int, default=6000, help="ogranicz do ostatnich N barów/parę")
    p.add_argument("--bez-zapisu", action="store_true", help="nie zapisuj cząstek do areny")
    p.add_argument("--force", action="store_true", help="przelicz nawet policzone pary")
    args = p.parse_args()

    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print("Brak plików pasujących do wzorca."); sys.exit(1)
    print(raport(pliki, args.interwal, frac=args.frac, okno=args.okno,
                 min_trade_barow=args.min_trade_barow, zapisz=not args.bez_zapisu,
                 max_barow=args.max_barow, force=args.force))
