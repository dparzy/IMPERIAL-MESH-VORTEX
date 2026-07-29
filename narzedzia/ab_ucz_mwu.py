"""
🎓 DISCIPULUS — A/B ZAMKNIĘTEJ PĘTLI UCZENIA (`ucz_mwu`, W-049/W-280/W-285.1).

Pytanie: czy rój, który po KAŻDEJ zamkniętej pozycji rozlicza neurony, które
głosowały za wejściem (HedgeMWU z pamięcią reżimu → mnożniki wag wracają do
Legatusa NA BIEŻĄCO), zarabia więcej niż rój ze stałymi wagami?

  OFF = backtest(...)                — wagi stałe (baseline)
  ON  = backtest(..., ucz_mwu=True)  — pętla uczenia domknięta

Uczenie jest ONLINE i wyłącznie z JUŻ zamkniętych trade'ów → zero look-ahead,
więc porównanie idzie na tych samych barach, bez podziału TRAIN/TEST.

DLACZEGO OSOBNE NARZĘDZIE: `ab_strategy_mwu.py` mierzy INNY mechanizm —
`ucz_mwu_strategii` (W-362, ważenie 20 STRATEGII). Tu chodzi o wagi NEURONÓW.
Sonda z 2026-07-29 (BTC 4H, 1000 barów) dała +114.52 USDT na korzyść ON —
jedna para i jedno okno to NIE wyrok, stąd ten harness.

BRAMKA PRZECIW PRZYPADKOWI (Prawo XVI — pomiar, nie opinia):
  • test znaku (dwumianowy dokładny) na parach — czy przewaga bije rzut monetą,
  • DSR (walidacja.deflated_sharpe) z UCZCIWYM n_prob = liczbą wariantów,
  • PBO/CSCV (walidacja.pbo_cscv) na macierzy T×2 — czy zwycięzca IS trzyma OOS.
Portfel to RÓWNOWAŻONY koszyk par: zwrot_t = średnia zwrotów par na barze t
(krzywe equity mają tę samą długość, więc bary się zgadzają). Sumowanie procentów
po parach dałoby liczbę rosnącą z liczbą par — bez sensu jako P&L (lekcja Cubic P2).

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ, Prawo XXIV): każda para liczona osobno,
wynik + serie zwrotów lądują w cache `raporty/ab_ucz_mwu_cache.json` PRZED następną
parą; restart pomija policzone (`--force` przelicza). Pasek postępu na stderr.
Cache jest JEDYNYM źródłem wznawiania (arena dostaje kopię skalarną do rejestru —
dwa źródła prawdy przy wznawianiu rozjechałyby się po zmianie schematu).

Użycie:
  python narzedzia/ab_ucz_mwu.py --interwal 4h --okna-testu 600,1000
  python narzedzia/ab_ucz_mwu.py --glob "dane/godzinowe/Binance_*_1h.csv" --interwal 1H
  python narzedzia/ab_ucz_mwu.py --okna-testu 1000 --ledger
"""

from __future__ import annotations

import argparse
import glob as _glob
import json
import logging
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CACHE = ROOT / "raporty" / "ab_ucz_mwu_cache.json"

# Para z garstką trade'ów niesie szum, nie werdykt. Próg liczony PER RAMIĘ, nie z sumy:
# `tr_off + tr_on >= 10` przepuszczałoby parę 5/5, a `walidacja.MIN_TRADES` mówi wprost
# „mniej niż 10 = anegdota, nie statystyka" — o KAŻDEJ mierzonej serii z osobna (recenzja
# 2026-07-29). Suma dwóch anegdot nie staje się statystyką.
_MIN_TRADES = 10
# Minimum par z niezerową różnicą, żeby test znaku w ogóle coś znaczył.
_MIN_PAR_KONKLUZYWNYCH = 5


# ─── 1. POMIAR JEDNEJ PARY ────────────────────────────────────────────────────

def _zwroty_z_equity(krzywa) -> list:
    """Krzywa equity (kapitał po każdym barze) → zwroty prostych barów.

    Bar bez otwartej pozycji daje 0.0 i tak ma zostać: to uczciwa część rozkładu
    (strategia siedząca w gotówce nie zarabia), a wycięcie zer zawyżyłoby Sharpe.
    """
    out = []
    for i in range(1, len(krzywa)):
        poprz = krzywa[i - 1]
        out.append((krzywa[i] / poprz - 1.0) if poprz else 0.0)
    return out


