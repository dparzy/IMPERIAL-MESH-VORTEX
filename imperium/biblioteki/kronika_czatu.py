"""
📜 Kronika Czatu (W-360) — trwała pamięć CAŁEJ rozmowy między sesjami.

PROBLEM (Cezar, 2026-06-22): „abyśmy pamiętali wszystkie nasze rozmowy i cały czat
— lokalnie i w chmurze". Claude Code zapisuje transkrypty w ~/.claude/projects/
<projekt>/*.jsonl, ale ten katalog jest POZA repo i GINIE w świeżym kontenerze
chmury. Hermes Agent rozwiązuje to przez session_search po SQLite (~/.hermes/state.db).
My robimy odpowiednik, ale lepiej dla nas: destylujemy transkrypty do REPO (git),
więc historia płynie razem z kodem na każdą maszynę (lokal i chmura).

CO ROBI:
  • destyluj_jsonl()  — z surowego transkryptu wyciąga sam dialog (user + tekst
    asystenta), odrzuca szum tool_use/tool_result; redaguje to, co wygląda na klucz API.
  • eksportuj()       — zapisuje destylat per-sesja do bibliotheca_ulpia/dane/kronika/
    (korpus RAG `dane` → przeszukiwalny FTS5/wektory). Przyrostowy: pomija już zapisane.
  • szukaj()          — pełnotekstowe przeszukanie kroniki (gdy RAG niedostępny).

WARSTWA PAMIĘCI: to rozszerzenie Warstwy 3 (ciągłość sesji). pamiec_sesji.py trzyma
DESTYLAT (lekcje, mapa); kronika_czatu trzyma SUROWY DIALOG (pełny zapis), tak jak
u Hermesa MEMORY.md (rdzeń) ⊥ session_search (pełna historia).

Markdown w git (świadomie): czytelny dla Cezara, wersjonowany, indeksowany w RAG.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Dict, Iterator

ROOT = Path(__file__).resolve().parent.parent.parent
CEL_DOMYSLNY = ROOT / "bibliotheca_ulpia" / "dane" / "kronika"

# Katalog transkryptów Claude Code dla TEGO projektu: ścieżka repo, w której KAŻDY
# separator i dwukropek dysku staje się '-' (np. C:\Projekty\x → 'C--Projekty-x').
#
# BUG NAPRAWIONY 2026-07-20 (pytanie Cezara „czemu hook nie odpalił"): było
# `str(ROOT).replace("/", "-")` — na Windowsie ROOT ma BACKSLASHE i dwukropek dysku,
# więc podmiana '/' nie robiła NIC, a `_SLUG` zostawał ścieżką ABSOLUTNĄ. `pathlib`
# przy sklejaniu ze ścieżką absolutną kasuje wszystko przed nią, więc źródło
# transkryptów wskazywało… katalog projektu. Katalog istniał, więc nie było wyjątku —
# była pogodna informacja „0 sesji". Kronika czatu (W3b) była ŚLEPA przez całą erę
# lokalną: 26 transkryptów nigdy nie trafiło do archiwum (Prawo IX: nic nie ginie).
# W chmurze (Linux, separator '/') slug wychodził poprawnie PRZYPADKIEM — dlatego
# 102 sesje w kronice pochodzą sprzed przeprowadzki na lokal.
def _slug_projektu(sciezka: Path) -> str:
    """Ścieżka repo → nazwa katalogu transkryptów Claude Code (POSIX i Windows)."""
    return str(sciezka).replace(":", "-").replace("\\", "-").replace("/", "-")


_SLUG = _slug_projektu(ROOT)
ZRODLO_DOMYSLNE = Path.home() / ".claude" / "projects" / _SLUG

# Redakcja sekretów (Prawo Bezpieczeństwa: klucze NIGDY w repo). Wzorce typowych kluczy.
_WZORY_SEKRETOW = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),               # OpenAI/DeepSeek styl
    re.compile(r"\b[A-Za-z0-9]{32,}\b"),              # długie tokeny hex/base
    re.compile(r"(?i)(api[_-]?key|secret|token)\s*[=:]\s*\S+"),
]


# Redakcja KATALOGU DOMOWEGO (recenzja cubic PR #134, P0 — potwierdzona pomiarem 2026-07-27:
# 277 wystąpień w 30 plikach kroniki). Transkrypty niosą ścieżki narzędziowe w rodzaju
# `C:\Users\<user>\AppData\Local\Temp\claude\...`, więc do repo trafiała NAZWA KONTA Cezara
# i lokalizacje specyficzne dla maszyny — dane osobowe plus referencje nieprzenośne.
#
# TO BYŁ NAWRÓT, NIE NOWOŚĆ. Klasa została nazwana dzień wcześniej (archiwum lekcji
# 2026-07-26: „Commitowanie desktop paths łamie przenośność i PII"), ale została LEKCJĄ,
# a nie MECHANIZMEM — i wróciła w 277 egzemplarzach. Organ redakcji ISTNIAŁ; miał tylko
# za wąski zasięg: pilnował kluczy API i nie wiedział nic o ścieżkach. To ta sama klasa
# co bramka pilnująca jednego katalogu z jedenastu.
#
# DOM BIERZEMY Z `Path.home()`, NIGDY z wpisanej nazwy konta: mechanizm ma działać na
# maszynie każdego, kto uruchomi Imperium, a wpisanie „Ian" na sztywno utrwaliłoby w kodzie
# dokładnie tę daną, którą usuwamy.
def _wzorzec_domu(dom: str):
    """Katalog domowy → wzorzec tolerujący WSZYSTKIE formy zapisu separatora.

    Ta sama ścieżka żyje w transkrypcie w trzech postaciach naraz: `C:\\Users\\X` (proza),
    `C:\\\\Users\\\\X` (po ucieczce w JSON) i `C:/Users/X` (narzędzia POSIX-owe). Wzorzec
    dopasowujący tylko jedną z nich zostawiłby dwie — czyli redakcja meldowałaby sukces,
    a dane dalej by wyciekały (klasa „milczenie udające wynik")."""
    czesci = [c for c in re.split(r"[\\/]+", dom) if c]
    return re.compile(r"[\\/]{1,2}".join(re.escape(c) for c in czesci), re.IGNORECASE)


_WZORZEC_DOMU = _wzorzec_domu(str(Path.home()))


def _redaguj(tekst: str) -> str:
    """Zamienia klucze API na [ZREDAGOWANO], a katalog domowy na `~` — bezpieczeństwo.

    Kolejność jest istotna: sekrety redagujemy PRZED ścieżkami, bo klucz może wystąpić
    wewnątrz ścieżki, a `~` skróciłoby kontekst, w którym wzorzec klucza jeszcze pasował.
    """
    for wzor in _WZORY_SEKRETOW:
        tekst = wzor.sub("[ZREDAGOWANO]", tekst)
    return _WZORZEC_DOMU.sub("~", tekst)


def _tekst_z_tresci(c) -> str:
    """Wyciąga czysty tekst z pola content (str lub lista bloków)."""
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(b.get("text", "") for b in c
                       if isinstance(b, dict) and b.get("type") == "text")
    return ""


def destyluj_jsonl(sciezka: Path) -> List[Dict[str, str]]:
    """
    Z transkryptu JSONL zwraca [{"rola": "user|assistant", "tekst": "..."}]
    — tylko realny dialog, bez tool_use/tool_result/meta. Sekrety zredagowane.
    """
    wynik: List[Dict[str, str]] = []
    if not sciezka.exists():
        return wynik
    for line in sciezka.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            o = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        m = o.get("message") or {}
        rola = m.get("role") or o.get("type")
        if rola not in ("user", "assistant"):
            continue
        txt = _tekst_z_tresci(m.get("content")).strip()
        if txt:
            wynik.append({"rola": rola, "tekst": _redaguj(txt)})
    return wynik


def _na_markdown(dialog: List[Dict[str, str]], id_sesji: str) -> str:
    """Składa dialog w czytelny markdown (jeden plik = jedna sesja)."""
    linie = [f"# Kronika sesji {id_sesji}", ""]
    for w in dialog:
        kto = "🧑 Cezar" if w["rola"] == "user" else "🏛️ Claude"
        linie.append(f"## {kto}")
        linie.append(w["tekst"])
        linie.append("")
    return "\n".join(linie)


def _pliki_zrodlowe(zrodlo: Path) -> Iterator[Path]:
    if zrodlo.exists():
        yield from sorted(zrodlo.glob("*.jsonl"))


def diagnoza_zrodla(zrodlo: Path = ZRODLO_DOMYSLNE) -> str:
    """Pusty wynik = ŹRÓDŁO ZDROWE. Niepusty = opis awarii do wydrukowania GŁOŚNO.

    UODPORNIENIE KLASY (2026-07-20): sam bug ścieżki był banalny — groźna była CISZA.
    Zły katalog istniał, więc eksport meldował pogodne „0 sesji" zamiast alarmu i
    kronika była ślepa przez całą erę lokalną. Licznik, który przy awarii pokazuje
    zero zamiast krzyczeć, jest gorszy niż wyjątek: wygląda jak spokój.

    Dlatego pytamy WPROST o dwie rzeczy, których zero-w-liczniku nie odróżnia:
    czy katalog źródłowy w ogóle wygląda na katalog transkryptów, i czy są w nim
    jakiekolwiek transkrypty.
    """
    if not zrodlo.exists():
        return (f"🚨 KRONIKA ŚLEPA: katalog transkryptów nie istnieje: {zrodlo}\n"
                f"   Oczekiwany układ: ~/.claude/projects/{_SLUG}/*.jsonl")
    if not any(zrodlo.glob("*.jsonl")):
        oczekiwany = Path.home() / ".claude" / "projects" / _SLUG
        wsk = ""
        if zrodlo.resolve() != oczekiwany.resolve() and any(oczekiwany.glob("*.jsonl")):
            wsk = f"\n   Transkrypty leżą w: {oczekiwany} — źródło wskazuje gdzie indziej."
        return (f"🚨 KRONIKA ŚLEPA: zero transkryptów .jsonl w {zrodlo}{wsk}\n"
                "   Dialog sesji NIE jest archiwizowany (Prawo IX: nic nie ginie).")
    return ""


def eksportuj(zrodlo: Path = ZRODLO_DOMYSLNE, cel: Path = CEL_DOMYSLNY,
              tylko_nowe: bool = True, min_wiadomosci: int = 2) -> Dict[str, int]:
    """
    Destyluje wszystkie transkrypty z `zrodlo` do `cel` (jeden .md per sesja).

    tylko_nowe=True → re-eksportuje sesję TYLKO gdy źródło jest świeższe niż zapisany
    .md (mtime źródła > mtime celu). Naprawa UTRATY POTENCJAŁU (Prawo XV, audyt 2026-06-27):
    poprzednio pomijało KAŻDY istniejący .md → AKTYWNA sesja, eksportowana raz na starcie
    (gdy krótka), nigdy nie dostawała reszty dialogu. 5 dni pracy ginęło z kontenerem.
    Teraz rosnąca sesja jest re-destylowana, aż cały dialog trafi do repo (git).

    Zwraca statystyki {sesje, zapisane, zaktualizowane, pominiete, wiadomosci}.
    """
    cel.mkdir(parents=True, exist_ok=True)
    stat = {"sesje": 0, "zapisane": 0, "zaktualizowane": 0, "pominiete": 0, "wiadomosci": 0}
    for src in _pliki_zrodlowe(zrodlo):
        stat["sesje"] += 1
        id_sesji = src.stem
        cel_plik = cel / f"sesja_{id_sesji}.md"
        cel_gz = cel / f"sesja_{id_sesji}.md.gz"   # zimna (skompresowana) wersja
        # Sesja „istnieje" jeśli jest ciepła (.md) LUB zimna (.md.gz) — inaczej re-eksport
        # utworzyłby duplikat .md obok archiwum .md.gz.
        cel_istniejacy = cel_plik if cel_plik.exists() else (cel_gz if cel_gz.exists() else None)
        istnial = cel_istniejacy is not None
        if tylko_nowe and istnial:
            # Re-eksport tylko gdy źródło świeższe niż zapis (aktywna sesja rośnie).
            try:
                if src.stat().st_mtime <= cel_istniejacy.stat().st_mtime:
                    stat["pominiete"] += 1
                    continue
            except OSError:
                stat["pominiete"] += 1
                continue
        dialog = destyluj_jsonl(src)
        if len(dialog) < min_wiadomosci:
            stat["pominiete"] += 1
            continue
        # Źródło świeższe — re-warm: usuń nieaktualną zimną kopię, zapisz ciepłą .md.
        if cel_gz.exists():
            cel_gz.unlink()
        cel_plik.write_text(_na_markdown(dialog, id_sesji), encoding="utf-8")
        if istnial:
            stat["zaktualizowane"] += 1
        else:
            stat["zapisane"] += 1
        stat["wiadomosci"] += len(dialog)
    return stat


def szukaj(zapytanie: str, cel: Path = CEL_DOMYSLNY,
           limit: int = 20) -> List[Dict[str, str]]:
    """
    Przeszukanie kroniki PO SŁOWACH (token-based), nie po całej frazie.

    NAPRAWA KRYTYCZNA (Prawo XV, 2026-06-28): poprzednio `if zapytanie in linia` —
    całe zapytanie jako jeden substring. "numba JIT wydajność" → 0 trafień, choć
    historia o tym jest (samo "numba" → 4). Każde naturalne wielosłowne pytanie nie
    znajdowało historii → wracaliśmy, traciliśmy czas (dokładnie problem Cezara).

    Teraz: linia pasuje, gdy zawiera CHOĆ JEDNO słowo zapytania; ranking = liczba
    trafionych słów (więcej = wyżej), remis → świeższa sesja. Zwraca pole "trafienia"
    (ile słów pasuje) do scoringu w centrum_pamieci.
    """
    from datetime import datetime
    import re as _re
    slowa = [s for s in _re.findall(r"\w+", zapytanie.lower()) if len(s) >= 2]
    if not slowa:
        return []
    wyniki: List[Dict[str, str]] = []
    if not cel.exists():
        return wyniki
    # Czyta zarówno .md (ciepłe) jak i .md.gz (zimne, skompresowane przez Kustosza W7)
    # → ZERO „memory blindness": skompresowana historia wciąż przeszukiwalna.
    for plik in sorted(_pliki_sesji(cel), key=lambda p: p.stat().st_mtime, reverse=True):
        mtime = plik.stat().st_mtime
        data_pliku = datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%d")
        for linia in _czytaj_sesje_tekst(plik).splitlines():
            low = linia.lower()
            n_traf = sum(1 for s in slowa if s in low)
            if n_traf:
                wyniki.append({
                    "sesja": _id_sesji(plik),
                    "fragment": linia.strip()[:300],
                    "data": data_pliku,
                    "trafienia": n_traf,
                })
    # ranking: więcej trafionych słów najpierw (sesje już od najnowszej w pętli → stabilne)
    wyniki.sort(key=lambda x: x["trafienia"], reverse=True)
    return wyniki[:limit]


def _pliki_sesji(cel: Path) -> List[Path]:
    """Wszystkie pliki sesji: .md (ciepłe) + .md.gz (zimne/skompresowane)."""
    return list(cel.glob("sesja_*.md")) + list(cel.glob("sesja_*.md.gz"))


def _id_sesji(plik: Path) -> str:
    """ID sesji z nazwy pliku (obsługuje .md i .md.gz)."""
    nazwa = plik.name
    if nazwa.endswith(".md.gz"):
        nazwa = nazwa[:-6]
    elif nazwa.endswith(".md"):
        nazwa = nazwa[:-3]
    return nazwa.replace("sesja_", "")


def _czytaj_sesje_tekst(plik: Path) -> str:
    """Czyta treść sesji — przezroczyście dekompresuje .md.gz."""
    if plik.suffix == ".gz":
        import gzip
        try:
            with gzip.open(plik, "rt", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except OSError:
            return ""
    return plik.read_text(encoding="utf-8", errors="ignore")


def statystyki(cel: Path = CEL_DOMYSLNY) -> Dict[str, int]:
    """Ile sesji i znaków jest już w kronice (ciepłe .md + zimne .md.gz)."""
    if not cel.exists():
        return {"sesje": 0, "znaki": 0, "zimne": 0}
    cieple = list(cel.glob("sesja_*.md"))
    zimne = list(cel.glob("sesja_*.md.gz"))
    znaki = sum(p.stat().st_size for p in cieple) + sum(p.stat().st_size for p in zimne)
    return {"sesje": len(cieple) + len(zimne), "znaki": znaki, "zimne": len(zimne)}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Kronika czatu Imperium (W-360)")
    sub = ap.add_subparsers(dest="cmd")
    p_eksp = sub.add_parser("eksportuj", help="destyluj transkrypty do repo")
    p_eksp.add_argument("--wszystko", action="store_true", help="nadpisz też istniejące")
    p_szuk = sub.add_parser("szukaj", help="przeszukaj kronikę")
    p_szuk.add_argument("zapytanie", nargs="+")
    sub.add_parser("statystyki", help="ile sesji w kronice")
    args = ap.parse_args()

    if args.cmd == "eksportuj":
        awaria = diagnoza_zrodla()
        if awaria:
            print(awaria)   # GŁOŚNO przed statystyką — zero w liczniku to nie spokój
        s = eksportuj(tylko_nowe=not args.wszystko)
        print(f"📜 Kronika: {s['zapisane']} zapisane, {s.get('zaktualizowane', 0)} zaktualizowane, "
              f"{s['pominiete']} pominięte, {s['wiadomosci']} wiadomości z {s['sesje']} sesji.")
    elif args.cmd == "szukaj":
        for t in szukaj(" ".join(args.zapytanie)):
            print(f"[{t['sesja'][:8]}] {t['fragment']}")
    elif args.cmd == "statystyki":
        st = statystyki()
        print(f"📜 Kronika: {st['sesje']} sesji, {st['znaki']/1e6:.2f} MB tekstu.")
    else:
        ap.print_help()
