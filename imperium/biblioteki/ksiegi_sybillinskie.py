"""
🔮 KSIĘGI SYBILLIŃSKIE — rejestr falsyfikowalnych proroctw Imperium o SOBIE.

Perełka II (docs/WIZJA_KSIEGI_SYBILLINSKIE.md → KOD, Prawo XIX). Siostra Legionów Cieni:
Cienie mierzą DECYZJE nieprzeżyte — Sybilla mierzy PRZEKONANIA instytucji o samej sobie.

IDEA (jedno zdanie):
  Imperium spisuje o sobie proroctwa z prawdopodobieństwem P i terminem, a przyszłe sesje
  rozliczają je AUTOMATYCZNIE z bazy areny (zero opinii — Prawo I). Po roku wiemy nie tylko
  czy system zarabia, ale czy system WIE, CO O SOBIE WIE (Brier score instytucji).

MECHANIZM (deterministyczny, na tym co mamy):
  1. dodaj()   — proroctwo → linia JSONL w git (P i twierdzenie NIEMUTOWALNE przez historię).
  2. rozlicz() — proroctwa po horyzoncie rozstrzygane z pomiarów areny (arena_baza).
                 Brak danych → NIEROZSTRZYGNIĘTE (jawnie, nie znika cicho — Prawo I).
  3. brier()   — proper scoring rule: średnia (P − wynik)²; niższy = lepsza samowiedza.
  4. krzywa_kalibracji() — gdy mówimy „70%", jak często mamy rację? (per kubełek P)

ANTY-OSZUSTWO (falsyfikowalność, Prawo I):
  `rozlicz()` NIGDY nie zmienia P, twierdzenia, progu ani metryki — dopisuje wyłącznie
  status/data_rozliczenia/zmierzono. Zmiana P po fakcie byłaby widoczna w git diff.
  Brier liczony TYLKO z proroctw rozstrzygniętych (TRAFIONE/CHYBIONE) — asekuranctwo karane.

FUNDAMENT (ZPO):
  • Brier score — G.W. Brier, Monthly Weather Review 1950 (proper scoring rule).
    ⚠️ link do weryfikacji: https://journals.ametsoc.org/view/journals/mwre/78/1/1520-0493_1950_078_0001_vofeit_2_0_co_2.xml
  • Proper scoring rules — Gneiting & Raftery, JASA 2007. ⚠️ do weryfikacji.
  • Superforecasting — Tetlock & Gardner 2015: trafność rośnie od prowadzenia rozliczanego rejestru.

ZASADA WPIĘCIA: Sybilla to PAMIĘĆ/soczewka, poza ścieżką decyzyjną tradingu — nie zmienia
  zachowania roju. „Zegar" (realne proroctwa) zasiewa Cezar świadomie; moduł sam nic nie sieje.

CLI:
  python -m imperium.biblioteki.ksiegi_sybillinskie dodaj "twierdzenie" 0.70 200 --metryka IC_WARUNKOWY --neuron NEWS-01 --prog 0.02 --kierunek abs>=
  python -m imperium.biblioteki.ksiegi_sybillinskie lista
  python -m imperium.biblioteki.ksiegi_sybillinskie rozlicz
  python -m imperium.biblioteki.ksiegi_sybillinskie brier
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
PLIK_DOMYSLNY = ROOT / "bibliotheca_ulpia" / "dane" / "proroctwa.jsonl"

# Statusy rozliczenia (Prawo I — NIEROZSTRZYGNIETE jest jawne, nie znika)
OTWARTE = "OTWARTE"
TRAFIONE = "TRAFIONE"
CHYBIONE = "CHYBIONE"
NIEROZSTRZYGNIETE = "NIEROZSTRZYGNIETE"
STATUSY_ROZSTRZYGNIETE = {TRAFIONE, CHYBIONE}

# Kierunki porównania zmierzonej wartości z progiem
KIERUNKI = {">=", "<=", ">", "<", "abs>=", "abs<="}
# Agregacja pomiarów areny do jednej liczby przed porównaniem
AGREGATY = {"srednia", "ostatni", "suma", "liczba"}

# Pola NIETYKALNE po utworzeniu (falsyfikowalność) — rozlicz() ich nie dotyka
_POLA_NIEMUTOWALNE = ("id", "data", "twierdzenie", "metryka", "neuron", "prog",
                      "kierunek", "agregat", "horyzont_dni", "P", "domena", "zrodlo")


def _dzis() -> date:
    return date.today()


def _wczytaj(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    plik = plik or PLIK_DOMYSLNY
    if not Path(plik).exists():
        return []
    wynik = []
    for linia in Path(plik).read_text(encoding="utf-8", errors="ignore").splitlines():
        linia = linia.strip()
        if not linia:
            continue
        try:
            wynik.append(json.loads(linia))
        except (json.JSONDecodeError, ValueError):
            continue
    return wynik


def _nadpisz(wpisy: List[Dict[str, Any]], plik: Optional[Path] = None) -> None:
    plik = plik or PLIK_DOMYSLNY
    Path(plik).parent.mkdir(parents=True, exist_ok=True)
    with Path(plik).open("w", encoding="utf-8") as f:
        for w in wpisy:
            f.write(json.dumps(w, ensure_ascii=False) + "\n")


def _nastepny_id(wpisy: List[Dict[str, Any]]) -> str:
    n = 0
    for w in wpisy:
        sid = str(w.get("id", ""))
        if sid.startswith("SYB-"):
            try:
                n = max(n, int(sid.split("-")[1]))
            except (IndexError, ValueError):
                pass
    return f"SYB-{n + 1:04d}"


# ─── Tworzenie proroctwa ─────────────────────────────────────────────────────

def dodaj(twierdzenie: str, P: float, horyzont_dni: int,
          metryka: str = "", neuron: str = "", prog: float = 0.0,
          kierunek: str = "abs>=", agregat: str = "srednia",
          domena: str = "ogolne", zrodlo: str = "",
          data: Optional[str] = None, plik: Optional[Path] = None,
          dedup: bool = True) -> Optional[str]:
    """
    Zapisuje falsyfikowalne proroctwo. Zwraca jego id (SYB-NNNN) lub None gdy duplikat.

    twierdzenie   — czytelne zdanie (ZPO — pełny opis dla nowicjusza).
    P             — prawdopodobieństwo trafienia ∈ [0,1] (0 i 1 dozwolone — skrajna pewność).
    horyzont_dni  — po ilu dniach proroctwo można rozstrzygnąć (≥0).
    metryka       — rodzaj pomiaru w arenie do auto-rozstrzygnięcia (np. IC_WARUNKOWY,
                    LIVE_PNL, WAZNOSC). Pusta → proroctwo rozstrzygalne tylko ręcznie.
    neuron        — podmiot pomiaru (np. NEWS-01, ROJ). prog/kierunek/agregat definiują test.
    """
    if not (0.0 <= P <= 1.0):
        raise ValueError("P musi być w [0,1]")
    if horyzont_dni < 0:
        raise ValueError("horyzont_dni musi być ≥0")
    if kierunek not in KIERUNKI:
        raise ValueError(f"kierunek musi być jednym z: {sorted(KIERUNKI)}")
    if agregat not in AGREGATY:
        raise ValueError(f"agregat musi być jednym z: {sorted(AGREGATY)}")
    twierdzenie = twierdzenie.strip()
    if not twierdzenie:
        raise ValueError("twierdzenie nie może być puste")

    wpisy = _wczytaj(plik)
    if dedup:
        for w in wpisy:
            if w.get("twierdzenie", "").strip().lower() == twierdzenie.lower():
                return None  # duplikat — nie dublujemy proroctwa

    nowe = {
        "id": _nastepny_id(wpisy),
        "data": data or _dzis().isoformat(),
        "twierdzenie": twierdzenie,
        "metryka": metryka,
        "neuron": neuron,
        "prog": float(prog),
        "kierunek": kierunek,
        "agregat": agregat,
        "horyzont_dni": int(horyzont_dni),
        "P": float(P),
        "domena": domena,
        "zrodlo": zrodlo,
        "status": OTWARTE,
        "data_rozliczenia": None,
        "zmierzono": None,
    }
    wpisy.append(nowe)
    _nadpisz(wpisy, plik)
    return nowe["id"]


# ─── Rozstrzyganie ───────────────────────────────────────────────────────────

def _po_horyzoncie(pror: Dict[str, Any], teraz: date) -> bool:
    """Czy minął horyzont proroctwa (można je rozstrzygać)."""
    try:
        data_utw = date.fromisoformat(pror["data"])
    except (KeyError, ValueError):
        return False
    return teraz >= data_utw + timedelta(days=int(pror.get("horyzont_dni", 0)))


def _agreguj(pomiary: List[Dict[str, Any]], jak: str) -> Optional[float]:
    """Redukuje pomiary areny do jednej liczby. Zwraca None gdy brak danych."""
    if not pomiary:
        return None
    wart = [float(p["wartosc"]) for p in pomiary]
    if jak == "liczba":
        return float(len(wart))
    if jak == "suma":
        return float(sum(wart))
    if jak == "ostatni":
        # pytaj_pomiary zwraca najnowsze pierwsze → element [0]
        return wart[0]
    return sum(wart) / len(wart)  # srednia (domyślnie)


def _porownaj(zmierzono: float, prog: float, kierunek: str) -> bool:
    """Test proroctwa: czy zmierzona wartość spełnia próg w danym kierunku."""
    if kierunek == ">=":
        return zmierzono >= prog
    if kierunek == "<=":
        return zmierzono <= prog
    if kierunek == ">":
        return zmierzono > prog
    if kierunek == "<":
        return zmierzono < prog
    if kierunek == "abs>=":
        return abs(zmierzono) >= prog
    if kierunek == "abs<=":
        return abs(zmierzono) <= prog
    return False


def _zmierz_z_areny(pror: Dict[str, Any], db_path=None, limit: int = 500) -> Optional[float]:
    """Pyta arenę o pomiary metryki/neuronu proroctwa i agreguje. None → brak danych."""
    metryka = pror.get("metryka") or ""
    if not metryka:
        return None  # proroctwo bez metryki — rozstrzygalne tylko ręcznie
    from imperium.biblioteki.arena_baza import pytaj_pomiary, DEFAULT_DB
    pomiary = pytaj_pomiary(
        rodzaj=metryka, neuron=(pror.get("neuron") or None),
        limit=limit, db_path=db_path or DEFAULT_DB,
    )
    return _agreguj(pomiary, pror.get("agregat", "srednia"))


def rozlicz(teraz: Optional[date] = None, db_path=None,
            plik: Optional[Path] = None, wynik_reczny: Optional[Dict[str, bool]] = None) -> Dict[str, int]:
    """
    Rozstrzyga proroctwa OTWARTE, którym minął horyzont — z pomiarów areny (Prawo I).

    wynik_reczny: opcjonalna mapa {id_proroctwa: True/False} dla proroctw bez metryki
                  (rozstrzyganych z wyników walidacji, których nie ma w arenie).
    Zwraca licznik {rozliczone, trafione, chybione, nierozstrzygniete, otwarte}.

    NIEMUTOWALNOŚĆ: dotyka WYŁĄCZNIE status/data_rozliczenia/zmierzono. P i twierdzenie
    pozostają nietknięte (falsyfikowalność — Prawo I).
    """
    teraz = teraz or _dzis()
    wynik_reczny = wynik_reczny or {}
    wpisy = _wczytaj(plik)
    licz = {"rozliczone": 0, "trafione": 0, "chybione": 0,
            "nierozstrzygniete": 0, "otwarte": 0}
    zmieniono = False

    for w in wpisy:
        if w.get("status") != OTWARTE:
            continue
        if not _po_horyzoncie(w, teraz):
            licz["otwarte"] += 1
            continue

        # Rozstrzygnięcie: ręczne (walidacja) ma priorytet, potem arena
        trafil: Optional[bool] = None
        zmierzono: Optional[float] = None
        if w.get("id") in wynik_reczny:
            trafil = bool(wynik_reczny[w["id"]])
        else:
            zmierzono = _zmierz_z_areny(w, db_path=db_path)
            if zmierzono is not None:
                trafil = _porownaj(zmierzono, float(w.get("prog", 0.0)), w.get("kierunek", "abs>="))

        if trafil is None:
            w["status"] = NIEROZSTRZYGNIETE
            licz["nierozstrzygniete"] += 1
        else:
            w["status"] = TRAFIONE if trafil else CHYBIONE
            licz["trafione" if trafil else "chybione"] += 1
        w["data_rozliczenia"] = teraz.isoformat()
        w["zmierzono"] = zmierzono
        licz["rozliczone"] += 1
        zmieniono = True

    if zmieniono:
        _nadpisz(wpisy, plik)
    return licz


def do_rozliczenia(teraz: Optional[date] = None, plik: Optional[Path] = None) -> int:
    """Ile proroctw OTWARTYCH ma już przekroczony horyzont (do hooka startowego)."""
    teraz = teraz or _dzis()
    return sum(1 for w in _wczytaj(plik)
               if w.get("status") == OTWARTE and _po_horyzoncie(w, teraz))


# ─── Kalibracja (Brier + krzywa) ─────────────────────────────────────────────

def brier(domena: Optional[str] = None, plik: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """
    Brier score po proroctwach ROZSTRZYGNIĘTYCH (TRAFIONE=1, CHYBIONE=0).
    Brier = średnia (P − wynik)²; 0 = doskonała samowiedza, 0.25 = rzut monetą przy P=0.5.
    Zwraca None gdy brak rozstrzygniętych proroctw (Prawo I — nie zmyślamy metryki z pustki).
    """
    rozs = [w for w in _wczytaj(plik) if w.get("status") in STATUSY_ROZSTRZYGNIETE
            and (domena is None or w.get("domena") == domena)]
    if not rozs:
        return None
    kwadraty = []
    trafien = 0
    for w in rozs:
        wynik = 1.0 if w.get("status") == TRAFIONE else 0.0
        kwadraty.append((float(w.get("P", 0.0)) - wynik) ** 2)
        trafien += int(wynik)
    return {
        "domena": domena or "wszystkie",
        "n": len(rozs),
        "brier": round(sum(kwadraty) / len(kwadraty), 4),
        "trafien": trafien,
        "trafnosc": round(trafien / len(rozs), 4),
    }


def krzywa_kalibracji(kubelki: int = 5, plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Krzywa kalibracji: dla każdego kubełka P — deklarowane P vs empiryczna trafność.
    Idealna kalibracja: sredni_P ≈ trafnosc w każdym kubełku. Puste kubełki pomijane.
    """
    if kubelki < 1:
        return []
    rozs = [w for w in _wczytaj(plik) if w.get("status") in STATUSY_ROZSTRZYGNIETE]
    grupy: Dict[int, List[Dict[str, Any]]] = {}
    for w in rozs:
        p = min(max(float(w.get("P", 0.0)), 0.0), 1.0)
        idx = min(int(p * kubelki), kubelki - 1)   # p==1.0 → ostatni kubełek
        grupy.setdefault(idx, []).append(w)

    krzywa = []
    for idx in sorted(grupy):
        g = grupy[idx]
        traf = sum(1 for w in g if w.get("status") == TRAFIONE)
        krzywa.append({
            "kubelek": f"{idx / kubelki:.2f}-{(idx + 1) / kubelki:.2f}",
            "n": len(g),
            "sredni_P": round(sum(float(w.get("P", 0.0)) for w in g) / len(g), 3),
            "trafnosc": round(traf / len(g), 3),
        })
    return krzywa


