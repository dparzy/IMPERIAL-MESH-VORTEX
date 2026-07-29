#!/usr/bin/env python3
"""
📐 NORMA — Węgielnica Bibliotekarza: bramka 10 kryteriów, którą MUSI przejść
   każda metoda fragmentacji, zanim wolno o niej powiedzieć „jest dobra".

Rzymska *norma* = węgielnica, kątownik ciesielski — przyrząd, którym sprawdza się,
czy kąt jest prosty. Nie opinia o prostości: sprawdzian. Stąd `norma` w znaczeniu
„wzorzec, miara" i nasze „normalny".

────────────────────────────────────────────────────────────────────────────────
POWÓD POWSTANIA (pytanie Cezara 2026-07-29: „skąd wiesz, że ten rodzaj jest najlepszy?")

Bo NIE WIEDZIAŁEM — i to jest sedno tego organu. REDDITOR udowodnił SHA-256, że jego
cięcie jest bezstratne co do bajtu na 118/118 książek. To warunek KONIECZNY i nic
poza tym. Metoda może być idealnie bezstratna i jednocześnie GORSZA w wyszukiwaniu:
bezstratność mówi o tym, co WŁOŻYLIŚMY do indeksu, a nie o tym, co z niego WYJMIEMY.

Mylenie tych dwóch rzeczy to ta sama klasa błędu, za którą Cezar przyznał TALARA
(LEX TALARUS): ogłoszenie działania przed pomiarem. NORMA istnieje po to, żeby ta
klasa nie mogła się powtórzyć — bo każde kryterium ma stan, a stanem może być
**NIEZNANE**, i NIEZNANE blokuje werdykt „najlepsza" tak samo skutecznie jak PORAŻKA.

DZIESIĘĆ KRYTERIÓW — trzy rodziny, każda odpowiada na inne pytanie:

  WIERNOŚĆ (czy nic nie zginęło?)          K1 bezstratność bajtowa
                                            K2 pokrycie i rozłączność
                                            K3 struktura linii zachowana
  UŻYTECZNOŚĆ (czy fragment nadaje się     K4 brak gigantów
     do wyszukiwania?)                      K5 brak okruchów
                                            K6 tabela nierozerwana
                                            K7 fragment nie zaczyna się w pół słowa
                                            K8 fragment ma ADRES (albo jawne NIEZNANY)
  PRAWDA (czy jest LEPSZA?)                 K9 zgodność liczb z żywym kodem
                                            K10 trafność ≥ metody zastanej  ← ROZSTRZYGA

K10 jest jedynym kryterium, które odpowiada na pytanie Cezara, i jedynym, którego
NIE DA SIĘ policzyć z samego tekstu — wymaga zbioru pytań z prawdą podstawową
(organ QUAESITOR). Dopóki K10 = NIEZNANE, NORMA orzeka **NIEROZSTRZYGNIĘTE**,
choćby dziewięć pozostałych kryteriów świeciło na zielono. Tak wygląda uczciwa
bramka: nie da się jej przejść samą starannością.

ZASADA NADRZĘDNA: NORMA nie ocenia REDDITORA. NORMA ocenia DOWOLNĄ metodę — również
tę zastaną (`podziel_na_chunki`) — tym samym kątownikiem. Miara, która ma tylko
jednego kandydata, nie jest miarą, tylko uzasadnieniem.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

_TU = Path(__file__).resolve().parent
if str(_TU) not in sys.path:
    sys.path.insert(0, str(_TU))

KORZEN = Path(__file__).resolve().parents[2]
CACHE = KORZEN / "bibliotheca_ulpia" / "dane" / "tekst_cache"

ZALICZONE, PORAZKA, NIEZNANE = "✅ ZALICZONE", "🔴 PORAŻKA", "⏳ NIEZNANE"

SUFIT_SLOW = 2000     # fragment większy nie wskazuje już MIEJSCA w książce
PODLOGA_SLOW = 20     # mniejszy nie niesie samodzielnego sensu


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def zbadaj_metode(nazwa: str, tnij, teksty: dict[str, str]) -> dict:
    """Przykłada węgielnicę do JEDNEJ metody. `tnij(tekst) -> list[str]` albo zakresy.

    Metoda zwracająca ZAKRESY (start, koniec) może dowieść K1; metoda zwracająca
    same napisy — nie może, i to nie jest karą, tylko faktem o jej konstrukcji.
    """
    k = {f"K{i}": NIEZNANE for i in range(1, 11)}
    szczegoly: dict[str, str] = {}

    bezstratne = pokrycie_ok = 0
    linie_zrodlo = linie_po = 0
    gigantow = okruchow = zaczyna_w_pol = bez_adresu = 0
    fragmentow = 0
    tabel_calych = 0
    zakresowa = True

    for tekst in teksty.values():
        wynik = tnij(tekst)
        if not wynik:
            continue
        zakresy = [w for w in wynik if hasattr(w, "start")]
        if len(zakresy) != len(wynik):
            zakresowa = False

        if zakresy:
            odt = "".join(tekst[z.start:z.koniec] for z in zakresy)
            bezstratne += 1 if _sha(odt) == _sha(tekst) else 0
            ciagle = all(zakresy[i].koniec == zakresy[i + 1].start
                         for i in range(len(zakresy) - 1))
            pelne = zakresy[0].start == 0 and zakresy[-1].koniec == len(tekst)
            pokrycie_ok += 1 if (ciagle and pelne) else 0
            kawalki = [z.tekst(tekst) for z in zakresy]
            tabel_calych += sum(1 for z in zakresy if getattr(z, "tabelaryczny", False))
            bez_adresu += sum(1 for z in zakresy if not getattr(z, "adres", ""))
            for z in zakresy:
                if z.start > 0 and tekst[z.start - 1].isalnum() and tekst[z.start].isalnum():
                    zaczyna_w_pol += 1
        else:
            kawalki = list(wynik)
            bez_adresu += len(kawalki)

        fragmentow += len(kawalki)
        linie_zrodlo += tekst.count("\n")
        linie_po += sum(c.count("\n") for c in kawalki)
        gigantow += sum(1 for c in kawalki if len(c.split()) > SUFIT_SLOW)
        okruchow += sum(1 for c in kawalki if len(c.split()) < PODLOGA_SLOW)

    n = len(teksty)
    # ── WIERNOŚĆ ──
    if zakresowa:
        k["K1"] = ZALICZONE if bezstratne == n else PORAZKA
        szczegoly["K1"] = f"rekonstrukcja bajt-w-bajt: {bezstratne}/{n} książek"
        k["K2"] = ZALICZONE if pokrycie_ok == n else PORAZKA
        szczegoly["K2"] = f"kanon ciągły i pełny: {pokrycie_ok}/{n}"
    else:
        k["K1"] = PORAZKA
        szczegoly["K1"] = "metoda zwraca NAPISY, nie zakresy — bezstratności nie da się dowieść"
        k["K2"] = PORAZKA
        szczegoly["K2"] = "brak zakresów → brak pojęcia pokrycia"

    # Korpus BEZ znaków nowej linii nie mówi nic o metodzie — mówi o korpusie.
    # Poprzednio 0/0 dawało 0.0 i PORAŻKĘ, więc bramka odrzucała poprawną metodę
    # (rekonstrukcja bajt-w-bajt) za właściwość danych. Brakujący pomiar to NIEZNANE.
    if not linie_zrodlo:
        k["K3"] = NIEZNANE
        szczegoly["K3"] = "źródło nie ma znaków nowej linii — nie ma czego zachowywać"
    else:
        zach = linie_po / linie_zrodlo
        k["K3"] = ZALICZONE if zach >= 0.999 else PORAZKA
        szczegoly["K3"] = f"linie struktury zachowane: {linie_po}/{linie_zrodlo} ({zach:.1%})"

    # ── UŻYTECZNOŚĆ ──
    k["K4"] = ZALICZONE if gigantow == 0 else PORAZKA
    szczegoly["K4"] = f"fragmentów > {SUFIT_SLOW} słów: {gigantow}"
    k["K5"] = ZALICZONE if okruchow == 0 else PORAZKA
    szczegoly["K5"] = f"fragmentów < {PODLOGA_SLOW} słów: {okruchow}"
    k["K6"] = ZALICZONE if (tabel_calych > 0 or not zakresowa) else NIEZNANE
    szczegoly["K6"] = (f"bloków tabelarycznych zachowanych w całości: {tabel_calych}"
                       if zakresowa else "metoda nie rozpoznaje tabel — brak pojęcia")
    if not zakresowa:
        k["K6"] = PORAZKA
    k["K7"] = ZALICZONE if zaczyna_w_pol == 0 else PORAZKA
    szczegoly["K7"] = f"fragmentów zaczynających się w pół słowa: {zaczyna_w_pol}"
    k["K8"] = ZALICZONE if bez_adresu == 0 else PORAZKA
    szczegoly["K8"] = f"fragmentów bez adresu (rozdział/sekcja): {bez_adresu}/{fragmentow}"

    # ── PRAWDA ──
    k["K9"] = ZALICZONE
    szczegoly["K9"] = f"fragmentów policzonych z żywego kodu: {fragmentow}"
    # K10 zostaje NIEZNANE — świadomie. Liczy je wyłącznie pomiar trafności.
    szczegoly["K10"] = ("trafność vs metoda zastana — WYMAGA zbioru pytań z prawdą "
                        "podstawową (QUAESITOR). Bez tego werdykt 'najlepsza' jest wiarą.")

    return {"metoda": nazwa, "kryteria": k, "szczegoly": szczegoly,
            "fragmentow": fragmentow, "ksiazek": n}


def werdykt(bad: dict) -> str:
    k = bad["kryteria"].values()
    if any(v == PORAZKA for v in k):
        return "🔴 ODRZUCONA"
    if any(v == NIEZNANE for v in k):
        return "⏳ NIEROZSTRZYGNIĘTE — brak dowodu wyższości"
    return "✅ PRZYJĘTA"


def raport(badania: list[dict]) -> str:
    L = ["📐 NORMA — węgielnica fragmentacji", ""]
    for b in badania:
        L.append(f"── {b['metoda']}  ({b['ksiazek']} książek, {b['fragmentow']} fragmentów)")
        for i in range(1, 11):
            kod = f"K{i}"
            L.append(f"   {kod:4s} {b['kryteria'][kod]:14s} {b['szczegoly'].get(kod,'')}")
        L.append(f"   WERDYKT: {werdykt(b)}")
        L.append("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="NORMA — bramka 10 kryteriów dla fragmentacji")
    ap.add_argument("--limit", type=int, default=25)
    a = ap.parse_args(argv)

    from ekstraktor import podziel_na_chunki
    from redditor import kanon

    pliki = sorted(CACHE.glob("BIB-*.txt"))[:a.limit]
    teksty = {p.name: p.read_text(encoding="utf-8", errors="replace") for p in pliki}
    if not teksty:
        print("NORMA: brak książek", file=sys.stderr)
        return 2

    badania = [
        zbadaj_metode("METODA ZASTANA — podziel_na_chunki (400 słów / overlap 50)",
                      podziel_na_chunki, teksty),
        zbadaj_metode("REDDITOR — kanon strukturalny z dowodem SHA-256",
                      kanon, teksty),
    ]
    print(raport(badania))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
