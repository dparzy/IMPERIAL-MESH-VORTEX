"""⚖️ LIBRA MESSIS — Waga Plonu: A/B jakości zwiadu Hyginusa.

Rzymska *libra* to waga szalkowa, *messis* — żniwo. Organ waży DWA RAMIONA tego samego
zwiadu na tej samej liście tematów i mówi, które przynosi lepszy plon. Odpowiada na dwa
pytania, których do dziś NIKT w Imperium nie zmierzył (rozkaz Cezara 2026-07-21):

  1. **U4 ON vs OFF** — czy blok świadomości systemu realnie tnie duplikaty? Sąd nad
     33 cząstkami (2026-07-21) pokazał kolejkę w dużej mierze redundantną i wskazał
     przyczynę: te biegi NIE miały U4. To była DIAGNOZA, nie pomiar różnicy.
  2. **Profile DISPENSATORA** — flash/high vs v4-pro+high na krytyce. Sam DISPENSATOR
     mówi wprost, że wpływ profilu na JAKOŚĆ jest NIEZMIERZONY, a profile to hipotezy
     kosztowe. Tu je konfrontujemy z plonem.

ŻELAZNE ZASADY TEGO ORGANU:

• **NIE dotyka produkcyjnej kolejki hipotez.** Woła `scout_temat` bezpośrednio, z pominięciem
  `raport()`, i pisze WYŁĄCZNIE do własnego rejestru pomiarowego. Powód zmierzony 2026-07-21:
  bieg weryfikacyjny `--dry-run` zaśmiecił produkcyjną kolejkę wpisami testowymi. Narzędzie,
  które mierzy, nie ma prawa zmieniać mierzonego stanu.

• **Ta sama zmienna na raz.** W A/B profili OBA ramiona krytykują TEN SAM plon zwiadu —
  inaczej różnica w krytyce mieszałaby się z losowością generacji (temperatura 0.4).

• **Cząstka → zapis → następna** (ZASADA ANALIZY CZĄSTKOWEJ): każdy pomiar ląduje w JSONL
  natychmiast, bieg jest wznawialny, a pad nie traci nic. Pasek postępu na stderr (Prawo XXIV).

• **Metryki deterministyczne, 0 tokenów** — liczone z tekstu plonu, nie opinią modelu.
  Werdykt końcowy wydaje Architekt (Opus) na ich podstawie; narzędzie DOSTARCZA LICZBY.

UCZCIWOŚĆ METRYKI DUPLIKATÓW (Prawo I): `duplikaty` to HEURYSTYKA — leksykon pojęć żywych
w kodzie kontra tekst kandydata. Nie jest sędzią prawdy o redundancji (tym jest człowiek
czytający kandydata). Jest natomiast MIARĄ PORÓWNAWCZĄ: liczona identycznie w obu ramionach,
więc RÓŻNICA między ramionami niesie informację, nawet jeśli poziom bezwzględny jest zaszumiony.
"""
from __future__ import annotations

import argparse
import functools
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REJESTR = ROOT / "bibliotheca_ulpia" / "dane" / "ab_plon_hyginusa.jsonl"

# Tematy zwiadu dla A/B — świadomie NIESKANOWANE wcześniej (kolejka na 2026-07-21 liczyła
# 34 cząstki), żeby żaden arm nie korzystał z tematu, o którym rój już coś wie. Osiem pozycji
# = zakres zatwierdzony przez Cezara: dość na różnicę, bez palenia budżetu na v4-pro.
TEMATY_AB = [
    "order flow imbalance queue dynamics limit order book",
    "volatility risk premium variance swap term structure",
    "cross-sectional momentum factor crowding decay",
    "market maker inventory risk adverse selection spread",
    "jump diffusion tail risk extreme value estimation",
    "correlation breakdown contagion crisis regime",
    "seasonality intraday periodicity time of day effects",
    "position sizing drawdown control risk of ruin",
]

