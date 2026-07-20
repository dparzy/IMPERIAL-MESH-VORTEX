"""
🏛️ PORTITOR — celnik u wrót: pre-flight gotowości środowiska na starcie sesji (Prawo XV/XVII).

Rzymski *portitor* to celnik/strażnik u bram i portów — sprawdzał, co wchodzi, ZANIM
wpuścił. Ten organ robi to samo dla ŚRODOWISKA PRACY Imperium: zanim jakikolwiek neuron
policzy sygnał, PORTITOR sprawdza u wrót sesji, czy „paszporty" są w porządku:

  1. RUNTIME — wersja Pythona + obecność/wersje kluczowych zależności (numpy, TA-Lib, ccxt,
     requests, pandas, openpyxl). Brak krytycznej (numpy/TA-Lib) = Brama ograniczona (Prawo XV).
  2. KLUCZE API — czy zmienne środowiskowe SĄ USTAWIONE (DEEPSEEK_API_KEY, MEXC_API_KEY,
     MEXC_SECRET). Sprawdzana WYŁĄCZNIE OBECNOŚĆ — NIGDY wartość (Bezpieczeństwo NIENARUSZALNE:
     klucze nie trafiają do kodu ani do wydruku). Brak DEEPSEEK = Hyginus/auto-lekcja cichy.
  3. ŚWIEŻOŚĆ DANYCH — wiek najnowszej świecy w lokalnych CSV (informacyjnie; dane backtestu
     bywają celowo historyczne, więc BEZ alarmu — sonda żywego feedu = osobne, sieciowe).
  4. DRYF vs BASELINE — fingerprint środowiska (Python+pakiety) w git; po `git pull` na innej
     maszynie porównanie live↔baseline ujawnia zmianę „pod spodem" (dep zniknął/urósł) — alarm.

GRANICA (Prawo XVI — redundancja mierzona, NIE dublujemy):
  • CENSOR SPRZĘTU (imperium/oczy) = ŻELAZO (CPU/RAM/GPU) + dryf sprzętu. PORTITOR = SOFTWARE.
  • CENZUS ADAPTERÓW / WALIDUJ ZMYSŁY = adaptery na ŻYWYCH danych z sieci (ciężkie, ręczne).
    PORTITOR jest LEKKI i BEZ SIECI — biegnie na KAŻDYM starcie, nie pinguje giełdy.

DOWÓD, NIE ZAŁOŻENIE (Prawo I): mierzy żywe środowisko (importlib.metadata, os.environ,
mtime plików), nie ufa pamięci. Bez zależności zewnętrznych (stdlib) → działa wszędzie.
Non-blocking: raportuje i podnosi alarmy, NIGDY nie wstrzymuje startu (ZASADA WPIĘCIA).

Uruchom:  python -m imperium.pretorianie.portitor            # pełny raport (domyślnie)
          python -m imperium.pretorianie.portitor banner     # zwięzła 1-2 linijka (hook startu)
          python -m imperium.pretorianie.portitor migawka    # surowy JSON środowiska
          python -m imperium.pretorianie.portitor zmiana     # dryf vs baseline (Prawo XV)
          python -m imperium.pretorianie.portitor zatwierdz  # zaakceptuj żywy stan jako baseline
"""

from __future__ import annotations

import os
import platform
from datetime import datetime, timezone
from importlib import metadata, util
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
BAZA_BASELINE = ROOT / "bibliotheca_ulpia" / "dane" / "portitor_baseline.json"
# Powyżej tylu dni od ostatniej świecy dane uznajemy za STARE i mówimy o tym wprost.
# 45 dni: nasze pliki 1H/4H/1D bywają odświeżane co ~miesiąc (norma), a 4-letnia zaległość
# w danych 1m przeszła niezauważona przez wiele sesji — próg musi łapać drugie, nie pierwsze.
PROG_STAROSCI_DNI = 45

# Kluczowe pakiety: (nazwa_importu, nazwa_dystrybucji, krytyczny).
# Krytyczny=True → brak podnosi alarm (pełna moc Bramy). Reszta = informacyjnie (Prawo I:
# testy działają bez zależności; brak to ograniczenie, nie awaria).
PAKIETY = [
    ("numpy", "numpy", True),
    ("talib", "TA-Lib", True),
    ("pandas", "pandas", False),
    ("ccxt", "ccxt", False),
    ("requests", "requests", False),
    ("openpyxl", "openpyxl", False),
]

