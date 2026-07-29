"""
🔨 FABER — Kowal Imperium: odnajduje zewnętrzne narzędzia i głośno melduje ich brak.

Rzymski *faber* to rzemieślnik legionu (fabri pod praefectus fabrum) — ten, który dbał,
by narzędzia BYŁY POD RĘKĄ, zanim zaczęto budowę. Ten organ robi to samo dla binariów,
których Imperium nie ma w Pythonie: `ebook-convert`/`ebook-meta` (calibre), `djvutxt`
(djvulibre), `tesseract` (OCR).

PROBLEM ZMIERZONY (2026-07-28, otwarcie wachty): `shutil.which("ebook-convert")` → None,
`shutil.which("tesseract")` → None, choć OBA są zainstalowane (`C:\\Calibre Portable\\Calibre`,
`C:\\Program Files\\Tesseract-OCR`) — po prostu nie ma ich w PATH sesji. Potok ekstrakcji
traktował to jako „abstynencję, nie błąd" i zwracał pusty tekst, więc **11 pozycji djvu
wypadłoby po cichu z RAG** (w tym trzy rekordy odzyskane 2026-07-28: BIB-128/159/189).
To dokładnie klasa MILCZENIE UDAJĄCE WYNIK — cisza wyglądała jak sukces.

LEKARSTWO (dwa ruchy, oba konieczne):
  1. ZNAJDŹ — `sciezka()` szuka najpierw w PATH (`shutil.which`), a gdy nie ma, w ZNANYCH
     miejscach instalacji per platforma + katalogach z `IMPERIUM_NARZEDZIA_PATH`. Kod nie
     zgaduje: sprawdza, czy plik ISTNIEJE i jest wykonywalny.
  2. KRZYCZ — `BrakNarzedzia` + `alarmy()`. Brak narzędzia, którego wymagają POSIADANE
     formaty, jest ALARMEM (Prawo XV: utrata potencjału), nie ciszą.

GRANICA (Prawo XVI — nie dublujemy):
  • CENSOR SPRZĘTU (imperium/oczy) = ŻELAZO (CPU/RAM/GPU).
  • PORTITOR (imperium/pretorianie) = PAKIETY PYTHONA + klucze API + świeżość danych.
  • FABER = BINARIA SPOZA PYTHONA. Żaden z tamtych ich nie widział — stąd cicha strata.

Uruchom:  python -m imperium.fundament.faber              # pełny raport
          python -m imperium.fundament.faber banner       # 1 linijka (hook / potok)
          python -m imperium.fundament.faber migawka      # JSON
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent

# Katalogi dopisywane przez Cezara bez zmiany kodu (os.pathsep-separated) — instalacja
# w nietypowym miejscu nie wymaga wtedy commita (ta sama zasada, co lista pakietów
# PORTITORA generowana z requirements: kod nie trzyma ręcznej prawdy o środowisku).
ENV_KATALOGI = "IMPERIUM_NARZEDZIA_PATH"


class BrakNarzedzia(RuntimeError):
    """Brak binarki potrzebnej do ekstrakcji — wyjątek GŁOŚNY, świadomie nie ''.

    Pusty string był nierozróżnialny od „książka bez tekstu", więc potok mówił
    „scache'owano 197/208" i nie umiał powiedzieć, że 11 z tych porażek to nie wina
    książek, tylko brakującego narzędzia.
    """


# ── KATALOG NARZĘDZI (nazwa → gdzie szukać, po co, czy krytyczne) ────────────
# `krytyczne=True` → brak przy POSIADANYCH formatach podnosi alarm (Prawo XV).
# djvutxt świadomie NIE jest krytyczny: zmierzone 3× w wachcie biblio28 — calibre
# czyta .djvu samodzielnie (BIB-128/159/189), djvutxt jest tylko szybszą ścieżką.
NARZEDZIA: Dict[str, Dict[str, Any]] = {
    "ebook-convert": {
        "pakiet": "calibre",
        "rola": "uniwersalny konwerter (djvu/azw3/mobi/epub → txt) — fallback ekstraktora",
        "formaty": {".djvu", ".azw3", ".mobi", ".epub"},
        "krytyczne": True,
        "katalogi_win": [
            r"C:\Calibre Portable\Calibre",
            r"C:\Program Files\Calibre2",
            r"C:\Program Files (x86)\Calibre2",
            r"C:\Program Files\Calibre",
        ],
        "katalogi_posix": ["/usr/bin", "/usr/local/bin", "/opt/calibre", "/snap/bin"],
    },
    "ebook-meta": {
        "pakiet": "calibre",
        "rola": "metadane książek (autor/tytuł/tagi) dla katalogu — wzbogacenie",
        "formaty": set(),
        "krytyczne": False,
        "katalogi_win": [
            r"C:\Calibre Portable\Calibre",
            r"C:\Program Files\Calibre2",
            r"C:\Program Files (x86)\Calibre2",
            r"C:\Program Files\Calibre",
        ],
        "katalogi_posix": ["/usr/bin", "/usr/local/bin", "/opt/calibre", "/snap/bin"],
    },
    "djvutxt": {
        "pakiet": "djvulibre",
        "rola": "szybka warstwa tekstowa z .djvu (calibre umie to samo, wolniej)",
        "formaty": {".djvu"},
        "krytyczne": False,
        "katalogi_win": [
            r"C:\Program Files (x86)\DjVuLibre",
            r"C:\Program Files\DjVuLibre",
        ],
        "katalogi_posix": ["/usr/bin", "/usr/local/bin", "/opt/homebrew/bin"],
    },
    "tesseract": {
        "pakiet": "tesseract-ocr",
        "rola": "OCR skanów bez warstwy tekstowej (zmierzone: 5.2 s/stronę na PEDES)",
        "formaty": {".pdf"},
        "krytyczne": False,
        "katalogi_win": [
            r"C:\Program Files\Tesseract-OCR",
            r"C:\Program Files (x86)\Tesseract-OCR",
        ],
        "katalogi_posix": ["/usr/bin", "/usr/local/bin", "/opt/homebrew/bin"],
    },
}

_CACHE: Dict[str, Optional[str]] = {}


def wyczysc_cache() -> None:
    """Zapomina wyniki wyszukiwania (po zmianie PATH/env — używane też w testach)."""
    _CACHE.clear()


def _katalogi_env() -> List[Path]:
    """Katalogi z IMPERIUM_NARZEDZIA_PATH (os.pathsep). Puste wpisy pomijamy."""
    surowe = os.environ.get(ENV_KATALOGI, "")
    return [Path(k) for k in surowe.split(os.pathsep) if k.strip()]


def _kandydaci(nazwa: str) -> List[Path]:
    """Znane miejsca instalacji dla tej platformy + katalogi z env (env ma pierwszeństwo)."""
    spec = NARZEDZIA.get(nazwa, {})
    klucz = "katalogi_win" if os.name == "nt" else "katalogi_posix"
    return _katalogi_env() + [Path(k) for k in spec.get(klucz, [])]


def _w_katalogu(katalog: Path, nazwa: str) -> Optional[Path]:
    """Plik wykonywalny `nazwa` w tym katalogu (Windows: także .exe/.bat/.cmd)."""
    if not katalog.is_dir():
        return None
    warianty = [nazwa]
    if os.name == "nt":
        # PATHEXT bywa okrojony w środowiskach CI/hooków — nie polegamy na nim ślepo.
        rozszerzenia = os.environ.get("PATHEXT", ".EXE;.BAT;.CMD").split(os.pathsep)
        warianty += [nazwa + r.lower() for r in rozszerzenia if r.strip()]
    for w in warianty:
        p = katalog / w
        if p.is_file():
            return p
    return None


def sciezka(nazwa: str, odswiez: bool = False) -> Optional[Path]:
    """
    Pełna ścieżka do binarki albo None. PATH ma pierwszeństwo (uszanuj to, co Cezar ustawił),
    potem znane miejsca instalacji. Wynik cache'owany — `buduj_cache` woła to 208 razy.
    """
    if not odswiez and nazwa in _CACHE:
        z_cache = _CACHE[nazwa]
        return Path(z_cache) if z_cache else None
    znaleziona = shutil.which(nazwa)
    trafienie = Path(znaleziona) if znaleziona else None
    if trafienie is None:
        for katalog in _kandydaci(nazwa):
            trafienie = _w_katalogu(katalog, nazwa)
            if trafienie is not None:
                break
    _CACHE[nazwa] = str(trafienie) if trafienie else None
    return trafienie


def wymagaj(nazwa: str) -> Path:
    """Ścieżka do narzędzia albo GŁOŚNY BrakNarzedzia z instrukcją naprawy (nigdy ciche '')."""
    p = sciezka(nazwa)
    if p is None:
        spec = NARZEDZIA.get(nazwa, {})
        raise BrakNarzedzia(
            f"brak narzędzia `{nazwa}` (pakiet: {spec.get('pakiet', '?')}) — {spec.get('rola', '')}. "
            f"Zainstaluj albo wskaż katalog przez {ENV_KATALOGI}."
        )
    return p


def zapewnij_path(nazwy: Optional[List[str]] = None) -> Dict[str, Optional[str]]:
    """
    Dopisuje katalogi ZNALEZIONYCH narzędzi na POCZĄTEK PATH procesu i zwraca {nazwa: ścieżka}.

    Po co, skoro `sciezka()` daje pełną ścieżkę? Bo narzędzia wołają swoje własne pomocnicze
    binaria (calibre uruchamia podprocesy ze swojego katalogu), a część potoku i tak sięga
    po gołą nazwę. Idempotentne: katalog już obecny w PATH nie jest dopisywany drugi raz —
    inaczej wielokrotne wywołanie w jednym biegu rozdymałoby zmienną bez końca.
    """
    wynik: Dict[str, Optional[str]] = {}
    for nazwa in (nazwy if nazwy is not None else list(NARZEDZIA)):
        p = sciezka(nazwa)
        wynik[nazwa] = str(p) if p else None
        if p is None:
            continue
        katalog = str(p.parent)
        obecne = os.environ.get("PATH", "").split(os.pathsep)
        if katalog not in obecne:
            os.environ["PATH"] = katalog + os.pathsep + os.environ.get("PATH", "")
    return wynik


# ── RAPORTY I ALARMY (Prawo XV — brak narzędzia to utrata potencjału) ────────
def formaty_w_katalogu(katalog: Path) -> Dict[str, int]:
    """Ile plików którego rozszerzenia leży w katalogu (pomiar, nie założenie)."""
    liczby: Dict[str, int] = {}
    if not katalog.is_dir():
        return liczby
    for p in katalog.iterdir():
        if p.is_file():
            liczby[p.suffix.lower()] = liczby.get(p.suffix.lower(), 0) + 1
    return liczby


def migawka(katalog_ksiag: Optional[Path] = None) -> Dict[str, Any]:
    """Żywy stan narzędzi + (opcjonalnie) formaty, których realnie dotyczy brak."""
    formaty = formaty_w_katalogu(katalog_ksiag) if katalog_ksiag else {}
    narzedzia = []
    for nazwa, spec in NARZEDZIA.items():
        p = sciezka(nazwa)
        dotkniete = sum(formaty.get(f, 0) for f in spec["formaty"]) if formaty else None
        narzedzia.append({
            "nazwa": nazwa,
            "pakiet": spec["pakiet"],
            "rola": spec["rola"],
            "sciezka": str(p) if p else None,
            "obecne": p is not None,
            "krytyczne": spec["krytyczne"],
            "formaty": sorted(spec["formaty"]),
            "dotkniete_pliki": dotkniete,
        })
    return {"narzedzia": narzedzia, "formaty_w_katalogu": formaty,
            "katalog": str(katalog_ksiag) if katalog_ksiag else None}


def alarmy(katalog_ksiag: Optional[Path] = None) -> List[str]:
    """
    Alarmy Prawa XV. Alarmujemy tylko o brakach, które REALNIE coś kosztują:
    narzędzie krytyczne + istnieją pliki w formatach, których dotyczy. Brak narzędzia
    dla formatu, którego nie mamy, byłby hałasem — a hałas uczy ignorować alarmy.
    """
    mig = migawka(katalog_ksiag)
    out: List[str] = []
    for n in mig["narzedzia"]:
        if n["obecne"]:
            continue
        dotkniete = n["dotkniete_pliki"]
        if not n["krytyczne"]:
            continue
        if dotkniete is not None and dotkniete == 0:
            continue
        ile = f"{dotkniete} plików" if dotkniete else "pliki"
        out.append(
            f"🚨 BRAK `{n['nazwa']}` ({n['pakiet']}) — {ile} w formatach "
            f"{', '.join(n['formaty'])} NIE wejdzie do RAG (Prawo XV). {n['rola']}."
        )
    return out


def banner(katalog_ksiag: Optional[Path] = None) -> str:
    """Zwięzła linijka do potoku/hooka + alarmy pod spodem (tylko gdy są)."""
    mig = migawka(katalog_ksiag)
    czesci = [f"{n['nazwa']}{'✓' if n['obecne'] else '✗'}" for n in mig["narzedzia"]]
    linie = [f"🔨 FABER: {' '.join(czesci)}"]
    linie += [f"   {a}" for a in alarmy(katalog_ksiag)]
    return "\n".join(linie)


def raport(katalog_ksiag: Optional[Path] = None) -> str:
    """Pełny raport — co znalezione, gdzie, i co kosztuje brak."""
    mig = migawka(katalog_ksiag)
    linie = ["🔨 FABER — Kowal Imperium: narzędzia zewnętrzne (poza Pythonem)", ""]
    for n in mig["narzedzia"]:
        znak = "✅" if n["obecne"] else ("🚨" if n["krytyczne"] else "⚪")
        linie.append(f"   {znak} {n['nazwa']} ({n['pakiet']}): {n['sciezka'] or 'BRAK'}")
        linie.append(f"        {n['rola']}")
        if n["dotkniete_pliki"] is not None and n["formaty"]:
            linie.append(f"        dotyczy {n['dotkniete_pliki']} plików "
                         f"({', '.join(n['formaty'])})")
    a = alarmy(katalog_ksiag)
    if a:
        linie += ["", "   ⚡ ALARMY (Prawo XV):"] + [f"   {x}" for x in a]
    else:
        linie += ["", "   ✅ Żaden posiadany format nie jest osierocony przez brak narzędzia."]
    linie += ["", f"   ℹ️ Nietypowa instalacja? wskaż katalogi w {ENV_KATALOGI} "
                  f"(rozdzielane '{os.pathsep}')."]
    return "\n".join(linie)


if __name__ == "__main__":
    import json

    _biblioteka = ROOT / "bibliotheca_ulpia"
    _cmd = sys.argv[1] if len(sys.argv) > 1 else "raport"
    if _cmd == "banner":
        print(banner(_biblioteka))
    elif _cmd == "migawka":
        print(json.dumps(migawka(_biblioteka), indent=2, ensure_ascii=False))
    else:
        print(raport(_biblioteka))
