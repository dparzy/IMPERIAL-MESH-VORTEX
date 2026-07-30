"""
📚 HYGINUS — BIBLIOTEKARZ-ZWIADOWCA Imperium. DeepSeek skanuje bibliotekę i proponuje KANDYDATÓW
(pod nadzorem Vitruviusza/Opusa).

Imię (Cezar Pixel, 2026-07-13): GAIUS JULIUS HYGINUS — wyzwoleniec Augusta, pierwszy prefekt
Biblioteki Palatyńskiej (pierwszej cesarskiej biblioteki), uczony-polihistor i zarządca zbiorów.
Symetria epoki: Vitruviusz (Architekt) + Hyginus (Bibliotekarz) — obaj ze złotego wieku Augusta.

Operacjonalizacja ZASADY ZWIADOWCY WIEDZY (CLAUDE.md): DWA modele o różnych rolach.
  • DeepSeek (deepseek-v4-flash, tani ~$0.14/1M) = HYGINUS, ZWIADOWCA/proponent — czyta fragmenty
    RAG biblioteki i wyciąga KANDYDATÓW na neurony/strategie/koncepcje.
  • Opus/Vitruviusz = SĘDZIA/krytyk kompletności — czyta kolejkę kandydatów, weryfikuje, odrzuca
    halucynacje, decyduje co idzie do areny.

ŻELAZNE ZASADY (Prawo I + ZASADA WPIĘCIA):
  • Każdy wynik DeepSeeka = ⚠️ HIPOTEZA/KANDYDAT, NIGDY fakt. Trafia do kolejki, NIE do kodu.
  • Rozstrzyga wyłącznie POMIAR areny (IC/WFO/P&L). Wpięcie w ścieżkę = opt-in OFF + A/B.
  • DeepSeek proponuje TYLKO z podanych fragmentów, cytuje źródło (BIB-xxx). Zero wymyślania.

CZĄSTKOWANIE (ZASADA ANALIZY CZĄSTKOWEJ): temat → RAG → DeepSeek → ZAPIS do kolejki JSONL
ZANIM ruszy następny temat (wznawialność, nic nie ginie). Pasek postępu na stderr (Prawo XXIV).

Użycie:
  python narzedzia/bibliotekarz.py --temat "momentum mean-reversion regime"     # jeden temat
  python narzedzia/bibliotekarz.py                                              # domyślne tematy
  python narzedzia/bibliotekarz.py --dry-run                                    # tylko RAG, bez DeepSeek (bez kosztu)
"""

from __future__ import annotations

import argparse
import functools
import json
import logging
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "narzedzia" / "rag"))

KOLEJKA = ROOT / "docs" / "KOLEJKA_HIPOTEZ_BIBLIOTEKARZ.jsonl"

# Domyślne tematy zwiadu — luki/obszary rozwoju roju (można nadpisać --temat).
TEMATY_DOMYSLNE = [
    "momentum trend-following breakout entry rules",
    "mean reversion overextension bands entry",
    "market regime detection volatility filter",
    "order flow volume delta absorption",
    "risk position sizing stop placement expectancy",
]

_SYSTEM = (
    "Jesteś HYGINUSEM — Bibliotekarzem-Zwiadowcą Imperium tradingowego. Dostajesz FRAGMENTY z książek "
    "(z oznaczeniem źródła BIB-xxx). Twoje zadanie: zaproponuj 1-4 KANDYDATÓW na nowy neuron/"
    "strategię/koncepcję, WYŁĄCZNIE na podstawie podanych fragmentów. ŻELAZNE ZASADY:\n"
    "1. Każdy kandydat to HIPOTEZA, nie fakt — nie twierdź, że coś działa.\n"
    "2. Cytuj źródło (BIB-xxx) dla każdego kandydata. Nie wymyślaj źródeł ani nazw.\n"
    "3. Dla każdego podaj: nazwa, typ (neuron/strategia/koncepcja), zwięzły opis mechanizmu, "
    "oraz JAK to ZMIERZYĆ w backteście (co byłoby dowodem przewagi).\n"
    "4. Jeśli fragmenty nie niosą nic wartościowego — powiedz to wprost, nie konfabuluj.\n"
    "Odpowiedz ZWIĘZŁO, po polsku, w punktach. Bez wstępów."
)


def _fragmenty_tekst(wyniki) -> str:
    """Składa fragmenty RAG w blok dla DeepSeeka (źródło + tekst, przycięte)."""
    czesci = []
    for w in wyniki:
        tekst = (w.tekst or "")[:900]
        czesci.append(f"[{w.zrodlo} — {w.tytul}, chunk {w.nr_chunk}]\n{tekst}")
    return "\n\n---\n\n".join(czesci)


_RE_SLOWO = re.compile(r"[A-Za-z0-9]+")


