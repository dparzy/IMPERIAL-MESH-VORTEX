"""📐 MATURITAS — na którym PIĘTRZE inżynierii stoi Imperium i czy pętle się domykają.

Rzymska *maturitas* to dojrzałość: nie wiek i nie rozmiar, lecz **stopień, do jakiego coś
doszło**. Ten organ odpowiada na trzy pytania Cezara, każde LICZBĄ Z KODU, nie z prozy:
  1. **PROMPT** — czy specyfikacja, którą pracuję, jest zdrowa (czy nie gnije i nie puchnie)?
  2. **LOOP**   — czy pętle się DOMYKAJĄ, czy tylko otwierają?
  3. **GRAPH**  — czy graf istnieje, czy graf DZIAŁA, i czy wpływa na DECYZJĘ?

POWÓD ISTNIENIA (rozkaz Cezara 2026-08-02: „pilnujmy i weryfikujmy stany prompt/loop/graph,
poziom rozwinięcia, pomiar działania i domknięcia — na otwarciu i zamknięciu"):
Doktryna „domykaj loop, otwieraj drogę na graph" była KRYTERIUM bez MIERNIKA. Wpisanie do
checklisty samego polecenia „zweryfikuj stan" dałoby zasadę bez mechanizmu — dokładnie tę
klasę, którą tego samego dnia złapaliśmy przy kontrakcie append-only (deklarowany w sześciu
organach, egzekwowany przez zero). Krok w checkliście ma WOŁAĆ POMIAR, nie prosić o refleksję.

DLACZEGO TO JEST INGENIUM, A NIE NOWY BYT (Prawo XVI):
`docs/INGENIUM_IQ_IMPERII.md` projektuje CENZORA ROZUMU — 7 kategorii liczonych z kodu.
Projekt istnieje od 2026-07-29 i **nie ma ani linii kodu**. Ten organ jest jego pierwszą
ŻYWĄ kategorią (ósmą w rejestrze: MATURITAS), zbudowaną wg zasad nienaruszalnych stamtąd:
  • każda składowa z KODU albo LEDGERA — zero liczb wpisanych ręcznie,
  • **`NIEZNANE` to wynik** — kategoria bez pomiaru nie dostaje punktów „z rozsądku",
  • **lustro, nie kierownica** — wynik NIGDY nie steruje decyzją handlową ani doborem wag,
  • **antywskaźnik obowiązkowy** — przy każdym piętrze zapisane, JAK można je oszukać,
  • **wynik ma być spadalny** — miernik, który nigdy nie spada, nie mierzy, tylko chwali.

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ Nie liczy jednej „oceny Imperium" — trzy piętra mierzą rozłączne rzeczy i uśrednienie
    ukryłoby to, co najważniejsze (można mieć doskonały LOOP przy zerowym GRAPH).
  • ❌ Nie ocenia wyniku TRADINGOWEGO. Ścieżka decyzyjna handlowa nie zawiera LLM-a, więc
    piętro inżynierii poprawia pamięć i pracę Architekta — mylenie tego z zyskiem byłoby
    tym samym rozkalibrowaniem, które złapaliśmy przy frazach zwiadu.
  • ❌ Nie zgaduje tam, gdzie nie ma danych — brak pomiaru wychodzi jako `NIEZNANE`.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

KORZEN = Path(__file__).resolve().parent.parent.parent
DANE = KORZEN / "bibliotheca_ulpia" / "dane"

NIEZNANE = "NIEZNANE"
POZIOMY = {0: "ZALĄŻEK", 1: "POCZĄTEK", 2: "DZIAŁA", 3: "DOJRZAŁE", 4: "WPIĘTE W DECYZJĘ"}


def _git(*args: str) -> str:
    try:
        p = subprocess.run(["git", *args], cwd=KORZEN, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return ""
    return p.stdout if p.returncode == 0 else ""


def _jsonl(nazwa: str) -> List[dict]:
    plik = DANE / nazwa
    if not plik.exists():
        return []
    out = []
    for linia in plik.open(encoding="utf-8", errors="replace"):
        linia = linia.strip()
        if linia:
            try:
                out.append(json.loads(linia))
            except json.JSONDecodeError:
                continue          # uszkodzony wiersz to nie powód, żeby oślepnąć
    return out


def _poziom(warunki: List[bool]) -> int:
    """Poziom = ile kolejnych progów spełniono OD DOŁU.

    Kolejność jest istotą: piętro nie „przeskakuje" progu. Graf z tysiącem węzłów, którego
    nikt nie czyta przy decyzji, NIE jest dojrzalszy od małego grafu, który decyduje.
    """
    poziom = 0
    for w in warunki:
        if not w:
            break
        poziom += 1
    return poziom


def wiersze_stanu(tekst: str) -> List[tuple]:
    """Wiersze tabel ROADMAP jako `[(etykieta, stan)]` — JEDEN parser na całe Imperium.

    Publiczne, bo pyta o to więcej niż jeden organ: MATURITAS liczy, JAKA CZĘŚĆ pozycji jest
    domknięta, a CONDITOR LUSTRI pyta o KONKRETNE wiersze etapów LUSTRATIO. To jedno źródło
    i dwa pytania — nie dwa parsery. Powód zapisany w Księdze Wad (2026-07-17): „jeden format
    = jeden parser; dwa parsery rozjadą się co do znaku", a rozjazd byłby tu niewidoczny,
    bo obie strony dawałyby liczbę wyglądającą sensownie.
    """
    out: List[tuple] = []
    for w in tekst.splitlines():
        if not w.startswith("|") or w.count("|") < 4:
            continue
        kol = [c.strip() for c in w.split("|")]
        if len(kol) < 4 or not kol[1] or kol[1].startswith("-") or kol[1] == "#":
            continue
        out.append((kol[1], kol[3]))
    return out


def _stan_domkniety(stan: str) -> Optional[bool]:
    """True = domknięte, False = otwarte, **None = nie wiem** (klasa K2: milczenie ≠ zieleń)."""
    if "✅" in stan:
        return True
    if any(z in stan for z in ("🔴", "🟡", "⏸️")):
        return False
    return None


# ── PIĘTRO 1: PROMPT — zdrowie specyfikacji ─────────────────────────────────────

def zmierz_prompt() -> Dict[str, Any]:
    """Czy specyfikacja, wg której pracuję, jest zdrowa: zwięzła, żywa i osiągalna."""
    konstytucja = (KORZEN / "CLAUDE.md")
    linie = len(konstytucja.read_text(encoding="utf-8", errors="replace").splitlines()) \
        if konstytucja.exists() else 0
    skille = sorted((KORZEN / ".claude" / "skills").glob("*/SKILL.md")) \
        if (KORZEN / ".claude" / "skills").exists() else []
    # Sigla MUSZĄ czytać kroki z konstytucji, nie mieć własnej kopii (żelazna zasada).
    try:
        from imperium.biblioteki import sigillarium
        sigla = {n: len(sigillarium.kroki(n)) for n in ("apertio", "clausura", "limes")}
    except Exception:  # noqa: BLE001
        sigla = {}
    puste = [n for n, ile in sigla.items() if ile == 0]

    wskazniki = {
        "CLAUDE.md_linii": linie,
        "limit_doktrynalny": 200,
        "skille_na_zadanie": len(skille),
        "sigla_kroki": sigla,
        "sigla_puste": puste,
    }
    poziom = _poziom([
        linie > 0,                       # 1 — specyfikacja w ogóle istnieje
        bool(sigla) and not puste,       # 2 — procedury są wyzwalane, nie przepisywane
        len(skille) >= 5,                # 3 — rozkazy ładowane na żądanie, nie na starcie
        linie <= 200,                    # 4 — i nie puchnie ponad limit
    ])
    return {
        "pietro": "PROMPT", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki,
        "wask": (f"CLAUDE.md {linie} linii > 200 — dług kontekstu płacony w KAŻDEJ sesji"
                 if linie > 200 else "" ) or ("puste pieczęcie: " + ", ".join(puste) if puste else ""),
        "antywskaznik": "poziom rośnie od PRZENOSZENIA treści do skilli — a przeniesienie "
                        "rozkazu, którego nikt potem nie woła, POGARSZA stan, choć liczbę poprawia",
    }


# ── PIĘTRO 2: LOOP — czy pętle się domykają ─────────────────────────────────────

def zmierz_loop() -> Dict[str, Any]:
    """Nie „ile mamy pętli", tylko **jaka ich część jest DOMKNIĘTA**."""
    # ROADMAP: pozycje otwarte vs domknięte (stan czytany z tabel, nie z pamięci)
    rm = (KORZEN / "docs" / "ROADMAP_IMPERIUM.md")
    tekst = rm.read_text(encoding="utf-8", errors="replace") if rm.exists() else ""
    otw = dom = 0
    for _etykieta, stan in wiersze_stanu(tekst):
        czy = _stan_domkniety(stan)
        if czy is True:
            dom += 1
        elif czy is False:
            otw += 1

    # SUGESTIE: rekord zamknięcia jest OSOBNYM wpisem (ledger append-only), więc liczymy
    # po ostatnim statusie per element — inaczej wyjdzie fałszywy alarm. Zmierzone 2026-08-02:
    # filtr po nazwie statusu `ZAMKNIETA` zamiast `ZAMKNIETE` dał „zero zamkniętych".
    sug: Dict[str, str] = {}
    for r in _jsonl("rejestr_testow.jsonl"):
        if r.get("typ") == "SUGESTIA" and r.get("element"):
            sug[r["element"]] = str(r.get("status", "")).upper()
    zamkniete = sum(1 for s in sug.values()
                    if s.startswith(("ZAMKNIET", "ZREALIZOWAN", "ZABLOKOWAN")))
    otwarte_sug = len(sug) - zamkniete

    wizje = _jsonl("wizje_i_decyzje.jsonl")
    bez_werdyktu = sum(1 for w in wizje if w.get("status") in ("POMYSŁ", "PLANOWANE"))

    # KLASA K1 (naprawiona 2026-08-05): dług liczyliśmy TUTAJ jako `NOTA − CORONA`, czyli
    # drugą arytmetyką obok CODEX NOTARUM. Dwa błędy naraz: (1) odejmowanie LICZNIKÓW nie wie,
    # KTÓRA korona spłaca KTÓRĄ notę (5 koron i 3 niespłacone noty dają fałszywe zero),
    # (2) nie wie o ODROCZENIU wprowadzonym 2026-08-03. Dziś obie drogi dają 0, więc rozjazd
    # był NIEWIDOCZNY — i dokładnie tak wygląda K1, zanim zacznie kłamać. Fakt ma jednego
    # producenta; my go WOŁAMY.
    from imperium.biblioteki import codex_notarum
    dlug_honorowy = len(codex_notarum.dlug_honorowy())
    odroczonych = len(codex_notarum.odroczone())

    hooki = sorted((KORZEN / ".claude" / "hooks").glob("*.sh")) \
        if (KORZEN / ".claude" / "hooks").exists() else []
    # Warstwy liczymy po ZNACZNIKACH `[W..]`, którymi audyt oznacza swoje zarzuty — nie po
    # nazwach funkcji. Zmierzone: `def _warstwa_\d+` daje 15 przy realnych 24, bo część
    # warstw żyje w helperach i pod innymi nazwami. Miara ma liczyć to, co audyt EGZEKWUJE.
    audyt = KORZEN / "narzedzia" / "audyt_spojnosci.py"
    warstwy = len(set(re.findall(r"\[W\d+[a-z]?\]",
                                 audyt.read_text(encoding="utf-8", errors="replace")))) \
        if audyt.exists() else 0

    razem = otw + dom
    domkniecie = round(100 * dom / razem, 1) if razem else None
    wskazniki = {
        "roadmap_domkniete": dom, "roadmap_otwarte": otw,
        "roadmap_domkniecie_proc": domkniecie if domkniecie is not None else NIEZNANE,
        "sugestie_zamkniete": zamkniete, "sugestie_otwarte": otwarte_sug,
        "wizje_bez_werdyktu": bez_werdyktu,
        "hooki": len(hooki), "warstwy_audytu": warstwy,
        "dlug_honorowy": dlug_honorowy,
        # Odroczenie zdejmuje BLOKADĘ, nie dług — więc musi być widoczne obok niego,
        # inaczej stałoby się cichym umorzeniem (klasa K4: wyciszenie bez powodu na widoku).
        "noty_odroczone": odroczonych,
    }
    poziom = _poziom([
        len(hooki) >= 1,                              # 1 — cokolwiek się samo sprawdza
        warstwy >= 10,                                # 2 — bramka ma realny zasięg
        dlug_honorowy == 0,                           # 3 — błędy są spłacane, nie kumulowane
        domkniecie is not None and domkniecie >= 50,  # 4 — DOMYKAMY więcej, niż otwieramy
    ])
    return {
        "pietro": "LOOP", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki,
        "wask": (f"ROADMAP domknięty w {domkniecie}% ({dom}/{razem}) — otwieramy szybciej, "
                 f"niż zamykamy; {otwarte_sug} sugestii i {bez_werdyktu} wizji bez werdyktu"
                 if domkniecie is not None and domkniecie < 50 else ""),
        "antywskaznik": "wskaźnik domknięcia rośnie od USUWANIA pozycji z ROADMAP zamiast ich "
                        "robienia — i od niedopisywania nowych. Spadek po dopisaniu uczciwie "
                        "nazwanego zadania jest ZDROWY, nie zły",
    }


