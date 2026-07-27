"""INDEX FALSORUM — Spis Twierdzeń Obalonych (organ pamięci Imperium).

Rejestruje twierdzenia, które **pomiar obalił**, i pilnuje, by nie żyły dalej w
korpusie jako fakt. Powód powstania (zmierzone 2026-07-20, NOTA N-7d2c4847):

  Pomiar 2026-07-19 udowodnił, że backtest jest LINIOWY, nie O(n²). Korekta poszła
  do LOG_ZMIAN, CODEX i pamięci — ale **nie do help-stringów kodu**. Trzy żywe
  narzędzia A/B dalej straszyły operatora „backtest O(n²)", więc biegi 1H szły na
  800 barach. To za krótkie okno wyprodukowało FAŁSZYWY werdykt „NEUTRALNE"
  (na 2000 barach: DVOL POMAGA +1.77 pp). Martwe twierdzenie zafałszowało wynik
  badawczy — korekta „dokument po dokumencie" nie łapie miejsc, o których nikt
  nie pamiętał. Ten organ zamienia korektę jednorazową w MECHANIZM.

Klasa wady jest ta sama co Warstwa 15 (ręczna liczba się rozjedzie) i Warstwa 16
(API-widma w docs) — tylko po stronie TWIERDZEŃ, nie liczb i ścieżek.

Obrona przed FAŁSZYWYM ALARMEM (lekcja z Księgi Wad #35: chroniczny FP uczy
ignorować bramkę — detektor bez tej obrony jest gorszy niż jego brak):
  • **Negacja nie jest trafieniem.** „backtest jest LINIOWY, **nie** O(n²)" to
    zdanie PRAWDZIWE i pożądane — zawiera frazę, ale ją prostuje. Linie z markerem
    negacji/korekty są pomijane.
  • **Historia nie jest kłamstwem** (Prawo I: nie falsyfikujemy historii). ACTA,
    archiwum, datowane snapshoty i sam ten plik są poza zasięgiem — wpis z 2026-07-05
    mówiący „O(n²)" był prawdą swojego czasu.
  • Trafienie to NUDGE („sprawdź to"), nie wyrok — jak cała Księga Wad.

Nazwa rzymska (ZASADA NOMENKLATURY): index falsorum = „spis rzeczy fałszywych".
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "bibliotheca_ulpia" / "dane" / "index_falsorum.jsonl"

POLA = ("data", "fraza", "poprawna_teza", "obalone_przez", "zrodlo")

# Katalogi trzymane poza zasięgiem: historia (Prawo I) i magazyn.
KATALOGI_POMIJANE = ("archiwum", ".git", "raporty", "wrzutnia", "bibliotheca_ulpia",
                     "dane", "__pycache__", "tests")

# Dokumenty-kroniki: ich treść to datowana prawda swojego czasu, nie żywe twierdzenie.
PLIKI_POMIJANE = ("LOG_ZMIAN.md", "PAMIEC_SESJI.md", "PAMIEC_SESJI_ARCHIWUM.md",
                  "index_falsorum.py")

# Markery negacji/korekty — linia, która frazę PROSTUJE, nie głosi.
# (Ta sama filozofia co _NEGACJA_TWARDA w refleksja_pamieci.py po Księdze Wad #35.)
# DWIE KLASY MARKERÓW — rozdzielone po pomiarze 2026-07-20 (nie z góry):
#
# Pierwsza wersja traktowała samo „nie" w linii jako dowód sprostowania. Sweep na
# twierdzeniu „Fujitsu 8 GB" (obalonym pomiarem: 15.88 GB) znalazł 2 z 5 miejsc —
# 3 umknęły, bo ich linie zawierały „nie" negujące COŚ INNEGO:
#   ROADMAP:69  „Obliczenia ciężkie: przez API, NIE lokalnie (Fujitsu, 8GB RAM)"
# Zdanie głosi obaloną liczbę i jednocześnie neguje lokalność obliczeń. Szeroki marker
# zamienił detektor w ślepca — czyli w dokładnie to, przed czym ostrzega komentarz niżej.
#
# NEGACJA musi dotyczyć FRAZY, więc liczy się tylko TUŻ PRZED nią (≤ ZASIEG_NEGACJI zn.):
#   „LINIOWY, nie O(n²)"          → odległość 0  → sprostowanie ✅
#   „nie lokalnie (Fujitsu, 8GB)" → odległość 10 → NIE dotyczy liczby ✅ (trafienie)
# GRANICE SŁÓW obowiązkowe: podciąg „nie " trafia w środek słowa „lokal-NIE (", przez co
# zdanie „przez API, nie lokalnie (Fujitsu, 8GB RAM)" (ROADMAP:69) uchodziło za sprostowanie
# i obalona liczba przeżyła. Zmierzone 2026-07-20 — dlatego \b, nie `in`.
NEGACJA_RE = re.compile(r"\bnie\b|\bNIE\b|≠|!=|\bzamiast\b", re.IGNORECASE)
ZASIEG_NEGACJI = 8

# KOREKTA JAWNA jest jednoznaczna (mówi wprost „to było błędne"), więc wolno jej stać
# gdziekolwiek w oknie — także gdy zdanie zawija się przez granicę linii.
KOREKTA_JAWNA = ("obalon", "OBALON", "błędn", "BŁĘDN", "bledn", "dawn", "DAWN", "mylon",
                 "premisa", "korekt", "KOREKT", "sprostow", "historyczn")


def _dzis() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _linia(rekord: dict) -> str:
    return json.dumps(rekord, ensure_ascii=False, sort_keys=True)


def wczytaj(sciezka: Path = LEDGER) -> list[dict]:
    """Czyta CAŁY spis, łącznie z wycofaniami (jeden rekord na linię). Brak pliku → []."""
    if not sciezka.exists():
        return []
    return [json.loads(ln) for ln in sciezka.read_text(encoding="utf-8").splitlines()
            if ln.strip()]


def aktywne(sciezka: Path = LEDGER) -> list[dict]:
    """Frazy obecnie pod strażą — bez wycofanych (ostatni rekord dla frazy wygrywa)."""
    stan: dict[str, dict] = {}
    for r in wczytaj(sciezka):
        stan[r["fraza"]] = r
    return [r for r in stan.values() if not r.get("wycofane")]


def wycofaj(*, fraza: str, powod: str, data: str | None = None,
            sciezka: Path = LEDGER) -> bool:
    """Wycofuje frazę ze straży (append-only nagrobek — historia zostaje, Prawo I).

    Powód istnienia (zmierzone 2026-07-20, w pierwszej godzinie życia organu): fraza
    `8\\s?GB\\s+RAM` trafiła w „15.**88 GB RAM**" (brak granicy liczby), a `O\\(n²\\)`
    w opis CUDZEGO algorytmu — obalone było twierdzenie „BACKTEST jest O(n²)", nie sama
    notacja. Bez wycofania źle dobrana fraza zostawałaby wiecznym fałszywym alarmem,
    czyli dokładnie wadą #35 z Księgi Wad (chroniczny FP uczy ignorować bramkę).
    """
    if not powod or not powod.strip():
        raise ValueError("powod wycofania jest wymagany (dlaczego fraza była zła)")
    if not any(r["fraza"] == fraza for r in wczytaj(sciezka)):
        raise ValueError(
            f"wycofaj: brak frazy '{fraza}' w spisie — nie wycofujemy czegoś, czego nie ma")
    rekord = {"data": data or _dzis(), "fraza": fraza, "poprawna_teza": "",
              "obalone_przez": "", "zrodlo": "", "wycofane": powod}
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(_linia(rekord) + "\n")
    return True


def dodaj(*, fraza: str, poprawna_teza: str, obalone_przez: str, zrodlo: str = "",
          data: str | None = None, sciezka: Path = LEDGER) -> bool:
    """Dopisuje obalone twierdzenie. Zwraca czy dopisano (idempotencja po FRAZIE).

    `obalone_przez` jest OBOWIĄZKOWE (Prawo I, KANDYDAT ≠ PRAWDA): twierdzenie
    trafia tu wyłącznie z POMIARU/dowodu, nigdy z opinii — inaczej organ stałby się
    narzędziem cenzury poglądów zamiast rejestrem faktów.
    """
    if not fraza or not fraza.strip():
        raise ValueError("fraza jest wymagana")
    if not obalone_przez or not obalone_przez.strip():
        raise ValueError(
            "obalone_przez jest wymagane — twierdzenie wpisujemy TYLKO z dowodu "
            "(pomiar/recenzja/decyzja Cezara), nigdy z opinii (Prawo I)")
    try:
        re.compile(fraza)
    except re.error as e:
        raise ValueError(f"fraza musi być poprawnym wyrażeniem regularnym: {e}") from e
    # DEDUP WOBEC AKTYWNYCH, NIE WOBEC HISTORII (naprawa 2026-07-27, złapana na sobie).
    # Poprzednio porównywaliśmy z `wczytaj()`, czyli z CAŁYM ledgerem razem z rekordami
    # wycofanymi — a ledger jest append-only, więc wycofany wpis zostaje w pliku na zawsze.
    # Efekt: raz wycofanej frazy NIE DAŁO SIĘ ponownie zarejestrować. Normalna ścieżka
    # poprawiania wpisu (wycofaj → dodaj z lepszą treścią) cicho gubiła twierdzenie: strażnik
    # tracił frazę, a `dodaj` zwracał False, co czyta się jak nieszkodliwe „już jest".
    # Zmierzone na żywym organie: INDEX spadł z 7 pozycji na 6 i zameldował „korpus czysty",
    # choć właśnie przestał pilnować obalonej tezy o U4. Milczenie udające wynik.
    if any(r.get("fraza") == fraza for r in aktywne(sciezka)):
        return False
    rekord = {"data": data or _dzis(), "fraza": fraza, "poprawna_teza": poprawna_teza,
              "obalone_przez": obalone_przez, "zrodlo": zrodlo}
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    with sciezka.open("a", encoding="utf-8") as f:
        f.write(_linia(rekord) + "\n")
    return True


# Zdanie prostujące potrafi przejść przez granicę linii (zawijanie prozy/docstringów),
# więc marker szukamy w OKNIE, nie w jednej linii. Zmierzone 2026-07-20 przy pierwszym
# biegu organu: scriba_codex.py:135 „sugestia O(n^2) została" / :136 „obalona pomiarem" —
# detektor jednoliniowy zgłosił sprostowanie jako kłamstwo (klasa FP z Księgi Wad #35).
KONTEKST_LINII = 2


def _linia_prostuje(linia: str) -> bool:
    """Czy linia zawiera JAWNĄ korektę (mówi wprost, że twierdzenie było błędne)?"""
    return any(m in linia for m in KOREKTA_JAWNA)


def _negacja_przy(linia: str, start: int, dopasowanie: str = "") -> bool:
    """Czy negacja dotyczy TEJ frazy — stoi tuż przed nią albo w jej obrębie?

    Wewnątrz dopasowania, bo wzorzec kodujący twierdzenie bywa rozciągnięty
    („backtest … O(n²)"), a negacja siedzi w środku: „backtest LINIOWY, **nie** O(n²)".
    """
    przed = linia[max(0, start - ZASIEG_NEGACJI - 4):start]
    return bool(NEGACJA_RE.search(przed + dopasowanie))


def _okno_prostuje(linie: list[str], i: int) -> bool:
    """Czy w oknie ±KONTEKST_LINII stoi JAWNA korekta (zdanie może zawijać linie)?"""
    lo = max(0, i - KONTEKST_LINII)
    return any(_linia_prostuje(l) for l in linie[lo:i + KONTEKST_LINII + 1])


def _pomijany(sciezka: Path, korzen: Path) -> bool:
    if sciezka.name in PLIKI_POMIJANE:
        return True
    return any(cz in KATALOGI_POMIJANE for cz in sciezka.relative_to(korzen).parts[:-1])


def przeszukaj(korzen: Path | None = None, wpisy: list[dict] | None = None,
               rozszerzenia: tuple[str, ...] = (".py", ".md")) -> list[dict]:
    """Sweep korpusu: gdzie obalone twierdzenie wciąż jest GŁOSZONE jako fakt.

    Zwraca listę {plik, linia_nr, linia, fraza, poprawna_teza}. Pusta lista = czysto.
    """
    korzen = korzen or ROOT
    wpisy = aktywne() if wpisy is None else wpisy
    if not wpisy:
        return []
    skompilowane = [(re.compile(w["fraza"]), w) for w in wpisy]
    trafienia = []
    for plik in korzen.rglob("*"):
        if not plik.is_file() or plik.suffix not in rozszerzenia:
            continue
        if _pomijany(plik, korzen):
            continue
        try:
            tekst = plik.read_text(encoding="utf-8")
        except Exception:
            continue
        # Szybkie odsianie: jeśli ŻADNA fraza nie występuje w całym pliku, nie ma po co
        # iterować po liniach. Sweep leci na starcie KAŻDEJ sesji, więc koszt ma znaczenie.
        # ZMIERZONE (nie szacowane): 1.91 s → 0.99 s (~1.9×), wynik identyczny. Reszta kosztu
        # to samo czytanie ~500 plików korpusu — tam regex już nie jest wąskim gardłem.
        if not any(wzor.search(tekst) for wzor, _ in skompilowane):
            continue
        linie = tekst.splitlines()
        for i, linia in enumerate(linie):
            nr = i + 1
            if _okno_prostuje(linie, i):
                continue
            for wzor, wpis in skompilowane:
                m = wzor.search(linia)
                if m and not _negacja_przy(linia, m.start(), m.group()):
                    trafienia.append({
                        "plik": str(plik.relative_to(korzen)).replace("\\", "/"),
                        "linia_nr": nr, "linia": linia.strip()[:160],
                        "fraza": wpis["fraza"], "poprawna_teza": wpis.get("poprawna_teza", ""),
                    })
    return trafienia


def raport() -> str:
    """Zero-tokenowy raport stanu spisu (do hooka/konsoli)."""
    wpisy = aktywne()
    if not wpisy:
        return "📕 INDEX FALSORUM: spis pusty — brak zarejestrowanych obalonych twierdzeń."
    traf = przeszukaj()
    naglowek = f"📕 INDEX FALSORUM: {len(wpisy)} obalonych twierdzeń pod strażą"
    if not traf:
        return f"{naglowek} — korpus czysty ✅ (żadne nie żyje dalej jako fakt)."
    linie = [f"{naglowek} — ⚠️ {len(traf)} miejsc głosi obalone twierdzenie:"]
    for t in traf[:20]:
        linie.append(f"   {t['plik']}:{t['linia_nr']}  → {t['poprawna_teza']}")
    return "\n".join(linie)


if __name__ == "__main__":
    print(raport())
