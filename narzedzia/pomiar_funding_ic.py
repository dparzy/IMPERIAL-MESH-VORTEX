"""
🧪 PROBATIO FUNDING (Prawo I + XXIV) — walidacja TIER A: czy FUNDING_RATE ma IC?

Rzymskie *probatio* = próba/egzamin rekruta przed przyjęciem do legionu. Tu: kandydat
TIER A (funding, z PLON_HYGINUSA 2026-07-14) przechodzi próbę POMIARU, zanim wejdzie
w ścieżkę decyzyjną (ZASADA WPIĘCIA — pomiar najpierw, nie wiara).

Mierzy Information Coefficient funding-rate: IC = Spearman(funding_t, zwrot_{t→t+h}).
Funding historyczny (8h, Binance public via AdapterFutures.pobierz_historie) → forward-fill
KAUZALNY na oś barów (ts ≤ bar, zero look-ahead) → korelacja rang ze zwrotem forward.

Hipoteza z literatury (Sinclair/Kaufman, PLON_HYGINUSA): wysoki funding = stłoczone longi
płacą → kontrariański → IC UJEMNY (funding↑ → cena↓). Mierzymy znak i siłę, nie zakładamy.

Dwa tryby próbkowania (kontrola persystencji, Prawo I):
  • NIENAKŁADAJĄCE (odstęp = h): uczciwe n, bez inflacji autokorelacją zwrotów.
  • NAKŁADAJĄCE (co bar): więcej próbek, ale IC zawyżone przez nakładanie — do porównania.

Uruchom:  python narzedzia/pomiar_funding_ic.py
Opcje:    --symbole BTCUSDT ETHUSDT ...  --interwal 1H  --horyzonty 6 12 24  --arena
"""
import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DOMYSLNE_SYMBOLE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT"]
MIN_PAR = 30           # minimum próbek na policzalny IC (jak metryki_ic/pomiar_nowe_moduly)
PROG_SKILL = 0.03      # |IC| > 0.03 = realny skill (konwencja Imperium, W-369)


def _pasek(i, n, opis):
    print(f"\r[{i}/{n}] {opis:<40}", end="", file=sys.stderr, flush=True)
    if i == n:
        print("", file=sys.stderr, flush=True)


def _zwroty_fwd(closes, h):
    return [(closes[i + h] / closes[i] - 1.0) if i + h < len(closes) else None
            for i in range(len(closes))]


def _ic(fund, zwr, krok, mnoznik=1.0):
    """IC = Spearman(funding, zwrot) na siatce co `krok` barów. Zwraca (ic, n) lub (None, n)."""
    import numpy as np
    from imperium.legiony.metryki_ic import _spearman
    pary = [(fund[i], zwr[i]) for i in range(0, len(fund), krok)
            if fund[i] is not None and zwr[i] is not None]
    if len(pary) < MIN_PAR:
        return None, len(pary)
    x = np.array([p[0] for p in pary], dtype=float)
    y = np.array([p[1] for p in pary], dtype=float)
    if np.std(x) < 1e-12:
        return None, len(pary)
    return _spearman(x, y), len(pary)


def _pomiar_symbolu(sym, interwal, limit, horyzonty, loader, adf):
    from imperium.akwedukty.sentyment_historyczny import forward_fill_na_bary
    from imperium.koloseum.petla_live import _df_do_barow
    df = loader.fetch(sym, interwal, limit=limit)
    bary = _df_do_barow(df, sym, interwal)
    hist = adf.pobierz_historie(sym, limit=1000)
    mapa = forward_fill_na_bary(bary, hist)
    fund = [mapa.get(b["timestamp"], {}).get("FUNDING_RATE") for b in bary]
    closes = [b["close"] for b in bary]
    pokrycie = sum(1 for f in fund if f is not None)
    wynik = {}
    for h in horyzonty:
        zwr = _zwroty_fwd(closes, h)
        ic_nn, n_nn = _ic(fund, zwr, krok=h)     # nienakładające
        ic_ov, n_ov = _ic(fund, zwr, krok=1)     # nakładające
        wynik[h] = {"ic_nn": ic_nn, "n_nn": n_nn, "ic_ov": ic_ov, "n_ov": n_ov}
    return wynik, len(bary), pokrycie


