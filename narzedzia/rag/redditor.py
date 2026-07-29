#!/usr/bin/env python3
"""
🧩 REDDITOR — Zwracający Całość: fragmentacja z KRYPTOGRAFICZNYM DOWODEM bezstratności.

Rzymski *redditor* = ten, który ZWRACA, oddaje w całości (od `reddere` — oddać).
Imię dobrane do jedynej właściwości, która ten organ odróżnia: z jego fragmentów da
się ODDAĆ dokument źródłowy co do bajtu — i to jest sprawdzane, nie obiecywane.

────────────────────────────────────────────────────────────────────────────────
DLACZEGO TO JEST UNIKAT (spłata TALARA, Cezar 2026-07-29)

Zwiad zewnętrzny (FRUMENTARIUS, 2026-07-29) ustalił dwie luki w całym publicznym
dorobku: (a) nie istnieje benchmark fragmentacji dla korpusów quant-finance,
(b) nikt nie MIERZY, czy fragmentacja coś zgubiła — mierzy się trafność wyszukiwania
(recall@k, RAGAS), czyli skutek, nigdy przyczynę. Świat dzieli teksty i ZAKŁADA,
że nic nie przepadło, bo „przecież tylko tniemy".

Nasz własny pomiar pokazał, ile kosztuje to założenie: 1 479 710 linii struktury
w cache → **0** po fragmentacji. Słowa przeżywały wszystkie (0 zgubionych), ale
tabela przestawała być tabelą. Zdanie „nic nie zginęło" było prawdziwe o SŁOWACH
i fałszywe o DOKUMENCIE.

REDDITOR odwraca ciężar dowodu: fragment nie jest kopią tekstu, tylko **ZAKRESEM
(start, koniec) w dokumencie źródłowym**. Skoro fragmenty są zakresami kanonicznego
podziału, to ich sklejenie MUSI dać źródło — a jeśli nie daje, SHA-256 to wykrzyczy.
Bezstratność przestaje być deklaracją i staje się twierdzeniem sprawdzanym per książka.

RÓŻNICA WOBEC TEGO, CO MAMY (Prawo XVI — nie dublujemy):
    podziel_na_chunki:  " ".join(tekst.split())  → kasuje 100% struktury, brak dowodu
    REDDITOR:           tekst[start:koniec]      → zachowuje bajt w bajt + dowód SHA-256

────────────────────────────────────────────────────────────────────────────────
TRZY WŁASNOŚCI, KTÓRE MUSZĄ ZACHODZIĆ RAZEM (i są testowane)

1. KANON POKRYWA WSZYSTKO. Zakresy kanoniczne są rozłączne, posortowane i ich suma
   to dokładnie [0, len(tekst)). Stąd rekonstrukcja = proste sklejenie.
2. REKONSTRUKCJA JEST TOŻSAMA. sha256(sklejenie) == sha256(źródło). Bajt w bajt,
   razem ze znakami nowej linii, wcięciami i białymi znakami tabel.
3. OKNA WYSZUKIWANIA SĄ POCHODNE, NIE ŹRÓDŁEM. Do indeksu idą okna z zakładką
   (overlap) — ale zakładka NIE psuje dowodu, bo dowód liczy się z kanonu.
   To rozdzielenie jest sednem: overlap służy trafności, kanon służy prawdzie.

GRANICE CIĘCIA — dlaczego akapit, a nie 400 słów:
Tniemy na granicach STRUKTURALNYCH (pusta linia = koniec akapitu/bloku), bo to one
niosą sens w książce technicznej. Blok, który wygląda na TABELĘ (wiele krótkich linii
z liczbami), jest NIEROZERWALNY — wolimy fragment większy niż rozkrojona tabela,
bo tabela przecięta w pół jest bezwartościowa dla obu połówek.

ADRES FRAGMENTU (kontekst) jest METADANĄ, nie tekstem — doklejenie go do treści
złamałoby własność 2. To celowe: adres pomaga wyszukiwarce, ale nie wolno mu
zanieczyścić dowodu bezstratności.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

KORZEN = Path(__file__).resolve().parents[2]
CACHE = KORZEN / "bibliotheca_ulpia" / "dane" / "tekst_cache"

# Blok = ciąg tekstu rozdzielony pustą linią. To najtańsza granica strukturalna,
# która nie wymaga ani modelu, ani zależności (doktryna stdlib-first).
RE_PUSTA = re.compile(r"\n[ \t]*\n")
# Nagłówek rozdziału/sekcji — używany do ADRESU fragmentu (metadana).
RE_SEKCJA = re.compile(
    r"^\s*(?:(?:CHAPTER|Chapter|Rozdział)\s+\d+|(\d+\.\d+(?:\.\d+)?)\s+\S)", re.MULTILINE
)
# Wiersz „tabelaryczny": krótki i z co najmniej dwiema liczbami/symbolami kolumn.
RE_LICZBA = re.compile(r"(?<![\w.])-?\d+[\d.,]*")

DOMYSLNY_CEL = 400      # docelowy rozmiar fragmentu w słowach
DOMYSLNY_MAX = 900      # twardy sufit — chroni przed połknięciem całego rozdziału
DOMYSLNY_OVERLAP = 50   # zakładka OKIEN wyszukiwania (nie dotyczy kanonu)
PODLOGA_SLOW = 20       # poniżej tego fragment nie niesie samodzielnego sensu (NORMA K5)
ADRES_FRONT = "«front»"  # fragment przed pierwszym nagłówkiem — adres ZNANY, nie pusty


@dataclass(frozen=True)
class Zakres:
    """Fragment jako ZAKRES w źródle — nie kopia. Stąd bierze się dowód."""

    start: int
    koniec: int
    adres: str = ""
    tabelaryczny: bool = False

    def tekst(self, zrodlo: str) -> str:
        return zrodlo[self.start:self.koniec]

    def slowa(self, zrodlo: str) -> int:
        return len(self.tekst(zrodlo).split())


@dataclass
class Podzial:
    """Wynik pracy organu: kanon (dowód) + okna (wyszukiwanie)."""

    zrodlo_sha: str
    kanon: list[Zakres] = field(default_factory=list)
    okna: list[Zakres] = field(default_factory=list)


def _bloki(tekst: str) -> list[tuple[int, int]]:
    """Dzieli tekst na bloki po pustych liniach. Zakresy POKRYWAJĄ całość."""
    granice: list[tuple[int, int]] = []
    poz = 0
    for m in RE_PUSTA.finditer(tekst):
        # koniec bloku ustawiamy PO separatorze, żeby nie zgubić ani jednego znaku
        granice.append((poz, m.end()))
        poz = m.end()
    granice.append((poz, len(tekst)))
    return [g for g in granice if g[0] < g[1]]


def _rozbij_wielki(tekst: str, b0: int, b1: int, cel: int,
                   maks: int = 900) -> list[tuple[int, int]]:
    """Dzieli NADMIAROWY blok na mniejsze, schodząc po coraz słabszych granicach.

    POWÓD (zmierzony 2026-07-29, przed jakąkolwiek deklaracją, że organ działa):
    podział wyłącznie po pustych liniach zakładał, że każda książka je ma. BIB-012
    dała medianę 4 904 słów na fragment, a BIB-001 czternaście fragmentów >2000 słów —
    fragment tej wielkości jest bezużyteczny dla wyszukiwania, bo trafienie nie
    wskazuje już MIEJSCA. Schodzimy więc kolejno: koniec zdania → nowa linia →
    twarde cięcie po słowach. Ostatni poziom nigdy nie zawodzi, więc pokrycie
    (a z nim dowód SHA-256) pozostaje nienaruszone.
    """
    for wzor in (re.compile(r"(?<=[.!?])\s+"), re.compile(r"\n")):
        punkty = [b0] + [b0 + m.end() for m in wzor.finditer(tekst[b0:b1])] + [b1]
        punkty = sorted(set(p for p in punkty if b0 <= p <= b1))
        if len(punkty) <= 2:
            continue
        wynik, start, slow = [], b0, 0
        for i in range(1, len(punkty)):
            slow += len(tekst[punkty[i - 1]:punkty[i]].split())
            if slow >= cel and punkty[i] < b1:
                wynik.append((start, punkty[i]))
                start, slow = punkty[i], 0
        if start < b1:
            wynik.append((start, b1))
        # WARUNEK NAPRAWIONY po recenzji 2026-07-29: poprzednio wystarczyło „więcej niż
        # jeden kawałek", więc tekst o rzadkich kropkach (4 zdania po 1500 słów) kończył
        # pracę na poziomie zdaniowym i zwracał fragmenty po 1501 słów przy sufcie 900 —
        # czyli funkcja istniejąca WYŁĄCZNIE po to, by pilnować sufitu, cicho go łamała.
        # Teraz poziom musi dodatkowo ZMIEŚCIĆ każdy kawałek pod sufitem; inaczej schodzimy
        # niżej, aż do twardego cięcia po słowach, które nie może zawieść.
        if len(wynik) > 1 and all(len(tekst[a:b].split()) <= maks for a, b in wynik):
            return wynik

    # Ostatnia deska: tekst bez zdań i bez linii (np. jednolita sieczka OCR).
    slowa = list(re.finditer(r"\S+", tekst[b0:b1]))
    if len(slowa) <= cel:
        return [(b0, b1)]
    wynik, start = [], b0
    for i in range(cel, len(slowa), cel):
        ciecie = b0 + slowa[i].start()
        wynik.append((start, ciecie))
        start = ciecie
    wynik.append((start, b1))
    return wynik


def _wyglada_na_tabele(blok: str) -> bool:
    """Blok tabelaryczny: min. 3 krótkie linie, z których większość niesie liczby.

    Świadomie ostrożne: wolimy przeoczyć tabelę niż uznać akapit prozy za tabelę
    (fałszywa tabela scaliłaby sąsiednie akapity i rozdęła fragment).
    """
    linie = [ln for ln in blok.split("\n") if ln.strip()]
    if len(linie) < 3:
        return False
    krotkie = [ln for ln in linie if len(ln.split()) <= 12]
    if len(krotkie) < 3 or len(krotkie) / len(linie) < 0.6:
        return False
    z_liczba = sum(1 for ln in krotkie if RE_LICZBA.search(ln))
    return z_liczba / len(krotkie) >= 0.5


def _adres(tekst: str, poz: int) -> str:
    """Ostatni nagłówek sekcji PRZED pozycją — adres fragmentu (metadana).

    Gdy przed fragmentem nie ma ŻADNEGO nagłówka, zwracamy `«front»`, a nie pusty
    napis. To nie jest obejście kryterium NORMY (K8), tylko poprawka nazewnicza:
    „przed pierwszym rozdziałem" to ADRES ZNANY i prawdziwy, natomiast pusty napis
    znaczy „nie wiem", czyli co innego. Mieszanie tych dwóch stanów kazałoby traktować
    poprawnie zaadresowany front matter jak brak wiedzy.
    """
    ostatni = ""
    for m in RE_SEKCJA.finditer(tekst, 0, poz + 1):
        ostatni = m.group(0).strip()
    return ostatni or ADRES_FRONT


def kanon(tekst: str, cel: int = DOMYSLNY_CEL, maks: int = DOMYSLNY_MAX) -> list[Zakres]:
    """Podział KANONICZNY: rozłączny, posortowany, pokrywający [0, len).

    Skleja bloki aż do `cel` słów; blok tabelaryczny NIGDY nie jest rozrywany,
    nawet gdy przekracza cel — rozkrojona tabela jest bezużyteczna dla obu połówek.
    """
    if not tekst:
        return []
    wynik: list[Zakres] = []
    start: int | None = None
    slow = 0
    tabela_w_srodku = False

    # Blok większy niż twardy sufit rozbijamy PRZED sklejaniem — inaczej jeden
    # rozdział bez pustych linii połknąłby całą książkę (zmierzone na BIB-012).
    surowe: list[tuple[int, int]] = []
    for b0, b1 in _bloki(tekst):
        if len(tekst[b0:b1].split()) > maks:
            surowe.extend(_rozbij_wielki(tekst, b0, b1, cel, maks))
        else:
            surowe.append((b0, b1))

    for b0, b1 in surowe:
        blok = tekst[b0:b1]
        n = len(blok.split())
        tab = _wyglada_na_tabele(blok)
        if start is None:
            start, slow, tabela_w_srodku = b0, 0, False

        slow += n
        tabela_w_srodku = tabela_w_srodku or tab
        # domykamy fragment, gdy osiągnął cel — chyba że właśnie wciągamy tabelę
        # i nie przekroczyliśmy jeszcze twardego sufitu
        if slow >= cel and not (tab and slow < maks):
            wynik.append(Zakres(start, b1, _adres(tekst, start), tabela_w_srodku))
            start, slow, tabela_w_srodku = None, 0, False

    if start is not None:
        wynik.append(Zakres(start, len(tekst), _adres(tekst, start), tabela_w_srodku))

    # OKRUCHY: fragment krótszy niż PODLOGA nie niesie samodzielnego sensu — trafienie
    # w niego nie odpowiada na nic. Wchłaniamy go do sąsiada, bo SKLEJENIE sąsiadujących
    # zakresów zachowuje ciągłość, a więc i dowód SHA-256 (usunięcie by go złamało).
    # Wykryte przez NORMĘ (K5): 6 okruchów na 25 książkach — mało, ale niezerowo.
    scalone: list[Zakres] = []
    for z in wynik:
        if scalone and z.slowa(tekst) < PODLOGA_SLOW:
            p = scalone[-1]
            scalone[-1] = Zakres(p.start, z.koniec, p.adres, p.tabelaryczny or z.tabelaryczny)
        else:
            scalone.append(z)
    # okruch na SAMYM POCZĄTKU nie ma poprzednika — wchłania go następny
    if len(scalone) > 1 and scalone[0].slowa(tekst) < PODLOGA_SLOW:
        a, b = scalone[0], scalone[1]
        scalone[0:2] = [Zakres(a.start, b.koniec, b.adres, a.tabelaryczny or b.tabelaryczny)]
    return scalone


def okna(tekst: str, kan: list[Zakres], overlap: int = DOMYSLNY_OVERLAP) -> list[Zakres]:
    """Okna wyszukiwania = kanon rozszerzony wstecz o `overlap` słów sąsiada.

    Zakładka ratuje odpowiedzi leżące NA GRANICY fragmentów (klasa błędu, którą
    literatura testuje osobno). Nie dotyka kanonu, więc nie dotyka dowodu.

    NAPRAWIONE po recenzji 2026-07-29 (zmierzone: 1581 z 2492 okien, czyli 63,4%,
    zaczynało się w PÓŁ SŁOWA). Poprzednia wersja liczyła cofnięcie jako długość
    `" ".join(ogon[-overlap:])` — czyli tekstu po NORMALIZACJI białych znaków. W źródle
    stoją tam znaki nowej linii i wielokrotne spacje, więc offset był za mały i okno
    startowało w środku wyrazu, wpychając do indeksu śmieciowy token. Teraz cofamy się
    po REALNYCH pozycjach słów w oryginale, więc start ZAWSZE ląduje na granicy wyrazu.
    """
    if not kan:
        return []
    wynik = [kan[0]]
    for i in range(1, len(kan)):
        poprz, biez = kan[i - 1], kan[i]
        slowa = list(re.finditer(r"\S+", tekst[poprz.start:poprz.koniec]))
        nowy_start = (poprz.start + slowa[-overlap].start()
                      if len(slowa) > overlap else poprz.start)
        wynik.append(Zakres(nowy_start, biez.koniec, biez.adres, biez.tabelaryczny))
    return wynik


def podziel(tekst: str, cel: int = DOMYSLNY_CEL, maks: int = DOMYSLNY_MAX,
            overlap: int = DOMYSLNY_OVERLAP) -> Podzial:
    kan = kanon(tekst, cel, maks)
    return Podzial(
        zrodlo_sha=hashlib.sha256(tekst.encode("utf-8")).hexdigest(),
        kanon=kan,
        okna=okna(tekst, kan, overlap),
    )


def zrekonstruuj(zrodlo: str, kan: list[Zakres]) -> str:
    """Odtwarza dokument z KANONU. Gdy podział jest poprawny — zwraca źródło."""
    return "".join(zrodlo[z.start:z.koniec] for z in kan)


def dowod_bezstratnosci(zrodlo: str, p: Podzial) -> dict:
    """TWIERDZENIE, nie obietnica: czy z fragmentów odzyskujemy dokument co do bajtu.

    Zwraca też powody porażki — miernik, który mówi tylko „nie", jest bezużyteczny
    przy naprawie (nasza własna lekcja: NIEZNANE to wynik, nie zero).
    """
    odt = zrekonstruuj(zrodlo, p.kanon)
    sha_odt = hashlib.sha256(odt.encode("utf-8")).hexdigest()
    rozlaczne = all(p.kanon[i].koniec == p.kanon[i + 1].start
                    for i in range(len(p.kanon) - 1))
    pokrycie = (not p.kanon) or (p.kanon[0].start == 0 and p.kanon[-1].koniec == len(zrodlo))
    powody = []
    if not rozlaczne:
        powody.append("zakresy kanonu nie są rozłączne/ciągłe")
    if not pokrycie:
        powody.append("kanon nie pokrywa całego dokumentu")
    if sha_odt != p.zrodlo_sha:
        powody.append(f"SHA-256 rozjazd: {sha_odt[:12]} != {p.zrodlo_sha[:12]}")
    return {
        "bezstratny": not powody,
        "sha_zrodla": p.zrodlo_sha,
        "sha_rekonstrukcji": sha_odt,
        "znakow_zrodla": len(zrodlo),
        "znakow_odtworzonych": len(odt),
        "fragmentow_kanonu": len(p.kanon),
        "powody": powody,
    }


def porownaj_ze_starym(tekst: str) -> dict:
    """Zestawia REDDITORA ze starą fragmentacją NA TYCH SAMYCH danych (Prawo XVI)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ekstraktor import podziel_na_chunki

    stare = podziel_na_chunki(tekst)
    p = podziel(tekst)
    d = dowod_bezstratnosci(tekst, p)
    stare_txt = " ".join(stare)
    return {
        "stare_chunkow": len(stare),
        "stare_linii_zachowanych": sum(c.count("\n") for c in stare),
        "stare_znakow": len(stare_txt),
        "stare_bezstratne": hashlib.sha256(stare_txt.encode()).hexdigest() == p.zrodlo_sha,
        "redditor_fragmentow": len(p.kanon),
        "redditor_linii_zachowanych": sum(z.tekst(tekst).count("\n") for z in p.kanon),
        "redditor_tabel_nierozerwanych": sum(1 for z in p.kanon if z.tabelaryczny),
        "redditor_bezstratny": d["bezstratny"],
        "linii_w_zrodle": tekst.count("\n"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="REDDITOR — fragmentacja z dowodem bezstratności")
    ap.add_argument("--limit", type=int, default=10, help="ile książek zbadać")
    ap.add_argument("--cel", type=int, default=DOMYSLNY_CEL)
    a = ap.parse_args(argv)

    pliki = sorted(CACHE.glob("BIB-*.txt"))[:a.limit]
    if not pliki:
        print(f"REDDITOR: brak plików w {CACHE}", file=sys.stderr)
        return 2

    ok = 0
    lin_stare = lin_nowe = lin_zrodlo = 0
    print(f"🧩 REDDITOR — dowód bezstratności na {len(pliki)} książkach\n")
    for i, p in enumerate(pliki, 1):
        t = p.read_text(encoding="utf-8", errors="replace")
        w = porownaj_ze_starym(t)
        ok += 1 if w["redditor_bezstratny"] else 0
        lin_stare += w["stare_linii_zachowanych"]
        lin_nowe += w["redditor_linii_zachowanych"]
        lin_zrodlo += w["linii_w_zrodle"]
        znak = "✅" if w["redditor_bezstratny"] else "🔴"
        print(f"  [{i}/{len(pliki)}] {znak} {p.name.split('__')[0][:42]:44s} "
              f"frag={w['redditor_fragmentow']:>4} tabel={w['redditor_tabel_nierozerwanych']:>3} "
              f"linie {w['linii_w_zrodle']:>6}→{w['redditor_linii_zachowanych']:<6} "
              f"(stare→{w['stare_linii_zachowanych']})", flush=True)

    print()
    print(f"   DOWÓD SHA-256: {ok}/{len(pliki)} książek odtworzonych CO DO BAJTU")
    print(f"   struktura: źródło {lin_zrodlo} linii | REDDITOR {lin_nowe} | stary chunker {lin_stare}")
    return 0 if ok == len(pliki) else 1


if __name__ == "__main__":
    raise SystemExit(main())