def _fts_bezpieczne(q: str) -> str:
    """U2: sanityzacja do bezpiecznej składni FTS5 — tylko słowa złączone OR.

    Bez tego myślniki/słowa-klucze FTS wywalają MATCH (realny bug: temat
    'momentum trend-following breakout entry rules' → OperationalError
    'no such column: following' → temat cicho ginął). OR poszerza recall
    (trafienie na dowolny termin), a BM25 i tak rankuje najlepsze na górę.

    DELEGUJE do `szukaj.sanityzuj_fts` (naprawa u źródła 2026-07-30). Ta funkcja
    była JEDNĄ Z TRZECH kopii tej samej logiki, a czwarty wołający — `mcp_server`,
    czyli ścieżka, którą Architekt czyta bibliotekę — nie miał jej wcale i płacił
    za to recallem 16,7% zamiast 66,7% (QUAESITOR, 30 pytań). Zostaje jako nazwa
    dla istniejących wywołań, ale implementacja jest już tylko w jednym miejscu.
    """
    from szukaj import sanityzuj_fts  # type: ignore[import]
    return sanityzuj_fts(q, "or")


# ── DISPENSATOR (Szafarz) — ile myślenia KUPUJEMY do której fazy zwiadu ─────────────
# Organ istniał od sesji dane20, ale Hyginus go NIE WOŁAŁ — martwy potencjał wykryty przez
# BREVIARIUM 2026-07-21 (Prawo XV). Fazy różnią się rodzajem pracy, więc i ceną:
#   rozwijanie zapytania — ekstrakcja słów, zero rozważań → najtaniej (thinking off),
#   generacja kandydatów — objętość ważniejsza od głębi → tanio (flash, effort low),
#   krytyka adwersarialna — realne rozważanie kontrargumentów → NAJDROŻEJ (v4-pro, effort high).
#
# KRYTYKA PRZENIESIONA NA PROFIL 'osad' (v4-pro) — decyzja Cezara 2026-07-21 po A/B LIBRA MESSIS.
# Podstawą jest ASYMETRIA BŁĘDU, nie dowód statystyczny (Prawo I — mówimy wprost, czego nie wiemy):
# zmierzony sygnał jakości był SŁABY (kapitulacji „brak kontrargumentów" 23 vs 13 na 8 tematach,
# rozkład 4-2-2 — nieistotny), a koszt jest PEWNY (3.46×, 1.81× czasu). Zdecydowała obserwacja
# jakościowa: na tym samym plonie flash napisał o kandydacie „nie znaleziono kontrargumentów"
# i ocenił MOCNE, podczas gdy v4-pro wyciągnął Z TYCH SAMYCH fragmentów trzy zarzuty z cytatami
# dosłownymi i ocenił SPRZECZNE. Faza krytyki istnieje wyłącznie po to, by łamać confirmation
# bias — krytyk, który kapituluje, zamienia U3 w teatr i PODNOSI ocenę słabego kandydata.
# Bezwzględnie mowa o centach za bieg. Ramię tańsze pozostaje dostępne przez `profil=` w
# krytyka_kandydatow, więc A/B da się powtórzyć bez cofania tej zmiany.
#
# To NIE dotyka ścieżki decyzyjnej tradingu (zwiad nie ma odwołań z koloseum/ ani cesarz/),
# więc opt-in nie jest wymagany — sędzią kandydatów pozostaje Opus/Vitruviusz, nie DeepSeek
# (ZASADA ZWIADOWCY WIEDZY — dwa modele o RÓŻNYCH rolach).
_PROFIL_ROZWIN = "klasyfikacja"
_PROFIL_ZWIAD = "zwiad"
_PROFIL_KRYTYKA = "osad"

_SYSTEM_ROZWIN = (
    "Jesteś asystentem wyszukiwania pełnotekstowego w anglojęzycznej bibliotece tradingowej. "
    "Rozwiń podany TEMAT w bogate zapytanie: dodaj synonimy, terminy techniczne i pokrewne "
    "pojęcia (trading, finance, statistics). Zwróć WYŁĄCZNIE słowa kluczowe po angielsku, "
    "oddzielone spacjami — bez zdań, bez wyjaśnień, bez interpunkcji. Maksymalnie 30 słów."
)


def rozwin_zapytanie(glos, temat: str) -> str:
    """U2: DeepSeek rozszerza temat w zapytanie bogate w synonimy → lepszy recall FTS.

    Retrieval-only: NIE generuje kandydatów, więc ryzyko halucynacji ograniczone do trafień
    RAG, które i tak filtruje sędzia (Opus) + arena. Fallback na oryginalny temat przy pustej/
    błędnej odpowiedzi — zwiad nigdy nie ginie przez błąd rozszerzenia (Prawo XV)."""
    try:
        # Rozwinięcie tematu w synonimy to ekstrakcja, nie rozważanie — DISPENSATOR kupuje
        # tu najtaniej (thinking off). Zmierzone 07-20: wyłączone rozumowanie = 11.7× taniej.
        odp = glos.zapytaj(_SYSTEM_ROZWIN, f"TEMAT: {temat}", temperatura=0.3,
                           profil=_PROFIL_ROZWIN)
    except Exception:  # noqa: BLE001 — błąd API nie może zabić zwiadu; wracamy do surowego tematu
        return temat
    slowa = _RE_SLOWO.findall(odp or "")
    return " ".join(slowa[:40]) or temat


# U3: sufiks szukania DOWODÓW PRZECIW — poszerza retrieval o kontrargumenty (ryzyka, założenia,
# ograniczenia, sprzeczne wyniki), których „happy-path" zwiad by nie pobrał.
_KONTRA_SUFIKS = "risk failure limitation assumption drawback criticism overfitting"

