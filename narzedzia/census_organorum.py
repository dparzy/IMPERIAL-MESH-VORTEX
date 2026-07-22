#!/usr/bin/env python3
"""CENSUS ORGANORUM — spis wszystkich organów i narzędzi Imperium, GENEROWANY z kodu.

CEL (LEX TALIONIS, CORONA za notę N-9992ba7b): nowy moduł przestaje móc żyć
w ukryciu. Zmierzone 2026-07-20 (zarzut Cezara): `imperium/cesarz/dispensator.py`
(152 linie + 125 linii testów) nie występował w ŻADNYM dokumencie — MANIFEST 0,
INDEKS 0, ARCHITEKTURA 0, README 0 — a audyt mimo to dawał „✅ pełna harmonia".
Powód: strażnik meldunku (Warstwa 11) pilnował WYŁĄCZNIE `imperium/biblioteki/`;
reszta organów i całe `narzedzia/` były poza jego zasięgiem. Łącznie 19 modułów
`imperium/` + 31 narzędzi milczało bezkarnie.

LEKARSTWO — nie „dopisać 50 wpisów ręcznie" (za miesiąc znów skłamią, dokładnie
jak liczby przed Filarem 4), tylko ODEBRAĆ dokumentowi prawo do ręcznego opisu:
spis jest PRZEPISYWANY z żywego kodu (moduł + pierwsza linia docstringu jako rola),
a audyt (Warstwa 17) porównuje plik na dysku z tym, co wygenerowałby kod TERAZ.
Rozjazd = czerwień. Nowy organ bez regeneracji nie przejdzie bramki commita.

To ta sama klasa mechanizmu co Warstwa 15 (liczby wstrzykiwane) i 16 (API-widma),
tylko po stronie ISTNIENIA MODUŁU: tam „liczba musi pochodzić z kodu" i „ścieżka
cytowana w docs musi istnieć", tu — „moduł istniejący w kodzie musi być zameldowany".

Nazwa rzymska (ZASADA NOMENKLATURY): census organorum = „spis organów"; rzymski
cenzus spisywał obywateli, by nikt nie umknął powinnościom — tu żaden moduł nie
umyka meldunkowi.

UŻYCIE:
    python narzedzia/census_organorum.py            # sprawdź (miękko, drukuje różnice)
    python narzedzia/census_organorum.py --zapisz   # przepisz docs/CENSUS_ORGANORUM.md
    python narzedzia/census_organorum.py --twardy   # exit 1 przy rozjeździe (bramka)
"""
from __future__ import annotations

import argparse
import ast
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_s = getattr(sys, "stdout", None)
if _s is not None and hasattr(_s, "reconfigure"):
    try:
        _s.reconfigure(encoding="utf-8")   # type: ignore[union-attr]
    except Exception:  # noqa: BLE001 — brak reconfigure → zostaje domyślne kodowanie
        pass

DOKUMENT = os.path.join(ROOT, "docs", "CENSUS_ORGANORUM.md")

# Korzenie objęte cenzusem. `imperium/` to organy, `narzedzia/` to warsztat —
# oba są kodem Imperium, więc oba muszą się meldować (lekcja: audyt widział 1/11 organów).
KORZENIE = ("imperium", "narzedzia")

# Poza cenzusem — pliki techniczne bez własnej roli do opisania.
POMIJANE_PLIKI = {"__init__.py"}
POMIJANE_KATALOGI = {"__pycache__", ".pytest_cache"}

ZNACZNIK_START = "<!-- CENSUS:start — sekcja generowana, NIE edytuj ręcznie -->"
ZNACZNIK_KONIEC = "<!-- CENSUS:koniec -->"

# Rzymskie imiona organów (katalogów) — ZASADA NOMENKLATURY. Klucz = katalog w kodzie.
ORGANY = {
    "imperium/akwedukty": "AQUAEDUCTUS — przepływ danych (świece, adaptery zewnętrzne)",
    "imperium/biblioteki": "BIBLIOTHECA — pamięć, kroniki, rejestry, uczenie",
    "imperium/cesarz": "CAESAR — rdzeń decyzji (most LLM, refleksja)",
    "imperium/drogi": "VIA — routing i egzekucja zleceń",
    "imperium/fundament": "FUNDAMENTUM — Brama Kalkulatora, narzędzia bazowe",
    "imperium/koloseum": "COLOSSEUM — walidacja, backtest, kontrfaktyki",
    "imperium/legiony": "LEGIONES — neurony, zwiadowcy, strategie, Legatus",
    "imperium/oczy": "OCULI — percepcja (sprzęt, zmysły zewnętrzne)",
    "imperium/pretorianie": "PRAETORIANI — bezpieczniki, weto ryzyka, straż u wrót",
    "imperium/senat": "SENATUS — meta-decyzje, debata",
    "imperium/swiatynie": "TEMPLA — wiedza, mapy, panele, wizualizacje",
    "narzedzia": "OFFICINA — warsztat: pomiary, audyty, generatory, raporty",
}


