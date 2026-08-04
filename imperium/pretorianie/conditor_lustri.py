"""🏁 CONDITOR LUSTRI — miernik gotowości Imperium (U1; do 2026-08-05 bramka zamrożenia).

⚠️ **STAN OD 2026-08-05:** Cezar zdjął ZAMROŻENIE LUSTRATIO **decyzją, nie spełnieniem
kryteriów** — ten organ świecił wtedy 2 spełnione / 2 niespełnione / 3 NIE WIEM. Od tej
chwili **mierzy, ale nie blokuje**: `--bramka` nadal zwraca kod wyjścia, żeby dało się go
użyć w skrypcie, lecz nic w Imperium nie jest od niego zależne. Kryteria bez producenta
(KLASY, KALIBRACJA) **pozostają długiem** i mają być widoczne dopóki go nie spłacimy.
Organ NIE ZOSTAJE przerobiony na „zielony", bo zamrożenie zniknęło — miernik, który po
zmianie decyzji politycznej zaczyna raportować sukces, przestaje być miernikiem.


Rzymscy cenzorzy kończyli lustrację obrzędem *condere lustrum* — „zamknąć lustrum".
Dopóki go nie odprawiono, cenzus trwał. Ten organ jest tym obrzędem: odpowiada
JEDNĄ liczbą i JEDNYM kodem wyjścia na pytanie, którego dotąd nikt nie umiał zadać
maszynie — **czy wolno już wrócić do rozwoju.**

POWÓD ISTNIENIA (zmierzony 2026-08-05, rozkaz Cezara „daj wg rekomendacji"):
ZAMROŻENIE LUSTRATIO (2026-08-04) zabroniło rozwoju, dopóki Imperium nie będzie
„w pełni skalibrowane i zgodne z prawem" — ale **warunek ten nie miał liczby**.
Nasz własny ROADMAP nazwał to wprost: *„W pełni skalibrowane bez liczby jest stanem
niefalsyfikowalnym: zamrożenie albo nigdy się nie skończy, albo skończy się arbitralnie."*
To jest DOKŁADNIE ta klasa wady, która zamrożenie wywołała — organ bez miary, którego
milczenie czyta się dowolnie. Zamrożenie leczące bramki bez miary samo nie miało miary.

TRZY ZASADY KONSTRUKCYJNE — po jednej z każdej klasy, którą LUSTRATIO tępi:

  • **K1 — jeden fakt, jeden producent.** Ten organ NIE LICZY NICZEGO SAM. Każde
    kryterium WOŁA organ, który już ten fakt produkuje (audyt, TABULARIUM, CODEX
    NOTARUM, BREVIARIUM, MATURITAS). Druga arytmetyka obok istniejącej to nie
    kontrola, tylko drugie źródło prawdy — na tym potknął się MATURITAS, licząc
    dług honorowy jako `NOTA − CORONA` i nie wiedząc o ODROCZENIU.

  • **K2 — milczenie NIE JEST zielenią.** Kryterium ma TRZY stany, nie dwa.
    `NIE WIEM` **blokuje tak samo jak `NIE`** i jest liczone osobno. Wyjątek
    (awaria producenta) też daje `NIE WIEM` — organ, który po błędzie mówi „OK",
    jest gorszy od organu, którego nie ma.

  • **K4 — wyciszenie zawsze z powodem na widoku.** Nie ma tu trybu „pomiń
    kryterium". Jedyne, co wolno, to nazwać BRAK PRODUCENTA — i wtedy kryterium
    świeci `NIE WIEM` razem z instrukcją, co zbudować, żeby przestało.

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ **Nie ocenia L4 samego siebie.** L4 („bramka wyjścia") jest w ROADMAP pozycją
    otwartą, a domknie ją dopiero istnienie TEGO organu. Gdyby wchodziła do kryteriów,
    bramka żądałaby własnego domknięcia, by się domknąć — zakleszczenie, które
    wyglądałoby na surowość, a byłoby błędem logicznym.
  • ❌ **Nie zdejmuje zamrożenia sam.** Zwraca werdykt; zdjęcie zamrożenia to decyzja
    Cezara (nieodwracalna, kierunkowa — Prawo XVIII).
  • ❌ **Nie steruje niczym w handlu.** To lustro procesu, nie kierownica (Goodhart).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

KORZEN = Path(__file__).resolve().parent.parent.parent

SPELNIONE = "SPEŁNIONE"
NIESPELNIONE = "NIESPEŁNIONE"
NIE_WIEM = "NIE WIEM"

IKONA = {SPELNIONE: "✅", NIESPELNIONE: "❌", NIE_WIEM: "❔"}


@dataclass
class Kryterium:
    """Jedno pytanie bramki wyjścia — z jawnym PRODUCENTEM faktu (K1)."""
    klucz: str
    pytanie: str
    producent: str                      # kto ten fakt WYTWARZA (nie: kto go przepisuje)
    stan: str = NIE_WIEM
    wartosc: str = ""
    powod: str = ""
    co_zrobic: str = ""

    @property
    def blokuje(self) -> bool:
        """`NIE WIEM` blokuje tak samo jak `NIESPEŁNIONE` — to jest cała klasa K2."""
        return self.stan != SPELNIONE


# ── KRYTERIA ────────────────────────────────────────────────────────────────────
# Każde jest funkcją bez argumentów zwracającą Kryterium. Wyjątek producenta łapiemy
# w `zmierz()` i zamieniamy na NIE WIEM — nigdy na zieleń.

def k_audyt() -> Kryterium:
    """Bramka Prawa XXI — 24 warstwy audytu spójności."""
    from narzedzia.audyt_spojnosci import audyt      # producent
    bledy, _info = audyt()
    return Kryterium(
        klucz="AUDYT",
        pytanie="Bramka Prawa XXI (audyt spójności) jest zielona",
        producent="narzedzia/audyt_spojnosci.py::audyt()",
        stan=SPELNIONE if not bledy else NIESPELNIONE,
        wartosc=f"{len(bledy)} rozbieżności",
        powod="" if not bledy else "; ".join(bledy[:3]),
        co_zrobic="" if not bledy else "Napraw rozbieżności — audyt musi dawać exit 0",
    )


def k_testy() -> Kryterium:
    """Testy zielone dla DOKŁADNIE tego kodu (odcisk źródeł, nie „ostatnio przechodziły")."""
    from imperium.oczy.breviarium import stan_testow    # producent
    s = stan_testow()
    status = s.get("status", "BRAK")
    # BREVIARIUM rozróżnia „czerwone" od „nie wiem, bo pieczęć dotyczy innego kodu" — i to
    # rozróżnienie jest tu warte więcej niż sama liczba testów: wynik zielony dla PRZESZŁEJ
    # wersji kodu to niewiedza, nie zgoda. Mapujemy je 1:1, nie spłaszczamy do bool.
    stan = {"ZIELONE": SPELNIONE, "CZERWONE": NIESPELNIONE}.get(status, NIE_WIEM)
    return Kryterium(
        klucz="TESTY", pytanie="Testy zielone dla DOKŁADNIE tego kodu",
        producent="imperium/oczy/breviarium.py::stan_testow()",
        stan=stan,
        wartosc=s.get("opis", status),
        powod="" if stan == SPELNIONE else f"status pieczęci: {status}",
        co_zrobic="" if stan == SPELNIONE else "Uruchom `python tests/run_tests.py` na bieżącym kodzie",
    )


def k_tabularium() -> Kryterium:
    """Rejestr dokumentów: zero błędów I zero nieprzerobionych alarmów GNICIA/DUBLET."""
    from narzedzia.tabularium import sprawdz            # producent
    bledy, ostrzezenia, _info = sprawdz()
    razem = len(bledy) + len(ostrzezenia)
    return Kryterium(
        klucz="TABULARIUM",
        pytanie="Rejestr dokumentów bez błędów i bez nieprzerobionych alarmów",
        producent="narzedzia/tabularium.py::sprawdz()",
        stan=SPELNIONE if razem == 0 else NIESPELNIONE,
        wartosc=f"{len(bledy)} błędów, {len(ostrzezenia)} ostrzeżeń",
        powod="" if razem == 0 else f"{len(ostrzezenia)} alarmów T2/T3 czeka na przegląd treści",
        co_zrobic="" if razem == 0 else
                  "Przerób alarmy (`tabularium.py swiadectwa` nadaje im wagę) albo zapisz "
                  "werdykt z POWODEM — wyciszenie bez powodu jest zakazane (K4)",
    )


def k_dlug_honorowy() -> Kryterium:
    """LEX TALIONIS — błąd bez kompensującego unikatu. Producent liczy PAROWANIE, nie sumy."""
    from imperium.biblioteki import codex_notarum       # producent
    dlug = codex_notarum.dlug_honorowy()
    odr = codex_notarum.odroczone()
    return Kryterium(
        klucz="DLUG",
        pytanie="Dług honorowy spłacony (LEX TALIONIS)",
        producent="imperium/biblioteki/codex_notarum.py::dlug_honorowy()",
        stan=SPELNIONE if not dlug else NIESPELNIONE,
        # Odroczone pokazujemy ZAWSZE, także przy zielonym — odroczenie zdejmuje blokadę,
        # nie dług, a niewidoczne odroczenie jest cichym umorzeniem (K4).
        wartosc=f"{len(dlug)} nieodrobionych, {len(odr)} odroczonych",
        powod="" if not dlug else f"{len(dlug)} not bez CORONY",
        co_zrobic="" if not dlug else "Dostarcz zatwierdzoną CORONĘ (Cezar wybiera z TRZECH opcji)",
    )


# Etapy LUSTRATIO czytane z ROADMAP. L4 świadomie POZA listą — patrz docstring modułu.
ETAPY_POZA_OCENA = {"L4"}


def k_etapy() -> Kryterium:
    """Etapy przeglądu L0–L3x domknięte (stan czytany z ROADMAP jednym parserem)."""
    from imperium.oczy.maturitas import wiersze_stanu, _stan_domkniety   # producent parsera
    import re

    rm = KORZEN / "docs" / "ROADMAP_IMPERIUM.md"
    if not rm.exists():
        return Kryterium(
            klucz="ETAPY", pytanie="Etapy LUSTRATIO L0–L3 domknięte",
            producent="docs/ROADMAP_IMPERIUM.md + maturitas.wiersze_stanu()",
            stan=NIE_WIEM, wartosc="brak ROADMAP",
            powod="Nie ma z czego czytać stanu etapów",
            co_zrobic="Przywróć docs/ROADMAP_IMPERIUM.md",
        )
    tekst = rm.read_text(encoding="utf-8", errors="replace")
    otwarte, nieznane, domkniete = [], [], []
    for etykieta, stan in wiersze_stanu(tekst):
        czysta = etykieta.replace("*", "").strip()
        if not re.fullmatch(r"L\d[a-z]?\d?", czysta) or czysta in ETAPY_POZA_OCENA:
            continue
        czy = _stan_domkniety(stan)
        (domkniete if czy is True else otwarte if czy is False else nieznane).append(czysta)

    if nieznane:
        stan_k = NIE_WIEM
    elif otwarte:
        stan_k = NIESPELNIONE
    elif domkniete:
        stan_k = SPELNIONE
    else:
        stan_k = NIE_WIEM          # zero rozpoznanych etapów = zmieniony format, nie sukces

    return Kryterium(
        klucz="ETAPY",
        pytanie="Etapy LUSTRATIO L0–L3 domknięte (L4 poza oceną — to ta bramka)",
        producent="docs/ROADMAP_IMPERIUM.md + maturitas.wiersze_stanu()",
        stan=stan_k,
        wartosc=f"{len(domkniete)} domkniętych / {len(otwarte)} otwartych"
                + (f" / {len(nieznane)} bez statusu" if nieznane else ""),
        powod=("otwarte: " + ", ".join(otwarte) if otwarte else
               "bez czytelnego statusu: " + ", ".join(nieznane) if nieznane else
               "nie rozpoznano ani jednego wiersza etapu" if stan_k == NIE_WIEM else ""),
        co_zrobic=("Domknij etapy albo — jeśli etap jest zbędny — skreśl go z POWODEM"
                   if otwarte or nieznane else ""),
    )


# ── KRYTERIA BEZ PRODUCENTA ─────────────────────────────────────────────────────
# Nie udajemy, że ich nie ma, i nie dajemy im zieleni „z rozsądku". Świecą NIE WIEM
# i NIOSĄ INSTRUKCJĘ, co zbudować. To jest ta różnica, o którą chodzi w całym LUSTRATIO:
# organ przyznaje się do niewiedzy zamiast milczeć.

BRAK_PRODUCENTA: List[Dict[str, str]] = [
    {
        "klucz": "KLASY",
        "pytanie": "Cztery klasy wad K1–K4 mają lek WDROŻONY, nie tylko nazwany",
        "producent": "BRAK — nikt nie mierzy pokrycia klas lekami",
        "powod": "K1–K4 są opisane w ROADMAP jako tabela prozą; żaden organ nie odpowiada, "
                 "czy lek został wdrożony i gdzie. Rozpoznane po tym, że K1 (MATURITAS liczący "
                 "dług osobną arytmetyką) przeżył dobę po własnym nazwaniu.",
        "co_zrobic": "Rejestr klas: dla każdej K1–K4 lista miejsc wdrożenia leku + test, "
                     "który pilnuje, że lek nie zniknął",
    },
    {
        "klucz": "KALIBRACJA",
        "pytanie": "Organy ORZEKAJĄCE skalibrowane na prawdzie podstawowej (LEX TALARUS)",
        "producent": "BRAK — nie istnieje rejestr kalibracji przyrządów",
        "powod": "Powód samego zamrożenia: przyrządy orzekały bez kalibracji (bramka GNICIA "
                 "miała 33% precyzji, LUSTRUM 100% fałszywek na jednym sygnale). Dziś "
                 "kalibracja żyje w prozie Dziennika, więc nie da się zapytać, ILE organów "
                 "orzekających jest jeszcze nieskalibrowanych.",
        "co_zrobic": "Rejestr kalibracji: organ orzekający → data, próbka, precyzja/recall; "
                     "organ bez wpisu liczy się jako NIESKALIBROWANY",
    },
]


def _kryteria_bez_producenta() -> List[Kryterium]:
    return [Kryterium(klucz=b["klucz"], pytanie=b["pytanie"], producent=b["producent"],
                      stan=NIE_WIEM, wartosc="brak miernika",
                      powod=b["powod"], co_zrobic=b["co_zrobic"])
            for b in BRAK_PRODUCENTA]


KRYTERIA: List[Callable[[], Kryterium]] = [
    k_audyt, k_testy, k_tabularium, k_dlug_honorowy, k_etapy,
]


@dataclass
class Werdykt:
    kryteria: List[Kryterium] = field(default_factory=list)

    @property
    def spelnione(self) -> int:
        return sum(1 for k in self.kryteria if k.stan == SPELNIONE)

    @property
    def niespelnione(self) -> int:
        return sum(1 for k in self.kryteria if k.stan == NIESPELNIONE)

    @property
    def nieznane(self) -> int:
        return sum(1 for k in self.kryteria if k.stan == NIE_WIEM)

    @property
    def wolno_zdjac(self) -> bool:
        """Zamrożenie wolno zdjąć TYLKO gdy każde kryterium jest SPEŁNIONE.

        `NIE WIEM` blokuje celowo: gdyby nie blokowało, dołożenie kryterium bez miernika
        byłoby najtańszym sposobem na zieloną bramkę — czyli mierzenie zamienione
        w chwalenie (Goodhart).
        """
        return bool(self.kryteria) and all(k.stan == SPELNIONE for k in self.kryteria)

    def jako_dict(self) -> Dict[str, Any]:
        return {
            "wolno_zdjac_zamrozenie": self.wolno_zdjac,
            "spelnione": self.spelnione,
            "niespelnione": self.niespelnione,
            "nieznane": self.nieznane,
            "kryteria": [
                {"klucz": k.klucz, "stan": k.stan, "wartosc": k.wartosc,
                 "producent": k.producent, "powod": k.powod, "co_zrobic": k.co_zrobic}
                for k in self.kryteria
            ],
        }


def zmierz(kryteria: Optional[List[Callable[[], Kryterium]]] = None) -> Werdykt:
    """Woła każdego producenta. Awaria producenta = NIE WIEM (nigdy zieleń)."""
    out: List[Kryterium] = []
    for fn in (KRYTERIA if kryteria is None else kryteria):
        try:
            out.append(fn())
        except Exception as e:                        # noqa: BLE001 — celowo szeroko
            out.append(Kryterium(
                klucz=getattr(fn, "__name__", "?").removeprefix("k_").upper(),
                pytanie="(producent nie odpowiedział)",
                producent=getattr(fn, "__name__", "?"),
                stan=NIE_WIEM, wartosc="awaria producenta",
                powod=f"{type(e).__name__}: {e}",
                co_zrobic="Napraw producenta — organ, który po błędzie mówi OK, jest gorszy "
                          "od organu, którego nie ma",
            ))
    out.extend(_kryteria_bez_producenta())
    return Werdykt(kryteria=out)


def raport_tekst(w: Optional[Werdykt] = None) -> str:
    w = w or zmierz()
    linie = ["🏁 CONDITOR LUSTRI — bramka wyjścia z ZAMROŻENIA LUSTRATIO (U1)", ""]
    for k in w.kryteria:
        linie.append(f"   {IKONA[k.stan]} [{k.klucz}] {k.pytanie}")
        linie.append(f"      · stan: {k.stan} — {k.wartosc}")
        linie.append(f"      · producent: {k.producent}")
        if k.powod:
            linie.append(f"      · dlaczego: {k.powod}")
        if k.co_zrobic:
            linie.append(f"      → {k.co_zrobic}")
    linie.append("")
    linie.append(f"   RAZEM: {w.spelnione} spełnionych | {w.niespelnione} niespełnionych "
                 f"| {w.nieznane} NIE WIEM")
    if w.wolno_zdjac:
        linie.append("   ✅ WOLNO ZDJĄĆ ZAMROŻENIE — decyzja należy do Cezara (organ nie zdejmuje sam).")
    else:
        linie.append(f"   ⛔ ZAMROŻENIE TRWA — do zdjęcia brakuje "
                     f"{w.niespelnione + w.nieznane} kryteriów (powyżej, z instrukcją).")
        linie.append("   ℹ️ `NIE WIEM` blokuje tak samo jak `NIE` — milczenie nie jest zielenią (K2).")
    return "\n".join(linie)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    w = zmierz()
    if "--json" in argv:
        import json
        print(json.dumps(w.jako_dict(), ensure_ascii=False, indent=2))
    else:
        print(raport_tekst(w))
    # `--bramka`: kod wyjścia do skryptów. Bez flagi raport nie bramkuje niczego,
    # żeby dało się go czytać w hooku bez wywracania sesji.
    if "--bramka" in argv:
        return 0 if w.wolno_zdjac else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
