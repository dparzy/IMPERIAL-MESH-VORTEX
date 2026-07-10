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
PLIK_PROFILU = ROOT / "docs" / "PROFIL_CEZARA.md"

_NAGLOWEK_LEKCJE = "## 📚 LEKCJE Z SESJI"

# Wspólny wzorzec lekcji (parser + przepisywanie używają TEGO SAMEGO, by były spójne —
# inaczej _zapisz_lekcje mogło inaczej wykrywać granicę „ogona" niż lekcje(), co przy
# linii `## ` w treści duplikowało lekcje). Kotwica na dacie: lekcja = nagłówek
# `### YYYY-MM-DD — tytuł`; body kończy się na następnym takim nagłówku, sekcji `## ` lub końcu.
_WZOR_LEKCJI = re.compile(
    r"^### (\d{4}-\d{2}-\d{2})\s*[—-]\s*(.+?)\s*\n"
    r"(.*?)(?=\n### \d{4}-\d{2}-\d{2}\s*[—-]|\n## |\Z)",
    re.M | re.S,
)

# Limity zwięzłości (inspiracja Hermes Agent: MEMORY.md ~2200 zn., USER.md ~1375 zn.).
# Hermes ODRZUCA zapis przekraczający limit (twardy błąd, zero auto-kompakcji) — robimy
# tak samo dla POJEDYNCZEJ lekcji (wymusza ostrość). Dla CAŁEJ sekcji lekcji dajemy
# miękki alarm Prawa XV (log puchnie → czas skonsolidować), bo to świadomie rosnący
# dziennik, nie pamięć rdzeniowa o stałym budżecie.
LIMIT_ZNAKOW_LEKCJA = 1200
LIMIT_ZNAKOW_SEKCJA = 24000

# ── Dedup semantyczny (naprawa: 4 kopie tej samej lekcji, recenzja cubic PR #118) ──
# Stary dedup porównywał DOKŁADNY PODCIĄG tytułu (`szukaj(tytul)`). DeepSeek ekstrahuje
# lekcje z temperatura=0.3, więc za każdym przebiegiem formułuje tytuł inaczej —
# „Martwy głos ATR_MULT w EXP-07" vs „Dead voice bug: ATR_MULT w EXP-07". Żaden nie jest
# podciągiem drugiego → duplikat przechodził.
#
# POMIAR (Prawo XVI — redundancja mierzona, nie zgadywana), 71 realnych lekcji:
#   • podobieństwo NAPISÓW nie rozdziela: prawdziwy duplikat 0.642 < różne lekcje 0.667
#     („ATR_MULT w TLP" vs „ATR w Night Turbo" to RÓŻNE moduły: EXP-07 i EXP-08).
#   • podobieństwo SYGNATUR TECHNICZNYCH rozdziela czysto: wszystkie pary ≥ 0.60 są
#     duplikatami, żadna para różnych lekcji nie przekracza 0.571.
# Stąd: dedup po zbiorze identyfikatorów (ATR_MULT, EXP-07, HA_Open, 299), miara Jaccarda.
# Próg dobrany z marginesem 0.60 (najbliższy fałszywy kandydat: 0.571).
PROG_PODOBIENSTWA = 0.60
# Sygnatura z 1 tokenu jest zbyt uboga, by orzekać o tożsamości lekcji (np. samo „ATR”
# łączyłoby lekcje o różnych modułach) → poniżej tego progu NIE deduplikujemy.
MIN_TOKENOW_SYGNATURY = 2

