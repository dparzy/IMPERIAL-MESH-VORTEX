"""
🧹 LUSTRUM — obrzęd oczyszczenia KOŃCZĄCY cenzus (CORONA A, spłata noty N-fa723062)

ROZKAZ CEZARA (2026-08-03 wybór korony, 2026-08-04 „najpierw lustrum"):
organ, który mierzy **POŻYTEK** narzędzia i wycofuje etapami — wariant SZEROKI,
czyli wchłaniający strażnika obcych plików (P-04 zamknięte).

═══ PO CO ISTNIEJE ═══
CENSUS ORGANORUM (W17) pyta wyłącznie „czy zameldowany", **nigdy „czy jeszcze
potrzebny"**. Prawo XV robiliśmy RĘCZNIE 2026-07-05 (12 niepodpiętych modułów) —
audyt na rozkaz, nie organ w pętli. LUSTRUM domyka tę pętlę: CENSUS spisuje,
LUSTRUM oczyszcza. W Rzymie *lustrum* był właśnie obrzędem zamykającym cenzus,
więc organ nie stoi OBOK census-u — on go KOŃCZY (Prawo XVI: nie mnożymy bytów).

Jeden organ obsługuje DWA przypadki, bo to ten sam mechanizm:
  • **MODUŁY** — kod, którego nikt już nie potrzebuje,
  • **OBCE PLIKI** — pliki, których nie zadeklarował żaden rejestr.
W obu: znajdź zapomniane → oceń → przesuń etapami → **nigdy nie kasuj sam**.

═══ DLACZEGO WIELE SYGNAŁÓW, A NIE JEDEN (LEX TALARUS — pomiar przed ogłoszeniem) ═══
Pierwsza, „oczywista" wersja miary brzmiała: *kto mnie woła*. ZMIERZONE 2026-08-04
na żywym drzewie: **27 z 260 modułów nie ma ŻADNEGO wołacza — nawet testu**.
Gdyby na tym poprzestać, organ kazałby wycofać 27 narzędzi. Sprawdzenie tej listy
obaliło sygnał w całości: **25/25 zbadanych sierot MA własne wejście CLI
(`__main__`) i jest opisanych w żywych dokumentach** — to nie trupy, tylko
przyrządy uruchamiane RĘCZNIE (`pomiar_*`, `ab_w32*`, `install_hooks`).
Narzędzie wołane z wiersza poleceń z definicji nie ma wołacza w kodzie.
**Fałszywek byłoby 100%.** Stąd pożytek liczymy z PIĘCIU niezależnych świadectw.

═══ ZASADA ANTY-UTRWALANIA (wzorzec W10 ZAPOMINANIE + W7 KUSTOSZ) ═══
LUSTRUM **NIGDY nie kasuje i nie przenosi** — tylko PROPONUJE i prowadzi zegar
karencji. Wyrok wykonuje organ nadrzędny albo Cezar (Prawo XVIII). Dokładnie tak
działa Mądre Zapominanie: W10 decyduje CO, Kustosz W7 to wykonuje. Nic nie ginie
(git + archiwum), rzecz tylko schodzi z gorącej ścieżki. Odwracalne.

═══ ETAPY (zegar w ledgerze, nie w pamięci) ═══
  ⚔️ AKTYWNY        — pożytek ≥ PROG_AKTYWNY, nic nie robimy
  💤 PODEJRZANY     — pożytek poniżej progu; ledger zapisuje DATĘ pierwszego podejrzenia
  ⏳ KARENCJA       — podejrzany nieprzerwanie ≥ KARENCJA_DNI → wniosek do Cezara
  🕯️ HONESTA MISSIO — WYŁĄCZNIE po zatwierdzeniu (rekord w ledgerze); zaszczytne
                       zwolnienie ze służby, nie kasowanie

CLI:
  python -m imperium.pretorianie.lustrum raport
  python -m imperium.pretorianie.lustrum kandydaci --prog 0.40
  python -m imperium.pretorianie.lustrum obce
  python -m imperium.pretorianie.lustrum znacz          # zapisz podejrzenia do ledgera
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

KORZEN = Path(__file__).resolve().parents[2]
LEDGER = KORZEN / "bibliotheca_ulpia" / "dane" / "lustrum.jsonl"

# Katalogi, w których mieszkają organy podlegające cenzusowi (te same co W17).
KATALOGI_ORGANOW = ("imperium", "narzedzia")

# ── WAGI POŻYTKU ────────────────────────────────────────────────────────────────
# Suma = 1.0. Dobrane tak, by ŻADEN pojedynczy sygnał nie wystarczał do skazania,
# bo dokładnie na tym poległa wersja jednosygnałowa (100% fałszywek, pomiar wyżej).
# Wołacz produkcyjny waży najwięcej, ale CLI+dokument razem (0.35) też ratują moduł
# przed podejrzeniem — i tak ma być: przyrząd ręczny jest pełnoprawnym narzędziem.
WAGA_WOLACZ_PROD = 0.40
WAGA_CLI = 0.20
WAGA_DOKUMENT = 0.15
WAGA_LEDGER = 0.15
WAGA_TEST = 0.10

PROG_AKTYWNY = 0.40          # ≥ próg → ⚔️ AKTYWNY
KARENCJA_DNI = 30            # ile dni podejrzenia zanim pójdzie wniosek

STOPNIE = {
    "AKTYWNY": "⚔️",
    "PODEJRZANY": "💤",
    "KARENCJA": "⏳",
    "HONESTA_MISSIO": "🕯️",
}

# ── CZTERY WERDYKTY (rozkaz Cezara 2026-08-04) ──────────────────────────────────
# Stopień mówi „jak długo milczy", werdykt mówi „CO Z TYM ZROBIĆ" — i to drugie jest
# treścią rozkazu: organ ma zgłaszać rzecz ORGANOWI, KTÓRY DECYDUJE, a nie wyrokować.
# LUSTRUM nigdy nie orzeka SCALIĆ samodzielnie: podobieństwo mierzy się korelacją
# (Prawo XVI), a nie ocenia z wyglądu — dlatego kieruje sprawę do przyrządu.
WERDYKTY = {
    "ZOSTAW":   ("✅", "—"),
    "WPIAC":    ("🔌", "Prawo XV / Backlog CODEX"),
    "ZBADAC":   ("🔎", "diagnostyka_korelacji (Prawo XVI)"),
    "ARCHIWUM": ("📦", "Cezar (Prawo XVIII) — wykonanie: archiwum/"),
}

# Pliki, których NIE cenzurujemy jako organy: wejścia pakietów i cache.
_POMIJANE = {"__init__.py"}


# ── ŹRÓDŁA ──────────────────────────────────────────────────────────────────────

def moduly() -> List[Path]:
    """Ścieżki modułów podlegających cenzusowi (posortowane — wynik deterministyczny)."""
    znalezione: List[Path] = []
    for katalog in KATALOGI_ORGANOW:
        baza = KORZEN / katalog
        if not baza.exists():
            continue
        for p in baza.rglob("*.py"):
            if "__pycache__" in p.parts or p.name in _POMIJANE:
                continue
            znalezione.append(p)
    return sorted(znalezione)


def _wczytaj(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _korpus_kodu() -> Dict[Path, str]:
    """Treść WSZYSTKICH plików .py repo raz — inaczej skan jest kwadratowy."""
    korpus: Dict[Path, str] = {}
    for p in KORZEN.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        korpus[p] = _wczytaj(p)
    return korpus


def _korpus_dokumentow() -> str:
    """Treść żywych dokumentów — dowód, że narzędzie jest OSIĄGALNE dla człowieka."""
    baza = KORZEN / "docs"
    if not baza.exists():
        return ""
    return "\n".join(_wczytaj(p) for p in sorted(baza.rglob("*.md")))


def _korpus_ledgera() -> str:
    """Ślad w rejestrze testów — dowód, że narzędzie NAPRAWDĘ biegło i dało wynik."""
    czesci = []
    for nazwa in ("rejestr_testow.jsonl", "codex_notarum.jsonl"):
        p = KORZEN / "bibliotheca_ulpia" / "dane" / nazwa
        if p.exists():
            czesci.append(_wczytaj(p))
    return "\n".join(czesci)


def _wiek_dni(sciezka: Path) -> Optional[int]:
    """Dni od ostatniego commitu dotykającego pliku. None = brak w historii gita."""
    wzgledna = os.path.relpath(sciezka, KORZEN).replace("\\", "/")
    try:
        wynik = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", wzgledna],
            capture_output=True, text=True, timeout=10, cwd=KORZEN,
            encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if wynik.returncode != 0 or not wynik.stdout.strip():
        return None
    try:
        return (date.today() - date.fromisoformat(wynik.stdout.strip())).days
    except ValueError:
        return None


# ── POMIAR POŻYTKU ──────────────────────────────────────────────────────────────

def sygnaly(sciezka: Path, korpus: Optional[Dict[Path, str]] = None,
            dokumenty: Optional[str] = None, ledger: Optional[str] = None) -> Dict[str, Any]:
    """Pięć niezależnych świadectw o module. Żadne samo nie skazuje ani nie uniewinnia."""
    korpus = _korpus_kodu() if korpus is None else korpus
    dokumenty = _korpus_dokumentow() if dokumenty is None else dokumenty
    ledger = _korpus_ledgera() if ledger is None else ledger

    nazwa = sciezka.stem
    wzor = re.compile(rf"\b{re.escape(nazwa)}\b")
    wolacze_prod, wolacze_test = 0, 0
    for p, tresc in korpus.items():
        if p == sciezka or not wzor.search(tresc):
            continue
        # Test liczymy OSOBNO: pokrycie testem to inne świadectwo niż realne użycie.
        # Sklejenie ich dawałoby modułowi martwemu w produkcji, lecz otestowanemu,
        # taki sam wynik jak wpiętemu — a to dwie różne prawdy.
        if "tests" in p.parts or p.name.startswith("test_"):
            wolacze_test += 1
        else:
            wolacze_prod += 1

    tresc_wlasna = _wczytaj(sciezka)
    return {
        "modul": os.path.relpath(sciezka, KORZEN).replace("\\", "/"),
        "wolacze_prod": wolacze_prod,
        "wolacze_test": wolacze_test,
        "cli": "__main__" in tresc_wlasna,
        "w_dokumentach": bool(wzor.search(dokumenty)),
        "w_ledgerze": bool(wzor.search(ledger)),
        "wiek_dni": _wiek_dni(sciezka),
    }


def pozytek(sygn: Dict[str, Any]) -> float:
    """Pożytek w [0,1] — suma ważona pięciu świadectw. Deterministyczna, bez API."""
    wynik = 0.0
    if sygn.get("wolacze_prod", 0) > 0:
        wynik += WAGA_WOLACZ_PROD
    if sygn.get("cli"):
        wynik += WAGA_CLI
    if sygn.get("w_dokumentach"):
        wynik += WAGA_DOKUMENT
    if sygn.get("w_ledgerze"):
        wynik += WAGA_LEDGER
    if sygn.get("wolacze_test", 0) > 0:
        wynik += WAGA_TEST
    return round(wynik, 4)


# ── LEDGER (zegar karencji — append-only, pilnowany przez VINDEXA) ───────────────

def _czytaj_ledger() -> List[Dict[str, Any]]:
    if not LEDGER.exists():
        return []
    rekordy = []
    for linia in _wczytaj(LEDGER).splitlines():
        linia = linia.strip()
        if not linia:
            continue
        try:
            rekordy.append(json.loads(linia))
        except json.JSONDecodeError:
            continue    # uszkodzona linia nie może wywrócić całego zegara
    return rekordy


def _dopisz(rekord: Dict[str, Any]) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rekord, ensure_ascii=False) + "\n")


def historia(modul: str, rekordy: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Ostatni stan modułu w ledgerze: od kiedy podejrzany, czy zwolniony ze służby.

    Ledger jest append-only, więc „stan" to OSTATNI rekord — nie suma rekordów.
    Rekord `AKTYWNY` kasuje zegar: moduł, który wrócił do użycia, zaczyna od zera,
    inaczej karencja naliczałaby się za czasy, gdy narzędzie już znów służyło.
    """
    rekordy = _czytaj_ledger() if rekordy is None else rekordy
    moje = [r for r in rekordy if r.get("modul") == modul]
    if not moje:
        return {"podejrzany_od": None, "zwolniony": False}
    zwolniony = any(r.get("stopien") == "HONESTA_MISSIO" for r in moje)
    podejrzany_od = None
    for r in moje:
        if r.get("stopien") in ("PODEJRZANY", "KARENCJA"):
            podejrzany_od = podejrzany_od or r.get("data")
        elif r.get("stopien") == "AKTYWNY":
            podejrzany_od = None
    return {"podejrzany_od": podejrzany_od, "zwolniony": zwolniony}


