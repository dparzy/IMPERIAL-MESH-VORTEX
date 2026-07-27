"""🏷️ NOMENCLATOR — Strażnik Imion Imperium (warstwa 2 anty-redundancyjna Hyginusa).

W Rzymie *nomenclator* był niewolnikiem idącym u boku pana i szeptał mu imiona mijanych
osób: „tego już znasz". Tu robi dokładnie to samo z PLONEM Bibliotekarza (Hyginusa) — czyta
nazwy proponowanych kandydatów i szepcze sędziemu: **to imię Imperium już nosi**.

POWÓD ISTNIENIA (zmierzone 2026-07-27, wachta po replikacji A/B U4):
Zwiad proponuje moduły, które JUŻ MAMY — **39.3% kandydatów** nazywa pojęcie obecne w kodzie
(VPIN → `VPIN_50`; Value Area → VP-01; Kelly → IUSTITIA; CVD/funding → wskaźniki; Kalman →
`exp_kalman`; triple_barrier → W-357; DSR/PBO → koloseum). Próbowaliśmy leczyć to PROMPTEM
(U4: wstrzyknięcie 87 kluczy + polecenie „nie proponuj duplikatów") i **zmierzyliśmy, że to
nie działa**: 256 biegów A/B dało −0.7 pp, CI [−7.3, +6.0], p=0.888, przy koszcie 1.49×.

Sedno diagnozy: **deklaracja modelu „ten kandydat nie dubluje" jest bezwartościowa** — padała
przy 100% kandydatów, także przy VPIN_TOKSYCZNOSC, który dublował Z-01. Liczy się `grep`,
nie zapewnienie. NOMENCLATOR jest tym grepem, wykonanym ZANIM cząstka trafi do kolejki.

DLACZEGO ORGAN, A NIE FUNKCJA W NARZĘDZIU POMIAROWYM (Prawo XVI — jedno źródło prawdy):
detektor istniał od 07-21 i był hartowany dwoma naprawami (ślepota na `WIELKIE_Z_PODKRESLENIEM`,
4 z 7 formatów nagłówka sklejające plon) — ale żył WYŁĄCZNIE w stanowisku pomiarowym
`narzedzia/ab_plon_hyginusa.py`. Mierzący miał przyrząd, mierzony nie. To była utrata
potencjału (Prawo XV): płaciliśmy modelowi za deklarację bez wartości, mając obok darmowy
detektor. Kod został tu PRZENIESIONY, nie skopiowany — `ab_plon_hyginusa` importuje z tego
organu, więc pomiar i produkcja nie mogą się rozjechać.

CO SPRAWDZA (i czego świadomie NIE sprawdza):
  • ✅ Czy NAZWA kandydata (nagłówek bloku) trafia w pojęcie żyjące w naszym kodzie.
  • ❌ NIE czyta ciała bloku. To poprawka na zmierzony błąd pomiarowy: uzasadnienie kandydata
    wymienia nasze moduły w ZAPRZECZENIACH („istnieje V-03 CVD, ale to wolumen transakcyjny"),
    więc liczenie wzmianek karałoby kandydata za to, że zna Imperium. Nazwa mówi CO jest
    proponowane; ciało mówi, jak to uzasadniono.
  • ❌ NIE orzeka, że kandydat jest bezwartościowy. „Nosi znane imię" ≠ „nie wnosi nic” —
    OFI kontra IMBALANCE BARS to ten sam wyraz przy różnych pojęciach (patrz leksykon).

WERDYKT JEST MONOTONICZNIE OSTROŻNY (ZASADA WPIĘCIA — zero wpływu na ścieżkę decyzyjną):
organ wyłącznie DOKŁADA adnotację do cząstki. Nigdy nie usuwa kandydata, nie przerywa zwiadu
i nie przepuszcza niczego, co przeszłoby bez niego. Sędzią pozostaje człowiek — NOMENCLATOR
podaje mu listę imion do sprawdzenia, żeby nie czytał 21 kandydatów na oślep.
"""
from __future__ import annotations