# Identyfikator techniczny: KLUCZ-NUMER (EXP-07, X-28), nazwa_z_podkreśleniem
# (ATR_MULT, HA_Open), AKRONIM (ATR, RSI) albo liczba ≥ 2 cyfr (299, 14).
#
# KOLEJNOŚĆ ALTERNATYW JEST ISTOTNA (bug z samo-recenzji): gdyby `[A-Z]{2,}` szło pierwsze,
# na „EXP-07" dopasowałoby samo „EXP", a „-07" zostałoby gołą liczbą. Sygnatura gubiłaby
# tożsamość modułu, a osierocone liczby zawyżały Jaccarda: „EXP-07 ATR 14" i „EXP-07 RSI 14"
# dawały {07,14,ATR,EXP} vs {07,14,EXP,RSI} = 0.60 → scalenie dwóch RÓŻNYCH lekcji dokładnie
# na progu. Klucz-numer musi być łapany jako JEDEN token.
_WZOR_TOKENU = re.compile(
    r"\b(?:[A-Z]+-\d+|[A-Za-z]+_[A-Za-z0-9_]+|[A-Z]{2,}[A-Z0-9_]*|\d{2,})\b"
)
# Tokeny bez mocy rozróżniającej — występują w połowie lekcji, nic nie identyfikują.
_TOKENY_PUSTE = frozenset({"NEUTRAL", "LONG", "SHORT", "TODO", "OHLCV"})

# Sito 3: lekcje CZYSTO PROZATORSKIE (bez identyfikatorów) — np. „True Range - poprawna
# definicja" vs „Poprawiona definicja True Range". Sygnatura techniczna jest tam pusta,
# więc porównujemy worek RDZENI tytułu: prefiks 5 znaków zrównuje polską fleksję
# („poprawna"/„poprawiona" → „popra"), a kolejność słów przestaje mieć znaczenie.
# POMIAR na 71 lekcjach: łapie 3 kopie True Range, zero fałszywych trafień.
_DL_RDZENIA = 5
# UWAGA: „nie" NIE MOŻE tu być (bug z samo-recenzji). Sito 3 patrzy wyłącznie na tytuł,
# więc pominięcie negacji zrównywałoby zdanie z jego zaprzeczeniem: „Numba przyspiesza
# wskaźniki" i „Numba NIE przyspiesza wskaźników" miałyby ten sam worek rdzeni → lekcja
# obalająca poprzednią byłaby odrzucona jako duplikat. Negacja jest treścią, nie szumem.
_SLOWA_PUSTE = frozenset({"jest", "bug", "przy", "to", "sie", "gdy", "oraz"})


def _dzis() -> str:
    return _dt.date.today().isoformat()


def sygnatura_lekcji(tytul: str, tresc: str = "") -> frozenset:
    """
    Zbiór identyfikatorów technicznych z lekcji — „o czym ona właściwie jest".
    Odporna na przeformułowanie prozy (i na zmianę języka: „martwy głos" ↔ „dead voice"),
    bo patrzy wyłącznie na nazwy modułów, kluczy i stałych.
    """
    tokeny = {t.upper() for t in _WZOR_TOKENU.findall(f"{tytul} {tresc}")}
    return frozenset(tokeny - _TOKENY_PUSTE)


def _jaccard(a: frozenset, b: frozenset) -> float:
    """Podobieństwo zbiorów |A∩B| / |A∪B|. Zwraca 0.0 dla dwóch zbiorów pustych."""
    suma = a | b
    return len(a & b) / len(suma) if suma else 0.0


def _sygnatura_rozstrzygajaca(sygn: frozenset) -> bool:
    """
    Czy sygnatura wystarcza, by orzec o tożsamości lekcji?

    Wymaga dwóch rzeczy: dość tokenów (MIN_TOKENOW_SYGNATURY) i **co najmniej jednego
    tokenu z literą**. Same liczby nie identyfikują lekcji — `\\d{2,}` łapie też daty
    i wartości progów, więc „RSI 14, próg 30" i „stop 14 przy 30 barach" miałyby
    sygnaturę {14, 30} i Jaccard 1.0. Trzy lekcje w docs/PAMIEC_SESJI.md mają dziś
    sygnaturę czysto liczbową (np. {06, 2026} — to data z treści). Bez tego warunku
    dedup scaliłby je z dowolną inną lekcją o tych samych liczbach.
    """
    if len(sygn) < MIN_TOKENOW_SYGNATURY:
        return False
    return any(not token.isdigit() for token in sygn)