def wniosek(sygn: Dict[str, Any], poz: float, prog: float = PROG_AKTYWNY) -> str:
    """CO zrobić z modułem — cztery werdykty Cezara, nie jeden wyrok.

    Kolejność reguł jest istotna. Najpierw łapiemy przypadek **gotowy, otestowany,
    a mimo to nieużywany** — to dosłownie pierwsza pozycja checklisty Prawa XV
    („moduł gotowy, ale niepodpięty do pipeline") i zmierzony fakt z 2026-07-05,
    gdy ręczny audyt znalazł 12 takich. Taki moduł jest MAJĄTKIEM do wpięcia,
    nie kandydatem do archiwum — pomylenie tych dwóch byłoby utratą potencjału.

    Przyrząd z wejściem CLI opisany w dokumentach NIE trafia do archiwum: zmierzone
    2026-08-04, że narzędzie wołane ręcznie z definicji nie ma wołacza w kodzie
    (25/25 sierot miało CLI i wzmiankę w docs). Idzie do ZBADAĆ, czyli do pomiaru.
    """
    if poz >= prog:
        return "ZOSTAW"
    if sygn.get("wolacze_test", 0) > 0 and sygn.get("wolacze_prod", 0) == 0:
        return "WPIAC"
    if sygn.get("cli") or sygn.get("w_dokumentach") or sygn.get("w_ledgerze"):
        return "ZBADAC"
    return "ARCHIWUM"