import functools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# ── Leksykon pojęć, które Imperium JUŻ POSIADA ───────────────────────────────────
# PIERWSZA WERSJA BYŁA ZEPSUTA I ZŁAPAŁ TO POMIAR, NIE TEST (2026-07-21): leksykon budowany
# z nazw plików modułów flagował 95% bloków w OBU ramionach — miara nasycona nie odróżnia
# niczego. Jednocześnie gubiła prawdziwe duplikaty wskazane w sądzie nad kolejką, bo pojęcia
# żyjące pod rzymskimi imionami (Kelly → IUSTITIA) nie mają pliku o swojej nazwie.
#
# Dlatego leksykon jest KURATORSKI i PRECYZYJNY: pojęcie z literatury → token, który MUSI
# istnieć w kodzie. Weryfikacja jest automatyczna (`niezweryfikowane()` + test), więc wpis,
# który przestanie odpowiadać rzeczywistości, zapali się w bramce zamiast cicho kłamać.
# Klucz = wzorzec szukany w prozie kandydata; wartość = dowód w kodzie.
KONCEPTY_IMPERIUM = {
    r"\bvpin\b": "VPIN",
    r"\bkelly\b": "kelly",
    r"\bvalue area\b|\bvolume profile\b": "volume_profile",
    r"\bcvd\b|cumulative volume delta": "CVD",
    r"funding rate|\bfunding\b": "funding",
    r"\bkalman\b": "kalman",
    r"triple[- ]barrier": "triple_barrier",
    r"meta[- ]label": "meta_labeling",
    r"deflated sharpe|\bdsr\b": "deflated",
    r"\bpbo\b|backtest overfitting": "pbo",
    r"purged|combinatorial cross": "purged",
    r"\bhurst\b": "hurst",
    r"permutation entropy|\bpermen\b": "permutacyjna",
    r"fear (and |& )?greed": "fear_greed",
    r"open interest": "open_interest",
    r"\bamihud\b": "amihud",
    r"yang[- ]zhang": "yang_zhang",
    r"\bsupertrend\b": "supertrend",
    r"\bichimoku\b": "ichimoku",
    r"\bvwap\b": "vwap",
    r"bollinger": "BBANDS",
    r"\bmacd\b": "MACD",
    r"\brsi\b": "RSI",
    r"\badx\b": "ADX",
    r"\batr\b": "ATR",
    r"conformal": "konformalna",
    r"change[- ]point|\bbocpd\b": "changepoint",
    r"jump model|\bviterbi\b": "viterbi",
    r"path signature": "signature",
    r"feature importance|\bmda\b": "feature_importance",
    r"multiplicative weights|\bmwu\b": "mwu",
    r"walk[- ]forward": "walk_forward",
}
# ŚWIADOMIE USUNIĘTE Z LEKSYKONU (zmierzone 2026-07-21, po wykluczeniu samo-dowodu):
#  • „order flow imbalance / OFI" — Imperium ma IMBALANCE BARS (W-356, próbkowanie barów
#    wg nierównowagi), co jest INNYM pojęciem niż sygnał OFI z książki zleceń. Wpis
#    oskarżał zwiad o duplikat przy pomyśle, którego rój naprawdę nie posiada — a sam
#    kandydat poprawnie zauważył różnicę („istnieje V-03 CVD, ale to wolumen transakcyjny,
#    nie książkowy"). Miara myliła się, model miał rację.
#  • „hidden markov / HMM" — w kodzie występuje wyłącznie w DOCSTRINGU porównawczym
#    („jump model bije HMM trwałością stanów"). Wzmianka w komentarzu nie jest modułem;
#    Imperium świadomie wybrało jump model, więc HMM nie jest rzeczą, którą posiadamy.

# PLIKI WYŁĄCZONE Z KORPUSU DOWODOWEGO — moduły, które o pojęciach MÓWIĄ, zamiast je
# realizować. Bez tego weryfikacja czyta własną deklarację jako dowód (patrz `_korpus_kodu`).
_POZA_KORPUSEM = frozenset({
    "nomenclator.py",           # ten plik: deklaruje leksykon, więc każdy wpis „dowodziłby" siebie
    "ab_plon_hyginusa.py",      # stanowisko pomiarowe: cytuje pojęcia w prozie o pomiarze
})