_SYSTEM_KRYTYKA = (
    "Jesteś SĘDZIĄ-SCEPTYKIEM Imperium (ZASADA ZWIADOWCY WIEDZY: kandydat≠prawda). Dostajesz "
    "KANDYDATÓW (hipotezy Bibliotekarza) oraz FRAGMENTY z biblioteki. Dla KAŻDEGO kandydata wskaż "
    "DOWODY PRZECIW: co w tych fragmentach go podważa, ogranicza lub mu zaprzecza (ukryte założenia, "
    "warunki ważności, znane pułapki, sprzeczne wyniki, ryzyko overfittingu). Oceń wsparcie dowodowe "
    "każdego: MOCNE / SŁABE / SPRZECZNE. Jeśli NIE znajdujesz dowodów przeciw — powiedz to wprost "
    "(to sygnał możliwej stronniczości potwierdzenia, nie dowód słuszności). Surowo, zwięźle, po polsku."
)


def krytyka_kandydatow(glos, kandydaci: str, wyniki_kontra, profil: str | None = None) -> str:
    """U3 (self-critique): drugie przejście — sędzia-sceptyk szuka DOWODÓW PRZECIW kandydatom.

    Wzorzec agentic-RAG: po hipotezie szukamy dowodów DISCONFIRMING, by ograniczyć confirmation
    bias. Wynik ląduje w polu 'krytyka' cząstki — Opus-sędzia i arena widzą od razu słabe hipotezy.
    Błąd API nie może zabić zwiadu (Prawo XV): zwracamy komunikat, kandydaci już są zapisani.

    `profil` (domyślnie None → `_PROFIL_KRYTYKA`, czyli zachowanie NIEZMIENIONE) pozwala
    zmierzyć inny profil DISPENSATORA na tej samej fazie — bez tego A/B „flash vs v4-pro na
    krytyce" wymagałby duplikatu tej funkcji, a duplikat rozjechałby się z oryginałem."""
    tresc = (f"KANDYDACI:\n{kandydaci}\n\n"
             f"FRAGMENTY (możliwe kontrargumenty):\n{_fragmenty_tekst(wyniki_kontra)}")
    try:
        # Szukanie dowodów PRZECIW własnym kandydatom to realne rozważanie — tu DISPENSATOR
        # kupuje głębokość (profil 'krytyka'), inaczej sceptyk byłby równie płytki co proponent.
        return glos.zapytaj(_SYSTEM_KRYTYKA, tresc, temperatura=0.3,
                            profil=profil or _PROFIL_KRYTYKA).strip()
    except Exception:  # noqa: BLE001 — krytyka to dodatek; jej brak nie przekreśla cząstki
        return "(krytyka niedostępna — błąd API)"


# U4 jest DOMYŚLNIE WYŁĄCZONE od 2026-07-27 (DECYZJA CEZARA, wachta otwarta po replikacji).
#
# HISTORIA W TRZECH KROKACH — zostaje w całości, bo sama zmiana domyślnej wartości bez powodu
# byłaby cichym cofnięciem rozkazu z 07-21, a rozkaz padł na podstawie, która później upadła:
#
# 1) 07-21 → ON. Podstawa: A/B na kampanii `u4_rdzen` (64+64) dał „−12.1 pp duplikatów,
#    p=0.016". Rozkaz Cezara po sądzie nad kolejką.
# 2) 07-27 → teza OBALONA. Ten sam zapisany plon przeliczony detektorem BEZ ślepych plam:
#    OFF 88/224 = 39.3% wobec ON 82/200 = 41.0%, Fisher p=0.766 — różnicy nie ma. Stary
#    detektor był ślepy ASYMETRYCZNIE: 34.7% kandydatów ramienia ON nosiło nazwy
#    WIELKIE_Z_PODKRESLENIEM (bo ten blok pokazuje modelowi NASZE klucze, więc podpowiada
#    konwencję), a wzorce typu `\bvpin\b` nie przekraczają podkreślenia — dublet ON-a był
#    niewidzialny z definicji. Do tego 4 z 7 formatów nagłówka sklejały plon.
# 3) 07-27 → REPLIKACJA na 128 świeżych pomiarach (rundy 5-8): świeża −3.1 pp p=0.549;
#    łącznie 256 biegów −0.7 pp, CI [−7.3, +6.0], p=0.888. MOC na publikowane −12 pp = 94.2%,
#    więc efekt tej wielkości jest WYKLUCZONY. Przy 5 pp moc to tylko 31% — małego efektu
#    NIE wykluczamy i nie udajemy, że wykluczyliśmy.
#
# DECYZJA (Cezar, 2026-07-27): OFF. Rachunek jest asymetryczny — koszt 1.49× jest ZMIERZONY
# i pewny, korzyść mieści się w szumie. Płacenie połowy więcej za efekt nieodróżnialny od zera
# to utrata potencjału w drugą stronę (Prawo XV liczy też wydatek bez zwrotu).
#
# CO ZOSTAJE PRAWDĄ mimo OFF (nie kasować tej obserwacji): zwiad BEZ tego bloku proponuje
# moduły, które JUŻ MAMY — 39.3% kandydatów ramienia OFF nazywa pojęcie obecne w kodzie
# (VPIN → WSKAZNIK „VPIN_50"; Value Area → VP-01; Kelly → IUSTITIA; CVD/FUNDING_EXTREME →
# wskaźniki; Kalman → exp_kalman; triple_barrier → W-357; DSR/PBO → koloseum). Zmierzone
# jest tylko to, że TEN blok tego NIE NAPRAWIA. Anty-redundancję egzekwuje więc SĘDZIA
# (grep przy wyroku), nie prompt — deklaracja modelu „nie dubluje" padała przy KAŻDYM
# kandydacie, także przy VPIN (Prawo XVI: redundancja mierzona, nie zgadywana).
#
# Wyłącznik zostaje obustronny: `--swiadomosc` włącza z powrotem, A/B wymaga obu ramion.
# Szczegóły pomiarów: INDEX FALSORUM + CODEX PROBATIONUM (2026-07-27).
@functools.lru_cache(maxsize=1)
def _kontekst_systemu() -> str:
    """U4 (świadomość systemu): zwięzły blok o LUKACH (Prawo XV) i ISTNIEJĄCYCH modułach
    (anty-redundancja, Prawo XVI), wstrzykiwany DeepSeekowi przy generacji kandydatów.

    Dzięki temu Hyginus proponuje pod REALNE braki roju i wie, co już istnieje — odtwarza
    główną siłę ręcznego web-DeepSeeka (kontekst systemu), ale ze źródeł biblioteki. Cache 1×
    (rejestr nie zmienia się w trakcie biegu). Brak rejestru → '' (zwiad działa dalej, Prawo XV)."""
    try:
        from imperium.legiony.rejestr import wszystkie_neurony
        from narzedzia.audyt_spojnosci import NEURONY_ZALEZNE_OD_ADAPTEROW as LUKI
    except Exception:  # noqa: BLE001 — brak rejestru/audytu nie może zabić zwiadu
        return ""
    neurony = wszystkie_neurony()
    istniejace = ", ".join(sorted({n.KLUCZ for n in neurony}))
    kategorie = ", ".join(sorted({n.KATEGORIA for n in neurony}))
    luki = "; ".join(f"{k} ({opis})" for k, opis in sorted(LUKI.items()))
    return (
        "\n\nKONTEKST IMPERIUM (świadomość systemu — steruj doborem kandydatów):\n"
        f"• ISTNIEJĄCE moduły — NIE proponuj duplikatów (Prawo XVI): {istniejace}\n"
        f"• Kategorie w użyciu: {kategorie}\n"
        f"• LUKI — moduły milczące, czekają na dane/adapter; PREFERUJ kandydatów, którzy je "
        f"zasilają lub wnoszą NOWĄ informację: {luki}\n"
        "Dla KAŻDEGO kandydata dopisz: (a) którą LUKĘ zasila LUB jaką NOWĄ informację wnosi, "
        "(b) czy NIE dubluje istniejącego modułu."
    )


