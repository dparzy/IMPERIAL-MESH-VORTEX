"""
🧠 Pamięć Sesji (W-360) — ciągłość między sesjami Claude Code.

WARSTWA 3 PAMIĘCI (uzupełnia, nie zastępuje):
  • Warstwa 1: pamiec_absolutna / Mnemosyne — pamięć TRANSAKCJI (trade learning).
  • Warstwa 2: Bibliotheca-RAG — pamięć semantyczna KSIĄŻEK + dokumentów.
  • Warstwa 3 (TEN MODUŁ): pamięć CIĄGŁOŚCI SESJI — mapa podpięć, lekcje, decyzje
    które GINĘŁY przy kompakcji kontekstu. Źródło prawdy: docs/PAMIEC_SESJI.md.

PROBLEM KTÓRY ROZWIĄZUJE (Cezar, 2026-06-21):
  „pamiętasz pełną mapę podpięć do lokala?" — mapa zniknęła w poprzedniej kompakcji.
  Ten moduł czyni pamięć sesji PROGRAMOWĄ: czyta, dopisuje i przeszukuje lekcje,
  a SessionStart hook wyświetla ją na starcie KAŻDEJ sesji (nigdy więcej utraty).

Markdown jako baza (świadomie, nie SQLite): plik jest jednocześnie czytelny dla
Cezara, wersjonowany w git, indeksowalny w RAG (korpus `dane`). Prawo I — jedno
źródło prawdy, zero duplikacji stanu.
"""

from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import List, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
DOMYSLNY_PLIK = ROOT / "docs" / "PAMIEC_SESJI.md"

_NAGLOWEK_LEKCJE = "## 📚 LEKCJE Z SESJI"


def _dzis() -> str:
    return _dt.date.today().isoformat()


def wczytaj(plik: Path = DOMYSLNY_PLIK) -> str:
    """Surowa treść pliku pamięci sesji ("" gdy brak)."""
    return plik.read_text(encoding="utf-8") if plik.exists() else ""


