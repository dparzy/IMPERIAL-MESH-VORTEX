"""
🧩 WFO CHUNKED (Cursus Fenestrarum) — walk-forward CZĄSTKOWY i WZNAWIALNY.

Realizuje ZASADĘ ANALIZY CZĄSTKOWEJ (rozkaz Cezara): długa analiza = wiele MAŁYCH,
ZAPISANYCH, ŁĄCZONYCH kroków, nigdy jeden wielki blokujący bieg. Lekcja WFO: „wisiał
godzinami na ~76 oknach synchronicznie; padał = tracił wszystko". Tu każde OKNO to
najmniejsza jednostka: policz → ZAPISZ do checkpointu → następne. Bieg który padnie
NIE traci nic — wznawia od pierwszego niezapisanego okna (antykruchość, Taleb).

Zero zmiany wyników vs raport_wfo: ta sama matematyka (imperium/koloseum/walk_forward),
tylko checkpoint + wznawianie + pasek postępu (Prawo XXIV). Determinizm: optymalizuj
ma stały seed → okno policzone dwa razy = identyczny wynik (dlatego wznawianie bezpieczne).

Checkpoint: raporty/wfo_ckpt/<sygnatura>.jsonl (gitignore=widok). Sygnatura = hash configu
(plik, interwał, IS, OOS, okno, iteracje, lo, hi, seed, zakotwiczony) — inny config = inny
plik, zero mieszania nieporównywalnych biegów.

Uruchom (dane rynkowe LOKALNE, poza gitem):
    python narzedzia/wfo_chunked.py dane/4h/Binance_BTCUSDT_4h.csv 4h --is 500 --oos 150
    # po padzie/przerwaniu — ten sam bieg wznawia od niezapisanego okna:
    python narzedzia/wfo_chunked.py dane/4h/Binance_BTCUSDT_4h.csv 4h --is 500 --oos 150
    python narzedzia/wfo_chunked.py ... --reset   # licz od zera (skasuj checkpoint)
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CKPT_DIR = ROOT / "raporty" / "wfo_ckpt"


def _sygnatura(plik: str, interwal: str, rozmiar_is: int, rozmiar_oos: int, okno: int,
               n_iteracji: int, lo: float, hi: float, seed: Optional[int],
               zakotwiczony: bool) -> str:
    """Krótki hash configu — identyczny config = ten sam plik checkpointu (wznawialny)."""
    klucz = f"{Path(plik).name}|{interwal}|IS{rozmiar_is}|OOS{rozmiar_oos}|okno{okno}|" \
            f"it{n_iteracji}|lo{lo}|hi{hi}|seed{seed}|anch{int(zakotwiczony)}"
    return hashlib.sha256(klucz.encode("utf-8")).hexdigest()[:16]


def _wynik_do_dict(wynik, zwroty_oos: List[float]) -> dict:
    return {"idx": wynik.okno.idx,
            "wynik": dataclasses.asdict(wynik),
            "zwroty_oos": [float(z) for z in zwroty_oos]}


def _dict_do_wynik(d: dict) -> "Tuple[object, List[float]]":
    from imperium.koloseum.walk_forward import OknoWF, WynikOkna
    w = d["wynik"]
    okno = OknoWF(**w["okno"])
    wynik = WynikOkna(
        okno=okno, parametry=dict(w["parametry"]),
        sharpe_is=w["sharpe_is"], sharpe_oos=w["sharpe_oos"],
        wynik_is=w["wynik_is"], wynik_oos=w["wynik_oos"], efektywnosc=w["efektywnosc"])
    return wynik, [float(z) for z in d["zwroty_oos"]]


def wczytaj_checkpoint(sciezka: Path) -> "Dict[int, Tuple[object, List[float]]]":
    """Wczytuje policzone okna z JSONL. Pomija uszkodzone linie (antykruchość — Prawo I:
    lepiej przeliczyć jedno okno niż stracić cały bieg)."""
    wznow: Dict[int, Tuple[object, List[float]]] = {}
    if not sciezka.exists():
        return wznow
    for linia in sciezka.read_text(encoding="utf-8").splitlines():
        linia = linia.strip()
        if not linia:
            continue
        try:
            d = json.loads(linia)
            wynik, zwroty = _dict_do_wynik(d)
            wznow[int(d["idx"])] = (wynik, zwroty)   # ostatni wpis danego idx wygrywa
        except Exception:  # noqa: BLE001
            continue
    return wznow


def uruchom(plik: str, interwal: str, rozmiar_is: int, rozmiar_oos: int, okno: int,
            n_iteracji: int, lo: float, hi: float, seed: Optional[int] = 42,
            zakotwiczony: bool = False, reset: bool = False, podglad: bool = True):
    """Chunkowany, wznawialny WFO. Zwraca RaportWalkForward."""
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    from imperium.koloseum.optymalizator import PrzestrzeńParam
    from imperium.koloseum.walk_forward import walk_forward, generuj_okna
    from narzedzia.raport_wfo import ewaluator_backtest

    bary = wczytaj_csv(plik, interwal)
    # Fail-fast: backtest() wymaga wycinka DŁUŻSZEGO niż okno (backtest.py: len<=okno → ValueError).
    # Sprawdzamy ZANIM policzymy jakiekolwiek okno — inaczej pad w środku biegu marnuje pracę.
    if rozmiar_oos <= okno or rozmiar_is <= okno:
        raise ValueError(
            f"IS={rozmiar_is} i OOS={rozmiar_oos} muszą być > okno={okno} "
            f"(backtest liczy wskaźniki na wycinku dłuższym niż okno). Zwiększ --is/--oos lub zmniejsz --okno.")
    okna = generuj_okna(len(bary), rozmiar_is, rozmiar_oos, zakotwiczony=zakotwiczony)
    n = len(okna)

    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    sig = _sygnatura(plik, interwal, rozmiar_is, rozmiar_oos, okno, n_iteracji, lo, hi,
                     seed, zakotwiczony)
    ckpt = CKPT_DIR / f"{sig}.jsonl"
    if reset and ckpt.exists():
        ckpt.unlink()

    wznow = wczytaj_checkpoint(ckpt)
    juz = len([o for o in okna if o.idx in wznow])
    print(f"🧩 WFO CHUNKED — {Path(plik).name} ({len(bary)} barów) | IS={rozmiar_is} "
          f"OOS={rozmiar_oos} okno={okno} it={n_iteracji} | okien={n}", flush=True)
    print(f"   checkpoint: {ckpt.name} | wznowione: {juz}/{n} "
          f"{'(wszystko policzone — tylko agregacja)' if juz >= n and n else ''}", flush=True)

    # Dopisywacz cząstek: KAŻDE świeże okno ZANIM następne (antykruchość)
    f = ckpt.open("a", encoding="utf-8")

    def checkpoint_cb(wynik, zwroty_oos):
        f.write(json.dumps(_wynik_do_dict(wynik, zwroty_oos), ensure_ascii=False) + "\n")
        f.flush()

    def postep_cb(i: int, total: int, wynik):
        proc = 100.0 * i / max(1, total)
        znak = "✓" if wynik.okno.idx in wznow else "•"
        print(f"   [{i:>3}/{total}] {znak} okno idx={wynik.okno.idx:>3} "
              f"WFE={wynik.efektywnosc:+.3f} Sh_OOS={wynik.sharpe_oos:+.3f} | {proc:5.1f}%",
              file=sys.stderr, flush=True)

    try:
        rap = walk_forward(
            list(bary), ewaluator_backtest(interwal, okno=okno),
            przestrzenie=[PrzestrzeńParam("min_pewnosc", lo, hi)],
            rozmiar_is=rozmiar_is, rozmiar_oos=rozmiar_oos, n_iteracji=n_iteracji,
            zakotwiczony=zakotwiczony, seed=seed,
            checkpoint_cb=checkpoint_cb, postep_cb=postep_cb, wznow=wznow)
    finally:
        f.close()

    cv = rap.stabilnosc_parametrow.get("min_pewnosc", 0.0)
    print("=" * 66, flush=True)
    print(f" WERDYKT: {rap.werdykt}  ({rap.powod})", flush=True)
    print(f" okien: {rap.n_okien} | WFE śr: {rap.wfe_srednia:+.3f} | "
          f"OOS Sharpe: {rap.oos_sharpe_zagregowany:+.3f} | CV(min_pewnosc): {cv:.2f}", flush=True)
    print("=" * 66, flush=True)

    if podglad and rap.n_okien:
        p = _podglad_kapitol(plik, interwal, rozmiar_is, rozmiar_oos, okno, n_iteracji,
                             lo, hi, seed, zakotwiczony, rap)
        print(f"🏛️ Podgląd Kapitolu: {p}", flush=True)
        print(f"   Link: {p.as_uri()}", flush=True)
    return rap


def _podglad_kapitol(plik, interwal, rozmiar_is, rozmiar_oos, okno, n_iteracji, lo, hi,
                     seed, zakotwiczony, rap) -> Path:
    from narzedzia.kapitol_podglad import zapisz
    prog = 0.5
    spec = [
        ("Co testowane", "Walk-Forward Optimization (WFO, Pardo) — przeuczenie parametrów"),
        ("Plik / para", Path(plik).name),
        ("Interwał czasowy", interwal),
        ("IS / OOS (barów)", f"{rozmiar_is} / {rozmiar_oos}"),
        ("Okno backtestu / iteracje", f"{okno} / {n_iteracji} prób hyperopt per okno IS"),
        ("Zakres min_pewnosc", f"{lo}–{hi} · seed={seed} · {'zakotwiczony' if zakotwiczony else 'kroczący'}"),
        ("Okien WF", str(rap.n_okien)),
        ("WERDYKT", f"{rap.werdykt} — {rap.powod}"),
        ("WFE śr / OOS Sharpe", f"{rap.wfe_srednia:+.3f} / {rap.oos_sharpe_zagregowany:+.3f}"),
    ]
    slupki_wfe = [(f"okno {w.okno.idx}", round(w.efektywnosc, 3),
                   "#8fe388" if w.efektywnosc >= prog else "#e0794b") for w in rap.okna]
    slupki_sh = [(f"okno {w.okno.idx}", round(w.sharpe_oos, 4),
                  "#8fe388" if w.sharpe_oos > 0 else "#e0794b") for w in rap.okna]
    wykresy = [
        {"tytul": f"WFE per okno (zielony ≥ {prog} = ROBUST, Pardo)", "jednostka": "WFE",
         "opis": "WFE = Sharpe_OOS / Sharpe_IS. ≥0.5 → parametry generalizują poza próbą.",
         "slupki": slupki_wfe},
        {"tytul": "Sharpe OOS per okno (egzamin na nieznanym)", "jednostka": "Sharpe",
         "opis": "Zielony = dodatni Sharpe poza próbą; pomarańczowy = brak przewagi OOS.",
         "slupki": slupki_sh},
    ]
    werdykt = (f"WERDYKT: {rap.werdykt} — {rap.powod}\n"
               f"WFE śr {rap.wfe_srednia:+.3f} · OOS Sharpe {rap.oos_sharpe_zagregowany:+.3f} "
               f"· {rap.n_okien} okien. Liczone cząstkowo z checkpointu (wznawialne).")
    return zapisz(f"KAPITOL_PODGLAD_wfo_{Path(plik).stem}_{interwal}",
                  f"Podgląd testu — WFO {Path(plik).name} {interwal}",
                  spec, wykresy, werdykt, otworz=False)


def main(argv=None):
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="WFO chunkowany i wznawialny (ZASADA ANALIZY CZĄSTKOWEJ)")
    p.add_argument("plik")
    p.add_argument("interwal")
    p.add_argument("--is", dest="rozmiar_is", type=int, default=500)
    p.add_argument("--oos", type=int, default=150)
    p.add_argument("--okno", type=int, default=60)
    p.add_argument("--iteracje", type=int, default=30)
    p.add_argument("--lo", type=float, default=0.45)
    p.add_argument("--hi", type=float, default=0.75)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--zakotwiczony", action="store_true")
    p.add_argument("--reset", action="store_true", help="skasuj checkpoint i licz od zera")
    p.add_argument("--bez-podgladu", dest="podglad", action="store_false")
    args = p.parse_args(argv)
    try:
        uruchom(args.plik, args.interwal, args.rozmiar_is, args.oos, args.okno,
                args.iteracje, args.lo, args.hi, seed=args.seed,
                zakotwiczony=args.zakotwiczony, reset=args.reset, podglad=args.podglad)
    except FileNotFoundError as e:
        print(f"❌ Nie wczytano {args.plik}: {e}")
        return 1
    except ValueError as e:
        print(f"❌ {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