def scout_temat(glos, temat: str, topk: int = 6, tryb: str = "hybrid",
                korpus: str | None = "biblioteka", rozwin: bool = False,
                krytyka: bool = False, swiadomosc: bool = False,
                probator: bool = True, nomenclator: bool = False) -> dict:
    """Jeden temat: RAG → DeepSeek proponuje kandydatów. Zwraca dict cząstki (do kolejki).

    Zakłada, że indeks RAG ISTNIEJE (bramkuje raport() — Cubic P2). Status cząstki:
    'ok' = kandydaci od DeepSeeka, 'dry' = podgląd RAG bez API, 'pusto' = brak trafień.

    U1 (anty-echo, Prawo XVI): domyślnie czytamy TYLKO korpus 'biblioteka' (książki BIB-xxx),
    nie 'docs'/'dane' — inaczej Hyginus wyciąga NASZE własne notatki i podaje je jako
    „odkrycie" (echo własnego głosu = redundancja). korpus=None świadomie omija filtr.

    U2 (recall): tryb domyślnie 'hybrid' (auto-fallback na FTS gdy brak wektorów). Gdy rozwin=True
    DeepSeek rozszerza temat w synonimy PRZED RAG. Zapytanie ZAWSZE sanityzowane do bezpiecznej
    składni FTS5 (_fts_bezpieczne) — inaczej myślniki/słowa-klucze wywalają MATCH."""
    from szukaj import szukaj  # type: ignore[import]
    zapytanie = rozwin_zapytanie(glos, temat) if (rozwin and glos is not None) else temat
    # Sanityzacja jest JUŻ w `szukaj` (jedno źródło prawdy, 2026-07-30) — podwójne
    # złożenie dałoby „a OR OR OR b", czyli błąd składni FTS. Przekazujemy surowe.
    wyniki = szukaj(zapytanie, topk=topk, tryb=tryb, cichy=True, korpus=korpus)
    zrodla = sorted({w.zrodlo for w in wyniki})
    baza = {"temat": temat, "zapytanie": zapytanie, "ts": time.time()}
    if not wyniki:                          # indeks jest (bramka w raport), więc to REALNY brak trafień
        return {**baza, "zrodla": [], "kandydaci": "(brak fragmentów RAG)", "status": "pusto"}
    if glos is None:                       # dry-run: bez DeepSeeka, tylko podgląd RAG
        return {**baza, "zrodla": zrodla,
                "kandydaci": "(dry-run — DeepSeek pominięty)", "status": "dry"}
    tresc = f"TEMAT: {temat}\n\nFRAGMENTY:\n{_fragmenty_tekst(wyniki)}"
    if swiadomosc:  # U4: dołącz świadomość systemu (luki + istniejące moduły) do generacji kandydatów
        tresc += _kontekst_systemu()
    # Generacja kandydatów = zwiad objętościowy (dużo fragmentów, płytka analiza każdego).
    odp = glos.zapytaj(_SYSTEM, tresc, temperatura=0.4, profil=_PROFIL_ZWIAD)
    rec = {**baza, "zrodla": zrodla, "kandydaci": odp.strip(), "status": "ok",
           "profil": _PROFIL_ZWIAD}
    if probator:  # WARSTWA 1 anty-halucynacyjna: cytat spoza podanych fragmentów (0 tokenów)
        from imperium.pretorianie.probator import do_slownika, sprawdz
        rec["probator"] = do_slownika(sprawdz(rec["kandydaci"], wyniki))
    if nomenclator:  # WARSTWA 2 anty-redundancyjna: nazwa kandydata vs leksykon roju (0 tokenów)
        # OPT-IN, DOMYŚLNIE OFF (ZASADA WPIĘCIA — włącza się po zielonym A/B). Organ jest
        # monotonicznie ostrożny: DOKŁADA adnotację dla sędziego, nie usuwa kandydatów
        # i nie zmienia niczego, co bez niego trafiłoby do kolejki.
        from imperium.pretorianie.nomenclator import do_slownika as _nom_slownik
        from imperium.pretorianie.nomenclator import sprawdz as _nom_sprawdz
        rec["nomenclator"] = _nom_slownik(_nom_sprawdz(rec["kandydaci"]))
    if krytyka:  # U3: drugie przejście — dowody PRZECIW (osobne retrieval na kontrargumenty)
        kontra = szukaj(f"{zapytanie} {_KONTRA_SUFIKS}",
                        topk=topk, tryb=tryb, cichy=True, korpus=korpus)
        # Profil KRYTYKI zapisany wprost (2026-07-27). Cząstka niosła tylko `profil` generacji,
        # więc z samego ledgera NIE DAŁO SIĘ udowodnić, że krytyka poszła na droższy `osad`
        # (v4-pro) — wiedzieliśmy to wyłącznie z kodu. Decyzja Cezara z 07-21 kosztuje pieniądze,
        # więc ma być WIDOCZNA W POMIARZE, nie tylko w źródle (pomiar > pamięć).
        # Jedna zmienna do WYWOŁANIA i do ZAPISU — inaczej zapis byłby deklaracją, nie dowodem
        # (gdy ktoś kiedyś poda `profil=` z zewnątrz, ledger mówiłby o profilu, który nie biegł).
        profil_krytyki = _PROFIL_KRYTYKA
        rec["krytyka"] = krytyka_kandydatow(glos, rec["kandydaci"], kontra, profil=profil_krytyki)
        rec["profil_krytyki"] = profil_krytyki
        if probator:  # krytyka to też plon modelu — bada się ją wobec WŁASNYCH fragmentów
            from imperium.pretorianie.probator import do_slownika, sprawdz
            rec["probator_krytyka"] = do_slownika(sprawdz(rec["krytyka"], kontra))
    return rec


