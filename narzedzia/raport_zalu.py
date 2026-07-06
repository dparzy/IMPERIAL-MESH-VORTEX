"""
👥 RAPORT ŻALU — Kronika Żyć Nieprzeżytych (Legiony Cieni, krok 3 wizji).

Czyta z bazy areny wyniki realnego roju (LIVE_PNL) i widmowych wariantów (CIEN_PNL,
z legiony_cieni.py) i liczy ŻAL każdego mechanizmu: ile kosztowała nas ostrożność,
ile odwaga — per reżim, zmierzone na żywo (Prawo XV: alarm o niewykorzystanych DECYZJACH).

ŻAL (definicja v1, prosta i uczciwa):
  żal(cień) = średni PnL% cienia − średni PnL% realnego roju
  • żal > 0  → cień zarobiłby WIĘCEJ niż my → nasza decyzja KOSZTOWAŁA
  • żal < 0  → cień zarobiłby MNIEJ → nasza decyzja URATOWAŁA (dobrze wybraliśmy)

INTERPRETACJA per cień:
  • bez_wet       żal>0 → weta/bezpieczniki nas KOSZTUJĄ; żal<0 → weta CHRONIĄ
  • prog_lagodny  żal>0 → jesteśmy ZA OSTROŻNI (luźniejszy próg by zarobił)
  • prog_surowy   żal>0 → jesteśmy ZA ODWAŻNI (surowszy próg by zarobił)

OGRANICZENIE (Prawo I — jawne): real (LIVE_PNL, per symbol) i cienie (CIEN_PNL, per
wariant) to OSOBNE serie, nie sparowane trade-po-trade. Porównanie średnich to
zgrubny pierwszy pomiar kierunku żalu, nie precyzyjny per-trade rachunek. Przy próbie
< min_barow raport mówi „za mało danych" (NIE zmyśla werdyktu z szumu).

FUNDAMENT (ZPO): Counterfactual Regret Minimization — Zinkevich, Johanson, Bowling,
  Piccione, NeurIPS 2007. ⚠️ link: https://papers.nips.cc/paper/2007/hash/08d98638c6fcd194a4b1e6992063e944-Abstract.html

Użycie (na LAPTOPIE po sesji live z cienie=True):
  python narzedzia/raport_zalu.py                 # wszystkie dane z arena_wyniki.db
  python narzedzia/raport_zalu.py --min-barow 100 # werdykt tylko przy ≥100 zamknięciach
  python narzedzia/raport_zalu.py --db inna.db
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Kanoniczne reżimy (klasyfikuj_rezim / namiestnik) — do parsowania noty pomiaru
REZIMY = {"NORMAL", "RANGING", "TREND_STRONG", "VOLATILE", "PANIC"}

# Duży limit — chcemy CAŁĄ historię pomiarów, nie ostatnie 20
_LIMIT = 1_000_000

_INTERPRETACJE = {
    "bez_wet": ("weta/bezpieczniki nas KOSZTUJĄ (odważny cień zarobił więcej)",
                "weta CHRONIĄ (odważny cień stracił więcej)"),
    "prog_lagodny": ("jesteśmy ZA OSTROŻNI (luźniejszy próg by zarobił)",
                     "luźniejszy próg by stracił — próg dobrze trzyma"),
    "prog_surowy": ("jesteśmy ZA ODWAŻNI (surowszy próg by zarobił)",
                    "surowszy próg by stracił — nie warto zaostrzać"),
}


def _rezim_z_noty(nota: str) -> str:
    """Wyłuskuje kanoniczny reżim z noty pomiaru (dowolna pozycja tokenu). Fallback NORMAL."""
    for token in (nota or "").split():
        if token in REZIMY:
            return token
    return "NORMAL"


def _agreguj(pomiary: list) -> dict:
    """{reżim: [pnl...]} + '__all__' zbiorczo. Pomiary z arena_baza.pytaj_pomiary."""
    grupy: dict = {"__all__": []}
    for p in pomiary:
        pnl = float(p["wartosc"])
        rez = _rezim_z_noty(p.get("nota", ""))
        grupy.setdefault(rez, []).append(pnl)
        grupy["__all__"].append(pnl)
    return grupy


def _srednia(xs: list):
    return sum(xs) / len(xs) if xs else None


def zbierz_zal(db_path=None, min_barow: int = 1) -> dict:
    """
    Liczy żal per cień per reżim z bazy areny. Zwraca strukturę raportu (Prawo I: gdy
    real lub cień ma < min_barow zamknięć w danym reżimie → werdykt 'za mało danych').
    """
    from imperium.biblioteki.arena_baza import pytaj_pomiary, DEFAULT_DB
    db = db_path or DEFAULT_DB

    real = pytaj_pomiary(rodzaj="LIVE_PNL", limit=_LIMIT, db_path=db)
    cienie = pytaj_pomiary(rodzaj="CIEN_PNL", limit=_LIMIT, db_path=db)

    real_grupy = _agreguj(real)
    # cienie per nazwa (neuron = nazwa cienia)
    cienie_per_nazwa: dict = {}
    for p in cienie:
        cienie_per_nazwa.setdefault(p["neuron"], []).append(p)

    wyniki = []
    for nazwa in sorted(cienie_per_nazwa):
        cg = _agreguj(cienie_per_nazwa[nazwa])
        per_rezim = []
        for rez in sorted(set(cg) | set(real_grupy)):
            if rez == "__all__":
                continue
            cien_pnl = cg.get(rez, [])
            real_pnl = real_grupy.get(rez, [])
            per_rezim.append(_werdykt(rez, nazwa, cien_pnl, real_pnl, min_barow))
        wyniki.append({
            "cien": nazwa,
            "ogolem": _werdykt("OGÓŁEM", nazwa, cg["__all__"], real_grupy["__all__"], min_barow),
            "per_rezim": per_rezim,
        })

    return {
        "real_zamkniec": len(real),
        "cien_zamkniec": len(cienie),
        "min_barow": min_barow,
        "cienie": wyniki,
    }


def _werdykt(rezim: str, nazwa: str, cien_pnl: list, real_pnl: list, min_barow: int) -> dict:
    """Żal cienia vs real w jednym reżimie. Za mało próby → 'za mało danych' (bez werdyktu)."""
    cien_sr = _srednia(cien_pnl)
    real_sr = _srednia(real_pnl)
    dose = min(len(cien_pnl), len(real_pnl))
    if cien_sr is None or real_sr is None or dose < min_barow:
        return {"rezim": rezim, "n_cien": len(cien_pnl), "n_real": len(real_pnl),
                "zal": None, "werdykt": "za mało danych"}
    zal = round(cien_sr - real_sr, 4)
    poz, neg = _INTERPRETACJE.get(nazwa, ("cień zarobił więcej", "cień zarobił mniej"))
    return {
        "rezim": rezim, "n_cien": len(cien_pnl), "n_real": len(real_pnl),
        "cien_sr": round(cien_sr, 4), "real_sr": round(real_sr, 4),
        "zal": zal, "werdykt": (poz if zal > 0 else neg) if zal != 0 else "bez różnicy",
    }


def raport_tekst(dane: dict) -> str:
    """Formatuje Kronikę Żyć Nieprzeżytych do czytelnego raportu."""
    L = ["=" * 72,
         "👥 KRONIKA ŻYĆ NIEPRZEŻYTYCH — Raport Żalu (Legiony Cieni)",
         "=" * 72,
         f"Zamknięć: realnych {dane['real_zamkniec']} | cieni {dane['cien_zamkniec']} "
         f"| próg werdyktu: ≥{dane['min_barow']} zamknięć"]
    if not dane["cienie"]:
        L.append("\n  (brak danych CIEN_PNL — uruchom pętlę live z cienie=True)")
        return "\n".join(L)
    for c in dane["cienie"]:
        og = c["ogolem"]
        zal = og.get("zal")
        znak = "🔴" if (zal or 0) > 0 else ("🟢" if (zal or 0) < 0 else "⚪")
        L.append(f"\n{znak} CIEŃ „{c['cien']}\" — ogółem: "
                 f"{'żal ' + format(zal, '+.4f') + '% → ' + og['werdykt'] if zal is not None else og['werdykt']}")
        for r in c["per_rezim"]:
            rz = r.get("zal")
            if rz is None:
                L.append(f"     · {r['rezim']:14} {r['werdykt']} (cień {r['n_cien']}, real {r['n_real']})")
            else:
                L.append(f"     · {r['rezim']:14} żal {rz:+.4f}%  (cień {r['cien_sr']:+.3f} vs "
                         f"real {r['real_sr']:+.3f}, n={r['n_cien']}/{r['n_real']}) → {r['werdykt']}")
    return "\n".join(L)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Raport Żalu — Kronika Żyć Nieprzeżytych (Legiony Cieni)")
    p.add_argument("--db", default=None, help="Ścieżka do arena_wyniki.db (domyślnie bazowa)")
    p.add_argument("--min-barow", type=int, default=1,
                   help="Minimum zamknięć w reżimie na werdykt (Prawo I — bez werdyktu z szumu)")
    args = p.parse_args(argv)
    dane = zbierz_zal(db_path=args.db, min_barow=args.min_barow)
    print(raport_tekst(dane))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