def _metryki(eng) -> dict:
    s = eng.podsumowanie()
    ret = (s.kapital_koncowy / s.kapital_startowy - 1.0) if s.kapital_startowy else 0.0
    return {"ret": ret, "trades": s.total_trades, "wr": s.win_rate,
            "pnl_usdt": s.total_pnl_usdt,
            "zwroty": _zwroty_z_equity(getattr(eng, "krzywa_equity", []) or [])}


def analizuj_pare(bary, interwal, okno=250, min_barow=400, max_barow=None,
                  tryb="agregat") -> "dict | None":
    """OFF vs ON na tych samych barach. None = za mało danych na wiarygodny bieg."""
    from imperium.koloseum.backtest import backtest
    if max_barow:
        bary = bary[-max_barow:]
    if len(bary) < min_barow:
        return None
    off = _metryki(backtest("x", interwal, bary=bary, okno=okno, tryb=tryb))
    on = _metryki(backtest("x", interwal, bary=bary, okno=okno, tryb=tryb, ucz_mwu=True))
    return {
        "bary": len(bary),
        "ret_off": off["ret"], "ret_on": on["ret"],
        "tr_off": off["trades"], "tr_on": on["trades"],
        "wr_off": off["wr"], "wr_on": on["wr"],
        "pnl_off": off["pnl_usdt"], "pnl_on": on["pnl_usdt"],
        "zwroty_off": [round(x, 10) for x in off["zwroty"]],
        "zwroty_on": [round(x, 10) for x in on["zwroty"]],
    }


# ─── 2. CACHE (wznawianie) ────────────────────────────────────────────────────

def klucz_biegu(nazwa, interwal, tryb, okno, min_barow, max_barow) -> str:
    """Klucz = para + PEŁNY podpis konfiguracji.

    Bez podpisu zmiana okna/capu/trybu raportowałaby STARY wynik pod nową etykietą
    (ta sama wada, którą Cubic złapał w ab_strategy_mwu) — resume ma pomijać wyłącznie
    RÓWNOWAŻNE eksperymenty, nie „podobne".
    """
    return (f"{nazwa}#i={interwal};tryb={tryb};okno={okno};"
            f"min={min_barow};max={max_barow or 0}")


def wczytaj_cache(sciezka: Path = CACHE) -> dict:
    if not sciezka.exists():
        return {}
    try:
        with open(sciezka, encoding="utf-8") as f:
            dane = json.load(f)
        return dane if isinstance(dane, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}   # uszkodzony cache = brak cache, nie wywrotka biegu


def zapisz_cache(cache: dict, sciezka: Path = CACHE) -> None:
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    tmp = sciezka.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    tmp.replace(sciezka)


# ─── 3. STATYSTYKA ────────────────────────────────────────────────────────────

def p_dwumianowy(k: int, n: int) -> float:
    """Dokładny dwustronny test dwumianowy przeciw p=0.5 (test znaku).

    k = ile par wygrał wariant ON, n = par z niezerową różnicą. Sumujemy wyniki
    NIE BARDZIEJ prawdopodobne niż zaobserwowany (klasyczna definicja dwustronna).
    n=0 → 1.0: brak różnic to brak dowodu, nie dowód braku.
    """
    if n <= 0:
        return 1.0
    if not 0 <= k <= n:
        raise ValueError(f"k={k} poza zakresem 0..{n}")
    obs = math.comb(n, k)
    return min(1.0, sum(math.comb(n, i) for i in range(n + 1)
                        if math.comb(n, i) <= obs) / 2 ** n)


