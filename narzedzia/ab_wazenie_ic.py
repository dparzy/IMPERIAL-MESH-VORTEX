"""
⚖️ A/B NA ŻYWO — ważenie głosów IC w REALNYM Legatusie (W-361, hipoteza B).

Offline (narzedzia/hipoteza_b.py) porównał agregat CZYSTYCH głosów: sign(Σ głos) vs
sign(Σ IC·głos), +3.6pp OOS. To był UPROSZCZONY agregator. Tu robimy A/B na PRAWDZIWYM
Legatus._agreguj — z wagami reżimowymi już wliczonymi w pewnosc_finalna·waga (raport.sygnaly),
progami i wetem — żeby zmierzyć, czy przełącznik `wazenie_ic` pomaga REALNEJ ścieżce decyzyjnej.
Dopiero zielony wynik uzasadni przełączenie flagi na sztywno (ZASADA WPIĘCIA, decyzja Cezara).

METODA (OOS, zero look-ahead — ZASADA WPIĘCIA + Prawo I):
  1. backtest(zbieraj_sygnaly + zbieraj_pelne_sygnaly) → per bar: pełne SygnalNeuronu
     (już z wagami reżimowymi), kierunki i etykieta forward (±1). Bary z decyzją, bez look-ahead.
  2. Podział czasowy TRAIN (`frac`) / TEST (reszta = OOS).
  3. IC kierunkowy per-neuron liczony na TRAIN kanoniczną oblicz_wagi_ic (jedno źródło prawdy).
  4. Na TEST replay tych samych sygnałów przez Legatus._agreguj DWA razy:
       OFF = ważenie_ic wyłączone (bazowa agregacja — odtwarza decyzję backtestu 1:1)
       ON  = ważenie_ic włączone wagami z TRAIN (×|IC|, IC<0 odwraca kierunek)
     Trafność = odsetek barów z kierunkiem != NEUTRAL, gdzie znak == etykieta.
  5. Werdykt: ON leczy gdy acc_ON > acc_OFF ORAZ acc_ON > 50% (spójnie na parach).

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ): każda para → zapis do arena_wyniki.db
(rodzaj='ab_wazenie_ic') ZANIM ruszy następna; restart pomija już policzone (--force wymusza
przeliczenie). Pasek postępu na stderr (Prawo XXIV). Legatus min_przewaga=0.0/min_neuronow=1 —
mierzymy SAM znak agregatu (jak offline), bez interferencji weta progowego (identyczne OFF i ON).

Użycie:
  python narzedzia/ab_wazenie_ic.py                                  # 5 par 4h
  python narzedzia/ab_wazenie_ic.py --glob "dane/4h/Binance_*_4h.csv" --interwal 4h
  python narzedzia/ab_wazenie_ic.py --frac 0.6 --max-barow 6000 --force
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

_RODZAJ = "ab_wazenie_ic"
_KIER_ZNAK = {"LONG": 1, "SHORT": -1}


def _trafnosc_legatus(leg, pelne, wyniki) -> tuple:
    """Trafność znaku agregatu Legatusa na zadanym zbiorze (kierunek != NEUTRAL).

    leg:    Legatus (OFF lub z ustaw_wagi_ic — ON). Reużywany dla obu wariantów.
    pelne:  lista barów, każdy = lista SygnalNeuronu (z pewnosc_finalna·waga).
    wyniki: etykiety forward ∈ {+1, -1} RÓWNOLEGLE do pelne.
    Zwraca (trafnosc, liczba_barow_decyzyjnych)."""
    trafne = 0
    aktywne = 0
    for sygnaly, etykieta in zip(pelne, wyniki):
        raport = leg._agreguj("AB", "AB", "NORMAL", sygnaly)
        znak = _KIER_ZNAK.get(raport.kierunek, 0)
        if znak == 0:
            continue          # NEUTRAL — brak decyzji kierunkowej, nie liczymy
        aktywne += 1
        if (znak > 0) == (etykieta > 0):
            trafne += 1
    if aktywne == 0:
        return float("nan"), 0
    return trafne / aktywne, aktywne


def analizuj_pare(bary, interwal, frac=0.6, okno=250, min_glosow=20, max_barow=None):
    """Zwraca dict z acc_OFF/acc_ON na TEST (OOS) dla jednej pary lub None gdy za mało danych."""
    from imperium.koloseum.backtest import backtest
    from imperium.legiony.legatus import Legatus, oblicz_wagi_ic

    if max_barow:
        bary = bary[-max_barow:]
    eng = backtest("x", interwal, bary=bary, okno=okno,
                   zbieraj_sygnaly=True, zbieraj_pelne_sygnaly=True)
    directions = getattr(eng, "historia_sygnalow", []) or []
    pelne = getattr(eng, "historia_pelnych_sygnalow", []) or []
    wyniki = getattr(eng, "historia_wynikow", []) or []
    n = len(pelne)
    if n < min_glosow * 2 or len(directions) != n or len(wyniki) != n:
        return None

    podzial = int(n * frac)
    if n - podzial < min_glosow:
        return None
    dir_train, wyn_train = directions[:podzial], wyniki[:podzial]
    pelne_test, wyn_test = pelne[podzial:], wyniki[podzial:]

    wagi_ic = oblicz_wagi_ic(dir_train, wyn_train)

    # Mierzymy SAM znak agregatu (jak offline): brak weta progowego, identyczne OFF i ON.
    leg = Legatus(neurony=[], min_neuronow=1, min_przewaga=0.0)
    acc_off, akt_off = _trafnosc_legatus(leg, pelne_test, wyn_test)   # OFF
    leg.ustaw_wagi_ic(wagi_ic, wlacz=True)
    acc_on, akt_on = _trafnosc_legatus(leg, pelne_test, wyn_test)     # ON
    return {
        "bary_train": podzial, "bary_test": n - podzial,
        "acc_off": acc_off, "akt_off": akt_off,
        "acc_on": acc_on, "akt_on": akt_on,
        "neuronow_wazonych": len(wagi_ic),
    }


def _nota(nazwa, frac, w) -> str:
    return (f"para={nazwa};frac={frac};test={w['bary_test']};"
            f"accOFF={w['acc_off']:.4f};accON={w['acc_on']:.4f};"
            f"aktOFF={w['akt_off']};aktON={w['akt_on']}")


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
            "acc_off": float(pola["accOFF"]), "acc_on": float(pola["accON"]),
            "akt_off": int(pola["aktOFF"]), "akt_on": int(pola["aktON"]),
            "z_areny": True,
        }
    except (KeyError, ValueError):
        return None


def raport(pliki, interwal, frac=0.6, okno=250, min_glosow=20,
           zapisz=True, max_barow=None, force=False) -> str:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    from imperium.biblioteki.arena_baza import zapisz_pomiar
    per_para = []
    N = len(pliki)
    for i, plik in enumerate(pliki, 1):
        nazwa = Path(plik).name
        # Wznawialność — pomiń już policzone (chyba że --force). ZASADA ANALIZY CZĄSTKOWEJ.
        if not force:
            zapisana = _wczytaj_z_areny(nazwa)
            if zapisana is not None:
                per_para.append(zapisana)
                d = zapisana["acc_on"] - zapisana["acc_off"]
                print(f"[{i}/{N}] {nazwa} — z areny (pomijam): "
                      f"OFF={zapisana['acc_off']:.1%} ON={zapisana['acc_on']:.1%} "
                      f"(Δ={d:+.1%})", file=sys.stderr, flush=True)
                continue
        print(f"[{i}/{N}] {nazwa} — wczytuję + backtest (pełne sygnały)…",
              file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
            w = analizuj_pare(bary, interwal, frac=frac, okno=okno,
                              min_glosow=min_glosow, max_barow=max_barow)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ {nazwa}: {e}", file=sys.stderr, flush=True)
            continue
        if w is None:
            print(f"[{i}/{N}] {nazwa} — za mało danych, pomijam.", file=sys.stderr, flush=True)
            continue
        w["para"] = nazwa
        per_para.append(w)
        d = w["acc_on"] - w["acc_off"]
        print(f"[{i}/{N}] {nazwa} — OFF={w['acc_off']:.1%} ON={w['acc_on']:.1%} "
              f"(Δ={d:+.1%}, test={w['bary_test']})", file=sys.stderr, flush=True)
        if zapisz:
            zapisz_pomiar(_RODZAJ, nazwa, d, _nota(nazwa, frac, w))
            print(f"    💾 arena: cząstka {nazwa} zapisana", file=sys.stderr, flush=True)

    if not per_para:
        return "⚖️ A/B WAŻENIE IC — brak wystarczających danych na żadnej parze."

    # Agregat po parach (waga = liczba barów TEST — pary z większym OOS ważą więcej).
    def _wazona(klucz_acc, klucz_akt):
        licz = sum(p[klucz_acc] * p[klucz_akt] for p in per_para if p[klucz_acc] == p[klucz_acc])
        mian = sum(p[klucz_akt] for p in per_para if p[klucz_acc] == p[klucz_acc])
        return (licz / mian) if mian else float("nan")

    glob_off = _wazona("acc_off", "akt_off")
    glob_on = _wazona("acc_on", "akt_on")
    lepsze = sum(1 for p in per_para if p["acc_on"] > p["acc_off"])

    linie = [
        f"⚖️ A/B WAŻENIE IC — REALNY Legatus (W-361) — {len(per_para)} par, OOS (frac={frac})",
        "   OFF = agregacja bazowa (pewnosc·waga) | ON = + ważenie IC (×|IC|, znak odwraca)",
        "",
        f"   {'PARA':<26} {'OFF':>8} {'ON':>8} {'Δ':>8} {'test':>6}",
    ]
    for p in sorted(per_para, key=lambda x: x["acc_on"] - x["acc_off"], reverse=True):
        d = p["acc_on"] - p["acc_off"]
        linie.append(f"   {p['para']:<26} {p['acc_off']:>7.1%} {p['acc_on']:>7.1%} "
                     f"{d:>+7.1%} {p['bary_test']:>6}")
    linie += [
        "",
        f"   ▸ GLOBALNIE (ważone barami OOS): OFF={glob_off:.1%}  ON={glob_on:.1%}  "
        f"Δ={glob_on - glob_off:+.1%}",
        f"   ▸ ON > OFF na {lepsze}/{len(per_para)} parach",
        "",
    ]
    # Werdykt (Prawo I — z pomiaru, nie z wiary). Decyzja o flagi = Cezar (ZASADA WPIĘCIA).
    if glob_on > glob_off and glob_on > 0.50:
        linie.append("   ✅ WERDYKT: ważenie IC leczy REALNY Legatus (ON>OFF i ON>50% OOS). "
                     "Kandydat do włączenia flagi na żywo — decyzja Cezara (Prawo XVIII).")
    elif glob_on > glob_off:
        linie.append("   ⚠️ WERDYKT: ON > OFF, ale ≤50% OOS. Ważenie POMAGA, lecz realny rój "
                     "nadal nie bije losowości — sam re-weighting nie wystarcza.")
    else:
        linie.append("   ❌ WERDYKT: ON nie bije OFF na realnym Legatusie. W przeciwieństwie do "
                     "offline (czyste głosy) — realne wagi reżimowe już częściowo robią tę robotę.")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="A/B ważenie IC na realnym Legatusie (W-361, OOS)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv", help="wzorzec par CSV")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--frac", type=float, default=0.6, help="udział TRAIN (reszta = OOS test)")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--min-glosow", type=int, default=20)
    p.add_argument("--max-barow", type=int, default=6000, help="ogranicz do ostatnich N barów/parę")
    p.add_argument("--bez-zapisu", action="store_true", help="nie zapisuj cząstek do areny")
    p.add_argument("--force", action="store_true", help="przelicz nawet policzone pary")
    args = p.parse_args()

    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print("Brak plików pasujących do wzorca."); sys.exit(1)
    print(raport(pliki, args.interwal, frac=args.frac, okno=args.okno,
                 min_glosow=args.min_glosow, zapisz=not args.bez_zapisu,
                 max_barow=args.max_barow, force=args.force))
