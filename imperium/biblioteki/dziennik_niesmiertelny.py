"""
♾️ Dziennik Nieśmiertelny — W6 Centrum Pamięci W-360 v6 (UNIKAT IMPERIUM)

ROZKAZ CEZARA (2026-06-28): „każda nasza rozmowa, każde zdanie, każdy punkt co
zrobiliśmy ma być pamiętane DOŻYWOTNIO. Cofamy się, tracimy czas, tracimy potencjał —
to dziadostwo, łamie zasady."

DIAGNOZA PROBLEMU (Prawo XV): przechowywanie pamięci DZIAŁA (git = na zawsze, 100+
sesji w kronice). Ale RECALL zawodzi — na starcie sesji wstrzykiwane było tylko top-3
lekcje + profil. Nie widziałem CAŁEGO łuku projektu → wracałem do tematów już zamkniętych,
proponowałem rzeczy już zrobione (np. Numba — omawiana, niezaimplementowana, ale niewidoczna).

ROZWIĄZANIE (UNIKAT — żaden konkurent: Mem0/Zep/Letta/A-Mem polega na retrievalu, który
GUBI): dożywotnia, ZWIĘZŁA oś czasu. Każda sesja = kilka linii (co zrobiono / decyzje /
następny krok), wstrzykiwana W CAŁOŚCI na każdym starcie. Gwarancja, nie statystyka:
zawsze widzę pełną historię. Detale (cały dialog) zostają w kronice (W3b, teraz
przeszukiwalnej po słowach). Dziennik = indeks-przewodnik po wszystkim, co zrobiliśmy.

DLACZEGO DETERMINISTYCZNE (bez DeepSeek): wpis pisze Claude SAM na końcu sesji (jestem
LLM — nie potrzebuję API do siebie). To ROZKAZ STAŁY (CLAUDE.md), nie opcja. Audyt
sprawdza, czy ostatnia sesja zostawiła wpis — brak = czerwony alarm.

ZWIĘZŁOŚĆ = NIEŚMIERTELNOŚĆ: ~5 linii/sesja. 200 sesji = ~1000 linii ≈ 40 KB → mieści
się w kontekście W CAŁOŚCI. Gdy urośnie ponad próg → konsolidacja najstarszych w
„epoki" (jak FinMem deep layer), ale oś nigdy nie traci kroku.

Format JSONL (1 wpis = 1 linia JSON):
  {"data": "RRRR-MM-DD", "sesja": "id8", "co": ["..."], "decyzje": ["..."], "nastepny": "..."}

CLI:
  python -m imperium.biblioteki.dziennik_niesmiertelny wpis --co "X" "Y" --decyzje "Z" --nastepny "W"
  python -m imperium.biblioteki.dziennik_niesmiertelny full      # cała oś (do wstrzyknięcia)
  python -m imperium.biblioteki.dziennik_niesmiertelny ostatni   # ostatni wpis
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
PLIK_DOMYSLNY = ROOT / "bibliotheca_ulpia" / "dane" / "dziennik_niesmiertelny.jsonl"

# Próg konsolidacji: powyżej tylu wpisów najstarsze zwijamy w epoki (na razie tylko alarm).
PROG_KONSOLIDACJI = 400

# Ile najnowszych sesji pokazać PEŁNYCH na starcie (starsze jako jednolinijkowce).
# POMIAR I DECYZJA CEZARA 2026-07-26 (8 → 3). Rozbiór wydruku hooka (35,5 KB) pokazał, że
# DZIENNIK to 84% całości, a w nim rozwinięte wpisy to 15 434 zn. za osiem sesji (średnio
# 1 929 zn. na wpis) — 43% CAŁEGO wydruku startowego. Zmierzone warianty:
#   ostatnie=8 → 29 788 zn. (~9 309 tok.)   ostatnie=3 → 20 036 zn. (~6 261 tok.)
# czyli 9 752 zn. ≈ 3 048 tokenów mniej na KAŻDEJ sesji.
# ROZKAZ O CAŁEJ OSI NIENARUSZONY — dowód policzony, nie założony: przy obu wartościach
# wydruk zawiera 124 pozycje ze 124 w pliku (8 → 116 jednolinijkowców + 8 pełnych;
# 3 → 121 + 3). Zwinięcie zmienia FORMĘ, nie zawartość: plik (166 KB, 124 wpisy) zostaje
# nietknięty, a pełna treść jest w nim i w kronice (`centrum_pamieci szukaj`).
DOMYSLNE_PELNE = 3
# Maks. szerokość jednolinijkowca starszej sesji. POMIAR (69 wpisów): pierwsze punkty „co"
# miały medianę 121 zn., ale ogon do 721 zn. — 57 jednolinijkowców ważyło 14 KB. Przycięcie
# do 110 zn. tnie to do ~5 KB bez utraty rozpoznawalności wpisu (Prawo XV: oś ma być
# ZWIĘZŁA; detale są w kronice, przeszukiwalne po słowach).
SZER_JEDNOLINIJKI = 110


def _dzis() -> str:
    return date.today().isoformat()


def _skroc(tekst, maks: int) -> str:
    """
    Przytnij do `maks` znaków z wielokropkiem. Krótkie zwraca bez zmian.

    `str(tekst)` na wejściu (recenzja cubic PR #118): stare/uszkodzone wpisy JSONL mogą mieć
    pierwszy punkt „co" jako liczbę, None lub listę zamiast tekstu — wcześniejsze
    interpolowanie w f-string tolerowało to, `.split()` już nie. Formatowanie ma być odporne
    na brudne dane, nie wywalać startu sesji.
    """
    maks = max(maks, 2)                       # strażnica: maks<2 dałby [:maks-1] == [:-1] (bug)
    tekst = " ".join(str(tekst).split())      # koercja + zwinięcie białych znaków
    return tekst if len(tekst) <= maks else tekst[:maks - 1].rstrip() + "…"


def _wczytaj(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    if plik is None:
        plik = PLIK_DOMYSLNY
    if not plik.exists():
        return []
    wynik = []
    for linia in plik.read_text(encoding="utf-8", errors="ignore").splitlines():
        linia = linia.strip()
        if not linia:
            continue
        try:
            obj = json.loads(linia)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(obj, dict):     # linia poprawna-ale-nie-obiekt (np. liczba/lista) → pomiń
            wynik.append(obj)
    return wynik


def dopisz(co: List[str], decyzje: Optional[List[str]] = None,
           nastepny: str = "", sesja: str = "",
           data: Optional[str] = None,
           plik: Optional[Path] = None) -> bool:
    """
    Dopisuje wpis sesji do dożywotniej osi czasu. Zwraca True (zawsze dopisuje —
    historii się nie falsyfikuje, Prawo I; każda sesja zostawia ślad).

    co        : lista „co zrobiliśmy" (zwięźle, 1 fakt = 1 punkt)
    decyzje   : lista decyzji/ustaleń (czego NIE robić, co wybrano)
    nastepny  : jednozdaniowy następny krok (żeby kolejna sesja wiedziała gdzie wejść)
    sesja     : id sesji (8 znaków wystarczy) — do korelacji z kroniką
    """
    if plik is None:
        plik = PLIK_DOMYSLNY
    wpis = {
        "data": data or _dzis(),
        "sesja": (sesja or "")[:8],
        "co": [c.strip() for c in co if c.strip()],
        "decyzje": [d.strip() for d in (decyzje or []) if d.strip()],
        "nastepny": nastepny.strip(),
    }
    plik.parent.mkdir(parents=True, exist_ok=True)
    with plik.open("a", encoding="utf-8") as f:
        f.write(json.dumps(wpis, ensure_ascii=False) + "\n")
    return True


def wszystkie(plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Cała oś czasu (lista wpisów, najstarsze pierwsze)."""
    return _wczytaj(plik)


def ostatni_wpis(plik: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Najnowszy wpis lub None."""
    w = _wczytaj(plik)
    return w[-1] if w else None


def szukaj(zapytanie: str, limit: int = 10,
           plik: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Po słowach (jak kronika): wpis pasuje gdy zawiera choć jedno słowo zapytania."""
    import re
    slowa = [s for s in re.findall(r"\w+", zapytanie.lower()) if len(s) >= 2]
    if not slowa:
        return []
    wyniki = []
    for w in _wczytaj(plik):
        tekst = (" ".join(w.get("co", [])) + " " + " ".join(w.get("decyzje", []))
                 + " " + w.get("nastepny", "")).lower()
        n = sum(1 for s in slowa if s in tekst)
        if n:
            wyniki.append((n, w))
    wyniki.sort(key=lambda x: x[0], reverse=True)
    return [w for _, w in wyniki[:limit]]


def _sprostowania(blok: str) -> List[str]:
    """Linie ⚠️ dla twierdzeń OBALONYCH, które ten blok wciąż głosi jako fakt.

    SEDNO (zmierzone 2026-07-27, pytanie Cezara „co znaczy 4 z 9"): Dziennik jest
    wstrzykiwany W CAŁOŚCI na starcie każdej sesji, a INDEX FALSORUM świadomie pomija
    katalogi kronik — więc jedyny korpus czytany na pewno co rano był jedynym, którego
    strażnik fałszów nie skanował. Twierdzenie „Imperium używa 2 z ~9 zdarzeń hooka"
    przeżyło tam obalenie i wróciło do kontekstu jako fakt; powtórzyłem je Cezarowi.

    HISTORII NIE RUSZAMY (Prawo I) — wpis zostaje słowo w słowo. Zmienia się wyłącznie to,
    co mu TOWARZYSZY przy odczycie: obalone twierdzenie nigdy nie dociera samo.

    Awaria strażnika nie może wywalić Dziennika: bez osi czasu Architekt traci ciągłość
    całego projektu, a to koszt nieporównanie większy niż brak jednej adnotacji.
    """
    try:
        from imperium.biblioteki.index_falsorum import trafienia_w_tekscie
        traf = trafienia_w_tekscie(blok)
    except Exception:  # noqa: BLE001
        return []
    return [f"   ⚠️ OBALONE (INDEX FALSORUM): {t['poprawna_teza']}" for t in traf]


def _formatuj_wpis(w: Dict[str, Any], pelny: bool = True) -> str:
    """Jedna sesja → zwięzły blok tekstu (z adnotacją, jeśli głosi obalone twierdzenie)."""
    linie = [f"📅 {w.get('data','?')} [{w.get('sesja','')}]"]
    for c in w.get("co", []):
        linie.append(f"   ✓ {c}")
    if pelny:
        for d in w.get("decyzje", []):
            linie.append(f"   ⚖️ {d}")
    if w.get("nastepny"):
        linie.append(f"   → następny: {w['nastepny']}")
    linie += _sprostowania("\n".join(linie))
    return "\n".join(linie)


def os_czasu(plik: Optional[Path] = None, ostatnie: Optional[int] = None) -> str:
    """
    Cała oś czasu jako tekst do WSTRZYKNIĘCIA na starcie sesji.
    ostatnie=N → tylko N najnowszych pełnych (starsze jako jednolinijkowe nagłówki).
    None → wszystko pełne (dożywotnia widoczność — domyślnie).
    """
    wpisy = _wczytaj(plik)
    if not wpisy:
        return "♾️ DZIENNIK NIEŚMIERTELNY — pusty (pierwsza sesja zostawi ślad)."
    linie = [f"♾️ DZIENNIK NIEŚMIERTELNY — {len(wpisy)} sesji, pełna oś projektu:"]

    def jednolinijka(w: Dict[str, Any]) -> str:
        co0 = (w.get("co") or ["—"])[0]   # _skroc koercuje str() → odporne na nie-tekst (PR118 P2)
        return f"   · {w.get('data','?')}: {_skroc(co0, SZER_JEDNOLINIJKI)}"

    if ostatnie is not None and ostatnie <= 0:
        # ostatnie=0 (lub ujemne) → wszystkie jednolinijkowe (slice [:-0] dałby PEŁNE — bug)
        for w in wpisy:
            linie.append(jednolinijka(w))
        return "\n".join(linie)
    if ostatnie is not None and len(wpisy) > ostatnie:
        # starsze: jednolinijkowe; najnowsze `ostatnie`: pełne
        starsze, nowsze = wpisy[:-ostatnie], wpisy[-ostatnie:]
        for w in starsze:
            linie.append(jednolinijka(w))
        for w in nowsze:
            linie.append(_formatuj_wpis(w, pelny=True))
    else:
        for w in wpisy:
            linie.append(_formatuj_wpis(w, pelny=True))
    if len(wpisy) > PROG_KONSOLIDACJI:
        linie.append(f"   ⚠️ {len(wpisy)} wpisów > {PROG_KONSOLIDACJI} — czas skonsolidować najstarsze w epoki.")
    return "\n".join(linie)


def brak_wpisu_dzis(plik: Optional[Path] = None) -> bool:
    """True gdy dziś jeszcze nie ma wpisu (do alarmu audytu — Prawo XV)."""
    last = ostatni_wpis(plik)
    return not last or last.get("data") != _dzis()


def banner_nastepny(plik: Optional[Path] = None) -> str:
    """Zwięzły, JEDNOLINIJKOWY banner NASTĘPNEGO KROKU z ostatniego wpisu — do wydruku
    na GÓRZE startu sesji (A2, uszczelnienie OTWARCIA 2026-07-19).

    Powód (luka L7 zmierzona 2026-07-19): pełny wydruk hooka startowego (~25 KB) ucinał
    podgląd w harnessie i „→ następny" z Dziennika wypadał poza pierwsze okno — trzeba było
    czytać plik tymczasowy, żeby w ogóle zobaczyć plan. Ta jedna linia u samej góry jest
    zawsze widoczna, niezależnie od długości reszty wydruku. `_skroc` koercuje str() →
    odporne na brudny/nietekstowy `nastepny` (jak reszta formatowania osi)."""
    w = ostatni_wpis(plik)
    if not w:
        return "🎯 NASTĘPNY KROK — Dziennik pusty (pierwsza sesja ustali kierunek)."
    nast = _skroc(w.get("nastepny") or "", 240)
    return (f"🎯 NASTĘPNY KROK (Dziennik, sesja {w.get('sesja', '')}, {w.get('data', '?')}): "
            f"{nast or '(brak — ustal na starcie)'}")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Dziennik Nieśmiertelny — W6 W-360 v6")
    sub = p.add_subparsers(dest="cmd")

    p_w = sub.add_parser("wpis", help="Dopisz wpis sesji")
    p_w.add_argument("--co", nargs="+", required=True, help="Co zrobiliśmy (punkty)")
    p_w.add_argument("--decyzje", nargs="*", default=[], help="Decyzje/ustalenia")
    p_w.add_argument("--nastepny", default="", help="Następny krok")
    p_w.add_argument("--sesja", default="", help="ID sesji")

    p_f = sub.add_parser("full", help="Cała oś czasu (do wstrzyknięcia)")
    p_f.add_argument("--ostatnie", type=int, default=None)
    sub.add_parser("ostatni", help="Ostatni wpis")
    sub.add_parser("nastepny", help="Banner NASTĘPNEGO KROKU (jedna linia na górę startu)")
    p_s = sub.add_parser("szukaj", help="Szukaj w osi czasu")
    p_s.add_argument("zapytanie")

    args = p.parse_args()

    if args.cmd == "wpis":
        dopisz(args.co, args.decyzje, args.nastepny, args.sesja)
        print(f"✅ Wpis dopisany ({len(args.co)} punktów).")
    elif args.cmd == "full":
        print(os_czasu(ostatnie=args.ostatnie))
    elif args.cmd == "ostatni":
        w = ostatni_wpis()
        print(_formatuj_wpis(w) if w else "(pusty)")
    elif args.cmd == "nastepny":
        print(banner_nastepny())
    elif args.cmd == "szukaj":
        for w in szukaj(args.zapytanie):
            print(_formatuj_wpis(w, pelny=False))
    else:
        p.print_help()