def lekcje(plik: Path = DOMYSLNY_PLIK, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Lista lekcji z sekcji „LEKCJE Z SESJI", od najnowszej (góra pliku).
    Zwraca [{"naglowek": "### DATA — tytuł", "data": "...", "tytul": "...",
             "tresc": "..."}]. limit=N → tylko N pierwszych.
    """
    tekst = wczytaj(plik)
    if _NAGLOWEK_LEKCJE not in tekst:
        return []
    sekcja = tekst.split(_NAGLOWEK_LEKCJE, 1)[1]

    # KOTWICA NA DACIE (odporne na markdown w treści — recenzja adversarial 2026-06-21):
    # lekcja to TYLKO nagłówek `### YYYY-MM-DD — tytuł`. Body kończy się na następnym
    # takim nagłówku, następnej sekcji `## ` (np. STAN BIEŻĄCY) lub końcu. Dzięki temu
    # `### podtytuł` ani `## wniosek` W TREŚCI nie rozbijają parsowania na fantomy.
    wzor = re.compile(
        r"^### (\d{4}-\d{2}-\d{2})\s*[—-]\s*(.+?)\s*\n"
        r"(.*?)(?=\n### \d{4}-\d{2}-\d{2}\s*[—-]|\n## |\Z)",
        re.M | re.S,
    )
    wyniki: List[Dict[str, str]] = []
    for m in wzor.finditer(sekcja):
        data, tytul, tresc = m.group(1), m.group(2).strip(), m.group(3).strip()
        wyniki.append({"naglowek": f"### {data} — {tytul}", "data": data,
                       "tytul": tytul, "tresc": tresc})
        if limit is not None and len(wyniki) >= limit:
            break
    return wyniki


def dopisz_lekcje(tytul: str, tresc: str, data: Optional[str] = None,
                  plik: Path = DOMYSLNY_PLIK) -> None:
    """
    Dopisuje nową lekcję na GÓRZE sekcji „LEKCJE Z SESJI" (najnowsza pierwsza).
    Tworzy sekcję, gdy nie istnieje. Aktualizuje też „Ostatnia aktualizacja".
    tresc: markdown (może mieć wiele linii, listy itd.).
    """
    data = data or _dzis()
    tekst = wczytaj(plik)
    blok = f"### {data} — {tytul}\n{tresc.strip()}\n"

    if _NAGLOWEK_LEKCJE in tekst:
        przed, po = tekst.split(_NAGLOWEK_LEKCJE, 1)
        # po zaczyna się od reszty sekcji; wstaw blok zaraz po nagłówku
        po = po.lstrip("\n")
        nowy = f"{przed}{_NAGLOWEK_LEKCJE}\n\n{blok}\n{po}"
    else:
        nowy = f"{tekst.rstrip()}\n\n{_NAGLOWEK_LEKCJE}\n\n{blok}\n"

    # Zaktualizuj datę "Ostatnia aktualizacja: ..." (lub wstaw gdy brak — BUG 4 recenzji,
    # bez tego re.sub był cichym no-op i kontrakt „aktualizuje datę" był łamany).
    if re.search(r"## Ostatnia aktualizacja:", nowy):
        nowy = re.sub(r"(## Ostatnia aktualizacja:).*",
                      rf"\1 {data}", nowy, count=1)
    else:
        linie = nowy.split("\n", 1)
        naglowek_pliku = linie[0]
        reszta_pliku = linie[1] if len(linie) > 1 else ""
        nowy = f"{naglowek_pliku}\n\n## Ostatnia aktualizacja: {data}\n{reszta_pliku}"

    plik.write_text(nowy, encoding="utf-8")


def szukaj(zapytanie: str, plik: Path = DOMYSLNY_PLIK) -> List[Dict[str, str]]:
    """Lekcje zawierające zapytanie (case-insensitive) w tytule lub treści."""
    q = zapytanie.lower()
    return [lek for lek in lekcje(plik)
            if q in lek["tytul"].lower() or q in lek["tresc"].lower()]


def mapa_podpiec(plik: Path = DOMYSLNY_PLIK) -> str:
    """Zwraca sekcję mapy podpięć ("" gdy brak) — do wyświetlenia na starcie sesji."""
    tekst = wczytaj(plik)
    znacznik = "## 🗺️"
    if znacznik not in tekst:
        return ""
    od = tekst.index(znacznik)
    reszta = tekst[od + len(znacznik):]
    nast = re.search(r"\n## ", reszta)
    return (znacznik + reszta[:nast.start()]).strip() if nast else (znacznik + reszta).strip()


def podsumowanie_startowe(plik: Path = DOMYSLNY_PLIK, n_lekcji: int = 3) -> str:
    """
    Zwięzłe podsumowanie dla SessionStart hooka: ostatnie N lekcji + przypomnienie
    o mapie. Wyświetlane na starcie KAŻDEJ sesji → mapa nigdy nie ginie w kompakcji.
    """
    if not plik.exists():
        return ""
    ostatnie = lekcje(plik, limit=n_lekcji)
    linie = ["🧠 PAMIĘĆ SESJI (W-360) — ciągłość między sesjami:"]
    if ostatnie:
        linie.append(f"   Ostatnie {len(ostatnie)} lekcje:")
        for lek in ostatnie:
            linie.append(f"   • [{lek['data']}] {lek['tytul']}")
    linie.append("   📍 Pełna mapa podpięć + kolejność wdrożeń: docs/PAMIEC_SESJI.md")
    return "\n".join(linie)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Pamięć sesji Imperium (W-360)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("start", help="podsumowanie startowe (dla hooka)")
    sub.add_parser("lekcje", help="wszystkie lekcje")
    p_szukaj = sub.add_parser("szukaj", help="szukaj w lekcjach")
    p_szukaj.add_argument("zapytanie", nargs="+")
    p_dopisz = sub.add_parser("dopisz", help="dopisz lekcję")
    p_dopisz.add_argument("--tytul", required=True)
    p_dopisz.add_argument("--tresc", required=True)
    args = ap.parse_args()

    if args.cmd == "start":
        print(podsumowanie_startowe())
    elif args.cmd == "lekcje":
        for lek in lekcje():
            print(f"[{lek['data']}] {lek['tytul']}")
    elif args.cmd == "szukaj":
        for lek in szukaj(" ".join(args.zapytanie)):
            print(f"[{lek['data']}] {lek['tytul']}")
    elif args.cmd == "dopisz":
        dopisz_lekcje(args.tytul, args.tresc)
        print(f"✅ Dopisano lekcję: {args.tytul}")
    else:
        print(podsumowanie_startowe())