# ─── CLI ─────────────────────────────────────────────────────────────────────

def _cli(argv=None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Księgi Sybillińskie — rejestr proroctw Imperium")
    sub = p.add_subparsers(dest="cmd", required=True)

    pd = sub.add_parser("dodaj", help="Dodaj proroctwo")
    pd.add_argument("twierdzenie")
    pd.add_argument("P", type=float)
    pd.add_argument("horyzont_dni", type=int)
    pd.add_argument("--metryka", default="")
    pd.add_argument("--neuron", default="")
    pd.add_argument("--prog", type=float, default=0.0)
    pd.add_argument("--kierunek", default="abs>=", choices=sorted(KIERUNKI))
    pd.add_argument("--agregat", default="srednia", choices=sorted(AGREGATY))
    pd.add_argument("--domena", default="ogolne")
    pd.add_argument("--zrodlo", default="")

    sub.add_parser("lista", help="Pokaż wszystkie proroctwa")
    sub.add_parser("rozlicz", help="Rozstrzygnij proroctwa po horyzoncie")
    pb = sub.add_parser("brier", help="Brier score instytucji")
    pb.add_argument("--domena", default=None)

    args = p.parse_args(argv)

    if args.cmd == "dodaj":
        sid = dodaj(args.twierdzenie, args.P, args.horyzont_dni, metryka=args.metryka,
                    neuron=args.neuron, prog=args.prog, kierunek=args.kierunek,
                    agregat=args.agregat, domena=args.domena, zrodlo=args.zrodlo)
        print(f"🔮 {'Zapisano ' + sid if sid else 'Duplikat — pominięto'}")
    elif args.cmd == "lista":
        wpisy = _wczytaj()
        if not wpisy:
            print("🔮 Księgi puste — żadnego proroctwa jeszcze nie spisano.")
        for w in wpisy:
            print(f"  [{w.get('status'):17}] {w.get('id')} P={w.get('P'):.2f} "
                  f"h={w.get('horyzont_dni')}d — {w.get('twierdzenie')}")
    elif args.cmd == "rozlicz":
        licz = rozlicz()
        print(f"⚖️ Rozliczono {licz['rozliczone']}: "
              f"✅{licz['trafione']} ❌{licz['chybione']} ⁇{licz['nierozstrzygniete']} "
              f"| otwartych (przed horyzontem): {licz['otwarte']}")
    elif args.cmd == "brier":
        b = brier(domena=args.domena)
        if b is None:
            print("🔮 Brak rozstrzygniętych proroctw — Brier niepoliczalny (Prawo I).")
        else:
            print(f"📊 Brier [{b['domena']}] = {b['brier']} (n={b['n']}, "
                  f"trafność {b['trafnosc']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
