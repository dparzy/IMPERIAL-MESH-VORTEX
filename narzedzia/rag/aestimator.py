#!/usr/bin/env python3
"""
⚖️ AESTIMATOR — Szacownik Wierności Biblioteki: mierzy, ILE GINIE po drodze
   z książki do indeksu RAG.

Rzymski *aestimator* = urzędnik szacujący realną wartość dobra (od `aestimare` —
oceniać, wyceniać). Tutaj: organ, który wycenia, jaka część KSIĄŻKI faktycznie
dociera do wyszukiwarki — i nazywa po imieniu to, co przepada.

POWÓD POWSTANIA (rozkaz Cezara 2026-07-29: „musimy być pewni, czy wszystkie dane
zostały najlepiej pobrane"): QUAESITOR mierzy, czy wyszukiwarka ZNAJDUJE. To za mało.
Wyszukiwarka nie znajdzie tego, czego w indeksie NIE MA — a pomiar trafności na
okrojonym korpusie da wysoką notę i fałszywy spokój. AESTIMATOR pyta pytanie
wcześniejsze i ważniejsze: **czy to, czego szukamy, w ogóle tam dotarło?**

TRZY BRAMY, NA KTÓRYCH GINIE TREŚĆ — i każda ginie inaczej:

    KSIĄŻKA  ──(1) EKSTRAKCJA──▶  tekst_cache  ──(2) FRAGMENTACJA──▶  chunki  ──(3) INDEKS──▶ FTS
             (calibre/pdfminer)                  (podziel_na_chunki)

    (1) EKSTRAKCJA gubi to, co jest OBRAZEM, nie tekstem: wykresy, a w książkach
        technicznych bardzo często także LISTINGI KODU i złożone wzory. Ginie
        bezpowrotnie i cicho — zostaje sam podpis („SNIPPET 18.1 …"), po którym
        nikt nie pozna, że treści zabrakło.
    (2) FRAGMENTACJA gubi STRUKTURĘ: `podziel_na_chunki` robi `" ".join(tekst.split())`,
        co kasuje 100% znaków nowej linii. Słowa przeżywają, UKŁAD nie. Tabela
        przestaje być tabelą i staje się ciągiem słów, w którym nie da się
        odtworzyć, która wartość należy do którego wiersza.
    (3) INDEKS gubi to, czego nikt nie zaindeksował (mierzy osobno `quaesitor`/`katalog`).

DLACZEGO ROZRÓŻNIENIE (1) vs (2) JEST SEDNEM, A NIE PEDANTERIĄ:
    strata z (2) jest ODWRACALNA — tekst mamy, wystarczy ciąć mądrzej;
    strata z (1) jest NIEODWRACALNA bez ponownej ekstrakcji ze źródła.
Mylenie ich prowadzi prosto do zbudowania pięknego chunkera nad treścią, której
w pliku nigdy nie było. Dlatego AESTIMATOR raportuje je w OSOBNYCH kolumnach.

UCZCIWOŚĆ MIARY (inaczej przyrząd kłamie — nasza własna lekcja):
- „Zapowiedziane" liczymy z PODPISÓW w tekście (SNIPPET/Table/Figure), bo tylko
  one mówią, ile autor OBIECAŁ. Różnica obiecane−dostarczone to strata.
- Podpisy ze SPISU TREŚCI są odsiewane pozycją w dokumencie: pierwsze procenty
  pliku to front matter, gdzie podpisy stoją listą bez treści. Zliczanie ich jako
  „straty" zawyżyłoby wynik — sprawdzone na BIB-007, gdzie 14 z 24 trafień „Table"
  siedziało w spisie treści.
- Miarą śmieciowości OCR jest UDZIAŁ UNIKALNYCH SŁÓW, nie długość pliku
  (lekcja z audytu biblioteki: skan potrafi dać megabajty powtarzalnej sieczki).

Organ NIE zmienia ani jednego bajtu w bazie ani w cache — wyłącznie mierzy.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_TU = Path(__file__).resolve().parent
if str(_TU) not in sys.path:
    sys.path.insert(0, str(_TU))

from ekstraktor import podziel_na_chunki  # noqa: E402

KORZEN = Path(__file__).resolve().parents[2]
CACHE = KORZEN / "bibliotheca_ulpia" / "dane" / "tekst_cache"
MIGAWKA = KORZEN / "bibliotheca_ulpia" / "dane" / "aestimator_migawka.json"

# Front matter: podpisy z listy rysunków/tabel stoją w pierwszych procentach pliku.
# 8% dobrane z zapasem wobec zmierzonego 3.0-3.1% dla BIB-007 (spis treści AFML).
PROG_FRONT_MATTER = 0.08

# NAGŁÓWEK listingu, nie wzmianka o nim. Różnica skalibrowana na próbce ręcznej
# (2026-07-29): „SNIPPET 2.1 THE MARCENKO–PASTUR PDF" to nagłówek — po nim MA stać kod;
# „Snippet 9.1 lists function clfHyperFit" to zdanie prozy — kodu tam nie ma i być nie
# powinno. Wersja bezwzględna na wielkość liter liczyła prozę jako obietnicę kodu
# i ZAWYŻAŁA stratę 259 vs 96 (2,7×). Wersaliki tytułu są jedynym sygnałem, który je
# rozdziela, i dlatego są w tym wzorcu obowiązkowe.
RE_SNIPPET = re.compile(r"\bSNIPPET\s+\d+[.\d]*\s+[A-Z][A-Z \-–—,'()]{4,}")
RE_TABELA = re.compile(r"\b(?:TABLE|Tabela)\s+\d+\.\d+")
RE_RYSUNEK = re.compile(r"\b(?:FIGURE|Rysunek)\s+\d+\.\d+", re.IGNORECASE)
# Ślady ŻYWEGO kodu. `return` i gołe `import` USUNIĘTE po pomiarze: w książkach
# finansowych „return" znaczy „stopa zwrotu" i dawało 6,2% fałszywek na czystej prozie
# (600 losowych okien). Wersja poniżej: 1,5%, a i te trafienia okazały się realnym
# kodem wplecionym w tekst — czyli przyrząd nie zawyża w tę stronę.
RE_KOD = re.compile(
    r"\bdef\s+\w+\s*\(|\bimport\s+(?:numpy|pandas|scipy|sklearn|matplotlib)\b|"
    r"\bfrom\s+\w+\s+import\b|\bpd\.\w+|\bnp\.\w+|\bself\.\w+|"
    r"\bprint\s*\(|\.append\s*\(|\blambda\s+\w+\s*:"
)
RE_MATH = re.compile(r"[∑∫√±≈≠≤≥∂ΔσμαβγθλΩ∞×÷]|\\frac|\\sum|\\int")


def _po_front_matter(tekst: str, wzor: re.Pattern) -> list[int]:
    """Pozycje trafień wzorca POZA front matter (spis treści zawyżałby stratę)."""
    n = max(1, len(tekst))
    return [m.start() for m in wzor.finditer(tekst)
            if m.start() / n > PROG_FRONT_MATTER]


def _ma_kod_po(tekst: str, poz: int, okno: int = 600) -> bool:
    """Czy po podpisie listingu stoi cokolwiek, co wygląda na kod?"""
    return bool(RE_KOD.search(tekst[poz:poz + okno]))


def _ma_tresc_po(tekst: str, poz: int, okno: int = 500, min_slow: int = 12) -> bool:
    """Czy po podpisie tabeli stoi treść (komórki), czy tylko biały szum?"""
    ogon = tekst[poz:poz + okno]
    # pomijamy sam podpis — liczymy słowa PO nim
    ogon = ogon.split("\n", 1)[1] if "\n" in ogon else ogon
    return len(ogon.split()) >= min_slow


def zmierz_ksiazke(sciezka: Path) -> dict:
    """Wycena jednej książki. Zwraca surowe liczby — werdykt osobno (Prawo I)."""
    t = sciezka.read_text(encoding="utf-8", errors="replace")
    slowa = t.split()
    n_slow = len(slowa)
    unikalne = len({w.lower() for w in slowa})

    chunki = podziel_na_chunki(t)
    # BEZSTRATNOŚĆ (2): czy każde słowo oryginału przeżyło fragmentację?
    zbior_zrodla = set(slowa)
    zbior_chunkow = set(" ".join(chunki).split()) if chunki else set()
    zgubione = zbior_zrodla - zbior_chunkow

    sn = _po_front_matter(t, RE_SNIPPET)
    sn_z_kodem = sum(1 for p in sn if _ma_kod_po(t, p))
    tab = _po_front_matter(t, RE_TABELA)
    tab_z_trescia = sum(1 for p in tab if _ma_tresc_po(t, p))
    rys = _po_front_matter(t, RE_RYSUNEK)

    return {
        "ksiazka": sciezka.name.split("__")[0],
        "slowa": n_slow,
        "unikalne": unikalne,
        "udzial_unikalnych": round(unikalne / max(1, n_slow), 4),
        "linie_w_cache": t.count("\n"),
        "linie_po_fragmentacji": sum(c.count("\n") for c in chunki),
        "chunkow": len(chunki),
        "slow_zgubionych_przy_cieciu": len(zgubione),
        "listingi_zapowiedziane": len(sn),
        "listingi_z_kodem": sn_z_kodem,
        "tabele_zapowiedziane": len(tab),
        "tabele_z_trescia": tab_z_trescia,
        "rysunki_zapowiedziane": len(rys),
        "znaki_matematyczne": len(RE_MATH.findall(t)),
    }


def werdykt(w: dict) -> tuple[str, list[str]]:
    """Nazywa straty. Zwraca (werdykt, powody). NIEZNANE to wynik, nie zero."""
    powody: list[str] = []
    if w["slowa"] < 500:
        return "PUSTY", ["mniej niż 500 słów — ekstrakcja praktycznie nie zadziałała"]
    if w["udzial_unikalnych"] < 0.02:
        powody.append(f"sieczka OCR (unikalnych {w['udzial_unikalnych']:.1%})")

    zap, zkod = w["listingi_zapowiedziane"], w["listingi_z_kodem"]
    if zap >= 3 and zkod / max(1, zap) < 0.25:
        powody.append(f"listingi kodu ZGUBIONE w ekstrakcji ({zkod}/{zap} ma kod)")

    tz, tt = w["tabele_zapowiedziane"], w["tabele_z_trescia"]
    if tz >= 3 and tt / max(1, tz) < 0.5:
        powody.append(f"tabele bez treści ({tt}/{tz})")

    if w["linie_w_cache"] > 200 and w["linie_po_fragmentacji"] == 0:
        powody.append("100% struktury linii skasowane przez fragmentację")

    if w["slow_zgubionych_przy_cieciu"] > 0:
        powody.append(f"{w['slow_zgubionych_przy_cieciu']} słów NIE trafiło do chunków")

    if not powody:
        return "CZYSTA", []
    ciezkie = any("ZGUBIONE" in p or "sieczka" in p or "NIE trafiło" in p for p in powody)
    return ("USZKODZONA" if ciezkie else "OKROJONA"), powody


def oceń(limit: int | None = None, od: int = 0) -> dict:
    """Wycenia korpus etapami (Prawo XXIV: pasek postępu, wynik zapisywany)."""
    pliki = sorted(CACHE.glob("BIB-*.txt"))[od:]
    if limit:
        pliki = pliki[:limit]
    n = len(pliki)
    wyniki = []
    for i, p in enumerate(pliki, 1):
        w = zmierz_ksiazke(p)
        w["werdykt"], w["powody"] = werdykt(w)
        wyniki.append(w)
        print(f"  [{i}/{n}] {w['ksiazka'][:44]:46s} {w['werdykt']}", flush=True)
    return {"zbadanych": len(wyniki), "ksiazki": wyniki}


def raport(dane: dict) -> str:
    ks = dane["ksiazki"]
    if not ks:
        return "⚖️ AESTIMATOR — brak książek do wyceny."
    licz: dict[str, int] = {}
    for k in ks:
        licz[k["werdykt"]] = licz.get(k["werdykt"], 0) + 1

    L = ["⚖️ AESTIMATOR — wierność biblioteki cyfrowej", ""]
    L.append(f"   zbadanych książek: {len(ks)}")
    for w in ("CZYSTA", "OKROJONA", "USZKODZONA", "PUSTY"):
        if w in licz:
            L.append(f"   {w:12s} {licz[w]:>4}")

    zap = sum(k["listingi_zapowiedziane"] for k in ks)
    zkod = sum(k["listingi_z_kodem"] for k in ks)
    tz = sum(k["tabele_zapowiedziane"] for k in ks)
    tt = sum(k["tabele_z_trescia"] for k in ks)
    rys = sum(k["rysunki_zapowiedziane"] for k in ks)
    lin = sum(k["linie_w_cache"] for k in ks)
    linpo = sum(k["linie_po_fragmentacji"] for k in ks)

    L += ["", "   STRATA (1) EKSTRAKCJA — nieodwracalna bez ponownego czytania źródła:"]
    L.append(f"      listingi kodu: {zkod}/{zap} zapowiedzianych ma treść"
             + (f"  → ZGUBIONE {zap - zkod}" if zap else ""))
    L.append(f"      tabele:        {tt}/{tz} zapowiedzianych ma treść")
    L.append(f"      rysunki:       {rys} podpisów (treść wykresu to obraz — nigdy nie było jej w tekście)")
    L += ["", "   STRATA (2) FRAGMENTACJA — odwracalna, wystarczy ciąć mądrzej:"]
    L.append(f"      linie struktury: {lin} w cache → {linpo} po fragmentacji")

    uszk = [k for k in ks if k["werdykt"] in ("USZKODZONA", "PUSTY")]
    if uszk:
        L += ["", f"   🚨 NAJCIĘŻEJ POSZKODOWANE ({len(uszk)}):"]
        for k in sorted(uszk, key=lambda x: -x["listingi_zapowiedziane"])[:10]:
            L.append(f"      • {k['ksiazka'][:46]:48s} {'; '.join(k['powody'])[:90]}")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="AESTIMATOR — wierność biblioteki cyfrowej")
    ap.add_argument("--limit", type=int, default=None, help="ile książek (etapami)")
    ap.add_argument("--od", type=int, default=0, help="od której książki (wznawianie)")
    ap.add_argument("--zapisz", action="store_true", help="zapisz migawkę JSON")
    a = ap.parse_args(argv)

    if not CACHE.exists():
        print(f"⚖️ AESTIMATOR: brak katalogu {CACHE}", file=sys.stderr)
        return 2
    dane = oceń(limit=a.limit, od=a.od)
    print()
    print(raport(dane))
    if a.zapisz:
        MIGAWKA.write_text(json.dumps(dane, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n   migawka: {MIGAWKA.relative_to(KORZEN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