def stopien(poz: float, hist: Dict[str, Any], dzis: Optional[date] = None) -> str:
    """Etap wycofywania. HONESTA MISSIO nigdy nie nadaje się automatycznie."""
    if hist.get("zwolniony"):
        return "HONESTA_MISSIO"
    if poz >= PROG_AKTYWNY:
        return "AKTYWNY"
    od = hist.get("podejrzany_od")
    if not od:
        return "PODEJRZANY"
    try:
        start = date.fromisoformat(str(od))
    except (ValueError, TypeError):
        return "PODEJRZANY"    # zepsuta data nie może AWANSOWAĆ do karencji
    dzis = dzis or date.today()
    return "KARENCJA" if (dzis - start).days >= KARENCJA_DNI else "PODEJRZANY"


# ── OBCE PLIKI (wchłonięty strażnik, P-04) ──────────────────────────────────────

def obce_pliki() -> List[str]:
    """Pliki leżące w repo, których nie zadeklarował żaden rejestr ani git.

    Świadomie NIE kasujemy i NIE przenosimy — zgodnie z Twoim rozkazem z 2026-07-28
    strażnik ma KIEROWAĆ do wrzutni/kwarantanny, nigdy usuwać. Tu tylko wskazujemy.
    Bierzemy pliki nieśledzone i NIEZIGNOROWANE: coś, co ani nie weszło do historii,
    ani nie zostało świadomie wykluczone, jest z definicji nieopisane.
    """
    try:
        wynik = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            capture_output=True, text=True, timeout=30, cwd=KORZEN,
            encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if wynik.returncode != 0:
        return []
    obce = []
    for linia in wynik.stdout.splitlines():
        if linia.startswith("?? "):
            obce.append(linia[3:].strip().strip('"'))
    return sorted(obce)