def _rdzenie_tytulu(tytul: str) -> frozenset:
    """Worek rdzeni słów tytułu — odporny na fleksję i szyk (sito 3, patrz _DL_RDZENIA)."""
    tekst = re.sub(r"[^0-9a-ząćęłńóśźż_-]+", " ", tytul.lower().replace("ł", "l"))
    return frozenset(
        slowo[:_DL_RDZENIA] for slowo in tekst.split()
        if len(slowo) > 2 and slowo not in _SLOWA_PUSTE
    )


def duplikat_lekcji(tytul: str, tresc: str = "",
                    plik: Path = DOMYSLNY_PLIK) -> Optional[Dict[str, str]]:
    """
    Zwraca ISTNIEJĄCĄ lekcję mówiącą to samo (lub None). Podstawa dedupu auto-lekcji.

    Trzy sita, w kolejności:
      1. identyczny tytuł po normalizacji (tani, pewny),
      2. sygnatura techniczna o podobieństwie ≥ PROG_PODOBIENSTWA (odporny na parafrazę),
      3. identyczny worek rdzeni tytułu — dla lekcji bez identyfikatorów (proza).

    Świadomie ZACHOWAWCZY: przy ubogiej sygnaturze (< MIN_TOKENOW_SYGNATURY) sito 2 milczy.
    Wolimy przepuścić duplikat niż scalić dwie różne lekcje — fałszywe scalenie kasuje
    wiedzę bezpowrotnie, fałszywy duplikat kosztuje kilka linii pliku.
    """
    for lek in lekcje(plik):
        if czy_duplikaty(tytul, tresc, lek["tytul"], lek["tresc"]):
            return lek
    return None


def czy_duplikaty(tytul_a: str, tresc_a: str, tytul_b: str, tresc_b: str) -> bool:
    """
    Czy dwie lekcje mówią to samo? Wspólny predykat dedupu i scalania — jedno źródło
    prawdy, żeby próg nie rozjechał się między zapisem a konsolidacją (Prawo I).

    ZNANE OGRANICZENIE (świadome, udokumentowane — Prawo I: nie udajemy, że go nie ma):
    sygnatura widzi IDENTYFIKATORY, nie kierunek wniosku. „ATR_MULT w EXP-07 za niski"
    i „ATR_MULT w EXP-07 za wysoki" mają tę samą sygnaturę → zostaną uznane za duplikat.
    Dlatego `auto_lekcja` LOGUJE każdy pominięty tytuł — pominięcie jest widoczne, nie ciche.
    Lekcja obalająca poprzednią wymaga ręcznego `aktualizuj_lekcje()`, nie dopisania obok.
    """
    a, b = tytul_a.strip().lower(), tytul_b.strip().lower()
    if a and a == b:
        return True

    sygn_a = sygnatura_lekcji(tytul_a, tresc_a)
    sygn_b = sygnatura_lekcji(tytul_b, tresc_b)
    if (_sygnatura_rozstrzygajaca(sygn_a) and _sygnatura_rozstrzygajaca(sygn_b)
            and _jaccard(sygn_a, sygn_b) >= PROG_PODOBIENSTWA):
        return True

    rdzenie_a = _rdzenie_tytulu(tytul_a)
    return bool(rdzenie_a) and rdzenie_a == _rdzenie_tytulu(tytul_b)


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

    # Parser i przepisywanie współdzielą _WZOR_LEKCJI (patrz komentarz przy definicji).
    wzor = _WZOR_LEKCJI
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
    # Limit zwięzłości pojedynczej lekcji (Hermes-style: twardy błąd, nie ciche ucięcie).
    dlugosc = len(tytul) + len(tresc.strip())
    if dlugosc > LIMIT_ZNAKOW_LEKCJA:
        raise ValueError(
            f"Lekcja '{tytul}' ma {dlugosc} znaków > limit {LIMIT_ZNAKOW_LEKCJA}. "
            "Skróć (pamięć ma być ostra, nie obszerna) — zob. limit Hermes MEMORY.md."
        )
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