# ── PIĘTRO 3: GRAPH — czy graf istnieje, działa i DECYDUJE ──────────────────────

# Moduły ścieżki DECYZYJNEJ. Graf czytany tutaj znaczy co innego niż graf czytany
# w raporcie startowym — i to rozróżnienie jest całym sensem tego piętra.
SCIEZKA_DECYZJI = ("legatus.py", "brama", "roj_sygnalow.py", "dyrygent.py", "petla_live")


def zmierz_graph() -> Dict[str, Any]:
    """Rozróżnia trzy rzeczy, które łatwo pomylić: graf ISTNIEJE / DZIAŁA / DECYDUJE."""
    czytelnicy = [l for l in _git("grep", "-l", "-E", "graf_pamieci|GrafPamieci").split()
                  if l.endswith(".py")]
    czytelnicy_kodu = [c for c in czytelnicy if not c.startswith("tests/")]
    przy_decyzji = [c for c in czytelnicy_kodu if any(s in c for s in SCIEZKA_DECYZJI)]
    producenci = [l for l in _git("grep", "-l", "krawedzie", "--", "imperium/", "narzedzia/").split()
                  if l.endswith(".py")]

    wezly = krawedzie = NIEZNANE
    try:
        # `_wczytaj` jest prywatne, ale to JEDYNE miejsce podające rozmiar grafu — tak samo
        # czyta go `raport_startowy`. Własne parsowanie pliku byłoby drugim źródłem prawdy
        # o tej samej rzeczy, a to rozjeżdża się przy pierwszej zmianie formatu (Prawo XVI).
        from imperium.biblioteki import graf_pamieci
        stan = graf_pamieci._wczytaj()
        wezly, krawedzie = stan.get("n_wezlow", NIEZNANE), stan.get("n_krawedzi", NIEZNANE)
    except Exception:  # noqa: BLE001
        pass                     # brak odczytu to NIEZNANE, nie zero (Prawo I)

    wskazniki = {
        "wezly": wezly, "krawedzie": krawedzie,
        "czytelnicy_w_kodzie": len(czytelnicy_kodu),
        "czytelnicy_przy_decyzji": len(przy_decyzji),
        "kto_przy_decyzji": przy_decyzji or "NIKT",
        "producenci_krawedzi": len(producenci),
    }
    poziom = _poziom([
        wezly not in (NIEZNANE, 0),      # 1 — graf w ogóle istnieje
        len(czytelnicy_kodu) >= 2,       # 2 — ktoś go czyta (nie tylko sam siebie)
        len(producenci) >= 2,            # 3 — coś go KARMI, więc rośnie
        bool(przy_decyzji),              # 4 — czytany PRZY DECYZJI, nie tylko drukowany
    ])
    return {
        "pietro": "GRAPH", "poziom": poziom, "nazwa": POZIOMY[poziom],
        "wskazniki": wskazniki,
        "wask": ("graf NIE jest czytany przy żadnej decyzji — karmi raport i zapominanie, "
                 "czyli poprawia PAMIĘĆ, nie WYBÓR" if not przy_decyzji else ""),
        "antywskaznik": "poziom rośnie od DOPISYWANIA węzłów, a węzły przybywają same z każdą "
                        "sesją. Rozstrzyga wyłącznie próg 4 (czytany przy decyzji) — reszta "
                        "mierzy rozmiar, nie pożytek",
    }