# ── RAPORT ──────────────────────────────────────────────────────────────────────

def przeglad(prog: float = PROG_AKTYWNY) -> List[Dict[str, Any]]:
    """Pełen cenzus pożytku — jeden przebieg po korpusie, nie N przebiegów."""
    korpus = _korpus_kodu()
    dokumenty = _korpus_dokumentow()
    ledger_tekst = _korpus_ledgera()
    rekordy = _czytaj_ledger()

    wynik = []
    for p in moduly():
        s = sygnaly(p, korpus, dokumenty, ledger_tekst)
        poz = pozytek(s)
        hist = historia(s["modul"], rekordy)
        st = stopien(poz, hist) if poz < prog or hist.get("zwolniony") else "AKTYWNY"
        wer = wniosek(s, poz, prog)
        ikona_w, decydent = WERDYKTY[wer]
        s.update({"pozytek": poz, "stopien": st, "ikona": STOPNIE[st],
                  "wniosek": wer, "ikona_wniosku": ikona_w, "decyduje": decydent,
                  "podejrzany_od": hist.get("podejrzany_od")})
        wynik.append(s)
    return sorted(wynik, key=lambda r: (r["pozytek"], r["modul"]))


def kandydaci(prog: float = PROG_AKTYWNY) -> List[Dict[str, Any]]:
    """Moduły poniżej progu pożytku — WNIOSKI, nie wyroki."""
    return [r for r in przeglad(prog) if r["stopien"] != "AKTYWNY"]