def portfel_zwrotow(wyniki: list) -> "tuple[list, list, int]":
    """Równoważony koszyk: zwrot_t = średnia zwrotów par na barze t.

    Serie par przycinamy do NAJKRÓTSZEJ **od końca** (najświeższe bary) — pary
    o różnej historii inaczej rozjechałyby się w czasie, a średnia mieszałaby
    bar z 2024 z barem z 2026. Zwraca (portfel_off, portfel_on, dlugosc).
    """
    serie = [(w["zwroty_off"], w["zwroty_on"]) for w in wyniki
             if w.get("zwroty_off") and w.get("zwroty_on")]
    if not serie:
        return [], [], 0
    dl = min(min(len(a), len(b)) for a, b in serie)
    if dl <= 0:
        return [], [], 0
    off = [sum(a[-dl:][t] for a, _ in serie) / len(serie) for t in range(dl)]
    on = [sum(b[-dl:][t] for _, b in serie) / len(serie) for t in range(dl)]
    return off, on, dl


def statystyki_zbiorcze(wyniki: list, n_prob: int, s_blokow: int = 10) -> dict:
    """Δ portfela + test znaku + DSR(ON/OFF) + PBO. Wejście: pary konkluzywne.

    Pusta lista to BŁĄD WOŁAJĄCEGO, nie wynik — głośny ValueError zamiast
    ZeroDivisionError z wnętrza średniej (recenzja 2026-07-29).
    """
    from imperium.koloseum.walidacja import deflated_sharpe, pbo_cscv
    if not wyniki:
        raise ValueError("brak par do policzenia statystyk — nie ma czego uśredniać")
    n = len(wyniki)
    sr_off = sum(w["ret_off"] for w in wyniki) / n
    sr_on = sum(w["ret_on"] for w in wyniki) / n
    lepsze = sum(1 for w in wyniki if w["ret_on"] > w["ret_off"])
    rozne = sum(1 for w in wyniki if w["ret_on"] != w["ret_off"])
    p_znak = p_dwumianowy(lepsze, rozne)

    p_off, p_on, dl = portfel_zwrotow(wyniki)
    dsr_on = deflated_sharpe(p_on, n_prob=n_prob) if dl else {
        "dsr": 0.0, "ok": False, "sharpe": None, "sr0": None, "powod": "brak serii"}
    dsr_off = deflated_sharpe(p_off, n_prob=n_prob) if dl else dict(dsr_on)
    if dl:
        macierz = [[p_off[t], p_on[t]] for t in range(dl)]
        pbo = pbo_cscv(macierz, s_blokow=s_blokow)
    else:
        pbo = {"pbo": None, "ok": False, "n_podzialow": 0, "powod": "brak serii"}
    return {
        "par": n, "sr_off": sr_off, "sr_on": sr_on, "delta": sr_on - sr_off,
        "lepsze": lepsze, "rozne": rozne, "p_znak": p_znak,
        "barow_portfela": dl, "dsr_on": dsr_on, "dsr_off": dsr_off, "pbo": pbo,
        "n_prob": n_prob,
    }


