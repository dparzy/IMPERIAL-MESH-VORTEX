#!/usr/bin/env python3
"""
🏛️ SCHOLA — organ Szkoły Cezara: czyta lekcje z ŻYWEGO dokumentu i pilnuje,
   żeby żadna nie została ładną teorią.

Rzymska *schola* = ława, przy której siada się razem i rozprawia — nauczyciel i uczeń
po tej samej stronie stołu. Stąd nazwa dokumentu `docs/SCHOLA_CAESARIS.md`.

────────────────────────────────────────────────────────────────────────────────
DLACZEGO ORGAN, A NIE SAM DOKUMENT (rozkaz Cezara 2026-07-29: „dokument żywy stale
podlegający rozwojowi i pamiętany co sesja")

Sam plik .md zgniłby — mamy na to twardy dowód z własnej historii: runbook W11 kazał
Claude `git push` przez 9 dni po zakazie, bo miał własną, ręcznie wpisaną treść.
Lekarstwem na gnicie jest **odebranie dokumentowi prawa do własnej prawdy o sobie**:
liczba lekcji, postęp i lista hipotez NIE są wpisywane ręcznie — organ liczy je
z treści przy każdym wywołaniu.

CO ORGAN EGZEKWUJE (i dlaczego to nie jest ozdoba):
  • **Każda lekcja MUSI mieć status.** Lekcja bez statusu jest niedokończona dokładnie
    tak jak organ bez testu (LEX TALARUS) — brzmi mądrze i nie zobowiązuje do niczego.
  • **HIPOTEZY są wyliczane osobno.** To jedyne miejsce, w którym nauka Cezara wraca
    do Imperium jako ZADANIE: „to warto sprawdzić pomiarem w najbliższej wachcie".
  • **Postęp liczony z pliku**, nigdy z pamięci — inaczej spis kłamałby po pierwszej
    dopisanej lekcji.

Organ NICZEGO nie ocenia i nie interpretuje treści lekcji — czyta strukturę. Ocena
należy do pomiaru, nie do parsera (Prawo I).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[2]
DOKUMENT = KORZEN / "docs" / "SCHOLA_CAESARIS.md"

# Nagłówek lekcji: "## LEKCJA 7 — TYTUŁ"
RE_LEKCJA = re.compile(r"^##\s+LEKCJA\s+(\d+)\s+[—-]\s+(.+?)\s*$", re.MULTILINE)
# Status: linia po "### 📊 Status"
RE_STATUS = re.compile(r"###\s*📊\s*Status\s*\n+\*\*(?:[^*]*?)?(POTWIERDZONE|OBALONE|ZMIERZONE|HIPOTEZA)")

STATUSY_DOMKNIETE = {"POTWIERDZONE", "OBALONE"}


class Lekcja:
    __slots__ = ("numer", "tytul", "status", "ma_sprawdzian", "ma_dowod")

    def __init__(self, numer: int, tytul: str, tresc: str):
        self.numer = numer
        self.tytul = tytul
        m = RE_STATUS.search(tresc)
        self.status = m.group(1) if m else "BRAK"
        self.ma_sprawdzian = "🎓 Sprawdzian" in tresc
        self.ma_dowod = "🔬 Nasz własny dowód" in tresc

    def __repr__(self) -> str:  # pragma: no cover - pomocnicze
        return f"<Lekcja {self.numer} {self.status}>"


def wczytaj(sciezka: Path | str = DOKUMENT) -> list[Lekcja]:
    """Czyta lekcje z żywego dokumentu. Brak pliku = pusta lista, nie wyjątek."""
    p = Path(sciezka)
    if not p.exists():
        return []
    tekst = p.read_text(encoding="utf-8", errors="replace")
    trafienia = list(RE_LEKCJA.finditer(tekst))
    lekcje = []
    for i, m in enumerate(trafienia):
        koniec = trafienia[i + 1].start() if i + 1 < len(trafienia) else len(tekst)
        lekcje.append(Lekcja(int(m.group(1)), m.group(2), tekst[m.start():koniec]))
    return lekcje


def braki(lekcje: list[Lekcja]) -> list[str]:
    """Lekcje niedokończone — brak statusu, dowodu albo sprawdzianu.

    To NIE jest pedanteria formalna: lekcja bez własnego dowodu jest cudzą teorią,
    a lekcja bez statusu nie zobowiązuje do żadnego pomiaru. Obie klasy sprawiają,
    że szkoła zamienia się w zbiór ładnych zdań.
    """
    out = []
    for lek in lekcje:
        if lek.status == "BRAK":
            out.append(f"LEKCJA {lek.numer} „{lek.tytul[:40]}” — BRAK STATUSU")
        if not lek.ma_dowod:
            out.append(f"LEKCJA {lek.numer} — brak własnego dowodu (cudza teoria)")
        if not lek.ma_sprawdzian:
            out.append(f"LEKCJA {lek.numer} — brak sprawdzianu")
    return out


def hipotezy(lekcje: list[Lekcja]) -> list[Lekcja]:
    """Lekcje czekające na pomiar — tędy nauka Cezara wraca do Imperium jako zadanie."""
    return [x for x in lekcje if x.status not in STATUSY_DOMKNIETE and x.status != "BRAK"]


def linia_startowa(lekcje: list[Lekcja] | None = None) -> str:
    """Jedna linia na otwarcie wachty (hook sesji) — postęp LICZONY, nie wpisany."""
    lekcje = wczytaj() if lekcje is None else lekcje
    if not lekcje:
        return "🏛️ SCHOLA CAESARIS: brak dokumentu lekcji"
    hip = hipotezy(lekcje)
    domkniete = sum(1 for x in lekcje if x.status in STATUSY_DOMKNIETE)
    txt = (f"🏛️ SCHOLA CAESARIS: {len(lekcje)} lekcji | "
           f"potwierdzonych pomiarem {domkniete} | do sprawdzenia {len(hip)}")
    if hip:
        txt += f" → najbliższa: LEKCJA {hip[0].numer} „{hip[0].tytul[:38]}”"
    b = braki(lekcje)
    if b:
        txt += f" | 🚨 niedokończonych pozycji: {len(b)}"
    return txt


def raport(lekcje: list[Lekcja] | None = None) -> str:
    lekcje = wczytaj() if lekcje is None else lekcje
    if not lekcje:
        return "🏛️ SCHOLA CAESARIS — brak lekcji (dokument nie istnieje lub jest pusty)."
    ikony = {"POTWIERDZONE": "✅", "OBALONE": "❌", "ZMIERZONE": "📊",
             "HIPOTEZA": "⏳", "BRAK": "🚨"}
    L = ["🏛️ SCHOLA CAESARIS — Szkoła Cezara", ""]
    for x in lekcje:
        L.append(f"   {ikony.get(x.status,'?')} LEKCJA {x.numer:>2} — {x.tytul[:52]:54s} {x.status}")
    hip = hipotezy(lekcje)
    domkniete = sum(1 for x in lekcje if x.status in STATUSY_DOMKNIETE)
    L += ["", f"   lekcji: {len(lekcje)} | potwierdzonych pomiarem: {domkniete} | "
              f"czeka na pomiar: {len(hip)}"]
    if hip:
        L.append("")
        L.append("   ⏳ DO SPRAWDZENIA W REALU (tędy nauka wraca do Imperium jako zadanie):")
        for x in hip:
            L.append(f"      • LEKCJA {x.numer} — {x.tytul[:60]}")
    b = braki(lekcje)
    if b:
        L += ["", f"   🚨 NIEDOKOŃCZONE ({len(b)}):"]
        L += [f"      • {x}" for x in b]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SCHOLA CAESARIS — lekcje Imperium")
    ap.add_argument("tryb", nargs="?", default="raport",
                    choices=["raport", "linia", "hipotezy", "braki"])
    a = ap.parse_args(argv)
    lek = wczytaj()
    if a.tryb == "linia":
        print(linia_startowa(lek))
    elif a.tryb == "hipotezy":
        for x in hipotezy(lek):
            print(f"LEKCJA {x.numer} — {x.tytul}  [{x.status}]")
    elif a.tryb == "braki":
        for x in braki(lek):
            print(x)
        return 1 if braki(lek) else 0
    else:
        print(raport(lek))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