def znacz(prog: float = PROG_AKTYWNY, dzis: Optional[date] = None) -> Dict[str, Any]:
    """Zapisz do ledgera dzisiejszy stan podejrzeń — to URUCHAMIA zegar karencji.

    Bez tego kroku karencja nigdy nie ruszy: `stopien()` liczy dni od PIERWSZEGO
    zapisanego podejrzenia, a nie od chwili uruchomienia raportu. Rozdzielenie
    „popatrz" (raport) od „zapisz" (znacz) jest celowe — czytanie musi być zawsze
    wolne i bez skutków ubocznych, inaczej organ uczy się go obchodzić.
    """
    dzis = dzis or date.today()
    rekordy = _czytaj_ledger()
    dopisane = 0
    for r in przeglad(prog):
        hist = historia(r["modul"], rekordy)
        if hist.get("zwolniony"):
            continue
        podejrzany = r["pozytek"] < prog
        if podejrzany and not hist.get("podejrzany_od"):
            _dopisz({"data": dzis.isoformat(), "modul": r["modul"],
                     "stopien": "PODEJRZANY", "pozytek": r["pozytek"]})
            dopisane += 1
        elif not podejrzany and hist.get("podejrzany_od"):
            # Moduł wrócił do służby — kasujemy zegar jawnym rekordem, nie ciszą.
            _dopisz({"data": dzis.isoformat(), "modul": r["modul"],
                     "stopien": "AKTYWNY", "pozytek": r["pozytek"]})
            dopisane += 1
    return {"dopisane": dopisane, "ledger": str(LEDGER)}