# Klucze API: (nazwa_env, opis_skutku_braku). SPRAWDZAMY TYLKO OBECNOŚĆ — nigdy wartość.
KLUCZE_API = [
    ("DEEPSEEK_API_KEY", "Hyginus (Bibliotekarz-Zwiadowca) + auto-lekcja cichy bez klucza"),
    ("MEXC_API_KEY", "handel/live na MEXC niedostępny (faza paper — dziś informacyjnie)"),
    ("MEXC_SECRET", "handel/live na MEXC niedostępny (faza paper — dziś informacyjnie)"),
]

# Katalogi danych: interwał → (podkatalog, sufiks_pliku). Źródło prawdy mapowania:
# narzedzia/codex_probationum.DANE_INTERWALY (imperium nie importuje narzedzia — kopia stała).
DANE_INTERWALY = {
    "1m": ("dane/minutowe", "_minute"),
    "1H": ("dane/godzinowe", "_1h"),
    "4H": ("dane/4h", "_4h"),
    "1D": ("dane/dzienne", "_d"),
}


# ── POMIAR ŻYWEGO ŚRODOWISKA (Prawo I — mierz, nie zgaduj) ───────────────────
def _wersja_pakietu(import_name: str, dist_name: str) -> Optional[str]:
    """Wersja zainstalowanego pakietu lub None gdy nieobecny. find_spec (bez wykonania
    importu = szybko) potwierdza obecność; metadata.version daje numer bez ładowania modułu."""
    try:
        if util.find_spec(import_name) is None:
            return None
    except (ModuleNotFoundError, ValueError, ImportError):
        return None
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return "?"          # zaimportowalny, ale bez metadanych dystrybucji (np. lokalny)


def _zaleznosci() -> List[Dict[str, Any]]:
    """Lista {nazwa, wersja, krytyczny, obecny} dla kluczowych pakietów."""
    out = []
    for imp, dist, kryt in PAKIETY:
        w = _wersja_pakietu(imp, dist)
        out.append({"nazwa": dist, "import": imp, "wersja": w,
                    "krytyczny": kryt, "obecny": w is not None})
    return out


def _klucze_api() -> List[Dict[str, Any]]:
    """Lista {nazwa, obecny, skutek} — WYŁĄCZNIE obecność env (Bezpieczeństwo: bez wartości)."""
    out = []
    for nazwa, skutek in KLUCZE_API:
        obecny = bool(os.environ.get(nazwa, "").strip())
        out.append({"nazwa": nazwa, "obecny": obecny, "skutek": skutek})
    return out


def _swiezosc_danych() -> List[Dict[str, Any]]:
    """Najnowsza świeca per interwał z lokalnych CSV (informacyjnie, bez sieci).

    Pliki Binance_*.csv są malejące (najnowszy bar w 1. wierszu danych: linia URL, nagłówek,
    potem dane). Czytamy tylko pierwszy wiersz danych każdego pliku i bierzemy maksimum —
    najświeższą świecę w danym interwale. Wiek liczony vs teraz (UTC)."""
    teraz = datetime.now(timezone.utc)
    out = []
    for interw, (podkat, suf) in DANE_INTERWALY.items():
        d = ROOT / podkat
        if not d.is_dir():
            continue
        najnowszy = ""
        for plik in d.glob(f"Binance_*{suf}.csv"):
            try:
                with open(plik, encoding="utf-8", errors="replace") as fh:
                    fh.readline()                 # linia URL
                    fh.readline()                 # nagłówek kolumn
                    pierwsza = fh.readline()      # najnowszy bar
                if not pierwsza.strip():
                    continue
                ts = pierwsza.split(",")[1].strip()
                if ts > najnowszy:
                    najnowszy = ts
            except (OSError, IndexError):
                continue
        if not najnowszy:
            continue
        wiek_dni = None
        try:
            # format Binance: "YYYY-MM-DD HH:MM:SS" (bez strefy → traktuj jako UTC)
            dt = datetime.fromisoformat(najnowszy.split("+")[0].strip())
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            wiek_dni = round((teraz - dt).total_seconds() / 86400.0, 1)
        except (ValueError, IndexError):
            pass
        out.append({"interwal": interw, "najnowsza": najnowszy, "wiek_dni": wiek_dni})
    return out