def werdykt(st: dict) -> "tuple[str, str]":
    """(token, zdanie). Token krótki — trafia do ledgera; zdanie dla Cezara.

    Kolejność bramek: najpierw „czy próba w ogóle uprawnia do sądu", potem „czy jest
    różnica", potem „czy dodatnia", na końcu „czy przetrwa korektę o liczbę prób i
    podział IS/OOS". WIELKOŚĆ PRÓBY IDZIE PIERWSZA (recenzja 2026-07-29): alarm
    „mechanizm martwy" wypowiedziany z jednej pary byłby tym samym grzechem, co
    werdykt POMAGA z jednej pary.
    """
    if not st.get("baza_pelna", True):
        return ("NIEKONKLUZYWNE",
                f"⚠️ NIEKONKLUZYWNE: ŻADNA para nie ma ≥{_MIN_TRADES} trade'ów na ramię — "
                f"liczby niżej policzono na wszystkich parach, ale to anegdota, nie wyrok.")
    if st["par"] < _MIN_PAR_KONKLUZYWNYCH:
        ogon = (" W tej próbce mechanizm nie zmienił ani jednej decyzji — za mało par, "
                "by orzec, czy jest martwy." if st["rozne"] == 0 else "")
        return ("NIEKONKLUZYWNE", f"⚠️ NIEKONKLUZYWNE: tylko {st['par']} par konkluzywnych "
                                  f"(< {_MIN_PAR_KONKLUZYWNYCH}) — za wąska podstawa na wyrok."
                                  + ogon)
    if st["rozne"] == 0:
        return ("BEZ_WPLYWU", "🚨 BEZ WPŁYWU: ON == OFF na każdej parze — pętla uczenia "
                              "nie zmienia ANI JEDNEJ decyzji. To utrata potencjału "
                              "(Prawo XV), nie remis: sprawdź, czy mnożniki docierają "
                              "do Legatusa.")
    if st["delta"] <= 0:
        return ("SZKODZI", "❌ SZKODZI: pętla uczenia obniża zwrot portfela. Flaga zostaje "
                           "OFF (ZASADA WPIĘCIA — nic nie wchodzi w ścieżkę decyzyjną "
                           "bez zielonego A/B).")
    mocny = (st["p_znak"] < 0.05 and st["dsr_on"].get("ok") and st["pbo"].get("ok"))
    if mocny:
        return ("POMAGA", "✅ POMAGA: przewaga dodatnia, bije rzut monetą (p<0.05), przeżywa "
                          "korektę o liczbę prób (DSR) i podział IS/OOS (PBO). Kandydat do "
                          "wpięcia jako flaga — decyzja Cezara.")
    braki = []
    if st["p_znak"] >= 0.05:
        braki.append(f"test znaku p={st['p_znak']:.3f} ≥ 0.05")
    if not st["dsr_on"].get("ok"):
        braki.append(f"DSR={st['dsr_on'].get('dsr')} < 0.95")
    if not st["pbo"].get("ok"):
        braki.append(f"PBO={st['pbo'].get('pbo')} ≥ 0.20")
    return ("SLABE", "⚠️ PRZEWAGA DODATNIA, ALE NIEPOTWIERDZONA: " + "; ".join(braki) +
                     ". Za mało na wpięcie — dodatni znak bez bramki to nadal loteria.")


# ─── 4. RAPORT ────────────────────────────────────────────────────────────────

def _nota(nazwa, w) -> str:
    return (f"para={nazwa};bary={w['bary']};retOFF={w['ret_off']:.4f};retON={w['ret_on']:.4f};"
            f"trOFF={w['tr_off']};trON={w['tr_on']};wrOFF={w['wr_off']:.4f};"
            f"wrON={w['wr_on']:.4f}")


def zbierz_okno(pliki, interwal, okno, min_barow, max_barow, tryb="agregat",
                force=False, zapisz=True, cache=None) -> list:
    """Liczy (lub czyta z cache) wszystkie pary dla JEDNEGO okna testowego."""
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    cache = wczytaj_cache() if cache is None else cache
    wyniki = []
    n = len(pliki)
    for i, plik in enumerate(pliki, 1):
        nazwa = Path(plik).name
        klucz = klucz_biegu(nazwa, interwal, tryb, okno, min_barow, max_barow)
        etykieta = f"[{i}/{n}] okno={max_barow or 'całość'} {nazwa}"
        if not force and klucz in cache:
            w = dict(cache[klucz])
            w["z_cache"] = True
            wyniki.append(w)
            print(f"{etykieta} — z cache: OFF={w['ret_off']:+.1%} ON={w['ret_on']:+.1%} "
                  f"(Δ={w['ret_on'] - w['ret_off']:+.1%})", file=sys.stderr, flush=True)
            continue
        print(f"{etykieta} — backtest OFF vs ON(ucz_mwu)…", file=sys.stderr, flush=True)
        try:
            bary = wczytaj_csv(plik, interwal)
            w = analizuj_pare(bary, interwal, okno=okno, min_barow=min_barow,
                              max_barow=max_barow, tryb=tryb)
        except Exception as e:  # noqa: BLE001
            print(f"{etykieta} — ⚠️ {e}", file=sys.stderr, flush=True)
            continue
        if w is None:
            print(f"{etykieta} — za mało danych.", file=sys.stderr, flush=True)
            continue
        w["para"] = nazwa
        wyniki.append(w)
        print(f"{etykieta} — OFF={w['ret_off']:+.1%} ON={w['ret_on']:+.1%} "
              f"(Δ={w['ret_on'] - w['ret_off']:+.1%}, tr {w['tr_off']}/{w['tr_on']})",
              file=sys.stderr, flush=True)
        if zapisz:
            cache[klucz] = w
            zapisz_cache(cache)
            from imperium.biblioteki.arena_baza import zapisz_pomiar
            zapisz_pomiar(f"ab_ucz_mwu_{tryb}", klucz, w["ret_on"] - w["ret_off"],
                          _nota(nazwa, w))
            print("    💾 cache + arena zapisane", file=sys.stderr, flush=True)
    return wyniki


