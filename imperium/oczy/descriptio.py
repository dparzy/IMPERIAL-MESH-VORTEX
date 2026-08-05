"""🏛️ DESCRIPTIO IMPERII — z jakich FILARÓW zbudowane jest Imperium i czy któryś słabnie.

Rzymska *descriptio* to formalny opis-spis państwa sporządzany przy cenzusie: nie lista
obywateli (od tego był census), lecz **podział na jednostki i ich wzajemny stosunek**.
Dokładnie ta różnica dzieli ten organ od CENSUS ORGANORUM: tamten odpowiada „ile modułów
i czy każdy zameldowany", ten — **„z jakich filarów Imperium się składa, kto do którego
należy, kto kogo woła i który filar jest za cienki"**.

POWÓD ISTNIENIA (rozkaz Cezara 2026-08-05): *„musimy wiedzieć, z jakich filarów, jakich
kategorii i jaki schemat ma nasze Imperium, jakie są do nich przypisane organy i jak
wzajemnie współpracują — wtedy będziemy po kolei naprawiać braki i luki. Nic nie wolno
pomijać."* Do dziś odpowiedzi nie było: `CENSUS_ORGANORUM` liczy moduły, `MATURITAS` mierzy
piętra, a `ARCHITEKTURA_IMPERIUM.md` opisuje organy **ręcznie** — więc gnije (2026-08-05
znaleziono cztery przeterminowane liczby w jednej wachcie). Mapa Imperium pisana ręcznie
kłamie tym pewniej, im większe Imperium; **jedyną uczciwą formą jest generator**.

ZASADY KONSTRUKCYJNE (te same cztery klasy, które tępi LUSTRATIO):
  • **K1 — jeden fakt, jeden producent.** Lista modułów pochodzi z `census_organorum.spisz_moduly()`,
    piętra z `maturitas.zmierz()`. Ten organ **nie liczy modułów po raz drugi** — inaczej
    dwie liczby zaczęłyby się rozjeżdżać i nikt by nie wiedział, która kłamie.
  • **K2 — nieprzypisany moduł to ALARM, nie cisza.** `zgodny()` jest fałszem, gdy suma
    filarów ≠ liczbie modułów. Nowy katalog w repo **musi** wywrócić ten organ na czerwono,
    zamiast po cichu wypaść z obrazu — na tym poległ MATURITAS (52 wiersze poza pomiarem).
  • **Strażnik nazwany musi ISTNIEĆ.** Filar wskazuje organ, który go pilnuje; jeśli tego
    pliku nie ma w kodzie, `bledy()` krzyczy. Inaczej dopisalibyśmy Imperium strażników-widma.
  • **Miara cienkości jest OPISOWA, nie normatywna.** Organ mówi, ile modułów i połączeń ma
    filar; NIE mówi „za mało" progiem z sufitu. Próg bez kalibracji byłby zgadywaniem
    udającym pomiar (LEX TALARUS), a Imperium ma już jeden taki dług.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

KORZEN = Path(__file__).resolve().parent.parent.parent

# ── PODZIAŁ NA FILARY ───────────────────────────────────────────────────────────
# Klucz: katalog w repo (prefiks). Wartość: (FILAR, po co istnieje, organ-strażnik).
# Strażnik = organ, który pilnuje ZDROWIA tego filara, nie ten, który w nim najwięcej robi.
FILARY: List[Tuple[str, str, str, str]] = [
    ("imperium/biblioteki", "I. WIEDZA I PAMIĘĆ",
     "pamięta, przechowuje i oddaje wiedzę — 14 warstw pamięci + ledgery",
     "imperium/biblioteki/kustosz_pamieci.py"),
    ("narzedzia/rag", "I. WIEDZA I PAMIĘĆ",
     "wydobywa i wyszukuje wiedzę z biblioteki (Bibliotheca Ulpia)",
     "narzedzia/rag/quaesitor.py"),
    ("imperium/oczy", "II. ZMYSŁY",
     "mierzy stan Imperium i sprzętu — patrzy, nie decyduje",
     "imperium/oczy/maturitas.py"),
    ("imperium/akwedukty", "III. DANE",
     "doprowadza dane z zewnątrz: bary, news, adaptery",
     "imperium/pretorianie/portitor.py"),
    ("imperium/legiony", "IV. RÓJ",
     "liczy sygnały: neurony, zwiadowcy, Legatus",
     "imperium/legiony/diagnostyka_korelacji.py"),
    ("imperium/cesarz", "V. DECYZJA",
     "waży opinie i rozstrzyga: doradcy, Titan Mind, szafarz modeli",
     "imperium/cesarz/doradcy/rada.py"),
    ("imperium/senat", "V. DECYZJA",
     "debata i konsensus nad sygnałem",
     "imperium/senat/meta_kora.py"),
    ("imperium/koloseum", "VI. PRÓBA",
     "poddaje próbie: backtest, walidacja, walk-forward, arena",
     "imperium/koloseum/walidacja.py"),
    ("imperium/pretorianie", "VII. OBRONA I PRAWO",
     "broni prawa i spójności: strażnicy, bramki, kalkulator ryzyka",
     "imperium/pretorianie/vindex.py"),
    ("imperium/drogi", "VIII. EGZEKUCJA",
     "zamienia decyzję w order — jedyny styk z rynkiem",
     "imperium/drogi/nexus_hub.py"),
    ("imperium/fundament", "IX. FUNDAMENT",
     "jedyne wejście do matematyki (Prawo I) — Brama Kalkulatora",
     "imperium/fundament/brama_kalkulatora.py"),
    ("imperium/swiatynie", "X. WIDOK",
     "pokazuje Imperium Cezarowi: Praetorium, dashboard, wykresy",
     "imperium/swiatynie/praetorium.py"),
    ("narzedzia", "XI. NARZĘDZIA I POMIAR",
     "mierzy, audytuje i raportuje — warstwa, która pyta wszystkie inne",
     "narzedzia/audyt_spojnosci.py"),
]

# `narzedzia` jest CELOWO ostatnie: dopasowanie idzie po NAJDŁUŻSZYM prefiksie, więc
# `narzedzia/rag` trafia do WIEDZY, a reszta `narzedzia/` do POMIARU. Kolejność w liście
# nie decyduje o wyniku — decyduje długość prefiksu — ale zapisana wprost oszczędza pytań.


def _filar_dla(katalog: str) -> Optional[Tuple[str, str, str]]:
    """(FILAR, po co, strażnik) dla katalogu — po NAJDŁUŻSZYM pasującym prefiksie."""
    najlepszy, wynik = "", None
    for prefiks, filar, po_co, straznik in FILARY:
        if (katalog == prefiks or katalog.startswith(prefiks + "/")) and len(prefiks) > len(najlepszy):
            najlepszy, wynik = prefiks, (filar, po_co, straznik)
    return wynik


def podzial() -> Dict[str, Any]:
    """Filary z ŻYWEGO kodu. Producent listy modułów: `census_organorum` (K1)."""
    sys.path.insert(0, str(KORZEN)) if str(KORZEN) not in sys.path else None
    from narzedzia.census_organorum import spisz_moduly          # producent

    spis = spisz_moduly()
    filary: Dict[str, Dict[str, Any]] = {}
    nieprzypisane: List[str] = []
    razem = 0
    for katalog, wpisy in spis.items():
        razem += len(wpisy)
        trafienie = _filar_dla(katalog)
        if trafienie is None:
            nieprzypisane.extend(f"{katalog}/{n}" for n, _ in wpisy)
            continue
        filar, po_co, straznik = trafienie
        wpis = filary.setdefault(filar, {"po_co": po_co, "straznik": straznik,
                                         "moduly": [], "katalogi": []})
        wpis["moduly"].extend(f"{katalog}/{n}" for n, _ in wpisy)
        wpis["katalogi"].append(katalog)
    return {"filary": dict(sorted(filary.items())),
            "nieprzypisane": nieprzypisane,
            "modulow_razem": razem}


def wspolpraca(p: Optional[Dict[str, Any]] = None) -> Dict[Tuple[str, str], int]:
    """Krawędzie MIĘDZY filarami: ile razy moduł jednego filara importuje moduł innego.

    Liczymy po NAZWACH modułów, bo importy w repo bywają i bezwzględne, i względne, i robione
    leniwie wewnątrz funkcji — pełne parsowanie AST łapałoby tylko część, a różnica byłaby
    niewidoczna. To miara RUCHU, nie dokładnej liczby wywołań; do porównywania filarów między
    sobą wystarcza, do orzekania o pojedynczym module NIE — i tak jest opisana.
    """
    p = p or podzial()
    gdzie = {Path(m).stem: f for f, d in p["filary"].items() for m in d["moduly"]}
    kraw: Dict[Tuple[str, str], int] = {}
    for filar, dane in p["filary"].items():
        for wzgl in dane["moduly"]:
            plik = KORZEN / wzgl
            if not plik.exists():
                continue
            tekst = plik.read_text(encoding="utf-8", errors="replace")
            for m in set(re.findall(r"(?:from|import)\s+([\w\.]+)", tekst)):
                cel = gdzie.get(m.split(".")[-1])
                if cel and cel != filar:
                    kraw[(filar, cel)] = kraw.get((filar, cel), 0) + 1
    return kraw


def bledy(p: Optional[Dict[str, Any]] = None) -> List[str]:
    """Co jest NIE TAK z samym podziałem. Pusta lista = obraz Imperium jest kompletny."""
    p = p or podzial()
    out: List[str] = []
    if p["nieprzypisane"]:
        ile = len(p["nieprzypisane"])
        out.append(f"[DESCRIPTIO] {ile} modułów POZA filarami (nowy katalog bez wpisu w FILARY): "
                   + ", ".join(p["nieprzypisane"][:5]) + (" …" if ile > 5 else ""))
    suma = sum(len(d["moduly"]) for d in p["filary"].values()) + len(p["nieprzypisane"])
    if suma != p["modulow_razem"]:
        out.append(f"[DESCRIPTIO] suma filarów {suma} ≠ modułów w CENSUS {p['modulow_razem']} "
                   "— podział gubi moduły po drodze")
    for filar, dane in p["filary"].items():
        if not (KORZEN / dane["straznik"]).exists():
            out.append(f"[DESCRIPTIO] filar {filar} wskazuje strażnika, którego NIE MA w kodzie: "
                       f"{dane['straznik']}")
    return out


def zgodny(p: Optional[Dict[str, Any]] = None) -> bool:
    """Czy obraz Imperium jest kompletny — bez sierot i bez strażników-widm."""
    return not bledy(p)


def raport_tekst(p: Optional[Dict[str, Any]] = None, zwiezle: bool = False) -> str:
    p = p or podzial()
    kraw = wspolpraca(p)
    wych: Dict[str, int] = {}
    przych: Dict[str, int] = {}
    for (a, b), n in kraw.items():
        wych[a] = wych.get(a, 0) + n
        przych[b] = przych.get(b, 0) + n

    linie = ["🏛️ DESCRIPTIO IMPERII — filary, organy i ich współpraca"]
    for filar, dane in p["filary"].items():
        n = len(dane["moduly"])
        linie.append(f"   {filar:24} {n:>4} organów | woła {wych.get(filar, 0):>3}"
                     f" | wołany {przych.get(filar, 0):>3}")
        if not zwiezle:
            linie.append(f"      · po co: {dane['po_co']}")
            linie.append(f"      · strażnik: {dane['straznik']}")
    linie.append(f"   {'RAZEM':24} {p['modulow_razem']:>4} modułów (źródło: CENSUS ORGANORUM)")

    b = bledy(p)
    if b:
        linie.append("   🚨 OBRAZ NIEKOMPLETNY:")
        linie.extend(f"      ❌ {x}" for x in b)
    else:
        linie.append("   ✅ Każdy moduł Imperium należy do filara — zero pominięć.")
    return "\n".join(linie)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = podzial()
    if "--json" in argv:
        import json
        dane = {f: {"organow": len(d["moduly"]), "po_co": d["po_co"], "straznik": d["straznik"]}
                for f, d in p["filary"].items()}
        print(json.dumps({"filary": dane, "modulow_razem": p["modulow_razem"],
                          "bledy": bledy(p)}, ensure_ascii=False, indent=2))
    else:
        print(raport_tekst(p, zwiezle="--zwiezle" in argv))
    return 1 if ("--bramka" in argv and not zgodny(p)) else 0


if __name__ == "__main__":
    sys.exit(main())