def zmierz() -> Dict[str, Any]:
    pietra = [zmierz_prompt(), zmierz_loop(), zmierz_graph()]
    return {"pietra": pietra,
            "wask_gardla": [p["wask"] for p in pietra if p["wask"]],
            "poziomy": {p["pietro"]: p["poziom"] for p in pietra}}


# ── MIGAWKI — bo „IQ 137" bez historii jest fikcją (zasada 3 projektu INGENIUM) ──

MIGAWKI = DANE / "maturitas_migawki.jsonl"


def zapisz_migawke(w: Optional[Dict[str, Any]] = None, sciezka: Path = MIGAWKI) -> Dict[str, Any]:
    """Dopisuje migawkę poziomów (append-only — VINDEX tego pilnuje).

    Zapisujemy WYŁĄCZNIE poziomy i garść liczb, nie cały raport: migawka ma służyć
    porównaniu, a nie być drugą kopią stanu, która zaraz rozjedzie się z kodem.
    """
    from datetime import date
    w = w or zmierz()
    wpis = {"data": date.today().isoformat(), "poziomy": w["poziomy"],
            "wask_gardla": len(w["wask_gardla"]),
            "loop": {k: v for k, v in w["pietra"][1]["wskazniki"].items()
                     if k in ("roadmap_domkniecie_proc", "sugestie_otwarte",
                              "wizje_bez_werdyktu", "dlug_honorowy")}}
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False, sort_keys=True) + "\n")
    return wpis