def raport(pliki, interwal, okna_testu, okno=250, min_barow=400, tryb="agregat",
           force=False, zapisz=True, n_prob=None, s_blokow=10) -> "tuple[str, dict]":
    """Pełny raport A/B po wszystkich oknach. Zwraca (tekst, {okno: statystyki})."""
    cache = wczytaj_cache()
    # n_prob UCZCIWIE: dwa ramiona × każde testowane okno. Zaniżenie n_prob obniża
    # poprzeczkę DSR — czyli oszukuje własną bramkę (Prawo I).
    n_prob = n_prob or max(2, 2 * len(okna_testu))
    linie = [
        f"🎓 DISCIPULUS — A/B pętli uczenia (ucz_mwu) · interwał={interwal} · tryb={tryb}",
        "   OFF = wagi stałe | ON = MWU rozlicza neurony po każdej zamkniętej pozycji",
        f"   n_prob (uczciwa liczba wariantów dla DSR) = {n_prob}",
    ]
    statystyki = {}
    for max_barow in okna_testu:
        wyniki = zbierz_okno(pliki, interwal, okno, min_barow, max_barow, tryb=tryb,
                             force=force, zapisz=zapisz, cache=cache)
        linie += ["", f"── OKNO {max_barow} barów ─────────────────────────────",
                  f"   {'PARA':<26} {'BARY':>6} {'OFF':>8} {'ON':>8} {'Δ':>8} {'tr o/n':>9}"]
        if not wyniki:
            linie.append("   (brak danych)")
            continue
        for w in sorted(wyniki, key=lambda x: x["ret_on"] - x["ret_off"], reverse=True):
            # BARY drukowane jawnie: para krótsza od okna wchodziła do tabeli pod etykietą
            # pełnego okna i mieszała horyzonty bez śladu (recenzja 2026-07-29).
            skrot = "*" if w["bary"] < (max_barow or w["bary"]) else " "
            linie.append(f"   {w['para']:<26} {w['bary']:>5}{skrot} "
                         f"{w['ret_off']:>+7.1%} {w['ret_on']:>+7.1%} "
                         f"{w['ret_on'] - w['ret_off']:>+7.1%} {w['tr_off']:>4}/{w['tr_on']:<4}")
        if any(w["bary"] < (max_barow or w["bary"]) for w in wyniki):
            linie.append("   * para krótsza niż okno — mierzona na tym, co ma")
        # Próg PER RAMIĘ: suma dwóch anegdot nie jest statystyką (recenzja 2026-07-29).
        konkluz = [w for w in wyniki if min(w["tr_off"], w["tr_on"]) >= _MIN_TRADES]
        baza = konkluz or wyniki
        st = statystyki_zbiorcze(baza, n_prob=n_prob, s_blokow=s_blokow)
        st["baza_pelna"] = bool(konkluz)
        tok, zdanie = werdykt(st)
        st["werdykt"] = tok
        statystyki[max_barow] = st
        opis_bazy = (f"{st['par']} par ≥{_MIN_TRADES} trade na ramię" if konkluz
                     else f"WSZYSTKIE {st['par']} par — żadna nie ma ≥{_MIN_TRADES} na ramię")
        linie += [
            "",
            f"   ▸ PORTFEL (średni zwrot/parę, {opis_bazy}): "
            f"OFF={st['sr_off']:+.1%}  ON={st['sr_on']:+.1%}  Δ={st['delta']:+.1%}",
            f"   ▸ ON > OFF na {st['lepsze']}/{st['rozne']} par z różnicą "
            f"→ test znaku p={st['p_znak']:.4f}",
            f"   ▸ DSR ON={st['dsr_on'].get('dsr')} (Sharpe={st['dsr_on'].get('sharpe')}, "
            f"SR₀={st['dsr_on'].get('sr0')}) | DSR OFF={st['dsr_off'].get('dsr')}",
            f"   ▸ PBO={st['pbo'].get('pbo')} na {st['pbo'].get('n_podzialow')} podziałach "
            f"(macierz {st['barow_portfela']}×2)",
            f"   {zdanie}",
        ]
    return "\n".join(linie), statystyki


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(
        description="DISCIPULUS — A/B zamkniętej pętli uczenia (ucz_mwu, W-049/W-280)")
    p.add_argument("--glob", default="dane/4h/Binance_*_4h.csv")
    # ETYKIETA KANONICZNA ('4H', nie '4h'): bary noszą ją przez cały pipeline, a słowniki
    # Imperium są po niej kluczowane. Pomiar 2026-07-29: '4h' dawał inny wynik backtestu,
    # bo trafiał w fallbacki. Normalizator w kodzie już to łata, ale mierzymy tak, jak
    # gra produkcja (petla_live używa '4H').
    p.add_argument("--interwal", default="4H")
    p.add_argument("--tryb", default="agregat", choices=["agregat", "filtr", "strategia"])
    p.add_argument("--okno", type=int, default=250, help="ile barów wstecz widzi rój")
    p.add_argument("--okna-testu", default="1000",
                   help="długości okien testowych po przecinku, np. 600,1000")
    p.add_argument("--min-barow", type=int, default=400)
    p.add_argument("--s-blokow", type=int, default=10, help="liczba bloków CSCV (parzysta)")
    p.add_argument("--n-prob", type=int, default=None,
                   help="ile wariantów przetestowano ŁĄCZNIE (DSR); domyślnie 2×liczba okien")
    p.add_argument("--bez-zapisu", action="store_true")
    p.add_argument("--force", action="store_true")
    p.add_argument("--ledger", action="store_true", help="dopisz POMIAR do CODEX PROBATIONUM")
    p.add_argument("--uwaga", default="", help="dopisek do noty w ledgerze (np. powód korekty)")
    args = p.parse_args()

    pliki = sorted(_glob.glob(str(ROOT / args.glob)))
    if not pliki:
        print(f"Brak plików dla wzorca: {args.glob}")
        sys.exit(1)
    okna = [int(x) for x in args.okna_testu.split(",") if x.strip()]
    tekst, staty = raport(pliki, args.interwal, okna, okno=args.okno,
                          min_barow=args.min_barow, tryb=args.tryb, force=args.force,
                          zapisz=not args.bez_zapisu, n_prob=args.n_prob,
                          s_blokow=args.s_blokow)
    print(tekst)

    if args.ledger and staty:
        from narzedzia.scriba_codex import zapisz_pomiar as ledger_pomiar
        for maxb, st in staty.items():
            ledger_pomiar(
                temat="A/B zamkniętej pętli uczenia (ucz_mwu) — DISCIPULUS",
                pytanie="Czy MWU rozliczające neurony po każdej zamkniętej pozycji "
                        "poprawia zwrot portfela?",
                warianty={"ret_OFF_%": round(st["sr_off"] * 100, 2),
                          "ret_ON_%": round(st["sr_on"] * 100, 2),
                          "delta_pp": round(st["delta"] * 100, 2),
                          "par_ON_lepsze": st["lepsze"], "par_z_roznica": st["rozne"],
                          "p_znak": round(st["p_znak"], 4),
                          "DSR_ON": st["dsr_on"].get("dsr"),
                          "PBO": st["pbo"].get("pbo")},
                metryka="zwrot % / p / DSR / PBO", werdykt=st["werdykt"],
                zrodlo="narzedzia/ab_ucz_mwu.py", okno_barow=maxb, interwal=args.interwal,
                uwaga=f"{len(pliki)} par wejściowych, podstawa werdyktu {st['par']} par"
                      f"{'' if st.get('baza_pelna', True) else ' (ŻADNA bez progu — anegdota)'}, "
                      f"tryb={args.tryb}, okno roju={args.okno}, n_prob={st['n_prob']}, "
                      f"portfel równoważony {st['barow_portfela']} barów"
                      + (f". {args.uwaga}" if args.uwaga else ""))
        print("\n📜 CODEX PROBATIONUM: pomiary dopisane.")