def _zapisz_lekcje(lekcje_lista: List[Dict[str, str]], plik: Path) -> None:
    """Przepisuje sekcję LEKCJE Z SESJI z podanej listy (zachowuje resztę pliku)."""
    tekst = wczytaj(plik)
    bloki = "\n".join(f"### {lek['data']} — {lek['tytul']}\n{lek['tresc']}\n"
                      for lek in lekcje_lista)
    if _NAGLOWEK_LEKCJE in tekst:
        przed = tekst.split(_NAGLOWEK_LEKCJE, 1)[0]
        po_sekcji = tekst.split(_NAGLOWEK_LEKCJE, 1)[1]
        # Granicę „ogona" (np. STAN BIEŻĄCY) liczymy od KOŃCA ostatniej sparsowanej lekcji
        # tym samym wzorcem co parser — odporne na linię `## ` w treści lekcji (inaczej
        # pierwsza taka linia w treści ucinałaby ogon i duplikowała kolejne lekcje).
        dopasowania = list(_WZOR_LEKCJI.finditer(po_sekcji))
        if dopasowania:
            reszta = po_sekcji[dopasowania[-1].end():]
            m = re.search(r"\n## ", reszta)
            ogon = reszta[m.start():].lstrip("\n") if m else ""
        else:
            m = re.search(r"\n## ", po_sekcji)
            ogon = po_sekcji[m.start():].lstrip("\n") if m else ""
        nowy = f"{przed}{_NAGLOWEK_LEKCJE}\n\n{bloki}\n{ogon}"
    else:
        nowy = f"{tekst.rstrip()}\n\n{_NAGLOWEK_LEKCJE}\n\n{bloki}\n"
    plik.write_text(nowy, encoding="utf-8")


def usun_lekcje(tytul: str, plik: Path = DOMYSLNY_PLIK) -> bool:
    """
    Usuwa lekcję po dokładnym tytule (Hermes memory tool: akcja `remove`).
    Zwraca True gdy usunięto, False gdy nie znaleziono. Bez tego pamięć tylko
    rosła — nieaktualne lekcje zostawały na zawsze (UTRATA POTENCJAŁU, Prawo XV).
    """
    lst = lekcje(plik)
    nowe = [lek for lek in lst if lek["tytul"] != tytul]
    if len(nowe) == len(lst):
        return False
    _zapisz_lekcje(nowe, plik)
    return True


def aktualizuj_lekcje(tytul: str, nowa_tresc: str, plik: Path = DOMYSLNY_PLIK,
                      nowy_tytul: Optional[str] = None) -> bool:
    """
    Zastępuje treść (i opcjonalnie tytuł) istniejącej lekcji (Hermes: akcja `replace`).
    Zwraca True gdy podmieniono, False gdy nie znaleziono. Limit zwięzłości jak w dopisz.
    """
    docelowy = nowy_tytul or tytul
    if len(docelowy) + len(nowa_tresc.strip()) > LIMIT_ZNAKOW_LEKCJA:
        raise ValueError(f"Lekcja '{docelowy}' przekracza limit {LIMIT_ZNAKOW_LEKCJA} znaków.")
    lst = lekcje(plik)
    znaleziono = False
    for lek in lst:
        if lek["tytul"] == tytul:
            lek["tytul"] = docelowy
            lek["tresc"] = nowa_tresc.strip()
            znaleziono = True
            break
    if not znaleziono:
        return False
    _zapisz_lekcje(lst, plik)
    return True