def _tematy_ukonczone() -> set:
    """Tematy już zeskanowane realnie (status ≠ 'dry') w kolejce — by NIE płacić DeepSeekowi
    ponownie ani nie dublować kandydatów (Cubic P2). Stare rekordy bez pola status = ukończone."""
    if not KOLEJKA.exists():
        return set()
    done = set()
    with open(KOLEJKA, encoding="utf-8") as f:
        for linia in f:
            linia = linia.strip()
            if not linia:
                continue
            try:
                rec = json.loads(linia)
            except json.JSONDecodeError:
                continue
            if rec.get("temat") and rec.get("status") != "dry":
                done.add(rec["temat"])
    return done


def zapisz_czastke(czastka: dict) -> None:
    """Dopisz kandydatów tematu do kolejki JSONL (ZASADA ANALIZY CZĄSTKOWEJ — natychmiast)."""
    KOLEJKA.parent.mkdir(parents=True, exist_ok=True)
    with open(KOLEJKA, "a", encoding="utf-8") as f:
        f.write(json.dumps(czastka, ensure_ascii=False) + "\n")
    # KAŻDY ZAPIS UNIEWAŻNIA MIGAWKĘ (błąd własny 2026-07-27, złapany przez istniejące testy):
    # `_znaczniki` cache'uje TAKŻE znaczniki zwiadu, więc bez tego świeżo dopisana cząstka
    # była niewidzialna dla walidacji wyroku — sędzia dostawałby „wyrok bez adresata" na
    # cząstkę, którą sam przed chwilą zapisał. Cache stanu wymaga ścieżki unieważnienia
    # przy KAŻDYM zapisie, nie tylko przy tym, o którym pamiętał autor.
    _znaczniki.cache_clear()


def ile_tematow(wpisy) -> int:
    """Ile RÓŻNYCH tematów stoi za listą wpisów „temat [plon] → opis".

    Osobna funkcja, żeby dało się ją przetestować bez płatnego zwiadu — inline'owe
    wyrażenie w raporcie testowałoby się wyłącznie przez powtórzenie samego siebie.
    """
    return len({str(x).split(" [", 1)[0] for x in wpisy})


WERDYKTY = ("PRZYJETY", "ODRZUCONY", "CZESCIOWO")