# ZESTAW „RDZEŃ" — tematy o ZMIERZONEJ zdolności do produkowania duplikatów.
# Powód (zmierzone 2026-07-21): pierwszy bieg A/B na zestawie „nowe" dał 0 duplikatów w OBU
# ramionach. To nie był werdykt o U4, tylko dowód, że dobrałem tematy z obszarów, gdzie rój
# ma słabe pokrycie — miara nie miała czego mierzyć. Eksperyment o zdolności BLOKOWANIA
# duplikatów musi biec tam, gdzie duplikat jest MOŻLIWY. Te osiem tematów pochodzi z kolejki
# 33 cząstek zebranych BEZ U4 i dały tam 12 duplikatów na 24 kandydatów (50%) — czyli
# istnieje historyczny punkt odniesienia dla ramienia OFF na dokładnie tych tematach.
TEMATY_RDZEN = [
    "kelly criterion optimal bet sizing growth",
    "walidacja strategii tradingowej metody statystyczne przeuczenie backtestu",
    "kalibracja prawdopodobienstwa i ocena jakosci sygnalu",
    "market regime detection volatility filter",
    "market profile value area volume distribution auction theory",
    "trading psychology discipline probabilistic thinking edge",
    "mean reversion overextension bands entry",
    "backtest overfitting deflated sharpe multiple testing",
    # ── dobite 2026-07-21 (decyzja Cezara: domknąć U4 rozstrzygnięciem) ──
    # Celują wprost w pojęcia, które Imperium NA PEWNO posiada (leksykon + dowód w kodzie),
    # więc szansa na duplikat jest wysoka — a to jedyny sposób, by pomiar miał moc.
    "toxic order flow informed trading probability vpin",
    "long memory fractal dimension persistence hurst exponent",
    "entropy information theory market predictability",
    "perpetual futures funding rate open interest positioning",
    "volatility estimator range based high low efficiency",
    "adaptive moving average trend following crossover systems",
    "volume weighted average price execution benchmark",
    "illiquidity measure price impact per volume",
]

ZESTAWY = {"nowe": TEMATY_AB, "rdzen": TEMATY_RDZEN}

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