def delta(w: Optional[Dict[str, Any]] = None, sciezka: Path = MIGAWKI) -> Dict[str, Any]:
    """Różnica wobec OSTATNIEJ migawki. Brak historii to `NIEZNANE`, nie „bez zmian".

    Rozróżnienie jest istotne: „bez zmian" twierdzi, że porównaliśmy i wyszło zero.
    Przy pierwszym biegu nie porównaliśmy niczego — i tak ma to być powiedziane.
    """
    w = w or zmierz()
    if not sciezka.exists():
        return {"stan": NIEZNANE, "powod": "brak historii — to pierwsza migawka"}
    poprzednie = [json.loads(l) for l in sciezka.open(encoding="utf-8") if l.strip()]
    if not poprzednie:
        return {"stan": NIEZNANE, "powod": "brak historii — to pierwsza migawka"}
    ost = poprzednie[-1]
    zmiany = {p: w["poziomy"][p] - ost["poziomy"].get(p, 0)
              for p in w["poziomy"] if w["poziomy"][p] != ost["poziomy"].get(p, 0)}
    return {"stan": "zmiana" if zmiany else "bez zmian", "od": ost.get("data"),
            "zmiany_poziomow": zmiany, "poprzednie": ost["poziomy"], "obecne": w["poziomy"]}