def zapisz_wyrok(*, dot_ts: float, temat: str, werdykt: str, uzasadnienie: str,
                 przyjete=(), sedzia: str = "Vitruviusz") -> bool:
    """Zamyka cząstkę WYROKIEM sędziego. Zwraca czy dopisano (idempotencja po `dot_ts`).

    DLACZEGO TO W OGÓLE POWSTAŁO (zmierzone 2026-07-27): kolejka rosła nieprzerwanie od
    2026-07-14 do 43 cząstek czekających na sędziego — nie dlatego, że sędzia był leniwy,
    ale dlatego, że NIE MIAŁ GDZIE ORZEC. Zwiadowca umiał dopisać plon, nikt nie umiał go
    domknąć, więc każda wachta zaczynała od zera i „dług przeglądu" mógł tylko rosnąć.
    Brakujący krok procesu wygląda identycznie jak zaniedbanie — i tak był raportowany.

    WYROK IDZIE DO TEGO SAMEGO PLIKU co plon (Prawo XVI — bez drugiego rejestru), jako
    osobny rekord `status="wyrok"` wskazujący cząstkę przez `dot_ts`. Plon zwiadowcy
    zostaje NIETKNIĘTY (Prawo I: nie przepisujemy cudzego meldunku po fakcie) — życie
    cząstki czyta się jako łańcuch: zwiad → wyrok.
    """
    if werdykt not in WERDYKTY:
        raise ValueError(f"werdykt musi być jednym z {WERDYKTY}, jest: {werdykt!r}")
    if not uzasadnienie or not uzasadnienie.strip():
        raise ValueError("uzasadnienie jest wymagane — wyrok bez powodu to nie wyrok")
    # WYROK MUSI MIEĆ ADRESATA (recenzja cubic PR #134, P2 — przyjęta 2026-07-27).
    # Literówka w `dot_ts` tworzyła rekord wskazujący na nieistniejącą cząstkę: wyrok
    # wyglądał na wydany, a sądzona cząstka dalej czekała w kolejce. Przy 35 cząstkach do
    # osądzenia w jednej wachcie to nie jest przypadek teoretyczny — to jedno przestawienie
    # cyfry. Cichy `False` byłby tu gorszy niż wyjątek: „już osądzone" i „nie ma czego sądzić"
    # to dwa różne stany, a tylko drugi jest błędem sędziego (Prawo I).
    zwiad, wyroki = _znaczniki()
    if dot_ts in wyroki:
        return False
    if dot_ts not in zwiad:
        raise ValueError(
            f"dot_ts={dot_ts!r} nie wskazuje ŻADNEJ cząstki zwiadu w {KOLEJKA.name} — "
            "wyrok bez adresata zostawiłby sądzoną cząstkę w kolejce. Sprawdź znacznik.")
    zapisz_czastke({"status": "wyrok", "dot_ts": dot_ts, "temat": temat,
                    "werdykt": werdykt, "uzasadnienie": uzasadnienie.strip(),
                    "przyjete": list(przyjete), "sedzia": sedzia, "ts": time.time()})
    osadzone_ts.cache_clear()
    _znaczniki.cache_clear()
    return True


@functools.lru_cache(maxsize=1)
def osadzone_ts() -> frozenset:
    """Znaczniki cząstek, nad którymi ZAPADŁ już wyrok."""
    return _znaczniki()[1]


@functools.lru_cache(maxsize=1)
def _znaczniki() -> tuple:
    """(znaczniki cząstek ZWIADU, znaczniki OSĄDZONE) — jeden przebieg po kolejce.

    Dwa zbiory z JEDNEGO odczytu, bo mają zawsze opisywać ten sam stan pliku: gdyby
    każdy czytał kolejkę osobno, mogłyby kiedyś pochodzić z dwóch różnych migawek
    (ta sama klasa co licznik i mianownik z osobnych przebiegów, Księga Wad 2026-07-27).
    """
    if not KOLEJKA.exists():
        return frozenset(), frozenset()
    zwiad, wyroki = set(), set()
    with open(KOLEJKA, encoding="utf-8") as f:
        for linia in f:
            if not linia.strip():
                continue
            try:
                rec = json.loads(linia)
            except json.JSONDecodeError:
                continue
            if rec.get("status") == "wyrok":
                if rec.get("dot_ts") is not None:
                    wyroki.add(rec["dot_ts"])
            elif rec.get("ts") is not None:
                zwiad.add(rec["ts"])
    return frozenset(zwiad), frozenset(wyroki)


