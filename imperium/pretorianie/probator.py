"""
🛡️ PROBATOR — Strażnik Cytatów Imperium (warstwa 1 anty-halucynacyjna Hyginusa).

W Rzymie *probator* sprawdzał i DOPUSZCZAŁ — badał monetę przed obiegiem, rekruta przed
przysięgą. Tu bada PLON Bibliotekarza (Hyginusa) zanim trafi do kolejki hipotez: czy każde
źródło, na które się powołuje, NAPRAWDĘ było mu podane.

POWÓD ISTNIENIA (zmierzone, web 2026-07-21 — patrz pamięć `rozbudowa-hyginusa-modele-tryby-deepseek`):
DeepSeek V4-Pro halucynuje 94%, V4-Flash 96% na pytaniach wiedzy (AA-Omniscience,
„near-total overconfidence"). Z czterech typów halucynacji (factual, grounding, CITATION,
reasoning) **citation jest jedynym, który da się złapać DETERMINISTYCZNIE — bez modelu,
bez tokenów, bez kosztu.** Reszta warstw (faithfulness drugim modelem, self-consistency,
abstention) jest droga; ta jest darmowa, więc idzie pierwsza.

CO SPRAWDZA (i czego świadomie NIE sprawdza):
  • ✅ Czy cytowany BIB-xxx był W TYM PROMPCIE — nie „czy istnieje w bibliotece".
    To rozróżnienie jest całym sednem: model, który cytuje realną książkę, której mu NIE
    podano, konfabuluje tak samo jak ten, który wymyślił tytuł. Grounding to zgodność ze
    ŹRÓDŁEM POKAZANYM, nie z korpusem.
  • ✅ Czy cytowany numer chunku był wśród podanych chunków tego źródła.
  • ❌ NIE ocenia, czy teza WYNIKA z fragmentu (to faithfulness — warstwa 2, drugi model).
    PROBATOR mówi „powołał się na coś, czego nie widział", nigdy „teza jest fałszywa".

ABSTENCJA JEST POPRAWNYM WYNIKIEM (Prawo I): odpowiedź „fragmenty nic nie wnoszą" nie ma
cytatów i NIE jest halucynacją — karanie jej uczyłoby model konfabulować zamiast milczeć.

Werdykt jest MONOTONICZNIE OSTROŻNY: tylko dokłada ostrzeżenie do cząstki, nigdy nie
przepuszcza niczego, co przeszłoby bez niego (ZASADA WPIĘCIA — zero wpływu na ścieżkę decyzyjną).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# ── Składnia cytatu ─────────────────────────────────────────────────────────────────
# Księga Wad #53 („ślepa plama detektora na wariant składni"): detektor, który CHRONI,
# musi pokryć WSZYSTKIE formy zapisu celu, a nie tylko tę, którą akurat widzieliśmy.
# Formy spotykane w plonie: „BIB-006", „BIB 006", „bib-6", „[BIB-006_Autor_Tytul.pdf …]".
# Numer normalizujemy do 3 cyfr, więc „BIB-6" i „BIB-006" to TEN SAM identyfikator.
#
# Domknięcie to `(?!\d)`, a NIE `\b` — bo podkreślenie jest znakiem SŁOWNYM, więc `\b`
# nie zamyka się w „BIB-006_Carson_Tytul.pdf", czyli w najczęstszej formie, jaką model
# widzi w prompcie. Złapane własnym testem: detektor cytatów nie rozpoznawał cytatu.
# Wariant tej samej wady co Księga Wad #53 — i dowód, że test negatywny + pełen zestaw
# form zapisu to nie formalność.
_RE_BIB = re.compile(r"\bBIB[\s\-_]?(\d{1,4})(?!\d)", re.IGNORECASE)

# „chunk 8", „chunk: 8", „fragment 8" — numer chunku doklejony do cytatu (opcjonalny).
_RE_CHUNK = re.compile(r"\b(?:chunk|fragment)\s*[:#]?\s*(\d{1,6})(?!\d)", re.IGNORECASE)

# Ile znaków po identyfikatorze BIB przeszukujemy w poszukiwaniu numeru chunku.
# Wąsko celowo: „BIB-006 … 40 zdań dalej … chunk 8" to NIE jest cytat chunku 8.
_ZASIEG_CHUNKU = 60

# Zwroty abstencji — odpowiedź świadomie odmawiająca kandydatów (poprawny wynik, nie wada).
_ZWROTY_ABSTENCJI = (
    "brak fragmentów", "brak fragmentow", "nie niosą", "nie niosa", "nic wartościowego",
    "nic wartosciowego", "nie znajduję", "nie znajduje", "brak wartościowych",
    "brak wartosciowych", "nie zawierają", "nie zawieraja", "brak podstaw",
    "dry-run", "brak trafień", "brak trafien",
)

CZYSTY = "CZYSTY"                     # każdy cytat wskazuje na realnie podany fragment
PODEJRZANY = "PODEJRZANY"             # co najmniej jeden cytat spoza podanych fragmentów
BEZ_CYTATU = "BEZ_CYTATU"             # są kandydaci, ale zero powołań na źródło
ABSTENCJA = "ABSTENCJA"               # model odmówił kandydatów — poprawne, nie karzemy
NIC_DO_SPRAWDZENIA = "NIC_DO_SPRAWDZENIA"   # nie podano fragmentów albo pusta odpowiedź


@dataclass(frozen=True)
class Cytat:
    """Jedno powołanie się na źródło, wyłuskane z odpowiedzi modelu."""
    bib: str                       # znormalizowany identyfikator, np. „BIB-006"
    chunk: Optional[int] = None    # numer chunku, gdy podany tuż przy cytacie


@dataclass(frozen=True)
class Werdykt:
    """Wynik badania plonu. `czysty` = nic nie budzi zastrzeżeń."""
    status: str
    cytaty: Tuple[Cytat, ...] = ()
    obce_zrodla: Tuple[str, ...] = ()             # BIB cytowane, a NIE podane
    obce_chunki: Tuple[Tuple[str, int], ...] = ()  # (BIB, chunk) — źródło podane, chunk nie
    podane: Tuple[str, ...] = ()                  # co model faktycznie dostał
    uwagi: Tuple[str, ...] = field(default=())

    @property
    def czysty(self) -> bool:
        return self.status in (CZYSTY, ABSTENCJA, NIC_DO_SPRAWDZENIA)

    def opis(self) -> str:
        """Jednolinijkowy meldunek do raportu/kolejki (zero-tokenowy podgląd)."""
        if self.status == CZYSTY:
            ogon = f" ({self.uwagi[0]})" if self.uwagi else ""
            return (f"🛡️ PROBATOR: CZYSTY — {len(self.cytaty)} cytat(ów), "
                    f"wszystkie z podanych źródeł{ogon}")
        if self.status == ABSTENCJA:
            return "🛡️ PROBATOR: ABSTENCJA — model odmówił kandydatów (poprawny wynik, nie wada)"
        if self.status == NIC_DO_SPRAWDZENIA:
            return "🛡️ PROBATOR: nic do sprawdzenia (brak fragmentów lub pusta odpowiedź)"
        if self.status == BEZ_CYTATU:
            return "🚨 PROBATOR: BEZ_CYTATU — są kandydaci, ale ZERO powołań na źródło"
        czesci = []
        if self.obce_zrodla:
            czesci.append(f"źródła spoza promptu: {', '.join(self.obce_zrodla)}")
        if self.obce_chunki:
            czesci.append("chunki spoza promptu: "
                          + ", ".join(f"{b}/{c}" for b, c in self.obce_chunki))
        return f"🚨 PROBATOR: PODEJRZANY — {'; '.join(czesci)}"


def id_bib(tekst: str) -> Optional[str]:
    """Wyłuskaj znormalizowany identyfikator BIB z dowolnego napisu (nazwa pliku, cytat)."""
    m = _RE_BIB.search(tekst or "")
    return f"BIB-{int(m.group(1)):03d}" if m else None


def podane_zrodla(wyniki: Iterable[Any]) -> Dict[str, Set[int]]:
    """
    Mapa „co model FAKTYCZNIE dostał": BIB → zbiór numerów chunków.

    Przyjmuje wyniki RAG (obiekty z `.zrodlo`/`.nr_chunk`) albo krotki/słowniki — żeby
    dało się badać plon także z zapisanej cząstki, bez ponownego odpytywania RAG.
    """
    mapa: Dict[str, Set[int]] = {}
    for w in wyniki or ():
        if isinstance(w, dict):
            zrodlo, nr = w.get("zrodlo", ""), w.get("nr_chunk")
        elif isinstance(w, (tuple, list)):
            zrodlo, nr = (list(w) + [None, None])[:2]
        else:
            zrodlo, nr = getattr(w, "zrodlo", ""), getattr(w, "nr_chunk", None)
        bib = id_bib(str(zrodlo or ""))
        if not bib:
            continue
        chunki = mapa.setdefault(bib, set())
        try:
            if nr is not None:
                chunki.add(int(nr))
        except (TypeError, ValueError):
            pass                       # nieparsowalny numer = brak wiedzy o chunku, nie błąd
    return mapa


def aliasy_zrodel(wyniki: Iterable[Any]) -> Dict[str, str]:
    """
    Mapa „nazwisko autora → BIB" z nazw plików (`BIB-037_Hull_Options-Futures….epub`).

    POWÓD (zmierzone 2026-07-21 na 34 realnych cząstkach kolejki): model potrafi cytować
    NAZWISKIEM zamiast identyfikatorem — „Źródła: Hull chunk 560, chunk 559". Detektor
    znający tylko formę „BIB-xxx" zgłaszał na tym BEZ_CYTATU, czyli FAŁSZYWY ALARM na
    poprawnie ugruntowanym plonie. Fałszywy alarm jest groźniejszy niż brak alarmu, bo
    uczy operatora ignorować organ.

    Aliasów używamy WYŁĄCZNIE na korzyść modelu (potwierdzenie, że cytat istnieje), nigdy
    do oskarżania: nieznane nazwisko NIE jest tu dowodem konfabulacji, bo zwykłe słowo
    mogłoby przypadkiem trafić w wzorzec. Wykrywanie „autor spoza promptu" wymaga
    słownika autorów całej biblioteki — to zadanie warstwy 2, nie tej.
    """
    mapa: Dict[str, str] = {}
    for w in wyniki or ():
        if isinstance(w, dict):
            zrodlo = str(w.get("zrodlo", ""))
        elif isinstance(w, (tuple, list)):
            zrodlo = str(w[0]) if w else ""
        else:
            zrodlo = str(getattr(w, "zrodlo", ""))
        bib = id_bib(zrodlo)
        if not bib:
            continue
        czesci = zrodlo.split("_")
        if len(czesci) >= 2:
            autor = czesci[1].strip()
            # Nazwiska krótsze niż 4 znaki odrzucamy — „Lo", „Ng" trafiałyby w prozę.
            if len(autor) >= 4 and autor.isalpha():
                mapa[autor.lower()] = bib
    return mapa


def _cytaty_nazwiskiem(odpowiedz: str, aliasy: Dict[str, str]) -> List[str]:
    """Nazwiska autorów z PODANYCH źródeł, na które powołuje się odpowiedź."""
    niski = (odpowiedz or "").lower()
    return sorted({bib for alias, bib in aliasy.items()
                   if re.search(rf"\b{re.escape(alias)}\b", niski)})


def wyodrebnij_cytaty(odpowiedz: str) -> List[Cytat]:
    """
    Wszystkie powołania na źródło w odpowiedzi modelu, w kolejności wystąpienia.

    Numer chunku wiążemy z cytatem TYLKO gdy stoi tuż obok (`_ZASIEG_CHUNKU` znaków) —
    inaczej odległe „chunk 8" z innego akapitu przykleiłoby się do przypadkowego BIB
    i PROBATOR zgłaszałby fałszywy alarm na poprawnym plonie.
    """
    tekst = odpowiedz or ""
    cytaty: List[Cytat] = []
    for m in _RE_BIB.finditer(tekst):
        bib = f"BIB-{int(m.group(1)):03d}"
        ogon = tekst[m.end():m.end() + _ZASIEG_CHUNKU]
        mc = _RE_CHUNK.search(ogon)
        cytaty.append(Cytat(bib=bib, chunk=int(mc.group(1)) if mc else None))
    return cytaty


def _czy_abstencja(odpowiedz: str) -> bool:
    niski = (odpowiedz or "").lower()
    return any(z in niski for z in _ZWROTY_ABSTENCJI)


def sprawdz(odpowiedz: str, wyniki: Sequence[Any]) -> Werdykt:
    """
    Zbadaj plon modelu wobec fragmentów, które mu podano. Deterministyczne, 0 tokenów.

    Kolejność rozstrzygania jest istotna: NIC_DO_SPRAWDZENIA → ABSTENCJA → cytaty.
    Gdyby abstencja szła po cytatach, odpowiedź „fragmenty nic nie wnoszą (BIB-006)"
    zostałaby uznana za konfabulację mimo poprawnego zachowania modelu.
    """
    podane = podane_zrodla(wyniki)
    tresc = (odpowiedz or "").strip()
    if not podane or not tresc:
        return Werdykt(status=NIC_DO_SPRAWDZENIA, podane=tuple(sorted(podane)))

    cytaty = tuple(wyodrebnij_cytaty(tresc))
    if not cytaty:
        if _czy_abstencja(tresc):
            return Werdykt(status=ABSTENCJA, podane=tuple(sorted(podane)))
        # Zanim oskarżymy o brak cytatu — sprawdź słabszą, ale legalną formę: nazwisko autora.
        nazwiskiem = _cytaty_nazwiskiem(tresc, aliasy_zrodel(wyniki))
        if nazwiskiem:
            return Werdykt(
                status=CZYSTY, podane=tuple(sorted(podane)),
                cytaty=tuple(Cytat(bib=b) for b in nazwiskiem),
                uwagi=("cytowane NAZWISKIEM autora, nie identyfikatorem BIB-xxx — "
                       "ugruntowane, ale słabiej sprawdzalne (chunk nieweryfikowalny)",))
        return Werdykt(status=BEZ_CYTATU, podane=tuple(sorted(podane)))

    obce_zrodla, obce_chunki = [], []
    for c in cytaty:
        if c.bib not in podane:
            if c.bib not in obce_zrodla:
                obce_zrodla.append(c.bib)
            continue
        # Chunk sprawdzamy tylko, gdy WIEMY, które chunki podano (pusty zbiór = brak wiedzy,
        # nie dowód winy — inaczej źródło bez numeracji dawałoby fałszywy alarm).
        znane = podane[c.bib]
        if c.chunk is not None and znane and c.chunk not in znane:
            para = (c.bib, c.chunk)
            if para not in obce_chunki:
                obce_chunki.append(para)

    status = PODEJRZANY if (obce_zrodla or obce_chunki) else CZYSTY
    return Werdykt(status=status, cytaty=cytaty, obce_zrodla=tuple(obce_zrodla),
                   obce_chunki=tuple(obce_chunki), podane=tuple(sorted(podane)))


def do_slownika(w: Werdykt) -> Dict[str, Any]:
    """Werdykt w formie zdatnej do zapisu w cząstce JSONL (kolejka hipotez)."""
    return {
        "status": w.status,
        "czysty": w.czysty,
        "cytatow": len(w.cytaty),
        "obce_zrodla": list(w.obce_zrodla),
        "obce_chunki": [[b, c] for b, c in w.obce_chunki],
        "podane": list(w.podane),
        "opis": w.opis(),
    }
