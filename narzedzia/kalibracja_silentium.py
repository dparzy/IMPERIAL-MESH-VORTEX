"""📏 KALIBRACJA SILENTIUM — pomiar klasyfikatora komend na PRAWDZIE PODSTAWOWEJ.

LEX TALARUS: „nowy przyrząd bez testu kalibracyjnego na prawdzie podstawowej nie istnieje".
SILENTIUM ma dwie części o zupełnie różnej wiarygodności i wolno je mierzyć tylko osobno:

  • blokada `Write/Edit` po ŚCIEŻCE — precyzja z konstrukcji (ścieżkę znamy dokładnie),
    nie ma tu czego kalibrować, jest za to test granicy w `tests/test_silentium.py`;
  • klasyfikator KOMEND POWŁOKI — heurystyka, więc **musi mieć zmierzoną cenę pomyłki**.

PRAWDA PODSTAWOWA: realne komendy `Bash`/`PowerShell` z transkryptów tego projektu
(`~/.claude/projects/<repo>/*.jsonl`) — to, co faktycznie było wołane w tym repo, a nie
komendy wymyślone przez autora klasyfikatora pod własny klasyfikator. Etykiety nadaje
Architekt czytając komendę i odpowiadając na JEDNO pytanie:

    „czy wykonanie tego w czystym drzewie może zmienić `git status`?"

Etykiety są WERSJONOWANE (`bibliotheca_ulpia/dane/kalibracja_silentium.json`), więc
`test_silentium_kalibracja` pilnuje, że żadna późniejsza zmiana klasyfikatora nie
pogorszy wyniku po cichu. Korpus bez zapisanych etykiet byłby jednorazową anegdotą.

DLACZEGO PRÓBA WARSTWOWA, A NIE LOSOWA Z CAŁOŚCI:
komend piszących jest w korpusie mniejszość, więc próba losowa zmierzyłaby precyzję na
kilku sztukach i nie powiedziała nic o pomyłkach. Losujemy więc osobno z warstwy
OSKARŻONYCH (klasyfikator mówi „pisze") i z warstwy PRZEPUSZCZONYCH — pierwsza mierzy
FAŁSZYWE ALARMY (koszt: Architekt uczy się obchodzić strażnika), druga PRZECIEKI
(koszt: unieważniony bieg, czyli dokładnie to, przed czym SILENTIUM ma bronić).

Uruchomienie:
    python narzedzia/kalibracja_silentium.py --probka        # wypisz próbkę do etykietowania
    python narzedzia/kalibracja_silentium.py --raport        # metryki wobec zapisanych etykiet
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

KORZEN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KORZEN))

from imperium.pretorianie.silentium import komenda_pisze  # noqa: E402

PLIK_ETYKIET = KORZEN / "bibliotheca_ulpia" / "dane" / "kalibracja_silentium.json"
ZIARNO = 20260803          # jawne, żeby próbka była odtwarzalna (Prawo I)


def katalog_transkryptow() -> Optional[Path]:
    """Katalog transkryptów tego repo albo None (np. w chmurze/CI — wtedy pomiar pomijamy)."""
    baza = Path.home() / ".claude" / "projects"
    if not baza.is_dir():
        return None
    znacznik = str(KORZEN).replace(":", "-").replace("\\", "-").replace("/", "-")
    for kand in baza.iterdir():
        if kand.name.lower().lstrip("-") == znacznik.lower().lstrip("-"):
            return kand
    return None


def zbierz_komendy(katalog: Path) -> List[str]:
    """Unikalne komendy powłoki z transkryptów, w kolejności pierwszego wystąpienia."""
    widziane: Dict[str, None] = {}
    for plik in sorted(katalog.glob("*.jsonl")):
        try:
            with open(plik, encoding="utf-8", errors="replace") as f:
                for linia in f:
                    if '"tool_use"' not in linia:
                        continue
                    try:
                        rekord = json.loads(linia)
                    except ValueError:
                        continue
                    tresc = (rekord.get("message") or {}).get("content") or []
                    if not isinstance(tresc, list):
                        continue
                    for blok in tresc:
                        if (isinstance(blok, dict) and blok.get("type") == "tool_use"
                                and blok.get("name") in ("Bash", "PowerShell")):
                            cmd = (blok.get("input") or {}).get("command")
                            if cmd:
                                widziane.setdefault(cmd, None)
        except OSError:
            continue
    return list(widziane)


def warstwy(komendy: List[str]) -> Tuple[List[str], List[str]]:
    oskarzone = [c for c in komendy if komenda_pisze(c)]
    przepuszczone = [c for c in komendy if not komenda_pisze(c)]
    return oskarzone, przepuszczone


def probka(komendy: List[str], n_na_warstwe: int = 75) -> List[str]:
    oskarzone, przepuszczone = warstwy(komendy)
    rng = random.Random(ZIARNO)
    wybor = rng.sample(oskarzone, min(n_na_warstwe, len(oskarzone)))
    wybor += rng.sample(przepuszczone, min(n_na_warstwe, len(przepuszczone)))
    return wybor


def wczytaj_etykiety() -> Dict[str, str]:
    try:
        dane = json.loads(PLIK_ETYKIET.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {p["komenda"]: p["etykieta"] for p in dane.get("probki", [])}


def raport(etykiety: Optional[Dict[str, str]] = None) -> Dict[str, object]:
    """Metryki klasyfikatora wobec etykiet Architekta."""
    etykiety = wczytaj_etykiety() if etykiety is None else etykiety
    tp = fp = tn = fn = 0
    pomylki: List[Dict[str, str]] = []
    for cmd, prawda in etykiety.items():
        powod = komenda_pisze(cmd)
        orzeklem = bool(powod)
        pisze = prawda == "PISZE"
        if orzeklem and pisze:
            tp += 1
        elif orzeklem and not pisze:
            fp += 1
            pomylki.append({"typ": "FAŁSZYWY ALARM", "komenda": cmd, "powod": powod or ""})
        elif not orzeklem and pisze:
            fn += 1
            pomylki.append({"typ": "PRZECIEK", "komenda": cmd, "powod": ""})
        else:
            tn += 1
    precyzja = tp / (tp + fp) if (tp + fp) else None
    czulosc = tp / (tp + fn) if (tp + fn) else None
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "n": len(etykiety),
            "precyzja": precyzja, "czulosc": czulosc, "pomylki": pomylki,
            **_wazone_populacja()}


def _wazone_populacja() -> Dict[str, object]:
    """Czułość PRZELICZONA NA POPULACJĘ, nie na próbkę.

    Próbka jest WZBOGACONA (50/50), a w korpusie warstwy mają rozmiary ~1109 / ~4462.
    Czułość liczona wprost z próbki zawyżałaby wynik, bo przecieki mieszkają w warstwie
    liczniejszej — czyli miernik chwaliłby zamiast mierzyć. Ważymy udziałem warstw.
    """
    try:
        dane = json.loads(PLIK_ETYKIET.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    rozmiary = dane.get("rozmiary_warstw") or {}
    if not rozmiary:
        return {}
    licznik = mianownik = 0.0
    for warstwa, populacja in rozmiary.items():
        pozycje = [p for p in dane["probki"] if p["warstwa"] == warstwa]
        if not pozycje:
            continue
        waga = populacja / len(pozycje)
        for p in pozycje:
            if p["etykieta"] != "PISZE":
                continue
            mianownik += waga
            if komenda_pisze(p["komenda"]):
                licznik += waga
    return {"czulosc_populacyjna": (licznik / mianownik) if mianownik else None,
            "zapisow_w_korpusie": round(mianownik)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Kalibracja klasyfikatora komend SILENTIUM")
    ap.add_argument("--probka", action="store_true", help="wypisz próbkę do etykietowania")
    ap.add_argument("--raport", action="store_true", help="metryki wobec zapisanych etykiet")
    ap.add_argument("--na-warstwe", type=int, default=75)
    a = ap.parse_args()

    if a.probka:
        katalog = katalog_transkryptow()
        if katalog is None:
            print("⚠️ Brak katalogu transkryptów — próbki nie da się zbudować na tej maszynie.")
            return 1
        komendy = zbierz_komendy(katalog)
        oskarzone, przepuszczone = warstwy(komendy)
        print(f"# korpus: {len(komendy)} unikalnych | oskarżone {len(oskarzone)} "
              f"| przepuszczone {len(przepuszczone)}")
        for i, cmd in enumerate(probka(komendy, a.na_warstwe), 1):
            print(f"--- {i} [{'OSKARZONA' if komenda_pisze(cmd) else 'PRZEPUSZCZONA'}]")
            print(cmd.replace("\n", "\\n")[:400])
        return 0

    wynik = raport()
    if not wynik["n"]:
        print("⚠️ Brak zapisanych etykiet — najpierw `--probka`, potem etykietowanie.")
        return 1
    p, c = wynik["precyzja"], wynik["czulosc"]
    print("📏 KALIBRACJA SILENTIUM — klasyfikator komend powłoki")
    print(f"   próba: {wynik['n']} realnych komend (warstwowa, ziarno {ZIARNO})")
    print(f"   TP {wynik['tp']} | FP {wynik['fp']} | TN {wynik['tn']} | FN {wynik['fn']}")
    print(f"   precyzja: {p:.1%}" if p is not None else "   precyzja: —")
    print(f"   czułość (próbka wzbogacona): {c:.1%}" if c is not None else "   czułość: —")
    cp = wynik.get("czulosc_populacyjna")
    if cp is not None:
        print(f"   czułość WAŻONA POPULACJĄ: {cp:.1%} "
              f"(szacowanych zapisów w korpusie: {wynik.get('zapisow_w_korpusie')})")
    for m in wynik["pomylki"]:
        print(f"   ⚠️ {m['typ']}: {m['komenda'][:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