@functools.lru_cache(maxsize=1)
def _korpus_kodu() -> str:
    """Żywy kod `imperium/` + `narzedzia/` jako jeden tekst — BEZ tego pliku.

    WYKLUCZENIE SIEBIE JEST ISTOTĄ, NIE DETALEM (zmierzone 2026-07-21): pierwsza wersja
    skanowała cały korpus RAZEM z plikiem deklarującym leksykon, więc każdy wpis znajdował
    „dowód" we własnej linijce i weryfikacja przechodziła ZAWSZE. Miara ogłaszała
    „wszystkie pojęcia potwierdzone w kodzie", a wpis `order flow imbalance → order_flow`
    nie miał w Imperium ŻADNEGO odpowiednika poza samym sobą — i oskarżał zwiad o duplikat
    przy pomyśle, którego rój naprawdę nie ma. Weryfikacja czytająca własną deklarację jako
    dowód to bramka, która przy awarii wygląda na sprawną.
    """
    ten_plik = Path(__file__).resolve()
    czesci = []
    for katalog in ("imperium", "narzedzia"):
        for sciezka in (ROOT / katalog).rglob("*.py"):
            if "__pycache__" in str(sciezka) or sciezka.resolve() == ten_plik:
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
_NAGLOWEK = re.compile(
    r"(?m)^[ \t]{0,3}(?:[-*+][ \t])?(?:#{1,6}[ \t]?)?(?:\*\*)?"
    r"(?:\d{1,2}[.):](?:\*\*)?[ \t]|kandydat\w*[ \t]?[A-Za-z0-9]{0,3}[ \t]?[:.])",
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


def zmierz(tekst: str, leksykon, probator: dict | None = None) -> dict:
    """Deterministyczne metryki plonu (0 tokenów)."""
    dubel, bloki, trafione = policz_duplikaty(tekst, leksykon)
    return {
        "kandydatow": bloki,
        "duplikaty": dubel,
        "duplikaty_pct": round(100 * dubel / bloki, 1) if bloki else None,
        "trafione_pojecia": trafione[:20],
        "cytatow_bib": len(re.findall(r"BIB-\d{3}", tekst or "")),
        "znakow": len(tekst or ""),
        "probator_status": (probator or {}).get("status"),
        "probator_czysty": (probator or {}).get("czysty"),
    }


def _zuzycie(glos) -> dict:
    """Koszt i tokeny OSTATNIEGO wywołania — z faktycznego `usage`, nie z szacunku.

    Koszt liczony wg taryfy z chwili WYWOŁANIA (DeepSeek bierze 2× w oknach szczytu),
    a nie z chwili raportu — i zapisujemy `szczyt`, żeby dało się później odtworzyć, po
    jakiej stawce liczyliśmy. Bez tego pola ten sam rekord przeliczony innego dnia mógłby
    dostać inną cenę i nikt by nie wiedział, która jest prawdziwa.
    """
    from datetime import datetime, timezone
    from imperium.cesarz.dispensator import czy_szczyt, koszt_usd, tokeny_rozumowania
    u = getattr(glos, "ostatnie_zuzycie", None)
    model = getattr(glos, "ostatni_model", None)
    teraz = datetime.now(timezone.utc)
    if u is None or model is None:
        return {"koszt_usd": None, "tokeny_rozumowania": None, "model": model,
                "szczyt": czy_szczyt(teraz)}
    return {"koszt_usd": koszt_usd(u, model, kiedy=teraz),
            "tokeny_rozumowania": tokeny_rozumowania(u),
            "model": model, "szczyt": czy_szczyt(teraz)}


# ── Rejestr pomiarowy (własny, NIGDY produkcyjna kolejka) ────────────────────────

def wczytaj(sciezka: Path = REJESTR) -> list:
    if not Path(sciezka).exists():
        return []
    out = []
    for ln in Path(sciezka).read_text(encoding="utf-8").splitlines():
        if ln.strip():
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
    return out


def zapisz(rekord: dict, sciezka: Path = REJESTR) -> None:
    Path(sciezka).parent.mkdir(parents=True, exist_ok=True)
    with open(sciezka, "a", encoding="utf-8") as f:
        f.write(json.dumps(rekord, ensure_ascii=False) + "\n")


def zrobione(bieg: str, sciezka: Path = REJESTR) -> set:
    """(temat, ramię, runda) już ZMIERZONE — wznawianie nie płaci drugi raz za to samo.

    Rekord o statusie 'blad' NIE liczy się jako zrobiony: zerwane łącze ma zostać
    ponowione przy następnym biegu, inaczej porażka utrwalałaby się jako wynik.

    RUNDA jest częścią klucza, bo powtórzenie tego samego tematu to NOWE LOSOWANIE
    (temperatura 0.4), a więc nowa obserwacja — bez tego wymiaru nie dało się zwiększyć
    próby inaczej niż wymyślaniem kolejnych tematów. Stare rekordy bez pola `runda`
    czytamy jako rundę 1 (wsteczna zgodność: nie unieważniamy pomiarów sprzed zmiany).
    """
    return {(r["temat"], r["ramie"], r.get("runda", 1)) for r in wczytaj(sciezka)
            if r.get("bieg") == bieg and r.get("status") != "blad"}


def _postep(i: int, n: int, opis: str) -> None:
    print(f"[{i}/{n}] {opis}", file=sys.stderr, flush=True)


# Odstępy ponowień (s) — rosnące, żeby chwilowy zryw łącza nie zabijał całego biegu.
# ZMIERZONE 2026-07-21: pierwszy pełny bieg padł na `openai.APITimeoutError` przy 11 z 16
# pomiarów. Cząstki przetrwały (ZASADA ANALIZY CZĄSTKOWEJ zadziałała), ale bieg wymagał
# ręcznego wznowienia — a łącze Cezara bywa zrywne. Jednostka, która nie wstała po
# ponowieniach, jest ZAPISYWANA jako błąd i bieg leci dalej: jeden zerwany temat nie może
# kosztować pozostałych.
PONOWIENIA = (5, 15, 45)


def _z_ponowieniem(wywolaj, opis: str):
    """Wykonuje wywołanie sieciowe, ponawiając przy błędzie. Zwraca (wynik, blad)."""
    ostatni = None
    for próba, przerwa in enumerate((*PONOWIENIA, None), 1):
        try:
            return wywolaj(), None
        except Exception as e:  # noqa: BLE001 — dowolna awaria sieci/API ma być przeżywalna
            ostatni = e
            if przerwa is None:
                break
            print(f"    ⚠️ {opis}: {type(e).__name__} — ponawiam za {przerwa}s "
                  f"(próba {próba}/{len(PONOWIENIA)})", file=sys.stderr, flush=True)
            time.sleep(przerwa)
    print(f"    🚨 {opis}: poddaję się po {len(PONOWIENIA)} ponowieniach ({ostatni})",
          file=sys.stderr, flush=True)
    return None, f"{type(ostatni).__name__}: {ostatni}"


# ── Bieg 1: U4 ON vs OFF ─────────────────────────────────────────────────────────

def bieg_u4(tematy=None, topk: int = 6, sciezka: Path = REJESTR,
            etykieta: str = "u4", runda: int = 1) -> int:
    """Ten sam temat skanowany ze świadomością systemu i bez niej. Metryka główna: duplikaty.

    `etykieta` oddziela zestawy tematów w rejestrze — mieszanie poligonu „nowe" (bez szans
    na duplikat) z „rdzeń" (duplikat możliwy) rozcieńczyłoby oba wyniki w jedną średnią,
    która nie opisuje żadnego z nich.
    """
    from narzedzia.bibliotekarz import scout_temat
    from imperium.cesarz.deepseek_glos import GlosImperium
    tematy = list(tematy or TEMATY_AB)
    leksykon = leksykon_roju()
    glos = GlosImperium()
    gotowe = zrobione(etykieta, sciezka)
    zadania = [(t, r) for t in tematy for r in ("on", "off")
               if (t, r, runda) not in gotowe]
    print(f"⚖️ LIBRA MESSIS — bieg {etykieta.upper()}: {len(zadania)} pomiarów "
          f"({len(gotowe)} już w rejestrze, pomijam)", file=sys.stderr, flush=True)
    for i, (temat, ramie) in enumerate(zadania, 1):
        _postep(i, len(zadania), f"U4={ramie:3} — {temat[:52]}")
        t0 = time.time()
        czastka, blad = _z_ponowieniem(
            lambda t=temat, r=ramie: scout_temat(glos, t, topk=topk, swiadomosc=(r == "on"),
                                                 krytyka=False, probator=True),
            f"zwiad U4={ramie}")
        if czastka is None:      # zapisujemy PORAŻKĘ, nie pomijamy jej po cichu (Prawo I)
            zapisz({"bieg": etykieta, "ramie": ramie, "temat": temat, "faza": "zwiad",
                    "runda": runda, "ts": time.time(), "status": "blad", "blad": blad}, sciezka)
            continue
        rec = {"bieg": etykieta, "ramie": ramie, "temat": temat, "faza": "zwiad",
               "runda": runda,
               "ts": time.time(), "czas_s": round(time.time() - t0, 1),
               "status": czastka.get("status"), "zrodla": czastka.get("zrodla", []),
               "plon": czastka.get("kandydaci", ""),
               **zmierz(czastka.get("kandydaci", ""), leksykon, czastka.get("probator")),
               **_zuzycie(glos)}
        zapisz(rec, sciezka)
    return len(zadania)


# ── Bieg 2: profile DISPENSATORA na krytyce ──────────────────────────────────────

def bieg_profile(tematy=None, topk: int = 6, sciezka: Path = REJESTR) -> int:
    """Krytyka TEGO SAMEGO plonu dwoma profilami: 'krytyka' (flash/high) vs 'osad' (pro/high).

    Plon zwiadu jest wspólny dla obu ramion — inaczej mierzylibyśmy losowość generacji,
    nie profil. Zwiad bierzemy z biegu U4 (ramię ON = dzisiejsze domyślne zachowanie),
    żeby nie płacić drugi raz za tę samą generację.
    """
    from narzedzia.bibliotekarz import krytyka_kandydatow, _fts_bezpieczne, _KONTRA_SUFIKS
    from imperium.cesarz.deepseek_glos import GlosImperium
    from imperium.pretorianie.probator import do_slownika, sprawdz
    from szukaj import szukaj  # type: ignore[import]

    zrodlowe = {r["temat"]: r for r in wczytaj(sciezka)
                if r.get("bieg") == "u4" and r.get("ramie") == "on" and r.get("plon")}
    tematy = [t for t in (tematy or TEMATY_AB) if t in zrodlowe]
    if not tematy:
        print("🚨 Brak plonu zwiadu do krytyki — uruchom najpierw bieg U4.",
              file=sys.stderr, flush=True)
        return 0
    leksykon = leksykon_roju()
    glos = GlosImperium()
    gotowe = zrobione("profile", sciezka)
    zadania = [(t, r) for t in tematy for r in ("krytyka", "osad")
               if (t, r, 1) not in gotowe]
    print(f"⚖️ LIBRA MESSIS — bieg PROFILE: {len(zadania)} pomiarów "
          f"({len(gotowe)} już w rejestrze, pomijam)", file=sys.stderr, flush=True)
    for i, (temat, ramie) in enumerate(zadania, 1):
        _postep(i, len(zadania), f"profil={ramie:8} — {temat[:48]}")
        t0 = time.time()
        kontra = szukaj(_fts_bezpieczne(f"{temat} {_KONTRA_SUFIKS}"), topk=topk,
                        tryb="hybrid", cichy=True, korpus="biblioteka")
        tekst, blad = _z_ponowieniem(
            lambda t=temat, r=ramie: krytyka_kandydatow(glos, zrodlowe[t]["plon"],
                                                        kontra, profil=r),
            f"krytyka profil={ramie}")
        if tekst is None:
            zapisz({"bieg": "profile", "ramie": ramie, "temat": temat, "faza": "krytyka",
                    "ts": time.time(), "status": "blad", "blad": blad}, sciezka)
            continue
        rec = {"bieg": "profile", "ramie": ramie, "temat": temat, "faza": "krytyka",
               "ts": time.time(), "czas_s": round(time.time() - t0, 1),
               "plon": tekst,
               **zmierz(tekst, leksykon, do_slownika(sprawdz(tekst, kontra))),
               **_zuzycie(glos)}
        zapisz(rec, sciezka)
    return len(zadania)


# ── Agregacja ────────────────────────────────────────────────────────────────────

def agreguj(bieg: str, sciezka: Path = REJESTR) -> dict:
    """Zwija rejestr do porównania ramion. Brak danych ramienia → ramię nieobecne (nie zero)."""
    # Rekordy błędu (zerwane łącze) NIE wchodzą do agregacji: nie mają metryk, a policzone
    # jako temat zaniżałyby średnie ramienia, które akurat trafiło na awarię sieci.
    rekordy = [r for r in wczytaj(sciezka)
               if r.get("bieg") == bieg and r.get("status") != "blad"]
    out: dict = {}
    for r in rekordy:
        out.setdefault(r["ramie"], []).append(r)

    def _srednia(lista, pole):
        wart = [x[pole] for x in lista if isinstance(x.get(pole), (int, float))]
        return round(sum(wart) / len(wart), 2) if wart else None

    podsumowanie = {}
    for ramie, lista in out.items():
        kand = sum(x.get("kandydatow") or 0 for x in lista)
        dubel = sum(x.get("duplikaty") or 0 for x in lista)
        koszty = [x["koszt_usd"] for x in lista if isinstance(x.get("koszt_usd"), (int, float))]
        podsumowanie[ramie] = {
            "tematow": len(lista),
            "kandydatow": kand,
            "duplikatow": dubel,
            "duplikaty_pct": round(100 * dubel / kand, 1) if kand else None,
            "cytatow_bib": sum(x.get("cytatow_bib") or 0 for x in lista),
            "podejrzanych": sum(1 for x in lista if x.get("probator_czysty") is False),
            "sr_znakow": _srednia(lista, "znakow"),
            "sr_czas_s": _srednia(lista, "czas_s"),
            "koszt_usd": round(sum(koszty), 6) if koszty else None,
            "tokeny_rozumowania": sum(x.get("tokeny_rozumowania") or 0 for x in lista),
        }
    return podsumowanie


def przelicz(sciezka: Path = REJESTR) -> int:
    """Przelicza metryki z ZAPISANEGO plonu — bez ani jednego wywołania API.

    Powód istnienia (i powód, dla którego rejestr trzyma surowy tekst, a nie same liczby):
    2026-07-21 poprawiłem miarę duplikatów PO biegu — leksykon potwierdzał sam siebie, a
    wzmianki w zaprzeczeniach liczyły się jak propozycje. Gdyby rejestr trzymał wyłącznie
    metryki, poprawka wymagałaby powtórzenia całego, płatnego biegu. Surowy plon czyni
    pomiar ODWRACALNYM: zmiana definicji miary nie kosztuje nic.

    Nadpisuje plik w miejscu (przez zapis tymczasowy), zachowując kolejność i surowy plon.
    """
    rekordy = wczytaj(sciezka)
    if not rekordy:
        return 0
    lex = leksykon_roju()
    zmienione = 0
    for r in rekordy:
        if r.get("status") == "blad" or "plon" not in r:
            continue
        nowe = zmierz(r.get("plon", ""), lex,
                      {"status": r.get("probator_status"), "czysty": r.get("probator_czysty")})
        if any(r.get(k) != v for k, v in nowe.items()):
            zmienione += 1
        r.update(nowe)
    tmp = Path(sciezka).with_suffix(".jsonl.tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rekordy),
                   encoding="utf-8")
    tmp.replace(sciezka)          # atomowo: przerwany zapis nie zostawia obciętego rejestru
    return zmienione


def raport_tekstowy(bieg: str, sciezka: Path = REJESTR) -> str:
    a = agreguj(bieg, sciezka)
    if not a:
        return f"⚖️ LIBRA MESSIS — bieg '{bieg}': brak pomiarów w rejestrze."
    kolumny = ["tematow", "kandydatow", "duplikatow", "duplikaty_pct", "cytatow_bib",
               "podejrzanych", "sr_znakow", "sr_czas_s", "koszt_usd", "tokeny_rozumowania"]
    linie = [f"⚖️ LIBRA MESSIS — bieg '{bieg}' (rejestr: {Path(sciezka).name})",
             "   " + "ramię".ljust(10) + "".join(k[:13].rjust(15) for k in kolumny)]
    for ramie, m in sorted(a.items()):
        linie.append("   " + ramie.ljust(10)
                     + "".join(str(m.get(k)).rjust(15) for k in kolumny))
    return "\n".join(linie)


# Górna granica liczby tematów w jednym biegu. Nie jest to limit techniczny, tylko HAMULEC
# KOSZTU: każdy temat to 2 płatne wywołania (po jednym na ramię), a ramię 'osad' idzie na
# v4-pro. Bez granicy literówka („--tematy 800") zamienia eksperyment za centy w rachunek.
_TEMATY_MAX = 50


def _tematy_arg(tekst: str) -> int:
    v = int(tekst)
    if not (1 <= v <= _TEMATY_MAX):
        raise argparse.ArgumentTypeError(
            f"--tematy musi być w [1, {_TEMATY_MAX}], podano: {tekst}")
    return v


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="LIBRA MESSIS — A/B jakości plonu Hyginusa")
    p.add_argument("bieg", choices=["u4", "profile", "raport", "przelicz"],
                   help="u4 = świadomość ON/OFF; profile = flash vs pro na krytyce; "
                        "raport = same liczby; przelicz = metryki z zapisanego plonu (0 API)")
    # Oba argumenty sterują ROZMIAREM PŁATNEGO biegu, więc walidujemy zakres przy parsowaniu,
    # a nie po fakcie (znana klasa z Księgi Wad: liczbowy argument kosztu bez granicy).
    # `--topk` reużywa walidatora Hyginusa — druga własna kopia rozjechałaby się z oryginałem.
    from narzedzia.bibliotekarz import _topk_arg
    p.add_argument("--topk", type=_topk_arg, default=6, help="fragmentów RAG na temat [1,20]")
    p.add_argument("--tematy", type=_tematy_arg, default=len(TEMATY_AB),
                   help=f"ile tematów z listy [1,{_TEMATY_MAX}] (mniej = taniej)")
    p.add_argument("--runda", type=int, default=1,
                   help="numer rundy — powtórzenie tych samych tematów to NOWE losowanie "
                        "(temperatura 0.4), czyli dodatkowe obserwacje do tej samej próby")
    p.add_argument("--zestaw", choices=sorted(ZESTAWY), default="nowe",
                   help="'nowe' = obszary słabo pokryte; 'rdzen' = tematy o ZMIERZONEJ "
                        "zdolności produkowania duplikatów (właściwy poligon dla U4)")
    a = p.parse_args(argv)
    tematy = ZESTAWY[a.zestaw][:max(1, a.tematy)]
    etykieta = "u4" if a.zestaw == "nowe" else f"u4_{a.zestaw}"
    if a.bieg == "raport":
        for b in ("u4", "u4_rdzen", "profile"):
            print(raport_tekstowy(b))
        return 0
    if a.bieg == "przelicz":
        print(f"⚖️ Przeliczono metryki z zapisanego plonu: {przelicz()} rekordów zmienionych "
              "(0 wywołań API)")
        for b in ("u4", "u4_rdzen", "profile"):
            print(raport_tekstowy(b))
        return 0
    if a.bieg == "u4":
        bieg_u4(tematy, topk=a.topk, etykieta=etykieta, runda=a.runda)
        print(raport_tekstowy(etykieta))
    else:
        bieg_profile(tematy, topk=a.topk)
        print(raport_tekstowy("profile"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