def migawka_srodowiska() -> Dict[str, Any]:
    """Pełna migawka żywego środowiska — jedno źródło prawdy o gotowości u wrót."""
    return {
        "python": platform.python_version(),
        "platforma": f"{platform.system()} {platform.release()}".strip(),
        "zaleznosci": _zaleznosci(),
        "klucze_api": _klucze_api(),
        "dane": _swiezosc_danych(),
        "znacznik": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


# ── ALARMY (Prawo XV — brak = utrata potencjału) ─────────────────────────────
def _alarmy(mig: Dict[str, Any]) -> List[str]:
    """Actionable alarmy: krytyczna zależność brak, klucz DEEPSEEK brak. Świeżość danych i
    klucze MEXC = informacyjne (nie alarm — faza paper / dane historyczne)."""
    alarmy: List[str] = []
    for z in mig["zaleznosci"]:
        if z["krytyczny"] and not z["obecny"]:
            alarmy.append(
                f"⚠️ Brak KRYTYCZNEJ zależności {z['nazwa']} — Brama/rój działają w trybie "
                f"ograniczonym (Prawo XV). Instaluj: pip install {z['nazwa']}."
            )
    for k in mig["klucze_api"]:
        if k["nazwa"] == "DEEPSEEK_API_KEY" and not k["obecny"]:
            alarmy.append(f"⚠️ Brak {k['nazwa']} — {k['skutek']}.")
    return alarmy


def _fingerprint(mig: Dict[str, Any]) -> Dict[str, Any]:
    """Odcisk środowiska do porównań dryfu (Python + wersje pakietów). Klucze/świeżość NIE
    wchodzą — zmieniają się z natury; dryf dotyczy STAŁEJ warstwy runtime."""
    return {
        "python": mig["python"],
        "pakiety": {z["nazwa"]: z["wersja"] for z in mig["zaleznosci"]},
    }


# ── BASELINE + WYKRYWANIE DRYFU (Prawo XV — jak CENSOR sprzętu) ───────────────
def wczytaj_baseline() -> Optional[Dict[str, Any]]:
    """Ostatnio zatwierdzony fingerprint (None = pierwszy pre-flight na tej gałęzi)."""
    if not BAZA_BASELINE.exists():
        return None
    try:
        import json
        return json.loads(BAZA_BASELINE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def zapisz_baseline(fp: Dict[str, Any]) -> None:
    """Zapisuje fingerprint jako nowy baseline (wersjonowany w git — most maszyn)."""
    import json
    BAZA_BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BAZA_BASELINE.write_text(
        json.dumps(fp, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _dryf_pol(base: Dict[str, Any], live: Dict[str, Any]) -> List[str]:
    """Czytelne różnice fingerprintu (Python + pakiety) vs baseline."""
    zmiany: List[str] = []
    if base.get("python") != live.get("python"):
        zmiany.append(f"Python: {base.get('python')} → {live.get('python')}")
    pb, pl = base.get("pakiety", {}), live.get("pakiety", {})
    for nazwa in sorted(set(pb) | set(pl)):
        wb, wl = pb.get(nazwa), pl.get(nazwa)
        if wb != wl:
            zmiany.append(f"{nazwa}: {wb or 'brak'} → {wl or 'brak'}")
    return zmiany


def wykryj_dryf() -> Dict[str, Any]:
    """Porównuje żywy fingerprint z baseline. Read-only: NIE nadpisuje (akceptacja to jawny
    `zatwierdz`), żeby dryf był widoczny na każdym starcie aż Cezar go zatwierdzi."""
    mig = migawka_srodowiska()
    live_fp = _fingerprint(mig)
    base = wczytaj_baseline()
    if base is None:
        return {"pierwszy": True, "zmiany": [], "live_fp": live_fp, "mig": mig}
    return {"pierwszy": False, "zmiany": _dryf_pol(base, live_fp),
            "live_fp": live_fp, "mig": mig}


# ── RAPORTY ──────────────────────────────────────────────────────────────────
def banner() -> str:
    """ZWIĘZŁA 1-3 linijka do hooka startu (świadomie krótka — nie rozdymamy startu, L7).
    Pełnia przez `raport`. Alarmy pokazywane tylko gdy są."""
    mig = migawka_srodowiska()
    alarmy = _alarmy(mig)
    dryf = wykryj_dryf()
    deps_ok = sum(1 for z in mig["zaleznosci"] if z["obecny"])
    deps_all = len(mig["zaleznosci"])
    # Grupuj klucze po prefiksie (MEXC_API_KEY + MEXC_SECRET → jedno „MEXC" = AND obu),
    # inaczej banner drukuje „MEXC✗ MEXC✗". Kolejność zachowana (dict od 3.7).
    grupy: Dict[str, bool] = {}
    for k in mig["klucze_api"]:
        g = k["nazwa"].split("_")[0]
        grupy[g] = grupy.get(g, True) and k["obecny"]
    klucze = " ".join(f"{g}{'✓' if ok else '✗'}" for g, ok in grupy.items())
    # Wiek danych z OSTRZEŻENIEM, nie samą liczbą (naprawione 2026-07-20 po własnej pomyłce
    # Architekta): banner drukował „1m:1453.5d", co miało znaczyć „najświeższa świeca ma 1453
    # DNI", a zostało odczytane jako „mamy 1453 dni historii" — czyli ostrzeżenie wzięto za
    # zaletę i zbudowano agregację 5m/15m na danych sprzed 4 lat. Miernik mówił prawdę, ale
    # nie krzyczał. Od teraz stary wiek dostaje ⚠️ i słowo „STARE".
    def _wiek(d):
        w = d["wiek_dni"]
        return f"{d['interwal']}:{w}d" + (" ⚠️STARE" if w is not None and w > PROG_STAROSCI_DNI else "")

    dane = " ".join(_wiek(d) for d in mig["dane"] if d["wiek_dni"] is not None)
    linie = [f"🏛️ PORTITOR: Python {mig['python']} | deps {deps_ok}/{deps_all} | "
             f"klucze {klucze}" + (f" | dane {dane}" if dane else "")]
    if not dryf["pierwszy"] and dryf["zmiany"]:
        linie.append(f"   📐 dryf środowiska vs baseline: {'; '.join(dryf['zmiany'])}")
    for a in alarmy:
        linie.append(f"   {a}")
    return "\n".join(linie)


def raport() -> str:
    """Pełny raport PORTITORA — runtime, klucze, dane, dryf, alarmy."""
    dryf = wykryj_dryf()
    mig = dryf["mig"]
    linie = [
        "🏛️ PORTITOR — celnik u wrót: pre-flight środowiska (Prawo XV/XVII)",
        "",
        f"   Python: {mig['python']}   Platforma: {mig['platforma']}",
        "",
        "   📦 Zależności:",
    ]
    for z in mig["zaleznosci"]:
        znak = "✅" if z["obecny"] else ("🚨" if z["krytyczny"] else "⚪")
        kryt = " (KRYTYCZNA)" if z["krytyczny"] else ""
        linie.append(f"   {znak} {z['nazwa']}{kryt}: {z['wersja'] or 'BRAK'}")
    linie += ["", "   🔑 Klucze API (tylko obecność — nigdy wartość):"]
    for k in mig["klucze_api"]:
        znak = "✅" if k["obecny"] else "⚪"
        linie.append(f"   {znak} {k['nazwa']}: {'ustawiony' if k['obecny'] else 'brak — ' + k['skutek']}")
    if mig["dane"]:
        linie += ["", "   🕰️ Świeżość danych lokalnych (informacyjnie):"]
        for d in mig["dane"]:
            wiek = f"{d['wiek_dni']} dni" if d["wiek_dni"] is not None else "?"
            linie.append(f"   • {d['interwal']}: najnowsza {d['najnowsza']} (wiek {wiek})")
    if dryf["pierwszy"]:
        linie += ["", "   ℹ️ Pierwszy pre-flight na tej gałęzi — zapisz baseline: "
                  "`python -m imperium.pretorianie.portitor zatwierdz`"]
    elif dryf["zmiany"]:
        linie += ["", "   📐 DRYF środowiska vs baseline:"]
        linie += [f"   • {z}" for z in dryf["zmiany"]]
        linie += ["", "   (zaakceptuj: `python -m imperium.pretorianie.portitor zatwierdz`)"]
    else:
        linie += ["", "   ✅ Środowisko bez dryfu — fingerprint stabilny."]
    alarmy = _alarmy(mig)
    if alarmy:
        linie += ["", "   ⚡ ALARMY (Prawo XV):"]
        linie += [f"   {a}" for a in alarmy]
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(description="PORTITOR — pre-flight środowiska u wrót sesji (Prawo XV)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("banner", help="Zwięzła 1-3 linijka (hook startu)")
    sub.add_parser("migawka", help="Surowa migawka środowiska (JSON)")
    sub.add_parser("zmiana", help="Wykryj dryf środowiska vs baseline (Prawo XV)")
    sub.add_parser("zatwierdz", help="Zaakceptuj żywy fingerprint jako nowy baseline")
    sub.add_parser("raport", help="Pełny raport (domyślnie)")
    args = p.parse_args()

    if args.cmd == "banner":
        print(banner())
    elif args.cmd == "migawka":
        print(json.dumps(migawka_srodowiska(), indent=2, ensure_ascii=False))
    elif args.cmd == "zmiana":
        print(json.dumps(wykryj_dryf(), indent=2, ensure_ascii=False, default=str))
    elif args.cmd == "zatwierdz":
        fp = _fingerprint(migawka_srodowiska())
        zapisz_baseline(fp)
        print(f"✅ Baseline PORTITORA zatwierdzony ({len(fp['pakiety'])} pakietów, Python {fp['python']}).")
    else:  # raport domyślnie
        print(raport())