def _rola_modulu(sciezka: str) -> str:
    """Pierwsza sensowna linia docstringu modułu = jego rola.

    Czytane przez `ast` (bez importu): import wciągnąłby zależności i skutki uboczne,
    a cenzus ma tylko SPISYWAĆ, nie uruchamiać Imperium.
    """
    try:
        with open(sciezka, encoding="utf-8") as f:
            drzewo = ast.parse(f.read())
    except (SyntaxError, UnicodeDecodeError, OSError):
        return "⚠️ nie udało się odczytać docstringu"
    doc = ast.get_docstring(drzewo)
    if not doc:
        return "⚠️ BRAK DOCSTRINGU — moduł nie mówi, po co istnieje"
    for linia in doc.splitlines():
        linia = linia.strip()
        if linia:
            # Pipe rozwaliłby komórkę tabeli Markdown; kropka na końcu jest zbędna.
            return linia.replace("|", "/").rstrip(".")
    return "⚠️ BRAK DOCSTRINGU — moduł nie mówi, po co istnieje"


def spisz_moduly() -> dict[str, list[tuple[str, str]]]:
    """Żywy spis: {katalog: [(nazwa_pliku, rola), ...]} — posortowany deterministycznie."""
    spis: dict[str, list[tuple[str, str]]] = {}
    for korzen in KORZENIE:
        for biezacy, katalogi, pliki in os.walk(os.path.join(ROOT, korzen)):
            katalogi[:] = sorted(k for k in katalogi if k not in POMIJANE_KATALOGI)
            wpisy = []
            for plik in sorted(pliki):
                if not plik.endswith(".py") or plik in POMIJANE_PLIKI:
                    continue
                wpisy.append((plik, _rola_modulu(os.path.join(biezacy, plik))))
            if wpisy:
                wzgledny = os.path.relpath(biezacy, ROOT).replace(os.sep, "/")
                spis[wzgledny] = wpisy
    return dict(sorted(spis.items()))


def _organ_dla(katalog: str) -> str:
    """Rzymskie imię organu dla katalogu (podkatalogi dziedziczą po rodzicu)."""
    najlepszy, wynik = "", "—"
    for prefiks, nazwa in ORGANY.items():
        if (katalog == prefiks or katalog.startswith(prefiks + "/")) and len(prefiks) > len(najlepszy):
            najlepszy, wynik = prefiks, nazwa
    return wynik


def sekcja_md(spis: dict[str, list[tuple[str, str]]] | None = None) -> str:
    """Generuje sekcję spisu (między znacznikami) — czysta funkcja z żywego kodu."""
    spis = spis if spis is not None else spisz_moduly()
    lacznie = sum(len(v) for v in spis.values())
    linie = [
        ZNACZNIK_START,
        "",
        f"**Modułów w cenzusie: {lacznie}** w {len(spis)} katalogach "
        "(generowane z żywego kodu — `python narzedzia/census_organorum.py --zapisz`).",
        "",
    ]
    for katalog, wpisy in spis.items():
        linie.append(f"### `{katalog}/` — {_organ_dla(katalog)}")
        linie.append("")
        linie.append("| Moduł | Rola (docstring modułu) |")
        linie.append("|-------|--------------------------|")
        for nazwa, rola in wpisy:
            linie.append(f"| `{nazwa}` | {rola} |")
        linie.append("")
    linie.append(ZNACZNIK_KONIEC)
    return "\n".join(linie)


def dokument_md(stan_na: str | None = None) -> str:
    """Pełny dokument (nagłówek Tabularium + sekcja generowana)."""
    stan_na = stan_na or date.today().isoformat()
    naglowek = f"""---
kategoria: TABULA
typ: zywy
wlasciciel: narzedzia/census_organorum.py
stan_na: {stan_na}
powod_istnienia: "Spis WSZYSTKICH modulow imperium/ i narzedzia/ generowany z zywego kodu — zadny organ nie moze istniec bez meldunku; bramka Warstwy 17 audytu porownuje ten plik z kodem"
---
# 🏛️ CENSUS ORGANORUM — spis organów i narzędzi Imperium

> **Dokument GENEROWANY.** Nie edytuj ręcznie — treść jest przepisywana z żywego
> kodu przez `narzedzia/census_organorum.py`. Rola każdego modułu to pierwsza linia
> jego docstringu, więc opis nie może rozjechać się z kodem: żeby zmienić opis,
> zmieniasz docstring.
>
> **Po co to istnieje (dla nowicjusza):** wcześniej moduł mógł powstać, działać
> i nigdzie się nie zameldować — `imperium/cesarz/dispensator.py` przeżył tak całą
> sesję, a audyt i tak meldował „pełna harmonia", bo pilnował tylko jednego
> katalogu z jedenastu. Teraz **Warstwa 17** audytu porównuje ten plik z tym, co
> kod wygenerowałby w tej chwili — rozjazd zapala czerwień i blokuje commit.
>
> **Dodałeś moduł?** `python narzedzia/census_organorum.py --zapisz` i commituj
> razem ze zmianą (ZASADA PEŁNEJ SYMBIOZY).

"""
    return naglowek + sekcja_md() + "\n"


