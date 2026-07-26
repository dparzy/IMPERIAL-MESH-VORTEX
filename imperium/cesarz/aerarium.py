"""
🏦 AERARIUM — skarbiec Imperium: waga kontekstu startowego i stopnie wysiłku.

Rzymskie *aerarium* (Aerarium Saturni, skarbiec pod świątynią Saturna) trzymało pieniądz
państwa i — co ważniejsze — **rachunki**: kwestorzy wiedzieli, ile Rzym wydaje i na co.
Ten organ robi to samo z tokenami: mierzy, ile kontekstu wchodzi w KAŻDĄ sesję (koszt
stały, płacony przed pierwszym słowem Cezara) i nazywa stopnie wysiłku, którymi Architekt
dobiera głębokość rozumowania do konsekwencji zadania (ZASADA OSZCZĘDNOŚCI TOKENÓW).

DLACZEGO POWSTAŁ (zmierzone 2026-07-26): `CLAUDE.md` miał 760 linii / 51 185 znaków, a
oficjalna dokumentacja Anthropic zaleca trzymać go **pod 200 linii** i przenosić rozkazy
do skilli ładowanych na żądanie. Koszt startu nie był nigdzie widoczny, więc rósł
niezauważony — dokładnie klasa wady „rzecz niemierzona rośnie" (Prawo XV).

CO MIERZY, A CZEGO NIE (Prawo I — abstynencja zamiast zera, lekcja z 2026-07-26):
  • MIERZY trwałe wejścia kontekstu: `CLAUDE.md` (ładowany na starcie każdej sesji)
    oraz indeks pamięci użytkownika, jeśli jest widoczny z tego środowiska.
  • NIE MIERZY wydruku hooka — w chwili, gdy hook woła ten organ, jego własny wydruk
    jeszcze nie istnieje. Zgadywanie byłoby fałszem; organ mówi wprost „zmienny".
  • NIE MIERZY limitu planu Cezara — `/usage` jest komendą interaktywną bez API. Organ
    NIE UDAJE, że zna zużycie planu; twardym źródłem jest rachunek podany przez Cezara
    (ta sama lekcja co taryfa szczytowa DeepSeeka: rachunek > specyfikacja).
  • Stopień wysiłku ODCZYTUJE z konfiguracji (settings.json / zmienna środowiskowa).
    Gdy nie ma żadnego zapisu → None = „nieznany, Architekt deklaruje", nigdy „high":
    środowisko hooka nie niesie faktycznego stopnia sesji (zmierzone: `CLAUDE_EFFORT`
    jest puste), a wartość domyślna modelu to nie to samo co wartość ustawiona.

Bez zależności zewnętrznych (stdlib) → działa też w kontenerze bez pakietów.

Uruchom:  python -m imperium.cesarz.aerarium            # baner (domyślnie, dla hooka)
          python -m imperium.cesarz.aerarium raport      # pełny rachunek + stopnie
          python -m imperium.cesarz.aerarium gradus      # sama tabela stopni
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
KONSTYTUCJA = ROOT / "CLAUDE.md"
USTAWIENIA = ROOT / ".claude" / "settings.json"
KATALOG_SKILLI = ROOT / ".claude" / "skills"

# Limit doktrynalny długości konstytucji. Nie nasza opinia — oficjalna rekomendacja
# Anthropic („aim to keep CLAUDE.md under 200 lines"), bo plik wchodzi w KAŻDĄ sesję.
PROG_LINII_KONSTYTUCJI = 200

# Ile znaków przypada średnio na token w naszym korpusie (polszczyzna + markdown).
# ŚWIADOMIE PRZYBLIŻENIE, oznaczane „~" w wydruku: nie mamy lokalnego tokenizatora
# Anthropic, a `count_tokens` wymagałby płatnego wywołania sieciowego przy każdym
# starcie sesji — to byłby koszt zamiast oszczędności. Liczba służy do wykrywania
# RZĘDU WIELKOŚCI i trendu, nigdy do rozliczeń (Prawo I: nie udajemy precyzji).
ZNAKI_NA_TOKEN = 3.2


# ── GRADUS OPERIS — stopnie pracy (ZASADA NOMENKLATURY: imię dobrane DO FUNKCJI) ──
# Źródło prawdy dla tabeli w CLAUDE.md §💰. Test parytetu pilnuje, by dokument i kod
# nie rozjechały się (lekcja z BREVIARIUM 07-26: kłamał WIDOK, nie logika).
GRADUS: List[Dict[str, str]] = [
    {
        "effort": "low",
        "imie": "VELES",
        "skad_imie": "lekka piechota bez zbroi — szybka, tania, nie wdaje się w walkę",
        "po_co": "mechaniczne, zero osądu",
        "przyklady": "uruchom testy i odczytaj kod wyjścia; regeneruj CODEX; liczenie plików",
        "trwalosc": "trwały",
    },
    {
        "effort": "medium",
        "imie": "MILES",
        "skad_imie": "szeregowy legionista — wykonuje rzemiosło, nie dowodzi",
        "po_co": "rutyna wg wzorca",
        "przyklady": "commity i LOG_ZMIAN; naprawa liczb w dokumentach; wpisy do ledgerów",
        "trwalosc": "trwały",
    },
    {
        "effort": "high",
        "imie": "CENTURIO",
        "skad_imie": "dowódca centurii — kręgosłup legionu, stopień standardowy",
        "po_co": "domyślny stopień Opusa 5",
        "przyklady": "implementacja wg specyfikacji; recenzja; raporty; rozmowa z Cezarem",
        "trwalosc": "trwały",
    },
    {
        "effort": "xhigh",
        "imie": "TRIBUNUS",
        "skad_imie": "trybun — decyzje operacyjne całego legionu",
        "po_co": "trudne, wymaga hipotezy",
        "przyklady": "debugowanie realnego buga; projekt organu; osąd kandydatów; A/B",
        "trwalosc": "trwały",
    },
    {
        "effort": "max",
        "imie": "DICTATOR",
        "skad_imie": "władza nadzwyczajna, która WYGASAŁA z czasem — jak stopień tylko na tę sesję",
        "po_co": "nieodwracalne konsekwencje",
        "przyklady": "zmiana konstytucji; kierunek strategiczny; decyzje o kapitale",
        "trwalosc": "tylko bieżąca sesja",
    },
    {
        "effort": "ultrathink (słowo w prompcie)",
        "imie": "AUSPICIUM",
        "skad_imie": "jednorazowa wróżba PRZED konkretnym czynem, potem znika",
        "po_co": "jedna tura głębiej, bez podnoszenia całej wachty",
        "przyklady": "jedno trudne pytanie w środku taniej sesji",
        "trwalosc": "jedna tura (stopień API bez zmian)",
    },
    {
        "effort": "ultracode (ustawienie Claude Code)",
        "imie": "PRAEFECTUS FABRUM",
        "skad_imie": "oficer od inżynierów — organizował roboty, nie wykonywał ich sam",
        "po_co": "xhigh + orkiestracja dynamicznych workflow",
        "przyklady": "wielka rozbudowa na wielu frontach naraz",
        "trwalosc": "tylko bieżąca sesja",
    },
]

# Stopnie, które wolno zapisać trwale w settings.json (max i ultracode są sesyjne).
POZIOMY_TRWALE = ("low", "medium", "high", "xhigh")


def _imie_stopnia(poziom: str) -> str:
    """Rzymskie imię stopnia albo '?' — nieznanej nazwy NIE tłumaczymy na siłę."""
    for g in GRADUS:
        if g["effort"] == poziom:
            return g["imie"]
    return "?"


def _katalogi_projektu() -> List[Path]:
    """Katalogi harnessa dla TEGO projektu — źródło pamięci i zapisanych wydruków hooka.

    Leżą POZA repo (per maszyna), więc w kontenerze chmury mogą nie istnieć: pusta lista
    znaczy „nie wiem z tego środowiska", nigdy „nie ma".
    """
    baza = Path(os.getenv("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")) / "projects"
    if not baza.exists():
        return []
    znacznik = ROOT.name.lower()
    trafione = [d for d in baza.iterdir() if d.is_dir() and znacznik in d.name.lower()]
    if trafione:
        return trafione
    wszystkie = [d for d in baza.iterdir() if d.is_dir()]
    return wszystkie if len(wszystkie) == 1 else []


def _indeks_pamieci() -> Optional[Path]:
    """MEMORY.md użytkownika — ładowany na starcie każdej sesji, ale leży POZA repo."""
    for kat in _katalogi_projektu():
        plik = kat / "memory" / "MEMORY.md"
        if plik.exists():
            return plik
    return None


def koszt_hooka() -> Optional[Dict[str, Any]]:
    """NADZÓR: ile znaków miał OSTATNI zapisany wydruk hooka i który blok go zdominował.

    Mierzymy POPRZEDNI bieg, nie bieżący — w chwili, gdy hook woła ten organ, jego własny
    wydruk jeszcze nie istnieje. Pomiar po fakcie jest uczciwy; zgadywanie nie byłoby.

    Po co nadzór (rozkaz Cezara 2026-07-26 „hook musi zawierać wszystko… pod nadzorem"):
    kompletność hooka jest DOBRA i tania — wszystkie organy razem to ~1,3 KB. Ale koszt
    całego wydruku rośnie (zmierzone: 35–37 KB), więc każda decyzja „dołóżmy jeszcze jeden
    meldunek" musi być widoczna w cenie. Bez tej linii koszt rósłby po cichu — dokładnie
    ta klasa wady, dla której powstał cały skarbiec.

    None = brak zapisanego wydruku w tym środowisku (abstynencja).
    """
    pliki: List[Path] = []
    for kat in _katalogi_projektu():
        pliki.extend(kat.glob("*/tool-results/hook-*stdout.txt"))
    if not pliki:
        return None
    najnowszy = max(pliki, key=lambda p: p.stat().st_mtime)
    tekst = najnowszy.read_text(encoding="utf-8", errors="replace")
    znaki = len(tekst)

    # Podział na bloki po nagłówkach organów — ta sama granica, którą widzi czytelnik.
    granice = ("[hook]", "🏛️", "📕", "📋", "📜", "🧠", "♾️", "🎯", "🐞", "🏦", "🔏")
    bloki: List[List[str]] = []
    for linia in tekst.splitlines():
        if linia.startswith(granice):
            bloki.append([linia])
        elif bloki:
            bloki[-1].append(linia)
    najciezszy = None
    if bloki:
        wybrany = max(bloki, key=lambda b: sum(len(x) + 1 for x in b))
        waga = sum(len(x) + 1 for x in wybrany)
        najciezszy = {
            "naglowek": wybrany[0][:46],
            "znaki": waga,
            "udzial_proc": int(100 * waga / znaki) if znaki else 0,
        }
    return {"znaki": znaki, "tokeny_szac": int(znaki / ZNAKI_NA_TOKEN),
            "najciezszy_blok": najciezszy, "plik": najnowszy.name}


def waga_kontekstu() -> Dict[str, Any]:
    """Ile kontekstu wchodzi w KAŻDĄ sesję — policzone z plików, nie z pamięci.

    Wartość None przy składniku = „nie wiem z tego środowiska" (abstynencja).
    """
    wynik: Dict[str, Any] = {"skladniki": {}, "znaki_razem": 0}

    if KONSTYTUCJA.exists():
        tekst = KONSTYTUCJA.read_text(encoding="utf-8")
        linie = len(tekst.splitlines())
        wynik["skladniki"]["CLAUDE.md"] = {"znaki": len(tekst), "linie": linie}
        wynik["znaki_razem"] += len(tekst)
        wynik["linie_konstytucji"] = linie
    else:
        wynik["skladniki"]["CLAUDE.md"] = None
        wynik["linie_konstytucji"] = None

    pamiec = _indeks_pamieci()
    if pamiec is not None and pamiec.exists():
        zn = len(pamiec.read_text(encoding="utf-8"))
        wynik["skladniki"]["MEMORY.md"] = {"znaki": zn, "linie": None}
        wynik["znaki_razem"] += zn
    else:
        wynik["skladniki"]["MEMORY.md"] = None      # niewidoczny stąd ≠ nie istnieje

    # Skille NIE wchodzą w kontekst startowy — do kontekstu wchodzi tylko ich opis,
    # a pełna treść dopiero po wywołaniu. Liczymy je osobno jako „oszczędność odłożoną":
    # tyle znaków NIE płacimy na starcie dzięki wzorcowi ładowania na żądanie.
    odlozone = 0
    liczba_skilli = 0
    if KATALOG_SKILLI.exists():
        for plik in KATALOG_SKILLI.glob("*/SKILL.md"):
            odlozone += len(plik.read_text(encoding="utf-8"))
            liczba_skilli += 1
    wynik["skille"] = {"ile": liczba_skilli, "znaki_odlozone": odlozone}

    wynik["tokeny_szac"] = int(wynik["znaki_razem"] / ZNAKI_NA_TOKEN)
    return wynik


def stopien_domyslny() -> Dict[str, Optional[str]]:
    """Skonfigurowany stopień wysiłku + SKĄD go znamy. None = nieznany (abstynencja).

    Kolejność wg dokumentacji Claude Code: zmienna środowiskowa nadpisuje ustawienia.
    Brak zapisu NIE znaczy „high" — model ma swoją wartość domyślną, ale to nie jest
    to samo co decyzja Cezara, a organ raportuje decyzje, nie domysły (Prawo I).
    """
    env = os.getenv("CLAUDE_CODE_EFFORT_LEVEL")
    if env:
        return {"poziom": env, "zrodlo": "CLAUDE_CODE_EFFORT_LEVEL", "imie": _imie_stopnia(env)}
    if USTAWIENIA.exists():
        try:
            dane = json.loads(USTAWIENIA.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            dane = {}
        poziom = dane.get("effortLevel")
        if poziom:
            return {"poziom": poziom, "zrodlo": ".claude/settings.json",
                    "imie": _imie_stopnia(poziom)}
    return {"poziom": None, "zrodlo": None, "imie": None}


def alarmy(waga: Optional[Dict[str, Any]] = None) -> List[str]:
    """Czerwone alarmy skarbca. Pusta lista = skarbiec w porządku."""
    w = waga if waga is not None else waga_kontekstu()
    lista: List[str] = []
    linie = w.get("linie_konstytucji")
    if linie is not None and linie > PROG_LINII_KONSTYTUCJI:
        lista.append(
            f"DŁUG KONTEKSTU: CLAUDE.md ma {linie} linii > {PROG_LINII_KONSTYTUCJI} "
            f"(limit doktrynalny) — rozkazy do przeniesienia w skille ładowane na żądanie"
        )
    return lista


def banner() -> str:
    """Krótki wydruk dla hooka startowego — świadomie zwięzły, bo hook sam jest kosztem."""
    w = waga_kontekstu()
    st = stopien_domyslny()
    wiersze = ["🏦 AERARIUM — skarbiec kontekstu i stopni wysiłku:"]

    km = w["skladniki"].get("CLAUDE.md")
    czesci = []
    if km:
        czesci.append(f"CLAUDE.md {km['linie']} linii ({km['znaki'] // 1024} KB)")
    else:
        czesci.append("CLAUDE.md NIEZNANY")
    pm = w["skladniki"].get("MEMORY.md")
    czesci.append(f"pamięć {pm['znaki'] // 1024} KB" if pm else "pamięć niewidoczna stąd")
    wiersze.append(f"   stały koszt startu: {' + '.join(czesci)} ≈ ~{w['tokeny_szac']} tokenów"
                   f" (wydruk hooka liczony osobno — niżej)")

    if st["poziom"]:
        wiersze.append(f"   stopień skonfigurowany: {st['poziom']} = {st['imie']}"
                       f"  (źródło: {st['zrodlo']})")
    else:
        wiersze.append("   stopień skonfigurowany: BRAK ZAPISU — Architekt deklaruje sam"
                       " (środowisko hooka nie niesie stopnia sesji)")

    wiersze.append("   GRADUS: " + " ".join(
        f"{g['imie']}({g['effort'].split()[0]})" for g in GRADUS[:5]))
    wiersze.append("   AUSPICIUM: słowo „ultrathink" + '" w prompcie = jedna tura głębiej,'
                   " bez zmiany stopnia sesji")

    sk = w["skille"]
    if sk["ile"]:
        wiersze.append(f"   odłożone na żądanie: {sk['ile']} skilli / "
                       f"{sk['znaki_odlozone']} zn. NIE płaconych na starcie")

    kh = koszt_hooka()
    if kh is None:
        wiersze.append("   nadzór wydruku hooka: brak zapisu w tym środowisku (nie wiem)")
    else:
        naj = kh["najciezszy_blok"]
        ogon = (f" | najcięższy: {naj['naglowek']} = {naj['udzial_proc']}%"
                if naj else "")
        wiersze.append(f"   nadzór wydruku hooka: poprzedni bieg {kh['znaki'] // 1024} KB"
                       f" ≈ ~{kh['tokeny_szac']} tokenów{ogon}")

    for a in alarmy(w):
        wiersze.append(f"   🚨 {a}")
    return "\n".join(wiersze)


def raport() -> str:
    """Pełny rachunek skarbca + tabela stopni (do czytania przez Cezara, nie do hooka)."""
    w = waga_kontekstu()
    st = stopien_domyslny()
    linie = [banner(), "", "   ── GRADUS OPERIS (stopień podnosisz za KONSEKWENCJE, nie za rozmiar) ──"]
    for g in GRADUS:
        linie.append(f"   {g['imie']:<18} {g['effort']:<34} {g['trwalosc']}")
        linie.append(f"   {'':<18} po co: {g['po_co']}")
        linie.append(f"   {'':<18} np.:   {g['przyklady']}")
        linie.append(f"   {'':<18} imię:  {g['skad_imie']}")
    linie.append("")
    linie.append(f"   Trwale zapisywalne w settings.json: {', '.join(POZIOMY_TRWALE)}"
                 " (max i ultracode są sesyjne)")
    linie.append(f"   Stopień skonfigurowany: {st['poziom'] or 'BRAK ZAPISU (abstynencja)'}")
    linie.append(f"   Suma stałego kosztu startu: {w['znaki_razem']} zn."
                 f" ≈ ~{w['tokeny_szac']} tokenów")
    return "\n".join(linie)


def _tabela_gradus_md() -> str:
    """Tabela stopni w markdownie — dla dokumentów, generowana z JEDNEGO źródła (kodu)."""
    naglowek = ("| Stopień (effort) | Imię rzymskie | Kiedy | Trwałość |\n"
                "|---|---|---|---|\n")
    return naglowek + "\n".join(
        f"| `{g['effort']}` | **{g['imie']}** | {g['po_co']} | {g['trwalosc']} |"
        for g in GRADUS)


if __name__ == "__main__":                                   # pragma: no cover
    komenda = sys.argv[1] if len(sys.argv) > 1 else "banner"
    if komenda == "raport":
        print(raport())
    elif komenda == "gradus":
        print(_tabela_gradus_md())
    else:
        print(banner())