def alarm_przepelnienia(plik: Path = DOMYSLNY_PLIK) -> Optional[str]:
    """
    Prawo XV: gdy sekcja lekcji puchnie ponad LIMIT_ZNAKOW_SEKCJA → miękki alarm
    (czas skonsolidować/usunąć stare lekcje). Zwraca komunikat lub None gdy OK.
    """
    tekst = wczytaj(plik)
    if _NAGLOWEK_LEKCJE not in tekst:
        return None
    sekcja = tekst.split(_NAGLOWEK_LEKCJE, 1)[1]
    nast = re.search(r"\n## ", sekcja)
    sekcja = sekcja[:nast.start()] if nast else sekcja
    if len(sekcja) > LIMIT_ZNAKOW_SEKCJA:
        return (f"🚨 Prawo XV — sekcja LEKCJE ma {len(sekcja)} zn. > {LIMIT_ZNAKOW_SEKCJA}. "
                "Skonsoliduj/usuń najstarsze (usun_lekcje) — pamięć ma być ostra.")
    return None


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


def profil_cezara(plik: Path = PLIK_PROFILU) -> str:
    """
    Model Cezara (odpowiednik USER.md Hermesa): preferencje, styl, decyzje stałe.
    Trzymany osobno od lekcji (środowisko ≠ użytkownik — rozdział jak MEMORY/USER).
    Zwraca treść pliku ("" gdy brak).
    """
    return plik.read_text(encoding="utf-8") if plik.exists() else ""


def profil_skrot(plik: Path = PLIK_PROFILU, maks_linii: int = 6) -> List[str]:
    """Pierwsze punkty profilu (linie zaczynające się od '- ') — do podsumowania startowego."""
    tekst = profil_cezara(plik)
    punkty = [ln.strip() for ln in tekst.splitlines() if ln.strip().startswith("- ")]
    return punkty[:maks_linii]


def podsumowanie_startowe(plik: Path = DOMYSLNY_PLIK, n_lekcji: int = 3) -> str:
    """
    Zwięzłe podsumowanie dla SessionStart hooka: model Cezara (USER.md-style) +
    ostatnie N lekcji + alarm przepełnienia + przypomnienie o mapie. Wyświetlane na
    starcie KAŻDEJ sesji → mapa i preferencje nigdy nie giną w kompakcji.
    """
    if not plik.exists():
        return ""
    linie = ["🧠 PAMIĘĆ SESJI (W-360) — ciągłość między sesjami:"]

    profil = profil_skrot()
    if profil:
        linie.append("   👤 Profil Cezara (kogo słuchasz):")
        for p in profil:
            linie.append(f"   {p}")

    ostatnie = lekcje(plik, limit=n_lekcji)
    if ostatnie:
        linie.append(f"   Ostatnie {len(ostatnie)} lekcje:")
        for lek in ostatnie:
            linie.append(f"   • [{lek['data']}] {lek['tytul']}")

    alarm = alarm_przepelnienia(plik)
    if alarm:
        linie.append(f"   {alarm}")

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
    p_usun = sub.add_parser("usun", help="usuń lekcję po tytule")
    p_usun.add_argument("--tytul", required=True)
    p_akt = sub.add_parser("aktualizuj", help="podmień treść lekcji")
    p_akt.add_argument("--tytul", required=True)
    p_akt.add_argument("--tresc", required=True)
    sub.add_parser("profil", help="pokaż profil Cezara (USER.md-style)")
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
    elif args.cmd == "usun":
        ok = usun_lekcje(args.tytul)
        print(f"{'✅ Usunięto' if ok else '⚠️ Nie znaleziono'}: {args.tytul}")
    elif args.cmd == "aktualizuj":
        ok = aktualizuj_lekcje(args.tytul, args.tresc)
        print(f"{'✅ Zaktualizowano' if ok else '⚠️ Nie znaleziono'}: {args.tytul}")
    elif args.cmd == "profil":
        print(profil_cezara() or "(brak docs/PROFIL_CEZARA.md)")
    else:
        print(podsumowanie_startowe())