def raport(tematy, topk=6, tryb="hybrid", dry_run=False, force=False, korpus="biblioteka",
           rozwin=False, krytyka=False, swiadomosc=False, probator=True,
           nomenclator=False) -> str:
    # Cubic P2: bramka indeksu RAG — brak bazy to AWARIA INFRY, nie „pusty wynik". Nie skanujemy
    # i NIC nie zapisujemy do kolejki (inaczej awaria udawałaby ukończony, pusty zwiad).
    from szukaj import DEFAULT_BAZA  # type: ignore[import]
    if not DEFAULT_BAZA.exists():
        return (f"🚨 BIBLIOTEKARZ — brak indeksu RAG ({DEFAULT_BAZA}). "
                "Uruchom: python narzedzia/rag/indeksuj.py. Nic nie zeskanowano ani nie zapisano.")

    glos = None
    if not dry_run:
        from imperium.cesarz.deepseek_glos import GlosImperium
        glos = GlosImperium()   # domyślny = deepseek-v4-flash (tani zwiadowca; Prawo XVI: rola proponenta)

    # Cubic P2: pomiń tematy już zeskanowane realnie (chyba że --force) — zero podwójnego kosztu API.
    zrobione = set() if force else _tematy_ukonczone()

    N = len(tematy)
    podejrzane: list[str] = []      # tematy, w których PROBATOR złapał cytat spoza fragmentów
    znane_imiona: list[str] = []    # tematy, w których NOMENCLATOR rozpoznał imię z leksykonu roju
    linie = [f"📚 HYGINUS (Bibliotekarz-Zwiadowca) — {N} tematów, {'DRY-RUN' if dry_run else 'DeepSeek'} "
             f"(⚠️ KANDYDACI — prawdą po arenie)"]
    for i, temat in enumerate(tematy, 1):
        if temat in zrobione:
            print(f"[{i}/{N}] ⏭️ „{temat}” — już w kolejce (pomijam; --force by przeliczyć)",
                  file=sys.stderr, flush=True)
            linie.append(f"\n── [{i}/{N}] {temat} — pominięty (już zeskanowany; --force by powtórzyć) ──")
            continue
        print(f"[{i}/{N}] zwiad: „{temat}” — RAG + {'(dry)' if dry_run else 'DeepSeek'}…",
              file=sys.stderr, flush=True)
        try:
            czastka = scout_temat(glos, temat, topk=topk, tryb=tryb, korpus=korpus,
                                  rozwin=rozwin, krytyka=krytyka, swiadomosc=swiadomosc,
                                  probator=probator, nomenclator=nomenclator)
        except Exception as e:  # noqa: BLE001
            print(f"[{i}/{N}] ⚠️ „{temat}”: {e}", file=sys.stderr, flush=True)
            continue
        zapisz_czastke(czastka)
        zr = ", ".join(czastka["zrodla"][:5]) or "—"
        print(f"[{i}/{N}] ✅ „{temat}” → źródła: {zr} | 💾 kolejka", file=sys.stderr, flush=True)
        # PROBATOR mówi tylko wtedy, gdy ma co zarzucić — cisza znaczy „cytaty się zgadzają".
        # 🚨 OBA PLONY, nie sam kandydat (2026-07-27): krytyka też jest wypowiedzią modelu i też
        # bywa skażona. Zmierzone na partii 07-26: kandydaci 10/10 czyste, krytyka 2/10 nie —
        # a raport milczał, bo czytał wyłącznie `probator`. Sędzia dostawał obronę bez ostrzeżenia.
        linie.append(f"\n── [{i}/{N}] {temat} (źródła: {zr}) ──\n{czastka['kandydaci']}")
        for pole, etykieta in (("probator", "kandydaci"), ("probator_krytyka", "krytyka")):
            pro = czastka.get(pole) or {}
            if not pro:
                continue
            if not pro.get("czysty", True):
                print(f"[{i}/{N}] [{etykieta}] {pro['opis']}", file=sys.stderr, flush=True)
                podejrzane.append(f"{temat} [{etykieta}] → {pro['opis']}")
            linie.append(f"[{etykieta}] {pro['opis']}")
        # NOMENCLATOR mówi tylko GŁOSEM POZYTYWNYM (patrz docstring organu): milczenie znaczy
        # „żadna nazwa nie trafiła w 32 pojęcia leksykonu", co jest słabym dowodem nowości.
        # Dlatego raportujemy trafienia, a nie „czystość" — inaczej powtórzylibyśmy dokładnie
        # tę bezwartościową deklarację „nie dubluje", którą zmierzyliśmy przy U4.
        nom = czastka.get("nomenclator") or {}
        if nom.get("podejrzanych"):
            opis = (f"{nom['podejrzanych']}/{nom['kandydatow']} nosi znane imię: "
                    f"{', '.join(nom['pojecia'])}")
            print(f"[{i}/{N}] [nomenclator] {opis}", file=sys.stderr, flush=True)
            znane_imiona.append(f"{temat} → {opis}")
            linie.append(f"[nomenclator] {opis}")

    if znane_imiona:
        linie.append(f"\n🏷️ NOMENCLATOR — {len(znane_imiona)}/{N} tematów z kandydatem, którego "
                     f"NAZWA trafia w pojęcie żywe w kodzie (sprawdź grepem przed przyjęciem; "
                     f"trafienie ≠ wyrok — to samo słowo bywa innym pojęciem):")
        linie.extend(f"   • {x}" for x in znane_imiona)
    if podejrzane:
        # LICZYMY TEMATY, NIE WPISY (recenzja cubic PR #134, P3 — przyjęta 2026-07-27).
        # PROBATOR bada OBA plony (kandydaci + krytyka), więc jeden temat potrafi dołożyć
        # DWA wpisy — a nagłówek mówił „X/N tematów". Przy obu skażonych plonach licznik
        # mógł przekroczyć N i ogłosić więcej tematów skażonych, niż w ogóle skanowano.
        # Klasa znana: licznik, który kłamie. Lista zostaje pełna (wpisy per plon).
        linie.append(f"\n🚨 PROBATOR — {ile_tematow(podejrzane)}/{N} tematów ({len(podejrzane)} plonów) "
                     f"z cytatem spoza podanych fragmentów "
                     f"(halucynacja citation; sędzia niech czyta je najostrożniej):")
        linie.extend(f"   • {x}" for x in podejrzane)
    # Ścieżka WZGLĘDNA jest tylko wygodą czytania. `relative_to` rzuca ValueError, gdy kolejka
    # leży poza drzewem repo (inny dysk, katalog tymczasowy) — i wywalałaby CAŁY raport już PO
    # zapłaceniu za skan DeepSeekiem. Kosmetyka nie ma prawa niszczyć opłaconej pracy.
    try:
        gdzie = KOLEJKA.relative_to(ROOT)
    except ValueError:
        gdzie = KOLEJKA
    linie.append(f"\n💾 Kolejka: {gdzie} — do PRZEGLĄDU Opusa (sędzia). "
                 f"Nic nie wchodzi do kodu bez weryfikacji + areny (Prawo I, ZASADA WPIĘCIA).")
    return "\n".join(linie)


