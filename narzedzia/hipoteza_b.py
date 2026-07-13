"""
🧪 HIPOTEZA B — czy WAŻENIE GŁOSÓW IC leczy wąskie gardło agregacji (Prawo XV/XVI).

Diagnoza triady (2026-07-06): skill SIEDZI w neuronach (stabilny IC), GINIE w warstwie
agregacji — base accuracy roju 48.3% < 50% przy RÓWNEJ wadze głosów. Teoria za naprawą:
Grinold & Kahn (BIB-025), Fundamental Law: sygnał = Σ IC_i · głos_i. Głos neuronu powinien
ważyć PROPORCJONALNIE do jego zmierzonego IC (skorygowany o znak — neuron mylący się
systematycznie GŁOSUJE ODWROTNIE), nie równo.

POMIAR (offline, OOS, bez dotykania ścieżki decyzyjnej — ZASADA WPIĘCIA):
  1. backtest(zbieraj_sygnaly=True) → per bar {neuron: kierunek} + etykieta forward (±1).
  2. Podział czasowy: TRAIN (pierwsze `frac`) / TEST (reszta = OOS, zero look-ahead).
  3. Na TRAIN licz per-neuron IC kierunkowy = średnia(głos_i · etykieta) po barach z głosem.
  4. Agregat na TEST:
       A (równa waga)  = znak(Σ głos_i)
       B (waga IC)     = znak(Σ IC_train_i · głos_i)
     Trafność = odsetek barów, gdzie znak agregatu == etykieta (bary z niezerowym agregatem).
  5. Werdykt: B leczy gdy acc_B > acc_A ORAZ acc_B > 50% (na OOS, spójnie na parach).

Cząstki (per para) → arena_wyniki.db (rodzaj='hipoteza_b'), wznawialność + audyt.
Pasek postępu na stderr (Prawo XXIV). NIC nie buduje w ścieżce decyzyjnej — to POMIAR,
który dopiero uzasadni (lub obali) build opt-in + A/B na żywo (Prawo I, decyzja Cezara).

Użycie:
  python narzedzia/hipoteza_b.py                                  # 5 par 4h
  python narzedzia/hipoteza_b.py --glob "dane/4h/Binance_*_4h.csv" --interwal 4h
  python narzedzia/hipoteza_b.py --frac 0.6 --min-glosow 30
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

_KIER = {"LONG": 1, "SHORT": -1}


def _glos(kier: str) -> int:
    """Kierunek neuronu → głos ∈ {+1, -1, 0}."""
    return _KIER.get(kier, 0)


def _ic_kierunkowy_train(sygnaly, wyniki):
    """Per-neuron IC kierunkowy na TRAIN = średnia(głos · etykieta) po barach z głosem.

    Wagi liczy KANONICZNA imperium.legiony.legatus.oblicz_wagi_ic (jedno źródło prawdy,
    W-361 — ta sama logika wpina się w Legatusa). Tu dokładamy licznik głosów per-neuron
    (audyt/testy). Zwraca ({neuron: waga_ic}, {neuron: liczba_głosów}). Znak wagi niesie
    kierunek przewagi (ujemny → neuron myli się systematycznie, głos ODWRÓCONY w B)."""
    from imperium.legiony.legatus import oblicz_wagi_ic
    wagi = oblicz_wagi_ic(sygnaly, wyniki)
    liczba: dict = {}
    # Cubic P3: licznik głosów musi opisywać TE SAME próbki co wagi IC — iterujemy po
    # sparowanej historii (zip), nie po samym `sygnaly`, by audyt nie rozjechał się z wagami.
    for mapa, _ in zip(sygnaly, wyniki):
        for nid, kier in mapa.items():
            if _glos(kier) == 0:
                continue
            liczba[nid] = liczba.get(nid, 0) + 1
    return wagi, liczba


def _trafnosc_agregatu(sygnaly, wyniki, wagi=None):
    """Trafność agregatu na zadanym zbiorze. wagi=None → równa waga (A); w p.p. → B.

    Zwraca (trafnosc, liczba_barow_z_agregatem)."""
    trafne = 0
    aktywne = 0
    for mapa, etykieta in zip(sygnaly, wyniki):
        s = 0.0
        for nid, kier in mapa.items():
            g = _glos(kier)
            if g == 0:
                continue
            w = 1.0 if wagi is None else wagi.get(nid, 0.0)
            s += w * g
        if abs(s) < 1e-12:
            continue   # agregat neutralny — nie liczymy (nie było decyzji kierunkowej)
        aktywne += 1
        if (s > 0) == (etykieta > 0):
            trafne += 1
    if aktywne == 0:
        return float("nan"), 0
    return trafne / aktywne, aktywne


def analizuj_pare(bary, interwal, frac=0.6, okno=250, min_glosow=20, max_barow=None):
    """Zwraca dict z acc_A/acc_B na TEST (OOS) dla jednej pary lub None gdy za mało danych."""
    from imperium.koloseum.backtest import backtest

    if max_barow:
        bary = bary[-max_barow:]
    eng = backtest("x", interwal, bary=bary, okno=okno, zbieraj_sygnaly=True)
    sygnaly = getattr(eng, "historia_sygnalow", []) or []
    wyniki = getattr(eng, "historia_wynikow", []) or []
    n = len(sygnaly)
    if n < min_glosow * 2:
        return None

    podzial = int(n * frac)
    s_train, w_train = sygnaly[:podzial], wyniki[:podzial]
    s_test, w_test = sygnaly[podzial:], wyniki[podzial:]
    if len(s_test) < min_glosow:
        return None

    wagi_ic, _ = _ic_kierunkowy_train(s_train, w_train)
    acc_a, akt_a = _trafnosc_agregatu(s_test, w_test, wagi=None)
    acc_b, akt_b = _trafnosc_agregatu(s_test, w_test, wagi=wagi_ic)
    return {
        "bary_train": len(s_train), "bary_test": len(s_test),
        "acc_a": acc_a, "akt_a": akt_a,
        "acc_b": acc_b, "akt_b": akt_b,
        "neuronow_wazonych": len(wagi_ic),
    }


def raport(pliki, interwal, frac=0.6, okno=250, min_glosow=20, zapisz=True, max_barow=None) -> str:
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    per_para = []
    N = len(pliki)
    for i, plik in enumerate(pliki, 1):
        nazwa = Path(plik).name
        print(f"[{i}/{N}] {nazwa} — wczytuję + backtest…", file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
            wynik = analizuj_pare(bary, interwal, frac=frac, okno=okno,
                                  min_glosow=min_glosow, max_barow=max_barow)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ {nazwa}: {e}", file=sys.stderr, flush=True)
            continue
        if wynik is None:
            print(f"[{i}/{N}] {nazwa} — za mało danych, pomijam.", file=sys.stderr, flush=True)
            continue
        wynik["para"] = nazwa
        per_para.append(wynik)
        delta = wynik["acc_b"] - wynik["acc_a"]
        print(f"[{i}/{N}] {nazwa} — A={wynik['acc_a']:.1%} B={wynik['acc_b']:.1%} "
              f"(Δ={delta:+.1%}, test={wynik['bary_test']})", file=sys.stderr, flush=True)
        # Zapis CZĄSTKI natychmiast (ZASADA ANALIZY CZĄSTKOWEJ — wznawialność, nie na końcu)
        if zapisz:
            from imperium.biblioteki.arena_baza import zapisz_pomiar
            nota = (f"para={nazwa};frac={frac};test={wynik['bary_test']};"
                    f"accA={wynik['acc_a']:.4f};accB={wynik['acc_b']:.4f}")
            zapisz_pomiar("hipoteza_b", nazwa, wynik["acc_b"] - wynik["acc_a"], nota)
            print(f"    💾 arena: cząstka {nazwa} zapisana", file=sys.stderr, flush=True)

    if not per_para:
        return "🧪 HIPOTEZA B — brak wystarczających danych na żadnej parze."

    # Agregat po parach (waga = liczba barów TEST — pary z większym OOS ważą więcej)
    def _wazona(klucz_acc, klucz_akt):
        licz = sum(p[klucz_acc] * p[klucz_akt] for p in per_para if p[klucz_acc] == p[klucz_acc])
        mian = sum(p[klucz_akt] for p in per_para if p[klucz_acc] == p[klucz_acc])
        return (licz / mian) if mian else float("nan")

    glob_a = _wazona("acc_a", "akt_a")
    glob_b = _wazona("acc_b", "akt_b")
    lepsze = sum(1 for p in per_para if p["acc_b"] > p["acc_a"])

    linie = [
        f"🧪 HIPOTEZA B (ważenie głosów IC, Grinold-Kahn) — {len(per_para)} par, OOS test (frac={frac})",
        "   A = agregat RÓWNA waga | B = agregat WAŻONY IC_train (znak koryguje odwrócone)",
        "",
        f"   {'PARA':<26} {'A(równa)':>9} {'B(IC)':>9} {'Δ':>8} {'test':>6}",
    ]
    for p in sorted(per_para, key=lambda x: x["acc_b"] - x["acc_a"], reverse=True):
        d = p["acc_b"] - p["acc_a"]
        linie.append(f"   {p['para']:<26} {p['acc_a']:>8.1%} {p['acc_b']:>8.1%} "
                     f"{d:>+7.1%} {p['bary_test']:>6}")
    linie += [
        "",
        f"   ▸ GLOBALNIE (ważone barami OOS): A={glob_a:.1%}  B={glob_b:.1%}  Δ={glob_b - glob_a:+.1%}",
        f"   ▸ B > A na {lepsze}/{len(per_para)} parach",
        "",
    ]
    # Werdykt (Prawo I — z pomiaru, nie z wiary)
    if glob_b > glob_a and glob_b > 0.50:
        linie.append("   ✅ WERDYKT: B leczy agregację (B>A i B>50% OOS). Kandydat do buildu "
                     "opt-in OFF + A/B na żywo — decyzja Cezara (ZASADA WPIĘCIA).")
    elif glob_b > glob_a:
        linie.append("   ⚠️ WERDYKT: B > A, ale wciąż ≤50% OOS. Ważenie POMAGA, lecz rój nadal "
                     "nie bije losowości — sam re-weighting nie wystarcza.")
    else:
        linie.append("   ❌ WERDYKT: B nie bije A na OOS. Hipoteza B (samo ważenie IC) NIE leczy "
                     "wąskiego gardła — szukać dalej (breadth/dekorelacja/próg).")
    return "\n".join(linie)


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="Hipoteza B — ważenie głosów IC (Prawo XV/XVI, OOS)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv", help="wzorzec par CSV")
    p.add_argument("--interwal", default="4h")
    p.add_argument("--frac", type=float, default=0.6, help="udział TRAIN (reszta = OOS test)")
    p.add_argument("--okno", type=int, default=250)
    p.add_argument("--min-glosow", type=int, default=20)
    p.add_argument("--max-barow", type=int, default=None, help="ogranicz do ostatnich N barów/parę")
    p.add_argument("--bez-zapisu", action="store_true", help="nie zapisuj cząstek do areny")
    args = p.parse_args()

    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print("Brak plików pasujących do wzorca."); sys.exit(1)
    print(raport(pliki, args.interwal, frac=args.frac, okno=args.okno,
                 min_glosow=args.min_glosow, zapisz=not args.bez_zapisu, max_barow=args.max_barow))