def raport(prog: float = PROG_AKTYWNY) -> Dict[str, Any]:
    wszystkie = przeglad(prog)
    licznik: Dict[str, int] = {}
    for r in wszystkie:
        licznik[r["stopien"]] = licznik.get(r["stopien"], 0) + 1
    wg_wniosku: Dict[str, int] = {}
    for r in wszystkie:
        wg_wniosku[r["wniosek"]] = wg_wniosku.get(r["wniosek"], 0) + 1
    return {
        "modulow": len(wszystkie),
        "wg_stopnia": licznik,
        "wg_wniosku": wg_wniosku,
        "kandydaci": [r for r in wszystkie if r["stopien"] != "AKTYWNY"],
        "obce_pliki": obce_pliki(),
        "prog": prog,
    }


def raport_tekst(prog: float = PROG_AKTYWNY) -> str:
    r = raport(prog)
    linie = [f"🧹 LUSTRUM — obrzęd oczyszczenia (próg pożytku {prog:.2f}):"]
    czesci = [f"{STOPNIE[k]} {k} {v}" for k, v in sorted(r["wg_stopnia"].items())]
    linie.append(f"   modułów: {r['modulow']} | " + " | ".join(czesci))
    czesci_w = [f"{WERDYKTY[k][0]} {k} {v}" for k, v in sorted(r["wg_wniosku"].items())]
    linie.append("   werdykty: " + " | ".join(czesci_w))
    if r["kandydaci"]:
        linie.append(f"   ⚠️ WNIOSKI (nie wyroki) — {len(r['kandydaci'])}:")
        for k in r["kandydaci"][:15]:
            swiadectwa = []
            if k["wolacze_prod"]:
                swiadectwa.append(f"woła {k['wolacze_prod']}")
            if k["cli"]:
                swiadectwa.append("CLI")
            if k["w_dokumentach"]:
                swiadectwa.append("docs")
            if k["w_ledgerze"]:
                swiadectwa.append("ledger")
            if k["wolacze_test"]:
                swiadectwa.append("test")
            linie.append(f"      {k['ikona']} {k['ikona_wniosku']} {k['wniosek']:<8} "
                         f"{k['modul']}  pożytek {k['pozytek']:.2f}"
                         f"  [{', '.join(swiadectwa) or 'BRAK ŚWIADECTW'}]"
                         f"  → decyduje: {k['decyduje']}")
        if len(r["kandydaci"]) > 15:
            linie.append(f"      … i {len(r['kandydaci']) - 15} więcej")
    else:
        linie.append("   ✅ każdy moduł ma pożytek — nic do wycofania")
    if r["obce_pliki"]:
        linie.append(f"   📦 OBCE PLIKI (do wrzutni/kwarantanny, NIE do kasacji) — "
                     f"{len(r['obce_pliki'])}:")
        for o in r["obce_pliki"][:10]:
            linie.append(f"      • {o}")
    linie.append("   ℹ️ LUSTRUM nigdy nie kasuje ani nie przenosi — wyrok wydaje Cezar.")
    return "\n".join(linie)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="LUSTRUM — pożytek organów i obce pliki")
    ap.add_argument("komenda", choices=["raport", "kandydaci", "obce", "znacz"])
    ap.add_argument("--prog", type=float, default=PROG_AKTYWNY)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    if a.komenda == "raport":
        print(json.dumps(raport(a.prog), ensure_ascii=False, indent=2, default=str)
              if a.json else raport_tekst(a.prog))
    elif a.komenda == "kandydaci":
        k = kandydaci(a.prog)
        if a.json:
            print(json.dumps(k, ensure_ascii=False, indent=2, default=str))
        else:
            for r in k:
                print(f"{r['ikona']} {r['modul']}  pożytek {r['pozytek']:.2f}")
            print(f"razem: {len(k)}")
    elif a.komenda == "obce":
        o = obce_pliki()
        for x in o:
            print(f"📦 {x}")
        print(f"razem: {len(o)} (do wrzutni/kwarantanny, NIE do kasacji)")
    elif a.komenda == "znacz":
        print(json.dumps(znacz(a.prog), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