@functools.lru_cache(maxsize=1)
def _korpus_kodu() -> str:
    """Żywy kod `imperium/` + `narzedzia/` jako jeden tekst — BEZ modułów z `_POZA_KORPUSEM`.

    WYKLUCZENIE SIEBIE JEST ISTOTĄ, NIE DETALEM (zmierzone 2026-07-21): pierwsza wersja
    skanowała cały korpus RAZEM z plikiem deklarującym leksykon, więc każdy wpis znajdował
    „dowód" we własnej linijce i weryfikacja przechodziła ZAWSZE. Miara ogłaszała
    „wszystkie pojęcia potwierdzone w kodzie", a wpis `order flow imbalance → order_flow`
    nie miał w Imperium ŻADNEGO odpowiednika poza samym sobą — i oskarżał zwiad o duplikat
    przy pomyśle, którego rój naprawdę nie ma. Weryfikacja czytająca własną deklarację jako
    dowód to bramka, która przy awarii wygląda na sprawną.

    WYKLUCZENIE ROZSZERZONE PRZY PRZENOSINACH DO ORGANU (2026-07-27): dawniej wystarczyło
    pominąć `__file__`, bo leksykon i stanowisko pomiarowe były JEDNYM plikiem. Po
    wyodrębnieniu organu `ab_plon_hyginusa.py` wpadłby do korpusu — a jest pełen prozy
    o mierzonych pojęciach („kandydat VPIN_TOKSYCZNOSC dublował Z-01"). Samo-dowód
    przeniósłby się wtedy do sąsiedniego pliku i znowu wyglądałby na sprawną bramkę.
    """
    czesci = []
    for katalog in ("imperium", "narzedzia"):
        for sciezka in (ROOT / katalog).rglob("*.py"):
            if "__pycache__" in str(sciezka) or sciezka.name in _POZA_KORPUSEM:
                continue
            czesci.append(sciezka.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(czesci).lower()


def niezweryfikowane() -> list:
    """Pojęcia z leksykonu, których DOWODU nie ma dziś w kodzie (Prawo I: leksykon nie kłamie).

    Pusta lista = każdy wpis reprezentuje realnie istniejący moduł. Niepusta = wpis
    przeterminowany albo literówka — miara duplikatów oskarżałaby o posiadanie czegoś,
    czego Imperium nie ma."""
    kod = _korpus_kodu()
    return [wzor for wzor, dowod in KONCEPTY_IMPERIUM.items() if dowod.lower() not in kod]


@functools.lru_cache(maxsize=1)
def leksykon_roju() -> tuple:
    """Skompilowane wzorce pojęć, które rój JUŻ posiada (tylko zweryfikowane w kodzie)."""
    zle = set(niezweryfikowane())
    return tuple((wzor, re.compile(wzor, re.IGNORECASE))
                 for wzor in KONCEPTY_IMPERIUM if wzor not in zle)


# Nagłówek kandydata: opcjonalne '###'/'-', opcjonalne '**', a potem ALBO numer z
# separatorem ('1.', '1)', '1:'), ALBO samo słowo „Kandydat" z etykietą ('Kandydat A:',
# 'Kandydat 1:').
#
# NAWRÓT KLASY, nie nowa wada (zmierzone 2026-07-27 przy sądzie nad kolejką). Wzorzec był
# już raz poprawiany — wtedy dołożono JEDEN brakujący wariant składni zamiast domknąć klasę
# „ślepa plama detektora na wariant składni" (Księga Wad). Pomiar siedmiu formatów realnie
# występujących w kolejce pokazał, że 4 z 7 nadal sklejały cały plon w jeden blok:
#   ### Kandydat A: X · ### Kandydat 1: X · 1: X · - **Kandydat: X**
# Skutek: licznik kandydatów kłamał W DÓŁ, a sklejony blok ma jeden nagłówek, więc miara
# duplikatów widziała nazwę wyłącznie PIERWSZEGO kandydata z każdej sklejki.
# WCIĘCIE JEST CZĘŚCIĄ DEFINICJI, NIE OZDOBĄ (zmierzone przy tej samej naprawie). Pierwsza
# wersja poprawki dopisała swobodne `\s*` w środku wzorca, co zniosło limit `^\s{0,3}` — i
# wzorzec zaczął uznawać za kandydatów ZAGNIEŻDŻONE KROKI instrukcji („1. Oblicz surowy SR",
# wcięte 5 spacjami), dokładając 12 widm w jednym rekordzie. Kandydat stoi przy lewej
# krawędzi; to, co wcięte pod nim, jest jego treścią. Dlatego wszystkie odstępy wewnątrz są
# ograniczone, a po numerze wymagana jest spacja (inaczej „2.5" byłoby nagłówkiem).
#
# ETYKIETA MUSI KOŃCZYĆ SIĘ GRANICĄ, NIE `kandydat\w*` (recenzja cubic PR #134, zweryfikowana
# pomiarem 2026-07-27). Swobodny przyrostek wpuszczał POLSKĄ ODMIANĘ z prozy jako nowy
# nagłówek: „Kandydatura: opis" liczyło się jako kandydat, zawyżając licznik i mianownik
# odsetka duplikatów. Większość odmian odpadała sama („Kandydatem jest VPIN: tak",
# „Kandydaci: lista"), bo po etykiecie wolno stać najwyżej 3 znakom przed dwukropkiem —
# dlatego wada była WĄSKA, ale realna. Na żywym korpusie 0 wystąpień, więc naprawa nie
# rusza żadnej opublikowanej liczby (zweryfikowane `przelicz` przed i po: zero dryfu).
#
# PIERWSZA POPRAWKA BYŁA ZA SŁABA I ZŁAPAŁ TO WŁASNY TEST: samo usunięcie `\w*` nie
# wystarczyło, bo slot etykiety `[A-Za-z0-9]{0,3}` dalej połykał „ura" z „Kandydatura:".
# Dopiero WYMÓG SEPARATORA po słowie („kandydat" + spacja + etykieta, albo od razu `:`)
# zamyka klasę. Zawężanie na oślep byłoby równie złe — stąd test trzyma OBIE strony granicy.
# Wspierane formy pozostają wszystkie: „Kandydat:", „Kandydat A:", „Kandydat 1:".
_NAGLOWEK = re.compile(
    r"(?m)^[ \t]{0,3}(?:[-*+][ \t])?(?:#{1,6}[ \t]?)?(?:\*\*)?"
    r"(?:\d{1,2}[.):](?:\*\*)?[ \t]|kandydat(?:[ \t]+[A-Za-z0-9]{1,3})?[ \t]?[:.])",
    re.IGNORECASE)


# Miara duplikatów porównuje NAZWĘ kandydata z leksykonem roju, a nazwy modułów piszemy
# WIELKIMI_Z_PODKREŚLENIEM. Podkreślenie jest w regexie znakiem SŁOWA, więc `\bvpin\b` NIE
# trafia w `VPIN_TOKSYCZNOSC` — dokładnie ten kandydat dublował Z-01 (NeuronToxicFlow,
# VPIN_50) i przeszedł jako „nowy". Normalizujemy podkreślenia do spacji przed dopasowaniem:
# to naprawia miarę, nie ruszając kuratorowanych wzorców (myślnik działał od zawsze, bo nie
# jest znakiem słowa — stąd `Half-Kelly` trafiał, a `KELLY_FRACTION` nie).
def _do_dopasowania(naglowek: str) -> str:
    return naglowek.replace("_", " ")


def podziel_kandydatow(tekst: str) -> list:
    """Rozbija plon na bloki kandydatów (numerowana lista, także pod nagłówkiem markdown).

    Brak numeracji → cały tekst jako jeden blok: plon bez struktury to nadal plon, a
    zwrócenie pustej listy zaniżałoby ramię, które akurat odpowiedziało prozą (Prawo I).
    """
    if not tekst or not tekst.strip():
        return []
    granice = [m.start() for m in _NAGLOWEK.finditer(tekst)]
    if not granice:
        return [tekst.strip()]
    bloki = []
    for i, poczatek in enumerate(granice):
        koniec = granice[i + 1] if i + 1 < len(granice) else len(tekst)
        blok = tekst[poczatek:koniec].strip()
        if blok:
            bloki.append(blok)
    return bloki or [tekst.strip()]


def _naglowek_bloku(blok: str) -> str:
    """Linia, w której kandydat jest NAZWANY (pierwsza niepusta linia bloku)."""
    for linia in blok.splitlines():
        if linia.strip():
            return linia
    return ""


def policz_duplikaty(tekst: str, leksykon) -> tuple:
    """(ile kandydatów NAZYWA pojęcie, które rój już ma; ile bloków; trafione pojęcia).

    LICZYMY WYŁĄCZNIE NAGŁÓWEK KANDYDATA, nie całe ciało — i to jest poprawka na błąd
    pomiarowy zmierzony 2026-07-21, który przekręcał cały A/B. Blok U4 każe modelowi
    dopisać do każdego kandydata zdanie „czy NIE dubluje istniejącego modułu", więc ramię
    ON WYMIENIA nasze moduły w ZAPRZECZENIACH („wnosi nowość; istnieje V-03 CVD, ale to
    wolumen transakcyjny"). Licząc wzmianki w całym bloku, karałem ramię dokładnie za to,
    że wykonuje polecenie — miara faworyzowałaby OFF niezależnie od jakości plonu.
    Nazwa kandydata mówi, CO jest proponowane; ciało bloku mówi, jak to uzasadniono.
    """
    bloki = podziel_kandydatow(tekst)
    trafione: set = set()
    dubel = 0
    for blok in bloki:
        naglowek = _do_dopasowania(_naglowek_bloku(blok))
        trafienia = {wzor for wzor, rx in leksykon if rx.search(naglowek)}
        if trafienia:
            dubel += 1
            trafione |= trafienia
    return dubel, len(bloki), sorted(trafione)


# ── WERDYKT DLA SĘDZIEGO — wpięcie w zwiad (2026-07-27) ──────────────────────────

def sprawdz(tekst: str, leksykon=None) -> dict:
    """Werdykt NOMENCLATORA nad plonem jednej cząstki — deterministyczny, 0 tokenów.

    Zwraca listę kandydatów, których NAZWA trafia w pojęcie żywe w kodzie, wraz z imieniem,
    które je zdradziło. To adnotacja dla sędziego, nie wyrok: `czysty=True` znaczy tylko
    „żadna nazwa nie trafiła w leksykon", a nie „kandydat jest nowy" — leksykon liczy dziś
    32 pojęcia, więc milczenie organu jest słabym dowodem, a jego głos mocnym.

    ASYMETRIA JEST ZAMIERZONA i wynika z pomiaru: deklaracja modelu „nie dubluje" miała 100%
    trafień i zerową wartość, więc dokładamy WYŁĄCZNIE sygnał pozytywny — nazwane trafienie
    z nazwanym powodem, który sędzia sprawdzi `grep`em w sekundę.
    """
    lex = leksykon_roju() if leksykon is None else leksykon
    podejrzani = []
    for blok in podziel_kandydatow(tekst):
        naglowek = _naglowek_bloku(blok)
        trafienia = sorted({wzor for wzor, rx in lex
                            if rx.search(_do_dopasowania(naglowek))})
        if trafienia:
            podejrzani.append({"nazwa": naglowek.strip()[:120], "pojecia": trafienia})
    bloki = podziel_kandydatow(tekst)
    return {
        "czysty": not podejrzani,
        "kandydatow": len(bloki),
        "podejrzanych": len(podejrzani),
        "podejrzani": podejrzani,
        "leksykon_pojec": len(lex),
    }


def do_slownika(werdykt: dict) -> dict:
    """Spłaszcza werdykt do zapisu w cząstce (JSONL) — bez zagnieżdżeń w polach liczbowych.

    Ten sam kształt co PROBATOR: `status` czytelny w meldunku, szczegóły obok. Dzięki temu
    BREVIARIUM i raporty mogą liczyć podejrzanych bez znajomości wnętrza organu."""
    return {
        "status": "czysty" if werdykt.get("czysty") else "podejrzany",
        "kandydatow": werdykt.get("kandydatow", 0),
        "podejrzanych": werdykt.get("podejrzanych", 0),
        "pojecia": sorted({p for w in werdykt.get("podejrzani", []) for p in w["pojecia"]}),
    }