def _na_dysku() -> str:
    try:
        with open(DOKUMENT, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _wytnij_sekcje(tekst: str) -> str:
    """Sekcja generowana z dokumentu (bez nagłówka i daty — te wolno zmieniać)."""
    if ZNACZNIK_START not in tekst or ZNACZNIK_KONIEC not in tekst:
        return ""
    poczatek = tekst.index(ZNACZNIK_START)
    koniec = tekst.index(ZNACZNIK_KONIEC) + len(ZNACZNIK_KONIEC)
    return tekst[poczatek:koniec]


def sprawdz() -> list[str]:
    """Zwraca listę rozbieżności między dokumentem a żywym kodem ([] = zgodny).

    Porównywana jest WYŁĄCZNIE sekcja generowana — nagłówek i data należą do
    człowieka. Różnica raportowana modułami (nie diffem tekstu), żeby komunikat
    mówił CO dopisać, a nie „pliki się różnią".
    """
    na_dysku = _na_dysku()
    if not na_dysku:
        return [f"[W17] Brak {os.path.relpath(DOKUMENT, ROOT)} — uruchom: "
                "python narzedzia/census_organorum.py --zapisz"]

    sekcja_dysk = _wytnij_sekcje(na_dysku)
    if not sekcja_dysk:
        return ["[W17] CENSUS_ORGANORUM.md bez znaczników CENSUS:start/koniec — "
                "sekcja generowana zniszczona, odtwórz: --zapisz"]

    zywe = {f"{kat}/{nazwa}" for kat, wpisy in spisz_moduly().items() for nazwa, _ in wpisy}
    spisane = {f"{kat}/{nazwa}" for kat, wpisy in _parsuj_sekcje(sekcja_dysk).items()
               for nazwa, _ in wpisy}

    bledy = []
    niezameldowane = sorted(zywe - spisane)
    widma = sorted(spisane - zywe)
    if niezameldowane:
        bledy.append(f"[W17] Moduły w kodzie BEZ meldunku w CENSUS_ORGANORUM "
                     f"({len(niezameldowane)}): {', '.join(niezameldowane[:8])}"
                     f"{' …' if len(niezameldowane) > 8 else ''} "
                     "→ python narzedzia/census_organorum.py --zapisz")
    if widma:
        bledy.append(f"[W17] Moduły-widma w CENSUS_ORGANORUM (nie ma ich w kodzie, "
                     f"{len(widma)}): {', '.join(widma[:8])}"
                     f"{' …' if len(widma) > 8 else ''} → --zapisz")
    if not bledy and sekcja_dysk.strip() != sekcja_md().strip():
        bledy.append("[W17] CENSUS_ORGANORUM: komplet modułów zgodny, ale opisy ról "
                     "rozjechały się z docstringami → --zapisz")
    return bledy


def _parsuj_sekcje(sekcja: str) -> dict[str, list[tuple[str, str]]]:
    """Odczytuje spis z wygenerowanej sekcji Markdown (odwrotność `sekcja_md`)."""
    spis: dict[str, list[tuple[str, str]]] = {}
    katalog = None
    for linia in sekcja.splitlines():
        linia = linia.strip()
        if linia.startswith("### `"):
            katalog = linia.split("`")[1].rstrip("/")
            spis[katalog] = []
        elif linia.startswith("| `") and katalog is not None:
            czesci = [c.strip() for c in linia.strip("|").split("|")]
            if len(czesci) >= 2:
                spis[katalog].append((czesci[0].strip("`"), czesci[1]))
    return spis


def zapisz() -> int:
    """Przepisuje dokument z żywego kodu. Zwraca liczbę spisanych modułów."""
    tresc = dokument_md()
    os.makedirs(os.path.dirname(DOKUMENT), exist_ok=True)
    with open(DOKUMENT, "w", encoding="utf-8", newline="\n") as f:
        f.write(tresc)
    return sum(len(v) for v in spisz_moduly().values())


def main() -> None:
    ap = argparse.ArgumentParser(description="Census Organorum — spis organów Imperium z żywego kodu")
    ap.add_argument("--zapisz", action="store_true", help="przepisz docs/CENSUS_ORGANORUM.md")
    ap.add_argument("--twardy", action="store_true", help="exit 1 przy rozjeździe (bramka)")
    args = ap.parse_args()

    if args.zapisz:
        print(f"✅ CENSUS ORGANORUM zapisany: {zapisz()} modułów → docs/CENSUS_ORGANORUM.md")
        return

    bledy = sprawdz()
    if bledy:
        print("🔴 CENSUS ORGANORUM — rozjazd z żywym kodem:")
        for b in bledy:
            print(f"   • {b}")
        if args.twardy:
            sys.exit(1)
    else:
        lacznie = sum(len(v) for v in spisz_moduly().values())
        print(f"✅ CENSUS ORGANORUM — {lacznie} modułów, wszystkie zameldowane.")


if __name__ == "__main__":
    main()