def raport(w: Optional[Dict[str, Any]] = None) -> str:
    w = w or zmierz()
    linie = ["📐 MATURITAS — piętro inżynierii Imperium (lustro, nie kierownica):"]
    for p in w["pietra"]:
        pasek = "█" * p["poziom"] + "·" * (4 - p["poziom"])
        linie.append(f"   {p['pietro']:<6} [{pasek}] {p['poziom']}/4 {p['nazwa']}")
        for k, v in p["wskazniki"].items():
            linie.append(f"      · {k}: {v}")
        if p["wask"]:
            linie.append(f"      ⚠️ WĄSKIE GARDŁO: {p['wask']}")
    if not w["wask_gardla"]:
        linie.append("   ✅ żadne piętro nie zgłasza wąskiego gardła")
    linie.append("   ℹ️ Goodhart: ten wynik NIE steruje decyzją handlową ani wagami. "
                 "Podnosi się go wyłącznie naprawą tego, co mierzy (`--antywskazniki`).")
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import sys

    ap = argparse.ArgumentParser(
        description="MATURITAS — na którym piętrze inżynierii stoi Imperium")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--antywskazniki", action="store_true",
                    help="jak można oszukać każde piętro (obowiązek z projektu INGENIUM)")
    ap.add_argument("--zwiezle", action="store_true", help="same poziomy, bez wskaźników")
    ap.add_argument("--zapisz", action="store_true", help="dopisz migawkę poziomów (append-only)")
    ap.add_argument("--delta", action="store_true", help="różnica wobec ostatniej migawki")
    args = ap.parse_args()

    wynik = zmierz()
    if args.delta:
        d = delta(wynik)
        print(f"📐 MATURITAS Δ: {d['stan']}" + (f" (od {d['od']})" if d.get("od") else ""))
        if d.get("powod"):
            print(f"   ℹ️ {d['powod']}")
        for p, z in (d.get("zmiany_poziomow") or {}).items():
            print(f"   {'📈' if z > 0 else '📉'} {p}: {d['poprzednie'][p]} → {d['obecne'][p]}")
        if d["stan"] == "bez zmian":
            print(f"   poziomy: {d['obecne']}")
        sys.exit(0)
    if args.zapisz:
        print(f"📐 MATURITAS — migawka zapisana: {zapisz_migawke(wynik)}")
        sys.exit(0)
    if args.antywskazniki:
        print("📐 MATURITAS — jak można oszukać każde piętro (czytaj PRZED chwaleniem się):")
        for p in wynik["pietra"]:
            print(f"\n   {p['pietro']}: {p['antywskaznik']}")
    elif args.json:
        print(json.dumps(wynik, ensure_ascii=False, indent=2))
    elif args.zwiezle:
        print("📐 MATURITAS: " + " | ".join(
            f"{p['pietro']} {p['poziom']}/4 {p['nazwa']}" for p in wynik["pietra"]))
        for g in wynik["wask_gardla"]:
            print(f"   ⚠️ {g}")
    else:
        print(raport(wynik))
    sys.exit(0)