def main(argv=None):
    import numpy as np
    p = argparse.ArgumentParser(description="Probatio funding IC (walidacja TIER A, Prawo I).")
    p.add_argument("--symbole", nargs="+", default=DOMYSLNE_SYMBOLE)
    p.add_argument("--interwal", default="1H")
    p.add_argument("--limit", type=int, default=500, help="ile barów OHLCV (MEXC cap ~500)")
    p.add_argument("--horyzonty", nargs="+", type=int, default=[6, 12, 24],
                   help="horyzonty zwrotu forward w barach")
    p.add_argument("--arena", action="store_true",
                   help="zapisz IC do arena_wyniki.db (rodzaj=WALIDACJA_FUNDING)")
    a = p.parse_args(argv)

    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    logging.disable(logging.WARNING)
    from imperium.akwedukty.kwatermistrz_danych import DataLoader
    from imperium.akwedukty.adaptery.futures import AdapterFutures

    loader, adf = DataLoader(), AdapterFutures()
    print(f"🧪 PROBATIO FUNDING (TIER A) — {len(a.symbole)} par {a.interwal} x{a.limit}, "
          f"horyzonty {a.horyzonty} barów. Pomiar-najpierw (Prawo I).\n")

    agg = {h: [] for h in a.horyzonty}     # tylko nienakładające do werdyktu
    wiersze_arena = []
    n = len(a.symbole)
    print(f"{'para':10} " + "  ".join(f"IC(h={h})nn/ov" for h in a.horyzonty))
    print("-" * (10 + 20 * len(a.horyzonty)))
    for i, sym in enumerate(a.symbole, 1):
        _pasek(i, n, f"funding+OHLCV {sym}")
        try:
            wynik, nbar, pokr = _pomiar_symbolu(sym, a.interwal, a.limit, a.horyzonty, loader, adf)
        except Exception as e:
            print(f"\n{sym:10} BŁĄD: {e}", file=sys.stderr)
            continue
        komorki = []
        for h in a.horyzonty:
            w = wynik[h]
            nn = f"{w['ic_nn']:+.3f}" if w["ic_nn"] is not None else " n/a "
            ov = f"{w['ic_ov']:+.3f}" if w["ic_ov"] is not None else " n/a "
            komorki.append(f"{nn}/{ov}")
            if w["ic_nn"] is not None:
                agg[h].append(w["ic_nn"])
                wiersze_arena.append(("WALIDACJA_FUNDING", f"FUNDING_IC_h{h}", float(w["ic_nn"]),
                                      f"{sym} {a.interwal} n={w['n_nn']} pokrycie={pokr}/{nbar}"))
        print(f"{sym:10} " + "  ".join(f"{c:>16}" for c in komorki))

    print("\n" + "=" * 68)
    print(" WERDYKT PROBATIO — średnie IC nienakładające (po parach)")
    print("=" * 68)
    for h in a.horyzonty:
        vals = agg[h]
        if not vals:
            print(f"  h={h:>2}: brak policzalnych (za mało nienakł. próbek — zwiększ --limit lub h↓)")
            continue
        sr = float(np.mean(vals))
        zgodnosc = sum(1 for v in vals if (v < 0) == (sr < 0))
        werdykt = ("SKILL ✅" if abs(sr) > PROG_SKILL else "szum ~0 ⚠️")
        kier = "kontrariański (funding↑→cena↓)" if sr < 0 else "podążający (funding↑→cena↑)"
        print(f"  h={h:>2}: śr IC={sr:+.4f}  [{werdykt}]  {kier}  "
              f"zgodność znaku {zgodnosc}/{len(vals)} par")
    print("=" * 68)
    print(f" Próg skill |IC|>{PROG_SKILL}. Nienakładające = uczciwe; nakładające (ov) zwykle "
          f"|IC| większe (inflacja autokorelacją).")

    if a.arena and wiersze_arena:
        from imperium.biblioteki.arena_baza import zapisz_pomiary
        z = zapisz_pomiary(wiersze_arena)
        print(f" 💾 Arena: zapisano {z} pomiarów (rodzaj=WALIDACJA_FUNDING).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