_TOPK_MAX = 20


def _topk_arg(tekst: str) -> int:
    """Cubic P2: ogranicz --topk do małego dodatniego zakresu — bez tego wielki/ujemny topk
    ściąga nieograniczony korpus i wysyła go do PŁATNEGO API."""
    v = int(tekst)
    if not (1 <= v <= _TOPK_MAX):
        raise argparse.ArgumentTypeError(f"--topk musi być w [1, {_TOPK_MAX}], podano: {tekst}")
    return v


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    p = argparse.ArgumentParser(description="HYGINUS — Bibliotekarz-Zwiadowca, DeepSeek skanuje bibliotekę (W-363)")
    p.add_argument("--temat", action="append", help="temat zwiadu (można wiele razy). Brak → domyślne.")
    p.add_argument("--topk", type=_topk_arg, default=6, help=f"ile fragmentów RAG na temat [1, {_TOPK_MAX}]")
    p.add_argument("--tryb", default="hybrid", choices=["fts", "hybrid", "wektor"],
                   help="U2: domyślnie 'hybrid' (semantyka+FTS; auto-fallback na FTS gdy brak wektorów)")
    p.add_argument("--korpus", default="biblioteka", choices=["biblioteka", "dane", "docs", "wszystko"],
                   help="korpus RAG do zwiadu (U1: domyślnie 'biblioteka' — tylko książki, anty-echo docs)")
    p.add_argument("--rozwin", action="store_true",
                   help="U2: rozszerz temat przez DeepSeek w synonimy przed RAG (lepszy recall; +1 tani call/temat)")
    p.add_argument("--krytyka", action="store_true",
                   help="U3: self-critique — drugie przejście szuka DOWODÓW PRZECIW kandydatom (+1 RAG +1 call/temat)")
    p.add_argument("--swiadomosc", action="store_true",
                   help="włącz U4 (świadomość systemu: istniejące klucze + luki Prawa XV). "
                        "DOMYŚLNIE OFF od 2026-07-27 — replikacja na 256 biegach dała −0.7 pp "
                        "CI [−7.3,+6.0] p=0.888 przy zmierzonym koszcie 1.49×")
    p.add_argument("--bez-swiadomosci", action="store_true",
                   help="(bez efektu — U4 jest domyślnie WYŁĄCZONE od 2026-07-27; flaga zostawiona, "
                        "żeby stare polecenia i skrypty nie padały)")
    p.add_argument("--pelny", action="store_true",
                   help="komplet U2+U3: --rozwin --krytyka naraz (U4 zostaje OFF — włącz --swiadomosc)")
    p.add_argument("--bez-probatora", action="store_true",
                   help="wyłącz PROBATORA (strażnik cytatów, 0 tokenów) — domyślnie WŁĄCZONY")
    p.add_argument("--nomenclator", action="store_true",
                   help="włącz NOMENCLATORA (strażnik imion, 0 tokenów): oznacza kandydatów, "
                        "których NAZWA trafia w pojęcie żywe w kodzie. OPT-IN, domyślnie OFF "
                        "do czasu zielonego A/B (ZASADA WPIĘCIA)")
    p.add_argument("--dry-run", action="store_true", help="tylko RAG, bez DeepSeek (bez kosztu API)")
    p.add_argument("--force", action="store_true", help="przeskanuj też tematy już w kolejce")
    args = p.parse_args()

    tematy = args.temat or TEMATY_DOMYSLNE
    korpus = None if args.korpus == "wszystko" else args.korpus  # 'wszystko' → bez filtra (dawne zachowanie)
    rozwin = args.rozwin or args.pelny
    krytyka = args.krytyka or args.pelny
    # Domyślnie OFF (decyzja Cezara 07-27) — patrz komentarz przy _kontekst_systemu.
    # `--bez-swiadomosci` celowo NIE ma już mocy wyłączania: jest zgodnością wsteczną, a nie
    # przełącznikiem, więc stare polecenie z tą flagą daje dokładnie to, o co prosiło (brak U4).
    swiadomosc = args.swiadomosc and not args.bez_swiadomosci
    print(raport(tematy, topk=args.topk, tryb=args.tryb, dry_run=args.dry_run,
                 force=args.force, korpus=korpus, rozwin=rozwin, krytyka=krytyka,
                 swiadomosc=swiadomosc, probator=not args.bez_probatora,
                 nomenclator=args.nomenclator))
