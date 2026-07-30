"""🔍 DISCRIMINATOR — orzeka, czy SKUPISKO neuronów to naprawdę redundancja.

Rzymski *discriminator* to ten, kto ROZDZIELA i ROZRÓŻNIA. Organ robi jedno: bierze
skupiska wskazane przez `rejestr.raport_mechanizmow()` i pyta o każde z nich pomiarem —
czy neurony o tej samej etykiecie `(KATEGORIA, MECHANIZM)` naprawdę niosą ten sam sygnał,
czy tylko dzielą nazwę szufladki.

POWÓD ISTNIENIA (alarm Prawa XV, zmierzony 2026-07-30, pozycja F0 ROADMAP):
`raport_mechanizmow()` liczy `skupiska_redundancji` — **17 skupisk** (m.in. `T/trend` 8
neuronów, `M/trend` 6, `R/regime` 6, `R/mean_rev` 5 czyli całe PSY). `grep` po całym
repozytorium dawał DWA trafienia: własną definicję i test na obecność klucza. Nikt tego
nie czytał.

ALE PRAWDZIWA LUKA BYŁA GŁĘBSZA NIŻ „nikt nie drukuje listy" (rozpoznanie 2026-07-31):
własny docstring `raport_mechanizmow` mówi wprost, że skupisko to **kandydat do pomiaru
korelacji (Prawo XVI)**. Przyrząd do tego pomiaru istnieje (`korelacja_pearson`), ścieżka
bary→Brama→`interpretuj` też — a mimo to **kandydaci nigdy nie trafiali pod przyrząd**.
Jedyny taki pomiar w historii Imperium (`narzedzia/dekorelacja_w322.py`) był skryptem
jednorazowym, zahardkodowanym na 5 neuronów i jedną parę. Lista bez werdyktu i przyrząd
bez wejścia to ta sama utrata potencjału, tylko widziana z dwóch stron.

CZEGO ŚWIADOMIE NIE ROBI:
  • ❌ Nie wycisza ani nie scala niczego. Prawo XVI zabrania odrzucania za podobieństwo —
    organ dostarcza LICZBĘ, decyzja o składzie roju należy do Cezara.
  • ❌ Nie twierdzi, że wysoka korelacja = zbędność. Dwa neurony mogą być skorelowane
    i nieść różną informację w ogonach; dlatego werdykt nazywa się KANDYDAT, nie WYROK.
  • ❌ Nie liczy korelacji sam — używa `korelacja_pearson` z `diagnostyka_korelacji`
    (Prawo XVI: jedno źródło prawdy, kopia rozjechałaby się z produkcją).
  • ❌ Nie udaje pomiaru tam, gdzie go nie ma: neuron o ZEROWEJ WARIANCJI (stały głos)
    nie dostaje korelacji `0.0`, tylko osobny werdykt CISZA_W_POMIARZE. Para z takim
    neuronem jest NIEROZSTRZYGNIĘTA, nie zielona.
  • ❌ **Nie nazywa ciszy martwym głosem** — i to jest granica zmierzona, nie założona.
    Pierwszy bieg (2026-07-31) zgłosił `K-03` i `K-04` jako stały głos. Sprawdzenie:
    to neurony ALT-DANYCH (przepływ stablecoinów, siła dolara) z kampanii Tier-1, a ten
    pomiar karmi rój WYŁĄCZNIE świecami OHLCV z CSV. Neuron, któremu nie podano jego
    źródła, MUSI milczeć — cisza jest wtedy poprawnym zachowaniem, nie wadą. Oskarżenie
    o „martwy głos" (Prawo XV) byłoby fałszywym alarmem generowanym przez ograniczenie
    PRZYRZĄDU, nie przez stan Imperium.
    ⚠️ LUKA ODSŁONIĘTA PRZY OKAZJI: neurony **nie deklarują w kodzie, jakich danych
    wymagają** (brak pola typu `WYMAGA`/`ZRODLO` — sprawdzone na K-03, K-04, X-05), więc
    organ NIE MOŻE programowo odróżnić „milczy z braku wejścia" od „milczy, bo zepsuty".
    Zapisane jako dług, nie zamiecione: werdykt nazywa stan faktyczny (CISZA), a nie
    domniemaną przyczynę.

CO POKAZAŁ PIERWSZY POMIAR (BTCUSDT 4h, 2026-07-31) — także tam, gdzie zaprzeczył tezie:
  • **17 skupisk, 125 par, JEDEN kandydat do scalenia:** `X-05 ↔ XII-02`, r=0,82.
    Podejrzenie o masową redundancję NIE potwierdziło się: największe skupisko `T/trend`
    (8 neuronów, 28 par) ma 17 par poniżej progu dywersyfikacji, czyli jest zdrowe.
  • **Wynik jest stabilny na próbce:** powtórka na 2640 krokach zamiast 440 (6× więcej
    danych) dała ten sam jedyny kandydat, r=0,81. Nie jest to artefakt krótkiego okna.
  • **27 z 66 neuronów milczy** — i to NIE jest brak historii (patrz punkt wyżej: 6×
    dłuższy bieg nic nie zmienił). Przyczyna ustalona z KODU, nie z domysłu: `RADAR-01`
    czyta klucz `BTC_TREND`, którego Brama nie zna przy karmieniu POJEDYNCZĄ parą —
    neuron sam mówi „Brak kontekstu BTC (radar milczy)". Milczą więc dwie legalne rodziny:
    neurony ALT-DANYCH (K-03/K-04, NEWS-*, AUG-01, PSY-05) i neurony KONTEKSTU
    MIĘDZYRYNKOWEGO (RADAR-*), którym ten pomiar z założenia nie podaje wejścia.
  • **Czego więc NIE WIEMY:** dla części milczących (SMC-*, OC-*, PSY-01..04, Z-05/Z-06)
    przyczyna nie została sprawdzona po kolei. Rozstrzygnie dopiero bieg karmiony
    adapterami i wieloma parami — do tego czasu ich cisza jest NIEZMIERZONA, nie zielona.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from imperium.legiony.diagnostyka_korelacji import korelacja_pearson
from imperium.legiony.rejestr import raport_mechanizmow, wszystkie_neurony

# Progi Prawa XVI — te same liczby, co w `raport_dekorelacji`, świadomie nie inne.
PROG_REDUNDANCJI = 0.80
PROG_DYWERSYFIKACJI = 0.20


def sygnal_na_liczbe(sygnal: Any) -> float:
    """SygnalNeuronu → liczba w [-1, 1]. LONG dodatni, SHORT ujemny, NEUTRAL zero.

    Neurony DEFENSYWNE (np. Amihud) głosują tłumieniem: kierunek NEUTRAL, ale niezerowa
    `pewnosc_przeciwnika`. Gdyby czytać sam kierunek, ich głos byłby stale zerowy i organ
    ogłaszałby martwy głos tam, gdzie neuron pracuje — dlatego tłumienie wchodzi jako
    wartość ujemna (zachowane z `dekorelacja_w322.py`, gdzie zostało wypracowane).
    """
    kierunek = getattr(sygnal, "kierunek", "NEUTRAL")
    pewnosc = float(getattr(sygnal, "pewnosc", 0.0) or 0.0)
    znak = 1 if kierunek == "LONG" else (-1 if kierunek == "SHORT" else 0)
    wartosc = znak * pewnosc
    if wartosc == 0:
        przeciwnik = float(getattr(sygnal, "pewnosc_przeciwnika", 0.0) or 0.0)
        if przeciwnik > 0:
            wartosc = -przeciwnik
    return wartosc


def skupiska() -> Dict[str, List[str]]:
    """Kandydaci z rejestru: {'KATEGORIA/MECHANIZM': [klucze neuronów]}."""
    return raport_mechanizmow()["skupiska_redundancji"]


def _wariancja_zerowa(seria: List[float]) -> bool:
    return len(set(seria)) <= 1


def ocen_pare(klucz_a: str, klucz_b: str, seria_a: List[float],
              seria_b: List[float]) -> Dict[str, Any]:
    """Werdykt dla JEDNEJ pary — czysty, bez wejścia/wyjścia.

    Kolejność sprawdzeń jest istotna: martwy głos rozstrzygamy PRZED korelacją, bo
    Pearson na stałej serii jest niezdefiniowany, a `None` czytane jako „brak korelacji"
    wyglądałoby jak dywersyfikacja. Rzecz niezmierzona nie jest zielona (Prawo I).
    """
    martwe = [k for k, s in ((klucz_a, seria_a), (klucz_b, seria_b)) if _wariancja_zerowa(s)]
    if martwe:
        return {"para": (klucz_a, klucz_b), "korelacja": None, "werdykt": "CISZA_W_POMIARZE",
                "martwe": martwe,
                "opis": f"stały głos w tym pomiarze: {', '.join(martwe)} — "
                        "korelacji NIE DA SIĘ policzyć, ale to jeszcze nie zarzut (patrz niżej)"}

    r = korelacja_pearson(seria_a, seria_b)
    if r is None:
        return {"para": (klucz_a, klucz_b), "korelacja": None, "werdykt": "NIEROZSTRZYGNIETE",
                "martwe": [], "opis": "korelacji nie dało się policzyć (za mało wspólnych próbek)"}

    if abs(r) > PROG_REDUNDANCJI:
        werdykt, opis = "KANDYDAT_DO_SCALENIA", f"|r|={abs(r):.2f} > {PROG_REDUNDANCJI}"
    elif abs(r) < PROG_DYWERSYFIKACJI:
        werdykt, opis = "FILAR_DYWERSYFIKACJI", f"|r|={abs(r):.2f} < {PROG_DYWERSYFIKACJI}"
    else:
        werdykt, opis = "POSREDNIE", f"|r|={abs(r):.2f} w strefie pośredniej"
    return {"para": (klucz_a, klucz_b), "korelacja": round(r, 4),
            "werdykt": werdykt, "martwe": [], "opis": opis}


def ocen_skupisko(nazwa: str, serie: Dict[str, List[float]]) -> Dict[str, Any]:
    """Werdykt dla całego skupiska: wszystkie pary + podsumowanie."""
    klucze = sorted(serie)
    pary = [ocen_pare(klucze[i], klucze[j], serie[klucze[i]], serie[klucze[j]])
            for i in range(len(klucze)) for j in range(i + 1, len(klucze))]
    licznik: Dict[str, int] = {}
    for p in pary:
        licznik[p["werdykt"]] = licznik.get(p["werdykt"], 0) + 1
    martwe = sorted({k for p in pary for k in p["martwe"]})
    return {
        "skupisko": nazwa, "neurony": klucze, "par": len(pary),
        "pary": pary, "licznik": licznik, "martwe_glosy": martwe,
        "kandydatow_do_scalenia": licznik.get("KANDYDAT_DO_SCALENIA", 0),
        "filarow": licznik.get("FILAR_DYWERSYFIKACJI", 0),
    }


def zbierz_serie(bary: List[Dict[str, Any]], klucze: List[str], budowniczy,
                 *, od: int = 360, postep=None) -> Dict[str, List[float]]:
    """Głosy wskazanych neuronów na kolejnych barach: {KLUCZ: [wartości]}.

    `od` to minimalna historia, jakiej potrzebuje najbardziej łakomy wskaźnik (Pi Cycle
    wymaga ≥360 barów) — liczenie od zera dawałoby głosy z niepełnych okien, czyli pomiar
    czegoś innego niż produkcja.
    """
    wybrane = [n for n in wszystkie_neurony() if n.KLUCZ in set(klucze)]
    serie: Dict[str, List[float]] = {n.KLUCZ: [] for n in wybrane}
    krokow = max(0, len(bary) - od)
    for i, koniec in enumerate(range(od, len(bary)), 1):
        wskazniki = budowniczy.zbuduj(bary[:koniec])
        for n in wybrane:
            try:
                serie[n.KLUCZ].append(sygnal_na_liczbe(n.interpretuj(wskazniki)))
            except Exception:
                # Awaria jednego neuronu nie może przerwać pomiaru całego skupiska,
                # ale NEUTRAL jest tu uczciwy: brak głosu to brak głosu, nie sygnał.
                serie[n.KLUCZ].append(0.0)
        if postep and (i % 25 == 0 or i == krokow):
            postep(i, krokow)
    return serie


def raport(wyniki: List[Dict[str, Any]]) -> str:
    """Wydruk dla Cezara — najpierw to, co wymaga decyzji."""
    linie = ["🔍 DISCRIMINATOR — skupiska redundancji pod pomiarem (Prawo XVI)"]
    do_scalenia = sum(w["kandydatow_do_scalenia"] for w in wyniki)
    martwe = sorted({k for w in wyniki for k in w["martwe_glosy"]})
    linie.append(f"   skupisk zbadanych: {len(wyniki)} | par: {sum(w['par'] for w in wyniki)} "
                 f"| kandydatów do scalenia: {do_scalenia} | milczących w pomiarze: {len(martwe)}")
    if martwe:
        linie.append(f"   ⚠️ CISZA W TYM POMIARZE: {', '.join(martwe)}")
        linie.append("      To NIE jest jeszcze zarzut: pomiar karmi rój wyłącznie świecami "
                     "OHLCV, więc neurony alt-danych (stablecoin, DXY, funding, news) muszą "
                     "milczeć. Rozstrzyga dopiero bieg z adapterami.")
    for w in sorted(wyniki, key=lambda x: -x["kandydatow_do_scalenia"]):
        ikona = "🚨" if w["kandydatow_do_scalenia"] else "✅"
        linie.append(f"   {ikona} {w['skupisko']:<16} neuronów {len(w['neurony']):2d} "
                     f"| par {w['par']:3d} | do scalenia {w['kandydatow_do_scalenia']:2d} "
                     f"| filarów {w['filarow']:2d}")
        for p in w["pary"]:
            if p["werdykt"] == "KANDYDAT_DO_SCALENIA":
                linie.append(f"        • {p['para'][0]} ↔ {p['para'][1]}: r={p['korelacja']} "
                             f"({p['opis']})")
    linie.append("   ℹ️ KANDYDAT ≠ WYROK: wysoka korelacja to podstawa do POMIARU wartości "
                 "dodanej, nie do wyciszenia (Prawo XVI). Decyzja należy do Cezara.")
    return "\n".join(linie)


def zbadaj(sciezka_csv: str, interwal: str = "4h", *, limit: Optional[int] = None,
           od: int = 360, tylko: Optional[List[str]] = None, postep=None) -> List[Dict[str, Any]]:
    """Pomiar na żywych danych: wczytaj bary → policz głosy → oceń każde skupisko."""
    from imperium.akwedukty.czytnik_csv import wczytaj_csv
    from imperium.legiony.budowniczy_wskaznikow import BudowniczyWskaznikow

    bary = wczytaj_csv(sciezka_csv, interwal=interwal, limit=limit)
    budowniczy = BudowniczyWskaznikow()
    wszystkie = skupiska()
    nazwy = [n for n in sorted(wszystkie) if not tylko or n in set(tylko)]

    # JEDEN przebieg wskaźników dla WSZYSTKICH skupisk naraz. Koszt biegu to niemal
    # wyłącznie `budowniczy.zbuduj` (liczy cały arsenał raz na bar, niezależnie od tego,
    # ilu neuronów słucha) — liczenie go osobno dla każdego z 17 skupisk mnożyłoby tę samą
    # pracę siedemnastokrotnie. Zmierzone: ~50 ms na krok, więc oszczędność jest realna,
    # a nie kosmetyczna (Prawo XXIV: długa praca ma być wznawialna i widoczna, nie ślepa).
    potrzebne = sorted({k for n in nazwy for k in wszystkie[n]})
    if postep:
        postep(f"liczę głosy {len(potrzebne)} neuronów z {len(nazwy)} skupisk "
               f"na {max(0, len(bary) - od)} barach", None)
    serie = zbierz_serie(bary, potrzebne, budowniczy, od=od,
                         postep=(lambda i, ile: postep(f"[{i}/{ile}] barów", None))
                         if postep else None)

    wyniki = []
    for nazwa in nazwy:
        podzbior = {k: serie[k] for k in wszystkie[nazwa] if k in serie}
        wyniki.append(ocen_skupisko(nazwa, podzbior))
    return wyniki


if __name__ == "__main__":
    import argparse
    import json
    import logging
    import sys

    logging.disable(logging.CRITICAL)
    ap = argparse.ArgumentParser(
        description="DISCRIMINATOR — czy skupiska redundancji to naprawdę redundancja")
    ap.add_argument("--dane", default="dane/4h/Binance_BTCUSDT_4h.csv")
    ap.add_argument("--interwal", default="4h")
    ap.add_argument("--limit", type=int, default=800,
                    help="ile ostatnich barów wczytać (0 = wszystkie)")
    ap.add_argument("--od", type=int, default=360,
                    help="minimalna historia przed pierwszym głosem (Pi Cycle wymaga 360)")
    ap.add_argument("--tylko", nargs="*", default=None, help="tylko wskazane skupiska")
    ap.add_argument("--lista", action="store_true", help="wypisz skupiska i zakończ")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.lista:
        s = skupiska()
        print(f"🔍 SKUPISKA REDUNDANCJI (kandydaci, Prawo XVI): {len(s)}")
        for nazwa in sorted(s, key=lambda k: -len(s[k])):
            print(f"   {nazwa:<16} {len(s[nazwa]):2d} neuronów: {', '.join(s[nazwa])}")
        sys.exit(0)

    def _postep(co, _ile):
        print(f"   {co}", flush=True)

    wyniki = zbadaj(args.dane, args.interwal,
                    limit=args.limit or None, od=args.od,
                    tylko=args.tylko, postep=_postep)
    print(json.dumps(wyniki, ensure_ascii=False, indent=2) if args.json else raport(wyniki))
